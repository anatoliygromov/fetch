"""tools/build_roof_kit.py: the tall Downtown's high road pieces (art/scene/town_roof_*.png, town_footbridge.png;
docs/art_hooks_r8.md), BUILT from stamped parts (art/placement, 23 Oct 2026; docs/BIBLE.md section 3).

  python3 -I tools/build_roof_kit.py              write every piece
  python3 -I tools/build_roof_kit.py --check      fail if a file on disk is not what this script builds
  python3 -I tools/build_roof_kit.py --sheet P    every piece at 4x on one sheet

They are obstacles on Pepper's line: crisp, an unbroken 1 px dark outline, front-on with a thin top (the top row is
the outline over the edge she walks on, one row above the box's top), true scale (46 px a metre). Each repeated part
(a baluster, a brick, a modillion, a voussoir, a flower box, a railing bar, a strut) is drawn once and stamped on an
integer grid. One granite ramp for all stone (the house fronts' own, tools/build_tall_fronts.py), light from the upper
left: lit top and left edges, the shade on the right and under. Sizes: the hooks' widths; the heights are the
shallow ones the true-scale house fronts need (a piece hanging lower would cover the doors under the roofline):
  town_roof_ledge.png          16 x 9    3-slice (left 4, middle 8 repeated, right 4): a cornice slab on modillions
  town_roof_chimney.png        18 x 46   brick in running bond under a stone cap (no pots over the top row)
  town_roof_gable.png         122 x 40   the guild house's stepped gable: coped brick steps on the 8 x 4 px boxes, an
                                         oculus, a string course at its foot (anchor: top-left at the steps' left - 1,
                                         the highest step's top - 1)
  town_roof_gallery88.png      90 x 32   a balustrade: end pedestals, handrail, vase balusters every 8 px, plinth
  town_roof_gallery72.png      74 x 32
  town_roof_loggia.png        122 x 26   a cornice over a blind arcade of five round arches
  town_roof_dormer.png         58 x 36   a copper roof with standing seams over a dormer window
  town_roof_flower_roof.png    90 x 14   a ledge with five terracotta flower boxes along its front
  town_footbridge.png         162 x 52   iron railing (12 rows, behind Pepper), the deck (its outline row 12), an
                                         iron arch with struts under it
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")

C = {
    "K": (20, 18, 26),                                                   # the outline ink
    "L": (230, 222, 206), "T": (190, 180, 164), "U": (154, 144, 132), "V": (112, 104, 98),   # granite
    "B": (170, 88, 62), "b": (128, 62, 46), "c": (198, 116, 86), "m": (214, 186, 166),       # brick, mortar
    "P": (140, 196, 166), "C": (94, 156, 128), "Q": (62, 110, 90),       # copper (verdigris)
    "W": (222, 198, 152), "S": (184, 156, 114),                         # cream plaster
    "G": (62, 72, 88), "R": (98, 114, 130), "F": (232, 228, 218),        # glass, reflection, frames
    "O": (148, 104, 66), "o": (186, 140, 92), "d": (102, 70, 46),        # oak deck
    "I": (56, 58, 68), "i": (104, 108, 120),                            # iron
    "Z": (70, 62, 68), "z": (98, 88, 92),                               # the arcade's shadowed back wall
    "r": (214, 62, 78), "y": (244, 196, 66), "g": (70, 122, 62), "h": (112, 162, 84),   # flowers, leaves
    "t": (184, 100, 66), "u": (140, 72, 50),                            # terracotta
}

class Cv:
    def __init__(self, w, h): self.w, self.h = w, h; self.a = np.full((h, w), ".", dtype="<U1")
    def put(self, x, y, r):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = r
    def rect(self, x0, y0, x1, y1, r):
        if x1 < x0 or y1 < y0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = r
    def stamp(self, rows, x, y):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".": self.put(x + dx, y + dy, ch)
    def outline(self):
        """ink every opaque pixel that touches transparency or the image edge (4-neighbours)"""
        op = self.a != "."
        pad = np.pad(op, 1, constant_values=False)
        edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        self.a[edge] = "K"
    def image(self):
        im = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y, x] != ".": im[y, x] = (*C[self.a[y, x]], 255)
        return im

def slab(cv, x0, x1, y):
    """a stone slab's front: lit top, two mid rows, a shade row (rows y .. y + 3), inked later"""
    cv.rect(x0, y, x1, y, "L"); cv.rect(x0, y + 1, x1, y + 2, "T"); cv.rect(x0, y + 3, x1, y + 3, "V")

