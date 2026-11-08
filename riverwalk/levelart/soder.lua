-- Level art for Söder Hill (levelart.lua; 8 Nov 2026, owner: "finish levels 4-6"). Built by rule, 0 credits.
-- Parts are added as they pass QA; whatever this module does not draw, stage.lua draws as greybox.
-- The pixels are built by tools/build_soder_art.py into riverwalk/levelart/soder/ (props/*.png, the ground and back
-- tiles, the backdrop) from one palette (soder/palette.lua, written from the tool's PAL table: swap colours there).
--   A  labels off: every prop is drawn without its printed name (the names are debug only)
--   B  the props and their holders, by rule: every sign hangs from a bracket bar fixed to the wall by two plates and
--      two chains; the awning hangs from its iron arm and wall plate; the balconies stand on stone corbels, their
--      railings behind Pepper; tables stand on their legs, the parasols on poles down to the tables; the terraces on
--      corner posts; the arch on two piers; every piece on the street casts a contact shadow; the checkpoint lamps
--      are the approved lamp post. Obstacles keep a 1 px dark outline on their hit box's edge; holders have none.
local Sc = require("scene")
local Look = require("look")
local lg = love.graphics
local DIR = "levelart/soder/"
local M = {}
M.__index = M
function M.new(stage) return setmetatable({ stage = stage, def = stage.def, world = stage.world }, M) end

local IMG = {}
local function img(n)
  if IMG[n] == nil then
    local f = DIR .. n .. ".png"
    IMG[n] = love.filesystem.getInfo(f) and lg.newImage(f) or false
    if IMG[n] then IMG[n]:setFilter("nearest", "nearest") end
  end
  return IMG[n] or nil
end
local function at(im, x, y) if im then lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x), math.floor(y)) end end

-- a prop without art yet: its greybox box, no label (a copy whose name is blank)
local function plain(pr, cam, colour)
  Sc.drawProp(setmetatable({ name = "" }, { __index = pr }), cam, colour)
end

-- the street's top (Pepper's feet line) under x: terrain only
local function streetAt(w, x)
  local sy = w:slopeFloor(x); if sy then return sy end
  local best
  for _, r in ipairs(w.rects) do if r.terrain and x >= r.x0 and x < r.x1 and (not best or r.y0 < best) then best = r.y0 end end
  return best
end
M.streetAt = streetAt

-- the hanging signs' pictures, left to right (no letters): a cafe, a bakery, a fish shop by the quay
local SIGNS = { "sign_cup", "sign_loaf", "sign_fish" }
local function signIndex(def, pr)
  local i = 0
  for _, q in ipairs(def.props) do if q.name == "SIGN" then i = i + 1; if q == pr then return i end end end
  return 1
end

-- the balcony's quads: the railing rows (behind Pepper) and the slab with its corbels (her line)
local BQ = {}
local function balconyQ(im, rail)
  local k = tostring(im) .. (rail and "r" or "s")
  if not BQ[k] then
    local iw, ih = im:getDimensions()
    BQ[k] = rail and lg.newQuad(0, 0, iw, 46, iw, ih) or lg.newQuad(0, 46, iw, ih - 46, iw, ih)
  end
  return BQ[k]
end

local function crates(T, pr, x)                                     -- (Downtown's apple crates, 16 px each)
  local w, k = pr.x1 - pr.x0, math.max(1, math.floor((pr.y1 - pr.y0) / 16 + 0.5))
  local cr = T.crates[w]
  local FILL = { false, "pears", false, "bread", false, false, "cloth" }
  for i = 1, k do
    local f = FILL[(math.floor(pr.x0 / 16) * 3 + i * 5) % #FILL + 1]
    local v = f and T.crateFills and T.crateFills[f] and T.crateFills[f][w .. "_" .. f]
    at(v or cr or T.crate, x - 1, pr.y1 - 16 * i - 5)
  end
end

function M:drawProp(pr, cam, colour, kicked)
  local n, x, w, h = pr.name, pr.x0 - cam, pr.x1 - pr.x0, pr.y1 - pr.y0
  if x > 340 or x + w < -60 then return true end
  if pr.kind == "decor" then return true end                        -- brackets, the arm, poles: drawn by what they hold;
                                                                    -- STAIRS: in the back row
  local function shadow(depth) Sc.shadow(x + w / 2, pr.y1 - 1, w + 4, depth) end
  if n == "SIGN" then at(img("props/" .. SIGNS[(signIndex(self.def, pr) - 1) % #SIGNS + 1]), x - 9, pr.y0 - 13)
  elseif n == "AWNING" then at(img("props/awning"), x - 1, pr.y0 - 28)
  elseif n == "BALCONY" then
    local im = img("props/balcony" .. w)
    if im then lg.setColor(1, 1, 1, 1); lg.draw(im, balconyQ(im, false), math.floor(x) - 1, pr.y0 - 1) else plain(pr, cam, colour) end
  elseif n == "TERRACE" then shadow(); at(img("props/terrace"), x, pr.y0)
  elseif n == "CART" then shadow(); at(img("props/cart"), x, pr.y0)
  elseif n == "BIKES" then shadow(); at(img("props/planter"), x, pr.y0)
  elseif n == "RAILING" then shadow(); at(img("props/railing"), x, pr.y0)
  elseif n == "ARCH" then at(img("props/arch"), x - 8, pr.y0)
  elseif n == "TABLE" then
    local T = Sc.townArt("town")
    local g = streetAt(self.world, pr.x0 + w / 2) or pr.y1
    Sc.shadow(x + w / 2, g - 1, w + 4, 5); at(T.table, x - 1, pr.y0)
  elseif n == "PARASOL" then
    local T = Sc.townArt("town")
    local tb
    for _, q in ipairs(self.def.props) do if q.name == "TABLE" and q.x0 >= pr.x0 and q.x1 <= pr.x1 then tb = q end end
    local px = math.floor(x + w / 2) - 1
    local foot = tb and tb.y0 or (streetAt(self.world, pr.x0 + w / 2) or 240)
    local P = M.pal()
    lg.setColor(P.ink); lg.rectangle("fill", px - 1, pr.y1, 4, foot - pr.y1)     -- the pole down to the table
    lg.setColor(P.iron); lg.rectangle("fill", px, pr.y1, 2, foot - pr.y1)
    lg.setColor(P.iron_lit); lg.rectangle("fill", px, pr.y1, 1, foot - pr.y1)
    local im = T.parasols[w] or T.parasol
    at(im, x - (T.parasols[w] and 1 or 0), pr.y0 - 1)
  elseif n == "CRATE" or n == "CRATES" or (n == "" and w == 32) then shadow(); crates(Sc.townArt("town"), pr, x)
  elseif n == "" and w == 12 and h == 14 then shadow(); at(img("props/bollard"), x, pr.y0)
  else plain(pr, cam, colour) end
  lg.setColor(1, 1, 1, 1)
  return true
end

-- C + D: the ground, painted by tools/build_soder_art.py into 512 x 240 tiles (ground_NN.png): the setts, the
-- kerb, the retaining wall, the stair flights as 8 px stone steps between granite landings, the open cellar hatches
-- with their lids, the harbour quay. The joins it stamps are marked for the joins kit (joins.lua): street>landing,
-- landing>stair, stair>landing, landing>street (or quay), street>hatch, hatch>street.
M.drawsHatches = true                                               -- (chase.lua leaves the hatches to this module)
local TILE = 512
local Tiles = {}
Tiles.__index = Tiles
function Tiles:draw(cam, camY)
  lg.setColor(1, 1, 1, 1)
  for i, im in pairs(self.ims) do
    local x = i * TILE - cam
    if x < 320 and x + TILE > 0 then lg.draw(im, x, 0) end
  end
end
function Tiles:release() for _, im in pairs(self.ims) do im:release() end; self.ims = {} end
local function tiles(name, w)
  local t = setmetatable({ ims = {} }, Tiles)
  for i = 0, math.ceil(w / TILE) - 1 do
    local im = img(("%s_%02d"):format(name, i))
    if im then t.ims[i] = im end
  end
  return t
end

function M:paintGround(w)
  Sc.quayEdge = nil
  local Jn = require("joins")
  Jn.reset()
  local kind = {}
  local hatchAt = {}
  for _, h in ipairs(self.def.hatches or {}) do for x = h[1], h[2] - 1 do hatchAt[x] = true end end
  for x = 0, w.width - 1 do kind[x] = hatchAt[x] and "hatch" or (w:slopeAt(x) and "stair" or "street") end
  for x = 1, w.width - 1 do
    if kind[x] ~= kind[x - 1] then Jn.mark(x, kind[x - 1] .. ">" .. kind[x]) end
  end
  self.front = tiles("front", w.width)
  return tiles("ground", w.width)
end

-- in front of Pepper: the kerb and the wall in front of each open hatch, so she drops into the cellar behind them
function M:drawFront(cam, camY, t)
  if not self.front then return end
  if Look.on and self.look then Look.use("ground") end
  self.front:draw(cam, camY)
  lg.setColor(1, 1, 1, 1)
end

-- E: the backdrop (screen space; replaces the greybox far town). Back to front: the painted sky (build_sky.py's
-- rules in Söder's golden evening, 0.05 of the camera plus a drift), the far city across the water (its skyline
-- moved at most 128 px over the level), the harbour's water under it, and a row of roofs down the hill (0.5). The
-- whole backdrop sinks with the street (DY px over the level): the street drops 96 px from the top to the quay, so
-- the roofs and the far city stay just over the alleys' walls, and at the bottom the view opens on the harbour.
-- Each layer has its own ground: the city stands on the water, the water runs down to the screen's bottom, the
-- roofs' walls run down past the alleys' walls (they end before the harbour opens, at mid x 2320, in a gable).
M.Y_MID, M.Y_CITY, M.DY = 32, 46, 96
local skyQ = {}
function M:drawFar(cam, camY, t)
  local W = self.world.width
  local dy = math.floor(M.DY * math.min(1, cam / math.max(1, W - 320)) + 0.5)
  local sky = img("sky")
  if sky then
    local sw, sh = sky:getDimensions()
    local o = math.floor(cam * 0.05 + t * 2) % sw
    skyQ[1] = skyQ[1] or lg.newQuad(0, 0, 1, 1, sw, sh); skyQ[2] = skyQ[2] or lg.newQuad(0, 0, 1, 1, sw, sh)
    local n = math.min(320, sw - o)
    skyQ[1]:setViewport(o, 0, n, sh, sw, sh); lg.setColor(1, 1, 1, 1); lg.draw(sky, skyQ[1], 0, 0)
    if n < 320 then skyQ[2]:setViewport(0, 0, 320 - n, sh, sw, sh); lg.draw(sky, skyQ[2], n, 0) end
  end
  local lk = Look.on and self.look
  local cy = M.Y_CITY + dy                                            -- the far shore's line
  local city = img("skyline")
  if city then
    if lk then Look.use("city") end
    local sx = -math.floor(math.min(128, cam * 128 / math.max(1, W - 320)))
    lg.setColor(1, 1, 1, 1)
    lg.draw(city, sx, cy - city:getHeight()); lg.draw(city, sx + city:getWidth(), cy - city:getHeight())
  end
  local far = img("far")
  if far then
    if lk then Look.use("shore") end
    local fw, fh = far:getDimensions()
    local ox = math.floor(cam * 0.25) % fw
    lg.setColor(1, 1, 1, 1)
    for x = -ox, 320, fw do lg.draw(far, x, cy) end
    if cy + fh < 240 then lg.setColor(M.pal().water_1); lg.rectangle("fill", 0, cy + fh, 320, 240 - cy - fh) end
  end
  local mid = img("mid")
  if mid then
    if lk then Look.use("mid") end
    lg.setColor(1, 1, 1, 1); lg.draw(mid, -math.floor(cam * 0.5), M.Y_MID + dy - 20)
  end
  if lk then Look.off() end
  lg.setColor(1, 1, 1, 1)
end

-- the colour script (look.lua format): golden early evening, a low warm sun from the upper left. The art comes in
-- its final colours, so the look is mild: a little warmth on the lights, a little violet in the darks, and each far
-- layer one clean step towards the evening air (its haze a tint of the sky's horizon).
local function hexc(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end
local function L(warm, cool, sat, haze, k, clean) return { warm = warm, cool = cool, sat = sat, haze = hexc(haze), k = k, clean = clean or 0 } end
M.look = {
  layers = { clouds = L(0, 0, 1.0, "fadca0", 0), city = L(0, 0, 1.0, "000000", 0),
             shore = L(0.2, 0.6, 1.0, "f6d2a2", 0.10, 0.4), mid = L(0.3, 0.8, 1.0, "f4cc98", 0.22, 0.45),
             water = L(0.2, 0.6, 1.0, "f6d2a2", 0.05), back = L(0.25, 0.7, 1.0, "f4cc98", 0.04),
             ground = L(0.2, 0.6, 1.0, "000000", 0), play = L(0.3, 0.7, 1.05, "000000", 0),
             front = L(0.0, 1.8, 1.10, "241a24", 0.40) },
  bands = { { 0, "e8b274" }, { 30, "efbc76" }, { 62, "f4c67c" }, { 92, "f8d28a" }, { 118, "fadca0" } },
  fg = { dark = hexc("241a24"), mid = hexc("33262e"), rim = hexc("6a4e4a"), warm = hexc("c08850"), warmK = 0.2 },
  kinds = {},
  fade = { back = 0.12 },
}

local PAL
function M.pal() PAL = PAL or require("levelart.soder.palette"); return PAL end

-- behind Pepper's line: the house fronts (E), then the balconies' railings (so she, the bones and the ball are
-- always in front of them)
function M:drawBack(cam, camY, t)
  self.back = self.back or tiles("back", self.world.width)
  self.back:draw(cam, camY)
  for _, pr in ipairs(self.def.props) do
    if pr.name == "BALCONY" and pr.x1 - cam > -10 and pr.x0 - cam < 330 then
      local im = img("props/balcony" .. (pr.x1 - pr.x0))
      if im then lg.setColor(1, 1, 1, 1); lg.draw(im, balconyQ(im, true), math.floor(pr.x0 - cam) - 1, pr.y0 - 1 - 46) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- the checkpoint lamps: the approved lamp post (River Walk's), its foot on the street's back half, a passed one lit
function M:drawLamp(l, cam, t)
  local A = Sc.art()
  local im = l.lit and A.lamp_lit or A.lamp_post
  local x = l.x - cam
  local lx, top = math.floor(x - im:getWidth() / 2), l.y - Sc.EDGE - im:getHeight()
  Sc.shadow(x, l.y - Sc.EDGE - 1, 14)
  if Look.on and self.look then Look.use("back") end
  lg.setColor(1, 1, 1, 1); lg.draw(im, lx, top)
  if l.lit then Sc.lampLight(lx + im:getWidth() / 2, top + 17, t - (l.litAt or -9), t) end
  return true
end

return M
