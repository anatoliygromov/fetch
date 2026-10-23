#!/bin/sh
# tools/fix_shots.sh OUTDIR [ROOT]: in-game frames (look on, 1x) of the pieces art/fixes touches, on the levels as
# played (tall City Park and tall Downtown): the statue and pedestal, the stall, the shelter, the plaza houses, the
# winch keeper, the ferry deck. ROOT defaults to this checkout (pass another worktree for the "before" frames).
set -e
OUT=${1:-out/fix_shots}; ROOT=${2:-$(cd "$(dirname "$0")/.." && pwd)}; mkdir -p "$OUT"
shoot() {  # level spots
  X=$(mktemp -d)
  (cd "$ROOT" && LOOK_SPOTS="$2" SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$X timeout 150 xvfb-run -a love riverwalk --level $1 --lookshots >/dev/null 2>&1) || true
  mkdir -p "$OUT/$1"; cp $X/love/*/look*_after.png "$OUT/$1/" 2>/dev/null || true
}
shoot downtown_tall "1360,424;600,424;1960,424;1500,424;1760,424"
shoot citypark_tall "950,328"
shoot riverwalk "1500,184"
ls "$OUT"/*/
