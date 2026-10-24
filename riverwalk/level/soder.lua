-- Level 5: Söder Hill (greybox), the chase. Terrain is in soder.map (written by tools/make_soder.py); this file
-- places everything else. Same format as citypark.lua; x, y in level pixels, y grows downwards, "feet" = the y
-- Pepper stands on. The level is 5120 px (16 screens). See docs/soder_beatsheet.md.
--
-- The street runs down the hill: feet y 112 at the top, 16 px lower after every flight of stairs (x 400, 1176,
-- 1936, 2616, 3216, 3896), down to the quay at y 208. Open cellar hatches are gaps in the street.
--
-- The chase (chase.lua, L.scroll): the screen moves on by itself (L.scroll.speeds) and its left edge pushes
-- Pepper along. Pinned against something she didn't jump or crawl under, or fallen into a hatch, she loses a
-- heart and goes back to the last lamp. The ball rolls ahead of her, always on screen, and stops against the quay
-- railing at the bottom, where Mia comes down the stairs.
--
-- Screens (320 px each):
--   1  The top        Mia drops the ball; it rolls away. Run! Tap A over a crate.
--   2  First stairs   hold A: a held jump onto a tall crate stack
--   3  The cafe sign  crawl under a hanging sign; crate steps to a balcony (gold bone, a secret)
--   4  First hatch    a tap hop over an open cellar hatch; stairs; lamp 1
--   5  Parked bikes   hop the bikes, crawl under a low awning
--   6  The terrace    a hatch; the ball knocks a barrel off a stack on a terrace: it rolls down the stairs ahead
--   7  Barrel street  catch up with the barrel and jump it (hold A); crawl under a sign
--   8  Two hatches    hop, land, hop; lamp 2
--   9  Cafe tables    crawl under them or hop over the tops (parasols above: the high road)
--   10 The fruit cart a held jump onto the cart (or hop + scramble); a wide hatch; the second barrel
--   11 The arch       the barrel again; crawl through a low arch
--   12 High street    crate steps up to a long balcony over two hatches (gold bone, a secret), or hop the hatches
--   13 Down to the quay  lamp 3, the last stairs
--   14 The quay       crawl under a sign, hop two bollards
--   15 Crate stack    hop up and over
--   16 The end        the ball stops against the railing; Mia comes down the stairs. Give it to her: GOOD GIRL!
local L = {}
L.name = "SÖDER HILL"
L.number = 5
L.title = "Pepper: Soder Hill"
L.scenery = "greybox"
L.greyStyle = "town"
L.map = "level/soder.map"
L.time = 200
L.start = { x = 24, y = 112 }   -- left of the intro card (at x 60 the card would drop onto the PRESS ANY BUTTON prompt)

-- the chase: from camera x on, the scroll's speed in px/s (Pepper runs at 120, walks at 60); the ball stops at
-- ballStop, against the railing
L.scroll = {
  speeds = { { 0, 50 }, { 560, 62 }, { 1300, 70 }, { 2600, 78 }, { 3900, 70 }, { 4600, 60 } },
  ballStop = 5088,
}

-- the open cellar hatches: x0, x1, the street's y (the gaps themselves are in soder.map)
L.hatches = {
  { 1040, 1072, 128 }, { 1824, 1856, 144 }, { 2320, 2344, 160 }, { 2424, 2456, 160 }, { 3040, 3080, 176 },
  { 3600, 3632, 192 }, { 3720, 3752, 192 },
}

