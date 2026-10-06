-- The checks for Level 1, City Park (love riverwalk --level citypark <flag>). Same flags as tests.lua:
--   --physics   checks every set piece: hop, held jump, log, bench, hedge, stepping stones, duck boat, pond,
--               bin, picnic table, leaf cart, the oak's branches, the runaway ball, slide, climbing frame, the gate
--   --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
--   --test      a screenshot tour of the 6 screens, the ball chase, the debug view and the tally
local I = require("input")
local Pp = require("pepper")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    results[#results + 1] = ok
    print(("%-50s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); s.bikes = {}; s.bikeT = 99
  end
  local function jump(...) hold(...); love.keypressed("space") end           -- press A and keep holding it
  local function landed() return { cond = function(p) return p.onGround and p.mode == "normal" end, act = function() end, limit = 3 } end
  local function prop(name, k)                                                -- the k-th prop with this name
    local i = 0
    for _, pr in ipairs(api.stage().def.props) do if pr.name == name then i = i + 1; if i == (k or 1) then return pr end end end
  end

  local steps
  if mode == "--physics" then
    local minY, startY, airT, hearts, inside
    local function near(a, b) return math.abs(a - b) < 1 end
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      -- 0 the gaps in the map and props: crawl gaps 18 px or more (and less than her standing height)
      { act = function()
          local bench, hedge = prop("BENCH"), prop("HEDGE")
          local g1, g2 = 184 - bench.y1, 184 - hedge.y1
          report("crawl gaps: bench and hedge 18-25 px", g1 >= 18 and g1 < Pp.H_STAND and g2 >= 18 and g2 < Pp.H_STAND, ("bench %d, hedge %d px"):format(g1, g2))
          report("hedge top out of reach from the path", 184 - hedge.y0 > 46 + 12, ("%d px up (reach 58)"):format(184 - hedge.y0))
        end },
      -- 1 held jump and tap hop
      { act = function() tp(260, 184); startY = 184; minY = 184 end }, { wait = 0.2 },
      { act = function() jump("jump") end },
      { during = 1.0, each = function(p) minY = math.min(minY, p.y) end },
      { act = function() release(); report("held jump reaches 46 px", math.abs(startY - minY - 46) <= 1, ("%.1f px"):format(startY - minY)) end },
      { act = function() tp(260, 184); minY = 184 end }, { wait = 0.2 },
      { act = function() jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end },
      { during = 1.0, each = function(p) minY = math.min(minY, p.y) end },
      { act = function() report("tapped jump is a 24 px hop", math.abs(184 - minY - 24) <= 2, ("%.1f px"):format(184 - minY)) end },
      -- 2 the log (16 px): a tapped hop lands on it
      { act = function() tp(136, 184); hold("right") end }, { during = 0.15 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) release(); report("log: a tapped hop lands on it", near(p.y, 168), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 3 the bench: stops a walk, crawl under it, a held jump lands on the seat
      { act = function() tp(300, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) report("bench: stops a walk", p.x < 337, ("x %.0f"):format(p.x)); hold("right", "down") end },
      { during = 4.0 },
      { act = function(p) release(); report("bench: crawling passes under it", p.x > 465 and near(p.y, 184), ("x %.0f"):format(p.x)) end },
      { act = function() tp(290, 184); hold("right") end }, { during = 0.4 },
      { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("bench: a held jump lands on the seat", near(p.y, 156), ("y %.0f"):format(p.y)) end },
      -- 4 the hedge: stops a walk and a held jump from the path, crawling passes; from the bench seat a running
      --   held jump reaches its top (the gold bone)
      { act = function() tp(470, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) report("hedge: stops a walk", p.x < 512, ("x %.0f"):format(p.x)); jump("right", "jump") end },
      { during = 0.3 }, landed(),
      { act = function(p) report("hedge: a held jump from the path does not get over", p.x < 512 and near(p.y, 184), ("x %.0f y %.0f"):format(p.x, p.y)); hold("right", "down") end },
      { during = 3.5 },
      { act = function(p) release(); report("hedge: crawling passes through the gap", p.x > 610 and near(p.y, 184), ("x %.0f"):format(p.x)) end },
      { act = function() tp(420, 156); hold("right") end }, { during = 0.3 },
      { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("hedge: a running jump from the seat reaches the top", near(p.y, 112), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 5 the pond: walk onto the first stone, hop to the second, walk onto the duck boat, ride it, hop up the bank
      { act = function() tp(690, 184); hold("right") end },
      { cond = function(p) return p.x > 740 or p.mode ~= "normal" end, act = function() release() end, limit = 3 }, { during = 0.4 },
      { act = function(p) report("pond: walk off the bank onto the first stone", near(p.y, 188) and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(752, 188); hold("right") end },
      { cond = function(p) return p.x >= 766 end, act = function() jump("right", "jump") end, limit = 2 }, { wait = 1 / 60 },
      { act = function() hold("right") end },
      { cond = function(p) return p.x >= 816 or p.mode ~= "normal" end, act = function() release() end, limit = 3 }, { during = 0.5 },
      { act = function(p) report("pond: hop from stone to stone", near(p.y, 188) and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() local m = api.stage().movers[1]; m.x0, m.x1, m.dir = m.from, m.from + 48, 1; tp(822, 188); hold("right") end },
      { during = 0.5 }, { act = function() release() end }, { during = 0.3 },
      { act = function(p) local m = api.stage().movers[1]; report("pond: walk off the stone onto the duck boat", p.ground == m, ("y %.0f, on it: %s"):format(p.y, tostring(p.ground == m))) end },
      { during = 1.0 },
      { act = function(p) local m = api.stage().movers[1]; report("pond: the duck boat carries Pepper", p.ground == m and math.abs(p.x - (m.x0 + m.x1) / 2) < 14, ("x %.0f boat %.0f-%.0f"):format(p.x, m.x0, m.x1)) end },
      { act = function() local m = api.stage().movers[1]; m.x0, m.x1, m.dir = m.to, m.to + 48, -1; tp(m.x0 + 30, 202); hold("right") end },
      { during = 0.05 }, { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("pond: a jump from the boat up the far bank", near(p.y, 184) and p.x > 944, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(786, 188); hearts = api.stage().hearts end }, { during = 2.5 },
      { act = function() local s = api.stage(); report("pond: falling in costs a heart", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      -- 6 the bin (56 px): a held jump and a scramble
      { act = function() tp(980, 184); jump("right", "jump") end }, { during = 0.3 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 2 },
      { act = function(p) release(); report("bin: jump and scramble on top", near(p.y, 128), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 7 the leaf cart: it hurts on the path, the picnic table is above it, a running jump clears it
      { act = function() tp(1210, 184); local s = api.stage(); hearts = s.hearts; s.bikes = { { x = 1300, y = 184, warn = 0, zone = s.def.bikes[1] } } end },
      { during = 2.0 },
      { act = function() local s = api.stage(); report("leaf cart: hurts Pepper on the path", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { act = function() tp(1070, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); local s = api.stage(); hearts = s.hearts
          report("picnic table: a held jump lands on top", near(p.y, 156), ("x %.0f y %.0f"):format(p.x, p.y))
          s.bikes = { { x = p.x + 90, y = 184, warn = 0, zone = s.def.bikes[1] } }; s.bikeT = 99 end },
      { during = 2.0 },
      { act = function(p) local s = api.stage(); report("picnic table: safe from the leaf cart", near(p.y, 156) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts)) end },
      { act = function() tp(1190, 184); local s = api.stage(); hearts = s.hearts; s.bikes = { { x = 1330, y = 184, warn = 0, zone = s.def.bikes[1] } }; hold("right") end },
      { cond = function(p, s) return s.bikes[1] and s.bikes[1].x - p.x < 92 end, act = function() jump("right", "jump") end, limit = 2 },
      { during = 1.2 },
      { act = function() local s = api.stage(); release(); report("leaf cart: a running jump clears it", s.hearts == hearts, ("hearts %d"):format(s.hearts)) end },
      -- 8 the oak: held jumps from branch to branch up to the top
      { act = function() tp(1446, 184); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("oak: path to the low branch", near(p.y, 156), ("y %.0f"):format(p.y)) end },
      { act = function() tp(1470, 156); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("oak: low branch to the middle branch", near(p.y, 128), ("y %.0f"):format(p.y)) end },
      { act = function() tp(1460, 128); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("oak: middle branch to the top branch", near(p.y, 100), ("y %.0f"):format(p.y)) end },
      -- the runaway ball: it hops on when Pepper comes near, waits for her, and leaves the park at the end
      { act = function() local s = api.stage(); local b, run = s.ball, s.def.ballRun
          b.state, b.wp, b.hop, b.x, b.y = "run", 2, nil, run[2].x, run[2].y; tp(run[2].x - 200, 184) end }, { wait = 0.3 },
      { act = function() local b = api.stage().ball; report("ball: it waits while Pepper is far", b.wp == 2 and not b.hop, ("wp %d"):format(b.wp)); tp(b.x - 60, 184) end },
      { wait = 0.1 },
      { act = function() local b = api.stage().ball; report("ball: it hops on when Pepper comes near", b.wp == 3 and b.hop ~= nil, ("wp %d"):format(b.wp)); tp(140, 184) end },
      { wait = 2.0 },
      { act = function() local s = api.stage(); local b, run = s.ball, s.def.ballRun
          report("ball: it lands on the next point", not b.hop and near(b.x, run[3].x) and near(b.y, run[3].y), ("x %.0f y %.0f"):format(b.x, b.y))
          b.wp, b.x, b.y = #run - 1, run[#run - 1].x, run[#run - 1].y; tp(b.x - 60, 184) end },
      { wait = 2.0 },
      { act = function() local b = api.stage().ball; report("ball: it leaves the park after the last point", b.state == "gone", b.state) end },
      -- 9 the playground: up the slide tower, down the slide on the ground, the climbing frame's bars
      { act = function() tp(1630, 184); jump("right", "jump") end }, { during = 0.3 }, landed(),
      { act = function(p) release(); report("slide: a held jump onto the tower", near(p.y, 152), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1680, 152); airT = 0; hold("right") end },
      { during = 0.6, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("slide: down the slide on the ground", airT < 0.05 and near(p.y, 184) and p.x > 1728, ("air %.2f s, x %.0f y %.0f"):format(airT, p.x, p.y)) end },
      -- (a knock-back that does not lift her: her jump base is set so the short-hop rule cancels the bounce,
      --  as happened in a QA fuzz run)
      { act = function(p) tp(1698.1, 154.1); local s = api.stage(); s.pepper:hurt(s.pepper.x + 10, s.world); s.pepper.jumpBase = s.pepper.y + 30; inside = false end },
      { during = 1.5, each = function(p)                                                     -- the QA rule (qa.lua)
          local w = api.stage().world
          local r = w:solidIn(p.x - 12.5, p.x + 12.5, p.y - p:height() + 1.5, p.y - w.STEP - 0.5)
          if r and r.terrain and w:slopeNear(p.x - Pp.HW, p.x + Pp.HW) then r = nil end
          if p.x > 1664 and p.x < 1696 and p.y > 152.5 and p.y < 183.5 then r = true end      -- in the tower, under its top
          if r then inside = ("x %.1f y %.1f"):format(p.x, p.y) end
        end },
      { act = function(p) report("slide: knocked back off its top, not into the tower", not inside, inside or ("ends x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1776, 184); jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end }, { during = 0.1 }, landed(),
      { act = function(p) report("climbing frame: a hop onto the low bar", near(p.y, 160), ("y %.0f"):format(p.y)) end },
      { act = function() tp(1784, 160); jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end }, { during = 0.1 }, landed(),
      { act = function(p) report("climbing frame: a hop onto the top bar", near(p.y, 136), ("y %.0f"):format(p.y)) end },
      -- 10 out through the far gate
      { act = function() tp(1850, 184); hold("right") end }, { wait = 3.0 },
      { act = function() release(); report("gate: reaching it clears the level", api.getState() == "clear", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec")
    local function at(cond, act, limit) return { cond = cond, act = act, limit = limit or 6 } end
    steps = {
      { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 },
      at(function() return true end, function() hold("right") end),
      -- 1 the gate: through the leaves, a hop onto the log
      at(function(p) return p.x >= 146 end, function() jump("right", "jump") end),
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      -- 2 a held jump onto the bench, then crawl under the hedge
      at(function(p) return p.x >= 300 and p.onGround and p.y > 183 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() hold("right") end),
      at(function(p) return p.x >= 490 and p.onGround and p.y > 183 end, function() hold("right", "down") end),
      at(function(p) return p.x >= 612 end, function() hold("right") end, 9),
      -- 3 the pond: onto the first stone, a hop to the second, wait for the duck boat, ride it, up the bank
      at(function(p) return p.onGround and p.y >= 187 and p.x > 735 end, function() hold("right") end),
      at(function(p) return p.x >= 766 end, function() jump("right", "jump") end),             -- a tapped hop
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.x >= 794 end, function() release() end),                          -- brake in the air
      at(function(p) return p.onGround and p.x >= 800 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 <= 842 and s.movers[1].dir < 0 or s.movers[1].x0 <= 841 end, function() hold("right") end, 9),
      at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 26 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 >= 884 end, function() jump("right", "jump") end, 9),
      at(function(p) return p.onGround and p.y <= 185 and p.x > 944 end, function() hold("right") end),
      -- 4 the bin (jump + scramble), the picnic table, wait there for the leaf cart to pass
      at(function(p) return p.x >= 984 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 129 end, function() hold("right") end),
      at(function(p) return p.x >= 1030 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 and p.x > 1100 end, function() release() end),
      at(function(p) return p.x >= 1124 or p.vx < 1 end, function() release() end),
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 40 end, function() hold("right") end, 12),
      -- 5 the oak: up the branches to the top (gold bone), then off the branches to the right
      at(function(p) return p.x >= 1446 end, function() jump("jump") end, 9),
      at(function(p) return p.onGround and p.y <= 157 end, function() release() end),
      { wait = 0.15 }, { act = function() jump("jump") end },
      at(function(p) return p.onGround and p.y <= 129 end, function() release() end),
      { wait = 0.15 }, { act = function() jump("jump") end },
      at(function(p) return p.onGround and p.y <= 101 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 1480 end, function() hold("right") end, 9),
      -- 6 the playground: up the slide tower, down the slide, the climbing frame, the girl
      at(function(p) return p.x >= 1628 end, function() jump("right", "jump") end, 9),
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 1728 end, function() hold("right") end),
      at(function(p) return p.x >= 1762 end, function() jump("right", "jump") end),
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.onGround and p.y <= 161 end, function() release() end),
      { wait = 0.3 }, { act = function() jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end },
      at(function(p) return p.onGround and p.y <= 137 end, function() release() end),
      { wait = 0.2 }, { act = function() hold("right") end },
      at(function() return api.getState() == "clear" end, function() release() end, 9),
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, lives %d hearts %d, %.1f s played"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    }
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("cp_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    -- one shot per screen (camera on the screen's left edge), Pepper standing in it
    local spots = { { 60, 184 }, { 476, 184 }, { 820, 188 }, { 1132, 156 }, { 1300, 184 }, { 1640, 184 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      if i == 4 then steps[#steps + 1] = { act = function() local s = api.stage(); s.bikes = { { x = 1250, y = 184, warn = 0, zone = s.def.bikes[1] } }; s.bikeT = 99 end } end
      steps[#steps + 1] = { wait = i == 4 and 0.25 or 0.6 }
      steps[#steps + 1] = shot(("cp_%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    -- the runaway ball: Pepper comes near, it hops on
    steps[#steps + 1] = { act = function() local s = api.stage(); local b, run = s.ball, s.def.ballRun
      b.state, b.wp, b.hop, b.x, b.y = "run", 1, nil, run[1].x, run[1].y; tp(40, 184); s.pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.35 }; steps[#steps + 1] = shot("cp_07_chase", 0)
    steps[#steps + 1] = { wait = 0.35 }; steps[#steps + 1] = shot("cp_08_chase", 0)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("cp_11_debug_screen5", 1280)
    steps[#steps + 1] = { act = function() tp(1700, 160) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("cp_12_debug_screen6", 1600)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }
    -- out through the far gate: the tally
    steps[#steps + 1] = { act = function() tp(1860, 184); I.force = { right = true } end }
    steps[#steps + 1] = { wait = 1.0 }; steps[#steps + 1] = shot("cp_13_gate")
    steps[#steps + 1] = { act = function() I.force = {} end }
    steps[#steps + 1] = { wait = 4.5 }; steps[#steps + 1] = shot("cp_14_tally")
    steps[#steps + 1] = { wait = 0.3 }; steps[#steps + 1] = { act = function() love.event.quit() end }
  end

  local i, since, T, lastHearts = 1, 0, 0, nil
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; T = T + dt; since = since + dt
    old(dt)
    local s = api.stage(); local p = s and s.pepper
    if mode == "--auto" then
      frame = frame + 1
      if s and s.hearts ~= (lastHearts or 3) then print(("  lost a heart at x %.0f y %.0f (step %d)"):format(p.x, p.y, i)) end
      lastHearts = s and s.hearts
      if frame % 3 == 0 then n = n + 1; love.graphics.captureScreenshot(("rec/%04d.png"):format(n)) end
    end
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.during then if st.each and p then st.each(p) end; if since >= st.during then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond(p, s) then
        if os.getenv("AUTO_DEBUG") then print(("step %d at x %.1f y %.1f vx %.0f %s boat %.0f"):format(i, p.x, p.y, p.vx, p.onGround and "G" or "A", s.movers[1] and s.movers[1].x0 or 0)) end
        st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
