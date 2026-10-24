-- The game around the levels: the run, the menus, the story cards, the ending and what is saved.
--   The run:      the levels of levels.lua in order, from the first one (START GAME) or the one picked in the level
--                 select, to the end. One score for the whole run, lives carry from level to level, hearts refill
--                 and the timer starts again in every level. A level whose file is missing is skipped.
--   Main menu:    START GAME, LEVEL SELECT, over the title picture (dimmed, the logo stays bright).
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

-- the main menu and the level select: the cursor moves; returns what was chosen
F.menu = { sel = 1, items = { "START GAME", "LEVEL SELECT", "HARD MODE" } }
F.pick = { sel = 1 }
function F.menuInput(a)
  local m = F.menu
  if a == "up" or a == "down" then m.sel = (m.sel + (a == "up" and -2 or 0)) % #m.items + 1; S.play("tick")
  elseif a == "ok" then
    S.play("select")
    if m.sel == 3 then F.setHard(not F.hard); return "hard" end
    return m.sel == 1 and "start" or "select"
  elseif a == "back" then return "back" end
end
function F.selectInput(a)
  local p = F.pick
  if a == "up" or a == "down" then p.sel = (p.sel + (a == "up" and -2 or 0)) % #F.levels + 1; S.play("tick")
  elseif a == "ok" then
    if F.levels[p.sel].exists and F.isOpen(p.sel) then S.play("select"); return "play", p.sel end
    S.play("push")                                               -- locked or coming soon: a dull thud
  elseif a == "back" then S.play("tick"); return "back" end
end

-- the menus' background: the title picture, animated, under the smooth warm dim (the level select)
local function backdrop(t) Title.draw(t, nil, true); U.dimWarm() end
local function blink(t) return (t % 1.1) < 0.75 end
local function centreX(w, cx) return math.floor((cx or 159.5) - (w - 1) / 2 + 0.5) end
-- (ui/hud-v8) the kit's button coins on a frame's bottom gold line: F.tabs before the panel (they hang behind its
-- edge), F.coins after it. list: { { "btn_a", "OK" }, ... }; xs: each coin's centre
function F.tabs(line, xs)
  local tw = U.body("tab")
  for _, cx in ipairs(xs) do U.put("tab", math.floor(cx - (tw - 1) / 2), line, "tab") end
end
function F.coins(line, list, xs)
  local cw, ch = U.body("btn_a")
  for k, b in ipairs(list) do
    local cx = xs[k]
    U.put(b[1], math.floor(cx - (cw - 1) / 2), line - (ch - 1) / 2, "button")
    U.say(7, "cream", b[2], centreX(U.sayW(7, b[2]), cx), line + (ch - 1) / 2 + 3, "hint")
  end
end
-- words on a frame's bottom gold line (PRESS ANY BUTTON): the gold line hidden under them, small cream letters
function F.onEdge(text, line, cx)
  local w = U.sayW(7, text); local x = centreX(w, cx)
  lg.setColor(U.INK); lg.rectangle("fill", x, line, w, 1); lg.setColor(1, 1, 1, 1)
  U.say(7, "cream", text, x, line - 4, "press")
end
-- a row's label (13 px) centred on the row; the selected row gets the paw coin over its left end
local function rowLabel(on, rx, ry, rh, label, style)
  local cy = ry + (rh - 1) / 2
  if on then local _, ch = U.body("coin_paw"); U.put("coin_paw", rx - 6, math.floor(cy - (ch - 1) / 2 + 0.5), "cursor") end
  U.say(13, style or "cream", label, rx + 18, math.floor(cy - (U.sayH(13) - 1) / 2 + 0.5), "label")
end
-- ON / OFF: small letters on a plate (gold on red when on, dim on the dark plate when off), right edge at xr
local function toggle(on, xr, cy)
  local s = on and "ON" or "OFF"
  local w = U.sayW(7, s) + 6
  local x, y = xr - w + 1, math.floor(cy - 6 + 0.5)
  if on then
    lg.setColor(U.SHADE); lg.rectangle("fill", x + 1, y + 1, w, 13); lg.setColor(U.INK); lg.rectangle("fill", x, y, w, 13)
    lg.setColor(U.RED); lg.rectangle("fill", x + 1, y + 1, w - 2, 11); lg.setColor(1, 1, 1, 1)
  else U.plate(x, y, w, 13) end
  U.say(7, on and "gold" or "dim", s, x + 3, y + 2, "toggle")
end

