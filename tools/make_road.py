# Draws the road under the promenade (riverwalk/art/scene/road.png, 640 x 41, tiles left to right) and its
# decals: a manhole cover (manhole.png) and a kerb drain (drain.png). Pixel art made here in code; nothing from
# outside. The road replaces the flat rows 27-67 of pavement.png in the game (the paving rows of the user's
# pavement art are untouched; the granite kerb face over the road is drawn by scene.lua); see Sc.paintGround.
# (art/rw-ground-06nov, owner 6 Nov: "these connections of asphalt really look weird") Clean asphalt by rule:
#   * flat fills: one asphalt colour (a neutral grey: the look's grade adds its blue), a darker gutter strip along the kerb with a shadow row under it
#   * aggregate: a few 2 px flecks, one shade lighter, on a fixed grid (every 80 px on 4 rows, rows offset)
#   * the centre line: dashes all 64 px long on an even 160 px pitch, rows 20-21, one flat white, no worn pixels
#   * no grain noise, no cracks, no repair patches; everything wraps at x = 640, so the strip tiles without a seam
#   * rows 0-3 (the gutter, the drain's band 200-202) and 20-21 (the line) sit inside look.lua's road bands
import os, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
W, H = 640, 41
BASE = np.array([86, 91, 98])                     # asphalt
GUT = np.array([76, 80, 88])                      # the gutter strip by the kerb (rows 1-3)
SHAD = np.array([60, 64, 70])                      # the kerb's shadow (row 0)
FLECK = np.array([100, 104, 110])                  # aggregate, one shade lighter
LINE = np.array([206, 208, 214])                   # the centre line
img = np.tile(BASE, (H, W, 1)).astype(int)
img[0, :] = SHAD
img[1:4, :] = GUT
for row, off in ((8, 0), (14, 40), (27, 20), (36, 60)):   # flecks on a grid (clear of the line and the gutter)
    for x in range(off, W, 80):
        img[row, x] = FLECK; img[row, (x + 1) % W] = FLECK
for x in range(W):                                 # dashes 64 px, pitch 160
    if x % 160 < 64:
        img[20, x] = LINE; img[21, x] = LINE
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
