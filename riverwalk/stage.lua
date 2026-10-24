-- One level being played: world, Pepper, the ball, the girl, bones, bikes, lamps, camera and rules.
local Wd = require("world")
local Pp = require("pepper")
local Sc = require("scene")
local Rd = require("road")
local Look = require("look")
local S = require("sfx")
local I = require("input")
local Ex = require("extras")                  -- visual extras around Pepper (drawing only, E toggles them)
local Sp = require("setpieces")               -- hard mode, rope ferries, traffic warnings, secrets, code-drawn pieces
local Cr = require("critters")                -- geese, gulls (L.critters) and springy tops (bounce = h on a prop)
local Ch = require("chase")                   -- Level 4: the scroll, the rolling ball, barrels, hatches (L.scroll)
local Nt = require("night")                   -- Level 5's night rules: darkness, sniffing, the fox, crumbling planks
local Vc = require("vcam")                    -- the vertical camera (tall levels; s.camY is 0 in a 240 px world)
local Lf = require("lift")                    -- movers on both axes (a goods lift): L.movers entries with fromY
local Rf = require("roofs")                   -- steam puffs (L.steam) and loose tiles (props with loose = true)
local AH = require("arthooks")                -- r8: the cargo bike, the tram lane, optional art of the first batch
local St = {}
St.__index = St
local lg = love.graphics
local function img(p) local i = lg.newImage(p); i:setFilter("nearest", "nearest"); return i end
local girlImg, ballImg, girlQ
local GF = require("girl_frames")             -- the girl's SpriteCook animations: idle, wave, cheer, call
local GIRL_ROW, GIRL_FPS = {}, { idle = 6, wave = 9, cheer = 9, call = 8, pet = 7 }
local POP_T = 1.2                                                -- a lamp's heart rises and fades this long
local HEART = { ".kk.kk.", "krrkrrk", "krwrrrk", "krrrrrk", ".krrrk.", "..krk..", "...k..." }   -- 7 x 7, drawn 2x
local HCOL = { k = { 0.13, 0.08, 0.10 }, r = { 0.90, 0.20, 0.25 }, w = { 1, 0.85, 0.85 } }
for i, r in ipairs(GF.rows) do GIRL_ROW[r.name] = i end

