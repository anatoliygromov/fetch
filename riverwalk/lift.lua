-- Movers on both axes (a goods lift on a building site, later a cable car or a sliding gantry): a platform that
-- goes to and fro along a straight line from (from, fromY) to (to, toY), resting `pause` s at each end.
-- A level gives one in L.movers with fromY (and toY) set; without fromY a mover is the old sideways kind
-- (stage.lua moves those exactly as before):
--   { name = "LIFT", x0 = 896, x1 = 944, y0 = 504, y1 = 512,     -- the platform's box at the start (y0 = its top)
--     from = 896, to = 896, fromY = 504, toY = 184,              -- its x0 and y0 at both ends
--     speed = 48, pause = 1.5,                                   -- px/s along the line; s at each end
--     winch = { x = 920, y = 120 } }                             -- (optional) the motor house and its operator
-- It is a one-way platform (jump up through it, Down + A drops off it). Nothing moves by itself: the motor is in
-- the winch house at the top and the operator in it runs the lift up and down all day (drawn with the lift).
-- It carries Pepper (and a ball resting on it) both ways. It never crushes her: if carrying her on would push her
-- into a solid (a ceiling, a wall), or the platform would come down (or slide) into her, it waits until it can go.
-- Over her it always leaves room for her standing (26 px) plus 2 px, even while she crouches (see Lf.CLEAR).
local lg = love.graphics
local Lf = {}

function Lf.new(m)
  local w, h = m.x1 - m.x0, m.y1 - m.y0
  return { name = m.name or "LIFT", x0 = m.from, x1 = m.from + w, y0 = m.fromY, y1 = m.fromY + h, w = w, h = h,
    from = m.from, to = m.to or m.from, fromY = m.fromY, toY = m.toY or m.fromY, speed = m.speed, pause = m.pause or 1,
    k = 0, dir = 1, dx = 0, dy = 0, kind = "oneway", waitT = m.pause or 1, winch = m.winch, lift = true }
end

