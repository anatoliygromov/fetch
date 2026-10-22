#!/usr/bin/env python3
"""Draws the first version of the tall City Park (greybox) as a Tiled map: maps/citypark_tall.tmx and its export
riverwalk/level/tiled/citypark_tall.lua. See docs/citypark_tall_beatsheet.md.

  python3 tools/make_citypark_tall.py [--force]

It starts from City Park as the game loads it (riverwalk/level/citypark.lua, i.e. maps/citypark.tmx), moves
everything down 18 rows (144 px: the path goes from y 184 to y 328, the world is 48 rows = 384 px high) and adds
the treetop tier (the high road), the play tower and the big oak, the magpie's new perches, lamps, bones, secrets
and hints. Once the map has been edited in Tiled, the .tmx is the level: this script refuses to overwrite it
unless given --force.

What changes from City Park (besides the shift), and why:
  * the three willow branches over the pond go (a fall from them landed in the water); the high road crosses the
    pond on the treetop walk instead, a solid boardwalk with no gaps over water
  * the hollow log is drawn as a plain box (setpieces.lua draws the hollow log down to y 184)
  * no park art (L.art): the art and the cart code assume the path at y 184 (docs/citypark_tall_beatsheet.md,
    "What the engine must add")
  * the two leaf-cart zones are kept on a note layer "#carts" (the game skips layers named #...): today a cart
    zone only starts while Pepper's feet are above y 184 and the cart drives at y 184, which is the treetop tier
    here. They go back to class "bikes" once the engine reads a zone's y (their property y = 328 is ready); their
    two hints ("CART! GET UP HIGH!", "ANOTHER CART! UP HIGH!", bike = true) are left out until then
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_to_tiled as T  # noqa: E402

DY = 144                 # 18 rows of 8 px
PATH = 184 + DY          # the low road's feet line: 328
NAME = "citypark_tall"
YKEYS = ("y", "y0", "y1", "maxY", "minY")


def shift(item):
    if isinstance(item, dict):
        return {k: (v + DY if k in YKEYS and isinstance(v, (int, float)) else shift(v)) for k, v in item.items()}
    if isinstance(item, list):
        return [shift(v) for v in item]
    return item


def P(name, kind, x0, x1, y0, y1, layer="play", **kw):
    d = {"name": name, "kind": kind, "layer": layer, "x0": x0, "x1": x1, "y0": y0, "y1": y1}
    d.update(kw)
    return d


def ow(name, x0, x1, y, **kw):           # a one-way ledge 6 px thick, feet at y
    return P(name, "oneway", x0, x1, y, y + 6, **kw)


# ------------------------------------------------------------------------------------------- the high road
# (x0, x1, feet y). Pepper: tap hop 24, held jump 46, ledge scramble 58, half width 17, standing 26, crouched 16.
HIGH = [
    # screen 3: from the hedge top (y 256) up into the plane tree, then the treetop walk over the pond
    ow("PLANE TREE", 608, 704, 216, label="top"),
    P("TREETOP WALK", "solid", 704, 944, 216, 222, label="below"),   # solid: no dropping through over the water
    # screen 4: the lime trees over the goose lawn (one-way, 48 px apart)
    ow("LIMES", 976, 1040, 200, label="top"),
    ow("", 1088, 1144, 184),
    ow("", 1192, 1248, 200),
    ow("", 1296, 1352, 232),                       # over the bin: from its top (y 272) a held jump up (40)
    # screen 5: over the leaf-cart run
    ow("", 1400, 1456, 216),
    ow("", 1504, 1560, 200),
    ow("", 1600, 1640, 200),
    # screen 6: the old oak's crown (walk on it), its top twig (the golden bone), a stub on its right side
    ow("CROWN", 1656, 1832, 192, label="top"),
    ow("TWIG", 1756, 1788, 152, label="top"),
    ow("", 1840, 1872, 224),                       # from the oak's top branch (y 244) up to the crown
    # screen 7: the ash on the near bank, then the alder walk over the creek (solid), with a low bough on it
    ow("ASH", 1888, 1968, 200, label="top"),
    P("ALDER WALK", "solid", 1968, 2312, 200, 206, label="below"),
    P("LOW BOUGH", "solid", 2216, 2248, 166, 182, label="top"),    # crawl under it (16 px high) or hop over
    # screen 8: the rose arbour's top over the second cart run
    ow("ARBOUR", 2344, 2400, 216, label="top"),
    ow("", 2448, 2496, 200),
    ow("", 2544, 2592, 216),
]
# screen 9: the play tower (two decks above the slide tower, which is terrain with its top at y 296) and the big oak
TOWER = [
    ow("", 2600, 2656, 256),
    ow("PLAY TOWER", 2616, 2672, 216, label="top"),
    ow("BOUGH", 2688, 2744, 184, label="top"),
    ow("", 2776, 2840, 152),
    ow("", 2696, 2752, 120),
    ow("NEST BOUGH", 2768, 2864, 88, label="top"),
]
DECOR = [
    # the trees of the high road (behind Pepper): trunks and crowns
    P("", "decor", 640, 652, 222, PATH, layer="back"),                # the plane tree's trunk
    P("", "decor", 592, 720, 168, 216, layer="back"),                # its crown
    P("", "decor", 1004, 1012, 206, PATH, layer="back"), P("", "decor", 1112, 1120, 190, PATH, layer="back"),
    P("", "decor", 1216, 1224, 206, PATH, layer="back"), P("", "decor", 1420, 1428, 222, PATH, layer="back"),
    P("", "decor", 1528, 1536, 206, PATH, layer="back"),
    P("", "decor", 960, 1576, 150, 184, layer="back"),               # the limes' crowns, one long band
    P("", "decor", 1640, 1848, 120, 188, layer="back"),              # the old oak's crown, now up to y 120
    P("", "decor", 1916, 1924, 206, PATH, layer="back"),             # the ash's trunk
    P("", "decor", 1872, 2320, 140, 196, layer="back"),              # ash and alders' crowns
    P("", "decor", 2392, 2400, 222, PATH, layer="back"), P("", "decor", 2584, 2592, 222, PATH, layer="back"),  # arbour posts
    P("", "decor", 2604, 2608, 222, 296, layer="back"),              # the play tower's posts
    P("", "decor", 2664, 2668, 222, 296, layer="back"),
    P("BIG OAK", "decor", 2744, 2776, 94, PATH, layer="back", label="top"),   # the landmark: trunk
    P("", "decor", 2600, 2880, 8, 120, layer="back"),                # and its crown, the highest thing in the park
    P("NEST", "decor", 2824, 2852, 78, 88, layer="back"),
]

LAMPS_HIGH = [
    {"x": 864, "y": 216, "checkpoint": True},      # a lantern on the treetop walk (after the climb up from the hedge)
    {"x": 1696, "y": 192, "checkpoint": True},     # on the old oak's crown (after the lime trees)
    {"x": 2624, "y": 216, "checkpoint": True},     # the play tower's top deck (both roads meet here; the oak above)
]

BONES_HIGH = [
    {"x": 640, "y": 216}, {"x": 680, "y": 216},
    {"x": 744, "y": 216}, {"x": 784, "y": 216}, {"x": 824, "y": 216, "super": True}, {"x": 904, "y": 216},
    {"x": 1008, "y": 200}, {"x": 1116, "y": 184}, {"x": 1220, "y": 200}, {"x": 1324, "y": 232},
    {"x": 1428, "y": 216}, {"x": 1532, "y": 200}, {"x": 1620, "y": 200},
    {"x": 1680, "y": 192}, {"x": 1740, "y": 192}, {"x": 1810, "y": 192},
    {"x": 1772, "y": 152, "super": True, "golden": True},           # THE golden bone, on the old oak's top twig
    {"x": 1856, "y": 224}, {"x": 1928, "y": 200},
    {"x": 2040, "y": 200}, {"x": 2100, "y": 200}, {"x": 2232, "y": 200}, {"x": 2280, "y": 200},
    {"x": 2372, "y": 216}, {"x": 2472, "y": 200}, {"x": 2568, "y": 216},
    {"x": 2640, "y": 256}, {"x": 2716, "y": 184}, {"x": 2808, "y": 152}, {"x": 2724, "y": 120},
]

PERCHES = [
    {"x": 240, "y": PATH, "flee": 80},    # 1 the path past the log
    {"x": 400, "y": 282},                 # 2 the bench's backrest (the ball lands on the seat)
    {"x": 656, "y": 264},                 # 3 the lamp post by the hedge (the ball drops to the path)
    {"x": 840, "y": 216},                 # 4 NEW the treetop walk's rail: only a dog up there can bark at it
    {"x": 1268, "y": 312},                # 5 the log on the goose lawn
    {"x": 1345, "y": 272},                # 6 the bin (the ball stays on top)
    {"x": 1624, "y": 244},                # 7 the lamp post before the old oak (the ball drops to the path)
    {"x": 1800, "y": 192},                # 8 NEW the old oak's crown: bark from its branches or the crown
    {"x": 2160, "y": 200},                # 9 NEW the alder walk over the creek: only from the high road
    {"x": 2428, "y": 282},                # 10 the rose walk bench's backrest (the ball lands on the seat)
    {"x": 2752, "y": 280},                # 11 the climbing frame's top bar
    {"x": 2832, "y": 88},                 # 12 its nest at the top of the big oak: its last perch
]

HINTS_HIGH = [   # inserted after the need-based hints (BARK, PICK UP, GIVE), so those still win
    {"x0": 2560, "x1": 2880, "text": "IT FLEW UP TO ITS NEST IN THE BIG OAK!", "need": "magpie"},
    {"x0": 2768, "x1": 2880, "btn": "down", "text": "DOWN + A: DROP", "need": "ball", "maxY": 160},
    {"x0": 528, "x1": 600, "btn": "a", "text": "HOLD: UP THE TREE", "minY": 250, "maxY": 262},
    {"x0": 1744, "x1": 1800, "btn": "a", "text": "HOLD: UP!", "minY": 238, "maxY": 250},
    {"x0": 2560, "x1": 2660, "btn": "a", "text": "HOLD: CLIMB THE TOWER", "minY": 250},
    {"x0": 2196, "x1": 2216, "btn": "down", "text": "CRAWL", "minY": 190, "maxY": 210},
]


def build():
    L = T.read_level("citypark")
    rows = T.read_rows(os.path.join(T.LEVELS, "citypark.map"))
    cols = len(rows[0])
    rows = ["." * cols] * (DY // 8) + rows
    L = shift(L)
    L.pop("art", None)
    L.pop("pieces", None)
    L["title"] = "Pepper: City Park, tall (greybox)"
    # the willow branches over the pond (one-way, x 672 / 776 / 880) go: the treetop walk replaces them
    props = [p for p in L["props"] if not (p["kind"] == "oneway" and p["x0"] in (672, 776, 880))]
    for p in props:
        if p["name"] == "HOLLOW LOG":
            p.pop("hidden", None)
        if p["name"] == "WILLOWS":
            p["label"] = "below"
    front = [p for p in props if p["layer"] == "front"]
    rest = [p for p in props if p["layer"] != "front"]
    L["props"] = rest + DECOR + HIGH + TOWER + front
    L["lamps"] = sorted(L["lamps"] + LAMPS_HIGH, key=lambda l: (l["x"], l["y"]))
    willow_bones = {(700, 120 + DY), (804, 112 + DY), (908, 120 + DY)}
    L["bones"] = [b for b in L["bones"] if (b["x"], b["y"]) not in willow_bones] + BONES_HIGH
    L["secrets"] = [s for s in L["secrets"] if s["name"] != "WILLOWS"] + [
        {"name": "TREETOP WALK", "x0": 784, "x1": 864, "y0": 204, "y1": 216},
        {"name": "GOLDEN BONE", "x0": 1756, "x1": 1788, "y0": 140, "y1": 152},
    ]
    L["magpie"]["perches"] = PERCHES
    hints = [h for h in L["hints"] if not h.get("bike")]     # "CART! GET UP HIGH!": back with the carts
    for h in hints:                                           # City Park's hints for one spot: on the low road only
        if h["x1"] - h["x0"] < 600 and "minY" not in h:
            h["minY"] = 290
    k = next(i for i, h in enumerate(hints) if not h.get("need") or h["need"] not in ("magpienear", "nearball", "ball"))
    L["hints"] = hints[:k] + HINTS_HIGH + hints[k:]
    # the leaf carts wait on a note layer until the engine reads a zone's y (see the docstring)
    L["#carts"] = [dict(b, y=PATH) for b in L.pop("bikes")]
    for b in L["#carts"]:
        b.pop("minY", None)
    L["bikes"] = []
    L["intro"] = ["LEVEL 1", "CITY PARK", "A MAGPIE STOLE MIA'S BALL!", "UP IN THE TREES OR DOWN ON THE PATH"]
    return L, rows


def main(argv):
    tmx = os.path.join(T.MAPS, NAME + ".tmx")
    if os.path.exists(tmx) and "--force" not in argv:
        sys.exit("maps/%s.tmx exists (edit it in Tiled); --force overwrites it" % NAME)
    L, rows = build()
    T.write_tmx(tmx, NAME, L, rows)
    lua = T.export(tmx, os.path.join(T.EXPORTS, NAME + ".lua"))
    print("%s -> %s, %s (%d x %d cells)" % (NAME, os.path.relpath(tmx, T.ROOT), os.path.relpath(lua, T.ROOT),
                                           len(rows[0]), len(rows)))


if __name__ == "__main__":
    main(sys.argv[1:])
