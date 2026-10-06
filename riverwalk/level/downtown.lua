-- Level 2: Downtown (greybox). Terrain is in downtown.map; this file places everything else.
-- Same format as citypark.lua. x, y in level pixels; y grows downwards; "feet" = the y Pepper stands on.
-- The street (feet) is y 184. The fountain's water starts at y 192. The level is 1920 px (6 screens). See
-- docs/downtown_beatsheet.md.
--
-- Screens (320 px each):
--   1  Old town lane  tap A to hop up the crate steps
--   2  Cafe terrace   two cafe tables: crawl under them or jump on; their parasols are one-way tops, and from the
--                     second parasol a jump reaches the shop sign (gold bone)
--   3  Market         a stall: jump onto the counter, up onto its awning; a crate stack up to a second awning
--   4  The plaza      the cat sits on the ball on the statue's arm: bark it off, pick up the ball. The pedestal,
--                     the arm and the hat are a climb (gold bone on the hat)
--   5  The fountain   carry the ball over the basin: hop from rim to fountain bowl to rim. Falling in costs a heart, and the
--                     ball goes back to the plaza
--   6  Tram street    the tram zone: up on the kiosk and the shelter roof while the tram passes, then the girl
--                     waiting at the stairs down to the river: give her the ball (X), GOOD GIRL!
--
-- Story (level 2 of 3): in town the ball rolled away across the plaza and a cat sat on it. Pepper barks the cat
-- away and carries the ball to the girl, who waits at the stairs down to the river. Level 3 (River Walk): by the
-- river she throws it again and it lands on a ferry.
--
-- Everything but Pepper and the ball is greybox (scenery = "greybox"; greyStyle = "town": far rooftops and spires,
-- near facades with window rows instead of the park's trees; see Sc.drawFarGrey).
-- props: kind = solid | oneway | decor; layer = "back", "play", "front"; label = "top" / "below" places the name.
local L = {}
L.name = "DOWNTOWN"
L.number = 2
L.title = "Pepper: Downtown (greybox)"
L.scenery = "greybox"
L.greyStyle = "town"
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
  -- screen 4: the plaza. The pedestal is 40 px up (a held jump), the statue's arm 36 px above it, its hat 32 px
  -- above the arm. The cat sits on the ball on the arm.
  { name = "STATUE",   kind = "decor",  layer = "back", x0 = 1130, x1 = 1158, y0 = 80,  y1 = 144 },
  { name = "PEDESTAL", kind = "solid",  layer = "play", x0 = 1120, x1 = 1168, y0 = 144, y1 = 184 },
  { name = "ARM",      kind = "oneway", layer = "play", x0 = 1158, x1 = 1198, y0 = 108, y1 = 112, label = "below" },
  { name = "",         kind = "oneway", layer = "play", x0 = 1132, x1 = 1156, y0 = 76,  y1 = 80 },      -- the hat
  -- screen 5: the fountain. The basin's water is x 1416-1528 (from y 192); the rims are 16 px up (a hop), the
  -- fountain bowl in the middle 24 px up, 40 px from each rim: a tapped hop from rim to bowl to rim.
  { name = "",         kind = "decor",  layer = "back", x0 = 1416, x1 = 1528, y0 = 184, y1 = 240 },     -- the basin's inside
  { name = "RIM",      kind = "solid",  layer = "play", x0 = 1400, x1 = 1416, y0 = 168, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 1466, x1 = 1478, y0 = 128, y1 = 160 },     -- spout
  { name = "FOUNTAIN", kind = "solid",  layer = "play", x0 = 1456, x1 = 1488, y0 = 160, y1 = 240, label = "top" },
  { name = "RIM",      kind = "solid",  layer = "play", x0 = 1528, x1 = 1544, y0 = 168, y1 = 184, label = "top" },
  -- screen 6: tram street. The kiosk (36 px up) and the shelter roof (one-way, 12 px above the kiosk) are above
  -- the tram (26 px). Then the stairs down to the river (terrain slopes, x 1888-1920).
  { name = "KIOSK",    kind = "solid",  layer = "play", x0 = 1648, x1 = 1688, y0 = 148, y1 = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1732, x1 = 1736, y0 = 140, y1 = 184 },     -- shelter posts
  { name = "",         kind = "decor",  layer = "back", x0 = 1792, x1 = 1796, y0 = 140, y1 = 184 },
  { name = "SHELTER",  kind = "oneway", layer = "play", x0 = 1728, x1 = 1800, y0 = 136, y1 = 140, label = "below" },
  { name = "RIVER",    kind = "decor",  layer = "back", x0 = 1856, x1 = 1884, y0 = 120, y1 = 140 },     -- sign
  { name = "",         kind = "decor",  layer = "back", x0 = 1868, x1 = 1872, y0 = 140, y1 = 184 },
  -- foreground frame: arcade pillars
  { name = "",         kind = "decor",  layer = "front", x0 = 620,  x1 = 632,  y0 = 56, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 1580, x1 = 1592, y0 = 56, y1 = 240 },
}

