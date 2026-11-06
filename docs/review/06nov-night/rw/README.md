# River Walk track, night of 6 Nov 2026 (branch `night/06nov-rw`)

Base: `night/06nov-concepts`, with `art/rw-ground-06nov` and `art/rw-audit-06nov` merged (producer's order).
Credits: SpriteCook 64 (the rower, job db5f2e89, run by the producer). Nothing else spent.

## 1 The rowing boat, rebuilt by parts

Owner, 6 Nov: the old boat was "still ridiculously small" (hull 60 px, child-sized rower); the r2 SpriteCook boat
was "really terrible". Nothing of r2 is used. Design target: concept b (`art/gen/concepts/rw_rowboat_concept_b.png`).

| Part | How | File | Numbers |
| --- | --- | --- | --- |
| Hull | built by rule, `tools/build_rw_rowboat.py --check` | `riverwalk/art/scene/rw_rowboat.png` | 185 x 62 (4.0 m eka at 46 px/m); bow +12 px in runs 1,1,2,2,2,3,3,4,5,6,8,11, transom +5 px; 2 px rail, white strake, a honey top plank and mahogany planks under it, each seam its own curve fanning into the stem; asset_qa PASS |
| Rower | SpriteCook GPT 2.5, variant a, cut 1:1, arms re-keyed | `art/source/rw_rower/` | cut 40 x 46, cap top 2 px under Pepper's head on the deck; face 12 px; 19 colours |
| Oar + loop | built per frame by rule | `riverwalk/art/scene/rw_rower.png` | 6 frames of 78 x 62 on hull x 106-183: catch, drive, drive, finish, return, return; ash oar pivoting on the rowlock at hull x 150, handle 16 px, blade end 48 px, blade tipped 7 degrees on the return (clear of the water); lean -2/+1 px |
| Water | code, `Sp.drawRowboat` | `riverwalk/setpieces.lua` | tint under y 224 on the hull's own columns, 2 ripple rows, a wake, splash at catch and finish |

- The fists are stamped from the render on the oar handle in every frame; the near arm is two bones (9 + 15 px)
  from his shoulder to the wrist, the elbow always bent down, in his own sleeve colours with a highlight row, so
  arm, hands and oar always connect.
- He rows from the stern thwart (fix round 1): Pepper's spot amidships stays clear of him. The deck box and the
  route are unchanged; the autopilot rides at box + 60, walks to the stern to jump onto the jetty, and on boat 2
  jumps over him onto the far quay.
- He faces the bow, as in concept b. Pulling moves the boat right (towards the jetty and the far quay); going back
  left the loop plays backwards. At rest the blade is lifted.
- The rower cut is SpriteCook's own pixel output. `grid_cut.py` on the raw 1024 render found only 67 % clean cells
  and dropped the fists (they reach past the blockout), so it was not used.
- asset_qa: rw_rower WARN (3.3 % lone pixels, the eye, nose and beard; 0.5 % noise; the blade's lowest pixel moves,
  as it should). Card: `cards/WARN_rw_rower.png`, its loop `cards/rw_rower_row1.gif`. Hull: `cards/PASS_rw_rowboat.png`.
- In motion, from the autopilot's run: `frames/harbour_ride_autopilot.gif`.

**One change from the agreed spec:** the gunwale is at y 212 and Pepper stands on it (the spec had the gunwale at
208 and her deck 4 px below it, inside the boat). With the hull behind her she would have stood on the boat's side
in front of the rail, and the hull in front of her would cover her paws (not allowed). The duck boat does the same
(deck = gunwale). Freeboard 12 px (0.26 m) amidships; she still walks on from the quay (4 px up).

## 2 The harbour: 208 px wider

- Water x 2192-2848 (was 2192-2640). The level is 4048 px. `tools/shift_level.py riverwalk 2640 208`, then the
  harbour by hand; tests and the autopilot updated; Tiled map and export regenerated (now identical to the level).
- Why 208 and not 352 (preview/06nov): the 4 m boat is 185 px (that one was 239). Water = 423 + 2 x the row, so
  208 gives each boat a 116 px row (about 4 s). Wider only makes the waits longer for a 7 year old.
- Pepper's box on the hull: columns 25-178 (154 px), where the rail is within 4 px of her deck.
- Boat 1: bow at the quay (2193) to stern at the jetty (2494). Jetty 2496-2544 (top y 196, a hop from the deck).
  Boat 2: bow at the jetty (2545) to stern at the far quay (2847). Bones over the boats at y 178 (above his cap).
- Frames: `before_after_harbour_quay_*.png`, `_jetty_*`, `_far_quay_*` (left before, right after, 2x).

## 3 The other River Walk gaps

| Item | Result | Frames |
| --- | --- | --- |
| Pier at x 1920, navy band | already a stone arch on jambs (merged rw-ground) | `before_after_pier_*` |
| Jetty piles like table legs (audit 2) | piles run on into the water, tinted, ripple round each | `frames/` harbour |
| Kennel reads as a post box (audit 3) | rebuilt by rule 44 x 44, pitched roof, arched door, `tools/build_rw_kennel.py`; start x 62 | `before_after_kennel_*`, `cards/PASS_kennel.png` |
| Pontoon: taut rope, no waterline (audit 4) | floats and the timber mooring pile tinted under the surface, lines sag 2-6 px | `before_after_pontoon_*` |
| Road band (audit 1) | rebuilt by rw-ground; fix round 1: one palette step darker (asphalt 74, 78, 86; drawn median 88 to 74 on my measure), dashes and kerb kept | `before_after_road_*` |
| Grit boxes (audit 5) | already a wooden chest with a lid and hasp (rw-audit) | |
| Knocked ball on a boat | a knock's flight never lands on a mover now (stage.lua `St:ballLands`) | |

## 4 Checks (all on this branch)

- `check_pepper.sh`: PEPPER UNCHANGED, 3908 steps (golden trace re-recorded: the harbour, the kennel's start, the
  autopilot's riding spot; `check_pepper_lab.sh` 1401 lab steps identical, Pepper's files unchanged).
- River Walk `--physics` 55/55; City Park tall 97/97; Downtown tall 102/102; autopilot GOOD GIRL in 54.9 s.
- `check_tiled.sh` PASSED; `check_backdrop.py` OK; `check_flow.sh` 125/125.
- `check_curve.py` (6 levels, 10 seeds): T1-T4 PASS; River Walk kids 8.5, parents 10.9, Elsa 100 %, 0 % lost.
- `measure_layers.py --ladder`: River Walk play median 117 (was 99, the honey hull), back 170. The "shore > back
  median" note is in the base already (the light house fronts).
- The independent review (gate 8) is the producer's: `art/gen/reviews/` is left empty.

## 5 Questions for the owner

1. **Gull size** (`size_sheets/gull_sizes_4x.png`): span A 16, B 20 or C 24 px? (now 22 x 16).
2. **Cat size** (`size_sheets/cat_sizes_4x.png`): sitting A 24, B 27, C 30 or D 34 px? (now 30; Pepper 38).
(Settled in review round 1: Pepper stays on the gunwale; the road one step darker, not to 40.)

## 6 Fix round 1 (review 4384ff9)

Arm with an elbow and a highlight row; the blade lifted on the return and at rest; the lower planks mahogany and
the oar ash; the bow's seams as separate smooth curves; the rower at the stern, Pepper's spot clear; the road one
step darker; the mooring pile wet; the concept PNGs committed. Frames: `frames/after_ride_boat1_right.png`,
`after_jetty_boat1_back_left.png` (boat 1 rowing back left on its own), `after_ride_boat2_right.png`, the GIF.
