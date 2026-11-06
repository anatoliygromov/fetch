# City Park pond: the stepping stones and the walks (art/cp-pond-06nov, 6 Nov 2026, 0 credits)

The owner looked at the tall pond (camera x 620, y 144) and said "this thing looks weird".

1. The stepping stones filled their 52 px box down to the bottom of the world and the pond was drawn half see-through over them: grey glass pillars standing in the water.
2. The treetop walk's legs ran from the walkway straight down into the pond every 46 px, in front of the willows and the bank, like cage bars. The cross braces made it worse.

## What changed
- **park_stone** (26 x 55 to 26 x 21, play, hand fix by rule, `tools/fix_cp_pond.py`): the top of the rock and its own wet band, 10 straight rows of the sides spliced out, an ink row at the waterline (the pond's dark edge row), 7 specks inside the face by hand rule (edits.json, `pond`). scene.lua draws it standing on the water, cut there, and under it only a dark reflection that sways 1 px per row. The box (24 x 52) is unchanged; a stone on dry ground would be drawn on its box as before (there is none in any level). Same in the flat City Park.
- **The walks are rope bridges** (`tools/build_cp_built.py`): no tree trunk stands under either walk, so each is hung: a 6 px timber pylon at each end on dry ground (TREETOP WALK: x 698 on the left bank under the plane tree's branch, x 944 on the right bank; ALDER WALK: x 1970 under its left end and x 2312 on the path, clear of the lamp at 2300), one rope cable sagging from pylon top to pylon top, a hanger to the deck at every other plank joint, knee braces under the deck ends. Nothing in the water, nothing under the deck across the pond, no tie. The pylons are one post from the ground to the cap (unfaded, drawn with the walk, in front of the willows). The decks are the same boxes, straight; nothing Pepper stands on moved.
- Untouched: the duck boat (the owner picks on the board).

## Frames (3x, colour and `_grey`)
`before_*` is the merge of art/cp-built-06nov and art/cp-props-06nov (f4e8d77), `after_*` this branch. `compare_*` puts them side by side.
- `*_tall_pond_x620_y144`: the spot the owner looked at
- `*_tall_treetop_x700_y144`: the treetop walk's right end, the winch keeper
- `*_tall_alder_x1900_y130`, `*_tall_alder_x2060_y130`: the alder walk over the creek
- `*_flat_pond_x620`, `*_flat_creek_x1980`: the flat City Park's stones

## Cards
PASS_park_stone, PASS_cp_walk704_deck/rail/legs, PASS_cp_walk1968_deck/rail/legs (asset_qa all PASS).
