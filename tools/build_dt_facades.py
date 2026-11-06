#!/usr/bin/env python3
"""tools/build_dt_facades.py: the tall Downtown's house fronts lifted to the concept (night/06nov-dt, 0 credits).

The 6 Nov sweep: the tall fronts were big flat walls, every house the same grey windows, no cornices, no shutters, no
flower boxes, no anchors, no signs. The producer's design target is art/gen/concepts/dt_highroad_concept_a.png (and
dt_street_concept_a.png): moulded cornices per storey, small pediments over the windows (the same on a storey,
different per house), wooden shutters, geranium window boxes, black iron wall anchors, a drainpipe between houses, a
hanging iron shop sign with a picture (no letters). Design only: nothing here is cut from it.

Everything is BUILT from parts drawn once (a window, a pediment, an arch head, a shutter, a window box, an anchor, a
dentil, a sign plate, a picture) and stamped on the fronts' integer grid (tools/build_tall_fronts.py: storeys of
140 px, 3.0 m; the upper window 44 x 74, 1.0 x 1.6 m; the ground floor's bays). A house is one STYLE: every window of
one storey is pixel-identical within a house, and the style differs house to house (the box property `style` in
maps/downtown_tall.tmx, arthooks.lua frontImg). The window glass, frame and sill rows are the 5 Nov fronts' own, so the
high road's pieces that carry a first-floor window down to a balcony or a ledge (tools/build_highroad.py
town_window_door, town_window_rail) still meet it. Ground floors keep their bays (1 door, 2 shop, 3 gate, 5 plain);
the shop front's paint, the cornice's moulding and the sign over a door change with the style.

  style  first floor              second floor   shutters  window boxes  anchors  cornices  shop paint  door sign
  a      triangular pediment      straight hood  -         first floor   yes      dentils   green       a boot
  b      segmental arch, key      the same       -         -             -        double    oxblood     a cup
  c      straight hood            the same       yes       first floor   -        plain     blue        -
  d      eared surround, key      straight hood  -         -             yes      dentils   ink green   a key
  e      straight hood            the same       -         both          yes      double    green       a fish
  f      triangular pediment      the same       -         -             yes      plain     oxblood     -

Files (riverwalk/art/scene/, decoration, faded by the game, plaster W / S swapped per building as before):
  town_front_tall<k>_<s>.png   k = 1, 2, 3, 5 (80, 88, 96, 88 x 432), s = a .. f
  town_front_tall6_<s>.png     the guild house (148 x 432): build_highroad's granite ground floor, styled storeys
  town_front_tall7_<s>.png     the loggia's house as one 148 px bay (the portal's carriage gate) with TWO window axes
                               (was the 96 px gate widened by its edge column: one window over 148 px of wall)
  town_drainpipe.png           6 x 432: a zinc downpipe with a collar on every storey and a shoe on the plinth, drawn at
                               a house's right edge (box property `pipe`)

  python3 -I tools/build_dt_facades.py            write them
  python3 -I tools/build_dt_facades.py --check    fail if a file on disk differs from the build
  python3 -I tools/build_dt_facades.py --sheet P  one bay of every style at 4x, and the parts
"""
import os, sys, argparse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_tall_fronts as TF
import build_highroad as HR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")
FH = 432                                     # the full front: rows 0-279 the two upper storeys, 280-431 the ground floor
STOREY = 140

# the fronts' ramps (TF.C) plus the new materials, each set from its on-screen value after the back fade (28 %) and
# the look shader, like the fronts' own (art/dt-sample-05nov review round 1)
C = dict(TF.C)
C.update(
    P=(172, 28, 34), Q=(220, 72, 58),        # geranium red, its lit petals
    E=(54, 98, 40), O=(34, 66, 30),          # geranium leaves, their shade
    Y=(168, 128, 52),                        # gilt (the sign's picture, the anchors' none)
)
SHOP = {"green": ((56, 88, 70), (84, 120, 94)), "oxblood": ((96, 44, 40), (128, 66, 56)),
        "blue": ((50, 70, 100), (76, 100, 132)), "ink": ((40, 56, 52), (62, 82, 74))}

