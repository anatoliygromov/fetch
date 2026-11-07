# Levels 4 to 6 audit, 7 Nov: ground joins and weirdness

Owner, 7 Nov: "whenever we see two different types of ground connecting, they look cut, including the hills etc."
He also flags the weird things first: floating pieces, hard cuts, things that read as something else, scale clashes,
dirty details, props seen from above.

Read-only audit of `rooftops`, `soder` and `night` (levels 4 to 6 in `riverwalk/levels.lua`) on `origin/main` at
5f30120. No game files changed, no image service called, 0 credits. Same method, tables and severity scale as the
levels 1 to 3 audit (`origin/audit/07nov-ground-joins`, `docs/review/07nov/ground_joins/README.md`), so the two read
as one. Join and cause numbers here refer back to it where they match.

## The headline

All three levels are still greybox. Each has `L.scenery = "greybox"` and no `L.art`, so `St:draw` takes the grey
branch: the ground is `Sc.paintGroundGrey`, the backdrop `Sc.drawFarGrey`, every prop `Sc.drawProp` (a flat box with
its name printed on it), and the Lion King look is off. `docs/STATUS.md` line 158 already says the labels "go with
their art". In levels 1 to 3 two grounds meet and the seam looks cut. In levels 4 to 6 there is only one ground: roofs,
walls, slopes, the street, stairs and the quay are one slate fill with a 1 px edge. So every join is missing rather
than cut, and most of what the owner would call weird is greybox showing through.

This matters for order of work. Patching joins one by one here would be wasted: the fix is the level's art and its
ground by rule, built so the joins come out right the first time.

## How it was done

- Every screen at every height tier: `LOOK_SWEEP=1 LOOK_STEP=320 SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$(mktemp -d)
  xvfb-run -a love riverwalk --level <L> --lookshots`, a fresh `XDG_DATA_HOME` per run. Rooftops is 7472 x 1200
  (934 x 150 tiles; the header of `level/rooftops.lua` still says 1920 x 960): 216 frames, 24 across, tiers camY 960
  to 0. Söder Hill 5120 x 240: 16 frames. Night Harbour 4480 x 240: 14 frames.
- Every change of terrain kind or height listed from the maps (`level/tiled/rooftops.lua`, `level/soder.map`,
  `level/night.map`, parsed per 8 px cell) and every prop from the level files, then each suspect spot rendered again
  with `LOOK_XS` / `LOOK_YS` (and `LOOK_PX=-3000` to leave Pepper out) and checked at 4x, nearest neighbour.
- Each problem traced to the code or data that draws it.

Camera (x, y) is the sweep frame the join was judged in. World x is the join itself. Severity: High = visible at once
at 1x, Med = visible when you look, Low = minor, OK = no fix needed.

Sweep note: where a whole column is solid (88 of the 216 Rooftops frames are over 85 % one slate colour) the sweep
stands Pepper inside the wall, 60 px under the screen top. That is the tool (`tests_look.lua`), not the game.

## Count

| Level | Joins checked | Look cut or missing | OK | Weird things listed |
| --- | --- | --- | --- | --- |
| rooftops | 48 | 48 | 0 | 15 |
| soder | 28 | 28 | 0 | 15 |
| night | 18 | 18 | 0 | 15 |
| total | 94 | 94 | 0 | 45 |

Severity of the 94 joins: 43 High, 49 Med, 2 Low.

## 1. Ground joins

### Rooftops (greybox; `Sc.paintGroundGrey`; terrain from `level/tiled/rooftops.lua`, first drawn by `tools/make_rooftops.py`)

Every terrain column is `C.ground` with one `C.groundEdge` row on top, and a 1 px edge down the open side of a terrain
rect (scene.lua:473-501). The props (STAIRWELL A, BAKERY, HOTEL, LIGHT COURT ...) are decor boxes in `C.back` behind.

