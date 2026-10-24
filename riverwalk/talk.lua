-- The talk panel, the hint bubbles and the stuck nudge (drawing and watching only: nothing here changes Pepper).
--   What St:hint() says now. The girl's (Mia's) goal and story lines: the speech panel (the kit's gold panel sized to
--   the words, 13 px, her portrait in a thin gold frame on its side, playing its talking loop, art/portraits, 8
--   frames, 9 fps, while the line is said), low at the right, or under the HUD when Pepper is low, never over her;
--   it goes after a few seconds. Pepper's control hints: a small bubble near her (step 3, docs/ui_design.md screen
--   9): the button as the device used last shows it, a picture of the action (T.picFor), at most 3 words; it stays
--   while the hint applies.
--   The nudge: when Pepper has pushed against something for 2 s without getting anywhere, or has stood still for
--   3 s where a control hint applies, the hint's bubble bounces (or a bubble of its own with the button she needs)
--   until a button is pressed. It reads Pepper from outside (position, speed, the buttons held) and is never drawn
--   over her. No hints and no nudges in hard mode (St:hint() returns only messages then, and T.watch does nothing).
local U = require("hud")
local I = require("input")
local T = {}
local lg = love.graphics

-- portraits: the talking loops, cropped to head and shoulders (sx, sy, w, h in each frame)
local PORT = {
  pepper = { file = "art/portraits/pepper_talk.png", fw = 74, sx = 5, sy = 8, w = 64, h = 48 },
  girl   = { file = "art/portraits/girl_talk.png",   fw = 70, sx = 6, sy = 6, w = 58, h = 48 },
}
-- (step 3) the speech panel's portrait windows: head and face, cut from the same loops (sx, sy, w, h in each frame)
local WIN = { pepper = { sx = 14, sy = 10, w = 54, h = 38 }, girl = { sx = 13, sy = 8, w = 42, h = 38 } }
T.WIN_FILL = { 236 / 255, 214 / 255, 170 / 255 }                 -- behind the portrait (the dark hood and coat read on it)
T.FPS, T.FRAMES = 9, 8
T.LINGER = 0.3            -- a line stays this long after it stops applying (no flicker at a zone edge)
T.GIRL_SHOW = 4.5         -- seconds a girl's line from a level zone stays up
T.PUSH_WAIT, T.IDLE_WAIT = 2.0, 3.0

local function loadPorts()
  for _, p in pairs(PORT) do
    if not p.img then
      p.img = lg.newImage(p.file); p.img:setFilter("nearest", "nearest"); p.q = {}
      for f = 1, T.FRAMES do p.q[f] = lg.newQuad((f - 1) * p.fw + p.sx, p.sy, p.w, p.h, p.img:getDimensions()) end
      local wn = WIN[p == PORT.pepper and "pepper" or "girl"]; p.win = wn; p.wq = {}
      for f = 1, T.FRAMES do p.wq[f] = lg.newQuad((f - 1) * p.fw + wn.sx, wn.sy, wn.w, wn.h, p.img:getDimensions()) end
    end
  end
end

