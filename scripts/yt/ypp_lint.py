"""Monetisation lint of one video folder before publication (rules and sources: references/monetisation-youtube.md).

  python ypp_lint.py <video_dir> [--scripts "<glob of the channel's earlier script.md>"]     exit 1 on any ERROR
  python ypp_lint.py --title "Do Women Really Prefer Tall Men? What the Data Says"         counts and checks one title by code
  python ypp_lint.py --selftest

Reads <video_dir>/script.md, brief.json and, in <video_dir>/livraison/ or <video_dir>/: titre-description-tags.txt (labels TITLE,
THUMBNAIL TEXT, DESCRIPTION, TAGS), short-titre-description-tags.txt (SHORT TITLE, TAGS). Checks what a YouTube Partner Program
reviewer and the ad classifier see:
  ERROR  a sexual or sexual-violence word in a title, a Short title, a thumbnail text or the tags (limited or no ads)
  ERROR  the long title: over 60 characters, not at the template « Do [Women/Men] Really [X]? What the Data Says », a ranking of groups
  ERROR  packaging left in a title: "(53 characters)", a title that starts with a lower-case letter or is hashtags only, > 100 chars
  ERROR  templated storyline: sentences of 6+ words copied word for word from an earlier script of the channel (more than
         MAX_REUSED of them, or any in the first 10 lines)
  ERROR  fewer than 4 named, dated sources in the description; a voice language other than English in brief.json
  WARN   a placeholder left ([CHANNEL], [lien de la vidéo]), a risky word in the description, a title that is not plain English letters
It only catches known patterns: read the delivery files yourself too.
"""
import glob, json, pathlib, re, sys

RISK = r"\b(sex|sexual|sexy|rape[ds]?|raping|porn\w*|orgasm\w*|nude[s]?|naked|fetish\w*|erotic\w*|nsfw|xxx|horny|adult content|genital\w*|masturbat\w*)\b"
TEMPLATE = r"^Do (Women|Men) Really .+\? What the Data Says$"   # 9.3 % of clicks at 52 characters; two questions of 75-91 characters: 3.3 to 7.2 % (Studio, 11 Nov 2026)
RANKING = r"\b(rank(?:ed|ing|s)?|races?|ethnicit(?:y|ies)|nationalit(?:y|ies)|religions?|which (?:country|group))\b"      # no ranking of groups, ever
LEFTOVER = r"\(\s*\d+\s*(?:characters?|caract[eè]res?|chars?)\s*\)"
PLACEHOLDER = r"\[(?:CHANNEL|Channel name|lien[^\]]*|link[^\]]*)\]"
MAX_REUSED = 5   # sentences shared with earlier scripts; the channel's signature lines must be rephrased each time


def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("’", "'").replace("'", "")).strip()


def sentences(text):
    """Spoken lines of a script.md, in order: no headings, nothing after a non-chapter section such as '## Sources'."""
    text = re.split(r"^## (?!Chapter)", text, flags=re.M | re.I)[0]
    return [l.strip() for l in text.splitlines() if l.strip() and not l.startswith(("#", "<!--"))]


def reused(script, others, min_words=6):
    """[(line number, sentence)] of script lines found word for word in any earlier script."""
    seen = {norm(s) for o in others for s in sentences(o) if len(norm(s).split()) >= min_words}
    return [(n + 1, s) for n, s in enumerate(sentences(script)) if norm(s) in seen]


def labelled(text, label):
    """The first non-empty line after a line starting with one of the labels (TITLE, SHORT TITLE, TAGS...)."""
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if re.match(rf"^\W*(?:{label})\b", l.strip(), flags=re.I):
            for nxt in lines[i + 1:]:
                if nxt.strip(): return nxt.strip()
    return ""


def title_problems(t, long=False):
    """long=True: the title of the long video (60 characters, the channel's template, no ranking of groups); else a Short title."""
    errs, warns = [], []
    if not t: return ["title not found"], []
    if re.search(LEFTOVER, t, flags=re.I): errs.append("character count left in the title")
    if t.lstrip().startswith("#"): errs.append("title is hashtags only")
    elif t[0].islower(): errs.append("title starts with a lower-case letter (first letter lost?)")
    if len(t) > 100: errs.append(f"{len(t)} characters (> 100)")
    elif len(t) > 60: (errs if long else warns).append(f"{len(t)} characters: cut on mobile after 60")
    if long and not re.match(TEMPLATE, t): errs.append("not at the template « Do [Women/Men] Really [X]? What the Data Says »")
    if m := re.search(RISK, t, flags=re.I): errs.append(f'ad-unfriendly word "{m.group(0)}"')
    if m := re.search(RANKING, t, flags=re.I): errs.append(f'"{m.group(0)}": a ranking or comparison of groups is a banned subject')
    if re.search(r"[^\x00-\x7F’…]", t): warns.append("non-English characters")
    return errs, warns


