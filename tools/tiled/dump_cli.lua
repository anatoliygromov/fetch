-- lua dump_cli.lua <dump_level.lua> <level.lua>: prints the level as JSON (used by tools/level_to_tiled.py)
io.write(dofile(arg[1])(arg[2]))
