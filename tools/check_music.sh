#!/bin/sh
# Checks the music files: each one in riverwalk/music/manifest.txt decodes in LOVE, has its expected length, peaks
# under -1 dBFS, and each loop's last sample runs into its first without a click; and sfx.lua picks the right
# track for the title, a level with a tune and a level without one (tools/musiccheck/main.lua).
# Run from anywhere; needs LÖVE (no window, no sound device).
cd "$(dirname "$0")/.."
T="$(mktemp -d)"; cp tools/musiccheck/*.lua "$T"/; cp -r riverwalk/music "$T"/music       # sfx.lua finds music/ there
SDL_AUDIODRIVER=dummy XDG_DATA_HOME="$T/save" love "$T" "$(pwd)/riverwalk/music" "$(pwd)/riverwalk" 2>&1 | grep -E 'PASS|FAIL|MUSIC|ERROR' > "$T/log"
cat "$T/log"; grep -q 'MUSIC OK' "$T/log"; R=$?; rm -rf "$T"; exit $R