-- the main menu (ui/hud-v8): the title picture as painted (no dim), the logo's shine; the kit's gold panel under the
-- logo with START GAME, LEVEL SELECT, HARD MODE and its ON / OFF, the best run, the A / B coins on its bottom edge
F.MN = { X = 136, W = 180, Y = 98, ROW0 = 109, PITCH = 21, PAD = 11, BEST = 174, H = 104 }
function F.drawMenu(t)
  Title.draw(t, nil, true); Title.drawLogo(t)
  local N = F.MN
  local line = N.Y + N.H - 6
  local cx = N.X + (N.W - 1) / 2
  local xs = { cx - 28.5, cx + 28.5 }
  F.tabs(line, xs)
  U.panel(N.X, N.Y, N.W, N.H)
  local rx, rw = N.X + N.PAD, N.W - 2 * N.PAD
  for i, it in ipairs(F.menu.items) do
    local ry, on = N.ROW0 + (i - 1) * N.PITCH, F.menu.sel == i
    U.row(on, rx, ry, rw)
    rowLabel(on, rx, ry, 19, it)
    if i == 3 then toggle(F.hard, rx + rw - 6, ry + 9) end
  end
  if F.bestRun > 0 then local s = ("BEST RUN %06d"):format(F.bestRun); U.say(7, "cream", s, centreX(U.sayW(7, s), cx), N.BEST, "best") end
  F.coins(line, { { "btn_a", "OK" }, { "btn_b", "BACK" } }, xs)
end

-- the level select (ui/hud-v8): the title under the smooth dim, the gold panel with a LEVEL SELECT ribbon, a row
-- per level (number, name, a status line in the small font: its best and time, NOT PLAYED YET, LOCKED or COMING
-- SOON; its medals, or the padlock), the A / B coins (PLAY / BACK) on the bottom edge
F.SL = { X = 16, W = 288, RIB = 3, PANEL = 13, ROW0 = 29, PITCH = 28, ROW_H = 27, PAD = 14, H = 201 }
function F.drawSelect(t)
  backdrop(t)
  local S = F.SL
  local line = S.PANEL + S.H - 6
  local xs = { 131, 188 }
  F.tabs(line, xs)
  U.panel(S.X, S.PANEL, S.W, S.H)
  local tw = U.sayW(13, "LEVEL SELECT")
  U.ribbon3(159.5, S.RIB, tw + 20)
  U.say(13, "ink", "LEVEL SELECT", centreX(tw), S.RIB + 2, "title")
  if F.hard then U.hardTag8(159.5 + (tw + 20) / 2 + 24, S.RIB + 3) end
  local rx, rw = S.X + S.PAD, S.W - 2 * S.PAD
  local mw = U.body("medal_on")
  local lw, lh = U.body("padlock")
  for i, l in ipairs(F.levels) do
    local ry = S.ROW0 + (i - 1) * S.PITCH
    local on, open = F.pick.sel == i, F.isOpen(i)
    local ok = open and l.exists
    U.row(on, rx, ry, rw, "row", S.ROW_H)
    if on then local _, ch = U.body("coin_paw"); U.put("coin_paw", rx - 6, math.floor(ry + (S.ROW_H - 1) / 2 - (ch - 1) / 2 + 0.5), "cursor") end
    local st = ok and "cream" or "dim"
    U.say(13, ok and "gold" or "dim", tostring(l.number), rx + 18, ry + 2, "label")
    U.say(13, st, l.title, rx + 34, ry + 2, "name")
    local note
    if not l.exists then note = "COMING SOON"
    elseif not open then note = "LOCKED"
    else
      local b, bt = F.levelBest(l.name), F.levelTimeBest(l.name)
      note = b > 0 and ("BEST %06d"):format(b) or "NOT PLAYED YET"
      if bt then note = note .. "  " .. F.clock(bt) end
    end
    U.say(7, st, note, rx + 34, ry + 17, "status")
    if ok and (F.levelBest(l.name) > 0 or F.levelTimeBest(l.name)) then     -- played: its medals
      local m = F.medals(l.name)
      for k, kind in ipairs(F.MEDALS) do U.medal(kind, rx + rw - 6 - 3 * mw - 4 + (k - 1) * (mw + 2), ry + 4, m[kind]) end
    elseif not ok then U.put("padlock", rx + rw - 8 - lw + 1, math.floor(ry + (S.ROW_H - 1) / 2 - (lh - 1) / 2 + 0.5), "lock") end
  end
  F.coins(line, { { "btn_a", "PLAY" }, { "btn_b", "BACK" } }, xs)
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

-- between two levels: what happened at the end of the level just cleared (its L.outro). (ui/hud-v8) the smooth
-- dim, the gold panel with Pepper's head on its top edge, the lines in the small font, the A coin (small) on its
-- bottom edge once A goes on
local function storyW(lines) local w = 200; for _, s in ipairs(lines) do w = math.max(w, U.sayW(7, s) + 40) end; return w + (w % 2) end
function F.drawStory(lines, t, avoid)
  U.dimWarm()
  local w = storyW(lines)
  shifted(F.placeY(centreX(w), w, 70, 62, avoid) - 70, function() F.storyCard(lines, t) end)
