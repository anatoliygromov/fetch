-- Level 3: Downtown (greybox). Terrain is in downtown.map; this file places everything else.
-- Same format as citypark.lua. x, y in level pixels; y grows downwards; "feet" = the y Pepper stands on.
-- The street (feet) is y 184. The fountain's water starts at y 192. The level is 3520 px (11 screens). See
-- docs/downtown_beatsheet.md (the first 6 screens) and docs/progression.md.
--
-- Screens (320 px each). Manner: bounce and carry. New here: springy awnings and parasols (bounce = h), and a
-- long carry: after the cat, Pepper carries the ball through five screens of water, geese and cargo bikes.
--   1  Old town lane  tap A to hop up the crate steps
--   2  Cafe terrace   two cafe tables: crawl under them or jump on; their parasols are one-way tops, and from the
--                     second parasol a jump reaches the shop sign (gold bone)
--   3  Market         a stall: jump onto the counter, up onto its awning; a crate stack up to a second awning
--   4  Bakery row     a springy awning launches Pepper over a crate wall too high to jump; a springier one up to
--                     the bakery sign (gold bone). Holding Down she can stand on one.
--   5  The plaza      the cat sits on the ball on the statue's arm: bark it off, pick up the ball. A flower tub is a
--                     step up to the pedestal; the pedestal, the arm and the hat are a climb (gold bone on the hat)
--   6  The fountain   carry the ball over the basin: hop from rim to fountain bowl to rim. Or the high route: from
--                     the statue's arm along the balconies and over the fountain's top tier (gold bone)
--   7  Tram street    the cargo bike zone: up on the kiosk and the shelter roof while the baker's cargo bike
--                     passes (a vintage tram rolls by in the back lane, scenery)
--   8  Flower market  two geese: a bite knocks the ball out. Bark them off, or go high: the tub, the cafe table, the
--                     springy parasol, the balcony
--   9  The canal      the awning at the edge launches Pepper over the water onto the crates on the far quay
--  10  Flooded square three springy parasols in the water: bounce from one to the next, holding Right
--  11  Tram street    a faster cargo bike, every 4 s: the kiosk, the shelter, then Mia at the stairs down to the river:
--                     give her the ball (X), GOOD GIRL!
-- Falling in the water with the ball (fountain, canal) costs a heart; the ball goes back by the last lamp Pepper
-- carried it past (L.ballHomeAtLamps), or to the statue.
--
-- Story (level 2 of 3): in town the ball rolled away across the plaza and a cat sat on it. Pepper barks the cat
-- away and carries the ball to the girl, who waits at the stairs down to the river. Level 3 (River Walk): by the
-- river she throws it again and it lands on a ferry.
--
-- scenery = "greybox" keeps the greybox rules (no road, no traffic); L.art = "town" draws the scenery art over the
-- boxes (Sc.drawPropArt, Sc.drawFarArt; tools/make_town_art.py). Without L.art it is drawn as boxes again
-- (greyStyle = "town": far rooftops and spires, near facades; see Sc.drawFarGrey).
-- props: kind = solid | oneway | decor; layer = "back", "play", "front"; label = "top" / "below" places the name.
-- Secrets (L.secrets, counted on the tally): the shop sign, the statue's hat, the fountain's top tier (the
-- rooftop route).
local L = {}
L.name = "DOWNTOWN"
L.number = 3
L.title = "Pepper: Downtown"
L.scenery = "greybox"
L.greyStyle = "town"
L.art = "town"                -- scenery art (tools/make_town_art.py; drawn by Sc.drawPropArt from the boxes)
L.map = "level/downtown.map"
L.time = 300
L.start = { x = 60, y = 184 }

