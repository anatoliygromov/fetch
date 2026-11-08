-- Level art for Night Harbour (levelart.lua; 8 Nov 2026, phase 1, 0 credits: built by rule, code and built pixels).
-- The palette is one table (levelart/night/palette.lua), sampled from the picked concept (nh_home_concept_b.png).
-- Parts, in the order they were added:
--   A  labels off: every prop and boat is drawn without its greybox name (the debug view still has the boxes)
local Sc = require("scene")
local lg = love.graphics
local M = {}
M.__index = M

local P = {}                                                        -- the palette as colours (0-1)
for k, v in pairs(require("levelart.night.palette")) do
  P[k] = { tonumber(v:sub(1, 2), 16) / 255, tonumber(v:sub(3, 4), 16) / 255, tonumber(v:sub(5, 6), 16) / 255 }
end
M.P = P

local function box(c, x, y, w, h) lg.setColor(c); lg.rectangle("fill", math.floor(x), math.floor(y), w, h) end
local function outlined(c, x, y, w, h) box(P.ink, x, y, w, h); if w > 2 and h > 2 then box(c, x + 1, y + 1, w - 2, h - 2) end end

function M.new(stage) return setmetatable({ stage = stage, def = stage.def, world = stage.world }, M) end

-- A: a prop with no art yet is a plain box in the night's colours, without its label
function M:drawProp(pr, cam, colour, kicked)
  local x, w = pr.x0 - cam, pr.x1 - pr.x0
  if x > 330 or x + w < -10 then return true end
  if pr.hidden then return true end
  if pr.kind == "decor" then box(pr.layer == "front" and P.ink or P.shed3, x, pr.y0, w, pr.y1 - pr.y0)
  else outlined(P.g4, x, pr.y0, w, pr.y1 - pr.y0) end
  return true
end

-- A: the boats without their labels
function M:drawMover(m, cam, t)
  outlined(P.hull2, m.x0 - cam, m.y0, m.x1 - m.x0, m.y1 - m.y0)
  return true
end

return M
