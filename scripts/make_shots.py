"""Shot list of a « Do [Women/Men] Really [X]? What the Data Says » video: one line of script.md = one voice clip = one shot.
Copy this file next to script.md, then, in that folder:
  python make_shots.py --voice     -> shots_voice.json (i, sentence): the voice can start now (tts.py), in parallel with the images
  (replace SPECS below: one list per "## Chapter N — title", one entry per spoken line, in order)
  python make_shots.py             -> shots.json + chapters.json + files.json ; refuses if a line differs from shots_voice.json
  python <skill>/scripts/prompts.py shots.json --strict        (lint + prompts.json)
  python make_shots.py --chapters  -> chapters.md with the real times of timing.json, and where the Short ends (after the voice)

Helpers (one per line of the script):
  S(key, scene, comp, cast, era, dark)   a scene with the recurring cast: cast = "hero", "hero+heroine", "hero+heroine+friend"... ;
                                         era = "modern" (default, no weapon) or "tribe" (fur clothes; ancient history is a short proof only)
  N(key, scene, comp, dark)              a place or an object without the cast (any people = small plain stick figures)
  M(key, scene, dark)                    a visual metaphor on a plain background
  A(key, file, frame, caption)           a ready-made picture: archive photo (cinematic-film fetch_commons.py) or 3D still
                                         (open-3d-skills), read from assets/photos/<file>.jpg|png|webp; caption = its credit
  R(key, frame)                          the same image again with another framing: on the next line (3 lines at most in a row),
                                         or later (the opening scene returns in the last chapter, no new image)
  D(spec) / card(big, small, icon)       a data insert drawn by code (hand-drawn-visuals): card, compare, gauge, bar, line, pie, timeline, list
  DATE(big, sub)                         documentary date card ("1292", "PARIS TAX ROLL"), animated by code (docfx.py)
  CLIP(quote, mark, source, file)        source clipping: exact quote of facts.md, `mark` highlighted, Source label, real page behind
  MAP(places, route, fill, focus)        animated dark map: countries filled, cities pop, dashed route draws (docfx.py)
  T(title)                               a kinetic title card (a short shock line)
  BURST(keys, frame)                     one line, several images already made, cut fast (about 1 to 1.5 s each): lists, contrasts
  src(spec, text)                        a source tag on screen (how the figure was made): the method leaves the voice, not the video
  grade(spec, g) / GRADE = {chapter: g}  colour of the part: cool | warm | night | modern | none (references/structure-ecriture.md §5)
frame = wide | zoom | zoom-out | pan-left | pan-right | left | right. Budget: 6 to 7 Flow images a minute, a data insert every 20 to 25 s.
In script.md a line ending with " //" is a beat: tts.py leaves BEAT seconds of silence after it (mix.py lifts the music there) and
its picture holds; one to three beats a chapter, on the reveals (structure-ecriture.md §5).

SPECS below is the 12-line example of assets/example/script.md (2 blocks instead of 6): replace it with your own.
"""
import json, re, sys, pathlib
HERE = pathlib.Path(__file__).parent
is_flow = lambda f: f[:1] == "F" and f[1:].isdigit()     # F001...: a Flow image; anything else is a ready-made picture A(...)

def S(key, scene, comp="wide", cast="hero", era="modern", dark=False, frame="wide"):
    return {"family": "scene", "key": key, "scene": scene, "composition": comp, "cast": cast, "era": era, "dark": dark, "frame": frame}
def N(key, scene, comp="wide", dark=False, frame="wide"):
    return {"family": "scene", "key": key, "scene": scene, "composition": comp, "dark": dark, "frame": frame}
def M(key, scene, dark=False, kind="metaphor"):
    return {"family": kind, "key": key, "scene": scene, "dark": dark, "frame": "wide"}
def A(key, file, frame="zoom", caption=""):
    """A ready-made picture instead of a Flow image: an archive photo fetched with its licence (cinematic-film fetch_commons.py ->
    assets/photos/P01.jpg), or a still of a 3D scene (open-3d-skills). `file` is the file name without extension; hf_build.py looks
    for it in --flow, then in --photos (default assets/photos). No Flow prompt, no Flow budget. caption = the credit line shown small."""
    return {"family": "archive", "key": key, "photo": file, "frame": frame, **({"caption": caption} if caption else {})}
