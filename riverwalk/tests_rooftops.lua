-- The checks for Rooftops (greybox; love riverwalk --level rooftops <flag>):
--   --physics   the world; every steam puff (its apex is y0 - lift within 1 px, it lands her on the floor it serves
--               when she steers, back on its hood or the floor with no input; the warning comes 0.8 s before the
--               lift; one lift per puff; a bark starts a resting vent at once; the sauna puffs only after a bark;
--               crouching stays put); the loose tiles (a floor for 0.6 s, then not; a bridge of three crossed with
--               hops; back after 3 s, not while she is in its place); every jump on the main route (the cafe table,
--               the walk up the stairwells to the terrace, the finale) and the high road's plain jumps; the gull's
--               nest (a bark drops the ball on the chimney); the fetch ends the level
--   --auto      the main route and the finale on autopilot (frames in rec_rooftops/ every 3rd frame)
--   --test      a screenshot tour, and frames of a puff and a loose tile (rec_rooftops_puff/, rec_rooftops_tile/)
local I = require("input")
local Pp = require("pepper")
local St = require("stage")
local Vc = require("vcam")
local Rf = require("roofs")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-66s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function near(a, b, e) return a and b and math.abs(a - b) <= (e or 0.01) end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); Vc.snap(s)
  end

  -- the simulation stage (no gull over T2: it is checked in play) ---------------------------------------------
  local function fresh()
    local st = St.new(api.stage().def); st.critters = {}
    return st
  end
  local function place(st, x, y)
    local p = st.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    p.carrying, p.dropT, p.bufferT, p.coyoteT = nil, 0, 0, 0
    st.hearts, st.deadT, st.drownT, st.fallT, st.msg = 3, nil, nil, nil, nil
    st.cam = math.max(0, math.min(st.world.width - 320, x - 140)); Vc.snap(st)
    I.force = {}
    for _ = 1, 4 do st:update(1 / 60, {}) end                      -- settle: she finds her floor
  end
  -- plan(p, f, air) -> held buttons, press jump?, press bark?; runs until she lands after being in the air (or
  -- maxT). Returns { x, y, landed, minY, hearts, fell }
  local function run(st, plan, maxT, keepGoing)
    local p, air, minY = st.pepper, false, st.pepper.y
    for f = 1, math.floor((maxT or 4) * 60) do
      local held, jump, bark = plan(p, f, air)
      I.force = held or {}
      st:update(1 / 60, { jump = jump or nil, bark = bark or nil })
      if not p.onGround then air = true end
      minY = math.min(minY, p.y)
      if st.fallT or p.mode == "gone" then I.force = {}; return { x = p.x, y = p.y, fell = true, minY = minY, hearts = st.hearts } end
      if air and p.onGround and p.mode == "normal" and not keepGoing then I.force = {}; return { x = p.x, y = p.y, landed = true, minY = minY, hearts = st.hearts } end
    end
    I.force = {}
    return { x = p.x, y = p.y, landed = p.onGround, minY = minY, hearts = st.hearts }
  end
  local function vent(st, name) for _, v in ipairs(st.vents) do if v.d.name == name then return v end end end
  local function puffNow(v) v.st, v.t = "warn", (v.d.warn or 0.8) - 1 / 60 end   -- its puff starts next frame

  local steps
  if mode == "--physics" then
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      { act = function(p, s)
          report("a tall map: 1920 x 960 px (240 x 120 cells)", s.world.width == 1920 and s.world.height == 960, ("%d x %d"):format(s.world.width, s.world.height))
          report("6 steam vents, 5 loose tiles, the gull's nest, Mia on the terrace", #s.vents == 6 and #s.tiles == 5 and s.def.magpie.look == "gull"
            and s.ball.state == "magpie" and near(s.girl.y, 328), ("%d vents, %d tiles"):format(#s.vents, #s.tiles))
        end },
      -- 1 every vent: apex exact; no input; steering to the floor it serves
      { act = function()
          -- name, no-input landing (y), steer, landing when steering (y), its x range (feet span overlaps)
          local V = {
            { "KITCHEN FAN", 616, nil, 616 },
            { "DORMER VENT", 612, "right", 520, 688, 768 },
            { "LAUNDRY VENT", 452, "right", 360, 1240, 1320 },
            { "CHIMNEY", 356, "right", 232, 1568, 1792 },
            { "TERRACE FAN", 232, nil, 232 },
            { "SAUNA", 228, "right", 136, 1808, 1840 },
          }
          for _, c in ipairs(V) do
            local st = fresh(); local v = vent(st, c[1]); local d = v.d
            local mid = (d.x0 + d.x1) / 2
            place(st, mid, d.y0)
            local onHood = near(st.pepper.y, d.y0)
            puffNow(v)
            local r = run(st, function() return {} end, 4)
            report(("%s: apex y0 - lift = %d (within 1 px)"):format(c[1], Rf.apex(v)), onHood and near(r.minY, Rf.apex(v), 1), ("top %.2f"):format(r.minY))
            report(("%s: no input, she lands on y %d"):format(c[1], c[2]), r.landed and near(r.y, c[2]) and r.hearts == 3, ("y %.1f x %.0f"):format(r.y, r.x))
            if c[3] then
              st = fresh(); v = vent(st, c[1]); place(st, mid, d.y0); puffNow(v)
              r = run(st, function(p, f, air) if air then return { [c[3]] = true } end; return {} end, 4)
              report(("%s: steering %s she lands on the floor it serves (y %d)"):format(c[1], c[3], c[4]),
                r.landed and near(r.y, c[4]) and r.x + 13 > c[5] and r.x - 13 < c[6] and r.hearts == 3, ("y %.1f x %.0f"):format(r.y, r.x))
            end
          end
        end },
      -- 2 the warning comes first; one lift per puff; crouching stays put; a bark; the sauna only on a bark
      { act = function()
          local st = fresh(); local v = vent(st, "KITCHEN FAN"); local d = v.d
          place(st, (d.x0 + d.x1) / 2, d.y0); v.st, v.t = "rest", 0
          local warnAt, liftAt, f = nil, nil, 0
          for i = 1, 60 * 4 do
            st:update(1 / 60, {}); f = i
            if v.st == "warn" and not warnAt then warnAt = i end
            if not st.pepper.onGround and not liftAt then liftAt = i end
            if liftAt then break end
          end
          report("a vent warns (rattle, wisps) 0.8 s before it lifts her", warnAt and liftAt and near((liftAt - warnAt) / 60, 0.8, 2 / 60),
            ("warn at %.2f s, lift at %.2f s"):format((warnAt or 0) / 60, (liftAt or 0) / 60))
          report("the cycle: rest every - warn - puff (3 - 0.8 - 0.9 = 1.3 s)", warnAt and near(warnAt / 60, 1.3, 2 / 60), ("%.2f s"):format((warnAt or 0) / 60))
          -- one lift per puff: put her back on the hood while it still puffs
          st = fresh(); v = vent(st, "KITCHEN FAN"); place(st, (d.x0 + d.x1) / 2, d.y0); puffNow(v)
          st:update(1 / 60, {}); st:update(1 / 60, {})
          local lifted1 = not st.pepper.onGround
          local p = st.pepper; p.y, p.vy, p.onGround, p.ground = d.y0, 0, true, nil
          local again = false
          for i = 1, 20 do st:update(1 / 60, {}); if v.st == "puff" and p.vy < -50 then again = true end end
          report("one lift per puff: back in the column, she is not lifted again", lifted1 and not again and st.puffed == 1, ("%d lifts"):format(st.puffed or 0))
          -- crouching through a puff
          st = fresh(); v = vent(st, "KITCHEN FAN"); place(st, (d.x0 + d.x1) / 2, d.y0); I.force = { down = true }
          for i = 1, 10 do st:update(1 / 60, {}) end
          puffNow(v)
          for i = 1, 70 do st:update(1 / 60, {}) end
          I.force = {}
          report("crouched (Down) on the hood she stays put through a puff", st.pepper.onGround and near(st.pepper.y, d.y0) and not st.puffed, ("y %.1f"):format(st.pepper.y))
          -- a bark starts a resting vent within one frame (her feet within 60 px of its mouth, 80 px across)
          st = fresh(); v = vent(st, "LAUNDRY VENT"); place(st, 1180, 456); v.st, v.t = "rest", 0
          st:update(1 / 60, { bark = true })
          report("a bark near a resting vent starts its warning at once", v.st == "warn", v.st)
          -- the sauna: never by itself; a bark: it puffs and lifts her to the nest chimney
          st = fresh(); v = vent(st, "SAUNA"); d = v.d; place(st, (d.x0 + d.x1) / 2, d.y0)
          local any = false
          for i = 1, 60 * 8 do st:update(1 / 60, {}); if v.st ~= "rest" then any = true end end
          report("the sauna never puffs by itself (8 s)", not any, v.st)
          st:update(1 / 60, { bark = true })
          local r = run(st, function(q, f, air) if air then return { right = true } end; return {} end, 4)
          report("a bark: the sauna puffs and carries her onto the nest chimney (136)", r.landed and near(r.y, 136), ("y %.1f"):format(r.y))
        end },
      -- 3 loose tiles
      { act = function()
          local st = fresh(); local k = st.tiles[1]; local t = k.p
          place(st, (t.x0 + t.x1) / 2, t.y0)
          local on = near(st.pepper.y, t.y0) and st.pepper.ground == t
          local fellAt
          for i = 1, 60 do st:update(1 / 60, {}); if not fellAt and (not st.pepper.onGround or st.pepper.ground ~= t) then fellAt = i end end
          report("a loose tile: a floor for 0.6 s, then she falls through", on and fellAt and near((fellAt + 4) / 60, 0.6, 3 / 60), ("%.2f s"):format(((fellAt or 0) + 4) / 60))
          local r = run(st, function() return {} end, 3)
          report("she lands on the roof below, no harm", r.landed and r.hearts == 3 and r.y > t.y0, ("y %.0f"):format(r.y))
          -- not back while she is in its place; back after 3 s once she is out of it
          local p = st.pepper
          for i = 1, 60 * 3.5 do p.x, p.y, p.vy, p.onGround = (t.x0 + t.x1) / 2, t.y0 + 10, 0, true; st:update(1 / 60, {}) end
          local stillGone = k.st == "gone"
          place(st, t.x0 - 120, 712)
          st:update(1 / 60, {})
          local back = false; for _, r2 in ipairs(st.world.rects) do if r2 == t then back = true end end
          report("it does not come back while she is in its place", stillGone, k.st)
          report("it is back after 3 s once she is out of the way", k.st == "idle" and back, k.st)
          -- the bridge of three (x 800, 856, 912 at y 520): walking, a tap hop on each, from the ledge to the gable
          st = fresh(); place(st, 700, 520)
          local low = 0
          r = run(st, function(q, f, air)                            -- running, a tap hop each time she lands
              if q.y > low then low = q.y end
              if q.x >= 968 then return {} end
              return { right = true }, q.onGround and q.x >= 752
            end, 5, true)
          report("running, a tap hop on each tile crosses the bridge of three to the gable", st.pepper.x >= 960 and near(st.pepper.y, 520) and low <= 521 and st.hearts == 3,
            ("x %.0f y %.0f, lowest %.0f"):format(st.pepper.x, st.pepper.y, low))
        end },
      -- 4 the main route: the cafe table, the stairwells, the terrace; the high road's plain jumps
      { act = function()
          local st = fresh(); place(st, 70, 904)
          local r = run(st, function(q, f) return { right = true }, f == 1 end, 3)
          report("street: a running jump onto the cafe table (y 880)", r.landed and near(r.y, 880), ("y %.1f x %.0f"):format(r.y, r.x))
          st = fresh(); place(st, 70, 904)
          r = run(st, function(q) return { right = true, down = true } end, 3, true)
          report("street: or crawl under it", st.pepper.x > 150 and near(st.pepper.y, 904), ("x %.0f"):format(st.pepper.x))
          -- the walk up: street to the roof terrace, holding right, no jump
          st = fresh(); place(st, 150, 904)
          local maxDrop, last = 0, st.pepper.y
          r = run(st, function(q) maxDrop = math.max(maxDrop, q.y - last); last = q.y; return { right = true } end, 30, true)
          local p = st.pepper
          for _ = 1, 600 do if p.x >= 1700 then break end; I.force = { right = true }; st:update(1 / 60, {}) end
          I.force = {}
          report("the low road: street to the roof terrace, walking and stairs only", p.x >= 1700 and near(p.y, 328) and st.hearts == 3,
            ("x %.0f y %.0f"):format(p.x, p.y))
          -- the high road's plain jumps
          local J = {
            { "gable (520) -> ledge 488: held jump right", 1030, 520, "right", 488 },
            { "ledge 488 -> ledge 456: held jump right", 1126, 488, "right", 456 },
            { "ledge 360 -> chimney pot (312): held jump and scramble", 1460, 360, "right", 312 },
            { "nest chimney -> step off left onto the sauna's hood (228)", 1812, 136, "left", 228, true },
          }
          for _, j in ipairs(J) do
            st = fresh(); place(st, j[2], j[3])
            r = run(st, function(q, f) if j[6] then return { [j[4]] = true, walk = true } end; return { [j[4]] = true, jump = f < 40 }, f == 1 end, 3)
            report(j[1], r.landed and near(r.y, j[5]) and r.hearts == 3, ("y %.1f x %.0f"):format(r.y, r.x))
          end
          st = fresh(); place(st, 1750, 232)
          r = run(st, function(q, f) if f < 4 then return { down = true }, f == 2 end; return {} end, 3)
          report("copper roof -> Down + A -> the roof terrace (328)", r.landed and near(r.y, 328), ("y %.1f"):format(r.y))
        end },
      -- 5 the gull's nest and the fetch
      { act = function(p, s) tp(1778, 228); p.face = 1 end }, { wait = 0.3 },
      { act = function() love.keypressed("z") end }, { wait = 1.2 },
      { act = function(p, s)
          report("a bark from the copper roof: the gull lets go, the ball lands on the chimney", s.ball.state == "rest" and near(s.ball.y, 136) and s.magpie.state ~= "perch",
            ("ball %s y %.0f"):format(s.ball.state, s.ball.y)) end },
      { act = function(p, s) tp(s.ball.x + 18, 136); p.face = -1 end }, { wait = 0.3 },
      { act = function() love.keypressed("x") end }, { wait = 0.5 },
      { act = function(p) report("on the chimney Pepper picks the ball up", p.carrying ~= nil) end },
      { act = function(p, s) tp(1740, 328); p.face = -1 end }, { wait = 0.2 },
      { act = function() love.keypressed("x") end }, { wait = 0.4 },
      { act = function(p, s) report("giving the ball to Mia on the terrace: GOOD GIRL (FETCH 2000)", s.ball.state == "given" and s.bonus and s.bonus[2] == 2000, s.ball.state) end },
      { wait = 2.6 },
      { act = function(p, s) report("the fetch ends the level", s.events.clear == true or api.getState() ~= "play", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec_rooftops")
    local function at(cond, act, limit) return { cond = cond, act = act or function() end, limit = limit or 8 } end
    local function settle() return at(function(p) return p.onGround and math.abs(p.vx) < 1 end, function() release() end, 3) end
    local function runTo(x, ...)
      local extra = { ... }
      return at(function(p) if p.x >= x then return true end; local h = { right = true }; for _, k in ipairs(extra) do h[k] = true end; I.force = h; return false end,
        function() release() end, 25)
    end
    local function goTo(x)
      return at(function(p) if math.abs(p.x - x) < 3 then release(); return math.abs(p.vx) < 1 end
          I.force = { [p.x < x and "right" or "left"] = true, walk = true }; return false end, function() release() end, 8)
    end
    local function vent(s, name) for _, v in ipairs(s.vents) do if v.d.name == name then return v end end end
    steps = { { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      runTo(76),
      { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.4 }, { act = function() hold("right") end },   -- the cafe table
      runTo(1660), settle(),                                                    -- up the stairwells to the terrace
      goTo(1692),                                                               -- onto the terrace fan
      at(function(p, s) return vent(s, "TERRACE FAN").st == "puff" or not p.onGround end, nil, 6),
      at(function(p) return p.onGround and p.y < 300 end, function() release() end, 4), settle(),   -- the copper roof
      goTo(1778), { act = function(p) p.face = 1; love.keypressed("z") end },    -- bark: the gull lets go, the sauna steams
      at(function(p, s) return not p.onGround end, function() hold("right") end, 4),
      at(function(p) return p.onGround and p.y < 200 end, function() release() end, 4), settle(),
      goTo(1812), { act = function(p) p.face = 1 end },
      at(function(p, s) return s.ball.state == "rest" end, function() love.keypressed("x") end, 4), { wait = 0.6 },
      { act = function() hold("left", "walk") end },                            -- step off onto the copper roof
      at(function(p) return p.onGround and p.y > 200 end, function() release() end, 4), settle(),
      goTo(1752), { act = function() hold("down"); love.keypressed("space") end }, { wait = 0.2 }, { act = function() release() end },
      at(function(p) return p.onGround and p.y > 300 end, function() release() end, 4), settle(),
      goTo(1752), { act = function(p) p.face = -1; love.keypressed("x") end },
      { wait = 6 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets, st.secretsTotal, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    }
  else  -- --test: a screenshot tour; frames of a puff and of a loose tile
    local rec
    local function shot(name) return { act = function() love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("rt_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    local spots = { { 60, 904 }, { 400, 800 }, { 560, 712 }, { 640, 616 }, { 860, 520 }, { 1100, 488 }, { 1300, 520 },
      { 1280, 360 }, { 1500, 312 }, { 1660, 328 }, { 1650, 232 }, { 1824, 136 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.25 }
      steps[#steps + 1] = shot(("rt_%02d_spot"):format(i))
    end
    for _, st in ipairs({
      { act = function(p, s) love.filesystem.createDirectory("rec_rooftops_puff"); tp(632, 708); s.vents[1].st, s.vents[1].t = "rest", 0.8; rec = { dir = "rec_rooftops_puff", n = 0 } end },
      { wait = 3.2 }, { act = function() rec = nil end },
      { act = function(p, s) love.filesystem.createDirectory("rec_rooftops_tile"); tp(812, 520); rec = { dir = "rec_rooftops_tile", n = 0 } end },
      { wait = 2.0 }, { act = function() rec = nil end },
      { act = function() love.event.quit() end },
    }) do steps[#steps + 1] = st end
    local old = love.update
    local f = 0
    api.recHook = function() if rec then f = f + 1; if f % 2 == 0 then rec.n = rec.n + 1; love.graphics.captureScreenshot(("%s/%04d.png"):format(rec.dir, rec.n)) end end end
  end

  local i, since, frame, n, lastHearts = 1, 0, 0, 0, nil
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; since = since + dt
    old(dt)
    local s = api.stage(); local p = s and s.pepper
    if api.recHook then api.recHook() end
    if mode == "--auto" then
      frame = frame + 1
      if s and s.hearts ~= (lastHearts or s.maxHearts) then print(("  lost a heart at x %.0f y %.0f (step %d)"):format(p.x, p.y, i)) end
      lastHearts = s and s.hearts
      if os.getenv("AUTO_TRACE") and frame % 10 == 0 then print(("F %d x %.0f y %.0f step %d"):format(frame, p.x, p.y, i)) end
      if frame % 3 == 0 and not os.getenv("NO_REC") then n = n + 1; love.graphics.captureScreenshot(("rec_rooftops/%04d.png"):format(n)) end
    end
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond(p, s) then st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
