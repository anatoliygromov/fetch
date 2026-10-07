-- Passing traffic on the road in front of the promenade: cars and cyclists in the near lane (the road band is
-- y 199-240 under the promenade). Pure scenery: nothing here touches Pepper. Vehicles appear only where there is
-- road (flat promenade at y 184) and are clipped to it, so none drives over the river or the quay.
-- The near lane is closer to the camera than the promenade, so its traffic is drawn bigger than things on it
-- (Mia is about 60 px tall, about 44 px a metre): cars about 190-235 x 70-92 px, cyclists about 95 px tall.
-- Their tops are at y 192 / 190, below Pepper's feet (y 184), so they never cover her; the frame crops their
-- lower part (the wheels), as the near lane would be.
--   cars drive to the right (Swedish right-hand traffic, near lane), 110-170 px/s (art: road_car1-5, facing left)
--   cyclists use the bike lane next to the kerb in either direction, 45-70 px/s (art: road_cyclist1-2, facing right)
-- The promenade bikes (stage.lua) keep the small cyclist1.png: they ride on Pepper's line.
local Sc = require("scene")
local lg = love.graphics
local Rd = {}
Rd.__index = Rd

local art
local function load()
  if art then return art end
  art = { cars = {}, cyclists = {}, riders = {} }
  local function img(n) local im = lg.newImage("art/scene/" .. n .. ".png"); im:setFilter("nearest", "nearest"); return im end
  for i = 1, 5 do art.cars[i] = img("road_car" .. i) end
  for i = 1, 2 do art.cyclists[i] = img("cyclist" .. i) end       -- the promenade bikes (stage.lua)
  for i = 1, 2 do art.riders[i] = img("road_cyclist" .. i) end    -- the road's cyclists
  -- rolling wheels (tools/make_wheels.py): the same art in 4 frames, the spokes a quarter of a gap further each;
  -- px = how far the bike rolls per frame (wheel radius x spoke gap / 4)
  art.roll = {}
  local function roll(still, name, r, spokes)
    local im = img(name .. "_roll")
    local w, h = still:getWidth(), still:getHeight()
    local q = {}
    for f = 0, 3 do q[f] = lg.newQuad(f * w, 0, w, h, im:getWidth(), im:getHeight()) end
    art.roll[still] = { im = im, q = q, px = r * (2 * math.pi / spokes) / 4 }
  end
  for i = 1, 2 do roll(art.cyclists[i], "cyclist" .. i, 9.5, 8); roll(art.riders[i], "road_cyclist" .. i, 14.5, 12) end
  return art
end
-- draws a bike's art with its wheels turned for the distance it has ridden (dist grows whichever way it goes);
-- flip: mirrored (riding left). Other art is drawn as it is.
function Rd.drawBike(still, dist, x, y, flip)
  local r = load().roll[still]
  local sx, ox = flip and -1 or 1, flip and still:getWidth() or 0
  if not r then lg.draw(still, x + ox, y, 0, sx, 1); return end
  lg.draw(r.im, r.q[math.floor(dist / r.px) % 4], x + ox, y, 0, sx, 1)
end
Rd.art = load
Rd.CAR_TOP, Rd.RIDER_TOP = 192, 190                                -- below Pepper's feet (y 184)

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
    self.list[#self.list + 1] = { im = im, x = x, w = w, vx = 110 + rng:random() * 60, top = Rd.CAR_TOP, flip = true, sp = sp, bob = 0 }
  else                                                              -- a cyclist, either way
    local im = art.riders[rng:random(1, #art.riders)]
    local w = im:getWidth()
    local right = rng:random() < 0.5
    local x = right and (cam - w - 10) or (cam + 330)
    self.list[#self.list + 1] = { im = im, x = x, w = w, vx = (right and 1 or -1) * (45 + rng:random() * 25), top = Rd.RIDER_TOP, flip = not right, sp = sp, bob = 1 }   -- cyclist art faces right
  end
end

function Rd:draw(cam, t)
  if #self.list == 0 then return end
  lg.setColor(1, 1, 1, 1)
  for _, v in ipairs(self.list) do
    local a, b = math.max(v.sp[1], cam) - cam, math.min(v.sp[2], cam + 320) - cam
    if b > a then
      lg.setScissor(a, 0, b - a, 240)                                 -- clip to its stretch of road
      local y = v.top or (v.base - v.im:getHeight())
      local x = math.floor(v.x - cam + 0.5)
      if v.bob == 1 then Rd.drawBike(v.im, v.vx > 0 and v.x or -v.x, x, y, v.flip)   -- a cyclist: wheels roll
      elseif v.flip then lg.draw(v.im, x + v.w, y, 0, -1, 1) else lg.draw(v.im, x, y) end
      lg.setScissor()
    end
  end
end

return Rd