| # | Camera x,y | World x | Ground A / B | What is wrong | Drawn by | Good transition | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RT1 | 320,960 | 576 | street / stair slope up | The street turns into a 45 degree wedge of the same slate, 192 px high. Only a 1 px stepped edge marks it: no treads, no wall face, no railing. The STAIRWELL A box behind is a pale panel. Reads as a ski slope. | Sc.paintGroundGrey (scene.lua:473), slope tiles in level/tiled/rooftops.lua | Stone steps at 8 px rise per 8 px run (Sc.STEP_RW on day/07nov-ground) with a lit nosing per tread, a cheek wall with coping and a handrail, inside a stairwell housing. | High | |
| RT2 | 640,840 | 768 | stair slope / flat roof T1 | The wedge's top runs into the roof line. No landing, no parapet. | as RT1 | A landing slab and the roof's parapet coping starting at the stair head. | Med | |
| RT3 | 640,840 | 896 | flat roof / pitched roof R1 | R1 is a plain triangle in the flat roof's colour, and the wall under it is the same fill. No gutter, eaves, tiles or gable wall. Reads as a hill. | Sc.paintGroundGrey | Gable end by rule: a gutter line at the foot, eaves 2 px over with a shadow row, tile courses on an 8 px slope tile with a lit top edge, a plaster gable face below. | High | 09 |
| RT4 | 640,720 | 960 | R1 slope / R1 slope (ridge) | The ridge is a 1 px point. | as RT3 | Ridge cap tiles; a chimney pot. | Med | |
| RT5 | 960,840 | 1024 | R1 / flat roof | As RT3, mirrored. | as RT3 | as RT3 | High | |
| RT6 | 1280,720 | 1280 | flat roof / wall up 96 px | Roof and wall are one slate fill. A 1 px edge on the wall's top and side, nothing else: no coping, no wall face, no windows, no shadow on the lower roof. | Sc.paintGroundGrey (the rect sides pass) | Wall step piece: coping 1-2 px over with its shadow row, a plaster face with one window row (asset plan RT4), a 2 px shadow band on the lower roof. | High | |
| RT7 | 1280,720 | 1568 | roof / light well (down 96) | The well is a straight slot in the slab; loose tiles hang over it. | as RT6 | A parapet on both lips, darker inner wall faces, a skylight frame at the bottom. | Med | |
| RT8 | 1600,720 | 1664 | light well / roof (up 96) | As RT7, mirrored. | as RT6 | as RT7 | Med | |
| RT9 | 1600,720 | 1792 | flat roof / pitched roof R2 | As RT3. | as RT3 | as RT3 | High | 09 |
| RT10 | 1600,600 | 1856 | R2 ridge | As RT4. | as RT3 | as RT4 | Med | 09 |
| RT11 | 1600,720 | 1920 | R2 / flat roof | As RT5. | as RT3 | as RT3 | High | |
| RT12 | 1920,600 | 2048 | roof / wall up 96 | As RT6. | as RT6 | as RT6 | High | |
| RT13 | 1920,600 | 2112 | roof / market hall glass roof R3 | As RT3. The plan's glass roof is the same slate as everything else. | as RT3 | as RT3, with glazing bars on a grid in place of tiles. | High | |
| RT14 | 1920,600 | 2176 | R3 ridge | As RT4. | as RT3 | as RT4 | Med | |
| RT15 | 1920,600 | 2240 | R3 / flat roof | As RT5. | as RT3 | as RT3 | High | |
| RT16 | 2240,480 | 2400 | roof / chimney block (up 96) | As RT6. The SWEEP'S CHIMNEYS box sits on it as a pale label panel. | as RT6 | as RT6, with a chimney stack on top. | High | |
| RT17 | 2240,480 | 2464 | chimney block / roof | As RT16, mirrored. | as RT6 | as RT6 | High | |
| RT18 | 2240,600 | 2528 | roof / skylight dip (down 96) | As RT7. | as RT6 | as RT7 | Med | |
| RT19 | 2560,600 | 2624 | skylight dip / roof | As RT8. | as RT6 | as RT7 | Med | |
| RT20 | 3200,480 | 3328 | roof / roof bar wall (up 192) | As RT6, twice as tall. | as RT6 | as RT6, two window rows. | High | |
| RT21 | 3200,480 | 3432 | roof / drying yard dip (down 40) | A 40 px step with only the 1 px side edge. | as RT6 | A low parapet both sides and a 2 px shadow band on the yard floor. | Med | |
| RT22 | 3520,480 | 3576 | dip / roof | As RT21, mirrored. | as RT6 | as RT21 | Med | |
| RT23 | 3840,240 | 3872 | roof / roof terrace wall (up 192) | As RT20. | as RT6 | as RT20 | High | |
| RT24 | 4160,240 | 4224 | roof / hotel dip (down 40) | As RT21. The HOTEL box sinks into the slab and its label is cut by the wall. | as RT6, Sc.drawProp | as RT21 | Med | |
| RT25 | 4160,240 | 4320 | dip / roof | As RT24. | as RT6 | as RT21 | Med | |
| RT26 | 4160,240 | 4384 | roof / dip | As RT24. | as RT6 | as RT21 | Med | |
| RT27 | 4160,240 | 4480 | dip / roof | As RT24. | as RT6 | as RT21 | Med | |
| RT28 | 4480,120 | 4608 | roof / hotel chimney block (up 96) | As RT16. | as RT6 | as RT16 | High | |
| RT29 | 4480,120 | 4672 | block / roof | As RT17. | as RT6 | as RT16 | High | |
| RT30 | 4480,240 | 4800 | roof / light court (down 288) | The court is a slot 400 px wide. Its back is the LIGHT COURT decor box: a pale panel in an 8 px frame of sky. The court's walls are plain slate. | Sc.paintGroundGrey, Sc.drawProp (decor box) | Court walls as wall faces with windows down to the floor, the back a darker courtyard wall with no sky behind it. | High | 12 |
| RT31 | 5120,120 | 5200 | light court / wall up 384 | As RT6, 384 px tall. | as RT6 | as RT6, four window rows. | High | |
| RT32 | 5120,120 | 5424 | roof / scaffold dip (down 40) | As RT21. | as RT6 | as RT21 | Med | |
| RT33 | 5440,120 | 5568 | dip / roof | As RT22. | as RT6 | as RT21 | Med | |
| RT34 | 5440,0 | 5696 | roof / wall up 96 | As RT6. | as RT6 | as RT6 | High | |
| RT35 | 5760,0 | 5856 | roof / yard dip (down 40) | As RT21. | as RT6 | as RT21 | Med | |
| RT36 | 5760,0 | 6000 | yard / chimney stacks (up 136) | As RT6. The CHIMNEY STACKS box is a pale label panel on it. | as RT6 | as RT16 | High | |
| RT37 | 6080,0 | 6104 | chimney / roof (down 96) | As RT17. | as RT6 | as RT16 | High | |
| RT38 | 6080,0 | 6176 | roof / sauna dip (down 40) | As RT24; the SAUNA ROOF label is cut ("SAUNA ROO"). | as RT6, Sc.drawProp | as RT21 | Med | 11 |
| RT39 | 6080,0 | 6272 | dip / roof | As RT38. | as RT6 | as RT21 | Med | 11 |
| RT40 | 6080,0 | 6400 | roof / nest chimney (up 96) | As RT16. | as RT6 | as RT16 | High | |
| RT41 | 6400,0 | 6432 | chimney top / the long roof down | As RT1: a 45 degree slate wedge, then three more down to the roof cafe. Reads as a hillside. | as RT1 | A pitched roof run as tiles on the slope tile, with a gutter and a ladder or roof steps at each landing. | High | |
| RT42 | 6400,0 | 6528 | slope / landing | As RT2. | as RT1 | as RT2 | Med | |
| RT43 | 6400,0 | 6656 | landing / slope | As RT41. | as RT1 | as RT41 | High | |
| RT44 | 6720,120 | 6752 | slope / landing | As RT2. | as RT1 | as RT2 | Med | |
| RT45 | 6720,120 | 6848 | landing / slope | As RT41. | as RT1 | as RT41 | High | |
| RT46 | 6720,240 | 6944 | slope / landing | As RT2. | as RT1 | as RT2 | Med | |
| RT47 | 6720,240 | 7040 | landing / slope | As RT41. | as RT1 | as RT41 | High | |
| RT48 | 7040,360 | 7136 | slope / roof cafe | As RT2. The RAILING box stands on the slab's edge. | as RT1, Sc.drawProp | as RT2, a railing tile. | Med | |

