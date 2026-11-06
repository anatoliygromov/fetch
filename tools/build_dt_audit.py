#!/usr/bin/env python3
"""tools/build_dt_audit.py: the Downtown (tall) audit fixes of 6 Nov evening, BUILT by rule (art/dt-audit-06nov,
0 credits). Every colour is the street's own (town_ground.png's quay and kerb greys) or from art/palettes/downtown.gpl
(the sample screen's granite, steel, green and pine). No resampling, binary alpha.

  town_ground.png        240 x 68  rows 0-31 (the pavement's back edge, the cobbles, the kerb) kept pixel for pixel
                                   from the old file (art/source/dt_audit/town_ground_old.png); rows 32-67, the quay wall
                                   under the kerb, rebuilt as flat granite courses: 3 courses of 12 rows (a bed joint, a
                                   lit top row, 9 face rows, a shade row), blocks 26-46 px long in running bond, a lit
                                   left edge and a shaded right edge on every block, two face tones by block. It was a
                                   mirror-symmetric blotchy noise (the audit: "purple noise"). Wraps at x 240.
  town_quaydrain.png      20 x 22  decoration in the quay wall (arthooks.lua H.drawQuayDrains): a drain arch with a
                                   granite voussoir ring, a dark opening and an iron grate (3 bars, 1 cross bar), on a
                                   sill stone. Where the front bollards stood (their tops read as black domes).
  town_bridge_pier.png    14 x 113 decoration (H.drawBridgePiers): the footbridge's abutment, a granite pier from the
                                   arch's foot (y 311) to the quay (y 424): an impost cap, coursed shaft (12 px), plinth.
  town_punt.png           52 x 14  play, outlined (scene.lua PARASOL over water; it carries the parasol Pepper hops on):
                                   a moored green market boat; the parasol's pole stands in it, not in the water.
  town_lantern_bracket.png 18 x 12 back, faded as the lamp (stage.lua, a lamp on a ledge): a wall plate, an iron arm and a scroll
                                   brace in the lamp post's own iron; the approved lamp's lantern (rows 0-26 of
                                   lamp_post.png, not changed) hangs from its hook.

  python3 -I tools/build_dt_audit.py             write them all (riverwalk/art/scene/)
  python3 -I tools/build_dt_audit.py --check     fail if a file on disk differs from the build
  python3 -I tools/build_dt_audit.py --sheet P   all pieces at 5x on one sheet
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene")
SRC = os.path.join(ROOT, "art", "source", "dt_audit")

C = {
    # the quay wall and kerb: town_ground.png's own greys (the Look's ground grade turns them blue-violet)
    "qj": (47, 43, 47), "qs": (60, 56, 56), "qa": (72, 66, 64), "qb": (78, 72, 69), "ql": (94, 87, 81),
    "k1": (161, 158, 151), "k2": (141, 136, 129), "k3": (108, 103, 98), "qd": (28, 26, 32),
    # the sample screen's granite and steel (tools/build_dt_details.py)
    "g1": (135, 130, 120), "g2": (110, 103, 95), "g3": (77, 72, 68), "g4": (58, 50, 56),
    "s1": (132, 146, 156), "s2": (88, 100, 112), "s3": (64, 74, 86), "s4": (46, 54, 64),
    # the lamp post's iron (lamp_post.png)
    "i1": (88, 109, 134), "i2": (53, 69, 95), "i3": (15, 21, 40),
    # boat: Downtown greens and pine
    "e1": (81, 130, 109), "e2": (61, 104, 87), "e3": (48, 83, 69), "e4": (43, 74, 56),
    "p1": (127, 90, 53), "p2": (114, 81, 53), "p3": (82, 58, 36), "p4": (52, 38, 30),
    "ink": (18, 18, 26),
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

    def outline(self):
        """ink every opaque pixel on the shape's edge (4-neighbours), as tools/build_dt_details.py"""
        on = self.a != ""
        pad = np.pad(on, 1, constant_values=False)
        edge = on & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        self.a[edge] = "ink"

    def png(self, base=None):
        im = np.zeros((self.h, self.w, 4), np.uint8) if base is None else base.copy()
        for y in range(self.h):
            for x in range(self.w):
                if self.a[y, x]: im[y, x] = (*C[self.a[y, x]], 255)
        return im


