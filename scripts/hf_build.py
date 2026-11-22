"""Build a HyperFrames project (HTML rendered to video) from shots.json + voice: animated captions and motion-design titles.

  python hf_build.py shots.json voice.wav timing.json <project_dir> --flow flow/<video> --split-long 2.5
                     [--no-captions] [--accent "#F2C446"] [--static-inserts] [--photos assets/photos]
  then: npx hyperframes check <project_dir> --json ; npx hyperframes preview <project_dir> ; npx hyperframes render <project_dir>

What it writes (the HyperFrames contract, references/format.md of the hyperframes skill):
  index.html                 root composition: one scene host per chapter (data-track-kind="graphics"), one captions host
                             (data-track-kind="captions"), <audio id="voice">
  compositions/chN.html      one .clip per shot, hard cuts; the image sits in a .kb wrapper that GSAP zooms/pans by "frame"
                             (wide | zoom | zoom-out | pan-left | pan-right | left | right); "title" shots are kinetic
                             typography (words blur in 0.067 s apart, accent on the last word, dead still, blur out)
  compositions/captions.html one group of 3-5 words per .clip, active word popped in the accent colour, hard kill at the end
  assets/                    F###.png from --flow, data inserts from <flow>/html/H<i>.png (hand-drawn-visuals render.mjs --shots), voice.wav
Data inserts: with <flow>/html/H<i>.anim.json next to the PNG (render.mjs --shots --anim), the insert is mounted as live SVG + text and
GSAP builds it in (bars grow, figures count up, icons pop, labels fade), then it holds under a slow push-in; without that file, or with
--static-inserts, the PNG is shown still. The PNG is always needed: it is the one read on the contact sheet and it sizes the caption fit.
Ready-made pictures (family "archive", make_shots.A(...)): archive photos or 3D stills of any shape, framed whole over a blurred copy
with their credit line at the top right; they move like a Flow image (same "frame" zooms and pans).
Word timings come from tts.py's timing.json ({"chars", "end", "starts"}, VoiceStudio or ElevenLabs); with a plain list of starts the words are spread
evenly inside each line. The music bed is NOT added here: it is mixed after the render at a measured level (references/voix-musique.md).
Anti-boredom fields of make_shots.py (22 Nov 2026, references/structure-ecriture.md §5): "burst" = several images on one line, cut
fast in turn; "src" = a source tag at the top left (how the figure was made, so the voice no longer says it); "grade" = the colour of
the part (cool | warm | night | modern), a CSS filter and tint on the pictures only, never on inserts, maps or titles.
A missing image becomes a cream card carrying the sentence and its name is printed (exit code 1): fix it before the render.
"""
import json, pathlib, re, shutil, subprocess, sys
import imageio_ffmpeg
sys.path.insert(0, str(pathlib.Path(__file__).parent)); import docfx   # documentary shots: DATE, CLIP, MAP (merged 22 Nov 2026)
DOC = {"docdate", "clipping", "docmap"}
from PIL import Image, ImageChops, ImageDraw, ImageFont

W, H = 1920, 1080

def starts_from_timing(shots, timing):
    """One start per shot: tts.py writes them ("starts"); a plain list is accepted too."""
    starts = timing["starts"] if isinstance(timing, dict) else timing
    assert len(starts) == len(shots), f"{len(starts)} starts in timing.json for {len(shots)} shots: the voice was made from another script (make_shots.py --voice, then tts.py)"
    return [float(t) for t in starts]

PHOTOS = pathlib.Path("assets/photos")   # --photos: where A(...) pictures live (cinematic-film fetch_commons.py downloads there)

