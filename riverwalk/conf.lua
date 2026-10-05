function love.conf(t)
  t.identity = "pepper_riverwalk"
  t.version = "11.0"
  t.window.title = "Pepper: River Walk (greybox)"
  t.window.width, t.window.height = 640, 480
  t.window.resizable = true
  t.window.vsync = 1
  t.modules.physics = false
end
