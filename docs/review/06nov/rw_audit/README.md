# River Walk audit fixes, 6 Nov 2026 (branch art/rw-audit-06nov, 0 credits)

Audit: items 2, 7, 10, 13 (bones) and 15 (bones) of the River Walk weirdness audit. The road, quay joins, bridge
passage, front clumps and railing ends are another track. Frames: the look sweep (camera y 0, step 160), 1x shown
at 3x, before on the left, after on the right, colour and grey. Rules: `tools/fix_rw_audit_06nov.py`, every pixel in
`art/source/NAME/edits.json` under `06nov_audit`.

| Piece | File, size | Layer | Method | asset_qa | Frames |
| --- | --- | --- | --- | --- | --- |
| grit box | gritbox_front.png 88x32 (same slot, same box) | play | built by rule | PASS | x0640, x0800, x3040, x3200 |
| pontoon | pontoon.png 54x19 (was 54x12; deck at the same y) | play | built by rule; mooring and ripple in code (setpieces.lua) | PASS | x1280, pontoon_pepper_on_it |
| kennel | kennel.png 34x36 | play | hand fix by rule | PASS | x0000 |
| bone, bone_gold | 11x6 | char | hand fix by rule | PASS | bones_all_4x_1/2 (every bone, before and after) |

- **Grit box:** was a green chest with a 3/4 side face, the kiosk's green. Now front-on: a pine box, a lid board 2 px
  wider than the body each side, three planks, an end batten each side with a nail per plank, an iron hasp. 7 colours,
  1 px ink outline.
- **Pontoon:** was a grey slab on two stubs, its 1 px line ran from a post at the quay's end to a post in open water.
  Now a mahogany deck (the ferry's ramp) on two floats; the river's line (y 224) crosses the floats, the part under it
  is water-dark, a light ripple each side. A horn cleat on each end of the deck: one line to a cleat on the quay's
  end, one to a timber pile in the river by the ferry's bow (lashed, ripple round it). Drawn at y0 - 5 (cleats above
  the deck), so the deck top stays at y 212 and her box (214) is unchanged.
- **Kennel (the red and black box):** Pepper's kennel, a code piece with art. Its white corner trim (2 px inside the
  ink, both sides, full height) read as a white halo. The trim takes the falu red planks of its row, so the only edge
  is the 1 px dark ink (obstacle rule). The doorway's top corners are rounded into an arch.
- **Bones:** every bone is drawn after every play prop already (stage.lua: props, then bones). They looked inside the
  flowers because the outline was open over and under the shaft, so petals and cobbles showed through. The outline is
  closed (6 px) and one step darker (#3a2c1e, gold #4a2e0c). All 63 bones checked in the collage: each reads on cobbles,
  daisies, bushes, water, the bench and the bridge's shadow. Left as is: the gold bone inside the kennel stays hidden
  by the kennel (the level's secret); the City Park leaf piles draw over bones on purpose. No bone moved.

My eye at 5x beside bench, bin and lamp (`pieces_5x_cobble.png`, `pieces_5x_water.png`): the box reads as a lidded
wooden box, apart from the kiosk; the pontoon as a raft on floats tied at both ends; the kennel as a red dog house;
the bones as bones. As crisp as the bench.

Checks: PEPPER UNCHANGED, flow 125/125 (own save folder), Tiled PASSED, BACKDROP OK, riverwalk `--physics` 55/55,
`--auto` GOOD GIRL (bones 55/63, 66 s).
