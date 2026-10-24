-- FETCH! Pepper's levels in order (levels.lua): 1 River Walk, 2 City Park, 3 Downtown, 4 Rooftops, 5 Soder Hill,
-- 6 Night Harbour. Pepper, the girl and the ball are real art; every level has scenery art (City Park and Downtown over their greybox boxes). 320 x 240, drawn 2x on the RG35XX's
-- 640 x 480 screen. Game logic steps at a fixed 1/60 s, so jumps are the same on every machine.
--
--   d-pad / arrows   run (Pepper runs by default);  Down: crouch and crawl
--   A / Space        jump (hold for higher);  Down + A: drop through a railing or deck
--   B / Shift        walk          X / X key   pick up, drop, give the ball        Y / Z key   bark
--   Start / Enter    pause         Select / G  debug view        Tab  tuning panel (keyboard)
--   L1 / R1 / Q      sniff (hold; Level 5, night.lua)
--   F fullscreen, M music, E visual extras off / on (dust, splash; extras.lua), L the Lion King look off / on
--   Volume buttons (keys volumeup / volumedown / mute): the game's sound level, saved (settings.lua). The pause
--   has a SOUND row too (left / right). Select (pad) toggles the debug view only with --dev or a test flag.
--   Menus: up / down move, A / Space / Enter choose, B / Esc back. In the pause: Start / Enter go on; QUIT asks
--   first (B / Esc only ever go back). On the title screen Esc quits the game.
--
-- The flow (flow.lua): title -> menu (PLAY, LEVELS, OPTIONS) -> each level: intro card, play, tally ->
-- story card -> the next level ... -> the ending -> title. GAME OVER -> TRY AGAIN (the same level) or the menu.
-- Hints and story lines are said in the talk panel (talk.lua); the tally shows times and medals (flow.lua).
-- A level cleared with a golden bone found opens FETCH FRENZY (bonus.lua) between the tally and the story card.
-- love riverwalk --bonus starts that bonus round directly (--level <name> --bonus: that level's round); with
-- --physics or --auto it runs tests_bonus.lua (the checks, or the autopilot that records rec/ for a GIF).
-- love riverwalk --level <name> starts a run at that level (no menus). The test flags (--physics, --auto,
-- --test, --qa) play one level alone, River Walk unless --level names another; --flowtest checks the flow.
-- --auto --playtest <persona>: the playtest lab (playtest.lua, pt_bot.lua, docs/playtest/method.md).
function love.errorhandler(msg) io.stderr:write("ERROR: " .. tostring(msg) .. "\n" .. debug.traceback() .. "\n"); io.stderr:flush(); os.exit(1) end
love.graphics.setDefaultFilter("nearest", "nearest")
local W, H = 320, 240
local DT = 1 / 60
local S = require("sfx")
local U = require("hud")
local I = require("input")
local St = require("stage")
local Pp = require("pepper")
local Ex = require("extras")
local Flow = require("flow")
local Talk = require("talk")
local Se = require("settings")
local Look = require("look")
local Bonus = require("bonus")                                  -- FETCH FRENZY, the golden bone bonus round
local bonus, bonusArg                                           -- the round being played; --bonus was given
local devMode = false                                           -- --dev or a test flag: Select shows the debug view
local levelName, def                                            -- the level being played
local function argLevel(args)
  for i, a in ipairs(args or {}) do if a == "--level" and args[i + 1] then return args[i + 1] end end
end

local canvas = love.graphics.newCanvas(W, H)
local stage, state, t = nil, "intro", 0
local acc = 0
local presses = {}
local debugView, tuning, tuneRow = false, false, 1
local musicOn = true                                           -- from settings.txt (Se.music) once loaded
local fps, frameMs = 60, 0
local tally
local run                                                       -- the run (Flow.newRun): its levels, score, lives
local story, ending                                             -- the story card's lines; the ending's numbers
local over, pz = { sel = 1 }, { sel = 1 }                       -- the GAME OVER card's and the pause's cursors
local clearAt, hit, hl                                          -- the level's clear time; a heart lost in it

local function setLevel(name) levelName = name; def = require("level." .. name) end
-- the current level from the start, alone (the test modes, api.newRun)
local function fresh() Talk.reset(); clearAt, hit, hl = nil, false, nil; over.sel, pz.sel, pz.confirm, pz.controls = 1, 1, nil, nil end
local function freeStage() if stage and stage.ground then stage.ground:release(); stage.ground = nil end end   -- its 3 MB ground canvas
local function newRun() freeStage(); stage = St.new(def); state, t, tally = "intro", 0, nil; fresh() end
-- the run's current level: its intro card; it starts with the run's score and lives
local function startLevel()
  setLevel(run.names[run.k])
  freeStage(); stage = St.new(def, { score = run.score, lives = run.lives, hard = Flow.hard or nil }); state, t, tally = "intro", 0, nil
  fresh(); S.music(musicOn)
end
local function startRun(i) run = Flow.newRun(i); if #run.names > 0 then startLevel() end end
-- FETCH FRENZY: the round of the level just cleared (its number picks the round's throws)
-- (direct: started by --bonus, so it goes back to the title afterwards)
local function startBonus(direct)
  local lv = Flow.levels[Flow.index(levelName) or 0] or {}
  bonus = Bonus.new({ level = lv.number or def.number or 1 }); state, t = "bonus", 0; presses = {}
  bonus.direct = direct
end
local Title = require("title")                                  -- the title screen: PRESS ANY KEY, then the menu
local titleLeaving                                              -- seconds since a key was pressed on the title
local function toTitle() state, t, titleLeaving, run = "title", 0, nil, nil; S.music(musicOn) end
local function leaveTitle()
  if state ~= "title" then return false end
  if t > 0.5 and not titleLeaving then S.play("select"); titleLeaving = 0 end
  return true
end
function love.load(args)
  local lv, test = argLevel(args), nil
  for _, a in ipairs(args or {}) do if a == "--bonus" then bonusArg = true end end
  for _, a in ipairs(args or {}) do
    if a == "--test" or a == "--auto" or a == "--physics" or a == "--qa" or a == "--flowtest" or a == "--lookshots" or a == "--uishots" or a == "--titleshots" or a == "--cardshots" or a == "--screenshots" then test = a end
  end
  Se.save = not test
  for _, a in ipairs(args or {}) do if a == "--dev" then devMode = true end end
  devMode = devMode or test ~= nil
  Se.load(); musicOn = Se.music
  I.startDevice()
  S.load(); S.music(musicOn)
  Title.load()
  if test and test ~= "--flowtest" and test ~= "--titleshots" then                           -- the checks play one level alone, from its intro
    Flow.save = false
    setLevel(lv or "riverwalk")
    if def.title then love.window.setTitle(def.title) end
    newRun()
  else
    love.window.setTitle("FETCH!")
    if test then Flow.prefix = "flowtest_"; Flow.wipe() end
    Flow.load()
    if bonusArg and not test then setLevel(lv or "citypark"); startBonus(true)                 -- --bonus: the round alone
    elseif lv and Flow.index(lv) and not test then startRun(Flow.index(lv)) else state, t = "title", 0 end
  end
  local api = { stage = function() return stage end, setState = function(s) state = s end, getState = function() return state end, newRun = newRun,
    run = function() return run end, tally = function() return tally end, flow = Flow, talk = Talk,
    bonus = function() return bonus end, startBonus = function() startBonus(true) end, startRun = startRun, levelName = function() return levelName end,
    over = function() return over end, pause = function() return pz end,
    setStory = function(l) story = l end, setEnding = function(e) ending = e end, setT = function(v) t = v end }   -- (the screens' frames)
  for _, a in ipairs(args or {}) do
    if (a == "--auto" or a == "--physics") and bonusArg then require("tests_bonus")(a, api)          -- the bonus round's checks
    elseif a == "--test" or a == "--auto" or a == "--physics" then require(levelName == "riverwalk" and "tests" or ("tests_" .. levelName))(a, api) end
    if a == "--noextras" then Ex.enabled = false end
    if a == "--classic" then Look.on = false end                                        -- start with the look as before
    if a == "--uishots" then require("tests_ui")(api) end
    if a == "--titleshots" then require("tests_titleui")(api) end                               -- the title and menus' frames (pilot 2)                                        -- the UI's frames (ui/hud-v8)
    if a == "--cardshots" then require("tests_cards")(api) end                                  -- the level select's pictures (step 3)
    if a == "--screenshots" then require("tests_screens")(api) end                              -- every UI screen's frames (step 3)
    if a == "--lookshots" then require("tests_look")(api) end                                    -- start with the extras off
    if a == "--qa" then require("qa")({ stage = function() return stage end }) end
    if a == "--flowtest" then require("tests_flow")(api) end
    if a == "--pepperlab" then require("pepperlab")() end                              -- Pepper alone in a test room
  end
  for _, a in ipairs(args or {}) do if a == "--playtest" then require("playtest")(api, args) end end   -- the playtest lab (with --auto)
end
function love.joystickadded(j)
  print(("[input] joystick added: %s, gamepad %s, %d buttons, %d hats"):format(j:getName(), tostring(j:isGamepad()), j:getButtonCount(), j:getHatCount()))
  if j:isGamepad() then I.pad = j end
end
-- raw buttons that are not mapped as gamepad buttons (the volume rocker can arrive as one of these)
function love.joystickpressed(j, n)
  if not (j:isGamepad() and I.pad == j) then print(("[input] joystick %s button %d"):format(j:getName(), n)) else print(("[input] raw button %d"):format(n)) end
end

local TUNE = {
  { "run", "run speed", 10, " PX/S" }, { "walk", "walk speed", 5, " PX/S" }, { "crawl", "crawl speed", 5, " PX/S" },
  { "accel", "acceleration", 40, "" }, { "brake", "braking", 40, "" }, { "jumpH", "jump height", 2, " PX" },
  { "minJump", "tap hop", 2, " PX" }, { "fallMul", "fall speed", 0.05, "X" }, { "scramble", "ledge grab", 2, " PX" },
}

local function press(name)
  if not name then return end
  if state == "intro" and t > 0.5 then state = "play"; return end
  if state == "play" then presses[name] = true end
end
-- after the tally: the story card (if the level has one), the next level's intro, or the ending after the last
local function nextLevel()
  if run and run.k < #run.names then
    run.k = run.k + 1
    if def.outro then story = def.outro; state, t = "story", 0 else startLevel() end
  else
    local score = run and run.score or tally.score
    local newBest = Flow.runOver(score)
    ending = { score = score, best = Flow.bestRun, newBest = newBest, lines = def.outro }
    state, t = "ending", 0
  end
end
-- the round is over: its points go into the tally's (and the run's) score, B.LIFE_AT catches give an extra life (at most
-- 9 lives); then the flow goes on as after the tally (the story card, the next level or the ending)
local function finishBonus()
  local r = bonus:result(); r.direct = bonus.direct
  bonus.newBest = Flow.bonusBest(r.points)
  if tally then tally.score = tally.score + r.points; tally.bonusDone = true; tally.bonus = r end
  if run then run.score = run.score + r.points; if r.life then run.lives = math.min(9, run.lives + 1) end end
  bonus = nil
  if r.direct or not tally then toTitle() else nextLevel() end
end
-- a button in the bonus round: the cards take any button, in play the presses go to Pepper
local function bonusKey(name)
  if bonus:press(name) then return end
  if name and bonus.phase ~= "intro" and bonus.phase ~= "result" then presses[name] = true end
end
-- GAME OVER: TRY AGAIN plays the same level again with 3 lives and the score it started with; MENU
local function toMenu() state, t, run = "menu", 0, nil; Flow.menu.sel = 1; S.music(musicOn) end
local function tryAgain() if run then run.lives = 3; startLevel() else newRun() end end
local function overAction(a)
  if t < Flow.OVER_WAIT then return end
  local r = Flow.cursor(over, a, #Flow.overItems)
  if r == 1 then tryAgain() elseif r == 2 then toMenu() end
end
-- the pause: GO ON or QUIT; QUIT asks first. Back (B / Esc) goes one step back: from the question to the pause,
-- from the pause to the game. B is also sneak, so it never quits.
local function resume() state = "play"; pz.sel, pz.confirm, pz.controls = 1, nil, nil; S.music(musicOn) end
local function pauseAction(a)
  if pz.controls then                                             -- the controls page: B (or A) goes back to the pause
    if a == "back" or a == "ok" then pz.controls = nil; S.play("tick") end
    return
  end
  if pz.confirm then
    if a == "back" then pz.confirm = nil; S.play("tick"); return end
    local c = pz.cm or {}; c.sel = pz.confirm                      -- (pz.cm: the question's cursor, eased by the drawing)
    local r = Flow.cursor(c, a, #Flow.confirmItems); pz.confirm = c.sel; pz.cm = c
    if r == 1 then pz.confirm = nil elseif r == 2 then S.play("tick"); toMenu() end
    return
  end
  if a == "back" then resume(); return end
  if pz.sel == Flow.PAUSE_SOUND and (a == "left" or a == "right") then
    if Se.step(a == "right" and 1 or -1) then S.play("tick") end; return
  end
  local r = Flow.cursor(pz, a, #Flow.pauseItems)
  if r == 1 then resume()
  elseif r == Flow.PAUSE_SOUND then if Se.volume >= Se.MAX then Se.step(-Se.MAX) else Se.step(1) end; S.play("tick")
  elseif r == Flow.PAUSE_CONTROLS then pz.controls = true
  elseif r == Flow.PAUSE_QUIT then pz.confirm = 1 end
end
-- the story card: only A goes on, after Flow.CARD_WAIT seconds (time to read it aloud)
local function storyA() if state == "story" and t >= Flow.CARD_WAIT then S.play("select"); startLevel() end end
local function anyKey()
  if state == "clear" and tally and not tally.done then Flow.tallySkip(tally); return end   -- (ui step 3) skip the show
  if state == "clear" and tally and tally.done then
    S.play("select")
    if not tally.bonusDone and Flow.bonusOpen(stage) then startBonus() else nextLevel() end    -- a golden bone: the bonus
  elseif state == "ending" and t > Flow.ENDING_WAIT then S.play("select"); toTitle() end
end
-- the main menu and the level select
local MENUS = { menu = true, select = true, options = true, controls = true }
local function menuAction(a)
  if not a then return end
  if state == "menu" then
    local r = Flow.menuInput(a)
    if r == "play" then startRun(Flow.furthest())                  -- PLAY: on from the furthest open level
    elseif r == "select" then state = "select"; Flow.pick.sel = 1
    elseif r == "options" then state = "options"; Flow.opts.sel, Flow.opts.from = 1, 1
    elseif r == "back" then toTitle(); t = 0.5 end                 -- back to PRESS START (no fade-in)
  elseif state == "options" then
    local r = Flow.optionsInput(a)
    if r == "back" then state = "menu" elseif r == "controls" then state = "controls" end
  elseif state == "controls" then
    if Flow.controlsInput(a) == "back" then state = "options" end
  else
    local r, i = Flow.selectInput(a)
    if r == "play" then startRun(i) elseif r == "back" then state = "menu" end
  end
end
-- the handheld's volume buttons: the game's own sound level (never "any key", never a game button)
local function volumeKey(k)
  if k == "volumeup" or k == "volumedown" then Se.step(k == "volumeup" and 1 or -1); return true end
  if k == "mute" or k == "audiomute" then Se.toggleMute(); return true end
  return false
end
-- every press is written to stdout (the handheld's launcher keeps it in ports/fetch/log.txt), so a console test
-- shows what the firmware really sends for the volume buttons, the d-pad and the face buttons
local function logInput(kind, what) print(("[input] %s %s (%s)"):format(kind, tostring(what), state)); io.stdout:flush() end
function love.keypressed(k, sc)
  logInput("key", k .. (sc and sc ~= k and (" sc=" .. sc) or ""))
  if volumeKey(k) then return end
  I.setLast("key")
  if k == "f" then love.window.setFullscreen(not love.window.getFullscreen()); return end
  if k == "m" then musicOn = not musicOn; Se.setMusic(musicOn); S.music(musicOn and state ~= "pause"); return end
  if k == "g" then debugView = not debugView; return end
  if k == "tab" then tuning = not tuning; return end
  if k == "e" then Ex.toggle(); return end
  if k == "l" then Look.toggle(); return end                     -- the Lion King look off / on (look.lua)
  if state == "title" and k == "escape" then love.event.quit(); return end
  if leaveTitle() then return end
  if MENUS[state] then menuAction(Flow.action(k)); return end
  if state == "bonus" then bonusKey(I.keyName(k)); return end
  if tuning and state == "play" then
    local n = tonumber(k) or tonumber((k:gsub("kp", "")))
    if n and TUNE[n] then tuneRow = n; return end
    local d = (k == "-" or k == "kp-") and -1 or ((k == "=" or k == "+" or k == "kp+") and 1 or 0)
    if d ~= 0 then local r = TUNE[tuneRow]; Pp.P[r[1]] = math.max(0, math.floor((Pp.P[r[1]] + d * r[3]) * 100 + 0.5) / 100); Pp.saveTuning(); return end
  end
  if state == "pause" then
    if k == "return" or k == "p" then resume() else pauseAction(Flow.action(k)) end
    return
  end
  if state == "over" then overAction(Flow.action(k)); return end
  if state == "story" then if k == "space" or k == "return" then storyA() end; return end
  if (k == "return" or k == "p" or k == "escape") and state == "play" then state = "pause"; S.play("tick"); S.music(false); return end
  if state == "intro" and t > 0.5 then state = "play"; return end
  press(I.keyName(k)); anyKey()
end
function love.gamepadpressed(j, b)
  logInput("pad", b)
  I.pad = j; I.setLast("pad")
  if b == "leftshoulder" or b == "rightshoulder" then return end    -- L1 / R1: sniff (held; night.lua reads them)
  if leaveTitle() then return end
  if b == "back" then if devMode then debugView = not debugView end; return end
  if MENUS[state] then menuAction(Flow.action(nil, b)); return end
  if state == "bonus" then bonusKey(I.padName(b)); return end
  if b == "start" and (state == "play" or state == "pause") then
    if state == "play" then state = "pause"; S.music(false) else resume() end
    return
  end
  if state == "pause" then pauseAction(Flow.action(nil, b ~= "start" and b or nil)); return end
  if state == "over" then overAction(Flow.action(nil, b ~= "start" and b or nil)); return end
  if state == "story" then if b == "a" or b == "start" then storyA() end; return end
  if state == "intro" and t > 0.5 then state = "play"; return end
  press(I.padName(b)); anyKey()
end
-- the left stick moves the menu cursor too (one step each time it is pushed past half way)
local stickY = 0
local stickX = 0
function love.gamepadaxis(j, axis, v)
  if axis == "leftx" then                                       -- left / right: the pause's SOUND row
    local d = v > 0.6 and 1 or (v < -0.6 and -1 or (math.abs(v) < 0.3 and 0 or stickX))
    if d ~= stickX then stickX = d; if d ~= 0 then
      I.setLast("pad")
      if state == "pause" then pauseAction(d < 0 and "left" or "right") elseif state == "options" then menuAction(d < 0 and "left" or "right") end
    end end
    return
  end
  if axis ~= "lefty" then return end
  local d = v > 0.6 and 1 or (v < -0.6 and -1 or (math.abs(v) < 0.3 and 0 or stickY))
  if d ~= stickY then stickY = d; if d ~= 0 then
    local a = d < 0 and "up" or "down"
    I.setLast("pad")
    if MENUS[state] then menuAction(a) elseif state == "pause" then pauseAction(a) elseif state == "over" then overAction(a) end
  end end
end

function love.update(dt)
  dt = math.min(dt, 0.1); t = t + dt
  if titleLeaving then
    titleLeaving = titleLeaving + dt
    if titleLeaving >= Title.LEAVE then titleLeaving = nil; state = "menu"; Flow.menu.sel = 1 end
  end
  fps = love.timer.getFPS()
  local t0 = love.timer.getTime()
  if state == "play" then
    acc = acc + dt
    local steps = 0
    while acc >= DT - 1e-9 and steps < 4 do
      stage:update(DT, presses); Talk.watch(stage, presses, DT); presses = {}; acc = acc - DT; steps = steps + 1
      local now = stage.lives * 10 + stage.hearts                 -- a heart (or a life) lost: no NO HIT medal
      if hl and now < hl then hit = true end; hl = now
      if (stage.ballKnocks or 0) > 0 then hit = true end         -- (r6/engine) a hit that knocked the ball out: no NO HIT medal either
      if stage.clearT and not clearAt then clearAt = stage.t end                -- the ball given: the clear time
      if stage.events.over then state, t = "over", 0; over.sel = 1; S.music(false); S.play("over"); if run then Flow.runOver(stage.score) end; break end
      if stage.events.clear then
        state, t = "clear", 0; S.music(false); S.play("clear")
        -- the tally: bones, the level's bonus (if any) and the time bonus make the level's points; the run's
        -- score goes on from where the level started
        local st = stage:stats(); local left = math.max(0, math.floor(st.time))
        tally = { t = 0, shown = 0, lines = { { "BONES", st.bones .. "/" .. st.total } } }
        if st.bonus then tally.lines[#tally.lines + 1] = { st.bonus[1], tostring(st.bonus[2]) } end
        tally.lines[#tally.lines + 1] = { "TIME BONUS", tostring(left * 10) }
        tally.points = st.levelScore + left * 10
        tally.from = st.score - st.levelScore
        tally.score = st.score + left * 10
        tally.newBest = Flow.levelPoints(levelName, tally.points)
        -- the clear time, the best time and the medals (NO HIT, ALL BONES, PAR TIME); SECRETS if the level has them
        local lv = Flow.levels[Flow.index(levelName) or 0] or {}
        tally.time = math.floor((clearAt or stage.t) * 100 + 0.5) / 100
        tally.par = lv.par or 60
        tally.best, tally.newBestTime = Flow.levelTime(levelName, tally.time)
        tally.medals = { nohit = not hit, bones = st.bones >= st.total, par = tally.time <= tally.par }
        Flow.addMedals(levelName, tally.medals)
        tally.hard = stage.hard
        if st.secrets and st.secretsTotal then table.insert(tally.lines, #tally.lines, { "SECRETS", st.secrets .. "/" .. st.secretsTotal }) end
        Flow.cleared(levelName)
        if run then run.score, run.lives = tally.score, st.lives end
        break
      end
    end
    if steps == 4 then acc = 0 end
  elseif state == "bonus" then                                     -- FETCH FRENZY: fixed steps, as the levels
    acc = acc + dt
    local steps = 0
    while acc >= DT - 1e-9 and steps < 4 do
      bonus:update(DT, presses); presses = {}; acc = acc - DT; steps = steps + 1
      if bonus.phase == "done" then finishBonus(); break end
    end
    if steps == 4 then acc = 0 end
  elseif state == "clear" then
    Flow.tallyStep(tally, dt)                                      -- (ui step 3) the tally's show: counts, ticks, medals, stamp
  end
  if state == "play" then Talk.update(dt, stage) end
  frameMs = (love.timer.getTime() - t0) * 1000
end

local function drawTuning()                                       -- (dev, Tab) in the v8 small font (ui step 3)
  if not tuning then return end
  local x, y, w, h = 160, 30, 156, 16 + #TUNE * 10
  love.graphics.setColor(40 / 255, 20 / 255, 12 / 255, 0.92); love.graphics.rectangle("fill", x, y, w, h); love.graphics.setColor(1, 1, 1, 1)
  for i, r in ipairs(TUNE) do
    local style = (i == tuneRow) and "gold" or "cream"
    U.say(7, style, i .. " " .. r[2]:upper(), x + 4, y + 3 + (i - 1) * 10)
    local v = tostring(Pp.P[r[1]]) .. r[4]
    U.say(7, style, v, x + w - 4 - U.sayW(7, v), y + 3 + (i - 1) * 10)
  end
  U.say(7, "dim", "- + CHANGE", x + 4, y + h - 11)
end

function love.draw()
  love.graphics.setCanvas(canvas); love.graphics.clear(0, 0, 0)
  local screen = (state == "title" and function() Title.draw(t, titleLeaving) end)
    or (state == "menu" and function() Flow.drawMenu(t) end) or (state == "select" and function() Flow.drawSelect(t) end)
    or (state == "options" and function() Flow.drawOptions(t) end) or (state == "controls" and function() Flow.drawControls(t) end)
    or (state == "ending" and function() Flow.drawEnding(ending, t) end)
    or (state == "bonus" and function() bonus:draw() end)
  if screen then                                                  -- the screens drawn without a level behind them
    screen()
    if Se.showing() then U.volumeToast(Se.volume, Se.MAX, U.TOAST_MENU) end
    love.graphics.setCanvas()
    local ww, wh = love.graphics.getDimensions()
    local s = math.max(1, math.floor(math.min(ww / W, wh / H)))
    love.graphics.clear(0, 0, 0)
    love.graphics.draw(canvas, math.floor((ww - W * s) / 2), math.floor((wh - H * s) / 2), 0, s, s)
    return
  end
  stage:draw(debugView)
  local st = stage:stats()
  -- the HUD (hud.lua): while playing, a group Pepper is up under steps aside (ui/hud-v8: per group, not the whole HUD).
  -- Only while playing (ui/panel-hud, 24 Oct): under a centred card (intro, pause, GAME OVER, tally, story) the HUD
  -- row is not drawn at all, so the card's ribbon and frame never cut through its numbers; the pause shows the bones
  -- found and the tally the level's points in the card itself.
  if state == "play" then
    U.status({ lives = st.lives, hearts = st.hearts, bones = st.bones, total = st.total, time = st.time, score = st.score, hard = stage.hard },
      { Talk.pepperRect(stage) })
  end
  if state == "intro" then
    Flow.drawIntro(def, t, { Talk.pepperRect(stage) })            -- (ui step 3) the gold card, the story, A GO
  elseif state == "play" then
    Talk.draw(stage)
    drawTuning()
  elseif state == "pause" then
    Flow.drawPause(pz, def, { Talk.pepperRect(stage) }, st)
  elseif state == "over" then
    Flow.drawOver(over, t, { Talk.pepperRect(stage) })
  elseif state == "clear" then
    Flow.drawTally(tally, { Talk.pepperRect(stage) })
  elseif state == "story" then
    Flow.drawStory(story, t, { Talk.pepperRect(stage) })
  end
  if state ~= "play" and not (state == "pause" and pz.controls) then   -- the cards dim the level, never Pepper (the
    -- controls page from the pause covers the screen)
    love.graphics.push(); love.graphics.translate(0, -math.floor((stage.camY or 0) + 0.5))   -- (tall levels: camera y)
    love.graphics.setColor(1, 1, 1, 1); stage.pepper:draw(math.floor(stage.cam + 0.5))
    love.graphics.pop()
  end
  if Se.showing() then U.volumeToast(Se.volume, Se.MAX, state == "play" and U.TOAST_PLAY or U.TOAST_MENU) end
  if debugView then
    U.say(7, "gold", ("%d FPS  %.1f MS"):format(fps, frameMs), 4, 228)
    local p = stage.pepper
    U.say(7, "gold", ("X %d Y %d %s"):format(p.x, p.y, p.onGround and "GROUND" or "AIR"), 160, 228)
  end
  love.graphics.setCanvas()
  local ww, wh = love.graphics.getDimensions()
  local s = math.max(1, math.floor(math.min(ww / W, wh / H)))
  love.graphics.clear(0, 0, 0)
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.draw(canvas, math.floor((ww - W * s) / 2), math.floor((wh - H * s) / 2), 0, s, s)
end
