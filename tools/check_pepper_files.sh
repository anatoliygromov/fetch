#!/bin/sh
# Proves Pepper's files are byte-identical to aa38be5, the build the user approved ("I am happy with how the dog
# moves now"): her controller, her frame table, her sprite sheet, the buttons and the collision world.
# Checks the working tree (so uncommitted edits count too). Run from anywhere inside the repo.
# world.lua: one function may differ, Wd:groundAt (22 Oct, engine/round2: an optional fromY for carts and bikes on
# tall levels). Pepper never calls it; everything else in world.lua, all her collision, must be byte-identical.
# input.lua: one block may differ, the menus' last-used device (7 Nov, day/07nov-integration: 4afd8d2, UI pilot 2,
# added I.last, I.setLast and I.startDevice, so the menus draw pad or key glyphs). Pepper never reads them; every
# key and button binding and every function she uses must be byte-identical.
cd "$(dirname "$0")/.."
APPROVED=aa38be5
bad=0
for f in riverwalk/pepper.lua riverwalk/pepper_frames.lua riverwalk/art/pepper.png; do
  want="$(git rev-parse "$APPROVED:$f" 2>/dev/null)"
  have="$(git hash-object "$f" 2>/dev/null)"
  if [ -n "$want" ] && [ "$want" = "$have" ]; then echo "  same  $f"
  else echo "  DIFF  $f"; bad=1; fi
done
# input.lua without the last-used device block (its 2 comment lines, I.last, I.setLast, I.startDevice)
istrip() { awk '/^-- the device used last/{c=2} c>0{c--; next} /^I\.last = /||/^function I\.setLast\(/||/^function I\.startDevice\(/{next} {print}' ; }
A="$(git show "$APPROVED:riverwalk/input.lua" | istrip | git hash-object --stdin)"
B="$(istrip < riverwalk/input.lua | git hash-object --stdin)"
if [ "$A" = "$B" ]; then echo "  same  riverwalk/input.lua (all but the menus' last-used device, which Pepper never reads)"
else echo "  DIFF  riverwalk/input.lua"; bad=1; fi
if grep -nE "I\.last|setLast|startDevice" riverwalk/pepper.lua >/dev/null 2>&1; then echo "  DIFF  pepper.lua reads the last-used device"; bad=1; fi
# world.lua without Wd:groundAt (from its comment block to the next blank line after "end")
strip() { awk '/^-- the ground under x/{skip=1} skip&&/^end$/{skip=0; next} !skip' ; }
A="$(git show "$APPROVED:riverwalk/world.lua" | strip | git hash-object --stdin)"
B="$(strip < riverwalk/world.lua | git hash-object --stdin)"
if [ "$A" = "$B" ]; then echo "  same  riverwalk/world.lua (all but Wd:groundAt, which Pepper never calls)"
else echo "  DIFF  riverwalk/world.lua"; bad=1; fi
if grep -n "groundAt" riverwalk/pepper.lua >/dev/null 2>&1; then echo "  DIFF  pepper.lua calls groundAt"; bad=1; fi
if [ $bad -eq 0 ]; then echo "PEPPER FILES UNCHANGED: 5 files identical to $APPROVED (world.lua and input.lua: all but the one stated block each)"
else echo "PEPPER FILES CHANGED since $APPROVED"; exit 1; fi
