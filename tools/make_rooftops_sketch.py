#!/usr/bin/env python3
"""The paper map of Level 3, Rooftops: maps/rooftops_sketch.tmx (greybox geometry only, not wired into the game).
See docs/rooftops_beatsheet.md.

  python3 tools/make_rooftops_sketch.py [--force]
  python3 tools/draw_routes.py rooftops_sketch          (the PNG with the routes drawn on it)

6 x 4 screens: 1920 x 960 px (240 x 120 cells), going up from the street (feet y 904) to the nest chimney (y 136).
Terrain: the street, three stair towers (45 degree stairs, walked up), three flat roofs T1 (y 712), T2 (y 520) and
the roof terrace T3 (y 328), two pitched roofs on the way (R1, R2). Objects: props as in every level, plus two new
kinds the engine does not have yet (docs/rooftops_beatsheet.md has their specs):
  steam   the vent box (its top is the vent's mouth); lift = how high above the vent top a puff carries Pepper's
          feet, every / warn / puff in seconds, source = who makes it, bark = true: only a bark starts it
  props with loose = true: a loose roof tile (a one-way ledge that crumbles: warn, fall, come back)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_to_tiled as T  # noqa: E402

NAME = "rooftops_sketch"
COLS, ROWS = 240, 120
g = [["."] * COLS for _ in range(ROWS)]


def fill(x0, x1, y0, y1, ch="#"):
    for j in range(y0 // 8, y1 // 8):
        for i in range(x0 // 8, x1 // 8):
            g[j][i] = ch


def stairs(x0, y0, n, ch="/"):
    """n slope cells from (x0, feet y0): '/' rises to the right, '\\' falls to the right. Solid under each."""
    for k in range(n):
        if ch == "/":
            i, j = x0 // 8 + k, y0 // 8 - 1 - k
        else:
            i, j = x0 // 8 + k, y0 // 8 - n + k
        g[j][i] = ch
        for jj in range(j + 1, ROWS):
            if g[jj][i] == ".":
                g[jj][i] = "#"


fill(0, 288, 904, 960)                 # the street
stairs(288, 904, 24)                   # stair tower A: up 192 px to T1
fill(480, 1008, 712, 960)              # T1, the first flat roof
stairs(768, 712, 12)                   # R1, a pitched roof on T1: up to its ridge (y 616) ...
stairs(864, 712, 12, "\\")             # ... and down again
stairs(1008, 712, 24)                  # stair tower B: up to T2
fill(1200, 1440, 520, 960)             # T2
stairs(1264, 520, 8)                   # R2, a smaller pitched roof on T2 (ridge y 456)
stairs(1328, 520, 8, "\\")
stairs(1440, 520, 24)                  # stair tower C: up to the roof terrace
fill(1632, 1920, 328, 960)             # T3, the roof terrace (Mia waits here)
fill(1808, 1840, 136, 328)             # the nest chimney: the landmark, 192 px tall, the gull's nest on top
rows = ["".join(r) for r in g]


def P(name, kind, x0, x1, y0, y1, layer="play", **kw):
    d = {"name": name, "kind": kind, "layer": layer, "x0": x0, "x1": x1, "y0": y0, "y1": y1}
    d.update(kw)
    return d


def ow(name, x0, x1, y, **kw):
    return P(name, "oneway", x0, x1, y, y + 6, **kw)


def loose(x0, y):
    return P("", "oneway", x0, x0 + 24, y, y + 6, loose=True, crumble=True)


props = [
    # the street and the cafe (the story's start: the gull takes the ball off Mia's table)
    P("CAFE", "decor", 24, 216, 824, 904, layer="back", label="top"),
    P("CAFE TABLE", "solid", 104, 136, 880, 884),
    P("STAIRWELL A", "decor", 280, 488, 664, 904, layer="back", label="top"),
    P("STAIRWELL B", "decor", 1000, 1208, 472, 712, layer="back", label="top"),
    P("STAIRWELL C", "decor", 1432, 1640, 280, 520, layer="back", label="top"),
    P("CITY HALL TOWER", "decor", 40, 200, 40, 560, layer="back", label="top"),   # far layer: the skyline
    # T1: the high road begins with the first puff (safe: the flat roof is under it)
    ow("DORMER", 600, 680, 616, label="top"),
    ow("", 688, 768, 520),
    loose(800, 520), loose(856, 520), loose(912, 520),
    P("GABLE", "solid", 968, 1040, 520, 536, label="top"),
    # T2: two ledges up, the laundry puff, the loose-tile bridge, the chimney pot with the golden bone
    ow("", 1072, 1136, 488), ow("", 1168, 1232, 456),
    ow("", 1240, 1320, 360),
    loose(1352, 360), loose(1408, 360),
    ow("", 1456, 1536, 360),
    P("CHIMNEY POT", "solid", 1488, 1512, 312, 360, label="top"),
    # T3: the copper roof over the terrace; the lift house Mia came up in (run by the caretaker)
    ow("COPPER ROOF", 1568, 1792, 232, label="top"),     # one-way: the terrace fan lifts her up through it
    P("LIFT HOUSE", "decor", 1864, 1920, 248, 328, layer="back", label="top"),
    P("NEST", "decor", 1804, 1844, 126, 136, layer="back", label="top"),
    P("RAILING", "decor", 1632, 1800, 312, 328, layer="back"),
]
steam = [   # the vent's box: its top is the vent's mouth
    {"name": "KITCHEN FAN", "x0": 620, "x1": 644, "y0": 704, "y1": 712, "lift": 112, "every": 3.0, "warn": 0.8, "puff": 0.9,
     "source": "the cafe's kitchen (the cook)"},
    {"name": "DORMER VENT", "x0": 652, "x1": 672, "y0": 608, "y1": 616, "lift": 112, "every": 3.0, "warn": 0.8, "puff": 0.9,
     "source": "the attic flat's bathroom fan"},
    {"name": "LAUNDRY VENT", "x0": 1208, "x1": 1228, "y0": 448, "y1": 456, "lift": 112, "every": 3.5, "warn": 0.8, "puff": 0.9,
     "source": "the laundry room's dryer"},
    {"name": "CHIMNEY", "x0": 1516, "x1": 1536, "y0": 352, "y1": 360, "lift": 144, "every": 3.5, "warn": 0.8, "puff": 1.0,
     "source": "the bakery's oven chimney"},
    {"name": "TERRACE FAN", "x0": 1680, "x1": 1704, "y0": 320, "y1": 328, "lift": 112, "every": 3.0, "warn": 0.8, "puff": 0.9,
     "source": "the roof restaurant's kitchen"},
    {"name": "SAUNA", "x0": 1768, "x1": 1788, "y0": 224, "y1": 232, "lift": 112, "every": 0, "warn": 0.6, "puff": 1.0,
     "source": "the roof sauna (a bark: the guest throws water on the stones)", "bark": True},
]
lamps = [
    {"x": 40, "y": 904, "checkpoint": True}, {"x": 512, "y": 712, "checkpoint": True},
    {"x": 1216, "y": 520, "checkpoint": True}, {"x": 1648, "y": 328, "checkpoint": True},
    {"x": 984, "y": 520, "checkpoint": True},          # high: on the gable, after the first loose tiles
    {"x": 1600, "y": 232, "checkpoint": True},         # high (both roads): the copper roof, before the finale
]
bones = [
    {"x": 160, "y": 904}, {"x": 330, "y": 864}, {"x": 380, "y": 814}, {"x": 430, "y": 764}, {"x": 560, "y": 712},
    {"x": 720, "y": 712}, {"x": 816, "y": 664}, {"x": 864, "y": 616}, {"x": 912, "y": 664},
    {"x": 1050, "y": 670}, {"x": 1100, "y": 620}, {"x": 1150, "y": 570}, {"x": 1300, "y": 484}, {"x": 1360, "y": 484},
    {"x": 1480, "y": 480}, {"x": 1530, "y": 430}, {"x": 1580, "y": 380}, {"x": 1740, "y": 328}, {"x": 1880, "y": 328},
    # the high road
    {"x": 620, "y": 616}, {"x": 660, "y": 616}, {"x": 720, "y": 520}, {"x": 812, "y": 520}, {"x": 868, "y": 520},
    {"x": 924, "y": 520}, {"x": 1104, "y": 488}, {"x": 1200, "y": 456}, {"x": 1280, "y": 360}, {"x": 1364, "y": 360},
    {"x": 1420, "y": 360}, {"x": 1500, "y": 312, "super": True, "golden": True},
    {"x": 1640, "y": 232}, {"x": 1720, "y": 232}, {"x": 1824, "y": 136, "super": True},
]
L = {
    "name": "ROOFTOPS", "number": 3, "title": "Pepper: Rooftops (paper map)", "scenery": "greybox", "time": 300,
    "start": {"x": 40, "y": 904},
    "ball": {"x": 1824, "y": 136},          # in the nest
    "girl": {"x": 1720, "y": 328},          # Mia waits on the roof terrace (she took the lift)
    "props": props, "steam": steam, "lamps": lamps, "bones": bones,
    "critters": [{"kind": "gull", "x0": 1180, "x1": 1460, "every": 4.0}],
    "nest": [{"x": 1824, "y": 136, "kind": "gull", "say": "THE GULL'S NEST! BARK!"}],
    "secrets": [{"name": "GOLDEN BONE", "x0": 1488, "x1": 1512, "y0": 300, "y1": 312},
                {"name": "DORMER", "x0": 600, "x1": 680, "y0": 604, "y1": 616}],
    "bikes": [], "movers": [],
    "intro": ["LEVEL 3", "ROOFTOPS", "A GULL TOOK THE BALL TO ITS NEST!", "UP THE STAIRS OR OVER THE ROOFS!"],
}


def main(argv):
    tmx = os.path.join(T.MAPS, NAME + ".tmx")
    if os.path.exists(tmx) and "--force" not in argv:
        sys.exit("maps/%s.tmx exists (edit it in Tiled); --force overwrites it" % NAME)
    T.write_tmx(tmx, NAME, L, rows)
    print("%s -> %s (%d x %d cells)" % (NAME, os.path.relpath(tmx, T.ROOT), COLS, ROWS))


if __name__ == "__main__":
    main(sys.argv[1:])