### Söder Hill (greybox, town style; `Sc.paintGroundGrey`; terrain from `level/soder.map`, `tools/make_soder.py`)

The street steps down 16 px at six stair flights (x 400, 1176, 1936, 2616, 3216, 3896) and has seven open cellar
hatches (gaps in the map, `L.hatches`).

| # | Camera x,y | World x | Ground A / B | What is wrong | Drawn by | Good transition | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SH1 | 320,0 | 400 | street / stair flight 1 (head) | The street bends into a 16 px ramp with a 1 px stepped edge. Street and stairs are one slate fill: no treads, nosing, cheek wall or kerb. Reads as a bump in the road. | Sc.paintGroundGrey, slope cells in level/soder.map | Two 8 px stone steps (River Walk's step tile, Sc.STEP_RW on day/07nov-ground) with a lit nosing, the cobbles ending in a kerb at the head, a cheek wall with coping on the near side. | Med | 06 |
| SH2 | 320,0 | 416 | flight 1 foot / street | The ramp's foot runs into the street line. | as SH1 | A landing slab where the last tread meets the cobbles. | Med | 06 |
| SH3 | 960,0 | 1040 | street / cellar hatch 1 | The street ends in a vertical cut. A black slot runs from the street to the screen bottom. The open lid is two 2 px sticks. Reads as a bottomless crack. | chase.lua Ch.drawBack (slot box, lid sticks), the gap in level/soder.map | Hatch piece: an iron frame 2 px with a lit edge flush with the cobbles, the lid a plank door leaning back, dark only 24 px deep with a cellar step showing, then a falloff. | High | 05 |
| SH4 | 960,0 | 1072 | hatch 1 / street | As SH3, mirrored. | as SH3 | as SH3 | High | 05 |
| SH5 | 960,0 | 1176 | street / flight 2 head | As SH1. | as SH1 | as SH1 | Med | 06 |
| SH6 | 960,0 | 1192 | flight 2 foot / street | As SH2. | as SH1 | as SH2 | Med | 06 |
| SH7 | 1600,0 | 1824 | street / hatch 2 | As SH3. | as SH3 | as SH3 | High | |
| SH8 | 1600,0 | 1856 | hatch 2 / street | As SH4. | as SH3 | as SH3 | High | |
| SH9 | 1920,0 | 1936 | street / flight 3 head | As SH1. | as SH1 | as SH1 | Med | |
| SH10 | 1920,0 | 1952 | flight 3 foot / street | As SH2. | as SH1 | as SH2 | Med | |
| SH11 | 2240,0 | 2320 | street / hatch 3 | As SH3. | as SH3 | as SH3 | High | |
| SH12 | 2240,0 | 2344 | hatch 3 / street | As SH4. | as SH3 | as SH3 | High | |
| SH13 | 2240,0 | 2424 | street / hatch 4 | As SH3. | as SH3 | as SH3 | High | |
| SH14 | 2240,0 | 2456 | hatch 4 / street | As SH4. | as SH3 | as SH3 | High | |
| SH15 | 2560,0 | 2616 | street / flight 4 head | As SH1. | as SH1 | as SH1 | Med | |
| SH16 | 2560,0 | 2632 | flight 4 foot / street | As SH2. | as SH1 | as SH2 | Med | |
| SH17 | 2880,0 | 3040 | street / hatch 5 | As SH3. | as SH3 | as SH3 | High | |
| SH18 | 2880,0 | 3080 | hatch 5 / street | As SH4. | as SH3 | as SH3 | High | |
| SH19 | 3200,0 | 3216 | street / flight 5 head | As SH1. | as SH1 | as SH1 | Med | |
| SH20 | 3200,0 | 3232 | flight 5 foot / street | As SH2. | as SH1 | as SH2 | Med | |
| SH21 | 3520,0 | 3600 | street / hatch 6 | As SH3. | as SH3 | as SH3 | High | |
| SH22 | 3520,0 | 3632 | hatch 6 / street | As SH4. | as SH3 | as SH3 | High | |
| SH23 | 3520,0 | 3720 | street / hatch 7 | As SH3. | as SH3 | as SH3 | High | |
| SH24 | 3520,0 | 3752 | hatch 7 / street | As SH4. | as SH3 | as SH3 | High | |
| SH25 | 3840,0 | 3896 | street / flight 6 head | As SH1. | as SH1 | as SH1 | Med | |
| SH26 | 3840,0 | 3912 | flight 6 foot / quay | As SH2. | as SH1 | as SH2 | Med | |
| SH27 | all,0 | whole street | street back edge / far town | The far town's grey blocks stand straight on the street's top line. No house fronts, no pavement edge, nothing between the street and the skyline. | Sc.drawFarGrey (town style, base 172), Sc.paintGroundGrey | The Söder house fronts stepping down the hill along the back edge (asset plan SH1), a 1 px shadow under them. Interim: a back pavement band and a plinth row by rule. | Med | |
| SH28 | 4800,0 | 5096-5120 | quay / RAILING box, level end | The street ends at a grey box labelled RAILING, then the world edge. | Sc.drawProp | The quay railing tile (SH3 kit), the coping and the water beyond. | Low | |

