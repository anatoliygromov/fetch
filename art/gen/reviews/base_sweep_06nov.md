# Base sweep review: prod/integrate-e, all three levels (reviewer, 6-7 Nov night)

Independent reviewer. Branch `prod/integrate-e` at 7fe6c8f, before the night's art tracks. Every screen of
`riverwalk` (12), `citypark_tall` (27, tiers y 144 / 24 / 0) and `downtown_tall` (33, tiers y 240 / 120 / 0)
rendered with `LOOK_SWEEP=1 LOOK_STEP=320`, looked at as 2x contact sheets in colour and greyscale, suspect
spots at 4x. Camera x,y below are the sweep's camera (world px). The eye checks are the brief's: crisp, reads at
1x, true scale, nothing floats, layer ladder, consistency, "would the owner call it terrible, dirty, flat or
floating".

Already assigned to the three night tracks (marked COVERED): River Walk rowboat, harbour, pier band, gull and
cat size sheets; City Park willow, pond bank, floating log at the alder walk end, trunk pillars, keeper cart,
goose fly row; Downtown facade lift, floating high road, scale-break mini houses, tram shelter wireframe,
fountain basin.

## Not covered by any track (fix list, by impact)

### River Walk
1. **Foreground road band is dirty.** Every screen, y 199-240. `art/scene/road.png` (tools/make_road.py, drawn by
   scene.lua line 768-788 and look.lua ROAD_BANDS). `asset_qa.py --layer front --level rw`: FAIL, noise 3.3 %,
   stray 3.9 %, blotches 10.9 %, median luma 69 against the front row's 40. At 4x it is speckled asphalt with
   random light pixels. Fixed: a flat dark band in 3-4 shades (BIBLE front row: median 40, 3-8 colours, dark
   silhouette), kerb line, dashes, manhole; no dither.
2. **Jetty stub in the harbour (cam 2240,0; world 2400-2448, y 196-240).** `art/scene/rw_jetty.png` via
   setpieces.lua `jetty`. A 48 px plank top on three piles that run to the bottom of the screen over the water;
   reads as a table standing in the river. Fixed: piles end at a waterline with a dark wet band and a ripple,
   the deck wider than it is tall or joined to the quay. (The pier band track may take this; confirm.)
3. **Kennel is dolls'-house sized (cam 0,0; world 0-34, y 148-184).** `art/scene/kennel.png` 34 x 36 (0.75 m
   for a Labrador, Pepper is 46 px). Reads as a post box at 1x. Fixed: about 46 x 44 px with a visible arched
   doorway she fits in; keep the bone plate.
4. **Mooring rope is a taut 1 px line (cam 1280,0; world 1530-1660, y 225).** scene.lua harbour draw. A straight
   line across the water with no sag; the pontoon (`art/scene/pontoon.png`) has no waterline. Fixed: 2 px rope
   with a sag, a wet band under the pontoon. Part of the harbour track; listed in case it is not in scope.
5. **Grit boxes read as plain green slabs (cam 640,0 world 831-917; cam 3200,0 world 3240-3326).**
   `gritbox_front` is crisp but featureless. Fixed: a lid line, two hinges, a sand symbol. Low priority.

### City Park (tall)
1. **Empty sky over the high road (cam 960,0 to 960,24; also 0-320 at y 0-24).** scene.lua tier draw: the mid
   trees and far city scroll down (vcam FAR 0.3, MID 0.6) so from camY 56 and up, which the boughs at world y
   about 200 reach (camY = floor - 168) and look-up reaches, the top 100-140 px of the screen at x 900-1100 is
   bare gradient with one cloud. Fixed: a far canopy band or the big tree crowns extended across x 880-1150 at
   the top tier, as they already are at x 1280-1600.
2. **Trunk pillars sit on the mid layer's value (cam 1280,144; 1600,144).** In greyscale the back-layer trunks
   (world 1130-1200, 1480-1590) are the same grey as the mid-layer crowns and the far city. COVERED (trunk
   pillars track) but note the number: they need one palette step darker than the crowns, and the boughs on them
   stay darkest.
3. **Keeper has no face (cam 960,144; world 960-1010).** `art/scene/park_keeper_cart.png`: a beanie and a blank
   skin patch, no eye or mouth at 1x. COVERED (keeper cart) but listed as a checklist item 5 defect.
4. **Leaf front at the top tiers** (every x at camY under 112): dark leaf clumps along the bottom of the screen with
   no ground under them, in front of the trunks. This is plan decision 5 (owner 26 Oct, look.lua Look.leaves), so
   PASS as designed; note it is the first thing a player sees when the camera is up.

### Downtown (tall)
1. **Roof ledges hang on blank plaster as grey combs (cam 1920,240 and 1920,120; world 1920-1976 y 264, 2016-2072
   y 248, 2112-2168 y 264, 2416-2464 y 248).** `art/scene/town_roof_ledge.png` 3-sliced by arthooks.lua lines
   408-416 on DORMER and the unnamed oneway ledges. A stone cornice with corbels, 56 px wide, in the middle of a
   storey with no window, door or string course behind it. Fixed: a French window or a balcony door behind each
   ledge (as the iron balconies at world 1552-1608 have), or a string-course band along the facade at the ledge's
   height so it reads as a cornice. Not in the facade-lift scope as written.
2. **Parasols grow out of the flooded square (cam 2880,240; world 2832-3056, poles y 392-480).**
   Level objects at 2854, 2942, 3030 (4 px poles, 88-100 px tall) and PARASOL tops. Three 1 px grey poles rise
   from the water with no base, ripple or wet band. Fixed: a ripple ring and a dark wet 2 px on each pole at the
   waterline, the table top just under the surface, or a pontoon under each pole.
