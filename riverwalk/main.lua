-- FETCH! Pepper's levels in order (levels.lua): 1 City Park, 2 Downtown, 3 River Walk. Pepper, the girl and the
-- ball are real art; River Walk has scenery art, the others are greybox. 320 x 240, drawn 2x on the RG35XX's
-- 640 x 480 screen. Game logic steps at a fixed 1/60 s, so jumps are the same on every machine.
--
--   d-pad / arrows   run (Pepper runs by default);  Down: crouch and crawl
--   A / Space        jump (hold for higher);  Down + A: drop through a railing or deck
--   B / Shift        walk          X / X key   pick up, drop, give the ball        Y / Z key   bark
--   Start / Enter    pause         Select / G  debug view        Tab  tuning panel (keyboard)
--   F fullscreen, M music, E visual extras off / on (dust, splash; extras.lua)
--   Volume buttons (keys volumeup / volumedown / mute): the game's sound level, saved (settings.lua). The pause
--   has a SOUND row too (left / right). Select (pad) toggles the debug view only with --dev or a test flag.
--   Menus: up / down move, A / Space / Enter choose, B / Esc back. In the pause: Start / Enter go on; QUIT asks
--   first (B / Esc only ever go back). On the title screen Esc quits the game.
--
-- The flow (flow.lua): title -> menu (START GAME or LEVEL SELECT) -> each level: intro card, play, tally ->
-- story card -> the next level ... -> the ending -> title. GAME OVER -> TRY AGAIN (the same level) or the menu.
-- Hints and story lines are said in the talk panel (talk.lua); the tally shows times and medals (flow.lua).
-- love riverwalk --level <name> starts a run at that level (no menus). The test flags (--physics, --auto,
-- --test, --qa) play one level alone, River Walk unless --level names another; --flowtest checks the flow.
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
local function fresh() Talk.reset(); clearAt, hit, hl = nil, false, nil; over.sel, pz.sel, pz.confirm = 1, 1, nil end
local function newRun() stage = St.new(def); state, t, tally = "intro", 0, nil; fresh() end
-- the run's current level: its intro card; it starts with the run's score and lives
local function startLevel()
  setLevel(run.names[run.k])
  stage = St.new(def, { score = run.score, lives = run.lives, hard = Flow.hard or nil }); state, t, tally = "intro", 0, nil
  fresh(); S.music(musicOn)
