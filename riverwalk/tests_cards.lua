-- love riverwalk --cardshots: the level select's pictures (ui/hud-v8 step 3). Every level of levels.lua is loaded
-- alone, Pepper is put on the ground at each spot of SPOTS (or, for a level not listed, every eighth of its width),
-- the game runs 40 steps with no buttons so the camera settles, and the level is drawn (no HUD, no talk) to a
-- 320 x 240 canvas: card_<name>_<x>.png in the save folder. tools/card_shots.py crops the chosen ones 1:1 into
-- riverwalk/art/ui/cards/<name>.png. Prints "CARDSHOTS <folder>" and quits.
local St = require("stage")
local Vc = require("vcam")
local Talk = require("talk")
local LEVELS = require("levels")
-- the characteristic spot of each level (Pepper's x; y: the ground found under her, the lowest one unless top;
-- nobones: the greybox levels' placeholder bones are left out of the picture)
local SPOTS = {
  riverwalk = { { 960 } }, citypark_tall = { { 1080 } }, downtown_tall = { { 1320 } },
  rooftops = { { 3640, nobones = true } }, soder = { { 1280, nobones = true } }, night = { { 560, nobones = true } },
}
return function(api)
  local lg = love.graphics
  require("bigfont").print = function() end                        -- (review fix 1) no greybox debug labels on a card
  local canvas = lg.newCanvas(320, 240)
  local only = os.getenv("CARDS_ALL")                              -- set: every eighth of each level, to choose spots
  -- the ground surfaces at x (tops of solid ground with 40 px clear above), lowest first
  local function grounds(w, x)
    local out, H = {}, w.height or 240
    for y = H - 1, 8, -1 do
      if w:solidIn(x - 6, x + 6, y, y) and not w:solidIn(x - 6, x + 6, y - 40, y - 1) then out[#out + 1] = y end
    end
    return out
  end
  local done = false
  love.update = function()
    if done then return end
    done = true
    for _, l in ipairs(LEVELS) do
      if love.filesystem.getInfo("level/" .. l.name .. ".lua") then
        local def = require("level." .. l.name)
        local spots = SPOTS[l.name]
        local probe = St.new(def)
        if only or not spots then
          spots = {}
          for k = 1, 7 do spots[#spots + 1] = { math.floor(probe.world.width * k / 8) } end
        end
        if probe.ground then probe.ground:release() end
        for _, sp in ipairs(spots) do
          local s = St.new(def)
          s.time = def.time; s.bikes = {}; s.bikeT = 99
          local g = grounds(s.world, sp[1])
          local y = sp.top and g[#g] or g[1] or def.start.y
          local p = s.pepper
          p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.invuln = sp[1], y, 0, 0, true, nil, "normal", 0
          p.face = sp.face or 1
          s.cam = math.max(0, math.min(s.world.width - 320, sp[1] - 140)); Vc.snap(s)
          if s.chase then s.chase = nil end
          for _ = 1, 40 do s:update(1 / 60, {}) end
          p.invuln = 0
          if sp.nobones then for _, bn in ipairs(s.bones) do bn.taken = true end end
          lg.setCanvas(canvas); lg.clear(0, 0, 0, 1); lg.origin()
          s:draw(false)
          lg.setCanvas()
          canvas:newImageData():encode("png", ("card_%s_%d.png"):format(l.name, sp[1]))
          print(("card %s x %d y %d cam %d,%d"):format(l.name, sp[1], p.y, s.cam, s.camY or 0))
          if s.ground then s.ground:release(); s.ground = nil end
        end
      end
    end
    Talk.reset()
    print("CARDSHOTS " .. love.filesystem.getSaveDirectory()); io.stdout:flush()
    love.event.quit()
  end
end
