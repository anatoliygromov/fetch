-- The rooftops' mechanics, for any level (data from Tiled objects; docs/rooftops_beatsheet.md):
--   steam puffs   L.steam: vents { name, x0, x1, y0, y1, lift, every, warn, puff, phase, bark, source }. The box is the
--                 vent hood, a solid box (keep it 4 px tall: Pepper walks onto it); its top y0 is the vent's mouth.
--                 Someone makes every puff (a cook, a dryer, an oven, a sauna guest): nothing puffs by itself.
--                 Cycle: rest (every - warn - puff s), warn (warn s: the hood's flap rattles, two wisps rise, a
--                 "chuff"), puff (puff s: a column of steam up to y0 - lift - 16), rest. phase: s into the first
--                 rest (so neighbours do not puff together). every = 0 with bark = true: it only puffs after a bark.
--                 A bark within 80 px of the vent's middle and 60 px of y0 starts the warning now (someone heard
--                 her and turned it up). The lift: while it puffs, Pepper on or over the mouth (feet x in x0 - 6 ..
--                 x1 + 6, feet y in y0 - lift .. y0 + 2), not crouched, is launched once per puff to the apex
--                 y0 - lift exactly: only her upward speed is set (vy = -sqrt(2 * 560 * h)) and her jump base moved
--                 so letting go of A does not cut the rise short, as the springy awnings' bounce (critters.lua).
--                 Steam never hurts. Crouching (Down) on the hood stays put through a puff.
--   loose tiles   props with loose = true (one-way ledges, 24 x 6): Night Harbour's crumbling planks made general.
--                 The moment Pepper stands on one it shakes (SHAKE s, with a clink and grit), then it is no floor:
--                 it tips and falls with gravity and breaks on the roof below (it only drops while she is on it, so
--                 it never falls on her). GONE s later it is back, once her box is out of its place.
-- stage.lua calls Rf.init (St.new), Rf.update (after Pepper), Rf.bark (a bark), Rf.drawBack (behind Pepper's line)
-- and Rf.drawPlay (her plane).
local S = require("sfx")
local Pp = require("pepper")
local lg = love.graphics
local Rf = {}
Rf.SHAKE, Rf.GONE = 0.6, 3.0       -- a loose tile shakes this long, then is gone this long
Rf.BARK_X, Rf.BARK_Y = 80, 60      -- a bark this close to a vent (across, and her feet to its mouth) turns it up
Rf.MOUTH = 6                       -- the lift reaches this far either side of the mouth

function Rf.init(s, def)
  s.vents, s.tiles = {}, {}
  for i, v in ipairs(def.steam or {}) do
    local hood = { name = "", kind = "solid", x0 = v.x0, x1 = v.x1, y0 = v.y0, y1 = v.y1, vent = true }
    s.world.rects[#s.world.rects + 1] = hood
    s.vents[i] = { d = v, hood = hood, st = "rest", t = v.phase or 0, lifted = false }
  end
  for _, p in ipairs(def.props or {}) do
    if p.loose then p.hidden = true; s.tiles[#s.tiles + 1] = { p = p, st = "idle", t = 0 } end   -- (drawn here)
  end
end

local function rest(v) return math.max(0, (v.d.every or 0) - (v.d.warn or 0.8) - (v.d.puff or 0.9)) end
local function startWarn(s, v) v.st, v.t = "warn", 0; S.play("scramble") end      -- the flap rattles

-- the apex a vent's puff sends Pepper to (world y of her feet)
function Rf.apex(v) return v.d.y0 - v.d.lift end

local function removeRect(w, r) for i, q in ipairs(w.rects) do if q == r then table.remove(w.rects, i); return end end end

function Rf.update(s, dt)
  local p, w = s.pepper, s.world
  for _, v in ipairs(s.vents or {}) do
    local d = v.d
    v.t = v.t + dt
    if v.st == "rest" then
      if (d.every or 0) > 0 and not d.bark and v.t >= rest(v) then startWarn(s, v) end
    elseif v.st == "warn" then
      if v.t >= (d.warn or 0.8) then v.st, v.t, v.lifted = "puff", 0, false; S.play("hiss") end     -- pfff
    elseif v.st == "puff" then
      if not v.lifted and p.mode == "normal" and not p.crouch and p.x >= d.x0 - Rf.MOUTH and p.x <= d.x1 + Rf.MOUTH
         and p.y >= Rf.apex(v) and p.y <= d.y0 + 2 then
        local h = p.y - Rf.apex(v)                                   -- up to the apex: only her upward speed is set
        p.vy = -math.sqrt(2 * Pp.GRAV * h); p.onGround = false; p.ground = nil
        p.jumpBase = Rf.apex(v) + Pp.P.minJump; v.lifted = true
        s.puffed = (s.puffed or 0) + 1
      end
      if v.t >= (d.puff or 0.9) then v.st, v.t = "rest", 0 end
    end
  end
  for _, k in ipairs(s.tiles or {}) do
    k.t = k.t + dt
    if k.st == "idle" then
      if p.onGround and p.ground == k.p then k.st, k.t = "shake", 0; S.play("key") end      -- a clink: it moves
    elseif k.st == "shake" and k.t >= Rf.SHAKE then
      k.st, k.t = "gone", 0; removeRect(w, k.p); S.play("land")
      if p.ground == k.p then p.ground = nil end
      k.fy = w:floor(k.p.x0, k.p.x1, (k.p.x0 + k.p.x1) / 2, k.p.y1, w.height, k.p.y1) or w.height   -- where it breaks
    elseif k.st == "gone" and k.t >= Rf.GONE then
      local x0, y0, x1, y1 = p:box()
      if not (x1 > k.p.x0 and x0 < k.p.x1 and y1 > k.p.y0 - 2 and y0 < k.p.y1) then
        k.st, k.t = "idle", 0; w.rects[#w.rects + 1] = k.p
      end
    end
  end
end

-- a bark near a vent turns it up: a resting vent starts its warning now (a bark vent's only way to puff)
function Rf.bark(s)
  local p = s.pepper
  for _, v in ipairs(s.vents or {}) do
    local d = v.d
    if v.st == "rest" and math.abs(p.x - (d.x0 + d.x1) / 2) <= Rf.BARK_X and math.abs(p.y - d.y0) <= Rf.BARK_Y then
      startWarn(s, v)
      if d.bark and not v.said then v.said = true; s:say(d.say or ("WOOF! THE " .. (d.name or "VENT") .. " STEAMS UP!"), 2.2) end
    end
  end
end

-- drawing (greybox) ----------------------------------------------------------------------------------------------
local INK = { 0.11, 0.10, 0.09 }
-- behind Pepper's line: the steam column (semi-transparent, 3 frames), the warning's wisps
function Rf.drawBack(s, cam, t)
  for _, v in ipairs(s.vents or {}) do
    local d = v.d
    local cx = (d.x0 + d.x1) / 2 - cam
    if cx > -60 and cx < 380 then
      if v.st == "warn" then                                       -- two small wisps rise 8 px
        for i = 0, 1 do
          local k = (v.t * 2.5 + i * 0.5) % 1
          lg.setColor(0.92, 0.94, 0.96, 0.7 * (1 - k))
          lg.rectangle("fill", math.floor(cx - 4 + i * 6), math.floor(d.y0 - 2 - k * 8), 3, 2)
        end
      elseif v.st == "puff" then
        local top = Rf.apex(v) - 16
        local f = math.floor(t * 12) % 3                            -- a 3-frame animation
        local grow = math.min(1, v.t / 0.25)
        local y0 = d.y0 - (d.y0 - top) * grow
        local fade = v.t > (d.puff or 0.9) - 0.25 and math.max(0, ((d.puff or 0.9) - v.t) / 0.25) or 1
        local hw = (d.x1 - d.x0) / 2
        for y = math.floor(y0), d.y0 - 1, 6 do
          local k = (d.y0 - y) / math.max(1, d.y0 - top)             -- wider and fainter as it rises
          local wob = ((math.floor(y / 6) + f) % 3) - 1
          local ww = math.floor(hw + 2 + k * 10)
          lg.setColor(0.93, 0.95, 0.97, (0.55 - 0.3 * k) * fade)
          lg.rectangle("fill", math.floor(cx - ww + wob), y, ww * 2, 6)
        end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- in Pepper's plane: the vent hoods (the flap rattles while it warns) and the loose tiles
function Rf.drawPlay(s, cam, Sc)
  local F = require("bigfont")
  for _, v in ipairs(s.vents or {}) do
    local d = v.d
    local x = math.floor(d.x0 - cam + 0.5)
    if x > -40 and x < 360 then
      local w, h = d.x1 - d.x0, d.y1 - d.y0
      lg.setColor(INK); lg.rectangle("fill", x - 1, d.y0 - 1, w + 2, h + 1)
      lg.setColor(0.55, 0.57, 0.60); lg.rectangle("fill", x, d.y0, w, h)
      local jig = v.st == "warn" and ((math.floor(v.t * 20) % 2 == 0) and -1 or 1) or 0
      lg.setColor(0.78, 0.80, 0.82); lg.rectangle("fill", x + 2 + jig, d.y0 - (v.st == "warn" and 2 or 1), w - 4, 1)   -- the flap
      if v.st == "warn" then lg.setColor(1, 0.85, 0.2); F.print("!", x + math.floor(w / 2) - 2, d.y0 - 14, 1) end
      if d.bark and v.st == "rest" then lg.setColor(0.85, 0.85, 0.85, 0.8); F.print("?", x + math.floor(w / 2) - 2, d.y0 - 12, 1) end
    end
  end
  for _, k in ipairs(s.tiles or {}) do
    local p = k.p
    local x, w = p.x0 - cam, p.x1 - p.x0
    if x < 340 and x + w > -20 then
      local dx, dy, rot = 0, 0, 0
      if k.st == "shake" then dx = (math.floor(k.t * 10) % 2 == 0) and 2 or -2 end        -- 2 px, every 0.1 s
      local show = true
      if k.st == "gone" then
        dy = math.min((k.fy or p.y1) - p.y1, 0.5 * 560 * k.t * k.t)                       -- it falls with gravity
        if dy >= (k.fy or p.y1) - p.y1 and k.t > 0.1 then show = false end               -- and breaks below
      end
      if show and not (k.st == "gone" and k.t > 1.2) then
        lg.setColor(INK); lg.rectangle("fill", math.floor(x + dx), math.floor(p.y0 + dy), w, p.y1 - p.y0)
        lg.setColor(0.72, 0.36, 0.26); lg.rectangle("fill", math.floor(x + dx) + 1, math.floor(p.y0 + dy) + 1, w - 2, p.y1 - p.y0 - 2)
        lg.setColor(0.85, 0.50, 0.38); lg.rectangle("fill", math.floor(x + dx) + 1, math.floor(p.y0 + dy) + 1, w - 2, 1)
        lg.setColor(0.45, 0.22, 0.16); lg.rectangle("fill", math.floor(x + dx) + math.floor(w / 2), math.floor(p.y0 + dy) + 1, 1, p.y1 - p.y0 - 2)
      end
      if k.st == "shake" then                                      -- grit
        lg.setColor(0.6, 0.5, 0.45)
        for i = 0, 2 do lg.rectangle("fill", math.floor(x + 4 + i * 8), math.floor(p.y1 + (k.t * 40 + i * 3) % 10), 1, 1) end
      end
      if k.st == "gone" and k.fy and k.t > 0.1 and k.t < 0.6 and dy >= k.fy - p.y1 then   -- broken bits on the roof
        lg.setColor(0.72, 0.36, 0.26)
        for i = 0, 3 do lg.rectangle("fill", math.floor(x + 2 + i * 6 + (i - 1.5) * k.t * 20), math.floor(k.fy - 2 - (i % 2)), 3, 2) end
      end
      if k.st == "gone" and k.t > Rf.GONE - 0.6 then                -- coming back: a faint outline first
        lg.setColor(0.85, 0.5, 0.38, 0.5); lg.rectangle("line", math.floor(x) + 0.5, p.y0 + 0.5, w - 1, p.y1 - p.y0 - 1)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

return Rf
