-- The height engine's test level (greybox, not in the play order): love riverwalk --level lab_tall.
-- 3 screens wide x 3 screens tall (960 x 720 px; lab_tall.map has 90 rows, made by tools/make_lab_tall.py).
-- A tall level is any map with more than 30 rows: the world is rows x 8 px high and the camera follows Pepper up
-- and down (vcam.lua). Coordinates are world pixels, y grows downwards, "feet" = the y Pepper stands on.
--
-- The route, bottom to top:
--   ground floor (y 664)  the start and a lamp; a pit (x 224-256, open to the bottom of the world: a heart, back
--                         to the lamp); tap A to hop it
--   stairs                up 96 px to the landing L1 (y 568); on it three 4 px steps up and down (walked onto)
--   scaffold              one-way planks, 32 px apart, left and right of a tall gap (x 560-720), up to y 408
--                         (hold A, jump up and across; Down + A drops through a plank)
--   the beam              y 376, x 720-816; walk off its end: a tall drop (128 px) onto F2 (y 504), no harm
--   the goods lift        x 896-944, from F2 (y 504) up to the roof (y 184) and back, 56 px/s, 1.5 s at each end.
--                         It has a motor: the winch house above the top stop, where an operator runs it.
--   the roof (y 184)      Mia, and the ball nearby: pick it up (X), give it to her (X)
local L = {}
L.name = "LAB: TALL"
L.number = 0
L.title = "Pepper: lab, a tall level"
L.scenery = "greybox"
L.map = "level/lab_tall.map"
L.time = 300
L.start = { x = 40, y = 664 }

L.props = {
  -- L1: three 4 px steps up and three down (solid, each one stepped onto without a jump)
  { name = "",       kind = "solid",  layer = "play", x0 = 432, x1 = 456, y0 = 564, y1 = 568 },
  { name = "",       kind = "solid",  layer = "play", x0 = 456, x1 = 480, y0 = 560, y1 = 568 },
  { name = "STEPS",  kind = "solid",  layer = "play", x0 = 480, x1 = 504, y0 = 556, y1 = 568 },
  { name = "",       kind = "solid",  layer = "play", x0 = 504, x1 = 528, y0 = 560, y1 = 568 },
  { name = "",       kind = "solid",  layer = "play", x0 = 528, x1 = 552, y0 = 564, y1 = 568 },
  -- the scaffold: one-way planks, left (x 560-624) and right (x 656-720), 32 px apart
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 560, x1 = 624, y0 = 632, y1 = 638 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 656, x1 = 720, y0 = 600, y1 = 606 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 560, x1 = 624, y0 = 568, y1 = 574 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 656, x1 = 720, y0 = 536, y1 = 542 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 560, x1 = 624, y0 = 504, y1 = 510 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 656, x1 = 720, y0 = 472, y1 = 478 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 560, x1 = 624, y0 = 440, y1 = 446 },
  { name = "PLANK",  kind = "oneway", layer = "play", x0 = 656, x1 = 720, y0 = 408, y1 = 414 },
  { name = "BEAM",   kind = "oneway", layer = "play", x0 = 720, x1 = 816, y0 = 376, y1 = 384 },
  -- scaffold poles behind the planks (decoration)
  { name = "",       kind = "decor",  layer = "back", x0 = 564, x1 = 568, y0 = 432, y1 = 664 },
  { name = "",       kind = "decor",  layer = "back", x0 = 616, x1 = 620, y0 = 432, y1 = 664 },
  { name = "",       kind = "decor",  layer = "back", x0 = 660, x1 = 664, y0 = 400, y1 = 664 },
  { name = "",       kind = "decor",  layer = "back", x0 = 712, x1 = 716, y0 = 376, y1 = 664 },
  -- the roof: a parapet at its open end (a hop), so a fetch does not end in a fall back to L1
  { name = "",       kind = "solid",  layer = "play", x0 = 560, x1 = 568, y0 = 172, y1 = 184 },
}

L.lamps = {
  { x = 100, y = 664, checkpoint = true },     -- the ground floor
  { x = 840, y = 504, checkpoint = true },     -- F2, by the lift
  { x = 860, y = 184, checkpoint = true },     -- the roof
}

-- the goods lift (lift.lua): a mover on both axes; here only y changes
L.movers = {
  { name = "LIFT", x0 = 896, x1 = 944, y0 = 504, y1 = 512, from = 896, to = 896, fromY = 504, toY = 184,
    speed = 56, pause = 1.5, winch = { x = 920, y = 96 } },
}

L.ball = { x = 720, y = 184 }
L.ballBack = "THE BALL IS BACK ON THE ROOF"
L.girl = { x = 600, y = 184 }

L.bones = {
  { x = 150, y = 664 }, { x = 240, y = 648 }, { x = 330, y = 622 }, { x = 492, y = 556 },
  { x = 600, y = 568 }, { x = 690, y = 536 }, { x = 590, y = 504 }, { x = 690, y = 472 }, { x = 590, y = 440 },
  { x = 780, y = 376 }, { x = 860, y = 504 }, { x = 920, y = 344, super = true }, { x = 780, y = 184 },
}

L.bikes = {}
L.secrets = {}
L.hints = {
  { x0 = 0,   x1 = 960, btn = "x",    text = "PICK UP",          need = "nearball" },
  { x0 = 560, x1 = 700, btn = "x",    text = "GIVE",             need = "ball", maxY = 200 },
  { x0 = 170, x1 = 224, btn = "a",    text = "TAP: HOP",         maxY = 670 },
  { x0 = 560, x1 = 720, btn = "a",    text = "HOLD: BIG JUMP",   maxY = 640 },
  { x0 = 856, x1 = 896, text = "RIDE THE LIFT UP!", minY = 480, maxY = 504 },   -- (minY / maxY: on F2 only)
  { x0 = 0,   x1 = 960, text = "BRING ME THE BALL!", need = "ball" },
}

L.intro = { "LAB", "A TALL LEVEL", "CLIMB UP TO MIA!", "UP: LOOK UP  DOWN: LOOK DOWN" }
return L