def brick_wall(cv, mask_fn, x0, x1, y0, y1, gx=0, gy=0):
    """running bond on a global grid: courses of 3 rows and a mortar row, bricks 7 long and a joint, offset by 4"""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not mask_fn(x, y): continue
            row = (y + gy) % 4
            course = (y + gy) // 4
            if row == 3: cv.put(x, y, "m"); continue
            if (x + gx + (4 if course % 2 else 0)) % 8 == 7: cv.put(x, y, "m"); continue
            cv.put(x, y, "c" if row == 0 else ("b" if row == 2 else "B"))

# ---- the pieces ---------------------------------------------------------------------------------------------------
def ledge():
    cv = Cv(16, 9)
    cv.rect(0, 0, 15, 6, "T"); slab(cv, 1, 14, 1); cv.rect(1, 5, 14, 5, "U")
    cv.rect(14, 1, 14, 5, "U")                                        # the right end in shade
    for mx in (6,):                                                   # one modillion per 8 px of the middle
        cv.rect(mx, 6, mx + 3, 8, "U"); cv.rect(mx, 7, mx, 7, "T")
    cv.outline()
    return cv

def chimney():
    cv = Cv(18, 46)
    cv.rect(1, 6, 16, 45, "B")
    brick_wall(cv, lambda x, y: True, 2, 15, 6, 44, gx=1, gy=2)
    cv.rect(2, 6, 2, 44, "c")                                         # lit left edge, shaded right
    cv.rect(14, 6, 15, 44, "b")
    cv.rect(0, 0, 17, 5, "T"); slab(cv, 1, 16, 1)
    cv.rect(2, 6, 15, 6, "b")                                         # the cap's shadow on the brick
    cv.outline()
    return cv

GABLE_TOPS = [29] * 8 + [25] * 8 + [21] * 8 + [17] * 8 + [13] * 8 + [9] * 8 + [5] * 8 + [1] * 40 + [5] * 8 + [9] * 8 + [13] * 8
def gable():
    cv = Cv(122, 40)
    top = [None] + GABLE_TOPS + [None]                                  # local x 1..120 are the steps (box columns)
    assert len(top) == 122
    def t(x): return top[x] if top[x] is not None else top[x - 1 if x > 0 and top[x - 1] is not None else x + 1]
    inside = lambda x, y: 0 < x < 121 and y >= t(x) + 3 and y <= 35
    brick_wall(cv, inside, 0, 121, 0, 35, gx=0, gy=1)
    for x in range(1, 121):                                           # each step's coping: lit, mid, shade
        y = t(x); cv.put(x, y, "L"); cv.put(x, y + 1, "T"); cv.put(x, y + 2, "V")
    for x in range(1, 120):                                           # a riser: the coping turns down the higher step's side
        if t(x + 1) != t(x):
            hx = x if t(x) < t(x + 1) else x + 1                      # the column of the higher step at the join
            lo = max(t(x), t(x + 1))
            for y in range(t(hx), lo + 3): cv.put(hx, y, "L" if hx == x + 1 else "V")
    for y in range(t(1), 36): cv.put(1, y, cv.a[y, 1] if cv.a[y, 1] in ("L", "T", "V") else "c")   # lit left end
    for y in range(t(120), 36): cv.put(120, y, cv.a[y, 120] if cv.a[y, 120] in ("L", "T", "V") else "b")
    slab(cv, 1, 120, 35); cv.rect(1, 38, 120, 38, "V")                # the string course at its foot
    cx, cy = 76, 17                                                   # an oculus in the top block: stone ring, glass
    for y in range(cy - 6, cy + 7):
        for x in range(cx - 6, cx + 7):
            d = np.hypot(x - cx, y - cy)
            if d <= 6.2: cv.put(x, y, "T" if d > 4.2 else ("G" if (x - cx) + (y - cy) > -3 else "R"))
            if 4.2 < d <= 6.2 and x - cx + y - cy < -3: cv.put(x, y, "L")
            if 4.2 < d <= 6.2 and x - cx + y - cy > 4: cv.put(x, y, "V")
    cv.rect(cx, cy - 4, cx, cy + 4, "F"); cv.rect(cx - 4, cy, cx + 4, cy, "F")
    for x in range(1, 121): cv.put(x, t(x) - 1, ".")                  # (room for the outline row over every top)
    cv.a[:, 0] = "."; cv.a[:, 121] = "."
    for x in range(0, 122):                                           # extend down to the foot, then ink round
        tx = t(x) if 0 < x < 121 else (t(1) if x == 0 else t(120))
        for y in range(tx - 1, 40):
            if cv.a[y, x] == ".": cv.put(x, y, "B")
    cv.outline()
    return cv

