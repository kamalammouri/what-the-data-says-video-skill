"""Build the Google Flow prompts of a shot list and lint it against the channel's image rules.

  python prompts.py shots.json [--brief brief.json] [--setting "..."] [--flow-per-min 7] [--strict]
      -> prompts.json (for flow/batch.mjs, with the reference images of each prompt in "refs") + lint report ; --strict exits 1 on an ERROR
  python prompts.py --thumbs thumb_specs.json   -> thumbs.json: the thumbnail scenes, same sheets, covered costumes, same references
  python prompts.py --selftest

shots.json = [{"i": 1, "sentence": "...", "family": "scene", "file": "F001", "scene": "...", "composition": "wide", "frame": "wide",
               "cast": "hero+heroine", "era": "modern", "dark": false}, ...]      (written by make_shots.py)
  family: scene | metaphor | icon | schema | map -> one Flow image per distinct "file" ; html (hand-drawn insert) and title -> by code, no prompt
  cast:   names of styles.json "cast" joined by "+" (hero, heroine, friend). No cast = a scene without the recurring characters.
  era:    modern (default) | tribe -> the costume of each cast member (styles.json). modern never carries a weapon.
  composition: wide | medium | close | cutaway | overhead | pov ; frame: the motion hf_build.py gives the shot.
Never edit a prompt by hand: the prefix and the character sheets must be in EVERY prompt, Flow has no memory between generations.

Flow budget: 6 to 7 images per minute (70 to 85 for 12 min). 112 images for 12 min cost 27 regenerations, 43 refusals and six
control passes (bath-en, 10 Nov 2026); each image is held over up to three consecutive shots with different framings.
"""
import json, re, sys, itertools, pathlib

HERE = pathlib.Path(__file__).parent
FLOW_PER_MIN = 7
WPM, GAP = 170, 0.22                 # the voice: 165-175 words a minute, 0.2-0.25 s between lines (tts.py)
DATA_WARN, DATA_MAX, FIRST_DATA = 25, 30, 60   # seconds: a data insert every 20-25 s, the first figure on screen before 1:00
COMPOSITIONS = {
    "wide": "Wide shot, the whole set visible, horizon line low,",
    "medium": "Medium shot, waist up, the set suggested behind,",
    "close": "Close-up on one object filling the frame, no hands and no person in the frame,",   # "hands" gave realistic flesh hands on 6 close-ups (older-men-en, 11 Nov 2026)
    "cutaway": "Cutaway view as if one wall were removed, the inside drawn like a dollhouse,",
    "overhead": "Overhead view looking straight down,",
    "pov": "First-person point of view, {pov_hands},",
}
FAMILY_TEMPLATE = {
    "scene": "{comp} {scene}. {scene_bg}",
    "icon": "A single isolated object: {scene}. {insert_bg} Thick clean outline, flat fill.",
    "schema": "Simple explanatory diagram: {scene}. {insert_bg} Thin outlines, two or three flat colours, thick coloured arrows where motion matters.",
    "metaphor": "Visual metaphor, drawn literally: {scene}. {insert_bg}",
    "map": "Simple flat map silhouette: {scene}. {insert_bg} One red pin, no place names.",
}
# Flow draws everything the prompt evokes: these words gave speech bubbles, signs and screens full of fake text.
BANNED = ["talking", "talks", "calling", "says", "saying", "speaks", "speaking", "conversation", "sign ", "signs", "label", "poster", "screen showing",
          "reads ", "written", "writing", "text", "clock showing", "gauge reading", "number", "digits", "letters", "caption", "subtitle"]
# Channel rules (user, 9-11 Nov 2026; references/images-flow.md).
WEAPON = r"\b(spears?|clubs?|bows?|arrows?|axes?|swords?|knife|knives)\b"
RELIGIOUS = r"\b(a cross|the cross|crosses|crucifix\w*|church\w*|cathedral|chapel|mosque|minaret|synagogue|bible|quran|koran|torah|rosary|halo|angels?|altar|priest|nun|monk|star of david)\b"
SILHOUETTE = r"\b(silhouettes?|shadowy figure|black figure|dark figure|faceless)\b"
DETAILED = r"\b(detailed|realistic|photoreal\w*|lifelike)\b"
# One simple symbol is drawn by code (hand-drawn-visuals), exact and free: never ask Flow for it.
CODE_ICONS = {"check mark": "check", "checkmark": "check", "cross mark": "x", "question mark": "circle-help", "exclamation": "circle-alert",
              "light bulb": "lightbulb", "lightbulb": "lightbulb", "padlock": "lock", "coin": "coins", "envelope": "mail", "magnifying glass": "search",
              "heart shape": "heart", "calendar": "calendar-days", "hourglass": "hourglass", "thermometer": "thermometer", "battery": "battery"}

