-- Small visual extras around Pepper, 90s console style: hard 1 px pixels, a few palette steps, no blur.
-- Drawing only. They watch Pepper's state from outside (stage.lua calls Ex.update after her update) and never
-- change it, so she moves exactly as before (tools/check_pepper.sh proves it). Each one has its own switch;
-- E toggles them all off and on in the game (A/B), `--noextras` starts with them off.
local Ex = {}
local lg = love.graphics

Ex.on = {                       -- the switches, all on by default
  dust_land = true,             -- puffs at her paws when she lands from a real fall (12 px or more), bigger the higher
  dust_skid = true,             -- small puffs off her front paws while she skids
}
Ex.enabled = true               -- the master switch (E key, --noextras)
function Ex.toggle() Ex.enabled = not Ex.enabled end

local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end
-- dust: the pavement's warm greys, a step or two lighter than its lightest stone (the kerb, e5ddda), so it reads
-- as dust kicked off the paving and not as more paving
local DUST = { hi = hex("f7f3f0"), body = hex("ebe5e1"), lo = hex("cdc7c5") }

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
  if not was then return end
  local jumped = math.abs(now.x - was.x) > 20 or math.abs(now.y - was.y) > 40     -- a respawn or a test teleport
  if not now.onGround then fx.minY = math.min(fx.minY or now.y, now.y, was.y) end
  if not Ex.enabled or jumped then if now.onGround then fx.minY = nil end; return end

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

local function draw(fx, cam, front)
  if not Ex.enabled then return end
  for _, q in ipairs(fx.parts) do
    if (q.front or false) == front then
      if q.kind == "puff" then drawPuff(q, cam) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
function Ex.drawBehind(fx, cam) draw(fx, cam, false) end      -- right before Pepper
function Ex.drawFront(fx, cam) draw(fx, cam, true) end        -- right after Pepper (and the ball she carries)
return Ex
