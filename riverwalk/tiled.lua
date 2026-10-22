-- Loads a level from a Tiled map (mapeditor.org). Tiled writes the map as a Lua table (File > Export As > Lua, then
-- File > Export, Ctrl+E); this file turns that table into the two things a level is made of today: the terrain rows
-- (the text grid of level/<name>.map, 8 x 8 px cells) and the level table L (level/<name>.lua).
-- A level file is then one line:   return require("tiled").load("level/tiled/citypark.lua")
-- The Tiled maps are maps/<name>.tmx (repo root); tools/level_to_tiled.py makes them from a level, docs/tiled.md
-- explains them. The rules, kept generic so new kinds of objects need no change here:
--   terrain   the tile layer "terrain" (else the first tile layer). Each tile's custom property "char" is its map
--             character ('#' solid, '~' water, '/' and '\' slopes); an empty cell is '.'. Any number of rows.
--   objects   each object goes into the list L[class] (Tiled's Class field, Type before Tiled 1.9); an empty class
--             means the layer's name. A dotted class goes into a nested list ("magpie.perches" -> L.magpie.perches).
--             Classes named in SINGLE (and in the map property "singles", comma separated) are one object, not a
--             list: L.start = { x, y }. Objects keep their order in the map (the layers from the bottom up).
--             A rectangle gives x0, x1, y0, y1; its property "box" can name other fields for its left, right, top
--             and bottom sides ("zoneX0,zoneX1", "x0,x1", "1,2,3"; "-" skips a side). A point gives x and y. A
--             polyline or polygon gives x, y and points = { { x, y }, ... } (absolute). Positions are rounded
--             to whole pixels. The object's name is the field "name"; every custom property is copied as it is
--             (a property wins over the shape, so a property "name" = "" survives). A text property that starts
--             with "{" is a Lua table: "{ 600, 830 }".
--   notes     text objects, and layers or classes whose name starts with "#", are notes: they are skipped.
--   the rest  map properties are the level's other fields; a dotted name sets a nested field ("magpie.flee").
-- In the game the terrain rows are written to the save folder (tiled_<name>.map, like pepperlab.lua does) and L.map
-- names that file, so world.lua reads it as before.
local T = {}

local SINGLE = { start = true, ball = true, girl = true, cat = true, fox = true, exit = true }
local DEFAULT_CHARS = { "#", "~", "/", "\\" }      -- tile ids 0..3 of a tileset without "char" properties

local function round(v) return math.floor(v + 0.5) end

-- a Lua table written as text ("{ 600, 830 }"), read with no access to anything else
local function literal(s, where)
  local f, err
  if setfenv then
    f, err = loadstring("return " .. s, where)
    if f then setfenv(f, {}) end
  else
    f, err = load("return " .. s, where, "t", {})
  end
  if not f then error("tiled: " .. where .. ": not a Lua table: " .. tostring(err), 0) end
  return f()
end

local function value(v, where)
  if type(v) == "string" and v:match("^%s*{") then return literal(v, where) end
  return v
end

local function key(k) return tonumber(k) or k end

-- properties as Tiled's Lua export writes them ({ name = value }), or as a list ({ { name =, value = } }, JSON)
local function props(p)
  local out = {}
  if not p then return out end
  if p[1] ~= nil then for _, q in ipairs(p) do out[q.name] = q.value end else for k, v in pairs(p) do out[k] = v end end
  return out
end

local function sortedKeys(t)
  local ks = {}
  for k in pairs(t) do ks[#ks + 1] = k end
  table.sort(ks)
  return ks
end

-- set L.a.b.c = v for the path "a.b.c" (dotted map properties)
local function setPath(L, path, v)
  local t, segs = L, {}
  for s in path:gmatch("[^%.]+") do segs[#segs + 1] = key(s) end
  for i = 1, #segs - 1 do
    if type(t[segs[i]]) ~= "table" then t[segs[i]] = {} end
    t = t[segs[i]]
  end
  t[segs[#segs]] = v
end

-- put an item into L by its class: a list (append) or a single object (merged)
local function place(L, class, item, singles)
  local t, segs = L, {}
  for s in class:gmatch("[^%.]+") do segs[#segs + 1] = key(s) end
  for i = 1, #segs - 1 do
    if type(t[segs[i]]) ~= "table" then t[segs[i]] = {} end
    t = t[segs[i]]
  end
  local last = segs[#segs]
  if singles[class] then
    local s = t[last] or {}
    for k, v in pairs(item) do s[k] = v end
    t[last] = s
  else
    t[last] = t[last] or {}
    table.insert(t[last], item)
  end
end

local function terrain(map)
  local layer
  for _, l in ipairs(map.layers) do if l.type == "tilelayer" and l.name == "terrain" then layer = l; break end end
  if not layer then for _, l in ipairs(map.layers) do if l.type == "tilelayer" then layer = l; break end end end
  if not layer then error("tiled: the map has no tile layer (terrain)", 0) end
  if layer.chunks then error("tiled: the map is infinite; make it a fixed size (Map > Map Properties)", 0) end
  if layer.encoding and layer.encoding ~= "lua" then
    error("tiled: the terrain layer is stored as " .. layer.encoding .. "; set Map > Map Properties > Tile Layer Format to CSV", 0)
  end
  local chars = {}
  for _, ts in ipairs(map.tilesets or {}) do
    local named = false
    for _, tile in ipairs(ts.tiles or {}) do
      local c = props(tile.properties).char
      if c then chars[ts.firstgid + tile.id] = c; named = true end
    end
    if not named then for i, c in ipairs(DEFAULT_CHARS) do chars[ts.firstgid + i - 1] = chars[ts.firstgid + i - 1] or c end end
  end
  local w, h, rows = layer.width, layer.height, {}
  for r = 1, h do
    local line = {}
    for c = 1, w do
      local gid = layer.data[(r - 1) * w + c] or 0
      gid = gid % 536870912                         -- drop Tiled's flip flags
      if gid == 0 then line[c] = "."
      else
        line[c] = chars[gid] or error(("tiled: terrain cell (%d, %d) has a tile with no \"char\" property"):format(c - 1, r - 1), 0)
      end
    end
    rows[r] = table.concat(line)
  end
  return rows
end

local function object(o, layerName)
  local class = o.type
  if class == nil or class == "" then class = o.class end
  if class == nil or class == "" then class = layerName end
  if o.shape == "text" or class:sub(1, 1) == "#" then return nil end
  local p = props(o.properties)
  local where = ("object %s (%s, %s)"):format(tostring(o.id), class, o.name ~= "" and o.name or "no name")
  local item = {}
  if o.shape == "point" then
    item.x, item.y = round(o.x), round(o.y)
  elseif o.shape == "polyline" or o.shape == "polygon" then
    item.x, item.y, item.points = round(o.x), round(o.y), {}
    for i, q in ipairs(o.polyline or o.polygon or {}) do item.points[i] = { round(o.x + q.x), round(o.y + q.y) } end
  else                                               -- rectangle (and ellipse)
    local sides = { round(o.x), round(o.x + o.width), round(o.y), round(o.y + o.height) }
    local names, i = {}, 0
    for s in (p.box or "x0,x1,y0,y1"):gmatch("[^,]+") do
      i = i + 1
      s = s:match("^%s*(.-)%s*$")
      if s ~= "-" and s ~= "" and i <= 4 then item[key(s)] = sides[i] end
    end
  end
  if o.name and o.name ~= "" then item.name = o.name end
  for k, v in pairs(p) do if k ~= "box" then item[key(k)] = value(v, where .. " property " .. k) end end
  return class, item
end

-- map: the table of a Tiled Lua export. Returns the level table L and the terrain rows.
function T.parse(map)
  if map.tilewidth ~= 8 or map.tileheight ~= 8 then error("tiled: tiles must be 8 x 8 px", 0) end
  local L = {}
  local mp = props(map.properties)
  local singles = {}
  for k in pairs(SINGLE) do singles[k] = true end
  for s in (mp.singles or ""):gmatch("[^,%s]+") do singles[s] = true end
  mp.singles = nil
  for _, k in ipairs(sortedKeys(mp)) do setPath(L, k, value(mp[k], "map property " .. k)) end
  for _, layer in ipairs(map.layers) do
    if layer.type == "objectgroup" and layer.name:sub(1, 1) ~= "#" then
      for _, o in ipairs(layer.objects) do
        local class, item = object(o, layer.name)
        if class then place(L, class, item, singles) end
      end
    end
  end
  return L, terrain(map)
end

-- path: a Tiled Lua export inside the game folder. Returns L, ready for St.new (L.map is the terrain file).
function T.load(path)
  local L, rows
  if love and love.filesystem then
    local chunk, err = love.filesystem.load(path)
    if not chunk then error("tiled: cannot read " .. path .. ": " .. tostring(err), 0) end
    L, rows = T.parse(chunk())
    local file = "tiled_" .. path:match("([^/]+)%.lua$") .. ".map"
    local text = table.concat(rows, "\n") .. "\n"
    if love.filesystem.read(file) ~= text then
      local ok, e = love.filesystem.write(file, text)
      if not ok then error("tiled: cannot write " .. file .. " to the save folder: " .. tostring(e), 0) end
    end
    L.map = file
  else
    L, rows = T.parse(dofile((T.base or "") .. path))  -- outside LOVE (tools/tiled/check_tiled.lua): T.base = game folder
    L.rows = rows
  end
  return L
end

return T
