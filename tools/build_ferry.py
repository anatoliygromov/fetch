#!/usr/bin/env python3
"""build_ferry.py: the River Walk boat (5 Nov 2026), the polish of the SpriteCook cut art/source/rw_ferry/rw_ferry_cut.png.

  python3 -I tools/build_ferry.py      -> art/source/rw_ferry/rw_ferry.png (252 x 79), edits.json, .aseprite

Why a rebuild on the cut's design and not pixel touch-ups: the render (art/gen/renders/rw_ferry_n5a.png) gives the
design (white launch, mahogany cabin with portholes and a lifebuoy, white wheelhouse, red bottom, stern flag) and the
colours, but after the snap to the level palette its fills were mottled (red specks in the wood, grey specks in the
white), its foredeck was drawn from above (a strip of deck planks: "no tops"), its bow stood 5 px above Pepper's deck
and its wheelhouse 5 px under her roof box. So every flat part is drawn by rule in the cut's own colours, on the
exact lines Pepper stands on, and the detailed parts are stamped from the cut: one porthole (the cleanest of the
four, stamped four times, identical and evenly spaced) and the lifebuoy. Every pixel that differs from the cut
(placed where the game draws it) is listed in edits.json.

Lines (image row y = world y - 154; x = level x - 1560, the BOAT prop's ax):
  wheelhouse roof y 0 (box 97-145), cabin roof y 30 (box 60-180), deck y 52 (box 2-237), waterline y 70, bottom y 78.
The image is drawn bottom-anchored at world y 233 (level ay), so nothing in the level moves."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

SRC = 'art/source/rw_ferry'
W_, H_ = 252, 79
hexc = lambda h: (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
K = hexc('#010102')                                                    # the one ink
P, Wh, B, G = hexc('#fbfbfa'), hexc('#e1e1e1'), hexc('#b5b9bf'), hexc('#9c9ea8')   # white ramp
R, Rd = hexc('#7d1c24'), hexc('#5a2e2a')                               # bottom paint, its dark
WL, WB, WS = hexc('#d49a54'), hexc('#bf6d36'), hexc('#a86e3e')         # mahogany light, base, shade
N, S, L = hexc('#21273a'), hexc('#5f7387'), hexc('#455870')            # glass, glint, glass mid
Y = hexc('#f4cc69')                                                    # flag cross
CUT_DX, CUT_DY = 1, 5        # cut pixel (cx, cy) sits at image (cx + 1, cy + 5): deck rows meet (cut 47 = image 52)

img = np.zeros((H_, W_, 4), np.uint8)


def put(x, y, c):
    if 0 <= x < W_ and 0 <= y < H_: img[y, x] = c


def hline(x0, x1, y, c):
    for x in range(x0, x1 + 1): put(x, y, c)


def rect(x0, y0, x1, y1, c):
    img[y0:y1 + 1, x0:x1 + 1] = c


# ---- hull: deck line y 52, rubbing strake 53-55, white topsides 56-69, boot line 70, red bottom 71-77, keel 78 ----
def bow(y):    # the stem, raked forward: x of the hull's left edge at row y
    return 2 + int(round(18 * ((y - 52) / 26) ** 2))


def stern(y):  # the transom, nearly upright, rounding into the bottom
    return 237 - int(round(9 * ((y - 52) / 26) ** 3))


for y in range(52, 79):
    x0, x1 = bow(y), stern(y)
    if y == 52 or y == 78:
        hline(x0, x1, y, K); continue
    c = (WL if y == 53 else WB if y == 54 else Rd if y == 55 else P if y == 56 else
         B if y in (67, 68) else G if y == 69 else Rd if y == 70 else Wh if y < 67 else R)
    hline(x0 + 1, x1 - 1, y, c)
    if 56 <= y <= 66:                                     # the sun from the upper left: a bright bow, a shaded stern
        put(x0 + 1, y, P); put(x1 - 1, y, B); put(x1 - 2, y, B if y > 60 else c)
    if 71 <= y <= 77: put(x1 - 1, y, Rd)
    put(x0, y, K); put(x1, y, K)
    # close the outline where the edge steps by more than one pixel between rows
    px0, px1 = bow(y - 1), stern(y - 1)
    for x in range(px0 + 1, x0): put(x, y - 1, K) if y - 1 > 52 else None
    for x in range(x1 + 1, px1): put(x, y - 1, K) if y - 1 > 52 else None

# ---- cabin: roof y 30-34 over x 60-180, mahogany walls y 35-51 over x 61-179 ----
hline(60, 180, 30, K); hline(60, 180, 34, K)
for y, c in ((31, P), (32, Wh), (33, B)):
    hline(61, 179, y, c)
put(60, 31, K); put(60, 32, K); put(60, 33, K); put(180, 31, K); put(180, 32, K); put(180, 33, K)
rect(62, 35, 178, 51, WB)
hline(62, 178, 35, WS); hline(62, 178, 36, WS)           # the roof's shadow on the wall (sun high, upper left)
for y in range(37, 52): put(62, y, WL)                  # sunlit front edge
for y in range(35, 52): put(178, y, WS)                 # shaded back edge
hline(63, 177, 51, WS)                                   # the sill on the deck
for y in range(35, 52): put(61, y, K); put(179, y, K)
for y in (38, 49):                                       # two plank seams in the varnished wood
    hline(63, 177, y, WS)

# ---- portholes: the cleanest of the cut's four (cut x 72-83, y 37-45), stamped four times, 22 px apart ----
cut = np.array(Image.open(f'{SRC}/rw_ferry_cut.png').convert('RGBA'))
GLASSY = {K[:3], N[:3], S[:3], L[:3], (118, 120, 132), (57, 56, 71)}
ph = cut[37:46, 72:84].copy()
keep = np.array([[tuple(p[:3]) in GLASSY for p in row] for row in ph])
# the ring: keep the ink ring and everything inside it (fill each row between its first and last ink)
mask = np.zeros(keep.shape, bool)
for r in range(ph.shape[0]):
    ks = [i for i in range(ph.shape[1]) if tuple(ph[r, i, :3]) == K[:3]]
    if ks: mask[r, ks[0]:ks[-1] + 1] = True
PORTS = (70, 92, 114, 136)
for px in PORTS:
    for r in range(ph.shape[0]):
        for i in range(ph.shape[1]):
            if mask[r, i]:
                c = tuple(ph[r, i, :3])
                put(px + i, 40 + r, ph[r, i] if c in GLASSY else N)

# ---- lifebuoy: drawn by rule (round, 8 even bands red and white, ink rims), on the cabin's back wall ----
import math
LCX, LCY = 165, 43
for y in range(LCY - 8, LCY + 9):
    for x in range(LCX - 8, LCX + 9):
        d = math.hypot(x - LCX, y - LCY)
        if d > 6.6 or d < 2.4: continue
        if d > 5.6 or d < 3.4: put(x, y, K); continue
        band = int(((math.degrees(math.atan2(y - LCY, x - LCX)) + 22.5) % 360) // 45) % 2
        lit = (x - LCX) + (y - LCY) < 0                       # the upper left half catches the sun
        put(x, y, (P if lit else Wh) if band else (R if lit else Rd))
put(LCX, LCY - 7, K)                                            # the cord it hangs on, to the roof's edge
for y in range(35, LCY - 6): put(LCX, y, WS)

# ---- wheelhouse: roof y 0-4 over x 97-145, body y 5-29, its front raked (x 101 at the top to 98 at the foot) ----
hline(97, 145, 0, K); hline(97, 145, 4, K)
for y, c in ((1, P), (2, Wh), (3, B)):
    hline(98, 144, y, c)
for y in (1, 2, 3): put(97, y, K); put(145, y, K)
for y in range(5, 30):
    put(99, y, K); put(143, y, K)
    hline(100, 142, y, Wh)
    put(100, y, P); put(142, y, B)
    if y == 5: hline(100, 142, y, B)                    # the roof's shadow
# windscreen (the front pane, taller) and the side window: glass with one glint each
rect(102, 8, 114, 20, K); rect(103, 9, 113, 19, N)
for i in range(8): put(111 - i, 10 + i, S); put(112 - i, 10 + i, S)
rect(119, 8, 132, 18, K); rect(120, 9, 131, 17, N)
for i in range(6): put(128 - i, 10 + i, S); put(129 - i, 10 + i, S)

# ---- fenders: two blue fenders on ropes over the side (a harbour boat's), ink rims ----
for fx in (34, 196):
    put(fx + 2, 53, K); put(fx + 2, 54, K)
    rect(fx, 55, fx + 4, 63, K)
    rect(fx + 1, 56, fx + 3, 62, L); put(fx + 1, 56, K); put(fx + 3, 56, K); put(fx + 1, 62, K); put(fx + 3, 62, K)
    put(fx, 55, Wh); put(fx + 4, 55, Wh); put(fx, 63, Wh); put(fx + 4, 63, Wh)   # rounded ends
    for y in range(57, 62): put(fx + 1, y, S)

# ---- stern flag staff and flag (beyond Pepper's deck box, x 238 on) ----
for y in range(19, 53):
    put(238, y, K); put(239, y, WB if y > 19 else K); put(240, y, K)
put(239, 19, Y)                                          # the gilded knob
rect(241, 20, 251, 28, K)
rect(241, 21, 250, 27, L)
for y in range(21, 28): put(244, y, Y); put(245, y, Y)
for x in range(241, 251): put(x, 24, Y)
put(241, 21, L)

# ---- write, then list every pixel that differs from the cut as the game places it ----
os.makedirs(SRC, exist_ok=True)
out = Image.fromarray(img, 'RGBA')
out.save(f'{SRC}/rw_ferry.png')
ref = np.zeros_like(img)
ch, cw = cut.shape[:2]
ys, xs = slice(CUT_DY, min(H_, CUT_DY + ch)), slice(CUT_DX, min(W_, CUT_DX + cw))
ref[ys, xs] = cut[:ys.stop - CUT_DY, :xs.stop - CUT_DX]
ref[ref[..., 3] == 0] = 0
diff = np.argwhere(np.any(ref != img, axis=2))
edits = {'asset': 'rw_ferry', 'base': f'{SRC}/rw_ferry_cut.png placed at +{CUT_DX},+{CUT_DY}',
         'method': 'flat parts drawn by rule in the cut colours; porthole x4 and lifebuoy stamped from the cut',
         'changed': int(len(diff)), 'of': int((img[..., 3] > 0).sum()),
         'pixels': [[int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in img[y, x])] for y, x in diff]}
json.dump(edits, open(f'{SRC}/edits.json', 'w'))
aseprite_io.write(f'{SRC}/rw_ferry.aseprite', [img], layer='rw_ferry')
print('rw_ferry', out.size, 'colours', len(np.unique(img[img[..., 3] > 0][:, :3], axis=0)), 'changed', len(diff))
