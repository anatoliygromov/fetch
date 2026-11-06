#!/usr/bin/env python3
"""tools/build_dt_built.py: the tall Downtown's backdrop and street pieces redrawn on the board's call (25 Oct), BUILT
from parts drawn once and stamped on integer grids (art/dt-built-06nov, 6 Nov 2026; tier C; BIBLE 3: true scale, the
crispness bar; no resampling, binary alpha, 0 credits). The look is the Downtown sample screen's (5 Nov):
tools/build_tall_fronts.py and tools/build_dt_street.py, whose parts this script reuses where a piece is at their scale.

  town_facades.png    mid row (scroll 0.5), 23 px a metre: the old town houses across the square at their layer's
                      true scale (layer plan decision 2c): a ground floor of 3.3 m (76 px), a first floor of 3.0 m
                      (70 px), then a gable or a roof. One window (1.0 x 1.5 m, 22 x 34) drawn once and stamped on
                      every storey of every house; one door; one shop window; one attic window; one dormer. Seven
                      houses in four plasters, 548 px, repeating. Decoration: no outline, edges a darker shade.
  town_roofs.png      far shore layer (scroll 0.25), 13 px a metre: the roofscape behind the row, tiled and copper
                      roofs with their top storey, dormers stamped, chimneys, two church towers (a copper spire, a
                      lantern). Repeats; faded 70 % by the game.
  town_door.png       back, 46 px a metre: the start, Pepper's home: a house front at the level's left end with a
                      round-arched oak door 2.1 m tall (97 px) in a stone surround with a fanlight, a ground-floor
                      window with a flower box, and the street's upper storeys (build_tall_fronts.upper_window, the
                      same pixels as every front). 120 x 432, its top never on screen (layer plan decision 2b).
  town_tramshed96.png back, decoration: the courtyard gate of screen 10 (the GATE 3072-3168) at true scale: the
                      sample screen's gateway (build_dt_street.gateway, 3 m) in a stretch of plastered courtyard wall
                      3.5 m high (plastered, the street's ochre) with a stone coping, 160 x 161, standing on the back line, centred on the box.
  town_gatestep96.png play, outlined: the GATE's solid perch (96 x 36): the gateway's granite doorstep, two coursed
                      blocks, 98 x 37 at the box's x0 - 1, y0 - 1.
  town_house3.png     back, decoration: the plaza house at its slot (52 x 118), built like the two fixed plaza
                      houses (their window, door, plaster ramps): a yellow stepped gable, no outline.
  town_bollard.png    front layer (scroll 1.3), about 60 px a metre: a cast-iron bollard 0.9 m (54 px) tall, 16
                      wide, dark with a rim of light on its cap; only its top rows show (arthooks: y 461 and down).

  python3 -I tools/build_dt_built.py             write them all (riverwalk/art/scene/)
  python3 -I tools/build_dt_built.py --check     fail if a file on disk differs from the build
  python3 -I tools/build_dt_built.py --sheet P   all pieces at 4x on one sheet
"""
import os, sys, argparse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_tall_fronts as BTF          # noqa: E402  (the street's fronts: upper storeys, window, cornice)
import build_dt_street as BDS            # noqa: E402  (the sample screen's gateway and its colours)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("DT_OUT") or os.path.join(ROOT, "riverwalk", "art", "scene")


