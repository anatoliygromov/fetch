-- Level 3: River Walk (greybox). Terrain is in riverwalk.map; this file places everything else.
-- x, y in level pixels; y grows downwards; "feet" = the y Pepper stands on.
-- Upper promenade feet y = 184, lower quay y = 216, river surface y = 224.
--
-- Screens (320 px each):
--   1 Home        hop onto the bench, over the bin
--   2 Promenade   bikes ride through: get up onto the railing or a planter
--   3 Steps       down to the quay, ride the pontoon over the river
--   4 Boat        climb the cabin (scramble) and pick up the ball
--   5 Bridge      crawl under the bridge pier with the ball, steps back up
--   6 The girl    give her the ball: GOOD GIRL!
--
-- props: kind = solid | oneway | decor; layer = "back" (behind Pepper), "play", "front" (in front of Pepper)
-- art = an image in art/scene, drawn bottom-left on the box (x0, y1); without it the prop is a greybox
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
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 97,   x1 = 146,  y0 = 173, y1 = 184, art = "bench" },
  { name = "POT",      kind = "decor",  layer = "play", x0 = 168,  x1 = 185,  y0 = 157, y1 = 184, art = "pot" },
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 201,  x1 = 218,  y0 = 158, y1 = 184, art = "bin" },
  { name = "RAILING",  kind = "oneway", layer = "back", x0 = 256,  x1 = 680,  y0 = 149, y1 = 153, railing = true },
  -- 2 promenade
  { name = "PLANTER",  kind = "solid",  layer = "play", x0 = 352,  x1 = 388,  y0 = 154, y1 = 184 },
  { name = "PLANTER",  kind = "solid",  layer = "play", x0 = 560,  x1 = 596,  y0 = 154, y1 = 184 },
  -- 3 steps and quay
  -- 4 boat
  { name = "BOAT",     kind = "solid",  layer = "play", x0 = 968,  x1 = 1144, y0 = 206, y1 = 236 },
  { name = "CABIN",    kind = "solid",  layer = "play", x0 = 1024, x1 = 1096, y0 = 150, y1 = 206 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1112, x1 = 1115, y0 = 96,  y1 = 206, sub = true },
  -- 6 the girl
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 1641, x1 = 1690, y0 = 173, y1 = 184, art = "bench" },
  { name = "BIKES",    kind = "decor",  layer = "back", x0 = 1716, x1 = 1772, y0 = 152, y1 = 184 },
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 1791, x1 = 1808, y0 = 158, y1 = 184, art = "bin" },
  -- foreground frame
  { name = "",         kind = "decor",  layer = "front", x0 = 930,  x1 = 940,  y0 = 60, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 1470, x1 = 1480, y0 = 60, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 1730, x1 = 1880, y0 = 18, y1 = 66 },
}

-- lamp posts; the ones marked checkpoint save Pepper's place when she passes
L.lamps = {
  { x = 240,  y = 184, checkpoint = true },
  { x = 470,  y = 184 },
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
  { x = 108, y = 173 }, { x = 122, y = 173 }, { x = 136, y = 173 }, { x = 210, y = 158 },
  { x = 290, y = 149 }, { x = 330, y = 149 }, { x = 410, y = 149 }, { x = 450, y = 149 }, { x = 490, y = 149 },
  { x = 530, y = 149 }, { x = 610, y = 149 }, { x = 370, y = 154 }, { x = 578, y = 154 },
  { x = 420, y = 184 }, { x = 520, y = 184 },
  { x = 698, y = 194 }, { x = 740, y = 216 }, { x = 836, y = 192 }, { x = 872, y = 180 }, { x = 908, y = 192 },
  { x = 992, y = 206 }, { x = 1010, y = 206 }, { x = 1086, y = 150, super = true },
  { x = 1240, y = 216 }, { x = 1330, y = 216 }, { x = 1372, y = 216 }, { x = 1414, y = 216 }, { x = 1490, y = 216 },
  { x = 1606, y = 184 }, { x = 1652, y = 173 }, { x = 1666, y = 173 }, { x = 1680, y = 173 }, { x = 1800, y = 158 },
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
