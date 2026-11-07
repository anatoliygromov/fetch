#!/usr/bin/env python3
"""build_ferry_n07.py [--check]: the River Walk boat (ferry.png, 252 x 79), rebuilt by rule (track chars, 7 Nov 2026).

Owner, board 7 Nov, rw_ferry_v2: "terrible details". The 5 Nov boat was flat parts in a SpriteCook cut's colours
with four stamped oval portholes, a blobby lifebuoy, a plain white hull and a bare wheelhouse. Nothing is cut now:
every part is drawn by rule, on exactly the lines Pepper uses (so nothing in the level moves):
  wheelhouse roof row 0 (box x 97-145), cabin roof row 30 (box x 60-180), deck row 52 (box x 2-237), waterline
  row 70 (setpieces.lua tints the columns below world y 224 = row 70 and runs a ripple row), keel row 78.
Parts, light from the upper left, one 1 px ink outline round the boat (Pepper stands on it: an obstacle):
  HULL   a raked stem and a rounded transom; a varnished cap rail (lit row, base row) over a dark mahogany rubbing
         strake; white topsides in three bands (lit, white, cool shade under the turn of the bilge) with one plank
         seam and a navy pinstripe under the strake; a navy boot stripe; the red bottom with its dark under the waterline; an iron anchor on the bow;
         two black fenders hung over the side on short lines from the rail; two iron cleats on the deck.
  CABIN  varnished mahogany planks (a seam every 6 px, a lit top band, a dark sill band), a white roof cap with a
         1 px overhang; four identical windows (14 x 9, round corners, a chrome frame, glass in two tones with one
         glint), a lifebuoy (round, 8 even red and white bands, ink rims) on its hook, a panelled door with a round
         port and a brass handle.
  WHEELHOUSE white, a roof cap, two identical big windows with chrome frames and glints, a varnished trim band,
         a lit left edge and a shaded right edge.
  FLAG   the stern staff with a gilded knob and the Swedish flag (blue with the yellow cross), rooted on the deck.
Writes riverwalk/art/scene/ferry.png and art/source/rw_ferry_n07/ferry.aseprite. 16 colours."""
import math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

OUT = 'riverwalk/art/scene/ferry.png'
SRC = 'art/source/rw_ferry_n07'
W_, H_ = 252, 79
hexc = lambda h: (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
K = hexc('#17181f')                                                    # the ink (the family's)
P, Wh, B, G = hexc('#fbfbfa'), hexc('#e6e6e2'), hexc('#c4c8ce'), hexc('#9c9ea8')   # white ramp
R, Rd = hexc('#a42c30'), hexc('#7d1c24')                               # bottom paint
WL, WB, WS, WD = hexc('#eaa264'), hexc('#bf6d36'), hexc('#a87046'), hexc('#583626')   # varnished mahogany
N, L, S = hexc('#21273a'), hexc('#455870'), hexc('#8aa6c0')            # navy/glass dark, glass, glint
Y, RB = hexc('#f4cc69'), hexc('#ce3531')                               # brass/flag cross, lifebuoy red
img = np.zeros((H_, W_, 4), np.uint8)


def put(x, y, c):
    if 0 <= x < W_ and 0 <= y < H_: img[y, x] = c


def hline(x0, x1, y, c):
    for x in range(x0, x1 + 1): put(x, y, c)


def rect(x0, y0, x1, y1, c):
    img[y0:y1 + 1, x0:x1 + 1] = c


def bow(y):    # the stem, raked forward: the hull's left edge at row y
    return 2 + int(round(18 * ((y - 52) / 26) ** 2))


def stern(y):  # the transom, nearly upright, rounding into the bottom
    return 237 - int(round(9 * ((y - 52) / 26) ** 3))


# ---- hull ----
BANDS = {52: WL, 53: WB, 54: WD, 55: WS, 56: P}
for y in range(52, 79):
    x0, x1 = bow(y), stern(y)
    if y in BANDS: c = BANDS[y]
    elif y == 58: c = N                       # the navy sheer pinstripe
    elif y <= 61: c = Wh
    elif y == 62: c = B                       # the plank seam
    elif y <= 65: c = Wh
    elif y <= 68: c = B
    elif y <= 70: c = N                       # boot stripe (the waterline is row 70)
    elif y <= 75: c = R
    else: c = Rd
    hline(x0, x1, y, c)
    if 56 <= y <= 68: put(x1 - 1, y, B); put(x1, y, G)              # the transom's turn, in shade
    if 56 <= y <= 68: put(x0, y, P) if y < 62 else None              # the stem catches the light
# anchor on the bow (iron, drawn on the grid)
ANCHOR = ["..k..", ".kgk.", "..k..", "..k..", "..k..", "k.k.k", ".kkk."]
for j, r_ in enumerate(ANCHOR):
    for i, ch in enumerate(r_):
        if ch == 'k': put(14 + i, 57 + j, K)
        elif ch == 'g': put(14 + i, 57 + j, G)
# fenders: a short line from the rail, a black fender with a lit edge
for fx in (64, 172):
    put(fx + 2, 54, K); put(fx + 2, 55, K)
    for y in range(56, 64):
        hline(fx, fx + 4, y, N); put(fx, y, K); put(fx + 4, y, K)
        put(fx + 1, y, L)
    hline(fx + 1, fx + 3, 64, K); hline(fx + 1, fx + 3, 55, K)
# cleats on the deck (iron, sitting on the rail)
for cx in (10, 226):
    hline(cx, cx + 5, 51, G); hline(cx + 2, cx + 3, 50, G)

# ---- cabin: roof row 30 (box 60-180), walls 32-51 ----
rect(59, 30, 181, 31, P); hline(59, 181, 31, B)                       # roof cap, 1 px over the walls each side
for y in range(32, 52):
    for x in range(60, 181):
        c = WB
        if y <= 33: c = WL
        elif y >= 50: c = WD
        elif (x - 60) % 6 == 5: c = WS                                # the plank seams
        put(x, y, c)
    put(60, y, WL); put(180, y, WD)


def window(x0, y0, w, h):
    """a round-cornered window: chrome frame (lit top-left, grey bottom-right), glass dark at the top, one glint"""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            corner = (x in (x0, x0 + w - 1)) and (y in (y0, y0 + h - 1))
            if corner: continue
            edge = x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1)
            if edge: c = P if (y == y0 or x == x0) else G
            else: c = N if y <= y0 + 2 else L
            put(x, y, c)
    for i in range(min(w, h) - 3):                                    # the glint: one 45-degree line, 2 px
        put(x0 + 3 + i, y0 + h - 2 - i, S); put(x0 + 4 + i, y0 + h - 2 - i, S)


