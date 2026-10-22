-- The vertical camera for tall levels (a map with more than 30 rows: the world is rows x 8 px high).
-- s.cam stays the camera's x (left edge); s.camY is the world y at the top of the screen. In a world 240 px high
-- s.camY is always 0, so the five flat levels play and draw exactly as before.
--
--   Standing      "platform snap": the camera settles (eased, at most SPEED px/s) so the floor she stands on sits
--                 at screen y FLOOR. A hop and a landing on the same floor move nothing.
--   In the air    a dead zone: her feet may go from screen y TOP to BOTTOM before the camera follows, so jumps
--                 do not bob the screen. Falling well below the floor she left (FALL_LEAD px), the camera leads
--                 down: her feet go towards screen y FALL_AT, so she sees where she will land.
--   Looking       Up held while she stands still looks up, Down held while she is crouched (or sits) and still
--                 looks down: LOOK px, after LOOK_DELAY s (as Simba did). What Up and Down do to Pepper is unchanged.
--   Clamped       to the world: 0 .. world height - 240.
local I = require("input")
local Vc = {}
Vc.FLOOR = 168        -- screen y of the floor she stands on (the flat levels' walking line is 184)
Vc.TOP = 64           -- in the air: her feet may rise to this screen y before the camera follows
Vc.BOTTOM = 204       -- and sink to this one
Vc.FALL_AT = 120      -- falling: the camera leads down until her feet are about here
Vc.FALL_LEAD = 24     -- a fall counts once her feet are this far below the floor she left (a hop never does)
Vc.LOOK = 64          -- looking up / down moves the view this far
Vc.LOOK_DELAY = 0.5   -- after holding Up / Down still this long
Vc.LOOK_SPEED = 160   -- px/s the view slides when looking
Vc.SPEED = 300        -- px/s at most while settling on a floor
Vc.SKY, Vc.FAR, Vc.MID = 0.1, 0.3, 0.6   -- the parallax layers' vertical scroll factors

local function clamp(s, y) return math.max(0, math.min(s.camYMax, y)) end
local function approach(v, target, rate) if v < target then return math.min(target, v + rate) else return math.max(target, v - rate) end end

function Vc.init(s)
  s.camYMax = math.max(0, s.world.height - 240)
  Vc.snap(s)
end

-- straight to Pepper, no easing (the start, a respawn, a test moving her)
function Vc.snap(s)
  s.lookY, s.lookT, s.lookDir = 0, 0, 0
  s.floorY = s.pepper.y
  s.camY = clamp(s, s.pepper.y - Vc.FLOOR)
end

function Vc.update(s, dt)
  if s.camYMax <= 0 then s.camY = 0; return end
  local p = s.pepper
  -- looking up / down
  local still = p.onGround and math.abs(p.vx) < 5 and p.mode == "normal"
  local dir = 0
  if still and not p.crouch and I.down("up") and not I.down("down") then dir = -1
  elseif still and p.crouch and I.down("down") then dir = 1 end
  if dir ~= 0 and dir == s.lookDir then s.lookT = s.lookT + dt else s.lookT = 0 end
  s.lookDir = dir
  local want = (dir ~= 0 and s.lookT >= Vc.LOOK_DELAY) and dir * Vc.LOOK or 0
  s.lookY = approach(s.lookY, want, Vc.LOOK_SPEED * dt)
  -- following
  local y = s.camY
  if p.mode == "gone" or p.mode == "drown" then
    -- (out of the world or in the water: the camera stays where it is until she is back)
  elseif p.onGround then
    s.floorY = p.y
    local d = (p.y - Vc.FLOOR + s.lookY) - y
    y = y + math.max(-Vc.SPEED * dt, math.min(Vc.SPEED * dt, d * math.min(1, dt * 6)))
    local sy = p.y - y                                               -- never let her leave the screen
    if sy < 40 then y = p.y - 40 elseif sy > 236 then y = p.y - 236 end
  else
    if p.vy > 0 and p.y > s.floorY + Vc.FALL_LEAD then                -- falling: lead down
      local target = p.y - Vc.FALL_AT
      if target > y then y = y + (target - y) * math.min(1, dt * 8) end
    end
    local sy = p.y - y
    if sy < Vc.TOP then y = p.y - Vc.TOP elseif sy > Vc.BOTTOM then y = p.y - Vc.BOTTOM end
  end
  s.camY = clamp(s, y)
end

-- the parallax layers' vertical offsets on screen for camera y cy: 0 at the bottom of the world (where the flat
-- levels' far layers belong), moving down slower than the world as the camera rises, so climbing rises over the city
function Vc.parallax(s, cy)
  if (s.camYMax or 0) <= 0 then return nil end                     -- a flat level: nothing moves
  local rel = s.camYMax - cy
  return { sky = math.floor(rel * Vc.SKY + 0.5), far = math.floor(rel * Vc.FAR + 0.5), mid = math.floor(rel * Vc.MID + 0.5), world = -cy }
end

return Vc
