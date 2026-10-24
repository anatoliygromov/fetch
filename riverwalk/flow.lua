-- The game around the levels: the run, the menus, the story cards, the ending and what is saved.
--   The run:      the levels of levels.lua in order, from the first one (START GAME) or the one picked in the level
--                 select, to the end. One score for the whole run, lives carry from level to level, hearts refill
--                 and the timer starts again in every level. A level whose file is missing is skipped.
--   Main menu:    PLAY (on from the furthest open level), LEVELS (the level select), OPTIONS (SOUND, HARD MODE,
--                 CONTROLS), outlined text over the title picture (docs/ui_design.md, 24 Oct).
--   Level select: every level of levels.lua. Level 1 is always open; a level opens when the one before it is
--                 cleared. Locked ones are dimmed with a padlock, a missing file says COMING SOON.
--   Saved:        progress.txt (the open levels, one name per line), best_run.txt (the best run score), the
--                 best points per level (best.txt for River Walk, best_<name>.txt for the others), the best clear
--                 time per level (time_<name>.txt, seconds) and the medals won on it (medals_<name>.txt: nohit,
--                 bones, par), hard.txt (1: HARD MODE is on) and bonus_best.txt (the best FETCH FRENZY points).
--   Bonus:        a level cleared with at least one of its golden bones found: tally -> FETCH FRENZY (bonus.lua,
--                 30 s, its points go into the run's score, 11 catches (bonus.lua B.LIFE_AT) give an extra life) -> story card.
--   Medals:       NO HIT (no heart lost), ALL BONES, PAR TIME (cleared within the level's par, levels.lua).
--   Cards:        the story card waits 2 s, then only A goes on. GAME OVER: TRY AGAIN (the same level, 3 lives,
--                 the score it started with) or MENU. The pause: GO ON or QUIT, and QUIT asks first (B is sneak,
--                 so B only ever goes back).
local U = require("hud")
local Title = require("title")
local S = require("sfx")
local LEVELS = require("levels")
local lg = love.graphics
local Talk = require("talk")
local F = { prefix = "", save = true, unlocked = {}, bestRun = 0, hard = false }

-- the levels in play order; exists: level/<name>.lua is there
function F.list(src)
  local out = {}
  for i, l in ipairs(src or LEVELS) do
    out[i] = { name = l.name, number = l.number or i, title = l.title or l.name:upper(), par = l.par or 60, was = l.was,
      exists = love.filesystem.getInfo("level/" .. l.name .. ".lua") ~= nil }
  end
  return out
end
F.levels = F.list()
function F.index(name) for i, l in ipairs(F.levels) do if l.name == name then return i end end end

-- saving (F.save = false in the test modes; the flow test uses its own files through F.prefix)
local function read(n) local ok, s = pcall(love.filesystem.read, F.prefix .. n); return ok and s or nil end
local function write(n, s) if F.save then pcall(love.filesystem.write, F.prefix .. n, s) end end
function F.load()
  F.unlocked = {}
  for n in (read("progress.txt") or ""):gmatch("[%w_]+") do F.unlocked[n] = true end
  for _, l in ipairs(F.levels) do if l.was and F.unlocked[l.was] then F.unlocked[l.name] = true end end   -- (D2: a save from
  -- before the tall levels: the flat level it opened opens its tall twin)
  F.bestRun = tonumber(read("best_run.txt") or "") or 0
  F.hard = (read("hard.txt") or ""):match("1") ~= nil
end
-- every save file (the flow test starts from none)
F.FILES = { "progress.txt", "best_run.txt", "hard.txt", "bonus_best.txt" }
function F.wipe()
  local list = {}
  for _, n in ipairs(F.FILES) do list[#list + 1] = n end
  for _, l in ipairs(F.levels) do for _, n in ipairs({ F.bestFile(l.name), "time_" .. l.name .. ".txt", "medals_" .. l.name .. ".txt" }) do list[#list + 1] = n end end
  for _, n in ipairs(list) do pcall(love.filesystem.remove, F.prefix .. n) end
end
function F.setHard(on) F.hard = on; write("hard.txt", on and "1\n" or "0\n") end
function F.isOpen(i) return i == 1 or F.unlocked[F.levels[i].name] == true end
-- a level is cleared: the levels after it open, up to and including the next one whose file exists
-- (so a missing level never blocks the ones after it)
function F.cleared(name)
  local i = F.index(name)
  if not i then return end
  for j = i + 1, #F.levels do F.unlocked[F.levels[j].name] = true; if F.levels[j].exists then break end end
  local open = {}
  for _, l in ipairs(F.levels) do if F.unlocked[l.name] then open[#open + 1] = l.name end end
  write("progress.txt", table.concat(open, "\n") .. "\n")
end
function F.bestFile(name) return name == "riverwalk" and "best.txt" or ("best_" .. name .. ".txt") end
function F.levelBest(name) return tonumber(read(F.bestFile(name)) or "") or 0 end
-- a level's points (its bones, bonus and time bonus): true if they beat its best
function F.levelPoints(name, points)
  if points <= F.levelBest(name) then return false end
  write(F.bestFile(name), tostring(points)); return true
end
-- a level's clear time (seconds): the best time so far and true if this one beats it
function F.levelTimeBest(name) return tonumber(read("time_" .. name .. ".txt") or "") end
function F.levelTime(name, t)
  t = math.floor(t * 100 + 0.5) / 100
  local b = F.levelTimeBest(name)
  if b and b <= t then return b, false end
  write("time_" .. name .. ".txt", ("%.2f\n"):format(t)); return t, true
end
-- the medals won on a level (kept from every clear): { nohit = true, bones = true, par = true }
F.MEDALS = { "nohit", "bones", "par" }
function F.medals(name)
  local m = {}
  for k in (read("medals_" .. name .. ".txt") or ""):gmatch("%a+") do m[k] = true end
  return m
end
function F.addMedals(name, won)
  local m, list = F.medals(name), {}
  for _, k in ipairs(F.MEDALS) do if won[k] then m[k] = true end; if m[k] then list[#list + 1] = k end end
  write("medals_" .. name .. ".txt", table.concat(list, " ") .. "\n")
  return m
end
-- 35.3 -> "0:35.3"
function F.clock(t) t = math.max(0, t or 0); return ("%d:%04.1f"):format(math.floor(t / 60), t % 60) end

-- FETCH FRENZY (bonus.lua): the bonus round opens after a level's tally when Pepper found at least one of the
-- level's golden bones (super = true in its bones list). A level with none never opens it.
function F.bonusOpen(stage)
  for _, bn in ipairs(stage and stage.bones or {}) do if bn.super and bn.taken then return true end end
  return false
end
-- the best bonus round points (bonus_best.txt): true if these beat it
function F.bonusBestPoints() return tonumber(read("bonus_best.txt") or "") or 0 end
function F.bonusBest(points)
  if points <= F.bonusBestPoints() then return false end
  write("bonus_best.txt", tostring(points)); return true
end

-- the run is over (the ending or GAME OVER): true if its score is the best run
function F.runOver(score)
  if score <= F.bestRun then return false end
  F.bestRun = score; write("best_run.txt", tostring(score)); return true
end

-- a new run from level i of the list to the end, the missing ones skipped
function F.newRun(i, list)
  local r = { names = {}, k = 1, score = 0, lives = 3 }
  for j = i or 1, #(list or F.levels) do local l = (list or F.levels)[j]; if l.exists then r.names[#r.names + 1] = l.name end end
  return r
end

-- menu buttons: a key or a pad button -> "up", "down", "ok", "back" (or nil)
local KEYS = { up = "up", w = "up", down = "down", s = "down", left = "left", a = "left", right = "right", d = "right", space = "ok", ["return"] = "ok", kpenter = "ok", x = "ok",
  escape = "back", backspace = "back" }
local PADS = { dpup = "up", dpdown = "down", dpleft = "left", dpright = "right", a = "ok", start = "ok", b = "back" }
function F.action(key, pad) if key then return KEYS[key] end; return PADS[pad] end

-- the main menu (docs/ui_design.md screen 2): PLAY, LEVELS, OPTIONS. PLAY goes on from the furthest level that is
-- open (its file there); LEVELS is the level select; OPTIONS the options panel. The cursor moves; returns the choice.
F.menu = { sel = 1, items = { "PLAY", "LEVELS", "OPTIONS" }, moved = -1, from = 1 }
F.pick = { sel = 1 }
local function move(m, a, n)
  m.from, m.moved = m.sel, love.timer.getTime()
  m.sel = (m.sel + (a == "up" and -2 or 0)) % n + 1; S.play("tick")
end
function F.menuInput(a)
  local m = F.menu
  if a == "up" or a == "down" then move(m, a, #m.items)
  elseif a == "ok" then
    S.play("select")
    return ({ "play", "select", "options" })[m.sel]
  elseif a == "back" then return "back" end
end
-- the furthest level open with its file there (PLAY starts the run there)
function F.furthest()
  local best = 1
  for i, l in ipairs(F.levels) do if l.exists and F.isOpen(i) then best = i end end
  return best
end
-- OPTIONS (screen 3): SOUND (left / right turn it down or up; A steps it up and wraps round to off), HARD MODE
-- (A, left or right switch it), CONTROLS (A opens the controls page). B goes back.
F.opts = { sel = 1, items = { "SOUND", "HARD MODE", "CONTROLS" }, moved = -1, from = 1 }
F.OPT_SOUND, F.OPT_HARD, F.OPT_CONTROLS = 1, 2, 3
function F.optionsInput(a)
  local o, Se = F.opts, require("settings")
  if a == "up" or a == "down" then move(o, a, #o.items)
  elseif a == "back" then S.play("tick"); return "back"
  elseif o.sel == F.OPT_SOUND and (a == "left" or a == "right" or a == "ok") then
    if a == "ok" then if Se.volume >= Se.MAX then Se.step(-Se.MAX) else Se.step(1) end
    else Se.step(a == "right" and 1 or -1) end
    S.play("tick")
  elseif o.sel == F.OPT_HARD and (a == "left" or a == "right" or a == "ok") then
    local on = (a == "ok" and not F.hard) or a == "right"
    if on ~= F.hard then F.setHard(on); S.play("select") else S.play("push") end
    return "hard"
  elseif o.sel == F.OPT_CONTROLS and a == "ok" then S.play("select"); return "controls" end
end
-- the controls page: B (or A) goes back
function F.controlsInput(a) if a == "back" or a == "ok" then S.play("tick"); return "back" end end
-- the level select: left / right (or up / down) browse the cards, wrapping round; A plays an open level
function F.selectInput(a)
  local p = F.pick
  if a == "up" or a == "down" or a == "left" or a == "right" then
    local d = (a == "up" or a == "left") and -1 or 1
    p.from, p.moved, p.dir = p.sel, love.timer.getTime(), d
    p.sel = (p.sel - 1 + d) % #F.levels + 1; S.play("slide")
  elseif a == "ok" then
    if F.levels[p.sel].exists and F.isOpen(p.sel) then S.play("select"); return "play", p.sel end
    S.play("push")                                               -- locked or coming soon: a dull thud
  elseif a == "back" then S.play("tick"); return "back" end
end

local function blink(t) return (t % 1.1) < 0.75 end

-- the cursor's place: eased from the row it left to the new one (6 frames, ease out), with a 1 px bob
local function cursorY(m, y_of)
  local u = math.min(1, (love.timer.getTime() - (m.moved or -1)) / 0.1)
  u = 1 - (1 - u) * (1 - u)
  return math.floor(y_of(m.from) + (y_of(m.sel) - y_of(m.from)) * u + 0.5)
end
local function bob() return (math.floor(love.timer.getTime() * 3) % 2 == 0) and 0 or 1 end

-- the main menu: the title picture as it is (no dim, no box), the three rows as outlined 13 px text centred under the
-- logo on Title.CX, the selected one gold with the paw coin before it; the controls strip at the bottom
F.M = { ROW0 = 132, PITCH = 20, CUR_GAP = 4 }
function F.drawMenu(t)
  Title.draw(t, nil, true)
  local th = U.sayH(13)
  local function rowY(i) return F.M.ROW0 + (i - 1) * F.M.PITCH end
  for i, it in ipairs(F.menu.items) do
    local on = F.menu.sel == i
    local w = U.sayW(13, it)
    local x = math.floor(Title.CX - (w - 1) / 2 + 0.5)
    U.say(13, on and "gold" or "cream", it, x, rowY(i), "label")
    if on then
      local cw, ch = U.body("coin_paw")
      local cy = cursorY(F.menu, rowY) + (th - 1) / 2
      U.put("coin_paw", x - F.M.CUR_GAP - cw, math.floor(cy - (ch - 1) / 2 + 0.5) - bob(), "cursor")
    end
  end
  U.strip({ { "ok", "OK" }, { "back", "BACK" } })
end

-- OPTIONS: the title picture under the smooth warm dim, the kit's gold panel with the OPTIONS ribbon, three rows
-- (label left, its control right: the 9-segment sound meter, the HARD MODE switch), the strip at the bottom
F.O = { X = 60, W = 200, PANEL = 66, H = 104, RIB = 56, ROW0 = 88, PITCH = 22, LABEL_IN = 36, CUR_IN = 10, RIGHT_IN = 16 }
local function backdropWarm(t) Title.draw(t, nil, true); U.dimWarm() end
function F.drawOptions(t)
  local Se = require("settings")
  local O = F.O
  backdropWarm(t)
  U.panel(O.X, O.PANEL, O.W, O.H)
  U.ribbon("ribbon_menu", 159.5, O.RIB)
  local tw = U.sayW(13, "OPTIONS")
  U.say(13, "ink", "OPTIONS", math.floor(159.5 - (tw - 1) / 2 + 0.5), O.RIB + 2, "title")
  local th = U.sayH(13)
  local function rowY(i) return O.ROW0 + (i - 1) * O.PITCH end
  local xr = O.X + O.W - 1 - O.RIGHT_IN                            -- the controls' right edge
  for i, it in ipairs(F.opts.items) do
    local on = F.opts.sel == i
    local y = rowY(i); local cy = y + (th - 1) / 2
    U.say(13, on and "gold" or "cream", it, O.X + O.LABEL_IN, y, "label")
    if i == F.OPT_SOUND then                                       -- one segment a step, lit up to the level
      local segw, segh = U.body("seg_on")
      local mw = (Se.MAX - 1) * 4 + segw
      local mx, my = xr - mw + 1, math.floor(cy - (segh - 1) / 2 + 0.5)
      for k = 1, Se.MAX do U.put(k <= Se.volume and "seg_on" or "seg_off", mx + (k - 1) * 4, my, "seg") end
      U.logBox("meter", mx, my, mx + mw - 1, my + segh - 1)
    elseif i == F.OPT_HARD then
      local n = F.hard and "tog_on" or "tog_off"
      local w, h = U.body(n)
      U.put(n, xr - w + 1, math.floor(cy - (h - 1) / 2 + 0.5), "toggle")
    end
  end
  local cw, ch = U.body("coin_paw")
  local cy = cursorY(F.opts, rowY) + (th - 1) / 2
  U.put("coin_paw", O.X + O.CUR_IN, math.floor(cy - (ch - 1) / 2 + 0.5) - bob(), "cursor")
  local items = { { "ok", "OK" }, { "back", "BACK" } }
  if F.opts.sel == F.OPT_SOUND then items = { { "lr", "CHANGE" }, { "back", "BACK" } }
  elseif F.opts.sel == F.OPT_HARD then items = { { "ok", F.hard and "OFF" or "ON" }, { "back", "BACK" } } end
  U.strip(items)
end

-- the controls page (screen 4): the handheld drawn on the left, a row per control on the right (8 rows, 17 px apart): the button as it is
-- on the handheld, its action (13 px, one or two words), the keyboard key(s)
F.C = { X = 10, W = 300, PANEL = 36, H = 172, RIB = 26, HX = 30, ROW0 = 56, PITCH = 17, GX0 = 116, GX1 = 160, LX = 166, KR = 293 }
F.CONTROLS = { { "dpad", "MOVE" }, { "a", "JUMP" }, { "down", "CRAWL" }, { "b", "SNEAK" }, { "x", "PICK UP" }, { "y", "BARK" }, { "lrsh", "SNIFF" }, { "start", "PAUSE" } }
function F.drawControls(t, overLevel)
  local C = F.C
  if overLevel then U.dimWarm() else backdropWarm(t) end
  U.panel(C.X, C.PANEL, C.W, C.H)
  U.ribbon("ribbon_menu", 159.5, C.RIB)
  local tw = U.sayW(13, "CONTROLS")
  U.say(13, "ink", "CONTROLS", math.floor(159.5 - (tw - 1) / 2 + 0.5), C.RIB + 2, "title")
  local hw, hh = U.body("handheld")
  local rows = #F.CONTROLS
  local th = U.sayH(13)
  local blockH = (rows - 1) * C.PITCH + 13
  local midY = C.ROW0 + (blockH - 1) / 2
  U.put("handheld", C.HX, math.floor(midY - (hh - 1) / 2 + 0.5), "handheld")
  for i, r in ipairs(F.CONTROLS) do
    local y = C.ROW0 + (i - 1) * C.PITCH                          -- the 13 px row's top
    local cy = y + 6
    local g = U.GLYPHS.pad[r[1]]                                   -- centred in the glyph column
    U.glyph(g, math.floor((C.GX0 + C.GX1) / 2 - (U.glyphW(g) - 1) / 2 + 0.5), y, "glyph")
    U.say(13, "cream", r[2], C.LX, math.floor(cy - (th - 1) / 2 + 0.5), "label")
    local keys = U.GLYPHS.key[r[1]]
    U.glyph(keys, C.KR - U.glyphW(keys) + 1, y, "key")
  end
  U.strip({ { "back", "BACK" } })
end

-- the level select (docs/ui_design.md screen 5, step 3): one big card per level on the title picture under the warm
-- dim. The card: the kit's gold panel, a LEVEL n ribbon over its top edge, the level's picture (a 1x crop of the
-- game, art/ui/cards, tools/card_shots.py) in the thin gold frame, its name (17 px), then the three medals won
-- (left) and the best time and best points (right) from the save. Locked: the picture darkened with the padlock on
-- it. Left / right slide the next card in (0.12 s, ease out) with a sound; arrows either side, a dot per level
-- under the card, the controls strip at the bottom.
F.SEL = { X = 40, W = 240, PANEL = 16, H = 192, RIB = 6, PIC_Y = 33, NAME = 158, STATS = 191, ARROW_OUT = 7, DOTS = 211,
  DOT_PITCH = 11, SLIDE = 0.12, LOCKED = { 0.26, 0.23, 0.27, 1 } }
local cards = {}
function F.cardImage(name)
  if cards[name] == nil then
    local ok, im = pcall(lg.newImage, "art/ui/cards/" .. name .. ".png")
    cards[name] = ok and im or false; if ok then im:setFilter("nearest", "nearest") end
  end
  return cards[name] or nil
end
function F.selectCard(i)
  local S3, l = F.SEL, F.levels[i]
  local open, ok = F.isOpen(i), F.isOpen(i) and l.exists
  U.panel(S3.X, S3.PANEL, S3.W, S3.H)
  local rib = "LEVEL " .. l.number
  U.ribbon("ribbon_pause", 159.5, S3.RIB)
  U.sayC(13, "ink", rib, 159.5, S3.RIB + 2, "title")
  if F.hard then U.hardTag8(S3.X + S3.W - 30, S3.RIB + 4) end
  local im = F.cardImage(l.name)
  local pw, ph = 216, 118
  if im then pw, ph = im:getDimensions() end
  local px = math.floor(159.5 - (pw - 1) / 2 + 0.5)
  if im then U.framed(im, px, S3.PIC_Y, not ok and S3.LOCKED or nil, "picture")
  else lg.setColor(44 / 255, 22 / 255, 14 / 255); lg.rectangle("fill", px, S3.PIC_Y, pw, ph); lg.setColor(1, 1, 1, 1)
    U.nine("frame_s", px - 4, S3.PIC_Y - 4, pw + 8, ph + 8, 4, true, "picture") end
  local pcx, pcy = px + (pw - 1) / 2, S3.PIC_Y + (ph - 1) / 2
  if not l.exists then U.sayC(13, "cream", "COMING SOON", pcx, math.floor(pcy - 7 + 0.5), "soon")
  elseif not open then U.putC("lock_big", pcx, pcy, "lock") end
  U.sayC(17, "gold", l.title, 159.5, S3.NAME, "name")
  -- the stats row on one centre line: the medals from the picture's left edge, the time and points to its right edge
  local cy = S3.STATS
  local m = F.medals(l.name)
  local mw, mh = U.body("medal_nohit_on")
  for k, kind in ipairs(F.MEDALS) do
    U.put(("medal_%s_%s"):format(kind, (ok and m[kind]) and "on" or "off"), px + (k - 1) * (mw + 4), math.floor(cy - (mh - 1) / 2 + 0.5), "medal")
  end
  local best, bt = F.levelBest(l.name), F.levelTimeBest(l.name)
  if ok and (best > 0 or bt) then
    local xr = px + pw - 1
    local th = U.sayH(13)
    local ty = math.floor(cy - (th - 1) / 2 + 0.5)
    local sw = U.sayW(13, tostring(best))
    U.say(13, "gold", tostring(best), xr - sw + 1, ty, "score")
    if bt then
      local ts = F.clock(bt)
      local tw = U.sayW(13, ts)
      local tx = xr - sw + 1 - 10 - tw
      U.say(13, "cream", ts, tx, ty, "time")
      local cw, ch = U.body("clock")
      U.put("clock", tx - U.ICON_GAP - cw, math.floor(cy - (ch - 1) / 2 + 0.5), "clock")
    end
  end
end
function F.drawSelect(t)
  local S3, p = F.SEL, F.pick
  backdropWarm(t)
  local u = math.min(1, (love.timer.getTime() - (p.moved or -1)) / S3.SLIDE)
  local e = 1 - (1 - u) * (1 - u)
  if u < 1 and p.from and p.from ~= p.sel then                       -- the card leaving, then the one coming in
    lg.push(); lg.translate(math.floor(-(p.dir or 1) * 320 * e + 0.5), 0); F.selectCard(p.from); lg.pop()
    lg.push(); lg.translate(math.floor((p.dir or 1) * 320 * (1 - e) + 0.5), 0); F.selectCard(p.sel); lg.pop()
  else F.selectCard(p.sel) end
  -- the arrows on the picture's middle line, nudging out and back; the dots under the card
  local aw, ah = U.body("arrow_l")
  local ay = math.floor(S3.PIC_Y + 59 - (ah - 1) / 2 + 0.5)
  local nudge = (math.floor(love.timer.getTime() * 3) % 2 == 0) and 0 or 1
  U.put("arrow_l", S3.X - S3.ARROW_OUT - aw - nudge, ay, "arrow")
  U.put("arrow_r", S3.X + S3.W + S3.ARROW_OUT + nudge, ay, "arrow")
  local n = #F.levels
  local dw = U.body("dot_on")
  local x0 = math.floor(159.5 - ((n - 1) * S3.DOT_PITCH + dw - 1) / 2 + 0.5)
  for i = 1, n do U.put(i == p.sel and "dot_on" or "dot_off", x0 + (i - 1) * S3.DOT_PITCH, S3.DOTS, "dot") end
  U.strip({ { "lr", "BROWSE" }, { "ok", "PLAY" }, { "back", "BACK" } })
end

-- a card's top on the level: y if the card misses Pepper's sprite (avoid = { x0, y0, x1, y1 } on screen), else
-- the top of the screen, else the bottom (nothing is drawn over Pepper; main.lua draws her again over the dim)
function F.placeY(x, w, y, h, avoid)
  local function miss(yy) return not avoid or not (avoid[1] < x + w and avoid[3] > x and avoid[2] < yy + h and avoid[4] > yy) end
  for _, yy in ipairs({ y, 18, 236 - h }) do if miss(yy) then return yy, true end end
  return y, false
end
-- draws f moved down by dy
local function shifted(dy, f) lg.push(); lg.translate(0, dy); f(); lg.pop() end

-- (step 3) text in lines no wider than maxw at a font size: a line that fits stays whole, a longer one is split where
-- its two halves are most even, else word by word
function F.wrap(size, text, maxw)
  local UF = require("uifont")
  local function wd(x) return UF.width(size, x) + 2 end
  if wd(text) <= maxw then return { text } end
  local words = {}
  for w in text:gmatch("%S+") do words[#words + 1] = w end
  local best, bw
  for k = 1, #words - 1 do
    local a, b = table.concat(words, " ", 1, k), table.concat(words, " ", k + 1)
    local m = math.max(wd(a), wd(b))
    if m <= maxw and (not bw or m < bw) then best, bw = { a, b }, m end
  end
  if best then return best end
  local out, cur = {}, nil
  for _, w in ipairs(words) do
    local try = cur and (cur .. " " .. w) or w
    if cur and wd(try) > maxw then out[#out + 1] = cur; cur = w else cur = try end
  end
  out[#out + 1] = cur
  return out
end
-- (step 3) where a card goes: centred in the room above the controls strip, else at the top, else just above the
-- strip, the first that misses Pepper's sprite; if none does, the one that covers least of her (main.lua draws her
-- over the card in any case)
function F.cardTop(x, w, h, avoid)
  local best, least
  for _, yy in ipairs({ math.floor((U.STRIP_Y - 6 - h) / 2), 4, U.STRIP_Y - 6 - h }) do
    local a = avoid
    local ov = a and math.max(0, math.min(a[3], x + w) - math.max(a[1], x)) * math.max(0, math.min(a[4], yy + h) - math.max(a[2], yy)) or 0
    if ov == 0 then return yy end
    if not least or ov < least then best, least = yy, ov end
  end
  return best
end
-- a card dropping in: 6 frames, ease out, from 10 px up
local function dropIn(t) local u = math.min(1, (t or 1) / 0.1); return -math.floor(10 * (1 - u) * (1 - u) + 0.5) end

-- the level intro card (step 3): the warm dim, the kit's panel with the LEVEL n ribbon, the level's name in the 17 px
-- font and the story (intro lines 3 and 4) in the 13 px font, the controls strip (A GO) once a button starts it
F.I = { X = 26, W = 268, RIB = 0, PANEL = 10, NAME = 25, STORY = 50, PITCH = 16, PAD = 12, TEXT_W = 236 }
function F.introLayout(def)
  local lines = {}
  for k = 3, #(def.intro or {}) do for _, l in ipairs(F.wrap(13, def.intro[k], F.I.TEXT_W)) do lines[#lines + 1] = l end end
  local h = F.I.STORY + (#lines - 1) * F.I.PITCH + U.sayH(13) + F.I.PAD - 1
  return lines, h
end
function F.drawIntro(def, t, avoid)
  local I = F.I
  local lines, h = F.introLayout(def)
  U.dimWarm()
  shifted(F.cardTop(I.X, I.W, h, avoid) + dropIn(t), function()
    U.panel(I.X, I.PANEL, I.W, h - I.PANEL)
    U.ribbon("ribbon_pause", 159.5, I.RIB)
    U.sayC(13, "ink", def.intro[1] or "", 159.5, I.RIB + 2, "title")
    U.sayC(17, "gold", def.intro[2] or "", 159.5, I.NAME, "name")
    for i, l in ipairs(lines) do U.sayC(13, "cream", l, 159.5, I.STORY + (i - 1) * I.PITCH, "story") end
  end)
  if t > 0.5 then U.strip({ { "ok", "GO" } }) end
end

-- between two levels: what happened at the end of the level just cleared (its L.outro). (step 3) A story moment, so
-- the portrait panel: the warm dim, Mia telling it in the kit's gold panel (13 px, each outro line split where its
-- halves are most even), her portrait (the talking loop while the lines are read) in the thin gold frame on the
-- panel's right end; the group centred where it misses Pepper. After CARD_WAIT the strip shows (A) GO ON (only A).
F.ST = { W_TEXT = 200, PAD_X = 16, PAD_Y = 12, PITCH = 16, IN = 12 }
function F.storyLayout(lines, other)
  local Talk = require("talk")
  -- the bubble keeps above the controls strip at the bottom
  return Talk.raise(Talk.cornerLayout(Talk.port("girl"), lines or {}, false, other), F.STRIP_TOP - 3)
end
-- (owner 24 Oct: a speech bubble, Mia never cropped, no frame) Mia in her corner telling it, the cream bubble beside
-- her; the other corner (mirrored) when Pepper stands in hers
function F.drawStory(lines, t, avoid)
  local Talk = require("talk")
  local L = F.storyLayout(lines)
  local a = avoid and (type(avoid[1]) == "table" and avoid[1] or avoid)   -- Pepper's rect { x0, y0, x1, y1 }
  local function hit(L)
    for _, r in ipairs(L.rects) do if r[1] < a[3] and r[3] > a[1] and r[2] < a[4] and r[4] > a[2] then return true end end
  end
  if a and hit(L) then
    local L2 = F.storyLayout(lines, true)
    if not hit(L2) then L = L2 else L = Talk.above(F.storyLayout(lines)) end      -- else over her head, in her corner
  end
  U.dimWarm()
  F.storyCard(lines, t, L)
  if t >= F.CARD_WAIT then U.strip({ { "ok", "GO ON" } }) end
end
function F.storyCard(lines, t, L)
  local Talk = require("talk")
  L = L or F.storyLayout(lines)
  local talkFor = math.min(3.0, 0.6 + 0.04 * #table.concat(lines or {}, " "))
  local f = t < talkFor and 1 + math.floor(t * Talk.FPS) % Talk.FRAMES or 1
  local u = math.min(1, t / 0.25)
  Talk.drawCorner(L, f, math.floor(8 * (1 - u) * (1 - u) + 0.5), "story")
end
F.STRIP_TOP = U.STRIP_Y               -- the controls strip's top row (the story bubble keeps above it)
F.CARD_WAIT = 2                   -- seconds before A leaves a story card

-- the tally after a level. tl: { lines, shown, from, points, t, done, newBest, time, best, newBestTime, par, medals,
-- hard }. avoid: Pepper's sprite on screen (x0, y0, x1, y1).
-- (step 3) a show, not a table: the warm dim, the kit's panel under the arched GOOD GIRL! ribbon; BONES counts up
-- with a tick per bone, then the level's bonus (FETCH), TIME BONUS and the TOTAL (counting up, a tick each 500),
-- each line sliding in with its picture (the bone, the ball, the clock); then the medals pop in one by one with
-- their names; the clear time, the best time and the secrets found in the small font; NEW BEST! lands as a stamp
-- (a new best score or time); then the controls strip. Any button skips to the end (main.lua). Same numbers as
-- before; F.tallyStep runs the clock and the sounds. Offsets from the card's top (the ribbon's top).
F.T = { X = 36, W = 248, PANEL = 18, H = 115, ICON = 48, LABEL = 71, VALUE = 188, ROW0 = 38, PITCH = 18, RULE = 92, TOTAL = 96,
  MEDAL_X = 197, MEDAL0 = 38, MPITCH = 21, SECRETS = 104, NOTE = 116, BOX_H = 134, STAMP_Y = 125, STAMP_OUT = 6 }
-- the show's timetable: when each line comes (rows: { label, value, kind, at }), the bones' count, the total's
-- count, the medals and the stamp; tl.tEnd when it is over
function F.tallyPlan(tl)
  if tl.plan then return tl.plan end
  local P = { rows = {}, medals = {} }
  local t = 0.45
  local bones = tl.lines[1]
  local n = tonumber((bones[2] or ""):match("^(%d+)")) or 0
  P.bonesN, P.bonesT0, P.bonesD = n, t, math.min(1.5, n * 0.05)
  P.rows[1] = { "BONES", bones[2], "bone", t }
  t = t + P.bonesD + 0.3
  for i = 2, #tl.lines do
    local l = tl.lines[i]
    if l[1] == "SECRETS" then P.secrets = l[2]
    else P.rows[#P.rows + 1] = { l[1], l[2], l[1] == "TIME BONUS" and "clock" or "ball", t }; t = t + 0.3 end
  end
  P.totalT0, P.totalD = t + 0.05, 0.9
  t = P.totalT0 + P.totalD + 0.25
  for k = 1, #F.MEDALS do P.medals[k] = t; t = t + 0.3 end
  P.noteT = t - 0.15
  if tl.newBest or tl.newBestTime then P.stampT = t + 0.1; t = t + 0.5 end
  P.tEnd = t + 0.1
  tl.plan = P
  return P
end
-- every frame of the show: the clock, the counts and their sounds; done at the end
function F.tallyStep(tl, dt)
  local P = F.tallyPlan(tl)
  local t0 = tl.t; tl.t = tl.t + dt; local t1 = tl.t
  local function crossed(at) return t0 < at and t1 >= at end
  if P.bonesN > 0 and t1 > P.bonesT0 then                          -- a tick per bone counted
    local function cnt(t) return math.max(0, math.min(P.bonesN, math.floor((t - P.bonesT0) / math.max(0.01, P.bonesD) * P.bonesN))) end
    if cnt(t1) > cnt(t0) then S.play("tick") end
  end
  for i = 2, #P.rows do if crossed(P.rows[i][4]) then S.play("tick") end end
  if t1 > P.totalT0 then
    local before = tl.shown
    tl.shown = math.min(tl.points, math.floor(tl.points * math.min(1, (t1 - P.totalT0) / P.totalD)))
    if math.floor(before / 500) ~= math.floor(tl.shown / 500) then S.play("tick") end
  end
  for k, at in ipairs(P.medals) do if crossed(at) then S.play(tl.medals[F.MEDALS[k]] and "key" or "push") end end
  if P.stampT and crossed(P.stampT) then S.play("stamp") end
  if t1 >= P.tEnd then tl.shown, tl.done = tl.points, true end
end
-- any button during the show: straight to its end (no sounds owed)
function F.tallySkip(tl)
  local P = F.tallyPlan(tl)
  tl.t = math.max(tl.t, P.tEnd); tl.shown, tl.done = tl.points, true
end
function F.tallyBox(avoid)
  local T = F.T
  return T.X, F.cardTop(T.X, T.W, T.BOX_H, avoid), T.W, T.BOX_H
end
function F.drawTally(tl, avoid)
  local _, y = F.tallyBox(avoid)
  U.dimWarm(); shifted(y, function() F.tallyCard(tl) end)
  if tl.done then U.strip({ { "ok", "OK" } }) end
end
-- an item sliding in from 6 px left over 6 frames once its time comes (nil: not yet)
local function slide(t, at) if t < at then return nil end; local u = math.min(1, (t - at) / 0.1); return -math.floor(6 * (1 - u) * (1 - u) + 0.5) end
function F.tallyCard(tl)
  local T, P = F.T, F.tallyPlan(tl)
  local t = tl.t
  U.panel(T.X, T.PANEL, T.W, T.H)
  U.ribbon("ribbon_tally", 159.5, 0)
  local bounce = (t < 0.6) and math.floor(math.sin(t * 20) * 2) or 0
  U.sayC(17, "ink", "GOOD GIRL!", 159.5, 4 + bounce, "title")
  local th7, th13 = U.sayH(7), U.sayH(13)
  for i, r in ipairs(P.rows) do                                    -- the lines, each on its centre line
    local dx = slide(t, r[4])
    if dx then
      local cy = T.ROW0 + (i - 1) * T.PITCH + (th13 - 1) / 2
      local value = r[2]
      if i == 1 and P.bonesN > 0 then                              -- BONES counts up
        local c = math.max(0, math.min(P.bonesN, math.floor((t - P.bonesT0) / math.max(0.01, P.bonesD) * P.bonesN)))
        value = tostring(c) .. (r[2]:match("(/%d+)$") or "")
      end
      local iw, ih = U.body(r[3])
      U.put(r[3], T.ICON + dx + math.floor((19 - iw) / 2), math.floor(cy - (ih - 1) / 2 + 0.5), "ticon")
      U.say(7, "cream", r[1], T.LABEL + dx, math.floor(cy - (th7 - 1) / 2 + 0.5), "tlabel")
      U.say(13, "gold", value, T.VALUE - U.sayW(13, value) + 1 + dx, math.floor(cy - (th13 - 1) / 2 + 0.5), "tvalue")
    end
  end
  local dx = slide(t, P.totalT0)
  if dx then                                                       -- the rule and the TOTAL, counting up
    lg.setColor(64 / 255, 11 / 255, 6 / 255); lg.rectangle("fill", T.ICON, T.RULE, T.VALUE - T.ICON + 1, 1)
    lg.setColor(196 / 255, 102 / 255, 24 / 255); lg.rectangle("fill", T.ICON, T.RULE + 1, T.VALUE - T.ICON + 1, 1); lg.setColor(1, 1, 1, 1)
    U.logBox("rule", T.ICON, T.RULE, T.VALUE, T.RULE + 1)
    U.say(13, "gold", "TOTAL", T.ICON + dx, T.TOTAL, "tlabel")
    local v = tostring(tl.shown)
    U.say(13, "gold", v, T.VALUE - U.sayW(13, v) + 1 + dx, T.TOTAL, "tvalue")
  end
  local names = { nohit = "NO HIT", bones = "ALL BONES", par = "PAR " .. F.clock(tl.par):gsub("%.0$", "") }
  local mw, mh = U.body("medal_nohit_on")
  for k, kind in ipairs(F.MEDALS) do                               -- the medals pop in: up 3 px, then down
    local at = P.medals[k]
    if t >= at then
      local won = tl.medals[kind]
      local pop = (t - at < 0.05) and -2 or (t - at < 0.1) and -1 or 0
      local my = T.MEDAL0 + (k - 1) * T.MPITCH
      U.put(("medal_%s_%s"):format(kind, won and "on" or "off"), T.MEDAL_X, my + pop, "medal")
      U.say(7, won and "gold" or "dim", names[kind], T.MEDAL_X + mw + U.ICON_GAP, math.floor(my + (mh - 1) / 2 - (th7 - 1) / 2 + 0.5), "mlabel")
    end
  end
  if t >= P.noteT then                                             -- the times and the secrets, small
    local ts = ("TIME %s  BEST %s"):format(F.clock(tl.time), F.clock(tl.best))
    U.say(7, tl.newBestTime and "gold" or "cream", ts, T.ICON, T.NOTE, "note")
    if P.secrets then U.say(7, "cream", "SECRETS " .. P.secrets, T.MEDAL_X, T.SECRETS, "secrets") end
  end
  if tl.hard then U.hardTag8(T.X + 34, T.PANEL + 4) end
  if P.stampT and t >= P.stampT then                               -- NEW BEST! lands across the frame's bottom right
    local sw = U.body("stamp")
    local k = math.floor((t - P.stampT) / (1 / 30))                -- it lands with a thud: a 2 px jolt for 4 frames
    local jx = (k < 4) and ((k % 2 == 0) and 2 or -1) or 0
    U.put("stamp", T.X + T.W - 1 + T.STAMP_OUT - sw + 1 + jx, T.STAMP_Y + ((k < 2) and 1 or 0), "stamp")
  end
end

-- GAME OVER: o = { sel } (1 TRY AGAIN, 2 MENU)
F.OVER_WAIT = 1.2
F.overItems = { "TRY AGAIN", "MENU" }
-- (step 3) the warm dim, the kit's panel with the GAME OVER ribbon, after OVER_WAIT the two rows as plain outlined text
-- (the selected one gold, the paw coin before it) and the strip (A) OK
F.OV = { X = 80, W = 160, RIB = 0, PANEL = 10, ROW0 = 35, PITCH = 20, H = 70, LABEL_IN = 44, CUR_IN = 19 }
function F.drawOver(o, t, avoid)
  local V = F.OV
  U.dimWarm(); shifted(F.cardTop(V.X, V.W, V.PANEL + V.H, avoid) + dropIn(t), function() F.overCard(o, t) end)
  if t >= F.OVER_WAIT then U.strip({ { "ok", "OK" } }) end
end
function F.overCard(o, t)
  local V = F.OV
  U.panel(V.X, V.PANEL, V.W, V.H)
  U.ribbon("ribbon_menu", 159.5, V.RIB)
  U.sayC(13, "ink", "GAME OVER", 159.5, V.RIB + 2, "title")
  if t < F.OVER_WAIT then return end
  local th = U.sayH(13)
  local function rowY(i) return V.ROW0 + (i - 1) * V.PITCH end
  for i, it in ipairs(F.overItems) do U.say(13, o.sel == i and "gold" or "cream", it, V.X + V.LABEL_IN, rowY(i), "label") end
  local cw, ch = U.body("coin_paw")
  local cy = cursorY({ sel = o.sel, from = o.from or o.sel, moved = o.moved }, rowY) + (th - 1) / 2
  U.put("coin_paw", V.X + V.CUR_IN, math.floor(cy - (ch - 1) / 2 + 0.5) - bob(), "cursor")
end
-- the cursor of a two-item card: "up" / "down" move it, returns the item on "ok"
function F.cursor(o, a, n)
  if a == "up" or a == "down" then o.from, o.moved = o.sel, love.timer.getTime(); o.sel = (o.sel + (a == "up" and -2 or 0)) % n + 1; S.play("tick")
  elseif a == "ok" then S.play("select"); return o.sel end
end

-- the pause: pz = { sel (1 GO ON, 2 SOUND, 3 CONTROLS, 4 QUIT), confirm (nil, or the QUIT? card's sel: 1 NO, 2 YES),
-- controls (true: the controls page is open over the level) }
-- SOUND: left / right turn the game's volume down or up (0 is off), A steps it up and wraps round to off
F.pauseItems, F.confirmItems = { "GO ON", "SOUND", "CONTROLS", "QUIT" }, { "NO", "YES, QUIT" }
F.PAUSE_SOUND, F.PAUSE_CONTROLS, F.PAUSE_QUIT = 2, 3, 4
-- (step 3) the owner's pause, for a child: the warm dim, the kit's gold panel with the PAUSED ribbon over its top edge,
-- the level's name (7 px) and the bones found (the bone and the count, 13 px), then the rows as plain outlined text
-- (only the selected one gold, the paw coin before it, eased between rows with a 1 px bob), SOUND's 9-segment meter at
-- the right; no boxes round the rows, no buttons hanging off the frame: the controls strip at the bottom. QUIT asks
-- first in the same card. Offsets from the card's top (the ribbon's top); the card goes where it misses Pepper.
F.P = { X = 70, W = 180, RIB = 0, PANEL = 10, SUB = 24, BONES = 42, ROW0 = 57, PITCH = 17, H = 124, BOX_H = 134,
  LABEL_IN = 38, CUR_IN = 13, RIGHT_IN = 16, SEGS = 4 }
function F.drawPause(pz, def, avoid, st)
  local P = F.P
  if pz.controls then F.drawControls(0, true); return end
  U.dimWarm(); shifted(F.cardTop(P.X, P.W, P.BOX_H, avoid), function() F.pauseCard(pz, def, st) end)
  local items = { { "ok", "OK" }, { "back", "BACK" } }
  if not pz.confirm and pz.sel == F.PAUSE_SOUND then items = { { "lr", "CHANGE" }, { "back", "BACK" } } end
  U.strip(items)
end
function F.pauseCard(pz, def, st)
  local Se = require("settings")
  local P = F.P
  U.panel(P.X, P.PANEL, P.W, P.H)
  U.ribbon("ribbon_pause", 159.5, P.RIB)
  U.sayC(13, "ink", "PAUSED", 159.5, P.RIB + 2, "title")
  U.sayC(7, "cream", ("LEVEL %d %s"):format(def.number or 1, (def.name or ""):upper()), 159.5, P.SUB, "subtitle")
  local th = U.sayH(13)
  local items, sel, m = F.pauseItems, pz.sel, pz
  if pz.confirm then
    items, sel = F.confirmItems, pz.confirm
    m = pz.cm or {}; pz.cm = m; m.sel = pz.confirm
    U.sayC(13, "gold", "QUIT TO MENU?", 159.5, math.floor(P.BONES - (th - 1) / 2 + 0.5), "question")
  else
    pz.cm = nil
    local bstr = st and ("%d/%d"):format(st.bones, st.total) or ""
    local bw, bh = U.body("bone")
    local nw = U.sayW(13, bstr)
    local gx = math.floor(159.5 - (bw + U.ICON_GAP + nw - 1) / 2 + 0.5)
    U.put("bone", gx, math.floor(P.BONES - (bh - 1) / 2 + 0.5), "bone")
    U.say(13, "gold", bstr, gx + bw + U.ICON_GAP, math.floor(P.BONES - (th - 1) / 2 + 0.5), "bones")
  end
  local function rowY(i) return P.ROW0 + (i - 1) * P.PITCH end
  local xr = P.X + P.W - 1 - P.RIGHT_IN
  for i, it in ipairs(items) do
    local on = sel == i
    local y = rowY(i)
    U.say(13, on and "gold" or "cream", it, P.X + P.LABEL_IN, y, "label")
    if not pz.confirm and i == F.PAUSE_SOUND then                -- one segment a step, lit up to the level
      local segw, segh = U.body("seg_on")
      local mw = (Se.MAX - 1) * P.SEGS + segw
      local mx, my = xr - mw + 1, math.floor(y + (th - 1) / 2 - (segh - 1) / 2 + 0.5)
      for k = 1, Se.MAX do U.put(k <= Se.volume and "seg_on" or "seg_off", mx + (k - 1) * P.SEGS, my, "seg") end
      U.logBox("meter", mx, my, mx + mw - 1, my + segh - 1)
    end
  end
  local cw, ch = U.body("coin_paw")
  if (m.from or 0) > #items then m.from = sel end
  local cy = cursorY({ sel = sel, from = m.from or sel, moved = m.moved }, rowY) + (th - 1) / 2
  U.put("coin_paw", P.X + P.CUR_IN, math.floor(cy - (ch - 1) / 2 + 0.5) - bob(), "cursor")
end

-- after the last level: e = { score, best, newBest, lines (the last level's outro, optional) }. (step 3) The title
-- picture under the warm dim, the kit's panel under the arched GOOD GIRL! ribbon: the outro (13 px), FINAL SCORE (7 px)
-- and the run's score (17 px gold), NEW BEST RUN! (13 px gold, blinking) or the best run (7 px), THE END (17 px) and
-- THANKS FOR PLAYING (7 px); the strip (A) OK once a button leaves it.
F.EN = { X = 30, W = 260, PANEL = 18, TEXT_W = 228 }
function F.drawEnding(e, t)
  local E = F.EN
  backdropWarm(t)
  local rows = {}
  for _, l in ipairs(e.lines or {}) do for _, r in ipairs(F.wrap(13, l, E.TEXT_W)) do rows[#rows + 1] = r end end
  local y = 40
  local items = {}
  local function add(h, f) items[#items + 1] = { y, f }; y = y + h end
  for _, r in ipairs(rows) do add(16, function(yy) U.sayC(13, "cream", r, 159.5, yy, "story") end) end
  y = y + 5
  add(11, function(yy) U.sayC(7, "cream", "FINAL SCORE", 159.5, yy, "label") end)
  add(22, function(yy) U.sayC(17, "gold", ("%06d"):format(e.score), 159.5, yy, "score") end)
  if e.newBest then add(18, function(yy) if math.floor(t * 3) % 2 == 0 then U.sayC(13, "gold", "NEW BEST RUN!", 159.5, yy, "best") end end)
  else add(14, function(yy) U.sayC(7, "cream", ("BEST RUN %06d"):format(e.best), 159.5, yy, "best") end) end
  y = y + 4
  add(22, function(yy) U.sayC(17, "gold", "THE END", 159.5, yy, "end") end)
  add(11, function(yy) U.sayC(7, "cream", "THANKS FOR PLAYING", 159.5, yy, "thanks") end)
  local h = y + 10 - E.PANEL
  U.panel(E.X, E.PANEL, E.W, h)
  U.ribbon("ribbon_tally", 159.5, 0)
  local bounce = (t < 0.6) and math.floor(math.sin(t * 20) * 2) or 0
  U.sayC(17, "ink", "GOOD GIRL!", 159.5, 4 + bounce, "title")
  for _, it in ipairs(items) do it[2](it[1]) end
  if t > F.ENDING_WAIT then U.strip({ { "ok", "OK" } }) end
end
F.ENDING_WAIT = 2                 -- seconds before a key leaves the ending
return F
