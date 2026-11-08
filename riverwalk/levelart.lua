-- Levels 4 to 6 get their art through one module each (8 Nov 2026, owner: "finish levels 4-6").
-- A level sets L.levelart = "<name>" and riverwalk/levelart/<name>.lua draws its art. City Park and Downtown keep
-- their own path (L.art = "park" / "town" in scene.lua and arthooks.lua); nothing here touches them.
--
-- The level stays scenery = "greybox" for the game rules (no road, no traffic). stage.lua asks the module for each
-- part and draws the greybox for any part the module does not have, so a level can be finished piece by piece.
--
-- A module returns a table M with M.new(stage) -> an object. Every method is optional:
--   o:drawFar(cam, camY, t)            sky, far, mid layers (screen space; replaces Sc.drawFarGrey)
--   o:paintGround(world)               returns a ground object with :draw(cam, camY) (replaces Sc.paintGroundGrey)
--   o:drawBack(cam, camY, t)           behind Pepper's line, after the back props (world space)
--   o:drawProp(pr, cam, colour, kicked) -> true when it drew the prop (else the greybox box and label)
--   o:drawLamp(l, cam, t)              -> true when it drew the checkpoint lamp (else the greybox lamp)
--   o:drawMover(m, cam, t)             -> true when it drew the mover (else the labelled box)
--   o:drawFront(cam, camY, t)          in front of Pepper, after the front props (world space)
--   o:drawScreen(cam, camY, t)         screen space, over everything (after the night's darkness)
--   o.look                             the level's colour script (look.lua format); registered as Look.scripts[name].
--                                      Without one the Lion King look stays off for the level.
local LA = {}

function LA.new(stage)
  local name = stage.def.levelart
  if not name then return nil end
  local M = require("levelart." .. name)
  local o = M.new(stage)
  if o and o.look then require("look").scripts[name] = o.look end
  return o
end

return LA
