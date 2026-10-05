-- Small visual extras around Pepper, 90s console style: hard 1 px pixels, a few palette steps, no blur.
-- Drawing only. They watch Pepper's state from outside (stage.lua calls Ex.update after her update) and never
-- change it, so she moves exactly as before (tools/check_pepper.sh proves it). Each one has its own switch;
-- E toggles them all off and on in the game (A/B), `--noextras` starts with them off.
local Ex = {}
local lg = love.graphics

Ex.on = {                       -- the switches, all on by default
  dust_land = true,             -- puffs at her paws when she lands from a real fall (12 px or more), bigger the higher
  dust_skid = true,             -- small puffs off her front paws while she skids
  dust_start = true,            -- one little kick of dust behind her when she breaks into a run from standing
  splash = true,                -- a splash when she falls in the river: drops, a foam line at the surface, ripples
  bone_pop = true,              -- a twinkle and a small "+100" where a bone was picked up
}
Ex.enabled = true               -- the master switch (E key, --noextras)
function Ex.toggle() Ex.enabled = not Ex.enabled end

local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end
-- dust: the pavement's warm greys, a step or two lighter than its lightest stone (the kerb, e5ddda), so it reads
-- as dust kicked off the paving and not as more paving
local DUST = { hi = hex("f7f3f0"), body = hex("ebe5e1"), lo = hex("cdc7c5") }
-- the bones' colours (scene.lua): white, bone, gold for a super bone; dark for the points' 1 px shadow
local BONE = { white = hex("ffffff"), bone = hex("efe8d8"), gold = hex("f2c94c"), dark = hex("141824") }
-- water: the river art's light tones (art/scene/water.png), lightest first
local WATER = { hex("caecfc"), hex("acd5ee"), hex("98c4e5"), hex("78a7d1") }

-- one effects state per run of the level; a small LCG of its own, so nothing else's random numbers change
function Ex.new() return { parts = {}, seed = 12345, prev = nil, minY = nil } end
local function rnd(fx, a, b)
  fx.seed = (fx.seed * 1103515245 + 12345) % 2147483648
  return a + (fx.seed % 10000) / 10000 * (b - a)
