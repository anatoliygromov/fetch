-- Set pieces the levels share, kept out of stage.lua so the stage stays small (stage.lua calls these):
--   hard mode      carry.hard (from the menu) or --hard (tests): 1 heart, bikes and the tram 25% faster
--   rope ferries   a mover with `call` waits at its far end and is winched over to the near end when Pepper comes
--                  near (it waits there for her), then carries her across when she stands on it
--   traffic        a bike, cart, cargo bike or tram is sent 1 s before it reaches the screen edge: a bell rings, and a small
--                  warning sign shows at the edge it comes from until it is on screen. A zone with start = "enter"
--                  sends its first one as soon as Pepper walks in (no global timer)
--   secrets        L.secrets: hidden spots; reaching one counts it (stats: secrets, secretsTotal)
--   code pieces    L.pieces: things drawn in code (a kennel, a hollow log, kiosks, a jetty): their collision is ordinary
--                  hidden props in L.props with exactly the same boxes
local S = require("sfx")
local Sc = require("scene")
local Look = require("look")
local F = require("bigfont")
local lg = love.graphics
local Sp = {}
Sp.HARD_SPEED = 1.25           -- hard mode: traffic is 25% faster
Sp.WARN = 1.0                  -- seconds between the bell and the bike's front reaching the screen edge
for _, a in ipairs(arg or {}) do if a == "--hard" then Sp.hardFlag = true end end

function Sp.init(s, def, carry)
  s.hard = (carry and carry.hard) or Sp.hardFlag or nil
  s.maxHearts = s.hard and 1 or 3
  s.hearts = s.maxHearts
  s.secrets, s.secretsFound = {}, 0
  for i, z in ipairs(def.secrets or {}) do s.secrets[i] = { name = z.name, x0 = z.x0, x1 = z.x1, y0 = z.y0, y1 = z.y1 } end
  s.zoneIn = {}
  for i, mv in ipairs(s.movers) do                                 -- rope ferries start at their far end
    local m = def.movers[i]
    if m.call then
      local w = mv.x1 - mv.x0
      mv.call, mv.callSpeed, mv.rope = m.call, m.callSpeed or m.speed, m.rope
      mv.x0, mv.x1, mv.dir = m.to, m.to + w, -1
    end
  end
end

-- a rope ferry (the River Walk pontoon, the City Park duck boat): pulled along its rope, never by itself.
-- On it: across to the far end (after a short pause when she has just stepped on). Pepper near the near end
-- (m.call = { x0, x1 }): winched over to the near end, faster (callSpeed), to wait there for her. Else it stays.
function Sp.updateFerry(s, m, dt)
  local p = s.pepper
  local target, speed
  if p.ground == m and p.onGround then
    m.boardT = (m.boardT or 0) + dt
    if m.boardT > 0.3 then target, speed = m.to, m.speed end
  else
    m.boardT = 0
    if p.mode == "normal" and p.x >= m.call[1] and p.x <= m.call[2] then target, speed = m.from, m.callSpeed end
  end
  local nx = m.x0
  if target and math.abs(target - m.x0) > 0.001 then
    local d = target > m.x0 and 1 or -1
    nx = m.x0 + d * math.min(speed * dt, math.abs(target - m.x0)); m.dir = d
  end
  m.dx = nx - m.x0; m.x1 = m.x1 + m.dx; m.x0 = nx
end

