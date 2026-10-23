-- The checks for Level 2, Downtown (love riverwalk --level downtown <flag>). Same flags as tests_citypark.lua:
--   --physics   checks every set piece: hop, held jump, crates, cafe tables and parasols, the shop sign, market
--               stall and awnings, the statue, the cat and the ball, the fountain, the tram, the girl
--   --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
--   --test      a screenshot tour of the 11 screens, the cat beat, the tram, a bounce, the geese, the canal, the
--               debug view and the tally
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
          report("the perches are above the cargo bike's box", tops[1] < 184 - tram.h and tops[2] < 184 - tram.h, ("kiosk %d, shelter %d, box top %d"):format(tops[1], tops[2], 184 - tram.h))
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
      { act = function() tp(350, 184); hold("right") end }, { during = 1.0 },
      { act = function(p) report("table: stops a walk", p.x < 352, ("x %.0f"):format(p.x)); hold("right", "down") end },
      { during = 6.0 },
      { act = function(p) release(); report("tables: crawling passes under both", p.x > 545 and near(p.y, 184), ("x %.0f"):format(p.x)) end },
      { act = function() tp(350, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("table: a held jump lands on the top", near(p.y, 158), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- (r6/levels) the crate splits the jump: a tap hop onto it, a tap hop from it onto the table
      { act = function() tp(262, 184); hold("right") end }, { during = 0.15 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end }, { during = 0.1 }, landed(),
      { act = function(p) release(); report("terrace crate: a tapped hop onto it", near(p.y, 168), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(312, 168); hold("right") end }, { during = 0.12 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end }, { during = 0.1 },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 3 },
      { act = function(p) report("terrace crate: a tapped hop from it onto the table", near(p.y, 158), ("x %.0f y %.0f"):format(p.x, p.y)) end },
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
      -- the flower tub before the pedestal (28 px): a tapped hop and a scramble, then a hop onto the pedestal
      { act = function() tp(1370, 184); hold("right") end }, { during = 0.2 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.onGround and p.mode == "normal" and p.y < 183 end, act = function() release() end, limit = 2 },
      { act = function(p) report("tub: a tapped hop and a scramble onto it", near(p.y, 156) and p.x < 1442, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1420, 156); hold("right") end }, { during = 0.05 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) release(); report("pedestal: a tapped hop from the tub onto it", near(p.y, 144), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1380, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("pedestal: a held jump from the street gets up", p.y <= 156.5, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1478, 144); jump("right", "jump") end }, { during = 0.15 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("arm: a held jump from the pedestal onto it", near(p.y, 108), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1482, 108); jump("jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("hat: a held jump from the arm onto it", near(p.y, 76), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 6 the cat: a far bark only makes it look up; the ball cannot be picked up under it; a bark from the street
      --   under the arm scares it, the ball drops to the street, the cat runs off; Pepper picks the ball up
      { act = function() tp(1380, 184) end }, { wait = 0.1 },
      { act = function(p) p.face = 1; love.keypressed("z") end }, { wait = 0.6 },
      { act = function() local s = api.stage(); report("cat: a bark from far away does not scare it", s.cat.state == "sit" and s.ball.state == "cat", s.cat.state) end },
      { act = function() local s = api.stage(); tp(1490, 184) end }, { wait = 0.1 },
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
      { act = function() tp(1959, 184); carry(); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); report("ball: a held jump onto the kiosk carrying it", near(p.y, 148) and p.carrying ~= nil, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 8 the fountain: a hop onto the rim, onto the bowl, onto the far rim; falling in costs a heart, and the
      --   ball goes back by the statue
      { act = function() tp(1690, 184); hold("right") end }, { during = 0.05 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 3 },
      { act = function(p) report("fountain: a tapped hop onto the rim", near(p.y, 168) and p.x < 1750, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1728, 168); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.25 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("fountain: a jump from the rim onto the bowl", near(p.y, 160), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1792, 160); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.25 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) report("fountain: a jump from the bowl onto the far rim", near(p.y, 168) and p.x > 1835, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1724, 168); hold("right") end }, { during = 0.15 },
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },
      { during = 0.1 }, landed(),
      { act = function(p) release(); report("fountain: a running tapped hop from rim to bowl", near(p.y, 160), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(1756, 168); carry(); hearts = api.stage().hearts end }, { during = 2.5 },
      { act = function(p) local s = api.stage(); local b = s.ball
          report("fountain: falling in costs a heart", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts))
          report("fountain: the ball goes back home (statue or lamp)", b.state == "rest" and near(b.x, b.home.x) and b.x < 1990 and not p.carrying,
            ("ball %s x %.0f y %.0f"):format(b.state, b.x, b.y)) end },
      -- 9 the tram: it hurts on the street; on the kiosk and on the shelter roof it passes under Pepper
      { act = function() tp(1959, 184); hearts = api.stage().hearts; tram(2040) end },
      { during = 2.0 },
      { act = function() local s = api.stage(); report("cargo bike: hurts Pepper on the street", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { act = function() tp(1959, 184); jump("right", "jump") end }, { during = 0.2 }, landed(),
      { act = function(p) release(); local s = api.stage(); hearts = s.hearts
          report("kiosk: a held jump lands on top", near(p.y, 148), ("x %.0f y %.0f"):format(p.x, p.y)); tram(p.x + 120) end },
      { during = 2.5 },
      { act = function(p) local s = api.stage(); report("kiosk: safe from the cargo bike", near(p.y, 148) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts)) end },
      { act = function() tp(2004, 148); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.2 },
      { cond = function(p) return p.vy > 0 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) local s = api.stage(); hearts = s.hearts
          report("shelter: a jump from the kiosk onto the roof", near(p.y, 136), ("x %.0f y %.0f"):format(p.x, p.y)); tram(p.x + 120) end },
      { during = 2.5 },
      { act = function(p) local s = api.stage(); report("shelter: safe from the cargo bike", near(p.y, 136) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts)) end },
      { act = function() tp(1980, 184); tram(2220) end }, { during = 0.5 },
      { act = function() local c = api.stage().bikes[1]; report("cargo bike: stays on its rail over the stairs", c and near(c.y, 184), c and ("x %.0f y %.0f"):format(c.x, c.y) or "none") end },
      -- 10 the rooftops (the high route): from the statue's arm along the balconies and the fountain's top tier,
      --    carrying the ball, down to the street by the lamp before tram street
      { act = function() tp(1500, 108); carry(); hold("right") end },
      { cond = function(p) return p.x >= 1514 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("rooftops: from the arm onto the first balcony", near(p.y, 104) and p.x > 1545, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 1604 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("rooftops: onto the second balcony", near(p.y, 96) and p.x > 1650, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 1708 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("rooftops: onto the fountain's top tier (gold)", near(p.y, 104) and p.x > 1760, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 1812 end, act = function() jump("right", "jump") end, limit = 2 }, { during = 0.2 }, landed(),
      { act = function(p) report("rooftops: onto the last balcony", near(p.y, 104) and p.x > 1835, ("x %.0f y %.0f"):format(p.x, p.y)); hold("right") end },
      { cond = function(p) return p.x >= 1905 end, act = function() release() end, limit = 2 }, landed(),
      { act = function(p) local s = api.stage()
          report("rooftops: down to the street, ball still carried", (near(p.y, 184) or near(p.y, 148)) and p.x > 1866 and p.carrying ~= nil, ("x %.0f y %.0f"):format(p.x, p.y))
          report("secret: ROOFTOPS counted", s.secrets[3].found, ("%d of %d"):format(s:stats().secrets, s:stats().secretsTotal)) end },
      -- the other two secrets: the shop sign and the statue's hat (reached by the climbs checked above)
      { act = function() local s = api.stage()
          report("secrets: SHOP SIGN and STATUE HAT counted (of 4)", s.secrets[1].found and s.secrets[2].found and s:stats().secrets == 3 and s:stats().secretsTotal == 4,
            ("%d of %d"):format(s:stats().secrets, s:stats().secretsTotal)) end },
      -- the tram sets off when Pepper walks into its zone, its front 1 s from the screen edge
      { act = function() tp(1910, 184); hold("right") end },
      { cond = function(p, s) return #s.bikes > 0 end, act = function(p, s) release(); local c = s.bikes[1]
          local lead = (c.x - 40 - (s.cam + 320)) / c.speed
          report("cargo bike: sets off as Pepper enters its zone", p.x > 1930 and p.x < 1945, ("x %.0f"):format(p.x))
          report("cargo bike: 1 s from the screen edge (bell)", math.abs(lead - 1) < 0.05, ("%.2f s"):format(lead)) end, limit = 2 },
      { act = function() local St = require("stage"); local h = St.new(api.stage().def, { hard = true })
          report("hard mode: 1 heart, the cargo bike 25% faster", h.hearts == 1 and Sp.speed(h, h.def.bikes[1]) == h.def.bikes[1].speed * 1.25,
            ("hearts %d, speed %.1f"):format(h.hearts, Sp.speed(h, h.def.bikes[1]))) end },
      -- 12 the springy awnings and parasol (bounce), the geese, the canal, the second tram
      { act = function() tp(1076, 184); hold("right") end }, { during = 0.1 }, { act = function() jump("right", "jump") end }, { during = 1.6 },
      { act = function(p) release(); report("bakery: the crates (64 px) stop a jump and scramble", p.x < 1104 and near(p.y, 184), ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() tp(984, 184); hold("right") end }, { cond = function(p) return p.x >= 992 end, act = function() jump("right", "jump") end, limit = 2 },
      { cond = function(p) return p.vy < -260 end, act = function(p) minY = p.y end, limit = 2 },
      { during = 1.2, each = function(p) minY = math.min(minY, p.y) end }, landed(),
      { act = function(p) release(); report("bakery: the awning launches her 76 px, over the crates", p.x > 1104 and 152 - minY >= 74 and 152 - minY <= 78, ("up %.0f px, x %.0f y %.0f"):format(152 - minY, p.x, p.y)) end },
      { act = function() tp(1040, 140); local p = api.stage().pepper; p.onGround = false; hold("down") end }, { during = 0.6 },
      { act = function(p) release(); report("bakery: holding Down she stands on the awning", p.onGround and near(p.y, 152), ("y %.0f"):format(p.y)) end },
      { act = function() tp(1200, 184); hold("right") end }, { cond = function(p) return p.x >= 1210 end, act = function() jump("right", "jump") end, limit = 2 },
      { cond = function(p) return p.vy < 0 and p.y < 140 and p.x >= 1266 end, act = function() hold("jump") end, limit = 3 }, landed(),
      { act = function(p) release(); local s = api.stage(); report("bakery: the second awning reaches the sign (gold)", near(p.y, 64) and s.secrets[4].found, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() local s = api.stage(); local k = s.critters[1]; k.state, k.x, k.y, k.dir, k.t = "walk", 2230, 184, -1, 0
          s.hearts = 3; hearts = 3; tp(2160, 184); carry(); s.pepper.face = 1; hold("right") end }, { during = 2.0 },
      { act = function(p) release(); local s = api.stage(); report("geese: a bite knocks the ball out (no heart: r6/engine)", s.hearts == hearts and not p.carrying, ("hearts %d, carrying %s"):format(s.hearts, tostring(p.carrying ~= nil))) end },
      { act = function() local s = api.stage(); for _, k in ipairs(s.critters) do k.state, k.y = "gone", -999 end; tp(2300, 156); carry() end }, { wait = 0.2 },
      { act = function() hold("right") end }, { cond = function(p) return p.x >= 2306 end, act = function() jump("right", "jump") end, limit = 2 },
      { during = 0.3 }, { cond = function(p) return p.onGround and p.mode == "normal" and p.y < 100 end, act = function() end, limit = 3 },
      { act = function(p) release(); report("market: tub, parasol bounce, up onto the balcony", near(p.y, 88) and p.x > 2407 and p.carrying ~= nil, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() local s = api.stage(); s.hearts = 3; hearts = 3; tp(2476, 88); hold("right") end }, { during = 0.4 },
      { cond = function(p) return p.onGround and p.mode == "normal" and p.y <= 121 end, act = function() end, limit = 3 },
      { act = function(p) release(); report("canal: off the balcony, the awning launches her onto the crates", near(p.y, 120) and p.x > 2611 and p.carrying ~= nil, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      { act = function() local s = api.stage(); s.lamps[5].lit = false; tp(2520, 184); carry() end }, { wait = 0.1 },
      { act = function() hold("right") end }, { during = 1.5 },
      { cond = function(p, s) return s.ball.state == "rest" and not s.drownT and not s.deadT end, act = function() end, limit = 4 },
      { act = function(p) release(); local s = api.stage(); local b = s.ball
          report("canal: walking in drowns; the ball is back by the lamp", s.hearts == hearts - 1 and near(b.x, 2552) and b.state == "rest", ("hearts %d, ball %s x %.0f"):format(s.hearts, b.state, b.x)) end },
      { act = function() local s = api.stage(); s.hearts = 3; hearts = 3; tp(2802, 168) end }, { wait = 0.2 },
      { act = function() jump("right", "jump") end },
      { cond = function(p) return p.onGround and p.mode == "normal" and p.x > 3072 end, act = function() release() end, limit = 6 },
      { act = function(p) release(); local s = api.stage()
          report("flooded square: holding Right she bounces across, onto the courtyard gate", near(p.y, 148) and s.hearts == hearts, ("x %.0f y %.0f hearts %d"):format(p.x, p.y, s.hearts)) end },
      { act = function() local s = api.stage(); s.hearts = 3; hearts = 3; tp(2770, 184); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 2.5 },
      { act = function(p) release(); local s = api.stage()
          report("flooded square: from the street a jump can't reach a parasol", s.hearts == hearts - 1 or (p.y >= 167 and p.x < 2832), ("x %.0f y %.0f hearts %d"):format(p.x, p.y, s.hearts)) end },
      { cond = function(p, s) return not s.drownT and not s.deadT end, act = function() end, limit = 3 },
      { act = function() local s = api.stage(); s.lamps[6].lit = false; s.hearts = 3; hearts = 3; tp(2770, 184); carry() end }, { wait = 0.1 },
      { act = function() local p = api.stage().pepper; p.x, p.y, p.onGround = 2900, 170, false end }, { during = 2.5 },
      { cond = function(p, s) return s.ball.state == "rest" and not s.drownT and not s.deadT end, act = function() end, limit = 4 }, { wait = 1.0 },
      { act = function() local s = api.stage(); local b = s.ball
          report("flooded square: a ball lost there rests by the lamp (pickable)", b.state == "rest" and not s:ballLost() and math.abs(b.x - 2764) <= 24, ("ball %s x %.0f"):format(b.state, b.x)) end },
      -- the trams end in their sheds: tram 2 never drives over the flooded square
      { act = function() local s = api.stage(); tp(3270, 136); s.bikes = { { x = 3420, y = 184, warn = 0, zone = s.def.bikes[2], speed = 130 } }; s.bikeT = 99; s.zoneIn[s.def.bikes[2]] = true; minY = 9999 end },
      { during = 3.0, each = function(p) local c = api.stage().bikes[1]; if c then minY = math.min(minY, c.x + 52) end end },
      { act = function() local s = api.stage()
          report("cargo bike 2: drives into its courtyard (gone past the gateway), not over the water", #s.bikes == 0 and minY <= 3168 + 2 and minY >= 3150, ("its back end reached x %.0f (door 3168)"):format(minY)) end },
      { act = function() local z1, z2 = api.stage().def.bikes[1], api.stage().def.bikes[2]
          local tops = { prop("GATE", 2).y0, prop("SHELTER", 2).y0 }
          report("cargo bike 2: faster and more often; its perches are above it", z2.speed > z1.speed and z2.every < z1.every and tops[1] < 184 - z2.h and tops[2] < 184 - z2.h,
            ("speed %d, every %.1f s"):format(z2.speed, z2.every)) end },
      -- 11 the girl at the stairs: reaching her without the ball does nothing, giving her the ball clears
      { act = function() local s = api.stage(); s.ball.state = "rest"; s.pepper.carrying = nil; tp(2120, 184); hold("right") end },
      { wait = 3.0 },
      { act = function() release(); report("girl: without the ball the level goes on", api.getState() == "play" and not api.stage().clearT, api.getState()) end },
      { act = function() local s = api.stage(); carry(); tp(s.girl.x - 30, 184); s.pepper.face = 1 end }, { wait = 0.1 },
      { act = function() love.keypressed("x") end }, { wait = 3.0 },
      { act = function() local st = api.stage():stats()
          report("girl: giving her the ball clears (FETCH 2000)", api.getState() == "clear" and st.bonus and st.bonus[1] == "FETCH", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
    require("tests_safety")(steps, api, report)                  -- the safety nets (r6/engine), before the summary
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
      at(function(p) return p.x >= 270 and p.onGround and p.y > 183 end, function() jump("right", "jump") end),   -- the crate (r6/levels)
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      at(function(p) return p.x >= 318 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
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
      -- 4 the bakery row: onto the springy awning, launched over the crates; the second awning up to the sign
      at(function(p) return p.onGround and p.y >= 183 and p.x >= 960 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.x > 1100 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 end, function() hold("right") end),
      at(function(p) return p.x >= 1204 end, function() jump("right", "jump") end),
      at(function(p) return p.vy < 0 and p.y < 140 and p.x >= 1266 end, function() hold("jump") end),   -- brake in the air
      at(function(p) return p.onGround and p.y <= 65 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 end, function() hold("right") end),
      -- 5 the plaza: onto the pedestal, bark the cat off, up the arm to the hat (gold bone), down, pick up the ball
      at(function(p) return p.x >= 1380 end, function() jump("right", "jump") end),             -- over the tub
      at(function(p) return p.onGround and p.y <= 145 end, function() release() end),
      at(function(p) return math.abs(p.vx) < 1 end, function() love.keypressed("z") end),
      { wait = 0.6 },
      at(function(p, s) return s.ball.state == "rest" end, function() hold("right") end),
      at(function(p) return p.x >= 1470 end, function() jump("right", "jump") end),
      at(function(p) return p.x >= 1488 end, function() hold("jump") end),                    -- brake in the air
      at(function(p) return p.onGround and p.y <= 109 end, function() hold("left") end),
      at(function(p) return p.x <= 1486 end, function() release() end),
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
      at(function(p) return p.x >= 1694 end, function() jump("right", "jump") end, 9),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end),
      at(function(p) return p.x >= 1730 end, function() jump("right", "jump") end),                -- tapped hops
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 161 end, function() hold("right") end),
      at(function(p) return p.x >= 1798 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 and p.x > 1835 end, function() hold("right") end),
      -- 7 tram street: a hop from the rim onto the tram shed's roof, on to the kiosk and the shelter roof, wait
      --   there for the tram to pass
      at(function(p) return p.x >= 1850 end, function() jump("right") end, 9),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 149 end, function() hold("right") end),             -- the shed roof
      at(function(p) return p.x >= 1926 end, function() jump("right") end),                      -- a hop
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 1990 end, function() release() end),
      at(function(p) return p.onGround and p.y <= 149 and p.x > 1966 end, function() hold("right") end),     -- the kiosk
      at(function(p) return p.x >= 2004 end, function() jump("right", "jump") end),
      at(function(p) return p.vy > 0 end, function() release() end),
      at(function(p) return p.onGround and p.y <= 137 end, function() release() end),
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 60 end, function() hold("right") end, 12),
      -- 8 the flower market, carrying the ball: bark the first goose off, then the high route: the tub, the table,
      --   the springy parasol, the balcony; off the balcony onto the canal's awning, which launches her over
      at(function(p, s) local k = s.critters[1]; return p.onGround and p.y >= 183 and (k.state == "gone" or k.x - p.x < 76) end, function() release(); love.keypressed("z") end, 9),
      { wait = 0.5 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 2256 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 157 end, function() hold("right") end),
      at(function(p) return p.x >= 2306 end, function() jump("right", "jump") end),           -- onto the parasol: up
      at(function(p) return p.onGround and p.y <= 89 end, function() hold("right") end),     -- the balcony
      -- 9 the canal: off the balcony onto the awning, launched over the water onto the crates, down
      at(function(p) return p.onGround and p.y <= 121 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= 183 end, function() hold("right") end),
      -- 10 the flooded square: onto the crate, a held jump onto the first parasol, then hold Right: bounce, bounce,
      --    bounce, out onto the far side
      at(function(p) return p.x >= 2770 end, function() jump("right") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 end, function() release() end),
      at(function(p) return math.abs(p.vx) < 1 end, function() jump("right", "jump") end),
      -- 11 tram street again: the last bounce lands on the tram shed; wait for the fast tram, on over the shelter roof
      at(function(p) return p.onGround and p.y <= 149 and p.x > 3060 end, function() release() end, 9),
      at(function(p, s) return s.bikes[1] ~= nil end, function() end, 12),                   -- the tram comes, and
      at(function(p, s) return s.bikes[1] == nil end, function() hold("right") end, 12),      -- drives into its shed
      at(function(p) return p.x >= 3162 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 137 end, function() release() end),            -- the shelter roof
      at(function(p, s) return #s.bikes == 0 end, function() end, 12),                           -- the next tram
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 60 end, function() hold("right") end, 12),
      at(function(p, s) return p.onGround and p.y >= 183 and p.x >= s.girl.x - 40 end, function() release() end, 9),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      at(function() return api.getState() == "clear" end, function() end, 9),
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played%s"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time, s.hard and " (hard)" or "")); io.stdout:flush()
          love.event.quit() end },
    }
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("dt_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    -- one shot per screen (camera on the screen's left edge), Pepper standing in it
    local spots = { { 60, 184 }, { 340, 184 }, { 650, 184 }, { 990, 184 }, { 1380, 184 }, { 1690, 184 }, { 1988, 148 },
      { 2296, 156 }, { 2802, 168 }, { 3148, 148 }, { 3260, 136 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      if i == 7 then steps[#steps + 1] = { act = function() tram(2180) end } end
      steps[#steps + 1] = { wait = 0.6 }
      steps[#steps + 1] = shot(("dt_%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    -- the cat beat: bark from the pedestal, the cat startles, leaps off, runs; the ball on the street; pick it up
    local beatCam = 1330
    steps[#steps + 1] = { act = function() tp(1466, 144); api.stage().pepper.face = 1 end }
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
    steps[#steps + 1] = shot("dt_13_debug_screen5", 1280)
    steps[#steps + 1] = { act = function() tp(1792, 160) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("dt_14_debug_screen6", 1600)
    steps[#steps + 1] = { act = function() tp(1988, 148) end }; steps[#steps + 1] = { wait = 0.3 }
    steps[#steps + 1] = shot("dt_15_debug_screen7", 1920)
    steps[#steps + 1] = { act = function() love.keypressed("g") end }
    -- the new spots: the tub before the pedestal, the rooftop route, the tram's warning sign
    local function add(t) for _, st in ipairs(t) do steps[#steps + 1] = st end end
    add({ { act = function() tp(1424, 156) end }, { wait = 0.4 }, shot("dt_18_tub", 1310),
          { act = function() tp(1792, 104); carry() end }, { wait = 0.4 }, shot("dt_19_rooftops", 1580),
          { act = function() local s = api.stage(); s.pepper.carrying = nil; s.ball.state = "rest"; tp(1988, 148); s.bikes = { Sp.spawn(s, s.def.bikes[1]) } end },
          { wait = 0.1 }, shot("dt_20_cargo_warning", 1920) })
    -- the new screens: a bounce off the bakery awning, the geese, the flight over the canal
    add({ { act = function() local s = api.stage(); s.bikes = {}; tp(992, 184); hold("right") end }, { wait = 0.05 }, { act = function() jump("right", "jump") end },
          { cond = function(p) return p.vy < -200 and p.y < 140 end, act = function() end, limit = 3 }, { wait = 0.15 }, shot("dt_21_bounce", 960),
          { act = function() release(); tp(2150, 184) end }, { wait = 0.8 }, shot("dt_22_geese", 2136),
          { act = function() local s = api.stage(); for _, k in ipairs(s.critters) do k.state, k.y = "gone", -999 end; tp(2476, 88); carry(); hold("right") end },
          { cond = function(p) return p.vy < -100 and p.x > 2520 end, act = function() end, limit = 3 }, { wait = 0.25 }, shot("dt_23_canal", 2460),
          { act = function() release(); local s = api.stage(); s.pepper.carrying = nil; s.ball.state = "rest" end } })
    -- the trams drive into their sheds (Pepper on the shed roofs)
    add({ { act = function() local s = api.stage(); tp(1904, 148); s.zoneIn[s.def.bikes[1]] = true; s.bikes = { { x = 2010, y = 184, warn = 0, zone = s.def.bikes[1], speed = 110 } }; s.bikeT = 99 end },
          { wait = 0.45 }, shot("dt_24_gate1", 1780),
          { act = function() local s = api.stage(); tp(3110, 148); s.zoneIn[s.def.bikes[2]] = true; s.bikes = { { x = 3240, y = 184, warn = 0, zone = s.def.bikes[2], speed = 130 } }; s.bikeT = 99 end },
          { wait = 0.45 }, shot("dt_25_gate2", 2990), { act = function() api.stage().bikes = {} end } })
    -- give the girl the ball: the tally
    steps[#steps + 1] = { act = function() local s = api.stage(); carry(); tp(s.girl.x - 30, 184); s.pepper.face = 1 end }
    steps[#steps + 1] = { wait = 0.2 }; steps[#steps + 1] = { act = function() love.keypressed("x") end }
    steps[#steps + 1] = { wait = 0.8 }; steps[#steps + 1] = shot("dt_16_give")
    steps[#steps + 1] = { wait = 4.5 }; steps[#steps + 1] = shot("dt_17_tally")
    steps[#steps + 1] = { wait = 0.3 }; steps[#steps + 1] = { act = function() love.event.quit() end }
  end

  local i, since, T, lastHearts, lastBikes = 1, 0, 0, nil, nil
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; T = T + dt; since = since + dt
    old(dt)
    local s = api.stage(); local p = s and s.pepper
    if mode == "--auto" then
      frame = frame + 1
      if s and s.hearts ~= (lastHearts or s.maxHearts) then print(("  lost a heart at x %.0f y %.0f (step %d)%s"):format(p.x, p.y, i, s.bikes[1] and (" cargo bike at %.0f"):format(s.bikes[1].x) or "")) end
      lastHearts = s and s.hearts
      if os.getenv("AUTO_DEBUG") and s and #s.bikes ~= (lastBikes or 0) then print(("  bikes %d: pepper x %.0f cam %.0f bike x %s"):format(#s.bikes, p.x, s.cam, s.bikes[1] and ("%.0f"):format(s.bikes[1].x) or "-")) end
      lastBikes = s and #s.bikes
      if os.getenv("AUTO_TRACE") and p and p.x > tonumber(os.getenv("AUTO_TRACE")) and frame % 6 == 0 then print(("    f%d x %.0f y %.0f vx %.0f %s %s"):format(frame, p.x, p.y, p.vx, p.mode, p.anim or "")) end
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
