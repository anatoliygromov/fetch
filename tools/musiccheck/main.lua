-- Decodes every music file of the game the way LOVE will (love.sound.newDecoder), checks its length against
-- riverwalk/music/manifest.txt (made by tools/make_music.py), its peak, and for the loops that the last sample
-- runs into the first without a jump bigger than the music's own steps. Run by tools/check_music.sh.
local fails = 0
local function report(name, ok, msg)
  print(("%-44s %s  %s"):format(name, ok and "PASS" or "FAIL", msg or ""))
  if not ok then fails = fails + 1 end
end
local function readFile(path)
  local f = io.open(path, "rb"); if not f then return nil end
  local s = f:read("*a"); f:close(); return s
end
-- every sample of a file, as a Lua array (mono: the first channel)
local function decode(path, maxSeconds)
  local bytes = readFile(path); if not bytes then return nil, "missing" end
  local ok, dec = pcall(love.sound.newDecoder, love.filesystem.newFileData(bytes, path:match("[^/]+$")), 32768)
  if not ok then return nil, tostring(dec) end
  local out, rate, chans = {}, dec:getSampleRate(), dec:getChannelCount()
  while true do
    local sd = dec:decode(); if not sd then break end
    for i = 0, sd:getSampleCount() - 1 do out[#out + 1] = sd:getSample(i * chans) end
    if maxSeconds and #out > maxSeconds * rate then break end           -- (a module that loops by itself never ends)
  end
  return out, rate, chans
end
function love.load(args)
  local dir = args[1] or "riverwalk/music"
  local man = readFile(dir .. "/manifest.txt")
  if not man then print("ERROR: no manifest in " .. dir); os.exit(1) end
  for line in man:gmatch("[^\n]+") do
    local name, n, rate, kind = line:match("^(%S+) (%d+) (%d+) (%a+)")
    if name then
      n, rate = tonumber(n), tonumber(rate)
      local s, r = decode(dir .. "/" .. name .. ".ogg")
      if not s then report(name .. ".ogg decodes", false, r) else
        report(name .. ".ogg decodes", true, ("%d Hz, %.2f s"):format(r, #s / r))
        report(name .. ".ogg length", #s == n and r == rate, ("%d samples, expected %d"):format(#s, n))
        local peak, big = 0, 0
        for i = 1, #s do local a = math.abs(s[i]); if a > peak then peak = a end end
        local steps = {}
        for i = 2, #s do steps[#steps + 1] = math.abs(s[i] - s[i - 1]) end
        table.sort(steps); big = steps[math.floor(#steps * 0.995)]          -- a step bigger than 99.5 % of them
        local db = 20 * math.log10(math.max(peak, 1e-9))
        report(name .. ".ogg peak under -1 dBFS", db < -1, ("%.1f dBFS"):format(db))
        if kind == "loop" then
          local join = math.abs(s[#s] - s[1])
          report(name .. ".ogg loop join", join <= big, ("last to first %.3f, 99.5 %% of the steps inside are under %.3f"):format(join, big))
        else
          report(name .. ".ogg ends in silence", math.abs(s[#s]) < 0.01, ("last sample %.4f"):format(s[#s]))
        end
      end
    end
  end
  -- the game's music code (sfx.lua) picks the right track for each state (args[2]: the game folder; the script
  -- copied music/ next to this file)
  local game = args[2]
  if game then
    package.preload.settings = function() return assert(loadfile(game .. "/settings.lua"))() end
    local S = assert(loadfile(game .. "/sfx.lua"))()
    local good, err = pcall(function()
      S.load()
      local want = { { "title", true }, { "citypark", true }, { "downtown", false }, { "title", true } }
      for _, w in ipairs(want) do
        S.music(true, w[1]); local name, file = S.track()
        report("sfx.lua: track " .. w[1], name == w[1] and file == w[2], file and "its file" or "the synthesised loop")
      end
      S.music(false); S.music(true); S.play("fetch"); S.play("clear"); S.play("over"); S.play("jump")
      S.music(true, "citypark"); S.music(false, "soder")
      local name, file = S.track()
      report("sfx.lua: music off still sets the track", name == "soder" and not file, name)
    end)
    report("sfx.lua: music calls run without errors", good, err)
  end
  -- the tracker module (libmodplug): it must decode, make sound, and loop by itself without a gap (it jumps back
  -- to the start on its last row: 40 s decoded of a 36.4 s tune, sound all through the join)
  local s, r = decode(dir .. "/title.mod", 40)
  if s then
    local function rms(a, b) local e = 0; for i = a, b do e = e + s[i] * s[i] end; return math.sqrt(e / (b - a + 1)) end
    report("title.mod decodes (libmodplug)", rms(1, r * 10) > 0.01, ("%d Hz, rms %.3f"):format(r, rms(1, r * 10)))
    local quiet = 1
    for k = math.floor(35.5 * r), math.floor(37.5 * r), math.floor(r / 50) do quiet = math.min(quiet, rms(k, k + math.floor(r / 50))) end
    report("title.mod loops by itself", #s >= 40 * r and quiet > 0.01, ("%.1f s decoded, quietest 20 ms at the join: rms %.3f"):format(#s / r, quiet))
  else report("title.mod decodes (libmodplug)", false, r) end
  print(fails == 0 and "MUSIC OK" or ("MUSIC: " .. fails .. " FAILED"))
  os.exit(fails == 0 and 0 or 1)
end