L.props = {
  -- screen 1: old town lane. The crates are steps: 16 px, then 16 px more.
  { name = "DOOR",     kind = "decor",  layer = "back", x0 = 0,    x1 = 28,   y0 = 120, y1 = 184 },
  { name = "",         kind = "solid",  layer = "play", x0 = 144,  x1 = 176,  y0 = 168, y1 = 184 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 176,  x1 = 208,  y0 = 152, y1 = 184, label = "top" },
  -- screen 2: cafe terrace. A table's box is only its top (y 158-165): 19 px to crawl under it, a held jump onto
  -- it. Its parasol (one-way, top y 114) is 44 px above the table top: a held jump. The shop sign (one-way, y 80)
  -- is 34 px above the second parasol: the gold bone.
  -- (r6/levels: 46% of the level's failures and 20 quits were here: Elsa could not crawl yet, Anna missed the
  -- held jump onto the table.) An apple crate splits the jump: a tap hop onto it (16 px), a tap hop from it onto the
  -- table (10 px up). The 36 px of street between them keep the crawl under the tables as the other way.
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 300,  x1 = 332,  y0 = 168, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 390,  x1 = 394,  y0 = 118, y1 = 158 },     -- parasol pole
  { name = "",         kind = "decor",  layer = "back", x0 = 372,  x1 = 376,  y0 = 165, y1 = 184 },     -- legs
  { name = "",         kind = "decor",  layer = "back", x0 = 408,  x1 = 412,  y0 = 165, y1 = 184 },
  { name = "TABLE",    kind = "solid",  layer = "play", x0 = 368,  x1 = 416,  y0 = 158, y1 = 165, label = "below" },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 360,  x1 = 424,  y0 = 114, y1 = 118, label = "below" },
  { name = "",         kind = "decor",  layer = "back", x0 = 502,  x1 = 506,  y0 = 118, y1 = 158 },
  { name = "",         kind = "decor",  layer = "back", x0 = 484,  x1 = 488,  y0 = 165, y1 = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 520,  x1 = 524,  y0 = 165, y1 = 184 },
  { name = "TABLE",    kind = "solid",  layer = "play", x0 = 480,  x1 = 528,  y0 = 158, y1 = 165, label = "below" },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 472,  x1 = 536,  y0 = 114, y1 = 118, label = "below" },
  { name = "",         kind = "decor",  layer = "back", x0 = 598,  x1 = 602,  y0 = 76,  y1 = 184 },     -- sign post
  { name = "SIGN",     kind = "oneway", layer = "play", x0 = 560,  x1 = 600,  y0 = 80,  y1 = 84,  label = "below" },
  -- screen 3: market. The stall's counter is 28 px up (a held jump), its awning 40 px above the counter. The crate
  -- stack is two steps (16, then 32 px) to the second awning (40 px above the top crate); the street under it is
  -- clear.
  { name = "",         kind = "decor",  layer = "back", x0 = 682,  x1 = 686,  y0 = 116, y1 = 184 },     -- stall posts
  { name = "",         kind = "decor",  layer = "back", x0 = 754,  x1 = 758,  y0 = 116, y1 = 184 },
  { name = "STALL",    kind = "solid",  layer = "play", x0 = 688,  x1 = 752,  y0 = 156, y1 = 184 },
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 680,  x1 = 760,  y0 = 116, y1 = 120, label = "below" },
  { name = "",         kind = "solid",  layer = "play", x0 = 800,  x1 = 832,  y0 = 168, y1 = 184 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 832,  x1 = 864,  y0 = 152, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 932,  x1 = 936,  y0 = 112, y1 = 184 },     -- awning post
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 872,  x1 = 936,  y0 = 112, y1 = 116, label = "below" },
  -- screen 4: the bakery row (968-1288). Springy awnings (bounce = h: landing on one launches Pepper h px up;
  -- holding Down she stands on it). The crate stack (64 px, more than a jump and a scramble) is only crossed by
  -- bouncing off the first awning; the second, springier one reaches the bakery sign (gold bone).
  { name = "",         kind = "decor",  layer = "back", x0 = 1010, x1 = 1014, y0 = 152, y1 = 184 },     -- awning posts
  { name = "",         kind = "decor",  layer = "back", x0 = 1066, x1 = 1070, y0 = 152, y1 = 184 },
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 1008, x1 = 1072, y0 = 152, y1 = 156, label = "below", bounce = 76 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 1104, x1 = 1136, y0 = 120, y1 = 184, label = "top" },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 1136, x1 = 1168, y0 = 152, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 1234, x1 = 1238, y0 = 152, y1 = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1290, x1 = 1294, y0 = 152, y1 = 184 },
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 1232, x1 = 1296, y0 = 152, y1 = 156, label = "below", bounce = 100 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1308, x1 = 1312, y0 = 60,  y1 = 152 },     -- sign post
  { name = "SIGN",     kind = "oneway", layer = "play", x0 = 1270, x1 = 1310, y0 = 64,  y1 = 68,  label = "below" },
  -- screen 5: the plaza. A flower tub (28 px up: a tap hop and a scramble, or a held jump) stands before the
  -- pedestal, which is 12 px above it (40 px above the street: a held jump); the statue's arm is 36 px above the
  -- pedestal, its hat 32 px above the arm. The cat sits on the ball on the arm.
  { name = "TUB",      kind = "solid",  layer = "play", x0 = 1408, x1 = 1440, y0 = 156, y1 = 184, label = "top" },
  { name = "STATUE",   kind = "decor",  layer = "play", x0 = 1450, x1 = 1478, y0 = 80,  y1 = 144 },
  { name = "PEDESTAL", kind = "solid",  layer = "play", x0 = 1440, x1 = 1488, y0 = 144, y1 = 184 },
  { name = "ARM",      kind = "oneway", layer = "play", x0 = 1478, x1 = 1518, y0 = 108, y1 = 112, label = "below" },
  { name = "",         kind = "oneway", layer = "play", x0 = 1452, x1 = 1476, y0 = 76,  y1 = 80 },      -- the hat
  -- the high route (the rooftops): three houses at the back of the plaza (decoration, base y 174) with balconies
  -- (one-way, y 104, 96, 104) and the fountain's top tier (one-way, y 104) between them. From the statue's arm
  -- a running held jump reaches the first balcony; from the last, Pepper drops to the street by the lamp.
  { name = "HOUSE",    kind = "decor",  layer = "back", x0 = 1536, x1 = 1624, y0 = 56,  y1 = 174, label = "top" },
  { name = "HOUSE",    kind = "decor",  layer = "back", x0 = 1644, x1 = 1724, y0 = 48,  y1 = 174, label = "top" },
  { name = "HOUSE",    kind = "decor",  layer = "back", x0 = 1832, x1 = 1900, y0 = 56,  y1 = 174, label = "top" },
  { name = "BALCONY",  kind = "oneway", layer = "play", x0 = 1552, x1 = 1608, y0 = 104, y1 = 108, label = "below" },
  { name = "BALCONY",  kind = "oneway", layer = "play", x0 = 1656, x1 = 1712, y0 = 96,  y1 = 100, label = "below" },
  { name = "",         kind = "decor",  layer = "back", x0 = 1788, x1 = 1796, y0 = 108, y1 = 128 },     -- the tier's column
  { name = "TIER",     kind = "oneway", layer = "play", x0 = 1768, x1 = 1816, y0 = 104, y1 = 108, label = "below" },
  { name = "BALCONY",  kind = "oneway", layer = "play", x0 = 1840, x1 = 1896, y0 = 104, y1 = 108, label = "below" },
  -- screen 6: the fountain. The basin's water is x 1736-1848 (from y 192); the rims are 16 px up (a hop), the
  -- fountain bowl in the middle 24 px up, 40 px from each rim: a tapped hop from rim to bowl to rim.
  { name = "",         kind = "decor",  layer = "back", x0 = 1736, x1 = 1848, y0 = 184, y1 = 240 },     -- the basin's inside
  { name = "RIM",      kind = "solid",  layer = "play", x0 = 1720, x1 = 1736, y0 = 168, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 1786, x1 = 1798, y0 = 128, y1 = 160 },     -- spout
  { name = "FOUNTAIN", kind = "solid",  layer = "play", x0 = 1776, x1 = 1808, y0 = 160, y1 = 240, label = "top" },
  { name = "RIM",      kind = "solid",  layer = "play", x0 = 1848, x1 = 1864, y0 = 168, y1 = 184, label = "top" },
  -- screen 7: tram street. The kiosk (36 px up) and the shelter roof (one-way, 12 px above the kiosk) are above
  -- the cargo bike's box (26 px). The stairs down to the river are at the end of the level (terrain slopes, x 3488-3520).
  -- a courtyard gate after the fountain (r8/levels D1; it was the tram shed: the same art and box): the end of the
  -- first cargo bike's run. Its roof (36 px up, a hop from the fountain's rim) is a perch; the bike rides into the
  -- courtyard through the gateway on the right (depot = 1938) and is gone.
  { name = "GATE", kind = "solid", layer = "play", x0 = 1868, x1 = 1938, y0 = 148, y1 = 184, label = "top" },
  { name = "KIOSK",    kind = "solid",  layer = "play", x0 = 1980, x1 = 2020, y0 = 148, y1 = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 2052, x1 = 2056, y0 = 140, y1 = 184 },     -- shelter posts
  { name = "",         kind = "decor",  layer = "back", x0 = 2112, x1 = 2116, y0 = 140, y1 = 184 },
  { name = "SHELTER",  kind = "oneway", layer = "play", x0 = 2048, x1 = 2120, y0 = 136, y1 = 140, label = "below" },
  -- screen 8: the flower market (2136-2456), carrying the ball. Two geese on the cobbles: a bite knocks the ball
  -- out of Pepper's mouth. Bark them off, or go high: the tub, the cafe table, the springy parasol, the balcony.
  { name = "TUB",      kind = "solid",  layer = "play", x0 = 2280, x1 = 2312, y0 = 156, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 2366, x1 = 2370, y0 = 118, y1 = 158 },     -- parasol pole
  { name = "",         kind = "decor",  layer = "back", x0 = 2348, x1 = 2352, y0 = 165, y1 = 184 },     -- legs
  { name = "",         kind = "decor",  layer = "back", x0 = 2384, x1 = 2388, y0 = 165, y1 = 184 },
  { name = "TABLE",    kind = "solid",  layer = "play", x0 = 2344, x1 = 2392, y0 = 158, y1 = 165, label = "below" },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 2336, x1 = 2400, y0 = 114, y1 = 118, label = "below", bounce = 64 },
  { name = "HOUSE",    kind = "decor",  layer = "back", x0 = 2404, x1 = 2492, y0 = 56,  y1 = 174, label = "top" },
  { name = "BALCONY",  kind = "oneway", layer = "play", x0 = 2420, x1 = 2476, y0 = 88,  y1 = 92,  label = "below" },
  -- screen 9: the canal (2456-2776). Its water (x 2560-2624, from y 192) runs under a wall of crates 64 px
  -- high on the far quay: too high to jump. The springy awning at the edge launches Pepper over the water onto them.
  { name = "",         kind = "decor",  layer = "back", x0 = 2498, x1 = 2502, y0 = 152, y1 = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 2554, x1 = 2558, y0 = 152, y1 = 184 },
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 2496, x1 = 2560, y0 = 152, y1 = 156, label = "below", bounce = 80 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 2624, x1 = 2656, y0 = 120, y1 = 240, label = "top" },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 2656, x1 = 2688, y0 = 120, y1 = 184, label = "top" },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 2688, x1 = 2720, y0 = 152, y1 = 184, label = "top" },
  -- screen 10: the flooded square (2784-3104). The water (x 2816-3072, from y 192) is too wide to jump; three
  -- springy parasols stand in it on their poles (tops y 136, 88 px apart). A crate at the edge is the step up to
  -- the first (from the street it is 48 px: more than a jump). Each one launches her 56 px: hold Right and she
  -- bounces from one to the next and over to the tram shed's roof on the far side (Lion King's hippos and rhinos, our way).
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 2788, x1 = 2816, y0 = 168, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 2854, x1 = 2858, y0 = 140, y1 = 240 },     -- parasol poles
  { name = "",         kind = "decor",  layer = "back", x0 = 2942, x1 = 2946, y0 = 140, y1 = 240 },
  { name = "",         kind = "decor",  layer = "back", x0 = 3030, x1 = 3034, y0 = 140, y1 = 240 },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 2832, x1 = 2880, y0 = 136, y1 = 140, label = "below", bounce = 56 },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 2920, x1 = 2968, y0 = 136, y1 = 140, label = "below", bounce = 56 },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 3008, x1 = 3056, y0 = 136, y1 = 140, label = "below", bounce = 56 },
  -- screen 11: tram street again (3104-3424): a faster cargo bike, every 4 s (wait for two). The gate's roof (the
  -- bounce off the last parasol lands on it), then a shelter roof a running jump away. Then Mia at the stairs down
  -- to the river. The second cargo bike's run ends in a courtyard gate at the far side of the flooded square: the
  -- last bounce lands on its roof, and the bike rides in through its gateway (depot = 3168)
  { name = "GATE", kind = "solid", layer = "play", x0 = 3072, x1 = 3168, y0 = 148, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 3240, x1 = 3244, y0 = 140, y1 = 184 },     -- shelter posts
  { name = "",         kind = "decor",  layer = "back", x0 = 3300, x1 = 3304, y0 = 140, y1 = 184 },
  { name = "SHELTER",  kind = "oneway", layer = "play", x0 = 3236, x1 = 3308, y0 = 136, y1 = 140, label = "below" },
  { name = "RIVER",    kind = "decor",  layer = "back", x0 = 3456, x1 = 3484, y0 = 120, y1 = 140 },     -- sign
  { name = "",         kind = "decor",  layer = "back", x0 = 3468, x1 = 3472, y0 = 140, y1 = 184 },
  -- foreground frame: arcade pillars
  { name = "",         kind = "decor",  layer = "front", x0 = 620,  x1 = 632,  y0 = 221, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 1900, x1 = 1912, y0 = 221, y1 = 240 },
}

