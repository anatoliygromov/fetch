-- The checks for Level 2, Downtown (love riverwalk --level downtown <flag>). Same flags as tests_citypark.lua:
--   --physics   checks every set piece: hop, held jump, crates, cafe tables and parasols, the shop sign, market
--               stall and awnings, the statue, the cat and the ball, the fountain, the tram, the exit
--   --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
--   --test      a screenshot tour of the 6 screens, the cat beat, the tram, the debug view and the tally
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
  local function carry() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball end
  local function tram(x) local s = api.stage(); s.bikes = { { x = x, y = 184, warn = 0, zone = s.def.bikes[1] } }; s.bikeT = 99 end

  local steps
  if mode == "--physics" then
    local minY, startY, hearts
    local function near(a, b) return math.abs(a - b) < 1 end
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      -- 0 the gaps and heights in the props
      { act = function()
          local t1, t2 = prop("TABLE", 1), prop("TABLE", 2)
          local g1, g2 = 184 - t1.y1, 184 - t2.y1
          report("crawl gaps: both cafe tables 18-25 px", g1 >= 18 and g1 < Pp.H_STAND and g2 >= 18 and g2 < Pp.H_STAND, ("%d, %d px"):format(g1, g2))
          local tram = api.stage().def.bikes[1]
          local tops = { prop("KIOSK").y0, prop("SHELTER").y0 }
          report("tram perches are above the tram", tops[1] < 184 - tram.h and tops[2] < 184 - tram.h, ("kiosk %d, shelter %d, tram top %d"):format(tops[1], tops[2], 184 - tram.h))
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
      -- 2 the crate steps: a walk stops, a tapped hop onto the low crate, another onto the high one
      { act = function() tp(100, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) report("crates: stop a walk", p.x < 136 and near(p.y, 184), ("x %.0f"):format(p.x)) end },
      { act = function() tp(104, 184); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.x >= 136 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("crates: a tapped hop onto the low crate", near(p.y, 168), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(158, 168); hold("right") end }, { during = 0.05 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) release(); report("crates: a tapped hop onto the high crate", near(p.y, 152), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 3 the cafe tables: stop a walk, crawl under both, a held jump onto a table, up onto its parasol, from
      --   parasol to parasol, from the second parasol to the shop sign
      { act = function() tp(310, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) report("table: stops a walk", p.x < 352, ("x %.0f"):format(p.x)); hold("right", "down") end },
      { during = 6.0 },
      { act = function(p) release(); report("tables: crawling passes under both", p.x > 545 and near(p.y, 184), ("x %.0f"):format(p.x)) end },
      { act = function() tp(320, 184); hold("right") end }, { during = 0.3 },
      { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("table: a held jump lands on the top", near(p.y, 158), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(392, 158); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("parasol: a held jump from the table onto it", near(p.y, 114), ("y %.0f"):format(p.y)) end },
      { act = function() tp(380, 114); hold("right") end }, { during = 0.3 },
      { act = function() jump("right", "jump") end }, { during = 0.2 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 3 },
      { act = function(p) report("parasol: a running jump to the next one", near(p.y, 114) and p.x > 472, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(500, 114); hold("right") end }, { during = 0.25 },
      { act = function() jump("right", "jump") end }, { during = 0.15 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("sign: a running jump from the parasol onto it", near(p.y, 80), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(440, 184); jump("jump") end }, { during = 1.0 },
      { act = function(p) release(); report("sign: out of reach from the street", near(p.y, 184) and 184 - prop("SIGN").y0 > 46 + 12, ("%d px up"):format(184 - prop("SIGN").y0)) end },
      -- 4 the market: onto the stall, up onto its awning, Down + A drops through; the crates up to the second awning
      { act = function() tp(650, 184); hold("right") end }, { during = 0.2 },
      { act = function() jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("stall: a held jump onto the counter", near(p.y, 156), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(720, 156); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("awning: a held jump from the counter onto it", near(p.y, 116), ("y %.0f"):format(p.y)) end },
      { act = function() tp(704, 116) end }, { wait = 0.1 }, { act = function() jump("down", "jump") end }, { wait = 0.1 },
      { act = function() release() end }, { during = 0.2 }, landed(),
      { act = function(p) report("awning: Down + A drops through to the counter", near(p.y, 156), ("y %.0f"):format(p.y)) end },
      { act = function() tp(770, 184); hold("right") end }, { during = 0.05 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) report("market crates: a hop onto the low one", near(p.y, 168), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(806, 168); hold("right") end }, { during = 0.05 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) release(); report("market crates: a hop onto the high one", near(p.y, 152), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(842, 152); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.2 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("awning 2: a held jump from the crates onto it", near(p.y, 112), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 5 the statue: the pedestal, the arm, the hat
      { act = function() tp(1090, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("pedestal: a held jump onto it", near(p.y, 144), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1158, 144); jump("right", "jump") end }, { during = 0.15 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("arm: a held jump from the pedestal onto it", near(p.y, 108), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1162, 108); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("hat: a held jump from the arm onto it", near(p.y, 76), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 6 the cat: a far bark only makes it look up; the ball cannot be picked up under it; a bark from the street
      --   under the arm scares it, the ball drops to the street, the cat runs off; Pepper picks the ball up
      { act = function() tp(1060, 184) end }, { wait = 0.1 },
      { act = function(p) p.face = 1; love.keypressed("z") end }, { wait = 0.6 },
      { act = function() local s = api.stage(); report("cat: a bark from far away does not scare it", s.cat.state == "sit" and s.ball.state == "cat", s.cat.state) end },
      { act = function() local s = api.stage(); tp(1170, 184) end }, { wait = 0.1 },
      { act = function() love.keypressed("x") end }, { wait = 0.2 },
      { act = function(p) local s = api.stage(); report("cat: the ball cannot be picked up under it", s.ball.state == "cat" and not p.carrying, s.ball.state) end },
      { wait = 0.4 }, { act = function(p) p.face = 1; love.keypressed("z") end }, { wait = 0.1 },
      { act = function() local s = api.stage(); report("cat: a bark from the street under the arm scares it", s.cat.state ~= "sit", s.cat.state) end },
      { during = 1.5 },
      { act = function() local s = api.stage(); local b = s.ball
          report("cat: the ball drops to the street", b.state == "rest" and near(b.y, 184), ("ball %s x %.0f y %.0f"):format(b.state, b.x, b.y)) end },
      { during = 2.0 },
      { act = function() local s = api.stage(); report("cat: it runs off and is gone", s.cat.state == "gone", s.cat.state) end },
      { act = function() local b = api.stage().ball; tp(b.x - 18, 184); api.stage().pepper.face = 1 end }, { wait = 0.1 },
      { act = function() love.keypressed("x") end }, { wait = 0.2 },
      { act = function(p) report("ball: Pepper picks it up", p.carrying ~= nil, tostring(p.carrying ~= nil)) end },
      -- 7 carrying the ball: every move still works (crawl under a table, a held jump onto the kiosk)
      { act = function() tp(340, 184); carry(); hold("right", "down") end }, { during = 3.0 },
      { act = function(p) release(); report("ball: crawl under a table carrying it", p.x > 420 and near(p.y, 184) and p.carrying ~= nil, ("x %.0f"):format(p.x)) end },
      { act = function() tp(1620, 184); carry(); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("ball: a held jump onto the kiosk carrying it", near(p.y, 148) and p.carrying ~= nil, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 8 the fountain: a hop onto the rim, onto the bowl, onto the far rim; falling in costs a heart, and the
      --   ball goes back by the statue
      { act = function() tp(1370, 184); hold("right") end }, { during = 0.05 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 3 },
      { act = function(p) report("fountain: a tapped hop onto the rim", near(p.y, 168) and p.x < 1430, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1408, 168); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.25 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("fountain: a jump from the rim onto the bowl", near(p.y, 160), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1472, 160); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.25 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("fountain: a jump from the bowl onto the far rim", near(p.y, 168) and p.x > 1515, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1404, 168); hold("right") end }, { during = 0.15 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) release(); report("fountain: a running tapped hop from rim to bowl", near(p.y, 160), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1436, 168); carry(); hearts = api.stage().hearts end }, { during = 2.5 },
      { act = function(p) local s = api.stage(); local b = s.ball
          report("fountain: falling in costs a heart", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts))
          report("fountain: the ball goes back by the statue", b.state == "rest" and near(b.x, b.home.x) and b.x < 1300 and not p.carrying,
            ("ball %s x %.0f y %.0f"):format(b.state, b.x, b.y)) end },
      -- 9 the tram: it hurts on the street; on the kiosk and on the shelter roof it passes under Pepper
      { act = function() tp(1620, 184); hearts = api.stage().hearts; tram(1720) end },
      { during = 2.0 },
      { act = function() local s = api.stage(); report("tram: hurts Pepper on the street", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { act = function() tp(1620, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); local s = api.stage(); hearts = s.hearts
          report("kiosk: a held jump lands on top", near(p.y, 148), ("x %.0f y %.0f"):format(p.x, p.y)); tram(p.x + 120) end },
      { during = 2.5 },
      { act = function(p) local s = api.stage(); report("kiosk: safe from the tram", near(p.y, 148) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts)) end },
      { act = function() tp(1672, 148); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.2 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) local s = api.stage(); hearts = s.hearts
          report("shelter: a jump from the kiosk onto the roof", near(p.y, 136), ("x %.0f y %.0f"):format(p.x, p.y)); tram(p.x + 120) end },
      { during = 2.5 },
      { act = function(p) local s = api.stage(); report("shelter: safe from the tram", near(p.y, 136) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts)) end },
      { act = function() tp(1660, 184); tram(1900) end }, { during = 0.5 },
      { act = function() local c = api.stage().bikes[1]; report("tram: stays on its rail over the stairs", c and near(c.y, 184), c and ("x %.0f y %.0f"):format(c.x, c.y) or "none") end },
      -- 10 the stairs down to the river: without the ball they do not end the level, with it they do
      { act = function() local s = api.stage(); s.ball.state = "rest"; s.pepper.carrying = nil; tp(1840, 184); hold("right") end },
      { wait = 3.0 },
      { act = function() release(); report("exit: without the ball it does not clear", api.getState() == "play" and not api.stage().clearT, api.getState()) end },
      { act = function() tp(1840, 184); carry(); hold("right") end }, { wait = 3.0 },
      { act = function() release(); local st = api.stage():stats()
          report("exit: with the ball it clears (+1000 BALL)", api.getState() == "clear" and st.bonus and st.bonus[1] == "BALL" and st.bonus[2] == 1000, api.getState()) end },
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
      -- 1 old town lane: a hop onto each crate
      at(function(p) return p.x >= 106 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 138 end, function() release() end),                        -- brake in the air
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      at(function(p) return p.x >= 152 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end),
      -- 2 cafe terrace: onto the first table, its parasol, the second parasol, the shop sign (gold bone)
      at(function(p) return p.x >= 322 and p.onGround and p.y > 183 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 159 end, function() release() end),
      at(function(p) return math.abs(p.vx) < 1 end, function() jump("jump") end),
      at(function(p) return p.onGround and p.y <= 115 end, function() hold("left") end),
      at(function(p) return p.x <= 372 end, function() hold("right") end),
      at(function(p) return p.x >= 412 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 115 and p.x > 472 end, function() hold("right") end),
      at(function(p) return p.x >= 518 end, function() jump("right", "jump") end),
      at(function(p) return p.vy > 0 and p.x >= 560 end, function() release() end),
      at(function(p) return p.onGround and p.y <= 81 end, function() hold("right") end),
      at(function(p) return p.x >= 604 end, function() release() end),                         -- off the sign, brake
      at(function(p) return p.onGround and p.y >= 183 end, function() hold("right") end),
      -- 3 market: onto the stall, its awning, down, the crates, the second awning
      at(function(p) return p.x >= 652 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() release() end),
      at(function(p) return p.x >= 714 or math.abs(p.vx) < 1 end, function() jump("jump") end),
      at(function(p) return p.onGround and p.y <= 117 end, function() hold("right") end),
      at(function(p) return p.x >= 766 end, function() release() end),                         -- off the awning, brake
      at(function(p) return p.onGround and p.y >= 183 end, function() hold("right") end),
      at(function(p) return p.x >= 774 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 800 end, function() release() end),                         -- brake in the air
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      at(function(p) return p.x >= 808 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end),
      at(function(p) return p.x >= 846 end, function() jump("right", "jump") end),
      at(function(p) return p.vy > 0 end, function() release() end),
      at(function(p) return p.onGround and p.y <= 113 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 end, function() hold("right") end),
      -- 4 the plaza: onto the pedestal, bark the cat off, up the arm to the hat (gold bone), down, pick up the ball
      at(function(p) return p.x >= 1092 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 145 end, function() release() end),
      at(function(p) return math.abs(p.vx) < 1 end, function() love.keypressed("z") end),
      { wait = 0.6 },
      at(function(p, s) return s.ball.state == "rest" end, function() hold("right") end),
      at(function(p) return p.x >= 1150 end, function() jump("right", "jump") end),
      at(function(p) return p.x >= 1168 end, function() hold("jump") end),                    -- brake in the air
      at(function(p) return p.onGround and p.y <= 109 end, function() hold("left") end),
      at(function(p) return p.x <= 1166 end, function() release() end),
      { wait = 0.25 }, { act = function() jump("jump") end },
      at(function(p) return p.onGround and p.y <= 77 end, function() release() end),
      { wait = 0.2 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y >= 183 end, function() release() end, 9),
      at(function(p, s)                                                                       -- walk up to the ball
        local b = s.ball
        local want = p.x < b.x and 1 or -1                                                    -- face the ball
        if p.face == want and math.abs(p.x + p.face * 18 - b.x) < 20 and math.abs(p.vx) < 1 then return true end
        local tx = b.x - want * 18
        if p.face ~= want then hold(want > 0 and "right" or "left", "walk")
        elseif p.x < tx - 3 then hold("right", "walk") elseif p.x > tx + 3 then hold("left", "walk") else release() end
        return false
      end, function() release() end),
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.6 },
      -- 5 the fountain with the ball: onto the rim, the bowl, the far rim
      at(function(p) return p.carrying ~= nil end, function() hold("right") end, 2),
      at(function(p) return p.x >= 1374 end, function() jump("right", "jump") end, 9),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      at(function(p) return p.x >= 1410 end, function() jump("right", "jump") end),                -- tapped hops
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 161 end, function() hold("right") end),
      at(function(p) return p.x >= 1478 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 and p.x > 1515 end, function() hold("right") end),
      -- 6 tram street: onto the kiosk, onto the shelter roof, wait there for the tram to pass, down the stairs
      at(function(p) return p.x >= 1622 and p.onGround and p.y > 183 end, function() jump("right", "jump") end, 9),
      at(function(p) return p.onGround and p.y <= 149 end, function() hold("right") end),
      at(function(p) return p.x >= 1672 end, function() jump("right", "jump") end),
      at(function(p) return p.vy > 0 end, function() release() end),
      at(function(p) return p.onGround and p.y <= 137 end, function() release() end),
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 60 end, function() hold("right") end, 12),
      at(function() return api.getState() == "clear" end, function() release() end, 9),
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, lives %d hearts %d, %.1f s played"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    }
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("dt_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    -- one shot per screen (camera on the screen's left edge), Pepper standing in it
    local spots = { { 60, 184 }, { 340, 184 }, { 650, 184 }, { 1060, 184 }, { 1340, 184 }, { 1668, 148 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      if i == 6 then steps[#steps + 1] = { act = function() tram(1860) end } end
      steps[#steps + 1] = { wait = i == 6 and 0.6 or 0.6 }
      steps[#steps + 1] = shot(("dt_%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    -- the cat beat: bark from the pedestal, the cat startles, leaps off, runs; the ball on the street; pick it up
    local beatCam = 1010
    steps[#steps + 1] = { act = function() tp(1146, 144); api.stage().pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.5 }; steps[#steps + 1] = shot("dt_07_cat", beatCam)
    steps[#steps + 1] = { act = function() love.keypressed("z") end }
    steps[#steps + 1] = { wait = 0.15 }; steps[#steps + 1] = shot("dt_08_bark", beatCam)
    steps[#steps + 1] = { wait = 0.4 }; steps[#steps + 1] = shot("dt_09_leap", beatCam)
    steps[#steps + 1] = { wait = 0.5 }; steps[#steps + 1] = shot("dt_10_run", beatCam)
    steps[#steps + 1] = { wait = 1.5 }; steps[#steps + 1] = shot("dt_11_ball", beatCam)
    steps[#steps + 1] = { act = function() local b = api.stage().ball; tp(b.x - 18, 184); api.stage().pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.2 }; steps[#steps + 1] = { act = function() love.keypressed("x") end }
    steps[#steps + 1] = { wait = 0.3 }; steps[#steps + 1] = shot("dt_12_pickup", beatCam)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }; steps[#steps + 1] = { wait = 0.1 }
    steps[#steps + 1] = shot("dt_13_debug_screen4", 960)
    steps[#steps + 1] = { act = function() tp(1472, 160) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("dt_14_debug_screen5", 1280)
    steps[#steps + 1] = { act = function() tp(1668, 148) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("dt_15_debug_screen6", 1600)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }
    -- down the stairs with the ball: the tally
    steps[#steps + 1] = { act = function() carry(); tp(1830, 184); I.force = { right = true } end }
    steps[#steps + 1] = { wait = 0.8 }; steps[#steps + 1] = shot("dt_16_exit")
    steps[#steps + 1] = { act = function() I.force = {} end }
    steps[#steps + 1] = { wait = 4.5 }; steps[#steps + 1] = shot("dt_17_tally")
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
        if os.getenv("AUTO_DEBUG") then print(("step %d at x %.1f y %.1f vx %.0f %s"):format(i, p.x, p.y, p.vx, p.onGround and "G" or "A")) end
        st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
