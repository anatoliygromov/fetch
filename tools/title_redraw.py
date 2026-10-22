#!/usr/bin/env python3
# THE TITLE SCREEN, HAND-PIXELED. This script is the source of truth for riverwalk/art/title/*.png and
# riverwalk/title_data.lua (tools/make_title.py, which cut the AI painting down to 320x240, is the old pipeline,
# kept for reference only; do not run it, it would overwrite this picture).
#
# Every pixel here is authored: shapes (polygons, ellipses, lines), indexed pixel grids for the small key details
# (Pepper's eye, wink, nose, tongue, the paw print, the bird), and shading rules written out below (light from the
# upper left, 3 to 5 tone ramps per material). The old 320x240 picture was used only as a sketch for positions
# and silhouettes; no colour is read from it or from the painting. Colours come only from PAL (32 colours on the
# VGA 6-bit grid), and the swatch is written to source_title/palette_redraw.png.
#
#   python3 tools/title_redraw.py [preview_dir]      (preview_dir: also writes 1x/3x previews there)
#
# Layers written (title.lua draws them; positions go to title_data.lua):
#   base.png        the whole screen
#   press_off.png   the PRESS ANY KEY box without its text (the text blinks)
#   eye_closed.png  Pepper's open eye, closed (she blinks)
#   bird.png        a gull, 3 frames (wings up, level, down)
#   logo_hi.png     the logo's letters and paw, one ramp step brighter (the shine sweep)
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'riverwalk', 'art', 'title')
W, H = 320, 240

# ------------------------------------------------------------------------------------------------ palette
def vga(c):                          # snap to the 6-bit VGA grid (0..63 per channel, shown as 0..255)
    return tuple(int(round(round(v * 63 / 255) * 255 / 63)) for v in c)

PAL_SRC = [  # name, colour (before snapping), ramp
    ('OUT',    (12, 12, 28)),     # outline: Pepper, railing, text shade
    ('NAVY',   (24, 36, 93)),     # logo outline, banner, iron
    ('P_SH',   (26, 26, 44)),     # Pepper: shadow (cool, violet)
    ('P_BS',   (40, 42, 62)),     # Pepper: base black
    ('P_MD',   (64, 72, 101)),    # Pepper: sheen
    ('P_HI',   (105, 121, 154)),  # Pepper: highlight (cool blue-grey)
    ('EDGE',   (4, 61, 150)),     # HUD edge blue; deep water
    ('BLUE',   (4, 109, 231)),    # HUD blue; sky top
    ('SKY2',   (40, 142, 239)),   # sky middle
    ('RIM',    (81, 162, 239)),   # HUD rim blue; lower sky, light water
    ('SKY4',   (150, 208, 247)),  # horizon, cloud shade
    ('WHITE',  (255, 255, 255)),
    ('COPPER', (93, 174, 150)),   # copper roofs (verdigris)
    ('G_DK',   (16, 77, 61)),     # foliage ramp, cool dark to warm light
    ('G_MD',   (36, 125, 57)),
    ('G_LT',   (101, 178, 57)),
    ('G_HI',   (186, 219, 77)),
    ('BRN_DK', (77, 45, 40)),     # bark, stone joints, wood
    ('BRN',    (138, 85, 57)),    # bark, brick
    ('SAND',   (198, 158, 113)),  # paving, stone
    ('CREAM',  (239, 219, 174)),  # paving light, facades
    ('PK_DK',  (158, 20, 89)),    # bandana ramp
    ('PK',     (231, 52, 138)),
    ('PK_LT',  (251, 134, 190)),
    ('TNG',    (219, 85, 105)),   # tongue
    ('TNG_LT', (251, 154, 154)),
    ('EYE_BR', (101, 40, 24)),    # eye, also dark brick
    ('EYE_AM', (194, 109, 36)),   # eye amber, ochre facades
    ('LG_RED', (206, 61, 20)),    # logo ramp: shadow orange-red to pale yellow
    ('LG_OR',  (243, 134, 28)),
    ('LG_YE',  (251, 206, 49)),
    ('LG_PL',  (251, 243, 150)),
]
PAL = [vga(c) for _, c in PAL_SRC]
for i, (n, _) in enumerate(PAL_SRC): globals()[n] = i
assert len(PAL) <= 32 and len(set(PAL)) == len(PAL)
NONE = 255                           # transparent in layer canvases

C = np.full((H, W), SKY2, np.uint8)  # the canvas: palette indices

# ------------------------------------------------------------------------------------------------ helpers
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
YY, XX = np.mgrid[0:H, 0:W]

def poly(pts):
    im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=1, outline=1)
    return np.array(im, bool)

def ell(cx, cy, rx, ry):             # the same row-by-row ellipse as title.lua: clean, symmetric steps
    m = np.zeros((H, W), bool)
    for dy in range(-ry, ry + 1):
        k = np.sqrt(max(0.0, 1 - (dy / (ry + 0.5)) ** 2))
        hw = int(np.floor(rx * k + 0.5))
        y = cy + dy
        if hw > 0 and 0 <= y < H: m[y, max(0, cx - hw):max(0, min(W, cx + hw))] = True
    return m

def rect(x0, y0, x1, y1):            # inclusive, clipped to the screen
    m = np.zeros((H, W), bool)
    if x1 >= 0 and y1 >= 0: m[max(0, y0):min(H, y1 + 1), max(0, x0):min(W, x1 + 1)] = True
    return m

def line(x0, y0, x1, y1):            # Bresenham: steps in even runs on clean slopes
    m = np.zeros((H, W), bool)
    dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        if 0 <= x0 < W and 0 <= y0 < H: m[y0, x0] = True
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy
    return m

def polyline(pts):
    m = np.zeros((H, W), bool)
    for a, b in zip(pts, pts[1:]): m |= line(*a, *b)
    return m

def shift(m, dx, dy):
    o = np.zeros_like(m)
    ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
    o[ys, xs] = m[yd, xd]; return o

N4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
def inner_edge(m): return m & ~ndi.binary_erosion(m, N4, border_value=1)
def outer_ring(m, s=N4): return ndi.binary_dilation(m, s) & ~m
def grow(m, n=1, s=N4): return ndi.binary_dilation(m, s, iterations=n) if n else m

def put(m, c, canvas=None):
    (C if canvas is None else canvas)[m] = c

def stamp(rows, x, y, key, canvas=None, mask_out=None):
    cv = C if canvas is None else canvas
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in key and 0 <= y + j < H and 0 <= x + i < W:
                cv[y + j, x + i] = key[ch]
                if mask_out is not None: mask_out[y + j, x + i] = True

