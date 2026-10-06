-- Playtest lab (docs/playtest/method.md). Only loaded by its own flags; normal play and the tests never load it.
--   love riverwalk --playtest <personaId> --seed <n> [--level <name>] [--fresh] [--out <file.json>]
--        [--capture-steps 120,480,... --capture-prefix <path>]
--     a persona bot plays the level once (headless and fast: no drawing, 600 game steps of 1/60 s per frame)
--     and writes the run (summary and event log) as JSON. --fresh: the persona has not played the levels before
--     this one (default: campaign, they have). --capture-steps: draw and save the frames after those game steps
--     (the run is deterministic for a persona, level and seed, so a second run can picture what the first found).
--   love riverwalk --level <name> --auto --log [--out <file.json>]
--     the autopilot's clean run with the event log riding along (it only watches).
local J = require("pt_json")
local Log = require("pt_log")
local loaded = false

local function argVal(args, name) for i, a in ipairs(args) do if a == name then return args[i + 1] end end end
local function has(args, name) for _, a in ipairs(args) do if a == name then return true end end end
local function write(path, s) local f = assert(io.open(path, "wb")); f:write(s); f:close() end

return function(flag, api, args)
  if loaded then return end
  loaded = true
  local log = Log.new(api)
  local out = argVal(args, "--out")
  local level = argVal(args, "--level") or "riverwalk"

  if not has(args, "--playtest") then                               -- --log: watch whatever runs
    local prev = love.update
    love.update = function(dt) prev(dt); log:tick() end
    local prevQuit = love.quit
    love.quit = function()
      log:finish()
      local s = api.stage()
      local res = { persona = "autopilot", level = level, mode = "auto", result = api.getState() == "clear" and "clear" or api.getState(),
        play_time = log.playT, steps = log.step, bones = s and s.taken, bones_total = s and s.total, events = log.events, cards = log.cards }
      if out then write(out, J.encode(res)) else print(J.encode(res)) end
      if prevQuit then return prevQuit() end
    end
    return
  end

  -- the persona
  local id = argVal(args, "--playtest")
  local src = argVal(args, "--personas") or (love.filesystem.getSource() .. "/../docs/playtest/personas.json")
  local f = assert(io.open(src, "r"), "no personas file: " .. src)
  local data = J.decode(f:read("*a")); f:close()
  local persona
  for _, p in ipairs(data.personas) do if p.id == id then persona = p end end
  assert(persona, "no persona " .. tostring(id))
  local Bot = require("pt_bot")
  local bot = Bot.new(api, log, persona, { level = level, seed = tonumber(argVal(args, "--seed") or "1"), fresh = has(args, "--fresh") })

  -- frames to capture (game steps), drawn and saved as <prefix>_<step>.png
  local caps, capPrefix = {}, argVal(args, "--capture-prefix") or "cap"
  for n in (argVal(args, "--capture-steps") or ""):gmatch("%d+") do caps[tonumber(n)] = true end
  local lastCap = 0
  for n in pairs(caps) do lastCap = math.max(lastCap, n) end

  pcall(love.window.setVSync, 0)
  local STEPS = 600
  local update, draw = love.update, love.draw
  local drawNow, finished, written = nil, false, false
  local function save()                                             -- the run's result, once, when the bot is done
    if written then return end
    written = true
    log:finish()
    local res = bot:summary()
    if out then write(out, J.encode(res)) else print(J.encode(res)) end
    io.stdout:flush()
  end
  local function finish() save(); finished = true; love.event.quit() end
  love.update = function()
    if finished then return end
    for _ = 1, STEPS do
      update(1 / 60)
      log:tick()
      bot:tick()
      if bot.done then
        save()
        if log.step >= lastCap then finish(); return end
      end
      if log.T > 4000 then bot.result = "stall"; finish(); return end
      if caps[log.step] then drawNow = log.step; return end
    end
  end
  love.draw = function()
    if not drawNow then return end
    local n = drawNow; drawNow = nil
    draw()
    love.graphics.captureScreenshot(function(img)
      local fd = img:encode("png")
      write(("%s_%06d.png"):format(capPrefix, n), fd:getString())
    end)
  end
end
