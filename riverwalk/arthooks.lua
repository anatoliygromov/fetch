-- Hooks for the first art batch (r8/levels; the names, sizes and anchors: docs/art_hooks_r8.md). Every piece looks
-- for its file and falls back to what the game had before (today's art) or to a placeholder drawn in code, so new
-- files drop in by name with no code change. Nothing here touches Pepper or her rules.
--   cargo bikes    Downtown's street hazard (D1): kind = "cargo" in L.bikes. art/scene/cargo_bike.png (and
--                  cargo_bike_pedal.png), else an outlined box bike with its rider drawn in code (about 92 x 76)
--   the tram lane  L.trams: a vintage tram in the back lane (decoration, faded, behind Pepper's line, never a hazard).
--                  It is sent while the camera is over the lane's stretch, comes in at the right edge of the screen,
--                  stops at its tram stop sign (L.trams[i].stop) for a few seconds and drives on to the left. Its
--                  driver sits in the front cab. art/scene/tram_vintage.png, else drawn in code (about 300 x 130)
local Sc = require("scene")
local Look = require("look")
local lg = love.graphics
local H = {}

local INK = { 0.07, 0.07, 0.10 }                                    -- the 1 px dark outline of every obstacle
-- decoration: k of the way to the level's back haze (scene.lua Sc.fadeC; k nil: the level's back amount)
local function faded(c, k) return Sc.fadeC(c, k) end
local function rect(c, x, y, w, h) lg.setColor(c[1], c[2], c[3], c[4] or 1); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end

-- an optional picture: art/<name>.png, or false when it is not there (asked once). fade: decoration, faded
-- towards the level's back haze as the scenery art is (no outline); cached per colour script
local cache = {}
function H.img(name, fade)
  local key = name .. (fade and ("#" .. tostring(fade) .. "#" .. Look.key) or "")
  if cache[key] == nil then
    cache[key] = false
    local path = "art/" .. name .. ".png"
    if love.filesystem.getInfo(path) then
      local d = love.image.newImageData(path)
      if fade then Sc.fadeData(d, type(fade) == "number" and fade or nil) end   -- (a number: that much towards the haze)
      local im = lg.newImage(d); im:setFilter("nearest", "nearest"); cache[key] = im
    end
  end
  return cache[key]
end
-- a strip of frames, each `fw` wide, side by side (as the cyclists' _roll sheets): the quads, or nil
local quads = {}
function H.strip(im, fw)
  if not im then return nil end
  local k = tostring(im) .. fw
  if not quads[k] then
    quads[k] = {}
    for i = 0, math.floor(im:getWidth() / fw) - 1 do quads[k][i + 1] = lg.newQuad(i * fw, 0, fw, im:getHeight(), im:getDimensions()) end
  end
  return quads[k]
end
local frontCache, spireFar = {}, {}                                 -- (the house fronts per plaster, the far spire)
H.forget = function() cache, quads, frontCache = {}, {}, {}; spireFar = {} end                     -- (tests: look again for the files)

-- ===================================================================================================================
-- the cargo bike (Downtown, D1): a long box bike, a wooden cargo box of bread crates at the front, ridden by the
-- baker's delivery man. It rides right to left on the street. Its hit box (the zone's w x h, 80 x 26) is the cargo
-- box and the front wheel; the rider sits over the back wheel, behind the box, and is drawn tall (as the leaf-cart
-- keeper is) but never hurts. The bell rings 1 s before it comes in (setpieces.lua), and the rider's thumb rings it
-- again as it enters the screen (little rings by the handlebar).
local WOOD, WOOD_D, WOOD_L = { 0.72, 0.42, 0.20 }, { 0.52, 0.29, 0.13 }, { 0.86, 0.60, 0.33 }
local FRAME_C = { 0.16, 0.40, 0.33 }
local BREAD, BREAD_L = { 0.80, 0.55, 0.26 }, { 0.93, 0.74, 0.42 }
local SKIN, CAP, SHIRT, APRON, TROUSERS = { 0.93, 0.74, 0.60 }, { 0.45, 0.30, 0.20 }, { 0.30, 0.42, 0.62 }, { 0.94, 0.93, 0.88 }, { 0.22, 0.24, 0.30 }

local function line2(c, x0, y0, x1, y1, w)                           -- an outlined stroke: ink, then colour
  lg.setLineStyle("rough")
  lg.setColor(INK); lg.setLineWidth(w + 2); lg.line(x0, y0, x1, y1)
  lg.setColor(c); lg.setLineWidth(w); lg.line(x0, y0, x1, y1)
  lg.setLineWidth(1)
end
local function wheel(cx, cy, r, a)
  lg.setColor(INK); lg.circle("fill", cx, cy, r + 1)
  lg.setColor(0.20, 0.20, 0.24); lg.circle("fill", cx, cy, r)
  lg.setColor(0.70, 0.72, 0.76); lg.circle("fill", cx, cy, r - 2)
  lg.setColor(0.20, 0.20, 0.24); lg.circle("fill", cx, cy, r - 3)
  lg.setColor(0.70, 0.72, 0.76); lg.setLineWidth(1)
  for k = 0, 2 do local b = a + k * math.pi / 3; lg.line(cx - math.cos(b) * (r - 3), cy - math.sin(b) * (r - 3), cx + math.cos(b) * (r - 3), cy + math.sin(b) * (r - 3)) end
  rect(INK, cx - 1, cy - 1, 3, 3)
