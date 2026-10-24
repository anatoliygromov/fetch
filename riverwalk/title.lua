-- The title screen, animated (v2, 24 Oct: docs/ui_design.md screen 1). The painting on its native grid with layers cut
-- by art/source/title/tools/build_title.py; everything moves by time t: Pepper pants (her mouth, 3 frames from the
-- owner's videos, about 8 fps) and blinks every 3 to 5 s (her open eye, 3 frames), the river sparkles twinkle, the
-- bird flaps, a shine sweeps across the logo (the logo and the tagline are their own layers, redrawn on the grid), and PRESS START blinks (fast once pressed; then the main menu opens
-- over the same picture, flow.lua). Only the pixels that change are drawn over the picture, so nothing else moves.
-- (The clouds and the sailboats stay still: they are painted into the sky and the water and cannot be lifted out
-- cleanly.)
-- Regrid (24 Oct): the picture is now the regridded composite (art/source/title/tools/build_title_regrid.py): base.png
-- holds the background, Pepper, the logo and the tagline as approved, so the default logo and plate ("regrid") draw
-- the very pixels under them and only the shine and the stars change anything there. Pepper is still for this build
-- (T.PEPPER_ANIM: the old mouth and eye frames do not match the new Pepper), the painting's bird stays in the picture
-- (T.BIRD_ANIM: the old overlay's pixels are out of style next to the new art), and the river sparkles are the new
-- water's own light ripple streaks, each dimmed to the water round it in its off phase (T.SPARKLES).
local D = require("title_data")
local R = require("title_regrid")
D.sparkle_points.regrid = R.sparkle_points
local T = {}
local lg = love.graphics
local I
local function img(n) local i = lg.newImage("art/title/" .. n .. ".png"); i:setFilter("nearest", "nearest"); return i end
local function strip(im, d)
  local q = {}
  for f = 0, d.n - 1 do q[f] = lg.newQuad(f * d.w, 0, d.w, d.h, im:getDimensions()) end
  return q
end

function T.load()
  if I then return end
  I = { base = img("base"), bird = img("bird"), mouth = img("mouth"), eye = img("eye"), logos = {},
    tagline = { caps = img("tagline_caps"), lower = img("tagline_lower"), regrid = img("tagline_regrid") } }
  for _, m in ipairs({ "clean", "bands", "gradient", "steps6", "regrid" }) do I.logos[m] = { fill = img("logo_" .. m), hi = img("logo_hi_" .. m) } end
  I.stars = img("stars"); I.starQ = {}
  for sz = 0, 2 do I.starQ[sz] = {}; for f = 0, 5 do I.starQ[sz][f] = lg.newQuad(f * 11, sz * 11, 11, 11, I.stars:getDimensions()) end end
  -- the sparkle schedule, the same every run (a seeded generator): one star at a time, the next one 0.6 to 1.4 s
  -- after the last began, at a random point on the letters' upper edges or highlight streaks, small / medium /
  -- large (the large ones rarer); and the shine's sweeps, 5 to 7 s apart. 10 minutes of it, then it repeats.
  local rng = love.math.newRandomGenerator(1994)
  T.starList, T.shineList = {}, {}
  local u = 0.9
  while u < 600 do
    local r = rng:random()
    T.starList[#T.starList + 1] = { t = u, p = rng:random(1, 100000), size = r < 0.45 and 0 or (r < 0.8 and 1 or 2) }
    u = u + 0.6 + rng:random() * 0.8
  end
  u = 2.0
  while u < 600 do T.shineList[#T.shineList + 1] = u; u = u + 5 + rng:random() * 2 end
  I.mouthQ, I.eyeQ = strip(I.mouth, D.mouth), strip(I.eye, D.eye)
  I.birdQ = {}
  for f = 0, 2 do I.birdQ[f] = lg.newQuad(f * D.bird.w, 0, D.bird.w, D.bird.h, I.bird:getDimensions()) end
end

-- Pepper: the pant, 6 steps at 8 fps (rest, rest, tongue half down, down, down, half: 0.75 s a breath); the blink,
-- half shut, shut, shut, half (12 fps), after 3.4, 4.6, 3.9 and 4.3 s in turn
T.PANT = { 0, 0, 1, 2, 2, 1 }
T.BLINK = { 1, 2, 2, 1 }
T.BLINK_GAPS = { 3.4, 4.6, 3.9, 4.3 }
function T.pepperFrames(t)
  local m = T.PANT[math.floor(t * 8) % #T.PANT + 1]
  local cycle = 0; for _, g in ipairs(T.BLINK_GAPS) do cycle = cycle + g end
  local u, e = t % cycle, 0
  for _, g in ipairs(T.BLINK_GAPS) do
    if u < g then local k = math.floor((u - (g - #T.BLINK / 12)) * 12); if k >= 0 then e = T.BLINK[k + 1] end; break end
    u = u - g
  end
  return m, e
end

-- t: seconds on the title; leaving: seconds since a button was pressed (nil before);
-- plain: the picture only (the main menu's background): no PRESS START, no fade
function T.draw(t, leaving, plain)
  T.load()
  lg.setColor(1, 1, 1, 1)
  lg.draw(I.base, 0, 0)
  -- river sparkles: each ripple streak twinkles on its own rhythm (base.png shows it lit; in its off phase it takes
  -- the water colour round it)
  if T.SPARKLES then
    for i, s in ipairs(R.ripples) do
      local ph = (s[1] * 0.37 + s[2] * 1.71 + i * 0.53) % 6.283
      if math.sin(t * (1.4 + (i % 5) * 0.25) + ph) <= -0.35 then
        lg.setColor(s[4] / 255, s[5] / 255, s[6] / 255, 1); lg.rectangle("fill", s[1], s[2], s[3], 1)
      end
    end
    lg.setColor(1, 1, 1, 1)
  end
  if T.PEPPER_ANIM then
    local m, e = T.pepperFrames(t)
    if m > 0 then lg.draw(I.mouth, I.mouthQ[m], D.mouth.x, D.mouth.y) end
    if e > 0 then lg.draw(I.eye, I.eyeQ[e], D.eye.x, D.eye.y) end
  end
  -- the bird: flaps (up, level, down, level), glides now and then, drifts a little
  if T.BIRD_ANIM then
    local f = 1
    if t % 5 < 3.2 then f = ({ 0, 1, 2, 1 })[math.floor(t / 0.14) % 4 + 1] end
    local bx = D.bird.x + math.floor(math.sin(t * 0.35) * 4 + 0.5)
    local by = D.bird.y + math.floor(math.sin(t * 0.9) * 1.2 + 0.5)
    lg.draw(I.bird, I.birdQ[f], bx, by)
  end
  -- the logo and the tagline plate as their own layers: the older plates go under the letters; the regrid plate goes
  -- over the logo (its outline and shadow reach down behind the plate), the composite's order
  local P, L = T.plateBox(), T.logoBox()
  local plate = I.tagline[T.TAGLINE] or I.tagline.regrid
  if plate ~= I.tagline.regrid then lg.draw(plate, P.x, P.y) end
  lg.draw(T.logo().fill, L.x, L.y)
  if plate == I.tagline.regrid then lg.draw(plate, P.x, P.y) end
  T.shine(t)
  T.sparkle(t)
  if plain then return end
  -- PRESS START blinks (fast once pressed), on the menu's centre line where the menu will open
  local on = leaving and (math.floor(leaving / 0.07) % 2 == 0) or (not leaving and (t % 1.1) < 0.75)
  if on and t > 0.5 then
    local U = require("hud")
    local w = U.sayW(13, "PRESS START")
    U.say(13, "gold", "PRESS START", math.floor(T.CX - (w - 1) / 2 + 0.5), T.PRESS_Y, "press")
  end
  -- fade in at the start
  if t < 0.5 then lg.setColor(0, 0, 0, 1 - t / 0.5); lg.rectangle("fill", 0, 0, 320, 240) end
  lg.setColor(1, 1, 1, 1)
end

-- the latest entry of a sorted schedule at or before t (t wraps round after 600 s)
local function latest(list, t, key)
  t = t % 600
  local lo, hi = 1, #list
  if #list == 0 or (key and list[1][key] or list[1]) > t then return nil end
  while lo < hi do
    local mid = math.floor((lo + hi + 1) / 2)
    if (key and list[mid][key] or list[mid]) <= t then lo = mid else hi = mid - 1 end
  end
  return list[lo], t
end
-- the twinkle star: 6 frames at 12 fps (grow, grow, flash, shrink, shrink, a dot), centred on its point
function T.sparkle(t)
  local s, tt = latest(T.starList, t, "t")
  if not s then return end
  local f = math.floor((tt - s.t) * 12)
  if f > 5 then return end
  local pts = D.sparkle_points[T.LOGO] or D.sparkle_points.regrid
  local p = pts[(s.p - 1) % #pts + 1]
  lg.setColor(1, 1, 1, 1); lg.draw(I.stars, I.starQ[s.size][f], p[1] - 5, p[2] - 5)
end
-- a shine sweeps across the letters every 5 to 7 s: a slanted band of the brightened letters (only the letters'
-- fill has pixels in it, so the band is clipped to them), drawn as 2-row strips through a scissor
function T.shine(t)
  local s0, tt = latest(T.shineList, t)
  local st = s0 and (tt - s0) or 99
  if st < 0.8 then
    local L = T.logoBox()
    local pos = -30 + (L.w + 60) * (st / 0.8)
    for y = 0, L.h - 1, 2 do
      local x = math.floor(pos - y * 0.45)
      if x + 8 > 0 and x < L.w then
        lg.setScissor(L.x + math.max(0, x), L.y + y, 8 + math.min(0, x), 2)
        lg.draw(T.logo().hi, L.x, L.y)
      end
    end
    lg.setScissor()
  end
end
T.LOGO = "regrid"                 -- the logo: "regrid" (the regridded logo, as baked into base.png), or the older ones drawn
                                  -- over it: "clean" (the painting's own, its speckle replaced by an ordered dither),
                                  -- "gradient" (six steps, ordered 2 x 2 dither between them), "steps6" (the six steps,
                                  -- hard), "bands" (three hard bands and a lip)
function T.logo() return I.logos[T.LOGO] or I.logos.regrid end
local OLD_LOGO = { clean = true, bands = true, gradient = true, steps6 = true }
function T.logoBox() return OLD_LOGO[T.LOGO] and D.logo or R.logo end
T.TAGLINE = "regrid"              -- the tagline plate: "regrid" (The City Dog Adventurer, regridded, as baked into
                                  -- base.png), or the older "caps" (THE CITY DOG ADVENTURER) or "lower"
function T.plateBox() return (T.TAGLINE == "caps" or T.TAGLINE == "lower") and D.plate or R.plate end
T.PEPPER_ANIM = false             -- Pepper's pant and blink (mouth.png, eye.png): off, they were cut from the old Pepper
T.BIRD_ANIM = false               -- the flapping bird overlay (bird.png): off, the painting's bird stays in base.png
T.SPARKLES = true                 -- the river ripples twinkle (title_regrid.lua ripples)
T.CX = 220                        -- the centre line under the logo (the regrid tagline plate's centre: its frame x 150..290)
T.PRESS_Y = 152                   -- PRESS START's top: the main menu's middle row
T.LEAVE = 0.45                    -- seconds from the press to the menu
return T
