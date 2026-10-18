-- Level 1: City Park (greybox). Terrain is in citypark.map; this file places everything else.
-- Same format as riverwalk.lua. x, y in level pixels; y grows downwards; "feet" = the y Pepper stands on.
-- The path (feet) is y 184. The pond's water starts at y 208. The level is 2880 px (9 screens). See
-- docs/citypark_beatsheet.md (the first 6 screens) and docs/progression.md.
--
-- Screens (320 px each). Manner: sneak and bark (docs/progression.md). New here: geese (L.critters, critters.lua).
--   1  The gate      run, tap A to hop onto the log; the leaf pile hides bones
--   2  Benches       hold A to jump onto the bench (or crawl under it); crawl through the hedge gap;
--                    a running jump from the bench seat reaches the hedge top (gold bone)
--   3  The pond      hop onto the stepping stones, ride the duck boat, hop up the far bank; or the high route:
--                    from the hedge top over the three willows' branches (gold bone), down on the far bank
--   4  Goose lawn    the first goose: it hisses, then charges. Bark at it (Y) and it flies off, or jump over it
--   5  Leaf cart     climb the bin (jump + scramble); the leaf cart zone: get up on the picnic table
--   6  The big oak   hop over the hollow log or crawl through it (a gold bone hidden inside); climb the branches
--                    for a gold bone
--   7  The creek     three small stepping stones over deep water: stop on each, then hop. A goose on the far bank
--   8  Rose walk     the second leaf cart run, faster carts: wait on the bench, then the picnic table
--   9  Playground    up the slide tower, down the slide, the climbing frame, give the girl her ball
--
-- Story (level 1 of 3): a magpie has stolen the girl's ball. It sits on a perch and flies on to the next one when
-- Pepper comes near: from far off if she runs, only close up if she walks (hold B). Sneak up and bark (Y): it
-- drops the ball. Pick it up (X) and bring it to the girl, who waits by the swings (X again: GOOD GIRL!).
-- If Pepper never gets it to drop the ball, the magpie ends up on the climbing frame, its last perch.
--
-- scenery = "greybox" keeps the greybox rules (no road, no traffic); L.art = "park" draws the scenery art over the
-- boxes (Sc.drawPropArt, Sc.drawFarArt; tools/make_town_art.py). Without L.art the level is drawn as boxes again.
-- props: kind = solid | oneway | decor; layer = "back", "play", "front"; over = true draws a play prop over
-- the bones (the leaf piles); leaves = true: it flattens when Pepper runs through it.
-- Secrets (L.secrets, counted on the tally): the willows (the high route over the pond), inside the hollow log,
-- the oak's top branch.
local L = {}
L.name = "CITY PARK"
L.number = 1
L.title = "Pepper: City Park"
L.scenery = "greybox"
L.art = "park"                -- scenery art (tools/make_town_art.py; drawn by Sc.drawPropArt from the boxes)
L.map = "level/citypark.map"
L.time = 300
L.start = { x = 60, y = 184 }

