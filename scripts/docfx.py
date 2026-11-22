"""Documentary shots drawn by code for hf_build.py (merged from the documentary-explainer-video skill, 22 Nov 2026):
  family "docdate"  DATE("1292", "PARIS TAX ROLL")            big date card, letters slam in, accent bar draws, held
  family "clipping" CLIP(quote, mark, source, file=None)       source clipping: paper card slightly rotated, the key phrase
                                                               gets a marker highlight that draws on, "Source:" label; with
                                                               `file` (an assets/photos picture) the real page sits behind it
  family "docmap"   MAP(places, route=None, fill=None, view=None, focus=None)
                                                               dark map from Natural Earth (assets/maps/countries-50m.json):
                                                               slow push-in toward `focus`, `fill` countries in the accent
                                                               colour, cities pop with labels, a dashed route draws on with a
                                                               dot travelling along it
Every function returns (html, tweens) for one clip; `pid` is the clip id, `st`/`du` its start and duration in the scene.
Style rules (references/documentaire.md): dark desaturated base, one accent colour, all-caps sans labels with soft shadow,
never static (slow drift), facts on screen = facts.md only.
"""
import json, math, pathlib, html as _h

HERE = pathlib.Path(__file__).parent
W, H = 1920, 1080
MAP_FILE = HERE.parent / "assets" / "maps" / "countries-50m.json"
_COUNTRIES = None
CITIES = {   # lat, lon of places the channel's history subjects use; any other place: pass [name, lat, lon]
    "Paris": (48.857, 2.352), "Vienna": (48.208, 16.373), "Brussels": (50.850, 4.352), "Antwerp": (51.219, 4.402),
    "London": (51.507, -0.128), "Southwark": (51.503, -0.090), "Rome": (41.903, 12.496), "Florence": (43.770, 11.256),
    "Ghent": (51.054, 3.725), "Nuremberg": (49.452, 11.077), "Basel": (47.560, 7.588), "Rotterdam": (51.924, 4.478),
}

def esc(t): return _h.escape(str(t), quote=True)

CSS = """
.doc { position: absolute; inset: 0; overflow: hidden; }
.doc .lab { position: absolute; font-family: Montserrat, Inter, sans-serif; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #fff; text-shadow: 0 3px 14px rgba(0,0,0,.75); white-space: nowrap; }
.ddate { background: radial-gradient(ellipse at 50% 45%, #1c2533 0%, #0b0f1a 75%); }
.ddate .big { position: absolute; left: 0; width: 1920px; top: 330px; text-align: center; font-family: Oswald, Inter, sans-serif; font-weight: 700; font-size: 300px; line-height: 1; color: #fff; letter-spacing: .04em; text-shadow: 0 10px 40px rgba(0,0,0,.6); }
.ddate .big span { display: inline-block; }
.ddate .bar { position: absolute; left: 760px; top: 650px; width: 400px; height: 10px; transform-origin: 0 50%; }
.ddate .sub { position: absolute; left: 0; width: 1920px; top: 690px; text-align: center; font-family: Montserrat, Inter, sans-serif; font-weight: 700; font-size: 46px; letter-spacing: .18em; color: #d8dde6; text-transform: uppercase; }
.dclip { background: #1a1d24; }
.dclip .page { position: absolute; left: -40px; top: -40px; width: 2000px; height: 1160px; object-fit: cover; filter: blur(6px) brightness(.45) saturate(.6); }
.dclip .card { position: absolute; left: 310px; top: 230px; width: 1300px; padding: 64px 80px 70px; background: #f6f1e4; border-radius: 6px; box-shadow: 0 30px 80px rgba(0,0,0,.55); transform: rotate(-1.6deg); }
.dclip .q { font-family: Georgia, 'Times New Roman', serif; font-size: 54px; line-height: 1.38; color: #26221b; margin: 0; }
.dclip .hl { background-color: rgba(255,216,77,0); border-radius: 4px; padding: 0 3px; box-decoration-break: clone; -webkit-box-decoration-break: clone; }
.dclip .src { position: absolute; right: 40px; bottom: 18px; font-family: Inter, sans-serif; font-size: 24px; color: #7b7466; letter-spacing: .02em; }
.dmap { background: #0d1622; }
.dmap svg { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }
"""

def date_html(pid, spec, accent, st, du):
    big, sub = str(spec.get("big", "")), str(spec.get("sub", ""))
    letters = "".join(f'<span>{esc(c) if c != " " else "&nbsp;"}</span>' for c in big)
    html = (f'<div class="doc ddate"><div class="big">{letters}</div><div class="bar" style="background:{accent}"></div>'
            f'<div class="sub">{esc(sub)}</div></div>')
    tw = [f'tl.fromTo("#{pid} .big span", {{opacity: 0, y: -60, scale: 1.4}}, {{opacity: 1, y: 0, scale: 1, duration: 0.22, ease: "back.out(2)", stagger: 0.06}}, {st + 0.05:.3f});',
          f'tl.fromTo("#{pid} .bar", {{scaleX: 0}}, {{scaleX: 1, duration: 0.45, ease: "power3.out"}}, {st + 0.25 + 0.06 * len(big):.3f});',
          f'tl.fromTo("#{pid} .sub", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power2.out"}}, {st + 0.4 + 0.06 * len(big):.3f});',
          f'tl.fromTo("#{pid} .ddate", {{scale: 1}}, {{scale: 1.04, duration: {du:.3f}, ease: "none"}}, {st:.3f});']
    return html, tw

