"""Voice track: one clip per line of the script, concatenated, with exact start times.

  python tts.py shots_voice.json [--only 1,2,3] [--gap 0.22] [--speed 1.0] [--voice NAME] [--engine voicestudio|eleven]
                                 [--seed 42] [--brief brief.json] [--out voice.wav] [--timing timing.json] [--cache tts]
  python tts.py --selftest

Engine (brief.json "voice": {"engine"}, default "voicestudio"):
- voicestudio (default since 22 Nov 2026): local and free. The VoiceStudio app must be running (`voicestudio status`); its
  backend answers on http://127.0.0.1:3900 (override: VOICESTUDIO_URL). Each line goes to /v1/audio/speech with the saved
  voice named in brief.json and a fixed seed (same seed = same timbre on every line); the clip is then transcribed by
  /v1/audio/transcriptions with word timestamps and the words are aligned back on the script text, which gives the same
  per-character end times ElevenLabs used to send. Measured 22 Nov 2026 on an M-series Mac: about 30 s per line on the first call.
- eleven: the former ElevenLabs path, kept as a fallback. Needs ELEVENLABS_API_KEY in the .env of the working folder; run it with
  `env -u ELEVENLABS_API_KEY` (a stale key in the shell shadows the .env and gives HTTP 401, 4 Nov 2026).
Voice, speed and seed come from brief.json ("voice": {"engine", "name", "speed", "seed"}), each overridable by a flag.
shots_voice.json = [{"i": 1, "sentence": "..."}] written by make_shots.py --voice: whole lines of the script, never split.
A line may carry "pause": seconds of silence added after it (a beat, " //" at the end of the script line): the cache is untouched.

Each sentence is synthesised to <cache>/<engine>/S<i>.wav next to a .txt holding "voice|sentence": a clip whose text has not changed
is skipped, so a run is resumable and a corrected line costs only its own clip. Changing --gap only re-joins the cache.
The clips are joined with --gap seconds of silence into voice.wav; timing.json gets
{"chars", "end", "starts"} (per-character end times for the captions, one start per line for the cuts).

Guards: the script must be English (two videos went out with a French voice on this English channel, audit 8 Nov 2026);
exit code 3 when the engine is not reachable (VoiceStudio closed) or the ElevenLabs quota is short (never mix voices).
"""
import json, sys, os, time, wave, pathlib, subprocess, base64, shutil, re

SR = 44100   # ElevenLabs sends 44.1 kHz; the old 24 kHz cut everything above 12 kHz (air, s and t of the voice): 7 Nov 2026
GAP = 0.22   # seconds between lines. Measured 11 Nov 2026 on the 166 clips of bath-en: see references/voix-musique.md
MODEL = "eleven_multilingual_v2"
ENGINE = "voicestudio"
VS_URL = os.environ.get("VOICESTUDIO_URL", "http://127.0.0.1:3900")
SEED = 42    # VoiceStudio: one fixed seed for the whole video, or the timbre drifts from line to line
FRENCH = re.compile(r"\b(le|la|les|des|une|est|sont|vous|nous|avec|pour|dans|que|qui|toi|tes|nos|vos|ne|pas|sur|mais|ou|et|du|au|aux|ce|cette|ces|il|elle|ils|elles|était|ont|avaient)\b", re.I)

def arg_value(args, flag, default=None):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default

def load_env():
    """Read KEY=VALUE lines of a .env in the working directory or its parents (3 levels) into os.environ, without overriding."""
    here = pathlib.Path.cwd()
    for d in [here, *list(here.parents)[:3]]:     # list(): slicing .parents needs Python 3.10+
        f = d / ".env"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return

def french_lines(shots, limit=0.25):
    """Lines that read as French: a quarter of the words or more are French function words, or the line has French accents
    AND at least one French function word in ten. Accents alone no longer flag a line (22 Nov 2026: an English line naming
    « René de Lespinasse » or « Saint-Barthélemy » was refused, while the history format needs French proper names)."""
    out = []
    for s in shots:
        t = (s.get("sentence") or "").strip(); w = t.split()
        r = len(FRENCH.findall(t)) / len(w) if w else 0
        if w and (r >= limit or (r >= 0.1 and re.search(r"[àâçèêëîïôûùœ]", t, re.I))): out.append(s["i"])
    return out

