-- The v8 UI font: one family in three sizes, every glyph drawn on its own pixel grid (art/source/ui/v8/font):
--   7  small: body text, subtitles, the tally          (styles cream, gold, dim)
--   13 mid:   HUD numbers, menu labels, PAUSED          (gold, cream, dim, ink)
--   17 big:   titles on the tally ribbon                (ink, gold)
-- Atlases and metrics are made by art/source/ui/v8/tools/build8.py (art/ui/font<size>_<style>.png, uifont_data.lua).
-- Never scaled: drawn at whole pixels only. x, y is the top-left of the glyph bodies; the 1 px outline sits round
-- them and the shadow 1 px further down-right (ink: no outline, a light line under each stroke).
local D = require("uifont_data")
local lg = love.graphics
local UF = {}
local img, quads = {}, {}

local function atlas(size, style)
  local key = size .. style
  if not img[key] then
    local i = lg.newImage("art/ui/font" .. size .. "_" .. style .. ".png"); i:setFilter("nearest", "nearest")
    img[key] = i; quads[key] = {}
    local h = D[size].h + 5
    for ch, c in pairs(D[size].cells) do quads[key][ch] = lg.newQuad(c[1], 0, c[2] + 5, h, i:getDimensions()) end
  end
  return img[key], quads[key]
end
local function cell(size, ch)
  local c = D[size].cells
  if c[ch] then return ch, c[ch] end
  local u = ch:upper(); if c[u] then return u, c[u] end
end

-- (review fix 3) one character at a time, UTF-8 aware, so a glyph like the Ö of SÖDER is one cell, not two bytes
local CHAR = "[%z\1-\127\194-\244][\128-\191]*"
UF.height = function(size) return D[size].h end
-- the width of the glyph bodies of s (no outline)
function UF.width(size, s)
  local f, w, n = D[size], 0, 0
  for ch in s:gmatch(CHAR) do
    if ch == " " then w = w + f.space
    else local _, c = cell(size, ch); if c then w = w + c[2] + f.gap; n = n + 1 end end
  end
  if n > 0 and s:sub(-1) ~= " " then w = w - f.gap end
  return w
end
-- draws s with its glyph bodies' top-left at x, y (whole pixels); returns the body width
function UF.print(size, style, s, x, y)
  local f = D[size]; local im, q = atlas(size, style)
  x, y = math.floor(x + 0.5), math.floor(y + 0.5)
  local x0 = x
  lg.setColor(1, 1, 1, 1)
  for ch in s:gmatch(CHAR) do
    if ch == " " then x = x + f.space
    else
      local k, c = cell(size, ch)
      if k then lg.draw(im, q[k], x - 2, y - 2); x = x + c[2] + f.gap end
    end
  end
  return x - x0 - f.gap
end
-- the same, centred on cx (the body box centred; an odd leftover pixel goes right)
function UF.center(size, style, s, cx, y) return UF.print(size, style, s, math.floor(cx - (UF.width(size, s) - 1) / 2 + 0.5), y) end
-- right-aligned: the last body column at xr
function UF.right(size, style, s, xr, y) return UF.print(size, style, s, xr - UF.width(size, s) + 1, y) end
return UF
