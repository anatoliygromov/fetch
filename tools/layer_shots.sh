#!/bin/sh
# tools/layer_shots.sh OUTDIR: in-game frames of the three art levels (look on), plus a colour | greyscale sheet
# (OUTDIR/ladder_<level>.png, 2x) to check the layer rule: furthest layer lightest, nearer layers darker.
set -e
OUT=${1:-out/layer_shots}; mkdir -p "$OUT"; ROOT=$(cd "$(dirname "$0")/.." && pwd)
for L in riverwalk citypark downtown; do
  X=$(mktemp -d)
  (cd "$ROOT" && SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$X timeout 120 xvfb-run -a love riverwalk --level $L --lookshots >/dev/null 2>&1) || true
  mkdir -p "$OUT/$L"; cp $X/love/*/look*_after.png "$OUT/$L/" 2>/dev/null || true
done
python3 -I - "$OUT" <<'PY'
import sys, glob
from PIL import Image
out = sys.argv[1]
for L in ("riverwalk", "citypark", "downtown"):
    fs = sorted(glob.glob(f"{out}/{L}/*after.png"))
    if not fs: continue
    W, H = 640, 480
    sheet = Image.new("RGB", (W * 2 + 8, (H + 8) * len(fs) - 8), (30, 30, 34))
    for i, f in enumerate(fs):
        im = Image.open(f).convert("RGB").resize((W, H), Image.NEAREST)
        sheet.paste(im, (0, i * (H + 8))); sheet.paste(im.convert("L").convert("RGB"), (W + 8, i * (H + 8)))
    sheet.save(f"{out}/ladder_{L}.png"); print(f"{out}/ladder_{L}.png", len(fs), "frames")
PY