# ---- the quay wall -------------------------------------------------------------------------------------------------
QUAY_TOP, COURSE = 32, 12
# block lengths per course (wrap at 240 exactly), running bond: course 1 starts at 0, 2 at 18, 3 at 9
BLOCKS = [[40, 34, 46, 30, 38, 52], [36, 44, 30, 42, 34, 54], [44, 32, 38, 46, 28, 52]]
STARTS = [0, 18, 9]


def quay_rows(cv, y0, W, ncourses=3):
    for c in range(ncourses):
        top = y0 + c * COURSE
        assert sum(BLOCKS[c]) == W
        cuts, x = [], STARTS[c]
        for i, b in enumerate(BLOCKS[c]):
            cuts.append((x % W, b, i)); x += b
        for (x0, b, i) in cuts:
            face = "qa" if (i + c) % 2 == 0 else "qb"
            for k in range(b):
                xx = (x0 + k) % W
                cv.rect(xx, top, xx, top, "qj")                                  # bed joint
                cv.rect(xx, top + 1, xx, top + COURSE - 2, face)
                cv.put(xx, top + 1, "ql")                                         # lit top row
                cv.put(xx, top + COURSE - 1, "qs")                                # shade row
            cv.rect(x0, top + 1, x0, top + COURSE - 1, "qj")                      # head joint
            cv.rect((x0 + 1) % W, top + 2, (x0 + 1) % W, top + COURSE - 2, "ql")  # the lit left edge
            cv.rect((x0 + b - 1) % W, top + 2, (x0 + b - 1) % W, top + COURSE - 2, "qs")   # shaded right edge


def ground():
    old = np.array(Image.open(os.path.join(SRC, "town_ground_old.png")).convert("RGBA"))
    H, W = old.shape[:2]
    cv = Cv(W, H)
    quay_rows(cv, QUAY_TOP, W)
    return cv, old


def quaydrain():
    cv = Cv(20, 22)
    # voussoir ring: a half circle of radius 9 (outer) / 6 (inner) centred at (10, 10), then straight jambs to the sill
    for y in range(22):
        for x in range(20):
            dx, dy = x + 0.5 - 10, y + 0.5 - 10
            r = np.hypot(dx, dy) if dy < 0 else abs(dx)
            if y >= 20: continue
            if r < 6.0: cv.put(x, y, "qd")                                       # the opening
            elif r < 9.0: cv.put(x, y, "k3" if (dx < 0 and (dy < 0 or dx < -7.5)) else "ql")
    # joints between the voussoirs (5 stones over the arch), lit ring edge
    for ang in (0.2, 0.4, 0.6, 0.8):
        a = np.pi * ang
        for rr in (6.5, 7.5, 8.5):
            cv.put(int(10 + np.cos(np.pi - a) * rr), int(10 - np.sin(a) * rr), "qj")
    for y in (13, 17):                                                            # joints on the jambs
        cv.rect(1, y, 3, y, "qj"); cv.rect(16, y, 18, y, "qj")
    # the grate: three bars and a cross bar, steel, lit left
    for bx in (6, 9, 12):
        cv.rect(bx, 4, bx + 1, 19, "s3"); cv.rect(bx, 4, bx, 19, "s2")
    cv.rect(4, 12, 15, 13, "s3"); cv.rect(4, 12, 15, 12, "s2")
    # the sill stone
    cv.rect(0, 20, 19, 21, "k3"); cv.rect(0, 20, 19, 20, "k2"); cv.rect(0, 21, 19, 21, "qs")
    return cv


