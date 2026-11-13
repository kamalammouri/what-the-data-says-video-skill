"""Voice track with ElevenLabs: one clip per line of the script, concatenated, with exact start times.

  env -u ELEVENLABS_API_KEY python tts.py shots_voice.json [--only 1,2,3] [--gap 0.22] [--speed 1.0] [--voice NAME]
                                          [--brief brief.json] [--out voice.wav] [--timing timing.json] [--cache tts]
  python tts.py --selftest

Run it with `env -u ELEVENLABS_API_KEY`: a stale key in the shell shadows the .env of the working folder and gives HTTP 401
(4 Nov 2026); load_env() never overrides an existing variable.
Voice, model and speed come from brief.json ("voice": {"name", "model", "speed"}), each overridable by a flag.
shots_voice.json = [{"i": 1, "sentence": "..."}] written by make_shots.py --voice: whole lines of the script, never split.

Each sentence is synthesised to <cache>/eleven/S<i>.wav next to a .txt holding "voice|sentence": a clip whose text has not changed
is skipped, so a run is resumable and a corrected line costs only its own characters. No clip to make = no call to ElevenLabs:
changing --gap only re-joins the cache. The clips are joined with --gap seconds of silence into voice.wav; timing.json gets
{"chars", "end", "starts"} (per-character end times for the captions, one start per line for the cuts).

Guards: the script must be English (two videos went out with a French voice on this English channel, audit 8 Nov 2026);
the remaining character quota is read before the first call and the script exits with code 3 when it is short (never mix voices).
"""
import json, sys, os, time, wave, pathlib, subprocess, base64, shutil, re

SR = 44100   # ElevenLabs sends 44.1 kHz; the old 24 kHz cut everything above 12 kHz (air, s and t of the voice): 7 Nov 2026
GAP = 0.22   # seconds between lines. Measured 11 Nov 2026 on the 166 clips of bath-en: see references/voix-musique.md
MODEL = "eleven_multilingual_v2"
FRENCH = re.compile(r"\b(le|la|les|des|une|est|sont|vous|nous|avec|pour|dans|que|qui|toi|tes|nos|vos|ne|pas|sur|mais|ou|et|du|au|aux|ce|cette|ces|il|elle|ils|elles|était|ont|avaient)\b", re.I)

def arg_value(args, flag, default=None):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default

def load_env():
    """Read KEY=VALUE lines of a .env in the working directory or its parents (3 levels) into os.environ, without overriding."""
    here = pathlib.Path.cwd()
    for d in [here, *here.parents[:3]]:
        f = d / ".env"
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return

def french_lines(shots, limit=0.25):
    """Lines that read as French: a quarter of the words or more are French function words, or the line has French accents."""
    out = []
    for s in shots:
        t = (s.get("sentence") or "").strip(); w = t.split()
        if w and (len(FRENCH.findall(t)) / len(w) >= limit or re.search(r"[àâçèêëîïôûùœ]", t, re.I)): out.append(s["i"])
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
    voice, model = arg_value(args, "--voice", bv.get("name")), arg_value(args, "--model", bv.get("model") or MODEL)
    if not voice: sys.exit("no voice: brief.json \"voice\": {\"name\": ...} or --voice NAME")
    speed = float(arg_value(args, "--speed", bv.get("speed") or 1.0))      # 0.7..1.2; a speed other than 1 is part of the cache key
    key = lambda text: f"{voice if speed == 1.0 else f'{voice}@{speed}'}|{text}"
    gap = float(arg_value(args, "--gap", GAP)); only = {int(x) for x in arg_value(args, "--only", "").split(",") if x.strip()}
    cache = pathlib.Path(arg_value(args, "--cache", "tts")) / "eleven"; cache.mkdir(parents=True, exist_ok=True)
    clip = lambda s: (cache / f"S{s['i']:04d}.wav", cache / f"S{s['i']:04d}.txt")
    todo = [s for s in shots if (not only or s["i"] in only)
            and not (clip(s)[0].exists() and clip(s)[1].exists() and clip(s)[1].read_text(encoding="utf-8") == key(s["sentence"].strip()))]
    print(f"voice {voice} | model {model} | speed {speed} | gap {gap} s | {len(shots)} lines, {len(todo)} to generate")
    made = failed = 0
    if todo:
        if not os.environ.get("ELEVENLABS_API_KEY"): print("ELEVENLABS_API_KEY missing: put it in the .env of the working folder"); sys.exit(3)
        voice_id = eleven_voice_id(voice)
        need, left = sum(len(s["sentence"].strip()) for s in todo), eleven_quota()
        print(f"ElevenLabs quota: {left} characters left, {need} needed")
        if left < need: print("quota too short: ask the user, never switch voice inside a video"); sys.exit(3)
        for s in todo:
            text = s["sentence"].strip(); dst, txt = clip(s)
            print(f"#{s['i']:>3}: {text[:70]}")
            for n in range(4):                       # quota (429), transient 5xx, network: wait and retry
                try: tts_eleven(text, voice_id, model, dst, speed); txt.write_text(key(text), encoding="utf-8"); made += 1; time.sleep(0.3); break
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
        fr, cut = trim_edges(read_frames(clip(s)[0])); cuts[s["i"]] = (cut, len(fr) / 2 / SR)
        frames += [fr, silence]; t += (len(fr) // 2 + len(silence) // 2) / SR; words += len(s["sentence"].split())
    out, timing = pathlib.Path(arg_value(args, "--out", "voice.wav")), pathlib.Path(arg_value(args, "--timing", "timing.json"))
    with wave.open(str(out), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(b"".join(frames))
    ct = char_timing(shots, starts, cache, gap, cuts) if not missing else None
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
    print("selftest ok")

if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main(sys.argv[1:])
