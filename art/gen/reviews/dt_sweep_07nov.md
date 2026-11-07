Reviewer: independent gate-8 visual reviewer (Claude, did not make this), round 1, 7 Nov 2026

# Downtown (tall), branch day/07nov-dt (ab40394): the low row, screen by screen

# Round 1 (reviewer, 7 Nov)

Method. Own worktree at ab40394. Rendered `LOOK_SWEEP=1 LOOK_STEP=320`: 33 frames, 11 screens (cam x 0 to 3200)
at the three tiers (cam y 240 street, 120, 0 roof). Looked at every screen as a 2x stack of its three tiers in
colour, at every tier as a 1x greyscale sheet, and at the suspect spots at 4x to 6x. Route render with
`tools/draw_routes.py downtown_tall`. The pieces at 5x beside the bench, bin and lamp; `asset_qa.py` on the key
files. The concepts (`art/gen/concepts/dt_design_A1_a, A1_b, A2_a, A3_a, A4_a`) and `design/README.md` read
first; the maker's `docs/review/07nov/dt/README.md` read last, to check numbers. Its numbers hold (asset_qa
results reproduced; world 3520x480; the three moved boxes as stated). Metres at 46 px/m. Pepper on screen is
52 px long and 40 px tall.

PASS means I would show that screen to the owner as finished.

## Screens