-- lamp posts: every one is a checkpoint
L.lamps = {                    -- one every 1.5 screens or so (City Park: every screen)
  { x = 636,  y = 184, checkpoint = true },
  { x = 960,  y = 184, checkpoint = true },
  { x = 1620, y = 184, checkpoint = true },
  { x = 1959, y = 184, checkpoint = true },    -- (between the gate and the kiosk: 42 px, room for her)
  { x = 2528, y = 184, checkpoint = true },
  { x = 2764, y = 184, checkpoint = true },
}
-- a lamp Pepper reaches while carrying the ball becomes the ball's home: if it is lost (the fountain, the canal),
-- it comes back there, not all the way back at the statue
L.ballHomeAtLamps = true

L.movers = {}

-- the cat sits on the ball on the statue's arm; a bark within 90 px scares it off and the ball drops to the
-- street. If Pepper falls in the water with the ball, it goes back there (or by the last lamp she carried it to).
L.ball = { x = 1508, y = 108 }
L.cat = { x = 1508, y = 102, range = 90 }
L.ballBack = "THE BALL IS BY THE STATUE!"
L.pickupSay = "BRING ME THE BALL!"
-- the girl waits at the top of the stairs down to the river
L.girl = { x = 3460, y = 184 }
L.outro = { "A SEAGULL TOOK THE BALL!" }