for wx in (66, 86, 106, 126): window(wx, 35, 14, 9)
# lifebuoy: 13 px, 8 even bands, ink rims, on a brass hook
cx, cy, ro, ri = 152, 42, 6.4, 3.0
put(152, 35, Y)
for y in range(35, 50):
    for x in range(145, 160):
        r_ = math.hypot(x - cx, y - cy)
        if ri < r_ <= ro:
            a = (math.degrees(math.atan2(y - cy, x - cx)) + 22.5) % 360
            c = RB if int(a // 45) % 2 == 0 else P
            if r_ > ro - 1 or r_ <= ri + 1: c = K
            put(x, y, c)
# door: frame, two panels, a round port, a brass handle
rect(162, 34, 176, 51, WD)
rect(163, 35, 175, 51, WS)
for y in range(36, 51):
    for x in range(164, 175): put(x, y, WB)
hline(164, 174, 36, WL)
hline(164, 174, 44, WS)
for y in range(37, 43):
    for x in range(166, 173):
        if math.hypot(x - 169, y - 39.5) <= 2.9: put(x, y, L if y > 38 else N)
put(167, 38, S)
put(173, 47, Y)

# ---- wheelhouse: roof row 0 (box 97-145), walls 2-29 ----
rect(96, 0, 146, 1, P); hline(96, 146, 1, B)
for y in range(2, 30):
    for x in range(97, 146):
        c = Wh
        if x <= 98: c = P
        elif x >= 144: c = B
        if y >= 27: c = B if x < 144 else G
        put(x, y, c)
hline(97, 145, 19, WL); hline(97, 145, 20, WB); hline(97, 145, 21, WD)   # a varnished trim band, as the cabin
for wx in (101, 123): window(wx, 5, 19, 12)

# ---- stern flag staff and flag ----
put(231, 17, Y)
for y in range(18, 52): put(231, y, WB)
rect(233, 19, 242, 26, L)
for y in range(19, 27): put(236, y, Y); put(237, y, Y)
hline(233, 242, 22, Y); hline(233, 242, 23, Y)

# ---- one ink outline round everything (outside pixels next to the boat), kept inside the image ----
m = img[..., 3] > 0
out = np.zeros_like(m)
for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    sh = np.zeros_like(m); ys0, ys1 = max(0, dy), H_ + min(0, dy); xs0, xs1 = max(0, dx), W_ + min(0, dx)
    sh[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]; out |= sh
out &= ~m
img[out] = K
for sl in (np.s_[0, :], np.s_[:, 0], np.s_[:, -1]):                   # the border rows keep their ink
    e = m[sl]; img[sl][e] = K
if __name__ == '__main__':
    if '--check' in sys.argv:
        ok = np.array_equal(np.array(Image.open(OUT).convert('RGBA')), img); print('ferry', 'OK' if ok else 'DIFFERS'); sys.exit(0 if ok else 1)
    os.makedirs(SRC, exist_ok=True)
    Image.fromarray(img).save(OUT); aseprite_io.write(f'{SRC}/ferry.aseprite', [img])
    print(OUT, W_, 'x', H_, len(np.unique(img[img[..., 3] > 0][:, :3], axis=0)), 'colours')