3. **Crate tower sinks below the street (cam 2560,240; world 2624-2656, y 360-480).** CRATES 32 x 120 and
   32 x 64 in level/tiled/downtown_tall.lua: the bottom two crates stand in front of the dark road band under the
   kerb, 56 px under the street line (y 424), with no water there. Fixed: the stack stands on the street (y1 424)
   with the same top, or it stands in water with a waterline on the bottom crate.
4. **Street lamp on a balcony (cam 1600,120; world 1830, y 256).** The checkpoint lamp (lamps object at 1830,
   256) stands on the GALLERY platform two storeys up. A street lamp on a balcony reads wrong. Fixed: a wall
   lantern (bracket) for high-road checkpoints, same light.
5. **Pavement end at the last screen (cam 3200,240; world 3497-3520).** The cobble kerb ends in a diagonal
   stepped block with a bollard silhouette in front. Fixed: run the kerb to the edge. Low priority.

## Screen-by-screen

PASS means I would show that screen to the owner as finished. A screen that only shows covered defects is marked
FAIL (covered) so the night's board can tick it.

### River Walk (12 screens, y 0)
| cam x | result | what is wrong |
| --- | --- | --- |
| 0 | FAIL | road band noise (RW1); kennel small (RW3) |
| 320 | FAIL | road band noise (RW1) |
| 640 | FAIL | road band noise (RW1); grit box plain (RW5) |
| 960 | FAIL | road band noise (RW1) |
| 1280 | FAIL (covered) | harbour: ferry hull drawn whole on the water, no wet hull; taut rope, flat pontoon (RW4) |
| 1600 | FAIL (covered) | ferry as above; gull 24 px wingspan at 1x (size sheet) |
| 1920 | FAIL (covered) | pier: stone block with balustrade, pier band track; gull |
| 2240 | FAIL | jetty stub (RW2); rowboats: flat orange hull sliver, rower a blue blob (covered) |
| 2560 | PASS | quay, lamp, stair, Pepper: clean |
| 2880 | FAIL | road band noise (RW1); gull small (covered) |
| 3200 | FAIL | road band noise (RW1); grit box plain (RW5) |
| 3520 | FAIL | road band noise (RW1); otherwise the end with Mia and the cafe is clean |

### City Park tall (27 screens)
| cam x | y 144 (path) | y 24 | y 0 |
| --- | --- | --- | --- |
| 0 | PASS: gate, leaf pile, log, stump, magpie, lamp | PASS (sky, unreachable) | PASS (unreachable) |
| 320 | PASS: bench, hedge | PASS (sky, unreachable) | PASS (unreachable) |
| 640 | FAIL (covered): willow crowns soft, pond bank slab, duck boat, deck | FAIL (covered): willow | PASS: bridge |
| 960 | FAIL (covered): keeper no face (CP3), trunk value (CP2) | FAIL: empty sky (CP1) | FAIL: empty sky (CP1) |
| 1280 | FAIL (covered): trunk value (CP2) | PASS: canopy, boughs | PASS |
| 1600 | FAIL (covered): trunk value (CP2) | PASS | PASS |
| 1920 | FAIL (covered): pond bank slab, stepping stones | FAIL (covered): floating log at the alder walk end | FAIL (covered): log |
| 2240 | PASS: pergola planks with lights, goose, bench, table | PASS | PASS |
| 2560 | PASS: playground, swing, Mia | PASS: nest, boughs | PASS |

### Downtown tall (33 screens)
| cam x | y 240 (street) | y 120 | y 0 |
| --- | --- | --- | --- |
| 0 | FAIL (covered): mini-house roofs and sky at the top of the street screen | FAIL (covered): mini houses beside the true-scale corner house | FAIL (covered): mini roofs |
| 320 | FAIL (covered): same | FAIL (covered) | FAIL (covered) |
| 640 | FAIL (covered): same | FAIL (covered) | FAIL (covered) |
| 960 | FAIL (covered): mini-house roof seam | FAIL (covered): seam mini to true scale | FAIL (covered) |
| 1280 | PASS: statue, loggia, balconies, crates | PASS: iron balconies with brackets, arcade | PASS: plain wall, windows crisp |
| 1600 | FAIL (covered): fountain basin, mini house between facades, stone high road floats | FAIL (covered): high road; lamp on balcony (DT4) | FAIL: lamp on balcony (DT4) |
| 1920 | FAIL: comb ledges (DT1); tram shelter wireframe (covered) | FAIL: comb ledges (DT1) | PASS |
| 2240 | FAIL: comb ledges (DT1); mini house under the bridge (covered) | FAIL: comb ledge at 2416 (DT1) | PASS |
| 2560 | FAIL: crate tower below street (DT3); mini houses right (covered) | FAIL (covered): mini houses | FAIL (covered) |
| 2880 | FAIL: parasols in the flood (DT2) | PASS | PASS |
| 3200 | FAIL: kerb end (DT5); tram shelter (covered) | PASS | PASS |

## Checks run
- `python3 -I tools/asset_qa.py --file riverwalk/art/scene/road.png --layer front --level rw`: FAIL (noise 3.3 %,
  stray 3.9 %, ladder 69 > 40, blotches 10.9 %).
- `pavement.png` front: noise 0.8 %, 16 colours, blotches 0.9 %: WARN (the owner keeps the light pavement).
- `town_ground.png` play: blotches 1.4 %, outline 2 % broken: WARN.
