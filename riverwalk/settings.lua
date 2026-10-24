-- Player settings that outlive a run: the sound volume (0 = off .. 9: the options' 9 segments) and the music on or off. Saved in
-- settings.txt next to the progress files. The volume is LÖVE's master volume, so it scales every sound.
-- On the handheld the volume buttons reach the game as the keys volumeup / volumedown (main.lua), and the pause
-- has a SOUND row too, so the player can always turn the game down or off whatever the firmware does.
local Se = { volume = 8, music = true, save = true, shownAt = nil }
local FILE = "settings.txt"
Se.MAX = 9

local function apply() if love.audio then pcall(love.audio.setVolume, Se.volume / Se.MAX) end end
function Se.load()
  local ok, s = pcall(love.filesystem.read, FILE)
  if ok and s then
    local v = tonumber(s:match("volume=(%d+)") or "")
    if v then Se.volume = math.max(0, math.min(Se.MAX, v)) end
    local m = s:match("music=(%d)")
    if m then Se.music = m == "1" end
  end
  apply()
end
local function write()
  if Se.save then pcall(love.filesystem.write, FILE, ("volume=%d\nmusic=%d\n"):format(Se.volume, Se.music and 1 or 0)) end
end
-- d = +1 / -1; returns true if the volume changed
function Se.step(d)
  local v = math.max(0, math.min(Se.MAX, Se.volume + d))
  Se.shownAt = love.timer.getTime()
  if v == Se.volume then return false end
  Se.volume = v; apply(); write(); return true
end
-- mute: off, or back to the middle if it was off
function Se.toggleMute()
  Se.shownAt = love.timer.getTime()
  if Se.volume > 0 then Se.lastOn = Se.volume; Se.volume = 0 else Se.volume = Se.lastOn or 6 end
  apply(); write()
end
function Se.setMusic(on) Se.music = on; write() end
-- the volume indicator is shown for a moment after a change
function Se.showing() return Se.shownAt and love.timer.getTime() - Se.shownAt < 1.6 end
return Se