-- a rowing boat (a mover rowed to and fro, River Walk's harbour). night/06nov-rw: a 4.0 m eka at true scale, split
-- into parts (tools/build_rw_rowboat.py): the hull BUILT by rule (art/scene/rw_rowboat.png, 185 x 62, bow left,
-- row 0 = world y 176, the rail on row 36 = the mover's top y 212, the waterline row 48 = y 224) and the rower's
-- 6-frame loop (art/scene/rw_rower.png, frames 78 x 62 on hull x 106-183, he rows from the stern thwart so Pepper's
-- spot amidships stays clear of him): his torso, the oar built per frame on
-- its rowlock, his near arm keyed by rule from shoulder to the fists on the handle. The mover's box is the hull's
-- columns 25-178. He rows while the boat moves (pulling when it goes right, stern first, as he faces the bow; the
-- loop backwards when it goes left), and rests with the blade lifted at each end. In code here: the water's tint
-- over everything below the waterline, a moving ripple row along the hull, a wake behind it while it moves, and a
-- splash where the blade goes in. Without the art: the old code-drawn boat.
local boatImg, rowerImg, rowerQ, hullCol, oarCol
local BOX0, FX0, FW, NF = 25, 106, 78, 6                          -- (fix round 1: the rower at the stern, hull x 106-183)
local WROW = 48                                                    -- the waterline's row in the art (world y 224)
local SPLASH = { [1] = 165, [4] = 131 }                            -- where the oar crosses the surface (hull x): catch, finish
local function cols(data, x0, w)                                   -- per column: the first opaque row at or under the
  local c = {}                                                     -- waterline and the last one (the submerged part)
  for x = 0, w - 1 do
    local t, bt
    for r = WROW, data:getHeight() - 1 do
      local _, _, _, a = data:getPixel(x0 + x, r)
      if a > 0 then t = t or r; bt = r end
    end
    c[x] = t and { t, bt } or false
  end
  return c
end
function Sp.drawRowboat(m, cam, t)
  if boatImg == nil then
    boatImg = false
    if love.filesystem.getInfo("art/scene/rw_rowboat.png") and love.filesystem.getInfo("art/scene/rw_rower.png") then
      local hd, rd = love.image.newImageData("art/scene/rw_rowboat.png"), love.image.newImageData("art/scene/rw_rower.png")
      boatImg, rowerImg = lg.newImage(hd), lg.newImage(rd)
      boatImg:setFilter("nearest", "nearest"); rowerImg:setFilter("nearest", "nearest")
      rowerQ, oarCol = {}, {}
      for i = 1, NF do rowerQ[i] = lg.newQuad((i - 1) * FW, 0, FW, 62, rd:getDimensions()); oarCol[i] = cols(rd, (i - 1) * FW, FW) end
      hullCol = cols(hd, 0, hd:getWidth())
    end
  end
  if boatImg then
    local hx = math.floor(m.x0 - cam + 0.5) - BOX0                  -- the hull's left (bow) column on screen
    local top = m.y0 - 36
    if hx > 330 or hx + 185 < -40 then return end
    local moving = math.abs(m.dx or 0) > 0
    local i = 5                                                     -- at rest: the blade lifted over the water
    if moving then
      local k = math.floor(t * 7) % NF
      i = (m.dir or 1) > 0 and 1 + k or NF - k                      -- going left: the loop backwards (backing water)
    end
    lg.setColor(1, 1, 1, 1)
    lg.draw(boatImg, hx, top)
    lg.draw(rowerImg, rowerQ[i], hx + FX0, top)
    -- the water over the hull and the blade below the waterline, column by column on their own shapes
    lg.setColor(22 / 255, 52 / 255, 125 / 255, 0.7)                -- (deeper than the surface blue: a wet hull reads darker)
    for x = 0, 184 do
      local c = hullCol[x]
      if c then lg.rectangle("fill", hx + x, top + c[1], 1, c[2] - c[1] + 1) end
    end
    for x = 0, FW - 1 do                                            -- the blade: only where the hull is not (no double tint)
      local c, h = oarCol[i][x], hullCol[FX0 + x]
      if c then
        local a1, a2 = c[1], c[2]
        if h then
          if a1 < h[1] then lg.rectangle("fill", hx + FX0 + x, top + a1, 1, math.min(a2, h[1] - 1) - a1 + 1) end
          if a2 > h[2] then local b1 = math.max(a1, h[2] + 1); lg.rectangle("fill", hx + FX0 + x, top + b1, 1, a2 - b1 + 1) end
        else lg.rectangle("fill", hx + FX0 + x, top + a1, 1, a2 - a1 + 1) end
      end
    end
    -- the ripple where the hull meets the water: two rows of short white dashes that run along it
    local wy = top + WROW
    local ph = math.floor(t * 6)
    for x = -3, 187 do
      if ((x + ph) % 9) < 3 and (hullCol[math.max(0, math.min(184, x))] or x < 0 or x > 184) then
        lg.setColor(0.86, 0.94, 0.97, 0.9); lg.rectangle("fill", hx + x, wy, 1, 1)
      end
      if ((x - ph + 4) % 13) < 2 and x > 2 and x < 182 then
        lg.setColor(0.86, 0.94, 0.97, 0.55); lg.rectangle("fill", hx + x, wy + 1, 1, 1)
      end
    end
    -- the wake: dashes trailing from the end it leaves, while it moves
    if moving then
      local back = (m.dir or 1) > 0 and -1 or 1                     -- the side it comes from
      local x0 = back < 0 and hx - 2 or hx + 186
      for k = 0, 5 do
        local d = 3 + k * 5 + (ph % 5)
        local len = 3 - math.floor(k / 2)
        lg.setColor(0.86, 0.94, 0.97, 0.85 - k * 0.12)
        lg.rectangle("fill", x0 + back * d - (back < 0 and len or 0), wy + (k % 2), len, 1)
      end
    end
    -- the splash: drops thrown up where the blade goes in (the catch) and a few as it comes out (the finish)
    local sx = SPLASH[i]
    if sx and moving then
      lg.setColor(0.93, 0.97, 1, 0.95)
      local n = i == 1 and 1 or 0.6
      for _, d in ipairs({ { -3, -2 }, { -1, -4 }, { 1, -3 }, { 3, -1 }, { 0, -1 }, { -2, -1 }, { 2, -5 } }) do
        if n == 1 or d[2] > -4 then lg.rectangle("fill", hx + sx + d[1], wy + d[2], 1, 1) end
      end
    end
    lg.setColor(1, 1, 1, 1)
    return
  end
  local x0, x1, y = math.floor(m.x0 - cam + 0.5), math.floor(m.x1 - cam + 0.5), m.y0
  local INK = { 0.11, 0.10, 0.09 }
  lg.setColor(INK)                                                 -- the hull: deck line to the waterline, tapered
  lg.polygon("fill", x0 - 3, y - 1, x1 + 3, y - 1, x1 - 3, y + 11, x0 + 3, y + 11)
  lg.setColor(0.55, 0.33, 0.18); lg.polygon("fill", x0 - 1, y, x1 + 1, y, x1 - 4, y + 10, x0 + 4, y + 10)
  lg.setColor(0.72, 0.47, 0.27); lg.rectangle("fill", x0, y, x1 - x0, 2)              -- the gunwale, lit
  lg.setColor(1, 1, 1, 1)
end

-- (6 Nov audit) The River Walk pontoon's line ended at a post in open water. It is moored now: a line from the
-- horn cleat on each end of its deck (pontoon.png, cleat horns at y0 - 4), one to a cleat on the quay's end, one to
-- a timber pile in the river by the ferry's bow (the ferry's crew winch it). Decoration: no outline, edges a
-- darker shade. Drawn behind the pontoon and Pepper.
local MOOR = { line = { 0.20, 0.17, 0.14 }, iron = { 0.30, 0.33, 0.38 }, ironL = { 0.48, 0.51, 0.56 },
               pile = { 0.50, 0.40, 0.30 }, pileD = { 0.40, 0.31, 0.24 }, pileL = { 0.62, 0.51, 0.39 } }
local function hline(x0, y0, x1, y1, sag)                          -- a 1 px line, whole pixels, x0 < x1; sag: px
  local n = math.max(1, x1 - x0)                                   -- it hangs at its middle (night/06nov-rw: was taut)
  local py
  for i = 0, n - 1 do
    local t = (i + 0.5) / n
    local y = math.floor(y0 + (y1 - y0) * t + (sag or 0) * 4 * t * (1 - t) + 0.5)
    if py and math.abs(y - py) > 1 then lg.rectangle("fill", x0 + i, math.min(y, py) + 1, 1, math.abs(y - py) - 1) end   -- no gaps
    lg.rectangle("fill", x0 + i, y, 1, 1); py = y
  end
end
local function moored(m, cam)
  local qx, px = math.floor(m.rope[1] - cam + 0.5), math.floor(m.rope[2] - cam + 0.5) - 7   -- the quay's end, the pile
  local ax = math.floor(m.x0 - cam + 0.5) - 3                      -- the pontoon art's left (drawn at x0 - 3, y0 - 5)
  local cy = m.y0 - 4                                              -- the cleats' horns
  lg.setColor(MOOR.iron); lg.rectangle("fill", qx - 7, m.y0 - 3, 7, 1); lg.rectangle("fill", qx - 5, m.y0 - 2, 3, 2)
  lg.setColor(MOOR.ironL); lg.rectangle("fill", qx - 7, m.y0 - 4, 7, 1)                    -- a horn cleat on the quay
  lg.setColor(MOOR.pileD); lg.rectangle("fill", px, m.y0 - 3, 6, 240 - m.y0 + 3)          -- the pile, to the river bed
  lg.setColor(MOOR.pile); lg.rectangle("fill", px + 1, m.y0 - 3, 4, 240 - m.y0 + 3)
  lg.setColor(MOOR.pileL); lg.rectangle("fill", px + 1, m.y0 - 4, 4, 1); lg.rectangle("fill", px + 1, m.y0 - 3, 1, 240 - m.y0 + 3)
  lg.setColor(22 / 255, 52 / 255, 125 / 255, 0.7); lg.rectangle("fill", px, 224, 6, 16)    -- (fix round 1) wet under the surface
  lg.setColor(MOOR.line)
  local span = m.rope[2] - m.rope[1] - 54                          -- (the longest the quay line gets)
  local d1, d2 = ax + 4 - (qx - 1), px + 1 - (ax + 50)
  hline(qx - 1, m.y0 - 4, ax + 4, cy, math.min(6, 2 + math.max(0, span - d1) / 24))   -- quay cleat to its left cleat:
  hline(ax + 50, cy, px + 1, m.y0 - 1, math.min(6, 2 + math.max(0, span - d2) / 24))  -- it slackens as they come close
  lg.rectangle("fill", px, m.y0 - 2, 6, 1); lg.rectangle("fill", px, m.y0, 6, 1)          -- the turns round the pile
  lg.setColor(0.61, 0.79, 0.94)                                    -- a ripple where the floats meet the river (y 224)
  for _, dx in ipairs({ 1, 2, 24, 25, 28, 29, 50, 51 }) do lg.rectangle("fill", ax + dx, m.y0 + 10, 1, 1) end
  for _, dx in ipairs({ 0, 26, 27, 52 }) do lg.rectangle("fill", ax + dx, m.y0 + 11, 1, 1) end
  for _, dx in ipairs({ -2, -1, 6, 7 }) do lg.rectangle("fill", px + dx, m.y0 + 10, 1, 1) end              -- and round the pile
end

-- (night/06nov-rw, base audit: "the pontoon with no waterline") the water's tint over the pontoon's floats below the
-- surface (y 224), as on the rowing boats and the jetty; called by stage.lua right after it draws the pontoon
local pontCol
function Sp.pontoonWater(m, cam, img)
  if not pontCol then
    pontCol = {}
    local d = love.image.newImageData("art/scene/pontoon.png")
    for x = 0, d:getWidth() - 1 do
      local b
      for y = 0, d:getHeight() - 1 do local _, _, _, a = d:getPixel(x, y); if a > 0 then b = y end end
      pontCol[x] = b
    end
  end
  local ax, top = math.floor(m.x0 - cam + 0.5) - 3, m.y0 - 5
  lg.setColor(22 / 255, 52 / 255, 125 / 255, 0.7)
  for x, b in pairs(pontCol) do
    if b and top + b >= 224 then lg.rectangle("fill", ax + x, 224, 1, top + b - 224 + 1) end
  end
  lg.setColor(1, 1, 1, 1)
end

-- the rope a ferry runs on: a thin line just under its deck, from bank to bank (drawn behind the ferry); the River Walk pontoon is moored
function Sp.drawRopes(s, cam)
  for _, m in ipairs(s.movers) do
    if m.rope and m.name == "PONTOON" and not s.def.art then moored(m, cam)
    elseif m.rope then
      local y = m.y0 + (m.rope.dy or 3)
      lg.setColor(0.18, 0.20, 0.25, 0.75); lg.rectangle("fill", math.floor(m.rope[1] - cam), y, m.rope[2] - m.rope[1], 1)
      lg.setColor(0.18, 0.20, 0.25, 1)
      for _, x in ipairs({ m.rope[1], m.rope[2] - 3 }) do lg.rectangle("fill", math.floor(x - cam), y - 3, 3, 7) end   -- the rope's posts
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- traffic: how fast this zone's vehicle goes, and a new one 1 s off the right edge of the screen, with its bell
function Sp.speed(s, bk) return bk.speed * (s.hard and Sp.HARD_SPEED or 1) end
function Sp.spawn(s, bk)
  local v = Sp.speed(s, bk)
  local hw = (bk.w or 48) / 2
  S.play(bk.bell or (bk.kind == "cart" and "honk") or (bk.kind == "tram" and "ding") or "bell")
  return { x = s.cam + 320 + hw + v * Sp.WARN, y = bk.roadY or 184, warn = Sp.WARN, zone = bk, speed = v }   -- (roadY: tall)
end
-- the zone was just entered: a zone with start = "enter" sends its vehicle now
function Sp.enterZone(s, bk, inside)
  if inside and not s.zoneIn[bk] and bk.start == "enter" then s.bikeT = math.min(s.bikeT, 0) end
  s.zoneIn[bk] = inside
end

-- a small warning sign at the screen edge a vehicle comes from (bikes, carts and trams come from the right),
-- shown until its front is on screen: a yellow diamond with "!" and an arrow pointing the way it goes. It sits
-- at the lane's height and moves above Pepper's head if she is there (it never covers her).
local SIGN = {
  "......k......", ".....kyk.....", "....kyyyk....", "...kyykyyk...", "..kyyykyyyk..", ".kyyyykyyyyk.",
  "kyyyyykyyyyyk", ".kyyyyyyyyyk.", "..kyyykyyyk..", "...kyyyyyk...", "....kyyyk....", ".....kyk.....", "......k......",
}
local SCOL = { k = { 0.13, 0.12, 0.10 }, y = { 0.99, 0.80, 0.18 } }
function Sp.drawWarnings(s, cam)
  local p = s.pepper
  local px0, py0, px1, py1 = p:box()
  for _, c in ipairs(s.bikes) do
    local bk = c.zone or {}
    local front = c.x - (bk.w or 48) / 2
    if front > cam + 320 and (c.warn or 0) > -1 then
      local w, h = 13, 13
      local x, y = 320 - w - 2, (bk.roadY or 184) - (bk.h or 26) / 2 - h / 2 - 2   -- (world y: drawn inside the camY shift)
      local sx0, sx1 = px0 - cam - 2, px1 - cam + 2
      if sx1 > x and sx0 < x + w and py1 > y - 2 and py0 < y + h + 2 then y = math.floor(py0) - h - 4 end
      if math.floor(s.t * 6) % 2 == 0 or front > cam + 320 + (c.speed or 100) * 0.5 then   -- blinks when it is close
        for row, line in ipairs(SIGN) do
          for col = 1, #line do
            local cc = SCOL[line:sub(col, col)]
            if cc then lg.setColor(cc); lg.rectangle("fill", x + col - 1, y + row - 1, 1, 1) end
          end
        end
        lg.setColor(SCOL.k)                                        -- the arrow: it comes this way
        lg.rectangle("fill", x - 9, y + 6, 1, 1); lg.rectangle("fill", x - 8, y + 5, 1, 3); lg.rectangle("fill", x - 7, y + 4, 1, 5)
        lg.rectangle("fill", x - 6, y + 6, 4, 1)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- secrets: reaching one (her feet inside its box) counts it, once
function Sp.updateSecrets(s)
  local p = s.pepper
  if p.mode ~= "normal" then return end
  for _, z in ipairs(s.secrets) do
    if not z.found and p.x >= z.x0 and p.x <= z.x1 and p.y >= z.y0 and p.y <= z.y1 then
      z.found = true; s.secretsFound = s.secretsFound + 1
      S.play("secret"); s:say(("SECRET! %s %d/%d"):format(z.name, s.secretsFound, #s.secrets), 2.2)
    end
  end
end

-- code-drawn pieces -------------------------------------------------------------------------------------
local function rect(c, x, y, w, h, a) lg.setColor(c[1], c[2], c[3], a or 1); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end
local function hexc(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end
local function faded(c) return Sc.fadeC(c) end                     -- decoration: to the level's back haze (scene.lua)
local INK = { 0.07, 0.07, 0.10 }                                    -- the 1 px dark outline of every obstacle
-- River Walk colours, taken from its art: the flower box's wood, the bench's green, the pot's terracotta
local WOOD, WOOD_D, WOOD_L = hexc("b86a34"), hexc("8a4a22"), hexc("d98c4e")
local GREEN, GREEN_D = hexc("3f6b48"), hexc("2c4e35")
local RED, WHITE, CREAM = hexc("c8473f"), hexc("efece4"), hexc("e8dcc0")

-- art for the pieces (tools/make_riverwalk_pieces.py), same sizes as the boxes below; kiosks faded like decoration
local ARTS = {}                                                    -- per colour script (the kiosks' fade)
local function art()
  if ARTS[Look.key] then return ARTS[Look.key] end
  local pieceArt = {}
  ARTS[Look.key] = pieceArt
  local function load(n, fade)
    local d = love.image.newImageData("art/scene/" .. n .. ".png")
    if fade then Sc.fadeData(d) end
    local im = lg.newImage(d); im:setFilter("nearest", "nearest"); return im
  end
  pieceArt.kennel = load("kennel")
  pieceArt.kiosk = { [64] = load("kiosk_kaffe", true), [56] = load("kiosk_glass", true) }
  pieceArt.awning = { [88] = load("awning_88"), [80] = load("awning_80") }
  return pieceArt
end

-- Pepper's kennel by her house (River Walk, the left edge): flat roof (top y0), plank walls, a dark doorway
-- 19 px high on its right end that she crawls into. Collision: one solid box x0-x1, y0-door top.
local function kennel(pc, cam)
  local x, y0, x1, dt = pc.x0 - cam, pc.y0, pc.x1 - cam, pc.door
  local foot = pc.foot or 184                                      -- (the path it stands on; tall levels set foot)
  local w = x1 - x
  local A = art()
  if w == A.kennel:getWidth() and A.kennel:getHeight() == foot - y0 then lg.setColor(1, 1, 1, 1); lg.draw(A.kennel, math.floor(x), y0); return end   -- (the art from its top down to the path)
  rect(INK, x, y0, w, foot - y0)                                    -- outline and body
  rect(WOOD, x + 1, y0 + 4, w - 2, foot - y0 - 5)
  for yy = y0 + 8, foot - 2, 5 do rect(WOOD_D, x + 1, yy, w - 2, 1) end -- planks
  rect(RED, x + 1, y0 + 1, w - 2, 3); rect(INK, x, y0 + 4, w, 1)   -- the roof board
  rect(INK, x + 3, dt - 1, w - 4, foot - dt + 1)                    -- the doorway: dark, open to the right end
  rect({ 0.12, 0.10, 0.12 }, x + 4, dt, w - 5, foot - dt)
  rect(WOOD_L, x + 1, y0 + 6, 2, dt - y0 - 6)                      -- the left corner post, light side
  lg.setColor(1, 1, 1, 1)
end

-- a kiosk at the back edge of the pavement (decoration: faded, no outline, base y 174) with a striped awning
-- reaching out over the pavement (an obstacle: crisp, outlined; a one-way top at y0 that Pepper can stand on).
local function kioskBack(pc, cam)
  local bx0, bx1 = pc.bx0 - cam, pc.bx1 - cam
  local top = pc.y0 + 6
  local im = art().kiosk[bx1 - bx0]
  if im and im:getHeight() == 174 - top then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(bx0), top); return end
  local wood, dark, glass = faded(GREEN), faded(GREEN_D), faded(hexc("9fb8c8"))
  rect(dark, bx0, top, bx1 - bx0, 174 - top)
  rect(wood, bx0 + 2, top, bx1 - bx0 - 4, 174 - top)
  rect(glass, bx0 + 6, top + 8, bx1 - bx0 - 12, 18)                -- the window
  rect(faded(CREAM), bx0 + 4, top + 26, bx1 - bx0 - 8, 4)          -- the counter
  rect(dark, bx0 + 4, top + 30, bx1 - bx0 - 8, 1)
  lg.setColor(1, 1, 1, 1)
end
local function kioskAwning(pc, cam)
  local x, y, w = pc.x0 - cam, pc.y0, pc.x1 - pc.x0
  local im = art().awning[w]
  if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x), y); return end
  rect(INK, x, y, w, 8)
  for i = 0, w - 3, 8 do rect((i / 8) % 2 == 0 and RED or WHITE, x + 1 + i, y + 1, math.min(8, w - 2 - i), 6) end
  for i = 0, w - 1, 8 do rect(INK, x + i + 2, y + 8, 4, 2); rect((i / 8) % 2 == 0 and RED or WHITE, x + i + 3, y + 8, 2, 1) end   -- scallops
  lg.setColor(1, 1, 1, 1)
end

-- a hollow log (City Park greybox): its bark shell is the top (solid, y0-y1, 19 px to crawl through under it),
-- the two cut ends are rings down to the path, the inside is dark (it hides what is in it)
local function hollowLog(pc, cam)
  local C = Sc.C
  local x, w, y0, y1 = pc.x0 - cam, pc.x1 - pc.x0, pc.y0, pc.y1
  local foot = pc.foot or 184                                      -- (the path it lies on; tall levels set foot)
  rect({ 0.16, 0.18, 0.22 }, x + 3, y1, w - 6, foot - y1)          -- the dark inside
  Sc.outlined(C.prop, C.propEdge, x, y0, w, y1 - y0 + 1)           -- the shell on top
  Sc.outlined(C.prop, C.propEdge, x, y0, 4, foot - y0)              -- the cut ends
  Sc.outlined(C.prop, C.propEdge, x + w - 4, y0, 4, foot - y0)
  lg.setColor(Sc.C.ground); local tw = F.width("HOLLOW", 1); F.print("HOLLOW", math.floor(x + w / 2 - tw / 2), y1 + 4, 1)
  tw = F.width("LOG", 1); F.print("LOG", math.floor(x + w / 2 - tw / 2), y1 + 11, 1)
  lg.setColor(1, 1, 1, 1)
end

-- a wooden jetty on piles (River Walk's harbour): a plank deck (its top is the box's top), crisp and outlined,
-- standing on three dark piles down into the water
local jettyImg, jettyCol
local function jetty(pc, cam)
  local x0, x1, y = math.floor(pc.x0 - cam), math.floor(pc.x1 - cam), pc.y0
  if jettyImg == nil then                                          -- the art (SpriteCook, tools/import_assets_v2.py)
    jettyImg = false
    if love.filesystem.getInfo("art/scene/rw_jetty.png") then
      -- (night/06nov-rw, base audit: "three piles run to the screen bottom over open water like a table leg") the
      -- piles end on an ink row 11 px under the surface: here each pile runs on down past the bottom of the screen
      -- (its row 32, plain wood, repeated from its foot), and the part under the surface takes the water's tint
      -- and a ripple, as the rowing boats do. The png is unchanged.
      local src = love.image.newImageData("art/scene/rw_jetty.png")
      local w, h = src:getDimensions()
      local d = love.image.newImageData(w, h + 6)
      for yy = 0, h + 5 do
        for xx = 0, w - 1 do
          local sy = yy < h - 1 and yy or 32
          local r, g, b, a = src:getPixel(xx, sy)
          if yy >= h - 1 then local _, _, _, a0 = src:getPixel(xx, h - 1); if a0 == 0 then a = 0 end end
          d:setPixel(xx, yy, r, g, b, a)
        end
      end
      jettyImg = lg.newImage(d); jettyImg:setFilter("nearest", "nearest")
      jettyCol = {}                                                -- per column: the rows under the surface
      for xx = 0, w - 1 do
        local t0, t1
        for yy = 0, h + 5 do local _, _, _, a = d:getPixel(xx, yy); if a > 0 then t0 = t0 or yy; t1 = yy end end
        jettyCol[xx] = t0 and { t0, t1 } or false
      end
    end
  end
  if jettyImg then
    lg.setColor(1, 1, 1, 1); lg.draw(jettyImg, x0, y - 1)
    local wr = 224 - (y - 1)                                       -- the surface's row in the art (world y 224)
    lg.setColor(22 / 255, 52 / 255, 125 / 255, 0.7)
    for xx, c in pairs(jettyCol) do
      if c and c[2] >= wr then lg.rectangle("fill", x0 + xx, y - 1 + math.max(wr, c[1]), 1, c[2] - math.max(wr, c[1]) + 1) end
    end
    local ph = math.floor(love.timer.getTime() * 6)                -- a ripple round each pile: dashes either side
    lg.setColor(0.86, 0.94, 0.97, 0.9)
    for xx, c in pairs(jettyCol) do
      if c and c[1] <= wr and c[2] >= wr then
        local l = not jettyCol[xx - 1] or jettyCol[xx - 1][2] < wr
        local r = not jettyCol[xx + 1] or jettyCol[xx + 1][2] < wr
        if l then lg.rectangle("fill", x0 + xx - 3 - ph % 2, 224, 2, 1) end
        if r then lg.rectangle("fill", x0 + xx + 2 + ph % 2, 224, 2, 1) end
      end
    end
    lg.setColor(1, 1, 1, 1)
    return
  end
  local INK = { 0.11, 0.10, 0.09 }
  for _, px in ipairs({ x0 + 3, math.floor((x0 + x1) / 2) - 3, x1 - 9 }) do     -- the piles
    lg.setColor(INK); lg.rectangle("fill", px - 1, y + 5, 8, 240 - y)
    lg.setColor(0.30, 0.24, 0.20); lg.rectangle("fill", px, y + 6, 6, 240 - y)
    lg.setColor(0.42, 0.34, 0.27); lg.rectangle("fill", px, y + 6, 1, 240 - y)
  end
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, x1 - x0 + 2, 8)           -- the deck
  lg.setColor(0.66, 0.47, 0.29); lg.rectangle("fill", x0, y, x1 - x0, 6)
  lg.setColor(0.80, 0.61, 0.40); lg.rectangle("fill", x0, y, x1 - x0, 1)
  lg.setColor(0.48, 0.33, 0.20)
  for x = x0 + 7, x1 - 2, 8 do lg.rectangle("fill", x, y + 1, 1, 5) end           -- plank joints
  lg.setColor(1, 1, 1, 1)
end

local BACK = { kiosk = kioskBack }
local PLAY = { kennel = kennel, kiosk = kioskAwning, hollowlog = hollowLog, jetty = jetty }
local function each(s, cam, list)
  for _, pc in ipairs(s.def.pieces or {}) do
    local f = list[pc.kind]
    if f and pc.x1 - cam > -20 and pc.x0 - cam < 340 then
      if not (s.def.art and Sc.drawPieceArt(pc, cam, s.def)) then f(pc, cam) end   -- art levels: scene.lua's art
    end
  end
end
function Sp.drawBack(s, cam) each(s, cam, BACK) end                -- behind Pepper's line (after the back props)
function Sp.drawPlay(s, cam) each(s, cam, PLAY) end                -- in her plane, after the bones, before her
return Sp
