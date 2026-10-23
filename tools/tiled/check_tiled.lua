-- The Tiled round trip check (run by tools/check_tiled.sh, under lua5.1 / luajit / lua or LOVE's love_runner).
--   lua check_tiled.lua <repo> same <dir> <label> [names]   each level's original files (riverwalk/level/<name>.lua
--                                                          and .map) against the Tiled export <dir>/<name>.lua read
--                                                          by riverwalk/tiled.lua: the same table, the same rows
--   lua check_tiled.lua <repo> info <dir> [names]           the same, only reported (a map changed in Tiled differs)
--   lua check_tiled.lua <repo> pair <dirA> <dirB> [names]   two exports of the same maps load the same
--   lua check_tiled.lua <repo> game [names]                 the level files as the game requires them: a level that
--                                                          loads from Tiled must give the original table
-- Tables are compared deeply: lists in order, other keys as sets; L.map (the terrain file's name) is not compared.
local repo, mode = arg[1], arg[2]
local GAME = repo .. "/riverwalk/"
package.path = GAME .. "?.lua;" .. package.path
local T = require("tiled")
T.base = GAME

local function names(from)
  local list = {}
  for i = from, #arg do list[#list + 1] = arg[i] end
  if #list == 0 then for _, l in ipairs(dofile(GAME .. "levels.lua")) do list[#list + 1] = l.name end end
  return list
end

local function readFile(p) local f = assert(io.open(p, "rb")); local s = f:read("*a"); f:close(); return s end

local function compile(src, name)
  local f, err
  if setfenv then f, err = loadstring(src, name) else f, err = load(src, name) end
  return assert(f, err)
end

-- the original level: its .lua with the Tiled switch off, and its .map (a level drawn in Tiled only, with no .map:
-- the level as the game loads it, from its committed export)
local function original(name)
  if not io.open(GAME .. "level/" .. name .. ".map", "rb") then
    local L = dofile(GAME .. "level/" .. name .. ".lua")
    return L, L.rows
  end
  local src = readFile(GAME .. "level/" .. name .. ".lua"):gsub("local USE_TILED = true", "local USE_TILED = false")
  local L = compile(src, name .. ".lua")()
  local rows = {}
  for line in readFile(GAME .. "level/" .. name .. ".map"):gmatch("[^\n]+") do rows[#rows + 1] = line end
  return L, rows
end

local IGNORE = { map = true, rows = true }

local function show(v) return type(v) == "string" and ("%q"):format(v) or tostring(v) end

local function diff(a, b, path, out, top)
  if type(a) ~= type(b) then out[#out + 1] = path .. ": " .. show(a) .. " vs " .. show(b); return end
  if type(a) ~= "table" then
    if a ~= b then out[#out + 1] = path .. ": " .. show(a) .. " vs " .. show(b) end
    return
  end
  local keys = {}
  for k in pairs(a) do keys[k] = true end
  for k in pairs(b) do keys[k] = true end
  local sorted = {}
  for k in pairs(keys) do if not (top and IGNORE[k]) then sorted[#sorted + 1] = k end end
  table.sort(sorted, function(x, y)
    if type(x) == type(y) then return x < y end
    return type(x) == "number"
  end)
  for _, k in ipairs(sorted) do diff(a[k], b[k], path .. (type(k) == "number" and ("[" .. k .. "]") or ("." .. k)), out) end
end

local function compare(La, Ra, Lb, Rb)
  local out = {}
  diff(La, Lb, "L", out, true)
  if #Ra ~= #Rb then out[#out + 1] = ("terrain: %d rows vs %d"):format(#Ra, #Rb) end
  for r = 1, math.min(#Ra, #Rb) do
    if Ra[r] ~= Rb[r] then out[#out + 1] = ("terrain row %d differs"):format(r) end
  end
  return out
end

local function count(L)
  local n = 0
  for k, v in pairs(L) do if not IGNORE[k] and type(v) == "table" and v[1] ~= nil then n = n + #v end end
  return n
end

local function report(name, label, out, L, rows, failWord)
  if #out == 0 then
    print(("PASS  %-10s %s: identical (%d list items, %d x %d terrain cells)"):format(name, label, count(L), #rows[1], #rows))
    return true
  end
  print(("%s  %-10s %s: %d differences"):format(failWord, name, label, #out))
  for i = 1, math.min(#out, 12) do print("        " .. out[i]) end
  return false
end

local function export(dir, name)
  local path = dir .. "/" .. name .. ".lua"
  local f = io.open(path, "rb")
  if not f then return nil end
  f:close()
  return T.parse(dofile(path))
end

local ok = true
if mode == "same" or mode == "info" then
  local dir, label = arg[3], mode == "same" and arg[4] or "Tiled map"
  for _, name in ipairs(names(mode == "same" and 5 or 4)) do
    local L0, R0 = original(name)
    local L1, R1 = export(dir, name)
    if not L1 then print("FAIL  " .. name .. ": no " .. dir .. "/" .. name .. ".lua"); ok = false
    else
      local same = report(name, label .. " vs the original files", compare(L0, R0, L1, R1), L1, R1,
        mode == "same" and "FAIL" or "NOTE")
      if mode == "same" then ok = ok and same end
    end
  end
elseif mode == "pair" then
  for _, name in ipairs(names(5)) do
    local La, Ra = export(arg[3], name)
    local Lb, Rb = export(arg[4], name)
    if not (La and Lb) then print("FAIL  " .. name .. ": an export is missing"); ok = false
    else
      local same = report(name, "export up to date with maps/" .. name .. ".tmx", compare(La, Ra, Lb, Rb), La, Ra,
        "FAIL")
      if not same then print("        (open maps/" .. name .. ".tmx in Tiled and press Ctrl+E: File > Export)") end
      ok = ok and same
    end
  end
elseif mode == "game" then
  for _, name in ipairs(names(3)) do
    local L = dofile(GAME .. "level/" .. name .. ".lua")
    if L.rows then
      local L0, R0 = original(name)
      report(name, "the game loads it from Tiled; same as the original files", compare(L0, R0, L, L.rows), L,
        L.rows, "NOTE")
    else
      print(("PASS  %-10s the game loads it from level/%s.lua and .map"):format(name, name))
    end
  end
elseif mode == "moved" then
  -- every object of the maps in <dirB> was dragged by (dx, dy) and dy / 8 empty rows added at the top
  -- (tools/tiled/move_map.py, as Map > Resize Map with an offset does): every position that belongs to an object
  -- moved with it, nothing else changed
  local dirA, dirB, dx, dy = arg[3], arg[4], tonumber(arg[5]), tonumber(arg[6])
  local X = { x = 1, x0 = 1, x1 = 1, zoneX0 = 1, zoneX1 = 1, from = 1, to = 1, call = 1, rope = 1, endX = 1,
    depot = 1, trigger = 1, ax = 1, bx0 = 1, bx1 = 1, stop = 1 }   -- (stop: a tram lane's stop sign, r8/levels)
  local Y = { y = 1, y0 = 1, y1 = 1, fromY = 1, toY = 1, minY = 1, maxY = 1, ay = 1, door = 1, foot = 1 }   -- (foot: a piece's path)
  local XY = { winch = 1, rest = 1 }
  local function add(v, a, b)                     -- v + (a, b): numbers, lists, { x =, y = }, lists of points
    if type(v) == "number" then return v + a end
    local out = {}
    for k, w in pairs(v) do out[k] = w end
    if b == nil then for i, w in ipairs(v) do out[i] = add(w, a) end
    elseif v.x or v.y then out.x, out.y = v.x + a, v.y + b
    elseif type(v[1]) == "number" then out[1], out[2] = v[1] + a, v[2] + b
    else for i, w in ipairs(v) do out[i] = add(w, a, b) end end
    return out
  end
  local function expect(L)                         -- L with every object's positions moved by (dx, dy)
    local E = {}
    for k, v in pairs(L) do E[k] = v end
    local function item(it, class)
      if type(it) ~= "table" then return it end
      local e = {}
      for k, v in pairs(it) do e[k] = v end
      if class == "hatches" then e[1], e[2], e[3] = it[1] + dx, it[2] + dx, it[3] + dy; return e end
      for k, v in pairs(it) do
        if X[k] then e[k] = add(v, dx)
        elseif Y[k] and not (class == "bikes" and k == "minY") then e[k] = add(v, dy)  -- (a bike zone's minY: not used)
        elseif XY[k] then e[k] = add(v, dx, dy)
        elseif type(v) == "table" and type(v[1]) == "table" and (v[1].x or v[1].x0) then  -- magpie.perches, fox.hideouts
          local l = {}
          for i, w in ipairs(v) do l[i] = item(w, class .. "." .. k) end
          e[k] = l
        end
      end
      return e
    end
    for k, v in pairs(L) do
      if type(v) == "table" and (v.x or v.x0) then E[k] = item(v, k)
      elseif type(v) == "table" and type(v[1]) == "table" and k ~= "scroll" then
        local l = {}
        for i, w in ipairs(v) do l[i] = item(w, k) end
        E[k] = l
      elseif type(v) == "table" and k == "magpie" then E[k] = item(v, k)
      end
    end
    return E
  end
  for _, name in ipairs(names(7)) do
    local La, Ra = export(dirA, name)
    local Lb, Rb = export(dirB, name)
    if not (La and Lb) then print("FAIL  " .. name .. ": an export is missing"); ok = false
    else
      local R = {}
      for i = 1, dy / 8 do R[i] = ("."):rep(#Ra[1]) end
      for i = 1, #Ra do R[#R + 1] = Ra[i] end
      local same = report(name, ("dragged by (%d, %d): every position moved with its object"):format(dx, dy),
        compare(expect(La), R, Lb, Rb), Lb, Rb, "FAIL")
      ok = ok and same
    end
  end
elseif mode == "unit" then
  -- a tall map (50 rows, 400 px) with kinds of objects no level has yet: the loader needs no change for them
  local data = {}
  for i = 1, 4 * 50 do data[i] = 0 end
  for c = 1, 4 do data[49 * 4 + c] = 1 end                          -- the bottom row solid
  data[20 * 4 + 2] = 2                                              -- a water cell in row 21
  local map = { tilewidth = 8, tileheight = 8, width = 4, height = 50,
    properties = { time = 90, ["lift.speed"] = 40, singles = "exit", ["notes"] = "{ 1, { a = \"b\" } }" },
    tilesets = { { firstgid = 1, tiles = { { id = 0, properties = { char = "#" } }, { id = 1, properties = { char = "~" } } } } },
    layers = {
      { type = "tilelayer", name = "terrain", width = 4, height = 50, encoding = "lua", data = data },
      { type = "objectgroup", name = "lifts", objects = {
        { id = 1, name = "LIFT", type = "", shape = "rectangle", x = 8, y = 380.4, width = 16, height = 4,
          properties = { travel = 300, path = "{ 380, 80 }", ["relx.from"] = 0, to = 999, ["relx.to"] = 8,
            ["rely.toY"] = -300, ["relxy.winch"] = "{ x = 4, y = -10 }", ["relx.rope"] = "{ 0, 16, dy = 3 }",
            ["relxy.rest"] = "{ { 1, 2 }, { 3, 4 } }" } },
        { id = 2, name = "", type = "", shape = "polyline", x = 10, y = 20, polyline = { { x = 0, y = 0 }, { x = 0, y = -12.6 } },
          properties = {} },
        { id = 3, name = "a note", type = "", shape = "text", x = 0, y = 0, width = 10, height = 10, properties = {} } } },
      { type = "objectgroup", name = "#notes", objects = { { id = 4, name = "", type = "bones", shape = "point", x = 1, y = 1 } } },
      { type = "objectgroup", name = "story", objects = {
        { id = 5, name = "", type = "exit", shape = "point", x = 30, y = 392, properties = { to = "night" } },
        { id = 6, name = "", type = "bones", shape = "point", x = 12, y = 100, properties = { super = true } },
        { id = 7, name = "", type = "hatches", shape = "rectangle", x = 4, y = 50, width = 9, height = 99,
          properties = { box = "1,2,3", { name = "x" } } } } } } }
  map.layers[4].objects[3].properties = { box = "1, 2, -, 3" }
  local L, rows = T.parse(map)
  local want = { time = 90, lift = { speed = 40 }, notes = { 1, { a = "b" } },
    lifts = { { name = "LIFT", x0 = 8, x1 = 24, y0 = 380, y1 = 384, travel = 300, path = { 380, 80 },
                from = 8, to = 16, toY = 80, winch = { x = 12, y = 370 }, rope = { 8, 24, dy = 3 },
                rest = { { 9, 382 }, { 11, 384 } } },
              { x = 10, y = 20, points = { { 10, 20 }, { 10, 7 } } } },
    exit = { x = 30, y = 392, to = "night" }, bones = { { x = 12, y = 100, super = true } }, hatches = { { 4, 13, 149 } } }
  local out = {}
  diff(want, L, "L", out, true)
  if #rows ~= 50 or rows[50] ~= "####" or rows[21] ~= ".~.." or rows[1] ~= "...." then out[#out + 1] = "terrain rows" end
  ok = report("tall map", "50 rows, new object kinds (lifts, polyline, exit), relx / rely / relxy fields, notes skipped", out, L, rows, "FAIL")
else
  error("check_tiled.lua: unknown mode " .. tostring(mode))
end
os.exit(ok and 0 or 1)