end
local function startRun(i) run = Flow.newRun(i); if #run.names > 0 then startLevel() end end
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
  for _, a in ipairs(args or {}) do
    if a == "--test" or a == "--auto" or a == "--physics" or a == "--qa" or a == "--flowtest" then test = a end
  end
  Se.save = not test
  for _, a in ipairs(args or {}) do if a == "--dev" then devMode = true end end
  devMode = devMode or test ~= nil
  Se.load(); musicOn = Se.music
  S.load(); S.music(musicOn)
  Title.load()
  if test and test ~= "--flowtest" then                           -- the checks play one level alone, from its intro
    Flow.save = false
    setLevel(lv or "riverwalk")
    if def.title then love.window.setTitle(def.title) end
    newRun()
  else
    love.window.setTitle("FETCH!")
    if test then Flow.prefix = "flowtest_"; Flow.wipe() end
    Flow.load()
    if lv and Flow.index(lv) and not test then startRun(Flow.index(lv)) else state, t = "title", 0 end
  end
  local api = { stage = function() return stage end, setState = function(s) state = s end, getState = function() return state end, newRun = newRun,
    run = function() return run end, tally = function() return tally end, flow = Flow, talk = Talk,
    over = function() return over end, pause = function() return pz end }
  for _, a in ipairs(args or {}) do
    if a == "--test" or a == "--auto" or a == "--physics" then require(levelName == "riverwalk" and "tests" or ("tests_" .. levelName))(a, api) end
    if a == "--noextras" then Ex.enabled = false end                                    -- start with the extras off
    if a == "--qa" then require("qa")({ stage = function() return stage end }) end
    if a == "--flowtest" then require("tests_flow")(api) end
    if a == "--pepperlab" then require("pepperlab")() end                              -- Pepper alone in a test room
  end
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
local function resume() state = "play"; pz.sel, pz.confirm = 1, nil; S.music(musicOn) end
local function pauseAction(a)
  if pz.confirm then
    if a == "back" then pz.confirm = nil; S.play("tick"); return end
    local c = { sel = pz.confirm }
    local r = Flow.cursor(c, a, #Flow.confirmItems); pz.confirm = c.sel
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
  elseif r == Flow.PAUSE_QUIT then pz.confirm = 1 end
end
-- the story card: only A goes on, after Flow.CARD_WAIT seconds (time to read it aloud)
local function storyA() if state == "story" and t >= Flow.CARD_WAIT then S.play("select"); startLevel() end end
local function anyKey()
  if state == "clear" and tally and tally.done then S.play("select"); nextLevel()
  elseif state == "ending" and t > Flow.ENDING_WAIT then S.play("select"); toTitle() end
end
-- the main menu and the level select
local function menuAction(a)
  if not a then return end
  if state == "menu" then
    local r = Flow.menuInput(a)
    if r == "start" then startRun(1)
    elseif r == "select" then state = "select"; Flow.pick.sel = 1
    elseif r == "back" then toTitle(); t = 0.5 end                 -- back to PRESS ANY KEY (no fade-in)
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
  if k == "f" then love.window.setFullscreen(not love.window.getFullscreen()); return end
  if k == "m" then musicOn = not musicOn; Se.setMusic(musicOn); S.music(musicOn and state ~= "pause"); return end
  if k == "g" then debugView = not debugView; return end
  if k == "tab" then tuning = not tuning; return end
  if k == "e" then Ex.toggle(); return end
  if state == "title" and k == "escape" then love.event.quit(); return end
  if leaveTitle() then return end
  if state == "menu" or state == "select" then menuAction(Flow.action(k)); return end
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
  if state == "story" then if k == "space" then storyA() end; return end
  if (k == "return" or k == "p" or k == "escape") and state == "play" then state = "pause"; S.play("tick"); S.music(false); return end
  if state == "intro" and t > 0.5 then state = "play"; return end
  press(I.keyName(k)); anyKey()
end
function love.gamepadpressed(j, b)
  logInput("pad", b)
  I.pad = j
  if leaveTitle() then return end
  if b == "back" then if devMode then debugView = not debugView end; return end
  if state == "menu" or state == "select" then menuAction(Flow.action(nil, b)); return end
  if b == "start" and (state == "play" or state == "pause") then
    if state == "play" then state = "pause"; S.music(false) else resume() end
    return
  end
  if state == "pause" then pauseAction(Flow.action(nil, b ~= "start" and b or nil)); return end
  if state == "over" then overAction(Flow.action(nil, b ~= "start" and b or nil)); return end
  if state == "story" then if b == "a" then storyA() end; return end
  if state == "intro" and t > 0.5 then state = "play"; return end
  press(I.padName(b)); anyKey()
end
-- the left stick moves the menu cursor too (one step each time it is pushed past half way)
local stickY = 0
local stickX = 0
function love.gamepadaxis(j, axis, v)
  if axis == "leftx" then                                       -- left / right: the pause's SOUND row
    local d = v > 0.6 and 1 or (v < -0.6 and -1 or (math.abs(v) < 0.3 and 0 or stickX))
    if d ~= stickX then stickX = d; if d ~= 0 and state == "pause" then pauseAction(d < 0 and "left" or "right") end end
    return
  end
  if axis ~= "lefty" then return end
  local d = v > 0.6 and 1 or (v < -0.6 and -1 or (math.abs(v) < 0.3 and 0 or stickY))
  if d ~= stickY then stickY = d; if d ~= 0 then
    local a = d < 0 and "up" or "down"
    if state == "menu" or state == "select" then menuAction(a) elseif state == "pause" then pauseAction(a) elseif state == "over" then overAction(a) end
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
  elseif state == "clear" then
    tally.t = tally.t + dt
    if tally.t > 1.4 and tally.shown < tally.points then              -- the points count up into the score
      local before = tally.shown
      tally.shown = math.min(tally.points, tally.shown + math.max(10, math.floor(tally.points * dt * 0.9)))
      if math.floor(before / 500) ~= math.floor(tally.shown / 500) then S.play("tick") end
    end
    if tally.shown >= tally.points and tally.t > 1.8 then tally.done = true end
  end
  if state == "play" then Talk.update(dt, stage) end
  frameMs = (love.timer.getTime() - t0) * 1000
end

local function drawTuning()
  if not tuning then return end
  local x, y, w, h = 168, 22, 148, 14 + #TUNE * 10
  love.graphics.setColor(0.08, 0.12, 0.22, 0.9); love.graphics.rectangle("fill", x, y, w, h)
  for i, r in ipairs(TUNE) do
    local col = (i == tuneRow) and { 252/255, 214/255, 60/255 } or U.WHITE
    U.text(i .. " " .. r[2]:upper(), x + 4, y + 3 + (i - 1) * 10, col)
    local v = tostring(Pp.P[r[1]]) .. r[4]
    U.text(v, x + w - 4 - 6 * #v, y + 3 + (i - 1) * 10, col)
  end
  U.text("- + CHANGE", x + 4, y + h - 10, U.RIM)
end

function love.draw()
  love.graphics.setCanvas(canvas); love.graphics.clear(0, 0, 0)
  local screen = (state == "title" and function() Title.draw(t, titleLeaving) end)
    or (state == "menu" and function() Flow.drawMenu(t) end) or (state == "select" and function() Flow.drawSelect(t) end)
    or (state == "ending" and function() Flow.drawEnding(ending, t) end)
  if screen then                                                  -- the screens drawn without a level behind them
    screen()
    if Se.showing() then U.volumeToast(Se.volume, Se.MAX) end
    love.graphics.setCanvas()
    local ww, wh = love.graphics.getDimensions()
    local s = math.max(1, math.floor(math.min(ww / W, wh / H)))
    love.graphics.clear(0, 0, 0)
    love.graphics.draw(canvas, math.floor((ww - W * s) / 2), math.floor((wh - H * s) / 2), 0, s, s)
    return
  end
  stage:draw(debugView)
  local st = stage:stats()
  U.status({ lives = st.lives, hearts = st.hearts, bones = st.bones, total = st.total, time = st.time, score = st.score, hard = stage.hard })
  if state == "intro" then
    U.dim()
    love.graphics.push(); love.graphics.translate(0, Flow.placeY(60, 200, 70, 76, { Talk.pepperRect(stage) }) - 70)
    U.box(60, 70, 200, 76)
    U.center(def.intro[1], 160, 78, 2, U.GOLD); U.center(def.intro[2], 160, 96, 2, U.GOLD)
    U.center(def.intro[3], 160, 118, 1); U.center(def.intro[4], 160, 130, 1)
    love.graphics.pop()
    if t > 0.5 and (t % 1.1) < 0.75 then U.prompt("PRESS ANY BUTTON") end
  elseif state == "play" then
    Talk.draw(stage)
    drawTuning()
  elseif state == "pause" then
    Flow.drawPause(pz, def, { Talk.pepperRect(stage) })
  elseif state == "over" then
    Flow.drawOver(over, t, { Talk.pepperRect(stage) })
  elseif state == "clear" then
    Flow.drawTally(tally, { Talk.pepperRect(stage) })
  elseif state == "story" then
    Flow.drawStory(story, t, { Talk.pepperRect(stage) })
  end
  if state ~= "play" then                                         -- the cards dim the level, never Pepper
    love.graphics.setColor(1, 1, 1, 1); stage.pepper:draw(math.floor(stage.cam + 0.5))
  end
  if Se.showing() then U.volumeToast(Se.volume, Se.MAX) end
  if debugView then
    U.text(("%d FPS  %.1f MS"):format(fps, frameMs), 4, 228, { 1, 1, 0.4 })
    local p = stage.pepper
    U.text(("X %d Y %d %s"):format(p.x, p.y, p.onGround and "GROUND" or "AIR"), 160, 228, { 1, 1, 0.4 })
  end
  love.graphics.setCanvas()
  local ww, wh = love.graphics.getDimensions()
  local s = math.max(1, math.floor(math.min(ww / W, wh / H)))
  love.graphics.clear(0, 0, 0)
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.draw(canvas, math.floor((ww - W * s) / 2), math.floor((wh - H * s) / 2), 0, s, s)
end
