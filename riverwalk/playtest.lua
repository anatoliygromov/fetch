-- Playtest lab (docs/playtest/method.md). Loaded only by its own flag; normal play and the checks never load it.
--   love riverwalk --level <name> --auto --playtest <personaId> --seed <n> [--out <file.json>]
--     the level's own autopilot (tests_<level>.lua, --auto) plays, and a persona (docs/playtest/personas.json) stands
--     between its buttons and the game (pt_bot.lua). Headless and fast: no drawing, no screenshots, 600 game steps
--     of 1/60 s per frame. Writes one JSON result. AUTO_ROUTE=high picks the Rooftops high road, as for --auto.
--   --playtest perfect: the autopilot through the same layer with no errors (the clean baseline).
local J = require("pt_json")
local loaded = false
local function argVal(args, name) for i, a in ipairs(args) do if a == name then return args[i + 1] end end end

return function(api, args)
  if loaded then return end
  loaded = true
  local id = argVal(args, "--playtest")
  local level = argVal(args, "--level") or "riverwalk"
  local persona
  if id == "perfect" then persona = { id = "perfect", group = "baseline", perfect = true, patience = 1 }
  else
    local src = argVal(args, "--personas") or (love.filesystem.getSource() .. "/../docs/playtest/personas.json")
    local f = assert(io.open(src, "r"), "no personas file: " .. src)
    local data = J.decode(f:read("*a")); f:close()
    for _, p in ipairs(data.personas) do if p.id == id then persona = p end end
  end
  assert(persona, "no persona " .. tostring(id))
  local out = argVal(args, "--out")
  love.graphics.captureScreenshot = function() end                -- the autopilot's GIF frames: not needed here
  print = function() end                                          -- (the input log and the autopilot's lines)
  local Bot = require("pt_bot")
  local bot = Bot.new(api, persona, { level = level, seed = tonumber(argVal(args, "--seed") or "1"), route = os.getenv("AUTO_ROUTE") or "main" })
  pcall(love.window.setVSync, 0)
  local function save()
    local s = J.encode(bot.summary)
    if out then local f = assert(io.open(out, "wb")); f:write(s); f:close() else io.write(s, "\n") end
    io.stdout:flush()
  end
  local finished = false
  love.update = function()
    if finished then return end
    for _ = 1, 600 do
      bot.tick()
      if bot.done then finished = true; save(); bot.realQuit(); return end
    end
  end
  love.draw = function() end
end