| cam x | y 240 (street) | y 120 (the high road) | y 0 (roofs and sky) |
| --- | --- | --- | --- |
| 0 | PASS. Start house (2 storeys, door 36x90), two shops, the stall, crates. One scale, crisp, clean ladder. | FAIL. The mid row's lowest storey of 12x18 windows sits directly on the shops' cornices (0 to 2 px above them at screen y 100-136): the half-scale town stands on the true-scale shops, two scales touching vertically. closed4's chimney is an 8x38 brown plank with no cap standing at screen x 290-298; closed3's roof hat floats 3 px above its cornice (the pink mid wall shows through at screen y 137-139). | FAIL (small). Sky, spire and clouds are good. The start house's chimney is a brown 8x24 stick with no cap, the roof's own dark colour: a plank. The mid row's roofs are the same brown as the start house's roof, one step lighter only in places. |
| 320 | PASS. Cafe: parasols, tables, the pretzel sign, lamp. | FAIL. The mid row's lowest windows on the shop cornices again (screen x 170-250, y 100-136); the shops' roof hats are striped brown pyramids with grey step caps that read as ziggurats, not tile; closed7's chimney stick (8 px, no cap) floats 1 px above its roof (row 13 of the file is empty). | PASS (small): the cafe house's hip roof and the mid row behind it read; the chimney sticks again. Would pass with the chimney fixed. |
| 640 | PASS. Market: stall, awning, crates. | FAIL. closed9's hat floats 3 px above the cornice (the cream mid wall shows in the slit at screen y 137-139, x 0-110); the mid row's lowest windows sit on the shop tops. | FAIL (small). Chimney sticks; the mid row's roofs at the front row's value. |
| 960 | PASS. Awnings, crates, the bakery's ground floor at true scale. | FAIL. Same cause: the mid row's lowest storey on the shop tops; closed13's chimney plank (5x30, no cap) at screen x 125-130; the bakery's upper storey is fine. | PASS (small). The bakery's low stepped roof and the sky read; its chimney is the stick again. |
| 1280 | FAIL. The plaza. The statue and the cat read, the wing and the arcade's ground floor are built. But the arcade's arches are 26 px wide (0.57 m) beside a 52 px dog: a row of slits, not an arcade. The roofs at the top of the frame are two dark brown-grey brick bars (median 135, darkest 24) on light walls: slabs, not roofs. The mid row's half-scale window shows in the alley between the wing and the arcade at the street tier. | FAIL. The route reads (two dark bars, Pepper on them, the guild's red gable at the right) but the picture is bars on a wall: the wing's and the arcade's walls (luma 150-200) are the same value as the mid row behind them (155-207); nothing has a silhouette; the mid row's lowest windows sit right behind the bars. | PASS. Sky, the mid row's gables, the bakery's roof and chimney stick at the left. Would pass as a sky screen. |
| 1600 | FAIL. The fountain square. The two pavilion canopies are 58x14 planks with three dark teeth, hung at y 336/344, one straddling the seam between the guild hall's stone wall and its pavilion (25 px of it, x 1655-1680, hangs on the guild's wall), the other 9 px past its pavilion's right edge into the alley (1888-1897): hung shelves that belong to no one shop front. The fountain is the old one: a grey column with a flat plate top, two straight white 1 px lines for jets, the basin a pit between posts, and the mid row's half-scale window and pink wall right behind the column in the gap. | FAIL. The guild roof is a red running-bond brick mass (median 78, range 55-135, the busiest thing on the screen) with crow steps: it reads as a brick wall with a stepped top, not a tiled gable. The pavilion roofs are dark bars; the pavilion walls (152) are the same value as the mid row's pink house beside them (155). The gap between the pavilions shows the mid row's pink wall, not the fountain and not sky: the concept's "the gap is the fountain" does not happen at this tier (the column top is at 344, below the frame). The chimney with the bone is right. | PASS (small). Sky and the mid row's rooflines; the chimney and the bone at the bottom left read. |
| 1920 | FAIL. Tram street. Shelter, kiosk, stop sign, goose, crate stack: fine. The shed's gate opening is 40 px (0.87 m): a door, not a tram gate. The three roofs at the top are dark bars at three heights. | FAIL. The dormer is a 24x12 px box with a red cap standing ON TOP of the shed's parapet coping: doll-sized (0.5 x 0.26 m, smaller than Pepper's head) and on the wrong side of the parapet. The kiosk house (56 px of blank plaster, 156) and the shelter house are the same value as the mid-row walls beside them: no silhouette, the bars float on a wall of small windows. | PASS. Sky, spire, the mid row. |
| 2240 | FAIL (small). Flower market: the glass hall, the springy awning, the tub and table, the goose, the footbridge: the street reads. The canal house's canopy is the plank with teeth again, hung on a plain door wall. | FAIL. The hall's roof garden is a 160x8 px dark ledge with 2 px flower dots: a ledge, not the concept's railing with planters. The canal house's parapet is a dark bar on a 48 px plaster strip; the mid row's windows run behind and between everything. | PASS. Sky, the spire, the mid row's roofs. |
| 2560 | PASS (small). The bridge lands on the crate stack; the shops and the 2-storey house at true scale. The brown chimney sticks are off screen here. | FAIL. The mid row's lowest storey on the cornices; closed1's chimney stick (8x18, roof colour, no cap) 1 px off its roof; closed3-type hats floating 3 px. | FAIL (small). Chimney sticks on closed2 and the hat on closed1. |
| 2880 | PASS. The bounce chain over the water and the gateway house. | FAIL. Same cause: the mid row's lowest storey on the shops' cornices; closed16's chimney plank at screen x 77-83. | FAIL (small). The gateway house's top is a flat band with a small stepped hat in the middle and a stick chimney at the right end (x 3180): a box with a hat. |
| 3200 | PASS. Shelter, shops, the arrow sign, Mia, the stairs. | FAIL. Same cause. | PASS (small). Sky, the mid row; the 2-storey house's hip roof reads. |

Street tier: 8 of 11 PASS. The three FAILs are the three set-piece screens (1280, 1600, 1920): arch and gate
scale, the plank canopies, the old fountain. High road tier: 0 of 11 PASS. Roof tier: 7 of 11 PASS; the FAILs
are small (chimney sticks, the gateway's hat).

## Route render (`tools/draw_routes.py downtown_tall`)

PASS as a route: every high-road box sits on a building of the table, every drop lands on the street, the two
ways up and the chimney bone are where the design says. Two notes, not failures: the map's names still carry
the old vocabulary (BALCONY, LOGGIA, GALLERY, DORMER, TIER) for pieces that are now parapets, a porch and a
roof; and the middle tier's three boxes (1552 y 312, 1656 y 336, 1840 y 344) are drawn as canopies that
overhang their buildings (see 1600).

## The five problems of design/README.md, judged on the frames

1. **Fiction and scale contradict each other.** PASS at the street tier, FAIL at the high road tier. The
   true-scale walls that never ended are gone: every low-row building is one or two storeys, the high road is
   their tops, and there is sky on every screen at y 0 and on most at y 120 (frames x 1280 to 2240, y 120: sky
   in the top 60 to 80 px). But the mid row still scrolls at 0.6 vertically (`vcam.lua` Vc.MID), so between the
   street tier and the roof tier it rises 96 px against the low row (0.4 x 240) and its half-scale lowest storey
   comes up and stands on the low row's cornices (x 0, 320, 640, 960, 2560, 2880, 3200 at y 120: window sills
   0 to 2 px above the dentil bands). The fiction
   "tall houses behind a square" breaks into "a half-scale upper town sitting on the shops" on 7 of 11 screens.
2. **No single language for "you can stand here".** PASS with one exception. Every walkable roof is the same
   stone parapet strip with a 1 px ink outline (wing, arcade, pav1, pav2, shed, kiosk house, shelter house,
   canal house, hall), the guild gable's crow steps and the chimney are outlined too, and the decorative roofs
   (brown hats, no outline) never look like them. A first-time player sees "dark outlined bar = walk" on every
   high-road screen. The exception is the middle tier: the three canopies are a third vocabulary (plank with
   teeth), neither the street's striped awnings she bounces on nor the parapets she walks on.
3. **No silhouettes, no sky.** FAIL. Sky: solved at y 0 everywhere and at y 120 on the set-piece screens.
   Silhouettes: not solved. Front-on, a flat roof behind a parapet shows nothing but the parapet, so each
   low-row building is a plaster rectangle with a dark bar on top, and its plaster (152 to 156) is the same
   value as the mid row's walls directly behind it (pink 155, ochre 160 to 176, cream 194 to 207). In the y 120
   greyscale sheet, screens 1280 to 2240 are one even grey wall of small windows with dark bars on it. The only
   silhouettes against the sky are the mid row's gables, which are not the route. The guild gable is the one
   low-row shape with a skyline, and its brick fill makes it a busy mass (the A2 fault the brief warned about).
4. **Two scales on one street.** FAIL. Side by side on the street: solved (one scale on the street, x 0 to
   3520). Vertically: not solved, see 1. The alleys between the high-road buildings (16 to 48 px) show the mid
   row's half-scale windows at the street tier too (x 1280 between the wing and the arcade; x 1600
   behind the fountain column), where the concept shows the arcade's roof edge and sky.
