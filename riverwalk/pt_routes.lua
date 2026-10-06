-- Playtest lab: the persona bots' routes. Each is the level's autopilot step list (tests.lua, tests_citypark.lua,
-- tests_downtown.lua, mode --auto) copied step for step, with tags the persona layer needs. The autopilots
-- themselves are not touched (their --auto runs and the Pepper golden trace stay exactly as they were).
-- Changes from the autopilot, all marked here:
--   * presses go through ctl (the persona layer): ctl.jump = a held jump, ctl.hop = a tapped hop (A held for
--     2 steps, as the autopilot's jump + wait 1/60 + release), ctl.key("bark" / "act") = Y / X.
--   * tags: ob = the obstacle the step belongs to (retries and quits are counted per obstacle), r = a reactive
--     step (it waits for something in the world: a reaction delay applies, not just timing jitter), w = a wait
--     the persona may not know about (boat, cart, tram, pontoon; not knowing it they go on without waiting),
--     need = a button the step needs (bark, act).
--   * the magpie beat (City Park) and every "walk up to the ball and press X" are not steps: the bot's magpie
--     and fetch controllers do them wherever the bird or the ball happens to be (see pt_bot.lua).
--   * opt = an optional part (bones, a gold bone): take = the autopilot's steps, skip = a shorter way past it.
--   * mv = lead(p): a moving platform. Players see it coming and time the run to it: the step's condition is
--     checked on where the boat or pontoon will be lead s from now (plus the timing jitter), no reaction delay.
--     (The autopilot starts the instant it docks, from a spot it never misses from; a person reacting only then
--     would miss it nearly every time, which is not what people do.)
--   * hw: River Walk's bike zones: on the last perch a player who knows what bikes do stops for one that is
--     coming and goes when it has passed (added; the autopilot just goes)
--   * onto (River Walk): the autopilot's onto() helper, with the jump point shifted by the persona's timing.
--   * sync = x: the step starts an obstacle at x. After a respawn the route restarts at the first such step ahead
--     of the lamp; when stuck, the bot may skip ahead to one whose condition already holds (she got past
--     another way, e.g. hopped over the log instead of onto it).
local R = {}
local function at(c, a, o) local s = { c = c, a = a }; for k, v in pairs(o or {}) do s[k] = v end; return s end
local T = function() return true end
R.T = T                                              -- a step that needs nothing (never a resync target)
local function landedAt(maxY) return function(p) return p.onGround and p.y <= maxY end end

-- Level 1: City Park (tests_citypark.lua --auto)
function R.citypark()
  return {
    at(T, function(c) c.hold("right") end, { ob = "gate" }),
    -- the autopilot first sneaks up to the log and barks; here the magpie controller does that when it can
    at(function(p) return p.x >= 140 end, function(c) c.hop("right") end, { ob = "log" }),
    at(function(p) return p.onGround and p.y <= 169 end, function(c) c.hold("right") end, { ob = "log" }),
    -- 2 a held jump onto the bench, then crawl under the hedge
    at(function(p) return p.x >= 300 and p.onGround and p.y > 183 end, function(c) c.jump("right") end, { sync = 300, ob = "bench" }),
    at(landedAt(157), function(c) c.hold("right") end, { ob = "bench" }),
    at(function(p) return p.x >= 490 and p.onGround and p.y > 183 end, function(c) c.hold("right", "down") end, { sync = 490, ob = "hedge" }),
    at(function(p) return p.x >= 612 end, function(c) c.hold("right") end, { ob = "hedge", lim = 9 }),
    -- 3 the pond: onto the first stone, a hop to the second, wait for the duck boat, ride it, up the bank
    at(function(p) return p.onGround and p.y >= 187 and p.x > 735 end, function(c) c.hold("right") end, { sync = 735, ob = "stones" }),
    at(function(p) return p.x >= 766 end, function(c) c.hop("right") end, { ob = "stones" }),
    at(function(p) return p.x >= 794 end, function(c) c.release() end, { ob = "stones" }),          -- brake in the air
    at(function(p) return p.onGround and p.x >= 800 end, function(c) c.release() end, { ob = "stones" }),
    at(function(p, s) return s.movers[1].x0 <= 842 and s.movers[1].dir < 0 or s.movers[1].x0 <= 841 end, function(c) c.hold("right") end,
      { ob = "boat", lim = 9, w = "boat", mv = function(p) return 0.29 + math.max(0, 845 - p.x - 17) / 120 - 0.08 end }),
    at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 26 end, function(c) c.release() end, { ob = "boat" }),
    at(function(p, s) return s.movers[1].x0 >= 884 end, function(c) c.jump("right") end, { ob = "boat", lim = 9, w = "boat", mv = function() return 0 end }),
    at(function(p) return p.onGround and p.y <= 185 and p.x > 944 end, function(c) c.hold("right") end, { ob = "bank" }),
    -- 4 the bin (jump + scramble), the picnic table, wait there for the leaf cart to pass
    at(function(p) return p.x >= 984 end, function(c) c.jump("right") end, { sync = 984, ob = "bin" }),
    at(landedAt(129), function(c) c.hold("right") end, { ob = "bin" }),
    at(function(p) return p.x >= 1030 end, function(c) c.jump("right") end, { sync = 1030, ob = "picnic table" }),
    at(function(p) return p.onGround and p.y <= 157 and p.x > 1100 end, function(c) c.release() end, { ob = "picnic table" }),
    at(function(p) return p.x >= 1124 or p.vx < 1 end, function(c) c.release() end, { ob = "picnic table" }),
    at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 40 end, function(c) c.hold("right") end,
      { ob = "leaf cart", lim = 12, r = true, w = "cart" }),
    -- 5 the oak: up the branches to the top (gold bone), then off the branches to the right
    { opt = "oak", take = {
      at(function(p) return p.x >= 1446 end, function(c) c.jump() end, { sync = 1446, ob = "oak", lim = 9 }),
      at(landedAt(157), function(c) c.release() end, { ob = "oak" }),
      { wait = 0.15 }, at(T, function(c) c.jump() end, { ob = "oak" }),
      at(landedAt(129), function(c) c.release() end, { ob = "oak" }),
      { wait = 0.15 }, at(T, function(c) c.jump() end, { ob = "oak" }),
      at(landedAt(101), function(c) c.hold("right") end, { ob = "oak" }),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 1480 end, function(c) c.hold("right") end, { ob = "oak", lim = 9 }),
    }, skip = {} },
    -- 6 the playground: up the slide tower, down the slide, the climbing frame, the girl
    at(function(p) return p.x >= 1628 end, function(c) c.jump("right") end, { sync = 1628, ob = "slide", lim = 9 }),
    at(landedAt(153), function(c) c.hold("right") end, { ob = "slide" }),
    at(function(p) return p.onGround and p.y >= 183 and p.x > 1728 end, function(c) c.hold("right") end, { ob = "slide" }),
    -- the climbing frame: bones on its bars. Optional (a dynamic choice, made on the spot): with the ball in her mouth
    -- a persona who does not go for bones runs on to the girl; without it (the magpie's last perch is the frame's
    -- top bar, and the ball lands there) everyone climbs
    { opt = "frame", dyn = function(s, p, pick) return p.carrying == nil or pick == "take" end, take = {
      at(function(p) return p.x >= 1762 end, function(c) c.hop("right") end, { sync = 1762, ob = "frame" }),
      -- changed: the autopilot stops on the landing frame and has 4 px of the bar left; a player brakes in the air
      at(function(p) return p.x >= 1780 end, function(c) c.release() end, { ob = "frame" }),
      at(landedAt(161), function(c) c.release() end, { ob = "frame" }),
      { wait = 0.3 }, at(T, function(c) c.hop() end, { ob = "frame" }),
      at(landedAt(137), function(c) c.release() end, { ob = "frame" }),
      { wait = 0.2 }, at(T, function(c) c.hold("right") end, { ob = "frame" }),
    }, skip = {} },
    { give = true, ob = "girl" },
  }