def html_is_data(s):
    """A data insert = a hand-drawn insert that shows a figure (a title card or a bare symbol does not count)."""
    h = s.get("html") or {}
    return s["family"] == "html" and h.get("type") != "title" and bool(re.search(r"\d", json.dumps(h)))

def code_candidate(s):
    if s["family"] not in ("icon", "metaphor", "schema"): return None
    low = " " + s.get("scene", "").lower() + " "
    if len(low.split()) > 14 or " character" in low or " figure" in low or " hand" in low: return None
    hits = {v for k, v in CODE_ICONS.items() if k in low}
    return hits.pop() if len(hits) == 1 else None

def tokens(s): return set(re.findall(r"[a-z]{4,}", s.lower()))

def arg_value(args, flag):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else None

def resolve_style(args=()):
    """styles.json (one style) + brief.json "setting" + --setting."""
    cfg = json.load(open(HERE / "styles.json", encoding="utf-8")); st = dict(cfg["styles"][cfg["default"]]); st["id"] = cfg["default"]
    bp = pathlib.Path(arg_value(args, "--brief") or "brief.json")
    brief = json.load(open(bp, encoding="utf-8")) if bp.exists() else {}
    setting = arg_value(args, "--setting") or brief.get("setting") or ""
    st["setting"] = ("Setting: " + setting.rstrip(". ") + ".") if setting else ""
    return st

def durations(shots):
    """Seconds each shot stays on screen: real starts when every shot has one, else the words at 170 a minute plus the pause."""
    if all(isinstance(s.get("start"), (int, float)) for s in shots):
        st = [s["start"] for s in shots]
        return [b - a for a, b in zip(st, st[1:])] + [len(shots[-1].get("sentence", "").split()) / WPM * 60 + GAP]
    return [len(s.get("sentence", "").split()) / WPM * 60 + GAP for s in shots]

def lint(shots, st, per_min=FLOW_PER_MIN):
    errs, warns = [], []
    dur = durations(shots); minutes = sum(dur) / 60
    per_file = {}
    for s in shots:
        if s["family"] in FAMILY_TEMPLATE: per_file[s.get("file") or f"F{s['i']:03d}"] = per_file.get(s.get("file") or f"F{s['i']:03d}", 0) + 1
    n, budget = len(per_file), int(per_min * minutes + 0.999)
    if n > budget: errs.append(f"{n} Flow images for {minutes:.1f} min, budget {budget} ({per_min:g}/min): hold an image over the next line (R(key, frame)) or use a data insert")
    run = 0
    for k, s in enumerate(shots):                   # an image may come back later (the opening scene at the end), but never 4 lines in a row
        run = run + 1 if k and s.get("file") and s.get("file") == shots[k - 1].get("file") else 1
        if run == 4: errs.append(f"#{s['i']}: {s['file']} held over 4 lines in a row, 3 framings at most per image")
    t = since = 0.0; seen_data = False
    for k, (s, d) in enumerate(zip(shots, dur)):
        fam, low = s["family"], " " + s.get("scene", "").lower() + " "
        first_of_file = not (k and s.get("file") and s.get("file") == shots[k - 1].get("file"))
        if fam in FAMILY_TEMPLATE and first_of_file:
            if not s.get("scene"): errs.append(f"#{s['i']}: empty scene description")
            if hit := [b for b in BANNED if b in low]: errs.append(f"#{s['i']}: banned words {hit} in the scene (they trigger bubbles or fake text)")
            if m := re.search(SILHOUETTE, low): errs.append(f"#{s['i']}: \"{m.group(0)}\": every person has a drawn face, never a silhouette (a Black character = cast \"friend\")")
            if m := re.search(DETAILED, low): errs.append(f"#{s['i']}: \"{m.group(0)}\": all people are stick figures, never mixed with detailed humans")
            if m := re.search(RELIGIOUS, low): errs.append(f"#{s['i']}: religious symbol \"{m.group(0)}\" in the scene")
            cast = [c for c in (s.get("cast") or "").split("+") if c]; era = s.get("era") or "modern"
            for c in cast:
                if c not in st["cast"]: errs.append(f"#{s['i']}: unknown cast member \"{c}\" (known: {', '.join(st['cast'])})")
                elif era not in st["cast"][c]["costumes"]: errs.append(f"#{s['i']}: unknown era \"{era}\"")
            if era == "modern" and (m := re.search(WEAPON, low)): errs.append(f"#{s['i']}: \"{m.group(0)}\" in a modern scene (no spear or weapon outside the tribe era)")
            if ic := code_candidate(s): errs.append(f"#{s['i']}: a simple symbol, draw it by code: {{\"family\": \"html\", \"html\": {{\"type\": \"symbol\", \"icon\": \"{ic}\"}}}}")
            for o in shots[max(0, k - 10):k]:
                if o.get("file") == s.get("file") or o["family"] != fam or o.get("composition") != s.get("composition"): continue
                a, b = tokens(o.get("scene", "")), tokens(s.get("scene", ""))
                if a and b and len(a & b) / len(a | b) > 0.6: warns.append(f"#{s['i']}: near-duplicate of #{o['i']} (same composition, same words)")
        if html_is_data(s):
            if not seen_data and t > FIRST_DATA: errs.append(f"#{s['i']}: first figure on screen at {t:.0f} s, it must come before {FIRST_DATA} s")
            if k and html_is_data(shots[k - 1]): warns.append(f"#{s['i']}: two data inserts in a row, put a scene between")
            seen_data, since = True, 0.0
        else:
            since += d
            if since - d <= DATA_MAX < since: errs.append(f"#{s['i']}: {since:.0f} s without a figure on screen (one data insert every 20 to 25 s, {DATA_MAX} s at most)")
            elif since - d <= DATA_WARN < since: warns.append(f"#{s['i']}: {since:.0f} s since the last data insert (aim for 20 to 25 s)")
        t += d
    if not seen_data: errs.append("no data insert at all (family html with a figure)")
    return errs, warns, n, minutes

