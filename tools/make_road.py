# Draws the road under the promenade (riverwalk/art/scene/road.png, 640 x 41, tiles left to right) and its
# decals: a manhole cover (manhole.png) and a kerb drain (drain.png). Pixel art made here in code; nothing from
# outside. The road replaces the flat rows 27-67 of pavement.png in the game (the paving and kerb rows 0-26 of
# the user's pavement art are untouched); see Sc.paintGround.
#   * colours: the pavement art's road colour (92, 101, 124) plus two darker and two lighter shades of it
#   * grain: small clusters of light and dark stones, denser along the two worn tyre tracks of each lane
#   * a darker gutter row along the kerb, a dashed centre line (worn, some pixels missing), a few hairline
#     cracks and two darker repair patches
#   * everything wraps at x = 640, so the strip tiles without a seam
import os, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
W, H = 640, 41
BASE = np.array([92, 101, 124]); D1 = np.array([82, 90, 112]); D2 = np.array([70, 77, 97])
L1 = np.array([103, 111, 133]); L2 = np.array([121, 128, 148]); LINE = np.array([206, 208, 214]); LINE2 = np.array([170, 175, 186])
rng = np.random.default_rng(3)
img = np.tile(BASE, (H, W, 1)).astype(int)
def put(y, x, c):
    if 0 <= y < H: img[y, x % W] = c
# gutter along the kerb, then a soft shadow row
img[0, :] = D2; img[1, :] = D1
# worn tyre tracks: two per lane (lanes are rows 2-19 and 22-40), slightly darker bands with denser grain
tracks = [5, 14, 26, 35]
for t in tracks:
    for x in range(W):
        if rng.random() < 0.55: put(t, x, D1)
        if rng.random() < 0.25: put(t + 1, x, D1)
# grain: clusters of 1-3 px, light and dark
for _ in range(2400):
    y, x = rng.integers(2, H), rng.integers(0, W)
    near = min(abs(y - t) for t in tracks) <= 1
    c = [L1, L2, D1, D2][rng.choice(4, p=[0.45, 0.12, 0.3, 0.13] if not near else [0.25, 0.05, 0.45, 0.25])]
    put(y, x, c)
    if rng.random() < 0.35: put(y, x + 1, c)
    if rng.random() < 0.15: put(y + 1, x, c)
# repair patches: darker rectangles with a 1 px seam
for px, py, pw, ph in [(118, 24, 46, 11), (430, 4, 34, 9)]:
    for y in range(py, py + ph):
        for x in range(px, px + pw):
            edge = y in (py, py + ph - 1) or x in (px, px + pw - 1)
            if edge: put(y, x, D2)
            elif rng.random() < 0.85: put(y, x, D1)
            else: put(y, x, BASE)
# hairline cracks: random walks of dark pixels
for sx, sy, n in [(60, 30, 26), (270, 8, 18), (360, 33, 22), (560, 12, 30)]:
    x, y = sx, sy
    for _ in range(n):
        put(y, x, D2)
        x += 1
        r = rng.random()
        if r < 0.3: y += 1
        elif r < 0.6: y -= 1
        y = max(3, min(H - 2, y))
# dashed centre line on rows 20-21: dashes 20 px, gaps 28 px (worn: a few pixels missing or greyer)
for x in range(W):
    if (x % 48) < 20:
        for y in (20, 21):
            r = rng.random()
            img[y, x] = LINE if r < 0.82 else (LINE2 if r < 0.95 else img[y, x])
Image.fromarray(img.astype(np.uint8)).save(os.path.join(OUT, 'road.png'))

# manhole cover seen from a low angle: an ellipse 19 x 7, dark rim, iron grey with a cross-hatch
mw, mh = 19, 7
m = np.zeros((mh, mw, 4), np.uint8)
RIM = (46, 50, 60, 255); IRON = (98, 102, 112, 255); IRON2 = (78, 82, 92, 255); HI = (132, 136, 146, 255)
cx, cy, rx, ry = (mw - 1) / 2, (mh - 1) / 2, mw / 2, mh / 2
for y in range(mh):
    for x in range(mw):
        d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        if d <= 1.0:
            if d > 0.62: m[y, x] = RIM
            else: m[y, x] = IRON2 if (x + y) % 3 == 0 or (x - y) % 3 == 0 else IRON
for x in range(6, 13): m[1, x] = HI if m[1, x][3] and tuple(m[1, x]) != RIM else m[1, x]
Image.fromarray(m).save(os.path.join(OUT, 'manhole.png'))

# kerb drain: a grate 12 x 3 right against the kerb
g = np.zeros((3, 12, 4), np.uint8)
for x in range(12):
    g[0, x] = RIM
    g[1, x] = (36, 38, 46, 255) if x % 2 else (90, 94, 104, 255)
    g[2, x] = RIM
Image.fromarray(g).save(os.path.join(OUT, 'drain.png'))
print('road', W, H, 'manhole', mw, mh, 'drain 12 3')
