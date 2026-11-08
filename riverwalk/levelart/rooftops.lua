-- Level art for Rooftops (levelart.lua; 8 Nov 2026, phase 1, 0 credits). Each part is added as it passes QA; stage.lua
-- draws the greybox for any part this module does not have. Design target: art/gen/concepts/rt_hotel_concept_a.png
-- (reference only): Stockholm old-town roofs on a warm late afternoon.
--   A    drawProp: the props without their printed names (the greybox labels are a debug view, audit RW1)
--   C+D  paintGround: the houses, roofs, stairs, chimneys, skylights and the street, BUILT by rule from the map by
--        tools/build_rooftops_art.py into 512 px chunks (levelart/rooftops/ground_<x>_<y>.png, manifest.lua). If the
--        map has changed since the build (its surface key differs), the greybox ground is drawn and a line printed:
--        run the tool again.
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
M.look = {
  layers = { clouds = L(0.4, 1.2, 1.0, "fde6b6", 0.04), city = L(0, 0, 1.0, "000000", 0),
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

-- A: a prop as its greybox shape with no label (decor: a flat box in its layer's colour; the rest outlined)
function M:drawProp(pr, cam, colour)
  local x, w = pr.x0 - cam, pr.x1 - pr.x0
  if x > 330 or x + w < -10 or pr.hidden then return true end
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
