-- Level 6: Night Harbour (greybox). Terrain is in night.map (tools/make_night_map.py); this file places the rest.
-- Same format as the other levels. The quay (feet) is y 184; the water in the gaps starts at y 208. The level is
-- 4736 px (14.8 screens; the two rowboat gaps widened 128 px each for the real-size boats, 25 Oct). See
-- docs/night_beatsheet.md.
--
-- Screens (320 px each):
--   1  The quay        the fox sits there with Mia's ball; come close and it runs off into the dark
--   2  Lantern street  a first water gap (48 px: a hop), fish crates; sniff (hold L1 / Q) shows the fox's trail
--   3  The tarp        hideout 1: the fox is under the tarp of a beached boat. Bark at it: it bolts
--   4  Old jetty       two old planks over the water crumble half a second after Pepper lands: keep moving
--   5  The rowboat     a fisherman rows his boat to and fro over a wide gap: ride it across
--   6  Fish boxes      a box step, the net shed (crawl under it or go over its roof)
--   7  The fish crates hideout 2: behind the crates. A crate stack and the shed roof (a secret, gold bone)
--   8  Rotten planks   four crumbling planks in a row over the water: hop, hop, hop, hop
--   9  Two boats       a boat, a mooring post, a second boat: timing
--   10 The low jetty   hideout 3: under the jetty. Bark: the fox drops the ball and runs off for good. Crawl in
--   11 Back over       carry the ball: a third rowboat, one more crumbling plank
--   12 Crate tower     a climb to the top of the stacked crates (a secret, gold bone), or walk on
--   13 The slipway     the last water, carrying the ball: a boat, one crumbling plank, a second boat
--   14 Home            Mia waits at the front door under the porch light: give her the ball. THE END
--
-- Story (level 5 of 5): it got dark on the way home along the harbour, and a fox snatched the ball. The fox hides
-- three times (L.fox); sniff to see where, bark to chase it out; the third time it drops the ball.
-- Night rules (night.lua): L.dark draws the darkness with light pools (the lamp posts, L.lights, Pepper's own
-- glow); hidden bones only show in a light or while she sniffs. crumble = true props: 0.5 s after Pepper stands on
-- one it falls into the water, and it is back 3 s later.
local L = {}
L.name = "NIGHT HARBOUR"
L.number = 6
L.title = "Pepper: Night Harbour"
L.scenery = "greybox"
L.greyStyle = "town"
L.map = "level/night.map"
L.time = 420
L.start = { x = 60, y = 184 }
L.dark = true

