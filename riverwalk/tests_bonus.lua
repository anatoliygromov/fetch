-- love riverwalk --bonus --physics   FETCH FRENZY's checks (bonus.lua); prints PASS / FAIL and "n of m passed":
--   every throw of the three rounds lands on the lawn, stays under the signs, and can be caught in the air by
--   Pepper's real controller (pepper.lua: run, held jump, unchanged numbers) starting where the throw before
--   landed (searched by simulation); Mia winds up before every throw; the timer ends the round; the extra life
--   comes at B.LIFE_AT catches; the flow: tally -> bonus -> story card with a golden bone, tally -> story without;
--   the autopilot catches most items; a model child gets the extra life about half the time (the tuning).
-- love riverwalk --bonus --auto      the autopilot plays a round (--level X picks the round) and saves every 3rd
--   frame to rec/ (for the GIF), then the result card as bonus_result.png.
local I = require("input")
local B = require("bonus")
local Pp = require("pepper")

-- the autopilot: for every item in the air, the earliest point of its path she can reach (running at full speed,
-- with a held jump if it is high); it runs there and jumps in time. Items on the lawn: it runs to them.
-- kid (optional): { react = s, aim = px, jumpErr = s, rng } a model child (late, off target, jumps off time).
local RISE_V = math.sqrt(2 * Pp.GRAV * Pp.P.jumpH)
local function riseTime(h)                                          -- seconds for a held jump to rise h px
  local d = RISE_V * RISE_V - 2 * Pp.GRAV * h
  if d < 0 then return nil end
  return (RISE_V - math.sqrt(d)) / Pp.GRAV