### Night Harbour (greybox, town style, `L.dark`; `Sc.paintGroundGrey` under `Nt.draw`; terrain from `level/night.map`, `tools/make_night_map.py`)

Eight water gaps in the quay (y 184, water from y 208). Over the darkness `Nt.draw` adds a 1 px moonlit line on every
floor and a dashed line on the water (night.lua:366).

| # | Camera x,y | World x | Ground A / B | What is wrong | Drawn by | Good transition | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NH1 | 320,0 | 400 | quay / water | The quay is a dark slab ending in a vertical cut to the screen bottom. The moonlit line stops at the corner. The water is one flat box with a dashed 1 px line. No coping, wet band, ripple or reflection. | Sc.paintGroundGrey; Nt.draw moonlit tops and water line | River Walk's quay-end cap (day/07nov-ground, Sc.paintQuay quay-end pass: coping 2 px over with its shadow, wet arris, ripple, reflection) in the night palette, and the nearest light as a broken column in the water. | Med | |
| NH2 | 320,0 | 448 | water / quay | As NH1, mirrored. | as NH1 | as NH1 | Med | |
| NH3 | 960,0 | 1000 | quay / water (old jetty) | As NH1. The jetty planks float 24 px over the gap with nothing under them (NW5). | as NH1 | as NH1, plus jetty piles (NW5). | High | 03 |
| NH4 | 960,0 | 1160 | water / quay | As NH3, mirrored. | as NH1 | as NH3 | High | 03 |
| NH5 | 1280,0 | 1320 | quay / water (rowboat) | As NH1. | as NH1 | as NH1 | Med | 04 |
| NH6 | 1280,0 | 1560 | water / quay | As NH2. | as NH1 | as NH1 | Med | |
| NH7 | 2240,0 | 2280 | quay / water (rotten planks) | As NH3. | as NH1 | as NH3 | High | |
| NH8 | 2240,0 | 2520 | water / quay | As NH4. | as NH1 | as NH3 | High | |
| NH9 | 2560,0 | 2600 | quay / water (two boats) | As NH1. | as NH1 | as NH1 | Med | |
| NH10 | 2560,0 | 2712-2728 | water / mooring POST | A 16 px slate column from the water bottom, its top a box labelled POST with a lantern on it. No wet band at the waterline. | Sc.drawProp (solid prop), Nt.drawLights | A timber pile with a cap, a wet dark band at the waterline, a ripple ring. | Med | |
| NH11 | 2560,0 | 2840 | water / quay | As NH2. | as NH1 | as NH1 | Med | |
| NH12 | 3200,0 | 3240 | quay / water | As NH1. | as NH1 | as NH1 | Med | |
| NH13 | 3200,0 | 3400 | water / pier stub | A 24 px slab of quay stands in the gap, vertical cuts both sides. | Sc.paintGroundGrey, level/night.map | A stone pier: NH1's cap both sides, coping on top. | Med | |
| NH14 | 3200,0 | 3424 | pier stub / water | As NH13. | as NH13 | as NH13 | Med | |
| NH15 | 3200,0 | 3520 | water / quay | As NH2. | as NH1 | as NH1 | Med | |
| NH16 | 3520,0 | 3800 | quay / water (slipway) | As NH1. The plan calls it a slipway, but it is the same vertical cut. | as NH1 | A slipway: a 2 px slope tile running into the water (the City Park near-bank rule, Sc.nearBanks, in stone). | Med | |
| NH17 | 3840,0 | 4080 | water / quay | As NH2. | as NH1 | as NH1 | Med | |
| NH18 | all,0 | whole quay | quay back edge / far town | As SH27: the far town stands on the quay's top line. | Sc.drawFarGrey, Sc.paintGroundGrey | Warehouses and cranes along the back edge (asset plan NH1), a shadow row. | Low | |

## 2. Weirdness, top 15 per level

Ranked by what the owner would notice first. Same columns as the joins, plus "Reads as".

### Rooftops

