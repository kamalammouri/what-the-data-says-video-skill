"""YouTube keyword and packaging research for a US audience, with free sources only.
  python keywords.py "do women prefer tall men" "do women prefer older men" [--n 25] [--out keywords.md]      one seed per candidate subject
  python keywords.py --selftest
Sources: (1) YouTube autocomplete (gl=US, hl=en): the seed, then seed + " " + each modifier (why, how, science, study, data,
psychology, explained, a..z); (2) YouTube search results via yt-dlp ("ytsearchN:<query>"), with views, duration, channel.
Output (markdown): the demand score of each seed (score b of references/sujets.md), suggestions ranked by how many queries
produced them, the top results by views with their title patterns, and tag candidates. yt-dlp needs a JS runtime: --js-runtimes node.
"""
import json, re, subprocess, sys, urllib.parse, urllib.request, datetime, collections

UA = {"User-Agent": "Mozilla/5.0"}
MODS = ["why", "how", "what", "really", "actually", "science", "study", "data", "statistics", "psychology", "explained", "facts",
        "dating", "attraction", "vs", "reddit", "truth"] + list("abcdefghijklmnopqrstuvwxyz")

def demand(n_suggestions, views):
    """Demand score 0-3 of one candidate subject: how many autocomplete suggestions its seed produced, and the median views of the
    10 most viewed search results. Starting thresholds (11 Nov 2026), to re-fit on references/channel-results.md after five videos."""
    top = sorted(views, reverse=True)[:10]; med = sorted(top)[len(top) // 2] if top else 0
    if not n_suggestions: return 0, med   # nobody types the seed: the search results are off-topic videos, their views say nothing (11 Nov 2026: "funny men", 0 suggestions, median 3.0M)
    return (3 if n_suggestions >= 10 and med >= 100_000 else 2 if n_suggestions >= 5 or med >= 30_000 else 1), med

STOP = {"do", "does", "did", "really", "actually", "the", "a", "an", "what", "why", "how", "is", "are", "to", "of", "in", "more", "than"}
SAME = [{"prefer", "like", "love", "want", "attracted", "choose", "date", "into"}, {"men", "man", "guys", "guy", "males"}, {"women", "woman", "girls", "girl", "females"}]
OURS = "hidden bargain"

def same_question(seed, title):
    """True when a video title asks the seed's question: every content word of the seed (or a synonym) is in the title.
    ponytail: word match with three synonym groups, no meaning; it misses a reworded title ("age gap dating"), so the table also
    prints the titles for a human read. Upgrade path: compare transcripts if a missed duplicate is ever published."""
    words = lambda s: {w[:-1] if len(w) > 4 and w.endswith("s") else w for w in re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()}
    t = words(title)
    return all(any(x in t for x in next((g for g in SAME if w in g), {w})) for w in words(seed) - STOP)

def existing(seed, rows):
    """The search results that already ask the seed's question on other channels, most viewed first, and how many of them are
    our kind of video: 8 min or longer with a data word in the title (study, science, data, research, statistics, psychology...)."""
    hits = sorted((r for r in rows if r["seed"] == seed and OURS not in r["channel"].lower() and same_question(seed, r["title"])), key=lambda r: -r["views"])
    for r in hits: r["kind"] = "long data video" if r["dur"] >= 480 and re.search(r"stud|scien|data|research|statistic|psycholog|evidence|explained", r["title"].lower()) else "long" if r["dur"] >= 480 else "short"
    return hits, sum(1 for r in hits if r["kind"] == "long data video")

def suggest(q):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&gl=US&hl=en&q=" + urllib.parse.quote(q)
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10).read().decode("utf-8", "replace")
        return json.loads(raw)[1]
    except Exception:
        return []

