-- The talk panel and the stuck nudge (drawing and watching only: nothing here changes Pepper).
--   The panel: what St:hint() says now, as a short dialogue line. Pepper says the control hints: a button
--   picture and 1 to 3 words ([B] HOLD: SNEAK). The girl says the goal and story lines (BRING ME THE BALL!).
--   Pepper's portrait sits bottom left, the girl's bottom right; the portrait plays its talking loop
--   (art/portraits, 8 frames, 9 fps) while the line is being said, then rests on frame 1. The panel sits low on
--   the pavement; if Pepper's sprite would touch it, it moves to the top of the screen, and if she would touch
--   that too it is not drawn. A girl's line goes away after a few seconds; a control hint stays while it applies.
--   The nudge: when Pepper has pushed against something for 2 s without getting anywhere, or has stood still for
--   3 s where a control hint applies, the button she needs bounces above her head until a button is pressed.
--   It reads Pepper from outside (position, speed, the buttons held) and is never drawn over her.
--   No hints and no nudges in hard mode (St:hint() returns only messages then, and T.watch does nothing).
local F = require("bigfont")
local U = require("hud")
local I = require("input")
local T = {}
local lg = love.graphics

-- portraits: the talking loops, cropped to head and shoulders (sx, sy, w, h in each frame)
local PORT = {
  pepper = { file = "art/portraits/pepper_talk.png", fw = 74, sx = 5, sy = 8, w = 64, h = 48 },
  girl   = { file = "art/portraits/girl_talk.png",   fw = 70, sx = 6, sy = 6, w = 58, h = 48 },
}
T.FPS, T.FRAMES = 9, 8
T.LINGER = 0.3            -- a line stays this long after it stops applying (no flicker at a zone edge)
T.GIRL_SHOW = 4.5         -- seconds a girl's line from a level zone stays up
T.PUSH_WAIT, T.IDLE_WAIT = 2.0, 3.0

local function loadPorts()
  for _, p in pairs(PORT) do
    if not p.img then
      p.img = lg.newImage(p.file); p.img:setFilter("nearest", "nearest"); p.q = {}
      for f = 1, T.FRAMES do p.q[f] = lg.newQuad((f - 1) * p.fw + p.sx, p.sy, p.w, p.h, p.img:getDimensions()) end
    end
  end
end

-- pixel circles (no smoothing): a filled disc of radius r
local discs = {}
local function disc(r)
  if not discs[r] then
    local n = r * 2
    local d = love.image.newImageData(n, n)
    for y = 0, n - 1 do for x = 0, n - 1 do
      if (x + 0.5 - r) ^ 2 + (y + 0.5 - r) ^ 2 <= r * r then d:setPixel(x, y, 1, 1, 1, 1) end
    end end
    discs[r] = lg.newImage(d); discs[r]:setFilter("nearest", "nearest")
  end
  return discs[r]
end

-- the RG35XX face buttons (A right, B bottom, X top, Y left) and the d-pad
local LETTER = { a = "A", b = "B", x = "X", y = "Y" }
local KNOB = { 0.93, 0.93, 0.96 }
local INK = { 22/255, 26/255, 40/255 }
T.SIZE = { big = 10, small = 7 }                                 -- the glyph's radius
-- a button picture centred on cx, cy: a round button with its letter, or the d-pad with one arm lit
function T.glyph(btn, cx, cy, size)
  local r = T.SIZE[size or "big"]
  cx, cy = math.floor(cx + 0.5), math.floor(cy + 0.5)
  if LETTER[btn] then
    lg.setColor(U.SHADE); lg.draw(disc(r), cx - r + 1, cy - r + 1)
    lg.setColor(INK); lg.draw(disc(r), cx - r, cy - r)
    lg.setColor(KNOB); lg.draw(disc(r - 1), cx - r + 1, cy - r + 1)
    lg.setColor(INK)
    if r >= 10 then F.print(LETTER[btn], cx - 4, cy - 7, 2) else F.print(LETTER[btn], cx - 2, cy - 3, 1) end
  else                                                           -- the d-pad: a cross, the arm to press lit
    local a = r >= 10 and 6 or 4                                 -- arm width
    local function cross(col, dx, dy)
      lg.setColor(col)
      lg.rectangle("fill", cx - a / 2 + dx, cy - r + dy, a, 2 * r); lg.rectangle("fill", cx - r + dx, cy - a / 2 + dy, 2 * r, a)
    end
    cross(U.SHADE, 1, 1); cross(INK, 0, 0)
    local arm = { down = { 0, 1 }, up = { 0, -1 }, left = { -1, 0 }, right = { 1, 0 } }
    local d = arm[btn] or arm.down
    lg.setColor(KNOB)
    local lx, ly = cx - a / 2 + 1, cy - a / 2 + 1                -- the lit arm, inside the cross's outline
    if d[1] == 0 then lg.rectangle("fill", lx, d[2] > 0 and cy or cy - r + 1, a - 2, r - 1)
    else lg.rectangle("fill", d[1] > 0 and cx or cx - r + 1, ly, r - 1, a - 2) end
    lg.setColor(INK)                                              -- an arrow on the lit arm
    local tx, ty = cx + d[1] * (r - 4), cy + d[2] * (r - 4)
    for i = 0, 1 do
      if d[1] == 0 then lg.rectangle("fill", tx - (1 - i), ty + d[2] * (i - 1), 3 - 2 * i, 1)
      else lg.rectangle("fill", tx + d[1] * (i - 1), ty - (1 - i), 1, 3 - 2 * i) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- word wrap to at most two lines of width w at scale s (nil if it does not fit)
