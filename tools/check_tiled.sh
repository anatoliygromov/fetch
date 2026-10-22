#!/bin/sh
# The Tiled pipeline check (docs/tiled.md). Run from anywhere; needs python3 and lua5.1, luajit, lua or LÖVE.
#  1. round trip: every level (riverwalk/level/<name>.lua + .map; citypark_tall, rooftops, downtown_tall: the export) -> a fresh
#     Tiled map (tools/level_to_tiled.py, with the drag-safe relx. / rely. / relxy. fields) -> its Lua export ->
#     riverwalk/tiled.lua gives the identical table and terrain rows
#  2. the same through Tiled itself (tiled --export-map lua), when Tiled is installed
#  3. the exports the game reads (riverwalk/level/tiled/<name>.lua) are up to date with maps/<name>.tmx, and the
#     committed maps upgraded to drag-safe fields (level_to_tiled.py --upgrade, into a scratch folder: the maps
#     themselves are not touched) still give the same levels
#  3b. drag-safe: every object of the fresh and the upgraded maps dragged by (16, 80) with 10 rows added on top
#     (tools/tiled/move_map.py): every position that belongs to an object moved with it
#  4. the level files as the game loads them: a level switched to Tiled (City Park) still gives the original table
#     (a NOTE, not a failure, once a map has been changed in Tiled on purpose)
#  5. a tall map (50 rows) with kinds of objects no level has yet loads with no change to the loader
#  6. NOTE lines: which committed Tiled maps differ from the original level files (changed in Tiled)
cd "$(dirname "$0")/.."
REPO="$(pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
FAIL=0
if command -v lua5.1 >/dev/null; then LUA="lua5.1"; elif command -v luajit >/dev/null; then LUA="luajit"
elif command -v lua >/dev/null; then LUA="lua"; elif command -v love >/dev/null; then LUA="love tools/tiled/love_runner"
else LUA="/Applications/love.app/Contents/MacOS/love tools/tiled/love_runner"; fi        # a Mac with only LOVE
CHECK="$LUA tools/tiled/check_tiled.lua $REPO"

LEVELS="citypark downtown riverwalk soder night lab_tall citypark_tall rooftops downtown_tall"   # the play order, the lab, the tall ones
MAPPED="citypark downtown riverwalk soder night citypark_tall rooftops downtown_tall"   # the ones with a committed maps/*.tmx

echo "== 1. round trip: level files -> Tiled map -> export -> tiled.lua ($LUA)"
python3 tools/level_to_tiled.py $LEVELS --out "$TMP/maps" --export-dir "$TMP/export" > /dev/null || FAIL=1
$CHECK same "$TMP/export" "round trip" $LEVELS || FAIL=1

echo "== 2. the same through Tiled's own Lua export"
TILED="$(command -v tiled)"
[ -z "$TILED" ] && [ -x /Applications/Tiled.app/Contents/MacOS/Tiled ] && TILED=/Applications/Tiled.app/Contents/MacOS/Tiled
QPA=""; [ "$(uname)" = Linux ] && QPA="QT_QPA_PLATFORM=offscreen"      # no display needed (Linux)
if [ -n "$TILED" ]; then
  mkdir -p "$TMP/tiled"
  for f in "$TMP"/maps/*.tmx; do
    env $QPA "$TILED" --export-map lua "$f" "$TMP/tiled/$(basename "$f" .tmx).lua" > /dev/null 2>&1 || FAIL=1
  done
  $CHECK same "$TMP/tiled" "Tiled $(env $QPA "$TILED" --version 2>/dev/null | awk "{print \$NF}") export" $LEVELS || FAIL=1
else
  echo "SKIP  Tiled is not installed"
fi

echo "== 3. the game's exports are up to date with maps/*.tmx"
mkdir -p "$TMP/fresh"
for f in maps/*.tmx; do python3 tools/level_to_tiled.py --export "$f" "$TMP/fresh/$(basename "$f" .tmx).lua" > /dev/null || FAIL=1; done
$CHECK pair riverwalk/level/tiled "$TMP/fresh" || FAIL=1
$CHECK pair riverwalk/level/tiled "$TMP/fresh" citypark_tall || FAIL=1      # (a level drawn in Tiled, not in the play order)
$CHECK pair riverwalk/level/tiled "$TMP/fresh" rooftops || FAIL=1           # (the same: Rooftops, engine/round2)
$CHECK pair riverwalk/level/tiled "$TMP/fresh" downtown_tall || FAIL=1      # (the same: the tall Downtown, r3/design)
python3 tools/level_to_tiled.py --upgrade maps/*.tmx --out "$TMP/upgraded" --export-dir "$TMP/upexport" > /dev/null || FAIL=1
for n in $MAPPED; do
  $CHECK pair riverwalk/level/tiled "$TMP/upexport" $n > "$TMP/out" || FAIL=1
  sed "s|export up to date with maps/$n.tmx|maps/$n.tmx upgraded to drag-safe fields: same level|" "$TMP/out"
done

echo "== 3b. drag-safe: everything dragged by (16, 80), 10 rows added on top"
mkdir -p "$TMP/moved" "$TMP/upmoved"
for n in $LEVELS; do
  python3 tools/tiled/move_map.py "$TMP/maps/$n.tmx" "$TMP/moved/$n.tmx" 16 80 &&
    python3 tools/level_to_tiled.py --export "$TMP/moved/$n.tmx" "$TMP/moved/$n.lua" > /dev/null || FAIL=1
done
$CHECK moved "$TMP/export" "$TMP/moved" 16 80 $LEVELS || FAIL=1
for n in $MAPPED; do
  python3 tools/tiled/move_map.py "$TMP/upgraded/$n.tmx" "$TMP/upmoved/$n.tmx" 16 80 &&
    python3 tools/level_to_tiled.py --export "$TMP/upmoved/$n.tmx" "$TMP/upmoved/$n.lua" > /dev/null || FAIL=1
done
$CHECK moved "$TMP/upexport" "$TMP/upmoved" 16 80 $MAPPED > "$TMP/out" || FAIL=1
sed 's/^\(PASS\|FAIL\)  \([a-z_]*\) */\1  \2 (upgraded map) /' "$TMP/out"

echo "== 4. the levels as the game loads them"
$CHECK game || FAIL=1

echo "== 5. the loader on a tall map with new kinds of objects"
$CHECK unit || FAIL=1

echo "== 6. the Tiled maps against the original level files"
$CHECK info riverwalk/level/tiled

if [ "$FAIL" = 0 ]; then echo "TILED CHECK PASSED"; else echo "TILED CHECK FAILED"; exit 1; fi
