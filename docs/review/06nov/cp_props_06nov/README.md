# City Park props, 6 Nov 2026 (family cp_props_06nov, branch art/cp-props-06nov)

City Park tall, Pepper's line, 46 px a metre. Obstacles have a 1 px dark outline. The leaf piles are decoration
drawn over Pepper. Their edge is the darkest rust of the leaves (luma 53), not an ink line.

| Piece | File | Size | Was | Method | Credits | asset_qa | Card |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hedge (board redraw) | riverwalk/art/scene/park_hedge.png | 66 x 72 | 64 x 72, topiary on two stems | SpriteCook GPT 2.5 (cp_hedge r1b) | 24 NB probe (rejected) + 48 | WARN (lone 3.1 %, organic) | cards/WARN_park_hedge.png |
| leaf pile | park_leaves.png | 56 x 22 | 49 x 22, noisy | GPT 2.5 (cp_leaves a) | 48 for the pair | PASS | cards/PASS_park_leaves.png |
| leaf pile, kicked (board redraw) | park_leaves_flat.png | 64 x 12 | 51 x 17, lone 8 % | the same render, the heap's 7 colours | (in the pair) | PASS | cards/PASS_park_leaves_flat.png |
| stepping stone (x5) | park_stone.png | 26 x 55 | a mossy post | GPT 2.5 (cp_rocklog a) | 48 for the pair | PASS | cards/PASS_park_stone.png |
| hollow log | park_hollowlog.png | 44 x 27 | a rounded box with two holes | the same render | (in the pair) | PASS | cards/PASS_park_hollowlog.png |
| duck boat | park_boat_front.png | 58 x 38 | 54 x 33, its inside showing | GPT 2.5 (cp_duckboat a) | 48 | PASS | cards/PASS_park_boat_front.png |

Triage kept as they are (0 credits): park_table_front (clean, asset_qa WARN 0.9 % noise; its 0.6 m height is the
perch, an owner design call), park_bush (front layer, on-screen median 32, 6 colours, only its top 19 rows show at the
screen's bottom edge; asset_qa WARN noise and blotches). Both are unchanged.

## How it was made
- Blockouts `art/gen/blockouts/cp_*.py`: 256 frame, Pepper at 1x on the ground line, the part shapes at true size.
- The probe on Nano Banana 2.1 drew the hedge 2x to 3x too big. Pepper stayed 1:1. Retry 1 of the family changed one
  input, the model, to GPT 2.5 Sunburst 1K. It follows the blockout grid at 4 px per art pixel. The other three jobs
  ran on GPT 2.5 as probes.
- Every render: `tools/grid4_cut.py` on the raw 1024 px image. Clean cells 96 to 99 %. Pepper measures 52 x 38 in every cut,
  the same as in the blockout.
- `tools/cut_cp_props.py`: the magenta is keyed, then the piece's window is cut out. Colours come from k-means in Lab.
  Each cluster takes its medoid, a real render pixel. A clean pass runs on the new cut.
- `tools/polish_cp_props.py`: GPT drew some pieces longer or taller than the blockout. Those are fitted by splicing out
  whole straight rows or columns where the seam matches best. The hedge loses 5 rows of leaf clumps, the leaf heap 5
  rows, the stone 3 columns, and the log its branch stub, 28 columns of bark grain and 3 rows. No pixel is resampled. Then
  blotches on the new cut are merged and the outline is closed in the ink. The leaves get a rust rim. Eight hand edits
  on the kicked pile are listed, with reasons, in `art/source/park_leaves_flat/edits.json`. Every step is in
  `art/source/NAME/edits.json`, and the .aseprite sources are written by tools/aseprite_io.py.

## In the game (scene.lua)
- HEDGE: centred on its box (the 66 px art has its outline 1 px outside the 64 px box on each side).
- Duck boat (`Sc.drawMoverArt`): its deck is row 20 of the art, and the hull's middle column 30 is centred on the mover box both
  ways round. The old 54 px art keeps its old anchor if it comes back.
- tests_look.lua: `LOOK_KICK=1` draws every leaf pile kicked (the frame for the flat pile).
- Frames: `frames/sweep_citypark_y144_x*.png` (after), `frames/before_x*.png`, `frames/kicked_x1290.png`.

## What to look at
- Hedge: it is greener and busier than the park around it. The shady gap with the stems is 17 rows; the crawl box under it is 19 px, so the lowest leaves overlap it by 2 px.
- Stones: pink granite. The wet band is about 7 px below the water line, under the pond tint.
- Duck boat: 4 px longer and 5 px taller than before, still on the same mover box.

## Fix round 1 (independent review, 6 Nov, 0 credits)
- park_hedge, item 4: the 2x2 orange leaf fragment the row splice left at (15-16, 45-46) is painted out in the leaf
  green (hand edits in edits.json). Its greens are pulled toward olive by one listed map (hue toward 80 degrees,
  saturation x 0.62, the same values; the lit top a warm gold, not pale). Now it sits with the autumn lime and ash.
  asset_qa WARN: lone 3.1 % and 4 small blotches, organic, warnings only. Card: cards/WARN_park_hedge.png.
- park_bush, item 5: redrawn by rule on its own silhouette by `tools/fix_cp_bush.py`, not a clean pass. The shape is
  kept. Four flat shades of its own colours: a rim on the top edge, a lit upper left with scalloped clumps, the shade,
  and dark twigs and side edges. Every changed pixel is in `art/source/park_bush/edits.json`; the old file is
  `park_bush_before.png`. asset_qa PASS. Card: cards/PASS_park_bush.png.
- park_stone is not touched (another track redoes the pond stones).
- Frames: frames/r1_x0420.png, frames/r1_x1800.png.
