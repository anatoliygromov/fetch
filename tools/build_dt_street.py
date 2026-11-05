#!/usr/bin/env python3
"""tools/build_dt_street.py: the tall Downtown's street pieces for the sample screen (art/dt-sample-05nov), BUILT from
parts drawn once and stamped on integer grids (tier C; BIBLE 3: 46 px a metre, the crispness bar; no resampling,
binary alpha, 0 credits).

Layer plan decision 4a (owner, 26 Oct): the cargo bike's hiding places at true scale behind Pepper, the perches on
their old tops drawn as stacks of the baker's bread crates. Decision 1a: the dormer becomes a window hood.

  town_shelter_tall.png  back, decoration (no outline): the tram stop shelter, 2.5 m (115 px) tall, 3.0 m (140 px)
                         long; steel posts, a flat roof, a glass back wall with reflections, a bench, a lit poster
                         (a cinnamon bun, no text). Centred on the SHELTER box, standing on the back line (y 414).
  town_gateway70.png,    back, decoration: the courtyard gateway, 3 m (138 px) tall, in rusticated stone under a
  town_gateway96.png     cornice; the passage is dark, a sunny courtyard at its far end. Centred on the GATE box.
  town_crates70.png,     play, obstacle (1 px dark outline): the GATE's solid perch (70 or 96 x 36) as two rows of
  town_crates96.png      bread crates, 34 or 31 x 17 each (0.74 x 0.37 m), drawn at the box's x0 - 1, y0 - 1.
  town_breadboard.png    play, the SHELTER's one-way perch (72 px, 48 px up): the baker's long board, outlined,
                         drawn at x0 - 1, y0 - 1.
  town_crate_leg.png     back, decoration: the board's two legs, three bread crates end-on (16 x 14 each).
  town_hood.png          play, the DORMER's ledge (56 px) as a copper window hood on two stone consoles, outlined.

  python3 -I tools/build_dt_street.py             write them all (riverwalk/art/scene/)
  python3 -I tools/build_dt_street.py --check     fail if a file on disk differs from the build
  python3 -I tools/build_dt_street.py --sheet P   all pieces at 5x on one sheet
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")

C = dict(
    ink=(18, 18, 26),                                                   # the obstacles' outline (arthooks INK)
    wl=(236, 208, 160), wm=(208, 172, 118), ws=(164, 124, 80), wd=(118, 84, 54), wi=(70, 48, 36),   # pine crate wood, interior
    bl=(232, 168, 84), bm=(194, 120, 52), bd=(140, 78, 34),             # bread crust
    sl=(132, 146, 156), sm=(88, 100, 112), ss=(64, 74, 86), sd=(46, 54, 64),   # steel (dark, so it reads faded)
    gl=(204, 222, 228), gm=(178, 200, 208), gw=(232, 242, 244),         # glass: lit, mid, a streak
    pc=(244, 236, 214), pk=(234, 150, 172),                            # the poster's card, pink icing
    tl=(222, 214, 198), tm=(176, 166, 152), tv=(116, 108, 102),         # granite (the fronts' L, T, V)
    pd=(84, 76, 80), pdd=(64, 58, 62), pf=(104, 96, 98),               # the passage, its shade, its floor
    cw=(226, 206, 160), cg=(96, 146, 84), cgd=(70, 112, 66),            # the courtyard: sunny wall, a bush
    cl=(150, 206, 176), cm=(104, 166, 140), cs=(72, 122, 102),          # copper (the roof kit's copper)
)


class Cv:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.full((h, w), "", dtype="<U3")

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c):                                   # inclusive
        if x1 < x0 or y1 < y0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = c

    def stamp(self, part, x, y):
        for dy in range(part.shape[0]):
            for dx in range(part.shape[1]):
                if part[dy, dx]: self.put(x + dx, y + dy, part[dy, dx])

    def outline(self, c="ink"):
        """a 1 px dark ring on the transparent pixels around the shape (4-neighbours)"""
        on = self.a != ""
        ring = np.zeros_like(on)
        ring[1:] |= on[:-1]; ring[:-1] |= on[1:]; ring[:, 1:] |= on[:, :-1]; ring[:, :-1] |= on[:, 1:]
        self.a[ring & ~on] = c

    def png(self):
        im = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y, x]: im[y, x] = (*C[self.a[y, x]], 255)
        return im


# ---- parts, drawn once ------------------------------------------------------------------------------------------
LOAF = ["..bbb..",                                                      # a loaf's crust over the crate's rail
        ".blmmm.",
        "blmmmmd",
        "mmmmmmd",
        "mmmmmmd"]
LOAF_KEY = {"b": "bl", "l": "bl", "m": "bm", "d": "bd", ".": "wi"}


def crate(w, h=17):
    """a pine bread crate, front-on, w x h: a lit top rail with a hand slot, an opening with loaves, a middle slat,
    a low opening, the bottom rail; the posts lit on the left, shaded on the right"""
    cv = Cv(w, h)
    cv.rect(0, 0, w - 1, h - 1, "wm")
    cv.rect(0, 0, w - 1, 0, "wl")                                       # top rail
    cv.rect(w // 2 - 4, 1, w // 2 + 3, 1, "wd")                          # the hand slot
    o1, o2, mid = (3, 7), (11, 13), 8
    if h < 17: o1, o2, mid = (3, 6), (10, 11), 7                         # (end-on, 14 tall: shorter openings)
    cv.rect(3, o1[0], w - 4, o1[1], "wi")
    cv.rect(3, o2[0], w - 4, o2[1], "wi")
    iw = w - 6; n = (iw + 1) // 8; x0 = 3 + (iw - (n * 8 - 1)) // 2
    for i in range(n):                                                   # loaves along the crate
        lx = x0 + i * 8
        for dy, row in enumerate(LOAF[: o1[1] - o1[0] + 1]):
            for dx, ch in enumerate(row):
                if ch != ".": cv.put(lx + dx, o1[0] + dy, LOAF_KEY[ch])
        cv.rect(lx, o2[0], lx + 5, o2[1] - 1, "bm"); cv.rect(lx + 6, o2[0], lx + 6, o2[1] - 1, "bd")
        cv.rect(lx, o2[1], lx + 6, o2[1], "bd")
    cv.rect(0, mid, w - 1, mid, "wl")                                    # the middle slat: lit top
    cv.rect(0, h - 3, w - 1, h - 3, "wl")                                # bottom rail: lit top, shade under
    cv.rect(0, h - 1, w - 1, h - 1, "ws")
    cv.rect(0, 0, 0, h - 1, "wl"); cv.rect(1, 1, 2, h - 2, "wm")          # posts: the left lit, the right shaded
    cv.rect(w - 3, 1, w - 2, h - 2, "wm"); cv.rect(w - 1, 0, w - 1, h - 1, "ws")
    cv.rect(2, o1[0], 2, o1[1], "ws"); cv.rect(2, o2[0], 2, o2[1], "ws")  # the left post's inner edge in shade
    return cv.a


def crates(box_w):
    """the GATE's solid perch: two rows of crates in one dark outline, a dark line between crates"""
    n = 2 if box_w < 80 else 3
    cw = (box_w + 1 - (n + 1)) // n                                      # 70: 34, 96: 31
    W = n * (cw + 1) + 1; H = 2 * (17 + 1) + 1
    cv = Cv(W, H)
    cv.rect(0, 0, W - 1, H - 1, "ink")
    part = crate(cw)
    for r in range(2):
        for i in range(n): cv.stamp(part, 1 + i * (cw + 1), 1 + r * 18)
    return cv