end
function F.storyCard(lines, t)
  local w = storyW(lines); local x = centreX(w)
  local y0 = 70 + 9
  local h = 18 + #lines * 11 + 14
  U.panel(x, y0, w, h)
  local hw, hh = U.body("head")
  U.put("head", centreX(hw), y0 - 9, "head")
  for i, s in ipairs(lines) do U.say(7, "cream", s, centreX(U.sayW(7, s)), y0 + 18 + (i - 1) * 11, "text") end
  if t >= F.CARD_WAIT and blink(t) then Talk.glyph("a", x + w - 26, y0 + h - 6, "small") end   -- ready: A goes on
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
-- (ui/hud-v8) like the pause: the smooth dim, a GAME OVER ribbon over the gold panel, two rows (after a moment),
-- the A coin with its OK tab on the bottom edge
F.O = { X = 82, W = 156, PANEL = 10, ROW0 = 27, PITCH = 21, PAD = 15, H = 76, BOX_H = 104 }
function F.drawOver(o, t, avoid)
  U.dimWarm(); shifted(F.placeY(F.O.X, F.O.W, 60, F.O.BOX_H, avoid), function() F.overCard(o, t) end)
end
function F.overCard(o, t)
  local O = F.O
  local line = O.PANEL + O.H - 6
  F.tabs(line, { 159 })
  U.panel(O.X, O.PANEL, O.W, O.H)
  local tw = U.sayW(13, "GAME OVER")
  U.ribbon3(159.5, 0, tw + 20)
  U.say(13, "ink", "GAME OVER", centreX(tw), 2, "title")
  if t >= F.OVER_WAIT then
    for i, it in ipairs(F.overItems) do
      local ry, on = O.ROW0 + (i - 1) * O.PITCH, o.sel == i
      U.row(on, O.X + O.PAD, ry, O.W - 2 * O.PAD); rowLabel(on, O.X + O.PAD, ry, 19, it)
    end
  end
  F.coins(line, { { "btn_a", "OK" } }, { 159 })
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
-- (ui/hud-v8) the title under the smooth dim, the gold panel with the arched GOOD GIRL! ribbon, the last lines and
-- the run's score, THE END, PRESS ANY BUTTON on the bottom edge
function F.drawEnding(e, t)
  backdrop(t)
  local X, W, P, H = 40, 240, 30, 178
  U.panel(X, P, W, H)
  U.ribbon("ribbon_tally", 159.5, 10)
  local bounce = (t < 0.6) and math.floor(math.sin(t * 20) * 2) or 0
  local tw = U.sayW(17, "GOOD GIRL!")
  U.say(17, "ink", "GOOD GIRL!", centreX(tw), 14 + bounce, "title")
  local y = 54
  for _, s in ipairs(e.lines or {}) do U.say(7, "cream", s, centreX(U.sayW(7, s)), y, "text"); y = y + 11 end
  y = math.max(y + 6, 82)
  U.say(7, "cream", "FINAL SCORE", centreX(U.sayW(7, "FINAL SCORE")), y, "text")
  local sc = ("%06d"):format(e.score)
  U.say(13, "gold", sc, centreX(U.sayW(13, sc)), y + 12, "text")
  if e.newBest then if math.floor(t * 3) % 2 == 0 then U.say(7, "gold", "NEW BEST RUN!", centreX(U.sayW(7, "NEW BEST RUN!")), y + 34, "text") end
  else local b = ("BEST RUN %06d"):format(e.best); U.say(7, "cream", b, centreX(U.sayW(7, b)), y + 34, "text") end
  U.say(13, "gold", "THE END", centreX(U.sayW(13, "THE END")), y + 56, "text")
  U.say(7, "cream", "THANKS FOR PLAYING", centreX(U.sayW(7, "THANKS FOR PLAYING")), y + 80, "text")
  if t > F.ENDING_WAIT and blink(t) then F.onEdge("PRESS ANY BUTTON", P + H - 6) end
end
-- the level's intro card (ui/hud-v8): "LEVEL 1" on a ribbon, the level's name in the big gold font, its two lines in
-- the small font, PRESS ANY BUTTON on the bottom edge (blinking, after half a second); where it misses Pepper
local function introW(intro)
  local w = math.max(200, U.sayW(17, intro[2] or "") + 40)
  for i = 3, 4 do if intro[i] then w = math.max(w, U.sayW(7, intro[i]) + 32) end end
  return w + (w % 2)
end
function F.drawIntro(intro, t, avoid)
  U.dimWarm()
  local w = introW(intro); local x = centreX(w)
  shifted(F.placeY(x, w, 66, 84, avoid) - 66, function()
    local y0 = 66
    local line = y0 + 10 + 72 - 6
    U.panel(x, y0 + 10, w, 72)
    local rw = U.sayW(13, intro[1])
    U.ribbon3(159.5, y0, rw + 20)
    U.say(13, "ink", intro[1], centreX(rw), y0 + 2, "title")
    U.say(17, "gold", intro[2], centreX(U.sayW(17, intro[2])), y0 + 25, "name")
    for i = 3, 4 do if intro[i] then U.say(7, "cream", intro[i], centreX(U.sayW(7, intro[i])), y0 + 46 + (i - 3) * 11, "text") end end
    if t > 0.5 and blink(t) then F.onEdge("PRESS ANY BUTTON", line) end
  end)
end
F.ENDING_WAIT = 2                 -- seconds before a key leaves the ending
return F
