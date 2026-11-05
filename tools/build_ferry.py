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


RB = hexc('#ce3531')                                                   # the boot top stripe, the lifebuoy's red
# rows of the topsides, light from the upper left in three bands (fix round 1: the flat white read as unfinished)
BAND = {56: P, 57: P, 58: P, 59: Wh, 60: Wh, 61: Wh, 62: Wh, 63: Wh, 64: Wh, 65: B, 66: B, 67: B, 68: B, 69: G}
for y in range(52, 79):
    x0, x1 = bow(y), stern(y)
    if y == 52 or y == 78:
        hline(x0, x1, y, K); continue
    c = (WL if y == 53 else WB if y == 54 else Rd if y == 55 else BAND[y] if y in BAND else RB if y == 70
         else Rd if y == 77 else R)
    hline(x0 + 1, x1 - 1, y, c)
    if 56 <= y <= 68:                                     # a brighter bow, a shaded stern
        put(x0 + 1, y, P); put(x1 - 1, y, B if y < 65 else G)
    if 71 <= y <= 76: put(x1 - 1, y, Rd)
    put(x0, y, K); put(x1, y, K)
    px0, px1 = bow(y - 1), stern(y - 1)                   # close the outline where the edge steps more than 1 px
    for x in range(px0 + 1, x0): put(x, y - 1, K) if y - 1 > 52 else None
    for x in range(x1 + 1, px1): put(x, y - 1, K) if y - 1 > 52 else None
# the rub rail: a varnished timber along the hull at the sheer's second line, lit on top
for y, c in ((61, WL), (62, WB), (63, WS)):
    hline(bow(y) + 2, stern(y) - 2, y, c)

# ---- deck cleats: two small bronze-grey cleats on the deck line, fore and aft ----
CLEAT = ['.KKKKK.', 'KPWWWBK', '.KWWBK.', '.KBGGK.']
for cx in (18, 206):
    for r, row in enumerate(CLEAT):
        for i, ch in enumerate(row):
            if ch != '.': put(cx + i, 48 + r, {'K': K, 'P': P, 'W': Wh, 'B': B, 'G': G}[ch])

# ---- cabin: roof y 30-34 over x 60-180, mahogany walls y 35-51 over x 61-179 ----
hline(60, 180, 30, K); hline(60, 180, 34, K)
for y, c in ((31, P), (32, Wh), (33, B)):
    hline(61, 179, y, c)
for y in (31, 32, 33): put(60, y, K); put(180, y, K)
rect(62, 35, 178, 51, WB)
hline(62, 178, 35, WS); hline(62, 178, 36, WS)           # the roof's shadow on the wall (sun high, upper left)
for y in range(37, 52): put(62, y, WL)                  # sunlit front edge
for y in range(35, 52): put(178, y, WS)                 # shaded back edge
hline(63, 177, 51, WS)                                   # the sill on the deck
for y in range(35, 52): put(61, y, K); put(179, y, K)
for y in (38, 49):                                       # two plank seams in the varnished wood
    hline(63, 177, y, WS)

# ---- portholes: the cleanest of the cut's four (cut x 72-83, y 37-45), stamped three times, 20 px apart ----
cut = np.array(Image.open(f'{SRC}/rw_ferry_cut.png').convert('RGBA'))
GLASSY = {K[:3], N[:3], S[:3], L[:3], (118, 120, 132), (57, 56, 71)}
ph = cut[37:46, 72:84].copy()
mask = np.zeros(ph.shape[:2], bool)
for r in range(ph.shape[0]):
    ks = [i for i in range(ph.shape[1]) if tuple(ph[r, i, :3]) == K[:3]]
    if ks: mask[r, ks[0]:ks[-1] + 1] = True
PORTS = (68, 88, 108)
for px in PORTS:
    for r in range(ph.shape[0]):
        for i in range(ph.shape[1]):
            if mask[r, i]:
                c = tuple(ph[r, i, :3])
                put(px + i, 40 + r, ph[r, i] if c in GLASSY else N)

# ---- lifebuoy: drawn by rule (round, 8 even bands red and white, ink rims), 15 px, hung from the roof's edge ----
import math
LCX, LCY = 135, 43
for y in range(LCY - 9, LCY + 10):
    for x in range(LCX - 9, LCX + 10):
        d = math.hypot(x - LCX, y - LCY)
        if d > 7.6 or d < 2.9: continue
        if d > 6.6 or d < 3.9: put(x, y, K); continue
        band = int(((math.degrees(math.atan2(y - LCY, x - LCX)) + 22.5) % 360) // 45) % 2
        lit = (x - LCX) + (y - LCY) < 0                       # the upper left half catches the sun
        put(x, y, (P if lit else Wh) if band else (RB if lit else R))

# ---- cabin door (aft), with a brass handle and a small window ----
rect(153, 37, 167, 51, K)
rect(154, 38, 166, 51, WS)
for y in range(38, 52): put(154, y, WB)                  # the door's lit edge
hline(155, 166, 38, WB)
rect(157, 40, 163, 44, K); rect(158, 41, 162, 43, N); put(161, 41, S); put(160, 42, S)
put(164, 46, Y); put(164, 47, K)                         # the handle
for x in range(153, 168): put(x, 51, WS if 154 <= x <= 166 else K)
hline(153, 167, 51, K)                                    # the threshold on the sill

# ---- wheelhouse: roof y 0-4 over x 97-145, body y 5-29 over x 99-143 ----
hline(97, 145, 0, K); hline(97, 145, 4, K)
for y, c in ((1, P), (2, Wh), (3, B)):
    hline(98, 144, y, c)
for y in (1, 2, 3): put(97, y, K); put(145, y, K)
for y in range(5, 30):
    put(99, y, K); put(143, y, K)
    hline(100, 142, y, Wh)
    put(100, y, P); put(142, y, B)
    if y == 5: hline(100, 142, y, B)                    # the roof's shadow
# two identical windows mirrored about col 121 (11 x 11 glass), one glint each, the same pixels
WIN = np.zeros((13, 13), int)                            # 0 ink, 1 glass, 2 glint
WIN[1:12, 1:12] = 1
for i in range(7): WIN[2 + i, 9 - i] = 2; WIN[2 + i, 10 - i] = 2
for wx in (102, 128):
    for r in range(13):
        for i in range(13):
            put(wx + i, 8 + r, (K, N, S)[WIN[r, i]])
# a lower panel line and a seam down the middle: the wheelhouse's front planking
hline(102, 140, 23, B)
for y in range(23, 30): put(121, y, B)
hline(101, 141, 29, B)

# ---- fenders: two blue fenders on ropes over the side (a harbour boat's), ink rims, rounded ends ----
for fx in (34, 196):
    put(fx + 2, 53, K); put(fx + 2, 54, K)
    hline(fx + 1, fx + 3, 55, K); hline(fx + 1, fx + 3, 64, K)
    for y in range(56, 64):
        put(fx, y, K); put(fx + 4, y, K)
        hline(fx + 1, fx + 3, y, L); put(fx + 1, y, S)

# ---- stern flag staff (rooted on the aft deck) and flag ----
put(231, 17, K)
put(230, 18, K); put(231, 18, Y); put(232, 18, K)        # the gilded knob, capped
for y in range(19, 52):
    put(230, y, K); put(231, y, WB); put(232, y, K)
rect(233, 19, 243, 27, K)
rect(233, 20, 242, 26, L)
for y in range(20, 27): put(236, y, Y); put(237, y, Y)
for x in range(233, 243): put(x, 23, Y)

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
