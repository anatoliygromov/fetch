#!/usr/bin/env python3
"""Draws the first version of the tall Downtown (greybox) as a Tiled map: maps/downtown_tall.tmx and its export
riverwalk/level/tiled/downtown_tall.lua. See docs/downtown_tall_beatsheet.md.

  python3 tools/make_downtown_tall.py [--force]

It starts from Downtown as the game loads it (riverwalk/level/downtown.lua and downtown.map), moves everything
down 30 rows (240 px: the street goes from y 184 to y 424, the world is 60 rows = 480 px high, 11 x 2 screens) and
adds the high road: the roofs of the old town above the bakery row, the plaza, the fountain, tram street and the
flower market, out over the canal on a footbridge. Once the map has been edited in Tiled, the .tmx is the level:
this script refuses to overwrite it unless given --force.

What changes from Downtown (besides the shift), and why:
  * no scenery art (L.art): the town art places the street's props at y 184 (as citypark_tall)
  * the two tram zones get roadY = 424 (engine/round2: the tram drives on the street and the zone counts Pepper in
    only on the street, up to 90 px above it; on the roofs no tram comes) and lose minY
  * hints for one spot on the street show only on the street (minY 380; Mia's lines for one spot too), so "TAP: HOP" does not show on a roof
  * new: the high road (balcony, loggia over the statue, the guild house's pitched roof with its chimney (the
    golden bone), the gallery over the fountain, six roof ledges with a springy window awning, the canal
    footbridge), 2 lamps up high, 31 bones, the GOLDEN BONE secret, the landmark (Riddarholmen church's spire, by
    the river stairs where Mia waits), hints for the ways up and for barking at the cat from above
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_to_tiled as T  # noqa: E402

DY = 240                 # 30 rows of 8 px
STREET = 184 + DY        # the street's feet line: 424
NAME = "downtown_tall"
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


def roof(name, x0, y0, rise, ridge, fall, y1):
    """A pitched roof as one-way steps 8 px wide and 4 px high (Pepper walks onto 4 px steps): from (x0, feet y0)
    `rise` steps up, a ridge `ridge` px long, then `fall` steps down; the last step's feet are y1. Returns the props
    and the ridge's (x0, x1, y)."""
    out, x, y = [], x0, y0
    for k in range(rise):
        out.append(ow(name if k == 0 else "", x, x + 8, y - 4 * k))
        x += 8
    ry = y0 - 4 * rise
    out.append(ow("", x, x + ridge, ry))
    rx = (x, x + ridge, ry)
    x += ridge
    for k in range(fall):
        out.append(ow("", x, x + 8, ry + 4 * (k + 1)))
        x += 8
    assert ry + 4 * fall == y1, (ry, fall, y1)
    return out, rx


# ------------------------------------------------------------------------------------------- the high road
# (x0, x1, feet y). Pepper: tap hop 24, held jump 46, ledge scramble 58, half width 17, standing 26, crouched 16.
# Everything up here is at y 232 to 280 (144 to 192 px above the street); the old secret route of Downtown (the
# balconies and the fountain's top tier, y 336 to 344) stays as a middle tier under it, and nothing solid hangs
# lower than y 262 over it (a held jump from those balconies reaches head height y 264).
GUILD, RIDGE = roof("GUILD ROOF", 1560, 272, 7, 40, 3, 256)      # ridge 1616-1656 y 244, down to y 256 at 1680
HIGH = [
    # screen 4/5: from the bakery sign (y 304, way up A) onto a balcony, then the loggia over the statue: the cat
    # sits on the ball 67 px below it, so a bark from the loggia (x 1448-1536) scares it. The statue's hat (y 316)
    # is 36 px under the loggia: way up B, for a Pepper who picked the ball up on the street.
    ow("BALCONY", 1328, 1392, 272, label="top"),
    ow("LOGGIA", 1416, 1536, 280, label="top"),
    # screen 5/6: the guild house's pitched roof (one-way steps), its chimney on the ridge (the golden bone, 44 px
    # up: a held jump), the gallery over the fountain in two halves: between them, right over the fountain's top
    # tier (the ROOFTOPS secret), a 48 px gap; falling in lands on the tier
] + GUILD + [
    P("CHIMNEY", "solid", 1628, 1644, 200, 244, label="top"),
    P("GALLERY", "solid", 1680, 1768, 256, 262, label="below"),      # solid: over the basin, no dropping through
    P("GALLERY", "solid", 1816, 1888, 256, 262, label="below"),
    # screen 7/8: over tram street and the flower market: roof ledges 40 px apart; a springy window awning
    # launches her up to the flower house's roof
    ow("DORMER", 1920, 1976, 264, label="top"),
    ow("", 2016, 2072, 248),
    ow("", 2112, 2168, 264),
    ow("AWNING", 2208, 2264, 272, label="below", bounce=56),          # apex y 216
    ow("FLOWER ROOF", 2288, 2376, 232, label="top"),
    ow("", 2416, 2464, 248),
    # screen 9: the footbridge over the canal (solid: no dropping into the water). Its left end is over the street,
    # its right end over the crates on the far quay
    P("FOOTBRIDGE", "solid", 2480, 2640, 272, 278, label="below"),
]
DECOR = [
    # the houses behind the high road (behind Pepper)
    P("BAKERY", "decor", 1180, 1320, 300, STREET - 10, layer="back", label="top"),
    P("", "decor", 1320, 1400, 278, STREET - 10, layer="back"),
    P("", "decor", 1404, 1548, 286, STREET - 10, layer="back"),          # behind the loggia
    P("GUILD HOUSE", "decor", 1552, 1700, 250, STREET - 10, layer="back", label="top"),
    P("", "decor", 1912, 2180, 270, STREET - 10, layer="back"),
    P("", "decor", 2296, 2384, 238, STREET - 10, layer="back"),
    # the landmark: Riddarholmen church's cast-iron spire, by the river stairs (Mia), seen from the roofs
    P("RIDDARHOLMEN", "decor", 3380, 3412, 24, STREET - 10, layer="back", label="top"),
]

