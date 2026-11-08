-- Level art for Night Harbour (levelart.lua; 8 Nov 2026, phase 1, 0 credits: built by rule, code and built pixels).
-- The palette is one table (levelart/night/palette.lua), sampled from the picked concept (nh_home_concept_b.png).
-- The built parts are PNGs from tools/build_night_kit.py (levelart/night/*.png); the rest is flat fills here.
-- Parts, in the order they were added:
--   A  labels off: every prop and boat is drawn without its greybox name (the debug view still has the boxes)
--   B  holders and contacts: nothing floats. Crates stacked from one built crate (one ink seam between two), the
--      net shed's roof on its posts with the nets hung under it, the fish shed with its ledge on three brackets, the
--      low jetty on its legs, the mooring post standing in the water (wet below the waterline), the old jetty's
--      piles under every crumbling plank (they stay when a plank falls), the boats sitting in the water with their
--      lantern on a mast (it rides with the boat), the lanterns on posts, the lamp posts on the paving, the house's
--      lantern on a bracket, a contact shadow under everything that stands on the quay.
--   C+D the quay and the water by rule, every join designed (M:paintGround, below)
--   E  the backdrop by rule: sky, far town, the bay's far shore, each on its own ground (M:drawFar)
--   F  the night light model: stepped amber pools on the paving, small two-step halos, the lights and the moon
--      reflected in the water, a small glow and a moonlit rim on Pepper (with night.lua Nt.drawArtLight); the
--      level's colour script (M.look)
local Sc = require("scene")
local lg = love.graphics
local M = {}
M.__index = M

local P = {}                                                        -- the palette as colours (0-1)
for k, v in pairs(require("levelart.night.palette")) do
  P[k] = { tonumber(v:sub(1, 2), 16) / 255, tonumber(v:sub(3, 4), 16) / 255, tonumber(v:sub(5, 6), 16) / 255 }
end
M.P = P

local IMG = {}
local function img(n)
  if not IMG[n] then IMG[n] = lg.newImage("levelart/night/" .. n .. ".png"); IMG[n]:setFilter("nearest", "nearest") end
  return IMG[n]
end
local function box(c, x, y, w, h) if w > 0 and h > 0 then lg.setColor(c); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end end
local function at(im, x, y) lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x), math.floor(y)) end
M.box, M.img = box, img

local WATERLINE = 208                                                -- the water's surface at Pepper's depth
M.WATERLINE = WATERLINE

-- what each prop is (worked out once from the level's props: the art follows the level)
local function classify(def)
  local K = {}
  for _, p in ipairs(def.props) do
    local k
    if p.crumble then k = "plank"
    elseif p.name == "TARP" then k = "tarp"
    elseif p.name == "NET SHED" then k = "netroof"
    elseif p.name == "ROOF" then k = "ledge"
    elseif p.name == "POST" then k = "post"
    elseif p.name == "LOW JETTY" then k = "jetty"
    elseif p.name == "HOME" then k = "house"
    elseif p.name == "DOOR" then k = "door"
    elseif p.layer == "front" then k = "frontpile"
    elseif p.kind == "decor" and p.layer == "back" and p.x1 - p.x0 <= 6 then k = "leg"        -- shed posts, jetty legs
    elseif p.kind == "decor" and p.layer == "back" and p.y0 <= 104 then k = "fishshed"
    elseif p.kind == "decor" and p.layer == "back" then k = "backcrates"
    elseif p.kind == "solid" then k = "crates" end
    K[p] = k
  end
  return K
end

function M.new(stage)
  local o = setmetatable({ stage = stage, def = stage.def, world = stage.world }, M)
  o.K = classify(o.def)
  -- the boat lights ride on a boat: each light of kind "boat" goes with the mover nearest to it (where it starts)
  o.boatOf = {}
  for _, l in ipairs(o.def.lights or {}) do
    if l.kind == "boat" then
      local best, bd
      for _, m in ipairs(stage.movers or {}) do
        local d = math.abs((m.from + (m.x1 - m.x0) / 2) - l.x)
        if not bd or d < bd then best, bd = m, d end
      end
      o.boatOf[l] = best
    end
  end
  return o
end

-- where a light is drawn now (a boat's lantern rides its boat); nil = where the level puts it
function M:lightPos(l)
  local m = self.boatOf[l]
  if m then return m.x0 + 8, m.y0 - 20 end
end

-- B: things standing on the quay get a contact shadow (Sc.shadow, the same as every level)
local function foot(cx, y, w) Sc.shadow(cx, y - 1, w) end

-- a crate stack: the built crate stamped on a 16 px grid, its outline closed on the right and the bottom (one
-- ink seam between two crates). `open` = a taller stack stands right against its right side (one seam, not two)
local function crates(p, cam, open)
  local x0 = math.floor(p.x0 - cam)
  local w, h = p.x1 - p.x0, p.y1 - p.y0
  local cell = img("crate_cell")
  for y = p.y0, p.y1 - 1, 16 do for x = 0, w - 1, 16 do at(cell, x0 + x, y) end end
  if not open then box(P.ink, x0 + w - 1, p.y0, 1, h) end
  box(P.ink, x0, p.y1 - 1, w, 1)
end

local function timberPost(x, y0, y1)                                  -- a 4 px post (decoration: no ink)
  box(P.pile2, x, y0, 4, y1 - y0); box(P.pile1, x, y0, 1, y1 - y0); box(P.pile3, x + 3, y0, 1, y1 - y0)
end

-- the pieces that stand on the quay behind Pepper: drawn by the ground (M:paintGround's draw), after the paving,
-- since the stage paints the ground after the back props (the paving's back course, y 172-193, would cover them)
local BACK = { tarp = true, leg = true, fishshed = true, backcrates = true, house = true }
M.BACK = BACK

function M:drawProp(pr, cam, colour, kicked)
  if BACK[self.K[pr]] then return true end                             -- (drawn with the ground)
  return self:art(pr, cam)
end

function M:art(pr, cam)
  local x, w = pr.x0 - cam, pr.x1 - pr.x0
  if x > 340 or x + w < -150 then return true end
  local k = self.K[pr]
  if pr.hidden or k == "plank" or k == "door" then return true end    -- (planks: night.lua, over the dark)
  if k == "crates" then
    local open = false
    for _, q in ipairs(self.def.props) do
      if q ~= pr and self.K[q] == "crates" and q.x0 == pr.x1 and q.y0 <= pr.y0 and q.y1 == pr.y1 then open = true end
    end
    foot(x + w / 2, pr.y1, w + 4)
    crates(pr, cam, open)
  elseif k == "tarp" then
    foot(x + 21, pr.y1, 14); foot(x + 67, pr.y1, 14)
    at(img("tarp"), x, pr.y1 - 24)
  elseif k == "leg" then
    foot(x + 2, pr.y1, 8)
    timberPost(x, pr.y0, pr.y1)
  elseif k == "netroof" then                                           -- the net shed's roof (an obstacle)
    local h = pr.y1 - pr.y0
    box(P.ink, x, pr.y0, w, h)
    box(P.wd2, x + 1, pr.y0 + 1, w - 2, h - 2)
    box(P.wd1, x + 1, pr.y0 + 1, w - 2, 1)
    box(P.wd3, x + 1, pr.y0 + h - 3, w - 2, 1)                         -- the fascia board's lower edge
    for bx = 8, w - 8, 16 do box(P.wd4, x + bx, pr.y0 + 2, 1, h - 5) end
  elseif k == "fishshed" then
    foot(x + w / 2, pr.y1, w + 6)
    at(img("fishshed"), x, pr.y0)
  elseif k == "ledge" then                                             -- the fish shed's loft ledge on 3 brackets
    for bx = 8, w - 8, math.floor((w - 16) / 2) do                     -- knee braces into the shed's boards
      for i = 0, 5 do box(P.wd3, x + bx - math.floor(i / 2), pr.y1 + i, 2, 1) end
      box(P.wd4, x + bx + 1, pr.y1, 1, 7)
    end
    local h = pr.y1 - pr.y0
    box(P.ink, x, pr.y0, w, h)
    box(P.wd2, x + 1, pr.y0 + 1, w - 2, h - 2)
    box(P.wd1, x + 1, pr.y0 + 1, w - 2, 1)
  elseif k == "backcrates" then
    local cb = img("crate_back")
    for y = pr.y1 - 16, pr.y0 + 8, -16 do for cx = 0, w - 1, 16 do at(cb, x + cx, y) end end
    at(img("rope"), x + 8, pr.y0)
    foot(x + w / 2, pr.y1, w + 4)
  elseif k == "post" then                                              -- the mooring pile, standing in the water
    at(img("post"), x, pr.y0)
  elseif k == "jetty" then                                             -- the low jetty's deck (an obstacle)
    local h = pr.y1 - pr.y0
    box(P.ink, x, pr.y0, w, h)
    box(P.wd2, x + 1, pr.y0 + 1, w - 2, h - 2)
    box(P.wd1, x + 1, pr.y0 + 1, w - 2, 1)
    box(P.wd4, x + 1, pr.y0 + h - 2, w - 2, 1)                         -- the stringer under the planks' ends
    for bx = 6, w - 6, 6 do box(P.wd3, x + bx, pr.y0 + 2, 1, h - 4) end   -- the planks' ends
    box(P.iron2, x + 5, pr.y0 + 3, 1, 1); box(P.iron2, x + w - 6, pr.y0 + 3, 1, 1)   -- bolts over the legs
  elseif k == "house" then
    foot(x + w / 2, pr.y1, w + 8)
    at(img("house"), x - 8, pr.y1 - 176)
  elseif k == "frontpile" then
    at(img("frontpile"), x, pr.y0)
  else
    return false                                                       -- (anything new: the greybox)
  end
  return true
end

-- the old jetty under the crumbling planks: two piles under each plank (3 px, down into the water, wet below the
-- waterline) and a cross brace between them. They stay when the plank falls: the jetty is old, its deck is not
function M:drawPiles(cam)
  for _, p in ipairs(self.def.props) do
    if self.K[p] == "plank" and p.x1 - cam > -10 and p.x0 - cam < 330 then
      local a, b = math.floor(p.x0 - cam) + 2, math.floor(p.x1 - cam) - 5
      for i = 0, WATERLINE - p.y1 - 4 do                                -- the brace (behind the piles)
        local k = i / (WATERLINE - p.y1 - 4)
        box(P.wd4, math.floor(a + 2 + (b - a - 2) * k), p.y1 + 1 + i, 1, 1)
      end
      for _, px in ipairs({ a, b }) do
        box(P.pile2, px, p.y1, 3, WATERLINE - p.y1); box(P.pile1, px, p.y1, 1, WATERLINE - p.y1)
        box(P.wet, px, WATERLINE, 3, 240 - WATERLINE); box(P.pile3, px, WATERLINE, 1, 240 - WATERLINE)
        box(P.door3, px, WATERLINE - 2, 3, 2)                          -- weed at the waterline
      end
    end
  end
end

-- the net shed's nets: hung from its roof between the posts, behind Pepper (decoration), sagging; cork floats
function M:drawNets(cam)
  for _, p in ipairs(self.def.props) do
    if self.K[p] == "netroof" and p.x1 - cam > -10 and p.x0 - cam < 330 then
      local x0, x1 = math.floor(p.x0 - cam) + 5, math.floor(p.x1 - cam) - 5
      local W = x1 - x0
      for x = 0, W - 1 do
        local sag = math.floor(6 * math.sin(math.pi * x / W) + 0.5)
        local bottom = p.y1 + 4 + sag
        for y = p.y1, bottom do
          local yy = y - p.y1
          if (x + yy) % 4 == 0 or (x - yy) % 4 == 0 then box(P.net2, x0 + x, y, 1, 1) end
        end
        box(P.net1, x0 + x, bottom, 1, 1)
        if x % 9 == 4 then box(P.wd1, x0 + x - 1, bottom + 1, 3, 2) end -- cork floats on the foot rope
      end
    end
  end
end

-- the lamp posts (checkpoints): lamp_post.png recoloured to dark iron (lamp_night.png), standing on the paving's
-- back course (foot y 174, as River Walk's); a passed checkpoint keeps River Walk's lamp light
function M:drawLamp(l, cam, t)
  local im = img("lamp_night")
  local x = math.floor(l.x - cam)
  local lx, top = x - math.floor(im:getWidth() / 2), l.y - Sc.EDGE - im:getHeight()
  Sc.shadow(x, l.y - Sc.EDGE - 1, 14)
  at(im, lx, top)
  if l.lit then Sc.lampLight(lx + im:getWidth() / 2, top + 17, t - (l.litAt or -9), t) end
  return true
end

-- the lights (night.lua asks before it draws one): lanterns on a post down to what holds them (the paving, the
-- mooring post), a boat's lantern on its boat's mast, the house's brass lantern on a bracket; the house's own
-- windows and porch are in its art
function M:drawLight(l, cam) return true end                         -- (drawn with the ground: M:lightArt)
function M:lightArt(l, cam)
  local x = math.floor(l.x - cam)
  if l.kind == "lantern" then
    local base = 178                                                   -- on the paving
    for _, p in ipairs(self.def.props) do                              -- or on the mooring post's cap
      if self.K[p] == "post" and l.x >= p.x0 and l.x < p.x1 then base = p.y0 end
    end
    if base == 178 then Sc.shadow(x, base, 8) end
    box(P.iron3, x - 2, base - 2, 5, 2); box(P.iron2, x - 1, base - 3, 3, 1)   -- its foot
    box(P.iron2, x - 1, l.y + 6, 2, base - 3 - l.y - 6); box(P.iron1, x - 1, l.y + 6, 1, base - 3 - l.y - 6)
    at(img("lantern"), x - 3, l.y - 4)
  elseif l.kind == "boat" then return true                              -- (drawn with its boat: drawMover)
  elseif l.kind == "window" and l.x == 4344 then                        -- the brass wall lantern by the door
    box(P.brass3, x - 1, l.y - 8, 6, 1); box(P.brass3, x + 4, l.y - 8, 1, 4)   -- its bracket into the wall
    box(P.brass2, x - 3, l.y - 7, 7, 2)
    box(P.brass2, x - 3, l.y - 5, 7, 9); box(P.glass, x - 2, l.y - 5, 5, 7); box(P.win2, x - 2, l.y + 1, 5, 1)
    box(P.brass1, x - 3, l.y - 5, 1, 9)
    box(P.brass2, x - 2, l.y + 4, 5, 1); box(P.brass3, x - 1, l.y + 5, 3, 1)
  end
  return true
end

-- the boats: the built hulls (deck on the mover's top row), sitting in the water: the waterline's ripple at both
-- ends and the hull's dark reflection broken under it; a boat that carries a light has a mast with the lantern
function M:drawMover(m, cam, t)
  local x = math.floor(m.x0 - cam + 0.5)
  local w = m.x1 - m.x0
  if x > 330 or x + w < -20 then return true end
  local im = img(w >= 56 and "rowboat" or "boat")
  for l, bm in pairs(self.boatOf) do
    if bm == m then                                                    -- the mast at the stern, the lantern on it
      local mx = x + 8
      box(P.wd3, mx, m.y0 - 16, 1, 16); box(P.wd2, mx - 1, m.y0 - 16, 1, 16)
      box(P.wd4, mx - 2, m.y0 - 1, 5, 1)
      at(img("lantern"), mx - 3, m.y0 - 24)
    end
  end
  at(im, x - 2, m.y0 - 2)
  local ph = math.floor(t * 4) % 2
  for i = 1, 3 do                                                      -- the ripple against the hull's ends
    if (i + ph) % 3 ~= 0 then box(P.w6, x - 2 - i, WATERLINE - 1, 1, 1); box(P.w6, x + w + 1 + i, WATERLINE - 1, 1, 1) end
  end
  for xx = 2, w - 3 do                                                 -- its reflection, broken
    if (xx + ph) % 5 ~= 0 then box(P.w0, x + xx, WATERLINE + 1, 1, 1) end
    if (xx + ph) % 3 ~= 0 and xx > 4 and xx < w - 5 then box(P.w0, x + xx, WATERLINE + 3, 1, 1) end
  end
  return true
end

-- the pass the ground draws after its paving and water: the old jetty's piles, the back pieces on the quay, the nets
-- and the lanterns (everything behind Pepper that stands on the paving or in the water)
function M:drawStanding(cam)
  self:drawReflections(cam, self.stage.t)
  self:drawPiles(cam)
  for _, pr in ipairs(self.def.props) do if BACK[self.K[pr]] then self:art(pr, cam) end end
  self:drawNets(cam)
  for _, l in ipairs(self.def.lights or {}) do
    local x = l.x - cam
    if x > -20 and x < 340 then self:lightArt(l, cam) end
  end
end

-- E: the backdrop by rule (screen space). Each layer stands on its own ground, never on the quay's top line:
--   sky       flat steps of the palette's navy (sky0 at the top to the violet-blue glow sky8 at the horizon), the
--             stars and the moon over it (they are behind everything now: no star over a mast or a roof)
--   far town far_town.png, the old town on the far shore with its spire and lit windows, scrolling 128 px over the
--             whole level (capped, never repeated), its foot on the far quay, under the bay's top row
--   shore    shore.png at 0.3: the boat sheds on their pier and the moored boats, standing in the bay (their own
--             water, water.png's top rows recoloured), their lights reflected in it; the bay runs down to the
--             paving's back edge (y 171), where the quay's wet row meets it
M.SKY = { { 0, "sky0" }, { 16, "sky1" }, { 31, "sky2" }, { 45, "sky3" }, { 58, "sky4" }, { 70, "sky5" }, { 81, "sky6" },
          { 91, "sky7" }, { 100, "sky8" } }
M.FAR_Y, M.SHORE_Y, M.SHORE_K, M.FAR_MAX = 40, 40, 0.3, 128
local MOON = {                                                        -- 13 x 13: a crescent, lit from the right
  "....mmmm.....", "..mmmmmm.....", ".mmmmmd......", ".mmmmd.......", "mmmmd........", "mmmmd........",
  "mmmmd........", "mmmmd........", "mmmmmd.......", ".mmmmd.......", ".mmmmmd......", "..mmmmmmd....", "....mmmm.....",
}
M.MOON_X, M.MOON_Y = 252, 18
function M:drawSky(t)
  for i, b in ipairs(M.SKY) do
    local y1 = M.SKY[i + 1] and M.SKY[i + 1][1] or 172
    box(P[b[2]], 0, b[1], 320, y1 - b[1])
  end
  local n = self.stage.night
  for i, st in ipairs(n and n.stars or {}) do                           -- (night.lua's stars, behind the town now)
    local x = math.floor((st.x - (self.stage.cam or 0) * 0.02) % 330) - 5
    if st.y < 100 and math.sin(t * 2 + st.ph) > -0.6 then box((i % 5 == 0) and P.star or P.moonHalo, x, st.y, 1, 1) end
    if i % 9 == 0 and st.y < 60 then box(P.star, x, st.y, 1, 1) end
  end
  for r, line in ipairs(MOON) do                                        -- the moon: a halo ring a step off the sky
    for c = 1, #line do
      local ch = line:sub(c, c)
      if ch == "m" then box(P.moon, M.MOON_X + c - 1, M.MOON_Y + r - 1, 1, 1)
      elseif ch == "d" then box(P.moonD, M.MOON_X + c - 1, M.MOON_Y + r - 1, 1, 1) end
    end
  end
end
function M:drawFar(cam, camY, t)
  self:drawSky(t)
  local W = self.world.width
  local fo = math.floor(cam * M.FAR_MAX / math.max(1, W - 320) + 0.5)
  at(img("far_town"), -fo, M.FAR_Y)
  local so = math.floor(cam * M.SHORE_K + 0.5)
  local sh = img("shore")
  at(sh, -so, M.SHORE_Y)
  self:drawBayMoon(t)
  lg.setColor(1, 1, 1, 1)
end

-- C+D: the quay and the water, painted once into chunks by rule (ImageData, one palette colour per pixel).
-- Front-on, as River Walk's quay: the paving's thin cap above and below Pepper's line (y 172-192: a back course of
-- 24 px slabs, a front course of 32 px slabs, each slab flat with a lit top row), the granite coping (y 193-198, a
-- lit arris, joints every 48 px) with its shadow, the wall of ashlar courses (10 px, 40 px blocks, half-bond) down to
-- the screen's bottom, a wet row where the bay meets the paving's back edge. The water in the gaps: water.png
-- recoloured whole-pixel (water_near.png), from the paving's back line down.
-- Joins (every change of kind, marked for joins.lua's check):
--   quay>water / water>quay   the quay-end cap (River Walk's, in granite): the end stone, the coping 2 px over the
--                             water with its shadow, quoins (long and short in turn), the arris wet below the
--                             waterline, a ripple along it, the wall's dark reflection stepping out
--   the slipway (x 3800)      a stone ramp (2 px run per 1 px drop) from the paving's back course down into the
--                             water, under it in the water's own colours; no overhang
--   the pier stub             the cap on both its sides
-- Bollards stand on the back course every so often (where nothing else stands), as in the concept.
local SLIPWAY = 3800                                                  -- the level's slipway (beat 13), a quay end
local PAVE0, FRONT0, CAP0, WALL0 = 172, 182, 193, 200                 -- the rows where each part starts
local function hash(i) return (i * 2654435761) % 4294967296 end

function M:groundMap()
  local w = self.world
  local W = w.width
  local top, kind = {}, {}
  for x = 0, W - 1 do
    for _, m in ipairs(Sc.columnRuns(w, x, "all")) do if m[1] >= 150 then top[x] = m[1]; break end end
    if top[x] then kind[x] = "quay"
    else
      for _, r in ipairs(w.water) do if x >= r.x0 and x < r.x1 then kind[x] = "water" end end
    end
  end
  local dL, dR = {}, {}
  local n
  for x = 0, W - 1 do if top[x] then n = (x > 0 and not top[x - 1]) and 0 or (n and n + 1); dL[x] = n else n = nil end end
  n = nil
  for x = W - 1, 0, -1 do if top[x] then n = (x < W - 1 and not top[x + 1]) and 0 or (n and n + 1); dR[x] = n else n = nil end end
  return top, kind, dL, dR
end

-- the kind map for joins.lua's check (Jn.check): quay and water, with this painter's marks
function M:joinKinds()
  local top, kind = self:groundMap()
  local K = {}
  for x = 0, self.world.width - 1 do K[x] = { kind = kind[x], top = top[x] } end
  return K
end

function M:paintGround(w)
  local Jn = require("joins")
  local W, H = w.width, 240
  local top, kind, dL, dR = self:groundMap()
  self.kind = kind
  local wn = love.image.newImageData("levelart/night/water_near.png")
  local WN = wn:getWidth()
  local data = love.image.newImageData(W, H)
  local function set(x, y, c, a)
    if x < 0 or x >= W or y < 0 or y >= H or not c then return end
    if a then
      local r, g, b = data:getPixel(x, y)
      data:setPixel(x, y, r + (c[1] - r) * a, g + (c[2] - g) * a, b + (c[3] - b) * a, 1)
    else data:setPixel(x, y, c[1], c[2], c[3], 1) end
  end
  local function lum(x, y) local r, g, b = data:getPixel(x, y); return 0.299 * r + 0.587 * g + 0.114 * b end
  -- the paving, coping and wall of a quay column (d: columns from its end, side: 1 = the water on its right)
  local function quayCol(x, d, side)
    set(x, PAVE0 - 1, P.wet)                                            -- the wet row along the bay
    set(x, PAVE0, P.g4)
    local bi = math.floor(x / 24)                                       -- the back course (y 173-180)
    for y = PAVE0 + 1, FRONT0 - 2 do
      local c = (hash(bi) % 3 == 0) and P.g3 or P.g2
      if y == PAVE0 + 1 then c = P.g1 end
      if x % 24 == 0 then c = P.g6 end
      set(x, y, c)
    end
    set(x, FRONT0 - 1, P.g6)
    local fi = math.floor((x + 12) / 32)                                -- the front course (y 182-192)
    for y = FRONT0, CAP0 - 1 do
      local c = (hash(fi + 7) % 3 == 1) and P.g3 or P.g2
      if y == FRONT0 then c = P.g1 elseif y == CAP0 - 1 then c = P.g4 end
      if (x + 12) % 32 == 0 then c = P.g6 end
      set(x, y, c)
    end
    for y = CAP0, WALL0 - 2 do                                          -- the coping (y 193-198)
      local c = (y == CAP0) and P.g1 or (y == WALL0 - 2 and P.g5 or P.g4)
      if x % 48 == 0 and y > CAP0 then c = P.g6 end
      set(x, y, c)
    end
    set(x, WALL0 - 1, P.g8)                                             -- its shadow on the wall
    for y = WALL0, H - 1 do                                             -- the wall: 10 px courses, 40 px blocks
      local k, r = math.floor((y - WALL0) / 10), (y - WALL0) % 10
      local c = (r == 0) and P.g7 or (r == 1 and P.g4 or P.g5)
      if r > 0 then
        local head
        if d and d < 30 then head = d == ((k % 2 == 0) and 13 or 25)   -- quoins: long and short in turn
        else head = (x + (k % 2) * 20) % 40 == 0 end
        if head then c = P.g7 end
      end
      if d == 0 then c = (side == -1) and P.g4 or P.g7 end              -- the corner's arris: lit on the left end
      if d and d <= 1 and y >= WATERLINE then c = P.wet end             -- wet below the waterline
      set(x, y, c)
    end
    if d and d <= 3 then                                                -- the end stone of the paving and coping
      local c = (d == 3) and P.g6 or (d == 0 and ((side == -1) and P.g1 or P.g4) or P.g2)
      for y = PAVE0 + 1, CAP0 - 1 do set(x, y, c) end
    end
  end
  for x = 0, W - 1 do
    if kind[x] == "water" then
      for y = PAVE0, H - 1 do set(x, y, { wn:getPixel(x % WN, y - PAVE0) }) end
    end
  end
  Jn.reset()
  for x = 0, W - 1 do
    if top[x] then
      local d, side = dL[x], -1
      if dR[x] and (not d or dR[x] < d) then d, side = dR[x], 1 end
      quayCol(x, d, side)
    end
  end
  -- the quay-end caps
  for x = 0, W - 1 do
    local side = (dR[x] == 0 and x + 1 < W and 1) or (dL[x] == 0 and x > 0 and -1) or nil
    if side then
      Jn.mark(side == 1 and x + 1 or x, side == 1 and "quay>water" or "water>quay")
      if not (side == 1 and x + 1 == SLIPWAY) then
        for i = 1, 2 do                                                 -- the coping over the water, its shadow
          local ox = x + side * i
          for y = PAVE0 + 1, CAP0 - 1 do set(ox, y, (i == 1) and P.g2 or P.g3) end
          set(ox, PAVE0, P.g4)
          for y = CAP0, WALL0 - 2 do set(ox, y, (y == CAP0) and P.g1 or P.g5) end
          set(ox, WALL0 - 1, P.w0); set(ox, WALL0, P.w0)
        end
      end
      for i = 2, 5 do                                                   -- the wall's reflection, stepping out
        local c = (i <= 3) and P.w0 or P.w1
        for y = WATERLINE + 1, H - 1 do
          if lum(x + side * i, y) > 0.299 * c[1] + 0.587 * c[2] + 0.114 * c[3] then set(x + side * i, y, c) end
        end
      end
      for i = 1, 6 do if i % 3 ~= 0 then set(x + side * i, WATERLINE, P.w6) end end   -- the ripple
    end
  end
  -- the slipway: a stone ramp from the back course into the water, 2 px run per 1 px drop, 4 px thick
  for i = 0, 63 do
    local x, yt = SLIPWAY + i, PAVE0 + 1 + math.floor(i / 2)
    if yt > WATERLINE - 4 then break end
    for k = 0, 4 do
      local y = yt + k
      local c = (k == 0) and P.g1 or (k == 4 and P.g6 or P.g4)
      if y >= WATERLINE - 12 then c = (k == 0) and P.w5 or P.w3 end    -- under the water's surface
      set(x, y, c)
    end
    if i % 8 == 0 then set(x, yt + 1, P.g6) end                         -- its stones' joints
  end

  -- F: the light pools on the paving, slab by slab: each slab takes the step of the nearest light by its middle's
  -- distance (inner, middle, outer: pool1, pool2, pool3 with the step above on its lit top row), so a pool has the
  -- slabs' own hard edges, as in the concept. The front course is lit a little less far than the back course
  -- (the lamps stand on the back course). Joints in a lit slab go dark amber; the coping's lit arris takes the step
  -- of the slab above it.
  local pools = self:pools()
  local STEP = { { P.poolHi, P.pool1 }, { P.pool1, P.pool2 }, { P.pool2, P.pool3 } }
  local function stepAt(cx, k)
    local best
    for _, pl in ipairs(pools) do
      local d = math.abs(cx - pl.x) / (pl.r * k)
      local st = (d < 0.4 and 1) or (d < 0.7 and 2) or (d < 1 and 3) or nil
      if st and (not best or st < best) then best = st end
    end
    return best
  end
  for x = 0, W - 1 do
    if top[x] then
      local sb = stepAt(math.floor(x / 24) * 24 + 12, 1)
      local sf = stepAt(math.floor((x + 12) / 32) * 32 + 4, 0.85)
      if sb then
        for y = PAVE0 + 1, FRONT0 - 2 do
          local joint = x % 24 == 0
          set(x, y, joint and (sb < 3 and P.pool3 or P.g6) or STEP[sb][(y == PAVE0 + 1) and 1 or 2])
        end
      end
      if sf then
        for y = FRONT0, CAP0 - 2 do
          local joint = (x + 12) % 32 == 0
          set(x, y, joint and (sf < 3 and P.pool3 or P.g6) or STEP[sf][(y == FRONT0) and 1 or 2])
        end
        if sf < 3 then set(x, CAP0 - 1, P.pool3); set(x, CAP0, sf == 1 and P.pool2 or P.pool3) end
      end
    end
  end
  -- bollards on the back course (6 x 8), every 192 px where nothing stands within 28 px
  local B = { { 0, 1, 4, P.iron1 }, { 0, 0, 6, nil } }
  local function free(x)
    for _, p in ipairs(self.def.props) do if p.x1 > x - 28 and p.x0 < x + 34 and p.layer ~= "front" then return false end end
    for _, l in ipairs(self.def.lamps) do if math.abs(l.x - x) < 30 then return false end end
    for _, l in ipairs(self.def.lights or {}) do if math.abs(l.x - x) < 30 then return false end end
    for i = -8, 14 do if not top[x + i] then return false end end
    return true
  end
  for bx = 136, W - 40, 192 do
    if free(bx) then
      for y = 0, 7 do
        for i = 0, 5 do
          local c = P.iron2
          if y == 0 then c = (i >= 1 and i <= 4) and P.iron1 or nil
          elseif i == 0 then c = P.iron1 elseif i == 5 then c = P.iron3 end
          if y == 2 then c = P.iron3 end
          if y == 7 then c = P.iron3 end
          set(bx + i, 168 + y, c)
        end
      end
      for i = -1, 6 do set(bx + i, 176, P.g4) end                      -- its contact on the paving
    end
  end
  self.groundImg = data
  -- the chunks (512 px, as scene.lua's ground)
  local chunks = {}
  for cx = 0, W - 1, 512 do
    local cw = math.min(512, W - cx)
    local d = love.image.newImageData(cw, H)
    d:paste(data, 0, 0, cx, 0, cw, H)
    local im = lg.newImage(d); im:setFilter("nearest", "nearest")
    chunks[#chunks + 1] = { im = im, x = cx, w = cw }
  end
  local art = self
  local g = { chunks = chunks }
  function g:draw(cam, camY)
    lg.setColor(1, 1, 1, 1)
    for _, c in ipairs(self.chunks) do
      if c.x - cam < 320 and c.x + c.w - cam > 0 then lg.draw(c.im, c.x - cam, 0) end
    end
    art:drawStanding(cam)                                               -- what stands on it, behind Pepper
    lg.setColor(1, 1, 1, 1)
  end
  function g:release() for _, c in ipairs(self.chunks) do c.im:release() end; self.chunks = {} end
  if os.getenv("NIGHT_JOINS") then
    local ok, n, bad = Jn.check(self:joinKinds(), W)
    print(("NIGHT JOINS %s %d changes%s"):format(ok and n > 0 and "PASS" or "FAIL", n, ok and "" or ": " .. table.concat(bad, "; "))); io.stdout:flush()
  end
  return g
end

-- F: the night light model (night.lua Nt.drawArtLight draws the halos, Pepper's glow and rim; the pools are painted
-- with the ground; the reflections are drawn with it, over the water)
M.nightLight = true
-- the lights that fall on the paving: { x, r } (lamps, the lanterns on the quay, the house's window, door, lantern)
function M:pools()
  local top = self:groundMap()
  local out = {}
  for _, l in ipairs(self.def.lamps) do out[#out + 1] = { x = l.x, r = 44 } end
  for _, l in ipairs(self.def.lights or {}) do
    if l.kind == "lantern" and top[math.floor(l.x)] then
      local onPost = false
      for _, p in ipairs(self.def.props) do if self.K[p] == "post" and l.x >= p.x0 and l.x < p.x1 then onPost = true end end
      if not onPost then out[#out + 1] = { x = l.x, r = 34 } end
    elseif l.kind == "window" then out[#out + 1] = { x = l.x, r = (l.x == 4344) and 30 or 26 }
    elseif l.kind == "porch" then out[#out + 1] = { x = l.x, r = 40 } end
  end
  return out
end
-- a light's halo round its glass as drawn: x, y, radius (nil: none, the house's window and door are their art)
function M:halo(l)
  local x, y = self:lightPos(l)
  if x then return x, y, 8 end
  if l.kind == "lamp" then return l.x, 84, 12 end
  if l.kind == "lantern" then return l.x, l.y, 8 end
  if l.kind == "window" and l.x == 4344 then return l.x, l.y - 2, 9 end
end
-- the reflections in the water of the gaps: under each light (as drawn) a broken column of amber dashes that
-- widens and darkens with depth and shimmers sideways; under the moon's screen x a pale one. Only on water columns.
local function column(self, sx, cols, t, seed)
  local kind = self.kind or {}
  local cam = math.floor(self.stage.cam + 0.5)
  for i = 0, 9 do
    local y = WATERLINE + 2 + i * 3
    if y > 238 then break end
    local w = 1 + math.floor(i / 2)
    local off = math.floor(math.sin(t * 2.5 + i * 1.7 + seed) * 1.5 + 0.5)
    local c = cols[math.min(#cols, 1 + math.floor(i / 3))]
    for xx = sx - math.floor(w / 2) + off, sx - math.floor(w / 2) + off + w - 1 do
      if kind[xx + cam] == "water" then box(c, xx, y, 1, 1) end
    end
  end
end
function M:drawReflections(cam, t)
  local seen = {}
  for _, l in ipairs(self.stage.night and self.stage.night.lights or {}) do
    local x = self:lightPos(l) or l.x
    if l.kind ~= "window" and l.kind ~= "porch" and x - cam > -8 and x - cam < 328 then
      column(self, math.floor(x - cam), { P.refl1, P.refl2, P.refl3 }, t, x)
    end
  end
  column(self, M.MOON_X + 4, { P.moon, P.moonD, P.w6 }, t, 0)
end
-- the moon's reflection on the bay (screen space, under the moon)
function M:drawBayMoon(t)
  for i = 0, 6 do
    local y = 150 + i * 3
    local w = 2 + i
    local off = math.floor(math.sin(t * 2 + i * 1.3) * 1.5 + 0.5)
    box(i < 3 and P.moonD or P.w6, M.MOON_X + 5 - math.floor(w / 2) + off, y, w, 1)
  end
end

-- the level's colour script (look.lua format): a still harbour night. The art is painted in its final colours, so
-- each layer's grade is light: warm lights lean a touch more golden, darks a touch more violet, no haze (the
-- distance is in the palette: the far layers are lighter steps of the night's blue)
local function L(warm, cool, sat, haze, k) return { warm = warm, cool = cool, sat = sat, k = k or 0, clean = 0,
  haze = { tonumber(haze:sub(1, 2), 16) / 255, tonumber(haze:sub(3, 4), 16) / 255, tonumber(haze:sub(5, 6), 16) / 255 } } end
M.look = {
  layers = { clouds = L(0, 0, 1, "1d2c66"), city = L(0, 0, 1, "1d2c66"), shore = L(0, 0, 1, "1d2c66"),
             mid = L(0, 0, 1, "1d2c66"), water = L(0.3, 0.3, 1.0, "000000"), back = L(0.35, 0.3, 1.05, "000000"),
             ground = L(0.35, 0.3, 1.05, "000000"), play = L(0.35, 0.25, 1.05, "000000"),
             front = L(0.0, 0.6, 1.0, "0c0e24", 0.2) },
  bands = { { 0, "061340" }, { 112, "213a72" } },
  fg = { dark = { 0.05, 0.06, 0.13 }, mid = { 0.08, 0.09, 0.19 }, rim = { 0.3, 0.36, 0.5 }, warm = { 0.5, 0.36, 0.25 }, warmK = 0.05 },
  kinds = {},
  fade = {},
}

return M