L.props = {
  -- 1 the top (street y 112)
  { name = "CRATE",    kind = "solid",  layer = "play", x0 = 232,  x1 = 264,  y0 = 96,  y1 = 112 },
  -- 2 the first stairs (y 128 from x 416): a tall stack, 32 px: a held jump
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 520,  x1 = 552,  y0 = 96,  y1 = 128, label = "top" },
  -- 3 the cafe sign, hanging from its bracket: 19 px to crawl under it. Crate steps up to a balcony.
  { name = "",         kind = "decor",  layer = "back", x0 = 712,  x1 = 760,  y0 = 62,  y1 = 66 },      -- bracket
  { name = "SIGN",     kind = "solid",  layer = "play", x0 = 720,  x1 = 752,  y0 = 72,  y1 = 109 },
  { name = "",         kind = "solid",  layer = "play", x0 = 860,  x1 = 892,  y0 = 112, y1 = 128 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 892,  x1 = 924,  y0 = 96,  y1 = 128, label = "top" },
  { name = "BALCONY",  kind = "oneway", layer = "play", x0 = 904,  x1 = 968,  y0 = 70,  y1 = 74,  label = "below" },
  -- 5 parked bikes (20 px: a hop), a low awning (19 px to crawl under)
  { name = "BIKES",    kind = "solid",  layer = "play", x0 = 1340, x1 = 1380, y0 = 124, y1 = 144 },
  { name = "",         kind = "decor",  layer = "back", x0 = 1508, x1 = 1512, y0 = 60,  y1 = 86 },      -- its arm
  { name = "AWNING",   kind = "solid",  layer = "play", x0 = 1480, x1 = 1512, y0 = 86,  y1 = 125 },
  -- 6 the terrace with the barrels (24 px up), just before the stairs
  { name = "TERRACE",  kind = "solid",  layer = "play", x0 = 1872, x1 = 1928, y0 = 120, y1 = 144, label = "below" },
  -- 7 a sign to crawl under (street y 160)
  { name = "",         kind = "decor",  layer = "back", x0 = 2172, x1 = 2220, y0 = 94,  y1 = 98 },
  { name = "SIGN",     kind = "solid",  layer = "play", x0 = 2180, x1 = 2212, y0 = 104, y1 = 141 },
  -- 9 cafe tables (street y 176): tops y 150-157, 19 px to crawl under; parasols 42 px above the tops
  { name = "",         kind = "decor",  layer = "back", x0 = 2722, x1 = 2726, y0 = 112, y1 = 150 },     -- poles
  { name = "",         kind = "decor",  layer = "back", x0 = 2802, x1 = 2806, y0 = 112, y1 = 150 },
  { name = "TABLE",    kind = "solid",  layer = "play", x0 = 2700, x1 = 2748, y0 = 150, y1 = 157, label = "below" },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 2692, x1 = 2756, y0 = 108, y1 = 112, label = "below" },
  { name = "TABLE",    kind = "solid",  layer = "play", x0 = 2780, x1 = 2828, y0 = 150, y1 = 157, label = "below" },
  { name = "PARASOL",  kind = "oneway", layer = "play", x0 = 2772, x1 = 2836, y0 = 108, y1 = 112, label = "below" },
  -- 10 the fruit cart (40 px: a held jump, or a hop and a scramble), the second terrace with a barrel
  { name = "CART",     kind = "solid",  layer = "play", x0 = 2940, x1 = 2980, y0 = 136, y1 = 176, label = "top" },
  { name = "TERRACE",  kind = "solid",  layer = "play", x0 = 3120, x1 = 3176, y0 = 152, y1 = 176, label = "below" },
  -- 11 the low arch (street y 192): 19 px to crawl through
  { name = "ARCH",     kind = "solid",  layer = "play", x0 = 3400, x1 = 3432, y0 = 112, y1 = 173 },
  -- 12 crate steps to a long balcony over the two hatches (40 px above the stack: a held jump)
  { name = "",         kind = "solid",  layer = "play", x0 = 3510, x1 = 3542, y0 = 176, y1 = 192 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 3542, x1 = 3574, y0 = 160, y1 = 192, label = "top" },
  { name = "BALCONY",  kind = "oneway", layer = "play", x0 = 3590, x1 = 3770, y0 = 120, y1 = 124, label = "below" },
  -- 12b (r7/curve) a third terrace with barrels, after the balcony's hatches (street y 192, 24 px up)
  { name = "TERRACE",  kind = "solid",  layer = "play", x0 = 3776, x1 = 3832, y0 = 168, y1 = 192, label = "below" },
  -- 13 a crate on the way down to the quay (street y 208)
  { name = "CRATE",    kind = "solid",  layer = "play", x0 = 4000, x1 = 4032, y0 = 192, y1 = 208 },
  -- 14 the quay: a sign to crawl under, two bollards (14 px)
  { name = "",         kind = "decor",  layer = "back", x0 = 4192, x1 = 4240, y0 = 142, y1 = 146 },
  { name = "SIGN",     kind = "solid",  layer = "play", x0 = 4200, x1 = 4232, y0 = 152, y1 = 189 },
  { name = "",         kind = "solid",  layer = "play", x0 = 4300, x1 = 4312, y0 = 194, y1 = 208 },
  { name = "",         kind = "solid",  layer = "play", x0 = 4380, x1 = 4392, y0 = 194, y1 = 208 },
  -- 15 a crate stack: 16 px, then 16 more
  { name = "",         kind = "solid",  layer = "play", x0 = 4560, x1 = 4592, y0 = 192, y1 = 208 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 4592, x1 = 4624, y0 = 176, y1 = 208, label = "top" },
  -- 16 the stairs Mia comes down (decoration) and the quay railing the ball stops against
  { name = "STAIRS",   kind = "decor",  layer = "back", x0 = 4904, x1 = 4984, y0 = 112, y1 = 198, label = "top" },
  { name = "RAILING",  kind = "solid",  layer = "play", x0 = 5096, x1 = 5120, y0 = 172, y1 = 208, label = "top" },
}

-- lamp posts: the three checkpoints
L.lamps = {
  { x = 1240, y = 144, checkpoint = true },
  { x = 2580, y = 160, checkpoint = true },
  { x = 3860, y = 192, checkpoint = true },
}

