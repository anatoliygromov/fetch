-- love . --physics   checks jump heights, crawl gaps, bench, bin, grit box, ferry, stairs, pontoon; prints PASS / FAIL
-- love . --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
-- love . --auto --trace   the same run, printing Pepper's position, speed, clip and frame every step instead
-- love . --test      a screenshot tour of every screen, the debug view and the tuning panel
local I = require("input")
local Sp = require("setpieces")
return function(mode, api)
  I.testing = true
  for _, a in ipairs(arg or {}) do if a == "--trace" then TRACE = true end end
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false                                     -- (a nil result must count as a failure)
    results[#results + 1] = ok
    print(("%-46s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function jump(...) hold(...); love.keypressed("space") end           -- press A and keep holding it
  local function landed() return { cond = function(p) return p.onGround and p.mode == "normal" end, act = function() end, limit = 3 } end
  local function near(a, b) return math.abs(a - b) < 1 end
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
      { act = function() tp(2767, 216); airT = 0; hold("right") end },
      { during = 0.8, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("stairs up stay on the ground", airT < 0.05 and math.abs(p.y - 184) < 1, ("air %.2f s, y %.0f"):format(airT, p.y)) end },
      -- 8 the grit box in bike zone 1: it stops a walk, a held jump lands on top (above the bikes)
      { act = function() tp(804, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) hold("right", "jump"); love.keypressed("space") end }, { during = 1.0 },
      { act = function(p) release(); report("grit box: a held jump lands on top", math.abs(p.y - 152) < 1 and p.onGround, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 8b the flower box in bike zone 2: it stops a walk, a held jump lands on top, high enough to be safe from
      --    a bike riding under her
      { act = function() tp(3054, 184); hold("right") end }, { during = 1.0 },
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
      -- 11 bike zone 2: the planter is a step up to the bin (a tapped hop and a scramble each)
      { act = function() tp(3346, 184); hold("right") end }, { during = 0.6 },
      { act = function(p) report("planter step: stops a walk", p.x < 3356 and near(p.y, 184), ("x %.0f"):format(p.x)); jump("right", "jump") end },
      { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.onGround and p.mode == "normal" and p.y < 183 end, act = function() release() end, limit = 2 },
      { act = function(p) report("planter step: a tapped hop and a scramble", near(p.y, 154), ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { during = 0.15 }, { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.onGround and p.mode == "normal" and p.y < 153 end, act = function() release() end, limit = 2 },
      { act = function(p) report("bin: a tapped hop and a scramble from the step", near(p.y, 128), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 12 the pontoon (a rope ferry): it waits by the ferry, comes to the quay when Pepper is near, takes her across
      { act = function() local m = api.stage().movers[1]; m.x0, m.x1 = m.to, m.to + 48; tp(1850, 216) end }, { during = 1.0 },
      { act = function() local m = api.stage().movers[1]; report("pontoon: waits by the ferry", near(m.x0, m.to), ("x %.0f"):format(m.x0)); tp(1160, 184) end },
      { during = 2.0 },
      { act = function() local m = api.stage().movers[1]; report("pontoon: Pepper near: it comes to the quay", near(m.x0, m.from), ("x %.0f in 2 s"):format(m.x0)) end },
      { act = function() local m = api.stage().movers[1]; tp(m.x0 + 22, m.y0) end }, { during = 4.5 },
      { act = function(p) local m = api.stage().movers[1]; report("pontoon: carries her across to the ferry", near(m.x0, m.to) and p.ground == m, ("x %.0f, on it %s"):format(m.x0, tostring(p.ground == m))) end },
      -- 13 the high route over bike zone 1: from the bin onto the kiosks' awnings, down onto the planter
      { act = function() tp(660, 128); hold("right") end },
      { cond = function(p) return p.x >= 678 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("kiosks: from the bin onto the first awning", near(p.y, 112) and p.x > 722, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 820 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("kiosks: onto the second awning (gold bone)", near(p.y, 112) and p.x > 875, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 975 end, act = function() release() end, limit = 2 },
      { cond = function(p) return p.onGround and p.y > 150 end, act = function() end, limit = 2 },
      { act = function(p) local s = api.stage()
          report("kiosks: down onto the planter (route done)", near(p.y, 154) and p.x > 976 and p.x < 1048, ("x %.0f y %.0f"):format(p.x, p.y))
          report("secret: KIOSK ROOFS counted", s.secrets[2].found, ("%d of %d"):format(s:stats().secrets, s:stats().secretsTotal)) end },
      -- 14 Pepper's kennel: it stops a walk; crawling in finds the gold bone (a secret)
      { act = function() tp(60, 184); api.stage().pepper.face = -1; hold("left") end }, { during = 0.6 },
      { act = function(p) report("kennel: stops a walk", p.x >= 50.9 and near(p.y, 184), ("x %.1f"):format(p.x)); hold("left", "down") end }, { during = 1.5 },
      { act = function(p) release(); local s = api.stage(); local got
          for _, bn in ipairs(s.bones) do if bn.x == 16 then got = bn.taken end end
          report("kennel: crawl in, the gold bone is inside", p.x < 22 and got, ("x %.0f, bone %s"):format(p.x, tostring(got)))
          report("secret: KENNEL counted (2 of 3)", s.secrets[1].found and s:stats().secrets == 2 and s:stats().secretsTotal == 3, ("%d of %d"):format(s:stats().secrets, s:stats().secretsTotal)) end },
      { act = function() hold("right", "down") end }, { during = 1.2 },
      { act = function(p) release(); report("kennel: crawl back out", p.x > 50 and near(p.y, 184), ("x %.0f"):format(p.x)) end },
      -- 15 traffic: a bike is sent 1 s before it reaches the screen edge (its bell rings then); hard mode
      { act = function() local s = api.stage(); local c = Sp.spawn(s, s.def.bikes[1]); local lead = (c.x - (s.def.bikes[1].w or 48) / 2 - (s.cam + 320)) / c.speed   -- (the front: half the hit box)
          report("bike: sent 1 s before the screen edge (bell)", math.abs(lead - 1) < 0.01, ("%.2f s"):format(lead))
          local St = require("stage"); local h = St.new(s.def, { hard = true })
          report("hard mode: 1 heart, bikes 25% faster", h.hearts == 1 and Sp.speed(h, h.def.bikes[1]) == h.def.bikes[1].speed * 1.25,
            ("hearts %d, speed %.2f"):format(h.hearts, Sp.speed(h, h.def.bikes[1]))) end },
      -- 16 the harbour: the rowing boats carry Pepper and rest at each end; the gulls
      { act = function() local s = api.stage(); local b = s.movers[2]; b.x0, b.x1, b.dir, b.waitT = 2200, 2256, 1, 0; tp(2228, 219)
          for _, k in ipairs(s.critters) do k.state, k.timer = "circle", 99 end end },                  -- (the gulls wait)
      { wait = 2.0 },
      { act = function(p) local s = api.stage(); local b = s.movers[2]
          report("harbour: a rowing boat carries Pepper", p.ground == b and p.x > 2270 and near(p.y, 219), ("x %.0f, boat x %.0f"):format(p.x, b.x0)) end },
      { cond = function(p, s) return s.movers[2].waitT and s.movers[2].waitT > 0 end, act = function(p, s) minY = s.movers[2].x0 end, limit = 6 },
      { wait = 1.2 },
      { act = function(p, s) local b = api.stage().movers[2]
          report("harbour: a boat rests at the end of its row", near(b.x0, minY) and near(minY, 2340), ("x %.0f"):format(b.x0)) end },
      { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("harbour: a jump from the boat onto the jetty", near(p.y, 196) and p.x > 2387, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() local s = api.stage(); s.hearts = 3; hearts = 3; local k = s.critters[1]
          k.state, k.t, k.x, k.y, k.tx, k.ty = "warn", 0, 2424, 36, 2424, 196; tp(2424, 196) end }, { during = 2.2 },
      { act = function(p) local s = api.stage(); report("gull: its swoop hits a standing Pepper", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { act = function() local s = api.stage(); s.hearts = 3; hearts = 3; local k = s.critters[1]; s.pepper.invuln = 0
          k.state, k.t, k.x, k.y, k.tx, k.ty = "warn", 0, 2424, 36, 2424, 196; tp(2424, 196); hold("down") end }, { during = 2.2 },
      { act = function(p) release(); local s = api.stage(); report("gull: crawling ducks under it", s.hearts == hearts, ("hearts %d"):format(s.hearts)) end },
      { act = function() local s = api.stage(); local k = s.critters[1]; s.pepper.barkT = 0
          k.state, k.t, k.x, k.y, k.tx, k.ty = "warn", 0, 2424, 36, 2424, 196; tp(2424, 196) end }, { wait = 0.1 },
      { act = function() love.keypressed("z") end }, { wait = 0.2 },
      { act = function() local k = api.stage().critters[1]; report("gull: a bark while it squawks scares it off", k.state == "away", k.state) end },
      { act = function() local s = api.stage(); local z1, z2 = s.def.bikes[1], s.def.bikes[2]
          report("bikes: zone 1 the tutorial's pace, zone 2 faster", z1.speed == 115 and z2.speed == 135 and z2.every < z1.every, ("%d, %d"):format(z1.speed, z2.speed)) end },
      -- 17 (r6/levels) the tutorial: the fallen branch is a tap hop on flat pavement
      { act = function() tp(232, 184); hold("right") end }, { during = 0.8 },
      { act = function(p) report("branch: stops a walk", p.x < 254 and near(p.y, 184), ("x %.0f"):format(p.x)); jump("right", "jump") end },
      { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.onGround and p.mode == "normal" and p.y < 183 end, act = function() release() end, limit = 2 },
      { act = function(p) report("branch: a tapped hop lands on it", near(p.y, 163), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 18 the first bike: climbing the bin sends one right under her; standing still up there she is safe
      { act = function() local s = api.stage(); tp(616, 184); s.bikeT = 2.5; s.zoneIn = {}; s.hearts = 3; hold("right", "jump"); love.keypressed("space") end },
      { during = 0.3 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 2 },
      { act = function(p, s) local st = api.stage(); report("first bike: sent as she lands on the bin", #st.bikes == 1 and near(p.y, 128), ("bikes %d, y %.0f"):format(#st.bikes, p.y)) end },
      { cond = function(p) local st = api.stage(); return #st.bikes == 0 end, act = function() end, limit = 8 },
      { act = function(p) local st = api.stage(); report("first bike: passes under her, no heart lost", st.hearts == 3 and near(p.y, 128), ("hearts %d"):format(st.hearts)) end },
      -- 19 the first gull only circles: Pepper standing under it for 8 s keeps her hearts
      { act = function() local s = api.stage(); s.hearts = 3; tp(1850, 216) end }, { during = 8 },
      { act = function(p) local st = api.stage(); local k = st.critters[3]
          report("first gull: circles, never swoops", st.hearts == 3 and k.state == "circle", ("hearts %d, %s"):format(st.hearts, k.state)) end },
      -- 20 (night/25oct-fixes) every quay railing is drawn from its prop's left end to its right end (whole bays
      --    alone stopped up to 83 px short), as the game draws it: the image put on a canvas, its opaque columns; and
      --    no two posts closer than 40 px (their foot plates on the bottom row), for the level's railings and for
      --    every width from 89 to 430 px (every remainder with 0 to 3 whole bays)
      { act = function()
          local Sc = require("scene")
          local function measure(w)
            local im = Sc.railing(w, "decor")
            local cv = love.graphics.newCanvas(im:getWidth(), im:getHeight())
            love.graphics.push("all"); love.graphics.setCanvas(cv); love.graphics.clear(0, 0, 0, 0); love.graphics.origin()
            love.graphics.setColor(1, 1, 1, 1); love.graphics.draw(im, 0, 0); love.graphics.pop()
            local d = cv:newImageData(); local first, last, feet, run = nil, nil, {}, nil
            for x = 0, d:getWidth() - 1 do
              for y = 0, d:getHeight() - 1 do if select(4, d:getPixel(x, y)) > 0 then first = first or x; last = x; break end end
              local foot = select(4, d:getPixel(x, d:getHeight() - 1)) > 0
              if foot and not run then run = x elseif not foot and run then feet[#feet + 1] = (run + x - 1) / 2; run = nil end
            end
            if run then feet[#feet + 1] = (run + d:getWidth() - 1) / 2 end
            local gap = 999; for i = 2, #feet do gap = math.min(gap, feet[i] - feet[i - 1]) end
            cv:release()
            return first, last, gap
          end
          local bad, n = {}, 0
          for _, pr in ipairs(api.stage().def.props) do
            if pr.railing then
              local w = pr.x1 - pr.x0; n = n + 1
              local first, last, gap = measure(w)
              if first ~= 0 or last ~= w - 1 or gap < 40 then bad[#bad + 1] = ("x %d-%d drawn %s-%s, posts %s apart"):format(pr.x0, pr.x1, tostring(first and pr.x0 + first), tostring(last and pr.x0 + last + 1), gap) end
            end
          end
          for w = 89, 430 do
            local first, last, gap = measure(w)
            if first ~= 0 or last ~= w - 1 or gap < 40 then bad[#bad + 1] = ("w %d: %s-%s, posts %s apart"):format(w, tostring(first), tostring(last), gap); if #bad > 4 then break end end
          end
          report("quay railings reach both ends, posts 40 px apart", n > 0 and #bad == 0, #bad == 0 and (n .. " railings, widths 89-430") or table.concat(bad, "; ")) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
    require("tests_safety")(steps, api, report)                  -- the safety nets (r6/engine), before the summary
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
    -- the harbour: wait (ducking when a gull squawks over her: hold Down until it has swooped) until done(p, s)
    local function gullNear(p, s)
      for _, k in ipairs(s.critters or {}) do
        if k.kind == "gull" and (k.state == "warn" or k.state == "swoop") and math.abs((k.tx or k.x) - p.x) < 48 then return true end
      end
    end
    local function ride(done, limit, ...)
      local keys = { ... }
      return at(function(p, s)
        if gullNear(p, s) then hold("down") elseif #keys > 0 then hold(unpack(keys)) else release() end
        return done(p, s) and not gullNear(p, s)
      end, function() release() end, limit or 12)
    end
    steps = {
      { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 },
      at(function(p) return true end, function() hold("right") end),
      at(function(p) return p.x >= 70 end, function() hold("right", "jump"); love.keypressed("space") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() hold("right") end),            -- on the bench seat
      onto(270, 163),                                                                                -- the fallen branch (r6/levels)
      onto(401, 152, 310),                                                                           -- the flower box
      onto(641, 128),                                                                                -- the bin: jump and scramble
      -- bike zone 1 by the high route (a secret): from the bin onto the two kiosk awnings, down onto the planter,
      -- then the flower box; up there the bikes pass under her
      at(function(p) return p.x >= 678 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 113 and p.x > 722 end, function() hold("right") end),
      at(function(p) return p.x >= 820 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 113 and p.x > 875 end, function() hold("right") end),
      at(function(p) return p.x >= 975 end, function() release() end),
      at(function(p) return p.onGround and p.y > 150 end, function() hold("right") end),
      onto(1113, 152, 1034),
      -- (r6/levels: slower bikes, so one may still be coming: wait on the flower box until it has passed under her)
      at(function(p) return p.x >= 1185 end, function() release() end, 4),
      at(function(p, s) return (#s.bikes == 0 and s.bikeT > 1.2) or (#s.bikes > 0 and s.bikes[1].x < p.x - 60) end, function() hold("right") end, 9),
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
      -- the harbour: wait on the quay for the first rowing boat, hop on, ride it to the jetty, jump onto the
      -- jetty, wait there for the second boat, step down onto it, ride it to the far quay; duck under the gull
      at(function(p) return p.x >= 2150 end, function() release() end, 9),
      ride(function(p, s) local b = s.movers[2]; return p.onGround and b.x0 <= 2198 and b.dir > 0 end, 14),
      at(function() return true end, function() jump("right") end), { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p, s) return p.x >= s.movers[2].x0 + 16 end, function() release() end, 2),
      ride(function(p, s) return p.ground == s.movers[2] and s.movers[2].x0 >= 2338 end, 14),
      at(function() return true end, function() jump("right", "jump") end),
      at(function(p) return p.x >= 2412 end, function() release() end, 3),
      ride(function(p, s) local b = s.movers[3]; return p.onGround and p.y <= 197 and b.x0 <= 2458 and b.dir > 0 end, 14),
      at(function() return true end, function() hold("right") end),
      at(function(p, s) return p.ground == s.movers[3] and p.x >= s.movers[3].x0 + 20 end, function() release() end, 3),
      ride(function(p, s) return (p.ground == s.movers[3] and s.movers[3].x0 >= 2578) or (p.onGround and p.x > 2610 and p.y <= 217) end, 14),
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.x >= 2840 and p.y <= 185 end, function() hold("right") end, 9),           -- up the steps
      onto(2930, 154),                                                                               -- the planter
      -- bike zone 2: flower box, grit box, bin
      onto(3081, 152), onto(3240, 152, 3183), onto(3416, 128, 3326),                -- (a held jump from the grit box clears the planter step)
      onto(3548, 156),                                                                               -- the last bench
      at(function(p) return p.x >= 3740 and p.onGround end, function() release() end, 9),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played%s"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time, s.hard and " (hard)" or "")); io.stdout:flush()
          love.event.quit() end },
    }
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("title") end }, { wait = 0.2 }, shot("00_title"), { act = function() api.setState("intro") end },
      { wait = 0.6 }, shot("00_intro"), { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    -- one shot per screen (camera on the screen's left edge), Pepper standing on open ground in it
    local spots = { { 40, 184 }, { 480, 152 }, { 760, 184 }, { 1074, 184 }, { 1350, 216 },
                    { 1680, 154 }, { 2110, 216 }, { 2420, 196 }, { 2700, 216 }, { 3010, 184 }, { 3300, 152 }, { 3720, 184 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.6 }
      steps[#steps + 1] = shot(("%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    steps[#steps + 1] = { act = function() love.keypressed("g") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("11_debug_screen12", 3520)
    steps[#steps + 1] = { act = function() tp(1680, 154) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("12_debug_screen6", 1600)
    steps[#steps + 1] = { act = function() love.keypressed("g"); love.keypressed("tab") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("13_tuning")
    steps[#steps + 1] = { act = function() love.keypressed("tab") end }
    -- the new spots: the kennel, the kiosk roofs over a bike, a bike's warning sign, the pontoon waiting at the
    -- quay, the planter step before the bin
    local function add(t) for _, st in ipairs(t) do steps[#steps + 1] = st end end
    add({ { act = function() tp(60, 184); api.stage().pepper.face = -1; hold("left", "down") end }, { wait = 1.3 },
          shot("14_kennel", 0), { act = function() release() end },
          { act = function() local s = api.stage(); tp(800, 112); s.bikes = { { x = 905, y = 184, warn = 0, zone = s.def.bikes[1], speed = 115 } } end },
          { wait = 0.4 }, shot("15_kiosk_roofs", 640),
          { act = function() local s = api.stage(); tp(860, 184); s.bikes = { Sp.spawn(s, s.def.bikes[1]) } end },
          { wait = 0.3 }, shot("16_bike_warning", 700),
          { act = function() tp(1330, 216) end }, { wait = 2.2 }, shot("17_pontoon_at_quay", 1230),
          { act = function() tp(3394, 154) end }, { wait = 0.4 }, shot("18_planter_step", 3220) })
    -- the near lane's traffic, at its perspective size: cars and cyclists put on the road for the shots
    local function traffic(list)
      local s = api.stage(); local Rd = require("road"); local A = Rd.art()
      s.road.list = {}
      for _, v in ipairs(list) do
        local car = v[1] == "car"
        local im = car and A.cars[v[2]] or (A.riders or A.cyclists)[v[2]]
        local sp = { 0, s.world.width }
        for _, q in ipairs(s.road.spans) do if v[3] >= q[1] and v[3] < q[2] then sp = q end end
        local e = { im = im, x = v[3], w = im:getWidth(), vx = (v[4] and 1 or -1) * 0.01, sp = sp, bob = 0,
          flip = car and v[4] or (not car and not v[4]), f = 1, cam0 = 0, base = 0.01, still = true }   -- (at world x, kept for the shot)
        if car then e.top = Rd.CAR_TOP; if not e.top then e.base = 239 end
        else e.top = Rd.RIDER_TOP; if not e.top then e.base = 236 end end
        s.road.list[#s.road.list + 1] = e
      end
      s.road.t = 99
    end
    add({ { act = function() tp(150, 184) end }, { wait = 0.3 },
          { act = function() traffic({ { "car", 1, 10, true }, { "rider", 1, 250, false } }) end }, { wait = 0.05 }, shot("19_traffic_home", 0),
          { act = function() tp(700, 184) end }, { wait = 0.3 },
          { act = function() traffic({ { "car", 2, 690, true }, { "car", 3, 450, true } }) end }, { wait = 0.05 }, shot("20_traffic_bin", 520),
          { act = function() tp(2952, 154) end }, { wait = 0.3 },
          { act = function() traffic({ { "car", 4, 2830, true }, { "rider", 2, 3020, false } }) end }, { wait = 0.05 }, shot("21_traffic_planter", 2760),
          { act = function() tp(140, 184); api.stage().pepper.face = 1; hold("down") end }, { wait = 0.4 },
          { act = function() traffic({ { "car", 5, 60, true } }) end }, { wait = 0.05 }, shot("22_traffic_crawl", 0),
          { act = function() release() end } })
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
      if TRACE then                                    -- --auto --trace: Pepper's state every step, no screenshots
        if p then print(("T %d %.3f %.3f %.3f %.3f %s %d %d %s %s %s"):format(frame, p.x, p.y, p.vx, p.vy, p.anim, p.frame, p.face,
          p.mode, tostring(p.onGround), tostring(p.crouch))) end
      elseif frame % 3 == 0 then n = n + 1; love.graphics.captureScreenshot(("rec/%04d.png"):format(n)) end
      if os.getenv("AUTO_TRACE") and p and p.x > tonumber(os.getenv("AUTO_TRACE")) and frame % 6 == 0 then print(("    f%d x %.0f y %.0f"):format(frame, p.x, p.y)) end   -- (for cutting GIFs: rec/ n = frame / 3)
      if s and not TRACE and s.hearts ~= (lastHearts or s.maxHearts) then print(("  lost a heart at x %.0f y %.0f (step %d)"):format(p.x, p.y, i)) end
      lastHearts = s and s.hearts
    end
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.during then if st.each and p then st.each(p) end; if since >= st.during then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond(p, s) then
        if os.getenv("AUTO_DEBUG") then print(("step %d at x %.1f y %.1f vx %.0f %s"):format(i, p.x, p.y, p.vx, p.onGround and "G" or "A")) end
        st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
