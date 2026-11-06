# cp_critters (6 Nov): the City Park magpie, the duck boat, the goose triage

Branch `art/cp-critters-06nov` (off `preview/05nov-night`). Run: owner 6 Nov 18:45 "All 3 levels now, up to 2,000".
SpriteCook: 62 credits in 4 jobs (ledger rows match the charges). Paid calls stopped on the producer's order at
about 19:10; everything after that was 0 credits.

| Piece | File | Size | Layer | Method | Credits | asset_qa | Card |
| --- | --- | --- | --- | --- | --- | --- | --- |
| magpie | riverwalk/art/magpie.png | 5 cells of 32 x 26 (bird 30 x 18 perched, 30 x 22 flying) | char (no look shader, 1 px ink) | SpriteCook Pixel Engine Image at game size (perched, flying), pixel-engine-v1.5 wingbeat; `tools/build_magpie.py` (palette, tail flick and wings-level frame by rule, wings-down frame from the animation) | 12 + 12 + 26 | WARN (size jump perch to wings up: expected) | WARN_magpie.png, magpie_row1.gif |
| duck boat | riverwalk/art/scene/cp_duckboat.png | 92 x 60 (2.0 m) | play (1 px ink) | SpriteCook Pixel Engine Image at game size; `tools/build_duckboat.py` (the inside and far rim taken out: front-on, the gunwale is the deck) | 12 | PASS | PASS_cp_duckboat.png |
| goose | riverwalk/art/goose.png | 272 x 102 (34 x 34 cells) | char | kept as is (triage) | 0 | WARN | WARN_goose.png |

## Sizes
- `magpie_sizes_4x.png`: options A 24 px (the code magpie), B 30 px, C 36 px beak to tail, beside Pepper, the cat
  (32 px sitting) and the gull (34 px span, about 32 px long) of art/animals-r2. **Picked B (30 px)**: next to the gull's
  32 px body it reads as the slightly smaller bird it is, and next to Pepper (38 px tall) it is clearly a small bird
  that still carries the 6 px ball. A true-scale magpie would be 21 px (0.45 m at 46 px/m). This is the agent's pick
  per the brief, not the owner's: the job's owner_size says so.
- `size_sheet.png` (producer's ask): the finished magpie, perched and flying, and the duck boat with Pepper on its
  deck, beside Pepper's real sprite at 4x and 1x.

## Magpie
- Frames: 1 perch, 2 tail flick (the perched tail mirrored up behind the wing tips), 3 wings up, 4 wings level, 5
  wings down. Flying it loops 3 4 5 4 at 12 fps; perched it flicks as the code magpie did.
- scene.lua `Sc.magpie`: the art when `art/magpie.png` exists (feet at cell 20, 25, mirrored when it faces left);
  the code magpie (MAGPIE rows) stays as the fallback. `Sc.magpieBeak` / stage.lua `St:beak()`: the ball's near edge
  on the beak tip, its top on the beak row (perched x+12 / x-11, y-9; flying y-6); the old offsets without the art.
- 9 colours, one ink #000000, closed outline. Every changed pixel against the 1:1 sources: art/source/cp_magpie/edits.json.
- In game: `frame_magpie_perch.png` (perch 1, facing Pepper, ball in the beak), `frame_magpie_fly.png` (flying to perch 2).

## Duck boat
- True scale: 2.0 m = 92 px. Its gunwale (row 41, the ink) is the deck on the mover's top (y 346); the pond's surface
  is 7 px under it, on the red stripe. The tall City Park's DUCK BOAT mover is now 80 px wide (the hull's cols 8-87;
  was 48), x 826, travel 30 px (was 64), rope and call zone unchanged on screen (816-944, 600-830): a 92 px boat
  fits the 128 px pond only this way. Same 8 px gaps to the stone and the bank as before.
  Map: maps/citypark_tall.tmx and its export. The flat City Park keeps park_boat_front.png (its 48 px box).
- scene.lua `Sc.drawMoverArt`: the new art on a box 78 px or wider, mirrored about the box when it paddles right.
- Note for the review: the flat deck between the neck and the seat is 31 px; Pepper (52 px) standing at the front
  end of the box is drawn over the duck's breast (`frame_duckboat.png`); before: `frame_duckboat_before.png`.
- 19 colours. Edits: art/source/cp_duckboat/edits.json.

## Goose (triage)
asset_qa WARN (lone pixels 3.5 %, 13 small blotches, fly row size jumps). In game (`frame_goose.png`) it is about
28 px tall beside Pepper, crisp, outlined, cute. The walk and hiss rows are clean at 5x; fly row frames 2 and 4 are
rough. Not a FAIL, so it is kept (brief: remake only on a fail).

## Checks
`--level citypark_tall --physics` 97/97, `--level citypark --physics` 85/85, `--level citypark_tall --auto` GOOD GIRL
(the magpie drops the ball, 39.1 s), PEPPER UNCHANGED, flow 125/125 (with its own save folder; a first run on the
shared save folder stuck in the level select), TILED CHECK PASSED (the map change re-exported), BACKDROP OK.