def cast_sentences(st, cast, era):
    order = ["Recurring character", "Second recurring character", "Third recurring character"]
    parts = [f"{order[k]}, the {c}: {st['cast'][c]['sheet'].replace('{costume}', st['cast'][c]['costumes'][era])}. Keep this exact character design in every image."
             for k, c in enumerate(cast)]
    parts.append("The same character as in the reference image, exactly the same design." if len(cast) == 1
                 else "The same characters as in the reference images, exactly the same design.")
    return " ".join(parts + [st["crowd"]])

def build(shots, st):
    out, comps, seen = [], itertools.cycle(["wide", "medium", "close", "cutaway", "overhead", "pov"]), set()
    for s in shots:
        fam = s["family"]; f = s.get("file") or f"F{s['i']:03d}"
        if fam not in FAMILY_TEMPLATE or f in seen: continue      # by code, or the same image held over several lines
        seen.add(f)
        cast = [c for c in (s.get("cast") or "").split("+") if c] if fam == "scene" else []
        comp = s.get("composition") or (next(comps) if fam == "scene" else ""); dark = bool(s.get("dark"))
        body = FAMILY_TEMPLATE[fam].format(comp=COMPOSITIONS.get(comp, "").format(pov_hands=st["pov_hands"]), scene=s["scene"].rstrip("."),
                                           scene_bg=st["dark_scene_bg"] if dark else (st["scene_bg"] if cast else st["scene_bg_nochar"]),
                                           insert_bg=st["dark_insert_bg"] if dark else st["insert_bg"])
        parts = [st["prefix"] if fam == "scene" else st["insert_prefix"], cast_sentences(st, cast, s.get("era") or "modern") if cast else "",
                 st["setting"] if fam == "scene" else "", body, st["dark"] if dark else "", st["suffix"]]
        p = {"file": f, "i": s["i"], "family": fam, "prompt": re.sub(r"\s+", " ", " ".join(x for x in parts if x)).strip()}
        if cast: p["refs"] = [st["cast"][c]["ref"] for c in cast]      # attached as Flow ingredients by batch.mjs
        out.append(p)
    return out

def build_thumbs(specs, st):
    """Thumbnail scenes from the same character sheets (covered costumes) and reference images as the video.
    specs = [{"file": "T1", "cast": "hero+heroine+friend", "era": "tribe", "action": "...", "prop": "...", "setting": "..."}]"""
    out = []
    for t in specs:
        cast = t["cast"].split("+"); who = {1: "One character", 2: "Two characters", 3: "Three characters"}[len(cast)]
        scene = st["thumbnail"].format(who=who, action=t["action"].rstrip(". ") + ".", prop=(t["prop"].rstrip(". ") + ".") if t.get("prop") else "", setting=t["setting"].rstrip(". "))
        for rx, what in ((SILHOUETTE, "silhouette"), (RELIGIOUS, "religious symbol"), (DETAILED, "detailed human")):
            if m := re.search(rx, " ".join((t["action"], t.get("prop", ""), t["setting"])).lower()): sys.exit(f"{t['file']}: {what} \"{m.group(0)}\" in the thumbnail spec")
        out.append({"file": t["file"], "refs": [st["cast"][c]["ref"] for c in cast],
                    "prompt": re.sub(r"\s+", " ", " ".join([scene, cast_sentences(st, cast, t.get("era") or "tribe"), st["suffix"]])).strip()})
    return out