def bayer_band(m, y0, y1, c_top, c_bot):
    # ordered dither from c_top to c_bot over rows y0..y1, in three equal steps of a 2x2 pattern: 25%, 50% (a clean
    # checker), 75%. No sparser levels, so there are no dotted lines, only even textures.
    B2 = np.array([[0, 2], [3, 1]])
    step = np.clip(((YY - y0) * 3) // max(1, (y1 - y0 + 1)), 0, 2) + 1      # 1, 2, 3 quarters of c_bot
    lower = B2[YY % 2, XX % 2] < step
    C[m & ~lower] = c_top; C[m & lower] = c_bot

def checker(m, c, phase=0):
    C[m & (((XX + YY + phase) % 2) == 0)] = c

def deorphan(m, canvas=None, passes=2):
    # a pixel with no same-coloured 8-neighbour takes its most common neighbour colour (no orphan pixels)
    cv = C if canvas is None else canvas
    for _ in range(passes):
        ys, xs = np.nonzero(m)
        changes = []
        for y, x in zip(ys, xs):
            if y == 0 or x == 0 or y == H - 1 or x == W - 1: continue
            nb = cv[y - 1:y + 2, x - 1:x + 2].ravel()
            nb = np.delete(nb, 4)
            if not (nb == cv[y, x]).any():
                v, k = np.unique(nb, return_counts=True); changes.append((y, x, v[np.argmax(k)]))
        for y, x, v in changes: cv[y, x] = v

def light_field(m, sigma, L=(-0.55, -0.62, 0.56), strength=3.0):
    # a soft dome over the mask; returns how much each pixel faces the light (upper left, a bit towards us)
    h = ndi.gaussian_filter(m.astype(float), sigma)
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * strength * sigma, -gy * strength * sigma, np.ones_like(h)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    L = np.array(L) / np.linalg.norm(L)
    return (nx * L[0] + ny * L[1] + nz * L[2]) / n

def ramp_shade(m, sigma, ramp, cuts, **kw):
    # quantise the light field into a ramp: ramp[k] where field passes cuts[k-1]
    f = light_field(m, sigma, **kw)
    out = np.full((H, W), ramp[0], np.uint8)
    for k, t in enumerate(cuts): out[f >= t] = ramp[k + 1]
    C[m] = out[m]
    return f

def sheen(m, a, b):                  # a band inside m, between a and b px in from its upper-left edge
    return m & shift(m, a, a) & ~shift(m, b, b)
def shade_rim(m, d, dx=-1, dy=-1):   # the lower-right rim of m, d px deep
    return m & ~shift(m, d * dx, d * dy)

def leafclump(cx, cy, r, back=False):
    # a clump of leaves: a big lobe with four smaller lobes round it (a bumpy, leafy edge), dark on the
    # lower right, a lit band on the upper left, a few bright leaves at the top left
    s = max(2, int(r * 0.6))
    m = (ell(cx, cy, r, max(2, r * 4 // 5)) | ell(cx - r * 2 // 3, cy + r // 3, s, max(1, s * 4 // 5))
         | ell(cx + r * 2 // 3, cy + r // 4, s, max(1, s * 4 // 5)) | ell(cx - r // 4, cy - r * 3 // 5, s, max(1, s * 4 // 5))
         | ell(cx + r // 3, cy - r // 2, max(1, s - 1), max(1, (s - 1) * 4 // 5)))
    if back:
        put(m, G_DK); put(sheen(m, 1, 3), G_MD)
    else:
        put(m, G_MD); put(shade_rim(m, 3), G_DK); put(sheen(m, 1, 4), G_LT)
        put(sheen(m, 1, 2) & ell(cx - r // 2, cy - r // 2, r // 2 + 1, max(1, r // 2)), G_HI)
    return m

# ------------------------------------------------------------------------------------------------ the font
def load_font():
    src = open(os.path.join(ROOT, 'riverwalk', 'bigfont.lua')).read()
    G = {}
    for m in re.finditer(r'(?:(\w)|\["(.)"\])\s*=\s*\{((?:\s*"[.#]{5}",?){7})\s*\}', src):
        ch = m.group(1) or m.group(2)
        G[ch] = re.findall(r'"([.#]{5})"', m.group(3))
    return G
FONT = load_font()

def text_width(s): return len(s) * 6 - 1
def draw_text(s, x, y, c, canvas=None, shade=None):
    # the game's 5x7 font at 1x, like hud.lua's U.center: the shade 1 px down-right, then the letters
    for layer, (ox, oy, col) in enumerate(((1, 1, shade), (0, 0, c))):
        if col is None: continue
        for i, ch in enumerate(s.upper()):
            g = FONT[ch]
            for j, r in enumerate(g):
                for k, b in enumerate(r):
                    if b == '#': (C if canvas is None else canvas)[y + j + oy, x + i * 6 + k + ox] = col

# ================================================================================================ the scene
# ---- sky: four bands, joined by 4x4 ordered dither
sky = rect(0, 0, W - 1, H - 1)
put(sky, BLUE)
bayer_band(rect(0, 20, W - 1, 31), 20, 31, BLUE, SKY2)
put(rect(0, 32, W - 1, 65), SKY2)
bayer_band(rect(0, 66, W - 1, 77), 66, 77, SKY2, RIM)
put(rect(0, 78, W - 1, 100), RIM)
bayer_band(rect(0, 101, W - 1, 109), 101, 109, RIM, SKY4)
put(rect(0, 110, W - 1, 150), SKY4)

# ---- clouds: cumulus heaps of puffs, each puff a shade ellipse with a white one up-left of it; flat bottoms
def cloud(puffs, base_y):
    m = np.zeros((H, W), bool)
    for cx, cy, rx, ry in puffs: m |= ell(cx, cy, rx, ry)
    m &= YY <= base_y
    put(m, SKY4)
    for cx, cy, rx, ry in puffs:
        w = ell(cx - 1, cy - 2, max(1, rx - 2), max(1, ry - 2)) & m & (YY <= base_y - 2)
        put(w, WHITE)
    put(m & (YY >= base_y - 1) & ~shift(m & (YY >= base_y - 1), 0, 0) | (m & (YY == base_y)), RIM)
    return m

cloud([(48, 86, 10, 7), (60, 80, 11, 10), (74, 84, 9, 8), (86, 90, 8, 6), (38, 92, 7, 5)], 95)
cloud([(150, 118, 9, 6), (163, 112, 10, 8), (177, 116, 9, 7), (190, 119, 8, 5)], 123)
cloud([(246, 116, 8, 6), (258, 110, 10, 9), (272, 113, 9, 8), (285, 108, 11, 10), (300, 112, 10, 8),
       (313, 116, 9, 6)], 124)
cloud([(302, 80, 7, 4), (312, 78, 8, 5), (320, 81, 6, 4)], 84)

# ---- far shore: low hills in haze (light blue, lit faces lighter)
far = poly([(140, 136), (150, 128), (164, 126), (180, 129), (196, 124), (214, 127), (240, 125), (262, 128),
            (284, 123), (306, 126), (320, 124), (320, 142), (140, 142)])
put(far, RIM)
put(inner_edge(far) & ~shift(far, -1, -1) & (YY < 134), SKY4)

# ---- the city: Gamla stan facades along the water, roofs of copper and tile, windows in rows
WATER_Y = 141                      # the waterline at the far quay
def house(x0, w, h, wall, wall_sh, roof, roof_h=3, gable=False, win=NAVY):
    y1 = WATER_Y - 1; y0 = y1 - h + 1
    put(rect(x0, y0, x0 + w - 1, y1), wall)
    put(rect(x0 + w - 1, y0, x0 + w - 1, y1), wall_sh)               # right side in shade
    if gable:
        cx = x0 + (w - 1) / 2
        for j in range(roof_h + 2):
            hw = int(round((w / 2 + 0.5) * j / (roof_h + 1)))
            put(rect(int(np.floor(cx - hw + 0.5)), y0 - roof_h - 2 + j, int(np.floor(cx + hw)), y0 - roof_h - 2 + j)
                & (YY < y0), roof)
    else:
        put(rect(x0, y0 - roof_h, x0 + w - 1, y0 - 1), roof)
        put(rect(x0, y0 - roof_h, x0 + w - 1, y0 - roof_h), CREAM if roof != CREAM else SAND)
    for wy in range(y0 + 2, y1 - 1, 3):                                 # window rows: one dark pixel each 2
        for wx in range(x0 + 1, x0 + w - 1, 2):
            C[wy, wx] = win

# left to right (x 138 .. 320); Pepper's ear covers the start
house(138, 8, 9, CREAM, SAND, COPPER, 2)
house(146, 7, 12, EYE_AM, BRN, LG_RED, 2, gable=True)
house(153, 9, 10, SAND, BRN, COPPER, 2)
house(162, 6, 13, CREAM, SAND, LG_RED, 2, gable=True)
house(168, 8, 9, BRN, BRN_DK, COPPER, 2)
house(176, 7, 11, CREAM, SAND, BRN, 2)
house(183, 9, 8, EYE_AM, BRN, COPPER, 2)
house(192, 6, 12, SAND, BRN, LG_RED, 2, gable=True)
house(198, 6, 9, CREAM, SAND, COPPER, 2)
# Riddarholmen church: brick nave and its open iron spire (x 176..183)
put(rect(172, 124, 182, 140), BRN); put(rect(182, 124, 182, 140), BRN_DK); put(rect(172, 124, 172, 140), EYE_AM)
for wy in (127, 132):
    for wx in (175, 179): put(rect(wx, wy, wx, wy + 2), NAVY)
put(rect(171, 122, 183, 123), NAVY)
sp = np.zeros((H, W), bool)
for j in range(0, 19):                                            # the spire: 6 wide at the bottom, to a point
    hw = 3 - (j * 3) // 19
    y = 121 - j
    sp |= rect(177 - hw, y, 177 + hw, y)
put(sp, NAVY)
put(sp & (((YY // 2) % 2) == 0) & (XX == 177), RIM)              # openwork: the sky shows through the lattice
put(rect(177, 100, 177, 102), NAVY)

# City Hall (Stadshuset): the long brick hall on the water and its square tower with the three gold crowns
put(rect(204, 128, 252, 140), BRN)
put(rect(204, 128, 252, 128), EYE_AM)                            # the cornice catches the light
put(rect(204, 129, 204, 140), EYE_AM)
for wx in range(207, 252, 4):                                      # arches on the water
    put(rect(wx, 136, wx + 1, 140), BRN_DK); C[135, wx] = BRN_DK; C[135, wx + 1] = BRN_DK
for wx in range(207, 252, 3): C[131, wx] = BRN_DK
put(rect(204, 126, 216, 127), COPPER)                              # a copper roof on the left wing
tower = rect(222, 112, 233, 128)                                   # (all below the banner)
put(tower, BRN)
put(rect(222, 112, 224, 128), EYE_AM)                              # lit left face
put(rect(232, 112, 233, 128), BRN_DK)                              # shaded right face
for wy in (115, 120): put(rect(226, wy, 226, wy + 2), BRN_DK); put(rect(229, wy, 229, wy + 2), BRN_DK)
put(rect(221, 110, 234, 111), CREAM)                               # the white parapet
put(rect(234, 110, 234, 111), SAND)
put(poly([(223, 109), (232, 109), (230, 105), (225, 105)]), COPPER)  # the copper lantern
put(rect(223, 107, 224, 109), SKY4)
put(rect(231, 106, 232, 109), G_DK)
put(rect(226, 102, 228, 104), COPPER); put(rect(228, 102, 228, 104), G_DK)
stamp(["Y.Y.Y", "YYYYY"], 225, 100, {'Y': LG_YE})                  # the three crowns, gold
C[100, 227] = LG_PL

house(253, 7, 9, CREAM, SAND, COPPER, 2)
house(260, 9, 12, SAND, BRN, LG_RED, 2, gable=True)
house(269, 6, 9, EYE_AM, BRN, COPPER, 2)
house(275, 8, 11, CREAM, SAND, BRN, 2)

# trees on the far quay between the houses: small dark clumps
for cx, cy, rx, ry in [(145, 138, 4, 3), (186, 139, 4, 2), (200, 139, 3, 2), (241, 139, 3, 2), (266, 139, 3, 2)]:
    m = ell(cx, cy, rx, ry); put(m, G_DK); put(m & shift(m, 1, 1) & ~shift(m, 2, 2), G_MD)

# ---- water: from the light far water to the deep near water, ordered dither between
water = rect(130, WATER_Y, W - 1, 186)
put(water, RIM)
bayer_band(water & (YY >= 148) & (YY <= 156), 148, 156, RIM, SKY2)
put(water & (YY > 156) & (YY < 168), SKY2)
bayer_band(water & (YY >= 168) & (YY <= 176), 168, 176, SKY2, BLUE)
put(water & (YY > 176), BLUE)

# ---- the bridge (Riksbron style stone arches), far left, x 138..210, deck at y 142..145
deck = rect(138, 142, 212, 145)
put(deck, SAND); put(rect(138, 142, 212, 142), CREAM)
for ax in range(146, 212, 16):                                     # piers and dark arch holes
    hole = ell(ax, 148, 5, 3) & (YY >= 146)
    put(rect(ax - 7, 146, ax + 7, 148) & ~hole, SAND)
    put(hole, EDGE)
    put(rect(ax - 7, 146, ax - 7, 148), CREAM)
put(rect(138, 145, 212, 145), BRN)
for x in range(139, 212, 3): C[141, x] = NAVY                     # the railing on the bridge: posts

# reflections under the city and the bridge: broken streaks in the deeper colour, deliberate lengths
REFL = [(140, 150, 9), (156, 151, 6), (170, 150, 10), (186, 151, 5), (196, 150, 7), (212, 143, 8), (224, 144, 10),
        (238, 143, 6), (248, 144, 5), (256, 143, 9), (270, 144, 7), (283, 143, 5),
        (214, 146, 6), (226, 147, 6), (244, 146, 4), (262, 146, 6), (226, 150, 4)]
for x, y, n in REFL: put(rect(x, y, x + n - 1, y), SKY2)
put(rect(225, 143, 231, 143), BRN); put(rect(226, 145, 230, 145), BRN)   # the tower's warm reflection
put(rect(227, 148, 229, 148), BRN)
# ripples: short light dashes on the darker water, staggered
RIPPLE = [(150, 160, 4), (166, 158, 3), (184, 162, 5), (205, 159, 3), (222, 163, 4), (196, 168, 6), (214, 171, 3),
          (236, 169, 4), (176, 172, 5), (156, 170, 3), (258, 172, 5), (284, 170, 4), (300, 168, 3), (148, 178, 4),
          (190, 180, 6), (226, 179, 4), (270, 181, 5), (306, 178, 4), (168, 183, 3), (246, 184, 5)]
for x, y, n in RIPPLE: put(rect(x, y, x + n - 1, y), RIM if y < 176 else SKY2)

# ---- boats
def sailboat(x, y, s, hull=WHITE, stripe=EDGE):
    # x: the mast; y: the waterline; s: 1 big, 0 small
    hgt = 22 if s else 15
    mast = rect(x, y - hgt - 2, x, y - 2); put(mast, BRN_DK)
    main = poly([(x - 1, y - hgt), (x - 1, y - 3), (x - (9 if s else 6), y - 3)])
    put(main, WHITE); put(main & shift(main, 1, 0) & ~shift(main, -2, 0) & (XX >= x - 2), SKY4)
    jib = poly([(x + 1, y - hgt + 3), (x + 1, y - 3), (x + (7 if s else 5), y - 3)])
    put(jib, SKY4); put(inner_edge(jib) & (XX > x + 1), RIM)
    hl = (11 if s else 8)
    put(rect(x - hl // 2 - 1, y - 2, x + hl // 2 + 2, y - 1), hull)
    put(rect(x - hl // 2, y, x + hl // 2 + 1, y), stripe)
    put(rect(x - hl // 2 + 1, y + 1, x + hl // 2, y + 1), SKY2)    # its shadow on the water

sailboat(237, 158, 1)
sailboat(258, 152, 0)
sailboat(196, 152, 0, hull=CREAM)

def motorboat(x, y, w, hull, hull_sh, cabin=True):
    # x: left end; y: waterline
    put(poly([(x, y - 3), (x + w, y - 3), (x + w - 3, y), (x + 2, y)]), hull)
    put(rect(x + 2, y, x + w - 3, y), hull_sh)
    put(rect(x, y - 3, x + w, y - 3), WHITE)
    if cabin:
        put(rect(x + w // 3, y - 6, x + w // 3 + w // 3, y - 4), WHITE)
        put(rect(x + w // 3 + 1, y - 5, x + w // 3 + w // 3 - 1, y - 5), EDGE)
    put(rect(x + 2, y + 1, x + w - 2, y + 1), EDGE)

motorboat(158, 166, 18, WHITE, SKY4)
motorboat(246, 172, 22, LG_RED, EYE_BR)
motorboat(204, 157, 10, WHITE, SKY4, cabin=False)
motorboat(176, 150, 8, LG_RED, EYE_BR, cabin=False)

# ---- the near quay on the right: a stone quay running into the picture (its edge climbs 1 px every 4),
# the wall face down to the water, a strip of grass with flowers, trees
walk = poly([(256, 180), (320, 164), (320, 156), (262, 171)])
face = poly([(256, 181), (320, 165), (320, 168), (256, 184)])
grass = poly([(262, 171), (320, 156), (320, 148), (270, 164)])
put(shift(face, 0, 4) & ~face & water, EDGE)                                 # the wall's dark reflection
put(face, BRN)
for x in range(258, W, 6): put(line(x, 0, x, H - 1) & face, BRN_DK)        # stone joints on the face
put(walk, SAND)
put(line(256, 180, 320, 164), CREAM)                                          # the lit lip of the quay
for x in range(266, W, 10): put(line(x, 178 - (x - 256) // 4, x + 3, 170 - (x - 256) // 4) & walk, BRN)
for cx, cy, r in [(300, 138, 8), (314, 130, 10), (290, 146, 6)]: leafclump(cx, cy, r, back=True)
for cx, cy, r in [(296, 140, 6), (310, 134, 8), (318, 144, 6), (284, 150, 4), (304, 150, 5)]: leafclump(cx, cy, r)
put(grass, G_MD)
put(sheen(grass, 0, 1), G_LT)
put(grass & ~shift(grass, 0, -2), G_DK)
for fx, fy, c in [(276, 165, PK), (281, 163, LG_YE), (286, 162, WHITE), (291, 161, PK), (296, 159, LG_YE),
                  (301, 158, PK_LT), (306, 157, PK), (311, 156, WHITE), (316, 154, LG_YE), (288, 165, PK_LT),
                  (298, 162, PK), (308, 160, PK_LT)]:
    C[fy, fx] = c; C[fy, fx + 1] = c; C[fy + 1, fx] = G_DK
# the quay lamp: a slim iron post and a lantern
put(rect(289, 136, 289, 166), NAVY); put(rect(288, 166, 290, 167), NAVY)
stamp([".N.", "NYN", "NYN", "NNN"], 288, 132, {'N': NAVY, 'Y': LG_PL})

# ---- the railing along the near quay (x 130..320): iron bars between stone posts
RAIL_TOP, RAIL_BOT = 186, 206
put(rect(130, RAIL_TOP, W - 1, RAIL_TOP + 1), NAVY)
put(rect(130, RAIL_TOP, W - 1, RAIL_TOP), EDGE)
put(rect(130, RAIL_TOP + 5, W - 1, RAIL_TOP + 5), NAVY)
put(rect(130, RAIL_BOT - 2, W - 1, RAIL_BOT - 1), NAVY)
for x in range(131, W, 4):
    put(rect(x, RAIL_TOP + 2, x, RAIL_BOT - 2), NAVY)
    if (x // 4) % 2 == 0: put(rect(x, RAIL_TOP + 2, x, RAIL_TOP + 4) & False, NAVY)
# little rings between the two top rails
for x in range(133, W, 8):
    stamp([".N.", "N.N", ".N."], x - 1, RAIL_TOP + 2, {'N': NAVY})
def post(x):                                                        # an iron post with a ball on top
    put(rect(x, RAIL_TOP - 4, x + 4, RAIL_BOT), NAVY)
    put(rect(x, RAIL_TOP - 4, x, RAIL_BOT), EDGE)
    put(rect(x + 4, RAIL_TOP - 4, x + 4, RAIL_BOT), OUT)
    stamp([".NNN.", "NENNN", "NNNNO", ".NNO."], x, RAIL_TOP - 8, {'N': NAVY, 'E': RIM, 'O': OUT})
    put(rect(x - 1, RAIL_TOP - 4, x + 5, RAIL_TOP - 4), NAVY)
for px in (150, 196, 242):
    post(px)

# ---- the bench on the right, in front of the railing
put(rect(294, 190, 319, 192), BRN); put(rect(294, 190, 319, 190), EYE_AM)       # backrest slats
put(rect(294, 194, 319, 196), BRN); put(rect(294, 194, 319, 194), EYE_AM)
put(rect(292, 200, 319, 202), BRN); put(rect(292, 200, 319, 200), EYE_AM)       # seat
put(rect(292, 203, 319, 203), BRN_DK)
for lx in (296, 314):
    put(rect(lx, 188, lx + 1, 211), OUT); put(rect(lx, 188, lx, 211), NAVY)
put(rect(294, 197, 319, 197), BRN_DK)

# ---- the pavement: big flagstones in rows that grow taller towards us; each stone's top edge lit for part of
# its width, joints in brown; stone widths vary row by row (laid by hand, not a brick pattern)
put(rect(0, 206, W - 1, H - 1), SAND)
put(rect(0, 206, W - 1, 206), CREAM)                                  # the kerb's lit edge
put(rect(0, 207, W - 1, 207), BRN)
# rows in perspective: the joints run towards a vanishing point above the river (x 200), so the stones
# widen row by row; the rows' heights grow 5, 6, 7, 8, 9 px towards us
VP = 200
ROWS = [(208, 5, [24, 30, 21, 33, 27, 29]), (213, 6, [31, 23, 36, 26, 33]), (219, 7, [27, 35, 24, 31]),
        (226, 8, [33, 26, 38, 29]), (234, 9, [30, 36, 27])]
for k, (y0, hgt, widths) in enumerate(ROWS):
    put(rect(0, y0 + hgt - 1, W - 1, y0 + hgt - 1), BRN)             # the joint under the row
    s0, s1 = 1.0 + 0.22 * k, 1.0 + 0.22 * (k + 1)                     # the row's scale at its top and bottom
    u, i = -(k * 11) % 23 - 230, 0
    while VP + u * s0 < W + 40:
        w = widths[i % len(widths)]; i += 1
        u1 = u + w
        xt, xb = int(round(VP + u1 * s0)), int(round(VP + u1 * s1))
        put(line(xt, y0, xb, y0 + hgt - 2), BRN)                         # the joint on the stone's right
        lt = int(round(VP + u * s0)) + 2
        put(rect(lt, y0, lt + int(w * s0 * 0.55), y0), CREAM)             # its lit top edge, part of the way
        u = u1
put(rect(292, 208, 319, 209) & ((XX + YY) % 2 == 0), BRN)            # the bench's shadow on the stones
# ---- left: a pale stone building behind the tree, a stone wall and bushes
for cx, cy, r in [(4, 130, 7), (16, 126, 8), (26, 134, 6), (6, 146, 8), (20, 148, 7), (30, 152, 5), (10, 160, 7),
                  (24, 166, 6)]:
    leafclump(cx, cy, r)
wall = rect(0, 170, 34, 205)
put(wall, SAND)
for k, y0 in enumerate(range(170, 206, 6)):
    put(rect(0, y0, 34, y0), CREAM); put(rect(0, y0 + 5, 34, y0 + 5), BRN)
    for x in range(-(k % 2) * 6, 35, 12): put(rect(x, y0, x, y0 + 5), BRN)
put(rect(0, 169, 35, 169), CREAM); put(rect(35, 169, 35, 205), BRN)

# ---- the lamp post at the far left (x 30..37), its lantern at y 52..74
put(rect(32, 74, 34, 205), NAVY); put(rect(32, 74, 32, 205), EDGE); put(rect(34, 74, 34, 205), OUT)
put(rect(30, 196, 36, 205), NAVY); put(rect(30, 196, 30, 205), EDGE)
LAMP = [
    "....NN....",
    "...NNNN...",
    "..NNNNNN..",
    ".NNNNNNNN.",
    "NNNNNNNNNN",
    ".NPPYYPPN.",
    ".NPYYYYPN.",
    ".NYYWWYYN.",
    ".NYYWWYYN.",
    ".NYYWWYYN.",
    ".NYYYYYYN.",
    ".NPYYYYPN.",
    ".NNNNNNNN.",
    "..NNNNNN..",
    "...NNNN...",
    "....NN....",
]
stamp(LAMP, 28, 52, {'N': NAVY, 'P': LG_YE, 'Y': LG_PL, 'W': WHITE})
put(rect(29, 56, 29, 56), EDGE)

# ---- the tree: a trunk leaning out of the left edge, branches, a canopy of leaf clumps against the sky
trunk = poly([(0, 40), (8, 34), (14, 28), (18, 22), (22, 18), (24, 22), (20, 32), (16, 44), (14, 60), (14, 90),
              (15, 120), (17, 200), (0, 200)])
put(trunk, BRN)
put(trunk & shift(trunk, 3, 0) & ~shift(trunk, 6, 0), EYE_AM)        # lit left side (sun from the upper left)
put(inner_edge(trunk) & ~shift(trunk, -1, 0), BRN_DK)                 # shaded right edge
for y in range(48, 200, 7):                                           # bark: short dark strokes, staggered
    x = 6 + (y // 7) % 3 * 2
    put(rect(x, y, x, y + 3) & trunk, BRN_DK)
branches = [((16, 30), (40, 18)), ((40, 18), (62, 12)), ((22, 22), (30, 8)), ((18, 40), (50, 34)),
            ((50, 34), (70, 30)), ((40, 18), (52, 4))]
for (a, b) in branches:
    m = line(*a, *b); m = grow(m, 1, np.ones((2, 2), bool)) if True else m
    put(m, BRN); put(line(*a, *b), BRN_DK) if False else None
    put(shift(line(*a, *b), 0, 1), BRN_DK)
CANOPY_BACK = [(10, 8, 12), (32, 4, 12), (56, 6, 12), (80, 4, 11), (102, 8, 10), (118, 4, 8), (20, 28, 11),
               (46, 30, 10), (70, 26, 10), (92, 24, 9), (110, 20, 7), (8, 44, 8), (34, 44, 7), (58, 44, 7),
               (80, 40, 6)]
CANOPY_FRONT = [(6, 4, 9), (26, 14, 9), (48, 12, 10), (72, 10, 9), (94, 12, 8), (112, 10, 6), (16, 32, 8),
                (38, 34, 8), (62, 30, 8), (84, 30, 7), (100, 28, 5), (48, 48, 5), (70, 46, 5)]
for cx, cy, r in CANOPY_BACK: leafclump(cx, cy, r, back=True)
for (a, b) in branches:                                               # branches show between the clumps
    put(line(*a, *b) | shift(line(*a, *b), 0, -1), BRN); put(shift(line(*a, *b), 0, 1), BRN_DK)
for cx, cy, r in CANOPY_FRONT: leafclump(cx, cy, r)

# =============================================================================================== Pepper
# Pepper is built as forms, back to front: chest, bandana, far ear, skull, near cheek, muzzle, jaw, near ear.
# Proportions follow her in-game portrait (a wide grin, the wink in the middle of the face, the open eye high on
# the right, the nose at the right edge); the old title was the sketch for size and place. Each form gets its own
# dome of light (light_field), quantised into her 4-step fur ramp, so every form is lit on its upper left and
# turns into shadow on its lower right. Creases between forms are short shadow lines; the silhouette is OUT.
# Eyes, wink, nose, mouth and tongue are pixel grids and shapes placed by hand.
PEP = np.zeros((H, W), np.uint8)
FUR = [P_SH, P_BS, P_MD, P_HI]

CHEST = poly([(0, 190), (12, 178), (26, 166), (40, 156), (52, 148), (66, 150), (90, 160), (112, 166), (128, 150),
              (136, 138), (141, 150), (142, 170), (141, 192), (141, 212), (141, 239), (0, 239)])
EAR_FAR = poly([(116, 80), (128, 79), (139, 83), (147, 90), (151, 99), (152, 110), (150, 122), (146, 132),
                (141, 139), (136, 136), (134, 122), (133, 108), (128, 94)])
def head_shape(cx, cy, rx, ry, tilt):
    # the skull: squarer on top (a superellipse, power 2.8) and round below (power 2), tilted with her head
    a = np.radians(tilt)
    u = (XX - cx) * np.cos(a) + (YY - cy) * np.sin(a)
    v = -(XX - cx) * np.sin(a) + (YY - cy) * np.cos(a)
    pw = np.where(v < 0, 2.8, 2.0)
    return np.abs(u / rx) ** pw + np.abs(v / ry) ** pw <= 1.0
SKULL = head_shape(95.5, 114, 41.5, 34, -7) | ell(129, 142, 8, 12)   # the head, and the far cheek under the ear
CHEEK = ell(84, 142, 27, 22)
MUZZLE = poly([(100, 113), (110, 110), (121, 112), (129, 117), (134, 124), (136, 132), (133, 140), (124, 144),
               (110, 145), (100, 142), (95, 134), (95, 121)])
JAW = poly([(88, 154), (96, 161), (108, 166), (120, 165), (128, 159), (133, 150), (135, 156), (130, 166),
            (118, 173), (104, 173), (93, 167)])
EAR_NEAR = poly([(56, 89), (68, 84), (76, 86), (72, 95), (67, 106), (63, 120), (61, 134), (58, 146), (53, 154),
                 (45, 157), (37, 152), (31, 141), (28, 128), (30, 114), (36, 103), (45, 94)])
BANDANA = poly([(28, 178), (40, 171), (56, 170), (74, 174), (92, 177), (112, 177), (128, 171), (137, 166),
                (141, 173), (136, 188), (127, 204), (117, 219), (109, 228), (101, 220), (86, 205), (68, 192),
                (50, 185), (34, 184)])
KNOT = ell(33, 177, 4, 3)
FLAP1 = poly([(30, 179), (24, 184), (19, 191), (24, 191), (32, 182)])
FLAP2 = poly([(34, 180), (35, 189), (38, 195), (42, 192), (38, 180)])

SHOULDER = ell(26, 222, 28, 36) & CHEST                       # the near shoulder and leg, in front of the chest
ORDER = [('chest', CHEST, 16, [0.40, 0.86, 0.97]),
         ('shoulder', SHOULDER, 10, [0.4, 0.8, 0.9]),
         ('bandana', BANDANA | KNOT | FLAP1 | FLAP2, None, None),
         ('ear_far', EAR_FAR, 6, [0.46, 0.80, 0.93]),
         ('skull', SKULL, 12, [0.36, 0.70, 0.88]),
         ('cheek', CHEEK & ~(YY < 128), 9, [0.36, 0.68, 0.86]),
         ('muzzle', MUZZLE, 6, [0.38, 0.68, 0.86]),
         ('jaw', JAW, 4, [0.44, 0.74, 0.92]),
         ('ear_near', EAR_NEAR, 7, [0.46, 0.80, 0.92])]
PARTS = {}
for k, (nm, m, sig, cuts) in enumerate(ORDER, 1):
    PEP[m] = k; PARTS[nm] = k
def part(nm): return PEP == PARTS[nm]
pep = PEP > 0
HEADALL = SKULL | CHEEK | MUZZLE | JAW

# every form starts flat in the base black; then shadow shapes, then sheen shapes, painted by these rules
put(pep, P_BS)
sk, ch, mz, jw = part('skull'), part('cheek'), part('muzzle'), part('jaw')
en, ef, cs = part('ear_near'), part('ear_far'), part('chest')
# chest: the head's cast shadow, the far side in shadow, a lit shoulder
put(cs & shift(SKULL | CHEEK | JAW | EAR_NEAR, 2, 7), P_SH)
put(shade_rim(cs, 7, -1, 0), P_SH)
sh = part('shoulder')
put(sheen(cs, 2, 6) & (YY > 170) & (XX > 6) & (XX < 30) & ~sh, P_MD)
put(sheen(SHOULDER, 2, 7) & sh & (YY < 214), P_MD)
put(sheen(SHOULDER, 3, 5) & sh & ell(14, 198, 10, 6), P_HI)
put(shade_rim(sh, 3, -1, 0) & (YY > 200), P_SH)
put(sh & shift(part('bandana'), 0, 3) & ~part('bandana'), P_SH)
# far ear: in the head's shadow, its folded top edge lit
put(ef, P_BS); put(shade_rim(ef, 3), P_SH); put(ef & (YY > 128), P_SH)
put(sheen(ef, 1, 4) & (YY < 112), P_MD); put(sheen(ef, 1, 2) & (YY < 96) & (XX > 134), P_HI)
# skull: a broad sheen over the forehead, a highlight stroke on the crown, shadow round the far side
put(shade_rim(sk, 5), P_SH)
put(sheen(SKULL, 2, 8) & sk & (XX < 116) & (YY < 112), P_MD)
put(sheen(SKULL, 3, 5) & sk & ell(90, 86, 18, 8), P_HI)
put(ell(101, 107, 3, 5) & sk, P_SH)                                        # the stop between the eyes
# near cheek: lit on its upper left, shadow under it where it rounds into the jaw
put(shade_rim(ch, 4) & (YY > 152), P_SH)
put(sheen(CHEEK, 2, 6) & ch & (XX < 70) & (YY > 132) & (YY < 156), P_MD)
put(sheen(CHEEK, 2, 4) & ch & ell(62, 140, 4, 6), P_HI)
# muzzle: the lit bridge from the stop to the nose; the far side under the eye in shadow
put(shade_rim(mz, 3, -1, 0) & (YY < 132), P_SH)
put(sheen(MUZZLE, 1, 4) & mz & (XX < 118) & (YY < 122), P_MD)
put(sheen(MUZZLE, 1, 2) & mz & (XX < 112) & (YY < 118), P_HI)
put(polyline([(98, 126), (100, 134), (104, 140)]) & mz, P_MD)            # the lip pad's lit roll
# the smiling cheek pushed up under the wink: its own small form, lit on its upper left
APPLE = ell(84, 131, 12, 8) & sk
put(sheen(APPLE, 1, 4) & (XX < 92), P_MD)
put(sheen(APPLE, 1, 2) & ell(78, 126, 5, 3), P_HI)
put(shade_rim(APPLE, 2) & (YY > 132) & (XX < 94), P_SH)
# jaw: under the grin, mostly in shadow, its front catches light
put(jw, P_SH); put(sheen(jw, 1, 3) & (XX < 118) & (XX > 96), P_MD)
# near ear: lit flap fold at the top, darker where it hangs against the cheek, its tip in shadow
put(shade_rim(en, 4, -1, 0), P_SH)
put(en & ell(46, 158, 12, 7), P_SH)
put(sheen(en, 2, 7) & (YY < 136), P_MD)
put(sheen(en, 2, 4) & (YY < 112), P_HI)
def crease(front, behind_names, col=P_SH, sides=((1, 0), (0, 1), (1, 1))):
    fm = part(front); bm = np.zeros((H, W), bool)
    for b in behind_names: bm |= part(b)
    e = np.zeros((H, W), bool)
    for dx, dy in sides: e |= fm & shift(bm, -dx, -dy)
    put(e, col)
crease('muzzle', ['skull', 'cheek'], P_SH, ((0, 1), (-1, 1)))

# --- the bandana: fuchsia, lit top-left, the chin's shadow along the top, folds to the point, a knot with tails
bm = part('bandana')
f = light_field(bm, 6)
put(bm, PK)
put(bm & (f >= 0.82), PK_LT)
put(bm & (f < 0.40), PK_DK)
head_all = SKULL | CHEEK | JAW | EAR_NEAR | EAR_FAR
put(bm & shift(head_all, 0, 2) & ~head_all, PK_DK)
for pts in ([(44, 187), (68, 199), (90, 213), (104, 224)], [(62, 185), (78, 193)],
            [(128, 180), (120, 197), (111, 218)]):
    fold = polyline(pts) & bm
    put(fold, PK_DK); put(shift(fold, 0, -1) & bm & ~fold, PK_LT)
put(KNOT, PK); put(ell(32, 176, 2, 1) & KNOT, PK_LT)
put(inner_edge(KNOT) & ~shift(KNOT, -1, -1), PK_DK)
put((FLAP1 | FLAP2) & ~shift(FLAP1 | FLAP2, -1, 0), PK_DK)
put((FLAP1 | FLAP2) & ~shift(FLAP1 | FLAP2, 1, 0) & ~shift(FLAP1 | FLAP2, 0, 1), PK_LT)

# --- outer silhouette, and lines where the ears / head sit over other forms
put(inner_edge(pep), OUT)
for front in ('ear_near', 'skull', 'cheek', 'jaw', 'shoulder'):
    fm = part(front)
    behind = pep & ~fm & (PEP < PARTS[front]) & ~part('skull') & ~part('cheek')
    put(fm & grow(behind, 1) & inner_edge(fm), OUT)
put(part('bandana') & grow(part('chest'), 1) & inner_edge(part('bandana')), OUT)

# --- brows: a lit ridge over each eye
put(ell(116, 99, 8, 3) & ~ell(117, 101, 8, 3) & SKULL, P_HI)

# --- the eyes
EYE = [
    "...OOOOOOO...",
    ".OOObbbbbOOO.",
    ".ObWWbOOObbO.",
    "ObbWWOOOOObbO",
    "ObbbOOOOOOObO",
    "ObbaOOOOOOabO",
    "ObaaOOOOOaabO",
    ".ObaaaOOWaaO.",
    ".OObaaaaaaOO.",
    "...OOOOOOO...",
]
EYE_KEY = {'O': OUT, 'b': EYE_BR, 'a': EYE_AM, 'W': WHITE}
EYE_X, EYE_Y = 110, 102
put(ell(EYE_X + 6, EYE_Y + 11, 6, 1), P_MD)                              # the lit lower lid
stamp(EYE, EYE_X, EYE_Y, EYE_KEY)
stamp(["OO", ".O"], EYE_X + 12, EYE_Y, {'O': OUT})                         # lashes at the outer corner
WINK = [
    "......HHHHH......",
    "...HHHOOOOOHHH...",
    "..HOOOOOOOOOOOH..",
    ".HOOOMMMMMMMOOOH.",
    "OOOMM.......MMOO.",
    "OO.............O.",
]
WINK_X, WINK_Y = 74, 110
stamp(WINK, WINK_X, WINK_Y, {'O': OUT, 'H': P_HI, 'M': P_MD})
stamp(["O..", ".O.", "..."], WINK_X - 2, WINK_Y + 3, {'O': OUT})                # her lashes on the outer corner
stamp(["O.", ".O"], WINK_X - 1, WINK_Y + 1, {'O': OUT})

# --- the nose: big and shiny, lit on top
NOSE = [
    ".....OOOOOOOOOOOO.....",
    "...OOkMMMHHHHMMkkOO...",
    "..OkMHHWWHHHHHMMkkkO..",
    ".OkMHHWWWHHHHMMMkkkkO.",
    "OkkMMHHHHHMMMMkkkkkkkO",
    "OkkkMMMMMMMkkkkkkkkkkO",
    "OkMMMMkkkkkkkkMMMMkkkO",
    "OkOOOOkkkkkkkkkOOOOkkO",
    "OOOOOOOkkkkkkkOOOOOOOO",
    ".OOOOOOkkkOOkkkOOOOOO.",
    "..OOOOkkkOOOOkkkOOOO..",
    "....OOOOOO..OOOOOO....",
]
NOSE_X, NOSE_Y = 110, 119
stamp(NOSE, NOSE_X, NOSE_Y, {'O': OUT, 'k': P_SH, 'M': P_MD, 'H': P_HI, 'W': WHITE})
put(rect(121, 131, 121, 141), OUT)                                       # nose to lip

# --- the grin: the upper lip sweeps from the nose down and round to the corner under the wink; the mouth is open
UPPER = [(121, 141), (114, 145), (104, 147), (95, 146), (88, 143), (84, 139)]
UPPER_FAR = [(121, 141), (128, 144), (134, 142)]
MOUTH = poly(UPPER + [(86, 147), (92, 154), (102, 160), (114, 162), (124, 159), (131, 152), (134, 145)]
             + UPPER_FAR[::-1])
put(MOUTH, EYE_BR)                                                     # inside of the mouth: dark red-brown
put(inner_edge(MOUTH), OUT)
put(polyline(UPPER), OUT); put(polyline(UPPER_FAR), OUT)
put(shift(polyline(UPPER), 0, -2) & ~MOUTH & ~polyline(UPPER), P_HI)     # the upper lip catches the light
put(outer_ring(MOUTH) & (YY > 146) & (XX < 122) & ~shift(MOUTH, 0, -1), P_MD)  # the lower lip's lit edge
put(shift(polyline(UPPER[1:5]), 0, -1) & ~MOUTH, P_MD)                   # the lit edge of the upper lip
put(polyline([(84, 139), (82, 135)]), OUT)                               # the corner curls up into the cheek
TONGUE = (poly([(100, 155), (110, 151), (124, 152), (129, 157), (128, 164), (102, 164)]) | ell(115, 167, 13, 12)) & (YY >= 151)
put(TONGUE, TNG)
put(ell(107, 163, 2, 3) & TONGUE, TNG_LT)                                 # a wet highlight on the left lobe
put(sheen(TONGUE, 1, 2) & (YY > 166) & (XX < 112), TNG_LT)
put(line(115, 158, 115, 172) & TONGUE, PK_DK)
put(TONGUE & shift(MOUTH, 0, 2) & (YY < 157), PK_DK)                      # in the shadow of the upper lip
put(inner_edge(TONGUE) & ~shift(TONGUE, -1, -1), PK_DK)
put(outer_ring(TONGUE) & ~MOUTH, OUT)
tongue_all = TONGUE | outer_ring(TONGUE)

# sheen strokes: clean arcs that follow the forms (forehead, cheek over the grin, ear fold, shoulder, chest)
for pts, col in [([(84, 88), (94, 84), (106, 83)], P_HI), ([(80, 92), (90, 88)], P_MD),
                 ([(64, 128), (68, 124), (74, 122)], P_MD),
                 ([(40, 104), (48, 97), (58, 92)], P_HI), ([(36, 112), (42, 104)], P_MD),
                 ([(10, 188), (22, 178), (34, 172)], P_MD), ([(14, 196), (24, 188)], P_MD),
                 ([(130, 200), (136, 186)], P_MD), ([(116, 230), (126, 214)], P_MD)]:
    put(polyline(pts) & pep & ~part('bandana') & (C != OUT), col)

holes = ndi.binary_fill_holes(pep | MOUTH | TONGUE) & ~(pep | MOUTH | TONGUE)   # no sky through her
put(holes, P_SH); pep = pep | holes

deorphan(pep & ~rect(EYE_X - 1, EYE_Y - 1, EYE_X + 14, EYE_Y + 12) & ~rect(NOSE_X, NOSE_Y, NOSE_X + 22, NOSE_Y + 12)
         & ~tongue_all & ~rect(WINK_X, WINK_Y, WINK_X + 17, WINK_Y + 6))

# ================================================================================================= the logo
# Hand-lettered FETCH!: each letter is built from stroke boxes on a 44 px high grid (stems 10 px, arms 9-10 px),
# outer corners rounded twice, a round C and a tapered "!". The word climbs to the right like the old logo: each
# column moves up 1 px every 13 columns (steps of even length), and the letters bounce a little. The fill is a
# 2-tone gradient (yellow over orange) joined by one clean checker row; the top and left inner edges are lit, the
# bottom and right inner edges darker; a 2 px navy outline and a 3 px drop shadow; the paw print beside the "!".
LH = 44
LET_X, LET_TOP, RISE = 130, 24, 13
def letter_masks():
    lw = 162
    m = np.zeros((LH, lw), bool)
    def box(x0, y0, x1, y1): m[y0:y1 + 1, x0:x1 + 1] = True
    # F
    box(0, 0, 9, LH - 1); box(0, 0, 25, 9); box(0, 17, 21, 25)
    # E
    x = 28; box(x, 0, x + 9, LH - 1); box(x, 0, x + 25, 9); box(x, 17, x + 22, 25); box(x, LH - 10, x + 25, LH - 1)
    # T
    x = 56; box(x, 0, x + 27, 9); box(x + 9, 0, x + 18, LH - 1)
    # C: an elliptic ring, opened on the right
    x = 86; cx, cy = x + 14, (LH - 1) / 2
    yy, xx = np.mgrid[0:LH, 0:lw]
    ring = (((xx - cx) / 14.6) ** 2 + ((yy - cy) / 22.2) ** 2 <= 1) & ~((((xx - cx) / 5.2) ** 2 + ((yy - cy) / 12.6) ** 2) <= 1)
    ring &= ~((xx > cx + 2) & (np.abs(yy - cy) < 7))
    m |= ring
    # H
    x = 118; box(x, 0, x + 9, LH - 1); box(x + 18, 0, x + 27, LH - 1); box(x, 17, x + 27, 25)
    # ! : a bar narrowing towards the bottom, and its dot
    x = 150
    for y in range(0, 31):
        inset = y * 2 // 31
        m[y, x + inset:x + 11 - inset] = True
    box(x, 34, x + 10, LH - 1)
    # round every outer corner (twice: a 2-step curve)
    for _ in range(2):
        nb = ndi.convolve(m.astype(int), np.ones((3, 3), int), mode='constant')
        m &= ~(m & (nb <= 4))
    return m
LM = letter_masks()
BOUNCE = [(0, 26, 1), (28, 54, -1), (56, 84, 1), (86, 116, 0), (118, 146, -1), (150, 162, 0)]
L_IN = np.zeros((H, W), bool); GY = np.full((H, W), -1, np.int16)
for x in range(LM.shape[1]):
    b = [d for x0, x1, d in BOUNCE if x0 <= x <= x1]
    top = LET_TOP - x // RISE + (b[0] if b else 0)
    for y in range(LH):
        if LM[y, x]: L_IN[top + y, LET_X + x] = True; GY[top + y, LET_X + x] = y

# the paw print: four toe beans over a three-lobed pad
PAW_X, PAW_Y = 284, 52
PAW = (ell(PAW_X + 3, PAW_Y + 8, 2, 3) | ell(PAW_X + 8, PAW_Y + 3, 2, 3) | ell(PAW_X + 14, PAW_Y + 3, 2, 3)
       | ell(PAW_X + 19, PAW_Y + 8, 2, 3) | ell(PAW_X + 11, PAW_Y + 14, 6, 4) | ell(PAW_X + 7, PAW_Y + 16, 3, 2)
       | ell(PAW_X + 15, PAW_Y + 16, 3, 2))

ALL = L_IN | PAW
outline = grow(ALL, 2, np.ones((3, 3), bool)) & ~ALL
outline_paw = grow(PAW, 1, np.ones((3, 3), bool)) & ~ALL
outline = (grow(L_IN, 2, np.ones((3, 3), bool)) | outline_paw) & ~ALL
shadow = np.zeros((H, W), bool)
for d in (1, 2, 3): shadow |= shift(ALL | outline, d, d)
put(shadow & ~(ALL | outline), OUT)
put(outline, NAVY)
# the gradient by each letter's own row, so it climbs with the letters
put(L_IN, LG_YE)
checker(L_IN & (GY == 22), LG_OR)
put(L_IN & (GY >= 23), LG_OR)
# the shine stripe across the top of every letter
put(L_IN & (GY >= 3) & (GY <= 4), LG_PL)
# lit inner edges (top, left), darker inner edges (bottom, right)
ie = inner_edge(L_IN)
put(ie & ~shift(L_IN, 1, 0), LG_PL)
put(ie & ~shift(L_IN, 0, 1), LG_PL)
put(ie & ~shift(L_IN, 0, 1) & (GY < 2), WHITE)
put(L_IN & ~shift(L_IN, -1, 0), LG_RED)
put(L_IN & ~shift(L_IN, 0, -1), LG_RED)
put(L_IN & ~shift(L_IN, 0, -1) & shift(L_IN, 0, 2) & ~shift(L_IN, 0, -2) & (GY < 22), LG_OR)
# the paw: yellow, lit up-left, orange down-right
put(PAW, LG_YE)
put(PAW & ~shift(PAW, 1, 1), LG_PL)
put(PAW & ~shift(PAW, -1, -1), LG_OR)
LOGO_PIX = ALL
LOGO_X, LOGO_Y = 124, 4

# ---- the banner: THE CITY DOG ADVENTURER in the game's font, in a navy box with a light rim
BAN_TXT = 'THE CITY DOG ADVENTURER'
bw = text_width(BAN_TXT) + 12
BAN_X, BAN_Y, BAN_H = 214 - bw // 2, 82, 15
def box(x, y, w, h, edge, rim, body):
    put(rect(x + 1, y, x + w - 2, y + h - 1) | rect(x, y + 1, x + w - 1, y + h - 2), edge)
    put(rect(x + 2, y + 1, x + w - 3, y + h - 2) | rect(x + 1, y + 2, x + w - 2, y + h - 3), rim)
    put(rect(x + 2, y + 2, x + w - 3, y + h - 3), body)
put(shift(rect(BAN_X + 1, BAN_Y, BAN_X + bw - 2, BAN_Y + BAN_H - 1) | rect(BAN_X, BAN_Y + 1, BAN_X + bw - 1, BAN_Y + BAN_H - 2), 2, 2), OUT)
box(BAN_X, BAN_Y, bw, BAN_H, OUT, RIM, NAVY)
draw_text(BAN_TXT, BAN_X + 6, BAN_Y + 4, WHITE, shade=OUT)

# ---- PRESS ANY KEY TO START: the HUD's box (edge, rim, blue), the HUD's text
PR_TXT = 'PRESS ANY KEY TO START'
PR_W = text_width(PR_TXT) + 10
PR_H = 17
PR_X, PR_Y = 214 - PR_W // 2, 189
box(PR_X, PR_Y, PR_W, PR_H, EDGE, RIM, BLUE)
put(shift(rect(PR_X + 1, PR_Y + PR_H, PR_X + PR_W - 1, PR_Y + PR_H), 0, 0), OUT)
press_off = C[PR_Y:PR_Y + PR_H, PR_X:PR_X + PR_W].copy()
draw_text(PR_TXT, PR_X + PR_W // 2 - text_width(PR_TXT) // 2, PR_Y + 5, WHITE, shade=OUT)

# ============================================================================================ the layers
def rgb(a, alpha=None):
    p = np.array(PAL + [(0, 0, 0)] * (256 - len(PAL)), np.uint8)
    im = p[a]
    if alpha is None: return Image.fromarray(im, 'RGB')
    return Image.fromarray(np.dstack([im, (alpha * 255).astype(np.uint8)]), 'RGBA')

def write_all(preview=None):
    os.makedirs(ART, exist_ok=True)
    rgb(C).save(os.path.join(ART, 'base.png'))
    rgb(press_off).save(os.path.join(ART, 'press_off.png'))
    # eye closed: the eye and its lashes painted over with fur, then a lid arc
    ex0, ey0, ew, eh = EYE_X - 1, EYE_Y - 1, 15, 11
    patch = C[ey0:ey0 + eh, ex0:ex0 + ew].copy()
    eyem = np.zeros((H, W), bool); stamp(EYE, EYE_X, EYE_Y, EYE_KEY, canvas=np.zeros((H, W), np.uint8), mask_out=eyem)
    stamp(["OO", ".O"], EYE_X + 12, EYE_Y, {'O': OUT}, canvas=np.zeros((H, W), np.uint8), mask_out=eyem)
    em = eyem[ey0:ey0 + eh, ex0:ex0 + ew]
    patch[em] = P_BS
    # the closed eye is drawn like her wink: a happy arc, lit above, with a lash at the outer corner
    BLINK = [
        "....HHHHH....",
        "..HHOOOOOHH..",
        ".HOOOOOOOOOH.",
        "HOOMMMMMMMOOH",
        "OOM.......MOO",
        "O...........O",
    ]
    alpha = em.copy()
    for j, r in enumerate(BLINK):
        for i, ch in enumerate(r):
            if ch != '.':
                patch[2 + j, 1 + i] = {'O': OUT, 'H': P_HI, 'M': P_MD}[ch]; alpha[2 + j, 1 + i] = True
    patch[6, 13] = OUT; alpha[6, 13] = True                                  # the lash
    rgb(patch, alpha.astype(float)).save(os.path.join(ART, 'eye_closed.png'))
    # the bird: a gull, three frames
    BIRD = [
        ["O...........O", ".OW.......WO.", "..OWW...WWO..", "....OWWWO....", ".....OOO.....", "............."],
        [".............", ".............", "OOWW.....WWOO", "...OWWWWWO...", ".....OOO.....", "............."],
        [".............", ".............", ".....OWO.....", "...OWWWWWO...", "..OW.....WO..", ".O.........O."],
    ]
    bw_, bh_ = 13, 6
    sheet = np.zeros((bh_, bw_ * 3), np.uint8); al = np.zeros((bh_, bw_ * 3))
    for f, fr in enumerate(BIRD):
        for j, r in enumerate(fr):
            for i, ch in enumerate(r):
                if ch != '.': sheet[j, f * bw_ + i] = {'O': NAVY, 'W': WHITE}[ch]; al[j, f * bw_ + i] = 1
    rgb(sheet, al).save(os.path.join(ART, 'bird.png'))
    # the logo, one step brighter (the shine)
    ys, xs = np.nonzero(grow(LOGO_PIX, 4, np.ones((3, 3), bool)))   # the logo's box: letters, outline, shadow
    lx0, ly0, lx1, ly1 = xs.min(), ys.min(), min(W, xs.max() + 1), ys.max() + 1
    up = {LG_RED: LG_OR, LG_OR: LG_YE, LG_YE: LG_PL, LG_PL: WHITE, WHITE: WHITE}
    reg = C[ly0:ly1, lx0:lx1].copy(); m = LOGO_PIX[ly0:ly1, lx0:lx1]
    hi = reg.copy()
    for a, b in up.items(): hi[(reg == a) & m] = b
    rgb(hi, m.astype(float)).save(os.path.join(ART, 'logo_hi.png'))
    # positions
    lua = ['-- generated by tools/title_redraw.py (the hand-pixeled title): positions of the animated parts', 'return {']
    lua.append('  sparkles = {')
    for x, y, n, c in SPARKLES: lua.append('    { %d, %d, %d, %d, %d, %d },' % (x, y, n, *PAL[c]))
    lua.append('  },')
    lua.append('  bird = { x = %d, y = %d, w = %d, h = %d },' % (BIRD_X, BIRD_Y, bw_, bh_))
    lua.append('  eye = { x = %d, y = %d },' % (ex0, ey0))
    lua.append('  press = { x = %d, y = %d },' % (PR_X, PR_Y))
    lua.append('  logo = { x = %d, y = %d, w = %d, h = %d },' % (lx0, ly0, lx1 - lx0, ly1 - ly0))
    lua.append('  lamps = { { 33, 61, 7 }, { 289, 134, 3 } },')
    lua.append('}')
    open(os.path.join(ROOT, 'riverwalk', 'title_data.lua'), 'w').write('\n'.join(lua) + '\n')
    # the palette swatch, ramps in rows of 8
    sw = np.zeros((4 * 12, 8 * 12), np.uint8)
    for i in range(len(PAL)): sw[(i // 8) * 12:(i // 8) * 12 + 12, (i % 8) * 12:(i % 8) * 12 + 12] = i
    rgb(sw).resize((sw.shape[1] * 3, sw.shape[0] * 3), Image.NEAREST).save(os.path.join(ROOT, 'source_title', 'palette_redraw.png'))
    if preview:
        os.makedirs(preview, exist_ok=True)
        rgb(C).save(os.path.join(preview, 'redraw_1x.png'))
        rgb(C).resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(preview, 'redraw_3x.png'))
        rgb(C).crop((0, 70, 160, 240)).resize((160 * 6, 170 * 6), Image.NEAREST).save(os.path.join(preview, 'redraw_pepper_6x.png'))

# sparkles on the water: streaks in white and the palest blue, placed by hand (title.lua twinkles them)
SPARKLES = [(150, 149, 3, WHITE), (172, 153, 2, SKY4), (186, 148, 4, WHITE), (208, 151, 2, WHITE),
            (216, 155, 3, SKY4), (233, 161, 4, WHITE), (250, 158, 2, SKY4), (268, 155, 3, WHITE),
            (282, 151, 2, WHITE), (300, 154, 3, SKY4), (160, 162, 3, WHITE), (194, 164, 2, SKY4),
            (212, 166, 4, WHITE), (230, 170, 3, SKY4), (264, 165, 2, WHITE), (296, 163, 4, WHITE),
            (176, 176, 3, SKY4), (204, 178, 4, WHITE), (240, 177, 2, SKY4), (290, 176, 3, WHITE),
            (150, 172, 2, WHITE), (220, 182, 3, SKY4), (258, 180, 2, WHITE), (166, 156, 3, SKY4),
            (182, 159, 2, WHITE), (200, 163, 3, WHITE), (244, 163, 3, SKY4), (226, 158, 2, WHITE),
            (186, 171, 4, WHITE), (248, 168, 3, WHITE), (164, 180, 3, SKY4), (236, 183, 3, WHITE),
            (196, 185, 2, SKY4), (278, 184, 3, WHITE), (144, 160, 2, SKY4)]
BIRD_X, BIRD_Y = 96, 60
# keep only the streaks that lie wholly on open water (not on a boat, the quay or a tree)
SPARKLES = [sp for sp in SPARKLES if all(C[sp[1], x] in (RIM, SKY2, BLUE) and water[sp[1], x] for x in range(sp[0], sp[0] + sp[2]))]

if __name__ == '__main__':
    write_all(sys.argv[1] if len(sys.argv) > 1 else None)
    used = np.unique(C)
    print('colours used', len(used), 'of', len(PAL))
