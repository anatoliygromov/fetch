-- runs a plain Lua script inside LOVE when no Lua interpreter is installed (see main.lua)
function love.conf(t)
  t.identity = "fetch_tools"
  t.window = false
  for _, m in ipairs({ "audio", "graphics", "image", "joystick", "keyboard", "mouse", "physics", "sound", "touch",
                       "video", "window", "font" }) do t.modules[m] = false end
end
