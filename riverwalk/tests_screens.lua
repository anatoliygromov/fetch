-- love riverwalk --screenshots: every UI screen of step 3 (ui/hud-v8), shot from the window (640 x 480, the game
-- at exactly 2x) for the QA frames: the level select's cards (open, all medals, locked, mid-slide, both devices,
-- hard mode), the level intro card, the talk panel and the hint bubbles, the pause, the tally show, the story card,
-- GAME OVER, the bonus round's screens and the ending. Saves s_<name>.png and s_<name>.txt (the bodies hud.lua
-- placed, for tools/layout_qa_menus.py) in the save folder, prints "SCREENSHOTS <folder>" and quits.
-- tools/screen_frames.py turns them into 320 x 240 frames in colour and greyscale.
local I = require("input")
local Se = require("settings")
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
  local extra, xcv                                                  -- drawn over the game's frame (a made-up case)
  love.draw = function()
    oldDraw()
    if extra then                                                   -- drawn at 1x on a canvas of its own, shown at 2x
      xcv = xcv or love.graphics.newCanvas(320, 240)
      love.graphics.push(); love.graphics.origin()
      love.graphics.setCanvas(xcv); love.graphics.clear(0, 0, 0, 0); extra(); love.graphics.setCanvas()
      love.graphics.setColor(1, 1, 1, 1); love.graphics.draw(xcv, 0, 0, 0, 2, 2); love.graphics.pop()
    end
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
  local function places(list)
    for _, c in ipairs(list) do
      local fake = { pepper = { x = c[1], y = c[2], face = 1 }, cam = 0, camY = 0 }
      love.graphics.setColor(0.2, 0.2, 0.2, 1); local x0, y0, x1, y1 = api.talk.pepperRect(fake)
      love.graphics.rectangle("line", x0 + 0.5, y0 + 0.5, x1 - x0 - 1, y1 - y0 - 1); love.graphics.setColor(1, 1, 1, 1)
      local L = api.talk.bubble({ btn = c[4], text = c[3] }, fake); if L then api.talk.drawBubble(L, 0) end
      U.logBox("pepper", x0, y0, x1 - 1, y1 - 1)
    end
  end
  local function sel(i) local p = F.pick; p.sel, p.from, p.moved = i, i, -1 end
  local steps = {
    { wait = 0.8 }, { act = function() I.last = "pad" end, wait = 0.05 }, shot("intro_riverwalk"),
    { act = function() api.startRun(F.index("soder")) end, wait = 0.04 }, shot("intro_drop"), { wait = 0.8 }, shot("intro_soder"),
    { act = function() I.last = "key"; api.startRun(F.index("night")) end, wait = 0.8 }, shot("intro_night"),
    { act = function() api.startRun(F.index("citypark_tall")) end, wait = 0.8 }, shot("intro_citypark"),
    -- the talk panel: the girl's lines (one row, two rows; the longest line in the game), at the bottom and (Pepper low on the quay) at the top
    { act = function() api.startRun(1) end, wait = 0.6 }, { act = function() api.setState("play"); tp(760, 184) end, wait = 0.3 },
    { act = function() api.talk.reset(); say("GOOD GIRL, PEPPER!") end, wait = 0.03 }, shot("talk_rise"), { wait = 0.5 }, shot("talk_short"),
    { act = function() api.talk.reset(); say("THE BALL IS ON THE BOAT!") end, wait = 0.5 }, shot("talk_long"),
    { act = function() api.talk.reset(); tp(1340, 216); say("OOPS! GET THE BALL!") end, wait = 0.5 }, shot("talk_top"),
    { act = function() api.talk.reset(); tp(2400, 184); say("THE SEAGULL DROPPED THE BALL!") end, wait = 0.5 }, shot("talk_longest"),
    { act = function() local st = api.stage(); st.msg = nil; api.talk.reset() end, wait = 0.1 },
    -- the hint bubbles (River Walk's tutorial zones) and the nudges, the gamepad's glyphs then the keyboard's
    { act = function() I.last = "pad"; tp(230, 184) end, wait = 0.03 }, shot("hint_rise"), { wait = 0.4 }, shot("hint_hop"),
    { act = function() tp(360, 184) end, wait = 0.5 }, shot("hint_bigjump"),
    { act = function() tp(120, 184) end, wait = 0.5 }, shot("hint_crawl"),
    { act = function() tp(30, 184) end, wait = 0.5 }, shot("hint_run"),
    { act = function() I.last = "key"; tp(360, 184) end, wait = 0.5 }, shot("hint_bigjump_key"),
    { act = function() tp(230, 184) end, wait = 0.4 }, shot("hint_hop_key"),
    { act = function() I.last = "pad"; tp(230, 184); local n = api.talk.nudge; n.btn, n.why, n.t = "a", "idle", 0.3 end, wait = 0.05 }, shot("nudge_same"),
    { act = function() local n = api.talk.nudge; n.btn = nil; tp(1000, 184) end, wait = 0.3 },
    { act = function() local n = api.talk.nudge; n.btn, n.why, n.t = "down", "push", 0.1 end, wait = 0.05 }, shot("nudge_push"),
    -- made-up places: Pepper high on the screen (the bubble beside her) and at the very top (under her); her sprite's
    -- box drawn as a thin line
    { act = function() api.talk.nudge.btn = nil; api.stage().msg = nil; extra = function() end end, wait = 0.1 }, shot("hint_none"),
    { act = function() extra = function() places({ { 50, 110, "HOLD: CLIMB", "a" } }) end end, wait = 0.1 }, shot("hint_side"),
    { act = function() extra = function() places({ { 270, 104, "PICK UP", "x" } }) end end, wait = 0.1 }, shot("hint_side_left"),
    { act = function() extra = function() places({ { 160, 52, "HOLD: SNEAK", "b" } }) end end, wait = 0.1 }, shot("hint_under"),
    { act = function() extra = function() places({ { 160, 150, "HOLD: SNIFF", "sniff" } }) end end, wait = 0.1 }, shot("hint_sniff"),
    { act = function() I.last = "key" end, wait = 0.1 }, shot("hint_sniff_key"), { act = function() I.last = "pad" end, wait = 0.05 },
    { act = function() extra = nil; api.talk.reset() end, wait = 0.1 },
    -- the pause: each row, the question, the controls page; the keyboard's glyphs too
    { act = function() I.last = "pad"; tp(760, 184); api.stage().msg = nil; api.talk.reset(); local st = api.stage(); st.taken = 12
      api.setState("pause"); local p = api.pause(); p.sel, p.from, p.moved, p.confirm, p.controls = 1, 1, -1, nil, nil end, wait = 0.15 }, shot("pause_1"),
    { act = function() local p = api.pause(); p.sel, p.from = 2, 2 end, wait = 0.1 }, shot("pause_2_sound"),
    { act = function() local p = api.pause(); p.sel, p.from = 3, 3 end, wait = 0.1 }, shot("pause_3"),
    { act = function() local p = api.pause(); p.sel, p.from = 4, 4 end, wait = 0.1 }, shot("pause_4"),
    { act = function() local p = api.pause(); p.confirm, p.cm = 1, { sel = 1, from = 1, moved = -1 } end, wait = 0.1 }, shot("pause_confirm_1"),
    { act = function() local p = api.pause(); p.confirm, p.cm = 2, { sel = 2, from = 2, moved = -1 } end, wait = 0.1 }, shot("pause_confirm_2"),
    { act = function() local p = api.pause(); p.confirm, p.cm, p.controls = nil, nil, true end, wait = 0.1 }, shot("pause_controls"),
    { act = function() I.last = "key"; local p = api.pause(); p.controls, p.sel, p.from = nil, 2, 2 end, wait = 0.1 }, shot("pause_2_key"),
    { act = function() local p = api.pause(); p.sel, p.from = 1, 1; api.setState("play") end, wait = 0.1 },
    -- the tally's show: River Walk cleared (a bone line, FETCH, SECRETS, TIME BONUS), shot along its timetable
    { act = function() local st = api.stage(); st.taken = 12; st.hearts = 3; st.ball.state = "carried"; st.pepper.carrying = st.ball; st:giveBall() end,
      cond = function() return api.getState() == "clear" end, wait = 0 },
    { act = function() local tl = api.tally(); tl.t, tl.shown, tl.done = 0.05, 0, nil end, wait = 0.02 }, shot("tally_a_start"),
    { act = function() local tl = api.tally(); tl.t = 0.7 end, wait = 0.02 }, shot("tally_b_bones"),
    { act = function() local tl = api.tally(); tl.t = F.tallyPlan(tl).totalT0 + 0.5 end, wait = 0.02 }, shot("tally_c_total"),
    { act = function() local tl = api.tally(); tl.t = F.tallyPlan(tl).medals[2] + 0.02 end, wait = 0.02 }, shot("tally_d_medals"),
    { act = function() local tl = api.tally(); tl.newBest = true; tl.plan = nil; tl.t = F.tallyPlan(tl).stampT + 0.03 end, wait = 0.01 }, shot("tally_e_stamp"),
    { act = function() local tl = api.tally(); F.tallySkip(tl) end, wait = 0.1 }, shot("tally_f_end"),
    { act = function() I.last = "key"; local tl = api.tally(); tl.hard = true; tl.newBest, tl.newBestTime = false, true; tl.plan = nil; F.tallySkip(tl)
      tl.medals = { nohit = true, bones = true, par = true } end, wait = 0.1 }, shot("tally_g_allmedals_key"),
    { act = function() I.last = "pad"; local tl = api.tally(); tl.hard = nil; tl.newBestTime = false; tl.plan = nil; F.tallySkip(tl)
      tl.medals = { nohit = false, bones = false, par = false } end, wait = 0.1 }, shot("tally_h_nomedals"),
    -- the story card, GAME OVER, the ending
    { act = function() local tl = api.tally(); if tl then tl.done = true end; api.setStory(require("level.riverwalk").outro); api.setState("story"); api.setT(0.04) end, wait = 0.01 }, shot("story_drop"),
    { act = function() api.setT(0.6) end, wait = 0.02 }, shot("story_talk"),
    { act = function() api.setT(2.5) end, wait = 0.05 }, shot("story_ready"),
    { act = function() api.setStory(require("level.soder").outro); I.last = "key"; api.setT(2.5) end, wait = 0.05 }, shot("story_soder_key"),
    { act = function() I.last = "pad"; local o = api.over(); o.sel, o.from, o.moved = 1, 1, -1; api.setState("over"); api.setT(0.5) end, wait = 0.02 }, shot("over_wait"),
    { act = function() api.setT(1.5) end, wait = 0.05 }, shot("over_1"),
    { act = function() local o = api.over(); o.sel, o.from = 2, 2 end, wait = 0.05 }, shot("over_2"),
    { act = function() api.setEnding({ score = 23450, best = 23450, newBest = true, lines = require("level.night").outro }); api.setState("ending"); api.setT(0.8) end, wait = 0.02 }, shot("ending_best"),
    { act = function() api.setEnding({ score = 18320, best = 23450, newBest = false, lines = require("level.night").outro }); api.setT(2.6) end, wait = 0.05 }, shot("ending_ready"),
    -- the bonus round: its intro, READY, GO, the last seconds, TIME UP, the result (an extra life, then not)
    { act = function() api.startBonus() end, wait = 0.6 }, shot("bonus_intro"),
    { act = function() local b = api.bonus(); b.phase, b.t = "ready", 0.3 end, wait = 0.02 }, shot("bonus_ready"),
    { act = function() local b = api.bonus(); b.phase, b.t = "play", 0; b.catches, b.points, b.time = 7, 700, 12 end, wait = 0.05 }, shot("bonus_play"),
    { act = function() local b = api.bonus(); b.catches, b.points, b.time = 11, 1350, 3.5 end, wait = 0.03 }, shot("bonus_last"),
    { act = function() local b = api.bonus(); b.phase, b.t = "timeup", 0.2 end, wait = 0.02 }, shot("bonus_timeup"),
    { act = function() local b = api.bonus(); b.phase, b.t, b.air = "result", 1.8, 4 end, wait = 0.02 }, shot("bonus_result_life"),
    { act = function() local b = api.bonus(); b.catches, b.t = 6, 1.8 end, wait = 0.02 }, shot("bonus_result_try"),
    { act = function() api.setState("select"); I.last = "pad"; sel(1) end, wait = 0.3 }, shot("select_1_pad"),
    { act = function() sel(2) end, wait = 0.1 }, shot("select_2_pad"),
    { act = function() sel(3) end, wait = 0.1 }, shot("select_3_pad"),
    { act = function() sel(4) end, wait = 0.1 }, shot("select_4_pad"),
    { act = function() sel(6) end, wait = 0.1 }, shot("select_6_pad"),
    { act = function() I.last = "key"; sel(1) end, wait = 0.1 }, shot("select_1_key"),
    { act = function() sel(4) end, wait = 0.1 }, shot("select_4_key"),
    { act = function() F.hard = true; sel(2) end, wait = 0.1 }, shot("select_hard"),
    { act = function() F.hard = false; sel(1); F.selectInput("right") end, wait = 0.05 }, shot("select_slide"),
    { act = function() sel(1); Se.shownAt = love.timer.getTime() end, wait = 0.1 }, shot("toast_menu"),
  }
  local old = love.update
  love.update = function(dt)
    old(dt); T = T + dt
    local st = steps[k]
    if st and st.cond and not st.cond() then T = 0; return end
    if st and T < (st.wait or 0) then return end
    k = k + 1; T = 0
    st = steps[k]
    if not st then F.wipe(); print("SCREENSHOTS " .. love.filesystem.getSaveDirectory()); io.stdout:flush(); love.event.quit(); return end
    if st.act then st.act() end
  end
end
