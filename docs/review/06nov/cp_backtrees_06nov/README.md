# City Park back and far trees, triage (6 Nov 2026, branch art/cp-backtrees-06nov)

Frames: `sweep_citypark_y{024,144}_x{0640,0960}.png` (City Park tall, screen 3, the pond and the willows).

| Piece | Size | Layer | asset_qa | Verdict |
| --- | --- | --- | --- | --- |
| park_willow | 65x84 | back | WARN lone 3.8 %, 2 blotches, 3 pinholes | FAIL on scale: 1.8 m on the 46 px/m line, reads as a bush beside Pepper (0.8 m) under the treetop walk |
| park_willow_tall | 65x92 | back | WARN lone 3.9 %, 3 pinholes | FAIL on scale: 2.0 m |
| park_treeline | 480x31 | shore | WARN noise 0.4 %, 16 blotches | kept: far layer, tier C (never generated, rules.json); reads as a far row of round trees in the frames. Its scale (31 px at 12-14 px/m, about 2.4 m) is a note for the owner; a remake would be built in code, not by SpriteCook |

## Willow remake: prepared, not run (paid calls held by the producer, 6 Nov 19:10)
`art/gen/jobs/cp_willow.json`, `art/gen/blockouts/cp_willow.py`: one weeping willow at true scale (trunk 0.6 m,
crown 7 m = 322 px, curtain to 55 px above the ground, top above the screen) in place of the three small ones, the
cp_lime method (GPT 2.5 Sunburst 2K, refs: blockout, rw_lime 4x, cp_lime 4x). Preflight dry pass: 76 credits.
Pepper 52 x 38 in the blockout. Wiring needs a scene.lua change (the WILLOWS draw: one tree art on the middle crown,
the side crowns skipped, as TREE_ART does for the oak).