5. **Set pieces pressed into the walls.** PASS for the statue, the kiosk and the shelter (each in front of its
   own house, with an alley each side). FAIL for the fountain: it is the old piece, the basin is still a pit,
   the column top is a flat plate, the jets are two straight white lines, and the thing standing behind its
   column in the gap is a half-scale house, not sky. The maker lists it as the next piece; as shown it fails.

## The seven questions

1. Walkable at a glance, one walking language: YES for the parapets and the gable (dark outlined bar, every
   time). NO for the middle tier (planks with teeth). The way goes right along the bars; a child can see that.
2. Buildings with roofs and silhouettes, or slabs and boxes: SLABS AND BOXES on the high road. Parapet strips
   on plaster rectangles, no roof surface, no ridge, no gutter, no silhouette, same value as the wall behind.
   The decorative roofs are brown striped pyramids with step caps (ziggurats), not tile.
3. Mid row behind, lighter, smaller, quieter: SMALLER yes (windows 12x18 against 36x60). LIGHTER only where it
   is cream (194 to 207); its pink and ochre houses (155 to 176) sit at the low row's value (152 to 156). QUIETER
   no: it has three times the windows, white frames, and it climbs up onto the low row at the roof tier.
4. True scale: the fronts, doors (36x90), windows, the chimney and the parapets (0.46 m) are right. Doll-sized:
   the arcade's arches (26 px, 0.57 m), the shed's gate (40 px, 0.87 m), the dormer (24x12 px), the roof
   garden (8 px tall), the hat chimneys (8 px wide, no cap). Nothing is giant.