end
-- the placeholder: L = the hit box's left edge (on screen), B = the wheel line (y)
local function cargoCode(L, B, x, warn)
  local a = -x / 9                                                  -- (the wheels turn as it rides left)
  wheel(L + 10, B - 9, 9, a); wheel(L + 82, B - 9, 9, a)
  line2(FRAME_C, L + 56, B - 13, L + 82, B - 9, 2)                  -- the frame: box to the back wheel,
  line2(FRAME_C, L + 74, B - 12, L + 71, B - 38, 2)                 -- the seat post, the steering column
  line2(FRAME_C, L + 58, B - 22, L + 55, B - 46, 2)
  rect(INK, L + 51, B - 48, 8, 3); rect({ 0.25, 0.25, 0.28 }, L + 52, B - 47, 6, 1)       -- the handlebar
  rect(INK, L + 66, B - 41, 10, 4); rect({ 0.20, 0.17, 0.15 }, L + 67, B - 40, 8, 2)      -- the saddle
  -- the cargo box (the hit box: 80 x 26 with the front wheel): wooden, low between the wheels; bread in crates
  rect(INK, L + 2, B - 27, 56, 19)
  rect(WOOD, L + 3, B - 26, 54, 17)
  rect(WOOD_L, L + 3, B - 26, 54, 2)
  for xx = L + 12, L + 50, 10 do rect(WOOD_D, xx, B - 24, 1, 15) end
  rect(WOOD_D, L + 3, B - 18, 54, 1)
  for i, cx in ipairs({ L + 8, L + 30 }) do                           -- two bread crates, loaves over the rim
    rect(INK, cx - 1, B - 33, 22, 7); rect({ 0.60, 0.62, 0.66 }, cx, B - 32, 20, 5)
    for j = 0, 2 do rect(INK, cx + 1 + j * 6, B - 36 - (i + j) % 2, 6, 4); rect(BREAD, cx + 2 + j * 6, B - 35 - (i + j) % 2, 4, 2); rect(BREAD_L, cx + 2 + j * 6, B - 35 - (i + j) % 2, 4, 1) end
  end
  -- the rider: legs to the pedals (they go round with the distance), the body leaning to the bars, cap
  local ca = -x / 5
  local px1, py1 = L + 72 + math.cos(ca) * 5, B - 13 + math.sin(ca) * 5
  local px2, py2 = L + 72 - math.cos(ca) * 5, B - 13 - math.sin(ca) * 5
  line2(TROUSERS, L + 72, B - 40, (L + 72 + px2) / 2 - 3, (B - 40 + py2) / 2, 4); line2(TROUSERS, (L + 72 + px2) / 2 - 3, (B - 40 + py2) / 2, px2, py2, 3)
  line2(TROUSERS, L + 72, B - 40, (L + 72 + px1) / 2 - 3, (B - 40 + py1) / 2, 4); line2(TROUSERS, (L + 72 + px1) / 2 - 3, (B - 40 + py1) / 2, px1, py1, 3)
  rect(INK, px1 - 3, py1 - 1, 6, 3); rect(INK, px2 - 3, py2 - 1, 6, 3)                    -- shoes
  lg.setColor(INK); lg.polygon("fill", L + 58, B - 63, L + 70, B - 66, L + 80, B - 40, L + 66, B - 38)   -- the body,
  lg.setColor(SHIRT); lg.polygon("fill", L + 59, B - 62, L + 69, B - 65, L + 79, B - 41, L + 67, B - 39)  -- leaning
  lg.setColor(APRON); lg.polygon("fill", L + 64, B - 52, L + 71, B - 55, L + 76, B - 41, L + 67, B - 40)  -- to the bars
  line2(SHIRT, L + 62, B - 60, L + 56, B - 47, 3)                   -- the arm to the bars
  rect(INK, L + 52, B - 75, 11, 13); rect(SKIN, L + 53, B - 73, 9, 10)                    -- head
  rect(INK, L + 53, B - 70, 1, 1); rect({ 0.75, 0.50, 0.40 }, L + 52, B - 67, 2, 1)       -- eye, nose
  rect(INK, L + 50, B - 77, 14, 6); rect(CAP, L + 51, B - 76, 12, 4); rect(CAP, L + 49, B - 72, 6, 1)   -- the flat cap
  if warn and warn > -0.8 and math.floor(warn * 8) % 2 == 0 then    -- the bell: rings by the handlebar
    lg.setColor(0.99, 0.80, 0.18); rect({ 0.99, 0.80, 0.18 }, L + 52, B - 51, 3, 2)
    lg.setColor(1, 1, 1, 0.9); lg.setLineWidth(1)
    lg.arc("line", "open", L + 53, B - 52, 5, math.pi * 0.9, math.pi * 1.6); lg.arc("line", "open", L + 53, B - 52, 8, math.pi * 0.95, math.pi * 1.55)
  end
  lg.setColor(1, 1, 1, 1)