def R(key, frame="zoom"): return {"family": "reuse", "key": key, "frame": frame}
def D(spec, dark=False): return {"family": "html", "html": spec, "dark": dark}
def card(big, small, icon, layout="left", colour="terra"): return D({"type": "card", "icon": icon, "big": big, "small": small, "layout": layout, "colour": colour})
def T(title): return D({"type": "title", "title": title})
def BURST(items, frame="zoom"):
    """items = keys of images made earlier, or new S/N/M/A specs (each becomes its own image, as on its own line)."""
    return {"family": "burst", "keys": list(items), "frame": frame}
def src(spec, text): return {**spec, "src": text}
def grade(spec, g): return {**spec, "grade": g}
BEAT = 0.9            # seconds of silence after a line ending with " //"
GRADE = {}            # {chapter number: "cool" | "warm" | "night" | "modern"}: the colour of each part; a shot's own grade() wins
# Documentary shots drawn by code (scripts/docfx.py, style: references/documentaire.md). No Flow image, no Flow budget.
def DATE(big, sub=""): return {"family": "docdate", "doc": {"big": big, "sub": sub}}
def CLIP(quote, mark="", source="", file=None):
    """A source clipping: the exact quote of facts.md on a paper card, `mark` highlighted, "Source: ..." label; `file` = an
    assets/photos picture (P01...) shown blurred behind the card (the real page)."""
    return {"family": "clipping", "doc": {"quote": quote, "mark": mark, "source": source, **({"file": file} if file else {})}}
def MAP(places, route=None, fill=None, focus=None, view=None, title=None, zoom=1.35):
    """Animated map: places = city names of docfx.CITIES or [name, lat, lon]; route = the same, drawn as a dashed line;
    fill = ISO3 codes of countries in the accent colour (FRA, AUT, BEL, NLD, GBR...); focus = where the camera pushes in."""
    return {"family": "docmap", "doc": {"places": places, "route": route or [], "fill": fill or [], "focus": focus, "view": view, "title": title, "zoom": zoom}}

GRADE = {1: "modern", 2: "cool", 3: "night", 4: "warm", 5: "modern"}   # one colour per part (structure-ecriture.md §5)
BAR = "a small warm bar in the evening, wooden counter, hanging lamps"

SPECS = {
 1: [   # 0:00-1:00 the question of the title in a concrete scene, then the first figure, then "But..." (this chapter is also the Short)
  S("bar", "the hero on a stool at the counter of " + BAR + ", looking up at his friend who stands a head taller beside him, the heroine smiling at the friend from the next stool", "wide", cast="hero+heroine+friend"),
  R("bar", "zoom"),
  card("7 in 10", "said yes (example survey)", "users"),
  S("phone", "the hero alone at the counter of " + BAR + ", frowning at a blank glowing phone in his hand, one eyebrow raised", "medium"),
 ],
 2: [   # one block = one study: the claim, the figure on screen, what the figure does not say, an open loop
  N("clipboard", "a plain blank clipboard and a pencil on a round cafe table by a window, morning light", "close"),
  D({"type": "compare", "left": "the wish", "right": "+4 inches", "icon_left": "heart", "icon_right": "ruler", "sign": "→"}),
  S("gap", "the heroine at a cafe table, pointing one way with her hand while looking the other way, the friend sitting across with a puzzled face", "medium", cast="heroine+friend"),
 ],
 3: [   # the reversal: the data contradicts the belief
  D({"type": "gauge", "icon": "users", "big": "1 in 10", "small": "couples matched the wish", "value": 0.1}),
  M("door", "a tall door standing half open on a dark floor, warm golden light pouring through the gap"),
 ],
 4: [   # the honest answer in one sentence: individual preference versus social bias
  S("walk", "the hero and the heroine walking side by side down a city street at dusk, both laughing, he is a little shorter than her", "wide", cast="hero+heroine"),
 ],
 5: [   # back to the opening scene (same image, no new generation), then the question to the viewer
  R("bar", "wide"),
  R("bar", "zoom-out"),
 ],
}

