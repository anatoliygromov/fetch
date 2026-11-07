-- Scenery. Art in art/scene: far shore and bridge, bench, bin, pot, lamp post (riverwalk_scenery_v1), water (SpriteCook),
-- skyline, pavement, building, tree (trial). Everything else is still wireframe: plain boxes in a misty grey-blue per layer, lighter the
-- further back. Layers 2 to 5 scroll slower (parallax).
local F = require("bigfont")
local Look = require("look")
local Sc = {}
local Jn = require("joins")                                          -- (day/07nov-ground) the ground's transitions
local lg = love.graphics
local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end

-- one shade per layer, far (light, misty) to near (dark)
Sc.C = {
  sky1 = hex("dde5ec"), sky2 = hex("c8d3de"),      -- 1 sky
  cloud = hex("eaeff3"),                           -- 2 clouds
  city = hex("b6c3cf"),                            -- 3 far city
  back = hex("788a9d"),                            -- 6 quay back (behind Pepper)
  ground = hex("5f6f81"), groundEdge = hex("435060"), -- 7 play layer: terrain
  prop = hex("6c7d90"), propEdge = hex("2f3a46"),  --   play layer: props Pepper can use (outlined)
  river = hex("7f91a4"),                           --   play layer: the river Pepper can fall into
  front = hex("3c4857"),                           -- 8 foreground frame
  label = hex("e4eaf0"), bone = hex("efe8d8"), boneEdge = hex("8a7f68"), gold = hex("f2c94c"),
}
-- greybox park (City Park): two more misty layers between the far city and the play layer, the leaf piles,
-- the cat, the pond
Sc.C.trees = hex("a5b3c1")                         -- 4 far trees
Sc.C.bushes = hex("90a0b1")                        -- 5 near trees and bushes
Sc.C.leaves = hex("8494a6")                        --   play layer: leaf piles (decoration over the bones)
Sc.C.cat, Sc.C.catEdge = hex("3f4654"), hex("1d222b")
Sc.C.pond, Sc.C.pondTop = hex("8a9cb0"), hex("b9c6d3")
local C = Sc.C
Sc.speeds = { clouds = 0.05, city = 0.08, shore = 0.3, water = 0.5 }

-- decoration is faded part of the way towards the haze when the level loads, so it sits back and the obstacle course
-- stands out. Decision 3 (owner, 23 Oct): the haze is the level's own, per layer (look.lua: the colour script of the
-- level being played, Look.key), no longer one cool grey (200, 210, 222) for every level; the amounts per layer are
-- the script's `fade` (River Walk's decoration 28 %, as before). The files are untouched: a copy is faded at load,
-- and every faded image is cached per colour script.
function Sc.haze(layer) local L = Look.scripts[Look.key].layers; return (L[layer or "back"] or L.back).haze end
function Sc.fadeK(layer) return (Look.scripts[Look.key].fade or {})[layer or "back"] or 0 end
-- a colour k of the way to the layer's haze (k: the layer's amount when nil)
function Sc.fadeC(c, k, layer)
  local h = Sc.haze(layer); k = k or Sc.fadeK(layer)
  return { c[1] + (h[1] - c[1]) * k, c[2] + (h[2] - c[2]) * k, c[3] + (h[3] - c[3]) * k }
end
-- ImageData d, every pixel k of the way to the layer's haze (in place; returns d)
function Sc.fadeData(d, k, layer)
  local h = Sc.haze(layer); k = k or Sc.fadeK(layer)
  if k > 0 then d:mapPixel(function(_, _, r, g, b, a) return r + (h[1] - r) * k, g + (h[2] - g) * k, b + (h[3] - b) * k, a end) end
  return d
end

-- the characters' 1 px dark outline around an image's silhouette, outside the art (the result is 1 px bigger on
-- every side). Used on everything Pepper can use: bench, bin, railing.
function Sc.outline(src)
  local w, h = src:getDimensions()
  local d = love.image.newImageData(w + 2, h + 2)
  d:paste(src, 1, 1, 0, 0, w, h)
  local function solid(x, y) if x < 0 or y < 0 or x >= w or y >= h then return false end local _, _, _, a = src:getPixel(x, y); return a > 0 end
  for y = -1, h do
    for x = -1, w do
      if not solid(x, y) and (solid(x - 1, y) or solid(x + 1, y) or solid(x, y - 1) or solid(x, y + 1)) then
        d:setPixel(x + 1, y + 1, 1 / 255, 1 / 255, 2 / 255, 1)
      end
    end
  end
  return d
end

