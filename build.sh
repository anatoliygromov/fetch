#!/bin/sh
# Packs the game folder into RIVERWALK.love (git ignores the output).
cd "$(dirname "$0")/riverwalk" && rm -f ../RIVERWALK.love && zip -qr ../RIVERWALK.love . && echo "built RIVERWALK.love"
