-- The Lion King look (branch lk/look, River Walk only; L / a shoulder button switches it off and on to compare).
-- What the 1994 game does, done here in code. Pepper, Mia, the ball, the bones and the HUD are never touched.
--   1 a colour script: the level has one key light (summer morning, warm) and one haze colour per distance,
--     instead of one cool grey haze for everything
--   2 split toning per layer (a shader): light colours lean warm, dark ones lean blue-violet, colours a bit
--     richer; the further back a layer is, the more it turns into its haze colour. Each colour in maps to one
--     colour out, so an asset keeps its number of colours. The art files are untouched.
--   3 a painted sky in bands, joined by 2 x 2 ordered dither rows (the 16-bit way to do a gradient)
--   4 the road recedes: each road row scrolls a little faster the nearer it is (row scrolling, like the river),
--     and the near-lane traffic slides with its row
--   5 a dark foreground band at the bottom (shrubs, grass, bollards) that scrolls 1.4x, only in front of the road.
--     Its tops are at y 218 or lower (under Pepper's lowest walking line, the lower quay at y 216), or y 206 deep
--     inside a stretch of road, where she walks at y 184. It never covers her.
local Look = { on = true, CHECK = os.getenv("LOOK_CHECK") ~= nil }
local lg = love.graphics
local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end

-- per layer: warm = how far light colours lean to warm, cool = how far dark ones lean to blue-violet,
-- sat = colour richness (1 = as drawn), haze / k = the layer's distance colour and how much of it
Look.layers = {
  clouds = { warm = 0.9, cool = 1.6, sat = 1.0, haze = hex("f7ead2"), k = 0.10 },
  city   = { warm = 0.2, cool = 1.8, sat = 0.70, haze = hex("aaa6d0"), k = 0.46 },
  shore  = { warm = 0.5, cool = 1.5, sat = 1.05, haze = hex("9fb3cc"), k = 0.30 },
  water  = { warm = 0.5, cool = 1.2, sat = 1.35, haze = hex("8fb4d8"), k = 0.06 },
  back   = { warm = 1.0, cool = 1.2, sat = 1.35, haze = hex("f0e0c6"), k = 0.10 },
  ground = { warm = 0.75, cool = 1.3, sat = 1.20, haze = hex("000000"), k = 0 },
  play   = { warm = 0.7, cool = 0.8, sat = 1.18, haze = hex("000000"), k = 0 },
  front  = { warm = 0.0, cool = 1.8, sat = 1.10, haze = hex("1b1934"), k = 0.40 },
}

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
  local p = Look.layers[name]
  shader:send("haze", p.haze); shader:send("k", p.k); shader:send("warm", p.warm); shader:send("cool", p.cool); shader:send("sat", p.sat)
  lg.setShader(shader)
end
function Look.off() lg.setShader() end
function Look.toggle() Look.on = not Look.on; print("[look] " .. (Look.on and "lion king" or "as before")); io.stdout:flush() end

-- 3 the sky: bands from deep summer blue at the top to warm cream at the horizon (behind the skyline, y 138).
-- Between two bands, 3 rows of 2 x 2 ordered dither (25 %, 50 %, 75 %). Painted once, screen-fixed.
local BANDS = { { 0, "4b7ec2" }, { 16, "5a8aca" }, { 32, "6b98d1" }, { 48, "80a8d7" }, { 62, "98b8db" },
                { 76, "b2c6da" }, { 89, "cbd1d4" }, { 101, "dfd7c9" }, { 112, "ecdabd" }, { 122, "f4dcb3" } }
local BAYER = { [0] = { [0] = 0, 2 }, { [0] = 3, 1 } }               -- 2 x 2 order: 0 .. 3
local skyImg
local function sky()
  if skyImg then return skyImg end
  local d = love.image.newImageData(320, 240)
  local cols = {}
  for i, b in ipairs(BANDS) do cols[i] = hex(b[2]) end
  for y = 0, 239 do
    local i = 1
    while BANDS[i + 1] and y >= BANDS[i + 1][1] do i = i + 1 end
    local nxt = BANDS[i + 1] and (BANDS[i + 1][1] - y) or 99       -- rows until the next band starts
    local lvl = (nxt <= 3) and (4 - nxt) or 0                       -- 1, 2, 3 = 25, 50, 75 % of the next colour
    for x = 0, 319 do
      local c = cols[i]
      if lvl > 0 and BAYER[y % 2][x % 2] < lvl then c = cols[i + 1] end
      d:setPixel(x, y, c[1], c[2], c[3], 1)
    end
  end
  skyImg = lg.newImage(d); skyImg:setFilter("nearest", "nearest")
  return skyImg
end
function Look.sky() lg.setColor(1, 1, 1, 1); lg.draw(sky(), 0, 0) end

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
-- with shrubs, and pairs of bollards. Each clump belongs to a spot on the road (never in front of the river or the
-- quay) and is exactly there when it is mid-screen; it moves 1.4x, like the foreground props. Built once from a
-- fixed seed, with open road between the clumps.
Look.FRONT_SPEED, Look.FRONT_TOP, Look.FRONT_TALL = 1.4, 218, 206
local FG = { dark = hex("161c2c"), mid = hex("1f2b42"), rim = hex("4c5d7c"), warm = hex("9a8174") }
local function rng(seed) local s = seed return function(a, b) s = (s * 1103515245 + 12345) % 2147483648; return a + (s % 100000) / 100000 * (b - a) end end

local function clump(r, kind, w, h)
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
      if solid(x, y) then put(x, y, (r(0, 1) < 0.05) and FG.warm or FG.rim); break end
    end
  end
  local im = lg.newImage(d); im:setFilter("nearest", "nearest")
  return im
end

local function buildFront(stage)
  local r, list = rng(1994), {}
  for _, sp in ipairs(stage.road and stage.road.spans or {}) do
    local x = sp[1] + math.floor(r(20, 120))
    while true do
      local bol = r(0, 1) < 0.22
      local w = bol and math.floor(r(30, 38)) or math.floor(r(60, 170))
      if x + w > sp[2] - 10 then break end
      -- deep inside a stretch of road Pepper only walks at y 184, so a clump may stand taller there (top y 206):
      -- wherever the 1.4x layer puts it on screen (at most 0.4 x (160 + w / 2) px from its spot) the road is under it
      local m = 0.4 * (160 + w / 2) + 6
      local tall = not bol and x - m > sp[1] and x + w + m < sp[2] and r(0, 1) < 0.6
      local h = tall and (240 - Look.FRONT_TALL) or (240 - Look.FRONT_TOP)
      list[#list + 1] = { x = x, w = w, h = h, img = clump(r, bol and "bollards" or "verge", w, h) }
      x = x + w + math.floor(r(110, 260))                          -- open road between them
    end
  end
  return list
end
function Look.front(stage, cam)
  stage.lkFront = stage.lkFront or buildFront(stage)
  lg.setColor(1, 1, 1, 1)
  local k = Look.FRONT_SPEED - 1
  for _, c in ipairs(stage.lkFront) do
    local mid = c.x + c.w / 2
    local sx = math.floor(c.x - cam - (cam + 160 - mid) * k + 0.5)
    if sx < 330 and sx + c.w > -10 then
      lg.draw(c.img, sx, 240 - c.h)
      if Look.CHECK then                                          -- LOOK_CHECK=1: report a clump over Pepper's box
        local x0, y0, x1, y1 = stage.pepper:box()
        if x1 - cam > sx and x0 - cam < sx + c.w and y1 + 2 > 240 - c.h then
          print(("LOOK OVERLAP clump at %d (top %d) over Pepper x %.0f y %.0f"):format(c.x, 240 - c.h, stage.pepper.x, stage.pepper.y)); io.stdout:flush()
        end
      end
    end
  end
end

return Look
