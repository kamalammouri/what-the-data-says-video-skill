"""Final mix: the voice of the HyperFrames render + the music, as film cues (default) or as a continuous bed.

  python mix.py hf/renders/<render>.mp4 music.mp3 out.mp4 [--shots shots.json] [--timing timing.json] [--chapters chapters.json]
                [--continuous] [--level -28] [--bed -34] [--lift 8]
  python mix.py --selftest

Cues (default since 23 Nov 2026, the user's choice: « la musique sur quelques parties, comme les films »): the music plays only
  - under the opening hook (0 to --intro seconds, 12 by default), then fades out;
  - across every chapter change (from 2.5 s before the new chapter to 5 s into it);
  - on every beat (a script line ending with " //": the silence tts.py leaves after it, then 3.5 s more under the next line);
  - under the last --outro seconds (35 by default).
  Elsewhere there is no music at all. Level --level LUFS (-28 by default, about 14 dB under the voice), ramps of 0.15 s in and
  1.2 s out. The voice-only stretches keep their 0.22 s gaps: check the result with analyze_video.py out.mp4 check --cues.
--continuous: the former bed, all along, --bed LUFS (-34, 20 dB under the voice), lifted by --lift dB on each beat
  (references/voix-musique.md §4; the user disliked it on 23 Nov 2026 after the medieval-bath video).
Voice chain in both modes: high-pass 70 Hz, compressor, loudnorm -14 LUFS, true peak -1.5 dB after the limiter.
"""
import json, pathlib, subprocess, sys

def beats(shots, starts):
    """(start, end) of each beat: the silence between the end of a line with "pause" and the start of the next line."""
    out = []
    for k, s in enumerate(shots[:-1]):
        p = float(s.get("pause") or 0)
        if p > 0: out.append((round(starts[k + 1] - p, 3), round(starts[k + 1], 3)))
    return out

def chapter_starts(shots, starts, chapters=None):
    """Start time of every chapter after the first: from chapters.json ({"shot": first shot}) or the "chapter" field of shots.json."""
    if chapters: return [round(starts[c["shot"] - 1], 3) for c in chapters[1:] if 0 < c["shot"] <= len(starts)]
    out, prev = [], None
    for s, t in zip(shots, starts):
        if s.get("chapter") is not None and prev is not None and s["chapter"] != prev: out.append(round(t, 3))
        prev = s.get("chapter", prev)
    return out

def cue_windows(dur, beat_w, chap, intro=12.0, outro=35.0):
    w = [(0.0, min(intro, dur))] + [(max(0.0, c - 2.5), min(dur, c + 5.0)) for c in chap] + [(a, min(dur, b + 3.5)) for a, b in beat_w]
    if outro > 0: w.append((max(0.0, dur - outro), dur))
    return sorted(w)

def window_expr(windows, rise=0.15, fall=1.2):
    """ffmpeg volume expression (eval=frame): 1 inside a window, 0 outside, with ramps; overlapping windows do not add up."""
    if not windows: return "0"
    terms = "+".join(f"clip((t-{a - rise:.3f})/{rise},0,1)*clip(({b:.3f}-t)/{fall},0,1)" if a > 0 else f"clip(({b:.3f}-t)/{fall},0,1)" for a, b in windows)
    return f"min(1,{terms})"

def lift_expr(windows, lift_db, rise=0.15, fall=0.35):
    """Continuous bed: 1 outside the beats, 10^(lift/20) inside, with short ramps."""
    if not windows: return "1"
    g = 10 ** (lift_db / 20) - 1
    terms = "+".join(f"clip((t-{a - rise:.3f})/{rise},0,1)*clip(({b + fall:.3f}-t)/{fall},0,1)" for a, b in windows)
    return f"1+{g:.3f}*min(1,{terms})"

def ffmpeg():
    try: import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError: return "ffmpeg"