def ffmpeg():
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return shutil.which("ffmpeg") or sys.exit("ffmpeg not found: pip install imageio-ffmpeg")

def to_wav(src, dst):
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", str(SR), "-sample_fmt", "s16", str(dst)], check=True)

def read_frames(path):
    """The 16-bit mono SR frames of a WAV, converting through ffmpeg when the format differs."""
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == SR: return w.readframes(w.getnframes())
    tmp = path.with_suffix(".sr.wav"); to_wav(path, tmp)
    with wave.open(str(tmp), "rb") as w: frames = w.readframes(w.getnframes())
    tmp.unlink(); return frames

def eleven_req(path, data=None, headers=None):
    import urllib.request
    req = urllib.request.Request("https://api.elevenlabs.io/v1" + path, data=data,
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], **(headers or {})})
    return urllib.request.urlopen(req, timeout=180).read()

def eleven_voice_id(name):
    if len(name) >= 20 and " " not in name: return name
    voices = json.loads(eleven_req("/voices"))["voices"]
    for v in voices:
        if v["name"].split(" - ")[0].strip().lower() == name.lower(): return v["voice_id"]   # library names read "Brian - Deep, Resonant..."
    sys.exit(f"ElevenLabs voice '{name}' not found; available: {[v['name'] for v in voices]}")

def eleven_quota():
    s = json.loads(eleven_req("/user/subscription")); return s["character_limit"] - s["character_count"]

