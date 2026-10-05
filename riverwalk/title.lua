-- The title screen, animated. The painting is cut into layers by tools/make_title.py; everything moves by time t:
-- the river sparkles twinkle, the lamps glow, Pepper blinks, the bird flaps, a shine sweeps across the logo,
-- and PRESS ANY KEY blinks (fast once a key is pressed, then the screen fades out).
local D = require("title_data")
local T = {}
local lg = love.graphics
local I
local function img(n) local i = lg.newImage("art/title/" .. n .. ".png"); i:setFilter("nearest", "nearest"); return i end

function T.load()
  if I then return end
  I = { base = img("base"), press_off = img("press_off"), eye = img("eye_closed"), bird = img("bird"), logo = img("logo_hi") }
  I.birdQ = {}
  for f = 0, 2 do I.birdQ[f] = lg.newQuad(f * D.bird.w, 0, D.bird.w, D.bird.h, I.bird:getDimensions()) end
end

-- pixel-exact filled ellipse, row by row
local function ellipse(cx, cy, rx, ry)
  for dy = -ry, ry do
    local k = math.sqrt(math.max(0, 1 - (dy / (ry + 0.5)) ^ 2))
    local hw = math.floor(rx * k + 0.5)
    if hw > 0 then lg.rectangle("fill", cx - hw, cy + dy, hw * 2, 1) end
  end
end

-- t: seconds on the title; leaving: seconds since a key was pressed (nil before)
function T.draw(t, leaving)
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
  -- lamp glow, with a slight flicker
  for i, l in ipairs(D.lamps) do
    local f = 0.85 + 0.15 * math.sin(t * 9 + i * 2) * math.sin(t * 2.3 + i)
    lg.setColor(1, 0.85, 0.45, 0.10 * f); ellipse(l[1], l[2], l[3] + 5, l[3] + 5)
    lg.setColor(1, 0.85, 0.45, 0.13 * f); ellipse(l[1], l[2], l[3] + 1, l[3] + 1)
  end
  lg.setColor(1, 1, 1, 1)
  -- Pepper blinks: a quick blink every few seconds, sometimes a double one
  local bt = t % 4.3
  if (bt > 3.0 and bt < 3.13) or (math.floor(t / 4.3) % 3 == 1 and bt > 3.25 and bt < 3.37) then lg.draw(I.eye, D.eye.x, D.eye.y) end
  -- the bird: flaps (up, level, down, level), glides now and then, drifts a little
  local cycle = t % 5
  local f = 1
  if cycle < 3.2 then f = ({ 0, 1, 2, 1 })[math.floor(t / 0.14) % 4 + 1] end
  local bx = D.bird.x + math.floor(math.sin(t * 0.35) * 4 + 0.5)
  local by = D.bird.y + math.floor(math.sin(t * 0.9) * 1.2 + 0.5)
  lg.draw(I.bird, I.birdQ[f], bx, by)
  -- a shine sweeps across the logo: a slanted band, drawn as 2-row strips through a scissor
  local st = t % 3.6
  if st < 0.8 then
    local L = D.logo
    local pos = -30 + (L.w + 60) * (st / 0.8)
    for y = 0, L.h - 1, 2 do
      local x = math.floor(pos - y * 0.45)
      if x + 8 > 0 and x < L.w then
        lg.setScissor(L.x + math.max(0, x), L.y + y, 8 + math.min(0, x), 2)
        lg.draw(I.logo, L.x, L.y)
      end
    end
    lg.setScissor()
  end
  -- PRESS ANY KEY TO START blinks (fast once pressed)
  local on = leaving and (math.floor(leaving / 0.07) % 2 == 0) or (not leaving and (t % 1.1) < 0.75)
  if not on then lg.draw(I.press_off, D.press.x, D.press.y) end
  -- fade in at the start, fade out after the key press
  local black = 0
  if t < 0.5 then black = 1 - t / 0.5 end
  if leaving and leaving > T.LEAVE - 0.25 then black = math.max(black, (leaving - (T.LEAVE - 0.25)) / 0.25) end
  if black > 0 then lg.setColor(0, 0, 0, math.min(1, black)); lg.rectangle("fill", 0, 0, 320, 240) end
  lg.setColor(1, 1, 1, 1)
end
T.LEAVE = 0.6       -- seconds from the key press to the level card
return T
