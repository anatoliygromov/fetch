-- love riverwalk [--level citypark|downtown] --lookshots: before / after shots of the Lion King look (look.lua).
-- For each screen of the level,
-- Pepper stands on open ground and the level is drawn twice into a 320 x 240 canvas, as before and with the look,
-- with no HUD and no talk panel. Saves look_NN_before.png / look_NN_after.png (1x) in the save folder, then quits.
local Look = require("look")
local I = require("input")
return function(api)
  I.testing = true
  local SPOTS = {
    riverwalk = { { 120, 184 }, { 480, 152 }, { 760, 184 }, { 1074, 184 }, { 1350, 216 },
                  { 1680, 154 }, { 2110, 216 }, { 2520, 196 }, { 2868, 216 }, { 3288, 184 } },   -- (night/06nov-rw: the harbour +208)
    citypark = { { 60, 184 }, { 476, 184 }, { 820, 188 }, { 1132, 156 }, { 1320, 184 }, { 1640, 184 } },
    downtown = { { 60, 184 }, { 340, 184 }, { 650, 184 }, { 1060, 184 }, { 1340, 184 }, { 1668, 148 } },
  }
  local name = ({ park = "citypark", town = "downtown" })[api.stage().def.art] or "riverwalk"
  local spots = SPOTS[name]
  if os.getenv("LOOK_SPOTS") then                                  -- (art/fixes) custom spots "x,y;x,y", any level
    spots = {}
    for a, b in os.getenv("LOOK_SPOTS"):gmatch("(%-?%d+),(%-?%d+)") do spots[#spots + 1] = { tonumber(a), tonumber(b) } end
  end
  local prefix = name == "riverwalk" and "look" or ("look_" .. name)
  local cv = love.graphics.newCanvas(320, 240)
  local T, i, phase = 0, 0, "start"
  local old = love.update
  -- (art/placement) LOOK_SWEEP=1: every screen of the level, look on, no HUD. The camera steps along the level by
  -- LOOK_STEP px (default 300; the last frame ends at the level's right end) at each height tier (a tall level:
  -- the bottom of the world, then every 120 px up to the top). Pepper stands on the highest floor 60-236 px down
  -- the screen at the camera + 140, or is left out. Saves sweep_<level>_y<camY>_x<cam>.png (1x), then quits.
  -- (7 Nov, cplog) LOOK_CRAWL="1530,1556,1585": Pepper crawling (crouched, the crawl clip's frame LOOK_FRAME, default
  -- 5) on the floor under her at each x (or at y LOOK_CRAWLY: the path under a log), the camera at LOOK_CAM (default x - 140) and LOOK_CAMY (default the
  -- bottom of the world); a bone she has passed (within her reach) is taken. Saves crawl_<level>_x<x>.png (1x, look
  -- on, no HUD), then quits. For the hollow log frames.
  if os.getenv("LOOK_CRAWL") then
    love.update = function(dt)
      dt = 1 / 60; T = T + dt
      old(dt)
      local s = api.stage()
      if phase == "start" and T > 0.5 then love.keypressed("space"); phase = "go"; T = 0 end
      if phase ~= "go" or T < 0.7 then return end
      local w, p = s.world, s.pepper
      s.bikes = {}; s.bikeT = 99
      local n = 0
      for v in os.getenv("LOOK_CRAWL"):gmatch("%-?%d+") do
        local px = tonumber(v)
        local cx = tonumber(os.getenv("LOOK_CAM") or "") or (px - 140)
        local cy = tonumber(os.getenv("LOOK_CAMY") or "") or math.max(0, w.height - 240)
        local fy = tonumber(os.getenv("LOOK_CRAWLY") or "") or w:floor(px - 4, px + 4, px, cy + 60, cy + 240, -1e9)
        p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.invuln = px, fy or cy + 200, 0, 0, true, nil, "normal", 0
        p.crouch, p.anim, p.frame, p.face = true, "crawl", tonumber(os.getenv("LOOK_FRAME") or "") or 5, 1
        for _, bn in ipairs(s.bones) do if math.abs(bn.y - p.y) < 20 and bn.x - 5 < px + 17 and bn.x > px - 400 then bn.taken = true end end
        s.cam, s.camY = cx, cy
        love.graphics.push("all"); love.graphics.setCanvas(cv); love.graphics.clear(0, 0, 0, 1); love.graphics.origin()
        s:draw(false)
        love.graphics.pop()
        cv:newImageData():encode("png", ("crawl_%s_x%04d.png"):format(name, px))
        n = n + 1
      end
      print("CRAWL " .. n); io.stdout:flush(); love.event.quit()
      phase = "done"
    end
    return
  end
  if os.getenv("LOOK_SWEEP") then
    -- (art/dt-highroad-06nov) LOOK_OLDHOUSES=1: decision 2a off, the old plaza houses (arthooks H.PLAZA_FRONTS)
    if os.getenv("LOOK_OLDHOUSES") then (package.loaded.arthooks or require("arthooks")).PLAZA_FRONTS = false end
    -- (night/06nov-dt, fix round 2) LOOK_CLOSED=1: the closed street (arthooks H.CLOSED_STREET, decision 2)
    if os.getenv("LOOK_CLOSED") then (package.loaded.arthooks or require("arthooks")).CLOSED_STREET = true end
    love.update = function(dt)
      dt = 1 / 60; T = T + dt
      old(dt)
      local s = api.stage()
      if phase == "start" and T > 0.5 then love.keypressed("space"); phase = "go"; T = 0 end
      if phase ~= "go" or T < 0.7 then return end
      local w, p = s.world, s.pepper
      local step = tonumber(os.getenv("LOOK_STEP") or "") or 300
      local ymax = math.max(0, w.height - 240)
      local tiers, n = {}, 0
      for y = ymax, 0, -120 do tiers[#tiers + 1] = y end
      if tiers[#tiers] ~= 0 then tiers[#tiers + 1] = 0 end
      local xs = {}
      for x = 0, w.width - 320, step do xs[#xs + 1] = x end
      if xs[#xs] ~= w.width - 320 then xs[#xs + 1] = w.width - 320 end
      -- (art/dt-sample) LOOK_XS="1920,1700" and LOOK_YS="120,240": only these camera spots (sample screen frames);
      -- LOOK_PX: Pepper at the camera + this (default 140)
      if os.getenv("LOOK_XS") then xs = {}; for v in os.getenv("LOOK_XS"):gmatch("%-?%d+") do xs[#xs + 1] = tonumber(v) end end
      if os.getenv("LOOK_YS") then tiers = {}; for v in os.getenv("LOOK_YS"):gmatch("%-?%d+") do tiers[#tiers + 1] = tonumber(v) end end
      s.bikes = {}; s.bikeT = 99
      if os.getenv("LOOK_CLEAN") then                          -- (8 Nov concepts) base frames: no labels, bones,
        require("scene").label = function() end               -- critters, girl or nest bird (fewer holes)
        local Cr = package.loaded.critters or require("critters"); Cr.draw = function() end; Cr.drawBird = function() end
        require("scene").magpie = function() end
        for _, bn in ipairs(s.bones or {}) do bn.taken = true end
        if s.girl then s.girl.x = -99999 end
        for _, pr in ipairs(s.def.props or {}) do pr.name = "" end
      end
      -- (day/07nov-dt, round 3) LOOK_CARGO=x in a sweep: a cargo bike standing with its middle at world x, with its
      -- zone's depot (clipped at the gateway's jamb as it rides in), for frames of the shed's gate
      if os.getenv("LOOK_CARGO") and s.def.bikes then
        local z
        for _, b in ipairs(s.def.bikes) do if b.kind == "cargo" then z = z or b end end
        if z then s.bikes[1] = { x = tonumber(os.getenv("LOOK_CARGO")), y = z.roadY or s.def.foot, zone = { kind = "cargo", w = z.w, h = z.h, speed = 0, endX = -1e9, rail = true, depot = z.depot }, warn = -9 } end
      end
      -- (night 6 Nov, cp) LOOK_MAGPIE=k: the magpie sits on its perch k with the ball (card frames of a perch)
      if os.getenv("LOOK_MAGPIE") and s.def.magpie then s:resetMagpie(tonumber(os.getenv("LOOK_MAGPIE"))) end
      -- (6 Nov, cp_props_06nov) LOOK_KICK=1: every leaf pile drawn as Pepper leaves it after running through
      if os.getenv("LOOK_KICK") then for _, pr in ipairs(s.def.props) do if pr.leaves then s.kicked[pr] = true end end end
      for _, cy in ipairs(tiers) do
        for _, cx in ipairs(xs) do
          local px = cx + (tonumber(os.getenv("LOOK_PX") or "") or 140)
          local fy = w:floor(px - 4, px + 4, px, cy + 60, cy + 236, -1e9)
          p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = 0, 0, true, nil, "normal", false, 0
          if fy then p.x, p.y = px, fy else p.x, p.y = -999, cy + 200 end
          s.cam, s.camY = cx, cy
          love.graphics.push("all"); love.graphics.setCanvas(cv); love.graphics.clear(0, 0, 0, 1); love.graphics.origin()
          s:draw(false)
          love.graphics.pop()
          cv:newImageData():encode("png", ("sweep_%s_y%03d_x%04d.png"):format(name, cy, cx))
          n = n + 1
        end
      end
      print("SWEEP " .. n .. " " .. w.width .. "x" .. w.height); io.stdout:flush(); love.event.quit()
      phase = "done"
    end
    return
  end
  love.update = function(dt)
    dt = 1 / 60; T = T + dt
    old(dt)
    local s = api.stage()
    if phase == "start" and T > 0.5 then love.keypressed("space"); phase = "go"; T = 0 end
    if phase ~= "go" or T < 0.7 then return end
    T = 0
    if i > 0 then                                                  -- shoot the spot placed last time
      for _, on in ipairs({ false, true }) do
        Look.on = on
        love.graphics.push("all"); love.graphics.setCanvas(cv); love.graphics.clear(0, 0, 0, 1); love.graphics.origin()
        s:draw(false)
        love.graphics.pop()
        cv:newImageData():encode("png", ("%s_%02d_%s.png"):format(prefix, i, on and "after" or "before"))
      end
      Look.on = true
    end
    i = i + 1
    local sp = spots[i]
    if not sp then print("LOOKSHOTS " .. (i - 1)); io.stdout:flush(); love.event.quit(); return end
    local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = sp[1], sp[2], 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, sp[1] - 140)); s.bikes = {}; s.bikeT = 99
    if os.getenv("LOOK_BIKE") then                                  -- (art/preflight) a parked bike for card frames
      s.bikes[1] = { x = sp[1] + tonumber(os.getenv("LOOK_BIKE")), y = sp[2], rider = tonumber(os.getenv("LOOK_RIDER") or "1"), speed = 0, warn = 99,   -- (5 Nov: LOOK_RIDER=2, the second rider)
                      zone = { speed = 0, endX = -1e9, w = 48, h = 26 } }
    end
    -- (art/dt-traffic-06nov) LOOK_CARGO=dx: a cargo bike parked dx px right of Pepper (the street's first cargo
    -- zone); LOOK_TRAM=x: the back lane's first tram standing with its middle at world x (LOOK_TRAM_X: its x for
    -- the wheels, so frames of one spot can show the wheel loop)
    if os.getenv("LOOK_CARGO") and s.def.bikes then
      local z
      for _, b in ipairs(s.def.bikes) do if b.kind == "cargo" then z = z or b end end
      if z then s.bikes[1] = { x = sp[1] + tonumber(os.getenv("LOOK_CARGO")), y = z.roadY or sp[2], zone = { kind = "cargo", w = z.w, h = z.h, speed = 0, endX = -1e9, rail = true, depot = z.depot }, warn = -9 } end
    end
    if os.getenv("LOOK_TRAM") and s.trams and s.trams[1] then
      local x = tonumber(os.getenv("LOOK_TRAM"))
      s.trams[1].car = { x = x, v = 0, state = "stop", wait = 99 }; s.trams[1].t = 99
      if s.trams[2] then s.trams[2].car = nil; s.trams[2].t = 99 end
    end
  end
end
