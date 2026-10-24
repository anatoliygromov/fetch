-- The Lion King look (branch lk/look; the L key switches it off and on to compare).
-- What the 1994 game does, done here in code. Pepper, Mia, the ball, the bones and the HUD are never touched.
--   1 a colour script per level, as Lion King gives every level its own light: River Walk a summer morning,
--     City Park a golden autumn afternoon, Downtown a bright midday. Each has one key light and one haze colour
--     per distance, instead of one cool grey haze for everything (Look.scripts)
--   2 split toning per layer (a shader): light colours lean warm, dark ones lean blue-violet, colours a bit
--     richer; the further back a layer is, the more it turns into its haze colour. Each colour in maps to one
--     colour out, so an asset keeps its number of colours. The art files are untouched.
--   3 a painted sky in bands, joined by 2 x 2 ordered dither rows (the 16-bit way to do a gradient); in a tall
--     art level it goes on above the old top (deeper blues) and rises with the far city (Look.skyTall)
--   4 River Walk's road recedes: each road row scrolls a little faster the nearer it is (row scrolling, like the
--     river), and the near-lane traffic slides with its row
--   5 a dark foreground band at the bottom that scrolls 1.4x, only in front of the flat ground Pepper walks at
--     y 184 (River Walk: grass verges, shrubs, bollards; a script can also have chain fences). City Park and
--     Downtown have none: their bottom band (earth, quay wall) is already dark, and shapes there did not read.
--     Its tops are at y 218 or lower (under her lowest walking line, the lower quay at y 216), or y 206 deep
--     inside a stretch of flat ground. It never covers her.
local Look = { on = true, CHECK = os.getenv("LOOK_CHECK") ~= nil }
local lg = love.graphics
local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end

