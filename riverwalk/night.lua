-- Level 5 (Night Harbour): the night rules. stage.lua calls these through a few marked hooks (s.night).
--   darkness  (L.dark) a 320 x 240 canvas, dark blue, deeper at the top; light pools are stamped into it with
--             dithered, banded light sprites (blend multiply: cheap on the RG35XX, no shader). Lights: every lamp
--             post, L.lights (lanterns, boat lights, windows, the porch) and Pepper's own glow, so nothing ever
--             covers her. After the darkness: stars and the moon, a faint moonlit edge on every floor Pepper can
--             stand on (terrain tops, props, boats, the water's surface), so the path always reads.
--   sniff     hold L1 / R1 (handheld) or Q: standing on the ground, Pepper stops and sniffs (her own sniff clip).
--             A trail of glowing dots runs from her nose towards the fox's hideout (or the dropped ball, or Mia
--             when she carries it), and the bones nearby glow. Her movement code is not touched: while she sniffs
--             the stage simply does not run her controller (see Nt.sniffing).
--   bones     in the dark a bone shows only inside a light, or while she sniffs (within 200 px).
--   fox       (L.fox) it has Mia's ball. It sits on the quay, runs off when Pepper comes close, then hides at each
--             hideout in turn. Hidden, it can not be seen: sniffing close by (FIND px) finds it (its eyes shine), and
--             then a bark close enough chases it on; at the last one it drops the ball and is gone.
--   crumble   (props with crumble = true) 0.5 s after Pepper stands on one it shakes and falls into the water; it
--             is back 3 s later (once she is not in its way). Drawn here, over the darkness, so they always read.
local I = require("input")
local S = require("sfx")
local Sc = require("scene")
local F = require("bigfont")
local lg = love.graphics
local Nt = {}

local DARK_TOP, DARK_BOTTOM = 0.86, 0.66          -- how dark the night is at the top of the screen and at the bottom
local NIGHT = { 0.03, 0.04, 0.12 }
local SHAKE, GONE = 0.5, 3.0                      -- a crumbling plank: shakes this long, then is gone this long
local SNIFF_REACH = 200                            -- the trail's length; how far sniffing shows bones
local FIND = 150                                   -- sniffing this close to the hidden fox finds it

-- the darkness canvas and the light sprites (dithered bands: clear in the middle, 2 steps of dusk to the edge)
local darkCv, lightImg, glowImg = nil, {}, {}
local ballImg
local function ball() if not ballImg then ballImg = lg.newImage("art/ball.png"); ballImg:setFilter("nearest", "nearest") end; return ballImg end
local BAYER = { { 0, 8, 2, 10 }, { 12, 4, 14, 6 }, { 3, 11, 1, 9 }, { 15, 7, 13, 5 } }
local function lightSprite(r)
  if lightImg[r] then return lightImg[r] end
  local n = r * 2
  local d = love.image.newImageData(n, n)
  for y = 0, n - 1 do for x = 0, n - 1 do
    local k = math.sqrt((x + 0.5 - r) ^ 2 + (y + 0.5 - r) ^ 2) / r      -- 0 in the middle, 1 at the edge
    local v                                                            -- what is left of the darkness
    if k < 0.55 then v = 0 elseif k >= 1 then v = 1 else
      local t = (k - 0.55) / 0.45 * 3                                    -- 3 bands, dithered between them
      local band, frac = math.floor(t), t - math.floor(t)
      if frac * 16 > BAYER[y % 4 + 1][x % 4 + 1] then band = band + 1 end
      v = math.min(1, band / 3)
    end
    d:setPixel(x, y, v, v, v, v)                                         -- premultiplied (for blend multiply)
  end end
  lightImg[r] = lg.newImage(d); lightImg[r]:setFilter("nearest", "nearest")
  return lightImg[r]
