#!/bin/bash
# tools/dt_sample_frames.sh OUTDIR [XS] [YS] [PX]: the Downtown (tall) sample screen frames, look on, no HUD, 1x
# (riverwalk/tests_look.lua LOOK_SWEEP with LOOK_XS / LOOK_YS / LOOK_PX). Default: screen 7 (camera x 1920) at the
# high road camera (y 120) and the street camera (y 240), Pepper at the camera + 140.
ROOT=$(cd "$(dirname "$0")/.." && pwd); OUT=$1; mkdir -p "$OUT"; X=$(mktemp -d)
(cd "$ROOT" && LOOK_SWEEP=1 LOOK_XS="${2:-1920}" LOOK_YS="${3:-120,240}" LOOK_PX="${4:-140}" SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$X \
  timeout 150 xvfb-run -a love riverwalk --level downtown_tall --lookshots >/dev/null 2>&1) || true
cp "$X"/love/*/sweep_*.png "$OUT"/ 2>/dev/null || find "$X" -name 'sweep_*.png' -exec cp {} "$OUT"/ \;
ls "$OUT"
