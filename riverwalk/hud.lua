-- The game's UI kit (ui/hud-v8): the Lion King look after the owner's target renders (art/source/ui/ref). Every
-- piece is drawn on the pixel grid (art/source/ui/v8, built into art/ui by build8.py), every letter is one of the
-- three grid fonts (uifont.lua: 7, 13, 17 px), one outline (64,11,6) and one shadow (36,8,5), and a dim is the
-- smooth warm one (no dotted dither anywhere). The old helpers (box, center, text, prompt, dim, lock, dog, medal,
-- volume bar) keep their names and arguments and now draw in this kit, so every screen that uses them matches.
local U = {}
local lg = love.graphics
-- colour names kept as the old API's style keys: GOLD -> gold letters, WHITE -> cream, RIM -> dim
U.BLUE  = { 3/255, 108/255, 231/255 }
U.RIM   = { 80/255, 160/255, 238/255 }
U.EDGE  = { 2/255, 60/255, 150/255 }
U.WHITE = { 1, 1, 1 }
U.SHADE = { 36/255, 8/255, 5/255 }
U.GOLD  = { 252/255, 214/255, 60/255 }
U.INK   = { 64/255, 11/255, 6/255 }
local function bitmap(rows)
  local d = love.image.newImageData(#rows[1], #rows)
  for y, r in ipairs(rows) do for x = 1, #r do if r:sub(x, x) == "#" then d:setPixel(x - 1, y - 1, 1, 1, 1, 1) end end end
  local i = lg.newImage(d); i:setFilter("nearest", "nearest"); return i
end
local dogIcon = bitmap({ "........##", "#......###", ".########.", ".#######..", ".##...##..", ".#.....#.." })

-- ---- v8 (ui/hud-v8): the HUD, the pause and the tally in the Lion King kit, after the owner's three target renders
-- (art/source/ui/ref). Pieces are drawn on the pixel grid (art/source/ui/v8, built into art/ui by build8.py) and
-- placed by their drawn bodies, never their drop shadows (the v6 layout spec): margin M to every body, one centre
-- line per row, 3 px from an icon to its number, one outline (64,11,6) and one shadow (36,8,5).
local UF = require("uifont")
local ART = require("uiart_data")
U.M, U.ICON_GAP = 4, 3
local arts = {}
function U.art(name)
  if not arts[name] then arts[name] = lg.newImage("art/ui/" .. name .. ".png"); arts[name]:setFilter("nearest", "nearest") end
  return arts[name]
end
function U.body(name) local b = ART[name]; return b[3] - b[1] + 1, b[4] - b[2] + 1 end     -- body width, height
-- U.log: when a table, every placed body is listed in it ({ name, x0, y0, x1, y1 }) for tools/layout_qa8.py
local function log(name, x0, y0, x1, y1)
  if not U.log then return end
  local ax, ay = lg.transformPoint(x0, y0); local bx, by = lg.transformPoint(x1, y1)          -- (on screen: a card may be moved)
  U.log[#U.log + 1] = { name, math.floor(ax + 0.5), math.floor(ay + 0.5), math.floor(bx + 0.5), math.floor(by + 0.5) }
end
U.logBox = log
-- a piece with its body's top-left at x, y
function U.put(name, x, y, logName)
  local b = ART[name]
  lg.setColor(1, 1, 1, 1); lg.draw(U.art(name), x - b[1], y - b[2])
  log(logName or name, x, y, x + b[3] - b[1], y + b[4] - b[2])
end
-- text with its outlined box (the bodies and the 1 px outline round them) at x, y; returns the box's width
function U.say(size, style, s, x, y, logName)
  local w = UF.width(size, s)
  UF.print(size, style, s, x + 1, y + 1)
  log(logName or "text", x, y, x + w + 1, y + UF.height(size) + 1)
  return w + 2
end
function U.sayW(size, s) return UF.width(size, s) + 2 end                 -- an outlined box's width and height
function U.sayH(size) return UF.height(size) + 2 end
-- the top of a box h tall centred on the line cy (cy may be .5)
local function top(cy, h) return math.floor(cy - (h - 1) / 2 + 0.5) end
local function hits(a, x0, y0, x1, y1) return a and a[1] < x1 and a[3] > x0 and a[2] < y1 and a[4] > y0 end

-- g: { lives, hearts, bones, total, time (seconds left), score, hard }. avoid: Pepper's sprite on screen
-- ({ x0, y0, x1, y1 }, while playing): a group she is under steps aside (is not drawn), the others stay. talk:
-- the talk panel's rect (talk.lua T.placed): the lives step aside under it.
-- Top row on one centre line: the health bar left, the watch and the time in the middle, the bone and its count
-- right with the score under them; bottom left: Pepper's head and the lives.
U.TOP_C = U.M + 10                                               -- the watch (21 rows, the tallest) fills rows 4-24
function U.status(g, avoid, talk)
  local M, G = U.M, U.ICON_GAP
  -- health: the paw medallion capsule, one segment a heart
  local bw, bh = U.body("bar_3")
  if not hits(avoid, M, top(U.TOP_C, bh), M + bw, top(U.TOP_C, bh) + bh) then
    U.put("bar_" .. math.max(0, math.min(3, g.hearts)), M, top(U.TOP_C, bh), "health")
  end
  -- the watch and the time left, one group centred on the screen; the last 30 s blink
  local tstr = ("%03d"):format(math.max(0, math.ceil(g.time)))
  local cw, ch = U.body("clock")
  local tw, th = U.sayW(13, tstr), U.sayH(13)
  local gx = math.floor(159.5 - (cw + G + tw - 1) / 2 + 0.5)
  if not hits(avoid, gx, M, gx + cw + G + tw, M + 21 + (g.hard and 14 or 0)) then
    U.put("clock", gx, top(U.TOP_C, ch), "clock")
    local low = g.time < 30 and math.floor(love.timer.getTime() * 4) % 2 == 0
    U.say(13, low and "dim" or "gold", tstr, gx + cw + G, top(U.TOP_C, th), "time")
    if g.hard then U.hardTag8(159.5, top(U.TOP_C, ch) + ch + 2) end
  end
  -- bones (the bone and the count) right-aligned at the margin, the score under the count, right-aligned too
  local bstr = ("%02d/%02d"):format(g.bones, g.total)
  local ow, oh = U.body("bone")
  local nw = U.sayW(13, bstr)
  local sstr = ("%06d"):format(g.score)
  local sw = U.sayW(13, sstr)
  local bx = 319 - M - nw + 1 - G - ow
  local sy = top(U.TOP_C, th) + th + 3                           -- 2 clear rows under the count (its shadow takes one)
  if not hits(avoid, math.min(bx, 319 - M - sw), M, 320, sy + th) then
    U.put("bone", bx, top(U.TOP_C, oh), "bone")
    U.say(13, "gold", bstr, 319 - M - nw + 1, top(U.TOP_C, th), "bones")
    U.say(13, "gold", sstr, 319 - M - sw + 1, sy, "score")
  end
  -- lives: Pepper's head and x3, bottom left, on one centre line, the head's bottom at the margin
  local hw, hh = U.body("head")
  local cy = 239 - M - (hh - 1) / 2
  local lx1 = M + hw + G + U.sayW(13, "x" .. g.lives)
  local underTalk = talk and talk.x0 < lx1 and talk.x1 > M and talk.y1 > 239 - M - hh
  if not underTalk and not hits(avoid, M, 239 - M - hh, lx1, 240) then
    U.put("head", M, 239 - M - hh + 1, "head")
    U.say(13, "gold", "x" .. g.lives, M + hw + G, top(cy, th), "lives")
  end
end
-- HARD (hard mode): small gold letters on a dark red plate, centred on cx, its top at y
function U.hardTag8(cx, y)
  local w = U.sayW(7, "HARD") + 4
  local x = math.floor(cx - (w - 1) / 2 + 0.5)
  lg.setColor(36 / 255, 8 / 255, 5 / 255); lg.rectangle("fill", x + 1, y + 1, w, 13)
  lg.setColor(64 / 255, 11 / 255, 6 / 255); lg.rectangle("fill", x, y, w, 13)
  lg.setColor(U.RED); lg.rectangle("fill", x + 1, y + 1, w - 2, 11)
  U.say(7, "gold", "HARD", x + 2, y + 2, "hard")
end
-- the kit's gold panel (art/ui/panel.png, kit/frames/panel_menu: a true 9-slice, corners 15 x 16 as drawn, each
-- edge one repeated column or row, a flat fill), body at x, y, w x h; every stretch is a copy of one pixel line
local panelQ
function U.panel(x, y, w, h, logName)
  local im = U.art("panel"); local iw, ih = im:getDimensions()
  local L, R, T, B = 15, 15, 16, 16
  if not panelQ then
    panelQ = {}
    local function q(n, qx, qy, qw, qh) panelQ[n] = lg.newQuad(qx, qy, qw, qh, iw, ih) end
    q("tl", 0, 0, L, T); q("tr", iw - R, 0, R, T); q("bl", 0, ih - B, L, B); q("br", iw - R, ih - B, R, B)
    q("t", L, 0, 1, T); q("b", L, ih - B, 1, B); q("l", 0, T, L, 1); q("r", iw - R, T, R, 1); q("c", L, T, 1, 1)
  end
  local Q = panelQ; lg.setColor(1, 1, 1, 1)
  lg.draw(im, Q.c, x + L, y + T, 0, w - L - R, h - T - B)
  lg.draw(im, Q.t, x + L, y, 0, w - L - R, 1); lg.draw(im, Q.b, x + L, y + h - B, 0, w - L - R, 1)
  lg.draw(im, Q.l, x, y + T, 0, 1, h - T - B); lg.draw(im, Q.r, x + w - R, y + T, 0, 1, h - T - B)
  lg.draw(im, Q.tl, x, y); lg.draw(im, Q.tr, x + w - R, y); lg.draw(im, Q.bl, x, y + h - B); lg.draw(im, Q.br, x + w - R, y + h - B)
  log(logName or "panel", x, y, x + w - 1, y + h - 1)
end
-- a title ribbon (ribbon_pause / ribbon_tally) with its main band's centre on cx and the band's top (in the middle,
-- for the arched one) at y; logs the band (not the tails) as "ribbon". uiart_data <name>_band: x0, x1, top, height
function U.ribbon(name, cx, y)
  local b = ART[name .. "_band"]; local bw = b[2] - b[1] + 1
  local x = math.floor(cx - (bw - 1) / 2 + 0.5)
  lg.setColor(1, 1, 1, 1); lg.draw(U.art(name), x - b[1], y - b[3])
  log("ribbon", x, y, x + bw - 1, y + b[4] - 1)
  return x, bw
end
-- a straight ribbon with its band bw px wide (ribbon_pause as a 3-slice: tails and band ends as drawn, the band's
-- middle one repeated column), the band's centre on cx and its top at y; logs the band as "ribbon"
local rib3
function U.ribbon3(cx, y, bw)
  local im = U.art("ribbon_pause"); local iw, ih = im:getDimensions()
  local b = ART.ribbon_pause_band                                   -- x0, x1, top, height
  if not rib3 then rib3 = { lg.newQuad(0, 0, b[1] + 3, ih, iw, ih), lg.newQuad(math.floor((b[1] + b[2]) / 2), 0, 1, ih, iw, ih),
    lg.newQuad(b[2] - 2, 0, iw - (b[2] - 2), ih, iw, ih) } end
  local x = math.floor(cx - (bw - 1) / 2 + 0.5)
  lg.setColor(1, 1, 1, 1)
  lg.draw(im, rib3[1], x - b[1], y - b[3]); lg.draw(im, rib3[2], x + 3, y - b[3], 0, bw - 6, 1); lg.draw(im, rib3[3], x + bw - 3, y - b[3])
  log("ribbon", x, y, x + bw - 1, y + b[4] - 1)
  return x
end
-- the smooth warm dim behind the pause and the tally (owner, 23 Oct: like the pause render, no dotted dither):
-- one full-screen dark brown rectangle at 75 %
U.DIM = { 40 / 255, 20 / 255, 12 / 255, 0.75 }
function U.dimWarm() lg.setColor(U.DIM); lg.rectangle("fill", 0, 0, 320, 240); lg.setColor(1, 1, 1, 1) end

-- FETCH FRENZY (bonus.lua): g = { time (seconds left), catches, need (catches for the extra life), points }.
-- The HUD's top row: the ball and the catches against the goal left (gold, then x and Pepper's head once reached),
-- the watch and the time centred (the last 5 s blink), the points right.
function U.bonusStatus(g)
  local M, G = U.M, U.ICON_GAP
  local th = U.sayH(13)
  local bw, bh = U.body("ball")
  U.put("ball", M, top(U.TOP_C, bh), "ball")
  local cstr = g.catches >= g.need and ("%02d"):format(g.catches) or ("%02d/%02d"):format(g.catches, g.need)
  local w = U.say(13, "gold", cstr, M + bw + G, top(U.TOP_C, th), "catches")
  if g.catches >= g.need then local hw, hh = U.body("head"); U.put("head", M + bw + G + w + G, top(U.TOP_C, hh), "life") end
  local tstr = ("%02d"):format(math.max(0, math.ceil(g.time)))
  local cw, ch = U.body("clock")
  local tw = U.sayW(13, tstr)
  local gx = math.floor(159.5 - (cw + G + tw - 1) / 2 + 0.5)
  U.put("clock", gx, top(U.TOP_C, ch), "clock")
  local low = g.time <= 5 and g.time > 0 and math.floor(love.timer.getTime() * 4) % 2 == 0
  U.say(13, low and "dim" or "gold", tstr, gx + cw + G, top(U.TOP_C, th), "time")
  local pstr = ("%05d"):format(g.points)
  U.say(13, "gold", pstr, 319 - M - U.sayW(13, pstr) + 1, top(U.TOP_C, th), "score")
