"""tools/build_night_kit.py: Night Harbour's built parts (8 Nov 2026, phase 1, 0 credits).

Every part is BUILT on an integer grid from the level's one palette table (riverwalk/levelart/night/palette.lua):
each repeated piece (board, window, crate, block, pile, shed, boat) is drawn once and stamped, flat fills with at
most one shade band, a 1 px ink outline on what Pepper uses, none on decoration (its edge a darker shade of its own
colour). No resampling: the two recoloured River Walk files (water.png, lamp_post.png) are mapped colour by colour,
whole pixel, never scaled. No dithering.

    python3 -I tools/build_night_kit.py            writes riverwalk/levelart/night/*.png
    python3 -I tools/build_night_kit.py --sheet X  also a 4x contact sheet of every part

Parts (file: size, layer, what):
  crate_cell.png      16 x 16  play   a fish crate, ink on its top and left (stacks stamp it, then close the outline)
  crate_back.png      16 x 16  back   the same crate for the back stack (no ink, a shade lighter)
  rope.png            24 x 8   back   a coiled rope on the back stack
  tarp.png            88 x 24  back   a rowboat drawn up on two chocks, a tarp over it (the fox's first hideout)
  fishshed.png        96 x 80  back   the fish shed: tarred boards, loading doors, a dark window, roof edge
  house.png          144 x 176 back   Mia's house: Falu red boards, white trim, gable, lit windows, green door
  post.png            16 x 64  play   the mooring pile in the water (timber, iron band, wet band)
  lamp_night.png      14 x 101 back   lamp_post.png recoloured whole-pixel to dark iron, warm glass
  lantern.png          7 x 10  back   a harbour lantern's head (cap, warm glass, frame)
  rowboat.png         60 x 14  play   the rowboat's hull (56 px deck, sheer up at bow and stern)
  boat.png            52 x 14  play   the small boat's hull (48 px deck), white paint
  water_near.png     320 x 68  play   water.png rows 26-93 recoloured (the water in the quay's gaps, y 172-239)
  shore.png         1568 x 132 shore  the far side of the bay at 0.3: boat sheds on a pier, moored boats, masts,
                                       their lights and reflections, the bay (water.png rows 0-25 recoloured)
  far_town.png       448 x 110 city   the old town on the far shore: gables, a spire, lit windows (0.03, capped)
  frontpile.png       12 x 19  front  a mooring pile's top in the foreground: a dark silhouette, its rim
"""
import os, re, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "riverwalk", "levelart", "night")
SCENE = os.path.join(ROOT, "riverwalk", "art", "scene")


def palette():
    src = open(os.path.join(OUT, "palette.lua")).read()
    pal = {}
    for k, v in re.findall(r'(\w+)\s*=\s*"([0-9a-fA-F]{6})"', src):
        pal[k] = (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16), 255)
    return pal


P = palette()


class Canvas:
    """a grid of palette names (None = transparent)"""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [[None] * w for _ in range(h)]

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def stamp(self, other, x, y):
        for yy in range(other.h):
            for xx in range(other.w):
                c = other.g[yy][xx]
                if c is not None:
                    self.px(x + xx, y + yy, c)

    def outline(self, c="ink"):
        """a 1 px outline on the silhouette's own edge pixels (inside the art)"""
        edge = []
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x] is None:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.get(x + dx, y + dy) is None:
                        edge.append((x, y)); break
        for x, y in edge:
            self.g[y][x] = c

    def image(self):
        a = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                c = self.g[y][x]
                if c is not None:
                    a[y, x] = P[c] if isinstance(c, str) else c
        return Image.fromarray(a, "RGBA")


def save(cv, name, parts):
    im = cv.image()
    im.save(os.path.join(OUT, name))
    parts.append((name, im))