-- Over Pepper it keeps the room she needs STANDING (H_STAND) plus CLEAR px, even while she crouches: when she lets
-- go of Down she stands up (pepper.lua's headroom test sees only solids, not movers), so a lift that waited at her
-- crouched height would be inside her. A lift already lower than that over her backs up until there is room.
Lf.CLEAR = 2

-- the space a platform must keep out of: her body, as tall as she is standing (plus CLEAR) when not riding it
local function room(p)
  local x0, top, x1, bot = p:box()
  return x0, math.min(top, bot - require("pepper").H_STAND - Lf.CLEAR), x1, bot
end

-- would this step (dx, dy) hurt Pepper? (she rides it into a solid, or it moves into her body)
function Lf.blocked(s, m, dx, dy)
  local p, w = s.pepper, s.world
  if p.mode == "gone" or p.mode == "drown" then return false end
  local x0, top, x1, bot = p:box()
  if p.onGround and p.ground == m then                              -- on it: her body where it takes her is clear
    return w:solidIn(x0 + dx + 1, x1 + dx - 1, top + dy, bot + dy - 1) ~= nil
  end
  x0, top, x1, bot = room(p)
  local nx0, nx1, ny0, ny1 = m.x0 + dx, m.x1 + dx, m.y0 + dy, m.y1 + dy
  if nx1 > x0 and nx0 < x1 and ny1 > top and ny0 < bot - 0.01 then  -- the platform would be inside her room
    return dy > 0 or dx ~= 0                                         -- (rising up under her it simply picks her up)
  end
  return false
end

-- the platform is in her standing room now (it came down while she was elsewhere and she crawled under it)
local function inRoom(s, m)
  local p = s.pepper
  if p.mode == "gone" or p.mode == "drown" or (p.onGround and p.ground == m) then return false end
  local x0, top, x1, bot = room(p)
  return m.x1 > x0 and m.x0 < x1 and m.y1 > top + 0.01 and m.y0 < bot - 0.01
end

function Lf.update(s, m, dt)
  m.dx, m.dy = 0, 0
  if m.waitT > 0 then m.waitT = m.waitT - dt; return end
  local len = math.max(1, math.sqrt((m.to - m.from) ^ 2 + (m.toY - m.fromY) ^ 2))
  local nk, arrive = m.k + m.dir * m.speed * dt / len, false
  if nk >= 1 then nk, arrive = 1, true elseif nk <= 0 then nk, arrive = 0, true end
  local nx, ny = m.from + (m.to - m.from) * nk, m.fromY + (m.toY - m.fromY) * nk
  local dx, dy = nx - m.x0, ny - m.y0
  if Lf.blocked(s, m, dx, dy) then                                  -- it waits (the operator sees her)
    m.blocked = true
    if inRoom(s, m) then                                             -- too low over her: the operator winds it back up
      local up = (m.toY < m.fromY) and 1 or -1                       -- (the way along the line that goes up)
      local bk = math.max(0, math.min(1, m.k + up * m.speed * dt / len))
      local bx, by = m.from + (m.to - m.from) * bk, m.fromY + (m.toY - m.fromY) * bk
      if by < m.y0 then
        m.dx, m.dy = bx - m.x0, by - m.y0; m.x0, m.x1, m.y0, m.y1, m.k = bx, bx + m.w, by, by + m.h, bk
        local b = s.ball; if b.state == "rest" and b.on == m then b.y = by end
      end
    end
    return
  end
  m.blocked = nil
  local p, b = s.pepper, s.ball
  local riding = p.onGround and p.ground == m and p.mode ~= "gone" and p.mode ~= "drown"
  m.x0, m.x1, m.y0, m.y1, m.k, m.dx, m.dy = nx, nx + m.w, ny, ny + m.h, nk, dx, dy
  if riding then p.y = ny end                                         -- up and down with it (sideways: pepper.lua adds dx)
  if b.state == "rest" and b.on == m then b.y = ny end                -- (and the ball's x: stage.lua adds dx)
  if arrive then m.dir = -m.dir; m.waitT = m.pause end
end

-- greybox: the cables from the winch, the winch house with its operator, the platform (outlined: Pepper stands on it)
function Lf.draw(m, cam, Sc, t)
  local C = Sc.C
  local x0, x1 = math.floor(m.x0 - cam + 0.5), math.floor(m.x1 - cam + 0.5)
  local y0 = math.floor(m.y0 + 0.5)
  if m.winch then
    local wx, wy = math.floor(m.winch.x - cam + 0.5), m.winch.y
    lg.setColor(0.25, 0.26, 0.30, 0.8)                                -- the cables (decoration: faded, no outline)
    lg.rectangle("fill", x0 + 4, wy + 14, 1, y0 - wy - 14); lg.rectangle("fill", x1 - 5, wy + 14, 1, y0 - wy - 14)
    Sc.box(C.back, wx - 22, wy - 16, 44, 30)                           -- the winch house
    lg.setColor(0.35, 0.33, 0.30); lg.rectangle("fill", wx - 22, wy - 19, 44, 3)
    local turning = math.abs(m.dy) + math.abs(m.dx) > 0
    lg.setColor(0.30, 0.30, 0.34); lg.circle("fill", wx + 9, wy + 4, 6)  -- the drum, turning while the lift moves
    lg.setColor(0.85, 0.80, 0.55)
    local a = turning and t * 6 or 0
    lg.rectangle("fill", math.floor(wx + 9 + math.cos(a) * 4), math.floor(wy + 4 + math.sin(a) * 4), 2, 2)
    lg.setColor(0.95, 0.65, 0.15); lg.rectangle("fill", wx - 15, wy - 9, 7, 3)   -- the operator: a hard hat,
    lg.setColor(0.85, 0.70, 0.55); lg.rectangle("fill", wx - 14, wy - 6, 5, 5)   -- a face,
    lg.setColor(0.20, 0.35, 0.60); lg.rectangle("fill", wx - 16, wy - 1, 9, 10)  -- overalls
    lg.setColor(0.85, 0.70, 0.55)                                                -- an arm on the lever
    if turning then lg.rectangle("fill", wx - 7, wy + 1, 6, 2) else lg.rectangle("fill", wx - 7, wy + 4, 5, 2) end
    Sc.label("LIFT", wx, wy + 16)
  end
  Sc.outlined(C.prop, C.propEdge, x0, y0, x1 - x0, m.y1 - m.y0)       -- the platform
  lg.setColor(C.propEdge)                                             -- its guard rails, low enough to step over
  lg.rectangle("fill", x0, y0 - 6, 1, 6); lg.rectangle("fill", x1 - 1, y0 - 6, 1, 6)
end

return Lf
