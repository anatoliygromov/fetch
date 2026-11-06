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

art/dt-roofs-06nov: the pieces the game draws (ledge, galleries, loggia, flower roof, footbridge) are redrawn in the
Downtown sample screen's ramps (tools/build_dt_street.py: ink 18, 18, 26; granite 135 / 110 / 77; every colour from
art/palettes/downtown.gpl), about 103 on screen like town_portal_top, below the houses' 145 to 152, so arthooks.lua's
draw-time tint is off. Ledge: a 6 row slab, one modillion per 8 px tile. Galleries: an 8 x 20 vase baluster on a 10 px
pitch. Footbridge: posts on the deck joints, a 4 px arch (ink, lit, iron, ink), hangers every 16 px. The chimney,
dormer and gable are not drawn while the sample screen's first floor is on (H.FIRST_FLOOR) and keep their 23 Oct art.
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
    # (art/dt-roofs-06nov) the redrawn pieces take the Downtown sample screen's ramps, every colour from
    # art/palettes/downtown.gpl: the obstacles' ink and granite of town_portal_top / town_oriel (tools/build_dt_street.py)
    "ink": (18, 18, 26),
    "g1": (135, 130, 120), "g2": (110, 103, 95), "g3": (77, 72, 68), "g4": (58, 50, 56), "g5": (42, 36, 42),   # granite, recess
    "s1": (132, 146, 156), "s2": (88, 100, 112), "s3": (64, 74, 86), "s4": (46, 54, 64),                       # iron (the shelter's steel)
    "o1": (136, 92, 60), "o2": (104, 66, 44), "o3": (68, 44, 32),                                              # oak (the fronts' doors)
    "t1": (207, 123, 82), "t2": (122, 59, 42),                                                                 # terracotta
    "f1": (247, 134, 113), "f2": (206, 53, 49), "fy": (244, 204, 105),                                         # geraniums, a yellow
    "l1": (96, 146, 84), "l2": (70, 112, 66), "l3": (43, 74, 56),                                              # leaves
}

class Cv:
    def __init__(self, w, h): self.w, self.h = w, h; self.a = np.full((h, w), ".", dtype="<U3")
    def put(self, x, y, r):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = r
    def rect(self, x0, y0, x1, y1, r):
        if x1 < x0 or y1 < y0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = r
    def stamp(self, rows, x, y):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".": self.put(x + dx, y + dy, ch)
    def outline(self, ink="K"):
        """ink every opaque pixel that touches transparency or the image edge (4-neighbours)"""
        op = self.a != "."
        pad = np.pad(op, 1, constant_values=False)
        edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        self.a[edge] = ink
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

# ---- the pieces redrawn on art/dt-roofs-06nov (the sample screen's ramps and ink, every part drawn once) ------------
# Light from the upper left: a lit top row (g1), the stone (g2), its shade (g3) on the right and under; recesses g4/g5.
def keyed(cv, rows, key, x, y):
    """stamp a part drawn as rows of characters, each mapped to a colour key ('.' stays as it is)"""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch != ".": cv.put(x + dx, y + dy, key[ch])

def stone_band(cv, x0, x1, y0, rows):
    """a moulded stone band's front, rows y0 .. y0 + rows - 1: lit top, stone, a shade row"""
    cv.rect(x0, y0, x1, y0, "g1"); cv.rect(x0, y0 + 1, x1, y0 + rows - 2, "g2"); cv.rect(x0, y0 + rows - 1, x1, y0 + rows - 1, "g3")

# the stone ledge, a 3-slice (arthooks.lua threeSlice: the left 4 px, the middle 8 repeated, the right 4): a slab 6 rows
# deep (0.13 m) on one modillion per 8 px, 3 rows under it
LEDGE_L = ["kkkk", "kaaa", "kabb", "kabb", "kccc", "kkkk", "....", "....", "...."]
LEDGE_M = ["kkkkkkkk", "aaaaaaaa", "bbbbbbbb", "bbbbbbbb", "cccccccc", "kkkabckk", "..kabck.", "..kbcck.", "..kkkkk."]
LEDGE_R = ["kkkk", "aack", "bbck", "bbck", "ccck", "kkkk", "....", "....", "...."]
STONE_KEY = {"k": "ink", "a": "g1", "b": "g2", "c": "g3", "d": "g4", "e": "g5"}