function T.port(who) loadPorts(); return PORT[who] or PORT.girl end   -- (the story card draws Mia's too)

-- the picture of a control hint (art/ui/pic_<kind>.png, step 3): what the hint asks, drawn, so a child who
-- cannot read knows it from the button and the picture. A hint can name one (pic = "climb"); otherwise its words
-- choose it, first match wins.
T.PICS = {
  { "CLIMB", "climb" }, { "HOLD: UP", "climb" }, { "BIG JUMP", "jump" }, { "BOUNCE", "bounce" }, { "HOP", "hop" },
  { "SNEAK", "sneak" }, { "CRAWL", "crawl" }, { "DUCK", "duck" }, { "STAY ON", "stay" }, { "DROP", "drop" },
  { "PICK UP", "pickup" }, { "GIVE", "give" }, { "BARK", "bark" }, { "RUN", "run" }, { "SNIFF", "sniff" },
}
function T.picFor(line)
  if not line.btn then return nil end
  if line.pic then return line.pic end
  for _, m in ipairs(T.PICS) do if line.text:find(m[1], 1, true) then return m[2] end end
end

-- (step 3) a story line (no button): the kit's gold panel sized to the words (13 px, at most SAY_W wide, split
-- where its halves are most even), the speaker's portrait in the thin gold frame on its side (the girl right,
-- Pepper left), standing up out of it. Bottom: the group's bottom at the margin; top: under the HUD.
T.SAY_W, T.SAY_PAD_X, T.SAY_PAD_Y, T.SAY_PITCH, T.SAY_IN = 188, 14, 8, 16, 8
T.SAY_TOP = 46
function T.sayLayout(line, where)
  loadPorts()
  local Fl = require("flow")
  local p = PORT[line.who] or PORT.girl
  local rows = Fl.wrap(13, line.text, T.SAY_W)
  local tw = 0
  for _, r in ipairs(rows) do tw = math.max(tw, U.sayW(13, r)) end
  local th = (#rows - 1) * T.SAY_PITCH + U.sayH(13)
  local pw, ph = tw + 2 * T.SAY_PAD_X, math.max(32, th + 2 * T.SAY_PAD_Y)
  local fw, fh = p.win.w + 8, p.win.h + 8
  local w = pw + fw - T.SAY_IN
  local gy0 = where == "top" and T.SAY_TOP or (239 - U.M - math.max(ph, fh) + 1)
  local h = math.max(ph, fh)
  local x0 = line.who == "pepper" and U.M or (320 - U.M - w)
  local by = gy0 + h - ph                                        -- the panel's top (its bottom on the group's)
  local fx = line.who == "pepper" and x0 or (x0 + w - fw)
  local px = line.who == "pepper" and (x0 + fw - T.SAY_IN) or x0
  return { x0 = x0, y0 = gy0, x1 = x0 + w, y1 = gy0 + h, by = by, w = w, rows = rows, tw = tw, port = p, say = true,
    px = px, pw = pw, ph = ph, fx = fx, fy = gy0 + h - fh, fw = fw, fh = fh }
end
-- (step 3) a control hint (a line with a button): a small bubble near Pepper (T.bubble) with the button as the device
-- used last shows it, the picture of the action and at most 3 words; stage: to place it by her (nil: at 0, 0)
function T.layout(line, where, stage)
  if not line.btn then return T.sayLayout(line, where) end
  return T.bubble(line, stage)
end

-- the hint bubble's words: at most 3 words in one or two rows of the 13 px font (docs/ui_design.md: pictures first).
-- The level files keep their texts (the tests and the zones read them); only what is shown is shortened:
-- "TAP: " goes (a tap is the plain press), "HOLD: X" and "A, B" become two rows without the colon or comma, a row wider
-- than T.ROW_W is split at a space, and SHORT lists the one hint that was longer than 3 words.
T.SHORT = { ["RUN, HOLD: BIG JUMP"] = { "HOLD", "BIG JUMP" } }
T.ROW_W = 92
function T.hintRows(text)
  if T.SHORT[text] then return T.SHORT[text] end
  local t = text:gsub("^TAP: ", "")
  local a, b = t:match("^(.-)[:,] (.+)$")
  if a then return { a, b } end
  return require("flow").wrap(13, t, T.ROW_W)
end
-- the buttons as the device used last shows them (hud.lua pieces, 13 px)
T.GLYPHS = { pad = { a = "g_a", b = "g_b", x = "g_x", y = "g_y", down = "g_down", right = "g_right", up = "g_dpad", sniff = "g_l" },
  key = { a = "k_space", b = "k_shift", x = "k_x", y = "k_z", down = "k_down", right = "k_right", up = "k_up", sniff = "k_q" } }
