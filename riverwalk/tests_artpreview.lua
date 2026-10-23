-- The art preview (r8/preview): shots and frame runs of every piece of art batch 1 at its place in the game, for
-- the owner to judge the art in context (tools/art_preview.sh runs it with and without the batch's files and makes
-- the before/after pictures, the GIFs and the overview).
--   love riverwalk --level riverwalk --artpreview       the promenade's cyclists, the road's near-lane riders
--   love riverwalk --level downtown_tall --artpreview   the cargo bike, the vintage tram, the roof kit, the tall
--                                                        house fronts, the row across the square, the spire
--   love riverwalk --bonus --artpreview                 Mia's throw in FETCH FRENZY
-- Screenshots go to the save folder as <AP_TAG>_<name>.png (AP_TAG: "before" or "after"); a frame run goes to
-- <AP_TAG>_<name>/0001.png ... Nothing here changes the game.
local I = require("input")
local Vc = require("vcam")
return function(api, level, bonus)
  I.testing = true
  api.talk.draw = function() end                                  -- (no talk panels over the art)
  local TAG = os.getenv("AP_TAG") or "after"
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end
  local function release() I.force = {} end
  local function quiet(s) s.bikes, s.bikeT = {}, 99; if s.road then s.road.list, s.road.t = {}, 99 end end
  local function tp(x, y, face)
    local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    p.face = face or 1
    s.hearts = 3
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); quiet(s)
    if Vc.snap then Vc.snap(s) end
  end
  local steps = {}
  local function add(t) for _, st in ipairs(t) do steps[#steps + 1] = st end end
  local function shot(name) return { act = function()
    local s = api.stage(); local p = s and s.pepper
    if p and not bonus then print(("shot %s: pepper %.0f %.0f %s, cam %.0f %.0f"):format(name, p.x, p.y, p.mode, s.cam, s.camY or 0)); io.stdout:flush() end
    love.graphics.captureScreenshot(TAG .. "_" .. name .. ".png") end } end
  -- a frame run: every `every` frames for `secs` seconds, into <tag>_<name>/
  local function rec(name, secs, every)
    return { rec = name, during = secs, every = every or 2 }
  end
  local function wait(t) return { wait = t } end
  local function act(f) return { act = f } end

  if bonus then
    add({ act(function() api.startBonus() end), wait(0.8), act(function() love.keypressed("space") end), wait(0.05),
      -- the first throw lets go 1.2 s into play: the wind-up from 0.84 s; Pepper stays put (no catching)
      act(function() local b = api.bonus(); b.pepper.x = 230 end),
      { cond = function() local b = api.bonus(); return b and b.phase == "play" and b.nextT <= 0.6 end, act = function() end, limit = 8 },
      rec("bonus_throw", 1.5, 1) })
    -- the 8 frames of her clip, one still each, from the second throw (its wind-up starts nextT - 0.36 s)
    add({ act(function() local b = api.bonus(); b.pepper.x = 230 end) })
    for f = 1, 8 do
      add({ { cond = function()
        local b = api.bonus(); local m = b and b.mia
        if not m then return false end
        if f <= 5 then return m.state == "windup" and m.t >= (f - 1) / 5 * 0.36 + 0.01 end
        return m.state == "throw" and m.t >= (f - 6) / 3 * 0.3 + 0.01
      end, act = function() end, limit = 6 }, shot(("bonus_throw_f%d"):format(f)), wait(1 / 60) })
    end
  elseif level == "riverwalk" then
    local Sp = require("setpieces")
    local function bike(x, rider, speed)
      return act(function() local s = api.stage(); s.bikes = { { x = x, y = 184, warn = -1, zone = s.def.bikes[1], speed = speed or 0.01, rider = rider } }; s.bikeT = 99 end)
    end
    local function traffic(list)                                      -- (as tests.lua: riders put on the road, still)
      return act(function()
        local s = api.stage(); local Rd = require("road"); local A = Rd.art()
        s.road.list = {}
        for _, v in ipairs(list) do
          local im = (A.near or A.riders)[v[1]]
          local sp = { 0, s.world.width }
          for _, q in ipairs(s.road.spans) do if v[2] >= q[1] and v[2] < q[2] then sp = q end end
          s.road.list[#s.road.list + 1] = { im = im, x = v[2], w = im:getWidth(), vx = (v[3] and 1 or -1) * 0.01, sp = sp, bob = 1,
            flip = not v[3], f = 1, cam0 = 0, base = 0.01, still = true, top = Rd.RIDER_TOP }
        end
        s.road.t = 99
      end)
    end
    add({ wait(0.6), act(function() love.keypressed("space") end), wait(0.3),
      act(function() tp(860, 184) end), wait(0.3), bike(960, 1), wait(0.05), shot("rw_promenade_rider1"),
      act(function() tp(860, 184) end), wait(0.3), bike(960, 2), wait(0.05), shot("rw_promenade_rider2"),
      act(function() tp(800, 112) end), wait(0.3), bike(905, 1), wait(0.05), shot("rw_promenade_under_kiosk"),
      act(function() tp(150, 184) end), wait(0.3), traffic({ { 1, 250, false }, { 2, 60, true } }), wait(0.05), shot("rw_road_riders"),
      act(function() tp(2952, 154) end), wait(0.3), traffic({ { 2, 3020, false } }), wait(0.05), shot("rw_road_rider_planter"),
      -- a promenade bike riding by (a frame run)
      act(function() tp(700, 184) end), wait(0.3),
      act(function() local s = api.stage(); s.bikes = { { x = s.cam + 380, y = 184, warn = -1, zone = s.def.bikes[1], speed = 115, rider = 1 } }; s.bikeT = 99 end),
      rec("rw_promenade_bike", 3.4, 2) })
  else  -- downtown_tall
    local STREET = 424
    add({ wait(0.6), act(function() love.keypressed("space") end), wait(0.3) })
    local spots = {
      { "dt_bakery_fronts", 1250, STREET }, { "dt_loggia", 1496, 280 }, { "dt_loggia_from_street", 1470, STREET },
      { "dt_gable_chimney", 1640, 244 }, { "dt_chimney_top", 1636, 200 }, { "dt_gallery", 1752, 256 },
      { "dt_gallery2", 1852, 256 }, { "dt_dormer", 1948, 264 }, { "dt_ledges", 2044, 248 }, { "dt_ledge2", 2140, 264 },
      { "dt_flower_roof", 2330, 232 }, { "dt_ledge3", 2440, 248 }, { "dt_footbridge", 2560, 272 },
      { "dt_square_street", 60, STREET }, { "dt_plaza_street", 1500, STREET }, { "dt_market_street", 2236, STREET },
      { "dt_flooded_square", 2780, STREET }, { "dt_spire_a", 3250, STREET }, { "dt_spire_b", 3460, STREET },
    }
    for _, sp in ipairs(spots) do add({ act(function() tp(sp[2], sp[3]) end), wait(0.8), shot(sp[1]) }) end
    add({
      -- the cargo bike passing under Pepper on the kiosk
      act(function() tp(2000, 388); local s = api.stage(); s.zoneIn[s.def.bikes[1]] = true; s.bikes = { { x = 2120, y = STREET, warn = -1, zone = s.def.bikes[1], speed = 110 } } end),
      wait(0.5), shot("dt_cargo_bike_under_kiosk"),
      act(function() tp(2000, 388); local s = api.stage(); s.zoneIn[s.def.bikes[1]] = true; s.bikes = { { x = s.cam + 380, y = STREET, warn = -1, zone = s.def.bikes[1], speed = 110 } } end),
      rec("dt_cargo_bike", 4.2, 2),
      -- the vintage tram: comes in, stops at its sign, drives off (seen whole: the camera over the stop)
      act(function() tp(2150, STREET, -1); local s = api.stage(); s.zoneIn[s.def.bikes[1]] = true; s.trams[1].car = nil; s.trams[1].t = 0.05 end),
      rec("dt_tram", 12.0, 4),
      act(function() tp(2150, STREET, -1); local s = api.stage(); s.trams[1].car = nil; s.trams[1].t = 0.05 end),
      { cond = function(p, s) local c = s.trams[1].car; return c and c.state == "stop" end, act = function() end, limit = 12 },
      wait(0.5), shot("dt_tram_at_stop"),
      act(function() tp(2000, 388); local s = api.stage(); s.trams[1].car = nil; s.trams[1].t = 0.05 end),
      { cond = function(p, s) local c = s.trams[1].car; return c and c.state == "stop" end, act = function() end, limit = 12 },
      wait(0.5), shot("dt_tram_from_kiosk"),
    })
  end
  add({ wait(0.2), act(function() love.event.quit() end) })

  local i, since, n, frame = 1, 0, 0, 0
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; since = since + dt
    old(dt)
    local s = api.stage(); local p = s and s.pepper
    if s and not bonus then s.hearts = 3 end
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.rec then
      frame = frame + 1
      if frame % st.every == 0 then
        n = n + 1
        love.filesystem.createDirectory(TAG .. "_" .. st.rec)
        love.graphics.captureScreenshot(("%s_%s/%04d.png"):format(TAG, st.rec, n))
      end
      if since >= st.during then i, since, n, frame = i + 1, 0, 0, 0 end
    elseif st.cond then
      if st.cond(p, s) then st.act(p, s); i, since = i + 1, 0
      elseif since > st.limit then print(("ARTPREVIEW STUCK at step %d"):format(i)); io.stdout:flush(); i, since = i + 1, 0 end
    else st.act(p, s); i, since = i + 1, 0 end
  end
end