-- lamp posts: every one is a checkpoint
L.lamps = {
  { x = 296,  y = 184, checkpoint = true },
  { x = 636,  y = 184, checkpoint = true },
  { x = 960,  y = 184, checkpoint = true },
  { x = 1300, y = 184, checkpoint = true },
  { x = 1600, y = 184, checkpoint = true },
}

L.movers = {}

-- the cat sits on the ball on the statue's arm; a bark within 90 px scares it off and the ball drops to the
-- street. If Pepper falls in the fountain with the ball, it goes back there.
L.ball = { x = 1188, y = 108 }
L.cat = { x = 1188, y = 102, range = 90 }
L.ballBack = "THE BALL IS BACK BY THE STATUE"
L.pickupSay = "BRING THE BALL TO THE GIRL!"
-- the girl waits at the top of the stairs down to the river
L.girl = { x = 1860, y = 184 }
L.outro = { "BY THE RIVER SHE THREW IT", "AGAIN. IT LANDED ON A FERRY..." }

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
  { x = 1000, y = 184 }, { x = 1030, y = 184 }, { x = 1132, y = 144 }, { x = 1156, y = 144 },
  { x = 1144, y = 76, super = true }, { x = 1230, y = 184 }, { x = 1250, y = 184 },
  -- 5 the fountain: over the water, on the bowl
  { x = 1340, y = 184 }, { x = 1408, y = 168 }, { x = 1438, y = 160 }, { x = 1472, y = 160 }, { x = 1506, y = 160 },
  { x = 1536, y = 168 }, { x = 1570, y = 184 },
  -- 6 tram street: the kiosk, the shelter roof
  { x = 1660, y = 148 }, { x = 1676, y = 148 }, { x = 1748, y = 136 }, { x = 1772, y = 136 }, { x = 1832, y = 184 },
}

-- the tram zone (the bike-zone code): a tram drives right to left while Pepper is in the zone, and on until it
-- passes endX (before the fountain). w, h: its hit box (80 x 26); rail: it stays on the street's line (y 184)
-- instead of following the ground, so it does not drive down the river stairs.
L.bikes = {
  { zoneX0 = 1610, zoneX1 = 1800, minY = 150, every = 6.0, speed = 110, endX = 1580, kind = "tram", w = 80, h = 26, rail = true },
}

-- prompt banner hints: first match wins; need = "ball" / "noball" / "nearball" / "cat"
L.hints = {
  { x0 = 0,    x1 = 152,  text = "TAP A TO HOP UP THE CRATES" },
  { x0 = 300,  x1 = 368,  text = "DOWN: CRAWL UNDER THE TABLES" },
  { x0 = 640,  x1 = 688,  text = "HOLD A TO JUMP ONTO THE STALL" },
  { x0 = 1040, x1 = 1280, text = "Y: BARK AT THE CAT!", need = "cat" },
  { x0 = 1040, x1 = 1400, text = "X: PICK UP THE BALL", need = "nearball" },
  { x0 = 1280, x1 = 1920, text = "GO BACK: BARK AT THE CAT", need = "cat" },
  { x0 = 1280, x1 = 1920, text = "GO BACK FOR THE BALL", need = "noball" },
  { x0 = 1340, x1 = 1400, text = "TAP A: HOP OVER THE FOUNTAIN" },
  { x0 = 1610, x1 = 1800, text = "TRAM! GET UP HIGH", bike = true },
  { x0 = 1800, x1 = 1920, text = "X: GIVE HER THE BALL", need = "ball" },
  { x0 = 1400, x1 = 1920, text = "BRING THE BALL TO THE GIRL", need = "ball" },
}

L.intro = { "LEVEL 2", "DOWNTOWN", "A CAT IS SITTING ON THE BALL!", "BARK IT AWAY. BRING THE BALL!" }
return L