def search(q, n):
    r = subprocess.run(["yt-dlp", "--js-runtimes", "node", "--flat-playlist", "-J", f"ytsearch{n}:{q}"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try: return json.loads(r.stdout).get("entries", [])
    except Exception: return []

def main():
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 25
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    skip = {str(n), out}
    seeds = [a for a in sys.argv[1:] if not a.startswith("--") and a not in skip]
    lines = [f"# Keyword research (US) — {', '.join(seeds)} — {datetime.date.today()}"]
    counter, examples, per_seed = collections.Counter(), {}, collections.defaultdict(set)
    for s in seeds:
        for q in [s] + [f"{s} {m}" for m in MODS]:
            for sug in suggest(q):
                if re.search(r"(hindi|urdu|tamil|telugu|bangla|bengali|malayalam|kannada|marathi|punjabi|arabic|reaction|reacts?|shorts?|zenn|mr\.? hell)", sug.lower()): continue   # other languages, reaction videos, channel names
                counter[sug.lower()] += 1; examples.setdefault(sug.lower(), q); per_seed[s].add(sug.lower())
    lines.append("\n## 1. What Americans type (YouTube autocomplete, gl=US)\n\n| Suggestion | Queries that produce it |\n|---|---|")
    for sug, c in counter.most_common(60): lines.append(f"| {sug} | {c} |")
    lines.append("\n## 2. What the search page rewards (sorted by views)\n")
    rows = []
    for s in seeds:
        for e in search(s, n):
            v = e.get("view_count") or 0; d = e.get("duration") or 0; t = e.get("title") or ""
            rows.append({"seed": s, "title": t, "views": v, "dur": int(d), "channel": e.get("channel") or e.get("uploader") or "", "id": e.get("id")})
    table = ["\n## 0. Demand per candidate subject (score b)\n\n| Seed | Suggestions | Median views, 10 most viewed results | Score b |\n|---|---|---|---|"]
    for s in seeds:
        score, med = demand(len(per_seed[s]), [r["views"] for r in rows if r["seed"] == s])
        table.append(f"| {s} | {len(per_seed[s])} | {med:,} | {score} |")
    table.append(f"\n## 0 bis. Already on YouTube (the {n} first results of each seed, other channels)\n\n| Seed | Videos asking the same question | of which long data videos (8 min or more, a data word in the title) | Verdict |\n|---|---|---|---|")
    detail = []
    for s in seeds:
        hits, long = existing(s, rows)
        verdict = "free: nobody asks it" if not hits else "a long data video exists: show it to the user, say what ours adds, or drop" if long else "asked, but no long data video found: go, with our own title and our own sources"
        table.append(f"| {s} | {len(hits)} | {long} | {verdict} |")
        detail += [f"| {s} | {r['views']:,} | {r['dur']//60}:{r['dur']%60:02d} | {r['kind']} | {r['channel'][:28]} | {r['title']} | https://youtu.be/{r['id']} |" for r in sorted(hits, key=lambda r: r["kind"] != "long data video")[:5]]
    if detail: table += ["\n| Seed | Views | Length | Kind | Channel | Title | Link |\n|---|---|---|---|---|---|---|"] + detail
    lines[1:1] = table
    seen = set(); rows = [r for r in rows if not (r["id"] in seen or seen.add(r["id"]))]
    rows.sort(key=lambda r: -r["views"])
    lines.append("| Views | Length | Channel | Title |\n|---|---|---|---|")
    for r in rows[:40]: lines.append(f"| {r['views']:,} | {r['dur']//60}:{r['dur']%60:02d} | {r['channel'][:28]} | {r['title']} |")
    tt = [r["title"] for r in rows[:40]]
    openers = collections.Counter(" ".join(t.split()[:2]).lower() for t in tt)
    qs = sum(1 for t in tt if "?" in t); nums = sum(1 for t in tt if re.search(r"\d", t)); avg = sum(len(t) for t in tt) / max(1, len(tt))
    lines.append(f"\n## 3. Title patterns in the top 40\n\n- questions: {qs}/{len(tt)} · with a number: {nums}/{len(tt)} · average length: {avg:.0f} characters")
    lines.append("- most common openers: " + ", ".join(f"« {o} » ×{c}" for o, c in openers.most_common(8)))
    tags = [s for s, _ in counter.most_common(40)][:20]
    lines.append("\n## 4. Tag candidates (≤ 500 characters in Studio)\n\n" + ", ".join(tags))
    lines.append(f"\n(total: {len(', '.join(tags))} characters)")
    text = "\n".join(lines)
    if out: open(out, "w", encoding="utf-8").write(text); print(f"-> {out}")
    else: print(text)

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        assert demand(12, [900_000, 150_000, 120_000, 5_000]) == (3, 150_000) and demand(6, [1_000]) == (2, 1_000)
        assert demand(1, [40_000] * 10)[0] == 2 and demand(2, [500])[0] == 1 and demand(0, []) == (0, 0) and demand(0, [3_000_000] * 10)[0] == 0
        q = "do women prefer older men"
        assert same_question(q, "Why Do Girls Like Older Guys? (science)") and same_question(q, "Do Women REALLY Prefer Older Men?") and not same_question(q, "Do Women Prefer Tall Men?") and not same_question(q, "Older men explain dating")
        rows = [{"seed": q, "title": "Why women love older men", "views": 9, "dur": 700, "channel": "X", "id": "a"}, {"seed": q, "title": "Do Women Really Prefer Older Men? What the Data Says", "views": 5, "dur": 733, "channel": "The Hidden Bargain", "id": "b"}, {"seed": q, "title": "girls like older guys #shorts", "views": 99, "dur": 40, "channel": "Y", "id": "c"}]
        hits, long = existing(q, rows); assert [r["id"] for r in hits] == ["c", "a"] and long == 0 and hits[1]["kind"] == "long"
        rows[0]["title"] = "Why women love older men: the science"; assert existing(q, rows)[1] == 1
        print("selftest ok"); sys.exit(0)
    main()
