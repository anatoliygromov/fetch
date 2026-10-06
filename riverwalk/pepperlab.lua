-- love riverwalk --pepperlab   a level-independent check of Pepper's controller (tools/check_pepper_lab.sh).
-- It builds a small test room in code (no level file is read), drops Pepper in and plays a fixed, scripted
-- sequence of button presses, printing her x, y, vx, vy, clip, frame, face, mode, ground and crouch after every
-- step ("L ..." lines). The room and the script never change, so the printout only changes if Pepper does.
-- The room (feet line y 184, 1200 px wide), left to right:
--   a 28 px block (x 240-280): a tapped hop and a ledge scramble
--   a 56 px block (x 360-400): a held jump and a scramble, then a 56 px drop (landing)
--   a low bar (x 520-600, bottom y 165): 19 px to crawl under
--   a one-way ledge (x 630-710, top y 150): jump up through it, Down + A drops back through
--   a moving one-way deck (x 730-794 to 770-834, top y 172), like the pontoon
--   a water pit (x 864-912, water from y 200), then a flight of stairs down to y 216 (x 1000-1032)
-- The script: idle, walk (B), run, tap jump + scramble, a fall, held jump + scramble, a drop, standing blocked,
-- crawl, skid, turn, bark, pick up (X: the grab clip), one-way ledge up and drop through, ride the deck, a
-- running jump over the pit, the stairs down and up, and at the end a walk into the water.
local I = require("input")
local Wd = require("world")
local Pp = require("pepper")

local W, ROWS = 150, 30
local function buildMap()
  local rows = {}
  for r = 0, ROWS - 1 do
    local line = {}
    for c = 0, W - 1 do
      local ch = "."
      local pit = c >= 108 and c <= 113                            -- x 864-912
      if r >= 23 then
        if pit then ch = (r >= 25) and "~" or "."
        elseif c < 125 + (r - 23) then ch = "#"                      -- the upper floor, then the stairs' fill
        elseif r >= 27 then ch = "#" end                            -- the lower floor (y 216)
        if r >= 23 and r <= 26 and c == 125 + (r - 23) then ch = "\\" end
      end
      line[#line + 1] = ch
    end
    rows[#rows + 1] = table.concat(line)
  end
  return table.concat(rows, "\n") .. "\n"
end

local PROPS = {
  { name = "BLOCK28", kind = "solid",  x0 = 240, x1 = 280, y0 = 156, y1 = 184 },
  { name = "BLOCK56", kind = "solid",  x0 = 360, x1 = 400, y0 = 128, y1 = 184 },
  { name = "BAR",     kind = "solid",  x0 = 520, x1 = 600, y0 = 100, y1 = 165 },
  { name = "LEDGE",   kind = "oneway", x0 = 630, x1 = 710, y0 = 150, y1 = 154 },
}

-- the script: n steps holding these buttons; press = buttons pressed on the segment's first step
local SCRIPT = {
  { n = 30 },                                                      -- stand
  { n = 50, hold = { "right", "walk" } },                          -- walk (sneak)
  { n = 70, hold = { "right" } },                                  -- run into the 28 px block: blocked
  { n = 1,  hold = { "right", "jump" }, press = { "jump" } },      -- tapped hop ...
  { n = 45, hold = { "right" } },                                  -- ... and a scramble onto it
  { n = 40, hold = { "right" } },                                  -- run off it (a 28 px fall), on to the 56 px block
  { n = 1,  hold = { "right", "jump" }, press = { "jump" } },      -- held jump ...
  { n = 40, hold = { "right", "jump" } },                          -- ... and a scramble onto it
  { n = 10 },
  { n = 70, hold = { "right" } },                                  -- run off it: a 56 px drop, landing, on to the bar
  { n = 20, hold = { "right" } },                                  -- standing: blocked by the bar
  { n = 170, hold = { "right", "down" } },                         -- crawl under the bar
  { n = 50, hold = { "right" } },                                  -- run
  { n = 25 },                                                      -- let go at full speed: skid
  { n = 30, hold = { "left" } },                                   -- turn round
  { n = 20, hold = { "right" } },                                  -- and back
  { n = 20 },
  { n = 30, press = { "bark" } },                                  -- bark
  { n = 30, press = { "act" } },                                   -- pick up (the grab clip)
  { n = 1,  hold = { "jump" }, press = { "jump" } },              -- held jump up through the one-way ledge
  { n = 50, hold = { "jump" } },
  { n = 20 },
  { n = 1,  hold = { "down", "jump" }, press = { "jump" } },       -- Down + A: drop through it
  { n = 50 },
  { n = 30, hold = { "right" } },                                  -- onto the moving deck
  { n = 1,  hold = { "right", "jump" }, press = { "jump" } },
  { n = 30, hold = { "right" } },
  { n = 90 },                                                      -- ride it
  { n = 25, hold = { "right" } },
  { n = 1,  hold = { "right", "jump" }, press = { "jump" } },      -- a running held jump over the pit
  { n = 50, hold = { "right", "jump" } },
  { n = 80, hold = { "right" } },                                  -- down the stairs
  { n = 30 },
  { n = 70, hold = { "left" } },                                   -- up the stairs, back towards the pit
  { n = 120, hold = { "left", "walk" } },                          -- walk into the water
}

return function()
  I.testing = true
  local ok = love.filesystem.getInfo("tuning.txt")
  if ok then print("# WARNING: tuning.txt in the save folder changes Pepper's numbers") end
  love.filesystem.write("pepperlab.map", buildMap())
  local w = Wd.load("pepperlab.map", PROPS)
  love.filesystem.remove("pepperlab.map")
  local deck = { name = "DECK", x0 = 730, x1 = 794, y0 = 172, y1 = 176, from = 730, to = 770, speed = 30, dir = 1, dx = 0 }
  w:addMover(deck)
  local p = Pp.new(60, 184)
  local step = 0
  for _, seg in ipairs(SCRIPT) do
    for k = 1, seg.n do
      I.force = {}
      for _, b in ipairs(seg.hold or {}) do I.force[b] = true end
      local presses = {}
      if k == 1 then for _, b in ipairs(seg.press or {}) do presses[b] = true end end
      -- the deck moves first, as in the game (St:update)
      local nx = deck.x0 + deck.dir * deck.speed / 60
      if nx > deck.to then nx = deck.to; deck.dir = -1 elseif nx < deck.from then nx = deck.from; deck.dir = 1 end
      deck.dx = nx - deck.x0; deck.x1 = deck.x1 + deck.dx; deck.x0 = nx
      p:update(1 / 60, w, presses)
      if presses.act and p.mode == "normal" then p:grab() end      -- what the stage does on X
      p.barked = false
      step = step + 1
      print(("L %d %.3f %.3f %.3f %.3f %s %d %d %s %s %s"):format(step, p.x, p.y, p.vx, p.vy, p.anim, p.frame, p.face,
        p.mode, tostring(p.onGround), tostring(p.crouch)))
    end
  end
  I.force = {}
  print(("LAB DONE %d steps"):format(step)); io.stdout:flush()
  love.event.quit()
end
