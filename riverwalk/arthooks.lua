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
-- stepped by the distance ridden (one frame per H.CARGO_PEDAL_PX px; 6 Nov: 13 px, 8 frames = one crank turn in
-- about 104 px, about once a second at its 110-130 px/s, as the River Walk riders).
H.CARGO_PEDAL_PX = 13
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
    if q and #q > 0 then lg.draw(pedal, q[1 + math.floor(-c.x / H.CARGO_PEDAL_PX) % #q], L, B - still:getHeight())
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
-- (art/dt-audit-06nov) the audit: "the tram is a pale see-through ghost", lighter than everything in front of it. Faded
-- 40 % to Downtown's back haze (efe6da) and then the back grade, its blue went to 150 on screen, at the far city's
-- value, so the facades' warm plaster read through it and the street in front looked darker. It is a hazard Pepper
-- must read: 10 % now, on the back look like the shelter and the fronts' darks, opaque (binary alpha, as always):
-- 10th percentile 88, median 106 on screen, under the far city (145) and the fronts (about 170).
H.TRAM_FADE = 0.10
-- (6 Nov, art/dt-traffic-06nov) the true-scale tram art: tram_vintage.png 586 x 188 (12.7 m body, 3.3 m to the
-- clerestory at 46 px/m, the trolley pole above), its front door's middle 60 px from its left edge; its wheels are
-- tram_vintage_wheel.png (4 frames of 31 x 31, turned a frame per TRAM_WHEEL_PX ridden) at these centres, drawn
-- behind the body. Without the art: the code tram above (300 x 130, its door 24 px in). H.tramDims() gives the
-- width and door the lane uses, so the stop puts the door at the sign either way.
H.TRAM_DOOR = 24
H.TRAM_ART = { door = 60, wheels = { 90, 164, 424, 498 }, wheelY = 16 }
H.TRAM_WHEEL_PX = 3
function H.tramDims()
  local im = H.img("scene/tram_vintage", H.TRAM_FADE)
  if im then return im:getWidth(), H.TRAM_ART.door end
  return H.TRAM_W, H.TRAM_DOOR
end
function H.newTrams(def) local out = {}; for i, l in ipairs(def.trams or {}) do out[i] = { lane = l, t = l.first or 2.0 } end; return out end
function H.updateTrams(s, dt)
  local cam = s.cam
  local TW, TD = H.tramDims()
  for _, tl in ipairs(s.trams or {}) do
    local l, c = tl.lane, tl.car
    local mid = cam + 160
    if not c then
      if mid > l.x0 and mid < l.x1 then
        tl.t = tl.t - dt
        if tl.t <= 0 then                                         -- sent: just off the right edge of the screen
          tl.t = l.every or 16
          c = { x = cam + 320 + TW / 2 + 8, v = l.speed or 110, state = "run" }
          if l.stop + TW / 2 - TD > c.x then c.state = "go" end      -- (its stop is behind it: no stop)
          tl.car = c
        end
      end
    else
      local stopX = l.stop + TW / 2 - TD                            -- its middle, with the front door at the sign
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
      if c.x + TW / 2 < cam - 16 or c.x - TW / 2 > cam + 900 then tl.car = nil end
    end
  end
