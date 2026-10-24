-- love riverwalk --flowtest   drives the real menus with key presses through a whole run and checks the flow:
--   title -> menu -> level select (locks, COMING SOON) -> PLAY -> each level: intro, play (the level is
--   finished through the stage: Pepper is put at the exit or gives the ball), tally, story card -> the ending ->
--   title; then a level from the level select (with its medals), the pause's QUIT and its question, GAME OVER
--   with TRY AGAIN and MENU, and OPTIONS (SOUND, CONTROLS, HARD MODE).
-- Checks: lives and score carry over, hearts refill, unlocks are saved, missing level files are skipped, the
-- talk panel (who says what, the hints that used to be hidden, teaching hints first), the stuck nudge, the story
-- card's wait, best times and medals saved, and that every hint fits the panel.
-- It uses its own save files (flowtest_*.txt). Prints PASS / FAIL lines and "n of m passed", saves a screenshot
-- of every screen (flow_*.png) and all of them on one sheet, flow_screens.png, in the save folder.
local I = require("input")
local St = require("stage")
local Se = require("settings")
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
  local T = api.talk
  local function said() local c = T.cur; return c and c.line end
  local function tp(x, y) local s = api.stage(); local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", false, 0
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); s.bikes = {}; s.bikeT = 99
  end
  local function hold(...) I.force = {}; for _, k in ipairs({ ... }) do I.force[k] = true end end

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
  local bh = { add = add, key = key, wait = wait, state = state, check = check, shot = shot, api = api }   -- [bonus] tests_bonus.flow

  -- the level list and the run: a missing file is skipped (also checked on a made-up list)
  add(check("levels.lua: files found as they are on disk", function()
    local ok, d = true, {}
    for _, l in ipairs(F.levels) do
      local has = love.filesystem.getInfo("level/" .. l.name .. ".lua") ~= nil
      ok = ok and (l.exists == has); d[#d + 1] = l.name .. (l.exists and "" or " (missing)")
    end
    return ok, table.concat(d, ", ")
  end))
  add(check("levels.lua: the order (D2: the tall City Park and Downtown are levels 2 and 3)", function()
    local want = { "riverwalk", "citypark_tall", "downtown_tall", "rooftops", "soder", "night" }
    local ok, d = #F.levels == #want, {}
    for i, l in ipairs(F.levels) do ok = ok and l.name == want[i] and l.number == i; d[#d + 1] = l.name end
    return ok, table.concat(d, ", ")
  end))
  add(check("levels.lua: every level's cards agree (number, name, intro, story)", function()
    local bad, d = {}, {}
    for i, l in ipairs(F.levels) do
      local L = require("level." .. l.name)
      local good = L.number == l.number and L.name == l.title and L.intro and L.intro[1] == "LEVEL " .. l.number
        and L.intro[2] == l.title and (i == #F.levels or (L.outro and #L.outro > 0))
      if not good then bad[#bad + 1] = l.name end
      d[#d + 1] = ("%d %s"):format(L.number or -1, L.name or "?")
    end
    return #bad == 0, #bad == 0 and table.concat(d, ", ") or ("wrong: " .. table.concat(bad, ", "))
  end))
  add(check("levels.lua: a save with the flat City Park opens the tall one", function()
    local u, sv, fr = F.unlocked, F.save, love.filesystem.read
    F.save = false
    love.filesystem.read = function(n, ...) if n == F.prefix .. "progress.txt" then return "riverwalk\ncitypark\n" end return fr(n, ...) end
    F.load(); local ok = F.unlocked.citypark_tall == true and not F.unlocked.downtown_tall
    love.filesystem.read = fr; F.unlocked, F.save = u, sv
    return ok, ok and "citypark -> citypark_tall open" or "not carried over"
  end))
  add(check("a run skips missing level files", function()
    local fake = { { name = "a", exists = true }, { name = "b", exists = false }, { name = "c", exists = true } }
    local r, real = F.newRun(1, fake), 0
    for _, l in ipairs(F.levels) do if l.exists then real = real + 1 end end
    return #r.names == 2 and r.names[2] == "c" and #names == real, ("made-up: %s; real run: %s"):format(table.concat(r.names, " "), table.concat(names, " "))
  end))

  -- the hints: every one fits the panel; Pepper's have a known button and 1 to 3 words
  add(check("hints: all fit the panel, Pepper's are 1 to 3 words with a picture sign", function()
    local bad, n = {}, 0
    for _, l in ipairs(F.levels) do
      if l.exists then
        for _, h in ipairs(require("level." .. l.name).hints) do
          n = n + 1
          local who = h.btn and "pepper" or "girl"
          local L = T.layout({ who = who, btn = h.btn, text = h.text }, "bottom")
          local words = select(2, h.text:gsub("%a+", ""))                  -- "+" is not a word
          local shown = select(2, table.concat(L.rows, " "):gsub("%a+", ""))     -- (step 3: the words the bubble shows)
          if L.x0 < 0 or L.x1 > 320 or #L.rows > (h.btn and 2 or 3) or (h.btn and (words > 3 or shown > 3))
            or (h.btn and not ({ a = 1, b = 1, x = 1, y = 1, down = 1, right = 1, sniff = 1 })[h.btn]) or h.text:find("\226\128\148")
            or (h.btn and not T.picFor({ btn = h.btn, text = h.text })) then bad[#bad + 1] = l.name .. ": " .. h.text end
        end
      end
    end
    return #bad == 0, #bad == 0 and (n .. " hints") or table.concat(bad, "; ")
  end))
  -- the hints that never showed before, and who wins the panel (on stages of their own)
  add(check("hints: the log hop shows once Pepper sneaks (City Park)", function()
    local s = St.new(require("level.citypark")); local p = s.pepper
    p.x = 120; hold("walk"); local h = s:hint(); I.force = {}
    local h2 = (function() p.x = 60; return s:hint() end)()
    return h and h.btn == "a" and h.text == "TAP: HOP" and h2 and h2.btn == "b", ("walking at 120: %s; running at 60: %s"):format(h and h.text or "-", h2 and h2.text or "-")
  end))
  add(check("bones: none is inside a solid (every level of levels.lua)", function()
    local bad = {}
    for _, L in ipairs(require("levels")) do
      local s = St.new(require("level." .. L.name)); local w = s.world
      for _, bn in ipairs(s.bones) do
        if w:solidIn(bn.x - 3, bn.x + 3, bn.y - 12, bn.y - 6) then bad[#bad + 1] = L.name .. " " .. bn.x end
      end
    end
    return #bad == 0, #bad == 0 and "all clear" or table.concat(bad, ", ")
  end))
  add(check("hints: the magpie line shows (City Park)", function()
    local s = St.new(require("level.citypark")); s:resetMagpie(6); s.pepper.x = 1900
    local h = s:hint(); return h and h.who == "girl" and h.text:find("BIRD STILL") ~= nil, h and h.text or "-"
  end))
  add(check("hints: GO BACK: BARK AT THE CAT shows (Downtown)", function()
    local s = St.new(require("level.downtown")); s.pepper.x = 1900
    local h = s:hint(); return h and h.who == "girl" and h.text:find("BARK AT THE CAT") ~= nil, h and h.text or "-"
  end))
  add(check("hints: a teaching hint wins over a message", function()
    local s = St.new(require("level.citypark")); s.pepper.x = 500; s:say("IT DROPPED THE BALL!")
    local h = s:hint(); return h and h.btn == "down" and h.text == "CRAWL", h and h.text or "-"
  end))
  add(check("hints: hard mode has messages but no hints", function()
    local s = St.new(require("level.citypark"), { hard = true }); s.pepper.x = 500
    local h1 = s:hint(); s:say("IT DROPPED THE BALL!"); local h2 = s:hint()
    return s.hard and h1 == nil and h2 and h2.who == "girl", ("%s / %s"):format(h1 and h1.text or "none", h2 and h2.text or "none")
  end))

  -- title and menu
  add(wait(0.8), shot("0_title"), check("starts on the title screen", function() return api.getState() == "title", api.getState() end))
  add(key("volumeup"), wait(0.6), check("title: a volume button is not 'any key'", function() return api.getState() == "title", api.getState() end), shot("u11_title_volume"))
  add(key("space"), state("menu", 2), wait(0.7), shot("1_menu"))
  add(check("menu: PLAY is selected", function() return F.menu.sel == 1 and F.menu.items[1] == "PLAY", F.menu.items[F.menu.sel] end))
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

  -- PLAY: the whole run (a fresh save: the furthest open level is the first)
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
    if name == "citypark" or name == "citypark_tall" then        -- (r6/levels: level 2 now; River Walk opens the run)
      local dy = (require("level." .. name).foot or 184) - 184     -- (r8/levels: the tall City Park, its path at y 328)
      -- the talk panel: Pepper says the control hint at the start (the magpie is ahead: sneak)
      add(wait(0.4), check("talk: Pepper says [B] HOLD: SNEAK at the start", function()
        local l = said(); return l and l.who == "pepper" and l.btn == "b" and l.text == "HOLD: SNEAK", l and l.text or "nothing" end), shot("u1_pepper"))
      add(check("talk: the panel never covers Pepper", function()
        local L = T.placed(api.stage()); local x0, y0, x1, y1 = T.pepperRect(api.stage())
        return L and not (L.x0 < x1 and L.x1 > x0 and L.y0 < y1 and L.y1 > y0), L and ("panel y %d-%d, Pepper y %d-%d"):format(L.y0, L.y1, y0, y1) or "no panel" end))
      -- idle 3 s where a hint applies: the button bounces above her head; a press ends it
      add(wait(3.1), check("nudge: idle 3 s shows the B button above Pepper", function()
        local n = T.nudge; return n.btn == "b" and n.why == "idle", tostring(n.btn) end), wait(0.25), shot("u3_nudge"))
      add(key("z"), wait(0.05), check("nudge: a button press ends it", function() return T.nudge.btn == nil, tostring(T.nudge.btn) end))
      -- pushing against the hedge for 2 s: the Down button
      add({ act = function() tp(500, 184 + dy); api.stage().pepper.face = 1; hold("right") end }, wait(2.4),
        check("nudge: 2 s pushing at the hedge shows Down", function() local n = T.nudge; return n.btn == "down" and n.why == "push", tostring(n.btn) end),
        { act = function() I.force = {} end })
      -- the girl's line: the magpie still has the ball, far off
      add({ act = function() tp(1900, 184 + dy) end }, wait(0.5), check("talk: the girl says the magpie line", function()
        local l = said(); return l and l.who == "girl" and l.text:find("BIRD STILL") ~= nil, l and l.text or "nothing" end), shot("u2_girl"))
      add({ act = function() tp(1600, 216 + dy) end }, wait(0.1))
    end
    if name == "riverwalk" then
      -- low on the quay the bottom panel would cover Pepper: it moves to the top
      add({ act = function() tp(1340, 216) end }, wait(0.4), check("talk: Pepper low on the quay: the panel goes to the top", function()
        local L = T.placed(api.stage()); local x0, y0, x1, y1 = T.pepperRect(api.stage())
        return L and L.by < 100 and not (L.x0 < x1 and L.x1 > x0 and L.y0 < y1 and L.y1 > y0), L and ("panel y %d-%d, Pepper y %d-%d"):format(L.y0, L.y1, y0, y1) or "no panel" end),
        shot("u10_top"))
    end
    add({ act = function() local s = api.stage(); s.lives, s.hearts, s.score = 2, 1, s.score + 1200
      if k == 1 then for _, bn in ipairs(s.bones) do if bn.super then bn.taken = true; s.taken = s.taken + 1; break end end end   -- [bonus] a golden bone
      finish() end })
    add(state("clear", 6), { cond = function() local tl = api.tally(); return tl and tl.done end, act = function() end, limit = 8, what = "the tally" })
    add(check(("run %d: the tally adds up"):format(k), function()
      local tl, st = api.tally(), stats()
      if not tl then return false, "no tally" end
      local tb = tonumber(tl.lines[#tl.lines][2])
      local ok = tl.lines[1][1] == "BONES" and tl.lines[#tl.lines][1] == "TIME BONUS" and tl.points == st.levelScore + tb
        and tl.score == st.score + tb and api.run().score == tl.score
      local n = 2 + (st.bonus and 1 or 0) + (st.secrets and st.secretsTotal and 1 or 0)    -- SECRETS: when the level has them
      if st.bonus then ok = ok and tl.lines[2][1] == st.bonus[1] end
      ok = ok and #tl.lines == n
      local d = {}; for _, l in ipairs(tl.lines) do d[#d + 1] = l[1] .. " " .. l[2] end
      return ok, table.concat(d, ", ") .. (", points %d, score %d"):format(tl.points, tl.score)
    end))
    add({ act = function() prev = api.tally() end })
    add(check(("run %d: clear time and best time saved"):format(k), function()
      local tl = api.tally(); local saved = tonumber(readSave("time_" .. name .. ".txt"))
      return tl.time > 0 and saved and math.abs(saved - tl.time) < 0.01 and tl.best == saved and tl.newBestTime, ("time %.2f, saved %s"):format(tl.time, tostring(saved))
    end))
    add(check(("run %d: medals (a heart lost: no NO HIT) saved"):format(k), function()
      local tl = api.tally(); local m = F.medals(name)
      return not tl.medals.nohit and tl.medals.par and not tl.medals.bones and m.par and not m.nohit, readSave("medals_" .. name .. ".txt"):gsub("\n", "")
    end))
    add(key("space"))
    if k == 1 then require("tests_bonus").flow(bh, { name = "bonus, run 1", life = false, after = k < #names and "story" or "ending", tag = "b" }) end   -- [bonus]
    if k == 2 then add(check("bonus: no golden bone, no FETCH FRENZY", function() return api.getState() ~= "bonus" and api.bonus() == nil, api.getState() end)) end
    if k < #names then
      if require("level." .. name).outro then
        add(state("story", 1), wait(0.6), key("space"), key("x"),
          check(("run %d: story card with %s's outro waits 2 s"):format(k, name), function() return api.getState() == "story", api.getState() end),
          wait(1.6), key("x"), key("lshift"), check(("run %d: story card: only A goes on"):format(k), function() return api.getState() == "story", api.getState() end),
          shot("4_story"), key("space"))
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
  -- a clean clear (every bone, no heart lost, fast): all three medals, a new best time
  local last = names[#names]
  add(wait(0.6), key("space"), state("play", 1), wait(0.3))
  add({ act = function() local s = api.stage(); for _, bn in ipairs(s.bones) do bn.taken = true end; s.taken = s.total; finish() end })
  add(state("clear", 6), wait(0.3), key("lshift"), check("tally: any button skips the show to its end", function()   -- (ui step 3)
    local tl = api.tally(); return tl and tl.done and tl.shown == tl.points and api.getState() == "clear", tl and ("t %.2f, shown %d of %d"):format(tl.t, tl.shown, tl.points) or "no tally" end))
  add({ cond = function() local tl = api.tally(); return tl and tl.done end, act = function() end, limit = 8, what = "the tally" })
  add(check("medals: NO HIT, ALL BONES, PAR TIME won and saved", function()
    local tl, m = api.tally(), F.medals(last)
    return tl.medals.nohit and tl.medals.bones and tl.medals.par and m.nohit and m.bones and m.par, readSave("medals_" .. last .. ".txt"):gsub("\n", "")
  end))
  add(check("best time: the faster of the two clears is kept", function()
    local tl = api.tally(); local b = math.min(tl.time, prev.time)
    return tl.best == b and tl.newBestTime == (tl.time < prev.time) and F.levelTimeBest(last) == b,
      ("%.2f then %.2f, best %.2f"):format(prev.time, tl.time, tl.best) end), shot("5_tally"), shot("u4_tally"))
  add(key("space"))
  require("tests_bonus").flow(bh, { name = "bonus, clean clear", life = true, after = "ending", tag = "c" })    -- [bonus] every bone: golden too
  add(wait(2.3), key("space"), state("title", 1))
  add(wait(0.8), key("space"), state("menu", 2), key("down"), key("space"), state("select", 1), wait(0.3), shot("u6_select"),
    check("level select: medals shown from the saves", function() local m = F.medals(last); return m.nohit and m.bones and m.par, "" end))
  add(key("escape"), state("menu", 1))

  -- pause: B never quits, QUIT asks first
  add(key("up"), key("space"), state("intro", 1), wait(0.6), key("space"), state("play", 1), wait(0.2), key("return"), state("pause", 1), wait(0.1), shot("7_pause"))
  add(key("lshift"), check("pause: B does nothing", function() return api.getState() == "pause", api.getState() end))
  add(key("escape"), check("pause: Esc (back) goes on playing", function() return api.getState() == "play", api.getState() end))
  -- SOUND (the second row): left / right change the game's volume, A steps it up; the volume buttons work anywhere
  add(key("return"), state("pause", 1), key("down"), { act = function() Se.volume = 8 end }, key("left"), key("left"),
    check("pause: SOUND left turns the volume down", function() return Se.volume == 6 and api.getState() == "pause", "volume " .. Se.volume end),
    key("right"), key("space"), check("pause: SOUND right and A turn it up", function() return Se.volume == 8, "volume " .. Se.volume end),
    key("volumedown"), check("volume button down: quieter, still paused", function() return Se.volume == 7 and api.getState() == "pause", "volume " .. Se.volume end),
    key("mute"), check("mute button: sound off", function() return Se.volume == 0, "volume " .. Se.volume end),
    key("mute"), check("mute button again: sound back", function() return Se.volume == 7, "volume " .. Se.volume end),
    wait(0.05), shot("u10_pause_sound"), key("escape"), state("play", 1))
  -- CONTROLS (the third row, step 3): the controls page over the level; B goes back to the pause
  add(key("return"), state("pause", 1), key("down"), key("down"), key("space"),
    check("pause: CONTROLS opens the controls page", function() return api.getState() == "pause" and api.pause().controls == true, tostring(api.pause().controls) end),
    shot("u14_pause_controls"), key("escape"),
    check("pause: B goes back from the controls page", function() return api.getState() == "pause" and not api.pause().controls, api.getState() end),
    key("escape"), state("play", 1))
  add(key("return"), state("pause", 1), key("down"), key("down"), key("down"), key("space"),
    check("pause: QUIT asks first", function() return api.getState() == "pause" and api.pause().confirm == 1, api.getState() end), shot("u7_pause"))
  add(key("space"), check("pause: NO keeps the game", function() return api.getState() == "pause" and not api.pause().confirm, api.getState() end))
  add(key("down"), key("space"), key("escape"), check("pause: back from the question", function() return api.getState() == "pause" and not api.pause().confirm, api.getState() end))
  add(key("down"), key("down"), key("down"), key("space"), key("down"), key("space"),
    check("pause: YES, QUIT goes to the menu", function() return api.getState() == "menu" and api.run() == nil, api.getState() end))

  -- GAME OVER: TRY AGAIN (the same level, 3 lives, the score it started with), then MENU
  add(key("space"), state("intro", 1), wait(0.6), key("space"), state("play", 1))
  add({ act = function() local s = api.stage(); s.score = s.score + 500; s.lives, s.hearts = 1, 1; s:loseHeart() end }, state("over", 1))
  add(key("space"), check("game over: no key for the first 1.2 s", function() return api.getState() == "over", api.getState() end))
  add(wait(1.4), shot("8_gameover"), shot("u5_over"), key("space"), state("intro", 1), check("game over: TRY AGAIN restarts the level", function()
    local st, r = stats(), api.run()                               -- (PLAY started the furthest open level: the last)
    return r and r.names[r.k] == names[#names] and st.lives == 3 and st.score == 0 and st.hearts == 3, ("%s, lives %d, score %d"):format(r and r.names[r.k] or "-", st.lives, st.score)
  end))
  add(wait(0.6), key("space"), state("play", 1))
  add({ act = function() local s = api.stage(); s.lives, s.hearts = 1, 1; s:loseHeart() end }, state("over", 1), wait(1.4), key("down"), key("space"),
    state("menu", 1), check("game over: MENU, unlocks kept", function()
    F.load(); local ok = api.getState() == "menu" and api.run() == nil
    for i, l in ipairs(F.levels) do if l.exists then ok = ok and F.isOpen(i) end end
    return ok, api.getState()
  end))

  -- OPTIONS (the menu's third item): SOUND, HARD MODE, CONTROLS; B goes back one screen at a time
  add(key("down"), key("down"), key("space"), state("options", 1), wait(0.2), shot("u12_options"),
    check("options: SOUND is selected", function() return F.opts.sel == 1, F.opts.items[F.opts.sel] end))
  add({ act = function() Se.volume = 5 end }, key("left"), check("options: SOUND left turns the volume down", function() return Se.volume == 4, "volume " .. Se.volume end),
    key("right"), key("right"), check("options: SOUND right turns it up", function() return Se.volume == 6, "volume " .. Se.volume end))
  add(key("down"), key("down"), key("space"), state("controls", 1), wait(0.2), shot("u13_controls"),
    check("options: CONTROLS opens the controls page", function() return api.getState() == "controls", api.getState() end))
  add(key("escape"), check("controls: B goes back to the options", function() return api.getState() == "options" and F.opts.sel == 3, api.getState() end))
  -- HARD MODE: the options' second row, saved; the stage gets it, says no hints, shows the tag
  add(key("up"), key("space"), check("hard mode: on and saved", function()
    return F.hard and readSave("hard.txt"):find("1") ~= nil, readSave("hard.txt"):gsub("\n", "") end), wait(0.2), shot("u8_menu"))
  add(key("escape"), check("options: B goes back to the menu", function() return api.getState() == "menu", api.getState() end))
  add(key("up"), key("up"), key("space"), state("intro", 1), wait(0.6), key("space"), state("play", 1), wait(0.5),
    check("hard mode: the stage is hard, no hints, no nudge", function()
      local s = api.stage(); return s.hard == true and s:hint() == nil and T.cur == nil, tostring(s.hard) end))
  add(wait(3.2), check("hard mode: no idle nudge", function() return T.nudge.btn == nil, tostring(T.nudge.btn) end), shot("u9_hard"))
  add(key("return"), state("pause", 1), key("down"), key("down"), key("down"), key("space"), key("down"), key("space"), state("menu", 1),
    key("down"), key("down"), key("space"), state("options", 1), key("down"), key("space"),
    check("hard mode: off again", function() return not F.hard and readSave("hard.txt"):find("0") ~= nil, "" end))

  -- the summary and the contact sheet (4 x 2, the screens at 2x)
  add(wait(0.2), { act = function()
    table.sort(shots, function(a, b) return a.name < b.name end)
    local keep = {}
    for _, s in ipairs(shots) do if s.name ~= "0_title" and s.name:match("^%d") then keep[#keep + 1] = s end end
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
