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
function F.selectInput(a)
  local p = F.pick
  if a == "up" or a == "down" then p.sel = (p.sel + (a == "up" and -2 or 0)) % #F.levels + 1; S.play("tick")
  elseif a == "ok" then
    if F.levels[p.sel].exists and F.isOpen(p.sel) then S.play("select"); return "play", p.sel end
    S.play("push")                                               -- locked or coming soon: a dull thud
  elseif a == "back" then S.play("tick"); return "back" end
end

-- the menus' background: the title picture, animated, dimmed
local function backdrop(t) Title.draw(t, nil, true); U.dim() end
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
function F.drawControls(t)
  local C = F.C
  backdropWarm(t)
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

function F.drawSelect(t)
  backdrop(t)
  U.box(40, 10, 240, 208)
  U.center("LEVEL SELECT", 160, 18, 2, U.GOLD)
  if F.hard then U.hardTag(244, 20) end
  -- (r5/bugs: rows of 30 px, so all five levels fit in the panel; at 46 px the fourth ran under the footer and the
  -- fifth, NIGHT HARBOUR, hung off the panel and the screen)
  -- (r6/levels: six levels: rows of 26 px from y 40, the note 17 px under the title, the highlight the whole row)
  local step = math.min(46, math.floor(156 / #F.levels))
  local y0, ny = step < 30 and 40 or 42, 17                        -- the first row's y; the note's y in a row
  for i, l in ipairs(F.levels) do
    local y = y0 + (i - 1) * step
    local on, open = F.pick.sel == i, F.isOpen(i)
    local ok = open and l.exists
    if on then lg.setColor(U.EDGE); lg.rectangle("fill", 46, y - 3, 228, step < 30 and step or step - 1); lg.setColor(1, 1, 1, 1) end
    local col = ok and (on and U.GOLD or U.WHITE) or U.RIM
    U.center(tostring(l.number), 62, y + 4, 2, col)
    U.center(l.title, 164, y, 2, col)
    local note
    if not l.exists then note = "COMING SOON"
    elseif not open then note = "LOCKED"
    else
      local b, bt = F.levelBest(l.name), F.levelTimeBest(l.name)
      note = b > 0 and ("BEST %06d"):format(b) or "NOT PLAYED YET"
      if bt then note = note .. "  " .. F.clock(bt) end
    end
    if ok and (F.levelBest(l.name) > 0 or F.levelTimeBest(l.name)) then     -- played: its best and its medals
      U.text(note, 76, y + ny, U.WHITE)
      local m = F.medals(l.name)
      for k, kind in ipairs(F.MEDALS) do U.medal(kind, 216 + (k - 1) * 14, y + ny - 2, m[kind]) end
    else U.center(note, 164, y + ny, 1, ok and U.WHITE or U.RIM) end
    if not ok then U.lock(253, y + 4, U.RIM, 2) end
  end
  U.center("A PLAY    B BACK", 160, 200, 1, U.RIM)
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

-- between two levels: what happened at the end of the level just cleared (its L.outro)
function F.drawStory(lines, t, avoid)
  U.dim()
  shifted(F.placeY(36, 248, 76, 70, avoid) - 76, function() F.storyCard(lines, t) end)
end
function F.storyCard(lines, t)
  U.box(36, 76, 248, 70)
  U.dog(150, 86, U.GOLD, 2)
  for i, s in ipairs(lines) do U.center(s, 160, 108 + (i - 1) * 12, 1) end
  if t >= F.CARD_WAIT and blink(t) then Talk.glyph("a", 270, 134, "small") end   -- ready: A goes on
end
F.CARD_WAIT = 2                   -- seconds before A leaves a story card

-- the tally after a level. tl: { lines, shown, from, points, t, done, newBest, time, best, newBestTime, par,
-- medals, secrets, hard }. avoid: Pepper's sprite on screen (x0, y0, x1, y1): the card is centred, or at the top
-- when she would be under it (main.lua draws her over the card in any case).
-- (ui/hud-v8) drawn to the owner's tally target: the smooth warm dim, the kit's gold panel, the arched ribbon with
-- GOOD GIRL! in the big font, two columns in the small font (the level's points and the score on the left; the
-- times and the three medals on the right), PRESS ANY BUTTON on the frame's bottom edge. Same data, same timing.
-- Offsets from the card's top (the ribbon's top).
F.T = { X = 45, W = 230, PANEL = 18, H = 113, L = 62, LR = 168, R = 180, RR = 258, ROW0 = 38, PITCH = 11, SCORE = 86,
  MEDAL0 = 60, MPITCH = 19, NOTE = 98, BOX_H = 135 }
function F.tallyBox(avoid)
  local T = F.T
  local y = math.floor((240 - T.BOX_H) / 2)
  local function miss(yy) return not avoid or not (avoid[1] < T.X + T.W and avoid[3] > T.X and avoid[2] < yy + T.BOX_H and avoid[4] > yy) end
  local clear = miss(y)
  if not clear and miss(2) then y, clear = 2, true end
  return T.X, y, T.W, T.BOX_H, clear
end
function F.drawTally(tl, avoid)
  local _, y = F.tallyBox(avoid)
  U.dimWarm(); shifted(y, function() F.tallyCard(tl) end)
end
function F.tallyCard(tl)
  local T = F.T
  U.panel(T.X, T.PANEL, T.W, T.H)
  U.ribbon("ribbon_tally", 159.5, 0)
  local bounce = (tl.t < 0.6) and math.floor(math.sin(tl.t * 20) * 2) or 0
  local tw = U.sayW(17, "GOOD GIRL!")
  U.say(17, "ink", "GOOD GIRL!", math.floor(159.5 - (tw - 1) / 2 + 0.5), 4 + bounce, "title")
  local function row(label, value, y, lx, rx, style)
    U.say(7, style, label, lx, y, "tlabel")
    U.say(7, style, value, rx - U.sayW(7, value) + 1, y, "tvalue")
  end
  for i, l in ipairs(tl.lines) do                                  -- the level's points, one line each
    if tl.t > 0.3 + i * 0.25 then row(l[1], l[2], T.ROW0 + (i - 1) * T.PITCH, T.L, T.LR, "cream") end
  end
  if tl.t > 1.3 then row("SCORE", tostring(tl.from + tl.shown), T.SCORE, T.L, T.LR, "gold") end   -- (counts up)
  if tl.t > 0.55 then
    row("TIME", F.clock(tl.time), T.ROW0, T.R, T.RR, "cream")
    row("BEST", F.clock(tl.best), T.ROW0 + T.PITCH, T.R, T.RR, "cream")
  end
  local names = { nohit = "NO HIT", bones = "ALL BONES", par = "PAR " .. F.clock(tl.par):gsub("%.0$", "") }
  local mw, mh = U.body("medal_on")
  local th = U.sayH(7)
  for k, kind in ipairs(F.MEDALS) do
    if tl.t > 1.3 + k * 0.2 then
      local won, my = tl.medals[kind], T.MEDAL0 + (k - 1) * T.MPITCH
      U.put(won and "medal_on" or "medal_off", T.R, my, "medal")
      U.say(7, won and "gold" or "dim", names[kind], T.R + mw + U.ICON_GAP, math.floor(my + (mh - 1) / 2 - (th - 1) / 2 + 0.5), "mlabel")
    end
  end
  local line = T.PANEL + T.H - 6                                  -- the frame's bottom gold line
  if tl.hard then U.hardTag8(T.X + 34, line - 6) end
  if tl.done then
    local blinkOn = math.floor(tl.t * 3) % 2 == 0
    local ny = T.NOTE
    if tl.newBest then if blinkOn then U.say(7, "gold", "NEW BEST SCORE!", T.L, ny, "note") end; ny = ny + T.PITCH end
    if tl.newBestTime and blinkOn then U.say(7, "gold", "NEW BEST TIME!", T.L, ny, "note") end
    if blink(tl.t) then
      local pw = U.sayW(7, "PRESS ANY BUTTON")
      local px = math.floor(159.5 - (pw - 1) / 2 + 0.5)
      lg.setColor(64 / 255, 11 / 255, 6 / 255); lg.rectangle("fill", px, line, pw, 1); lg.setColor(1, 1, 1, 1)   -- (the gold line not between the words)
      U.say(7, "cream", "PRESS ANY BUTTON", px, line - (th - 1) / 2, "press")
    end
  end
end

-- GAME OVER: o = { sel } (1 TRY AGAIN, 2 MENU)
F.OVER_WAIT = 1.2
F.overItems = { "TRY AGAIN", "MENU" }
function F.drawOver(o, t, avoid)
  U.dim(); shifted(F.placeY(86, 148, 76, 92, avoid) - 76, function() F.overCard(o, t) end)
end
function F.overCard(o, t)
  U.box(86, 76, 148, 92); U.center("GAME OVER", 160, 84, 2)
  if t < F.OVER_WAIT then return end
  for i, it in ipairs(F.overItems) do
    local iy = 108 + (i - 1) * 20
    local on = o.sel == i
    if on then lg.setColor(U.EDGE); lg.rectangle("fill", 92, iy - 3, 136, 19); lg.setColor(1, 1, 1, 1) end
    U.center(it, 160, iy + 1, 2, on and U.GOLD or U.WHITE)
  end
  Talk.glyph("a", 144, 156, "small"); U.text("OK", 154, 153)
end
-- the cursor of a two-item card: "up" / "down" move it, returns the item on "ok"
function F.cursor(o, a, n)
  if a == "up" or a == "down" then o.sel = (o.sel + (a == "up" and -2 or 0)) % n + 1; S.play("tick")
  elseif a == "ok" then S.play("select"); return o.sel end
end

-- the pause: pz = { sel (1 GO ON, 2 SOUND, 3 QUIT), confirm (nil, or the QUIT? card's sel: 1 NO, 2 YES) }
-- SOUND: left / right turn the game's volume down or up (0 is off), A steps it up and wraps round to off
F.pauseItems, F.confirmItems = { "GO ON", "SOUND", "QUIT" }, { "NO", "YES, QUIT" }
F.PAUSE_SOUND, F.PAUSE_QUIT = 2, 3
-- (ui/hud-v8) drawn to the owner's pause target: the smooth warm dim, the kit's gold panel, the PAUSED ribbon over
-- its top edge, the level in the small font, three rows (the selected one gold with the paw coin over its left end),
-- the A and B coins with their OK / BACK tabs across the bottom edge. Layout in game px; the card's top is P.Y.
-- Offsets from the card's top (the ribbon's top). The card goes where it misses Pepper: centred, else at the top.
F.P = { X = 75, W = 170, RIB = 0, PANEL = 10, SUB = 24, ROW0 = 35, ROW_H = 19, PITCH = 21, PAD = 15, H = 106,
  BOX_H = 136, CUR_OUT = 6, LABEL_IN = 18, SEGS = 4 }
function F.drawPause(pz, def, avoid)
  local P = F.P
  local y = math.floor((240 - P.BOX_H) / 2)
  local function miss(yy) local a = avoid; return not a or not (a[1] < P.X + P.W and a[3] > P.X and a[2] < yy + P.BOX_H and a[4] > yy) end
  if not miss(y) and miss(2) then y = 2 end
  U.dimWarm(); shifted(y, function() F.pauseCard(pz, def) end)
end
function F.pauseCard(pz, def)
  local Se = require("settings")
  local P = F.P
  local line = P.PANEL + P.H - 6                                  -- the frame's bottom gold line
  local tabw = U.body("tab")
  for _, cx in ipairs({ 131, 188 }) do U.put("tab", cx - (tabw - 1) / 2, line, "tab") end   -- (hanging behind the frame)
  U.panel(P.X, P.PANEL, P.W, P.H)
  U.ribbon("ribbon_pause", 159.5, P.RIB)
  local tw = U.sayW(13, "PAUSED")
  U.say(13, "ink", "PAUSED", math.floor(159.5 - (tw - 1) / 2 + 0.5), P.RIB + 2, "title")
  local items, sel = F.pauseItems, pz.sel
  local sub = ("LEVEL %d %s"):format(def.number or 1, (def.name or ""):upper())
  if pz.confirm then sub, items, sel = "QUIT TO THE MENU?", F.confirmItems, pz.confirm end
  local sw = U.sayW(7, sub)
  U.say(7, "cream", sub, math.floor(159.5 - (sw - 1) / 2 + 0.5), P.SUB, "subtitle")
  local rx = P.X + P.PAD
  local rw = P.W - 2 * P.PAD
  local th = U.sayH(13)
  for i, it in ipairs(items) do
    local ry = P.ROW0 + (i - 1) * P.PITCH
    local on = sel == i
    U.put(on and "row_on" or "row_off", rx, ry, "row")
    local cy = ry + (P.ROW_H - 1) / 2
    local ly = math.floor(cy - (th - 1) / 2 + 0.5)
    if on then local _, ch = U.body("coin_paw"); U.put("coin_paw", rx - P.CUR_OUT, math.floor(cy - (ch - 1) / 2 + 0.5), "cursor") end
    U.say(13, "cream", it, rx + P.LABEL_IN, ly, "label")
    if not pz.confirm and i == F.PAUSE_SOUND then                -- the sound level: one segment a step, lit up to it
      local segw, segh = U.body("seg_on")
      local mw = (Se.MAX - 1) * P.SEGS + segw
      local mx, my = rx + rw - 6 - mw, math.floor(cy - (segh - 1) / 2 + 0.5)
      -- a dark trough under the meter (it reads on the gold row too): ink edge, the dark row's fill
      lg.setColor(64 / 255, 11 / 255, 6 / 255); lg.rectangle("fill", mx - 2, my - 2, mw + 4, segh + 4)
      lg.setColor(44 / 255, 22 / 255, 14 / 255); lg.rectangle("fill", mx - 1, my - 1, mw + 2, segh + 2); lg.setColor(1, 1, 1, 1)
      for k = 1, Se.MAX do U.put(k <= Se.volume and "seg_on" or "seg_off", mx + (k - 1) * P.SEGS, my, "seg") end
      U.logBox("meter", mx, my, mx + mw - 1, my + segh - 1)
    end
  end
  -- A and B: coins centred on the frame's bottom gold line, their tabs hanging under them with OK / BACK
  local cw, ch = U.body("btn_a")
  for k, b in ipairs({ { "btn_a", "OK" }, { "btn_b", "BACK" } }) do
    local cx = k == 1 and 131 or 188
    U.put(b[1], cx - (cw - 1) / 2, line - (ch - 1) / 2, "button")
    local hw = U.sayW(7, b[2])
    U.say(7, "cream", b[2], math.floor(cx - (hw - 1) / 2 + 0.5), line + (ch - 1) / 2 + 3, "hint")
  end
end

-- after the last level: e = { score, best, newBest, lines (the last level's outro, optional) }
function F.drawEnding(e, t)
  backdrop(t)
  U.box(40, 14, 240, 200)
  local bounce = (t < 0.6) and math.floor(math.sin(t * 20) * 2) or 0
  U.center("GOOD GIRL!", 160, 34 + bounce, 3, U.GOLD)
  local y = 70
  for _, s in ipairs(e.lines or {}) do U.center(s, 160, y, 1); y = y + 10 end
  U.center("FINAL SCORE", 160, y + 4, 1)
  U.center(("%06d"):format(e.score), 160, y + 16, 2, U.GOLD)
  if e.newBest then if math.floor(t * 3) % 2 == 0 then U.center("NEW BEST RUN!", 160, y + 38, 1, U.GOLD) end
  else U.center(("BEST RUN %06d"):format(e.best), 160, y + 38, 1) end
  lg.setColor(U.RIM); lg.rectangle("fill", 72, y + 56, 176, 1); lg.setColor(1, 1, 1, 1)
  U.center("THE END", 160, y + 68, 2)
  U.center("THANKS FOR PLAYING", 160, y + 88, 1)
  if t > F.ENDING_WAIT and blink(t) then U.center("PRESS ANY BUTTON", 160, 196, 1) end
end
F.ENDING_WAIT = 2                 -- seconds before a key leaves the ending
return F
