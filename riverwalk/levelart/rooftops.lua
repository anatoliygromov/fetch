-- Level art for Rooftops (levelart.lua; 8 Nov 2026, phase 1, 0 credits). Each part is added as it passes QA; stage.lua
-- draws the greybox for any part this module does not have. Design target: art/gen/concepts/rt_hotel_concept_a.png
-- (reference only): Stockholm old-town roofs on a warm late afternoon.
--   A    drawProp: the props without their printed names (the greybox labels are a debug view, audit RW1)
--   C+D  paintGround: the houses, roofs, stairs, chimneys, skylights and the street, BUILT by rule from the map by
--        tools/build_rooftops_art.py into 512 px chunks (levelart/rooftops/ground_<x>_<y>.png, manifest.lua). If the
--        map has changed since the build (its surface key differs), the greybox ground is drawn and a line printed:
--        run the tool again.
--   E    drawFar: the painted sky, the far town (the German Church's spire, the Great Church's tower), the mid town and
--        the back row of houses behind the roofs, from tools/build_rooftops_backdrop.py (backdrop.lua). The sky and
--        the far town rise 0.03 of the camera's climb, the mid town 0.06, each strip filled to its bottom, so nothing
--        hangs over empty sky at any tier; the back row moves with the world. The nest chimney's far copy (the goal
--        in view from below) stands on the far town's roofs, between the far and the mid town.
--   B    drawBack, drawProp, drawLamp: holders by rule (posts to the floor below, brackets into a wall, rails under
--        loose tiles), the slabs as stone, timber, copper or striped canvas, built stand-ins for the decor and the
--        solid props, the approved lamp post standing on its roof
--   look the level's colour script (look.lua format): warm late-afternoon light between Downtown's midday and Söder's
--        evening
local Sc = require("scene")
local lg = love.graphics
local DIR = "levelart/rooftops/"
local M = {}
M.__index = M

local function hex(h) return { tonumber(h:sub(1, 2), 16) / 255, tonumber(h:sub(3, 4), 16) / 255, tonumber(h:sub(5, 6), 16) / 255 } end
local function L(warm, cool, sat, haze, k, clean) return { warm = warm, cool = cool, sat = sat, haze = hex(haze), k = k, clean = clean or 0 } end
-- the colour script: light colours lean warm, darks a little cool; the haze per layer is the sky's warm horizon
M.look = {                                                       -- (sky, far and mid: as built, neutral)
  layers = { clouds = L(0, 0, 1.0, "000000", 0), city = L(0, 0, 1.0, "000000", 0),
             shore = L(0, 0, 1.0, "000000", 0), mid = L(0, 0, 1.0, "000000", 0),
             water = L(0.4, 1.2, 1.2, "8fb4d8", 0.05), back = L(0.1, 0.3, 1.0, "f6e0c0", 0.04),
             ground = L(0.1, 0.4, 1.10, "000000", 0), play = L(0.3, 0.6, 1.12, "000000", 0),
             front = L(0.0, 1.6, 1.10, "1e1620", 0.40) },
  bands = { { 0, "f0c79c" }, { 60, "f6d2a6" }, { 120, "fbdcac" }, { 180, "fde6b6" } },
  fg = { dark = hex("1e1620"), mid = hex("2c2030"), rim = hex("5a4250"), warm = hex("b07848"), warmK = 0.1 },
  kinds = {},                                                     -- no dark foreground band (the roofs are the frame)
  fade = { back = 0.12 },
}

function M.new(stage) return setmetatable({ stage = stage, def = stage.def, world = stage.world }, M) end

local function img(f) local i = lg.newImage(DIR .. f); i:setFilter("nearest", "nearest"); return i end

