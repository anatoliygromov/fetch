# Art batch 1 (branch `r8/art`, 23 Oct 2026)

The owner approved batch 1 of `docs/asset_plan_22oct.md` section 5 (up to 528 SpriteCook credits; D1 = cargo bike
hazard plus a true-scale vintage tram in the back lane; D2 = tall City Park and tall Downtown are the real levels).
Everything here is a **proposal**: new files only, in `riverwalk/art/r8/`, nothing in `riverwalk/art/scene/` or any
Pepper file was touched, and no gameplay code reads them yet. The owner reviews the contact sheets first.

**Credits: 408 spent of 528 (the 120 reserve was not used). Balance 1,486 before, 1,078 after.** Uploads were free
(checked against the balance).

Contact sheets (3x, every asset on its level's ground beside Pepper and Mia, alternates and the old art beside it):
`/home/claude/out/r8-art/B0_style_sheet.png` ... `B11_spire.png`, and `overview.png` (2x, every chosen asset).

SpriteCook: project **FETCH** (`593872c7-1329-42ad-a326-d406846286f5`), collection **batch1**
(`9da01846-c324-4f64-bb75-65f32451bb55`); every asset of this batch (generations, animations, uploads) is in it.

## How it was made

- Model: Nano Banana 2.1 (`gemini-nano-banana-2.1`), pixel mode on, 2 variations per call (1K = 24 credits, 2K = 36);
  animations pixel-engine-v1.5, auto prompt enhancement off, 8 frames, spritesheet (26 credits each).
- Style references on every still: the chapter 1 style sheet `8a64c999` (B0), plus Pepper 1x `8c939973` (people and
  props), the town style sheet `36fe3255` (Downtown pieces), and a specific reference where useful (the old road
  cyclist `5efe458f`, the leaf-cart keeper `43bb3a0a`, the B8 house fronts `d69a16d5` for B9).
- Transfers: api.spritecook.ai is still blocked from the cloud workspace and the Mac's shell, and the owner's Chrome
  extension was not connected. The Claude desktop app's browser pane reaches SpriteCook: downloads go page ->
  base64 text -> the session's saved tool output -> decoded and checked by SHA-256 (`F|name|sha|data` lines, sliced at
  240,000 characters). Uploads: the page itself makes the file and PUTs it to the upload URL (same origin); the style
  sheet was sent into the page in 2,000 to 6,000 character chunks, each checked by hash. The 1x animation sources were
  built in the page from the downloaded pictures by `tools/r8_browser_reduce.js` (the same steps as `tools/r8lib.py`)
  and downloaded again, so `source_sheets/r8_*_1x.png` are byte for byte what SpriteCook animated.
- Size: SpriteCook's pixel output comes back at its detected pixel grid, often smaller than asked (the tram 222 px,
  the house fronts 194 px for three houses). Never scaled up: those pieces were built from the raw render instead
  (box-reduced 4x in the page before transfer: `*_raw4.png`), keyed off its white ground, then box-filtered down.
- Build: `tools/build_r8_stylesheet.py` (B0), `tools/build_r8_people.py` (B1 to B5), `tools/build_r8_scenery.py`
  (B6 to B11), `tools/build_r8_sheets.py` (contact sheets), `tools/art_qa.py` (checks). All rebuild from
  `source_scenery/r8_*` and `source_sheets/r8_*`.
- QA (`python3 tools/art_qa.py`): **28 of 28 files pass**: size against target, colours (obstacle 6-20, decoration
  6-16, character up to 24), outline (obstacles and characters 100 % of the silhouette dark, decoration 0 to 4 %),
  lone pixels under 2.2 %, no isolated pixels, no semi-transparent pixels, no grey matte.

## Lines

