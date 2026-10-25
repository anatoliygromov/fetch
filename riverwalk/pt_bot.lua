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
  if os.getenv("PT_STEPS") then
    for k, st in ipairs(steps) do
      local f = st.cond or st.act
      io.stderr:write(("step %d %s line %s\n"):format(k, st.wait and ("wait " .. st.wait) or (st.cond and "cond" or "act"), f and debug.getinfo(f, "S").linedefined or "-"))
    end
  end
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
  -- learning across levels (whole-game mode): opts.carry.known = the controls found on earlier levels of this
  -- playthrough (known from the start, no trying time again); opts.carry.seen = the controls whose button glyph was on
  -- screen in a hint (seen, or read without knowing the control): their trying time is halved
  local carry = opts.carry or {}
  local known, seen = {}, {}
  for m in pairs(carry.known or {}) do known[m] = true end
  for m, f in pairs(carry.seen or {}) do seen[m] = f end
  if perfect then for _, m in pairs(MECH_BTN) do known[m] = true end end
  local function teach(text, t, btn)
    if not text then return end
    local bm = btn and MECH_BTN[btn]
    if bm and not known[bm] then seen[bm] = 0.5 end                -- the glyph names the button: trying is shorter
    if not canRead(text) then return end
    local up = text:upper()
    for _, tk in ipairs(TEACH) do
      if up:find(tk[1], 1, true) and not known[tk[2]] then known[tk[2]] = true; log.discover[#log.discover + 1] = { mech = tk[2], how = "read", t = t, dur = 0 } end
    end
  end
  b.known, b.seen = known, seen
  -- the run's lives and score carried over from the level before (as St.new(def, carry) does in the real flow)
  local carryScore = carry.score or 0
  local function applyCarry(lives)
    local s0 = S()
    if s0 and (carry.lives or carry.score) then s0.lives = lives; s0.score = carryScore; s0.startScore = carryScore end
  end
  applyCarry(carry.lives or 3)

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
  local offT, offN = 0, {}
  b.done, b.result = false, nil

  -- the world's state as the route sees it (recovery v2): the ball (in her mouth, with a critter, loose, given) and
  -- the critters that hold it (the magpie's perch while it has the ball, the fox's hideout and whether it was sniffed
  -- out there, the cat sitting or not)
  local function sig(s)
    local p, bl = s.pepper, s.ball
    local bs = p.carrying and "held" or (bl.state == "given" and "given")
      or ((bl.state == "magpie" or bl.state == "cat" or bl.state == "fox") and bl.state) or "loose"
    local m = (s.magpie and bl.state == "magpie") and s.magpie.i or 0
    local f = (s.night and s.night.fox) and (s.night.fox.i * 2 + (s.night.fox.found and 1 or 0)) or 0   -- (found: sniffed out)
    local c = s.cat and (s.cat.state == "sit" and 1 or 0) or 0
    return ("%s|%d|%d|%d"):format(bs, m, f, c)
  end
  b.sig = sig
  local route = opts.routeMap                                     -- the clean run's step entries (recovery v2), or nil
  local function onMover(p) for _, m in ipairs(S().movers or {}) do if p.ground == m then return true end end; return false end
  -- the perfect run records where each step is first entered: the map recovery picks the route up from
  local routeOut = persona.perfect and {} or nil
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
    local kn = {}; for m in pairs(known) do kn[m] = true end
    local se = {}; for m, f in pairs(seen) do if not known[m] then se[m] = f end end
    local tl = b.api.tally and b.api.tally()
    local carryOut = { known = kn, seen = se }
    if result == "clear" then carryOut.lives = st.lives; carryOut.score = (tl and tl.score) or ((st.score or 0) + math.max(0, math.floor(st.time or 0)) * 10) end
    b.summary = { persona = persona.id, carry_in = { lives = carry.lives, score = carry.score }, carry_out = carryOut, group = persona.group, level = opts.level, route = opts.route, seed = seed,
      result = result, play_time = playT, clear_time = b.clearPT, total_time = T, hearts_lost = log.hearts, lives_lost = log.lives, gameovers = log.gameovers,
      bones = st.bones, bones_total = st.total, secrets = st.secrets or 0, secrets_total = st.secretsTotal or 0,
      fails = log.fails, discover = log.discover, waits = log.waits, stall = log.stall, spot_pos = log.spotPos,
      route = routeOut and (function() local o = {}; for k = 1, #steps do if routeOut[k] then o[#o + 1] = routeOut[k] end end; return o end)() or nil,
      resumes = log.resumes or 0, lab_walks = log.lab_walks or 0, lab_walk_s = log.lab_walk_s or 0, offroute = log.offroute or 0, recovery = route and "v2" or "v1",
      quit_spot = extra and extra.spot, probes = (function() local n = 0; for _ in pairs(probe.done) do n = n + 1 end; return n end)(), quit_xy = extra and extra.xy, max_step = maxStep, steps_total = #steps }
  end
  -- a failure at the step the autopilot is on: counted; at `patience` failures at one spot the persona quits there
  local function fail(cause, s)
    local i = getI()
    local spot = spotOf(i)
    local p = s.pepper
    if steps[i] and (steps[i].limit or 0) >= 100 then             -- a reactive autopilot (one step): the spot is the screen
      spot = ("%s@%d"):format(spot, math.floor(p.x / 320)); log.spotPos[spot] = { math.floor(p.x), math.floor(p.y) }
    end
    log.fails[#log.fails + 1] = { spot = spot, cause = cause, x = math.floor(p.x), y = math.floor(p.y), t = playT }
    log.failCount[spot] = (log.failCount[spot] or 0) + 1
    -- the lab's own check: after 3 failures in a row at one spot, one try with the autopilot's exact inputs. If
    -- that fails too, the bot (not the player) has lost the route here (the ball or a critter is somewhere the
    -- route does not expect): the run ends as "lost" and is left out of the difficulty numbers.
    if probe.active then
      probe.active = false; perfect = persona.perfect
      -- (with recovery v2 only a stuck or an offroute proves the route lost; the game's hazards end the try unproven)
      if probe.spot == spot and (not route or cause == "stuck" or cause == "offroute") then
        finish("lost", { spot = spot, xy = { math.floor(p.x), math.floor(p.y) } }); return true
      elseif route then probe.done[spot] = nil; probe.n = 0 end
    end
    if probe.spot == spot then probe.n = probe.n + 1 else probe.spot, probe.n, probe.step = spot, 1, i end
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
  local fetchFails = 0
  local function resumeAt(k)
    fetchFails = 0
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
    local dur = gamma2(persona.discovery_s or 10) * (seen[mech] or 1)
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

  -- recovery v2 (with the clean run's route map): pick the route up from the step whose clean entry matches where
  -- Pepper stands now and what the world looks like (sig: the ball, the magpie, the fox, the cat). Order of tries:
  --   1. the ball lies loose within 480 px (and 64 px up or down): fetch it (walk, hop, X), then plan again;
  --   2. the magpie still has the ball on a perch the clean run never saw it on: sneak up to it, bark, plan again;
  --   3. a step on the same floor (|dy| < 10, within 480 px) with the same sig: the nearest one at or behind her
  --      (a 32 px run-up when the clean run was moving there), else the nearest one ahead; walk there and go on;
  --   4. none on her floor: she walks to the nearest step with the same sig anywhere (the lab moves her there with
  --      the game's own respawn and she stands for the walk, distance / 120 px/s, at most 20 s: lab_walks);
  --   5. still none: the step with the nearest entry anywhere, from where she stands (the old way).
  -- Pepper on a boat, a lift or in the air: wait (up to 3 s) until she stands on solid ground.
  local plan
  local lastCause = "stuck"
  local function planned(k, runup, tries)
    local en, p = route[k], S().pepper
    local f = {}; for _, kk in ipairs(en.f or {}) do f[kk] = true end
    entries[k] = entries[k] or { x = en.x, y = en.y, force = f, carrying = en.c, play = true, ground = en.g }
    entries[k].force = f                                           -- resume with the clean run's buttons there
    log.resumes = (log.resumes or 0) + 1
    -- (night/25oct-lab) the run-up (up to 32 px back) stays on the floor the step starts from: never past its edge.
    -- City Park tall's ash branch ends 11 px behind step 71, so the full run-up walked Pepper off it onto the ledge
    -- below, the step ran her off that and down to the low road, every retry: 14 of 160 runs were lost there.
    local dir, back, w = (en.vx or 0) >= 0 and 1 or -1, 0, S().world
    if runup then
      for d = 4, 32, 4 do
        local x = en.x - dir * d
        if not w:floor(x - 1, x + 1, x, en.y - 2, en.y + 2, en.y - 2) then break end
        back = d
      end
    end
    local tx = en.x - dir * back
    if math.abs(tx - p.x) > 6 and (tries or 0) < 2 then
      mode, modeT, modeData = "walkback", 0, { k = k, x = tx, blockT = 0, v2 = true, y = p.y, tries = tries or 0 }
    else resumeAt(k) end
  end
  -- a step can be picked up from where the clean run stood on solid ground, not on a boat or lift, and was not in
  -- the middle of an action (holding A, or a button pressed as the step began: a press cannot be replayed), and was
  -- not coasting (running fast with no direction held)
  local function usable(en)
    if not (en.play and en.g and not en.mv and not en.pk and not en.bad) then return false end
    local dir = false
    for _, k in ipairs(en.f or {}) do if k == "jump" then return false end; if k == "left" or k == "right" then dir = true end end
    if math.abs(en.vx or 0) > 60 and not dir then return false end -- coasting on the clean run's speed: no button to replay it
    return true
  end
  -- matching a step's clean sig against the world now: the ball and the fox and the cat must be as then; the magpie
  -- (it has the ball) may be further along its perches than the step saw it (City Park tall: it flees ahead of her)
  local function parse(sg) local a, m, f, c = sg:match("^(%a+)|(%d+)|(%d+)|(%d+)$"); return a, tonumber(m), tonumber(f), tonumber(c) end
  local seenPerch = {}
  for _, en in pairs(route or {}) do local a, m = parse(en.sig); if a == "magpie" then seenPerch[m] = true end end
  local function sigOk(esig, cur)
    if esig == cur then return true end
    local a1, m1, f1, c1 = parse(esig); local a2, m2, f2, c2 = parse(cur)
    return a1 == "magpie" and a2 == "magpie" and f1 == f2 and c1 == c2 and m1 <= m2 and seenPerch[m2]
  end
  local function candidates(p, cur, needSig)
    local same, ahead = nil, nil
    local bestB, bestA
    for k, en in pairs(route) do
      if usable(en) and (not needSig or sigOk(en.sig, cur)) and math.abs(en.y - p.y) < 10 and math.abs(en.x - p.x) < 480 then
        local dx = en.x - p.x
        if dx <= 4 then
          local key = -dx * 1000 - k                                  -- nearest behind; on a tie the later step
          if not bestB or key < bestB then bestB, same = key, k end
        else
          local key = dx * 1000 - k
          if not bestA or key < bestA then bestA, ahead = key, k end
        end
      end
    end
    return same, ahead
  end
  plan = function(tries, cause)
    tries = tries or 0
    cause = cause or lastCause
    local s = S(); local p, bl = s.pepper, s.ball
    if (not p.onGround or onMover(p) or p.mode ~= "normal") and tries < 3 then
      mode, modeT, modeData = "settle", 0, { tries = tries }; return
    end
    local ci = getI()
    if steps[ci] and (steps[ci].limit or 0) >= 100 then resumeAt(ci); return end   -- a reactive autopilot (Soder Hill) picks itself up
    local cur = sig(s)
    local same, ahead = candidates(p, cur, true)
    -- 1. the ball lies loose and the route expects it in her mouth here (or it is nearer than the loose steps)
    if cur:sub(1, 5) == "loose" and (bl.state == "rest" or bl.state == "home") and fetchFails < 2 then
      local nearest = same and math.abs(route[same].x - p.x) or (ahead and math.abs(route[ahead].x - p.x)) or 1e9
      if math.abs(bl.x - p.x) < 480 and math.abs(bl.y - p.y) < 64 then local _ = nearest
        mode, modeT, modeData = "fetch", 0, { v2 = true, tries = tries }; return
      end
    end
    -- 2. the magpie has the ball on a perch no step expects
    if cur:sub(1, 6) == "magpie" and not seenPerch[s.magpie and s.magpie.i or 0] and s.magpie and s.magpie.state == "perch" then
      mode, modeT, modeData = "magpie", 0, { tries = tries }; return
    end
    -- 3. a step on her floor
    -- after a stuck: back up (the nearest step at or behind her, a run-up); after going off the route or a respawn:
    -- the nearest step either way (one ahead counts 1.5 times its distance)
    if same and ahead and cause ~= "stuck" and 1.5 * math.abs(route[ahead].x - p.x) < math.abs(route[same].x - p.x) then same = nil end
    if same then planned(same, math.abs(route[same].vx or 0) > 60, tries); return end
    if ahead then planned(ahead, false, tries); return end
    -- 4a. the ball lies loose somewhere else (it went home after a fall): she walks back to it, then fetches it
    if cur:sub(1, 5) == "loose" and (bl.state == "rest" or bl.state == "home") and fetchFails < 2 and tries < 3 then
      local walk = math.min(20, (math.abs(bl.x - p.x) + math.abs(bl.y - p.y)) / 120)
      if bl.state == "home" and bl.home then bl = { x = bl.home.x, y = bl.home.y } end
      local ck = s.check; s.check = { x = bl.x, y = bl.y }
      myRespawn = true; s:respawn(); myRespawn = false; s.check = ck
      log.lab_walks = (log.lab_walks or 0) + 1; log.lab_walk_s = (log.lab_walk_s or 0) + walk
      mode, modeT, modeData = "settle", 0, { tries = tries + 1, wait = math.max(0.3, walk) }; return
    end
    -- 4. none on her floor: she walks there (the lab puts her at that step's spot with the game's own respawn, and
    --    she stands for the walk: distance / 120 px/s, at most 20 s; the risks on the way are not played)
    local best, bd
    for _, need in ipairs({ "sig", "near", "ball", "any" }) do
      for k, en in pairs(route) do
        if usable(en) and ((need == "any") or (need == "sig" and en.sig == cur) or (need == "near" and sigOk(en.sig, cur))
                           or (need == "ball" and en.c == (p.carrying ~= nil))) then
          local d = math.abs(en.x - p.x) + 3 * math.abs(en.y - p.y) - k * 0.01
          if not bd or d < bd then best, bd = k, d end
        end
      end
      if best then break end
    end
    if best and tries < 3 then
      local en = route[best]
      local walk = math.min(20, (math.abs(en.x - p.x) + math.abs(en.y - p.y)) / 120)
      local ck = s.check; s.check = { x = en.x, y = en.y }
      myRespawn = true; s:respawn(); myRespawn = false; s.check = ck
      log.lab_walks = (log.lab_walks or 0) + 1; log.lab_walk_s = (log.lab_walk_s or 0) + walk
      mode, modeT, modeData = "settle", 0, { tries = tries + 1, wait = math.max(0.3, walk) }; return
    end
    -- 5. the nearest step anywhere, from where she stands (the old way)
    planned(best or 1, false, 3)
  end
  if route then
    -- the v2 recovery replaces the old one (same entry points: after a failure, and after the game's respawn)
    local oldRecover = recover
    recover = function(s, fromGame, cause)
      lastCause = fromGame and "respawn" or cause or "stuck"
      local after = function()
        if fromGame then mode, modeT, modeData = "settle", 0, { tries = 0, wait = 1.3 } else plan(0) end
      end
      if heldPending and not known.heldjump then heldPending = false; startDiscover("heldjump", after) else after() end
      local _ = oldRecover
    end
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
          if DEBUG then io.stderr:write(("  key %s at f%d x%.0f y%.0f %s\n"):format(ev.key, frame, S().pepper.x, S().pepper.y, S().pepper.onGround and "G" or "a")) end
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
      api.newRun(); applyCarry(3)                                 -- TRY AGAIN: 3 lives, the score the level started with
      queue, lastAt = {}, qclock; D, Aforce, jp = {}, {}, nil; setI(1); mode = "run"
      return
    end
    -- texts on screen: a reader learns the controls they name
    if state == "play" and s then
      local h = s:hint()
      if h and h.text and not log.readHints[h.text] then log.readHints[h.text] = true; teach(h.text, playT, h.btn) end
    end
    local livesBefore = s and s.lives
    if p and p.onGround and math.abs(p.vx) < 1 then idleT = idleT + DT else idleT = 0 end
    if mode == "run" then
      local iBefore, sinceBefore = getI(), getSince()
      inRunner = true; pressesNow = {}; quitReq = false
      local okRun = pcall(runner, DT)
      inRunner = false
      if not okRun then                                           -- (v2) a step picked up without the step before it that
        if route and route[iBefore] then route[iBefore].bad = true end   -- set it up (Rooftops' vent rides): never again
        if route and route[getI()] then route[getI()].bad = true end
        quitReq = true
      end
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
      if routeOut and p then                                       -- the clean run: where each step ran (x range, lowest floor)
        local ro = routeOut[iAfter]
        if ro then
          ro.xlo = math.min(ro.xlo or p.x, math.floor(p.x)); ro.xhi = math.max(ro.xhi or p.x, math.ceil(p.x))
          if p.onGround and not onMover(p) then ro.ymax = math.max(ro.ymax or p.y, math.ceil(p.y)) end
        end
      end
      if iAfter ~= iBefore then
        if probe.active and iAfter > (probe.step or 0) + 1 and (steps[probe.step] and (steps[probe.step].limit or 0) or 0) < 100 then probe.active = false; perfect = persona.perfect end
        newE()
        if not entries[iAfter] and p then
          entries[iAfter] = { x = p.x, y = p.y, force = copy(D), carrying = p.carrying ~= nil, play = state == "play", ground = p.onGround }
        end
        if routeOut and not routeOut[iAfter] and p then                -- the clean run: the route map (recovery v2)
          local f = {}; for k, v in pairs(D) do if v then f[#f + 1] = k end end; table.sort(f)
          routeOut[iAfter] = { i = iAfter, x = math.floor(p.x * 10 + 0.5) / 10, y = math.floor(p.y * 10 + 0.5) / 10, vx = math.floor(p.vx), g = p.onGround or false,
            c = p.carrying ~= nil, mv = onMover(p) or nil, play = state == "play", sig = sig(s), f = f, pk = (#pressesNow > 0) or nil, reactive = (steps[iAfter] and (steps[iAfter].limit or 0) >= 100) or nil }
        end
        if iAfter > maxStep then maxStep = iAfter end
      end
      -- (v2) off the route: Pepper stands somewhere the clean run never went during this step (more than 72 px to the
      -- side of where it ran, or 20 px below the lowest floor it stood on), for 0.3 s: a failure here, then recovery
      if route and not quitReq and state == "play" and p and not b.done then
        local ii = getI()
        local e1, e2 = route[ii], route[ii + 1]
        local st = steps[ii] or {}
        if e1 and e2 and (st.limit or 0) < 100 and p.onGround and not onMover(p) then
          local mg = math.min(288, 72 * (1 + (offN[ii] or 0)))     -- a step she keeps leaving: a wider margin
          local lo, hi = math.min(e1.x, e2.x, e1.xlo or e1.x) - mg, math.max(e1.x, e2.x, e1.xhi or e1.x) + mg
          local ymax = math.max(e1.g and e1.y or -1e9, e2.g and e2.y or -1e9, e1.ymax or -1e9)
          if p.x < lo or p.x > hi or (ymax > -1e9 and p.y > ymax + 20) then offT = offT + DT else offT = 0 end
          if offT > 0.3 then
            offT = 0; log.offroute = (log.offroute or 0) + 1; offN[ii] = (offN[ii] or 0) + 1
            if fail("offroute", s) then return end
            recover(s, false, "offroute")
          end
        else offT = 0 end
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
      elseif mode == "settle" then                                -- (v2) wait until she stands on solid ground
        stallAdd("recover", s)
        modeData.hold = {}
        local busy = (s.deadT or s.drownT or s.fallT or (s.ballBackT and s.ballBackT > 0)) and modeT < 5
        local ok = p.onGround and not onMover(p) and p.mode == "normal"
        if not busy and modeT >= (modeData.wait or 0.3) and (ok or modeT > 3) then plan((modeData.tries or 0) + (ok and 0 or 1)) end
      elseif mode == "magpie" then                                -- (v2) sneak up to the magpie and bark
        stallAdd("recover", s)
        local m, d = s.magpie, s.def.magpie
        if not m or s.ball.state ~= "magpie" or modeT > 20 then
          if modeT > 20 then fetchFails = fetchFails + 1 end
          plan((modeData.tries or 0) + (modeT > 20 and 1 or 0))
        elseif m.state == "perch" then
          local dx = m.x - p.x
          if math.abs(dx) > d.bark - 12 then
            modeData.hold = { [dx > 0 and "right" or "left"] = true, walk = known.sneak or nil }
            if p.onGround and math.abs(p.vx) < 1 and modeT > 0.5 then modeData.blockT = (modeData.blockT or 0) + DT else modeData.blockT = 0 end
            if (modeData.blockT or 0) > 0.25 then modeData.blockT = 0; modeData.hold.jump = true; origKey("space") end
          else
            modeData.hold = {}
            if math.abs(p.vx) < 1 and (modeData.barkT or 0) <= 0 then
              if not known.bark then startDiscover("bark", function() mode, modeT, modeData = "magpie", 0, { tries = 0 } end)
              else p.face = dx > 0 and 1 or -1; origKey("z"); modeData.barkT = 1.5 end
            end
          end
          if modeData.barkT then modeData.barkT = modeData.barkT - DT end
        else modeData.hold = {} end
      elseif mode == "walkback" and modeData.v2 then              -- (v2) walk to the chosen step's entry
        stallAdd("recover", s)
        local dx = modeData.x - p.x
        if math.abs(dx) < 6 then
          modeData.hold = {}; if p.onGround and math.abs(p.vx) < 1 then resumeAt(modeData.k) end
        elseif modeT > 8 or (p.onGround and math.abs(p.y - modeData.y) > 40) then    -- could not get there: plan again
          modeData.hold = {}; if p.onGround or modeT > 10 then plan(modeData.tries + 1) end
        else
          modeData.hold = { [dx > 0 and "right" or "left"] = true }
          if math.abs(dx) < 24 then modeData.hold.walk = true end
          if p.onGround and math.abs(p.vx) < 1 then modeData.blockT = modeData.blockT + DT else modeData.blockT = 0 end
          if modeData.blockT > 0.25 then modeData.blockT = 0; modeData.hold.jump = true; origKey("space") end   -- in the way: hop over
        end
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
      elseif mode == "fetch" and modeData.v2 then                 -- (v2) go and get the ball, then plan again
        stallAdd("recover", s)
        local ball = s.ball
        if p.carrying then plan(modeData.tries)
        elseif modeT > 10 or (ball.state ~= "rest" and ball.state ~= "home" and ball.state ~= "air") then
          fetchFails = fetchFails + 1; plan(modeData.tries)
        else
          local want = (ball.x >= p.x) and 1 or -1
          local gap = math.abs(p.x + want * 18 - ball.x)
          if p.face == want and gap < 12 and math.abs(p.vx) < 1 and ball.state ~= "air" then
            modeData.hold = {}
            if (modeData.pt or 0) <= 0 then origKey("x"); modeData.pt = 0.5 else modeData.pt = modeData.pt - DT end
          elseif p.face == want and gap < 12 then modeData.hold = {}
          else
            local dir = (want > 0) and "right" or "left"
            if p.face ~= want then modeData.hold = { [dir] = true, walk = true }
            elseif (want > 0 and p.x + 18 > ball.x) or (want < 0 and p.x - 18 < ball.x) then modeData.hold = { [want > 0 and "left" or "right"] = true, walk = true }
            else modeData.hold = { [dir] = true, walk = gap < 48 or nil } end
            if p.onGround and math.abs(p.vx) < 1 and modeT > 0.4 then modeData.blockT = (modeData.blockT or 0) + DT else modeData.blockT = 0 end
            if modeData.blockT > 0.4 then modeData.blockT = 0; modeData.hold.jump = true; origKey("space") end
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
