"""Gate of a « Do [Women/Men] Really [X]? What the Data Says » script: the retention structure, the safe wording, the sources.

  python script_lint.py script.md [--minutes 12]      prints the measures and the chapter clock; exit 1 on any ERROR
  python script_lint.py --selftest

script.md:   # <title>                         (the question of the title is read from here)
             ## Chapter 1 — <name>             one spoken sentence per line; 9 chapters: 1 opening, 6 blocks, 1 answer, 1 return
             ## Sources                        "- Name, year, what, link": 4 to 7 lines, not spoken
Times are words at 170 a minute (the voice runs at 165-175, pauses included: tts.py prints the real figure).

Why each rule exists (Studio, The Hidden Bargain, 8 and 11 Nov 2026; references/channel-results.md):
  the data promised by the title came at 8:45 in the 12-minute « Black Men » video: viewers left at 1:58 and 4:00, 33 % watched;
  the first question was asked at 65 s in bath-en, the channels that work ask it before 15 s;
  lines copied from a reference channel in every script are what YouTube calls templated content.
Anti-boredom rules (22 Nov 2026, the bath video: chapter 2 spent 4 lines dating a manuscript, chapter 7 4 lines on how a poll was run
before its number and 4 on its limits after, every line 11 words, no pause; references/structure-ecriture.md §5):
  method and caveat lines (how a source was made, what it can't tell) at most a quarter of a chapter: the method goes on screen (src);
  2 punch lines of 5 words or less and a spread of line lengths in every block; one beat (" //") or more in every block;
  a teaser (a promise kept later) in every block, as a warning.
"""
import re, sys

WPM = 170
TITLE = r"^Do (Women|Men) Really .+\? What the Data Says$"
RISK = r"\b(sex|sexual|sexy|rape[ds]?|raping|porn\w*|orgasm\w*|nude[s]?|naked|fetish\w*|erotic\w*|nsfw|xxx|horny|adult content|genital\w*|masturbat\w*)\b"   # same list as ypp_lint.py
NUMW = r"(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|percent|half|twice|double)"
GENERAL = r"\b(?:all |most )?(?:women|men|girls|guys|wives|husbands) (?:really |actually |just |simply |always |never |only |secretly )?(?:prefer|want|love|hate|like|choose|pick|reject|desire|need|go for|are attracted|care about|don't care|do not care)\b"
HEDGE = (r"\?$|on average|in (?:this|that|the|their|one|another|every) (?:data|study|sample|survey|experiment|report|analysis|paper|poll)|data set|\bsome\b|\bmany\b|\bsaid\b|"
         r"\bsay they\b|\brated\b|\breported\b|\banswered\b|percent|\bin (?:ten|five|four|three|two)\b|the (?:claim|idea|belief|stereotype|myth|rumor|story)|"
         r"people (?:say|think|believe|assume)|you(?:'ve| have) heard|supposed|tend(?:s|ed)? to|more likely|less likely|(?:the|those|these) (?:women|men) (?:in|who|they)")
HISTORY = r"\b(ancient|prehistoric|stone age|ice age|cavem[ae]n|hunter-gatherers?|tribes?|ancestors?|romans?|rome|egypt\w*|greeks?|medieval|middle ages|victorian|pharaohs?|thousand years ago|centur(?:y|ies) ago)\b"
METHOD = r"\b(published|edition|editors?|printed|reprinted|transcrib\w*|translat\w*|manuscript|copied|hand(?:writing)?\b|poll ran|panel|respondents|self-reported|sample|surveyed|questionnaire|answered|methodology|footnote|archive[sd]?)\b"
CAVEAT = r"(\bcatch\b|\blimits?\b|can't tell|cannot tell|doesn't prove|does not prove|won't promise|safe way|be careful|careful with|\bhides?\b|doesn't mean|does not mean|can't divide|we don't know|nobody knows)"
TEASER = r"(hold (?:on to )?that|keep that|remember (?:that|this)|in a (?:minute|moment)|later|by the end|wait until|you're about to|coming up|the strangest|the real reason|here's where|that's not the end|stay with)"
FORMULAS = ["you will be shocked by a terrifying truth", "to understand the scale of this nightmare", "this takes us to the most shocking part",
            "the biggest lie planted in your mind", "lets travel to", "this brings us back to the very first image", "the truth is exactly the opposite",
            "until the turning point arrived", "changed the face of humanity", "you are the winning version"]   # lines of the reference channel reused in every old script

def norm(s): return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", s.lower().replace("’", "'").replace("'", "").replace("&", " and "))).strip()
def source_name(s): return norm(re.sub(r"\bet al\b\.?", "", s.split(",")[0]))   # "Bruch & Newman" is said "Bruch and Newman", "Walter et al." is said "Walter and colleagues" (11 Nov 2026)
def nwords(s): return len(s.split())
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def spell(n):
    """0-99 in words, as the voice says them ("30" in a title is said "thirty"; 23 Nov 2026)."""
    n = int(n)
    if n < 20: return ONES[n]
    return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