# ---------------------------------------------------------------------------------------------------------- crates
def crate(back=False):
    """a 16 x 16 fish crate seen front-on: three boards, corner posts, a hand hole; the light from upper left.
    play: ink on its top row and left column (a stack stamps these on a 16 px grid and closes its right and bottom
    with one ink line, so two crates share one ink seam). back: no ink, its seams a darker shade of its wood."""
    c = Canvas(16, 16)
    lit, base, shade, seam = ("wd1", "wd2", "wd3", "wd4") if not back else ("wd2", "wd3", "wd3", "wd4")
    edge = "ink" if not back else "wd5"
    c.rect(0, 0, 16, 16, base)
    for y, h, col in ((1, 4, base), (6, 4, base), (11, 5, shade)):      # three boards, the lowest in shade
        c.rect(1, y, 15, h, col)
        c.rect(1, y, 15, 1, lit if y == 1 else (base if not back else "wd3"))
    c.rect(1, 1, 15, 1, lit)                                            # the top board's lit edge
    c.rect(1, 5, 15, 1, seam); c.rect(1, 10, 15, 1, seam)               # the gaps between the boards
    c.rect(1, 1, 2, 15, shade); c.rect(13, 1, 3, 15, shade)             # corner posts
    c.rect(1, 1, 1, 15, lit if not back else "wd2")                     # the left post's lit face
    c.rect(6, 3, 5, 1, "wd5")                                           # the hand hole
    c.rect(0, 0, 16, 1, edge); c.rect(0, 0, 1, 16, edge)
    if back:
        c.rect(0, 0, 16, 1, "wd4"); c.rect(0, 0, 1, 16, "wd4")
    return c


def rope():
    """a coiled rope on top of the back stack: three turns seen from the front, a loose end"""
    c = Canvas(24, 8)
    for i, (x0, x1) in enumerate(((3, 21), (1, 23), (2, 22))):
        y = 2 + i * 2
        c.rect(x0, y, x1 - x0, 2, "net1" if i < 2 else "net2")
        c.rect(x0, y + 1, x1 - x0, 1, "net2")
    c.rect(5, 1, 14, 1, "net1")
    c.rect(1, 7, 22, 1, "net2")
    return c