5. Nothing floats: FAIL. The decorative roof hats float 3 px above their cornices on closed3, 5, 8, 15, 18, 20
   (file rows 37 to 39 empty) and 1 px on closed1, 4, 10, 13, 16, 19 (row 39); the chimney sticks float 1 px on
   closed7 and 22 (row 13); the mid row shows through every slit. The pav1 canopy overhangs its pavilion by
   25 px to the left onto the guild hall's wall, pav2's by 9 px to the right into the alley. The dormer stands on the coping, not on the
   roof. The fountain's jets are lines in the air. The chimney (guild), the signs and the statue are attached.
6. Closeness to the concept: the street tier of A4 is close (the arcade, the statue in front of the middle
   arch, the tub, the guild's stone door). The roof tiers are far: A1's lead flats with light copings and tile
   slopes became dark brick parapet bars; A2's tiled gable became brick; A2's free-standing fountain with sky
   over its column is the old fountain with a pink mid-row wall behind it; A3's glass hall with a railing
   garden is a glass box with a ledge; A1's mid row a clean step lighter and behind is the old mid row at the
   same value, climbing onto the roofs. Biggest gaps, in order: the mid row (value and vertical scroll), the
   parapets as the only roof language, the fountain, the brick gable, the toy arches and gate.
7. Would the owner still call it messy: at the street tier, no, it is calmer than before and one scale. At the
   high road tier, yes: "dark bars on a wall of small windows, and the small town sits on my shops".

## Top 8 fixes by impact

1. **Mid row vertical scroll and feet.** Stop the mid row climbing onto the low row: its feet must stay below
   the low row's eaves at every tier. Either set the Downtown mid layer's vertical factor from 0.6 to 1.0 (it
   is a square behind the row, at world distance), or keep 0.6 and move the mid row's base 96 px down (feet at
   world 490 instead of 394), so that at cam y 0 its feet are at world-equivalent 394 and never above 300.
   Then the mid row's lowest storey stays at least 40 px below every low-row eave at every tier (x 0, 320, 640,
   960, 2560, 2880, 3200 at y 120) and out of the alleys at y 240.
2. **Mid row one step lighter and quieter** (the planned rebuild from the styled parts at half size). Target
   on screen after fade: plaster medians at least 25 luma above the low row's (low row 152 to 156, so mid
   plaster 180 to 210, no house under 180), window glass no darker than 130, frames in the plaster's light
   shade not white, and half the window count per storey (one window per 24 px of front, not per 16). Roofs
   of the mid row in a lighter pink-grey than the low row's roofs by 25 luma.
3. **Parapets as roofs, not bars.** Keep the one language but make it the concept's stone coping over a lead or
   tile roof: the parapet body in a mid-tone granite (on-screen median 150 to 165, not 135 with a 24 darkest),
   the coping 2 px light (about 200), the 1 px ink outline kept, and under the coping a 3 px lead-sheet seam
   row (two greys) so the top reads as a roof edge; on the pavilions, kiosk house, shelter house and canal
   house add a 6 px tile eave course (two oxblood shades, the 4 px scallop stamp) under the parapet so the
   building ends in a roof, not in a strip. Same ramp on all nine roofs.
4. **Fronts darker than the mid row, with a cornice silhouette.** Low-row plaster one step darker than the mid
   row (fix 2 does half of it); and each high-road front gets a 4 px dentil cornice plus a 2 px shadow line
   under the parapet (the closed fronts have the dentil band already; pav1, pav2, kiosk house, shelter house,
   canal house, wing and arcade do not), so that on the y 120 greyscale sheet every building has an edge.
5. **Decorative roofs and chimneys.** Fill the empty file rows (closed3/5/8/15/18/20 rows 37 to 39, closed1/4/
   10/13/16/19 row 39, closed7/22 row 13) so the hat and the chimney touch the cornice; redraw the hat as a
   tile hip with the 4 px scallop course stamp (3 courses, two oxblood shades, 2 px ridge cap, no grey step
   caps); chimneys 10 px wide with a 2 px stone cap and a body one shade darker than the roof, on every front
   that has one (closed1, 2, 7, 22, start, bakery, gateway).
