#!/usr/bin/env python3
"""Level 3, Rooftops, as a playable greybox (engine/round2): maps/rooftops.tmx and its export
riverwalk/level/tiled/rooftops.lua, read by riverwalk/level/rooftops.lua (not in levels.lua yet:
love riverwalk --level rooftops). See docs/rooftops_beatsheet.md.

  python3 tools/make_rooftops.py [--force]

It starts from the paper map (tools/make_rooftops_sketch.py: the same terrain, props, lamps, bones, secrets) and
makes it play:
  * the vent hoods are 4 px tall (Pepper walks onto a hood; the sketch had 8 px), and each vent's lift is set so the
    puff's apex is 16 px over the ledge it serves (as the beat sheet asks): lift = mouth - (ledge - 16)
  * the oven's vent (CHIMNEY) moves 8 px right, onto a chimney ledge 16 px longer: at x 1516 her body overlapped the
    chimney pot and the pot stopped the puff's lift (a vent is at least 17 px clear of any solid above it)
  * vents that serve the same climb start at different phases (phase, s), so neighbours do not puff together
  * the gull's nest is the magpie's code with one perch and a gull's look (L.magpie, look = "gull"): a bark within
    95 px across and 110 px up or down makes it let go of the ball, which drops onto the chimney's top
  * the loose tiles lose the sketch's `crumble` (Night Harbour's own planks); `loose = true` is the general kind
  * hints: the sauna's BARK, the nest's BARK, PICK UP, GIVE, Mia's call
Once the map has been edited in Tiled, the .tmx is the level: this script refuses to overwrite it unless --force.
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import level_to_tiled as T  # noqa: E402
import make_rooftops_sketch as K  # noqa: E402

NAME = "rooftops"
SERVES = {"KITCHEN FAN": 616, "DORMER VENT": 520, "LAUNDRY VENT": 360, "CHIMNEY": 232, "TERRACE FAN": 232,
          "SAUNA": 136}   # the floor each puff lands her on (the apex is 16 px over it)
PHASE = {"KITCHEN FAN": 0.0, "DORMER VENT": 1.5, "LAUNDRY VENT": 0.0, "CHIMNEY": 1.0, "TERRACE FAN": 0.5, "SAUNA": 0.0}


def build():
    L = copy.deepcopy(K.L)
    L["title"] = "Pepper: Rooftops (greybox)"
    for v in L["steam"]:
        v["y0"] = v["y1"] - 4
        v["lift"] = v["y0"] - (SERVES[v["name"]] - 16)
        v["phase"] = PHASE[v["name"]]
    for p in L["props"]:
        p.pop("crumble", None)
        if p["kind"] == "oneway" and p["x0"] == 1456 and p["y0"] == 360:
            p["x1"] = 1552                          # the chimney ledge, 16 px longer for the oven's vent
    for v in L["steam"]:
        if v["name"] == "CHIMNEY":                  # its mouth 17 px (her half width) clear of the chimney pot,
            v["x0"], v["x1"] = 1524, 1544           # so a puff never bumps her head on the pot (the sketch: 1516)
    L.pop("nest")
    L["magpie"] = {"look": "gull", "bark": 95, "flee": 0, "fleeWalk": 0, "dropSay": "THE GULL LET GO OF THE BALL!",
                   "perches": [{"x": 1824, "y": 136}]}
    L["ballBack"] = "THE BALL IS BACK BY THE LAMP"
    L["ballHomeAtLamps"] = True
    L["hints"] = [
        {"x0": 0, "x1": 1920, "btn": "x", "text": "PICK UP", "need": "nearball"},
        {"x0": 1640, "x1": 1800, "btn": "x", "text": "GIVE", "need": "ball", "minY": 300},
        {"x0": 1730, "x1": 1800, "btn": "b", "text": "BARK!", "need": "magpienear", "minY": 200, "maxY": 240},
        {"x0": 1600, "x1": 1720, "btn": "a", "text": "STAND ON THE FAN", "minY": 300, "maxY": 330, "need": "magpie"},
        {"x0": 590, "x1": 680, "btn": "down", "text": "HOLD: STAY PUT", "minY": 700, "maxY": 712},
        {"x0": 0, "x1": 1920, "text": "BRING ME THE BALL!", "need": "ball"},
    ]
    return L


def main(argv):
    tmx = os.path.join(T.MAPS, NAME + ".tmx")
    if os.path.exists(tmx) and "--force" not in argv:
        sys.exit("maps/%s.tmx exists (edit it in Tiled); --force overwrites it" % NAME)
    L = build()
    T.write_tmx(tmx, NAME, L, K.rows)
    lua = T.export(tmx, os.path.join(T.EXPORTS, NAME + ".lua"))
    print("%s -> %s, %s (%d x %d cells)" % (NAME, os.path.relpath(tmx, T.ROOT), os.path.relpath(lua, T.ROOT),
                                           K.COLS, K.ROWS))


if __name__ == "__main__":
    main(sys.argv[1:])