def clip_html(pid, spec, page_src, st, du):
    """The quote is written as given; the first occurrence of `mark` inside it is highlighted. Words are never invented here:
    the quote and the source come from facts.md (rule of references/documentaire.md)."""
    q, mark, src = spec.get("quote", ""), spec.get("mark", ""), spec.get("source", "")
    if mark and mark in q:
        a, b = q.split(mark, 1)   # one highlighted span per word: survives a line break, animates with opacity only
        body = esc(a) + " ".join(f'<span class="hl">{esc(w)}</span>' for w in mark.split()) + esc(b)
    else: body = esc(q)
    bg = f'<img class="page" src="{page_src}" alt="">' if page_src else ""
    html = f'<div class="doc dclip">{bg}<div class="card"><p class="q">“{body}”</p><div class="src">Source: {esc(src)}</div></div></div>'
    tw = [f'tl.fromTo("#{pid} .card", {{opacity: 0, y: 70, rotation: -4}}, {{opacity: 1, y: 0, rotation: -1.6, duration: 0.5, ease: "power3.out"}}, {st + 0.05:.3f});',
          f'tl.fromTo("#{pid} .hl", {{backgroundColor: "rgba(255,216,77,0)"}}, {{backgroundColor: "rgba(255,216,77,0.9)", duration: 0.25, ease: "power1.out", stagger: 0.12}}, {st + min(1.0, du * 0.35):.3f});',
          f'tl.fromTo("#{pid} .card", {{scale: 1}}, {{scale: 1.05, duration: {du:.3f}, ease: "none"}}, {st:.3f});']
    if page_src: tw.append(f'tl.fromTo("#{pid} .page", {{scale: 1.0, x: 0}}, {{scale: 1.08, x: -30, duration: {du:.3f}, ease: "none"}}, {st:.3f});')
    return html, tw

def _countries():
    global _COUNTRIES
    if _COUNTRIES is None: _COUNTRIES = json.load(open(MAP_FILE, encoding="utf-8"))["countries"]
    return _COUNTRIES

def _place(p):
    if isinstance(p, (list, tuple)): return p[0], float(p[1]), float(p[2])
    if p not in CITIES: raise SystemExit(f'MAP(): unknown place "{p}": pass ["{p}", lat, lon] or add it to docfx.CITIES')
    return (p, *CITIES[p])

