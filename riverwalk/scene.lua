-- Scenery. Art in art/scene: far shore and bridge, bench, bin, pot, lamp post (riverwalk_scenery_v1), water (SpriteCook),
-- skyline, pavement, building, tree (trial). Everything else is still wireframe: plain boxes in a misty grey-blue per layer, lighter the
-- further back. Layers 2 to 5 scroll slower (parallax).
local F = require("bigfont")
local Look = require("look")
local Sc = {}
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
    local n = math.max(0, math.floor((w - lw - ew) / uw))
    d = love.image.newImageData(lw + n * uw + ew, rh)
    d:paste(l, 0, 0, 0, 0, lw, rh)
    for i = 0, n - 1 do d:paste(u, lw + i * uw, 0, 0, 0, uw, rh) end
    d:paste(en, lw + n * uw, 0, 0, 0, ew, rh)
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
  for _, n in ipairs({ "water", "skyline", "pavement", "road", "manhole", "drain" }) do A[n] = newImg("art/scene/" .. n .. ".png") end
  A.waterQ = {}                                                   -- one quad per row: each row of the river moves on its own
  for y = 0, A.water:getHeight() - 1 do A.waterQ[y] = lg.newQuad(0, y, A.water:getWidth(), 1, A.water:getDimensions()) end
  -- decoration (pot, lamp posts, the houses and trees) is faded the back amount towards the level's back haze, so it
  -- sits back and the obstacle course stands out. The files are untouched; this is done to a copy when the game loads.
  for _, n in ipairs({ "pot", "lamp_post", "building", "tree", "tree_near", "tree_far", "cafe", "gable" }) do
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
function Sc.magpie(m, camx, t)
  local x, y = math.floor(m.x - camx + 0.5), math.floor(m.y + 0.5)
  if x < -40 or x > 360 then return end
  local pose
  if m.state == "fly" then pose = (math.floor(t * 12) % 2 == 0) and MAGPIE.up or MAGPIE.down
  else pose = (math.floor(t * 0.8) % 3 == 0 and (t * 0.8) % 1 < 0.25) and MAGPIE.flick or MAGPIE.perch end
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
function Sc.paintGround(w, props)
  local art = Sc.art()
  local pave = art.pavement
  local pw, ph = pave:getDimensions()
  local q = {}
  for i = 0, pw - 1 do q[i] = lg.newQuad(i, 0, 1, ph, pw, ph) end
  local road = art.road                                             -- the road under the paving (tools/make_road.py)
  local rw, rh = road:getDimensions()
  local rq = {}
  for i = 0, rw - 1 do rq[i] = lg.newQuad(i, 0, 1, rh, rw, rh) end
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
          lg.draw(road, rq[x % rw], x, m[1] + 15)                   -- rows 27+ of the paving art are the road
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
function Sc.passageBack(p, camx)
  local x0, x1 = math.floor(p.x0 - camx), math.floor(p.x1 - camx)
  if x1 < -2 or x0 > 322 then return end
  lg.setColor(PASS1); lg.rectangle("fill", x0, p.y0, x1 - x0, p.y1 - p.y0)
  lg.setColor(PASS2); lg.rectangle("fill", x0, p.y1 - 14, x1 - x0, 6)
  for y = p.y1 - 15, p.y1 - 8, 2 do lg.rectangle("fill", x0, y, x1 - x0, 1) end
  lg.setColor(1, 1, 1, 1)
