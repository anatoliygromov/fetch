# City Park climbing parts, 6 Nov 2026 (branch art/cp-boughs-06nov, family cp_boughs_06nov)

The tall City Park's oak climbing parts were drawn in code (scene.lua drawBranch, drawFork, tipTwig, drawLowBough, the
blob leaf mass, drawNest, drawTrunk, the STUMP). The owner rejected code-drawn organic shapes as "lifeless". They are
now art from one SpriteCook parts sheet, stamped over exactly the same boxes. Nothing Pepper stands on moved: a limb's
top row is its ledge's top row, the low bough's level part is its 32 x 16 box, the stump its 24 x 28 box.

## How it was made
- One render: GPT 2.5 Sunburst 2K, 2 variants, the 512 blockout `art/gen/blockouts/cp_boughs.py` (Pepper at 1x, every
  part at 46 px/m) as the edit image and the approved cp_lime at 4x as style. 60 credits (ledger cp_boughs@1106-185013).
  Variant a used (b: the fork drew a sawn ring, the nest a stiff twig cradle).
- Cut 1:1 on the render's 4 px grid (`tools/grid4_cut.py`, 91 % clean cells, Pepper 38 px tall in the blockout and in
  the cut), colours per material by k-means (`tools/cut_cp_boughs.py`), then parts by rule (`tools/build_cp_boughs.py`,
  every rule counted in `art/source/cp_boughs/edits.json`): the lime's leaf and bark ramps, leaf specks on bark merged,
  limb columns moved whole so the top is one straight row and bodies over 8 px lose middle rows, the low bough's level
  part 16 rows, 1 px ink on the play pieces, a clean pass on this new cut, decoration edges without ink (lit edges the
  mid bark shade). No resampling anywhere. Sources: `art/source/cp_boughs/*.aseprite`.
- scene.lua stamps them: a ledge is whole columns of the limb (its tip at the free end, mirrored for a left tip, the
  middle repeated when a span is longer than the art), a fork two limbs from the trunk's middle, a branch's dip into
  its trunk the same columns stepped down. A small faded clump (one of three, by place) sits on each twig. The code
  drawing stays as the fallback when a file is missing (`cpb()`).

## Pieces
| Piece | File | Size | Layer | asset_qa | Card |
| --- | --- | --- | --- | --- | --- |
| thin limb (all ledges except the oaks') | cp_bough_limb.png | 249x37 | play, ink | PASS | cards/PASS_cp_bough_limb.png |
| thick limb (old oak and big oak ledges) | cp_bough_limbx.png | 336x37 | play, ink | PASS | cards/PASS_cp_bough_limbx.png |
| low bough | cp_bough_low.png | 106x70 | play, ink | PASS | cards/PASS_cp_bough_low.png |
| its leaf mass | cp_bough_low_leaves.png | 106x70 | decoration, unfaded (as before) | WARN decor-ink 47 % | cards/WARN_cp_bough_low_leaves.png |
| tip clumps (3 of the 9 used) | cp_bough_clumps.png | 272x35 | decoration, back fade | WARN decor-ink 30 % | cards/WARN_cp_bough_clumps.png |
| magpie's nest | cp_bough_nest.png | 42x19 | decoration, unfaded (as before) | WARN stray 3.5 % | cards/WARN_cp_bough_nest.png |
| stump | cp_bough_stump.png | 32x30 | play, ink | PASS | cards/PASS_cp_bough_stump.png |
| big oak trunk (32 px box) | cp_bough_trunk.png | 57x357 | decoration, back fade | WARN decor-ink 47 % | cards/WARN_cp_bough_trunk.png |
| small trunks (8-12 px boxes) | cp_bough_trunk9.png, cp_bough_trunk10.png | 21x140, 20x140 | decoration, back fade | WARN decor-ink 46 / 44 % | cards/WARN_cp_bough_trunk9.png, cards/WARN_cp_bough_trunk10.png |

decor-ink warnings are the bark ramp's own dark shade on the shaded edges, as cp_lime (52 %) and cp_ash.

## For the reviewer
- Frames: `frames/before_*` (the code drawing, base dff15cf) and `frames/after_*`, 1x, at y 0/24/144 and x 100, 1120,
  2100, 2560; side by side at 2x in `before_after_2x.png`.
- The limbs are 8 px of bark over the 6 px box (the render drew them 8-10 px; middle rows dropped), so they hang 2 px
  lower than the box. Their top row is the ledge.
- Trunks with tree art (cp_oak, cp_lime, cp_ash) and canopies under CANOPY_SKIP are not drawn, as before.
- The big oak's trunk (57 wide with its root flare) is 33 px at its middle for a 32 px box; small trunks are 9 or 10 px
  for 8, 10 and 12 px boxes (decoration; the fork ledges centre on the box).
- Known: a lit orange patch where the low bough meets its leaves; the limbs' broken twig ends under the small clumps.

## Checks (this branch)
See the CHANGELOG entry: check_pepper, check_flow, check_tiled, check_backdrop, `--physics` 97/97, `--auto`, `--test`,
`--qa` on citypark_tall.
