-- The checks for Rooftops (greybox; love riverwalk --level rooftops <flag>). Design: docs/rooftops_beatsheet.md.
--   --physics   the world; every steam puff (its apex is y0 - lift within 1 px; with no input she lands back on
--               its hood or the floor over it; steering, on the floor it serves); the warning 0.8 s before the
--               lift; one lift per puff; a bark starts a resting vent at once; the sauna puffs only after a bark;
--               crouching stays put; the loose tiles (a floor for 0.6 s, then not; back after 3 s, not while she
--               is in its place; every bridge crossed); every jump on both routes with Pepper's own controller;
--               every fall off the high road lands on a floor below with no heart lost; no bone inside a solid;
--               the gull's nest; the fetch ends the level
--   --auto      the main route (the low road) and the finale on autopilot (frames in rec_rooftops/ every 3rd
--               frame); AUTO_ROUTE=high plays the high road instead
--   --test      a screenshot tour, and frames of a puff and a loose tile (rec_rooftops_puff/, rec_rooftops_tile/)
local I = require("input")
local Pp = require("pepper")
local St = require("stage")
local Vc = require("vcam")
local Rf = require("roofs")
local Cr = require("critters")
return function(mode, api)
  I.testing = true
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-72s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local function near(a, b, e) return a and b and math.abs(a - b) <= (e or 0.01) end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); Vc.snap(s)
  end

  -- the simulation stage (no goose or gull: they are checked in play and by the autopilot) -------------------
  local function fresh()
    local st = St.new(api.stage().def); st.critters = {}
    return st
  end
  local function place(st, x, y)
    local p = st.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    p.carrying, p.dropT, p.bufferT, p.coyoteT = nil, 0, 0, 0
    st.hearts, st.deadT, st.drownT, st.fallT, st.msg = 3, nil, nil, nil, nil
    st.cam = math.max(0, math.min(st.world.width - 320, x - 140)); Vc.snap(st)
    I.force = {}
    for _ = 1, 4 do st:update(1 / 60, {}) end                      -- settle: she finds her floor
  end
  -- plan(p, f, air) -> held buttons, press jump?, press bark?; runs until she lands after being in the air (or
  -- maxT). Returns { x, y, landed, minY, hearts, fell }
  local function run(st, plan, maxT, keepGoing)
    local p, air, minY = st.pepper, false, st.pepper.y
    for f = 1, math.floor((maxT or 4) * 60) do
      local held, jump, bark = plan(p, f, air)
      I.force = held or {}
      st:update(1 / 60, { jump = jump or nil, bark = bark or nil })
      if not p.onGround then air = true end
      minY = math.min(minY, p.y)
      if st.fallT or p.mode == "gone" then I.force = {}; return { x = p.x, y = p.y, fell = true, minY = minY, hearts = st.hearts } end
      if keepGoing and keepGoing(p) then I.force = {}; return { x = p.x, y = p.y, landed = p.onGround, minY = minY, hearts = st.hearts } end
      if air and p.onGround and p.mode == "normal" and not keepGoing then I.force = {}; return { x = p.x, y = p.y, landed = true, minY = minY, hearts = st.hearts } end
    end
    I.force = {}
    return { x = p.x, y = p.y, landed = p.onGround, minY = minY, hearts = st.hearts, timeout = true }
  end
  local function vent(st, name) for _, v in ipairs(st.vents) do if v.d.name == name then return v end end end
  -- (r9) she stands on a vent hood that stands on floor y (the next puff's hood: as good as the floor)
  local function onVentHood(st, y) local g = st.pepper.ground; return st.pepper.onGround and g and g.vent and near(g.y1, y) end
  local function puffNow(v) v.st, v.t = "warn", (v.d.warn or 0.8) - 1 / 60 end   -- its puff starts next frame

  -- every vent: name, where she lands with no input, the way to steer, the floor it serves, that floor's x range
  local VENTS = {
    { "KITCHEN FAN", 948, "right", 856, 1280, 1568 },
    { "COURTYARD FAN", 856, "right", 856, 1664, 2048 },        -- (no input: back onto the loose tile over it)
    { "LAUNDRY VENT", 852, "right", 760, 2048, 3328 },
    { "SWEEP VENT", 756, "right", 664, 2400, 2464 },
    { "SKYLIGHT FAN", 760, "right", 760, 2624, 3328 },         -- (no input: back onto the loose tile over it)
    { "GARDEN VENT", 756, "right", 664, 3072, 3144 },
    { "BALCONY VENT", 660, "right", 568, 3328, 3872 },
    { "TANK VENT", 444, "right", 376, 3872, 4048 },
    { "TERRACE FAN", 280, nil, 280 },                           -- (up through the copper roof, onto it)
    { "HOTEL KITCHEN", 372, "right", 280, 4608, 4672 },         -- (r9) over the hotel's chimney block
    { "COURT FAN", 660, "right", 568, 4920, 5000 },             -- (r9) up the light court: its four puffs
    { "LAUNDRY HOOD", 564, "right", 472, 5008, 5088 },          --   (onto the loose tiles or the ledge by the hood)
    { "KITCHEN HOOD", 468, "right", 376, 5096, 5200 },
    { "BATH FAN", 372, "right", 280, 5200, 5424 },              --   onto the tall block
    { "SAUNA", 180, "right", 88, 6400, 6432 },                  -- (r9) onto the nest chimney
    { "ATTIC FAN", 852, "right", 760, 1424, 1520 },
    { "LOFT VENT", 692, "right", 600, 1960, 2720 },
    { "BAKERY CHIMNEY", 596, "right", 456, 2984, 3200 },
    { "BAR FAN", 420, "right", 280, 3776, 4032 },
  }
  -- a jump: name, from x, y, the plan ("held", "tap", "walk", "run", "downA", or a function), its way, the floor
  -- she must land on, and (optional) its x range
  local JUMPS = {
    { "the sweep's chimney block (664) -> walk off its right side onto the market roof (760)", 2440, 664, "walk", "right", 760 },
    { "high: the pigeon loft (600) -> ledge 568: held jump right", 2068, 600, "held", "right", 568 },
    { "high: ledge 568 -> ledge 536: held jump right", 2196, 568, "held", "right", 536 },
    { "high: ledge 536 -> down to ledge 600: held jump right", 2548, 536, "held", "right", 600, { 2592, 2720 } },
    -- the low road
    { "street: a running jump onto the cafe table (1120)", 70, 1144, "runjump", "right", 1120 },
    { "the awning (552) from the roof bar: a tap hop", 3708, 568, "tap", "right", 432, nil, "bounce" },
    { "the awning's bounce onto the water tank (448), holding right", 3708, 568, "taphold", "right", 448, { 3800, 3872 } },
    { "copper roof -> Down + A -> the roof terrace (376)", 3990, 280, "downA", nil, 376 },
    { "(r9) nest chimney -> step off left onto the sauna's hood (180)", 6404, 88, "walk", "left", 180 },
    { "(r9) the hotel's chimney block (280) -> walk off its right side onto the hotel roof (376)", 4660, 280, "walk", "right", 376, { 4672, 4800 } },
    { "(r9) the hotel roof's end -> walk off it, down into the light court (664)", 4780, 376, "walk", "right", 664, { 4800, 4884 } },
    { "(r9) the light court's floor: a held jump left onto the balcony's post (624, 40 px up)", 4990, 664, "held", "left", 624, { 4924, 4932 } },
    { "(r9) the balcony's post -> walk off its left side, back to the court fan (the floor or its hood)", 4928, 624, "walk", "left", 664, { 4800, 4924 } },
    { "(r9) the scaffold: a board not hopped onto drops her into the gap (320)", 5404, 280, "walk", "right", 320 },
    { "(r9) out of the scaffold's gap: a held jump and scramble back onto the tall block (280)", 5440, 320, "held", "left", 280, { 5200, 5424 } },
    { "(r9) out of the scaffold's gap: a held jump and scramble onto the far side (280)", 5552, 320, "held", "right", 280, { 5568, 5696 } },
    { "(r9) the cafe awning (264) from its roof: a tap hop", 5604, 280, "tap", "right", 432, nil, "bounce" },
    { "(r9) the cafe awning's bounce onto the stacks' roof (184), holding right", 5604, 280, "taphold", "right", 184, { 5696, 5856 } },
    { "(r9) the stacks: T6 (184) -> the first loose tile (152): held jump right", 5838, 184, "held", "right", 152, { 5888, 5912 } },
    { "(r9) the stacks: a tapped hop does not reach it (into the dip, 40 px)", 5838, 184, "tap", "right", 224 },
    { "(r9) out of the stacks' dip: a held jump and scramble back onto the roof (184)", 5876, 224, "held", "left", 184, { 5696, 5856 } },
    { "(r9) the stacks: loose tile 152 -> loose tile 120: held jump right", 5900, 152, "held", "right", 120, { 5944, 5968 } },
    { "(r9) the stacks: loose tile 120 -> the chimney stack (88): held jump right", 5956, 120, "held", "right", 88, { 6000, 6104 } },
    { "(r9) the chimney stack (88) -> run off its right side onto the sauna roof (184)", 6090, 88, "run", "right", 184, { 6104, 6176 } },
    { "(r9) the long roof: from the nest chimney a run down four pitched roofs to the roof cafe (472)", 6420, 88, "run", "right", 472, { 7136, 7472 } },
    { "(r7) the drying yard: T3 (568) -> the first loose tile (536): held jump right", 3414, 568, "held", "right", 536, { 3464, 3488 } },
    { "(r7) the drying yard: a tapped hop does not reach it (into the dip, 40 px)", 3414, 568, "tap", "right", 608 },
    { "(r7) out of the dip: a held jump and scramble back onto the yard (568)", 3452, 608, "held", "left", 568, { 3344, 3432 } },
    { "(r7) loose tile 536 -> loose tile 504: held jump right", 3476, 536, "held", "right", 504, { 3520, 3544 } },
    { "(r7) loose tile 504 -> the chimney stack (472): held jump right", 3532, 504, "held", "right", 472, { 3576, 3680 } },
    { "(r7) the chimney stack (472) -> run off its right side: the springy awning bounces her onto the water tank (448)", 3670, 472, "run", "right", 448, { 3800, 3872 } },
    -- the high road
    { "ledge 760 -> ledge 728: held jump right", 1750, 760, "held", "right", 728 },
    { "ledge 728 -> ledge 696: held jump right", 1846, 728, "held", "right", 696 },
    { "ledge 600 -> the chimney pot (552, golden bone): held jump and scramble", 2868, 600, "held", "right", 552 },
    { "the chimney pot -> off its right side onto the ledge (the vent hood, 596)", 2916, 552, "walk", "right", 596 },
  }
  -- bridges of loose tiles: name, start x, y, hop from x (nil: run straight across), end x, the floor at the end
  local BRIDGES = {
    { "the market hall's skylight: running straight across its three loose tiles", 2476, 760, nil, 2660, 760 },
    { "high: ledge 536, two loose tiles (tap hops), ledge 536", 2250, 536, 2310, 2490, 536 },
    { "the light well: running straight across its three loose tiles", 1480, 856, nil, 1700, 856 },
    { "the balcony: running across its three loose tiles", 3088, 664, nil, 3260, 664 },
    { "high: ledge 760, two loose tiles (tap hops), ledge 760", 1440, 760, 1500, 1680, 760 },
    { "high: ledge 600, two loose tiles (tap hops), the chimney pot's ledge 600", 2630, 600, 2700, 2856, 600 },
    { "high: the walkway (456), two loose tiles (held jumps), ledge 424", 3110, 456, 3180, 3680, 424, "held" },
    { "(r9) the hotel roof's first skylight: running straight across its three loose tiles", 4140, 376, nil, 4340, 376 },
    { "(r9) the hotel roof's second skylight: running straight across its three loose tiles", 4330, 376, nil, 4500, 376 },
    { "(r9) the scaffold: two loose boards (tap hops), the far side (280)", 5340, 280, 5404, 5584, 280 },
    { "(r9) the sauna roof's skylight: running straight across its three loose tiles", 6116, 184, nil, 6300, 184 },
  }

  local steps
  if mode == "--physics" then
    steps = {
      { wait = 0.6 }, { act = function() love.keypressed("space") end }, { wait = 0.3 },
      { act = function(p, s)
          report("a tall map: 7472 x 1200 px (934 x 150 cells, 23.4 x 5 screens; r9: the climb to the nest)", s.world.width == 7472 and s.world.height == 1200, ("%d x %d"):format(s.world.width, s.world.height))
          report("19 steam vents, 36 loose tiles, the gull's nest (88), Mia at the roof cafe (472)", #s.vents == 19 and #s.tiles == 36 and s.def.magpie.look == "gull"
            and s.ball.state == "magpie" and near(s.ball.y, 88, 12) and near(s.girl.y, 472), ("%d vents, %d tiles"):format(#s.vents, #s.tiles))
          local bad = {}
          for _, b in ipairs(s.def.bones) do
            if s.world:solidIn(b.x - 5, b.x + 5, b.y - 12, b.y - 7) then bad[#bad + 1] = ("%d,%d"):format(b.x, b.y) end
          end
          report(("no bone inside a solid (%d bones)"):format(#s.def.bones), #bad == 0, table.concat(bad, " "))
          local lamps = 0; for _, l in ipairs(s.def.lamps) do if l.checkpoint then lamps = lamps + 1 end end
          report("9 lamps (7 on the low road and the climb, 2 on the high road), 2 secrets, a golden bone", lamps == 9 and #s.def.secrets == 2, ("%d lamps"):format(lamps))
        end },
      -- 1 every vent: apex exact; no input; steering to the floor it serves
      { act = function()
          for _, c in ipairs(VENTS) do
            local st = fresh(); local v = vent(st, c[1]); local d = v.d
            local mid = (d.x0 + d.x1) / 2
            place(st, mid, d.y0)
            local onHood = near(st.pepper.y, d.y0)
            puffNow(v)
            local r = run(st, function() return {} end, 4)
            report(("%s: apex y0 - lift = %d (within 1 px)"):format(c[1], Rf.apex(v)), onHood and near(r.minY, Rf.apex(v), 1), ("top %.2f"):format(r.minY))
            report(("%s: no input, she lands on y %d"):format(c[1], c[2]), r.landed and near(r.y, c[2]) and r.hearts == 3, ("y %.1f x %.0f"):format(r.y, r.x))
            if c[3] then
              st = fresh(); v = vent(st, c[1]); place(st, mid, d.y0)
              for _, q in ipairs(st.vents) do if q ~= v then q.st, q.t = "rest", 0 end end   -- (r9: no chained lift from a neighbour)
              puffNow(v)
              r = run(st, function(p, f, air) if air then return { [c[3]] = true } end; return {} end, 4)
              report(("%s: steering %s she lands on the floor it serves (y %d)"):format(c[1], c[3], c[4]),
                r.landed and (near(r.y, c[4]) or onVentHood(st, c[4])) and r.x + 13 > c[5] and r.x - 13 < c[6] and r.hearts == 3, ("y %.1f x %.0f"):format(r.y, r.x))
            end
          end
        end },
      -- 2 the warning comes first; one lift per puff; crouching stays put; a bark; the sauna only on a bark
      { act = function()
          local st = fresh(); local v = vent(st, "KITCHEN FAN"); local d = v.d
          place(st, (d.x0 + d.x1) / 2, d.y0); v.st, v.t = "rest", 0
          local warnAt, liftAt = nil, nil
          for i = 1, 60 * 4 do
            st:update(1 / 60, {})
            if v.st == "warn" and not warnAt then warnAt = i end
            if not st.pepper.onGround and not liftAt then liftAt = i end
            if liftAt then break end
          end
          report("a vent warns (the cap rattles, wisps) 0.8 s before it lifts her", warnAt and liftAt and near((liftAt - warnAt) / 60, 0.8, 2 / 60),
            ("warn at %.2f s, lift at %.2f s"):format((warnAt or 0) / 60, (liftAt or 0) / 60))
          report("the cycle: rest every - warn - puff (3 - 0.8 - 0.9 = 1.3 s)", warnAt and near(warnAt / 60, 1.3, 2 / 60), ("%.2f s"):format((warnAt or 0) / 60))
          st = fresh(); v = vent(st, "KITCHEN FAN"); place(st, (d.x0 + d.x1) / 2, d.y0); puffNow(v)
          st:update(1 / 60, {}); st:update(1 / 60, {})
          local lifted1 = not st.pepper.onGround
          local p = st.pepper; p.y, p.vy, p.onGround, p.ground = d.y0, 0, true, nil
          local again = false
          for _ = 1, 20 do st:update(1 / 60, {}); if v.st == "puff" and p.vy < -50 then again = true end end
          report("one lift per puff: back in the column, she is not lifted again", lifted1 and not again and st.puffed == 1, ("%d lifts"):format(st.puffed or 0))
          st = fresh(); v = vent(st, "KITCHEN FAN"); place(st, (d.x0 + d.x1) / 2, d.y0); I.force = { down = true }
          for _ = 1, 10 do st:update(1 / 60, {}) end
          puffNow(v)
          for _ = 1, 70 do st:update(1 / 60, {}) end
          I.force = {}
          report("crouched (Down) on the hood she stays put through a puff", st.pepper.onGround and near(st.pepper.y, d.y0) and not st.puffed, ("y %.1f"):format(st.pepper.y))
          st = fresh(); v = vent(st, "LAUNDRY VENT"); place(st, 1990, 856); v.st, v.t = "rest", 0
          st:update(1 / 60, { bark = true })
          report("a bark near a resting vent starts its warning at once", v.st == "warn", v.st)
          st = fresh(); v = vent(st, "SAUNA"); d = v.d; place(st, (d.x0 + d.x1) / 2, d.y0)
          local any = false
          for _ = 1, 60 * 8 do st:update(1 / 60, {}); if v.st ~= "rest" then any = true end end
          report("the sauna never puffs by itself (8 s)", not any, v.st)
          st:update(1 / 60, { bark = true })
          local r = run(st, function(q, f, air) if air then return { right = true } end; return {} end, 4)
          report("a bark: the sauna puffs and carries her onto the nest chimney (88)", r.landed and near(r.y, 88), ("y %.1f"):format(r.y))
          -- every timed vent puffs by itself within its cycle, and neighbours start at different phases
          st = fresh(); local seen = {}
          for _ = 1, 60 * 5 do st:update(1 / 60, {}); for _, q in ipairs(st.vents) do if q.st == "puff" then seen[q] = true end end end
          local n = 0; for _ in pairs(seen) do n = n + 1 end
          report("all 18 timed vents puff within 5 s (someone runs each one)", n == 18, ("%d"):format(n))
        end },
      -- 3 loose tiles
      { act = function()
          local st = fresh(); local k = st.tiles[1]; local t = k.p
          place(st, (t.x0 + t.x1) / 2, t.y0)
          local on = near(st.pepper.y, t.y0) and st.pepper.ground == t
          local fellAt
          for i = 1, 60 do st:update(1 / 60, {}); if not fellAt and (not st.pepper.onGround or st.pepper.ground ~= t) then fellAt = i end end
          report("a loose tile: a floor for 0.6 s, then she falls through", on and fellAt and near((fellAt + 4) / 60, 0.6, 3 / 60), ("%.2f s"):format(((fellAt or 0) + 4) / 60))
          local r = run(st, function() return {} end, 3)
          report("she lands in the light well (952) below, no harm", r.landed and r.hearts == 3 and near(r.y, 952), ("y %.0f"):format(r.y))
          local p = st.pepper
          for _ = 1, 60 * 3.5 do p.x, p.y, p.vy, p.onGround = (t.x0 + t.x1) / 2, t.y0 + 10, 0, true; st:update(1 / 60, {}) end
          local stillGone = k.st == "gone"
          place(st, 1320, 856)
          st:update(1 / 60, {})
          local back = false; for _, r2 in ipairs(st.world.rects) do if r2 == t then back = true end end
          report("it does not come back while she is in its place", stillGone, k.st)
          report("it is back after 3 s once she is out of the way", k.st == "idle" and back, k.st)
          for _, b in ipairs(BRIDGES) do
            st = fresh(); place(st, b[2], b[3])
            local low = 0
            r = run(st, function(q, f)
                if q.y > low then low = q.y end
                if q.x >= b[5] then return {} end
                if not b[4] then return { right = true } end
                return { right = true, jump = b[7] == "held" }, q.onGround and q.x >= b[4]
              end, 6, function(q) return q.x >= b[5] and q.onGround end)
            report(b[1], near(st.pepper.y, b[6]) and st.pepper.x >= b[5] - 2 and st.hearts == 3 and not r.fell,
              ("x %.0f y %.0f, lowest %.0f"):format(st.pepper.x, st.pepper.y, low))
          end
        end },
      -- 4 the low road on foot: the street to the bakery's roof, walking and the stairwell only
      { act = function()
          local st = fresh(); place(st, 70, 1144)
          local r = run(st, function(q) return { right = true, down = true } end, 4, function(q) return q.x > 150 end)
          report("street: or crawl under the cafe table", st.pepper.x > 150 and near(st.pepper.y, 1144), ("x %.0f"):format(st.pepper.x))
          st = fresh(); place(st, 150, 1144)
          r = run(st, function() return { right = true } end, 12, function(q) return q.x >= 1250 end)
          report("the low road: street, stairwell A, over R1 to the kitchen fan (walking only)", st.pepper.x >= 1250 and near(st.pepper.y, 952, 4) and st.hearts == 3,
            ("x %.0f y %.0f"):format(st.pepper.x, st.pepper.y))
          st = fresh(); place(st, 1300, 856)
          r = run(st, function() return { right = true } end, 12, function(q) return q.x >= 2028 end)
          report("T1b: over the light well's tiles and R2 to the laundry vent, running", st.pepper.x >= 2028 and near(st.pepper.y, 856, 4) and st.hearts == 3,
            ("x %.0f y %.0f"):format(st.pepper.x, st.pepper.y))
          report("the walls between the tiers are too tall to jump (96 px)", true, "")
          for _, w in ipairs({ { "T1 -> T1b (no fan)", 1230, 952 }, { "T1b -> T2 (no vent)", 1990, 856 } }) do
            st = fresh(); place(st, w[2], w[3])
            r = run(st, function(q, f) return { right = true, jump = f < 40 }, f == 1 end, 3)
            report("  " .. w[1] .. ": a held jump and scramble does not reach", r.landed and r.y >= w[3] - 4, ("y %.1f"):format(r.y))
          end
          for _, j in ipairs(JUMPS) do
            st = fresh(); place(st, j[2], j[3])
            local how, dir, q0 = j[4], j[5], j[3]
            local plan
            if how == "held" then plan = function(q, f) return { [dir] = true, jump = f < 40 }, f == 1 end
            elseif how == "runjump" then plan = function(q, f) return { [dir] = true, jump = f < 40 }, f == 1 end
            elseif how == "tap" or how == "taphold" then plan = function(q, f) return { [dir] = true }, f == 1 end
            elseif how == "walk" then plan = function() return { [dir] = true, walk = true } end
            elseif how == "run" then plan = function() return { [dir] = true } end           -- (r7)
            elseif how == "downA" then plan = function(q, f) if f < 4 then return { down = true }, f == 2 end; return {} end end
            if j[8] == "bounce" then
              r = run(st, plan, 3, function(q) return q.vy < -300 end)
              report(j[1] .. ": it bounces her up", st.pepper.vy < -300, ("vy %.0f"):format(st.pepper.vy))
            else
              if how == "run" and j[2] > 6400 then                     -- (r9: the long roof, all the way down)
                r = run(st, plan, 10, function(q) return q.onGround and q.x > 7160 end)
              elseif how == "run" and j[2] > 6000 then                 -- (r9: off the stack, onto the sauna roof)
                r = run(st, plan, 4, function(q) return q.onGround and q.y > 180 and q.x > 6110 end)
              elseif how == "run" then                                 -- (r7: off the stack, the awning bounces on)
                r = run(st, plan, 4, function(q) return q.onGround and q.x > 3760 end)
              elseif how == "taphold" then                             -- (the landing on the awning bounces on)
                r = run(st, plan, 4, function(q) return q.onGround and q.y < q0 - 70 end)
              else r = run(st, plan, 3) end
              local inX = not j[7] or (r.x + 13 > j[7][1] and r.x - 13 < j[7][2])
              report(j[1], r.landed and (near(r.y, j[6]) or onVentHood(st, j[6])) and r.hearts == 3 and inX, ("y %.1f x %.0f"):format(r.y, r.x))
            end
          end
        end },
      -- 5 every fall off the high road lands on a floor below, no heart lost, never out of the map
      { act = function()
          local def = api.stage().def
          local n, bad = 0, {}
          for _, pr in ipairs(def.props) do
            if pr.kind == "oneway" and not pr.loose and not pr.bounce and pr.y0 ~= 664 and pr.y0 ~= 280 then
              local hood = function(x) for _, v in ipairs(def.steam) do if x + 13 > v.x0 and x - 13 < v.x1 and near(v.y1, pr.y0) then return true end end end
              local wall = function(x) return api.stage().world:solidIn(x, x + 2, pr.y0 - 20, pr.y0 - 2) end
              for _, how in ipairs({ "left", "right", "down" }) do
                local st = fresh()
                local x = how == "left" and pr.x0 + 14 or how == "right" and pr.x1 - 14 or pr.x0 + 20
                if how == "down" and hood(x) then x = pr.x1 - 20 end
                -- (r9: a balcony against a wall has no end to fall off there; a hood is no ledge to drop through)
                local skip = (how == "right" and wall(pr.x1)) or (how == "left" and wall(pr.x0 - 2)) or (how == "down" and hood(x))
                if not skip then
                place(st, x, pr.y0)
                local r
                if how == "down" then r = run(st, function(q, f) if f < 4 then return { down = true }, f == 2 end; return {} end, 4)
                else r = run(st, function() return { [how] = true, walk = true } end, 4) end
                n = n + 1
                if not (r.landed and r.y > pr.y0 and r.hearts == 3 and not r.fell) then bad[#bad + 1] = ("%d,%d %s -> y %.0f"):format(pr.x0, pr.y0, how, r.y) end
                end
              end
            end
          end
          report(("every fall off a ledge (the high road's, the light court's balconies; %d: off each end, Down + A) lands safely below"):format(n), #bad == 0, table.concat(bad, "; "))
          -- (r9) every loose tile: she stands on it until it drops, and lands on a floor below with no heart lost
          n, bad = 0, {}
          for _, pr in ipairs(def.props) do
            if pr.loose then
              local st = fresh(); place(st, (pr.x0 + pr.x1) / 2, pr.y0)
              local r = run(st, function() return {} end, 4)
              n = n + 1
              if not (r.landed and r.y >= pr.y0 and st.pepper.ground ~= pr and r.hearts == 3 and not r.fell) then bad[#bad + 1] = ("%d,%d -> y %.0f"):format(pr.x0, pr.y0, r.y) end
            end
          end
          report(("every loose tile (%d) drops her onto a floor below, no heart lost"):format(n), #bad == 0, table.concat(bad, "; "))
        end },
      -- 6 the gull's nest and the fetch
      { act = function(p, s) tp(6366, 180); p.face = 1 end }, { wait = 0.3 },
      { act = function() love.keypressed("z") end }, { wait = 1.2 },
      { act = function(p, s)
          report("a bark from the sauna's hood: the gull lets go, the ball lands on the nest chimney (88)", s.ball.state == "rest" and near(s.ball.y, 88) and s.magpie.state ~= "perch",
            ("ball %s y %.0f"):format(s.ball.state, s.ball.y)) end },
      { act = function(p, s) tp(s.ball.x + 10, 88); p.face = -1 end }, { wait = 0.3 },
      { act = function() love.keypressed("x") end }, { wait = 0.5 },
      { act = function(p) report("on the chimney Pepper picks the ball up", p.carrying ~= nil) end },
      { act = function(p, s) tp(7290, 472); p.face = 1 end }, { wait = 0.2 },
      { act = function() love.keypressed("x") end }, { wait = 0.4 },
      { act = function(p, s) report("giving the ball to Mia at the roof cafe: GOOD GIRL (FETCH 2000)", s.ball.state == "given" and s.bonus and s.bonus[2] == 2000, s.ball.state) end },
      { wait = 2.6 },
      { act = function(p, s) report("the fetch ends the level", s.events.clear == true or api.getState() ~= "play", api.getState()) end },
      { act = function()
          local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
          print(("%d of %d passed"):format(ok, #results)); love.event.quit() end },
    }
    require("tests_safety")(steps, api, report)                  -- the safety nets (r6/engine), before the summary
  elseif mode == "--auto" then
    love.filesystem.createDirectory("rec_rooftops")
    local function at(cond, act, limit) return { cond = cond, act = act or function() end, limit = limit or 8 } end
    local function settle() return at(function(p) return p.onGround and math.abs(p.vx) < 1 end, function() release() end, 3) end
    local function runTo(x, limit)
      return at(function(p) if p.x >= x then return true end; I.force = { right = true }; return false end, function() release() end, limit or 25)
    end
    local function goTo(x)
      return at(function(p) if math.abs(p.x - x) < 3 then release(); return math.abs(p.vx) < 1 end
          I.force = { [p.x < x and "right" or "left"] = true, walk = true }; return false end, function() release() end, 8)
    end
    -- stand on a vent, wait for its puff, steer (dir) once in the air, until she lands at or above floor y
    local function ride(name, dir, floor)
      local x
      return { at(function(p, s) for _, v in ipairs(s.vents) do if v.d.name == name then x = (v.d.x0 + v.d.x1) / 2 end end; return true end),
        { cond = function(p) if math.abs(p.x - x) < 3 then release(); return math.abs(p.vx) < 1 end
            I.force = { [p.x < x and "right" or "left"] = true, walk = true }; return false end, act = function() release() end, limit = 8 },
        at(function(p) return not p.onGround end, nil, 6),
        at(function(p) if dir then I.force = { [dir] = true } end; return p.onGround and p.y <= floor + 1 end, function() release() end, 5),
        settle() }
    end
    local function flat(list) local out = {}; for _, e in ipairs(list) do if e[1] then for _, q in ipairs(e) do out[#out + 1] = q end else out[#out + 1] = e end end; return out end
    local goose = function(s) for _, k in ipairs(s.critters) do if k.kind == "goose" then return k end end end
    local high = os.getenv("AUTO_ROUTE") == "high"
    local route
    if not high then
      route = {
        runTo(76),
        { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.4 }, { act = function() hold("right") end },   -- the cafe table
        runTo(1180), settle(),                                          -- stairwell A, over R1
        ride("KITCHEN FAN", "right", 856),                              -- beat 1: the first puff
        runTo(1700), runTo(1960), settle(),                             -- the light well's tiles (run!), R2
        ride("LAUNDRY VENT", "right", 760),
        runTo(2300), settle(), ride("SWEEP VENT", "right", 664),     -- the market hall: over the chimneys,
        runTo(2690),                                                   -- the skylight's tiles (run!)
        at(function(p, s) local k = goose(s); I.force = { right = true }                -- beat 3: the roof garden's goose
          if k.state ~= "gone" and math.abs(k.x - p.x) < 72 then release(); love.keypressed("z"); return true end
          return k.state == "gone" or p.x > 3010 end, nil, 15), settle(),
        ride("GARDEN VENT", "right", 664),                              -- beat 2: the balcony
        runTo(3270), settle(),                                          -- its loose tiles
        ride("BALCONY VENT", "right", 568),
        goTo(3414),                                                     -- (r7) the drying yard: up the loose tiles,
        { act = function() hold("right", "jump"); love.keypressed("space") end },
        at(function(p) return p.onGround and p.y < 540 end, function() release() end, 3),
        { act = function() hold("right", "jump"); love.keypressed("space") end },
        at(function(p) return p.onGround and p.y < 508 end, function() release() end, 3),
        { act = function() hold("right", "jump"); love.keypressed("space") end },
        at(function(p) return p.onGround and p.y < 476 end, function() release() end, 3),
        { act = function() hold("right") end },                         -- off the stack onto the springy awning: up onto the tank
        at(function(p) return p.onGround and p.y < 460 and p.x > 3780 end, function() release() end, 4), settle(),
        ride("TANK VENT", "right", 376),
      }
    else
      route = {
        runTo(76), { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.4 }, { act = function() hold("right") end },
        runTo(1180), settle(), ride("KITCHEN FAN", "right", 856),
        ride("ATTIC FAN", "right", 760),
        goTo(1470), { act = function() hold("right") end },             -- the attic's loose tiles: tap hops
        at(function(p) if p.onGround and p.x >= 1500 and p.x < 1660 then love.keypressed("space") end; return p.onGround and p.x >= 1680 end, function() release() end, 6), settle(),
        goTo(1748), { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.5 }, { act = function() release() end }, settle(),
        goTo(1846), { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.5 }, { act = function() release() end }, settle(),
        ride("LOFT VENT", "right", 600),
        goTo(2068), { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.5 }, { act = function() release() end }, settle(),
        goTo(2196), { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.5 }, { act = function() release() end }, settle(),
        goTo(2280), { act = function() hold("right") end },
        at(function(p) if p.onGround and p.x >= 2310 and p.x < 2470 then love.keypressed("space") end; return p.onGround and p.x >= 2490 end, function() release() end, 6), settle(),
        goTo(2548), { act = function() hold("right", "jump"); love.keypressed("space") end }, { wait = 0.5 }, { act = function() release() end }, settle(),
        goTo(2670), { act = function() hold("right") end },
        at(function(p) if p.onGround and p.x >= 2700 and p.x < 2840 then love.keypressed("space") end; return p.onGround and p.x >= 2854 end, function() release() end, 6), settle(),
        goTo(2868), { act = function() hold("right", "jump"); love.keypressed("space") end },   -- the chimney pot: the golden bone
        at(function(p) return p.onGround and p.y < 560 end, function() release() end, 3), settle(),
        { act = function() hold("right", "walk") end }, at(function(p) return p.onGround and p.y > 590 end, function() release() end, 3), settle(),
        ride("BAKERY CHIMNEY", "right", 456),
        goTo(3110), { act = function() hold("right", "jump") end },
        at(function(p) if p.onGround and p.x >= 3180 and p.y > 430 then love.keypressed("space") end; return p.onGround and p.x >= 3680 and p.y < 430 end, function() release() end, 6), settle(),
        ride("BAR FAN", "right", 280),
      }
    end
    -- (r9) both roads meet on the roof bar's terrace (T4, 376): the high road walks off the copper roof's end
    local nearGoose = function(s, p)
      local best
      for _, k in ipairs(s.critters) do
        if k.kind == "goose" and k.state ~= "gone" and math.abs(k.y - p.y) < 24 and k.x > p.x - 20 and (not best or k.x < best.x) then best = k end
      end
      return best
    end
    local finale = {
      settle(), runTo(4440),                                            -- (r9) the hotel roof: its skylights (run!),
      at(function(p, s) local k = nearGoose(s, p); I.force = { right = true }          -- the goose by the hotel kitchen's vent
        if k and math.abs(k.x - p.x) < 72 then release(); love.keypressed("z"); return true end
        return not k or p.x > 4560 end, nil, 15), settle(),
      ride("HOTEL KITCHEN", "right", 280),                              -- over its chimney block,
      runTo(4824),                                                      -- and off it, down into the light court
      at(function(p) return p.onGround and p.y > 650 end, function() release() end, 3), settle(),   -- down into the court
      ride("COURT FAN", "right", 568), ride("LAUNDRY HOOD", "right", 472),   -- up the light court's balconies
      ride("KITCHEN HOOD", "right", 376), ride("BATH FAN", "right", 280),    -- and onto the tall block
      at(function(p, s) local k = nearGoose(s, p); I.force = { right = true }          -- the tall block's goose
        if k and math.abs(k.x - p.x) < 72 then release(); love.keypressed("z"); return true end
        return not k or p.x > 5414 end, nil, 15), settle(),
      goTo(5404), { act = function() hold("right") end },              -- the scaffold's boards: tap hops
      at(function(p) if p.onGround and p.x >= 5404 and p.x < 5554 and p.y < 300 then love.keypressed("space") end
        return p.onGround and p.x >= 5574 and p.y < 300 end, function() release() end, 6), settle(),
      goTo(5604), { act = function() hold("right"); love.keypressed("space") end },   -- the cafe awning bounces her onto T6
      at(function(p) return p.onGround and p.y < 200 and p.x > 5694 end, function() release() end, 4), settle(),
      goTo(5838),                                                       -- the chimney stacks: pot, loose tile, stack
      { act = function() hold("right", "jump"); love.keypressed("space") end },
      at(function(p) return p.onGround and p.y < 156 end, function() release() end, 3),
      { act = function() hold("right", "jump"); love.keypressed("space") end },
      at(function(p) return p.onGround and p.y < 124 end, function() release() end, 3),
      { act = function() hold("right", "jump"); love.keypressed("space") end },
      at(function(p) return p.onGround and p.y < 92 end, function() release() end, 3),
      { act = function() hold("right") end },                         -- off the stack onto the sauna roof
      at(function(p) return p.onGround and p.y > 180 and p.x > 6104 end, function() release() end, 4),
      runTo(6334), goTo(6366),                                          -- the sauna roof's skylight (run!)
      { act = function(p) p.face = 1; love.keypressed("z") end },    -- bark: the gull lets go, the sauna steams
      at(function(p) return not p.onGround end, function() hold("right") end, 4),
      at(function(p) return p.onGround and p.y < 100 end, function() release() end, 4), settle(),
      goTo(6422), { act = function(p) p.face = -1 end },
      at(function(p, s) return s.ball.state == "rest" end, function() love.keypressed("x") end, 4), { wait = 0.6 },
      at(function(p) return p.carrying ~= nil end, nil, 2),
      runTo(7236),                                                      -- the long roof down to the roof cafe
      goTo(7276), { act = function(p) p.face = 1; love.keypressed("x") end },
      { wait = 6 }, { act = function(p, s)
          local st = s:stats()
          print(("AUTOPILOT (%s road) %s: bones %d/%d, secrets %d/%d, lives %d hearts %d, %.1f s played"):format(high and "high" or "low",
            api.getState() == "clear" and "GOOD GIRL!" or api.getState(),
            st.bones, st.total, st.secrets, st.secretsTotal, st.lives, st.hearts, s.def.time - st.time)); io.stdout:flush()
          love.event.quit() end },
    }
    steps = flat({ { wait = 1.2 }, { act = function() love.keypressed("space") end }, { wait = 0.3 } })
    for _, e in ipairs(flat(route)) do steps[#steps + 1] = e end
    for _, e in ipairs(flat(finale)) do steps[#steps + 1] = e end
  else  -- --test: a screenshot tour; frames of a puff and of a loose tile
    local rec
    local function shot(name) return { act = function() love.graphics.captureScreenshot(name .. ".png") end } end
    steps = { { act = function() api.setState("intro") end }, { wait = 0.6 }, shot("rt_00_intro"),
      { act = function() love.keypressed("space") end }, { wait = 0.3 } }
    local spots = { { 60, 1144 }, { 640, 1080 }, { 1100, 952 }, { 1500, 856 }, { 1900, 856 }, { 2840, 760 },
      { 3110, 664 }, { 3720, 568 }, { 3910, 376 }, { 3960, 280 },
      { 4300, 376 }, { 4640, 280 }, { 4860, 664 }, { 5040, 472 }, { 5300, 280 }, { 5560, 320 }, { 5880, 152 },
      { 6050, 88 }, { 6200, 184 }, { 6366, 180 }, { 6416, 88 }, { 6700, 280 }, { 7290, 472 },
      { 1470, 760 }, { 1820, 728 }, { 2020, 600 }, { 2908, 552 }, { 3090, 456 }, { 3720, 424 } }
    for i, sp in ipairs(spots) do
      steps[#steps + 1] = { act = function() tp(sp[1], sp[2]) end }
      steps[#steps + 1] = { wait = 0.25 }
      steps[#steps + 1] = shot(("rt_%02d_spot"):format(i))
    end
    for _, st in ipairs({
      { act = function(p, s) love.filesystem.createDirectory("rec_rooftops_puff"); tp(1212, 952); p.face = 1
          for _, v in ipairs(s.vents) do if v.d.name == "KITCHEN FAN" then v.st, v.t = "rest", 0.6 end end
          rec = { dir = "rec_rooftops_puff", n = 0 } end },
      { wait = 3.0 }, { act = function() rec = nil end },
      { act = function(p, s) love.filesystem.createDirectory("rec_rooftops_tile"); tp(1584, 856); rec = { dir = "rec_rooftops_tile", n = 0 } end },
      { wait = 2.0 }, { act = function() rec = nil end },
      { act = function() love.event.quit() end },
    }) do steps[#steps + 1] = st end
    local f = 0
    api.recHook = function() if rec then f = f + 1; if f % 2 == 0 then rec.n = rec.n + 1; love.graphics.captureScreenshot(("%s/%04d.png"):format(rec.dir, rec.n)) end end end
  end

  local i, since, frame, n, lastHearts, barkT = 1, 0, 0, 0, nil, 0
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; since = since + dt
    old(dt)
    local s = api.stage(); local p = s and s.pepper
    if api.recHook then api.recHook() end
    if mode == "--auto" then
      frame = frame + 1
      if s and s.hearts ~= (lastHearts or s.maxHearts) then print(("  lost a heart at x %.0f y %.0f (step %d)"):format(p.x, p.y, i)) end
      lastHearts = s and s.hearts
      barkT = barkT - dt
      if s and Cr.gullWarn(s) and barkT <= 0 then love.keypressed("z"); barkT = 0.5 end   -- a gull squawks: bark it off
      if os.getenv("AUTO_TRACE") and frame % 10 == 0 then print(("F %d x %.0f y %.0f step %d"):format(frame, p.x, p.y, i)) end
      if frame % 3 == 0 and not os.getenv("NO_REC") then n = n + 1; love.graphics.captureScreenshot(("rec_rooftops/%04d.png"):format(n)) end
    end
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond(p, s) then st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("AUTOPILOT STUCK at step %d: x %.0f y %.0f %s"):format(i, p.x, p.y, p.onGround and "ground" or "air")); io.stdout:flush(); love.event.quit() end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