end
function Sc.passageFront(p, camx)
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
    for _, n in ipairs({ "swings", "oak", "willow", "willow_tall", "winch" }) do T[n] = fadeImg("park_" .. n) end
    T.gate = fadeImg("park_gate", 0.28)                           -- (its own amount: dark ironwork, ladder darkest 80)
    T.boat = img("park_boat_front")                               -- front-on (tools/make_front_view.py)
    T.table = img("park_table_front")                             -- front-on (tools/make_table_front.py)
  else
    for _, n in ipairs({ "ground", "crate", "parasol", "table", "stall", "awning80", "awning64", "statue", "pedestal", "tram", "shelter", "kiosk", "shopsign", "rim", "bowl", "bollard", "tub", "tier" }) do T[n] = img("town_" .. n) end
    -- the plaza houses are decoration on the back layer: faded like the rest of it (art/fixes, owner decision 4;
    -- their balconies are separate play ledges, drawn in code)
    for _, n in ipairs({ "door", "sign", "spout", "house1", "house2", "house3" }) do T[n] = fadeImg("town_" .. n) end
    T.crate, T.table = img("town_crate_front"), img("town_table_front")   -- front-on (tools/make_front_view.py)
    T.tramshed = { [70] = img("town_tramshed70"), [96] = img("town_tramshed96") }   -- SpriteCook (tools/import_assets_v2.py)
    -- the two far layers sit further back than the back-edge decoration, each faded to its layer's haze (the
    -- script's shore and mid amounts), so the street's obstacles and the climbable houses stand out against them
    -- (r8/levels: art/scene/town_row.png, the row of old town houses across the square with volume, replaces
    -- town_facades.png when it is there: the same layer, a strip that repeats, standing on y 178)
    T.facades = fadeImg(love.filesystem.getInfo("art/scene/town_row.png") and "town_row" or "town_facades", nil, "mid")
    T.roofs = fadeImg("town_roofs", nil, "shore")
  end
  T.groundQ = colQuads(T.ground)
  local gw, gd = T.ground:getWidth(), { T.ground:getDimensions() }
  T.bankTop = lg.newQuad(0, 0, gw, style == "park" and 9 or 10, gd[1], gd[2])   -- the lawn / pavement's back edge
  T.bankEarth = lg.newQuad(0, 44, gw, 20, gd[1], gd[2])                        -- earth rows (the pond's far bank)
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
    strip(T.treeline, camx, 0.25, 177)                            -- 4 the far tree line
    vpop(on); on = vpush("mid")
    Look.use("mid")
    local ox = math.floor(camx * 0.5)                             -- 5 near trees (faded)
    for _, tr in ipairs(L.trees) do
      local im = T["tree" .. tr.i]
      local x = tr.x - ox
      if x < 330 and x + im:getWidth() > -10 then lg.draw(im, x, 180 - im:getHeight()) end
    end
  else
    Look.use("shore")
    strip(T.roofs, camx, 0.25, 160)                               -- 4 far roofs and spires
    if def then (package.loaded.arthooks or require("arthooks")).drawFarSpire(def, camx, w.width) end   -- (art/placement:
    -- the tall Downtown's landmark, Riddarholmen's spire, behind the old town row on this layer)
    vpop(on); on = vpush("mid")
    Look.use("mid")
    strip(T.facades, camx, 0.5, 178)                              -- 5 old town facades (faded)
  end
  vpop(on); on = vpush("world")                                   -- (the ponds are in the world)
  -- the pond / basin: its far bank, then the water (rows of the river art, each moving on its own)
  Look.use("ground")
  local gw = T.ground:getWidth()
  for _, p in ipairs(pools(w)) do
    local x0, x1 = math.floor(p.x0 - camx), math.floor(p.x1 - camx)
    if x1 > -2 and x0 < 322 then
      lg.setScissor(math.max(0, x0), 0, math.max(0, math.min(320, x1) - math.max(0, x0)), 240)   -- (screen space)
      local ox = math.floor(camx) % gw
      if L.style == "park" then                                   -- the lawn goes on behind, then an earth bank
        for x = -ox - gw, 320, gw do
          lg.draw(T.ground, T.bankTop, x, 172 + dy()); lg.draw(T.ground, T.bankEarth, x, 181 + dy()); lg.draw(T.ground, T.bankEarth, x, 201 + dy())
        end
      else                                                        -- the pavement's back, then the basin's granite
        local d = dy()
        for x = -ox - gw, 320, gw do lg.draw(T.ground, T.bankTop, x, 172 + d) end
        lg.setColor(0.62, 0.59, 0.56); lg.rectangle("fill", x0, 182 + d, x1 - x0, p.y0 - 182 - d)
        lg.setColor(0.76, 0.73, 0.69); lg.rectangle("fill", x0, 182 + d, x1 - x0, 2)
        lg.setColor(0.45, 0.42, 0.40)
        for x = x0 - (x0 % 18), x1, 18 do lg.rectangle("fill", x, 184 + d, 1, p.y0 - 184 - d) end
      end
      lg.setColor(0.18, 0.2, 0.22); lg.rectangle("fill", x0, p.y0 - 1, x1 - x0, 1)   -- the water's edge
      Look.use("water")
      local tint = L.style == "park" and { 0.80, 0.93, 0.86 } or { 0.92, 1, 1 }
      local ww, wh = A.water:getDimensions()
      for y = p.y0, w.height - 1 do                               -- (down to the bottom of the world)
        local row = math.min(wh - 1, 20 + (y - p.y0))
        local depth = (y - p.y0) / 32
        local o = math.floor(camx + math.sin(t * 1.3 + y * 0.55) * (0.6 + depth) + t * (1 + 2 * depth) + 0.5) % ww
        lg.setColor(tint)
        lg.draw(A.water, A.waterQ[row], -o, y); lg.draw(A.water, A.waterQ[row], ww - o, y)
      end
      lg.setScissor()
      Look.use("ground")
    end
  end
  vpop(on)
  Look.off()
  lg.setColor(1, 1, 1, 1)
end

-- the ground of an art level, painted once: the path / pavement strip on every walkable top (its back edge 12 px
-- above Pepper's line), dark edges on the cut faces (the pond's banks); Downtown's river stairs as stone steps.
function Sc.paintGroundArt(w, style, foot)
  foot = foot or 184                                              -- (the path line: a tall level's def.foot)
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
      clip(x, 0, 1, m[2])
      lg.draw(T.ground, T.groundQ[x % gw], x, top - 12)
      if top - 12 + gh < w.height then lg.draw(T.ground, T.groundQ[x % gw], x, top - 12 + gh) end
      clip()
      if stair then                                               -- each step: a light granite nosing
        lg.setColor(0.78, 0.75, 0.70); lg.rectangle("fill", x, top, 1, 1)
        lg.setColor(0.36, 0.34, 0.33); lg.rectangle("fill", x, top + 3, 1, 1)
      end
    end
  end
  local function solid(x, y)
    for _, m in ipairs(cover[x] or {}) do if y >= m[1] and y < m[2] then return true end end
    return false
  end
  lg.setColor(0.16, 0.13, 0.11)                                   -- cut faces (the banks): a dark edge
  for x = xa, xb - 1 do                                           -- (the chunk's columns)
    if not w:slopeAt(x) then
      for _, m in ipairs(cover[x]) do
        for y = math.max(m[1], foot), m[2] - 1 do
          if (x > 0 and not solid(x - 1, y) and not w:slopeAt(x - 1)) or (x < w.width - 1 and not solid(x + 1, y) and not w:slopeAt(x + 1)) then
            lg.rectangle("fill", x, y, 1, 1)
          end
        end
      end
    end
  end
  end)
end

-- an oak branch over its one-way box: 6 px thick by the trunk, 4 at the tip, its top row the ledge; between the
-- box and the trunk it dips down (it is no ledge there). Autumn leaves hang under the tip.
local BARK = { hex("7a5536"), hex("a3774c"), hex("523823") }
local INK = { 29 / 255, 24 / 255, 22 / 255 }
local LEAF = { hex("d9822b"), hex("b8551f"), hex("e2a53a") }
local function drawBranch(p, trunk, camx)
  local side = ((p.x0 + p.x1) / 2 < (trunk.x0 + trunk.x1) / 2) and -1 or 1
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
local function drawBough(p, camx)
  local ox = math.floor(camx)
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
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
local function drawBalcony(p, camx)
  local ox = math.floor(camx)
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
  local w = x1 - x0
  lg.setColor(INK); lg.rectangle("fill", x0 + 1, y - 9, w - 2, 9)    -- the railing (behind Pepper)
  lg.setColor(0.30, 0.32, 0.36)
  lg.rectangle("fill", x0 + 2, y - 8, w - 4, 1)
  for x = x0 + 2, x1 - 3, 3 do lg.rectangle("fill", x, y - 8, 1, 8) end
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
function Sc.spring(x, y, h)
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
--   TREETOP WALK, ALDER WALK  a plank walk on timber legs down to the ground or the bed of the water under it
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
local function drawTrunk(t, top, foot, ox, big)
  local x0, w = t.x0 - ox, t.x1 - t.x0
  local h = foot - top
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
local function drawCanopy(c, ox, T)
  local Q = crowns()
  local w, h = c.x1 - c.x0, c.y1 - c.y0
  local r = rng(c.x0 * 3 + c.y0)
  lg.setColor(1, 1, 1, 1)
  local function put(cr, x, y, flip)
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
local function drawFork(p, t, ox)
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

-- a plank walk: the deck (crisp), a rope hand-rail on posts behind Pepper
local function drawWalk(p, ox)
  local x0, x1, y = p.x0 - ox, p.x1 - ox, p.y0
  local hgt = p.y1 - p.y0
  local w = x1 - x0
  for px = x0 + 4, x1 - 4, 40 do                                     -- rail posts and the rope between them
    lg.setColor(INK); lg.rectangle("fill", px - 1, y - 15, 4, 15)
    lg.setColor(WOOD[3]); lg.rectangle("fill", px, y - 14, 2, 14); lg.setColor(WOOD[2]); lg.rectangle("fill", px, y - 14, 1, 1)
    if px + 40 <= x1 - 4 then
      for dx = 2, 39 do
        local u = dx / 40
        local ry = math.floor(y - 12 + 4 * 4 * u * (1 - u) * 0.5 + 0.5)
        lg.setColor(INK); lg.rectangle("fill", px + dx, ry - 1, 1, 3)
        lg.setColor(hex("c9b48a")); lg.rectangle("fill", px + dx, ry, 1, 1)
      end
    end
  end
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, w + 2, hgt + 2)  -- the deck
  lg.setColor(WOOD[1]); lg.rectangle("fill", x0, y, w, hgt)
  lg.setColor(WOOD[2]); lg.rectangle("fill", x0, y, w, 1)
  lg.setColor(WOOD[3]); lg.rectangle("fill", x0, y + hgt - 1, w, 1)
  for x = x0 + 7, x1 - 2, 8 do lg.setColor(WOOD[3]); lg.rectangle("fill", x, y + 1, 1, hgt - 2) end   -- plank joints
end
-- its legs (behind Pepper): pairs of timbers down to the ground, or into the water (seen through it)
local function drawWalkLegs(p, ox, foot, world)
  local floorY = world and world.height or (foot + 56)
  for lx = p.x0 + 6, p.x1 - 10, 60 do
    local wet = false
    for _, r in ipairs(world and world.water or {}) do if lx >= r.x0 and lx < r.x1 then wet = true end end
    local bottom = wet and floorY or foot
    local x = lx - ox
    lg.setColor(INK); lg.rectangle("fill", x - 1, p.y1, 6, bottom - p.y1)
    lg.setColor(0.30, 0.24, 0.20); lg.rectangle("fill", x, p.y1, 4, bottom - p.y1)
    lg.setColor(0.42, 0.34, 0.27); lg.rectangle("fill", x, p.y1, 1, bottom - p.y1)
    for by = p.y1 + 20, bottom - 30, 40 do                           -- cross ties
      lg.setColor(INK); lg.rectangle("fill", x - 3, by - 1, 10, 4); lg.setColor(0.36, 0.29, 0.23); lg.rectangle("fill", x - 2, by, 8, 2)
    end
    if wet then                                                       -- under the surface: the water's colour over it
      lg.setColor(0.33, 0.47, 0.52, 0.55); lg.rectangle("fill", x - 3, foot + 24, 10, bottom - foot - 24)
    end
  end
end

-- the rose arbour: a slat (crisp), its posts and roses (faded, behind)
local function drawSlat(p, ox)
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
  local x0, x1, y, hgt = p.x0 - ox, p.x1 - ox, p.y0, p.y1 - p.y0
  lg.setColor(INK); lg.rectangle("fill", x0 - 1, y - 1, x1 - x0 + 2, hgt + 2)
  lg.setColor(DECK[1]); lg.rectangle("fill", x0, y, x1 - x0, hgt)
  lg.setColor(DECK[2]); lg.rectangle("fill", x0, y, x1 - x0, 1)
  lg.setColor(DECK[3]); lg.rectangle("fill", x0, y + hgt - 1, x1 - x0, 1)
end
-- (art/placement) a post goes down to the path (foot), behind the slide tower's art: it stopped in the air at the
-- cage's top; top: where it starts (its deck), default its box's top
local function drawTowerPost(t, ox, foot, top)
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
  -- (art/placement) front-on, as a bough is seen from the side: over its box it lies level (the top Pepper stands
  -- on, the gap she crawls under), its free end rounded off; towards its trunk it bends up into the leaves, the
  -- underside curving up faster than the top, so it thins from 16 px to about 7 (was a slab rising 1 px a column,
  -- which read as a crate seen from above)
  local cols = {}                                                   -- { x, top, bottom (inclusive) }
  local n = x1 - x0
  for i = 0, n - 1 do
    local x = x0 + i
    local e = side > 0 and i or (n - 1 - i)                        -- columns from the free end
    local tip = ({ 6, 3, 1 })[e + 1] or 0
    cols[#cols + 1] = { x, y0 + (e == 0 and 1 or 0), y1 - 1 - tip }
  end
  local reach = 20
  for i = 1, reach do                                               -- towards its trunk, rising into the leaves
    local x = side > 0 and (x1 - 1 + i) or (x0 - i)
    local mid = (y0 + y1 - 1) / 2 - i * i / 13                     -- its middle line curves up (a parabola)
    local th = (y1 - y0) - i * 0.45                                -- and it thins
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
  local ex = side > 0 and (x1 + reach) or (x0 - reach)              -- where it goes into the leaves: a leafy clump
  local last = cols[#cols]
  local ey = math.floor((last[2] + last[3]) / 2)                    -- (round its end, which goes on up out of sight)
  for i, q in ipairs({ { -3, -6 }, { 1, -9 }, { 4, -4 }, { -6, -1 }, { 0, -2 }, { 3, 1 }, { -2, 3 }, { 5, -8 } }) do
    lg.setColor(INK); lg.rectangle("fill", ex + side * q[1] - 2, ey + q[2] - 1, 5, 4)
  end
  for i, q in ipairs({ { -3, -6 }, { 1, -9 }, { 4, -4 }, { -6, -1 }, { 0, -2 }, { 3, 1 }, { -2, 3 }, { 5, -8 } }) do
    lg.setColor(LEAF[1 + i % 3]); lg.rectangle("fill", ex + side * q[1] - 1, ey + q[2], 3, 2)
  end
end

-- the magpie's nest at the top of the big oak (the landmark: dark twigs, not faded, so it reads from below)
local function drawNest(p, ox)
  local x0, x1, y0, y1 = p.x0 - ox, p.x1 - ox, p.y0, p.y1
  local w = x1 - x0
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
  for _, t in ipairs(TI.trunks) do                                   -- trunks
    if not t.art and t.x1 - ox > -20 and t.x0 - ox < 340 then
      local c = canopyOver(t)
      local top = c and math.floor((c.y0 + c.y1) / 2) or t.y0
      drawTrunk(t, math.min(top, t.y0), foot, ox, t.x1 - t.x0 >= 24)
    end
  end
  for _, c in ipairs(TI.canopies) do                                 -- canopies, over the trunks' tops
    if c.x1 - ox > -120 and c.x0 - ox < 440 then drawCanopy(c, ox, T) end
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
  local r = TI and TI.role[p]
  if not r then return false end
  local ox = math.floor(camx)
  if r == "nest" then drawNest(p, ox)
  elseif r == "walk" then drawWalk(p, ox)
  elseif r == "slat" then drawSlat(p, ox)
  elseif r == "deck" then drawDeck(p, ox)
  elseif r == "lowbough" then drawLowBough(p, (trunkOf(TI, p)), ox)
  elseif r == "branch" then
    local t = trunkOf(TI, p)
    if t and t.x0 < p.x1 and t.x1 > p.x0 then drawFork(p, t, ox)
    elseif t then drawBranch(p, t, camx)
    else drawFork(p, { x0 = p.x0, x1 = p.x1 }, ox) end
  end
  lg.setColor(1, 1, 1, 1)
  return true
end

-- one prop of an art level. kicked: a leaf pile Pepper has run through.
function Sc.drawPropArt(p, camx, def, kicked)
  local style = def.art
  local T, A = Sc.townArt(style), Sc.art()
  local x, w = p.x0 - camx, p.x1 - p.x0
  if x > 360 or x + w < -120 then return end
  if p.layer == "front" then                                      -- the foreground frame: below Pepper's lines only
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
    if style == "park" and underCrown(def, p) then drawBough(p, camx); return end
    local o = owner(def, p)
    if p.kind == "decor" or not o then return end                 -- posts, legs, crowns: drawn with their set piece
    n = o.name
    if style == "park" and (n == "OAK" or n == "BRANCH") then drawBranch(p, named(def, "OAK"), camx); return end
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
      local sx, sy, sw, sh = math.floor(x), p.y0, w, p.y1 - p.y0
      lg.setColor(INK); lg.rectangle("fill", sx - 1, sy - 1, sw + 2, sh + 1)
      lg.setColor(0.42, 0.26, 0.14); lg.rectangle("fill", sx, sy + 3, sw, sh - 3)
      lg.setColor(0.33, 0.20, 0.11); for i = 3, sw - 3, 5 do lg.rectangle("fill", sx + i, sy + 5, 1, sh - 7) end
      lg.setColor(0.86, 0.66, 0.40); lg.rectangle("fill", sx, sy, sw, 3)
      lg.setColor(0.70, 0.50, 0.28); lg.rectangle("fill", sx + 4, sy + 1, sw - 8, 1)
      lg.setColor(1, 1, 1, 1)
    elseif n == "BENCH" then Sc.shadow(x + w / 2, 183 + d, w + 10, 5); at(A.bench, x - 3, 184 + d - A.bench:getHeight())
    elseif n == "HEDGE" then Sc.shadow(x + w / 2, 183 + d, w + 4, 5); at(T.hedge, x, p.y0)
    elseif n == "STONE" then
      at(T.stone, x - 1, p.y0 - 1)
      local water = 208 + d                                       -- under the surface: the pond's colour over it
      lg.setColor(0.33, 0.47, 0.52, 0.55); lg.rectangle("fill", math.floor(x) - 1, water, T.stone:getWidth(), 240 + d - water)
    elseif n == "BIN" then shadowUnder(p, camx); at(A.bin, x - 1, 184 + d - A.bin:getHeight())
    elseif n == "PICNIC TABLE" then shadowUnder(p, camx); at(T.table, x, p.y0)
    elseif n == "OAK" then at(T.oak, x + w / 2 - 94, 175 + d - T.oak:getHeight())
    elseif n == "BRANCH" then drawBranch(p, named(def, "OAK"), camx)
    elseif n == "SLIDE" or n == "FRAME" then
      if n == "FRAME" then at(T.frame, x - 1, 119 + d) end            -- (the slide: Sc.drawTerrainArt, over the path)
    elseif n == "SWINGS" then at(T.swings, x + w / 2 - T.swings:getWidth() / 2, 175 + d - T.swings:getHeight())
    elseif n == "WILLOWS" then                                    -- all three willows (decoration, base y 174)
      for i, c in ipairs(willowCrowns(def)) do
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
      lg.setColor(1, 1, 1, 1)
      lg.draw(T.keeperWinch, T.keeperWinchQ[Sc.winchFrame or 1], math.floor(x + w / 2), 174 + d, 0, -1, 1, 60, 79)
    else Sc.drawProp(p, camx, C.prop) end
  else
    if n == "DOOR" then at(T.door, x, 175 + d - T.door:getHeight())
    elseif n == "CRATES" then                                     -- a stack of apple crates, 16 px each
      local k = math.max(1, math.floor((p.y1 - p.y0) / 16 + 0.5))
      shadowUnder(p, camx)
      for i = 1, k do at(T.crate, x, p.y1 - 16 * i - 12) end
    elseif n == "TABLE" then Sc.shadow(x + w / 2, 183 + d, w + 4, 5); at(T.table, x - 1, p.y0)
    elseif n == "PARASOL" then
      local tb                                                     -- its pole, down to the table under it
      for _, q in ipairs(def.props) do if q.name == "TABLE" and q.x0 >= p.x0 and q.x1 <= p.x1 then tb = q end end
      local px = math.floor(x + w / 2) - 1
      local foot = tb and tb.y0 or 240 + d                        -- (no table: a pole standing in the water)
      lg.setColor(INK); lg.rectangle("fill", px - 1, p.y1, 4, foot - p.y1)
      lg.setColor(0.55, 0.57, 0.6); lg.rectangle("fill", px, p.y1, 2, foot - p.y1)
      local sq = (p.squashT or 0) > 0 and 2 or 0                  -- a springy one dips as it launches her
      at(T.parasol, x, p.y0 - 1 + sq)
      if p.bounce then Sc.spring(px + 1, p.y1 + sq, 10 - sq) end
    elseif n == "SIGN" then at(T.shopsign, x - 1, p.y0 - 6)
    elseif n == "STALL" then shadowUnder(p, camx); at(T.stall, x - 1, p.y0 - 15)
    elseif n == "AWNING" then
      for _, q in ipairs(def.props) do                            -- its posts (thin decoration boxes under it)
        if q.kind == "decor" and q.x1 - q.x0 <= 6 and q.y0 == p.y0 and q.x0 >= p.x0 - 2 and q.x1 <= p.x1 + 2 then
          local qx = math.floor(q.x0 - camx)
          lg.setColor(INK); lg.rectangle("fill", qx - 1, q.y0, q.x1 - q.x0 + 2, q.y1 - q.y0)
          lg.setColor(0.42, 0.29, 0.18); lg.rectangle("fill", qx, q.y0, q.x1 - q.x0, q.y1 - q.y0)
          lg.setColor(0.58, 0.42, 0.27); lg.rectangle("fill", qx, q.y0, 1, q.y1 - q.y0)
        end
      end
      local im = w >= 72 and T.awning80 or T.awning64
      local sq = (p.squashT or 0) > 0 and 2 or 0                  -- a springy one dips as it launches her
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
    elseif n == "PEDESTAL" then shadowUnder(p, camx); at(T.pedestal, x, p.y0)
    elseif n == "ARM" then return
    elseif n == "RIM" then at(T.rim, x - 1, p.y0 - 1)
    elseif n == "FOUNTAIN" then
      at(T.bowl, x - 1, p.y0 - 1)
      lg.setColor(0.33, 0.47, 0.52, 0.45); lg.rectangle("fill", math.floor(x) + 8, 193 + d, w - 16, 47)
    elseif n == "KIOSK" then shadowUnder(p, camx); at(T.kiosk, x - 1, p.y0 - 1)
    elseif n == "SHELTER" then shadowUnder({ x0 = p.x0, x1 = p.x1, y1 = 184 + d }, camx); at(T.shelter, x, p.y0)
    elseif n == "RIVER" then at(T.sign, x + w / 2 - T.sign:getWidth() / 2, 175 + d - T.sign:getHeight())
    elseif n == "TUB" then shadowUnder(p, camx); at(T.tub, x, p.y0 - 18)
    elseif n == "HOUSE" then                                      -- faded decoration; their balconies are the ledges
      local im = T["house" .. ((houseIndex(def, p) - 1) % 3 + 1)]
      at(im, x + w / 2 - im:getWidth() / 2, 175 + d - im:getHeight())
    elseif n == "BALCONY" then drawBalcony(p, camx)
    elseif n == "TIER" then at(T.tier, x - 1, p.y0 - 1)
    else Sc.drawProp(p, camx, C.prop) end
  end
  lg.setColor(1, 1, 1, 1)
end

-- terrain set pieces drawn over the path (after the ground): City Park's slide, Downtown's fountain spout and jets
function Sc.drawTerrainArt(def, camx, t)
  local T = Sc.townArt(def.art)
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
      if tier then                                                -- water falls from the top tier's rims to the basin
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
function Sc.drawMoverArt(m, camx, style)
  local T = Sc.townArt(style)
  local im = T.boat
  local x = math.floor(m.x0 - camx + 0.5) - 3
  lg.setColor(1, 1, 1, 1)
  if m.dir and m.dir > 0 then lg.draw(im, x + im:getWidth(), m.y0 - 18, 0, -1, 1) else lg.draw(im, x, m.y0 - 18) end
  local d = dy()
  lg.setColor(0.33, 0.47, 0.52, 0.5); lg.rectangle("fill", x, 209 + d, im:getWidth(), m.y0 - 18 + im:getHeight() - 209 - d)
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