end
local function glowSprite(r)                                             -- a small warm glow, added on top
  if glowImg[r] then return glowImg[r] end
  local n = r * 2
  local d = love.image.newImageData(n, n)
  for y = 0, n - 1 do for x = 0, n - 1 do
    local k = math.sqrt((x + 0.5 - r) ^ 2 + (y + 0.5 - r) ^ 2) / r
    local a = k < 1 and (1 - k) ^ 2 * 0.22 or 0
    d:setPixel(x, y, a, a * 0.78, a * 0.42, a)
  end end
  glowImg[r] = lg.newImage(d); glowImg[r]:setFilter("nearest", "nearest")
  return glowImg[r]
end

-- the sniff button: L1 / R1 on the handheld, Q on the keyboard (tests: I.force.sniff)
function Nt.sniffHeld()
  if I.force.sniff then return true end
  if I.testing then return false end
  if love.keyboard.isDown("q") then return true end
  return I.pad ~= nil and (I.pad:isGamepadDown("leftshoulder") or I.pad:isGamepadDown("rightshoulder"))
end

function Nt.new(s, def)
  local n = { dark = def.dark, lights = {}, planks = {}, tops = {}, water = {}, stars = {}, sniff = false, sniffT = 0 }
  for _, l in ipairs(def.lamps or {}) do n.lights[#n.lights + 1] = { x = l.x, y = l.y - 34, r = 60, kind = "lamp" } end
  for _, l in ipairs(def.lights or {}) do n.lights[#n.lights + 1] = l end
  for _, p in ipairs(def.props) do
    if p.crumble then n.planks[#n.planks + 1] = { p = p, st = "idle", t = 0 } end
  end
  -- the moonlit edges: the top cell of every terrain column and the water's surface, merged into runs
  local w = s.world
  local function runs(ch, list)
    local y0s = {}
    for c = 1, w.cols do
      y0s[c] = false
      for r = 1, w.rows do
        local k = w.map[r]:sub(c, c)
        if k == ch then y0s[c] = (r - 1) * 8; break elseif k ~= "." then break end
      end
    end
    local c = 1
    while c <= w.cols do
      if y0s[c] then
        local c1 = c
        while c1 < w.cols and y0s[c1 + 1] == y0s[c] do c1 = c1 + 1 end
        list[#list + 1] = { x0 = (c - 1) * 8, x1 = c1 * 8, y = y0s[c] }
        c = c1 + 1
      else c = c + 1 end
    end
  end
  runs("#", n.tops); runs("~", n.water)
  local seed = 7
  for i = 1, 46 do                                                       -- the stars (screen space, slow parallax)
    seed = (seed * 1103515245 + 12345) % 2147483648; local x = seed % 640
    seed = (seed * 1103515245 + 12345) % 2147483648; local y = 4 + seed % 52
    n.stars[i] = { x = x, y = y, ph = i * 0.7 }
  end
  if def.fox then
    n.fox = { x = def.fox.x, y = def.fox.y, state = "sit", i = 0, t = 0, dir = -1 }
    s.ball.state = "fox"
  end
  return n
end

-- what the sniff trail points at: the fox's hideout, the dropped ball, or Mia (with the ball)
local function target(s)
  local n, b = s.night, s.ball
  if s.pepper.carrying then return s.girl.x, s.girl.y end
  if b.state == "rest" or b.state == "air" then return b.x, b.y end
  local f = n.fox
  if f and f.state ~= "gone" then
    if f.state == "run" then return f.tx, f.ty end
    if f.state == "hide" then local h = s.def.fox.hideouts[f.i]; return h.x, h.y end
    return f.x, f.y
  end
end
Nt.target = target

-- the fox ------------------------------------------------------------------------------------------------------
local function runTo(f, x, y, after)
  f.state, f.t, f.found, f.sniffed = "run", 0, false, 0
  f.fx, f.fy, f.tx, f.ty, f.after = f.x, f.y, x, y, after
  f.dur = math.max(0.5, math.abs(x - f.x) / 170)
  f.hops = math.max(1, math.ceil(math.abs(x - f.x) / 60))
  f.dir = x > f.x and 1 or -1
  S.play("flap")
end
local function updateFox(s, dt)
  local f, d, p, b = s.night.fox, s.def.fox, s.pepper, s.ball
  if not f or f.state == "gone" then return end
  f.t = f.t + dt
  if f.state == "hide" and not f.found and s.night.sniff and math.abs(p.x - f.x) < FIND and math.abs(p.y - f.y) < 60 then
    f.sniffed = (f.sniffed or 0) + dt                                    -- a moment's sniffing finds it
    if f.sniffed >= 0.4 then f.found = true; S.play("heart"); s:say("THERE IT IS! BARK!", 2) end
  end
  if f.state == "sit" then
    f.dir = p.x < f.x and -1 or 1
    if math.abs(p.x - f.x) < d.flee then
      local h = d.hideouts[1]; f.i = 1; runTo(f, h.x, h.y, "hide")
      s:say("THE FOX RAN OFF WITH MY BALL!", 2.6)
    end
  elseif f.state == "run" then
    local k = math.min(1, f.t / f.dur)
    f.x = f.fx + (f.tx - f.fx) * k
    local ph = (k * f.hops) % 1
    f.y = f.fy + (f.ty - f.fy) * k - math.sin(ph * math.pi) * 18
    if k >= 1 then
      f.x, f.y = f.tx, f.ty
      if f.after == "hide" then f.state, f.t = "hide", 0 else f.state = "gone"; f.x = -999 end
    end
  end
  if b.state == "fox" then b.x, b.y = f.x + f.dir * 11, f.y - 6 end
end
-- a bark: at the fox on the quay or in its hideout, close enough, it runs on (and drops the ball at the last one)
function Nt.bark(s)
  local n, d, p, b = s.night, s.def.fox, s.pepper, s.ball
  local f = n.fox
  if not f or (f.state ~= "hide" and f.state ~= "sit") then return end
  local fx, fy = f.x, f.y
  if math.abs(p.x - fx) > d.bark or math.abs(p.y - fy) > 48 or (f.state == "hide" and not f.found) then f.heard = s.t; return end
  if f.state == "sit" then local h = d.hideouts[1]; f.i = 1; runTo(f, h.x, h.y, "hide"); return end
  if f.i < #d.hideouts then
    local h = d.hideouts[f.i + 1]; f.i = f.i + 1
    runTo(f, h.x, h.y, "hide")
    s:say(f.i == #d.hideouts and "IT'S RUNNING TO THE JETTY!" or "THERE IT GOES! SNIFF AGAIN!", 2.4)
  else
    b.state, b.x, b.y, b.vx, b.vy, b.airT = "air", f.x, f.y - 6, 0, -40, 0  -- it drops the ball and is gone
    b.home = { x = f.x, y = f.y }
    runTo(f, s.world.width + 60, f.y, "gone")
    s:say("IT DROPPED THE BALL!", 2.4)
  end
end
-- the hint conditions for the fox (St:zoneHint asks for the needs it does not know)
function Nt.need(s, need)
  local f, d, p = s.night.fox, s.def.fox, s.pepper
  if not f then return false end
  if need == "fox" then return s.ball.state == "fox" end
  if need == "dropped" then return not p.carrying and (s.ball.state == "rest" or s.ball.state == "air") end
  if need == "foxhidden" then return s.ball.state == "fox" and (f.state == "hide" or f.state == "run") end
  if need == "sniffhere" then
    return f.state == "hide" and not f.found and math.abs(p.x - f.x) < 240
  end
  if need == "foxnear" then
    return (f.state == "sit" or (f.state == "hide" and f.found)) and s.ball.state == "fox" and math.abs(p.x - f.x) <= d.bark and math.abs(p.y - f.y) <= 48
  end
  return true
end

-- crumbling planks ------------------------------------------------------------------------------------------------
local function remove(w, p) for i, r in ipairs(w.rects) do if r == p then table.remove(w.rects, i); return end end end
local function updatePlanks(s, dt)
  local p, w = s.pepper, s.world
  for _, k in ipairs(s.night.planks) do
    k.t = k.t + dt
    if k.st == "idle" then
      if p.onGround and p.ground == k.p then k.st, k.t = "shake", 0; S.play("scramble") end
    elseif k.st == "shake" and k.t >= SHAKE then
      k.st, k.t = "gone", 0; remove(w, k.p); S.play("splash")
    elseif k.st == "gone" and k.t >= GONE then
      local x0, y0, x1, y1 = p:box()
      if not (x1 > k.p.x0 and x0 < k.p.x1 and y1 > k.p.y0 - 2 and y0 < k.p.y1) then
        k.st, k.t = "idle", 0; w.rects[#w.rects + 1] = k.p
      end
    end
  end
end

-- the stage's update hook (after the bark rings): sniffing, the fox, the planks
function Nt.update(s, dt)
  local n = s.night
  n.sniffT = n.sniff and n.sniffT + dt or 0
  updateFox(s, dt)
  updatePlanks(s, dt)
end
-- the stage asks this before running Pepper's controller: true = she sniffs this step (it is skipped)
function Nt.sniffing(s, dt)
  local n, p = s.night, s.pepper
  n.sniff = Nt.sniffHeld() and p.mode == "normal" and p.onGround and not p.crouch
  if not n.sniff then return false end
  p.vx = 0; p.invuln = math.max(0, p.invuln - dt); p.barked = false
  if p.ground and p.ground.dx then p.x = p.x + p.ground.dx end             -- on a rowboat she rides with it
  if p.anim ~= "sniff" then p.anim, p.frame, p.at = "sniff", 1, 0 end
  p:animate(dt)
  return true
end

-- lights and bones ------------------------------------------------------------------------------------------------
local function lit(s, x, y)
  for _, l in ipairs(s.night.lights) do
    if (x - l.x) ^ 2 + (y - l.y) ^ 2 < (l.r * 0.8) ^ 2 then return true end
  end
  local p = s.pepper
  return (x - p.x) ^ 2 + (y - p.y + 18) ^ 2 < 40 ^ 2
end
-- the stage asks before drawing a bone: true = it is hidden in the dark (not lit, not sniffed)
function Nt.hideBone(s, bn)
  local n = s.night
  if not n.dark then return false end
  if n.sniff and math.abs(bn.x - s.pepper.x) < SNIFF_REACH then return false end
  return not lit(s, bn.x, bn.y - 8)
end

-- drawing -----------------------------------------------------------------------------------------------------
local FOX = {                                                            -- 24 x 10, facing right
  run1 = {
    "....................k.k.",
    "....................okok",
    "w..................oooooy",
    "wwo......oooooooooooowwo",
    ".woooooooooooooooooww...",
    "..ooooooooooooooooow....",
    "....oo...........oo.....",
    "...kk.............kk....",
  },
  run2 = {
    "....................k.k.",
    "....................okok",
    "...................oooooy",
    "ww.......oooooooooooowwo",
    "wwoooooooooooooooooww...",
    "..ooooooooooooooooow....",
    ".....ook.......ook......",
    "......k.........k.......",
  },
  sit = {
    "...........k.k",
    "...........okok",
    "..........oooooy",
    "..........oowwo.",
    ".........ooww...",
    "w.......ooow....",
    "ww.....oooo.....",
    "wwoooooooo......",
    ".oooooooo.......",
    "..kk..kk........",
  },
}
local FCOL = { o = { 0.84, 0.43, 0.16 }, k = { 0.16, 0.10, 0.08 }, w = { 0.95, 0.93, 0.88 }, y = { 0.10, 0.08, 0.08 } }
local function drawFox(s, f, cam, k)                                    -- k: brightness (moonlight)
  if f.state == "gone" or f.state == "hide" then return end
  local pose = f.state == "run" and ((math.floor(f.t * 12) % 2 == 0) and FOX.run1 or FOX.run2) or FOX.sit
  local x, y = math.floor(f.x - cam + 0.5), math.floor(f.y + 0.5)
  local h, w = #pose, #pose[1]
  for r, line in ipairs(pose) do
    for c = 1, #line do
      local col = FCOL[line:sub(c, c)]
      if col then
        local dx = f.dir > 0 and (c - 1 - math.floor(w / 2)) or (math.floor(w / 2) - c + 1)
        lg.setColor(col[1] * k, col[2] * k, col[3] * k); lg.rectangle("fill", x + dx, y - h + r - 1, 1, 1)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
-- the fox and the ball in its mouth. In the dark they are drawn over the darkness (moonlit, a little dimmer), so a
-- child can always see the fox run; without the darkness, with the characters
local function foxAndBall(s, cam, k)
  local f = s.night.fox
  if not f then return end
  drawFox(s, f, cam, k)
  if s.ball.state == "fox" and f.state ~= "hide" then
    lg.setColor(k, k, k, 1); lg.draw(ball(), math.floor(s.ball.x - cam - 3 + 0.5), math.floor(s.ball.y - 6 + 0.5))
  end
  lg.setColor(1, 1, 1, 1)
end
function Nt.drawWorld(s, cam)
  if not s.night.dark then foxAndBall(s, cam, 1) end
end

local function plankColour(k, a) return { 0.52 * a, 0.40 * a, 0.27 * a } end
local function drawPlanks(s, cam)
  for _, k in ipairs(s.night.planks) do
    local p = k.p
    local x, w = p.x0 - cam, p.x1 - p.x0
    if x < 330 and x + w > -10 then
      local dy, dx = 0, 0
      if k.st == "shake" then dx = (math.floor(k.t * 30) % 2 == 0) and 1 or -1 end
      if k.st == "gone" then dy = math.min(26, k.t * 80) end
      if not (k.st == "gone" and k.t > 0.4) then                          -- gone: it drops into the water
        lg.setColor(0.10, 0.08, 0.07); lg.rectangle("fill", math.floor(x + dx), p.y0 + dy, w, p.y1 - p.y0)
        lg.setColor(plankColour(k, 1)); lg.rectangle("fill", math.floor(x + dx) + 1, p.y0 + dy + 1, w - 2, p.y1 - p.y0 - 2)
        lg.setColor(0.30, 0.22, 0.15)                                    -- cracks: these planks are old
        for cx = 6, w - 4, 9 do lg.rectangle("fill", math.floor(x + dx) + cx, p.y0 + dy + 2, 1, 2) end
      end
      if k.st == "gone" and k.t > GONE - 0.6 then                        -- coming back: a faint outline first
        lg.setColor(0.6, 0.5, 0.35, 0.5); lg.rectangle("line", math.floor(x) + 0.5, p.y0 + 0.5, w - 1, p.y1 - p.y0 - 1)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- the lantern posts, ship lights and windows themselves (under the darkness: the light pool shows them)
function Nt.drawLights(s, cam)
  for _, l in ipairs(s.night.lights) do
    local x = math.floor(l.x - cam)
    if x > -20 and x < 340 then
      if l.kind == "lantern" or l.kind == "boat" then
        local base = 184
        lg.setColor(0.18, 0.18, 0.22); lg.rectangle("fill", x - 1, l.y + 4, 2, base - l.y - 4)
        lg.setColor(0.95, 0.80, 0.45); lg.rectangle("fill", x - 2, l.y - 2, 5, 6)
        lg.setColor(0.18, 0.18, 0.22); lg.rectangle("fill", x - 3, l.y - 4, 7, 2)
      elseif l.kind == "window" then
        lg.setColor(0.98, 0.84, 0.50); lg.rectangle("fill", x - 7, l.y - 9, 14, 18)
        lg.setColor(0.35, 0.25, 0.15); lg.rectangle("fill", x - 1, l.y - 9, 2, 18); lg.rectangle("fill", x - 7, l.y - 1, 14, 2)
      elseif l.kind == "porch" then
        lg.setColor(0.98, 0.86, 0.55); lg.rectangle("fill", x - 3, 130, 6, 5)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- the darkness and everything drawn over it (the stage's draw, at the very end)
function Nt.draw(s, cam)
  local n = s.night
  if n.dark then
    if not darkCv then darkCv = lg.newCanvas(320, 240); darkCv:setFilter("nearest", "nearest") end
    lg.push("all")
    lg.setCanvas(darkCv); lg.clear(0, 0, 0, 0); lg.origin(); lg.setBlendMode("alpha", "alphamultiply")
    for y = 0, 239, 8 do                                                -- deeper at the top (the sky)
      local a = DARK_TOP + (DARK_BOTTOM - DARK_TOP) * math.min(1, y / 200)
      lg.setColor(NIGHT[1], NIGHT[2], NIGHT[3], a); lg.rectangle("fill", 0, y, 320, 8)
    end
    lg.setBlendMode("multiply", "premultiplied"); lg.setColor(1, 1, 1, 1)
    local p = s.pepper
    local function stamp(x, y, r) local im = lightSprite(r); lg.draw(im, math.floor(x - r), math.floor(y - r)) end
    for _, l in ipairs(n.lights) do
      local x = l.x - cam
      if x > -l.r and x < 320 + l.r then stamp(x, l.y, l.r) end
    end
    stamp(p.x - cam, p.y - 20, 60)                                       -- her own glow: she is never in the dark
    lg.pop()
    lg.push("all")
    lg.setBlendMode("alpha", "premultiplied"); lg.setColor(1, 1, 1, 1); lg.draw(darkCv, 0, 0)
    lg.setBlendMode("add")                                               -- a warm glow round each light
    for _, l in ipairs(n.lights) do
      local x = l.x - cam
      if x > -l.r and x < 320 + l.r then local g = glowSprite(math.floor(l.r * 0.6)); lg.draw(g, math.floor(x - l.r * 0.6), math.floor(l.y - l.r * 0.6)) end
    end
    lg.pop()
    -- the sky: stars and the moon
    for _, st in ipairs(n.stars) do
      local x = math.floor((st.x - cam * 0.02) % 330) - 5
      local a = 0.55 + 0.4 * math.sin(s.t * 2 + st.ph)
      lg.setColor(0.9, 0.92, 1, a); lg.rectangle("fill", x, st.y, 1, 1)
    end
    lg.setColor(0.93, 0.93, 0.82); lg.circle("fill", 262, 30, 9); lg.setColor(0.03, 0.04, 0.12); lg.circle("fill", 266, 27, 8)
    -- the moonlit edges of every floor Pepper may need (terrain, props she can stand on, the boats, the water)
    lg.setColor(0.55, 0.64, 0.82, 0.55)
    for _, r in ipairs(n.tops) do
      local x0, x1 = r.x0 - cam, r.x1 - cam
      if x1 > 0 and x0 < 320 then lg.rectangle("fill", math.floor(x0), r.y, x1 - x0, 1) end
    end
    for _, pr in ipairs(s.def.props) do
      if (pr.kind == "solid" or pr.kind == "oneway") and not pr.hidden then
        local x0, x1 = pr.x0 - cam, pr.x1 - cam
        if x1 > 0 and x0 < 320 then
          lg.rectangle("fill", math.floor(x0), pr.y0, x1 - x0, 1)
          if pr.kind == "solid" then lg.rectangle("fill", math.floor(x0), pr.y0, 1, math.min(pr.y1, 184) - pr.y0); lg.rectangle("fill", math.floor(x1) - 1, pr.y0, 1, math.min(pr.y1, 184) - pr.y0) end
        end
      end
    end
    for _, m in ipairs(s.movers) do lg.rectangle("fill", math.floor(m.x0 - cam), m.y0, m.x1 - m.x0, 1) end
    lg.setColor(0.45, 0.62, 0.85, 0.65)
    for _, r in ipairs(n.water) do                                       -- the water: a shimmering line
      for x = math.max(r.x0, cam - 8), math.min(r.x1, cam + 328) - 4, 6 do
        if math.sin(x * 0.3 + s.t * 3) > -0.2 then lg.rectangle("fill", math.floor(x - cam), r.y + (x % 12 == 0 and 1 or 0), 4, 1) end
      end
    end
    lg.setColor(1, 1, 1, 1)
  end
  drawPlanks(s, cam)
  if n.dark then foxAndBall(s, cam, 0.8) end
  local f = n.fox
  if f and f.state ~= "gone" and n.dark then                             -- the fox's eyes shine in the dark
    local ex, ey = f.x - cam, f.y - 7
    if f.state == "hide" then
      if f.found and math.floor(s.t * 1.3) % 3 ~= 0 then
        lg.setColor(0.95, 0.85, 0.35); lg.rectangle("fill", math.floor(ex) - 3, math.floor(ey) + 2, 1, 1); lg.rectangle("fill", math.floor(ex) + 1, math.floor(ey) + 2, 1, 1)
      end
      if f.heard and s.t - f.heard < 0.8 then lg.setColor(Sc.C.label); F.print("?", math.floor(ex) - 2, math.floor(ey) - 14, 1) end
    else
      lg.setColor(0.95, 0.85, 0.35); lg.rectangle("fill", math.floor(ex + f.dir * 9), math.floor(ey) - 1, 1, 1)
    end
  end
  -- the ball and Mia keep a faint glow, so a child can always find them
  local b = s.ball
  if n.dark and (b.state == "rest" or b.state == "air") then
    lg.setColor(1, 1, 1, 0.55); lg.draw(ball(), math.floor(b.x - cam - 3 + 0.5), math.floor(b.y - 6 + 0.5))
  end
  -- sniffing: the trail of glowing dots and the bones nearby
  if n.sniff then
    local p = s.pepper
    local tx, ty = target(s)
    if tx then
      local dir = tx > p.x and 1 or -1
      local dist = math.min(math.abs(tx - p.x), SNIFF_REACH)
      local x0 = p.x + dir * 22
      for d = 0, dist - 22, 10 do
        local k = d / SNIFF_REACH
        local pulse = (math.sin(s.t * 8 - d * 0.12) + 1) / 2
        lg.setColor(1, 0.86, 0.35, (0.35 + 0.55 * pulse) * (1 - k * 0.6))
        local x = math.floor(x0 + dir * d - cam)
        local y = math.floor(p.y - 4 + (ty - p.y) * (d / math.max(1, math.abs(tx - p.x))))
        lg.rectangle("fill", x, y, 2, 2)
      end
      if math.abs(tx - p.x) > SNIFF_REACH then                           -- further on: an arrow at the end
        local x = math.floor(x0 + dir * (SNIFF_REACH - 12) - cam)
        lg.setColor(1, 0.86, 0.35, 0.9)
        for i = 0, 3 do lg.rectangle("fill", x + dir * i, p.y - 4 - (3 - i), 1, 2 * (3 - i) + 1) end
      end
    end
    local art = Sc.art()
    for _, bn in ipairs(s.bones) do
      if not bn.taken and math.abs(bn.x - p.x) < SNIFF_REACH then
        lg.setColor(1, 0.95, 0.7, 0.55 + 0.35 * math.sin(s.t * 6 + bn.x))
        lg.draw(bn.super and art.bone_gold or art.bone, math.floor(bn.x - cam + 0.5) - 5, bn.y - 12)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

return Nt