| # | Camera x,y | World x | Thing | Reads as | What is wrong | Drawn by | Good fix | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RW1 | every frame | all | text labels (CAFE, STAIRWELL A, ATTIC, ROOF WALKWAY, HOTEL, LIGHT COURT, BALCONY ...) | a debug view | The names of the boxes are printed in the play view. | Sc.drawProp (scene.lua:718), Sc.label | Labels only in the debug view (tests_cards.lua already blanks them for cards). | High | 10, 12 |
| RW2 | 3200,720 to 7152,720 | all | the buildings | a blue-grey cliff | Roofs, walls and slopes are one slate fill. 88 of 216 frames are over 85 % one colour. No facade, window, coping or edge but a 1 px line. | Sc.paintGroundGrey | Wall faces and roofs by rule from a wall and roof kit (RT1 to RT48; asset plan RT3, RT4). | High | 09 |
| RW3 | 640,720; 1600,600; 1920,600 | 896-1024, 1792-1920, 2112-2240 | pitched roofs R1, R2, R3 | mountain peaks | Plain triangles, the same colour as the flat roofs and walls. | Sc.paintGroundGrey | Gable ends, tiles on a slope tile, ridge caps (RT3). | High | 09 |
| RW4 | 1600,720; 2240,600; 2880,360 | 1424-3776 | one-way slabs: ATTIC, PIGEON LOFT, ROOF WALKWAY and eleven unnamed 64-176 px slabs | girders floating in the sky | 6 px outlined bars with nothing under them and no wall behind them. | Sc.drawProp (outlined box), level/tiled/rooftops.lua props | A holder for every slab: brackets into a wall face, posts to the roof below, or a hung walkway with rails. | High | 10 |
| RW5 | x 0 to 3200 at camY 480 and up | all | the backdrop | the level is in the clouds | The far town is drawn at a fixed base (172) and slides off at the upper tiers: from camY 480 up the sky runs to the screen bottom under every slab. | Sc.drawFarGrey (scene.lua:340), Sc.vshift | A far town seen from above with its own ground, shifted with the tiers (as the City Park mid lawn fix for CP9); final art RT1, RT2. | High | 10 |
| RW6 | 1600,720; 2240,600; 6080,0 | 1552-6268 | loose tiles (36 of them) | floating bricks | Orange 24 x 6 bars hang in the air between slabs and over wells. | roofs.lua Rf.drawPlay | A loose tile sitting in a roof's tile course, with the gap it leaves when it falls. | High | 11 |
| RW7 | 1920,600; 2880,360 | 1976, 2992 | lamp posts on slab ends | a lamp on a floating plank | A full street lamp stands on a 6 px slab with nothing under it. | Sc.lampGrey (scene.lua:504), lamps in rooftops.lua | A wall lantern on a bracket where there is a wall (as AH.wallLantern in Downtown), or a post with a foot bracket. | High | 10 |
| RW8 | 4800,480 | 4924 | the POST under the light court balcony | a column ending in mid-air | A 40 px post stops 56 px under the balcony it should hold. | Sc.drawProp; prop POST y 624-664 under BALCONY y 568 | Run the post up to the balcony (or brackets into the court wall). | High | 12 |
| RW9 | 4800,480 | 4808-5192 | LIGHT COURT box | a glass tank or cage | A pale panel inside an 8 px frame of brighter sky, with slabs and a post in front. | Sc.drawProp decor box (C.back) | A dark courtyard wall with windows filling the court, no sky behind. | Med | 12 |
| RW10 | 6080,120; 6400,120; 6720,120 | the nest chimney's far copy | landmark copy | a glass pillar | A pale 8 x 46 column with a nest on top is drawn at camY + 22. When a roof is near the top of the screen it seems to stand on it. | roofs.lua Rf.drawLandmark | Draw it on the far layer only, behind the far town, and never lower than the far skyline. | Med | 11 |
| RW11 | 320,960 | 576-768 | the way up from the street | a ski slope | A 192 px 45 degree wedge (RT1). | Sc.paintGroundGrey | Stairs in a stairwell (RT1). | Med | |
| RW12 | 6400,0 to 7040,360 | 6432-7136 | the long roof down | a hillside | Four 45 degree wedges and landings of plain slate (RT41-48). | Sc.paintGroundGrey | A tiled roof run with a gutter and roof steps (RT41). | Med | |
| RW13 | 4160,240; 6080,0 | 4056, 6112 | HOTEL, SAUNA ROOF boxes | a box sunk into the roof | The decor boxes sit half inside the slab and their labels are cut ("SAUNA ROO"). | Sc.drawProp | Fronts built from the kit, standing on the roof with a plinth and shadow. | Med | 11 |
| RW14 | 1600,720; 4800,480 | vents | steam vents with "?" and "!" | a floating question mark | The front-on vent hood is fine, but a grey "?" hangs over the bark vents and a yellow "!" over a warning one. | roofs.lua Rf.drawPlay | Keep the hood; show the cue as the hood's rattle and a wisp, or a hint bubble from talk.lua. | Low | 12 |
| RW15 | 2560,600; 4160,240; 5120,240 | 2880, 4540, 5340 | the geese and the gull | art from another game | Finished pixel-art birds stand on plain slate boxes: a style clash, not a scale clash. | critters.lua on the greybox | Goes away with the roof kit; no change to the birds. | Low | |

### Söder Hill

