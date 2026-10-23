-- The checks for the tall Downtown (love riverwalk --level downtown_tall <flag>; docs/downtown_tall_beatsheet.md):
--   --physics   the world and the camera; the trams on the street only; every jump of the low road (Downtown's,
--               240 px lower), of the two ways up and of the high road, simulated with Pepper's own controller from
--               where a player stands (a standing held jump unless it says otherwise; "through" = on through a
--               springy bounce); jumps that must fail (so the tiers stay apart); Downtown's old balcony route under
--               the new roofs; every drop off the high road (walk off each end, a running jump off each end, Down + A
--               through each one-way ledge) lands on a floor below with no heart lost and never in the water; the cat
--               from the loggia; no bone inside a solid, every bone within a jump of a floor; the fetch ends the level
--   --auto      the autopilot plays the high road with the ball (bark from the loggia, down for the ball, up the
--               statue, over the roofs) and the flooded square, saving every 3rd frame to rec_downtown_tall/
--   --test      a screenshot tour (dt2_*.png)
-- The jump and drop checks run on a second stage of their own, stepped 1/60 s at a time inside one frame. The
-- geese are taken out of that stage (a bite is not a fall).
local I = require("input")
local St = require("stage")
local Vc = require("vcam")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local frame, n = 0, 0
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-66s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); Vc.snap(s)
  end
  local function jump(...) hold(...); love.keypressed("space") end
  local function near(a, b, e) return math.abs(a - b) <= (e or 0.01) end
  local STREET = 424

  -- the simulation stage ---------------------------------------------------------------------------------------
  local sim
  local function simStage()
    if not sim then sim = St.new(api.stage().def); sim.critters = {} end
    return sim
  end
  local function place(st, x, y)
    local p = st.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    p.carrying, p.dropT, p.bufferT, p.coyoteT = nil, 0, 0, 0
    st.hearts, st.deadT, st.drownT, st.fallT, st.msg = 3, nil, nil, nil, nil
    st.bikes, st.zoneIn, st.bikeT = {}, {}, 99
    I.force = {}
    for _ = 1, 6 do st:update(1 / 60, {}) end                     -- settle: she finds her floor
  end
  -- runs a plan(p, t, air) -> force table, press jump? until she lands after being in the air (or maxT). A landing
  -- on a springy top (bounce = h) launches her again at once; it counts as a landing (bounced = true) unless
  -- through is set, when she flies on. Returns { x, y, landed, water, hearts, air, bounced, stuck }
  local function run(st, plan, maxT, through)
    local p, air, t = st.pepper, false, 0
    for _ = 1, math.floor((maxT or 4) * 60) do
      local force, press = plan(p, t, air)
      I.force = force or {}
      local vy0 = p.vy
      st:update(1 / 60, press and { jump = true } or {})
      t = t + 1 / 60
      if not p.onGround then air = true end
      if p.mode == "drown" or st.drownT or st.fallT or p.mode == "gone" then
        I.force = {}; return { x = p.x, y = p.y, water = true, hearts = st.hearts, air = air } end
      if air and vy0 > 0 and p.vy < -100 and not press and not through then              -- a springy top launched her
        I.force = {}; return { x = p.x, y = p.y, landed = true, bounced = true, hearts = st.hearts, air = air } end
      if air and p.onGround and (p.mode == "normal" or p.mode == "hurt") then
        I.force = {}; return { x = p.x, y = p.y, landed = true, hearts = st.hearts, air = air, ground = p.ground } end
    end
    I.force = {}
    return { x = p.x, y = p.y, landed = p.onGround, hearts = st.hearts, air = air, stuck = true }
  end
  -- a jump: from (x, y), towards dir ("right", "left" or nil: straight up). run = take-off x for a running jump
  -- (she runs from x and presses A there); tap = a tapped hop; brake = let go of the direction past this x
  local function leap(j)
    local st = simStage(); place(st, j.x, j.y)
    local pressed = false
    return run(st, function(p, t, air)
      local f = {}
      if j.dir and not (j.brake and ((j.dir == "right" and p.x >= j.brake) or (j.dir == "left" and p.x <= j.brake))) then f[j.dir] = true end
      if j.run and not pressed then
        if (j.dir == "right" and p.x >= j.run) or (j.dir == "left" and p.x <= j.run) then pressed = true; f.jump = true; return f, true end
        return f, false
      end
      if not pressed then pressed = true; f.jump = true; return f, true end
      if not j.tap then f.jump = true end
      return f, false
    end, 5, j.through)
  end

  local steps
  if mode == "--physics" then
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      -- 0 the world and the camera
      { act = function(p, s)
          report("a tall map: 3520 x 480 px (440 x 60 cells, 11 x 2 screens)", s.world.width == 3520 and s.world.height == 480, ("%d x %d"):format(s.world.width, s.world.height))
          report("on the street (y 424) the camera rests at the bottom of the world", near(p.y, STREET) and s.camY == s.camYMax and s.camYMax == 240,
            ("feet %.0f, camY %.0f of %d: the street is at screen y %.0f, as in Downtown"):format(p.y, s.camY, s.camYMax, p.y - s.camY))
          local okZ = #s.def.bikes == 2
          for _, z in ipairs(s.def.bikes) do okZ = okZ and z.roadY == STREET and z.kind == "cargo" and z.w == 80 and z.h == 26 end
          report("2 cargo bike zones on the street (roadY 424, hit box 80 x 26)", okZ, ("%d zones"):format(#s.def.bikes))
          report("Downtown's art, placed from the street line (art town, foot 424)", s.def.art == "town" and s.def.foot == STREET,
            ("art %s, foot %s"):format(tostring(s.def.art), tostring(s.def.foot)))
        end },
      -- 0b the trams: one sets off as she walks in on the street, drives at y 424 and hurts her there; on the
      -- shelter roof it passes under her; on the roofs above tram street no tram comes
      { act = function()
          local st = simStage()
          for zi, z in ipairs(st.def.bikes) do
            place(st, z.zoneX0 - 30, STREET); st.bikeT = 2.5
            local sent, ys, hurt, warned = nil, {}, false, false
            for f = 1, 60 * 6 do
              I.force = (st.pepper.x < z.zoneX0 + 30) and { right = true, walk = true } or {}
              local h = st.hearts
              st:update(1 / 60, {})
              local c = st.bikes[1]
              if c and not sent then sent = st.pepper.x; warned = c.warn > 0.9 end
              if c then ys[#ys + 1] = c.y end
              if st.hearts < h then hurt = true; break end
            end
            I.force = {}
            local okY = #ys > 0; for _, y in ipairs(ys) do if not near(y, STREET, 0.01) then okY = false end end
            report(("cargo bike %d sets off as she walks in on the street, warned 1 s before, drives at y 424"):format(zi), sent ~= nil and sent > z.zoneX0 and sent < z.zoneX0 + 20 and warned and okY,
              ("at x %s, %d frames at y %s"):format(tostring(sent and math.floor(sent)), #ys, tostring(ys[1])))
            report(("cargo bike %d: standing on the street, it hurts her"):format(zi), hurt)
            local sh
            for _, pr in ipairs(st.def.props) do if pr.name == "SHELTER" and pr.x0 > z.zoneX0 and pr.x1 <= z.zoneX1 + 10 then sh = pr end end
            place(st, (sh.x0 + sh.x1) / 2, sh.y0); st.zoneIn[z] = true; st.bikeT = 0
            local passed = false
            for f = 1, 60 * 6 do st:update(1 / 60, {}); if st.bikes[1] and st.bikes[1].x < sh.x0 - 30 then passed = true end end
            report(("cargo bike %d: on the shelter roof (y 376) it passes under her"):format(zi), passed and st.hearts == 3 and near(st.pepper.y, sh.y0), ("hearts %d"):format(st.hearts))
          end
          local z = st.def.bikes[1]
          place(st, 2044, 248); local any = false
          for f = 1, 60 * 8 do st:update(1 / 60, {}); if #st.bikes > 0 then any = true end end
          report("on the roofs over cargo bike street no cargo bike comes", not any and near(st.pepper.y, 248), ("y %.0f"):format(st.pepper.y))
        end },
      -- 0c the back lane's vintage tram (scenery, D1): it comes in off the right edge, stops at its sign for its
      -- dwell, drives off to the left and is gone off screen; it is never a hazard
      { act = function()
          local st = simStage()
          report("2 tram lanes in the back lane (rails at y 414, behind Pepper's line)", #st.trams == 2 and st.def.trams[1].y1 == STREET - 10 and st.def.trams[2].y1 == STREET - 10,
            ("%d lanes"):format(#st.trams))
          place(st, 2000, STREET); st.trams[1].t = 0.5; st.trams[1].car = nil
          local came, stopped, waited, left, hurt, cam0 = nil, nil, 0, false, false, st.cam
          for f = 1, 60 * 25 do
            st.bikes, st.bikeT = {}, 99
            local h = st.hearts
            st:update(1 / 60, {})
            if st.hearts < h then hurt = true end
            local c = st.trams[1].car
            if c and not came then came = c.x - 150 - st.cam end
            if c and c.state == "stop" then stopped = c.x; waited = waited + 1 / 60 end
            if stopped and not c then left = true; break end
          end
          local l = st.def.trams[1]
          report("the tram comes in off the right edge of the screen", came and came > 320, ("its front %s px from the left edge"):format(tostring(came and math.floor(came))))
          report("it stops with its front door at the tram stop sign, waits 3 s, drives off left", stopped and near(stopped - 126, l.stop, 1) and near(waited, l.dwell, 0.05) and left,
            ("stopped at %s (sign %d), waited %.2f s, gone %s"):format(tostring(stopped and math.floor(stopped - 126)), l.stop, waited, tostring(left)))
          report("the tram is scenery: no heart lost, never in the hazards", not hurt and st.hearts == 3, ("hearts %d"):format(st.hearts))
        end },
      { act = function() tp(1852, 256) end }, { wait = 1.2 },
      { act = function(p, s) report("on the gallery (y 256) the camera follows her up", near(s.camY, 256 - Vc.FLOOR, 1),
          ("camY %.1f, her feet at screen y %.0f"):format(s.camY, p.y - s.camY)) end },
      -- 1 Pepper's numbers, measured in the simulation
      { act = function()
          local st = simStage(); place(st, 260, STREET); local minY = STREET
          run(st, function(p, t) minY = math.min(minY, p.y); return { jump = true }, t == 0 end, 2)
          report("her held jump: 46 px", near(STREET - minY, 46, 1), ("%.1f px"):format(STREET - minY))
          place(st, 260, STREET); minY = STREET
          run(st, function(p, t) minY = math.min(minY, p.y); return t == 0 and { jump = true } or {}, t == 0 end, 2)
          report("her tapped hop: 24 px", near(STREET - minY, 24, 2), ("%.1f px"):format(STREET - minY))
        end },
      -- 2 every jump, simulated
      { act = function()
          local J = {
            -- the low road: Downtown, 240 px lower
            { "low: hop onto the low crate (16 px, tapped)", x = 124, y = STREET, dir = "right", tap = true, brake = 160, to = 408 },
            { "low: hop onto the high crate (16 px more)", x = 158, y = 408, dir = "right", tap = true, brake = 192, to = 392 },
            { "low: held jump onto the cafe table (26 px)", x = 350, y = STREET, dir = "right", brake = 392, to = 398 },
            -- (r6/levels) the crate steps: two tap hops instead of a held jump, at the terrace, the stall, the tub
            { "low: hop onto the terrace crate (16 px, tapped)", x = 270, y = STREET, dir = "right", tap = true, brake = 316, to = 408 },
            { "low: terrace crate -> the table (10 px, tapped)", x = 316, y = 408, dir = "right", tap = true, brake = 392, to = 398 },
            { "low: hop onto the stall's crate (16 px, tapped)", x = 626, y = STREET, dir = "right", tap = true, brake = 672, to = 408 },
            { "low: stall's crate -> the stall (12 px, tapped)", x = 672, y = 408, dir = "right", tap = true, brake = 720, to = 396 },
            { "low: hop onto the plaza crate (16 px, tapped)", x = 1340, y = STREET, dir = "right", tap = true, brake = 1384, to = 408 },
            { "low: plaza crate -> the tub and on up to the pedestal (tapped)", x = 1384, y = 408, dir = "right", tap = true, brake = 1424, to = 384 },
            { "low: table -> its parasol (36 px, straight up; r7: 8 px lower)", x = 392, y = 398, to = 362 },
            { "low: parasol -> the shop sign (running, gold; r7: both 8 px lower)", x = 480, y = 362, dir = "right", run = 518, to = 328 },
            { "low: onto the stall's counter (28 px)", x = 660, y = STREET, dir = "right", brake = 714, to = 396 },
            { "low: counter -> the stall's awning (40 px)", x = 714, y = 396, to = 356 },
            { "low: crates -> the second awning (40 px)", x = 846, y = 392, dir = "right", brake = 900, to = 352 },
            { "low: the springy awning launches her over the crate wall", x = 980, y = STREET, dir = "right", through = true, to = 360 },
            { "way up A: the springier awning reaches the bakery sign (r7: a tap from the crate step)", x = 1186, y = 400, dir = "right", run = 1196, tap = true, brake = 1266, through = true, to = 304 },
            { "low: onto the flower tub (28 px)", x = 1350, y = STREET, dir = "right", brake = 1410, to = 396 },
            { "low: tub -> pedestal (12 px, tapped)", x = 1424, y = 396, dir = "right", tap = true, brake = 1460, to = 384 },
            { "low: street -> pedestal from the right (40 px, with the ball after the cat)", x = 1522, y = STREET, dir = "left", brake = 1470, to = 384 },
            { "low: pedestal -> the statue's arm (36 px)", x = 1470, y = 384, dir = "right", brake = 1488, to = 348 },
            { "low: arm -> the statue's hat (32 px, gold)", x = 1486, y = 348, to = 316 },
            { "low: onto the fountain's rim (tapped)", x = 1694, y = STREET, dir = "right", run = 1700, tap = true, brake = 1726, to = 408 },
            { "low: rim -> the fountain bowl (tapped, running)", x = 1724, y = 408, dir = "right", run = 1730, tap = true, brake = 1792, to = 400 },
            { "low: bowl -> the far rim (tapped, running)", x = 1792, y = 400, dir = "right", run = 1798, tap = true, brake = 1840, to = 408 },
            { "low: rim -> the gate's roof (20 px)", x = 1856, y = 408, dir = "right", brake = 1900, to = 388 },
            { "low: kiosk -> the shelter roof", x = 2004, y = 388, dir = "right", brake = 2070, to = 376 },
            { "low: tub -> table -> springy parasol -> the flower balcony", x = 2296, y = 396, dir = "right", run = 2306, through = true, to = 328 },
            { "low: the canal awning launches her over the water", x = 2470, y = 328, dir = "right", run = 2476, through = true, to = 360 },
            { "low: the flooded square: crate -> three parasols -> courtyard gate", x = 2802, y = 408, dir = "right", through = true, to = 388 },
            { "low (r7): the same with a tapped hop onto the first parasol (20 px)", x = 2802, y = 408, dir = "right", tap = true, through = true, to = 388 },
            -- way up B (with the ball): the hat to the loggia; (r7) or the plaza's springy parasol straight to the loggia
            { "way up B (r7): street -> the springy parasol -> the loggia (held jump left)", x = 1574, y = STREET, dir = "left", brake = 1546, through = true, to = 280 },
            { "way up B (r7): a tapped hop onto the parasol (20 px) bounces her up to the loggia too", x = 1574, y = STREET, dir = "left", tap = true, brake = 1546, through = true, to = 280 },
            { "way up B: the statue's hat -> the loggia (36 px)", x = 1464, y = 316, to = 280 },
            -- the high road, west to east
            { "high: bakery sign -> the balcony (gap 18, 32 up)", x = 1293, y = 304, dir = "right", to = 272 },
            { "high: balcony -> the loggia (gap 24, 8 down)", x = 1375, y = 272, dir = "right", to = 280 },
            { "high: loggia -> onto the guild roof's steps (y 244-276)", x = 1519, y = 280, dir = "right", brake = 1572, to = 260, tol = 16 },
            { "high: ridge -> the chimney: THE GOLDEN BONE (44 up)", x = 1611, y = 244, dir = "right", brake = 1636, to = 200 },
            { "high: gallery -> gallery (gap 48)", x = 1751, y = 256, dir = "right", to = 256 },
            { "high: gallery -> dormer (gap 32, 8 down)", x = 1871, y = 256, dir = "right", to = 264 },
            { "high: dormer -> roof ledge (gap 40, 16 up)", x = 1959, y = 264, dir = "right", to = 248 },
            { "high: roof ledge -> roof ledge (gap 40, 16 down)", x = 2055, y = 248, dir = "right", to = 264 },
            { "high: ledge -> the window awning: bounce up to the flower roof", x = 2151, y = 264, dir = "right", through = true, to = 232 },
            { "high: flower roof -> last ledge (gap 40, 16 down)", x = 2359, y = 232, dir = "right", to = 248 },
            { "high: last ledge -> the footbridge (gap 16, 24 down)", x = 2447, y = 248, dir = "right", to = 272 },
            -- running jumps of the high road (a child runs): they land on the next ledge, not past it
            { "high, running: gallery -> gallery", x = 1700, y = 256, dir = "right", run = 1751, to = 256 },
            { "high, running: dormer -> roof ledge", x = 1930, y = 264, dir = "right", run = 1959, to = 248 },
            { "high, running: roof ledge -> roof ledge", x = 2024, y = 248, dir = "right", run = 2055, to = 264 },
            { "high, running: flower roof -> last ledge", x = 2300, y = 232, dir = "right", run = 2359, to = 248 },
            -- Downtown's old balcony route (the middle tier) under the new roofs: no bumped head
            { "middle: arm -> first balcony (running)", x = 1500, y = 348, dir = "right", run = 1514, to = 344 },
            { "middle: first balcony -> second (running)", x = 1580, y = 344, dir = "right", run = 1604, to = 336 },
            { "middle: second balcony -> the fountain's top tier (running)", x = 1680, y = 336, dir = "right", run = 1708, to = 344 },
            { "middle: tier -> last balcony (running)", x = 1790, y = 344, dir = "right", run = 1812, to = 344 },
          }
          for _, j in ipairs(J) do
            local r = leap(j)
            report(j[1], r.landed and not r.water and near(r.y, j.to, j.tol or 0.01) and r.hearts == 3,
              ("lands x %.0f y %.1f (want %d)%s"):format(r.x, r.y, j.to, r.water and " IN THE WATER" or (r.stuck and " (never landed)" or "")))
          end
          -- the tiers stay apart: the same jumps from below fall short
          for _, j in ipairs({ { "the loggia is out of reach from the street", x = 1420, y = STREET, dir = "right", run = 1430, bad = 280 },
                               { "the loggia is out of reach from the statue's arm (68 px)", x = 1500, y = 348, bad = 280 },
                               { "the balcony is out of reach from the springy bakery awning", x = 1186, y = 400, dir = "right", run = 1196, through = true, bad = 272 },
                               { "the flower roof is out of reach from the springy parasol", x = 2296, y = 396, dir = "right", run = 2306, brake = 2330, through = true, bad = 232 } }) do
            local r = leap(j)
            report(j[1], not near(r.y, j.bad, 1) and r.y > j.bad, ("ends at y %.0f"):format(r.y))
          end
          -- the guild roof: she walks up its 4 px steps to the ridge, where the chimney stops her
          local st = simStage(); place(st, 1566, 272)
          run(st, function(p, t) return t < 1.0 and { right = true, walk = true } or {}, false end, 1.2)
          report("high: she walks up the guild roof's steps to the ridge; the chimney stops her", near(st.pepper.y, 244) and st.pepper.x > 1600 and st.pepper.x < 1612,
            ("x %.0f y %.0f"):format(st.pepper.x, st.pepper.y))
          place(st, 1636, 200)
          local r = run(st, function(p, t) return { right = true, walk = true }, false end, 2)
          report("high: off the chimney she lands on the roof's far side", r.landed and r.y >= 244 and r.y <= 256 and r.hearts == 3, ("x %.0f y %.0f"):format(r.x, r.y))
          place(st, 1740, 256)
          r = run(st, function(p, t) return { right = true, walk = true }, false end, 2)
          report("high: walking off the gallery into its gap lands on the fountain's top tier", r.landed and near(r.y, 344) and not r.water, ("x %.0f y %.0f"):format(r.x, r.y))
          place(st, 2600, 272)
          r = run(st, function(p, t) return { right = true, walk = true }, false end, 2)
          report("high: off the footbridge's end onto the crates on the far quay", r.landed and near(r.y, 360), ("x %.0f y %.0f"):format(r.x, r.y))
        end },
      -- 3 every way off the high road lands on a floor below: no heart, never the water
      { act = function()
          local st = simStage()
          local ledges = {}
          for _, r in ipairs(st.world.rects) do
            if not r.terrain and (r.kind == "oneway" or r.kind == "solid") and r.y0 <= 304 and r.x1 - r.x0 >= 16 then ledges[#ledges + 1] = r end
          end
          table.sort(ledges, function(a, b) return a.x0 < b.x0 end)
          local bad, cases = {}, 0
          local function check(label, r, res, y0)
            cases = cases + 1
            if res.water or not res.landed or res.hearts ~= 3 or (res.y <= y0 and not res.jumped and not res.bounced) then
              bad[#bad + 1] = ("%s x %d-%d y %d: %s at x %.0f y %.0f"):format(label, r.x0, r.x1, r.y0, res.water and "WATER/OUT" or (res.landed and "landed" or "stuck"), res.x, res.y)
            end
          end
          for _, r in ipairs(ledges) do
            local y = r.y0
            for _, d in ipairs({ { "left", r.x0 + 6 }, { "right", r.x1 - 6 } }) do
              place(st, d[2], y)
              if near(st.pepper.y, y) then
                local res = run(st, function(p, t, air) if air then return {} end; return t < 3 and { [d[1]] = true, walk = true } or {}, false end, 6)
                if res.air then check("walk off " .. d[1], r, res, y) end      -- (no edge: the floor goes on)
                place(st, d[1] == "left" and r.x0 + 40 or r.x1 - 40, y)
                if near(st.pepper.y, y) then
                  local pressed = false
                  res = run(st, function(p, t, air)
                    local f = { [d[1]] = true }
                    if not pressed and ((d[1] == "left" and p.x <= r.x0 + 14) or (d[1] == "right" and p.x >= r.x1 - 14)) then pressed = true; f.jump = true; return f, true end
                    if pressed then f.jump = true end
                    return f, false end, 6)
                  res.jumped = true                                            -- (onto the next high ledge: fine too)
                  check("run-jump off " .. d[1], r, res, y)
                end
              end
            end
            if r.kind == "oneway" and r.x1 - r.x0 >= 24 then
              place(st, (r.x0 + r.x1) / 2, y)
              local res = run(st, function(p, t) return t == 0 and { down = true } or {}, t == 0 end, 6)
              check("drop through", r, res, y)
            end
          end
          for i = 1, math.min(#bad, 12) do print("        " .. bad[i]) end
          report("every way off the high road lands on a floor below, no heart lost", #bad == 0, ("%d ledges, %d drops, %d bad"):format(#ledges, cases, #bad))
          local ok = true
          for _, x in ipairs({ { 1750, 256 }, { 1830, 256 }, { 2592, 272 } }) do
            place(st, x[1], x[2]); run(st, function(p, t) return t == 0 and { down = true } or {}, t == 0 end, 1)
            ok = ok and near(st.pepper.y, x[2]) and st.pepper.onGround
          end
          report("the gallery and the footbridge are solid: no drop into the water", ok)
        end },
      -- 4 the cat, from above: a bark from the loggia scares it, the ball drops to the street
      { act = function()
          local st = simStage()
          local function fresh() st.cat = nil; local s2 = St.new(st.def); s2.critters = {}; return s2 end
          local s2 = fresh(); place(s2, 1430, 280); s2.pepper.face = 1; s2:barkAtCat()
          report("cat: a bark from the loggia's far end (x 1430) only makes it look up", s2.cat.state == "sit" and s2.cat.heard ~= nil)
          s2 = fresh(); place(s2, 1376, 272); s2.pepper.face = 1; s2:barkAtCat()
          report("cat: from the balcony it does not even hear", s2.cat.state == "sit")
          s2 = fresh(); place(s2, 1496, 280); s2.pepper.face = 1; s2:barkAtCat()
          for _ = 1, 150 do s2:update(1 / 60, {}) end
          local b = s2.ball
          report("cat: a bark from right above it (loggia, x 1496) scares it off", s2.cat.state ~= "sit")
          report("cat: the ball drops to the street", b.state == "rest" and near(b.y, STREET), ("ball %s at x %.0f y %.0f"):format(b.state, b.x, b.y))
          -- down from the loggia with Down + A, to the ball
          place(s2, 1500, 280)
          local r = run(s2, function(p, t) return t == 0 and { down = true } or {}, t == 0 end, 3)
          report("Down + A off the loggia: she lands on the arm (a step down to the street)", r.landed and near(r.y, 348) and r.hearts == 3, ("y %.0f"):format(r.y))
        end },
      -- 5 bones and secrets
      { act = function()
          local st = simStage(); local w = st.world
          local inside, far = {}, {}
          for _, b in ipairs(st.def.bones) do
            if w:solidIn(b.x - 3, b.x + 3, b.y - 14, b.y - 4) then inside[#inside + 1] = ("%d,%d"):format(b.x, b.y) end
            local found = false
            for dx = -40, 40, 8 do for dy = 0, 46 do
              if not found and w:floor(b.x + dx - 12, b.x + dx + 12, b.x + dx, b.y + dy - 1, b.y + dy + 1, b.y + dy - 2) then found = true end
            end end
            for _, pr in ipairs(st.def.props) do        -- over a springy top: on the arc of its bounce
              if pr.bounce and b.x > pr.x0 - 40 and b.x < pr.x1 + 90 and b.y >= pr.y0 - pr.bounce - 8 and b.y < pr.y0 then found = true end
            end
            if not found then far[#far + 1] = ("%d,%d"):format(b.x, b.y) end
          end
          local supers, golden, high = 0, 0, 0
          for _, b in ipairs(st.def.bones) do if b.super then supers = supers + 1 end; if b.golden then golden = golden + 1 end; if b.y < 320 then high = high + 1 end end
          report("no bone inside a solid", #inside == 0, ("%d bones; %s"):format(#st.def.bones, table.concat(inside, " ")))
          report("every bone is within a held jump of a floor (or a bounce)", #far == 0, table.concat(far, " "))
          report("one golden bone (and the gold super bones)", golden == 1, ("%d golden, %d super, %d up high"):format(golden, supers, high))
          report("5 secrets: shop sign, statue hat, rooftops, bakery sign, golden bone", #st.def.secrets == 5, ("%d"):format(#st.def.secrets))
          local hl = 0; for _, l in ipairs(st.def.lamps) do if l.y < 320 then hl = hl + 1 end end
          report("8 lamps: 6 on the street, 2 up high", #st.def.lamps == 8 and hl == 2, ("%d, %d high"):format(#st.def.lamps, hl))
        end },
      -- 6 the fetch: with the ball to Mia at the river stairs: GOOD GIRL, the level ends
      { act = function(p, s) s.cat.state = "gone"; s.cat.x = -999
          s.ball.state, s.ball.x, s.ball.y = "rest", 3420, STREET; tp(3398, STREET); p.face = 1 end },
      { wait = 0.3 }, { act = function() love.keypressed("x") end }, { wait = 0.5 },
      { act = function(p) report("by the river stairs Pepper picks the ball up", p.carrying ~= nil); hold("right", "walk") end },
      { cond = function(p, s) return p.x >= s.girl.x - 36 end, act = function(p) release(); p.face = 1 end, limit = 4 }, { wait = 0.3 },
      { act = function() love.keypressed("x") end }, { wait = 0.4 },
      { act = function(p, s) report("giving the ball to Mia: GOOD GIRL (FETCH 2000)", s.ball.state == "given" and s.bonus and s.bonus[2] == 2000, s.ball.state) end },
      { wait = 2.6 },
      { act = function(p, s) report("the fetch ends the level", s.events.clear == true or api.getState() ~= "play", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
    require("tests_safety")(steps, api, report)                  -- the safety nets (r6/engine), before the summary
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec_downtown_tall")
    local function at(cond, act, limit) return { cond = cond, act = act or function() end, limit = limit or 6 } end
    local function settle() return at(function(p) return p.onGround and math.abs(p.vx) < 1 end, function() release() end, 3) end
    local function runTo(x)                         -- run right (or left) and brake to stop about at x
      return at(function(p) local d = x > p.x and 1 or -1
          if math.abs(p.x - x) <= 13 then release(); return true end
          hold(d > 0 and "right" or "left"); return false end, function() release() end, 12), settle()
    end
    local function goTo(x)                          -- walk to x and stop
      return at(function(p) if math.abs(p.x - x) < 2.5 then release(); return math.abs(p.vx) < 1 end
          hold(p.x < x and "right" or "left", "walk"); return false end, function() release() end, 6)
    end
    local function leapTo(dir, toY, brake)          -- a held jump (dir or straight up) until she lands at toY
      return { act = function() if dir then jump(dir, "jump") else jump("jump") end end },
        at(function(p) if brake and ((dir == "right" and p.x >= brake) or (dir == "left" and p.x <= brake)) then hold("jump") end
          return p.onGround and p.vy == 0 and near(p.y, toY, 0.5) end, function() release() end, 4)
    end
    local function add(list) for _, st in ipairs(list) do steps[#steps + 1] = st end end
    local function hop(x, dir, toY, brake) local a, b = runTo(x); local c = goTo(x); local e, f = leapTo(dir, toY, brake); add({ a, b, c, e, f }) end
    local Y = function(y) return y + 240 end        -- Downtown's feet lines, 240 px lower
    steps = { { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 } }
    add({
      at(function() return true end, function() hold("right") end),
      -- 1 old town lane: a hop onto each crate (Downtown's autopilot, 240 px lower)
      at(function(p) return p.x >= 106 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 138 end, function() release() end),
      at(function(p) return p.onGround and p.y <= Y(169) end, function() hold("right") end),
      at(function(p) return p.x >= 152 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(153) end, function() hold("right") end),
      -- 2 cafe terrace: table, parasol, parasol, the shop sign (gold)
      at(function(p) return p.x >= 270 and p.onGround and p.y > Y(183) end, function() jump("right", "jump") end),   -- the crate (r6/levels)
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(169) end, function() hold("right") end),
      at(function(p) return p.x >= 318 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(159) end, function() release() end),
      at(function(p) return math.abs(p.vx) < 1 end, function() jump("jump") end),
      at(function(p) return p.onGround and p.y <= Y(122) end, function() hold("right") end),         -- (r7: both parasols at 362, walk across)
      at(function(p) return p.x >= 518 end, function() jump("right", "jump") end),
      at(function(p) return p.vy > 0 and p.x >= 560 end, function() release() end),
      at(function(p) return p.onGround and p.y <= Y(88) end, function() hold("right") end),
      at(function(p) return not p.onGround and p.x > 580 end, function() release() end),   -- (r7: let go once she is off the sign, never on it)
      at(function(p) return p.onGround and p.y >= Y(183) end, function() hold("right") end),
      -- 3 market: the stall, its awning, down, the crates, the second awning
      at(function(p) return p.x >= 628 end, function() jump("right", "jump") end),         -- (r7) the crate step: a tap,
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(168) end, function() jump("right", "jump") end),   -- and a tap onto the stall
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(157) end, function() release() end),
      at(function(p) return p.x >= 714 or math.abs(p.vx) < 1 end, function() jump("jump") end),
      at(function(p) return p.onGround and p.y <= Y(117) end, function() hold("right") end),
      at(function(p) return not p.onGround and p.x > 740 end, function() release() end),      -- (r7: once off the awning)
      at(function(p) return p.onGround and p.y >= Y(183) end, function() hold("right") end),
      at(function(p) return p.x >= 774 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.x >= 800 end, function() release() end),
      at(function(p) return p.onGround and p.y <= Y(169) end, function() hold("right") end),
      at(function(p) return p.x >= 808 end, function() jump("right", "jump") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(153) end, function() hold("right") end),
      at(function(p) return p.x >= 846 end, function() jump("right", "jump") end),
      at(function(p) return p.vy > 0 end, function() release() end),
      at(function(p) return p.onGround and p.y <= Y(113) end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= Y(183) end, function() hold("right") end),
      -- 4 the bakery row: the springy awning over the crates; the springier one up to the bakery sign (way up A)
      at(function(p) return p.onGround and p.y >= Y(183) and p.x >= 960 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.x > 1100 end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= Y(160) and p.x >= 1180 end, function() hold("right") end),   -- (r7) down onto the crate step (400)
      at(function(p) return p.x >= 1196 end, function() jump("right", "jump") end),                -- a tap onto the springier awning
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.vy < 0 and p.y < Y(140) and p.x >= 1266 end, function() hold("jump") end),
      at(function(p) return p.onGround and p.y <= Y(65) end, function() release() end),
    })
    -- the high road: onto the balcony, the loggia; bark the cat off from right above it
    hop(1293, "right", 272); hop(1375, "right", 280)
    add({ goTo(1496), { wait = 0.2 }, { act = function(p) p.face = 1; love.keypressed("z") end }, { wait = 1.4 },
      -- down for the ball: Down + A onto the arm, off the arm to the street, pick it up
      goTo(1500), { act = function() hold("down"); love.keypressed("space") end }, { wait = 0.05 }, { act = function() release() end },
      at(function(p) return p.onGround and near(p.y, 348, 0.5) end),
      at(function() return true end, function() hold("right", "walk") end),
      at(function(p) return p.onGround and p.y > 420 end, function() release() end, 4),
      at(function(p, s)                                                                        -- walk up to the ball
        local b = s.ball
        local want = p.x < b.x and 1 or -1
        if p.face == want and math.abs(p.x + p.face * 18 - b.x) < 20 and math.abs(p.vx) < 1 then release(); return true end
        local tx = b.x - want * 18
        if p.face ~= want then hold(want > 0 and "right" or "left", "walk")
        elseif p.x < tx - 3 then hold("right", "walk") elseif p.x > tx + 3 then hold("left", "walk") else release() end
        return false end, nil, 6),
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.5 },
    })
    -- way up B with the ball (r7): the plaza's springy parasol, a held jump onto it from its right, up to the loggia
    hop(1574, "left", 280, 1546)
    -- the guild roof, the chimney (the golden bone), the gallery, the roof ledges, the window awning, the footbridge
    hop(1519, "right", 256, 1572)
    add({ at(function() return true end, function() hold("right", "walk") end), at(function(p) return p.x >= 1606 end, function() release() end), settle() })
    hop(1611, "right", 200, 1636)
    add({ at(function() return true end, function() hold("right", "walk") end), at(function(p) return p.onGround and p.y >= 255 end, function() release() end), settle() })
    hop(1751, "right", 256); hop(1871, "right", 264); hop(1959, "right", 248); hop(2055, "right", 264)
    add({ runTo(2151), goTo(2151), { act = function() jump("right", "jump") end },
      at(function(p) return p.onGround and near(p.y, 232, 0.5) end, function() release() end, 4) })
    hop(2359, "right", 248); hop(2447, "right", 272)
    -- off the footbridge onto the crates, down to the street; the flooded square (Downtown's autopilot)
    add({
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.onGround and p.y >= Y(183) end, function() hold("right") end, 6),
      at(function(p) return p.x >= 2770 end, function() jump("right") end),
      { wait = 1 / 60 }, { act = function() hold("right") end },
      at(function(p) return p.onGround and p.y <= Y(169) end, function() release() end),
      at(function(p) return math.abs(p.vx) < 1 end, function() jump("right", "jump") end),
      -- 11 tram street again: the last bounce lands on the tram shed; wait for the fast tram, on over the shelter
      at(function(p) return p.onGround and p.y <= Y(149) and p.x > 3060 end, function() release() end, 9),
      at(function(p, s) return s.bikes[1] ~= nil end, function() end, 12),
      at(function(p, s) return s.bikes[1] == nil end, function() hold("right") end, 12),
      at(function(p) return p.x >= 3162 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y <= Y(137) end, function() release() end),
      at(function(p, s) return #s.bikes == 0 end, function() end, 12),
      at(function(p, s) return s.bikes[1] and s.bikes[1].x < p.x - 60 end, function() hold("right") end, 12),
      at(function(p, s) return p.onGround and p.y >= Y(183) and p.x >= s.girl.x - 40 end, function() release() end, 9),
      { wait = 0.3 }, { act = function() love.keypressed("x") end },
      at(function() return api.getState() == "clear" end, function() end, 9),
      { wait = 6 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    })
  else  -- --test: a screenshot tour
    local function shot(name) return { act = function() love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("dt2_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    local spots = { { 60, STREET }, { 1180, STREET }, { 1293, 304 }, { 1496, 280 }, { 1500, STREET }, { 1636, 200 }, { 1752, 256 },
                    { 2044, 248 }, { 2236, 216 }, { 2560, 272 }, { 2900, STREET }, { 3420, STREET } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.8 }
      steps[#steps + 1] = shot(("dt2_%02d_spot"):format(i))
    end
    for _, st in ipairs({ { act = function() tp(1460, STREET) end }, { wait = 0.5 }, { act = function() hold("up") end }, { wait = 1.6 },
      shot("dt2_20_lookup_from_the_plaza"), { act = function() release() end },
      { act = function() local s = api.stage(); s.hearts = 3; s.bikes, s.zoneIn, s.bikeT = {}, {}, 2.5; tp(1910, STREET); hold("right") end },
      { wait = 0.45 }, shot("dt2_21_cargo_warning"), { act = function() release(); tp(2084, 376) end }, { wait = 1.6 }, shot("dt2_22_cargo_under_the_shelter"),
      -- r8/levels: the cargo bike passing under Pepper on the kiosk; the vintage tram at its stop in the back lane
      { act = function() local s = api.stage(); tp(2000, 388); s.bikeT = 99; s.zoneIn[s.def.bikes[1]] = true; s.bikes = { { x = 2120, y = STREET, warn = -1, zone = s.def.bikes[1], speed = 110 } } end },
      { wait = 0.5 }, shot("dt2_23_cargo_bike_passes"),
      { act = function() local s = api.stage(); tp(2000, 388); s.bikes, s.bikeT = {}, 99; s.zoneIn[s.def.bikes[1]] = true; s.trams[1].car = nil; s.trams[1].t = 0.1 end },
      { cond = function(p, s) local c = s.trams[1].car; return c and c.state == "stop" end, act = function() end, limit = 12 },
      { wait = 1.0 }, shot("dt2_24_vintage_tram_at_its_stop"),
      { act = function() local s = api.stage(); tp(3120, 388); s.bikes, s.bikeT = {}, 99; s.zoneIn[s.def.bikes[2]] = true; s.trams[2].car = nil; s.trams[2].t = 0.1 end },
      { wait = 2.6 }, shot("dt2_25_vintage_tram_coming_in"),
      { act = function() love.event.quit() end } }) do steps[#steps + 1] = st end
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
      if frame % 3 == 0 and not os.getenv("NO_REC") then n = n + 1; love.graphics.captureScreenshot(("rec_downtown_tall/%04d.png"):format(n)) end
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
