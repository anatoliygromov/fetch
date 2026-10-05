-- love . --physics   checks jump heights, crawl gaps, bench, bin, grit box, ferry, stairs, pontoon; prints PASS / FAIL
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
      { act = function() tp(330, 184); startY = 184; minY = 184 end }, { wait = 0.2 },
      { act = function() hold("jump"); love.keypressed("space") end },
      { during = 1.0, each = function(p) minY = math.min(minY, p.y) end },
      { act = function() release(); report("held jump reaches 46 px", math.abs(startY - minY - 46) <= 1, ("%.1f px"):format(startY - minY)) end },
      -- 2 tap
      { act = function() tp(330, 184); minY = 184 end }, { wait = 0.2 },
      { act = function() hold("jump"); love.keypressed("space") end }, { wait = 1 / 60 },
      { act = function() release() end },
      { during = 1.0, each = function(p) minY = math.min(minY, p.y) end },
      { act = function() report("tapped jump is a 24 px hop", math.abs(184 - minY - 24) <= 2, ("%.1f px"):format(184 - minY)) end },
      -- 3 standing Pepper cannot pass under the bridge pier (24 px gap), crawling Pepper can
      { act = function() tp(1882, 216); hold("right") end },
      { during = 2.0 },
      { act = function(p) report("standing: blocked at the bridge pier", p.x < 1922, ("x %.0f"):format(p.x)); hold("right", "down") end },
      { during = 6.0 },
      { act = function(p) report("crawling: passes under the bridge pier", p.x > 2090, ("x %.0f"):format(p.x)); release() end },
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
      { act = function() tp(616, 184); hold("right", "jump"); love.keypressed("space") end },
      { during = 0.3 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 2 },
      { act = function(p) release(); report("bin: scramble from the pavement on top", math.abs(p.y - 128) < 1 and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 5 the ferry: a hop from the deck to the saloon roof, a held jump up to the wheelhouse roof
      { act = function() tp(1599, 206); hold("right", "jump"); love.keypressed("space") end },
      { during = 0.25 }, { act = function() hold("jump") end },
      { cond = function(p) return p.onGround end, act = function() end, limit = 2 },
      { act = function(p) release(); report("ferry: deck to saloon roof", math.abs(p.y - 184) < 1, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1633, 184); hold("right", "jump"); love.keypressed("space") end },
      { during = 0.25 }, { act = function() hold("jump") end },
      { cond = function(p) return p.onGround end, act = function() end, limit = 2 },
      { act = function(p) release(); report("ferry: saloon roof to wheelhouse roof", math.abs(p.y - 154) < 1, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 6 stairs down without leaving the ground
      { act = function() tp(1260, 184); airT = 0; hold("right") end },
      { during = 0.75, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("stairs down stay on the ground", airT < 0.05 and math.abs(p.y - 216) < 1, ("air %.2f s, y %.0f"):format(airT, p.y)) end },
      -- 7 stairs up
      { act = function() tp(2127, 216); airT = 0; hold("right") end },
      { during = 0.8, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("stairs up stay on the ground", airT < 0.05 and math.abs(p.y - 184) < 1, ("air %.2f s, y %.0f"):format(airT, p.y)) end },
      -- 8 the grit box in bike zone 1: it stops a walk, a held jump lands on top (above the bikes)
      { act = function() tp(804, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) hold("right", "jump"); love.keypressed("space") end }, { during = 1.0 },
      { act = function(p) release(); report("grit box: a held jump lands on top", math.abs(p.y - 152) < 1 and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 8b the flower box in bike zone 2: it stops a walk, a held jump lands on top, high enough to be safe from
      --    a bike riding under her
      { act = function() tp(2414, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) hold("right", "jump"); love.keypressed("space") end }, { during = 0.5 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 2 },
      { act = function(p) local s = api.stage(); s.bikes = { { x = p.x + 90, y = 184, warn = 0, zone = s.def.bikes[2] } }; s.bikeT = 99 end },
      { during = 1.5 },
      { act = function(p) local s = api.stage(); report("bike zone 2: safe from bikes on the flower box", math.abs(p.y - 152) < 1 and p.onGround and s.hearts == 3, ("x %.0f y %.0f hearts %d"):format(p.x, p.y, s.hearts)) end },
      -- 9 the pontoon carries Pepper
      { act = function() local s = api.stage(); local m = s.movers[1]; tp((m.x0 + m.x1) / 2, m.y0); maxX = m.x0 end },
      { during = 1.0 },
      { act = function(p) local m = api.stage().movers[1]
          report("the pontoon carries Pepper", p.ground == m and math.abs(p.x - (m.x0 + m.x1) / 2) < 2, ("on it: %s"):format(tostring(p.ground == m))) end },
      -- 10 water costs a heart
      { act = function() tp(1793, 216) end },
      { during = 2.5 },
      { act = function() local s = api.stage(); report("falling in the river costs a heart", s.hearts == 2, ("hearts %d"):format(s.hearts)) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec")
    local function at(cond, act, limit) return { cond = cond, act = act, limit = limit or 6 } end
    -- onto a box from the pavement (x0 = its left edge, top = its top), or hopping over from the box Pepper stands
    -- on (fromX1 = that box's right edge). While she waits for the landing it retries: a bike may knock her off,
    -- or she may respawn at a lamp post behind it.
    local function onto(x0, top, fromX1)
      return at(function(p)
        if p.onGround and p.mode == "normal" and p.x < x0 - 10 then
          local blocked = I.force.right and math.abs(p.vx) < 1          -- stopped by a box on the way (after a respawn)
          if (p.y > 183 and (p.x >= x0 - 46 or blocked)) or (fromX1 and p.y < 183 and p.x >= fromX1 - 12) then
            hold("right", "jump"); love.keypressed("space")
          else hold("right") end
        end
        return p.onGround and math.abs(p.y - top) < 1 and p.x > x0 - 13
      end, function() hold("right") end, 12)
    end
    steps = {
      { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 },
      at(function(p) return true end, function() hold("right") end),
      at(function(p) return p.x >= 70 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() hold("right") end),            -- on the bench seat
      onto(401, 152),                                                                                -- the flower box
      onto(641, 128),                                                                                -- the bin: jump and scramble
      -- bike zone 1: grit box, planter, flower box; the perches keep her above the bikes
      onto(831, 152), onto(990, 154, 917), onto(1113, 152, 1034),
      -- down the steps to the quay, then the pontoon
      at(function(p) return p.x >= 1378 and p.onGround and p.y >= 215 end, function() release() end, 14),
      at(function(p, s) return s.movers[1].x0 <= 1402 end, function() hold("right") end, 9),
      at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 18 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 >= 1498 end, function() hold("right", "jump"); love.keypressed("space") end, 9),
      at(function(p) return p.onGround and p.y <= 207 and p.x > 1560 end, function() hold("right") end),     -- on the ferry deck
      at(function(p) return p.x >= 1598 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 185 end, function() hold("right") end),            -- on the saloon roof
      at(function(p) return p.x >= 1630 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.x >= 1655 end, function() hold("jump") end),
      at(function(p) return p.onGround and p.y <= 155 end, function() release() end),             -- on the wheelhouse roof
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.4 },
      at(function(p) return p.carrying ~= nil end, function() hold("right") end, 2),
      at(function(p) return p.x >= 1757 and p.y >= 205 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y >= 215 and p.x > 1802 end, function() hold("right") end),   -- the far quay
      at(function(p) return p.x >= 1902 end, function() hold("right", "down") end),                       -- crawl under the pier
      at(function(p) return p.x >= 2094 end, function() hold("right") end, 9),
      at(function(p) return p.x >= 2200 and p.y <= 185 end, function() hold("right") end, 9),           -- up the steps
      onto(2290, 154),                                                                               -- the planter
      -- bike zone 2: flower box, grit box, bin
      onto(2441, 152), onto(2616, 152, 2543), onto(2776, 128, 2702),
      onto(2908, 156),                                                                               -- the last bench
      at(function(p) return p.x >= 3100 and p.onGround end, function() release() end, 9),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      { wait = 9 }, { act = function() love.event.quit() end },
    }
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("title") end }, { wait = 0.2 }, shot("00_title"), { act = function() api.setState("intro") end },
      { wait = 0.6 }, shot("00_intro"), { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    -- one shot per screen (camera on the screen's left edge), Pepper standing on open ground in it
    local spots = { { 40, 184 }, { 480, 152 }, { 760, 184 }, { 1074, 184 }, { 1350, 216 },
                    { 1680, 154 }, { 2110, 216 }, { 2370, 184 }, { 2660, 152 }, { 3080, 184 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.6 }
      steps[#steps + 1] = shot(("%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    steps[#steps + 1] = { act = function() love.keypressed("g") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("11_debug_screen10", 2880)
    steps[#steps + 1] = { act = function() tp(1680, 154) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("12_debug_screen6", 1600)
    steps[#steps + 1] = { act = function() love.keypressed("g"); love.keypressed("tab") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("13_tuning")
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
