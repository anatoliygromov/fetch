-- Level 3: River Walk (greybox). Terrain is in riverwalk.map; this file places everything else.
-- x, y in level pixels; y grows downwards; "feet" = the y Pepper stands on.
-- Upper promenade feet y = 184, lower quay y = 216, river surface y = 224.
--
-- Screens (320 px each):
--   1 Home        crawl under the bench or jump onto its seat, then up onto the bin
--   2 Promenade   bikes ride through: get up onto the flower boxes and the planter
--   3 Steps       down to the quay, ride the pontoon over the river
--   4 Boat        climb the cabin (scramble) and pick up the ball
--   5 Bridge      crawl under the bridge pier with the ball, steps back up
--   6 The girl    give her the ball: GOOD GIRL!
--
-- props: kind = solid | oneway | decor; layer = "back" (behind Pepper), "play", "front" (in front of Pepper)
-- art = an image in art/scene, drawn bottom-left on the box (x0, y1), or on (ax, ay) when the art is bigger than
-- the box; without it the prop is a greybox. The bench's box is only its seat (y 156-165): Pepper crawls under
-- it (19 px gap) or jumps onto it; its legs and backrest are drawn, not solid.
-- Obstacles (bench, bin) stand on Pepper's walking line (y 184), so they read as things in her way.
-- Decoration (the pot, the lamp posts) stands on the back edge of the pavement by the water, 10 px behind her
-- line (the pot's box ends at y 174), so it reads as scenery she passes.
local L = {}
L.name = "RIVER WALK"
L.number = 3
L.map = "level/riverwalk.map"
L.time = 300
L.start = { x = 52, y = 184 }

L.props = {
  -- 1 home
  { name = "HOME",     kind = "decor",  layer = "back", x0 = 0,    x1 = 77,   y0 = 37,  y1 = 172, art = "building" },
  { name = "TREE",     kind = "decor",  layer = "back", x0 = 0,    x1 = 114,  y0 = 45,  y1 = 172, art = "tree" },
  { name = "POT",      kind = "decor",  layer = "play", x0 = 214,  x1 = 231,  y0 = 147, y1 = 174, art = "pot" },
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 97,   x1 = 204,  y0 = 156, y1 = 165, art = "bench", ax = 90, ay = 184 },
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 255,  x1 = 293,  y0 = 128, y1 = 184, art = "bin", ax = 252, ay = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 80,   x1 = 688,  y0 = 144, y1 = 174, railing = true },   -- decorative railing by the water
  -- 2 promenade
  { name = "FLOWERS",  kind = "solid",  layer = "play", x0 = 313,  x1 = 415,  y0 = 152, y1 = 184, art = "flowerbox", ax = 312, ay = 184 },
  { name = "PLANTER",  kind = "solid",  layer = "play", x0 = 434,  x1 = 478,  y0 = 154, y1 = 184, art = "planter_sq" },
  { name = "FLOWERS",  kind = "solid",  layer = "play", x0 = 519,  x1 = 619,  y0 = 157, y1 = 184, art = "flowerbox_low", ax = 518, ay = 184 },
  -- 3 steps and quay
  -- 4 boat
  { name = "BOAT",     kind = "solid",  layer = "play", x0 = 968,  x1 = 1144, y0 = 206, y1 = 236 },
  { name = "CABIN",    kind = "solid",  layer = "play", x0 = 1024, x1 = 1096, y0 = 150, y1 = 206 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1112, x1 = 1115, y0 = 96,  y1 = 206, sub = true },
  -- 6 the girl
  { name = "GABLE",    kind = "decor",  layer = "back", x0 = 1706, x1 = 1776, y0 = -3,  y1 = 172, art = "gable" },
  { name = "CAFE",     kind = "decor",  layer = "back", x0 = 1770, x1 = 1920, y0 = -33, y1 = 172, art = "cafe" },
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 1627, x1 = 1734, y0 = 156, y1 = 165, art = "bench", ax = 1620, ay = 184 },
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 1759, x1 = 1797, y0 = 128, y1 = 184, art = "bin", ax = 1756, ay = 184 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1608, x1 = 1706, y0 = 144, y1 = 174, railing = true },   -- decorative railing by the water
  -- foreground frame
  { name = "",         kind = "decor",  layer = "front", x0 = 930,  x1 = 940,  y0 = 60, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 1470, x1 = 1480, y0 = 60, y1 = 240 },
}

-- lamp posts; the ones marked checkpoint save Pepper's place when she passes
L.lamps = {
  { x = 240,  y = 184, checkpoint = true },
  { x = 498,  y = 184 },
  { x = 652,  y = 184, checkpoint = true },
  { x = 1200, y = 216, checkpoint = true },
  { x = 1580, y = 184, checkpoint = true },
}

-- the pontoon drifts to and fro over the river
L.movers = {
  { name = "PONTOON", x0 = 800, x1 = 848, y0 = 214, y1 = 220, from = 800, to = 904, speed = 30 },
}

L.ball = { x = 1062, y = 150 }
L.girl = { x = 1866, y = 184 }

-- bones: x, feet y (drawn floating 9 px above); super = 1,000 points
L.bones = {
  { x = 124, y = 156 }, { x = 150, y = 156 }, { x = 176, y = 156 }, { x = 274, y = 128 },
  { x = 336, y = 152 }, { x = 364, y = 152 }, { x = 392, y = 152 }, { x = 546, y = 157 }, { x = 570, y = 157 },
  { x = 594, y = 157 }, { x = 630, y = 184 }, { x = 456, y = 154 }, { x = 230, y = 184 },
  { x = 424, y = 184 }, { x = 498, y = 184 },
  { x = 698, y = 194 }, { x = 740, y = 216 }, { x = 836, y = 192 }, { x = 872, y = 180 }, { x = 908, y = 192 },
  { x = 992, y = 206 }, { x = 1010, y = 206 }, { x = 1086, y = 150, super = true },
  { x = 1240, y = 216 }, { x = 1330, y = 216 }, { x = 1372, y = 216 }, { x = 1414, y = 216 }, { x = 1490, y = 216 },
  { x = 1590, y = 184 }, { x = 1654, y = 156 }, { x = 1680, y = 156 }, { x = 1706, y = 156 }, { x = 1778, y = 128 },
}

-- a cyclist rides right to left along the promenade while Pepper is in this zone
L.bikes = { zoneX0 = 280, zoneX1 = 590, minY = 150, every = 6.5, speed = 115, endX = 180 }

-- prompt banner hints: first match wins; need = "ball" / "noball" / "nearball"
L.hints = {
  { x0 = 0,    x1 = 92,   text = "HOLD A TO JUMP HIGHER" },
  { x0 = 290,  x1 = 600,  text = "BIKES! GET UP HIGH", bike = true },
  { x0 = 690,  x1 = 800,  text = "RIDE THE PONTOON" },
  { x0 = 940,  x1 = 1150, text = "X: PICK UP THE BALL", need = "nearball" },
  { x0 = 940,  x1 = 1150, text = "JUMP UP ON THE CABIN", need = "noball" },
  { x0 = 1236, x1 = 1304, text = "DOWN: CRAWL UNDER THE BRIDGE" },
  { x0 = 1780, x1 = 1920, text = "X: GIVE HER THE BALL", need = "ball" },
  { x0 = 1700, x1 = 1920, text = "FIND THE BALL ON THE BOAT", need = "noball" },
}

L.intro = { "LEVEL 3", "RIVER WALK", "THE BALL LANDED ON A BOAT.", "FETCH IT FOR THE GIRL!" }
return L
