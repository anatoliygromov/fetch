#!/usr/bin/env python3
"""The paper map of Metro (T-Centralen to Odenplan): maps/metro_sketch.tmx (greybox geometry only, not wired into
the game). See docs/metro_beatsheet.md, which also specifies the new engine pieces.

  python3 tools/make_metro_sketch.py [--force]
  python3 tools/draw_routes.py metro_sketch <out.png>          (the PNG with the routes drawn on it)

8 x 3 screens: 2560 x 720 px (320 x 90 cells), going down in a zig-zag: row 1 (the street and the ticket hall,
feet y 184) runs right, row 2 (the long passage, y 424) runs left, row 3 (the platform, the ride, Odenplan, y 664)
runs right. Rock everywhere else. The rows are joined by escalators that turn back under the floor above (a
switchback: Pepper hops down 60-odd px onto the moving steps and rides under the hall she just crossed).
Objects: props as in every level, plus kinds the engine does not have yet (docs/metro_beatsheet.md specs them):
  escalators   a rectangle whose diagonal is the moving stairs: slope "/" (rises to the right) or "\\"; way =
               "down" or "up" (where the steps carry her); belt = px/s along the stairs
  walkways     a moving walkway, flat (its top is the floor): belt = px/s, + to the right, - to the left
  gates        ticket gates: the glass flaps (a solid box, an 18 px gap under it: crawl); a passenger opens them
               every `every` s for `open` s; a bark at the booth (booth = x) opens the wide gate for `wide` s
  doors        platform screen doors: closed (a solid glass wall) unless open; chime, light
  wagon        the track crew's flat wagon: the deck, its path (from, to), speed, the driver
  signs        low tunnel signs over the wagon's way: bottom 19 px over the deck (crouched 16 passes, standing 26 not)
  hazards      things that move because someone moves them: a suitcase sliding down an escalator, a floor scrubber
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_to_tiled as T  # noqa: E402

NAME = "metro_sketch"
COLS, ROWS = 320, 90
R1, R2, R3 = 184, 424, 664          # the feet lines of the three rows
g = [["#"] * COLS for _ in range(ROWS)]


def air(x0, x1, y0, y1):
    for j in range(max(0, y0 // 8), min(ROWS, y1 // 8)):
        for i in range(max(0, x0 // 8), min(COLS, x1 // 8)):
            g[j][i] = "."


def shaft(xa, ya, xb, yb, room=112):
    """Air above an escalator's line from (xa, ya) to (xb, yb) (45 degrees), `room` px high."""
    for x in range(min(xa, xb), max(xa, xb), 8):
        t = (x + 4 - xa) / (xb - xa)
        y = ya + t * (yb - ya)
        air(x, x + 8, int(y) - room, int(y) + 4)