-- bones: x, feet y (drawn floating 9 px above); super = 1,000 points
L.bones = {
  -- 1 old town lane: the crate steps
  { x = 100, y = 184 }, { x = 136, y = 184 }, { x = 160, y = 168 }, { x = 192, y = 152 }, { x = 232, y = 184 },
  { x = 268, y = 184 },
  -- 2 cafe terrace: on and under the tables, on the parasols, the shop sign
  { x = 380, y = 158 }, { x = 404, y = 158 }, { x = 392, y = 184 }, { x = 392, y = 114 }, { x = 504, y = 158 },
  { x = 504, y = 114 }, { x = 580, y = 80, super = true }, { x = 604, y = 184 },
  -- 3 market: the counter, the awnings, the crates
  { x = 708, y = 156 }, { x = 720, y = 116 }, { x = 816, y = 168 }, { x = 848, y = 152 }, { x = 888, y = 112 },
  { x = 912, y = 112 }, { x = 920, y = 184 },
  -- 4 the plaza: the pedestal, the hat
  { x = 1320, y = 184 }, { x = 1350, y = 184 }, { x = 1424, y = 156 }, { x = 1452, y = 144 }, { x = 1476, y = 144 },
  { x = 1464, y = 76, super = true }, { x = 1550, y = 184 }, { x = 1570, y = 184 },
  -- 5 the fountain: over the water, on the bowl
  { x = 1660, y = 184 }, { x = 1728, y = 168 }, { x = 1758, y = 160 }, { x = 1792, y = 160 }, { x = 1826, y = 160 },
  { x = 1856, y = 168 }, { x = 1884, y = 148 },
  -- 5 the rooftops (the high route): the balconies, gold on the fountain's top tier
  { x = 1580, y = 104 }, { x = 1684, y = 96 }, { x = 1792, y = 104, super = true }, { x = 1868, y = 104 },
  -- 4 the bakery row: on the first awning, up over the crates, gold on the bakery sign
  { x = 1040, y = 152 }, { x = 1072, y = 104 }, { x = 1096, y = 88 }, { x = 1120, y = 120 }, { x = 1152, y = 152 },
  { x = 1264, y = 120 }, { x = 1290, y = 64, super = true },
  -- 7 tram street: the kiosk, the shelter roof
  { x = 1920, y = 148 }, { x = 1996, y = 148 }, { x = 2068, y = 136 }, { x = 2092, y = 136 },
  -- 8 the flower market: the tub, the table, high over the parasol, the balcony
  { x = 2200, y = 184 }, { x = 2296, y = 156 }, { x = 2368, y = 158 }, { x = 2368, y = 80 }, { x = 2400, y = 64 },
  { x = 2436, y = 88 }, { x = 2460, y = 88 },
  -- 9 the canal: over the water, along the crates
  { x = 2528, y = 152 }, { x = 2568, y = 96 }, { x = 2600, y = 88 }, { x = 2640, y = 120 }, { x = 2672, y = 120 },
  { x = 2704, y = 152 },
  -- 10 the flooded square: on the crate, high over each parasol
  { x = 2802, y = 168 }, { x = 2856, y = 136 }, { x = 2900, y = 84 }, { x = 2944, y = 136 }, { x = 2988, y = 84 },
  { x = 3032, y = 136 }, { x = 3076, y = 84 },
  -- 11 tram street again: the kiosk, the shelter, by Mia
  { x = 3148, y = 148 }, { x = 3260, y = 136 }, { x = 3284, y = 136 }, { x = 3432, y = 184 },
}

