-- The game around the levels: the run, the menus, the story cards, the ending and what is saved.
--   The run:      the levels of levels.lua in order, from the first one (START GAME) or the one picked in the level
--                 select, to the end. One score for the whole run, lives carry from level to level, hearts refill
--                 and the timer starts again in every level. A level whose file is missing is skipped.
--   Main menu:    START GAME, LEVEL SELECT, over the title picture (dimmed, the logo stays bright).
--   Level select: every level of levels.lua. Level 1 is always open; a level opens when the one before it is
--                 cleared. Locked ones are dimmed with a padlock, a missing file says COMING SOON.
--   Saved:        progress.txt (the open levels, one name per line), best_run.txt (the best run score) and the
--                 best points per level (best.txt for River Walk, best_<name>.txt for the others).
local U = require("hud")
local Title = require("title")
local S = require("sfx")
local LEVELS = require("levels")
local lg = love.graphics
local F = { prefix = "", save = true, unlocked = {}, bestRun = 0 }

-- the levels in play order; exists: level/<name>.lua is there
function F.list(src)
  local out = {}
  for i, l in ipairs(src or LEVELS) do
    out[i] = { name = l.name, number = l.number or i, title = l.title or l.name:upper(),
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
  F.bestRun = tonumber(read("best_run.txt") or "") or 0
end
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
local KEYS = { up = "up", w = "up", down = "down", s = "down", space = "ok", ["return"] = "ok", kpenter = "ok", x = "ok",
  escape = "back", backspace = "back" }
local PADS = { dpup = "up", dpdown = "down", a = "ok", start = "ok", b = "back" }
function F.action(key, pad) if key then return KEYS[key] end; return PADS[pad] end

-- the main menu and the level select: the cursor moves; returns what was chosen
F.menu = { sel = 1, items = { "START GAME", "LEVEL SELECT" } }
F.pick = { sel = 1 }
function F.menuInput(a)
  local m = F.menu
  if a == "up" or a == "down" then m.sel = (m.sel + (a == "up" and -2 or 0)) % #m.items + 1; S.play("tick")
  elseif a == "ok" then S.play("select"); return m.sel == 1 and "start" or "select"
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

-- the menus' background: the title picture, animated, dimmed
local function backdrop(t) Title.draw(t, nil, true); U.dim() end
local function blink(t) return (t % 1.1) < 0.75 end

function F.drawMenu(t)
  backdrop(t)
  Title.drawLogo(t)
  local cx = 213                                                   -- under the logo and the PRESS ANY KEY box
  U.box(cx - 80, 102, 160, 58)
  for i, it in ipairs(F.menu.items) do
    local y = 110 + (i - 1) * 22
    local on = F.menu.sel == i
    if on then lg.setColor(U.EDGE); lg.rectangle("fill", cx - 76, y - 3, 152, 19); lg.setColor(1, 1, 1, 1) end
    U.center(it, cx, y + 1, 2, on and U.GOLD or U.WHITE)
  end
  if F.bestRun > 0 then U.center(("BEST RUN %06d"):format(F.bestRun), cx, 172, 1) end
  Title.drawBanner("A OK    B BACK")
end

function F.drawSelect(t)
  backdrop(t)
  U.box(40, 14, 240, 200)
  U.center("LEVEL SELECT", 160, 24, 2, U.GOLD)
  for i, l in ipairs(F.levels) do
    local y = 52 + (i - 1) * 46
    local on, open = F.pick.sel == i, F.isOpen(i)
    local ok = open and l.exists
    if on then lg.setColor(U.EDGE); lg.rectangle("fill", 46, y - 5, 228, 40); lg.setColor(1, 1, 1, 1) end
    local col = ok and (on and U.GOLD or U.WHITE) or U.RIM
    U.center(tostring(l.number), 62, y + 4, 2, col)
    U.center(l.title, 164, y, 2, col)
    local note
    if not l.exists then note = "COMING SOON"
    elseif not open then note = "LOCKED"
    else local b = F.levelBest(l.name); note = b > 0 and ("BEST %06d"):format(b) or "NOT PLAYED YET" end
    U.center(note, 164, y + 20, 1, ok and U.WHITE or U.RIM)
    if not ok then U.lock(253, y + 4, U.RIM, 2) end
  end
  U.center("A PLAY    B BACK", 160, 196, 1, U.RIM)
end

-- between two levels: what happened at the end of the level just cleared (its L.outro)
function F.drawStory(lines, t)
  U.dim()
  U.box(36, 76, 248, 70)
  U.dog(150, 86, U.GOLD, 2)
  for i, s in ipairs(lines) do U.center(s, 160, 108 + (i - 1) * 12, 1) end
  if t > 0.5 and blink(t) then U.prompt("PRESS ANY BUTTON") end
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
