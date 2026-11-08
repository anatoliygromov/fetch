#!/usr/bin/env python3
"""tools/build_rooftops_art.py: Rooftops (level 4) art BUILT by rule from the level's own map (8 Nov 2026, phase 1, 0
credits; docs/review/08nov/rooftops/). Design target: art/gen/concepts/rt_hotel_concept_a.png (reference only, never
cut): warm ochre plaster under every roof with evenly spaced 4-pane windows, a sandstone parapet cap in blocks on the
edges Pepper walks, red clay tile roofs, green copper on the hotel, glass skylights in iron frames, stucco chimneys.

  python3 -I tools/build_rooftops_art.py              write riverwalk/levelart/rooftops/*.png and manifest.lua
  python3 -I tools/build_rooftops_art.py --check      fail if a file on disk is not what this script builds
  python3 -I tools/build_rooftops_art.py --preview D  also write previews of the whole level into folder D
  python3 -I tools/build_rooftops_art.py --parts D    also write each stamped part alone (for tools/asset_qa.py)

The ground (ground_<x>_<y>.png, 512 px chunks, the greybox's own chunking) is every terrain column of
riverwalk/level/tiled/rooftops.lua painted by rule, one pass per part, each part drawn once and stamped on the grid:
  * houses: the table HOUSES gives each building's span, plaster and cap material. Every house's front goes down to
    the street (y 1144): flat plaster, one shade band under its cap, windows stamped on one storey grid for the whole
    level (storey lines y 88 + 96 k: every tier of the map is one storey), the ground storey with doors and shop
    windows over a stone plinth, a downpipe on every party wall.
  * flat roofs: the parapet cap (sandstone blocks, copper with standing seams, or tin), 8 rows, the blocks spread
    evenly along each run; an open end overhangs 2 px; an end against a taller wall gets tin flashing up the wall.
  * pitched roofs: a 9 row band along the slope (red clay courses in running bond, or iron and glass), a ridge cap at
    the peak, the eaves over the cap line, the gable face below with an attic window (or a glazed iron grid).
  * stairs (the stairwell, x 576-768): 8 px stone steps (rise = run, the treads centred on the walking line as River
    Walk's ramps), a stone stringer under them, an iron handrail (decoration) above.
  * chimney blocks: stucco in brick courses on the roof's cap line, a stone slab on top, a tin apron at the foot.
  * skylights: every 40 px dip in a roof holds a glass lantern in an iron frame (decoration, behind Pepper).
  * the street: granite paving, a kerb and cobbles, along the whole block's foot.
  * the outline: 1 px ink on every sky pixel 4-next to the obstacle art (the edges Pepper walks and bumps).
PAL is the one palette table (per-material ramps sampled from the concept, neutral darks); swap it to recolour."""
import os, re, sys, hashlib
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "riverwalk/level/tiled/rooftops.lua")
OUT = os.path.join(ROOT, "riverwalk/levelart/rooftops")
CHUNK = 512
STREET = 1144                       # the street's walking line (start, cafe); every house front ends on it
STOREY0, STOREY = 88, 96            # storey lines: y = 88 + 96 k (all the map's tiers lie on them)