-- E: the backdrop (screen space; the back row in world space)
M.SKY_RISE, M.FAR_RISE, M.MID_RISE = 0.03, 0.03, 0.06           -- of the camera's climb from the bottom of the world
M.FAR_Y, M.MID_Y = 6, 70                                         -- the strips' top rows on screen at the bottom tier
M.FAR_X, M.MID_X, M.SKY_X, M.SKY_DRIFT = 0.1, 0.5, 0.05, 2
local quads = {}
local function strip(im, ox, y)                                  -- a wrapping strip, ox px into it, top at screen y
  local w, h = im:getDimensions()
  ox = math.floor(ox) % w
  local key = tostring(im)
  quads[key] = quads[key] or { lg.newQuad(0, 0, 1, 1, w, h), lg.newQuad(0, 0, 1, 1, w, h) }
  local a, b = quads[key][1], quads[key][2]
  local n = math.min(320, w - ox)
  a:setViewport(ox, 0, n, h, w, h); lg.draw(im, a, 0, y)
  if n < 320 then b:setViewport(0, 0, 320 - n, h, w, h); lg.draw(im, b, n, y) end
end
function M:backdrop()
  if self.bd ~= nil then return self.bd end
  local ok, man = pcall(require, "levelart.rooftops.backdrop")
  if not ok then self.bd = false; return false end
  local bd = { sky = img(man.sky), far = img(man.far), mid = img(man.mid), back = {} }
  for _, c in ipairs(man.back) do bd.back[#bd.back + 1] = { im = img(c.file), x = c.x, y = c.y, w = c.w, h = c.h } end
  self.bd = bd
  return bd
end
-- the goal from below: while the nest is above the screen, a far copy of the nest chimney stands among the far
-- roofs (far colours, no outline), the gull circling over it. It slides with the far town.
local FARC = { hex("e2bca4"), hex("d6ae96"), hex("c8a088") }
function M:drawLandmark(cam, camY, t, yf)
  local m = self.def.magpie and self.def.magpie.perches and self.def.magpie.perches[1]
  if not m or m.y > camY + 8 then return end
  local sx = math.floor(160 + (m.x - (cam + 160)) * 0.3 + 0.5)
  if sx < -20 or sx > 340 then return end
  local base = yf + 110                                           -- the far roofs' eaves row
  lg.setColor(FARC[1]); lg.rectangle("fill", sx - 4, base - 40, 8, 40)          -- the chimney
  lg.setColor(FARC[2]); lg.rectangle("fill", sx + 2, base - 40, 2, 40)
  lg.setColor(FARC[1]); lg.rectangle("fill", sx - 6, base - 42, 12, 2)
  lg.setColor(FARC[3]); lg.rectangle("fill", sx - 6, base - 45, 12, 3)            -- the nest
  lg.rectangle("fill", sx - 7, base - 44, 14, 1)
  local fl = math.floor(t * 6) % 2                                -- the gull, circling
  local gx, gy = math.floor(sx + math.cos(t * 1.2) * 14), math.floor(base - 56 + math.sin(t * 2.4) * 3)
  lg.setColor(FARC[3])
  lg.rectangle("fill", gx - 3, gy - fl, 3, 1); lg.rectangle("fill", gx + 1, gy - fl, 3, 1); lg.rectangle("fill", gx, gy, 1, 1)
end
function M:drawFar(cam, camY, t)
  local bd = self:backdrop()
  if not bd then return Sc.drawFarGrey(self.stage.layers, cam, t) end
  local Look = require("look")
  local rel = math.max(0, (self.stage.camYMax or 0) - camY)
  lg.setColor(1, 1, 1, 1)
  Look.use("clouds")
  local sy = -120 + math.floor(rel * M.SKY_RISE + 0.5)
  strip(bd.sky, cam * M.SKY_X + t * M.SKY_DRIFT, sy)
  if sy > 0 then lg.setColor(bd.skyTop or { 0.94, 0.77, 0.65 }); lg.rectangle("fill", 0, 0, 320, sy); lg.setColor(1, 1, 1, 1) end
  Look.use("city")
  local yf = M.FAR_Y + math.floor(rel * M.FAR_RISE + 0.5)
  strip(bd.far, cam * M.FAR_X, yf)
  Look.off(); self:drawLandmark(cam, camY, t, yf); lg.setColor(1, 1, 1, 1)
  Look.use("mid")
  strip(bd.mid, cam * M.MID_X, M.MID_Y + math.floor(rel * M.MID_RISE + 0.5))
  Look.use("back")                                                -- the back row, with the world
  lg.push(); lg.translate(-cam, -camY)
  for _, c in ipairs(bd.back) do
    if c.x - cam < 320 and c.x + c.w - cam > 0 and c.y - camY < 240 and c.y + c.h - camY > 0 then lg.draw(c.im, c.x, c.y) end
  end
  lg.pop()
  Look.off(); lg.setColor(1, 1, 1, 1)
end

-- the decor boxes that name a building the ground and the back row now draw (E): not drawn
M.BUILT = { CAFE = true, ["STAIRWELL A"] = true, BAKERY = true, ["MARKET HALL"] = true, LAUNDRY = true, ["ROOF BAR"] = true,
  HOTEL = true, ["LIGHT COURT"] = true, ["TALL BLOCK"] = true, ["CHIMNEY STACKS"] = true, ["SAUNA ROOF"] = true,
  ["THE LONG ROOF"] = true }
-- B: holders, contacts and built stand-ins (code, the tool's palette PAL carried by manifest.lua). Every slab is held:
-- posts down to the floor under it (the terrain or a solid prop, never a loose tile or another slab) at both ends and
-- at most 64 px apart, or, where a wall stands at its end, an iron bracket into that wall; every run of loose tiles
-- lies on an iron rail from ledge to ledge (it stays when a tile falls); the light court's post runs up to its balcony.
-- Slabs Pepper uses are obstacles: an unbroken 1 px ink outline, the top row over the box's top - 1. Holders and
-- the decor stand-ins are decoration: no outline, their edges a darker shade of their own colour.
local P = {}                                                      -- the palette, by name (manifest.lua's pal)
local function col(n) lg.setColor(P[n]) end
local function rect(n, x, y, w, h) if w > 0 and h > 0 then col(n); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end end
function M:palette()
  if next(P) then return true end
  local ok, man = pcall(require, "levelart.rooftops.manifest")
  if not ok then return false end
  for k, v in pairs(man.pal) do P[k] = hex(v) end
  return true
end
local SLAB = { BALCONY = "stone", ["COPPER ROOF"] = "copper", AWNING = "awning", ["CAFE AWNING"] = "awning" }
local function material(pr) return SLAB[pr.name] or "timber" end
-- the first floor at or under y in column x: the terrain's top, or a solid prop's (not a loose tile, not a slab)
function M:floorBelow(x, y)
  local best
  for _, m in ipairs(Sc.columnRuns(self.world, math.floor(x), "all")) do if m[1] >= y and (not best or m[1] < best) then best = m[1] end end
  for _, q in ipairs(self.def.props) do
    if q.kind == "solid" and x >= q.x0 and x < q.x1 and q.y0 >= y and (not best or q.y0 < best) then best = q.y0 end
  end
  return best
end
function M:wallAt(x, y)                                           -- terrain standing up past y in column x
  local r = Sc.columnRuns(self.world, math.floor(x), "all")[1]
  return r and r[1] < y
end
-- the holders of every slab, worked out once
function M:holders()
  if self.hold then return self.hold end
  local H = {}
  for _, pr in ipairs(self.def.props) do
    if pr.kind == "oneway" and not pr.loose and pr.layer == "play" then
      local iron = material(pr) ~= "timber"
      local wl = self:wallAt(pr.x0 - 2, pr.y0) and self:wallAt(pr.x0 - 8, pr.y0)
      local wr = self:wallAt(pr.x1 + 1, pr.y0) and self:wallAt(pr.x1 + 7, pr.y0)
      local a, b = pr.x0 + 2, pr.x1 - 5
      if wl then H[#H + 1] = { k = "bracket", x = pr.x0, y = pr.y1, dir = 1 }; a = pr.x0 + 26 end
      if wr then H[#H + 1] = { k = "bracket", x = pr.x1, y = pr.y1, dir = -1 }; b = pr.x1 - 29 end
      if b >= a then                                              -- a frame of iron tubes (timber posts under a
        local xs = { a }                                          -- wooden ledge): posts at the ends (and the
        if b - a > 160 then xs[#xs + 1] = math.floor((a + b) / 2) end   -- middle of a long slab), ties every 48 px
        if b > a then xs[#xs + 1] = b end                         -- between them, one brace in the top bay
        local prev
        for _, x in ipairs(xs) do
          local f = self:floorBelow(x + 1, pr.y1)
          if f and f - pr.y1 < 400 then
            H[#H + 1] = { k = "post", x = x, y0 = pr.y1, y1 = f, iron = iron }
            if prev then
              local low = math.min(prev.y1, f)
              for y = pr.y1 + 40, low - 12, 48 do H[#H + 1] = { k = "tie", x0 = prev.x + 3, x1 = x, y = y, iron = iron } end
              if low - pr.y1 > 30 then H[#H + 1] = { k = "brace", x0 = prev.x + 3, x1 = x, y0 = pr.y1 + 2, y1 = math.min(low - 4, pr.y1 + 40), iron = iron } end
            end
            prev = { x = x, y1 = f }
          end
        end
      end
    end
  end
  local runs, loose = {}, {}                                      -- loose tiles: one rail per run, ledge to ledge
  for _, pr in ipairs(self.def.props) do if pr.loose then loose[#loose + 1] = pr end end
  table.sort(loose, function(p, q) if p.y0 ~= q.y0 then return p.y0 < q.y0 end return p.x0 < q.x0 end)
  for _, pr in ipairs(loose) do
    local r = runs[#runs]
    if r and r.y == pr.y1 and pr.x0 - r.x1 <= 16 then r.x1 = pr.x1 else runs[#runs + 1] = { x0 = pr.x0, x1 = pr.x1, y = pr.y1 } end
  end
  for _, r in ipairs(runs) do H[#H + 1] = { k = "rail", x0 = r.x0 - 6, x1 = r.x1 + 6, y = r.y } end
  self.hold = H
  return H
end
-- (round 2, producer 8 Nov: "no thin 1 px line drawings over walls") the frames are solid: tubes and planks 3 px
-- with a 1 px ink outline and a lit edge, diagonal braces 2 px with ink, a foot plate on the floor, brackets as solid
-- iron knees. Drawn in two passes, ink first, so crossing parts join into one frame.
local function tube(pass, x, y0, y1, timber)                     -- a vertical pole, x its left column
  if pass == 1 then rect("ink", x - 1, y0, 5, y1 - y0 + 1); rect("ink", x - 3, y1 - 3, 9, 4); return end
  rect(timber and "wd_hi" or "iron_hi", x, y0, 1, y1 - y0); rect(timber and "wd" or "tin_sh", x + 1, y0, 1, y1 - y0)
  rect(timber and "wd_sh" or "iron", x + 2, y0, 1, y1 - y0)
  rect(timber and "wd_sh" or "iron", x - 2, y1 - 2, 7, 2); rect(timber and "wd_hi" or "iron_hi", x - 2, y1 - 2, 7, 1)
end
local function plank(pass, x0, x1, y, timber)                    -- a horizontal plank or tube, top row y
  if pass == 1 then rect("ink", x0, y - 1, x1 - x0, 5); return end
  rect(timber and "wd_hi" or "iron_hi", x0, y, x1 - x0, 1); rect(timber and "wd" or "tin_sh", x0, y + 1, x1 - x0, 1)
  rect(timber and "wd_sh" or "iron", x0, y + 2, x1 - x0, 1)
end
local function brace(pass, x0, y0, x1, y1, timber)               -- a diagonal brace, 2 px
  local n = math.max(1, math.abs(x1 - x0))
  for i = 0, n - 1 do
    local x, y = x0 + (x1 > x0 and i or -i), math.floor(y0 + (y1 - y0) * i / n)
    if pass == 1 then rect("ink", x, y - 1, 1, 4) else rect(timber and "wd" or "tin_sh", x, y, 1, 1); rect(timber and "wd_sh" or "iron", x, y + 1, 1, 1) end
  end
end
local function knee(pass, x, y, dir)                              -- a solid iron bracket: a knee under the slab's end
  local L = 18
  for r = 0, L - 1 do
    local w = L - r
    local x0 = dir > 0 and x or x - w
    if pass == 1 then rect("ink", x0 - 1, y + r, w + 2, 1)
    else rect(r == 0 and "iron_hi" or "tin_sh", x0, y + r, math.max(0, w - 1), 1); rect("iron", dir > 0 and x0 + w - 1 or x0, y + r, 1, 1) end
  end
  if pass == 1 then rect("ink", dir > 0 and x - 1 or x - 4, y - 1, 5, L + 6); rect("ink", x - L - 1, y + L, 1, 0)
  else rect("iron", dir > 0 and x or x - 3, y, 3, L + 4); rect("iron_hi", dir > 0 and x or x - 3, y, 1, L + 4) end
end
M.tube, M.plank, M.brace = tube, plank, brace
function M:drawBack(cam, camY, t)
  if not self:palette() then return end
  local H = self:holders()
  for pass = 1, 2 do
    for _, h in ipairs(H) do
      if h.k == "post" and h.x - cam > -8 and h.x - cam < 328 then tube(pass, h.x - cam, h.y0, h.y1, not h.iron)
      elseif h.k == "tie" and h.x1 - cam > -4 and h.x0 - cam < 324 then plank(pass, h.x0 - cam - 1, h.x1 - cam + 1, h.y, not h.iron)
      elseif h.k == "brace" and h.x1 - cam > -4 and h.x0 - cam < 324 then brace(pass, h.x0 - cam, h.y0 + 3, h.x1 - cam, h.y1, not h.iron)
      elseif h.k == "bracket" and math.abs(h.x - cam - 160) < 200 then knee(pass, h.x - cam, h.y, h.dir)
      elseif h.k == "rail" and h.x1 - cam > -4 and h.x0 - cam < 324 then plank(pass, h.x0 - cam, h.x1 - cam, h.y + 1, false)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
end

-- a slab Pepper uses: ink outline over its box (its top row at y0 - 1), the material inside
local function slab(pr, x, t)
  local w, h = pr.x1 - pr.x0, pr.y1 - pr.y0
  local m = material(pr)
  rect("ink", x - 1, pr.y0 - 1, w + 2, h + 2)
  if m == "awning" then                                           -- striped canvas, a scalloped valance under it
    for i = 0, w - 1 do
      local red = math.floor(i / 8) % 2 == 0
      rect(red and "tile" or "canvas", x + i, pr.y0, 1, h)
      rect(red and "tile_hi" or "cre_hi", x + i, pr.y0, 1, 1)
      if i % 8 >= 1 and i % 8 <= 6 then rect(red and "tile_sh" or "cre_sh", x + i, pr.y1 + 1, 1, (i % 8 >= 2 and i % 8 <= 5) and 3 or 2) end
    end
    return
  end
  local hi, top, body, sh, jt = "cap_hi", "cap_top", "cap", "cap_sh", "cap_jt"
  if m == "copper" then hi, top, body, sh, jt = "cu_hi", "cu_top", "cu", "cu_sh", "cu_jt"
  elseif m == "timber" then hi, top, body, sh, jt = "wd_hi", "wd_hi", "wd", "wd_sh", "wd_sh" end
  rect(hi, x, pr.y0, w, 1); rect(body, x, pr.y0 + 1, w, h - 2); rect(sh, x, pr.y1 - 1, w, 1)
  local step = m == "copper" and 8 or (m == "timber" and 16 or 24)
  for i = step, w - 2, step do rect(jt, x + i, pr.y0 + 1, 1, h - 2); if m == "copper" then rect(top, x + i - 1, pr.y0 + 1, 1, h - 2) end end
end
local function pots(x, y1, w)                                       -- three clay chimney pots on a stack (decoration)
  for i = 0, 2 do
    local px = math.floor(x + w / 2 - 28 + i * 20)
    rect("tile", px + 1, y1 - 16, 8, 16); rect("tile_hi", px + 1, y1 - 16, 2, 16); rect("tile_sh", px + 7, y1 - 16, 2, 16)
    rect("tile_dk", px + 1, y1 - 10, 8, 1)
    rect("tile_hi", px, y1 - 19, 10, 3); rect("tile_sh", px, y1 - 17, 10, 1); rect("tile_dk", px + 2, y1 - 19, 6, 1)
  end
end
local function brick(x, y0, w, y1)                                  -- stucco in brick courses (the ground's chimneys)
  rect("ch", x, y0, w, y1 - y0); rect("ch_hi", x, y0, 2, y1 - y0); rect("ch_sh", x + w - 2, y0, 2, y1 - y0)
  local k = 0
  for y = y0 + 5, y1 - 1, 6 do
    rect("ch_jt", x, y, w, 1)
    for xx = x + (k % 2) * 8, x + w - 1, 16 do rect("ch_jt", xx, y - 5, 1, 5) end
    k = k + 1
  end
end
M.STAND = {                                                       -- built stand-ins until phase 2's renders
  ["SWEEP'S CHIMNEYS"] = function(pr, x) pots(x, pr.y1, pr.x1 - pr.x0) end,
  ["HOTEL CHIMNEYS"] = function(pr, x) pots(x, pr.y1, pr.x1 - pr.x0) end,
  ["ROOF GARDEN"] = function(pr, x)                               -- planter boxes with greenery on the parapet
    for bx = 4, pr.x1 - pr.x0 - 28, 36 do
      for i = 0, 27, 4 do rect(i % 8 == 0 and "leaf" or "leaf_sh", x + bx + i, pr.y1 - 14 + (i % 8 == 0 and 0 or 2), 5, 7) end
      for i = 2, 25, 8 do rect("leaf_hi", x + bx + i, pr.y1 - 14, 2, 1) end
      rect("wd", x + bx, pr.y1 - 8, 28, 8); rect("wd_hi", x + bx, pr.y1 - 8, 28, 1); rect("wd_sh", x + bx + 26, pr.y1 - 7, 2, 7)
    end
  end,
  ["ROOF BAR TERRACE"] = function(pr, x)                          -- the bar's glazed pavilion under the copper roof
    local w = pr.x1 - pr.x0
    rect("gl_sh", x, 290, w, pr.y1 - 300)
    for gx = 0, w - 1, 20 do rect("gl_hi", x + gx + 6, 296, 2, 10); rect("gl_hi", x + gx + 4, 300, 2, 6) end
    for cx = 0, w - 4, 40 do rect("cre_hi", x + cx, 286, 2, pr.y1 - 286); rect("cre_sh", x + cx + 2, 286, 2, pr.y1 - 286) end
    rect("cre_sh", x + w - 4, 286, 4, pr.y1 - 286)
    rect("wd", x + 8, pr.y1 - 24, w - 16, 14); rect("wd_hi", x + 8, pr.y1 - 24, w - 16, 2)   -- the bar counter
  end,
  RAILING = function(pr, x)
    local im = Sc.railing(pr.x1 - pr.x0, "decor"); lg.setColor(1, 1, 1, 1); lg.draw(im, math.floor(x), pr.y1 - im:getHeight())
  end,
  ["DRYING YARD"] = function(pr, x)                               -- a washing line on two posts, three sheets
    local w = pr.x1 - pr.x0
    rect("wd", x + 2, pr.y1 - 26, 2, 26); rect("wd", x + w - 4, pr.y1 - 26, 2, 26)
    for i = 4, w - 5 do rect("iron", x + i, pr.y1 - 25 + math.floor(math.sin((i - 4) / (w - 8) * math.pi) * 3), 1, 1) end
    for k = 0, 2 do
      local sx = 10 + k * 20
      local sy = pr.y1 - 25 + math.floor(math.sin((sx + 6 - 4) / (w - 8) * math.pi) * 3)
      rect(k == 1 and "cre_hi" or "canvas", x + sx, sy, 12, 11); rect("cap_top", x + sx + 10, sy, 2, 11)
    end
  end,
  SCAFFOLD = function(pr, x)                                      -- poles from the gap's floor, rails, a brace
    local w = pr.x1 - pr.x0
    local px = { 2, math.floor(w / 2) - 1, w - 5 }
    for pass = 1, 2 do
      for _, p in ipairs(px) do tube(pass, x + p, 246, 319) end
      plank(pass, x + 1, x + w - 1, 248); plank(pass, x + 1, x + w - 1, 300)
      brace(pass, x + px[1] + 3, 298, x + px[2], 252)
    end
  end,
  NEST = function(pr, x)                                          -- a bowl of twigs on the chimney
    local w = pr.x1 - pr.x0
    for r = 0, 9 do
      local inset = math.floor(math.abs(r - 3) * 0.8)
      for i = inset, w - 1 - inset do
        local c = (i + r * 3) % 7 == 0 and "wd_hi" or ((i + r) % 5 == 0 and "wd_sh" or "wd")
        rect(c, x + i, pr.y0 + r, 1, 1)
      end
    end
  end,
  ["ROOF CAFE"] = function(pr, x)                                 -- a parasol over a cafe table
    local cx = math.floor(x + (pr.x1 - pr.x0) / 2)
    rect("iron", cx, pr.y0 + 6, 2, pr.y1 - pr.y0 - 6)
    for r = 0, 9 do
      local hw = 10 + r * 3
      for i = -hw, hw - 1 do rect(math.floor((i + 64) / 10) % 2 == 0 and "tile" or "canvas", cx + i, pr.y0 - 4 + r, 1, 1) end
    end
    for i = -38, 37 do if (i + 38) % 10 >= 2 and (i + 38) % 10 <= 7 then rect("tile_sh", cx + i, pr.y0 + 6, 1, 2) end end
    rect("wd", cx - 14, pr.y1 - 18, 30, 3); rect("wd_hi", cx - 14, pr.y1 - 18, 30, 1)
    rect("wd_sh", cx - 11, pr.y1 - 15, 2, 15); rect("wd_sh", cx + 11, pr.y1 - 15, 2, 15)
  end,
  ["STAIRS UP (MIA)"] = function(pr, x)                           -- the stair housing Mia came up: a door, a cap
    local w = pr.x1 - pr.x0
    rect("cre", x, pr.y0 + 8, w, pr.y1 - pr.y0 - 8); rect("cre_sh", x, pr.y0 + 14, w, 4)
    rect("cap_hi", x - 2, pr.y0 + 8, w + 4, 1); rect("cap", x - 2, pr.y0 + 9, w + 4, 4); rect("cap_sh", x - 2, pr.y0 + 13, w + 4, 1)
    for rr = 0, 7 do rect(rr == 0 and "tile_hi" or (rr % 4 == 3 and "tile_sh" or "tile"), x + 8 - rr, pr.y0 + rr, w - 16 + 2 * rr, 1) end
    local dx = math.floor(x + w / 2 - 11)
    rect("frame", dx, pr.y1 - 42, 22, 42); rect("wood", dx + 2, pr.y1 - 40, 18, 40)
    for i = 4, 17, 4 do rect("wood_sh", dx + 1 + i, pr.y1 - 40, 1, 40) end
  end,
}
function M:drawProp(pr, cam, colour)
  local x, w = pr.x0 - cam, pr.x1 - pr.x0
  if x > 340 or x + w < -60 or pr.hidden then return true end
  if not self:palette() then return false end
  if pr.kind == "decor" then
    if M.BUILT[pr.name] then return true end
    local f = M.STAND[pr.name]
    if f then f(pr, x); lg.setColor(1, 1, 1, 1); return true end
    Sc.box(colour, x, pr.y0, w, pr.y1 - pr.y0); return true
  end
  local h = pr.y1 - pr.y0
  if pr.kind == "oneway" then slab(pr, x)
  elseif pr.name == "CAFE TABLE" then                             -- a table on two legs (she crawls under it)
    rect("wd_sh", x + 3, pr.y1, 2, 20); rect("wd_sh", x + w - 5, pr.y1, 2, 20)
    rect("ink", x - 1, pr.y0 - 1, w + 2, h + 2); rect("wd_hi", x, pr.y0, w, 1); rect("wd", x, pr.y0 + 1, w, h - 1)
  elseif pr.name == "WATER TANK" then                             -- a wooden water tank in iron hoops
    rect("ink", x - 1, pr.y0 - 1, w + 2, h + 1)
    rect("wd", x, pr.y0, w, h); rect("wd_hi", x, pr.y0, 3, h); rect("wd_sh", x + w - 4, pr.y0, 4, h)
    for i = 8, w - 6, 8 do rect("wd_sh", x + i, pr.y0 + 4, 1, h - 4) end
    rect("cap_hi", x, pr.y0, w, 1); rect("cap", x, pr.y0 + 1, w, 3)
    for y = pr.y0 + 14, pr.y1 - 6, 26 do rect("iron", x, y, w, 2); rect("iron_hi", x, y, w, 1) end
  elseif pr.name == "CHIMNEY STACK" then                          -- the ground's chimney, as an obstacle
    rect("ink", x - 3, pr.y0 - 1, w + 6, h + 1)
    brick(x, pr.y0 + 6, w, pr.y1)
    rect("cap_hi", x - 2, pr.y0, w + 4, 1); rect("cap", x - 2, pr.y0 + 1, w + 4, 3); rect("cap_sh", x - 2, pr.y0 + 4, w + 4, 1)
    rect("ink", x - 2, pr.y0 + 5, w + 4, 1)
  elseif pr.name == "CHIMNEY POT" then                            -- a tall clay chimney pot
    rect("ink", x - 1, pr.y0 - 1, w + 2, h + 1)
    rect("tile", x, pr.y0, w, h); rect("tile_hi", x, pr.y0, 4, h); rect("tile_sh", x + w - 5, pr.y0, 5, h)
    rect("tile_hi", x, pr.y0, w, 2); for y = pr.y0 + 12, pr.y1 - 4, 12 do rect("tile_dk", x, y, w, 1) end
  elseif pr.name == "POST" then                                   -- an iron post; its column runs up to the balcony
    local top = pr.y0
    for _, q in ipairs(self.def.props) do
      if q.kind == "oneway" and q.x0 <= pr.x0 and q.x1 >= pr.x1 and q.y1 <= pr.y0 and pr.y0 - q.y1 < 80 then top = q.y1 end
    end
    rect("iron", x + 2, top, 4, pr.y0 - top); rect("iron_hi", x + 2, top, 1, pr.y0 - top)
    rect("ink", x - 1, pr.y0 - 1, w + 2, h + 1); rect("iron_hi", x, pr.y0, 2, h); rect("iron", x + 2, pr.y0, w - 2, h)
  else Sc.outlined(Sc.C.prop, Sc.C.propEdge, x, pr.y0, w, h) end
  lg.setColor(1, 1, 1, 1)
  return true
end
-- the checkpoint lamps: the approved lamp post, its foot on the roof or ledge it stands on
function M:drawLamp(l, cam, t)
  local art = Sc.art()
  local im = l.lit and art.lamp_lit or art.lamp_post
  local x = math.floor(l.x - cam - im:getWidth() / 2)
  local top = l.y + 1 - im:getHeight()
  Sc.shadow(l.x - cam, l.y - 1, 12)
  lg.setColor(1, 1, 1, 1); lg.draw(im, x, top)
  if l.lit then Sc.lampLight(x + im:getWidth() / 2, top + 17, self.stage.t - (l.litAt or -9), t) end
  return true
end

-- C+D: the ground. The map's surface key (every 8th column's first top, as the tool reads the map) must match the
-- manifest's, so the art never drifts from the hit boxes after a map edit.
local function surfaceKey(w)
  local t = {}
  for x = 0, w.width - 1, 8 do local r = Sc.columnRuns(w, x, "all")[1]; t[#t + 1] = r and tostring(r[1]) or "-" end
  return love.data.encode("string", "hex", love.data.hash("md5", table.concat(t, ",")))
end
function M:paintGround(w)
  local ok, man = pcall(require, "levelart.rooftops.manifest")
  if not ok then print("[rooftops] no built ground: python3 -I tools/build_rooftops_art.py"); return Sc.paintGroundGrey(w) end
  if surfaceKey(w) ~= man.key then
    print("[rooftops] the map changed since the art was built: python3 -I tools/build_rooftops_art.py"); io.stdout:flush()
    return Sc.paintGroundGrey(w)
  end
  Sc.quayEdge = nil
  local g = setmetatable({ chunks = {}, width = w.width, height = w.height }, Sc.Ground)
  for _, c in ipairs(man.ground) do
    local im = lg.newImage(DIR .. c.file); im:setFilter("nearest", "nearest")
    g.chunks[#g.chunks + 1] = { cv = im, x = c.x, y = c.y, w = c.w, h = c.h }
  end
  return g
end

return M
