"""Builds the park keepers for City Park from SpriteCook output in source_sheets/:
- keeper_walk.png: the keeper pushing his wheelbarrow of leaves (8 frames, 82 x 82; SpriteCook still 14e58436,
  styled on the River Walk cyclist with the old park_cart as reference, walk cycle by pixel-engine-v1.5)
  -> art/scene/park_keeper_cart.png. The leaf cart hazard now has someone pushing it.
- keeper_winch.png (if present): the second keeper turning the duck boat's winch -> art/scene/park_keeper_winch.png
Cleanup: the animator's grey matte (#7e7e7e) is removed where it touches the outside, detached specks go. The
art keeps its own outline and colours (it is already 16 colours)."""
import os, numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def clean(sheet, n):
    a = np.array(sheet.convert("RGBA")).astype(int)
    fw = a.shape[1] // n
    out = []
    for f in range(n):
        fr = a[:, f * fw:(f + 1) * fw].copy()
        op = fr[..., 3] >= 128
        grey = op & (np.abs(fr[..., :3] - 126).max(-1) <= 6)
        outside = nd.binary_dilation(~op, iterations=1)
        for _ in range(3):                                       # peel matte inwards from the outside
            rem = grey & outside
            if not rem.any(): break
            op &= ~rem; grey &= ~rem; outside = nd.binary_dilation(~op, iterations=1)
        lab, k = nd.label(op, structure=np.ones((3, 3)))
        if k > 1:
            sizes = nd.sum(op, lab, range(1, k + 1)); big = int(np.argmax(sizes)) + 1
            for i, s in enumerate(sizes, 1):
                if i != big and s < 6: op[lab == i] = False
        fr[..., 3] = np.where(op, 255, 0)
        out.append(fr.astype(np.uint8))
    return Image.fromarray(np.concatenate(out, 1))
for src, dst, n in (("keeper_walk.png", "park_keeper_cart.png", 8), ("keeper_winch.png", "park_keeper_winch.png", 8)):
    p = os.path.join(ROOT, "source_sheets", src)
    if os.path.exists(p):
        clean(Image.open(p), n).save(os.path.join(ROOT, "riverwalk", "art", "scene", dst)); print("art/scene/" + dst)
