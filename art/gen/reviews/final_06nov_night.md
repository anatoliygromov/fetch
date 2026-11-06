# Final gate review, night of 6-7 Nov (independent reviewer, gate 8)

Branch reviewed: `origin/prod/integrate-f` at 92ac3de (the merge of night/06nov-rw 76feb9d, night/06nov-cp 33151eb,
night/06nov-dt 958a829 plus the fix rounds). Worktree `/home/claude/wt/review-final`, branch `review/06nov-final`.
Levels: riverwalk (13 screens, 1 tier), citypark_tall (27 screens, tiers y0 / y24 / y144), downtown_tall (33 screens,
tiers y0 / y120 / y240). Every screen rendered with `LOOK_SWEEP=1 LOOK_STEP=320 ... --lookshots`, looked at on 2x
colour sheets and 1x greyscale sheets, hot spots at 4x to 8x. The River Walk boat ride was played: Pepper on the
first rowing boat, no input, 45 frames at 0.2 s over 9 s (one full trip out, rest, and back).

Method notes: I did not read the makers' notes before forming a view. The script checks below were run after.

## 1 Regression check against the track branches

The same sweep was rendered on the three track branches (worktrees `/home/claude/wt/rw`, `cp`, `dt` at the heads
above) and compared pixel by pixel with the integration frames.

| Level | Frames | Identical | Differences |
| --- | --- | --- | --- |
| riverwalk | 13 | 13 | none |
| citypark_tall | 27 | 2 | 25 frames differ by 12 to 311 px: every differing blob is a bobbing bone pickup (bob phase) or one goose pixel; no blob larger than 25 x 10 px, none on a built piece |
| downtown_tall | 33 | 14 | 19 frames differ by 78 to 392 px: all bobbing bones; no blob larger than 20 x 14 px |

Verdict: no regression from the merge. Nothing that passed on a track branch looks different here. The hand-joined
scene.lua water code (the park's pond and bank, Downtown's canal and basin) draws exactly as on the track branches.

## 2 Screen-by-screen

PASS = I would show it to the owner as finished. One FAIL cause can cover several screens; the cause is named once.

### River Walk (camera y 0)

| Camera x | Verdict | What is wrong |
| --- | --- | --- |
| 0 | PASS | house, kennel, bench, log: crisp, true scale |
| 320 | PASS | |
| 640 | PASS | bin, kiosks, chest |
| 960 | PASS | |
| 1280 | PASS | quay steps, lamp, rope pontoon in the water on its piles |
| 1600 | PASS | ferry; note: its hull ends flat on the surface with no wet band or ripple row, unlike the rowing boats (older approved piece, not touched tonight) |
| 1920 | FAIL | the pier block (world x ~1930-2070, y 60-215): a pale pink brick wall on the play line, as light as the far city in greyscale (it reads as background, not an obstacle); its brick courses are 40 x 14 px (0.9 m stones) so it reads as a chimney or a wall, not a quay pier; the arch underside (y ~200-214) is a soft dark gradient smear, not flat ramps; no 1 px ink on a play-line obstacle |
| 2240 | FAIL | the first rowing boat at rest (same cause as 2560) and the jetty between the boats (world x ~2500-2545): a 45 px table-like frame, reads as a table standing in the water at 1x |
| 2560 | FAIL | the rower at rest (frame 5, shown 1.5 s at each end of every trip, about 28 % of the time): the oar is a 12 px stub ending in a grey blade lying on the gunwale by his hand; a man holding a spoon. In motion the oar is right (see section 5) |
| 2880 | PASS | far quay, steps, promenade B |
| 3200 | PASS | |
| 3520 | PASS | |
| 3728 | PASS | cafe front, house, Mia |

Greyscale: ladder reads (far city lightest, hedge, water, play line darkest) except the pier block, see 1920.

### City Park tall

Tier y144 is the ground (path y 328); tiers y24 and y0 are the treetops and walks.

| Camera (x, y) | Verdict | What is wrong |
| --- | --- | --- |
| 0, 144 | PASS | gate pillars, leaf pile, log, stump with the magpie and ball, bench, hedge block: crisp, cute |
| 320, 144 | PASS | |
| 640, 144 | PASS | pond 1, stepping stones, duck boat sits in the water (waterline, wet hull), rushes; walk with lamp above |
| 960, 144 | PASS | keeper raking, leaf pile, goose, hollow log |
| 1280, 144 | PASS | bin, picnic table, leaf pile, hollow log |
| 1600, 144 | PASS | |
| 1920, 144 | PASS | pond 2, rope bridge above |
| 2240, 144 | PASS | bench, goose, walk, picnic table |
| 2560, 144 | FAIL | playground: the slide is a 2 px red line from the tower to the ground with no chute or rails; the climbing tower is a wire frame of 2-3 px bars beside solid pieces (bench, bin); a child cannot name the slide at 1x |
| 0, 24 | FAIL | front bushes (cause A, below) |
| 320, 24 | FAIL | cause A |
| 640, 24 | FAIL | cause A; the walk, rope bridge and lamp are fine |
| 960, 24 | FAIL | cause A; boughs attach to trunks, fine |
| 1280, 24 | FAIL | cause A |
| 1600, 24 | FAIL | cause A |
| 1920, 24 | FAIL | cause A |
| 2240, 24 | FAIL | cause A |
| 2560, 24 | PASS | the end oak, boughs, nest, walks, swing frame top |
| 0, 0 | FAIL | cause A |
| 320, 0 | FAIL | cause A |
| 640, 0 | FAIL | cause A; the rope bridge's hangers are 1 px pale lines, hard to see (minor) |
| 960, 0 | FAIL | cause A |
| 1280, 0 | FAIL | cause A |
| 1600, 0 | FAIL | cause A |
| 1920, 0 | FAIL | cause A |
| 2240, 0 | FAIL | cause A |
| 2560, 0 | FAIL | cause A |

