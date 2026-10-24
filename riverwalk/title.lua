-- The title screen, animated (v2, 24 Oct: docs/ui_design.md screen 1). The painting on its native grid with layers cut
-- by art/source/title/tools/build_title.py; everything moves by time t: Pepper pants (her mouth, 3 frames from the
-- owner's videos, about 8 fps) and blinks every 3 to 5 s (her open eye, 3 frames), the river sparkles twinkle, the
-- bird flaps, a shine sweeps across the logo (the logo and the tagline are their own layers, redrawn on the grid), and PRESS START blinks (fast once pressed; then the main menu opens
-- over the same picture, flow.lua). Only the pixels that change are drawn over the picture, so nothing else moves.
-- (The clouds and the sailboats stay still: they are painted into the sky and the water and cannot be lifted out
-- cleanly.)
local D = require("title_data")
local T = {}
-- which picture: "clean" (default, the material cleanup, a1e0e15) or "light" (the painting on its native grid with
-- only its specks removed: art/source/title/tools/light_clean.py; its own pant, blink and bird frames)
T.PICTURE = "clean"
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
  local sfx = T.PICTURE == "light" and "_light" or ""
  I = { base = img("base" .. sfx), bird = img("bird" .. sfx), mouth = img("mouth" .. sfx), eye = img("eye" .. sfx), logos = {},
    tagline = { caps = img("tagline_caps"), lower = img("tagline_lower") } }
  for _, m in ipairs({ "clean", "bands", "gradient", "steps6" }) do I.logos[m] = { fill = img("logo_" .. m), hi = img("logo_hi_" .. m) } end
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
  -- river sparkles: each streak twinkles on its own rhythm
  for i, s in ipairs(D.sparkles) do
    local ph = (s[1] * 0.37 + s[2] * 1.71 + i * 0.53) % 6.283
    if math.sin(t * (1.4 + (i % 5) * 0.25) + ph) > -0.35 then
      lg.setColor(s[4] / 255, s[5] / 255, s[6] / 255, 1); lg.rectangle("fill", s[1], s[2], s[3], 1)
    end
  end
  lg.setColor(1, 1, 1, 1)
  local m, e = T.pepperFrames(t)
  if m > 0 then lg.draw(I.mouth, I.mouthQ[m], D.mouth.x, D.mouth.y) end
  if e > 0 then lg.draw(I.eye, I.eyeQ[e], D.eye.x, D.eye.y) end
  -- the bird: flaps (up, level, down, level), glides now and then, drifts a little
  local f = 1
  if t % 5 < 3.2 then f = ({ 0, 1, 2, 1 })[math.floor(t / 0.14) % 4 + 1] end
  local bx = D.bird.x + math.floor(math.sin(t * 0.35) * 4 + 0.5)
  local by = D.bird.y + math.floor(math.sin(t * 0.9) * 1.2 + 0.5)
  lg.draw(I.bird, I.birdQ[f], bx, by)
  -- the logo and the tagline plate, rebuilt on the grid (art/source/title/tools/logo.py): the plate, then the letters
  lg.draw(I.tagline[T.TAGLINE] or I.tagline.caps, D.plate.x, D.plate.y)
  lg.draw(T.logo().fill, D.logo.x, D.logo.y)
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
  local pts = D.sparkle_points[T.LOGO] or D.sparkle_points.clean
  local p = pts[(s.p - 1) % #pts + 1]
  lg.setColor(1, 1, 1, 1); lg.draw(I.stars, I.starQ[s.size][f], p[1] - 5, p[2] - 5)
end
-- a shine sweeps across the letters every 5 to 7 s: a slanted band of the brightened letters (only the letters'
-- fill has pixels in it, so the band is clipped to them), drawn as 2-row strips through a scissor
function T.shine(t)
  local s0, tt = latest(T.shineList, t)
  local st = s0 and (tt - s0) or 99
  if st < 0.8 then
    local L = D.logo
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
T.LOGO = "clean"                  -- the logo: "clean" (the painting's own, its speckle replaced by an ordered dither), or
                                  -- rebuilt: "gradient" (six steps, ordered 2 x 2 dither between them), "steps6" (the six
                                  -- steps, hard), "bands" (three hard bands and a lip)
function T.logo() return I.logos[T.LOGO] or I.logos.clean end
T.TAGLINE = "caps"                -- the tagline plate: "caps" (THE CITY DOG ADVENTURER) or "lower" (The City Dog Adventurer)
T.CX = 220.5                      -- the centre line under the logo (the tagline plate's centre, x 144..297)
T.PRESS_Y = 152                   -- PRESS START's top: the main menu's middle row
T.LEAVE = 0.45                    -- seconds from the press to the menu
return T
