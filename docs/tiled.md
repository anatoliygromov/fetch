# Drawing levels in Tiled

Tiled is a free map editor (mapeditor.org). Every FETCH! level is now also a Tiled map, so you can draw the
ground, move a bench or add a bone with the mouse instead of typing numbers in Lua.

City Park already plays from its Tiled map. The other four levels have Tiled maps too, ready to switch.

## The files

| File | What it is |
| --- | --- |
| `maps/<level>.tmx` | The Tiled map. Open and edit this one. |
| `maps/terrain.png` | The four ground tiles (solid, water, two slopes). |
| `riverwalk/level/tiled/<level>.lua` | The export the game reads. Tiled writes it when you press Ctrl+E. |
| `riverwalk/level/<level>.lua` and `.map` | The old level files. They stay as the fallback. |

Levels: `citypark`, `downtown`, `riverwalk`, `soder`, `night`.

## Open a map

1. Install Tiled 1.10 or later from mapeditor.org.
2. In Tiled: File > Open, pick `maps/citypark.tmx`.
3. The Layers panel (right) shows the layers. Click an eye to hide a layer, the lock to stop editing it.
4. Click an object to see its Properties (left): X, Y, Width, Height, Name, Class and its custom properties.
5. Map > Map Properties shows the level's own settings (time limit, intro text and so on).

Tip: View > Snapping > Snap to Grid snaps to the 8 px cells. Snap to Pixels keeps everything on whole pixels.

## Units

- Everything is in pixels. One cell is 8 x 8 px. One screen is 320 x 240 px (40 x 30 cells).
- x grows to the right, **y grows downwards**. y 0 is the top of the map.
- Positions of Pepper, Mia, bones and lamps are **feet**: the y where they stand. The path in most levels is y 184.
- A rectangle's top edge is what Pepper lands on. Its bottom edge matters for walking under it.

Pepper's limits (measure from the ground she stands on):

| | |
| --- | --- |
| Body | 34 px wide (17 each side of her middle), 26 px tall standing, 16 px crouched |
| Crawl under | a gap of 16 px or more (the benches leave 19) |
| Step up | 4 px or less: she walks onto it |
| Tap hop (tap A) | 24 px up |
| Held jump (hold A) | 46 px up, about 75 px forward from standing |
| Jump and scramble | a ledge up to 58 px up (hold A and push towards it) |

## The layers

| Layer | What is in it |
| --- | --- |
| terrain | The ground, drawn with tiles: solid, water, slope up, slope down. Empty cells are air. |
| props | Benches, logs, branches, houses: rectangles. Also `pieces` (things drawn in code) and `passages`. |
| zones | Bike, cart and tram zones (`bikes`), secrets, Söder's hatches and barrels. |
| movers | Moving platforms: boats, the pontoon. |
| critters | Geese and gulls. |
| lamps | Lamp posts (checkpoints). Night Harbour's light pools (`lights`). |
| bones | Bones to collect. |
| story | Pepper's start, the ball, Mia, the cat, the fox and its hideouts, the magpie's perches, hints. |

How the game reads an object:

- **Class** says which list the object belongs to: `props`, `bones`, `lamps`, `hints`... (Tiled 1.8 calls the
  field Type.) The layer does not matter to the game, only to you.
- **Name** is the object's name (a prop's label, a secret's name, a boat's name).
- **A rectangle** gives the box: left, right, top, bottom.
- **A point** gives a position (x, feet y).
- **Custom properties** are copied as they are. A value written in curly brackets is a list:
  `{ 600, 830 }`.
- **Order matters** in two places: hints (the first one that fits wins) and the magpie's perches (it flies to
  them in order). The order is the order in the Objects panel. Raise and lower with Page Up and Page Down.

Easiest way to add anything: select one that is like it, copy (Ctrl+C), paste (Ctrl+V), move it. The copy keeps
its class and properties.

### props

| Property | Meaning |
| --- | --- |
| kind | `solid` (blocks from every side), `oneway` (land on it from above, jump up through it, Down + A drops through), `decor` (only drawn) |
| layer | `back` (behind Pepper), `play`, `front` (in front of everything) |
| label | where the name is written: `top` or `below` |
| hidden | true: not drawn (a collision box for something drawn in code) |
| bounce | springy top: landing on it launches Pepper this many px up |
| over, leaves | a leaf pile: drawn over the bones, flattens when she runs through |
| art, ax, ay, depth | River Walk's pictures: which picture, and where it is anchored |
| crumble | Night Harbour: a plank that falls when she stands on it |

Unnamed props carry a property `name` that is empty. You can leave it out on new ones.

### zones, movers, critters

