-- The game's UI pieces and the HUD (ui/hud-v8): the Lion King kit after the owner's target renders, drawn on the pixel
-- grid (art/source/ui/v8), the v8 font (uifont.lua). (Step 3 removed the old blue signs, boxes, 5x7 letters, the
-- dotted checker dim and the code-drawn picture signs: nothing draws them any more.)
local U = {}
local lg = love.graphics
U.RED = { 170 / 255, 30 / 255, 52 / 255 }                         -- the HARD tag's plate

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
  if U.toastInStrip and require("settings").showing() then return end   -- (review fix 6) the sound toast has its place
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
-- (step 3) the v8 HUD row: the ball and the catches against the goal left (gold and +1 once reached), the watch and
-- the seconds left in the middle (the last 5 blink), the points right; one centre line, bodies at the margin.
function U.bonusStatus(g)
  local M, G = U.M, U.ICON_GAP
  local th = U.sayH(13)
  local bw, bh = U.body("ball")
  U.put("ball", M, top(U.TOP_C, bh), "ball")
  local reached = g.catches >= g.need
  local cstr = reached and ("%02d"):format(g.catches) or ("%02d/%02d"):format(g.catches, g.need)
  local x = M + bw + G
  x = x + U.say(13, reached and "gold" or "cream", cstr, x, top(U.TOP_C, th), "catches")
  if reached then U.say(13, "gold", "+1", x + 4, top(U.TOP_C, th), "hudlife") end
  local tstr = ("%02d"):format(math.max(0, math.ceil(g.time)))
  local cw, ch = U.body("clock")
  local tw = U.sayW(13, tstr)
  local gx = math.floor(159.5 - (cw + G + tw - 1) / 2 + 0.5)
  U.put("clock", gx, top(U.TOP_C, ch), "clock")
  local low = g.time <= 5 and g.time > 0 and math.floor(love.timer.getTime() * 4) % 2 == 0
  U.say(13, low and "dim" or "gold", tstr, gx + cw + G, top(U.TOP_C, th), "time")
  local pstr = ("%05d"):format(g.points)
  U.say(13, "gold", pstr, 319 - M - U.sayW(13, pstr) + 1, top(U.TOP_C, th), "points")
end

-- shown for a moment when the volume buttons are pressed: (step 3) a small gold panel with SOUND (7 px) and the 9
-- segments, centred; y: its top (under the HUD while playing). (review fix 6) Over menus and cards it takes the
-- controls strip's place at the bottom for that moment (the strip waits, U.toastInStrip): the hint bubble's frame,
-- 18 px tall, so it never covers a card's words (no card reaches below the strip's top less 6 px)
function U.volumeToast(level, max, y)
  y = y or 30
  local segw, segh = U.body("seg_on")
  local mw = (max - 1) * 4 + segw
  local lw = U.sayW(7, "SOUND")
  local small = y == U.TOAST_MENU
  local pad = small and 8 or 14
  local w = pad + lw + 6 + mw + pad
  local x = math.floor(159.5 - (w - 1) / 2 + 0.5)
  local h = small and 18 or 32
  if small then U.nine("bubble", x, y, w, h, 4, false, "toast") else U.panel(x, y, w, 32, "toast") end
  local cy = y + (h - 1) / 2
  U.say(7, "cream", "SOUND", x + pad, math.floor(cy - (U.sayH(7) - 1) / 2 + 0.5), "toastlabel")
  local mx = x + pad + lw + 6
  for k = 1, max do U.put(k <= level and "seg_on" or "seg_off", mx + (k - 1) * 4, math.floor(cy - (segh - 1) / 2 + 0.5), "seg") end
end
U.TOAST_PLAY, U.TOAST_MENU = 30, 239 - U.M - 18 + 1
U.toastInStrip = true

return U