-- the cargo bike zones (the bike-zone code; D1, r8/levels: they were tram zones with the same numbers): the
-- baker's cargo bike rides right to left while Pepper is in the zone, into a courtyard through its gate: depot = the
-- gateway (the bike is drawn and hurts only right of it), endX = where it is all inside. w, h: its hit box
-- (80 x 26: the cargo box and the front wheel; the rider sits behind the box and is drawn tall, arthooks.lua);
-- rail: it keeps to the street's line (y 184) instead of following the ground, so it does not ride down the river
-- stairs. start = "enter": the first one sets off when Pepper walks into the zone (its bell rings 1 s before it is
-- on screen), then one every 6 s (4 s). 110 and 130 px/s: about 9 and 11 km/h, a loaded cargo bike's pace; the
-- tram's speeds, so the kiosk, the shelter and the gates are the same perches.
L.bikes = {
  { zoneX0 = 1930, zoneX1 = 2120, minY = 150, every = 6.0, speed = 110, endX = 1882, depot = 1938, kind = "cargo", w = 80, h = 26, rail = true, start = "enter" },
  { zoneX0 = 3120, zoneX1 = 3300, minY = 150, every = 4.0, speed = 130, endX = 3112, depot = 3168, kind = "cargo", w = 80, h = 26, rail = true, start = "enter" },
}
-- the back lane's vintage tram (D1; scenery, arthooks.lua): it runs behind Pepper's line (rails at y 174) on both
-- tram streets, stops at the tram stop sign by each shelter for 3 s and drives on to the left, now and then
L.trams = {
  { x0 = 1700, x1 = 2300, y0 = 44, y1 = 174, stop = 2124, every = 16, dwell = 3, speed = 110 },
  { x0 = 3020, x1 = 3520, y0 = 44, y1 = 174, stop = 3312, every = 16, dwell = 3, speed = 110 },
}
-- the geese on the flower market (critters.lua): one on the cobbles before the tub, one under the balcony
L.critters = {
  { kind = "goose", x = 2230, y = 184, x0 = 2190, x1 = 2262 },
  { kind = "goose", x = 2446, y = 184, x0 = 2424, x1 = 2470 },
}

