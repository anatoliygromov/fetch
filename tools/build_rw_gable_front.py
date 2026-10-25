#!/usr/bin/env python3
"""River Walk gable house, ground floor at true scale (46 px a metre). Pilot, 25 Oct 2026.

Owner's call (25 Oct): true-scale ground floors, upper floors run off the top of the screen (Lion King style).
Built from parts drawn once and stamped on an integer grid (BIBLE 3, the crispness bar). Every colour is one of
the approved gable's own 24 (riverwalk/art/scene/gable.png); no new colour, no resampling, binary alpha.

Slot: back layer, decoration (no outline, edges by a darker shade of its own colour), 200 x 174, base row on the
pavement's back edge (y 174). Sizes: door opening 46 x 100 (2.2 m), fanlight 16, window 52 x 76 (1.1 x 1.65 m),
ground storey 156 (3.4 m), plinth 12.

Usage:
  build_rw_gable_front.py OUTDIR            writes gable_front.png (flat) and one PNG per layer
  build_rw_gable_front.py OUTDIR --parts    also a sheet of the parts at 8x
"""
import os
import sys

import numpy as np
from PIL import Image

W, H = 200, 174
HEX = {  # the approved gable's colours, named by material
    "wall": "f1c57e", "wall_shade": "d9ad72",
    "stone": "f7d6a2", "stone_shade": "c39764",
    "trim_hi": "fafbf9", "trim": "ebe9e1", "trim_in": "b2bbc5", "trim_sh": "8e959f",
    "glass": "5f7387", "glass_hi": "74889b", "glass_dk": "465267",
    "door": "445b43", "door_dk": "2a3f2e", "door_hi": "58725a",
    "iron": "35455f", "iron_dk": "314058",
    "plinth_cap": "c4ac8d", "plinth": "ab8c6b", "plinth_dk": "785747",
}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in HEX.items()}


