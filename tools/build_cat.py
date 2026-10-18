"""Builds art/cat.png, the Downtown cat (modelled on the user's Abyssinian), from the SpriteCook clips in
source_sheets/: cat_idle.png (8 x 36 px), cat_leap.png and cat_run.png (8 x 48 px). Source: the hand-pixeled
sitting cat source_sheets/cat_sit_source.png (SpriteCook asset 3a0c5b07), animated with pixel-engine-v1.5.
Cleanup like Pepper's clips: grey matte left by the animator becomes transparent, every pixel snaps to the cat's
11-colour palette, detached specks go, and a 1 px dark outline closes every open edge.
Output: one 48 x 48 cell per frame, rows idle / leap / run, the cat's feet on the cell's anchor (ax, ay)."""
import os, numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAL = np.array([
    (36, 14, 8),     # 0 outline, pupil
    (73, 36, 22),    # 1 dark ticking
    (147, 65, 26),   # 2 shadow
    (204, 110, 42),  # 3 coat
    (233, 149, 72),  # 4 light coat
    (246, 195, 130), # 5 cream
    (249, 228, 196), # 6 pale chin
    (224, 148, 127), # 7 ear pink
    (178, 98, 78),   # 8 nose
    (139, 178, 82),  # 9 eye green
], int)
CELL = 48
def frames(name, n=8):
    im = np.array(Image.open(os.path.join(ROOT, "source_sheets", name)).convert("RGBA")).astype(int)
    w = im.shape[1] // n
    return [im[:, i * w:(i + 1) * w] for i in range(n)]
def clean(f):
    rgb, al = f[..., :3], f[..., 3] >= 128
    sat = rgb.max(-1) - rgb.min(-1)
    matte = (sat < 18) & (rgb.max(-1) > 60)                 # the animator's grey matte (#808080) at the edges
    al &= ~matte
    d = ((rgb[..., None, :] - PAL[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1); idx[~al] = -1
    lab, k = nd.label(idx >= 0, structure=np.ones((3, 3)))
    if k > 1:
        sizes = nd.sum(idx >= 0, lab, range(1, k + 1)); big = int(np.argmax(sizes)) + 1
        for i, s in enumerate(sizes, 1):
            if i != big and s < 6: idx[lab == i] = -1
    op = idx >= 0                                            # outline: edge pixels that are not already dark
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    idx[edge & (idx > 1)] = 0
    return idx
def bbox(idx):
    ys, xs = np.nonzero(idx >= 0); return xs.min(), ys.min(), xs.max(), ys.max()
rows = [("idle", frames("cat_idle.png")), ("leap", frames("cat_leap.png")), ("run", frames("cat_run.png"))]
sheet = np.zeros((CELL * 3, CELL * 8, 4), np.uint8)
AX, AY = 24, 44                                              # the cat's feet in every cell
anchors = []
for r, (name, fs) in enumerate(rows):
    cl = [clean(f) for f in fs]
    x0, y0, x1, y1 = bbox(cl[0])                             # idle: the sitting cat's centre and feet stay put
    for i, idx in enumerate(cl):
        if name != "idle":                                   # leap, run: every frame centred on its own body,
            x0, y0, x1, y1 = bbox(idx)                       # lowest paw on the line (the game moves the cat)
        ox, oy = AX - (x0 + x1) // 2, AY - y1
        ys, xs = np.nonzero(idx >= 0)
        for y, x in zip(ys, xs):
            X, Y = x + ox, y + oy
            if 0 <= X < CELL and 0 <= Y < CELL:
                sheet[r * CELL + Y, i * CELL + X, :3] = PAL[idx[y, x]]; sheet[r * CELL + Y, i * CELL + X, 3] = 255
Image.fromarray(sheet).save(os.path.join(ROOT, "riverwalk", "art", "cat.png"))
print("art/cat.png", sheet.shape[1], "x", sheet.shape[0], "anchor", AX, AY)
