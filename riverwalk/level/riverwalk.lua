-- Level 3: River Walk (greybox). Terrain is in riverwalk.map; this file places everything else.
-- x, y in level pixels; y grows downwards; "feet" = the y Pepper stands on.
-- Upper promenade feet y = 184, lower quay y = 216, river surface y = 224. The level is 3840 px (12 screens).
-- Manner: water and traffic (docs/progression.md). New here: the harbour's rowing boats and the gulls.
--
-- Screens (320 px each):
--   1  Home          crawl under the bench or jump onto its seat (tutorial: hold A to jump higher). Secret: go
--                    left and crawl into Pepper's kennel by the house (a gold bone)
--   2  Promenade A   open pavement, a flower box
--   3  Promenade A   a bin on its own (tutorial: hold A and push to climb), then bike zone 1 starts: the grit box
--   4  Bike zone 1   hop from perch to perch while the bikes pass: planter, flower box. The high route: from the bin
--                    a held jump onto the first kiosk's awning, then the second (gold bone), down onto the planter
--   5  Steps         down to the quay, ride the pontoon over the river
--   6  Boat          the commuter ferry: deck, saloon roof, wheelhouse roof; pick up the ball up there
--   7  Bridge        the far quay, crawl under the bridge pier with the ball
--   8  Harbour       open water: hop onto the rowing boat, ride it to the jetty; a gull swoops (crawl to duck, or
--                    bark while it squawks). Gold high over the jetty (secret JETTY JUMP)
--   9  Harbour       wait on the jetty for the second boat, ride it to the far quay, steps back up
--  10  Promenade B   a planter on its own and a gull, then bike zone 2 (faster bikes): the flower box
--  11  Bike zone 2   grit box, a planter as a step (a tap hop and a scramble), bin
--  12  The girl      a bench, then the cafe: give her the ball, GOOD GIRL!
-- Lamps about every 2 screens. Falling in with the ball: it comes back by the last lamp she carried it past.
--
-- props: kind = solid | oneway | decor; layer = "back" (behind Pepper), "play", "front" (in front of Pepper)
-- art = an image in art/scene, drawn bottom-left on the box (x0, y1), or on (ax, ay) when the art is bigger than
-- the box; without it the prop is a greybox. The bench's box is only its seat (y 156-165): Pepper crawls under
-- it (19 px gap) or jumps onto it; its posts and backrest are drawn, not solid. depth = 5: its shadow fills the
-- ground under the seat, so it stands on the pavement.
-- Obstacles (bench, bin, flower box, grit box, planter) stand on Pepper's walking line (y 184), so they read as
-- things in her way. They stand apart, with clear pavement between them; the gaps vary.
-- Decoration (the pot, the lamp posts, the trees) stands on the back edge of the pavement by the water, 10 px
-- behind her line (its box ends at y 174), so it reads as scenery she passes.
-- Code-drawn pieces (L.pieces, setpieces.lua): the kennel and the kiosks' awnings are obstacles (crisp, 1 px dark
-- outline; their collision is a hidden prop with the same box), the kiosks themselves decoration (faded, base
-- y 174). Secrets (L.secrets, counted on the tally): the kennel, the kiosk roofs.
local L = {}
L.name = "RIVER WALK"
L.number = 3
L.map = "level/riverwalk.map"
L.time = 420
L.start = { x = 52, y = 184 }

-- the ferry's art left x: hull 1562-1797, between the pontoon's far end (1552) and the far quay (1808)
local FX = 1560