def tts_eleven(text, voice_id, model, dst, speed=1.0):
    """with-timestamps endpoint: the audio plus one end time per character, saved next to the clip (<name>.align.json)."""
    import urllib.error
    body = json.dumps({"text": text, "model_id": model, "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.0, "speed": speed}}).encode()
    try: raw = eleven_req(f"/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128", body, {"Content-Type": "application/json"})
    except urllib.error.HTTPError as e:
        if e.code in (401, 402): print(f"ElevenLabs refused ({e.code}): {e.read()[:200]} (key shadowed by the shell? run with env -u ELEVENLABS_API_KEY)"); sys.exit(3)
        raise
    r = json.loads(raw); audio = base64.b64decode(r["audio_base64"]); al = r.get("alignment") or r.get("normalized_alignment")
    if al: dst.with_suffix(".align.json").write_text(json.dumps({"chars": "".join(al["characters"]), "end": al["character_end_times_seconds"]}), encoding="utf-8")
    mp3 = dst.with_suffix(".mp3"); mp3.write_bytes(audio); to_wav(mp3, dst); mp3.unlink()

def vs_req(path, data=None, headers=None, timeout=600):
    import urllib.request
    req = urllib.request.Request(VS_URL + path, data=data, headers=headers or {})
    return urllib.request.urlopen(req, timeout=timeout).read()

def vs_alive():
    try: return json.loads(vs_req("/.well-known/voicestudio-speech", timeout=10)) is not None
    except Exception: return False

def vs_multipart(fields, file_field, file_path):
    """multipart/form-data body (urllib has none): fields may repeat, e.g. timestamp_granularities[]."""
    b = "----vs" + os.urandom(8).hex(); out = []
    for k, v in fields:
        out += [f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()]
    out += [f"--{b}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{pathlib.Path(file_path).name}\"\r\n"
            f"Content-Type: audio/wav\r\n\r\n".encode(), pathlib.Path(file_path).read_bytes(), f"\r\n--{b}--\r\n".encode()]
    return b"".join(out), f"multipart/form-data; boundary={b}"

def vs_words(wav):
    body, ctype = vs_multipart([("response_format", "verbose_json"), ("timestamp_granularities[]", "word"), ("language", "en")], "file", wav)
    return json.loads(vs_req("/v1/audio/transcriptions", body, {"Content-Type": ctype})).get("words") or []

_norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())

def align_chars(text, words):
    """Per-character end times of `text` from ASR word timings: script words and heard words are matched in order
    (difflib on normalised words), unmatched script words (numbers heard as digits, names spelt differently) are spread
    between their matched neighbours, and inside a word the time grows linearly with the characters. Spaces take the
    end of the word before them. Same shape as the ElevenLabs alignment: {"chars": text, "end": [one float per char]}."""
    import difflib
    spans = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    if not spans: return {"chars": text, "end": []}
    sw = [_norm(text[a:b]) for a, b in spans]; hw = [_norm(w.get("word", "")) for w in words]
    t = [None] * len(spans)
    for blk in difflib.SequenceMatcher(None, sw, hw, autojunk=False).get_matching_blocks():
        for k in range(blk.size): t[blk.a + k] = (float(words[blk.b + k]["start"]), float(words[blk.b + k]["end"]))
    lo = float(words[0]["start"]) if words else 0.0; hi = float(words[-1]["end"]) if words else 0.1 * len(text)
    i = 0
    while i < len(t):                                  # fill runs of unmatched words by sharing the gap by character count
        if t[i] is not None: i += 1; continue
        j = i
        while j < len(t) and t[j] is None: j += 1
        a = t[i - 1][1] if i > 0 else lo; z = t[j][0] if j < len(t) else hi; z = max(z, a)
        n = sum(spans[k][1] - spans[k][0] for k in range(i, j)); acc = a
        for k in range(i, j):
            d = (z - a) * (spans[k][1] - spans[k][0]) / max(1, n); t[k] = (acc, acc + d); acc += d
        i = j
    end, last = [], lo
    for (a, b), (s, e) in zip(spans, t):
        while len(end) < a: end.append(round(last, 3))          # spaces before this word
        for c in range(a, b): end.append(round(s + (e - s) * (c - a + 1) / (b - a), 3))
        last = e
    while len(end) < len(text): end.append(round(last, 3))
    return {"chars": text, "end": end}

def tts_voicestudio(text, voice, dst, speed=1.0, seed=SEED, duration=None, num_step=None):
    """Local VoiceStudio: one clip. `duration` (s) makes the engine aim at that length, which is how the words a minute are held
    (the speed setting barely moved it: 198 words/min at speed 0.91, measured 22 Nov 2026). `num_step` trades quality for time
    (32: 33 s for a 17-word line, 16: 12 s, same day). Word timings are NOT taken per line: one transcription costs about 85 s
    whatever its length, so the whole track is transcribed once after the join (track_timing)."""
    req = {"input": text, "voice": voice, "response_format": "wav", "speed": speed, "language": "en", "seed": seed}
    if duration: req["duration"] = duration
    if num_step: req["num_step"] = num_step
    raw = dst.with_suffix(".raw.wav"); raw.write_bytes(vs_req("/v1/audio/speech", json.dumps(req).encode(), {"Content-Type": "application/json"}))
    to_wav(raw, dst); raw.unlink()

def track_timing(shots, starts, wav, chunk=60.0):
    """Per-character times of the joined track from VoiceStudio transcriptions with word timestamps, one per ~`chunk` seconds of
    whole lines (one call for 11 min answered HTTP 504 after the backend timeout, 22 Nov 2026). Word times are offset by the
    start of their chunk, then aligned on the whole script text."""
    import tempfile
    text = " ".join(s["sentence"].strip() for s in shots) + " "
    cuts = [0]
    for k, st in enumerate(starts):
        if st - starts[cuts[-1]] >= chunk: cuts.append(k)
    words = []
    with tempfile.TemporaryDirectory() as tmp:
        for n, a in enumerate(cuts):
            b = cuts[n + 1] if n + 1 < len(cuts) else None
            t0 = starts[a]; part = pathlib.Path(tmp) / f"c{n}.wav"
            cmd = [ffmpeg(), "-y", "-loglevel", "error", "-ss", f"{t0:.3f}", "-i", str(wav)] + (["-t", f"{starts[b] - t0:.3f}"] if b else []) + [str(part)]
            subprocess.run(cmd, check=True)
            print(f"  words {n + 1}/{len(cuts)} ({t0:.0f} s)", flush=True)
            words += [{**w, "start": float(w["start"]) + t0, "end": float(w["end"]) + t0} for w in vs_words(part)]
    al = align_chars(text, words)
    return {"chars": al["chars"], "end": al["end"], "starts": starts}

def stretch(frames, tempo):
    """Slow down (tempo < 1) or speed up a clip without changing the pitch (ffmpeg atempo). The engine reads about 15 to 25 %
    faster than the duration asked (195 words/min for 155 asked, 22 Nov 2026): tempo brings the track back into 165-175."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        a, b = pathlib.Path(tmp) / "a.wav", pathlib.Path(tmp) / "b.wav"
        with wave.open(str(a), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(frames)
        subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(a), "-filter:a", f"atempo={tempo}", "-ar", str(SR), "-ac", "1", str(b)], check=True)
        return read_frames(b)

def char_timing(shots, starts, cache, gap, cuts):
    """Global per-character timing from the clips' align files: sentences joined by one space, end times offset by each clip's start
    (minus the lead silence trim_edges removed). None when a clip has no alignment (then timing.json is only the list of starts)."""
    chars, end = "", []
    for s, st in zip(shots, starts):
        al = cache / f"S{s['i']:04d}.align.json"
        if not al.exists(): return None
        a = json.load(open(al, encoding="utf-8"))
        if not a["end"]: return None
        cut, top = cuts[s["i"]]   # (lead removed, trimmed clip length): the engine may stamp the last character at the end of its trailing silence
        fix = lambda e: round(st + min(top, max(0.0, e - cut)), 3)
        chars += a["chars"] + " "; end += [fix(e) for e in a["end"]] + [round(fix(a["end"][-1]) + gap, 3)]
    return {"chars": chars, "end": end, "starts": starts}

KEEP_LEAD, KEEP_TRAIL = 0.03, 0.05   # silence kept around a clip so no consonant is clipped; it counts as part of the --gap

def trim_edges(frames, keep_lead=KEEP_LEAD, keep_trail=KEEP_TRAIL, thr_db=-40.0):
    """Cut the silence the engine leaves around a clip (~0.1 s lead, ~0.4 s trail, up to 2.6 s on a one-word line, measured
    4 Nov 2026) so the pause between lines is the --gap and nothing else. Returns (frames, seconds removed at the start).
    Before 11 Nov 2026 0.15 s was kept on top of the gap: a "0.35 s" gap was a 0.50 s pause (speech ratio 0.78 on bath-en)."""
    import array
    a = array.array("h"); a.frombytes(frames); n = len(a); win = int(SR * 0.02); thr = 32768 * 10 ** (thr_db / 20)
    def quiet(seg): return (sum(x * x for x in seg) / max(1, len(seg))) ** 0.5 < thr
    lead = 0
    while lead + win < n and quiet(a[lead:lead + win]): lead += win
    trail = 0
    while trail + win < n - lead and quiet(a[n - trail - win:n - trail]): trail += win
    lo, hi = max(0, lead - int(SR * keep_lead)), n - max(0, trail - int(SR * keep_trail))
    return a[lo:hi].tobytes(), lo / SR

def main(args):
    load_env()
    src = next((a for a in args if a.endswith(".json") and (args.index(a) == 0 or not args[args.index(a) - 1].startswith("--"))), "shots_voice.json")
    shots = [s for s in json.load(open(src, encoding="utf-8")) if (s.get("sentence") or "").strip()]
    bp = pathlib.Path(arg_value(args, "--brief", "brief.json")); brief = json.load(open(bp, encoding="utf-8")) if bp.exists() else {}
    bv = brief.get("voice") or {}
    lang = (brief.get("voice_language") or "en")[:2].lower()
    if lang != "en": sys.exit(f"brief.json voice_language is '{lang}': this channel is English only")
    if fr := french_lines(shots): sys.exit(f"lines that read as French, not sent to the voice: {fr[:12]}")
    engine = arg_value(args, "--engine", bv.get("engine") or ENGINE)
    if engine not in ("voicestudio", "eleven"): sys.exit(f"unknown engine '{engine}': voicestudio or eleven")
    voice, model = arg_value(args, "--voice", bv.get("name")), arg_value(args, "--model", bv.get("model") or MODEL)
    if not voice: sys.exit("no voice: brief.json \"voice\": {\"name\": ...} or --voice NAME")
    speed = float(arg_value(args, "--speed", bv.get("speed") or 1.0))      # 0.7..1.2; a speed other than 1 is part of the cache key
    seed = int(arg_value(args, "--seed", bv.get("seed") if bv.get("seed") is not None else SEED))
    wpm = float(arg_value(args, "--wpm", bv.get("wpm") or 0)) or None          # VoiceStudio: target words a minute per line (duration)
    num_step = int(arg_value(args, "--num-step", bv.get("num_step") or 0)) or None
    tempo = float(arg_value(args, "--tempo", bv.get("tempo") or 1.0))     # applied at the join, the cache is untouched (stretch)
    dur_of = lambda text: round(len(text.split()) / wpm * 60, 2) if wpm else None
    tag = voice if engine == "eleven" else f"{voice}#{seed}" + (f"~{wpm:g}wpm" if wpm else "") + (f"/n{num_step}" if num_step else "")
    key = lambda text: f"{tag if speed == 1.0 else f'{tag}@{speed}'}|{text}"
    gap = float(arg_value(args, "--gap", GAP)); only = {int(x) for x in arg_value(args, "--only", "").split(",") if x.strip()}
    cache = pathlib.Path(arg_value(args, "--cache", "tts")) / engine; cache.mkdir(parents=True, exist_ok=True)
    clip = lambda s: (cache / f"S{s['i']:04d}.wav", cache / f"S{s['i']:04d}.txt")
    todo = [s for s in shots if (not only or s["i"] in only)
            and not (clip(s)[0].exists() and clip(s)[1].exists() and clip(s)[1].read_text(encoding="utf-8") == key(s["sentence"].strip()))]
    print(f"engine {engine} | voice {voice} | " + (f"model {model}" if engine == "eleven" else f"seed {seed}")
          + f" | speed {speed} | gap {gap} s | {len(shots)} lines, {len(todo)} to generate")
    made = failed = 0
    if todo:
        if engine == "eleven":
            if not os.environ.get("ELEVENLABS_API_KEY"): print("ELEVENLABS_API_KEY missing: put it in the .env of the working folder"); sys.exit(3)
            voice_id = eleven_voice_id(voice)
            need, left = sum(len(s["sentence"].strip()) for s in todo), eleven_quota()
            print(f"ElevenLabs quota: {left} characters left, {need} needed")
            if left < need: print("quota too short: ask the user, never switch voice inside a video"); sys.exit(3)
            speak = lambda text, dst: tts_eleven(text, voice_id, model, dst, speed)
        else:
            if not vs_alive(): print(f"VoiceStudio not reachable at {VS_URL}: open the app (or `voicestudio status`), then run again"); sys.exit(3)
            speak = lambda text, dst: tts_voicestudio(text, voice, dst, speed, seed, dur_of(text), num_step)
        for s in todo:
            text = s["sentence"].strip(); dst, txt = clip(s)
            print(f"#{s['i']:>3}: {text[:70]}", flush=True)
            for n in range(4):                       # quota (429), transient 5xx, network: wait and retry
                try: speak(text, dst); txt.write_text(key(text), encoding="utf-8"); made += 1; time.sleep(0.3); break
                except Exception as e:
                    print(f"  retry in {10 * 3 ** n}s after: {str(e)[:160]}")
                    if dst.exists(): dst.unlink()
                    time.sleep(10 * 3 ** n)
            else: failed += 1
    # join in line order, exact start times
    silence = b"\x00\x00" * int(max(0.0, gap - KEEP_LEAD - KEEP_TRAIL) * SR); frames, starts, missing, t, cuts, words = [], [], [], 0.0, {}, 0
    for s in shots:
        starts.append(round(t, 3))
        if not clip(s)[0].exists(): missing.append(s["i"]); continue
        fr, cut = trim_edges(read_frames(clip(s)[0]))
        if tempo != 1.0: fr = stretch(fr, tempo); cut = cut / tempo
        cuts[s["i"]] = (cut, len(fr) / 2 / SR)
        sil = silence + b"\x00\x00" * int(float(s.get("pause") or 0) * SR)   # a beat (script line ending with " //"): extra silence after the line
        frames += [fr, sil]; t += (len(fr) // 2 + len(sil) // 2) / SR; words += len(s["sentence"].split())
    out, timing = pathlib.Path(arg_value(args, "--out", "voice.wav")), pathlib.Path(arg_value(args, "--timing", "timing.json"))
    with wave.open(str(out), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(b"".join(frames))
    ct = char_timing(shots, starts, cache, gap, cuts) if not missing else None
    if engine == "voicestudio" and not missing and "--no-words" not in args:   # one transcription for the whole track (see tts_voicestudio)
        sel = [s for s in shots if not only or s["i"] in only]
        if len(sel) == len(shots):
            try: print("word timings: transcribing the whole track once…", flush=True); ct = track_timing(shots, starts, out)
            except Exception as e: print(f"WARN word timings failed ({str(e)[:120]}): timing.json keeps the line starts only"); ct = None
    json.dump(ct or starts, open(timing, "w", encoding="utf-8"))
    wpm = words / (t / 60) if t else 0
    print(f"clips: {made} made, {len(shots) - len(missing) - made} cached, {failed} failed | {out} {t / 60:.2f} min, {wpm:.0f} words/min "
          f"(target 165-175) | {timing}{' with per-character times' if ct else ''} | missing clips: {missing or 'none'}"
          + (" (run again without --only for the full track)" if only else ""))
    if not only and not missing and not 165 <= wpm <= 175: print(f"WARN {wpm:.0f} words/min is outside 165-175: change voice.speed in brief.json (cache key changes: every clip is paid again) or shorten the slow lines")

def selftest():
    assert french_lines([{"i": 1, "sentence": "Imagine-toi assis près d'un feu il y a 40 000 ans."}, {"i": 2, "sentence": "Nos ancêtres avaient plus de temps libre que toi ?"},
                         {"i": 3, "sentence": "So, do women really prefer tall men?"}, {"i": 4, "sentence": "In nineteen sixty-seven, only three percent of newlyweds did."}]) == [1, 2]
    a = __import__("array").array("h", [0] * SR + [9000, -9000] * (SR // 2) + [0] * SR)          # 1 s silence, 1 s tone, 1 s silence
    fr, cut = trim_edges(a.tobytes()); assert 0.94 < cut < 1.0 and 1.05 < len(fr) / 2 / SR < 1.12, (cut, len(fr) / 2 / SR)
    heard = [{"word": "In", "start": 0.1, "end": 0.2}, {"word": "1896,", "start": 0.25, "end": 1.0}, {"word": "New", "start": 1.1, "end": 1.3},
             {"word": "York", "start": 1.3, "end": 1.6}, {"word": "burned.", "start": 1.7, "end": 2.1}]
    al = align_chars("In eighteen ninety-six, New York burned.", heard)
    assert len(al["end"]) == len(al["chars"]) and al["end"] == sorted(al["end"]), al
    assert al["end"][1] == 0.2 and al["end"][-1] == 2.1 and 0.2 < al["end"][10] < 1.0, al   # digits heard for words: spread in between
    assert len(vs_multipart([("a", "1"), ("a", "2")], "file", __file__)[0]) > 100
    print("selftest ok")

if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main(sys.argv[1:])
