-- Level art for Söder Hill (levelart.lua; 8 Nov 2026, owner: "finish levels 4-6"). Built by rule, 0 credits.
-- Parts are added as they pass QA; whatever this module does not draw, stage.lua draws as greybox.
--   A  labels off: every prop is drawn without its printed name (the names are debug only)
local Sc = require("scene")
local M = {}
M.__index = M
function M.new(stage) return setmetatable({ stage = stage, def = stage.def, world = stage.world }, M) end

-- a prop without art yet: its greybox box, no label (a copy whose name is blank)
local function plain(pr, cam, colour)
  Sc.drawProp(setmetatable({ name = "" }, { __index = pr }), cam, colour)
end

function M:drawProp(pr, cam, colour, kicked)
  plain(pr, cam, colour)
  return true
end

return M
