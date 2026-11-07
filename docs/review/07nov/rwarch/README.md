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

`tools/build_rw_arch.py` (`--check`) builds `riverwalk/art/scene/rw_arch.png`, 130 x 25 (round 2), by rule, in the pier
art's own stone colours (13 colours, no new stone colours). Source: `art/source/rw_arch/rw_arch.aseprite`.
Art row 1 is world y 192, x 0 is world 1939: the plinth's own width, down to y 215. Pepper's line is y 216. Row 0
(y 191) is transparent except the two outer corners (round 2).

- **Jambs**: 18 px of the pier's ashlar a side, 10 px courses like the block above (lit top row, face, shade row,
  joint), the head joints alternating, a base course like the pier's plinth, the outer edges as the pier's sides.
  They come down to Pepper's line and hide the paving behind them, so the pier stands on the quay on solid stone.
- **Arch**: segmental, span 94 px, rise 16 (was 6). Its crown is at y 192, so the opening is as tall as the passage
  Pepper crawls through (y 192-216). A ring of voussoirs (5 px) on each haunch in the pier's light granite with
  radial joints, a lit arris row and a joint round its back. The ring runs up under the plinth, so the plinth reads
  as the band course over the arch. (Round 1 had a keystone hanging under the plinth; dropped in round 2.)
- **Vault**: one-point perspective from Pepper's eye height. Soffit and side walls in darker shades of the same
  stone (deeper is darker), a 2 px ring joint half way in. The floor is left open, so the paving runs through.
- **Far end**: the same arch scaled to 0.44 about the eye point, lit: daylight, a tree line of rounded crowns of
  uneven widths over a shaded row (round 2), the far quay's paving.
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

Round 2: `round2/arch_x1860_round2.png`, `round2/arch_pepper_inside_round2.png` (each with `_grey`),
`round2/round1_vs_round2_6x.png` (and `_grey`), `round2/corner_{left,right}_{round1,round2}_16x.png`.

Card: `cards/PASS_rw_arch.png` (round 2; 5x beside the approved bench, bin and lamp, in-game frame in colour and
greyscale, slot 130 x 25 OK).

## Round 2 (independent review round 1: FAIL with 3 small fixes)

| Review said | Done |
| --- | --- |
| One pixel of river at each outer corner, (1939, 191) and (2068, 191), where the plinth's rounded corner meets the jamb | The arch file has one more row on top (y 191), transparent except those two pixels, in the jambs' side colours (158 left, 109 right). Drawn at y 191. pier.png unchanged. |
| Drop the hanging keystone (wrong as stonework, 1 px or less over Pepper's back) | Dropped. The ring runs up under the band course; the opening is clear to y 192 everywhere. |
| The far trees read as a green railing (flat rows, a dark tick every 6 px) | A tree line: rounded crowns of uneven widths (3 to 8 px), 1 to 3 px over a shaded underside row, no regular ticks. |
| Keep 18 px jambs; do not lighten the vault; base course top row 243 to 219 if it does not hurt | Done. The base course's lit row is 219. asset_qa now PASS (contrast inside the back row). |

## Checks

| Check | Result |
| --- | --- |
| `tools/check_pepper.sh` | PEPPER UNCHANGED (3908 steps identical) |
| `tools/check_flow.sh` | 125 of 125 passed |
| `love riverwalk --level riverwalk --physics` | 56 of 56 passed, identical to the base branch (56 of 56) |
| `tools/check_tiled.sh` | TILED CHECK PASSED |
| `tools/check_backdrop.py` | BACKDROP OK |
| `tools/build_rw_arch.py --check` | CHECK PASS |
| `asset_qa.py --file rw_arch.png --layer back --level rw --fade 0` | PASS (round 2; round 1 was WARN, contrast 134). Lone 0.0 %, dirt 0.0 %, blotches 0, colours 13 |

All checks above were run again after round 2 with the same results.

About the round 1 WARN: the reviewer measured that its cause was the light end (the daylight and the 243 lit rows),
not the vault: the arch's darkest equals the approved pier's. Dropping the keystone and taking the base course's lit
row to 219 brought it inside the row; the vault is unchanged.

## Open questions

None left from round 1: the reviewer answered all three (keystone dropped, 18 px jambs kept, vault not lightened).
