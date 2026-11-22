#!/usr/bin/env bash
# Generates every image of a prompts file in Google Flow and survives its "unusual activity" refusals.
# User rule (9 Nov 2026): at the FIRST refusal, keep what is on disk, close ALL Chrome windows, relaunch Flow in a fresh Chrome
# session, then resume. Stops after MAXIDLE (5) restarts in a row with no new image: then ask the user (a new Flow project is the fallback).
#   bash <skill>/scripts/flow/flow_loop.sh prompts.json flow/<video>     run from the working folder; project URL in flow/project.txt
#   bash <skill>/scripts/flow/flow_loop.sh thumbs.json  flow/thumbs      same loop for the two thumbnail scenes
# Env: PACE (ms between images, 20000), RESTWAIT (s between restarts, 60), MAXIDLE (5), FLOW_PROJECT_FILE (flow/project.txt),
#      PLAYWRIGHT_DIR, FLOW_CHANNEL=msedge + FLOW_PROFILE (Edge: only the Edge windows of the Flow profile are closed).
# WARNING: with Chrome (the default) every chrome.exe of the machine is closed at each restart: tell the user before starting.
set -u
PROMPTS=${1:-prompts.json}; OUT=${2:-flow/out}
PFILE=${FLOW_PROJECT_FILE:-flow/project.txt}
[ -f "$PROMPTS" ] || { echo "no $PROMPTS"; exit 2; }
[ -f "$PFILE" ] || { echo "no $PFILE: put the URL of the Flow project that holds the three reference images in it"; exit 2; }
PROJECT=$(cat "$PFILE")
SK="$(cd "$(dirname "$0")" && pwd)"
if [ -z "${PLAYWRIGHT_DIR:-}" ]; then [ -d "$HOME/video-tools/node_modules/playwright" ] && PLAYWRIGHT_DIR="$HOME/video-tools" || PLAYWRIGHT_DIR="C:/Users/kamalAmmouri/Desktop/nastro"; fi
export PLAYWRIGHT_DIR
LOG=batch.log; idle=0; round=0
count() { ls "$OUT"/*.jpg "$OUT"/*.png "$OUT"/*.webp 2>/dev/null | wc -l; }
# Edge (FLOW_CHANNEL=msedge, user request 10 Nov 2026): only the msedge windows of the Flow profile are closed, the user's own Edge stays open
# macOS / Linux (22 Nov 2026): no PowerShell; only the Chrome started on the Flow profile is closed, the user's own Chrome stays open
kill_chrome() { if ! command -v powershell >/dev/null 2>&1; then pkill -f -- "--user-data-dir=${FLOW_PROFILE:-$HOME/.flow-profile}" 2>/dev/null; elif [ "${FLOW_CHANNEL:-chrome}" = msedge ]; then powershell -NoProfile -ExecutionPolicy Bypass -File "$SK/kill_flow_edge.ps1" >/dev/null 2>&1; else powershell -NoProfile -Command "try { Stop-Process -Name chrome -Force -ErrorAction Stop } catch {}" >/dev/null 2>&1; fi; [ -n "${BPID:-}" ] && kill "$BPID" 2>/dev/null; sleep 3; }
trap 'pkill -P $$ 2>/dev/null; kill_chrome' EXIT
while true; do
  round=$((round+1)); before=$(count)
  kill_chrome
  node "$SK/browser.mjs" > browser.log 2>&1 & BPID=$!
  for i in $(seq 1 30); do curl -s http://127.0.0.1:9222/json/version >/dev/null && break; sleep 2; done
  node "$SK/goto.mjs" "$PROJECT" >> $LOG 2>&1
  echo "=== loop round $round $(date +%T) ($before images)" >> $LOG
  MAXFAIL=1 PACE=${PACE:-20000} node "$SK/batch.mjs" "$PROMPTS" "$OUT" >> $LOG 2>&1
  if tail -3 $LOG | grep -q "done:" && ! tail -3 $LOG | grep -q "Stopping"; then
    missing=$(tail -1 $LOG | grep -o "[0-9]* skipped or failed" | cut -d' ' -f1)
    [ "${missing:-0}" = "0" ] && { echo "=== loop finished: $(count) images" >> $LOG; exit 0; }
  fi
  # harvest only when this round left a generated-but-not-downloaded tile (TIMEOUT / NOT QUEUED): a refusal makes no image,
  # and every image already downloaded is on disk (user remark 10 Nov 2026: never re-download what is already there)
  if sed -n "/=== loop round $round /,\$p" $LOG | grep -qE "TIMEOUT|NOT QUEUED"; then
    rm -rf "$OUT/harvest"; node "$SK/harvest.mjs" "$OUT" >> harvest_loop.log 2>&1      # H-numbers change at every harvest: start from an empty folder
  fi
  after=$(count); [ "$after" -gt "$before" ] && idle=0 || idle=$((idle+1))
  echo "=== loop restart after refusal: $after images, idle rounds $idle" >> $LOG
  kill_chrome; sleep ${RESTWAIT:-60}      # measured 10 Nov: back-to-back restarts kept hitting the same block; one quiet minute between them
  [ $idle -ge ${MAXIDLE:-5} ] && { echo "=== loop STOP: MAXIDLE restarts without progress, ask the user" >> $LOG; exit 2; }
done
