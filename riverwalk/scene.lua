-- Scenery. Art in art/scene: far shore and bridge, river, bench, bin, pot, lamp post (riverwalk_scenery_v1),
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
local C = Sc.C
Sc.speeds = { clouds = 0.05, city = 0.08, shore = 0.3, water = 0.5 }

-- art: loaded once. The images are used exactly as delivered; the two made here only rearrange their pixels
-- or swap colours, so nothing is redrawn.
local A
Sc.DECOR_FADE = 0.28
local HAZE = { 200 / 255, 210 / 255, 222 / 255 }
local function newImg(d) local i = lg.newImage(d); i:setFilter("nearest", "nearest"); return i end
function Sc.art()
  if A then return A end
  A = {}
  for _, n in ipairs({ "river", "skyline", "pavement", "building", "tree" }) do A[n] = newImg("art/scene/" .. n .. ".png") end
  -- decoration on the pavement (pot, lamp posts) is faded DECOR_FADE of the way towards the haze, so it sits back
  -- and the obstacle course stands out. The files are untouched; this is done to a copy when the game loads.
  for _, n in ipairs({ "pot", "lamp_post" }) do
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
  for _, n in ipairs({ "bench", "bin" }) do
    local src = love.image.newImageData("art/scene/" .. n .. ".png")
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
    A[n] = newImg(d); A.outlined[n] = true
  end
  -- far shore: the 320 px strip ends inside the bridge, but the shore layer must cover 800 px. The strip is
  -- extended with its own columns: one arch and pier (columns 293-307) repeated 14 times (column 308 equals
  -- column 293, so the joins are invisible), then the strip's last arch (308-316), then the bridge's left end and
  -- the trees (columns 0-278) mirrored, which closes the bridge on the far side.
  local src = love.image.newImageData("art/scene/far_shore_bridge.png")
  local h = src:getHeight()
  local cols = {}
  for x = 0, 307 do cols[#cols + 1] = x end
  for _ = 1, 14 do for x = 293, 307 do cols[#cols + 1] = x end end
  for x = 308, 316 do cols[#cols + 1] = x end
  for x = 278, 0, -1 do cols[#cols + 1] = x end
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
  -- 2 clouds
  local r = rng(11); L.clouds = {}
  local x = -40
  while x < span(0.05) + 200 do
    local w = math.floor(r(40, 110)); L.clouds[#L.clouds + 1] = { x = x, y = math.floor(r(28, 92)), w = w, h = math.floor(r(9, 20)) }
    x = x + w + math.floor(r(40, 120))
  end
  Sc.art()
  return L
end

local function box(c, x, y, w, h) lg.setColor(c); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end
local function outlined(c, e, x, y, w, h)
  x, y = math.floor(x), math.floor(y)
  lg.setColor(e); lg.rectangle("fill", x, y, w, h)
  if w > 2 and h > 2 then lg.setColor(c); lg.rectangle("fill", x + 1, y + 1, w - 2, h - 2) end
end
Sc.box, Sc.outlined = box, outlined

-- layers 1 to 5 (everything behind the quay)
function Sc.drawFar(L, camx, t)
  for y = 0, 239 do                                                -- 1 sky
    local k = math.min(1, y / 170)
    lg.setColor(C.sky1[1] + (C.sky2[1] - C.sky1[1]) * k, C.sky1[2] + (C.sky2[2] - C.sky1[2]) * k, C.sky1[3] + (C.sky2[3] - C.sky1[3]) * k)
    lg.rectangle("fill", 0, y, 320, 1)
  end
  local o = camx * 0.05 - t * 3                                    -- 2 clouds drift
  for _, c in ipairs(L.clouds) do
    local x = (c.x - o) % (#L.clouds * 120 + 400) - 120
    if x < 330 then box(C.cloud, x, c.y, c.w, c.h); box(C.cloud, x + c.w * 0.2, c.y - 5, c.w * 0.5, 5) end
  end
  -- 3 far city: the skyline, bottom at y 138 (its misty base is behind the far shore trees). It scrolls at 0.08,
  -- so over the whole level it moves 128 px: the strip is followed by its own first 128 columns, which never
  -- bring a second City Hall tower on screen.
  lg.setColor(1, 1, 1, 1)
  local sw = A.skyline:getWidth()
  local sx = -math.floor(camx * 0.08)
  lg.draw(A.skyline, sx, 138 - A.skyline:getHeight()); lg.draw(A.skyline, sx + sw, 138 - A.skyline:getHeight())
  lg.setColor(1, 1, 1, 1)
  lg.draw(A.shore, -math.floor(camx * 0.3), 113)                   -- 4 far shore and bridge: bottom row = waterline
  local rw = A.river:getWidth()                                    -- 5 river, y 146 to the bottom, tiles left-right
  for x = -(math.floor(camx * 0.5) % rw), 319, rw do lg.draw(A.river, x, 146) end
end

-- a prop of the level; usable ones (solid / one-way) are outlined, decorations are flat
function Sc.drawProp(p, camx, layerColour)
  local x, y, w, h = p.x0 - camx, p.y0, p.x1 - p.x0, p.y1 - p.y0
  if x > 330 or x + w < -10 then return end
  if p.art then
    local art = Sc.art(); local im = art[p.art]
    local o = art.outlined[p.art] and 1 or 0                       -- outlined art is 1 px bigger on every side
    lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x) - o, p.y1 - im:getHeight() + o)
    return
  end
  if p.railing then
    box(C.back, x, y, w, 3)                                         -- top bar
    box(C.back, x, y + 14, w, 2)                                     -- lower bar
    for px = 0, w - 3, 32 do box(C.back, x + px, y, 3, 184 - y) end  -- posts
    return
  end
  if p.kind == "decor" then box(layerColour, x, y, w, h)
  else outlined(C.prop, C.propEdge, x, y, w, h) end
  if p.name and p.name ~= "" and w >= 14 then
    lg.setColor(C.label)
    local tw = F.width(p.name, 1)
    if tw <= w + 30 then F.print(p.name, math.floor(x + w / 2 - tw / 2), math.floor(y + math.min(h, 40) / 2 - 3), 1) end
  end
end

-- the ground of the play layer, painted once into a canvas as wide as the level. Every walkable top at or below
-- y 150 gets the pavement art, one column per pixel (it repeats every 320 px): its back edge is 12 px above the
-- line Pepper walks on, then the kerb and the road. Higher terrain (the bridge pier) stays a greybox.
function Sc.paintGround(w)
  local art = Sc.art()
  local pave = art.pavement
  local pw, ph = pave:getDimensions()
  local q = {}
  for i = 0, pw - 1 do q[i] = lg.newQuad(i, 0, 1, ph, pw, ph) end
  local cv = lg.newCanvas(w.width, 240)
  cv:setFilter("nearest", "nearest")
  lg.push("all"); lg.setCanvas(cv); lg.clear(0, 0, 0, 0); lg.origin()
  local high = {}
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
        lg.setScissor()
      end
    end
  end
  for _, h in ipairs(high) do                                      -- greybox terrain drawn last, over the pavement
    lg.setColor(C.ground); lg.rectangle("fill", h[1], h[2], 1, h[3] - h[2])
    lg.setColor(C.groundEdge); lg.rectangle("fill", h[1], h[2], 1, 1)
  end
  lg.pop()
  return cv
end

-- Props stand SETBACK px behind the line Pepper walks on (towards the water or the building), as in the concept.
-- Their collision boxes in the level file are set back by the same amount, so she lands where the seat is drawn.
Sc.SETBACK = 5
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
function Sc.shadow(cx, y, w)
  if w < 4 then return end
  local rx = math.floor(w / 2)
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

function Sc.label(text, x, y)
  lg.setColor(C.label); local tw = F.width(text, 1); F.print(text, math.floor(x - tw / 2), math.floor(y), 1)
end
return Sc
