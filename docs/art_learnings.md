# FETCH! art learnings

The rules are in `docs/BIBLE.md`. This file is the evidence behind them and the rejection log. Every rejection adds a
line here in the same session: what the owner saw, the cause, and the check that now catches it (docs/WORKFLOW.md).
History before 25 Oct: project doc `claude/archive-to-25oct.md` (the 23 Oct art learnings in full).

## What produced art the owner liked
1. Art already at game pixel size, cut 1:1: Pepper and Mia (SpriteCook 1x, pixel-engine animation at 1x), the
   portraits (SpriteCook native ~64 px), the cat (hand-pixeled 30 px, animated at 1x).
2. A render sampled on its own grid: one colour per art pixel (majority or centre), never an average.
3. Isolate-exactly edits from the owner's concept crops (the River Walk baseline: bench, bin, lamp, tree, building).
4. Flat fills drawn in code for simple geometry (pavement, kiosks, awnings) and parts stamped on a grid (Old Town row).
5. Palettes from per-material ramps with neutral darks.

## What made art dirty, washed out or "AI"
1. Area averaging to a non-integer size (box, bilinear, Lanczos): soft edges, wobbly lines, blotchy walls.
2. Haze, pale, mist in prompts; lifted darks and baked fades on soft art.
3. Layers carved out of one flattened picture.
4. Too few pixels for the detail (windows as noise); buildings colour-reduced from a painting.
5. Painting models (Artlist) used for game pixels: fake pixel art, off grid, wrong scale, scenes copied from style input.
6. Generated lettering halved to size; code-drawn organic shapes.

## Rejection log
| Date | What the owner saw | Cause | Check that now catches it |
| --- | --- | --- | --- |
| 23 Oct | Art batch 1 "dirty, flushed" | box filter twice before and after transfer | grid_cut.py samples one colour per cell; BIBLE grid rule |
| 25 Oct | Pilot: cyclist "the size of a toddler", scenes copied, 3 of 12 usable (3,360 credits) | grey box ignored, full screen as style input, no part sizes | blockout with Pepper and part shapes; preflight size and blockout checks |
| 25 Oct | Picked cyclist: lumpy wheels, black jaggy outline, mottled coat, beige helmet | script PASS taken as ready; per-image quantise; no polish, no eye review | level palette snap in grid_cut; pipeline.py requires .aseprite polish and a 9-item review |
| 25 Oct | Credit audit: 76 % of Artlist and ~43 % of SpriteCook wasted | assets before a fixed target; Artlist for pixels; rules not enforced; no ledger | WORKFLOW.md, preflight tool rule and caps, ledger.csv, Sunday audit |
| 25 Oct | River Walk house and front trees end inside the screen, sky above them | made at a third of true scale, placed with their tops at y 39 to 47 | BIBLE rule "taller than the viewport"; `tools/check_backdrop.py` |
| 25 Oct | Board: free fixes smother details (building, gable), cafe window railings holed; tram shed and shelter "super small" in the scene | script clean pass on painted art; pieces sized without metres | BIBLE: no automated clean pass on existing art; redraws sized from metres (preflight); backlog in docs/art_backlog.md |
| 25 Oct | Gull: "it has holes and doesnt really look like a bird"; a pixel fix was not enough | 22 px SpriteCook gull (19 Oct) without a blockout: smaller than true size, holes between the feathers, frames of different sizes | a redraw from a true-size spec (body 28 px, wingspan 64 px) and one still animated at 1x; asset_qa pinholes and frame-size checks before the board |
