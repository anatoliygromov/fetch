-- love riverwalk --lookshots: before / after shots of the Lion King look (look.lua). For each River Walk screen,
-- Pepper stands on open ground and the level is drawn twice into a 320 x 240 canvas, as before and with the look,
-- with no HUD and no talk panel. Saves look_NN_before.png / look_NN_after.png (1x) in the save folder, then quits.
local Look = require("look")
local I = require("input")
return function(api)
  I.testing = true
  local spots = { { 120, 184 }, { 480, 152 }, { 760, 184 }, { 1074, 184 }, { 1350, 216 },
                  { 1680, 154 }, { 2110, 216 }, { 2370, 184 }, { 2660, 152 }, { 3080, 184 } }
  local cv = love.graphics.newCanvas(320, 240)
  local T, i, phase = 0, 0, "start"
  local old = love.update
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
        cv:newImageData():encode("png", ("look_%02d_%s.png"):format(i, on and "after" or "before"))
      end
      Look.on = true
    end
    i = i + 1
    local sp = spots[i]
    if not sp then print("LOOKSHOTS " .. (i - 1)); io.stdout:flush(); love.event.quit(); return end
    local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = sp[1], sp[2], 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, (i - 1) * 320)); s.bikes = {}; s.bikeT = 99
  end
end