def music_core(music, below=12.0):
    """The music without its quiet intro and outro: with cues, a beat that falls in a fade-in or a fade-out of the looped track is
    heard as dead air (23 Nov 2026, Not To Notice: 0-16 s and 129-149 s far under the rest, two beats failed the gate). Keeps from
    the first to the last second louder than (track loudness - below dB). Returns a trimmed copy (temp WAV) and (start, end)."""
    import array, math, tempfile
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", str(music), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array.array("h"); a.frombytes(raw[:len(raw) // 2 * 2]); n = len(a) // 8000
    if n < 30: return str(music), (0.0, len(a) / 8000)
    rms = [math.sqrt(sum(x * x for x in a[k * 8000:(k + 1) * 8000:4]) / 2000) + 1e-6 for k in range(n)]
    db = [20 * math.log10(r / 32768) for r in rms]; ref = 20 * math.log10(math.sqrt(sum(r * r for r in rms) / n) / 32768)
    live = [k for k, d in enumerate(db) if d > ref - below]
    s, e = float(live[0]), float(live[-1] + 1)
    if s < 0.5 and e > n - 0.5: return str(music), (0.0, n)
    out = str(pathlib.Path(tempfile.mkdtemp()) / "music_core.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(music), "-ss", f"{s:.2f}", "-to", f"{e:.2f}", "-ar", "48000", out], check=True)
    return out, (s, e)

def duration(path):
    err = subprocess.run([ffmpeg(), "-i", str(path)], capture_output=True, text=True).stderr
    hh, mm, ss = err.split("Duration: ")[1].split(",")[0].split(":"); return 3600 * int(hh) + 60 * int(mm) + float(ss)

def main(a):
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    render, music, out = pos[:3]
    shots = json.load(open(opt("--shots", "shots.json"), encoding="utf-8"))
    t = json.load(open(opt("--timing", "timing.json"), encoding="utf-8")); starts = [float(x) for x in (t["starts"] if isinstance(t, dict) else t)]
    cp = pathlib.Path(opt("--chapters", "chapters.json")); chapters = json.load(open(cp, encoding="utf-8")) if cp.exists() else None
    w = beats(shots, starts); dur = duration(render)
    if "--continuous" in a:
        level = float(opt("--bed", -34)); expr = lift_expr(w, float(opt("--lift", 8))); fade = f",afade=t=in:d=1,afade=t=out:st={max(0, dur - 3):.2f}:d=3"
        what = f"continuous bed {level:g} LUFS, {len(w)} beats lifted by {opt('--lift', 8)} dB"
    else:
        level = float(opt("--level", -28)); chap = chapter_starts(shots, starts, chapters)
        music, core = music_core(music)
        win = cue_windows(dur, w, chap, float(opt("--intro", 12)), float(opt("--outro", 35))); expr = window_expr(win); fade = ""
        on = sum(b - a for a, b in win)
        what = f"music cues {level:g} LUFS: opening, {len(chap)} chapter changes, {len(w)} beats, ending ({len(win)} cues, about {100 * on / dur:.0f} % of the video), music looped on its live part {core[0]:.1f}-{core[1]:.1f} s"
    fc = (f"[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3dB,loudnorm=I=-14:TP=-2:LRA=9[v];"
          f"[1:a]loudnorm=I={level:g}:TP=-9:LRA=7,volume=eval=frame:volume='{expr}'{fade}[m];"
          f"[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=disabled[a]")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", render, "-stream_loop", "-1", "-i", music, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out], check=True)
    print(f"{out}: {dur:.1f} s, {what} | next: python yt/analyze_video.py {out} check" + ("" if "--continuous" in a else " --cues"))

def selftest():
    sh = [{"i": 1, "chapter": 1}, {"i": 2, "pause": 0.9, "chapter": 1}, {"i": 3, "chapter": 2}, {"i": 4, "pause": 0.9, "chapter": 2}]
    st = [0, 2, 5, 7]
    assert beats(sh, st) == [(4.1, 5.0)], beats(sh, st)     # the last line's pause has no next line: no beat
    assert chapter_starts(sh, st) == [5.0] and chapter_starts(sh, st, [{"shot": 1}, {"shot": 3}]) == [5.0]
    win = cue_windows(100.0, [(40.0, 40.9)], [30.0])
    assert win == [(0.0, 12.0), (27.5, 35.0), (40.0, 44.4), (65.0, 100.0)], win
    e = window_expr(win); assert e.startswith("min(1,clip((12.000-t)/1.2,0,1)+") and "clip((t-27.350)/0.15,0,1)" in e, e
    assert window_expr([]) == "0" and lift_expr([], 8) == "1"
    e = lift_expr([(4.1, 5.0)], 8); assert e.startswith("1+1.512*min(1,") and "clip((5.350-t)/0.35,0,1)" in e, e
    print("mix selftest ok")

if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main(sys.argv[1:])