# ------------------------------------------------------------------------------------------------------------ tarp
def tarp():
    """88 x 24: a rowboat drawn up on two wooden chocks with a tarp over it (decoration, back layer, no ink).
    The tarp's back rises in a flat dome, its hem hangs in folds; the bow and the stern show at each end; the
    chocks stand on the quay (bottom row = y 184)."""
    c = Canvas(88, 24)
    # the hull's ends under the tarp (wood), rows 12-19
    for x in range(4, 84):
        e = min(x - 4, 83 - x)
        top = 12 + max(0, 3 - e // 2)
        bot = 19 - max(0, 2 - e // 3)
        c.rect(x, top, 1, bot - top + 1, "wd3")
        c.px(x, top, "wd2")
        c.px(x, bot, "wd4")
    # the tarp: a dome from row 2 to row 15, hem at rows 13-17 in folds every 11 px
    for x in range(6, 82):
        e = min(x - 6, 81 - x)
        top = 2 + max(0, 6 - e // 3)
        hem = 15 + (2 if (x // 11) % 2 == 0 else 1)
        if x < 10 or x > 77:
            hem = 14
        c.rect(x, top, 1, hem - top + 1, "tarp2")
        c.px(x, top, "tarp1")
        if top + 1 <= hem:
            c.px(x, top + 1, "tarp1" if e > 8 else "tarp2")
        c.px(x, hem, "tarp3")
    for fx in range(16, 76, 11):                                        # folds: one shade band each
        for y in range(6, 16):
            if c.get(fx, y) == "tarp2":
                c.px(fx, y, "tarp3")
    c.rect(20, 5, 48, 1, "tarp1")                                       # the lit crown of the dome
    # two lashing ropes over the tarp to the chocks
    for rx in (24, 62):
        for y in range(3, 18):
            if c.get(rx, y) is not None:
                c.px(rx, y, "net1")
    # the chocks (two wooden blocks), rows 19-23
    for bx in (16, 62):
        c.rect(bx, 19, 10, 5, "wd3")
        c.rect(bx, 19, 10, 1, "wd2")
        c.rect(bx + 9, 20, 1, 4, "wd4")
    return c


# ------------------------------------------------------------------------------------------------------- fish shed
def fishshed():
    """96 x 80 (x 1952-2048, y 104-184): tarred vertical boards on a 4 px grid, white-ish corner boards, the roof
    edge band at the top (rows 0-7: the roof seen front-on as it slopes away), two loading doors, a small window.
    The one-way ROOF ledge (y 112-116) is drawn by the module over it, held by brackets into these boards."""
    c = Canvas(96, 80)
    c.rect(0, 8, 96, 72, "tar2")                                        # the wall (rows 8-79)
    for x in range(0, 96, 6):                                           # boards: a joint every 6 px, lit edge
        c.rect(x, 8, 1, 72, "tar3")
        c.rect(x + 1, 8, 1, 72, "tar1")
    c.rect(0, 8, 96, 2, "tar3")                                         # the eave's shadow on the wall
    c.rect(0, 0, 96, 8, "shedRoof")                                     # the roof band, its lit front row
    c.rect(0, 6, 96, 2, "roof2")
    c.rect(0, 0, 96, 1, "roof1")
    for x in (0, 1, 2, 93, 94, 95):                                     # corner boards
        c.rect(x, 10, 1, 70, "shedTrim" if x in (1, 94) else "tar3")
    # two loading doors (32 x 44), with diagonal braces, under a lintel
    dx, dy, dw, dh = 32, 36, 32, 44
    c.rect(dx - 2, dy - 2, dw + 4, 2, "shedTrim")
    c.rect(dx - 2, dy, 2, dh, "shedTrim"); c.rect(dx + dw, dy, 2, dh, "shedTrim")
    c.rect(dx, dy, dw, dh, "shedDoor")
    for x in range(dx, dx + dw, 4):
        c.rect(x, dy, 1, dh, "tar3")
    c.rect(dx + dw // 2, dy, 1, dh, "ink")
    for half in (0, 1):                                                 # the Z braces
        x0 = dx + half * dw // 2
        c.rect(x0 + 1, dy + 6, dw // 2 - 2, 2, "tar1"); c.rect(x0 + 1, dy + dh - 2, dw // 2 - 2, 2, "tar1")
        for i in range(dh - 10):
            xx = x0 + 2 + int(i * (dw // 2 - 5) / (dh - 10))
            c.rect(xx, dy + 8 + i, 2, 1, "tar1")
    # a small dark window with a moon glint (12 x 10), left of the doors
    wx, wy = 10, 30
    c.rect(wx - 1, wy - 1, 14, 12, "shedTrim")
    c.rect(wx, wy, 12, 10, "shedDoor")
    c.rect(wx + 5, wy, 2, 10, "shedTrim"); c.rect(wx, wy + 4, 12, 2, "shedTrim")
    return c


# ---------------------------------------------------------------------------------------------------------- house
def house():
    """144 x 176: Mia's house (wall x 4240-4368 = cols 8-135, y 72-184 = rows 64-175; the gable above, the eaves 8 px
    out each side). Falu red vertical boards on a 6 px grid, white trim at the corners and round the windows and the
    door, a gable with a lit attic window, a lit double window (the light at x 4280), a green door with a lit pane
    (x 4312-4336), wooden porch steps. The brass lantern (the light at x 4344) is drawn by night.lua with the lights."""
    W, H = 144, 176
    c = Canvas(W, H)
    wl, wr, wt = 8, 136, 64                                             # the wall: cols 8-135, rows 64-175
    peak = 4
    # the gable: boards up to the roof line (45 degrees: 1 px up per px in)
    for x in range(wl, wr):
        e = min(x - wl, wr - 1 - x)
        top = max(peak + 2, wt - e)
        c.rect(x, top, 1, H - top, "red2")
    for x in range(wl, wr, 6):                                          # boards (6 px): joint, lit edge
        for y in range(0, H):
            if c.get(x, y) == "red2":
                c.px(x, y, "red3")
            if c.get(x + 1, y) == "red2":
                c.px(x + 1, y, "red1")
    c.rect(wl, wt - 2, wr - wl, 1, "red3")                              # the gable's sill board
    c.rect(wl, wt - 1, wr - wl, 1, "trim2")
    # the roof: barge boards (white trim) along both slopes, the eaves out 8 px, a dark roof edge behind them
    for x in range(0, W):
        e = min(x, W - 1 - x)
        y = wt + 6 - e
        if y < peak:
            y = peak
        for k, col in ((-3, "roof3"), (-2, "roof2"), (-1, "roof1"), (0, "trim1"), (1, "trim1"), (2, "trim2")):
            if 0 <= y + k < H and y + k <= wt + 8:
                c.px(x, y + k, col)
    for x in range(W // 2 - 2, W // 2 + 2):                             # the ridge
        c.px(x, peak - 1, "trim1"); c.px(x, peak - 2, "roof1")
    # corner boards
    for x in (wl, wl + 1, wl + 2, wr - 3, wr - 2, wr - 1):
        c.rect(x, wt + 4, 1, H - wt - 4, "trim1" if x in (wl + 1, wr - 2) else "trim2")
    c.rect(wl, H - 3, wr - wl, 3, "red4")                               # the plinth's shadow at the foot

    def window(x, y, w, h, bars):
        c.rect(x - 2, y - 2, w + 4, h + 4, "trim1")
        c.rect(x - 2, y + h + 1, w + 4, 2, "trim2")                     # the sill
        c.rect(x, y, w, h, "win1")
        c.rect(x, y + h // 2, w, h - h // 2, "win2")                    # lower panes a step deeper
        for bx in bars[0]:
            c.rect(x + bx, y, 1, h, "winBar")
        for by in bars[1]:
            c.rect(x, y + by, w, 1, "winBar")
    # the double window: its middle on the light at x 4280 (col 48), y 112 (row 104)
    window(48 - 13, 104 - 14, 26, 28, ((6, 12, 13, 19), (13,)))
    # the attic window in the gable, on the middle
    window(W // 2 - 8, 26, 16, 16, ((7, 8), (7, 8)))
    # the door: x 4312-4336 (cols 80-103), its top at row 56 above the box (y 128), to the steps (y 176)
    dx, dw, dt, db = 80, 24, 120 - 72 + 56 - 48, 168
    dt = 56 + 64 - 8                                                     # row 112 = y 120
    c.rect(dx - 3, dt - 3, dw + 6, db - dt + 3, "trim1")
    c.rect(dx - 3, dt - 3, dw + 6, 1, "trim2")
    c.rect(dx, dt, dw, db - dt, "door2")
    c.rect(dx, dt, 1, db - dt, "door1"); c.rect(dx + dw - 1, dt, 1, db - dt, "door3")
    c.rect(dx + 4, dt + 4, dw - 8, 14, "door3")                         # the lit pane, in a sash
    c.rect(dx + 5, dt + 5, dw - 10, 12, "win2")
    c.rect(dx + 5, dt + 10, dw - 10, 1, "winBar"); c.rect(dx + 11, dt + 5, 2, 12, "winBar")
    c.rect(dx + 4, dt + 24, dw - 8, 1, "door3"); c.rect(dx + 4, dt + 24, 1, db - dt - 28, "door3")
    c.rect(dx + 4, db - 4, dw - 8, 1, "door1"); c.rect(dx + dw - 5, dt + 24, 1, db - dt - 28, "door1")
    c.rect(dx + dw - 6, dt + 30, 2, 2, "brass1")                        # the handle
    # porch steps (wood), rows 168-175: two treads, wider than the door
    c.rect(dx - 6, 168, dw + 12, 4, "wd2"); c.rect(dx - 6, 168, dw + 12, 1, "wd1")
    c.rect(dx - 10, 172, dw + 20, 4, "wd3"); c.rect(dx - 10, 172, dw + 20, 1, "wd1")
    c.rect(dx - 6, 171, dw + 12, 1, "wd4")
    return c


# ----------------------------------------------------------------------------------------------------------- post
def post():
    """16 x 64 (x 2712-2728, y 176-240): a timber mooring pile in the water, an obstacle (ink outline). An iron cap
    on top, an iron band, the grain, below the waterline (row 32 = y 208) wet and dark."""
    c = Canvas(16, 64)
    c.rect(0, 0, 16, 64, "pile2")
    for x in (4, 9, 12):
        c.rect(x, 4, 1, 60, "pile3")
    c.rect(1, 0, 3, 64, "pile1")
    c.rect(0, 0, 16, 3, "iron2"); c.rect(1, 0, 14, 1, "iron1")          # the cap
    c.rect(0, 12, 16, 2, "iron3"); c.rect(1, 12, 3, 1, "iron2")         # an iron band
    c.rect(0, 30, 16, 2, "door3")                                       # weed at the waterline
    c.rect(0, 32, 16, 32, "wet")                                        # below the waterline
    c.rect(1, 32, 3, 32, "pile3")
    c.outline("ink")
    return c


def frontpile():
    """12 x 19: a pile's top in the foreground (front layer: a dark silhouette, a 1 px rim on its top and left, a
    rope wrapped round it). No ink outline: the front layer's own dark."""
    c = Canvas(12, 19)
    c.rect(0, 2, 12, 17, "ink")
    c.rect(1, 1, 10, 1, "ink")
    c.rect(1, 1, 10, 1, "pile3"); c.rect(0, 2, 1, 17, "pile3")
    c.rect(1, 7, 10, 2, "wd4")                                         # the rope round it
    return c


# ------------------------------------------------------------------------------------------------- lamp, lantern
def lamp_night():
    """lamp_post.png recoloured whole-pixel (no resampling): its iron by luma rank to the night's dark iron, its
    glass to warm lamplight. 14 x 101, the same pixels."""
    src = Image.open(os.path.join(SCENE, "lamp_post.png")).convert("RGBA")
    a = np.array(src)
    cols = sorted({tuple(p) for p in a.reshape(-1, 4) if p[3] > 0}, key=lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2])
    iron = ["iron4", "iron3", "iron2", "iron1"]
    m = {}
    for i, col in enumerate(cols):
        r, g, b = col[:3]
        L = 0.299 * r + 0.587 * g + 0.114 * b
        if L > 170:                                                     # the glass: warm, lit
            m[col] = "glass" if L > 200 else "win2"
        else:
            m[col] = iron[min(3, i * 4 // max(1, len(cols) - 1))]
    c = Canvas(a.shape[1], a.shape[0])
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            p = tuple(a[y, x])
            if p[3] > 0:
                c.px(x, y, m[p])
    return c, m


def lantern():
    """7 x 10: a harbour lantern's head: an iron cap, warm glass in a frame, a bottom plate"""
    c = Canvas(7, 10)
    c.rect(1, 0, 5, 1, "iron2"); c.rect(0, 1, 7, 1, "iron1")
    c.rect(1, 2, 5, 6, "iron2")
    c.rect(2, 2, 3, 5, "glass"); c.rect(2, 6, 3, 1, "win2")
    c.rect(1, 8, 5, 1, "iron2"); c.rect(2, 9, 3, 1, "iron3")
    return c


# ------------------------------------------------------------------------------------------------------------ boats
def hull(deck, white):
    """a boat's hull seen from the side, its deck (gunwale top) on row 2 across `deck` px from col 2; the sheer
    rises 2 px at the bow (right) and the stern (left); the keel curves up at both ends; clinker strakes. The
    waterline is row 11 (y 207): the module draws the water's line against it. An obstacle: ink outline."""
    W = deck + 4
    c = Canvas(W, 14)
    body, lit, shade, strake = ("hull1", "trim1", "hull3", "hull2") if white else ("wd2", "wd1", "wd4", "wd3")
    for x in range(W):
        e = min(x, W - 1 - x)
        top = 2 - (1 if e < 4 else 0) - (1 if e < 2 else 0)
        bot = 13 - max(0, 4 - e) - (1 if e < 1 else 0)
        if bot <= top:
            continue
        c.rect(x, top, 1, bot - top + 1, body)
        c.px(x, top + 1, lit)
        for sy in (5, 8):
            if top + 1 < sy < bot:
                c.px(x, sy, strake)
        if bot - 1 > top + 1:
            c.px(x, bot - 1, shade)
    c.rect(4, 3, W - 8, 1, "wd2" if white else "wd3")                  # the inside of the far gunwale
    c.outline("ink")
    return c


# ------------------------------------------------------------------------------------------------------------ water
def recolour_water(rows):
    """water.png rows recoloured whole-pixel: each of its colours to the night ramp w0-w6 by its luma rank"""
    src = np.array(Image.open(os.path.join(SCENE, "water.png")).convert("RGB"))[rows[0]:rows[1]]
    cols = sorted({tuple(p) for p in src.reshape(-1, 3)}, key=lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2])
    ramp = ["w0", "w1", "w2", "w3", "w4", "w5", "w6"]
    n = len(cols)
    m = {col: ramp[min(6, i * 7 // n)] for i, col in enumerate(cols)}
    c = Canvas(src.shape[1], src.shape[0])
    for y in range(src.shape[0]):
        for x in range(src.shape[1]):
            c.px(x, y, m[tuple(src[y, x])])
    return c


# ------------------------------------------------------------------------------------------------------------ shore
def shed(w, wall_h, lit_win, door):
    """a boat shed seen front-on (about 13 px a metre): vertical boards on a 3 px grid, a gable at 45 degrees with
    white-ish barge boards, a dark door, a small window (lit or not). Returns the canvas; its bottom row stands on
    the pier."""
    gh = w // 2
    H = wall_h + gh + 2
    c = Canvas(w + 4, H)
    for x in range(2, w + 2):
        e = min(x - 2, w + 1 - x)
        top = max(2, gh + 2 - e)
        c.rect(x, top, 1, H - top, "shed2")
        if (x - 2) % 3 == 0:
            c.rect(x, top, 1, H - top, "shed3")
        elif (x - 2) % 3 == 1:
            c.rect(x, top, 1, H - top, "shed1")
    for x in range(0, w + 4):                                           # barge boards and the roof's dark edge
        e = min(x, w + 3 - x)
        y = gh + 3 - e
        if y < 1:
            y = 1
        c.px(x, y, "shedTrim")
        if y - 1 >= 0:
            c.px(x, y - 1, "shedRoof")
    c.rect(2, gh + 2, w, 1, "shed3")
    if door:
        dw, dh = max(6, w // 3), max(9, wall_h * 2 // 3)
        dx = 2 + (w - dw) // 2
        c.rect(dx - 1, H - dh - 1, dw + 2, dh + 1, "shedTrim")
        c.rect(dx, H - dh, dw, dh, "shedDoor")
        c.rect(dx + dw // 2, H - dh, 1, dh, "shed3")
    wx, wy = 2 + w // 2 - 2, gh // 2 + 3
    c.rect(wx - 1, wy - 1, 6, 5, "shedTrim")
    c.rect(wx, wy, 4, 3, "tiny" if lit_win else "shedDoor")
    if lit_win:
        c.rect(wx, wy + 2, 4, 1, "win2")
    return c


def sailboat(L, mast, light):
    """a moored sailboat at ~13 px a metre: a hull (L px), a mast (`mast` px), a forestay and a backstay, a
    furled boom; a tiny light at the masthead"""
    H = mast + 10
    c = Canvas(L + 2, H)
    hy = H - 6
    for x in range(L):
        e = min(x, L - 1 - x)
        top = hy - (1 if e < 3 else 0)
        bot = hy + 4 - max(0, 3 - e)
        c.rect(x + 1, top, 1, max(1, bot - top + 1), "hull2")
        c.px(x + 1, top, "hull1")
    mx = 1 + L * 2 // 5
    c.rect(mx, hy - mast, 1, mast, "mast")
    for i in range(1, mast):                                            # forestay to the bow, backstay to the stern
        fx = mx + int(i * (L - (mx - 1) - 2) / mast)
        bx = mx - int(i * (mx - 2) / mast)
        c.px(fx, hy - mast + i, "mast"); c.px(bx, hy - mast + i, "mast")
    c.rect(mx, hy - 8, L * 2 // 5, 2, "hull3")                          # the boom with its furled sail
    c.rect(mx, hy - 8, L * 2 // 5, 1, "hull2")
    if light:
        c.px(mx, hy - mast - 1, "tiny")
    return c


def motorboat(L):
    """a small moored motorboat: a hull and a low wheelhouse with a lit window"""
    c = Canvas(L + 2, 14)
    for x in range(L):
        e = min(x, L - 1 - x)
        top = 8 - (1 if e < 3 else 0)
        c.rect(x + 1, top, 1, 14 - top - max(0, 2 - e), "hull1" if x % 1 == 0 else "hull1")
        c.px(x + 1, 13 - max(0, 2 - e), "hull3")
    c.rect(1, 9, L, 1, "hull2")
    c.rect(L // 3, 2, L // 3, 6, "hull2"); c.rect(L // 3, 2, L // 3, 1, "hull1")
    c.rect(L // 3 + 2, 4, 3, 2, "tiny")
    return c


def shore(water_top):
    """1568 x 132 (screen y 40-171): the far side of the bay. A pier on piles at y 146 (row 106) with boat sheds
    on it in groups, moored boats between them, the bay below (water.png rows 0-25 recoloured), every boat's and
    window's light reflected in it as a broken amber column, each hull's dark reflection."""
    W, H = 1568, 132
    c = Canvas(W, H)
    pier = 106                                                          # y 146
    wl = 112                                                            # the waterline of the boats (y 152)
    # the bay: rows 106-131 (y 146-171)
    for y in range(water_top.h):
        for x in range(W):
            c.px(x, pier + y, water_top.g[y][x % water_top.w])
    refl = []                                                           # (x, colour) light reflections
    # groups of sheds on the pier, boats between (a fixed layout: seeded)
    rng = np.random.RandomState(8)
    x = 12
    gi = 0
    while x < W - 60:
        n = 2 + (gi % 2)
        group_w = 0
        sheds = []
        for k in range(n):
            w = [40, 46, 52][(gi + k) % 3]
            wall = [22, 26, 24][(gi * 2 + k) % 3]
            sh = shed(w, wall, lit_win=((gi + k) % 3 == 1), door=True)
            sheds.append((group_w, sh, (gi + k) % 3 == 1, w))
            group_w += w + 4 + 2
        # the pier under the group: deck 2 px, piles every 8 px down into the water
        px0, px1 = x - 4, x + group_w + 2
        c.rect(px0, pier - 2, px1 - px0, 2, "shed1"); c.rect(px0, pier - 1, px1 - px0, 1, "shed3")
        for pxx in range(px0 + 2, px1, 8):
            c.rect(pxx, pier, 2, 7, "shed3")
        for ox, sh, lit, w in sheds:
            c.stamp(sh, x + ox, pier - 2 - sh.h)
            if lit:
                refl.append((x + ox + 2 + w // 2, 2))
        x = px1 + 10
        # boats moored in the gap
        gap = 70 + (gi * 37) % 60
        bx = x
        while bx < x + gap - 34:
            if (gi + bx) % 3 == 0:
                L = 30 + (bx * 7) % 12
                b = motorboat(L)
                c.stamp(b, bx, wl - 10)
                refl.append((bx + L // 3 + 3, 3))
                hullref = (bx + 1, bx + L, "hull3")
            else:
                L = 34 + (bx * 5) % 14
                mast = 52 + (bx * 3) % 26
                b = sailboat(L, mast, light=(bx % 2 == 0))
                c.stamp(b, bx, wl + 4 - b.h + 2)
                if bx % 2 == 0:
                    refl.append((1 + bx + L * 2 // 5, 1))
                hullref = (bx + 2, bx + L - 1, "hull3")
            for xx in range(hullref[0], hullref[1]):                    # the hull's dark reflection, broken
                if xx % 5 != 0:
                    c.px(xx, wl + 5, "w0")
                if xx % 3 != 0 and hullref[0] + 2 < xx < hullref[1] - 2:
                    c.px(xx, wl + 7, "w0")
            bx += L + 8
        x += gap
        gi += 1
    # the lights' reflections: a broken column of amber dashes under each light, widening down the bay
    for rx, kind in refl:
        y0 = pier + 3
        for i, y in enumerate(range(y0, H - 1, 3)):
            w = 1 + i // 3
            off = (i * 2) % 3 - 1
            col = "refl1" if i < 2 else ("refl2" if i < 5 else "refl3")
            if i > 7:
                break
            c.rect(rx - w // 2 + off, y, w, 1, col)
    return c


def far_town():
    """448 x 110 (screen y 40-149): the old town on the far shore, at 0.03 (capped, 128 px over the level: the strip
    is 320 + 128 wide, never repeated). Houses with stepped and pointed gables on a 4 px grid, a tall spire and a
    tower, windows 1 x 2 on a 4 x 6 grid (about one in four lit, fixed), a quay line at the foot (rows 106-109)."""
    W, H = 448, 110
    c = Canvas(W, H)
    base = 106
    rng = np.random.RandomState(4)
    x = 0
    k = 0
    houses = []
    while x < W:
        w = int(rng.choice([16, 20, 24, 28]))
        h = int(rng.choice([28, 32, 36, 40, 44]))
        if 150 <= x < 182:                                              # the church: nave and spire
            w, h = 40, 34
        houses.append((x, w, h, k))
        x += w
        k += 1
    for (x0, w, h, k) in houses:
        col = ["far1", "far2", "far1", "far3"][k % 4]
        top = base - h
        c.rect(x0, top, w, base - top, col)
        gable = k % 3
        if gable == 0:                                                  # pointed gable
            for i in range(w // 2):
                c.rect(x0 + i, top - i // 2 * 1 - 1, 1, i // 2 + 1, col)
                c.rect(x0 + w - 1 - i, top - i // 2 - 1, 1, i // 2 + 1, col)
            c.rect(x0 + w // 2 - 1, top - w // 4 - 1, 2, w // 4 + 1, col)
        elif gable == 1:                                                # stepped gable, 4 px steps
            for s in range(1, w // 8 + 1):
                c.rect(x0 + s * 4, top - s * 4, w - s * 8, 4, col)
        else:                                                           # a roof seen from the street
            c.rect(x0 + 2, top - 6, w - 4, 6, "farRoof")
            c.rect(x0 + 1, top - 2, w - 2, 2, "farRoof")
        # windows on a 4 x 6 grid: dark, about one in four lit
        for wy in range(top + 5, base - 6, 6):
            for wx in range(x0 + 2, x0 + w - 2, 4):
                lit = rng.rand() < 0.26
                c.rect(wx, wy, 1, 2, "farWin" if lit else "far3" if col != "far3" else "far2")
    # the spire (the church at x 150-190) and a tower
    sx = 170
    for i in range(40):
        hw = max(0, (i * 5) // 40)
        c.rect(sx - hw, base - 34 - 40 + i, hw * 2 + 1, 1, "far1")
    c.rect(sx - 5, base - 34 - 12, 11, 12, "far1")
    c.rect(sx - 1, base - 34 - 8, 2, 3, "farWin")                       # a lit belfry window
    c.px(sx, base - 34 - 41, "far1")
    tx = 330
    c.rect(tx, base - 70, 12, 70, "far2")
    for i in range(10):                                                 # its pyramid roof
        w = max(1, (i + 1) * 12 // 10)
        c.rect(tx + 6 - w // 2, base - 80 + i, w, 1, "far2")
    for wy in range(base - 64, base - 10, 8):
        c.rect(tx + 5, wy, 2, 3, "far3")
    c.rect(tx + 5, base - 64, 2, 3, "farWin")
    c.rect(0, base, W, 4, "far3")                                       # the far quay
    c.rect(0, base, W, 1, "far2")
    return c


# ------------------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    args = ap.parse_args()
    parts = []
    save(crate(False), "crate_cell.png", parts)
    save(crate(True), "crate_back.png", parts)
    save(rope(), "rope.png", parts)
    save(tarp(), "tarp.png", parts)
    save(fishshed(), "fishshed.png", parts)
    save(house(), "house.png", parts)
    save(post(), "post.png", parts)
    save(frontpile(), "frontpile.png", parts)
    lm, m = lamp_night()
    save(lm, "lamp_night.png", parts)
    save(lantern(), "lantern.png", parts)
    save(hull(56, False), "rowboat.png", parts)
    save(hull(48, True), "boat.png", parts)
    save(recolour_water((26, 94)), "water_near.png", parts)
    save(shore(recolour_water((0, 26))), "shore.png", parts)
    save(far_town(), "far_town.png", parts)
    for n, im in parts:
        print("%-16s %4d x %-4d %2d colours" % (n, im.width, im.height, len({p for p in im.getdata() if p[3]})))
    if args.sheet:
        small = [(n, im) for n, im in parts if im.width <= 160]
        k = 4
        W = sum(im.width * k + 8 for _, im in small)
        H = max(im.height * k for _, im in small)
        S = Image.new("RGBA", (W, H + 4), (90, 90, 110, 255))
        x = 0
        for n, im in small:
            S.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST), (x, 0))
            x += im.width * k + 8
        S.save(args.sheet)


if __name__ == "__main__":
    main()
