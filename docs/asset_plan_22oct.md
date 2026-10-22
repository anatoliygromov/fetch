# FETCH! asset plan (round 5, 22 Oct 2026)

A plan only: nothing was generated and no credits were spent. SpriteCook was queried with free, read-only calls
(balance, models, projects, presets, recent assets). Balance: **1,486 credits** (subscription, tier Adventurer,
0 top-up credits). SpriteCook has no projects and no presets yet.

Sources read: the repo at `/home/claude/fetch` (branch `round1`: `riverwalk/art/`, `riverwalk/level/*.lua`,
`maps/*.tmx`, all beat sheets, `docs/progression.md`, `CHANGELOG.md`, `tools/build_*.py`, `tools/make_*.py`,
`source_sheets/`, `source_scenery/`), the project docs (`claude/all-assets.md`, `levels-v2.md`,
`spritecook-pipeline.md`, `lionking-look.md`, `fetch-game-notes.md`, `riverwalk-handoff.md`, `game-notes.md`,
`title-and-plan-22oct.md`, `agents-round3-22oct.md`) and the doc "FETCH! levels and release plan" (the 10 levels).
`/home/claude/out/r5-bugs/NEEDS_ART.md` did not exist when this plan was finished, so the two known bugs are folded
in here (section 1.0); merge the sweep's list into section 2 when it lands.

Level order used (new order): 1 River Walk, 2 City Park, 3 Downtown (Morning, the Christmas demo), 4 Rooftops,
5 Metro, 6 Soder Hill (Midday), 7 Building site, 8 Funfair, 9 Night Harbour, 10 Home in the storm (Evening and
night).

---

## 0. The owner's art rules (every asset is checked against these)

1. **Front-on at Pepper's height.** Props show their front plus a thin cap. No top surfaces seen from above, no side
   faces, no insides.
2. **Obstacles** (anything Pepper stands on, crawls under or is hurt by): crisp, mid-tone, own 1 px dark outline,
   on Pepper's line. Never faded.
3. **Decoration**: faded toward the level's haze (28 % in code), no outline, base behind Pepper's line (y foot - 10).
4. **Backdrops** have perspective and volume (cornices, recesses, roofs in depth, light and shadow). No line-drawn
   flat facades, no strokes: edges only by value steps.
5. **Follow the owner's 4-panel concept art** (summer waterfront, plaza, autumn park, night) and the Stockholm
   reference photos.
6. **Scale everything to Pepper.** Obstacles must not look small next to her; buildings match the screen-1 building
   (`art/scene/building.png`, 77 x 135).
7. **New scenery is shown to the owner before it goes into the build.** Old assets stay only if spotless.
8. **The dog is the star**: nothing covers Pepper (draw order and the `LOOK_CHECK` overlap test).
9. **All art at 1x game pixels**, a limited palette per level (the colour script in `look.lua`), pixel-authentic:
   no soft AI noise. Learned so far: hand-pixel small sprites at game size, import, animate at 1x; big pieces
   generated at 2 to 5x, box-filter downscaled, snapped to their own palette and outlined (obstacles only).
10. Kept from the game rules: nothing moves by itself (every vehicle and lift has someone running it), every hazard
    warns first, no transit or funfair logos (real places evoked, not named).

### The scale ruler (from `road.lua`: about 44 px per metre)

| Thing | Real size | Game px (target) | Today |
| --- | --- | --- | --- |
| Pepper (Labrador, standing) | 0.6 m at the shoulder, 1 m long | 48 x 34 frame, body box 34 x 26 | frozen |
| Mia (child) | about 1.35 m | 60 tall (66 px cells) | done |
| Adult (keeper, commuter, builder) | 1.7 m | 72 to 78 tall | keepers 80 to 82 px cells: OK |
| Cyclist on a city bike, promenade line | 1.75 m long, 1.75 m to the helmet | **about 76 x 76** | 49 x 50: **64 % of target** |
| Cyclist, near lane (closer to the camera, x 1.2) | | **about 92 x 92** | 73 x 75: 80 % of target |
| Car, near lane | 4.3 x 1.5 m (x 1.2) | 220 to 235 x 75 to 90 | 181 to 233 x 71 to 92: **scale OK** |
| Tram (Stockholm, vintage or modern) | 3.4 to 3.7 m tall | 120 to 160 tall | **105 x 34: a toy, as tall as Pepper** |
| Goose | 0.8 m | about 30 to 35 tall | 30: OK |
| Fox | 0.4 m shoulder, 0.65 m body | about 30 x 20 | code-drawn 24 x 12: too small |
| Barrel (Soder) | small keg 0.5 m | 20 to 22 | 14 x 14: small |
| Parked bike (Soder) | 1.75 m long | about 76 x 44 | 40 x 20: far too small |

Architecture is compressed on purpose (doors about 58, lamp posts 101, the screen-1 building 135): new buildings
are measured against `building.png` (window size and storey height), not against metres. People, vehicles,
animals and things Pepper interacts with use the ruler.

---

## 1. Inventory

Status key: **DONE** = in `main` v0.5 or on `round1` with no open complaint (the owner accepted v0.5 as main; an
explicit art sign-off is only recorded for the River Walk v0.1 to v0.3 pieces); **FIX** = exists but needs a fix
(why given); **CODE** = drawn in code, reads as pixel art, needs the owner's review; **GREY** = greybox boxes only;
**MISSING** = nothing exists. Noise figures are the share of opaque pixels with no same-colour neighbour (measured on
the files today; the old asset standard says under 8 %, foliage can run to 12 %). Outline figures are the share of
silhouette pixels that are dark (obstacles should be 95 % or more, decoration close to 0).

### 1.0 Known bugs that need art

| Bug | Finding | Art needed |
| --- | --- | --- |
| Cyclists and bikes too small next to Pepper | Promenade riders `cyclist1/2.png` are 49 x 50 (target about 76 x 76); road riders `road_cyclist1/2.png` 73 x 75 (target about 92 x 92). Both are also noisy (9 % and 13 %). Riders' legs do not pedal (only `make_wheels.py` rolls the wheels). | New riders at true scale, pedal loops (section 2, S2, S3). The bike hit box (48 x 26, y 158 to 184) stays; the rider's body above it is drawn before Pepper, so on a perch she is drawn over him (reads as the bike lane a step behind her line; set the wheel line at y 182). |
| Cars cropped | Code: `Rd.CAR_TOP = 192` with cars 71 to 92 px tall, so 23 to 40 px fall below the 240 px frame (riders lose 25 px). The car sprites' scale is right (about 4.3 m at 44 px/m x 1.2 for the near lane). | No new car art. Fix in code: River Walk becomes 12 x 1.5 in the plan, so let the world extend about 48 px below the road and have the camera rest low enough on the promenade to show whole cars, or draw the road band lower and the promenade higher. Do not shrink cars (it breaks the scale rule). Delete the unused half-scale `car1.png` to `car5.png` (100 x 40). |
| (found while checking) The tram is a toy | `town_tram.png` 105 x 34 is Pepper's height. A tram at scale (120 to 160 px) cannot pass under Pepper on the kiosk or shelter roofs (top y 148). | Owner decision D1 (section 6): recommended, the street hazard becomes a **cargo bike with its rider** (hit box = the cargo box, 80 x 26, unchanged; rider drawn tall like the leaf-cart keeper), and a true-scale vintage tram rides the back lane as moving decoration. The tram sheds become courtyard gates the cargo bike rides into (same art, same `depot` code). |

### 1.1 Shared assets

