# what-the-data-says-video — Claude Code skill

A [Claude Code](https://claude.com/claude-code) skill that produces a 12-minute faceless YouTube
video in the format "Do [Women/Men] Really [X]? What the Data Says": a common belief about
attraction, asked as the title question, then checked against six named studies or datasets —
what people say, what they do, whom they marry, the figure that contradicts it all — and an
honest answer. It was built for the channel The Hidden Bargain (@hiddenbargain); every norm in
`SKILL.md` comes from a dated measurement of that channel (`references/channel-results.md`).

It covers the whole pipeline, with a code gate after each step: subject scored on numbers →
angle and brief → fact-check → retention-oriented script → voice (ElevenLabs, per-character
timings) → shot list → images (Google Flow driven by Playwright, fixed cast) → data inserts →
edit (HyperFrames, word-by-word captions, animated inserts) → music bed → thumbnail, title,
description, tags, teaser Short → measurement in YouTube Studio at D+2 and D+7. The publication
sheet is linted against the YouTube Partner Program rules (`scripts/yt/ypp_lint.py`,
`references/monetisation-youtube.md`). The docs are in French; the scripts produce an
American-English video.

## Layout

- `SKILL.md` — the skill itself: the dated norms, the ten-step workflow and its gates, `brief.json`.
- `references/` — subjects, structure and writing, images and Flow, voice and music, edit,
  publication, measurement, monetisation rules, the agent table, the channel's measured results.
- `scripts/` — `make_shots.py` (shot-list template), `prompts.py` (shot-list lint + Flow prompts),
  `tts.py` (ElevenLabs with timings), `hf_build.py` (HyperFrames project; data inserts are built
  in by GSAP: bars grow while their figure counts up), `thumb.py`, `sheets.py`, `openverse.py`
  (CC0 music), `styles.json`.
- `scripts/flow/` — Playwright scripts that drive flow.google.com in a real Chrome.
- `scripts/yt/` — `keywords.py`, `script_lint.py`, `ypp_lint.py`, `analyze_video.py`,
  `studio.mjs` (read-only reader of YouTube Studio).
- `assets/cast/` — the three reference drawings of the channel's cast; `assets/example/script.md`.

## Install

```bash
git clone https://github.com/kamalammouri/what-the-data-says-video-skill ~/.claude/skills/what-the-data-says-video
```

Claude Code picks it up on the next session. Trigger it by asking for a "what the data says"
video, or run `/what-the-data-says-video`.

## Requirements

- **Python 3.13** with `pip install pillow imageio-ffmpeg librosa soundfile scenedetect yt-dlp`.
- **Node 18+** with the `playwright` package installed in some folder; point the scripts at it
  with `PLAYWRIGHT_DIR=/path/to/that/folder`. Google Chrome must be installed.
- **ElevenLabs**: put `ELEVENLABS_API_KEY=...` in a `.env` file of your *working* folder (never
  in this repo; `.gitignore` excludes it).
- **HyperFrames CLI** (`npx hyperframes`) and the `hyperframes` Claude Code skill.
- The **`hand-drawn-visuals`** skill for the data inserts
  ([faceless-video-skills](https://github.com/kamalammouri/faceless-video-skills)). Animated
  inserts need its `render.mjs --anim` export (pull request 6 of that repository); without it
  `hf_build.py` shows each insert as a still image.
- The Claude Code skills and agents named in `SKILL.md` and `references/agents.md`
  (`yt-script`, `yt-package`, `yt-seo`, `yt-chapters`, `yt-retention`; agents `story-architect`,
  `fact-checker`, `image-qc`, `visual-director`, `packaging-strategist`, `seo-metadata-editor`).

## Settings to adapt

The docs mention the author's machine and channel; change these to your own:

- `PLAYWRIGHT_DIR` — docs show `C:/Users/kamalAmmouri/Desktop/nastro`.
- `FLOW_PROFILE` — Chrome profile used for the Google session, default `~/.flow-profile`.
- `references/channel-results.md` and the norms of `SKILL.md` — they are measurements of one
  channel; replace them with your own channel's figures before trusting the thresholds.
- `assets/cast/` — the cast of that channel; draw your own.

## License

MIT — see `LICENSE`.