def breadboard():
    """the baker's long board on the shelter's perch: 72 + 2 px, a 5 px plank in its outline"""
    cv = Cv(74, 7)
    cv.rect(0, 0, 73, 6, "ink")
    cv.rect(1, 1, 72, 5, "wm"); cv.rect(1, 1, 72, 1, "wl"); cv.rect(1, 5, 72, 5, "ws")
    for x in range(10, 70, 18): cv.rect(x, 3, x + 5, 3, "ws")               # a few grain lines, on an 18 px grid
    return cv


def crate_leg():
    """three bread crates end-on (16 x 14), stacked: decoration, no outline (the bottom row is the darkest wood)"""
    cv = Cv(16, 42)
    part = crate(16, 14)
    for r in range(3): cv.stamp(part, 0, r * 14)
    return cv


def hood():
    """the dormer's ledge (56 px) as a copper window hood with standing seams, on two stepped stone consoles"""
    W = 58; cv = Cv(W, 19)
    cv.rect(1, 1, W - 2, 1, "cl"); cv.rect(1, 2, W - 2, 4, "cm"); cv.rect(1, 5, W - 2, 5, "cs")
    for x in range(8, W - 4, 8): cv.rect(x, 2, x, 4, "cs"); cv.rect(x + 1, 2, x + 1, 4, "cl")   # standing seams
    for cx in (9, W - 10):                                                # consoles: 6, 4, 2 wide, stepped down
        for i, (half, rows) in enumerate(((4, 4), (3, 4), (2, 3))):
            y0 = 6 + sum((4, 4, 3)[:i])
            cv.rect(cx - half, y0, cx + half - 1, y0 + rows - 1, "tm")
            cv.rect(cx - half, y0, cx - half, y0 + rows - 1, "tl")
            cv.rect(cx + half - 1, y0, cx + half - 1, y0 + rows - 1, "tv")
    cv.a[0] = ""; cv.a[:, 0] = ""; cv.a[:, -1] = ""
    cv.outline()
    return cv


