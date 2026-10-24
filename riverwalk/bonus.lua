-- FETCH FRENZY: the golden bone bonus round (the plan's Timon and Pumbaa stages). One screen of City Park lawn,
-- 30 seconds: Mia stands on the left and throws balls, sticks and frisbees; Pepper catches them.
--   Opens:     after a level's tally when Pepper found at least one of its golden bones (Flow.bonusOpen), before
--              the story card. --bonus starts it directly; --level X --bonus plays level X's round.
--   Pepper:    her real controller and physics (pepper.lua, unchanged), on a flat lawn at y 184, the screen's
--              edges as walls: run, walk, tap hop, held jump, crawl.
--   Mia:       throws every item with a throwing animation (her wave clip winds up, the cheer clip's open arms
--              let go). Nothing moves by itself: an item is in her hand until she throws it.
--   Items:     ball (bounces, rolls), stick (spins, drops flat), frisbee (glides slowly). Each has its own
--              gravity; B.flight simulates a throw with the same step the game uses (the tests use it too).
--   Catching:  Pepper's body box touching an item. In the air: CATCH, +100. After it touched the ground
--              (bouncing, rolling or lying there): PICK UP, +50. Both count as catches. An item that leaves the
--              screen is lost; one lying still on the lawn for 3 s fades away (lost).
--   Variants:  three throw lists (A ball rally, B sticks, C frisbees), picked by the level's number:
--              1 and 4 A, 2 and 5 B, 3 C, so two levels in a row never play the same round.
--   Result:    catches, points, and an extra life for B.LIFE_AT (11) catches or more (tuned with a model child,
--              see tests_bonus.lua: about half of the model runs get it).
local Pp = require("pepper")
local Wd = require("world")
local S = require("sfx")
local U = require("hud")
local lg = love.graphics
local B = { TIME = 30, FEET = 184, LIFE_AT = 11, AIR = 100, GROUND = 50, MIA_X = 34, REST = 3, DT = 1 / 60 }
B.__index = B

-- how each kind flies: gravity, radius (half its size), bounce, ground friction, glide (max fall speed)
B.KIND = {
  ball    = { g = 300, r = 3, bounce = 0.5, friction = 70 },
  stick   = { g = 300, r = 4, bounce = 0, friction = 260, spin = 9 },
  frisbee = { g = 90,  r = 5, bounce = 0, friction = 200, glide = 36 },
}
-- Mia's hand: where an item sits during the wind-up (wave clip frames 2-4), and where it leaves her hand
-- (cheer clip frame 2, the open arm in front), relative to her feet (she faces right)
B.WIND = { { 2, -13, -27 }, { 3, -15, -39 }, { 4, -11, -45 } }       -- { wave frame, hand dx, dy }
B.HAND = { 15, -33 }
B.WINDUP, B.FOLLOW = 0.36, 0.3                                     -- seconds before and after she lets go

-- the throws: { kind, where it lands (x), how high it goes over her hand (px), seconds since the throw before }.
-- Short and long balls first (to learn the arc), then the round's own mix. All land on the lawn (tests_bonus).
local A = {
  { "ball", 150, 40, 1.2 }, { "ball", 250, 60, 1.9 }, { "ball", 130, 55, 1.6 }, { "ball", 280, 55, 1.6 },
  { "stick", 200, 45, 1.8 }, { "ball", 170, 70, 1.6 }, { "frisbee", 250, 30, 1.7 }, { "ball", 300, 50, 2.2 },
  { "ball", 150, 80, 1.8 }, { "stick", 260, 35, 1.6 }, { "ball", 220, 75, 1.6 }, { "frisbee", 200, 25, 1.7 },
  { "ball", 110, 35, 2.0 }, { "ball", 290, 60, 1.4 }, { "stick", 160, 50, 1.6 },
}
local Bv = {
  { "ball", 150, 40, 1.2 }, { "ball", 260, 55, 1.9 }, { "stick", 130, 40, 1.6 }, { "stick", 240, 55, 1.7 },
  { "ball", 300, 45, 1.7 }, { "stick", 180, 65, 1.9 }, { "frisbee", 240, 30, 1.6 }, { "stick", 120, 35, 2.0 },
  { "ball", 270, 70, 1.4 }, { "stick", 210, 45, 1.7 }, { "frisbee", 160, 20, 1.7 }, { "stick", 290, 50, 2.1 },
  { "ball", 140, 55, 1.5 }, { "stick", 250, 40, 1.6 }, { "ball", 190, 60, 1.6 },
}
local C = {
  { "ball", 150, 40, 1.2 }, { "ball", 260, 55, 1.9 }, { "frisbee", 220, 30, 1.6 }, { "ball", 130, 45, 2.0 },
  { "frisbee", 280, 35, 1.6 }, { "stick", 190, 50, 2.1 }, { "frisbee", 150, 20, 1.6 }, { "ball", 300, 55, 1.8 },
  { "frisbee", 240, 40, 1.4 }, { "ball", 120, 30, 1.9 }, { "frisbee", 300, 30, 1.6 }, { "stick", 230, 55, 1.9 },
  { "frisbee", 180, 25, 1.5 }, { "ball", 270, 60, 1.6 },
}
B.VARIANTS = { A, Bv, C }
B.NAMES = { "BALL RALLY", "STICK TIME", "FRISBEE FLOAT" }
function B.variantFor(levelNumber) return ((math.max(1, levelNumber or 1) - 1) % 3) + 1 end

-- one step of an item's flight (the game and B.flight share it)
local function step(it, dt)
  local k = B.KIND[it.kind]
  if it.state == "air" then
    local g = k.g
    it.vy = it.vy + g * dt
    if k.glide and it.vy > k.glide then it.vy = k.glide end           -- the frisbee floats down
    it.x, it.y = it.x + it.vx * dt, it.y + it.vy * dt
    it.spin = (it.spin or 0) + (k.spin or 0) * dt * (it.vx >= 0 and 1 or -1)
    if it.y + k.r >= B.FEET then
      it.y = B.FEET - k.r
      if not it.landed then it.landed, it.landX = true, it.x end
      if k.bounce > 0 and it.vy > 70 then it.vy = -it.vy * k.bounce; it.vx = it.vx * 0.8
      else it.vy = 0; it.state = "ground"; it.vx = it.vx * (k.bounce > 0 and 0.85 or 0.4) end
    end
  elseif it.state == "ground" then
    local v = math.max(0, math.abs(it.vx) - k.friction * dt)
    it.vx = (it.vx >= 0 and 1 or -1) * v
    it.x = it.x + it.vx * dt
    if it.kind == "ball" then it.spin = (it.spin or 0) + it.vx * dt / 3 end
    if v == 0 then it.restT = (it.restT or 0) + dt end
  end
end
B.step = step

-- a throw's start: { x, y, vx, vy } from its landing x and its height over the hand (solved by simulation)
function B.launch(kind, landX, apex)
  local k = B.KIND[kind]
  local x0, y0 = B.MIA_X + B.HAND[1], B.FEET + B.HAND[2]
  local vy = -math.sqrt(2 * k.g * apex)
  local lo, hi = 10, 400
  for _ = 1, 30 do                                                 -- bisect vx so its first touch is at landX
    local vx = (lo + hi) / 2
    local f = B.flight(kind, { x = x0, y = y0, vx = vx, vy = vy })
    if f.landX < landX then lo = vx else hi = vx end
  end
  return { x = x0, y = y0, vx = (lo + hi) / 2, vy = vy }
end
-- the whole flight of a throw: the path (one point per step until it first touches the lawn), where it lands
-- and when; and where it ends (stops or leaves the screen)
function B.flight(kind, l)
  local it = { kind = kind, x = l.x, y = l.y, vx = l.vx, vy = l.vy, state = "air" }
  local path, t = {}, 0
  while not it.landed and t < 8 do path[#path + 1] = { x = it.x, y = it.y, t = t }; step(it, B.DT); t = t + B.DT end
  local landX, landT = it.landX or it.x, t
  local u = 0
  while it.state ~= "ground" or math.abs(it.vx) > 0 do step(it, B.DT); u = u + B.DT; if u > 10 or it.x > 340 then break end end
  return { path = path, landX = landX, landT = landT, endX = it.x, top = (function() local m = 999; for _, p in ipairs(path) do m = math.min(m, p.y) end; return m end)() }
end

-- the lawn: one screen, the ground at y 184 down to the bottom (the world's own walls keep Pepper on screen)
function B.world()
  local w = setmetatable({ rects = { { x0 = 0, x1 = 320, y0 = B.FEET, y1 = 240, kind = "solid", terrain = true } },
    slopes = {}, water = {}, movers = {} }, Wd)
  w.cols, w.rows, w.width, w.height = 40, 30, 320, 240
  return w
end

-- a new round. o: { variant (1-3), level (number, picks the variant when variant is not given) }
function B.new(o)
  o = o or {}
  local r = setmetatable({ phase = "intro", t = 0, time = B.TIME, catches = 0, points = 0, air = 0, picked = 0, lost = 0,
    items = {}, pops = {}, thrown = 0 }, B)
  r.variant = o.variant or B.variantFor(o.level)
  r.list = B.VARIANTS[r.variant]
  r.world = B.world()
  r.pepper = Pp.new(o.pepperX or 128, B.FEET); r.pepper.face = -1      -- she looks at Mia, ready
  r.mia = { x = B.MIA_X, state = "idle", t = 0 }
  r.nextT, r.k = r.list[1][4], 1                                   -- seconds of play until the next throw lets go
  return r
end

-- a button: on the cards any button goes on; in play the presses go to Pepper (jump, bark)
function B:press(name)
  if self.phase == "intro" and self.t > 0.5 then self.phase, self.t = "ready", 0; S.play("select"); return true end
  if self.phase == "result" and self.t > 1.5 then self.phase = "done"; S.play("select"); return true end
  return false
end

local function boxHit(it, x0, y0, x1, y1)
  local r = B.KIND[it.kind].r
  return it.x + r > x0 and it.x - r < x1 and it.y + r > y0 and it.y - r < y1
end

function B:update(dt, presses)
  self.t = self.t + dt
  for i = #self.pops, 1, -1 do local p = self.pops[i]; p.t = p.t + dt; if p.t > 0.7 then table.remove(self.pops, i) end end
  local m = self.mia
  m.t = m.t + dt
  if self.phase == "intro" or self.phase == "result" or self.phase == "done" then
    if self.phase == "result" then m.state = self.life and "cheer" or "wave" end
    return
  end
  if self.phase == "ready" and self.t >= 1.2 then self.phase, self.t = "play", 0 end
  if self.phase == "timeup" and self.t >= 1.4 then
    self.phase, self.t = "result", 0
    self.life = self.catches >= B.LIFE_AT
    S.play(self.life and "clear" or "bell")
  end
  -- Pepper: as in the levels (she can move during READY and TIME UP too, so she never freezes mid-jump)
  local p = self.pepper
  p:update(dt, self.world, presses or {})
  if self.phase ~= "play" and self.phase ~= "timeup" then return end
  if self.phase == "play" then
    local before = math.ceil(self.time)
    self.time = math.max(0, self.time - dt)
    if math.ceil(self.time) < before and self.time > 0 and self.time <= 5 then S.play("tick") end
    if self.time <= 0 then self.phase, self.t = "timeup", 0; S.play("bell") end
  end
  -- Mia: the wind-up starts B.WINDUP before the throw lets go; the item is in her hand meanwhile
  if self.phase == "play" and self.k <= #self.list then
    self.nextT = self.nextT - dt
    local th = self.list[self.k]
    if self.nextT <= B.WINDUP and not self.holding then
      self.holding = { kind = th[1], state = "hand", x = m.x, y = B.FEET - 30 }
      m.state, m.t = "windup", 0
    end
    if self.nextT <= 0 then
      local l = B.launch(th[1], th[2], th[3])
      local it = self.holding
      it.state, it.x, it.y, it.vx, it.vy, it.n = "air", l.x, l.y, l.vx, l.vy, self.k
      self.items[#self.items + 1] = it; self.holding = nil; self.thrown = self.thrown + 1
      m.state, m.t = "throw", 0; S.play("jump")
      self.k = self.k + 1
      if self.list[self.k] then self.nextT = self.list[self.k][4] end
    end
  end
  if m.state == "throw" and m.t > B.FOLLOW then m.state, m.t = "idle", 0 end
  if self.holding then                                              -- the item follows her hand
    local f = math.min(#B.WIND, 1 + math.floor(m.t / B.WINDUP * #B.WIND))
    self.holding.x, self.holding.y = m.x + B.WIND[f][2], B.FEET + B.WIND[f][3]
  end
  -- the items: fly, land, roll; Pepper's body box catches them
  local x0, y0, x1, y1 = p:box()
  for i = #self.items, 1, -1 do
    local it = self.items[i]
    step(it, dt)
    local gone
    if boxHit(it, x0, y0, x1, y1) and p.mode ~= "gone" then
      local pts = it.landed and B.GROUND or B.AIR
      self.catches = self.catches + 1; self.points = self.points + pts
      if it.landed then self.picked = self.picked + 1 else self.air = self.air + 1 end
      self.pops[#self.pops + 1] = { x = it.x, y = it.y, t = 0, pts = pts, air = not it.landed }
      S.play(it.landed and "key" or "bone")
      if self.catches == B.LIFE_AT then S.play("superbone") end
      gone = true
    elseif it.x - 8 > 320 or it.x + 8 < 0 or (it.restT or 0) > B.REST then
      self.lost = self.lost + 1; gone = true
    end
    if gone then table.remove(self.items, i) end
  end
end

-- done: the round's result for main.lua
function B:result() return { catches = self.catches, points = self.points, life = self.catches >= B.LIFE_AT, air = self.air, picked = self.picked, lost = self.lost, thrown = self.thrown } end

---------------------------------------------------------------------------------------------------- drawing
local art                                                          -- the park (City Park's own art), loaded once
local function loadArt()
  if art then return end
  local Sc = require("scene")
  local GF = require("girl_frames")
  art = { Sc = Sc, GF = GF, layers = Sc.buildArt(320, "park"), row = {} }
  art.girl = lg.newImage("art/girl.png"); art.girl:setFilter("nearest", "nearest")
  art.ball = lg.newImage("art/ball.png"); art.ball:setFilter("nearest", "nearest")
  -- Mia's own throw (r8/levels, the first art batch): art/girl_throw.png, one row of frames in girl.png's 66 x 66
  -- cells (feet centre 33, 66; facing right): 1 standing with the item, 2-5 the wind-up (behind her head, the step),
  -- 6 the release (the hand at B.HAND), 7-8 the follow-through. Without it: the wave and cheer clips, as before.
  if love.filesystem.getInfo("art/girl_throw.png") then
    art.throw = lg.newImage("art/girl_throw.png"); art.throw:setFilter("nearest", "nearest"); art.throwQ = {}
    for c = 1, math.floor(art.throw:getWidth() / GF.CW) do art.throwQ[c] = lg.newQuad((c - 1) * GF.CW, 0, GF.CW, GF.CH, art.throw:getDimensions()) end
  end
  art.q = {}
  for r, rw in ipairs(GF.rows) do
    art.row[rw.name] = r; art.q[r] = {}
    for c = 1, rw.n do art.q[r][c] = lg.newQuad((c - 1) * GF.CW, (r - 1) * GF.CH, GF.CW, GF.CH, art.girl:getDimensions()) end
  end
  -- the stick and the frisbee: a few hand-placed pixels each (no generated art). Stick 12 x 3, frisbee 12 x 5.
  local function bitmap(rows, pal)
    local d = love.image.newImageData(#rows[1], #rows)
    for y, s in ipairs(rows) do for x = 1, #s do local c = pal[s:sub(x, x)]; if c then d:setPixel(x - 1, y - 1, c[1], c[2], c[3], 1) end end end
    local im = lg.newImage(d); im:setFilter("nearest", "nearest"); return im
  end
  local wood = { o = { 0.23, 0.14, 0.08 }, m = { 0.55, 0.36, 0.19 }, l = { 0.74, 0.54, 0.31 } }
  art.stick = bitmap({ ".........oo.", "oooooooooolo", "olllmmmmmmmo", "oooooooooooo" }, wood)
  art.stickV = bitmap({ ".oo.", "olmo", "olmo", "olmo", "olmo", "olmo", "olmo", "omm.", "olmo", "olmo", "olmo", ".oo." }, wood)
  local disc = { o = { 0.30, 0.06, 0.12 }, r = { 0.90, 0.20, 0.32 }, l = { 1.0, 0.55, 0.62 }, w = { 1, 0.9, 0.9 } }
  art.frisbee = bitmap({ "...oooooo...", ".oollwllroo.", "orrrrrrrrrro", ".oorrrrrroo.", "...oooooo..." }, disc)
  art.frisbeeTilt = bitmap({ "..oooooooo..", "oollwlllrroo", "oorrrrrrrroo", "..oooooooo.." }, disc)
end

local function drawItem(it, x, y, t)
  lg.setColor(1, 1, 1, 1)
  if it.kind == "ball" then lg.draw(art.ball, math.floor(x - 3 + 0.5), math.floor(y - 3 + 0.5))
  elseif it.kind == "stick" then
    local a = (it.state == "air") and (math.floor((it.spin or 0) / (math.pi / 4)) % 4) or 0   -- 4 pixel angles
    if a == 0 then lg.draw(art.stick, math.floor(x - 6 + 0.5), math.floor(y - 2 + 0.5))
    elseif a == 2 then lg.draw(art.stickV, math.floor(x - 2 + 0.5), math.floor(y - 6 + 0.5))
    else lg.draw(art.stick, math.floor(x + 0.5), math.floor(y + 0.5), (a == 1 and 1 or -1) * math.pi / 4, 1, 1, 6, 2) end
  else
    local tilt = it.state == "air" and math.floor((t or 0) * 6) % 2 == 1
    lg.draw(tilt and art.frisbeeTilt or art.frisbee, math.floor(x - 6 + 0.5), math.floor(y - 2 + 0.5))
  end
end

-- Pepper's sprite rectangle on screen (nothing may cover her): x0, y0, x1, y1
function B:pepperRect() local p = self.pepper; return p.x - 30, p.y - 52, p.x + 30, p.y + 8 end

function B:drawScene()
  loadArt()
  local Sc, Look = art.Sc, require("look")
  Look.level({ art = "park" })
  Sc.drawFarArt(art.layers, 0, self.t + (self.time or 0), self.world)       -- the City Park sky, skyline, trees
  if not self.ground then self.ground = Sc.paintGroundArt(self.world, "park") end
  if Look.on then Look.use("ground") end
  lg.setColor(1, 1, 1, 1); self.ground:draw(0, 0)
  Look.off()
  -- shadows on the lawn
  local m, p = self.mia, self.pepper
  Sc.shadow(m.x, B.FEET, 22)
  for _, it in ipairs(self.items) do Sc.shadow(it.x, B.FEET, 8 - math.min(4, (B.FEET - it.y) / 10)) end
  Sc.shadow(p.x, B.FEET, 32 * (1 - math.min(48, B.FEET - p.y) / 96))
  -- Mia: idle, the wind-up (wave clip), the throw (cheer clip's open arms), cheering or waving at the result
  local GF, row, fr = art.GF, art.row.idle, 1
  if m.state == "windup" then row, fr = art.row.wave, B.WIND[math.min(#B.WIND, 1 + math.floor(m.t / B.WINDUP * #B.WIND))][1]
  elseif m.state == "throw" then if m.t < 0.18 then row, fr = art.row.cheer, 2 else row, fr = art.row.call, 7 end
  elseif m.state == "cheer" then row, fr = art.row.cheer, 1 + math.floor(m.t * 9) % 8
  elseif m.state == "wave" then row, fr = art.row.wave, 1 + math.floor(m.t * 9) % 8
  else fr = 1 + math.floor(m.t * 6) % 8 end
  local rw = GF.rows[row]
  lg.setColor(1, 1, 1, 1)
  local tq = art.throwQ
  if tq and #tq >= 8 and (m.state == "windup" or m.state == "throw") then   -- her own throw clip: the wind-up over
    local f = m.state == "windup" and 1 + math.min(4, math.floor(m.t / B.WINDUP * 5))   -- frames 1-5, the release 6,
      or 6 + math.min(2, math.floor(m.t / B.FOLLOW * 3))                     -- the follow-through 7-8
    lg.draw(art.throw, tq[f], m.x, B.FEET, 0, 1, 1, 33, 66)
  else lg.draw(art.girl, art.q[row][fr], m.x, B.FEET, 0, 1, 1, rw.x, rw.y) end
  if self.holding then drawItem(self.holding, self.holding.x, self.holding.y, self.t) end
  for _, it in ipairs(self.items) do
    local fade = (it.restT or 0) > B.REST - 1 and math.floor(it.restT * 8) % 2 == 0            -- blinks before it goes
    if not fade then drawItem(it, it.x, it.y, self.t) end
  end
  -- Pepper, then the pops (+100 over where she caught it; they float up, never over her: they start at the item)
  for _, pp in ipairs(self.pops) do                                -- the pop's ring: behind her
    local k = pp.t / 0.7
    lg.setColor(1, 1, 1, 1 - k); lg.setLineWidth(1)
    lg.circle("line", math.floor(pp.x), math.floor(pp.y), 3 + k * 14)
  end
  lg.setColor(1, 1, 1, 1); p:draw(0)
  for _, pp in ipairs(self.pops) do
    local k = pp.t / 0.7
    local s = "+" .. pp.pts
    local y = math.floor(pp.y - 22 - k * 16)
    local x0, y0, x1, y1 = self:pepperRect()
    if pp.x > x0 - 20 and pp.x < x1 + 20 and y + 7 > y0 then y = math.floor(y0 - 9 - k * 10) end       -- above her
    U.center(s, pp.x, y, 1, pp.air and U.GOLD or U.WHITE)
  end
  lg.setColor(1, 1, 1, 1)
end

function B:draw()
  self:drawScene()
  local F = require("flow")
  U.bonusStatus({ time = self.time, catches = self.catches, need = B.LIFE_AT, points = self.points })
  local avoid = { self:pepperRect() }
  if self.phase == "intro" then                                   -- (ui/hud-v8) the kit card, like the level intro
    U.dimWarm()
    local w = 230
    local y = F.placeY(45, w, 50, 100, avoid)
    local line = y + 10 + 86 - 6
    U.panel(45, y + 10, w, 86)
    local tw = U.sayW(13, "FETCH FRENZY!")
    U.ribbon3(159.5, y, tw + 20)
    U.say(13, "ink", "FETCH FRENZY!", math.floor(159.5 - (tw - 1) / 2 + 0.5), y + 2, "title")
    local rows = { { "A GOLDEN BONE BONUS", "cream" }, { "CATCH WHAT MIA THROWS!", "cream" },
      { ("%d CATCHES: EXTRA LIFE"):format(B.LIFE_AT), "gold" }, { B.NAMES[self.variant], "dim" } }
    for i, r in ipairs(rows) do U.say(7, r[2], r[1], math.floor(159.5 - (U.sayW(7, r[1]) - 1) / 2 + 0.5), y + 26 + (i - 1) * 11, "text") end
    if self.t > 0.5 and (self.t % 1.1) < 0.75 then F.onEdge("PRESS ANY BUTTON", line) end
  elseif self.phase == "ready" then
    U.center(self.t < 0.8 and "READY..." or "GO!", 160, 60, 3, U.GOLD)
  elseif self.phase == "play" and self.time <= 5 then
    U.center(tostring(math.ceil(self.time)), 160, 40, 3, U.GOLD)       -- the last seconds, big
  elseif self.phase == "timeup" then
    U.center("TIME UP!", 160, 60, 3, U.GOLD)
  elseif self.phase == "result" or self.phase == "done" then
    self:drawResult(avoid)
  end
  if self.phase ~= "play" and self.phase ~= "ready" and self.phase ~= "timeup" then        -- the cards never cover Pepper
    lg.setColor(1, 1, 1, 1); self.pepper:draw(0)
  end
end

function B:drawResult(avoid)                                       -- (ui/hud-v8) the kit card, like the tally
  local F = require("flow")
  local life = self.catches >= B.LIFE_AT
  local w, h = 220, 104
  local y = F.placeY(50, w, 24, h + 10, avoid)
  U.dimWarm()
  local line = y + 10 + h - 6
  U.panel(50, y + 10, w, h)
  local bounce = (self.t < 0.6) and math.floor(math.sin(self.t * 20) * 2) or 0
  local tw = U.sayW(13, "FETCH FRENZY!")
  U.ribbon3(159.5, y, tw + 20)
  U.say(13, "ink", "FETCH FRENZY!", math.floor(159.5 - (tw - 1) / 2 + 0.5), y + 2 + bounce, "title")
  local L, R = 70, 250
  local rows = { { "CATCHES", ("%d"):format(self.catches) }, { "IN THE AIR", tostring(self.air) }, { "POINTS", tostring(self.points) } }
  for i, rr in ipairs(rows) do
    if self.t > 0.2 + i * 0.25 then
      local st = i == 3 and "gold" or "cream"
      U.say(7, st, rr[1], L, y + 15 + i * 11, "tlabel"); U.say(7, st, rr[2], R - U.sayW(7, rr[2]) + 1, y + 15 + i * 11, "tvalue")
    end
  end
  if self.t > 1.2 then
    if life then
      local s = "EXTRA LIFE!"
      local ew = U.sayW(13, s); local hw, hh = U.body("head")
      local x = math.floor(159.5 - (ew + 3 + hw - 1) / 2 + 0.5)
      if math.floor(self.t * 3) % 2 == 0 then U.say(13, "gold", s, x, y + 67, "text") end
      U.put("head", x + ew + 3, y + 74 - (hh - 1) / 2, "life")
    else
      local s = ("%d CATCHES FOR AN EXTRA LIFE"):format(B.LIFE_AT)
      U.say(7, "dim", s, math.floor(159.5 - (U.sayW(7, s) - 1) / 2 + 0.5), y + 66, "text")
      U.say(7, "cream", "GOOD TRY, PEPPER!", math.floor(159.5 - (U.sayW(7, "GOOD TRY, PEPPER!") - 1) / 2 + 0.5), y + 78, "text")
    end
  end
  if self.t > 1.5 and (self.t % 1.1) < 0.75 then F.onEdge("PRESS ANY BUTTON", line) end
end
return B
