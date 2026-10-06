#!/bin/sh
# Checks the game flow: love riverwalk --flowtest drives the menus through a whole run (see riverwalk/tests_flow.lua)
# and prints PASS / FAIL lines. The screenshots of every screen end up on one sheet, copied to the path given
# (default: flow_screens.png in the repo root, which git ignores). Run from anywhere; needs LÖVE (headless: xvfb-run).
cd "$(dirname "$0")/.."
OUT="${1:-$(pwd)/flow_screens.png}"
LOG="$(mktemp)"
SDL_AUDIODRIVER=dummy xvfb-run -a -s "-screen 0 1400x1100x24" love riverwalk --flowtest > "$LOG" 2>&1
grep -E 'PASS|FAIL|passed|^ERROR' "$LOG"
SHEET="$(sed -n 's/^SHEET \(.*\) (.*/\1/p' "$LOG")"
if [ -n "$SHEET" ] && [ -f "$SHEET" ]; then mkdir -p "$(dirname "$OUT")"; cp "$SHEET" "$OUT" && echo "screens: $OUT"; fi
grep -q 'FAIL\|^ERROR' "$LOG" && { rm -f "$LOG"; exit 1; }
rm -f "$LOG"
