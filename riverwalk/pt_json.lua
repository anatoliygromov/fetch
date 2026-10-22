-- Playtest lab: a small JSON reader and writer (personas.json in, one result file per run out).
local J = {}

local function skip(s, i) local _, e = s:find("^[ \n\r\t]*", i); return e + 1 end
local decodeValue
local function decodeString(s, i)
  local out, j = {}, i + 1
  while true do
    local c = s:sub(j, j)
    if c == '"' then return table.concat(out), j + 1 end
    if c == "\\" then
      local n = s:sub(j + 1, j + 1)
      local map = { n = "\n", t = "\t", r = "\r", b = "\b", f = "\f", ['"'] = '"', ["\\"] = "\\", ["/"] = "/" }
      if n == "u" then out[#out + 1] = "?"; j = j + 6 else out[#out + 1] = map[n] or n; j = j + 2 end
    else out[#out + 1] = c; j = j + 1 end
    if j > #s then error("unterminated string") end
  end
end
function decodeValue(s, i)
  i = skip(s, i)
  local c = s:sub(i, i)
  if c == "{" then
    local t = {}; i = skip(s, i + 1)
    if s:sub(i, i) == "}" then return t, i + 1 end
    while true do
      local k; k, i = decodeString(s, skip(s, i)); i = skip(s, i)
      assert(s:sub(i, i) == ":", "expected :"); local v; v, i = decodeValue(s, i + 1); t[k] = v
      i = skip(s, i); local d = s:sub(i, i)
      if d == "}" then return t, i + 1 end
      assert(d == ",", "expected ,"); i = i + 1
    end
  elseif c == "[" then
    local t = {}; i = skip(s, i + 1)
    if s:sub(i, i) == "]" then return t, i + 1 end
    while true do
      local v; v, i = decodeValue(s, i); t[#t + 1] = v
      i = skip(s, i); local d = s:sub(i, i)
      if d == "]" then return t, i + 1 end
      assert(d == ",", "expected ,"); i = i + 1
    end
  elseif c == '"' then return decodeString(s, i)
  elseif s:sub(i, i + 3) == "true" then return true, i + 4
  elseif s:sub(i, i + 4) == "false" then return false, i + 5
  elseif s:sub(i, i + 3) == "null" then return nil, i + 4
  else
    local num = s:match("^-?[%d%.eE+-]+", i)
    return tonumber(num), i + #num
  end
end
function J.decode(s) return (decodeValue(s, 1)) end

local function isArray(t)
  local n = 0
  for k in pairs(t) do if type(k) ~= "number" then return false end; n = n + 1 end
  return n == #t
end
local function enc(v, out)
  local tv = type(v)
  if tv == "nil" then out[#out + 1] = "null"
  elseif tv == "boolean" then out[#out + 1] = tostring(v)
  elseif tv == "number" then
    if v ~= v or v == math.huge or v == -math.huge then out[#out + 1] = "null"
    elseif math.floor(v) == v and math.abs(v) < 1e15 then out[#out + 1] = string.format("%d", v)
    else out[#out + 1] = string.format("%.3f", v) end
  elseif tv == "string" then out[#out + 1] = '"' .. v:gsub('[%c"\\]', function(c) return string.format("\\u%04x", c:byte()) end) .. '"'
  elseif tv == "table" then
    if next(v) == nil then out[#out + 1] = "[]"
    elseif isArray(v) then
      out[#out + 1] = "["
      for i, x in ipairs(v) do if i > 1 then out[#out + 1] = "," end; enc(x, out) end
      out[#out + 1] = "]"
    else
      out[#out + 1] = "{"
      local keys = {}
      for k in pairs(v) do keys[#keys + 1] = tostring(k) end
      table.sort(keys)
      for i, k in ipairs(keys) do
        if i > 1 then out[#out + 1] = "," end
        enc(k, out); out[#out + 1] = ":"; enc(v[k] == nil and v[tonumber(k)] or v[k], out)
      end
      out[#out + 1] = "}"
    end
  else out[#out + 1] = "null" end
end
function J.encode(v) local out = {}; enc(v, out); return table.concat(out) end
return J
