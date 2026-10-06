-- Playtest lab: the event log. It only watches the game (api.stage(), api.getState()) after every 1/60 s step and
-- writes down what happened; it never changes the game. Loaded by --playtest and by --log (which can ride along
-- with any other mode, e.g. --auto, to log the autopilot's clean run).
--   events: { t (s of play), T (s since launch, cards included), type, x, y, screen, ... }
local I = require("input")
local L = {}
L.__index = L
local DT = 1 / 60

function L.new(api)
  return setmetatable({ api = api, T = 0, playT = 0, step = 0, events = {}, seenHint = {}, cards = {}, cardT = 0,
    state = nil, activity = nil, firstUse = {} }, L)
end

local function screenOf(x) return math.floor(x / 320) + 1 end
function L:event(kind, data)
  local s = self.api.stage()
  local p = s and s.pepper
  local e = { t = self.playT, T = self.T, step = self.step, type = kind, x = p and math.floor(p.x + 0.5) or 0, y = p and math.floor(p.y + 0.5) or 0 }
  e.screen = screenOf(e.x)
  e.ob = self.curOb                                   -- the obstacle the bot is at (persona runs only)
  for k, v in pairs(data or {}) do e[k] = v end
  self.events[#self.events + 1] = e
  if self.onEvent then self.onEvent(e) end
  return e
end

-- a fresh stage (start, or a restart after GAME OVER): take a new snapshot
function L:snapshot(s)
  self.s = s
  local p = s.pepper
  self.prev = { hearts = s.hearts, lives = s.lives, time = s.time, mode = p.mode, ball = s.ball.state,
    magI = s.magpie and s.magpie.i, cat = s.cat and s.cat.state, bones = {}, lamps = {}, bikes = {}, carrying = p.carrying ~= nil }
  for i, b in ipairs(s.bones) do self.prev.bones[i] = b.taken end
  for i, l in ipairs(s.lamps) do self.prev.lamps[i] = l.lit end
  for _, b in ipairs(s.bikes) do self.prev.bikes[b] = true end
  self.lastHint = nil
  self.still = nil
end

function L:use(mech, data)                   -- the first time a mechanic is used in this run
  if self.firstUse[mech] then return end
  self.firstUse[mech] = true
  local d = { mech = mech }; for k, v in pairs(data or {}) do d[k] = v end
  self:event("mech_use", d)
end

function L:tick()
  self.step = self.step + 1
  self.T = self.T + DT
  local api = self.api
  local st = api.getState()
  local s = api.stage()
  if st ~= self.state then
    local was = self.state
    self.state = st
    if self.cardStart and was ~= "play" then
      self.cards[#self.cards + 1] = { kind = was, dur = self.T - self.cardStart }
      self.cardStart = nil
    end
    if st ~= "play" then self.cardStart = self.T end
    if st == "play" and was == "intro" then self:event("start") end
    if st == "clear" then self:event("clear") end
    if st == "over" then self:event("game_over") end
  end
  if st ~= "play" then if st ~= "pause" then self.cardT = self.cardT + DT end; return end
  self.playT = self.playT + DT
  if s ~= self.s then self:snapshot(s) end
  local p, pv = s.pepper, self.prev

  -- hints and messages: the first time each text is shown
  local h = s:hint()
  if h and h ~= self.lastHint and not self.seenHint[h] then
    self.seenHint[h] = true
    self:event("hint", { text = h, say = s.msg ~= nil })
  end
  self.lastHint = h

  for i, b in ipairs(s.bones) do
    if b.taken and not pv.bones[i] then self:event("bone", { gold = b.super and true or false, i = i }) end
    pv.bones[i] = b.taken
  end
  for i, l in ipairs(s.lamps) do
    if l.lit and not pv.lamps[i] then self:event("checkpoint", { i = i }) end
    pv.lamps[i] = l.lit
  end
  for _, b in ipairs(s.bikes) do
    if not pv.bikes[b] then
      pv.bikes[b] = true
      local z = b.zone or {}
      self:event("hazard", { kind = z.kind or "bike", hx = math.floor(b.x) })
    end
  end

  -- what hurt her: water, a bike / cart / tram, or the clock
  if p.mode ~= pv.mode then
    if p.mode == "drown" then self.cause = { "water", self.T }; self:event("drown")
    elseif p.mode == "hurt" then
      local kind, best = "hit", 1e9
      for _, b in ipairs(s.bikes) do local d = math.abs(b.x - p.x); if d < best then best = d; kind = (b.zone and b.zone.kind) or "bike" end end
      self.cause = { kind, self.T }; self:event("hit", { kind = kind })
    elseif p.mode == "scramble" then self:use("scramble"); self:event("scramble") end
    pv.mode = p.mode
  end
  if s.time > pv.time + 1 then self.cause = { "time", self.T }; self:event("time_up") end
  pv.time = s.time
  local lostHeart = (s.hearts < pv.hearts and s.lives == pv.lives) or s.lives < pv.lives
  if lostHeart then
    local cause = (self.cause and self.T - self.cause[2] < 3) and self.cause[1] or "unknown"
    if cause ~= "time" then self:event("heart_lost", { cause = cause }) end
    if s.lives < pv.lives then self:event("life_lost", { cause = cause }) end
  end
  pv.hearts, pv.lives = s.hearts, s.lives

  -- the magpie, the cat, the ball, the girl
  if s.magpie and s.magpie.i ~= pv.magI then self:event("magpie_flee", { perch = s.magpie.i }); pv.magI = s.magpie.i end
  local bs = s.ball.state
  if bs ~= pv.ball then
    if pv.ball == "magpie" and bs == "air" then self:event("magpie_drop", { perch = s.magpie and s.magpie.i, bx = math.floor(s.ball.x), by = math.floor(s.ball.y) }) end
    if bs == "carried" then self:event("ball_pickup"); self:use("act") end
    if pv.ball == "carried" and bs == "air" then self:event("ball_drop") end
    if pv.ball == "carried" and bs == "home" then self:event("ball_lost") end
    if pv.ball == "home" and bs == "rest" then self:event("ball_home", { bx = math.floor(s.ball.x), by = math.floor(s.ball.y) }) end
    if bs == "given" then self:event("girl_given") end
    pv.ball = bs
  end
  if s.cat and s.cat.state ~= pv.cat then
    if s.cat.state == "scared" then self:event("cat_scared") end
    pv.cat = s.cat.state
  end

  -- mechanics used (the first time): bark, crawl, walk, held jump, riding a moving platform
  if p.barkT == 0.5 then self:use("bark"); self:event("bark") end
  if p.crouch and math.abs(p.vx) > 5 then self:use("crawl") end
  if p.onGround and p.mode == "normal" and not p.crouch and math.abs(p.vx) > 40 and math.abs(p.vx) < 66 and I.down("walk") then self:use("walk") end
  if not p.onGround and p.vy < 0 and p.jumpBase - p.y > 30 then self:use("held") end
  if p.onGround and p.ground then for _, m in ipairs(s.movers) do if p.ground == m then self:use("ride", { mover = m.name }) end end end

  -- standing still for more than a second (while playing, not on a card)
  local stillNow = p.onGround and math.abs(p.vx) < 5 and p.mode == "normal" and not s.deadT and not s.drownT
  if stillNow then
    if not self.still then self.still = { t = self.playT, T = self.T, x = p.x, why = self.activity } end
    if self.activity and not self.still.why then self.still.why = self.activity end
  elseif self.still then
    local d = self.playT - self.still.t
    if d >= 1 then
      local e = self:event("idle", { dur = d, why = self.still.why or "idle" }); e.t = self.still.t; e.x = math.floor(self.still.x)
      e.screen = screenOf(e.x)
    end
    self.still = nil
  end
end

-- a still stretch still open at the end
function L:finish()
  if self.still then
    local d = self.playT - self.still.t
    if d >= 1 then local e = self:event("idle", { dur = d, why = self.still.why or "idle" }); e.t = self.still.t end
    self.still = nil
  end
  if self.cardStart then self.cards[#self.cards + 1] = { kind = self.state, dur = self.T - self.cardStart }; self.cardStart = nil end
end
return L
