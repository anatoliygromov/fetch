-- The checks for Level 5, Night Harbour (love riverwalk --level night <flag>). Same flags as tests.lua:
--   --physics   the darkness, sniffing (Pepper stops, the trail points at the right hideout), the fox's hideouts
--               and bark range, crumbling planks (timing, falling, coming back), the water gaps, the rowboats,
--               the crawl under the low jetty, the climbs, giving Mia the ball
--   --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
--   --test      a screenshot tour of the 14 screens, sniffing, the fox, the planks, the tally
local I = require("input")
local Pp = require("pepper")
local Nt = require("night")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-50s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140))
  end
  local function jump(...) hold(...); love.keypressed("space") end
  local function landed() return { cond = function(p) return p.onGround and p.mode == "normal" end, act = function() end, limit = 3 } end
  local function prop(name, k)
    local i = 0
    for _, pr in ipairs(api.stage().def.props) do if pr.name == name then i = i + 1; if i == (k or 1) then return pr end end end
  end
  local function plank(k) return api.stage().night.planks[k] end
  local function near(a, b, t) return math.abs(a - b) < (t or 1) end
  local function foxTo(i)                                                     -- put the fox in hideout i
    local s = api.stage(); local f, h = s.night.fox, s.def.fox.hideouts[i]
    f.state, f.i, f.x, f.y, f.t, f.found = "hide", i, h.x, h.y, 0, true; s.ball.state = "fox"; s.pepper.carrying = nil
  end
  local function at(cond, act, limit) return { cond = cond, act = act, limit = limit or 6 } end

  local steps
  if mode == "--physics" then
    local hearts, minY
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      { act = function() local s = api.stage()
          report("night: the level is dark", s.night ~= nil and s.night.dark == true, tostring(s.night and s.night.dark))
          report("night: 5 checkpoint lamps, 12 more lights", #s.def.lamps == 5 and #s.def.lights == 12, ("%d + %d"):format(#s.def.lamps, #s.def.lights))
          local maxGap = 0
          for i = 2, #s.def.lamps do maxGap = math.max(maxGap, s.def.lamps[i].x - s.def.lamps[i - 1].x) end
          report("checkpoints about 3 screens apart", maxGap <= 1000, ("largest gap %d px"):format(maxGap))
          report("the fox starts on the quay with the ball", s.night.fox.state == "sit" and s.ball.state == "fox", s.ball.state)
          local hidden = 0
          for _, bn in ipairs(s.bones) do if Nt.hideBone(s, bn) then hidden = hidden + 1 end end
          report("most bones are hidden in the dark", hidden >= #s.bones / 2, ("%d of %d"):format(hidden, #s.bones))
        end },
      -- the fox runs off when Pepper comes close, to hideout 1
      { act = function() tp(100, 184); hold("right") end },
      at(function(p, s) return s.night.fox.state ~= "sit" end, function() release() end, 4),
      { act = function(p, s) report("fox: it runs off when Pepper comes close", s.night.fox.state == "run" and s.night.fox.i == 1, ("x %.0f"):format(p.x)) end },
      { wait = 4 },
      { act = function(p, s) local f, h = s.night.fox, s.def.fox.hideouts[1]
          report("fox: it hides at the tarp", f.state == "hide" and near(f.x, h.x), ("%s x %.0f"):format(f.state, f.x)) end },
      -- hidden, the fox must be sniffed out first: a bark does nothing; a moment's sniffing close by finds it
      { act = function() local s = api.stage(); tp(804 - 60, 184); s.pepper.face = 1; s.pepper.barkT = 0; love.keypressed("z") end }, { wait = 0.2 },
      { act = function(p, s) local f = s.night.fox
          report("fox: hidden, a bark before sniffing does nothing", f.state == "hide" and f.i == 1 and not f.found, f.state)
          report("fox: hidden, the hint says HOLD: SNIFF", Nt.need(s, "sniffhere") and not Nt.need(s, "foxnear"), "")
          hold("sniff") end }, { wait = 0.6 },
      { act = function(p, s) release(); local f = s.night.fox
          report("fox: sniffing close by finds it", f.found == true and Nt.need(s, "foxnear"), tostring(f.found)) end },
      -- sniffing: she stops, sniffs, the trail points at hideout 1
      { act = function() tp(400 - 60, 184); api.stage().pepper.vx = 120; hold("sniff") end }, { wait = 0.3 },
      { act = function(p, s)
          local tx = Nt.target(s)
          report("sniff: she stops and sniffs", s.night.sniff and p.vx == 0 and p.anim == "sniff", ("vx %.0f anim %s"):format(p.vx, p.anim))
          report("sniff: the trail points at the tarp", tx == s.def.fox.hideouts[1].x, tostring(tx))
          local shown = 0
          for _, bn in ipairs(s.bones) do if not Nt.hideBone(s, bn) and math.abs(bn.x - p.x) < 200 then shown = shown + 1 end end
          report("sniff: the bones nearby show", shown >= 3, ("%d bones"):format(shown))
          hold("right", "sniff") end }, { wait = 0.3 },
      { act = function(p) report("sniff: she does not move while sniffing", near(p.x, 340), ("x %.1f"):format(p.x)); release() end },
      { act = function() hold("right") end }, { wait = 0.3 },
      { act = function(p) report("sniff: let go, she runs again", p.x > 345, ("x %.1f"):format(p.x)); release() end },
      -- bark range at each hideout
    }
    for i = 1, 3 do
      local add = {
        { act = function() local s = api.stage(); foxTo(i); local h = s.def.fox.hideouts[i]; tp(h.x - s.def.fox.bark - 30, 184); s.pepper.face = 1; s.pepper.barkT = 0; love.keypressed("z") end },
        { wait = 0.2 },
        { act = function(p, s) report(("hideout %d: a bark from too far does nothing"):format(i), s.night.fox.state == "hide" and s.night.fox.i == i, s.night.fox.state) end },
        { act = function() local s = api.stage(); local h = s.def.fox.hideouts[i]; tp(h.x - s.def.fox.bark + 10, 184); s.pepper.face = 1; s.pepper.barkT = 0; love.keypressed("z") end },
        { wait = 0.2 },
        { act = function(p, s)
            if i < 3 then report(("hideout %d: a bark close up chases it on"):format(i), s.night.fox.state == "run" and s.night.fox.i == i + 1, s.night.fox.state)
            else report("hideout 3: a bark drops the ball", s.ball.state == "air" or s.ball.state == "rest", s.ball.state) end end },
        { wait = 3.5 },
      }
      for _, st in ipairs(add) do steps[#steps + 1] = st end
    end
    local more = {
      { act = function(p, s) local h = s.def.fox.hideouts[3]
          local f = s.night.fox; report("fox: it runs off for good after the last hideout", f.state == "gone" or (f.state == "run" and f.tx > s.world.width), f.state)
          report("ball: it rests under the low jetty", s.ball.state == "rest" and near(s.ball.x, h.x, 2) and near(s.ball.y, 184), ("%s x %.0f y %.0f"):format(s.ball.state, s.ball.x, s.ball.y))
          local tx = Nt.target(s); report("sniff: the trail now points at the ball", tx == s.ball.x, tostring(tx)) end },
      -- crawl under the low jetty to the ball and pick it up
      { act = function() local j = prop("LOW JETTY"); report("low jetty: 19 px to crawl under", 184 - j.y1 == 19, ("%d px"):format(184 - j.y1)); tp(2930, 184); hold("right", "down") end },
      at(function(p, s) return p.x + 18 >= s.ball.x - 4 end, function() release() end, 4),
      { wait = 0.2 }, { act = function() hold("down"); love.keypressed("x") end }, { wait = 0.3 },
      { act = function(p, s) report("ball: picked up crawling under the jetty", p.carrying ~= nil, tostring(p.carrying ~= nil)); release() end },
      { act = function(p, s) local tx = Nt.target(s); report("sniff: with the ball the trail points at Mia", tx == s.girl.x, tostring(tx)) end },
      -- crumbling planks: stand on one, it holds 0.5 s, then she falls; it is back 3 s later
      { act = function(p, s) s.pepper.carrying = nil; s.ball.state = "rest"; hearts = s.hearts; local k = plank(1); tp((k.p.x0 + k.p.x1) / 2, 184) end },
      { wait = 0.35 },
      { act = function(p) local k = plank(1); report("plank: holds for a moment (0.35 s)", p.onGround and p.y == 184 and k.st == "shake", ("y %.0f %s"):format(p.y, k.st)) end },
      { wait = 0.4 },
      { act = function(p) local k = plank(1); report("plank: after 0.5 s it falls, and Pepper with it", k.st == "gone" and (p.y > 184 or p.mode == "drown"), ("y %.0f %s"):format(p.y, k.st)) end },
      { wait = 2.0 },
      { act = function(p, s) report("water: falling in costs a heart", s.hearts == hearts - 1, ("hearts %d"):format(s.hearts)) end },
      { wait = 1.5 },
      { act = function(p, s) local k = plank(1); report("plank: it is back 3 s later", k.st == "idle", k.st) end },
      -- a running hop chain over the four rotten planks (tap hops), from the quay
      { act = function(p, s) for _, k in ipairs(s.night.planks) do if k.st == "gone" then s.world.rects[#s.world.rects + 1] = k.p end; k.st, k.t = "idle", 0 end
          hearts = s.hearts; tp(2240, 184); hold("right") end },
      at(function(p) return p.x >= 2266 end, function() jump("right", "jump") end),          -- (r7: narrower planks)
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2300 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2356 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2412 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2520 end, function() release() end, 3),
      { act = function(p, s) report("rotten planks: four tap hops get across", p.x > 2520 and p.y == 184 and s.hearts == hearts, ("x %.0f hearts %d"):format(p.x, s.hearts)) end },
      -- the rowboat: it comes to the quay, she rides it, it reaches the far side
      { act = function(p, s) local m = s.movers[1]
          report("rowboat 1: deck 12 px below the quay, rows 176 px", m.y0 == 196 and m.to - m.from == 176, ("deck %d"):format(m.y0)) end },
      at(function(p, s) return s.movers[1].x0 <= s.movers[1].from + 1 end, function() tp(1316, 184); hold("right") end, 20),
      at(function(p, s) return p.ground == s.movers[1] end, function() release() end, 3),
      at(function(p, s) return s.movers[1].x0 >= s.movers[1].to - 1 end, function() jump("right", "jump") end, 12),
      at(function(p) return p.onGround and p.x > 1560 end, function() release() end, 3),
      { act = function(p) report("rowboat 1: ride across, hop up the far quay", p.x > 1560 and p.y == 184, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- the climbs: the stack and the shed roof (secret), the crate tower (secret)
      { act = function() tp(1880, 184); hold("right") end },
      at(function(p) return p.x >= 1888 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end, 3),
      at(function(p) return p.x >= 1934 end, function() jump("right", "jump") end, 3),
      at(function(p) return p.onGround and p.y <= 113 end, function() release() end, 3),
      { wait = 0.2 },
      { act = function(p, s) report("shed roof: stack then held jump (secret)", p.y == 112 and s.secretsFound >= 1, ("y %.0f secrets %d"):format(p.y, s.secretsFound)) end },
      { act = function() tp(3540, 184); hold("right") end },
      at(function(p) return p.x >= 3570 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end, 3),
      at(function(p) return p.onGround and (p.y <= 121 or p.x >= 3642) end, function(p) if p.y > 121 then jump("right", "jump") end end, 3),
      at(function(p) return p.onGround and p.y <= 121 end, function() release() end, 3),
      { wait = 0.2 },
      { act = function(p, s) report("crate tower: three steps up (secret)", p.y == 120 and s.secretsFound >= 2, ("y %.0f secrets %d"):format(p.y, s.secretsFound)) end },
      -- Mia at the door takes the ball
      { act = function() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball; tp(s.girl.x - 30, 184); s.pepper.face = 1 end },
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.3 },
      { act = function(p, s) report("Mia: giving her the ball clears the level", s.ball.state == "given" and s.clearT ~= nil, s.ball.state) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
    for _, st in ipairs(more) do steps[#steps + 1] = st end
    require("tests_safety")(steps, api, report)                  -- the safety nets (r6/engine), before the summary
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec")
    local function sniff(t) return { act = function() hold("sniff") end }, { wait = t }, { act = function() release() end } end
    local function hop() return at(function() return true end, function() jump("right", "jump") end), { wait = 1 / 60 }, { act = function() hold("right") end } end
    steps = { { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 } }
    local function add(...) for _, st in ipairs({ ... }) do steps[#steps + 1] = st end end
    add(
      -- 1 the quay: run at the fox, it runs off
      { act = function() hold("right") end },
      at(function(p, s) return s.night.fox.state ~= "sit" end, function() end, 6),
      -- 2 lantern street: the first gap (a hop), sniff, the crates
      at(function(p) return p.x >= 380 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 450 end, function() release() end),
      sniff(0.9),
      { act = function() hold("right") end },
      at(function(p) return p.x >= 495 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end),
      -- 3 the tarp: bark the fox out
      at(function(p) return p.x >= 740 and p.onGround and p.y >= 183 end, function() release() end, 6),
      { wait = 0.2 }, { act = function() hold("sniff") end }, at(function(p, s) return s.night.fox.found end, function() release() end, 4),
      { wait = 0.1 }, { act = function() love.keypressed("z") end }, { wait = 0.6 },
      at(function(p, s) return s.night.fox.i == 2 end, function() hold("right") end),
      -- 4 old jetty: hop, hop, hop
      at(function(p) return p.x >= 990 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 1040 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 1112 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 1160 end, function() hold("right") end, 3),
      -- 5 the rowboat: wait for it at the quay, ride, hop off
      at(function(p) return p.x >= 1290 end, function() release() end),
      at(function(p, s) return s.movers[1].x0 <= s.movers[1].from + 2 end, function() hold("right") end, 20),
      at(function(p, s) return p.ground == s.movers[1] and p.x >= s.movers[1].x0 + 28 end, function() release() end, 3),
      at(function(p, s) return s.movers[1].x0 >= s.movers[1].to - 1 end, function() jump("right", "jump") end, 12),
      at(function(p) return p.onGround and p.x > 1560 end, function() hold("right") end, 3),
      -- 6 fish boxes, over the net shed's roof
      at(function(p) return p.x >= 1650 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 169 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 153 end, function() hold("right") end),
      at(function(p) return p.x >= 1736 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 159 end, function() hold("right") end, 3),
      -- 7 the stack, the shed roof (gold bone, secret), down, bark the fox out of the crates
      at(function(p) return p.onGround and p.y <= 153 and p.x > 1900 end, function() hold("right") end, 4),
      at(function(p) return p.x >= 1930 end, function() jump("right", "jump") end, 3),
      at(function(p) return p.onGround and p.y <= 113 end, function() hold("right") end, 3),
      at(function(p) return p.onGround and p.y >= 183 and p.x > 2040 end, function() release() end, 4),
      { wait = 0.2 }, { act = function() hold("sniff") end }, at(function(p, s) return s.night.fox.found end, function() release() end, 4),
      { wait = 0.1 }, { act = function() love.keypressed("z") end }, { wait = 0.6 },
      at(function(p, s) return s.night.fox.i == 3 end, function() hold("right") end),
      -- 8 rotten planks: four tap hops (each lands on the next plank)
      at(function(p) return p.x >= 2266 end, function() jump("right", "jump") end),          -- (r7: narrower planks)
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2300 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2356 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2412 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 2520 end, function() release() end, 3),
      -- 9 two boats and the post
      at(function(p, s) return s.movers[2].x0 <= s.movers[2].from + 2 end, function() hold("right") end, 20),
      at(function(p, s) return p.ground == s.movers[2] and p.x >= s.movers[2].x0 + 20 end, function() release() end, 3),
      at(function(p, s) return s.movers[2].x0 >= s.movers[2].to - 1 end, function() jump("right", "jump") end, 12),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= 177 end, function() release() end, 3),
      at(function(p, s) return s.movers[3].x0 <= s.movers[3].from + 2 end, function() jump("right", "jump") end, 20),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p, s) return p.ground == s.movers[3] end, function() release() end, 3),
      at(function(p, s) return s.movers[3].x0 >= s.movers[3].to - 1 end, function() jump("right", "jump") end, 12),
      at(function(p) return p.onGround and p.x > 2840 end, function() hold("right") end, 3),
      -- 10 the low jetty: bark at the fox, crawl under, pick up the ball
      at(function(p) return p.x >= 2930 end, function() release() end, 4),
      { wait = 0.2 }, { act = function() hold("sniff") end }, at(function(p, s) return s.night.fox.found end, function() release() end, 4),
      { wait = 0.1 }, { act = function() love.keypressed("z") end }, { wait = 1.2 },
      at(function(p, s) return s.ball.state == "rest" end, function() hold("right", "down") end, 4),
      at(function(p, s) return p.x + 18 >= s.ball.x - 4 end, function() release() end, 6),
      { wait = 0.2 }, { act = function() hold("down"); love.keypressed("x") end }, { wait = 0.4 },
      at(function(p) return p.carrying ~= nil end, function() hold("right", "down") end, 2),
      at(function(p) return p.x >= 3096 end, function() hold("right") end, 6),
      -- 11 back over: the third rowboat, one crumbling plank
      at(function(p) return p.x >= 3210 end, function() release() end),
      at(function(p, s) return s.movers[4].x0 <= s.movers[4].from + 2 end, function() hold("right") end, 20),
      at(function(p, s) return p.ground == s.movers[4] and p.x >= s.movers[4].x0 + 28 end, function() release() end, 3),
      at(function(p, s) return s.movers[4].x0 >= s.movers[4].to - 1 end, function() jump("right", "jump") end, 12),
      at(function(p) return p.onGround and p.x > 3400 end, function() hold("right") end, 3),
      at(function(p) return p.x >= 3412 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 3430 end, function() jump("right", "jump") end, 2),     -- (r7) two narrow planks
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 3470 end, function() jump("right", "jump") end, 2),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.x > 3510 end, function() hold("right") end, 3),
      -- 12 the crate tower (gold bone, secret)
      at(function(p) return p.x >= 3570 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= 169 end, function() hold("right") end, 3),
      at(function(p) return p.onGround and (p.y <= 121 or p.x >= 3642) end, function(p) if p.y > 121 then jump("right", "jump") end end, 3),
      at(function(p) return p.onGround and p.y <= 121 end, function() hold("right") end, 3),
      -- 13 the slipway: boat, plank, boat, the quay
      at(function(p) return p.x >= 3770 end, function() release() end),
      at(function(p, s) return s.movers[5].x0 <= s.movers[5].from + 2 end, function() hold("right") end, 20),
      at(function(p, s) return p.ground == s.movers[5] and p.x >= s.movers[5].x0 + 22 end, function() release() end, 3),
      at(function(p, s) return s.movers[5].x0 >= s.movers[5].to - 1 end, function() jump("right", "jump") end, 12),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p, s) return p.onGround and p.ground == s.night.planks[#s.night.planks].p end, function() jump("right", "jump") end, 3),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p, s) return p.onGround and p.ground == s.movers[6] end, function() release() end, 3),
      at(function(p, s) return s.movers[6].x0 >= s.movers[6].to - 1 end, function() jump("right", "jump") end, 12),
      at(function(p) return p.onGround and p.x > 4080 end, function() hold("right") end, 3),
      -- 14 home: Mia
      at(function(p, s) return p.onGround and p.y >= 183 and p.x >= s.girl.x - 40 end, function() release() end, 15),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played%s"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time, s.hard and " (hard)" or "")); io.stdout:flush()
          love.event.quit() end })
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("nt_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    local spots = { { 60, 184 }, { 470, 184 }, { 700, 184 }, { 1200, 184 }, { 1300, 184 }, { 1620, 184 }, { 2150, 184 },
      { 2250, 184 }, { 2570, 184 }, { 2920, 184 }, { 3200, 184 }, { 3560, 184 }, { 3780, 184 }, { 4180, 184 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]); local s = api.stage(); s.pepper.face = 1 end }
      steps[#steps + 1] = { wait = 0.4 }
      steps[#steps + 1] = shot(("nt_%02d_screen%d"):format(i, i), (i - 1) * 320)
    end
    local function add(t) for _, st in ipairs(t) do steps[#steps + 1] = st end end
    add({
      -- the fox on the quay, running off
      { act = function() local s = api.stage(); local f = s.night.fox; f.state, f.x, f.y = "sit", 240, 184; s.ball.state = "fox"; tp(150, 184); s.pepper.face = 1 end },
      { wait = 0.2 }, shot("nt_20_fox", 0),
      -- sniffing towards the tarp
      { act = function() foxTo(1); tp(560, 152); hold("sniff") end }, { wait = 0.6 }, shot("nt_21_sniff"), { act = function() release() end },
      -- barking the fox out of the tarp
      { act = function() foxTo(1); tp(740, 184); api.stage().pepper.face = 1; love.keypressed("z") end }, { wait = 0.25 }, shot("nt_22_fox_bolts"),
      -- a plank shaking, then gone
      { act = function() local k = plank(1); tp((k.p.x0 + k.p.x1) / 2, 184) end }, { wait = 0.3 }, shot("nt_23_plank_shakes"),
      { wait = 0.5 }, shot("nt_24_plank_falls"), { wait = 2.6 },
      -- the low jetty: the ball dropped under it
      { act = function() foxTo(3); tp(2950, 184); api.stage().pepper.face = 1; love.keypressed("z") end }, { wait = 1.0 }, shot("nt_25_ball_dropped"),
      { act = function() local s = api.stage(); tp(2980, 184); hold("sniff") end }, { wait = 0.5 }, shot("nt_26_sniff_ball"), { act = function() release() end },
      { act = function() love.keypressed("g") end }, { wait = 0.1 }, shot("nt_27_debug", 2880), { act = function() love.keypressed("g") end },
      -- giving Mia the ball: the tally
      { act = function() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball; tp(s.girl.x - 30, 184); s.pepper.face = 1 end },
      { wait = 0.2 }, { act = function() love.keypressed("x") end },
      { wait = 1.0 }, shot("nt_28_give"),
      { wait = 4.5 }, shot("nt_29_tally"),
      { wait = 0.3 }, { act = function() love.event.quit() end },
    })
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
        if os.getenv("AUTO_DEBUG") then print(("step %d at x %.1f y %.1f vx %.0f %s"):format(i, p.x, p.y, p.vx, p.onGround and "G" or "A")) end
        st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