STYLES = {
    "a": dict(heads=("tri", "hood"), shutters=False, boxes=(1,), anchors=True, cornice="dentil", shop="green", sign="boot"),
    "b": dict(heads=("seg", "seg"), shutters=False, boxes=(), anchors=False, cornice="double", shop="oxblood", sign="cup"),
    "c": dict(heads=("hood", "hood"), shutters=True, boxes=(1,), anchors=False, cornice="plain", shop="blue", sign=None),
    "d": dict(heads=("ear", "hood"), shutters=False, boxes=(), anchors=True, cornice="dentil", shop="ink", sign="key"),
    "e": dict(heads=("hood", "hood"), shutters=False, boxes=(1, 2), anchors=True, cornice="double", shop="green", sign="fish"),
    "f": dict(heads=("tri", "tri"), shutters=False, boxes=(), anchors=True, cornice="plain", shop="oxblood", sign=None),
}

class G:
    """a role grid (one letter per pixel, '.' transparent), as the fronts' Canvas but any height"""
    def __init__(self, w, h, fill="W"):
        self.w, self.h = w, h
        self.a = np.full((h, w), fill, dtype="<U1")
    def put(self, x, y, r):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = r
    def rect(self, x0, y0, x1, y1, r):
        if x1 < x0 or y1 < y0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = r
    def stamp(self, rows, x, y):
        for dy, rr in enumerate(rows):
            for dx, ch in enumerate(rr):
                if ch != ".": self.put(x + dx, y + dy, ch)

# ---- parts, drawn once ------------------------------------------------------------------------------------------
def glazing(g, x0, y0):
    """the 5 Nov upper window's frame and panes (44 x 74: three across, three down, 2 px bars, a lit left column)"""
    x1, y1 = x0 + 43, y0 + 73
    g.rect(x0, y0, x1, y1, "F")
    for px in (x0 + 2, x0 + 16, x0 + 30):
        for py in (y0 + 2, y0 + 26, y0 + 50):
            g.rect(px, py, px + 11, py + 21, "G"); g.rect(px, py, px, py + 21, "R")

