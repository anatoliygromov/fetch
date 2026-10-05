-- One level being played: world, Pepper, the ball, the girl, bones, bikes, lamps, camera and rules.
local Wd = require("world")
local Pp = require("pepper")
local Sc = require("scene")
local S = require("sfx")
local I = require("input")
local St = {}
St.__index = St
local lg = love.graphics
local function img(p) local i = lg.newImage(p); i:setFilter("nearest", "nearest"); return i end
local girlImg, ballImg, girlQ
local GF = require("girl_frames")             -- the girl's SpriteCook animations: idle, wave, cheer, call
local GIRL_ROW, GIRL_FPS = {}, { idle = 6, wave = 9, cheer = 9, call = 8, pet = 7 }
for i, r in ipairs(GF.rows) do GIRL_ROW[r.name] = i end

function St.new(def)
  if not girlImg then
    girlImg, ballImg, girlQ = img("art/girl.png"), img("art/ball.png"), {}
    for r, rw in ipairs(GF.rows) do
      girlQ[r] = {}
      for c = 1, rw.n do girlQ[r][c] = lg.newQuad((c - 1) * GF.CW, (r - 1) * GF.CH, GF.CW, GF.CH, girlImg:getDimensions()) end
    end
  end
  local s = setmetatable({ def = def, t = 0, cam = 0, lead = 0, score = 0, hearts = 3, lives = 3, time = def.time,
    rings = {}, msg = nil, events = {}, bikeT = 2.5, bikes = {} }, St)
  s.world = Wd.load(def.map, def.props)
  s.movers = {}
  for _, m in ipairs(def.movers) do
    local mv = { name = m.name, x0 = m.from, x1 = m.from + (m.x1 - m.x0), y0 = m.y0, y1 = m.y1, from = m.from, to = m.to, speed = m.speed, dir = 1, dx = 0, kind = "oneway" }
    s.world:addMover(mv); s.movers[#s.movers + 1] = mv
  end
  s.layers = Sc.build(s.world.width)
  s.pepper = Pp.new(def.start.x, def.start.y)
  s.check = { x = def.start.x, y = def.start.y }
  s.bones = {}
  for i, b in ipairs(def.bones) do s.bones[i] = { x = b.x, y = b.y, super = b.super, taken = false } end
  s.total = #s.bones
  s.taken = 0
  s.lamps = {}
  for i, l in ipairs(def.lamps) do s.lamps[i] = { x = l.x, y = l.y, checkpoint = l.checkpoint, lit = false } end
  s.ball = { x = def.ball.x, y = def.ball.y, home = { x = def.ball.x, y = def.ball.y }, state = "rest", vy = 0 }
  s.girl = { x = def.girl.x, y = def.girl.y, state = "idle", t = 0, callT = 0 }
  s.cam = 0
  return s
end

function St:say(text, t) self.msg = { text = text, t = t or 2.2 } end

function St:respawn()
  local p = self.pepper
  p.x, p.y, p.vx, p.vy = self.check.x, self.check.y, 0, 0
  p.mode, p.onGround, p.ground, p.crouch, p.invuln = "normal", true, nil, false, 1.0
  self.cam = math.max(0, math.min(self.world.width - 320, p.x - 140))
end

function St:loseHeart()
  self.hearts = self.hearts - 1
  if self.hearts <= 0 then
    self.lives = self.lives - 1; self.hearts = 3
    if self.lives <= 0 then self.events.over = true; return end
    self:say("OUCH! BACK TO THE LAMP POST", 2)
    self.deadT = 0.6
  end
end

local function nearBall(s) local p, b = s.pepper, s.ball
  return b.state == "rest" and math.abs(p.x + p.face * 18 - b.x) < 24 and math.abs(p.y - b.y) < 22
end
local function nearGirl(s) return math.abs(s.pepper.x - s.girl.x) < 44 and math.abs(s.pepper.y - s.girl.y) < 20 end

function St:dropBall()
  local b, p = self.ball, self.pepper
  b.x, b.y = p:mouthPos(); b.state = "air"; b.vy = -40; b.vx = p.vx * 0.5; p.carrying = nil
end

function St:giveBall()
  local b = self.ball
  b.state = "given"; self.pepper.carrying = nil; self.girl.state = "cheer"; self.girl.t = 0
  self.score = self.score + 2000; S.play("heart"); self:say("GOOD GIRL, PEPPER!", 3)
  self.clearT = 2.2
end

function St:update(dt, presses)
  self.t = self.t + dt
  local p, w = self.pepper, self.world
  if self.msg then self.msg.t = self.msg.t - dt; if self.msg.t <= 0 then self.msg = nil end end
  if self.clearT then self.clearT = self.clearT - dt; if self.clearT <= 0 then self.events.clear = true; self.clearT = nil end end
  if not self.clearT and not self.events.clear then self.time = self.time - dt end
  if self.time <= 0 then
    self.time = self.def.time; self.lives = self.lives - 1; self.hearts = 3
    if self.lives <= 0 then self.events.over = true else self:say("TIME UP!", 2); self:respawn() end
  end

  -- moving platforms
  for _, m in ipairs(self.movers) do
    local nx = m.x0 + m.dir * m.speed * dt
    if nx > m.to then nx = m.to; m.dir = -1 elseif nx < m.from then nx = m.from; m.dir = 1 end
    m.dx = nx - m.x0; m.x1 = m.x1 + m.dx; m.x0 = nx
  end

  -- Pepper
  if self.deadT then
    self.deadT = self.deadT - dt
    if self.deadT <= 0 then self.deadT = nil; self:respawn() end
  else
    p:update(dt, w, presses)
    if p.mode == "drown" and not self.drownT then
      self.drownT = 1.0
      if p.carrying then p.carrying = nil; self.ball.state = "home"; self.ballBackT = 1.2 end
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
      self.ball.state = "carried"; p.carrying = self.ball; p:grab(); S.play("key")
      self:say("BRING IT TO THE GIRL!", 2.4)
    end
  end
  local b = self.ball
  if b.state == "carried" then b.x, b.y = p:mouthPos()
  elseif b.state == "air" then
    b.vy = math.min(b.vy + 520 * dt, 400)
    local ny = b.y + b.vy * dt; b.x = b.x + (b.vx or 0) * dt
    local f = w:floor(b.x - 3, b.x + 3, b.x, b.y - 0.5, ny, b.y)
    if f then b.y = f; b.state = "rest"; if nearGirl(self) or math.abs(b.x - self.girl.x) < 30 then self:giveBall() end
    else b.y = ny end
    if w:inWater(b.x, b.y) then b.state = "home"; self.ballBackT = 1.2; S.play("splash") end
  end
  if b.state == "home" then
    self.ballBackT = (self.ballBackT or 0) - dt
    if self.ballBackT <= 0 then b.x, b.y, b.state = b.home.x, b.home.y, "rest"; self:say("THE BALL IS BACK ON THE BOAT", 2.2) end
  end

  -- bones
  local x0, y0, x1, y1 = p:box()
  for _, bn in ipairs(self.bones) do
    if not bn.taken and bn.x + 5 > x0 and bn.x - 5 < x1 and bn.y - 14 < y1 and bn.y - 4 > y0 - 6 then
      bn.taken = true; self.taken = self.taken + 1
      self.score = self.score + (bn.super and 1000 or 100); S.play(bn.super and "superbone" or "bone")
    end
  end

  -- lamp posts: passing a checkpoint lamp saves Pepper's place
  for _, l in ipairs(self.lamps) do
    if l.checkpoint and not l.lit and p.x >= l.x - 6 and p.x <= l.x + 40 and p.y <= l.y + 2 and p.y >= l.y - 90 and p.mode == "normal" then
      l.lit = true; l.litAt = self.t; self.check = { x = l.x, y = l.y }; S.play("checkpoint")
    end
  end

  -- bikes: one rides through every few seconds while Pepper is on the promenade
  local bk = self.def.bikes
  local inZone = p.x > bk.zoneX0 and p.x < bk.zoneX1 and p.y <= 184
  if inZone then
    self.bikeT = self.bikeT - dt
    if self.bikeT <= 0 and #self.bikes == 0 then
      self.bikeT = bk.every
      self.bikes[1] = { x = self.cam + 320 + bk.speed * 1.1, y = 184, warn = 1.1 }
      S.play("bell")
    end
  end
  for i = #self.bikes, 1, -1 do
    local c = self.bikes[i]
    c.x = c.x - bk.speed * dt; c.warn = c.warn - dt
    if c.x < bk.endX or c.x < self.cam - 80 then table.remove(self.bikes, i)
    else
      local bx0, bx1, by0 = c.x - 24, c.x + 24, c.y - 26
      if x1 > bx0 and x0 < bx1 and y1 > by0 and y0 < c.y and p:hurt(c.x) then self:loseHeart() end
    end
  end

  -- bark rings
  if p.barked then p.barked = false; self.rings[#self.rings + 1] = { x = p.x + p.face * 22, y = p.y - 22, t = 0 }
    if math.abs(p.x - self.girl.x) < 110 and self.girl.state == "idle" then self.girl.state = "wave"; self.girl.t = 0 end
  end
  for i = #self.rings, 1, -1 do local r = self.rings[i]; r.t = r.t + dt; if r.t > 0.4 then table.remove(self.rings, i) end end

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
end

function St:hint()
  if self.msg then return self.msg.text end
  local p = self.pepper
  for _, h in ipairs(self.def.hints) do
    if p.x >= h.x0 and p.x < h.x1 and (not h.maxY or p.y <= h.maxY) then
      local ok = true
      if h.need == "ball" then ok = p.carrying ~= nil
      elseif h.need == "noball" then ok = p.carrying == nil and self.ball.state ~= "given"
      elseif h.need == "nearball" then ok = nearBall(self) end
      if h.bike then ok = true end
      if ok then return h.text end
    end
  end
  return nil
end

function St:draw(debug)
  local cam = math.floor(self.cam + 0.5)
  local C = Sc.C
  Sc.drawFar(self.layers, cam, self.t)
  -- 6 quay back: railing and things behind Pepper
  for _, pr in ipairs(self.def.props) do if pr.layer == "back" then Sc.drawProp(pr, cam, C.back) end end
  -- 7 play layer: terrain (pavement art, painted once; see Sc.paintGround)
  local w = self.world
  if not self.ground then self.ground = Sc.paintGround(w) end
  lg.setColor(1, 1, 1, 1)
  lg.draw(self.ground, -cam, 0)
  -- the river Pepper can fall into is not drawn: it is a gap in the quay, and the river art shows through
  local art = Sc.art()
  -- shadows of the things standing on the pavement (drawn on the ground, under them)
  for _, pr in ipairs(self.def.props) do
    if pr.art and pr.layer == "play" and pr.x1 - cam > -10 and pr.x0 - cam < 330 then
      Sc.shadow((pr.x0 + pr.x1) / 2 - cam, pr.y1 - 1, pr.x1 - pr.x0 + 4)
    end
  end
  for _, l in ipairs(self.lamps) do if l.x - cam > -20 and l.x - cam < 340 then Sc.shadow(l.x - cam, l.y - Sc.EDGE - 1, 14) end end
  lg.setColor(1, 1, 1, 1)
  for _, l in ipairs(self.lamps) do                                -- lamp posts; a passed checkpoint lights up
    local x = l.x - cam
    if x > -20 and x < 340 then
      local im = l.lit and art.lamp_lit or art.lamp_post
      local lx, top = math.floor(x - im:getWidth() / 2), l.y - Sc.EDGE - im:getHeight()
      lg.draw(im, lx, top)
      if l.lit then Sc.lampLight(lx + im:getWidth() / 2, top + 17, self.t - (l.litAt or -9), self.t) end
    end
  end
  for _, pr in ipairs(self.def.props) do if pr.layer == "play" then Sc.drawProp(pr, cam, C.prop) end end
  for _, m in ipairs(self.movers) do Sc.outlined(C.prop, C.propEdge, m.x0 - cam, m.y0, m.x1 - m.x0, m.y1 - m.y0) end
  if self.movers[1] then local m = self.movers[1]; Sc.label("PONTOON", (m.x0 + m.x1) / 2 - cam, m.y0 + 8) end
  for _, bn in ipairs(self.bones) do                               -- bones: small boxes, gold = super bone
    if not bn.taken then
      local bob = math.floor(math.sin(self.t * 3 + bn.x) * 1.5 + 0.5)
      local wd = bn.super and 12 or 9
      Sc.outlined(bn.super and C.gold or C.bone, C.boneEdge, bn.x - cam - wd / 2, bn.y - 11 + bob, wd, 5)
    end
  end
  -- shadows of the girl, the ball and Pepper: on the floor right under them (smaller the higher they are)
  local g = self.girl
  Sc.shadow(g.x - cam, g.y, 22)
  local b = self.ball
  if b.state == "rest" or b.state == "air" then
    local fy = w:floor(b.x - 2, b.x + 2, b.x, b.y - 0.5, 240, b.y - 0.5)
    if fy then Sc.shadow(b.x - cam, fy, 8 - math.min(4, (fy - b.y) / 8)) end
  end
  local p = self.pepper
  if p.mode ~= "gone" and p.mode ~= "drown" then
    local fy = w:floor(p.x - 4, p.x + 4, p.x, p.y - 0.5, 240, p.y - 0.5)
    if fy then Sc.shadow(p.x - cam, fy, 32 * (1 - math.min(48, fy - p.y) / 96)) end
  end
  -- the girl (real art)
  local gr = GIRL_ROW[g.state] or GIRL_ROW.idle                    -- "happy" (after petting) shows the idle clip
  local rw = GF.rows[gr]
  local fr = 1 + math.floor(g.t * GIRL_FPS[rw.name]) % rw.n
  if rw.name == "pet" then fr = math.min(rw.n, 1 + math.floor(g.t * GIRL_FPS.pet)) end    -- plays once and holds
  local face = (self.pepper.x < g.x) and -1 or 1
  lg.setColor(1, 1, 1, 1)
  lg.draw(girlImg, girlQ[gr][fr], math.floor(g.x - cam + 0.5), g.y, 0, face, 1, rw.x, rw.y)
  -- the ball (real art), unless Pepper carries it (drawn after her)
  if b.state == "rest" or b.state == "air" or (b.state == "given" and g.state ~= "pet" and g.state ~= "happy") then
    local bx, by = b.x, b.y
    if b.state == "given" then bx, by = g.x + face * 8, g.y - 30 - math.abs(math.sin(g.t * 6)) * 14 end
    lg.draw(ballImg, math.floor(bx - cam - 3 + 0.5), math.floor(by - 6 + 0.5))
  end
  -- bikes
  for _, c in ipairs(self.bikes) do
    local x = c.x - cam
    Sc.outlined(C.prop, C.propEdge, x - 24, c.y - 26, 48, 26)
    Sc.outlined(C.prop, C.propEdge, x - 8, c.y - 62, 16, 36)
    Sc.label("BIKE", x, c.y - 17)
    if c.warn > 0 and x > 320 then lg.setColor(C.gold); lg.rectangle("fill", 312, 150, 6, 18); lg.rectangle("fill", 312, 170, 6, 6) end
  end
  -- Pepper
  lg.setColor(1, 1, 1, 1)
  self.pepper:draw(cam)
  if b.state == "carried" and self.pepper.anim ~= "grab" then lg.setColor(1, 1, 1, 1); lg.draw(ballImg, math.floor(b.x - cam - 3 + 0.5), math.floor(b.y - 3 + 0.5)) end
  for _, r in ipairs(self.rings) do
    lg.setColor(1, 1, 1, 1 - r.t / 0.4); lg.setLineWidth(1)
    lg.circle("line", math.floor(r.x - cam), math.floor(r.y), 6 + r.t * 70)
  end
  -- 8 foreground frame
  -- (scrolls 1.3x: a prop sits at its own x when it is mid-screen and slides faster than Pepper's layer)
  for _, pr in ipairs(self.def.props) do
    if pr.layer == "front" then Sc.drawProp(pr, math.floor(cam + (cam + 160 - (pr.x0 + pr.x1) / 2) * 0.3), C.front) end
  end
  lg.setColor(1, 1, 1, 1)
  if debug then self:drawDebug(cam) end
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
  lg.setColor(1, 1, 1, 0.5); lg.line(112, 20, 112, 240); lg.line(208, 20, 208, 240)
  lg.setColor(1, 1, 1, 1)
end

function St:stats() return { bones = self.taken, total = self.total, time = self.time, score = self.score, hearts = self.hearts, lives = self.lives } end
return St
