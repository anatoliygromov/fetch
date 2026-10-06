-- Passing traffic on the road in front of the promenade: cars and cyclists in the near lane (the road band is
-- y 199-240 under the promenade). Pure scenery: nothing here touches Pepper. Vehicles appear only where there is
-- road (flat promenade at y 184) and are clipped to it, so none drives over the river or the quay.
--   cars drive to the right (Swedish right-hand traffic, near lane), wheels on y 239, 110-170 px/s
--   cyclists use the bike lane next to the kerb in either direction, wheels on y 236, 45-70 px/s
local Sc = require("scene")
local lg = love.graphics
local Rd = {}
Rd.__index = Rd

local art
local function load()
  if art then return art end
  art = { cars = {}, cyclists = {} }
  for i = 1, 5 do local im = lg.newImage("art/scene/car" .. i .. ".png"); im:setFilter("nearest", "nearest"); art.cars[i] = im end
  for i = 1, 2 do local im = lg.newImage("art/scene/cyclist" .. i .. ".png"); im:setFilter("nearest", "nearest"); art.cyclists[i] = im end
  return art
end
Rd.art = load

function Rd.new(world)
  load()
  local r = setmetatable({ list = {}, t = 2.0, rng = love.math.newRandomGenerator(11), spans = {} }, Rd)
  -- road spans: runs of columns whose terrain top is the promenade (y 184)
  local s = nil
  for x = 0, world.width - 1, 4 do
    local flat = false
    for _, b in ipairs(world.rects) do if b.terrain and b.y0 == 184 and x >= b.x0 and x < b.x1 then flat = true; break end end
    if flat and not s then s = x elseif not flat and s then r.spans[#r.spans + 1] = { s, x }; s = nil end
  end
  if s then r.spans[#r.spans + 1] = { s, world.width } end
  return r
end

local function spanAt(self, x) for _, sp in ipairs(self.spans) do if x >= sp[1] and x < sp[2] then return sp end end end

function Rd:update(dt, cam)
  for i = #self.list, 1, -1 do
    local v = self.list[i]
    v.x = v.x + v.vx * dt
    if (v.vx > 0 and v.x > v.sp[2] + 10) or (v.vx < 0 and v.x + v.w < v.sp[1] - 10) or v.x > cam + 700 or v.x + v.w < cam - 380 then
      table.remove(self.list, i)
    end
  end
  self.t = self.t - dt
  if self.t > 0 or #self.list >= 2 then return end
  self.t = 3 + self.rng:random() * 6
  local mid = cam + 160
  local sp = spanAt(self, mid)
  if not sp then return end
  local rng = self.rng
  if rng:random() < 0.7 then                                        -- a car, from the left
    local im = art.cars[rng:random(1, #art.cars)]
    local w = im:getWidth()
    local x = cam - w - 20
    if x < sp[1] - w then x = sp[1] - w end
    self.list[#self.list + 1] = { im = im, x = x, w = w, vx = 110 + rng:random() * 60, base = 239, flip = true, sp = sp, bob = 0 }
  else                                                              -- a cyclist, either way
    local im = art.cyclists[rng:random(1, #art.cyclists)]
    local w = im:getWidth()
    local right = rng:random() < 0.5
    local x = right and (cam - w - 10) or (cam + 330)
    self.list[#self.list + 1] = { im = im, x = x, w = w, vx = (right and 1 or -1) * (45 + rng:random() * 25), base = 236, flip = not right, sp = sp, bob = 1 }   -- cyclist art faces right
  end
end

function Rd:draw(cam, t)
  if #self.list == 0 then return end
  lg.setColor(1, 1, 1, 1)
  for _, v in ipairs(self.list) do
    local a, b = math.max(v.sp[1], cam) - cam, math.min(v.sp[2], cam + 320) - cam
    if b > a then
      lg.setScissor(a, 0, b - a, 240)                                 -- clip to its stretch of road
      local h = v.im:getHeight()
      local y = v.base - h
      local x = math.floor(v.x - cam + 0.5)
      if v.flip then lg.draw(v.im, x + v.w, y, 0, -1, 1) else lg.draw(v.im, x, y) end
      lg.setScissor()
    end
  end
end

return Rd
