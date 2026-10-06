#!/bin/sh
# Proves Pepper's files are byte-identical to aa38be5, the build the user approved ("I am happy with how the dog
# moves now"): her controller, her frame table, her sprite sheet, the buttons and the collision world.
# Checks the working tree (so uncommitted edits count too). Run from anywhere inside the repo.
cd "$(dirname "$0")/.."
APPROVED=aa38be5
bad=0
for f in riverwalk/pepper.lua riverwalk/pepper_frames.lua riverwalk/art/pepper.png riverwalk/input.lua riverwalk/world.lua; do
  want="$(git rev-parse "$APPROVED:$f" 2>/dev/null)"
  have="$(git hash-object "$f" 2>/dev/null)"
  if [ -n "$want" ] && [ "$want" = "$have" ]; then echo "  same  $f"
  else echo "  DIFF  $f"; bad=1; fi
done
if [ $bad -eq 0 ]; then echo "PEPPER FILES UNCHANGED: 5 files identical to $APPROVED"
else echo "PEPPER FILES CHANGED since $APPROVED"; exit 1; fi