def map_html(pid, spec, accent, st, du):
    places = [_place(p) for p in spec.get("places", [])]
    route = [_place(p) for p in spec.get("route", [])]
    fill = {f.upper() for f in spec.get("fill", [])}
    pts = places + route
    if spec.get("view"): lon0, lat0, lon1, lat1 = spec["view"]
    else:
        lats, lons = [p[1] for p in pts], [p[2] for p in pts]
        one = len({(p[1], p[2]) for p in pts}) == 1   # a single city: show the country around it, not a field of one colour (22 Nov 2026)
        pad_lat, pad_lon = max(7.0 if one else 3.0, (max(lats) - min(lats)) * 0.6), max(12.0 if one else 5.0, (max(lons) - min(lons)) * 0.6)
        lon0, lon1, lat0, lat1 = min(lons) - pad_lon, max(lons) + pad_lon, min(lats) - pad_lat, max(lats) + pad_lat
    k = math.cos(math.radians((lat0 + lat1) / 2))
    sx = W / ((lon1 - lon0) * k); sy = H / (lat1 - lat0); s = max(sx, sy)            # cover the frame
    cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    X = lambda lon: W / 2 + (lon - cx) * k * s
    Y = lambda lat: H / 2 - (lat - cy) * s
    paths = []
    for c in _countries():
        hit = c["iso"] in fill or (c["name"] or "").upper() in fill
        for r in c["rings"]:
            if max(x for x, _ in r) < lon0 - 10 or min(x for x, _ in r) > lon1 + 10 or max(y for _, y in r) < lat0 - 8 or min(y for _, y in r) > lat1 + 8: continue
            d = "M" + "L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in r) + "Z"
            paths.append(f'<path class="{"hit" if hit else "land"}" d="{d}"/>')
    dots, labels = [], []
    for n, (name, la, lo) in enumerate(places):
        x, y = X(lo), Y(la)
        dots.append(f'<g class="pin p{n}" transform="translate({x:.1f},{y:.1f})"><circle r="26" fill="{accent}" opacity=".25"/><circle r="11" fill="{accent}" stroke="#fff" stroke-width="3"/></g>')
        right = x > W * 0.72   # near the right edge (or pushed there by the zoom): label on the left of the dot
        labels.append(f'<text class="lbl l{n}" x="{x - 22 if right else x + 22:.1f}" y="{y - 20:.1f}" text-anchor="{"end" if right else "start"}">{esc(name.upper())}</text>')
    route_svg = ""
    if len(route) >= 2:
        rp = [(X(lo), Y(la)) for _, la, lo in route]
        d = "M" + " ".join(f"{a:.1f},{b:.1f}" if i == 0 else f"Q{(rp[i-1][0] + a) / 2:.1f},{min(rp[i-1][1], b) - 90:.1f} {a:.1f},{b:.1f}" for i, (a, b) in enumerate(rp))
        route_svg = (f'<path id="{pid}-route" class="route" d="{d}" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".95"/>'
                     f'<circle id="{pid}-dot" r="13" fill="{accent}" stroke="#fff" stroke-width="5"/>')
    fx, fy = (X(_place(spec["focus"])[2]), Y(_place(spec["focus"])[1])) if spec.get("focus") else (W / 2, H / 2)
    style = (f'<style>#{pid} .land{{fill:#243244;stroke:#3d5068;stroke-width:1.2}} #{pid} .hit{{fill:{accent};fill-opacity:.8;stroke:#fff;stroke-width:2}}'
             f' #{pid} .lbl{{font-family:Montserrat,Inter,sans-serif;font-weight:800;font-size:38px;letter-spacing:.08em;fill:#fff;paint-order:stroke;stroke:rgba(0,0,0,.65);stroke-width:8px}}</style>')
    title = f'<div class="lab" style="left:80px;top:70px;font-size:44px">{esc(spec["title"])}</div>' if spec.get("title") else ""
    html = (f'<div class="doc dmap">{style}<svg viewBox="0 0 {W} {H}"><g class="cam">{"".join(paths)}{route_svg}{"".join(dots)}{"".join(labels)}</g></svg>{title}</div>')
    zoom = float(spec.get("zoom", 1.35))   # svgOrigin = the focus in SVG units: it stays put while the map grows around it
    tw = [f'tl.fromTo("#{pid} .cam", {{scale: 1, svgOrigin: "{fx:.1f} {fy:.1f}"}}, {{scale: {zoom}, svgOrigin: "{fx:.1f} {fy:.1f}", duration: {du:.3f}, ease: "sine.inOut"}}, {st:.3f});',
          f'tl.fromTo("#{pid} .hit", {{fillOpacity: 0}}, {{fillOpacity: 0.8, duration: 0.6, ease: "power2.out"}}, {st + 0.2:.3f});']
    for n in range(len(places)):
        t = st + 0.35 + n * min(0.45, du * 0.5 / max(1, len(places)))
        tw.append(f'tl.fromTo("#{pid} .p{n}", {{scale: 0, transformOrigin: "50% 50%"}}, {{scale: 1, duration: 0.35, ease: "back.out(2.5)"}}, {t:.3f});')
        tw.append(f'tl.fromTo("#{pid} .l{n}", {{opacity: 0, x: -12}}, {{opacity: 1, x: 0, duration: 0.3, ease: "power2.out"}}, {t + 0.15:.3f});')
    if route_svg:
        rd = max(0.8, min(du * 0.6, 3.0)); t0 = st + 0.4
        tw.append(f'(function(){{ const r = document.getElementById("{pid}-route"), RL = r.getTotalLength(); r.style.strokeDasharray = RL; '
                  f'tl.fromTo(r, {{strokeDashoffset: RL}}, {{strokeDashoffset: 0, duration: {rd:.3f}, ease: "power1.inOut"}}, {t0:.3f}); '
                  f'const dot = document.getElementById("{pid}-dot"), o = {{v: 0}}; '
                  f'const put = () => {{ const p = r.getPointAtLength(o.v * RL); dot.setAttribute("cx", p.x); dot.setAttribute("cy", p.y); }}; put(); '
                  f'tl.to(o, {{v: 1, duration: {rd:.3f}, ease: "power1.inOut", onUpdate: put}}, {t0:.3f}); }})();')
    return html, tw

def selftest():
    h, t = date_html("x", {"big": "1292", "sub": "Paris tax roll"}, "#F2C446", 0, 3)
    assert "1292"[0] in h and len(t) == 4
    h, t = clip_html("x", {"quote": "nothing was more in Vogue in Brabant, than hot Baths", "mark": "hot Baths", "source": "Erasmus, 1523"}, None, 0, 4)
    assert h.count('class="hl"') == 2 and "Source: Erasmus" in h
    h, t = map_html("x", {"places": ["Paris", "Vienna"], "route": ["Paris", "Vienna"], "fill": ["FRA", "AUT"], "focus": "Paris"}, "#F2C446", 0, 4)
    assert h.count("class=\"hit\"") >= 2 and "x-route" in h and any("getTotalLength" in s for s in t)
    print("docfx selftest ok")

if __name__ == "__main__":
    selftest()
