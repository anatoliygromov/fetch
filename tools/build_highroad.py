#!/usr/bin/env python3
"""tools/build_highroad.py: the tall Downtown's high road attached to its house fronts (art/dt-highroad-06nov, 0 credits).

The owner on the 6 Nov roofs frames (camera x 1440-1640, y 120): "this looks weird". Since decision 1a the fronts are
true scale and run past the top of the screen, but the high road's pieces were drawn for the old small roofs, so they
hung in the middle of a big wall: the guild house's stepped gable as a floating brick pyramid with a disc, a chimney
in front of a dormer window, a balustrade on nothing, balconies as cages on quarter-scale doll houses. Here every
piece Pepper stands on up there is part of a facade: built from the 5 Nov sample fronts' parts
(tools/build_tall_fronts.py: the upper window, the string course, the granite and plaster ramps) and the roof kit's
ink and granite (tools/build_roof_kit.py, tools/build_dt_details.py: the balcony corbel). No box moves.

Decoration (faded with the fronts, no outline; the plaster colours W / S swapped per building as the fronts are):
  town_front_tall5.png     88 x 432  a plain bay: the two upper storeys and their windows over a ground floor of wall,
                                     cornice and plinth only (decision 2a: the wall behind a plaza balcony)
  town_front_tall6.png    148 x 432  the guild house at true scale (GUILD HOUSE, x 1552-1700): a granite ground floor
                                     whose top is the stepped gable's line (the steps are its coping), a 2.1 m oak door
                                     between its two balconies, a French window behind each, plaster upper storeys
                                     with two windows each, clear of the stone pedestal on the steps' landing
  town_balcony_door.png    38 x 52   a French window (two panes across, two down, the fronts' panes and bars, a stone
                                     surround) behind a plaza balcony, its top at y 295, its foot behind the slab
  town_window_door.png     52 x 50   the first-floor window carried down to a first-floor balcony (BALCONY x 1328):
                                     the same panes and bars, rows y 222-271, through the sill and the cornice
  town_window_rail.png     44 x 24   the flush railing of a French balcony: a ledge of the high road under a first-floor
                                     window is its stone sill, the window carried down to it (town_window_door)
  town_pilaster.png        14 x 101  a granite pilaster (capital, shaft, base; its cast shadow on the right) from the
                                     LOGGIA's foot (y 305) to the plinth: two frame the carriage gate, so the loggia
                                     is the portal's entablature
Play (outlined, unfaded, the roof kit's ink and granite):
  town_guild_steps.png    122 x 35   the stepped coping on the GUILD ROOF boxes (x 1560-1680), one stone coping per
                                     step (lit top, three mid, shade), at the steps' x0 - 1, the highest top - 1
  town_guild_pier.png      18 x 46   the CHIMNEY box (16 x 44) as a stone pedestal on the steps' landing: cornice cap
                                     (the golden bone's perch), shaft with a sunk panel, base; exactly the box + 1
  town_console.png          8 x 7    the balcony corbel (build_dt_details CORBEL), drawn once, stamped under both ends
                                     of every ledge of the high road (its top row on the slab's ink row)

  python3 -I tools/build_highroad.py             write them all (riverwalk/art/scene/)
  python3 -I tools/build_highroad.py --check     fail if a file on disk differs from the build
  python3 -I tools/build_highroad.py --sheet P   all pieces at 4x on one sheet
"""
import os, sys, argparse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_tall_fronts as TF                                            # the 5 Nov sample fronts' parts and ramps
import build_dt_details as DD                                             # the balcony corbel, the play granite

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")

FH = 432                                     # a full-height front: its top at y -18, its foot at y 414 (row = y + 18)
def row(y): return y + 18

# ---- decoration on the fronts' role grid (W S L T V G R F K J D N M I, tools/build_tall_fronts.py C) -------------
class Grid:
    def __init__(self, w, h, fill="W"):
        self.w, self.h = w, h
        self.a = np.full((h, w), fill, dtype="<U1")
    def rect(self, x0, y0, x1, y1, r):
        if x1 < x0 or y1 < y0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = r
    def put(self, x, y, r):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = r
    def stamp(self, rows, x, y):
        for dy, rr in enumerate(rows):
            for dx, ch in enumerate(rr):
                if ch != ".": self.put(x + dx, y + dy, ch)
    def png(self):
        im = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y, x] != ".": im[y, x] = (*TF.C[self.a[y, x]], 255)
        return im