def as_said(s): return norm(re.sub(r"\b\d{1,2}\b", lambda m: spell(m.group(0)), s.replace("-", " ")))
def has_number(s):
    return bool(re.search(r"\d", s)) or any(m.lower() not in ("one", "zero") for m in re.findall(rf"\b{NUMW}(?:[\s-]+(?:and\s+|point\s+)?{NUMW})*\b", s, flags=re.I))
def unsafe(line): return bool(re.search(GENERAL, line, flags=re.I)) and not re.search(HEDGE, line.strip(), flags=re.I)
def mmss(words): t = words / WPM * 60; return f"{int(t) // 60}:{int(t) % 60:02d}"

def beat(l): return l.rstrip().endswith("//")
def unbeat(l): return l.rstrip().removesuffix("//").rstrip()

def boredom(head, ls):
    """Errors and warnings of one block on the anti-boredom rules (ls: raw lines, beats still marked)."""
    e, w = [], []; clean = [unbeat(l) for l in ls]; n = len(clean) or 1
    drag = [k for k, l in enumerate(clean, 1) if re.search(METHOD, l, flags=re.I) or re.search(CAVEAT, l, flags=re.I)]
    if len(drag) > max(2, n // 4): e.append(f"{head}: {len(drag)} of {n} lines explain a method or a limit (lines {drag[:8]} of the block): a quarter at most; put the method on screen (make_shots src(...)) and keep one limit, said once")
    lens = [nwords(l) for l in clean]; mean = sum(lens) / n; sd = (sum((x - mean) ** 2 for x in lens) / n) ** 0.5
    if sum(1 for x in lens if x <= 5) < 2: e.append(f"{head}: {sum(1 for x in lens if x <= 5)} punch line of 5 words or less, 2 or more (a figure alone, « Most days. Not every day. »)")
    if sd < 3.5: e.append(f"{head}: every line about {mean:.0f} words (spread {sd:.1f}, 3.5 or more): mix punch lines and long ones, the ear tunes out a steady length")
    if not any(beat(l) for l in ls): e.append(f"{head}: no beat, end the line of the reveal with « // » (a silence the music fills, the picture holds)")
    if not any(re.search(TEASER, l, flags=re.I) for l in clean): w.append(f"{head}: no teaser (« hold on to that number », « you're about to… ») promising a payoff later in the video")
    return e, w

def parse(text):
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "")
    chapters, sources = [], []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        head, *lines = block.strip().splitlines()
        lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith("<!--")]
        if re.match(r"Chapter \d+", head): chapters.append((head, lines))
        elif head.lower().startswith("sources"): sources = [l.lstrip("-• ").strip() for l in lines]
    return title, chapters, sources

def title_errors(t):
    e = []
    if not re.match(TITLE, t): e.append(f"title not at the template « Do [Women/Men] Really [X]? What the Data Says »: {t!r}")
    if len(t) > 60: e.append(f"title of {len(t)} characters, 60 at most (cut on mobile; 52 characters made 9.3 % of clicks, 75 to 91 made 3.3 to 7.2 %)")
    if m := re.search(RISK, t, flags=re.I): e.append(f"ad-unfriendly word \"{m.group(0)}\" in the title")
    return e

def relance_gap(lines, limit):
    """(words, first line, last line) of the longest stretch without a question or a line opening with But; None under the limit."""
    worst, start, at, pos = (0, 1, 1), 0, 1, 0
    for n, l in enumerate(lines, 1):
        if l.endswith("?") or re.match(r"But\b", l):
            if pos - start > worst[0]: worst = (pos - start, at, n - 1)
            start, at = pos + nwords(l), n + 1
        pos += nwords(l)
    if pos - start > worst[0]: worst = (pos - start, at, len(lines))
    return worst if worst[0] > limit else None