| # | Camera x,y | World x | Thing | Reads as | What is wrong | Drawn by | Good fix | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SW1 | every frame | all | text labels (CRATE, SIGN, BALCONY, BIKES, AWNING, PARASOL, TABLE, CART, ARCH, TERRACE, STAIRS, RAILING) | a debug view | The names of the boxes are printed in the play view. | Sc.drawProp, Sc.label | As RW1. | High | 07, 08 |
| SW2 | 2560,0 | 2692-2836 | cafe tables and parasols | two shelves on a pole | The table top floats 3 px over the street with no legs. The parasol is a flat bar. The pole is a 4 px decor box. | Sc.drawProp; props TABLE y 150-157, PARASOL y 108-112 in soder.lua | A table with legs to the street, a parasol canopy (a shallow front-on dome with a scalloped edge), the top as the one-way surface. | High | 07 |
| SW3 | 640,0; 2240,0; 4160,0 | 720, 2180, 4200 | hanging cafe signs | a box floating under a bar | The 32 x 37 SIGN box hangs 6 px under its bracket bar with nothing joining them. | Sc.drawProp; bracket decor y 62-66, SIGN y 72-109 | Two chains or rods from the bracket to the sign, the bracket fixed into a wall face. | High | 08 |
| SW4 | 960,0 and 6 more | 1040-3752 | open cellar hatches | a bottomless crack | A black slot to the screen bottom, the lid two 2 px sticks (SH3). | chase.lua Ch.drawBack | As SH3. | High | 05 |
| SW5 | 640,0; 3520,0 | 904-968, 3590-3770 | balconies | floating shelves | Thin bars with no wall, brackets or railing. | Sc.drawProp | An iron balcony on a house front: slab, two corbels, railing (asset plan SH3). | High | 08 |
| SW6 | 3200,0 | 3400-3432 | the ARCH | a floating pillar | A 32 x 61 grey box hangs 19 px over the street with nothing at its sides. | Sc.drawProp; prop ARCH y 112-173 | An arch with two piers to the street and the crawl space under its keystone. | High | |
| SW7 | 960,0 to 3840,0 | 6 flights | the stair flights | bumps in the road | 16 px smooth ramps (SH1). | Sc.paintGroundGrey | Stone steps (SH1). | Med | 06 |
| SW8 | 1600,0; 2880,0; 3520,0 | terraces | barrels | small crates that slide | 14 x 14 squares with two hoops. A barrel is round-ended and taller than wide; a rolling one turns. 14 px is the old small scale (plan D3: 20-22 px). | chase.lua barrel() | Barrel art at 20-22 px, 4 roll frames, hand-pixel (plan SH4, 0 credits; physics re-check). | Med | |
| SW9 | 1280,0 | 1480-1512 | the AWNING | a box on a stick | A 32 x 39 box hanging from a 4 px post. | Sc.drawProp | A low striped awning: arm, canvas front-on, scalloped valance. | Med | |
| SW10 | 1280,0 | 1340-1380 | parked BIKES | a crate | A 40 x 20 grey box. Also the old small scale (plan D3). | Sc.drawProp | Plan SH5: two fallen e-scooters at true scale. | Med | |
| SW11 | 2880,0 | 2940-2980 | fruit CART | a crate | A 40 x 40 grey box. | Sc.drawProp | A cart with wheels, crates of fruit, an awning. | Med | |
| SW12 | every frame | all | the street | a slab with nothing on it | One flat slate band from top to quay: no cobbles, no kerb, no house fronts (SH27). | Sc.paintGroundGrey, Sc.drawFarGrey | Cobbles (plan SH6, recolour town_ground.png, 0 credits) and house fronts (SH1). | Med | |
| SW13 | 1600,0; 2880,0; 3520,0 | 1872, 3120, 3776 | TERRACE decks | a box | Grey boxes labelled under, barrels on top. | Sc.drawProp | A timber deck on posts with a rail. | Med | |
| SW14 | 4800,0 | 4904-4984 | Mia's STAIRS | a sign board | A pale decor panel labelled STAIRS; Mia stands in front of it, not on stairs. | Sc.drawProp | A stair flight down to the quay from a house door. | Med | |
| SW15 | 4160,0 | 4300-4392 | bollards | stubs | Two 12 x 14 unlabelled boxes on the quay. | Sc.drawProp | Cast-iron bollards (plan SH3). | Low | |

### Night Harbour

| # | Camera x,y | World x | Thing | Reads as | What is wrong | Drawn by | Good fix | Sev | Crop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NW1 | every lamp | lamps 296, 1240, 2200, 3176, 3760 and the 12 other lights | light pools | fog discs, glass pillars | The darkness is multiplied away in a 96 px dithered disc. Inside it the pale greybox colours come back near white: the lamp post turns into a pale glass column and the far houses into a white panel. The Bayer dither ring is noisy. | night.lua lightSprite / Nt.draw (multiply), Sc.lampGrey drawn in C.back | Light pools that tint, not bleach: cap the light at the back layer's luma, a warm tint, dark lamp posts at night, a cleaner 2-step edge. | High | 01 |
| NW2 | 1280,0; 3200,0; 3840,0 | 1440, 3320, 3976 | boat lanterns | a lantern hanging in the air | The lights of kind "boat" are fixed points 20 px over the water on a 4 px stub pole. The boats row away under them. | night.lua Nt.drawLights (base 184, l.x fixed), L.lights in night.lua | Each boat light rides on its mover (s.movers) on a short mast in the boat. | High | 02 |
| NW3 | every frame | all | text labels (ROWBOAT, BOAT written on the water, BOXES, NET SHED, ROOF, STACK, TARP, CRATES, POST, LOW JETTY, TOWER, HOME, DOOR) | a debug view | Printed in the play view; BOAT and ROWBOAT are printed on the water. | Sc.drawProp, stage.lua mover labels (St:draw grey branch) | As RW1. | High | 04 |
| NW4 | every frame | Pepper | Pepper's own glow | a bubble round the dog | A 120 px light disc always follows her, so she walks in a white bubble. | Nt.draw stamp(p.x, p.y - 20, 60) | Keep a small rim light on her and a smaller pool; the lamps carry the light. | High | |
| NW5 | 960,0; 2240,0; 3200,0; 3840,0 | 1040-1152, 2308-2500, 3440-3504, 3960 | crumbling planks | planks floating in the air | Brown planks hang 24 px over the water with no piles or stringers. | night.lua drawPlanks | An old jetty: piles to the water, stringers, the crumbling planks on top. | High | 03 |
| NW6 | 1280,0; 2560,0; 3200,0; 3840,0 | 6 movers | rowboats and boats | dark shelves over the water | 48-56 x 6 bars hovering 6 px over the water line, no hull. | stage.lua St:draw (grey mover box) | Rowboat art sitting in the water (rowboat.png recoloured, plan NH6). | High | 04 |
| NW7 | 960,0 to 3840,0 | 8 gaps | quay ends | a slab cut with a knife | Vertical cuts into flat water (NH1). | Sc.paintGroundGrey | Quay-end caps (NH1). | Med | 03, 04 |
| NW8 | 4160,0 | 4240-4368 | Mia's house | a sign board | A grey box labelled HOME with two lit windows, a porch light and a DOOR label. | Sc.drawProp, Nt.drawLights | Mia's house front (plan NH4). | Med | |
| NW9 | 1600,0; 1920,0 | 1800-1872, 1952-2048 | NET SHED and fish shed | a bar on sticks; a shelf over a box | The net shed is a roof bar on two 4 px sticks; the ROOF bar floats over the fish shed box. | Sc.drawProp | Sheds with walls, a pitched roof seen front-on, the one-way roof on the roof. | Med | |
| NW10 | 2560,0 | 2712-2728 | the mooring POST | a pillar in the sea | A slate column labelled POST with a lantern on top (NH10). | Sc.drawProp | A timber pile (NH10). | Med | |
| NW11 | 1280,0; 2560,0 | 1460, 2780 | front mooring piles | dark stubs | Two 12 x 19 dark boxes stick up from the screen bottom. | Sc.drawProp (front layer) | Pile tops with caps and a wet band, or leave them out. | Med | 02 |
| NW12 | every frame | water | the water | a flat floor | One colour with a dashed line; no depth band, no lamp reflections. | Sc.paintGroundGrey (C.pond), Nt.draw water line | Night water from water.png recoloured (plan NH6), lamp reflections. | Med | 03 |
| NW13 | 640,0; 1920,0; 3520,0 | 520-584, 1712, 1912, 3600-3696 | crates, BOXES, STACK, TOWER | plain boxes | Labelled grey boxes with a moonlit outline. | Sc.drawProp, Nt.draw moonlit sides | Fish crates from the harbour kit (plan NH3). | Med | |
| NW14 | 640,0 | 760-848 | TARP over the beached boat | a box | A grey box labelled TARP. | Sc.drawProp | A tarp over a boat shape (plan NH3). | Low | |
| NW15 | every frame | all floors | moonlit edges | a wire frame | A 1 px pale line on every floor top and down the sides of every solid prop. | Nt.draw (n.tops, prop sides) | Keep it on tops only; let the art's own lit edge do it once there is art. | Low | |