class Layer:
    def __init__(self, name):
        self.name = name
        self.px = np.zeros((H, W), dtype=object)
        self.px[:] = None

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.px[y, x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def stamp(self, part, x, y):
        for (dx, dy), c in part.items():
            self.put(x + dx, y + dy, c)

    def image(self):
        a = np.zeros((H, W, 4), dtype=np.uint8)
        for y in range(H):
            for x in range(W):
                c = self.px[y, x]
                if c is not None:
                    a[y, x, :3] = RGB[c]
                    a[y, x, 3] = 255
        return Image.fromarray(a, "RGBA")


# ---- parts, each drawn once -------------------------------------------------------------------------------

def part_window(w=52, h=76):
    """Swedish two-casement window, three panes a casement. Light from the left: lit frame left and top,
    shadow on the right. Top panes catch the sky (glass_hi)."""
    p = {}
    def r(x, y, ww, hh, c):
        for yy in range(y, y + hh):
            for xx in range(x, x + ww):
                p[(xx, yy)] = c
    r(0, 0, w, h, "trim")                       # frame body
    r(0, 0, w, 1, "trim_hi"); r(0, 0, 1, h, "trim_hi")
    r(w - 1, 1, 1, h - 1, "trim_sh")
    # two casements, inner edges trim_in, glass inside
    cw = (w - 3 * 3) // 2                       # 3 px outer frame each side, 3 px mullion
    for k, cx in enumerate((3, 3 + cw + 3)):
        r(cx, 3, cw, h - 6, "glass")
        pane_h = (h - 6 - 2 * 2) // 3           # two 2 px glazing bars
        for i in range(3):
            py = 3 + i * (pane_h + 2)
            if i == 0:
                r(cx, py, cw, pane_h, "glass_hi")
            r(cx, py, cw, 1, "glass_dk")        # shadow of the bar or frame above
            r(cx, py, 1, pane_h, "glass_dk")    # shadow of the frame on the left
            if i < 2:
                r(cx, py + pane_h, cw, 1, "trim")
                r(cx, py + pane_h + 1, cw, 1, "trim_in")
        r(cx - 1, 3, 1, h - 6, "trim_in")       # inner edge of the frame, left side of each casement
    return p


def part_sill(w):
    p = {}
    for x in range(w):
        p[(x, 0)] = "trim_hi"
        p[(x, 1)] = "trim"
        p[(x, 2)] = "trim_sh"
        p[(x, 3)] = "stone_shade"                   # cast shadow on the wall
    p[(0, 1)] = "trim_hi"
    return p


def part_lintel(w):
    p = {}
    for x in range(w):
        p[(x, 0)] = "trim_hi"
        p[(x, 1)] = "trim"
        p[(x, 2)] = "trim"
        p[(x, 3)] = "trim_sh"
    for y in range(4):
        p[(0, y)] = "trim_hi"
        p[(w - 1, y)] = "trim_sh" if y else "trim_hi"
    return p


def part_door_leaf(w=23, h=100):
    """One door leaf: green with two recessed panels (shadow top and left inside the panel)."""
    p = {}
    for y in range(h):
        for x in range(w):
            p[(x, y)] = "door"
    for y in range(h):
        p[(w - 1, y)] = "door_dk"               # the joint between leaves / shadow side
    def panel(x0, y0, pw, ph):
        for x in range(x0, x0 + pw):
            p[(x, y0)] = "door_dk"
            p[(x, y0 + ph - 1)] = "door_hi"
        for y in range(y0, y0 + ph):
            p[(x0, y)] = "door_dk"
            p[(x0 + pw - 1, y)] = "door_hi" if y > y0 else "door_dk"
    panel(4, 8, w - 9, 38)
    panel(4, 54, w - 9, 38)
    for y in (49, 50, 51):
        p[(w - 5, y)] = "stone_shade"                                # brass handle
    return p


def part_fanlight(w=46, h=16):
    p = {}
    for y in range(h):
        for x in range(w):
            p[(x, y)] = "glass_hi" if y < 6 else "glass"
    for x in range(w):
        p[(x, 0)] = "glass_dk"
    for y in range(h):
        p[(0, y)] = "glass_dk"
    for k in range(1, 4):                       # three upright bars, 2 px
        bx = k * w // 4
        for y in range(h):
            p[(bx, y)] = "trim"; p[(bx + 1, y)] = "trim_in"
    for x in range(w):                          # transom bar under the fanlight
        p[(x, h - 2)] = "trim"; p[(x, h - 1)] = "trim_in"
    return p


def part_surround(w, h, t=5):
    """Ochre stone surround around the door, lit on the left, shaded right and under the top."""
    p = {}
    for y in range(h):
        for x in range(w):
            if x < t or x >= w - t or y < t + 1:
                p[(x, y)] = "stone"
    for y in range(h):
        p[(w - 1, y)] = "stone_shade"; p[(w - t, y)] = "stone_shade" if y > t else p.get((w - t, y))
    for x in range(t, w - t):
        p[(x, t)] = "stone_shade"               # under the lintel, over the opening
    for x in range(w):
        p[(x, 0)] = "trim_hi" if x < w - 1 else "stone_shade"
    return p


def part_step(w):
    p = {}
    for x in range(w):
        p[(x, 0)] = "plinth_cap"
        for y in (1, 2, 3, 4):
            p[(x, y)] = "plinth"
        p[(x, 5)] = "plinth_dk"
    p[(w - 1, 1)] = "plinth_dk"; p[(w - 1, 2)] = "plinth_dk"; p[(w - 1, 3)] = "plinth_dk"; p[(w - 1, 4)] = "plinth_dk"
    return p


# ---- the house ----------------------------------------------------------------------------------------------

BASE = H                 # row under the house (pavement's back edge)
PLINTH = 12
COURSE_Y = 12            # string course rows 12..17, ground storey wall from 18 down to the plinth
DOOR_X, DOOR_W, DOOR_H = 36, 46, 100
WIN_X, WIN_W, WIN_H = 124, 52, 76


def part_lantern():
    """Small iron wall lantern on a bracket (the lamp post's iron and glass)."""
    rows = [
        "...kkkkkkk...",
        "...kiiiiik...",
        "...kkkkkkk...",
        "......k......",
        "......k......",
        ".....kkk.....",
        "....kkkkk....",
        "..kkkkkkkkk..",
        "...kiiiiik...",
        "...klggggk...",
        "...klggggk...",
        "...klggggk...",
        "...klggggk...",
        "...klggggk...",
        "...klggggk...",
        "...klggggk...",
        "...klggggk...",
        "...kiiiiik...",
        "....kkkkk....",
        ".....kkk.....",
        "......k......",
    ]
    m = {"k": "iron_dk", "i": "iron", "g": "glass_hi", "l": "trim_in"}
    p = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in m:
                p[(x, y)] = m[ch]
    return p


def part_downpipe(h):
    p = {}
    for y in range(h):
        p[(0, y)] = "iron"; p[(1, y)] = "iron"; p[(2, y)] = "iron_dk"
    for y in range(20, h - 4, 44):              # brackets
        for x in range(-1, 4):
            p[(x, y)] = "iron_dk"
    return p


def part_vent(w=20, h=6):
    p = {}
    for y in range(h):
        for x in range(w):
            p[(x, y)] = "plinth_dk"
    for x in range(1, w - 1, 3):                # iron bars
        for y in range(h):
            p[(x, y)] = "iron"
    for x in range(w):
        p[(x, h - 1)] = "plinth_cap"            # lit lower lip
    return p


def build():
    wall, course, trim, glass, door, shade, iron = (Layer(n) for n in
        ("wall", "string course", "windows", "fanlight", "door", "shadows", "ironwork"))
    G = H - PLINTH                               # first plinth row (162)
    OPEN_TOP = G - DOOR_H - 16                   # top of the door opening, fanlight included (46)
    # wall: one flat fill, a lit left edge, a shaded right edge, the plinth
    wall.rect(0, 0, W, H, "wall")
    wall.rect(0, 0, 1, G, "stone")
    wall.rect(W - 1, 0, 1, G, "wall_shade")
    wall.rect(0, G, W, 1, "plinth_cap")
    wall.rect(0, G + 1, W, PLINTH - 2, "plinth")
    wall.rect(0, H - 1, W, 1, "plinth_dk")
    wall.rect(W - 1, G + 1, 1, PLINTH - 2, "plinth_dk")
    # string course between the ground and the first floor, and its shadow (the one shade band)
    course.rect(0, COURSE_Y, W, 1, "trim_hi")
    course.rect(0, COURSE_Y + 1, W, 3, "trim")
    course.rect(0, COURSE_Y + 4, W, 1, "trim_sh")
    course.rect(0, COURSE_Y + 5, W, 1, "trim_in")
    shade.rect(0, COURSE_Y + 6, W, 2, "wall_shade")
    # ground floor window: top level with the door opening's top, lintel above, sill below
    trim.stamp(part_lintel(WIN_W + 6), WIN_X - 3, OPEN_TOP - 4)
    trim.stamp(part_window(WIN_W, WIN_H), WIN_X, OPEN_TOP)
    trim.stamp(part_sill(WIN_W + 6), WIN_X - 3, OPEN_TOP + WIN_H)
    # first floor: the same window and sill over each bay, cut by the top of the screen
    for bx in (DOOR_X - 3, WIN_X):
        fy = COURSE_Y - 4 - WIN_H
        trim.stamp(part_window(WIN_W, WIN_H), bx, fy)
        trim.stamp(part_sill(WIN_W + 6), bx - 3, fy + WIN_H)
    # door: stone surround (5 px jambs, 6 px lintel), fanlight, two leaves, a threshold stone in the plinth
    sx, sw = DOOR_X - 5, DOOR_W + 10
    door.stamp(part_surround(sw, G - (OPEN_TOP - 6)), sx, OPEN_TOP - 6)
    glass.stamp(part_fanlight(DOOR_W, 16), DOOR_X, OPEN_TOP)
    leaf = part_door_leaf(DOOR_W // 2, DOOR_H)
    door.stamp(leaf, DOOR_X, G - DOOR_H)
    door.stamp(leaf, DOOR_X + DOOR_W // 2, G - DOOR_H)
    for y in range(G + 1, H - 1):                # joints either side of the threshold stone
        door.put(sx - 1, y, "plinth_dk"); door.put(sx + sw, y, "plinth_dk")
    door.rect(sx, G, sw, 1, "trim_hi")
    # ironwork: a downpipe at the right edge, a lantern beside the door, a cellar vent under the window
    iron.stamp(part_downpipe(G), W - 9, 0)
    iron.stamp(part_lantern(), DOOR_X + DOOR_W + 12, OPEN_TOP - 2)
    iron.stamp(part_vent(), WIN_X + (WIN_W - 20) // 2, G + 3)
    return [wall, shade, course, trim, glass, door, iron]


def flatten(layers):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for l in layers:
        out.alpha_composite(l.image())
    return out


def parts_sheet(path):
    parts = [part_window(), part_sill(58), part_lintel(58), part_door_leaf(), part_fanlight(), part_lantern(),
             part_vent()]
    sheet = Image.new("RGBA", (420, 110), (255, 0, 255, 255))
    x = 2
    for p in parts:
        w = max(k[0] for k in p) + 1
        h = max(k[1] for k in p) + 1
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for (px, py), c in p.items():
            im.putpixel((px, py), RGB[c] + (255,))
        sheet.alpha_composite(im, (x, 2))
        x += w + 6
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(path)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    layers = build()
    for i, l in enumerate(layers):
        l.image().save(os.path.join(out, f"layer_{i}_{l.name.replace(' ', '_')}.png"))
    flatten(layers).save(os.path.join(out, "gable_front.png"))
    with open(os.path.join(out, "palette.txt"), "w") as f:
        f.write("\n".join("#" + v for v in HEX.values()) + "\n")
    if "--parts" in sys.argv:
        parts_sheet(os.path.join(out, "parts_8x.png"))
    print("built", W, "x", H, "layers:", [l.name for l in layers])