L.props = {
  -- screen 1: home
  -- the starter composition (the user's): the house's left edge and the tree's cut left side sit exactly on the
  -- level's left edge, which the camera never passes, so neither looks cropped; the tree leans over Pepper's start
  { name = "HOME",     kind = "decor",  layer = "back", x0 = 0,    x1 = 77,   y0 = 39,  y1 = 174, art = "building" },
  { name = "TREE",     kind = "decor",  layer = "back", x0 = -2,   x1 = 112,  y0 = 47,  y1 = 174, art = "tree" },
  { name = "POT",      kind = "decor",  layer = "play", x0 = 214,  x1 = 231,  y0 = 147, y1 = 174, art = "pot" },
  { name = "",         kind = "decor",  layer = "back", x0 = 80,   x1 = 1288, y0 = 144, y1 = 174, railing = true },   -- decorative railing by the water
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 93,   x1 = 189,  y0 = 156, y1 = 165, art = "bench", ax = 90, ay = 184, depth = 5 },
  -- Pepper's kennel by the house (drawn in code): its roof and walls are solid down to the doorway (y 148-165),
  -- 19 px to crawl in; a gold bone is inside. It ends 1 px left of her box at the start.
  { name = "KENNEL",   kind = "solid",  layer = "play", x0 = 0,    x1 = 34,   y0 = 148, y1 = 165, hidden = true },
  -- promenade A
  { name = "",         kind = "decor",  layer = "back", x0 = 520,  x1 = 621,  y0 = 74,  y1 = 174, art = "tree_far" },
  { name = "FLOWERS",  kind = "solid",  layer = "play", x0 = 401,  x1 = 503,  y0 = 152, y1 = 184, art = "flowerbox_front", ax = 400, ay = 184 },
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 641,  x1 = 676,  y0 = 128, y1 = 184, art = "bin", ax = 640, ay = 184 },
  -- bike zone 1: three perches with clear pavement between them
  { name = "",         kind = "decor",  layer = "back", x0 = 1056, x1 = 1164, y0 = 39,  y1 = 174, art = "tree_near" },
  { name = "SAND",     kind = "solid",  layer = "play", x0 = 831,  x1 = 917,  y0 = 152, y1 = 184, art = "gritbox_front", ax = 830, ay = 184 },
  { name = "PLANTER",  kind = "solid",  layer = "play", x0 = 990,  x1 = 1034, y0 = 154, y1 = 184, art = "planter_sq" },
  { name = "FLOWERS",  kind = "solid",  layer = "play", x0 = 1113, x1 = 1215, y0 = 152, y1 = 184, art = "flowerbox_front", ax = 1112, ay = 184 },
  -- the high route over bike zone 1: two kiosks at the back of the pavement; their awnings (one-way, top y 112,
  -- drawn in code) reach out over Pepper's line, high above the bikes
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 736,  x1 = 824,  y0 = 112, y1 = 116, hidden = true },
  { name = "AWNING",   kind = "oneway", layer = "play", x0 = 888,  x1 = 968,  y0 = 112, y1 = 116, hidden = true },
  -- steps, quay and the river
  -- the ferry (art/scene/ferry.png, 252 x 93): one image; three hidden boxes give its deck (y 206), the saloon
  -- roof (y 184, 22 px up: a hop) and the wheelhouse roof (y 154, 30 px up: a held jump). The hull sits 9 px
  -- into the river.
  { name = "BOAT",     kind = "solid",  layer = "play", x0 = FX + 2,   x1 = FX + 237, y0 = 206, y1 = 236, art = "ferry", ax = FX, ay = 233, noshadow = true },
  { name = "SALOON",   kind = "solid",  layer = "play", x0 = FX + 60,  x1 = FX + 180, y0 = 184, y1 = 206, hidden = true },
  { name = "WHEELHOUSE", kind = "solid", layer = "play", x0 = FX + 97, x1 = FX + 145, y0 = 154, y1 = 184, hidden = true },
  -- the harbour (screens 8-9, 2112-2752), on the quay's level: open water x 2192-2640 (surface y 224). Two rowing
  -- boats (movers; a rower in each) row to and fro; between them a jetty on piles (top y 196, 16 px above a boat's
  -- deck: a hop). Gulls circle over the water and swoop at a standing Pepper (crawl to duck, or bark).
  { name = "JETTY",    kind = "solid",  layer = "play", x0 = 2400, x1 = 2448, y0 = 196, y1 = 240, hidden = true },   -- drawn in code
  -- promenade B
  { name = "",         kind = "decor",  layer = "back", x0 = 2880, x1 = 3626, y0 = 144, y1 = 174, railing = true },   -- decorative railing by the water
  { name = "",         kind = "decor",  layer = "back", x0 = 2978, x1 = 3079, y0 = 74,  y1 = 174, art = "tree_far" },
  { name = "PLANTER",  kind = "solid",  layer = "play", x0 = 2930, x1 = 2974, y0 = 154, y1 = 184, art = "planter_sq" },
  -- bike zone 2
  { name = "POT",      kind = "decor",  layer = "play", x0 = 3188, x1 = 3205, y0 = 147, y1 = 174, art = "pot" },
  { name = "FLOWERS",  kind = "solid",  layer = "play", x0 = 3081, x1 = 3183, y0 = 152, y1 = 184, art = "flowerbox_front", ax = 3080, ay = 184 },
  { name = "SAND",     kind = "solid",  layer = "play", x0 = 3240, x1 = 3326, y0 = 152, y1 = 184, art = "gritbox_front", ax = 3239, ay = 184 },
  -- a planter right before the bin: a step (30 px: a tap hop and a scramble), then 26 px more up to the bin top
  { name = "PLANTER",  kind = "solid",  layer = "play", x0 = 3372, x1 = 3416, y0 = 154, y1 = 184, art = "planter_sq" },
  { name = "BIN",      kind = "solid",  layer = "play", x0 = 3416, x1 = 3451, y0 = 128, y1 = 184, art = "bin", ax = 3415, ay = 184 },
  -- screen 10: the girl
  { name = "GABLE",    kind = "decor",  layer = "back", x0 = 3626, x1 = 3696, y0 = -1,  y1 = 174, art = "gable" },
  { name = "CAFE",     kind = "decor",  layer = "back", x0 = 3690, x1 = 3840, y0 = -31, y1 = 174, art = "cafe" },
  { name = "BENCH",    kind = "solid",  layer = "play", x0 = 3548, x1 = 3644, y0 = 156, y1 = 165, art = "bench", ax = 3545, ay = 184, depth = 5 },
  -- the bridge over the far quay (screen 7): granite abutment art (138 x 162) over the pier's collision
  -- (riverwalk.map, x 1936-2072, y 0-192); Pepper crawls through the low passage under its lintel (y 192-216).
  -- Drawing only: kind decor adds no collision. covers = true: the ground painter leaves the pier's greybox out.
  { name = "",         kind = "decor",  layer = "play", x0 = 1935, x1 = 2073, y0 = 30,  y1 = 192, art = "pier", noshadow = true, covers = true },
  -- foreground frame: the tops of dark mooring piles (art/scene/pile.png, 18 x 182) rising into the bottom of the
  -- screen in front of everything. Their tops are at y 221, below every line Pepper stands on (lowest: the
  -- quay, 216), so they never hide her.
  { name = "",         kind = "decor",  layer = "front", x0 = 1548, x1 = 1566, y0 = 221, y1 = 403, art = "pile" },
  { name = "",         kind = "decor",  layer = "front", x0 = 1572, x1 = 1590, y0 = 225, y1 = 407, art = "pile" },
  { name = "",         kind = "decor",  layer = "front", x0 = 2098, x1 = 2116, y0 = 221, y1 = 403, art = "pile" },
}

