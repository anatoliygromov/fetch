-- Critters: creatures with simple, readable rules (docs/progression.md). L.critters lists them; stage.lua calls
-- Cr.init (St.new), Cr.update (St:update, after Pepper), Cr.bark (a bark) and Cr.draw (with the magpie and cat).
-- Every one warns before it can hurt, and a bark is always a good answer. Nothing moves by itself: they walk or fly.
--
--   goose  { kind = "goose", x, y (feet), x0, x1 (its patrol), speed }
--          Walks to and fro between x0 and x1. When Pepper is in front of it within 70 px (and on its level), it
--          stops and hisses (0.5 s, a "!"), then charges (90 px/s for 0.9 s), then stands blowing (0.8 s) and walks
--          on. Its bite costs a heart (it is 22 x 20, so a held jump clears it). A bark within 80 px shoos it away for
--          good: it flaps off, honking (+200). After a bite it struts off the other way for 2 s (never two bites
--          in a row). A bite knocks the ball out of Pepper's mouth if she carries it.
--   gull   { kind = "gull", x0, x1 (where it hunts Pepper), every (s between swoops) }
--          Circles high over Pepper while she is between x0 and x1. Every few seconds it squawks and its shadow
--          shows on the ground where she is (0.9 s), then it swoops down to her head height and back up. Crawling
--          (Down) ducks under it; it hurts only a standing Pepper. A bark while it squawks scares it off for 4 s.
local S = require("sfx")
local lg = love.graphics
local Cr = {}

local GOOSE_W, GOOSE_H = 22, 20
function Cr.init(s, def)
  s.critters = {}
  for i, c in ipairs(def.critters or {}) do
    local k = { kind = c.kind, i = i, t = 0, def = c }
    if c.kind == "goose" then
      k.x, k.y, k.dir, k.state = c.x, c.y, -1, "walk"
    else
      k.x, k.y, k.state, k.timer = (c.x0 + c.x1) / 2, 40, "circle", c.every or 4
    end
    s.critters[i] = k
  end
end

local function hits(p, x0, y0, x1, y1)
  local a, b, c, d = p:box()
  return c > x0 and a < x1 and d > y0 and b < y1
end

