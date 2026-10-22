-- The checks for the height engine's test level (love riverwalk --level lab_tall <flag>):
--   --physics   the vertical camera (it follows up the stairs, a hop does not bob it, it leads down a tall drop,
--               it settles on the new floor, Up / Down held still look up / down), floors at any height (stairs,
--               4 px steps, one-way planks and dropping through them), the goods lift (it carries Pepper up and
--               down, waits rather than crush her, never comes down on her), a fall out of the world (a heart,
--               back to the lamp), a tall drop (no harm), the fetch to Mia; and the flat levels unchanged (240 px
--               high, camera y always 0, even looking up and down)
--   --auto      plays the level on autopilot, saving every 3rd frame to rec_lab_tall/ (for the GIF)
--   --test      a screenshot tour: every screen of the 3 x 3, looking up and down, the lift
local I = require("input")
local Pp = require("pepper")
local St = require("stage")
local Vc = require("vcam")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local recLook                                    -- --test: frames of looking up and down (rec_lab_tall_look/)
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-58s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  -- move Pepper and the camera to her (x and y)
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); Vc.snap(s)
  end
  local function jump(...) hold(...); love.keypressed("space") end
  local function near(a, b, e) return math.abs(a - b) <= (e or 1) end
  local function lift() return api.stage().movers[1] end
  local function camFor(y) local s = api.stage(); return math.max(0, math.min(s.camYMax, y - Vc.FLOOR)) end

  local steps
  if mode == "--physics" then
    local cam0, minY, maxBob, hearts, onScreen, camAtTop, extra
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      -- 0 the world: 90 rows, 720 px high; the camera starts at the bottom
      { act = function(p, s)
          report("a tall map: 960 x 720 px (90 rows)", s.world.width == 960 and s.world.height == 720, ("%d x %d"):format(s.world.width, s.world.height))
          report("the camera starts at the bottom of the world", s.camY == s.camYMax and s.camYMax == 480, ("camY %.0f of %d"):format(s.camY, s.camYMax))
        end },
      -- 1 the flat levels: 240 px high, camera y 0 always (looking up and down too), no parallax shift
      { act = function()
          local ok, info = true, ""
          for _, name in ipairs({ "citypark", "downtown", "riverwalk", "soder", "night" }) do
            local st = St.new(require("level." .. name))
            local p = st.pepper
            local okL = st.world.height == 240 and st.camYMax == 0 and st.camY == 0 and Vc.parallax(st, 0) == nil
            for i = 1, 120 do
              I.force = i < 60 and { up = true } or { down = true }
              st:update(1 / 60, {})
              if st.camY ~= 0 then okL = false end
            end
            release()
            ok = ok and okL; info = info .. (" %s %s"):format(name, okL and "ok" or ("BAD h " .. st.world.height))
          end
          report("the five flat levels: 240 high, camera y always 0", ok, info)
        end },
      -- 2 up the stairs: the camera follows her up and settles on the landing
      { act = function() tp(270, 664); cam0 = api.stage().camY; hold("right"); onScreen = true end },
      { cond = function(p) local s = api.stage(); local sy = p.y - s.camY; if sy < 20 or sy > 236 then onScreen = false end
          return p.x >= 400 end, act = function() release() end, limit = 4 },
      { wait = 1.2 },
      { act = function(p, s)
          report("up the stairs to the landing (y 568), no jump", near(p.y, 568, 0.01), ("y %.1f"):format(p.y))
          report("the camera followed her up and settled (568 - 168)", cam0 == 480 and near(s.camY, camFor(568), 1), ("%.0f -> %.1f"):format(cam0, s.camY))
          report("she stayed on screen all the way", onScreen) end },
      -- 3 the 4 px steps are walked onto
      { act = function() tp(410, 568); minY = 999; hold("walk", "right") end },
      { cond = function(p) minY = math.min(minY, p.y); return p.x >= 545 or not p.onGround end, act = function() release() end, limit = 4 },
      { act = function(p) report("the 4 px steps are walked up (to 556) without a jump", near(minY, 556, 0.01) and p.onGround, ("top %.1f, %s"):format(minY, p.onGround and "on the ground" or "in the air")) end },
      -- 4 a hop does not bob the camera
      { act = function() tp(410, 568) end }, { wait = 1.0 },
      { act = function(p, s) cam0 = s.camY; maxBob = 0; jump("jump") end }, { wait = 0.1 }, { act = function() hold("jump") end },
      { during = 1.0, each = function(p) local s = api.stage(); maxBob = math.max(maxBob, math.abs(s.camY - cam0)); minY = math.min(minY, p.y) end },
      { act = function(p) release(); report("a held jump (46 px) does not move the camera", maxBob < 0.01 and p.onGround, ("moved %.2f px"):format(maxBob)) end },
      -- 5 look up and look down
      { act = function() tp(410, 568) end }, { wait = 1.0 },
      { act = function(p, s) cam0 = s.camY; hold("up") end }, { wait = 0.3 },
      { act = function(p, s) report("looking up waits a moment", near(s.camY, cam0, 0.01), ("%.1f"):format(s.camY - cam0)) end },
      { wait = 1.2 },
      { act = function(p, s) report("Up held, standing still: the view looks up 64 px", near(s.camY, cam0 - 64, 1) and p.onGround and near(p.y, 568, 0.01),
          ("%.1f, Pepper y %.0f"):format(s.camY - cam0, p.y)); release() end },
      { wait = 1.5 },
      { act = function(p, s) report("let go: the view comes back", near(s.camY, cam0, 1), ("%.1f"):format(s.camY - cam0)); hold("down") end },
      { wait = 1.6 },
      { act = function(p, s) report("Down held, crouched and still: the view looks down 64 px", near(s.camY, cam0 + 64, 1) and p.crouch, ("%.1f %s"):format(s.camY - cam0, p.crouch and "crouched" or "standing")); release() end },
      { wait = 1.5 },
      { act = function(p) tp(410, 568); hold("right", "up") end }, { wait = 1.0 },
      { act = function(p, s) report("Up held while running does not look up", near(s.camY, camFor(p.y), 6), ("%.1f"):format(s.camY - camFor(p.y))); release() end },
      -- 6 the scaffold: one-way planks; Down + A drops through one
      { act = function() tp(590, 504) end }, { wait = 0.3 },
      { act = function() hold("down"); love.keypressed("space") end }, { wait = 0.8 },
      { act = function(p) release(); report("Down + A drops through a plank onto the one below", near(p.y, 568, 0.01) and p.onGround, ("y %.1f"):format(p.y)) end },
      { act = function() tp(610, 568) end }, { wait = 0.3 },
      { act = function() jump("right", "jump") end },
      { cond = function(p) return p.onGround and p.vy == 0 and p.y < 568 end, act = function() release() end, limit = 2 },
      { act = function(p) report("a held jump up and across to the next plank (32 px up)", near(p.y, 536, 0.01) and p.x > 656, ("x %.0f y %.1f"):format(p.x, p.y)) end },
      -- 7 a tall drop off the beam onto F2: no harm; the camera leads down, then settles
      { act = function(p, s) tp(790, 376); hearts = s.hearts; onScreen = true; extra = nil; hold("right", "walk") end },
      { cond = function(p) local s = api.stage(); local sy = p.y - s.camY; if sy < 0 or sy > 240 then onScreen = false end
          if not p.onGround and p.y > 440 and not extra then extra = s.camY - camFor(376) end
          return p.onGround and p.y > 400 end, act = function() release() end, limit = 4 },
      { act = function(p, s) report("a tall drop (128 px) lands on the floor below: no harm", near(p.y, 504, 0.01) and s.hearts == hearts, ("y %.0f hearts %d"):format(p.y, s.hearts))
          report("falling, the camera leads down; she stays on screen", (extra or 0) > 20 and onScreen, ("%.0f px down mid-fall"):format(extra or 0)) end },
      { wait = 1.2 },
      { act = function(p, s) report("landed: the camera settles on the new floor", near(s.camY, camFor(504), 1), ("camY %.1f"):format(s.camY)) end },
      -- 8 the goods lift carries her up; the camera follows
      { act = function() local m = lift(); m.k, m.dir, m.waitT, m.y0, m.y1 = 0, 1, 1.0, 504, 512; tp(920, 504) end },
      { cond = function() return lift().k > 0.05 end, act = function() end, limit = 3 },
      { act = function(p) report("the lift picks her up as it starts", p.ground == lift() and p.y < 504, ("y %.1f on %s"):format(p.y, tostring(p.ground and p.ground.name))) end },
      { cond = function(p) return lift().k >= 1 end, act = function() end, limit = 9 },
      { wait = 0.5 },
      { act = function(p, s) camAtTop = s.camY
          report("the lift carries her up to the roof (y 184)", near(p.y, 184, 0.01) and p.ground == lift(), ("y %.1f"):format(p.y))
          report("riding up, the camera followed her to the roof", near(s.camY, camFor(184), 4), ("camY %.1f, want %.0f"):format(s.camY, camFor(184))) end },
      { cond = function(p) return lift().k <= 0 end, act = function() end, limit = 9 },
      { wait = 0.2 },
      { act = function(p) report("and back down to F2 (y 504)", near(p.y, 504, 0.01) and p.onGround, ("y %.1f"):format(p.y)) end },
      -- 9 it never crushes her: a beam put over her head stops the lift until it is gone
      { act = function() local s = api.stage(); local m = lift(); m.k, m.dir, m.waitT, m.y0, m.y1 = 0, 1, 0.2, 504, 512; tp(920, 504)
          extra = { x0 = 880, x1 = 960, y0 = 380, y1 = 388, kind = "solid", name = "TEST BEAM" }; table.insert(s.world.rects, extra) end },
      { wait = 4.0 },
      { act = function(p, s) local m = lift()
          report("a solid over her head: the lift waits, she is not squeezed", m.blocked and p.y - Pp.H_STAND >= 388 - 0.01 and p.ground == m and s.hearts == 3,
            ("feet %.1f head %.1f, %s"):format(p.y, p.y - Pp.H_STAND, m.blocked and "waiting" or "moving"))
          for i, r in ipairs(s.world.rects) do if r == extra then table.remove(s.world.rects, i) end end end },
      { wait = 0.5 },
      { act = function(p) report("the beam gone: the lift goes on up", not lift().blocked and p.y < 410, ("y %.1f"):format(p.y)) end },
      -- 10 it never comes down on her: Pepper under the lift's platform, the lift waits above her head
      { act = function() local m = lift(); m.k, m.dir, m.waitT, m.y0, m.y1 = 0.5, -1, 0, 344, 352; tp(920, 504) end },
      { wait = 4.0 },
      { act = function(p, s) local m = lift()
          report("Pepper under the lift: it stops above her head", m.blocked and m.y1 <= p.y - p:height() + 0.01 and near(p.y, 504, 0.01),
            ("platform bottom %.1f, her head %.1f"):format(m.y1, p.y - p:height())); hold("left") end },
      { wait = 0.6 }, { act = function() release() end }, { wait = 0.9 },
      { act = function() local m = lift(); report("she steps out: it comes down to F2", near(m.y0, 504, 0.01), ("y %.1f"):format(m.y0)) end },
      -- 10b the review's case: crouched under the descending lift, then she lets go of Down and stands up. The lift
      -- must wait at her standing height (26 px + 2), so she never stands up into the platform
      { act = function() local m = lift(); m.k, m.dir, m.waitT, m.y0, m.y1 = 0.5, -1, 0, 344, 352; tp(920, 504); hold("down") end },
      { wait = 4.0 },
      { act = function(p) local m = lift()
          report("crouched under the lift: it waits at her standing height", m.blocked and p.crouch and m.y1 <= p.y - Pp.H_STAND - 2 + 0.01,
            ("platform bottom %.1f, standing head %.1f"):format(m.y1, p.y - Pp.H_STAND)); release() end },
      { wait = 0.5 },
      { act = function(p) local m = lift()
          report("she lets go of Down and stands up: her head clear of the platform", not p.crouch and m.y1 <= p.y - p:height() + 0.01,
            ("platform bottom %.1f, her head %.1f"):format(m.y1, p.y - p:height())) end },
      -- 10c a lift already lower than that over her (she crawled under it) winds back up until she has room
      { act = function(p) local m = lift(); m.dir, m.waitT = -1, 0; m.k = (504 - 486) / (504 - 184); m.y0, m.y1 = 486, 494
          tp(920, 504); api.stage().pepper.crouch = true; hold("down") end },
      { wait = 1.5 },
      { act = function(p) local m = lift()
          report("a lift too low over a crouched Pepper backs up to standing room", m.y1 <= p.y - Pp.H_STAND - 2 + 0.01 and m.y1 > p.y - Pp.H_STAND - 6,
            ("platform bottom %.1f"):format(m.y1)); release() end },
      { wait = 0.5 },
      { act = function(p) local m = lift(); report("and she stands up under it, head clear", not p.crouch and m.y1 <= p.y - p:height() + 0.01, ("head %.1f"):format(p.y - p:height())); hold("left") end },
      { wait = 0.8 }, { act = function() release() end }, { wait = 1.0 },
      -- 11 a fall into the pit: out of the bottom of the world, a heart, back to the lamp
      { act = function(p, s) s.check = { x = 100, y = 664 }; s.hearts = 3; tp(240, 600); p.onGround = false end },
      { during = 2.0 },
      { act = function(p, s) report("the pit: falling out of the world costs a heart", s.hearts == 2, "hearts " .. s.hearts)
          report("the pit: back to the lamp, the camera with her", near(p.x, 100, 0.01) and near(p.y, 664, 0.01) and p.mode == "normal" and near(s.camY, camFor(664), 1),
            ("x %.0f y %.0f %s camY %.0f"):format(p.x, p.y, p.mode, s.camY)) end },
      -- 12 the fetch at the top: pick up the ball, give it to Mia
      { act = function(p, s) s.hearts = 3; tp(s.ball.x + 18, 184); p.face = -1 end },
      { wait = 0.3 }, { act = function() love.keypressed("x") end }, { wait = 0.4 },
      { act = function(p) report("Pepper picks the ball up on the roof", p.carrying ~= nil, tostring(p.carrying ~= nil)); hold("left") end },
      { cond = function(p, s) return p.x <= s.girl.x + 34 end, act = function() release() end, limit = 3 },
      { wait = 0.3 }, { act = function(p) p.face = -1; love.keypressed("x") end }, { wait = 0.4 },
      { act = function(p, s) report("giving the ball to Mia: GOOD GIRL (FETCH 2000)", s.ball.state == "given" and s.bonus and s.bonus[2] == 2000, s.ball.state) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec_lab_tall")
    -- a scripted autopilot (the route is fixed): each step holds buttons until its condition
    local function run(dir, x, ...)                -- run (or walk) towards x
      local extra = { ... }
      return { cond = function(p) if (dir == "right" and p.x >= x) or (dir == "left" and p.x <= x) then return true end
          local h = { [dir] = true }; for _, k in ipairs(extra) do h[k] = true end; I.force = h; return false end,
        act = function() release() end, limit = 12 }
    end
    local function goTo(x)                         -- walk to x and stop there
      return { cond = function(p) if math.abs(p.x - x) < 3 then release(); return math.abs(p.vx) < 1 end
          I.force = { [p.x < x and "right" or "left"] = true, walk = true }; return false end, act = function() release() end, limit = 6 }
    end
    local function settle() return { cond = function(p) return p.onGround and math.abs(p.vx) < 1 end, act = function() end, limit = 3 } end
    local function leap(dir, toY)                  -- a held jump towards dir, until she lands at toY
      return { act = function() jump(dir, "jump") end }, { wait = 0.35 }, { act = function() hold(dir) end },
        { cond = function(p) return p.onGround and near(p.y, toY, 0.5) end, act = function() release() end, limit = 3 }
    end
    steps = { { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      run("right", 194),
      { act = function() jump("right", "jump") end }, { wait = 1 / 60 }, { act = function() hold("right") end },  -- hop the pit
      run("right", 598), settle(), goTo(606),
    }
    local ys = { 536, 504, 472, 440, 408 }
    for i, y in ipairs(ys) do
      local a, b, c, d = leap(i % 2 == 1 and "right" or "left", y)
      for _, st in ipairs({ a, b, c, d, settle() }) do steps[#steps + 1] = st end
      steps[#steps + 1] = goTo(i % 2 == 1 and 670 or 606)
    end
    local a, b, c, d = leap("right", 376)                         -- onto the beam
    for _, st in ipairs({ a, b, c, d }) do steps[#steps + 1] = st end
    for _, st in ipairs({
      run("right", 850, "walk"),                                   -- off the beam's end: the tall drop onto F2
      { cond = function(p) return p.onGround and p.y > 500 end, act = function() release() end, limit = 3 },
      settle(), { wait = 0.5 },
      { cond = function() return lift().k == 0 and lift().waitT > 0.4 end, act = function() end, limit = 20 },   -- the lift is down
      run("right", 918, "walk"), settle(),
      { cond = function(p) return lift().k >= 1 end, act = function() end, limit = 12 },                         -- ride it up
      { wait = 0.3 }, run("left", 760), settle(), run("left", 739, "walk"), settle(),
      { act = function() love.keypressed("x") end }, { wait = 0.6 },                                              -- the ball
      run("left", 636), settle(), { act = function(p) p.face = -1; love.keypressed("x") end },                    -- to Mia
      { wait = 6 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, lives %d hearts %d, %.1f s played"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    }) do steps[#steps + 1] = st end
  else  -- --test: a screenshot tour
    local function shot(name) return { act = function() love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("lt_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    local spots = { { 150, 664 }, { 440, 568 }, { 690, 536 }, { 690, 408 }, { 780, 376 }, { 860, 504 }, { 700, 184 }, { 860, 184 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.2 }
      steps[#steps + 1] = shot(("lt_%02d_spot"):format(i))
    end
    for _, st in ipairs({
      { act = function() tp(410, 568); love.filesystem.createDirectory("rec_lab_tall_look"); recLook = 0 end }, { wait = 0.5 },
      { act = function() hold("up") end }, { wait = 1.5 }, shot("lt_10_lookup"), { act = function() release() end }, { wait = 1.0 },
      { act = function() hold("down") end }, { wait = 2.0 }, shot("lt_11_lookdown"), { act = function() release() end }, { wait = 1.2 },
      { act = function() recLook = nil end },
      { act = function() local m = lift(); m.k, m.dir, m.waitT, m.y0, m.y1 = 0, 1, 0.3, 504, 512; tp(920, 504) end },
      { wait = 3.0 }, shot("lt_12_lift"), { wait = 3.0 }, shot("lt_13_lift_top"),
      { act = function() love.event.quit() end },
    }) do steps[#steps + 1] = st end
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
      if os.getenv("AUTO_TRACE") and frame % 10 == 0 then print(("F %d x %.0f y %.0f camY %.0f step %d"):format(frame, p.x, p.y, s.camY, i)) end
      if frame % 3 == 0 and not os.getenv("NO_REC") then n = n + 1; love.graphics.captureScreenshot(("rec_lab_tall/%04d.png"):format(n)) end
    end
    if recLook then recLook = recLook + 1; if recLook % 3 == 0 then love.graphics.captureScreenshot(("rec_lab_tall_look/%04d.png"):format(math.floor(recLook / 3))) end end
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
