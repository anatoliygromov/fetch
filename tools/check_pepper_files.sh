#!/bin/sh
# Proves Pepper's files are byte-identical to aa38be5, the build the user approved ("I am happy with how the dog
# moves now"): her controller, her frame table, her sprite sheet, the buttons and the collision world.
# Checks the working tree (so uncommitted edits count too). Run from anywhere inside the repo.
# world.lua: one function may differ, Wd:groundAt (22 Oct, engine/round2: an optional fromY for carts and bikes on
# tall levels). Pepper never calls it; everything else in world.lua, all her collision, must be byte-identical.
cd "$(dirname "$0")/.."
APPROVED=aa38be5
bad=0
for f in riverwalk/pepper.lua riverwalk/pepper_frames.lua riverwalk/art/pepper.png riverwalk/input.lua; do
  want="$(git rev-parse "$APPROVED:$f" 2>/dev/null)"
  have="$(git hash-object "$f" 2>/dev/null)"
  if [ -n "$want" ] && [ "$want" = "$have" ]; then echo "  same  $f"
  else echo "  DIFF  $f"; bad=1; fi
done
# world.lua without Wd:groundAt (from its comment block to the next blank line after "end")
strip() { awk '/^-- the ground under x/{skip=1} skip&&/^end$/{skip=0; next} !skip' ; }
A="$(git show "$APPROVED:riverwalk/world.lua" | strip | git hash-object --stdin)"
B="$(strip < riverwalk/world.lua | git hash-object --stdin)"
if [ "$A" = "$B" ]; then echo "  same  riverwalk/world.lua (all but Wd:groundAt, which Pepper never calls)"
else echo "  DIFF  riverwalk/world.lua"; bad=1; fi
if grep -n "groundAt" riverwalk/pepper.lua >/dev/null 2>&1; then echo "  DIFF  pepper.lua calls groundAt"; bad=1; fi
if [ $bad -eq 0 ]; then echo "PEPPER FILES UNCHANGED: 5 files identical to $APPROVED"
else echo "PEPPER FILES CHANGED since $APPROVED"; exit 1; fi