def ground_floor_plain(w):
    """the ground floor's rows (the 240 canvas' rows 88-239): wall, the cornice, the plinth and its joints only"""
    cv = TF.Canvas(w); TF.common(cv)
    return cv.role[TF.CORNICE:]

def front_plain(w=88):
    return np.vstack([TF.upper(w), ground_floor_plain(w)])

# The French window, drawn once: the fronts' frame (F), panes 12 x 20 (G) with a lit left column (R), 2 px bars, two
# across and two down (30 x 46), in a 3 px granite surround (lit top and left, shade right), its cast shadow (S) 2 px
# to the right; no sill (the balcony's slab is its sill)
def french_window():
    W, H = 38, 52
    g = Grid(W, H, ".")
    g.rect(0, 0, 35, H - 1, "T"); g.rect(0, 0, 35, 0, "L"); g.rect(0, 0, 0, H - 1, "L"); g.rect(35, 1, 35, H - 1, "V")
    g.rect(36, 0, 37, H - 1, "S")
    x0, y0 = 3, 3
    g.rect(x0, y0, x0 + 29, H - 1, "F")
    for px in (x0 + 2, x0 + 16):
        for py in (y0 + 2, y0 + 24):
            g.rect(px, py, px + 11, py + 19, "G"); g.rect(px, py, px, py + 19, "R")
    g.rect(x0 + 2, y0 + 46, x0 + 27, H - 1, "G")                         # (the next panes, behind the slab)
    return g

BD_TOP = 295                                 # the French window's top row (y): under the galleries' string course
def window_door():
    """the upper window (build_tall_fronts.upper_window) carried down from its frame's foot (y 222) to y 271: the
    surround's sides, the frame, the next two panes and bars in its rhythm (panes every 24 rows), the cast shadow"""
    W, H = 52, 50
    g = Grid(W, H, ".")
    x0, x1 = 3, 46                                                       # the frame (44 wide), surround 3 each side
    g.rect(0, 0, 2, H - 1, "T"); g.rect(0, 0, 0, H - 1, "L"); g.rect(x1 + 1, 0, x1 + 3, H - 1, "T"); g.rect(x1 + 3, 0, x1 + 3, H - 1, "V")
    g.rect(x1 + 4, 0, x1 + 5, H - 1, "S")
    g.rect(x0, 0, x1, H - 1, "F")
    for px in (x0 + 2, x0 + 16, x0 + 30):
        for py in (0, 24):                                              # (y 222-243, 246-267: the window's own rhythm)
            g.rect(px, py, px + 11, py + 21, "G"); g.rect(px, py, px, py + 21, "R")
    return g

def window_rail():
    """a French balcony: the flush iron railing across the foot of a French window over a ledge (44 x 24, the glass's
    width), decoration, so no ink: the fronts' frame grey (F) for the handrail's lit top, granite shade (V) for the
    iron: a handrail (2 rows), a mid rail, a bottom rail, 1 px bars on a 4 px pitch"""
    W, H = 44, 24
    g = Grid(W, H, ".")
    g.rect(0, 0, W - 1, 1, "V"); g.rect(0, 0, W - 1, 0, "F")
    g.rect(0, 12, W - 1, 12, "V"); g.rect(0, H - 2, W - 1, H - 1, "V")
    for x in range(1, W - 1, 4): g.rect(x + 1, 2, x + 1, H - 3, "V")
    g.rect(0, 0, 0, H - 1, "V"); g.rect(W - 1, 0, W - 1, H - 1, "V")
    return g