6. **Canopies as part of the shop fronts.** Replace the 58x14 plank with teeth by a cloth canopy in the street
   awning's vocabulary: width = the shop window + 8 px (pav1 window 1692-1755 so 72 wide, pav2 1820-1883 so
   72, guild door 1572-1613 so 50), depth 10 px, a 3 px valance with a 1 px ink edge, fixed at the window
   head, and inside its own building's x range (pav1 canopy x 1688 to 1760, not 1655 to 1713; pav2 1816 to
   1888, not 1839 to 1897; guild 1568 to 1618).
   The box widths in the map change with them (the maker's lever note applies: physics rerun).
7. **The fountain to A2.** A granite column 16 px wide with a ball finial, its top at y 296 so 48 px of it shows
   in the gap at the y 120 tier with sky above it once fix 1 lands; a round bowl 48 px wide at y 344 (the TIER
   box); a 3 px kerb basin at street level with a water band behind it; jets as 2 px arcs, not straight lines.
8. **Scale of the openings and the dormer.** Arcade: two arches of 46 px (1 m) in the 120 px front instead of
   three of 26, the statue in front of the pier between them; shed gate: 100 px wide like the approved
   tramshed96's, which means the shed grows to 128 px or the gate takes the whole 88; dormer: 40x30 px (0.9 by
   0.65 m) drawn behind the parapet with its sill hidden by the coping, a 2-course tile cap, or dropped; roof
   garden: a 12 px iron railing with 3 planters of 16x6 instead of the 8 px ledge.

Then: the guild roof's brick fill to tile courses (scallop stamp, contrast at most 60 across the fill), brick
only on the crow steps and the chimney.


# Round 2 (reviewer, 7 Nov)

