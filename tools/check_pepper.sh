#!/bin/sh
# Proves Pepper moves exactly as in the build the user approved (try/scenery-v2 at aa38be5):
# plays the level on autopilot and compares her position, speed, clip and frame on every step
# with tools/pepper_golden_trace.txt. Run from the repo root; needs LÖVE (headless: xvfb-run).
cd "$(dirname "$0")/.."
T="$(mktemp)"; E="$(mktemp)"
SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk --auto --trace 2>"$E" | grep '^T ' > "$T"
if cmp -s "$T" tools/pepper_golden_trace.txt; then
  echo "PEPPER UNCHANGED: $(wc -l < "$T") steps identical"; rm -f "$T" "$E"
else
  echo "PEPPER CHANGED:"; diff "$T" tools/pepper_golden_trace.txt | head -5; grep -A8 '^ERROR' "$E"; rm -f "$T" "$E"; exit 1
fi
