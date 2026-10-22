-- The checks for the tall City Park (love riverwalk --level citypark_tall <flag>; docs/citypark_tall_beatsheet.md):
--   --physics   the world and the camera; every jump of the low road's new climb and of the high road, simulated
--               with Pepper's own controller from where a player stands (a standing held jump unless it says
--               otherwise); every drop off the high road (walk off each end, a running jump off each end, Down + A
--               through each one-way ledge) lands on a floor below with no heart lost and never in the water; the
--               magpie: from each perch the ball falls onto a floor Pepper can reach, the high perches only answer
--               a bark from up high, the last perch (its nest in the big oak) stays put; no bone inside a solid,
--               every bone within a jump of a floor; the fetch to Mia ends the level
--   --auto      the autopilot plays the high road and the finale in the big oak, saving every 3rd frame to
--               rec_citypark_tall/ (for the GIF)
--   --test      a screenshot tour (ct_*.png)
-- The jump and drop checks run on a second stage of their own, stepped 1/60 s at a time inside one frame, so the
-- hundred-odd jumps take a second, not minutes. The geese are taken out of that stage (a bite is not a fall).
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
  local PATH = 328

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
    I.force = {}
    for _ = 1, 6 do st:update(1 / 60, {}) end                     -- settle: she finds her floor
  end
  -- runs a plan(p, t) -> force table, press jump? until she lands after being in the air (or maxT). Returns the
  -- outcome: { y, x, landed, water, hearts, air }
  local function run(st, plan, maxT)
    local p, air, t = st.pepper, false, 0
    for _ = 1, math.floor((maxT or 4) * 60) do
      local force, press = plan(p, t, air)
      I.force = force or {}
      st:update(1 / 60, press and { jump = true } or {})
      t = t + 1 / 60
      if not p.onGround then air = true end
      if p.mode == "drown" or st.drownT or st.fallT or p.mode == "gone" then
        I.force = {}; return { x = p.x, y = p.y, water = true, hearts = st.hearts, air = air } end
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
    end, 4)
  end

  local steps
  if mode == "--physics" then
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      -- 0 the world and the camera
      { act = function(p, s)
          report("a tall map: 2880 x 384 px (360 x 48 cells)", s.world.width == 2880 and s.world.height == 384, ("%d x %d"):format(s.world.width, s.world.height))
          report("on the path (y 328) the camera rests at the bottom of the world", near(p.y, PATH) and s.camY == s.camYMax and s.camYMax == 144,
            ("feet %.0f, camY %.0f of %d: the path is at screen y %.0f, as in City Park"):format(p.y, s.camY, s.camYMax, p.y - s.camY))
          local okZ = #s.def.bikes == 2
          for _, z in ipairs(s.def.bikes) do okZ = okZ and z.roadY == PATH and z.kind == "cart" end
          report("the leaf carts are back: 2 cart zones on the low road (roadY 328)", okZ, ("%d cart zones"):format(#s.def.bikes))
        end },
      -- 0b the carts on the low road: one sets off as she walks in, drives on the path (y 328) and hurts her there;
      -- the picnic table is above it; on the treetops over the cart run no cart comes at all
      { act = function()
          local st = simStage(); local z = st.def.bikes[1]
          local function fresh(x, y) place(st, x, y); st.bikes, st.bikeT, st.zoneIn = {}, 2.5, {} end
          fresh(z.zoneX0 - 30, PATH)
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
          local okY = #ys > 0; for _, y in ipairs(ys) do if not near(y, PATH, 0.01) then okY = false end end
          report("a cart sets off as she walks into its zone on the path, with its warning", sent ~= nil and sent > z.zoneX0 and sent < z.zoneX0 + 20 and warned,
            ("at x %s"):format(tostring(sent and math.floor(sent))))
          report("it drives on the path (y 328), not on the treetops", okY, ("%d frames, y %s"):format(#ys, tostring(ys[1])))
          report("standing on the path, the cart hurts her", hurt)
          local tab
          for _, pr in ipairs(st.def.props) do if pr.name == "PICNIC TABLE" and pr.x0 > z.zoneX0 and pr.x1 < z.zoneX1 then tab = pr end end
          fresh((tab.x0 + tab.x1) / 2, tab.y0); st.zoneIn[z] = true; st.bikeT = 0
          local passed = false
          for f = 1, 60 * 6 do st:update(1 / 60, {}); if st.bikes[1] and st.bikes[1].x < tab.x0 - 30 then passed = true end end
          report("on the picnic table (y 300) the cart passes under her", passed and st.hearts == 3 and near(st.pepper.y, tab.y0), ("hearts %d"):format(st.hearts))
          local hi                                                    -- a treetop over the cart run, more than 90 px up
          for _, pr in ipairs(st.def.props) do
            if pr.kind ~= "decor" and pr.y0 < PATH - 90 and pr.x0 >= z.zoneX0 and pr.x1 <= z.zoneX1 and pr.x1 - pr.x0 >= 30 then hi = hi or pr end
          end
          fresh((hi.x0 + hi.x1) / 2, hi.y0); local any = false
          for f = 1, 60 * 8 do st:update(1 / 60, {}); if #st.bikes > 0 then any = true end end
          report("on a treetop over the cart run no cart comes", not any and near(st.pepper.y, hi.y0), ("y %.0f"):format(st.pepper.y))
        end },
      { act = function() tp(864, 216) end }, { wait = 1.2 },
      { act = function(p, s) report("on the treetop walk (y 216) the camera follows her up", near(s.camY, 216 - Vc.FLOOR, 1),
          ("camY %.1f, her feet at screen y %.0f"):format(s.camY, p.y - s.camY)) end },
      -- 1 Pepper's numbers, measured in the simulation
      { act = function()
          local st = simStage(); place(st, 300, PATH); local minY = PATH
          run(st, function(p, t) minY = math.min(minY, p.y); return { jump = true }, t == 0 end, 2)
          report("her held jump: 46 px", near(PATH - minY, 46, 1), ("%.1f px"):format(PATH - minY))
          place(st, 300, PATH); minY = PATH
          run(st, function(p, t) minY = math.min(minY, p.y); return t == 0 and { jump = true } or {}, t == 0 end, 2)
          report("her tapped hop: 24 px", near(PATH - minY, 24, 2), ("%.1f px"):format(PATH - minY))
        end },
      -- 2 every jump, simulated
      { act = function()
          local J = {
            -- the low road (the same as City Park, 144 px lower), and its new climb: the play tower and the big oak
            { "low: hop onto the log (running, tapped)", x = 120, y = PATH, dir = "right", run = 150, tap = true, brake = 196, to = 312 },
            { "low: held jump onto the stump, the practice ledge (running)", x = 180, y = PATH, dir = "right", run = 214, to = 300 },
            { "low: held jump onto the bench seat (between the stump and the bench)", x = 330, y = PATH, dir = "right", to = 300 },
            { "low: a held jump from the frame's step onto the top bar", x = 2724, y = 316, dir = "right", to = 280 },
            { "low: a running held jump onto the frame's low bar", x = 2694, y = PATH, dir = "right", run = 2697, to = 304 },
            { "low: stone to stone over the pond (running hop)", x = 744, y = 332, dir = "right", run = 758, tap = true, brake = 786, to = 332 },
            { "low: jump and scramble onto the bin (56 px)", x = 1300, y = PATH, dir = "right", to = 272 },
            { "low: creek, stone to stone (stop, then a held jump)", x = 2068, y = 332, dir = "right", brake = 2138, to = 332 },
            { "low: the oak's branches, 1 (28 px up)", x = 1766, y = PATH, to = 300 },
            { "low: the oak's branches, 2", x = 1772, y = 300, to = 272 },
            { "low: the oak's branches, 3 (the OAK TOP gold bone)", x = 1772, y = 272, to = 244 },
            { "low: onto the slide tower (running, 32 px)", x = 2560, y = PATH, dir = "right", run = 2588, to = 296 },
            { "finale: tower top -> second deck (40 px)", x = 2640, y = 296, to = 256 },
            { "finale: second deck -> top deck (40 px)", x = 2640, y = 256, to = 216 },
            { "finale: top deck -> the big oak's first bough", x = 2658, y = 216, dir = "right", to = 184 },
            { "finale: bough 1 -> bough 2 (32 up)", x = 2730, y = 184, dir = "right", to = 152 },
            { "finale: bough 2 -> bough 3 (32 up, back left)", x = 2790, y = 152, dir = "left", to = 120 },
            { "finale: bough 3 -> the nest bough (32 up)", x = 2738, y = 120, dir = "right", to = 88 },
            -- ways up from the low road to the high road
            { "way up 1: bench seat -> hedge top (running)", x = 420, y = 300, dir = "right", run = 439, to = 256 },
            { "way up 1: hedge top -> plane tree (40 up)", x = 578, y = 256, dir = "right", to = 216 },
            { "way up 2: bin top -> lime over it (40 up)", x = 1345, y = 272, to = 232 },
            { "way up 3: the oak's top branch -> the stub (20 up)", x = 1778, y = 244, dir = "right", to = 224 },
            { "way up 3: stub -> the old oak's crown (32 up, left)", x = 1846, y = 224, dir = "left", to = 192 },
            { "way up 3: stub -> the ash (24 up)", x = 1866, y = 224, dir = "right", to = 200 },
            -- the high road, west to east: standing held jumps from the edge
            { "high: treetop walk -> lime 1 (gap 32, 16 up)", x = 930, y = 216, dir = "right", to = 200 },
            { "high: lime 1 -> lime 2 (gap 48, 16 up)", x = 1026, y = 200, dir = "right", to = 184 },
            { "high: lime 2 -> lime 3 (gap 48, 16 down)", x = 1130, y = 184, dir = "right", to = 200 },
            { "high: lime 3 -> lime 4 (gap 48, 32 down)", x = 1234, y = 200, dir = "right", to = 232 },
            { "high: lime 4 -> lime 5 (gap 48, 16 up)", x = 1338, y = 232, dir = "right", to = 216 },
            { "high: lime 5 -> lime 6 (gap 48, 16 up)", x = 1442, y = 216, dir = "right", to = 200 },
            { "high: lime 6 -> lime 7 (gap 40, 40 wide)", x = 1546, y = 200, dir = "right", to = 200 },
            { "high: lime 7 -> the old oak's crown (gap 16, 8 up)", x = 1626, y = 200, dir = "right", to = 192 },
            { "high: crown -> the top twig: THE GOLDEN BONE (40 up)", x = 1772, y = 192, to = 152 },
            { "high: crown -> the ash (gap 56, 8 down)", x = 1818, y = 192, dir = "right", to = 200 },
            { "high: alder walk: hop over the low bough (34 up)", x = 2190, y = 200, dir = "right", brake = 2226, to = 166 },
            { "high: alder walk -> arbour 1 (gap 32, 16 down)", x = 2298, y = 200, dir = "right", to = 216 },
            { "high: arbour 1 -> arbour 2 (gap 48, 16 up)", x = 2386, y = 216, dir = "right", to = 200 },
            { "high: arbour 2 -> arbour 3 (gap 48, 16 down)", x = 2482, y = 200, dir = "right", to = 216 },
            { "high: arbour 3 -> the play tower's top deck (gap 24)", x = 2578, y = 216, dir = "right", to = 216 },
            -- running jumps of the high road (a child runs): they land on the next ledge, not past it
            { "high, running: treetop walk -> lime 1", x = 880, y = 216, dir = "right", run = 930, to = 200 },
            { "high, running: lime 1 -> lime 2", x = 990, y = 200, dir = "right", run = 1030, to = 184 },
            { "high, running: arbour 1 -> arbour 2", x = 2350, y = 216, dir = "right", run = 2390, to = 200 },
          }
          for _, j in ipairs(J) do
            local r = leap(j)
            report(j[1], r.landed and not r.water and near(r.y, j.to) and r.hearts == 3,
              ("lands x %.0f y %.1f (want %d)%s"):format(r.x, r.y, j.to, r.water and " IN THE WATER" or (r.stuck and " (never landed)" or "")))
          end
          -- the low road cannot get up there without a way up: the same jumps from the path fall short
          for _, j in ipairs({ { "the hedge top is out of reach from the path (72 px)", x = 500, y = PATH, dir = "right", run = 510, bad = 256 },
                               { "the plane tree is out of reach from the path (112 px)", x = 640, y = PATH, bad = 216 },
                               { "the nest bough is out of reach from bough 2 (64 px)", x = 2800, y = 152, bad = 88 } }) do
            local r = leap(j)
            report(j[1], not near(r.y, j.bad, 1) and r.y > j.bad, ("ends at y %.0f"):format(r.y))
          end
          -- the crawl under the low bough on the alder walk
          local st = simStage(); place(st, 2180, 200)
          local r = run(st, function(p, t) return t < 1.2 and { right = true } or {}, false end, 1.5)
          report("high: standing, the low bough stops her", st.pepper.x < 2200 and near(st.pepper.y, 200), ("x %.0f"):format(st.pepper.x))
          place(st, 2180, 200)
          run(st, function(p, t) return t < 2.5 and { right = true, down = true } or {}, false end, 2.6)
          report("high: crawling, she passes under the low bough (16 px)", st.pepper.x > 2262 and near(st.pepper.y, 200), ("x %.0f"):format(st.pepper.x))
        end },
      -- 3 every way off the high road lands on a floor below: no heart, never the water
      { act = function()
          local st = simStage()
          local ledges = {}
          for _, r in ipairs(st.world.rects) do
            if not r.terrain and (r.kind == "oneway" or r.kind == "solid") and r.y0 <= 256 and not r.mover and r.name ~= "LOW BOUGH" then ledges[#ledges + 1] = r end
          end
          table.sort(ledges, function(a, b) return a.x0 < b.x0 end)
          local bad, cases, worst = {}, 0, ""
          local function check(label, r, res, y0)
            cases = cases + 1
            if res.water or not res.landed or res.hearts ~= 3 or (res.y <= y0 and not res.jumped) then
              bad[#bad + 1] = ("%s x %d-%d y %d: %s at x %.0f y %.0f"):format(label, r.x0, r.x1, r.y0, res.water and "WATER/OUT" or (res.landed and "landed" or "stuck"), res.x, res.y)
            end
          end
          for _, r in ipairs(ledges) do
            local y = r.y0
            -- walk off each end
            for _, d in ipairs({ { "left", r.x0 + 14 }, { "right", r.x1 - 14 } }) do
              place(st, d[2], y)
              if near(st.pepper.y, y) then
                local res = run(st, function(p, t, air) if air then return {} end; return t < 3 and { [d[1]] = true, walk = true } or {}, false end, 6)
                if res.air then check("walk off " .. d[1], r, res, y) end      -- (no edge: the floor goes on)
                -- a running held jump off that end
                place(st, d[1] == "left" and r.x0 + 40 or r.x1 - 40, y)
                local pressed = false
                res = run(st, function(p, t, air)
                  local f = { [d[1]] = true }
                  if not pressed and ((d[1] == "left" and p.x <= r.x0 + 14) or (d[1] == "right" and p.x >= r.x1 - 14)) then pressed = true; f.jump = true; return f, true end
                  if pressed then f.jump = true end
                  return f, false end, 6)
                res.jumped = true                                              -- (onto the next high ledge: fine too)
                check("run-jump off " .. d[1], r, res, y)
              end
            end
            -- Down + A through a one-way ledge, in its middle
            if r.kind == "oneway" then
              place(st, (r.x0 + r.x1) / 2, y)
              local res = run(st, function(p, t) return t == 0 and { down = true } or {}, t == 0 end, 6)
              check("drop through", r, res, y)
            end
          end
          for i = 1, math.min(#bad, 12) do print("        " .. bad[i]) end
          report("every way off the high road lands on a floor below, no heart lost", #bad == 0, ("%d ledges, %d drops, %d bad"):format(#ledges, cases, #bad))
          -- the walks over the water are solid: Down + A does not drop her into the pond or the creek
          local ok = true
          for _, x in ipairs({ { 824, 216 }, { 2140, 200 } }) do
            place(st, x[1], x[2]); run(st, function(p, t) return t == 0 and { down = true } or {}, t == 0 end, 1)
            ok = ok and near(st.pepper.y, x[2]) and st.pepper.onGround
          end
          report("the treetop walk and the alder walk are solid: no drop into the water", ok)
        end },
      -- 4 the magpie: a bark from where a player stands; the ball falls onto a floor she can get to
      { act = function()
          local st = simStage(); local d = st.def.magpie
          local spots = {   -- perch -> where Pepper barks from, and the floor the ball must land on
            { 190, 312, 328 }, { 330, PATH, 300 }, { 600, PATH, PATH }, { 780, 216, 216 }, { 1200, PATH, 312 },
            { 1300, 232, 272 }, { 1560, PATH, PATH }, { 1752, 244, 192 }, { 2100, 200, 200 }, { 2350, PATH, 300 },
            { 2700, PATH, 280 }, { 2790, 152, 88 } }
          report("the magpie has 12 perches, the last one in the big oak", #d.perches == 12 and d.perches[12].y < 100, ("%d perches, the last at y %d"):format(#d.perches, d.perches[#d.perches].y))
          for i, sp in ipairs(spots) do
            place(st, sp[1], sp[2]); st:resetMagpie(i); st.pepper.face = st.pepper.x < st.magpie.x and 1 or -1
            st:updateMagpie(0)
            st:barkAtMagpie()
            for _ = 1, 150 do st:update(1 / 60, {}) end
            local b = st.ball
            report(("magpie perch %d (x %d y %d): bark from x %d y %d, the ball lands on y %d"):format(i, d.perches[i].x, d.perches[i].y, sp[1], sp[2], sp[3]),
              b.state == "rest" and near(b.y, sp[3]), ("ball %s at x %.0f y %.0f"):format(b.state, b.x, b.y))
          end
          -- the high perches only answer a bark from up high
          for _, c in ipairs({ { 4, 804, 332, "the treetop walk's rail (from a stone)" }, { 9, 2148, 332, "the alder walk (from a creek stone)" },
                               { 12, 2820, PATH, "the nest (from the ground under it)" } }) do
            place(st, c[2], c[3]); st:resetMagpie(c[1]); st:barkAtMagpie()
            report("perch " .. c[1] .. ", " .. c[4] .. ": too far below, it keeps the ball", st.ball.state == "magpie" and st.magpie.state == "perch")
          end
          -- the last perch: it stays even when Pepper runs right under it
          place(st, 2700, PATH); st:resetMagpie(12)
          run(st, function(p, t) return t < 1.2 and { right = true } or {}, false end, 1.3)
          report("its last perch, the nest: it stays put when she runs under it", st.magpie.i == 12 and st.magpie.state == "perch", ("x %.0f"):format(st.pepper.x))
        end },
      -- 5 bones
      { act = function()
          local st = simStage(); local w = st.world
          local inside, far = {}, {}
          for _, b in ipairs(st.def.bones) do
            if w:solidIn(b.x - 3, b.x + 3, b.y - 14, b.y - 4) then inside[#inside + 1] = ("%d,%d"):format(b.x, b.y) end
            local found = false                -- a floor under it, or beside it (a bone in the air over a gap: hop for it)
            for dx = -40, 40, 8 do for dy = 0, 46 do
              if not found and w:floor(b.x + dx - 12, b.x + dx + 12, b.x + dx, b.y + dy - 1, b.y + dy + 1, b.y + dy - 2) then found = true end
            end end
            for _, m in ipairs(st.def.movers) do          -- on a boat's deck, anywhere along its way
              if b.y == m.y0 and b.x >= m.from and b.x <= m.to + (m.x1 - m.x0) then found = true end
            end
            if not found then far[#far + 1] = ("%d,%d"):format(b.x, b.y) end
          end
          local supers, golden = 0, 0
          for _, b in ipairs(st.def.bones) do if b.super then supers = supers + 1 end; if b.golden then golden = golden + 1 end end
          report("no bone inside a solid", #inside == 0, ("%d bones; %s"):format(#st.def.bones, table.concat(inside, " ")))
          report("every bone is within a held jump of a floor (or a boat)", #far == 0, table.concat(far, " "))
          report("one golden bone (and the gold super bones)", golden == 1, ("%d golden, %d super"):format(golden, supers))
          report("4 secrets: hollow log, oak top, treetop walk, golden bone", #st.def.secrets == 4, ("%d"):format(#st.def.secrets))
        end },
      -- 6 the fetch: the ball on the nest bough; pick it up, drop down to Mia, give it: GOOD GIRL, the level ends
      { act = function(p, s) s.magpie.state = "gone"; s.magpie.x = -999
          s.ball.state, s.ball.x, s.ball.y = "rest", 2836, 88; tp(2818, 88); p.face = 1 end },
      { wait = 0.3 }, { act = function() love.keypressed("x") end }, { wait = 0.5 },
      { act = function(p) report("on the nest bough Pepper picks the ball up", p.carrying ~= nil); hold("right", "walk") end },
      { cond = function(p) return p.x >= 2856 end, act = function() hold("down"); love.keypressed("space") end, limit = 3 },
      { wait = 0.1 }, { act = function() release() end },
      { cond = function(p) return p.onGround and p.y > 300 end, act = function() end, limit = 3 },
      { act = function(p, s) report("Down + A off the nest bough: she drops to Mia, still carrying", near(p.y, PATH) and p.carrying ~= nil and s.hearts == 3,
          ("x %.0f y %.0f"):format(p.x, p.y)); p.face = -1; love.keypressed("x") end },
      { wait = 0.4 },
      { act = function(p, s) report("giving the ball to Mia: GOOD GIRL (FETCH 2000)", s.ball.state == "given" and s.bonus and s.bonus[2] == 2000, s.ball.state) end },
      { wait = 2.6 },
      { act = function(p, s) report("the fetch ends the level", s.events.clear == true or api.getState() ~= "play", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec_citypark_tall")
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
    local function leap(dir, toY)                   -- a held jump (dir or straight up) until she lands at toY
      return { act = function() if dir then jump(dir, "jump") else jump("jump") end end },
        at(function(p) return p.onGround and p.vy == 0 and near(p.y, toY, 0.5) end, function() release() end, 3)
    end
    local function add(list) for _, st in ipairs(list) do steps[#steps + 1] = st end end
    local function hop(x, dir, toY) local a, b = runTo(x); local c, d = goTo(x), nil; local e, f = leap(dir, toY); add({ a, b, c, e, f }) end
    steps = { { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.4 } }
    add({
      -- 1 the gate: run (the magpie flies on), over the log
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.x >= 150 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and p.y > 320 end, function() hold("right") end),
      -- 2 the stump (r6/levels: the practice ledge), across to the bench seat, a running jump to the hedge top
      at(function(p) return p.x >= 214 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and near(p.y, 300, 0.5) end, function() hold("right") end),
      at(function(p) return p.x >= 296 and p.onGround and p.y > 327 end, function() jump("right", "jump") end, 4),   -- off it, onto the seat
      at(function(p) return p.onGround and near(p.y, 300, 0.5) and p.x > 352 end, function() hold("right") end),
      at(function(p) return p.x >= 439 end, function() jump("right", "jump") end),
      at(function(p) return p.onGround and near(p.y, 256, 0.5) end, function() release() end),
    })
    hop(578, "right", 216)                                          -- up into the plane tree
    hop(930, "right", 200)                                          -- the treetop walk, then the limes
    hop(1026, "right", 184); hop(1130, "right", 200); hop(1234, "right", 232); hop(1338, "right", 216)
    hop(1442, "right", 200); hop(1546, "right", 200); hop(1626, "right", 192)
    hop(1772, nil, 152)                                             -- the golden bone on the top twig
    add({ { act = function() hold("down"); love.keypressed("space") end }, { wait = 0.05 }, { act = function() release() end },
      at(function(p) return p.onGround and near(p.y, 192, 0.5) end) })
    hop(1818, "right", 200)                                         -- the ash, then the alder walk over the creek
    add({ at(function() return true end, function() hold("right") end),
      at(function(p) return p.x >= 2186 end, function() hold("right", "down") end, 9),       -- crawl under the low bough
      at(function(p) return p.x >= 2266 end, function() release() end, 9) })
    hop(2298, "right", 216); hop(2386, "right", 200); hop(2482, "right", 216); hop(2578, "right", 216)
    hop(2658, "right", 184); hop(2730, "right", 152)                -- up the big oak
    add({ goTo(2792), { wait = 0.2 }, { act = function(p) p.face = 1; love.keypressed("z") end }, { wait = 1.2 } })   -- bark: it drops the ball
    hop(2790, "left", 120); hop(2738, "right", 88)
    add({
      at(function(p, s)                                                                        -- walk up to the ball
        local b = s.ball
        local want = p.x < b.x and 1 or -1
        if p.face == want and math.abs(p.x + p.face * 18 - b.x) < 20 and math.abs(p.vx) < 1 then release(); return true end
        local tx = b.x - want * 18
        if p.face ~= want then hold(want > 0 and "right" or "left", "walk")
        elseif p.x < tx - 3 then hold("right", "walk") elseif p.x > tx + 3 then hold("left", "walk") else release() end
        return false end, nil, 6),
      { wait = 0.2 }, { act = function() love.keypressed("x") end }, { wait = 0.5 },
      at(function() return true end, function() hold("right") end),
      at(function(p) return p.x >= 2856 end, function() release(); hold("down"); love.keypressed("space") end, 4),
      { wait = 0.1 }, { act = function() release() end },
      at(function(p) return p.onGround and p.y > 320 end, function(p) p.face = -1; love.keypressed("x") end, 4),
      { wait = 6 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played"):format(api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets or 0, st.secretsTotal or 0, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    })
  else  -- --test: a screenshot tour
    local function shot(name) return { act = function() love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("ct_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    local spots = { { 60, PATH }, { 578, 256 }, { 824, 216 }, { 1116, 184 }, { 1772, 152 }, { 2140, 200 }, { 2640, 216 }, { 2800, 152 }, { 2800, 88 }, { 2780, PATH } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.8 }
      steps[#steps + 1] = shot(("ct_%02d_spot"):format(i))
    end
    for _, st in ipairs({ { act = function() tp(1000, PATH) end }, { wait = 0.5 }, { act = function() hold("up") end }, { wait = 1.6 },
      shot("ct_20_lookup_from_the_lawn"), { act = function() release() end },
      -- the leaf carts on the low road (engine/round2): walk into the first cart run and up onto the picnic table
      { act = function() local s = api.stage(); s.hearts = 3; s.bikes, s.zoneIn, s.bikeT = {}, {}, 2.5; tp(1350, PATH); hold("right") end },
      { wait = 0.45 }, shot("ct_21_cart_warning"), { wait = 0.75 }, shot("ct_22_cart_coming"),
      { act = function() release(); tp(1452, 300) end }, { wait = 0.9 }, shot("ct_23_cart_under_the_table"),
      { act = function() release() end } }) do steps[#steps + 1] = st end
    -- every screen (r3/citypark-art): the low road (ct_3x), then the treetops over it (ct_4x, on a ledge of each
    -- screen; the gate screen has none, so the hedge top), for the art's contact sheet
    for i = 0, 8 do
      steps[#steps + 1] = { act = function() local s = api.stage(); s.hearts = 3; s.bikes, s.zoneIn, s.bikeT = {}, {}, 99; tp(160 + 320 * i, PATH) end }
      steps[#steps + 1] = { wait = 0.8 }
      steps[#steps + 1] = shot(("ct_3%d_low_screen%d"):format(i + 1, i + 1))
    end
    local high = { { 560, 256 }, { 650, 216 }, { 824, 216 }, { 1116, 184 }, { 1424, 216 }, { 1772, 192 }, { 2140, 200 }, { 2470, 200 }, { 2720, 120 } }
    for i, sp in ipairs(high) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.8 }
      steps[#steps + 1] = shot(("ct_4%d_high_screen%d"):format(i, i))
    end
    steps[#steps + 1] = { act = function() love.event.quit() end }
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
      if frame % 3 == 0 and not os.getenv("NO_REC") then n = n + 1; love.graphics.captureScreenshot(("rec_citypark_tall/%04d.png"):format(n)) end
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