Cause A (one fix clears 17 screens): the black front bushes are drawn at a fixed screen y (scene.lua, the front
frame prop: `at(im, ..., math.max(221 + dy(), p.y0))`, drawn outside the world's y shift). At the ground tier they
sit under the path as meant. In the treetop tiers they stay at the screen bottom, so they hang 2 to 3 m above the
path in front of trunks, walk legs and lamp heads (clearest at y0 x640, y0 x1920, y24 x2240). The owner's word for
this is "floating". Fix: draw the park's front bushes in world y (under the world shift) so they scroll down and off
with the path, or skip them when the camera is above the ground tier, as the tall Downtown already does for its
bollards (`if style == "town" and def.foot then return`).

Everything else in the treetop tiers passes: the boughs attach to their trunks (saddles, dark undersides), the walks
stand on their posts, the rope bridges hang from their posts, the magpie nest sits in the crown. Greyscale: the
boughs are only a step darker than the trunks behind them but their dark undersides keep them readable.

### Downtown tall

Tier y240 is the street (cobbles over the quay wall); y120 the balconies, loggias and the iron bridge; y0 the upper
storeys and the mid row's roofs.

| Camera (x, y) | Verdict | What is wrong |
| --- | --- | --- |
| 0, 240 | PASS | arched door, apple crates, cobbles, quay wall with its drain |
| 320, 240 | PASS | market stalls, pretzel sign |
| 640, 240 | PASS | |
| 960, 240 | PASS | note: six apple crate stacks in one screen, heavy repetition (not a defect) |
| 1280, 240 | PASS | statue with the cat, pedestal, planter, loggia above |
| 1600, 240 | PASS | fountain with 2 px jets, balustrades, bread crates |
| 1920, 240 | PASS | arch passage, tram shelter, ice cream cart, crate table, geese, parasol |
| 2240, 240 | PASS | parasols, bush planter, cafe table |
| 2560, 240 | PASS | the flooded basin: parasol poles stand in the water with a wet tint below the surface |
| 2880, 240 | PASS | mid-row gateway with the garden seen through its arch, granite block |
| 3200, 240 | PASS | tram shelter, river stairs, Mia |
| 0, 120 | PASS | |
| 320, 120 | PASS | the open square: mid row on its floor with bollards |
| 640, 120 | PASS | |
| 960, 120 | PASS | |
| 1280, 120 | PASS | iron balcony, loggia, stair |
| 1600, 120 | PASS | balustrades, urn, wall lamp |
| 1920, 120 | PASS | |
| 2240, 120 | PASS | the iron bridge over the square, arched rib |
| 2560, 120 | PASS | |
| 2880, 120 | PASS | |
| 3200, 120 | PASS | |
| 0, 0 | PASS | |
| 320, 0 | PASS | mid-row roofs against the far roofs: clean three-step ladder |
| 640, 0 | PASS | |
| 960, 0 | PASS | |
| 1280, 0 | PASS | wall of windows only (two storeys, nothing else); crisp, stamped, identical windows; note: five screens in a row are wall only, flat in greyscale, monotonous but not a defect |
| 1600, 0 | PASS | urn, wall lamp |
| 1920, 0 | PASS | |
| 2240, 0 | PASS | |
| 2560, 0 | PASS | |
| 2880, 0 | PASS | |
| 3200, 0 | PASS | |

Greyscale: far roofs lightest, mid row lighter, tall fronts darker, play props darkest. The cobbles are a 4-shade
ramp of single stones, crisp at 4x; at 1x they are a busy band, which the owner may or may not like.

## 3 Top 5 remaining issues per level (what a player or the owner would notice)

### River Walk
1. The rower's rest frame: oar is a 12 px stub on the gunwale (rw_rower.png frame 5; seen at world x ~2290-2400 and
   ~2640-2760, y 190-214, 1.5 s at each end of every trip). Fix: in frame 5 draw the full oar shipped across the
   gunwale, blade lifted out over the near side, same length as the stroke frames.
