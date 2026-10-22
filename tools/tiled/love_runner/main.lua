-- love tools/tiled/love_runner <script.lua> [args...]: runs the script as plain Lua (io.write and print go to
-- stdout) and quits with its exit code. Used by tools/level_to_tiled.py and tools/check_tiled.sh when lua5.1,
-- luajit or lua are not installed (on a Mac with only LOVE).
function love.load(args)
  local script = args[1]
  arg = { [0] = script }
  for i = 2, #args do arg[i - 1] = args[i] end
  local ok, code = pcall(dofile, script)
  if not ok then io.stderr:write(tostring(code) .. "\n"); love.event.quit(1); return end
  io.stdout:flush()
  love.event.quit(type(code) == "number" and code or 0)
end