Head b7fa47f. Same method: own sweep (33 frames, 2x tier stacks in colour, 1x greyscale per tier, suspect spots
at 4x to 8x), the route render, the changed files at 5x to 7x beside the bench and bin, numpy on the fronts (no
empty row inside any front now), the maker's `docs/review/07nov/dt/README.md` round 2 section read last. Its
numbers hold on my frames: low-row plaster 152 to 156, mid row 197 to 207 (45 apart), the mid row's lowest
window sills 52 px below the lowest eave at every tier (`L.vmid = 1.0`), arches 46 px, gate 62x100 from 1934,
dormer 40x30 behind the parapet, railing garden 12 px with three planters, guild roof in tile (fill 79 to 107),
canopies cloth, fountain rebuilt. A cargo bike rendered at the gate (LOOK_SPOTS 2060,424 with LOOK_CARGO -45
and -15 on this branch's tests_look.lua, which has the hook).

## Screens, round 2

| cam x | y 240 (street) | y 120 (the high road) | y 0 (roofs and sky) |
| --- | --- | --- | --- |
| 0 | PASS | PASS. Tile hips with ridge caps on the shops, brick chimneys with caps, the mid row a clean step lighter with its sills 52 px above the eaves. | PASS. |
| 320 | PASS | PASS (small: the closed1-kind hat's side slopes are 2 px vertical grey stripes that read as corrugation at 2x; flat lead with a 4 px seam would be quieter). | PASS. |
| 640 | PASS | PASS | PASS |
| 960 | PASS | PASS | PASS |
| 1280 | PASS. Two 46 px arches, the statue on the pier, dentil cornices, lead parapets with light copings. | PASS. The wing and arcade parapets read as the tops of two buildings against a pale quiet town and sky. | PASS |
| 1600 | PASS. The fountain stands free: column with a ball finial, 2 px jet arcs into a kerb basin at street level, striped cloth canopies on the pavilions' windows, the porch slab over the guild door. (Bone collisions on the statue and fountain are pending; not judged.) | PASS. Tile gable with granite crow steps and a brick chimney, tile eaves under the pavilion parapets, the column top in the gap. | PASS |
| 1920 | FAIL. The street lamp at x 1959 stands in the middle of the shed's gate opening (1934-1996), in front of the arch: the cargo bike rides through the lamp post (my bike frames: the post crosses the bike's box). The crates (1864-1934) end at the jamb as the maker says; that part is right. | PASS. The dormer sits behind the parapet with its sill hidden; kiosk and shelter houses have edges and a window each (the kiosk house's window is behind the shelter's glass canopy at the street tier, invisible there, visible here). | PASS |
| 2240 | FAIL. The canal house still carries the old hung balcony: map box BALCONY 2420 y 328 (56 wide) is not claimed by the low-row table, so the code fallback draws the plank with three teeth on the canal house's door wall (screen x 180-236, y 88-102 at this camera). The owner's "no hung balconies anywhere". Everything else on the screen passes: railing garden with planters, the springy awning, the footbridge. | FAIL. The same plank at the bottom right (screen x 180-236, y 208-222). | PASS |
| 2560 | PASS | PASS (small: closed1's striped side slopes) | PASS |
| 2880 | PASS | PASS | PASS |
| 3200 | PASS | PASS | PASS |

Street tier 9 of 11 PASS, high road tier 10 of 11, roof tier 11 of 11. Both FAIL causes are placements, not
drawings: one unclaimed balcony box and one lamp in a doorway.

## Route render, round 2

PASS. Names are the new ones (WING ROOF, ARCADE ROOF, PAVILION ROOF, SHED ROOF, KIOSK ROOF, SHELTER ROOF,
CANAL ROOF, PORCH, CANOPY), GATE at 1864-1934, CANOPY 1680-1752 and 1816-1888. The one old name left is BALCONY
2420 y 328 on the canal house, which is the unclaimed box above.

## Gate geometry

GATE crates 1864-1934 y 388 (36 tall), the shed's gate opening 1934-1996: the crates' right edge, the depot line
and the left jamb are one column, so a bike clipped at 1934 comes out of the doorway and nothing stands on the
crates' side. The 62 px gate is 1.35 m, enough for a cargo bike's width front-on; the bike is 100 px long so it
overlaps the piers while it leaves, which is how a doorway reads. The one fault is the lamp at 1959 (see 1920).
Fix: the lamp to x 2008 (the 16 px alley between the shed at 2000 and the kiosk house at 2016; the post's base
is 12 px) or to 1850, left of the crates. The checkpoint moves with it.

## The five problems, round 2

1. Fiction and scale: PASS. The mid row moves with the world (`L.vmid = 1.0`) and its lowest sills stay 52 px
   under the lowest eave at every tier; no half-scale storey stands on a shop anywhere in the sweep.
2. One language: PASS with one piece left over. Parapet with ink and a light coping = walk, on all nine roofs;
   the gable and the chimney outlined; the middle tier is cloth canopies and a stone porch, part of the fronts.
   The canal house's plank balcony (2420 y 328) is the last piece of the old vocabulary.
3. Silhouettes and sky: PASS. Low row 45 luma darker than the mid row, every building ends in a dentil cornice
   and a tile eave or a lead coping, the mid row's gables and the sky above; the y 120 greyscale sheet reads as
   a row of houses in front of a lighter town.
4. Two scales: PASS. One scale on the street, one behind, never touching; the alleys show plain wall (the grey
   wall in the fountain gap at the street tier measures a neutral 194 on my frames, not violet; the only
   lavender read is the mid row's grey-pink house beside cream at x 1920, (212,197,195), which is small).
5. Set pieces: PASS. The fountain stands free with sky over its column at the A2 camera; statue, kiosk and
   shelter in front of their own houses.

## The seven questions, round 2

1. Walkable at a glance, one language: yes. 2. Buildings with roofs: yes, low houses with cornices, tile eaves
and parapets; the hats are tile hips. 3. Mid row behind, lighter, smaller, quieter: yes on all three (201
against 152, 14x22 windows one per 24 px, no white frames). 4. True scale: arches 1 m, gate 1.35 by 2.2 m,
dormer 0.9 by 0.65 m, chimneys 10 px with caps; nothing doll-sized or giant. 5. Nothing floats: the hats and
chimneys touch their cornices, the canopies sit on their windows inside their buildings, the dormer sits behind
the parapet, the jets land in the basin; the one hung thing is the canal house plank. 6. Concept: A1, A2 and A4
are close now (A2 closest); A3's hall is the plainest of the four and is fine. 7. Would the owner still call the
high road messy: no. He would ask about the plank on the canal house and the lamp in the gate.

## Fixes, round 2 (in order)

1. Canal house: claim BALCONY 2420 y 328 in `dt_lowrow.lua` and draw it as a cloth canopy over the canal
   house's door (2420-2478, the box's width + 2, the same ramp), or drop the box if the route does not need it.
2. Lamp 1959 out of the gate: to x 2008 or 1850.
3. closed1-kind hat: side slopes as flat lead, two greys with a 4 px seam row, not 2 px vertical stripes.
4. Pending from other tracks, seen or not: bone collisions on the statue and fountain (not judged); the violet
   wall (not seen as violet on my frames, see problem 4).


# Round 3 (reviewer, 7 Nov)

Head a2506f8 (rounds 3, 4 and 5 of the maker: canal canopy, lamp, hips; the mid row lowered to world 430 and rebuilt
as 3-4 big gabled houses per screen, the far roofs strip off, saturated low-row plasters, hips 36-44 px, the camera
floor 152; the far band of round 4 removed again). Own sweep of 33 frames at the three tiers with a cargo bike parked
at x 1965 (`LOOK_CARGO=1965` in the sweep), 2x colour tier stacks, 1x colour and greyscale sheets per tier, suspect
spots at 6x, the route render, the maker's rounds 3 to 5 notes read last (their numbers hold: mid walls 184-195 on
screen against low-row plaster 153-173, sky over the gables 70-80 px at y 120, lamp at 2040, gate 1934-1996). The
sky is unpainted here (day/07nov-sky brings it) and is judged for space and clipping only.

## Round 2 fixes

1. Canal house balcony: DONE. Box 2420 y 328 is CANOPY, claimed, a striped cloth awning over the canal house's
   door (x 2240 frames, both tiers). No hung balcony anywhere now.
2. Lamp in the gate: DONE. The lamp is at 2040, the gate opening 1934-1996 is clear; the parked bike at 1965 stands
   in the arch with nothing through it. At 2040 the post stands in front of the kiosk house's door under the end of
   the shelter's glass roof (the maker's respawn reason for not 2008 accepted); at 1x it reads as a lamp beside the
   shelter's post. PASS.