def inherit(shots):
    """A shot that reuses the previous shot's file (another framing of the same image) inherits its description."""
    for k, s in enumerate(shots):
        if k and s.get("file") and s.get("file") == shots[k - 1].get("file") and not s.get("scene"):
            for key in ("scene", "composition", "dark", "cast", "era"):
                if key in shots[k - 1] and key not in s: s[key] = shots[k - 1][key]
    return shots

def selftest():
    st = resolve_style(["--brief", "__none__.json"])
    data = {"family": "html", "sentence": "Seventeen percent.", "html": {"type": "card", "icon": "heart", "big": "17%", "small": "of newlyweds"}}
    ok = [{"i": 1, "sentence": "You are at a bar with your friend tonight.", "family": "scene", "file": "F001", "scene": "the hero and his friend at a bar counter", "composition": "wide", "cast": "hero+friend"},
          {"i": 2, **data}]
    errs, warns, n, _ = lint(inherit(ok), st, 60); assert not errs and n == 1, errs
    p = build(ok, st); assert len(p) == 1 and p[0]["refs"] == ["reference.png", "second-male.png"]
    assert "empty-handed" in p[0]["prompt"] and "blond pompadour" in p[0]["prompt"] and "never a black silhouette" in p[0]["prompt"] and "{costume}" not in p[0]["prompt"]
    bad = lambda **kw: " | ".join(lint(inherit([{"i": 1, "sentence": "x " * 10, "family": "scene", "file": "F001", "composition": "wide", **kw}, {"i": 2, **data}]), st, 60)[0])
    assert "modern scene" in bad(scene="the hero holding a spear in a bar", cast="hero")
    assert "modern scene" not in bad(scene="the hero holding a spear by a cave", cast="hero", era="tribe")
    assert "silhouette" in bad(scene="a dark silhouette of a man at a door")
    assert "stick figures" in bad(scene="a detailed cartoon scientist in a lab")
    assert "religious" in bad(scene="a wedding in a church", cast="hero+heroine")
    assert "unknown cast" in bad(scene="a man at a desk", cast="rival")
    assert "banned words" in bad(scene="a phone screen showing a chat")
    slow = [{"i": k, "sentence": "one two three four five six seven eight nine ten eleven twelve", "family": "scene", "file": f"F{k // 3:03d}", "scene": f"place {k // 3} with a tree", "composition": "wide"} for k in range(1, 9)]
    e = " | ".join(lint(inherit(slow + [{"i": 9, **data}]), st, 60)[0]); assert "without a figure" in e and "3 framings" not in e, e
    e = " | ".join(lint(inherit([dict(x, file="F001") for x in slow[:4]] + [{"i": 9, **data}]), st, 60)[0]); assert "3 framings" in e, e
    t = build_thumbs([{"file": "T1", "cast": "hero+heroine+friend", "action": "The woman holds a flat grey stone tablet, both men stare at it", "setting": "a night-blue forest with a full moon"}], st)
    assert t[0]["refs"] == ["reference.png", "heroine.png", "second-male.png"] and "hem down to her ankles" in t[0]["prompt"] and "Three characters" in t[0]["prompt"]
    assert "religious" not in bad(scene="the hero about to cross the street", cast="hero")
    print("selftest ok")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args: selftest(); sys.exit(0)
    if "--thumbs" in args:                                  # python prompts.py --thumbs thumb_specs.json  -> thumbs.json next to it
        src = pathlib.Path(arg_value(args, "--thumbs")); out = src.resolve().parent / "thumbs.json"
        json.dump(build_thumbs(json.load(open(src, encoding="utf-8")), resolve_style(args)), open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"thumbnail prompts -> {out}"); sys.exit(0)
    src = next((a for a in args if not a.startswith("--") and (args.index(a) == 0 or args[args.index(a) - 1] not in ("--brief", "--setting", "--flow-per-min"))), "shots.json")
    shots = inherit(json.load(open(src, encoding="utf-8")))
    st = resolve_style(args)
    errs, warns, n, minutes = lint(shots, st, float(arg_value(args, "--flow-per-min") or FLOW_PER_MIN))
    for e in errs: print("ERROR ", e)
    for w in warns: print("warn  ", w)
    prompts = build(shots, st)
    out = pathlib.Path(src).resolve().parent / "prompts.json"
    json.dump(prompts, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    fams = {}
    for s in shots: fams[s["family"]] = fams.get(s["family"], 0) + 1
    print(f"{len(prompts)} Flow prompts -> {out} | {n} images for {minutes:.1f} min ({n / max(minutes, 0.01):.1f}/min) | "
          f"{sum(1 for s in shots if html_is_data(s))} data inserts | families {fams} | {len(errs)} errors, {len(warns)} warnings")
    if "--strict" in args and errs: sys.exit(1)
