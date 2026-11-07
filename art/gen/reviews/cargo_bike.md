# Gate 8 review: cargo_bike (the baker)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-chars at fec05c6, worktree review-chars07. Independent gate 8 reviewer; I did not make the art. Looked at every frame at 5x, the leg region at 8x, the still at 5x beside the bench and bin, and in Downtown tall at 1x, 2x and 5x crops (my own LOOK_CARGO shots at Pepper x 2040 and 3250, the bike at several offsets up to the depot line), colour and greyscale. Shoe and trouser colours measured. Maker's notes read after.

Piece: riverwalk/art/scene/cargo_bike.png 116 x 88 and cargo_bike_pedal.png (8 frames of 116 x 88, frame 1 is the still). Facing left, rides right to left in Downtown's two cargo zones (arthooks.lua H.drawCargo).

Owner's checks at 5x, every frame (he reported the body detached, no arm to the bars, legs off the pedals, sitting backwards):
- Seated on the saddle: PASS. The hip sits on the seat tube's top in every frame, the body does not move between frames; the saddle itself is hidden behind the thigh, which is fine.
- Hands on the grips: PASS. One arm from the shoulder to the bar end; the hand closes on the grip (about x 36-40, y 40-42 at 1x) in all 8 frames.
- Feet on the pedals: PASS at 5x. The near shoe (35,41,42) sits on a grey pedal in every frame; both shoes show in frames 2-8 at opposite phases.
- Facing the direction of travel: PASS. Face, beard and helmet point left, the box is in front, the bike rides left in the game (cargoA-H shots).
- Limbs connected: PASS at 5x. No gaps at knee or ankle at 8x.
- Loop physically sensible: PASS. The near shoe goes (68,74) front, (74,75), (75,76) bottom, (78,77), (76,74) back, (77,72), (75,72) top, (70,70): a crank circle of about 10 px, clockwise seen from the near side, one turn in 8 frames, no repeated frame.

So the five reported defects are fixed in the file. The piece fails on something else:

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Repeated parts | PASS | Two wheels on one stamp (big rear, small front), four identical loaves, two plank rows. |
| 2 | Wheels round, spokes even | PASS | Round at 5x, 8 spokes each. |
| 3 | One light direction, ramps | PASS | Jacket 3 shades lit from the upper left, box 3 shades, helmet 3. |
| 4 | Outline 1 px, one ink | PASS | One ink (23,24,31), unbroken. |
| 5 | Face, hands, feet whole, no boiling | PASS | Eye, brow, nose, beard, mouth in every frame; the body is pixel-identical across frames, only the legs and spokes change. |
| 6 | Scale against Pepper | PASS | 88 px with the helmet (1.9 m seated at 46 px/m), rear wheel 31 px, box 2 m long; beside Pepper a grown-up on a long cargo bike. |
| 7 | As the game draws it | PASS | Not flipped; rides left, in front of the perches and of Pepper (allowed for bikes). |
| 8 | In game, what shows | FAIL | At 1x and 2x the baker has no legs. Trousers (75,79,80, luma 78), shoes (35,41,42, luma 39), frame (58,60,68, luma 60), chain case (ink, luma 24): the whole lower half is one dark mass between the white jacket and the box. In the cargoA shot at 2x the rider reads as a torso on a black bike; a 7 year old cannot see that he pedals. The owner's "legs miss the pedals" will come back as "he has no legs". The River Walk riders avoid this: cyclist 1 trousers luma 98, cyclist 2 jeans luma 118 against the same frame. |
| 9 | Next to bench, bin, lamp | PASS | As crisp as the bench at 5x; script WARN only (noise 0.3 %, three small blotches in the bread). |
| R | Scale, layer, outline, shapes, shading, palette, view, fit, read | read FAIL | Everything else PASS; read at 1x fails for the legs. |

Fixes (0 credits, Aseprite on the still and the 8 frames):
1. Trousers: replace (75,79,80) with a value at least 40 luma above the frame, for example the baker's checked kitchen trousers in (118,124,134) with (93,98,108) as the shadow shade; shoes (35,41,42) to a brown (107,65,40) like the other riders'. The leg then separates from the frame in every frame.
2. Chain case: the ink slab (core 22 x 7 px at x 75-96, y 73-79) gets a 1 px rim in the frame grey on its top and front edge.
3. The far pedal shows empty in frames 3 and 7 (a 2 px grey stub under the near foot, x 75-77, y 80-82) while the far shoe is drawn elsewhere: either draw the far shoe on it or drop the stub.

The depot (not this piece, known, level track): at the Downtown tall gates the bike is clipped at a vertical line at x 1938 and 3168 (cargoE-H shots). The line is the right edge of the GATE crates, so the box and wheels do read as sliding behind the crates, but above the crates' top (37 px) nothing covers the rider: his front half, then the whole rider, is sliced in the open air in front of the arch opening and the lamp post (cargoH, 4x crop: half a helmet and a back hanging over the crates). It reads as a cut, not as riding in. Fix for that track: cover the depot column from the crates' top to the arch's top with a foreground piece (a gate leaf or the arch's left pier drawn in front), or move the depot x to the arch's left pier so the pier itself hides him.

VERDICT (round 1, 7 Nov): FAIL (the legs do not read at 1x; one recolour fixes it)

# Round 2 (reviewer, 7 Nov)

Branch day/07nov-chars at 3b69dbf merged into the review worktree. Re-rendered: the changed files at 5x to 8x, River Walk x 1600, 2240, 2880, City Park tall y 144 x 640, 1280, 2560, the lane riders, car 5 and the baker in game (my still-vehicle hook now reads Rd.RIDER_TOP), colour and greyscale.

Legs at 1x: PASS. Trousers (118,124,134) with the (93,98,108) shade, brown shoes, a frame-grey rim on the chain case: in the Downtown shot at 1x, 2x and the 5x crop, colour and grey, the leg runs hip to knee to the pedal as its own shape against the dark frame; the chain case reads as a case. The other checks hold from round 1 (seated, hand on the grip, both shoes on the pedals, facing left, limbs joined, the crank circle). Script: still WARN (15 dirt px, 0.4 %), sheet PASS.

VERDICT (round 2): PASS
