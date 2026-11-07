# RWARCH track, 7 Nov: River Walk bridge underpass arch

Branch `day/07nov-rwarch` (based on `origin/day/07nov-ground`). 0 credits, no image service called. Pepper
unchanged. The approved pier art (`riverwalk/art/scene/pier.png`) is not touched. Collision and floors unchanged.

## What the owner said

Board, 7 Nov: `rw_bridge_arch_06n`: redraw (no comment).

## What was wrong

The 6 Nov arch (scene.lua `archBack`, from 8f91328) was drawn per pixel behind the paving, in the 12 px between the
plinth's bottom (y 192) and the paving's back edge (y 204): 6 px jambs, a 6 px rise arch, a dark vault. Seen at 1x
it was a low wide dark slot. The pier block seemed to sit on a gap, not on stone. The jambs stopped at the paving's
back edge while the pier is an obstacle on Pepper's line, so the bridge also looked set back from her.

Side by side, `arch_history_5nov_6nov_7nov.png` (and `_grey`): 5 Nov (navy band), 6 Nov (shallow slot), 7 Nov
(this). Neither earlier version was better, so nothing of them is kept except the passage data and the ground
track's slanted shadow.

## What I built and how

`tools/build_rw_arch.py` (`--check`) builds `riverwalk/art/scene/rw_arch.png`, 130 x 24, by rule, in the pier
art's own stone colours (13 colours, no new stone colours). Source: `art/source/rw_arch/rw_arch.aseprite`.
Art (0, 0) is world (1939, 192): the plinth's own width, down to y 215. Pepper's line is y 216.

- **Jambs**: 18 px of the pier's ashlar a side, 10 px courses like the block above (lit top row, face, shade row,
  joint), the head joints alternating, a base course like the pier's plinth, the outer edges as the pier's sides.
  They come down to Pepper's line and hide the paving behind them, so the pier stands on the quay on solid stone.
- **Arch**: segmental, span 94 px, rise 16 (was 6). Its crown is at y 192, so the opening is as tall as the passage
  Pepper crawls through (y 192-216). A ring of voussoirs (5 px) on each haunch in the pier's light granite with
  radial joints, a lit arris row and a joint round its back. The ring runs up under the plinth, so the plinth reads
  as the band course over the arch. A keystone wedge hangs from the plinth at the crown (8 px wide, y 192-194).
- **Vault**: one-point perspective from Pepper's eye height. Soffit and side walls in darker shades of the same
  stone (deeper is darker), a 2 px ring joint half way in. The floor is left open, so the paving runs through.
- **Far end**: the same arch scaled to 0.44 about the eye point, lit: daylight, the far quay's trees and paving.
  It sits right behind Pepper when she crawls through, so she reads clearly.
- **Drawing** (scene.lua `archFront`, called from `Sc.passageFront`): drawn after the ground, in the back look like
  the pier art above it (the 6 Nov arch took the ground's grade, a shade off the plinth). `archBack` and its per-pixel
  loop are gone; `Sc.passageBack` draws nothing for an arch.
- **Shadow**: the ground track's slanted shadow is unchanged. It lines up with the new jambs: its back rows are now
  under the jambs, its slanted left end comes out from under the left jamb's foot, and its right end runs out past
  the right jamb, as the sun is upper left. No change needed.
- `riverwalk/level/riverwalk.lua`: only a comment. The art's x is `vx0 - 1` (1939). A new field broke the Tiled round
  trip, so none was added.

## Frames (3x, colour and greyscale)

| | before (6 Nov) | after |
| --- | --- | --- |
| the bridge, camera x 1860 | `arch_x1860_before.png`, `_grey` | `arch_x1860_after.png`, `_grey` |
| Pepper crawling inside (x 2004) | `arch_pepper_inside_before.png`, `_grey` | `arch_pepper_inside_after.png`, `_grey` |
| history 5 / 6 / 7 Nov | `arch_history_5nov_6nov_7nov.png`, `_grey` | |

Card: `cards/WARN_rw_arch.png` (5x beside the approved bench, bin and lamp, in-game frame in colour and greyscale,
slot 130 x 24 OK).

## Checks

| Check | Result |
| --- | --- |
| `tools/check_pepper.sh` | PEPPER UNCHANGED (3908 steps identical) |
| `tools/check_flow.sh` | 125 of 125 passed |
| `love riverwalk --level riverwalk --physics` | 56 of 56 passed, identical to the base branch (56 of 56) |
| `tools/check_tiled.sh` | TILED CHECK PASSED |
| `tools/check_backdrop.py` | BACKDROP OK |
| `tools/build_rw_arch.py --check` | CHECK PASS |
| `asset_qa.py --file rw_arch.png --layer back --level rw --fade 0` | WARN: ladder contrast 134, the back row allows 120. Lone 0.0 %, dirt 0.0 %, blotches 0, darkest 100 (row: 80), colours 13 (row: 20) |

About the contrast WARN: it comes from the pier's own joint colour (97) and the vault against the lit far opening.
The piece is the foot of an obstacle on Pepper's line (the pier she walks on), which is checked as back only because
it takes the back look. Lifting the vault two more steps passes the number but loses the "under the bridge" read.

## Open questions

1. The keystone hangs 3 px below the crown (y 192-194). Pepper's crawling back is at y 194-197, so it can touch her
   back for one frame as she passes the middle. Keep it, or drop it to a flat crown (opening fully clear to y 192)?
2. Pepper still crosses the jambs at both ends of the passage (the collision passage is x 1936-2072, the jambs are
   inside it), drawn in front of them as everywhere. Narrower jambs (12 px) would shorten that, but read less
   load-bearing. Keep 18 px?
3. The contrast WARN above: accept, or lighten the vault?
