-- love riverwalk --flowtest   drives the real menus with key presses through a whole run and checks the flow:
--   title -> menu -> level select (locks, COMING SOON) -> START GAME -> each level: intro, play (the level is
--   finished through the stage: Pepper is put at the exit or gives the ball), tally, story card -> the ending ->
--   title; then a level from the level select, the pause's quit to title, and GAME OVER.
-- Checks: lives and score carry over, hearts refill, unlocks are saved, missing level files are skipped.
-- It uses its own save files (flowtest_*.txt). Prints PASS / FAIL lines and "n of m passed", saves a screenshot
-- of every screen (flow_*.png) and all of them on one sheet, flow_screens.png, in the save folder.
local I = require("input")
return function(api)
  I.testing = true
  local F = api.flow
  local results = {}
  local function report(name, ok, detail)
    results[#results + 1] = ok and true or false
    print(("%-52s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local shots = {}
  local function shot(name)
    return { act = function()
      love.graphics.captureScreenshot(function(d) shots[#shots + 1] = { name = name, data = d }; d:encode("png", "flow_" .. name .. ".png") end)
    end }
  end
  local function key(k) return { act = function() love.keypressed(k) end } end
  local function wait(s) return { wait = s } end
  local function check(name, f) return { act = function() local ok, detail = f(); report(name, ok, detail) end } end
  local function state(want, limit) return { cond = function() return api.getState() == want end, act = function() end, limit = limit or 8, what = want } end
  local function stats() return api.stage():stats() end
  local function readSave(n) return love.filesystem.read("flowtest_" .. n) or "" end

  -- finish the level being played, through the stage: at the exit (with the ball if it needs it), or the
  -- ball given to the girl
  local function finish()
    local s = api.stage(); local p, e = s.pepper, s.def.exit
    if e then
      if e.needBall then s.ball.state = "carried"; p.carrying = s.ball end
      p.x = e.x + 4; p.y = s.world:groundAt(p.x) or p.y; p.vx, p.vy, p.onGround, p.mode = 0, 0, true, "normal"
    else s:giveBall() end
  end

  local run = F.newRun(1)
  local names = run.names
  local steps = {}
  local function add(...) for _, st in ipairs({ ... }) do steps[#steps + 1] = st end end

  -- the level list and the run: a missing file is skipped (also checked on a made-up list)
  add(check("levels.lua: files found as they are on disk", function()
    local ok, d = true, {}
    for _, l in ipairs(F.levels) do
      local has = love.filesystem.getInfo("level/" .. l.name .. ".lua") ~= nil
      ok = ok and (l.exists == has); d[#d + 1] = l.name .. (l.exists and "" or " (missing)")
    end
    return ok, table.concat(d, ", ")
  end))
  add(check("a run skips missing level files", function()
    local fake = { { name = "a", exists = true }, { name = "b", exists = false }, { name = "c", exists = true } }
    local r, real = F.newRun(1, fake), 0
    for _, l in ipairs(F.levels) do if l.exists then real = real + 1 end end
    return #r.names == 2 and r.names[2] == "c" and #names == real, ("made-up: %s; real run: %s"):format(table.concat(r.names, " "), table.concat(names, " "))
  end))

  -- title and menu
  add(wait(0.8), shot("0_title"), check("starts on the title screen", function() return api.getState() == "title", api.getState() end))
  add(key("space"), state("menu", 2), wait(0.7), shot("1_menu"))
  add(check("menu: START GAME is selected", function() return F.menu.sel == 1, F.menu.items[F.menu.sel] end))
  -- level select: fresh progress, only level 1 open
  add(key("down"), key("space"), state("select", 1), wait(0.3), shot("2_select"))
  add(check("level select: level 1 open, the others locked", function()
    local ok, d = F.isOpen(1), {}
    for i = 2, #F.levels do ok = ok and not F.isOpen(i); d[#d + 1] = F.levels[i].name .. (F.isOpen(i) and " open" or " locked") end
    return ok, table.concat(d, ", ")
  end))
  add(key("down"), key("space"),
    check("level select: a locked level cannot be chosen", function() return api.getState() == "select", api.getState() end))
  for i, l in ipairs(F.levels) do
    if not l.exists then
      add(check(("level select: %s says COMING SOON"):format(l.name), function() return not l.exists, "no level/" .. l.name .. ".lua" end))
    end
  end
  add(key("escape"), check("level select: Esc goes back to the menu", function() return api.getState() == "menu", api.getState() end))

  -- START GAME: the whole run
  local prev                                                       -- the tally of the level before
  add(key("up"), key("space"), state("intro", 1), wait(0.6), shot("3_intro"))
  for k, name in ipairs(names) do
    add(check(("run %d/%d: intro of %s"):format(k, #names, name), function()
      local s = api.stage()
      return api.getState() == "intro" and api.run().names[api.run().k] == name and s.def == require("level." .. name), s.def.name
    end))
    if k == 1 then
      add(check("run 1: a fresh run starts with 3 lives, score 0", function() local st = stats(); return st.lives == 3 and st.score == 0, ("lives %d score %d"):format(st.lives, st.score) end))
    else
      add(check(("run %d: lives carried over (2)"):format(k), function() local st = stats(); return st.lives == 2, ("lives %d"):format(st.lives) end))
      add(check(("run %d: score carried over"):format(k), function() local st = stats(); return st.score == prev.score and st.levelScore == 0, ("%d, before %d"):format(st.score, prev.score) end))
      add(check(("run %d: hearts refilled, timer restarted"):format(k), function() local st, s = stats(), api.stage()
        return st.hearts == 3 and st.time == s.def.time, ("hearts %d time %d"):format(st.hearts, st.time) end))
      add(check(("run %d: %s unlocked and saved"):format(k, name), function() return F.unlocked[name] and readSave("progress.txt"):find(name) ~= nil, (readSave("progress.txt"):gsub("\n", " ")) end))
    end
    add(wait(0.6), key("space"), state("play", 1), wait(0.2))
    add({ act = function() local s = api.stage(); s.lives, s.hearts, s.score = 2, 1, s.score + 1200; finish() end })
    add(state("clear", 6), { cond = function() local tl = api.tally(); return tl and tl.done end, act = function() end, limit = 8, what = "the tally" })
    add(check(("run %d: the tally adds up"):format(k), function()
      local tl, st = api.tally(), stats()
      if not tl then return false, "no tally" end
      local tb = tonumber(tl.lines[#tl.lines][2])
      local ok = tl.lines[1][1] == "BONES" and tl.lines[#tl.lines][1] == "TIME BONUS" and tl.points == st.levelScore + tb
        and tl.score == st.score + tb and api.run().score == tl.score
      if st.bonus then ok = ok and tl.lines[2][1] == st.bonus[1] and #tl.lines == 3 else ok = ok and #tl.lines == 2 end
      local d = {}; for _, l in ipairs(tl.lines) do d[#d + 1] = l[1] .. " " .. l[2] end
      return ok, table.concat(d, ", ") .. (", points %d, score %d"):format(tl.points, tl.score)
    end))
    add({ act = function() prev = api.tally() end })
    if k == #names then add(shot("5_tally")) end
    add(key("space"))
    if k < #names then
      if require("level." .. name).outro then
        add(state("story", 1), wait(0.6), shot("4_story"),
          check(("run %d: story card with %s's outro"):format(k, name), function() return api.getState() == "story", api.getState() end), key("space"))
      end
      add(state("intro", 1))
    end
  end
  -- the ending
  add(state("ending", 1), check("ending: the final score is the run's score", function()
    return api.run().score == prev.score, ("%d"):format(api.run().score) end))
  add(check("ending: best run saved", function() return tonumber(readSave("best_run.txt")) == prev.score and F.bestRun == prev.score, readSave("best_run.txt") end))
  add(key("space"), check("ending: no key for the first 2 s", function() return api.getState() == "ending", api.getState() end))
  add(wait(2.3), shot("6_ending"), key("space"), state("title", 1),
    check("ending: back to the title", function() return api.getState() == "title", api.getState() end))

  -- level select again: everything played is open; the last level from the select starts a fresh run
  add(wait(0.8), key("space"), state("menu", 2), key("down"), key("space"), state("select", 1))
  add(check("level select: every level of the run is open now", function()
    local ok = true; for i, l in ipairs(F.levels) do if l.exists then ok = ok and F.isOpen(i) end end
    F.load(); for i, l in ipairs(F.levels) do if l.exists then ok = ok and F.isOpen(i) end end      -- and from the file
    return ok, (readSave("progress.txt"):gsub("\n", " "))
  end))
  add(key("up"), key("space"), state("intro", 1), check("level select: the last level starts a fresh run", function()
    local st, r = stats(), api.run()
    return r.names[1] == names[#names] and #r.names == 1 and st.lives == 3 and st.score == 0, ("%s, lives %d, score %d"):format(r.names[1], st.lives, st.score)
  end))
  -- pause: quit to the title
  add(wait(0.6), key("space"), state("play", 1), wait(0.2), key("return"), state("pause", 1), wait(0.1), shot("7_pause"))
  add(key("escape"), check("pause: Esc quits to the title", function() return api.getState() == "title" and api.run() == nil, api.getState() end))
  -- GAME OVER: back to the title, the unlocks stay
  add(wait(0.8), key("space"), state("menu", 2), key("space"), state("intro", 1), wait(0.6), key("space"), state("play", 1))
  add({ act = function() local s = api.stage(); s.lives, s.hearts = 1, 1; s:loseHeart() end }, state("over", 1), wait(1.4), shot("8_gameover"))
  add(key("space"), state("title", 1), check("game over: back to the title, unlocks kept", function()
    F.load(); local ok = api.getState() == "title"
    for i, l in ipairs(F.levels) do if l.exists then ok = ok and F.isOpen(i) end end
    return ok, api.getState()
  end))

  -- the summary and the contact sheet (4 x 2, the screens at 2x)
  add(wait(0.2), { act = function()
    table.sort(shots, function(a, b) return a.name < b.name end)
    local keep = {}
    for _, s in ipairs(shots) do if s.name ~= "0_title" then keep[#keep + 1] = s end end
    local w, h, gap = 640, 480, 8
    local sheet = love.image.newImageData(4 * w + 5 * gap, 2 * h + 3 * gap)
    sheet:mapPixel(function() return 0.1, 0.1, 0.12, 1 end)
    for i, s in ipairs(keep) do
      local c, r = (i - 1) % 4, math.floor((i - 1) / 4)
      sheet:paste(s.data, gap + c * (w + gap), gap + r * (h + gap), 0, 0, w, h)
    end
    sheet:encode("png", "flow_screens.png")
    local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
    print(("SHEET %s/flow_screens.png (%d screens)"):format(love.filesystem.getSaveDirectory(), #keep))
    print(("%d of %d passed"):format(ok, #results)); io.stdout:flush()
    love.event.quit()
  end })

  local i, since = 1, 0
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; since = since + dt
    old(dt)
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond() then st.act(); i, since = i + 1, 0
      elseif since > st.limit then
        report(("step %d: waiting for %s"):format(i, st.what or "a condition"), false, "stuck in " .. api.getState())
        i, since = i + 1, 0
      end
    else st.act(); i, since = i + 1, 0 end
  end
end
