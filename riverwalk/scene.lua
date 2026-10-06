-- Scenery. Art in art/scene: far shore and bridge, bench, bin, pot, lamp post (riverwalk_scenery_v1), water (SpriteCook),
-- skyline, pavement, building, tree (trial). Everything else is still wireframe: plain boxes in a misty grey-blue per layer, lighter the
-- further back. Layers 2 to 5 scroll slower (parallax).
local F = require("bigfont")
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

-- decoration is faded DECOR_FADE of the way towards the haze, so it sits back and the obstacle course stands out
Sc.DECOR_FADE = 0.28
local HAZE = { 200 / 255, 210 / 255, 222 / 255 }

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
  local key = kind .. w .. "x" .. (h or 0)
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
    local k = Sc.DECOR_FADE
    d:mapPixel(function(x, y, r, g, b, a) return r + (HAZE[1] - r) * k, g + (HAZE[2] - g) * k, b + (HAZE[3] - b) * k, a end)
  end
  local im = lg.newImage(d); im:setFilter("nearest", "nearest")
  railCache[key] = im
  return im
end

-- art: loaded once. The images are used exactly as delivered; the two made here only rearrange their pixels
-- or swap colours, so nothing is redrawn.
local A
local function newImg(d) local i = lg.newImage(d); i:setFilter("nearest", "nearest"); return i end
function Sc.art()
  if A then return A end
  A = {}
  for _, n in ipairs({ "water", "skyline", "pavement", "road", "manhole", "drain" }) do A[n] = newImg("art/scene/" .. n .. ".png") end
  A.waterQ = {}                                                   -- one quad per row: each row of the river moves on its own
  for y = 0, A.water:getHeight() - 1 do A.waterQ[y] = lg.newQuad(0, y, A.water:getWidth(), 1, A.water:getDimensions()) end
  -- decoration (pot, lamp posts, the houses and trees) is faded DECOR_FADE of the way towards the haze, so it sits back
  -- and the obstacle course stands out. The files are untouched; this is done to a copy when the game loads.
  for _, n in ipairs({ "pot", "lamp_post", "building", "tree", "tree_near", "tree_far", "cafe", "gable" }) do
    local d = love.image.newImageData("art/scene/" .. n .. ".png")
    d:mapPixel(function(x, y, r, g, b, a)
      local k = Sc.DECOR_FADE
      return r + (HAZE[1] - r) * k, g + (HAZE[2] - g) * k, b + (HAZE[3] - b) * k, a
    end)
    A[n] = newImg(d)
  end
  -- things Pepper can use (stand on, jump onto) get the characters' 1 px dark outline, so they read as part of the
  -- obstacle course; decoration and background have none. The outline goes outside the art (image grows 1 px
  -- on every side), the art's own pixels are untouched.
  A.outlined = {}
  -- round 2 obstacles and buildings (tools/make_props.py): mid-tone SpriteCook art that already has its own 1 px
  -- dark outline, so none is added here
  for _, n in ipairs({ "bench", "bin", "flowerbox", "gritbox", "planter_sq", "ferry" }) do
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
  local x = 271
  while #cols < 1196 do cols[#cols + 1] = x; x = x - 1 end
  local d = love.image.newImageData(#cols, h)
  for i, x in ipairs(cols) do for y = 0, h - 1 do d:setPixel(i - 1, y, src:getPixel(x, y)) end end
  A.shore = newImg(d)
  -- lit lamp (a checkpoint Pepper has passed): the lantern glass (rows 12-23) glows warm.
  local lp = love.image.newImageData("art/scene/lamp_post.png")
  local function is(r, g, b, R, G, B) return math.abs(r * 255 - R) < 1 and math.abs(g * 255 - G) < 1 and math.abs(b * 255 - B) < 1 end
  lp:mapPixel(function(x, y, r, g, b, a)                           -- lit lamp: warm glass (exact colours), the rest faded
    if y >= 12 and y <= 23 and a > 0 then
      if is(r, g, b, 187, 211, 233) then return 250 / 255, 214 / 255, 120 / 255, a          -- the light is not faded
      elseif is(r, g, b, 88, 109, 134) then return 201 / 255, 150 / 255, 72 / 255, a end
    end
    local k = Sc.DECOR_FADE
    return r + (HAZE[1] - r) * k, g + (HAZE[2] - g) * k, b + (HAZE[3] - b) * k, a
  end)
  A.lamp_lit = newImg(lp)
  return A
end

-- deterministic boxes per layer
local function rng(seed) local s = seed return function(a, b) s = (s * 1103515245 + 12345) % 2147483648; return a + (s % 100000) / 100000 * (b - a) end end
function Sc.build(levelW)
  local L = {}
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
end

function Sc.drawFarGrey(L, camx, t)
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
  local base = 172                                                 -- the far edge of the park lawn
  local ox = math.floor(camx * 0.08)                               -- 3 far city
  for _, b in ipairs(L.city) do
    local x = b.x - ox
    if x < 330 and x + b.w > -10 then box(C.city, x, base - 20 - b.h, b.w, b.h + 20) end
  end
  if L.town then return drawTown(L, camx, base) end
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
end

-- the greybox ground: every terrain column flat grey with a 1 px edge on top; the pond's water as a flat box
-- with a light surface line. Painted once into a canvas as wide as the level.
function Sc.paintGroundGrey(w)
  local cv = lg.newCanvas(w.width, 240)
  cv:setFilter("nearest", "nearest")
  lg.push("all"); lg.setCanvas(cv); lg.clear(0, 0, 0, 0); lg.origin()
  for _, r in ipairs(w.water) do
    box(C.pond, r.x0, r.y0, r.x1 - r.x0, r.y1 - r.y0)
  end
  for _, r in ipairs(w.water) do                                   -- the surface: top row of the water only
    local top = true
    for _, q in ipairs(w.water) do if q ~= r and q.y1 == r.y0 and q.x0 < r.x1 and q.x1 > r.x0 then top = false end end
    if top then box(C.pondTop, r.x0, r.y0, r.x1 - r.x0, 1) end
  end
  for x = 0, w.width - 1 do
    local runs = {}
    for _, r in ipairs(w.rects) do if r.terrain and x >= r.x0 and x < r.x1 then runs[#runs + 1] = { r.y0, r.y1 } end end
    for _, sl in ipairs(w.slopes) do
      if x >= sl.x0 and x < sl.x1 then
        local i = x - sl.x0
        runs[#runs + 1] = { sl.dir < 0 and (sl.y0 + i) or (sl.y1 - i - 1), sl.y1 }
      end
    end
    table.sort(runs, function(a, b) return a[1] < b[1] end)
    local merged = {}
    for _, r in ipairs(runs) do
      local m = merged[#merged]
      if m and r[1] <= m[2] then m[2] = math.max(m[2], r[2]) else merged[#merged + 1] = { r[1], r[2] } end
    end
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
  lg.pop()
  return cv
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

-- layers 1 to 5 (everything behind the quay)
function Sc.drawFar(L, camx, t)
  for y = 0, 239 do                                                -- 1 sky
    local k = math.min(1, y / 170)
    lg.setColor(C.sky1[1] + (C.sky2[1] - C.sky1[1]) * k, C.sky1[2] + (C.sky2[2] - C.sky1[2]) * k, C.sky1[3] + (C.sky2[3] - C.sky1[3]) * k)
    lg.rectangle("fill", 0, y, 320, 1)
  end
  local o = camx * 0.05 - t * 3                                    -- 2 clouds drift
  lg.setColor(1, 1, 1, 1)
  for _, c in ipairs(L.clouds) do
    local x = math.floor((c.x - o) % L.cloudSpan - 120)
    if x < 330 and x + c.w > -10 then lg.draw(c.img, x, c.y) end
  end
  -- 3 far city: the skyline, bottom at y 138 (its misty base is behind the far shore trees). Over the whole
  -- level (3200 px, the camera moves 2880 px) it moves at most 128 px (factor 128 / 2880): the strip is followed
  -- by its own first 128 columns, which never bring a second City Hall tower on screen.
  lg.setColor(1, 1, 1, 1)
  local sw = A.skyline:getWidth()
  local sx = -math.floor(math.min(128, camx * 128 / 2880))
  lg.draw(A.skyline, sx, 138 - A.skyline:getHeight()); lg.draw(A.skyline, sx + sw, 138 - A.skyline:getHeight())
  lg.setColor(1, 1, 1, 1)
  lg.draw(A.shore, -math.floor(camx * 0.3), 113)                   -- 4 far shore and bridge: bottom row = waterline
  Sc.drawWater(camx, t)                                            -- 5 river
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

-- the ground of the play layer, painted once into a canvas as wide as the level. Every walkable top at or below
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
  local cv = lg.newCanvas(w.width, 240)
  cv:setFilter("nearest", "nearest")
  lg.push("all"); lg.setCanvas(cv); lg.clear(0, 0, 0, 0); lg.origin()
  local high, flat = {}, {}
  for x = 0, w.width - 1 do
    local runs = {}
    for _, r in ipairs(w.rects) do if r.terrain and x >= r.x0 and x < r.x1 then runs[#runs + 1] = { r.y0, r.y1 } end end
    for _, sl in ipairs(w.slopes) do
      if x >= sl.x0 and x < sl.x1 then
        local i = x - sl.x0
        runs[#runs + 1] = { sl.dir < 0 and (sl.y0 + i) or (sl.y1 - i - 1), sl.y1 }
      end
    end
    table.sort(runs, function(a, b) return a[1] < b[1] end)
    local merged = {}
    for _, r in ipairs(runs) do
      local m = merged[#merged]
      if m and r[1] <= m[2] then m[2] = math.max(m[2], r[2]) else merged[#merged + 1] = { r[1], r[2] } end
    end
    for _, m in ipairs(merged) do
      if m[1] < 150 then high[#high + 1] = { x, m[1], m[2] }
      else
        lg.setColor(1, 1, 1, 1)
        lg.setScissor(x, 0, 1, m[2])
        lg.draw(pave, q[x % pw], x, m[1] - 12)
        lg.draw(road, rq[x % rw], x, m[1] + 15)                     -- rows 27+ of the paving art are the road
        lg.setScissor()
        if m[1] == 184 then flat[x] = true end
      end
    end
  end
  -- manhole covers and kerb drains on the promenade road, at fixed pseudo-random spots where the road is flat
  local function flatRun(x0, x1) for x = x0, x1 do if not flat[x] then return false end end return true end
  lg.setColor(1, 1, 1, 1)
  local x, k = 150, 0
  while x < w.width - 30 do
    k = k + 1
    if flatRun(x - 2, x + 22) then lg.draw(art.manhole, x, 199 + ((k % 2 == 0) and 4 or 27)) end
    x = x + 260 + (k * 97) % 160
  end
  x, k = 60, 0
  while x < w.width - 20 do
    k = k + 1
    if flatRun(x - 2, x + 14) then lg.draw(art.drain, x, 200) end
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
  lg.pop()
  return cv
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
return Sc