-- (review fix 3: sniff is taught by a bubble with the L1 shoulder or the Q key, like every other action)
function T.glyphFor(btn) local G = T.GLYPHS[I.last] or T.GLYPHS.key; return G[btn] or G.a end
T.B_PAD, T.B_GAP, T.B_PITCH, T.B_AWAY = 6, 4, 15, 4
-- the bubble for a line { btn, text, pic } near Pepper: above her head (tail down), else beside her (tail toward
-- her), else above at the screen's top, else under her; the first that is on screen and clear of her sprite
-- (T.pepperRect) and, above, clear of the HUD's top row. Returns { x0, y0, x1, y1, side, tx, ty, rows, ... }.
function T.bubble(line, stage)
  local rows = T.hintRows(line.text)
  local pic = T.picFor(line)
  local gl = T.glyphFor(line.btn)
  local gw, gh = U.body(gl)
  local pw, ph = 0, 0
  if pic then pw, ph = U.body("pic_" .. pic) end
  local tw = 0
  for _, r in ipairs(rows) do tw = math.max(tw, U.sayW(13, r)) end
  local th = (#rows - 1) * T.B_PITCH + U.sayH(13)
  local w = T.B_PAD + gw + T.B_GAP + (pic and pw + T.B_GAP + 1 or 0) + tw + T.B_PAD
  local h = math.max(th, ph, gh) + 2 * T.B_PAD
  local L = { rows = rows, pic = pic, glyph = gl, gw = gw, gh = gh, pw = pw, ph = ph, tw = tw, th = th, w = w, h = h }
  if not stage then L.x0, L.y0, L.x1, L.y1, L.by = 0, 0, w, h, 0; return L end
  local px0, py0, px1, py1 = T.pepperRect(stage)
  local pcx = (px0 + px1) / 2
  local A = T.B_AWAY
  local function clampX(x) return math.max(U.M, math.min(320 - U.M - w, x)) end
  local function clampY(y) return math.max(U.M, math.min(240 - U.M - h, y)) end
  local hy = py0 + 14                                             -- her head's height on the sprite
  local cands = {
    { "down", clampX(math.floor(pcx - w / 2 + 0.5)), py0 - A - h, 30 },
    { "left", px1 + A, clampY(math.floor(hy - h / 2 + 0.5)) },          -- (right of her, the tail on its left)
    { "right", px0 - A - w, clampY(math.floor(hy - h / 2 + 0.5)) },
    { "down", clampX(math.floor(pcx - w / 2 + 0.5)), py0 - A - h, U.M },
    { "up", clampX(math.floor(pcx - w / 2 + 0.5)), py1 + A },
  }
  for _, c in ipairs(cands) do
    local x, y = c[2], c[3]
    if x >= U.M and x + w <= 320 - U.M and y >= (c[4] or U.M) and y + h <= 240 - U.M
      and not (x < px1 and x + w > px0 and y < py1 and y + h > py0) then
      L.x0, L.y0, L.x1, L.y1, L.by, L.side = x, y, x + w, y + h, y, c[1]
      if c[1] == "down" or c[1] == "up" then L.tx = math.max(x + 8, math.min(x + w - 9, math.floor(pcx + 0.5)))
      else L.ty = math.max(y + 6, math.min(y + h - 7, math.floor(hy + 0.5))) end
      return L
    end
  end
  return nil
end
-- draws a bubble laid out by T.bubble, moved by dy (the nudge's bounce, the rise as it appears)
function T.drawBubble(L, dy)
  lg.push(); lg.translate(0, dy or 0)
  local x, y, w, h = L.x0, L.y0, L.w, L.h
  U.nine("bubble", x, y, w, h, 4, false, "bubble")
  if L.side == "down" then U.put("tail_d", L.tx - 4, y + h - 2, "tail")
  elseif L.side == "up" then U.put("tail_u", L.tx - 4, y - 3, "tail")
  elseif L.side == "left" then U.put("tail_l", x - 3, L.ty - 4, "tail")
  elseif L.side == "right" then U.put("tail_r", x + w - 2, L.ty - 4, "tail") end
  local cy = y + (h - 1) / 2
  local cx = x + T.B_PAD
  U.put(L.glyph, cx, math.floor(cy - (L.gh - 1) / 2 + 0.5), "glyph")
  cx = cx + L.gw + T.B_GAP
  if L.pic then U.put("pic_" .. L.pic, cx, math.floor(cy - (L.ph - 1) / 2 + 0.5), "pic"); cx = cx + L.pw + T.B_GAP + 1 end
  local ty = math.floor(cy - (L.th - 1) / 2 + 0.5)
  for i, r in ipairs(L.rows) do U.say(13, "cream", r, math.floor(cx + (L.tw - U.sayW(13, r)) / 2 + 0.5), ty + (i - 1) * T.B_PITCH, "hint") end
  lg.pop()
end
-- the bounce while a nudge asks for this button (up and down 0 to 3 px, never toward her)
local function nudgeBob(L)
  local n = T.nudge
  local b = math.floor(math.abs(math.sin((n.t or 0) * 5)) * 3 + 0.5)
  if L.side == "up" then return b end
  return -b
end

-- Pepper's sprite on screen (her art reaches 30 px either side of her x and 41 px above her feet; a carried ball
-- and a little margin added)
function T.pepperRect(stage)
  local p = stage.pepper
  local x = math.floor(p.x + 0.5) - math.floor(stage.cam + 0.5)
  local y = p.y - math.floor((stage.camY or 0) + 0.5)               -- (a tall level: her feet on screen)
  return x - 33, y - 46, x + 33, y + 4
end
local function overlaps(a, x0, y0, x1, y1) return a.x0 < x1 and a.x1 > x0 and a.y0 < y1 and a.y1 > y0 end

-- the line being said: { key, line, t = seconds since it started, gone = seconds since it stopped applying }
T.cur = nil
local function keyOf(l) return (l.who or "") .. "|" .. (l.btn or "") .. "|" .. l.text end
-- the girl's lines from the level's zones: key -> { shown = seconds on screen, off = seconds since it applied }
T.girl = {}
function T.reset() T.cur = nil; T.girl = {}; T.nudge = { pushT = 0, idleT = 0, dir = 0 } end
T.reset()

-- every frame while playing
function T.update(dt, stage)
  local line = stage:hint()
  local k = line and keyOf(line)
  for kk, g in pairs(T.girl) do if kk ~= k then g.off = g.off + dt; if g.off > 1 then T.girl[kk] = nil end end end
  if line and not line.msg and line.who ~= "pepper" then
    local g = T.girl[k] or { shown = 0 }
    T.girl[k] = g; g.off = 0
    if g.shown >= T.GIRL_SHOW then line, k = nil, nil              -- said: quiet until it stops applying for 1 s
    else g.shown = g.shown + dt end
  end
  local c = T.cur
  if c and c.key == k then c.t = c.t + dt; c.gone = nil
  elseif line then T.cur = { key = k, line = line, t = dt }
  elseif c then c.gone = (c.gone or 0) + dt; if c.gone > T.LINGER then T.cur = nil end end
end

-- the line on screen now, laid out (or nil): at the bottom, or the top if Pepper is low, or nothing
function T.placed(stage)
  local c = T.cur
  if not c then return nil end
  local px0, py0, px1, py1 = T.pepperRect(stage)
  if c.line.btn then local L = T.layout(c.line, nil, stage); if L and not overlaps(L, px0, py0, px1, py1) then return L end; return nil end
  for _, where in ipairs({ "bottom", "top" }) do
    local L = T.layout(c.line, where)
    if not overlaps(L, px0, py0, px1, py1) then return L end
  end
end

-- the speech panel: rises 6 px into place over 6 frames; the portrait talks while the line is being said
function T.drawSay(L, c)
  local p = L.port
  local u = math.min(1, c.t / 0.1)
  local dy = math.floor(6 * (1 - u) * (1 - u) + 0.5) * (L.by < 120 and -1 or 1)
  lg.push(); lg.translate(0, dy)
  U.panel(L.px, L.by, L.pw, L.ph, "talkpanel")
  local th = U.sayH(13)
  local total = (#L.rows - 1) * T.SAY_PITCH + th
  local y0 = math.floor(L.by + (L.ph - 1) / 2 - (total - 1) / 2 + 0.5)
  local tx = L.px + T.SAY_PAD_X + (c.line.who == "pepper" and T.SAY_IN / 2 or -T.SAY_IN / 2)
  for i, r in ipairs(L.rows) do U.say(13, "cream", r, math.floor(tx + (L.tw - U.sayW(13, r)) / 2 + 0.5), y0 + (i - 1) * T.SAY_PITCH, "talk") end
  -- the portrait: its window filled light, the talking loop, the thin gold frame round it
  local talkFor = math.min(2.4, 0.6 + 0.06 * #c.line.text)
  local f = c.t < talkFor and 1 + math.floor(c.t * T.FPS) % T.FRAMES or 1
  local wx, wy = L.fx + 4, L.fy + 4
  lg.setColor(T.WIN_FILL); lg.rectangle("fill", wx, wy, p.win.w, p.win.h)
  lg.setColor(1, 1, 1, 1); lg.draw(p.img, p.wq[f], wx, wy)
  U.nine("frame_s", L.fx, L.fy, L.fw, L.fh, 4, true, "portrait")
  lg.pop()
end
function T.drawPanel(stage)
  local L = T.placed(stage)
  if not L then return end
  local c = T.cur
  if L.say then T.drawSay(L, c); return end
  if L.side then
    local u = math.min(1, c.t / 0.1)
    local rise = math.floor(4 * (1 - u) * (1 - u) + 0.5) * (L.side == "up" and -1 or 1)
    local n = T.nudge
    T.drawBubble(L, rise + ((n.btn and n.btn == c.line.btn) and nudgeBob(L) or 0)); return
  end
end

-- the nudge: watches Pepper and the buttons every game step (presses: the buttons pressed this step)
local function anyHeld()
  for _, b in ipairs({ "jump", "walk", "down", "act", "bark" }) do if I.down(b) then return true end end
  return I.axis() ~= 0
end
function T.watch(stage, presses, dt)
  local n, p = T.nudge, stage.pepper
  if stage.hard or p.mode ~= "normal" or stage.deadT or stage.clearT then n.pushT, n.idleT, n.dir, n.btn = 0, 0, 0, nil; return end
  if next(presses or {}) then n.pushT, n.idleT, n.btn = 0, 0, nil end            -- she did something
  local ax = I.axis()
  local h = stage:hint()
  local teach = h and h.btn
  -- pushing: the same way, on the ground, no further than 6 px in PUSH_WAIT seconds
  if ax ~= 0 and p.onGround then
    if ax ~= n.dir or math.abs(p.x - n.x0) > 6 then n.dir, n.x0, n.pushT = ax, p.x, 0; if n.why == "push" then n.btn = nil end
    else n.pushT = n.pushT + dt end
  else
    n.dir, n.pushT = 0, 0
    if n.why == "push" and ax ~= 0 then n.btn = nil end
  end
  -- standing still, nothing held, where a control hint applies
  if not anyHeld() and teach then n.idleT = n.idleT + dt else n.idleT = 0; if n.why == "idle" and anyHeld() then n.btn = nil end end
  if not n.btn then
    if n.pushT >= T.PUSH_WAIT then
      n.why = "push"
      n.btn = teach or T.guess(stage, ax)
    elseif n.idleT >= T.IDLE_WAIT and teach then n.why, n.btn = "idle", teach end
    if n.btn then n.t = 0 end
  end
  if n.btn then n.t = (n.t or 0) + dt end
end
-- pushing with no hint: a gap she fits through crouching wants Down, anything else a jump
function T.guess(stage, dir)
  local p, w = stage.pepper, stage.world
  local Pp = require("pepper")
  local a, b = p.x + dir * (Pp.HW + 1), p.x + dir * (Pp.HW + 8)
  local x0, x1 = math.min(a, b), math.max(a, b)
  if w:solidIn(x0, x1, p.y - Pp.H_STAND, p.y - 1) and not w:solidIn(x0, x1, p.y - Pp.H_CROUCH, p.y - 1) then return "down" end
  return "a"
end
-- the nudge (step 3): when the hint on screen asks for the same button, its bubble bounces (T.drawPanel); otherwise a
-- bubble of its own near her, bouncing: the button, its picture and its word (a guess while pushing: Down to
-- crawl, else A to hop)
T.NUDGE = { a = { "HOP", "hop" }, down = { "CRAWL", "crawl" }, b = { "SNEAK", "sneak" }, x = { "PICK UP", "pickup" },
  y = { "BARK!", "bark" }, right = { "RUN", "run" }, sniff = { "SNIFF", "sniff" } }
function T.drawNudge(stage)
  local n = T.nudge
  if not n.btn then return end
  local c = T.cur
  if c and c.line.btn == n.btn and T.placed(stage) then return end
  local w = T.NUDGE[n.btn] or T.NUDGE.a
  local L = T.bubble({ btn = n.btn, text = w[1], pic = w[2] }, stage)
  if L then T.drawBubble(L, nudgeBob(L)) end
end

function T.draw(stage)
  if U.log then local x0, y0, x1, y1 = T.pepperRect(stage); U.logBox("pepper", x0, y0, x1 - 1, y1 - 1) end   -- (for the layout checks)
  T.drawPanel(stage); T.drawNudge(stage)
end
return T
