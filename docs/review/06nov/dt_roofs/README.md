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