end
-- one cargo bike c (x = the hit box's middle, y = the wheel line), with its zone's depot (a courtyard gate: the
-- bike is drawn and hurts only right of the gate's door). Art: cargo_bike.png facing left, its hit box the left
-- w px of the frame, the bottom row on the wheel line; cargo_bike_pedal.png: frames of the same size side by side,
-- stepped by the distance ridden (one frame per 6 px).
function H.drawCargo(c, cam)
  local z = c.zone or {}
  local L, B = math.floor(c.x - (z.w or 80) / 2 - cam + 0.5), math.floor(c.y + 0.5)
  if z.depot then lg.setScissor(math.max(0, math.floor(z.depot - cam)), 0, 400, 240) end   -- (screen space, the whole height)
  Sc.shadow(L + 46, B - 1, 92)
  local still = H.img("scene/cargo_bike")
  if still then
    local pedal = H.img("scene/cargo_bike_pedal")
    local q = H.strip(pedal, still:getWidth())
    lg.setColor(1, 1, 1, 1)
    if q and #q > 0 then lg.draw(pedal, q[1 + math.floor(-c.x / 6) % #q], L, B - still:getHeight())
    else lg.draw(still, L, B - still:getHeight()) end
  else cargoCode(L, B, c.x, c.warn) end
  if z.depot then lg.setScissor() end
  lg.setColor(1, 1, 1, 1)
end

-- ===================================================================================================================
-- the tram lane (Downtown, D1): L.trams = { { x0, x1, y1, stop, every, dwell, speed } }. x0-x1: the stretch of the
-- level where trams run (one is sent while the middle of the screen is over it); y1: the rail line in the back lane
-- (behind Pepper's line: the street's foot minus 10, where decoration stands); stop: the tram stop sign's x. A tram
-- is about 300 px long and 130 tall (3.4 m at about 44 px a metre). It comes in at the right edge of the screen,
-- brakes to a halt with its front door at the stop sign, waits `dwell` seconds (its driver in the front cab), and
-- drives off to the left; it is gone once it is wholly off screen. Trams run every `every` seconds. Pure scenery:
-- it never touches Pepper and is drawn behind everything on her line.
H.TRAM_W, H.TRAM_H = 300, 130
H.TRAM_FADE = 0.4                                                   -- (the far lane: further back than the props' 0.28)
function H.newTrams(def) local out = {}; for i, l in ipairs(def.trams or {}) do out[i] = { lane = l, t = l.first or 2.0 } end; return out end
function H.updateTrams(s, dt)
  local cam = s.cam
  for _, tl in ipairs(s.trams or {}) do
    local l, c = tl.lane, tl.car
    local mid = cam + 160
    if not c then
      if mid > l.x0 and mid < l.x1 then
        tl.t = tl.t - dt
        if tl.t <= 0 then                                         -- sent: just off the right edge of the screen
          tl.t = l.every or 16
          c = { x = cam + 320 + H.TRAM_W / 2 + 8, v = l.speed or 110, state = "run" }
          if l.stop + H.TRAM_W / 2 - 24 > c.x then c.state = "go" end   -- (its stop is behind it: no stop)
          tl.car = c
        end
      end
    else
      local stopX = l.stop + H.TRAM_W / 2 - 24                      -- its middle, with the front door at the sign
      local vmax = l.speed or 110
      if c.state == "run" then
        local d = c.x - stopX
        c.v = math.min(vmax, math.sqrt(math.max(0, 2 * 45 * d)))   -- brakes at 45 px/s/s to the sign
        if d <= 0.5 then c.x, c.v, c.state, c.wait = stopX, 0, "stop", l.dwell or 3 end
      elseif c.state == "stop" then
        c.wait = c.wait - dt
        if c.wait <= 0 then c.state = "go" end
      else c.v = math.min(vmax, c.v + 40 * dt) end                 -- pulls away
      c.x = c.x - c.v * dt
      if c.x + H.TRAM_W / 2 < cam - 16 or c.x - H.TRAM_W / 2 > cam + 900 then tl.car = nil end
    end
  end
end
-- the tram stop sign: a pole and a round sign with a tram on it (no logo), faded; the tram, faded
local function stopSign(x, y)
  local pole, sign, edge = faded({ 0.30, 0.32, 0.36 }), faded({ 0.93, 0.93, 0.90 }), faded({ 0.18, 0.42, 0.30 })
  rect(pole, x, y - 46, 2, 46)
  lg.setColor(edge); lg.circle("fill", x + 1, y - 50, 7)
  lg.setColor(sign); lg.circle("fill", x + 1, y - 50, 5)
  rect(edge, x - 2, y - 52, 7, 3); rect(edge, x - 1, y - 49, 1, 1); rect(edge, x + 3, y - 49, 1, 1)
end
local function tramCode(cx, y, x, c)
  local W, Hh = H.TRAM_W, H.TRAM_H
  local function faded(c) return Sc.fadeC(c, H.TRAM_FADE) end
  local L = math.floor(cx - W / 2)
  local body, cream, roof, dark, glass = faded({ 0.24, 0.42, 0.66 }), faded({ 0.93, 0.88, 0.74 }), faded({ 0.42, 0.44, 0.48 }), faded({ 0.15, 0.17, 0.22 }), faded({ 0.62, 0.72, 0.80 })
  local top = y - Hh                                                -- the trolley pole up to the wire
  lg.setColor(dark); lg.setLineWidth(1); lg.line(L + 210, top + 26, L + 250, top - 2); rect(dark, L + 248, top - 3, 6, 2)
  rect(roof, L + 30, top + 18, W - 60, 10)                          -- the clerestory roof
  rect(roof, L + 70, top + 12, W - 140, 7)
  rect(body, L + 6, top + 28, W - 12, 72)                          -- the body: blue below, cream window band
  rect(cream, L + 6, top + 36, W - 12, 34)
  rect(faded({ 0.32, 0.52, 0.76 }), L + 6, top + 28, W - 12, 3)
  for wx = L + 46, L + W - 60, 24 do rect(glass, wx, top + 40, 18, 24); rect(cream, wx + 8, top + 40, 2, 24) end   -- windows
  rect(glass, L + 12, top + 38, 26, 28)                            -- the front cab (left: it drives left)
  rect(dark, L + 8, top + 72, 8, 26); rect(glass, L + 30, top + 74, 10, 22)              -- the front door
  rect(dark, L + W - 40, top + 72, 14, 26)                         -- the back door
  rect(faded({ 0.93, 0.74, 0.60 }), L + 22, top + 46, 8, 8)       -- the driver in the cab: face, cap, shoulders
  rect(faded({ 0.20, 0.24, 0.36 }), L + 21, top + 43, 10, 4)
  rect(faded({ 0.20, 0.24, 0.36 }), L + 19, top + 54, 14, 10)
  rect(dark, L + 4, top + 98, W - 8, 4)                            -- the skirt and the bogies, wheels turning
  local a = -x / 10
  for _, bx in ipairs({ L + 50, L + W - 50 }) do
    rect(dark, bx - 26, top + 100, 52, 8)
    for _, wx in ipairs({ bx - 14, bx + 14 }) do
      lg.setColor(dark); lg.circle("fill", wx, y - 11, 11)
      lg.setColor(roof); lg.line(wx - math.cos(a) * 9, y - 11 - math.sin(a) * 9, wx + math.cos(a) * 9, y - 11 + math.sin(a) * 9)
    end
  end
  rect(faded({ 0.99, 0.90, 0.60 }), L + 8, top + 84, 3, 3)         -- its headlamp
end
-- drawn in the back layer (behind the back props and everything on Pepper's line)
function H.drawTrams(s, cam)
  for _, tl in ipairs(s.trams or {}) do
    local l = tl.lane
    local c = tl.car
    if c and c.x + H.TRAM_W / 2 - cam > -10 and c.x - H.TRAM_W / 2 - cam < 330 then
      local im = H.img("scene/tram_vintage", H.TRAM_FADE)
      local x = math.floor(c.x - cam + 0.5)
      if im then lg.setColor(1, 1, 1, 1); lg.draw(im, x - math.floor(im:getWidth() / 2), l.y1 - im:getHeight())
      else tramCode(x, l.y1, c.x, c) end
    end
    if l.stop - cam > -20 and l.stop - cam < 340 then stopSign(math.floor(l.stop - cam), l.y1) end   -- (in front of it)
  end
  lg.setColor(1, 1, 1, 1)
end

-- ===================================================================================================================
-- the tall Downtown's old town (D2; a level with L.art = "town" and L.foot): the high road's pieces, the tall house
-- fronts under it and the far spire. Each piece looks for its art (docs/art_hooks_r8.md) and is drawn in code until
-- it lands. The roof kit (play props of the high road, crisp and outlined: obstacles): an image's top row is the
-- box's top minus 1 (the 1 px outline over the top Pepper walks on), centred on the box (best: the box's width + 2).
--   art/scene/town_roof_<name><w>.png, else town_roof_<name>.png   name: the prop's name, lower case, spaces to _
--                                                                  (loggia, gallery, chimney, dormer, flower_roof,
--                                                                  balcony), w: its box's width (gallery88)
--   art/scene/town_roof_gable.png      the guild house's stepped gable (GUILD ROOF and the steps right of it), its
--                                      top-left at the steps' left - 1 and the highest step's top - 1
--   art/scene/town_roof_ledge.png      any other ledge of the high road: a 3-slice (left 4 px, the middle repeated,
--                                      right 4 px), its top row at the box's top - 1
--   art/scene/town_footbridge.png      FOOTBRIDGE: H.BRIDGE_RAIL rows of railing above the deck (behind Pepper), then
--                                      the deck's outline row at the box's top - 1, the arch below; centred
-- The back layer (decoration, faded 28% as all decoration; drawn before the other back props, so Downtown's houses
-- with their balconies stand in front): the tall fronts (BAKERY, GUILD HOUSE and the unnamed back boxes 48 px wide
-- or more and 100 tall or more) are filled left to right with art/scene/town_front_tall1.png, 2, 3 (in turn), each
-- standing on the box's bottom and cut at its top (the roofline Pepper walks on) and at its right end; the far
-- landmark (RIDDARHOLMEN) is art/scene/spire_riddarholmen.png, faded 45%, centred on its box, standing on its bottom.
H.BRIDGE_RAIL = 12
H.SPIRE_DRIFT = 0.03                                      -- the far spire's scroll (was 0.3: on screen only from camera x 2727)
local function tallTown(def) return def.art == "town" and def.foot ~= nil end
local function high(def, p) return p.y0 <= def.foot - 120 end           -- the high road (the street is def.foot)
local function slug(n) return (n:lower():gsub("[^%w]+", "_")) end
local function isFront(p)
  return p.kind == "decor" and p.layer == "back" and (p.name == "" or p.name == nil or p.name == "BAKERY" or p.name == "GUILD HOUSE")
    and p.x1 - p.x0 >= 48 and p.y1 - p.y0 >= 100
end
local KIT = { LOGGIA = true, GALLERY = true, CHIMNEY = true, DORMER = true, ["FLOWER ROOF"] = true, ["GUILD ROOF"] = true, FOOTBRIDGE = true }

-- the guild house's stepped gable: GUILD ROOF and the unnamed ledges that follow it edge to edge
local gableOf = setmetatable({}, { __mode = "k" })
local function gable(def)
  if gableOf[def] ~= nil then return gableOf[def] end
  local g = false
  for i, p in ipairs(def.props) do
    if p.name == "GUILD ROOF" then
      g = { p, x0 = p.x0, x1 = p.x1, top = p.y0, bottom = p.y1, set = { [p] = true } }
      local j = i + 1
      while def.props[j] and (def.props[j].name or "") == "" and def.props[j].kind ~= "decor" and def.props[j].x0 == g.x1 do
        local q = def.props[j]; g.set[q] = true; g.x1 = q.x1; g.top = math.min(g.top, q.y0); g.bottom = math.max(g.bottom, q.y1); j = j + 1
      end
    end
  end
  gableOf[def] = g; return g
end

local STONE, STONE_L, STONE_D = { 0.78, 0.74, 0.66 }, { 0.90, 0.87, 0.80 }, { 0.58, 0.54, 0.48 }
local BRICK, BRICK_D, BRICK_L = { 0.66, 0.36, 0.26 }, { 0.50, 0.26, 0.19 }, { 0.80, 0.50, 0.38 }
local COPPER, COPPER_L = { 0.38, 0.62, 0.52 }, { 0.55, 0.78, 0.66 }
local function outlined(c, x, y, w, h) rect(INK, x - 1, y - 1, w + 2, h + 2); rect(c, x, y, w, h) end
local function ledgeCode(x, y, w, h)                                    -- a stone cornice: lit top, shadowed lip
  outlined(STONE, x, y, w, h); rect(STONE_L, x, y, w, 1); rect(STONE_D, x, y + h - 2, w, 2)
  for xx = x + 3, x + w - 4, 8 do rect(INK, xx, y + h + 1, 3, 2); rect(STONE_D, xx, y + h + 1, 3, 1) end   -- modillions
end
local function brickFace(x, y, w, h)
  rect(BRICK, x, y, w, h)
  for yy = y + 3, y + h - 1, 4 do rect(BRICK_D, x, yy, w, 1); for xx = x + ((yy - y) % 8 == 3 and 2 or 6), x + w - 1, 8 do rect(BRICK_D, xx, yy - 3, 1, 3) end end
end
local function kitCode(p, x, def)
  local w, h, y = p.x1 - p.x0, p.y1 - p.y0, p.y0
  local n = p.name or ""
  if n == "LOGGIA" then                                                 -- an arcade under a stone cornice
    rect(INK, x - 1, y + h, w + 2, 42 - h); rect(faded({ 0.86, 0.72, 0.46 }), x, y + h, w, 41 - h)
    for ax = x + 6, x + w - 22, 24 do rect(faded({ 0.20, 0.20, 0.26 }), ax, y + h + 8, 16, 33 - h); lg.setColor(faded({ 0.20, 0.20, 0.26 })); lg.circle("fill", ax + 8, y + h + 9, 8) end
    ledgeCode(x, y, w, h)
  elseif n == "GALLERY" then                                            -- a balustrade on a cornice
    outlined(STONE, x, y, w, h); rect(STONE_L, x, y, w, 1)
    rect(INK, x - 1, y + h, w + 2, 18); rect(STONE_D, x, y + h, w, 17)
    for bx = x + 3, x + w - 5, 7 do rect(STONE_L, bx, y + h + 2, 3, 11); rect(STONE, bx + 1, y + h + 5, 1, 5) end
    rect(STONE, x, y + h + 13, w, 4)
  elseif n == "CHIMNEY" then                                            -- brick, a stone cap, two clay pots below the top
    rect(INK, x - 1, y - 1, w + 2, h + 2); brickFace(x, y + 4, w, h - 4); rect(STONE, x - 1, y, w + 2, 4); rect(STONE_L, x - 1, y, w + 2, 1)
  elseif n == "DORMER" then                                             -- a copper cap over a little window gable
    rect(INK, x + 7, y + h, w - 14, 26); rect(faded({ 0.90, 0.84, 0.70 }), x + 8, y + h, w - 16, 25)
    rect(faded({ 0.24, 0.30, 0.40 }), x + w / 2 - 8, y + h + 5, 16, 15); rect(faded({ 0.90, 0.84, 0.70 }), x + w / 2 - 1, y + h + 5, 2, 15)
    outlined(COPPER, x, y, w, h); rect(COPPER_L, x, y, w, 1)
  elseif n == "FLOWER ROOF" then                                        -- a ledge with flower boxes along its front
    ledgeCode(x, y, w, h)
    for fx = x + 4, x + w - 14, 16 do rect(INK, fx - 1, y + h, 12, 6); rect(WOOD, fx, y + h, 10, 5); rect({ 0.86, 0.22, 0.30 }, fx + 1, y + h - 2, 2, 2); rect({ 0.95, 0.70, 0.20 }, fx + 5, y + h - 2, 2, 2) end
  elseif n == "FOOTBRIDGE" then                                         -- the rail behind, the deck, a shallow iron arch
    local rail = faded({ 0.25, 0.28, 0.30 })
    rect(rail, x, y - 11, w, 2); for px = x + 2, x + w - 2, 10 do rect(rail, px, y - 11, 1, 11) end
    outlined({ 0.55, 0.40, 0.26 }, x, y, w, h); rect({ 0.70, 0.54, 0.36 }, x, y, w, 1)
    lg.setColor(INK); lg.setLineWidth(3)
    local pts = {}; for i = 0, 16 do local k = i / 16; pts[#pts + 1] = x + k * w; pts[#pts + 1] = y + h + 1 + math.sin(k * math.pi) * -0 + (1 - math.sin(k * math.pi)) * 14 end
    lg.line(pts); lg.setColor(0.34, 0.38, 0.42); lg.setLineWidth(1); lg.line(pts)
  else ledgeCode(x, y, w, h) end
  lg.setColor(1, 1, 1, 1)
end
local function drawImgOn(im, p, x, ytop)
  lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x + (p.x1 - p.x0) / 2 - im:getWidth() / 2), math.floor(ytop))
end
local function threeSlice(im, x, y, w)
  local iw, ih = im:getDimensions()
  if not quads[im] then quads[im] = { lg.newQuad(0, 0, 4, ih, iw, ih), lg.newQuad(4, 0, iw - 8, ih, iw, ih), lg.newQuad(iw - 4, 0, 4, ih, iw, ih) } end
  local q = quads[im]
  lg.setColor(1, 1, 1, 1); lg.draw(im, q[1], x - 1, y - 1)
  local mw = iw - 8
  for xx = x + 3, x + w - 3, mw do
    local ww = math.min(mw, x + w - 3 - xx)
    if ww > 0 then lg.draw(im, lg.newQuad(4, 0, ww, ih, iw, ih), xx, y - 1) end
  end
  lg.draw(im, q[3], x + w - 3, y - 1)
end
-- a high road piece or a back piece of the tall Downtown (from Sc.drawPropArt): true when it is drawn (or drawn
-- elsewhere: the fronts and the spire, H.drawTownBack)
function H.townPiece(p, camx, def)
  if not tallTown(def) then return false end
  if p.layer == "back" and (isFront(p) or p.name == "RIDDARHOLMEN") then return true end   -- (H.drawTownBack)
  if p.layer ~= "play" or p.kind == "decor" or not high(def, p) then return false end
  local x = math.floor(p.x0 - camx)
  local n = p.name or ""
  local g = gable(def)
  if g and g.set[p] then                                               -- the stepped gable: drawn once, with its first step
    if p ~= g[1] then return true end
    local im = H.img("scene/town_roof_gable")
    if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(g.x0 - camx) - 1, g.top - 1); return true end
    for q in pairs(g.set) do local qx = math.floor(q.x0 - camx); rect(INK, qx - 1, q.y0 - 1, q.x1 - q.x0 + 2, 10); brickFace(qx, q.y0 + 2, q.x1 - q.x0, 7); rect(STONE, qx, q.y0, q.x1 - q.x0, 2) end
    lg.setColor(1, 1, 1, 1); return true
  end
  if n == "" or KIT[n] then
    local w = p.x1 - p.x0
    if n == "FOOTBRIDGE" then
      local im = H.img("scene/town_footbridge")
      if im then drawImgOn(im, p, x, p.y0 - 1 - H.BRIDGE_RAIL); return true end
    elseif n ~= "" then
      local im = H.img("scene/town_roof_" .. slug(n) .. w) or H.img("scene/town_roof_" .. slug(n))
      if im then drawImgOn(im, p, x, p.y0 - 1); return true end
    else
      local im = H.img("scene/town_roof_ledge")
      if im then threeSlice(im, x, p.y0, w); return true end
    end
    kitCode(p, x, def); return true
  end
  return false
end

-- the back layer of the tall Downtown: the spire far behind, then the tall house fronts (before the other back props)
local function frontCode(i, x, y0, y1, w)
  local plaster = ({ { 0.86, 0.66, 0.36 }, { 0.72, 0.38, 0.28 }, { 0.90, 0.78, 0.44 } })[(i - 1) % 3 + 1]
  local base, dark, light, glass = faded(plaster), faded({ plaster[1] * 0.8, plaster[2] * 0.8, plaster[3] * 0.8 }), faded({ math.min(1, plaster[1] * 1.12), math.min(1, plaster[2] * 1.12), math.min(1, plaster[3] * 1.12) }), faded({ 0.28, 0.34, 0.44 })
  rect(base, x, y0, w, y1 - y0)
  rect(light, x, y0, w, 2); rect(dark, x, y0 + 2, w, 3)                    -- the cornice, shadow under it
  rect(dark, x + w - 2, y0, 2, y1 - y0)                                   -- the edge to the next house
  local cols = math.max(1, math.floor((w - 8) / 24))
  local gap = (w - cols * 12) / (cols + 1)
  for yy = y0 + 12, y1 - 44, 26 do
    for c = 0, cols - 1 do
      local wx = math.floor(x + gap + c * (12 + gap))
      rect(dark, wx - 1, yy - 1, 14, 18); rect(glass, wx, yy, 12, 16); rect(light, wx - 1, yy + 16, 14, 2)
    end
    rect(dark, x, yy + 21, w, 1)                                          -- the storey line
  end
  local dx = math.floor(x + w / 2 - 8)                                    -- the door arch
  rect(dark, dx - 1, y1 - 27, 18, 27); rect(faded({ 0.22, 0.18, 0.16 }), dx, y1 - 25, 16, 25)
  lg.setColor(faded({ 0.22, 0.18, 0.16 })); lg.circle("fill", dx + 8, y1 - 25, 8)
end
local function spireCode(cx, y0, y1)
  local k = 0.45
  local function f(c) return Sc.fadeC(c, k) end
  local tower, iron = f({ 0.62, 0.36, 0.28 }), f({ 0.20, 0.26, 0.26 })
  local tb = y1 - 150
  rect(tower, cx - 14, tb, 28, y1 - tb); rect(f({ 0.50, 0.28, 0.22 }), cx + 8, tb, 6, y1 - tb)
  for yy = tb + 14, y1 - 20, 30 do rect(f({ 0.30, 0.22, 0.22 }), cx - 4, yy, 6, 12) end
  lg.setColor(iron); lg.polygon("fill", cx - 13, tb, cx + 13, tb, cx + 1, y0 + 8, cx - 1, y0 + 8)
  lg.setColor(f({ 0.62, 0.70, 0.74 })); lg.setLineWidth(1)                 -- the openwork: rows of little holes
  for yy = tb - 10, y0 + 30, -12 do
    local half = 13 * (yy - y0 - 8) / (tb - y0 - 8)
    for xx = -half + 3, half - 3, 5 do lg.rectangle("fill", math.floor(cx + xx), yy, 2, 5) end
  end
  rect(iron, cx - 1, y0, 2, 10); rect(iron, cx - 3, y0 + 3, 6, 1)
end
-- (art/placement) the fronts as bays of one building per box. The art (tools/build_tall_fronts.py) is one ground-floor
-- bay each, at true scale, in the yellow plaster ramp; a box is one building: its bays are near-equal shares of its
-- width (about 88 px each, or the box's `fronts` property, "2,1": the fronts in order), each front cropped
-- symmetrically or widened with its own edge column (every feature is centred and at most 70 px wide), and all in
-- the box's plaster (`plaster` property, else in turn), swapped by exact colour before the fade. The cut at the
-- box's top (the roofline the high road runs on) gets a stone coping; the box's right edge a 2 px shade.
local SRC = { { 214, 168, 104 }, { 176, 128, 80 } }                 -- the art's plaster: wall, shade (0-255)
H.PLASTER = {
  yellow = SRC,
  red = { { 172, 92, 70 }, { 130, 66, 52 } },
  cream = { { 222, 198, 152 }, { 184, 156, 114 } },
  ochre = { { 190, 140, 92 }, { 150, 106, 70 } },
  stone = { { 164, 150, 136 }, { 128, 114, 104 } },
}
H.PLASTER_ORDER = { "yellow", "red", "cream", "ochre", "stone" }
local COPING = { { 222 / 255, 214 / 255, 198 / 255 }, { 176 / 255, 166 / 255, 152 / 255 }, { 116 / 255, 108 / 255, 102 / 255 } }
local function frontImg(k, plaster)
  local key = k .. plaster .. "#" .. Look.key
  if frontCache[key] == nil then
    frontCache[key] = false
    local path = "art/scene/town_front_tall" .. k .. ".png"
    if love.filesystem.getInfo(path) then
      local d = love.image.newImageData(path)
      local to = H.PLASTER[plaster] or SRC
      d:mapPixel(function(x, y, r, g, b, a)
        for j = 1, 2 do
          local s = SRC[j]
          if math.floor(r * 255 + 0.5) == s[1] and math.floor(g * 255 + 0.5) == s[2] and math.floor(b * 255 + 0.5) == s[3] then
            return to[j][1] / 255, to[j][2] / 255, to[j][3] / 255, a
          end
        end
        return r, g, b, a
      end)
      Sc.fadeData(d)
      local im = lg.newImage(d); im:setFilter("nearest", "nearest")
      frontCache[key] = { im = im, w = d:getWidth(), h = d:getHeight() }
    end
  end
  return frontCache[key]
end
local function bays(p)                                               -- { { front, x, w }, ... } for a box
  local W, list = p.x1 - p.x0, {}
  if p.fronts then for k in tostring(p.fronts):gmatch("%d") do list[#list + 1] = tonumber(k) end end
  local n = #list > 0 and #list or math.max(1, math.floor(W / 88 + 0.5))
  local base, extra, x, out = math.floor(W / n), W - math.floor(W / n) * n, p.x0, {}
  for b = 1, n do
    local bw = base + (b <= extra and 1 or 0)
    out[b] = { list[b], x, bw }; x = x + bw
  end
  return out
end
local function drawBay(f, x, w, y0, y1)
  local ih = math.min(f.h, y1 - y0)
  local sy = f.h - ih
  lg.setColor(1, 1, 1, 1)
  if w <= f.w then
    lg.draw(f.im, lg.newQuad(math.floor((f.w - w) / 2), sy, w, ih, f.w, f.h), x, y1 - ih)
  else
    local l = math.floor((w - f.w) / 2)
    lg.draw(f.im, lg.newQuad(0, sy, 1, ih, f.w, f.h), x, y1 - ih, 0, l, 1)                 -- its wall, repeated
    lg.draw(f.im, lg.newQuad(0, sy, f.w, ih, f.w, f.h), x + l, y1 - ih)
    lg.draw(f.im, lg.newQuad(f.w - 1, sy, 1, ih, f.w, f.h), x + l + f.w, y1 - ih, 0, w - l - f.w, 1)
  end
end

-- (art/placement) the far landmark with its art: behind the old town row, on the far roofs' layer (scroll 0.3, the
-- shore's haze and fade), placed so that at the level's end it stands where its box is; its tip 8 px under the top
-- of the screen there (called by Sc.drawFarArt between the far roofs and the facades)
function H.drawFarSpire(def, camx, worldW)
  if not tallTown(def) then return end
  if spireFar[Look.key] == nil then
    spireFar[Look.key] = false
    if love.filesystem.getInfo("art/scene/spire_riddarholmen.png") then
      local d = Sc.fadeData(love.image.newImageData("art/scene/spire_riddarholmen.png"), nil, "shore")
      local im = lg.newImage(d); im:setFilter("nearest", "nearest"); spireFar[Look.key] = im
    end
  end
  local im = spireFar[Look.key]
  if not im then return end
  local camEnd = math.max(0, worldW - 320)
  for _, p in ipairs(def.props) do
    if p.name == "RIDDARHOLMEN" then
      -- (26 Oct, layer plan decision 6a: it drifts only H.SPIRE_DRIFT of the camera's way, so it is on screen from
      -- screen 1 to the end; at the level's end it still stands where its box is)
      local x = math.floor((p.x0 + p.x1) / 2 - (camx - camEnd) * H.SPIRE_DRIFT - camEnd - im:getWidth() / 2 + 0.5)
      if x > -im:getWidth() and x < 320 then lg.setColor(1, 1, 1, 1); lg.draw(im, x, 8) end
    end
  end
end

function H.drawTownBack(s, cam)
  local def = s.def
  if not tallTown(def) then return end
  if not love.filesystem.getInfo("art/scene/spire_riddarholmen.png") then   -- (with its art: far, H.drawFarSpire)
    for _, p in ipairs(def.props) do
      if p.name == "RIDDARHOLMEN" and p.x1 - cam > -40 and p.x0 - cam < 360 then spireCode(math.floor((p.x0 + p.x1) / 2 - cam), p.y0, p.y1) end
    end
  end
  if frontImg(1, "yellow") then                                      -- the fronts' art (all three) is there
    local nb = 0
    for _, p in ipairs(def.props) do
      if isFront(p) then
        nb = nb + 1
        local plaster = p.plaster or H.PLASTER_ORDER[(nb - 1) % #H.PLASTER_ORDER + 1]
        if p.x1 - cam > -10 and p.x0 - cam < 330 then
          for bi, b in ipairs(bays(p)) do
            local f = frontImg(b[1] or ((nb + bi) % 3 + 1), plaster) or frontImg(1, plaster)
            drawBay(f, math.floor(b[2] - cam), b[3], p.y0, p.y1)
          end
          local x0, x1 = math.floor(p.x0 - cam), math.floor(p.x1 - cam)
          local sh = Sc.fadeC({ H.PLASTER[plaster][2][1] / 255 * 0.86, H.PLASTER[plaster][2][2] / 255 * 0.86, H.PLASTER[plaster][2][3] / 255 * 0.86 })
          rect(sh, x1 - 2, p.y0, 2, p.y1 - p.y0)                       -- the building's right edge in shade
          rect(faded(COPING[1]), x0 - 1, p.y0, x1 - x0 + 2, 1)         -- the coping on the cut
          rect(faded(COPING[2]), x0 - 1, p.y0 + 1, x1 - x0 + 2, 2)
          rect(faded(COPING[3]), x0 - 1, p.y0 + 3, x1 - x0 + 2, 1)
        end
      end
    end
    lg.setColor(1, 1, 1, 1)
    return
  end
  local i = 0
  for _, p in ipairs(def.props) do
    if isFront(p) then
      local x, x1 = p.x0, p.x1
      while x < x1 do
        i = i + 1
        local im = H.img("scene/town_front_tall" .. ((i - 1) % 3 + 1), true)
        local fw = im and im:getWidth() or ({ 80, 88, 96 })[(i - 1) % 3 + 1]
        local w = math.min(fw, x1 - x)
        if x1 - x - w < 24 then w = x1 - x end                            -- (no sliver at the end: the last one widens)
        if x + w - cam > -10 and x - cam < 330 then
          if im then
            local ih = math.min(im:getHeight(), p.y1 - p.y0)
            lg.setColor(1, 1, 1, 1)
            lg.draw(im, lg.newQuad(0, im:getHeight() - ih, math.min(w, im:getWidth()), ih, im:getDimensions()), math.floor(x - cam), p.y1 - ih)
          else frontCode(i, math.floor(x - cam), p.y0, p.y1, w) end
        end
        x = x + w
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

return H
