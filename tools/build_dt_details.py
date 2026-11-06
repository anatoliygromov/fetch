#!/usr/bin/env python3
"""tools/build_dt_details.py: the tall Downtown's pieces that were drawn in code or with speckled stone, BUILT from parts
drawn once and stamped on integer grids (art/dt-roofs-06nov, tier C; BIBLE 3: 46 px a metre, the crispness bar, binary
alpha, no resampling, 0 credits). Every colour is from art/palettes/downtown.gpl: the sample screen's ink, granite,
steel and copper ramps (tools/build_dt_street.py), its reds and greens.

  town_balcony56.png   play, outlined (scene.lua drawBalcony; 58 / 66 x 60): a BALCONY 56 or 64 px wide. The iron railing
  town_balcony64.png   at its back, 1 m (46 px, Sc.BALCONY_RAIL) over the slab, open: a thick handrail, a bottom rail,
                       four posts, one iron ring per panel on a short bar; the stone slab, 8 rows (its ink row is the
                       box's top - 1) and two stepped corbels under it. Drawn at x0 - 1, y0 - 47.
  town_spring.png      play, outlined (scene.lua Sc.spring): the springy awning's and parasol's grey steel coil (three
                       turns, closed end plates, ink round every frame), 9 px wide, a strip of
                       4 frames 9 x 10 for the heights 7, 8, 9 and 10 (it is squashed by 2 px as it launches her); the
                       frame for height h is drawn with its top on the awning's underside, rows 0 .. h - 1.
  town_stopsign.png    back, decoration (arthooks.lua stopSign; faded by the game, no outline): the tram stop sign at true
                       scale, 2.2 m (101 px): a 3 px steel pole and a round sign 0.41 m (19 px) across, a green ring round
                       a white disc with a tram on it (no text, no logo). Centred on the stop's x (column 9 on it), its
                       bottom on the rail line; its top stays under the shelter's roof (108 px up).
  town_tier.png        play, outlined (scene.lua, the TIER: 50 x 58, drawn at x0 - 1, y0 - 1): the fountain's top
                       basin, a stone dish on a coursed column and a foot (the same silhouette as before).
  town_bowl.png        play, outlined (the FOUNTAIN: 34 x 82): the lower basin's dish on its coursed column.
  town_rim.png         play, outlined (each RIM: 18 x 18): the basin's corner bollard (art/dt-audit-06nov: it read as a brick cube).
  town_jet.png         decoration (scene.lua drawTerrainArt; no outline): the water falling from the top tier's lip to
                       the pool, 4 frames of 6 x 88 side by side (white dashes running down a 2 px stream that curls off
                       the lip, a splash at the bottom); the left stream as drawn, the right one mirrored. Its column 5
                       is next to the lip (the TIER's x0 - 2), its top row the TIER's top + 3, its splash in the pool (y 432-434).
  (Review of 6 Nov: the old tier, bowl and rim were lighter than the house walls behind them, 152 to 157 on screen
  against 145 to 152, and the bowl and rim had speckled stone; they now take the sample's granite, about 103.)

  python3 -I tools/build_dt_details.py             write them all (riverwalk/art/scene/)
  python3 -I tools/build_dt_details.py --check     fail if a file on disk differs from the build
  python3 -I tools/build_dt_details.py --sheet P   all pieces at 5x on one sheet
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")

C = {
    "ink": (18, 18, 26),
    "g1": (135, 130, 120), "g2": (110, 103, 95), "g3": (77, 72, 68), "g4": (58, 50, 56),                     # granite
    "s1": (132, 146, 156), "s2": (88, 100, 112), "s3": (64, 74, 86), "s4": (46, 54, 64),                     # steel
    "r1": (247, 134, 113), "r2": (206, 53, 49), "r3": (125, 28, 36),                                         # spring red
    "e1": (96, 146, 84), "e2": (56, 88, 70), "e3": (43, 74, 56),                                             # sign green
    "w": (244, 238, 243),                                                                                    # sign white
    "j1": (247, 249, 250), "j2": (150, 166, 174), "j3": (112, 132, 156),                                     # falling water
}


class Cv:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.full((h, w), "", dtype="<U3")

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c):                                   # inclusive
        if x1 < x0 or y1 < y0: return
        self.a[max(0, y0):min(self.h, y1 + 1), max(0, x0):min(self.w, x1 + 1)] = c

    def keyed(self, rows, key, x, y):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".": self.put(x + dx, y + dy, key[ch])

    def outline(self):
        """ink every opaque pixel on the shape's edge (4-neighbours): the obstacles' 1 px dark outline"""
        on = self.a != ""
        pad = np.pad(on, 1, constant_values=False)
        edge = on & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        self.a[edge] = "ink"

    def png(self):
        im = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y, x]: im[y, x] = (*C[self.a[y, x]], 255)
        return im


STONE = {"k": "ink", "a": "g1", "b": "g2", "c": "g3", "d": "g4"}

# ---- the balcony ---------------------------------------------------------------------------------------------------
RAIL = 46                                                                 # scene.lua Sc.BALCONY_RAIL: 1 m
# (fix round 1, 6 Nov: a wall of bars read as a birdcage.) An open Stockholm railing: a thick handrail and a bottom
# rail, a post at each end and between panels, and in each panel one iron ring held by a short bar above and below,
# so the wall behind reads as wall. The ring is drawn once (12 x 12, a 3 px band: ink, lit iron, ink), clear of the posts.
def ring12():
    rows = []
    for y in range(12):
        r = ""
        for x in range(12):
            d = np.hypot(x + 0.5 - 6, y + 0.5 - 6)
            r += ("a" if 4.0 <= d < 5.0 and (x + y) < 11 else "b") if 3.0 <= d < 6.0 else "."
        rows.append(r)
    return rows
RING12 = ring12()
CORBEL = ["kabbbbck", "kabbbbck", ".kabbck.", ".kabbck.", "..kbck..", "..kkkk.."]   # stepped in under the slab
SLAB = 8                                                                  # the slab's rows: ink, lit, stone x 4, shade, ink


def balcony(bw):
    """a BALCONY bw wide: image bw + 2 x 60, its row RAIL the slab's ink row (the box's top - 1)"""
    W, H = bw + 2, RAIL + SLAB + 6
    cv = Cv(W, H)
    s = RAIL
    # three panels between four posts (3 px): 56 -> panels of 14 over x 2-55, 64 -> panels of 16 over x 3-62
    span = W - 4 if bw == 56 else W - 6
    xa = (W - span) // 2
    P = (span - 12) // 3
    assert 3 * P + 12 == span, bw
    posts = [xa + i * (P + 3) for i in range(4)]
    # (review round 2: the bones float in the railing's lower part, rows 33-43 at 1x with their bob, so nothing upright
    # crosses them there): the middle posts and the rings' bars stop at a mid rail (rows 29-32); below it only the
    # two end posts run down to the bottom rail (rows 42-45)
    mid = 29
    cv.rect(xa, 0, xa + span - 1, 4, "s3"); cv.rect(xa + 1, 1, xa + span - 2, 1, "s1"); cv.rect(xa + 1, 2, xa + span - 2, 3, "s2")   # handrail
    cv.rect(xa, mid, xa + span - 1, mid + 3, "s3"); cv.rect(xa + 1, mid + 1, xa + span - 2, mid + 1, "s2")   # mid rail
    cv.rect(xa, s - 4, xa + span - 1, s - 1, "s3"); cv.rect(xa + 1, s - 3, xa + span - 2, s - 3, "s2")   # bottom rail
    for i, x in enumerate(posts):
        y1 = s - 1 if i in (0, len(posts) - 1) else mid + 3
        cv.rect(x, 0, x + 2, y1, "s3"); cv.rect(x + 1, 1, x + 1, y1 - 1, "s2")
    ry = 5 + (mid - 5 - 12) // 2                                          # the ring centred between handrail and mid rail
    for x in posts[:-1]:
        cx = x + 3 + P // 2                                               # the panel's middle (2 columns for an even panel)
        cv.keyed(RING12, {"a": "s2", "b": "s3"}, cx - 6, ry)
        cv.rect(cx - 1, 5, cx, ry, "s3"); cv.rect(cx - 1, ry + 11, cx, mid, "s3")   # held above and below
    cv.rect(0, s, W - 1, s + SLAB - 1, "g2"); cv.rect(1, s + 1, W - 2, s + 1, "g1"); cv.rect(1, s + SLAB - 2, W - 2, s + SLAB - 2, "g3")
    for cx in (5, W - 13):                                                # two corbels, 8 wide
        cv.keyed(CORBEL, STONE, cx, s + SLAB)
    cv.outline()
    return cv


# ---- the springy coil ------------------------------------------------------------------------------------------------
# (fix round 1, 6 Nov: the red bands read as a tassel and frames 0-2 were open at the bottom.) A grey steel coil, front
# on: three turns, each a full-width lit wire row over a narrower dark row (the back of the coil showing between the
# turns), so the silhouette steps in and out like a spring; a closed end plate on top and below; ink all round in
# every frame. The turn is drawn once.
TURN = ["kaaaaabbk", ".kccccck."]                                        # lit wire (lit left), the dark back between turns
TURN1 = ["kaaaabbbk"]                                                     # a turn pressed flat (the squashed frame)
PLATE = ["kbbbbbbbk"]                                                     # the closed end coil


def spring_frame(h):
    rows = {10: ["k", "P", "T", "T", "T", "P", "k"], 9: ["k", "P", "T", "T", "T", "k"], 8: ["k", "T", "T", "T", "k"],
            7: ["k", "T", "T", "t", "k"]}[h]
    key = {"k": "ink", "a": "s1", "b": "s2", "c": "s4"}
    cv = Cv(9, 10)
    y = 0
    for r in rows:
        if r == "k": cv.rect(0, y, 8, y, "ink"); y += 1
        elif r == "T": cv.keyed(TURN, key, 0, y); y += 2
        elif r == "P": cv.keyed(PLATE, key, 0, y); y += 1
        else: cv.keyed(TURN1, key, 0, y); y += 1
    assert y == h, (h, y)
    return cv


def spring():
    cv = Cv(36, 10)
    for i, h in enumerate((7, 8, 9, 10)):
        f = spring_frame(h)
        cv.a[:, i * 9:(i + 1) * 9] = f.a
    return cv


# ---- the tram stop sign ----------------------------------------------------------------------------------------------
TRAM = ["....eee....",                                                    # the pictogram: a tram, side view, facing left
        ".....e.....",
        ".eeeeeeeee.",
        "eewwewwewwe",
        "eewwewwewwe",
        "eeeeeeeeeee",
        "eeeeeeeeeee",
        ".ee.....ee."]


def stopsign():
    W, H = 19, 101
    cv = Cv(W, H)
    c = 9                                                                 # the pole's middle column, on the stop's x
    cv.rect(c - 1, 19, c + 1, H - 1, "s2"); cv.rect(c - 1, 19, c - 1, H - 1, "s1"); cv.rect(c + 1, 19, c + 1, H - 1, "s3")
    cv.rect(c - 2, H - 3, c + 2, H - 1, "s3"); cv.rect(c - 2, H - 3, c + 2, H - 3, "s2")   # its foot
    R = 9.5
    for y in range(19):
        for x in range(W):
            dx, dy = x + 0.5 - (c + 0.5), y + 0.5 - 9.5
            d = np.hypot(dx, dy)
            if d < R:
                if d >= R - 2.2: cv.put(x, y, "e3" if dx + dy > 6 else ("e1" if dx + dy < -6 else "e2"))   # the ring
                else: cv.put(x, y, "w")
    cv.keyed(TRAM, {"e": "e2", "w": "w"}, c - 5, 6)
    return cv


# ---- the fountain ----------------------------------------------------------------------------------------------------
def dish(cv, w, lip, under, x_in):
    """a stone basin's lip (rows 0 .. lip - 1, the full width) and its underside stepping in (rows lip .. lip + len - 1)"""
    cv.rect(1, 0, w - 2, 0, "g2"); cv.rect(0, 1, w - 1, lip - 2, "g2"); cv.rect(1, lip - 1, w - 2, lip - 1, "g2")
    cv.rect(1, 1, w - 2, 1, "g1"); cv.rect(1, lip - 2, w - 2, lip - 2, "g3")
    for k, (a, b) in enumerate(under):
        cv.rect(a, lip + k, b, lip + k, "g3"); cv.put(a + 1, lip + k, "g2") if b - a > 4 else None