-- railings, assembled into one image to the width. Two kinds, which must never look alike:
--   "decor": the open tube railing along the water's edge (tools/make_bg_railing.py, in the lamp posts' colours).
--            Faded like all decoration, no outline; Pepper cannot use it.
--   "fence": the iron fence with balusters (tools/make_railing.py), a short section on Pepper's line that she
--            climbs. Crisp and outlined like every obstacle;
--            its balusters are longer (row 15, a plain baluster row, repeated) so its top is high enough
--            to be safe from the bikes. Outlined as a whole, so the outline has no seams.
local railCache = {}
function Sc.railing(w, kind, h)
  local key = kind .. w .. "x" .. (h or 0) .. Look.key            -- (decor is faded to the level's haze)
  if railCache[key] then return railCache[key] end
  local function piece(n) return love.image.newImageData("art/scene/" .. n .. ".png") end
  local d
  if kind == "fence" then                                         -- the iron fence: left post + span, repeated, then the end post
    local seg, en = piece("rail_seg"), piece("rail_end")
    local sw, ew, rh = seg:getWidth(), en:getWidth(), seg:getHeight()
    local n = math.max(1, math.floor((w - ew) / sw))
    d = love.image.newImageData(n * sw + ew, rh)
    for i = 0, n - 1 do d:paste(seg, i * sw, 0, 0, 0, sw, rh) end
    d:paste(en, n * sw, 0, 0, 0, ew, rh)
  else                                                             -- the open tube railing: left post, spans, end
    local l, u, en = piece("rail_bg_left"), piece("rail_bg_unit"), piece("rail_bg_end")
    local lw, uw, ew, rh = l:getWidth(), u:getWidth(), en:getWidth(), l:getHeight()
    -- (night/25oct-fixes) the railing reaches both ends of its prop (whole bays alone stopped up to 83 px short of
    -- the house it meets). eo: the end piece as drawn (its empty right columns hang past the prop's end). What whole
    -- bays leave over (r): under 12 px, the last bay is drawn r px longer (the unit's left columns: tube only); from
    -- 12 px, the last whole bay and r share two even shorter bays, each with its own post (the unit's right columns,
    -- at least 48 px, so no two posts ever stand close). Whole-pixel crops of the pieces; nothing scaled or redrawn.
    local eo = ew
    local function empty(x) for y = 0, rh - 1 do if select(4, en:getPixel(x, y)) > 0 then return false end end return true end
    while eo > 1 and empty(eo - 1) do eo = eo - 1 end
    local n = math.max(0, math.floor((w - lw - eo) / uw))
    local r = math.max(0, w - lw - n * uw - eo)
    d = love.image.newImageData(lw + n * uw + r + ew, rh)
    local tail = {}                                                -- the bays after the whole ones: { width, from the right }
    if r >= 12 and n >= 1 then n = n - 1; local a = math.floor((uw + r) / 2); tail = { { a, true }, { uw + r - a, true } }
    elseif r >= 48 then tail = { { r, true } }                    -- (no whole bay to share with: a short one alone)
    elseif r > 0 then tail = { { r, false } } end
    d:paste(l, 0, 0, 0, 0, lw, rh)
    for i = 0, n - 1 do d:paste(u, lw + i * uw, 0, 0, 0, uw, rh) end
    local x = lw + n * uw
    for _, b in ipairs(tail) do d:paste(u, x, 0, b[2] and uw - b[1] or 0, 0, b[1], rh); x = x + b[1] end
    d:paste(en, x, 0, 0, 0, ew, rh)
  end
  local rh = d:getHeight()
  if kind == "fence" then
    local extra = math.max(0, h - rh)                             -- taller: repeat baluster row 15
    local t = love.image.newImageData(d:getWidth(), rh + extra)
    t:paste(d, 0, 0, 0, 0, d:getWidth(), 16)
    for k = 0, extra - 1 do t:paste(d, 0, 16 + k, 0, 15, d:getWidth(), 1) end
    t:paste(d, 0, 16 + extra, 0, 16, d:getWidth(), rh - 16)
    d = Sc.outline(t)
  else
    Sc.fadeData(d)
  end
  local im = lg.newImage(d); im:setFilter("nearest", "nearest")
  railCache[key] = im
  return im
end

-- art: loaded once. The images are used exactly as delivered; the two made here only rearrange their pixels
-- or swap colours, so nothing is redrawn.
local ARTS = {}                                                    -- one set per colour script (Look.key): its fades
local function newImg(d) local i = lg.newImage(d); i:setFilter("nearest", "nearest"); return i end
function Sc.art()
  local A = ARTS[Look.key]
  if A then return A end
  A = {}; ARTS[Look.key] = A
  for _, n in ipairs({ "water", "skyline", "pavement", "road", "manhole", "drain", "quaywall" }) do A[n] = newImg("art/scene/" .. n .. ".png") end
  A.waterQ = {}                                                   -- one quad per row: each row of the river moves on its own
  for y = 0, A.water:getHeight() - 1 do A.waterQ[y] = lg.newQuad(0, y, A.water:getWidth(), 1, A.water:getDimensions()) end
  -- decoration (pot, lamp posts, the houses and trees) is faded the back amount towards the level's back haze, so it
  -- sits back and the obstacle course stands out. The files are untouched; this is done to a copy when the game loads.
  -- (art/rw-sample-screen) rw_home and rw_lime: the true-scale house and street lime of the sample screen
  -- (night/25oct-rw-street) rw_gable and rw_cafe: the true-scale gable house and cafe of screen 12
  -- (art/rw-props-06nov) rw_birch: the true-scale street birch (screens 2 and 10), replaces tree_far
  for _, n in ipairs({ "pot", "lamp_post", "building", "tree", "tree_near", "tree_far", "cafe", "gable", "rw_home",
      "rw_lime", "rw_gable", "rw_gable_bay", "rw_cafe", "rw_birch" }) do
    A[n] = newImg(Sc.fadeData(love.image.newImageData("art/scene/" .. n .. ".png")))
  end
  -- things Pepper can use (stand on, jump onto) get the characters' 1 px dark outline, so they read as part of the
  -- obstacle course; decoration and background have none. The outline goes outside the art (image grows 1 px
  -- on every side), the art's own pixels are untouched.
  A.outlined = {}
  -- round 2 obstacles and buildings (tools/make_props.py): mid-tone SpriteCook art that already has its own 1 px
  -- dark outline, so none is added here
  for _, n in ipairs({ "bench", "bin", "flowerbox", "gritbox", "flowerbox_front", "gritbox_front", "planter_sq", "ferry",
      "park_log" }) do                                            -- (r6/levels: River Walk's fallen branch, the park's log)
    A[n] = newImg("art/scene/" .. n .. ".png")
  end
  -- night branch (tools/make_night_art.py): the bridge abutment and the pontoon (things Pepper uses: crisp, with
  -- their own outline), the bones, and the foreground mooring pile (dark, near the camera, not faded)
  for _, n in ipairs({ "pier", "pontoon", "bone", "bone_gold", "pile" }) do A[n] = newImg("art/scene/" .. n .. ".png") end
  A.clouds = {}                                                   -- sky clouds, widest first
  for i = 1, 99 do
    if not love.filesystem.getInfo("art/scene/cloud" .. i .. ".png") then break end
    A.clouds[i] = newImg("art/scene/cloud" .. i .. ".png")
  end
  -- far shore: the 320 px strip ends inside the bridge, but the shore layer (scrolled at 0.3) must cover
  -- 320 + 0.3 * (3200 - 320) = 1184 px. The strip is extended with its own columns (1196 px in all): one arch
  -- and pier (columns 293-307) repeated 4 times, so the bridge has 8 arches (column 308 equals column 293,
  -- so the joins are invisible), then the strip's last arch (308-316), then the bridge's left end and the
  -- trees (columns 0-278) mirrored, which closes the bridge on the far side, then the trees again
  -- (0-271 forwards, then backwards) to the end. (The bridge used to repeat 40 arches.)
  local src = love.image.newImageData("art/scene/far_shore_bridge.png")
  local h = src:getHeight()
  local cols = {}
  for x = 0, 307 do cols[#cols + 1] = x end
  for _ = 1, 4 do for x = 293, 307 do cols[#cols + 1] = x end end
  for x = 308, 316 do cols[#cols + 1] = x end
  for x = 278, 0, -1 do cols[#cols + 1] = x end
  for x = 0, 271 do cols[#cols + 1] = x end
  -- (r5/bugs: River Walk is 3840 px now, so the layer must cover 320 + 0.3 * 3520 = 1376 px; it was cut at 1196 and
  -- the trees ended in a hard edge over the last screens. The trees now go back and forth to 1600 px.)
  local x, dx = 271, -1
  while #cols < 1600 do
    cols[#cols + 1] = x; x = x + dx
    if x < 0 then x, dx = 0, 1 elseif x > 271 then x, dx = 271, -1 end
  end
  local d = love.image.newImageData(#cols, h)
  for i, x in ipairs(cols) do for y = 0, h - 1 do d:setPixel(i - 1, y, src:getPixel(x, y)) end end
  A.shore = newImg(d)
  -- lit lamp (a checkpoint Pepper has passed): the lantern glass (rows 12-23) glows warm.
  local lp = love.image.newImageData("art/scene/lamp_post.png")
  local hz, fk = Sc.haze("back"), Sc.fadeK("back")
  local function is(r, g, b, R, G, B) return math.abs(r * 255 - R) < 1 and math.abs(g * 255 - G) < 1 and math.abs(b * 255 - B) < 1 end
  lp:mapPixel(function(x, y, r, g, b, a)                           -- lit lamp: warm glass (exact colours), the rest faded
    if y >= 12 and y <= 23 and a > 0 then
      if is(r, g, b, 187, 211, 233) then return 250 / 255, 214 / 255, 120 / 255, a          -- the light is not faded
      elseif is(r, g, b, 88, 109, 134) then return 201 / 255, 150 / 255, 72 / 255, a end
    end
    return r + (hz[1] - r) * fk, g + (hz[2] - g) * fk, b + (hz[3] - b) * fk, a
  end)
  A.lamp_lit = newImg(lp)
  return A
end

-- deterministic boxes per layer
local function rng(seed) local s = seed return function(a, b) s = (s * 1103515245 + 12345) % 2147483648; return a + (s % 100000) / 100000 * (b - a) end end
function Sc.build(levelW)
  local L = { levelW = levelW }
  local function span(speed) return 320 + (levelW - 320) * speed + 64 end
  -- 2 clouds: SpriteCook cloud sprites (art/scene/cloud*.png) spaced along the sky, high ones bigger
  local A = Sc.art()
  local r = rng(11); L.clouds = {}
  local x, k = -40, 0
  while x < span(0.05) + 200 do
    k = k + 1
    local i = 1 + (k * 5) % #A.clouds                              -- every sprite in turn, in a mixed order
    local im = A.clouds[i]
    L.clouds[#L.clouds + 1] = { x = x, y = math.floor(r(14, 70)), img = im, w = im:getWidth() }
    x = x + im:getWidth() + math.floor(r(50, 140))
  end
  L.cloudSpan = x + 120
  return L
end

local function box(c, x, y, w, h) lg.setColor(c); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end
local function outlined(c, e, x, y, w, h)
  x, y = math.floor(x), math.floor(y)
  lg.setColor(e); lg.rectangle("fill", x, y, w, h)
  if w > 2 and h > 2 then lg.setColor(c); lg.rectangle("fill", x + 1, y + 1, w - 2, h - 2) end
end
Sc.box, Sc.outlined = box, outlined

-- tall levels (vcam.lua): while stage.lua draws the far layers, Sc.vshift = { sky, far, mid, world } holds how far
-- down each layer is moved on screen (the sky, far city, mid trees / houses scroll up and down slower than the
-- world; world = -camY for world things drawn here, the art levels' ponds). nil in a flat level: nothing moves.
local function vpush(k)
  local v = Sc.vshift
  if not v or v[k] == 0 then return false end
  lg.push(); lg.translate(0, v[k]); return true
end
local function vpop(on) if on then lg.pop() end end
local function skyGap()                                            -- the sky moved down: its top colour above it
  local v = Sc.vshift
  if v and v.sky > 0 then box(C.sky1, 0, 0, 320, v.sky) end
end

-- greybox park: the same sky and clouds, then plain boxes per layer, lighter the further back:
--   3 far city   (0.08) low blocks beyond the park
--   4 far trees  (0.25) round-ish crowns on trunks
--   5 near trees (0.5)  darker, bigger crowns and bushes
-- Deterministic (seeded), built once per level.
-- style = "town" (Downtown): layers 4 and 5 are a town instead of a park (see Sc.buildTown); the sky, clouds and
-- far city are the same.
function Sc.buildGrey(levelW, style)
  local L = Sc.build(levelW)
  local function span(speed) return 320 + (levelW - 320) * speed + 64 end
  local r = rng(23); L.city = {}
  local x = -20
  while x < span(0.08) do
    local w = math.floor(r(24, 60)); L.city[#L.city + 1] = { x = x, w = w, h = math.floor(r(18, 54)) }
    x = x + w + math.floor(r(0, 18))
  end
  if style == "town" then return Sc.buildTown(L, span) end
  r = rng(31); L.trees = {}
  x = -10
  while x < span(0.25) do
    local w = math.floor(r(30, 56)); L.trees[#L.trees + 1] = { x = x, w = w, h = math.floor(r(22, 40)), trunk = math.floor(r(8, 16)) }
    x = x + w + math.floor(r(6, 30))
  end
  r = rng(47); L.bushes = {}
  x = -10
  while x < span(0.5) do
    local w = math.floor(r(40, 80)); L.bushes[#L.bushes + 1] = { x = x, w = w, h = math.floor(r(26, 46)), trunk = math.floor(r(14, 30)) }
    x = x + w + math.floor(r(40, 110))
  end
  return L
end

-- greybox town (Downtown), layers 4 and 5:
--   4 far roofs   (0.25) pitched roofs as stepped boxes, now and then a church spire
--   5 near houses (0.5)  old town facades: stepped gables, rows of windows, a door
function Sc.buildTown(L, span)
  L.town = true
  local r = rng(31); L.roofs = {}
  local x = -10
  while x < span(0.25) do
    local w = math.floor(r(26, 52))
    L.roofs[#L.roofs + 1] = { x = x, w = w, h = math.floor(r(14, 30)), spire = r(0, 1) < 0.18 and math.floor(r(30, 52)) or nil }
    x = x + w + math.floor(r(0, 10))
  end
  r = rng(47); L.houses = {}
  x = -10
  while x < span(0.5) do
    local w = math.floor(r(34, 58))
    L.houses[#L.houses + 1] = { x = x, w = w, h = math.floor(r(44, 78)), gable = r(0, 1) < 0.5 }
    x = x + w + math.floor(r(2, 26))
  end
  return L
end

-- layers 4 and 5 of the greybox town (base: the far edge of the street)
local function drawTown(L, camx, base)
  local ox = math.floor(camx * 0.25)                               -- 4 far roofs and spires
  for _, b in ipairs(L.roofs) do
    local x = b.x - ox
    if x < 330 and x + b.w > -10 then
      local top = base - 22 - b.h
      box(C.trees, x, top, b.w, b.h + 22)
      box(C.trees, x + 4, top - 5, b.w - 8, 5); box(C.trees, x + 10, top - 9, b.w - 20, 4)      -- the roof
      if b.spire then
        local sx = x + math.floor(b.w / 2) - 5
        box(C.trees, sx, top - b.spire, 10, b.spire); box(C.trees, sx + 2, top - b.spire - 10, 6, 10)
        box(C.trees, sx + 4, top - b.spire - 22, 2, 12)
      end
    end
  end
  box(C.trees, 0, base - 6, 320, 240 - base + 6)
  local v = Sc.vshift                                              -- (tall levels: the houses are the mid layer)
  local on = v and v.mid ~= v.far
  if on then lg.push(); lg.translate(0, v.mid - v.far) end
  ox = math.floor(camx * 0.5)                                      -- 5 near houses
  for _, h in ipairs(L.houses) do
    local x = h.x - ox
    if x < 330 and x + h.w > -10 then
      local top = base + 2 - h.h
      box(C.bushes, x, top, h.w, h.h)
      if h.gable then                                              -- a stepped gable
        box(C.bushes, x + 6, top - 6, h.w - 12, 6); box(C.bushes, x + 12, top - 12, h.w - 24, 6)
      else box(C.bushes, x + 3, top - 4, h.w - 6, 4) end           -- or a plain roof edge
      for wy = top + 8, base - 22, 14 do                           -- rows of windows
        for wx = x + 6, x + h.w - 10, 11 do box(C.leaves, wx, wy, 5, 8) end
      end
      box(C.leaves, x + math.floor(h.w / 2) - 4, base - 12, 8, 14) -- the door
    end
  end
  box(C.bushes, 0, base + 2, 320, 240 - base - 2)                  -- the pavement's back edge, up to the street
  if on then lg.pop() end
end

function Sc.drawFarGrey(L, camx, t)
  skyGap(); local on = vpush("sky")
  for y = 0, 239 do                                                -- 1 sky
    local k = math.min(1, y / 170)
    lg.setColor(C.sky1[1] + (C.sky2[1] - C.sky1[1]) * k, C.sky1[2] + (C.sky2[2] - C.sky1[2]) * k, C.sky1[3] + (C.sky2[3] - C.sky1[3]) * k)
    lg.rectangle("fill", 0, y, 320, 1)
  end
  local o = camx * 0.05 - t * 3                                    -- 2 clouds drift (the same cloud sprites as River Walk)
  lg.setColor(1, 1, 1, 1)
  for _, c in ipairs(L.clouds) do
    local x = math.floor((c.x - o) % L.cloudSpan - 120)
    if x < 330 and x + c.w > -10 then lg.draw(c.img, x, c.y) end
  end
  vpop(on); on = vpush("far")
  local base = 172                                                 -- the far edge of the park lawn
  local ox = math.floor(camx * 0.08)                               -- 3 far city
  for _, b in ipairs(L.city) do
    local x = b.x - ox
    if x < 330 and x + b.w > -10 then box(C.city, x, base - 20 - b.h, b.w, b.h + 20) end
  end
  if L.town then drawTown(L, camx, base); vpop(on); return end
  ox = math.floor(camx * 0.25)                                     -- 4 far trees
  for _, tr in ipairs(L.trees) do
    local x = tr.x - ox
    if x < 330 and x + tr.w > -10 then
      local top = base - 6 - tr.trunk - tr.h
      box(C.trees, x + tr.w / 2 - 2, top + tr.h, 4, tr.trunk + 6)
      box(C.trees, x, top + 4, tr.w, tr.h - 4); box(C.trees, x + 4, top, tr.w - 8, 4)
    end
  end
  box(C.trees, 0, base - 6, 320, 240 - base + 6)                   -- the far lawn
  vpop(on); on = vpush("mid")
  ox = math.floor(camx * 0.5)                                      -- 5 near trees and bushes
  for _, tr in ipairs(L.bushes) do
    local x = tr.x - ox
    if x < 330 and x + tr.w > -10 then
      local top = base + 2 - tr.trunk - tr.h
      box(C.bushes, x + tr.w / 2 - 3, top + tr.h, 6, tr.trunk)
      box(C.bushes, x, top + 5, tr.w, tr.h - 5); box(C.bushes, x + 5, top, tr.w - 10, 5)
    end
  end
  box(C.bushes, 0, base + 2, 320, 240 - base - 2)                  -- the near lawn, up to the path
  vpop(on)
end

-- The painted ground is cut into chunks of CHUNK x CHUNK px (the last ones smaller), each its own canvas, drawn
-- only when on screen: one canvas as big as the world would take 15 to 20 MB of video memory in a tall, wide level
-- and could pass the handheld's largest texture (2048 px assumed). Each chunk is painted by the same code, moved
-- by the chunk's origin, so the pixels are exactly those of one big canvas. While a chunk is painted, clip() is the
-- scissor in world coordinates (love's scissor ignores the transform).
Sc.CHUNK = 512
local chunkX, chunkY, chunkW, chunkH = 0, 0, 0, 0
local function clip(x, y, w, h)
  if not x then lg.setScissor(); return end
  local x0, y0 = math.max(0, x - chunkX), math.max(0, y - chunkY)
  local x1, y1 = math.min(chunkW, x + w - chunkX), math.min(chunkH, y + h - chunkY)
  lg.setScissor(x0, y0, math.max(0, x1 - x0), math.max(0, y1 - y0))
end
-- the terrain runs { top, bottom } in column x, sorted and merged ("all": every slope cell over x counts, "first":
-- only the first one, as the art levels' ground has it). Worked out once per world and column (the chunks share it).
local function columnRuns(w, x, which)
  w.columnRuns = w.columnRuns or { all = {}, first = {} }
  local memo = w.columnRuns[which]
  if memo[x] then return memo[x] end
  local runs = {}
  for _, r in ipairs(w.rects) do if r.terrain and x >= r.x0 and x < r.x1 then runs[#runs + 1] = { r.y0, r.y1 } end end
  if which == "all" then
    for _, sl in ipairs(w.slopes) do
      if x >= sl.x0 and x < sl.x1 then
        local i = x - sl.x0
        runs[#runs + 1] = { sl.dir < 0 and (sl.y0 + i) or (sl.y1 - i - 1), sl.y1 }
      end
    end
  else
    local sl = w:slopeAt(x)
    if sl then local i = x - sl.x0; runs[#runs + 1] = { sl.dir < 0 and (sl.y0 + i) or (sl.y1 - i - 1), sl.y1 } end
  end
  table.sort(runs, function(a, b) return a[1] < b[1] end)
  local merged = {}
  for _, r in ipairs(runs) do
    local m = merged[#merged]
    if m and r[1] <= m[2] then m[2] = math.max(m[2], r[2]) else merged[#merged + 1] = { r[1], r[2] } end
  end
  memo[x] = merged
  return merged
end
Sc.columnRuns = columnRuns

local Ground = {}
Ground.__index = Ground
-- a chunk with no terrain or water in it (nor up to 16 px under it: the pavement art starts 12 px above a top) is
-- left out: it would stay transparent (the sky of a tall level), so it takes no memory
local function empty(w, x, y, cw, ch)
  local function hit(r) return r.x1 > x and r.x0 < x + cw and r.y1 > y and r.y0 < y + ch + 16 end
  for _, r in ipairs(w.rects) do if r.terrain and hit(r) then return false end end
  for _, r in ipairs(w.water) do if hit(r) then return false end end
  for _, r in ipairs(w.slopes) do if hit(r) then return false end end
  return true
end
-- paint(xa, xb): draws the ground in world coordinates; it may skip the columns outside xa .. xb - 1 (the chunk)
local function chunked(w, paint)
  local g = setmetatable({ chunks = {}, width = w.width, height = w.height }, Ground)
  local N = Sc.CHUNK
  for cy = 0, w.height - 1, N do
    for cx = 0, w.width - 1, N do
      local cw, ch = math.min(N, w.width - cx), math.min(N, w.height - cy)
      if not empty(w, cx, cy, cw, ch) then
      local cv = lg.newCanvas(cw, ch)
      cv:setFilter("nearest", "nearest")
      lg.push("all"); lg.setCanvas(cv); lg.clear(0, 0, 0, 0); lg.origin(); lg.translate(-cx, -cy)
      chunkX, chunkY, chunkW, chunkH = cx, cy, cw, ch
      paint(cx, cx + cw)
      lg.pop()
      g.chunks[#g.chunks + 1] = { cv = cv, x = cx, y = cy, w = cw, h = ch }
      end
    end
  end
  chunkX, chunkY, chunkW, chunkH = 0, 0, 0, 0
  return g
end
-- draw the chunks on screen (cam, camY: the camera; drawn in world y, inside the camera's y shift)
function Ground:draw(cam, camY)
  camY = camY or 0
  for _, c in ipairs(self.chunks) do
    if c.x - cam < 320 and c.x + c.w - cam > 0 and c.y - camY < 240 and c.y + c.h - camY > 0 then lg.draw(c.cv, c.x - cam, c.y) end
  end
end
function Ground:release() for _, c in ipairs(self.chunks) do c.cv:release() end; self.chunks = {} end
-- the video memory the ground takes (bytes, RGBA8) and its largest chunk side
function Ground:bytes() local n, m = 0, 0; for _, c in ipairs(self.chunks) do n = n + c.w * c.h * 4; m = math.max(m, c.w, c.h) end; return n, m end
Sc.Ground = Ground

-- the greybox ground: every terrain column flat grey with a 1 px edge on top; the pond's water as a flat box
-- with a light surface line. Painted once, in chunks (Sc.CHUNK).
function Sc.paintGroundGrey(w)
  return chunked(w, function(xa, xb)                              -- (painted once per chunk: Sc.CHUNK)
  for _, r in ipairs(w.water) do
    box(C.pond, r.x0, r.y0, r.x1 - r.x0, r.y1 - r.y0)
  end
  for _, r in ipairs(w.water) do                                   -- the surface: top row of the water only
    local top = true
    for _, q in ipairs(w.water) do if q ~= r and q.y1 == r.y0 and q.x0 < r.x1 and q.x1 > r.x0 then top = false end end
    if top then box(C.pondTop, r.x0, r.y0, r.x1 - r.x0, 1) end
  end
  for x = xa, xb - 1 do                                           -- (the chunk's columns)
    local merged = columnRuns(w, x, "all")
    for _, m in ipairs(merged) do
      lg.setColor(C.ground); lg.rectangle("fill", x, m[1], 1, m[2] - m[1])
      lg.setColor(C.groundEdge); lg.rectangle("fill", x, m[1], 1, 1)
    end
  end
  -- the sides of terrain steps (the pond banks, the slide tower) get the edge colour too
  for _, r in ipairs(w.rects) do
    if r.terrain then
      for _, side in ipairs({ { r.x0 - 1, r.x0 }, { r.x1, r.x1 - 1 } }) do
        local open = true
        for _, q in ipairs(w.rects) do if q ~= r and q.terrain and side[1] >= q.x0 and side[1] < q.x1 and q.y0 <= r.y0 and q.y1 >= r.y1 then open = false end end
        if open and side[1] >= 0 and side[1] < w.width and not w:slopeAt(side[1]) then lg.setColor(C.groundEdge); lg.rectangle("fill", side[2], r.y0, 1, r.y1 - r.y0) end
      end
    end
  end
  end)
end

-- a greybox lamp post standing on the path at (x, y): a post and a lantern; lit = a passed checkpoint
function Sc.lampGrey(x, y, lit, since, t)
  x = math.floor(x)
  Sc.shadow(x, y - 1, 12)
  box(C.back, x - 2, y - 70, 4, 70)
  box(C.back, x - 4, y - 4, 8, 4)
  outlined(lit and C.gold or C.sky2, C.back, x - 5, y - 82, 10, 12)
  box(C.back, x - 6, y - 84, 12, 3)
  if lit then Sc.lampLight(x, y - 76, since, t) end
end

-- the greybox cat (22 x 16) at its feet; it sits on the ball, startles ("!"), leaps and runs
function Sc.catGrey(c, camx, t)
  local x, y = math.floor(c.x - camx + 0.5), math.floor(c.y + 0.5)
  if x < -30 or x > 350 then return end
  local lift = 0
  if c.state == "sit" then lift = (math.floor(t * 1.5) % 4 == 0) and 1 or 0     -- breathing
  elseif c.state == "scared" then lift = math.floor(math.min(1, c.t / 0.12) * 4) end
  if c.state == "run" then lift = math.floor(t * 12) % 2 end
  local top = y - 16 - lift
  outlined(C.cat, C.catEdge, x - 11, top, 22, 16)
  local ear = c.dir or 1                                           -- ears on the side it faces
  if c.state == "sit" then ear = -1 end
  box(C.catEdge, x + ear * 7 - 2, top - 3, 2, 3); box(C.catEdge, x + ear * 7 + 1, top - 3, 2, 3)
  box(C.catEdge, x - ear * 11 - (ear > 0 and 3 or 0), top + 3, 3, 2)   -- tail
  lg.setColor(C.label); F.print("CAT", x - 8, top + 5, 1)
  if c.state == "scared" or c.state == "leap" then lg.setColor(C.gold); F.print("!", x - 2, top - 12, 1)
  elseif c.state == "sit" and c.heard then lg.setColor(C.label); F.print("?", x - 2, top - 12, 1) end
  lg.setColor(1, 1, 1, 1)
end

-- the cat (Downtown), modelled on the user's Abyssinian: art/cat.png (tools/build_cat.py), 48 x 48 cells, rows
-- idle / leap / run, feet at (24, 44), drawn facing right. Sitting it faces Pepper; idle holds its first pose
-- for 2 s, then plays the tail curl, ear twitch and blink. Scared: crouch and arched back; leap: in the air by
-- its vertical speed; run: the gallop loop (frames 3 to 8).
local catImg, catQ
function Sc.cat(c, camx, t, px)
  local x, y = math.floor(c.x - camx + 0.5), math.floor(c.y + 0.5)
  if x < -40 or x > 360 then return end
  if not catImg then
    catImg = newImg("art/cat.png"); catQ = {}
    for r = 1, 3 do catQ[r] = {}; for i = 1, 8 do catQ[r][i] = lg.newQuad((i - 1) * 48, (r - 1) * 48, 48, 48, catImg:getDimensions()) end end
  end
  local row, fr, face = 1, 1, c.dir or 1
  if c.state == "sit" then
    face = (px and px < c.x) and -1 or 1
    local k = t % 4
    fr = k < 2 and 1 or math.min(8, 2 + math.floor((k - 2) * 4))
    if c.heard then fr = 1 end
  elseif c.state == "scared" then row, fr = 2, math.min(4, 2 + math.floor(c.t / 0.35 * 3))
  elseif c.state == "leap" then row = 2; fr = (c.vy or 0) < -60 and 5 or ((c.vy or 0) < 60 and 6 or 7)
  else row, fr = 3, 3 + math.floor(t * 14) % 6 end
  if c.state ~= "leap" then Sc.shadow(x, y - 1, 16) end
  lg.setColor(1, 1, 1, 1)
  lg.draw(catImg, catQ[row][fr], x, y, 0, face, 1, 24, 44)
  if c.state == "scared" or c.state == "leap" then lg.setColor(C.gold); F.print("!", x - 2, y - 44, 1)
  elseif c.state == "sit" and c.heard then lg.setColor(C.label); F.print("?", x - 2, y - 44, 1) end
  lg.setColor(1, 1, 1, 1)
end

-- the magpie (City Park), drawn in code: black head, back and breast, white belly and shoulder patch, a long
-- blue-green tail; 24 px long, feet at (x, y) (column 13), facing m.dir. Perched it flicks its tail now and then
-- (the second pose); flying it flaps (wings up / down, white primaries). The ball hangs from its beak (St:beak).
local MAGPIE = {
  perch = {
    "...................kk...",
    ".................kkkkk..",
    "................kkdkkkyy",
    "...............kkkkkkk..",
    "..............kkkkkkk...",
    "...........kkkwwkkkk....",
    "......bbbkkkwwwwwkk.....",
    "...bbbuuukkswwwwwk......",
    ".bbuuggkkkkkwwwwk.......",
    "bugg...kkkkkkssk........",
    "gg........kkkkk.........",
    "............l.l.........",
    "...........ll.ll........",
  },
  flick = {
    "...................kk...",
    ".................kkkkk..",
    "................kkdkkkyy",
    "...............kkkkkkk..",
    "..............kkkkkkk...",
    "...........kkkwwkkkk....",
    "...........kkwwwwwkk....",
    ".....bbbbkkkswwwwk......",
    "..bbbuuuukkkkwwwk.......",
    ".buggg.kkkkkkssk........",
    ".gg.......kkkkk.........",
    "............l.l.........",
    "...........ll.ll........",
  },
  up = {
    ".........kkk............",
    "........kwwwk...........",
    "........kwwwk...........",
    ".......kkwwk............",
    ".......kkkk.......kkk...",
    "......kkkkkkkkkkkkkkkkyy",
    "bbbuuukkkswwwwwwkkkkk...",
    ".gguu...kkkwwwwwkkk.....",
    "..g.......kkkkkk........",
    "........................",
    "........................",
    "........................",
  },
  down = {
    "........................",
    "........................",
    "........................",
    "........................",
    "..................kkk...",
    "......kkkkkkkkkkkkkkkkyy",
    "bbbuuukkkswwwwwwkkkkk...",
    ".gguu..kkkkwwwwwkkk.....",
    "..g....kkwwkkkkkk.......",
    "......kwwwk.............",
    ".....kwwwk..............",
    ".....kkk................",
  },
}
local MCOL = { k = { 18 / 255, 18 / 255, 26 / 255 }, d = { 44 / 255, 46 / 255, 58 / 255 }, b = { 38 / 255, 62 / 255, 128 / 255 },
  u = { 58 / 255, 96 / 255, 168 / 255 }, g = { 40 / 255, 108 / 255, 96 / 255 }, w = { 242 / 255, 244 / 255, 247 / 255 },
  s = { 176 / 255, 184 / 255, 198 / 255 }, y = { 30 / 255, 30 / 255, 34 / 255 }, l = { 78 / 255, 78 / 255, 86 / 255 } }
-- (6 Nov, art/cp-critters-06nov) the art: art/magpie.png (tools/build_magpie.py; SpriteCook Pixel Engine at 1x),
-- 5 cells of 32 x 26: perch, tail flick, wings up, level, down. 30 px beak to tail (size B of
-- docs/review/06nov/cp_critters/magpie_sizes_4x.png), drawn facing right; the feet are at cell (20, 25), the beak tip
-- at cell (29, 10) perched and (29, 13) flying (St:beak). Flying it loops up, level, down, level. Without the file:
-- the code magpie below.
local magImg, magQ
local function magpieArt()
  if magImg == nil then
    magImg = false
    if love.filesystem.getInfo("art/magpie.png") then
      magImg = lg.newImage("art/magpie.png"); magImg:setFilter("nearest", "nearest"); magQ = {}
      for i = 1, 5 do magQ[i] = lg.newQuad((i - 1) * 32, 0, 32, 26, magImg:getDimensions()) end
    end
  end
  return magImg
end
Sc.MAGPIE_FLAP = { 3, 4, 5, 4 }
-- the ball's bottom-centre point at the beak (St:beak): its top row on the beak, its near edge on the beak tip
function Sc.magpieBeak(m)
  if not magpieArt() then return m.x + m.dir * 11, m.y - (m.state == "fly" and 5 or 8) end
  return m.x + (m.dir > 0 and 12 or -11), m.y - (m.state == "fly" and 6 or 9)
end
function Sc.magpie(m, camx, t)
  local x, y = math.floor(m.x - camx + 0.5), math.floor(m.y + 0.5)
  if x < -40 or x > 360 then return end
  local flick = math.floor(t * 0.8) % 3 == 0 and (t * 0.8) % 1 < 0.25
  if magpieArt() then
    local i = m.state == "fly" and Sc.MAGPIE_FLAP[1 + math.floor(t * 12) % 4] or (flick and 2 or 1)
    lg.setColor(1, 1, 1, 1)
    if m.dir > 0 then lg.draw(magImg, magQ[i], x - 20, y - 25) else lg.draw(magImg, magQ[i], x + 21, y - 25, 0, -1, 1) end
    if m.heard and t - m.heard < 0.8 then lg.setColor(C.label); F.print("?", x - 2, y - 30, 1) end
    lg.setColor(1, 1, 1, 1)
    return
  end
  local pose
  if m.state == "fly" then pose = (math.floor(t * 12) % 2 == 0) and MAGPIE.up or MAGPIE.down
  else pose = flick and MAGPIE.flick or MAGPIE.perch end
  for row, line in ipairs(pose) do
    for col = 1, #line do
      local c = MCOL[line:sub(col, col)]
      if c then
        local dx = m.dir > 0 and (col - 14) or (14 - col)
        lg.setColor(c); lg.rectangle("fill", x + dx, y - 14 + row, 1, 1)
      end
    end
  end
  if m.heard and t - m.heard < 0.8 then lg.setColor(C.label); F.print("?", x - 2, y - 26, 1) end
  lg.setColor(1, 1, 1, 1)
end

-- layers 1 to 5 (everything behind the quay)
function Sc.drawFar(L, camx, t)
  local A = Sc.art()
  skyGap(); local on = vpush("sky")
  if Look.on then Look.sky() else                                  -- 1 sky (look.lua: the banded, dithered sky)
  for y = 0, 239 do
    local k = math.min(1, y / 170)
    lg.setColor(C.sky1[1] + (C.sky2[1] - C.sky1[1]) * k, C.sky1[2] + (C.sky2[2] - C.sky1[2]) * k, C.sky1[3] + (C.sky2[3] - C.sky1[3]) * k)
    lg.rectangle("fill", 0, y, 320, 1)
  end
  end
  local o = camx * 0.05 - t * 3                                    -- 2 clouds drift
  Look.use("clouds")
  lg.setColor(1, 1, 1, 1)
  for _, c in ipairs(L.clouds) do
    local x = math.floor((c.x - o) % L.cloudSpan - 120)
    if x < 330 and x + c.w > -10 then lg.draw(c.img, x, c.y) end
  end
  vpop(on); on = vpush("far")
  -- 3 far city: the skyline, bottom at y 138 (its misty base is behind the far shore trees). Over the whole
  -- level it moves at most 128 px (factor 128 / the camera's range): the strip is followed by its own first 128
  -- columns, which never bring a second City Hall tower on screen. (r5/bugs: the range was fixed at 2880 px, from
  -- when River Walk was 3200 px; at 3840 px the skyline stood still over the last two screens.)
  Look.use("city")
  lg.setColor(1, 1, 1, 1)
  local sw = A.skyline:getWidth()
  local sx = -math.floor(math.min(128, camx * 128 / math.max(320, (L.levelW or 3200) - 320)))
  lg.draw(A.skyline, sx, 138 - A.skyline:getHeight()); lg.draw(A.skyline, sx + sw, 138 - A.skyline:getHeight())
  lg.setColor(1, 1, 1, 1)
  Look.use("shore")
  lg.draw(A.shore, -math.floor(camx * 0.3), 113)                   -- 4 far shore and bridge: bottom row = waterline
  vpop(on); on = vpush("mid")
  Look.use("water")
  Sc.drawWater(camx, t)                                            -- 5 river
  Look.off()
  vpop(on)
end

-- a prop of the level; usable ones (solid / one-way) are outlined, decorations are flat
function Sc.drawProp(p, camx, layerColour)
  local x, y, w, h = p.x0 - camx, p.y0, p.x1 - p.x0, p.y1 - p.y0
  if x > 330 or x + w < -10 then return end
  if p.hidden then return end                                      -- a collision box inside bigger art (the ferry)
  if p.art then
    local art = Sc.art(); local im = art[p.art]
    local o = art.outlined[p.art] and 1 or 0                       -- outlined art is 1 px bigger on every side
    -- ax, ay: where the art's bottom-left goes when it is bigger than the collision box (the bench's box is
    -- only its seat; the legs and backrest are drawn but Pepper passes them)
    lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor((p.ax or p.x0) - camx) - o, (p.ay or p.y1) - im:getHeight() + o)
    return
  end
  if p.railing then                                                -- decorative railing: posts on the pavement's back edge
    local im = Sc.railing(w, "decor")
    lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x), p.y1 - im:getHeight())
    return
  end
  if p.fence then                                                  -- a fence Pepper climbs: handrail top = y0, posts on her line
    local im = Sc.railing(w, "fence", h + 7)                       -- (+7: the post caps rise above the handrail)
    lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x) - 1, y - 7 - 1)
    return
  end
  if p.kind == "decor" then box(layerColour, x, y, w, h)
  else outlined(C.prop, C.propEdge, x, y, w, h) end
  if p.name and p.name ~= "" and w >= 14 then
    lg.setColor(C.label)
    local tw = F.width(p.name, 1)
    local ly = y + math.min(h, 40) / 2 - 3
    if p.label == "top" then ly = y + 3                            -- label placement (City Park): near the top,
    elseif p.label == "below" then ly = y + h + 2; lg.setColor(C.propEdge) end   -- or under a thin bar, dark
    if tw <= w + 30 then F.print(p.name, math.floor(x + w / 2 - tw / 2), math.floor(ly), 1) end
  end
end

-- the ground of the play layer, painted once (in chunks, Sc.CHUNK). Every walkable top at or below
-- y 150 gets the pavement art, one column per pixel (it repeats every 320 px): its back edge is 12 px above the
-- line Pepper walks on, then the kerb and the road. Higher terrain (the bridge pier) stays a greybox.
-- (owner, 6 Nov) the road runs only under the level promenade (feet y 184, as the traffic's spans and look.lua's
-- receding road rows); a ramp or the lower quay stands on the granite quay wall instead
Sc.PROMENADE, Sc.QUAY_Y0, Sc.QUAY_JOINT = 184, 196, { 72 / 255, 82 / 255, 107 / 255 }
Sc.STEP_RW = 8                                                    -- (day/07nov-ground) River Walk's ramps: 8 px stone steps (0.17 m)
local function columnTop(w, x)                                      -- the first walkable top at or under y 150, or nil
  if x < 0 or x >= w.width then return nil end
  for _, m in ipairs(columnRuns(w, x, "all")) do if m[1] >= 150 then return m[1] end end
end
function Sc.paintGround(w, props, def)
  if def and def.ground == "quay" then return Sc.paintQuay(w, props, def) end
  local art = Sc.art()
  local pave = art.pavement
  local pw, ph = pave:getDimensions()
  local q = {}
  for i = 0, pw - 1 do q[i] = lg.newQuad(i, 0, 1, ph, pw, ph) end
  local road = art.road                                             -- the road under the paving (tools/make_road.py)
  local rw, rh = road:getDimensions()
  local rq = {}
  for i = 0, rw - 1 do rq[i] = lg.newQuad(i, 0, 1, rh, rw, rh) end
  local quay = art.quaywall                                         -- (owner, 6 Nov) under ramps and the lower quay
  local qw, qh = quay:getDimensions()                               -- (tools/make_quaywall.py)
  local wq = {}
  for i = 0, qw - 1 do wq[i] = lg.newQuad(i, 0, 1, qh, qw, qh) end
  return chunked(w, function(xa, xb)                              -- (painted once per chunk: Sc.CHUNK)
  local high, flat = {}, {}
  for x = 0, w.width - 1 do
    local merged = columnRuns(w, x, "all")
    for _, m in ipairs(merged) do
      if m[1] < 150 then high[#high + 1] = { x, m[1], m[2] }
      else
        if x >= xa and x < xb then                                  -- (drawn in the chunk's columns only)
          lg.setColor(1, 1, 1, 1)
          clip(x, 0, 1, m[2])
          lg.draw(pave, q[x % pw], x, m[1] - 12)
          if m[1] == Sc.PROMENADE then
            lg.draw(road, rq[x % rw], x, m[1] + 15)                 -- rows 27+ of the paving art are the road
          else                                                      -- (owner, 6 Nov) a ramp or the lower quay: no road
            clip(x, m[1] + 15, 1, m[2] - m[1] - 15)                 -- under it (the road was a sheared copy), the granite
            lg.draw(quay, wq[x % qw], x, Sc.QUAY_Y0)                -- quay wall, its courses level (anchored in the world)
            local l, r = columnTop(w, x - 1), columnTop(w, x + 1)   -- where the level promenade (the road) starts beside
            if l == Sc.PROMENADE or r == Sc.PROMENADE then          -- it: a clean head joint, the road beside it
              lg.setColor(Sc.QUAY_JOINT); lg.rectangle("fill", x, m[1] + 15, 1, m[2] - m[1] - 15); lg.setColor(1, 1, 1, 1)
            end
          end
          clip()
        end
        if m[1] == 184 then flat[x] = true end
      end
    end
  end
  -- manhole covers and kerb drains on the promenade road, at fixed pseudo-random spots where the road is flat
  Sc.decals = {}
  local function flatRun(x0, x1) for x = x0, x1 do if not flat[x] then return false end end return true end
  lg.setColor(1, 1, 1, 1)
  local x, k = 150, 0
  while x < w.width - 30 do
    k = k + 1
    if flatRun(x - 2, x + 22) then
      local y = 199 + ((k % 2 == 0) and 4 or 27)
      lg.draw(art.manhole, x, y); Sc.decals[#Sc.decals + 1] = { im = art.manhole, x = x, y = y }   -- (look.lua redraws them)
    end
    x = x + 260 + (k * 97) % 160
  end
  x, k = 60, 0
  while x < w.width - 20 do
    k = k + 1
    if flatRun(x - 2, x + 14) then lg.draw(art.drain, x, 200); Sc.decals[#Sc.decals + 1] = { im = art.drain, x = x, y = 200 } end
    x = x + 180 + (k * 53) % 90
  end
  local function covered(x)                                         -- under art that replaces the greybox (the pier)
    for _, p in ipairs(props or {}) do if p.covers and x >= p.x0 and x < p.x1 then return true end end
    return false
  end
  for _, h in ipairs(high) do                                      -- greybox terrain drawn last, over the pavement
    if not covered(h[1]) then
      lg.setColor(C.ground); lg.rectangle("fill", h[1], h[2], 1, h[3] - h[2])
      lg.setColor(C.groundEdge); lg.rectangle("fill", h[1], h[2], 1, 1)
    end
  end
  end)
end

-- (art/rw-ground-06nov) River Walk's ground by rule (def.ground = "quay"), owner 6 Nov: "these connections of
-- asphalt really look weird, this is still the first level even". Every column of terrain is one of three kinds:
--   road: the promenade (top y 184, the traffic's stretches): the approved paving (pavement.png rows 0-21: the
--         slabs and the light kerb top), a granite kerb face (5 rows, joints under the kerb top's joints, every
--         16 px), then the asphalt (road.png, tools/make_road.py: flat fills)
--   quay: the lower quay by the water (top y 216): the same paving and granite coping, then the quay wall: granite
--         blocks in courses on one world grid (bed joints every 16 px from y 231, blocks 40 px, every other course
--         offset 20), so the walls of the ramps and both quays line up. A quay that ends at the water ends in a
--         coping stone running to the water's edge (a light strip) and a quoined corner.
--   ramp: the slopes (the terrain's own diagonal, unchanged): a clean 45 degree band of slabs in the paving's own
--         colours (courses parallel to the slope, flat fills), a coping stone along the slope (the kerb's colours,
--         no joints) and the quay wall's courses under it.
-- Where the road ends (the top of a ramp) its kerb turns the corner and runs down to the screen's bottom (a light
-- strip with a rounded inside corner); those few pixels are drawn again after look.lua's road (Sc.drawRoadEnds).
-- Nothing here changes where Pepper stands: only the drawing.
local function rgb(r, g, b) return { r / 255, g / 255, b / 255 } end
local Q = {
  top1 = rgb(229, 221, 218), top2 = rgb(216, 209, 206), tj = rgb(179, 174, 174),   -- the kerb top (pavement rows 20-21)
  -- granite (kerb face, coping face, wall). The look's grade pushes mid and dark greys to violet (the ground is
  -- graded twice: painted under the back layer's grade, drawn under the ground's), so these are a shade green-warm
  -- in the file to show as warm grey granite on screen (about 186/160/140 the face, 138 the wall)
  kf1 = rgb(165, 170, 171), kf2 = rgb(142, 146, 141), kf3 = rgb(124, 127, 116), kj = rgb(105, 109, 92),
  sh = rgb(72, 77, 56), w = rgb(122, 125, 114), wh = rgb(135, 138, 130), wj = rgb(92, 97, 77), we = rgb(103, 107, 91),
  pb = rgb(157, 160, 173), pj = rgb(168, 170, 182),                                -- the paving's back edge and joints
  ps = { rgb(196, 192, 195), rgb(207, 200, 198), rgb(184, 183, 190) },             -- its slabs (pavement.png's colours)
}
local COURSE, COURSE0, BLOCK = 16, 231, 40
-- the granite wall's colour at (x, y); d = distance to a corner at the water (0 = the corner's column) or nil
local function wallColour(x, y, d)
  local k = math.floor((y - COURSE0) / COURSE)
  local r = y - COURSE0 - k * COURSE
  if r == 0 then return Q.wj end
  if d and d == 0 then return Q.we end
  local head
  if d and d < 30 then head = d == ((k % 2 == 0) and 13 or 25)                     -- quoins: long and short in turn
  else head = (x - (k % 2) * (BLOCK / 2)) % BLOCK == 0 end
  if head then return Q.wj end
  return r == 1 and Q.wh or Q.w
end
-- the road's end: its kerb turns the corner towards us (8 columns; dir 1: the road is on the left, -1: on the right).
-- Rows from the kerb top's first row (t + 8); returns a colour or nil (leave what is there)
local function cornerColour(c, row)
  -- c: 0 .. 7 from the road's side (7 = the column against the wall's corner); row: 0 = t + 8 (the kerb top),
  -- 2 = the face's first row, 7 = the road's first.
  -- (day/07nov-ground, audit RW1/RW10: the kerb return ran down to the screen's bottom as a light strip) the kerb
  -- ends in an end stone against the wall (its end joint); the asphalt runs on to the wall's quoins, with a soft
  -- shadow at its foot (Sc.roadEnds, drawn over look.lua's road)
  -- the kerb's return down the road's end: 3 px of granite face (lit, mid, shade) with a rounded top corner,
  -- then the shadow row against the wall's quoins
  if c == 7 then return row <= 1 and Q.tj or Q.sh end
  if c == 6 then if row == 0 then return nil end return row <= 2 and Q.kf2 or Q.kf3 end
  if c == 5 then if row <= 1 then return Q.top2 end return row == 2 and Q.kf1 or Q.kf2 end
  if c == 4 then if row <= 1 then return nil end return (row <= 7) and nil or Q.kf1 end
  return nil
end
-- the shadow on the asphalt beside the wall's corner (alpha, 0 = none); c as above, row from the road's first row.
-- dir 1 (the wall on the road's right, the sun upper left): a 2 px contact line. dir -1 (the wall on its left):
-- the wall's cast shadow, 5 px at the kerb widening 1 px every 6 rows nearer the camera, its edge 1 px softer
local function roadShade(c, row, dir)
  local i = 3 - c                                                  -- columns out from the kerb return (c 4 .. 7)
  if i < 0 then return 0 end
  if dir == 1 then return (i == 0) and 0.35 or ((i == 1) and 0.15 or 0) end
  local w = 4 + math.floor(row / 8)                                -- the wall's cast shadow (wall on the road's left)
  if i < w - 1 then return 0.34 elseif i == w - 1 then return 0.17 end
  return 0
end
-- (day/07nov-ground) Pepper's front garden (a GARDEN prop with garden = true: x0-x1, its door path path0-path1):
-- owner 7 Nov, "Kennel like this would never be on the street": the kennel stands on a lawn in front of her house.
-- Painted by rule over the paving rows (t - 12 .. t + 7) of each column; the kerb and the road under it stay.
--   lawn: a dark row where it meets the house (its contact shadow), a shade row, then flat grass with v-shaped
--         tufts on a 6 px grid (three bands, offset 0 / 3 / 1), a lit lip on its front row, a tuft over the
--         kerb's top every 5 px (a lip, so lawn and kerb do not meet in a hard line)
--   joins: the paving next to the lawn (the door path, the garden's end) takes grass over its edge, 2 px deep,
--          on a fixed row rule (a worn edge, never a straight seam)
--   picket edging: low white pickets along the kerb on both sides of the path, rows t .. t + 7 (under her
--          line: it never covers her), 2 px pickets every 4 px with a pointed top, two rails, a post at each end
--          and by the path; decoration (no outline, edges a darker shade), a shadow under each picket on the kerb.
local G = { dark = rgb(68, 110, 72), shade = rgb(86, 132, 66), base = rgb(109, 144, 46), lit = rgb(148, 172, 57),
            tip = rgb(148, 172, 57), pick = rgb(240, 236, 224), pickD = rgb(211, 195, 180), rail = rgb(192, 172, 142),
            post = rgb(226, 209, 196), postD = rgb(170, 162, 158) }
local function gardenAt(gs, x)
  for _, g in ipairs(gs) do
    if x >= g.x0 and x < g.x1 then return g, (g.path0 and x >= g.path0 and x < g.path1) end
  end
end
Sc.G = G
-- the columns of an art file's bottom row that are opaque (its foot), cached: { x0, x1 } or false
local FOOT = {}
function Sc.footCols(name)
  if FOOT[name] == nil then
    FOOT[name] = false
    local ok, d = pcall(love.image.newImageData, "art/scene/" .. name .. ".png")
    if ok then
      local h = d:getHeight()
      local x0, x1
      for x = 0, d:getWidth() - 1 do local _, _, _, a = d:getPixel(x, h - 1); if a > 0 then x0 = x0 or x; x1 = x end end
      if x0 then FOOT[name] = { x0 = x0, x1 = x1 } end
    end
  end
  return FOOT[name]
end
function Sc.paintGarden(gs, x, t, px)
  local g, onPath = gardenAt(gs, x)
  local function lawnAt(u) local h, p = gardenAt(gs, u); return h and not p end
  if g and not onPath then
    for y = t - 12, t + 7 do
      local r = y - (t - 12)
      local c = G.base
      if r == 0 then c = G.dark elseif r == 1 then c = G.shade
      elseif y == t + 7 then c = G.lit
      else
        local band = math.floor((r - 2) / 6)                        -- three bands of tufts
        local by = (t - 12) + 2 + band * 6 + 2
        local u = (x + ({ 0, 3, 1 })[band % 3 + 1]) % 6
        if y == by and (u == 0 or u == 2) then c = G.lit
        elseif y == by + 1 and u == 1 then c = G.shade end
      end
      px(c, x, y)
    end
    if x % 5 == 0 then px(G.tip, x, t + 8) end                       -- a tuft over the kerb's top
  elseif lawnAt(x - 1) or lawnAt(x + 1) or lawnAt(x - 2) or lawnAt(x + 2) then
    local d = (lawnAt(x - 1) or lawnAt(x + 1)) and 1 or 2           -- paving beside the lawn: grass over its edge
    for y = t - 10, t + 6 do
      if (d == 1 and y % 3 ~= 0) or (d == 2 and y % 4 == 1) then px(d == 1 and G.base or G.lit, x, y) end
    end
  end
  -- the picket edging (not on the path)
  if g and not onPath then
    local e0 = (x - g.x0 < 3) or (g.path0 and x >= g.path0 - 3 and x < g.path0) or (g.path1 and x >= g.path1 and x < g.path1 + 3) or (x >= g.x1 - 3)
    if e0 then                                                      -- a post: 3 px, lit left, shaded right
      local k = (x - g.x0 < 3) and (x - g.x0) or ((x >= g.x1 - 3) and (x - (g.x1 - 3)) or ((x < (g.path0 or 0)) and (x - (g.path0 - 3)) or (x - g.path1)))
      for y = t, t + 7 do px(k == 2 and G.postD or G.post, x, y) end
      px(G.postD, x, t + 8)
    else
      local u = x % 4
      if u == 0 or u == 1 then                                      -- a picket
        if u == 0 then px(G.pick, x, t + 1) end                       -- the point
        for y = t + 2, t + 7 do px(u == 0 and G.pick or G.pickD, x, y) end
        px(Q.tj, x, t + 8)                                          -- its shadow on the kerb top
      else
        px(G.rail, x, t + 3); px(G.rail, x, t + 6)                   -- the rails between the pickets
      end
    end
  end
end
Sc.roadEnds = {}
function Sc.paintQuay(w, props, def)
  local art = Sc.art()
  local pave = art.pavement
  local pw, ph = pave:getDimensions()
  local q = {}
  for i = 0, pw - 1 do q[i] = lg.newQuad(i, 0, 1, 22, pw, ph) end                -- the paving rows 0-21 only
  local road = art.road
  local rw, rh = road:getDimensions()
  local rq = {}
  for i = 0, rw - 1 do rq[i] = lg.newQuad(i, 0, 1, rh, rw, rh) end
  -- one pass over the level: each column's top (its first run at or below y 150), kind and distances to ends
  local W = w.width
  local top, kind = {}, {}
  for x = 0, W - 1 do
    local merged = columnRuns(w, x, "all")
    for _, m in ipairs(merged) do if m[1] >= 150 then top[x] = m[1]; break end end
    if top[x] then
      if w:slopeAt(x) then kind[x] = "ramp"
      elseif merged[1][1] == 184 then kind[x] = "road"
      else kind[x] = "quay" end
    end
  end
  local dR, dL = {}, {}                                             -- distance to a quay's end at the water
  local n = nil
  for x = W - 1, 0, -1 do
    if not top[x] then n = nil elseif kind[x] == "quay" then n = (n == nil and (x + 1 < W) and not top[x + 1]) and 0 or (n and n + 1); dR[x] = n else n = nil end
  end
  n = nil
  for x = 0, W - 1 do
    if not top[x] then n = nil elseif kind[x] == "quay" then n = (n == nil and x > 0 and not top[x - 1]) and 0 or (n and n + 1); dL[x] = n else n = nil end
  end
  -- the road's ends next to a ramp: { x of the corner's first column, dir }
  local ends = {}
  for x = 1, W - 1 do
    if kind[x - 1] == "road" and kind[x] == "ramp" then ends[#ends + 1] = { x0 = x - 8, dir = 1 } end
    if kind[x - 1] == "ramp" and kind[x] == "road" then ends[#ends + 1] = { x0 = x, dir = -1 } end
  end
  -- (day/07nov-ground, audit RW1/RW10) beside a road's end the wall's corner is dressed in quoins (its distance
  -- from the road, as at the water's corners), instead of a light kerb strip running down to the screen's bottom
  local dRoad = {}
  for _, e in ipairs(ends) do
    for i = 0, 29 do
      local x = e.dir == 1 and (e.x0 + 8 + i) or (e.x0 - 1 - i)
      if kind[x] == "ramp" or kind[x] == "quay" then dRoad[x] = i end
    end
  end
  local function cornerAt(x)                                         -- (corner column c from the road's side, or nil)
    for _, e in ipairs(ends) do
      if x >= e.x0 and x < e.x0 + 8 then return e.dir == 1 and (x - e.x0) or (7 - (x - e.x0)) end
    end
  end
  local gardens = {}                                                -- (day/07nov-ground) the front garden
  for _, p in ipairs(def.props or {}) do if p.garden then gardens[#gardens + 1] = p end end
  -- (day/07nov-ground) the transitions this painter stamps, marked for the joins check (joins.lua)
  Jn.reset()
  for _, g in ipairs(gardens) do
    Jn.mark(g.x1, "garden>road")
    if g.path0 then Jn.mark(g.path0, "garden>path"); Jn.mark(g.path1, "path>garden") end
  end
  for _, e in ipairs(ends) do Jn.mark(e.dir == 1 and e.x0 + 8 or e.x0, e.dir == 1 and "road>ramp" or "ramp>road") end
  for x = 1, W - 1 do
    if kind[x - 1] == "ramp" and kind[x] == "quay" then Jn.mark(x, "ramp>quay") end
    if kind[x - 1] == "quay" and kind[x] == "ramp" then Jn.mark(x, "quay>ramp") end
    if kind[x - 1] == "quay" and not top[x] then Jn.mark(x, "quay>water") end
    if not top[x - 1] and kind[x] == "quay" then Jn.mark(x, "water>quay") end
  end
  local under = {}                                                  -- the columns under the bridge (its shadow)
  local spans = {}                                                  -- (day/07nov-ground, audit RW6: the shadow's ends
  for _, ps in ipairs(def.passages or {}) do                        -- were vertical cuts) its spans, for the slant
    spans[#spans + 1] = { ps.vx0 or ps.x0, ps.vx1 or ps.x1 }
    for x = (ps.vx0 or ps.x0) - 2, (ps.vx1 or ps.x1) + 22 do under[x] = true end
  end
  -- the bridge's shadow at (x, paving row r): the sun is upper left, so each row's shadow is shifted 1 px right per
  -- row nearer the camera (a parallelogram, its ends slanting), and the darkest band is the narrowest (1 px in)
  local function shadeAt(x, r)
    for _, sp in ipairs(spans) do
      local a, b = sp[1] + math.floor(r / 2), sp[2] + math.floor(r / 2)
      if x >= a and x < b then
        local e = math.min(x - a, b - 1 - x)                          -- columns from the shadow's slanted ends
        if e == 0 then return 0.86 end                                -- a 1 px penumbra at each end
        if r < 7 then return 0.62 elseif r < 14 then return 0.74 else return 0.86 end
      end
    end
  end
  local SHADE = { { 7, 0.62 }, { 14, 0.74 }, { 22, 0.86 } }           -- the bridge's shadow: three flat bands, back to front
  local function px(c, x, y) lg.setColor(c); lg.rectangle("fill", x, y, 1, 1) end
  local function run(c, x, y0, y1) if y1 > y0 then lg.setColor(c); lg.rectangle("fill", x, y0, 1, y1 - y0) end end
  -- (day/07nov-ground, audit RW2/RW3/RW9: the ramp was the flat recipe sheared per column, with a seam at each
  -- end) the ramp as stone steps, a slope tile of STEP px rise per STEP px run (Sc.STEP_RW): each step one granite
  -- tread, its courses level, a joint at its edge, the coping nosing along its front, its face and the wall's
  -- courses under it on the world grid; the first and last steps are the landings into the flat paving
  local function stepTop(x)
    local t0 = top[x]
    local S = Sc.STEP_RW
    return Sc.PROMENADE + math.floor((t0 - Sc.PROMENADE) / S + 0.5) * S
  end
  local function column(x, bottom)
    local t, k = top[x], kind[x]
    if k == "ramp" then t = stepTop(x) end
    -- 1 the paving (rows 0-21 from t - 12)
    if k == "ramp" then
      local edge = kind[x - 1] ~= "ramp" or stepTop(x - 1) ~= t     -- a step's first column: the joint
      local si = math.floor(x / Sc.STEP_RW)
      for r = 0, 19 do
        local c
        if r == 0 then c = Q.pb
        elseif edge then c = Q.pj
        elseif r % 5 == 0 then c = Q.pj
        else c = Q.ps[(si * 2 + math.floor(r / 5)) % 3 + 1] end
        px(c, x, t - 12 + r)
      end
      px(edge and Q.tj or Q.top1, x, t + 8); px(edge and Q.tj or Q.top2, x, t + 9)
    else
      if under[x] then
        for r = 0, 21 do
          local k = shadeAt(x, r) or 1
          clip(x, t - 12 + r, 1, 1)
          lg.setColor(k, k, k * (k < 1 and 1.06 or 1), 1); lg.draw(pave, q[x % pw], x, t - 12)
        end
        clip()
      else
        lg.setColor(1, 1, 1, 1); lg.draw(pave, q[x % pw], x, t - 12)
      end
      local d = dR[x] or dL[x]
      if d and d <= 3 then                                           -- the coping stone along the water's edge
        local c = (d == 3) and Q.pj or (d == 0 and Q.top2 or Q.top1)
        run(c, x, t - 12, t + 10)
      end
    end
    -- 2 the granite kerb / coping face (rows t + 10 .. t + 14)
    local joint = k ~= "ramp" and (x % 16 == 0) or (k == "ramp" and (kind[x - 1] ~= "ramp" or stepTop(x - 1) ~= t))
    local edge = (dR[x] == 0 or dL[x] == 0)
    for r = 0, 4 do
      local c = (r == 0) and Q.kf1 or (r == 4 and Q.kf3 or Q.kf2)
      if joint or edge then c = (r == 0 and edge) and Q.kf2 or Q.kj end
      px(c, x, t + 10 + r)
    end
    -- 3 under it: the asphalt, or the quay wall
    if k == "road" then
      lg.setColor(1, 1, 1, 1)
      clip(x, t + 15, 1, bottom - t - 15); lg.draw(road, rq[x % rw], x, t + 15); clip()
    else
      local d = dR[x] or dL[x] or dRoad[x]
      px(Q.sh, x, t + 15)
      for y = t + 16, bottom - 1 do px(wallColour(x, y, d), x, y) end
    end
    if #gardens > 0 and k == "road" then Sc.paintGarden(gardens, x, t, px) end
    -- 4 the road's end: the kerb turns the corner
    local c = cornerAt(x)
    if c then for row = 0, bottom - (t + 8) - 1 do local col = cornerColour(c, row); if col then px(col, x, t + 8 + row) end end end
  end
  local g = chunked(w, function(xa, xb)
    for x = xa, xb - 1 do
      if top[x] then
        local bottom
        for _, m in ipairs(columnRuns(w, x, "all")) do if m[1] == top[x] then bottom = m[2] end end
        column(x, bottom)
      end
    end
    -- (day/07nov-ground, audit RW4/5/7/8: the quay ended in one vertical line to the screen's bottom, no waterline)
    -- the quay-end cap: the coping overhangs the wall's end by 2 px with its shadow under it, the arris wet and dark
    -- from the river's surface (y 224) down, a ripple along the waterline, the wall's dark reflection in the water
    for x = xa, xb - 1 do
      local side = (dR[x] == 0 and 1) or (dL[x] == 0 and -1) or nil
      if side and top[x] then
        local t = top[x]
        for i = 1, 2 do                                             -- the overhang
          local ox = x + side * i
          run(i == 1 and Q.top1 or Q.top2, ox, t - 11, t + 10); px(Q.pj, ox, t - 12)
          for r = 0, 4 do px(i == 2 and Q.kj or (r == 0 and Q.kf1 or Q.kf2), ox, t + 10 + r) end
          lg.setColor(0.04, 0.06, 0.16, i == 1 and 0.5 or 0.35); lg.rectangle("fill", ox, t + 15, 1, 2)   -- its shadow
        end
        local wl = Sc.WATER_Y or 224
        for i = 0, 1 do lg.setColor(0.08, 0.10, 0.16, i == 0 and 0.5 or 0.25); lg.rectangle("fill", x - side * i, wl, 1, 240 - wl) end   -- wet stone
        for i, a in ipairs({ 0.30, 0.22, 0.14, 0.08 }) do           -- the reflection, fading out from the wall
          lg.setColor(0.04, 0.08, 0.22, a); lg.rectangle("fill", x + side * (2 + i), wl + 1, 1, 240 - wl - 1)
        end
        lg.setColor(0.86, 0.94, 0.97, 0.9)                          -- the waterline: a ripple against the stone
        for i = 1, 6 do if i % 3 ~= 0 then lg.rectangle("fill", x + side * i, wl, 1, 1) end end
        lg.setColor(1, 1, 1, 1)
      end
    end
    -- (day/07nov-ground, audit RW12-14: things stood on the paving with no contact) the contact pass: under every
    -- piece of back art that stands on the paving's back edge (y1 174: houses, trees, pots), a soft shadow on the
    -- paving's first two rows under its bottom row's columns (a tree grate was tried: it read as a bar in front)
    for _, pr in ipairs(def.props or {}) do
      if pr.art and pr.layer == "back" and pr.y1 == 174 and not pr.garden then
        local cols = Sc.footCols(pr.art)
        local ax = pr.ax or pr.x0
        if cols and ax + cols.x1 >= xa - 8 and ax + cols.x0 < xb + 8 then
          local a0, a1 = ax + cols.x0, ax + cols.x1
          for x = math.max(xa, a0 - 1), math.min(xb - 1, a1 + 1) do
            if top[x] and not gardenAt(gardens, x) and not under[x] then
              local t = top[x]
              lg.setColor(0.10, 0.08, 0.14, 0.30); lg.rectangle("fill", x, t - 12, 1, 1)
              lg.setColor(0.10, 0.08, 0.14, 0.16); lg.rectangle("fill", x, t - 11, 1, 1)
            end
          end
        end
      end
    end
    lg.setColor(1, 1, 1, 1)
    for x = xa, xb - 1 do                                           -- greybox terrain above y 150 (none is drawn
      for _, m in ipairs(columnRuns(w, x, "all")) do                 -- here: the bridge pier's art covers it)
        if m[1] < 150 then
          local cov = false
          for _, p in ipairs(props or {}) do if p.covers and x >= p.x0 and x < p.x1 then cov = true end end
          if not cov then lg.setColor(C.ground); lg.rectangle("fill", x, m[1], 1, m[2] - m[1]); lg.setColor(C.groundEdge); lg.rectangle("fill", x, m[1], 1, 1) end
        end
      end
    end
    -- manhole covers and kerb drains, where the road is flat and at least 12 px from its ends
    lg.setColor(1, 1, 1, 1)
    local function flatRun(x0, x1) for x = x0 - 12, x1 + 12 do if kind[x] ~= "road" then return false end end return true end
    local x, k = 150, 0
    while x < W - 30 do
      k = k + 1
      if flatRun(x - 2, x + 22) then lg.draw(art.manhole, x, 199 + ((k % 2 == 0) and 4 or 27)) end
      x = x + 260 + (k * 97) % 160
    end
    x, k = 60, 0
    while x < W - 20 do
      k = k + 1
      if flatRun(x - 2, x + 14) then lg.draw(art.drain, x, 200) end
      x = x + 180 + (k * 53) % 90
    end
  end)
  -- the decals for look.lua's road (the same spots)
  Sc.decals = {}
  local function flatRun(x0, x1) for x = x0 - 12, x1 + 12 do if kind[x] ~= "road" then return false end end return true end
  local x, k = 150, 0
  while x < W - 30 do
    k = k + 1
    if flatRun(x - 2, x + 22) then Sc.decals[#Sc.decals + 1] = { im = art.manhole, x = x, y = 199 + ((k % 2 == 0) and 4 or 27) } end
    x = x + 260 + (k * 97) % 160
  end
  x, k = 60, 0
  while x < W - 20 do
    k = k + 1
    if flatRun(x - 2, x + 14) then Sc.decals[#Sc.decals + 1] = { im = art.drain, x = x, y = 200 } end
    x = x + 180 + (k * 53) % 90
  end
  -- the road ends' corners again, as small canvases drawn over look.lua's road (painted here, as the chunks are)
  Sc.roadEnds = {}
  for _, e in ipairs(ends) do
    local t = top[e.x0] or 184
    local y0, bottom = t + 8, (w.height or 240)
    local W8 = 16                                                     -- (the cast shadow can reach 12 columns out)
    local ox = e.dir == 1 and (8 - W8) or 0                           -- the canvas's left, from e.x0
    local cv = lg.newCanvas(W8, bottom - y0)
    cv:setFilter("nearest", "nearest")
    lg.push("all"); lg.setCanvas(cv); lg.clear(0, 0, 0, 0); lg.origin()
    for i = 0, W8 - 1 do
      local c = e.dir == 1 and (i + ox) or (7 - i)                    -- c may run below 0 (further out on the road)
      for row = 7, bottom - y0 - 1 do
        local col = (c >= 0 and c <= 7) and cornerColour(c, row) or nil
        local a = roadShade(c, row - 7, e.dir)
        if col then lg.setColor(col); lg.rectangle("fill", i, row, 1, 1)
        elseif a > 0 then lg.setColor(0.04, 0.05, 0.10, a); lg.rectangle("fill", i, row, 1, 1) end
      end
    end
    lg.pop()
    Sc.roadEnds[#Sc.roadEnds + 1] = { cv = cv, x = e.x0 + ox, y = y0 }
  end
  return g
end
-- the road ends' corner pieces over look.lua's road (stage.lua, right after Look.road)
function Sc.drawRoadEnds(cam)
  lg.setColor(1, 1, 1, 1)
  for _, e in ipairs(Sc.roadEnds or {}) do
    if e.x - cam > -10 and e.x - cam < 330 then lg.draw(e.cv, e.x - cam, e.y) end
  end
end

-- Obstacles stand on the line Pepper walks on, so they read as in her way.
-- Decoration (lamp posts, the pot) stands further back, on the back edge of the pavement by the water:
-- its base is EDGE px above Pepper's walking line (the pavement's back edge is 12 px above it).
Sc.EDGE = 10

-- pixel-exact filled ellipse (rx, ry in px), drawn row by row so the edges stay crisp at 1x
local function ellipse(cx, cy, rx, ry)
  cx, cy = math.floor(cx + 0.5), math.floor(cy + 0.5)
  for dy = -ry, ry do
    local k = ry == 0 and 1 or math.sqrt(math.max(0, 1 - (dy / (ry + 0.5)) ^ 2))
    local hw = math.floor(rx * k + 0.5)
    if hw > 0 then lg.rectangle("fill", cx - hw, cy + dy, hw * 2, 1) end
  end
end
Sc.ellipse = ellipse

-- a soft shadow on the ground: a flat ellipse centred on the feet line (2 shades: rim and core)
local SHADOW = { 24 / 255, 28 / 255, 44 / 255 }
function Sc.shadow(cx, y, w, depth)
  if w < 4 then return end
  local rx = math.floor(w / 2)
  if depth then                                                    -- something with back and front feet (the bench):
    local ry = math.floor(depth / 2) + 1                           -- the shadow fills the ground between them, so it
    lg.setColor(SHADOW[1], SHADOW[2], SHADOW[3], 0.26); ellipse(cx, y - ry + 1, rx, ry)   -- stands on the pavement
    lg.setColor(SHADOW[1], SHADOW[2], SHADOW[3], 0.18); ellipse(cx, y - ry + 1, math.max(1, rx - 4), math.max(0, ry - 1))
    lg.setColor(1, 1, 1, 1)
    return
  end
  lg.setColor(SHADOW[1], SHADOW[2], SHADOW[3], 0.30); ellipse(cx, y, rx, 1)
  lg.setColor(SHADOW[1], SHADOW[2], SHADOW[3], 0.22); ellipse(cx, y, math.max(1, rx - 3), 0)
  lg.setColor(1, 1, 1, 1)
end

-- the warm light of a lit lamp: a steady glow around the lantern, and a flash that spreads out when it lights up
function Sc.lampLight(cx, cy, since, t)
  local f = 0.92 + 0.08 * math.sin(t * 7 + cx)                    -- a slight flicker
  lg.setColor(1, 0.86, 0.5, 0.10 * f); ellipse(cx, cy, 12, 12)
  lg.setColor(1, 0.86, 0.5, 0.14 * f); ellipse(cx, cy, 8, 8)
  if since < 0.6 then
    local k = since / 0.6
    lg.setColor(1, 0.92, 0.65, 0.45 * (1 - k)); ellipse(cx, cy, 6 + 22 * k, 6 + 22 * k)
  end
  lg.setColor(1, 1, 1, 1)
end

-- 5 the river (art/scene/water.png from the SpriteCook strip, y 146 to 240). Each row scrolls on its own:
-- the far water near the shore moves with the far shore (0.3) and barely flows, the near water moves with the
-- camera more (up to 0.55) and flows faster to the left, and every row wobbles a pixel or two (ripples).
-- The glints (water_data.lua) ride with their row and twinkle.
local GLINTS = require("water_data")
function Sc.drawWater(camx, t)
  local A = Sc.art()
  local ww, wh = A.water:getDimensions()
  local off = {}
  lg.setColor(1, 1, 1, 1)
  for y = 0, wh - 1 do
    local depth = y / (wh - 1)
    local rip = math.sin(t * 1.3 + y * 0.55) * (0.4 + depth * 1.4)
    local o = math.floor(camx * (0.3 + 0.25 * depth) + t * (1 + 5 * depth) + rip + 0.5) % ww
    off[y] = o
    lg.draw(A.water, A.waterQ[y], -o, 146 + y); lg.draw(A.water, A.waterQ[y], ww - o, 146 + y)
  end
  for i, g in ipairs(GLINTS) do
    if math.sin(t * (1.6 + (i % 4) * 0.3) + i * 1.7) > -0.25 then
      lg.setColor(g[4] / 255, g[5] / 255, g[6] / 255, 1)
      local x = (g[1] - off[g[2]]) % ww
      lg.rectangle("fill", x, 146 + g[2], g[3], 1)
      if x + g[3] > ww then lg.rectangle("fill", x - ww, 146 + g[2], g[3], 1) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- a low passage under the bridge: its back wall (dark, a little lighter low down) is drawn before the ground, so
-- the pavement runs into it; then the pavement inside is shaded. Ends fade with a checker dither.
local PASS1, PASS2 = { 21 / 255, 20 / 255, 31 / 255 }, { 38 / 255, 40 / 255, 56 / 255 }
-- (day/07nov-rwarch, owner 7 Nov board: "rw_bridge_arch_06n: redraw") p.arch: the underpass of River Walk's stone
-- bridge seen end on, as on Stockholm's quays, BUILT by rule (tools/build_rw_arch.py -> art/scene/rw_arch.png,
-- 130 x 25; its top row, y 191, only fills the plinth's two rounded corners): under the approved pier art's plinth
-- (whose pixels are not touched) the pier's face comes down to Pepper's line as two 18 px ashlar jambs on a base
-- course, a segmental arch (span 94, rise 16) with a ring of voussoirs running up under the plinth, the vault and
-- side walls inside in darker shades of the pier's own stone, and a lit opening at the far end (daylight, a tree
-- line, the far quay). Its crown is y 192: the opening is as tall as the passage. Drawn after the ground (the jambs
-- stand on the paving and hide it behind them; the floor between them is open, so the paving and its slanted
-- shadow run through), in the back look like the pier art above it. It replaces the 6 Nov slot (6 px jambs, a 6 px
-- rise arch, a dark vault) drawn per pixel behind the paving.
local archImg
local function archFront(p, camx)
  local x = (p.vx0 or p.x0) - 1 - camx                            -- (the plinth's first column, 1939)
  if x > 322 or x < -134 then return end
  archImg = archImg or newImg("art/scene/rw_arch.png")
  local sh = lg.getShader()                                       -- a look is on: the pier's (back) grade, not the ground's
  if sh then Look.use("back") end
  lg.setColor(1, 1, 1, 1); lg.draw(archImg, math.floor(x), p.y0 - 1)   -- (its row 0 is y 191)
  if sh then Look.use("ground") end
end
function Sc.passageBack(p, camx)
  if p.arch then return end                                         -- (drawn after the ground: archFront)
  local x0, x1 = math.floor(p.x0 - camx), math.floor(p.x1 - camx)
  if x1 < -2 or x0 > 322 then return end
  lg.setColor(PASS1); lg.rectangle("fill", x0, p.y0, x1 - x0, p.y1 - p.y0)
  lg.setColor(PASS2); lg.rectangle("fill", x0, p.y1 - 14, x1 - x0, 6)
  for y = p.y1 - 15, p.y1 - 8, 2 do lg.rectangle("fill", x0, y, x1 - x0, 1) end
  lg.setColor(1, 1, 1, 1)
end
function Sc.passageFront(p, camx)
  if p.arch then return archFront(p, camx) end                      -- (its shadow is in the painted ground)
  local x0, x1 = math.floor(p.x0 - camx), math.floor(p.x1 - camx)
  if x1 < -2 or x0 > 322 then return end
  lg.setColor(PASS1[1], PASS1[2], PASS1[3], 0.45); lg.rectangle("fill", x0 + 2, p.y1 - 12, x1 - x0 - 4, 14)
  lg.setColor(PASS1[1], PASS1[2], PASS1[3], 0.25)                -- softer at the two mouths
  lg.rectangle("fill", x0 - 3, p.y1 - 12, 5, 14); lg.rectangle("fill", x1 - 2, p.y1 - 12, 5, 14)
  lg.setColor(1, 1, 1, 1)
end

function Sc.label(text, x, y)
  lg.setColor(C.label); local tw = F.width(text, 1); F.print(text, math.floor(x - tw / 2), math.floor(y), 1)
end
-- ===================================================================================================================
-- Art for City Park and Downtown (def.art = "park" / "town"; the images come from tools/make_town_art.py). The
-- levels keep scenery = "greybox" for the game rules (no road, no traffic); only the drawing changes. Every piece is
-- placed from its prop's collision box, so a box and its art stay together.
--   obstacles (things Pepper stands on, bumps into, crawls under): crisp, mid-tone, their own 1 px dark outline,
--             standing on her line (y 184; in a tall level the path line Sc.FOOT, see dy() below)
--   decoration: faded towards the level's back haze (look.lua fade.back), no outline, its base on the back edge (y 174)
--   foreground: dark, only below her lowest line (tops at y 221+), never over her
-- ===================================================================================================================
-- Any path height (tall levels): the art was drawn for the path at y 184. Sc.FOOT is the level's path line (its
-- def.foot, default 184; stage.lua sets it before drawing), and every fixed y below is placed relative to it
-- (dy() = FOOT - 184), so a flat level draws exactly as before and the tall City Park's low road (path y 328)
-- looks exactly as City Park does.
Sc.FOOT = 184
local function dy() return Sc.FOOT - 184 end
local TA = {}
-- an art file faded towards the level's haze for its layer (default: back), k of the way (default: the layer's amount)
local function fadeImg(n, k, layer) return newImg(Sc.fadeData(love.image.newImageData("art/scene/" .. n .. ".png"), k, layer)) end
local function img(n) return newImg("art/scene/" .. n .. ".png") end
local function colQuads(im)
  local w, h = im:getDimensions()
  local q = {}
  for i = 0, w - 1 do q[i] = lg.newQuad(i, 0, 1, h, w, h) end
  return q
end
function Sc.townArt(style)
  local key = style .. "/" .. Look.key                            -- (faded to the level's haze: one set per script)
  if TA[key] then return TA[key] end
  local T = {}
  if style == "park" then
    for _, n in ipairs({ "ground", "bush", "log", "leaves", "leaves_flat", "table", "hedge", "stone", "boat", "cart", "slide", "frame", "hollowlog" }) do T[n] = img("park_" .. n) end
    -- the far tree line (shore), the round trees (mid) and the back decoration, each faded to its own layer's haze
    T.treeline = fadeImg("park_treeline", nil, "shore")
    for _, n in ipairs({ "tree1", "tree2" }) do T[n] = fadeImg("park_" .. n, nil, "mid") end
    -- (5 Nov, plan decision 2b) the tall City Park's mid row: young 6 m trees at the mid scale (138 px), a lime, a
    -- maple and a birch in turn, new art so the row stops repeating the high road's canopies
    if love.filesystem.getInfo("art/scene/cp_mid_lime.png") then
      T.cpmid = {}
      for _, n in ipairs({ "cp_mid_lime", "cp_mid_maple", "cp_mid_birch" }) do T.cpmid[#T.cpmid + 1] = fadeImg(n, nil, "mid") end
      -- (day/07nov-ground, audit CP9 / CP6) the mid row's own lawn and a tuft row over its feet (tools/make_ground_kit.py)
      if love.filesystem.getInfo("art/scene/kit_cp_midlawn.png") then
        T.midLawn, T.midTufts = fadeImg("kit_cp_midlawn", nil, "mid"), fadeImg("kit_cp_tufts", nil, "mid")
        T.shoreLawn = fadeImg("kit_cp_midlawn", nil, "shore")      -- (and the far tree line's, faded as the shore)
      end
    end
    for _, n in ipairs({ "swings", "oak", "willow", "willow_tall", "winch" }) do T[n] = fadeImg("park_" .. n) end
    T.gate = fadeImg("park_gate", 0.28)                           -- (its own amount: dark ironwork, ladder darkest 80)
    T.boat = img("park_boat_front")                               -- front-on (6 Nov: tools/cut_cp_props.py, 58 x 38)
    T.table = img("park_table_front")                             -- front-on (tools/make_table_front.py)
  else
    for _, n in ipairs({ "ground", "crate", "parasol", "table", "stall", "awning80", "awning64", "statue", "pedestal", "tram", "shelter", "kiosk", "shopsign", "rim", "bowl", "bollard", "tub", "tier" }) do T[n] = img("town_" .. n) end
    -- the plaza houses are decoration on the back layer: faded like the rest of it (art/fixes, owner decision 4;
    -- their balconies are separate play ledges, drawn in code)
    for _, n in ipairs({ "door", "sign", "spout", "house1", "house2", "house3" }) do T[n] = fadeImg("town_" .. n) end
    T.crate, T.table = img("town_crate_front"), img("town_table_front")   -- front-on (tools/make_front_view.py)
    -- (art/dt-props-06nov, tools/build_dt_props.py) one apple crate and one parasol canopy per box width, each the
    -- box's width + 2 for its ink, drawn at x0 - 1; a width with no file keeps the old piece
    local function byWidth(n, ws)
      local t = {}
      for _, w in ipairs(ws) do if love.filesystem.getInfo("art/scene/" .. n .. w .. ".png") then t[w] = img(n .. w) end end
      return t
    end
    T.crates = byWidth("town_crate_front", { 28, 32, 36 })
    T.crateFills = {}                                             -- (final review) pears, bread, a cloth: drawn once each
    for _, f in ipairs({ "pears", "bread", "cloth" }) do T.crateFills[f] = byWidth("town_crate_front", { "28_" .. f, "32_" .. f, "36_" .. f }) end
    T.parasols = byWidth("town_parasol", { 40, 48, 64, 96 })
    T.tramshed = { [70] = img("town_tramshed70"), [96] = img("town_tramshed96") }   -- SpriteCook (tools/import_assets_v2.py)
    -- the two far layers sit further back than the back-edge decoration, each faded to its layer's haze (the
    -- script's shore and mid amounts), so the street's obstacles and the climbable houses stand out against them
    -- (r8/levels: art/scene/town_row.png, the row of old town houses across the square with volume, replaces
    -- town_facades.png when it is there: the same layer, a strip that repeats, standing on y 178)
    T.facades = fadeImg(love.filesystem.getInfo("art/scene/town_row.png") and "town_row" or "town_facades", nil, "mid")
    -- (night/06nov-dt, fix round 3) the open squares' floor on the mid layer (tools/build_dt_facades.py)
    T.squareFloor = love.filesystem.getInfo("art/scene/town_square_floor.png") and fadeImg("town_square_floor", nil, "mid") or nil
    T.roofs = fadeImg("town_roofs", nil, "shore")
  end
  T.groundQ = colQuads(T.ground)
  local gw, gd = T.ground:getWidth(), { T.ground:getDimensions() }
  T.bankTop = lg.newQuad(0, 0, gw, style == "park" and 9 or 10, gd[1], gd[2])   -- the lawn / pavement's back edge
  T.bankEarth = lg.newQuad(0, 44, gw, 20, gd[1], gd[2])                        -- earth rows (the pond's far bank)
  T.bankLawn = lg.newQuad(0, 0, gw, 7, gd[1], gd[2])                           -- the lawn only (a park pond's far side)
  TA[key] = T
  return T
end

-- the sky and the drifting clouds (as River Walk and the greybox)
local function skyAndClouds(L, camx, t)
  local v = Sc.vshift
  if v and Look.on then                                            -- a tall art level: the sky rises with the far
    lg.push(); lg.translate(0, v.far)                              -- city (so the warm glow stays behind it) and
    Look.skyTall()                                                 -- goes on above, deeper blue, with high clouds
    local o = camx * 0.05 - t * 3
    Look.use("clouds")
    lg.setColor(1, 1, 1, 1)
    for _, list in ipairs({ L.clouds, L.cloudsHigh }) do
      for _, c in ipairs(list) do
        local x = math.floor((c.x - o) % L.cloudSpan - 120)
        if x < 330 and x + c.w > -10 and c.y + v.far < 240 and c.y + v.far + 60 > 0 then lg.draw(c.img, x, c.y) end
      end
    end
    lg.pop()
    return
  end
  skyGap(); local on = vpush("sky")
  if Look.on then Look.sky() else                                  -- (look.lua: the level's banded, dithered sky)
  for y = 0, 239 do
    local k = math.min(1, y / 170)
    lg.setColor(C.sky1[1] + (C.sky2[1] - C.sky1[1]) * k, C.sky1[2] + (C.sky2[2] - C.sky1[2]) * k, C.sky1[3] + (C.sky2[3] - C.sky1[3]) * k)
    lg.rectangle("fill", 0, y, 320, 1)
  end
  end
  local o = camx * 0.05 - t * 3
  Look.use("clouds")
  lg.setColor(1, 1, 1, 1)
  for _, c in ipairs(L.clouds) do
    local x = math.floor((c.x - o) % L.cloudSpan - 120)
    if x < 330 and x + c.w > -10 then lg.draw(c.img, x, c.y) end
  end
  vpop(on)
end

-- a strip that repeats sideways, scrolled at factor f, bottom at y
Sc.SQUARE_DEPTH = 30                                            -- (fix round 3) the square's floor under the mid row
local function strip(im, camx, f, y)
  local w = im:getWidth()
  local ox = math.floor(camx * f) % w
  for x = -ox, 320, w do lg.draw(im, x, y - im:getHeight()) end
end

-- the water's surface areas: runs of columns with their top (the world's water boxes are per map cell)
local function pools(w)
  if w.pools then return w.pools end
  local top = {}
  for _, r in ipairs(w.water) do for x = r.x0, r.x1 - 1 do top[x] = math.min(top[x] or 999, r.y0) end end
  local P, x = {}, 0
  while x < w.width do
    if top[x] then
      local x1 = x
      while top[x1 + 1] == top[x] do x1 = x1 + 1 end
      P[#P + 1] = { x0 = x, x1 = x1 + 1, y0 = top[x] }
      x = x1 + 1
    else x = x + 1 end
  end
  w.pools = P
  return P
end

function Sc.buildArt(levelW, style)
  local L = Sc.build(levelW)
  L.style = style
  local A, r, x = Sc.art(), rng(13), 30                            -- high clouds, for a tall level's sky (y < 0)
  L.cloudsHigh = {}
  while x < L.cloudSpan - 60 do
    local im = A.clouds[1 + (#L.cloudsHigh * 3) % #A.clouds]
    L.cloudsHigh[#L.cloudsHigh + 1] = { x = x, y = math.floor(r(-104, -40)), img = im, w = im:getWidth() }
    x = x + im:getWidth() + math.floor(r(120, 260))
  end
  if style == "park" then                                         -- near trees (parallax 0.5), deterministic
    local r = rng(47); L.trees = {}
    local x = -30
    while x < 320 + (levelW - 320) * 0.5 + 64 do
      L.trees[#L.trees + 1] = { x = x, i = 1 + #L.trees % 2 }
      x = x + 90 + math.floor(r(10, 90))
    end
  end
  return L
end

-- the big oak's silhouette on the far tree line, from screen 5 on (plan decision 8 f, the beat sheet's ask): the
-- finale's landmark stands up over the tree line, one flat dark shape in the tree line's own colour, a shade darker, no
-- outline (decoration, far scenery). Drawn from code once: a trunk with a flared foot and a broad, scalloped crown. It
-- moves with the tree line (0.25), so it comes in at the right edge in the last third of screen 5 and stands on the
-- left of the last screen, over the big oak itself. A tall level with a BIG OAK only.
local function hasProp(def, name) for _, q in ipairs(def.props) do if q.name == name then return true end end end
local function farOakImg(T)
  if T.farOak then return T.farOak end
  local W, H = 124, 72
  local src = love.image.newImageData("art/scene/park_treeline.png")
  local r, g, b, n = 0, 0, 0, 0
  src:mapPixel(function(_, _, pr, pg, pb, pa) if pa > 0.5 then r, g, b, n = r + pr, g + pg, b + pb, n + 1 end return pr, pg, pb, pa end)
  local c = Sc.fadeC({ r / n, g / n, b / n }, nil, "shore")          -- the tree line's average colour, faded as it is
  local main = { c[1] * 0.94, c[2] * 0.94, c[3] * 0.94 }
  local low = { c[1] * 0.89, c[2] * 0.89, c[3] * 0.89 }              -- the crown's underside and the trunk
  local d = love.image.newImageData(W, H)
  local rr = rng(2880)
  local function put(x, y, col) if x >= 0 and x < W and y >= 0 and y < H then d:setPixel(x, y, col[1], col[2], col[3], 1) end end
  local cx, foot = W / 2, H - 1
  for y = 36, foot do                                               -- the trunk, flaring at its foot
    local e = foot - y
    local half = 4 + (e < 8 and (8 - e) * 0.6 or 0) + (y < 50 and (50 - y) * 0.12 or 0)
    for x = math.floor(cx - half), math.ceil(cx + half) do put(x, y, low) end
  end
  local blobs = {}                                                  -- the crown: many small lobes in a broad dome, so its edge is leafy
  for k = 1, 34 do
    local a = rr(0, math.pi * 2)
    local rad = math.sqrt(rr(0, 1)) * 0.78
    local bx, by = cx + math.cos(a) * rad * 56, 30 + math.sin(a) * rad * 20
    blobs[#blobs + 1] = { bx, by, rr(7, 11) }
  end
  for _, bl in ipairs(blobs) do
    for y = math.floor(bl[2] - bl[3]), math.ceil(bl[2] + bl[3]) do
      for x = math.floor(bl[1] - bl[3]), math.ceil(bl[1] + bl[3]) do
        local dx, dy = x - bl[1], y - bl[2]
        if dx * dx + dy * dy <= bl[3] * bl[3] then put(x, y, (dy > bl[3] * 0.25) and low or main) end
      end
    end
  end
  T.farOak = newImg(d)
  return T.farOak
end

-- (art/cp-audit-06nov) a park pond's banks, by rule (0 credits). The audit: "the pond reads as a dark pit": a 30 px
-- band of the earth strata (the ground art's dark rows) over a strip of water, the path ending in a straight cut.
-- Now the water comes up to a waterline 16 px over its box's top (POND_RISE: the far part of its surface, seen from
-- the path, the water art's own lighter rows 4-19), under a short bank seen across the pond: the lawn, its lit lip,
-- a sloping face of sunlit earth going damp and wet down to the water, a row of rounded granite stones along its
-- foot. At each end the bank curves round to the path (BANK_R px), its wet foot following the shore, and under the
-- surface the basin's side slopes in (1 px every 3 rows) as submerged earth. Flat colours: the ground art's earth
-- ramp, the lawn, the stepping stones' granite; no outline (decoration). Nothing Pepper uses moves: the water box,
-- the path and the stones' boxes are as they were (she still splashes at the box's top, 2 px under the old line).
Sc.POND_RISE, Sc.BANK_R = 16, 16
Sc.WINCH_DX = 8                                                   -- (the winch keeper: see WINCH)
local BANK = { lip = hex("b5ad55"), lawn = hex("9e983f"), dry = hex("d09d68"), damp = hex("bd8354"), wet = hex("8a5a3a"),
  foot = hex("5e4127"), st1 = hex("c9c2b4"), st15 = hex("b3ac9f"), st2 = hex("a39b8e"), st3 = hex("7a736a"), sub = hex("3d5866"),
  subEdge = hex("4f6f7a"), rip = hex("d3f2fd"), lit = hex("ddae79") }
local STONE_W, STONE_H = { 10, 7, 12, 8, 9, 11 }, { 4, 3, 5, 4, 3, 4 }
-- the far bank's colour at row k (0 at the lawn's lip) of n rows, world column wx; nil: leave it (a stone)
local function bankRow(k, n, wx)
  if k == 0 then return BANK.lip end
  if k <= 2 then return BANK.lawn end
  if k == 3 then return (wx % 7 < 3) and BANK.lawn or BANK.dry end   -- grass hanging over the lip, a tuft every 7 px
  if k == 4 then return (wx % 7 == 1) and BANK.lawn or BANK.dry end
  if k >= n - 1 then return BANK.foot end
  if k >= n - 3 then return BANK.wet end
  if k >= math.floor(n / 2) + 1 then return BANK.damp end
  return BANK.dry
end
-- the stones along the bank's foot: one every 29 px of the world, sizes from a fixed list; their bottom row on the
-- foot row (the waterline). Returns the colour of world column wx at row k from the foot (0 = foot row), or nil
local function bankStone(wx, k)
  local i = math.floor(wx / 29)
  local sw, sh = STONE_W[1 + i % #STONE_W], STONE_H[1 + (i * 5) % #STONE_H]
  local c0 = i * 29 + (i * 13) % 11
  local u = wx - c0
  if u < 0 or u >= sw or k >= sh then return nil end
  if (u == 0 or u == sw - 1) and (k == sh - 1 or k == 0) then return nil end   -- rounded corners
  if k == sh - 1 then return BANK.st1 end                         -- its lit top
  if k == sh - 2 and k > 0 and u < sw - 1 then return BANK.st15 end   -- (round 1) the mid-light under it: the stepping stones' 4 shades
  if k == 0 or u == sw - 1 then return BANK.st3 end               -- the shaded underside and right side
  return BANK.st2
end
function Sc.drawPondBank(p, camx, d, wbottom)
  local x0, x1 = math.floor(p.x0 - camx), math.floor(p.x1 - camx)
  local yb, wt = 179 + d, p.y0 - Sc.POND_RISE                    -- the lawn's lip; the waterline
  local n = wt - yb
  local R = Sc.BANK_R
  local function px(x, y, c) lg.setColor(c); lg.rectangle("fill", x, y, 1, 1) end
  for x = math.max(x0, -1), math.min(x1 - 1, 320) do
    local wx = x + math.floor(camx)
    local i = math.min(x - x0, x1 - 1 - x)                        -- columns from the nearer end of the pond
    local foot = wt                                               -- where the bank meets the water in this column
    if i < R then
      local u = 1 - (i + 0.5) / R
      foot = wt + math.floor(Sc.POND_RISE * (1 - math.sqrt(math.max(0, 1 - u * u))) + 0.5)
      -- (night 6 Nov, cp fix round 1: the shore's last column no longer drops straight to the box's top, a 1 px
      -- vertical cut at the lawn's corner; the curve runs on to the end)
    end
    for y = yb, foot - 1 do
      local k = y - yb
      local kk = (foot > wt) and math.min(k, n - 4) or k            -- (at the ends the face runs on, damp, to the shore)
      local c = bankRow(kk, n, wx)
      if foot > wt and y >= foot - 3 then c = (y == foot - 1) and BANK.foot or (y == foot - 2) and BANK.wet or BANK.lit end
      if i < 4 and y < foot - 3 and y > yb then c = BANK.lawn end   -- (round 1) the lawn's shoulder runs on round the corner
      if foot == wt then c = bankStone(wx, foot - 1 - y) or c end
      px(x, y, c)
    end
    if i < R and foot < p.y0 then                                 -- the water's edge along the curved shore: a ripple
      if (wx + math.floor(foot)) % 3 ~= 0 then px(x, foot, BANK.rip) end
    elseif i >= R and (wx % 9 < 5) then px(x, wt, BANK.rip) end   -- (and along the far bank, in dashes)
    local sw = math.floor((wbottom - p.y0) / 3) + 1               -- the basin's sloping side under the surface
    if i < sw then
      for y = p.y0 + 3 * i, wbottom - 1 do px(x, y, (y == p.y0 + 3 * i) and BANK.subEdge or BANK.sub) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- (night 6 Nov, cp track; the design target art/gen/concepts/cp_pond_concept_a.png) the pond kit, built once by
-- tools/build_cp_pond.py and stamped here at whole pixels: reeds and bulrushes at both ends of a park pond, rounded
-- stones where its curved shore meets the water, a few small reeds on the far bank, lily pads on the surface. All
-- decoration on Pepper's line, drawn with the water (before the stepping stones, the duck boat and Pepper), at fixed
-- spots per pond in world x so nothing moves but the water. Without the files: nothing.
local PK
local function pondKit()
  if PK == nil then
    PK = false
    local f = { reeds = "cp_reeds", lily = "cp_lily", stones = "cp_bankstones" }
    local K = {}
    for k, n in pairs(f) do
      if not love.filesystem.getInfo("art/scene/" .. n .. ".png") then return false end
      K[k] = newImg("art/scene/" .. n .. ".png")
    end
    local function cells(im, w) local q = {}; for i = 0, im:getWidth() / w - 1 do q[i + 1] = lg.newQuad(i * w, 0, w, im:getHeight(), im:getDimensions()) end; return q end
    K.reedsQ, K.lilyQ, K.stonesQ = cells(K.reeds, 16), cells(K.lily, 10), cells(K.stones, 12)
    PK = K
  end
  return PK
end
-- the shore's row in column i from the nearer end (as Sc.drawPondBank draws it)
local function shoreAt(i, wt, y0)
  local R = Sc.BANK_R
  if i >= R then return wt end
  if i <= 0 then return y0 end
  local u = 1 - (i + 0.5) / R
  return wt + math.floor(Sc.POND_RISE * (1 - math.sqrt(math.max(0, 1 - u * u))) + 0.5)
end
function Sc.drawPondKit(p, camx, props)
  local K = pondKit()
  if not K then return end
  local ox = math.floor(camx)
  local wt, w = p.y0 - Sc.POND_RISE, p.x1 - p.x0
  local function clear(x0, x1)                                     -- not over a stepping stone's box
    for _, q in ipairs(props or {}) do if q.name == "STONE" and q.x0 < x1 + 4 and q.x1 > x0 - 4 then return false end end
    return true
  end
  local function at(im, q, x, y, flip)
    lg.setColor(1, 1, 1, 1)
    if flip then lg.draw(im, q, x - ox + 16, y, 0, -1, 1) else lg.draw(im, q, x - ox, y) end
  end
  -- lily pads: one every 52 px of the pond from 14 px in, on rows 3 to 9 under the waterline, off the stones
  local k = 0
  for x = p.x0 + 14, p.x1 - 24, 52 do
    k = k + 1
    local lx = x + (k * 17) % 13
    if clear(lx, lx + 10) then lg.setColor(1, 1, 1, 1); lg.draw(K.lily, K.lilyQ[1 + k % 3], lx - ox, wt + 3 + (k * 5) % 7) end
  end
  -- small reeds on the far bank, at about a third and two thirds, standing on the waterline
  for _, f in ipairs({ 0.31, 0.68 }) do
    local rx = p.x0 + math.floor(w * f)
    if clear(rx, rx + 16) then at(K.reeds, K.reedsQ[2], rx, wt - 33, rx % 2 == 0) end
  end
  -- both ends: stones on the curved shore, then a reed clump in the corner (the right end mirrored)
  for _, e in ipairs({ { p.x0, 1 }, { p.x1, -1 } }) do
    local sx = e[2] > 0 and e[1] + 9 or e[1] - 21                   -- (a stone cell is 12 px; its middle 6 px in)
    at(K.stones, K.stonesQ[e[2] > 0 and 1 or 2], sx, shoreAt(math.abs(sx + 6 - e[1]), wt, p.y0) - 6)
    local rx = e[2] > 0 and e[1] - 1 or e[1] - 15
    at(K.reeds, K.reedsQ[2], rx + 7 * e[2], shoreAt(11, wt, p.y0) - 33, e[2] > 0)   -- (the small clump behind, turned)
    at(K.reeds, K.reedsQ[1], rx, shoreAt(5, wt, p.y0) - 33, e[2] < 0)
  end
  lg.setColor(1, 1, 1, 1)
end

-- layers 1 to 5 of an art level, and the water of its pond or fountain basin with the far bank behind it
function Sc.drawFarArt(L, camx, t, w, def)
  local T, A = Sc.townArt(L.style), Sc.art()
  skyAndClouds(L, camx, t)
  local on = vpush("far")
  Look.use("city")
  lg.setColor(1, 1, 1, 1)                                         -- 3 far city: River Walk's skyline, moved at
  local sx = -math.floor(math.min(128, camx * 128 / math.max(1, w.width - 320)))   -- most 128 px (one City Hall)
  lg.draw(A.skyline, sx, 150 - A.skyline:getHeight()); lg.draw(A.skyline, sx + A.skyline:getWidth(), 150 - A.skyline:getHeight())
  if L.style == "park" then
    Look.use("shore")
    if def and def.foot and T.shoreLawn then strip(T.shoreLawn, camx, 0.25, 175 + T.shoreLawn:getHeight()) end   -- (day/07nov-
    -- ground, audit CP9: up in the trees, the rows behind ended straight over the sky) the tree line's own lawn
    strip(T.treeline, camx, 0.25, 177)                            -- 4 the far tree line
    if def and def.foot and hasProp(def, "BIG OAK") then          -- the big oak's silhouette on it (a tall park's finale)
      local oi = farOakImg(T)
      local x = math.floor((w.width - 320) * 0.25 + 100) - math.floor(camx * 0.25) - oi:getWidth() / 2
      if x < 330 and x + oi:getWidth() > -10 then lg.setColor(1, 1, 1, 1); lg.draw(oi, x, 177 - oi:getHeight()) end
    end
    vpop(on); on = vpush("mid")
    Look.use("mid")
    local ox = math.floor(camx * 0.5)                             -- 5 near trees (faded)
    local tall = def and def.foot and T.midLawn
    if tall then strip(T.midLawn, camx, 0.5, 176 + T.midLawn:getHeight()) end   -- (day/07nov-ground) its own lawn
    for k, tr in ipairs(L.trees) do
      local im = (def and def.foot and T.cpmid) and T.cpmid[1 + (k - 1) % #T.cpmid] or T["tree" .. tr.i]
      local x = tr.x - ox
      if x < 330 and x + im:getWidth() > -10 then lg.draw(im, x, 180 - im:getHeight()) end
    end
    if tall then strip(T.midTufts, camx, 0.5, 181) end            -- tufts over the row's feet
  else
    Look.use("shore")
    strip(T.roofs, camx, 0.25, 160)                               -- 4 far roofs and spires
    if def then (package.loaded.arthooks or require("arthooks")).drawFarSpire(def, camx, w.width) end   -- (art/placement:
    -- the tall Downtown's landmark, Riddarholmen's spire, behind the old town row on this layer)
    vpop(on); on = vpush("mid")
    Look.use("mid")
    -- (night/06nov-dt, fix round 3, review round 2: "the mid row's feet land on the pavement's far edge") in the tall
    -- Downtown the row stands across an open square: its foot 30 px up, the square's floor (a far kerb, setts,
    -- bollards at 23 px/m) under it at the same scroll, down to the pavement's far edge, so the row never touches
    -- the play floor
    if def and def.foot and T.squareFloor then
      strip(T.facades, camx, 0.5, 178 - Sc.SQUARE_DEPTH)
      strip(T.squareFloor, camx, 0.5, 178 - Sc.SQUARE_DEPTH + T.squareFloor:getHeight() - 21)
    else
    strip(T.facades, camx, 0.5, 178)                              -- 5 old town facades (faded)
    end
  end
  vpop(on); on = vpush("world")                                   -- (the ponds are in the world)
  Sc.pondPools, Sc.pondT = pools(w), t                             -- (a stepping stone stands in them: drawPropArt)
  -- the pond / basin: its far bank, then the water (rows of the river art, each moving on its own)
  Look.use("ground")
  local gw = T.ground:getWidth()
  for _, p in ipairs(pools(w)) do
    local x0, x1 = math.floor(p.x0 - camx), math.floor(p.x1 - camx)
    if x1 > -2 and x0 < 322 then
      lg.setScissor(math.max(0, x0), 0, math.max(0, math.min(320, x1) - math.max(0, x0)), 240)   -- (screen space)
      local ox = math.floor(camx) % gw
      local wtop = p.y0                                           -- (the water's top row as drawn)
      if L.style == "park" then                                   -- the lawn goes on behind, then the bank (art/cp-audit-06nov:
        for x = -ox - gw, 320, gw do lg.draw(T.ground, T.bankLawn, x, 172 + dy()) end   -- was the earth strata: a pit)
        wtop = p.y0 - Sc.POND_RISE
      else                                                        -- the pavement's back, then the basin's granite
        local d = dy()
        for x = -ox - gw, 320, gw do lg.draw(T.ground, T.bankTop, x, 172 + d) end
        -- (art/dt-audit-06nov) the far quay's face down to the water, in the near quay wall's greys (town_ground.png):
        -- a lit coping row, one course of blocks in running bond (head joints every 24 px, anchored in the world), a
        -- wet band, then the waterline. It was a flat light slab, so the gap read as a flat blue block.
        local h = p.y0 - 182 - d
        local wx0 = math.floor(p.x0)
        lg.setColor(94 / 255, 87 / 255, 81 / 255); lg.rectangle("fill", x0, 182 + d, x1 - x0, h)
        lg.setColor(141 / 255, 136 / 255, 129 / 255); lg.rectangle("fill", x0, 182 + d, x1 - x0, 1)
        lg.setColor(108 / 255, 103 / 255, 98 / 255); lg.rectangle("fill", x0, 183 + d, x1 - x0, 1)
        lg.setColor(47 / 255, 43 / 255, 47 / 255); lg.rectangle("fill", x0, 184 + d, x1 - x0, 1)
        for x = wx0 - wx0 % 24 + 12, math.floor(p.x1), 24 do
          local sx = math.floor(x - camx)
          if sx >= x0 and sx < x1 then lg.rectangle("fill", sx, 185 + d, 1, h - 5) end
        end
        lg.setColor(72 / 255, 66 / 255, 64 / 255); lg.rectangle("fill", x0, p.y0 - 3, x1 - x0, 2)   -- wet stone
      end
      if L.style ~= "park" then lg.setColor(0.18, 0.2, 0.22); lg.rectangle("fill", x0, p.y0 - 1, x1 - x0, 1) end   -- the water's edge
      Look.use("water")
      local tint = L.style == "park" and { 0.80, 0.93, 0.86 } or { 0.92, 1, 1 }
      local ww, wh = A.water:getDimensions()
      if L.style == "park" then
      for y = wtop, w.height - 1 do                               -- (down to the bottom of the world)
        local row = math.max(0, math.min(wh - 1, 20 + (y - p.y0)))
        local depth = math.max(0, y - p.y0) / 32
        local o = math.floor(camx + math.sin(t * 1.3 + y * 0.55) * (0.6 + depth) + t * (1 + 2 * depth) + 0.5) % ww
        lg.setColor(tint)
        lg.draw(A.water, A.waterQ[row], -o, y); lg.draw(A.water, A.waterQ[row], ww - o, y)
      end
      Look.use("ground"); Sc.drawPondBank(p, camx, dy(), w.height); Sc.drawPondKit(p, camx, def and def.props)
      else                                                        -- (night/06nov-dt, review round 1: "a flat saturated
        -- slab to the screen bottom") Downtown's canal front-on, as the River Walk harbour: a surface band (a lit edge,
        -- the quay's dark reflection, two rows of drifting ripples on the surface blue), under it the deep water in two
        -- darker steps, no streaks
        local yb, wdt = w.height, x1 - x0
        lg.setColor(0.31, 0.47, 0.61); lg.rectangle("fill", x0, p.y0, wdt, 8)                 -- the surface band
        lg.setColor(0.23, 0.37, 0.51); lg.rectangle("fill", x0, p.y0 + 8, wdt, 16)            -- deep
        lg.setColor(0.19, 0.31, 0.44); lg.rectangle("fill", x0, p.y0 + 24, wdt, yb - p.y0 - 24)   -- deeper
        lg.setColor(0.24, 0.34, 0.44); lg.rectangle("fill", x0, p.y0 + 1, wdt, 2)             -- the quay's reflection
        lg.setColor(0.27, 0.42, 0.56); lg.rectangle("fill", x0, p.y0 + 7, wdt, 1)             -- the band's foot
        local wo = math.floor(t * 5) % 24                                                      -- ripples, drifting
        for x = math.floor(p.x0) - math.floor(p.x0) % 24 - 24, math.floor(p.x1), 24 do
          local sx = math.floor(x + wo - camx)
          lg.setColor(0.55, 0.71, 0.82); lg.rectangle("fill", sx, p.y0 + 4, 7, 1); lg.rectangle("fill", sx + 13, p.y0 + 6, 4, 1)
          lg.setColor(0.25, 0.40, 0.54); lg.rectangle("fill", sx + 4, p.y0 + 5, 6, 1)
        end
        lg.setColor(0.70, 0.84, 0.93); lg.rectangle("fill", x0, p.y0, wdt, 1)                -- the lit top edge
      end
      if L.style == "never" then                                  -- (art/dt-audit-06nov) the waterline: the quay's
        lg.setColor(0.13, 0.25, 0.45)                             -- dark reflection under the edge, then broken
        lg.rectangle("fill", x0, p.y0, x1 - x0, 2)               -- light ripples drifting with the water
        lg.setColor(0.62, 0.80, 0.93)
        local wo = math.floor(t * 4) % 16
        for x = math.floor(p.x0) - math.floor(p.x0) % 16 - 16, math.floor(p.x1), 16 do
          local sx = math.floor(x + wo - camx)
          lg.rectangle("fill", sx, p.y0 + 3, 6, 1); lg.rectangle("fill", sx + 9, p.y0 + 5, 3, 1)
        end
      end
      lg.setScissor()
      Look.use("ground")
    end
  end
  vpop(on)
  Look.off()
  lg.setColor(1, 1, 1, 1)
end

local Q = { j = { 47, 43, 47 }, s = { 60, 56, 56 }, a = { 72, 66, 64 }, l = { 94, 87, 81 },
            k1 = { 161, 158, 151 }, k2 = { 141, 136, 129 }, k3 = { 108, 103, 98 } }
local function qc(c) lg.setColor(c[1] / 255, c[2] / 255, c[3] / 255) end
-- the ground of an art level, painted once: the path / pavement strip on every walkable top (its back edge 12 px
-- above Pepper's line), dark edges on the cut faces (the pond's banks); Downtown's river stairs as stone steps.
function Sc.paintGroundArt(w, style, foot)
  foot = foot or 184                                              -- (the path line: a tall level's def.foot)
  Jn.reset()                                                      -- (day/07nov-ground: the joins check's marks)
  local T = Sc.townArt(style)
  local gw, gh = T.ground:getDimensions()
  return chunked(w, function(xa, xb)                              -- (painted once per chunk: Sc.CHUNK)
  local cover = {}
  for x = 0, w.width - 1 do
    local sl = w:slopeAt(x)
    local merged = columnRuns(w, x, "first")
    cover[x] = merged
    for _, m in ipairs((x >= xa and x < xb) and merged or {}) do      -- (drawn in the chunk's columns only)
      local top = m[1]
      if top < foot then top = foot end                           -- the slide tower: the path goes on behind it
      local stair = sl and style == "town"
      if stair then top = foot + math.floor((top - foot) / 4) * 4 end   -- the river stairs: 4 px steps
      lg.setColor(1, 1, 1, 1)
      if stair and foot > 184 then                                -- (night/06nov-dt, audit item 5: "the kerb ends in a
        -- diagonal stepped block") the tall Downtown's river stairs as granite steps: no cobbles or kerb sheared down
        -- the slope, each 4 px step a block of the kerb's granite down to the world's bottom, its courses on the steps
        local sl0 = w:slopeAt(x - 1) and (function() for _, mm in ipairs(columnRuns(w, x - 1, "first")) do return mm[1] end end)()
        qc(Q.k3); lg.rectangle("fill", x, top, 1, w.height - top)
        for yy = top + 4, w.height - 1, 4 do qc(Q.a); lg.rectangle("fill", x, yy, 1, 1) end
        qc(Q.k1); lg.rectangle("fill", x, top, 1, 1); qc(Q.k2); lg.rectangle("fill", x, top + 1, 1, 2)
        local prev = sl0 and foot + math.floor((sl0 - foot) / 4) * 4
        if prev and prev ~= top then qc(Q.j); lg.rectangle("fill", x, math.min(prev, top), 1, math.abs(prev - top) + 1) end
        lg.setColor(1, 1, 1, 1)
      else
      clip(x, 0, 1, m[2])
      lg.draw(T.ground, T.groundQ[x % gw], x, top - 12)
      if top - 12 + gh < w.height then lg.draw(T.ground, T.groundQ[x % gw], x, top - 12 + gh) end
      clip()
      end
      if stair and foot <= 184 then                               -- each step: a light granite nosing
        lg.setColor(0.78, 0.75, 0.70); lg.rectangle("fill", x, top, 1, 1)
        lg.setColor(0.36, 0.34, 0.33); lg.rectangle("fill", x, top + 3, 1, 1)
      end
    end
  end
  local function solid(x, y)
    for _, m in ipairs(cover[x] or {}) do if y >= m[1] and y < m[2] then return true end end
    return false
  end
  local wetCol = {}                                               -- (art/cp-audit-06nov) a park pond's sides: no dark
  if style == "park" then                                         -- cut, its bank curves round in front (Sc.drawPondBank)
    for _, r in ipairs(w.water) do wetCol[r.x0 - 1] = true; wetCol[r.x1] = true end
  end
  lg.setColor(0.16, 0.13, 0.11)                                   -- cut faces (the banks): a dark edge
  for x = xa, xb - 1 do                                           -- (the chunk's columns)
    if not w:slopeAt(x) and not wetCol[x] then
      for _, m in ipairs(cover[x]) do
        for y = math.max(m[1], foot), m[2] - 1 do
          if (x > 0 and not solid(x - 1, y) and not w:slopeAt(x - 1)) or (x < w.width - 1 and not solid(x + 1, y) and not w:slopeAt(x + 1)) then
            lg.rectangle("fill", x, y, 1, 1)
          end
        end
      end
    end
  end
  if style == "town" then Sc.quayEnds(w, xa, xb, foot, solid) end
  if style == "park" then Sc.nearBanks(w, xa, xb, foot, T) end
  end)
end

-- (day/07nov-ground, audit CP2-CP5: the path, its verge and every earth band ended in a straight vertical cut at
-- each end of a pond) the near bank, a transition stamped by rule at both ends of every pond, into the pond's first
-- NEAR_R columns (drawn with the ground, so in front of the water): the ground's own column (path, verge, strata)
-- with its silhouette going down into the water: a rounded shoulder (6 px), then NEAR_STEP px down per column (a
-- slope tile of 2 px per step: the strata step back 1 px every 2 rows, the bank slopes away) to the world's bottom, a grass lip along its top with a tuft
-- every other column down the path and its verge, a wet foot down the earth, a ripple every 4 px against it.
Sc.NEAR_R, Sc.NEAR_STEP = 40, 2
function Sc.nearBanks(w, xa, xb, foot, T)
  local gw = T.ground:getWidth()
  local top0 = foot - 12 + 9                                       -- the path's top row (the tile's row 9)
  local H = w.height - top0
  local R = Sc.NEAR_R
  local K, S = 6, Sc.NEAR_STEP                                     -- a rounded shoulder, then S px down per column
  local function drop(i)
    if i < K then return math.floor(S * i * i / (2 * K) + 0.5) end
    return S * (i - math.floor(K / 2))
  end
  for _, p in ipairs(pools(w)) do
    local wt = p.y0 - Sc.POND_RISE
    Jn.mark(p.x0, "path>pond"); Jn.mark(p.x1, "pond>path")
    for _, e in ipairs({ { p.x0, 1 }, { p.x1 - 1, -1 } }) do
      for i = 0, R - 1 do
        local x = e[1] + e[2] * i
        local d, dp = drop(i), (i > 0) and drop(i - 1) or 0
        local ys = top0 + d
        if x >= xa and x < xb and x >= p.x0 and x < p.x1 and ys < w.height then
          clip(x, ys, 1, w.height - ys)
          lg.setColor(1, 1, 1, 1); lg.draw(T.ground, T.groundQ[x % gw], x, foot - 12)
          clip()
          if d > dp + 1 then                                         -- the step's side face, a shade darker
            lg.setColor(0.10, 0.06, 0.04, 0.28); lg.rectangle("fill", x, top0 + dp + 1, 1, math.max(0, ys - (top0 + dp + 1)))
          end
          if ys < top0 + 22 then                                     -- the path and its verge: a grass lip
            lg.setColor(0.10, 0.06, 0.04, 0.22); lg.rectangle("fill", x, ys + 1, 1, math.min(3, w.height - ys - 1))   -- the face under it
            lg.setColor(BANK.lip); lg.rectangle("fill", x, ys, 1, 1)
            if i % 2 == 0 and ys > top0 then lg.setColor(BANK.lawn); lg.rectangle("fill", x, ys - 1, 1, 1) end   -- a tuft
          else                                                       -- the earth meets the water: a wet foot
            lg.setColor(BANK.foot); lg.rectangle("fill", x, ys, 1, 1)
            lg.setColor(0.08, 0.10, 0.18, 0.35); lg.rectangle("fill", x, ys + 1, 1, math.min(2, w.height - ys - 1))
          end
          if ys - 1 >= wt and i % 4 == 0 then lg.setColor(BANK.rip[1], BANK.rip[2], BANK.rip[3], 0.6); lg.rectangle("fill", x + e[2], ys - 1, 1, 1) end   -- a ripple
        end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- (art/dt-audit-06nov) the audit: "the cobbles end in a hard vertical cut at every canal gap". Where the street (its
-- top on the path line) ends at water, the street gets a granite end: the kerb turns the corner (a 3 px kerb strip
-- up the end of the cobbles, lit on its top, the front kerb's corner stone), and the quay wall under it ends in
-- quoins (alternate long and short corner blocks, 10 and 6 px, on the wall's 12 px courses), its arris dark. The
-- colours are town_ground.png's kerb and quay greys (the Look's ground grade does the rest).
function Sc.quayEnds(w, xa, xb, foot, solid)
  local KERB, QUAY = foot + 15, foot + 20                          -- the tile's rows 27 and 32 (top at foot - 12)
  local function wet(x)
    for _, r in ipairs(w.water or {}) do if x >= r.x0 and x < r.x1 and r.y0 <= foot + 16 and r.y1 > foot then return true end end
    return false
  end
  for x = math.max(1, xa), math.min(w.width - 2, xb - 1) do
    local side = 0
    if solid(x, foot) and not solid(x + 1, foot) and wet(x + 1) then side = 1        -- the street ends on its right
    elseif solid(x, foot) and not solid(x - 1, foot) and wet(x - 1) then side = -1 end
    if side ~= 0 then
      local function col(k, c, y0, h) qc(c); lg.rectangle("fill", x - side * k, y0, 1, h) end   -- k columns in from the end
      -- the kerb up the end of the cobbles (rows foot - 2 .. KERB - 1): the arris, two lit columns, a mid one, the
      -- joint against the cobbles; its top row lit, its foot the front kerb's corner
      local kh = KERB - foot + 2
      col(0, Q.j, foot - 2, kh + 5); col(1, Q.k1, foot - 2, kh); col(2, Q.k1, foot - 2, kh); col(3, Q.k2, foot - 2, kh)
      col(4, Q.j, foot - 1, kh - 1)
      qc(Q.k1); lg.rectangle("fill", side > 0 and x - 4 or x, foot - 2, 5, 1)
      -- the quay wall's end: dressed quoins on its 12 px courses, a shade lighter than the wall
      local c = 0
      for top = QUAY, w.height - 1, 12 do
        local qw = (c % 2 == 0) and 10 or 6
        local x0 = side > 0 and x - qw + 1 or x
        local h = math.min(12, w.height - top)
        qc(Q.k3); lg.rectangle("fill", x0, top + 1, qw, h - 1)
        qc(Q.k2); lg.rectangle("fill", x0, top + 1, qw, 1)
        if h >= 12 then qc(Q.a); lg.rectangle("fill", x0, top + 11, qw, 1) end
        qc(Q.k2); lg.rectangle("fill", x0 + 1, top + 1, 1, h - 1)                        -- its lit left edge
        qc(Q.j); lg.rectangle("fill", side > 0 and x0 or x0 + qw - 1, top + 1, 1, h - 1)   -- its inner head joint
        qc(Q.j); lg.rectangle("fill", x0, top, qw, 1)                                       -- bed joint
        c = c + 1
      end
      qc(Q.j); lg.rectangle("fill", x, QUAY, 1, w.height - QUAY)                             -- the arris against the water
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- an oak branch over its one-way box: 6 px thick by the trunk, 4 at the tip, its top row the ledge; between the
-- box and the trunk it dips down (it is no ledge there). Autumn leaves hang under the tip.
local BARK = { hex("7a5536"), hex("a3774c"), hex("523823") }
local INK = { 29 / 255, 24 / 255, 22 / 255 }
local LEAF = { hex("d9822b"), hex("b8551f"), hex("e2a53a") }
-- (6 Nov, cp_boughs_06nov) the City Park climbing parts as art: one SpriteCook parts sheet of an old oak, cut 1:1 on
-- its own grid (tools/cut_cp_boughs.py) and made into parts by rule (tools/build_cp_boughs.py; sizes in
-- cp_boughs_data.lua). The limbs are whole columns of a straight bark strip laid along the SAME boxes: each column's
-- top is the ledge's top row, its rows taken from the strip's top and bottom (8 at the trunk, one fewer every 16 px
-- out, 4 at the tip), the 1 px ink round the play part, a rounded tip at a free end. Where a limb lies on its trunk
-- it takes the trunk's own fade and no ink, so it grows out of the tree instead of lying in front of it. Trunks are
-- the oak trunk art (33 px, true scale), faded as the back. Each drawing function keeps its code as the fallback.
local CPB                                                          -- nil: not looked for; false: a file is missing
local CPB_TI                                                       -- the tier being drawn (its trunks and ledges)
local function cpb()
  if CPB == nil then
    CPB = false
    local ok, D = pcall(require, "cp_boughs_data")
    if not ok then return false end
    local I = { D = D, fd = {} }
    for _, n in ipairs({ "limb", "limbx", "low", "nest", "stump", "trunk" }) do
      if not love.filesystem.getInfo("art/scene/cp_bough_" .. n .. ".png") then return false end
      I[n] = newImg("art/scene/cp_bough_" .. n .. ".png")
    end
    CPB = I
  end
  return CPB
end
local function cpbFaded(A, n, k)                                   -- a part faded k of the way to the back's haze
  local key = n .. "/" .. tostring(k) .. "/" .. Look.key
  if not A.fd[key] then A.fd[key] = newImg(Sc.fadeData(love.image.newImageData("art/scene/cp_bough_" .. n .. ".png"), k)) end
  return A.fd[key]
end
local CPBQ = {}                                                    -- quads, by image and rectangle
local function cpbQuad(im, x, y, w, h)
  local k = tostring(im) .. x .. "," .. y .. "," .. w .. "," .. h
  local q = CPBQ[k]
  if not q then q = lg.newQuad(x, y, w, h, im:getDimensions()); CPBQ[k] = q end
  return q
end
-- the trunk t as drawn: its world x span and the fade of its bark (an art tree's own trunk and fade, else the oak
-- trunk art at the back's fade); fake: no trunk at all
-- (night 6 Nov, cp fix round 1) an art tree's trunk as drawn at row y (riverwalk/cp_tree_spans.lua, from
-- tools/cp_trunk_spans.py): the trunk narrows upwards, and a limb that left the foot's width lay over sky
local SPANS
local function artSpan(u, y)
  if SPANS == nil then local ok, D = pcall(require, "cp_tree_spans"); SPANS = ok and D or false end
  local name = u.artName and u.artName:match("^([^@]+)")
  local S = SPANS and name and SPANS[name]
  if not S or not y then return nil end
  local r = S[y - u.artY0] or S[y - u.artY0 + 1] or S[y - u.artY0 - 1]
  if not r then return nil end
  if u.artName:find("@flip") then return u.artX0 + S.w - 1 - r[2], u.artX0 + S.w - r[1] end
  return u.artX0 + r[1], u.artX0 + r[2] + 1
end
local function cpbTrunkSpan(A, t, y)
  if not t or t.fake then return nil end
  local cx = (t.x0 + t.x1) / 2
  for _, u in ipairs(CPB_TI and CPB_TI.trunks or {}) do
    if u.hasArt and u.artW and math.abs((u.x0 + u.x1) / 2 - cx) < 4 then
      local a0, b0 = artSpan(u, y)
      if a0 then return a0, b0, 0.28, u end                         -- (round 2: the art trunk it is, 4th value)
      local a = math.floor(u.artCx - u.artW / 2)
      return a, a + u.artW, 0.28, u
    end
  end
  local tw = A.D.trunk.tw
  local a = math.floor(cx - tw / 2)
  return a, a + tw, Sc.fadeK("back")
end
local function cpbCrossed(q)                                      -- a trunk runs through this ledge (a fork)
  for _, t in ipairs(CPB_TI and CPB_TI.trunks or {}) do if t.x0 < q.x1 and t.x1 > q.x0 then return true end end
end
-- a tier branch at the same height that meets this one at its left (-1) or right (1) end: the two run on as one limb
-- (a gap of up to 60 px only when the other is a branch reaching back to its trunk across it)
local function cpbJoin(p, side)
  for _, q in ipairs(CPB_TI and CPB_TI.ledges or {}) do
    if q ~= p and q.y0 == p.y0 and CPB_TI.role[q] == "branch" then
      local gap = side > 0 and (q.x0 - p.x1) or (p.x0 - q.x1)
      if gap >= -2 and (gap <= 12 or (gap <= 60 and not cpbCrossed(q))) then return q end
    end
  end
end
-- one row less every 16 px away from the trunk (8 on it, 4 at least)
local function cpbThick(x, ta, tb, R)
  if not ta then return R end
  local d = math.max(0, ta - x, x - (tb - 1))
  return math.max(math.min(4, R), R - math.floor(d / 16))
end
-- columns { x, top, t, k (nil: in front, inked; else the fade of the trunk it lies on) } of strip n, whole columns
-- in world order (a joined limb stays continuous), runs of equal columns as one quad
local function cpbDraw(A, n, cols, ox)
  local d = A.D[n]; local R, W = d.rows, d.w - 2
  lg.setColor(INK)
  local sk = {}                                                     -- (round 2) the columns left out on an art trunk:
  for _, c in ipairs(cols) do if c.skip then sk[c.x] = true end end -- no ink on the trunk's side of the limb's root
  for _, c in ipairs(cols) do
    if not c.k then
      local l, r = sk[c.x - 1] and 0 or 1, sk[c.x + 1] and 0 or 1
      lg.rectangle("fill", c.x - l - ox, c.top - 1, 1 + l + r, c.t + 2)
    end
  end
  lg.setColor(1, 1, 1, 1)
  local keep = {}                                                   -- (round 2) never ledge art over an art tree's
  for _, c in ipairs(cols) do if not c.skip then keep[#keep + 1] = c end end   -- trunk: those columns are left out (no
  cols = keep                                                        -- bar through the bark); on a code trunk in the
                                                                     -- canopy the root still runs on in its fade
  local i = 1
  while i <= #cols do
    local c = cols[i]
    local j = i
    local sc = 1 + c.x % W
    while j < #cols do
      local q = cols[j + 1]
      if q.x ~= cols[j].x + 1 or q.top ~= c.top or q.t ~= c.t or q.k ~= c.k or 1 + q.x % W ~= sc + (j + 1 - i) then break end
      j = j + 1
    end
    local wdt = j - i + 1
    local im = c.k and cpbFaded(A, n, c.k) or A[n]
    if c.t <= R then
      local a = math.ceil(c.t / 2); local b = c.t - a
      lg.draw(im, cpbQuad(im, sc, 1, wdt, a), c.x - ox, c.top)
      if b > 0 then lg.draw(im, cpbQuad(im, sc, R + 1 - b, wdt, b), c.x - ox, c.top + a) end
    else                                                            -- a crotch: the strip's top half, its lower middle
      local h = math.floor(R / 2)                                   -- row stamped down, its bottom half
      lg.draw(im, cpbQuad(im, sc, 1, wdt, h), c.x - ox, c.top)
      for y = 0, c.t - R - 1 do lg.draw(im, cpbQuad(im, sc, h + 1, wdt, 1), c.x - ox, c.top + h + y) end
      lg.draw(im, cpbQuad(im, sc, h + 1, wdt, R - h), c.x - ox, c.top + c.t - (R - h))
    end
    i = j + 1
  end
end
-- a rounded free end past x (dir 1: to the right, -1: to the left), with a short twig rising out of it
local function cpbTip(cols, x, top, dir, R)
  if R > 8 then                                                     -- the low bough: its thick end rounded off
    cols[#cols + 1] = { x = x + dir, top = top + 2, t = R - 4 }
    cols[#cols + 1] = { x = x + 2 * dir, top = top + 5, t = R - 9 }
  else
    cols[#cols + 1] = { x = x + dir, top = top, t = 3 }
    cols[#cols + 1] = { x = x + 2 * dir, top = top + 1, t = 2 }
    for i = 1, 4 do cols[#cols + 1] = { x = x + (2 + i) * dir, top = top - i + 1, t = 1, twig = true } end
  end
end
-- the limb thinning to its free end: 4 rows at the end, one more every 3 columns back (the underside curves up)
local function cpbTaper(t, d) return math.min(t, 4 + math.floor(d / 3)) end
-- the crotch under a limb where it leaves its trunk: the underside curves down into the trunk's edge
local function cpbCrotch(x, ta, tb)
  if not ta then return 0 end
  local d = x < ta and (ta - 1 - x) or (x >= tb and (x - tb) or -1)
  if d < 0 or d > 6 then return 0 end
  return math.floor((7 - d) * (7 - d) / 6)
end
local function cpbSort(cols) table.sort(cols, function(a, b) return a.x < b.x end) end
-- (night 6 Nov, cp fix round 1; review cp_limes_pillars: "every crotch ledge reads as a canoe") a limb's profile from
-- where it leaves its trunk (d = 0) to its free end (d = L): T rows at the trunk with a 2 px collar (2 rows more, its
-- own darker band, drawn by cpbCollar), thinning to 3 rows at the tip, the underside curving up all the way (never a
-- deep crotch under the box's end). T differs per limb so the two arms of a fork are not mirror images.
local function cpbLimbT(d, L, T)
  T = math.min(T, 3 + math.floor(L / 4))                            -- a short arm is a short, slimmer limb, not a wedge
  local u = math.min(1, math.max(0, d / math.max(1, L)))
  local t = math.floor(3 + (T - 3) * (1 - u ^ 1.6) + 0.5)          -- (round 1b: full for most of its length, then thinning)
  if d < 2 then t = t + 2 end
  return t
end
-- the forked tip past x (dir 1: right): 2 rows, then two 1 px twigs, one on the top row going on level, one
-- dropping out of the underside (a small fork, no hook turned up)
local function cpbTip2(cols, x, top, dir)
  cols[#cols + 1] = { x = x + dir, top = top, t = 2 }
  cols[#cols + 1] = { x = x + 2 * dir, top = top, t = 1, twig = true }
  cols[#cols + 1] = { x = x + 3 * dir, top = top, t = 1, twig = true }
  cols[#cols + 1] = { x = x + 2 * dir, top = top + 3, t = 1, twig = true }
end
-- the bark collar: the 2 columns where a limb leaves its trunk, a darker vertical band over the limb's lower rows
-- (round 1b) the collar is the 2 px bulge itself (cpbLimbT: 2 rows more there) and one bark furrow across the limb
-- 2 px out from the trunk, in the strip's own dark (a dark band at the root read as a bracket under a shelf)
local COLLAR = hex("6b4329")
local BANDC = { oak = hex("6c3628"), lime = hex("5f3326") }   -- (polish) the limbs' bark bands
local function cpbCollar(x, top, t, ox, dir)
  lg.setColor(COLLAR); lg.rectangle("fill", x + dir * 2 - ox, top + 2, 1, math.max(1, t - 4))
  lg.setColor(1, 1, 1, 1)
end

local function drawBranch(p, trunk, camx)
  local side = ((p.x0 + p.x1) / 2 < (trunk.x0 + trunk.x1) / 2) and -1 or 1
  local A = cpb()
  if A then                                                         -- (6 Nov) the art: the box, the dip to the trunk, the
    local ox = math.floor(camx)                                     -- part on the trunk; a rounded tip at the free end
    local n = (trunk.art or trunk.x1 - trunk.x0 >= 24) and "limbx" or "limb"
    local ta, tb, k, artT = cpbTrunkSpan(A, trunk, p.y0 + 4)
    local tc = math.floor((trunk.x0 + trunk.x1) / 2)
    local cols = {}
    -- from the box's trunk end to the trunk: an earlier limb at this height there (a fork's arm) is joined instead
    local near = side > 0 and p.x0 or p.x1 - 1
    local stop, flat = side > 0 and tc or tc, false
    for _, q in ipairs(CPB_TI and CPB_TI.ledges or {}) do
      if q ~= p and q.y0 == p.y0 and CPB_TI.role[q] == "branch" and ((side > 0 and q.x1 > tb - 1 and q.x1 <= p.x0 + 2) or (side < 0 and q.x0 < ta + 1 and q.x0 >= p.x1 - 2)) then
        stop, flat = side > 0 and q.x1 or q.x0 - 1, true
      end
    end
    local a, b = side > 0 and tb or p.x1, side > 0 and p.x0 - 1 or ta - 1      -- the dip, between trunk and box
    local nn = b - a + 1
    local function drop(x)
      if flat or x < a or x > b or nn <= 6 then return 0 end
      local d = side > 0 and (b - x) or (x - a)
      return math.floor(6 * d / nn + 0.5)
    end
    local x0, x1 = side > 0 and stop or p.x0, side > 0 and p.x1 - 1 or stop
    local edge = ta and (side > 0 and tb or ta - 1)                 -- (round 1) the column where it leaves the trunk
    local tipx = side > 0 and p.x1 - 1 or p.x0
    local L = edge and math.abs(tipx - edge) or (p.x1 - p.x0)
    local T = 8 + (p.x0 + p.y0) % 3                                 -- 8 to 10 rows at the trunk, per limb
    local joined = cpbJoin(p, side)
    for x = x0, x1 do
      local onTrunk = not flat and x >= ta and x < tb
      local dd = onTrunk and drop(side > 0 and tb or ta - 1) or drop(x)
      local t
      if onTrunk then t = T + 2                                      -- its root on the trunk (in the trunk's fade)
      elseif joined or flat or not edge then t = cpbThick(x, ta, tb, 8)
      else t = cpbLimbT(math.abs(x - edge), L, T) end
      cols[#cols + 1] = { x = x, top = p.y0 + dd, t = t, k = onTrunk and k or nil, skip = onTrunk and artT ~= nil }
    end
    if not joined then cpbTip2(cols, tipx, p.y0, side) end
    cpbSort(cols)
    cpbDraw(A, n, cols, ox)
    -- (night 6 Nov, cp polish; review c06cfb6: the oaks' long limbs read as flat boards) two broken bark bands along
    -- the limb in the bark's dark (the old oak's own 6c3628, else the strip's 5f3326), a gap every 7 px
    lg.setColor(artT and artT.artName == "cp_oak" and BANDC.oak or BANDC.lime)
    for _, c in ipairs(cols) do
      if not c.skip and not c.k and not c.twig and c.t >= 5 then
        if c.x % 7 ~= 0 then lg.rectangle("fill", c.x - ox, c.top + math.floor(c.t / 3) + 1, 1, 1) end
        if (c.x + 3) % 7 ~= 0 then lg.rectangle("fill", c.x - ox, c.top + math.floor(2 * c.t / 3) + 1, 1, 1) end
      end
    end
    lg.setColor(1, 1, 1, 1)
    if edge and not flat then cpbCollar(edge, p.y0 + drop(edge), T + 2, ox, side) end
    -- (round 2) the art tree's own pixels were drawn again over the limb's end here, under the play look: a lighter
    -- box on the trunk. The limb no longer reaches over an art tree's trunk (cpbDraw skips those columns), so it is gone.
    return
  end
  local cols = {}                                                 -- x -> top, thickness
  local len = p.x1 - p.x0
  for x = p.x0, p.x1 - 1 do
    local d = side > 0 and (x - p.x0) or (p.x1 - 1 - x)           -- distance from the trunk end
    cols[#cols + 1] = { x, p.y0, 6 - math.floor(2 * d / len + 0.5) }
  end
  local a, b = side > 0 and trunk.x1 - 3 or p.x1, side > 0 and p.x0 - 1 or trunk.x0 + 2   -- the dip to the trunk
  local n = b - a + 1
  for x = a, b do
    local d = side > 0 and (b - x) or (x - a)
    local up = n > 6 and math.floor(6 * d / n + 0.5) or 0
    cols[#cols + 1] = { x, p.y0 + up, 6 }
  end
  local ox = math.floor(camx)
  lg.setColor(INK)
  for _, c in ipairs(cols) do lg.rectangle("fill", c[1] - 1 - ox, c[2] - 1, 3, c[3] + 2) end
  for _, c in ipairs(cols) do
    local x = c[1] - ox
    lg.setColor(BARK[1]); lg.rectangle("fill", x, c[2], 1, c[3])
    lg.setColor(BARK[2]); lg.rectangle("fill", x, c[2], 1, 1)
    lg.setColor(BARK[3]); lg.rectangle("fill", x, c[2] + c[3] - 1, 1, 1)
  end
  for k = 1, 3 do                                                 -- bark knots
    local x = math.floor(p.x0 + len * k / 4) - ox
    lg.setColor(BARK[3]); lg.rectangle("fill", x, p.y0 + 2, 2, 1)
  end
  -- a twig past the tip, rising out and away (no ledge), with a few autumn leaves on it
  local tx = (side > 0 and p.x1 or p.x0 - 1) - ox
  local pts = { { 0, 1 }, { 1, 0 }, { 2, -1 }, { 3, -2 }, { 4, -2 } }
  lg.setColor(INK)
  for _, q in ipairs(pts) do lg.rectangle("fill", tx + side * q[1] - 1, p.y0 + q[2] - 1, 3, 3) end
  for _, q in ipairs({ { 2, -4 }, { 5, -4 }, { 4, -6 }, { 1, -1 } }) do lg.rectangle("fill", tx + side * q[1] - 1, p.y0 + q[2] - 1, 3, 3) end
  lg.setColor(BARK[1])
  for _, q in ipairs(pts) do lg.rectangle("fill", tx + side * q[1], p.y0 + q[2], 1, 1) end
  for i, q in ipairs({ { 2, -4 }, { 5, -4 }, { 4, -6 }, { 1, -1 } }) do
    lg.setColor(LEAF[1 + i % 3]); lg.rectangle("fill", tx + side * q[1] - (side < 0 and 1 or 0), p.y0 + q[2], 2, 1)
    lg.rectangle("fill", tx + side * q[1], p.y0 + q[2] - 1, 1, 1)
  end
  lg.setColor(1, 1, 1, 1)
end

local function named(def, name) for _, q in ipairs(def.props) do if q.name == name then return q end end end
-- the named prop nearest to an unnamed one (it belongs to that set piece)
local function owner(def, p)
  local best, bd = nil, 1e9
  local cx = (p.x0 + p.x1) / 2
  for _, q in ipairs(def.props) do
    if q.name and q.name ~= "" and q.layer ~= "front" then
      local d = math.max(0, q.x0 - cx, cx - q.x1)
      if d < bd then best, bd = q, d end
    end
  end
  return best
end
local function shadowUnder(p, camx, depth) Sc.shadow((p.x0 + p.x1) / 2 - camx, p.y1 - 1, p.x1 - p.x0 + 4, depth) end
local function at(im, x, y) lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x), math.floor(y)) end

-- City Park's willows: the crown boxes (the WILLOWS prop and the unnamed decoration boxes of its size), each with
-- its bough (the one-way box right under the crown)
local function willowCrowns(def)
  if def._crowns then return def._crowns end
  local wl = named(def, "WILLOWS")
  local L = {}
  if wl then
    for _, q in ipairs(def.props) do
      if q.kind == "decor" and q.layer == "back" and (q == wl or ((not q.name or q.name == "") and q.x1 - q.x0 == wl.x1 - wl.x0
        and q.y1 - q.y0 == wl.y1 - wl.y0 and math.abs(q.x0 - wl.x0) < 200)) then L[#L + 1] = q end
    end
  end
  def._crowns = L
  return L
end
local function underCrown(def, p)
  for _, c in ipairs(willowCrowns(def)) do if p.kind == "oneway" and p.y0 == c.y1 and p.x0 >= c.x0 and p.x1 <= c.x1 then return c end end
end
-- a willow bough over its one-way box: 5 px thick in the middle, thinner at both ends, the trunk behind it; willow
-- twigs hang from its ends (past the box, below its top)
local WLEAF = { hex("c9a93c"), hex("a8892a"), hex("dcc35a") }
local WTRUNK = {}
local function drawBough(p, camx, crown, def)
  local ox = math.floor(camx)
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
  if crown and not (def and Sc.bigWillow(def)) then                  -- (night 6 Nov, cp fix round 1; review: "deck planks
    -- floating in the willow crowns") the willow's own trunk (park_willow's columns 29-35, its colours as faded) drawn
    -- up through the crown to the bough, so the bough sits on its tree instead of hanging in the leaves
    if not WTRUNK[Look.key] then
      WTRUNK[Look.key] = { Sc.fadeC(hex("665e48")), Sc.fadeC(hex("7a735e")), Sc.fadeC(hex("8a836c")) }
    end
    local W = WTRUNK[Look.key]
    local cx = math.floor((crown.x0 + crown.x1) / 2 - ox)
    local yb = 175 + dy() - 26                                        -- the trunk's top under the crown (art row ~58)
    for xx = -3, 3 do
      lg.setColor(xx == -3 and W[2] or (xx >= 2 and W[1] or W[3]))
      lg.rectangle("fill", cx + xx, y + 2, 1, yb - y - 2)
    end
  end
  local len = x1 - x0
  lg.setColor(INK)
  for x = x0, x1 - 1 do
    local d = math.abs((x - x0) - len / 2) / (len / 2)
    lg.rectangle("fill", x - 1, y - 1, 3, (d > 0.7 and 4 or 5) + 2)
  end
  for x = x0, x1 - 1 do
    local d = math.abs((x - x0) - len / 2) / (len / 2)
    local t = d > 0.7 and 4 or 5
    lg.setColor(BARK[1]); lg.rectangle("fill", x, y, 1, t)
    lg.setColor(BARK[2]); lg.rectangle("fill", x, y, 1, 1)
    lg.setColor(BARK[3]); lg.rectangle("fill", x, y + t - 1, 1, 1)
  end
  for _, e in ipairs({ { x0 + 2, 1 }, { x1 - 3, -1 } }) do           -- willow strands hanging from both ends
    for k = 0, 3 do
      local tx = e[1] + e[2] * k * 2
      lg.setColor(WLEAF[1 + k % 3]); lg.rectangle("fill", tx, y + 4, 1, 5 + (k * 3) % 7)
    end
  end
  lg.setColor(1, 1, 1, 1)
end
-- a balcony (Downtown's rooftop route) over its one-way box: an iron railing at its back, the stone slab (its top
-- the ledge), two brackets under it
Sc.BALCONY_RAIL = 46
-- (art/dt-roofs-06nov) built art for pieces drawn in code until now: art/scene/<name>.png, unfaded (they are obstacles),
-- or false when the file is not there; the code drawing stays as the fallback
local OPT = {}
local function optImg(n)
  if OPT[n] == nil then
    OPT[n] = love.filesystem.getInfo("art/scene/" .. n .. ".png") and newImg("art/scene/" .. n .. ".png") or false
  end
  return OPT[n]
end
local BQ = {}
local function balconyQ(im, rail)                                        -- the railing rows, or the slab and corbels
  local k = tostring(im) .. (rail and "r" or "s")
  if not BQ[k] then
    local iw, ih = im:getDimensions()
    BQ[k] = rail and lg.newQuad(0, 0, iw, Sc.BALCONY_RAIL, iw, ih) or lg.newQuad(0, Sc.BALCONY_RAIL, iw, ih - Sc.BALCONY_RAIL, iw, ih)
  end
  return BQ[k]
end
-- the balconies' railings with art, behind everything on her line (stage.lua, the back pass); the code fallback draws
-- its railing with the slab (drawBalcony)
function Sc.drawBalconyRails(def, camx)
  local ox = math.floor(camx)
  for _, p in ipairs(def.props) do
    if p.name == "BALCONY" and p.layer == "play" and p.x1 - ox > -10 and p.x0 - ox < 330 then
      local im = optImg("town_balcony" .. (p.x1 - p.x0))
      if im then lg.setColor(1, 1, 1, 1); lg.draw(im, balconyQ(im, true), p.x0 - ox - 1, p.y0 - 1 - Sc.BALCONY_RAIL) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
local function drawBalcony(p, camx)
  local ox = math.floor(camx)
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
  local w = x1 - x0
  -- (art/dt-roofs-06nov) town_balcony<w>.png (tools/build_dt_details.py): w + 2 wide, its slab's ink row (row
  -- BALCONY_RAIL) on the box's top - 1, so its top row is the box's top - 1 - BALCONY_RAIL
  -- (review round 2) only the slab and corbels here, on her line; the railing (rows 0 .. BALCONY_RAIL - 1) is drawn in
  -- the back pass (Sc.drawBalconyRails), so the bones, Pepper and Mia are always in front of it
  local im = optImg("town_balcony" .. w)
  if im then
    lg.setColor(1, 1, 1, 1); lg.draw(im, balconyQ(im, false), x0 - 1, y - 1); return
  end
  -- the railing (behind Pepper): 1 m high = BALCONY_RAIL px (46 at 46 px a metre; was 9; layer plan decision 6b, 26 Oct).
  -- Open work, so what is behind it shows: a top rail, a mid rail, balusters (1 px dark edge each side) every 6 px
  local hh = Sc.BALCONY_RAIL
  local gx = lg.setColor
  local function baluster(bx) gx(INK); lg.rectangle("fill", bx, y - hh, 3, hh); gx(0.30, 0.32, 0.36); lg.rectangle("fill", bx + 1, y - hh, 1, hh) end
  local n = math.max(1, math.floor((w - 5) / 6))                      -- (posts evenly from the first to the last, 3 px wide)
  for i = 0, n do baluster(x0 + 2 + math.floor(i * (w - 5) / n)) end
  gx(INK); lg.rectangle("fill", x0 + 1, y - math.floor(hh / 2) - 1, w - 2, 3)   -- the mid rail
  gx(0.30, 0.32, 0.36); lg.rectangle("fill", x0 + 1, y - math.floor(hh / 2), w - 2, 1)
  gx(INK); lg.rectangle("fill", x0 + 1, y - hh, w - 2, 4)             -- the top rail
  gx(0.50, 0.52, 0.56); lg.rectangle("fill", x0 + 2, y - hh + 1, w - 4, 2)
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, w + 2, 6)     -- the slab
  lg.setColor(0.79, 0.76, 0.72); lg.rectangle("fill", x0, y, w, 1)
  lg.setColor(0.64, 0.61, 0.57); lg.rectangle("fill", x0, y + 1, w, 2)
  lg.setColor(0.44, 0.41, 0.39); lg.rectangle("fill", x0, y + 3, w, 1)
  for _, bx in ipairs({ x0 + 5, x1 - 9 }) do                          -- brackets
    lg.setColor(INK); lg.rectangle("fill", bx - 1, y + 4, 6, 5); lg.rectangle("fill", bx, y + 9, 4, 2)
    lg.setColor(0.58, 0.55, 0.51); lg.rectangle("fill", bx, y + 4, 4, 4); lg.rectangle("fill", bx + 1, y + 8, 2, 2)
  end
  lg.setColor(1, 1, 1, 1)
end
local function houseIndex(def, p)
  local i = 0
  for _, q in ipairs(def.props) do if q.name == "HOUSE" then i = i + 1; if q == p then return i end end end
  return 1
end

-- a coil spring (crisp, outlined: it is part of an obstacle), centred on x, from y down h px
-- (art/dt-roofs-06nov) town_spring.png (tools/build_dt_details.py): 4 frames 9 x 10 side by side, for h = 7, 8, 9, 10
-- (it is squashed by 2 px as it launches her); the frame's rows 0 .. h - 1 are drawn
local springQ = {}
function Sc.spring(x, y, h)
  local im = optImg("town_spring")
  if im and h >= 7 and h <= 10 then
    springQ[h] = springQ[h] or lg.newQuad((h - 7) * 9, 0, 9, h, im:getDimensions())
    lg.setColor(1, 1, 1, 1); lg.draw(im, springQ[h], math.floor(x) - 4, math.floor(y)); return
  end
  lg.setColor(INK); lg.rectangle("fill", x - 4, y, 9, h)
  for yy = y + 1, y + h - 2, 3 do
    lg.setColor(0.86, 0.22, 0.18); lg.rectangle("fill", x - 3, yy, 7, 2)            -- red coils
    lg.setColor(1, 0.62, 0.52); lg.rectangle("fill", x - 3, yy, 7, 1)
  end
end

-- a courtyard gate at the end of a cargo bike's run (Downtown, r8/levels D1; until then the tram shed, the same art
-- and the same `depot` code): a brick front with a cornice (its roof is a perch) and a dark arched gateway open on
-- the right, where the cargo bike rides into the courtyard (it is drawn and hurts only right of the gateway)
local gateQ = {}
function Sc.courtyardGate(p, camx)
  local x, w, h = math.floor(p.x0 - camx), p.x1 - p.x0, p.y1 - p.y0
  local im = Sc.townArt("town").tramshed[w]                       -- the art (town_tramshed70 / 96): its cornice on
  if im and im:getHeight() > 48 then im = nil end                 -- (6 Nov: town_tramshed96 is the true-scale gate of the
                                                                  -- tall level, arthooks H.freeGate; here: the code gate)
  if im then                                                      -- the box's top; the old tram rails below the
    if not gateQ[im] then gateQ[im] = lg.newQuad(0, 0, w, math.min(h, im:getHeight()), im:getDimensions()) end   -- line are left out
    lg.setColor(1, 1, 1, 1); lg.draw(im, gateQ[im], x, p.y0); return
  end
  lg.setColor(INK); lg.rectangle("fill", x - 1, p.y0 - 1, w + 2, h + 1)
  lg.setColor(0.62, 0.36, 0.27); lg.rectangle("fill", x, p.y0 + 4, w, h - 4)               -- brick
  lg.setColor(0.52, 0.29, 0.22)
  for yy = p.y0 + 7, p.y1 - 2, 4 do
    lg.rectangle("fill", x, yy, w, 1)
    for xx = x + ((yy / 4) % 2 == 0 and 2 or 6), x + w - 1, 8 do lg.rectangle("fill", xx, yy - 3, 1, 3) end
  end
  lg.setColor(0.29, 0.35, 0.33); lg.rectangle("fill", x - 2, p.y0, w + 4, 4)               -- the cornice: the roof
  lg.setColor(0.46, 0.54, 0.50); lg.rectangle("fill", x - 2, p.y0, w + 4, 1)
  lg.setColor(INK); lg.rectangle("fill", x + 6, p.y0 + 10, w - 6, h - 10)                  -- the doorway
  lg.rectangle("fill", x + 9, p.y0 + 8, w - 9, 2)
  lg.setColor(0.10, 0.10, 0.13); lg.rectangle("fill", x + 7, p.y0 + 11, w - 7, h - 11)
  lg.setColor(0.86, 0.70, 0.22); lg.rectangle("fill", x + 2, p.y0 + 6, 4, 3)              -- a lamp by the door
  lg.setColor(1, 1, 1, 1)
end

-- ===================================================================================================================
-- The treetop tier of a tall park (the tall City Park's high road; only a level with L.foot, its path line, and
-- props high over it). Built from the level's boxes, as everything else here, in the park's two manners:
--   obstacles (the branches, the walks, the arbour's slats, the play tower's decks, the low bough): crisp, their
--             own 1 px dark outline, front-on (no tops seen from above), the box's top row is the ledge
--   decoration (trunks, the arbour's posts, the canopies): faded towards the haze, no outline, behind Pepper
-- The tier: a ledge (one-way or solid) whose bottom is 90 px or more above the path, and decoration whose top is
-- 100 px or more above it. Its parts, by name (an unnamed ledge belongs to the named ledge over or under it, else
-- to the named ledge before it in the map):
--   TREETOP WALK, ALDER WALK  a plank walk: built, a rope bridge between pylons on dry ground (cp_built.lua); else
--                             on timber legs down to the ground, none in the water
--   ARBOUR                    the rose arbour's slats, each on two posts with a climbing rose
--   PLAY TOWER                the play tower's decks (grey posts as the slide tower's)
--   LOW BOUGH                 a thick bough to crawl under, bending up into the canopy
--   NEST, BIG OAK             the magpie's nest (the landmark) and the big oak's trunk
--   any other ledge           a branch of the nearest tree: across its trunk, or reaching out from it
-- Narrow decoration boxes standing on the path are trunks (or posts under a deck or a slat); wide ones are the
-- canopies, drawn from the crowns of the park's tree art (park_tree1, park_tree2, park_oak), faded. A canopy
-- with no trunk near one end gets one there, on dry ground: nothing floats.
local TIER_NAMES = { ["TREETOP WALK"] = "walk", ["ALDER WALK"] = "walk", ARBOUR = "slat", ["PLAY TOWER"] = "deck",
  ["LOW BOUGH"] = "lowbough" }
local function fadeC(c, k) return Sc.fadeC(c, k) end
local FB = {}                                                      -- faded bark and roses, per colour script
local function fbark() if not FB[Look.key] then FB[Look.key] = { fadeC(BARK[1]), fadeC(BARK[2]), fadeC(BARK[3]) } end return FB[Look.key] end
local WOOD = { hex("a8784a"), hex("c99a63"), hex("6e4a2c") }           -- the walks' planks: light, top, dark
local POST = { hex("8f969c"), hex("b9bfc4"), hex("5d646b") }           -- the play tower's grey posts (the slide's)
local DECK = { hex("e2b23a"), hex("f3d36a"), hex("a77a1e") }           -- its yellow decks
local FR = {}
local function rose() if not FR[Look.key] then FR[Look.key] = { fadeC(hex("4f7a3a")), fadeC(hex("d9586e")), fadeC(hex("f2a0b0")) } end return FR[Look.key] end   -- vine, rose, rose light

local function tier(def)
  if def._tier ~= nil then return def._tier end
  local foot = def.foot
  if not foot or foot <= 184 then def._tier = false; return false end
  local TI = { role = {}, trunks = {}, canopies = {}, ledges = {}, foot = foot }
  local lastNamed
  local named_ = {}
  for _, p in ipairs(def.props) do
    if p.layer ~= "front" and p.kind ~= "decor" and p.y1 <= foot - 90 and p.name and p.name ~= "" then named_[#named_ + 1] = p end
  end
  for _, p in ipairs(def.props) do
    if p.layer == "front" then
    elseif p.kind ~= "decor" and p.y1 <= foot - 90 then              -- a ledge of the tier
      local who
      if p.name and p.name ~= "" then who = p
      else
        for _, q in ipairs(named_) do if q.x0 < p.x1 and q.x1 > p.x0 then who = q; break end end
        who = who or lastNamed
      end
      if p.name and p.name ~= "" then lastNamed = p end
      TI.role[p] = (who and TIER_NAMES[who.name]) or "branch"
      TI.ledges[#TI.ledges + 1] = p
    elseif p.kind == "decor" and p.y0 <= foot - 100 then             -- decoration of the tier
      if p.name == "NEST" then TI.role[p] = "nest"
      elseif p.name == "BIG OAK" then TI.role[p] = "trunk"; TI.trunks[#TI.trunks + 1] = p
      elseif p.x1 - p.x0 <= 12 and p.y1 >= foot - 40 then TI.role[p] = "trunk"
      elseif p.x1 - p.x0 >= 48 and p.y1 <= foot - 100 then TI.role[p] = "canopy"; TI.canopies[#TI.canopies + 1] = p
      else TI.role[p] = "skip" end
    end
  end
  for p, r in pairs(TI.role) do                                     -- a trunk under a deck or a slat is its post
    if r == "trunk" and p.name ~= "BIG OAK" then
      local post
      for _, q in ipairs(TI.ledges) do
        if (TI.role[q] == "deck" or TI.role[q] == "slat") and q.x0 < p.x1 and q.x1 > p.x0 and q.y1 <= p.y0 + 2 then post = TI.role[q] end
      end
      -- (art/placement) or a ledge it holds up part way down: the play tower's lower deck (on the low road's tier,
      -- so not one of TI.ledges) on its outer post, which was drawn as a 4 px tree trunk up into the oak's canopy
      -- (a post stops short of the path; a trunk goes down to it). It is drawn from that ledge down to the path,
      -- and the ledge as a deck (drawPropArt); it was an invisible step left of the slide tower's cage
      for _, q in ipairs(def.props) do
        if p.y1 < foot and q.kind == "oneway" and q.x0 < p.x1 and q.x1 > p.x0 and q.y0 > p.y0 and q.y1 <= p.y1 then
          post = "deck"; TI.postTop = TI.postTop or {}; TI.postTop[p] = q.y0
        end
      end
      if post then TI.role[p] = post == "deck" and "towerpost" or "skip" else TI.trunks[#TI.trunks + 1] = p end
    end
  end
  local oak = named(def, "OAK")                                      -- City Park's old oak (its art has its trunk)
  if oak then TI.trunks[#TI.trunks + 1] = { x0 = oak.x0, x1 = oak.x1, y0 = oak.y0, y1 = oak.y1, art = true } end
  table.sort(TI.trunks, function(a, b) return a.x0 < b.x0 end)
  def._tier = TI
  return TI
end
Sc.tier = tier

-- the trunk a branch grows from: one across it, else the nearest one under the canopy
local function trunkOf(TI, p)
  local best, bd
  for _, t in ipairs(TI.trunks) do
    local d = math.max(0, t.x0 - p.x1, p.x0 - t.x1)
    if not best or d < bd then best, bd = t, d end
  end
  return best, bd
end

-- a faded trunk from y top down to the path: bark lines, a lit left edge, a shaded right edge, roots that flare
local CPBT = {}                                                    -- (6 Nov) the trunk art, faded as the back, per script
-- (day/07nov-ground, audit CP8: the root flares ended in a straight line on the lawn) grass over a trunk's foot:
-- the kit's root tuft strip (tools/make_ground_kit.py kit_cp_roots, 16 x 5, faded as the back), stamped every 16 px
-- across the foot, 4 px past it each side
local ROOTS = {}
local function rootTufts(xa, xb, foot)
  if ROOTS[Look.key] == nil then
    local f = "art/scene/kit_cp_roots.png"
    ROOTS[Look.key] = love.filesystem.getInfo(f) and newImg(Sc.fadeData(love.image.newImageData(f))) or false
  end
  local im = ROOTS[Look.key]
  if not im then return end
  lg.setColor(1, 1, 1, 1)
  local a, b = math.floor(xa) - 4, math.floor(xb) + 4
  for x = a, b - 1, 16 do
    local w = math.min(16, b - x)
    lg.draw(im, lg.newQuad(0, 0, w, 5, 16, 5), x, foot - 5)
  end
end
local function drawTrunk(t, top, foot, ox, big)
  local x0, w = t.x0 - ox, t.x1 - t.x0
  local h = foot - top
  local A = cpb()
  if A then                                                         -- (6 Nov) the art: the trunk of the nearest width,
    local best, bd                                                  -- its foot on the path, its top the trunk's own
    for _, n in ipairs({ "trunk" }) do                              -- top rows again above it (round 2: every trunk the
                                                                    -- oak trunk, 33 px, true scale for a park tree)
      local dd = A.D[n] and math.abs(A.D[n].tw - w)
      if dd and (not bd or dd < bd) then best, bd = n, dd end
    end
    local key = best and (best .. "/" .. Look.key)
    if best and CPBT[key] == nil then
      local f = "art/scene/cp_bough_" .. best .. ".png"
      CPBT[key] = love.filesystem.getInfo(f) and newImg(Sc.fadeData(love.image.newImageData(f))) or false
    end
    local im = best and CPBT[key]
    if im then
      local d = A.D[best]
      local ix = math.floor(x0 + w / 2 - d.x0 - d.tw / 2)
      lg.setColor(1, 1, 1, 1)
      if h <= d.h then lg.draw(im, cpbQuad(im, 0, d.h - h, d.w, h), ix, top)
      else
        lg.draw(im, ix, foot - d.h)
        local seg = math.min(64, d.h - 20)                          -- the upper rows (no foot), stacked above
        local y = foot - d.h
        while y > top do
          local s = math.min(seg, y - top)
          lg.draw(im, cpbQuad(im, 0, seg - s, d.w, s), ix, y - s)
          y = y - s
        end
      end
      rootTufts(ix + d.x0, ix + d.x0 + d.tw, foot)
      return
    end
  end
  for y = top, foot - 1 do
    local fl = 0
    local e = foot - y
    if e <= 3 then fl = big and 6 or 3 elseif e <= 7 then fl = big and 3 or 1 elseif big and e <= 12 then fl = 1 end
    lg.setColor(fbark()[1]); lg.rectangle("fill", x0 - fl, y, w + 2 * fl, 1)
    lg.setColor(fbark()[2]); lg.rectangle("fill", x0 - fl, y, 1, 1)
    lg.setColor(fbark()[3]); lg.rectangle("fill", x0 + w + fl - (w > 10 and 3 or 2), y, w > 10 and 3 or 2, 1)
  end
  lg.setColor(fbark()[3])                                             -- bark furrows, broken now and then
  for bx = x0 + 3, x0 + w - 4, 4 do
    local s = (bx * 7) % 11
    for y = top + s, foot - 6, 13 do lg.rectangle("fill", bx, y, 1, 8) end
  end
  if big then                                                       -- knots on the big oak
    for _, k in ipairs({ 0.3, 0.55, 0.8 }) do
      local ky = math.floor(top + h * k)
      lg.setColor(fbark()[3]); lg.rectangle("fill", x0 + math.floor(w * k), ky, 4, 3)
      lg.setColor(fbark()[2]); lg.rectangle("fill", x0 + math.floor(w * k), ky - 1, 4, 1)
    end
  end
end

-- a canopy: the crowns of the park's trees (faded), overlapping, covering its box and a little round it
local CROWNS = {}                                                  -- per colour script
-- a tree's crown alone: the art down to its trunk's foot, minus the trunk (from row `from` down, only the leaves:
-- the orange pixels, red well over blue), faded as decoration
local function crownImg(n, rows, from)
  local src = love.image.newImageData("art/scene/" .. n .. ".png")
  local w = src:getWidth()
  local d = love.image.newImageData(w, rows)
  local hz, k = Sc.haze("back"), Sc.fadeK("back")
  for y = 0, rows - 1 do
    for x = 0, w - 1 do
      local r, g, b, a = src:getPixel(x, y)
      if a > 0 and (y < from or r - b > 0.28) then
        d:setPixel(x, y, r + (hz[1] - r) * k, g + (hz[2] - g) * k, b + (hz[3] - b) * k, a)
      end
    end
  end
  return newImg(d)
end
local function crowns()
  if CROWNS[Look.key] then return CROWNS[Look.key] end
  local function c(n, rows, from) local im = crownImg(n, rows, from); return { im = im, q = lg.newQuad(0, 0, im:getWidth(), rows, im:getDimensions()), w = im:getWidth(), h = rows } end
  CROWNS[Look.key] = { c("park_tree1", 78, 52), c("park_tree2", 78, 52), oak = c("park_oak", 76, 58) }
  return CROWNS[Look.key]
end
local CANOPY_SKIP = nil                                            -- (5 Nov) x spans of the art trees' crowns
local function drawCanopy(c, ox, T)
  local Q = crowns()
  local w, h = c.x1 - c.x0, c.y1 - c.y0
  local r = rng(c.x0 * 3 + c.y0)
  lg.setColor(1, 1, 1, 1)
  local function put(cr, x, y, flip)
    if CANOPY_SKIP then                                             -- an old crown that the new tree's leaves cover at its
      local cy = math.floor(y + cr.h / 2)                            -- middle row is left out (round 2: the box test left
      for _, a in ipairs(CANOPY_SKIP) do                             -- sky wedges where the new crown is narrow); one
        local r = a.rows and a.rows[cy - a.y0]                       -- beside it stays and goes on behind it
        if r and x + 6 < a.x0 + r[2] and x + cr.w - 6 > a.x0 + r[1] then return end
      end
    end
    x, y = math.floor(x - ox), math.floor(y)
    if x > 330 or x + cr.w < -10 then return end
    if flip then lg.draw(cr.im, cr.q, x + cr.w, y, 0, -1, 1) else lg.draw(cr.im, cr.q, x, y) end
  end
  if h >= 90 then                                                   -- a big crown: oak crowns over a row of trees
    local n = math.max(1, math.ceil((w - 187) / 120) + 1)
    for i = 0, n - 1 do
      local x = n == 1 and (c.x0 + w / 2 - 94) or (c.x0 - 14 + i * (w + 28 - 187) / (n - 1))
      put(Q.oak, x, c.y0 - 6 + (i % 2) * 8, i % 2 == 1)
    end
    for x = c.x0 - 16, c.x1 - 70, 58 do
      local k = 1 + math.floor(r(0, 1.99))
      put(Q[k], x + r(-6, 6), c.y1 - 52 + r(-4, 4), r(0, 1) < 0.5)
    end
    for x = c.x0 + 20, c.x1 - 100, 74 do                             -- and between them, to close the gaps
      local k = 1 + math.floor(r(0, 1.99))
      put(Q[k], x + r(-6, 6), c.y0 + 30 + r(-4, 4), r(0, 1) < 0.5)
    end
  elseif h >= 60 and w >= 180 then                                  -- an oak's top
    put(Q.oak, c.x0 + w / 2 - 94, c.y0, false)
  else                                                              -- a row of tree crowns
    local cy = (c.y0 + c.y1) / 2
    local n = math.max(1, math.ceil((w - 70) / 54) + 1)
    for i = 0, n - 1 do
      local k = 1 + (i + math.floor(c.x0 / 8)) % 2
      local x = n == 1 and (c.x0 + w / 2 - 43) or (c.x0 - 12 + i * (w + 24 - 87) / (n - 1))
      put(Q[k], x + r(-4, 4), cy - 36 + ((i % 2 == 0) and r(-5, 0) or r(2, 7)), i % 2 == 1)
    end
  end
end

-- leafy twigs at a branch's tip (as the old oak's branches have), rising out and away
local function tipTwig(tx, y, side)
  local pts = { { 0, 1 }, { 1, 0 }, { 2, -1 }, { 3, -2 }, { 4, -2 } }
  local lv = { { 2, -4 }, { 5, -4 }, { 4, -6 }, { 1, -1 } }
  lg.setColor(INK)
  for _, q in ipairs(pts) do lg.rectangle("fill", tx + side * q[1] - 1, y + q[2] - 1, 3, 3) end
  for _, q in ipairs(lv) do lg.rectangle("fill", tx + side * q[1] - 1, y + q[2] - 1, 3, 3) end
  lg.setColor(BARK[1])
  for _, q in ipairs(pts) do lg.rectangle("fill", tx + side * q[1], y + q[2], 1, 1) end
  for i, q in ipairs(lv) do
    lg.setColor(LEAF[1 + i % 3]); lg.rectangle("fill", tx + side * q[1] - (side < 0 and 1 or 0), y + q[2], 2, 1)
    lg.rectangle("fill", tx + side * q[1], y + q[2] - 1, 1, 1)
  end
end
-- a bough lying across its trunk: 6 px thick over the trunk, 4 at the tips, twigs at both tips; the trunk's top
-- shows under it (it grows out of the trunk)
-- (night 6 Nov, cp fix round 2: two failed rounds on the forks, so a new method; review e62a282) a stand-on limb drawn
-- pixel by pixel, never over the trunk: from the trunk's edge at its row (cp_tree_spans) out to its free end. Thick
-- at a bark collar on the trunk (7 rows, 8 in the collar's 2 columns), 2 to 3 rows at the free end and a 1 px twig;
-- its top curves down by 2 px towards the end and the underside follows; two broken bark bands run along it; the
-- tree's own bark ramp (the lime's, or the old oak's); a 1 px ink outline except where it meets the trunk.
local LIMBR = { lime = { hex("cb6b23"), hex("8e4a26"), hex("5f3326"), hex("3e2421"), hex("ad5724") },
                oak = { hex("f47815"), hex("9e4b21"), hex("6c3628"), hex("412c2b"), hex("9e4b21") } }   -- lit, mid, band, shade, second
local function limbCols(e, dir, L, y0, T0)
  local cols = {}
  for d = 0, L - 1 do
    local u = L > 1 and d / (L - 1) or 0
    local t = math.floor(T0 - (T0 - 2.5) * u + 0.5)
    if d < 2 then t = t + 1 end                                     -- the collar
    cols[#cols + 1] = { x = e + dir * d, top = y0 + math.floor(2 * u * u + 0.5), t = math.max(2, t), d = d }
  end
  local last = cols[#cols]
  for i = 1, 2 do cols[#cols + 1] = { x = last.x + dir * i, top = last.top + (i == 2 and 1 or 0), t = 1, d = L - 1 + i, twig = true } end
  return cols
end
local function stubCols(e, dir, K, y0)                              -- the stub on the other side: short, tapering 6 to 3,
  local cols = {}                                                   -- its end rounded (no square cut)
  for d = 0, K - 1 do
    local u = K > 1 and d / (K - 1) or 0
    local t = math.floor(6 - 3 * u + 0.5)
    local top = y0
    if d == K - 1 then top, t = y0 + 1, math.max(2, t - 1) end
    cols[#cols + 1] = { x = e + dir * d, top = top, t = t, d = d }
  end
  return cols
end
local function drawLimbCols(cols, R, ox)
  lg.setColor(INK)                                                  -- the outline: above, below, and round the free end
  for i, c in ipairs(cols) do
    lg.rectangle("fill", c.x - ox, c.top - 1, 1, 1); lg.rectangle("fill", c.x - ox, c.top + c.t, 1, 1)
    local nx = cols[i + 1]
    if not nx or nx.x == c.x then                                   -- the end column: its outer side
      local dir = (#cols > 1 and cols[2].x < cols[1].x) and -1 or 1
      lg.rectangle("fill", c.x + dir - ox, c.top - 1, 1, c.t + 2)
    elseif nx.top ~= c.top or nx.t ~= c.t then                       -- steps between columns: close them
      local a0, b0 = math.min(c.top, nx.top), math.max(c.top + c.t, nx.top + nx.t)
      for y = a0 - 1, b0 do
        local inC = y >= c.top and y < c.top + c.t
        local inN = y >= nx.top and y < nx.top + nx.t
        if inC ~= inN then lg.rectangle("fill", (inC and nx.x or c.x) - ox, y, 1, 1) end
      end
    end
  end
  for _, c in ipairs(cols) do
    for k = 0, c.t - 1 do
      local col
      if c.twig then col = R[2]
      elseif k == 0 then col = R[1]                                  -- the lit top, the stand-on edge
      elseif k == c.t - 1 then col = R[4]                            -- the shaded underside
      elseif k == 1 then col = R[5]                                  -- the second lit row
      else
        local band = (k == math.floor(c.t / 3) + 1 or k == math.floor(2 * c.t / 3) + 1) and (c.x % 7 ~= 0)
        col = band and R[3] or R[2]                                  -- the body, two broken bark bands along it
        if c.d < 2 and k >= c.t / 2 then col = R[3] end              -- the collar's lower half
      end
      lg.setColor(col); lg.rectangle("fill", c.x - ox, c.top + k, 1, 1)
    end
  end
  lg.setColor(1, 1, 1, 1)
end
-- a fork (a ledge its trunk crosses): its trunk's span at the ledge's row; on the landing side (the longer overhang,
-- the left on a tie) one limb, 24 px or more (past the box's end where the box is shorter, there thin and dropping),
-- on the other side a knot as long as the box reaches there. Both overhangs 24 px or more: a limb each side.
local function drawForkLimbs(p, t, ox, ta, tb)
  local name = t.artName and t.artName:match("^([^@]+)")
  local R = (name == "cp_oak") and LIMBR.oak or LIMBR.lime
  local oL, oR = ta - p.x0, p.x1 - tb
  -- (night 6 Nov, cp polish; review c06cfb6) a 2 px bark saddle along the box's top over the trunk, in the tree's own
  -- browns (its lit row, then its mid; no ink, no dark line), where she stands across the crotch
  for x = math.max(ta, p.x0), math.min(tb, p.x1) - 1 do
    lg.setColor(Sc.fadeC(R[1], 0.28)); lg.rectangle("fill", x - ox, p.y0, 1, 1)   -- (as the trunk is drawn: faded)
    lg.setColor(Sc.fadeC(R[5], 0.28)); lg.rectangle("fill", x - ox, p.y0 + 1, 1, 1)
  end
  lg.setColor(1, 1, 1, 1)
  local cols = {}
  local function add(cs) for _, c in ipairs(cs) do cols[#cols + 1] = c end end
  if oL >= 24 and oR >= 24 then
    drawLimbCols(limbCols(ta - 1, -1, oL, p.y0, 7), R, ox); drawLimbCols(limbCols(tb, 1, oR, p.y0, 7), R, ox)
    return
  end
  local left = oL >= oR
  local o, k = left and oL or oR, left and oR or oL
  local L = math.max(o, math.min(24, o + 16))
  drawLimbCols(limbCols(left and ta - 1 or tb, left and -1 or 1, L, p.y0, 7), R, ox)
  if k > 0 then drawLimbCols(stubCols(left and tb or ta - 1, left and 1 or -1, math.max(4, k), p.y0), R, ox) end
end
local function drawFork(p, t, ox)
  local A = cpb()
  if A then                                                         -- (6 Nov) the art: one limb across its trunk, on the
    local ta, tb, k, artT = cpbTrunkSpan(A, t, p.y0 + 4)            -- trunk in the trunk's fade, tapering to rounded tips
    if artT and ta > p.x0 - 2 and tb < p.x1 + 2 and not cpbJoin(p, -1) and not cpbJoin(p, 1) then
      return drawForkLimbs(p, artT or t, ox, ta, tb)                 -- (round 2: the new method)
    end
    local n = (t.art or t.x1 - t.x0 >= 24) and "limbx" or "limb"
    -- (night 6 Nov, cp fix round 1; review: "a lens deck with dark upturned tips at both ends") two limbs leaving the
    -- trunk, not one deck through it: over the trunk only a 2-row ridge (the crotch's top, in the trunk's fade, where
    -- she stands), each arm thick at its collar and thinning to a forked tip; the left arm 9 rows, the right 8 (or the
    -- other way round, by the box), so the fork is not mirrored
    local cols = {}
    local jl, jr = cpbJoin(p, -1), cpbJoin(p, 1)
    local TL, TR = 8 + (p.x0 % 2), 9 - (p.x0 % 2)
    for x = p.x0, p.x1 - 1 do
      local on = ta and x >= ta and x < tb
      local tt
      if not ta then tt = cpbThick(x, ta, tb, 8)
      elseif on then tt = 2                                       -- (round 1b) a ridge: the lit stand-on row and its shade
      elseif x < ta then tt = jl and cpbThick(x, ta, tb, 8) or cpbLimbT(ta - 1 - x, ta - 1 - p.x0, TL)
      else tt = jr and cpbThick(x, ta, tb, 8) or cpbLimbT(x - tb, p.x1 - 1 - tb, TR) end
      cols[#cols + 1] = { x = x, top = p.y0, t = tt, k = on and k or nil, skip = on and artT ~= nil }
    end
    if jr then                                                      -- runs on into the next limb: no tip, the gap filled
      for x = p.x1, jr.x0 - 1 do cols[#cols + 1] = { x = x, top = p.y0, t = cpbThick(x, ta, tb, 8) } end
    elseif not (tb and p.x1 - 1 < tb) then cpbTip2(cols, p.x1 - 1, p.y0, 1) end   -- (no tip on an end that lies on the trunk)
    if not jl and not (ta and p.x0 >= ta) then cpbTip2(cols, p.x0, p.y0, -1) end
    cpbSort(cols)
    cpbDraw(A, n, cols, ox)
    if ta then
      if ta > p.x0 and not jl then cpbCollar(ta - 1, p.y0, TL + 2, ox, -1) end
      if tb < p.x1 and not jr then cpbCollar(tb, p.y0, TR + 2, ox, 1) end
    end
    return
  end
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
  local tc = (t.x0 + t.x1) / 2 - ox
  local half = math.max(tc - x0, x1 - tc)
  local function th(x) return 6 - math.floor(2 * math.abs(x + 0.5 - tc) / half + 0.5) end
  lg.setColor(INK)
  for x = x0, x1 - 1 do lg.rectangle("fill", x - 1, y - 1, 3, th(x) + 2) end
  for x = x0, x1 - 1 do
    local k = th(x)
    lg.setColor(BARK[1]); lg.rectangle("fill", x, y, 1, k)
    lg.setColor(BARK[2]); lg.rectangle("fill", x, y, 1, 1)
    lg.setColor(BARK[3]); lg.rectangle("fill", x, y + k - 1, 1, 1)
  end
  lg.setColor(BARK[3])
  for k = 1, 3 do lg.rectangle("fill", math.floor(x0 + (x1 - x0) * k / 4), y + 2, 2, 1) end
  tipTwig(x1, y, 1); tipTwig(x0 - 1, y, -1)
end

-- (art/cp-built-06nov) the built art of the walks, the arbour and the play tower (tools/build_cp_built.py, 0
-- credits): riverwalk/cp_built.lua lists, per box, the images drawn instead of the code drawings below (file, top left
-- in the world, faded to the back haze or not). A box that is not in the list (it moved) or a missing file keeps the
-- code drawing, so nothing Pepper stands on can lose its art.
local CB, CBI = nil, {}
local function built(p, part)
  if CB == nil then CB = love.filesystem.getInfo("cp_built.lua") and require("cp_built") or false end
  if not CB then return nil end
  local e = CB[("%d,%d,%d,%d"):format(p.x0, p.y0, p.x1, p.y1)]
  local f = e and e[part]
  if not f then return nil end
  local key = f[1] .. (f[4] and ("/" .. Look.key) or "")
  if CBI[key] == nil then
    local path = "art/scene/" .. f[1] .. ".png"
    CBI[key] = love.filesystem.getInfo(path) and newImg(f[4] and Sc.fadeData(love.image.newImageData(path)) or path) or false
  end
  if not CBI[key] then return nil end
  return CBI[key], f[2], f[3], e
end
Sc.built = built

-- a plank walk: the deck (crisp), a rope hand-rail on posts behind Pepper. (art/cp-pond-06nov) The built walks
-- are rope bridges: a pylon at each end on dry ground, a cable sagging between their tops, hangers to the deck
-- (tools/build_cp_built.py); the pylons' legs are drawn here with the walk, unfaded and in front of the willows,
-- so each pylon is one post from the ground to its cap. Nothing stands in the water.
local function drawWalk(p, ox)
  local ri, rx, ry = built(p, "rail")
  local di, dx, dy_ = built(p, "deck")
  if ri and di then
    local li, lx_, ly = built(p, "legs")
    lg.setColor(1, 1, 1, 1)
    if li then lg.draw(li, lx_ - ox, ly) end
    lg.draw(ri, rx - ox, ry); lg.draw(di, dx - ox, dy_)
    return
  end
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
  local hgt = p.y1 - p.y0
  local w = x1 - x0
  -- the rail stands 1 m (46 px) over the deck, as a real hand rail does (plan decision 8 b, owner 26 Oct; it was 15
  -- px, 0.3 m): posts, a hand rope along the top and a second rope half way down. It is behind Pepper and Pepper
  -- passes through it: only the deck is a ledge.
  local RAIL = 46
  for px = x0 + 4, x1 - 4, 40 do                                     -- rail posts and the ropes between them
    lg.setColor(INK); lg.rectangle("fill", px - 1, y - RAIL - 1, 4, RAIL + 1)
    lg.setColor(WOOD[3]); lg.rectangle("fill", px, y - RAIL, 2, RAIL); lg.setColor(WOOD[2]); lg.rectangle("fill", px, y - RAIL, 1, 1)
    if px + 40 <= x1 - 4 then
      for dx = 2, 39 do
        local u = dx / 40
        local sag = 4 * 4 * u * (1 - u) * 0.5
        for _, top in ipairs({ y - RAIL + 3, y - 24 }) do            -- the hand rope, and the lower one
          local ry = math.floor(top + sag + 0.5)
          lg.setColor(INK); lg.rectangle("fill", px + dx, ry - 1, 1, 3)
          lg.setColor(hex("c9b48a")); lg.rectangle("fill", px + dx, ry, 1, 1)
        end
      end
    end
  end
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, w + 2, hgt + 2)  -- the deck
  lg.setColor(WOOD[1]); lg.rectangle("fill", x0, y, w, hgt)
  lg.setColor(WOOD[2]); lg.rectangle("fill", x0, y, w, 1)
  lg.setColor(WOOD[3]); lg.rectangle("fill", x0, y + hgt - 1, w, 1)
  for x = x0 + 7, x1 - 2, 8 do lg.setColor(WOOD[3]); lg.rectangle("fill", x, y + 1, 1, hgt - 2) end   -- plank joints
end
-- its legs (behind Pepper): pairs of timbers down to the ground, or into the water (seen through it). Decoration:
-- no outline, faded to the back haze like the trunks, the edge a darker shade of the timber's own colour (plan
-- decision 8 a, owner 26 Oct; they were INK outlined and unfaded, the darkest decoration in the level)
local function drawWalkLegs(p, ox, foot, world)
  local floorY = world and world.height or (foot + 56)
  if built(p, "legs") and built(p, "rail") and built(p, "deck") then return end   -- (built: drawn with the walk)
  local c1, c2 = fadeC({ 0.30, 0.24, 0.20 }), fadeC({ 0.42, 0.34, 0.27 })     -- timber, its lit left edge
  local c3 = { c1[1] * 0.78, c1[2] * 0.78, c1[3] * 0.78 }                    -- its shaded right edge
  local tie = fadeC({ 0.36, 0.29, 0.23 })
  local tie3 = { tie[1] * 0.78, tie[2] * 0.78, tie[3] * 0.78 }
  for lx = p.x0 + 6, p.x1 - 10, 60 do
    local wet = false
    for _, r in ipairs(world and world.water or {}) do if lx >= r.x0 and lx < r.x1 then wet = true end end
    if wet then goto nextLeg end                                      -- (art/cp-pond-06nov) no leg in the water
    do
    local bottom = foot
    local x = lx - ox
    lg.setColor(c1); lg.rectangle("fill", x, p.y1, 4, bottom - p.y1)
    lg.setColor(c2); lg.rectangle("fill", x, p.y1, 1, bottom - p.y1)
    lg.setColor(c3); lg.rectangle("fill", x + 3, p.y1, 1, bottom - p.y1)
    for by = p.y1 + 20, bottom - 30, 40 do                           -- cross ties
      lg.setColor(tie); lg.rectangle("fill", x - 2, by, 8, 2)
      lg.setColor(tie3); lg.rectangle("fill", x - 2, by + 2, 8, 1)
    end
    end
    ::nextLeg::
  end
end

-- the rose arbour: a slat (crisp), its posts and roses (faded, behind)
local function drawSlat(p, ox)
  local si, sx, sy = built(p, "slat")
  if si then lg.setColor(1, 1, 1, 1); lg.draw(si, sx - ox, sy); return end
  local x0, x1, y, hgt = p.x0 - ox, p.x1 - ox, p.y0, p.y1 - p.y0
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, x1 - x0 + 2, hgt + 2)
  lg.setColor(hex("e9e2d2")); lg.rectangle("fill", x0, y, x1 - x0, hgt)
  lg.setColor(hex("fbf7ec")); lg.rectangle("fill", x0, y, x1 - x0, 1)
  lg.setColor(hex("b3a993")); lg.rectangle("fill", x0, y + hgt - 1, x1 - x0, 1)
  for x = x0 + 3, x1 - 4, 6 do                                      -- the rose hanging off its front, under the top
    lg.setColor(rose()[1]); lg.rectangle("fill", x, y + hgt - 2, 3, 3)
    if math.floor(x / 6) % 2 == 0 then lg.setColor(hex("d9586e")); lg.rectangle("fill", x + 1, y + hgt, 2, 2) end
  end
end
local function drawSlatPosts(p, ox, foot)
  local pi_, px_, py = built(p, "posts")
  if pi_ then lg.setColor(1, 1, 1, 1); lg.draw(pi_, px_ - ox, py); return end
  for _, px in ipairs({ p.x0 + 2, p.x1 - 7 }) do
    local x = px - ox
    lg.setColor(fadeC(hex("cfc6b3"))); lg.rectangle("fill", x, p.y1, 5, foot - p.y1)
    lg.setColor(fadeC(hex("9d927c"))); lg.rectangle("fill", x + 4, p.y1, 1, foot - p.y1)
    for y = p.y1 + 4, foot - 6, 7 do                                  -- a climbing rose round it
      local s = math.floor(y / 7) % 2 == 0 and -1 or 5
      lg.setColor(rose()[1]); lg.rectangle("fill", x + s, y, 2, 4); lg.rectangle("fill", x + 1, y + 2, 3, 1)
      if math.floor(y / 7) % 3 == 0 then lg.setColor(rose()[2]); lg.rectangle("fill", x + s, y - 1, 2, 2); lg.setColor(rose()[3]); lg.rectangle("fill", x + s, y - 1, 1, 1) end
    end
  end
end

-- the play tower: a yellow deck (crisp), grey posts (crisp, as the slide tower's)
local function drawDeck(p, ox)
  local di, dx, dy_ = built(p, "deck")
  if di then
    lg.setColor(1, 1, 1, 1)
    for _, part in ipairs({ "support", "support2" }) do               -- (art/cp-audit-06nov) the post under its free end
      local si, sx, sy = built(p, part)
      if si then lg.draw(si, sx - ox, sy) end
    end
    lg.draw(di, dx - ox, dy_); return
  end
  local x0, x1, y, hgt = p.x0 - ox, p.x1 - ox, p.y0, p.y1 - p.y0
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, x1 - x0 + 2, hgt + 2)
  lg.setColor(DECK[1]); lg.rectangle("fill", x0, y, x1 - x0, hgt)
  lg.setColor(DECK[2]); lg.rectangle("fill", x0, y, x1 - x0, 1)
  lg.setColor(DECK[3]); lg.rectangle("fill", x0, y + hgt - 1, x1 - x0, 1)
end
-- (art/placement) a post goes down to the path (foot), behind the slide tower's art: it stopped in the air at the
-- cage's top; top: where it starts (its deck), default its box's top
local function drawTowerPost(t, ox, foot, top)
  local ti, tx, ty = built(t, "post")
  if ti then lg.setColor(1, 1, 1, 1); lg.draw(ti, tx - ox, ty); return end
  local x, w = t.x0 - ox, t.x1 - t.x0
  local y0, y1 = top or t.y0, math.max(t.y1, foot or t.y1)
  lg.setColor(INK); lg.rectangle("fill", x - 1, y0, w + 2, y1 - y0)
  lg.setColor(POST[1]); lg.rectangle("fill", x, y0, w, y1 - y0)
  lg.setColor(POST[2]); lg.rectangle("fill", x, y0, 1, y1 - y0)
  if w > 3 then lg.setColor(POST[3]); lg.rectangle("fill", x + w - 1, y0, 1, y1 - y0) end
end

-- the low bough (crisp): a thick bough over the walk, bending up into the canopy at its trunk's side
local function drawLowBough(p, t, ox)
  local x0, x1, y0, y1 = p.x0 - ox, p.x1 - ox, p.y0, p.y1
  local side = t and ((t.x0 + t.x1) / 2 > (p.x0 + p.x1) / 2) and 1 or -1
  local A = cpb()
  if A then                                                         -- (6 Nov) the art: 16 rows over its box (32 x 16),
    local ta, tb, k = cpbTrunkSpan(A, t)                            -- its free end rounded, then rising into its trunk
    local cols = {}                                                 -- (round 2: level, an elbow over the whole trunk)
    local far = ta and (side > 0 and tb - 1 or ta) or (side > 0 and p.x1 + 26 or p.x0 - 27)
    local xa, xb = side > 0 and p.x0 or far, side > 0 and far or p.x1 - 1
    for x = xa, xb do
      local on = ta and x >= ta and x < tb
      local tt = 16 + (on and 0 or math.floor(cpbCrotch(x, ta, tb) / 2))
      local edge = side > 0 and (x - (tb - 1)) or (ta - x)           -- the elbow's outer corner rounded over the trunk
      local top = p.y0 + ((on and edge > -3) and (3 + edge) or 0)
      cols[#cols + 1] = { x = x, top = top, t = tt - (top - p.y0), k = on and k or nil }
    end
    cpbTip(cols, side > 0 and p.x0 or p.x1 - 1, p.y0, -side, 16)
    cpbSort(cols)
    cpbDraw(A, "low", cols, ox)
    return
  end
  -- (art/placement) front-on, as a bough is seen from the side: over its box it lies level (the top Pepper stands
  -- on, the gap she crawls under), its free end rounded off; towards its trunk it bends up into the leaves, the
  -- underside curving up faster than the top, so it thins from 16 px to about 7 (was a slab rising 1 px a column,
  -- which read as a crate seen from above)
  local cols = {}                                                   -- { x, top, bottom (inclusive) }
  local n = x1 - x0
  for i = 0, n - 1 do
    local x = x0 + i
    local e = side > 0 and i or (n - 1 - i)                        -- columns from the free end
    local tip = e < 10 and math.floor(7 - e * 0.7 + 0.5) or 0       -- (the underside rises to the free end gently, a bough, not a hull)
    cols[#cols + 1] = { x, y0 + (e == 0 and 1 or 0), y1 - 1 - tip }
  end
  -- (plan decision 8 e, owner 26 Oct) it used to curl up in 20 columns, 30 px, ending in a thin leaf clump in open
  -- sky: a boat's prow. Now a gentler rise over 26 columns (16 px) into a leaf mass that is wider and taller than the
  -- bough's end, so it reads as a bough going into the foliage
  local reach = 26
  for i = 1, reach do                                               -- towards its trunk, rising into the leaves
    local x = side > 0 and (x1 - 1 + i) or (x0 - i)
    local mid = (y0 + y1 - 1) / 2 - i * i / 42                     -- its middle line curves up (a parabola)
    local th = (y1 - y0) - i * 0.4                                 -- and it thins
    cols[#cols + 1] = { x, math.floor(mid - th / 2 + 0.5), math.floor(mid + th / 2 + 0.5) }
  end
  lg.setColor(INK)
  for _, c in ipairs(cols) do lg.rectangle("fill", c[1] - 1, c[2] - 1, 3, c[3] - c[2] + 3) end
  for _, c in ipairs(cols) do
    local h = c[3] - c[2] + 1
    lg.setColor(BARK[1]); lg.rectangle("fill", c[1], c[2], 1, h)
    lg.setColor(BARK[2]); lg.rectangle("fill", c[1], c[2], 1, h > 9 and 2 or 1)
    lg.setColor(BARK[3]); lg.rectangle("fill", c[1], c[3] - (h > 9 and 1 or 0), 1, h > 9 and 2 or 1)
    if h >= 8 then                                                  -- two bark furrows along it, broken now and then
      for _, k in ipairs({ 0.36, 0.66 }) do
        if (c[1] * 7 + math.floor(k * 10)) % 9 < 6 then lg.rectangle("fill", c[1], c[2] + math.floor(h * k), 1, 1) end
      end
    end
  end
  tipTwig(side > 0 and x0 - 1 or x1, y0 + 4, -side)
  local ex = side > 0 and (x1 + reach) or (x0 - reach)              -- where it goes into the leaves: a leafy mass
  local last = cols[#cols]
  local ey = math.floor((last[2] + last[3]) / 2)
  local MASS = { { 0, -14 }, { -7, -11 }, { 7, -11 }, { 0, -8 }, { -12, -6 }, { 12, -6 }, { -6, -4 }, { 6, -4 }, { 0, -1 },
    { -13, 1 }, { 13, 0 }, { -8, 3 }, { 8, 3 }, { 0, 4 }, { -3, -12 }, { 4, -14 }, { -10, -2 }, { 10, -3 } }
  local function blob(cx, cy, w, h, c)                              -- a rounded patch of leaves: three rectangles
    lg.setColor(c)
    local x, y = math.floor(cx - w / 2), math.floor(cy - h / 2)       -- (whole pixels)
    lg.rectangle("fill", x + 2, y, w - 4, h); lg.rectangle("fill", x + 1, y + 1, w - 2, h - 2)
    lg.rectangle("fill", x, y + 2, w, h - 4)
  end
  for _, q in ipairs(MASS) do blob(ex + side * q[1], ey + q[2], 11, 9, INK) end     -- the mass's dark rim first
  for i, q in ipairs(MASS) do blob(ex + side * q[1], ey + q[2], 9, 7, LEAF[1 + (i * 7) % 3]) end
  for i, q in ipairs(MASS) do                                       -- light on the upper left of some of them
    if i % 2 == 0 then lg.setColor(LEAF[3]); lg.rectangle("fill", ex + side * q[1] - 2, ey + q[2] - 2, 3, 1) end
  end
end

-- the magpie's nest at the top of the big oak (the landmark: dark twigs, not faded, so it reads from below)
local function drawNest(p, ox)
  local x0, x1, y0, y1 = p.x0 - ox, p.x1 - ox, p.y0, p.y1
  local w = x1 - x0
  local A = cpb()
  if A then                                                         -- (6 Nov) the art: the bowl on its bough, centred
    lg.setColor(1, 1, 1, 1)
    lg.draw(A.nest, math.floor((x0 + x1) / 2 - A.D.nest.w / 2), y1 - A.D.nest.h)
    return
  end
  lg.setColor(INK)
  for x = x0 - 1, x1 do
    local u = (x - x0 + 0.5) / w * 2 - 1
    local top = y0 + math.floor(3 * u * u + 0.5)
    lg.rectangle("fill", x, top - 1, 1, y1 - top + 2)
  end
  for x = x0, x1 - 1 do
    local u = (x - x0 + 0.5) / w * 2 - 1
    local top = y0 + math.floor(3 * u * u + 0.5)
    lg.setColor(hex("5a4130")); lg.rectangle("fill", x, top, 1, y1 - top)
    lg.setColor(hex("8a6a4a")); if (x + top) % 3 == 0 then lg.rectangle("fill", x, top + 1 + (x % 4), 1, 1) end
    lg.setColor(hex("3b2a1f")); if x % 5 == 0 then lg.rectangle("fill", x, top + 3, 2, 1) end
  end
  lg.setColor(hex("2a1d16")); lg.rectangle("fill", x0 + 3, y0 + 1, w - 6, 2)   -- its hollow
  for _, s in ipairs({ { x0 - 3, y0 + 2, -1 }, { x1 + 1, y0 + 1, 1 }, { x0 + 6, y0 - 2, -1 }, { x1 - 8, y0 - 1, 1 } }) do   -- stray twigs
    lg.setColor(INK); lg.rectangle("fill", s[1] - 1, s[2] - 1, 5, 3)
    lg.setColor(hex("6e5038")); lg.rectangle("fill", s[1], s[2], 3, 1)
  end
end

-- (5 Nov, the City Park sample screen; owner's picks 26 Oct, plan decision 1) trees at true scale: a SpriteCook piece
-- per tree, trunk and one leaf mass whose top is above the world (tools/cut_cp_tree.py). Keyed by the trunk's x in the
-- tall City Park (OAK: the old oak). Its trunk is not drawn in code, the canopy boxes inside its crown are skipped, and
-- the art stands on the back props' line (the path - 9, as the old oak's art did), faded as back decoration.
local TREE_ART = { [1528] = "cp_lime", [1916] = "cp_ash", OAK = "cp_oak",
  -- (night 6 Nov, cp) the three LIMES trunks at 1004, 1112, 1216 were flat-topped pillars under their ledges, their
  -- crowns a low band: tables. Now lime trees whose crowns run out of the top of the screen, as the lime at 1528;
  -- the middle one mirrored ("@flip": the same art flipped whole, no new pixels) so the row is not a stamp
  -- (and the fourth pillar at 1420, the audit's "same grey as the mid crowns": the lime's darker bark, mirrored)
  [1004] = "cp_lime", [1112] = "cp_lime@flip", [1216] = "cp_lime", [1420] = "cp_lime@flip" }
local TREE_FADE = 0.28           -- their own amount, as the gate's: the bark's darkest 10 % then sits at the back layer's 80
local TA_IMG = {}
local function treeArtImg(n)
  local key = n .. "/" .. Look.key
  if TA_IMG[key] ~= nil then return TA_IMG[key] end
  local file, flip = n:match("^([^@]+)(@?f?l?i?p?)$")
  flip = flip == "@flip"
  if not love.filesystem.getInfo("art/scene/" .. file .. ".png") then TA_IMG[key] = false; return false end
  local d = love.image.newImageData("art/scene/" .. file .. ".png")
  local w, h = d:getDimensions()
  if flip then                                                       -- mirrored whole, pixel for pixel
    local s = d; d = love.image.newImageData(w, h)
    for y = 0, h - 1 do for x = 0, w - 1 do d:setPixel(w - 1 - x, y, s:getPixel(x, y)) end end
  end
  local sx, cnt = 0, 0                                               -- the trunk's centre: 30 px above its foot
  for x = 0, w - 1 do local _, _, _, a = d:getPixel(x, h - 31); if a > 0 then sx = sx + x; cnt = cnt + 1 end end
  local rows = {}                                                    -- each row's opaque x extent (the old canopies' test)
  for y = 0, h - 1 do
    local x0, x1
    for x = 0, w - 1 do local _, _, _, a = d:getPixel(x, y); if a > 0 then x0 = x0 or x; x1 = x end end
    rows[y] = x0 and { x0, x1 } or false
  end
  local t = { im = newImg(Sc.fadeData(d, TREE_FADE)), w = w, h = h, rows = rows, cx = cnt > 0 and math.floor(sx / cnt + 0.5) or math.floor(w / 2), tw = cnt }
  TA_IMG[key] = t
  return t
end
local function treeArt(def, TI)
  if TI.arttrees then return TI.arttrees end
  TI.arttrees = {}
  for _, t in ipairs(TI.trunks) do
    local n = t.art and TREE_ART.OAK or (not t.extra and TREE_ART[t.x0])
    if n and treeArtImg(n) then
      t.hasArt = true
      local a = treeArtImg(n)
      t.artCx, t.artW = math.floor((t.x0 + t.x1) / 2), a.tw            -- (6 Nov) its drawn trunk, for the limbs on it
      local cx = math.floor((t.x0 + t.x1) / 2)
      t.artName, t.artX0, t.artY0 = n, cx - a.cx, TI.foot - 9 - a.h     -- (round 1) for its trunk's width per row
      TI.arttrees[#TI.arttrees + 1] = { name = n, cx = cx, x0 = cx - a.cx, x1 = cx - a.cx + a.w, oak = t.art,
        y0 = TI.foot - 9 - a.h, rows = a.rows, art = a }
    end
  end
  table.sort(TI.arttrees, function(a, b) return (a.oak and 1 or 0) < (b.oak and 1 or 0) end)   -- the oak in front
  return TI.arttrees
end
-- (night 6 Nov, cp track) the tall City Park's weeping willow (art/scene/cp_willow.png, SpriteCook GPT 2.5 2K cut 1:1,
-- 10 m crown, true scale): one tree centred on the WILLOWS crown, its trunk's foot on the back props' line (the path - 10,
-- as the old willows), faded as the other art trees. It replaces the three 1.8-2 m willows (park_willow, _tall).
-- nil on the flat City Park or without the file.
function Sc.bigWillow(def)
  if def._bigWillow ~= nil then return def._bigWillow or nil end
  def._bigWillow = false
  local wl = def.foot and def.art == "park" and named(def, "WILLOWS")
  local a = wl and treeArtImg("cp_willow")
  if a then
    local cx = math.floor((wl.x0 + wl.x1) / 2)
    def._bigWillow = { art = a, x0 = cx - a.cx, x1 = cx - a.cx + a.w, y0 = def.foot - 9 - a.h }
  end
  return def._bigWillow or nil
end
function Sc.oakHasArt(def)
  local TI = def.foot and tier(def)
  if not TI then return false end
  for _, a in ipairs(treeArt(def, TI)) do if a.oak then return true end end
  return false
end

-- the tier's decoration, behind Pepper: trunks, posts, walk legs, canopies (called before the back props)
function Sc.drawTreetops(def, camx, world)
  if def.art ~= "park" then return end
  local TI = tier(def)
  if not TI then return end
  local T = Sc.townArt("park")
  local ox, foot = math.floor(camx), TI.foot
  if not TI.extra then                                              -- trunks a canopy needs at its ends (dry ground)
    TI.extra = {}
    for _, c in ipairs(TI.canopies) do
      for _, e in ipairs({ { c.x0 + 16, -1 }, { c.x1 - 16, 1 } }) do
        local near = false
        for _, t in ipairs(TI.trunks) do
          if math.abs((t.x0 + t.x1) / 2 - e[1]) <= math.max(100, (t.x1 - t.x0) * 5) then near = true end
        end
        local wet = false
        for _, r in ipairs(world and world.water or {}) do if e[1] >= r.x0 - 8 and e[1] < r.x1 + 8 then wet = true end end
        if not near and not wet then
          local t = { x0 = e[1] - 5, x1 = e[1] + 5, y0 = c.y1, y1 = foot, extra = true }
          TI.extra[#TI.extra + 1] = t; TI.trunks[#TI.trunks + 1] = t
        end
      end
    end
    table.sort(TI.trunks, function(a, b) return a.x0 < b.x0 end)
  end
  local function canopyOver(t)                                       -- the canopy a trunk goes up into
    for _, c in ipairs(TI.canopies) do if c.x0 <= t.x1 and c.x1 >= t.x0 and c.y1 <= t.y0 + 60 then return c end end
  end
  local AT = treeArt(def, TI)
  local wl = Sc.bigWillow(def)                                       -- (night 6 Nov, cp) the pond's weeping willow at
  if wl and wl.x1 - ox > -10 and wl.x0 - ox < 330 then               -- true scale, behind every other tree of the tier
    lg.setColor(1, 1, 1, 1); lg.draw(wl.art.im, wl.x0 - ox, wl.y0)
  end
  for _, t in ipairs(TI.trunks) do                                   -- trunks
    if not t.art and not t.hasArt and t.x1 - ox > -20 and t.x0 - ox < 340 then
      local c = canopyOver(t)
      local top = c and math.floor((c.y0 + c.y1) / 2) or t.y0
      drawTrunk(t, math.min(top, t.y0), foot, ox, t.x1 - t.x0 >= 24)
    end
  end
  for _, c in ipairs(TI.canopies) do                                 -- canopies, over the trunks' tops
    local inside = false                                             -- (one inside an art tree's crown: its leaves)
    for _, a in ipairs(AT) do if c.x0 >= a.x0 and c.x1 <= a.x1 then inside = true end end
    CANOPY_SKIP = AT                                                 -- (review 5 Nov: no old crown overlaps a new one)
    if not inside and c.x1 - ox > -120 and c.x0 - ox < 440 then drawCanopy(c, ox, T) end
    CANOPY_SKIP = nil
  end
  for p, r in pairs(TI.role) do                                      -- (night 6 Nov, cp) the low bough's trunk again, from
    if r == "lowbough" and p.x1 - ox > -60 and p.x0 - ox < 380 then  -- under the bough down, over the canopy that hid it:
      local t = trunkOf(TI, p)                                        -- the bough grows out of a trunk seen to the ground,
      if t and not t.art and not t.hasArt then
        drawTrunk(t, p.y0 - 24, foot, ox, t.x1 - t.x0 >= 24)         -- (it runs on 24 px over the bough, and the canopy's
        local sx0, sy0 = lg.transformPoint(t.x0 - ox - 20, 0)          -- leaves are laid again over that top, so the trunk
        local sx1, sy1 = lg.transformPoint(t.x1 - ox + 20, p.y0 - 10)  -- goes up into the crown and the bough branches off)
        if sy1 > 0 and sx1 > 0 and sx0 < 320 then
          lg.setScissor(math.max(0, math.floor(sx0)), 0, math.max(1, math.floor(sx1 - math.max(0, sx0))), math.floor(sy1))
          for _, c in ipairs(TI.canopies) do
            if c.x0 <= t.x1 and c.x1 >= t.x0 and c.y1 >= p.y0 - 30 then CANOPY_SKIP = AT; drawCanopy(c, ox, T); CANOPY_SKIP = nil end
          end
          lg.setScissor()
        end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
  for _, a in ipairs(AT) do                                          -- the art trees, over the canopies
    local im = treeArtImg(a.name)
    if a.x1 - ox > -10 and a.x0 - ox < 330 then lg.draw(im.im, a.x0 - ox, foot - 9 - im.h) end
  end
  for p, r in pairs(TI.role) do                                      -- posts and legs
    if p.x1 - ox > -20 and p.x0 - ox < 340 then
      if r == "walk" then drawWalkLegs(p, ox, foot, world)
      elseif r == "slat" then drawSlatPosts(p, ox, foot)
      elseif r == "towerpost" then drawTowerPost(p, ox, foot, TI.postTop and TI.postTop[p]) end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- a prop of the tier (drawPropArt): true if it is one (drawn here, or as decoration by Sc.drawTreetops)
local function drawTierProp(p, camx, def)
  local TI = tier(def)
  CPB_TI = TI or nil                                                -- (6 Nov) the climbing parts look up trunks and ledges
  local r = TI and TI.role[p]
  if not r then return false end
  local ox = math.floor(camx)
  if r == "nest" then drawNest(p, ox)
  elseif r == "walk" then drawWalk(p, ox)
  elseif r == "slat" then drawSlat(p, ox)
  elseif r == "deck" then drawDeck(p, ox)
  elseif r == "lowbough" then drawLowBough(p, (trunkOf(TI, p)), ox)
  elseif r == "branch" and built(p, "landing") then                -- (art/cp-audit-06nov) a walk's landing in its
    local li, lx, ly = built(p, "landing")                          -- tree: one deck with the walk (cp_built.lua)
    lg.setColor(1, 1, 1, 1); lg.draw(li, lx - ox, ly)
  elseif r == "branch" then
    local t = trunkOf(TI, p)
    if t and t.x0 < p.x1 and t.x1 > p.x0 then drawFork(p, t, ox)
    elseif t then drawBranch(p, t, camx)
    else drawFork(p, { x0 = p.x0, x1 = p.x1 }, ox) end
  end
  lg.setColor(1, 1, 1, 1)
  return true
end

-- a stepping stone's reflection (art/cp-pond-06nov): under the waterline wy, a dark copy of the rock's lower
-- outline, narrowing and breaking up row by row, each row swaying 1 px on its own (as the water's rows do). Flat
-- colours of the pond's own deep water, no alpha, no dither. x, w: the rock's art (its outline included).
local REFL = { hex("2f5568"), hex("3d6878") }
function Sc.stoneReflection(x, wy, w, t)
  for i = 0, 6 do
    if i < 4 or i % 2 == 0 then
      local inset = 1 + math.floor(i * 0.7) + (i == 0 and 0 or 1)
      local sway = math.floor(math.sin(t * 2.1 + i * 1.3) * 1.2 + 0.5)
      local c = i < 3 and REFL[1] or REFL[2]
      lg.setColor(c)
      if i >= 3 then                                                  -- the lower rows break into two dashes
        local half = math.floor((w - 2 * inset) / 2)
        lg.rectangle("fill", x + inset + sway, wy + i, half - 2, 1)
        lg.rectangle("fill", x + inset + half + 1 + sway, wy + i, w - 2 * inset - half - 1, 1)
      else
        lg.rectangle("fill", x + inset + sway, wy + i, w - 2 * inset, 1)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- (art/cp-audit-06nov) the ripple ring where a stepping stone stands in the water: the ring's two ends out past the
-- rock's sides on the waterline row (wy - 1, behind it the rock hides the far half), its near half a light line along
-- the row under the rock (wy), broken in two places that drift 1 px with the water. The water art's lightest colour.
function Sc.stoneRipple(x, wy, w, t)
  local s = math.floor(math.sin(t * 1.7) * 1.2 + 0.5)
  lg.setColor(BANK.rip)
  lg.rectangle("fill", x - 4 + s, wy - 1, 3, 1); lg.rectangle("fill", x + w + 1 + s, wy - 1, 3, 1)
  local a, b = x + 3 + s, x + w - 4 + s                            -- the near half: three dashes
  local third = math.floor((b - a) / 3)
  lg.rectangle("fill", x - 2 + s, wy, a - (x - 2 + s), 1)
  lg.rectangle("fill", a + 2, wy, third - 2, 1)
  lg.rectangle("fill", a + third + 2, wy, b - (a + third + 2), 1)
  lg.rectangle("fill", b + 2, wy, (x + w + 2 + s) - (b + 2), 1)
  lg.setColor(1, 1, 1, 1)
end

-- one prop of an art level. kicked: a leaf pile Pepper has run through.
function Sc.drawPropArt(p, camx, def, kicked)
  local style = def.art
  local T, A = Sc.townArt(style), Sc.art()
  local x, w = p.x0 - camx, p.x1 - p.x0
  if x > 360 or x + w < -120 then return end
  if p.layer == "front" then                                      -- the foreground frame: below Pepper's lines only
    -- (art/dt-audit-06nov) the tall Downtown: no bollard in front of the quay wall (only its top showed, a black
    -- dome in the wall); a drain arch in the wall instead (arthooks.lua H.drawQuayDrains)
    if style == "town" and def.foot then return end
    local im = style == "park" and T.bush or T.bollard
    at(im, x + w / 2 - im:getWidth() / 2, math.max(221 + dy(), p.y0))
    return
  end
  local n = p.name
  if p.hidden then return end
  if style == "park" and def.foot and drawTierProp(p, camx, def) then return end   -- the treetop tier (tall parks)
  local d = dy()                                                  -- (the art's fixed lines follow the path line)
  if style == "town" and def.foot and (package.loaded.arthooks or require("arthooks")).townPiece(p, camx, def) then return end   -- the
  -- tall Downtown's roofs, fronts and spire (r8/levels: arthooks.lua, its art when it lands, else drawn in code)
  if not n or n == "" then
    if style == "park" and underCrown(def, p) then drawBough(p, camx, underCrown(def, p), def); return end
    local o = owner(def, p)
    if p.kind == "decor" or not o then return end                 -- posts, legs, crowns: drawn with their set piece
    n = o.name
    if style == "park" and (n == "OAK" or n == "BRANCH") then drawBranch(p, named(def, "OAK"), camx); return end
    -- the old oak's ledge at y 248 (x 1656-1720), left of its trunk: its nearest named prop is the crown's, which draws
    -- nothing for it, so Pepper stood on nothing (plan decision 8 c). A branch of the oak, as its others are. A ledge
    -- Pepper uses is never removed: the oak's lower branches lead up to it.
    if style == "park" and n == "CROWN" and p.kind == "oneway" and def.foot and p.y0 > def.foot - 90 then
      local oak = named(def, "OAK")
      if oak and p.x1 >= oak.x0 - 12 and p.x0 < oak.x1 then drawBranch(p, oak, camx); return end
    end
    if style == "park" and (n == "SLIDE" or n == "PLAY TOWER") and p.kind == "oneway" then drawDeck(p, math.floor(camx)); return end   -- (art/placement: was invisible)
    if n ~= "CRATES" then return end                              -- the hat (statue), the frame's top bar (FRAME)
  end
  if style == "park" then
    if n == "GATE" then at(T.gate, x, 175 + d - T.gate:getHeight())
    elseif n == "LEAVES" then
      local im = kicked and T.leaves_flat or T.leaves
      at(im, x + w / 2 - im:getWidth() / 2, p.y1 - im:getHeight())
    elseif n == "LOG" then shadowUnder(p, camx); at(T.log, x, p.y0 - 4)
    elseif n == "STUMP" then                                      -- a tree stump (r6/levels: the tall City Park's
      shadowUnder(p, camx)                                        -- practice ledge), drawn in code: bark, a cut top
      local A = cpb()
      if A then                                                   -- (6 Nov) the art: its body over the box, its cut top
        at(A.stump, math.floor(x) - A.D.stump.body0, p.y0 - 1)   -- the box's top row, its ink on the path line
        return
      end
      local sx, sy, sw, sh = math.floor(x), p.y0, w, p.y1 - p.y0
      lg.setColor(INK); lg.rectangle("fill", sx - 1, sy - 1, sw + 2, sh + 1)
      lg.setColor(0.42, 0.26, 0.14); lg.rectangle("fill", sx, sy + 3, sw, sh - 3)
      lg.setColor(0.33, 0.20, 0.11); for i = 3, sw - 3, 5 do lg.rectangle("fill", sx + i, sy + 5, 1, sh - 7) end
      lg.setColor(0.86, 0.66, 0.40); lg.rectangle("fill", sx, sy, sw, 3)
      lg.setColor(0.70, 0.50, 0.28); lg.rectangle("fill", sx + 4, sy + 1, sw - 8, 1)
      lg.setColor(1, 1, 1, 1)
    elseif n == "BENCH" then Sc.shadow(x + w / 2, 183 + d, w + 10, 5); at(A.bench, x - 3, 184 + d - A.bench:getHeight())
    elseif n == "HEDGE" then Sc.shadow(x + w / 2, 183 + d, w + 4, 5); at(T.hedge, x + math.floor((w - T.hedge:getWidth()) / 2), p.y0)   -- (6 Nov: 66 px art, its outline 1 px outside the box each side)
    elseif n == "STONE" then
      -- (art/cp-pond-06nov, the owner: "this thing looks weird") a stepping stone is the top of a rock standing out
      -- of the water: its art (26 x 21, tools/fix_cp_pond.py) ends at the waterline, its last row the pond's dark
      -- edge row, cut there if the water is higher; under it only a dark reflection, wobbling. It filled its box
      -- down to the bottom of the world under a see-through wash: a grey glass pillar. The box is unchanged.
      local wy
      for _, q in ipairs(Sc.pondPools or {}) do
        if q.x0 < p.x1 and q.x1 > p.x0 and q.y0 > p.y0 and q.y0 < p.y1 then wy = q.y0 end
      end
      if wy then
        local sw, sh = T.stone:getDimensions()
        local rows = math.min(sh, wy - (p.y0 - 1))
        if not T.stoneQ or T.stoneQ.rows ~= rows then T.stoneQ = { q = lg.newQuad(0, 0, sw, rows, sw, sh), rows = rows } end
        lg.setColor(1, 1, 1, 1); lg.draw(T.stone, T.stoneQ.q, math.floor(x) - 1, p.y0 - 1)
        Sc.stoneReflection(math.floor(x) - 1, wy + 1, sw, Sc.pondT or 0)
        Sc.stoneRipple(math.floor(x) - 1, wy, sw, Sc.pondT or 0)
      else at(T.stone, x - 1, p.y0 - 1) end                         -- (on dry ground: the rock on its box, as before)
    elseif n == "BIN" then shadowUnder(p, camx); at(A.bin, x - 1, 184 + d - A.bin:getHeight())
    elseif n == "PICNIC TABLE" then shadowUnder(p, camx); at(T.table, x, p.y0)
    elseif n == "OAK" then if not Sc.oakHasArt(def) then at(T.oak, x + w / 2 - 94, 175 + d - T.oak:getHeight()) end
    elseif n == "BRANCH" then drawBranch(p, named(def, "OAK"), camx)
    elseif n == "SLIDE" or n == "FRAME" then
      if n == "FRAME" then at(T.frame, x - 1, 119 + d) end            -- (the slide: Sc.drawTerrainArt, over the path)
    elseif n == "SWINGS" then at(T.swings, x + w / 2 - T.swings:getWidth() / 2, 175 + d - T.swings:getHeight())
    elseif n == "WILLOWS" then                                    -- all three willows (decoration, base y 174)
      for i, c in ipairs(Sc.bigWillow(def) and {} or willowCrowns(def)) do   -- (the tall level's big willow: Sc.drawTreetops)
        local im = c.y1 < 120 + d and T.willow_tall or T.willow
        local cx = math.floor((c.x0 + c.x1) / 2 - camx)
        lg.setColor(1, 1, 1, 1)
        if i % 2 == 0 then lg.draw(im, cx + 33, 175 + d - im:getHeight(), 0, -1, 1) else lg.draw(im, cx - 32, 175 + d - im:getHeight()) end
      end
    elseif n == "WINCH" then                                       -- the second keeper at the duck boat's winch
      if not T.keeperWinch then                                   -- (art/scene/park_keeper_winch.png, 8 x 80 px,
        T.keeperWinch = fadeImg("park_keeper_winch", 0.35)       -- made facing right, drawn mirrored so the winch
        T.keeperWinchQ = {}                                       -- faces the pond; drum middle x 60, feet y 79;
                                                                  -- decoration on the back layer: faded 35 %, art/fixes)
        for i = 1, 8 do T.keeperWinchQ[i] = lg.newQuad((i - 1) * 80, 0, 80, 80, T.keeperWinch:getDimensions()) end
      end
      -- (art/cp-audit-06nov) the audit: "he grips a barrow that is not there, a tan blob cut behind the bridge post".
      -- The winch's left post and half its drum stood behind the treetop walk's right pylon (x 944-950): what showed
      -- was a pale drum end and the crank, with no frame. Drawn WINCH_DX px to the right, the whole winch (both posts,
      -- the drum, the crank he turns) stands clear beside the pylon, his back foot still clear of the lamp at 1028.
      lg.setColor(1, 1, 1, 1)
      lg.draw(T.keeperWinch, T.keeperWinchQ[Sc.winchFrame or 1], math.floor(x + w / 2) + Sc.WINCH_DX, 174 + d, 0, -1, 1, 60, 79)
    else Sc.drawProp(p, camx, C.prop) end
  else
    if n == "DOOR" then at(T.door, x, 175 + d - T.door:getHeight())
    elseif n == "CRATES" then                                     -- a stack of apple crates, 16 px each
      -- (art/dt-audit-06nov) a stack whose box runs on below the street (x 2624, down to the world's bottom: the
      -- quay's end) stands on the street: crates only above it, the quay wall below (the box is unchanged)
      local y1 = (def.foot and p.y1 > def.foot and p.y0 < def.foot) and def.foot or p.y1
      local k = math.max(1, math.floor((y1 - p.y0) / 16 + 0.5))
      shadowUnder({ x0 = p.x0, x1 = p.x1, y1 = y1 }, camx)
      local cr = T.crates[w]                                      -- (art/dt-props-06nov) the box's own width: 15 rows
      if cr then                                                  -- of crate, its ink shared with the crate above,
        local FILL = { false, "pears", false, "bread", false, false, "cloth" }   -- (final review: the crates repeat)
        for i = 1, k do                                           -- the apples' tops 3 rows over its rim; some crates
          local f = FILL[(math.floor(p.x0 / 16) * 3 + i * 5) % #FILL + 1]   -- hold pears or bread, or are empty
          local v = f and T.crateFills and T.crateFills[f] and T.crateFills[f][w .. "_" .. f]   -- under a cloth
          at(v or cr, x - 1, y1 - 16 * i - 5)
        end
      else
        for i = 1, k do at(T.crate, x, y1 - 16 * i - 12) end
      end
    elseif n == "TABLE" then Sc.shadow(x + w / 2, 183 + d, w + 4, 5); at(T.table, x - 1, p.y0)
    elseif n == "PARASOL" then
      local tb                                                     -- its pole, down to the table under it
      for _, q in ipairs(def.props) do if q.name == "TABLE" and q.x0 >= p.x0 and q.x1 <= p.x1 then tb = q end end
      local px = math.floor(x + w / 2) - 1
      local foot = tb and tb.y0 or 240 + d                        -- (no table: a pole standing in the water)
      if not tb and Sc.world then                                 -- (art/dt-props-06nov) on the pavement it stands on
        local wet = false                                         -- the street, it does not run through it
        for _, r in ipairs(Sc.world.water or {}) do if p.x0 + w / 2 >= r.x0 and p.x0 + w / 2 < r.x1 then wet = true end end
        if not wet then foot = 184 + d end
      end
      -- (night/06nov-dt, review round 1: the audit's 1.1 m boats were toys and read as a floor over deadly water)
      -- over the flooded square the pole goes into the water: a dark wet band where it meets the surface, a ripple
      -- ring, under the surface the pole and its heavy cast-iron foot seen through the water, one step darker
      local wl
      if not tb and def.foot and Sc.world then
        for _, r in ipairs(Sc.world.water or {}) do
          local wx = p.x0 + w / 2                                 -- (world x: px is on screen)
          if wx >= r.x0 and wx < r.x1 then wl = math.min(wl or 1e9, r.y0) end
        end
      end
      local top = wl and math.min(foot, wl) or foot
      lg.setColor(INK); lg.rectangle("fill", px - 1, p.y1, 4, top - p.y1)
      lg.setColor(0.55, 0.57, 0.6); lg.rectangle("fill", px, p.y1, 2, top - p.y1)
      lg.setColor(0.72, 0.74, 0.77); lg.rectangle("fill", px, p.y1, 1, top - p.y1)   -- its lit left edge
      if wl and foot > wl then
        local bot = 240 + d
        lg.setColor(0.17, 0.30, 0.44); lg.rectangle("fill", px - 1, wl, 4, bot - wl)        -- under the water
        lg.setColor(0.27, 0.42, 0.56); lg.rectangle("fill", px, wl, 2, bot - wl)
        lg.setColor(0.17, 0.30, 0.44); lg.rectangle("fill", px - 7, bot - 6, 16, 6)          -- its foot, a cast slab
        lg.setColor(0.27, 0.42, 0.56); lg.rectangle("fill", px - 6, bot - 5, 14, 1)
        lg.setColor(0.30, 0.31, 0.33); lg.rectangle("fill", px - 1, wl - 2, 4, 2)            -- the wet band
        local k = math.floor((Sc.pondT or 0) * 3) % 2                                        -- the ripple ring
        lg.setColor(0.78, 0.89, 0.96)
        lg.rectangle("fill", px - 6 - k, wl + 1, 4, 1); lg.rectangle("fill", px + 4 + k, wl + 1, 4, 1)
        lg.rectangle("fill", px - 3, wl + 3, 2, 1); lg.rectangle("fill", px + 3, wl + 3, 2, 1)
      end
      local sq = (p.squashT or 0) > 0 and 2 or 0                  -- a springy one dips as it launches her
      if T.parasols[w] then at(T.parasols[w], x - 1, p.y0 - 1 + sq)   -- (the box's own width, ink round it)
      else at(T.parasol, x, p.y0 - 1 + sq) end
      if p.bounce then                                            -- (review 6 Nov: the red coil block read as a
        local sx, sy = px + 1, p.y0 + 12 + sq                     -- box on the pole) a steel coil spring wound round
        local sh = math.min(10 - sq, foot - sy)                   -- the pole under the canopy's valance: ink, steel
        lg.setColor(INK); lg.rectangle("fill", sx - 3, sy, 7, sh) -- turns lit on their top
        for yy = sy + 1, sy + sh - 2, 3 do
          lg.setColor(0.62, 0.65, 0.70); lg.rectangle("fill", sx - 2, yy, 5, 2)
          lg.setColor(0.86, 0.88, 0.91); lg.rectangle("fill", sx - 2, yy, 5, 1)
        end
      end
    elseif n == "SIGN" then at(T.shopsign, x - 1, p.y0 - 6)
    elseif n == "STALL" then shadowUnder(p, camx); at(T.stall, x - 1, p.y0 - 15)
    elseif n == "AWNING" then
      local posts = {}
      for _, q in ipairs(def.props) do                            -- its posts (thin decoration boxes under it)
        if q.kind == "decor" and q.x1 - q.x0 <= 6 and q.y0 == p.y0 and q.x0 >= p.x0 - 2 and q.x1 <= p.x1 + 2 then
          posts[#posts + 1] = { x0 = q.x0, x1 = q.x1, y0 = q.y0, y1 = q.y1 }
        end
      end
      -- (art/dt-audit-06nov) a street awning is a market stall: a lone post gets its pair at the other end (x 872:
      -- one post, the cloth hung from nothing), and a stall counter stands between the posts (decoration, drawn in
      -- code: a pine top, a green planked front; no ink, its edges a darker shade). Not under the STALL's own awning.
      local street = def.foot and style == "town" and p.y0 > def.foot - 80
      if street and #posts == 1 then
        local q = posts[1]
        local mx = (q.x0 - p.x0 < p.x1 - q.x1) and (p.x1 - (q.x0 - p.x0) - (q.x1 - q.x0)) or (p.x0 + (p.x1 - q.x1))
        posts[2] = { x0 = mx, x1 = mx + q.x1 - q.x0, y0 = q.y0, y1 = q.y1 }
      end
      local stall = false
      for _, q in ipairs(def.props) do if q.name == "STALL" and q.x0 < p.x1 and q.x1 > p.x0 then stall = true end end
      if street and #posts == 2 and not stall then
        local a, b = math.min(posts[1].x1, posts[2].x1), math.max(posts[1].x0, posts[2].x0)
        local cx0, cw, top = math.floor(a - camx), b - a, def.foot - 30
        lg.setColor(0.32, 0.22, 0.14); lg.rectangle("fill", cx0, top, cw, 30)          -- the counter's shade
        lg.setColor(0.24, 0.41, 0.34); lg.rectangle("fill", cx0, top + 4, cw - 1, 25)  -- the green planked front
        lg.setColor(0.19, 0.33, 0.27)
        for k = 6, cw - 3, 6 do lg.rectangle("fill", cx0 + k, top + 5, 1, 24) end     -- plank joints
        lg.setColor(0.32, 0.51, 0.43); lg.rectangle("fill", cx0, top + 4, 1, 25)      -- its lit left edge
        lg.setColor(0.50, 0.35, 0.21); lg.rectangle("fill", cx0, top, cw, 3)           -- the pine counter top
        lg.setColor(0.65, 0.47, 0.30); lg.rectangle("fill", cx0, top, cw, 1)
        lg.setColor(0.32, 0.22, 0.14); lg.rectangle("fill", cx0, top + 3, cw, 1)       -- its shadow line
      end
      for _, q in ipairs(posts) do
        local qx = math.floor(q.x0 - camx)
        lg.setColor(INK); lg.rectangle("fill", qx - 1, q.y0, q.x1 - q.x0 + 2, q.y1 - q.y0)
        lg.setColor(0.42, 0.29, 0.18); lg.rectangle("fill", qx, q.y0, q.x1 - q.x0, q.y1 - q.y0)
        lg.setColor(0.58, 0.42, 0.27); lg.rectangle("fill", qx, q.y0, 1, q.y1 - q.y0)
      end
      local im = w >= 72 and T.awning80 or T.awning64
      local sq = (p.squashT or 0) > 0 and 2 or 0                  -- a springy one dips as it launches her
      if def.foot and p.y0 < def.foot - 120 and p.y0 - 268 > 0 and p.y0 - 268 <= 10 then   -- (night/06nov-dt) on the
        local ax = math.floor(x + w / 2 - im:getWidth() / 2)     -- high road: hung from the ground floor's cornice
        for _, bx in ipairs({ ax + 3, ax + im:getWidth() - 6 }) do   -- (y 262-268) on two iron hangers
          lg.setColor(INK); lg.rectangle("fill", bx, 267, 3, p.y0 - 267)
          lg.setColor(0.45, 0.48, 0.52); lg.rectangle("fill", bx + 1, 267, 1, p.y0 - 268)
        end
      end
      at(im, x + w / 2 - im:getWidth() / 2, p.y0 - 1 + sq)
      if p.bounce then                                            -- springs on top of its posts: it is springy
        for _, q in ipairs(def.props) do
          if q.kind == "decor" and q.x1 - q.x0 <= 6 and q.y0 == p.y0 and q.x0 >= p.x0 - 2 and q.x1 <= p.x1 + 2 then
            Sc.spring(math.floor((q.x0 + q.x1) / 2 - camx), p.y1 + sq, 9 - sq)
          end
        end
      end
    elseif n == "GATE" or n == "TRAM SHED" then Sc.courtyardGate(p, camx)
    elseif n == "STATUE" then at(T.statue, x - 1, p.y0 - 4)
    elseif n == "PEDESTAL" then                                   -- (art/dt-props-06nov: the plinth is the box + its
      shadowUnder(p, camx)                                        -- ink, at x0 - 1, y0 - 1; the old one was the box)
      if T.pedestal:getWidth() == w + 2 then at(T.pedestal, x - 1, p.y0 - 1) else at(T.pedestal, x, p.y0) end
    elseif n == "ARM" then return
    elseif n == "RIM" then
      at(T.rim, x - 1, p.y0 - 1)
    elseif n == "FOUNTAIN" then
      at(T.bowl, x - 1, p.y0 - 1)
      local bs = def.foot and optImg("town_basin")                    -- (night/06nov-dt) the basin front-on: far coping,
      local r0, r1                                                    -- the water band, the near kerb over the pit
      for _, q in ipairs(def.props) do
        if q.name == "RIM" and q.x1 <= p.x0 and (not r0 or q.x1 > r0.x1) then r0 = q end
        if q.name == "RIM" and q.x0 >= p.x1 and (not r1 or q.x0 < r1.x0) then r1 = q end
      end
      if bs and r0 and r1 and r1.x0 - r0.x1 == bs:getWidth() then
        lg.setColor(1, 1, 1, 1); lg.draw(bs, math.floor(r0.x1 - camx), def.foot - 12)
        local t = Sc.pondT or 0                                       -- the band's ripples drift
        lg.setColor(0.59, 0.73, 0.81)
        for k = 0, 3 do
          local sx = math.floor(r0.x1 - camx + ((k * 29 + t * 6) % (r1.x0 - r0.x1 - 6)))
          lg.rectangle("fill", sx, def.foot - 5, 4, 1)
        end
        local tier = named(def, "TIER")                               -- the jets' splashes on the band (final review:
        if tier then                                                  -- a crown of drops over the water, a ring on it)
          local k = math.floor(t * 8) % 2
          local y = def.foot - 8
          for _, jx in ipairs({ tier.x0 - 5, tier.x1 + 4 }) do
            local sx = math.floor(jx - camx)
            lg.setColor(0.78, 0.88, 0.95)                             -- the ring on the band
            lg.rectangle("fill", sx - 5 - k, y, 4, 1); lg.rectangle("fill", sx + 3 + k, y, 4, 1)
            lg.rectangle("fill", sx - 2, y + 1, 6, 1)
            lg.setColor(0.96, 0.98, 1.0)                              -- the crown and its drops
            lg.rectangle("fill", sx - 1, y - 2, 4, 2)
            lg.rectangle("fill", sx - 2 - k, y - 4, 1, 1); lg.rectangle("fill", sx + 3 + k, y - 4, 1, 1)
            lg.rectangle("fill", sx - 3 - k, y - 6 + k, 1, 1); lg.rectangle("fill", sx + 4 + k, y - 6 + k, 1, 1)
          end
        end
      else
      lg.setColor(0.33, 0.47, 0.52, 0.45); lg.rectangle("fill", math.floor(x) + 8, 193 + d, w - 16, 47)
      end
    elseif n == "KIOSK" then shadowUnder(p, camx); at(T.kiosk, x - 1, p.y0 - 1)
    elseif n == "SHELTER" then shadowUnder({ x0 = p.x0, x1 = p.x1, y1 = 184 + d }, camx); at(T.shelter, x, p.y0)
    elseif n == "RIVER" then at(T.sign, x + w / 2 - T.sign:getWidth() / 2, 175 + d - T.sign:getHeight())
    elseif n == "TUB" then shadowUnder(p, camx); at(T.tub, x, p.y1 - T.tub:getHeight())   -- (the tub is the box, the
                                                                  -- plant over it: art/dt-props-06nov, a taller shrub)
    elseif n == "HOUSE" then                                      -- faded decoration; their balconies are the ledges
      local im = T["house" .. ((houseIndex(def, p) - 1) % 3 + 1)]
      at(im, x + w / 2 - im:getWidth() / 2, 175 + d - im:getHeight())
    elseif n == "BALCONY" then drawBalcony(p, camx)
    elseif n == "TIER" then at(T.tier, x - 1, p.y0 - 1)
    else Sc.drawProp(p, camx, C.prop) end
  end
  lg.setColor(1, 1, 1, 1)
end

-- (art/dt-roofs-06nov) the fountain's falling water, built (tools/build_dt_details.py): art/scene/town_jet.png, frames of
-- 6 px side by side; false when it is not there (the drops in code)
local JET
function Sc.townJet()
  if JET == nil then
    JET = false
    local im = optImg("town_jet")
    if im then
      local w, h = im:getDimensions()
      JET = { im = im, q = {}, fw = math.floor(w / 4) }             -- (night/06nov-dt: 4 frames of 10, was 6)
      for i = 0, 3 do JET.q[i + 1] = lg.newQuad(i * JET.fw, 0, JET.fw, h, w, h) end
    end
  end
  return JET
end
-- terrain set pieces drawn over the path (after the ground): City Park's slide, Downtown's fountain spout and jets
-- (night 6 Nov, cp track; concept a) the path's end at a park pond: a grassy shoulder instead of a sawn cut. The
-- path band (its rows from the back edge + 1 to its front edge) ends 4 px before the water in a rounded corner, and
-- the corner is the lawn (its lit lip along the curve); the bank's face under it, the last 3 columns, is grass down
-- to the shore's damp and wet earth, the outer column a shade darker (no ink: decoration). Pepper's edge and the
-- boxes are unchanged (she walks on to the edge on the grass); drawn after the ground, before her.
function Sc.drawPondShoulders(world, camx)
  local ox = math.floor(camx)
  local yt, yf = Sc.FOOT - 3, Sc.FOOT + 16                         -- the path band's first and last rows (ground rows 9-28)
  local LIP, LAWN, DK = BANK.lip, BANK.lawn, hex("7d7834")
  local function px(x, y, c) lg.setColor(c); lg.rectangle("fill", x - ox, y, 1, 1) end
  for _, p in ipairs(pools(world)) do
    if p.x1 - ox > -16 and p.x0 - ox < 336 then
      local wt = p.y0 - Sc.POND_RISE
      for _, e in ipairs({ { p.x0 - 1, -1 }, { p.x1, 1 } }) do      -- the solid column next to the water, then outwards
        for d = 0, 12 do
          local x = e[1] + e[2] * d
          local top = yt                                              -- the grass's top row in this column
          if d > 4 then top = yf - math.floor((yf - yt) * math.sqrt(math.max(0, 1 - ((d - 4) / 8) ^ 2)) + 0.5) end
          if top <= yf then
            for y = top, yf do px(x, y, y == top and LIP or LAWN) end
            if (x % 3 == 0) and top > yt then px(x, top - 1, LAWN) end   -- a tuft over the curve
          end
          if d < 3 then                                                -- the bank's face down to the shore
            for y = yf + 1, wt + 6 do
              local c = y < wt + 1 and LAWN or (y < wt + 3 and BANK.damp or (y < wt + 5 and BANK.wet or BANK.foot))
              if d == 0 and y >= wt + 1 then c = BANK.foot end            -- (round 1: no dark outer column)
              px(x, y, c)
            end
          end
        end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
-- (night 6 Nov, cp fix round 1; review: "the feet look sawn off at the lawn") the art trees' feet, after the ground:
-- the lawn strip (the path's back edge) is painted over their last rows, so the trunk ended in a cut on the lawn's top.
-- Their last 3 rows are drawn again over the lawn, roots spread 1 to 3 px past the foot each side, and 2 dark base
-- rows (the bark's darkest, as faded, and a lighter one) sit in the lawn under them.
local FOOTC = {}
function Sc.drawTreeFeet(def, camx)
  local TI = def.foot and tier(def)
  if not TI then return end
  if not FOOTC[Look.key] then FOOTC[Look.key] = { Sc.fadeC(hex("3b2620"), TREE_FADE), Sc.fadeC(hex("5a3a2a"), TREE_FADE), Sc.fadeC(hex("7a5236"), TREE_FADE) } end
  local FC, ox, foot = FOOTC[Look.key], math.floor(camx), TI.foot
  for _, a in ipairs(treeArt(def, TI)) do
    local im = treeArtImg(a.name)
    local r                                                           -- the foot's widest of its last 4 rows
    for y = im and im.h - 4 or 0, im and im.h - 1 or -1 do
      local q = im.rows[y]
      if q and (not r or q[2] - q[1] > r[2] - r[1]) then r = q end
    end
    if r and a.x1 - ox > -10 and a.x0 - ox < 330 then
      local yb = foot - 10                                            -- the art's last row
      lg.setColor(1, 1, 1, 1)
      lg.draw(im.im, cpbQuad(im.im, 0, im.h - 3, im.w, 3), a.x0 - ox, yb - 2)
      local x0, x1 = a.x0 + r[1] - ox, a.x0 + r[2] - ox
      for k = 1, 3 do
        lg.setColor(k == 3 and FC[2] or FC[3])
        lg.rectangle("fill", x0 - k, yb - 3 + k, k, 1); lg.rectangle("fill", x1 + 1, yb - 3 + k, k, 1)
      end
      lg.setColor(FC[1]); lg.rectangle("fill", x0 - 3, yb + 1, x1 - x0 + 7, 1)
      lg.setColor(FC[2]); lg.rectangle("fill", x0 - 1, yb + 2, x1 - x0 + 3, 1)
      rootTufts(x0, x1, yb + 3)                                       -- (day/07nov-ground) grass over the foot's line
    end
  end
  lg.setColor(1, 1, 1, 1)
end
function Sc.drawTerrainArt(def, camx, t)
  local T = Sc.townArt(def.art)
  if def.art == "park" and Sc.world then Sc.drawPondShoulders(Sc.world, camx) end
  if def.art == "park" then Sc.drawTreeFeet(def, camx) end
  if def.art == "park" then
    local s = named(def, "SLIDE")
    if s and s.x1 - camx > -40 and s.x0 - camx < 360 then at(T.slide, s.x0 - camx - 1, s.y0 - 1) end
  else
    local f = named(def, "FOUNTAIN")
    if f and f.x1 - camx > -40 and f.x0 - camx < 360 then
      local cx = math.floor((f.x0 + f.x1) / 2 - camx)
      lg.setColor(1, 1, 1, 1)
      local A = Sc.art()
      local tier = named(def, "TIER")
      local jet = tier and Sc.townJet()
      if jet then                                                 -- (art/dt-roofs-06nov) town_jet.png: the built streams,
        local q = jet.q[math.floor(t * 20) % #jet.q + 1]          -- 4 frames, the right one mirrored
        local y = tier.y0 + 3
        lg.setColor(1, 1, 1, 1)
        local o = jet.fw == 6 and 7 or 10                         -- (the stream at the frame's x 5-6: x0 - 5 .. x0 - 4)
        lg.draw(jet.im, q, math.floor(tier.x0 - camx) - o, y); lg.draw(jet.im, q, math.floor(tier.x1 - camx) + o, y, 0, -1, 1)
      elseif tier then                                            -- water falls from the top tier's rims to the basin
        for i = 0, 7 do
          local k = (t * 1.1 + i / 8) % 1
          for _, e in ipairs({ { tier.x0 - camx, -1 }, { tier.x1 - camx, 1 } }) do
            lg.setColor(0.86, 0.94, 1, 0.85 - 0.4 * k)
            lg.rectangle("fill", math.floor(e[1] + e[2] * (1 + k * 4)), math.floor(tier.y0 + 4 + k * (190 + dy() - tier.y0 - 4)), 1, 2)
          end
        end
      else
        for i = 0, 5 do                                           -- water jets: two arcs of drops from the spout
          local k = ((t * 1.6 + i / 6) % 1)
          for _, dir in ipairs({ -1, 1 }) do
            local dx = dir * (2 + k * 13)
            local dy = -14 + 34 * (k - 0.35) ^ 2 * 2.2
            lg.setColor(0.86, 0.94, 1, 0.9 - 0.5 * k)
            lg.rectangle("fill", math.floor(cx + dx), math.floor(f.y0 - 10 + dy), 1, 2)
          end
        end
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end
function Sc.drawSpout(def, camx)
  if def.art ~= "town" or named(def, "TIER") then return end         -- (the top tier's column replaces it)
  local f = named(def, "FOUNTAIN")
  if f and f.x1 - camx > -40 and f.x0 - camx < 360 then
    local T = Sc.townArt("town")
    at(T.spout, (f.x0 + f.x1) / 2 - camx - 6, f.y0 - 12)
  end
end

-- code-drawn pieces (setpieces.lua) that have art in an art level: City Park's hollow log. Returns true if drawn.
function Sc.drawPieceArt(pc, camx, def)
  if def.art == "park" and pc.kind == "hollowlog" then
    local T = Sc.townArt("park")
    Sc.shadow((pc.x0 + pc.x1) / 2 - camx, (pc.foot or 184) - 1, pc.x1 - pc.x0 + 4, 5)   -- (on the path it lies on)
    at(T.hollowlog, pc.x0 - camx - 1, pc.y0 - 1)
    return true
  end
  return false
end

-- the duck boat (a mover): the duck faces the way it paddles; its hull sits in the pond
-- (6 Nov, art/cp-critters-06nov) art/scene/cp_duckboat.png (tools/build_duckboat.py; SpriteCook Pixel Engine at 1x):
-- a 2 m pedal boat at true scale (92 x 60, facing left), its gunwale (row 41, the ink) on the mover's top and the
-- mover's box on its cols 8-87 (the tall City Park's DUCK BOAT is 80 px wide); mirrored about the box when it
-- paddles right. The pond's surface is 7 px under the deck. Without the file: park_boat_front.png as before.
local duckImg, duckCol
function Sc.drawMoverArt(m, camx, style)
  if duckImg == nil then
    duckImg = false
    if love.filesystem.getInfo("art/scene/cp_duckboat.png") then
      local data = love.image.newImageData("art/scene/cp_duckboat.png")
      duckImg = newImg(data); duckCol = {}                        -- each column's opaque rows (top, bottom), for the
      for c = 0, data:getWidth() - 1 do                           -- water tint and the ripple: the hull's own shape
        local t, b
        for r = 0, data:getHeight() - 1 do
          local _, _, _, a = data:getPixel(c, r)
          if a > 0 then t = t or r; b = r end
        end
        duckCol[c] = t and { t, b } or false
      end
    end
  end
  local w = math.floor(m.x1 - m.x0 + 0.5)
  if duckImg and style == "park" and w >= 78 then                      -- (the flat City Park's 48 px boat keeps its art)
    local x0 = math.floor(m.x0 - camx + 0.5)
    local top = m.y0 - 41
    local flip = m.dir and m.dir > 0
    lg.setColor(1, 1, 1, 1)
    if flip then lg.draw(duckImg, x0 + w + 8, top, 0, -1, 1) else lg.draw(duckImg, x0 - 8, top) end
    -- (fix round 1) the water over the hull below the surface, and the ripple along the hull at the surface, column by
    -- column on the hull's own silhouette (a 92 px box stuck out past the hull's ends and read as glass)
    local d, ax = dy(), flip and x0 + w + 8 - 92 or x0 - 8
    local wr = 209 + d - top                                           -- the surface's row in the art
    for c = 0, 91 do
      local cr = duckCol[c]
      if cr and cr[2] >= wr then
        local sx = flip and ax + 91 - c or ax + c
        lg.setColor(0.33, 0.47, 0.52, 0.5); lg.rectangle("fill", sx, top + math.max(wr, cr[1]), 1, cr[2] - math.max(wr, cr[1]) + 1)
        if cr[1] < wr then lg.setColor(0.86, 0.94, 0.95, 0.8); lg.rectangle("fill", sx, top + wr - 1, 1, 1) end
      end
    end
    lg.setColor(1, 1, 1, 1)
    return
  end
  local T = Sc.townArt(style)
  local im = T.boat
  local iw = im:getWidth()
  -- (6 Nov, cp_props_06nov) the duck boat art: its deck (the hull's top ink row) is row DECK, the hull's middle column
  -- HC; the hull is centred on the mover's box both ways round. The old 54 x 33 art: deck 18, drawn 3 px left.
  local DECK, HC = 20, 30
  local cx = math.floor(m.x0 - camx + 0.5) + math.floor((m.x1 - m.x0) / 2)
  local x = cx - HC
  if iw == 54 then DECK, x = 18, math.floor(m.x0 - camx + 0.5) - 3 end
  lg.setColor(1, 1, 1, 1)
  if m.dir and m.dir > 0 then
    if iw ~= 54 then x = cx - (iw - 1 - HC) end
    lg.draw(im, x + iw, m.y0 - DECK, 0, -1, 1)
  else lg.draw(im, x, m.y0 - DECK) end
  local d = dy()
  lg.setColor(0.33, 0.47, 0.52, 0.5); lg.rectangle("fill", x, 209 + d, iw, m.y0 - DECK + im:getHeight() - 209 - d)
  lg.setColor(0.86, 0.94, 0.95, 0.8); lg.rectangle("fill", x + 2, 208 + d, im:getWidth() - 4, 1)   -- the ripple line
  lg.setColor(1, 1, 1, 1)
end

-- the hazards: the leaf cart (City Park) and the old toy-sized tram (Downtown before r8/levels; the cargo bike that
-- replaced it is drawn by arthooks.lua), wheels on the line, centred on the hit box
-- City Park: the park keeper pushes the leaf cart (art/scene/park_keeper_cart.png, 8 frames of 82 x 82, made facing
-- right and drawn mirrored; tools/build_keeper.py). The barrow's middle (x 58) is on the hit box's middle, the
-- feet and wheel on the line; the walk cycle steps with the distance he has covered, so his boots don't slide.
local keeperImg, keeperQ
local function keeperCart(c, camx)
  if not keeperImg then
    keeperImg = newImg("art/scene/park_keeper_cart.png"); keeperQ = {}
    for i = 1, 8 do keeperQ[i] = lg.newQuad((i - 1) * 82, 0, 82, 82, keeperImg:getDimensions()) end
  end
  local x = math.floor(c.x - camx + 0.5)
  Sc.shadow(x + 8, c.y - 1, 66)
  lg.setColor(1, 1, 1, 1)
  lg.draw(keeperImg, keeperQ[1 + math.floor(c.x / 5) % 8], x, math.floor(c.y + 0.5), 0, -1, 1, 58, 81)
end
function Sc.drawHazardArt(c, camx, style)
  if style == "park" then return keeperCart(c, camx) end
  local T = Sc.townArt(style)
  local im = style == "park" and T.cart or T.tram
  local x = c.x - camx
  Sc.shadow(x, c.y - 1, im:getWidth() - 6)
  lg.setColor(1, 1, 1, 1)
  local x0, y0 = math.floor(x - im:getWidth() / 2 + 0.5), math.floor(c.y - im:getHeight() + 0.5)
  -- they drive right to left: the tram's art faces left; the cart's faces right (its wheel leads), so it is mirrored
  if style == "park" then lg.draw(im, x0 + im:getWidth(), y0, 0, -1, 1) else lg.draw(im, x0, y0) end
end

return Sc
