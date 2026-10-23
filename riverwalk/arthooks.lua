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
local lg = love.graphics
local H = {}

local INK = { 0.07, 0.07, 0.10 }                                    -- the 1 px dark outline of every obstacle
local HAZE, FADE = { 200 / 255, 210 / 255, 222 / 255 }, Sc.DECOR_FADE
local function faded(c, k) k = k or FADE; return { c[1] + (HAZE[1] - c[1]) * k, c[2] + (HAZE[2] - c[2]) * k, c[3] + (HAZE[3] - c[3]) * k } end
local function rect(c, x, y, w, h) lg.setColor(c[1], c[2], c[3], c[4] or 1); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end

-- an optional picture: art/<name>.png, or false when it is not there (asked once). fade: decoration, faded
-- towards the haze as the scenery art is (no outline)
local cache = {}
function H.img(name, fade)
  local key = name .. (fade and ("#" .. tostring(fade)) or "")
  if cache[key] == nil then
    cache[key] = false
    local path = "art/" .. name .. ".png"
    if love.filesystem.getInfo(path) then
      local d = love.image.newImageData(path)
      local k = type(fade) == "number" and fade or FADE              -- (a number: that much towards the haze)
      if fade then d:mapPixel(function(_, _, r, g, b, a) return r + (HAZE[1] - r) * k, g + (HAZE[2] - g) * k, b + (HAZE[3] - b) * k, a end) end
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
H.forget = function() cache, quads = {}, {} end                     -- (tests: look again for the files)

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
  local function faded(c) return { c[1] + (HAZE[1] - c[1]) * H.TRAM_FADE, c[2] + (HAZE[2] - c[2]) * H.TRAM_FADE, c[3] + (HAZE[3] - c[3]) * H.TRAM_FADE } end
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

return H
