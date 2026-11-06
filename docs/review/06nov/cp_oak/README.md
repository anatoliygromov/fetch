# City Park old oak, retry 2 (6 Nov 2026, branch art/cp-oak-06nov)

Job 55457888 (GPT 2.5 Sunburst 2K, 2 variants, refs rw_lime + cp_lime 4x, 76 credits, spent and logged before this
run). Used: variant a (`art/gen/renders/cp_oak_r2a_raw.png`, SpriteCook asset 1dad2249). Variant b runs into the
frame's right edge (a flat cut) and has a thinner limb structure; not used.

## How it was made
1. `tools/grid4_cut.py` on the 2048 raw render: pitch 4, phase (0,2), 87 % clean cells, 512 x 511. One real pixel per
   cell, never an average.
2. `tools/cut_cp_tree.py art/gen/renders/cp_oak_r2a_grid4.png cp_oak --leaf 8 --bark 5 --rim-lum 60 --mode 1`
   (k-means ramps, one majority pass, the new cut's clean pass: holes, specks, lone pixels, blotches).
3. `tools/polish_cp_trees.py cp_oak`: 125 glints, 77 spikes, and the new `fringe` rule (35 violet magenta-fringe
   pixels on the trunk's left edge take their neighbours' colour).
4. `tools/fix_cp_oak_r4.py` (rules, every pixel in `art/source/cp_oak/edits.json` under r4, r4b, r4c, r4d):
   r4 the leaf highlight #fc9e1e (luma 172, 185 on screen) takes the lime's #f68a21 (158); r4b five highlight
   patches join their clump; r4c the bark's four darks within 20 luma become two (mottled at 5x), leaf reds on the
   trunk take bark shades; r4d asset_qa's blotches after that join their fill.
The old round (NB 2.1 render, 388 x 343) is kept in `art/source/cp_oak/r1_nb21/`.

## Measures (`art/gen/out/cp_oak.cut.json`)
506 x 511, 10 colours, top cut by the frame (y0 far above the world), sides not cut. Trunk 97 px at 20 up (root
flare), 68 at 50, 60 at 80, 58 at 110, 52 at 140 (spec 46: wider, as the lime; the asset is at 3 paid jobs, so this
is an owner question). Lowest leaves about 150 px up. On screen (fade 0.28 + look): p10 119, median 141, p90 177;
highlight about 176, under the tree line median 181 and the far city 190.

## Checklist (art/gen/reviews/cp_oak.md items), maker's own look, for the independent reviewer
1 scale: trunk above (owner question). 2 layer: back p10 119 >= 80, highlight 176 on screen. 3 outline: no ink ring,
darkest #412c2b (luma 50) is bark shade inside the furrows; asset_qa outline 27 % (no decor-ink warning).
4 shapes: no loose limb bits seen at 5x; crown sides round, no flat cut. 5 shading (round 3 FAIL, leaf patchwork):
clumps are drawn as clumps in the render itself, each with a lit top (#f68a21), mid (#f47815, #f26513), shade
(#d43918) and the gap rust (#813032); no 3-tone mottle, asset_qa blotches 0, lone 0.3 %. 6 palette 10 colours.
7 view front-on. 8 fit: in the frames it sits with the lime (x 1528) and the ash (x 1916). 9 read: an autumn oak.
My eye at 5x beside bench, bin and lamp: clumps crisp, trunk bark in clean vertical furrows; flatter than the bench.

## Files
- `cards/PASS_cp_oak.png` (asset_qa PASS, fade 0.28, slot 506 x 511)
- `frames/sweep_citypark_y{000,024,144}_x{1280,1600,1920}.png` (screens 5-7, high and low camera)
- `screens_5_7_colour.png`, `screens_5_7_grey.png` (the nine frames, 1x)

## Checks
PEPPER UNCHANGED (4591 steps), flow 125/125, Tiled PASS, BACKDROP OK, `--physics` citypark_tall 97/97.
