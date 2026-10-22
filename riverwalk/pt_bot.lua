-- Playtest lab, the persona layer (docs/playtest/method.md). It wraps the level's CURRENT autopilot (tests_<level>.lua,
-- the --auto step list) instead of copying its route: the autopilot still decides what to press and when, from the
-- real game state; this layer sits between its input stream (I.force, love.keypressed) and the game and turns the
-- perfect stream into a person's: reaction delays, timing spread (early and late), hold errors, controls that have
-- to be found first, failures, recovery (back up and try again, or back to the lamp), patience and quitting.
-- The game itself is untouched: it reads the persona's buttons through the same I.force the autopilots use.
local I = require("input")
local St = require("stage")
local Bot = {}

local DT = 1 / 60
local DEBUG = os.getenv("PT_DEBUG")
local DEBUG_N = tonumber(os.getenv("PT_DEBUG_N") or "")
local function copy(t) local o = {}; for k, v in pairs(t or {}) do o[k] = v end; return o end
local function same(a, b)
  for k, v in pairs(a) do if (b[k] and true) ~= (v and true) then return false end end
  for k, v in pairs(b) do if (a[k] and true) ~= (v and true) then return false end end
  return true
end
local function upvalue(fn, name)
  for k = 1, 255 do
    local n, v = debug.getupvalue(fn, k)
    if not n then return nil end
    if n == name then return k, v end
  end
end

-- texts that teach a control (same table in the analysis); a reader who reads one knows that control at once
local TEACH = {
  { "BIG JUMP", "heldjump" }, { "CLIMB", "heldjump" }, { "CRAWL", "crawl" }, { "DUCK", "crawl" }, { "BARK", "bark" },
  { "SHOO", "bark" }, { "PICK UP", "act" }, { "GIVE", "act" }, { "SNEAK", "sneak" }, { "SNIFF", "sniff" },
}
local MECH_BTN = { a = "heldjump", b = "sneak", x = "act", y = "bark", down = "crawl", l1 = "sniff" }

