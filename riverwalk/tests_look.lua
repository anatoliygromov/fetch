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
                  { 1680, 154 }, { 2110, 216 }, { 2370, 184 }, { 2660, 152 }, { 3080, 184 } },
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
  if os.getenv("LOOK_SWEEP") then
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
      s.bikes = {}; s.bikeT = 99
      for _, cy in ipairs(tiers) do
        for _, cx in ipairs(xs) do
          local px = cx + 140
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
      s.bikes[1] = { x = sp[1] + tonumber(os.getenv("LOOK_BIKE")), y = sp[2], rider = 1, speed = 0, warn = 99,
                      zone = { speed = 0, endX = -1e9, w = 48, h = 26 } }
    end
  end
end