local function wrap(text, w, s)
  if F.width(text, s) <= w then return { text } end
  local words = {}
  for wd in text:gmatch("%S+") do words[#words + 1] = wd end
  for k = #words - 1, 1, -1 do
    local a, b = table.concat(words, " ", 1, k), table.concat(words, " ", k + 1)
    if F.width(a, s) <= w and F.width(b, s) <= w then return { a, b } end
  end
end

-- the panel's layout for a line: its rect (x0, y0, x1, y1, the portrait included) at the bottom or the top
local BOX_H = 40
local GAP = 4                                                    -- between the button picture and the words
local TEXT_W = 238                                               -- room for the words (and a button) beside a portrait
function T.layout(line, where)
  loadPorts()
  local p = PORT[line.who] or PORT.girl
  local gw = line.btn and 2 * T.SIZE.big + GAP or 0              -- the button picture and a gap
  local scale, rows = 2, wrap(line.text, TEXT_W - gw, 2)
  if not rows then scale, rows = 1, wrap(line.text, TEXT_W - gw, 1) or { line.text } end
  local tw = 0
  for _, r in ipairs(rows) do tw = math.max(tw, F.width(r, scale)) end
  local w = 3 + p.w + 5 + gw + tw + 6                            -- portrait, words, margins
  local by = where == "top" and 30 or 198                        -- the box; the portrait stands up out of it
  local x0 = line.who == "pepper" and 2 or 318 - w
  return { x0 = x0, y0 = by + BOX_H - 1 - p.h, x1 = x0 + w, y1 = by + BOX_H, by = by, w = w, rows = rows, scale = scale,
    gw = gw, tw = tw, port = p }
end

-- Pepper's sprite on screen (her art reaches 30 px either side of her x and 41 px above her feet; a carried ball
-- and a little margin added)
function T.pepperRect(stage)
  local p = stage.pepper
  local x = math.floor(p.x + 0.5) - math.floor(stage.cam + 0.5)
  return x - 33, p.y - 46, x + 33, p.y + 4
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
  for _, where in ipairs({ "bottom", "top" }) do
    local L = T.layout(c.line, where)
    if not overlaps(L, px0, py0, px1, py1) then return L end
  end
end

function T.drawPanel(stage)
  local L = T.placed(stage)
  if not L then return end
  local c = T.cur
  U.box(L.x0, L.by, L.w, BOX_H)
  local p = L.port
  local talkFor = math.min(2.4, 0.6 + 0.06 * #c.line.text)        -- the loop plays while the line is being said
  local f = c.t < talkFor and 1 + math.floor(c.t * T.FPS) % T.FRAMES or 1
  local px = c.line.who == "pepper" and L.x0 + 3 or L.x1 - 3 - p.w
  lg.setColor(1, 1, 1, 1); lg.draw(p.img, p.q[f], px, L.y1 - 1 - p.h)
  local x = c.line.who == "pepper" and px + p.w + 5 or L.x0 + 6
  local cy = L.by + BOX_H / 2
  if c.line.btn then T.glyph(c.line.btn, x + T.SIZE.big, cy, "big"); x = x + L.gw end
  local lh = L.scale * 7
  local total = #L.rows * lh + (#L.rows - 1) * 3
  for i, r in ipairs(L.rows) do
    local y = math.floor(cy - total / 2 + (i - 1) * (lh + 3) + 0.5)
    lg.setColor(U.SHADE); F.print(r, x + 1, y + 1, L.scale)
    lg.setColor(c.line.who == "pepper" and U.WHITE or U.GOLD); F.print(r, x, y, L.scale)
  end
  lg.setColor(1, 1, 1, 1)
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
-- the button above her head, bouncing; beside her if there is no room above (never over her sprite)
function T.drawNudge(stage)
  local n = T.nudge
  if not n.btn then return end
  local r = T.SIZE.big
  local px0, py0, px1 = T.pepperRect(stage)
  local bounce = math.floor(math.abs(math.sin((n.t or 0) * 5)) * 4 + 0.5)
  local cx, cy = (px0 + px1) / 2, py0 - 2 - r - bounce
  if cy - r < 20 then                                            -- no room above: beside her, the way she faces
    local face = stage.pepper.face or 1
    cx = face > 0 and px1 + 2 + r or px0 - 2 - r
    cy = py0 + 14 - bounce
  end
  T.glyph(n.btn, cx, cy, "big")
end

function T.draw(stage) T.drawPanel(stage); T.drawNudge(stage) end
return T