def ledge():
    cv = Cv(16, 9)
    keyed(cv, LEDGE_L, STONE_KEY, 0, 0); keyed(cv, LEDGE_M, STONE_KEY, 4, 0); keyed(cv, LEDGE_R, STONE_KEY, 12, 0)
    return cv

# a vase baluster, 10 x 20, drawn once: a block under the rail, a neck, the belly (lit on the left), a neck, a foot.
# (fix round 1, 6 Nov: the 10 px pitch left slivers at the 72 gallery's ends.) Pedestals 10, balusters 10, every gap 6
# at the belly, ends included: a pitch of 16 fits both galleries whole (90 = 2 x 10 + 4 x 16 + 6, 74 = 2 x 10 + 3 x 16 + 6)
BAL_W = [10, 10, 8, 6, 6, 6, 8, 8, 10, 10, 10, 10, 10, 8, 6, 6, 8, 10, 10, 10]
def baluster_rows():
    rows = []
    for i, w in enumerate(BAL_W):
        lit = 2 if 8 <= i <= 11 else 1                                # the belly's lit side is 2 px
        core = "k" + "a" * lit + "b" * (w - 3 - lit) + "c" + "k"
        if i == len(BAL_W) - 1: core = "k" + "b" * (w - 4) + "cc" + "k"   # the foot's base in shade
        pad = (10 - w) // 2
        rows.append("." * pad + core + "." * pad)
    return rows
BALUSTER10 = baluster_rows()
GAL_PED, GAL_PITCH, GAL_GAP = 10, 16, 6

def gallery(w):
    """a balustrade 32 rows (0.7 m): the handrail (rows 0-5, Pepper's edge), vase balusters on a 16 px pitch with the
    same 6 px gap at the ends as between them, the plinth (rows 26-31), a pedestal with a sunk panel at each end"""
    cv = Cv(w, 32)
    cv.rect(0, 0, w - 1, 5, "g2"); stone_band(cv, 1, w - 2, 1, 4)
    cv.rect(0, 26, w - 1, 31, "g2"); stone_band(cv, 1, w - 2, 27, 4)
    P = GAL_PED
    for px in (0, w - P):                                             # the end pedestals
        cv.rect(px, 0, px + P - 1, 31, "g2"); cv.rect(px + 1, 1, px + 1, 30, "g1"); cv.rect(px + P - 2, 1, px + P - 2, 30, "g3")
        cv.rect(px + 1, 1, px + P - 2, 1, "g1")
        cv.rect(px + 3, 8, px + P - 4, 22, "g3"); cv.rect(px + 3, 23, px + P - 4, 23, "g1")   # the sunk panel, its lit sill
    span = w - 2 * P
    n = (span - GAL_GAP) // GAL_PITCH
    assert n * GAL_PITCH + GAL_GAP == span, (w, span)                  # whole balusters, equal gaps
    for i in range(n): keyed(cv, BALUSTER10, STONE_KEY, P + GAL_GAP + i * GAL_PITCH, 6)
    cv.outline("ink")
    return cv

def loggia():
    """a cornice (rows 0-6, a dentil course) over a blind arcade of five round arches on a 24 px pitch, a sill"""
    W, Hh = 122, 26
    cv = Cv(W, Hh)
    cv.rect(0, 0, W - 1, Hh - 1, "g2")
    stone_band(cv, 1, W - 2, 1, 4)                                    # the cornice
    cv.rect(1, 5, W - 2, 6, "g3")                                     # dentils: blocks of 2 on a 4 px grid, in shade
    for x in range(2, W - 2, 4): cv.rect(x, 5, x + 1, 5, "g2")
    cv.rect(1, 7, W - 2, 7, "g4")                                     # the cornice's shadow on the wall
    R = 8
    for i in range(5):
        a0 = 5 + i * 24; cx = a0 + 8                                  # the opening 16 wide (a0 .. a0 + 15), the crown at row 9
        spring = 9 + R
        for y in range(9, 22):
            for x in range(a0 - 1, a0 + 17):
                dx = x + 0.5 - cx
                inside = (y >= spring and a0 <= x <= a0 + 15) or (y < spring and np.hypot(dx, y + 0.5 - spring) < R)
                ring = (not inside) and ((y >= spring and x in (a0 - 1, a0 + 16)) or (y < spring and np.hypot(dx, y + 0.5 - spring) < R + 1))
                if inside: cv.put(x, y, "g5" if (y < spring - 3 or x < a0 + 2) else "g4")   # the recess, its shadow
                elif ring: cv.put(x, y, "g1" if dx < 0 else "g3")       # the arch's ring: lit on the left, shade right
    stone_band(cv, 1, W - 2, 22, 3)                                   # the sill
    cv.outline("ink")
    return cv

