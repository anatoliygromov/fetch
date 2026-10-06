#!/bin/sh
# Proves Pepper's controller is unchanged, independent of any level: love riverwalk --pepperlab builds a small
# test room in code (riverwalk/pepperlab.lua) and plays a fixed script of button presses (run, walk, crawl, tap
# and held jumps, ledge scrambles, skid, turn, landings, bark, pick up, one-way ledge, a moving deck, stairs, water).
# Her x, y, speed, clip, frame, face, mode, ground and crouch on every step are compared with
# tools/pepper_lab_golden.txt, recorded from the build the user approved (aa38be5's pepper.lua, pepper_frames.lua,
# art/pepper.png, input.lua and world.lua). Run from the repo root; needs LÖVE (headless: xvfb-run).
cd "$(dirname "$0")/.."
T="$(mktemp)"; E="$(mktemp)"
SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk --pepperlab 2>"$E" | grep '^L ' > "$T"
if [ -s "$T" ] && cmp -s "$T" tools/pepper_lab_golden.txt; then
  echo "PEPPER UNCHANGED: $(wc -l < "$T") lab steps identical"; rm -f "$T" "$E"
else
  echo "PEPPER CHANGED:"; diff "$T" tools/pepper_lab_golden.txt | head -5; grep -A8 '^ERROR' "$E"; rm -f "$T" "$E"; exit 1
fi
