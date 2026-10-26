-- tools/layer_ids_hook.lua: a layer map of the game's own frames (25 Oct 2026, City Park layer plan).
-- Not part of the game. tools/layer_frames_tall.py copies riverwalk/ to a temp folder, puts this file in the copy
-- and requires it from the copy's tests_look.lua when LAYER_IDS is set; the game in the repo is never changed.
-- Every pass of St:draw picks its layer with Look.use(name) (look.lua; the far layers, back, ground, play, front)
-- or Look.off() (the bones, Mia, the ball, Pepper: drawn as made), and the sky with Look.sky / Look.skyTall. Here
-- each of them sets a flat shader instead that writes the layer's number into the red channel (id * 20) wherever
-- a pixel is drawn (alpha 0.5 or more), so a frame comes out as a map of which layer is on top at each pixel.
-- The sweep then runs as usual (LOOK_SWEEP=1); its frames line up pixel for pixel with the colour sweep.
local Look = require("look")
local lg = love.graphics
local ID = { sky = 1, clouds = 2, city = 3, shore = 4, mid = 5, water = 6, back = 7, ground = 8, play = 9, front = 10,
  char = 11 }
local shader = lg.newShader([[
extern float id;
vec4 effect(vec4 col, Image tex, vec2 tc, vec2 sc) {
  float a = Texel(tex, tc).a * col.a;
  if (a < 0.5) discard;
  return vec4(id * 20.0 / 255.0, 0.0, 0.0, 1.0);
}]])
local function set(name)
  lg.setShader(shader)
  shader:send("id", ID[name] or 12)
end
Look.use = function(name) set(name) end
Look.off = function() set("char") end
for _, k in ipairs({ "sky", "skyTall" }) do
  local f = Look[k]
  Look[k] = function(...) set("sky"); return f(...) end
end
local front = Look.front
Look.front = function(...) set("front"); return front(...) end
print("[layer ids] on"); io.stdout:flush()