def lint(text, minutes=12.0):
    errs, warns = [], []
    title, raw, sources = parse(text)
    chapters = [(h, [unbeat(l) for l in ls]) for h, ls in raw]
    lines = [l for _, ls in chapters for l in ls]; total = sum(map(nwords, lines)); spoken = norm(" ".join(lines))
    errs += title_errors(title)
    if not lines: return errs + ["no spoken line under a '## Chapter N — name' heading"], [], {}
    # size and rhythm
    if not minutes * 160 <= total <= minutes * 180: errs.append(f"{total} words for {minutes:g} min: {minutes * 160:.0f} to {minutes * 180:.0f} expected (165-175 words a minute)")
    wps = total / len(lines)
    if not 9 <= wps <= 13: errs.append(f"{wps:.1f} words per sentence, 9 to 13 expected (punch lines bring it under 11, 22 Nov 2026)")
    for n, l in enumerate(lines, 1):
        if nwords(l) > 25: errs.append(f"line {n}: {nwords(l)} words, 25 at most (one line = one voice clip = one picture)")
        if unsafe(l): errs.append(f"line {n}: a claim about a whole group with no hedge (« on average », « in this data set », « the women in the study »): {l!r}")
        if hit := [f for f in FORMULAS if f in norm(l)]: errs.append(f"line {n}: line of the reference channel copied ({hit[0]!r}): write your own")
        if re.search(r"\d", l): warns.append(f"line {n}: digits in a spoken line, write the number in letters for the voice")
        if re.search(r"\bsubscribe\b|in this video|hit the bell", l, flags=re.I): warns.append(f"line {n}: channel talk in the voice (the end screen and the pinned comment do that job)")
    # the opening: the question before 0:15, the first figure before 1:00, then « but »
    if len(chapters) != 9: errs.append(f"{len(chapters)} chapters, 9 expected: 1 opening, 6 blocks, 1 honest answer, 1 return to the opening scene")
    q = as_said(title.split("?")[0]); ch1 = chapters[0][1]; pos = 0; q_at = None; num_at = None
    for l in ch1:
        pos += nwords(l)
        if q_at is None and q and q in as_said(l): q_at = pos
        elif q_at is not None and num_at is None and has_number(l): num_at = pos
    if q_at is None: errs.append("the question of the title is not said word for word in chapter 1")
    elif q_at > WPM / 4 + 1: errs.append(f"the question of the title ends at {mmss(q_at)} ({q_at} words): it must be said before 0:15 ({WPM // 4} words)")
    if num_at is None: errs.append("no figure after the question in chapter 1 (the first number that answers in part)")
    if pos > 160: errs.append(f"chapter 1 is {pos} words ({mmss(pos)}): 160 at most, it is also the Short (under 60 s) and the first figure must be on screen before 1:00")
    if not any(re.match(r"But\b", l) for l in ch1[-2:]): errs.append("chapter 1 must end on the turn: one of its last two lines opens with « But » (the number hides something)")
    # the six blocks, the answer, the return
    clock, start = [], 0
    for k, (head, ls) in enumerate(chapters, 1):
        w = sum(map(nwords, ls)); clock.append((head, start, w)); start += w
        if len(chapters) == 9 and 2 <= k <= 7:
            if not 225 <= w <= 315: errs.append(f"{head}: {w} words ({w / WPM * 60:.0f} s), a block is 80 to 110 s (225 to 315 words)")
            if not any(has_number(l) for l in ls): errs.append(f"{head}: no figure in this block (one study or data set per block, its number on screen)")
            if not (ls[-1].endswith("?") or re.match(r"(But|So|And)\b", ls[-1])): warns.append(f"{head}: the last line does not open a loop to the next block (a question, or But / So / And)")
            be, bw = boredom(head, raw[k - 1][1]); errs += be; warns += bw
    if len(chapters) == 9 and not 9.0 * WPM <= clock[7][1] <= 10.0 * WPM: warns.append(f"the honest answer starts at {mmss(clock[7][1])}, 9:30 expected")
    if not lines[-1].endswith("?"): errs.append("the last line is the question to the viewer: it ends with « ? »")
    if g := relance_gap(lines, 1.5 * WPM): errs.append(f"{g[0] / WPM * 60:.0f} s without a question or a line opening with « But » (lines {g[1]} to {g[2]}): one every 60 to 90 s")
    # ancient history: a short proof, never a chain of civilisations
    hist = [(head, sum(nwords(l) for l in ls if re.search(HISTORY, l, flags=re.I))) for head, ls in chapters]
    for head, w in hist:
        if w > WPM / 2: errs.append(f"{head}: {w} words of ancient history ({w / WPM * 60:.0f} s), 30 s at most")
    if sum(1 for _, w in hist if w) > 2: errs.append(f"ancient history in {sum(1 for _, w in hist if w)} chapters, 2 at most")
    # sources
    dated = [s for s in sources if re.search(r"\b(1[5-9]|20)\d\d\b", s)]
    if not 4 <= len(dated) <= 7: errs.append(f"{len(dated)} named and dated sources under « ## Sources », 4 to 7 expected")
    for s in dated:
        if source_name(s) not in spoken: errs.append(f"source not named in the voice: {s.split(',')[0]!r}")
    you = sum(1 for w in re.findall(r"[a-z']+", " ".join(lines).lower()) if w in ("you", "your", "yours", "yourself", "you're", "you've", "you'll", "you'd"))
    if 100 * you / total < 2: warns.append(f"{100 * you / total:.1f} « you » per 100 words: talk to the viewer (2 or more)")
    m = {"beats": sum(1 for _, ls in raw for l in ls if beat(l)), "words": total, "sentences": len(lines), "words_per_sentence": round(wps, 1), "minutes_at_170": round(total / WPM, 1), "you_per_100w": round(100 * you / total, 1),
         "figures_per_min": round(sum(1 for l in lines if has_number(l)) / (total / WPM), 1), "questions": sum(1 for l in lines if l.endswith("?")), "clock": clock}
    return errs, warns, m

