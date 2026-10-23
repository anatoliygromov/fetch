"""tools/build_tall_fronts.py: the tall Downtown's house fronts under the high road (art/scene/town_front_tall1-3.png,
80 / 88 / 96 x 240; docs/art_hooks_r8.md), BUILT from stamped parts at true scale (art/placement, 23 Oct 2026;
docs/BIBLE.md section 3: 46 px a metre, the crispness bar, decoration without an outline).

  python3 -I tools/build_tall_fronts.py                 write the three fronts
  python3 -I tools/build_tall_fronts.py --check         fail if the files on disk are not what this script builds
  python3 -I tools/build_tall_fronts.py --parts out.png a sheet of the three at 4x with the role colours

Each front is one bay of a ground floor, 3.1 m high (plinth 0.17 m, the floor 2.95 m), under a stone cornice; the
first floor starts above it. The game shows only the lower 114 to 176 px (each back box is cut at its top, the
roofline the high road runs on, arthooks.lua), so the bays are what counts:
  1  (80 px)  a panelled double door (0.96 x 2.1 m) under a glazed transom, in a stone surround with a keystone
  2  (88 px)  a shop front: painted pilasters, a fascia, a three-pane window (1.1 x 1.7 m) over a panelled riser
  3  (96 px)  a round-arched carriage gate (1.2 m wide, 2.6 m to the crown) in rusticated stone, plank leaves
Every feature is centred and at most 70 px wide; the left and right columns are plain wall, so the game can crop a
bay symmetrically to 70 px or widen it with its own wall column (arthooks.lua). The wall is one flat fill in the
yellow plaster ramp (W, S); the game swaps the ramp per building (red, cream, ochre, stone) by exact colour. Parts
are drawn once (a window, a panel, a rusticated block, a plank) and stamped on integer grids; light from the upper
left: lit stone on top and left edges, shade on the right and under the cornice. No resampling, binary alpha.
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")
H = 240
PLINTH, CORNICE = 232, 88                    # first plinth row; the cornice rows 88-95 (3.1 m over the street)
TOP = 131                                    # every feature starts at or below this row: the lowest box (114 px) shows rows 126 on,
                                             # its coping covers 126-129

# per-material ramps (full local colour; the game fades decoration towards the level's haze)
C = dict(
    W=(214, 168, 104), S=(176, 128, 80),                          # yellow plaster, its shade (swapped per building)
    L=(222, 214, 198), T=(176, 166, 152), V=(116, 108, 102),      # granite: lit, mid, dark
    G=(62, 72, 88), R=(98, 114, 130),                             # glass, its reflection
    F=(228, 224, 214),                                            # window frames and glazing bars
    K=(104, 66, 44), J=(136, 92, 60), D=(68, 44, 32),             # oak: leaf, lit panel edge, shadow / joints
    N=(56, 88, 70), M=(84, 120, 94),                              # painted shopfront green, lit
    I=(52, 50, 54),                                               # iron straps and rings
)

class Canvas:
    def __init__(self, w):
        self.w = w
        self.role = np.full((H, w), "W", dtype="<U1")
    def put(self, x, y, r):
        if 0 <= x < self.w and 0 <= y < H: self.role[y, x] = r
    def rect(self, x0, y0, x1, y1, r):        # inclusive
        if x1 < x0 or y1 < y0: return
        self.role[max(0, y0):min(H, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = r
    def stamp(self, rows, x, y):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".": self.put(x + dx, y + dy, ch)

# ---- parts, drawn once ------------------------------------------------------------------------------------------
def panel(w, h):
    """a raised door panel: lit top and left edge, shadow on the right and bottom, the leaf's colour inside"""
    rows = []
    for y in range(h):
        row = ""
        for x in range(w):
            if y == 0 or x == 0: row += "J"
            elif y == h - 1 or x == w - 1: row += "D"
            else: row += "K"
        rows.append(row)
    return rows

def green_panel(w, h):
    rows = []
    for y in range(h):
        rows.append("".join("M" if (y == 0 or x == 0) else ("D" if (y == h - 1 or x == w - 1) else "N") for x in range(w)))
    return rows