L.props = {
  -- screen 1: the gate
  { name = "GATE",     kind = "decor",  layer = "back", x0 = 0,    x1 = 32,   y0 = 112, y1 = 184 },
  { name = "LEAVES",   kind = "decor",  layer = "play", x0 = 92,   x1 = 140,  y0 = 172, y1 = 184, over = true, leaves = true },
  { name = "LOG",      kind = "solid",  layer = "play", x0 = 176,  x1 = 216,  y0 = 168, y1 = 184 },
  -- screen 2: bench and hedge. The bench's box is only its seat (y 156-165): 19 px to crawl under it.
  -- The hedge's box ends at y 165: 19 px to crawl under it, its top (72 px up) is out of reach from the path.
  { name = "",         kind = "decor",  layer = "back", x0 = 352,  x1 = 448,  y0 = 138, y1 = 152 },     -- backrest
  { name = "",         kind = "decor",  layer = "back", x0 = 356,  x1 = 362,  y0 = 165, y1 = 184 },     -- legs
  { name = "",         kind = "decor",  layer = "back", x0 = 438,  x1 = 444,  y0 = 165, y1 = 184 },
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 352,  x1 = 448,  y0 = 156, y1 = 165 },
  { name = "HEDGE",    kind = "solid",  layer = "play", x0 = 528,  x1 = 592,  y0 = 112, y1 = 165 },
  -- screen 3: the pond (water x 704-944). Two stepping stones (tops y 188, a 4 px step down from the bank, 32 px
  -- apart), then the duck boat (L.movers, deck y 202), a rope ferry: the park keeper's winch on the far bank
  -- pulls it along its rope
  { name = "STONE",    kind = "solid",  layer = "play", x0 = 736,  x1 = 760,  y0 = 188, y1 = 240, label = "top" },
  { name = "STONE",    kind = "solid",  layer = "play", x0 = 792,  x1 = 816,  y0 = 188, y1 = 240, label = "top" },
  { name = "WINCH",    kind = "decor",  layer = "back", x0 = 946,  x1 = 966,  y0 = 160, y1 = 174 },
  -- the high route over the pond: three willows on the far side of the water lean their branches over it
  -- (one-way, tops y 120, 112, 120, 48 px apart). From the hedge top a running held jump reaches the first;
  -- from the last Pepper drops onto the far bank. Trunks and crowns are decoration (base y 174).
  { name = "",         kind = "decor",  layer = "back", x0 = 664,  x1 = 736,  y0 = 96,  y1 = 120 },     -- crowns
  { name = "WILLOWS",  kind = "decor",  layer = "back", x0 = 768,  x1 = 840,  y0 = 88,  y1 = 112, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 872,  x1 = 944,  y0 = 96,  y1 = 120 },
  { name = "",         kind = "decor",  layer = "back", x0 = 696,  x1 = 704,  y0 = 120, y1 = 174 },     -- trunks
  { name = "",         kind = "decor",  layer = "back", x0 = 800,  x1 = 808,  y0 = 112, y1 = 174 },
  { name = "",         kind = "decor",  layer = "back", x0 = 904,  x1 = 912,  y0 = 120, y1 = 174 },
  { name = "",         kind = "oneway", layer = "play", x0 = 672,  x1 = 728,  y0 = 120, y1 = 125 },     -- branches
  { name = "",         kind = "oneway", layer = "play", x0 = 776,  x1 = 832,  y0 = 112, y1 = 117 },
  { name = "",         kind = "oneway", layer = "play", x0 = 880,  x1 = 936,  y0 = 120, y1 = 125 },
  -- screen 4: the goose lawn (984-1304). A leaf pile with bones, then a goose patrols the path: bark to shoo it
  -- (or time a held jump over it); a log to hop at the end (the magpie may perch on it)
  { name = "LEAVES",   kind = "decor",  layer = "play", x0 = 1008, x1 = 1052, y0 = 172, y1 = 184, over = true, leaves = true },
  { name = "LOG",      kind = "solid",  layer = "play", x0 = 1248, x1 = 1288, y0 = 168, y1 = 184 },
  -- screen 5: the bin, then the leaf cart zone with the picnic table
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 1328, x1 = 1363, y0 = 128, y1 = 184 },
  { name = "PICNIC TABLE", kind = "solid", layer = "play", x0 = 1416, x1 = 1488, y0 = 156, y1 = 184 },
  { name = "LEAVES",   kind = "decor",  layer = "play", x0 = 1516, x1 = 1560, y0 = 172, y1 = 184, over = true, leaves = true },
  -- screen 6: the hollow log (drawn in code, L.pieces): its bark shell is a solid top (y 158-165, 26 px up), 19 px
  -- to crawl through under it; a gold bone is hidden inside. Then the big oak. Trunk and crown are decoration;
  -- the branches are one-way ledges.
  { name = "HOLLOW LOG", kind = "solid", layer = "play", x0 = 1564, x1 = 1606, y0 = 158, y1 = 165, hidden = true },
  { name = "",         kind = "decor",  layer = "back", x0 = 1648, x1 = 1832, y0 = 44,  y1 = 92 },      -- crown
  { name = "OAK",      kind = "decor",  layer = "back", x0 = 1724, x1 = 1748, y0 = 92,  y1 = 184 },     -- trunk
  { name = "",         kind = "oneway", layer = "play", x0 = 1656, x1 = 1720, y0 = 104, y1 = 110 },     -- the left bough
  { name = "BRANCH",   kind = "oneway", layer = "play", x0 = 1752, x1 = 1808, y0 = 156, y1 = 162, label = "below" },
  { name = "",         kind = "oneway", layer = "play", x0 = 1768, x1 = 1832, y0 = 128, y1 = 134 },
  { name = "",         kind = "oneway", layer = "play", x0 = 1744, x1 = 1792, y0 = 100, y1 = 106 },
  -- screen 7: the creek (1920-2296). Water x 2000-2296 (from y 208); three stepping stones (tops y 188, 24 wide)
  -- with 56 px of water before, between and after them. Running across fails: off a stone at full speed she drops
  -- below the next one, past her 12 px scramble reach. A held jump from standing carries her 75 px, one stone
  -- (they are 80 px apart). So: stop, then hop. On the far bank a goose: it hisses as she lands, a bark sends it off.
  { name = "STONE",    kind = "solid",  layer = "play", x0 = 2056, x1 = 2080, y0 = 188, y1 = 240, label = "top" },
  { name = "STONE",    kind = "solid",  layer = "play", x0 = 2136, x1 = 2160, y0 = 188, y1 = 240, label = "top" },
  { name = "STONE",    kind = "solid",  layer = "play", x0 = 2216, x1 = 2240, y0 = 188, y1 = 240, label = "top" },
  -- screen 8: the rose walk (2296-2560): a second leaf cart run. Perches: the bench seat, then the picnic table
  { name = "",         kind = "decor",  layer = "back", x0 = 2380, x1 = 2476, y0 = 138, y1 = 152 },     -- backrest
  { name = "",         kind = "decor",  layer = "back", x0 = 2384, x1 = 2390, y0 = 165, y1 = 184 },     -- legs
  { name = "",         kind = "decor",  layer = "back", x0 = 2466, x1 = 2472, y0 = 165, y1 = 184 },
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 2380, x1 = 2476, y0 = 156, y1 = 165 },
  { name = "PICNIC TABLE", kind = "solid", layer = "play", x0 = 2500, x1 = 2572, y0 = 156, y1 = 184 },
  -- screen 9: the playground. The slide is terrain: the tower (x 2624-2656, top y 152) and the slide (slope cells,
  -- x 2656-2688). A hidden box fills the tower's left half: near slopes terrain steps are not walls (they are
  -- stairs), so without it a knock-back off the top of the slide could carry Pepper into the tower.
  { name = "SLIDE",    kind = "decor",  layer = "back", x0 = 2624, x1 = 2656, y0 = 124, y1 = 152, label = "top" },  -- handrail
  { name = "",         kind = "solid",  layer = "play", x0 = 2624, x1 = 2640, y0 = 152, y1 = 184, hidden = true },
  { name = "",         kind = "decor",  layer = "back", x0 = 2712, x1 = 2716, y0 = 120, y1 = 184 },     -- frame posts
  { name = "",         kind = "decor",  layer = "back", x0 = 2772, x1 = 2776, y0 = 120, y1 = 184 },
  { name = "FRAME",    kind = "oneway", layer = "play", x0 = 2712, x1 = 2760, y0 = 160, y1 = 164, label = "below" },
  { name = "",         kind = "oneway", layer = "play", x0 = 2728, x1 = 2776, y0 = 136, y1 = 140 },
  { name = "SWINGS",   kind = "decor",  layer = "back", x0 = 2804, x1 = 2876, y0 = 104, y1 = 184 },
  -- foreground frame
  { name = "",         kind = "decor",  layer = "front", x0 = 620,  x1 = 632,  y0 = 221, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 1900, x1 = 1912, y0 = 221, y1 = 240 },
}