end

-- Level 2: Downtown (tests_downtown.lua --auto)
function R.downtown()
  return {
    at(T, function(c) c.hold("right") end, { ob = "lane" }),
    -- 1 old town lane: a hop onto each crate
    at(function(p) return p.x >= 106 end, function(c) c.hop("right") end, { ob = "crates" }),
    at(function(p) return p.x >= 138 end, function(c) c.release() end, { ob = "crates" }),            -- brake in the air
    at(landedAt(169), function(c) c.hold("right") end, { ob = "crates" }),
    at(function(p) return p.x >= 152 end, function(c) c.hop("right") end, { ob = "crates" }),
    at(landedAt(153), function(c) c.hold("right") end, { ob = "crates" }),
    -- 2 cafe terrace: onto the first table, its parasol, the second parasol, the shop sign (gold bone).
    -- skip: crawl under both tables, as the hint says; rush: hop from table to table
    { opt = "parasols", take = {
      at(function(p) return p.x >= 322 and p.onGround and p.y > 183 end, function(c) c.jump("right") end, { sync = 322, ob = "cafe tables" }),
      at(landedAt(159), function(c) c.release() end, { ob = "cafe tables" }),
      at(function(p) return math.abs(p.vx) < 1 end, function(c) c.jump() end, { ob = "parasols" }),
      at(landedAt(115), function(c) c.hold("left") end, { ob = "parasols" }),
      at(function(p) return p.x <= 372 end, function(c) c.hold("right") end, { ob = "parasols" }),
      at(function(p) return p.x >= 412 end, function(c) c.jump("right") end, { ob = "parasols" }),
      at(function(p) return p.onGround and p.y <= 115 and p.x > 472 end, function(c) c.hold("right") end, { ob = "parasols" }),
      at(function(p) return p.x >= 518 end, function(c) c.jump("right") end, { ob = "shop sign" }),
      at(function(p) return p.vy > 0 and p.x >= 560 end, function(c) c.release() end, { ob = "shop sign" }),
      at(landedAt(81), function(c) c.hold("right") end, { ob = "shop sign" }),
      -- changed: the autopilot lets go at x 604 and slides off the sign's end with 3 px to spare; a player runs
      -- off it and lets go in the air (the same for the awning below)
      at(function(p) return not p.onGround end, function(c) c.release() end, { ob = "shop sign" }),
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.hold("right") end, { ob = "shop sign" }),
    }, skip = {
      at(function(p) return p.x >= 330 and p.onGround and p.y > 183 end, function(c) c.hold("right", "down") end, { sync = 330, ob = "cafe tables" }),
      at(function(p) return p.x >= 556 end, function(c) c.hold("right") end, { ob = "cafe tables", lim = 12 }),
    }, rush = {
      at(function(p) return p.x >= 322 and p.onGround and p.y > 183 end, function(c) c.jump("right") end, { sync = 322, ob = "cafe tables" }),
      at(landedAt(159), function(c) c.hold("right") end, { ob = "cafe tables" }),
      at(function(p) return p.x >= 412 end, function(c) c.hop("right") end, { ob = "cafe tables" }),
      at(function(p) return p.onGround and p.y <= 159 and p.x > 470 end, function(c) c.hold("right") end, { ob = "cafe tables" }),
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.hold("right") end, { ob = "cafe tables" }),
    } },
    -- 3 market: onto the stall, its awning, down, the crates, the second awning (skip: no awnings)
    { opt = "awnings", take = {
      at(function(p) return p.x >= 652 end, function(c) c.jump("right") end, { sync = 652, ob = "stall" }),
      at(landedAt(157), function(c) c.release() end, { ob = "stall" }),
      at(function(p) return p.x >= 714 or math.abs(p.vx) < 1 end, function(c) c.jump() end, { ob = "awning" }),
      at(landedAt(117), function(c) c.hold("right") end, { ob = "awning" }),
      at(function(p) return not p.onGround end, function(c) c.release() end, { ob = "awning" }),     -- off the awning, brake
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.hold("right") end, { ob = "awning" }),
      at(function(p) return p.x >= 774 end, function(c) c.hop("right") end, { sync = 774, ob = "market crates" }),
      at(function(p) return p.x >= 800 end, function(c) c.release() end, { ob = "market crates" }),   -- brake in the air
      at(landedAt(169), function(c) c.hold("right") end, { ob = "market crates" }),
      at(function(p) return p.x >= 808 end, function(c) c.hop("right") end, { ob = "market crates" }),
      at(landedAt(153), function(c) c.hold("right") end, { ob = "market crates" }),
      at(function(p) return p.x >= 846 end, function(c) c.jump("right") end, { ob = "awning 2" }),
      at(function(p) return p.vy > 0 end, function(c) c.release() end, { ob = "awning 2" }),
      at(landedAt(113), function(c) c.hold("right") end, { ob = "awning 2" }),
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.hold("right") end, { ob = "awning 2" }),
    }, skip = {
      at(function(p) return p.x >= 652 end, function(c) c.jump("right") end, { sync = 652, ob = "stall" }),
      at(landedAt(157), function(c) c.hold("right") end, { ob = "stall" }),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 752 end, function(c) c.hold("right") end, { ob = "stall" }),
      at(function(p) return p.x >= 774 end, function(c) c.hop("right") end, { sync = 774, ob = "market crates" }),
      at(function(p) return p.x >= 800 end, function(c) c.release() end, { ob = "market crates" }),
      at(landedAt(169), function(c) c.hold("right") end, { ob = "market crates" }),
      at(function(p) return p.x >= 808 end, function(c) c.hop("right") end, { ob = "market crates" }),
      at(landedAt(153), function(c) c.hold("right") end, { ob = "market crates" }),
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.hold("right") end, { ob = "market crates" }),
    } },
    -- 4 the plaza: onto the pedestal, bark the cat off, (opt) up the arm to the hat (gold bone), down, the ball
    at(function(p) return p.x >= 1092 end, function(c) c.jump("right") end, { sync = 1092, ob = "pedestal" }),
    at(landedAt(145), function(c) c.release() end, { ob = "pedestal" }),
    at(function(p) return math.abs(p.vx) < 1 end, function(c) c.key("bark") end, { ob = "cat", r = true, need = "bark" }),
    { wait = 0.6 },
    at(function(p, s) return s.cat.state ~= "sit" and s.ball.state ~= "air" end, function(c) end, { ob = "cat", r = true }),
    { opt = "hat", take = {
      at(T, function(c) c.hold("right") end, { ob = "statue" }),
      at(function(p) return p.x >= 1150 end, function(c) c.jump("right") end, { ob = "statue" }),
      at(function(p) return p.x >= 1168 end, function(c) c.hold("jump") end, { ob = "statue" }),   -- brake in the air
      at(landedAt(109), function(c) c.hold("left") end, { ob = "statue" }),
      -- changed: the autopilot lets go at x 1166 and stops on the last pixel under the hat (24 px wide); a little
      -- further left gives a player the same jump with a few pixels to spare
      at(function(p) return p.x <= 1160 end, function(c) c.release() end, { ob = "statue" }),
      { wait = 0.25 }, at(T, function(c) c.jump() end, { ob = "statue hat" }),
      at(landedAt(77), function(c) c.release() end, { ob = "statue hat" }),
      { wait = 0.2 }, at(T, function(c) c.hold("right") end, { ob = "statue hat" }),
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.release() end, { ob = "statue hat", lim = 9 }),
    }, skip = {
      at(T, function(c) c.hold("right") end, { ob = "pedestal" }),
      at(function(p) return p.onGround and p.y >= 183 end, function(c) c.release() end, { ob = "pedestal", lim = 9 }),
    } },
    { fetch = true, ob = "ball" },                                   -- the autopilot's walk up to the ball and X
    { needBall = true },
    -- 5 the fountain with the ball: onto the rim, the bowl, the far rim
    at(T, function(c) c.hold("right") end, { ob = "fountain" }),
    at(function(p) return p.x >= 1374 end, function(c) c.hop("right") end, { sync = 1374, ob = "fountain", lim = 9 }),
    at(landedAt(169), function(c) c.hold("right") end, { ob = "fountain" }),
    at(function(p) return p.x >= 1410 end, function(c) c.hop("right") end, { ob = "fountain" }),
    at(landedAt(161), function(c) c.hold("right") end, { ob = "fountain" }),
    at(function(p) return p.x >= 1478 end, function(c) c.hop("right") end, { ob = "fountain" }),
    at(function(p) return p.onGround and p.y <= 169 and p.x > 1515 end, function(c) c.hold("right") end, { ob = "fountain" }),
    -- 6 tram street: onto the kiosk, onto the shelter roof, wait there for the tram to pass, down to the girl
    at(function(p) return p.x >= 1622 and p.onGround and p.y > 183 end, function(c) c.jump("right") end, { sync = 1622, ob = "kiosk", lim = 9 }),
    at(landedAt(149), function(c) c.hold("right") end, { ob = "kiosk" }),
    at(function(p) return p.x >= 1672 end, function(c) c.jump("right") end, { ob = "shelter" }),
    at(function(p) return p.vy > 0 end, function(c) c.release() end, { ob = "shelter" }),
    at(landedAt(137), function(c) c.release() end, { ob = "shelter" }),
    at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 60 end, function(c) c.hold("right") end,
      { ob = "tram", lim = 12, r = true, w = "tram" }),
    { give = true, ob = "girl" },
  }