end
local function predict(it)                                          -- its path from now: { x, y, t } every step
  local c = { kind = it.kind, x = it.x, y = it.y, vx = it.vx, vy = it.vy, state = it.state, landed = it.landed }
  local path, t = {}, 0
  while c.state == "air" and t < 4 do B.step(c, B.DT); t = t + B.DT; path[#path + 1] = { x = c.x, y = c.y, t = t, landed = c.landed } end
  return path
end
local function newPilot(kid)
  local P = { plan = nil, jumpAt = nil, seen = {} }
  function P.holds(r)
    local p = r.pepper
    local hold, press = {}, {}
    local now = r.t
    -- the item to go for: the one whose best catch comes first
    local best
    for _, it in ipairs(r.items) do
      P.seen[it] = P.seen[it] or now
      local ready = not kid or now - P.seen[it] >= kid.react
      if ready then
        if it.state == "air" and not it.landed then
          local pick                                                -- its earliest point she can reach standing,
          for pass = 1, 2 do                                        -- else its earliest one with a jump
            for _, pt in ipairs(predict(it)) do
              if pt.landed then break end
              local need = math.max(0, (p.y - Pp.H_STAND) - (pt.y + B.KIND[it.kind].r) + 3)   -- how far up her top must go
              local rt = need > 0 and riseTime(need) or 0
              local d = math.max(0, math.abs(pt.x - p.x) - 10)            -- (her box reaches 17 px either side)
              local run = d > 0 and (d / Pp.P.run + 0.2) or 0
              if rt and (pass == 2 or need == 0) and run + rt + (need > 0 and 0.05 or 0) <= pt.t then
                pick = { it = it, x = pt.x, t = pt.t, jump = need > 0 and (pt.t - rt) or nil }; break
              end
            end
            if pick then break end
          end
          if pick and (not best or pick.t < best.t) then best = pick end
        else
          local tt = math.abs(it.x - p.x) / Pp.P.run + 0.5
          if not best or tt < best.t then best = { it = it, x = it.x + it.vx * 0.2, t = tt } end
        end
      end
    end
    if best then
      if kid then
        P.aim = P.aim or {}
        if not P.aim[best.it] then P.aim[best.it] = { dx = kid.rng() * kid.aim, dj = kid.rng() * kid.jumpErr, jumps = kid.rng() > -0.2 } end
        best.x = best.x + P.aim[best.it].dx
        if best.jump then best.jump = P.aim[best.it].jumps and best.jump + P.aim[best.it].dj or nil end
      end
      local dx = best.x - p.x
      if math.abs(dx) > 3 then hold[dx > 0 and "right" or "left"] = true end
      if best.jump and best.jump <= B.DT * 1.5 and p.onGround and math.abs(dx) < 14 then press.jump = true end
      if best.jump and best.jump <= 0.4 or not p.onGround then hold.jump = true end
    elseif r.holding then                                           -- wait in the middle of the lawn
      local dx = 170 - p.x
      if math.abs(dx) > 30 then hold[dx > 0 and "right" or "left"] = true end
    end
    return hold, press
  end
  return P
end

-- one whole round, headless: returns the round (its catches, points, ...)
local function playRound(variant, kid, onStep)
  local r = B.new({ variant = variant }); r.phase = "play"; r.t = 0
  local pilot = newPilot(kid)
  local dbg = os.getenv("BONUS_DEBUG") and not kid
  for _ = 1, math.floor((B.TIME + 3) / B.DT) do
    local hold, press = pilot.holds(r)
    I.force = hold
    local before, c0 = {}, r.catches
    for _, it in ipairs(r.items) do before[it] = true end
    r:update(B.DT, press)
    if dbg then
      for _, it in ipairs(r.items) do before[it] = nil end
      for it in pairs(before) do print(("  %5.2f item %d %s %s at x %.0f y %.0f, Pepper x %.0f y %.0f"):format(r.t, it.n, it.kind,
        r.catches > c0 and "CAUGHT" or "LOST", it.x, it.y, r.pepper.x, r.pepper.y)) end
      if press.jump then print(("  %5.2f jump at x %.0f"):format(r.t, r.pepper.x)) end
    end
    if onStep then onStep(r) end
    if r.phase == "result" then break end
  end
  I.force = {}
  return r
end

return function(mode, api)
  I.testing = true
  local results = {}
  local function report(name, ok, detail)
    ok = ok and true or false
    results[#results + 1] = ok
    print(("%-58s %s  %s"):format(name, ok and "PASS" or "FAIL", detail or "")); io.stdout:flush()
  end
  local steps = {}
  local function add(st) steps[#steps + 1] = st end
  local function check(name, f) add({ act = function() local ok, d = f(); report(name, ok, d) end }) end
  local function key(k) add({ act = function() love.keypressed(k) end }) end
  local function wait(s) add({ wait = s }) end
  local function state(want, limit) add({ cond = function() return api.getState() == want end, limit = limit or 8, what = want }) end

  if mode == "--physics" then
    -- 1 Pepper is Pepper: her numbers, and a held jump / a tap on the lawn reach 46 / 24 px
    check("Pepper's numbers are the levels' (run 120, jump 46, hop 24)", function()
      local P = Pp.P
      return P.run == 120 and P.walk == 60 and P.crawl == 40 and P.jumpH == 46 and P.minJump == 24 and P.fallMul == 1.25,
        ("run %d walk %d crawl %d jump %d hop %d"):format(P.run, P.walk, P.crawl, P.jumpH, P.minJump)
    end)
    check("on the lawn: held jump 46 px, tap 24 px, crawl 40 px/s", function()
      local w = B.world()
      local function jump(frames)
        local p = Pp.new(160, B.FEET); local top = B.FEET
        I.force = { jump = true }; p:update(B.DT, w, { jump = true })
        for f = 1, 120 do if f >= frames then I.force = {} end; p:update(B.DT, w, {}); top = math.min(top, p.y) end
        I.force = {}; return B.FEET - top
      end
      local p = Pp.new(100, B.FEET); I.force = { right = true, down = true }
      for _ = 1, 120 do p:update(B.DT, w, {}) end
      I.force = {}
      local held, tap = jump(200), jump(1)
      return math.abs(held - 46) <= 1 and math.abs(tap - 24) <= 2 and math.abs(p.vx - 40) < 1 and p.crouch,
        ("held %.1f, tap %.1f, crawl %.0f px/s"):format(held, tap, p.vx)
    end)
    -- 2 the throws: on the lawn, under the signs, readable (in the air long enough to follow)
    for v, list in ipairs(B.VARIANTS) do
      check(("round %d (%s): %d throws land on the lawn, under the signs"):format(v, B.NAMES[v], #list), function()
        local bad, lo, hi, top, tmin = {}, 999, 0, 999, 99
        for i, th in ipairs(list) do
          local f = B.flight(th[1], B.launch(th[1], th[2], th[3]))
          lo, hi, top, tmin = math.min(lo, f.landX), math.max(hi, f.landX), math.min(top, f.top), math.min(tmin, f.landT)
          if f.landX < 60 or f.landX > 310 or math.abs(f.landX - th[2]) > 1 or f.top < 30 or f.landT < 0.7 then bad[#bad + 1] = i end
        end
        return #bad == 0, #bad == 0 and ("lands x %.0f-%.0f, highest y %.0f, shortest flight %.2f s"):format(lo, hi, top, tmin) or ("throws " .. table.concat(bad, ", "))
      end)
      check(("round %d: the last throw lands before the time is up"):format(v), function()
        local t = 0; for _, th in ipairs(list) do t = t + th[4] end
        local last = list[#list]; local f = B.flight(last[1], B.launch(last[1], last[2], last[3]))
        return t + f.landT < B.TIME - 0.5, ("last throw at %.1f s, lands at %.1f s"):format(t, t + f.landT)
      end)
    end
    -- 3 every throw can be caught in the air: Pepper's real controller, starting standing where the throw before
    --   landed (the first: where the round starts her), runs to some x (8 px steps) and maybe jumps (held, at
    --   some step): simulated until the item first touches the lawn
    check("every throw can be caught in the air (simulated, real Pepper)", function()
      local w = B.world()
      local total, jumps, worst, bad = 0, 0, 0, {}
      local function try(kind, l, fromX, toX, jumpT)
        local p = Pp.new(fromX, B.FEET); p.face = -1
        local it = { kind = kind, x = l.x, y = l.y, vx = l.vx, vy = l.vy, state = "air" }
        local t = 0
        while not it.landed and t < 6 do
          local hold = {}
          local dx = toX - p.x
          if math.abs(dx) > 2 then hold[dx > 0 and "right" or "left"] = true end
          local pr = {}
          if jumpT and t >= jumpT then hold.jump = true; if t - jumpT < B.DT then pr.jump = true end end
          I.force = hold; p:update(B.DT, w, pr)
          B.step(it, B.DT); t = t + B.DT
          local x0, y0, x1, y1 = p:box(); local r = B.KIND[kind].r
          if not it.landed and it.x + r > x0 and it.x - r < x1 and it.y + r > y0 and it.y - r < y1 then I.force = {}; return true, t end
        end
        I.force = {}; return false
      end
      for v, list in ipairs(B.VARIANTS) do
        local from = 128
        for i, th in ipairs(list) do
          total = total + 1
          local l = B.launch(th[1], th[2], th[3])
          local f = B.flight(th[1], l)
          local ok, how = false, nil
          for x = 20, 300, 8 do if try(th[1], l, from, x) then ok, how = true, "run"; break end end
          if not ok then
            for x = 20, 300, 8 do
              for jt = 0, f.landT, 2 * B.DT do if try(th[1], l, from, x, jt) then ok, how = true, "jump"; break end end
              if ok then break end
            end
          end
          if how == "jump" then jumps = jumps + 1 end
          if not ok then bad[#bad + 1] = v .. "." .. i end
          worst = math.max(worst, math.abs(th[2] - from))
          from = f.landX
        end
      end
      return #bad == 0, #bad == 0 and ("%d of %d (%d need a jump), from up to %d px away"):format(total, total, jumps, worst) or ("not: " .. table.concat(bad, ", "))
    end)
    -- 4 Mia throws everything: every item was in her hand through a whole wind-up; nothing moves before
    check("Mia winds up before every throw; items start in her hand", function()
      local r = B.new({ variant = 1 }); r.phase = "play"
      local wound, bad, seen = 0, 0, {}
      for _ = 1, math.floor(B.TIME / B.DT) + 10 do
        if r.holding then wound = wound + B.DT; if r.mia.state ~= "windup" then bad = bad + 1 end end
        local before = #r.items
        r:update(B.DT, {})
        for _, it in ipairs(r.items) do
          if not seen[it] then
            seen[it] = true
            if wound < B.WINDUP - 2 * B.DT or math.abs(it.x - (B.MIA_X + B.HAND[1])) > 4 then bad = bad + 1 end
            wound = 0
          end
        end
      end
      local n = 0; for _ in pairs(seen) do n = n + 1 end
      return bad == 0 and n == #r.list, ("%d throws, all after a %.2f s wind-up"):format(n, B.WINDUP)
    end)
    -- 5 the timer ends the round: TIME UP at 30 s, then the result card; nothing is thrown after it
    check("the timer ends the round (30 s, TIME UP, then the result)", function()
      local r = B.new({ variant = 2 }); r.phase = "play"
      local t, upAt, resAt, thrownAtUp = 0, nil, nil, nil
      for _ = 1, math.floor(40 / B.DT) do
        r:update(B.DT, {}); t = t + B.DT
        if r.phase == "timeup" and not upAt then upAt = t; thrownAtUp = r.thrown end
        if r.phase == "result" and not resAt then resAt = t end
      end
      return upAt and math.abs(upAt - B.TIME) < 0.05 and resAt and resAt > upAt and r.thrown == thrownAtUp and r.time == 0,
        ("time up at %.2f s, result at %.2f s, %d thrown"):format(upAt or -1, resAt or -1, r.thrown)
    end)
    -- 6 the extra life: at B.LIFE_AT catches, not one fewer
    check(("extra life at %d catches, not at %d"):format(B.LIFE_AT, B.LIFE_AT - 1), function()
      local function finish(n)
        local r = B.new({}); r.phase = "play"; r.catches = n; r.time = 0.01
        for _ = 1, 120 do r:update(B.DT, {}) end
        return r.phase == "result" and r:result().life, r.life
      end
      local a, b = finish(B.LIFE_AT), finish(B.LIFE_AT - 1)
      return a == true and not b, ("%d: %s, %d: %s"):format(B.LIFE_AT, tostring(a), B.LIFE_AT - 1, tostring(b))
    end)
    -- 7 catching: in the air +100, on the lawn +50, off the screen lost
    check("catch in the air +100, pick up on the lawn +50, off screen lost", function()
      local r = B.new({}); r.phase = "play"; r.nextT = 99
      local p = r.pepper
      r.items = { { kind = "ball", state = "air", x = p.x, y = p.y - 20, vx = 0, vy = 0 } }
      r:update(B.DT, {})
      local a = r.points
      p.x = 60
      r.items = { { kind = "stick", state = "ground", landed = true, x = 60, y = B.FEET - 4, vx = 0, vy = 0 } }
      r:update(B.DT, {})
      local b = r.points - a
      r.items = { { kind = "ball", state = "ground", landed = true, x = 318, y = B.FEET - 3, vx = 200, vy = 0 } }
      for _ = 1, 30 do r:update(B.DT, {}) end
      return a == B.AIR and b == B.GROUND and r.catches == 2 and r.air == 1 and r.picked == 1 and r.lost == 1 and #r.items == 0,
        ("air %d, ground %d, lost %d"):format(a, b, r.lost)
    end)
    -- 8 the autopilot catches most items; a model child gets the extra life about half the time
    for v = 1, 3 do
      check(("autopilot catches most items (round %d)"):format(v), function()
        local r = playRound(v)
        return r.catches >= math.ceil(r.thrown * 0.8), ("%d of %d (%d in the air), %d points"):format(r.catches, r.thrown, r.air, r.points)
      end)
    end
    check("a model child gets the extra life about half the time", function()
      -- the model child (ages 6-10, set before tuning, not from a playtest): reacts 0.45-0.9 s after a throw,
      -- runs to a spot up to 50 px off, jumps up to 0.25 s off time and does not jump at all for 40% of the
      -- high ones. 120 rounds, 40 per round variant.
      local seed = 12345
      local function rnd() seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648 end
      local function sym() return rnd() * 2 - 1 end
      local got, n, counts, sum = 0, 0, {}, 0
      for v = 1, 3 do
        for _ = 1, 40 do
          local kid = { react = 0.45 + rnd() * 0.45, aim = 50, jumpErr = 0.25, rng = sym }
          local r = playRound(v, kid)
          n = n + 1; sum = sum + r.catches; counts[#counts + 1] = r.catches
          if r.catches >= B.LIFE_AT then got = got + 1 end
        end
      end
      table.sort(counts)
      local share = {}                                              -- the share of rounds with at least c catches
      for c = 8, 14 do local m = 0; for _, x in ipairs(counts) do if x >= c then m = m + 1 end end; share[#share + 1] = ("%d+: %d%%"):format(c, math.floor(m / n * 100 + 0.5)) end
      print("    model child, share of rounds with at least: " .. table.concat(share, ", "))
      local k = got / n
      return k >= 0.35 and k <= 0.65, ("%d%% of %d model rounds (catches: median %d, mean %.1f, %d-%d)"):format(math.floor(k * 100 + 0.5), n,
        counts[math.floor(n / 2)], sum / n, counts[1], counts[n])
    end)
    -- 9 nothing covers Pepper: the cards go where they miss her (or she is drawn again over them)
    check("the result card never covers Pepper on the lawn", function()
      local F = api.flow
      local bad = 0
      for x = 20, 300, 10 do
        for _, y in ipairs({ 184 }) do
          local r = B.new({}); r.pepper.x, r.pepper.y = x, y
          local x0, y0, x1, y1 = r:pepperRect()
          local cy, clear = F.placeY(50, 220, 24, 104, { x0, y0, x1, y1 })
          if not clear then bad = bad + 1 end
        end
      end
      return bad == 0, bad == 0 and "on the lawn the result card misses her (and she is drawn over every card)" or (bad .. " places")
    end)
    -- 10 the flow: a golden bone opens the bonus after the tally, before the story card; no golden bone, no bonus
    local function finishLevel(golden)
      return { act = function()
        local s = api.stage()
        if golden then for _, bn in ipairs(s.bones) do if bn.super then bn.taken = true; s.taken = s.taken + 1; break end end end
        local e = s.def.exit
        if e then
          if e.needBall then s.ball.state = "carried"; s.pepper.carrying = s.ball end
          s.pepper.x = e.x + 4; s.pepper.y = s.world:groundAt(s.pepper.x) or s.pepper.y; s.pepper.onGround = true
        else s:giveBall() end
      end }
    end
    local scoreBefore, livesBefore
    add({ act = function() api.flow.save = false; api.startRun(1) end }); state("intro", 1); wait(0.6); key("space"); state("play", 1); wait(0.2)
    add(finishLevel(true)); state("clear", 6)
    add({ cond = function() local tl = api.tally(); return tl and tl.done end, limit = 8, what = "the tally" })
    add({ act = function() scoreBefore, livesBefore = api.run().score, api.run().lives end })
    key("space"); wait(0.1)
    check("flow: golden bone found: tally -> FETCH FRENZY", function() return api.getState() == "bonus" and api.bonus().phase == "intro", api.getState() end)
    wait(0.6); key("space"); wait(1.3)
    check("flow: any button starts the round, Pepper plays", function() return api.bonus().phase == "play", api.bonus().phase end)
    add({ act = function() local b = api.bonus(); b.catches, b.points, b.time = B.LIFE_AT, 1234, 0.05 end })
    add({ cond = function() return api.bonus() and api.bonus().phase == "result" end, limit = 4, what = "the result" })
    wait(1.6); key("space"); wait(0.1)
    check("flow: then the story card", function() return api.getState() == "story", api.getState() end)
    check("flow: bonus points in the score, extra life in the run", function()
      local r = api.run(); return r.score == scoreBefore + 1234 and r.lives == livesBefore + 1, ("score %d -> %d, lives %d -> %d"):format(scoreBefore, r.score, livesBefore, r.lives) end)
    wait(2.1); key("space"); state("intro", 1); wait(0.6); key("space"); state("play", 1); wait(0.2)
    add(finishLevel(false)); state("clear", 6)
    add({ cond = function() local tl = api.tally(); return tl and tl.done end, limit = 8, what = "the tally" })
    key("space"); wait(0.1)
    check("flow: no golden bone: tally -> story card, no bonus", function() return api.getState() == "story" and api.bonus() == nil, api.getState() end)
    add({ act = function()
      local ok = 0; for _, r in ipairs(results) do if r then ok = ok + 1 end end
      print(("%d of %d passed"):format(ok, #results)); io.stdout:flush(); love.event.quit()
    end })
  else                                                              -- --auto: the autopilot plays a round for a GIF
    local pilot
    love.filesystem.createDirectory("rec")
    add({ act = function() api.startBonus() end }); wait(0.8)
    add({ act = function() love.graphics.captureScreenshot("bonus_intro.png") end }); wait(0.1)
    add({ act = function() love.keypressed("space") end })
    add({ act = function() pilot = newPilot() end })
    add({ cond = function()
      local b = api.bonus()
      if not b or b.phase == "result" then I.force = {}; return true end
      if b.phase == "play" then
        local hold, press = pilot.holds(b)
        I.force = hold
        if press.jump then love.keypressed("space") end
      end
      return false
    end, limit = 40, what = "the round" })
    wait(2.2)
    add({ act = function() love.graphics.captureScreenshot("bonus_result.png")
      local b = api.bonus(); local r = b:result()
      print(("AUTOPILOT FETCH FRENZY round %d (%s): %d catches of %d thrown (%d in the air), %d points, extra life %s"):format(
        b.variant, B.NAMES[b.variant], r.catches, r.thrown, r.air, r.points, r.life and "yes" or "no")); io.stdout:flush() end })
    wait(0.1)
    add({ act = function() local b = api.bonus(); b.catches, b.air, b.points, b.life, b.t = 7, 5, 600, false, 2 end }); wait(0.1)
    add({ act = function() love.graphics.captureScreenshot("bonus_result_try.png") end })            -- (fewer catches)
    wait(0.2); add({ act = function() love.event.quit() end })
  end

  local i, since, frame, n = 1, 0, 0, 0
  local old = love.update
  love.update = function(dt)
    dt = 1 / 60; since = since + dt
    old(dt)
    if mode == "--auto" then
      frame = frame + 1
      if frame % 3 == 0 then n = n + 1; love.graphics.captureScreenshot(("rec/%04d.png"):format(n)) end
    end
    local st = steps[i]
    if not st then return end
    if st.wait then if since >= st.wait then i, since = i + 1, 0 end
    elseif st.cond then
      if st.cond() then if st.act then st.act() end; i, since = i + 1, 0
      elseif since > st.limit then report(("step %d: waiting for %s"):format(i, st.what or "a condition"), false, "stuck in " .. api.getState()); i, since = i + 1, 0 end
    else st.act(); i, since = i + 1, 0 end
  end
end