-- secrets: reaching one (Pepper's feet in its box) counts it; the tally shows how many were found
L.secrets = {
  { name = "SHOP SIGN",   x0 = 548,  x1 = 612,  y0 = 70, y1 = 80 },
  { name = "STATUE HAT",  x0 = 1440, x1 = 1488, y0 = 66, y1 = 76 },
  { name = "ROOFTOPS",    x0 = 1756, x1 = 1828, y0 = 94, y1 = 104 },   -- the fountain's top tier
  { name = "BAKERY SIGN", x0 = 1258, x1 = 1322, y0 = 54, y1 = 64 },
}

-- hints (St:hint, drawn by talk.lua): first match wins. With btn ("a", "b", "x", "y", "down") it is Pepper's
-- control hint: a button picture and 1 to 3 words. Without, it is the girl's line. need: see St:zoneHint.
L.hints = {
  { x0 = 0,    x1 = 3520, btn = "y",    text = "BARK!",              need = "catnear" },
  { x0 = 0,    x1 = 3520, btn = "x",    text = "PICK UP",            need = "nearball" },
  { x0 = 3400, x1 = 3520, btn = "x",    text = "GIVE",               need = "ball" },
  { x0 = 0,    x1 = 3520, btn = "y",    text = "BARK: SHOO!",        need = "goose" },
  { x0 = 0,    x1 = 152,  btn = "a",    text = "TAP: HOP" },            -- up the crates
  { x0 = 336,  x1 = 368,  btn = "down", text = "CRAWL",              minY = 183 },   -- (r6/levels: the crate)
  { x0 = 240,  x1 = 300,  btn = "a",    text = "TAP: HOP",           minY = 183 },   -- onto the crate
  { x0 = 300,  x1 = 368,  btn = "a",    text = "TAP: HOP",           maxY = 169 },   -- from it onto the table
  { x0 = 640,  x1 = 688,  btn = "a",    text = "HOLD: BIG JUMP" },      -- onto the stall
  { x0 = 1384, x1 = 1440, btn = "a",    text = "HOLD: BIG JUMP" },      -- onto the pedestal
  { x0 = 1660, x1 = 1720, btn = "a",    text = "TAP: HOP" },            -- over the fountain
  { x0 = 968,  x1 = 1010, btn = "a",    text = "BOUNCE ON IT" },        -- the first springy awning
  { x0 = 1008, x1 = 1072, btn = "down", text = "HOLD: STAY ON",      maxY = 150 },   -- (above it, bouncing)
  { x0 = 1288, x1 = 1560, text = "THE CAT IS ON MY BALL!",    need = "cat" },
  { x0 = 1560, x1 = 3520, text = "GO BACK: BARK AT THE CAT!", need = "cat" },
  { x0 = 1600, x1 = 3520, text = "GO BACK FOR THE BALL!",     need = "noball" },
  { x0 = 1930, x1 = 2120, text = "BIG BIKE! GET UP HIGH!", bike = true },
  { x0 = 3120, x1 = 3300, text = "A FAST BIKE! GET UP!", bike = true },
  { x0 = 2136, x1 = 2190, text = "GEESE! DON'T LOSE MY BALL!", need = "ball" },
  { x0 = 2464, x1 = 2500, text = "BOUNCE OVER THE WATER!" },
  { x0 = 2784, x1 = 2832, btn = "a",    text = "BOUNCE ACROSS" },
  { x0 = 1720, x1 = 3520, text = "BRING ME THE BALL!", need = "ball" },
}

L.intro = { "LEVEL 3", "DOWNTOWN", "A CAT SITS ON THE BALL!" }
return L