-- def: the level (level/*.lua). carry (optional): { score, lives } carried over from the level before.
function St.new(def, carry)
  if not girlImg then
    girlImg, ballImg, girlQ = img("art/girl.png"), img("art/ball.png"), {}
    for r, rw in ipairs(GF.rows) do
      girlQ[r] = {}
      for c = 1, rw.n do girlQ[r][c] = lg.newQuad((c - 1) * GF.CW, (r - 1) * GF.CH, GF.CW, GF.CH, girlImg:getDimensions()) end
    end
  end
  local s = setmetatable({ def = def, t = 0, cam = 0, lead = 0, score = carry and carry.score or 0, hearts = 3,
    lives = carry and carry.lives or 3, time = def.time, startScore = carry and carry.score or 0,
    rings = {}, msg = nil, events = {}, bikeT = 2.5, bikes = {} }, St)
  s.world = Wd.load(def.map, def.props)
  if def.scenery ~= "greybox" then s.road = Rd.new(s.world) end    -- the greybox park has no road and no traffic
  s.trams = AH.newTrams(def)                                       -- the back lane's vintage trams (scenery, L.trams)
  s.movers = {}
  for _, m in ipairs(def.movers) do
    local mv = m.fromY and Lf.new(m) or { name = m.name, x0 = m.from, x1 = m.from + (m.x1 - m.x0), y0 = m.y0, y1 = m.y1, from = m.from, to = m.to, speed = m.speed, dir = 1, dx = 0, kind = "oneway", pause = m.pause }
    s.world:addMover(mv); s.movers[#s.movers + 1] = mv
  end
  Look.level(def)                                                  -- (the colour script first: the art is faded to its haze)
  s.layers = def.scenery == "greybox" and Sc.buildGrey(s.world.width, def.greyStyle) or Sc.build(s.world.width)
  if def.art then s.layers = Sc.buildArt(s.world.width, def.art) end   -- art for a greybox level (City Park, Downtown)
  s.pepper = Pp.new(def.start.x, def.start.y)
  s.check = { x = def.start.x, y = def.start.y }
  s.bones = {}
  for i, b in ipairs(def.bones) do s.bones[i] = { x = b.x, y = b.y, super = b.super, taken = false } end
  s.total = #s.bones
  s.taken = 0
  s.lamps = {}
  for i, l in ipairs(def.lamps) do s.lamps[i] = { x = l.x, y = l.y, checkpoint = l.checkpoint, lit = false } end
  s.ball = { x = def.ball.x, y = def.ball.y, home = { x = def.ball.x, y = def.ball.y }, state = "rest", vy = 0 }
  -- the girl: a level without her (L.girl) keeps one far off the map, hidden
  if def.girl then s.girl = { x = def.girl.x, y = def.girl.y, state = "idle", t = 0, callT = 0 }
  else s.girl = { x = -9999, y = -9999, state = "idle", t = 0, callT = 0, hidden = true } end
  -- the magpie (City Park): it has the ball in its beak (see St:updateMagpie)
  if def.magpie then s:resetMagpie(1) end
  -- the cat (Downtown): it sits on the ball until a bark scares it off; then the ball drops
  if def.cat then s.cat = { x = def.cat.x, y = def.cat.y, state = "sit", t = 0, vx = 0, vy = 0, dir = 1 }; s.ball.state = "cat" end
  s.kicked = {}                                                   -- leaf piles Pepper has run through
  s.pops = {}                                                     -- hearts popping out of a lamp (St:update, the lamps)
  s.cam = 0
  Vc.init(s)                                                      -- s.camY, the vertical camera (vcam.lua)
  s.fx = Ex.new()
  Sp.init(s, def, carry)                                          -- hard mode (carry.hard), rope ferries, secrets
  Cr.init(s, def)                                                 -- geese and gulls
  Rf.init(s, def)                                                 -- steam puffs, loose tiles (roofs.lua)
  if def.scroll then Ch.init(s, def) end                          -- the chase (Level 4)
  if def.dark or def.fox then s.night = Nt.new(s, def) end         -- [night hook] Level 5 (night.lua)
  return s
end

-- a message: a string is the girl's line; a table { btn, text } is Pepper's control hint (see St:hint)
function St:say(text, t)
  local l = type(text) == "table" and { who = "pepper", btn = text.btn, text = text.text, teach = text.btn ~= nil, msg = true }
    or { who = "girl", text = text, msg = true }
  self.msg = { text = l.text, t = t or 2.2, line = l }
end

-- the magpie (City Park) has the girl's ball in its beak. It sits on a perch, and flies on to the next perch
-- when Pepper comes near: from far off if she runs (def.magpie.flee px), only close up if she walks (fleeWalk).
-- A bark within its range (bark px) startles it: it drops the ball and flies away. So: sneak up, then bark.
-- On its last perch it stays put.
function St:resetMagpie(i)
  local d, b = self.def.magpie, self.ball
  local pr = d.perches[i]
  self.magpie = { i = i, x = pr.x, y = pr.y, state = "perch", t = 0, dir = -1 }
  b.state, b.drop = "magpie", nil
  b.x, b.y = self:beak()
end
function St:beak() local m = self.magpie; return m.x + m.dir * 11, m.y - (m.state == "fly" and 5 or 8) end   -- the ball's bottom, at the beak
function St:updateMagpie(dt)
  local m, d, p, b = self.magpie, self.def.magpie, self.pepper, self.ball
  m.t = m.t + dt
  if m.state == "fly" then
    local f = m.fly
    local k = math.min(1, m.t / f.dur)
    m.x = f.x0 + (f.x1 - f.x0) * k
    m.y = f.y0 + (f.y1 - f.y0) * k - f.peak * 4 * k * (1 - k)
    if k >= 1 then m.state, m.t = f.after, 0; if f.after == "gone" then m.x = -999 end end
  elseif m.state == "perch" then
    m.dir = (p.x < m.x) and -1 or 1                                -- it keeps an eye on Pepper
    local dist = math.abs(p.x - m.x)
    local running = math.abs(p.vx) > Pp.P.walk + 5 and p.mode == "normal"
    if m.i < #d.perches and dist < (running and (d.perches[m.i].flee or d.flee) or d.fleeWalk) then
      local n = d.perches[m.i + 1]
      m.i = m.i + 1
      m.fly = { x0 = m.x, y0 = m.y, x1 = n.x, y1 = n.y, dur = math.max(0.6, math.abs(n.x - m.x) / 200), peak = 30, after = "perch" }
      m.state, m.t = "fly", 0; m.dir = n.x > m.x and 1 or -1
      S.play("flap"); m.heard = nil
      if not self.magpieSaid then self.magpieSaid = true; self:say({ btn = "b", text = "HOLD: SNEAK" }, 2.6) end
    end
  end
  if b.state == "magpie" then b.x, b.y = self:beak() end
end
function St:barkAtMagpie()
  local m, d, p, b = self.magpie, self.def.magpie, self.pepper, self.ball
  if m.state ~= "perch" or b.state ~= "magpie" then return end
  if math.abs(p.x - m.x) <= d.bark and math.abs(p.y - m.y) < 110 then
    b.state, b.vx, b.vy, b.airT = "air", 0, -20, 0                 -- it lets go: the ball falls
    b.home = self:homeNear(self.check.x, self.check.y)             -- if it falls in the pond: back by the last lamp
    m.fly = { x0 = m.x, y0 = m.y, x1 = m.x - 260, y1 = m.y - 140, dur = 1.2, peak = 10, after = "gone" }
    m.state, m.t = "fly", 0; m.dir = -1
    S.play("flap"); self:say(d.dropSay or "IT DROPPED THE BALL!", 2.2)
  else m.heard = self.t end
end

-- the level's exit (goal = "exit"): reaching it clears the level; with needBall only while carrying the ball
function St:checkExit()
  local e, p = self.def.exit, self.pepper
  if not e or self.clearT or self.events.clear then return end
  if p.x >= e.x and p.mode == "normal" and (not e.needBall or p.carrying) then
    if e.needBall then self.score = self.score + (e.bonus or 1000); self.bonus = { e.bonusName or "BALL", e.bonus or 1000 } end
    S.play("heart"); self:say(e.say or "GOOD GIRL, PEPPER!", 3)
    self.clearT = e.wait or 1.6
  end
end

function St:respawn()
  local p = self.pepper
  p.x, p.y, p.vx, p.vy = self.check.x, self.check.y, 0, 0
  p.mode, p.onGround, p.ground, p.crouch, p.invuln = "normal", true, nil, false, 1.0
  self.cam = math.max(0, math.min(self.world.width - 320, p.x - 140))
  Vc.snap(self)
end

function St:loseHeart()
  self.hearts = self.hearts - 1
  if self.hearts <= 0 then
    self.lives = self.lives - 1; self.hearts = self.maxHearts
    if self.lives <= 0 then self.events.over = true; return end
    self:say("OUCH! BACK TO THE LAMP POST", 2)
    self.deadT = 0.6
  end
end

local function nearBall(s) local p, b = s.pepper, s.ball
  return b.state == "rest" and math.abs(p.x + p.face * 18 - b.x) < 24 and math.abs(p.y - b.y) < 22
end
local function nearGirl(s) return math.abs(s.pepper.x - s.girl.x) < 44 and math.abs(s.pepper.y - s.girl.y) < 20 end

-- the ball leaves Pepper's mouth. It never starts inside a wall or outside the level: if her mouth is in a solid
-- box (she is pressed against it), it drops at her own x instead, and it never flies faster than a gentle toss.
function St:dropBall()
  local b, p, w = self.ball, self.pepper, self.world
  b.x, b.y = p:mouthPos(); b.state = "air"; b.vy = -40; b.vx = math.max(-40, math.min(40, p.vx * 0.5)); p.carrying = nil
  if w:solidIn(b.x - 3, b.x + 3, b.y - 6, b.y) then b.x, b.vx = p.x, 0 end
  b.x = math.max(14, math.min(w.width - 14, b.x)); b.airT = 0; b.on = nil
end
-- a spot by a lamp (or Pepper's checkpoint) where a ball can rest and be picked up: 24 px past it, 24 px before
-- it, or on it (the respawn spot itself, always clear), whichever is first free of solids and water
function St:homeNear(x, y)
  local w = self.world
  for _, dx in ipairs({ 24, -24, 0 }) do
    local bx = x + dx
    if bx >= 14 and bx <= w.width - 14 and not w:solidIn(bx - 3, bx + 3, y - 6, y - 1) and not w:inWater(bx, y - 2)
      and w:floor(bx - 2, bx + 2, bx, y - 2, y + 2, y - 4) then return { x = bx, y = y } end
  end
  return { x = x, y = y }
end
-- a hazard hit Pepper (a bike, cart or tram, a goose, a gull, a barrel: p:hurt has already knocked her back and
-- made her blink). The free first mistake (benchmark principle 6): while she carries the ball, the ball is knocked
-- out of her mouth and she keeps her hearts; without the ball the hit costs a heart. Hard mode keeps the old rule:
-- every hit costs a heart (dropsBall: this hazard knocked the ball out before, the goose and the gull). A hazard
-- added later calls this after p:hurt. Returns true when the hit cost a heart.
function St:hazardHit(dropsBall)
  local p = self.pepper
  if p.carrying and not self.hard then self:knockBall(); return false end
  self:loseHeart()
  if dropsBall and p.carrying then self:dropBall() end
  return true
end
-- the ball pops out of her mouth with the knock-back and comes down on the ground near her. Its fallback spot is
-- fixed now (b.knock): the ground under her when she was hit, never a boat or a lift (they move on), else by the
-- last lamp. If the ball would land in the water or somewhere she can't reach, it is put back there.
function St:knockBall()
  local b, p, w = self.ball, self.pepper, self.world
  local fy = w:floor(p.x - Pp.HW, p.x + Pp.HW, p.x, p.y - 0.5, w.height, p.y - 0.5)   -- (under her paws: she may
  b.knock = fy and self:spotNear(p.x, fy) or self:homeNear(self.check.x, self.check.y) -- stand on a box's very edge)
  self:dropBall()
  -- it flies along with her, a little behind; if that flight would end in the water or out of reach, it pops
  -- straight up instead (and if even that fails, it splashes and comes back at b.knock)
  local vx = math.max(-90, math.min(90, p.vx * 0.6))
  if w:solidIn(b.x - 3, b.x + 3, b.y - 6, b.y) or not self:ballLands(b.x, b.y, vx, -150) then vx = 0 end
  b.vx, b.vy = vx, -150
  self.ballKnocks = (self.ballKnocks or 0) + 1
  self:say(self.def.knockSay or "OOPS! GET THE BALL!", 1.8)
end
-- a spot near (x, y) where a ball can rest and be picked up: on a floor within 8 px of y (not a boat or a lift,
-- they move on), out of the water and clear of boxes, the nearest of x, x -+ 12, ... x -+ 48; nil if none
function St:spotNear(x, y)
  local w = self.world
  for _, dx in ipairs({ 0, -12, 12, -24, 24, -36, 36, -48, 48 }) do
    local bx = x + dx
    local f, on = w:floor(bx - 2, bx + 2, bx, y - 8, y + 8, y - 8)
    local moving = false
    for _, m in ipairs(self.movers) do if on == m then moving = true end end
    if f and not moving and bx >= 14 and bx <= w.width - 14 and not w:inWater(bx, f - 2)
      and not w:solidIn(bx - 3, bx + 3, f - 6, f - 1) then return { x = bx, y = f } end
  end
end
-- where a ball thrown from (x, y) at (vx, vy) comes down, with the air branch's rules (St:update): true if on a
-- floor, out of the water and not inside a box
function St:ballLands(x, y, vx, vy)
  local w, dt = self.world, 1 / 60
  for _ = 1, 150 do
    vy = math.min(vy + 520 * dt, 400)
    local ny = y + vy * dt
    local nx = math.max(14, math.min(w.width - 14, x + vx * dt))
    if w:solidIn(nx - 3, nx + 3, y - 6, y - 1) then vx = 0 else x = nx end
    local f = w:floor(x - 3, x + 3, x, y - 0.5, ny, y)
    if f then return not w:inWater(x, f) and not w:solidIn(x - 2, x + 2, f - 5, f - 1) and f < w.height - 4 end
    y = ny
    if w:inWater(x, y) or y > w.height then return false end
  end
  return false
end
-- a ball that came to rest where Pepper cannot get it (inside a solid box or terrain, or it fell out of the
-- level) goes back to its home spot (the level's ball home, or where the magpie / cat let it go), with a line
function St:ballLost()
  local b = self.ball
  return b.y > self.world.height - 4 or b.x < 4 or b.x > self.world.width - 4 or (b.state == "air" and (b.airT or 0) > 2.5)
    or (not self.world:slopeAt(b.x) and self.world:solidIn(b.x - 2, b.x + 2, b.y - 5, b.y - 1) ~= nil)
end

function St:giveBall()
  local b = self.ball
  b.state = "given"; self.pepper.carrying = nil; self.girl.state = "cheer"; self.girl.t = 0
  self.score = self.score + 2000; S.play("heart"); self:say("GOOD GIRL, PEPPER!", 3)
  self.bonus = { "FETCH", 2000 }
  self.clearT = 2.2
end

function St:update(dt, presses)
  self.t = self.t + dt
  if self.chase then Ch.pre(self) end                             -- the chase: the camera was moved from outside
  local p, w = self.pepper, self.world
  if self.msg then self.msg.t = self.msg.t - dt; if self.msg.t <= 0 then self.msg = nil end end
  if self.clearT then self.clearT = self.clearT - dt; if self.clearT <= 0 then self.events.clear = true; self.clearT = nil end end
  if not self.clearT and not self.events.clear then self.time = self.time - dt end
  if self.time <= 0 and not self.drownT and not self.deadT then
    self.time = self.def.time; self.lives = self.lives - 1; self.hearts = self.maxHearts
    if self.lives <= 0 then self.events.over = true else self:say("TIME UP!", 2); self:respawn() end
  end

  -- moving platforms
  for _, m in ipairs(self.movers) do
    if m.call then Sp.updateFerry(self, m, dt)                     -- a rope ferry: it comes when Pepper is near
    elseif m.lift then Lf.update(self, m, dt) else                 -- a lift (both axes; lift.lua)
    local nx = m.x0 + m.dir * m.speed * dt
    if (m.waitT or 0) > 0 then m.waitT = m.waitT - dt; nx = m.x0                -- pause = s: it rests at each end
    elseif nx > m.to then nx = m.to; m.dir = -1; m.waitT = m.pause
    elseif nx < m.from then nx = m.from; m.dir = 1; m.waitT = m.pause end
    m.dx = nx - m.x0; m.x1 = m.x1 + m.dx; m.x0 = nx
    end
  end

  -- Pepper
  if self.deadT then
    self.deadT = self.deadT - dt
    if self.deadT <= 0 then self.deadT = nil; self:respawn() end
  else
    local wasAir = not p.onGround
    if not (self.night and Nt.sniffing(self, dt)) then p:update(dt, w, presses) end   -- [night hook] sniffing
    Cr.bounce(self, wasAir, dt)                                    -- a springy top launches her
    Rf.update(self, dt)                                            -- a steam puff lifts her, a loose tile goes
    if p.mode == "drown" and not self.drownT then
      self.drownT = 1.0
      if p.carrying then p.carrying = nil; self.ball.state = "home"; self.ballBackT = 1.2 end
    end
  end
  -- a fall out of the bottom of the world (a pit in a tall level): as in the water, a heart and back to the lamp.
  -- (Soder Hill's hatches have their own rule in chase.lua.) Landing on a lower floor costs nothing.
  if not self.chase and not self.fallT and not self.deadT and not self.drownT and p.mode ~= "gone" and p.mode ~= "drown"
    and p.y > w.height + 24 then
    self.fallT = 0.5; p.mode, p.vx, p.vy = "gone", 0, 0; S.play("hurt")
    if p.carrying then p.carrying = nil; self.ball.state = "home"; self.ballBackT = 1.2 end
  end
  if self.fallT then
    self.fallT = self.fallT - dt
    if self.fallT <= 0 then
      self.fallT = nil; self:loseHeart()
      if not self.events.over then self:respawn(); if not self.deadT then self:say("OOPS! LOST A HEART", 1.6) end end
    end
  end
  if self.drownT then
    self.drownT = self.drownT - dt
    if self.drownT <= 0 then
      self.drownT = nil; self:loseHeart()
      if not self.events.over then self:respawn(); if not self.deadT then self:say("SPLASH! LOST A HEART", 1.6) end end
    end
  end

  -- carrying, picking up, giving
  if presses.act and p.mode == "normal" then
    if p.carrying then
      if nearGirl(self) then self:giveBall() else self:dropBall() end
    elseif nearBall(self) then
      self.ball.state = "carried"; self.ball.picked = true; p.carrying = self.ball; p:grab(); S.play("key")
      self:say(self.def.pickupSay or "BRING ME THE BALL!", 2.4)
    end
  end
  local b = self.ball
  if self.magpie then self:updateMagpie(dt) end
  self:checkExit()
  if b.state == "carried" then b.x, b.y = p:mouthPos()
  elseif b.state == "air" then
    b.vy = math.min(b.vy + 520 * dt, 400); b.airT = (b.airT or 0) + dt
    local ny = b.y + b.vy * dt
    local nx = math.max(14, math.min(w.width - 14, b.x + (b.vx or 0) * dt))
    if w:solidIn(nx - 3, nx + 3, b.y - 6, b.y - 1) then b.vx = 0 else b.x = nx end   -- it bounces off walls, never into them
    local f, hit = w:floor(b.x - 3, b.x + 3, b.x, b.y - 0.5, ny, b.y, b.drop)    -- drop: knocked off a branch, falls through
    if f then b.y = f; b.state = "rest"; b.drop = nil; b.on = hit; b.airT = 0
      if b.knock and self:ballLost() then b.state = "home"; self.ballBackT = 0.6 else b.knock = nil end   -- (knocked: see below)
      if math.abs(b.x - self.girl.x) < 30 and math.abs(b.y - self.girl.y) < 20 then self:giveBall() end
    else b.y = ny end
    if w:inWater(b.x, b.y) then b.state = "home"; self.ballBackT = 1.2; S.play("splash")
    elseif self:ballLost() then b.state = "home"; self.ballBackT = 0.6 end
  elseif b.state == "rest" then
    if b.on and b.on.dx then b.x = b.x + b.on.dx end            -- it rides a ferry or the duck boat with it
    if b.on and b.on.dx and (b.x < b.on.x0 - 2 or b.x > b.on.x1 + 2) then b.state, b.vy, b.vx, b.airT, b.on = "air", 0, 0, 0, nil end
    if b.state == "rest" and self:ballLost() then b.state = "home"; self.ballBackT = 0.6 end
  end
  if b.state == "home" then
    self.ballBackT = (self.ballBackT or 0) - dt
    if self.ballBackT <= 0 and b.knock then                       -- a knocked-out ball comes back near where she was hit
      b.x, b.y, b.state, b.on, b.knock = b.knock.x, b.knock.y, "rest", nil, nil; S.play("land")
      if self:ballLost() then local h = self:homeNear(self.check.x, self.check.y); b.x, b.y = h.x, h.y end
    elseif self.ballBackT <= 0 then
      b.x, b.y, b.state = b.home.x, b.home.y, "rest"; self:say(b.homeSay or self.def.ballBack or "THE BALL IS BACK ON THE BOAT", 2.2)
      if self:ballLost() then b.home = self:homeNear(self.check.x, self.check.y); b.x, b.y = b.home.x, b.home.y end   -- never a home it can't rest at
    end
  end

  -- bones
  local x0, y0, x1, y1 = p:box()
  for _, bn in ipairs(self.bones) do
    if not bn.taken and bn.x + 5 > x0 and bn.x - 5 < x1 and bn.y - 14 < y1 and bn.y - 4 > y0 - 6 then
      bn.taken = true; self.taken = self.taken + 1
      self.score = self.score + (bn.super and 1000 or 100); S.play(bn.super and "superbone" or "bone")
    end
  end
  Sp.updateSecrets(self)

  -- lamp posts: passing a checkpoint lamp saves Pepper's place
  for _, l in ipairs(self.lamps) do
    if l.checkpoint and not l.lit and p.x >= l.x - 6 and p.x <= l.x + 40 and p.y <= l.y + 2 and p.y >= l.y - 90 and p.mode == "normal" then
      l.lit = true; l.litAt = self.t; self.check = { x = l.x, y = l.y }
      -- a lamp is a gift (benchmark principle 5): it gives back one heart, up to the most she can have, and a heart
      -- pops out of it (not in hard mode). The heart's chime instead of the lamp's, so the gift is heard.
      if not self.hard and self.hearts < self.maxHearts then
        local lift = l.y < (self.def.foot or 184) - 40 and Sc.EDGE + 1 or 0   -- (a high road lamp stands lower: draw)
        self.hearts = self.hearts + 1; self.pops[#self.pops + 1] = { x = l.x, y = l.y + lift, t = 0 }; S.play("heart")
      else S.play("checkpoint") end
      if p.carrying and self.def.ballHomeAtLamps then                -- L.ballHomeAtLamps: a lost ball comes back here
        self.ball.home = self:homeNear(l.x, l.y); self.ball.homeSay = "THE BALL IS BACK BY THE LAMP"
      end
    end
  end

  -- bikes: one rides through every few seconds while Pepper is in a bike zone of the promenade.
  -- def.bikes is one zone or a list of zones; each bike remembers its zone (speed, endX).
  -- roadY (tall levels): the feet line the zone's road is at (default 184, the flat levels' line). A zone with
  -- roadY counts Pepper in only while her feet are on that road or up to `band` px (default 90) above it, so a
  -- cart run on the low road says nothing to her on the treetops; without roadY: anywhere above 184, as before.
  local zones = self.def.bikes
  if zones.zoneX0 then zones = { zones } end
  for _, bk in ipairs(zones) do
    local inside = p.x > bk.zoneX0 and p.x < bk.zoneX1 and p.y <= (bk.roadY or 184)
      and (not bk.roadY or p.y > bk.roadY - (bk.band or 90))
    Sp.enterZone(self, bk, inside)                                 -- start = "enter": the first one comes now
    if inside then
      self.bikeT = self.bikeT - dt
      if self.bikeT <= 0 and #self.bikes == 0 then
        self.bikeT = bk.every
        self.bikes[1] = Sp.spawn(self, bk)                          -- 1 s off screen, with a bell (and a sign)
        self.bikeN = (self.bikeN or 0) + 1; self.bikes[1].rider = 1 + self.bikeN % 2   -- (the two riders take turns)
      end
    end
  end
  for i = #self.bikes, 1, -1 do
    local c = self.bikes[i]
    local bk = c.zone or zones[1]
    c.x = c.x - (c.speed or bk.speed) * dt; c.warn = c.warn - dt
    if not bk.rail then c.y = w:groundAt(c.x, bk.roadY and bk.roadY - 34) or c.y end   -- on the pavement, up and down the stairs
    local hw, h = (bk.w or 48) / 2, bk.h or 26                     -- (rail: a tram stays on its line)
    if c.x < bk.endX or c.x < self.cam - 80 then table.remove(self.bikes, i)
    else
      local bx0, bx1, by0 = math.max(c.x - hw, bk.depot or -1e9), c.x + hw, c.y - h   -- (inside its shed it is gone)
      if x1 > bx0 and x0 < bx1 and y1 > by0 and y0 < c.y and p:hurt(c.x, w) then self:hazardHit() end
    end
  end

  if self.road then self.road:update(dt, self.cam) end            -- passing cars and cyclists on the road (scenery)
  AH.updateTrams(self, dt)                                         -- trams in the back lane (scenery)
  Ex.update(self.fx, self, dt)                                     -- dust and splashes: they only watch Pepper

  -- bark rings
  if p.barked then p.barked = false; self.rings[#self.rings + 1] = { x = p.x + p.face * 22, y = p.y - 22, t = 0 }
    if math.abs(p.x - self.girl.x) < 110 and self.girl.state == "idle" then self.girl.state = "wave"; self.girl.t = 0 end
    if self.cat then self:barkAtCat() end
    if self.magpie then self:barkAtMagpie() end
    Cr.bark(self)
    Rf.bark(self)                                                  -- someone turns a vent up
    if self.night then Nt.bark(self) end                           -- [night hook] the fox
  end
  if self.night then Nt.update(self, dt) end                       -- [night hook] the fox, crumbling planks
  if self.cat then self:updateCat(dt) end
  if not self.deadT and not self.drownT then Cr.update(self, dt) end
  for _, pr in ipairs(self.def.props) do                           -- leaf piles flatten when Pepper runs through
    if pr.leaves and not self.kicked[pr] and x1 > pr.x0 and x0 < pr.x1 and y1 > pr.y0 then self.kicked[pr] = true end
  end
  for i = #self.rings, 1, -1 do local r = self.rings[i]; r.t = r.t + dt; if r.t > 0.4 then table.remove(self.rings, i) end end
  for i = #self.pops, 1, -1 do local h = self.pops[i]; h.t = h.t + dt; if h.t > POP_T then table.remove(self.pops, i) end end

  -- the girl
  local g = self.girl
  g.t = g.t + dt
  if (g.state == "wave" or g.state == "call") and g.t > 1.0 then g.state = "idle"; g.t = 0 end
  if g.state == "cheer" and g.t > 1.6 and math.abs(p.x - g.x) < 50 then g.state = "pet"; g.t = 0 end   -- then she pets Pepper
  if g.state == "pet" and g.t > 8 / 7 then g.state = "happy"; g.t = 0 end                             -- and stands back up
  g.callT = math.max(0, g.callT - dt)                             -- she calls Pepper over while the ball is on its way
  local d = math.abs(p.x - g.x)
  if g.state == "idle" and p.carrying and d > 60 and d < 240 and g.callT == 0 then g.state = "call"; g.t = 0; g.callT = 3.5 end

  -- camera: Pepper moves 48 px either side of centre before it follows; it leads 40 px the way she faces
  local want = p.face * 40
  self.lead = self.lead + (want - self.lead) * math.min(1, dt / 0.3)
  local focus = p.x + self.lead
  local centre = self.cam + 160
  if focus > centre + 48 then self.cam = focus - 160 - 48 elseif focus < centre - 48 then self.cam = focus - 160 + 48 end
  self.cam = math.max(0, math.min(w.width - 320, self.cam))
  Vc.update(self, dt)                                             -- and up and down in a tall level (vcam.lua)
  if self.chase then Ch.update(self, dt) end                      -- the chase: the scroll pushes the camera and Pepper
end

-- the cat: a bark close enough (def.cat.range between Pepper's middle and the cat's) scares it. It jumps up,
-- leaps off away from Pepper and runs out of the level; the ball is knocked off and drops to the ground.
function St:barkAtCat()
  local c, p, b = self.cat, self.pepper, self.ball
  if c.state ~= "sit" then return end
  local dx, dy = c.x - p.x, (c.y - 8) - (p.y - p:height() / 2)
  local range = self.def.cat.range or 90
  if dx * dx + dy * dy > range * range then
    if dx * dx + dy * dy < (range * 2) ^ 2 then c.heard = 0.7 end      -- too far: it only looks up ("?")
    return
  end
  c.state, c.t = "scared", 0
  c.dir = (c.x >= p.x) and 1 or -1
  b.state, b.vx, b.vy, b.drop, b.airT = "air", -c.dir * 20, -60, true, 0
  b.home = { x = b.x - c.dir * 12, y = self.world:groundAt(b.x - c.dir * 12, self.world.height > 240 and b.y - 2 or nil) or b.y }; b.homeSay = nil
  S.play("spring")
end

function St:updateCat(dt)
  local c, w = self.cat, self.world
  c.t = c.t + dt
  if c.heard then c.heard = c.heard - dt; if c.heard <= 0 then c.heard = nil end end
  if c.state == "scared" and c.t >= 0.35 then                     -- the startle is over: leap
    c.state, c.vx, c.vy = "leap", c.dir * 80, -150
  elseif c.state == "leap" then
    c.vy = c.vy + 560 * dt; c.x = c.x + c.vx * dt
    local ny = c.y + c.vy * dt
    local g = w:groundAt(c.x, w.height > 240 and c.y - 34 or nil)   -- (a tall world: the ground below it)
    if c.vy > 0 and g and ny >= g then c.y = g; c.state = "run"; self:say("THE CAT RAN OFF! GET THE BALL", 2.4)
    else c.y = ny end
  elseif c.state == "run" then
    c.x = c.x + c.dir * 170 * dt
    c.y = w:groundAt(c.x, w.height > 240 and c.y - 34 or nil) or c.y
    if c.x < self.cam - 60 or c.x > self.cam + 380 then c.state = "gone" end
  end
end

-- what is being said now (talk.lua draws it): nil or a line { who = "pepper" | "girl", btn, text, teach, msg }.
-- The level's L.hints, first match wins: { x0, x1, text, btn, need, maxY, minY, bike }. A hint with a button (btn: "a",
-- "b", "x", "y", "down") is Pepper's: it teaches a control, in 1 to 3 words. One without is the girl's (a goal or
-- a story line). need: "ball" (Pepper carries it), "noball", "nearball" (she can pick it up), "cat" (it sits on
-- the ball), "catnear" (a bark would scare it), "magpie" (it has the ball), "magpienear" (a bark would make it
-- drop the ball), "magpieahead" (it has the ball and sits within 230 px, and she is not sneaking).
-- A teaching hint wins over the other messages (St:say); in hard mode there are only the messages.
local function catNear(s)
  local c, p = s.cat, s.pepper
  if not c or c.state ~= "sit" then return false end
  local dx, dy = c.x - p.x, (c.y - 8) - (p.y - p:height() / 2)
  local r = s.def.cat.range or 90
  return dx * dx + dy * dy <= r * r
end
local function magpie(s, near)
  local m, d, p = s.magpie, s.def.magpie, s.pepper
  if not m or m.state ~= "perch" or s.ball.state ~= "magpie" then return false end
  local dx = math.abs(p.x - m.x)
  local inRange = dx <= d.bark and math.abs(p.y - m.y) < 110
  if near then return inRange end
  return not inRange and dx < 230 and not I.down("walk")
end
function St:zoneHint()
  local p = self.pepper
  for _, h in ipairs(self.def.hints) do
    if p.x >= h.x0 and p.x < h.x1 and (not h.maxY or p.y <= h.maxY) and (not h.minY or p.y >= h.minY) then   -- (minY: tall levels)
      local ok = true
      if h.need == "ball" then ok = p.carrying ~= nil
      elseif h.need == "goose" then ok = Cr.near(self)
      elseif h.need == "gull" then ok = Cr.gullWarn(self)
      elseif h.need == "untouched" then ok = not self.ball.picked and p.carrying == nil
      elseif h.need == "noball" then ok = p.carrying == nil and self.ball.state ~= "given"
      elseif h.need == "nearball" then ok = nearBall(self)
      elseif h.need == "cat" then ok = self.cat ~= nil and self.cat.state == "sit"
      elseif h.need == "catnear" then ok = catNear(self)
      elseif h.need == "magpie" then ok = self.ball.state == "magpie"
      elseif h.need == "magpienear" then ok = magpie(self, true)
      elseif h.need == "magpieahead" then ok = magpie(self, false)
      elseif h.need and self.night then ok = Nt.need(self, h.need) end                     -- [night hook] the fox
      if h.bike then ok = true end
      if ok then return { who = h.btn and "pepper" or "girl", btn = h.btn, text = h.text, teach = h.btn ~= nil } end
    end
  end
end
function St:hint()
  local msg = self.msg and self.msg.line
  if self.hard then return msg and not msg.teach and msg or nil end
  if msg and msg.teach then return msg end
  local zone = self:zoneHint()
  if zone and zone.teach then return zone end
  return msg or zone
end

function St:draw(debug)
  local cam = math.floor(self.cam + 0.5)
  local camY = math.floor((self.camY or 0) + 0.5)                -- the vertical camera (vcam.lua): 0 in a flat level
  local C = Sc.C
  local style = self.def.art                                      -- "park" / "town": a greybox level with its art
  local grey = self.def.scenery == "greybox" and not style
  local lk = Look.on and (style or not grey)                       -- the Lion King look (look.lua): the art levels
  Look.level(self.def)                                             -- (this level's colour script)
  Sc.FOOT = self.def.foot or 184                                   -- the path line the art is placed from (scene.lua)
  Sc.winchFrame = 1                                                -- the winch keeper cranks while a rope ferry moves
  for _, m in ipairs(self.movers or {}) do
    if m.call and math.abs(m.dx or 0) > 0 then Sc.winchFrame = 1 + math.floor(self.t * 10) % 8 end
  end
  local function use(n) if lk then Look.use(n) end end
  local function prop(pr, c, colour, kicked)
    if style then Sc.drawPropArt(pr, c, self.def, kicked) else Sc.drawProp(pr, c, colour) end
  end
  Sc.vshift = Vc.parallax(self, camY)                              -- (tall levels: the layers rise slower than the world)
  if style then Sc.drawFarArt(self.layers, cam, self.t, self.world, self.def)
  elseif grey then Sc.drawFarGrey(self.layers, cam, self.t) else Sc.drawFar(self.layers, cam, self.t) end
  Sc.vshift = nil
  lg.push(); lg.translate(0, -camY)                                -- the world, up to the foreground band
  -- 6 quay back: railing and things behind Pepper
  use("back")
  if style == "park" then Sc.drawTreetops(self.def, cam, self.world) end   -- a tall park's treetops: trunks, canopies
  if style then AH.drawTownBack(self, cam) end                    -- the tall Downtown: the spire, the tall house fronts
  AH.drawTrams(self, cam)                                          -- the back lane's tram and its stop sign (faded)
  for _, pr in ipairs(self.def.props) do if pr.layer == "back" then prop(pr, cam, C.back) end end
  if style then Sc.drawSpout(self.def, cam) end
  Sp.drawBack(self, cam)                                           -- code-drawn decoration (kiosks)
  Rf.drawBack(self, cam, self.t)                                   -- steam columns (behind Pepper)
  if self.chase then Ch.drawBack(self, cam) end                    -- the chase: open cellar hatches
  if self.night then Nt.drawLights(self, cam) end                  -- [night hook] lanterns, windows
  -- 7 play layer: terrain (pavement art, painted once; see Sc.paintGround)
  local w = self.world
  if not self.ground then
    if style then self.ground = Sc.paintGroundArt(w, style, self.def.foot)
    else self.ground = grey and Sc.paintGroundGrey(w) or Sc.paintGround(w, self.def.props) end
  end
  use("ground")
  for _, ps in ipairs(self.def.passages or {}) do Sc.passageBack(ps, cam) end
  lg.setColor(1, 1, 1, 1)
  self.ground:draw(cam, camY)                                      -- (in chunks, the ones on screen: scene.lua)
  if lk then Look.road(self, cam, Sc) end                          -- the road rows recede (row scrolling)
  for _, ps in ipairs(self.def.passages or {}) do Sc.passageFront(ps, cam) end
  if style then Sc.drawTerrainArt(self.def, cam, self.t) end         -- the slide, the fountain's jets
  -- the river Pepper can fall into is not drawn: it is a gap in the quay, and the river art shows through
  local art = Sc.art()
  -- shadows of the things standing on the pavement (drawn on the ground, under them)
  for _, pr in ipairs(self.def.props) do
    if (pr.art or pr.fence) and not pr.noshadow and pr.layer == "play" and pr.x1 - cam > -10 and pr.x0 - cam < 330 then
      if pr.ax then local iw = art[pr.art]:getWidth(); Sc.shadow(pr.ax + iw / 2 - cam, (pr.ay or pr.y1) - 1, iw + 4, pr.depth)
      else Sc.shadow((pr.x0 + pr.x1) / 2 - cam, pr.y1 - 1, pr.x1 - pr.x0 + 4) end
    end
  end
  if grey then                                                     -- greybox lamp posts on the path
    for _, l in ipairs(self.lamps) do if l.x - cam > -20 and l.x - cam < 340 then Sc.lampGrey(l.x - cam, l.y, l.lit, self.t - (l.litAt or -9), self.t) end end
  else
  -- (art/placement) a lamp on a tall level's high road stands on its ledge (a walk, a branch, a gallery): no
  -- pavement there, so its foot goes on the ledge's top, behind its front edge, not EDGE px above it in the air
  local function highLamp(l) return l.y < Sc.FOOT - 40 end
  for _, l in ipairs(self.lamps) do if l.x - cam > -20 and l.x - cam < 340 and not highLamp(l) then Sc.shadow(l.x - cam, l.y - Sc.EDGE - 1, 14) end end
  use("back")
  lg.setColor(1, 1, 1, 1)
  for _, l in ipairs(self.lamps) do                                -- lamp posts; a passed checkpoint lights up
    local x = l.x - cam
    if x > -20 and x < 340 then
      local im = l.lit and art.lamp_lit or art.lamp_post
      local lx, top = math.floor(x - im:getWidth() / 2), l.y - (highLamp(l) and -1 or Sc.EDGE) - im:getHeight()
      if highLamp(l) then                                          -- (its whole foot on the ledge: Downtown's lamp at
        for _, pr in ipairs(self.def.props) do                     -- 2420 stood half off the ledge's end; drawing only)
          if pr.kind ~= "decor" and pr.y0 == l.y and l.x >= pr.x0 and l.x < pr.x1 then
            lx = math.max(math.floor(pr.x0 - cam), math.min(math.floor(pr.x1 - cam) - im:getWidth(), lx))
          end
        end
      end
      lg.draw(im, lx, top)
      if l.lit then Sc.lampLight(lx + im:getWidth() / 2, top + 17, self.t - (l.litAt or -9), self.t) end
    end
  end
  end
  -- River Walk's bikes ride behind the obstacles on Pepper's line (r5/bugs): the adult's bike is taller than a flower
  -- box, so drawn in front of the box it rode through Pepper standing on it; behind it, the box hides its wheels
  -- Downtown's cargo bikes too (r8/levels, D1): the kiosk and the gates hide their wheels; Pepper on a perch is
  -- drawn over the tall rider (arthooks.lua)
  use("play")
  for _, c in ipairs(self.bikes) do if c.zone and c.zone.kind == "cargo" then AH.drawCargo(c, cam) end end
  if not style and not grey then
    use("play"); lg.setColor(1, 1, 1, 1)
    for _, c in ipairs(self.bikes) do
      local cyc = Rd.art().riders[c.rider or 1]
      Rd.drawBike(cyc, -c.x, math.floor(c.x - cam + 0.5) - math.floor(cyc:getWidth() / 2), math.floor(c.y - cyc:getHeight() + 0.5), true)
    end                                                            -- the art faces right; bikes ride left, wheels rolling
  end
  -- decoration on her line takes the back look, except the pieces whose drawn parts she stands on (art/fixes:
  -- the statue, its arm and hat are ledges): they are outlined obstacles and take the play look
  local PLAYLOOK = { STATUE = true }
  for _, pr in ipairs(self.def.props) do
    if pr.layer == "play" and not pr.over then use((pr.kind == "decor" and not PLAYLOOK[pr.name]) and "back" or "play"); prop(pr, cam, C.prop) end
  end
  use("play")
  Sp.drawRopes(self, cam)                                          -- the ropes the ferries run on
  for _, m in ipairs(self.movers) do
    if style then Sc.drawMoverArt(m, cam, style)                       -- the duck boat
    elseif m.lift then Lf.draw(m, cam, Sc, self.t)                     -- a lift (lift.lua)
    elseif grey then                                                   -- greybox level: labelled boxes (the duck boat)
      Sc.outlined(C.prop, C.propEdge, m.x0 - cam, m.y0, m.x1 - m.x0, m.y1 - m.y0); Sc.label(m.name or "PONTOON", (m.x0 + m.x1) / 2 - cam, m.y0 + 8)
    else                                                           -- the pontoon (art 54 x 12; its deck row 2 is the top)
      if m.name == "ROWBOAT" then Sp.drawRowboat(m, cam, self.t)        -- a rowing boat, its rower at the oars
      else lg.setColor(1, 1, 1, 1); lg.draw(art.pontoon, math.floor(m.x0 - cam + 0.5) - 3, m.y0 - 2) end
    end
  end
  if lk then Look.off() end                                        -- the bones, the girl, the ball, Pepper: as drawn
  lg.setColor(1, 1, 1, 1)
  for _, bn in ipairs(self.bones) do                               -- bones (11 x 6), gold = super bone
    if not bn.taken and not (self.night and Nt.hideBone(self, bn)) then   -- [night hook] bones in the dark
      local bob = math.floor(math.sin(self.t * 3 + bn.x) * 1.5 + 0.5)
      lg.draw(bn.super and art.bone_gold or art.bone, math.floor(bn.x - cam + 0.5) - 5, bn.y - 12 + bob)
    end
  end
  use("play")                                                      -- (the leaf piles are part of the park, the bones are not)
  for _, pr in ipairs(self.def.props) do                           -- props drawn over the bones (leaf piles)
    if pr.layer == "play" and pr.over then
      if style then prop(pr, cam, C.leaves, self.kicked[pr])
      elseif self.kicked[pr] then Sc.drawProp({ x0 = pr.x0 - 3, x1 = pr.x1 + 3, y0 = pr.y1 - 4, y1 = pr.y1, kind = "decor" }, cam, C.leaves)
      else Sc.drawProp(pr, cam, C.leaves) end
    end
  end
  use("play")
  Sp.drawPlay(self, cam)                                           -- code-drawn obstacles (kennel, hollow log, awnings)
  Rf.drawPlay(self, cam, Sc)                                       -- vent hoods, loose tiles
  use("ground")
  -- shadows of the girl, the ball and Pepper: on the floor right under them (smaller the higher they are)
  local g = self.girl
  if not g.hidden then Sc.shadow(g.x - cam, g.y, 22) end
  local b = self.ball
  if b.state == "rest" or b.state == "air" then
    local fy = w:floor(b.x - 2, b.x + 2, b.x, b.y - 0.5, w.height, b.y - 0.5, b.drop)
    if fy then Sc.shadow(b.x - cam, fy, 8 - math.min(4, (fy - b.y) / 8)) end
  end
  local p = self.pepper
  if p.mode ~= "gone" and p.mode ~= "drown" then
    local fy = w:floor(p.x - 4, p.x + 4, p.x, p.y - 0.5, w.height, p.y - 0.5)
    if fy then Sc.shadow(p.x - cam, fy, 32 * (1 - math.min(48, fy - p.y) / 96)) end
  end
  if lk then Look.off() end
  -- the girl (real art)
  local gr = GIRL_ROW[g.state] or GIRL_ROW.idle                    -- "happy" (after petting) shows the idle clip
  local rw = GF.rows[gr]
  local fr = 1 + math.floor(g.t * GIRL_FPS[rw.name]) % rw.n
  if rw.name == "pet" then fr = math.min(rw.n, 1 + math.floor(g.t * GIRL_FPS.pet)) end    -- plays once and holds
  local face = (self.pepper.x < g.x) and -1 or 1
  lg.setColor(1, 1, 1, 1)
  if not g.hidden then lg.draw(girlImg, girlQ[gr][fr], math.floor(g.x - cam + 0.5), g.y, 0, face, 1, rw.x, rw.y) end
  -- the ball (real art), unless Pepper carries it (drawn after her)
  if b.state == "rest" or b.state == "air" or b.state == "cat" or b.state == "magpie" or b.state == "roll" or (b.state == "given" and g.state ~= "pet" and g.state ~= "happy") then
    local bx, by = b.x, b.y
    if b.state == "given" then bx, by = g.x + face * 8, g.y - 30 - math.abs(math.sin(g.t * 6)) * 14 end
    lg.draw(ballImg, math.floor(bx - cam - 3 + 0.5), math.floor(by - 6 + 0.5))
  end
  -- bikes: an adult cyclist (art/scene/road_cyclist1-2.png, 73 x 75: the wheels as tall as Pepper's back; drawn
  -- behind the obstacles, before the play props) centred on the zone's hit box (River Walk: 70 x 28, the bike from wheel to wheel), wheels on the pavement; greybox:
  -- a box the size of the zone's hit box (w, h), labelled with its kind (CART, TRAM) or BIKE. (Until r5/bugs the
  -- small cyclist1.png, 49 x 50, a child's bike next to Pepper.)
  if self.cat and self.cat.state ~= "gone" then
    if self.def.art then Sc.cat(self.cat, cam, self.t, self.pepper.x) else Sc.catGrey(self.cat, cam, self.t) end
  end
  if self.magpie and self.magpie.state ~= "gone" then
    if self.def.magpie.look == "gull" then Cr.drawBird(self.magpie, cam, self.t) else Sc.magpie(self.magpie, cam, self.t) end   -- (a gull's nest)
  end
  Cr.draw(self, cam, self.t)                                       -- geese and gulls
  if self.chase then Ch.draw(self, cam) end                        -- the chase: barrels
  if self.night then Nt.drawWorld(self, cam) end                   -- [night hook] the fox
  use("play")
  for _, c in ipairs(self.bikes) do
    local x = c.x - cam
    local cargo = c.zone and c.zone.kind == "cargo"                      -- (drawn behind the obstacles, above)
    local depot = not cargo and c.zone and c.zone.depot                  -- a tram entering its shed: drawn right of the door
    if depot then lg.setScissor(math.max(0, math.floor(depot - cam)), 0, 400, 240) end   -- (screen space: the whole height)
    if cargo then                                                        -- (the cargo bike: arthooks.lua, above)
    elseif style then Sc.drawHazardArt(c, cam, style)                    -- the leaf cart, the tram
    elseif grey then
      local z = c.zone or {}
      local bw, bh = z.w or 48, z.h or 26
      Sc.outlined(C.prop, C.propEdge, math.floor(x - bw / 2 + 0.5), c.y - bh, bw, bh); Sc.label(z.kind and z.kind:upper() or "BIKE", x, c.y - 17)
    end                                                                  -- (River Walk's bikes: drawn behind the obstacles, above)
    if depot then lg.setScissor() end
  end
  if lk then Look.off() end
  Sp.drawWarnings(self, cam)                                       -- a sign at the edge a bike or tram comes from
  -- Pepper
  Ex.drawBehind(self.fx, cam)                                      -- dust behind her
  lg.setColor(1, 1, 1, 1)
  self.pepper:draw(cam)
  if b.state == "carried" and self.pepper.anim ~= "grab" then lg.setColor(1, 1, 1, 1); lg.draw(ballImg, math.floor(b.x - cam - 3 + 0.5), math.floor(b.y - 3 + 0.5)) end
  Ex.drawFront(self.fx, cam)                                       -- and the extras in front of her
  for _, r in ipairs(self.rings) do
    lg.setColor(1, 1, 1, 1 - r.t / 0.4); lg.setLineWidth(1)
    lg.circle("line", math.floor(r.x - cam), math.floor(r.y), 6 + r.t * 70)
  end
  for _, h in ipairs(self.pops) do                                 -- a heart pops out of a lamp: up 26 px, fading
    local k = h.t / POP_T
    local x = math.floor(h.x - cam + 0.5) - 7
    local y = math.floor(h.y - (grey and 76 or 94) - 26 * (1 - (1 - k) ^ 2) + 0.5) - 7
    local a = k < 0.7 and 1 or (1 - k) / 0.3
    if k < 0.12 then x, y = x + 3, y + 3 end                       -- (a small pop first, then full size)
    local sc = k < 0.12 and 1 or 2
    for r, line in ipairs(HEART) do
      for c = 1, #line do
        local col = HCOL[line:sub(c, c)]
        if col then lg.setColor(col[1], col[2], col[3], a); lg.rectangle("fill", x + (c - 1) * sc, y + (r - 1) * sc, sc, sc) end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
  use("play")
  if self.road then self.road:draw(cam, self.t, lk and Look.rowFactor) end            -- traffic in the near lane, in front of the promenade
  use("front")
  -- 8 foreground frame
  -- (scrolls 1.3x: a prop sits at its own x when it is mid-screen and slides faster than Pepper's layer)
  for _, pr in ipairs(self.def.props) do
    if pr.layer == "front" then prop(pr, math.floor(cam + (cam + 160 - (pr.x0 + pr.x1) / 2) * 0.3), C.front) end
  end
  lg.pop()                                                         -- (screen space again)
  if lk then Look.off(); Look.front(self, cam, camY) end           -- the dark foreground band (1.4x), under Pepper's lines
  if self.night then Nt.draw(self, cam) end                        -- [night hook] the darkness, the trail, the planks
  lg.setColor(1, 1, 1, 1)
  if debug then lg.push(); lg.translate(0, -camY); self:drawDebug(cam); lg.pop() end
end

function St:drawDebug(cam)
  local w = self.world
  lg.setLineWidth(1)
  for _, r in ipairs(w.rects) do
    if r.kind == "solid" then lg.setColor(1, 0.3, 0.3, 0.9) else lg.setColor(1, 0.9, 0.2, 0.9) end
    lg.rectangle("line", r.x0 - cam + 0.5, r.y0 + 0.5, r.x1 - r.x0 - 1, r.y1 - r.y0 - 1)
  end
  lg.setColor(0.2, 0.9, 1, 0.9)
  for _, s in ipairs(w.slopes) do
    if s.dir < 0 then lg.line(s.x0 - cam, s.y0, s.x1 - cam, s.y1) else lg.line(s.x0 - cam, s.y1, s.x1 - cam, s.y0) end
  end
  lg.setColor(0.3, 0.5, 1, 0.9)
  for _, r in ipairs(w.water) do lg.rectangle("line", r.x0 - cam + 0.5, r.y0 + 0.5, r.x1 - r.x0 - 1, r.y1 - r.y0 - 1) end
  lg.setColor(1, 0.9, 0.2, 0.9)
  for _, m in ipairs(self.movers) do lg.rectangle("line", m.x0 - cam + 0.5, m.y0 + 0.5, m.x1 - m.x0 - 1, m.y1 - m.y0 - 1) end
  local x0, y0, x1, y1 = self.pepper:box()
  lg.setColor(0.3, 1, 0.3, 1); lg.rectangle("line", x0 - cam + 0.5, y0 + 0.5, x1 - x0 - 1, y1 - y0 - 1)
  local cy = math.floor((self.camY or 0) + 0.5)                     -- (the camera's dead zone, on screen)
  lg.setColor(1, 1, 1, 0.5); lg.line(112, 20 + cy, 112, 240 + cy); lg.line(208, 20 + cy, 208, 240 + cy)
  lg.setColor(1, 1, 1, 1)
end

function St:stats() return { bones = self.taken, total = self.total, time = self.time, score = self.score, hearts = self.hearts,
  lives = self.lives, levelScore = self.score - self.startScore, bonus = self.bonus,
  secrets = self.secretsFound, secretsTotal = #self.secrets } end
return St