def chapters():
    text = (HERE / "script.md").read_text(encoding="utf-8")
    out = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        head, *lines = block.strip().splitlines()
        if not head.lower().startswith("chapter"): continue      # "## Sources" and other notes are not spoken
        m = re.match(r"Chapter (\d+) — (.+)", head)
        assert m, f"bad chapter header: {head!r} (expected '## Chapter N — title')"
        out.append((int(m.group(1)), m.group(2).strip(), [l.strip() for l in lines if l.strip() and not l.strip().startswith("<!--")]))
    return out

def mmss(t): return f"{int(t) // 60:02d}:{int(t) % 60:02d}"

def main():
    chaps = chapters(); vp = HERE / "shots_voice.json"
    beat = lambda l: l.rstrip().endswith("//")
    clean = lambda l: l.rstrip().removesuffix("//").rstrip()
    voice = [{"i": n + 1, "sentence": clean(l), **({"pause": BEAT} if beat(l) else {})} for n, l in enumerate(l for _, _, ls in chaps for l in ls)]
    if "--voice" in sys.argv:        # the voice cache (tts/) is keyed on these sentences: only changed lines are generated and paid again
        old = {v["i"]: v["sentence"] for v in json.loads(vp.read_text(encoding="utf-8"))} if vp.exists() else {}
        vp.write_text(json.dumps(voice, indent=0, ensure_ascii=False), encoding="utf-8")
        return print(f"shots_voice.json: {len(voice)} lines, {sum(len(v['sentence'].split()) for v in voice)} words"
                     + (f", {sum(1 for v in voice if old.get(v['i']) != v['sentence'])} changed since the last run" if old else ""))
    if "--chapters" in sys.argv:     # real times, never an estimate
        timing = json.loads((HERE / "timing.json").read_text(encoding="utf-8")); starts = timing["starts"] if isinstance(timing, dict) else timing
        first, rows = 0, []
        for num, title, lines in chaps: rows.append((starts[first], title)); first += len(lines)
        short = [a[1] for a, b in zip(rows, rows[1:]) if b[0] - a[0] < 10]
        assert rows[0][0] < 1 and len(rows) >= 3 and not short, f"YouTube shows chapters only with 00:00 first, 3 or more, 10 s each (too short: {short})"
        (HERE / "chapters.md").write_text("\n".join(f"{mmss(t)} {title}" for t, title in rows) + "\n", encoding="utf-8")
        return print(f"chapters.md: {len(rows)} chapters | the Short = chapter 1, cut at {rows[1][0]:.2f} s" + ("" if rows[1][0] <= 60 else "  (over 60 s: shorten chapter 1)"))
    shots, chap_index, files, last = [], [], {}, {}
    for num, title, lines in chaps:
        specs = SPECS[num]
        assert len(specs) == len(lines), f"chapter {num}: {len(lines)} lines but {len(specs)} specs"
        chap_index.append({"chapter": num, "title": title, "shot": len(shots) + 1})
        for line, spec in zip(lines, specs):
            pause = BEAT if line.rstrip().endswith("//") else 0; line = line.rstrip().removesuffix("//").rstrip()
            if spec["family"] == "burst":
                for it in [k for k in spec["keys"] if isinstance(k, dict)]:   # a new image inside the burst: registered like a line of its own
                    assert it["key"] not in files, f"duplicate key {it['key']!r}"
                    files[it["key"]] = it.get("photo") or f"F{sum(1 for v in files.values() if is_flow(v)) + 1:03d}"
                    last[it["key"]] = {"file": files[it["key"]], "family": it["family"], "sentence": line, **{k: it[k] for k in ("scene", "composition", "cast", "era", "caption") if it.get(k)}}
                spec = {**spec, "keys": [k["key"] if isinstance(k, dict) else k for k in spec["keys"]]}
                miss = [k for k in spec["keys"] if k not in last]
                assert not miss and len(spec["keys"]) >= 2, f"BURST({spec['keys']}) needs 2 or more keys made before it (missing {miss}), line {line!r}"
                s = {"i": len(shots) + 1, "sentence": line, "family": "burst", "burst": [last[k]["file"] for k in spec["keys"]], "frame": spec["frame"]}
            elif spec["family"] == "reuse":
                assert spec["key"] in last, f"R({spec['key']!r}) before its image (line {line!r})"
                s = {**last[spec["key"]], "i": len(shots) + 1, "sentence": line, "frame": spec["frame"]}
            else:
                s = {"i": len(shots) + 1, "sentence": line, "family": spec["family"]}
                if "key" in spec:
                    assert spec["key"] not in files, f"duplicate key {spec['key']!r}"
                    files[spec["key"]] = s["file"] = spec.get("photo") or f"F{sum(1 for v in files.values() if is_flow(v)) + 1:03d}"
                    for k in ("scene", "composition", "cast", "era", "frame", "caption"):
                        if spec.get(k): s[k] = spec[k]
                    if not s.get("cast"): s.pop("era", None)
                    last[spec["key"]] = s
                if spec["family"] == "html": s["html"] = spec["html"]
                if "doc" in spec: s["doc"] = spec["doc"]
                if spec.get("dark"): s["dark"] = True
            for k in ("src", "grade"):
                if spec.get(k): s[k] = spec[k]
            if not s.get("grade") and GRADE.get(num): s["grade"] = GRADE[num]
            if pause: s["pause"] = pause
            s["chapter"] = num
            shots.append(s)
    if vp.exists():
        diff = [v["i"] for v, s in zip(json.loads(vp.read_text(encoding="utf-8")), shots) if v["sentence"] != s["sentence"]]
        assert not diff and len(json.loads(vp.read_text(encoding="utf-8"))) == len(shots), f"script.md differs from shots_voice.json (lines {diff[:8]}): run --voice, then tts.py again"
    tp = HERE / "timing.json"      # after the voice: the real start of every line, so prompts.py measures the real gaps between data inserts (11 Nov 2026)
    if tp.exists():
        t = json.loads(tp.read_text(encoding="utf-8")); starts = t["starts"] if isinstance(t, dict) else t
        if len(starts) == len(shots):
            for s, st in zip(shots, starts): s["start"] = round(float(st), 3)
    # the rules of the structure that depend on the pictures (the words are checked by yt/script_lint.py)
    bounds = [c["shot"] - 1 for c in chap_index] + [len(shots)]
    has_figure = lambda s: s["family"] == "html" and s["html"].get("type") != "title" and re.search(r"\d", json.dumps(s["html"]))
    for c, a, b in zip(chap_index[:-2], bounds, bounds[1:]):     # chapter 1 and every block: a figure on screen
        assert any(has_figure(s) for s in shots[a:b]), f"chapter {c['chapter']} ({c['title']}): no figure on screen (add a D(...) insert)"
    opening = next(s["file"] for s in shots if s.get("file"))
    assert any(s.get("file") == opening for s in shots[bounds[-2]:]), "the last chapter must return to the opening scene: R(<key of the first image>)"
    # anti-boredom rules of the pictures (22 Nov 2026, bath video: one image on 11 shots, 5 of 12 pictures of minute 8 unrelated to the line)
    places = {}
    for k, s in enumerate(shots):
        for f in s.get("burst") or ([s["file"]] if s.get("file") else []):
            if not (k and f in (shots[k - 1].get("burst") or [shots[k - 1].get("file")])): places.setdefault(f, []).append(s["i"])
    over = {f: v for f, v in places.items() if len(v) > 2 and f != opening}
    assert not over, f"images shown in more than 2 places (consecutive R lines count once; the opening scene is exempt): {dict(list(over.items())[:6])}: make a DATE, CLIP, MAP, insert or BURST instead"
    if len(chap_index) > 1 and len({s.get("grade") for s in shots}) < 2: print("WARN one colour for the whole video: set GRADE per part (structure-ecriture.md §5)")
    for name, obj in (("shots.json", shots), ("files.json", files), ("chapters.json", chap_index)):
        (HERE / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    fam = {}
    for s in shots: fam[s["family"]] = fam.get(s["family"], 0) + 1
    n_flow = sum(1 for v in files.values() if is_flow(v))
    print(f"{len(shots)} shots in {len(chap_index)} chapters, {n_flow} Flow images, {len(files) - n_flow} ready-made pictures (A), {sum(1 for s in shots if has_figure(s))} data inserts, families {fam}")

if __name__ == "__main__":
    main()
