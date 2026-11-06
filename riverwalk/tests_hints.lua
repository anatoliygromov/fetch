-- love riverwalk --level <name> --hintshots: a frame of every control hint (a hint with a button) the level has, in
-- its own zone. Pepper is put on the ground in the zone (the floor nearest her start's that meets the zone's minY /
-- maxY) and says the hint (St:say, so its condition, a gull or a ball, need not hold), the gamepad's glyphs (the
-- RG35XX); the level's first hint again with the keyboard's. Shot from the window (640 x 480, the game at 2x): hint_<level>_<nn>.png
-- and .txt (the bodies hud.lua placed, for tools/layout_qa_menus.py) in the save folder. Prints "HINTSHOTS <folder>"
-- and the list (nn, button, text), then quits. tools/hint_frames.py turns them into 1x and 4x frames.
local I = require("input")
local U = require("hud")
return function(api)
  I.testing = true
  local T, k = 0, 0
  local pending
  local still                                                       -- (her hurt blink hides her: no blink in a shot)
  local function shot(name) return { act = function() still = true; api.stage().pepper.invuln = 0
    love.graphics.captureScreenshot(name .. ".png"); U.log = {}; pending = name end, wait = 0.12 } end
  local oldDraw = love.draw
  love.draw = function()
    oldDraw()
    if pending then
      local out = {}
      for _, b in ipairs(U.log or {}) do out[#out + 1] = table.concat(b, " ") end
      love.filesystem.write(pending .. ".txt", table.concat(out, "\n") .. "\n"); U.log, pending = nil, nil
    end
  end
  local function floors(w, x)
    local out, y = {}, -1000
    while true do local g = w:groundAt(x, y + 1); if not g then break end; out[#out + 1] = g; y = g end
    return out
  end
  local function place(h)
    local s = api.stage(); local p, w = s.pepper, s.world
    local x = math.floor((h.x0 + math.min(h.x1, w.width)) / 2)
    local sx = s.def.start.x                                        -- (a level-wide hint: at her start, not in the water)
    if h.x1 - h.x0 > 640 and sx >= h.x0 and sx < h.x1 then x = sx + 60 end
    s.magpieSaid = true                                             -- (its own HOLD: SNEAK would replace the hint)
    local y, ref = nil, s.def.start.y                               -- the floor nearest her start's (the walking line)
    for _, g in ipairs(floors(w, x)) do
      if (not h.minY or g >= h.minY) and (not h.maxY or g <= h.maxY) and (not y or math.abs(g - ref) < math.abs(y - ref)) then y = g end
    end
    y = y or s.def.start.y
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 99
    s.cam = math.max(0, math.min(w.width - 320, x - 140)); s.bikes = {}; s.bikeT = 99
    s.camY = math.max(0, math.min(s.camYMax or 0, y - 168))
    api.talk.reset(); s.msg = nil; still = false
    s:say({ btn = h.btn, text = h.text }, 8)
  end
  local lvl = api.levelName()
  local list, seen = {}, {}
  for _, h in ipairs(api.stage().def.hints or {}) do
    local key = h.btn and (h.btn .. "|" .. h.text)
    if key and not seen[key] then seen[key] = true; list[#list + 1] = h end
  end
  local steps = { { wait = 0.6 }, { act = function() love.keypressed("space") end, wait = 0.3 }, { act = function() api.setState("play") end, wait = 0.1 } }
  local names = {}
  for i, h in ipairs(list) do
    local n = ("hint_%s_%02d"):format(lvl, i)
    names[#names + 1] = ("%02d %s %s"):format(i, h.btn, h.text)
    steps[#steps + 1] = { act = function() I.last = "pad"; place(h) end, wait = 1.0 }
    steps[#steps + 1] = shot(n)
  end
  if list[1] then
    steps[#steps + 1] = { act = function() I.last = "key"; place(list[1]) end, wait = 1.0 }
    steps[#steps + 1] = shot(("hint_%s_%02d_key"):format(lvl, 1))
  end
  local old = love.update
  love.update = function(dt)
    old(dt); T = T + dt
    local s = api.stage(); if s and s.pepper and not still then s.pepper.invuln = 99 end
    local st = steps[k]
    if st and T < (st.wait or 0) then return end
    k = k + 1; T = 0
    st = steps[k]
    if not st then
      print("HINTSHOTS " .. love.filesystem.getSaveDirectory())
      for _, l in ipairs(names) do print("HINT " .. l) end
      io.stdout:flush(); love.event.quit(); return
    end
    if st.act then st.act() end
  end
end
