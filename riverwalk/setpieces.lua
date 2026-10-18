-- Set pieces the levels share, kept out of stage.lua so the stage stays small (stage.lua calls these):
--   hard mode      carry.hard (from the menu) or --hard (tests): 1 heart, bikes and the tram 25% faster
--   rope ferries   a mover with `call` waits at its far end and is winched over to the near end when Pepper comes
--                  near (it waits there for her), then carries her across when she stands on it
--   traffic        a bike, cart or tram is sent 1 s before it reaches the screen edge: a bell rings, and a small
--                  warning sign shows at the edge it comes from until it is on screen. A zone with start = "enter"
--                  sends its first one as soon as Pepper walks in (no global timer)
--   secrets        L.secrets: hidden spots; reaching one counts it (stats: secrets, secretsTotal)
--   code pieces    L.pieces: things drawn in code (a kennel, a hollow log, kiosks, a jetty): their collision is ordinary
--                  hidden props in L.props with exactly the same boxes
local S = require("sfx")
local Sc = require("scene")
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

-- a rowing boat (a mover rowed to and fro, River Walk's harbour): a wooden hull (crisp, outlined: Pepper stands on
-- it), its deck the mover's top (y0), and a rower on the thwart at the stern, pulling the oars as it moves. The
-- rower sits at the end away from where it is going (rowers face backwards), low, so Pepper is never behind him.
function Sp.drawRowboat(m, cam, t)
  local x0, x1, y = math.floor(m.x0 - cam + 0.5), math.floor(m.x1 - cam + 0.5), m.y0
  local INK = { 0.11, 0.10, 0.09 }
  lg.setColor(INK)                                                 -- the hull: deck line to the waterline, tapered
  lg.polygon("fill", x0 - 3, y - 1, x1 + 3, y - 1, x1 - 3, y + 11, x0 + 3, y + 11)
  lg.setColor(0.55, 0.33, 0.18); lg.polygon("fill", x0 - 1, y, x1 + 1, y, x1 - 4, y + 10, x0 + 4, y + 10)
  lg.setColor(0.72, 0.47, 0.27); lg.rectangle("fill", x0, y, x1 - x0, 2)              -- the gunwale, lit
  lg.setColor(0.93, 0.93, 0.88); lg.rectangle("fill", x0 + 3, y + 4, x1 - x0 - 6, 1)  -- a painted stripe
  local back = (m.dir or 1) > 0 and x0 + 6 or x1 - 12                                  -- the stern, where he sits
  local pull = math.sin(t * 5) * (math.abs(m.dx or 0) > 0 and 1 or 0.2)
  lg.setColor(INK); lg.rectangle("fill", back - 1, y - 9, 8, 9)                       -- the rower: coat
  lg.setColor(0.24, 0.42, 0.62); lg.rectangle("fill", back, y - 8, 6, 8)
  lg.setColor(INK); lg.rectangle("fill", back, y - 14, 6, 6)                          -- head and cap
  lg.setColor(0.93, 0.74, 0.60); lg.rectangle("fill", back + 1, y - 13, 4, 4)
  lg.setColor(0.80, 0.25, 0.20); lg.rectangle("fill", back, y - 14, 6, 2)
  lg.setColor(0.42, 0.29, 0.18)                                                       -- the oars, dipping in turn
  local ox = back + 3
  lg.line(ox, y - 5, ox - 12 + pull * 6, y + 13 + pull * 2)
  lg.line(ox + 1, y - 5, ox + 13 + pull * 6, y + 13 - pull * 2)
  lg.setColor(1, 1, 1, 1)
end

-- the rope a ferry runs on: a thin line just under its deck, from bank to bank (drawn behind the ferry)
function Sp.drawRopes(s, cam)
  for _, m in ipairs(s.movers) do
    if m.rope then
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
  return { x = s.cam + 320 + hw + v * Sp.WARN, y = 184, warn = Sp.WARN, zone = bk, speed = v }
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
      local x, y = 320 - w - 2, 184 - (bk.h or 26) / 2 - h / 2 - 2
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
local HAZE, FADE = { 200 / 255, 210 / 255, 222 / 255 }, Sc.DECOR_FADE
local function faded(c) return { c[1] + (HAZE[1] - c[1]) * FADE, c[2] + (HAZE[2] - c[2]) * FADE, c[3] + (HAZE[3] - c[3]) * FADE } end
local INK = { 0.07, 0.07, 0.10 }                                    -- the 1 px dark outline of every obstacle
-- River Walk colours, taken from its art: the flower box's wood, the bench's green, the pot's terracotta
local WOOD, WOOD_D, WOOD_L = hexc("b86a34"), hexc("8a4a22"), hexc("d98c4e")
local GREEN, GREEN_D = hexc("3f6b48"), hexc("2c4e35")
local RED, WHITE, CREAM = hexc("c8473f"), hexc("efece4"), hexc("e8dcc0")

-- art for the pieces (tools/make_riverwalk_pieces.py), same sizes as the boxes below; kiosks faded like decoration
local pieceArt
local function art()
  if pieceArt then return pieceArt end
  pieceArt = {}
  local function load(n, fade)
    local d = love.image.newImageData("art/scene/" .. n .. ".png")
    if fade then d:mapPixel(function(_, _, r, g, b, a) return r + (HAZE[1] - r) * FADE, g + (HAZE[2] - g) * FADE, b + (HAZE[3] - b) * FADE, a end) end
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
  local w = x1 - x
  local A = art()
  if w == A.kennel:getWidth() and dt - y0 == 17 then lg.setColor(1, 1, 1, 1); lg.draw(A.kennel, math.floor(x), y0); return end
  rect(INK, x, y0, w, 184 - y0)                                    -- outline and body
  rect(WOOD, x + 1, y0 + 4, w - 2, 184 - y0 - 5)
  for yy = y0 + 8, 182, 5 do rect(WOOD_D, x + 1, yy, w - 2, 1) end -- planks
  rect(RED, x + 1, y0 + 1, w - 2, 3); rect(INK, x, y0 + 4, w, 1)   -- the roof board
  rect(INK, x + 3, dt - 1, w - 4, 184 - dt + 1)                    -- the doorway: dark, open to the right end
  rect({ 0.12, 0.10, 0.12 }, x + 4, dt, w - 5, 184 - dt)
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
  rect({ 0.16, 0.18, 0.22 }, x + 3, y1, w - 6, 184 - y1)          -- the dark inside
  Sc.outlined(C.prop, C.propEdge, x, y0, w, y1 - y0 + 1)           -- the shell on top
  Sc.outlined(C.prop, C.propEdge, x, y0, 4, 184 - y0)              -- the cut ends
  Sc.outlined(C.prop, C.propEdge, x + w - 4, y0, 4, 184 - y0)
  lg.setColor(Sc.C.ground); local tw = F.width("HOLLOW", 1); F.print("HOLLOW", math.floor(x + w / 2 - tw / 2), y1 + 4, 1)
  tw = F.width("LOG", 1); F.print("LOG", math.floor(x + w / 2 - tw / 2), y1 + 11, 1)
  lg.setColor(1, 1, 1, 1)
end

-- a wooden jetty on piles (River Walk's harbour): a plank deck (its top is the box's top), crisp and outlined,
-- standing on three dark piles down into the water
local function jetty(pc, cam)
  local x0, x1, y = math.floor(pc.x0 - cam), math.floor(pc.x1 - cam), pc.y0
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
