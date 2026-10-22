-- Passing traffic on the road in front of the promenade: cars and cyclists in the near lane (the road band is
-- y 199-240 under the promenade). Pure scenery: nothing here touches Pepper. Vehicles appear only where there is
-- road (flat promenade at y 184) and are clipped to it, so none drives over the river or the quay.
-- The near lane is closer to the camera than the promenade, so its traffic is drawn bigger than things on it
-- (Mia is about 60 px tall, about 44 px a metre): cars about 190-235 x 70-92 px, cyclists about 95 px tall.
-- Their tops are at y 192 / 190, below Pepper's feet (y 184), so they never cover her; the frame crops their
-- lower part (the wheels), as the near lane would be.
--   cars drive to the right (Swedish right-hand traffic, near lane) or to the left (the far lane; r5/bugs, so that
--   traffic still passes while Pepper runs right), 300-380 px/s (art: road_car1-5, facing left)
--   cyclists use the bike lane next to the kerb in either direction, 190-240 px/s (art: road_cyclist1-2, facing right)
-- A vehicle is always seen whole (r5/bugs): it comes in at a screen edge and leaves at a screen edge, never at the
-- end of its stretch of road. One is only sent when its stretch reaches far enough past the screen for it to cross
-- at the camera's present speed; if Pepper then runs after it so that the stretch's end would come into view while
-- it is still on screen, it speeds up (or drops behind); it is removed only once it is wholly off screen. (Before,
-- the end of the road sliced cars in half where the promenade turns into the quay steps, a car could pop out of the
-- start of a stretch on screen, and one was removed on screen when it passed the end.)
-- The promenade bikes (stage.lua) use the same road_cyclist art since r5/bugs (the small cyclist1.png was a
-- child's bike next to Pepper).
local Sc = require("scene")
local Look = require("look")
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

-- where a vehicle is on screen: it slides with its road row (look.lua's row scrolling: f > 1 for the near rows),
-- counting only the camera's movement since it was sent, so it still comes in from the screen's edge
local function screenX(v, cam) return v.x - cam - (v.f - 1) * (cam - v.cam0) end
-- how far past the screen edge its stretch of road must reach when it is sent, with the camera moving at c the
-- way it goes (negative: the other way): it needs (320 + w) / (speed - f * c) seconds to cross while its front gains (speed - (f - 1) * c)
-- a second on its row
local function reach(speed, w, f, c)
  local s = speed - f * c
  if s <= 0 then return math.huge end
  return (speed - (f - 1) * c) * (320 + w) / s
end
-- the end of its stretch must not come into view while it is on screen: with the camera running towards that end
-- at c (px/s), the end shows in gap / c s. If it would not be gone by then, it changes speed: it leaves ahead (it
-- speeds up) or falls behind (it slows down, never below 40 % of its speed), whichever is the smaller change.
local function keepWhole(v, x, cam, c)
  local dir = v.vx > 0 and 1 or -1
  local gap = dir > 0 and (v.sp[2] - cam - 320) or (-(v.sp[1] - cam))          -- the end, beyond the edge it heads for
  local cc = c * dir                                                          -- the camera's speed towards that end
  if cc <= 1 or gap > 2000 then return end
  local T = math.max(0.05, (gap - 8) / cc)                                    -- (8 px to spare)
  local sAhead = (dir > 0 and (320 - x) or (x + v.w)) / T                     -- screen speed to leave ahead in time
  local sBack = (dir > 0 and (x + v.w) or (320 - x)) / T                      -- or to fall behind it
  local sp = math.abs(v.vx)
  local now = sp - v.f * cc                                                  -- its screen speed the way it goes
  if now >= sAhead * 1.1 or now <= -sBack * 1.1 then return end               -- it will be gone in time
  local ahead, back = sAhead * 1.1 + v.f * cc, -sBack * 1.1 + v.f * cc       -- the speeds that do it
  if back >= v.base * 0.4 and (sp - back) < (ahead - sp) then sp = back else sp = math.min(ahead, 1400) end
  v.vx = dir * sp
end

function Rd:update(dt, cam)
  local c = self.lastCam and (cam - self.lastCam) / math.max(dt, 1e-3) or 0  -- the camera's speed
  if math.abs(c) * dt > 40 then self.list = {}; c = 0 end                    -- a cut (a respawn): a new view
  self.lastCam = cam
  for i = #self.list, 1, -1 do
    local v = self.list[i]
    v.x = v.x + v.vx * dt
    local x = screenX(v, cam)
    if x > 330 or x + v.w < -10 then table.remove(self.list, i)                -- wholly off screen
    else
      keepWhole(v, x, cam, c)
      if Look.CHECK and x < 320 and x + v.w > 0 then                           -- LOOK_CHECK=1: it never meets a road end
        local a, b = v.sp[1] - cam, v.sp[2] - cam
        if (a > 0 and x < a) or (b < 320 and x + v.w > b) then print(("ROAD CUT vehicle at screen x %.0f, road %d-%d"):format(x, v.sp[1], v.sp[2])); io.stdout:flush() end
      end
    end
  end
  self.t = self.t - dt
  if self.t > 0 or #self.list >= 2 then return end
  self.t = 0.4                                                      -- (no room for one now: try again soon)
  local sp = spanAt(self, cam + 160)
  if not sp then return end
  local rng = self.rng
  local function rowF(top, im) return Look.on and Look.rowFactor(top + im:getHeight() * 0.6) or 1 end
  if rng:random() < 0.7 then                                        -- a car: to the right in the near lane, or to the left
    local im = art.cars[rng:random(1, #art.cars)]
    local w, vx = im:getWidth(), 300 + rng:random() * 80
    local f = rowF(Rd.CAR_TOP, im)
    local okR = sp[1] <= cam - w - 30 and sp[2] >= cam + 320 + reach(vx, w, f, c)
    local okL = sp[2] >= cam + 320 + w + 30 and sp[1] <= cam - reach(vx, w, f, -c)
    if not okR and not okL then return end
    local right = okR and (not okL or rng:random() < 0.5)
    self.t = 3 + rng:random() * 6
    self.list[#self.list + 1] = { im = im, x = right and (cam - w - 4) or (cam + 324), w = w, vx = right and vx or -vx, base = vx,
      top = Rd.CAR_TOP, flip = right, sp = sp, bob = 0, f = f, cam0 = cam }      -- (car art faces left)
  else                                                              -- a cyclist, either way
    local im = art.riders[rng:random(1, #art.riders)]
    local w, right = im:getWidth(), rng:random() < 0.5
    local vx = 190 + rng:random() * 50
    local f = rowF(Rd.RIDER_TOP, im)
    if right and (sp[1] > cam - w - 30 or sp[2] < cam + 320 + reach(vx, w, f, c)) then return end
    if not right and (sp[2] < cam + 320 + w + 30 or sp[1] > cam - reach(vx, w, f, -c)) then return end
    self.t = 3 + rng:random() * 6
    self.list[#self.list + 1] = { im = im, x = right and (cam - w - 4) or (cam + 324), w = w, vx = right and vx or -vx, base = vx,
      top = Rd.RIDER_TOP, flip = not right, sp = sp, bob = 1, f = f, cam0 = cam }  -- cyclist art faces right
  end
end

-- (rowFactor: look.lua's, when the look is on; each vehicle keeps the factor of its row from when it was sent)
function Rd:draw(cam, t, rowFactor)
  if #self.list == 0 then return end
  lg.setColor(1, 1, 1, 1)
  for _, v in ipairs(self.list) do
    local a, b = math.max(v.sp[1], cam) - cam, math.min(v.sp[2], cam + 320) - cam
    if b > a then
      lg.setScissor(a, 0, b - a, 240)                                 -- (a safety net: it never meets a road end on screen)
      local y = v.top
      local x = math.floor(screenX(v, cam) + 0.5)
      if v.bob == 1 then Rd.drawBike(v.im, v.vx > 0 and v.x or -v.x, x, y, v.flip)   -- a cyclist: wheels roll
      elseif v.flip then lg.draw(v.im, x + v.w, y, 0, -1, 1) else lg.draw(v.im, x, y) end
      lg.setScissor()
    end
  end
end

return Rd
