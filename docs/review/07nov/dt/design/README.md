# Downtown (tall): design review and redesign options, 7 Nov (track dt, Phase 1, no art changed)

The owner, 7 Nov: "that level with the buildings, balconies etc. looks extremely messy, we need some really serious
work there" and, of the high road pieces, "these look ok, but the way the level works is terrible. I really don't
understand what's going on in this scene. We need some concept art first."

This folder: the diagnosis (section 1 and 2), two structural options (3), greybox frames of the key screens for
each (`greybox/`), the as-is frames they answer (`asis/`), and a concept brief per key screen (4) for the
producer's Artlist run. Nothing in the game changed; `tools/greybox_dt_07nov.py` draws the greyboxes.

Measured today (main at 5f30120): autopilot GOOD GIRL! in 56.2 s, 65/102 bones, 3/5 secrets, no heart lost (the
beat sheet's 56.9 s). Route map: `routes_asis.png`. Every screen at every tier: `asis/tiers_screens_*.png`
(cam y 0, 120 and 240 stacked per screen, 2x).

## 1 What a player sees, screen by screen

World y: the street at 424, the high road 232 to 280, the middle tier 328 to 348. Frames: `asis/`.

| # | Screen (x) | What is there | Why it cannot be read |
| --- | --- | --- | --- |
| 1 | Old town lane (0-320) | The start house (true scale, orange, 46 px/m) beside the mid row's small houses (23 px/m, lighter) with a thin square floor between them and the street. | Two scales side by side on the first screen. The small houses stand 30 px up on a "square" that is a 10 px grey band: they read as a wall of small windows right behind Pepper, not as houses across a square. The mid row also slides at 0.6 when the camera rises, so the wall moves while the awnings and signs stay. |
| 2-3 | Cafe, market (320-968) | Parasols, tables, the shop sign, the stall and awnings on the street; the same small-house wall behind. | The street pieces are fine. The wall of windows behind them is flat, every window identical, no door at Pepper's scale, no sky until the camera is at the top tier. Nothing tells a child the sign is the one gold thing to reach. |
| 4 | Bakery row (968-1288) | The springy awnings, the crate wall, the bakery (true scale, styled front), its sign at 304, the balcony at 272 (way up A). | From the street the balcony is off screen above; from the bakery sign Pepper sees a balcony hung on a 4-storey wall with identical windows above and beside it. Nothing says "this is the way up". The old plaza houses behind are gone (decision 2a), so the bakery stands beside a half-scale street. |
| 5 | The plaza (1288-1608) | The statue with the cat, the loggia at 280 right over it, the tub, the pedestal, the parasol; walls of windows up to y 0 at every tier. | The loggia is a dark arcade strip stuck on a wall at first-floor height. The balconies 56/64 (approved) hang beside it at other heights (328-348, the middle tier) and look the same as the loggia and the galleries. Which of the five iron things can she stand on? All of them, but a child cannot tell; the decorative window rails (`town_window_rail`) look like them too. No sky at any tier (`asis/sweep_downtown_y000_x1600.png`: cam y 0 is still wall). |
| 6 | The fountain (1608-1928) | The guild house's stepped "roof" (272 up to 244), the chimney with the golden bone at 200, the two galleries at 256 with the 48 px gap, the fountain's top tier at 344, the basin and rims at the street, three balconies at 336-344. | The root of "I don't understand what's going on": the stepped gable is a ROOF shape drawn in front of a wall that carries on three storeys above it, and the chimney is an urn standing on a parapet in front of windows. The galleries are balustrades floating on the wall with nothing under them (no corbels, no arches), 30 px above decorative balconies that look the same. The fountain's bowl stands in front of a shop window; the basin is a trench in the pavement pressed against the house, so it reads as part of the building ("looks weird on top of the buildings"). |
| 7 | Tram street (1928-2136) | The tram shed (approved), the kiosk, the shelter (approved), the dormer at 264, the ledges at 248 and 264, the vintage tram behind. | The "dormer" and "roof ledges" are 56 px shelves at window-sill height on a 4-storey wall, each next to an identical decorative window rail. A dormer in the middle of a facade is not a dormer. Two tiers of balconies, the shelter and the shed roof all at different heights with no rule. |
| 8 | Flower market (2136-2456) | The geese, the tub, table and parasol, the springy window awning at 272, the flower roof at 232, the last ledge at 248, the lamp. | The flower roof is a window box ledge; the awning she must bounce on looks like the shop awnings below that she only walks under. The bounce up to 232 lands on a shelf with wall above and below. |
| 9 | The canal (2456-2784) | The footbridge at 272 from the last ledge to the crates, the canal, the mid row visible through the gap. | The best screen: sky, the lighter houses behind, one big readable piece (the iron bridge) over a clear hazard (water). This is what the whole high road should feel like. |
| 10-11 | Flooded square, river stairs (2784-3520) | The bounce chain, the gateway, the fast tram, Mia, the spire. | The street works. Above it the same half-scale wall as on screens 1-3 (true scale again only at the gateway). |

Summary of the visual facts, measured on the frames:
- Walkable surfaces on the high road: 21 pieces between x 1270 and 2640, 8 to 160 px wide, at 7 different heights (200, 232, 244-272 steps, 248, 256, 264, 272, 280, 304), drawn in 6 different vocabularies (sign, balcony, loggia, gable steps, chimney, balustrade, dormer, ledge, awning, flower box, bridge). Decorative pieces at the same heights and in the same vocabulary: 7 balconies (328-348), window rails under every upper window, lanterns, flower boxes.
- No sky on screens 5 to 8 at any camera height: the true-scale fronts run from the street past the top of the world. The "roofs of the old town" in the beat sheet are at 3.1 to 4.2 m above the street, the first floor of 9 m facades. There are no roofs.
- Scale: 46 px/m fronts on screens 4-9 and 10 (the gateway), 23 px/m fronts on screens 1-3 and 9-11, both touching the same street (the mid row is 30 px up, which reads as a kerb, not a square).
- Nothing on the high road is visibly supported: the galleries and the loggia hang on the wall without corbels or arches; the chimney stands on a parapet.

## 2 Root causes (few, big)

1. **The fiction and the scale contradict each other.** The beat sheet says "the roofs of the old town"; decision 2a (6 Nov) put true-scale 3-4 storey fronts under the high road. At 46 px/m a 3 storey house is 430 px: taller than the 480 px world. So the high road at 232-280 became shelves on the first floor of walls that never end, and every roof-shaped piece (gable, chimney, dormer, flower roof) is a roof in the middle of a facade. Nothing can fix this at the pixel level.
2. **No single language for "you can stand here".** Walkable pieces borrow the look of decoration (balconies, rails, awnings, flower boxes) and decoration borrows theirs. The approved balconies are both a play piece (the middle tier) and a wall ornament. Lion King: the walkable rock has one look everywhere and the background never has it.
3. **No silhouettes, no sky.** Big readable shapes against sky are what make a Lion King screen; here every screen at the high tier is a flat wall of identical windows, so the route is a thin line of small boxes on a texture. The only screen that works (9, the canal) is the one with sky and one big piece.
4. **Two scales on one street** (screens 1-3, 9-11 against 4-9), and a vertical parallax (0.6) that moves the "wall" the mid row makes while the street pieces stay.
5. **Set pieces pressed into the walls.** The fountain, the statue, the kiosk and the shelter stand against facades instead of in a square, so they read as parts of the building.

What is fine and stays: the street itself (cobbles, kerb, the front band), the street set pieces and the bounce beats, the approved pieces (styled front method, town_door, shelter, kiosk, parasols, pedestal, sign, stall, stop sign, tub, tramshed96, crate front, balconies 56/64 as pieces, the spire, the vintage tram), the beats and the ball story, the length (56 s autopilot, par 85), Pepper's moves, every box she stands on (both options keep every play box at its x and y, so physics, curve and the autopilot do not change).

## 3 Two structural options

Both keep: every play box of the map (same x, y, widths: the jumps in the beat sheet stay proven), the four beats, the
cat on the ball on the statue's arm barked from the loggia, the two ways up, the golden bone on the chimney box, the
lamps, the length. Both remove: every decorative piece in the high road's band (y 220 to 300) that is not the route;
the middle tier balconies as wall ornaments (see each option); the fountain's bowl in front of a window.

### Option A: the roofs of the low row (recommended)

The street is lined with LOW true-scale buildings: one-storey market pavilions and sheds, a two-storey bakery, an
open cafe arcade (the loggia), the guild hall with its tall stepped gable, the tram shed, the flower hall (a glass
market hall), a canal house. Their eaves are at 3 to 4 m (y 232-286), exactly where the high road is today. **The
high road is their roofs**: tile slopes and lead flats, ridges, a dormer on the tram shed, the chimney on the guild
hall's ridge, the flower hall's roof garden, the footbridge from the canal house's roof. Behind and above them, the
tall old-town houses stand on the mid row (23 px/m, scroll 0.5, a step lighter, 30 px up across the square, as now),
their rooflines at screen y 30-100 at the roof tier, and the sky and the spire above. True-scale tall walls appear
nowhere; the approved styled-front parts build the low row's fronts (the same doors, shop windows, cornices,
shutters, one storey instead of four) and, stamped at half size, the mid row.

