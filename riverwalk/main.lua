-- Pepper: Level 3, River Walk (greybox). Pepper, the girl and the ball are real art; everything else is
-- wireframe boxes, one misty grey-blue per layer. 320 x 240, drawn 2x on the RG35XX's 640 x 480 screen.
-- Game logic steps at a fixed 1/60 s, so jumps are the same on every machine.
--
--   d-pad / arrows   run (Pepper runs by default);  Down: crouch and crawl
--   A / Space        jump (hold for higher);  Down + A: drop through a railing or deck
--   B / Shift        walk          X / X key   pick up, drop, give the ball        Y / Z key   bark
--   Start / Enter    pause         Select / G  debug view        Tab  tuning panel (keyboard)
--   F fullscreen, M music, Esc quits from the pause menu
function love.errorhandler(msg) io.stderr:write("ERROR: " .. tostring(msg) .. "\n" .. debug.traceback() .. "\n"); io.stderr:flush(); os.exit(1) end
love.graphics.setDefaultFilter("nearest", "nearest")
local W, H = 320, 240
local DT = 1 / 60
local S = require("sfx")
local U = require("hud")
local I = require("input")
local St = require("stage")
local Pp = require("pepper")
local def = require("level.riverwalk")

local canvas = love.graphics.newCanvas(W, H)
local stage, state, t = nil, "intro", 0
local acc = 0
local presses = {}
local debugView, tuning, tuneRow = false, false, 1
local musicOn = true
local fps, frameMs = 60, 0
local tally
local best = 0
local checker
do
  local d = love.image.newImageData(W, H)
  for y = 0, H - 1 do for x = (y % 2), W - 1, 2 do d:setPixel(x, y, U.SHADE[1], U.SHADE[2], U.SHADE[3], 1) end end
  checker = love.graphics.newImage(d)
end

local function newRun() stage = St.new(def); state, t, tally = "intro", 0, nil end
function love.load(args)
  S.load(); S.music(musicOn)
  local ok, s = pcall(love.filesystem.read, "best.txt"); best = ok and tonumber(s or "") or 0
  newRun()
  for _, a in ipairs(args or {}) do
    if a == "--test" or a == "--auto" or a == "--physics" then require("tests")(a, { stage = function() return stage end, setState = function(s) state = s end, getState = function() return state end, newRun = newRun }) end
  end
end
function love.joystickadded(j) if j:isGamepad() then I.pad = j end end

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
local function anyKey()
  if (state == "over" and t > 1.2) or (state == "clear" and tally and tally.done) then S.play("select"); newRun() end
end
function love.keypressed(k)
  if k == "f" then love.window.setFullscreen(not love.window.getFullscreen()); return end
  if k == "m" then musicOn = not musicOn; S.music(musicOn); return end
  if k == "g" then debugView = not debugView; return end
  if k == "tab" then tuning = not tuning; return end
  if tuning and state == "play" then
    local n = tonumber(k) or tonumber((k:gsub("kp", "")))
    if n and TUNE[n] then tuneRow = n; return end
    local d = (k == "-" or k == "kp-") and -1 or ((k == "=" or k == "+" or k == "kp+") and 1 or 0)
    if d ~= 0 then local r = TUNE[tuneRow]; Pp.P[r[1]] = math.max(0, math.floor((Pp.P[r[1]] + d * r[3]) * 100 + 0.5) / 100); Pp.saveTuning(); return end
  end
  if state == "pause" then
    if k == "return" or k == "p" then state = "play"; S.music(musicOn) elseif k == "escape" then love.event.quit() end
    return
  end
  if (k == "return" or k == "p" or k == "escape") and state == "play" then state = "pause"; S.play("tick"); S.music(false); return end
  if state == "intro" and t > 0.5 then state = "play"; return end
  press(I.keyName(k)); anyKey()
end
function love.gamepadpressed(j, b)
  I.pad = j
  if b == "back" then debugView = not debugView; return end
  if b == "start" then
    if state == "play" then state = "pause"; S.music(false) elseif state == "pause" then state = "play"; S.music(musicOn) end
    return
  end
  if state == "pause" and b == "b" then love.event.quit() end
  if state == "intro" and t > 0.5 then state = "play"; return end
  press(I.padName(b)); anyKey()