def framed(im, caption=""):
    """An archive photo or 3D still of any shape on the 16:9 canvas: whole picture (never cropped, never stretched) over a
    blurred, darkened copy of itself, credit line small at the top right (the captions own the bottom band)."""
    from PIL import ImageFilter, ImageEnhance
    im = im.convert("RGB"); r = min(W / im.width, H / im.height)
    bg = im.resize((max(W, int(im.width * H / im.height)), max(H, int(im.height * W / im.width))))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.45)
    fg = im.resize((int(im.width * r), int(im.height * r))); bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    if caption:
        d = ImageDraw.Draw(bg)
        try: f = ImageFont.truetype("Arial.ttf", 22)
        except OSError: f = ImageFont.load_default()
        tw = d.textlength(caption, font=f); d.rectangle((W - tw - 36, 18, W - 14, 54), fill=(0, 0, 0)); d.text((W - tw - 25, 24), caption, font=f, fill=(235, 235, 235))
    return bg

def render(s, flow_dir):
    """The picture of a shot: a data insert drawn beforehand by hand-drawn-visuals, the Flow image, or a ready-made picture
    (family "archive": in --flow, then in --photos). None when it is missing."""
    names = [f"html/H{s['i']:04d}.png"] if s["family"] == "html" else [f"{s.get('file') or 'F%03d' % s['i']}{e}" for e in (".png", ".jpg", ".jpeg", ".webp")]
    dirs = [flow_dir, PHOTOS] if s["family"] == "archive" else [flow_dir]
    f = next((d / n for d in dirs for n in names if (d / n).exists()), None)
    if not f and s["family"] == "archive":   # fetch_commons.py names its downloads P01_<title>.jpg: match on the id prefix
        f = next((p for d in dirs if d.exists() for p in sorted(d.glob(f"{s.get('file')}_*")) if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff")), None)
    if not f: return None
    return framed(Image.open(f), s.get("caption", "")) if s["family"] == "archive" else Image.open(f).convert("RGB").resize((W, H))

def fallback(text):
    im = Image.new("RGB", (W, H), (245, 239, 224)); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype("C:/Windows/Fonts/segoepr.ttf", 64)
    except OSError: f = ImageFont.load_default()
    lines, cur = [], ""
    for w in text.split():
        if d.textlength((cur + " " + w).strip(), font=f) <= 1500: cur = (cur + " " + w).strip()
        else: lines.append(cur); cur = w
    lines.append(cur)
    for i, ln in enumerate(lines): d.text((W // 2, H // 2 - 40 * len(lines) + i * 80), ln, font=f, fill=(30, 27, 22), anchor="mm")
    return im
CAP_TOP = 860   # px; the caption box spans ~897-984 (bottom 96 px): flat-paper inserts drawn lower are shrunk above it
FIT = {}        # asset path -> (scale, background colour) for those inserts
FRAMES = {   # (scale from, scale to, x from, x to) in px of the 1920 canvas; y stays centred
    "wide": (1.00, 1.07, 0, 0), "zoom": (1.15, 1.30, 0, 0), "zoom-out": (1.30, 1.10, 0, 0),
    "pan-left": (1.20, 1.20, 192, -192), "pan-right": (1.20, 1.20, -192, 192),
    "left": (1.25, 1.29, 240, 240), "right": (1.25, 1.29, -240, -240),
}

SPLIT = 0.0   # seconds; --split-long N splits every moving clip longer than N into two framings (0 = off)
SUBCUT = {"wide": "zoom", "zoom": "pan-left", "zoom-out": "zoom", "pan-left": "zoom", "pan-right": "zoom", "left": "zoom", "right": "zoom"}

GRADES = {   # CSS filter on the picture + a tint laid over it (soft-light): one look per part of the video
    "cool":   ("saturate(0.8) brightness(1.02) contrast(1.05) hue-rotate(-8deg)", "rgba(70,130,200,.28)"),
    "modern": ("saturate(1.05) brightness(1.08) contrast(1.04)", "rgba(150,200,255,.22)"),
    "warm":   ("saturate(1.15) brightness(1.02) contrast(1.03)", "rgba(255,150,60,.25)"),
    "night":  ("saturate(0.6) brightness(0.72) contrast(1.12) hue-rotate(-20deg)", "rgba(20,40,110,.35)"),
}

def pill(s):
    """Source tag at the top left: the method of the figure on screen (the voice says the figure, the screen says how it was made)."""
    return f'<div class="srctag"><b>SOURCE</b> {esc(s["src"])}</div>' if s.get("src") else ""

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def words_from_eleven(timing):
    """ElevenLabs with-timestamps: one end time per character of the voiced text -> word timings."""
    chars, end = timing["chars"], timing["end"]; out = []; k = 0
    while k < len(chars):
        if chars[k].isspace(): k += 1; continue
        j = k
        while j < len(chars) and not chars[j].isspace(): j += 1
        out.append({"text": chars[k:j], "start": end[k - 1] if k else 0.0, "end": end[j - 1]}); k = j
    return out

def words_even(shots, starts, ends):
    out = []
    for s, a, b in zip(shots, starts, ends):
        ws = s["sentence"].split(); step = (b - a) / max(1, len(ws))
        for n, w in enumerate(ws): out.append({"text": w, "start": a + n * step, "end": a + (n + 1) * step - 0.02})
    return out

def groups(words, max_words=4):
    """3-5 words per group: break at sentence end, a pause >= 150 ms, or max_words."""
    gs, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or (w["start"] - cur[-1]["end"]) >= 0.15 or re.search(r"[.!?]$", cur[-1]["text"])):
            gs.append(cur); cur = []
        cur.append(w)
    if cur: gs.append(cur)
    return gs

def kb_tween(sel, frame, start, dur):
    s0, s1, x0, x1 = FRAMES.get(frame, FRAMES["wide"])
    return f'tl.fromTo("{sel}", {{scale: {s0}, x: {x0}, y: 0}}, {{scale: {s1}, x: {x1}, y: 0, duration: {dur:.3f}, ease: "none"}}, {start:.3f});'

ANIM = {}       # shot i -> {"dark", "html", "items"}: inserts exported by hand-drawn-visuals `render.mjs --anim` (none = the PNG, still)
FONT_CSS = ""   # @font-face of the two hand fonts of the inserts (html/fonts/fonts.css), written in every scene that has a live insert

def insert_tweens(sid, a, st, du):
    """Entrances of a live data insert, in reading order (bar grows, figure counts up, curve draws, icon pops, label fades).
    Everything is in place before half of the clip, then it holds under a slow push-in. A count-up keeps the final figure in
    the HTML and writes it back at the end, so a tween that fails still shows the true number."""
    items = a["items"]; step = min(0.15, min(1.4, 0.45 * du) / max(1, len(items))); end = st + du - 0.05; tw = []
    cd = max(0.7, min(1.2, 0.4 * du)); prev = (None, 0.0)   # one duration for a figure and the bar that carries it: they start and land together
    def add(sel, frm, to, t, d, ease):
        d = max(0.1, min(d, end - t))   # nothing lands after the clip
        tw.append(f'tl.fromTo("{sel}", {json.dumps(frm)}, {json.dumps({**to, "duration": round(d, 3), "ease": ease})}, {t:.3f});')
    for k, it in enumerate(items):
        t = min(st + 0.08 + k * step, end - 0.1); sel = "#" + it["id"].replace("__ID__", sid); kind = it["kind"]
        if {kind, prev[0]} in ({"count", "grow"}, {"count", "growx"}): t = prev[1]
        prev = (kind, t)
        if kind in ("grow", "growx"):
            ax = "scaleY" if kind == "grow" else "scaleX"; o = f'{it["ox"]:.1f} {it["oy"]:.1f}'
            add(sel, {ax: 0, "svgOrigin": o}, {ax: 1, "svgOrigin": o}, t, cd, "power2.out")
        elif kind == "draw":
            for p in it["paths"]: add("#" + p["id"].replace("__ID__", sid), {"strokeDashoffset": p["len"]}, {"strokeDashoffset": 0}, t, 0.8, "power2.inOut")
        elif kind == "fade": add(sel, {"opacity": 0, "y": 14}, {"opacity": 1, "y": 0}, t, 0.3, "power2.out")
        else:   # pop, count
            add(sel, {"opacity": 0, "scale": 0.7, "transformOrigin": "50% 50%"}, {"opacity": 1, "scale": 1}, t, 0.4, "back.out(1.7)")
            if kind == "count":
                d = max(0.1, min(cd, end - t)); args = json.dumps([sel, it["to"], it["pre"], it["suf"], it["dec"], it["grp"], it["text"]])
                tw.append(f'tl.to({{v: 0}}, {{v: {it["to"]}, duration: {d:.3f}, ease: "power2.out", onUpdate: function () {{ cnt(this.targets()[0].v, ...{args}); }}}}, {t:.3f});')
    tw.append(f'tl.fromTo("#{sid} .kb", {{scale: 1}}, {{scale: 1.025, duration: {du:.3f}, ease: "none"}}, {st:.3f});')
    return tw

def chapter_scene(cid, shots_in, t0, assets_rel, accent):
    """One scene file: local clock starts at the chapter's first shot."""
    clips, tw = [], []; live = False
    for z, (s, a, b) in enumerate(shots_in, 1):
        st, du = a - t0, max(b - a, 0.4); sid = f"{cid}-s{s['i']}"
        if s["family"] in DOC:   # documentary shots drawn by code (docfx.py): date card, source clipping, animated map
            d = s.get("doc") or {}
            if s["family"] == "docdate": h, t = docfx.date_html(sid, d, accent, st, du)
            elif s["family"] == "clipping": h, t = docfx.clip_html(sid, d, assets_rel.get(s["i"]), st, du)
            else: h, t = docfx.map_html(sid, d, accent, st, du)
            clips.append(f'<div id="{sid}" class="clip" data-start="{st:.3f}" data-duration="{du:.3f}" style="z-index:{z}">{h}{pill(s)}</div>'); tw.extend(t)
            if s.get("src"): tw.append(f'tl.fromTo("#{sid} .srctag", {{opacity: 0, x: -24}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power2.out"}}, {st + 0.4:.3f});')
            continue
        if s["family"] == "title":
            ws = s["title"].split()
            spans = "".join(f'<span class="w">{esc(w)}</span> ' for w in ws[:-1]) + f'<span class="w acc">{esc(ws[-1])}</span>'
            clips.append(f'<div id="{sid}" class="clip title" data-start="{st:.3f}" data-duration="{du:.3f}" style="z-index:{z}"><div class="tt"><h1>{spans}</h1></div></div>')
            tw.append(f'tl.fromTo("#{sid} .w", {{opacity: 0, filter: "blur(8px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power4.out", stagger: 0.067}}, {st + 0.1:.3f});')
            tw.append(f'tl.to("#{sid} .tt", {{opacity: 0, filter: "blur(6px)", duration: 0.15, ease: "power3.in"}}, {st + du - 0.16:.3f});')
        else:
            moving = s["family"] != "html"; fr = s.get("frame", "wide")
            parts = [(st, du, fr)]
            if s["family"] == "burst":   # one line, several images cut fast in turn (frames alternate so each cut also moves differently)
                k = len(s["burst"]); h = du / k; parts = []
                for n in range(k): parts.append((st + n * h, h, fr)); fr = SUBCUT.get(fr, "zoom")
            if moving and SPLIT and du > SPLIT:   # --split-long: a long clip becomes ceil(du/N) framings of the same image (the reference cuts every 2 s)
                k = -int(-du // SPLIT); h = du / k; parts = []
                for n in range(k): parts.append((st + n * h, h, fr)); fr = SUBCUT.get(fr, "zoom")
            for n, (pst, pdu, pfr) in enumerate(parts):
                pid = sid if n == 0 else f"{sid}{chr(97 + n)}"; src = assets_rel[s["i"]]
                if isinstance(src, list): src = src[n % len(src)]
                gcls = f' g-{s["grade"]}' if moving and s.get("grade") in GRADES else ""
                fit = FIT.get(src) if not moving else None   # static insert whose labels would sit under the captions
                bg, ist = (f";background:{fit[1]}", f' style="transform:scale({fit[0]:.3f});transform-origin:50% 0"') if fit else ("", "")
                a = ANIM.get(s["i"]) if not moving else None
                if a:   # live insert: the drawing itself (SVG + text) instead of its PNG, so GSAP can move each part
                    live = True; bgc = fit[1] if fit else ("#26303c" if a["dark"] else "#f5efe0")
                    clips.append(f'<div id="{pid}" class="clip" data-start="{pst:.3f}" data-duration="{pdu:.3f}" style="z-index:{z};background:{bgc}"><div class="kb"><div class="ins{" dark" if a["dark"] else ""}"{ist}>{a["html"].replace("__ID__", pid)}</div></div></div>')
                    tw.extend(insert_tweens(pid, a, pst, pdu)); continue
                clips.append(f'<div id="{pid}" class="clip{gcls}" data-start="{pst:.3f}" data-duration="{pdu:.3f}" style="z-index:{z}{bg}"><div class="kb"><img src="{src}" alt=""{ist}></div>{pill(s)}</div>')
                if moving: tw.append(kb_tween(f"#{pid} .kb", pfr, pst, pdu))
                if s.get("src") and n == 0: tw.append(f'tl.fromTo("#{pid} .srctag", {{opacity: 0, x: -24}}, {{opacity: 1, x: 0, duration: 0.35, ease: "power2.out"}}, {pst + 0.4:.3f});')
    return f"""<template>
<style>
#root {{ position: absolute; inset: 0; background: #0b0f1a; overflow: hidden; }}
.clip {{ position: absolute; inset: 0; }}
.kb {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
.kb img {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
.title .tt {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 160px; }}
.title h1 {{ font-family: Oswald, Inter, sans-serif; font-weight: 700; font-size: 128px; line-height: 1.05; color: #fff; letter-spacing: 0.02em; text-transform: uppercase; text-shadow: 0 6px 24px rgba(0,0,0,.6); margin: 0; }}
.title .acc {{ color: {accent}; }}
.srctag {{ position: absolute; left: 36px; top: 30px; max-width: 1100px; padding: 10px 18px; border-left: 6px solid {accent}; background: rgba(8,10,16,.78); color: #e8e8e8; font-family: Inter, sans-serif; font-size: 26px; font-weight: 500; line-height: 1.3; z-index: 3; }}
.srctag b {{ color: {accent}; font-weight: 800; letter-spacing: .08em; margin-right: 10px; }}
{"".join(f".g-{g} .kb img {{ filter: {f}; }} .g-{g} .kb::after {{ content: ''; position: absolute; inset: 0; background: {c}; mix-blend-mode: soft-light; }} " for g, (f, c) in GRADES.items())}
{FONT_CSS if live else ""}
{docfx.CSS}
.ins {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; font-family: 'Patrick Hand', sans-serif; font-size: 16px; font-weight: 400; line-height: normal; color: #1e1b16; }}
.ins.dark {{ color: #f5efe0; }}
.ins svg.layer {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; }}
.ins .abs {{ position: absolute; }}
.ins .num {{ font-family: 'Caveat', sans-serif; font-weight: 700; line-height: 1; }}
.ins .cap {{ color: #96918a; }} .ins.dark .cap {{ color: #bec4cc; }}
.ins .center {{ left: 0; width: {W}px; text-align: center; }}
</style>
<div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{chr(10).join(clips)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const cnt = (v, sel, to, pre, suf, dec, grp, text) => {{ const e = document.querySelector(sel); if (e) e.textContent = v >= to ? text : pre + v.toLocaleString("en-US", {{ minimumFractionDigits: dec, maximumFractionDigits: dec, useGrouping: grp }}) + suf; }};
{chr(10).join(tw)}
window.__timelines["{cid}"] = tl;
</script>
</template>
"""

def captions_scene(gs, accent):
    clips, tw = [], []
    for n, g in enumerate(gs, 1):
        a, b = max(0.1, g[0]["start"]), g[-1]["end"] + 0.08; gid = f"cap{n}"
        spans = " ".join(f'<span class="cw" id="{gid}w{k}">{esc(w["text"])}</span>' for k, w in enumerate(g))
        clips.append(f'<div id="{gid}" class="clip cg" data-start="{a:.3f}" data-duration="{b - a:.3f}" style="z-index:{n}"><p>{spans}</p></div>')
        tw.append(f'tl.fromTo("#{gid} p", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power3.out"}}, {a:.3f});')
        for k, w in enumerate(g):
            ws = max(a, w["start"])   # pop then settle: a word left at 1.08 grew into its neighbour (long words looked glued)
            tw.append(f'tl.fromTo("#{gid}w{k}", {{scale: 1, color: "#ffffff"}}, {{scale: 1.08, color: "{accent}", duration: 0.08, ease: "power2.out"}}, {ws:.3f});')
            tw.append(f'tl.to("#{gid}w{k}", {{scale: 1, duration: 0.12, ease: "power2.inOut"}}, {ws + 0.08:.3f});')
        fo = max(a + 0.15, b - 0.12)   # a group shorter than 0.27 s: the fade-out starts after the fade-in ends (check: overlapping_gsap_tweens)
        tw.append(f'tl.to("#{gid} p", {{opacity: 0, duration: {max(0.05, b - fo):.3f}, ease: "power2.in"}}, {fo:.3f});')
        tw.append(f'tl.set("#{gid} p", {{opacity: 0, visibility: "hidden"}}, {b + 0.001:.3f});')   # hard kill on the inner block, never on the .clip
    return f"""<template>
<style>
#root {{ position: absolute; inset: 0; }}
.cg {{ position: absolute; left: 0; right: 0; bottom: 96px; text-align: center; overflow: visible; }}
.cg p {{ display: inline-block; margin: 0; padding: 10px 28px; border-radius: 14px; background: rgba(0,0,0,.35); font-family: Inter, sans-serif; font-weight: 800; font-size: 56px; line-height: 1.2; color: #fff; text-shadow: 0 2px 0 #000, 0 0 12px rgba(0,0,0,.8); }}
.cw {{ display: inline-block; margin: 0 0.14em; transform-origin: 50% 80%; }}
</style>
<div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{chr(10).join(clips)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
window.__timelines["captions"] = tl;
</script>
</template>
"""

def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--") and (sys.argv[sys.argv.index(x) - 1] not in ("--flow", "--accent", "--split-long", "--photos"))]
    opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    globals()["SPLIT"] = float(opt("--split-long", 0)); globals()["PHOTOS"] = pathlib.Path(opt("--photos", "assets/photos"))
    shots_f, voice, timing_f, proj = a[0], a[1], a[2], pathlib.Path(a[3])
    flow_dir = pathlib.Path(opt("--flow", "flow")); accent = opt("--accent", "#F2C446")
    shots = json.load(open(shots_f, encoding="utf-8")); timing = json.load(open(timing_f, encoding="utf-8"))
    for s in shots:   # make_shots.T() writes titles as html cards: render them as kinetic titles (last word in accent colour)
        if s.get("family") == "html" and s.get("html", {}).get("type") == "title":
            s["family"], s["title"] = "title", s["html"]["title"]
    starts = starts_from_timing(shots, timing)
    FF = imageio_ffmpeg.get_ffmpeg_exe()
    hh, mm, ss = subprocess.run([FF, "-i", voice], capture_output=True, text=True).stderr.split("Duration: ")[1].split(",")[0].split(":")
    dur = 3600 * int(hh) + 60 * int(mm) + float(ss); ends = starts[1:] + [dur]
    (proj / "compositions").mkdir(parents=True, exist_ok=True); (proj / "assets").mkdir(exist_ok=True)
    shutil.copy(voice, proj / "assets" / "voice.wav")
    # images: each Flow file and each data insert copied once
    assets_rel, done, missing = {}, {}, []
    for s in shots:
        if s["family"] == "title" or s["family"] in DOC:
            if s["family"] == "clipping" and (s.get("doc") or {}).get("file"):   # the real page behind a source clipping
                pg = s["doc"]["file"]
                if pg not in done:
                    im = render({"family": "archive", "file": pg, "i": s["i"]}, flow_dir)
                    if im is None: missing.append(pg)
                    else: im.convert("RGB").save(proj / "assets" / f"{pg}.png", compress_level=1); done[pg] = f"assets/{pg}.png"
                if pg in done: assets_rel[s["i"]] = done[pg]
            continue
        if s["family"] == "burst":   # each image of the burst copied once, like any Flow image
            rel = []
            for f in s["burst"]:
                if f not in done:
                    im = render({"family": "scene", "file": f, "i": s["i"]}, flow_dir)
                    if im is None: missing.append(f); im = fallback(s["sentence"])
                    im.convert("RGB").resize((W, H)).save(proj / "assets" / f"{f}.png", compress_level=1); done[f] = f"assets/{f}.png"
                rel.append(done[f])
            assets_rel[s["i"]] = rel; continue
        key = s.get("file") or f"i{s['i']}"
        if key not in done:
            im = render(s, flow_dir)
            if im is None: missing.append(key); im = fallback(s["sentence"])
            name = f"{key}.png"; im = im.convert("RGB").resize((W, H)); im.save(proj / "assets" / name, compress_level=1); done[key] = f"assets/{name}"
            if s["family"] == "html":   # flat paper insert whose drawing reaches the caption band: shrink it from the top (textured bleed = bbox to the edge = left alone)
                bgc = im.getpixel((2, 2)); box = ImageChops.difference(im, Image.new("RGB", im.size, bgc)).convert("L").point(lambda v: 255 if v > 24 else 0).getbbox()
                if box and CAP_TOP < box[3] < H - 2: FIT[done[key]] = (CAP_TOP / box[3], "#%02x%02x%02x" % bgc)
                af = flow_dir / "html" / f"H{s['i']:04d}.anim.json"   # written by render.mjs --anim next to the PNG
                if af.exists() and "--static-inserts" not in sys.argv: ANIM[s["i"]] = json.load(open(af, encoding="utf-8"))
        assets_rel[s["i"]] = done[key]
    if ANIM:   # the hand fonts of the live inserts, as project files (HyperFrames resolves no other family by name)
        shutil.copytree(flow_dir / "html" / "fonts", proj / "assets" / "fonts", dirs_exist_ok=True)
        globals()["FONT_CSS"] = (flow_dir / "html" / "fonts" / "fonts.css").read_text(encoding="utf-8")
    # chapters: split at "title" shots (a title opens a chapter), else every ~60 s, so each scene stays small
    chapters, cur, t_open = [], [], 0.0
    for s, a_, b_ in zip(shots, starts, ends):
        if cur and (s["family"] == "title" or a_ - t_open >= 60): chapters.append(cur); cur = []
        if not cur: t_open = a_
        cur.append((s, a_, b_))
    if cur: chapters.append(cur)
    hosts = []
    for n, ch in enumerate(chapters, 1):
        cid = f"ch{n}"; t0, t1 = ch[0][1], ch[-1][2]
        (proj / "compositions" / f"{cid}.html").write_text(chapter_scene(cid, ch, t0, assets_rel, accent), encoding="utf-8")
        hosts.append(f'<div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:1"></div>')
    # captions
    cap_host = ""
    if "--no-captions" not in sys.argv:
        words = words_from_eleven(timing) if isinstance(timing, dict) and "chars" in timing else words_even(shots, starts, ends)
        words = [w for w in words if w["start"] < dur - 0.3]
        titles = [(a_, b_) for s, a_, b_ in zip(shots, starts, ends) if s["family"] == "title"]   # the title already says it: no caption on top
        words = [w for w in words if not any(a_ - 0.05 <= w["start"] < b_ for a_, b_ in titles)]
        (proj / "compositions" / "captions.html").write_text(captions_scene(groups(words), accent), encoding="utf-8")
        cap_host = f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{dur:.3f}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:5"></div>'
    audio = [f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{dur:.3f}" data-track-index="3" data-volume="1"></audio>']
    (proj / "index.html").write_text(f"""<!doctype html>
<html data-composition-variables='[{{"id":"accent","type":"color","label":"Accent","default":"{accent}"}}]'>
<head><meta charset="utf-8"><title>what-the-data-says-video</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script></head>
<body style="margin:0;background:#000">
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
{cap_host}
{chr(10).join(audio)}
</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
</body></html>
""", encoding="utf-8")
    if not (proj / "hyperframes.json").exists():          # project files the CLI expects (what `hyperframes init` writes)
        (proj / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, indent=2), encoding="utf-8")
        (proj / "meta.json").write_text(json.dumps({"id": proj.name, "name": proj.name}, indent=2), encoding="utf-8")
        (proj / "package.json").write_text(json.dumps({"name": proj.name, "private": True, "type": "module", "scripts": {
            "dev": "npx --yes hyperframes preview", "check": "npx --yes hyperframes check", "render": "npx --yes hyperframes render"}}, indent=2), encoding="utf-8")
    clips = sum(len(re.findall(r'class="clip', (proj / "compositions" / f"ch{n}.html").read_text(encoding="utf-8"))) for n in range(1, len(chapters) + 1))
    print(f"HyperFrames project -> {proj} | {len(shots)} shots, {clips} clips (a cut every {dur / max(clips, 1):.1f} s), {len(chapters)} scenes, {len(done)} images, {len(ANIM)} animated inserts, "
          f"captions {'off' if cap_host == '' else 'on'}, {dur:.1f} s | missing images: {missing or 'none'}")
    print(f"next: npx hyperframes check {proj} --json && npx hyperframes render {proj}")
    if missing: sys.exit(1)

def selftest():
    a = {"dark": False, "html": "", "items": [{"id": "__ID__-a0", "kind": "grow", "ox": 10, "oy": 860}, {"id": "__ID__-a1", "kind": "count", "to": 46, "pre": "", "suf": "%", "dec": 0, "grp": False, "text": "46%"},
         {"id": "__ID__-a2", "kind": "fade"}, {"id": "__ID__-a3", "kind": "draw", "paths": [{"id": "__ID__-a3p0", "len": 900}]}]}
    for du in (0.4, 2.4, 8.0):   # every entrance lands inside its clip; a bar and its figure start together; no placeholder id is left
        tw = insert_tweens("ch1-s7", a, 10.0, du); js = " ".join(tw); assert "__ID__" not in js and "#ch1-s7-a3p0" in js
        for l in tw[:-1]:
            t, d = float(l.rsplit(", ", 1)[1].rstrip(");")), float(re.search(r'"?duration"?: ([\d.]+)', l).group(1)); assert 10.0 <= t and t + d <= 10.0 + du + 1e-6, l
        assert tw[0].rsplit(", ", 1)[1] == tw[2].rsplit(", ", 1)[1], "the bar and its count-up must start together"
    print("hf_build selftest ok")

if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
