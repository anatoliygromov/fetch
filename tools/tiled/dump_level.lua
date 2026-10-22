-- Prints a level table (riverwalk/level/<name>.lua) as JSON on stdout, for tools/level_to_tiled.py.
-- Runs under plain Lua 5.1 / LuaJIT (lua dump_level.lua path/to/level.lua) or inside LOVE (see level_to_tiled.py).
-- Arrays (keys 1..n) become JSON arrays, an empty table becomes [], other tables become objects with sorted keys.
local function isArray(t)
  local n = 0
  for _ in pairs(t) do n = n + 1 end
  for i = 1, n do if t[i] == nil then return false end end
  return true, n
end

local function str(s)
  return '"' .. s:gsub('[%c"\\]', function(c)
    if c == '"' then return '\\"' elseif c == '\\' then return '\\\\' elseif c == '\n' then return '\\n' end
    return string.format('\\u%04x', c:byte())
  end) .. '"'
end

local function enc(v, out)
  local t = type(v)
  if t == "table" then
    local arr, n = isArray(v)
    if arr then
      out[#out + 1] = "["
      for i = 1, n do if i > 1 then out[#out + 1] = "," end; enc(v[i], out) end
      out[#out + 1] = "]"
    else
      local keys = {}
      for k in pairs(v) do keys[#keys + 1] = k end
      table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
      out[#out + 1] = "{"
      for i, k in ipairs(keys) do
        if i > 1 then out[#out + 1] = "," end
        -- numeric keys in a non-array table are written as "#<n>" so they come back as numbers
        out[#out + 1] = str(type(k) == "number" and ("#" .. k) or tostring(k)); out[#out + 1] = ":"; enc(v[k], out)
      end
      out[#out + 1] = "}"
    end
  elseif t == "string" then out[#out + 1] = str(v)
  elseif t == "number" then
    if v == math.floor(v) and math.abs(v) < 2^53 then out[#out + 1] = string.format("%d", v)
    else out[#out + 1] = string.format("%.17g", v) end
  elseif t == "boolean" then out[#out + 1] = tostring(v)
  else error("cannot encode a " .. t) end
end

-- a level file switched to Tiled (local USE_TILED = true) is read with the switch off: its own table
return function(path)
  local f = assert(io.open(path, "rb"))
  local src = f:read("*a"):gsub("local USE_TILED = true", "local USE_TILED = false")
  f:close()
  local chunk = assert((loadstring or load)(src, path))
  -- a level drawn in Tiled only (level/citypark_tall.lua: return require("tiled").load(...)) loads its export;
  -- its terrain comes back as L.rows
  local game = path:match("^(.*)level/[^/]+%.lua$") or ""
  package.path = game .. "?.lua;" .. package.path
  local ok, T = pcall(require, "tiled")
  if ok then T.base = game end
  local out = {}
  enc(chunk(), out)
  return table.concat(out)
end