BALUSTER = [".KTK.", ".KTK.", "KLTUK", "KLTUK", "KLTUK", "KLTUK", "KLTUK", "KLTUK", ".KTK.", ".KTK.", ".KTK.",
            "KLTUK", "KLTUK", "KLTUK", "KLTUK", ".KTK.", ".KTK.", ".KTK.", "KLTUK", "KLTUK"]
def gallery(w):
    cv = Cv(w, 32)
    cv.rect(0, 0, w - 1, 5, "T"); slab(cv, 1, w - 2, 1)                # the handrail (Pepper's edge)
    cv.rect(0, 26, w - 1, 31, "T"); slab(cv, 1, w - 2, 27)            # the plinth
    for px in (0, w - 7):                                             # end pedestals with a sunk panel
        cv.rect(px, 0, px + 6, 31, "T"); cv.rect(px + 1, 1, px + 1, 30, "L"); cv.rect(px + 5, 1, px + 5, 30, "V")
        slab(cv, px + 1, px + 5, 1); cv.rect(px + 2, 8, px + 4, 22, "U"); cv.rect(px + 2, 8, px + 4, 8, "V")
    inner0, inner1 = 7, w - 8
    n = (inner1 - inner0 + 1 - 5) // 8 + 1
    start = inner0 + (inner1 - inner0 + 1 - ((n - 1) * 8 + 5)) // 2
    for i in range(n): cv.stamp(BALUSTER, start + i * 8, 6)
    cv.outline()
    return cv

def loggia():
    cv = Cv(122, 26)
    cv.rect(0, 0, 121, 25, "T")
    slab(cv, 1, 120, 1); cv.rect(1, 5, 120, 5, "U")                   # the cornice
    for x in range(2, 120, 4): cv.rect(x, 7, x + 1, 8, "U")           # dentils under it
    cv.rect(1, 6, 120, 6, "V")
    for i in range(5):                                                # five arches 18 wide between piers of 5
        a0 = 6 + i * 23; a1 = a0 + 17; cxa = (a0 + a1) / 2; r = 9
        for y in range(10, 24):
            for x in range(a0, a1 + 1):
                if y >= 10 + r or np.hypot(x + 0.5 - (cxa + 0.5), y + 0.5 - (10 + r)) < r:
                    cv.put(x, y, "Z" if (y > 19 or x < a0 + 4) else "z")
        for x in range(a0 - 1, a1 + 2):                               # the arch's ring: lit on the left half
            for y in range(9, 10 + r):
                d = np.hypot(x + 0.5 - (cxa + 0.5), y + 0.5 - (10 + r))
                if r <= d < r + 1.2 and cv.a[y, x] == "T": cv.put(x, y, "L" if x < cxa else "V")
        cv.rect(a1 + 1, 10 + r, a1 + 1, 23, "L")                      # the pier's lit left face
        cv.rect(a0 - 1, 10 + r, a0 - 1, 23, "V")
    slab(cv, 1, 120, 22); cv.rect(1, 25, 120, 25, "V")                # the sill under the arcade
    cv.outline()
    return cv

