#!/bin/sh
# Packs the game folder into CITYPARK_greybox.love with City Park as the default level (git ignores the output).
# The same game as RIVERWALK.love plus one file, default_level.txt ("citypark"), added only inside the zip.
# Usage: ./build_citypark.sh [output path]
OUT="${1:-$(pwd)/CITYPARK_greybox.love}"
TMP="$(mktemp -d)"
cp -r "$(dirname "$0")/riverwalk/." "$TMP/" && echo citypark > "$TMP/default_level.txt"
rm -f "$OUT" && (cd "$TMP" && zip -qr "$OUT" .) && rm -rf "$TMP" && echo "built $OUT"