function Cr.update(s, dt)
  local p, w = s.pepper, s.world
  for _, k in ipairs(s.critters or {}) do
    local c = k.def
    k.t = k.t + dt
    if k.kind == "goose" then
      if k.state == "gone" then
        k.x = k.x + k.dir * 90 * dt; k.y = k.y - 70 * dt
      else
        local dx = p.x - k.x
        local level = math.abs(p.y - k.y) < 24
        if k.state == "walk" then
          k.x = k.x + k.dir * (c.speed or 22) * dt
          if k.x <= c.x0 then k.x, k.dir = c.x0, 1 elseif k.x >= c.x1 then k.x, k.dir = c.x1, -1 end
          if level and math.abs(dx) < 70 and (dx > 0) == (k.dir > 0) and p.mode == "normal" then
            k.state, k.t = "hiss", 0; S.play("hiss")
          end
        elseif k.state == "hiss" then
          if k.t >= 0.5 then k.state, k.t = "charge", 0 end
        elseif k.state == "charge" then
          k.x = math.max(c.x0 - 24, math.min(c.x1 + 24, k.x + k.dir * 90 * dt))
          if k.t >= 0.9 then k.state, k.t = "rest", 0 end
        elseif k.state == "rest" then
          if k.t >= 0.8 then k.state, k.t = "walk", 0 end
        end
        if k.state ~= "proud" and hits(p, k.x - GOOSE_W / 2, k.y - GOOSE_H, k.x + GOOSE_W / 2, k.y) and p:hurt(k.x, w) then
          s:loseHeart(); k.state, k.t, k.dir = "proud", 0, -k.dir           -- one bite, then it struts off the other way
          if p.carrying then s:dropBall() end                                -- the fright knocks the ball out of her mouth
        end
        if k.state == "proud" then
          k.x = math.max(c.x0, math.min(c.x1, k.x + k.dir * (c.speed or 22) * dt))
          if k.t >= 2.0 then k.state, k.t = "walk", 0 end
        end
      end
    else                                                           -- the gull
      local inZone = p.x >= c.x0 and p.x <= c.x1
      if k.state == "circle" or k.state == "away" then
        local tx = math.max(c.x0, math.min(c.x1, p.x)) + math.sin(k.t * 1.3) * 60
        k.x = k.x + (tx - k.x) * math.min(1, dt * 1.5); k.y = (k.state == "away" and 12 or 36) + math.sin(k.t * 2.1) * 6
        if k.state == "away" and k.t >= 4 then k.state, k.t = "circle", 0 end
        if k.state == "circle" and inZone and p.mode == "normal" then
          k.timer = k.timer - dt
          if k.timer <= 0 then k.state, k.t, k.tx, k.ty = "warn", 0, p.x, p.y; S.play("squawk") end
        end
      elseif k.state == "warn" then
        k.tx = k.tx + (p.x - k.tx) * math.min(1, dt * 3)            -- its shadow follows her a little
        if k.t >= 0.9 then k.state, k.t, k.sx, k.sy = "swoop", 0, k.x, k.y; k.ty = k.ty end
      elseif k.state == "swoop" then
        local u = math.min(1, k.t / 1.0)                           -- down to her head height and up again
        local low = k.ty - 22
        k.x = k.sx + (k.tx + (k.tx - k.sx) - k.sx) * u
        k.y = k.sy + (low - k.sy) * (1 - (2 * u - 1) ^ 2)
        if u >= 1 then k.state, k.t, k.timer = "circle", 0, c.every or 4 end
        if hits(p, k.x - 8, k.y - 4, k.x + 8, k.y + 4) and p:hurt(k.x, w) then
          s:loseHeart(); if p.carrying then s:dropBall() end
        end
      end
    end
  end
end

function Cr.bark(s)
  local p = s.pepper
  for _, k in ipairs(s.critters or {}) do
    if k.kind == "goose" and k.state ~= "gone" and math.abs(p.x - k.x) < 80 and math.abs(p.y - k.y) < 40 then
      k.state, k.t, k.dir = "gone", 0, (k.x >= p.x) and 1 or -1
      s.score = s.score + 200; S.play("honk"); s:say("SHOO! +200", 1.4)
    elseif k.kind == "gull" and k.state == "warn" and math.abs(p.x - k.x) < 140 then
      k.state, k.t = "away", 0; S.play("flap")
    end
  end
end

-- a goose that is still there, ahead of Pepper (the way she faces) within r px and on her level (for the
-- "BARK: SHOO!" hint; one behind her is no news)
function Cr.near(s, r)
  local p = s.pepper
  for _, k in ipairs(s.critters or {}) do
    local dx = (k.x - p.x) * p.face
    if k.kind == "goose" and k.state ~= "gone" and dx > -12 and dx < r and math.abs(p.y - k.y) < 30 then return true end
  end
  return false
end

