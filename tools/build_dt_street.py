#!/usr/bin/env python3
"""tools/build_dt_street.py: the tall Downtown's street pieces for the sample screen (art/dt-sample-05nov), BUILT from
parts drawn once and stamped on integer grids (tier C; BIBLE 3: 46 px a metre, the crispness bar; no resampling,
binary alpha, 0 credits).

Layer plan decision 4a (owner, 26 Oct): the cargo bike's hiding places at true scale behind Pepper, the perches on
their old tops drawn as stacks of the baker's bread crates. Decision 1a: the guild house's stepped gable becomes a
portal top and its chimney a bay window's roof. Review round 1 (5 Nov): every value set from its on-screen luma (back
below the far layers, play perches mid-tone like the apple crates), one crate size, the gateway an arch in a house.

  town_shelter_tall.png  back, decoration (no outline): the tram stop shelter, 2.5 m (115 px) tall, 3.0 m (140 px)
                         long; steel posts, a flat roof, clear glass with one reflection band per pane, a lit poster
                         (a cinnamon bun, no text). Centred on the SHELTER box, standing on the back line (y 414).
  town_gateway.png       back, decoration: the courtyard gateway, 3 m (138 px) tall, 80 wide: rusticated piers and a
                         stone arch, no wall of its own (the house's plaster shows round it); the dark passage with a
                         sunny courtyard at its end. Centred in the house that holds the GATE's right end (arthooks).
  town_crates70.png      play, obstacle (1 px dark outline): the GATE's solid perch (70 x 36) as 2 x 2 bread crates,
                         34 x 17 each (0.74 x 0.37 m) on an 18 px pitch, drawn at the box's x0 - 1, y0 - 1.
  town_breadboard.png    play, the SHELTER's one-way perch (72 px, 48 px up): the baker's board, two planks, outlined,
                         drawn at x0 - 1, y0 - 1 (rows 375-386).
  town_crate_leg.png     play, outlined: the board's two legs, two of the same crates end-on (16 x 17 on the 18 px pitch).
  town_portal_top.png    play, outlined: the guild house's portal top on the stepped gable's boxes (GUILD ROOF and the
                         steps right of it), stone steps, a gold medallion, a moulded base; at the steps' x0 - 1, top - 1.
  town_oriel.png         play, outlined: the CHIMNEY's solid box (16 x 44) exactly, as the bay window's central stone pier
                         under a copper cap (the golden bone's perch); at x0 - 1, y0 - 1.
  town_oriel_bay.png     back, decoration: the bay window round it (58 x 44, world y 200-243): roof, two lights, corbel.

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
    # play (no fade): crate wood median about 110 on screen, as the apple crates; bread a warm step apart
    wl=(150, 124, 88), wm=(130, 104, 68), ws=(104, 78, 48), wd=(82, 58, 36), wi=(52, 38, 30),   # pine crate wood, interior
    bl=(178, 124, 60), bm=(150, 94, 42), bd=(112, 64, 28),              # bread crust
    sl=(132, 146, 156), sm=(88, 100, 112), ss=(64, 74, 86), sd=(46, 54, 64),   # steel (dark, so it reads faded)
    gb=(150, 166, 174),                                                # the glass's reflection band
    pc=(113, 108, 94), pk=(104, 63, 74),                               # the poster's card (150 on screen), pink icing
    tl=(135, 130, 120), tm=(110, 103, 95), tv=(77, 72, 68),             # granite (the fronts' L, T, V)
    pd=(58, 50, 56), pdd=(42, 36, 42), pf=(84, 76, 80),                # the passage, its shade, its floor
    cw=(170, 154, 118), cg=(96, 146, 84), cgd=(70, 112, 66),            # the courtyard: sunny wall, a bush
    og=(31, 37, 45), ol=(47, 55, 62),                                  # window glass (the fronts' G, R)
    of=(140, 137, 131),                                                # window frames (the fronts' F)
    bb=(101, 84, 62), bs=(76, 63, 46),                                 # the bay window's body (135 on screen), its shade
    rl=(106, 146, 124), rm=(81, 130, 109), rs=(61, 104, 87),            # the pier's copper cap (play: 132 / 113 / 88)
    dl=(87, 119, 101), dm=(65, 104, 87), ds=(48, 83, 69),               # the bay's copper roof (decoration: 150 / 138 / 124)
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
    """the GATE's solid perch: 2 x 2 crates of 34 x 17 in one dark outline, a dark line between crates (18 px pitch)"""
    n = 2; cw = (box_w + 1 - (n + 1)) // n                               # 70: 34
    assert cw == 34, "one crate size: the GATE box must be 70 wide"
    W = n * (cw + 1) + 1; H = 2 * (17 + 1) + 1
    cv = Cv(W, H)
    cv.rect(0, 0, W - 1, H - 1, "ink")
    part = crate(cw)
    for r in range(2):
        for i in range(n): cv.stamp(part, 1 + i * (cw + 1), 1 + r * 18)
    return cv


