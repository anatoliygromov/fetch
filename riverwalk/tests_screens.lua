-- love riverwalk --screenshots: every UI screen of step 3 (ui/hud-v8), shot from the window (640 x 480, the game
-- at exactly 2x) for the QA frames: the level select's cards (open, all medals, locked, mid-slide, both devices,
-- hard mode), the level intro card, the talk panel and the hint bubbles, the pause, the tally show, the story card,
-- GAME OVER, the bonus round's screens and the ending. Saves s_<name>.png and s_<name>.txt (the bodies hud.lua
-- placed, for tools/layout_qa_menus.py) in the save folder, prints "SCREENSHOTS <folder>" and quits.
-- tools/screen_frames.py turns them into 320 x 240 frames in colour and greyscale.
local I = require("input")
local U = require("hud")
return function(api)
  I.testing = true
  local F = api.flow
  F.save, F.prefix = true, "shots_"
  F.wipe()
  -- a save with something to show: River Walk cleared with two medals, City Park with all three, Downtown open
  F.levelPoints("riverwalk", 4250); F.levelTime("riverwalk", 98.4); F.addMedals("riverwalk", { nohit = true, par = true })
  F.levelPoints("citypark_tall", 6120); F.levelTime("citypark_tall", 51.2); F.addMedals("citypark_tall", { nohit = true, bones = true, par = true })
  F.cleared("riverwalk"); F.cleared("citypark_tall")
  local T, k = 0, 0
  local pending
  local function shot(name) return { act = function() love.graphics.captureScreenshot("s_" .. name .. ".png"); U.log = {}; pending = name end, wait = 0.12 } end
  local oldDraw = love.draw
  love.draw = function()
    oldDraw()
    if pending then
      local out = {}
      for _, b in ipairs(U.log or {}) do out[#out + 1] = table.concat(b, " ") end
      love.filesystem.write("s_" .. pending .. ".txt", table.concat(out, "\n") .. "\n"); U.log, pending = nil, nil
    end
  end
  local function tp(x, y) local st = api.stage(); local p = st.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    st.cam = math.max(0, math.min(st.world.width - 320, x - 140)); st.bikes = {}; st.bikeT = 99
  end
  local function say(text, t) local st = api.stage(); st:say(text, t or 6) end
  local function sel(i) local p = F.pick; p.sel, p.from, p.moved = i, i, -1 end
  local steps = {
    { wait = 0.8 }, { act = function() I.last = "pad" end, wait = 0.05 }, shot("intro_riverwalk"),
    { act = function() api.startRun(F.index("soder")) end, wait = 0.04 }, shot("intro_drop"), { wait = 0.8 }, shot("intro_soder"),
    { act = function() I.last = "key"; api.startRun(F.index("night")) end, wait = 0.8 }, shot("intro_night"),
    { act = function() api.startRun(F.index("citypark_tall")) end, wait = 0.8 }, shot("intro_citypark"),
    -- the talk panel: the girl's lines (one row, two rows), at the bottom and (Pepper low on the quay) at the top
    { act = function() api.startRun(1) end, wait = 0.6 }, { act = function() api.setState("play"); tp(760, 184) end, wait = 0.3 },
    { act = function() api.talk.reset(); say("GOOD GIRL, PEPPER!") end, wait = 0.03 }, shot("talk_rise"), { wait = 0.5 }, shot("talk_short"),
    { act = function() api.talk.reset(); say("THE BALL IS BACK ON THE BOAT") end, wait = 0.5 }, shot("talk_long"),
    { act = function() api.talk.reset(); tp(1340, 216); say("OOPS! GET THE BALL!") end, wait = 0.5 }, shot("talk_top"),
    { act = function() api.talk.reset(); tp(2400, 184); say("IT LANDED ON A FERRY! RIDE THE PONTOON!") end, wait = 0.5 }, shot("talk_3rows"),
    { act = function() local st = api.stage(); st.msg = nil; api.talk.reset() end, wait = 0.1 },
    { act = function() api.setState("select"); I.last = "pad"; sel(1) end, wait = 0.3 }, shot("select_1_pad"),
    { act = function() sel(2) end, wait = 0.1 }, shot("select_2_pad"),
    { act = function() sel(3) end, wait = 0.1 }, shot("select_3_pad"),
    { act = function() sel(4) end, wait = 0.1 }, shot("select_4_pad"),
    { act = function() sel(6) end, wait = 0.1 }, shot("select_6_pad"),
    { act = function() I.last = "key"; sel(1) end, wait = 0.1 }, shot("select_1_key"),
    { act = function() sel(4) end, wait = 0.1 }, shot("select_4_key"),
    { act = function() F.hard = true; sel(2) end, wait = 0.1 }, shot("select_hard"),
    { act = function() F.hard = false; sel(1); F.selectInput("right") end, wait = 0.05 }, shot("select_slide"),
  }
  local old = love.update
  love.update = function(dt)
    old(dt); T = T + dt
    local st = steps[k]
    if st and T < (st.wait or 0) then return end
    k = k + 1; T = 0
    st = steps[k]
    if not st then F.wipe(); print("SCREENSHOTS " .. love.filesystem.getSaveDirectory()); io.stdout:flush(); love.event.quit(); return end
    if st.act then st.act() end
  end
end