end
local function add(fx, p) p.t = 0; fx.parts[#fx.parts + 1] = p; return p end

-- a dust puff: a little round cloud standing on the ground at (x, y), radius r, drifting (vx, vy) px/s
local function puff(fx, x, y, r, vx, vy, life, front)
  return add(fx, { kind = "puff", x = x, y = y, r = r, vx = vx, vy = vy, life = life, front = front })
end

-- watch Pepper (called once per step, after she has moved)
function Ex.update(fx, s, dt)
  local p = s.pepper
  local was = fx.prev
  local now = { x = p.x, y = p.y, vx = p.vx, vy = p.vy, onGround = p.onGround, mode = p.mode, skid = p.skid }
  fx.prev = now
  for i = #fx.parts, 1, -1 do
    local q = fx.parts[i]; q.t = q.t + dt
    if q.t >= q.life then table.remove(fx.parts, i) end
  end
  if not was then fx.popped = {}; for _, bn in ipairs(s.bones) do fx.popped[bn] = bn.taken end; return end
  -- bone pop (tracked even while the extras are off): a bone taken this step twinkles where it was, and its points float up.
  -- Drawn behind Pepper, so it never covers her: the points show as they rise above her head
  for _, bn in ipairs(s.bones) do
    if bn.taken and not fx.popped[bn] then
      fx.popped[bn] = true
      if Ex.enabled and Ex.on.bone_pop then add(fx, { kind = "pop", x = bn.x, y = bn.y - 9, super = bn.super, life = 0.75, front = false }) end
    end
  end

  if now.onGround and math.abs(now.vx) < 5 and now.mode == "normal" then fx.restT = 0
  else fx.restT = (fx.restT or 9) + dt end
  local jumped = math.abs(now.x - was.x) > 20 or math.abs(now.y - was.y) > 40     -- a respawn or a test teleport
  if not now.onGround then fx.minY = math.min(fx.minY or now.y, now.y, was.y) end
  if not Ex.enabled or jumped then if now.onGround then fx.minY = nil end; return end

  -- splash: she has just fallen in the river (Pepper's mode turns to "drown"; sfx.lua already plays the sound)
  if Ex.on.splash and now.mode == "drown" and was.mode ~= "drown" then
    local r = s.world:inWater(p.x, p.y)
    local sy = r and r.y0 or math.floor(p.y)
    add(fx, { kind = "foam", x = p.x, y = sy, life = 1.0, front = true })
    for k = 1, 16 do                                            -- drops thrown up and out, falling back in:
      local side = (k % 2 == 0) and 1 or -1                     -- the first six steep and chunky (the crown),
      local crown = k <= 6                                      -- the rest flatter spray
      local vy = crown and -rnd(fx, 105, 150) or -rnd(fx, 55, 105)
      add(fx, { kind = "drop", x = p.x + side * (crown and rnd(fx, 3, 9) or rnd(fx, 2, 12)), y = sy,
        vx = side * (crown and rnd(fx, 6, 22) or rnd(fx, 22, 60)), vy = vy, g = 460, life = -2 * vy / 460,
        big = crown, c = (k % 4 == 0) and 2 or 1, front = true })
    end
    for side = -1, 1, 2 do add(fx, { kind = "ripple", x = p.x, y = sy, dir = side, life = 0.9, front = true }) end
  end

  -- landing dust: she was in the air and is on the ground now (not the end of a scramble, not in the river)
  if Ex.on.dust_land and now.onGround and not was.onGround and (was.mode == "normal" or was.mode == "hurt")
     and now.mode ~= "drown" then
    local h = now.y - (fx.minY or now.y)
    if h >= 12 then
      local n = h < 26 and 1 or (h < 44 and 2 or 3)            -- puffs each side
      for side = -1, 1, 2 do
        for k = 1, n do
          local r = (k == 1 and n > 1) and 2 or 1
          if n == 3 and k == 2 then r = 2 end
          puff(fx, p.x + side * (6 + k * 4), p.y, r, side * (14 + k * 8 + rnd(fx, 0, 6)), -rnd(fx, 3, 8),
            0.30 + n * 0.04 + rnd(fx, 0, 0.06), false)
        end
      end
    end
  end
  if now.onGround then fx.minY = nil end

  -- skid dust: a small puff off her braced front paws on the first step of a skid and every 3rd step after; the
  -- puffs stay where they were kicked up, so they trail behind her as she slides
  if now.skid and now.onGround and now.mode == "normal" then
    fx.skidN = (fx.skidN or 0) + 1
    if Ex.on.dust_skid and fx.skidN % 3 == 1 then
      local dir = now.vx >= 0 and 1 or -1
      puff(fx, p.x + dir * (11 + rnd(fx, 0, 3)), p.y, (fx.skidN == 1) and 2 or 1, dir * rnd(fx, 6, 12), -rnd(fx, 4, 9),
        0.26 + rnd(fx, 0, 0.06), false)
    end
  else fx.skidN = 0 end

  -- run-start kick: she reaches running speed (the gallop starts) within 0.3 s of standing still
  local RUN = 70                                                -- Pepper's run clip starts above walk speed + 10
  if Ex.on.dust_start and now.onGround and now.mode == "normal" and not p.crouch and fx.restT <= 0.3
     and math.abs(now.vx) > RUN and math.abs(was.vx) <= RUN then
    local dir = now.vx > 0 and 1 or -1
    puff(fx, p.x - dir * 15, p.y, 2, -dir * 14, -6, 0.32, false)
    puff(fx, p.x - dir * 21, p.y, 1, -dir * 20, -4, 0.26, false)
  end
end

-- a puff, drawn pixel by pixel: it grows for the first quarter, holds, then breaks up into a checker dither
-- of the darker grey and thins out (palette steps, no alpha)
local function drawPuff(q, cam)
  local k = q.t / q.life
  local r = q.r
  if k < 0.25 then r = math.max(0, q.r - 1) end
  local cx = math.floor(q.x + q.vx * q.t - cam + 0.5)
  local by = math.floor(q.y + q.vy * q.t + 0.5)                -- the puff's bottom row sits on the ground
  local cy = by - r
  for dy = -r, r do
    for dx = -r - 1, r + 1 do
      local ex = dx / (r + 1.4)
      local ey = dy / (r + 0.5)
      if ex * ex + ey * ey <= 1 then
        local x, y = cx + dx, cy + dy
        local c
        if k < 0.6 then
          if dy == r and r > 0 then c = DUST.lo
          elseif dy < 0 or (dy == 0 and dx < 0) or r == 0 then c = DUST.hi
          else c = DUST.body end
        elseif k < 0.82 then
          if (x + y) % 2 == 0 then c = (dy < 0) and DUST.body or DUST.lo end
        else
          if (x + y) % 2 == 0 and (x % 2 == 0) then c = DUST.lo end
        end
        if c then lg.setColor(c); lg.rectangle("fill", x, y, 1, 1) end
      end
    end
  end
end

-- a drop: 2 x 2 for the crown's first moments, then 1 px, 2 px tall while it moves fast
local function drawDrop(q, cam)
  local t = q.t
  local x = math.floor(q.x + q.vx * t - cam + 0.5)
  local vy = q.vy + q.g * t
  local y = math.floor(q.y + q.vy * t + 0.5 * q.g * t * t + 0.5)
  if y > q.y then return end
  lg.setColor(WATER[q.c])
  if q.big and t < 0.16 then lg.rectangle("fill", x, y, 2, 2)
  else lg.rectangle("fill", x, y, 1, math.abs(vy) > 60 and 2 or 1) end
end
-- the foam line where she broke the surface: broken 1 px dashes across her, that thin out
local function drawFoam(q, cam)
  local k = q.t / q.life
  local cx, y = math.floor(q.x - cam + 0.5), q.y
  local hw = (k < 0.1) and 16 or 13
  for dx = -hw, hw do
    local keep = (k < 0.5 and (dx + 40) % 5 ~= 0) or (k >= 0.5 and k < 0.8 and (dx + 40) % 2 == 0)
      or (k >= 0.8 and (dx + 40) % 4 == 0)
    if keep then lg.setColor(WATER[(math.abs(dx) > hw - 3 or k >= 0.5) and 2 or 1]); lg.rectangle("fill", cx + dx, y, 1, 1) end
  end
  if k < 0.12 then                                              -- the first moment: a burst of white water
    lg.setColor(WATER[1]); lg.rectangle("fill", cx - 8, y - 1, 17, 1); lg.rectangle("fill", cx - 5, y - 2, 11, 1)
    lg.setColor(WATER[2]); lg.rectangle("fill", cx - 3, y - 3, 7, 1)
  end
end
-- a ripple sliding away along the surface, getting shorter and darker
local function drawRipple(q, cam)
  local k = q.t / q.life
  local x = math.floor(q.x - cam + q.dir * (16 + 22 * k) + 0.5)
  local len = k < 0.4 and 4 or (k < 0.75 and 3 or 2)
  lg.setColor(WATER[k < 0.4 and 2 or (k < 0.75 and 3 or 4)])
  lg.rectangle("fill", q.dir > 0 and x or x - len + 1, q.y + 1, len, 1)
end

-- a tiny 3 x 5 font for the points
local DIGIT = { ["+"] = { ".#.", "###", ".#." }, ["0"] = { "###", "#.#", "#.#", "#.#", "###" }, ["1"] = { ".#.", "##.", ".#.", ".#.", "###" } }
local function tiny(text, x, y, c)
  lg.setColor(c)
  for i = 1, #text do
    local g = DIGIT[text:sub(i, i)]
    local oy = (#g == 3) and 1 or 0
    for r, row in ipairs(g) do
      for col = 1, 3 do if row:sub(col, col) == "#" then lg.rectangle("fill", x + (i - 1) * 4 + col - 1, y + oy + r - 1, 1, 1) end end
    end
  end
end
-- a bone pop: a 4-point twinkle that opens up and breaks into dots, and the points rising and blinking out
local function drawPop(q, cam)
  local t = q.t
  local cx, cy = math.floor(q.x - cam + 0.5), math.floor(q.y + 0.5)
  local hi = q.super and BONE.gold or BONE.bone
  if t < 0.07 then
    lg.setColor(BONE.white); lg.rectangle("fill", cx - 1, cy, 3, 1); lg.rectangle("fill", cx, cy - 1, 1, 3)
  elseif t < 0.16 then
    lg.setColor(hi); lg.rectangle("fill", cx - 3, cy, 7, 1); lg.rectangle("fill", cx, cy - 3, 1, 7)
    lg.setColor(BONE.white); lg.rectangle("fill", cx - 1, cy, 3, 1); lg.rectangle("fill", cx, cy - 1, 1, 3)
  elseif t < 0.26 then
    lg.setColor(hi)
    for _, d in ipairs({ 3, 4 }) do
      lg.rectangle("fill", cx - d, cy, 1, 1); lg.rectangle("fill", cx + d, cy, 1, 1)
      lg.rectangle("fill", cx, cy - d, 1, 1); lg.rectangle("fill", cx, cy + d, 1, 1)
    end
    lg.setColor(BONE.white)
    for _, d in ipairs({ -2, 2 }) do lg.rectangle("fill", cx + d, cy + d, 1, 1); lg.rectangle("fill", cx + d, cy - d, 1, 1) end
  elseif t < 0.34 then
    lg.setColor(hi)
    lg.rectangle("fill", cx - 5, cy, 1, 1); lg.rectangle("fill", cx + 5, cy, 1, 1)
    lg.rectangle("fill", cx, cy - 5, 1, 1); lg.rectangle("fill", cx, cy + 5, 1, 1)
  end
  if t >= 0.08 and (t < 0.55 or math.floor(t * 20) % 2 == 0) then   -- the points: rise 11 px, then blink out
    local text = q.super and "+1000" or "+100"
    local w = #text * 4 - 1
    local y = cy - 7 - math.floor(math.min(1, (t - 0.08) / 0.4) * 11)
    local x = cx - math.floor(w / 2)
    tiny(text, x + 1, y + 1, BONE.dark); tiny(text, x, y, hi)
  end
end

local function draw(fx, cam, front)
  if not Ex.enabled then return end
  for _, q in ipairs(fx.parts) do
    if (q.front or false) == front then
      if q.kind == "puff" then drawPuff(q, cam)
      elseif q.kind == "drop" then drawDrop(q, cam)
      elseif q.kind == "foam" then drawFoam(q, cam)
      elseif q.kind == "ripple" then drawRipple(q, cam)
      elseif q.kind == "pop" then drawPop(q, cam) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
function Ex.drawBehind(fx, cam) draw(fx, cam, false) end      -- right before Pepper
function Ex.drawFront(fx, cam) draw(fx, cam, true) end        -- right after Pepper (and the ball she carries)
return Ex