# ------------------------------------------------------------------------------------------------ the palette
PAL = {
    "ink": "2a1c1e",
    # sandstone parapet cap (concept: a48c74 / ccac84 / 7c645c)
    "cap_hi": "e6cea6", "cap_top": "d2b68e", "cap": "b49a7c", "cap_sh": "927a66", "cap_jt": "6e5a50",
    # copper (green patina, standing seams; concept 7ca474 / 547c6c)
    "cu_hi": "a8cc9c", "cu_top": "88b48a", "cu": "6c9a78", "cu_sh": "527c6a", "cu_jt": "3e5e56",
    # tin flashing, pipes, the court's floor
    "tin_hi": "d6d8d8", "tin": "a8acb2", "tin_sh": "7a808a",
    # plaster, four houses' colours (lit, wall, shade band, deep) and the recessed court
    "och_hi": "e4a666", "och": "d48c4e", "och_sh": "b87446", "och_dk": "9a5c3c",
    "yel_hi": "f0d08e", "yel": "e2ba72", "yel_sh": "c89c5a", "yel_dk": "a47e46",
    "sal_hi": "e8ae88", "sal": "d6906c", "sal_sh": "b87458", "sal_dk": "945a48",
    "cre_hi": "f2dcb2", "cre": "e2c69a", "cre_sh": "c6a67e", "cre_dk": "a28868",
    "crt_hi": "c48a5a", "crt": "b07648", "crt_sh": "96603e", "crt_dk": "7a4c34",
    # windows and doors
    "frame": "6e4c40", "glass": "5a6a72", "glass_hi": "90a2a8", "wood": "7a4a34", "wood_sh": "76493a",
    # red clay tiles (concept ac543c / d46c44)
    "tile_hi": "e8875a", "tile": "c8603e", "tile_sh": "a24a34", "tile_dk": "7c3a2c",
    # glass roof: iron frame, panes
    "iron": "3e3a44", "iron_hi": "6a6672", "gl": "a2bac2", "gl_hi": "d2e0e0", "gl_sh": "7e98a4",
    # stucco chimney in brick courses (concept 8c6c5c / 644c44)
    "ch_hi": "aa8c78", "ch": "8e6e5e", "ch_sh": "70564a", "ch_jt": "5c463e",
    # the street: granite paving, kerb, cobbles
    "gr_hi": "cfc6bc", "gr": "aea69c", "gr_sh": "8a827a", "gr_jt": "6e6662", "cob": "8e847a", "cob_hi": "a49a8e",
    "cob_sh": "6e665f",
}
NAMES = list(PAL)
IDX = {n: i + 1 for i, n in enumerate(NAMES)}            # 0 = transparent
RGB = np.zeros((len(NAMES) + 1, 4), np.uint8)
for n, h in PAL.items(): RGB[IDX[n]] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
PLASTER = {"ochre": "och", "yellow": "yel", "salmon": "sal", "cream": "cre", "court": "crt"}
CAPS = {"sand": ("cap_hi", "cap_top", "cap", "cap_sh", "cap_jt"), "copper": ("cu_hi", "cu_top", "cu", "cu_sh", "cu_jt"),
        "tin": ("tin_hi", "tin_hi", "tin", "tin_sh", "tin_sh")}

# ------------------------------------------------------------------------------------------------ the level's plan
# (x0, x1, plaster, cap): the buildings left to right (docs/rooftops_beatsheet.md). The street (0-576) has none.
HOUSES = [
    (576, 768, "yellow", "sand"),      # stairwell A: the steps up its front
    (768, 1280, "ochre", "sand"),      # the bakery, pitched roof R1
    (1280, 1568, "yellow", "sand"),    # T1b
    (1568, 1664, "court", "sand"),     # the light well (a recessed bay)
    (1664, 2048, "salmon", "sand"),    # pitched roof R2
    (2048, 2688, "cream", "sand"),     # the market hall: glass roof R3, the sweep's chimneys, the skylight dip
    (2688, 3328, "ochre", "sand"),     # the laundry
    (3328, 3872, "yellow", "sand"),    # the roof bar, the drying yard
    (3872, 4048, "salmon", "sand"),    # the roof bar's terrace
    (4048, 4800, "cream", "copper"),   # the hotel: two skylights, its chimney block
    (4800, 5200, "court", "tin"),      # the light court's floor (the lobby's roof)
    (5200, 5424, "ochre", "sand"),     # the tall block
    (5424, 5568, "yellow", "sand"),    # the scaffold house
    (5568, 5696, "salmon", "sand"),    # the cafe awning's house
    (5696, 6104, "cream", "sand"),     # the chimney stacks
    (6104, 6400, "ochre", "sand"),     # the sauna roof
    (6400, 6656, "salmon", "sand"),    # the nest chimney, the long roof's first pitch
    (6656, 6848, "yellow", "sand"),
    (6848, 7040, "ochre", "sand"),
    (7040, 7136, "cream", "sand"),
    (7136, 7472, "salmon", "sand"),    # the roof cafe
]
CHIMNEYS = [(2400, 2464), (4608, 4672), (6000, 6104), (6400, 6432)]   # stucco stacks on the roof line
GABLES = [(896, 1024, "tile"), (1792, 1920, "tile"), (2112, 2240, "glass")]
STAIRS = (576, 768)
WIN_W, WIN_H, WIN_TOP, PITCH, MARGIN = 18, 24, 54, 48, 12


