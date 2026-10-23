"""Shared helpers for the r8/art batch 1 build scripts (tools/build_r8_*.py) and tools/art_qa.py.

Rules from docs/asset_plan_22oct.md section 0 and 3: generate big, reduce with a box filter to the exact target size,
snap to a small palette, binary alpha, no specks, 1 px dark outline on obstacles, no outline on decoration."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "source_scenery")
SS = os.path.join(ROOT, "source_sheets")
ART = os.path.join(ROOT, "riverwalk", "art")
R8 = os.path.join(ART, "r8")                              # every new file of batch 1 lands here (nothing is overwritten)


def load(p):
    return np.array(Image.open(p).convert("RGBA"))


def save(a, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    Image.fromarray(a.astype(np.uint8), "RGBA").save(p)
    print(os.path.relpath(p, ROOT), a.shape[1], "x", a.shape[0], ncolors(a), "colours")


def ncolors(a):
    op = a[..., 3] > 0
    return len(np.unique(a[op][:, :3], axis=0)) if op.any() else 0


def luma(rgb):
    rgb = np.asarray(rgb, float)
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def key_white(a, tol=22):
    """the generator paints on white: make the white that touches the border transparent (flood fill), so whites
    inside the picture (windows, shirts, the gaps between spokes inside a tyre) stay"""
    a = a.copy()
    rgb = a[..., :3].astype(int)
    white = (rgb.min(-1) >= 255 - tol) & ((rgb.max(-1) - rgb.min(-1)) < 14)
    lab, _ = nd.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    a[bg, 3] = 0
    return a


def bbox(a):
    ys, xs = np.where(a[..., 3] > 0)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def crop(a, box=None):
    x0, y0, x1, y1 = box or bbox(a)
    return a[y0:y1, x0:x1]


def split_columns(a, n):
    """cut a sheet into its n widest runs of non-empty columns (left to right)"""
    col = (a[..., 3] > 0).any(0)
    runs, x = [], 0
    while x < len(col):
        if col[x]:
            s = x
            while x < len(col) and col[x]: x += 1
            runs.append((s, x))
        else:
            x += 1
    runs = sorted(sorted(runs, key=lambda r: r[1] - r[0])[-n:])
    return [crop(a[:, s:e]) for s, e in runs]


def components(a, min_px=200):
    """connected opaque pieces (8-connected), biggest first, as (box, mask)"""
    lab, k = nd.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(nd.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() >= min_px:
            out.append(((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop), m.sum()))
    return sorted(out, key=lambda t: -t[1])


def box_resize(a, W, H):
    """box filter with premultiplied alpha"""
    f = a.astype(float)
    pre = np.dstack([f[..., :3] * (f[..., 3:4] / 255), f[..., 3]])
    sm = np.array(Image.fromarray(pre.clip(0, 255).round().astype(np.uint8), "RGBA").resize((W, H), Image.BOX)).astype(float)
    A = sm[..., 3:4] / 255
    rgb = np.where(A > 0, sm[..., :3] / np.maximum(A, 1e-6), 0)
    return np.dstack([rgb, sm[..., 3]]).clip(0, 255)


def fit_height(a, H):
    """box-filter to an exact height, width by the aspect ratio"""
    h, w = a.shape[:2]
    return box_resize(a, max(1, round(w * H / h)), H)


def palette_snap(a, n, cut=0.5, keep=None):
    """binary alpha at `cut`, then the opaque colours reduced to n by median cut (PIL), no dither"""
    a = a.copy()
    op = a[..., 3] >= 255 * cut
    pix = a[op][:, :3].round().astype(np.uint8)
    img = Image.fromarray(pix.reshape(-1, 1, 3), "RGB")
    q = img.quantize(n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:3 * n]).reshape(-1, 3)
    idx = np.array(q).reshape(-1)
    out = np.zeros(a.shape, np.uint8)
    out[op, :3] = pal[idx]
    out[op, 3] = 255
    return out


def despeckle(a, passes=2, min_island=3):
    """no isolated pixels: an opaque pixel with no same-colour 8-neighbour takes the most common neighbour colour;
    opaque islands smaller than min_island pixels go"""
    a = a.copy()
    op = a[..., 3] > 0
    lab, k = nd.label(op, structure=np.ones((3, 3)))
    if k:
        sizes = nd.sum(op, lab, range(1, k + 1))
        for i, s in enumerate(sizes, 1):
            if s < min_island: a[lab == i, 3] = 0
    H, W = a.shape[:2]
    for _ in range(passes):
        key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
        key[a[..., 3] == 0] = -1
        pad = np.pad(key, 1, constant_values=-2)
        same = np.zeros((H, W), bool)
        neigh = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0: continue
                nb = pad[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
                same |= nb == key
                neigh.append(nb)
        lone = (key >= 0) & ~same
        ys, xs = np.where(lone)
        nbs = np.stack(neigh, -1)
        for y, x in zip(ys, xs):
            v = nbs[y, x]
            v = v[v >= 0]
            if len(v) < 3: continue                                   # an edge tip: leave it (the outline pass handles it)
            vals, cnt = np.unique(v, return_counts=True)
            c = vals[cnt.argmax()]
            a[y, x, :3] = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    return a


def silhouette(a):
    op = a[..., 3] > 0
    pad = np.pad(op, 1)
    return op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])


def outline(a, ink=None):
    """obstacles: every silhouette pixel (4-neighbour of transparency) becomes the outline ink (the darkest colour)"""
    a = a.copy()
    op = a[..., 3] > 0
    if ink is None:
        cols = a[op][:, :3]
        ink = cols[luma(cols).argmin()]
    a[silhouette(a), :3] = ink
    return a


def no_outline(a, dark=72, peel=2):
    """decoration: the generator's dark stroke goes. Up to `peel` layers of dark silhouette pixels are peeled off
    (made transparent), then any dark silhouette pixel left takes the darkest light-enough colour among its inner
    neighbours, so the shape keeps its edge by value steps, not by a stroke"""
    a = a.copy()
    for _ in range(peel):
        e = silhouette(a) & (luma(a[..., :3]) < dark)
        a[e, 3] = 0
    edge = silhouette(a)
    inner = (a[..., 3] > 0) & ~edge
    H, W = a.shape[:2]
    for _ in range(2):
        ys, xs = np.where(edge & (luma(a[..., :3]) < dark))
        for y, x in zip(ys, xs):
            best = None
            for dy in (-3, -2, -1, 0, 1, 2, 3):
                for dx in (-3, -2, -1, 0, 1, 2, 3):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and inner[yy, xx] and luma(a[yy, xx, :3]) >= dark:
                        l = luma(a[yy, xx, :3])
                        if best is None or l < best[0]: best = (l, a[yy, xx, :3].copy())
            if best is not None: a[y, x, :3] = best[1]
    return crop(a) if a[..., 3].any() else a


def drop_isolated(a):
    """opaque pixels with no opaque 8-neighbour go"""
    a = a.copy()
    op = a[..., 3] > 0
    n = nd.convolve(op.astype(int), np.ones((3, 3), int), mode="constant") - op
    a[op & (n == 0), 3] = 0
    return a


def mirror(a):
    return a[:, ::-1].copy()


def pad_to(a, W, H, anchor="bottom"):
    """place on a W x H transparent canvas, centred, feet on the bottom row"""
    out = np.zeros((H, W, 4), np.uint8)
    h, w = a.shape[:2]
    x = (W - w) // 2
    y = H - h if anchor == "bottom" else (H - h) // 2
    out[y:y + h, x:x + w] = a
    return out