def selftest():
    assert title_errors("Do Women Really Prefer Tall Men? What the Data Says") == []
    assert len(title_errors("Do Women Really Prefer Black Men? And What Happened When Dating Apps Checked the Data?")) == 2
    assert "ad-unfriendly" in title_errors("Do Men Really Want More Sex? What the Data Says")[0]
    assert unsafe("Women prefer tall men.") and unsafe("And men always want younger women, everywhere.")
    assert not unsafe("So, do women really prefer tall men?") and not unsafe("On average, women in this data set preferred taller men.")
    assert not unsafe("You have heard the claim that women prefer tall men.") and not unsafe("Seven in ten women said they prefer a taller partner.")
    assert has_number("seven in ten women") and has_number("17 percent") and not has_number("no one knows") and has_number("twice as often")
    assert relance_gap(["a b c d", "But e f", "g h i j k l", "why?"], 5) == (6, 3, 3) and relance_gap(["a b", "But c", "d?"], 5) is None
    ex = ("# Do Women Really Prefer Tall Men? What the Data Says\n## Chapter 1 — The Question\nYou are at a bar tonight.\nSo, do women really prefer tall men?\n"
          "In one survey, seven in ten women said yes.\nBut that number hides something.\n## Chapter 2 — End\nWomen love tall men in ancient Rome.\nYou will be shocked by a terrifying truth.\n"
          "## Sources\n- Pew Research Center, 2017, Intermarriage in the U.S.\n")
    e = " | ".join(lint(ex, 0.3)[0])
    for must in ("2 chapters, 9 expected", "no hedge", "reference channel copied", "1 named and dated sources", "source not named in the voice: 'Pew Research Center'", "last line is the question"): assert must in e, (must, e)
    for must_not in ("question of the title", "no figure after the question", "must end on the turn", "template"): assert must_not not in e, (must_not, e)
    assert as_said("Did People Really Die at 30") == as_said("so, did people really die at thirty?").removeprefix("so ") and spell(47) == "forty seven"
    assert "question of the title is not said" in " | ".join(lint(ex.replace("So, do women really prefer tall men?", "So, do they?"), 0.3)[0])
    assert source_name("Bruch & Newman, 2018, x") == "bruch and newman" and source_name("Walter et al., 2020, x") == "walter" and norm("Lee  &  McKinnish") == "lee and mckinnish"
    old7 = ["In twenty eighteen, the polling firm Ipsos asked Americans about hygiene and cleanliness.", "The online poll ran from August third to sixth that year.",
            "About one thousand and five adults answered, all of them eighteen or older.", "Here's the headline number they published that September.",
            "The average American showers six point four times a week.", "Six point four.", "Now here's the limit on that number.", "Those showers were self-reported, in an online panel.",
            "So it can't tell you what any one person does.", "Now here's the bigger catch when you compare it with the past."]
    e, w = boredom("Chapter 7", old7); e = " | ".join(e)
    for must in ("explain a method or a limit", "punch line", "no beat"): assert must in e, (must, e)
    new7 = ["So how often do you actually use it?", "Take a guess before I tell you.", "Every day? Twice a day?", "Six point four times a week. //", "Most days. Not every day.",
            "Hold on to that number, because you're about to put it on a scale.", "And the number you'd really want, how often a family washed at home, left no count in any of these records."]
    assert boredom("Chapter 7", new7) == ([], []), boredom("Chapter 7", new7)
    print("selftest ok")

if __name__ == "__main__":
    if "--selftest" in sys.argv: selftest(); sys.exit(0)
    minutes = float(sys.argv[sys.argv.index("--minutes") + 1]) if "--minutes" in sys.argv else 12.0
    errs, warns, m = lint(open(sys.argv[1], encoding="utf-8").read(), minutes)
    for head, start, w in m.get("clock", []): print(f"  {mmss(start):>5}  {w:4d} words  {w / WPM * 60:4.0f} s  {head}")
    print("  " + " | ".join(f"{k} {v}" for k, v in m.items() if k != "clock"))
    for e in errs: print("ERROR", e)
    for w in warns: print("WARN ", w)
    print(f"{len(errs)} errors, {len(warns)} warnings")
    sys.exit(1 if errs else 0)
