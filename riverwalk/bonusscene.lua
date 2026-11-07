-- bonusscene.lua: where FETCH FRENZY (bonus.lua) is played. Owner, 7 Nov, on a round after River Walk that was set
-- in City Park: "these levels should have different scenery". Each round is now set in the place of the level it
-- follows: one calm, flat, open 320 x 240 screen built only from that level's own approved art and its colour
-- script (look.lua), nothing new drawn as art. What is code here is geometry by rule (a kerb, a coping) in the
-- level's own colours.
--   The play floor is the same in every scene: flat at y 184, the screen's edges as walls (bonus.lua B.world).
--   Nothing stands on it: decoration is behind Pepper's line (the railing, far rows) or below it (the front edge).
--   Every ground has a finished front edge (owner 7 Nov: no "cut" joins, no stack of flat earth stripes):
--     River Walk  the promenade's paving, its granite coping, the quay wall under it (Sc.paintQuay's own rule)
--     City Park   the path, a granite kerb (the park stone's greys), the lawn on to the bottom, a few leaves
--     Downtown    the street's setts and kerb, the quay wall under it in its own granite greys (town_ground.png)
-- Rooftops, Söder Hill and Night Harbour have no art key and no colour script yet (greybox levels), so their rounds
-- use the nearest level's place (BS.BY_LEVEL); change the line when their art lands.
local Sc = require("scene")
local Look = require("look")
local lg = love.graphics
local BS = {}
BS.__index = BS

BS.FEET = 184
-- the scene of each level's round, by level number (levels.lua)
BS.BY_LEVEL = {
  [1] = "riverwalk",    -- River Walk: the riverside promenade, summer morning
  [2] = "citypark",     -- City Park: the park lawn, autumn afternoon
  [3] = "downtown",     -- Downtown: an old town square, midday
  [4] = "downtown",     -- Rooftops (fallback): it climbs from Downtown's street; the square under the roofs
  [5] = "citypark",     -- Söder Hill (fallback): a hill park; City Park's lawn
  [6] = "riverwalk",    -- Night Harbour (fallback): a quay by the water; River Walk's promenade (no night script yet)
}
BS.FALLBACK = { [4] = true, [5] = true, [6] = true }
BS.ART = { riverwalk = nil, citypark = "park", downtown = "town" }   -- the art key, which picks the colour script
function BS.keyFor(levelNumber) return BS.BY_LEVEL[levelNumber or 2] or "citypark" end

local cache = {}                                                   -- the built scenes, one per key (and look on/off)
function BS.get(key)
  local k = key .. (Look.on and "" or "/classic")
  if not cache[k] then cache[k] = setmetatable({ key = key }, BS) end
  return cache[k]
end

-- the floor every scene stands on (as bonus.lua's B.world)
local function flatWorld()
  local Wd = require("world")
  local w = setmetatable({ rects = { { x0 = 0, x1 = 320, y0 = BS.FEET, y1 = 240, kind = "solid", terrain = true } },
    slopes = {}, water = {}, movers = {} }, Wd)
  w.cols, w.rows, w.width, w.height = 40, 30, 320, 240
  return w
end

-- a canvas painted once, under the back layer's grade as the levels paint their ground (stage.lua: the ground is
-- graded twice, painted under "back" and drawn under "ground", and its colours are tuned for that)
local function painted(paint)
  local cv = lg.newCanvas(320, 240); cv:setFilter("nearest", "nearest")
  lg.push("all"); lg.setCanvas(cv); lg.clear(0, 0, 0, 0); lg.origin()
  Look.use("back"); lg.setColor(1, 1, 1, 1)
  paint()
  lg.pop()
  return cv
end

local function hexc(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end
local function rect(c, x, y, w, h) lg.setColor(c); lg.rectangle("fill", x, y, w, h) end
local function rng(seed) local s = seed return function(a, b) s = (s * 1103515245 + 12345) % 2147483648; return a + (s % 100000) / 100000 * (b - a) end end

-- the art level's ground tile (park_ground.png / town_ground.png) across the screen, its top 12 px above the feet,
-- rows 0 .. rows - 1 only
local function tileFloor(style, rows)
  local T = Sc.townArt(style)
  local gw, gh = T.ground:getDimensions()
  rows = math.min(rows or gh, gh)
  local q = lg.newQuad(0, 0, gw, rows, gw, gh)
  for x = 0, 319, gw do lg.draw(T.ground, q, x, BS.FEET - 12) end
end

---------------------------------------------------------------------------------------------------- River Walk
-- The promenade by the river: River Walk's sky, clouds, skyline, far shore and bridge, the river (Sc.drawFar), the
-- railing along the water on the paving's back edge, and the paving with its coping and the quay wall under it, by
-- the level's own rule (Sc.paintQuay, the lower quay's kind).
local function buildRiverwalk(s)
  s.layers = Sc.build(320)
  s.rail = Sc.railing(340, "decor")
  local keepD, keepR, keepS = Sc.decals, Sc.roadEnds, Sc.roadOnSegs  -- (paintQuay resets the level's road decals)
  Look.use("back")                                                 -- (painted under the back grade, as in the level)
  local g = Sc.paintQuay(flatWorld(), {}, { ground = "quay", quayFront = true })
  Look.off()
  s.ground = g.chunks[1].cv                                        -- (one 320 x 240 chunk at 0, 0)
  Sc.decals, Sc.roadEnds, Sc.roadOnSegs = keepD, keepR, keepS
end
local function farRiverwalk(s, t)
  Sc.drawFar(s.layers, 0, t)
  Look.use("back"); lg.setColor(1, 1, 1, 1)
  lg.draw(s.rail, -6, BS.FEET - 10 - s.rail:getHeight())          -- (River Walk's railing: its foot on y 174)
end

---------------------------------------------------------------------------------------------------- City Park
-- The park lawn: City Park's sky, skyline, far tree line and round trees (Sc.drawFarArt), the lawn and the path
-- (park_ground.png rows 0-28), then the path's front edge by rule, in the park's own colours. Round 2 (7 Nov): no
-- dark foreground clumps (the owner called City Park's black front shapes "terrible", 11:27), no full-width bands.
--   a kerb of granite setts in the park stone's greys (park_stone.png): a lit top, the face, a shaded foot, joints
--   every 12 px; grass tufts with lit tips lean over its foot so the lawn meets it without a cut
--   the lawn runs on to the bottom of the screen: tufts (a lit pair over a dark pair, about 8 px apart, each moved
--   0-3 px and one in five left out) in offset rows that come closer together towards the bottom (the lawn nearer
--   the eye), and a few fallen leaves in the leaf
--   piles' colours (park_leaves.png), single leaves only (a pile would read as a bone's hiding place)
-- (An earth bank under a stepped verge edge was tried and dropped: graded as the ground it read as a plum band,
-- docs/review/07nov/bonusscene/round2_citypark_options_3x.png.)
local PK = { top = hexc("c9c2b4"), face1 = hexc("b3ac9f"), face = hexc("a39b8e"), foot = hexc("7a736a"), joint = hexc("5d5953"),
             lawn = hexc("9e983f"), lawnD = hexc("867744"), lawnL = hexc("b5ad55"), seam = hexc("665c3b"),
             leaf = { hexc("fb8c29"), hexc("fec244"), hexc("ec6e1f"), hexc("c6261b") }, leafL = hexc("fec244"), leafD = hexc("7d1812") }
BS.PARK_KERB = BS.FEET + 17                                         -- the kerb's top row (the path's tile rows end above it)
BS.PARK_TUFTS = { { 3, 0 }, { 8, 4 }, { 14, 2 }, { 19, 6 }, { 23, 1 }, { 27, 5 }, { 30, 3 }, { 33, 7 } }   -- { rows under the verge's top, x offset }
-- a leaf (5 x 3, its stem dark), drawn as is or mirrored: { x, y } as placed, colour i
local LEAF = { ".lc..", "cccck", ".kc.." }
BS.PARK_LEAVES = { { 19, 213, 1 }, { 61, 226, 2, true }, { 97, 217, 3 }, { 129, 233, 4, true }, { 168, 221, 1 },
                   { 205, 230, 3, true }, { 244, 215, 2 }, { 281, 227, 4 }, { 306, 235, 1, true }, { 2, 234, 3 } }
local function parkFront()
  local y0 = BS.PARK_KERB
  rect(PK.top, 0, y0, 320, 1); rect(PK.face1, 0, y0 + 1, 320, 1); rect(PK.face, 0, y0 + 2, 320, 1)
  rect(PK.foot, 0, y0 + 3, 320, 1); rect(PK.seam, 0, y0 + 4, 320, 1)
  for x = 6, 319, 12 do rect(PK.face, x, y0, 1, 1); rect(PK.joint, x, y0 + 1, 1, 3) end
  rect(PK.lawn, 0, y0 + 5, 320, 240 - y0 - 5)                      -- the lawn, on to the bottom
  for x = 2, 319, 8 do                                             -- grass over the kerb's foot: 2 px tufts, lit tips
    local h = ({ 2, 1, 2, 2, 1, 2, 1, 2 })[math.floor(x / 8) % 8 + 1]
    rect(PK.lawn, x, y0 + 5 - h, 2, h); rect(PK.lawnL, x, y0 + 5 - h, 2, 1)
  end
  local r = rng(1107)                                               -- (round 3) off the 8 px grid: each tuft moved
  for _, rw in ipairs(BS.PARK_TUFTS) do                            -- 0-3 px, one in five left out (no dot screen)
    for x = rw[2], 319, 8 do
      local jx, drop = math.floor(r(0, 4)), r(0, 1) < 0.2
      if not drop then rect(PK.lawnL, x + jx, y0 + 5 + rw[1], 2, 1); rect(PK.lawnD, x + jx, y0 + 6 + rw[1], 2, 1) end
    end
  end
  for _, l in ipairs(BS.PARK_LEAVES) do
    for r, row in ipairs(LEAF) do
      for i = 1, #row do
        local ch = row:sub(i, i)
        local c = (ch == "c" and PK.leaf[l[3]]) or (ch == "l" and PK.leafL) or (ch == "k" and PK.leafD) or nil
        if c then rect(c, l[1] + (l[4] and (#row - i) or (i - 1)), l[2] + r - 2, 1, 1) end
      end
    end
  end
end
local function buildCitypark(s)
  s.layers = Sc.buildArt(320, "park")
  s.world = flatWorld()
  s.ground = painted(function() tileFloor("park", BS.PARK_KERB - (BS.FEET - 12)); parkFront() end)
end
local function farCitypark(s, t) Sc.drawFarArt(s.layers, 0, t, s.world) end

---------------------------------------------------------------------------------------------------- Downtown
-- An old town square at midday, from the rebuilt Downtown (day/07nov-dt, merged 7 Nov): Downtown's painted sky and
-- clouds, its low painted skyline, and across the square the level's new mid row (town_facades.png: big pastel
-- houses at half scale, crow steps, Dutch gables and hips, a door in every ground floor), faded and graded as the
-- level's mid layer. Its ground floors stand on the square's far kerb (town_square_floor.png, its row 21), so every
-- house ends in its door and plinth on the kerb, not on a cut. Then the square's setts under the back grade, the
-- bollards, the lamp post, the street's setts and kerb and the granite quay wall (town_ground.png) as before.
-- The row's file is three storeys of 64 px (250 px tall): with its foot on the kerb its gables would be off the top
-- of the screen, the sky and the skyline hidden (with one upper storey kept the gables are still cut by the top
-- edge: docs/review/07nov/bonusscene/round4/storeys_0_1_2_2x.png). Its two upper storeys are pixel-identical stamped
-- bands (tools/build_dt_rooftops.py), so the bonus keeps BS.DT_STOREYS of them (0) when it loads the row: the same
-- houses, each its ground floor under its gable, whole pixels, nothing redrawn or scaled, the file untouched. The
-- gables then stand in the sky with the low skyline between them. Keep the Downtown part here.
BS.DT_KERB = 164                                                    -- the square's far kerb: the row's ground floors on it
BS.DT_X = 0                                                         -- the row's first column (a house's edge)
BS.DT_FLOOR_X = 28                                                  -- the floor's first column: its bollards (every 64 px)
                                                                    -- at x 2, 66, 130, 194, 258, clear of the row's doors
BS.DT_WALL = 30                                                     -- town_ground.png's kerb face, then the quay wall
BS.DT_STOREYS = 0                                                   -- upper storeys kept (the file has 2 over the ground floor)
BS.DT_STOREY, BS.DT_WALLTOP = 64, 58                                -- (the file's storey height and its walls' top row)
local function farDowntown(s, t)
  Sc.skyAndClouds(s.layers, 0, t)
  local city = Look.skyline(Sc.art().skyline)                      -- (the painted far city; it sets the city grade)
  lg.setColor(1, 1, 1, 1)
  lg.draw(city, 0, s.cornice + 4 - city:getHeight())               -- (its foot just under the row's cornice: it shows
  Look.use("mid")                                                  -- between and over the gables)
  Sc.strip(s.row, BS.DT_X, 1, BS.DT_KERB)
  -- (round 3, review: under the mid grade its setts were smothered, a flat pale stripe) the square's floor is the
  -- ground plane a few metres behind Pepper: the back row, unfaded, under the back grade, so its kerb and setts show
  Look.use("back"); Sc.strip(s.floor, BS.DT_FLOOR_X, 1, BS.DT_KERB - 21 + s.floor:getHeight())   -- (row 21: the kerb)
  Look.off()
end
-- the mid row as the bonus stands it: the gables and cornice (rows 0 .. walls' top - 1), BS.DT_STOREYS upper storeys,
-- the ground floor; faded to the mid haze as the level loads it
local function midRow()
  local src = love.image.newImageData("art/scene/town_facades.png")
  local w, h = src:getDimensions()
  local keep = BS.DT_WALLTOP + BS.DT_STOREY * BS.DT_STOREYS
  local out = love.image.newImageData(w, keep + BS.DT_STOREY)
  out:paste(src, 0, 0, 0, 0, w, keep)
  out:paste(src, 0, keep, 0, h - BS.DT_STOREY, w, BS.DT_STOREY)
  local im = lg.newImage(Sc.fadeData(out, nil, "mid")); im:setFilter("nearest", "nearest")
  return im, BS.DT_KERB - out:getHeight() + BS.DT_WALLTOP - 4        -- (the cornice's top row on screen)
end
local function buildDowntown(s)
  s.layers = Sc.buildArt(320, "town")
  s.row, s.cornice = midRow()
  s.floor = lg.newImage("art/scene/town_square_floor.png"); s.floor:setFilter("nearest", "nearest")
  s.ground = painted(function() tileFloor("town", BS.DT_WALL) end)
  -- (round 2, 7 Nov) the kerb's face and the quay wall in their own granite greys: graded twice like the street
  -- (painted under "back", drawn under "ground") their darks lean violet, a purple brick band. Drawn as the file has them
  local T = Sc.townArt("town")
  local gw, gh = T.ground:getDimensions()
  s.top = lg.newCanvas(320, 240); s.top:setFilter("nearest", "nearest")
  lg.push("all"); lg.setCanvas(s.top); lg.clear(0, 0, 0, 0); lg.origin(); lg.setShader(); lg.setColor(1, 1, 1, 1)
  local q = lg.newQuad(0, BS.DT_WALL, gw, gh - BS.DT_WALL, gw, gh)
  for x = 0, 319, gw do lg.draw(T.ground, q, x, BS.FEET - 12 + BS.DT_WALL) end
  lg.pop()
end

----------------------------------------------------------------------------------------------------
-- (round 3, review) one approved prop behind the line per scene, so each round says its place: River Walk's and
-- Downtown's lamp post at the far left (the levels' lamp, faded as their back decoration, unlit), City Park's bench
-- on the back lawn at the right (faded to the back haze like the back decoration). Feet as in the levels: River
-- Walk's back edge y 174, the art levels' lawn and pavement edge y 172. Nothing on the play floor, no collision.
BS.PROPS = {
  riverwalk = { { "lamp_post", 3, BS.FEET - 10, shadow = 14 } },                  -- { art, x, foot }, its shadow as
  citypark  = { { "bench", 250, BS.FEET - 12, fade = true, shadow = 107, depth = 5 } },   -- stage.lua draws it
  downtown  = { { "lamp_post", 3, BS.FEET - 12, shadow = 14 } },
}
local function buildProps(s)
  s.props = {}
  local A = Sc.art()
  for _, p in ipairs(BS.PROPS[s.key] or {}) do
    local im = A[p[1]]
    if p.fade then                                                 -- (the bench is an obstacle in River Walk: here it
      im = lg.newImage(Sc.fadeData(love.image.newImageData("art/scene/" .. p[1] .. ".png"), nil, "back"))   -- is back
      im:setFilter("nearest", "nearest")                           -- decoration, so it takes the back's fade)
    end
    s.props[#s.props + 1] = { im = im, x = p[2], foot = p[3], shadow = p.shadow, depth = p.depth }
  end
end
local function drawProps(s)
  for _, p in ipairs(s.props) do Sc.shadow(p.x + p.im:getWidth() / 2, p.foot - 1, p.shadow, p.depth) end
  Look.use("back"); lg.setColor(1, 1, 1, 1)
  for _, p in ipairs(s.props) do lg.draw(p.im, p.x, p.foot - p.im:getHeight()) end
  Look.off()
end

local BUILD = { riverwalk = buildRiverwalk, citypark = buildCitypark, downtown = buildDowntown }
local FAR = { riverwalk = farRiverwalk, citypark = farCitypark, downtown = farDowntown }

-- the whole scene behind the round: far layers, back decoration, the ground and its front edge
function BS:draw(t)
  Look.level({ art = BS.ART[self.key] })
  Sc.FOOT = BS.FEET
  if not self.built then BUILD[self.key](self); buildProps(self); self.built = true end
  FAR[self.key](self, t or 0)
  Look.use("ground"); lg.setColor(1, 1, 1, 1)
  lg.draw(self.ground, 0, 0)
  Look.off(); lg.setColor(1, 1, 1, 1)
  if self.top then lg.draw(self.top, 0, 0) end                    -- (no grade: the file's own colours)
  drawProps(self)                                                  -- (after the ground, as the levels draw their lamps)
end

return BS
