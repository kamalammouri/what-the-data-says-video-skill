"""Final mix: the voice of the HyperFrames render + the music bed 20 dB under it, lifted on every beat.

  python mix.py hf/renders/<render>.mp4 music.mp3 out.mp4 [--shots shots.json] [--timing timing.json] [--lift 8] [--bed -34]
  python mix.py --selftest

Same chain as references/voix-musique.md §4 (voice: high-pass, compressor, -14 LUFS; bed: -34 LUFS, no sidechain), plus the beats
(22 Nov 2026, references/structure-ecriture.md §5): a script line ending with " //" leaves a silence after it in the voice (tts.py);
the bed rises by --lift dB over that silence and falls back when the voice returns, so the pause is heard as a breath, never as
dead air (the gate of analyze_video.py still sees sound: no pause over 0.7 s). Without any beat it is exactly the §4 command.
"""
import json, pathlib, subprocess, sys

def beats(shots, starts):
    """(start, end) of each beat: the silence between the end of a line with "pause" and the start of the next line."""
    out = []
    for k, s in enumerate(shots[:-1]):
        p = float(s.get("pause") or 0)
        if p > 0: out.append((round(starts[k + 1] - p, 3), round(starts[k + 1], 3)))
    return out

def lift_expr(windows, lift_db, rise=0.15, fall=0.35):
    """ffmpeg volume expression (eval=frame): 1 outside the beats, 10^(lift/20) inside, with short ramps."""
    if not windows: return "1"
    g = 10 ** (lift_db / 20) - 1
    terms = "+".join(f"clip((t-{a - rise:.3f})/{rise},0,1)*clip(({b + fall:.3f}-t)/{fall},0,1)" for a, b in windows)
    return f"1+{g:.3f}*min(1,{terms})"

def ffmpeg():
    try: import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError: return "ffmpeg"

def duration(path):
    err = subprocess.run([ffmpeg(), "-i", str(path)], capture_output=True, text=True).stderr
    hh, mm, ss = err.split("Duration: ")[1].split(",")[0].split(":"); return 3600 * int(hh) + 60 * int(mm) + float(ss)

def main(a):
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    render, music, out = pos[:3]
    shots = json.load(open(opt("--shots", "shots.json"), encoding="utf-8"))
    t = json.load(open(opt("--timing", "timing.json"), encoding="utf-8")); starts = t["starts"] if isinstance(t, dict) else t
    w = beats(shots, [float(x) for x in starts]); dur = duration(render)
    bed = float(opt("--bed", -34)); expr = lift_expr(w, float(opt("--lift", 8)))
    fc = (f"[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3dB,loudnorm=I=-14:TP=-2:LRA=9[v];"
          f"[1:a]loudnorm=I={bed:g}:TP=-9:LRA=7,volume=eval=frame:volume='{expr}',afade=t=in:d=1,afade=t=out:st={max(0, dur - 3):.2f}:d=3[m];"
          f"[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.84:level=disabled[a]")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", render, "-stream_loop", "-1", "-i", music, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out], check=True)
    print(f"{out}: {dur:.1f} s, bed {bed:g} LUFS, {len(w)} beats lifted by {opt('--lift', 8)} dB"
          + ("" if w else " (no line ends with \" //\" in script.md: no beat)") + f" | next: python yt/analyze_video.py {out} check")

def selftest():
    sh = [{"i": 1}, {"i": 2, "pause": 0.9}, {"i": 3}, {"i": 4, "pause": 0.9}]
    assert beats(sh, [0, 2, 5, 7]) == [(4.1, 5.0)], beats(sh, [0, 2, 5, 7])     # the last line's pause has no next line: no beat
    e = lift_expr([(4.1, 5.0)], 8)
    assert e.startswith("1+1.512*min(1,") and "clip((t-3.950)/0.15,0,1)" in e and "clip((5.350-t)/0.35,0,1)" in e, e
    assert lift_expr([], 8) == "1"
    print("mix selftest ok")

if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main(sys.argv[1:])