class Cv:
    """a canvas of colour keys ('' = transparent); keys map to RGB in a per-piece table"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.full((h, w), "", dtype="<U4")

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c):                                   # inclusive
        if x1 < x0 or y1 < y0 or x1 < 0 or y1 < 0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = c

    def stamp(self, part, x, y):
        for dy in range(part.shape[0]):
            for dx in range(part.shape[1]):
                if part[dy, dx]: self.put(x + dx, y + dy, part[dy, dx])

    def png(self, pal):
        im = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y, x]: im[y, x] = (*pal[self.a[y, x]], 255)
        return im


def part(rows, key):
    """a small part from rows of characters (key: char -> colour key, '.' transparent)"""
    a = np.full((len(rows), len(rows[0])), "", dtype="<U4")
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".": a[y, x] = key[ch]
    return a


# =================================================================================================================
# 1  the old town row (mid, 23 px a metre)
# =================================================================================================================
# 14 colours (the mid layer's limit): four plasters with their shade, stone lit and dark, glass, two roof tiles
MID = dict(
    yw=(225, 184, 127), ys=(196, 156, 102),          # yellow plaster, its shade
    rw=(180, 99, 76), rs=(152, 80, 62),              # red
    cw=(226, 214, 189), cs=(198, 184, 158),          # cream
    ow=(200, 148, 106), os=(172, 122, 84),           # ochre
    sl=(232, 224, 208), sv=(138, 128, 121),          # stone: lit (cornices, surrounds, frames), dark (lips, joints)
    g=(118, 128, 146),                               # glass
    tl=(150, 96, 76), td=(116, 70, 56),              # roof tile, its shade (also the doors' oak)
)
FLOOR0, FLOOR1, CORN = 76, 70, 4                     # ground floor (3.3 m), first floor (3.0 m), cornice rows
EAVES = FLOOR0 + FLOOR1                              # 146 rows from the bottom to the eaves

# parts, drawn once ----------------------------------------------------------------------------------------------
# the window: 1.0 x 1.5 m, a stone frame with 3 x 3 panes and 1 px bars, a hood (lit, lip) over it, a sill (lit,
# lip) under it; its 1 px cast shadow on the wall to the right is stamped with it ('s' = the house's shade)
def _win(cols, rows, pw, ph, hood=True):
    """a window part: `cols` x `rows` panes of pw x ph glass with 1 px stone bars and frame; a hood (lit, lip) over
    it and a sill (lit, lip) under it; 's' marks its 1 px cast shadow on the wall to the right"""
    fw = cols * (pw + 1) + 1; fh = rows * (ph + 1) + 1
    out = []
    if hood: out += ["L" * (fw + 2) + ".", "V" * (fw + 2) + "s"]
    for y in range(fh):
        line = "".join("L" if (x % (pw + 1) == 0 or y % (ph + 1) == 0) else "g" for x in range(fw))
        out.append("." + line + ".s" if hood else line + "s")
    if hood: out += ["L" * (fw + 2) + "s", "V" * (fw + 2) + "s"]
    else: out += ["V" * fw + "s"]
    return part(out, {"L": "sl", "V": "sv", "g": "g", "s": "S"})


WIN = _win(3, 3, 6, 10)                            # 1.0 x 1.5 m: 22 x 34 glass and bars, 25 x 38 with hood and sill
ATTIC = _win(2, 2, 6, 9, hood=False)               # 0.6 x 0.9 m: 15 x 21


def door_part():
    """the door: 1.0 x 2.1 m (23 x 48) of oak, two leaves with raised panels, a 2-row transom of glass, in a stone
    surround 2 px with a lit top and left and a dark right edge"""
    w, h = 27, 52
    a = np.full((h, w), "", dtype="<U4")
    a[:, :] = "sl"
    a[:, w - 1] = "sv"; a[0, :] = "sl"
    a[2:5, 2:w - 2] = "g"; a[5, 2:w - 2] = "sl"                   # the transom over the leaves
    a[6:h, 2:w - 2] = "tl"
    a[6:h, 2] = "td"; a[6, 2:w - 2] = "td"                         # the reveal's shadow, top and left
    a[6:h, w // 2] = "td"                                          # the meeting stiles
    for x0 in (4, w // 2 + 2):                                     # raised panels: dark lower and right edge
        for y0, y1 in ((9, 26), (30, h - 4)):
            a[y1, x0:x0 + 8] = "td"; a[y0:y1 + 1, x0 + 8] = "td"
    return a


def shop_part():
    """a shop window: 2.0 x 1.7 m glass (46 x 39) in a stone frame, three lights, a stone riser below"""
    w, h = 50, 54
    a = np.full((h, w), "sl", dtype="<U4")
    a[:, w - 1] = "sv"; a[h - 1, :] = "sv"
    for i in range(3):
        x0 = 2 + i * 16
        a[3:42, x0:x0 + 14] = "g"
    a[44, 1:w - 1] = "sv"                                          # the riser's panel
    a[45:h - 2, 2] = "sv"; a[h - 3, 2:w - 2] = "sv"
    return a


DOOR, SHOP = door_part(), shop_part()


PITCH = 40                                           # the bay: a window (22 + its hood) and a pier, 1.74 m
MARGIN = 9                                           # the house's plain wall either side of its outer bays


def house(nb, hue, roof, ground, gable_h=0):
    """one house of the row: nb bays wide (40 px each, plus 9 px of wall either side), plaster `hue`, its roof kind,
    its ground floor (a part per bay: 'W' window, 'D' door, 'S' shop over two bays, '' plain). The first floor has a
    window on every bay. Returns a canvas whose bottom row is the strip's bottom row."""
    w = nb * PITCH + 2 * MARGIN
    W_, S_ = hue + "w", hue + "s"
    roof_h = {"stepped": gable_h, "bell": gable_h, "pediment": gable_h, "mansard": 40, "tile": 30}[roof]
    H = EAVES + roof_h
    cv = Cv(w, H)
    top = H - EAVES                                                # the eaves cornice's top row
    bx = [MARGIN + PITCH // 2 + i * PITCH for i in range(nb)]      # bay centres
    cv.rect(0, top, w - 1, H - 1, W_)
    cv.rect(w - 2, top, w - 1, H - 1, S_)                          # the house's right edge, in shade
    b = H - 1
    cv.rect(0, b - 3, w - 1, b, "sv"); cv.rect(0, b - 3, w - 1, b - 3, "sl")         # the plinth (4 rows)
    for y in (H - FLOOR0, top):                                    # cornices: lit top, stone, dark lip, shadow
        cv.rect(0, y, w - 1, y + 1, "sl"); cv.rect(0, y + 2, w - 1, y + 2, "sv")
        cv.rect(0, y + 3, w - 1, y + 3, S_)
    for cx in bx:                                                  # the first floor: the window on every bay
        stamp_key(cv, WIN, cx - 12, top + 16, S_)
    i = 0
    while i < nb:                                                  # the ground floor
        k = ground[i]
        if k == "W": stamp_key(cv, WIN, bx[i] - 12, H - FLOOR0 + 12, S_)
        elif k == "D": stamp_key(cv, DOOR, bx[i] - DOOR.shape[1] // 2, b - 3 - DOOR.shape[0], S_)
        elif k == "S":
            cx = (bx[i] + bx[i + 1]) // 2 if i + 1 < nb else bx[i]
            stamp_key(cv, SHOP, cx - SHOP.shape[1] // 2, b - 3 - SHOP.shape[0], S_); i += 1
        i += 1
    if roof in ("mansard", "tile"):
        ry1 = top - 1
        for y in range(roof_h):                                    # the roof's face, front-on
            yy = ry1 - y
            inset = y // 3 if roof == "mansard" else y
            if roof == "tile" and y >= roof_h - 2: break
            x0, x1 = inset, w - 1 - inset
            if x1 - x0 < 8: break
            course = (y % 6 == 5)
            cv.rect(x0, yy, x1, yy, "td" if course else "tl")
            cv.rect(x1 - 1, yy, x1, yy, "td")
        cv.rect(0, ry1, w - 1, ry1, "sv")                          # the gutter's shadow line
        if roof == "mansard":
            for cx in bx: dormer(cv, cx, ry1 - 4, S_, W_)          # a dormer over every window
        else:
            chimney(cv, int(w * 0.7), ry1 - 2)
    else:
        gable(cv, roof, top, w, W_, S_, gable_h, bx)
    return cv


def stamp_key(cv, p, x, y, shade):
    for dy in range(p.shape[0]):
        for dx in range(p.shape[1]):
            k = p[dy, dx]
            if k: cv.put(x + dx, y + dy, shade if k == "S" else k)


def dormer(cv, cx, base, S_, W_):
    """a dormer on a roof: plaster cheeks round the attic window, a little pitched tile cap"""
    x0 = cx - 10
    cv.rect(x0, base - 25, x0 + 19, base, W_); cv.rect(x0 + 18, base - 25, x0 + 19, base, S_)
    stamp_key(cv, ATTIC, x0 + 2, base - 22, S_)
    for k in range(6):                                             # the cap: a little pitched roof, lit, its edge dark
        cv.rect(x0 - 2 + k * 2, base - 26 - k, x0 + 21 - k * 2, base - 26 - k, "tl")
        cv.rect(x0 + 20 - k * 2, base - 26 - k, x0 + 21 - k * 2, base - 26 - k, "td")


def chimney(cv, x, base):
    """a chimney on a roof: plaster, a stone cap"""
    for y in range(base, -1, -1):
        if cv.a[y, x] == "": base = y; break
    cv.rect(x, base - 12, x + 7, base + 6, "rw"); cv.rect(x + 6, base - 12, x + 7, base + 6, "rs")
    cv.rect(x - 1, base - 14, x + 8, base - 13, "sl"); cv.rect(x - 1, base - 12, x + 8, base - 12, "sv")


def gable(cv, kind, top, w, W_, S_, gh, bx):
    """a front gable over the eaves cornice, by its profile (half widths row by row from the foot): stepped (steps
    12 wide and 12 high), bell (quarter-round shoulders and a cap), pediment (a triangle). Filled with plaster, its
    right 2 px in shade; every column's top pixel is the stone coping (lit), the left edge lit, the right edge dark.
    Attic windows on the bays' centres in the lower gable, one more on the axis higher up."""
    base = top - 1
    prof = []
    for y in range(gh):
        if kind == "stepped":
            half = w / 2 - 12 * (y // 12 + 1) + 12 if y < gh - 12 else 14
            half = max(14, w / 2 - 12 * (y // 12))
        elif kind == "bell":
            sh = gh - 14; cap = 13
            if y < sh: half = cap + (w / 2 - cap) * np.cos((y / sh) * np.pi / 2) ** 0.8
            else: half = cap if y < gh - 3 else cap - 2 * (y - gh + 4)
        else:
            half = (w / 2) * (1 - y / gh)
        prof.append(half)
    for y, half in enumerate(prof):
        yy = base - y
        x0 = int(round(w / 2 - half)); x1 = w - 1 - x0
        if x1 - x0 < 2: continue
        cv.rect(x0, yy, x1, yy, W_); cv.rect(x1 - 1, yy, x1, yy, S_)
    for x in range(w):                                             # the coping: each column's top pixel
        col = np.nonzero(cv.a[:base, x] != "")[0]
        if len(col): cv.put(x, col[0], "sl"); cv.put(x, col[0] + 1, "sl" if kind != "pediment" else W_)
    for y in range(base - gh, base):                               # the outline's sides: lit left, dark right
        row = np.nonzero(cv.a[y] != "")[0]
        if len(row): cv.put(row[0], y, "sl"); cv.put(row[-1], y, "sv")
    if kind == "pediment":                                         # its raking cornice under the coping
        for x in range(w):
            col = np.nonzero(cv.a[:base, x] != "")[0]
            if len(col) > 3: cv.put(x, col[0] + 2, "sv")
    nrow = 1 if gh < 50 else 2
    for cx in bx: stamp_key(cv, ATTIC, cx - 7, base - 27, S_) if gh >= 34 else None
    if nrow == 2: stamp_key(cv, ATTIC, w // 2 - 7, base - 55, S_)


ROW = [  # bays, plaster, roof, gable height, ground floor per bay
    (3, "y", "bell", 64, "DWW"),
    (2, "r", "stepped", 60, "SS"),
    (3, "c", "mansard", 0, "WDW"),
    (2, "o", "stepped", 48, "DW"),
    (3, "y", "pediment", 40, "WSS"),
    (2, "r", "tile", 0, "WD"),
    (2, "c", "bell", 56, "SS"),
]


def facades():
    houses = [house(nb, hue, roof, ground, gh) for nb, hue, roof, gh, ground in ROW]
    H = max(h.h for h in houses)
    W = sum(h.w for h in houses)
    cv = Cv(W, H); x = 0
    for h in houses:
        cv.stamp(h.a, x, H - h.h); x += h.w
    return cv


# =================================================================================================================
# 2  the far roofs (shore, 13 px a metre)
# =================================================================================================================
FAR = dict(
    pw=(216, 200, 172), ps=(188, 172, 146),          # cream plaster of the top storeys, its shade
    qw=(222, 182, 128), qs=(194, 154, 104),          # yellow plaster, its shade
    tl=(170, 106, 84), td=(138, 82, 66),             # tiled roofs
    kl=(120, 170, 152), kd=(92, 138, 124),           # copper roofs and the spire
    g=(118, 126, 140),                               # windows
    sl=(238, 232, 220), sv=(152, 142, 132),          # stone (cornices, the towers' trim, louvres)
)                                                    # 12 colours: the far layer's limit
FWIN = part(["LLLLLLLL", "LgggLggs", "LgggLggs", "LgggLggs", "LgggLggs", "LgggLggs", "LLLLLLLs", "LgggLggs",
             "LgggLggs", "LgggLggs", "LgggLggs", "LLLLLLLs"], {"L": "sl", "g": "g", "s": "sv"})   # 0.6 x 0.9 m
FDORM = part(["...kk...", "..kkkk..", ".kkkkkkd", "kkkkkkkd", ".LLLLLs.", ".LgggLs.", ".LgggLs.", ".LLLLLs."],
             {"k": "kl", "d": "kd", "L": "sl", "g": "g", "s": "sv"})


def far_block(w, storeys, roof, tile, cream=True):
    """a far house: its top storeys (13 px a metre: 39 px a storey, windows on a 16 px grid) under a steep roof
    seen front-on: 'eaves' (the long side, a dormer every 24 px, a chimney) or 'hip' (a tall hipped roof)"""
    pw, ps = ("pw", "ps") if cream else ("qw", "qs")
    rl, rd = ("tl", "td") if tile else ("kl", "kd")
    st = 39; wall = storeys * st; rh = 34 if roof == "eaves" else 44
    H = wall + rh + 14
    cv = Cv(w, H)
    cv.rect(0, H - wall, w - 1, H - 1, pw); cv.rect(w - 2, H - wall, w - 1, H - 1, ps)
    n = max(1, (w - 8) // 16); x0 = (w - (n * 16 - 8)) // 2
    for s_ in range(storeys):
        y = H - wall + s_ * st + 14
        for i in range(n): cv.stamp(FWIN, x0 + i * 16, y)
        cv.rect(0, H - wall + s_ * st, w - 1, H - wall + s_ * st + 1, "sl")      # cornice / string course
    top = H - wall
    for y in range(rh):
        inset = y if roof == "eaves" else (y * 2) // 3
        xa, xb = inset, w - 1 - inset
        if xb - xa < 6: break
        cv.rect(xa, top - 1 - y, xb, top - 1 - y, rl)
        cv.rect(xb - 1, top - 1 - y, xb, top - 1 - y, rd)
        if y % 7 == 6: cv.rect(xa, top - 1 - y, xb - 2, top - 1 - y, rd)       # tile courses / copper seams
    if roof == "eaves":
        for cx in range(x0 + 4, w - 12, 32): cv.stamp(FDORM, cx, top - 14)
    cx = int(w * 0.62)                                             # a chimney on the roof's right half
    for y in range(rh):
        row = top - 1 - y
        if cv.a[row, cx] == "" or y > rh - 10:
            cv.rect(cx, row - 6, cx + 5, row + 8, pw); cv.rect(cx + 4, row - 6, cx + 5, row + 8, ps)
            cv.rect(cx - 1, row - 7, cx + 6, row - 7, "sl"); break
    return cv


def tower(kind):
    """a church tower: a plaster shaft with louvred belfry openings under a stone cornice, a slim copper spire with a
    ball (Tyska kyrkan) or a copper bell roof with an open lantern (Storkyrkan)"""
    if kind == "spire":
        w, shaft, spire = 26, 150, 104
    else:
        w, shaft, spire = 34, 140, 60
    H = shaft + spire
    cv = Cv(w, H)
    cv.rect(0, spire, w - 1, H - 1, "qw"); cv.rect(w - 3, spire, w - 1, H - 1, "qs")
    for y in (spire + 14, spire + 54):                             # twin belfry openings with louvres
        for x0 in (w // 2 - 8, w // 2 + 3):
            cv.rect(x0, y, x0 + 4, y + 20, "sv")
            for yy in range(y + 2, y + 20, 3): cv.rect(x0 + 1, yy, x0 + 4, yy, "g")
    cv.rect(0, spire, w - 1, spire + 2, "sl"); cv.rect(0, spire + 3, w - 1, spire + 3, "sv")
    cv.rect(0, spire + 44, w - 1, spire + 45, "sl")
    if kind == "spire":
        for y in range(spire - 4):                                 # the spire: a slim copper cone, a ball, a vane rod
            half = 1 + (w / 2 - 1) * ((y) / (spire - 4)) ** 1.25
            x0 = int(round(w / 2 - half)); x1 = w - 1 - x0
            cv.rect(x0, y + 4, x1, y + 4, "kl"); cv.rect(max(x0, w // 2), y + 4, x1, y + 4, "kd")
        cv.rect(w // 2 - 1, 0, w // 2, 6, "kd"); cv.rect(w // 2 - 2, 7, w // 2 + 1, 9, "sl")
    else:
        for y in range(spire):                                     # a bell roof and an open lantern on it
            t = y / spire
            half = 4 if t < 0.45 else (5 + (w / 2 - 5) * ((t - 0.45) / 0.55) ** 1.5)
            x0 = int(round(w / 2 - half)); x1 = w - 1 - x0
            cv.rect(x0, y, x1, y, "kl"); cv.rect(max(x0, w // 2), y, x1, y, "kd")
        cv.rect(w // 2 - 5, 12, w // 2 + 4, 24, "sl"); cv.rect(w // 2 - 3, 14, w // 2 + 2, 22, "g")   # the lantern
        cv.rect(w // 2 - 6, 25, w // 2 + 5, 26, "sv")
        cv.rect(w // 2 - 1, 0, w // 2, 11, "kd")
    return cv


def far_roofs():
    blocks = [(72, 3, "eaves", True, True), (56, 4, "hip", False, False), (88, 3, "eaves", True, False),
              (60, 4, "hip", True, True), (44, 3, "hip", False, True), (80, 3, "eaves", False, False),
              (68, 4, "eaves", True, True), (56, 3, "hip", True, False)]
    W = sum(b[0] for b in blocks)
    parts = [far_block(*b) for b in blocks]
    t1, t2 = tower("spire"), tower("lantern")
    H = max(max(p.h for p in parts), t1.h, t2.h)
    cv = Cv(W, H); x = 0
    for p in parts: cv.stamp(p.a, x, H - p.h); x += p.w
    cv.stamp(t1.a, 122, H - t1.h)                                  # the towers stand among the roofs
    cv.stamp(t2.a, 388, H - t2.h)
    return cv


# =================================================================================================================
# 3  the start door: Pepper's home (back, 46 px a metre), from the street's front parts
# =================================================================================================================
HOME_W = 140
HOME_PLASTER = ((154, 82, 63), (127, 64, 51))        # arthooks H.PLASTER.red (the street's red houses)
FLOWER = dict(P=(205, 70, 84), Q=(232, 196, 92), E=(78, 120, 62), X=(56, 92, 48))   # (one-letter roles: BTF.Canvas)


def home():
    gw = HOME_W
    C = dict(BTF.C); C["W"], C["S"] = HOME_PLASTER
    C.update(FLOWER); C.update(dict(Y=(236, 220, 160)))           # (Y: the fanlight's warm glass, lit inside)
    BTF.H = 240
    cv = BTF.Canvas(gw); BTF.common(cv)
    cx, r, stone = 42, 24, 6                                       # the door: 48 wide, 97 px to the crown (2.1 m)
    ox0, ox1 = cx - r, cx + r - 1
    spring = BTF.PLINTH - 97 + r                                    # the arch's centre row
    crown = spring - r
    hole = np.zeros((240, gw), bool); ring = np.zeros((240, gw), bool)
    for y in range(crown - stone - 1, BTF.PLINTH):
        for x in range(gw):
            if y >= spring:
                if ox0 <= x <= ox1: hole[y, x] = True
                elif ox0 - stone <= x <= ox1 + stone: ring[y, x] = True
                continue
            d = np.hypot(x + 0.5 - cx, y + 0.5 - spring)
            if d < r: hole[y, x] = True
            elif d < r + stone: ring[y, x] = True
    for y, x in zip(*np.nonzero(ring)):                            # the stone surround, lit top-left, joints
        cv.put(x, y, "T")
    for y, x in zip(*np.nonzero(ring)):
        if not ring[y - 1, x] and not hole[y - 1, x]: cv.put(x, y, "L")
        elif not ring[y, x - 1] and not hole[y, x - 1] and x < cx: cv.put(x, y, "L")
        elif not ring[y, x + 1] and not hole[y, x + 1] and x > cx: cv.put(x, y, "V")
    for y in range(spring + 10, BTF.PLINTH, 16):                    # block joints on the jambs
        cv.rect(ox0 - stone + 1, y, ox0 - 1, y, "V"); cv.rect(ox1 + 1, y, ox1 + stone - 1, y, "V")
    for a in range(20, 180, 20):                                    # voussoir joints
        for d in np.arange(r + 0.5, r + stone - 0.5, 0.5):
            xx = int(cx + d * np.cos(np.radians(a))); yy = int(spring - d * np.sin(np.radians(a)))
            if ring[yy, xx] and abs(a - 90) > 10: cv.put(xx, yy, "V")
    cv.rect(cx - 4, crown - stone - 1, cx + 3, crown + 3, "T")      # the keystone
    cv.rect(cx - 4, crown - stone - 1, cx + 3, crown - stone - 1, "L"); cv.rect(cx - 4, crown - stone - 1, cx - 4, crown + 3, "L")
    cv.rect(cx + 3, crown - stone, cx + 3, crown + 3, "V")
    # the fanlight in the arch over the transom bar, radial bars; the leaf below it
    tb = spring + 2
    for y, x in zip(*np.nonzero(hole)):
        cv.put(x, y, "Y" if y < tb else "K")
    for a in (45, 90, 135):
        for d in np.arange(0, r, 0.5):
            xx = int(cx + d * np.cos(np.radians(a))); yy = int(spring - d * np.sin(np.radians(a)))
            if hole[yy, xx] and yy < tb: cv.put(xx, yy, "F")
    cv.rect(ox0, spring, ox1, spring, "F"); cv.rect(ox0, tb - 1, ox1, tb, "F")   # the transom bar
    for y in range(crown, spring):                                  # the fanlight's frame along the arch
        for x in range(ox0, ox1 + 1):
            if hole[y, x] and (not hole[y - 1, x] or not hole[y, x - 1] or not hole[y, x + 1]): cv.put(x, y, "F")
    lx0, lx1 = ox0, ox1
    cv.rect(lx0, tb + 1, lx1, tb + 2, "D")                          # the reveal's shadow under the transom
    cv.rect(lx0, tb + 1, lx0 + 1, BTF.PLINTH - 1, "D")
    for y0, h in ((tb + 6, 26), (tb + 38, 26)):                     # one leaf, 2 x 2 raised panels
        cv.stamp(BTF.panel(18, h), lx0 + 4, y0); cv.stamp(BTF.panel(18, h), lx0 + 25, y0)
    cv.rect(cx + 14, tb + 34, cx + 15, tb + 35, "I")                # the handle
    cv.stamp([".II.", "I..I", "I..I", ".II."], cx - 2, tb + 22)     # a knocker ring
    cv.rect(ox0 - stone, BTF.PLINTH - 1, ox1 + stone, BTF.PLINTH - 1, "L")   # the doorstep's nosing
    # the ground-floor window to the right (the street's upper window, on a sill at 0.9 m) with a flower box
    wx = 104
    BTF.upper_window(cv, wx, BTF.PLINTH - 42 - 74)
    by = BTF.PLINTH - 42 + 8                                        # the flower box under the sill, its blooms over it
    cv.rect(wx - 20, by, wx + 19, by + 8, "K"); cv.rect(wx - 20, by, wx + 19, by, "J"); cv.rect(wx - 20, by + 8, wx + 19, by + 8, "D")
    cv.rect(wx + 18, by + 1, wx + 19, by + 7, "D")
    for i, fx in enumerate(range(wx - 18, wx + 17, 6)):              # geraniums: leaves and blooms on a 6 px grid
        cv.rect(fx, by - 4, fx + 4, by - 1, "E"); cv.rect(fx + 4, by - 3, fx + 4, by - 1, "X")
        cv.rect(fx + 1, by - 7, fx + 3, by - 5, "P" if i % 2 == 0 else "Q"); cv.put(fx + 2, by - 8, "P" if i % 2 == 0 else "Q")
    ground = cv.role[BTF.CORNICE:]
    # (night/06nov-dt, the facade lift) Pepper's home in the street's style a (tools/build_dt_facades.py): pediments
    # over the first floor, hoods over the second, geranium boxes, dentil courses, lace curtains
    import build_dt_facades as BF
    for k in "OU":
        C.setdefault(k, BF.C[k])
    up = BF.upper(gw, [42, 104], dict(BF.STYLES["a"], anchors=False))   # (no room for anchors at its edge)
    role = np.vstack([up, ground])
    role[:, gw - 2:] = np.where(np.isin(role[:, gw - 2:], ["W"]), "S", role[:, gw - 2:])   # its right edge in shade
    im = np.zeros((role.shape[0], gw, 4), np.uint8)
    for y in range(role.shape[0]):
        for x in range(gw):
            im[y, x] = (*C[role[y, x]], 255)
    return im


# =================================================================================================================
# 4  the courtyard gate of screen 10 and its doorstep
# =================================================================================================================
GATE = dict(BDS.C)
GATE.update(br=(137, 101, 66), bs=(114, 81, 53),                     # the wall's plaster: arthooks H.PLASTER.ochre
            cy=(198, 184, 146))                                         # the courtyard's sunlit cobbles


def courtyard_gate():
    """the sample screen's gateway (80 x 138, 3 m) in a plastered courtyard wall 3.5 m high (161 px) with a stone coping,
    160 wide; the passage's floor is the doorstep's top (the gateway's bottom 23 rows stand behind the step)"""
    W, H = 160, 161
    cv = Cv(W, H)
    gw = BDS.gateway()
    cv.rect(0, 10, W - 1, H - 1, "br")
    cv.rect(W - 3, 10, W - 1, H - 1, "bs")                         # the wall's right end in shade
    cv.rect(0, 0, W - 1, 9, "")                                    # the coping: lit top, stone, dark lip
    cv.rect(0, 4, W - 1, 4, "tl"); cv.rect(0, 5, W - 1, 7, "tm"); cv.rect(0, 8, W - 1, 8, "tv"); cv.rect(0, 9, W - 1, 9, "bs")
    cv.rect(0, 10, W - 1, 12, "br")
    gx = (W - gw.w) // 2
    cv.rect(0, 0, gx - 5, 9, "")                                   # the wall's coping steps up over the gateway:
    cv.rect(gx + gw.w + 4, 0, W - 1, 9, "")                        # the sides' coping 10 rows lower
    for x0, x1 in ((0, gx - 5), (gx + gw.w + 4, W - 1)):
        cv.rect(x0, 10, x1, 19, "br")
        cv.rect(x0, 10, x1, 10, "tl"); cv.rect(x0, 11, x1, 13, "tm"); cv.rect(x0, 14, x1, 14, "tv"); cv.rect(x0, 15, x1, 15, "bs")
    cv.rect(gx - 4, 4, gx - 4, H - 1, "tl"); cv.rect(gx + gw.w + 3, 4, gx + gw.w + 3, H - 1, "bs")   # the gate's bay edges
    cv.stamp(gw.a, gx, H - gw.h)
    # (review round 1, 6 Nov: the gateway's courtyard wall with a window, seen over the doorstep, read as a hut in the
    # arch) the passage is redrawn as a dark way through: the vault darkest at the top and on the left reveal, and at
    # its far end a smaller arch of daylight, the sunny courtyard: a lit wall, a green bush, its cobbles
    hole = np.isin(cv.a, ["pd", "pdd", "pf", "cw", "pc", "og", "ol", "cg", "cgd"])
    hole[:, :gx] = False; hole[:, gx + gw.w:] = False
    cv.a[hole] = "pd"
    for y in range(H):                                             # the vault's shade: 3 rows under the arch, the
        for x in range(W):                                         # left reveal 3 columns
            if hole[y, x] and (not hole[y - 3, x] or not hole[y, x - 3]): cv.put(x, y, "pdd")
    cx, r = W // 2, 13                                             # the far arch: 26 wide, spring 58 rows over the foot
    spring = H - 58
    for y in range(spring - r, H):
        for x in range(cx - r, cx + r):
            inside = y >= spring or np.hypot(x + 0.5 - cx, y + 0.5 - spring) < r
            if not inside: continue
            k = "cw"                                               # the courtyard's sunny far wall
            if y >= H - 44: k = "cg"                               # a bush across it
            if y >= H - 30: k = "cy"                               # the sunlit cobbles
            cv.put(x, y, k)
    for x in range(cx - r, cx + r, 8):                             # the bush's round tops on an 8 px grid
        for dy, (a, b) in enumerate(((2, 5), (1, 6), (0, 7), (0, 7))):
            for dx in range(a, b + 1):
                if x + dx < cx + r: cv.put(x + dx, H - 47 + dy, "cg")
    cv.rect(cx - r, H - 31, cx + r - 1, H - 31, "cgd")             # the bush's shade on the cobbles
    for y in range(spring - r - 1, H):                             # the far arch's own dark reveal, 1 px
        for x in range(cx - r - 1, cx + r + 1):
            if cv.a[y, x] == "pd" and any(cv.a[y + dy, x + dx] in ("cw", "cg", "cy", "cgd") for dx, dy in ((1, 0), (-1, 0), (0, 1)) if 0 <= y + dy < H):
                cv.put(x, y, "pdd")
    return cv


def gate_step():
    """the GATE's perch (96 x 36, solid): the gateway's granite doorstep, two courses of 17 px, blocks 24 px on a
    staggered bond, lit tops and left edges; one dark outline: 98 x 37 at x0 - 1, y0 - 1 (its bottom on the street)"""
    W, H = 98, 37
    cv = Cv(W, H)
    cv.rect(0, 0, W - 1, H - 1, "ink")
    for r in range(2):
        y0 = 1 + r * 18; y1 = y0 + 16
        cv.rect(1, y0, W - 2, y1, "tm")
        cv.rect(1, y0, W - 2, y0, "tl")
        cv.rect(1, y1, W - 2, y1, "tv")
        off = 12 if r else 0
        for x in range(1 + 24 - off if off else 25, W - 2, 24):     # block joints, lit edge right of each
            cv.rect(x, y0 + 1, x, y1, "tv"); cv.rect(x + 1, y0 + 1, x + 1, y1 - 1, "tl")
        if r == 0: cv.rect(1, y1 + 1, W - 2, y1 + 1, "ink")          # the bed joint between the courses
    cv.rect(1, 1, 1, H - 2, "tl")
    return cv


# =================================================================================================================
# 5  the plaza house 3 (back, its slot 52 x 118), in the fixed plaza houses' parts and ramps
# =================================================================================================================
H3V = 0.66                                           # (the value of house 1 after its fix: the sample screen's back)
H3 = {k: tuple(int(round(c * H3V)) for c in v) for k, v in dict(   # house 3's own ramps (its 22 Oct file), house 1's glass
    w=(219, 164, 88), s=(192, 137, 81),              # yellow plaster, its shade
    l=(236, 239, 224), v=(178, 185, 164),            # white trim (cornices, frames, copings), the window lining
    g=(58, 62, 74),                                  # glass (house 1 after its contrast fix)
    d=(145, 76, 54), dd=(61, 41, 36),                # the door's paint, its panels and reveal
    p=(129, 133, 121), pd=(92, 88, 86),              # the plinth, its joints
).items()}
# the plaza houses' window, exactly house 1's (rows 39-56): a white frame, a grey lining, 2 x 2 panes of glass with a
# white cross bar, a sill one px wider each side with dark ends
H3WIN = part([".iiiiiiiiiii.",
              ".ibbbbbbbbbi.",
              ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.",
              ".ibiiiiiiibi.",
              ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.", ".ibhhhihhhbi.",
              ".iiiiiiiiiii.",
              "sbbbbbbbbbbbs"], {"i": "l", "b": "v", "h": "g", "s": "s"})
H3ATTIC = part(["iiiiiiiii", "ihhhihhhi", "ihhhihhhi", "ihhhihhhi", "ihhhihhhi", "iiiiiiiii", "ihhhihhhi", "ihhhihhhi",
                "ihhhihhhi", "ihhhihhhi", "iiiiiiiii", "sssssssss"], {"i": "l", "h": "g", "s": "s"})


def house3():
    """52 x 118, house 1's storeys and window: a ground floor (door between two windows) and two upper storeys of three
    windows on a 15 px pitch and a 24 px storey (the same rows as house 1), white cornices with a row of shade under
    them, a stepped gable of 4 steps (6 in, 8 up) with white copings and an attic window, the right 2 columns in shade;
    no outline: the edges are the plaster's shade"""
    W, H = 52, 118
    cv = Cv(W, H)
    eaves = 34
    cv.rect(0, eaves, W - 1, H - 1, "w")
    for i in range(4):                                             # the steps
        x0 = i * 6; y1 = eaves - 1 - i * 8
        cv.rect(x0, y1 - 7, W - 1 - x0, y1, "w")
        cv.rect(x0, y1 - 7, x0 + 5, y1 - 7, "l"); cv.rect(W - 6 - x0, y1 - 7, W - 1 - x0, y1 - 7, "l")
        cv.rect(x0, y1 - 6, x0, y1, "l")
    cv.rect(24, 0, 27, 1, "l")                                     # a finial on the top step
    cv.rect(W - 2, eaves, W - 1, H - 1, "s")
    for i in range(4):                                             # the steps' right risers in shade
        x0 = i * 6; y1 = eaves - 1 - i * 8
        cv.rect(W - 2 - x0, y1 - 6, W - 1 - x0, y1, "s")
    cv.stamp(H3ATTIC, 21, 11)
    for y in (eaves, 84):                                          # cornices: white, a shade row under
        cv.rect(0, y, W - 1, y, "l"); cv.rect(0, y + 1, W - 1, y + 1, "l"); cv.rect(0, y + 2, W - 1, y + 2, "s")
    for y0 in (40, 63):                                            # the upper storeys: 3 windows, pitch 15
        for x0 in (4, 19, 34): cv.stamp(H3WIN, x0 - 1, y0)
    for x0 in (4, 34): cv.stamp(H3WIN, x0 - 1, 91)                 # the ground floor's two windows
    dx0, dx1, dy0 = 19, 30, 92                                     # the door: white surround, two leaves, a fanlight
    cv.rect(dx0 - 1, dy0 - 3, dx1 + 1, H - 5, "l")
    cv.rect(dx0, dy0, dx1, dy0 + 3, "v"); cv.rect(dx0, dy0 + 4, dx1, dy0 + 4, "l")   # (the fanlight in the lining's grey)
    cv.rect(dx0, dy0 + 5, dx1, H - 5, "d")
    cv.rect(dx0, dy0 + 5, dx0, H - 5, "dd"); cv.rect(dx0 + 5, dy0 + 5, dx0 + 6, H - 5, "dd")
    for px in (dx0 + 2, dx0 + 8):
        cv.rect(px, dy0 + 7, px + 2, dy0 + 12, "dd"); cv.rect(px, dy0 + 14, px + 2, dy0 + 19, "dd")   # equal panels
    cv.rect(0, H - 4, W - 1, H - 1, "p"); cv.rect(0, H - 4, W - 1, H - 4, "l")   # the plinth and the step
    cv.rect(dx0 - 3, H - 5, dx1 + 3, H - 5, "l")
    cv.rect(W - 2, H - 4, W - 1, H - 1, "pd")
    return cv


# =================================================================================================================
# 6  the bollard (front, about 60 px a metre)
# =================================================================================================================
BOL = dict(k=(20, 24, 32), m=(32, 38, 50), r=(62, 74, 94), w=(44, 50, 60))


def bollard():
    """a cast-iron bollard, 0.9 m (54 px) x 0.26 m (16 px): a domed cap with a rim of sky light on its upper left,
    a collar ring, the shaft with one darker band; its 19 top rows are what shows (the rest is under the screen)"""
    W, H = 16, 54
    cv = Cv(W, H)
    prof = [6, 9, 11, 12, 13, 14, 14, 14]                          # the dome's width, row by row
    for y, w in enumerate(prof):
        x0 = (W - w) // 2
        cv.rect(x0, y, x0 + w - 1, y, "m")
        cv.put(x0, y, "r"); cv.put(x0 + 1, y, "r") if y < 3 else None
    cv.rect(5, 0, 8, 0, "r")
    cv.rect(0, 8, W - 1, 11, "m"); cv.rect(0, 8, W - 1, 8, "r"); cv.rect(0, 11, W - 1, 11, "k")   # the collar
    cv.rect(2, 12, W - 3, H - 1, "m")                              # the shaft
    cv.rect(2, 12, 3, H - 1, "w")                                  # its lit left side
    cv.rect(W - 5, 12, W - 3, H - 1, "k")                          # its shaded right side
    cv.rect(2, 12, W - 3, 12, "k")                                 # the collar's shadow
    return cv


# =================================================================================================================
def build():
    return {
        "town_facades": facades().png(MID),
        "town_roofs": far_roofs().png(FAR),
        "town_door": home(),
        "town_tramshed96": courtyard_gate().png(GATE),
        "town_gatestep96": gate_step().png(GATE),
        "town_house3": house3().png(H3),
        "town_bollard": bollard().png(BOL),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    ap.add_argument("--only", nargs="*")
    o = ap.parse_args()
    bad = 0; ims = build()
    for n, im in ims.items():
        if o.only and n not in o.only: continue
        p = os.path.join(OUT, n + ".png")
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(p, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{p} {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z = 4; W = sum(i.shape[1] * z + 20 for i in ims.values()) + 20; H = max(i.shape[0] for i in ims.values()) * z + 40
        sh = Image.new("RGBA", (W, H), (120, 140, 166, 255)); x = 20
        for im in ims.values():
            sh.alpha_composite(Image.fromarray(im).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST), (x, H - 20 - im.shape[0] * z)); x += im.shape[1] * z + 20
        sh.save(o.sheet)
    sys.exit(1 if bad else 0)
