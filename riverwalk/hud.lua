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
-- Picture signs (r6/levels): a little scene of what a control hint asks, for children who cannot read yet (the
-- talk panel draws one between the button and the words). 14 x 12 cells, drawn 3 px a cell (42 x 36 px): Pepper
-- (white, the HUD's dog in a pose) and what she uses (gold: the ground, a box, a bar, arrows, the ball, Mia).
U.PICT_CELL = 3
U.PICT_W, U.PICT_H = 14 * U.PICT_CELL, 12 * U.PICT_CELL
local lowDog = bitmap({ "..........##", "#########.##", ".##########.", "##.......##." })   -- crouched, crawling
local girlIcon = bitmap({ ".##.", ".##.", "####", ".##.", "####", "####", "####", ".#.#", ".#.#" })   -- Mia, 4 x 9
local ballDot = bitmap({ ".##.", "####", "####", ".##." })
local BALLC = { 236/255, 84/255, 104/255 }
local PICT = {}
-- the steps of one picture: { "dog" | "low" | "girl" | "ball", cx, cy } (its top-left cell), or { "box", cx, cy, w, h } (gold),
-- or { "dots", {cx, cy}, ... } (a dotted path, gold), or { "up" | "down" | "right", cx, cy } (an arrow, gold)
PICT.run    = { { "box", 0, 11, 14, 1 }, { "dog", 1, 5 }, { "box", 0, 6, 1, 1 }, { "box", 0, 8, 1, 1 }, { "right", 11, 5 } }
PICT.hop    = { { "box", 0, 11, 14, 1 }, { "box", 6, 9, 3, 2 }, { "dots", { 0, 10 }, { 1, 8 }, { 3, 6 } }, { "dog", 4, 2 } }
PICT.jump   = { { "box", 0, 11, 14, 1 }, { "box", 8, 6, 4, 5 }, { "dots", { 0, 10 }, { 1, 7 }, { 2, 4 } }, { "dog", 4, 0 } }
PICT.climb  = { { "box", 0, 11, 14, 1 }, { "box", 10, 5, 4, 6 }, { "dog", 0, 5 }, { "up", 8, 0 } }
PICT.crawl  = { { "box", 0, 11, 14, 1 }, { "box", 2, 6, 11, 1 }, { "box", 3, 7, 1, 4 }, { "box", 11, 7, 1, 4 }, { "low", 1, 7 } }
PICT.duck   = { { "box", 0, 11, 14, 1 }, { "low", 1, 7 }, { "box", 9, 1, 1, 1 }, { "box", 10, 2, 1, 1 }, { "box", 11, 1, 1, 1 },
  { "box", 12, 0, 1, 1 }, { "box", 8, 0, 1, 1 }, { "dots", { 8, 4 }, { 6, 5 } } }
PICT.stay   = { { "box", 0, 9, 14, 1 }, { "dots", { 1, 10 }, { 4, 11 }, { 7, 10 }, { 10, 11 }, { 12, 10 } }, { "low", 1, 5 }, { "down", 11, 0 } }
PICT.drop   = { { "box", 0, 6, 14, 1 }, { "box", 0, 11, 14, 1 }, { "dog", 0, 0 }, { "down", 11, 7 } }
PICT.bounce = { { "box", 2, 10, 10, 1 }, { "dots", { 3, 11 }, { 5, 11 }, { 7, 11 }, { 9, 11 }, { 11, 11 } }, { "up", 0, 3 }, { "dog", 4, 2 } }
PICT.pickup = { { "box", 0, 11, 14, 1 }, { "dog", 0, 5 }, { "ball", 10, 7 }, { "down", 10, 2 } }
PICT.give   = { { "box", 0, 11, 14, 1 }, { "dog", 0, 5 }, { "ball", 7, 1 }, { "girl", 10, 2 } }
PICT.bark   = { { "box", 0, 11, 14, 1 }, { "dog", 0, 5 }, { "box", 10, 4, 1, 1 }, { "box", 11, 5, 1, 2 }, { "box", 10, 7, 1, 1 },
  { "box", 12, 3, 1, 1 }, { "box", 13, 4, 1, 4 }, { "box", 12, 8, 1, 1 } }
PICT.sneak  = { { "box", 0, 11, 14, 1 }, { "dog", 4, 5 }, { "dots", { 0, 10 }, { 2, 10 } }, { "box", 0, 2, 3, 1 }, { "box", 2, 3, 1, 1 },
  { "box", 1, 4, 1, 1 }, { "box", 0, 5, 3, 1 } }     -- (soft steps behind her, a "z": quiet)
local arrows = {
  up    = bitmap({ ".#.", "###", ".#.", ".#." }), down = bitmap({ ".#.", ".#.", "###", ".#." }),
  right = bitmap({ "#..", "##.", "###", "##.", "#.." }),
}
-- draws picture `kind` with its top-left at x, y (cells of 2 px); returns false if there is no such picture
function U.pict(kind, x, y)
  local steps = PICT[kind]
  if not steps then return false end
  local c = U.PICT_CELL
  local function at(cx, cy) return x + cx * c, y + cy * c end
  for pass = 1, 2 do                                             -- 1: the shadow, 1 px down and right; 2: the picture
    local o = pass == 1 and 1 or 0
    for _, st in ipairs(steps) do
      local k = st[1]
      local col = pass == 1 and U.SHADE or (k == "dog" or k == "low") and U.WHITE or k == "ball" and BALLC or U.GOLD
      lg.setColor(col)
      if k == "box" then local px, py = at(st[2], st[3]); lg.rectangle("fill", px + o, py + o, st[4] * c, st[5] * c)
      elseif k == "dots" then for i = 2, #st do local px, py = at(st[i][1], st[i][2]); lg.rectangle("fill", px + o, py + o, c, c) end
      else
        local im = (k == "dog" and dogIcon) or (k == "low" and lowDog) or (k == "girl" and girlIcon) or (k == "ball" and ballDot) or arrows[k]
        local px, py = at(st[2], st[3]); lg.draw(im, px + o, py + o, 0, c)
      end
    end
  end
  lg.setColor(1, 1, 1, 1)
  return true
end
U.PICTS = PICT

return U
