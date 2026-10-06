-- The HUD from the concept art: four blue street signs along the top (lives and hearts, bones, time, score),
-- flat sign blue with a light top rim, a darker left edge and a pointed right end, white 5x7 letters.
-- The prompt banner on the pavement uses the same blue in a box with clipped corners.
local F = require("bigfont")
local U = {}
local lg = love.graphics
U.BLUE  = { 3/255, 108/255, 231/255 }
U.RIM   = { 80/255, 160/255, 238/255 }
U.EDGE  = { 2/255, 60/255, 150/255 }
U.WHITE = { 1, 1, 1 }
U.SHADE = { 20/255, 24/255, 36/255 }
U.GOLD  = { 252/255, 214/255, 60/255 }

local function bitmap(rows)
  local d = love.image.newImageData(#rows[1], #rows)
  for y, r in ipairs(rows) do for x = 1, #r do if r:sub(x, x) == "#" then d:setPixel(x - 1, y - 1, 1, 1, 1, 1) end end end
  local i = lg.newImage(d); i:setFilter("nearest", "nearest"); return i
end
local dogIcon = bitmap({ "........##", "#......###", ".########.", ".#######..", ".##...##..", ".#.....#.." })
local boneIcon = bitmap({ "##.....##", "#########", "#########", "##.....##" })
local heart = bitmap({ "##.##", "#####", "#####", ".###.", "..#.." })
local lockIcon = bitmap({ ".###.", "#...#", "#...#", "#####", "##.##", "##.##", "#####" })
local checker                                                   -- every other pixel dark: dims what is under it

-- a sign: body w wide (plus a 5 px point on the right), 12 rows tall
function U.sign(x, y, w)
  for i = 0, 11 do
    local ext = math.floor(5.5 - math.abs(i - 5.5))
    lg.setColor(U.BLUE); lg.rectangle("fill", x, y + i, w + ext, 1)
  end
  lg.setColor(U.RIM); lg.rectangle("fill", x + 1, y, w - 1, 1)
  lg.setColor(U.EDGE); lg.rectangle("fill", x, y, 1, 12); lg.rectangle("fill", x + 2, y + 1, 1, 10)
  lg.setColor(1, 1, 1, 1)
end
local function txt(s, x, y, col) lg.setColor(col or U.WHITE); F.print(s, x, y, 1); lg.setColor(1, 1, 1, 1) end

-- g: { lives, hearts, bones, total, time (seconds left), score }
function U.status(g)
  local y = 3
  U.sign(4, y, 62)
  lg.draw(dogIcon, 8, y + 3)
  txt("x" .. g.lives, 20, y + 3)
  for i = 1, 3 do lg.setColor(i <= g.hearts and U.WHITE or U.RIM); lg.draw(heart, 34 + (i - 1) * 7, y + 4) end
  U.sign(72, y, 66)
  lg.setColor(1, 1, 1, 1); lg.draw(boneIcon, 77, y + 4)
  txt(("%02d/%02d"):format(g.bones, g.total), 90, y + 3)
  U.sign(146, y, 62)
  local low = g.time < 30 and math.floor(love.timer.getTime() * 4) % 2 == 0
  txt(("TIME %03d"):format(math.max(0, math.ceil(g.time))), 152, y + 3, low and U.RIM or U.WHITE)
  U.sign(238, y, 74)
  txt(("SCORE %06d"):format(g.score), 243, y + 3)
end

-- a box with clipped corners: dark edge, light rim, blue body
function U.box(x, y, w, h)
  lg.setColor(U.EDGE); lg.rectangle("fill", x + 1, y, w - 2, h); lg.rectangle("fill", x, y + 1, w, h - 2)
  lg.setColor(U.RIM);  lg.rectangle("fill", x + 2, y + 1, w - 4, h - 2); lg.rectangle("fill", x + 1, y + 2, w - 2, h - 4)
  lg.setColor(U.BLUE); lg.rectangle("fill", x + 2, y + 2, w - 4, h - 4)
  lg.setColor(1, 1, 1, 1)
end
-- the prompt on the pavement (rows 201..211)
function U.prompt(text)
  local w = F.width(text, 1) + 16
  local x = math.floor((320 - w) / 2)
  U.box(x, 201, w, 11)
  txt(text, x + 8, 203)
end
function U.center(s, cx, y, scale, col)
  lg.setColor(U.SHADE); F.center(s, cx + 1, y + 1, scale)
  lg.setColor(col or U.WHITE); F.center(s, cx, y, scale)
  lg.setColor(1, 1, 1, 1)
end
function U.text(s, x, y, col) txt(s, x, y, col) end
-- dims the whole screen with a 1 px checker of the shade colour (behind boxes and cards)
function U.dim()
  if not checker then
    local d = love.image.newImageData(320, 240)
    for y = 0, 239 do for x = (y % 2), 319, 2 do d:setPixel(x, y, U.SHADE[1], U.SHADE[2], U.SHADE[3], 1) end end
    checker = lg.newImage(d)
  end
  lg.setColor(1, 1, 1, 1); lg.draw(checker, 0, 0)
end
-- a padlock as tall as a letter (5 x 7 at scale 1), with the same 1 px shadow
function U.lock(x, y, col, scale)
  lg.setColor(U.SHADE); lg.draw(lockIcon, x + 1, y + 1, 0, scale or 1)
  lg.setColor(col or U.WHITE); lg.draw(lockIcon, x, y, 0, scale or 1)
  lg.setColor(1, 1, 1, 1)
end
-- the dog from the lives sign (10 x 6), at scale (1 or 2)
function U.dog(x, y, col, scale)
  lg.setColor(U.SHADE); lg.draw(dogIcon, x + 1, y + 1, 0, scale or 1)
  lg.setColor(col or U.WHITE); lg.draw(dogIcon, x, y, 0, scale or 1); lg.setColor(1, 1, 1, 1)
end
return U