def shelter():
    """the tram stop shelter, 140 x 115: a flat steel roof, three posts, a clear glass back wall (the facade shows
    through it: only its edge rails and the reflections are drawn, on a grid), a lit poster"""
    W, H = 140, 115
    cv = Cv(W, H)
    roof = 7
    cv.rect(0, 0, W - 1, 0, "sl"); cv.rect(0, 1, W - 1, roof - 3, "sm"); cv.rect(0, roof - 2, W - 1, roof - 2, "ss")
    cv.rect(2, roof - 1, W - 3, roof - 1, "sd")                         # the roof's underside
    gx0, gx1, gy0, gy1 = 4, W - 5, roof, H - 13                          # the glass, 13 px clear of the pavement
    cv.rect(gx0, gy0, gx1, gy0 + 1, "sm")                                # its top rail
    for sx in range(gx0 + 8, gx1 - 40, 30):                              # reflections: two diagonal streaks, 30 apart
        for k in range(28):
            y = gy0 + 12 + k
            cv.rect(sx + k // 2, y, sx + k // 2 + 1, y, "gw")
            cv.rect(sx + 5 + k // 2, y, sx + 5 + k // 2, y, "gl")
    cv.rect(gx0, gy1 - 1, gx1, gy1 - 1, "sm")                            # the glass's bottom rail
    cv.rect(gx0, gy1, gx1, gy1, "ss")
    for px in (0, W // 2 - 2, W - 4):                                    # posts, 4 px: lit, mid, mid, shade
        cv.rect(px, roof - 1, px + 3, H - 1, "sm"); cv.rect(px, roof - 1, px, H - 1, "sl"); cv.rect(px + 3, roof - 1, px + 3, H - 1, "ss")
    # (no bench: the baker's board on its crates stands in front of the shelter and is the seat; art/dt-sample-05nov)
    ax0, ax1, ay0, ay1 = 5, 35, 30, 92                                   # the poster at the left end: clear of the crates,
                                                                         # and of the stop sign on the right (arthooks)
    cv.rect(ax0, ay0, ax1, ay1, "ss"); cv.rect(ax0, ay0, ax1, ay0, "sm"); cv.rect(ax0, ay0, ax0, ay1, "sm")
    cv.rect(ax0 + 2, ay0 + 2, ax1 - 2, ay1 - 2, "pc")
    # a cinnamon bun, 21 px: a round crust (lit upper left, shade lower right), a spiral groove, pink icing on top
    bcx, bcy, R = (ax0 + ax1) / 2, ay0 + 26, 10.5
    for y in range(int(bcy - R) - 1, int(bcy + R) + 2):
        for x in range(int(bcx - R) - 1, int(bcx + R) + 2):
            dx, dy = x + 0.5 - bcx, y + 0.5 - bcy; d = np.hypot(dx, dy)
            if d >= R: continue
            c = "bm"
            if d > R - 2.2: c = "bl" if dx + dy < -3 else ("bd" if dx + dy > 3 else "bm")
            th = (np.degrees(np.arctan2(dy, dx)) % 360) / 360
            if abs(d - (2.2 + 7.0 * th)) < 0.75 and d < R - 2: c = "bd"     # the spiral groove
            if d < R - 3 and dy < 1.5 and c == "bm" and (x + y) % 1 == 0 and d > 1.5: c = "pk" if dy < -0.5 or abs(dx) < 5 else c
            cv.put(x, y, c)
    cv.rect(ax0 + 7, ay1 - 14, ax1 - 7, ay1 - 12, "pk")                  # two pink bands under it (no text)
    cv.rect(ax0 + 11, ay1 - 9, ax1 - 11, ay1 - 8, "bm")
    return cv


def gateway(box_w):
    """the courtyard gateway, 138 px (3 m) tall: rusticated piers, a stone arch with a keystone, a cornice; the
    passage dark, a sunny courtyard wall with a bush at its far end"""
    op = box_w + 12                                                      # the opening (70: 82, 96: 108)
    pier = 16; W = op + 2 * pier; H = 138
    r = op // 2; cx = W // 2
    cvn = 8; ring = 8; spring = cvn + ring + r                           # the arch springs here (from the top)
    cv = Cv(W, H)
    cv.rect(0, 0, W - 1, H - 1, "tm")
    cv.rect(0, 0, W - 1, 0, "tl"); cv.rect(0, 1, W - 1, 4, "tm"); cv.rect(0, 5, W - 1, 5, "tv"); cv.rect(0, 6, W - 1, 7, "tm")   # cornice
    cv.rect(0, 0, 0, H - 1, "tl"); cv.rect(W - 1, 1, W - 1, H - 1, "tv")
    hole = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if y >= spring: hole[y, x] = pier <= x < W - pier
            else:
                d = np.hypot(x + 0.5 - cx, y + 0.5 - spring)
                if d < r: hole[y, x] = True
                elif d < r + ring:                                         # the voussoirs: light stone, dark joints
                    a = np.degrees(np.arctan2(spring - (y + 0.5), (x + 0.5) - cx))
                    joint = any(abs(a - j) < 0.55 * 180 / np.pi / max(d, 1) * 1.0 for j in range(15, 180, 15)) and abs(a - 90) > 9
                    edge = d > r + ring - 1.0
                    cv.put(x, y, "tv" if (joint or edge) else "tl")
    for i, y in enumerate(range(spring, H, 12)):                         # rusticated piers: 12 px courses, joints dark
        yb = min(y + 11, H - 1)
        for (bx0, bx1) in ((0, pier - 1), (W - pier, W - 1)):
            cv.rect(bx0, y, bx1, yb, "tm"); cv.rect(bx0, y, bx1, y, "tl"); cv.rect(bx0, y, bx0, yb, "tl")
            cv.rect(bx1, y + 1, bx1, yb, "tv")
            if yb == y + 11: cv.rect(bx0 + 1, yb, bx1, yb, "tv")
    # the passage and the courtyard at its end
    for y, x in zip(*np.nonzero(hole)): cv.put(x, y, "pd")
    cv.rect(pier, H - 9, W - pier - 1, H - 1, "pf")                      # its floor, lighter
    yx0, yx1, yy0 = cx - op // 4, cx + op // 4 - 1, H - 58               # the courtyard: a sunny wall, 1.2 m of bush
    cv.rect(yx0, yy0, yx1, H - 10, "cw")
    for wx in (yx0 + 5, yx1 - 14):                                        # two windows: a light frame, glass, a bar
        cv.rect(wx, yy0 + 7, wx + 9, yy0 + 22, "pc"); cv.rect(wx + 1, yy0 + 8, wx + 8, yy0 + 21, "gm")
        cv.rect(wx + 1, yy0 + 14, wx + 8, yy0 + 14, "pc"); cv.rect(wx + 1, yy0 + 8, wx + 1, yy0 + 21, "gl")
    for i, x in enumerate(range(yx0, yx1 + 1, 8)):                        # the bush: round tops on an 8 px grid
        for dx, dy in ((2, 0), (3, 0), (4, 0), (5, 0), (1, 1), (6, 1), (0, 2), (7, 2)):
            if x + dx <= yx1: cv.put(x + dx, H - 25 + dy, "cg")
        cv.rect(x, H - 22, min(x + 7, yx1), H - 10, "cg")
    cv.rect(yx0, H - 12, yx1, H - 11, "cgd")                              # its shaded foot
    cv.rect(yx0, H - 10, yx1, H - 10, "cgd")
    # the shadow under the arch and on the left reveal (light from the upper left)
    for y in range(H):
        for x in range(W):
            if hole[y, x] and (not hole[y - 1, x] or not hole[y - 2, x] or (x > 0 and not hole[y, x - 1]) or (x > 1 and not hole[y, x - 2])):
                if cv.a[y, x] == "pd": cv.put(x, y, "pdd")
    kx = cx - 5                                                          # the keystone
    cv.rect(kx, cvn, kx + 9, cvn + ring + 3, "tm"); cv.rect(kx, cvn, kx + 9, cvn, "tl"); cv.rect(kx, cvn, kx, cvn + ring + 3, "tl")
    cv.rect(kx + 9, cvn + 1, kx + 9, cvn + ring + 3, "tv"); cv.rect(kx + 1, cvn + ring + 3, kx + 9, cvn + ring + 3, "tv")
    return cv


def build():
    return {
        "town_shelter_tall": shelter(),
        "town_gateway70": gateway(70), "town_gateway96": gateway(96),
        "town_crates70": crates(70), "town_crates96": crates(96),
        "town_breadboard": breadboard(), "town_crate_leg": crate_leg(), "town_hood": hood(),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    o = ap.parse_args()
    bad = 0; ims = {}
    for n, cv in build().items():
        im = cv.png(); ims[n] = im; p = os.path.join(OUT, n + ".png")
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(p, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{p} {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z = 5; W = sum(i.shape[1] * z + 20 for i in ims.values()) + 20; H = max(i.shape[0] for i in ims.values()) * z + 40
        sh = Image.new("RGBA", (W, H), (96, 104, 118, 255)); x = 20
        for im in ims.values():
            sh.alpha_composite(Image.fromarray(im).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST), (x, H - 20 - im.shape[0] * z)); x += im.shape[1] * z + 20
        sh.save(o.sheet)
    sys.exit(1 if bad else 0)