def water(x0, x1, y0, y1):
    for j in range(y0 // 8, y1 // 8):
        for i in range(x0 // 8, x1 // 8):
            g[j][i] = "~"


# row 1: Sergels torg (open sky), the entrance pavilion and the ticket hall (ceiling y 72)
air(0, 640, 0, R1)
air(640, 1600, 72, R1)
# escalator A: from the hall's end (x 1600), down-left under the hall to the passage
shaft(1680, R1, 1440, R2, room=100)
air(1600, 1688, 120, R1 + 72)
# row 2: the long passage (T-Centralen to Stockholm City), ceiling y 264
air(160, 1440, 264, R2)
# escalator B: from the passage's end (x 160), down-right under it to the platform
shaft(80, R2, 320, R3, room=100)
air(72, 160, 360, R2 + 72)
# row 3: Stockholm City's platform (ceiling y 504), the tunnel (ceiling y 600), Odenplan's platform
air(320, 960, 504, R3)
air(960, 2240, 600, R3 + 32)            # the tunnel: the track bed is 32 px down (y 696)
for j in range((R3 + 32) // 8, ROWS):
    for i in range(960 // 8, 2240 // 8):
        g[j][i] = "#"
air(2240, 2560, 456, R3)
# escalator C (up): from Odenplan's platform up-right to the exit hall where Mia waits
shaft(2320, R3, 2496, R3 - 176, room=100)
air(2480, 2560, 400, R3 - 176)
# the floors the switchbacks pass under stay (the hall's floor over escalator A, the passage's over B)
for x0, x1, y in ((640, 1600, R1), (160, 1440, R2)):
    for i in range(x0 // 8, x1 // 8):
        g[y // 8][i] = "#"
rows = ["".join(r) for r in g]


def P(name, kind, x0, x1, y0, y1, layer="play", **kw):
    d = {"name": name, "kind": kind, "layer": layer, "x0": x0, "x1": x1, "y0": y0, "y1": y1}
    d.update(kw)
    return d


def ow(name, x0, x1, y, **kw):
    return P(name, "oneway", x0, x1, y, y + 6, **kw)


props = [
    # row 1: Sergels torg and the entrance
    P("KRISTALLVERTIKAL", "decor", 220, 236, 8, R1, layer="back", label="top"),       # the glass obelisk
    P("ENTRANCE", "decor", 480, 640, 96, R1, layer="back", label="top"),
    P("BENCH", "solid", 320, 368, 160, 166, label="below"),                           # crawl under or hop on
    P("PRESSBYRAN", "solid", 720, 776, 148, R1, label="top"),                         # the kiosk (36 px: held)
    P("BOOTH", "decor", 880, 936, 120, R1, layer="back", label="top"),               # the attendant
    P("GATE PILLAR", "solid", 1000, 1008, 120, R1),                                   # the gates' cabinet side
    P("TICKET MACHINE", "solid", 1048, 1080, 148, R1, label="top"),                  # way up: 36, then 36
    P("BANNER", "oneway", 1088, 1168, 112, 118, label="below"),                       # high: over the hall
    ow("", 1216, 1280, 96),
    ow("CLOCK", 1328, 1392, 80, label="top"),                                        # the golden bone
    ow("", 1440, 1504, 104),
    P("LANDING", "solid", 1600, 1608, 120, R1, label="top"),                          # the hall's end: a rail post
    # row 2: the long passage (going left). The blue cave's rock shelves are the high road over the walkways
    P("PILLAR", "solid", 1400, 1424, 392, R2, label="top"),                           # an information pillar (32)
    ow("SHELF", 1312, 1368, 352, label="top"),
    ow("", 1208, 1264, 336),
    ow("", 1104, 1160, 352),
    P("DUCT", "solid", 1024, 1056, 296, 336, label="top"),                            # a vent duct (way up: 56)
    ow("", 960, 1016, 336),
    ow("", 856, 912, 320),
    ow("", 752, 808, 336),
    ow("", 648, 704, 352),
    P("FLOWER TUB", "solid", 504, 536, 396, R2, label="top"),
    P("BENCH", "solid", 288, 336, 400, 406, label="below"),
    # row 3: Stockholm City's platform; the wagon's bay; the tunnel; Odenplan
    P("VENDING", "solid", 560, 592, 624, R3, label="top"),
    ow("CAVE SHELF", 640, 720, 600, label="top"),
    ow("", 768, 832, 576),
    ow("", 880, 936, 600),
    P("TUNNEL", "decor", 960, 2240, 600, 608, layer="back", label="below"),
    P("ODENPLAN", "decor", 2264, 2440, 470, 520, layer="back", label="top"),          # the big round clock: landmark
    P("EXIT HALL", "solid", 2496, 2560, R3 - 176, R3 - 168, label="top"),
]
escalators = [
    {"name": "ESCALATOR A", "x0": 1440, "x1": 1680, "y0": R1, "y1": R2, "slope": "/", "way": "down", "belt": 40},
    {"name": "ESCALATOR B", "x0": 80, "x1": 320, "y0": R2, "y1": R3, "slope": "\\", "way": "down", "belt": 56},
    {"name": "ESCALATOR C", "x0": 2320, "x1": 2496, "y0": R3 - 176, "y1": R3, "slope": "/", "way": "up", "belt": 40},
]
walkways = [
    {"name": "WALKWAY (WITH YOU)", "x0": 1104, "x1": 1360, "y0": R2 - 4, "y1": R2, "belt": -80},
    {"name": "WALKWAY (AGAINST YOU)", "x0": 624, "x1": 944, "y0": R2 - 4, "y1": R2, "belt": 60},
]
gates = [
    {"name": "TICKET GATES", "x0": 1008, "x1": 1040, "y0": 120, "y1": R1 - 18, "every": 7.0, "open": 1.5,
     "booth": 908, "wide": 4.0, "say": "GO ON THROUGH, DOGGY!"},
    {"name": "TICKET GATES", "x0": 400, "x1": 432, "y0": 360, "y1": R2 - 18, "every": 7.0, "open": 1.5,
     "booth": 460, "wide": 4.0, "say": "GO ON THROUGH, DOGGY!"},
]
doors = [
    {"name": "SCREEN DOOR", "x0": 944, "x1": 960, "y0": 504, "y1": R3, "open": 6.0, "shut": 8.0, "warn": 1.0,
     "bark": True},
    {"name": "SCREEN DOOR", "x0": 2240, "x1": 2256, "y0": 456, "y1": R3, "open": 0, "warn": 1.0},
]
wagon = [{"name": "WORK WAGON", "x0": 960, "x1": 1056, "y0": R3, "y1": R3 + 6, "from": 960, "to": 2144,
          "speed": 90, "accel": 90, "rails": 48, "driver": "the track crew", "wait": 1.0}]
signs = [
    {"name": "SIGN", "x0": 1280, "x1": 1304, "y0": 600, "y1": R3 - 19, "warn": 1.2},
    {"name": "SIGN", "x0": 1512, "x1": 1536, "y0": 600, "y1": R3 - 19, "warn": 1.2},
    {"name": "SIGNAL", "x0": 1720, "x1": 1744, "y0": 600, "y1": R3 - 19, "warn": 1.2},
    {"name": "SIGN", "x0": 1856, "x1": 1880, "y0": 600, "y1": R3 - 19, "warn": 1.2},
    {"name": "SIGN", "x0": 2000, "x1": 2024, "y0": 600, "y1": R3 - 19, "warn": 1.2},
]
hazards = [
    {"name": "SUITCASE", "kind": "suitcase", "x0": 96, "x1": 116, "y0": R2 - 16, "y1": R2, "on": "ESCALATOR B",
     "every": 9.0, "warn": 1.0, "speed": 110, "say": "OOPS!", "source": "a traveller at the top lets go of it"},
    {"name": "SCRUBBER", "kind": "scrubber", "x0": 600, "x1": 632, "y0": R2 - 20, "y1": R2, "path": "{ 600, 960 }",
     "speed": 50, "warn": 1.0, "source": "the cleaner drives it along the passage (beep, a flashing light)"},
]
lamps = [
    {"x": 400, "y": R1, "checkpoint": True}, {"x": 1184, "y": R1, "checkpoint": True},
    {"x": 1408, "y": R2, "checkpoint": True}, {"x": 480, "y": R2, "checkpoint": True},
    {"x": 352, "y": R3, "checkpoint": True}, {"x": 900, "y": R3, "checkpoint": True},
    {"x": 2264, "y": R3, "checkpoint": True},
    {"x": 1208, "y": 336, "checkpoint": True},          # high: on a shelf over the walkway
]
bones = [
    # row 1
    {"x": 120, "y": R1}, {"x": 300, "y": R1}, {"x": 344, "y": 160}, {"x": 344, "y": R1}, {"x": 560, "y": R1},
    {"x": 748, "y": 148}, {"x": 820, "y": R1}, {"x": 960, "y": R1}, {"x": 1024, "y": R1}, {"x": 1100, "y": R1},
    {"x": 1300, "y": R1}, {"x": 1500, "y": R1},
    # escalator A and row 2
    {"x": 1620, "y": 244}, {"x": 1560, "y": 304}, {"x": 1500, "y": 364}, {"x": 1380, "y": R2}, {"x": 1240, "y": R2},
    {"x": 1140, "y": R2}, {"x": 900, "y": R2}, {"x": 780, "y": R2}, {"x": 660, "y": R2}, {"x": 520, "y": 396},
    {"x": 416, "y": R2}, {"x": 312, "y": 400}, {"x": 220, "y": R2},
    # escalator B and row 3
    {"x": 140, "y": 484}, {"x": 200, "y": 544}, {"x": 260, "y": 604}, {"x": 440, "y": R3}, {"x": 576, "y": 624},
    {"x": 860, "y": R3},
    # the ride (on the deck's path, low enough to take crouched), Odenplan, escalator C
    {"x": 1160, "y": R3}, {"x": 1400, "y": R3}, {"x": 1640, "y": R3}, {"x": 1960, "y": R3}, {"x": 2100, "y": R3},
    {"x": 2290, "y": R3}, {"x": 2380, "y": 604}, {"x": 2440, "y": 544},
    # the high roads: over the ticket hall, over the passage, over the platform
    {"x": 1128, "y": 112}, {"x": 1248, "y": 96}, {"x": 1360, "y": 80, "super": True, "golden": True},
    {"x": 1472, "y": 104},
    {"x": 1340, "y": 352}, {"x": 1236, "y": 336}, {"x": 1132, "y": 352}, {"x": 1040, "y": 296, "super": True},
    {"x": 988, "y": 336}, {"x": 884, "y": 320}, {"x": 780, "y": 336}, {"x": 676, "y": 352},
    {"x": 680, "y": 600}, {"x": 800, "y": 576}, {"x": 908, "y": 600},
]
L = {
    "name": "METRO", "number": 5, "title": "Pepper: Metro (paper map)", "scenery": "greybox", "time": 400,
    "start": {"x": 60, "y": R1},
    "ball": {"x": 1008, "y": R3},           # it ends up on the work wagon (see the story)
    "girl": {"x": 2536, "y": R3 - 176},     # Mia waits at the top of Odenplan's escalator (she took the train)
    "props": props, "escalators": escalators, "walkways": walkways, "gates": gates, "doors": doors,
    "wagon": wagon, "signs": signs, "hazards": hazards, "lamps": lamps, "bones": bones,
    "secrets": [{"name": "GOLDEN BONE", "x0": 1328, "x1": 1392, "y0": 68, "y1": 80},
                {"name": "VENT DUCT", "x0": 1024, "x1": 1056, "y0": 284, "y1": 296},
                {"name": "CAVE SHELF", "x0": 768, "x1": 832, "y0": 564, "y1": 576}],
    "bikes": [], "movers": [],
    "intro": ["LEVEL 5", "METRO", "THE BALL BOUNCED DOWN INTO THE METRO!", "RIDE IT DOWN!"],
}


def main(argv):
    tmx = os.path.join(T.MAPS, NAME + ".tmx")
    if os.path.exists(tmx) and "--force" not in argv:
        sys.exit("maps/%s.tmx exists (edit it in Tiled); --force overwrites it" % NAME)
    T.write_tmx(tmx, NAME, L, rows)
    print("%s -> %s (%d x %d cells)" % (NAME, os.path.relpath(tmx, T.ROOT), COLS, ROWS))


if __name__ == "__main__":
    main(sys.argv[1:])