def load_map():
    src = open(MAP).read()
    i = src.index('name = "terrain"'); j = src.index("data = {", i); k = src.index("}", j)
    data = np.array([int(v) for v in re.findall(r"\d+", src[j + 8:k])])
    W = int(re.search(r"\bwidth = (\d+)", src).group(1)); H = int(re.search(r"\bheight = (\d+)", src).group(1))
    return data.reshape(H, W)


def terrain(g):
    """per pixel column: the first top (as scene.lua's columnRuns: a slope cell's column i is y0 + i for '\\', y1 - i - 1
    for '/'), the kind there (flat, up, down) and the solid mask"""
    H, W = g.shape[0] * 8, g.shape[1] * 8
    top = np.zeros(W, int); kind = [""] * W
    for c in range(g.shape[1]):
        col = g[:, c]; r = int(np.nonzero(col)[0][0]); t = col[r]
        for i in range(8):
            x = c * 8 + i
            if t == 1: top[x], kind[x] = r * 8, "flat"
            elif t == 3: top[x], kind[x] = r * 8 + 8 - i - 1, "up"      # '/' rises to the right
            elif t == 4: top[x], kind[x] = r * 8 + i, "down"           # '\' falls to the right
    solid = np.arange(H)[:, None] >= top[None, :]
    return W, H, top, kind, solid


class Canvas:
    def __init__(self, W, H): self.a = np.zeros((H, W), np.uint8); self.W, self.H = W, H
    def put(self, x, y, n):
        if 0 <= x < self.W and 0 <= y < self.H: self.a[y, x] = IDX[n]
    def fill(self, x0, y0, x1, y1, n):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(self.W, x1), min(self.H, y1)
        if x1 > x0 and y1 > y0: self.a[y0:y1, x0:x1] = IDX[n]
    def sprite(self, spr, x, y, only_empty=False):
        """stamp a sprite (list of strings, legend dict) with its top-left at (x, y)"""
        rows, leg = spr
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                n = leg.get(ch)
                if n and 0 <= x + i < self.W and 0 <= y + j < self.H and (not only_empty or self.a[y + j, x + i] == 0):
                    self.a[y + j, x + i] = IDX[n]


# ------------------------------------------------------------------------------------------------ the parts (drawn once)
def window():
    """the 4-pane window: a dark frame 2 px, mullion and transom 2 px, a lit corner in each pane; sill under it"""
    W, H = WIN_W, WIN_H
    rows = []
    for y in range(H + 2):
        r = ""
        for x in range(W + 4):
            if y >= H:                                           # the sill: 22 px, lit top row, shade row
                r += "s" if y == H else "d"
                continue
            xx = x - 2
            if xx < 0 or xx >= W: r += "."; continue
            if y < 2 or y >= H - 2 or xx < 2 or xx >= W - 2 or xx in (8, 9) or y in (11, 12): r += "f"
            else:
                px, py = (xx - 2) % 8 if xx < 8 else (xx - 10), (y - 2) if y < 11 else (y - 13)
                r += "h" if (px + py < 3) else "g"
        rows.append(r)
    return rows, {"f": "frame", "g": "glass", "h": "glass_hi", "s": "cap_hi", "d": "cap_sh"}


