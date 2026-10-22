-- The checks for Level 4, Söder Hill (love riverwalk --level soder <flag>). Same flags as tests_citypark.lua:
--   --physics   the chase's rules and every set piece: heights and crawl gaps, the scroll and the left edge's push,
--               pinned against an obstacle (a heart, back to the lamp), the hatches, the ball rolling ahead and
--               stopping at the railing, the barrels, picking up the ball and giving it to Mia
--   --auto      plays the whole level on autopilot and saves every 3rd frame to rec/ (for the GIF)
--   --test      a screenshot tour: the card, every screen, a hatch, the barrel, crawling, the end, the tally
local I = require("input")
local Pp = require("pepper")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-54s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  -- move Pepper (and the camera: the chase starts again from there)
  local function tp(x, y, camx) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, camx or (x - 140)))
  end
  local function jump(...) hold(...); love.keypressed("space") end
  local function prop(name, k)
    local i = 0
    for _, pr in ipairs(api.stage().def.props) do if pr.name == name then i = i + 1; if i == (k or 1) then return pr end end end
  end
  local function streetAt(x)                        -- the street's top at x (terrain and stairs only; nil over a hatch)
    local w = api.stage().world
    local sy = w:slopeFloor(x); if sy then return sy end
    local best
    for _, r in ipairs(w.rects) do if r.terrain and x >= r.x0 and x < r.x1 and (not best or r.y0 < best) then best = r.y0 end end
    return best
  end
  local function near(a, b, e) return math.abs(a - b) < (e or 1) end

  local steps
  if mode == "--physics" then
    local s0, minY, hearts, x0, cam0, t0
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      -- 0 the map and the props: heights Pepper can manage
      { act = function()
          local s = api.stage(); local w = s.world
          report("the street steps down the hill: 112 at the top, 208 at the quay", streetAt(60) == 112 and streetAt(5000) == 208,
            ("top %s, quay %s"):format(tostring(streetAt(60)), tostring(streetAt(5000))))
          local ok, bad = true, ""
          for _, pr in ipairs(s.def.props) do
            if pr.kind == "solid" and pr.name ~= "RAILING" then
              local g = streetAt((pr.x0 + pr.x1) / 2)
              if pr.y1 >= g - 1 then                                         -- standing in the street: a hop or a jump
                local h = g - pr.y0
                if h > 46 then ok = false; bad = bad .. (" %s %d px"):format(pr.name, h) end
              else                                                           -- hanging: a crawl gap
                local gap = g - pr.y1
                if gap < 18 or gap >= Pp.H_STAND then ok = false; bad = bad .. (" %s gap %d"):format(pr.name, gap) end
              end
            end
          end
          report("every obstacle is a hop, a jump (<= 46 px) or a crawl gap", ok, bad ~= "" and bad or "all fine")
          local okH = true
          for _, h in ipairs(s.def.hatches) do
            local open = true
            for x = h[1] + 1, h[2] - 1, 4 do if streetAt(x) then open = false end end
            if not open or h[2] - h[1] > 40 then okH = false end
          end
          report("the hatches are open gaps of at most 40 px", okH, #s.def.hatches .. " hatches")
          report("three lamps (checkpoints)", #s.def.lamps == 3, #s.def.lamps)
        end },
      -- 1 the scroll moves the camera on by itself
      { act = function() tp(400, 112, 300); hearts = api.stage().hearts end }, { wait = 0.1 },
      { act = function() cam0 = api.stage().cam end }, { wait = 1.0 },
      { act = function() local s = api.stage()
          report("the scroll moves the camera on (50 px/s at the top)", s.cam - cam0 > 45 and s.cam - cam0 < 56, ("%.1f px in 1 s"):format(s.cam - cam0)) end },
      -- 2 the left edge pushes a Pepper standing still along the open street
      { act = function() tp(1250, 144, 1200) end }, { wait = 1.5 },
      { act = function(p) local s = api.stage()
          report("the left edge pushes her along", p.x >= s.cam + Pp.HW - 0.5 and p.x > 1250, ("x %.1f, edge %.1f"):format(p.x, s.cam + Pp.HW))
          report("being pushed along open street costs nothing", s.hearts == 3, "hearts " .. s.hearts) end },
      -- 3 pinned against the bikes (she stands still behind them): a heart, back to the lamp
      { act = function() local s = api.stage(); s.check = { x = 1240, y = 144 }; tp(1318, 144, 1300); s.hearts = 3 end },
      { during = 1.8 },
      { act = function(p) local s = api.stage()
          report("pinned against the bikes: a heart lost", s.hearts == 2, "hearts " .. s.hearts)
          report("pinned: back to the lamp", near(p.x, 1240, 2), ("x %.1f"):format(p.x)) end },
      -- 4 an open hatch: she falls in, a heart, back to the lamp
      { act = function() local s = api.stage(); s.check = { x = 1240, y = 144 }; s.hearts = 3; tp(1840, 144, 1720) end },
      { during = 1.6 },
      { act = function(p) local s = api.stage()
          report("an open hatch: a heart lost", s.hearts == 2, "hearts " .. s.hearts)
          report("a hatch: back to the lamp", near(p.x, 1240, 2) and p.mode == "normal", ("x %.1f %s"):format(p.x, p.mode)) end },
      -- 5 a tapped hop clears a hatch, running
      { act = function() local s = api.stage(); s.hearts = 3; tp(980, 128, 900); hold("right") end },
      { cond = function(p) return p.x >= 1022 end, act = function() jump("right", "jump") end, limit = 3 },
      { wait = 1 / 60 }, { act = function() hold("right") end }, { during = 0.8 },
      { act = function(p) local s = api.stage()
          report("a running tap hop clears a 32 px hatch", s.hearts == 3 and p.x > 1080 and p.y <= 129, ("x %.0f y %.0f hearts %d"):format(p.x, p.y, s.hearts)); release() end },
      -- 6 crawling under the cafe sign keeps her clear of it
      { act = function() local s = api.stage(); s.hearts = 3; tp(690, 128, 560); hold("right", "down") end }, { during = 2.0 },
      { act = function(p) local s = api.stage()
          report("crawling under the cafe sign", p.x > 760 and s.hearts == 3, ("x %.0f hearts %d"):format(p.x, s.hearts)); release() end },
      -- 7 a held jump lands on the tall crate stack (32 px)
      { act = function() tp(490, 128, 400); hold("right") end }, { during = 0.1 },
      { act = function() jump("right", "jump") end }, { during = 0.25 }, { act = function() hold("right", "jump") end },
      { cond = function(p) return p.onGround end, act = function() release() end, limit = 3 },
      { act = function(p) report("a held jump lands on the tall crates (32 px)", p.y <= 97 and p.x >= 520, ("x %.0f y %.0f"):format(p.x, p.y)) end },
      -- 8 the ball rolls ahead of her, on screen
      { act = function() local s = api.stage(); local b = s.ball; b.state = "roll"; tp(2000, 160, 1900) end }, { wait = 0.6 },
      { act = function() local s = api.stage(); local b = s.ball
          report("the ball rolls ahead, on screen", b.state == "roll" and b.x - s.cam >= 199 and b.x - s.cam <= 312, ("ball at screen x %.0f"):format(b.x - s.cam))
          report("the ball rolls on the street", near(b.y, streetAt(b.x) or b.y, 2) or b.vy ~= 0, ("y %.0f street %s"):format(b.y, tostring(streetAt(b.x)))) end },
      -- 9 the barrel: the ball knocks it off its stack; it rolls down the street and hurts on touch
      { act = function() local s = api.stage(); local c = s.chase; c.barrels[1].state = "stack"; s.ball.state = "roll"; s.hearts = 3
          tp(1700, 144, 1640); c.hold = true end },
      { cond = function() return api.stage().chase.barrels[1].state == "roll" end, act = function() end, limit = 5 },
      { act = function() local s = api.stage()
          report("the ball knocks the barrel loose", s.chase.barrels[1].state == "roll", s.chase.barrels[1].state) end },
      { during = 3.0 },
      { act = function() local s = api.stage(); local br = s.chase.barrels[1]
          report("the barrel rolls down the stairs (3 s: about 90 px)", br.state == "roll" and br.x > 1950 and br.x < 2100 and near(br.y, streetAt(br.x) or 0, 3),
            ("x %.0f y %.0f (street %s), screen x %.0f"):format(br.x, br.y, tostring(streetAt(br.x)), br.x - s.cam))
          tp(br.x + 40, streetAt(br.x + 40), br.x - 100); hearts = s.hearts; s.chase.hold = nil end },
      { during = 1.5 },
      { act = function() local s = api.stage()
          report("touching the barrel costs a heart", s.hearts == hearts - 1, ("hearts %d -> %d"):format(hearts, s.hearts)) end },
      -- 10 at the bottom: the ball stops against the railing; she picks it up and gives it to Mia
      { act = function() local s = api.stage(); s.chase.barrels[1].state = "gone"; s.ball.state = "roll"; s.ball.x = 4990; s.ball.y = 208; s.hearts = 3
          tp(4900, 208, 4780) end },
      { during = 2.0 },
      { act = function() local s = api.stage(); local b = s.ball
          report("the ball stops against the railing", b.state == "rest" and near(b.x, s.def.scroll.ballStop, 1), ("%s x %.0f"):format(b.state, b.x))
          report("the scroll stops at the end", s.cam == s.world.width - 320, ("cam %.0f"):format(s.cam))
          tp(b.x - 18, 208, 4800); s.pepper.face = 1 end },
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.3 },
      { act = function(p) report("Pepper picks the ball up", p.carrying ~= nil, tostring(p.carrying ~= nil)); hold("left") end },
      { cond = function(p) local s = api.stage(); return p.x <= s.girl.x + 34 end, act = function() release() end, limit = 3 },
      { wait = 0.2 }, { act = function(p) p.face = -1; love.keypressed("x") end }, { wait = 0.4 },
      { act = function() local s = api.stage()
          report("giving the ball to Mia: GOOD GIRL (FETCH 2000)", s.ball.state == "given" and s.bonus and s.bonus[2] == 2000, s.ball.state) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
    require("tests_safety")(steps, api, report)                  -- the safety nets (r6/engine), before the summary
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec")
    -- a reactive autopilot: it runs right all the way, and at the set pieces (by x) it hops, jumps or crawls;
    -- a rolling barrel close ahead gets a held jump
    local plan = {                                 -- { x where it starts, what (, crawl until x) }
      { 204, "hop" }, { 476, "jump" }, { 676, "crawl", 770 }, { 836, "hop" }, { 868, "hop" }, { 1016, "hop" },
      { 1306, "hop" }, { 1440, "crawl", 1530 }, { 1800, "jump" }, { 2140, "crawl", 2230 }, { 2300, "hop" },
      { 2404, "hop" }, { 2662, "jump" }, { 2730, "hop" }, { 2900, "jump" }, { 3012, "jump" }, { 3090, "jump" },
      { 3360, "crawl", 3452 }, { 3482, "hop" }, { 3518, "hop" }, { 3552, "jump" }, { 3972, "hop" },
      { 4160, "crawl", 4252 }, { 4280, "hop" }, { 4360, "hop" }, { 4530, "hop" }, { 4568, "hop" },
    }
    local k, jumpT, crawlTo, lastX = 1, 0, nil, nil
    steps = {
      { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      { cond = function(p, s)
          if s.ball.state == "rest" then release(); return true end
          local held = { right = true }
          if p.x < (lastX or 0) - 60 then                                   -- back at a lamp: the plan from here
            k = 1; while plan[k] and plan[k][1] <= p.x do k = k + 1 end; crawlTo = nil
          end
          lastX = p.x
          if crawlTo then
            if p.x < crawlTo then held.down = true else crawlTo = nil end
          end
          local nx = plan[k]
          if os.getenv("AUTO_DEBUG") and frame % 20 == 0 then print(("x %.0f y %.0f vx %.0f cam %.0f %s k %d ball %s %.0f %.0f %.0f t %.1f"):format(p.x, p.y, p.vx, s.cam, p.onGround and "G" or "A", k, s.ball.state, s.ball.x, s.ball.y, s.ball.vy or 0, s.t)) end
          if nx and p.x >= nx[1] and p.onGround and p.mode == "normal" then
            if os.getenv("AUTO_DEBUG") then print(("  %s at x %.0f"):format(nx[2], p.x)) end
            if nx[2] == "crawl" then crawlTo = nx[3]; held.down = true
            else love.keypressed("space"); jumpT = nx[2] == "jump" and 0.35 or 1 / 60 end
            k = k + 1
          end
          for _, br in ipairs(s.chase.barrels) do                         -- a barrel close ahead: jump it
            if br.state == "roll" and br.x > p.x and br.x - p.x < 40 and p.onGround and p.mode == "normal" and not crawlTo then
              love.keypressed("space"); jumpT = 0.35
            end
          end
          if jumpT > 0 then held.jump = true; jumpT = jumpT - 1 / 60 end
          I.force = held
          return false
        end, act = function() end, limit = 200 },
      -- the ball lies by the railing: walk up to it, pick it up, bring it back to Mia
      { cond = function(p, s)
          local b = s.ball
          if math.abs(p.x + 18 - b.x) < 12 and math.abs(p.vx) < 1 then return true end
          hold(p.x + 18 < b.x and "right" or "left", "walk"); if math.abs(p.x + 18 - b.x) < 6 then release() end
          return false
        end, act = function(p) release(); p.face = 1 end, limit = 8 },
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.5 },
      { act = function() hold("left") end },
      { cond = function(p, s) return p.x <= s.girl.x + 36 end, act = function() release() end, limit = 6 },
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      { wait = 9 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played%s"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time, s.hard and " (hard)" or "")); io.stdout:flush()
          love.event.quit() end },
    }
  else  -- --test
    local function shot(name, cam) return { act = function() if cam then api.stage().cam = cam; api.stage().chase.lastCam = cam; api.stage().chase.x = cam end; love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("sd_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    for i = 1, 16 do
      local x = (i - 1) * 320 + 150
      steps[#steps + 1] = { act = function() local s = api.stage(); s.ball.state = "roll"; tp(x, streetAt(x) or 200, (i - 1) * 320 - 10) end }
      steps[#steps + 1] = { wait = 0.15 }
      steps[#steps + 1] = shot(("sd_%02d_screen%d"):format(i, i))
    end
    steps[#steps + 1] = { act = function() local s = api.stage(); s.chase.barrels[1].state = "stack"; s.ball.state = "roll"; tp(1700, 144, 1640) end }
    steps[#steps + 1] = { cond = function() return api.stage().chase.barrels[1].state == "roll" end, act = function() end, limit = 5 }
    steps[#steps + 1] = { wait = 0.8 }; steps[#steps + 1] = shot("sd_17_barrel")
    steps[#steps + 1] = { act = function() tp(1836, 144, 1720) end }; steps[#steps + 1] = { wait = 0.3 }; steps[#steps + 1] = shot("sd_18_hatch")
    steps[#steps + 1] = { act = function() tp(700, 128, 600); hold("right", "down") end }; steps[#steps + 1] = { wait = 0.9 }
    steps[#steps + 1] = shot("sd_19_crawl"); steps[#steps + 1] = { act = function() release() end }
    steps[#steps + 1] = { act = function() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball; tp(s.girl.x + 30, 208, 4800); s.pepper.face = -1 end }
    steps[#steps + 1] = { wait = 0.2 }; steps[#steps + 1] = { act = function() love.keypressed("x") end }
    steps[#steps + 1] = { wait = 1.0 }; steps[#steps + 1] = shot("sd_20_give")
    steps[#steps + 1] = { wait = 4.5 }; steps[#steps + 1] = shot("sd_21_tally")
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
        if os.getenv("AUTO_DEBUG") then print(("step %d at x %.1f y %.1f vx %.0f %s"):format(i, p.x, p.y, p.vx, p.onGround and "G" or "A")) end
        st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