2. The pier block at world x ~1930-2070: too pale for the play line (greyscale: as light as the far city), 0.9 m
   bricks, smeared arch shadow. Fix: one palette step darker with 1 px ink, 24 x 10 px granite blocks, the arch
   underside as two flat shades.
3. The jetty between the boats (world x ~2500-2545, y 196-224) reads as a table in the water. Fix: a deck twice as
   wide (at least 2 m, 92 px) on four piles, planks on top, a mooring post.
4. The ferry's hull (world x ~1560-1800) ends flat on the surface with no waterline ripple or wet band, unlike the
   rowing boats and the duck boat. Fix: give it the rowboat's ripple row and the tinted submerged strip (same code).
5. Bones bob mid-air over the harbour water (x 2200-2850, y 140-200): pickups over water with nothing under them.
   Design, not art; mention only if the owner asks why bones float.

### City Park tall
1. Cause A: the front bushes hang in the air in every treetop screen (17 of 27 screens). Fix as above (scene.lua).
2. The playground slide (world x ~2660-2720, y 290-328): a 2 px red line. Fix: an 8 to 10 px wide chute with 1 px
   rails and a flat run-out, the tower's bars 3 to 4 px with ink.
3. The climbing tower and swing frame are wire frames beside solid pieces (x ~2590-2720 and 2810-2880). Fix: thicker
   posts (4 px), a solid cabin wall, seats as 3 px planks.
4. The rope bridge hangers (y0 x640, y0 x1920, y144 x1920) are single pale pixels; at 1x the deck looks unhung.
   Fix: 1 px of the rope's dark shade for each hanger.
5. Greyscale: boughs and trunks sit one step apart. Fix: a 1 px ink line along each bough's top edge (play
   obstacle rule) so the stand-on edge reads.

### Downtown tall
1. The top tier from x 1280 to 2560 is wall only: five screens of identical windows with no prop, sign or lamp but
   one urn and one wall lamp. Fix: a sign bracket, a flag, a pigeon or a chimney shadow per screen (decoration, no
   ink); not a defect, a dead stretch.
2. Apple crates: six stacks in the screen at x 960 y240 and more at x 2560; the same crate repeated. Fix: a second
   crate (pears or bread) in half the stacks.
3. The cobbles at 1x are a busy purple-brown band (x 0-3520, y 420-440). Fix if the owner says so: drop one of the
   four stone shades.
4. The mid-row gateway (x ~2880-3060, mid layer) is a flat brown block with a flat cornice. Fix: a 1-shade-darker
   plinth row and a lighter coping line (decoration ramps, no ink).
5. The fountain's jets (x ~1600-1700, y 300-360) are 2 px white verticals with no splash ring where they land.
   Fix: a 2-frame ring of 3 white pixels at the basin surface.

## 4 Script checks (run after the eye review)

`python3 -I tools/asset_qa.py --all`: 252 assets, 182 PASS, 44 WARN, 26 FAIL. Of the 201 files this branch changes
against main, one is in the FAIL list: `rail_bg_left` (5 x 50 strip: one blotch, decor-ink). The rest of the 26 are
untouched older files (cyclist sheets, cargobike_pedal slot). Run by hand with guessed flags, outside the library
list: rw_rowboat PASS; rw_rower WARN (3.3 % lone pixels, "feet not anchored" which is the oar moving); cp_bough_limb,
limbx, low, stump PASS; cp_bough_nest and cp_bough_trunk FAIL on outline (they are decoration: the flag is my
guess, not a defect); town_roof_chimney, dormer, gable FAIL on ladder, decor-ink and pane size at `--layer mid
--building` (the makers' layer may differ; check their cards); quaywall FAIL (2.6 % dirt, 38 blotches, no ink).

## 5 The boat ride in motion

45 frames, Pepper amidships. Out: 14 frames moving right (stern first, the rower facing the bow and pulling), 7
frames rest at the jetty, 15 frames back, rest at the quay. In the stroke frames the oar runs from his fists over
the near gunwale into the water, the blade tinted below the surface; the arm bends at the elbow; the catch and the
finish put the blade in at different angles; the ripple row runs along the hull and a dashed wake trails the stern
while it moves; the hull below the waterline is tinted darker (wet). Nothing boils between frames, the hull and
the rower's torso are pixel-stable. The loop makes physical sense. The only bad frame is the rest frame (issue 1).
Pepper rides standing, keeps her spot, steps off onto the jetty top (y 196) cleanly.

## 6 Verdict per level

| Level | Ready for the owner to look at | Why |
| --- | --- | --- |
| River Walk | No | two small fixes first: the rower's rest oar and the pier block; the harbour is otherwise the best screen of the night |
| City Park tall | Yes, with cause A fixed first if it can be done in minutes (one line in scene.lua); otherwise show the ground tier only | the ground tier passes every screen; the treetop tiers fail on one shared cause |
| Downtown tall | Yes | all 33 screens pass; the remaining items are polish |

No regression from the merge. Nothing was fixed by me.
