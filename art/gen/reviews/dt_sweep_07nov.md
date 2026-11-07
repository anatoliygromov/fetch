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
