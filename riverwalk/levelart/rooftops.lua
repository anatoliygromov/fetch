-- Level art for Rooftops (levelart.lua; 8 Nov 2026, phase 1, 0 credits). Each part is added as it passes QA; stage.lua
-- draws the greybox for any part this module does not have.
--   A  drawProp: the props without their printed names (the greybox labels are a debug view, audit RW1)
local Sc = require("scene")
local lg = love.graphics
local M = {}
M.__index = M

function M.new(stage) return setmetatable({ stage = stage, def = stage.def, world = stage.world }, M) end

-- A: a prop as its greybox shape with no label (decor: a flat box in its layer's colour; the rest outlined)
function M:drawProp(pr, cam, colour)
  local x, w = pr.x0 - cam, pr.x1 - pr.x0
  if x > 330 or x + w < -10 or pr.hidden then return true end
  if pr.kind == "decor" then Sc.box(colour, x, pr.y0, w, pr.y1 - pr.y0)
  else Sc.outlined(Sc.C.prop, Sc.C.propEdge, x, pr.y0, w, pr.y1 - pr.y0) end
  return true
end

return M