L.movers = {}
L.bikes = {}

-- the barrels: knocked off their stack when the ball rolls past trigger; they roll down the street at speed px/s
-- (slower than the chase). rest: the barrels that stay on the stack (drawing only).
L.barrels = {
  { x = 1916, y = 120, trigger = 1880, speed = 30, rest = { { 1884, 120 }, { 1898, 120 }, { 1891, 106 } } },
  { x = 3164, y = 152, trigger = 3130, speed = 30, rest = { { 3132, 152 }, { 3146, 152 }, { 3139, 138 } } },
  { x = 3820, y = 168, trigger = 3786, speed = 34, rest = { { 3788, 168 }, { 3802, 168 }, { 3795, 154 } } },   -- (r7/curve)
}

-- the ball starts where Mia dropped it at the top of the hill (it rolls at once); she waits at the bottom
L.ball = { x = 140, y = 112 }
L.girl = { x = 5000, y = 208 }
L.ballBack = "THE BALL IS BY THE FENCE!"
L.pickupSay = "BRING ME THE BALL!"
L.outro = { "NIGHT! A FOX TOOK THE BALL!" }

-- bones: x, feet y (drawn floating 9 px above); super = 1,000 points
L.bones = {
  -- 1-2 the top, the first stairs, the stack
  { x = 160, y = 112 }, { x = 248, y = 96 }, { x = 330, y = 112 }, { x = 470, y = 128 }, { x = 536, y = 96 },
  -- 3 under the sign, the crate steps, the balcony (gold)
  { x = 724, y = 128 }, { x = 748, y = 128 }, { x = 876, y = 112 }, { x = 908, y = 96 }, { x = 936, y = 70, super = true },
  -- 4 over the first hatch
  { x = 1032, y = 112 }, { x = 1056, y = 104 }, { x = 1080, y = 112 },
  -- 5 the bikes, under the awning
  { x = 1360, y = 124 }, { x = 1484, y = 144 }, { x = 1508, y = 144 },
  -- 6 over the hatch, the terrace
  { x = 1840, y = 120 }, { x = 1900, y = 120 },
  -- 7 barrel street, the sign
  { x = 2060, y = 160 }, { x = 2120, y = 160 }, { x = 2196, y = 160 },
  -- 8 over the two hatches
  { x = 2332, y = 136 }, { x = 2440, y = 136 }, { x = 2520, y = 160 },
  -- 9 the tables, a parasol
  { x = 2724, y = 176 }, { x = 2804, y = 176 }, { x = 2724, y = 108 }, { x = 2804, y = 108 },
  -- 10 the cart, over the wide hatch
  { x = 2960, y = 136 }, { x = 3060, y = 150 },
  -- 11 the arch
  { x = 3300, y = 192 }, { x = 3416, y = 192 },
  -- 12 the balcony (gold in the middle) or the hatches
  { x = 3558, y = 160 }, { x = 3620, y = 120 }, { x = 3680, y = 120, super = true }, { x = 3740, y = 120 },
  { x = 3616, y = 176 }, { x = 3736, y = 176 },
  -- 13-15 down to the quay, the sign, the bollards, the stack
  { x = 4016, y = 192 }, { x = 4216, y = 208 }, { x = 4306, y = 194 }, { x = 4386, y = 194 }, { x = 4608, y = 176 },
  -- 16 the end
  { x = 4760, y = 208 }, { x = 4840, y = 208 },
}

-- secrets: reaching one (Pepper's feet in its box) counts it; the tally shows how many were found
L.secrets = {
  { name = "CAFE BALCONY", x0 = 904,  x1 = 968,  y0 = 60,  y1 = 70 },
  { name = "HIGH STREET",  x0 = 3650, x1 = 3710, y0 = 110, y1 = 120 },
}

-- hints (St:hint, drawn by talk.lua): first match wins
L.hints = {
  { x0 = 4700, x1 = 5120, btn = "x",    text = "PICK UP",           need = "nearball" },
  { x0 = 4900, x1 = 5120, btn = "x",    text = "GIVE",              need = "ball" },
  { x0 = 440,  x1 = 520,  btn = "a",    text = "HOLD: BIG JUMP" },
  { x0 = 640,  x1 = 720,  btn = "down", text = "CRAWL" },
  { x0 = 960,  x1 = 1040, btn = "a",    text = "TAP: HOP" },
  { x0 = 0,    x1 = 400,  text = "MY BALL! CATCH IT, PEPPER!" },
  { x0 = 1880, x1 = 2060, text = "LOOK OUT! A BARREL!" },
  { x0 = 4700, x1 = 5120, text = "BRING ME THE BALL!", need = "ball" },
}

L.intro = { "LEVEL 5", "SÖDER HILL", "CATCH THE ROLLING BALL!" }
return L
