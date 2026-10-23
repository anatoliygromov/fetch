#!/bin/sh
# Art batch 1 in context (r8/preview): runs riverwalk/tests_artpreview.lua on River Walk, the tall Downtown and the
# bonus round, and copies the shots and frame runs to $OUT/<tag>/. Tag "after": the game as it is. Tag "before":
# the same game with the batch's hook files taken out (a copy of riverwalk/ without them), so the placeholders and
# the old art show. Tag "misfit": the tall Downtown with the pieces that do not fit their boxes (gable, chimney,
# dormer) put in the LOVE save folder under their hook names, to show why they are not wired. Then
# tools/art_preview.py makes the pairs, the GIFs and the overview.
#   tools/art_preview.sh before|after|misfit [out dir]
cd "$(dirname "$0")/.."
TAG="${1:-after}"; OUT="${2:-/home/claude/out/r8-preview}"
GAME=riverwalk
if [ "$TAG" = before ]; then
  GAME="$(mktemp -d)/riverwalk"; cp -r riverwalk "$GAME"
  for f in $(python3 tools/wire_r8_art.py --list); do rm -f "${GAME:?}/${f:?}"; done
fi
mkdir -p "$OUT/$TAG"
RUNS="${AP_RUNS:---level_riverwalk --level_downtown_tall --bonus}"   # (AP_RUNS: some of them)
[ "$TAG" = misfit ] && RUNS='--level_downtown_tall'
for r in $RUNS; do
  run="$(echo "$r" | tr _ ' ' | sed 's/downtown tall/downtown_tall/')"
  D="$(mktemp -d)"
  [ "$TAG" = misfit ] && python3 tools/wire_r8_art.py --misfit "$D/love/pepper_riverwalk"
  XDG_DATA_HOME="$D" SDL_AUDIODRIVER=dummy AP_TAG="$TAG" xvfb-run -a love "$GAME" $run --artpreview > "$D/log.txt" 2>&1
  grep -i 'error\|STUCK' "$D/log.txt" | head -5
  cp -r "$D"/love/pepper_riverwalk/"$TAG"_* "$OUT/$TAG/" 2>/dev/null
  rm -rf "${D:?}"
done
echo "$TAG: $(ls "$OUT/$TAG" | wc -l) shots and runs in $OUT/$TAG"