3. Hips' side stripes: DONE. The rows beside a hip are transparent; the hip is the silhouette, sky or the mid row
   beside it (x 320, x 2560 at y 120).

## Screens, round 3

| cam x | y 240 (street) | y 120 (the high road) | y 0 (roofs and sky) |
| --- | --- | --- | --- |
| 0 | PASS | PASS (small: closed4's chimney at screen x 288-298 is a 10x36 oak-brown column against the pale gable and the sky; at 1x it reads as a post, the start house's brick chimney reads as a chimney) | PASS |
| 320 | PASS | PASS | PASS |
| 640 | PASS | PASS | PASS |
| 960 | PASS | PASS | PASS |
| 1280 | PASS | PASS | PASS |
| 1600 | PASS (the fountain's face in the quay wall's greys now; the gap behind the column is cream wall at the street tier, sky at y 120) | PASS (small: the mid row's chimney at screen x 150-158 is 8x38 px, 1.65 m at half scale, a thin tower) | PASS |
| 1920 | PASS (bike in the arch, lamp at 2040 clear of it, crates end at the jamb) | PASS | PASS |
| 2240 | PASS (cloth canopy on the canal house, railing garden, bridge) | PASS | PASS |
| 2560 | PASS | PASS | PASS (small: the far spire's cross lands on closed2's parapet at screen x 215, y 90 at this camera and reads as a cross on the house; the spire drifts at 0.03 so it sits on a roofline somewhere on three of the eleven screens) |
| 2880 | PASS | PASS | PASS |
| 3200 | PASS | PASS | PASS |

33 of 33 PASS. The small notes are polish, none would make the owner call a screen messy.

## Route render, round 3

PASS. CANOPY 2420 y 328 named and claimed, lamp at 2040, GATE 1864-1934, everything else as round 2.

## The five problems, round 3

1 fiction and scale PASS (the mid row is a row of big houses behind a square, its foot at 430 under the street
line, moving with the world; never on a cornice). 2 one language PASS, no leftover (parapet with ink and light
coping = walk; cloth canopies and the stone porch on the middle tier; nothing hung). 3 silhouettes and sky PASS
(crow-step, Dutch and hip gables of 80-112 px wide houses against 70-80 px of sky at y 120; the low row 30 luma
darker with cornices and tile eaves). 4 two scales PASS. 5 set pieces PASS.

## The seven questions, round 3

1 walkable at a glance: yes. 2 buildings with roofs: yes. 3 mid row behind, lighter, smaller, quieter: yes, and
now also few and big (3-4 houses a screen, 2-3 windows a storey). 4 true scale: yes; small: the mid row's chimneys
at 38 px are too tall for half scale (24 px). 5 nothing floats: nothing. 6 concept: close, see below. 7 messy: no.

## The main question: character against A1-A4

Close. The three things the concepts are made of are all there: a warm front row (ochre 0.49, salmon, oxblood,
cream, red tile hips 36-44 px with ridge caps, brick chimney on the start house, the guild's tile gable), calm big
pale houses behind (one tint each, two or three big windows a storey, flat wall between, crow steps and Dutch
gables as the concept's skyline), and sky over all of it at the high road tier. Beside A1 (x 1280 y 120) the
picture has the same bones: bakery wing and arcade at the left, the gables and sky behind, the dog on the lead
flat. Beside A2 (x 1600 y 120) the gable, the chimney with the bone, the two pavilion roofs, the column in the
gap. Beside A3 (x 1920-2240) the stepped roofs, the glass hall with its railing garden. A4 (x 1280 y 240) was
close already.

What is still busy, washed out or cut, all small:
- Busy: at the y 0 tier the River Walk skyline (far city, scroll 0.08) shows as a band of towers, domes and
  spires between the mid row's gables and the clouds (x 1600-2560 y 0, luma 173-200); it keeps the ladder but
  it is the one thing the concepts do not have behind the tall houses. The painted sky branch replaces it; if
  that sky keeps a skyline, it should be lower and simpler than this one (tops only, 20-30 px, no spires).
- Busy (small): the Riddarholmen spire's cross drifts with the camera and sits on a roofline on three screens.
- Washed out: nothing. The mid row at 184-195 reads as pale houses against a saturated blue sky, not as haze;
  the greyscale sheet keeps the order sky, mid, low row, play.
- Cut: nothing wrong. At y 120 the gables are whole (tops at screen y 60-100) and the low row's hips are whole;
  the mid row's lower storeys are hidden by the low row as the concept intends; at y 240 the parapet caps sit at
  the top edge as before.
- Reads: the closed-kind chimneys in the oak ramp (10x36 brown columns) read as posts beside the pale mid row;
  brick like the start house's would read as chimneys at 1x.

## Camera floor 152

Her feet sit at screen y 152 instead of 168, so 152 px of world is visible above her feet (was 168) and 16 px
more below. What that hides: anything 152-168 px above the floor she stands on. From the street (424) that is
world 256-272: the pavilion roofs, galleries, wing, bridge and bakery balcony, which at the old floor showed as 0
to 16 px of parapet cap at the top edge and are reached only from other roofs (every roof-to-roof step is within
her 46 px jump: wing 272 to arcade 280, steps 272 to 244, chimney 200 from 244, pavilions 256 from 248, shed 264,
kiosk 248, shelter 264, hall 232 from the awning's bounce, canal 248, bridge 272). The sign (304, 120 up), the
porch and canopies (312-344, 80-112 up), the crates and awnings are all on screen from the street. Bones: the 32
bones above y 300 all sit on or over the roofs and are collected from them; the five at y 272 (x 1360, 2500-2624)
sit at the top edge from the street, half cut, as roof bones. Hazards are at street level or below (water, bikes,
trams) and unaffected; the in-air dead zone (TOP 64) is unchanged. Looking up (64 px) still exists. Nothing Pepper
needs is hidden. PASS.

## Fixes, round 3 (polish, in order)

1. Closed-kind chimneys in the brick ramp (as the start house), 10 px with the 2 px cap, so they read as
   chimneys and not posts (closed1, 2, 4, 7, 13, 16, 22 and the bakery).
2. Mid row chimneys 24 px tall (not 38), 2 px cap.
3. When the painted sky lands: its far skyline lower and simpler than the River Walk one (tops only), and the
   spire parked at an x where its cross never lands on a low-row or mid-row roofline at any tier (or its drift
   off in this level).

VERDICT: PASS. The high road is not messy any more; I would show every screen to the owner as finished, with the
three polish items above as the next small round.