- One language: a roof Pepper walks on is red-brown tile or grey lead with a 1 px ink outline and a lit edge; a
  parapet or ridge behind her where she walks on a flat. Decoration never uses tile or lead.
- The route is the skyline: from the bakery's sign under its eave up onto its wing's terrace, the arcade's lead roof
  over the statue (bark the cat from its edge), the guild hall's gable steps up to the chimney, the two pavilion roofs
  flanking the fountain (the gap is the fountain's column between them), the tram shed's roof and dormer, the kiosk
  and shelter houses' flat roofs, the flower hall's awning and roof garden, the canal house, the bridge. Every drop
  lands on the street, as today.
- Scale: one scale on the street (46 px/m, the low row), one on the mid row (23 px/m), never touching. The start
  house becomes a two-storey house like the bakery.
- The middle tier (balconies at 328-348) becomes the pavilions' and the arcade's own canopies and the statue's arm:
  part of the building's shape, under its roof, not hung on a wall.
- Set pieces stand free in the square: the fountain between the two pavilions with sky over its column, the statue in
  front of the arcade's middle arch, the kiosk and shelter in front of their own houses.
- Cost: new roof art for 9 low buildings (built from parts: tile course, ridge, gutter, dormer, chimney, parapet:
  one kit), the fronts re-stamped one storey high from the approved parts, the mid row rebuilt from the same parts
  at half size (replaces town_facades, "needs total rework"), no play box moved.
- Open point for the owner: BIBLE "taller than the viewport" says back-layer buildings never show their top. In A
  the low row's roofs are play pieces (obstacles, outlined) and the mid row's roofs are seen at the roof tier only.
  The rule holds at the street tier; at the roof tier the sky is the point. Needs his yes.

### Option B: the portico street

The tall true-scale fronts stay the whole street long (the closed street, `H.CLOSED_STREET = true`, so one scale
everywhere), and the high road is ONE thing: a continuous stone PORTICO along the houses, round arches on granite
piers over the shop fronts, its top a flat walk with a low parapet, at the heights the boxes have today (the loggia
280, the bakery's 304 and 272, the guild house's porch rising in steps to a landing with a lantern, the fountain's
flanks a storey higher at 256, the tram street's pieces at 264 and 248, the flower hall's 232, the bridge joining the
portico's end across the canal). Pepper walks on the portico; the walls above it are quiet: windows only, no
balconies or rails in the band y 200-300, iron balconies only from the second floor up and smaller.

- One language: granite coping with a 1 px ink outline and a lit top over arches; anything walkable is on arches or
  on the bridge. Decoration never has arches or coping.
- The middle tier is cut (its 5 balcony boxes become decoration under the portico or go); the ROOFTOPS secret moves
  onto the portico.
- The route reads as a line of stone along the street with gaps (the fountain, the canal) and steps up (the guild
  porch, the flanks).
- Cost: lower than A (the approved fronts stay, one portico kit of 4 parts: pier, arch, coping, parapet, plus the
  guild porch), but the high tier is still a wall of windows at every camera height: the cam y 0 frames stay wall.
  Less Lion King, more consistent than today.

### Which one

A. It is the beat sheet's own story (roofs, a dog on the roofs, the hints say CLIMB UP), it gives every screen a
skyline and sky, it puts the approved roof-vocabulary pieces (gable, chimney, dormer, flower roof) on roofs at last,
and it ends the two-scale street. B is the safe fallback if the owner wants to keep the tall fronts as they stand.

### Greybox frames (`greybox/`, 320x240 and 3x; colours: sky, lighter mid row, warm plaster = decoration, red tile
or grey stone with ink = walkable, blue = water, orange line = the high road, gold = the golden bone)

| Screen | As is | A | B |
| --- | --- | --- | --- |
| 4-5 the bakery and the plaza, roof tier (cam 1240, 100) | asis_1_plaza | A1_plaza_roofs | B1_plaza_portico |
| 6 the guild hall and the fountain, roof tier (cam 1580, 90) | asis_2_guild | A2_guild_fountain_roofs | B2_guild_fountain_portico |
| 7-8 the tram street and the flower hall, roof tier (cam 2060, 90) | asis_3_tram | A3_tram_flower_roofs | B3_tram_flower_portico |
| 5-6 the plaza at the street (cam 1420, 240) | asis_4_street | A4_plaza_street | B4_plaza_street |

The as-is greyboxes draw the real map boxes by role: they show how thin the walkable pieces are against the walls.

## 4 Concept briefs (Artlist, by the producer; references only, never cut)

Style for all: 320x240 frame composition, flat clear shapes, Lion King 1994 Mega Drive spirit (big readable masses,
one strong silhouette line, decoration quieter than the route), late morning light from the upper left, full local
colour, Stockholm old town (Gamla stan: ochre, oxblood, cream plaster, red clay tile and grey lead roofs, granite).
No text, no logos, no haze or mist, no people. Pepper (a black Labrador) stands where the greybox puts her, the same
size. The greybox frame is the base (the geometry is binding: what is walkable, at what height); the as-is frame
beside it gives the existing palette and the approved street pieces.

**A1 (base `greybox/A1_plaza_roofs.png`, palette ref `asis/sweep_downtown_y120_x1280.png`).** Paint the roofs of
a low old-town row seen straight from the front at the dog's height: left, a two-storey bakery with a steep red
tile roof and a stepped gable, a wooden sign under its eave; right of it a lower wing with a flat lead roof and a
knee-high stone parapet behind the dog, who stands on that lead flat; then an open cafe arcade of three round
arches, its flat lead roof with a stone coping being the walkway, a bronze statue on a pedestal in front of the
middle arch with a cat on its arm. Behind everything, a row of tall pale old-town houses a step lighter and half
the size, with their own gables and chimneys against a blue sky with two flat clouds. The eye should read: dog on
the roofs, the way goes right along the rooftops, the cat is right under the arcade's edge.

**A2 (base `greybox/A2_guild_fountain_roofs.png`, palette ref `asis/sweep_downtown_y120_x1600.png`).** The
guild hall: a one-storey granite hall with a tall stepped gable roof of red tile, its steps big enough for a dog to
walk up, a brick chimney with a stone cap on the ridge (the golden bone sits on it); then the fountain square: two
one-storey market pavilions with flat lead roofs and low parapets flanking a stone fountain whose column and bowl
stand free between them with sky above, water in a granite basin at the street. The dog walks up the gable's
steps. The pavilions' canopies are part of their fronts, not hung balconies. Tall pale houses behind, sky above.
The eye should read: up the gable to the chimney, across the two pavilion roofs, the gap between them is the
fountain.

**A3 (base `greybox/A3_tram_flower_roofs.png`, palette ref `asis/sweep_downtown_y120_x1920.png` and
`asis/sweep_downtown_y120_x2240.png`).** A tram street's roofs: a low tram shed with a wide gate and a flat roof
with a dormer, a kiosk house and a shelter house with flat lead roofs and parapets (the dog stands on the shelter
house's roof), then a glass flower hall, taller, with a striped awning over its door that is springy and a roof
garden with flower boxes on its top, then a small canal house and the start of an iron footbridge. Tall pale houses
behind, sky above. The eye should read: a row of rooftops stepping up and down, the awning is the one soft thing
to bounce on, the garden on the roof is the high point.

**A4 (base `greybox/A4_plaza_street.png`, palette ref `asis/sweep_downtown_y240_x1280.png`).** The same plaza
from the street: the dog on the cobbles by a wooden tub, the three-arch cafe arcade with its lead roof edge at the
top of the frame, the bronze statue on its granite pedestal with the cat holding a red ball on its arm, the guild
hall's granite door and the foot of its gable, the first market pavilion and the fountain's basin at the right,
the lighter tall houses showing above the arcade's roof. The eye should read: the arcade's roof is where the dog
must get to, the statue is the stair.

**B1 (base `greybox/B1_plaza_portico.png`, palette ref `asis/sweep_downtown_y120_x1280.png`).** Tall ochre and
cream old-town fronts with calm sash windows, and along their ground floor a continuous granite portico of round
arches on piers, its flat top a walkway with a low parapet; the dog walks on it; the portico steps up from the
bakery's end to a loggia section over a bronze statue with a cat on its arm; no balconies or rails on the walls
near the walkway. The eye should read: one stone line to walk along, the walls are only a backdrop.

**B2 (base `greybox/B2_guild_fountain_portico.png`, palette ref `asis/sweep_downtown_y120_x1600.png`).** The
same portico rising in granite steps to the guild house's porch landing with a tall stone lantern on it (the golden
bone's perch), then two portico sections a storey higher flanking the fountain with a gap over its column, the
basin at the street. The eye should read: steps up, the lantern, across the two high sections.

The producer picks 2 variants per brief; the owner picks a direction (A or B) on the board, then Phase 2 (the
level layout, the facades and roofs rebuilt from parts, the basin and jets, the sky) follows that pick.

## 5 Numbers and checks

- Autopilot today: 56.2 s, 65/102 bones, 3/5 secrets, no heart lost. Both options keep every play box, so the
  curve, physics and flow do not change in Phase 2 until pieces are redrawn; then the usual checks.
- Phase 1 changed no game file: `tools/greybox_dt_07nov.py` (new) and this folder only.

## 6 Questions for the owner

1. A or B (or A's roofs with B's portico on the plaza only).
2. In A, may the roofs of the low row and of the mid row be on screen at the roof tier (the BIBLE "taller than the
   viewport" rule for back buildings would hold only at the street tier)?
3. In A, the start house (screen 1) becomes a two-storey house with a roof; its approved ground floor (town_door)
   stays. Yes?
4. The middle tier (the old Downtown secret route of balconies): A keeps it as the pavilions' canopies, B cuts it.