L.props = {
  -- 2 lantern street: fish crates (16 px, then 32 px)
  { name = "",         kind = "solid",  layer = "play", x0 = 520,  x1 = 552,  y0 = 168, y1 = 184 },
  { name = "CRATES",   kind = "solid",  layer = "play", x0 = 552,  x1 = 584,  y0 = 152, y1 = 184, label = "top" },
  -- 3 hideout 1: a beached rowboat under a tarp (decoration; the fox hides under it)
  { name = "TARP",     kind = "decor",  layer = "back", x0 = 760,  x1 = 848,  y0 = 160, y1 = 184, label = "top" },
  -- 4 the old jetty: two crumbling planks over the gap (water x 1000-1160)
  { name = "",         kind = "oneway", layer = "play", x0 = 1040, x1 = 1080, y0 = 184, y1 = 190, crumble = true, hidden = true },
  { name = "",         kind = "oneway", layer = "play", x0 = 1112, x1 = 1152, y0 = 184, y1 = 190, crumble = true, hidden = true },
  -- 6 fish boxes: a step (16 px, 32 px), then the net shed: its roof is solid (y 158-165), 19 px to crawl under
  { name = "",         kind = "solid",  layer = "play", x0 = 1808, x1 = 1840, y0 = 168, y1 = 184 },
  { name = "BOXES",    kind = "solid",  layer = "play", x0 = 1840, x1 = 1872, y0 = 152, y1 = 184, label = "top" },
  { name = "",         kind = "decor",  layer = "back", x0 = 1932, x1 = 1936, y0 = 165, y1 = 184 },     -- shed posts
  { name = "",         kind = "decor",  layer = "back", x0 = 1992, x1 = 1996, y0 = 165, y1 = 184 },
  { name = "NET SHED", kind = "solid",  layer = "play", x0 = 1928, x1 = 2000, y0 = 158, y1 = 165, label = "below" },
  -- 7 hideout 2: the fish crates at the back (decoration; the fox hides behind them). The high route: a crate
  -- stack (32 px up) and the fish shed's roof (one-way, 40 px above the stack): the SHED ROOF secret
  { name = "",         kind = "decor",  layer = "back", x0 = 2080, x1 = 2176, y0 = 104, y1 = 184 },     -- the shed
  { name = "ROOF",     kind = "oneway", layer = "play", x0 = 2088, x1 = 2168, y0 = 112, y1 = 116, label = "below" },
  { name = "STACK",    kind = "solid",  layer = "play", x0 = 2040, x1 = 2072, y0 = 152, y1 = 184, label = "top" },
  { name = "CRATES",   kind = "decor",  layer = "back", x0 = 2192, x1 = 2256, y0 = 144, y1 = 184, label = "top" },
  -- 8 rotten planks: four in a row over the gap (water x 2408-2648), 32 px apart (r7/curve: 24 px wide, were 32:
  --   each hop has to land on a narrower plank)
  { name = "",         kind = "oneway", layer = "play", x0 = 2436, x1 = 2460, y0 = 184, y1 = 190, crumble = true, hidden = true },
  { name = "",         kind = "oneway", layer = "play", x0 = 2492, x1 = 2516, y0 = 184, y1 = 190, crumble = true, hidden = true },
  { name = "",         kind = "oneway", layer = "play", x0 = 2548, x1 = 2572, y0 = 184, y1 = 190, crumble = true, hidden = true },
  { name = "",         kind = "oneway", layer = "play", x0 = 2604, x1 = 2628, y0 = 184, y1 = 190, crumble = true, hidden = true },
  -- 9 the mooring post between the two boats (top y 176, standing in the water)
  { name = "POST",     kind = "solid",  layer = "play", x0 = 2840, x1 = 2856, y0 = 176, y1 = 240, label = "top" },
  -- 10 hideout 3: the low jetty. Its deck is solid (y 158-165): 19 px to crawl under, where the fox hides
  { name = "",         kind = "decor",  layer = "back", x0 = 3092, x1 = 3096, y0 = 165, y1 = 184 },     -- jetty legs
  { name = "",         kind = "decor",  layer = "back", x0 = 3200, x1 = 3204, y0 = 165, y1 = 184 },
  { name = "LOW JETTY", kind = "solid", layer = "play", x0 = 3088, x1 = 3208, y0 = 158, y1 = 165, label = "below" },
  -- 11 two crumbling planks (water x 3680-3776; r7/curve: two narrow ones instead of one: hop, hop, carrying the ball)
  { name = "",         kind = "oneway", layer = "play", x0 = 3696, x1 = 3720, y0 = 184, y1 = 190, crumble = true, hidden = true },
  { name = "",         kind = "oneway", layer = "play", x0 = 3736, x1 = 3760, y0 = 184, y1 = 190, crumble = true, hidden = true },
  -- 12 the crate tower: 16, 32, then 64 px up (a held jump from the second step); gold bone on top
  { name = "",         kind = "solid",  layer = "play", x0 = 3856, x1 = 3888, y0 = 168, y1 = 184 },
  { name = "",         kind = "solid",  layer = "play", x0 = 3888, x1 = 3920, y0 = 152, y1 = 184 },
  { name = "TOWER",    kind = "solid",  layer = "play", x0 = 3920, x1 = 3952, y0 = 120, y1 = 184, label = "top" },
  -- 13 the slipway (water x 4056-4336): a boat, a crumbling plank in the middle, a second boat
  { name = "",         kind = "oneway", layer = "play", x0 = 4216, x1 = 4248, y0 = 184, y1 = 190, crumble = true, hidden = true },
  -- 14 home: the house (decoration) and its door
  { name = "HOME",     kind = "decor",  layer = "back", x0 = 4496, x1 = 4624, y0 = 72,  y1 = 184, label = "top" },
  { name = "DOOR",     kind = "decor",  layer = "back", x0 = 4568, x1 = 4592, y0 = 140, y1 = 184 },
  -- foreground frame: mooring piles
  { name = "",         kind = "decor",  layer = "front", x0 = 1588, x1 = 1600, y0 = 221, y1 = 240 },
  { name = "",         kind = "decor",  layer = "front", x0 = 2908, x1 = 2920, y0 = 221, y1 = 240 },
}

