"""tools/build_spire.py: Riddarholmen church's spire, the tall Downtown's far landmark (art/scene/spire_riddarholmen.png,
36 x 260), BUILT from stamped parts (art/placement, 23 Oct 2026; docs/BIBLE.md section 3).

  python3 -I tools/build_spire.py            write it
  python3 -I tools/build_spire.py --check    fail if the file on disk is not what this script builds

The real one: a brick tower with tall round-headed louvres and a corner pinnacle on each side, under a cast-iron
openwork spire with a cross. Here it is far city (the game draws it behind the old town row, scrolling 0.3, faded
to the shore haze, arthooks.lua): front-on silhouette, no outline, edges by a darker shade, light from the left. The
spire's lattice is two families of diagonals 6 px apart (diamond holes) cut to the taper, so the sky shows through
as it does in Stockholm. Brick in running bond on a 4 x 8 grid; the louvre is drawn once and stamped.

art/dt-roofs-06nov: a far silhouette (the far ladder rows: no outline, 8 colours, no colour under luma 70 on its edge,
so nothing reads as ink once faded): flat brick with a lit and a shaded edge (no mortar specks), the louvres a dark
recess, the lattice in the shelter's iron ramp (lit rib on the left, shade on the right), every colour from
art/palettes/downtown.gpl.
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk", "art", "scene", "spire_riddarholmen.png")
W, H = 36, 260
TOWER = 150                                                   # the tower from row 150 down; the spire above it
C = {"B": (122, 59, 42), "b": (104, 63, 74), "c": (136, 92, 60),          # brick, its shade, lit
     "I": (88, 100, 112), "i": (132, 146, 156), "j": (64, 74, 86),        # iron, lit rib, shade rib
     "T": (135, 130, 120), "G": (58, 50, 56)}                            # stone, the louvres' dark

def build():
    a = np.full((H, W), ".", dtype="<U1")
    def rect(x0, y0, x1, y1, r): a[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = r
    # the tower: 28 wide (x 4-31), flat brick lit on the left and shaded on the right, a stone cornice, two pinnacles
    rect(4, TOWER + 8, 31, H - 1, "B")
    rect(4, TOWER + 8, 5, H - 1, "c"); rect(30, TOWER + 8, 31, H - 1, "b")
    LOUVRE = ["..GG..", ".GGGG.", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG",
              "GGGGGG", "GGGGGG", "GGGGGG", "GGGGGG"]
    for lx in (9, 21):                                        # two tall louvres, stamped twice
        for ly in (TOWER + 18, TOWER + 58):
            for dy, r in enumerate(LOUVRE):
                for dx, ch in enumerate(r):
                    if ch != ".": a[ly + dy, lx + dx] = ch
            rect(lx - 1, ly + len(LOUVRE), lx + 6, ly + len(LOUVRE), "T")               # sill
    rect(2, TOWER + 4, 33, TOWER + 7, "T"); rect(2, TOWER + 7, 33, TOWER + 7, "b")      # the cornice, its shadow
    for px in (2, 30):                                        # pinnacles: a stone shaft and an iron point
        rect(px, TOWER - 6, px + 3, TOWER + 3, "T")
        rect(px + 1, TOWER - 10, px + 2, TOWER - 7, "I"); a[TOWER - 11, px + 1] = "I"
    # the spire: from 26 wide at its foot to a point, an iron lattice of diamonds round holes, ribs on its edges
    top = 12
    for y in range(top, TOWER + 4):
        k = (y - top) / (TOWER + 3 - top)
        hw = 1 + 12 * k
        x0, x1 = int(round(17.5 - hw)), int(round(17.5 + hw)) - 1
        for x in range(x0, x1 + 1):
            if x == x0: a[y, x] = "i"
            elif x == x1: a[y, x] = "j"
            elif (x + y) % 6 == 0 or (x - y) % 6 == 0 or hw < 4.5 or y >= TOWER: a[y, x] = "I"      # crossing diagonals
        if (y - top) % 18 == 17: rect(x0 + 1, y, x1 - 1, y, "i")   # a ring every 18 rows
    rect(17, 0, 18, top - 1, "I"); rect(15, 3, 20, 4, "I")    # the cross
    a[0:top, 17] = "i"; a[3, 15] = "i"
    # a hole of 1-4 px is a pinhole at this size, not openwork: closed with iron (only whole diamonds stay open)
    seen = np.zeros(a.shape, bool)
    for y0 in range(top, TOWER + 4):
        for x0 in range(W):
            if a[y0, x0] != "." or seen[y0, x0]: continue
            comp, st, edge = [], [(y0, x0)], False
            seen[y0, x0] = True
            while st:
                y, x = st.pop(); comp.append((y, x))
                for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if not (0 <= yy < H and 0 <= xx < W): edge = True; continue
                    if a[yy, xx] == "." and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
            if not edge and len(comp) <= 4:
                for y, x in comp: a[y, x] = "I"
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
