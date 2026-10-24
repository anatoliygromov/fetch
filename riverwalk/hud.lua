-- The HUD from the concept art: four blue street signs along the top (lives and hearts, bones, time, score),
-- flat sign blue with a light top rim, a darker left edge and a pointed right end, white 5x7 letters.
-- The prompt banner on the pavement uses the same blue in a box with clipped corners.
local F = require("bigfont")
local U = {}
local lg = love.graphics
U.BLUE  = { 3/255, 108/255, 231/255 }
U.RIM   = { 80/255, 160/255, 238/255 }
U.EDGE  = { 2/255, 60/255, 150/255 }
U.WHITE = { 1, 1, 1 }
U.SHADE = { 20/255, 24/255, 36/255 }
U.GOLD  = { 252/255, 214/255, 60/255 }

local function bitmap(rows)
  local d = love.image.newImageData(#rows[1], #rows)
  for y, r in ipairs(rows) do for x = 1, #r do if r:sub(x, x) == "#" then d:setPixel(x - 1, y - 1, 1, 1, 1, 1) end end end
  local i = lg.newImage(d); i:setFilter("nearest", "nearest"); return i
end
local dogIcon = bitmap({ "........##", "#......###", ".########.", ".#######..", ".##...##..", ".#.....#.." })
local boneIcon = bitmap({ "##.....##", "#########", "#########", "##.....##" })
local heart = bitmap({ "##.##", "#####", "#####", ".###.", "..#.." })
local lockIcon = bitmap({ ".###.", "#...#", "#...#", "#####", "##.##", "##.##", "#####" })
local clockIcon = bitmap({ ".###.", "#.#.#", "#.#.#", "#.###", "#...#", ".###." })
local bigHeart = bitmap({ ".#.#.", "#####", "#####", ".###.", "..#.." })
local smallBone = bitmap({ "#...#", "#####", "#...#" })
local checker                                                   -- every other pixel dark: dims what is under it

-- a sign: body w wide (plus a 5 px point on the right), 12 rows tall
function U.sign(x, y, w)
  for i = 0, 11 do
    local ext = math.floor(5.5 - math.abs(i - 5.5))
    lg.setColor(U.BLUE); lg.rectangle("fill", x, y + i, w + ext, 1)
  end
  lg.setColor(U.RIM); lg.rectangle("fill", x + 1, y, w - 1, 1)
  lg.setColor(U.EDGE); lg.rectangle("fill", x, y, 1, 12); lg.rectangle("fill", x + 2, y + 1, 1, 10)
  lg.setColor(1, 1, 1, 1)
end
local function txt(s, x, y, col) lg.setColor(col or U.WHITE); F.print(s, x, y, 1); lg.setColor(1, 1, 1, 1) end

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
-- ({ x0, y0, x1, y1 }, while playing): a group she is under steps aside (is not drawn), the others stay.
-- Top row on one centre line: the health bar left, the watch and the time in the middle, the bone and its count
-- right with the score under them; bottom left: Pepper's head and the lives.
U.TOP_C = U.M + 10                                               -- the watch (21 rows, the tallest) fills rows 4-24
function U.status(g, avoid)
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
  if not hits(avoid, M, 239 - M - hh, M + hw + G + U.sayW(13, "x" .. g.lives), 240) then
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
-- (step 3) a small 9-slice piece (frame_s, bubble: corners c x c as drawn, each edge one repeated line, the centre
-- one pixel stretched, or left out when hollow) with its outer box at x, y, w x h
local nineQ = {}
function U.nine(name, x, y, w, h, c, hollow, logName)
  local im = U.art(name); local iw, ih = im:getDimensions()
  if not nineQ[name] then
    local q = {}
    local function mk(n, qx, qy, qw, qh) q[n] = lg.newQuad(qx, qy, qw, qh, iw, ih) end
    mk("tl", 0, 0, c, c); mk("tr", iw - c, 0, c, c); mk("bl", 0, ih - c, c, c); mk("br", iw - c, ih - c, c, c)
    mk("t", c, 0, 1, c); mk("b", c, ih - c, 1, c); mk("l", 0, c, c, 1); mk("r", iw - c, c, c, 1); mk("c", c, c, 1, 1)
    nineQ[name] = q
  end
  local Q = nineQ[name]; lg.setColor(1, 1, 1, 1)
  if not hollow then lg.draw(im, Q.c, x + c, y + c, 0, w - 2 * c, h - 2 * c) end
  lg.draw(im, Q.t, x + c, y, 0, w - 2 * c, 1); lg.draw(im, Q.b, x + c, y + h - c, 0, w - 2 * c, 1)
  lg.draw(im, Q.l, x, y + c, 0, 1, h - 2 * c); lg.draw(im, Q.r, x + w - c, y + c, 0, 1, h - 2 * c)
  lg.draw(im, Q.tl, x, y); lg.draw(im, Q.tr, x + w - c, y); lg.draw(im, Q.bl, x, y + h - c); lg.draw(im, Q.br, x + w - c, y + h - c)
  log(logName or name, x, y, x + w - 1, y + h - 1)
end
-- (step 3) a picture in the thin gold frame: the picture's top-left at x, y; the frame 4 px round it
function U.framed(img, x, y, tint, logName)
  local w, h = img:getDimensions()
  lg.setColor(tint or { 1, 1, 1, 1 }); lg.draw(img, x, y); lg.setColor(1, 1, 1, 1)
  U.nine("frame_s", x - 4, y - 4, w + 8, h + 8, 4, true, logName or "frame")
end
-- text centred on cx (an odd leftover pixel right, as UF.center); returns its box's x
function U.sayC(size, style, s, cx, y, logName)
  local x = math.floor(cx - (U.sayW(size, s) - 1) / 2 + 0.5)
  U.say(size, style, s, x, y, logName); return x
end
-- a piece with its body centred on cx, cy
function U.putC(name, cx, cy, logName)
  local w, h = U.body(name)
  U.put(name, math.floor(cx - (w - 1) / 2 + 0.5), math.floor(cy - (h - 1) / 2 + 0.5), logName)
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
-- the smooth warm dim behind the pause and the tally (owner, 23 Oct: like the pause render, no dotted dither):
-- one full-screen dark brown rectangle at 75 %
U.DIM = { 40 / 255, 20 / 255, 12 / 255, 0.75 }
function U.dimWarm() lg.setColor(U.DIM); lg.rectangle("fill", 0, 0, 320, 240); lg.setColor(1, 1, 1, 1) end

-- ---- the controls strip (docs/ui_design.md, 24 Oct): one component, always in the same place at the bottom of every
-- menu screen: `(A) OK   (B) BACK`, the labels per screen. The glyphs follow the device used last (input.lua I.last):
-- a gamepad (the RG35XX) shows its round coins, a keyboard its keycaps. 13 px glyphs, 7 px cream labels on the
-- glyph's centre line, 3 px from glyph to label, 10 px between items; the group centred on the screen, its bodies'
-- bottom at the margin (y 235).
U.GLYPHS = { pad = { ok = { "g_a" }, back = { "g_b" }, lr = { "g_lr" }, a = { "g_a" }, b = { "g_b" }, x = { "g_x" }, y = { "g_y" },
    dpad = { "g_lr" }, down = { "g_down" }, lrsh = { "g_l", "g_r" }, start = { "g_start" } },
  key = { ok = { "k_space" }, back = { "k_esc" }, lr = { "k_left", "k_right" }, a = { "k_space" }, b = { "k_shift" }, x = { "k_x" },
    y = { "k_z" }, dpad = { "k_left", "k_right" }, down = { "k_down" }, lrsh = { "k_q" }, start = { "k_enter" } } }
U.STRIP_GAP, U.STRIP_ITEM = 3, 10
U.STRIP_Y = 239 - U.M - 12                                         -- the glyphs' top (13 px bodies)
-- the width of a glyph (one or more pieces, 1 px apart) and draws it with its top-left body at x, y
function U.glyphW(list) local w = 0; for i, n in ipairs(list) do w = w + U.body(n) + (i > 1 and 1 or 0) end; return w end
function U.glyph(list, x, y, logName)
  for _, n in ipairs(list) do U.put(n, x, y, logName or "glyph"); x = x + U.body(n) + 1 end
end
-- items: { { "ok", "OK" }, { "back", "BACK" } }; device: "pad" or "key" (default: the one used last)
function U.strip(items, device)
  local G = U.GLYPHS[device or require("input").last] or U.GLYPHS.key
  local th = U.sayH(7)
  local w = 0
  for i, it in ipairs(items) do w = w + U.glyphW(G[it[1]]) + U.STRIP_GAP + U.sayW(7, it[2]) + (i > 1 and U.STRIP_ITEM or 0) end
  local x = math.floor(159.5 - (w - 1) / 2 + 0.5)
  local y = U.STRIP_Y
  for _, it in ipairs(items) do
    local g = G[it[1]]
    U.glyph(g, x, y, "glyph"); x = x + U.glyphW(g) + U.STRIP_GAP
    x = x + U.say(7, "cream", it[2], x, top(y + 6, th), "strip") + U.STRIP_ITEM
  end
end

-- FETCH FRENZY (bonus.lua): g = { time (seconds left), catches, need (catches for the extra life), points }.
-- Three signs: the catches against the goal (gold once reached), the countdown (blinks in the last 5 s), points.
local ballIcon = bitmap({ ".###.", "#####", "#####", "#####", ".###." })
function U.bonusStatus(g)
  local y = 3
  U.sign(4, y, 84)
  lg.setColor(1, 1, 1, 1); lg.draw(ballIcon, 9, y + 4)
  if g.catches >= g.need then                                    -- the goal reached: the count in gold and a dog (+1 life)
    txt(("CATCH %02d"):format(g.catches), 18, y + 3, U.GOLD); lg.setColor(U.GOLD); lg.draw(dogIcon, 72, y + 3); lg.setColor(1, 1, 1, 1)
  else txt(("CATCH %02d/%02d"):format(g.catches, g.need), 18, y + 3) end
  U.sign(124, y, 62)
  local low = g.time <= 5 and g.time > 0 and math.floor(love.timer.getTime() * 4) % 2 == 0
  txt(("TIME %02d"):format(math.max(0, math.ceil(g.time))), 132, y + 3, low and U.GOLD or U.WHITE)
  U.sign(232, y, 80)
  txt(("POINTS %05d"):format(g.points), 237, y + 3)
end

-- a box with clipped corners: dark edge, light rim, blue body
function U.box(x, y, w, h)
  lg.setColor(U.EDGE); lg.rectangle("fill", x + 1, y, w - 2, h); lg.rectangle("fill", x, y + 1, w, h - 2)
  lg.setColor(U.RIM);  lg.rectangle("fill", x + 2, y + 1, w - 4, h - 2); lg.rectangle("fill", x + 1, y + 2, w - 2, h - 4)
  lg.setColor(U.BLUE); lg.rectangle("fill", x + 2, y + 2, w - 4, h - 4)
  lg.setColor(1, 1, 1, 1)
end
-- the prompt on the pavement (rows 201..211)
function U.prompt(text)
  local w = F.width(text, 1) + 16
  local x = math.floor((320 - w) / 2)
  U.box(x, 201, w, 11)
  txt(text, x + 8, 203)
end
function U.center(s, cx, y, scale, col)
  lg.setColor(U.SHADE); F.center(s, cx + 1, y + 1, scale)
  lg.setColor(col or U.WHITE); F.center(s, cx, y, scale)
  lg.setColor(1, 1, 1, 1)
end
function U.text(s, x, y, col) txt(s, x, y, col) end
-- dims the whole screen with a 1 px checker of the shade colour (behind boxes and cards)
function U.dim()
  if not checker then
    local d = love.image.newImageData(320, 240)
    for y = 0, 239 do for x = (y % 2), 319, 2 do d:setPixel(x, y, U.SHADE[1], U.SHADE[2], U.SHADE[3], 1) end end
    checker = lg.newImage(d)
  end
  lg.setColor(1, 1, 1, 1); lg.draw(checker, 0, 0)
end
-- a padlock as tall as a letter (5 x 7 at scale 1), with the same 1 px shadow
function U.lock(x, y, col, scale)
  lg.setColor(U.SHADE); lg.draw(lockIcon, x + 1, y + 1, 0, scale or 1)
  lg.setColor(col or U.WHITE); lg.draw(lockIcon, x, y, 0, scale or 1)
  lg.setColor(1, 1, 1, 1)
end
-- the dog from the lives sign (10 x 6), at scale (1 or 2)
function U.dog(x, y, col, scale)
  lg.setColor(U.SHADE); lg.draw(dogIcon, x + 1, y + 1, 0, scale or 1)
  lg.setColor(col or U.WHITE); lg.draw(dogIcon, x, y, 0, scale or 1); lg.setColor(1, 1, 1, 1)
end
-- the HARD tag (hard mode): gold letters on a dark red plate, 29 x 10
U.RED = { 170/255, 30/255, 52/255 }
function U.hardTag(x, y)
  lg.setColor(U.SHADE); lg.rectangle("fill", x + 1, y + 1, 29, 10)
  lg.setColor(U.RED); lg.rectangle("fill", x, y, 29, 10)
  txt("HARD", x + 3, y + 2, U.GOLD)
end
-- a medal, 11 x 11 at x, y: a gold disc with its picture (nohit: a heart, bones: a bone, par: a clock); not won
-- yet: a dark disc (visible on the selected row too) with the picture in the rim colour
local medalPic = { nohit = bigHeart, bones = smallBone, par = clockIcon }
local medalDisc
function U.medal(kind, x, y, won)
  if not medalDisc then medalDisc = bitmap({ "...#####...", ".#########.", ".#########.", "###########", "###########",
    "###########", "###########", "###########", ".#########.", ".#########.", "...#####..." }) end
  lg.setColor(U.SHADE); lg.draw(medalDisc, x + 1, y + 1)
  lg.setColor(won and U.GOLD or U.SHADE); lg.draw(medalDisc, x, y)
  local pic = medalPic[kind]
  lg.setColor(won and { 120/255, 70/255, 10/255 } or U.RIM)
  lg.draw(pic, x + math.floor((11 - pic:getWidth()) / 2), y + math.floor((11 - pic:getHeight()) / 2))
  lg.setColor(1, 1, 1, 1)
end
-- the sound level: 10 cells, 4 x h each with a 1 px gap (52 px wide), lit up to the level; "OFF" at 0
function U.volumeBar(x, y, level, max, h)
  h = h or 7
  if level == 0 then txt("OFF", x, y + math.floor((h - 7) / 2), U.GOLD); return end
  for i = 1, max do
    lg.setColor(U.SHADE); lg.rectangle("fill", x + (i - 1) * 5 + 1, y + 1, 4, h)
    lg.setColor(i <= level and U.GOLD or U.EDGE); lg.rectangle("fill", x + (i - 1) * 5, y, 4, h)
  end
  lg.setColor(1, 1, 1, 1)
end
-- shown for a moment when the volume buttons are pressed: a small box under the status signs while playing;
-- y = 218 (the bottom edge) over menus and cards, so it never covers their headings
function U.volumeToast(level, max, y)
  y = y or 20
  U.box(110, y, 100, 17)
  txt("SOUND", 116, y + 5)
  U.volumeBar(150, y + 5, level, max)
end
-- Picture signs (r6/levels): a little scene of what a control hint asks, for children who cannot read yet (the
-- talk panel draws one between the button and the words). 14 x 12 cells, drawn 3 px a cell (42 x 36 px): Pepper
-- (white, the HUD's dog in a pose) and what she uses (gold: the ground, a box, a bar, arrows, the ball, Mia).
U.PICT_CELL = 3
U.PICT_W, U.PICT_H = 14 * U.PICT_CELL, 12 * U.PICT_CELL
local lowDog = bitmap({ "..........##", "#########.##", ".##########.", "##.......##." })   -- crouched, crawling
local girlIcon = bitmap({ ".##.", ".##.", "####", ".##.", "####", "####", "####", ".#.#", ".#.#" })   -- Mia, 4 x 9
local ballDot = bitmap({ ".##.", "####", "####", ".##." })
local BALLC = { 236/255, 84/255, 104/255 }
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
      local col = pass == 1 and U.SHADE or (k == "dog" or k == "low") and U.WHITE or k == "ball" and BALLC or U.GOLD
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
