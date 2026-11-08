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

function M:drawProp(pr, cam, colour, kicked)
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
function M:drawLight(l, cam)
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

-- behind Pepper's line, after the back props: the nets
function M:drawBack(cam, camY, t)
  self:drawNets(cam)
end
-- after the play layer: the old jetty's piles (over the water the ground paints; under her line, so never over her
-- unless she is in the water)
function M:drawFront(cam, camY, t)
  self:drawPiles(cam)
end

return M