def bridge_pier():
    W, H = 14, 113
    cv = Cv(W, H)
    cv.rect(0, 0, W - 1, H - 1, "g2")
    cv.rect(0, 0, W - 1, 0, "g1"); cv.rect(0, 1, W - 1, 4, "g2"); cv.rect(0, 5, W - 1, 5, "g3")   # impost cap
    cv.rect(0, 6, W - 1, 6, "g4")                                                 # its shadow line
    # coursed shaft, 12 px courses counted up from the plinth (rows H - 7 up), a plain necking under the cap
    k = 0
    top = H - 7 - 12
    while top >= 7:
        cv.rect(1, top, W - 2, top + 10, "g2")
        cv.rect(1, top, W - 2, top, "g1")
        cv.rect(1, top + 10, W - 2, top + 10, "g3")
        jx = 5 if k % 2 == 0 else 9                                              # head joint in running bond
        cv.rect(jx, top + 1, jx, top + 9, "g3")
        cv.rect(1, top + 11, W - 2, top + 11, "g4")                               # bed joint
        top -= 12; k += 1
    cv.rect(1, 7, W - 2, top + 11, "g2"); cv.rect(1, top + 11, W - 2, top + 11, "g4")   # the necking
    cv.rect(0, 7, 0, H - 7, "g1"); cv.rect(W - 1, 7, W - 1, H - 7, "g3")        # lit left arris, shaded right
    cv.rect(0, H - 6, W - 1, H - 6, "g1"); cv.rect(0, H - 5, W - 1, H - 2, "g2"); cv.rect(0, H - 1, W - 1, H - 1, "g3")   # plinth
    cv.rect(W - 1, H - 5, W - 1, H - 1, "g3")
    return cv


def punt():
    W, H = 52, 14
    cv = Cv(W, H)
    # side view, front on: a raked bow and stern (the hull narrows 1 px a row downwards), a pine gunwale, two green
    # strakes, the waterline row darkest
    for y in range(H):
        inset = 0 if y < 2 else (y - 1)
        if inset * 2 >= W: continue
        x0, x1 = inset, W - 1 - inset
        if y == 0: c = "p1"
        elif y == 1: c = "p3"
        elif y < 6: c = "e2"
        elif y == 6: c = "e4"
        elif y < 11: c = "e3"
        else: c = "e4"
        cv.rect(x0, y, x1, y, c)
        if 2 <= y < 11:
            cv.put(x0, y, "e1" if y < 6 else "e2")                               # lit bow edge
            cv.put(x1, y, "e4")                                                   # the stern's shaded edge
    cv.rect(1, 0, W - 2, 0, "p1"); cv.put(0, 0, "p2"); cv.put(W - 1, 0, "p3")
    cv.rect(2, 2, W - 3, 2, "e1")                                                # light on the top strake
    for x in (12, 26, 40):                                                       # thwarts' bolt heads
        cv.put(x, 3, "p4")
    cv.outline()                                                                 # (it carries the parasol: the
    return cv                                                                    # play piece's 1 px ink)


def lantern_bracket():
    cv = Cv(18, 12)
    cv.rect(0, 0, 3, 11, "i2"); cv.rect(1, 1, 1, 10, "i1"); cv.rect(3, 0, 3, 11, "i3")   # the wall plate
    cv.put(2, 2, "i3"); cv.put(2, 9, "i3")                                                 # its two bolts
    cv.rect(4, 1, 16, 3, "i2"); cv.rect(4, 2, 16, 2, "i1"); cv.rect(4, 3, 16, 3, "i3")     # the arm
    cv.rect(17, 1, 17, 3, "i3")                                                            # its end
    # the scroll brace: from the plate's foot curving up to the arm (a quarter circle, 1 px iron, dark under side)
    for t in np.linspace(0, np.pi / 2, 40):
        x = int(round(4 + 7 * (1 - np.cos(t)))); y = int(round(11 - 8 * np.sin(t)))
        if 4 <= x <= 11 and 3 < y <= 11:
            cv.put(x, y, "i2")
            if y + 1 <= 11 and cv.a[y + 1, x] == "": cv.put(x, y + 1, "i3")
    cv.rect(14, 4, 15, 5, "i2")                                                            # the hook (its edge all iron)
    return cv


def build():
    g, old = ground()
    return {"town_ground": (g, old), "town_quaydrain": (quaydrain(), None), "town_bridge_pier": (bridge_pier(), None),
            "town_punt": (punt(), None), "town_lantern_bracket": (lantern_bracket(), None)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    ap.add_argument("names", nargs="*")
    o = ap.parse_args()
    bad = 0; ims = {}
    for n, (cv, base) in build().items():
        if o.names and n not in o.names: continue
        im = cv.png(base); ims[n] = im; p = os.path.join(OUT, n + ".png")
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
