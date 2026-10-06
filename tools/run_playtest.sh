#!/bin/sh
# The playtest lab (docs/playtest/method.md): every persona plays every level, several seeds each, then the
# analysis (tools/analyse_playtest.py) writes the tables, charts and frame strips.
#   tools/run_playtest.sh [OUT_DIR] [SEEDS] [FRESH_SEEDS]
# OUT_DIR defaults to ../out/playtest (next to the repo), SEEDS to 20 (campaign: each level played after the
# ones before it), FRESH_SEEDS to 10 (Downtown and River Walk played cold, nothing learnt before). Runs two jobs
# at a time. Needs LÖVE 11.5, xvfb-run and Python 3 with Pillow and matplotlib.
cd "$(dirname "$0")/.."
REPO="$(pwd)"
OUT="${1:-$REPO/../out/playtest}"
SEEDS="${2:-20}"
FRESH="${3:-10}"
mkdir -p "$OUT/runs" "$OUT/caps"
OUT="$(cd "$OUT" && pwd)"
PERSONAS="$(python3 -c "import json;print(' '.join(p['id'] for p in json.load(open('docs/playtest/personas.json'))['personas']))")"
LOVE() { SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk "$@"; }

echo "1/4 the autopilots' clean runs, with the event log"
for L in citypark downtown riverwalk; do echo "$L"; done | xargs -P 2 -I{} sh -c \
  'SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk --level {} --auto --log --out "'"$OUT"'/runs/auto-{}.json" > /dev/null 2>&1'

echo "2/4 persona runs: $SEEDS seeds per persona and level, $FRESH fresh seeds for levels 2 and 3"
JOBS="$(mktemp)"
for L in citypark downtown riverwalk; do for P in $PERSONAS; do
  s=1; while [ $s -le "$SEEDS" ]; do echo "--level $L --playtest $P --seed $s --out $OUT/runs/$L-$P-$s.json"; s=$((s + 1)); done
  if [ "$L" != citypark ]; then
    s=1; while [ $s -le "$FRESH" ]; do echo "--level $L --playtest $P --seed $s --fresh --out $OUT/runs/fresh-$L-$P-$s.json"; s=$((s + 1)); done
  fi
done; done > "$JOBS"
echo "   $(wc -l < "$JOBS") runs"
xargs -P 2 -L 1 sh -c 'SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk "$@" > /dev/null 2>&1 || echo "FAILED: $*"' _ < "$JOBS"
rm -f "$JOBS"

echo "3/4 frames: replaying the runs the pictures come from (the runs are deterministic)"
python3 tools/analyse_playtest.py plan "$OUT" > "$OUT/caps/plan.txt"
xargs -P 2 -L 1 sh -c 'SDL_AUDIODRIVER=dummy xvfb-run -a love riverwalk "$@" > /dev/null 2>&1 || echo "FAILED: $*"' _ < "$OUT/caps/plan.txt"

echo "4/4 analysis"
python3 tools/analyse_playtest.py report "$OUT"
