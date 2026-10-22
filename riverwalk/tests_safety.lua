-- The safety nets (branch r6/engine), checked the same way in every level's --physics run. Each level's tests file
-- calls this once its own steps are built: require("tests_safety")(steps, api, report). It adds its steps before
-- the last one (the "N of M passed" summary). The hazards are found in the level itself:
--   traffic  each kind of vehicle in L.bikes (bike, cart, tram, any new kind), sent at Pepper on its road
--   goose    a goose charging at her            gull   a gull's swoop at a standing Pepper
--   barrel   a rolling barrel of the chase (L.barrels)
-- For each hazard type, three checks (St:hazardHit):
--   carrying the ball: the hit knocks the ball out, no heart is lost, and the ball comes to rest where she can
--     pick it up (not in a wall or the water, within 160 px of where she was hit)
--   without the ball: the hit costs a heart
--   hard mode: the old rule, a heart even with the ball (the goose and the gull still knock it out, the others not)
-- And the lamps (the first checkpoint lamp): lighting it gives back a heart (and a heart pops out), not past the
-- most she can have, and not in hard mode.
-- These steps run last: they move critters, the ball and Pepper about, and nothing runs after them.
local Vc = require("vcam")
local I = require("input")

return function(steps, api, report)
  local function stage() return api.stage() end
  local hard0                                                     -- the level's hard flag, put back at the end
  local add = {}
  local function step(t) add[#add + 1] = t end
  -- T seconds (each test file runs its own step list; every one knows { cond, act, limit }), each(p, s) every frame
  -- SAFETY_SHOTS=1: the first hit while carrying and the lamp's heart are saved, every 2nd frame, to shots_safety/
  local SHOTS, done, shotN = os.getenv("SAFETY_SHOTS"), {}, 0
  if SHOTS then love.filesystem.createDirectory("shots_safety") end
  local function wait(T, each, tag)
    local n = 0
    step({ cond = function(p, s) if each and p then each(p, s) end; n = n + 1
        if SHOTS and tag and not done[tag] and n % 2 == 0 then shotN = shotN + 1; love.graphics.captureScreenshot(("shots_safety/%s_%03d.png"):format(tag, shotN)) end
        if n >= T * 60 then n = 0; if tag then done[tag] = true end; return true end end,
      act = function() end, limit = T + 5 })
  end

  -- a spot where Pepper can stand at x in [x0, x1] (every 8 px): the top floor there, or with roadY only that floor;
  -- not a mover, a loose tile, a crumbling plank, a vent hood or a springy top, not in the water, room for her body
  local function spot(s, x0, x1, road)
    local w = s.world
    for x = math.floor(x0), math.floor(x1), 8 do
      local fy, on
      if road then
        local gy = road(x)
        if gy then fy, on = w:floor(x - 6, x + 6, x, gy - 30, gy + 0.5, gy - 30); if fy ~= gy then fy = nil end end
      else fy, on = w:floor(x - 6, x + 6, x, -1e9, w.height, -1e9) end
      local moving = false
      for _, m in ipairs(s.movers) do if on == m then moving = true end end
      if fy and not moving and not (on and (on.loose or on.crumble or on.vent or on.bounce)) and fy < w.height - 4
        and not w:inWater(x, fy - 2) and not w:solidIn(x - 14, x + 14, fy - 30, fy - 1) then return x, fy end
    end
  end

  -- Pepper standing at (x, y), fresh: 3 hearts, no traffic, no fall or splash pending, the camera on her
  local function place(x, y, carrying)
    local s = stage(); local p, b = s.pepper, s.ball
    I.force = {}
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln, p.face = x, y, 0, 0, true, nil, "normal", false, 0, 1
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); Vc.snap(s)
    s.bikes, s.bikeT = {}, 99
    local zones = s.def.bikes; if zones.zoneX0 then zones = { zones } end
    for _, bk in ipairs(zones) do s.zoneIn[bk] = true end         -- (no "enter" zone sends one now)
    s.hearts, s.deadT, s.drownT, s.fallT, s.clearT = 3, nil, nil, nil, nil
    s.events = {}; api.setState("play")                           -- (the level may have been cleared before)
    b.knock, b.on, b.drop = nil, nil, nil
    if carrying then b.state = "carried"; p.carrying = b; b.x, b.y = p:mouthPos()
    else p.carrying = nil; b.state = "rest"; b.x, b.y = b.home.x, b.home.y end
    if s.chase then s.chase.hold = true end                        -- (the chase: the scroll waits)
    s.hitX = x
  end

  -- one hazard type: setup(case) puts Pepper somewhere and sends the hazard at her; drops: hard mode knocked
  -- the ball out before (goose, gull)
  local function hazard(name, setup, drops, each)
    step({ act = function() local s = stage(); if hard0 == nil then hard0 = s.hard or false end; s.hard = nil; setup(true) end })
    wait(2.2, each, "hit_" .. name)
    step({ act = function(p, s)
      local b = s.ball
      local reach = b.state == "rest" and not s:ballLost() and math.abs(b.x - s.hitX) < 160
      report(("safety: %s hit carrying: ball out, no heart"):format(name), s.hearts == 3 and not p.carrying and reach and (s.ballKnocks or 0) > 0,
        ("hearts %d, carrying %s, ball %s x %.0f (hit at %.0f)"):format(s.hearts, tostring(p.carrying ~= nil), b.state, b.x, s.hitX))
      s.ballKnocks = 0; setup(false) end })
    wait(2.0, each)
    step({ act = function(p, s)
      report(("safety: %s hit without the ball: a heart"):format(name), s.hearts == 2, ("hearts %d"):format(s.hearts))
      setup(true); s.hard = true end })
    wait(2.0, each)
    step({ act = function(p, s)
      local ok = s.hearts == 2 and (drops and p.carrying == nil or not drops and p.carrying ~= nil) and (s.ballKnocks or 0) == 0
      report(("safety: %s hit in hard mode: a heart (as before)"):format(name), ok,
        ("hearts %d, carrying %s"):format(s.hearts, tostring(p.carrying ~= nil)))
      s.hard = nil end })
  end

  local s0 = stage()
  local def = s0.def
  -- traffic: one check per kind of vehicle (the first zone of that kind)
  local zones = def.bikes; if zones.zoneX0 then zones = { zones } end
  local seen = {}
  for _, bk in ipairs(zones) do
    local kind = bk.kind or "bike"
    if not seen[kind] then
      seen[kind] = true
      hazard(kind, function(carrying)
        local s = stage(); local w = s.world
        local road = function(x) if bk.rail then return bk.roadY or 184 end; return w:groundAt(x, bk.roadY and bk.roadY - 34) end
        local x, y = spot(s, math.max(bk.zoneX0, (bk.endX or 0) + 120), bk.zoneX1 - 80, road)
        place(x or bk.zoneX0 + 100, y or bk.roadY or 184, carrying)
        s.bikes = { { x = s.pepper.x + 70, y = y or bk.roadY or 184, warn = 0, zone = bk, speed = bk.speed } }
      end, false)
    end
  end
  -- critters: a goose charging, a gull swooping
  local goose, gull
  for _, k in ipairs(s0.critters or {}) do
    if k.kind == "goose" and not goose then goose = k elseif k.kind == "gull" and not gull then gull = k end
  end
  local function quiet(s, keep)                                     -- the other critters keep away for the check
    for _, k in ipairs(s.critters) do
      if k ~= keep then
        if k.kind == "goose" then k.state, k.t, k.x = "proud", -99, -999 else k.state, k.t, k.timer = "away", -99, 99 end
      end
    end
  end
  if goose then
    hazard("goose", function(carrying)
      local s = stage(); local c = goose.def
      quiet(s, goose)
      place(c.x - 26, c.y, carrying)
      goose.x, goose.y, goose.dir, goose.state, goose.t = c.x, c.y, -1, "charge", 0
    end, true)
  end
  if gull then
    hazard("gull", function(carrying)
      local s = stage(); local c = gull.def
      quiet(s, gull)
      local x, y = spot(s, c.x0 + 40, c.x1 - 40)
      place(x, y, carrying)
      gull.state, gull.t, gull.x, gull.y, gull.tx, gull.ty = "warn", 0.8, x, y - 120, x, y
    end, true)
  end
  -- the chase's barrels
  if def.barrels and def.barrels[1] then
    local bd = def.barrels[1]
    local bx, by
    hazard("barrel", function(carrying)
      local s = stage()
      if not bx then bx, by = spot(s, bd.x + 120, bd.x + 900) end
      place(bx, by, carrying)
      s.rollBarrel = true                                          -- (sent on the next frame, after the chase's resync)
    end, false, function(p, s)                                     -- the chase restacks the barrels ahead when the
      local br = s.chase.barrels[1]                                -- camera jumps (Ch.pre): send it a frame later,
      if s.rollBarrel then                                         -- 40 px behind her, rolling her way
        s.rollBarrel = nil
        br.state, br.x, br.y, br.vx, br.vy, br.lastF, br.t = "roll", p.x - 40, p.y, bd.speed or 30, 0, p.y, 1
      elseif p.mode == "hurt" and br.state == "roll" then br.state = "gone" end   -- (one hit per check)
    end)
  end

  -- lamps: lighting one gives back a heart
  local lamp
  for _, l in ipairs(s0.lamps) do if l.checkpoint then lamp = l; break end end
  if lamp then
    local function atLamp(hearts, hard)
      local s = stage()
      if hard0 == nil then hard0 = s.hard or false end
      quiet(s)
      place(lamp.x + 4, lamp.y, false)
      lamp.lit = false; s.hearts = hearts; s.hard = hard or nil; s.pops = {}
    end
    step({ act = function() atLamp(1) end })
    wait(0.1)
    step({ act = function(p, s)
      report("safety: a lamp gives back a heart (and one pops out)", lamp.lit and s.hearts == 2 and #s.pops == 1, ("hearts %d, pops %d"):format(s.hearts, #s.pops))
      atLamp(3) end })
    wait(0.1)
    step({ act = function(p, s)
      report("safety: a lamp never gives more than 3 hearts", lamp.lit and s.hearts == 3 and #s.pops == 0, ("hearts %d"):format(s.hearts))
      atLamp(1, true) end })
    wait(0.1)
    step({ act = function(p, s)
      report("safety: hard mode: a lamp gives no heart", lamp.lit and s.hearts == 1 and #s.pops == 0, ("hearts %d"):format(s.hearts))
      s.hard = hard0 or nil end })
    if SHOTS then step({ act = function() atLamp(1); stage().hard = hard0 or nil end }); wait(1.4, nil, "lamp") end
  end
  step({ act = function() local s = stage(); if hard0 ~= nil then s.hard = hard0 or nil end; if s.chase then s.chase.hold = nil end end })

  local last = table.remove(steps)                                -- the summary goes back at the end
  for _, st in ipairs(add) do steps[#steps + 1] = st end
  steps[#steps + 1] = last
end