def column(cv, x0, x1, y0, y1, course=8, top=0):
    """a coursed stone column: blocks of `course` rows, a vertical joint in alternate courses, lit left, shade right"""
    cv.rect(x0, y0, x1, y1, "g2")
    for y in range(y0, y1 + 1):
        k = (y - y0 + top) % course
        if k == course - 1: cv.rect(x0, y, x1, y, "g3")
        elif ((y - y0 + top) // course) % 2 and x1 - x0 >= 8: cv.put((x0 + x1) // 2, y, "g3")
    cv.rect(x0 + 1, y0, x0 + 1, y1, "g1")
    cv.rect(x1 - 1, y0, x1 - 1, y1, "g3")


def tier():
    cv = Cv(50, 58)
    dish(cv, 50, 7, [(4, 45), (8, 41), (9, 40)], 0)
    column(cv, 20, 29, 9, 48)
    cv.rect(18, 49, 31, 57, "g2"); cv.rect(19, 50, 30, 50, "g1"); cv.rect(19, 56, 30, 56, "g3"); cv.rect(30, 51, 30, 55, "g3")
    cv.rect(19, 51, 19, 55, "g1")
    cv.outline()
    return cv


def bowl():
    cv = Cv(34, 82)
    dish(cv, 34, 10, [(2, 31), (3, 30), (5, 28), (6, 27)], 0)
    column(cv, 9, 24, 14, 81, top=0)
    cv.outline()
    return cv


def rim():
    # (art/dt-audit-06nov) the audit: "lone grey brick cubes" by the fountain. Each RIM is the basin's corner bollard:
    # one granite post, no joints, a chamfered cap stone (Pepper's flat top), a shadow under the cap, a round shaft
    # (lit left, mid, shade right), a plinth on the pavement. Same box, same 18 x 18.
    cv = Cv(18, 18)
    cv.rect(1, 0, 16, 5, "g2"); cv.rect(0, 1, 17, 4, "g2")                           # the cap stone, chamfered
    cv.rect(1, 1, 16, 1, "g1"); cv.rect(1, 4, 16, 4, "g3")
    cv.rect(2, 5, 15, 5, "g4")                                                       # the shadow under the cap
    cv.rect(3, 6, 14, 15, "g2")                                                      # the shaft, round
    cv.rect(3, 6, 4, 15, "g1"); cv.rect(5, 6, 5, 15, "g2"); cv.rect(12, 6, 13, 15, "g3"); cv.rect(14, 6, 14, 15, "g4")
    cv.rect(2, 16, 15, 17, "g3"); cv.rect(2, 16, 15, 16, "g2")                       # the plinth
    cv.outline()
    return cv


def jet():
    FW, FH = 6, 88
    cv = Cv(FW * 4, FH)
    for f in range(4):
        ox = f * FW
        for y in range(FH - 3):
            x = 5 if y < 2 else (4 if y < 8 else 3)                       # it curls off the lip, then falls straight
            w = 1 if y < 2 else 2
            lit = (y - 2 * f) % 8 < 3                                     # a white dash every 8 rows, 2 rows on per frame
            cv.put(ox + x, y, "j1" if lit else "j2")
            if w == 2: cv.put(ox + x - 1, y, "j2" if lit else "j3")
        sp = [(1, 5), (2, 4)] if f % 2 else [(2, 5), (1, 4)]              # the splash on the pool: two rows, flickering
        cv.rect(ox + sp[0][0], FH - 2, ox + sp[0][1], FH - 2, "j2"); cv.rect(ox + sp[1][0], FH - 1, ox + sp[1][1], FH - 1, "j1")
        cv.rect(ox + 2, FH - 3, ox + 4, FH - 3, "j1")
    return cv


def basin_wall():
    """(night/06nov-dt: "the water is a hard rectangle") the fountain basin's granite wall under a RIM, on the
    water's side: 10 x 56 (y 424-479), the rim's ashlar carried down in 8 px courses (blocks offset by half), lit on
    its left, its wet face to the water a darker stone with a dark joint; the left wall as drawn, the right mirrored.
    Ground, not a perch: no outline"""
    W, H = 10, 56
    cv = Cv(W, H)
    cv.rect(0, 0, W - 1, H - 1, "g2")
    for y in range(0, H, 8):
        cv.rect(0, y, W - 1, y, "g1"); cv.rect(0, y + 7, W - 1, y + 7, "g3")
        jx = 4 if (y // 8) % 2 == 0 else 7
        cv.rect(jx, y + 1, jx, y + 6, "g3")
    cv.rect(0, 0, 0, H - 1, "g1")
    cv.rect(W - 3, 0, W - 2, H - 1, "g3"); cv.rect(W - 1, 0, W - 1, H - 1, "g4")   # the wet face, its joint to the water
    return cv


def build():
    return {"town_basin_wall": basin_wall(), "town_balcony56": balcony(56), "town_balcony64": balcony(64), "town_spring": spring(),
            "town_stopsign": stopsign(), "town_tier": tier(), "town_bowl": bowl(), "town_rim": rim(), "town_jet": jet()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    ap.add_argument("names", nargs="*")
    o = ap.parse_args()
    bad = 0; ims = {}
    for n, cv in build().items():
        if o.names and n not in o.names: continue
        im = cv.png(); ims[n] = im; p = os.path.join(OUT, n + ".png")
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(p, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{n}: {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z = 5; W = sum(i.shape[1] * z + 20 for i in ims.values()) + 20; H = max(i.shape[0] for i in ims.values()) * z + 40
        sh = Image.new("RGBA", (W, H), (192, 128, 112, 255)); x = 20
        for im in ims.values():
            sh.alpha_composite(Image.fromarray(im).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST), (x, H - 20 - im.shape[0] * z)); x += im.shape[1] * z + 20
        sh.save(o.sheet)
    sys.exit(1 if bad else 0)