-- per layer: warm = how far light colours lean to warm, cool = how far dark ones lean to blue-violet,
-- sat = colour richness (1 = as drawn), haze / k = the layer's distance colour and how much of it.
-- Layers back to front: clouds, city (the far skyline), shore (River Walk's far shore; the far tree line or roofs),
-- mid (City Park's near trees, Downtown's facades), water, back (decoration behind Pepper's line), ground,
-- play (obstacles, the things Pepper uses), front (foreground props). bands = the sky, fg = the foreground's
-- colours (dark, mid, rim, warm rim, how often the rim is warm), kinds = what the foreground clumps are.
-- fade = the load-time distance step (scene.lua Sc.fadeK / Sc.fadeData): how far a layer's art is mixed towards that
-- layer's own haze when the level loads, before the shader (art comes at full local colour; the game does the
-- distance). Decision 3 (owner, 23 Oct): every load-time fade goes to the level's own haze for the layer, never to
-- the old cool grey. The amounts keep the ladder (docs/layer_ladder.md): the further back, the lighter. A piece
-- with its own amount (the park gate 28 %, the winch keeper 35 %, the vintage tram 40 %, the spire 45 %) keeps it
-- and takes the haze.
local function L(warm, cool, sat, haze, k) return { warm = warm, cool = cool, sat = sat, haze = hex(haze), k = k } end
Look.scripts = {
  riverwalk = {                                                    -- summer morning
    layers = { clouds = L(0.9, 1.6, 1.0, "f7ead2", 0.10), city = L(0.2, 1.8, 0.70, "aaa6d0", 0.46),
               shore = L(0.5, 1.5, 1.05, "9fb3cc", 0.30), mid = L(0.8, 1.3, 1.2, "c9d0d8", 0.15),
               water = L(0.5, 1.2, 1.35, "8fb4d8", 0.06), back = L(1.0, 1.2, 1.35, "f0e0c6", 0.10),
               ground = L(0.75, 1.3, 1.20, "000000", 0), play = L(0.7, 0.8, 1.18, "000000", 0),
               front = L(0.0, 1.8, 1.10, "1b1934", 0.40) },
    bands = { { 0, "4b7ec2" }, { 16, "5a8aca" }, { 32, "6b98d1" }, { 48, "80a8d7" }, { 62, "98b8db" },
              { 76, "b2c6da" }, { 89, "cbd1d4" }, { 101, "dfd7c9" }, { 112, "ecdabd" }, { 122, "f4dcb3" } },
    fg = { dark = hex("161c2c"), mid = hex("1f2b42"), rim = hex("4c5d7c"), warm = hex("9a8174"), warmK = 0.05 },
    kinds = { verge = 0.78, bollards = 0.22 },
    fade = { back = 0.28 },                                        -- (as before: decoration, railing, kiosks)
  },
  citypark = {                                                     -- golden autumn afternoon
    layers = { clouds = L(1.2, 1.7, 1.0, "f9e0c0", 0.14), city = L(0.2, 1.9, 0.60, "b8a0c2", 0.52),
               shore = L(0.6, 1.5, 1.05, "c8a6ae", 0.30), mid = L(1.0, 1.3, 1.25, "ecccae", 0.14),
               water = L(0.6, 1.3, 1.30, "86a2bc", 0.06), back = L(1.1, 1.3, 1.30, "f0d2b0", 0.10),
               ground = L(0.8, 1.0, 1.10, "000000", 0), play = L(0.8, 0.9, 1.18, "000000", 0),
               front = L(0.0, 1.8, 1.10, "1e1626", 0.40) },
    bands = { { 0, "6a83b8" }, { 18, "7b91bf" }, { 36, "8f9fc3" }, { 54, "a6adc3" }, { 72, "bebac0" },
              { 89, "d4c3b7" }, { 104, "e5c9a9" }, { 118, "efcb9b" }, { 131, "f4cc8e" }, { 143, "f7cd86" } },
    -- a tall level's sky goes on above y 0 (up in the treetops): deeper blues, each band 24 rows
    above = { { -120, "39579a" }, { -96, "4060a1" }, { -72, "4a68a7" }, { -48, "5571ad" }, { -24, "5f7ab3" } },
    fg = { dark = hex("1d1525"), mid = hex("2b1f33"), rim = hex("594257"), warm = hex("b5793f"), warmK = 0.22 },
    kinds = {},                                                    -- (the earth band is already the dark frame)
    -- the round trees (mid) must read lighter than the willows and oaks in front of them (back), and darker than
    -- the far tree line (shore): mid up from 28 %, back down from 28 % (the gate keeps 28 %: its dark ironwork),
    -- the tree line faded too
    fade = { shore = 0.35, mid = 0.48, back = 0.20 },
  },
  downtown = {                                                     -- bright midday
    layers = { clouds = L(0.5, 1.4, 1.0, "ffffff", 0.04), city = L(0.2, 1.7, 0.70, "a7bad6", 0.50),
               shore = L(0.4, 1.4, 1.00, "b2c3d9", 0.34), mid = L(0.7, 1.3, 1.15, "d6dee8", 0.18),
               water = L(0.4, 1.2, 1.35, "7fb0d8", 0.05), back = L(0.8, 1.2, 1.25, "efe6da", 0.08),
               ground = L(0.9, 0.7, 1.10, "000000", 0), play = L(0.7, 0.8, 1.15, "000000", 0),
               front = L(0.0, 1.8, 1.10, "141a26", 0.40) },
    bands = { { 0, "3e72c3" }, { 16, "4d7fc9" }, { 32, "5f8ecf" }, { 48, "75a0d5" }, { 64, "8db2da" },
              { 80, "a7c3de" }, { 96, "c0d3e0" }, { 112, "d5e0e2" }, { 126, "e3e9e3" }, { 140, "ebefe5" } },
    fg = { dark = hex("141a26"), mid = hex("1e2838"), rim = hex("4a5a72"), warm = hex("8e8070"), warmK = 0.04 },
    kinds = {},                                                    -- (the quay wall is already the dark frame)
    -- the far roofs (shore) must read lighter than the facades in front (mid), yet darker than the far city: roofs
    -- up from 45 %, facades down from 40 % (this script's shore haze is darker than its mid haze)
    fade = { shore = 0.70, mid = 0.25, back = 0.28 },  -- facades 0.25: back until their Aseprite redraw (owner, 23 Oct)
  },
}
Look.key = "riverwalk"
function Look.level(def) Look.key = ({ park = "citypark", town = "downtown" })[def.art] or "riverwalk" end
local function S() return Look.scripts[Look.key] end

local SRC = [[
extern vec3 haze; extern float k; extern float warm; extern float cool; extern float sat;
vec4 effect(vec4 color, Image tex, vec2 tc, vec2 sc) {
  vec4 c = Texel(tex, tc) * color;
  vec3 rgb = c.rgb;
  float L = dot(rgb, vec3(0.299, 0.587, 0.114));
  rgb = mix(vec3(L), rgb, sat);
  rgb += warm * L * L * vec3(0.080, 0.032, -0.048);
  rgb += cool * (1.0 - L) * (1.0 - L) * vec3(-0.030, -0.045, 0.085);
  rgb = mix(rgb, haze, k);
  return vec4(clamp(rgb, 0.0, 1.0), c.a);
}]]
local shader
function Look.use(name)
  if not Look.on then return end
  shader = shader or lg.newShader(SRC)
  local p = S().layers[name] or S().layers.play
  shader:send("haze", p.haze); shader:send("k", p.k); shader:send("warm", p.warm); shader:send("cool", p.cool); shader:send("sat", p.sat)
  lg.setShader(shader)
end
function Look.off() lg.setShader() end
function Look.toggle() Look.on = not Look.on; print("[look] " .. (Look.on and "lion king" or "as before")); io.stdout:flush() end

-- 3 the sky: bands from the script's top colour to its horizon colour, each split into flat steps (no dither since
-- 24 Oct). Painted once per level, screen-fixed.
-- (owner 24 Oct: the dotted rows between sky bands read as stripes) each band is split into Look.SKY_STEPS flat
-- sub-bands stepping evenly towards the next band's colour: a gradient in small flat steps, no dither
Look.SKY_STEPS = 4
local function skyRow(BANDS, cols, y)
  local i = 1
  while BANDS[i + 1] and y >= BANDS[i + 1][1] do i = i + 1 end
  if not BANDS[i + 1] then return cols[i] end
  local y0, y1 = BANDS[i][1], BANDS[i + 1][1]
  local k = math.floor((y - y0) * Look.SKY_STEPS / (y1 - y0)) / Look.SKY_STEPS
  local a, b = cols[i], cols[i + 1]
  return { a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k, a[3] + (b[3] - a[3]) * k }
end
local skies = {}
local function sky()
  if skies[Look.key] then return skies[Look.key] end
  local BANDS = S().bands
  local d = love.image.newImageData(320, 240)
  local cols = {}
  for i, b in ipairs(BANDS) do cols[i] = hex(b[2]) end
  for y = 0, 239 do
    local c = skyRow(BANDS, cols, y)
    for x = 0, 319 do d:setPixel(x, y, c[1], c[2], c[3], 1) end
  end
  local im = lg.newImage(d); im:setFilter("nearest", "nearest")
  skies[Look.key] = im
  return im
end
function Look.sky() lg.setColor(1, 1, 1, 1); lg.draw(sky(), 0, 0) end

-- a tall level's sky (art levels): the same bands with Look.SKY_ABOVE more rows above y 0, from the script's
-- `above` bands (or, without them, the top two bands' step carried on upwards, darker). Drawn from y -SKY_ABOVE.
Look.SKY_ABOVE = 120
local tallSkies = {}
function Look.skyTall()
  local key = Look.key
  if not tallSkies[key] then
    local S_ = S()
    local A, top = Look.SKY_ABOVE, S_.bands
    local above = S_.above
    if not above then                                               -- carry the top step on upwards
      above = {}
      local c0, c1 = hex(top[1][2]), hex(top[2][2])
      for i = 5, 1, -1 do
        local c = {}
        for j = 1, 3 do c[j] = math.max(0, math.min(1, c0[j] - (c1[j] - c0[j]) * i)) end
        above[#above + 1] = { -24 * i, string.format("%02x%02x%02x", math.floor(c[1] * 255 + 0.5), math.floor(c[2] * 255 + 0.5), math.floor(c[3] * 255 + 0.5)) }
      end
    end
    local BANDS = {}
    for _, b in ipairs(above) do if b[1] >= -A then BANDS[#BANDS + 1] = { b[1] + A, b[2] } end end
    for _, b in ipairs(top) do BANDS[#BANDS + 1] = { b[1] + A, b[2] } end
    local H = 240 + A
    local d = love.image.newImageData(320, H)
    local cols = {}
    for i, b in ipairs(BANDS) do cols[i] = hex(b[2]) end
    for y = 0, H - 1 do
      local c = skyRow(BANDS, cols, y)
      for x = 0, 319 do d:setPixel(x, y, c[1], c[2], c[3], 1) end
    end
    local im = lg.newImage(d); im:setFilter("nearest", "nearest")
    tallSkies[key] = im
  end
  lg.setColor(1, 1, 1, 1); lg.draw(tallSkies[key], 0, -Look.SKY_ABOVE)
end

-- 4 the road (rows 199-239 of the screen): row y scrolls ROAD_K * (y - 199) / 40 faster than the camera, so the
-- near edge of the road moves 1.3x and the far edge (the kerb) 1x, as a floor seen from a low camera does.
-- Drawn over the painted ground only on the stretches of road (the traffic's spans), from the same road tile;
-- the kerb and the pavement Pepper walks on stay at 1x.
-- The rows move in bands (as on the Mega Drive, which scrolls 8 px rows), so the lane markings (rows 219-220), the
-- manhole covers (203-209, 226-232) and the drains (200-202) each sit inside one band and never shear.
Look.ROAD_TOP, Look.ROAD_K = 199, 0.3
local ROAD_BANDS = { { 199, 203 }, { 203, 210 }, { 210, 219 }, { 219, 234 }, { 234, 240 } }
local function rawFactor(y) return 1 + Look.ROAD_K * math.max(0, math.min(1, (y - Look.ROAD_TOP) / 40)) end
function Look.rowFactor(y)
  if y < Look.ROAD_TOP then return 1 end
  for _, b in ipairs(ROAD_BANDS) do if y < b[2] then return rawFactor((b[1] + b[2] - 1) / 2) end end
  return rawFactor((234 + 239) / 2)                                  -- below the screen: the nearest band
end
local roadQ
function Look.road(stage, cam, Sc)
  if not stage.road then return end
  local A = Sc.art()
  local road = A.road
  local rw, rh = road:getDimensions()
  if not roadQ then roadQ = {}; for y = 0, rh - 1 do roadQ[y] = lg.newQuad(0, y, rw, 1, rw, rh) end end
  lg.setColor(1, 1, 1, 1)
  for _, sp in ipairs(stage.road.spans) do
    local a, b = math.max(sp[1], cam) - cam, math.min(sp[2], cam + 320) - cam
    if b > a then
      lg.setScissor(a, 0, b - a, 240)
      for r = 0, rh - 1 do
        local y = Look.ROAD_TOP + r
        local o = math.floor(cam * Look.rowFactor(y) + 0.5) % rw
        lg.draw(road, roadQ[r], -o, y); lg.draw(road, roadQ[r], rw - o, y)
      end
      for _, dc in ipairs(Sc.decals or {}) do                     -- manhole covers and drains ride with their row
        local f = Look.rowFactor(dc.y)
        lg.draw(dc.im, math.floor(dc.x - cam * f + 0.5), dc.y)
      end
      lg.setScissor()
    end
  end
end

-- 5 the foreground band: dark shapes near the camera, back-lit (a 1 px lighter rim on their tops): grass verges
-- with shrubs, pairs of bollards, chain fences (the script's kinds). Each clump belongs to a spot on flat ground at
-- Pepper's line (never in front of the river, a pond or the quay) and is exactly there when it is mid-screen; it
-- moves 1.4x, like the foreground props. Built once per level from a fixed seed, with open ground between clumps.
Look.FRONT_SPEED, Look.FRONT_TOP, Look.FRONT_TALL = 1.4, 218, 206
local function rng(seed) local s = seed return function(a, b) s = (s * 1103515245 + 12345) % 2147483648; return a + (s % 100000) / 100000 * (b - a) end end

local function clump(r, kind, w, h)
  local FG = S().fg
  local d = love.image.newImageData(w, h)
  local function put(x, y, c) if x >= 0 and x < w and y >= 0 and y < h then d:setPixel(x, y, c[1], c[2], c[3], 1) end end
  local function solid(x, y) if x < 0 or x >= w or y < 0 or y >= h then return false end local _, _, _, a = d:getPixel(x, y); return a > 0 end
  local function column(x, top, c) for y = math.max(0, math.floor(top)), h - 1 do put(x, y, c) end end
  local function shrub(cx, bw, bh)                                 -- a leafy shrub: a round crown with a scalloped edge
    local lobe = 0
    for x = math.floor(cx - bw / 2), math.floor(cx + bw / 2) do
      local u = (x - cx) / (bw / 2)
      if x % 3 == 0 then lobe = r(-2.2, 0.8) end                    -- the leaves: the edge steps every 3 px
      column(x, h - bh * math.sqrt(math.max(0, 1 - u * u)) + lobe, FG.dark)
    end
    for _ = 1, math.floor(bw / 4) do                                -- leaf clusters a shade lighter inside the crown
      local x, y = math.floor(cx + r(-bw / 2.8, bw / 2.8)), math.floor(h - r(3, bh * 0.75))
      if solid(x, y - 2) and solid(x - 2, y) and solid(x + 2, y) then put(x - 1, y, FG.mid); put(x, y, FG.mid); put(x + 1, y, FG.mid); put(x, y - 1, FG.mid) end
    end
  end
  local function blade(x, bh, lean, thick)                         -- a grass blade bending to one side; thick: 2 px low down
    for y = 0, bh - 1 do
      local bx = math.floor(x + lean * (y / bh) ^ 2 + 0.5)
      put(bx, h - 1 - y, FG.dark)
      if thick and y < bh * 0.6 then put(bx + 1, h - 1 - y, FG.dark) end
    end
  end
  local function bollard(x)                                        -- a street bollard: post with a round cap
    for y = h - 15, h - 1 do for dx = 0, 4 do put(x + dx, y, FG.dark) end end
    for dx = 1, 3 do put(x + dx, h - 16, FG.dark) end
    put(x + 1, h - 13, FG.mid); put(x + 1, h - 12, FG.mid)
  end
  if kind == "bollards" then bollard(1); bollard(w - 6)
  elseif kind == "chain" then                                      -- low posts with a chain sagging between them
    local n = math.max(2, math.floor((w - 4) / 18))
    local gap = (w - 4) / n
    for i = 0, n do
      local x = math.floor(2 + i * gap + 0.5)
      for y = h - 13, h - 1 do put(x - 1, y, FG.dark); put(x, y, FG.dark); put(x + 1, y, FG.dark) end
      put(x - 1, h - 14, FG.dark); put(x, h - 14, FG.dark); put(x + 1, h - 14, FG.dark); put(x, h - 15, FG.dark)
      if i < n then
        for dx = 2, math.floor(gap) - 2 do
          local u = dx / gap
          put(x + dx, math.floor(h - 11 + 4 * 4 * u * (1 - u) + 0.5), FG.dark)
        end
      end
    end
  else                                                             -- a verge: a low bank of grass, shrubs on it
    for x = 0, w - 1 do
      local e = math.min(x, w - 1 - x)                              -- the bank's ends slope down
      column(x, h - math.min(4, 1 + e / 3) - ((x % 7 < 3) and 1 or 0), FG.dark)
    end
    for x = 2, w - 3, 3 do                                          -- grass along it, now and then a tall spike
      local tall = r(0, 1) < 0.18
      blade(x + r(0, 1.5), tall and r(12, h - 1) or r(5, 10), r(-3.5, 3.5), tall or r(0, 1) < 0.4)
    end
    for _ = 1, math.floor(r(0, 2.6)) do local bw = math.floor(r(24, math.min(56 + (h - 22), w - 8))); shrub(r(bw / 2 + 2, w - bw / 2 - 2), bw, r(math.min(12, h - 10), h - 1)) end
  end
  for x = 0, w - 1 do                                              -- back light: the top pixel of each column
    for y = 0, h - 1 do
      if solid(x, y) then put(x, y, (r(0, 1) < FG.warmK) and FG.warm or FG.rim); break end
    end
  end
  local im = lg.newImage(d); im:setFilter("nearest", "nearest")
  return im
end

-- the stretches of flat ground at Pepper's line (terrain top y 184, or a tall level's path line foot), found as
-- the road's traffic finds them
local function flatSpans(world, foot)
  local spans, s = {}, nil
  for x = 0, world.width - 1, 4 do
    local flat = false
    for _, b in ipairs(world.rects) do if b.terrain and b.y0 == foot and x >= b.x0 and x < b.x1 then flat = true; break end end
    if flat and not s then s = x elseif not flat and s then spans[#spans + 1] = { s, x }; s = nil end
  end
  if s then spans[#spans + 1] = { s, world.width } end
  return spans
end
local function pick(r, kinds)
  local u, acc, last = r(0, 1), 0, nil
  for _, k in ipairs({ "bollards", "chain", "verge" }) do
    if kinds[k] then acc = acc + kinds[k]; last = k; if u < acc then return k end end
  end
  return last
end
local function buildFront(stage)
  local r, list = rng(1994), {}
  local kinds = S().kinds
  if next(kinds) == nil then return list end                       -- this level has no foreground band
  for _, sp in ipairs(flatSpans(stage.world, stage.def.foot or 184)) do
    local x = sp[1] + math.floor(r(20, 120))
    while true do
      local kind = pick(r, kinds)
      local w = (kind == "bollards") and math.floor(r(30, 38)) or (kind == "chain" and math.floor(r(60, 110)) or math.floor(r(60, 170)))
      if x + w > sp[2] - 10 then break end
      -- deep inside a stretch of flat ground Pepper only walks at y 184, so a clump may stand taller there (top
      -- y 206): wherever the 1.4x layer puts it on screen (at most 0.4 x (160 + w / 2) px from its spot) the
      -- flat ground is under it
      local m = 0.4 * (160 + w / 2) + 6
      local tall = kind == "verge" and x - m > sp[1] and x + w + m < sp[2] and r(0, 1) < 0.6
      local h = tall and (240 - Look.FRONT_TALL) or (240 - Look.FRONT_TOP)
      list[#list + 1] = { x = x, w = w, h = h, img = clump(r, kind, w, h) }
      x = x + w + math.floor(r(110, 260))                          -- open ground between them
    end
  end
  return list
end
function Look.front(stage, cam, camY)
  stage.lkFront = stage.lkFront or buildFront(stage)
  local bottom = (stage.def.foot or 184) + 56 - (camY or 0)        -- the screen y of the world's bottom row + 1 (a flat level: 240)
  lg.setColor(1, 1, 1, 1)
  local k = Look.FRONT_SPEED - 1
  for _, c in ipairs(stage.lkFront) do
    local mid = c.x + c.w / 2
    local sx = math.floor(c.x - cam - (cam + 160 - mid) * k + 0.5)
    if sx < 330 and sx + c.w > -10 then
      lg.draw(c.img, sx, bottom - c.h)
      if Look.CHECK then                                          -- LOOK_CHECK=1: report a clump over Pepper's box
        local x0, y0, x1, y1 = stage.pepper:box()
        if x1 - cam > sx and x0 - cam < sx + c.w and y1 + 2 - (camY or 0) > bottom - c.h then
          print(("LOOK OVERLAP clump at %d (top %d) over Pepper x %.0f y %.0f"):format(c.x, bottom - c.h, stage.pepper.x, stage.pepper.y)); io.stdout:flush()
        end
      end
    end
  end
end

return Look
