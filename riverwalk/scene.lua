-- Wireframe scenery: every layer is plain boxes in its own misty grey-blue, lighter the further back it is,
-- so each layer can be told apart while the level is tested. Layers 2 to 5 scroll slower (parallax).
local F = require("bigfont")
local Sc = {}
local lg = love.graphics
local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end

-- one shade per layer, far (light, misty) to near (dark)
Sc.C = {
  sky1 = hex("dde5ec"), sky2 = hex("c8d3de"),      -- 1 sky
  cloud = hex("eaeff3"),                           -- 2 clouds
  city = hex("b6c3cf"),                            -- 3 far city
  shore = hex("a2b1c0"),                           -- 4 far shore and bridge
  water = hex("8fa0b2"), sparkle = hex("a9b7c5"),  -- 5 water
  back = hex("788a9d"),                            -- 6 quay back (behind Pepper)
  ground = hex("5f6f81"), groundEdge = hex("435060"), -- 7 play layer: terrain
  prop = hex("6c7d90"), propEdge = hex("2f3a46"),  --   play layer: props Pepper can use (outlined)
  river = hex("7f91a4"),                           --   play layer: the river Pepper can fall into
  front = hex("3c4857"),                           -- 8 foreground frame
  label = hex("e4eaf0"), bone = hex("efe8d8"), boneEdge = hex("8a7f68"), gold = hex("f2c94c"),
}
local C = Sc.C
Sc.speeds = { clouds = 0.05, city = 0.15, shore = 0.3, water = 0.5 }

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
  -- 3 far city: towers of different sizes standing on the far shore line (y 150)
  r = rng(23); L.city = {}
  x = 0
  while x < span(0.15) do
    local w = math.floor(r(12, 34)); local h = math.floor(r(24, 78))
    L.city[#L.city + 1] = { x = x, y = 150 - h, w = w, h = h }
    x = x + w + math.floor(r(0, 10))
  end
  L.city[#L.city + 1] = { x = 150, y = 46, w = 22, h = 104 }     -- the spire tower (landmark)
  L.city[#L.city + 1] = { x = 157, y = 24, w = 8, h = 22 }
  -- 4 far shore: tree band and the far bridge
  r = rng(37); L.shore = {}
  x = -10
  while x < span(0.3) do
    local w = math.floor(r(14, 40)); local h = math.floor(r(8, 22))
    L.shore[#L.shore + 1] = { x = x, y = 158 - h, w = w, h = h + 4 }
    x = x + w - math.floor(r(2, 8))
  end
  L.bridge = { x = 260, y = 132, w = 240 }
  -- 5 water sparkles
  r = rng(53); L.sparkles = {}
  for i = 1, math.floor(span(0.5) / 22) do L.sparkles[i] = { x = math.floor(r(0, span(0.5))), y = math.floor(r(164, 236)), w = math.floor(r(4, 12)), ph = r(0, 6) } end
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
  o = camx * 0.15                                                  -- 3 far city
  for _, b in ipairs(L.city) do local x = b.x - o; if x > -40 and x < 330 then box(C.city, x, b.y, b.w, b.h) end end
  o = camx * 0.3                                                   -- 4 far shore and bridge
  local br = L.bridge; local bx = br.x - o
  box(C.shore, bx, br.y, br.w, 8)
  for i = 0, 4 do box(C.shore, bx + i * (br.w / 4) - 4, br.y + 8, 8, 24) end
  for _, b in ipairs(L.shore) do local x = b.x - o; if x > -50 and x < 330 then box(C.shore, x, b.y, b.w, b.h) end end
  o = camx * 0.5                                                   -- 5 water
  box(C.water, 0, 160, 320, 80)
  for _, s in ipairs(L.sparkles) do
    local x = s.x - o
    if x > -12 and x < 330 and math.sin(t * 2 + s.ph) > 0.2 then box(C.sparkle, x, s.y, s.w, 1) end
  end
end

-- a prop of the level; usable ones (solid / one-way) are outlined, decorations are flat
function Sc.drawProp(p, camx, layerColour)
  local x, y, w, h = p.x0 - camx, p.y0, p.x1 - p.x0, p.y1 - p.y0
  if x > 330 or x + w < -10 then return end
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

function Sc.label(text, x, y)
  lg.setColor(C.label); local tw = F.width(text, 1); F.print(text, math.floor(x - tw / 2), math.floor(y), 1)
end
return Sc