end
-- the tram stop sign: a pole and a round sign with a tram on it (no logo), faded; the tram, faded
-- (art/dt-roofs-06nov) town_stopsign.png (tools/build_dt_details.py), faded as back decoration: 2.2 m at true scale,
-- its pole's middle column (9) on x + 1 (the middle of the old 2 px pole), its bottom row on the rail line
local function stopSign(x, y)
  local im = H.img("scene/town_stopsign", true)
  if im then lg.setColor(1, 1, 1, 1); lg.draw(im, x + 1 - 9, y - im:getHeight()); return end
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
  local TW = H.tramDims()
  for _, tl in ipairs(s.trams or {}) do
    local l = tl.lane
    local c = tl.car
    if c and c.x + TW / 2 - cam > -10 and c.x - TW / 2 - cam < 330 then
      local im = H.img("scene/tram_vintage", H.TRAM_FADE)
      local x = math.floor(c.x - cam + 0.5)
      if im then
        local L0 = x - math.floor(im:getWidth() / 2)
        local wh = H.img("scene/tram_vintage_wheel", H.TRAM_FADE)   -- the wheels turn behind the still body
        local q = H.strip(wh, wh and wh:getHeight() or 1)
        lg.setColor(1, 1, 1, 1)
        if q and #q > 0 then
          local f = q[1 + math.floor(-c.x / H.TRAM_WHEEL_PX) % #q]
          local r = math.floor(wh:getHeight() / 2)
          for _, wx in ipairs(H.TRAM_ART.wheels) do lg.draw(wh, f, L0 + wx - r, l.y1 - H.TRAM_ART.wheelY - r) end
        end
        lg.draw(im, L0, l.y1 - im:getHeight())
      else tramCode(x, l.y1, c.x, c) end
    end
    -- (in front of it; art/dt-audit-06nov: the tall Downtown draws it after the shelter, H.drawTownStops, so the
    -- shelter's glass reflections no longer cross the roundel: it read as a "no trams" sign)
    if not s.stopAfterShelter and l.stop - cam > -20 and l.stop - cam < 340 then stopSign(math.floor(l.stop - cam), l.y1) end
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
-- layer plan decision 6d (26 Oct): the loggia and the galleries stand a stone darker than the houses behind them (their art
-- measured 147 against 128 to 154); a multiplier on the colour at draw time. (art/dt-roofs-06nov: the redrawn roof kit
-- is in the sample screen's granite, about 103 on screen against the houses' 145 to 152, so no tint is needed)
H.STONE_TINT = {}
H.SPIRE_DRIFT = 0.03                                      -- the far spire's scroll (was 0.3: on screen only from camera x 2727)
local function tallTown(def) return def.art == "town" and def.foot ~= nil end
local function high(def, p) return p.y0 <= def.foot - 120 end           -- the high road (the street is def.foot)
local function slug(n) return (n:lower():gsub("[^%w]+", "_")) end
-- (night/06nov-dt, fix round 2) the closed street: the fronts that fill the squares at both ends and the canal gap
-- (box property `closed`, objects 289-310). Off by default: decision 6a (owner, 26 Oct: the spire on screen) holds,
-- decision 2 is open; true closes the street in one line.
H.CLOSED_STREET = false
local function isFront(p)
  if p.closed and not H.CLOSED_STREET then return false end
  return p.kind == "decor" and p.layer == "back" and (p.name == "" or p.name == nil or p.name == "BAKERY" or p.name == "GUILD HOUSE")
    and p.x1 - p.x0 >= 48 and p.y1 - p.y0 >= 100
end
H.PLAZA_FRONTS = true   -- (decision 2a, the owner's call; art/dt-highroad-06nov) true: the plaza balconies stand on the
                        -- big fronts' own ground floor (doors 2.1 m; a plain wall bay, town_front_tall5, where a door
                        -- or gate would be behind a balcony; a French window behind each balcony). false: the old
                        -- quarter-scale plaza houses (town_house1-3) stand behind them, as on art/dt-roofs-06nov.
local FEATURE = { [1] = 26, [2] = 32, [3] = 35 }                    -- a bay's door, shop or gate: half its width
local function plazaBalconies(def)                                   -- the balconies on the street's houses (not high)
  local out = {}
  for _, q in ipairs(def.props) do
    if q.name == "BALCONY" and q.layer == "play" and q.y0 > (def.foot or 424) - 120 then out[#out + 1] = q end
  end
  return out
end
local function guildArt() return H.FIRST_FLOOR and love.filesystem.getInfo("art/scene/town_front_tall6.png") ~= nil end
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
local function drawImgOn(im, p, x, ytop, tint)
  tint = tint or 1; lg.setColor(tint, tint, tint, 1); lg.draw(im, math.floor(x + (p.x1 - p.x0) / 2 - im:getWidth() / 2), math.floor(ytop))
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
-- (art/dt-highroad-06nov) a ledge of the high road is carried by the wall: the balcony's corbel (town_console.png,
-- tools/build_highroad.py) under both its ends, its top row on the slab's ink row (the box's top + 4)
H.CONSOLE_IN = 2
-- (art/dt-audit-06nov) the audit: "floating shelves". The flower ledge's slab gets a granite corbel under each end
-- (the 4 px gaps outside its end boxes) and an iron hanger in each 3 px gap between its window boxes, so the slab and
-- its boxes are carried by the wall. ix, iy: the art's top-left (town_roof_flower_roof.png, 90 x 14), iw its width.
local GRANITE = { { 135 / 255, 130 / 255, 120 / 255 }, { 110 / 255, 103 / 255, 95 / 255 }, { 77 / 255, 72 / 255, 68 / 255 } }
local STEEL = { { 88 / 255, 100 / 255, 112 / 255 }, { 64 / 255, 74 / 255, 86 / 255 } }
function H.flowerBrackets(ix, iy, iw)
  for _, cx in ipairs({ ix, ix + iw - 4 }) do                          -- the end corbels, stepped in 1 px a side
    rect(INK, cx, iy + 6, 4, 2); rect(GRANITE[1], cx + 1, iy + 6, 1, 1); rect(GRANITE[2], cx + 2, iy + 6, 1, 1)
    rect(GRANITE[2], cx + 1, iy + 7, 2, 1)
    rect(INK, cx + 1, iy + 8, 2, 3); rect(GRANITE[3], cx + 1, iy + 8, 1, 2)
  end
  for gx = ix + 18, ix + iw - 21, 17 do                                 -- the iron hangers between the boxes
    rect(INK, gx, iy + 6, 3, 8); rect(STEEL[1], gx + 1, iy + 6, 1, 6); rect(STEEL[2], gx + 1, iy + 12, 1, 1)
  end
  lg.setColor(1, 1, 1, 1)
end
function H.consoles(p, x)
  local im = H.FIRST_FLOOR and H.img("scene/town_console")
  if not im then return end
  lg.setColor(1, 1, 1, 1)
  for _, cx in ipairs({ x + H.CONSOLE_IN, x + (p.x1 - p.x0) - H.CONSOLE_IN - im:getWidth() }) do lg.draw(im, math.floor(cx), p.y0 + 4) end
end
-- (day/07nov-dt, option A: the owner's pick, 7 Nov) the LOW ROW: the street is lined with low true-scale buildings
-- whose roofs are the high road (tools/build_dt_rooftops.py writes riverwalk/dt_lowrow.lua and the dtl_*.png files).
-- Each building claims the map boxes it draws or hides: its roof (a play piece, outlined, drawn unfaded when the
-- building's trigger box is drawn), its canopies (the middle tier's boxes), the old balcony / house / front boxes
-- (hidden). The fronts are decoration drawn in H.drawTownBack (faded as the fronts were). With the file absent
-- nothing changes.
local LOW = love.filesystem.getInfo("dt_lowrow.lua") and require("dt_lowrow") or nil
H.LOW_ROW = LOW ~= nil
local LOWC, LOWCAN = {}, {}
if LOW then
  for _, b in ipairs(LOW) do
    for _, c in ipairs(b.claims) do LOWC[c[1] .. "," .. c[2]] = b end
    for _, c in ipairs(b.canopies) do LOWCAN[c[1] .. "," .. c[2]] = c end
    if b.trigger then b.trig = b.trigger[1] .. "," .. b.trigger[2] end
  end
end
function H.lowRowPiece(p, camx)
  local key = p.x0 .. "," .. p.y0
  local b = LOWC[key]
  if not b then return false end
  if b.roof and b.trig == key then
    local im = H.img("scene/" .. b.roof)
    if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(b.rx - camx), b.ry) end
  end
  local c = LOWCAN[key]
  if c then
    local im = H.img("scene/" .. c[3])
    if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(c[4] - camx), c[5]) end
  end
  return true
end