-- dark passages drawn behind the pavement (the inside of the bridge, under the pier's lintel)
L.passages = {
  { x0 = 1936, x1 = 2072, y0 = 192, y1 = 216 },
}

-- lamp posts: every one is a checkpoint that lights up and saves Pepper's place when she passes
-- about one every 2 screens (City Park: every screen; Downtown: every 1.5)
L.lamps = {
  { x = 590,  y = 184, checkpoint = true },
  { x = 1350, y = 216, checkpoint = true },
  { x = 2120, y = 216, checkpoint = true },    -- before the harbour
  { x = 2660, y = 216, checkpoint = true },    -- after it
  { x = 3215, y = 184, checkpoint = true },
}
-- a lamp Pepper reaches while carrying the ball becomes its home (a ball lost in the harbour comes back there)
L.ballHomeAtLamps = true

-- code-drawn pieces (setpieces.lua); each matches a hidden collision prop above
L.pieces = {
  { kind = "kennel", x0 = 0, x1 = 34, y0 = 148, door = 165 },
  { kind = "kiosk",  x0 = 736, x1 = 824, y0 = 112, bx0 = 748, bx1 = 812 },
  { kind = "kiosk",  x0 = 888, x1 = 968, y0 = 112, bx0 = 900, bx1 = 956 },
  { kind = "jetty",  x0 = 2400, x1 = 2448, y0 = 196 },
}

-- the pontoon: a rope ferry over the river (water 1392-1808). It waits by the ferry; the ferry's crew winch it
-- over to the quay when Pepper comes near (call: x 1150-1398, from bike zone 1's last flower box), so it is
-- there when she gets down the steps; when she stands on it, it takes her across to the ferry.
L.movers = {
  { name = "PONTOON", x0 = 1400, x1 = 1448, y0 = 214, y1 = 220, from = 1400, to = 1504, speed = 30,
    call = { 1150, 1398 }, callSpeed = 60, rope = { 1392, 1562 } },
  -- the rowing boats in the harbour: rowed to and fro between from and to (deck y 212, 56 wide), resting 1.5 s at
  -- each end. The first one turns at the quay (2192) and by the jetty (2400); the second by the jetty and at the
  -- far quay (2640).
  { name = "ROWBOAT", x0 = 2196, x1 = 2252, y0 = 212, y1 = 218, from = 2196, to = 2340, speed = 30, pause = 1.5 },
  { name = "ROWBOAT", x0 = 2456, x1 = 2512, y0 = 212, y1 = 218, from = 2456, to = 2580, speed = 34, pause = 1.5 },
}
-- gulls (critters.lua): one over the harbour, one over promenade B up to bike zone 2
L.critters = {
  { kind = "gull", x0 = 2192, x1 = 2640, every = 4.5 },
  { kind = "gull", x0 = 2880, x1 = 3060, every = 4.5 },     -- (over promenade B before the bikes, not over them)
}

L.ball = { x = FX + 108, y = 154 }
L.girl = { x = 3780, y = 184 }
L.outro = { "UP ON SODER MIA DROPPED", "THE BALL. IT ROLLED AWAY..." }

-- bones: x, feet y (drawn floating 9 px above); super = 1,000 points
L.bones = {
  -- promenade A
  { x = 116, y = 156 }, { x = 141, y = 156 }, { x = 166, y = 156 }, { x = 250, y = 184 }, { x = 340, y = 184 },
  { x = 426, y = 152 }, { x = 452, y = 152 }, { x = 478, y = 152 }, { x = 600, y = 184 }, { x = 658, y = 128 },
  { x = 760, y = 184 },
  -- the kennel (gold, inside) and the kiosk roofs (gold on the second)
  { x = 16, y = 184, super = true }, { x = 760, y = 112 }, { x = 800, y = 112 }, { x = 928, y = 112, super = true },
  -- bike zone 1
  { x = 852, y = 152 }, { x = 874, y = 152 }, { x = 896, y = 152 }, { x = 1012, y = 154 },
  { x = 1140, y = 152 }, { x = 1164, y = 152 }, { x = 1188, y = 152 }, { x = 1248, y = 184 },
  -- steps, pontoon, ferry
  { x = 1298, y = 194 }, { x = 1340, y = 216 }, { x = 1436, y = 192 }, { x = 1472, y = 180 }, { x = 1508, y = 192 },
  { x = FX + 18, y = 206 }, { x = FX + 90, y = 184 }, { x = FX + 132, y = 154, super = true }, { x = FX + 215, y = 206 },
  -- far quay, under the bridge
  { x = 1872, y = 216 }, { x = 1962, y = 216 }, { x = 2004, y = 216 }, { x = 2046, y = 216 },
  -- the harbour: over the boats, the jetty (gold high above it), the far quay
  { x = 2150, y = 216 }, { x = 2236, y = 196 }, { x = 2300, y = 196 }, { x = 2364, y = 196 }, { x = 2414, y = 196 },
  { x = 2434, y = 196 }, { x = 2424, y = 150, super = true }, { x = 2490, y = 196 }, { x = 2550, y = 196 },
  { x = 2610, y = 196 }, { x = 2690, y = 216 }, { x = 2762, y = 216 },
  -- promenade B
  { x = 2852, y = 184 }, { x = 2952, y = 154 }, { x = 3030, y = 184 },
  { x = 3106, y = 152 }, { x = 3132, y = 152 }, { x = 3158, y = 152 },
  { x = 3262, y = 152 }, { x = 3284, y = 152 }, { x = 3306, y = 152 }, { x = 3394, y = 154 }, { x = 3433, y = 128 },
  -- the end
  { x = 3572, y = 156 }, { x = 3596, y = 156 }, { x = 3620, y = 156 },
}

-- bike zones: a cyclist rides right to left along the promenade while Pepper is in a zone; it rides on until
-- it passes endX
L.bikes = {
  { zoneX0 = 790,  zoneX1 = 1228, minY = 150, every = 5.5, speed = 125, endX = 600 },     -- (was 6.5 s, 115 px/s)
  { zoneX0 = 3040, zoneX1 = 3470, minY = 150, every = 5.0, speed = 135, endX = 2890 },    -- (was 6.0 s, 115 px/s)
}

-- secrets: reaching one (Pepper's feet in its box) counts it; the tally shows how many were found
L.secrets = {
  { name = "KENNEL",      x0 = 0,   x1 = 30,  y0 = 176, y1 = 184 },    -- inside the kennel
  { name = "KIOSK ROOFS", x0 = 876, x1 = 980, y0 = 100, y1 = 112 },    -- the second kiosk's awning
  { name = "JETTY JUMP",  x0 = 2400, x1 = 2448, y0 = 140, y1 = 152 },  -- a held jump from the jetty (gold)
}

-- hints (St:hint, drawn by talk.lua): first match wins. With btn ("a", "b", "x", "y", "down") it is Pepper's
-- control hint: a button picture and 1 to 3 words. Without, it is the girl's line. need: see St:zoneHint.
L.hints = {
  { x0 = 1550, x1 = 1800, btn = "x",    text = "PICK UP",            need = "nearball" },
  { x0 = 3690, x1 = 3840, btn = "x",    text = "GIVE",               need = "ball" },
  { x0 = 0,    x1 = 92,   btn = "a",    text = "HOLD: BIG JUMP" },
  { x0 = 560,  x1 = 641,  btn = "a",    text = "HOLD + PUSH: CLIMB" },
  { x0 = 1868, x1 = 1936, btn = "down", text = "CRAWL" },
  { x0 = 0,    x1 = 3840, btn = "down", text = "DUCK!",              need = "gull" },
  { x0 = 790,  x1 = 1228, text = "BIKES! GET UP HIGH!", bike = true },
  { x0 = 1290, x1 = 1400, text = "RIDE THE PONTOON!" },
  { x0 = 1550, x1 = 1800, text = "CLIMB UP TO THE WHEELHOUSE!", need = "noball" },
  { x0 = 2100, x1 = 2196, text = "HOP ON THE ROWING BOAT!" },
  { x0 = 2400, x1 = 2448, text = "WAIT FOR THE NEXT BOAT!", maxY = 197 },
  { x0 = 3040, x1 = 3470, text = "BIKES! GET UP HIGH!", bike = true },
  { x0 = 3620, x1 = 3840, text = "BRING ME THE BALL!", need = "ball" },
  { x0 = 3620, x1 = 3840, text = "FIND THE BALL ON THE BOAT!", need = "untouched" },
  { x0 = 3620, x1 = 3840, text = "GO BACK FOR THE BALL!", need = "noball" },
}

L.intro = { "LEVEL 3", "RIVER WALK", "THE BALL LANDED ON A BOAT.", "FETCH IT FOR MIA!" }
return L