def breadboard():
    """the baker's board on the shelter's perch: 72 + 2 px, two planks of 5 px in one outline, 12 rows (y 375-386),
    so the crate legs under it are two whole crates"""
    cv = Cv(74, 12)
    cv.rect(0, 0, 73, 11, "ink")
    for y in (1, 6):
        cv.rect(1, y, 72, y + 4, "wm"); cv.rect(1, y, 72, y, "wl"); cv.rect(1, y + 4, 72, y + 4, "ws")
    for x in range(10, 70, 18): cv.rect(x, 3, x + 5, 3, "ws"); cv.rect(x + 9, 8, min(x + 14, 72), 8, "ws")   # grain, 18 px grid
    return cv


def crate_leg():
    """two of the same bread crates end-on (16 x 17, 18 px pitch), in one dark outline: they hold her perch"""
    cv = Cv(18, 37)
    cv.rect(0, 0, 17, 36, "ink")
    part = crate(16)
    for r in range(2): cv.stamp(part, 1, 1 + r * 18)
    return cv


# the guild house's stepped gable boxes (riverwalk/level/tiled/downtown_tall.lua: GUILD ROOF and the steps right of
# it, 6 px tall; nothing here moves them): x0, x1, top
STEPS = [(1560, 1568, 272), (1568, 1576, 268), (1576, 1584, 264), (1584, 1592, 260), (1592, 1600, 256), (1600, 1608, 252),
         (1608, 1616, 248), (1616, 1656, 244), (1656, 1664, 248), (1664, 1672, 252), (1672, 1680, 256)]
PORTAL_BASE = 292                                                         # the portal top's base moulding, game y