## 3. Common causes

Shared with levels 1 to 3 (their cause numbers):

1. **One column at a time** (cause 1). `Sc.paintGroundGrey` paints each column from `columnRuns` with one fill and one
   edge row. In the greybox there is not even a second recipe, so every kind of ground is the same slab and every join
   is missing, not just cut (all 94 joins).
2. **Slopes are the flat recipe** (cause 3). Rooftops' stair slope, pitched roofs and long roof, and Söder's six stair
   flights are plain fill with a 1 px stepped edge (RT1-5, RT9-15, RT41-48, SH1-26 odd rows).
3. **No contact pass** (cause 4). `St:draw` only shadows props with art or a fence, so greybox boxes stand on the
   ground with nothing (crates, tables, the TERRACE, the POST, the HOME box).
4. **Layers with no ground of their own** (cause 5). `Sc.drawFarGrey` draws the far town on a fixed base 172. In
   Rooftops it leaves the screen from camY 480 up (RW5); in Söder and Night it stands straight on the play line
   (SH27, NH18).

New in levels 4 to 6:

5. **Greybox shown as the game.** No `L.art`, labels printed by `Sc.drawProp` and the mover branch of `St:draw`
   (RW1, SW1, NW3), plain boxes for every prop (RW13, SW9-11, SW13-15, NW8-9, NW13-14).
6. **Things placed from a fixed point, not from what holds them.** The data has a slab, sign, table or lantern with no
   holder, or the holder as a separate box with a gap: boat lights fixed while boats move and poles cut at y 184
   (NW2), signs 6 px under their brackets (SW3), tables 3 px over the street (SW2), the POST 56 px short (RW8), lamp
   posts on 6 px slabs (RW7), the landmark copy at camY + 22 (RW10), all slabs and planks (RW4, SW5, NW5).
7. **Decor boxes as pale panels with sky round them.** `Sc.drawProp` fills decor in `C.back`; where the box is
   smaller than the gap behind it, the sky frames it and it reads as glass (RW9, RW13, SW14, NW8).
8. **The night light model.** Multiplying the darkness away brings the pale greybox colours back near white, so light
   pools read as fog and lamp posts as glass (NW1, NW4).
9. **Old small scale.** Barrels 14 px and bikes 40 x 20 against Pepper's 46 px a metre (SW8, SW10; asset plan D3).

### What the ground-joins kit on `origin/day/07nov-ground` gives levels 4 to 6

Read, not changed: `riverwalk/joins.lua`, `tools/make_ground_kit.py`, the `scene.lua` and `tests.lua` that use them.

- **Usable as is: the system.** The kind map, the rule table, the painters' marks and `Jn.check` are the right shape
  for these levels too.
- **Not usable as is: the kinds.** `Jn.kinds` has branches only for `def.ground == "quay"` (River Walk) and
  `def.art == "park"` (City Park). For levels 4 to 6 every column gets no kind, so `Jn.changes` finds 0 changes and
  `Jn.check` returns ok with nothing checked. River Walk's test requires `n > 0`; the same must hold for each new
  level, or the check passes empty.
- **Height changes in one kind.** `Jn.SAME` only exempts `ramp`. Rooftops has about 30 wall steps and dips inside
  one kind (roof to roof); each would fail as "changes height with no transition". It needs a wall step rule, not an
  exemption.
