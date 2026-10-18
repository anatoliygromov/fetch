-- love . --qa   automated QA of the level's collision. Prints every problem it finds, then a summary.
--   1 hit sweep:  at every 6 px of the level, on every surface Pepper can stand on there, standing, crouching and
--                 in the air, she is knocked back (as a bike does, from either side) and followed for 1.5 s
--   2 bike sweep: in each bike zone a real bike rides at her from the right while she stands, crouches or hops
--   3 fuzz:       400 runs of 6 s of random play from random places
-- After every frame of every run: Pepper's body must not be inside a solid box (the pavement included, so
-- "pushed underground" is caught; her feet span is checked, deeper than a 4 px step) and she must not be below
-- the level. A run that ends in the river or at a
-- checkpoint after losing all hearts is fine; a run that ends stuck inside something is not.
local I = require("input")
local Pp = require("pepper")
return function(api)
  I.testing = true
  local HW = Pp.HW
  local problems, runs, frames, trace = {}, 0, 0, {}
  local function say(s) print(s); io.stdout:flush() end

  local function stage() return api.stage() end
  -- every height Pepper can stand at, at x (tops of boxes and terrain under her feet span, slope floors)
  local function floorsAt(w, x)
    local ys, seen = {}, {}
    local function add(y) y = math.floor(y + 0.5); if not seen[y] then seen[y] = true; ys[#ys + 1] = y end end
    for _, r in ipairs(w.rects) do if r.x1 > x - 13 and r.x0 < x + 13 and r.y0 > 8 then add(r.y0) end end
    local s = w:slopeAt(x); if s then local f = w:floor(x - 13, x + 13, x, s.y0 - 1, s.y1 + 1, s.y0 - 1) if f then add(f) end end
    local out = {}
    for _, y in ipairs(ys) do
      local h = Pp.H_STAND
      if not w:solidIn(x - HW, x + HW, y - h + 1, y - 0.5) then out[#out + 1] = y
      elseif not w:solidIn(x - HW, x + HW, y - Pp.H_CROUCH + 1, y - 0.5) then out[#out + 1] = -y end   -- crouch-only spot
    end
    return out
  end
  local function inside(w, p)
    if p.mode == "drown" or p.mode == "gone" or p.mode == "scramble" then return nil end
    local h = p:height()
    -- her feet span (13 px each side) must be clear; the outer 4 px of her body may brush a box edge as she
    -- slips past it, and a ledge up to a step (4 px) higher may overlap her paws: both are by design
    local r = w:solidIn(p.x - 12.5, p.x + 12.5, p.y - h + 1.5, p.y - w.STEP - 0.5)
    if r and r.terrain and w:slopeNear(p.x - HW, p.x + HW) then r = nil end   -- on the stairs her paws are on two steps
    if r then return ("inside box %s x %d-%d y %d-%d"):format(r.name or (r.terrain and "terrain" or "?"), r.x0, r.x1, r.y0, r.y1) end
    if p.y > w.height + 4 then return "below the level" end
    return nil
  end
  local function place(s, x, y, crouch)
    local p = s.pepper
    p.x, p.y, p.vx, p.vy, p.onGround, p.ground, p.mode, p.crouch, p.invuln = x, y, 0, 0, true, nil, "normal", crouch, 0
    p.carrying = nil
    s.cam = math.max(0, math.min(s.world.width - 320, x - 140)); s.bikes = {}; s.bikeT = 999; s.hearts = 3; s.lives = 3
    s.deadT = nil; s.events = {}
  end
  -- run n frames; inputs(f) returns the held buttons and presses for frame f; returns the first problem or nil
  local function sim(s, n, inputs, tag)
    runs = runs + 1; trace = {}
    for f = 1, n do
      local held, pr = inputs(f)
      I.force = held or {}
      s:update(1 / 60, pr or {})
      frames = frames + 1
      local q = s.pepper
      trace[#trace + 1] = ("f%d x %.1f y %.1f vy %.0f %s %s held %s"):format(f, q.x, q.y, q.vy, q.onGround and "G" or "A", q.crouch and "C" or "-", table.concat((function() local t = {} for k in pairs(held or {}) do t[#t + 1] = k end return t end)(), "+"))
      if #trace > (tonumber(os.getenv("QA_TRACE") or "") or 12) then table.remove(trace, 1) end
      local why = inside(s.world, s.pepper)
      if why then
        local p = s.pepper
        if os.getenv("QA_TRACE") then for _, l in ipairs(trace) do say("    " .. l) end end
        problems[#problems + 1] = ("%s: frame %d, Pepper x %.1f y %.1f (%s, %s): %s"):format(tag, f, p.x, p.y, p.mode, p.crouch and "crouched" or "standing", why)
        I.force = {}
        return true
      end
    end
    I.force = {}
    return false
  end

  local function run()
    local s = stage(); local w = s.world
    s.events = {}
    say("QA: hit sweep over " .. w.width .. " px")
    for x = 20, w.width - 20, 6 do
      for _, fy in ipairs(floorsAt(w, x)) do
        local y, crouchOnly = math.abs(fy), fy < 0
        for _, pose in ipairs(crouchOnly and { "crouch" } or { "stand", "crouch", "air" }) do
          for _, side in ipairs({ -1, 1 }) do
            place(stage(), x, y, pose == "crouch")
            local sp = stage().pepper
            if pose == "air" then sp.onGround = false; sp.vy = -150 end
            local held = pose == "crouch" and { down = true } or {}
            sim(stage(), 2, function() return held end, "settle")
            stage().pepper.invuln = 0
            if stage().pepper.mode == "normal" then
              stage().pepper:hurt(stage().pepper.x + side * 10, stage().world)
              sim(stage(), 90, function() return {} end, ("hit %s from %s at x %d y %d"):format(pose, side < 0 and "left" or "right", x, y))
            end
          end
        end
      end
    end
    say("QA: bike sweep")
    local zones = stage().def.bikes
    if zones.zoneX0 then zones = { zones } end
    for zi, z in ipairs(zones) do
      for x = z.zoneX0 + 10, z.zoneX1 - 10, 10 do
        for _, fy in ipairs(floorsAt(w, x)) do
          local y = math.abs(fy)
          for _, pose in ipairs({ "stand", "crouch", "hop" }) do
            place(stage(), x, y, pose == "crouch")
            local s2 = stage()
            s2.bikes = { { x = x + 90, y = 184, warn = 0, zone = z } }
            sim(s2, 120, function(f)
              if pose == "crouch" then return { down = true } end
              if pose == "hop" and f == 30 then return { jump = true }, { jump = true } end
              return {}
            end, ("bike zone %d, %s at x %d y %d"):format(zi, pose, x, y))
          end
        end
      end
    end
    say("QA: fuzz")
    local rnd = love.math.newRandomGenerator(7)
    local keys = { "left", "right", "down", "jump", "walk" }
    for k = 1, 400 do
      local x = rnd:random(30, w.width - 30)
      local fl = floorsAt(w, x)
      if #fl > 0 then
        local fy = fl[rnd:random(1, #fl)]
        place(stage(), x, math.abs(fy), fy < 0)
        local held, until_ = {}, 0
        sim(stage(), 360, function(f)
          local pr = {}
          if f >= until_ then
            held = {}
            for _, key in ipairs(keys) do if rnd:random() < 0.35 then held[key] = true end end
            if held.left and held.right then held.left = nil end
            if held.jump then pr.jump = true end
            until_ = f + rnd:random(6, 40)
            local bz = stage().def.bikes                                   -- (a level without bike zones gets no bikes)
            stage().bikes = (rnd:random() < 0.3 and (bz.zoneX0 or #bz > 0)) and { { x = stage().pepper.x + rnd:random(40, 160), y = 184, warn = 0 } } or stage().bikes
          end
          return held, pr
        end, ("fuzz run %d from x %d y %d"):format(k, x, math.abs(fy)))
      end
    end
    say(("QA: %d runs, %d frames, %d problems"):format(runs, frames, #problems))
    local kinds, order = {}, {}                                    -- one line per kind of problem, with a count
    for _, s2 in ipairs(problems) do
      local k = s2:gsub("%d+%.?%d*", "#")
      if not kinds[k] then kinds[k] = { n = 0, first = s2 }; order[#order + 1] = k end
      kinds[k].n = kinds[k].n + 1
    end
    for _, k in ipairs(order) do say(("  %4d x  %s"):format(kinds[k].n, kinds[k].first)) end
    love.event.quit()
  end

  local t = 0
  local old = love.update
  love.update = function(dt)
    t = t + 1
    if t == 2 then love.keypressed("space") end
    if t == 30 then run() end
    if t < 30 then old(1 / 60) end
  end
end
