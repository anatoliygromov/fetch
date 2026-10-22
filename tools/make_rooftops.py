#!/usr/bin/env python3
"""Level 3, Rooftops, full length (branch r3/rooftops): maps/rooftops.tmx and its export
riverwalk/level/tiled/rooftops.lua, read by riverwalk/level/rooftops.lua (not in levels.lua yet:
love riverwalk --level rooftops). Design and every number: docs/rooftops_beatsheet.md.

  python3 tools/make_rooftops.py [--force]

13 x 5 screens: 4160 x 1200 px (520 x 150 cells; r7/curve added the drying yard, x 3344-3664). The skyline climbs to the right in five tiers (feet y):
the street 1144, T1 952, T1b 856, T2 760, T3 568, the roof terrace T4 376 (Mia's roof cafe), the copper roof 280,
the nest chimney's top 184. The low road (the main route) walks and rides the steam puffs up the tiers; the high
road floats over it on ledges, loose tiles and puffs (the golden bone on the bakery's chimney pot) and meets it on
the copper roof for the finale.

Engine rules this map keeps (world.lua): at most one slope per column, and in a slope's columns no other terrain
floor (props are fine); every vent's mouth at least 17 px (Pepper's half width) clear of any solid above it, so a
puff never bumps her head; every puff's apex 16 px over the floor it serves (lift = mouth - (floor - 16)).
Once the map has been edited in Tiled, the .tmx is the level: this script refuses to overwrite it unless --force.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_to_tiled as T  # noqa: E402

NAME = "rooftops"
COLS, ROWS = 480, 150
g = [["."] * COLS for _ in range(ROWS)]

STREET, T1, T1B, T2, T3, T4, COPPER, NEST = 1144, 952, 856, 760, 568, 376, 280, 184


def fill(x0, x1, y0, y1=ROWS * 8, ch="#"):
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
            g[jj][i] = "#"


# the terrain: the street, stairwell A, then roofs, each taller than the last ---------------------------------------
fill(0, 576, STREET)                     # the street (the cafe where the gull took the ball)
stairs(576, STREET, 24)                  # stairwell A: up 192 px to T1
fill(768, 1280, T1)                      # T1, the bakery's flat roof
stairs(896, T1, 8)                       # R1, a small pitched roof (ridge 888)
stairs(960, T1, 8, "\\")
fill(1280, 1568, T1B)                    # T1b, one floor higher (the kitchen fan lifts her up the wall)
fill(1568, 1664, T1)                     # the light well: 96 px wide, 96 deep (the courtyard fan lifts her out)
fill(1664, 2048, T1B)
stairs(1792, T1B, 8)                     # R2, a pitched roof (ridge 792)
stairs(1856, T1B, 8, "\\")
fill(2048, 3328, T2)                     # T2, the laundry's roof with the roof garden (the goose)
fill(3328, 3552, T3)                     # T3, the roof bar (the awning, the water tank, the gull)
fill(3552, 3840, T4)                     # T4, the roof terrace: Mia's roof cafe
fill(3728, 3760, NEST, T4)               # the nest chimney: the landmark, 192 px over the terrace
# the market hall (2048-2688, on T2): its glass roof R3, the sweep's chimney block (a puff gets her over it), and
# the skylight: a dip 96 px wide and 96 deep with loose tiles over it and a fan in it (beat 2: practise both)
stairs(2112, T2, 8)
stairs(2176, T2, 8, "\\")
fill(2400, 2464, 664)
fill(2528, 2624, T2, T1B, ".")
rows = ["".join(r) for r in g]


def P(name, kind, x0, x1, y0, y1, layer="play", **kw):
    d = {"name": name, "kind": kind, "layer": layer, "x0": x0, "x1": x1, "y0": y0, "y1": y1}
    d.update(kw)
    return d


def ow(name, x0, x1, y, **kw):
    return P(name, "oneway", x0, x1, y, y + 6, **kw)


def loose(x0, y):
    return P("", "oneway", x0, x0 + 24, y, y + 6, loose=True)


props = [
    # the street: the cafe, its table (the gull took the ball off it), the far skyline
    P("CAFE", "decor", 24, 216, 1064, 1144, layer="back", label="top"),
    P("CAFE TABLE", "solid", 104, 136, 1120, 1124),
    P("STAIRWELL A", "decor", 568, 776, 904, 1144, layer="back", label="top"),
    P("BAKERY", "decor", 776, 1272, 960, 1144, layer="back", label="top"),
    P("MARKET HALL", "decor", 2056, 2680, 768, 952, layer="back", label="top"),
    P("SWEEP'S CHIMNEYS", "decor", 2400, 2464, 640, 664, layer="back", label="top"),
    P("LAUNDRY", "decor", 2696, 3320, 768, 952, layer="back", label="top"),
    P("ROOF GARDEN", "decor", 2752, 2976, 744, 760, layer="back", label="top"),
    P("ROOF BAR", "decor", 3336, 3544, 576, 760, layer="back", label="top"),
    P("ROOF CAFE", "decor", 3560, 3720, 312, 376, layer="back", label="top"),
    P("STAIRS UP (MIA)", "decor", 3776, 3840, 296, 376, layer="back", label="top"),
    P("NEST", "decor", 3724, 3764, 174, 184, layer="back", label="top"),
    P("RAILING", "decor", 3552, 3720, 360, 376, layer="back"),
    # the low road: the light well's loose tiles (beat 1, safe: the well's floor and its fan are under them),
    # the balcony with three loose tiles (beat 2), the roof bar's springy awning and the water tank (beat 3)
    loose(1572, T1B), loose(1604, T1B), loose(1636, T1B),
    loose(2532, T2), loose(2564, T2), loose(2596, T2),
    ow("BALCONY", 3072, 3144, 664, label="top"),
    loose(3152, 664), loose(3184, 664), loose(3216, 664),
    ow("", 3248, 3320, 664),
    P("AWNING", "oneway", 3408, 3464, 552, 556, bounce=120, label="top"),
    P("WATER TANK", "solid", 3480, 3552, 448, 568, label="top"),
    # the copper roof over the terrace: one-way, the terrace fan lifts her up through it
    ow("COPPER ROOF", 3456, 3712, COPPER, label="top"),
    # the high road: ledges, loose tiles and puffs over the roofs, the golden bone on the chimney pot
    ow("ATTIC", 1424, 1520, 760, label="top"),
    loose(1552, 760), loose(1608, 760),
    ow("", 1664, 1760, 760),
    ow("", 1792, 1856, 728),
    ow("", 1888, 1952, 696),
    ow("PIGEON LOFT", 1960, 2080, 600, label="top"),
    ow("", 2112, 2208, 568), ow("", 2240, 2336, 536),          # over the market hall: up two ledges,
    loose(2368, 536), loose(2424, 536), ow("", 2480, 2560, 536),   # two loose tiles,
    ow("", 2592, 2720, 600),                                   # and down onto the next run
    loose(2752, 600), loose(2808, 600),
    ow("", 2848, 2976, 600),
    P("CHIMNEY POT", "solid", 2896, 2920, 552, 600, label="top"),
    ow("ROOF WALKWAY", 2984, 3200, 456, label="top"),
    loose(3232, 456), loose(3288, 456),
    ow("", 3344, 3456, 424),
]

# the vents: (name, x0, x1, the floor its hood stands on, the floor it serves, every, phase, source)
VENTS = [
    ("KITCHEN FAN", 1244, 1268, T1, T1B, 3.0, 0.0, "the bakery's kitchen (the baker)"),
    ("COURTYARD FAN", 1604, 1628, T1, T1B, 3.0, 1.0, "the courtyard's boiler room"),
    ("LAUNDRY VENT", 2012, 2036, T1B, T2, 4.0, 0.5, "the laundry room's dryer"),
    ("SWEEP VENT", 2364, 2384, T2, 664, 4.0, 1.0, "the market hall's heating"),
    ("SKYLIGHT FAN", 2564, 2588, T1B, T2, 3.0, 0.0, "the market hall's fan, under the skylight"),
    ("GARDEN VENT", 3040, 3064, T2, 664, 4.0, 0.0, "the flats' bathroom fans"),
    ("BALCONY VENT", 3284, 3304, 664, T3, 4.0, 1.5, "the flat's kitchen hood"),
    ("TANK VENT", 3504, 3524, 448, T4, 4.0, 0.5, "the roof bar's dishwasher"),
    ("TERRACE FAN", 3600, 3624, T4, COPPER, 4.0, 0.5, "the roof cafe's kitchen"),
    ("SAUNA", 3688, 3708, COPPER, NEST, 0, 0.0, "the roof sauna (a bark: the guest throws water on the stones)"),
    # the high road
    ("ATTIC FAN", 1388, 1408, T1B, 760, 3.0, 2.0, "the attic flat's bathroom fan"),
    ("LOFT VENT", 1928, 1948, 696, 600, 3.0, 0.0, "the pigeon loft's warm air"),
    ("BAKERY CHIMNEY", 2944, 2964, 600, 456, 3.5, 1.0, "the bakery's oven"),
    ("BAR FAN", 3428, 3448, 424, COPPER, 3.0, 1.0, "the roof bar's kitchen"),
]
steam = []
for name, x0, x1, on, serves, every, phase, source in VENTS:
    y0 = on - 4
    v = {"name": name, "x0": x0, "x1": x1, "y0": y0, "y1": on, "lift": y0 - (serves - 16), "every": every,
         "warn": 0.8 if every else 0.6, "puff": 0.9 if every else 1.0, "phase": phase, "source": source}
    if not every:
        v["bark"] = True
    steam.append(v)

lamps = [
    {"x": 40, "y": STREET, "checkpoint": True},
    {"x": 1296, "y": T1B, "checkpoint": True},        # after the first puff (the kitchen fan)
    {"x": 2064, "y": T2, "checkpoint": True},         # after the light well and the laundry vent
    {"x": 3336, "y": T3, "checkpoint": True},         # after the balcony's loose tiles: a rest
    {"x": 3560, "y": T4, "checkpoint": True},         # after the gull and the awning: the roof terrace
    {"x": 1976, "y": 600, "checkpoint": True},        # high: the pigeon loft, after the first tiles and ledges
    {"x": 2992, "y": 456, "checkpoint": True},        # high: the roof walkway, after the golden bone
]


def B(x, y, **kw):
    d = {"x": x, "y": y}
    d.update(kw)
    return d


bones = [
    # the low road
    B(160, STREET), B(300, STREET), B(420, STREET), B(620, 1100), B(680, 1040), B(740, 980),
    B(860, T1), B(928, 920), B(992, 920), B(1100, T1), B(1180, T1), B(1256, 880),
    B(1340, T1B), B(1480, T1B), B(1584, T1B - 20), B(1616, T1B - 20), B(1648, T1B - 20), B(1616, T1),
    B(2080, T2), B(2144, 728), B(2208, 728), B(2300, T2), B(2374, 700), B(2432, 664), B(2496, T2),
    B(2544, T2 - 20), B(2576, T2 - 20), B(2608, T2 - 20), B(2576, T1B), B(2660, T2),
    B(1720, T1B), B(1824, 824), B(1888, 824), B(1960, T1B), B(2024, 790),
    B(2740, T2), B(2840, T2 - 30), B(2940, T2), B(3020, T2), B(3052, 700), B(3108, 664), B(3164, 664),
    B(3196, 664), B(3228, 664), B(3280, 664), B(3296, 600), B(3380, T3), B(3436, 500), B(3516, 448),
    B(3516, 400), B(3600, T4), B(3660, T4), B(3700, 330), B(3744, NEST, super=True),
    # the high road
    B(1440, 760), B(1500, 760), B(1564, 760), B(1620, 760), B(1700, 760), B(1824, 728), B(1920, 696),
    B(2000, 600), B(2700, 600), B(2764, 600), B(2820, 600), B(2880, 600), B(2908, 552, super=True, golden=True),
    B(2950, 560), B(3060, 456), B(3140, 456), B(3244, 456), B(3300, 456), B(3370, 424), B(3420, 424),
    B(3500, COPPER), B(3540, COPPER),
]

hints = [
    {"x0": 0, "x1": 3840, "btn": "x", "text": "PICK UP", "need": "nearball"},
    {"x0": 3560, "x1": 3720, "btn": "x", "text": "GIVE", "need": "ball", "minY": 340, "maxY": 380},
    {"x0": 3650, "x1": 3720, "btn": "y", "text": "BARK!", "need": "magpienear", "minY": 250, "maxY": 290},
    {"x0": 3570, "x1": 3650, "btn": "a", "text": "HOP ON FAN", "minY": 340, "maxY": 380, "need": "magpie"},
    {"x0": 1200, "x1": 1280, "text": "STAND ON THE FAN: STEAM LIFTS YOU!", "minY": 900, "maxY": 956},
    {"x0": 1520, "x1": 1572, "text": "LOOSE TILES! RUN!", "minY": 820, "maxY": 860},
    {"x0": 2300, "x1": 2390, "text": "RIDE THE STEAM OVER THE CHIMNEYS", "minY": 720, "maxY": 764},
    {"x0": 3340, "x1": 3540, "btn": "down", "text": "DUCK!", "need": "gull", "minY": 400, "maxY": 572},
    {"x0": 3370, "x1": 3410, "btn": "a", "text": "BOUNCE ON IT", "minY": 540, "maxY": 572},
    {"x0": 0, "x1": 3840, "text": "BRING ME THE BALL!", "need": "ball"},
]

L = {
    "name": "ROOFTOPS", "number": 4, "title": "Pepper: Rooftops (greybox)", "scenery": "greybox", "time": 300,
    "start": {"x": 40, "y": STREET},
    "ball": {"x": 3744, "y": NEST},          # in the gull's nest
    "girl": {"x": 3640, "y": T4},            # Mia at the roof cafe's table (she went up the building's stairs)
    "props": props, "steam": steam, "lamps": lamps, "bones": bones,
    "critters": [
        {"kind": "goose", "x": 2880, "y": T2, "x0": 2760, "x1": 2980, "speed": 22},   # the roof garden's goose
        {"kind": "gull", "x0": 3336, "x1": 3540, "every": 4.0},                        # over the roof bar
    ],
    "magpie": {"look": "gull", "bark": 95, "flee": 0, "fleeWalk": 0, "dropSay": "THE GULL LET GO OF THE BALL!",
               "perches": [{"x": 3744, "y": NEST}]},
    "secrets": [{"name": "GOLDEN BONE", "x0": 2896, "x1": 2920, "y0": 540, "y1": 552},
                {"name": "ROOF WALKWAY", "x0": 3080, "x1": 3140, "y0": 444, "y1": 456}],
    "hints": hints,
    "ballBack": "THE BALL IS BACK BY THE LAMP", "ballHomeAtLamps": True,
    "bikes": [], "movers": [],
    "intro": ["LEVEL 4", "ROOFTOPS", "A GULL TOOK THE BALL TO ITS NEST!", "MIA: MEET ME AT THE ROOF CAFE!"],
    "outro": ["AFTERNOON ON SODER THE BALL", "SLIPPED AND ROLLED DOWN THE HILL..."],
}


# ---- r7/curve: one more screen, the drying yard (x 3344-3664 on T3, 568), between the balcony vent and the roof bar.
# Everything from x 3344 on moves 320 px right (the roof bar, the terrace, the copper roof, the nest, Mia; the high
# road's ledge 424 and the bar fan), and the drying yard is drawn into the gap. It is the level's combined beat
# before the finale: loose tiles and held jumps together, under the roof bar's gull (its band now starts over the
# yard). A dip 144 px wide and 40 deep, and over it a staircase of two loose tiles up to a chimney stack:
# three held jumps (gaps 32, 32 px up each), no stopping on a tile (it drops 0.6 s after she lands). A hop that
# should have been a held jump, or a tile left too late, drops her into the dip (no harm: a held jump and a scramble
# get her back out onto the yard's floor, left). Off the stack's right side she drops onto the roof bar's springy
# awning, which bounces her onto the water tank. The high road crosses above at 456 (a ledge, two loose tiles);
# its ledge 424 now starts over the stack.
CUT, D = 3344, 320
COLS += D // 8
rows = [r[:CUT // 8] + r[CUT // 8 - 1] * (D // 8) + r[CUT // 8:] for r in rows]


def _shift(o):
    if isinstance(o, dict):
        for k in list(o):
            if k in ("x", "x0", "x1") and isinstance(o[k], (int, float)):
                o[k] = o[k] + D if o[k] >= CUT else o[k]
            else:
                _shift(o[k])
    elif isinstance(o, list):
        for e in o:
            _shift(e)


_shift(L)
WELL3, WELL3_FLOOR = (3432, 3576), 608                   # 144 wide, 40 deep: she scrambles out (58 px)
rows = [list(r) for r in rows]
for j in range(T3 // 8, WELL3_FLOOR // 8):
    for i in range(WELL3[0] // 8, WELL3[1] // 8):
        rows[j][i] = "."
rows = ["".join(r) for r in rows]
props += [
    P("DRYING YARD", "decor", 3352, 3424, 544, 568, layer="back", label="top"),
    loose(3464, 536), loose(3520, 504),                  # the staircase over the well: held jumps, keep moving
    P("CHIMNEY STACK", "solid", 3576, 3680, 472, 568, label="top"),
    ow("", 3344, 3440, 456), loose(3472, 456), loose(3528, 456),   # the high road: on from the walkway's tiles
]
for pr in props:                                         # the high road's ledge 424 reaches back over the stack
    if pr["x0"] == 3344 + D and pr["y0"] == 424:
        pr["x0"] = 3600
hints.insert(-1, {"x0": 3380, "x1": 3432, "btn": "a", "text": "HOLD: BIG JUMP", "minY": 540, "maxY": 572})
bones += [B(3384, T3), B(3476, 536), B(3532, 504), B(3500, WELL3_FLOOR), B(3600, 472), B(3640, 472), B(3664, 472),
          B(3700, T3), B(3392, 456), B(3484, 456), B(3540, 456), B(3628, 424)]

def main(argv):
    tmx = os.path.join(T.MAPS, NAME + ".tmx")
    if os.path.exists(tmx) and "--force" not in argv:
        sys.exit("maps/%s.tmx exists (edit it in Tiled); --force overwrites it" % NAME)
    T.write_tmx(tmx, NAME, L, rows)
    lua = T.export(tmx, os.path.join(T.EXPORTS, NAME + ".lua"))
    print("%s -> %s, %s (%d x %d cells)" % (NAME, os.path.relpath(tmx, T.ROOT), os.path.relpath(lua, T.ROOT),
                                           COLS, ROWS))


if __name__ == "__main__":
    main(sys.argv[1:])
