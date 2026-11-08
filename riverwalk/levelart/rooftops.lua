-- Level art for rooftops (levelart.lua). Empty: the level still draws as greybox. Each part is added as it passes QA.
local M = {}
M.__index = M
function M.new(stage) return setmetatable({ stage = stage, def = stage.def, world = stage.world }, M) end
return M
