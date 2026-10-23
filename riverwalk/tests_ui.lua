-- love riverwalk [--level <name>] --uishots: real frames of the UI for its QA cards (ui/hud-v8). River Walk's
-- intro is left, Pepper stands on open ground, then the HUD, the pause (each row selected, the QUIT question)
-- and the level tally are shot from the window (640 x 480, the game at 2x). Saves ui_<name>.png in the save
-- folder, prints "UISHOTS <n>" and quits. tools/ui_frames.py turns them into 320 x 240 frames.
-- With each shot, the bodies the UI placed in that frame (hud.lua U.log) go to ui_<name>.txt for tools/layout_qa8.py.
local I = require("input")
local U = require("hud")
return function(api)
  I.testing = true
  local T, k = 0, 0
  local pending
  local function shot(name) return { act = function() love.graphics.captureScreenshot("ui_" .. name .. ".png"); U.log = {}; pending = name end, wait = 0.15 } end
  local oldDraw = love.draw
  love.draw = function()
    oldDraw()
    if pending then
      local out = {}
      for _, b in ipairs(U.log or {}) do out[#out + 1] = table.concat(b, " ") end
      love.filesystem.write("ui_" .. pending .. ".txt", table.concat(out, "\n") .. "\n"); U.log, pending = nil, nil
    end
  end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); s.bikes = {}; s.bikeT = 99
  end
  local spot = { tonumber(os.getenv("UI_X") or "") or 760, tonumber(os.getenv("UI_Y") or "") or 184 }
  local steps = {
    { wait = 0.6 }, { act = function() love.keypressed("space") end, wait = 0.3 }, { act = function() api.setState("play") end, wait = 0.1 },
    { act = function() tp(spot[1], spot[2]) end, wait = 0.8 },
    shot("hud"),
    { act = function() local s = api.stage(); s.hearts = 2; s.taken = math.min(s.total, 12); s.score = 4250 end, wait = 0.3 },
    shot("hud_2"),
    { act = function() local s = api.stage(); s.hearts = 1; s.time = 9.5 end, wait = 0.2 }, shot("hud_low"),
    { act = function() local s = api.stage(); s.time = 245; s.hearts = 3; s.hard = true end, wait = 0.1 }, shot("hud_hard"),
    { act = function() api.stage().hard = nil end, wait = 0.1 },
    { act = function() api.setState("pause"); local p = api.pause(); p.sel, p.confirm = 1, nil end, wait = 0.2 }, shot("pause"),
    { act = function() api.pause().sel = 2 end, wait = 0.1 }, shot("pause_sound"),
    { act = function() api.pause().sel = 3 end, wait = 0.1 }, shot("pause_quit"),
    { act = function() api.pause().confirm = 1 end, wait = 0.1 }, shot("pause_confirm"),
    { act = function() local p = api.pause(); p.sel, p.confirm = 1, nil; api.setState("play") end, wait = 0.2 },
    { act = function() local s = api.stage(); s.ball.state = "carried"; s.pepper.carrying = s.ball; s:giveBall() end, wait = 6.5 },
    shot("tally"), { wait = 0.4 }, shot("tally_2"), { wait = 0.4 }, shot("tally_3"),
  }
  local old = love.update
  love.update = function(dt)
    old(dt); T = T + dt
    local st = steps[k]
    if st and T < (st.wait or 0) then return end
    k = k + 1; T = 0
    st = steps[k]
    if not st then print("UISHOTS " .. love.filesystem.getSaveDirectory()); io.stdout:flush(); love.event.quit(); return end
    if st.act then st.act() end
  end
end