LAMPS_HIGH = [
    {"x": 1830, "y": 256, "checkpoint": True},     # on the gallery, after the climb with the ball and the roof
    {"x": 2420, "y": 248, "checkpoint": True},     # on the last roof ledge, after the springy window awning
]

BONES_HIGH = [
    {"x": 1360, "y": 272}, {"x": 1440, "y": 280}, {"x": 1500, "y": 280},
    {"x": 1580, "y": 264}, {"x": 1604, "y": 252}, {"x": 1636, "y": 200, "super": True, "golden": True},
    {"x": 1668, "y": 252}, {"x": 1712, "y": 256}, {"x": 1744, "y": 256}, {"x": 1792, "y": 230},
    {"x": 1852, "y": 256}, {"x": 1904, "y": 236},
    {"x": 1948, "y": 264}, {"x": 1996, "y": 236}, {"x": 2044, "y": 248}, {"x": 2092, "y": 236},
    {"x": 2140, "y": 264}, {"x": 2236, "y": 272}, {"x": 2236, "y": 228}, {"x": 2280, "y": 210},
    {"x": 2308, "y": 232}, {"x": 2360, "y": 232}, {"x": 2440, "y": 248},
    {"x": 2500, "y": 272}, {"x": 2560, "y": 272}, {"x": 2592, "y": 272}, {"x": 2624, "y": 272},
]

HINTS_HIGH = [   # inserted after the need-based hints (BARK, PICK UP, GIVE), so those still win
    {"x0": 1440, "x1": 1536, "text": "BARK FROM UP HERE!", "need": "cat", "minY": 270, "maxY": 290},
    {"x0": 1416, "x1": 1536, "btn": "down", "text": "DOWN + A: DROP", "need": "noball", "minY": 270, "maxY": 290},
    {"x0": 1262, "x1": 1312, "btn": "a", "text": "HOLD: UP ON THE ROOFS", "minY": 296, "maxY": 312},
    {"x0": 1450, "x1": 1480, "btn": "a", "text": "HOLD: UP!", "minY": 306, "maxY": 322},
    {"x0": 1600, "x1": 1628, "btn": "a", "text": "HOLD: BIG JUMP", "minY": 240, "maxY": 262},
    {"x0": 2168, "x1": 2208, "btn": "a", "text": "BOUNCE UP", "minY": 250, "maxY": 280},
]


def build():
    L = T.read_level("downtown")
    rows = T.read_rows(os.path.join(T.LEVELS, "downtown.map"))
    cols = len(rows[0])
    rows = ["." * cols] * (DY // 8) + rows
    L = shift(L)
    L.pop("art", None)
    L["title"] = "Pepper: Downtown, tall (greybox)"
    props = L["props"]
    front = [p for p in props if p["layer"] == "front"]
    rest = [p for p in props if p["layer"] != "front"]
    L["props"] = rest + DECOR + HIGH + front
    L["lamps"] = sorted(L["lamps"] + LAMPS_HIGH, key=lambda l: (l["x"], l["y"]))
    L["bones"] = L["bones"] + BONES_HIGH
    L["secrets"] = L["secrets"] + [{"name": "GOLDEN BONE", "x0": 1628, "x1": 1644, "y0": 188, "y1": 200}]
    hints = list(L["hints"])
    for h in hints:                                           # Downtown's hints for one spot: on the street only
        if (h["x1"] - h["x0"] < 600 and "minY" not in h and "maxY" not in h and not h.get("bike")
                and h.get("need") not in ("catnear", "nearball", "cat", "noball")):
            h["minY"] = STREET - 44
        if "maxY" in h and "minY" not in h:                   # "HOLD: STAY ON" (above the awning, bouncing)
            h["minY"] = h["maxY"] - 90
    k = next(i for i, h in enumerate(hints) if h.get("need") not in ("catnear", "nearball", "ball", "goose"))
    L["hints"] = hints[:k] + HINTS_HIGH + hints[k:]
    # the trams drive on the street (roadY: the zone's feet line; the zone counts Pepper in up to 90 px above it)
    L["bikes"] = [dict(b, roadY=STREET) for b in L["bikes"]]
    for b in L["bikes"]:
        b.pop("minY", None)
    L["intro"] = ["LEVEL 2", "DOWNTOWN", "A CAT IS SITTING ON THE BALL!", "ON THE STREET OR OVER THE ROOFS"]
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