-- drawing: pixel critters in code (like the magpie), feet at (x, y)
local GOOSE = {
  walk = {
    "................kkk.......",
    "...............kwwwk......",
    "...............kwkwkoo....",
    "...............kwwwkoooo..",
    "...............kwwwk......",
    "................kwwk......",
    "................kwwk......",
    "................kwwk......",
    "...............kwwwk......",
    "..kkk.........kwwwwk......",
    ".kwwwkkkkkkkkkwwwwwk......",
    "kwwwwwwwwwwwwwwwwwwk......",
    "kwwwssswwwwwwwwwwwk.......",
    "kwwsssssswwwwwwwwk........",
    ".kwwssssswwwwwwwk.........",
    "..kwwwwwwwwwwwwk..........",
    "...kkkkkkkkkkkk...........",
    "........oo..oo............",
    "........o....o............",
    ".......oo...oo............",
  },
  hiss = {
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "..........................",
    "....................kkk...",
    "...................kwkwkoo",
    "..............kkkkkwwwwkoo",
    ".............kwwwwwwwwk...",
    "..kkk.......kwwwkkkkk.oo..",
    ".kwwwkkkkkkkwwwwk.........",
    "kwwwwwwwwwwwwwwwk.........",
    "kwwwssswwwwwwwwwk.........",
    "kwwsssssswwwwwwk..........",
    ".kwwssssswwwwwk...........",
    "..kwwwwwwwwwwwk...........",
    "...kkkkkkkkkkk............",
    "........oo..oo............",
    "........o....o............",
    ".......oo...oo............",
  },
}
local GCOL = { k = { 0.14, 0.14, 0.18 }, w = { 0.96, 0.96, 0.93 }, s = { 0.72, 0.74, 0.76 }, o = { 0.93, 0.55, 0.16 } }
local GULL = {
  { "kk..........kk", ".kwk......kwk.", "..kwwkkkkwwk..", "...kwwwwwwkoo.", "....kkkkkk...." },
  { "..............", "..............", "kkwwkkkkkwwkk.", ".kkwwwwwwwwkoo", "...kkkkkkk...." },
}
local function sprite(rows, cols, x, y, flip)
  local h, w = #rows, #rows[1]
  for r, line in ipairs(rows) do
    for c = 1, w do
      local col = cols[line:sub(c, c)]
      if col then
        lg.setColor(col)
        local dx = flip and (w - c) or (c - 1)
        lg.rectangle("fill", math.floor(x) + dx, math.floor(y) - h + r, 1, 1)
      end
    end
  end
end
function Cr.draw(s, cam, t)
  for _, k in ipairs(s.critters or {}) do
    local x = k.x - cam
    if x > -40 and x < 360 then
      if k.kind == "goose" then
        local rows = (k.state == "hiss" or k.state == "charge") and GOOSE.hiss or GOOSE.walk
        local bob = (k.state == "walk" and math.floor(k.t * 6) % 2 == 0) and 1 or 0
        if k.state ~= "gone" then require("scene").shadow(x, k.y - 1, 18) end
        sprite(rows, GCOL, x - 13, k.y - bob, k.dir < 0)            -- drawn facing right, mirrored when it walks left
        if k.state == "hiss" then lg.setColor(1, 0.85, 0.2); require("bigfont").print("!", math.floor(x) - 2, k.y - 34, 1) end
      else
        if k.state == "warn" then                                  -- its shadow where it will come down
          lg.setColor(0.09, 0.11, 0.17, 0.45 + 0.3 * math.sin(k.t * 20)); lg.ellipse("fill", math.floor(k.tx - cam), k.ty - 1, 9, 2)
        end
        local frame = GULL[(math.floor(t * (k.state == "swoop" and 4 or 8)) % 2) + 1]
        sprite(frame, GCOL, x - 7, k.y + 3, (k.state == "swoop" and k.tx < k.sx) or (k.state ~= "swoop" and s.pepper.x < k.x))
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- the bounce: a prop with bounce = h launches Pepper h px up when she lands on it (not when she holds Down).
-- Only her upward speed is set; her jump base is moved so letting go of A does not cut the launch short.
function Cr.bounce(s, wasAir)
  local p = s.pepper
  local g = p.ground
  if wasAir and p.onGround and g and g.bounce and p.mode == "normal" and not p.crouch and not require("input").down("down") then
    local Pp = require("pepper")
    p.vy = -math.sqrt(2 * 560 * g.bounce); p.onGround = false; p.ground = nil
    p.jumpBase = p.y - g.bounce + Pp.P.minJump
    g.squashT = 0.2; S.play("spring")
  end
  for _, pr in ipairs(s.def.props) do if pr.squashT then pr.squashT = math.max(0, pr.squashT - 1 / 60) end end
end
return Cr