def lint(d, scripts_glob):
    d = pathlib.Path(d); out = []; liv = d / "livraison"
    read = lambda name: next((p.read_text(encoding="utf-8") for p in (liv / name, d / name) if p.exists()), "")
    long_txt, short_txt, pub = read("titre-description-tags.txt"), read("short-titre-description-tags.txt"), read("publication.md")
    for what, txt, lab in (("title", long_txt, "TITLE|TITRE"), ("Short title", short_txt, "SHORT TITLE|TITRE DU SHORT|TITLE|TITRE")):
        t = labelled(txt, lab); errs, warns = title_problems(t, long=what == "title")
        out += [("ERROR", f"{what}: {e}: {t!r}") for e in errs] + [("WARN", f"{what}: {w}: {t!r}") for w in warns]
    thumb = labelled(long_txt, "THUMBNAIL TEXT|TEXTE DE MINIATURE") + " " + " ".join(re.findall(r"«\s*([A-Z0-9 ?!'|,.-]{3,40})\s*»", pub))
    for what, txt in (("tags", labelled(long_txt, "TAGS")), ("Short tags", labelled(short_txt, "TAGS")), ("thumbnail text", thumb)):
        if m := re.search(RISK, txt, flags=re.I): out.append(("ERROR", f'{what}: ad-unfriendly word "{m.group(0)}"'))
    bp = d / "brief.json"     # two videos went out with a French voice on this English channel (audit 8 Nov 2026)
    if bp.exists() and (json.loads(bp.read_text(encoding="utf-8")).get("voice_language") or "en")[:2].lower() != "en":
        out.append(("ERROR", "brief.json: voice_language is not English"))
    if m := sorted({x.lower() for x in re.findall(RISK, long_txt + short_txt, flags=re.I)}):
        out.append(("WARN", f"description: words the ad classifier reads: {', '.join(m)} (keep them educational and out of the first 2 lines)"))
    if m := sorted(set(re.findall(PLACEHOLDER, long_txt + short_txt + read("posts-youtube.md")))):
        out.append(("WARN", f"placeholders to replace before publishing: {', '.join(m)}"))
    src = re.split(r"^\W*sources?\b.*$", long_txt, flags=re.I | re.M)
    if len(src) < 2 or sum(1 for l in src[-1].splitlines()[:12] if re.search(r"\b(1[5-9]|20)\d\d\b", l)) < 4:
        out.append(("ERROR", "description: fewer than 4 named, dated sources (educational value is what separates this from a plain slideshow)"))
    sp = d / "script.md"
    if sp.exists():
        others = [pathlib.Path(p).read_text(encoding="utf-8") for p in glob.glob(scripts_glob) if pathlib.Path(p).resolve() != sp.resolve()]
        hits = reused(sp.read_text(encoding="utf-8"), others)
        early = [h for h in hits if h[0] <= 10]
        if len(hits) > MAX_REUSED or early:
            out.append(("ERROR", f"templated storyline: {len(hits)} sentences copied from earlier scripts ({len(early)} in the first 10 lines): "
                        + " | ".join(f"l.{n} {s[:60]}" for n, s in (early + hits)[:6])))
        elif hits: out.append(("WARN", f"{len(hits)} sentences shared with earlier scripts: " + " | ".join(f"l.{n} {s[:60]}" for n, s in hits)))
        out.append(("INFO", f"script compared with {len(others)} earlier scripts"))
    else: out.append(("WARN", "script.md not found: storyline reuse not checked"))
    return out


def selftest():
    assert title_problems("Why Evolution Kept Your Orgasm (It Wasn't for Babies) (53 caractères)")[0] == ["character count left in the title", 'ad-unfriendly word "Orgasm"']
    assert title_problems("hat Did Cavemen Do at Night?")[0] == ["title starts with a lower-case letter (first letter lost?)"]
    assert title_problems("#animation #humanevolution")[0] == ["title is hashtags only"]
    assert title_problems("How Did Ancient Humans Get Clean Without Soap?") == ([], [])
    assert title_problems("Do Women Really Prefer Black Men? And What Happened When Dating Apps Checked the Data?")[1] == ["86 characters: cut on mobile after 60"]
    assert title_problems("Do Women Really Prefer Tall Men? What the Data Says", long=True) == ([], [])
    assert len(title_problems("Do Women Really Prefer Black Men? And What Happened When Dating Apps Checked the Data?", long=True)[0]) == 2   # length + template
    assert "banned subject" in title_problems("Which Race Do Women Really Prefer? What the Data Says", long=True)[0][-1]
    a = "# T\n## Chapter 1 — x\nYou will be shocked by a terrifying truth.\nCome on.\nA brand new line about soap and ash.\n## Sources\nYou will be shocked by a terrifying truth."
    b = "## Chapter 1 — y\nYou will be shocked by a terrifying truth!\nCome on.\n"
    assert reused(a, [b]) == [(1, "You will be shocked by a terrifying truth.")]   # short lines and the Sources section are ignored
    assert labelled("TITLE\n\nHello there\nTAGS\na, b", "TITLE|TITRE") == "Hello there"
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest(); sys.exit(0)
    if "--title" in sys.argv:
        t = sys.argv[sys.argv.index("--title") + 1]; errs, warns = title_problems(t, long=True)
        print(f"{len(t)} characters | " + ("; ".join(errs + warns) or "ok")); sys.exit(1 if errs else 0)
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    g = sys.argv[sys.argv.index("--scripts") + 1] if "--scripts" in sys.argv else str(pathlib.Path(a[0]).resolve().parent / "*" / "script.md")
    res = lint(a[0], g)
    for lvl, msg in res: print(f"{lvl:5} {msg}")
    n = sum(1 for lvl, _ in res if lvl == "ERROR")
    print(f"{n} errors, {sum(1 for lvl, _ in res if lvl == 'WARN')} warnings")
    sys.exit(1 if n else 0)
