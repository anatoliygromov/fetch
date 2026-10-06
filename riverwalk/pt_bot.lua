-- Playtest lab: a persona bot. It plays a level like one of the personas in docs/playtest/personas.json would:
-- the level's route (pt_routes.lua, copied from the autopilot) goes through a persona layer before it reaches the
-- buttons (I.force and love.keypressed, the same way the autopilots press them). See docs/playtest/method.md.
--   timing     a positional step (jump at x) lands N(0, timing_sd) early or late: late = the press waits, early =
--              the step's condition is checked on where Pepper will be (x + vx * lead). A reactive step (the boat,
--              the cart, the ball dropping) waits reaction_ms (+ jitter) first.
--   holds      a held jump comes out as a tap (A let go after 60-160 ms) with chance hold_error, a tap as a held
--              jump (0.3-0.45 s); not knowing that holding A jumps higher, every jump is such a short press
--   knowledge  a mechanic is known from the texts the persona can read (reads: all / short = up to 4 words /
--              none), from an earlier level (campaign mode), or found: after a failure that the unknown mechanic
--              caused (or, for bark and X, at the first moment it is needed) they try buttons for a discovery
--              time (gamma, mean discovery_s), with real random presses, before they find it
--   failure    stuck (a step's condition not met in time, or pushing against something for 1.5 s), a fall in the
--              water, a lost life: they retry from the last lit lamp (the game's own respawn, or a teleport there
--              for a stuck) and the route rewinds to where that lamp was lit. patience failures at one obstacle
--              and they quit there
local I = require("input")
local R = require("pt_routes")
local B = {}
B.__index = B
local DT = 1 / 60

local LEVELS = { "citypark", "downtown", "riverwalk" }
-- the mechanics each level needs; in campaign mode a level starts knowing what the levels before it needed
local NEEDED = {
  citypark = { "held", "walk", "crawl", "bark", "act", "wait_boat", "wait_cart" },
  downtown = { "held", "crawl", "bark", "act", "wait_tram" },
  riverwalk = { "held", "crawl", "act", "wait_pontoon", "wait_bike" },
}
-- carried over to a new kind of the same thing: a moving platform, a hazard to wait out
local SIMILAR = { wait_boat = { "wait_pontoon" }, wait_cart = { "wait_tram", "wait_bike" }, wait_tram = { "wait_cart", "wait_bike" }, wait_pontoon = { "wait_boat" } }
-- what a text teaches (a pattern in the hint, message or intro card)
local TEACH = {
  { "HOLD A", "held" }, { "HOLD B", "walk" }, { "BARK", "bark" }, { "CRAWL", "crawl" }, { "X:", "act" }, { "PICK UP", "act" },
  { "RIDE THE DUCK BOAT", "wait_boat" }, { "RIDE THE PONTOON", "wait_pontoon" }, { "LEAF CART", "wait_cart" }, { "TRAM!", "wait_tram" }, { "BIKES!", "wait_bike" },
}
local function words(s) local n = 0; for _ in s:gmatch("%S+") do n = n + 1 end; return n end

function B.new(api, log, persona, opt)
  local self = setmetatable({ api = api, log = log, P = persona, level = opt.level, seed = opt.seed, mode = opt.fresh and "fresh" or "campaign",
    know = {}, naive = {}, fails = {}, intent = {}, approxT = 0, gameOvers = 0, retries = 0,
    disc = {}, done = false }, B)
  local h = 0
  for c in (persona.id .. opt.level):gmatch(".") do h = (h * 31 + c:byte()) % 1000003 end
  self.rng = love.math.newRandomGenerator(h + opt.seed * 7919)
  self.react = persona.reaction_ms / 1000
  self.sd = persona.timing_sd_ms / 1000
  -- from the bios: Elsa presses Y just for fun, Liam tries every button
  self.funRate = ({ elsa6 = 1 / 10, liam8 = 1 / 20 })[persona.id] or 0
  self.cap = persona.id == "elsa6" and 600 or 1200                 -- Elsa plays 10 minutes
  self.spw = persona.reads == "all" and (persona.age <= 10 and 0.4 or 0.25) or 0
  -- knowledge at the start
  if not opt.fresh then
    for _, lv in ipairs(LEVELS) do
      if lv == opt.level then break end
      for _, m in ipairs(NEEDED[lv]) do
        self:learn(m, "earlier level", true)
        for _, m2 in ipairs(SIMILAR[m] or {}) do self:learn(m2, "earlier level", true) end
      end
    end
  end
  self.def = require("level." .. opt.level)
  if persona.reads == "all" then for i = 1, 4 do self:read(self.def.intro[i] or "", "intro card", true) end end
  self.knowStart = {}
  for k, v in pairs(self.know) do self.knowStart[k] = v.how end
  -- the route, its optional parts chosen once for the run
  self.route, self.picks = R.build(opt.level, function(name, hasRush)
    if persona.rush then return hasRush and "rush" or "skip" end
    return (self.rng:random() < persona.explore) and "take" or "skip"
  end)
  self.i, self.phase, self.stepT = 1, "cond", 0
  self.j = self:jitter()
  self.nextFun = self.funRate > 0 and self:expo(1 / self.funRate) or 1e9
  log.onEvent = function(e) self:onEvent(e) end
  I.testing = true; I.force = {}
  return self
end

-- random numbers
function B:normal(sd) return self.rng:randomNormal(sd, 0) end
function B:expo(mean) return -mean * math.log(1 - self.rng:random()) end
function B:jitter() return self:normal(self.sd) end
function B:reaction() return math.max(0.1 * self.react, self.react + self:normal(self.sd)) end
function B:discoveryTime() return math.max(2, self:expo(self.P.discovery_s / 2) + self:expo(self.P.discovery_s / 2)) end   -- gamma(2)

-- knowledge
function B:known(m) return self.know[m] ~= nil end
function B:learn(m, how, quiet)
  if self.know[m] then return end
  self.know[m] = { how = how, t = self.log.playT }
  if not quiet then self.log:event("learned", { mech = m, how = how }) end
end
function B:canRead(text) return self.P.reads == "all" or (self.P.reads == "short" and words(text) <= 4) end
function B:read(text, src, quiet)
  if not self:canRead(text) then return end
  for _, t in ipairs(TEACH) do if text:find(t[1], 1, true) then self:learn(t[2], src .. ": " .. text, quiet) end end
end
function B:onEvent(e)
  if e.type == "hint" then self:read(e.text, e.say and "message" or "hint") end
  if e.type == "magpie_flee" and not self:known("walk") and not self.walkAt then        -- it flew off: they keep at it
    self.walkAt = self.log.playT + self:discoveryTime()
    self.disc[#self.disc + 1] = { mech = "walk", from = self.log.playT, ob = "magpie", background = true }
  end
  if (e.type == "magpie_drop" or e.type == "cat_scared") and not self:known("bark") then self:learn("bark", "a bark worked") end
  if e.type == "ball_pickup" and not self:known("act") then self:learn("act", "X worked") end
  if e.type == "heart_lost" and (e.cause == "bike" or e.cause == "cart" or e.cause == "tram") then self:learn("wait_" .. e.cause, "hit by one") end
end

-- the buttons: what the route (intent) or a controller (ctlKeys) wants, through the persona's hands
local function set(...) local t = {}; for _, k in ipairs({ ... }) do t[k] = true end; return t end
function B:ctl()
  if self._ctl then return self._ctl end
  local bot = self
  local c = {}
  function c.hold(...) bot.intent = set(...) end
  function c.release() bot.intent = {} end
  function c.jump(...) bot.intent = set(...); bot.intent.jump = true; bot:pressJump(false) end
  function c.hop(...) bot.intent = set(...); bot:pressJump(true) end
  function c.key(name) bot:pressKey(name) end
  self._ctl = c
  return c
end
function B:pressJump(tap)
  local now = self.log.T
  local jp = { t0 = now, tap = tap, ob = self:ob() }
  if tap then
    jp.dur = 2 * DT
    if self.rng:random() < self.P.hold_error then jp.dur = 0.3 + 0.15 * self.rng:random(); jp.err = true end
  else
    if not self:known("held") then jp.cut = now + 0.06 + 0.1 * self.rng:random(); jp.naive = true
    elseif self.rng:random() < self.P.hold_error then jp.cut = now + 0.06 + 0.1 * self.rng:random(); jp.err = true end
  end
  self.log:event("jump", { tap = tap })
  if jp.err then self.log:event("hold_error", { tap = tap, ob = jp.ob }) end
  self.jp = jp
  love.keypressed("space")
end
function B:pressKey(name)
  if not self:known(name) then                                       -- they do not know this button yet
    self.needKey = name; return
  end
  love.keypressed(name == "bark" and "z" or "x")
end
function B:applyButtons()
  local now = self.log.T
  local keys = (self.fid and self.fid.keys) or self.ctlKeys or self.intent
  local f = {}
  for k in pairs(keys) do f[k] = true end
  if not self.fid then
    if f.down and not self:known("crawl") then f.down = nil; self.naive.crawl = self:ob() end
    if f.walk and not self:known("walk") then f.walk = nil end
  end
  local jp = self.jp
  if jp and not self.fid and not self.ctlKeys then
    if jp.tap then f.jump = (now - jp.t0 < jp.dur) or nil
    elseif jp.cut and now >= jp.cut and f.jump then
      f.jump = nil
      if jp.naive and not jp.noted then jp.noted = true; self.naive.held = jp.ob end
    end
  end
  I.force = f
end

-- the obstacle being played (for retries and quits)
function B:ob()
  if self.ctlOb then return self.ctlOb end
  local st = self.route[self.i]
  return st and st.ob or "end"
end

-- the route: advance to the next step
local DEBUG = os.getenv("PT_DEBUG")
local TRACE = os.getenv("PT_TRACE")       -- PT_DEBUG / PT_TRACE: print the route steps / every step (debugging)
function B:advance()
  if DEBUG then local p = self.api.stage().pepper; print(("step %d -> %d  t %.2f x %.1f y %.1f vx %.0f %s"):format(self.i, self.i + 1, self.log.playT, p.x, p.y, p.vx, p.onGround and "G" or "A")) end
  self.i = self.i + 1; self.phase = "cond"; self.stepT = self.log.T; self.j = self:jitter()
  self.ontoTries, self.ontoShift = 0, nil
  local st = self.route[self.i]
  if st and st.ob and (not self.group or self.group.ob ~= st.ob) then     -- the start of an obstacle: a retry backs up to here
    local p = self.api.stage().pepper
    local h = {}; for k in pairs(self.intent) do if k ~= "jump" then h[k] = true end end
    self.group = { ob = st.ob, i = self.i, x = p.x, y = p.y, intent = h }
  end
end
-- where a moving platform (its left edge x0 and direction) will be t s from now: it turns at its ends
function B.predict(m, t)
  local x, d, rem = m.x0, m.dir, m.speed * t
  for _ = 1, 20 do
    if rem <= 0 then break end
    local lim = d > 0 and (m.to - x) or (x - m.from)
    if rem <= lim then x = x + d * rem; rem = 0 else x = x + d * lim; rem = rem - lim; d = -d end
  end
  return x, d
end
-- which way through an optional part: the run's pick, decided on the spot (dyn), the short way once given up
function B:variant(st, s, p)
  if self.abandoned and self.abandoned[st.branch] then return "skip" end
  if st.dyn then return st.dyn(s, p, st.pick) and "take" or "skip" end
  return st.at[st.pick] and st.pick or "skip"
end
-- jump to step k (a branch or the end of a taken branch)
function B:goStep(k) self.i = k - 1; self:advance() end
function B:limit(st) return (st.lim or 6) * 1.5 + self.react + 1 end

-- start trying buttons to find mechanics (fiddling): ms = list of mechanics, effect = ends it early if true
function B:fiddle(ms, ob, effect, after)
  local p = self.api.stage().pepper
  local d = self:discoveryTime()
  self.fid = { ms = ms, ob = ob, from = self.log.T, untilT = self.log.T + d, anchor = p.x, nextT = self.log.T, keys = {}, effect = effect, after = after }
  for _, m in ipairs(ms) do self.disc[#self.disc + 1] = { mech = m, from = self.log.playT, ob = ob } end
  self.log:event("fiddle", { mechs = table.concat(ms, ","), ob = ob, planned = d })
  self.log.activity = "trying buttons"
end
function B:fiddleTick(s, p)
  local f, now, r = self.fid, self.log.T, self.rng
  if (f.effect and f.effect(s, p)) or now >= f.untilT then
    local byEffect = f.effect and f.effect(s, p)
    for _, m in ipairs(f.ms) do self:learn(m, byEffect and "found by trying (it worked)" or "found by trying") end
    for _, d in ipairs(self.disc) do if not d.dur and d.ob == f.ob then d.dur = self.log.playT - d.from end end
    self.log:event("found", { mechs = table.concat(f.ms, ","), ob = f.ob, dur = now - f.from })
    self.fid = nil; self.log.activity = nil; I.force = {}
    if f.after then f.after(byEffect) end
    return
  end
  if now >= f.nextT then                                           -- a new random try
    f.nextT = now + 0.25 + 0.65 * r:random()
    local dir = (p.x < f.anchor - 24) and "right" or ((p.x > f.anchor + 24) and "left" or (r:random() < 0.5 and "left" or "right"))
    local w = s.world                                               -- they can see the water and the edge: no trying towards them
    if w:inWater(p.x + (dir == "right" and 48 or -48), p.y + 8) or not w:floor(p.x + (dir == "right" and 30 or -30) - 1, p.x + (dir == "right" and 30 or -30) + 1, p.x, p.y - 30, p.y + 6, p.y - 30) then
      dir = dir == "right" and "left" or "right"
    end
    local a = r:random(1, 9)
    f.keys = {}
    if a == 1 then f.keys[dir] = true
    elseif a == 2 then love.keypressed("space")
    elseif a == 3 then f.keys.jump = true; love.keypressed("space")
    elseif a == 4 then f.keys.walk = true; f.keys[dir] = true
    elseif a == 5 then love.keypressed("z")
    elseif a == 6 then f.keys.down = true
    elseif a == 7 then if not (p.carrying and self:known("act")) then love.keypressed("x") end   -- knowing X drops the ball, not while carrying it
    elseif a == 8 then f.keys.down = true; f.keys[dir] = true end
  elseif now >= f.nextT - 0.15 then f.keys = {} end                 -- let go before the next try
end

-- a failure at the current obstacle: count it, quit or learn, retry from the last lamp
function B:failure(cause, respawned)
  local s, p = self.api.stage(), self.api.stage().pepper
  local ob = self:ob()
  self.fails[ob] = (self.fails[ob] or 0) + 1
  self.retries = self.retries + 1
  self.log:event("retry", { ob = ob, cause = cause, n = self.fails[ob] })
  if self.fails[ob] >= self.P.patience then
    if self.optActive then return self:abandon() end                -- an optional detour: they give up on it, not the level
    return self:quit(ob, cause)
  end
  local st = self.route[self.i]
  if st and st.w and not self:known("wait_" .. st.w) then self:learn("wait_" .. st.w, "learned by failing") end
  local ms = {}
  for m, o in pairs(self.naive) do
    if o == ob and not self:known(m) then
      if m:sub(1, 5) == "wait_" then self:learn(m, "learned by failing")     -- waiting: the fall itself teaches it
      else ms[#ms + 1] = m end
    end
  end
  table.sort(ms)
  self.naive = {}
  self.ctlKeys, self.ctlOb, self.mag, self.fetch, self.jp, self.needKey = nil, nil, nil, nil, nil, nil
  local function retry()
    local g = self.group
    self.backupTries = (self.lastBackupOb == ob) and (self.backupTries or 0) + 1 or 1
    self.lastBackupOb = ob
    if not respawned and g and g.ob == ob and p.onGround and p.mode == "normal" and math.abs(p.y - g.y) < 4 and math.abs(p.x - g.x) < 300
       and math.abs(p.x - g.x) >= 12 and self.backupTries <= 2 then
      self.backup = { g = g, t = self.log.T }                      -- back up to where the obstacle started, try again
      self.log.activity = "backing up"
      return
    end
    if not respawned then
      local d = math.abs(p.x - s.check.x)
      self.approxT = self.approxT + d / 120                       -- walking back to the lamp to try again
      s:respawn()
    end
    self:rewind()
  end
  if #ms > 0 then self:fiddle(ms, ob, nil, retry) else retry() end
end
-- give up an optional detour (its bones): back to the lamp, on past it
function B:abandon()
  local name = self.optActive
  self.optActive = nil
  self.log:event("gave_up", { opt = name, ob = self:ob() })
  self.abandoned = self.abandoned or {}
  self.abandoned[name] = true
  local s = self.api.stage()
  local p = s.pepper
  self.naive, self.ctlKeys, self.ctlOb, self.mag, self.fetch, self.jp, self.backup = {}, nil, nil, nil, nil, nil, nil
  s:respawn(); self:rewind()                                           -- back to the lamp, on the short way past it
end
function B:rewind()
  local s = self.api.stage()
  -- back at the lamp (or the start): the route goes on from the first obstacle ahead of it
  local li = 0
  for i, l in ipairs(s.lamps) do if l.lit and l.x == s.check.x and l.y == s.check.y then li = i end end
  local target, opt = 1, nil
  if li > 0 then                                                    -- walk the route as it would be played from here
    local k, p = 1, s.pepper
    target = #self.route
    while k <= #self.route do
      local st = self.route[k]
      if st.branch then
        local v = self:variant(st, s, p)
        opt = (v == "take" and (not st.dyn or p.carrying)) and st.branch or nil
        k = st.at[v] or st.at.skip
      elseif st.go then k = st.go; opt = nil
      elseif st.segEnd then opt = nil; k = k + 1
      elseif (st.sync and st.sync >= s.check.x - 12) or st.give then target = k; break
      else k = k + 1 end
    end
  end
  self.i = target
  self.intent = li > 0 and { right = true } or {}
  self.optActive = opt
  self.mag, self.fetch, self.ctlKeys, self.ctlOb, self.give, self.backup = nil, nil, nil, nil, nil, nil
  self.needBall = false
  for k = 1, self.i - 1 do if self.route[k].needBall then self.needBall = true end end
  -- a run-up: back at the lamp, they step back a little (up to 48 px, never off a ledge) before going again,
  -- as the route's jump points assume she arrives running
  local p, w = s.pepper, s.world
  local x = p.x
  for k = 1, 12 do
    local nx = p.x - 4 * k
    local function ground(gx) return w:floor(gx - 1, gx + 1, gx, p.y - 4, p.y + 4, p.y - 4) end
    if nx < 20 or not ground(nx) or not ground(nx - 16) or w:inWater(nx - 16, p.y + 2) or w:solidIn(nx - 17, nx + 17, p.y - 24, p.y - 2) then break end
    x = nx
  end
  local st = self.route[self.i]
  self.group = { ob = st and st.ob or "start", i = self.i, x = x, y = p.y, intent = self.intent }
  if x < p.x - 8 then self.backup = { g = self.group, t = self.log.T, runup = true } end
end
function B:quit(ob, cause)
  local p = self.api.stage().pepper
  self.result = "quit"
  self.quitInfo = { ob = ob, cause = cause, x = math.floor(p.x), screen = math.floor(p.x / 320) + 1 }
  self.log:event("quit", self.quitInfo)
  self.done = true
end

-- the magpie (City Park): sneak up (if they know B) and bark (if they know Y); otherwise they just play on and it
-- flies ahead, perch to perch, to its last perch where it stays
function B:magpieTick(s, p)
  local m, b = s.magpie, s.ball
  if not m or b.state ~= "magpie" or m.state ~= "perch" then self.mag = nil; return false end
  local d = s.def.magpie
  local dx = m.x - p.x
  local ad = math.abs(dx)
  local last = m.i == #d.perches
  local mg = self.mag
  if not mg then
    local onPath = p.onGround and p.mode == "normal" and p.y >= 176 and not (p.ground and p.ground.from)
    if self:known("walk") and dx > -60 and dx < 200 and onPath and not (self.noSneak == m.i) then
      mg = { phase = "sneak", t = self.log.T, bd = 70 + 15 * self.rng:random(), perch = m.i }
      self.log:event("sneak", { perch = m.i })
    elseif (last or self:known("walk")) and ad <= 88 and math.abs(m.y - p.y) < 100 and p.onGround and p.mode == "normal" then
      mg = { phase = "stop", t = self.log.T, perch = m.i }
    else return false end
    self.mag = mg
  end
  self.ctlOb = "magpie"
  self.log.activity = "magpie"
  local now = self.log.T
  if mg.phase == "sneak" then
    if ad <= mg.bd and math.abs(m.y - p.y) < 100 then mg.phase, mg.t = "stop", now
    else
      self.ctlKeys = { [dx > 0 and "right" or "left"] = true, walk = true }
      if math.abs(p.vx) < 1 and p.onGround and now - mg.t > 0.5 then mg.blocked = (mg.blocked or 0) + DT else mg.blocked = 0 end
      if mg.blocked > 0.4 then
        if ad <= 95 then mg.phase, mg.t = "stop", now
        else self.noSneak = m.i; self.mag = nil; self.ctlKeys = nil; self.ctlOb = nil; return false end
      end
    end
  end
  if mg.phase == "stop" then
    self.ctlKeys = {}
    if not mg.barkAt then mg.barkAt = now + self:reaction() end
    if now >= mg.barkAt then
      if not self:known("bark") then
        self.mag = nil; self.ctlKeys = {}
        self:fiddle({ "bark" }, "magpie", function(st) return st.ball.state ~= "magpie" end, function(ok) if not ok then love.keypressed("z") end end)
        return true
      end
      love.keypressed("z"); mg.phase, mg.t, mg.tries = "barked", now, (mg.tries or 0) + 1
    end
  elseif mg.phase == "barked" and now - mg.t > 0.6 then
    if mg.tries < 3 then mg.phase, mg.barkAt = "stop", nil
    else self.noSneak = m.i; self.mag = nil; self.ctlKeys = nil; self.ctlOb = nil; return false end
  end
  return true
end

-- the ball: walk up to it and press X where it lies on Pepper's level; where it lies off the route (up a tree,
-- behind her) the human cost of fetching it is approximated (see method.md) and Pepper is given the ball
function B:wantBall(s)
  local b = s.ball
  if b.state ~= "rest" or s.pepper.carrying then return false end
  if s.cat and s.cat.state == "sit" then return false end
  return true
end
function B:isLocal(s, p, b)
  if not (p.onGround and p.mode == "normal") or (p.ground and p.ground.from) then return false end
  if math.abs(b.y - p.y) >= 22 or math.abs(b.x - p.x) >= 160 then return false end
  local x0, x1 = math.min(p.x, b.x), math.max(p.x, b.x)
  return not s.world:solidIn(x0 + 1, x1 - 1, p.y - 20, p.y - 2)
end
function B:approxFetch(s, p)
  local b = s.ball
  local dx, up, down = math.abs(b.x - p.x), math.max(0, p.y - b.y), math.max(0, b.y - p.y)
  local cost = 2 * (dx + up + down) / 100 + 2 * self:reaction()
  local jumps = math.ceil(up / 30)
  local pfail = self:known("held") and self.P.hold_error or 0.7
  local missed = 0
  for _ = 1, jumps do
    cost = cost + 0.8
    while self.rng:random() < pfail do
      missed = missed + 1; cost = cost + 1.5
      if missed >= self.P.patience then
        self.approxT = self.approxT + cost
        self.log:event("fetch_approx", { cost = cost, dx = math.floor(dx), up = math.floor(up), missed = missed, bx = math.floor(b.x), by = math.floor(b.y), ok = false })
        self.fails.ball = (self.fails.ball or 0) + missed
        return self:quit("ball (fetching it)", "missed jumps")
      end
    end
  end
  self.approxT = self.approxT + cost
  s.time = s.time - cost
  self.log:event("fetch_approx", { cost = cost, dx = math.floor(dx), up = math.floor(up), missed = missed, bx = math.floor(b.x), by = math.floor(b.y), ok = true })
  b.state = "carried"; p.carrying = b
end
function B:fetchTick(s, p, forced)
  local b = s.ball
  if not self:wantBall(s) then
    if self.fetch then self.fetch = nil; self.ctlKeys = nil; self.ctlOb = nil end
    return false
  end
  local now = self.log.T
  local fe = self.fetch
  if not fe then
    if self:isLocal(s, p, b) then
      fe = { t = now }; self.fetch = fe
    elseif p.onGround and p.mode == "normal" and (forced or self.needBall or b.x < p.x - 40) then
      self:approxFetch(s, p); return true
    else return false end
  end
  self.ctlOb = "ball"; self.log.activity = "fetching the ball"
  if now - fe.t > 10 then                                          -- could not get to it: fetch it the long way
    self.fetch = nil; self.ctlKeys = nil; self.ctlOb = nil
    self:approxFetch(s, p); return true
  end
  local want = p.x < b.x and 1 or -1
  local dir = want > 0 and "right" or "left"
  local walk = self:known("walk")
  if fe.pressAt then
    self.ctlKeys = {}
    if now >= fe.pressAt and not fe.pressed then
      fe.pressed = now
      if not self:known("act") then
        self.fetch = nil; self.ctlKeys = {}
        self:fiddle({ "act" }, "ball", function(st, pp) return pp.carrying ~= nil end, function(ok) if not ok then love.keypressed("x") end end)
        return true
      end
      love.keypressed("x")
    end
    if fe.pressed and now - fe.pressed > 0.5 then fe.pressAt, fe.pressed = nil, nil end   -- missed: line up again
    return true
  end
  if p.face == want and math.abs(p.x + p.face * 18 - b.x) < 20 and math.abs(p.vx) < 1 then
    fe.pressAt = now + self:reaction(); self.ctlKeys = {}; return true
  end
  local tx = b.x - want * 18
  local k = {}
  if p.face ~= want then k[dir] = true
  elseif math.abs(p.x - tx) > 3 then
    local d = p.x < tx and "right" or "left"
    if walk or math.abs(p.x - tx) > 24 then k[d] = true
    elseif (self.log.step % 8) == 0 then k[d] = true end           -- not knowing B: little taps on the d-pad
  end
  if walk then k.walk = true end
  self.ctlKeys = k
  return true
end

-- the last step: give the girl the ball
function B:giveTick(s, p, st)
  local g = s.girl
  if not p.carrying then self.needBall = true; return end
  self.needBall = false
  local now = self.log.T
  local gv = self.give or { t = now }
  self.give = gv
  if not (p.onGround and p.y >= 183 and p.x >= g.x - 40) then
    self.intent = { right = true }
    if now - gv.t > self:limit(st) then self.give = nil; self:failure("stuck", false) end
    return
  end
  self.intent = {}
  if not gv.pressAt then gv.pressAt = now + self:reaction() end
  if now >= gv.pressAt and not gv.pressed then
    gv.pressed = now
    if not self:known("act") then
      self.give = nil
      self:fiddle({ "act" }, "girl", function(st2) return st2.ball.state == "given" end, function(ok) if not ok then love.keypressed("x") end end)
      return
    end
    love.keypressed("x")
  end
  if gv.pressed and now - gv.pressed > 1.0 and s.ball.state ~= "given" then gv.pressAt, gv.pressed = nil, nil end
end

-- River Walk's onto(x0, top, fromX1): onto a box from the pavement, or over from the box she stands on
function B:ontoTick(s, p, st)
  local o = st.onto
  if p.onGround and math.abs(p.y - o.top) < 1 and p.x > o.x0 - 13 then self:ctl().hold("right"); self:advance(); return end
  if self.log.T - self.stepT > self:limit(st) then return self:failure("stuck", false) end
  if p.onGround and p.mode == "normal" and p.x < o.x0 - 10 then
    if not self.ontoShift then self.ontoShift = 120 * self:jitter() end
    local blocked = self.intent.right and math.abs(p.vx) < 1 and self.ontoTries > 0
    if (p.y > 183 and (p.x >= o.x0 - 46 + self.ontoShift or (blocked and p.x >= o.x0 - 30))) or (o.fromX1 and p.y < 183 and p.x >= o.fromX1 - 12 + self.ontoShift) then
      self.ontoTries = (self.ontoTries or 0) + 1
      self.ontoShift = nil
      if self.ontoTries > 1 then
        local ob = st.ob
        self.fails[ob] = (self.fails[ob] or 0) + 1; self.retries = self.retries + 1
        self.log:event("retry", { ob = ob, cause = "missed jump", n = self.fails[ob] })
        if self.fails[ob] >= self.P.patience then return self:quit(ob, "missed jump") end
        if self.naive.held == ob and not self:known("held") then
          self.naive = {}
          return self:fiddle({ "held" }, ob, nil, function() end)
        end
      end
      self:ctl().jump("right")
    else self.intent = { right = true } end
  end
end

-- backing up to the start of the obstacle (a stuck, Pepper still on the same level): real walking, real time
function B:backupTick(s, p)
  local bu, now = self.backup, self.log.T
  local g = bu.g
  local function resume()
    self.backup = nil; self.log.activity = nil; self.ctlKeys = nil
    self.i = g.i; self.phase, self.stepT, self.j = "cond", now, self:jitter()
    self.intent = {}; for k in pairs(g.intent) do self.intent[k] = true end
    self.ontoTries, self.ontoShift, self.mag, self.fetch, self.give = 0, nil, nil, nil, nil
  end
  if math.abs(p.vx) < 1 and now - bu.t > 0.4 and math.abs(p.x - g.x) > 8 then bu.blocked = (bu.blocked or 0) + DT else bu.blocked = 0 end
  if now - bu.t > 6 or p.mode ~= "normal" or bu.blocked > 0.5 then  -- that did not work
    if bu.runup then return resume() end                            -- (a run-up: just go from here)
    self.backup = nil; self.log.activity = nil; self.ctlKeys = nil
    s:respawn(); self:rewind(); return
  end
  local dx = g.x - p.x
  if math.abs(dx) <= 8 then
    self.ctlKeys = {}
    if math.abs(p.vx) < 5 then return resume() end
    return
  end
  local dir = dx > 0 and "right" or "left"
  if math.abs(dx) > 40 then self.ctlKeys = { [dir] = true }
  elseif self:known("walk") then self.ctlKeys = { [dir] = true, walk = true }
  else self.ctlKeys = ((self.log.step % 6) < 2) and { [dir] = true } or {} end   -- little taps
end

-- stuck, but a later step of the route is already true (she jumped over the log instead of onto it, she is past
-- the obstacle another way): a player just goes on from there, no retry
function B:resync(s, p)
  for k = self.i + 1, math.min(#self.route, self.i + 8) do
    local st = self.route[k]
    if st.branch or st.go or st.give or st.fetch or st.onto or st.needBall then break end
    if st.sync and st.c and p.onGround and st.c(p, s) then
      self.log:event("resync", { from = self.i, to = k, ob = st.ob })
      self.i = k - 1; self:advance(); return true
    end
  end
  return false
end

-- a hazard coming (a bike): stop on the perch until it has passed (if they know to)
function B:hazardWaitTick(s, p, st)
  local now = self.log.T
  local function go() self.hwSeen, self.hwGo = nil, nil; self.intent = { right = true }; self.log.activity = nil; self:advance() end
  if not self:known("wait_" .. st.w) then self.naive["wait_" .. st.w] = st.ob; return go() end
  if now - self.stepT > self:limit(st) then return go() end
  local b = s.bikes[1]
  if b and b.x > p.x - 40 then
    self.hwGo = nil
    if not self.hwSeen then self.hwSeen = now + self:reaction() end
    if now >= self.hwSeen then self.intent = {}; self.log.activity = "waiting: " .. st.w end
  elseif self.hwSeen then
    if not self.hwGo then self.hwGo = now + self:reaction() end
    if now >= self.hwGo then go() end
  else go() end
end

-- one step of the route
function B:routeTick(s, p)
  local st = self.route[self.i]
  if not st then return end
  local now = self.log.T
  if st.branch then
    local v = self:variant(st, s, p)
    self.optActive = (v == "take" and (not st.dyn or p.carrying)) and st.branch or nil
    return self:goStep(st.at[v] or st.at.skip)
  end
  if st.segEnd then self.optActive = nil; return self:advance() end
  if st.go then return self:goStep(st.go) end
  if st.wait then if now - self.stepT >= st.wait then self:advance() end; return end
  if st.needBall then self.needBall = true; self:advance(); return end
  if st.give then return self:giveTick(s, p, st) end
  if st.fetch then
    if p.carrying then self:advance(); return end
    if now - self.stepT > 25 then return self:failure("stuck", false) end
    return
  end
  if st.onto then return self:ontoTick(s, p, st) end
  if st.hw then return self:hazardWaitTick(s, p, st) end
  if self.phase == "cond" then
    local c = st.c
    local naiveWait = st.w and not self:known("wait_" .. st.w)
    local q, qs, delay = p, s, nil
    local react = st.r
    if type(react) == "function" then react = react(p, s) end
    if st.mv and not naiveWait then                                   -- a moving platform: they time it
      local L = st.mv(p) - self.j
      if L > 0 then
        local m = s.movers[1]
        local x0, dir = B.predict(m, L)
        local pm = setmetatable({ x0 = x0, dir = dir }, { __index = m })
        qs = setmetatable({ movers = { pm } }, { __index = s })
        delay = 0
      else delay = -L end
    elseif self.j < 0 and not react then q = setmetatable({ x = p.x + p.vx * (-self.j) }, { __index = p }) end
    if naiveWait or c(q, qs) then
      if naiveWait then self.naive["wait_" .. st.w] = st.ob end
      self.phase = "pending"
      self.pendT = now + (delay or (react and self:reaction() or math.max(0, self.j)))
      if react then self.log.activity = "reacting" end
    elseif now - self.stepT > self:limit(st) then if not self:resync(s, p) then return self:failure("stuck", false) end
    else
      local dirHeld = self.intent.right or self.intent.left
      if dirHeld and p.onGround and p.mode == "normal" and math.abs(p.vx) < 1 then self.blockT = (self.blockT or 0) + DT else self.blockT = 0 end
      if self.blockT > 1.5 + self.react then self.blockT = 0; if not self:resync(s, p) then return self:failure("stuck", false) end end
      if not (st.r or st.w) and p.onGround and p.mode == "normal" and math.abs(p.vx) < 1 and not dirHeld then self.stillT = (self.stillT or 0) + DT else self.stillT = 0 end
      if self.stillT > 2.5 + self.react then self.stillT = 0; if not self:resync(s, p) then return self:failure("stuck", false) end end
      if st.w then self.log.activity = "waiting: " .. st.w end
    end
  end
  if self.phase == "pending" and now >= self.pendT then
    self.log.activity = nil
    st.a(self:ctl(), p, s)
    self:advance()
    if self.needKey then                                             -- a button they do not know: find it
      local k = self.needKey; self.needKey = nil
      local eff = k == "bark" and function(s2) return (s2.cat and s2.cat.state ~= "sit") or (s2.magpie and s2.ball.state ~= "magpie") end
        or function(s2, p2) return p2.carrying ~= nil or s2.ball.state == "given" end
      self:fiddle({ k }, st.ob, eff, function(ok) if not ok then love.keypressed(k == "bark" and "z" or "x") end end)
    end
  end
end

-- cards: the intro (read or skipped), the tally after GOOD GIRL!
function B:cardTime(lines)
  local n = 0
  for _, l in ipairs(lines or {}) do n = n + words(l) end
  if self.P.rush then return 0.6 end
  if self.P.reads == "all" then return 1.0 + n * self.spw end
  return self.P.reads == "short" and 0.8 or 1.2
end

function B:tick()
  if self.done then return end
  local api, log = self.api, self.log
  local st = api.getState()
  local now = log.T
  if st == "intro" then
    if not self.introAt then self.introAt = now + math.max(0.6, self:cardTime({ self.def.intro[3], self.def.intro[4] }) + (self.gameOvers > 0 and -0.5 or 0)) end
    if now >= self.introAt then love.keypressed("space"); self.introAt = nil end
    return
  elseif st == "clear" then
    local ta = api.tally()
    if ta and ta.done then
      if not self.leaveAt then self.leaveAt = now + self:reaction() + 0.3 end
      if now >= self.leaveAt then self.result = "clear"; self.done = true end
    end
    return
  elseif st == "over" then
    if not self.overAt then self.overAt = now + 2; self.gameOvers = self.gameOvers + 1 end
    if now >= self.overAt then
      self.overAt = nil
      local ob = self:ob()
      self.fails[ob] = (self.fails[ob] or 0) + 1
      if self.fails[ob] >= self.P.patience then return self:quit(ob, "game over") end
      api.newRun()                                                 -- they start the level again
      self.i, self.phase, self.stepT, self.intent = 1, "cond", now, {}
      self.needBall, self.mag, self.fetch, self.fid, self.ctlKeys, self.ctlOb, self.give = false, nil, nil, nil, nil, nil, nil
      self.backup, self.group, self.noSneak, self.jp = nil, nil, nil, nil
      self.introAt, self.lastTime, self.dying = nil, nil, nil
    end
    return
  elseif st ~= "play" then return end

  local s = api.stage(); local p = s.pepper
  log.curOb = self:ob()
  if TRACE then local m = s.movers[1]; print(("TR %.2f i %d x %.1f y %.1f vx %.0f %s mv %.1f keys %s"):format(log.playT, self.i, p.x, p.y, p.vx, p.onGround and "G" or "A", m and m.x0 or 0, table.concat((function() local t = {} for k in pairs(I.force) do t[#t + 1] = k end return t end)(), "+"))) end
  if log.playT > self.cap then self.result = "cap"; self.log:event("quit", { ob = self:ob(), cause = "session over", x = math.floor(p.x), screen = math.floor(p.x / 320) + 1 }); self.quitInfo = { ob = self:ob(), cause = "session over", x = math.floor(p.x), screen = math.floor(p.x / 320) + 1 }; self.done = true; return end
  -- the game's own failures: in the water, a life lost, time up; the game puts her back at the lamp
  if p.mode == "drown" or s.deadT or s.drownT then
    if not self.dying then self.dying = (p.mode == "drown") and "water" or "life lost" end
    self.ctlKeys, self.fid, self.jp, self.backup = {}, nil, nil, nil; self.log.activity = nil
    self:applyButtons(); return
  end
  if self.dying then
    local cause = self.dying; self.dying = nil
    self:failure(cause, true)
    if self.done then return end
  end
  if self.lastTime and s.time > self.lastTime + 1 then self:failure("time up", true); if self.done then return end end
  self.lastTime = s.time
  if self.walkAt and self.log.playT >= self.walkAt then
    self.walkAt = nil; self:learn("walk", "found by trying (while chasing the magpie)")
    for _, d in ipairs(self.disc) do if d.mech == "walk" and not d.dur then d.dur = self.log.playT - d.from end end
  end
  -- fun barks (Elsa, Liam)
  if now >= self.nextFun then
    self.nextFun = now + self:expo(1 / self.funRate)
    if p.mode == "normal" and not self.fid then love.keypressed("z"); log:event("fun_bark") end
  end

  if self.backup then self:backupTick(s, p)
  elseif self.fid then self:fiddleTick(s, p)
  elseif self:fetchTick(s, p, self.route[self.i] and self.route[self.i].fetch) then
  elseif s.magpie and self:magpieTick(s, p) then
  else
    if self.ctlKeys then self.ctlKeys = nil; self.ctlOb = nil; self.stepT = now; self.log.activity = nil end
    self:routeTick(s, p)
  end
  if not self.done then self:applyButtons() end
end

-- the run's summary for results.json
function B:summary()
  local s, log = self.api.stage(), self.log
  local gold, goldTotal = 0, 0
  for _, b in ipairs(s.bones) do if b.super then goldTotal = goldTotal + 1; if b.taken then gold = gold + 1 end end end
  local hearts, lives = 0, 0
  for _, e in ipairs(log.events) do if e.type == "heart_lost" then hearts = hearts + 1 end; if e.type == "life_lost" then lives = lives + 1 end end
  local cards = 0
  for _, c in ipairs(log.cards) do cards = cards + c.dur end
  local story = self.def.outro and self:cardTime(self.def.outro) or 0
  local know = {}
  for k, v in pairs(self.know) do know[k] = v.how end
  return { persona = self.P.id, level = self.level, seed = self.seed, mode = self.mode, result = self.result or "stall",
    play_time = log.playT, card_time = cards, story_card_est = story, approx_time = self.approxT,
    total_time = log.playT + cards + story + self.approxT, steps = log.step,
    bones = s.taken, bones_total = s.total, gold = gold, gold_total = goldTotal, hearts_lost = hearts, lives_lost = lives,
    game_overs = self.gameOvers, retries = self.retries, fails = self.fails, quit = self.quitInfo, picks = self.picks,
    knowledge_start = self.knowStart, knowledge_end = know, discoveries = self.disc, events = log.events }
end
return B
