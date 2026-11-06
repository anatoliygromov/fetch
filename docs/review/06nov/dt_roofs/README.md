# Downtown roof kit, far spire, code-drawn pieces and fountain (art/dt-roofs-06nov, 6 Nov 2026)

Built from parts drawn once and stamped on integer grids. 0 SpriteCook credits, 0 Artlist. Every colour is from
`art/palettes/downtown.gpl`: the sample screen's ink (18, 18, 26), granite (135 / 110 / 77, recess 58 / 42), steel,
oak and its reds and greens. Scripts: `tools/build_roof_kit.py`, `tools/build_spire.py`, `tools/build_dt_details.py`
(each `--check`). Sources: `art/source/dt_roofs/*.aseprite`. Hooks: `docs/art_hooks_r8.md` (last section).

Why: the roof kit (23 Oct build) was light stone (median 147 on screen, highlights 228) against the 5 Nov sample
screen's darker street (houses 145 to 152, play perches 103 to 137), so the galleries and loggia needed a draw-time
tint and the ledges read as pale shelves. The fountain's tier, bowl and rim were lighter than the walls behind them
(152 to 157) and the bowl and rim had speckled stone. The balconies, the springy coil, the stop sign and the fountain's
jets were drawn in code (the jets as single translucent drops that read as specks).

| Piece | File, size | Layer | What it is now | asset_qa |
| --- | --- | --- | --- | --- |
| loggia | town_roof_loggia.png 122 x 26 | play | cornice, dentil course, five round arches on a 24 px pitch, sill | PASS |
| galleries | town_roof_gallery88 / 72.png 90 / 74 x 32 | play | handrail, vase balusters (8 x 20, one part) on a 10 px pitch, plinth, end pedestals | PASS |
| flower roof | town_roof_flower_roof.png 90 x 14 | play | ledge with five terracotta boxes of geraniums (no lone pixels) | PASS |
| ledge | town_roof_ledge.png 16 x 9 | play | 3-slice slab, one modillion per 8 px tile | PASS |
| footbridge | town_footbridge.png 162 x 52 | play | iron railing (posts on the deck joints), oak deck, iron arch with hangers | PASS |
| far spire | spire_riddarholmen.png 36 x 260 | shore (0.70) | silhouette: flat brick tower, louvres, lattice spire; 8 colours, no ink edge, no pinholes | PASS |
| balconies | town_balcony56 / 64.png 58 / 66 x 57 | play | 1 m iron railing (3 px bars on an 8 px pitch, ring frieze), granite slab, two corbels | PASS |
| springy coil | town_spring.png 36 x 10 (4 frames) | play | red coil for heights 7 to 10 (squash) | WARN (frames: bottom row moves by design) |
| tram stop sign | town_stopsign.png 19 x 101 | back (faded) | true scale 2.2 m: steel pole, 19 px green ring, white disc, tram pictogram, no text | PASS |
| fountain jets | town_jet.png 24 x 88 (4 frames) | back look, unfaded | a 2 px stream curling off each tier lip, dashes running down, a splash in the pool | PASS |
| fountain | town_tier 50 x 58, town_bowl 34 x 82, town_rim 18 x 18 | play | same silhouettes and hit boxes, coursed granite, no speckles | PASS |

Code (fallbacks kept: delete a file and the old drawing comes back): `scene.lua` drawBalcony, `Sc.spring`, `Sc.townJet`
in drawTerrainArt; `arthooks.lua` stopSign, `H.STONE_TINT` emptied. Registry: `tools/measure_layers.py` and
`tools/asset_qa.py` SLOTS and FRAMES now list the in-game names (the spire at the shore's 0.70, as the game fades it).

Folders: `cards/` (qa_card.py, colour and grey frames, 5x beside bench, bin, lamp), `frames/` (after, look sweep at
camera y 120 and 240), `before/` (the same spots on the base), `sheets/` (5x before and after), `qa.json`.

Card notes for the reviewer: the stop sign sits under the shelter roof and behind its glass (shelter drawn after it);
the coil WARN is the squash (frames of 7 to 10 rows); the flower boxes' blooms cover the ledge's face rows 2 to 5 (never
its top row).

## Fix round 1 (review art/gen/reviews/dt_roofs.md, 11 of 15 PASS)

| Finding | Change |
| --- | --- |
| town_roof_gallery72 Shapes: a 10 px pitch left 1-3 px slivers at the ends | Both galleries: pedestals 10, vase balusters 10 x 20 (one part), a 16 px pitch, every gap 6 px at the belly, the end gaps included (90 = 2 x 10 + 4 x 16 + 6; 74 = 2 x 10 + 3 x 16 + 6). gallery88 changed with it (its WARN was the same end gaps), so it goes back to review too |
| town_balcony56 / 64 Read: a wall of bars, a birdcage | An open railing: a thick handrail, a bottom rail, four posts, one iron ring (12 x 12, drawn once) on a short bar in each of three panels; the wall reads through. The slab is 8 rows, the corbels stepped. 58 / 66 x 60 (was 57) |
| town_spring Outline and Read: open at the bottom, a red tassel | A grey steel coil: three turns (a lit wire row over a narrower dark row, so the silhouette steps like a spring), closed end plates, ink all round in every frame (h 7 to 10) |

Pipeline: all 15 specs in `art/gen/jobs/` (family dt_roofs, tier C), spec, built and ingame done; review done for the 10
unchanged PASS pieces (the reviewer's sections split into `art/gen/reviews/NAME.md`, text unchanged, one item per line).
Waiting for review: gallery88, gallery72, balcony56, balcony64, spring.

## Fix round 2 (review round 2: galleries and spring PASS; balconies FAIL on item 9, bones caged)

The railing (rows 0-45) is drawn in the back pass (`Sc.drawBalconyRails`, stage.lua after the back props), so the
bones, Pepper and Mia are always in front of it; the slab and corbels stay on her line (drawBalcony). The middle
posts and the rings' bars stop at a mid rail (rows 29-32); below it only the end posts run to the bottom rail, so the
bones (rows 33-43 at 1x with their bob) float in a clear band at every balcony (x 1580, 1684, 1868, 2436, 2460, 1360).
No bone or box moved. Frames: `frames_r2/` (y 120, x 1440, 1500, 1640, 2380, 1180, colour and grey).