| Asset | File / where | Status |
| --- | --- | --- |
| Pepper, 14 clips | `art/pepper.png` (11 colours, 7.4 % noise, outline 100 %) | DONE, frozen (PEPPER UNCHANGED) |
| Mia, idle / wave / call / cheer / pet | `art/girl.png` (66 px cells) | DONE |
| Mia, throw | faked in `bonus.lua` from wave + cheer | FIX (nice to have): a real throw clip for Fetch Frenzy |
| Mia, walk; startle (storm); at the door / window | none | MISSING (Soder stairs, Metro, Storm) |
| Talk portraits (Mia, Pepper) | `art/portraits/` | DONE |
| Ball | `art/ball.png` 6 x 6 | DONE |
| Bones, golden bone | `bone.png`, `bone_gold.png` 11 x 6 | DONE |
| Lamp post, lit lamp (checkpoint) | `lamp_post.png` + code recolour | DONE |
| Warning sign (yellow diamond) | code | CODE, fine |
| Bonus round: stick 12 x 3, frisbee 12 x 5 | code, a few hand-placed pixels | FIX: proper hand-pixel sprites with spin / tilt frames |
| Bonus round lawn | City Park art | DONE |
| Springy awnings and parasols: coil springs | red coils drawn in code on the older town awning art | FIX: hand-pixel spring brackets and a 3-frame dip (open item since 19 Oct) |
| Steam puffs, vent caps (Rooftops) | `roofs.lua`, outlined blobs, cap states | CODE, review; keep procedural |
| Loose tiles, crumbling planks | code boxes | GREY: hand-pixel |
| Dust, splash, bone pop | `extras.lua` | CODE, DONE |
| Night darkness and light pools | `night.lua` | CODE, DONE |
| Rain, lightning, puddle splashes | none | MISSING (storm) |
| Title screen | the 19 Oct title (restored) | DONE as is; owner: no code-drawn redraw; a new one only by a human pixel artist or SpriteCook with credits agreed (not budgeted) |

### 1.2 Critters and people

| Asset | Status |
| --- | --- |
| Goose: walk 8, hiss 6, fly 8 (34 px cells) | DONE; FIX (cheap): 14.5 % noise, clean pass in code |
| Gull: flap 6 (26 px cells) | DONE; FIX (cheap): 16.4 % noise, clean pass |
| Magpie (24 px, code-pixeled at game size) | DONE (CODE) |
| Cat (Abyssinian): idle / leap / run | DONE. Note: sits about 30 px tall, roughly 1.7x a real cat next to Pepper; reads well, owner to confirm |
| Gull's nest (Rooftops), magpie's nest (City Park tall) | CODE (twigs); hand-pixel polish |
| Fox: sit, run, peek, snatch (Night Harbour) | GREY (code-drawn 24 x 12, too small): MISSING as art |
| Pigeons (Sergels torg, quay), squirrel (treetops) | MISSING, optional life |
| Park keepers: leaf cart (8 frames), winch (8 frames) | DONE (keeper sheet 9.1 % noise: clean pass) |
| Rower (rowing boat, 8 frames) | DONE |
| Promenade and road cyclists | FIX: scale (see 1.0) |
| Cargo bike rider (Downtown hazard, if D1 = A) | MISSING |
| Metro: commuters (walk, tap card), booth attendant (wave), traveller (lets go of a suitcase), cleaner on a floor scrubber, wagon driver | MISSING |
| Rooftops: sauna guest (throws water: the twist), baker / laundry / dishwasher (implied by the vents) | MISSING (only the sauna guest is worth drawing) |
| Building site: builders, crane operator, lift operator (code operator in `lift.lua`) | MISSING |
| Funfair: ride operators, crowd (decoration) | MISSING |

### 1.3 Vehicles and big movers

| Asset | Status |
| --- | --- |
| Road cars x5 (`road_car1-5.png`) | DONE (scale OK); crop is a code bug |
| `car1.png` to `car5.png` (100 x 40) | unused leftovers at half scale: delete |
| Commuter ferry (252 x 93) | DONE (outline 75 %: check the deck edge Pepper stands on) |
| Rowing boats, duck boat (front-on), pontoon, rope | DONE |
| Leaf cart (with keeper) | DONE (`park_cart.png` alone: 21.6 % noise, check it is unused) |
| Tram (105 x 34) | FIX: scale (D1) |
| Tram sheds 70 / 96 | DONE; FIX (cheap): 9 to 10 % noise; renamed courtyard gates if D1 = A |
| Night: rowboats and small boats with bow lanterns | GREY: recolour the rowing boat |
| Metro: work wagon with cab, passenger train (decoration), floor scrubber, suitcase | MISSING |
| Building site: tower crane (landmark), crane loads, goods lifts, conveyor | MISSING (lifts: CODE in lab_tall) |
| Funfair: Ferris wheel (landmark, turning gondolas), carousel, swing ride, bouncy castle | MISSING |
| Escalators, moving walkways, ticket gates, screen doors (Metro) | MISSING |

### 1.4 Level by level

**Level 1, River Walk (summer morning; 12 x 1.5 in the plan; flat 12-screen level built with art)**

| Asset | Status |
| --- | --- |
| Sky bands, clouds 1 to 8, skyline, far shore + bridge, river (row-scrolled) | DONE |
| Pavement, kerb, road, manholes, drains | DONE |
| Bench, bin, pot, lamp, flower box front, grit box front, square planter, railings, kennel, kiosks KAFFE / GLASS, striped awnings | DONE; bin shows a slim side face (FIX by hand, mild) |
| Screen-1 building, gable, cafe, trees (tree, tree_far, tree_near) | DONE; FIX (cheap): the trees are decoration but 64 to 67 % of their edge is dark and they are noisy (11 to 21 %): recolour edge pixels, clean pass |
| Ferry, pier (bridge abutment), piles, pontoon, rowing boats, jetty, gulls | DONE; jetty 16.1 % noise: clean pass |
| Road traffic | FIX: cyclists scale, cars crop (1.0) |
| Tall addition: quay steps down to the pontoons | MISSING (map not drawn yet) |
| Tall addition: the walk up over the bridge (deck, balustrade, span between abutments) | MISSING (the abutment exists) |

**Level 2, City Park (golden autumn afternoon script; tall version 9 x 2)**

| Asset | Status |
| --- | --- |
| Far city, tree line, near trees, path and grass, gate, leaf piles, log, bench, bin, hedge, pond, stepping stones, duck boat (front), picnic table (front), oak, slide, frame, swings, willows, winch keeper, cart keeper | DONE |
| Hedge (12.8 %), leaves (21 %), log (9.8 %), willows (11 %) | FIX (cheap): clean pass; foliage may keep some texture |
| `park_tree1.png` (decoration, 56 % dark edge) | FIX (cheap): drop the outline |
| Hollow log (both open ends show) | owner's call (D4); hand fix if wanted |
| Tall addition: treetop tier (branches, trunks, canopies, treetop walk and alder walk planks with rope rail, rose arbour, play tower, low bough, magpie nest) | CODE from approved art (`Sc.drawTreetops`): needs the owner's review; art only if rejected |
| Tall addition: sky above the old horizon | CODE, DONE |

**Level 3, Downtown (bright midday script; tall version 11 x 2)**

