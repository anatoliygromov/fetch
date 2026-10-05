-- love . --physics   checks jump heights, crawl gaps, bench, bin, flower box, scramble, stairs, pontoon; prints PASS / FAIL
-- love . --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
-- love . --test      a screenshot tour of every screen, the debug view and the tuning panel
local I = require("input")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    results[#results + 1] = ok
    print(("%-46s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); s.bikes = {}; s.bikeT = 99
  end

  local steps
  if mode == "--physics" then
    local minY, startY, maxX, airT
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end },      -- leave the intro
      { wait = 0.3 },
      -- 1 held jump
      { act = function() tp(640, 184); startY = 184; minY = 184 end }, { wait = 0.2 },
      { act = function() hold("jump"); love.keypressed("space") end },
      { during = 1.0, each = function(p) minY = math.min(minY, p.y) end },
      { act = function() release(); report("held jump reaches 46 px", math.abs(startY - minY - 46) <= 1, ("%.1f px"):format(startY - minY)) end },
      -- 2 tap
      { act = function() tp(640, 184); minY = 184 end }, { wait = 0.2 },
      { act = function() hold("jump"); love.keypressed("space") end }, { wait = 1 / 60 },
      { act = function() release() end },
      { during = 1.0, each = function(p) minY = math.min(minY, p.y) end },
      { act = function() report("tapped jump is a 24 px hop", math.abs(184 - minY - 24) <= 2, ("%.1f px"):format(184 - minY)) end },
      -- 3 standing Pepper cannot pass under the bridge pier (24 px gap), crawling Pepper can
      { act = function() tp(1250, 216); hold("right") end },
      { during = 2.0 },
      { act = function(p) report("standing: blocked at the bridge pier", p.x < 1290, ("x %.0f"):format(p.x)); hold("right", "down") end },
      { during = 6.0 },
      { act = function(p) report("crawling: passes under the bridge pier", p.x > 1458, ("x %.0f"):format(p.x)); release() end },
      -- 4 the bench (seat y 156-165, 28 px above the walking line, 19 px clear under it): it stops a walk,
      --   crawling passes under it, a held jump lands on the seat, and she walks off the far end
      { act = function() tp(60, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) report("walking: stopped by the bench", p.x < 82, ("x %.0f"):format(p.x)); hold("right", "down") end },
      { during = 6.0 },
      { act = function(p) release(); report("crawling: passes under the bench", p.x > 215 and math.abs(p.y - 184) < 1, ("x %.0f"):format(p.x)) end },
      { act = function() tp(60, 184); hold("right") end }, { during = 0.5 },
      { act = function() hold("right", "jump"); love.keypressed("space") end },
      { during = 0.2 },
      { cond = function(p) return p.onGround end, act = function() end, limit = 2 },
      { act = function(p) release(); report("a held jump lands on the bench seat", math.abs(p.y - 156) < 1, ("y %.0f"):format(p.y)); hold("right") end },
      { during = 1.2 },
      { act = function(p) release(); report("walks off the seat to the pavement", p.x > 215 and math.abs(p.y - 184) < 1, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 4b the bin (top 56 px up, as high as the cabin roof): from the pavement a held jump and a scramble
      { act = function() tp(228, 184); hold("right", "jump"); love.keypressed("space") end },
      { during = 0.3 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 2 },
      { act = function(p) release(); report("bin: scramble from the pavement on top", math.abs(p.y - 128) < 1 and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 5 scramble onto the cabin roof (56 px above the deck)
      { act = function() tp(1000, 206); hold("right", "jump"); love.keypressed("space") end },
      { during = 1.2 },
      { act = function(p) release(); report("scramble: deck to cabin roof", math.abs(p.y - 150) < 1 and p.onGround, ("y %.0f"):format(p.y)) end },
      -- 6 stairs down without leaving the ground
      { act = function() tp(660, 184); airT = 0; hold("right") end },
      { during = 0.75, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("stairs down stay on the ground", airT < 0.05 and math.abs(p.y - 216) < 1, ("air %.2f s, y %.0f"):format(airT, p.y)) end },
      -- 7 stairs up
      { act = function() tp(1495, 216); airT = 0; hold("right") end },
      { during = 0.8, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("stairs up stay on the ground", airT < 0.05 and math.abs(p.y - 184) < 1, ("air %.2f s, y %.0f"):format(airT, p.y)) end },
      -- 8 the low flower box on screen 2: it stops a walk, a held jump lands on top (above the bikes)
      { act = function() tp(498, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) hold("right", "jump"); love.keypressed("space") end }, { during = 1.0 },
      { act = function(p) release(); report("flower box: a held jump lands on top", math.abs(p.y - 157) < 1 and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 9 the pontoon carries Pepper
      { act = function() local s = api.stage(); local m = s.movers[1]; tp((m.x0 + m.x1) / 2, m.y0); maxX = m.x0 end },
      { during = 1.0 },
      { act = function(p) local m = api.stage().movers[1]
          report("the pontoon carries Pepper", p.ground == m and math.abs(p.x - (m.x0 + m.x1) / 2) < 2, ("on it: %s"):format(tostring(p.ground == m))) end },
      -- 10 water costs a heart
      { act = function() tp(1160, 216) end },
      { during = 2.5 },
      { act = function() local s = api.stage(); report("falling in the river costs a heart", s.hearts == 2, ("hearts %d"):format(s.hearts)) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec")
    local function at(cond, act, limit) return { cond = cond, act = act, limit = limit or 6 } end
    steps = {
      { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 },
      at(function(p) return true end, function() hold("right") end),
      at(function(p) return p.x >= 70 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() hold("right") end),            -- on the bench seat
      at(function(p) return p.x >= 186 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 129 end, function() hold("right") end),            -- on the bin
      at(function(p) return p.x >= 282 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 153 and p.x > 313 end, function() hold("right") end),     -- on the flower box
      at(function(p) return p.x >= 400 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.x >= 446 end, function() hold("jump") end),                             -- let go of right over the planter
      at(function(p) return p.onGround and p.y <= 155 and p.x > 434 end, function() hold("right") end),     -- on the planter
      at(function(p) return p.x >= 464 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 158 and p.x > 519 end, function() hold("right") end),     -- on the low flower box
      at(function(p) return p.x >= 778 and p.onGround and p.y >= 215 end, function() release() end, 14),
      at(function(p, s) return s.movers[1].x0 <= 802 end, function() hold("right") end, 9),
      at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 18 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 >= 898 end, function() hold("right", "jump"); love.keypressed("space") end, 9),
      at(function(p) return p.onGround and p.y <= 207 and p.x > 960 end, function() hold("right") end),
      at(function(p) return p.x >= 1004 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 151 end, function() release() end),
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.4 },
      at(function(p) return true end, function() hold("right") end),
      at(function(p) return p.x >= 1124 and p.y >= 205 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y >= 215 and p.x > 1170 end, function() hold("right") end),
      at(function(p) return p.x >= 1270 end, function() hold("right", "down") end),
      at(function(p) return p.x >= 1462 end, function() hold("right") end, 9),
      at(function(p) return p.x >= 1598 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 157 and p.x >= 1610 end, function() hold("right") end, 6),   -- on the bench seat
      at(function(p) return p.x >= 1716 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 129 end, function() hold("right") end),            -- on the bin
      at(function(p) return p.x >= 1826 and p.onGround end, function() release() end),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      { wait = 9 }, { act = function() love.event.quit() end },
    }
  else  -- --test
    local function shot(name) return { act = function() love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("title") end }, { wait = 0.2 }, shot("00_title"), { act = function() api.setState("intro") end },
      { wait = 0.6 }, shot("00_intro"), { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    for i, x in ipairs({ 40, 380, 790, 1110, 1430, 1830 }) do
      local y = ({ 184, 152, 216, 206, 216, 184 })[i]
      steps[#steps + 1] = { act = function() tp(x, y) end }
      steps[#steps + 1] = { wait = 0.6 }
      steps[#steps + 1] = shot(("%02d_screen%d"):format(i, i))
    end
    steps[#steps + 1] = { act = function() love.keypressed("g") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("07_debug_screen5")
    steps[#steps + 1] = { act = function() love.keypressed("g"); love.keypressed("tab") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("08_tuning")
    steps[#steps + 1] = { act = function() love.keypressed("tab") end }
    steps[#steps + 1] = { wait = 0.3 }; steps[#steps + 1] = { act = function() love.event.quit() end }
  end

  local i, since, T = 1, 0, 0
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; T = T + dt; since = since + dt
    old(dt)
    if mode == "--auto" then
      frame = frame + 1
      if frame % 3 == 0 then n = n + 1; love.graphics.captureScreenshot(("rec/%04d.png"):format(n)) end
    end
    local s = api.stage(); local p = s and s.pepper
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.during then if st.each and p then st.each(p) end; if since >= st.during then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond(p, s) then st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