# geraniums along a flower box, 12 wide, rows over the box: blooms (light, red), leaves (light, mid, dark)
FLOWERS6 = [".pr.....pr..", ".prr....prr.", "mrrrmmmmrrrm", "llmmllmmllmm"]   # (no lone pixels)
FLOWER_KEY = {"p": "f1", "r": "f2", "l": "l1", "m": "l2", "d": "l3", "y": "fy"}

def flower_roof():
    """a stone ledge (rows 0-5) with five terracotta window boxes hung on its front, geraniums in them (never over
    the ledge's top: Pepper walks there)"""
    cv = Cv(90, 14)
    cv.rect(0, 0, 89, 5, "g2"); stone_band(cv, 1, 88, 1, 4)
    for i in range(5):                                                # five boxes 14 wide, 3 px apart, centred
        bx = 4 + i * 17
        cv.rect(bx, 6, bx + 13, 13, "t2"); cv.rect(bx, 6, bx + 13, 6, "t1"); cv.rect(bx + 13, 7, bx + 13, 12, "o3")
        cv.rect(bx, 12, bx + 13, 12, "o3")
        keyed(cv, FLOWERS6, FLOWER_KEY, bx + 1, 2)                    # rows 2-5, in front of the ledge's face
    cv.outline("ink")
    return cv

def footbridge():
    """an iron footbridge 162 x 52: the railing (rows 0-11, behind Pepper: a top rail, bars every 4 px, posts on the
    deck's joints), the oak deck (its outline row 12 = the box's top - 1), an iron arch from wall to wall with hangers"""
    W, Hh = 162, 52
    cv = Cv(W, Hh)
    # the deck, rows 12-19: an oak edge beam, plank joints every 16 px
    cv.rect(0, 12, W - 1, 19, "o2"); cv.rect(1, 13, W - 2, 13, "o1"); cv.rect(1, 18, W - 2, 18, "o3")
    for x in range(16, W - 2, 16): cv.rect(x, 14, x, 17, "o3")
    # the railing: a top rail (rows 0-3: ink, lit, iron, ink), 1 px bars (rows 4-11) every 4 px, a 4 px post at each
    # end and every 32 px, on the deck's joints
    cv.rect(0, 0, W - 1, 3, "s3"); cv.rect(1, 1, W - 2, 1, "s2")
    for x in range(4, W - 3, 4): cv.rect(x, 4, x, 11, "s3")
    for x in [0] + list(range(31, W - 8, 32)) + [W - 4]:
        cv.rect(x, 0, x + 3, 11, "s3"); cv.rect(x + 1, 1, x + 1, 11, "s2")
    # the arch: a 3 px iron band from the walls (row 46) up to the deck's underside at the middle
    def arch_y(x): return 20 + 26 * (2 * (x + 0.5) / W - 1) ** 2
    for x in range(0, W):
        y = int(round(arch_y(x)))
        cv.rect(x, y, x, y + 3, "s3"); cv.put(x, y + 1, "s2")
    for x in range(12, W - 8, 16):                                    # hangers between the arch and the deck
        for hx in (x, W - 1 - x):
            y = int(round(arch_y(hx)))
            if y > 22: cv.rect(hx, 20, hx, y - 1, "s3")
    cv.rect(0, 44, 2, 51, "s3"); cv.rect(W - 3, 44, W - 1, 51, "s3")  # the springing plates on the walls
    cv.outline("ink")
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