-- a high road piece or a back piece of the tall Downtown (from Sc.drawPropArt): true when it is drawn (or drawn
-- elsewhere: the fronts and the spire, H.drawTownBack)
function H.townPiece(p, camx, def)
  if not tallTown(def) then return false end
  if H.LOW_ROW and p.layer ~= "front" and H.lowRowPiece(p, camx) then return true end
  if p.closed and not H.CLOSED_STREET then return true end           -- (fix round 2: an open square, nothing drawn)
  if p.layer == "back" and (isFront(p) or p.name == "RIDDARHOLMEN") then return true end   -- (H.drawTownBack)
  -- layer plan decision 4a (owner, 26 Oct; art/dt-sample-05nov): the cargo bike's hiding places stand at true scale
  -- behind her (H.drawTownGateways, H.drawTownStops); their old tops, her perches, are the baker's bread crates, drawn
  -- in their own pass before the cargo bikes so the rider is never cut by them (H.drawTownPerches, review round 1).
  -- A GATE with no house front to hold its gateway (screen 10) keeps the old gate piece.
  if H.FIRST_FLOOR and p.layer == "play" then
    if p.name == "GATE" and H.gatewayX(def, p) and H.img("scene/town_crates" .. (p.x1 - p.x0)) then return true end
    if p.name == "GATE" and not H.gatewayX(def, p) and H.freeGate(p) then return true end   -- (6 Nov: screen 10's gate)
    if p.name == "SHELTER" and H.img("scene/town_breadboard") then return true end
  end
  if p.name == "HOUSE" and H.PLAZA_FRONTS and H.FIRST_FLOOR then             -- (decision 2a) the old plaza house is
    for _, q in ipairs(plazaBalconies(def)) do                                -- not drawn under a balcony: the big
      if q.x1 > p.x0 and q.x0 < p.x1 then return true end                     -- front's own ground floor is there
    end
  end
  if p.layer ~= "play" or p.kind == "decor" or not high(def, p) then return false end
  local x = math.floor(p.x0 - camx)
  local n = p.name or ""
  local g = gable(def)
  if g and g.set[p] then                                               -- the stepped gable: drawn once, with its first step
    if p ~= g[1] then return true end
    local im = H.FIRST_FLOOR and (guildArt() and H.img("scene/town_guild_steps") or H.img("scene/town_portal_top")) or H.img("scene/town_roof_gable")
    -- (art/dt-highroad-06nov: the stone coping of the guild house's granite ground floor, town_front_tall6; else 1a:
    -- the stepped gable becomes the guild house's portal top, its steps where they were; tools/build_dt_street.py)
    if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(g.x0 - camx) - 1, g.top - 1); return true end
    for q in pairs(g.set) do local qx = math.floor(q.x0 - camx); rect(INK, qx - 1, q.y0 - 1, q.x1 - q.x0 + 2, 10); brickFace(qx, q.y0 + 2, q.x1 - q.x0, 7); rect(STONE, qx, q.y0, q.x1 - q.x0, 2) end
    lg.setColor(1, 1, 1, 1); return true
  end
  if n == "" or KIT[n] then
    local w = p.x1 - p.x0
    if n == "FOOTBRIDGE" then
      local im = H.img("scene/town_footbridge")
      if im then
        -- (night/06nov-dt) the arch's feet on granite springers on the two house corners, under its iron plates
        local sp = H.img("scene/town_bridge_springer")
        if sp then
          local bx = math.floor(x + w / 2 - im:getWidth() / 2)          -- (the art's left, as drawImgOn)
          local fy = math.floor(p.y0 - 1 - H.BRIDGE_RAIL) + 42           -- (art row 42: the plate's foot less 2)
          lg.setColor(1, 1, 1, 1)
          lg.draw(sp, bx + 3 - sp:getWidth(), fy)
          lg.draw(sp, bx + im:getWidth() - 3 + sp:getWidth(), fy, 0, -1, 1)
        end
        drawImgOn(im, p, x, p.y0 - 1 - H.BRIDGE_RAIL); return true
      end
    elseif n == "CHIMNEY" and guildArt() and H.img("scene/town_guild_pier") then   -- (art/dt-highroad-06nov: a stone
      drawImgOn(H.img("scene/town_guild_pier"), p, x, p.y0 - 1); return true         -- pedestal on the steps' landing)
    elseif n == "CHIMNEY" and H.FIRST_FLOOR and H.img("scene/town_oriel") then   -- (decision 1a: the chimney becomes
      drawImgOn(H.img("scene/town_oriel"), p, x, p.y0 - 1); return true          -- the roof of the guild house's bay
                                                                               -- window, H.drawTownBays; its flat top
                                                                               -- the perch with the golden bone)
    elseif n == "DORMER" and H.FIRST_FLOOR and H.img("scene/town_roof_ledge") then   -- (review round 1: no window
      threeSlice(H.img("scene/town_roof_ledge"), x, p.y0, w); H.consoles(p, x); return true   -- under it: a ledge)
    elseif n ~= "" then
      local im = H.img("scene/town_roof_" .. slug(n) .. w) or H.img("scene/town_roof_" .. slug(n))
      if im then
        drawImgOn(im, p, x, p.y0 - 1, H.STONE_TINT[n])                         -- (a draw-time tint: the art file is not changed)
        if n == "FLOWER ROOF" then H.flowerBrackets(math.floor(x + w / 2 - im:getWidth() / 2), p.y0 - 1, im:getWidth()) end
        return true
      end
    else
      local im = H.img("scene/town_roof_ledge")
      if im then threeSlice(im, x, p.y0, w); H.consoles(p, x); return true end
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
local SRC = { { 135, 106, 66 }, { 116, 85, 53 } }                    -- the art's plaster: wall, shade (0-255)
-- (art/dt-sample-05nov, review round 1: the houses sit below the far layers on screen, about 146 to 156 after the
-- back fade and shader, the old town row 168, the far roofs 169 to 176; each colour set from its on-screen luma)
H.PLASTER = {
  yellow = SRC,
  red = { { 154, 82, 63 }, { 127, 64, 51 } },
  cream = { { 129, 115, 88 }, { 110, 94, 68 } },
  ochre = { { 137, 101, 66 }, { 114, 81, 53 } },
  stone = { { 115, 105, 96 }, { 96, 86, 78 } },
}
H.PLASTER_ORDER = { "yellow", "red", "cream", "ochre", "stone" }
local COPING = { { 222 / 255, 214 / 255, 198 / 255 }, { 176 / 255, 166 / 255, 152 / 255 }, { 116 / 255, 108 / 255, 102 / 255 } }
local function plasterImg(name, plaster)                            -- art/scene/<name>.png, plaster swapped, faded
  local key = name .. plaster .. "#" .. Look.key
  if frontCache[key] == nil then
    frontCache[key] = false
    local path = "art/scene/" .. name .. ".png"
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
-- (night/06nov-dt, the facade lift) a box's `style` (a .. f, tools/build_dt_facades.py) picks its storeys' windows,
-- cornices, shutters, window boxes, anchors, shop paint and door sign; without the styled file the 5 Nov front is drawn
H.STYLED = true
local function frontImg(k, plaster, style)
  if H.STYLED and style then
    local im = love.filesystem.getInfo("art/scene/town_front_tall" .. k .. "_" .. style .. ".png") and plasterImg("town_front_tall" .. k .. "_" .. style, plaster)
    if im then return im end
  end
  return plasterImg("town_front_tall" .. k, plaster)
end
local function bays(p, W, def)                                            -- { { front, x, w }, ... } for a box
  local list = {}
  W = W or p.x1 - p.x0
  if p.fronts then for k in tostring(p.fronts):gmatch("%d") do list[#list + 1] = tonumber(k) end end
  if def and H.FIRST_FLOOR and #list > 1 and love.filesystem.getInfo("art/scene/town_pilaster.png") then
    for _, q in ipairs(def.props) do                                  -- (art/dt-highroad-06nov) a house under the
      if q.name == "LOGGIA" and q.layer == "play" and q.x0 >= p.x0 and q.x1 <= p.x0 + W then
        -- (night/06nov-dt) the portal's house as one 148 px bay with two window axes (town_front_tall7_<style>)
        list = { (H.STYLED and p.style and love.filesystem.getInfo("art/scene/town_front_tall7_" .. p.style .. ".png")) and 7 or list[1] }
      end
    end                                                               -- LOGGIA is one bay: its gate centred under the
  end                                                                 -- loggia, the portal (H.drawHighWall)
  if H.FIRST_FLOOR and p.name == "GUILD HOUSE" then list = { guildArt() and 6 or 4 } end   -- (its own 148 px front;
  -- art/dt-highroad-06nov: town_front_tall6, the stepped line is its granite ground floor's top)
  local n = #list > 0 and #list or math.max(1, math.floor(W / 88 + 0.5))
  local base, extra, x, out = math.floor(W / n), W - math.floor(W / n) * n, p.x0, {}
  for b = 1, n do
    local bw = base + (b <= extra and 1 or 0)
    out[b] = { list[b], x, bw }; x = x + bw
  end
  -- (decision 2a) no door, shop or gate behind a plaza balcony: that bay is the plain wall (town_front_tall5)
  if def and H.PLAZA_FRONTS and H.FIRST_FLOOR and love.filesystem.getInfo("art/scene/town_front_tall5.png") then
    for _, b in ipairs(out) do
      local hw = FEATURE[b[1] or 0]
      if hw then
        local c = b[2] + b[3] / 2
        for _, q in ipairs(plazaBalconies(def)) do if q.x1 > c - hw and q.x0 < c + hw then b[1] = 5 end end
      end
    end
  end
  return out
end
-- layer plan decision 1a (owner, 26 Oct; art/dt-sample-05nov): the houses run on past the top of the screen. A front
-- box whose `cut` property is not set is drawn at its full height (the files are 432 px: the ground floor and two upper
-- storeys, the top at y -18, never on screen), with no coping. The guild house too (review round 1, pick 1a as
-- written): its front is town_front_tall4 (148 px, the gate under the portal top, the upper windows at the sides),
-- its stepped gable is drawn as the portal top and its chimney as the bay window's roof (townPiece). A box with
-- `cut` = true still ends at its top.
H.FIRST_FLOOR = true
local function cutAtTop(p) return not H.FIRST_FLOOR or p.cut end
local function drawBay(f, x, w, y0, y1, full)
  local ih = full and f.h or math.min(f.h, y1 - y0)
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

local decoCache = {}
local function decoImg(n)
  local key = n .. "#" .. Look.key
  if decoCache[key] == nil then
    decoCache[key] = false
    local path = "art/scene/" .. n .. ".png"
    if love.filesystem.getInfo(path) then
      local im = lg.newImage(Sc.fadeData(love.image.newImageData(path))); im:setFilter("nearest", "nearest"); decoCache[key] = im
    end
  end
  return decoCache[key]
end
-- (day/07nov-dt, round 2) the fountain's jets: two 2 px arcs from the column's capital (y 304) out over the bowl into
-- the basin's water band (y 418), a highlight running down each; drawn by Sc.drawTerrainArt before the play props,
-- so the column stands in front of the arcs' first pixels (they come out of the capital)
function H.drawLowFountainJets(f, camx, t)
  local cx = math.floor((f.x0 + f.x1) / 2 - camx)
  local n = 28
  for _, dir in ipairs({ -1, 1 }) do
    for i = 2, n do
      local k = i / n
      local x = cx + dir * math.floor(4 + 46 * k + 0.5)
      local y = math.floor(304 - 16 * k + 130 * k * k + 0.5)
      local hl = (math.floor(t * 18 + (dir < 0 and 7 or 0)) % n) == i
      if hl then lg.setColor(0.98, 0.99, 1.0) else lg.setColor(0.72, 0.86, 0.95) end
      lg.rectangle("fill", x - (dir < 0 and 1 or 0), y, 2, 2)
    end
  end
  lg.setColor(1, 1, 1, 1)
end
-- (round 4) drawn with the ungraded quay wall (stage.lua, Look.off()): the fountain basin's outer face below the street
function H.drawLowRaw(def, cam)
  local im = H.img("scene/dtl_fountain_face")
  if im and 1848 - cam > 0 and 1736 - cam < 320 then lg.setColor(1, 1, 1, 1); lg.draw(im, 1736 - math.floor(cam), def.foot) end
end
function H.drawLowRow(def, cam)
  for _, b in ipairs(LOW) do
    if b.front and b.x1 - cam > -20 and b.x0 - cam < 340 then
      local im = decoImg(b.front)
      if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(b.fx - cam), b.fy) end
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
  if H.LOW_ROW then                                                  -- (day/07nov-dt) the low row's fronts
    H.drawLowRow(def, cam)
    H.drawTownGateways(def, cam, true)                               -- only the free courtyard gate (screen 10)
    lg.setColor(1, 1, 1, 1)
    return
  end
  if frontImg(1, "yellow") then                                      -- the fronts' art (all three) is there
    local nb = 0
    -- (decision 1a) a full-height house closes a gap of up to 8 px to the next front (else a sliver of sky shows
    -- between two houses all the way up): its last bay runs on to the next front
    local nextX = {}
    for _, p in ipairs(def.props) do
      if isFront(p) then
        for _, q in ipairs(def.props) do
          if q ~= p and isFront(q) and q.x0 > p.x1 and q.x0 - p.x1 <= 8 then nextX[p] = q.x0 end
        end
      end
    end
    for _, p in ipairs(def.props) do
      if isFront(p) then
        nb = nb + 1
        local plaster = p.plaster or H.PLASTER_ORDER[(nb - 1) % #H.PLASTER_ORDER + 1]
        if p.x1 - cam > -20 and p.x0 - cam < 330 then
          local full = not cutAtTop(p)
          local top, px1 = p.y0, (full and nextX[p]) or p.x1
          for bi, b in ipairs(bays(p, px1 - p.x0, def)) do
            local f = frontImg(b[1] or ((nb + bi) % 3 + 1), plaster, p.style) or frontImg(1, plaster)
            drawBay(f, math.floor(b[2] - cam), b[3], p.y0, p.y1, full)
            if full then top = math.min(top, p.y1 - f.h) end
          end
          local x0, x1 = math.floor(p.x0 - cam), math.floor(px1 - cam)
          local sh = Sc.fadeC({ H.PLASTER[plaster][2][1] / 255 * 0.86, H.PLASTER[plaster][2][2] / 255 * 0.86, H.PLASTER[plaster][2][3] / 255 * 0.86 })
          rect(sh, x1 - 2, top, 2, p.y1 - top)                         -- the building's right edge in shade
          if full and p.pipe and H.STYLED then                           -- (night/06nov-dt) a downpipe at its right edge
            local dp = decoImg("town_drainpipe")
            if dp then lg.setColor(1, 1, 1, 1); lg.draw(dp, x1 - 8, p.y1 - dp:getHeight()) end
          end
          if not full then
            rect(faded(COPING[1]), x0 - 1, p.y0, x1 - x0 + 2, 1)       -- the coping on the cut
            rect(faded(COPING[2]), x0 - 1, p.y0 + 1, x1 - x0 + 2, 2)
            rect(faded(COPING[3]), x0 - 1, p.y0 + 3, x1 - x0 + 2, 1)
          end
        end
      end
    end
    if H.drawFlanks then H.drawFlanks(def, cam) end                  -- (fix round 2) quoins where a front meets a square
    H.drawTownGateways(def, cam)
    H.drawTownBays(def, cam)
    H.drawHighWall(def, cam)
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

-- (decision 4a, art/dt-sample-05nov; review round 1) the courtyard gateway at true scale, 3 m (138 px): an arch in a
-- house's ground floor, centred in the house (the bay) whose front holds the GATE's right end, the bike's way out;
-- decoration on the back line (y 414), faded as the fronts, drawn with them (the tram passes in front). No house
-- front there (screen 10): no gateway, and the GATE keeps its old piece (townPiece). tools/build_dt_street.py.
H.BACK_LINE = 10                                         -- the back line: 10 px behind her street (def.foot - 10)
local gwCache = setmetatable({}, { __mode = "k" })
function H.gatewayX(def, p)                              -- the gateway's centre x for a GATE, or nil
  gwCache[def] = gwCache[def] or {}
  local c = gwCache[def]
  if c[p] == nil then
    c[p] = false
    if love.filesystem.getInfo("art/scene/town_gateway.png") then
      local ex = p.x1 - 1
      for _, q in ipairs(def.props) do
        if isFront(q) and not cutAtTop(q) and not q.nogate and ex >= q.x0 and ex < q.x1 then   -- (night/06nov-dt:
          -- a front with `nogate` keeps the free courtyard gate standing in front of it, screen 10)
          for _, b in ipairs(bays(q, nil, def)) do if ex >= b[2] and ex < b[2] + b[3] then c[p] = b[2] + b[3] / 2 end end
        end
      end
    end
  end
  return c[p] or nil
end
-- (art/dt-built-06nov, the board's redraw of town_tramshed96, "look at the size in the scene") a GATE with no house
-- front to hold a gateway (screen 10, x 3072-3168) gets the courtyard gate at true scale: the same gateway (3 m) in a
-- stretch of plastered courtyard wall 3.5 m high (town_tramshed96.png, 160 x 161, decoration, faded as the fronts),
-- centred on the box, standing on the back line; its solid box, her perch, is the gateway's granite doorstep
-- (town_gatestep<w>.png, play, outlined, at x0 - 1, y0 - 1, drawn with the other perches). tools/build_dt_built.py.
function H.freeGate(p)
  local w = p.x1 - p.x0
  local im = decoImg("town_tramshed" .. w)
  if im and im:getHeight() > 100 and H.img("scene/town_gatestep" .. w) then return im end
  return nil
end
function H.drawTownGateways(def, cam, freeOnly)
  if not (tallTown(def) and H.FIRST_FLOOR) then return end
  local im = decoImg("town_gateway")
  for _, p in ipairs(def.props) do
    if p.name == "GATE" and p.layer == "play" then
      local cx = H.gatewayX(def, p)
      local free = not cx and H.freeGate(p)
      if free then
        local x = math.floor((p.x0 + p.x1) / 2 - free:getWidth() / 2 - cam)
        if x < 330 and x + free:getWidth() > -10 then lg.setColor(1, 1, 1, 1); lg.draw(free, x, def.foot - H.BACK_LINE - free:getHeight()) end
      elseif cx and im and not freeOnly then                        -- (the low row bakes the gateway into its shed)
        local x = math.floor(cx - im:getWidth() / 2 - cam)
        if x < 330 and x + im:getWidth() > -10 then lg.setColor(1, 1, 1, 1); lg.draw(im, x, def.foot - H.BACK_LINE - im:getHeight()) end
      end
    end
  end
end
-- (decision 1a, review round 2) the guild house's bay window: decoration under the copper roof that is the CHIMNEY's
-- perch (town_oriel.png, townPiece), centred on the box, its bottom on the box's bottom (the portal top's crown); drawn
-- with the fronts, faded as they are. tools/build_dt_street.py town_oriel_bay.png.
function H.drawTownBays(def, cam)
  if not (tallTown(def) and H.FIRST_FLOOR) or guildArt() then return end
  local im = decoImg("town_oriel_bay")
  if not im then return end
  for _, p in ipairs(def.props) do
    if p.name == "CHIMNEY" and p.layer == "play" and p.x1 - cam > -40 and p.x0 - cam < 360 then
      lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor((p.x0 + p.x1) / 2 - im:getWidth() / 2 - cam), p.y1 - im:getHeight())
    end
  end
end
-- (art/dt-audit-06nov) the audit: the glass's pale diagonal reflection ran through the tram roundel, so the sign read
-- as "no trams". A copy of the shelter (the file is not changed) without the reflection pixels (its one stroke
-- colour, 150 166 174) in the columns round the sign's pole (col - 16 .. col + 10), faded as decoImg does.
local clearCache = {}
function H.shelterClear(col)
  local key = col .. "#" .. Look.key
  if clearCache[key] == nil then
    clearCache[key] = false
    local path = "art/scene/town_shelter_tall.png"
    if love.filesystem.getInfo(path) then
      local d = love.image.newImageData(path)
      d:mapPixel(function(x, y, r, g, b, a)
        if a > 0 and x >= col - 16 and x <= col + 10 and math.floor(r * 255 + 0.5) == 150 and math.floor(g * 255 + 0.5) == 166 and math.floor(b * 255 + 0.5) == 174 then return 0, 0, 0, 0 end
        return r, g, b, a
      end)
      local im = lg.newImage(Sc.fadeData(d)); im:setFilter("nearest", "nearest"); clearCache[key] = im
    end
  end
  return clearCache[key]
end
-- (decision 4a) the tram stop shelter at true scale, 2.5 m (115 px): decoration on the back line, faded; drawn after
-- the tram (stage.lua), which stops behind it.
function H.drawTownStops(s, cam)
  local def = s.def
  if not (tallTown(def) and H.FIRST_FLOOR) then return end
  local sh = decoImg("town_shelter_tall")
  if not sh then return end
  s.stopAfterShelter = true                                         -- (H.drawTrams leaves the stop sign to us)
  for _, p in ipairs(def.props) do
    if p.name == "SHELTER" and p.layer == "play" and p.x1 - cam > -100 and p.x0 - cam < 420 then
      local left = math.floor((p.x0 + p.x1) / 2 - sh:getWidth() / 2)
      local im = sh
      for _, tl in ipairs(s.trams or {}) do                          -- a stop sign over its glass: that glass
        local col = tl.lane.stop + 1 - left                          -- pane's reflection kept off the roundel
        if col > 0 and col < sh:getWidth() then im = H.shelterClear(col) or sh end
      end
      lg.setColor(1, 1, 1, 1)
      lg.draw(im, left - math.floor(cam), def.foot - H.BACK_LINE - sh:getHeight())
    end
  end
  for _, tl in ipairs(s.trams or {}) do                              -- the stop sign, in front of the shelter's glass
    local l = tl.lane
    if l.stop - cam > -20 and l.stop - cam < 340 then stopSign(math.floor(l.stop - cam), l.y1) end
  end
  lg.setColor(1, 1, 1, 1)
end
-- (decision 4a, review round 1) the perches of the hiding places, play pieces with their 1 px outline, drawn before
-- the cargo bikes (stage.lua) so the rider passes in front of them, never cut at the waist: the GATE's crates
-- (town_crates<w>.png at x0 - 1, y0 - 1, only where the gateway stands), the SHELTER's baker's board
-- (town_breadboard.png, x0 - 1, y0 - 1) on two stacks of the same bread crates end-on (town_crate_leg.png, at the
-- box's two ends, on her street).
function H.drawTownPerches(s, cam)
  local def = s.def
  if not (tallTown(def) and H.FIRST_FLOOR) then return end
  local board, leg = H.img("scene/town_breadboard"), H.img("scene/town_crate_leg")
  for _, p in ipairs(def.props) do
    if p.layer == "play" and p.x1 - cam > -20 and p.x0 - cam < 340 then
      if p.name == "GATE" then
        local im = H.gatewayX(def, p) and H.img("scene/town_crates" .. (p.x1 - p.x0))
          or (H.freeGate(p) and H.img("scene/town_gatestep" .. (p.x1 - p.x0)))   -- (6 Nov: the free gate's doorstep)
        if im then
          Sc.shadow((p.x0 + p.x1) / 2 - cam, p.y1 - 1, p.x1 - p.x0 + 4)
          lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(p.x0 - cam) - 1, p.y0 - 1)
        end
      elseif p.name == "SHELTER" and board then
        lg.setColor(1, 1, 1, 1)
        if leg then
          for _, lx in ipairs({ p.x0 - 1, p.x1 + 1 - leg:getWidth() }) do
            Sc.shadow(lx + leg:getWidth() / 2 - cam, def.foot - 1, leg:getWidth() + 2)
            lg.setColor(1, 1, 1, 1); lg.draw(leg, math.floor(lx - cam), def.foot - leg:getHeight())
          end
        end
        lg.draw(board, math.floor(p.x0 - cam) - 1, p.y0 - 1)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end


-- ===================================================================================================================
-- (art/dt-highroad-06nov) the high road attached to its house fronts. The owner on the roofs frames (6 Nov): "this
-- looks weird": the true-scale fronts (decision 1a) run past the top of the screen and the high road's pieces hung in
-- the middle of their walls. Drawn on the fronts here (decoration, faded, after the fronts, before the back props),
-- each from its file (tools/build_highroad.py), nothing drawn when it is not there:
--   the galleries' string course: the fronts' own course (granite lit, three mid, a dark lip) under the balustrades'
--     plinth (the box's top + 31), along the whole front of every house a gallery stands on (on the guild house only
--     under the gallery), so the balustrade stands on the facade
--   the loggia's pilasters (town_pilaster.png): from its foot (top + 25) to the plinth, 3 px in from its ends, so the
--     loggia is the entablature of the carriage gate's portal
--   a first-floor balcony's door (town_window_door.png): the upper window over it carried down to its slab
--   a plaza balcony's French window (town_balcony_door.png, decision 2a only): under the string course's line (the
--     front's foot - 119), cut at the slab; the guild house has its two in its own front (town_front_tall6)
--   cast shadows: every piece of the high road and every balcony throws its own silhouette 2 px right and 3 px down
--     on the wall (light from the upper left), multiplied so the wall's plaster turns exactly into its own shade (the
--     front's S over W, through the look) and a cornice or window under it a step darker
H.SHADOW_DX, H.SHADOW_DY = 2, 3
local frontList = setmetatable({}, { __mode = "k" })
local function frontsOf(def)                                         -- the fronts in order, their plaster and right end
  if frontList[def] then return frontList[def] end
  local out, nb = {}, 0
  for _, p in ipairs(def.props) do
    if isFront(p) then
      nb = nb + 1
      local x1 = p.x1
      if not cutAtTop(p) then
        for _, q in ipairs(def.props) do if q ~= p and isFront(q) and q.x0 > p.x1 and q.x0 - p.x1 <= 8 then x1 = q.x0 end end
      end
      out[#out + 1] = { p = p, plaster = p.plaster or H.PLASTER_ORDER[(nb - 1) % #H.PLASTER_ORDER + 1], x1 = x1 }
    end
  end
  frontList[def] = out; return out
end
local function frontAt(def, x)
  for _, f in ipairs(frontsOf(def)) do if x >= f.p.x0 and x < f.x1 and not cutAtTop(f.p) then return f end end
end
local function grade(c)                                              -- the look's back shader (look.lua SRC) on the CPU
  if not Look.on then return c end
  local sc = Look.scripts and Look.scripts[Look.key]
  local q = sc and sc.layers and (sc.layers.back or sc.layers.play)
  if not q then return c end
  local r, g, b = c[1], c[2], c[3]
  local L = 0.299 * r + 0.587 * g + 0.114 * b
  r, g, b = L + (r - L) * q.sat, L + (g - L) * q.sat, L + (b - L) * q.sat
  local w, k = q.warm * L * L, q.cool * (1 - L) * (1 - L)
  r, g, b = r + w * 0.080 - k * 0.030, g + w * 0.032 - k * 0.045, b - w * 0.048 + k * 0.085
  r, g, b = r + (q.haze[1] - r) * q.k, g + (q.haze[2] - g) * q.k, b + (q.haze[3] - b) * q.k
  local function cl(v) return math.max(0, math.min(1, v)) end
  return { cl(r), cl(g), cl(b) }
end
local STONE_SHADE = { { 110, 103, 95 }, { 77, 72, 68 } }             -- granite: its stone and shade (the fronts' T, V)
local function shadeRatio(plaster)                                   -- what turns the wall into its shade on screen
  local pl = plaster == "granite" and STONE_SHADE or H.PLASTER[plaster] or SRC
  local w = grade(Sc.fadeC({ pl[1][1] / 255, pl[1][2] / 255, pl[1][3] / 255 }))
  local s = grade(Sc.fadeC({ pl[2][1] / 255, pl[2][2] / 255, pl[2][3] / 255 }))
  return { math.min(1, s[1] / math.max(w[1], 1e-3)), math.min(1, s[2] / math.max(w[2], 1e-3)), math.min(1, s[3] / math.max(w[3], 1e-3)) }
end
local maskCache = {}
local function shadowMask(name, plaster)                             -- the art's silhouette in the shade ratio, white round it
  local key = name .. "#" .. plaster .. "#" .. Look.key .. tostring(Look.on)
  if maskCache[key] == nil then
    maskCache[key] = false
    local path = "art/scene/" .. name .. ".png"
    if love.filesystem.getInfo(path) then
      local r = shadeRatio(plaster)
      local d = love.image.newImageData(path)
      d:mapPixel(function(x, y, cr, cg, cb, a) if a > 0 then return r[1], r[2], r[3], 1 end return 1, 1, 1, 1 end)
      local im = lg.newImage(d); im:setFilter("nearest", "nearest"); maskCache[key] = im
    end
  end
  return maskCache[key]
end
local oldForget = H.forget
H.forget = function() oldForget(); maskCache = {} end
local function course(x0, x1, y)                                     -- the fronts' string course (5 rows), faded
  local L, T, V = faded({ 135 / 255, 130 / 255, 120 / 255 }), faded({ 110 / 255, 103 / 255, 95 / 255 }), faded({ 77 / 255, 72 / 255, 68 / 255 })
  rect(L, x0, y, x1 - x0, 1); rect(T, x0, y + 1, x1 - x0, 3); rect(V, x0, y + 4, x1 - x0, 1)
end
local function upperWindowX(def, f, cx)                              -- the centre of the upper window over x in front f
  for _, b in ipairs(bays(f.p, f.x1 - f.p.x0, def)) do
    if cx >= b[2] and cx < b[2] + b[3] and b[1] and b[1] ~= 4 and b[1] ~= 6 and b[1] ~= 7 then
      local im = frontImg(b[1], f.plaster, f.p.style)
      if not im then return nil end
      local fw = im.w
      if b[3] <= fw then return b[2] + math.floor(fw / 2) - math.floor((fw - b[3]) / 2) end
      return b[2] + math.floor((b[3] - fw) / 2) + math.floor(fw / 2)
    end
  end
end
local function drawPart(im, x, y, rows)                              -- an image's top rows (all of it when rows is nil)
  local iw, ih = im:getDimensions()
  rows = math.min(ih, rows or ih)
  if rows <= 0 then return end
  lg.setColor(1, 1, 1, 1); lg.draw(im, lg.newQuad(0, 0, iw, rows, iw, ih), math.floor(x), math.floor(y))
end
function H.drawHighWall(def, cam)
  if not (tallTown(def) and H.FIRST_FLOOR) then return end
  local shadows = {}                                                 -- { name, x, y, plaster } or { rect = {x, y, w, h}, plaster }
  local function onScreen(x0, x1) return x1 - cam > -60 and x0 - cam < 380 end
  -- the galleries' string course: one band per house front, merged
  local segs = {}
  for _, g in ipairs(def.props) do
    if g.name == "GALLERY" and g.layer == "play" and high(def, g) then
      for _, f in ipairs(frontsOf(def)) do
        if not cutAtTop(f.p) and f.p.x0 < g.x1 and f.x1 > g.x0 then
          if f.p.name == "GUILD HOUSE" then segs[#segs + 1] = { math.max(g.x0, f.p.x0), math.min(g.x1, f.x1), g.y0 + 31, f.plaster }
          else segs[#segs + 1] = { f.p.x0, f.x1, g.y0 + 31, f.plaster } end
        end
      end
    end
  end
  table.sort(segs, function(a, b) return a[1] < b[1] end)
  local merged = {}
  for _, sg in ipairs(segs) do
    local m = merged[#merged]
    if m and sg[1] <= m[2] and sg[3] == m[3] then m[2] = math.max(m[2], sg[2]) else merged[#merged + 1] = { sg[1], sg[2], sg[3], sg[4] } end
  end
  for _, m in ipairs(merged) do
    if onScreen(m[1], m[2]) then
      course(m[1] - cam, m[2] - cam, m[3])
      shadows[#shadows + 1] = { rect = { m[1] - cam, m[3] + 5, m[2] - m[1], 2 }, plaster = m[4] }
    end
  end
  for _, p in ipairs(def.props) do
    local cx = (p.x0 + p.x1) / 2
    if p.layer == "play" and p.kind ~= "decor" and onScreen(p.x0, p.x1) then
      local f = frontAt(def, cx)
      local n, x = p.name or "", math.floor(p.x0 - cam)
      if p.name == "LOGGIA" and high(def, p) and f then                    -- the portal's pilasters
        local im = plasterImg("town_pilaster", f.plaster)
        if im then
          for _, px in ipairs({ p.x0 + 3, p.x1 - 3 - 12 }) do drawPart(im.im, px - cam, p.y0 + 25, f.p.y1 - 8 - (p.y0 + 25)) end
        end
      end
      if n == "BALCONY" and f then
        local im = H.img("scene/town_balcony" .. (p.x1 - p.x0))
        if high(def, p) then                                               -- a first-floor balcony: its door
          local wcx = upperWindowX(def, f, cx)
          local wd = plasterImg("town_window_door", f.plaster)
          local y = f.p.y1 - 192
          if wcx and wd and math.abs(wcx - cx) <= 8 then drawPart(wd.im, wcx - 25 - cam, y, p.y0 - y) end
          if im then shadows[#shadows + 1] = { "town_balcony" .. (p.x1 - p.x0), x - 1, p.y0 - 1 - Sc.BALCONY_RAIL, f.plaster } end
        elseif H.PLAZA_FRONTS then                                         -- a plaza balcony (decision 2a): its window
          local bd = plasterImg("town_balcony_door", f.plaster)
          if bd and not (f.p.name == "GUILD HOUSE" and guildArt()) then
            local bx = math.max(f.p.x0 + 1, math.min(math.floor(cx - 18), f.x1 - 3 - bd.w))
            local y = f.p.y1 - 119
            drawPart(bd.im, bx - cam, y, p.y0 + 2 - y)
          end
          if im then shadows[#shadows + 1] = { "town_balcony" .. (p.x1 - p.x0), x - 1, p.y0 - 1 - Sc.BALCONY_RAIL, f.plaster } end
        end
      elseif high(def, p) and f then
        local w = p.x1 - p.x0
        local g = gable(def)
        if g and g.set[p] then
          if p == g[1] and guildArt() then shadows[#shadows + 1] = { "town_guild_steps", math.floor(g.x0 - cam) - 1, g.top - 1, "granite" } end
        elseif n == "CHIMNEY" and guildArt() then shadows[#shadows + 1] = { "town_guild_pier", x - 1, p.y0 - 1, f.plaster }
        elseif n == "LOGGIA" then shadows[#shadows + 1] = { "town_roof_loggia", x + math.floor(w / 2) - 61, p.y0 - 1, f.plaster }
        elseif n == "GALLERY" then shadows[#shadows + 1] = { "town_roof_gallery" .. w, x - 1, p.y0 - 1, f.plaster }
        elseif n == "FLOWER ROOF" then shadows[#shadows + 1] = { "town_roof_flower_roof", x - 1, p.y0 - 1, f.plaster }
        elseif n == "AWNING" then                                          -- (scene.lua: centred, its top row y0 - 1)
          local an = w >= 72 and "town_awning80" or "town_awning64"
          local aim = H.img("scene/" .. an)
          if aim then shadows[#shadows + 1] = { an, x + math.floor(w / 2 - aim:getWidth() / 2), p.y0 - 1, f.plaster } end
        elseif n == "" or n == "DORMER" then                               -- a ledge: its slab and its two corbels
          local wcx = upperWindowX(def, f, cx)                             -- (under a first-floor window: a French
          local wd, wr = plasterImg("town_window_door", f.plaster), plasterImg("town_window_rail", f.plaster)   -- balcony)
          local y = f.p.y1 - 192
          if wcx and wd and wr and math.abs(wcx - cx) <= 8 and p.y0 > y + wr.h then
            drawPart(wd.im, wcx - 25 - cam, y, p.y0 - 1 - y)
            drawPart(wr.im, wcx - 22 - cam, p.y0 - 1 - wr.h)
          end
          shadows[#shadows + 1] = { rect = { x - 1, p.y0 - 1, w + 2, 6 }, plaster = f.plaster }
          for _, c in ipairs({ x + H.CONSOLE_IN, x + w - H.CONSOLE_IN - 8 }) do
            shadows[#shadows + 1] = { rect = { c, p.y0 + 4, 8, 3 }, plaster = f.plaster }
            shadows[#shadows + 1] = { rect = { c + 2, p.y0 + 7, 4, 3 }, plaster = f.plaster }
          end
        end
      end
    end
  end
  -- the shadows, multiplied (no look shader: the ratio already went through it)
  lg.setShader(); lg.setBlendMode("multiply", "premultiplied")
  for _, sh in ipairs(shadows) do
    if sh.rect then
      local r = shadeRatio(sh.plaster)
      lg.setColor(r[1], r[2], r[3], 1)
      lg.rectangle("fill", math.floor(sh.rect[1] + H.SHADOW_DX), math.floor(sh.rect[2] + H.SHADOW_DY), sh.rect[3], sh.rect[4])
    else
      local m = shadowMask(sh[1], sh[4])
      if m then lg.setColor(1, 1, 1, 1); lg.draw(m, math.floor(sh[2] + H.SHADOW_DX), math.floor(sh[3] + H.SHADOW_DY)) end
    end
  end
  lg.setBlendMode("alpha"); lg.setColor(1, 1, 1, 1)
  if Look.on then Look.use("back") end
end

-- ===================================================================================================================
-- (art/dt-audit-06nov) the tall Downtown's audit fixes drawn here (tools/build_dt_audit.py builds their art)
-- the quay wall's drain arches (town_quaydrain.png, 20 x 22, decoration): one under each front-layer prop of the
-- level, where a bollard's top showed in the quay wall as a black dome. Its bottom 2 px over the world's bottom
-- (the quay's lowest course), centred on the prop; only on a stretch of quay (never over water). Drawn with the
-- ground, after it (stage.lua).
function H.drawQuayDrains(s, cam)
  local def = s.def
  if not tallTown(def) then return end
  local im = H.img("scene/town_quaydrain")
  if not im then return end
  local w = s.world
  lg.setColor(1, 1, 1, 1)
  for _, p in ipairs(def.props) do
    if p.layer == "front" and p.x1 - cam > -30 and p.x0 - cam < 350 then
      local cx = math.floor((p.x0 + p.x1) / 2)
      local x0, x1 = cx - 10, cx + 10
      local dry = true
      for _, r in ipairs(w.water or {}) do if x1 > r.x0 and x0 < r.x1 then dry = false end end
      if dry then lg.draw(im, x0 - math.floor(cam), w.height - 2 - im:getHeight()) end
    end
  end
end
-- the footbridge's abutments (town_bridge_pier.png, 14 px wide, decoration, unfaded: part of the bridge): a granite
-- pier under each foot of the arch, from the foot (the art's last row, the box's top - 1 - H.BRIDGE_RAIL + 52) down
-- to the quay (the street, def.foot), so the arch springs from the quays. Drawn in the back pass (behind the crates).
function H.drawBridgePiers(s, cam)
  local def = s.def
  if not (tallTown(def) and H.FIRST_FLOOR) then return end
  local pier, br = H.img("scene/town_bridge_pier"), H.img("scene/town_footbridge")
  if not (pier and br) then return end
  for _, p in ipairs(def.props) do
    if p.name == "FOOTBRIDGE" and p.x1 - cam > -40 and p.x0 - cam < 360 then
      local bx = math.floor(p.x0 + (p.x1 - p.x0) / 2 - br:getWidth() / 2)     -- the bridge art's left (drawImgOn)
      local foot = p.y0 - 1 - H.BRIDGE_RAIL + br:getHeight()                 -- the row under the arch's feet
      local ph = def.foot - foot
      local q = lg.newQuad(0, pier:getHeight() - ph, pier:getWidth(), ph, pier:getDimensions())
      if ph > pier:getHeight() then q = nil end
      lg.setColor(1, 1, 1, 1)
      for _, fx in ipairs({ bx + 1, bx + br:getWidth() - 2 }) do             -- centred on each foot (3 px wide)
        local x = fx - math.floor(pier:getWidth() / 2) - math.floor(cam)
        if q then lg.draw(pier, q, x, foot) else lg.draw(pier, x, def.foot - pier:getHeight()) end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
-- a lamp on a ledge of the high road (a checkpoint): no lamp post standing on the ledge but a wall lantern, the
-- approved lamp's lantern (rows 0-26 of lamp_post.png or the lit lamp, not changed) hanging from an iron bracket on
-- the wall (town_lantern_bracket.png, 18 x 12, its hook at columns 14-15 over the lantern's finial, columns 6-7).
-- Its bottom 44 px over the ledge (Pepper passes under it). Returns the lantern's left and top (for its light).
H.LANTERN_ROWS, H.LANTERN_UP = 27, 44
-- the lantern hangs on the wall pier between two windows: the house front's bay edge nearest the lamp (a bay is one
-- window column, centred), so it never covers a window; the lamp itself (the checkpoint) does not move
local lanternXs = setmetatable({}, { __mode = "k" })
function H.lanternX(def, x)
  lanternXs[def] = lanternXs[def] or {}
  local c = lanternXs[def]
  if c[x] == nil then
    c[x] = x
    local best
    for _, q in ipairs(def.props) do
      if isFront(q) and x >= q.x0 and x < q.x1 then
        for _, b in ipairs(bays(q, nil, def)) do
          for _, e in ipairs({ b[2], b[2] + b[3] }) do if not best or math.abs(e - x) < math.abs(best - x) then best = e end end
        end
      end
    end
    if best then c[x] = best end
  end
  return c[x]
end
function H.wallLantern(im, lx, ly, def, cam)
  if H.LOW_ROW then return nil end                                   -- (day/07nov-dt) a post on the roof terrace
  local br = H.img("scene/town_lantern_bracket", true)              -- (faded as the lamp: back decoration)
  if not br then return nil end
  if def then lx = H.lanternX(def, lx + cam) - cam end
  H.lanternQ = H.lanternQ or {}
  local q = H.lanternQ[im]
  if not q then q = lg.newQuad(0, 0, im:getWidth(), H.LANTERN_ROWS, im:getDimensions()); H.lanternQ[im] = q end
  local left = math.floor(lx - im:getWidth() / 2)
  local top = ly - H.LANTERN_UP - H.LANTERN_ROWS
  lg.setColor(1, 1, 1, 1)
  lg.draw(br, left + 6 - 14, top - 6)
  lg.draw(im, q, left, top)
  return left, top
end

-- (night/06nov-dt, fix round 2) a full-height front whose flank meets an open square (no front within 8 px; with
-- H.CLOSED_STREET off: x 140, 1180, 2480, 2640, 2816) ends in dressed quoins (town_quoin.png, tools/build_dt_facades.py),
-- not a cut (the start house has them in its file, tools/build_dt_built.py)
function H.drawFlanks(def, cam)
  local q = decoImg("town_quoin")
  if not q then return end
  local fl = frontsOf(def)
  local function near(x, left)
    for _, g in ipairs(fl) do
      if not cutAtTop(g.p) then
        if left and g.x1 <= x and g.x1 >= x - 8 then return true end
        if not left and g.p.x0 >= x and g.p.x0 <= x + 8 then return true end
      end
    end
    return false
  end
  lg.setColor(1, 1, 1, 1)
  for _, f in ipairs(fl) do
    if not cutAtTop(f.p) and f.x1 - cam > -20 and f.p.x0 - cam < 340 then
      local y = f.p.y1 - q:getHeight()
      if not near(f.p.x0, true) then lg.draw(q, math.floor(f.p.x0 - cam), y) end
      if not near(f.x1, false) then lg.draw(q, math.floor(f.x1 - cam), y, 0, -1, 1) end
    end
  end
end

return H