| # | Asset | Credits | SpriteCook ids | Choice |
| --- | --- | --- | --- | --- |
| B0 | Chapter 1 style sheet (River Walk, City Park, Downtown panels from approved 1x art; Pepper, Mia, cat, goose, keeper, cyclist; sky swatches) | 0 | upload `8a64c999` | `source_sheets/r8_style_ch1_2x.png` (1590 x 648, 2x of `_1x`) |
| B1 | Commuter cyclists, woman (red coat) and man (green jacket) | 24 | `252eab71` (chosen), `1ec80228` (alt) | v1: cleaner riders. 84 px tall (wheel to helmet), wheels about 30 px |
| B2 | Pedal loops, promenade riders 84 px | 52 | sources `ed4b757a`, `1ec3c589`; loops `2616973e`, `3121eb01` | steady loops, frames stay 1x |
| B3 | Pedal loops, road riders 92 px | 52 | sources `598007f4`, `f5b19627`; loops `ee8116f0`, `99b22d00` | same riders at 92 px |
| B4 | Mia throw | 26 | `c576fd67` from `7ca7be0e` | wind-up, step, release, follow-through. **Owner's eye:** frame 8 ends mid-stride, not back to standing; the ball in her hand is grey |
| B5 | Cargo bike with the baker (hazard) and its pedal loop | 24 + 26 | still `48ad61dc` (chosen), `d9655402` (alt); 1x source `1c2ce5bb`; loop `005b2cf2` | v1 (v2's white spokes read badly). Native 1x at SpriteCook's grid, no resampling |
| B6 | Vintage tram, back lane | 36 | `ebc29363` (chosen), `8453ee61` (alt) | v1: clerestory, two bogies, blue and cream |
| B7 | Downtown roof kit | 36 | `d4d99e4f` (chosen), `62b951f5` (alt) | v1. **Owner's eye:** the dormer was drawn with a side face in both variations; its side was cut off |
| B8 | Tall Old Town house fronts | 36 | `d69a16d5` (chosen), `c2ea74b3` (alt) | v1: stepped and curved gables; v2 has more roof depth but drawn strokes between houses |
| B9 | Row of house fronts across the square | 36 | `f6200cac` (chosen), `f24f1355` (alt) | v2 (786 px, finer) |
| B10 | Canal footbridge | 24 | `326e9348` (chosen), `8e25f928` (alt) | v1. **Owner's eye:** both variations painted a small dog on the deck (the Pepper reference leaking in); it was painted out by copying the railing two bays along, and the plank tops seen from above (7 rows) were cut out |
| B11 | Riddarholmen spire | 36 | `34933164` (chosen), `66272059` (alt) | v2: openwork spire on its brick tower |
| | **Total** | **408** | | reserve 120 unused |

Prompts (abridged; the full text is in each asset's SpriteCook record):
- B1: "Two Stockholm adult commuter cyclists side by side ... full side view facing right ... a woman in a red wool coat,
  dark trousers and a white helmet on a pale blue Dutch-style city bike with a front basket; a man in a dark green
  jacket, brown trousers and a grey helmet on a black city bike ... about 84 px tall ... wheels 30 px ... crisp 1 px
  dark outline ... no ground, no shadow, no text". 1K 16:9.
- B2/B3: "Looping pedal cycle in place, side view facing right: the [rider] pedals ...; the pedal cranks turn one full
  circle, knees rise and fall in turn, feet stay on the pedals, upper body steady ... The bike frame and the wheels
  stay exactly in place ... Same rider, same bike, same colours, same 1 px dark outline, same pixel scale."
- B4: "The girl throws a small ball for her dog, side view facing right, poses in order: standing holding the ball ...;
  wind up ... behind her head ...; she steps forward ...; arm swings forward ...; release ...; follow-through ...;
  the arm comes back ...; standing relaxed again. Back foot planted, hood stays up ... only the girl is drawn".
- B5: "A Stockholm cargo bike (bakfiets) ridden by a baker's delivery man ... low wooden cargo box full of bread
  crates ... flat cap, white shirt, long beige apron ... brass bell ... 96 px long and 76 px tall; the cargo box about
  26 px tall ... no text, no logos". 1K 1:1. Loop prompt as B2.
- B6: "An old Stockholm tram car from the 1920s to 1940s ... blue lower body and cream upper body, faded paint ...
  clerestory roof, trolley pole, two bogies ... background painting style: no dark outlines ... no text, no numbers,
  no logos, no advertising, no rails". 2K 16:9.
- B7: "A sprite sheet of separate old-town rooftop pieces ... seen straight from the front at street height: front face
  plus only a thin top edge ...: arcaded loggia, gallery with balustrade in two parts, stepped gable end of a guild
  house, brick chimney with three clay pots, small dormer, three flat stone ledges, striped window awning on iron
  arms ... 1 px dark outline". 2K 1:1.
- B8: "Three tall five-storey Gamla stan house fronts ... ochre, rust red, warm yellow ... recessed windows ..., cornices
  casting soft shadows, roofs receding ... windows the same size as in the beige building of the style guide ...
  no outlines, no strokes". 2K 1:1.
- B9: "A continuous row of seven narrow old-town house fronts seen across a sunny square ... hazy midday light ... no
  outlines ... the same style as the reference house fronts". 2K 16:9.
- B10: "A short iron footbridge over a narrow city canal ... flat walking deck with a thin top edge, dark green
  cast-iron railing behind it, one shallow iron arch, stone abutment stubs ... front view only ... 160 px wide".
  1K 16:9.
- B11: "The tall slender cast-iron openwork spire of Riddarholmen church ... brick tower at the bottom ... hazy
  blue-grey midday light ... no outlines". 2K 9:16.

## Files for the level agent (all in `riverwalk/art/r8/`, 1x, transparent)

Obstacles have a 1 px dark outline; decoration has none and is meant to be faded by the look shader (the `back` or
`city` layer). Every piece's bottom row is its base; widths match the greybox boxes in `maps/downtown_tall.tmx`.

| File | Size | Role | Meant for / replaces |
| --- | --- | --- | --- |
| `cyclist_a_84.png`, `cyclist_b_84.png` | 80 x 84, 78 x 84 | hazard riders, face right (mirror for left) | promenade bikes; replace `scene/road_cyclist1.png`, `road_cyclist2.png` (73 x 75) and the retired `cyclist1/2.png` |
| `cyclist_a_84_pedal.png`, `cyclist_b_84_pedal.png` | 8 cells of 80 x 84 / 78 x 84 | pedal loops (whole bike drawn; wheels keep their own roll in code if wanted) | replace `road_cyclist1_roll.png`, `road_cyclist2_roll.png` |
| `cyclist_a_92.png`, `cyclist_b_92.png` + `_pedal.png` | 87 x 92, 85 x 92 (8 cells) | near-lane road riders | the near lane's bikes (`road.lua`); same art one step closer |
| `mia_throw.png` | 8 cells of 57 x 60, feet on the bottom row | Mia's throw (faces right) | the faked throw in `bonus.lua`; a new row for `girl.png` / `girl_frames.lua` (cells there are 66 x 66, anchor x 33, y 66: centre these 57 x 60 cells on that anchor) |
| `cargobike.png` | 102 x 76, faces left | the street hazard (D1). Hit box 80 x 26 = the cargo box and front wheel: x 0-80 from the left edge, the bottom 26 rows (drawn in red on `B5_cargo_bike.png`) | replaces `scene/town_tram.png` as the hazard; the tram sheds become courtyard gates |
| `cargobike_pedal.png` | 8 cells of 102 x 76 | its pedal loop (bike still, legs move) | |
| `tram_vintage.png` | 276 x 130, faces right | back-lane moving decoration (D1), faded | new; wheels are drawn on (roll in code by shifting the bogie rows if wanted) |
| `roof_loggia.png` | 120 x 64 | obstacle, one-way top on row 0 | LOGGIA (x 1416, w 120) |
| `roof_gallery88.png`, `roof_gallery72.png` | 88 x 30, 72 x 31 | obstacles, top rail row 0 | the two GALLERY halves (w 88, 72) |
| `roof_gable.png` | 148 x 124 | obstacle, the stepped gable steps are the one-way steps | GUILD HOUSE (w 148) and GUILD ROOF |
| `roof_chimney.png` | 24 x 54 | obstacle (golden bone on top) | CHIMNEY (w 16, centre it) |
| `roof_dormer.png` | 56 x 72 | obstacle | DORMER (w 56) |
| `roof_awning56.png` | 56 x 29 | obstacle (springy window awning) | AWNING by the flower market (w 56) |
| `roof_ledge32/48/64.png` | 32/48/64 x 8 | obstacles | roof ledges over tram street |
| `house_tall_a/b/c.png` | 85/82/86 x 240 | decoration (back) | the tall fronts that carry the high road; with B9, replace `scene/town_facades.png` and the small `town_house1-3.png` on the tall level |
| `facades_square.png` | 247 x 130, repeats by whole houses | decoration (mid layer) | replaces `scene/town_facades.png` (225 x 114) |
| `footbridge.png` | 160 x 53, deck top on row 21 (railing above it, behind Pepper) | obstacle | FOOTBRIDGE (x 2480, w 160) |
| `spire_riddarholmen.png` | 89 x 400 | decoration (far / back), faded | Riddarholmen's spire landmark (greybox 32 x 400: the openwork spire is the narrow upper part, the brick tower the wide base; crop to the spire if the 32 px slot must hold) |

## For the owner's eye

1. Mia's throw ends mid-stride (frame 8), and her ball is grey: the game draws its own ball, so it can spawn at
   frame 5 (release) and the clip can hold frame 1 after.
2. The dormer: drawn with a side face; cut to its front, the roof cap still overhangs on the right.
3. The footbridge: a painted dog was removed and the plank tops cut; check the railing over x 40-60.
4. The tram's windows were holes onto the white ground in the render; they were filled with a flat glass tone.
5. The tall house fronts' windows are about the size of the screen-1 building's (see `B8_house_fronts.png`).
6. Far-layer pieces (tram, facades) had their darkest tones lifted to luma 76 so they do not read as strokes.
7. Left on the owner's Mac by the transfer: `2d game test/.r8_xfer/` (t.html, x1.html, x2.html; a failed upload
   route, the tokens in them have expired). Safe to delete; this session had no delete permission there.