function Bot.new(api, persona, opts)
  local b = { api = api, P = persona, opts = opts, level = opts.level }
  local seed = opts.seed or 1
  local rng = love.math.newRandomGenerator(seed * 7919 + 17)
  local function rand() return rng:random() end
  local function gauss(sd) return rng:randomNormal(sd or 1, 0) end
  local function gamma2(mean) return -(mean / 2) * (math.log(1 - rand()) + math.log(1 - rand())) end
  local perfect = persona.perfect
  local probe = { spot = nil, n = 0, done = {} }              -- the clean try (route lost or not), see fail()
  local reaction = (persona.reaction_ms or 0) / 1000
  local sd = (persona.timing_sd_ms or 0) / 1000
  local holdErr = persona.hold_error or 0
  local patience = persona.patience or 99
  local cap = persona.session_s or ((persona.id == "elsa6") and 600 or 1200)
  local function words(s) local n = 0; for _ in s:gmatch("%S+") do n = n + 1 end; return n end
  local function canRead(text)
    if perfect then return true end
    if persona.reads == "all" then return true end
    if persona.reads == "short" then return words(text) <= 4 end
    return false
  end

  -- the autopilot's runner: its step list and its index, read and set through its upvalues
  local runner = love.update
  local iIdx = upvalue(runner, "i")
  local sinceIdx = upvalue(runner, "since")
  local _, steps = upvalue(runner, "steps")
  local oldIdx, old = upvalue(runner, "old")
  assert(iIdx and sinceIdx and steps and oldIdx, "playtest: the autopilot runner has an unexpected shape")
  for _, st in ipairs(steps) do if st.limit then st.limit = st.limit * 1.5 end end    -- a person gets 1.5x the time
  local function getI() local _, v = debug.getupvalue(runner, iIdx); return v end
  local function setI(v) debug.setupvalue(runner, iIdx, v); debug.setupvalue(runner, sinceIdx, 0) end
  local function getSince() local _, v = debug.getupvalue(runner, sinceIdx); return v end
  local function nparams(f) local ok, info = pcall(debug.getinfo, f, "u"); return ok and info.nparams or 2 end

  -- the input split: D = what the autopilot wants (it reads and writes I.force), A = what the persona presses
  -- (the game reads I.force only inside the game step, and then gets A)
  local D, A, Aforce = copy(I.force), {}, {}
  local inGame = false
  rawset(I, "force", nil)
  setmetatable(I, {
    __index = function(_, k) if k == "force" then return inGame and A or D end end,
    __newindex = function(t, k, v) if k == "force" then D = v or {} else rawset(t, k, v) end end,
  })
  local origKey = love.keypressed
  local inRunner, pressesNow = false, {}
  love.keypressed = function(k, sc)
    if inRunner then pressesNow[#pressesNow + 1] = k else origKey(k, sc) end
  end
  local quitReq = false
  b.realQuit = love.event.quit
  love.event.quit = function() if inRunner then quitReq = true else b.realQuit() end end
  local realStageFn = api.stage
  local function S() return realStageFn() end

  -- early presses: the autopilot looks at where Pepper will be `la` seconds from now (x + vx * la)
  local la = 0
  local proxyFor = setmetatable({}, { __mode = "k" })
  api.stage = function()
    local s = realStageFn()
    if la <= 0 or not s or inGame then return s end
    local px = proxyFor[s]
    if not px then
      local p = s.pepper
      local pp = setmetatable({}, { __index = function(_, k) local q = s.pepper
          if k == "x" then return q.x + q.vx * la end; return q[k] end,
        __newindex = function(_, k, v) s.pepper[k] = v end })
      px = setmetatable({}, { __index = function(_, k) if k == "pepper" then return pp end; return s[k] end,
        __newindex = function(_, k, v) s[k] = v end })
      proxyFor[s] = px
      local _ = p
    end
    return px
  end

  -- what the game did (watched, never changed): hearts, lives, respawns
  local log = { fails = {}, failCount = {}, discover = {}, stall = {}, spotPos = {}, hearts = 0, lives = 0, gameovers = 0,
                waits = 0, waitN = 0, readHints = {} }
  b.log = log
  local respawned, myRespawn = false, false
  local origRespawn, origLose = St.respawn, St.loseHeart
  St.respawn = function(self, ...) if not myRespawn then respawned = true end; return origRespawn(self, ...) end
  St.loseHeart = function(self, ...) log.hearts = log.hearts + 1; return origLose(self, ...) end

  -- knowledge: what the persona knows; the texts it could read teach
  local known = {}
  if perfect then for _, m in pairs(MECH_BTN) do known[m] = true end end
  local function teach(text, t)
    if not text or not canRead(text) then return end
    local up = text:upper()
    for _, tk in ipairs(TEACH) do
      if up:find(tk[1], 1, true) and not known[tk[2]] then known[tk[2]] = true; log.discover[#log.discover + 1] = { mech = tk[2], how = "read", t = t, dur = 0 } end
    end
  end

  -- the queue of the persona's actions: { at = qclock time, force = snapshot } or { at, key }
  local queue, qclock, lastAt, curLag = {}, 0, 0, 0
  local e = 0                                                     -- the current step's timing error (s; < 0 = early)
  local function newE() if perfect then e = 0 else e = gauss(sd) end; la = (e < 0) and -e or 0 end
  newE()
  local lastD = copy(D)
  local jp                                                        -- the last jump press (hold errors)
  local frame, T, playT = 0, 0, 0
  local mode, modeT, modeData = "run", 0, nil                     -- run | discover | walkback | lampwait | fetch
  local entries = {}                                              -- step -> { x, y, force, carrying } at first entry
  local maxStep, failStepNow = 1, nil
  local heldPending = false                                        -- a held jump came out short for want of knowing it
  local lastPos, stillT, idleT = nil, 0, 0
  b.done, b.result = false, nil

  local function enqueue(ev, lag)
    local at = math.max(qclock + lag, lastAt); lastAt = at; ev.at = at
    queue[#queue + 1] = ev
  end
  local function stallAdd(kind, s)
    local p = s.pepper
    local key = ("%d,%d"):format(math.floor(p.x / 32), math.floor(p.y / 32))
    local c = log.stall[key] or { 0, 0, 0, 0 }; log.stall[key] = c
    local slot = ({ wait = 1, discover = 2, recover = 3, still = 4 })[kind] or 4
    c[slot] = c[slot] + DT
  end
  local function spotOf(i)
    local en = entries[i] or entries[maxStep] or { x = 0, y = 0 }
    log.spotPos[tostring(i)] = { math.floor(en.x), math.floor(en.y) }
    return tostring(i)
  end
  local function finish(result, extra)
    if b.done then return end
    b.done, b.result = true, result
    if result == "clear" or result == "quit" or result == "session" then end
    local s = S()
    local st = s and s:stats() or {}
    b.summary = { persona = persona.id, group = persona.group, level = opts.level, route = opts.route, seed = seed,
      result = result, play_time = playT, clear_time = b.clearPT, total_time = T, hearts_lost = log.hearts, lives_lost = log.lives, gameovers = log.gameovers,
      bones = st.bones, bones_total = st.total, secrets = st.secrets or 0, secrets_total = st.secretsTotal or 0,
      fails = log.fails, discover = log.discover, waits = log.waits, stall = log.stall, spot_pos = log.spotPos,
      quit_spot = extra and extra.spot, probes = (function() local n = 0; for _ in pairs(probe.done) do n = n + 1 end; return n end)(), quit_xy = extra and extra.xy, max_step = maxStep, steps_total = #steps }
  end
  -- a failure at the step the autopilot is on: counted; at `patience` failures at one spot the persona quits there
  local function fail(cause, s)
    local i = getI()
    local spot = spotOf(i)
    local p = s.pepper
    log.fails[#log.fails + 1] = { spot = spot, cause = cause, x = math.floor(p.x), y = math.floor(p.y), t = playT }
    log.failCount[spot] = (log.failCount[spot] or 0) + 1
    -- the lab's own check: after 3 failures in a row at one spot, one try with the autopilot's exact inputs. If
    -- that fails too, the bot (not the player) has lost the route here (the ball or a critter is somewhere the
    -- route does not expect): the run ends as "lost" and is left out of the difficulty numbers.
    if probe.active then
      probe.active = false; perfect = persona.perfect
      if probe.spot == spot then finish("lost", { spot = spot, xy = { math.floor(p.x), math.floor(p.y) } }); return true end
    end
    if probe.spot == spot then probe.n = probe.n + 1 else probe.spot, probe.n = spot, 1 end
    if not persona.perfect and probe.n >= 3 and not probe.done[spot] and log.failCount[spot] < patience then
      probe.done[spot] = true; probe.active = true; perfect = true
    end
    if not persona.perfect and log.failCount[spot] >= patience then
      finish("quit", { spot = spot, xy = { math.floor(p.x), math.floor(p.y) } }); return true
    end
    return false
  end
  -- where to pick the route up again: a step before the failing one, first entered closest to where Pepper stands
  -- (with the ball in her mouth or not, as then); on a tie the later one
  local function pickEntry(p, maxI, carrying, sameFloor)
    local best, bd
    for k = 1, maxI do
      local en = entries[k]
      if en and en.play and (not sameFloor or (en.ground and math.abs(en.y - p.y) < 12 and math.abs(en.x - p.x) < 200)) then
        local d = math.abs(en.x - p.x) + 1.5 * math.abs(en.y - p.y) + ((en.carrying ~= carrying) and 2000 or 0)
        if not bd or d <= bd then best, bd = k, d end
      end
    end
    return best
  end
  local function resumeAt(k)
    queue, lastAt = {}, qclock
    D = copy(entries[k] and entries[k].force or {}); lastD = copy(D)
    Aforce = copy(D); jp = nil
    setI(k); newE(); curLag = 0
    mode, modeData = "run", nil
  end
  -- go to where step k was first entered (on foot, on the same floor), then go on from there
  local function goTo(k)
    local en, p = entries[k], S().pepper
    if en and en.ground and math.abs(en.y - p.y) < 12 and math.abs(en.x - p.x) > 6 then
      mode, modeT, modeData = "walkback", 0, { k = k, x = en.x, blockT = 0 }
    else resumeAt(k) end
  end
  local function startDiscover(mech, then_)
    local dur = gamma2(persona.discovery_s or 10)
    mode, modeT, modeData = "discover", 0, { mech = mech, dur = dur, after = then_ }
    log.discover[#log.discover + 1] = { mech = mech, how = "tried", t = playT, dur = dur }
  end
  -- after a failure: back up on foot to a step before it on the same floor, else back to the last lamp (the
  -- game's own respawn, plus the time to walk back); the game's own respawns (water, a fall, a life) go to the lamp
  local function recover(s, fromGame)
    local p = s.pepper
    local fi = getI()
    local after
    if fromGame then
      after = function() mode, modeT, modeData = "lampwait", 0, { fi = fi } end
    else
      local k                                                     -- the latest step on this floor with a run-up (40 px)
      local ef = entries[fi] or { x = p.x, y = p.y }
      for kk = fi - 1, 1, -1 do
        local en = entries[kk]
        if en and en.play and en.ground and math.abs(en.y - p.y) < 12 and math.abs(en.x - p.x) < 240
           and math.abs(en.x - ef.x) + math.abs(en.y - ef.y) >= 40 and en.carrying == (p.carrying ~= nil) then k = kk; break end
      end
      if k then after = function() goTo(k) end
      else after = function()
          local cx, cy = p.x, p.y
          myRespawn = true; s:respawn(); myRespawn = false
          local walk = math.min(6, math.max(1, (math.abs(cx - p.x) + math.abs(cy - p.y)) / 120))
          mode, modeT, modeData = "lampwait", 0, { wait = walk, fi = fi }
        end end
    end
    if heldPending and not known.heldjump then heldPending = false; startDiscover("heldjump", after) else after() end
  end

  -- one game step (the autopilot's runner calls this as its `old`)
  local function gameStep(dt)
    local s = S()
    -- the persona's actions that are due
    if mode == "run" then
      while queue[1] and queue[1].at <= qclock + 1e-9 do
        local ev = table.remove(queue, 1)
        if ev.force then
          if jp and jp.extUntil == nil and Aforce.jump and not ev.force.jump and (T - jp.t) <= 4 * DT and jp.err then
            jp.extUntil = jp.t + 0.3 + 0.15 * rand()                -- a tap held too long
          end
          Aforce = copy(ev.force)
          if not Aforce.jump and jp then jp.cut = false end
        elseif ev.key then
          if ev.key == "space" then jp = { t = T, err = (not perfect) and rand() < holdErr, cutAt = 0.06 + 0.1 * rand() } end
          inGame = true; origKey(ev.key); inGame = false
        end
      end
    end
    A = copy(mode == "run" and Aforce or (modeData and modeData.hold) or {})
    if jp and mode == "run" then
      local held = T - jp.t
      if Aforce.jump and not jp.cut and held >= jp.cutAt and held < jp.cutAt + DT * 1.5 and (jp.err or not known.heldjump) then
        jp.cut = true                                              -- a held jump let go early: a hop
        if not known.heldjump and not perfect then heldPending = true end
      end
      if jp.cut then A.jump = nil end
      if jp.extUntil and T < jp.extUntil then A.jump = true end
    end
    inGame = true; old(dt); inGame = false
  end
  debug.setupvalue(runner, oldIdx, gameStep)

  -- every frame (playtest.lua calls this instead of love.update)
  function b.tick()
    if b.done then return end
    frame = frame + 1; T = T + DT
    local s = S()
    local state = api.getState()
    local p = s and s.pepper
    if state == "play" then playT = playT + DT end
    if state == "clear" then finish("clear"); return end
    if s and s.clearT and not b.clearPT then b.clearPT = playT end
    if T > cap + 60 or playT > cap then finish("session", { spot = spotOf(getI()), xy = p and { math.floor(p.x), math.floor(p.y) } }); return end
    if state == "over" then                                         -- GAME OVER: TRY AGAIN, the level from the start
      log.gameovers = log.gameovers + 1
      if fail("gameover", s) then return end
      api.newRun(); queue, lastAt = {}, qclock; D, Aforce, jp = {}, {}, nil; setI(1); mode = "run"
      return
    end
    -- texts on screen: a reader learns the controls they name
    if state == "play" and s then
      local h = s:hint()
      if h and h.text and not log.readHints[h.text] then log.readHints[h.text] = true; teach(h.text, playT) end
    end
    local livesBefore = s and s.lives
    if p and p.onGround and math.abs(p.vx) < 1 then idleT = idleT + DT else idleT = 0 end
    if mode == "run" then
      local iBefore, sinceBefore = getI(), getSince()
      inRunner = true; pressesNow = {}; quitReq = false
      runner(DT)
      inRunner = false
      s = S(); p = s and s.pepper
      local iAfter = getI()
      if not D then D = {} end
      -- the actions the autopilot took this frame, through the persona
      local changed = not same(D, lastD)
      if changed or #pressesNow > 0 then
        local st = steps[iBefore] or {}
        local lag
        local waited = (sinceBefore or 0) + DT
        if perfect then lag = 0
        elseif st.cond and (st.limit or 0) >= 100 then lag = math.max(0, e)       -- a reactive autopilot (Soder Hill): per press
        elseif st.cond and nparams(st.cond) >= 2 and idleT >= 0.3 then lag = math.max(0.05, reaction + gauss(sd))   -- standing, waiting for the world: a reaction
        elseif st.cond and nparams(st.cond) >= 1 then                                  -- a place on the route: early or late
          local release = #pressesNow == 0
          for k in pairs(D) do if not lastD[k] then release = false end end
          lag = release and 0 or math.max(0, e)                                        -- (people stop short, not late)
        else lag = curLag end                                                          -- the rest of the same action
        curLag = lag
        -- controls the persona does not know yet: find them first (trying buttons for a while)
        local need
        for _, k in ipairs(pressesNow) do
          if k == "z" and not known.bark then need = "bark" elseif k == "x" and not known.act and state == "play" then need = "act" end
        end
        if D.walk and not lastD.walk and not known.sneak then need = "sneak" end
        if D.sniff and not lastD.sniff and not known.sniff then need = "sniff" end
        if D.down and not lastD.down and not known.crawl and p and p.onGround then need = need or "crawl" end
        if state == "play" and need and not perfect then
          for _, k in ipairs(pressesNow) do enqueue({ key = k }, lag) end
          if changed then enqueue({ force = copy(D) }, lag) end
          startDiscover(need, function() mode = "run" end)
        else
          if changed then enqueue({ force = copy(D) }, lag) end
          for _, k in ipairs(pressesNow) do enqueue({ key = k }, lag) end
        end
        lastD = copy(D)
        if (st.limit or 0) >= 100 and #pressesNow > 0 then newE() end
      end
      if iAfter ~= iBefore then
        if probe.active and iAfter > tonumber(probe.spot) + 1 then probe.active = false; perfect = persona.perfect end
        newE()
        if not entries[iAfter] and p then
          entries[iAfter] = { x = p.x, y = p.y, force = copy(D), carrying = p.carrying ~= nil, play = state == "play", ground = p.onGround }
        end
        if iAfter > maxStep then maxStep = iAfter end
      end
      if quitReq and not b.done then                            -- the autopilot is stuck: the persona failed here
        if persona.perfect then finish("stuck", { spot = spotOf(getI()), xy = { math.floor(p.x), math.floor(p.y) } }); return end
        if fail("stuck", s) then return end
        recover(s, false)
      end
      qclock = qclock + DT
    else
      -- the bot is busy (finding a control, backing up, at the lamp, fetching the ball): the game goes on
      modeT = modeT + DT
      if mode == "discover" then
        stallAdd("discover", s)
        if modeT >= modeData.dur then known[modeData.mech] = true; local f = modeData.after; modeData = nil; f() end
      elseif mode == "walkback" then
        stallAdd("recover", s)
        local dx = modeData.x - p.x
        if math.abs(dx) < 6 or modeT > 6 then
          if p.onGround then modeData.hold = {}; if math.abs(p.vx) < 1 then resumeAt(modeData.k) end end
        else
          modeData.hold = { [dx > 0 and "right" or "left"] = true }
          if p.onGround and math.abs(p.vx) < 1 then modeData.blockT = modeData.blockT + DT else modeData.blockT = 0 end
          if modeData.blockT > 0.25 then modeData.blockT = 0; modeData.hold.jump = true; origKey("space") end   -- in the way: hop over
        end
      elseif mode == "lampwait" then
        stallAdd("recover", s)
        local busy = (s.deadT or s.drownT or s.fallT or (s.ballBackT and s.ballBackT > 0)) and modeT < 5
        if not busy and modeT >= ((modeData and modeData.wait) or 1.3) then
          local ball = s.ball
          if not p.carrying and ball and (ball.state == "rest" or ball.state == "home") and math.abs(ball.x - p.x) < 160 and math.abs(ball.y - p.y) < 40
             and (entries[maxStep] and entries[maxStep].carrying) then
            mode, modeT, modeData = "fetch", 0, { fi = modeData and modeData.fi }
          else
            local fi = modeData and modeData.fi or maxStep
            goTo(pickEntry(p, math.max(1, fi - 1), p.carrying ~= nil, false) or fi)
          end
        end
      elseif mode == "fetch" then
        stallAdd("recover", s)
        local ball = s.ball
        if p.carrying or modeT > 8 or ball.state ~= "rest" and modeT > 3 then
          goTo(pickEntry(p, maxStep, p.carrying ~= nil, false) or maxStep)
        else
          local tx = ball.x - p.face * 18
          if math.abs(p.x + p.face * 18 - ball.x) < 14 and math.abs(p.vx) < 1 then
            modeData.hold = {}
            if (modeData.pt or 0) <= 0 then origKey("x"); modeData.pt = 0.5 else modeData.pt = modeData.pt - DT end
          else
            local dir = (ball.x > p.x) and "right" or "left"
            modeData.hold = { [dir] = true, walk = true }; local _ = tx
          end
        end
      end
      gameStep(DT)
    end
    s = S(); p = s and s.pepper
    if not s or b.done then return end
    if DEBUG and frame % (DEBUG_N or 30) == 0 then io.stderr:write(("f%d %s i%d x%.0f y%.0f vx%.0f %s D[%s] A[%s] q%d\n"):format(frame, mode, getI(), p.x, p.y, p.vx,
      p.onGround and "G" or "a", table.concat((function() local o = {}; for k in pairs(D) do o[#o + 1] = k end; return o end)(), ","),
      table.concat((function() local o = {}; for k in pairs(A) do o[#o + 1] = k end; return o end)(), ","), #queue)) end
    if livesBefore and s.lives < livesBefore then log.lives = log.lives + (livesBefore - s.lives) end
    -- the game sent Pepper back to the lamp (water, a fall, a life, TIME UP): a failure here, then recover
    if respawned then
      respawned = false
      if mode ~= "run" then queue = {} end
      if not persona.perfect then
        if fail("respawn", s) then return end
        recover(s, true)
      end
    end
    -- forced waiting: the autopilot holds nothing and Pepper stands (a boat, a tram, a lift, a hazard)
    if mode == "run" and state == "play" and p then
      local idle = not (D.left or D.right or D.down or D.jump) and math.abs(p.vx) < 1 and p.onGround
      if idle then log.waitN = log.waitN + DT else
        if log.waitN >= 1 then log.waits = log.waits + log.waitN end; log.waitN = 0 end
      if idle and log.waitN >= 1 then stallAdd("wait", s) end
      -- a stall: Pepper has not moved 8 px in 2 s while the route goes on
      if lastPos and math.abs(p.x - lastPos[1]) + math.abs(p.y - lastPos[2]) < 0.2 and not idle then stillT = stillT + DT else stillT = 0 end
      if stillT > 1 then stallAdd("still", s) end
      lastPos = { p.x, p.y }
    end
  end
  return b
end
return Bot
