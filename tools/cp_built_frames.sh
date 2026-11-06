#!/bin/bash
# tools/cp_built_frames.sh OUTDIR LEVEL XS YS [PX] [ROOT]: in-game frames, look on, no HUD, 1x (tests_look.lua
# LOOK_SWEEP with LOOK_XS / LOOK_YS / LOOK_PX) of any level; each frame also as greyscale (_grey.png). Used for the
# 6 Nov built City Park and River Walk pieces (art/cp-built-06nov).
OUT=$1; LEVEL=$2; ROOT=${6:-$(cd "$(dirname "$0")/.." && pwd)}; mkdir -p "$OUT"; X=$(mktemp -d)
(cd "$ROOT" && LOOK_SWEEP=1 LOOK_XS="$3" LOOK_YS="$4" LOOK_PX="${5:-140}" SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$X \
  timeout 200 xvfb-run -a love riverwalk --level $LEVEL --lookshots >/dev/null 2>&1) || true
find "$X" -name 'sweep_*.png' -exec cp {} "$OUT"/ \;
python3 - "$OUT" <<'PY'
import sys, glob
from PIL import Image
for f in glob.glob(sys.argv[1] + '/sweep_*.png'):
    if f.endswith('_grey.png'): continue
    Image.open(f).convert('L').save(f[:-4] + '_grey.png')
PY
ls "$OUT" | grep -v _grey
