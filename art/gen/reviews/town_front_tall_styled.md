# town_front_tall<k>_<a-f> (37 styled fronts), town_drainpipe, town_front_tall7, town_door

Files: `riverwalk/art/scene/town_front_tall{1,2,3,5,6,7}_{a..f}.png`, `town_front_tall5.png`, `town_front_tall6.png`,
`town_drainpipe.png`, `town_door.png`. Maker: `tools/build_dt_facades.py`, `tools/build_dt_built.py`, branch
`night/06nov-dt` (2852d9c).

# Round 1 (reviewer, 6-7 Nov night)

Looked at: all 37 fronts at 3x (lower 176 px) and 2x (full 432 px) beside bench, bin and lamp; every screen of
`downtown_tall` at tiers y 0, 120, 240 (2x colour, 2x grey); `asset_qa.py --layer back --level dt --building`.

## Script
All 37 fronts, tall5, tall6, town_drainpipe: PASS (windows identical per storey, lone 0 %). town_door: FAIL
"outline 0 % dark" because the script's hook table lists it as a play piece; it is a back decoration and has no
outline, which is right. Note it in the hook table, no art change.

## Checklist (all fronts as one stamped family)
| Item | Result | Evidence |
| --- | --- | --- |
| Scale | PASS | doors 96-100 px (2.1 m), storeys 140 px, windows 50 x 80 px; the bench (56 px) sits under a door like a real bench |
| Layer | PASS | on screen median 152, darkest 100 (back row); grey sweep: lighter than the play pieces, darker than the far city |
| Outline | PASS | none; edges in a darker shade of the plaster |
| Shapes | PASS | window bars straight, surrounds square, the loggia house's gate arch an even curve |
| Shading | PASS | flat plaster, 3-4 shades per material, light upper left on surrounds and boxes |
| Palette | PASS | 11-20 colours per file, neutral darks |
| View | PASS | front-on, no tops |
| Fit | PASS | beside bench, bin and lamp at 5x: same pixel size, same crispness |
| Read | PASS | door, shop, gate, sign with boot/cup/key/fish read at 1x, no letters |
| Repeated parts | PASS | within one house all windows of a storey pixel-identical; curtains differ only between houses (checked x 1280-2560 at y 0 and y 120) |
| Light direction | PASS | one direction |
| Crisp | PASS | no averaged edges, no blotches, no lone pixels |
| Floats | PASS | downpipes run to the ground, signs on brackets, boxes on sills |
| Consistency | PASS | matches `dt_highroad_concept_a.png`: wall ties, pediments, geranium boxes, shutters, lace |
| Owner test | PASS | these are the first Downtown walls I would show him |

Verdict: PASS, the 37 fronts, drainpipe, tall7 and town_door are finished pieces.

Two notes, not defects of the files:
1. The fronts are only on screen at x 1100-2740. Everywhere else the street still stands in front of the
   quarter-scale `town_house1-3` (58 x 126 px, door about 20 px, a house the width of the bench) on the same
   back layer at the same scroll. See `dt_sweep_06nov.md`.
2. Six styles: the differences are in the window heads, cornices, curtains and shop colours. On the sweep they
   read as one street, not as six kinds of house, because every style shares the same storey grid and plaster
   ramps. Keep six. What would calm it is fewer plaster colours per screen (two neighbours in the same pink at
   x 1280 and x 2240 look better than the four-colour runs at x 1600-1920).

## The neighbour house, box 288 (x 2736-2816)
Style with shutters, flower box, blue shop front with a lamp in front: same family, same scale, stands on the
street, the shop's lit window reads. PASS. Keep the pair: one tower alone after the canal read as a cut-out.