-- lamp posts: every one is a checkpoint
L.lamps = {
  { x = 296,  y = 184, checkpoint = true },
  { x = 656,  y = 184, checkpoint = true },
  { x = 976,  y = 184, checkpoint = true },
  { x = 1306, y = 184, checkpoint = true },
  { x = 1624, y = 184, checkpoint = true },
  { x = 1936, y = 184, checkpoint = true },
  { x = 2358, y = 184, checkpoint = true },
  { x = 2592, y = 184, checkpoint = true },
}

-- things drawn in code (setpieces.lua); their collision is the hidden prop with the same box above
L.pieces = {
  { kind = "hollowlog", x0 = 1564, x1 = 1606, y0 = 158, y1 = 165 },
}

-- the duck boat: a rope ferry between the second stone (816) and the far bank (944). It waits by the far bank;
-- when Pepper comes to the pond (call: x 600-830) the keeper winches it over to the stone to wait for her, and
-- when she stands on it, it takes her across.
L.movers = {
  { name = "DUCK BOAT", x0 = 824, x1 = 872, y0 = 202, y1 = 208, from = 824, to = 888, speed = 24,
    call = { 600, 830 }, callSpeed = 48, rope = { 816, 944 } },
}

-- the magpie and the ball: perches in order (x, feet y). It starts on the path just past the log, so the first
-- try comes straight away: walk up to the log and bark from there (bark range 95 px, it flees from a running
-- Pepper at 110 px, from a walking one only at 40 px). On the first perch it is calmer: it flees a running Pepper
-- only at 80 px, inside bark range, so a kid who runs straight at it (the log stops her at 81 px) can still bark.
-- Every perch drops the ball where a small child can get it: the path, the bench seat, the bin top, the slide
-- tower, the climbing frame (the oak's high branch, out of reach for many, is no longer a perch).
L.ball = { x = 240, y = 184 }
L.magpie = { flee = 110, fleeWalk = 40, bark = 95, dropSay = "IT DROPPED THE BALL!",
  perches = {
    { x = 240,  y = 184, flee = 80 },   -- the path past the log
    { x = 400,  y = 138 },     -- the bench's backrest (the ball lands on the seat)
    { x = 656,  y = 120 },     -- the lamp post by the hedge
    { x = 1268, y = 168 },     -- the log on the goose lawn (the ball stays on the log)
    { x = 1345, y = 128 },     -- the bin (the ball stays on top: climb it)
    { x = 1624, y = 100 },     -- the lamp post before the oak (the ball drops to the path)
    { x = 2428, y = 138 },     -- the rose walk bench's backrest (the ball lands on the seat)
    { x = 2640, y = 124 },     -- the slide tower's rail (the ball lands on the tower)
    { x = 2752, y = 136 },     -- the climbing frame's top bar: its last perch
  } }
L.ballBack = "THE BALL IS BACK BY THE LAMP"
-- the girl waits by the swings at the far end of the park
L.girl = { x = 2840, y = 184 }
L.outro = { "OFF TO TOWN! BUT THE BALL", "ROLLED AWAY ACROSS THE PLAZA..." }

-- bones: x, feet y (drawn floating 9 px above); super = 1,000 points
L.bones = {
  -- 1 the gate: three in the leaf pile, two on the log
  { x = 102, y = 184 }, { x = 116, y = 184 }, { x = 130, y = 184 }, { x = 188, y = 168 }, { x = 204, y = 168 },
  { x = 248, y = 184 }, { x = 270, y = 184 },
  -- 2 bench and hedge
  { x = 376, y = 156 }, { x = 400, y = 156 }, { x = 424, y = 156 }, { x = 488, y = 184 },
  { x = 540, y = 184 }, { x = 560, y = 184 }, { x = 580, y = 184 }, { x = 560, y = 112, super = true },
  -- 3 the pond
  { x = 684, y = 184 }, { x = 748, y = 188 }, { x = 776, y = 180 }, { x = 804, y = 188 },
  { x = 866, y = 202 }, { x = 906, y = 202 }, { x = 952, y = 184 },
  -- 3 the willows (the high route): one on each branch, gold on the middle one
  { x = 700, y = 120 }, { x = 804, y = 112, super = true }, { x = 908, y = 120 },
  -- 4 the goose lawn: in the leaf pile, along the path, on the log
  { x = 1020, y = 184 }, { x = 1032, y = 184 }, { x = 1044, y = 184 }, { x = 1090, y = 184 }, { x = 1160, y = 160 },
  { x = 1262, y = 168 }, { x = 1276, y = 168 },
  -- 5 bin, picnic table, leaves
  { x = 1310, y = 184 }, { x = 1345, y = 128 }, { x = 1434, y = 156 }, { x = 1452, y = 156 }, { x = 1470, y = 156 },
  { x = 1530, y = 184 }, { x = 1546, y = 184 },
  -- 5 the hollow log (gold, hidden inside), the oak
  { x = 1585, y = 184, super = true },
  { x = 1648, y = 184 }, { x = 1780, y = 156 }, { x = 1810, y = 128 }, { x = 1768, y = 100, super = true },
  { x = 1864, y = 184 }, { x = 1888, y = 184 },
  -- 7 the creek: over the stones (hop to get the ones in the air)
  { x = 1968, y = 184 }, { x = 2028, y = 160 }, { x = 2068, y = 188 }, { x = 2108, y = 160 }, { x = 2148, y = 188 },
  { x = 2188, y = 160 }, { x = 2228, y = 188 }, { x = 2268, y = 160 }, { x = 2330, y = 184 },
  -- 8 the rose walk: the bench seat, the picnic table
  { x = 2404, y = 156 }, { x = 2428, y = 156 }, { x = 2452, y = 156 }, { x = 2490, y = 184 }, { x = 2520, y = 156 },
  { x = 2536, y = 156 }, { x = 2552, y = 156 }, { x = 2596, y = 184 },
  -- 9 playground
  { x = 2640, y = 152 }, { x = 2672, y = 168 }, { x = 2736, y = 160 }, { x = 2752, y = 136 }, { x = 2792, y = 184 },
}

-- the leaf cart zone (the bike-zone code): the park keeper's cart drives right to left while Pepper is in the
-- zone, and on until it passes endX. Same 48 x 26 hit box as the bikes. start = "enter": the first run starts
-- when Pepper walks into the zone (a honk 1 s before it is on screen), then one every 6 s while she is in it.
L.bikes = {
  { zoneX0 = 1376, zoneX1 = 1560, minY = 150, every = 6.0, speed = 100, endX = 1300, kind = "cart", start = "enter" },
  { zoneX0 = 2350, zoneX1 = 2576, minY = 150, every = 5.5, speed = 105, endX = 2340, kind = "cart", start = "enter" },
}

-- geese (critters.lua): each walks its stretch of path; bark to shoo it away (+200), or jump over it
L.critters = {
  { kind = "goose", x = 1160, y = 184, x0 = 1096, x1 = 1224 },
  { kind = "goose", x = 2340, y = 184, x0 = 2330, x1 = 2352 },
}

-- secrets: reaching one (Pepper's feet in its box) counts it; the tally shows how many were found
L.secrets = {
  { name = "WILLOWS",    x0 = 764,  x1 = 844,  y0 = 100, y1 = 112 },   -- the middle willow's branch
  { name = "HOLLOW LOG", x0 = 1570, x1 = 1600, y0 = 176, y1 = 184 },   -- inside the log
  { name = "OAK TOP",    x0 = 1732, x1 = 1804, y0 = 90,  y1 = 100 },   -- the oak's top branch
}

-- hints (St:hint, drawn by talk.lua): first match wins. With btn ("a", "b", "x", "y", "down") it is Pepper's
-- control hint: a button picture and 1 to 3 words. Without, it is the girl's line. need: see St:zoneHint.
L.hints = {
  { x0 = 0,    x1 = 2880, btn = "y",    text = "BARK!",              need = "magpienear" },
  { x0 = 0,    x1 = 2880, btn = "x",    text = "PICK UP",            need = "nearball" },
  { x0 = 2760, x1 = 2880, btn = "x",    text = "GIVE",               need = "ball" },
  { x0 = 288,  x1 = 352,  btn = "a",    text = "HOLD: BIG JUMP" },
  { x0 = 456,  x1 = 528,  btn = "down", text = "CRAWL" },
  { x0 = 660,  x1 = 736,  btn = "a",    text = "TAP: HOP" },
  { x0 = 0,    x1 = 2880, btn = "y",    text = "BARK: SHOO!",        need = "goose" },
  { x0 = 1960, x1 = 2230, btn = "a",    text = "STOP, THEN HOP" },            -- onto the creek's stones
  { x0 = 1300, x1 = 1328, btn = "a",    text = "HOLD + PUSH: CLIMB" },
  { x0 = 0,    x1 = 2880, btn = "b",    text = "HOLD: SNEAK",        need = "magpieahead" },
  { x0 = 100,  x1 = 176,  btn = "a",    text = "TAP: HOP" },            -- onto the log (once she sneaks)
  { x0 = 800,  x1 = 860,  text = "RIDE THE DUCK BOAT!", maxY = 196 },
  { x0 = 1376, x1 = 1560, text = "CART! GET UP HIGH!", bike = true },
  { x0 = 2350, x1 = 2576, text = "ANOTHER CART! UP HIGH!", bike = true },
  { x0 = 1040, x1 = 1100, text = "A GOOSE! BARK AT IT!" },
  { x0 = 300,  x1 = 2880, text = "THE MAGPIE STILL HAS MY BALL!", need = "magpie" },
  { x0 = 1880, x1 = 2880, text = "BRING ME THE BALL!", need = "ball" },
  { x0 = 1880, x1 = 2880, text = "GO BACK FOR THE BALL!", need = "noball" },
}

L.intro = { "LEVEL 1", "CITY PARK", "A MAGPIE STOLE MIA'S BALL!", "SNEAK UP AND BARK, PEPPER!" }
return L