| Asset | Status |
| --- | --- |
| Far roofs and spires, crates, cafe tables (front), parasols, shop sign, stall, awnings, tub, pedestal, statue, fountain (rims, bowl, tier, spout), kiosk, shelter, RIVER sign, door, bollards, three plaza houses, ground | DONE |
| Near facades strip `town_facades.png` (225 x 114) | FIX: reads as flat, line-drawn fronts (rule 4); needs volume (cornices, depth, cast shadow) |
| `town_roofs.png` (decoration, 37 % dark edge) | FIX (cheap): drop the outline |
| Pedestal (obstacle, 38 % outline), house2 (balconies are ledges, 52 %) | FIX (cheap): outline in code |
| Statue (14.6 %), stall (11.2 %), crates (11.7 %), tram sheds (10 %) | FIX (cheap): clean pass |
| Tram | FIX: D1 |
| Springy awning / parasol springs | FIX: hand-pixel |
| Tall additions (downtown_tall, all greybox): the loggia over the statue, the guild house's pitched roof (front-on gable, one-way steps), its chimney (golden bone), the gallery in two halves, the dormer and roof ledges, the springy window awning, the flower roof, the footbridge over the canal, Riddarholmen's spire (landmark, 32 x 400), tall house fronts that carry all of it | GREY: MISSING as art |

**Level 4, Rooftops (noon; 12 x 5, greybox)** GREY throughout: far city seen from above, mid roofscape, flat roof
edges and parapets, wall faces between tiers (96 px), stairwell housings, pitched roofs R1 and R2 (gable ends),
the market hall's glass roof R3, the sweep's chimney block, chimney pots (golden bone), the light well and skylight
dip, roof garden with planters and its goose (goose DONE), the balcony, the pigeon loft, the roof walkway, the roof
bar with its springy awning, the water tank, the roof terrace and roof cafe (Mia), the copper roof (verdigris), the
sauna hut, the nest chimney with the gull's nest (landmark; far copy CODE), the street cafe at the start. Steam
puffs and vent caps CODE. Loose tiles GREY.

**Level 5, Metro (early afternoon; 8 x 3, paper map only, not wired)** MISSING throughout: Sergels torg with the
glass obelisk (row 1 back layer), the ticket hall, T-Centralen's blue painted cave (row 2), Stockholm City's
platform wall (row 3), the tunnel, Odenplan's round clock (landmark), escalators A / B / C (steps, balustrade, comb
plates), two walkways, ticket gates and the booth, ticket machine, banner, light rails, station clock (golden bone),
a kiosk (no brand), vending machine, information pillar, benches, flower tub, rock shelves and the vent duct, screen
doors, the work wagon (deck 96 px, end rails, cab with lamp), tunnel signs, the passenger train (decoration), people
(1.2), the suitcase and the floor scrubber.

**Level 6, Soder Hill (afternoon; 16 x 2, greybox)** GREY throughout: the Soder street backdrop (steep plaster
houses stepping down the hill), the view over the water, cobbles and stone stair flights, open cellar hatches, the
barrel (14 x 14, 4 rolling frames) and its stacks, the terrace deck, hanging cafe signs on brackets, the low striped
awning, parked bikes (40 x 20: scale problem, D3), the fruit cart, the low arch (grand), balconies 64 and 180 wide,
bollards, the quay railing, Mia's stairs. Crates, cafe tables and parasols can reuse Downtown's (front-on versions).

**Level 7, Building site (late afternoon; 5 x 5, nothing built, no beat sheet yet)** MISSING: far skyline, the
neighbouring buildings and other cranes, the tower crane (landmark: mast, jib, cab, counterweight), crane loads
(pallet of bricks, skip with the ball, steel beam), scaffolding (tubes, one-way boards, netting), goods lifts with
motor houses, conveyor belt, the building shell (concrete floors, columns, half walls), site props (cement mixer,
barriers, cones, site hut, sand pile, pallets), builders and the crane operator.

**Level 8, Funfair (evening; 10 x 3, nothing built, no beat sheet yet)** MISSING: evening sky over the water and
the hill, ride silhouettes with lights (mid layer), the Ferris wheel (landmark: rim, spokes, hub, A-frame legs,
gondolas as turning platforms), the carousel (horses rising and falling), the swing ride, the bouncy castle
(`bounce`), stalls (candy floss, games), light strings, operators, crowd (decoration). No logos.

**Level 9, Night Harbour (night; 14 x 2, greybox with code darkness and fox)** GREY: night sky and moon (CODE),
warehouses and harbour cranes (backdrop), quay edge and granite tiles, night water, crumbling planks, rowboats and
small boats with lanterns, lantern posts, mooring posts, the net shed, the fish shed with roof, fish crates (stack,
tower), the tarp over a beached boat, the low jetty, Mia's house (door, warm windows, porch light), the fox.

**Level 10, Home in the storm (night thunderstorm; 6 x 4 down then up, nothing built, no beat sheet yet)** MISSING:
storm sky (bands + lightning flashes), the courtyard's building backs with lit windows, courtyard props (bike shed,
recycling bins, washing lines, sandbox), cellar steps, the cellar (storage cages, boiler, pipes), the stairwell
(flights, landings, banister), Mia's front door, rain, puddle splashes, lightning bolts, Mia's startle and door
clips.

---

## 2. Production list for every missing or fixable asset

Prices (SpriteCook model catalogue, read today): **Nano Banana 2.1** (`gemini-nano-banana-2.1`, the house model)
12 credits per 1K image, 18 per 2K, up to 14 reference images, no transparency (needs a background key or
`remove_background`); **GPT 2.5 Flare / Sunburst** 8 per 1K square at medium, but a non-square 1K is billed as 2K
(14) and **every reference image adds 8 credits**, so a style-locked Flare call (style sheet + Pepper) costs
8 + 16 = 24, dearer than Nano Banana's 24 for two variations; use Flare only where native transparency on a single
unreferenced piece saves a cleanup; **Pixel Engine Image** 6 per image, exact 16 to 128 px output, transparency,
but **no reference images** (so no style lock); **pixel-engine-v1.5 animation** about 26 per clip (CHANGELOG:
cat 3 clips = 78, keeper walk 26).

Unit costs used below: a still = one Nano Banana 2.1 call with **2 variations**: 1K = 2 x 12 = **24**, 2K = 2 x 18 =
**36**. Reserve = one retry, held back and only spent if the owner rejects both variations. Imports of 1x sprites
(`import_asset` / `create_asset_upload`) are budgeted at 0: verify the balance before and after the first upload
(an October note says uploads once seemed to cost credits).

