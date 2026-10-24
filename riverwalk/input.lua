-- Buttons, the same on the RG35XX and the keyboard. Tests can hold buttons through I.force.
--   d-pad / arrows     move;  Down = crouch and crawl
--   A / Space or Up    jump (hold for a higher jump);  Down + A drops through a railing or deck
--   B / Shift          walk (hold)
--   X / X key          pick up, drop, give
--   Y / Z key          bark
--   Start / Enter      pause;  Select / G   debug view
local I = { pad = nil, force = {} }
-- the device used last ("pad" or "key"): the menus draw its glyphs (round A / B coins, or SPACE / ESC keycaps).
-- main.lua sets it on every press; it starts as "pad" when a gamepad is plugged in (the handheld), else "key".
I.last = "key"
function I.setLast(kind) I.last = kind end
function I.startDevice() if love.joystick and love.joystick.getJoystickCount() > 0 then I.last = "pad" end end
local keys = {
  left = { "left", "a" }, right = { "right", "d" }, down = { "down", "s" }, up = { "up", "w" },
  jump = { "space", "up", "w" }, walk = { "lshift", "rshift" }, act = { "x" }, bark = { "z" },
}
local pads = { left = "dpleft", right = "dpright", down = "dpdown", up = "dpup", jump = "a", walk = "b", act = "x", bark = "y" }
function I.down(name)
  if I.force[name] then return true end
  if I.testing then return false end
  for _, k in ipairs(keys[name]) do if love.keyboard.isDown(k) then return true end end
  if I.pad and pads[name] and I.pad:isGamepadDown(pads[name]) then return true end
  return false
end
function I.axis()
  local x = 0
  if I.down("left") then x = x - 1 end
  if I.down("right") then x = x + 1 end
  if I.pad and x == 0 and not I.testing then
    local ax = I.pad:getGamepadAxis("leftx")
    if math.abs(ax) > 0.35 then x = ax > 0 and 1 or -1 end
  end
  return x
end
-- which game button a key or pad button is (for presses)
function I.keyName(k)
  for name, list in pairs(keys) do for _, kk in ipairs(list) do if kk == k and name ~= "up" then return name end end end
  return nil
end
function I.padName(b)
  for name, pb in pairs(pads) do if pb == b and name ~= "up" then return name end end
  return nil
end
return I
