# City Park (tall): built pieces and hand fix (art/cp-built-06nov, 6 Nov 2026, 0 credits)

Track 3 of the 6 Nov evening run. Everything here is built by rule in Python (`tools/build_cp_built.py`) or fixed by
hand rule (`tools/fix_cp_winch.py`). No SpriteCook, no Artlist, no automated clean pass. Each repeated part (brick,
iron bar, rosette, plank end, bolt, rail post, rope twist, leg, knee brace, rose, chain link) is drawn once and
stamped on an integer grid. Sources: `art/source/<name>/` (.aseprite via `tools/aseprite_io.py`, png, old files kept).

Frames: `tools/cp_built_frames.sh OUT LEVEL XS YS` (look on, no HUD, 1x, with a greyscale copy). Cards:
`tools/qa_card.py out/qa_cp_built.json` with the frames below. Every card is PASS.

| Piece | Files | Layer | Method | asset_qa | Frame |
| --- | --- | --- | --- | --- | --- |
| Park gate (board: redraw) | park_gate.png 120 x 96 | back, faded 28 % (its own amount, unchanged) | built | PASS | frames/gate.png (camera y 144 and 24) |
| Winch keeper (board: fix) | park_keeper_winch.png 640 x 80 | back, faded 35 % | hand fix by rule, 32 px in edits.json | PASS (was WARN frames) | frames/winch.png |
| Swings (triage: WARN, mottled) | park_swings.png 84 x 106 | back | built | PASS (was WARN) | frames/swings.png (y 144 and 24) |
| Treetop walk | cp_walk704_deck 242 x 8, _rail 240 x 45, _legs 240 x 162 | deck play; rail decoration; legs back, faded | built | PASS x3 | frames/treetop_walk.png (y 24 and 144) |
| Alder walk | cp_walk1968_deck 346 x 8, _rail 344 x 45, _legs 344 x 178 | as above | built | PASS x3 | frames/alder_walk.png (y 24 at x 1960, y 144 at x 2100) |
| Rose arbour | cp_arbour_slat56, cp_arbour_slat48 (used twice), cp_arbour_posts56x106, 48x122, 48x106 | slats play; posts back, faded | built | PASS x5 | frames/arbour.png (y 24 and 144) |
| Play tower | cp_tower_deck56 (used twice), cp_tower_post4x72, cp_tower_post4x106 | play, outlined | built | PASS x3 | frames/play_tower.png (y 24 and 0) |
| Slide (triage) | park_slide.png 66 x 63 | ground | kept as is | PASS | frames/playground.png |
| Climbing frame (triage) | park_frame.png 90 x 67 | play | kept as is | PASS | frames/playground.png |

Not done here, as briefed: **park_keeper_cart** has a board fix call (dirt pixels), but it is not in the 6 Nov
measured draw list of City Park tall, so it is left as is. A finding from reading the code: `stage.lua` draws every
`bikes` entry of an art level with `Sc.drawHazardArt`, which for the park is `keeperCart` (park_keeper_cart.png), and
citypark_tall has two cart zones (x 1376-1560 and 2350-2576, "CART! GET UP HIGH!"). The look sweep clears the bikes
(`s.bikes = {}`), which may be why the measurement missed it. Worth a check by the producer before the board.

## What each piece is

- **Park gate.** True scale: two brick piers 2.1 m with the ball (30 px wide, shaft 26 px, courses 4 px, bricks 11 + 1
  in stretcher bond, every third brick the second shade on a fixed pattern), a granite plinth, a sandstone cap and
  ball. A wrought iron double gate between them, 1.3 m opening, leaves 1.6 m to the spear tips, painted the approved
  bench's green: the left leaf shut (bars on a 4 px pitch, three rails, dog bars, a frieze of rosettes), the right leaf
  open and seen edge-on against its pier, so Pepper has come in through it. Decoration: no outline (the old file had
  a baked dark outline, decision 8 a skipped it for that reason; now 26 % dark edge, no decor-ink warning). Same
  anchor as before (x 0, bottom on the back props line), only wider (59 to 120 px).
- **Winch keeper.** The coat's deepest green #101a10 came and went between frames (none in frame 3) and a near ink
  #312f2a sat in frames 4 and 5 only. Rule per pixel: at the silhouette to the ink, inside the coat to the coat's dark,
  else to the nearest 4-neighbour colour. Now all 14 colours are in all 8 frames. Every pixel in
  `art/source/park_keeper_winch/edits.json`.
- **Plank walks.** Deck exactly the box plus the 1 px ink outline: the planks' lit top edge (the thin cap), plank ends
  7 px with a 1 x 2 joint on a pitch of 8, their shadow, a stringer with a bolt over every post. The rope rail 1 m
  (46 px) high on 4 px posts at an even pitch end to end (46 px on the treetop walk, 42 px on the alder walk), a hand
  rope and a lower rope, each sagging 3 px, a 3 px twist counted from each span so every span is pixel-identical
  (checked), a whipping over each post. Legs 6 px under every post, knee braces 1:1, one tie 40 px down; wet legs go to
  the bed with the water's colour over them, as before. The posts and legs line up, so the walk reads as built.
- **Rose arbour.** White painted slats (play, outlined). Two 5 px posts per slat with a climbing rose that winds across
  the front every 12 px, leaf pairs where it turns, a 4 x 4 coral rose drawn once (mirrored on the right side), and a
  swag of roses under the slat. The post image is 6 px wider each side for the leaves and roses.
- **Play tower.** The slide's yellow and greys: decks with a bolt at each end, posts with ink sides, all outlined.
- **Swings.** A green steel frame (the bench's green) 2.3 m to the beam's top, legs splayed 1 in 8 on straight
  stairs, two yellow seats 0.45 m off the ground on grey chains (2 px links). Replaces a mottled rust render with
  holes (noise, stray 4.2 %, blotches, pinholes).

## Wiring (scene.lua, nothing Pepper stands on moved)

`riverwalk/cp_built.lua` (written by the builder) lists each image with the box it was built for. scene.lua `built()`
draws the image only when the prop's box is that box and the file is there; otherwise the old code drawing runs
(drawWalk, drawWalkLegs, drawSlat, drawSlatPosts, drawDeck, drawTowerPost keep their code as the fallback). The gate,
swings and winch keeper are the same slots as before. No level data touched.

## Colours

Timber, rope, white paint, rose, leaf, yellow, greys, brick and granite from palette v1 (`art/palettes/citypark.gpl`)
or from the approved bench and the park's own slide. One new ramp: the sandstone of the gate's cap and ball (#cfc19d,
#a79b6f, #7a6c48, the winch keeper's khaki, already drawn in the park but not in palette v1). It counts only with the
owner's approve.

## Checks on the branch

PEPPER UNCHANGED (4591 steps); flow 125/125 (with its own save folder); TILED CHECK PASSED; BACKDROP OK; `--physics`
citypark_tall 97/97, riverwalk 55/55. asset_qa --all: every piece of this track PASS; the library's 6 FAILs are the old
ones (building, cafe, gable, rail_bg_left, town_bollard, park_leaves_flat).

Before and after (preview/05nov-night left, this branch right, 3x): `frames/before_after_*_3x.png`.