def portal_top():
    """the guild house's portal top: stone blocks under every step of the gable (the steps' tops lit, the risers lit on
    the rising side and shaded on the falling side), coursed joints, a gold medallion, a moulded base; outlined"""
    X0, Y0 = STEPS[0][0] - 1, min(t for _, _, t in STEPS) - 1
    W = STEPS[-1][1] - STEPS[0][0] + 2; H = PORTAL_BASE - Y0 + 1
    cv = Cv(W, H)
    for x0, x1, t in STEPS: cv.rect(x0 - X0, t - Y0, x1 - 1 - X0, PORTAL_BASE - 1 - Y0, "tm")
    for y in range(H):                                                    # coursed blocks: 8 px courses, 16 px blocks
        gy = y + Y0
        if (gy - 244) % 8 == 7:
            for x in range(W):
                if cv.a[y, x] == "tm": cv.put(x, y, "tv")
        else:
            off = 8 if ((gy - 244) // 8) % 2 else 0
            for x in range(W):
                if cv.a[y, x] == "tm" and (x + X0 - 1560 + off) % 16 == 15: cv.put(x, y, "tv")
    top = max(t for _, _, t in STEPS)
    for i, (x0, x1, t) in enumerate(STEPS):                               # step tops lit; risers by the light
        cv.rect(x0 - X0, t - Y0, x1 - 1 - X0, t - Y0, "tl")
        prev = STEPS[i - 1][2] if i else PORTAL_BASE
        nxt = STEPS[i + 1][2] if i + 1 < len(STEPS) else PORTAL_BASE
        if prev > t: cv.rect(x0 - X0, t - Y0, x0 - X0, prev - 1 - Y0, "tl")
        if nxt > t: cv.rect(x1 - 1 - X0, t - Y0 + 1, x1 - 1 - X0, nxt - 1 - Y0, "tv")
    cx, cy, R = 1620 - X0, 268 - Y0, 7.5                                  # the gold medallion (the bakers' guild)
    for y in range(int(cy - R) - 1, int(cy + R) + 2):
        for x in range(int(cx - R) - 1, int(cx + R) + 2):
            d = np.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d < R:
                c = "bm"
                if d > R - 1.6: c = "bl" if (x + 0.5 - cx) + (y + 0.5 - cy) < 0 else "bd"
                elif d < 2.6: c = "bd"
                cv.put(x, y, c)
    b = PORTAL_BASE - Y0                                                  # the base moulding, the full width
    cv.rect(0, b - 5, W - 1, b - 5, "tl"); cv.rect(0, b - 4, W - 1, b - 2, "tm"); cv.rect(0, b - 1, W - 1, b - 1, "tv")
    cv.a[:, 0] = ""; cv.a[:, -1] = ""; cv.a[0] = ""; cv.a[-1] = ""
    cv.a[:, 1] = np.where(cv.a[:, 1] != "", cv.a[:, 1], ""); cv.outline()
    return cv


def oriel():
    """the CHIMNEY's solid box (16 x 44; the golden bone on its top) as the bay window's central stone pier with a
    copper cap: exactly the box, outlined (play), 18 x 45 (y 199-243), so what stops Pepper is what she sees; the bay
    round it (its roof and two windows) is decoration (oriel_bay). Review round 3: no art wider than the box."""
    W, H = 18, 45
    cv = Cv(W, H)
    cv.rect(1, 1, 16, 44, "tm")
    cv.rect(1, 1, 1, 44, "tl"); cv.rect(16, 1, 16, 44, "tv")              # the pier: lit left, shaded right
    for y in range(14, 44, 8): cv.rect(2, y, 15, y, "tv")                  # its courses, 8 px
    cv.rect(1, 1, 16, 1, "rl"); cv.rect(1, 2, 16, 4, "rm"); cv.rect(1, 5, 16, 5, "rs")   # the copper cap (the perch)
    cv.rect(1, 6, 16, 6, "tv")
    cv.a[0] = ""; cv.a[:, 0] = ""; cv.a[:, -1] = ""
    cv.outline()
    return cv


def oriel_bay():
    """the bay window round the pier, decoration (no outline): 58 wide, world y 200-243: a copper roof falling from the
    pier's cap to the bay's width (edges a darker copper), a stone lintel, two windows (the house's frames and panes,
    one light each side of the pier), the body a step darker than the wall with a 3 px shade down its right edge, a
    sill, a corbel stepping in to the crown's 40 px top"""
    W, H = 58, 44
    cv = Cv(W, H)
    halves = [8, 12, 15, 19, 22, 26, 29]                                  # the roof, rows 0-6 (y 200-206)
    for k, hw in enumerate(halves):
        cv.rect(29 - hw, k, 28 + hw, k, "dm")
        if k: cv.rect(29 - hw, k, 29 - halves[k - 1] - 1, k, "dl"); cv.rect(28 + halves[k - 1] + 1, k, 28 + hw, k, "ds")
    cv.rect(0, 7, W - 1, 7, "ds")                                         # its eave, darker copper
    o = 8                                                                 # the body from y 208
    cv.rect(0, o, W - 1, H - 1, "bb")
    cv.rect(W - 3, o, W - 1, H - 1, "bs")
    cv.rect(0, o, W - 1, o, "tl"); cv.rect(0, o + 1, W - 1, o + 1, "tm"); cv.rect(0, o + 2, W - 1, o + 2, "tv")   # lintel
    y0, y1 = o + 5, o + 25
    for x0 in (4, 36):                                                    # two lights, 18 wide, either side of the pier
        cv.rect(x0, y0, x0 + 17, y1, "of")
        cv.rect(x0 + 2, y0 + 2, x0 + 15, y1 - 2, "og"); cv.rect(x0 + 2, y0 + 2, x0 + 2, y1 - 2, "ol")
        cv.rect(x0 + 2, y0 + 10, x0 + 15, y0 + 11, "of")                  # a bar, as the house's 2 px bars
    cv.rect(1, y1 + 1, W - 2, y1 + 1, "tl"); cv.rect(1, y1 + 2, W - 2, y1 + 3, "tm"); cv.rect(1, y1 + 4, W - 2, y1 + 4, "tv")   # sill
    for i, (a, b) in enumerate(((3, 54), (6, 51), (9, 48))):              # the corbel, stepping in to 40 px
        y = o + 31 + i * 2 - (1 if i else 0)
        cv.rect(0, y, W - 1, H - 1, "")
        cv.rect(a, y, b, H - 1, "tm"); cv.rect(a, y, b, y, "tl"); cv.rect(b, y + 1, b, H - 1, "tv")
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
    for sx in (44, 96):                                                  # one clean 45 degree band, 2 px, per pane
        for k in range(22):
            cv.rect(sx + k, gy0 + 12 + k, sx + k + 1, gy0 + 12 + k, "gb")
    cv.rect(gx0, gy1 - 1, gx1, gy1 - 1, "sm")                            # the glass's bottom rail
    cv.rect(gx0, gy1, gx1, gy1, "ss")
    for px in (0, W // 2 - 2, W - 4):                                    # posts, 4 px: lit, mid, mid, shade
        cv.rect(px, roof - 1, px + 3, H - 1, "sm"); cv.rect(px, roof - 1, px, H - 1, "sl"); cv.rect(px + 3, roof - 1, px + 3, H - 1, "ss")
        fx0, fx1 = max(0, px - 1), min(W - 1, px + 4)                    # a foot plate (bolted to the pavement)
        cv.rect(fx0, H - 3, fx1, H - 3, "sl"); cv.rect(fx0, H - 2, fx1, H - 1, "ss")
        cv.rect(px, roof + 1, px + 3, roof + 1, "sd")                    # the post's collar under the roof
    cv.rect(0, 2, W - 1, 2, "sl")                                        # the roof's fascia: a lit line, a dark groove
    cv.rect(0, 3, W - 1, 3, "ss")
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


def gateway():
    """the courtyard gateway, 138 px (3 m) tall, 80 wide, an arch in a house's ground floor: rusticated piers (12 px)
    on 12 px courses, a stone arch (7 px ring, 15 degree joints, a keystone), no wall of its own; the passage dark, a
    sunny courtyard wall with a window and a bush at its far end. Opening 56 wide, 96 px to the spring (2.1 m: the
    cargo bike's rider passes under)"""
    W, H, pier, ring, r = 80, 138, 12, 7, 28
    cx, spring = W // 2, 7 + ring + r                                     # the ring's outer top on row 7: the piers are 8
                                                                          # whole 12 px courses (spring row 42)
    cv = Cv(W, H)
    hole = np.zeros((H, W), bool)
    for y in range(H):
        for x in range(W):
            if y >= spring:
                if pier <= x < W - pier: hole[y, x] = True
                continue
            d = np.hypot(x + 0.5 - cx, y + 0.5 - spring)
            if d < r: hole[y, x] = True
            elif d < r + ring:
                a = np.degrees(np.arctan2(spring - (y + 0.5), (x + 0.5) - cx))
                joint = any(abs(a - j) < 0.55 * 180 / np.pi / max(d, 1) for j in range(15, 180, 15)) and abs(a - 90) > 9
                edge = d > r + ring - 1.0 or d < r + 1.0
                cv.put(x, y, "tv" if joint or (edge and a < 90) else ("tl" if edge else "tm"))
    for i, y in enumerate(range(spring, H, 12)):                          # the piers
        yb = min(y + 11, H - 1)
        for (bx0, bx1) in ((0, pier - 1), (W - pier, W - 1)):
            cv.rect(bx0, y, bx1, yb, "tm"); cv.rect(bx0, y, bx1, y, "tl"); cv.rect(bx0, y, bx0, yb, "tl")
            cv.rect(bx1, y + 1, bx1, yb, "tv")
            if yb == y + 11: cv.rect(bx0 + 1, yb, bx1, yb, "tv")
    cv.rect(0, spring - 2, pier + 1, spring - 1, "tl"); cv.rect(W - pier - 2, spring - 2, W - 1, spring - 1, "tl")   # imposts
    cv.rect(0, spring - 1, pier + 1, spring - 1, "tv"); cv.rect(W - pier - 2, spring - 1, W - 1, spring - 1, "tv")
    for y, x in zip(*np.nonzero(hole)): cv.put(x, y, "pd")
    cv.rect(pier, H - 9, W - pier - 1, H - 1, "pf")                      # the passage's floor
    yx0, yx1, yy0 = cx - 12, cx + 11, H - 52                             # the courtyard at its end
    cv.rect(yx0, yy0, yx1, H - 10, "cw")
    cv.rect(yx0 + 7, yy0 + 7, yx0 + 16, yy0 + 22, "pc"); cv.rect(yx0 + 8, yy0 + 8, yx0 + 15, yy0 + 21, "og")
    cv.rect(yx0 + 8, yy0 + 14, yx0 + 15, yy0 + 14, "pc"); cv.rect(yx0 + 8, yy0 + 8, yx0 + 8, yy0 + 21, "ol")
    for x in range(yx0, yx1 + 1, 8):                                       # the bush: round tops on an 8 px grid
        for dx, dy in ((2, 0), (3, 0), (4, 0), (5, 0), (1, 1), (6, 1), (0, 2), (7, 2)):
            if x + dx <= yx1: cv.put(x + dx, H - 25 + dy, "cg")
        cv.rect(x, H - 22, min(x + 7, yx1), H - 10, "cg")
    cv.rect(yx0, H - 12, yx1, H - 11, "cgd")
    for y in range(H):                                                    # the shadow under the arch, left reveal
        for x in range(W):
            if hole[y, x] and cv.a[y, x] == "pd" and (not hole[y - 1, x] or not hole[y - 2, x] or not hole[y, x - 1] or not hole[y, x - 2]):
                cv.put(x, y, "pdd")
    kx = cx - 4                                                           # the keystone, rows 3-16
    cv.rect(kx, 3, kx + 7, 16, "tm"); cv.rect(kx, 3, kx + 7, 3, "tl"); cv.rect(kx, 3, kx, 16, "tl")
    cv.rect(kx + 7, 4, kx + 7, 16, "tv"); cv.rect(kx + 1, 16, kx + 7, 16, "tv")
    return cv


def build():
    return {
        "town_shelter_tall": shelter(), "town_gateway": gateway(), "town_crates70": crates(70),
        "town_breadboard": breadboard(), "town_crate_leg": crate_leg(), "town_portal_top": portal_top(), "town_oriel": oriel(),
        "town_oriel_bay": oriel_bay(),
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