def dormer():
    cv = Cv(58, 36)
    cv.rect(0, 0, 57, 7, "C")                                         # the copper roof: seams every 6 px
    cv.rect(1, 1, 56, 1, "P"); cv.rect(1, 6, 56, 6, "Q")
    for x in range(5, 56, 6): cv.rect(x, 2, x, 5, "Q")
    cv.rect(1, 2, 1, 5, "P")
    x0, x1 = 13, 44                                                   # the dormer's front, 32 wide
    cv.rect(x0, 8, x1, 35, "W")
    cv.rect(x0 + 1, 8, x1 - 1, 8, "S")                                # the roof's shadow on it
    cv.rect(x1 - 1, 9, x1 - 1, 34, "S")
    gx0, gx1, gy0, gy1 = x0 + 6, x1 - 6, 12, 29
    cv.rect(gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1, "F")
    for px0, px1 in ((gx0, (gx0 + gx1) // 2 - 1), ((gx0 + gx1) // 2 + 1, gx1)):
        for py0, py1 in ((gy0, 19), (21, gy1)):
            cv.rect(px0, py0, px1, py1, "G"); cv.rect(px0 + 1, py0, px0 + 1, py1, "R")
    cv.rect(gx0 - 3, gy1 + 2, gx1 + 3, gy1 + 2, "L"); cv.rect(gx0 - 3, gy1 + 3, gx1 + 3, gy1 + 3, "V")   # sill
    cv.outline()
    return cv

FLOWERS = ["..r.y..r..y.", ".rgryhgyrhr.", "ghhgghhgghgh"]
def flower_roof():
    cv = Cv(90, 14)
    cv.rect(0, 0, 89, 6, "T"); slab(cv, 1, 88, 1); cv.rect(1, 5, 88, 5, "U")
    for i in range(5):                                                # five boxes 14 wide, 4 px apart, centred
        bx = 3 + i * 17
        cv.rect(bx, 6, bx + 13, 13, "t"); cv.rect(bx, 6, bx + 13, 6, "c"); cv.rect(bx, 12, bx + 13, 13, "u")
        cv.rect(bx + 13, 7, bx + 13, 12, "u")
        cv.stamp(FLOWERS, bx + 1, 3)                                  # flowers in front of the slab, never over its top
    cv.outline()
    return cv

def footbridge():
    W, Hh = 162, 52
    cv = Cv(W, Hh)
    # the railing (rows 0-11, behind Pepper): a top rail, thin bars every 4 px, posts every 20 px
    cv.rect(1, 1, W - 2, 2, "i"); cv.rect(1, 2, W - 2, 2, "I")
    for x in range(3, W - 2, 4): cv.rect(x, 3, x, 11, "I")
    for x in list(range(1, W - 2, 20)) + [W - 4]:
        cv.rect(x, 1, x + 2, 11, "I"); cv.rect(x, 1, x, 11, "i")
    # the deck (its outline row 12 is the box's top - 1): an oak edge beam with plank ends
    cv.rect(0, 12, W - 1, 19, "O")
    cv.rect(1, 13, W - 2, 13, "o"); cv.rect(1, 18, W - 2, 18, "d")
    for x in range(6, W - 2, 8): cv.rect(x, 14, x, 17, "d")
    # the arch: from the walls at row 47 up to the deck in the middle, 3 px thick iron, struts every 10 px
    def arch_y(x): return 20 + (Hh - 7 - 20) * (2 * (x + 0.5) / W - 1) ** 2
    for x in range(1, W - 1):
        y = int(round(arch_y(x)))
        cv.rect(x, y, x, y + 2, "I"); cv.put(x, y, "i")
    for x in list(range(10, W - 6, 10)):
        y = int(round(arch_y(x)))
        if y > 22: cv.rect(x, 20, x + 1, y - 1, "I"); cv.put(x, 20, "i")
    for x in (1, W - 2):                                              # the springing plates on the walls
        cv.rect(x - 1 if x > 1 else x, Hh - 9, x + 1 if x == 1 else x, Hh - 2, "I")
    cv.outline()
    return cv

PIECES = {"town_roof_ledge": ledge, "town_roof_chimney": chimney, "town_roof_gable": gable,
          "town_roof_gallery88": lambda: gallery(90), "town_roof_gallery72": lambda: gallery(74),
          "town_roof_loggia": loggia, "town_roof_dormer": dormer, "town_roof_flower_roof": flower_roof,
          "town_footbridge": footbridge}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet"); ap.add_argument("names", nargs="*")
    o = ap.parse_args()
    bad, ims = 0, {}
    for n, f in PIECES.items():
        if o.names and n not in o.names: continue
        im = f().image(); ims[n] = im
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        assert ncol <= 20, (n, ncol)
        p = os.path.join(OUT, n + ".png")
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(n, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{n}: {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z = 4; pad = 16
        Wd = max(im.shape[1] for im in ims.values()) * z + 2 * pad
        Ht = sum(im.shape[0] * z + pad for im in ims.values()) + pad
        sheet = Image.new("RGBA", (Wd, Ht), (120, 150, 190, 255)); y = pad
        for im in ims.values():
            sheet.alpha_composite(Image.fromarray(im).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST), (pad, y)); y += im.shape[0] * z + pad
        sheet.save(o.sheet)
    sys.exit(1 if bad else 0)
