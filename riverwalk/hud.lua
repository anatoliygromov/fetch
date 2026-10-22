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
local clockIcon = bitmap({ ".###.", "#.#.#", "#.#.#", "#.###", "#...#", ".###." })
local bigHeart = bitmap({ ".#.#.", "#####", "#####", ".###.", "..#.." })
local smallBone = bitmap({ "#...#", "#####", "#...#" })
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
  U.sign(146, y, g.hard and 56 or 62)                           -- hard mode: a shorter sign, the HARD tag after it
  local low = g.time < 30 and math.floor(love.timer.getTime() * 4) % 2 == 0
  txt(("TIME %03d"):format(math.max(0, math.ceil(g.time))), 152, y + 3, low and U.RIM or U.WHITE)
  if g.hard then U.hardTag(208, y + 1) end
  U.sign(238, y, 74)
  txt(("SCORE %06d"):format(g.score), 243, y + 3)
end

-- FETCH FRENZY (bonus.lua): g = { time (seconds left), catches, need (catches for the extra life), points }.
-- Three signs: the catches against the goal (gold once reached), the countdown (blinks in the last 5 s), points.
local ballIcon = bitmap({ ".###.", "#####", "#####", "#####", ".###." })
function U.bonusStatus(g)
  local y = 3
  U.sign(4, y, 84)
  lg.setColor(1, 1, 1, 1); lg.draw(ballIcon, 9, y + 4)
  if g.catches >= g.need then                                    -- the goal reached: the count in gold and a dog (+1 life)
    txt(("CATCH %02d"):format(g.catches), 18, y + 3, U.GOLD); lg.setColor(U.GOLD); lg.draw(dogIcon, 72, y + 3); lg.setColor(1, 1, 1, 1)
  else txt(("CATCH %02d/%02d"):format(g.catches, g.need), 18, y + 3) end
  U.sign(124, y, 62)
  local low = g.time <= 5 and g.time > 0 and math.floor(love.timer.getTime() * 4) % 2 == 0
  txt(("TIME %02d"):format(math.max(0, math.ceil(g.time))), 132, y + 3, low and U.GOLD or U.WHITE)
  U.sign(232, y, 80)
  txt(("POINTS %05d"):format(g.points), 237, y + 3)
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
-- the HARD tag (hard mode): gold letters on a dark red plate, 29 x 10
U.RED = { 170/255, 30/255, 52/255 }
function U.hardTag(x, y)
  lg.setColor(U.SHADE); lg.rectangle("fill", x + 1, y + 1, 29, 10)
  lg.setColor(U.RED); lg.rectangle("fill", x, y, 29, 10)
  txt("HARD", x + 3, y + 2, U.GOLD)
end
-- a medal, 11 x 11 at x, y: a gold disc with its picture (nohit: a heart, bones: a bone, par: a clock); not won
-- yet: a dark disc (visible on the selected row too) with the picture in the rim colour
local medalPic = { nohit = bigHeart, bones = smallBone, par = clockIcon }
local medalDisc
function U.medal(kind, x, y, won)
  if not medalDisc then medalDisc = bitmap({ "...#####...", ".#########.", ".#########.", "###########", "###########",
    "###########", "###########", "###########", ".#########.", ".#########.", "...#####..." }) end
  lg.setColor(U.SHADE); lg.draw(medalDisc, x + 1, y + 1)
  lg.setColor(won and U.GOLD or U.SHADE); lg.draw(medalDisc, x, y)
  local pic = medalPic[kind]
  lg.setColor(won and { 120/255, 70/255, 10/255 } or U.RIM)
  lg.draw(pic, x + math.floor((11 - pic:getWidth()) / 2), y + math.floor((11 - pic:getHeight()) / 2))
  lg.setColor(1, 1, 1, 1)
end
-- the sound level: 10 cells, 4 x h each with a 1 px gap (52 px wide), lit up to the level; "OFF" at 0
function U.volumeBar(x, y, level, max, h)
  h = h or 7
  if level == 0 then txt("OFF", x, y + math.floor((h - 7) / 2), U.GOLD); return end
  for i = 1, max do
    lg.setColor(U.SHADE); lg.rectangle("fill", x + (i - 1) * 5 + 1, y + 1, 4, h)
    lg.setColor(i <= level and U.GOLD or U.EDGE); lg.rectangle("fill", x + (i - 1) * 5, y, 4, h)
  end
  lg.setColor(1, 1, 1, 1)
end
-- shown for a moment when the volume buttons are pressed: a small box under the status signs while playing;
-- y = 218 (the bottom edge) over menus and cards, so it never covers their headings
function U.volumeToast(level, max, y)
  y = y or 20
  U.box(110, y, 100, 17)
  txt("SOUND", 116, y + 5)
  U.volumeBar(150, y + 5, level, max)
end
return U
