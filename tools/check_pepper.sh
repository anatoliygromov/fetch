#!/bin/sh
# Proves Pepper moves exactly as in the build the user approved (try/scenery-v2 at aa38be5):
# plays the level on autopilot and compares her position, speed, clip and frame on every step
# with tools/pepper_golden_trace.txt. Run from the repo root; needs LÖVE (headless: xvfb-run).
cd "$(dirname "$0")/.."
SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk --auto --trace 2>/dev/null | grep '^T ' > /tmp/pepper_trace.txt
if cmp -s /tmp/pepper_trace.txt tools/pepper_golden_trace.txt; then
  echo "PEPPER UNCHANGED: $(wc -l < /tmp/pepper_trace.txt) steps identical"
else
  echo "PEPPER CHANGED:"; diff /tmp/pepper_trace.txt tools/pepper_golden_trace.txt | head -5; exit 1
fi
