-- Pepper: controller, collision box and animation. Art: art/pepper.png made from the SpriteCook animations,
-- 52 x 52 cells, one row per animation; pepper_frames.lua holds each frame's anchor and mouth point.
-- rows: idle, happy, wag, walk, run (gallop), jump, skid, crouch, crawl, hurt, sit, bark, sniff, grab
local I = require("input")
local S = require("sfx")
local Pp = {}
Pp.__index = Pp

local HW, H_STAND, H_CROUCH, FHW = 17, 26, 16, 13
local GRAV = 560

-- G1 numbers; the tuning panel (Tab) changes them and saves tuning.txt
local P = { run = 120, walk = 60, crawl = 40, accel = 420, brake = 620, turn = 300, jumpH = 46, minJump = 24,
            fallMul = 1.25, coyote = 0.08, buffer = 0.10, scramble = 12 }
Pp.P = P
local function loadTuning()
  local ok, txt = pcall(love.filesystem.read, "tuning.txt")
  if ok and txt then for k, v in txt:gmatch("(%w+)%s*=%s*([%d%.]+)") do if P[k] then P[k] = tonumber(v) end end end
end
function Pp.saveTuning()
  local t = {}
  for _, k in ipairs({ "run", "walk", "crawl", "accel", "brake", "turn", "jumpH", "minJump", "fallMul", "coyote", "buffer", "scramble" }) do
    t[#t + 1] = k .. " = " .. P[k]
  end
  pcall(love.filesystem.write, "tuning.txt", table.concat(t, "\n") .. "\n")
end

local FR = require("pepper_frames")
local CW, CH = FR.CW, FR.CH
local ROW = {}
for i, r in ipairs(FR.rows) do ROW[r.name] = i end
local function row(name, from, to)              -- every frame of a row, or frames from..to
  local t, r = {}, FR.rows[ROW[name]]
  for c = from or 1, to or r.n do t[#t + 1] = { ROW[name], c } end
  return t
end
local function with(t, k) for kk, v in pairs(k) do t[kk] = v end; return t end
local ANIM = {                                   -- every animation is a whole SpriteCook clip, frames in order
  idle    = with(row("idle"), { fps = 8 }),
  pant    = with(row("happy"), { fps = 8 }),
  wag     = with(row("wag"), { fps = 8 }),
  walk    = with(row("walk"), { fps = 10 }),
  run     = with(row("run"), { fps = 14 }),
  skid    = with(row("skid"), { fps = 12, once = true }),
  crouch  = with(row("crouch"), { fps = 16, once = true }),
  crawl   = with(row("crawl"), { fps = 9, loopFrom = 3 }),     -- frames 1-2 get her down, 3-8 loop
  hurt    = with(row("hurt"), { fps = 12, once = true }),
  sitdown = with(row("sit"), { fps = 8, once = true }),
  sit     = { { ROW.sit, FR.rows[ROW.sit].n } },
  bark    = with(row("bark"), { fps = 12, once = true }),
  sniff   = with(row("sniff"), { fps = 8 }),
  grab    = with(row("grab"), { fps = 10, once = true }),
  turn    = { { ROW.idle, 1 } },
  air     = with(row("jump"), { manual = true }),                -- the jump clip, frame picked from the jump itself
  land    = with(row("jump", 7, 8), { fps = 12, once = true }),
}

local sheet, quads, base, mouth
local function loadArt()
  if sheet then return end
  sheet = love.graphics.newImage("art/pepper.png"); sheet:setFilter("nearest", "nearest")
  quads, base, mouth = {}, {}, {}
  for r, rw in ipairs(FR.rows) do
    quads[r], base[r], mouth[r] = {}, {}, {}
    for c = 1, rw.n do
      local f = rw.f[c]
      quads[r][c] = love.graphics.newQuad((c - 1) * CW, (r - 1) * CH, CW, CH, sheet:getDimensions())
      base[r][c] = { x = f.x, y = f.y }
      mouth[r][c] = { x = f.mx, y = f.my }
    end
  end
end

function Pp.new(x, y)
  loadArt(); loadTuning()
  return setmetatable({ x = x, y = y, vx = 0, vy = 0, face = 1, onGround = true, ground = nil, crouch = false,
    mode = "normal", anim = "idle", frame = 1, at = 0, coyoteT = 0, bufferT = 0, jumpBase = y, dropT = 0,
    invuln = 0, idleT = 0, landT = 0, grabT = 0, runT = 0, pantT = 0, barkT = 0, turnT = 0, skid = false, breathT = 0, carrying = nil }, Pp)
end

function Pp:height() return self.crouch and H_CROUCH or H_STAND end
function Pp:box() local h = self:height(); return self.x - HW, self.y - h, self.x + HW, self.y end
-- Pepper is drawn 1 px lower than her collision box, so her paws sit in the ground line
-- instead of on top of it (she looked like she was floating). Drawing only, physics unchanged.
local SINK = 1

function Pp:mouthPos()
  local a = ANIM[self.anim]; local f = a[math.min(self.frame, #a)]
  local m = mouth[f[1]][f[2]]
  return self.x + self.face * m.x, self.y + m.y + SINK
end

local function setAnim(self, n) if self.anim ~= n then self.anim, self.frame, self.at = n, 1, 0 end end
local function approach(v, target, rate, dt)
  if v < target then return math.min(target, v + rate * dt) else return math.max(target, v - rate * dt) end
end

function Pp:jumpV() return math.sqrt(2 * GRAV * P.jumpH) end

-- presses: table of buttons pressed this tick (jump, act, bark)
function Pp:update(dt, w, presses)
  self.invuln = math.max(0, self.invuln - dt)
  self.barkT = math.max(0, self.barkT - dt); self.turnT = math.max(0, self.turnT - dt)
  self.dropT = math.max(0, self.dropT - dt); self.coyoteT = math.max(0, self.coyoteT - dt)
  self.bufferT = math.max(0, self.bufferT - dt)
  self.landT = math.max(0, self.landT - dt); self.grabT = math.max(0, self.grabT - dt)

  if self.mode == "scramble" then
    self.st = self.st + dt
    local k = math.min(1, self.st / 0.3)
    self.y = self.sy0 + (self.sy1 - self.sy0) * k
    self.x = self.sx0 + self.face * 14 * k
    setAnim(self, "air"); self.frame = (k < 0.5) and 4 or 5
    if k >= 1 then self.mode = "normal"; self.onGround = true; self.vy = 0; self.vx = self.face * 30 end
    return
  elseif self.mode == "drown" or self.mode == "gone" then
    self.vy = math.min(self.vy + GRAV * 0.3 * dt, 40); self.y = self.y + self.vy * dt
    setAnim(self, "air"); self.frame = 6; return
  end

  local ax = I.axis()
  local downHeld, walkHeld, jumpHeld = I.down("down"), I.down("walk"), I.down("jump")
  if self.mode == "hurt" then ax = 0; if self.onGround and self.invuln < 1.2 then self.mode = "normal" end end

  -- crouch and crawl: stays crouched while there is no headroom
  local wantCrouch = downHeld and self.onGround
  if self.crouch and not wantCrouch then
    if w:solidIn(self.x - HW + 1, self.x + HW - 1, self.y - H_STAND, self.y - 1) then wantCrouch = true end
  end
  self.crouch = wantCrouch

  -- speed
  local top = self.crouch and P.crawl or (walkHeld and P.walk or P.run)
  local target = ax * top
  self.skid = false
  if ax ~= 0 and self.vx ~= 0 and (ax > 0) ~= (self.vx > 0) then
    self.vx = approach(self.vx, target, P.turn, dt); self.skid = self.onGround and math.abs(self.vx) > 70
  elseif ax == 0 then
    if self.onGround and math.abs(self.vx) > 100 and not self.crouch then self.skid = true end
    self.vx = approach(self.vx, 0, P.brake, dt)
  else
    self.vx = approach(self.vx, target, P.accel, dt)
  end
  if ax ~= 0 then
    if self.onGround and math.abs(self.vx) < 20 and ax ~= self.face and not self.crouch then self.turnT = 0.12 end
    if not self.skid then self.face = ax end
  end

  -- jump, drop through
  if presses.jump then
    if downHeld and self.onGround and self.ground and (self.ground.kind == "oneway") then
      self.dropT = 0.25; self.onGround = false; self.ground = nil; self.vy = 20
    elseif not self.crouch then self.bufferT = P.buffer end
  end
  if self.bufferT > 0 and (self.onGround or self.coyoteT > 0) and self.mode == "normal" then
    self.vy = -self:jumpV(); self.jumpBase = self.y; self.onGround = false; self.ground = nil
    self.coyoteT, self.bufferT = 0, 0; S.play("jump")
  end
  if self.vy < 0 and not jumpHeld and not self.onGround then          -- let go early: a short hop
    local risen = self.jumpBase - self.y
    local minV = math.sqrt(2 * GRAV * math.max(0, P.minJump - risen))
    self.vy = math.max(self.vy, -minV)
  end

  -- sideways
  local h = self:height()
  local nx = self.x + self.vx * dt
  if self.onGround and self.ground and self.ground.dx then nx = nx + self.ground.dx end
  local hitX, hitR = w:wall(self.x, nx, HW, self.y, h, self.onGround)
  if hitX then
    nx = hitX
    -- scramble: in the air, pushing at a ledge whose top is at most P.scramble above the paws
    local up = self.y - hitR.y0
    if not self.onGround and ax ~= 0 and up > 0 and up <= P.scramble and self.vy > -120
       and not w:solidIn(nx + ax * 14 - HW + 1, nx + ax * 14 + HW - 1, hitR.y0 - H_STAND, hitR.y0 - 1) then
      self.mode, self.st, self.sx0, self.sy0, self.sy1 = "scramble", 0, nx, self.y, hitR.y0
      self.face = ax; self.vx = 0; self.vy = 0; S.play("scramble"); self.x = nx; return
    end
    self.vx = 0
  end
  nx = math.max(HW, math.min(w.width - HW, nx))
  self.x = nx

  -- up and down
  if self.onGround then
    local f, surf = w:floor(self.x - FHW, self.x + FHW, self.x, self.y - w.STEP, self.y + 6, self.y, self.dropT > 0, w.STEP)
    if f then self.y = f; self.ground = surf
    else self.onGround = false; self.ground = nil; self.coyoteT = P.coyote; self.vy = 0; self.jumpBase = self.y end
  else
    local g = self.vy > 0 and GRAV * P.fallMul or GRAV
    local ny = self.y + (self.vy + 0.5 * g * dt) * dt          -- exact for constant gravity, so heights match the numbers
    self.vy = math.min(self.vy + g * dt, 420)
    if self.vy < 0 then
      local r = w:solidIn(self.x - HW + 1, self.x + HW - 1, ny - h, self.y - h)
      if r then ny = r.y1 + h; self.vy = 0 end
    else
      local f, surf = w:floor(self.x - FHW, self.x + FHW, self.x, self.y - 0.5, ny, self.y, self.dropT > 0)
      if f then
        if self.vy > 160 then S.play("land") end
        if self.vy > 60 then self.landT = 0.17 end
        ny = f; self.vy = 0; self.onGround = true; self.ground = surf
      end
    end
    self.y = ny
  end

  if w:inWater(self.x, self.y) then self.mode = "drown"; self.vy = 30; self.vx = 0; S.play("splash"); return end

  -- bark
  if presses.bark and self.barkT == 0 then self.barkT = 0.5; S.play("bark"); self.barked = true end

  -- idle bookkeeping
  local moving = math.abs(self.vx) > 5 or not self.onGround or ax ~= 0 or downHeld
  if moving or presses.jump or presses.act or presses.bark then self.idleT = 0 else self.idleT = self.idleT + dt end
  if math.abs(self.vx) > P.walk + 10 then self.runT = self.runT + dt else
    if self.runT > 1.5 then self.pantT = 2 end
    self.runT = 0
  end
  self.pantT = math.max(0, self.pantT - dt)
  self.breathT = (self.breathT + dt) % 2.4

  if self.onGround then self.airT = 0 end
  -- choose the animation
  if self.mode == "hurt" then setAnim(self, "hurt")
  elseif not self.onGround then
    setAnim(self, "air"); self.airT = (self.airT or 0) + dt
    if self.airT < 0.07 and self.vy < 0 then self.frame = 3            -- take-off
    elseif self.vy < -90 then self.frame = 4                            -- rising
    elseif self.vy < 90 then self.frame = 5                             -- top of the jump
    else self.frame = 6 end                                             -- coming down, front paws reaching
  elseif self.grabT > 0 and math.abs(self.vx) < 30 then setAnim(self, "grab")
  elseif self.crouch then setAnim(self, math.abs(self.vx) > 5 and "crawl" or "crouch")
  elseif self.barkT > 0 then setAnim(self, "bark")
  elseif self.landT > 0 then setAnim(self, "land")
  elseif self.skid then setAnim(self, "skid")
  elseif self.turnT > 0 then setAnim(self, "turn")
  elseif math.abs(self.vx) > P.walk + 10 then setAnim(self, "run")
  elseif math.abs(self.vx) > 5 then setAnim(self, "walk")
  elseif self.idleT > 10 then setAnim(self, (self.anim == "sitdown" or self.anim == "sit") and self.anim or "sitdown")
  elseif self.pantT > 0 then setAnim(self, "pant")
  elseif self.idleT > 5 then setAnim(self, "wag")
  else setAnim(self, "idle") end
  self:animate(dt)
end

function Pp:animate(dt)
  local a = ANIM[self.anim]
  if a.manual then return end
  if #a < 2 then self.frame = 1; return end
  local fps = a.fps or 8
  if self.anim == "walk" or self.anim == "crawl" then fps = fps * math.max(0.5, math.abs(self.vx) / (self.anim == "walk" and P.walk or P.crawl)) end
  self.at = self.at + dt * fps
  if a.once then
    self.frame = math.min(#a, 1 + math.floor(self.at))
    if self.anim == "sitdown" and self.at >= #a then self.anim, self.frame, self.at = "sit", 1, 0 end
  elseif a.loopFrom and self.at >= #a then
    local L = #a - a.loopFrom + 1
    self.frame = a.loopFrom + math.floor(self.at - #a) % L
  else self.frame = 1 + math.floor(self.at) % #a end
end

function Pp:grab() self.grabT = 0.8 end

function Pp:hurt(fromX)
  if self.invuln > 0 or self.mode ~= "normal" then return false end
  self.invuln = 1.5; self.mode = "hurt"
  local dir = (self.x < fromX) and -1 or 1
  self.vx = dir * 150; self.vy = -170; self.onGround = false; self.ground = nil; self.crouch = false
  S.play("hurt"); return true
end

function Pp:draw(camx)
  if self.mode == "gone" then return end
  if self.invuln > 0 and math.floor(self.invuln * 12) % 2 == 0 and self.mode ~= "drown" then return end
  local a = ANIM[self.anim]; local f = a[math.min(self.frame, #a)]
  local q, b = quads[f[1]][f[2]], base[f[1]][f[2]]
  local x, y = math.floor(self.x + 0.5), math.floor(self.y + 0.5)
  love.graphics.draw(sheet, q, x - camx, y + SINK, 0, self.face, 1, b.x, b.y)
end

Pp.HW, Pp.H_STAND, Pp.H_CROUCH, Pp.GRAV = HW, H_STAND, H_CROUCH, GRAV
return Pp