def window_first_floor(cv, cx, sill):
    """the first floor's window (only its lower part fits the file: the game never shows it in this level)"""
    w = 44; x0 = cx - w // 2
    cv.rect(x0, 0, x0 + w - 1, sill - 1, "F")
    for px in (x0 + 2, x0 + 2 + 14, x0 + 2 + 28):                 # three panes of 12 across, bars of 2
        for py0, py1 in ((0, 26), (30, sill - 3)):
            cv.rect(px, py0, px + 11, py1, "G")
            cv.rect(px + 1, py0, px + 1, py1, "R")                  # a reflection on the pane's left
    cv.rect(x0 - 3, sill, x0 + w + 2, sill + 1, "L")               # the sill, lit, then its shadow
    cv.rect(x0 - 3, sill + 2, x0 + w + 2, sill + 2, "S")

def common(cv):
    """wall, cornice, plinth and the first floor's window: the same on every bay"""
    w = cv.w
    cv.rect(0, CORNICE, w - 1, CORNICE, "L")                         # cornice: lit top, mid, dark lip,
    cv.rect(0, CORNICE + 1, w - 1, CORNICE + 3, "T")                 # then its shadow on the wall
    cv.rect(0, CORNICE + 4, w - 1, CORNICE + 4, "V")
    cv.rect(0, CORNICE + 5, w - 1, CORNICE + 6, "S")
    cv.rect(0, PLINTH, w - 1, PLINTH, "L")                           # granite plinth
    cv.rect(0, PLINTH + 1, w - 1, H - 1, "T")
    cv.rect(0, H - 1, w - 1, H - 1, "V")
    for x in range(8 + (w // 2) % 24, w - 4, 24):                    # its joints, on a 24 px grid
        cv.rect(x, PLINTH + 1, x, H - 2, "V")
    window_first_floor(cv, w // 2, 58)

# ---- the three bays ---------------------------------------------------------------------------------------------
def front_door(w=80):
    cv = Canvas(w); common(cv)
    cx = w // 2
    lw, top = 22, TOP + 7                                            # each leaf 22 px; the leaves from row 138
    dx0, dx1 = cx - lw, cx + lw - 1
    # stone surround (4 px) and lintel (6 px) with a keystone in it
    cv.rect(dx0 - 4, TOP, dx1 + 4, PLINTH - 1, "T")
    cv.rect(dx0 - 4, TOP, dx0 - 4, PLINTH - 1, "L"); cv.rect(dx0 - 4, TOP, dx1 + 4, TOP, "L")
    cv.rect(dx1 + 4, TOP + 1, dx1 + 4, PLINTH - 1, "V"); cv.rect(dx0 - 3, TOP + 6, dx1 + 3, TOP + 6, "V")
    cv.rect(cx - 4, TOP, cx + 3, TOP + 8, "T"); cv.rect(cx - 4, TOP, cx + 3, TOP, "L"); cv.rect(cx - 4, TOP, cx - 4, TOP + 8, "L")
    cv.rect(cx + 3, TOP + 1, cx + 3, TOP + 8, "V"); cv.rect(cx - 3, TOP + 8, cx + 3, TOP + 8, "V")
    for y in (156, 180, 204):                                        # the surround's block joints
        cv.rect(dx0 - 3, y, dx0 - 1, y, "V"); cv.rect(dx1 + 1, y, dx1 + 3, y, "V")
    # the two leaves (2.0 m): two raised panels each, the reveal's shadow on top and left, meeting stiles
    cv.rect(dx0, top, dx1, PLINTH - 1, "K")
    for x0 in (dx0, cx):
        cv.rect(x0, top, x0 + lw - 1, top + 1, "D")
        cv.stamp(panel(16, 38), x0 + 3, top + 5)
        cv.stamp(panel(16, 40), x0 + 3, top + 48)
    cv.rect(dx0, top, dx0, PLINTH - 1, "D")
    cv.rect(cx - 1, top, cx, PLINTH - 1, "D")
    cv.rect(cx - 4, top + 44, cx - 3, top + 45, "I"); cv.rect(cx + 2, top + 44, cx + 3, top + 45, "I")   # handles
    cv.rect(dx0 - 2, PLINTH - 1, dx1 + 2, PLINTH - 1, "L")           # the threshold step's nosing
    return cv

def front_shop(w=88):
    cv = Canvas(w); common(cv)
    cx = w // 2
    x0, x1 = cx - 32, cx + 31                                        # the shopfront, 64 px, from row 131
    cv.rect(x0, TOP, x1, PLINTH - 1, "N")
    cv.rect(x0, TOP, x1, TOP, "M"); cv.rect(x0, TOP, x0, PLINTH - 1, "M")
    cv.rect(x1, TOP + 1, x1, PLINTH - 1, "D")
    cv.rect(x0 + 3, TOP + 3, x1 - 3, TOP + 3, "D"); cv.rect(x0 + 3, TOP + 7, x1 - 3, TOP + 7, "M")   # the fascia's moulding
    cv.rect(x0 + 1, TOP + 9, x1 - 1, TOP + 10, "D")                  # under the fascia
    for px in (x0 + 1, x1 - 5):                                      # pilasters (5 px): lit edge, shade edge
        cv.rect(px, TOP + 11, px + 4, PLINTH - 1, "N")
        cv.rect(px, TOP + 11, px, PLINTH - 1, "M"); cv.rect(px + 4, TOP + 11, px + 4, PLINTH - 1, "D")
        cv.rect(px, TOP + 11, px + 4, TOP + 12, "M")                # capitals
    gx0, gx1, gy0, gy1 = x0 + 7, x1 - 7, TOP + 15, 203               # the window: 50 x 58 (1.1 x 1.3 m)
    cv.rect(gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1, "F")
    pw = (gx1 - gx0 + 1 - 4) // 3                                    # three panes, bars of 2
    for i in range(3):
        px0 = gx0 + i * (pw + 2)
        cv.rect(px0, gy0, px0 + pw - 1, gy0 + 9, "G"); cv.rect(px0 + 1, gy0, px0 + 1, gy0 + 9, "R")          # top lights
        cv.rect(px0, gy0 + 12, px0 + pw - 1, gy1, "G"); cv.rect(px0 + 1, gy0 + 12, px0 + 1, gy1, "R")
        cv.rect(px0 + 2, gy0 + 16, px0 + 2, gy0 + 25, "R")          # a second streak, high on the pane
    cv.rect(gx0 - 2, gy1 + 2, gx1 + 2, gy1 + 2, "L")                 # sill
    cv.rect(gx0 - 2, gy1 + 3, gx1 + 2, gy1 + 3, "D")
    cv.stamp(green_panel(gx1 - gx0 + 1, 18), gx0, 210)              # the riser's panel
    return cv

def front_gate(w=96):
    cv = Canvas(w); common(cv)
    cx = w // 2
    r = 28                                                           # the opening: 56 wide, the arch's radius 28
    stone = 6
    ox0, ox1, spring = cx - r, cx + r - 1, TOP + r + stone           # the ring's top on row 131
    # rusticated jambs: blocks 12 px high, long and short in turn (7 and 4 px into the wall), joints dark
    for i, y in enumerate(range(spring, PLINTH, 12)):
        dep = 7 if i % 2 == 0 else 4
        for side in (-1, 1):
            if side < 0: bx0, bx1 = ox0 - dep, ox0 - 1
            else: bx0, bx1 = ox1 + 1, ox1 + dep
            yb = min(y + 11, PLINTH - 1)
            cv.rect(bx0, y, bx1, yb, "T")
            cv.rect(bx0, y, bx1, y, "L"); cv.rect(bx0, y, bx0, yb, "L")
            cv.rect(bx1, y + 1, bx1, yb, "V")
            if yb == y + 11: cv.rect(bx0, yb, bx1, yb, "V")
    # the arch: a stone ring 6 px thick, voussoir joints every 18 degrees, a keystone
    ring = np.zeros((H, w), bool); hole = np.zeros((H, w), bool)
    for y in range(TOP, spring):
        for x in range(w):
            d = np.hypot(x + 0.5 - cx, y + 0.5 - spring)
            if d < r: hole[y, x] = True
            elif d < r + stone: ring[y, x] = True
    for y, x in zip(*np.nonzero(ring)):
        a = np.degrees(np.arctan2(spring - (y + 0.5), (x + 0.5) - cx))           # 0 right .. 180 left
        d = np.hypot(x + 0.5 - cx, y + 0.5 - spring)
        joint = any(abs(a - j) * np.pi / 180 * d < 0.6 for j in range(18, 180, 18)) and abs(a - 90) > 12
        cv.put(x, y, "V" if joint else ("L" if (d > r + stone - 1.3 and a > 80) else "T"))
    kx0, kx1, ky0 = cx - 5, cx + 4, TOP                              # keystone over the crown
    cv.rect(kx0, ky0, kx1, TOP + stone + 2, "T")
    cv.rect(kx0, ky0, kx1, ky0, "L"); cv.rect(kx0, ky0, kx0, TOP + stone + 2, "L")
    cv.rect(kx1, ky0 + 1, kx1, TOP + stone + 2, "V"); cv.rect(kx0 + 1, TOP + stone + 2, kx1, TOP + stone + 2, "V")
    # the leaves: oak planks 7 px wide, iron straps, ring handles; the reveal's shadow on top and left
    for y, x in zip(*np.nonzero(hole)): cv.put(x, y, "K")
    cv.rect(ox0, spring, ox1, PLINTH - 1, "K")
    for x in range(ox0 + 6, ox1, 7):
        for y in range(TOP, PLINTH):
            if cv.role[y, x] == "K": cv.put(x, y, "D")
    for y in range(TOP, PLINTH):                                     # the shadow under the arch
        for x in range(ox0, ox1 + 1):
            if cv.role[y, x] in ("K", "D") and (cv.role[y - 1, x] not in ("K", "D") or cv.role[y - 2, x] not in ("K", "D")):
                cv.put(x, y, "D")
    cv.rect(ox0, spring, ox0 + 1, PLINTH - 1, "D")
    cv.rect(cx - 1, TOP + stone + 3, cx, PLINTH - 1, "D")            # the meeting stiles
    for y in (178, 214):                                             # straps
        cv.rect(ox0 + 3, y, cx - 3, y + 2, "I"); cv.rect(cx + 2, y, ox1 - 3, y + 2, "I")
    for hx in (cx - 6, cx + 2):                                      # ring handles
        cv.stamp([".II.", "I..I", "I..I", ".II."], hx, 194)
    cv.rect(ox0 - 2, PLINTH - 1, ox1 + 2, PLINTH - 1, "L")           # the threshold
    return cv

FRONTS = {1: front_door, 2: front_shop, 3: front_gate}
WIDTHS = {1: 80, 2: 88, 3: 96}

def render(cv):
    im = np.zeros((H, cv.w, 4), np.uint8)
    for y in range(H):
        for x in range(cv.w):
            im[y, x] = (*C[cv.role[y, x]], 255)
    return im

def build():
    return {i: render(FRONTS[i](WIDTHS[i])) for i in FRONTS}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--parts", help="write the three at 4x side by side to this path")
    o = ap.parse_args()
    ims = build()
    bad = 0
    for i, im in ims.items():
        p = os.path.join(OUT, f"town_front_tall{i}.png")
        assert len({tuple(c) for c in im.reshape(-1, 4)}) <= 20, "colours"
        for col in (0, im.shape[1] - 1):                             # the edge columns: plain (the game repeats them)
            assert set(map(tuple, im[64:, col, :3].tolist())) <= {C[k] for k in "WSLTV"}, f"front {i}: a feature on column {col}"
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(p, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(p, im.shape[1], "x", im.shape[0], len({tuple(c) for c in im.reshape(-1, 4)}), "colours")
    if o.parts:
        z = 4; sheet = Image.new("RGBA", (sum(im.shape[1] * z + 20 for im in ims.values()) + 20, H * z + 40), (60, 60, 66, 255)); x = 20
        for im in ims.values():
            sheet.alpha_composite(Image.fromarray(im).resize((im.shape[1] * z, H * z), Image.NEAREST), (x, 20)); x += im.shape[1] * z + 20
        sheet.save(o.parts)
    sys.exit(1 if bad else 0)
