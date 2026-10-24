"""tools/build_spire.py: Riddarholmen church's spire, the tall Downtown's far landmark (art/scene/spire_riddarholmen.png,
36 x 260), BUILT from stamped parts (art/placement, 23 Oct 2026; docs/BIBLE.md section 3).

  python3 -I tools/build_spire.py            write it
  python3 -I tools/build_spire.py --check    fail if the file on disk is not what this script builds

The real one: a brick tower with tall round-headed louvres and a corner pinnacle on each side, under a cast-iron
openwork spire with a cross. Here it is far city (the game draws it behind the old town row, scrolling 0.3, faded
to the shore haze, arthooks.lua): front-on silhouette, no outline, edges by a darker shade, light from the left. The
spire's lattice is two families of diagonals 6 px apart (diamond holes) cut to the taper, so the sky shows through
as it does in Stockholm. Brick in running bond on a 4 x 8 grid; the louvre is drawn once and stamped.
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene", "spire_riddarholmen.png")
W, H = 36, 260
TOWER = 150                                                   # the tower from row 150 down; the spire above it
C = {"B": (156, 78, 58), "b": (120, 58, 44), "c": (182, 102, 76), "m": (190, 150, 128),   # brick, shade, lit, mortar
     "I": (58, 66, 72), "i": (92, 104, 110), "L": (214, 204, 186), "T": (172, 162, 148), "G": (44, 46, 56)}

def build():
    a = np.full((H, W), ".", dtype="<U1")
    def rect(x0, y0, x1, y1, r): a[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = r
    # the tower: 28 wide (x 4-31), brick, a stone cornice on top, a corner pinnacle each side
    for y in range(TOWER + 8, H):
        for x in range(4, 32):
            row, course = (y - TOWER) % 4, (y - TOWER) // 4
            if row == 3 or (x + (4 if course % 2 else 0)) % 8 == 3: a[y, x] = "m"
            else: a[y, x] = "B"
    rect(4, TOWER + 8, 5, H - 1, "c"); rect(30, TOWER + 8, 31, H - 1, "b")                  # lit left, shaded right
    LOUVRE = ["..GG..", ".GGGG.", "GGGGGG", "GiGGiG", "GGGGGG", "GiGGiG", "GGGGGG", "GiGGiG", "GGGGGG", "GiGGiG",
              "GGGGGG", "GiGGiG", "GGGGGG", "GGGGGG"]
    for lx in (9, 21):                                        # two tall louvres, stamped twice
        for ly in (TOWER + 18, TOWER + 58):
            for dy, r in enumerate(LOUVRE):
                for dx, ch in enumerate(r):
                    if ch != ".": a[ly + dy, lx + dx] = ch
            rect(lx - 1, ly + len(LOUVRE), lx + 6, ly + len(LOUVRE), "L")               # sill
    rect(2, TOWER + 4, 33, TOWER + 7, "T"); rect(2, TOWER + 4, 33, TOWER + 4, "L"); rect(2, TOWER + 7, 33, TOWER + 7, "b")
    for px in (2, 30):                                        # pinnacles: a shaft and a little point
        rect(px, TOWER - 6, px + 3, TOWER + 3, "T"); rect(px, TOWER - 6, px, TOWER + 3, "L")
        rect(px + 1, TOWER - 10, px + 2, TOWER - 7, "I"); a[TOWER - 11, px + 1] = "I"
    # the spire: from 26 wide at its foot to a point, an iron lattice of diamonds round holes, ribs on its edges
    top = 12
    for y in range(top, TOWER + 4):
        k = (y - top) / (TOWER + 3 - top)
        hw = 1 + 12 * k
        x0, x1 = int(round(17.5 - hw)), int(round(17.5 + hw)) - 1
        for x in range(x0, x1 + 1):
            if x in (x0, x1) or (x0 + 1 == x and hw > 4): a[y, x] = "I" if x != x0 else "i"
            else:
                if (x + y) % 6 == 0 or (x - y) % 6 == 0 or hw < 4.5 or y >= TOWER: a[y, x] = "I"      # crossing diagonals
        if (y - top) % 18 == 17: rect(x0, y, x1, y, "i")     # a ring every 18 rows
    rect(17, 0, 18, top - 1, "I"); rect(15, 3, 20, 4, "I")    # the cross
    a[0, 17] = "i"
    return a

def image(a):
    im = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            if a[y, x] != ".": im[y, x] = (*C[a[y, x]], 255)
    return im

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); o = ap.parse_args()
    im = image(build())
    if o.check:
        ok = os.path.exists(OUT) and np.array_equal(np.array(Image.open(OUT).convert("RGBA")), im)
        print(OUT, "matches the build" if ok else "DIFFERS from the build"); sys.exit(0 if ok else 1)
    Image.fromarray(im).save(OUT)
    print(OUT, W, "x", H, len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()}), "colours")