end

-- the old API in the kit -----------------------------------------------------------------------------------------
local function styleOf(col) return (col == U.GOLD and "gold") or (col == U.RIM and "dim") or ((col == nil or col == U.WHITE) and "cream") or "gold" end
local SIZE = { 7, 13, 17 }
-- a dark inset plate (the menu rows' unselected look) of any size: a brown line round a dark fill, a shaded top row
function U.plate(x, y, w, h)
  lg.setColor(108 / 255, 62 / 255, 34 / 255); lg.rectangle("fill", x + 1, y, w - 2, h); lg.rectangle("fill", x, y + 1, w, h - 2)
  lg.setColor(44 / 255, 22 / 255, 14 / 255); lg.rectangle("fill", x + 1, y + 1, w - 2, h - 2)
  lg.setColor(30 / 255, 13 / 255, 8 / 255); lg.rectangle("fill", x + 1, y + 1, w - 2, 1)
  lg.setColor(84 / 255, 46 / 255, 26 / 255); lg.rectangle("fill", x + 1, y + h - 2, w - 2, 1)
  lg.setColor(1, 1, 1, 1)
end
-- a menu row w x h (default 19 tall): row_on / row_off as 9-slices (corners as drawn, one middle row and column
-- repeated; the selected row keeps its 1 px shadow)
local rowQ = {}
function U.row(on, x, y, w, logName, h)
  h = h or 19
  local name = on and "row_on" or "row_off"
  local im = U.art(name); local iw, ih = im:getDimensions()
  local R, B = iw - 4, ih - 9                                       -- (source: right cap from R, bottom part from B)
  if not rowQ[name] then
    local q = {}
    for i, sy in ipairs({ { 0, 9 }, { 9, 1 }, { 9 + 1, ih - 10 } }) do
      q[i] = { lg.newQuad(0, sy[1], 4, sy[2], iw, ih), lg.newQuad(4, sy[1], 1, sy[2], iw, ih), lg.newQuad(R, sy[1], iw - R, sy[2], iw, ih) }
    end
    rowQ[name] = q
  end
  local q = rowQ[name]; lg.setColor(1, 1, 1, 1)
  local rx = x + w - (on and 3 or 4)                               -- (row_on's last 4 columns: 3 body + its shadow)
  for i, part in ipairs({ { y, 1 }, { y + 9, h - 18 }, { y + h - 9, 1 } }) do
    local sy = part[2]
    lg.draw(im, q[i][1], x, part[1], 0, 1, sy); lg.draw(im, q[i][2], x + 4, part[1], 0, rx - x - 4, sy); lg.draw(im, q[i][3], rx, part[1], 0, 1, sy)
  end
  log(logName or "row", x, y, x + w - 1, y + h - 1)
end
-- a box: the kit's gold panel (a plate when too small for its corners)
function U.box(x, y, w, h)
  if w >= 31 and h >= 33 then U.panel(x, y, w, h, "box") else U.plate(x, y, w, h) end
end
-- PRESS ANY BUTTON (or any short prompt) on the pavement: small cream letters on a dark plate, rows 201..211
function U.prompt(text)
  local tw = U.sayW(7, text)
  local w = tw + 8
  local x = math.floor((320 - w) / 2)
  U.plate(x, 201, w, 13)
  U.say(7, "cream", text, x + 4, 203, "prompt")
end
-- text centred on cx, its top at y: scale 1 the small font, 2 the mid, 3 the big (in the old 5x7 places)
function U.center(s, cx, y, scale, col)
  local size = SIZE[scale or 2] or 13
  local w = U.sayW(size, s)
  U.say(size, styleOf(col), s, math.floor(cx - (w - 1) / 2 + 0.5), y - 1 + (size == 17 and 2 or 0), "text")
end
function U.text(s, x, y, col) U.say(7, styleOf(col), s, x - 1, y - 1, "text") end
U.dim = function() U.dimWarm() end                                -- (the dotted checker is gone)
-- the kit padlock (11 x 14), its body's top-left at x, y (col and scale kept for the old calls; ignored)
function U.lock(x, y) U.put("padlock", x, y, "lock") end
-- the paw coin (21 px) where the old dog icon was (its top-left at x, y)
function U.dog(x, y) U.put("coin_paw", x, y, "dog") end
U.RED = { 170/255, 30/255, 52/255 }
function U.hardTag(x, y) local w = U.sayW(7, "HARD") + 4; U.hardTag8(x + (w - 1) / 2, y) end
-- a medal (15 x 19 on its ribbon) at x, y: won gold with a paw, not won a plain bronze disc
function U.medal(kind, x, y, won) U.put(won and "medal_on" or "medal_off", x, y, "medal") end
-- the sound level: one segment a step (4 px pitch) in a dark trough, lit up to the level; x, y the trough's top-left
function U.volumeBar(x, y, level, max)
  local sw, sh = U.body("seg_on")
  local mw = (max - 1) * 4 + sw
  lg.setColor(U.INK); lg.rectangle("fill", x, y, mw + 4, sh + 4)
  lg.setColor(44 / 255, 22 / 255, 14 / 255); lg.rectangle("fill", x + 1, y + 1, mw + 2, sh + 2); lg.setColor(1, 1, 1, 1)
  for k = 1, max do U.put(k <= level and "seg_on" or "seg_off", x + 2 + (k - 1) * 4, y + 2, "seg") end
  return mw + 4, sh + 4
end
-- shown for a moment when the volume buttons are pressed: a small gold panel with SOUND and the meter; under the
-- HUD while playing (y = 20 -> 30); y = 218 (the bottom edge) over menus and cards
function U.volumeToast(level, max, y)
  y = (y or 20) == 20 and 30 or 202
  local mw = (max - 1) * 4 + U.body("seg_on") + 4
  local lw = U.sayW(7, "SOUND")
  local w = 16 + lw + 6 + mw + 16
  local x = math.floor(159.5 - (w - 1) / 2 + 0.5)
  U.panel(x, y, w, 34, "toast")
  U.say(7, "cream", "SOUND", x + 16, y + 13, "text")
  U.volumeBar(x + 16 + lw + 6, y + 9, level, max)
end

-- Picture signs (r6/levels): a little scene of what a control hint asks, for children who cannot read yet (the
-- talk panel draws one between the button and the words). 14 x 12 cells, drawn 3 px a cell (42 x 36 px): Pepper
-- (white, the HUD's dog in a pose) and what she uses (gold: the ground, a box, a bar, arrows, the ball, Mia).
U.PICT_CELL = 3
U.PICT_W, U.PICT_H = 14 * U.PICT_CELL, 12 * U.PICT_CELL
local lowDog = bitmap({ "..........##", "#########.##", ".##########.", "##.......##." })   -- crouched, crawling
local girlIcon = bitmap({ ".##.", ".##.", "####", ".##.", "####", "####", "####", ".#.#", ".#.#" })   -- Mia, 4 x 9
local ballDot = bitmap({ ".##.", "####", "####", ".##." })
local BALLC = { 228/255, 52/255, 44/255 }
local CREAM = { 255/255, 250/255, 230/255 }
local PGOLD = { 250/255, 188/255, 48/255 }
local PICT = {}
-- the steps of one picture: { "dog" | "low" | "girl" | "ball", cx, cy } (its top-left cell), or { "box", cx, cy, w, h } (gold),
-- or { "dots", {cx, cy}, ... } (a dotted path, gold), or { "up" | "down" | "right", cx, cy } (an arrow, gold)
PICT.run    = { { "box", 0, 11, 14, 1 }, { "dog", 1, 5 }, { "box", 0, 6, 1, 1 }, { "box", 0, 8, 1, 1 }, { "right", 11, 5 } }
PICT.hop    = { { "box", 0, 11, 14, 1 }, { "box", 6, 9, 3, 2 }, { "dots", { 0, 10 }, { 1, 8 }, { 3, 6 } }, { "dog", 4, 2 } }
PICT.jump   = { { "box", 0, 11, 14, 1 }, { "box", 8, 6, 4, 5 }, { "dots", { 0, 10 }, { 1, 7 }, { 2, 4 } }, { "dog", 4, 0 } }
PICT.climb  = { { "box", 0, 11, 14, 1 }, { "box", 10, 5, 4, 6 }, { "dog", 0, 5 }, { "up", 8, 0 } }
PICT.crawl  = { { "box", 0, 11, 14, 1 }, { "box", 2, 6, 11, 1 }, { "box", 3, 7, 1, 4 }, { "box", 11, 7, 1, 4 }, { "low", 1, 7 } }
PICT.duck   = { { "box", 0, 11, 14, 1 }, { "low", 1, 7 }, { "box", 9, 1, 1, 1 }, { "box", 10, 2, 1, 1 }, { "box", 11, 1, 1, 1 },
  { "box", 12, 0, 1, 1 }, { "box", 8, 0, 1, 1 }, { "dots", { 8, 4 }, { 6, 5 } } }
PICT.stay   = { { "box", 0, 9, 14, 1 }, { "dots", { 1, 10 }, { 4, 11 }, { 7, 10 }, { 10, 11 }, { 12, 10 } }, { "low", 1, 5 }, { "down", 11, 0 } }
PICT.drop   = { { "box", 0, 6, 14, 1 }, { "box", 0, 11, 14, 1 }, { "dog", 0, 0 }, { "down", 11, 7 } }
PICT.bounce = { { "box", 2, 10, 10, 1 }, { "dots", { 3, 11 }, { 5, 11 }, { 7, 11 }, { 9, 11 }, { 11, 11 } }, { "up", 0, 3 }, { "dog", 4, 2 } }
PICT.pickup = { { "box", 0, 11, 14, 1 }, { "dog", 0, 5 }, { "ball", 10, 7 }, { "down", 10, 2 } }
PICT.give   = { { "box", 0, 11, 14, 1 }, { "dog", 0, 5 }, { "ball", 7, 1 }, { "girl", 10, 2 } }
PICT.bark   = { { "box", 0, 11, 14, 1 }, { "dog", 0, 5 }, { "box", 10, 4, 1, 1 }, { "box", 11, 5, 1, 2 }, { "box", 10, 7, 1, 1 },
  { "box", 12, 3, 1, 1 }, { "box", 13, 4, 1, 4 }, { "box", 12, 8, 1, 1 } }
PICT.sneak  = { { "box", 0, 11, 14, 1 }, { "dog", 4, 5 }, { "dots", { 0, 10 }, { 2, 10 } }, { "box", 0, 2, 3, 1 }, { "box", 2, 3, 1, 1 },
  { "box", 1, 4, 1, 1 }, { "box", 0, 5, 3, 1 } }     -- (soft steps behind her, a "z": quiet)
local arrows = {
  up    = bitmap({ ".#.", "###", ".#.", ".#." }), down = bitmap({ ".#.", ".#.", "###", ".#." }),
  right = bitmap({ "#..", "##.", "###", "##.", "#.." }),
}
-- draws picture `kind` with its top-left at x, y (cells of 2 px); returns false if there is no such picture
function U.pict(kind, x, y)
  local steps = PICT[kind]
  if not steps then return false end
  local c = U.PICT_CELL
  local function at(cx, cy) return x + cx * c, y + cy * c end
  for pass = 1, 2 do                                             -- 1: the shadow, 1 px down and right; 2: the picture
    local o = pass == 1 and 1 or 0
    for _, st in ipairs(steps) do
      local k = st[1]
      local col = pass == 1 and U.INK or (k == "dog" or k == "low") and CREAM or k == "ball" and BALLC or PGOLD
      lg.setColor(col)
      if k == "box" then local px, py = at(st[2], st[3]); lg.rectangle("fill", px + o, py + o, st[4] * c, st[5] * c)
      elseif k == "dots" then for i = 2, #st do local px, py = at(st[i][1], st[i][2]); lg.rectangle("fill", px + o, py + o, c, c) end
      else
        local im = (k == "dog" and dogIcon) or (k == "low" and lowDog) or (k == "girl" and girlIcon) or (k == "ball" and ballDot) or arrows[k]
        local px, py = at(st[2], st[3]); lg.draw(im, px + o, py + o, 0, c)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
  return true
end
U.PICTS = PICT

return U