end

function love.update(dt)
  dt = math.min(dt, 0.1); t = t + dt
  fps = love.timer.getFPS()
  local t0 = love.timer.getTime()
  if state == "play" then
    acc = acc + dt
    local steps = 0
    while acc >= DT - 1e-9 and steps < 4 do
      stage:update(DT, presses); presses = {}; acc = acc - DT; steps = steps + 1
      if stage.events.over then state, t = "over", 0; S.music(false); S.play("over"); break end
      if stage.events.clear then
        state, t = "clear", 0; S.music(false); S.play("clear")
        local st = stage:stats(); local left = math.max(0, math.floor(st.time))
        tally = { t = 0, shown = 0, lines = { { "BONES", st.bones .. "/" .. st.total }, { "FETCH", "2000" }, { "TIME BONUS", tostring(left * 10) } } }
        tally.score = st.score + left * 10
        if tally.score > best then best = tally.score; tally.newBest = true; pcall(love.filesystem.write, "best.txt", tostring(best)) end
        break
      end
    end
    if steps == 4 then acc = 0 end
  elseif state == "clear" then
    tally.t = tally.t + dt
    if tally.t > 1.4 and tally.shown < tally.score then
      local before = tally.shown
      tally.shown = math.min(tally.score, tally.shown + math.max(10, math.floor(tally.score * dt * 0.9)))
      if math.floor(before / 500) ~= math.floor(tally.shown / 500) then S.play("tick") end
    end
    if tally.shown >= tally.score and tally.t > 1.8 then tally.done = true end
  end
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
  stage:draw(debugView)
  local st = stage:stats()
  U.status({ lives = st.lives, hearts = st.hearts, bones = st.bones, total = st.total, time = st.time, score = st.score })
  if state == "intro" then
    love.graphics.draw(checker, 0, 0)
    U.box(60, 70, 200, 76)
    U.center(def.intro[1], 160, 78, 2, { 252/255, 214/255, 60/255 }); U.center(def.intro[2], 160, 96, 2, { 252/255, 214/255, 60/255 })
    U.center(def.intro[3], 160, 118, 1); U.center(def.intro[4], 160, 130, 1)
    if t > 0.5 and (t % 1.1) < 0.75 then U.prompt("PRESS ANY BUTTON") end
  elseif state == "play" then
    local h = stage:hint(); if h then U.prompt(h) end
    drawTuning()
  elseif state == "pause" then
    love.graphics.draw(checker, 0, 0); U.box(96, 88, 128, 54)
    U.center("PAUSED", 160, 95, 2); U.center("START  GO ON", 160, 116, 1); U.center("B OR ESC  QUIT", 160, 127, 1)
  elseif state == "over" then
    love.graphics.draw(checker, 0, 0); U.box(90, 92, 140, 40); U.center("GAME OVER", 160, 100, 2)
    if t > 1.2 and (t % 1.1) < 0.75 then U.center("PRESS ANY BUTTON", 160, 119, 1) end
  elseif state == "clear" then
    love.graphics.draw(checker, 0, 0); U.box(70, 56, 180, 104)
    local bounce = (tally.t < 0.6) and math.floor(math.sin(tally.t * 20) * 2) or 0
    U.center("GOOD GIRL!", 160, 64 + bounce, 2, { 252/255, 214/255, 60/255 })
    for i, l in ipairs(tally.lines) do
      if tally.t > 0.3 + i * 0.25 then U.text(l[1], 84, 82 + i * 12); U.text(l[2], 236 - 6 * #l[2], 82 + i * 12) end
    end
    if tally.t > 1.3 then U.text("SCORE", 84, 136); U.text(tostring(tally.shown), 236 - 6 * #tostring(tally.shown), 136, { 252/255, 214/255, 60/255 }) end
    if tally.done then
      if tally.newBest and math.floor(tally.t * 3) % 2 == 0 then U.center("NEW BEST!", 160, 148, 1) end
      if (tally.t % 1.1) < 0.75 then U.prompt("PRESS ANY BUTTON") end
    end
  end
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