end

-- Level 3: River Walk (tests.lua --auto). onto = the autopilot's onto(x0, top, fromX1)
function R.riverwalk()
  local function onto(x0, top, fromX1, ob) return { onto = { x0 = x0, top = top, fromX1 = fromX1 }, ob = ob, lim = 12, sync = x0 - 12 } end
  return {
    at(T, function(c) c.hold("right") end, { ob = "home bench" }),
    at(function(p) return p.x >= 70 end, function(c) c.jump("right") end, { ob = "home bench" }),
    at(landedAt(157), function(c) c.hold("right") end, { ob = "home bench" }),        -- on the bench seat
    onto(401, 152, nil, "flower box"),
    onto(641, 128, nil, "bin"),                                                      -- the bin: jump and scramble
    -- bike zone 1: grit box, planter, flower box; the perches keep her above the bikes
    onto(831, 152, nil, "bikes 1: grit box"), onto(990, 154, 917, "bikes 1: planter"), onto(1113, 152, 1034, "bikes 1: flower box"),
    -- added: on the last perch of a bike zone a player who has seen what bikes do waits for one that is coming
    { hw = true, w = "bike", ob = "bikes 1: flower box", lim = 14 },
    -- down the steps to the quay, then the pontoon
    -- changed: the autopilot lets go at x 1378 and stops 2 px from the river (x 1392); a player stops short of it
    at(function(p) return p.x >= 1362 and p.onGround and p.y >= 215 end, function(c) c.release() end, { sync = 1362, ob = "steps", lim = 14 }),
    at(function(p, s) return s.movers[1].x0 <= 1402 end, function(c) c.hold("right") end,
      { ob = "pontoon", lim = 9, w = "pontoon", mv = function(p) return 0.29 + math.max(0, 1388 - p.x) / 120 end }),
    at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 18 end, function(c) c.release() end, { ob = "pontoon" }),
    at(function(p, s) return s.movers[1].x0 >= 1498 end, function(c) c.jump("right") end, { ob = "pontoon", lim = 9, w = "pontoon", mv = function() return 0 end }),
    at(function(p) return p.onGround and p.y <= 207 and p.x > 1560 end, function(c) c.hold("right") end, { ob = "ferry" }),   -- on the deck
    at(function(p) return p.x >= 1598 end, function(c) c.jump("right") end, { ob = "ferry" }),
    at(landedAt(185), function(c) c.hold("right") end, { ob = "ferry" }),            -- on the saloon roof
    at(function(p) return p.x >= 1630 end, function(c) c.jump("right") end, { ob = "wheelhouse" }),
    at(function(p) return p.x >= 1655 end, function(c) c.hold("jump") end, { ob = "wheelhouse" }),
    at(landedAt(155), function(c) c.release() end, { ob = "wheelhouse" }),           -- on the wheelhouse roof
    { fetch = true, ob = "ball" },                                                  -- the autopilot: wait 0.2, X
    { needBall = true },
    at(T, function(c) c.hold("right") end, { ob = "ferry" }),
    at(function(p) return p.x >= 1757 and p.y >= 205 end, function(c) c.jump("right") end, { sync = 1757, ob = "far quay" }),
    at(function(p) return p.onGround and p.y >= 215 and p.x > 1802 end, function(c) c.hold("right") end, { ob = "far quay" }),
    at(function(p) return p.x >= 1902 end, function(c) c.hold("right", "down") end, { sync = 1902, ob = "bridge" }),   -- crawl under the pier
    at(function(p) return p.x >= 2094 end, function(c) c.hold("right") end, { ob = "bridge", lim = 9 }),
    at(function(p) return p.x >= 2200 and p.y <= 185 end, function(c) c.hold("right") end, { sync = 2200, ob = "steps up", lim = 9 }),
    onto(2290, 154, nil, "planter"),
    -- bike zone 2: flower box, grit box, bin
    onto(2441, 152, nil, "bikes 2: flower box"), onto(2616, 152, 2543, "bikes 2: grit box"), onto(2776, 128, 2702, "bikes 2: bin"),
    { hw = true, w = "bike", ob = "bikes 2: bin", lim = 14 },
    onto(2908, 156, nil, "last bench"),
    { give = true, ob = "girl" },
  }
end

-- the route for a run: optional parts chosen once per run by choose(name, hasRush) -> "take" | "skip" | "rush".
-- Every variant of an optional part stays in the list behind a branch marker, so the bot can still go the short way
-- after giving the detour up (or decide on the spot, dyn).
function R.build(level, choose)
  local src, out, picks = R[level](), {}, {}
  for _, st in ipairs(src) do
    if st.opt then
      local how = choose(st.opt, st.rush ~= nil)
      picks[st.opt] = how
      local br = { branch = st.opt, dyn = st.dyn, pick = how, at = {} }
      out[#out + 1] = br
      local gos = {}
      for _, v in ipairs({ "take", "skip", "rush" }) do
        if st[v] then
          br.at[v] = #out + 1
          for _, x in ipairs(st[v]) do out[#out + 1] = x end
          if v == "take" then out[#out + 1] = { segEnd = st.opt } end
          local go = { go = 0 }; out[#out + 1] = go; gos[#gos + 1] = go
        end
      end
      for _, go in ipairs(gos) do go.go = #out + 1 end
    else out[#out + 1] = st end
  end
  return out, picks
end
return R