def surround(g, x0, y0, ears=False):
    """the 3 px stone surround (lit top and left, shade right) and its 2 px cast shadow; `ears`: the top corners
    stepped out 3 px for 6 rows (the eared architrave), a keystone in the head"""
    x1, y1 = x0 + 43, y0 + 73
    g.rect(x0 - 3, y0 - 3, x1 + 3, y1, "T")
    g.rect(x0 - 3, y0 - 3, x1 + 3, y0 - 3, "L"); g.rect(x0 - 3, y0 - 3, x0 - 3, y1, "L")
    g.rect(x1 + 3, y0 - 2, x1 + 3, y1, "V")
    g.rect(x1 + 4, y0 - 3, x1 + 5, y1 + 6, "S")
    if ears:
        for sx0, sx1 in ((x0 - 6, x0 - 4), (x1 + 4, x1 + 6)):
            g.rect(sx0, y0 - 3, sx1, y0 + 6, "T")
            g.rect(sx0, y0 - 3, sx1, y0 - 3, "L")
        g.rect(x0 - 6, y0 - 3, x0 - 6, y0 + 6, "L"); g.rect(x0 - 6, y0 + 7, x0 - 4, y0 + 7, "V")
        g.rect(x1 + 6, y0 - 2, x1 + 6, y0 + 6, "V"); g.rect(x1 + 4, y0 + 7, x1 + 6, y0 + 7, "V")
        g.rect(x1 + 7, y0 - 3, x1 + 8, y0 + 9, "S")
        keystone(g, (x0 + x1 + 1) // 2, y0 - 6)

def keystone(g, cx, ytop):
    """a keystone 8 wide, 9 high, tapering: lit top and left, shade right"""
    for i in range(9):
        hw = 4 if i < 6 else 3
        g.rect(cx - hw, ytop + i, cx + hw - 1, ytop + i, "T")
        g.put(cx - hw, ytop + i, "L"); g.put(cx + hw - 1, ytop + i, "V")
    g.rect(cx - 4, ytop, cx + 3, ytop, "L"); g.rect(cx - 3, ytop + 9, cx + 2, ytop + 9, "V")

def head_hood(g, x0, y0):
    x1 = x0 + 43
    g.rect(x0 - 6, y0 - 7, x1 + 6, y0 - 7, "L")
    g.rect(x0 - 6, y0 - 6, x1 + 6, y0 - 5, "T")
    g.rect(x0 - 6, y0 - 4, x1 + 6, y0 - 4, "V")
    g.rect(x1 + 7, y0 - 6, x1 + 8, y0 - 3, "S")

def head_tri(g, x0, y0):
    """a small triangular pediment: the hood's three bands as its base (56 wide), a raking cornice 2 px thick rising
    1 px every 2 px to a 10 px apex, the tympanum in the plaster's shade, its cast shadow on the right"""
    x1 = x0 + 43
    head_hood(g, x0, y0)
    base, l, r = y0 - 8, x0 - 6, x1 + 6
    cx = (l + r) / 2
    for x in range(l, r + 1):
        d = min(x - l, r - x)
        top = base - min(10, d // 2)
        g.rect(x, top, x, base, "T")
        g.put(x, top, "L" if x <= cx else "T")
        if x > cx: g.put(x, top + 1, "V")
        if top + 2 <= base - 1 and d // 2 >= 2: g.rect(x, top + 2, x, base - 1, "S" if d // 2 > 2 else "T")
    for x in range(l, r + 1):                                         # the raking cornice's lower edge, the tympanum
        d = min(x - l, r - x)
        top = base - min(10, d // 2)
        if top + 2 <= base - 1: g.put(x, top + 2, "V" if x > cx else "T")
    g.rect(l, base, r, base, "V")
    for x in range(int(cx) + 1, r + 3):                                # cast shadow right of the rake
        d = r - x
        top = base - min(10, max(0, d) // 2) + 1
        if x > r: top = base - 2
        for y in range(top, base + 1):
            if g.a[y, x] == "W": g.put(x, y, "S")

def head_seg(g, x0, y0):
    """a segmental stone arch over the window: a ring 4 px thick, rising 8 px, voussoir joints, a keystone"""
    x1 = x0 + 43
    l, r = x0 - 3, x1 + 3
    cx = (l + r + 1) / 2
    half = (r - l + 1) / 2
    R = (half * half + 64) / 16                                       # the circle through the ends and the 8 px crown
    for x in range(l, r + 1):
        dx = x + 0.5 - cx
        k = int(round(8 - (R - np.sqrt(max(0.0, R * R - dx * dx)))))
        top = y0 - 4 - k
        g.rect(x, top, x, y0 - 3, "T")
        g.put(x, top, "L" if dx < 0 else "T")
        g.put(x, y0 - 3, "V")
        if dx > 0: g.put(x, top + 1, "V")
    for i, jx in enumerate((l + 9, l + 18, r - 18, r - 9)):           # the joints
        dx = jx + 0.5 - cx
        k = int(round(8 - (R - np.sqrt(max(0.0, R * R - dx * dx)))))
        g.rect(jx, y0 - 3 - k, jx, y0 - 4, "V")
    keystone(g, int(cx), y0 - 14)
    for x in range(r + 1, r + 3): g.rect(x, y0 - 8, x, y0 - 2, "S")

SHUTTER_W = 12
def shutter(g, x, y0, h):
    """a louvred oak shutter: a lit frame left and top, shade right and bottom, slats on a 3 px pitch"""
    g.rect(x, y0, x + SHUTTER_W - 1, y0 + h - 1, "K")
    for y in range(y0 + 3, y0 + h - 3, 3): g.rect(x + 2, y, x + SHUTTER_W - 3, y, "D")
    g.rect(x, y0, x + SHUTTER_W - 1, y0, "J"); g.rect(x, y0, x, y0 + h - 1, "J")
    g.rect(x + SHUTTER_W - 1, y0 + 1, x + SHUTTER_W - 1, y0 + h - 1, "D"); g.rect(x + 1, y0 + h - 1, x + SHUTTER_W - 1, y0 + h - 1, "D")
    g.rect(x + 1, y0 + h // 2, x + SHUTTER_W - 2, y0 + h // 2, "J")   # the middle rail

# the geranium motif, 8 px, repeated along a window box: P petal, Q lit petal, E leaf, O leaf shade
GERANIUM = ["..QP....",
            ".QPPP.Q.",
            "EPPPEQPP",
            "EEPEEPPP",
            "OEEEOEPE",
            "OOEOOEEO"]
def window_box(g, cx, ytop, w=46):
    """an oak window box 7 rows high under a sill, geraniums 6 rows above it (in front of the sill and the glass foot)"""
    x0 = cx - w // 2
    for i in range(w // 8 + 1):
        for dy, rr in enumerate(GERANIUM):
            for dx, ch in enumerate(rr):
                x = x0 + 1 + i * 8 + dx
                if ch != "." and x0 + 1 <= x <= x0 + w - 2: g.put(x, ytop - 6 + dy, ch)
    g.rect(x0, ytop, x0 + w - 1, ytop + 6, "K")
    g.rect(x0, ytop, x0 + w - 1, ytop, "J"); g.rect(x0, ytop, x0, ytop + 6, "J")
    g.rect(x0 + w - 1, ytop + 1, x0 + w - 1, ytop + 6, "D"); g.rect(x0, ytop + 6, x0 + w - 1, ytop + 6, "D")
    for x in range(x0 + 11, x0 + w - 4, 12): g.rect(x, ytop + 2, x, ytop + 5, "D")   # the planks' joints
    g.rect(x0 + 2, ytop + 7, x0 + w + 1, ytop + 7, "S")               # its shadow

ANCHOR = [".I..I.",                           # a wrought-iron wall anchor (ankarjarn): a bar with scrolled ends, 6 x 15
          "I.II.I",
          "..II..", "..II..", "..II..", "..II..", "..II..", "..II..", "..II..", "..II..", "..II..",
          "..II..",
          "..II..",
          "I.II.I",
          ".I..I."]
ANCHOR_DX = 31                               # either side of a window axis, clear of a pediment (28) and inside 70 px

PICTURES = {                                  # the hanging signs' pictures, 10 x 8, gilt on the plate (no letters)
    "boot": ["..YYY.....", "..YYY.....", "..YYY.....", "..YYY.....", "..YYYY....", "..YYYYYYY.", "..YYYYYYYY", "..YYYYYYYY"],
    "cup":  ["..Y..Y....", "...Y..Y...", "..........", "YYYYYYY...", "YYYYYYYYY.", "YYYYYYY.Y.", ".YYYYYYY..", "..YYYYY..."],
    "key":  [".YYY......", "Y...Y.....", "Y...YYYYYY", "Y...Y..Y.Y", ".YYY...Y.Y", "..........", "..........", ".........."],
    "fish": ["..........", "...YYYY..Y", ".YYYYYYYYY", "YY.YYYYYY.", "YYYYYYYYY.", ".YYYYYYYYY", "...YYYY..Y", ".........."],
}
def hanging_sign(g, cx, y, pic):
    """a wrought-iron bracket over a door (an arm with a scroll under it) and a plate on two short chains: an iron
    frame round a dark plate with a gilt picture"""
    ax0, ax1 = cx - 13, cx + 12
    g.rect(ax0, y, ax1, y, "I")                                       # the arm, its wall plate, the scroll under it
    g.rect(ax0, y - 2, ax0 + 1, y + 6, "I")
    g.stamp(["I.....", ".I....", "..II..", "....II", ".....I"], ax0 + 2, y + 1)
    g.rect(ax1, y - 1, ax1, y + 1, "I")
    for chx in (cx - 7, cx + 6): g.rect(chx, y + 1, chx, y + 3, "I")   # the chains
    px0, py0 = cx - 8, y + 4                                          # the plate 16 x 12
    g.rect(px0, py0, px0 + 15, py0 + 11, "I")
    g.rect(px0 + 1, py0 + 1, px0 + 14, py0 + 10, "D")
    for dy, rr in enumerate(PICTURES[pic]):
        for dx, ch in enumerate(rr):
            if ch == "Y": g.put(px0 + 3 + dx, py0 + 2 + dy, "Y")
    g.rect(px0 + 2, py0 + 12, px0 + 17, py0 + 12, "S")                # its shadow on the wall

def course(g, y, kind):
    """a storey's string course / the ground floor's cornice: the fronts' 7 rows (lit, three mid, dark lip, two rows
    of shadow); 'dentil' cuts a row of dentils (2 px blocks on a 4 px pitch) into the lip, 'double' adds a fillet
    over it"""
    w = g.w
    g.rect(0, y, w - 1, y, "L"); g.rect(0, y + 1, w - 1, y + 3, "T"); g.rect(0, y + 4, w - 1, y + 4, "V")
    g.rect(0, y + 5, w - 1, y + 6, "S")
    if kind == "dentil":
        g.rect(0, y + 4, w - 1, y + 5, "V")
        for x in range(1, w, 4): g.rect(x, y + 4, x + 1, y + 4, "T")
        g.rect(0, y + 6, w - 1, y + 7, "S")
    elif kind == "double":
        g.rect(0, y + 2, w - 1, y + 2, "L")
        g.rect(0, y - 1, w - 1, y - 1, "S")

# ---- a bay's two upper storeys ------------------------------------------------------------------------------------
def window(g, cx, y0, head, st, storey):
    x0 = cx - 22
    surround(g, x0, y0, ears=(head == "ear"))
    if st["shutters"]:
        for sx in (x0 - 3 - SHUTTER_W, x0 + 44 + 3):
            shutter(g, sx, y0 - 2, 76)
        g.rect(x0 + 44 + 3 + SHUTTER_W, y0 - 2, x0 + 44 + 4 + SHUTTER_W, y0 + 75, "S")
    glazing(g, x0, y0)
    if head == "hood": head_hood(g, x0, y0)
    elif head == "tri": head_tri(g, x0, y0)
    elif head == "seg": head_seg(g, x0, y0)
    y1 = y0 + 73                                                      # the sill (the fronts' own rows)
    g.rect(x0 - 5, y1 + 1, x0 + 48, y1 + 1, "L"); g.rect(x0 - 5, y1 + 2, x0 + 48, y1 + 3, "T")
    g.rect(x0 - 5, y1 + 4, x0 + 48, y1 + 4, "V"); g.rect(x0 - 4, y1 + 5, x0 + 50, y1 + 6, "S")
    if storey in st["boxes"]: window_box(g, cx, y1 + 5)

def upper(w, xs, st):
    """rows 0-279: the second floor (storey 2, rows 0-139) and the first floor (storey 1, rows 140-279), each under
    its course, a window on every axis in xs"""
    g = G(w, 280)
    course(g, 0, st["cornice"]); course(g, STOREY, st["cornice"])
    for k, storey in ((0, 2), (1, 1)):
        head = st["heads"][0 if storey == 1 else 1]
        for cx in xs:
            window(g, cx, k * STOREY + 26, head, st, storey)
            if st["anchors"]:
                for ax in (cx - ANCHOR_DX - 4, cx + ANCHOR_DX - 1):
                    if 1 <= ax and ax + 6 <= w - 1: g.stamp(ANCHOR, ax, k * STOREY + 10)
    return g.a

def ground(k, w, st):
    """rows 280-431: the 5 Nov ground floor bay k (TF fronts 1-3, HR plain 5), its cornice in the style, the shop's
    paint swapped, a hanging sign over a door"""
    if k == 5: a = HR.ground_floor_plain(w).copy()
    else: a = TF.FRONTS[k](w).role[TF.CORNICE:].copy()
    g = G(w, a.shape[0]); g.a = a
    g.rect(0, 0, w - 1, 7, "W"); course(g, 0, st["cornice"])
    if k == 1 and st["sign"]: hanging_sign(g, w // 2, 13, st["sign"])
    return g.a

def colours(st):
    c = dict(C)
    c["N"], c["M"] = SHOP[st["shop"]]
    return c

def render(a, c):
    im = np.zeros((a.shape[0], a.shape[1], 4), np.uint8)
    for r, rgb in c.items():
        im[a == r] = (*rgb, 255)
    return im

def front(k, s):
    st = STYLES[s]
    if k == 6:                                                        # the guild house: build_highroad's ground floor
        g = HR.front_guild(); a = g.a.copy()
        a[:280] = upper(148, HR.UPPER_X, dict(st, shutters=False))
        return render(a, colours(st))
    if k == 7:                                                        # the loggia's house: one 148 px portal bay
        w = 148
        gate = TF.front_gate(w).role[TF.CORNICE:].copy()
        g = G(w, gate.shape[0]); g.a = gate; g.rect(0, 0, w - 1, 7, "W"); course(g, 0, st["cornice"])
        return render(np.vstack([upper(w, [40, 108], st), g.a]), colours(st))
    w = TF.WIDTHS.get(k, 88)
    return render(np.vstack([upper(w, [w // 2], st), ground(k, w, st)]), colours(st))

def drainpipe():
    """a zinc downpipe 4 px (lit, two mid, shade) and its 2 px shadow, a collar every 46 px (a metre), a shoe on the
    plinth that turns out to the street (rows 422-431)"""
    g = G(6, FH, ".")
    Z = dict(L="L", T="T", V="V")
    g.rect(0, 0, 0, FH - 11, "L"); g.rect(1, 0, 2, FH - 11, "T"); g.rect(3, 0, 3, FH - 11, "V"); g.rect(4, 0, 5, FH - 11, "S")
    for y in range(20, FH - 14, 46):
        g.rect(0, y, 4, y + 1, "V"); g.rect(0, y, 4, y, "T")
    g.rect(0, FH - 10, 5, FH - 7, "T"); g.rect(0, FH - 10, 5, FH - 10, "L"); g.rect(0, FH - 7, 5, FH - 7, "V")
    g.rect(0, FH - 10, 0, FH - 7, "L")
    return render(g.a, C)

def build():
    out = {}
    for s in STYLES:
        for k in (1, 2, 3, 5, 6, 7):
            out[f"town_front_tall{k}_{s}"] = front(k, s)
    out["town_drainpipe"] = drainpipe()
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    o = ap.parse_args()
    ims = build(); bad = 0
    for n, im in ims.items():
        p = os.path.join(OUT, n + ".png")
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        assert ncol <= 20, (n, ncol)
        if n.startswith("town_front_tall") and not n.startswith("town_front_tall6"):
            for col in (0, im.shape[1] - 1):                          # the edge columns: plain (the game repeats them)
                assert set(map(tuple, im[:, col, :3].tolist())) <= {C[k] for k in "WSLTV"}, (n, col)
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(n, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{n}: {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z, pad = 4, 12
        names = [f"town_front_tall1_{s}" for s in STYLES]
        ims2 = [ims[n][130:432] for n in names]
        Wd = sum(v.shape[1] * z + pad for v in ims2) + pad
        sheet = Image.new("RGBA", (Wd, 302 * z + 2 * pad), (60, 60, 66, 255)); x = pad
        for v in ims2:
            sheet.alpha_composite(Image.fromarray(v).resize((v.shape[1] * z, v.shape[0] * z), Image.NEAREST), (x, pad)); x += v.shape[1] * z + pad
        sheet.save(o.sheet)
    sys.exit(1 if bad else 0)
