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
             water = L(0.4, 1.2, 1.2, "8fb4d8", 0.05), back = L(0.3, 0.6, 1.05, "f6d8ac", 0.06),
             ground = L(0.3, 0.5, 1.05, "000000", 0), play = L(0.5, 0.7, 1.12, "000000", 0),
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
M.FAR_Y, M.MID_Y = 46, 70                                        -- the strips' top rows on screen at the bottom tier
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
  local base = yf + 70                                            -- the far roofs' eaves row
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
-- A: a prop as its greybox shape with no label (decor: a flat box in its layer's colour; the rest outlined)
function M:drawProp(pr, cam, colour)
  local x, w = pr.x0 - cam, pr.x1 - pr.x0
  if x > 330 or x + w < -10 or pr.hidden then return true end
  if pr.kind == "decor" and M.BUILT[pr.name] then return true end
  if pr.kind == "decor" then Sc.box(colour, x, pr.y0, w, pr.y1 - pr.y0)
  else Sc.outlined(Sc.C.prop, Sc.C.propEdge, x, pr.y0, w, pr.y1 - pr.y0) end
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