def door():
    """a plank door 18 x 34 with a frame and a fanlight"""
    rows = []
    for y in range(36):
        r = ""
        for x in range(22):
            if x < 2 or x >= 20 or y < 2: r += "f"
            elif y < 8: r += "f" if (y == 7 or x in (10, 11)) else ("h" if x + y < 9 else "g")
            elif x in (2, 19) or x == 10 or x == 11: r += "w" if x not in (2, 19) else "d"
            else: r += "w" if (x % 4 != 1) else "d"
        rows.append(r)
    return rows, {"f": "frame", "g": "glass", "h": "glass_hi", "w": "wood", "d": "wood_sh"}


def shopwindow():
    """a ground floor shop window 30 x 30 (4 panes over a stone sill)"""
    rows = []
    for y in range(32):
        r = ""
        for x in range(32):
            if y >= 30: r += "s" if y == 30 else "d"; continue
            if x < 2 or x >= 30: r += "."; continue
            xx = x - 2
            if y < 2 or y >= 28 or xx < 2 or xx >= 26 or xx in (13, 14) or y == 9: r += "f"
            else:
                px, py = (xx - 2) if xx < 13 else (xx - 15), (y - 2) if y < 9 else (y - 10)
                r += "h" if (px + py < 3) else "g"
        rows.append(r)
    return rows, {"f": "frame", "g": "glass", "h": "glass_hi", "s": "cap_hi", "d": "cap_sh"}


def oculus():
    """a round attic window, 12 x 12"""
    rows = []
    for y in range(12):
        r = ""
        for x in range(12):
            d = ((x - 5.5) ** 2 + (y - 5.5) ** 2) ** 0.5
            if d > 6.0: r += "."
            elif d > 4.2: r += "f"
            elif x in (5, 6) or y in (5, 6): r += "f"
            else: r += "h" if (x + y < 8) else "g"
        rows.append(r)
    return rows, {"f": "frame", "g": "glass", "h": "glass_hi"}