def pilaster():
    """a granite pilaster (y 305-405): a capital 12 wide (lit top, mid, a dark lip), the shaft 10 wide (two lit
    columns, the stone, a shade column), a base 12 wide (two mouldings) on the plinth; its cast shadow (S) 2 px right"""
    W, H = 14, 101
    g = Grid(W, H, ".")
    g.rect(0, 0, 11, 4, "T"); g.rect(0, 0, 11, 0, "L"); g.rect(0, 4, 11, 4, "V")          # the capital
    g.rect(1, 5, 10, H - 9, "T"); g.rect(1, 5, 2, H - 9, "L"); g.rect(10, 5, 10, H - 9, "V")   # the shaft
    g.rect(1, 5, 10, 5, "V")                                                               # (under the capital)
    g.rect(0, H - 8, 11, H - 1, "T"); g.rect(0, H - 8, 11, H - 8, "L"); g.rect(0, H - 4, 11, H - 4, "V")   # the base
    g.rect(0, H - 3, 11, H - 3, "L"); g.rect(0, H - 1, 11, H - 1, "V"); g.rect(0, H - 8, 0, H - 1, "L"); g.rect(11, H - 7, 11, H - 1, "V")
    g.rect(12, 0, 13, 4, "S"); g.rect(11, 5, 12, H - 9, "S"); g.rect(12, H - 8, 13, H - 1, "S")   # its cast shadow
    return g

# ---- the guild house -----------------------------------------------------------------------------------------------
GX0 = 1552                                   # GUILD HOUSE x 1552-1700 (148 px)
# the stepped gable's boxes (riverwalk/level/tiled/downtown_tall.lua: GUILD ROOF and the steps right of it), x0, x1, top
STEPS = [(1560, 1568, 272), (1568, 1576, 268), (1576, 1584, 264), (1584, 1592, 260), (1592, 1600, 256), (1600, 1608, 252),
         (1608, 1616, 248), (1616, 1656, 244), (1656, 1664, 248), (1664, 1672, 252), (1672, 1680, 256)]
PIER = (1628, 1644, 200, 244)                # the CHIMNEY box: the pedestal
UPPER_X = [36, 118]                          # the guild's upper windows (both storeys): clear of the pedestal (x 1628-1644)
DOOR_CX = 1632                               # the door, between the balconies' slabs (x 1552-1608 and 1656-1712)
WIN_CX = [1580, 1674]                        # the French windows behind the two balconies (the right one inside the house)

def stone_top(lx):
    """the granite ground floor's top row (y) at the house's column lx"""
    x = GX0 + lx
    for x0, x1, t in STEPS:
        if x0 <= x < x1: return t
    return 280 if x < STEPS[0][0] else 262

def door(g, cx, lw=18):
    """a 2.1 m double door (the fronts' front_door, leaves 18 wide): a 4 px granite surround with a lintel and a
    keystone (y 305-311), two oak leaves with two raised panels each (y 312-405), handles, the threshold"""
    TOP, PL = row(305), row(406)
    dx0, dx1 = cx - lw, cx + lw - 1
    g.rect(dx0 - 4, TOP, dx1 + 4, PL - 1, "T")
    g.rect(dx0 - 4, TOP, dx0 - 4, PL - 1, "L"); g.rect(dx0 - 4, TOP, dx1 + 4, TOP, "L")
    g.rect(dx1 + 4, TOP + 1, dx1 + 4, PL - 1, "V"); g.rect(dx0 - 3, TOP + 6, dx1 + 3, TOP + 6, "V")
    g.rect(cx - 4, TOP, cx + 3, TOP + 8, "T"); g.rect(cx - 4, TOP, cx + 3, TOP, "L"); g.rect(cx - 4, TOP, cx - 4, TOP + 8, "L")
    g.rect(cx + 3, TOP + 1, cx + 3, TOP + 8, "V"); g.rect(cx - 3, TOP + 8, cx + 3, TOP + 8, "V")
    top = TOP + 7
    g.rect(dx0, top, dx1, PL - 1, "K")
    for x0 in (dx0, cx):
        g.rect(x0, top, x0 + lw - 1, top + 1, "D")
        g.stamp(TF.panel(12, 38), x0 + 3, top + 5)
        g.stamp(TF.panel(12, 40), x0 + 3, top + 48)
    g.rect(dx0, top, dx0, PL - 1, "D"); g.rect(cx - 1, top, cx, PL - 1, "D")
    g.rect(cx - 4, top + 44, cx - 3, top + 45, "I"); g.rect(cx + 2, top + 44, cx + 3, top + 45, "I")
    g.rect(dx0 - 2, PL - 1, dx1 + 2, PL - 1, "L")

