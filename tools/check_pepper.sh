#!/bin/sh
# Plays River Walk on autopilot and compares Pepper's position, speed, clip and frame on every step with
# tools/pepper_golden_trace.txt. The trace was first recorded from the build the user approved (aa38be5); it was
# recorded again on ml/levels because River Walk itself changed (the first difference, step 460, is the autopilot
# jumping for the new kiosk awning; see docs/riverwalk_notes.md), and again on levels/v2 for the harbour (the first
# difference, step 1658, is the autopilot stopping at the quay to wait for a rowing boat; on assets/v2 the boats'
# decks went down 7 px, first difference step 2295). Level changes
# legitimately change this trace:
# Pepper herself is proven unchanged by tools/check_pepper_lab.sh (a test room, no level) and
# tools/check_pepper_files.sh (her files against aa38be5). Run from the repo root; needs LÖVE (headless: xvfb-run).
cd "$(dirname "$0")/.."
T="$(mktemp)"; E="$(mktemp)"
SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk --auto --trace 2>"$E" | grep '^T ' > "$T"
if cmp -s "$T" tools/pepper_golden_trace.txt; then
  echo "PEPPER UNCHANGED: $(wc -l < "$T") steps identical"; rm -f "$T" "$E"
else
  echo "PEPPER CHANGED:"; diff "$T" tools/pepper_golden_trace.txt | head -5; grep -A8 '^ERROR' "$E"; rm -f "$T" "$E"; exit 1
fi