# ------------------------------------------------------------------------------------------------ the build
def build():
    g = load_map()
    W, H, top, kind, solid = terrain(g)
    cv = Canvas(W, H)
    house_at = [None] * W
    for h in HOUSES:
        for x in range(h[0], h[1]): house_at[x] = h
    chim_at = {}
    for c0, c1 in CHIMNEYS:
        base = min(top[c0 - 1] if kind[c0 - 1] == "flat" else 10 ** 6, top[c1] if kind[c1] == "flat" else 10 ** 6)
        for x in range(c0, c1): chim_at[x] = (c0, c1, top[c0], base)
    gab_at = {}
    for a, b, mat in GABLES:
        for x in range(a, b): gab_at[x] = (a, b, mat, top[a - 1])
    # the roof line each column's front starts under (a chimney sits on its house's cap line; a pitched roof's
    # front starts under its band)
    roof = np.array([chim_at[x][3] if x in chim_at else top[x] for x in range(W)])

    # 1 the fronts: plaster from the roof line down to the street, the shade band under the cap
    for x in range(STAIRS[0], W):
        h = house_at[x]; p = PLASTER[h[2]]
        cv.fill(x, roof[x], x + 1, STREET, p)
        if kind[x] == "flat" or x in chim_at: cv.fill(x, roof[x] + 8, x + 1, roof[x] + 12, p + "_sh")
    # 2 windows on the storey grid (one grid for the level), doors and shop windows in the ground storey
    WIN, DOOR, SHOP, OCU = window(), door(), shopwindow(), oculus()
    def clear(x0, x1, y):                                       # the wall above a window is free of roofs
        return max(roof[max(0, x0 - 2):x1 + 2]) <= y - 14
    for (x0, x1, pl, capm) in HOUSES:
        w = x1 - x0
        n = max(1, (w - 2 * MARGIN - WIN_W) // PITCH + 1)
        span = (n - 1) * PITCH + WIN_W
        xs = [x0 + (w - span) // 2 + i * PITCH for i in range(n)]
        for L in range(STOREY0, STREET - STOREY, STOREY):
            y = L + WIN_TOP
            for wx in xs:
                if clear(wx, wx + WIN_W, y): cv.sprite(WIN, wx - 2, y)
        mid = n // 2
        for i, wx in enumerate(xs):                              # the ground storey: a door in the middle
            cx = wx + WIN_W // 2
            if i == mid: cv.sprite(DOOR, cx - 11, STREET - 8 - 36)
            else: cv.sprite(SHOP, cx - 16, STREET - 8 - 32 - 4)
        cv.fill(x0, STREET - 8, x1, STREET - 7, "gr_hi"); cv.fill(x0, STREET - 7, x1, STREET, "gr")   # the plinth
        cv.fill(x0, STREET - 1, x1, STREET, "gr_sh")
    # 3 party walls: a downpipe with a hopper head on every join between two houses
    for (x0, x1, pl, capm) in HOUSES[1:]:
        y0 = max(roof[x0 - 1], roof[x0]) + 12
        cv.fill(x0 - 1, y0, x0, STREET - 8, "tin_hi"); cv.fill(x0, y0, x0 + 1, STREET - 8, "tin_sh")
        cv.fill(x0 - 2, y0 - 3, x0 + 2, y0, "tin"); cv.fill(x0 - 2, y0 - 3, x0 + 2, y0 - 2, "tin_hi")
        for yy in range(y0 + 40, STREET - 16, 48): cv.fill(x0 - 2, yy, x0 + 2, yy + 1, "tin_sh")   # pipe clips
    # 4 caps on every flat run (and under chimneys, along the eaves of a pitched roof)
    def capped(x): return kind[x] == "flat" or x in chim_at or x in gab_at
    def capY(x): return roof[x] if (kind[x] == "flat" or x in chim_at) else gab_at[x][3]
    x = STAIRS[1]
    while x < W:
        if not capped(x): x += 1; continue
        a, y = x, capY(x); hcap = house_at[x][3]
        while x < W and capped(x) and capY(x) == y and house_at[x][3] == hcap: x += 1
        b = x
        hi, tp, mid_, sh, jt = CAPS[hcap]
        n = max(1, round((b - a) / 24))
        joints = {a + round(i * (b - a) / n) for i in range(1, n)}
        lo = a - 2 if (a > 0 and roof[a - 1] > y and not capped(a - 1) and kind[a - 1] == "flat") else a
        hi_ = b + 2 if (b < W and roof[b] > y and kind[b] == "flat") else b
        for xx in range(lo, hi_):
            seam = hcap == "copper" and (xx - a) % 8 == 4
            cv.put(xx, y, hi); cv.put(xx, y + 1, tp)
            for r in range(2, 6): cv.put(xx, y + r, jt if xx in joints else (tp if seam else mid_))
            if seam: cv.put(xx + 1, y + 2, sh); cv.put(xx + 1, y + 3, sh); cv.put(xx + 1, y + 4, sh); cv.put(xx + 1, y + 5, sh)
            cv.put(xx, y + 6, sh); cv.put(xx, y + 7, jt)
        if lo < a: cv.fill(lo, y + 1, lo + 1, y + 7, tp)                     # the lit left end
        if hi_ > b: cv.fill(hi_ - 1, y + 1, hi_, y + 7, sh)                   # the shaded right end
        # an end against a taller wall: tin flashing up the wall's foot
        if a > 0 and roof[a - 1] < y and kind[a - 1] == "flat" and not capped(a - 1) or (a > 0 and capped(a - 1) and capY(a - 1) < y):
            cv.fill(a - 2, y - 6, a - 1, y + 8, "tin_hi"); cv.fill(a - 1, y - 6, a, y + 8, "tin")
        if b < W and (roof[b] < y and kind[b] == "flat" or (capped(b) and capY(b) < y)):
            cv.fill(b, y - 6, b + 1, y + 8, "tin"); cv.fill(b + 1, y - 6, b + 2, y + 8, "tin_sh")
    # 5 chimney blocks: stucco in brick courses, a stone slab on top, a tin apron on the cap line
    for c0, c1 in CHIMNEYS:
        t, base = top[c0], chim_at[c0][3]
        for yy in range(t + 6, base):
            course = (yy - t - 6) // 6
            for xx in range(c0, c1):
                if (yy - t - 6) % 6 == 5: n = "ch_jt"
                elif (xx - c0 + (course % 2) * 8) % 16 == 0: n = "ch_jt"
                elif xx - c0 < 2: n = "ch_hi"
                elif c1 - xx <= 2: n = "ch_sh"
                else: n = "ch"
                cv.put(xx, yy, n)
        cv.fill(c0 - 2, t, c1 + 2, t + 1, "cap_hi"); cv.fill(c0 - 2, t + 1, c1 + 2, t + 4, "cap")
        cv.fill(c0 - 2, t + 4, c1 + 2, t + 5, "cap_sh"); cv.fill(c0 - 2, t + 5, c1 + 2, t + 6, "cap_jt")
        cv.fill(c0 - 2, t + 1, c0 - 1, t + 5, "cap_top"); cv.fill(c1 + 1, t + 1, c1 + 2, t + 5, "cap_sh")
        cv.fill(c0, base - 3, c1, base - 2, "tin_hi"); cv.fill(c0, base - 2, c1, base, "tin")
    # 6 pitched roofs: the band along the slope, the ridge cap, the gable face with its attic window
    def band(x, mat):
        t, d_ = top[x], kind[x]
        u = x if d_ == "up" else -x
        for d in range(9):
            y = t + d
            if mat == "tile":
                if d == 0: n = "tile_hi"
                elif d in (1, 2): n = "tile_sh" if u % 8 == 7 else "tile"
                elif d == 3: n = "tile" if u % 8 in (3, 4) else "tile_sh"
                elif d == 4: n = "tile_hi" if u % 8 in (5, 6, 7) else "tile"
                elif d in (5, 6): n = "tile_sh" if u % 8 == 3 else "tile"
                elif d == 7: n = "tile" if u % 8 in (7, 0) else "tile_sh"
                else: n = "tile_dk"
            else:
                if d == 0: n = "iron_hi"
                elif d in (7, 8): n = "iron"
                elif u % 16 == 0: n = "iron"
                else: n = "gl_hi" if (u % 16 + d) in (4, 5, 12, 13) else "gl"
            cv.put(x, y, n)
    for a, b, mat in GABLES:
        base = top[a - 1]; peak = (a + b) // 2
        for x in range(a, b):
            if mat == "glass":                                    # the market hall's glazed end
                for y in range(top[x] + 9, base):
                    if (x - a) % 16 == 0 or (y - base) % 16 == 0: n = "iron"
                    else: n = "gl_hi" if ((x - a) % 16 + (y - base) % 16) in (6, 7, 20, 21) else ("gl" if ((base - y) // 16) % 2 else "gl_sh")
                    cv.put(x, y, n)
            else:
                cv.fill(x, top[x] + 9, x + 1, base, PLASTER[house_at[x][2]] + "_hi")
            band(x, mat)
        if mat == "tile":
            for x in range(peak - 3, peak + 3):                   # the ridge cap
                cv.put(x, top[x], "tile_hi"); cv.put(x, top[x] + 1, "tile_sh"); cv.put(x, top[x] + 2, "tile_dk")
            cv.sprite(OCU, peak - 6, (top[peak] + base) // 2 - 2)
    for x in range(STAIRS[1], W):                                 # the long roof's pitches (mono-pitch, tiles)
        if kind[x] == "down" and x not in gab_at:
            cv.fill(x, top[x] + 9, x + 1, top[x] + 12, PLASTER[house_at[x][2]] + "_sh")
            band(x, "tile")
    # 7 stairs: 8 px steps, treads centred on the walking line, a stone stringer under them
    s0, s1 = STAIRS
    def stepTop(x): return STREET - int(np.floor((STREET - top[x]) / 8 + 0.5)) * 8
    for x in range(s0, s1):
        t = stepTop(x)
        edge = x == s0 or stepTop(x - 1) != t
        cv.fill(x, t, x + 1, STREET, PLASTER["yellow"])
        cv.put(x, t, "cap_hi"); cv.put(x, t + 1, "cap_top")
        for r in range(2, 8): cv.put(x, t + r, "cap_jt" if edge else "cap")
        for r in range(8, 14): cv.put(x, t + r, "cap_sh" if r < 13 else "cap_jt")
        cv.fill(x, t + 14, x + 1, t + 17, "yel_sh")
    # 8 the street along the block's foot
    for x in range(W):
        y = STREET
        cv.put(x, y, "gr_hi")
        for r in range(1, 9): cv.put(x, y + r, "gr_jt" if x % 32 == 0 else "gr")
        cv.put(x, y + 9, "gr_sh")
        cv.put(x, y + 10, "gr_hi")
        for r in range(11, 14): cv.put(x, y + r, "gr_jt" if x % 48 == 0 else "gr")
        cv.put(x, y + 14, "ink")
        for r in range(15, H - y):                                # cobbles: 8 x 5 setts in running bond
            yy = y + r; row = (r - 15) // 5; cx = (x + (row % 2) * 4) % 8; cy = (r - 15) % 5
            cv.put(x, yy, "cob_sh" if (cx == 7 or cy == 4) else ("cob_hi" if cy == 0 else "cob"))
    # 9 the outline: ink on every sky pixel 4-next to the art, above the street
    art = cv.a > 0
    nb = np.zeros_like(art)
    nb[1:, :] |= art[:-1, :]; nb[:-1, :] |= art[1:, :]; nb[:, 1:] |= art[:, :-1]; nb[:, :-1] |= art[:, 1:]
    ink = nb & ~art
    ink[STREET - 1:, :] = False
    ink[:, :STAIRS[0]] = False
    cv.a[ink] = IDX["ink"]
    # 10 decoration after the outline (only into empty pixels): skylights in the 40 px dips, the stair's handrail
    x = STAIRS[1]
    while x < W:
        if kind[x] == "flat" and x > 0 and top[x] - top[x - 1] == 40:
            a = x
            while x < W and top[x] == top[a] and kind[x] == "flat": x += 1
            if x < W and top[x] == top[a] - 40 and x - a <= 160: skylight(cv, a, x, top[a])
        else: x += 1
    for x in range(s0 - 2, s1):                                   # iron handrail: a rail 24 px over the walking
        y = top[x] - 24 if x >= s0 else STREET - 24 + (s0 - x)     # line (one pixel a column), posts every 16 px
        for yy, n in ((y, "iron_hi"), (y + 1, "iron")):
            if cv.a[yy, x] == 0: cv.put(x, yy, n)
        if (x - s0) % 16 == 6 or x == s0 - 2:
            for yy in range(y + 2, stepTop(max(x, s0)) - 1):
                if cv.a[yy, x] == 0: cv.put(x, yy, "iron")
    return cv, W, H, top, kind


def skylight(cv, a, b, floor):
    """a glass lantern on the dip's floor: an iron frame, panes 16 px wide, a lit glint in each"""
    x0, x1, y0, y1 = a + 3, b - 3, floor - 34, floor - 1
    for y in range(y0, y1):
        for x in range(x0, x1):
            if cv.a[y, x] != 0: continue
            fr = y in (y0, y0 + 1, y1 - 2, y1 - 1, y0 + 12) or x in (x0, x1 - 1) or (x - x0) % 16 == 0
            if fr: n = "iron" if y not in (y0,) else "iron_hi"
            else:
                k = ((x - x0) % 16) + (y - y0)
                n = "gl_hi" if k in (6, 7, 8, 18, 19) else ("gl" if y < y0 + 12 else "gl_sh")
            cv.put(x, y, n)


def chunks(cv, W, H):
    out = {}
    for cy in range(0, H, CHUNK):
        for cx in range(0, W, CHUNK):
            a = cv.a[cy:cy + CHUNK, cx:cx + CHUNK]
            if (a > 0).any(): out[(cx, cy)] = RGB[a]
    return out


def terrain_key(top):
    """the map's surface, as the game checks it at load (manifest.lua): every 8th column's top"""
    return hashlib.md5(",".join(str(int(t)) for t in top[::8]).encode()).hexdigest()


def manifest(ch, top):
    lines = ["-- written by tools/build_rooftops_art.py: the ground chunks of the Rooftops art (do not edit)", "return {",
             f'  key = "{terrain_key(top)}",   -- the map surface the art was built for (every 8th column\'s top)',
             f"  chunk = {CHUNK},", "  ground = {"]
    for (x, y), a in sorted(ch.items()):
        lines.append(f'    {{ x = {x}, y = {y}, w = {a.shape[1]}, h = {a.shape[0]}, file = "ground_{x}_{y}.png" }},')
    lines += ["  },", "}", ""]
    return "\n".join(lines)


def main():
    check = "--check" in sys.argv
    prev = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    cv, W, H, top, kind = build()
    ch = chunks(cv, W, H)
    files = {f"ground_{x}_{y}.png": a for (x, y), a in ch.items()}
    man = manifest(ch, top)
    fails = []
    if check:
        for f, a in files.items():
            p = os.path.join(OUT, f)
            if not os.path.exists(p) or not np.array_equal(np.array(Image.open(p).convert("RGBA")), a): fails.append(f)
        mp = os.path.join(OUT, "manifest.lua")
        if not os.path.exists(mp) or open(mp).read() != man: fails.append("manifest.lua")
    else:
        os.makedirs(OUT, exist_ok=True)
        for f in os.listdir(OUT):
            if f.startswith("ground_"): os.remove(os.path.join(OUT, f))
        for f, a in files.items(): Image.fromarray(a, "RGBA").save(os.path.join(OUT, f), optimize=True)
        open(os.path.join(OUT, "manifest.lua"), "w").write(man)
    if "--parts" in sys.argv:                                     # each stamped part alone (for tools/asset_qa.py)
        d = sys.argv[sys.argv.index("--parts") + 1]; os.makedirs(d, exist_ok=True)
        for name, spr in (("window", window()), ("door", door()), ("shopwindow", shopwindow()), ("oculus", oculus())):
            rows, leg = spr
            a = np.zeros((len(rows), len(rows[0])), np.uint8)
            for j, r in enumerate(rows):
                for i, ch in enumerate(r): a[j, i] = IDX[leg[ch]] if ch in leg else 0
            Image.fromarray(RGB[a], "RGBA").save(os.path.join(d, f"rt_{name}.png"))
    if prev:
        os.makedirs(prev, exist_ok=True)
        im = Image.fromarray(RGB[cv.a], "RGBA")
        bg = Image.new("RGBA", im.size, (250, 222, 180, 255)); bg.alpha_composite(im)
        bg.convert("RGB").save(os.path.join(prev, "ground_full.png"))
    used = len(np.unique(cv.a)) - 1
    print(f"rooftops art: {len(files)} ground chunks, {used} colours" + (f", {len(fails)} differ: {fails[:5]}" if fails else ""))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
