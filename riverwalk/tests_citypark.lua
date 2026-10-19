-- The checks for Level 1, City Park (love riverwalk --level citypark <flag>). Same flags as tests.lua:
--   --physics   checks every set piece: hop, held jump, log, bench, hedge, stepping stones, duck boat, pond,
--               bin, picnic table, leaf cart, the oak's branches, the magpie and the ball, slide, climbing frame, the girl
--   --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
--   --test      a screenshot tour of the 6 screens, the magpie, the debug view and the tally
local I = require("input")
local Pp = require("pepper")
local Sp = require("setpieces")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false                                     -- (a nil result must count as a failure)
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
    local minY, startY, airT, hearts, inside, score0
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
      { act = function()
          local a, b = prop("STONE", 1), prop("STONE", 2)
          report("pond: the stepping-stone gaps are 32 px", a.x0 - 704 == 32 and b.x0 - a.x1 == 32, ("bank-stone %d, stone-stone %d px"):format(a.x0 - 704, b.x0 - a.x1)) end },
      { act = function() tp(744, 188); hold("right") end },
      { cond = function(p) return p.x >= 758 end, act = function() jump("right", "jump") end, limit = 2 }, { wait = 1 / 60 },
      { act = function() hold("right") end },
      { cond = function(p) return p.x >= 800 or p.mode ~= "normal" end, act = function() release() end, limit = 3 }, { during = 0.5 },
      { act = function(p) report("pond: hop from stone to stone", near(p.y, 188) and p.onGround and p.x > 790, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- the duck boat (a rope ferry) waits by the far bank and comes to the stone when Pepper comes near
      { act = function() local m = api.stage().movers[1]; m.x0, m.x1 = m.to, m.to + 48; tp(1320, 184) end }, { during = 1.0 },
      { act = function() local m = api.stage().movers[1]; report("pond: the duck boat waits by the far bank", near(m.x0, m.to), ("x %.0f"):format(m.x0)); tp(640, 184) end },
      { during = 1.6 },
      { act = function() local m = api.stage().movers[1]; report("pond: Pepper near: the boat comes to the stone", near(m.x0, m.from), ("x %.0f in 1.6 s"):format(m.x0)) end },
      { act = function() local m = api.stage().movers[1]; m.x0, m.x1, m.dir = m.from, m.from + 48, 1; tp(806, 188); hold("right") end },
      { during = 0.5 }, { act = function() release() end }, { during = 0.3 },
      { act = function(p) local m = api.stage().movers[1]; report("pond: walk off the stone onto the duck boat", p.ground == m, ("y %.0f, on it: %s"):format(p.y, tostring(p.ground == m))) end },
      { during = 1.0 },
      { act = function(p) local m = api.stage().movers[1]; report("pond: the duck boat carries Pepper", p.ground == m and m.x0 > m.from + 10 and p.x > m.x0 and p.x < m.x1, ("x %.0f boat %.0f-%.0f"):format(p.x, m.x0, m.x1)) end },
      { act = function() local m = api.stage().movers[1]; m.x0, m.x1, m.dir = m.to, m.to + 48, -1; tp(m.x0 + 30, 202); hold("right") end },
      { during = 0.05 }, { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("pond: a jump from the boat up the far bank", near(p.y, 184) and p.x > 944, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(776, 188); hearts = api.stage().hearts end }, { during = 2.5 },
      { act = function() local s = api.stage(); report("pond: falling in costs a heart", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      -- 6 the bin (56 px): a held jump and a scramble
      { act = function() tp(1300, 184); jump("right", "jump") end }, { during = 0.3 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 2 },
      { act = function(p) release(); report("bin: jump and scramble on top", near(p.y, 128), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 7 the leaf cart: it hurts on the path, the picnic table is above it, a running jump clears it
      { act = function() tp(1530, 184); local s = api.stage(); hearts = s.hearts; s.bikes = { { x = 1620, y = 184, warn = 0, zone = s.def.bikes[1] } } end },
      { during = 2.0 },
      { act = function() local s = api.stage(); report("leaf cart: hurts Pepper on the path", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { act = function() tp(1390, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); local s = api.stage(); hearts = s.hearts
          report("picnic table: a held jump lands on top", near(p.y, 156), ("x %.0f y %.0f"):format(p.x, p.y))
          s.bikes = { { x = p.x + 90, y = 184, warn = 0, zone = s.def.bikes[1] } }; s.bikeT = 99 end },
      { during = 2.0 },
      { act = function(p) local s = api.stage(); report("picnic table: safe from the leaf cart", near(p.y, 156) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts)) end },
      { act = function() tp(1510, 184); local s = api.stage(); hearts = s.hearts; s.bikes = { { x = 1330, y = 184, warn = 0, zone = s.def.bikes[1] } }; hold("right") end },
      { cond = function(p, s) return s.bikes[1] and s.bikes[1].x - p.x < 92 end, act = function() jump("right", "jump") end, limit = 2 },
      { during = 1.2 },
      { act = function() local s = api.stage(); release(); report("leaf cart: a running jump clears it", s.hearts == hearts, ("hearts %d"):format(s.hearts)) end },
      -- 8 the oak: held jumps from branch to branch up to the top
      { act = function() tp(1766, 184); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("oak: path to the low branch", near(p.y, 156), ("y %.0f"):format(p.y)) end },
      { act = function() tp(1790, 156); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("oak: low branch to the middle branch", near(p.y, 128), ("y %.0f"):format(p.y)) end },
      { act = function() tp(1780, 128); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("oak: middle branch to the top branch", near(p.y, 100), ("y %.0f"):format(p.y)) end },
      -- the magpie: it flees a running Pepper, lets a walking one come close, drops the ball when she barks
      { act = function() local s = api.stage(); s:resetMagpie(2); tp(250, 184); hold("right") end }, { during = 1.0 },
      { act = function() release(); local m = api.stage().magpie; report("magpie: it flies on when Pepper runs at it", m.i == 3, ("perch %d"):format(m.i)) end },
      -- the first perch is kinder: a kid who runs straight at it is stopped by the log inside bark range
      { act = function() local s = api.stage(); s:resetMagpie(1); tp(40, 184); hold("right") end }, { during = 1.5 },
      { act = function(p) local s = api.stage(); local m = s.magpie
          report("magpie 1: running at it, it stays (log stops her)", m.i == 1 and math.abs(p.x - m.x) <= s.def.magpie.bark, ("perch %d, %.0f px away"):format(m.i, math.abs(p.x - m.x)))
          release(); p.face = 1; love.keypressed("z") end }, { wait = 0.1 },
      { act = function() local s = api.stage(); report("magpie 1: a bark from there drops the ball", s.ball.state == "air" or s.ball.state == "rest", s.ball.state) end },
      { during = 1.5 },
      { act = function() local s = api.stage(); s:resetMagpie(1); tp(40, 184); s.pepper.face = 1; s.pepper.barkT = 0; love.keypressed("z") end }, { wait = 0.3 },
      { act = function() local s = api.stage(); report("magpie: a bark from far away does not work", s.ball.state == "magpie" and s.magpie.i == 1, s.ball.state); hold("right", "walk") end },
      { cond = function(p) return p.x >= 150 or p.vx < 1 and p.x > 100 end, act = function() release() end, limit = 3 }, { wait = 0.3 },
      { act = function(p) local s = api.stage(); report("magpie: a walking Pepper can come close", s.magpie.i == 1 and s.ball.state == "magpie", ("x %.0f perch %d"):format(p.x, s.magpie.i))
          p.face = 1; love.keypressed("z") end }, { wait = 0.1 },
      { act = function() local s = api.stage(); report("magpie: a bark close up makes it drop the ball", s.ball.state == "air" or s.ball.state == "rest", s.ball.state) end },
      { during = 1.5 },
      { act = function() local s = api.stage(); local b = s.ball
          report("ball: it falls to the path", b.state == "rest" and near(b.y, 184), ("%s x %.0f y %.0f"):format(b.state, b.x, b.y))
          report("magpie: it flies away", s.magpie.state == "gone", s.magpie.state) end },
      { act = function() local b = api.stage().ball; tp(b.x - 18, 184); api.stage().pepper.face = 1 end }, { wait = 0.1 },
      { act = function() love.keypressed("x") end }, { wait = 0.2 },
      { act = function(p) report("ball: Pepper picks it up", p.carrying ~= nil, tostring(p.carrying ~= nil)) end },
      -- each perch: a bark from the path makes it drop the ball, and the ball lands where a small child can get it:
      -- the path, or a top on the main route at most 56 px up (bench seat, bin top, slide tower, climbing frame)
    }
    local spots = { 150, 320, 610, 1200, 1280, 1545, 2360, 2580, 2700 }                     -- where Pepper barks from, per perch
    for k, x in ipairs(spots) do
      steps[#steps + 1] = { act = function() local s = api.stage(); s:resetMagpie(k); s.pepper.carrying = nil; tp(x, 184); s.pepper.face = 1
          for _, c in ipairs(s.critters) do c.state, c.y = "gone", -999 end end }                 -- geese have their own checks
      steps[#steps + 1] = { wait = 0.1 }
      steps[#steps + 1] = { act = function() love.keypressed("z") end }
      steps[#steps + 1] = { during = 1.5 }
      steps[#steps + 1] = { act = function() local s = api.stage(); local b, pr = s.ball, s.def.magpie.perches[k]
          report(("magpie perch %d (x %d): the ball is easy to reach"):format(k, pr.x), b.state == "rest" and 184 - b.y <= 56,
            ("%s at x %.0f y %.0f (%d px up)"):format(b.state, b.x, b.y, 184 - b.y)) end }
    end
    for _, st in ipairs({
      -- 9 the playground: up the slide tower, down the slide on the ground, the climbing frame's bars
      { act = function() tp(2590, 184); jump("right", "jump") end }, { during = 0.3 }, landed(),
      { act = function(p) release(); report("slide: a held jump onto the tower", near(p.y, 152), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(2640, 152); airT = 0; hold("right") end },
      { during = 0.6, each = function(p) if not p.onGround then airT = airT + 1 / 60 end end },
      { act = function(p) release(); report("slide: down the slide on the ground", airT < 0.05 and near(p.y, 184) and p.x > 2688, ("air %.2f s, x %.0f y %.0f"):format(airT, p.x, p.y)) end },
      -- (a knock-back that does not lift her: her jump base is set so the short-hop rule cancels the bounce,
      --  as happened in a QA fuzz run)
      { act = function(p) tp(2658.1, 154.1); local s = api.stage(); s.pepper:hurt(s.pepper.x + 10, s.world); s.pepper.jumpBase = s.pepper.y + 30; inside = false end },
      { during = 1.5, each = function(p)                                                     -- the QA rule (qa.lua)
          local w = api.stage().world
          local r = w:solidIn(p.x - 12.5, p.x + 12.5, p.y - p:height() + 1.5, p.y - w.STEP - 0.5)
          if r and r.terrain and w:slopeNear(p.x - Pp.HW, p.x + Pp.HW) then r = nil end
          if p.x > 2624 and p.x < 2656 and p.y > 152.5 and p.y < 183.5 then r = true end      -- in the tower, under its top
          if r then inside = ("x %.1f y %.1f"):format(p.x, p.y) end
        end },
      { act = function(p) report("slide: knocked back off its top, not into the tower", not inside, inside or ("ends x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(2736, 184); jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end }, { during = 0.1 }, landed(),
      { act = function(p) report("climbing frame: a hop onto the low bar", near(p.y, 160), ("y %.0f"):format(p.y)) end },
      { act = function() tp(2744, 160); jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end }, { during = 0.1 }, landed(),
      { act = function(p) report("climbing frame: a hop onto the top bar", near(p.y, 136), ("y %.0f"):format(p.y)) end },
      -- the high route over the pond: hedge top, the three willows' branches, down on the far bank
      { act = function() tp(560, 112); hold("right") end },
      { cond = function(p) return p.x >= 590 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("willows: from the hedge top onto the first branch", near(p.y, 120) and p.x > 660, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 724 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("willows: onto the middle branch (gold bone)", near(p.y, 112) and p.x > 770, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 828 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("willows: onto the last branch", near(p.y, 120) and p.x > 870, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 950 end, act = function() end, limit = 2 }, landed(),
      { act = function(p) release(); local s = api.stage()
          report("willows: down onto the far bank (route done)", near(p.y, 184) and p.x > 944, ("x %.0f y %.0f"):format(p.x, p.y))
          report("secret: WILLOWS counted", s.secrets[1].found, ("%d of %d"):format(s:stats().secrets, s:stats().secretsTotal)) end },
      -- the hollow log: stops a walk, a held jump onto it, crawling through finds the gold bone (a secret)
      { act = function() local s = api.stage(); tp(1535, 184); s.zoneIn[s.def.bikes[1]] = true; hold("right") end }, { during = 0.8 },
      { act = function(p) hearts = api.stage().hearts; report("hollow log: stops a walk", p.x < 1548, ("x %.0f"):format(p.x)); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("hollow log: a held jump lands on top", near(p.y, 158), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() local s = api.stage(); tp(1535, 184); s.zoneIn[s.def.bikes[1]] = true; hold("right", "down") end }, { during = 2.5 },
      { act = function(p) release(); local s = api.stage()
          report("hollow log: crawl through it", p.x > 1620 and p.x < 1650 and near(p.y, 184) and s.hearts == hearts, ("x %.0f"):format(p.x))
          report("secret: HOLLOW LOG counted (gold bone inside)", s.secrets[2].found and (function() for _, bn in ipairs(s.bones) do if bn.x == 1585 then return bn.taken end end end)(), ("found %s"):format(tostring(s.secrets[2].found))) end },
      -- the oak's top branch (the third secret)
      { act = function() tp(1780, 128); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); local s = api.stage()
          report("secret: OAK TOP counted", s.secrets[3].found and s:stats().secrets == 3 and s:stats().secretsTotal == 3, ("%d of %d"):format(s:stats().secrets, s:stats().secretsTotal)) end },
      -- the leaf cart sets off when Pepper walks into its zone, 1 s before it is on screen
      { act = function() tp(1350, 184); hold("right") end },
      { cond = function(p, s) return #s.bikes > 0 end, act = function(p, s) release(); local c = s.bikes[1]
          local lead = (c.x - 24 - (s.cam + 320)) / c.speed
          report("leaf cart: sets off as Pepper enters its zone", p.x > 1376 and p.x < 1390, ("x %.0f"):format(p.x))
          report("leaf cart: 1 s from the screen edge (bell)", math.abs(lead - 1) < 0.05, ("%.2f s"):format(lead)) end, limit = 2 },
      -- hard mode: one heart, the cart 25% faster
      { act = function() local St = require("stage"); local h = St.new(api.stage().def, { hard = true })
          report("hard mode: 1 heart, the cart 25% faster", h.hearts == 1 and h.maxHearts == 1 and Sp.speed(h, h.def.bikes[1]) == h.def.bikes[1].speed * 1.25,
            ("hearts %d, speed %.0f"):format(h.hearts, Sp.speed(h, h.def.bikes[1]))) end },
      -- the geese (critters.lua): a goose's bite costs a heart, a bark shoos it away for good (+200), a held jump
      -- clears one; the creek's gaps are too wide to walk across, a tapped hop lands on the next stone
      { act = function() local s = api.stage(); local k = s.critters[1]; k.state, k.x, k.y, k.dir, k.t = "walk", 1160, 184, -1, 0
          s.hearts = 3; hearts = 3; tp(1060, 184); hold("right") end }, { during = 2.5 },
      { act = function() release(); local s = api.stage(); report("goose: its bite costs a heart", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { act = function() local s = api.stage(); local k = s.critters[1]; k.state, k.x, k.y, k.dir, k.t = "walk", 1160, 184, -1, 0
          s.hearts = 3; tp(1100, 184); s.pepper.face = 1; s.pepper.invuln = 0; s.pepper.barkT = 0; score0 = s.score end }, { wait = 0.1 },
      { act = function() love.keypressed("z") end }, { wait = 0.2 },
      { act = function() local s = api.stage(); local k = s.critters[1]
          report("goose: a bark within 80 px shoos it (+200)", k.state == "gone" and s.score == score0 + 200, ("%s, +%d"):format(k.state, s.score - score0)) end },
      { during = 1.5 },
      { act = function() local s = api.stage(); local k = s.critters[1]; report("goose: it flies off the screen", k.x - s.cam > 330 or k.y < -20, ("x %.0f y %.0f"):format(k.x - s.cam, k.y)) end },
      { act = function() local s = api.stage(); local k = s.critters[1]; k.state, k.x, k.y, k.dir, k.t = "rest", 1160, 184, -1, 0
          s.hearts = 3; hearts = 3; tp(1040, 184); hold("right") end },
      { cond = function(p) return p.x >= 1104 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.3 }, landed(),
      { act = function(p) release(); local s = api.stage(); report("goose: a held jump clears a standing goose", p.x > 1172 and s.hearts == hearts, ("x %.0f hearts %d"):format(p.x, s.hearts)) end },
      { act = function() local s = api.stage(); s.critters[1].state = "gone"; s.hearts = 3; hearts = 3; tp(1990, 184); hold("right") end }, { during = 1.5 },
      { cond = function(p, s) return s.hearts < hearts end, act = function() end, limit = 5 }, { wait = 0.8 },
      { act = function() release(); local s = api.stage(); report("creek: running at it lands in the water", s.hearts == hearts - 1, ("hearts %d x %.0f y %.0f %s"):format(s.hearts, s.pepper.x, s.pepper.y, s.pepper.mode)) end },
      { act = function() tp(2068, 188) end }, { wait = 0.3 },
      { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("creek: a standing jump lands on the next stone", near(p.y, 188) and p.x > 2136 - 13 and p.x < 2160 + 13, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- every lamp's ball home is a spot the ball can rest on (by the bin lamp it was inside the bin once)
      { act = function() local s = api.stage(); local bad = {}
          for _, l in ipairs(s.lamps) do local h = s:homeNear(l.x, l.y); local w = s.world
            if w:solidIn(h.x - 3, h.x + 3, h.y - 6, h.y - 1) or w:inWater(h.x, h.y - 2) then bad[#bad + 1] = l.x end end
          report("lamps: the ball's home by each lamp is clear", #bad == 0, #bad == 0 and "all clear" or table.concat(bad, ", ")) end },
      -- last: give the ball to the girl by the swings
      { act = function() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball; tp(s.girl.x - 30, 184); s.pepper.face = 1 end },
      { wait = 0.1 }, { act = function() love.keypressed("x") end }, { wait = 3.0 },
      { act = function() report("girl: giving her the ball clears the level", api.getState() == "clear", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }) do steps[#steps + 1] = st end
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec")
    local function at(cond, act, limit) return { cond = cond, act = act, limit = limit or 6 } end
    -- a tapped hop from where she stands to a stepping stone centred at cx: hold right, tap A, brake in the air
    -- a held jump from standing onto the stepping stone (or bank) centred at cx: it carries her 75 px
    local function hopTo(cx) return {
      at(function(p) return p.onGround and math.abs(p.vx) < 1 end, function() jump("right", "jump") end),
      at(function(p) return p.x >= cx - 10 end, function() release() end),
      at(function(p) return p.onGround and p.mode == "normal" and math.abs(p.vx) < 1 end, function() release() end) } end
    local function bark() return { act = function() release(); love.keypressed("z") end } end
    local function goose(i) return function(p, s) local k = s.critters[i]; return k.state == "gone" or math.abs(k.x - p.x) < 72 end end
    steps = {
      { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 },
      -- 1 the gate: sneak up to the log (walk), bark, the magpie drops the ball; hop onto the log, pick it up
      at(function() return true end, function() hold("right", "walk") end),
      at(function(p) return p.x >= 158 or (p.x > 140 and p.vx < 1) end, function() release() end, 9),
      { wait = 0.3 }, { act = function() love.keypressed("z") end }, { wait = 1.4 },
      at(function(p, s) return s.ball.state == "rest" end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right", "walk") end),
      at(function(p, s) return p.onGround and p.y >= 183 end, function() end),
      at(function(p, s)                                                                       -- walk up to the ball
        local b = s.ball
        local want = p.x < b.x and 1 or -1
        if p.face == want and math.abs(p.x + p.face * 18 - b.x) < 20 and math.abs(p.vx) < 1 then return true end
        local tx = b.x - want * 18
        if p.face ~= want then hold(want > 0 and "right" or "left", "walk")
        elseif p.x < tx - 3 then hold("right", "walk") elseif p.x > tx + 3 then hold("left", "walk") else release() end
        return false
      end, function() release() end),
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.6 },
      at(function(p) return p.carrying ~= nil end, function() hold("right") end, 2),
      -- 2 a held jump onto the bench, then crawl under the hedge
      at(function(p) return p.x >= 300 and p.onGround and p.y > 183 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() hold("right") end),
      at(function(p) return p.x >= 490 and p.onGround and p.y > 183 end, function() hold("right", "down") end),
      at(function(p) return p.x >= 612 end, function() hold("right") end, 9),
      -- 3 the pond: onto the first stone, a hop to the second, wait for the duck boat, ride it, up the bank
      at(function(p) return p.onGround and p.y >= 187 and p.x > 727 end, function() hold("right") end),
      at(function(p) return p.x >= 758 end, function() jump("right", "jump") end),             -- a tapped hop
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.x >= 786 end, function() release() end),                          -- brake in the air
      at(function(p) return p.onGround and p.x >= 790 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 <= s.movers[1].from + 0.5 end, function() hold("right") end, 9),   -- the boat is there
      at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 26 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 >= 884 end, function() jump("right", "jump") end, 9),
      at(function(p) return p.onGround and p.y <= 185 and p.x > 944 end, function() hold("right") end),
      -- 4 the goose lawn: run up to the goose and bark it away, then hop onto the log and on to the bin
      at(goose(1), function() end, 9), bark(), { wait = 0.5 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 1226 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      -- 4 the bin (jump + scramble), the picnic table, wait there for the leaf cart to pass
      at(function(p) return p.x >= 1304 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 129 end, function() hold("right") end),
      at(function(p) return p.x >= 1350 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 and p.x > 1420 end, function() release() end),
      at(function(p) return p.x >= 1444 or p.vx < 1 end, function() release() end),
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 40 end, function() hold("right") end, 12),
      -- 5 crawl through the hollow log (the gold bone inside: a secret)
      at(function(p) return p.x >= 1542 and p.onGround end, function() hold("right", "down") end, 9),
      at(function(p) return p.x >= 1620 end, function() hold("right") end, 9),
      -- 5 the oak: up the branches to the top (gold bone), then off the branches to the right
      at(function(p) return p.x >= 1766 end, function() jump("jump") end, 9),
      at(function(p) return p.onGround and p.y <= 157 end, function() release() end),
      { wait = 0.15 }, { act = function() jump("jump") end },
      at(function(p) return p.onGround and p.y <= 129 end, function() release() end),
      { wait = 0.15 }, { act = function() jump("jump") end },
      at(function(p) return p.onGround and p.y <= 101 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 1800 end, function() hold("right") end, 9),
      -- 7 the creek: stop at the bank, then a tapped hop onto each stone; bark the goose off the far bank
      at(function(p) return p.x >= 1975 end, function() release() end, 9),
      at(function(p) return math.abs(p.vx) < 1 end, function() end),
    }
    for _, cx in ipairs({ 2068, 2148, 2228, 2306 }) do for _, st in ipairs(hopTo(cx)) do steps[#steps + 1] = st end end
    for _, st in ipairs({
      at(goose(2), function() end, 9), bark(), { wait = 0.6 },
      at(function() return true end, function() hold("right") end),
      -- 8 the rose walk: a held jump onto the bench, wait there for the cart, then over to the playground
      at(function(p) return p.x >= 2352 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() release() end),
      { wait = 0.3 },
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 40 end, function() hold("right") end, 12),
      at(function(p) return p.x >= 2474 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 and p.x > 2504 end, function() release() end),
      at(function(p, s) return not s.bikes[1] or s.bikes[1].x < p.x - 40 end, function() hold("right") end, 12),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 2572 end, function() hold("right") end, 9),
      -- 6 the playground: up the slide tower, down the slide, the climbing frame, the girl
      at(function(p) return p.x >= 2588 end, function() jump("right", "jump") end, 9),
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 2688 end, function() hold("right") end),
      at(function(p) return p.x >= 2722 end, function() jump("right", "jump") end),
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.onGround and p.y <= 161 end, function() release() end),
      { wait = 0.3 }, { act = function() jump("jump") end }, { wait = 1 / 60 }, { act = function() release() end },
      at(function(p) return p.onGround and p.y <= 137 end, function() release() end),
      { wait = 0.2 }, { act = function() hold("right") end },
      at(function(p, s) return p.onGround and p.y >= 183 and p.x >= s.girl.x - 40 end, function() release() end, 9),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played%s"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time, s.hard and " (hard)" or "")); io.stdout:flush()
          love.event.quit() end },
    }) do steps[#steps + 1] = st end
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("cp_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    -- one shot per screen (camera on the screen's left edge), Pepper standing in it
    local spots = { { 60, 184 }, { 476, 184 }, { 820, 188 }, { 1060, 184 }, { 1452, 156 }, { 1640, 184 }, { 2148, 188 }, { 2428, 156 }, { 2600, 184 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      if i == 5 then steps[#steps + 1] = { act = function() local s = api.stage(); s.bikes = { { x = 1570, y = 184, warn = 0, zone = s.def.bikes[1] } }; s.bikeT = 99 end } end
      steps[#steps + 1] = { wait = i == 5 and 0.25 or 0.6 }
      steps[#steps + 1] = shot(("cp_%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    -- the magpie: Pepper sneaks up to the log and barks; it drops the ball and flies away
    steps[#steps + 1] = { act = function() local s = api.stage(); s:resetMagpie(1); tp(150, 184); s.pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.4 }; steps[#steps + 1] = shot("cp_07_magpie", 0)
    steps[#steps + 1] = { act = function() love.keypressed("z") end }
    steps[#steps + 1] = { wait = 0.25 }; steps[#steps + 1] = shot("cp_08_drop", 0)
    steps[#steps + 1] = { wait = 0.5 }; steps[#steps + 1] = shot("cp_09_flyaway", 0)
    steps[#steps + 1] = { act = function() local s = api.stage(); s:resetMagpie(6); tp(1542, 184); s.pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.4 }; steps[#steps + 1] = shot("cp_10_oak", 1520)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("cp_11_debug_screen5", 1600)
    steps[#steps + 1] = { act = function() tp(2660, 160) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("cp_12_debug_screen6", 2560)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }
    -- the new spots: running at the magpie (the log stops her in bark range), the duck boat waiting at the stone,
    -- the willows, inside the hollow log, the leaf cart's warning sign
    local function add(t) for _, st in ipairs(t) do steps[#steps + 1] = st end end
    add({ { act = function() local s = api.stage(); s:resetMagpie(1); tp(40, 184); hold("right") end }, { wait = 1.4 },
          shot("cp_15_run_at_magpie", 0), { act = function() release() end },
          { act = function() tp(752, 188) end }, { wait = 1.6 }, shot("cp_16_boat_waits", 640),
          { act = function() tp(804, 112) end }, { wait = 0.4 }, shot("cp_17_willows", 640),
          { act = function() local s = api.stage(); tp(1535, 184); s.zoneIn[s.def.bikes[1]] = true; hold("right", "down") end }, { wait = 1.3 },
          shot("cp_18_hollow_log", 1440), { act = function() release() end },
          { act = function() local s = api.stage(); tp(1450, 156); s.bikes = { Sp.spawn(s, s.def.bikes[1]) } end },
          { wait = 0.3 }, shot("cp_19_cart_warning", 1280) })
    -- give the ball: the tally
    steps[#steps + 1] = { act = function() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball; tp(s.girl.x - 30, 184); s.pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.2 }; steps[#steps + 1] = { act = function() love.keypressed("x") end }
    steps[#steps + 1] = { wait = 1.0 }; steps[#steps + 1] = shot("cp_13_give")
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
      if s and s.hearts ~= (lastHearts or s.maxHearts) then print(("  lost a heart at x %.0f y %.0f (step %d)"):format(p.x, p.y, i)) end
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