Columns: size in game px; frames; layer (far / mid / back = decoration behind Pepper's line / play / front);
role (OBS obstacle, DEC decoration, CHR character, FX effect); method; credits as expected + reserve; milestone.

### 2.1 Shared and cross-level fixes

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | Chapter 1 style sheet | 640 x 270 sheet | | | ref | Composite in code from approved 1x art (Pepper, Mia, bench, bin, lamp, flower box, screen-1 building crop, kiosk, River Walk sky band, the three level palettes as swatches), upload once | 0 | M1 |
| S2 | Promenade cyclists x2 (woman red coat, white helmet, pale blue bike; man green jacket, grey helmet, black bike) | 76 x 76 | still + pedal loop 8 each | play | OBS (hazard) | NB 2.1 1K, both riders in one image at about 4x; box-filter to 76; snap to 14 colours; outline; import 1x; pixel-engine pedal loop; wheels keep `make_wheels.py` spokes | 24 + 2 x 26 = 76, reserve 24 | M1 |
| S3 | Road (near-lane) cyclists x2 | 92 x 92 | pedal loop 8 each | front of road | DEC (scenery traffic, outlined like the cars) | Same S2 source box-filtered to 92 (no new still); import; pedal loops | 2 x 26 = 52 | M1 |
| S4 | Cars crop | | | | | Code (1.0); delete `car1-5.png` | 0 | M1 |
| S5 | Mia throw | 66 px cells | 8 | play | CHR | Animate from Mia's standing pose 7ca7be0e: "wind up, ball in the right hand behind the head, step, arm forward, release, follow through, settle"; feet planted; hood stays up | 26 | M1 |
| S6 | Spring brackets for springy awnings and parasols | 6 x 10 coil, 3 dip frames | 3 | play | OBS | Hand-pixel at 1x in the awning's own colours (iron dark, highlight) | 0 | M1 |
| S7 | Stick, frisbee | 14 x 4 (4 spin frames), 12 x 5 (3 tilt frames) | 4, 3 | play | item | Hand-pixel | 0 | M1 |
| S8 | Clean pass on noisy approved art (goose, gull, jetty, tram sheds, statue, stall, crates, hedge, log, keeper sheet) | as is | as is | | | One script (`tools/clean_scenery.py`, Pepper's `clean.py` rules: palette snap, specks under 3 px merged, no new colours); before / after sheet for the owner | 0 | M1 |
| S9 | Outline rule pass: drop dark edges on decoration (tree, tree_far, park_tree1, town_roofs), add 1 px outline to obstacles (town_pedestal, town_house2 balconies, ferry deck edge, rail_seg) | as is | | | | Code, edge recolour to the darkest neighbouring shade (decoration) or the outline ink (obstacles) | 0 | M1 |
| S10 | Bin side face (River Walk), hollow log ends (if D4 says so) | as is | | play | OBS | Hand edit, `make_front_view.py` style | 0 | M1 |
| S11 | Mia walk | 66 px cells | 8 | play | CHR | Animate from 7ca7be0e, "walks in place, hood up, arms swing a little" | 26 | M2 |
| S12 | Loose tile / crumbling plank kit | 24 x 6, 32 x 6, 40 x 6 | rest, 3 shake, 2 fall, ghost | play | OBS | Hand-pixel (roof tile row and old plank in each level's palette) | 0 | M2 |
| S13 | Vent caps | 16 x 8 | rest / warn / open | play | OBS | Hand-pixel over the code cap | 0 | M2 |
| S14 | Rain, lightning bolts (3 shapes), puddle splash | 1 x 6 streaks; bolts 24 x 120; splash 8 x 4 | 3 to 4 | front / far | FX | Procedural rain; hand-pixel bolts and splashes; flashes as a palette step in the storm script (max 3 per second, calm option) | 0 | M3 |
| S15 | Pigeons (Sergels torg, quay), squirrel (treetops) | 14 x 10, 16 x 12 | 2 to 4 | back / play | DEC | Hand-pixel at 1x like the magpie | 0 | M2 |

### 2.2 Level 1, River Walk (M1)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RW1 | Granite quay set: steps down to the pontoons (8 px risers, front-on), quay wall tile 32 x 56, iron mooring ring, quay bollard | flights 64 x 48; tiles 32 x 56 | | play | OBS | NB 2.1 1K with `pier.png` and the River Walk props as refs; box-filter; snap to the pier's 12 colours | 24, reserve 24 | M1 (after the map) |
| RW2 | Bridge span for the walk over the bridge: deck with balustrade on top (Pepper's line), one arch, matching the abutment | 320 x 64 repeatable span | | play (deck) / back (arch) | OBS deck | NB 2.1 2K strip with `pier.png` as edit-style ref ("same granite, same balustrade"); cut balustrade columns to repeat | 36, reserve 36 | M1 (after the map) |

### 2.3 Level 2, City Park (M1)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CP1 | Treetop kit, only if the owner rejects the code dressing: the big oak's upper crown and limbs seen front-on, plank walk with rope rail, nest | crown 200 x 120; planks 64 x 10 | | back (crown) / play (limbs, planks) | DEC + OBS | NB 2.1 1K, refs `park_oak.png`, `park_tree1/2.png`, style sheet; limbs outlined, crown faded | 24, reserve 24 | M1 (conditional) |

### 2.4 Level 3, Downtown (M1)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DT1 | Cargo bike with rider (D1 = A): box bike, wooden cargo box with crates of bread, rider in a cap; bell | 96 x 76 (hit box 80 x 26 = the box and front wheel) | still + pedal loop 8 | play | OBS (hazard) | NB 2.1 1K, refs style sheet, keeper cart sheet (same people style), Pepper; box-filter, outline; animate | 24 + 26 = 50, reserve 24 | M1 |
| DT2 | Vintage Stockholm tram at true scale, back lane, moving decoration (no logos) | about 300 x 130 | wheels roll in code | back | DEC | NB 2.1 2K side view; faded like decoration | 36 | M1 (with D1 = A) |
| DT3 | Roofs kit A: loggia front (arcade, one-way top), gallery halves, guild house gable end with stepped one-way roof, chimney with pots (golden bone), dormer, roof ledges, springy window awning | loggia 120 x 48; gallery 88 / 72 x 32; gable 120 x 80; chimney 24 x 56; dormer 40 x 36; ledges 32 to 64 x 8 | | play | OBS | NB 2.1 2K sheet, refs town style sheet 36fe3255, `town_house1-3.png`, `town_awning80.png`, Pepper; box-filter each piece to its box; outline | 36, reserve 36 | M1 (if D2 = tall) |
| DT4 | Tall Gamla stan house fronts (5 storeys, ochre / red / yellow plaster, cornices, recessed windows, cast shadows) that carry the loggia, gallery and roofs; also replaces the flat near-facade look | 3 fronts, 80 to 96 x 240 | | back (faded) | DEC | NB 2.1 2K, refs `building.png` (window and storey size), town houses, owner's plaza panel | 36, reserve 36 | M1 (if D2 = tall) |
| DT5 | Near facades strip with volume (replaces `town_facades.png`) | 320 x 130 loop | | mid (0.5) | DEC | NB 2.1 2K strip, refs DT4 result + owner's plaza panel; no strokes, edges by value; tile by whole houses | 36 | M1 |
| DT6 | Footbridge over the canal (iron or timber, solid deck, rails behind Pepper) | 160 x 40 | | play | OBS | NB 2.1 1K, refs town kit | 24 | M1 (if D2 = tall) |
| DT7 | Riddarholmen spire (cast-iron openwork, landmark) | 32 x 400 | | far / back | DEC | NB 2.1 2K portrait, refs reference photo of Riddarholmskyrkan; faded | 36 | M1 (if D2 = tall) |

### 2.5 Level 4, Rooftops (M2)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RT0 | Key screen (chapter 2 style lock): one painted 320 x 240 screen of T2 with Pepper, for the owner | 320 x 240 | | | ref | NB 2.1 2K, refs chapter 1 sheet + Downtown roofs kit | 36 | M2 |
| RT1 | Far city seen from above (copper roofs, spires, City Hall tower, water) | 640 x 200 | | far (0.3, vertical parallax) | DEC | NB 2.1 2K, cut and loop | 36, reserve 36 | M2 |
| RT2 | Mid roofscape (chimney stacks, tin roofs) | 640 x 160 | | mid (0.6) | DEC | NB 2.1 2K | 36 | M2 |
| RT3 | Roof kit x3 sheets: flat roof edge + parapet tile, gable ends R1 / R2, glass roof R3, sweep's chimney block, chimney pot, water tank, planters, pigeon loft, roof walkway, copper roof edge, sauna hut, roof bar + awning, terrace table and parasol, stairwell housings | tiles 32 x 16; pieces 24 to 160 wide | | play | OBS | NB 2.1 2K x 3, refs RT0 + Downtown roofs kit | 3 x 36 = 108, reserve 36 | M2 |
| RT4 | Wall faces between tiers (plaster with windows, 3 colours, tileable) and light well walls | 64 x 96 tiles | | back | DEC | NB 2.1 2K one sheet; extra colours by palette swap in code | 36 | M2 |
| RT5 | Sauna guest (throws water on the stones: the twist) | 40 x 60 in a window | still + 1 clip | back | CHR | still in RT3's sheet; pixel-engine clip | 24 + 26 = 50 | M2 (optional) |

### 2.6 Level 5, Metro (M2)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MT0 | Key screen (row 2: the blue cave, a walkway, Pepper) | 320 x 240 | | | ref | NB 2.1 2K | 36 | M2 |
| MT1 | Sergels torg back layer with the glass obelisk | 640 x 180 | | far | DEC | NB 2.1 2K | 36 | M2 |
| MT2 | T-Centralen blue cave walls (painted bedrock, vines) | 320 x 240 tileable | | back | DEC | NB 2.1 2K | 36, reserve 36 | M2 |
| MT3 | Stockholm City platform wall | 320 x 200 | | back | DEC | NB 2.1 2K | 36 | M2 |
| MT4 | Odenplan round clock (landmark, lit) | 80 x 80 | | back | DEC | NB 2.1 1K | 24 | M2 |
| MT5 | Station furniture kit x2 sheets: ticket gates (64 tall flaps, 18 px gap), booth, ticket machine, kiosk (no brand), vending machine, bench, information pillar, screen doors, station clock, banner, light rails, rock shelves, vent duct | 16 to 96 wide | gate flaps 3, door 3 | play | OBS | NB 2.1 2K x 2, refs MT0 | 2 x 36 = 72, reserve 36 | M2 |
| MT6 | Escalator kit: balustrade, handrail, comb plates, landing lips | 16 px step, diagonal runs | steps scroll (code) | play | OBS | NB 2.1 1K; steps procedural | 24 | M2 |
| MT7 | Work wagon: flat deck 96 px, end rails 48, cab with orange lamp, driver | 160 x 70 | lamp blink, wheels (code) | play | OBS | NB 2.1 1K | 24, reserve 24 | M2 |
| MT8 | Passenger train behind the screen doors (decoration, no logos) | 480 x 150 | | back | DEC | NB 2.1 2K | 36 | M2 |
| MT9 | People sheet: commuter A, commuter B, booth attendant, traveller with suitcase, cleaner on a floor scrubber | 72 to 78 tall; scrubber 48 x 40 | | play | CHR / OBS | NB 2.1 1K, refs keeper sheet and Mia (people style) | 24, reserve 24 | M2 |
| MT10 | Clips: commuter A walk + tap, attendant wave, cleaner drive | | 8 each | play | CHR | pixel-engine from the 1x imports | 3 x 26 = 78 | M2 |
| MT11 | Suitcase (slides down the escalator), tunnel signs | 20 x 16; 32 x 24 | 2 | play | OBS | Hand-pixel | 0 | M2 |

### 2.7 Level 6, Soder Hill (M2)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SH0 | Key screen (the cafe tables screen, the slope reads) | 320 x 240 | | | ref | NB 2.1 2K | 36 | M2 |
| SH1 | Near Soder houses stepping down the hill (plaster, roofs in depth) | 640 x 200 | | mid / back | DEC | NB 2.1 2K | 36, reserve 36 | M2 |
| SH2 | Far view over the water to Gamla stan | 640 x 120 | | far | DEC | NB 2.1 2K | 36 | M2 |
| SH3 | Props kit x2 sheets: cellar hatch with open lid, hanging cafe sign + bracket, low awning + arm, terrace deck, fruit cart, low arch, iron balconies 64 / 180, bollards, quay railing tile, Mia's stairs | as in the beat sheet | | play | OBS | NB 2.1 2K x 2, refs SH0 + town kit | 2 x 36 = 72, reserve 36 | M2 |
| SH4 | Barrel and stack (D3: grow to 20 to 22 px) | 14 or 22 px | 4 roll | play | OBS | Hand-pixel | 0 | M2 |
| SH5 | Parked bikes replacement (D3: two fallen rental e-scooters, no logos, 44 x 16, true scale) | 44 x 16 | | play | OBS | Hand-pixel; true-scale parked bikes behind as decoration from S2's source | 0 | M2 |
| SH6 | Cobbles and stone stair tiles | 8 px cells | | play | OBS | Hand-pixel / recolour `town_ground.png` | 0 | M2 |
| SH7 | Crates, cafe tables, parasols | | | play | OBS | Reuse Downtown's front-on pieces after S8 | 0 | M2 |

### 2.8 Level 7, Building site (M3; art waits for the beat sheet, map and greybox)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BS0 | Key screen | 320 x 240 | | | ref | NB 2.1 2K | 36 | M3 |
| BS1 | Far skyline at late afternoon from height | 640 x 200 | | far | DEC | NB 2.1 2K | 36 | M3 |
| BS2 | Mid: neighbouring blocks, other cranes | 640 x 200 | | mid | DEC | NB 2.1 2K | 36 | M3 |
| BS3 | Tower crane: cab, jib, counterweight, hook block; mast as a hand-pixel lattice tile | cab 48 x 40; mast tile 24 x 24 | hook sway (code) | back / play | DEC + OBS (hook loads) | NB 2.1 1K for the top; lattice by hand | 24, reserve 24 | M3 |
| BS4 | Crane loads: pallet of bricks, skip, steel beam, bucket | 48 to 96 wide | | play | OBS | NB 2.1 1K sheet | 24 | M3 |
| BS5 | Goods lift cage, motor house with operator | 64 x 48; 32 x 32 | | play | OBS | NB 2.1 1K sheet | 24 | M3 |
| BS6 | Building shell (concrete slabs, columns, half walls, rebar) | tiles 64 x 96 | | play / back | OBS + DEC | NB 2.1 2K | 36, reserve 36 | M3 |
| BS7 | Site props: cement mixer, barriers, cones, site hut (perch), sand pile, pallets | 16 to 80 wide | | play | OBS | NB 2.1 2K sheet | 36 | M3 |
| BS8 | Scaffolding (tubes, boards, netting), conveyor belt | tiles | belt scroll | play | OBS | Hand-pixel tiles | 0 | M3 |
| BS9 | Builders sheet (2 builders, crane operator) + 2 clips | 72 to 78 tall | 8 | play | CHR | NB 2.1 1K + 2 x 26 | 24 + 52 = 76 | M3 |

### 2.9 Level 8, Funfair (M3; art waits for the beat sheet, map and greybox)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FF0 | Key screen | 320 x 240 | | | ref | NB 2.1 2K | 36 | M3 |
| FF1 | Far: evening sky over the water, the hill | 640 x 160 | | far | DEC | NB 2.1 2K | 36 | M3 |
| FF2 | Mid: ride silhouettes with lights (no logos) | 640 x 200 | lights blink (code) | mid | DEC | NB 2.1 2K | 36, reserve 36 | M3 |
| FF3 | Ferris wheel: hub, A-frame legs, gondola (rim and spokes procedural, rotated in code) | gondola 32 x 24; legs 160 x 240 | | back / play (gondolas) | DEC + OBS | NB 2.1 1K sheet | 24, reserve 24 | M3 |
| FF4 | Carousel: canopy, centre, horses (platforms that rise and fall) | 200 x 120; horse 32 x 24 | 3 | play | OBS | NB 2.1 2K | 36, reserve 36 | M3 |
| FF5 | Swing ride tower and seats | 48 x 160; seat 12 x 12 | | play | OBS | NB 2.1 1K | 24 | M3 |
| FF6 | Bouncy castle (front-on) | 96 x 64 | squash 3 (hand) | play | OBS | NB 2.1 1K | 24 | M3 |
| FF7 | Stalls: candy floss, game booths, light strings | 64 to 96 wide | | back / play | DEC + OBS | NB 2.1 2K sheet | 36 | M3 |
| FF8 | Ride operator sheet + 1 clip | 72 to 78 tall | 8 | play | CHR | NB 2.1 1K + 26 | 24 + 26 = 50 | M3 |

### 2.10 Level 9, Night Harbour (M3)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NH0 | Key screen (the owner's night panel is the reference) | 320 x 240 | | | ref | NB 2.1 2K | 36 | M3 |
| NH1 | Warehouses and harbour cranes | 640 x 200 | windows lit (code) | mid | DEC | NB 2.1 2K | 36, reserve 36 | M3 |
| NH2 | Far city at night (lights on the water) | 640 x 120 | | far | DEC | NB 2.1 2K | 36 | M3 |
| NH3 | Harbour kit: net shed, fish shed with roof, fish crates, tarp over a beached boat, low jetty, lantern post, mooring post | as in the beat sheet | | play | OBS | NB 2.1 2K sheet, refs `rw_jetty.png`, `pile.png`, NH0 | 36, reserve 36 | M3 |
| NH4 | Mia's house: front door, warm windows, porch light | 128 x 112 | | back / play (steps) | DEC | NB 2.1 1K | 24, reserve 24 | M3 |
| NH5 | Fox: hand-pixeled 1x sit (30 x 20), then run, peek (eyes in the dark), snatch | 40 x 32 cells | 3 clips x 8 | play | CHR | Hand-pixel the key pose, import, 3 pixel-engine clips | 3 x 26 = 78 | M3 |
| NH6 | Night boats, quay tiles, water, crumbling planks, lanterns | | | | | Recolour `rowboat.png`, `water.png`, pier granite into the night script; hand-pixel lanterns and planks | 0 | M3 |

### 2.11 Level 10, Home in the storm (M3; art waits for the beat sheet, map and greybox)

| ID | Asset | Size | Frames | Layer | Role | Method | Credits | MS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HS0 | Key screen | 320 x 240 | | | ref | NB 2.1 2K | 36 | M3 |
| HS1 | Courtyard building backs with lit windows | 640 x 240 | windows flicker (code) | mid / back | DEC | NB 2.1 2K | 36, reserve 36 | M3 |
| HS2 | Roofline and storm cloud shapes | 640 x 120 | lightning lit (code) | far | DEC | NB 2.1 2K | 36 | M3 |
| HS3 | Courtyard kit: bike shed (perch), recycling bins, washing lines, sandbox, cellar steps | 32 to 120 wide | | play | OBS | NB 2.1 2K sheet | 36, reserve 36 | M3 |
| HS4 | Cellar and stairwell kit: storage cages, boiler, pipes, stair flights, landings, banister, Mia's door | tiles + pieces | | play / back | OBS + DEC | NB 2.1 2K sheet | 36, reserve 36 | M3 |
| HS5 | Mia startle (thunder), Mia at the door | 66 px cells | 8 each | play | CHR | 2 pixel-engine clips from 7ca7be0e | 2 x 26 = 52 | M3 |

---

## 3. The pipeline

### 3.1 Before any generation (once per chapter)

1. **SpriteCook project.** Create a project "FETCH" and a collection per chapter (free organising tools; not called
   in this planning round). Every asset goes in, labelled `FETCH <level> <piece> <size>`.
2. **References uploaded once and reused by ID:** the owner's 4-panel concept art and the Stockholm reference photos
   (originals, through the in-page upload route in `claude/fetch-game-notes.md`), Pepper 1x (8c939973), Mia's
   standing pose (7ca7be0e), the town style sheet (36fe3255).
3. **Style lock: a style reference sheet per chapter**, made first and passed as a style reference to every
   generation in that chapter:
   - Chapter 1 (Morning): composited in code from approved 1x art (S1), 0 credits.
   - Chapters 2 and 3: the level key screens (RT0, MT0, SH0, BS0, FF0, NH0, HS0) are generated first, shown to the
     owner, and once approved they and the chapter's approved sprites become that chapter's sheet.
4. **Palette per level.** Write the level's colour script into `look.lua` first (Rooftops noon, Metro cool
   underground light, Soder warm afternoon, Building site late afternoon, Funfair evening, Night, Storm). Build a
   master palette per level, `tools/palettes/<level>.gpl`: the approved assets' colours merged at deltaE under 4,
   at most 64 scenery colours per level plus the shared character ramps. Each new piece snaps to its own 5 to 16
   colours drawn from that palette (the shader maps each colour to one colour, so counts hold in game).

### 3.2 Per asset class

**Backdrop layers (far, mid):**
1. Prompt for a wide strip at 2K: perspective and volume ("roofs recede, cornices cast shadow, windows recessed"),
   "16-bit console background painting, chunky square pixels, no outlines, no strokes, edges by value steps",
   "no text, no logos", the level's time of day and haze colour. Refs: chapter sheet, owner's concept panel,
   reference photos.
2. Download through Chrome (the false-colour render + hash route, `tools/decode.py`; api.spritecook.ai is blocked
   from the workspace and the Mac).
3. Measure the generated pixel grid (it ignores size hints), then box-filter to the exact game height; cut or
   repeat whole columns (houses, arches) to reach a loop width that is a multiple of 64; never scale by a
   non-integer factor after the box filter.
4. Snap to the level palette, 8 to 14 colours for far layers; leave dark colours out of a far layer's palette or
   the model draws strokes.
5. No outline. The shader and the 28 % fade make it recede.

**Building facades:** as backdrops, plus measure the window and storey size against `building.png` before the
downscale, and choose the factor so windows match; a 2x box reduction where it lands near the target. Facades that
carry ledges (balconies, loggia) are split: the facade is decoration (faded, no outline), the ledge is a separate
obstacle piece with its own outline.

**Props (obstacles):**
1. Sheets of 4 to 8 props per 2K call, each drawn front-on ("front view only: no top surface seen from above, no
   side faces, a thin cap"), at about 2 to 4x, refs: chapter sheet + the nearest approved prop.
2. Box-filter each to its collision box exactly (the box decides the size, not the art), snap to 6 to 16
   colours, despeckle, then a 1 px dark outline all round (`build_critters_art.py` routine).
3. Small props under about 40 px: hand-pixel at 1x in the level palette (the sprite rule from 4 Oct: small things
   drawn at game size look crisp; reduced renders look soft).
4. Decoration props: same, but no outline (edge pixels take the darkest neighbouring shade), faded in code.

**Critters with animations** (the goose / cat route, proven):
1. One key pose: hand-pixel at 1x (small animals) or generate at 2 to 4x and reduce; clean; outline.
2. Import the 1x (`import_asset` base64, or upload).
3. pixel-engine-v1.5, auto prompt enhancement off, 8 frames, poses named in order, what must not change ("same
   colours, same 1 px outline, same pixel scale, feet planted").
4. `clean.py`-style pass: palette snap, the animator's grey matte (#7e7e7e) peeled from the outside in, specks
   removed, eye fixed, outline restored. Cells with a fixed feet anchor.

**People:** generate a sheet of the cast for a level in one call (same style, same scale as the keepers and Mia),
reduce to 72 to 78 px tall, import each, animate only the clips gameplay needs (walk, one action). Reuse by recolour
where the silhouette allows (the keeper's barrow walk becomes a builder with a hard hat and hi-vis).

**Vehicles:** side view (that is front-on for a side-scroller), true scale from the ruler, wheels separate so
`make_wheels.py` rolls them; riders' pedalling as a pixel-engine clip; hit box decided by gameplay and drawn over
by the art, with Pepper always drawn after vehicles.

**Effects:** procedural or hand-pixel only (rain, splashes, lightning, steam, dust, light pools): no generation.
Max 3 flashes a second.

### 3.3 QA checks on every asset (a script, `tools/art_qa.py`, plus the owner's eye)

| Check | Pass |
| --- | --- |
| Scale against Pepper | Height within 10 % of the ruler (section 0) or of `building.png` for architecture; contact sheet with Pepper and Mia beside it |
| Outline rule | Obstacles: 95 % or more of silhouette pixels dark. Decoration: under 10 % |
| Front-on rule | Owner's eye on the contact sheet: no top faces, no side faces, no insides |
| Palette count | Prop 6 to 16, backdrop 8 to 14, character as its approved ramp; every colour in the level palette |
| Noise | Lone pixels under 8 % (hard surfaces), under 12 % (foliage); no isolated pixels in flat fills; no clusters of 2 to 3 near-identical shades |
| Pixel authenticity | Alpha only 0 or 255; no 2 x 2 duplicated blocks (an upscaled source); no gradients wider than 3 shades without dither |
| Fit | Exact collision box size; feet / base on the right row; loops seamless |
| In game | `LOOK_CHECK=1` autopilot run: 0 overlaps over Pepper; `check_pepper` UNCHANGED; physics, QA fuzz and flow checks unchanged |

### 3.4 Review gates with the owner

1. **Gate A, the list:** this plan and the batch (credits per line). Nothing is generated before it.
2. **Gate B, key screen / style sheet** per new level (one image, 36 credits) before any kit is generated.
3. **Gate C, proposals:** every batch comes back as a contact sheet (each piece at 1x and 4x, beside Pepper and Mia,
   old vs new) plus an in-game screenshot made from a proposals build. Pieces go into the build only when approved.
4. **Gate D, in game:** a build with the approved art and before / after GIFs.
Two tries per piece (the reserve); a third try is a new decision, not automatic.

### 3.5 Versioning in the repo

- One branch per batch (`assets/r5-b1`, ...), merged into `round1` after Gate D, then tagged with the build.
- Sources: raw downloads in `source_scenery/` (scenery) and `source_sheets/` (characters, clips), never edited.
- Proposals in `art_proposals/<batch>/` (not loaded by the game) until approved, then built into `riverwalk/art/`.
- Every 1x file is rebuilt by a script (`tools/build_<batch>.py`), so the art can be regenerated byte for byte.
- `source_scenery/manifest.json` gets one entry per asset: SpriteCook asset ID, model, prompt, references, credits,
  date, palette, size, status (proposed / approved / rejected).
- Replaced art keeps the old file (as `flowerbox.png` beside `flowerbox_front.png`) until the owner approves the new
  one; code fallbacks stay.
- CHANGELOG entry per batch with credits spent and left.

---

## 4. Budget

| Milestone | Levels | Expected | Reserve (retries) | Total |
| --- | --- | --- | --- | --- |
| M1 vertical slice (Christmas demo) | 1 River Walk, 2 City Park, 3 Downtown + shared fixes | 492 | 204 | **696** |
| M2 | 4 Rooftops, 5 Metro, 6 Soder Hill + Mia walk | 934 | 264 | **1,198** |
| M3 | 7 Building site, 8 Funfair, 9 Night Harbour, 10 Storm | 1,108 | 360 | **1,468** |
| **All** | | **2,534** | **828** | **3,362** |

Arithmetic: M1 expected = S2 76 + S3 52 + S5 26 + RW1 24 + RW2 36 + CP1 24 + DT1 50 + DT2 36 + DT3 36 + DT4 36 + DT5 36
+ DT6 24 + DT7 36 = 492; reserve = S2 24 + RW1 24 + RW2 36 + CP1 24 + DT1 24 + DT3 36 + DT4 36 = 204.
M2 expected = Rooftops 302 (36 + 36 + 36 + 108 + 36 + 50) + Metro 426 (36 + 36 + 36 + 36 + 24 + 72 + 24 + 24 + 36 + 24 + 78)
+ Soder 180 (36 + 36 + 36 + 72) + S11 26 = 934; reserve 72 + 120 + 72 = 264.
M3 expected = Building site 328 (36 + 36 + 36 + 24 + 24 + 24 + 36 + 36 + 76) + Funfair 302 (36 + 36 + 36 + 24 + 36 + 24
+ 24 + 36 + 50) + Night 246 (36 + 36 + 36 + 36 + 24 + 78) + Storm 232 (36 + 36 + 36 + 36 + 36 + 52) = 1,108;
reserve 60 + 96 + 96 + 108 = 360.

**Against the balance of 1,486:** M1 fits (1,486 - 696 = 790 left at worst, 994 if no retries). M2 does not fit in
what is left (1,198 needed vs 790 to 994). The whole plan is 3,362, a shortfall of **1,876** (1,048 if no retry is
ever used). This is lower than the 22 Oct estimate of about 4,000 because effects, tiles and small props are
hand-pixel and the backdrops reuse the look shader.

**Top-up recommendation:** none before M1. Buy about **1,000 credits before M2** starts (covers M2 with its reserve
on top of what M1 leaves) and about **1,000 before M3**, about 2,000 in all, spread as the 22 Oct plan suggested.
Check the price of one 2,000 pack against two 1,000 top-ups when M2 is approved.

### 4.1 The cheaper option

| Saving | How | Credits saved |
| --- | --- | --- |
| Fewer key screens | One key screen per chapter instead of per level (chapter 2: Rooftops only; chapter 3: Night uses the owner's night panel as its key) | 72 (M2) + 108 (M3) |
| Reuse far layers | Building site far = Rooftops far recoloured; Funfair far = River Walk water and shore recoloured; Night far = River Walk skyline at night; Soder far = Downtown far roofs | 36 (M2) + 108 (M3) |
| Hand-pixel simple geometry | Footbridge, spire (hand-cut from the skyline's spire), escalator kit, crane top, swing tower, bouncy castle | 60 (M1) + 24 (M2) + 72 (M3) |
| Fewer clips and people sheets | Road cyclists keep wheel-roll only (no pedalling); Metro one clip instead of three; no sauna guest; builders and ride operators recoloured from the keepers (no sheets, no clips) | 52 (M1) + 102 (M2) + 126 (M3) |
| Pixel Engine Image (6) for small unreferenced pieces | Odenplan clock (24 to 6), crane loads (24 to 6), lift cage (24 to 6) | 18 (M2) + 36 (M3) |
| No decorative tram | Downtown's back lane stays empty | 36 (M1) |
| Smaller reserves | Retries on backdrops only | 84 (M1) + 114 (M2) + 180 (M3) |

Cheaper totals: **M1 464** (344 + 120 reserve), **M2 832** (682 + 150), **M3 838** (658 + 180); **2,134 in all**,
a shortfall of about 648: **top up about 750** before M3.

**Quality risk of the cheaper option:** code- and hand-drawn geometric pieces read flat next to painted
SpriteCook pieces (the owner called a hand-pixel title redraw "terrible", so big hand-drawn pieces are a real
rejection risk; keep hand work to small, simple shapes); Pixel Engine Image takes no style references, so its
pieces drift in palette and shading and need more cleanup; recoloured far layers make levels feel alike, which
works against Lion King's distinct-per-level look; fewer clips make people stiff; fewer key screens move the
owner's first look later, so rejections cost more when they come. Recommended: the full plan for M1 (the demo is the
reference for "finished"), then decide per milestone.

---

## 5. First batch for immediate production (M1 must-haves): **528 credits** (408 expected + 120 reserve)

Approve line by line. Lines marked D1 (110) and D2 (204) depend on the decisions in section 6; without them the
batch is 214.
Every line: generation at Nano Banana 2.1, pixel mode on, 2 variations; download through Chrome with the hash check;
reduce, snap, outline in a `tools/build_r5b1.py`; contact sheet beside Pepper and Mia for the owner before anything
enters the build.

| # | Asset | Credits | Prompt approach | References |
| --- | --- | --- | --- | --- |
| B0 | Prep: chapter 1 style sheet (S1), SpriteCook project and collection, reference uploads | 0 | Composite in code; upload | Approved 1x art, concept panels, Stockholm photos |
| B1 | Promenade cyclists x2 (S2), source also used for the road riders | 24 + 24 reserve | "Two Stockholm commuter cyclists side by side, full side view facing right, for a 16-bit side-scroller: a woman in a red coat and white helmet on a pale blue city bike with a front basket; a man in a dark green jacket and grey helmet on a black city bike. Each figure 4 times larger than game size, so at game size 76 px tall from the bottom of the wheels to the helmet and 76 px long: the rider is more than twice the height of the black labrador reference, whose body is 26 px tall. Chunky square pixels, flat shading 2 to 3 tones per colour, crisp 1 px dark outline like the reference dog and park keeper. Wheels drawn round and clear. No ground, no shadow, plain background, only the two cyclists." | Pepper 1x, chapter 1 sheet, keeper cart sheet (people style), current cyclist1 (8d43c6f3) for the outfit |
| B2 | Pedal loops: promenade riders (S2) | 2 x 26 = 52 | Import each 1x; "Looping pedal cycle in place, side view: the rider pedals, knees rise and fall in turn, feet stay on the pedals, upper body steady, hands on the bars. The bike frame does not move. Same rider, same colours, same 1 px outline, same pixel scale." | The 1x import |
| B3 | Pedal loops: road riders at 92 px (S3) | 2 x 26 = 52 | Same prompt, from the 92 px box-filtered import | The 92 px import |
| B4 | Mia throw (S5) | 26 | From 7ca7be0e: "Throw, side view facing right, poses in order: standing holding the red ball, wind up with the ball behind her head, step forward, arm swings forward, release, follow-through, arm comes down, standing. Black hoodie, hood stays up, same girl, same colours, same outline, same scale." | Mia standing 7ca7be0e |
| B5 | D1: cargo bike with rider (DT1) | 24 + 26 + 24 reserve | "A Stockholm cargo bike (long box bike) with a wooden cargo box at the front full of bread crates, ridden by a baker's delivery man in a flat cap and apron, full side view facing left. At game size 96 px long and 76 px tall; the cargo box is low, about 26 px tall, the same height as the black labrador reference. 16-bit console pixel art, chunky square pixels, flat shading, crisp 1 px dark outline. No text, no logos, no ground, plain background." Then the pedal loop as B2 | Chapter 1 sheet, town style sheet 36fe3255, keeper cart sheet, Pepper |
| B6 | D1: vintage tram for the back lane (DT2) | 36 | "An old Stockholm tram car (1920s style, blue and cream, clerestory roof, pantograph pole), full side view, 16-bit console background art, no outlines, edges by value steps, soft midday light, no text, no logos. At game size 300 px long and 130 px tall." Faded as decoration | Town style sheet, reference photo of a Djurgarden line tram |
| B7 | D2: Downtown roofs kit A (DT3) | 36 + 36 reserve | "A sheet of front-view old town roof pieces for a side-scroller, each seen straight from the front at street height with only a thin top edge, no top surfaces from above, no side faces: an arcaded loggia front, a gallery with a balustrade in two parts, a stepped gable end of a guild house, a brick chimney with three clay pots, a small dormer, flat stone roof ledges, a striped window awning on iron arms. Ochre, red and grey-green plaster, copper and tile, the same palette as the reference town style sheet. Drawn at 3x game size. Chunky square pixels, flat shading, 1 px dark outline. No text, plain background." | 36fe3255, `town_house1-3`, `town_awning80`, Pepper |
| B8 | D2: tall house fronts (DT4) | 36 + 36 reserve | "Three five-storey Gamla stan house fronts side by side, ochre, rust red and yellow plaster, with cornices, recessed windows that show depth, door arches at the bottom, roofs receding behind; light from the upper left with soft cast shadows under the cornices. 16-bit console background painting, no outlines, no strokes, edges by value steps. Windows the same size as in the reference building. No text." | `building.png` (scale), owner's plaza panel, Stockholm photos, 36fe3255 |
| B9 | Near facades strip with volume (DT5) | 36 | As B8 but a continuous row of 6 to 7 narrower houses, at the far-layer haze, "a row of old town houses seen across a square" | B8 result (style), owner's plaza panel |
| B10 | D2: footbridge (DT6) | 24 | "A short iron footbridge over a canal, front view at water level: a flat deck with a thin top edge, an iron railing behind the deck, a shallow arch underneath. 3x game size, 1 px outline, no text, plain background." | 36fe3255 |
| B11 | D2: Riddarholmen spire (DT7) | 36 | "The cast-iron openwork spire of Riddarholmen church, tall and slender, seen from the side across the river, as a 16-bit console background element, no outlines, hazy blue-grey midday light. At game size 32 px wide and 400 px tall." | Reference photo, the existing skyline spire |
| B12 | Hand and code work (S4, S6 to S10): car crop fix in code, delete car1-5, springs, stick, frisbee, clean pass, outline pass, bin side face | 0 | Code and hand-pixel | Approved art |

Sum: B1 48 + B2 52 + B3 52 + B4 26 + B5 74 + B6 36 + B7 72 + B8 72 + B9 36 + B10 24 + B11 36 = **528**
(expected 408, reserve 120). Balance after the batch: 958 at worst, 1,078 if no retry is used.
Left of M1 for batch 2 (after the River Walk tall map and the treetop review): RW1 48, RW2 72, CP1 48 = 168.

---

## 6. Decisions for the owner

- **D1 The tram.** A: cargo bike hazard + true-scale tram as back-lane decoration (recommended, 110 credits incl.
  reserve). B: keep the tram as the hazard and accept its toy scale (breaks rule 6). C: a true-scale tram as the
  hazard (needs Downtown's perches redesigned above 160 px: level work).
- **D2 Tall Downtown and tall City Park** replace the flat versions in the demo? If Downtown stays flat, B7, B8, B10,
  B11 drop out (204 credits).
- **D3 Soder scale:** barrels from 14 to 20 to 22 px (needs a physics re-check), parked bikes replaced by fallen
  e-scooters (true scale at 44 x 16).
- **D4 Hollow log** ends: keep (they read as crawl-through) or redraw front-on.
- **D5 The cat** at about 1.7x real size: keep for readability?
- **D6 Top-up** about 1,000 before M2 and 1,000 before M3, or the cheaper option.
- **D7 Title:** stays the 19 Oct title unless a human pixel artist is found (not in this budget).