-- lamp posts: every one is a checkpoint (about one every three screens, closer near the end) and a pool of light
L.lamps = {
  { x = 296,  y = 184, checkpoint = true },
  { x = 1290, y = 184, checkpoint = true },    -- (25 Oct: 1240 -> 1290, 2328 -> 2290, 3304 -> 3290: the wider
  { x = 2290, y = 184, checkpoint = true },    --  rowboat gaps; lamps stay at most 1000 px apart)
  { x = 3290, y = 184, checkpoint = true },
  { x = 4016, y = 184, checkpoint = true },
}
-- other lights in the dark (x, y = the light's middle, r = its radius): lanterns, ship lights, windows, the porch
L.lights = {
  { x = 600,  y = 150, r = 48, kind = "lantern" }, { x = 980,  y = 150, r = 48, kind = "lantern" },
  { x = 1568, y = 176, r = 48, kind = "boat" },     { x = 1888, y = 150, r = 48, kind = "lantern" },
  { x = 2688, y = 150, r = 48, kind = "lantern" },  { x = 2848, y = 150, r = 40, kind = "lantern" },
  { x = 3576, y = 176, r = 48, kind = "boat" },     { x = 3816, y = 150, r = 48, kind = "lantern" },
  { x = 4232, y = 176, r = 44, kind = "boat" },
  { x = 4536, y = 112, r = 32, kind = "window" },   { x = 4600, y = 112, r = 32, kind = "window" },
  { x = 4580, y = 150, r = 72, kind = "porch" },
}

-- the rowboats: rowed to and fro (ping-pong movers, deck y 196, 12 px below the quay and 12 px above the water;
-- real size since 25 Oct: 178 wide, the gaps widened 128 px each)
L.movers = {
  { name = "ROWBOAT", x0 = 1324, x1 = 1502, y0 = 196, y1 = 202, from = 1324, to = 1506, speed = 28 },
  { name = "BOAT",    x0 = 2732, x1 = 2780, y0 = 196, y1 = 202, from = 2732, to = 2780, speed = 24 },
  { name = "BOAT",    x0 = 2864, x1 = 2912, y0 = 196, y1 = 202, from = 2864, to = 2916, speed = 26 },
  { name = "ROWBOAT", x0 = 3372, x1 = 3550, y0 = 196, y1 = 202, from = 3372, to = 3474, speed = 24 },
  { name = "BOAT",    x0 = 4060, x1 = 4108, y0 = 196, y1 = 202, from = 4060, to = 4140, speed = 26 },
  { name = "BOAT",    x0 = 4256, x1 = 4304, y0 = 196, y1 = 202, from = 4256, to = 4296, speed = 30 },   -- (r7: 22 -> 30, to 4028 -> 4040)
}

-- the fox (night.lua) has the ball. It sits on the quay at the start and runs into the dark when Pepper comes
-- within `flee` px; then it hides at each hideout in turn. Hidden, it has to be found first (sniff close by); then a
-- bark within `bark` px (and 48 px up or down) of the hideout chases it on; at the last one it drops the ball there
-- and runs off.
L.ball = { x = 240, y = 184 }
L.fox = { x = 240, y = 184, flee = 120, bark = 96,
  hideouts = {
    { x = 804,  y = 184, name = "TARP" },
    { x = 2224, y = 184, name = "CRATES" },
    { x = 3148, y = 184, name = "JETTY" },
  } }
L.ballBack = "THE BALL IS UNDER THE DOCK!"
L.pickupSay = "BRING ME THE BALL, PEPPER!"
L.girl = { x = 4656, y = 184 }
L.outro = { "HOME AT LAST!", "GOOD NIGHT, PEPPER!" }

-- bones: x, feet y (drawn floating 9 px above); super = 1,000 points. In the dark they show only in a light or
-- while Pepper sniffs.
L.bones = {
  -- 1 the quay
  { x = 120, y = 184 }, { x = 160, y = 184 }, { x = 200, y = 184 },
  -- 2 lantern street: over the gap, the crates
  { x = 360, y = 184 }, { x = 424, y = 160 }, { x = 480, y = 184 }, { x = 536, y = 168 }, { x = 568, y = 152 }, { x = 620, y = 184 },
  -- 3 the tarp
  { x = 700, y = 184 }, { x = 880, y = 184 }, { x = 930, y = 184 },
  -- 4 old jetty
  { x = 1060, y = 184 }, { x = 1132, y = 184 }, { x = 1200, y = 184 },
  -- 5 the rowboat
  { x = 1352, y = 180 }, { x = 1420, y = 180 }, { x = 1616, y = 180 }, { x = 1708, y = 184 },
  -- 6 fish boxes and the net shed
  { x = 1824, y = 168 }, { x = 1856, y = 152 }, { x = 1964, y = 158 }, { x = 1964, y = 184 }, { x = 2018, y = 184 },
  -- 7 the crates, the stack, the shed roof (gold)
  { x = 2056, y = 152 }, { x = 2128, y = 112, super = true }, { x = 2278, y = 184 }, { x = 2368, y = 184 },
  -- 8 rotten planks
  { x = 2448, y = 184 }, { x = 2504, y = 184 }, { x = 2560, y = 184 }, { x = 2616, y = 184 },
  -- 9 two boats
  { x = 2756, y = 196 }, { x = 2848, y = 176 }, { x = 2888, y = 196 }, { x = 3008, y = 184 },
  -- 10 the low jetty (gold underneath, past the fox)
  { x = 3068, y = 184 }, { x = 3128, y = 158 }, { x = 3188, y = 184, super = true }, { x = 3248, y = 184 },
  -- 11 back over
  { x = 3398, y = 180 }, { x = 3616, y = 180 }, { x = 3724, y = 184 }, { x = 3776, y = 184 },
  -- 12 crate tower (gold on top)
  { x = 3872, y = 168 }, { x = 3904, y = 152 }, { x = 3936, y = 120, super = true }, { x = 4016, y = 184 },
  -- 13 the slipway
  { x = 4084, y = 196 }, { x = 4232, y = 184 }, { x = 4280, y = 196 }, { x = 4376, y = 184 },
  -- 14 home
  { x = 4436, y = 184 }, { x = 4476, y = 184 },
}

L.bikes = {}

-- secrets: reaching one (Pepper's feet in its box) counts it
L.secrets = {
  { name = "SHED ROOF",   x0 = 2088, x1 = 2168, y0 = 100, y1 = 112 },
  { name = "CRATE TOWER", x0 = 3920, x1 = 3952, y0 = 108, y1 = 120 },
}

-- hints: first match wins (see St:zoneHint; the fox's needs are night.lua's: fox, foxhidden, sniffhere, foxnear, dropped)
L.hints = {
  { x0 = 0,    x1 = 4736, btn = "y",     text = "BARK!",           need = "foxnear" },
  { x0 = 0,    x1 = 4736, btn = "x",     text = "PICK UP",         need = "nearball" },
  { x0 = 4576, x1 = 4736, btn = "x",     text = "GIVE",            need = "ball" },
  { x0 = 0,    x1 = 4736, btn = "sniff", text = "HOLD: SNIFF",  need = "sniffhere" },
  { x0 = 300,  x1 = 760,  btn = "sniff", text = "HOLD: SNIFF",  need = "foxhidden" },
  { x0 = 340,  x1 = 400,  btn = "a",     text = "TAP: HOP" },
  { x0 = 1270, x1 = 1320, text = "JUMP ON THE BOAT!" },
  { x0 = 960,  x1 = 1160, text = "WOBBLY WOOD! KEEP GOING!" },
  { x0 = 2368, x1 = 2648, text = "WOBBLY WOOD! KEEP GOING!" },
  { x0 = 3956, x1 = 4056, text = "WAIT FOR THE BOAT!",         need = "ball" },
  { x0 = 0,    x1 = 400,  text = "A FOX TOOK MY BALL!",        need = "fox" },
  { x0 = 400,  x1 = 4736, text = "SNIFF OUT THE FOX!",         need = "foxhidden" },
  { x0 = 3228, x1 = 4736, text = "BRING ME THE BALL!",         need = "ball" },
  { x0 = 3228, x1 = 4736, text = "GO BACK FOR THE BALL!",      need = "dropped" },
}

L.intro = { "LEVEL 6", "NIGHT HARBOUR", "A FOX TOOK THE BALL!" }
return L
