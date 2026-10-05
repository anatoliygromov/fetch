-- The collision world: terrain from the text map (8 x 8 px cells) plus prop boxes with exact pixel sizes,
-- plus moving platforms. y grows downwards; a "feet" position is the bottom edge of a box.
--   solid   blocks from every side
--   oneway  can be landed on from above only (jump up through it, Down + A drops through)
--   slope   a 45 degree floor inside one cell ('\' falls to the right, '/' rises to the right)
--   water   falling below its surface costs a heart
local Wd = {}
Wd.__index = Wd
local CELL = 8
local STEP = 4            -- a ledge this low is walked onto without a jump
local SLIP = 5            -- how far her body may hang over a box edge she slipped past (body 17 px, paws 13 px)

function Wd.load(mapPath, props)
  local w = setmetatable({ rects = {}, slopes = {}, water = {}, movers = {} }, Wd)
  local rows = {}
  for line in love.filesystem.lines(mapPath) do if #line > 0 then rows[#rows + 1] = line end end
  w.cols, w.rows = #rows[1], #rows
  w.width, w.height = w.cols * CELL, w.rows * CELL
  w.map = rows
  for r, line in ipairs(rows) do
    local y0 = (r - 1) * CELL
    local c = 1
    while c <= #line do
      local ch = line:sub(c, c)
      if ch == '#' or ch == '~' then                       -- merge runs into one box
        local c1 = c
        while c1 < #line and line:sub(c1 + 1, c1 + 1) == ch do c1 = c1 + 1 end
        local box = { x0 = (c - 1) * CELL, x1 = c1 * CELL, y0 = y0, y1 = y0 + CELL, kind = ch == '#' and "solid" or "water", terrain = true }
        if ch == '#' then w.rects[#w.rects + 1] = box else w.water[#w.water + 1] = box end
        c = c1 + 1
      else
        if ch == '\\' or ch == '/' then
          w.slopes[#w.slopes + 1] = { x0 = (c - 1) * CELL, x1 = c * CELL, y0 = y0, y1 = y0 + CELL, dir = ch == '/' and 1 or -1 }
        end
        c = c + 1
      end
    end
  end
  for _, p in ipairs(props or {}) do
    if p.kind == "solid" or p.kind == "oneway" then w.rects[#w.rects + 1] = p end
  end
  return w
end

function Wd:addMover(m) m.kind = m.kind or "oneway"; self.movers[#self.movers + 1] = m end

local function overlapX(r, a, b) return r.x1 > a and r.x0 < b end

-- floor height of a slope cell at x
local function slopeY(s, x)
  local t = math.max(0, math.min(1, (x - s.x0) / (s.x1 - s.x0)))
  if s.dir < 0 then return s.y0 + t * (s.y1 - s.y0) else return s.y1 - t * (s.y1 - s.y0) end
end

-- the highest floor whose top lies between yFrom and yTo (inclusive), under the feet span [a, b] and centre cx.
-- wasAbove: the feet were at or above y = wasAbove before this move (one-way surfaces need that).
-- Returns y, the surface (rect, slope or mover) or nil.
function Wd:slopeAt(x)
  for _, s in ipairs(self.slopes) do if x >= s.x0 and x < s.x1 then return s end end
  return nil
end
function Wd:slopeFloor(x) local s = self:slopeAt(x); if s then return slopeY(s, x), s end end
function Wd:slopeNear(a, b)
  for _, s in ipairs(self.slopes) do if s.x1 > a and s.x0 < b then return true end end
  return false
end

-- the highest floor whose top lies between yFrom and yTo (inclusive), under the feet span [a, b] and centre cx.
-- wasAbove: where the feet were before this move (one-way surfaces need the feet to start above them).
-- Over a slope only the slope (and props) count, so walking up and down steps is smooth.
-- Returns y and the surface (box, slope or moving platform), or nil.
function Wd:floor(a, b, cx, yFrom, yTo, wasAbove, ignoreOneway, tol)
  tol = tol or 0.01
  local best, hit = nil, nil
  local function try(y, what) if y >= yFrom and y <= yTo and (not best or y < best) then best, hit = y, what end end
  local sl = self:slopeAt(cx)
  if sl then try(slopeY(sl, cx), sl) end
  for _, r in ipairs(self.rects) do
    if overlapX(r, a, b) and not (sl and r.terrain) then
      if r.kind == "solid" then try(r.y0, r)
      elseif not ignoreOneway and wasAbove <= r.y0 + tol then try(r.y0, r) end
    end
  end
  for _, m in ipairs(self.movers) do
    if overlapX(m, a, b) and not ignoreOneway and wasAbove <= m.y0 + math.max(tol, 1.5) then try(m.y0, m) end
  end
  return best, hit
end

-- a solid box blocking a body box [a, b] x [top, bot] (bot = feet). Used for walls and ceilings.
function Wd:solidIn(a, b, top, bot)
  for _, r in ipairs(self.rects) do
    if r.kind == "solid" and r.x1 > a and r.x0 < b and r.y1 > top and r.y0 < bot then return r end
  end
  return nil
end

-- the wall a body would run into moving from x to nx (half width hw), feet y, height h.
-- Boxes whose top is within STEP of the feet are not walls (they are stepped onto).
function Wd:wall(x, nx, hw, y, h, onGround)
  local lift = onGround and STEP or 0
  local a, b = math.min(x, nx) - hw, math.max(x, nx) + hw
  local nearSlope = self:slopeNear(a, b)
  local hitR, hitX = nil, nil
  for _, r in ipairs(self.rects) do
    local l = (nearSlope and r.terrain) and (hw + 2) or lift
    if r.kind == "solid" and r.y0 < y - l - 0.01 and r.y1 > y - h + 0.01 and r.x1 > a and r.x0 < b then
      -- a box is a wall even when her body already overlaps its edge by up to SLIP px (she can slip past a box's
      -- corner with her body over it, since she stands on her narrower paws): it pushes her back out
      if nx > x and r.x0 >= x + hw - SLIP then
        local lim = r.x0 - hw
        if not hitX or lim < hitX then hitX, hitR = lim, r end
      elseif nx < x and r.x1 <= x - hw + SLIP then
        local lim = r.x1 + hw
        if not hitX or lim > hitX then hitX, hitR = lim, r end
      end
    end
  end
  return hitX, hitR
end

-- the ground under x, terrain only (pavement, quay, stairs; not the props): for the bikes
function Wd:groundAt(x)
  local sy = self:slopeFloor(x)
  if sy then return sy end
  local best
  for _, r in ipairs(self.rects) do if r.terrain and x >= r.x0 and x < r.x1 and r.y0 >= 150 and (not best or r.y0 < best) then best = r.y0 end end
  return best
end

function Wd:inWater(x, y)
  for _, r in ipairs(self.water) do
    if x >= r.x0 and x < r.x1 and y > r.y0 + 2 then return r end
  end
  return nil
end

Wd.CELL, Wd.STEP = CELL, STEP
return Wd
