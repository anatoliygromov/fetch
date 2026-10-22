-- The chase (Level 4, Söder Hill): L.scroll. Lion King's Stampede, our way: the screen moves on by itself and the
-- ball rolls ahead of Pepper down the hill. stage.lua calls Ch.init, Ch.update (after its camera), Ch.drawBack
-- (the open cellar hatches, behind the play layer) and Ch.draw (the barrels) when the level has L.scroll.
--
--   The scroll   the camera's left edge (c.x) moves right at the speed of the section Pepper's screen is in
--                (L.scroll.speeds: { x, px/s }, from that x on). The camera rides with it, at most LEAD px ahead;
--                while the ball rolls Pepper can't run past AHEAD px into the screen, so the chase sets the pace,
--                as in Lion King's Stampede. It stops at the level's end.
--   The edge     Pepper can't stay left of the screen: the edge pushes her along. If an obstacle is in the way
--                (she didn't jump it or crawl under it), she is pinned: a heart, and back to the last lamp.
--   Hatches      open cellar hatches are gaps in the street (soder.map): falling in costs a heart, back to the lamp.
--   The ball     rolls downhill ahead of her, always on screen (200 to 312 px from the left edge) and
--                always ahead of her nose, hops
--                up onto whatever stands in the street and rolls across the hatches (it is quick); at the bottom
--                it stops against the quay railing (L.scroll.ballStop) and lies there to be picked up.
--   Barrels      the ball knocks a barrel off a stack (L.barrels: when the ball passes trigger); it rolls down the
--                street slower than the chase, so Pepper catches up with it: hop over it. Touching it costs a heart
--                (a knock-back; carrying the ball, the ball is knocked out instead: St:hazardHit). A barrel that
--                drops into a hatch is gone.
-- A respawn (or a test moving the camera) restarts the scroll from the new camera, puts the ball back on screen
-- and stacks the barrels again that are still ahead.
local Pp = require("pepper")
local S = require("sfx")
local Sc = require("scene")
local lg = love.graphics
local Ch = {}
local HW, STEP = Pp.HW, 4
local BALL_G = 520
local LEAD = 24          -- how far the camera may run ahead of the scroll when Pepper runs ahead
local AHEAD = 240        -- while the ball rolls, Pepper can't run (on the ground) further into the screen than this:
                         -- the chase sets the pace, as in Stampede. A jump still flies at her full speed (up to EDGE_R),
                         -- and when she lands past AHEAD she drifts back to it.
local EDGE_R = 320 - HW - 2
local BARREL_HIT = 5     -- a barrel hurts only on a real touch: its middle 10 px against Pepper's body without her paws

-- the speed of the scroll at camera x
local function speedAt(sc, x)
  local v = sc.speeds[1][2]
  for _, s in ipairs(sc.speeds) do if x >= s[1] then v = s[2] end end
  return v
end

-- the top of what stands under x (props reaching down to the street, terrain, the stairs), from y - reach down;
-- things hanging higher up (signs, awnings) are ignored: the ball rolls under them
local function surfaceAt(w, x, y, reach)
  local best
  local sy = w:slopeFloor(x)
  if sy and sy >= y - reach then best = sy end
  for _, r in ipairs(w.rects) do
    if r.kind == "solid" and x >= r.x0 and x < r.x1 and r.y0 >= y - reach and (r.terrain or r.y1 >= y - 2) and not (sy and r.terrain) then
      if not best or r.y0 < best then best = r.y0 end
    end
  end
  return best
end

local function resetBarrels(c, fromX)
  for _, br in ipairs(c.barrels) do
    if br.def.x > fromX then br.state, br.x, br.y, br.vx, br.vy = "stack", br.def.x, br.def.y, 0, 0 end
  end
end

-- start the chase again from the camera where it is now (after a respawn, or a test moving the camera): the ball
-- back on screen ahead of Pepper, the barrels still ahead back on their stacks
function Ch.resync(s)
  local c, b, w = s.chase, s.ball, s.world
  c.x, c.lastCam = s.cam, s.cam
  resetBarrels(c, s.cam + 40)
  if b.state == "roll" then b.x = math.min(c.sc.ballStop, s.cam + 220); b.vy = 0; b.y = surfaceAt(w, b.x, 240, 240) or b.y; b.lastF = b.y end
end

function Ch.init(s, def)
  local sc = def.scroll
  s.chase = { x = 0, lastCam = 0, edgeT = 4, prevX = 0, sc = sc, barrels = {} }
  for i, b in ipairs(def.barrels or {}) do s.chase.barrels[i] = { def = b, state = "stack", x = b.x, y = b.y, vx = 0, vy = 0 } end
  local b = s.ball
  b.state, b.vy, b.x, b.y = "roll", 0, def.ball.x, def.ball.y
  local respawn = s.respawn                                        -- every respawn starts the chase again from there
  s.respawn = function(self) respawn(self); Ch.resync(self) end
end

-- before the stage's update: the camera moved from outside (a test, the QA) since the last frame: start from there
function Ch.pre(s)
  local c = s.chase
  if c and math.abs(s.cam - c.lastCam) > 40 then Ch.resync(s) end
  if c then c.prevX = s.pepper.x end                               -- where she was before this frame's step
end

-- lose a heart for the chase (pinned, a hatch) and go back to the last lamp
local function kill(s, msg)
  s:loseHeart()
  if s.events.over or s.deadT then return end
  s:respawn(); s:say(msg, 1.8)
end

-- a body of half width hw standing at x, feet y, height h: is it inside a solid? (terrain beside the stairs is not)
local function blocked(w, x, y, h)
  local r = w:solidIn(x - HW + 1, x + HW - 1, y - h + 1, y - STEP - 0.5)
  if r and r.terrain and w:slopeNear(x - HW, x + HW) then return nil end
  return r
end

-- roll a round thing (the ball, a barrel) along the street: it falls with gravity and hops up onto steps in its
-- way. bridge = true: it rolls across gaps (the quick ball); else it drops into them.
local function roll(w, o, nx, dt, bridge)
  local f = surfaceAt(w, nx, o.y, 40)
  if f then o.lastF = f elseif bridge then f = o.lastF end         -- the quick ball skims across a hatch at street height
  if o.vy == 0 and f and f < o.y - 0.5 then                         -- a step up in the way: a little hop onto it
    o.vy = -math.sqrt(2 * BALL_G * (o.y - f + 6))
  end
  o.x = nx
  if o.vy ~= 0 or not f or f > o.y + 0.5 then                       -- in the air (or the street drops away)
    o.vy = math.min(o.vy + BALL_G * dt, 400)
    local ny = o.y + o.vy * dt
    local g = surfaceAt(w, o.x, o.y, 2) or (bridge and o.lastF)
    if o.vy > 0 and g and ny >= g then o.y = g; o.vy = 0 else o.y = ny end
  else
    o.y = f
  end
end

function Ch.update(s, dt)
  local c = s.chase
  if not c then return end
  local p, w, b, sc = s.pepper, s.world, s.ball, c.sc
  local maxCam = w.width - 320
  local busy = s.deadT or s.drownT or c.pitT or s.clearT or s.events.clear or c.hold   -- (hold: tests pause the scroll)
  if not busy then c.x = math.min(maxCam, c.x + speedAt(sc, c.x) * dt) end
  s.cam = math.max(c.x, math.min(s.cam, c.x + LEAD))              -- the camera rides with the scroll (a little ahead at most)
  c.lastCam = s.cam

  -- a fall into an open hatch
  if c.pitT then
    c.pitT = c.pitT - dt
    if c.pitT <= 0 then c.pitT = nil; p.mode = "normal"; kill(s, "OOPS! AN OPEN HATCH") end
  elseif p.mode ~= "gone" and p.mode ~= "drown" and p.y > w.height - 4 and not s.deadT then
    p.mode, p.vy, p.vx = "gone", 0, 0; c.pitT = 0.6; S.play("splash")
  end

  -- the left edge of the screen pushes Pepper along; pinned against an obstacle, she loses a heart
  if not busy and not c.pitT and (p.mode == "normal" or p.mode == "hurt") then
    local edge = s.cam + HW
    if p.x < edge then
      if blocked(w, edge, p.y, p:height()) then kill(s, "OUCH! JUMP OR CRAWL, PEPPER!")
      else p.x = edge; if p.vx < 0 then p.vx = 0 end end
    end
    if b.state == "roll" and p.x > s.cam + AHEAD then
      local v = speedAt(sc, c.x)
      if p.onGround then p.x = math.min(p.x, math.max(s.cam + AHEAD, c.prevX + v * 0.5 * dt)) end
      p.x = math.min(p.x, s.cam + EDGE_R)
    end
    c.edgeT = math.max(0, c.edgeT - dt)
    if p.x - s.cam < 56 and c.edgeT == 0 and not s.msg then s:say("KEEP UP, PEPPER!", 1.4); c.edgeT = 6 end
  end

  -- the ball rolls ahead, on screen, until it stops against the railing at the bottom
  if b.state == "roll" then
    local v = speedAt(sc, c.x) + 24
    local nx = math.min(sc.ballStop, math.max(b.x + v * dt, s.cam + 200, p.x + 34), s.cam + 312)
    roll(w, b, nx, dt, true)
    if b.x >= sc.ballStop - 0.5 and b.vy == 0 then
      b.state = "rest"; b.home = { x = b.x, y = b.y }; b.on = nil; S.play("land")
    end
  end

  -- barrels: knocked off their stack by the ball, they roll down the street
  for _, br in ipairs(c.barrels) do
    if br.state == "stack" and b.state == "roll" and b.x >= br.def.trigger then
      br.state, br.vx, br.vy = "roll", br.def.speed or 45, -60; S.play("spring")
    elseif br.state == "roll" then
      roll(w, br, br.x + br.vx * dt, dt, false)
      if br.y > 250 or br.x < s.cam - 60 or br.x > w.width then br.state = "gone" end
      local x0, y0, x1, y1 = p:box()
      if br.state == "roll" and x1 - 6 > br.x - BARREL_HIT and x0 + 6 < br.x + BARREL_HIT and y1 > br.y - 12 and y0 < br.y and p:hurt(br.x, w) then s:hazardHit() end
    end
  end
end

-- behind the play layer: the open cellar hatches (dark holes in the street, the lid standing open beside them)
function Ch.drawBack(s, cam)
  local c = s.chase
  if not c then return end
  for _, h in ipairs(s.def.hatches or {}) do
    local x = h[1] - cam
    if x < 330 and x + (h[2] - h[1]) > -10 then
      local y = h[3]
      lg.setColor(0.13, 0.14, 0.17); lg.rectangle("fill", math.floor(x), y, h[2] - h[1], 240 - y)
      lg.setColor(Sc.C.groundEdge); lg.rectangle("fill", math.floor(x) - 2, y - 14, 2, 14)   -- the lid, open
      lg.setColor(Sc.C.prop); lg.rectangle("fill", math.floor(x) - 4, y - 13, 2, 13)
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- the barrels, stacked or rolling (14 x 14, wooden staves and two hoops)
local function barrel(x, y, rolling, t)
  x, y = math.floor(x + 0.5), math.floor(y + 0.5)
  Sc.outlined({ 0.55, 0.37, 0.22 }, { 0.18, 0.12, 0.08 }, x - 7, y - 14, 14, 14)
  lg.setColor(0.32, 0.30, 0.30)
  local k = rolling and math.floor(t * 10) % 2 or 0               -- the hoops turn as it rolls
  lg.rectangle("fill", x - 6, y - 11 + k, 12, 1); lg.rectangle("fill", x - 6, y - 5 - k, 12, 1)
  lg.setColor(1, 1, 1, 1)
end
function Ch.draw(s, cam)
  local c = s.chase
  if not c then return end
  for _, br in ipairs(c.barrels) do
    if br.state == "stack" then
      barrel(br.def.x - cam, br.def.y, false, 0)
      for _, o in ipairs(br.def.rest or {}) do barrel(o[1] - cam, o[2], false, 0) end   -- the rest of the stack stays
    elseif br.state == "roll" then
      barrel(br.x - cam, br.y, true, s.t)
      for _, o in ipairs(br.def.rest or {}) do barrel(o[1] - cam, o[2], false, 0) end
    else for _, o in ipairs(br.def.rest or {}) do barrel(o[1] - cam, o[2], false, 0) end end
  end
end

return Ch