- **Parts that carry over (0 credits):** the 8 px stone step tile (`Sc.STEP_RW`, River Walk's ramps) for Söder's six
  flights (16 px = 2 steps) and Rooftops' stairs; the quay-end cap (`Sc.paintQuay` quay-end pass) for Night's 16
  quay/water joins once it takes the night palette; the 2 px slope tile of `Sc.nearBanks` for the slipway (NH16); the
  contact shadow under fronts.
- **Parts that do not carry over:** the three parts of `make_ground_kit.py` are City Park lawn (#9e983f): mid lawn,
  tufts, roots. Nothing for roofs, walls, cobbles, hatches or a harbour.
- **New parts needed:** wall step (coping, face, foot shadow), eaves and gutter, ridge cap, parapet, stair cheek,
  hatch frame and lid, pile and stringer, boat hull at the waterline. Geometry by rule; the roof and wall textures
  need the kit renders (family D).

## 4. Fix approach, by family

Credits are the asset plan's (`docs/asset_plan_22oct.md` 2.5, 2.7, 2.10), not re-priced: no jobs written, no
preflight run. Sizes: XS = an hour, S = half a day, M = a day or two, L = several days.

| Family | What | Fixes | Credits | Size |
| --- | --- | --- | --- | --- |
| A. Labels off | Greybox labels only in the debug view (`Sc.drawProp`, `Sc.label`, the mover branch of `St:draw`), as `tests_cards.lua` already does for cards. | RW1, SW1, NW3 | 0, built by rule | XS |
| B. Holders and contacts | A pass over the props by rule: every slab, balcony and walkway gets brackets into a wall or posts to the floor below; signs get chains to their bracket; tables get legs; planks get piles; the POST at 4924 reaches its balcony; boat lights ride their movers; lamps on slabs become wall lanterns; a 1 px contact shadow under every box. A check that fails on any slab or sign with nothing under or behind it. | RW4, RW7, RW8, SW2, SW3, SW5, SW6, NW2, NW5, NW9, NW10 | 0, built by rule | M |
| C. Ground kinds and rules for 4 to 6 | Extend `joins.lua`: kinds roof, wall, pitch, stair, street, hatch, quay, water, pier; rules for wall steps, roof to pitch, ridge, stairs (`Sc.STEP_RW`), hatch, quay to water (River Walk's cap), slipway; `n > 0` per level. The geometry of every join drawn from the level's palette. | all 94 joins (shape) | 0, built by rule | M to L |
| D. Surfaces and walls | Roof tiles, glass roof and wall faces with windows for Rooftops (plan RT3 part and RT4); cobbles and stair tiles for Söder (SH6, recolour town_ground.png); quay granite and night water (NH6, recolours). | RW2, RW3, RW11, RW12, SW12, NW7, NW12, and the joins' textures | Rooftops needs a render (RT4 36, roof part of RT3); Söder and Night 0 | M |
| E. Backdrops with their own ground | Interim, by rule: the far town given a ground strip and a vertical shift per tier, so no slab ever hangs over empty sky (as the CP9 fix). Final: far and mid layers RT1, RT2, SH1, SH2, NH1, NH2. | RW5, RW10, SH27, NH18 | interim 0; final needs a render (6 x 36 = 216) | S, then M |
| F. Night light model | Pools that tint and never pass the back layer's luma; dark lamp posts at night; a smaller glow on Pepper; lamp reflections in the water; a 2-step pool edge in place of the noisy dither ring. | NW1, NW4, NW12 | 0, built by rule | S |
| G. Props art | Roof kit (RT3: stairwell housings, chimneys, tank, planters, pigeon loft, sauna, roof bar), Söder props (SH3), harbour kit (NH3), Mia's house (NH4), the fox (NH5), key screens (RT0, SH0, NH0); barrels at 20-22 px by hand (SH4, 0 credits, physics re-check). | RW13, SW8-11, SW13-15, NW6, NW8, NW11, NW13, NW14 | needs a render: RT0 36 + RT3 108, SH0 36 + SH3 72, NH0 36 + NH3 36 + NH4 24 + NH5 78 | L |
| H. Tooling | The sweep skips Pepper when her floor is inside a solid column; fix the stale size in the `level/rooftops.lua` header. | sweep frames | 0 | XS |

Order that gives the owner the most for the least: A, B, F and E-interim first (all 0 credits, about three days),
then C with D's 0-credit parts. The render families (D for Rooftops, E-final, G) total about 678 credits before
reserves by the plan's prices (Rooftops 252, Söder 180, Night 246), and go through the art director's gates one pilot
at a time.

Check after the fix: the same sweep at every tier; `Jn.check` with `n > 0` on each of the three levels; a holder check
that lists every one-way slab, sign and light with nothing under or behind it.

## 5. Contact sheets and crops

Every screen at 1x, labelled with its camera x and y:

- `sheet_rooftops.png`: 24 x 9 frames, tiers camY 960 (bottom row of the world, top row of the sheet) to 0.
- `sheet_soder.png`: 16 frames, camY 0.
- `sheet_night.png`: 14 frames, camY 0.

The 12 worst, 4x (camera spots re-rendered with `LOOK_XS` / `LOOK_YS`, Pepper left out):

| Crop | Items |
| --- | --- |
| `01_nh_lamp_pool_glass_pillar_x1240.png` | NW1 |
| `02_nh_boat_lantern_in_air_x1440.png` | NW2, NW11 |
| `03_nh_jetty_planks_float_x1040.png` | NW5, NH3, NH4, NW12 |
| `04_nh_quay_end_rowboat_bar_x1320.png` | NH5, NW6, NW3 |
| `05_sh_cellar_hatch_slot_x1040.png` | SH3, SH4, SW4 |
| `06_sh_stair_flight_ramp_x1176.png` | SH5, SH6, SW7 |
| `07_sh_parasol_table_float_x2700.png` | SW2, SW1 |
| `08_sh_sign_balcony_float_x720.png` | SW3, SW5 |
| `09_rt_roof_and_wall_one_slab_x1856.png` | RT9, RT10, RW2, RW3 |
| `10_rt_walkway_in_empty_sky_x2984.png` | RW4, RW5, RW7 |
| `11_rt_landmark_pillar_loose_tiles_x6340.png` | RW10, RW6, RT38, RW13 |
| `12_rt_light_court_box_post_x4924.png` | RW8, RW9, RT30 |