def front_guild():
    W = 148
    g = Grid(W, FH, "W")
    up = TF.upper(W, {0: UPPER_X, 1: UPPER_X})                           # the two upper storeys (rows 0-279)
    g.a[:280] = up
    # the granite ground floor: coursed ashlar (12 px courses from the plinth up, 24 px blocks, offset by half), its top
    # the steps' line (the play coping covers each step's top 6 rows), lit at the left edge, a shade at the right
    PL = row(406)
    for lx in range(W):
        t = row(stone_top(lx))
        g.rect(lx, t, lx, PL - 1, "T")
    for y in range(row(262) - 20, PL):
        k = (PL - 1 - y) // 12
        if (PL - 1 - y) % 12 == 11:                                     # a bed joint
            for lx in range(W):
                if g.a[y, lx] == "T": g.put(lx, y, "V")
        else:
            for lx in range(W):
                if g.a[y, lx] == "T" and (lx + (12 if k % 2 else 0)) % 24 == 23: g.put(lx, y, "V")
    for lx in range(W):                                                  # the lit row under each step's coping
        t = row(stone_top(lx)) + 6
        if lx < STEPS[0][0] - GX0: t = row(280)
        g.put(lx, t, "L")
    g.rect(0, row(280), 0, PL - 1, "L")
    # the plinth (the fronts' common(): lit row, stone, a dark foot, joints on a 24 px grid)
    g.rect(0, PL, W - 1, PL, "L"); g.rect(0, PL + 1, W - 1, FH - 1, "T"); g.rect(0, FH - 1, W - 1, FH - 1, "V")
    for x in range(8 + (W // 2) % 24, W - 4, 24): g.rect(x, PL + 1, x, FH - 2, "V")
    door(g, DOOR_CX - GX0)
    fw = french_window()
    for cx in WIN_CX:                                                    # the French windows, cut at the plinth's top
        x = cx - GX0 - 18
        part = fw.a.copy()
        part[part == "S"] = "V"                                          # (the shadow on granite is its shade)
        for dy in range(part.shape[0]):
            for dx in range(part.shape[1]):
                if part[dy, dx] != ".": g.put(x + dx, row(BD_TOP) + dy, part[dy, dx])
        g.rect(x + 3, row(BD_TOP) + 52, x + 32, row(344) - 1, "G")       # (behind the slab)
    return g

# ---- play pieces (the roof kit's ink and granite, outlined) -------------------------------------------------------
def guild_steps():
    X0, Y0 = STEPS[0][0] - 1, min(t for _, _, t in STEPS) - 1
    W = STEPS[-1][1] - STEPS[0][0] + 2
    H = max(t for _, _, t in STEPS) + 6 - Y0
    cv = DD.Cv(W, H)
    def top(x):
        wx = x + X0
        for x0, x1, t in STEPS:
            if x0 <= wx < x1: return t
        return STEPS[0][2] if wx < STEPS[0][0] else STEPS[-1][2]
    for x in range(W):                                                   # a coping 7 rows on every step (its outline
        t = top(x) - Y0                                                  # row over the top, lit, three mid, shade, ink)
        cv.rect(x, t - 1, x, t + 5, "g2")
        cv.put(x, t, "g1"); cv.put(x, t + 4, "g3")
    for i, (x0, x1, t) in enumerate(STEPS):                              # the risers: lit where it rises (light from the
        if i and STEPS[i - 1][2] > t:                                    # upper left), shaded where it falls
            cv.rect(x0 - X0, t - Y0, x0 - X0, t - Y0 + 3, "g1")
        if i + 1 < len(STEPS) and STEPS[i + 1][2] > t:
            cv.rect(x1 - 1 - X0, t - Y0 + 1, x1 - 1 - X0, t - Y0 + 4, "g3")
    cv.outline()
    return cv

def guild_pier():
    """the CHIMNEY box as a stone urn on a pedestal (night/06nov-dt, review round 1: "the empty niche reads as a
    chimney stub"): 18 x 46 (x0 - 1, y0 - 1). The urn's flat lid is the perch (rows 1-4, the box's full width: the
    golden bone stands on it), a neck, a rim, a round body with a band, a short foot; under it the pedestal (a cap
    moulding, a plain die, a base). Each row is drawn from its half width (symmetric), lit on the left, shaded right"""
    cv = DD.Cv(18, 46)
    rows = {}                                                             # row: half width (the box is 16: half 8)
    for r in range(1, 5): rows[r] = 8                                     # the lid
    for r in range(5, 8): rows[r] = 5                                     # the neck
    for r in range(8, 10): rows[r] = 7                                    # the rim
    for r, hw in zip(range(10, 23), (6, 7, 7, 8, 8, 8, 8, 8, 8, 7, 7, 6, 6)): rows[r] = hw   # the body
    for r in range(23, 27): rows[r] = 4                                   # the foot
    for r in range(27, 45): rows[r] = 8                                   # the pedestal
    for r, hw in rows.items():
        cv.rect(9 - hw, r, 8 + hw, r, "g2")
    cv.outline()
    for r, hw in rows.items():                                            # light from the upper left, inside the ink
        if hw >= 2:
            for x, c in ((9 - hw + 1, "g1"), (8 + hw - 1, "g3")):
                if cv.a[r, x] != "ink": cv.put(x, r, c)
    cv.rect(2, 2, 15, 2, "g1"); cv.rect(5, 4, 12, 4, "g3")                # the lid's lit top and its shade
    cv.rect(3, 9, 14, 9, "g3")                                            # under the rim
    cv.rect(2, 16, 15, 16, "g3"); cv.rect(2, 15, 15, 15, "g1")            # the body's band
    cv.rect(2, 28, 15, 28, "g1"); cv.rect(2, 30, 15, 30, "g3")            # the pedestal's cap moulding
    cv.rect(2, 39, 15, 39, "g1"); cv.rect(2, 41, 15, 41, "g3")            # its base
    return cv

def console():
    """the balcony corbel under an ink row (the ledge's own bottom ink row, the box's top + 4, where it is drawn)"""
    cv = DD.Cv(8, 7)
    cv.rect(0, 0, 7, 0, "ink")
    cv.keyed(DD.CORBEL, DD.STONE, 0, 1)
    return cv

def build():
    def dd(cv):
        return cv.png()
    ims = {
        "town_front_tall5": TF.render(front_plain(88)),
        "town_front_tall6": front_guild().png(),
        "town_balcony_door": french_window().png(),
        "town_window_door": window_door().png(),
        "town_pilaster": pilaster().png(),
        "town_window_rail": window_rail().png(),
        "town_guild_steps": dd(guild_steps()),
        "town_guild_pier": dd(guild_pier()),
        "town_console": dd(console()),
    }
    return ims

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    o = ap.parse_args()
    ims = build(); bad = 0
    for n, im in ims.items():
        p = os.path.join(OUT, n + ".png")
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        assert ncol <= 20, (n, ncol)
        assert set(np.unique(im[..., 3]).tolist()) <= {0, 255}, n
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(n, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{n}: {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z, pad = 4, 16
        small = {k: v for k, v in ims.items() if v.shape[0] < 200}
        Wd = sum(v.shape[1] * z + pad for v in small.values()) + pad
        Ht = max(v.shape[0] for v in small.values()) * z + 2 * pad
        sheet = Image.new("RGBA", (Wd, Ht), (150, 120, 90, 255)); x = pad
        for v in small.values():
            sheet.alpha_composite(Image.fromarray(v).resize((v.shape[1] * z, v.shape[0] * z), Image.NEAREST), (x, pad)); x += v.shape[1] * z + pad
        sheet.save(o.sheet)
    sys.exit(1 if bad else 0)