- **bikes** (bikes, carts, trams): the band is the stretch where they come (`zoneX0` to `zoneX1`). Properties:
  `kind` (empty for a bike, `cart`, `tram`), `every` (seconds), `speed` (px per second), `endX` (where they
  leave), `start = enter` (the first one comes when she walks in). `minY` is not used by the game today.
- **secrets**: a box. Pepper's feet inside it count the secret. The name shows on the tally.
- **hatches** (Söder Hill): left, right and top of a hole in the street.
- **movers**: the box is the deck. `from` and `to` are where its left edge travels, `speed` in px per second,
  `pause` in seconds. A rope ferry has `call` (where Pepper calls it, `{ from, to }`), `callSpeed` and `rope`.
- **critters**: a goose is a point with `x0` and `x1`, the stretch it walks. A gull is a band with `every`.

Watch out: these numbers do not move when you drag the object. Move a boat and also change its `from` and `to`.
The same goes for a goose's `x0` and `x1`, River Walk's `ax` and `ay`, and a barrel's `trigger` and `rest`.

### lamps, bones, story

- **lamps**: a point at the post's foot. `checkpoint = true`: Pepper comes back here after a fall.
- **bones**: a point at the feet line under the bone (it floats 9 px above). `super = true`: a gold bone, 1,000
  points.
- **start**, **ball**, **girl** (Mia), **cat**, **fox**: one each, a point at the feet.
- **magpie.perches**, **fox.hideouts**: points, in order.
- **hints**: a band above the map, from where to where on the level the hint shows. `text` is what is said.
  With `btn` (`a`, `b`, `x`, `y`, `down`) it is Pepper's button hint, without it Mia says it. `need` adds a
  condition (`ball`, `noball`, `goose`, `magpienear`...), `maxY` only shows it above that height.

Bands above the map (hints, bike zones, gulls) only use their left and right edges. Their height and how high
they sit are free.

## Notes for yourself

- A **text object** (the T tool) is a note. The game ignores it.
- A **layer whose name starts with #** is ignored too: use one for guides and sketches.

## Add a prop, a bone or a lamp

**A prop.** Select a prop like the one you want (a bench, a branch). Ctrl+C, Ctrl+V, drag it into place. Drag the
handles to resize. Check its `kind`: `solid`, `oneway` or `decor`. Type a new Name if you like.

**A bone.** Select a bone, copy and paste it, drag it so the pin sits on the floor under where the bone should
float. For a gold bone tick `super`.

**A lamp.** Select a lamp, copy and paste, drag the pin to the foot of the post on the ground.

**Ground.** Click the terrain layer, pick a tile in the Tilesets panel, paint with the stamp (B). Erase with E.
Slopes go one cell at a time: up to the right, then down to the right.

## Export, then play

1. Save the map: Ctrl+S (this keeps the `.tmx`).
2. Export it: File > Export, Ctrl+E. It writes `riverwalk/level/tiled/<level>.lua`. The map remembers this.
   If Tiled asks where, pick that file and the format "Lua files (*.lua)".
3. Run the game (below).

Forgot to export? `sh tools/check_tiled.sh` tells you which map is out of date.

### Run the game on the Mac

Install LÖVE 11.5 from love2d.org (drag love.app to Applications). Then in Terminal, from the repo folder:

```
/Applications/love.app/Contents/MacOS/love riverwalk --level citypark
```

`--level` starts straight in that level. Leave it out to play from the title screen. Add `--physics` or `--auto`
to run the level's checks or let the autopilot play it.

## Switch a level to Tiled, and back

City Park's `riverwalk/level/citypark.lua` starts with:

```
local USE_TILED = true
if USE_TILED then return require("tiled").load("level/tiled/citypark.lua") end
```

- Back to the old level: change `true` to `false`. The old table below it is played again.
- Another level: put the same two lines at the top of its file, with its own name.

Note: the old files do not follow your Tiled changes. Once you edit a map, the Tiled map is the level.

## Taller levels

A map can have any number of rows. Map > Resize Map makes it taller. Give it an offset to add the rows at the
top, so the level moves down with everything on it. The game reads any height; it shows the extra height once
the camera can scroll up and down (being added on another branch).

## For the curious

- `python3 tools/level_to_tiled.py citypark` makes `maps/citypark.tmx` again from the old files. **It overwrites
  your map**, so only use it on purpose.
- `python3 tools/level_to_tiled.py --export maps/citypark.tmx` writes the export without Tiled.
- `python3 tools/tiled/render_map.py maps/citypark.tmx preview.png --rows 3` draws a map to a PNG (needs Pillow).
- `sh tools/check_tiled.sh` proves the Tiled maps give the game exactly the same levels. Once you change a map,
  its "NOTE" lines list what is different from the old files. That is expected.
- The rules the game follows are at the top of `riverwalk/tiled.lua`.
