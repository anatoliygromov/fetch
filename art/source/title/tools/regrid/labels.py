"""Step 2a: palette from the painting's flat areas and a full-resolution label map.

Every source pixel gets one palette index. Flat pixels take the nearest palette
colour. Edge pixels (the painting's anti-aliasing) are snapped to the colour of a
nearby flat pixel instead, so blends between two materials never become a third
colour.
"""
import numpy as np, os
from scipy import ndimage as ndi
from sklearn.cluster import KMeans
from common import load_src, srgb_to_lab, CACHE


def flat_mask(a, thr=10.0):
    f = a.astype(np.float32)
    g = np.zeros(a.shape[:2], np.float32)
    for ax in (0, 1):
        d = np.abs(np.roll(f, -1, ax) - np.roll(f, 1, ax)).max(2) * 0.5
        g = np.maximum(g, d)
    return g < thr, g


def build_palette(a, flat, k=96, merge_de=3.0, seed=0):
    lab = srgb_to_lab(a)
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(flat.ravel())
    pick = rng.choice(idx, size=min(400000, len(idx)), replace=False)
    X = lab.reshape(-1, 3)[pick]
    km = KMeans(n_clusters=k, n_init=2, random_state=seed, max_iter=200).fit(X)
    lab_l = km.labels_
    rgb = a.reshape(-1, 3)[pick].astype(np.float32)
    pal, cnt = [], []
    for c in range(k):
        m = lab_l == c
        if m.sum() < 50:
            continue
        # representative = medoid-ish: the most common exact colour bin near the centre
        sub = rgb[m]
        q = (sub // 4).astype(np.int32)
        key = q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2]
        v, n = np.unique(key, return_counts=True)
        best = v[n.argmax()]
        pal.append(sub[key == best].mean(0)); cnt.append(m.sum())
    pal = np.array(pal); cnt = np.array(cnt)
    # merge near duplicates
    order = np.argsort(-cnt)
    keep = []
    pl = srgb_to_lab(pal)
    for i in order:
        if all(np.linalg.norm(pl[i] - pl[j]) > merge_de for j in keep):
            keep.append(i)
    return np.round(pal[keep]).astype(np.uint8)


def nearest(lab, pal_lab, chunk=1 << 20):
    flat = lab.reshape(-1, 3)
    out = np.empty(len(flat), np.int16)
    for s in range(0, len(flat), chunk):
        d = ((flat[s:s + chunk, None, :] - pal_lab[None]) ** 2).sum(-1)
        out[s:s + chunk] = d.argmin(1)
    return out.reshape(lab.shape[:2])


def label_map(a, pal, flat):
    lab = srgb_to_lab(a)
    pl = srgb_to_lab(pal)
    L = nearest(lab, pl)
    # snap edge pixels to the closest colour among nearby flat pixels
    best = np.where(flat, 0.0, np.inf).astype(np.float32)
    out = L.copy()
    H, W = L.shape
    offs = [(dy, dx) for r in (1, 2, 3, 4) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if max(abs(dy), abs(dx)) == r]
    for dy, dx in offs:
        Ls = np.roll(L, (-dy, -dx), (0, 1)); fs = np.roll(flat, (-dy, -dx), (0, 1))
        d = ((lab - pl[Ls]) ** 2).sum(-1) + 0.5 * (dy * dy + dx * dx)
        d = np.where(fs, d, np.inf)
        upd = (~flat) & (d < best)
        best[upd] = d[upd]; out[upd] = Ls[upd]
    return out


def run(force=False):
    p = os.path.join(CACHE, 'labels.npz')
    if os.path.exists(p) and not force:
        z = np.load(p); return z['pal'], z['L'], z['flat']
    a = load_src()
    flat, _ = flat_mask(a)
    pal = build_palette(a, flat)
    L = label_map(a, pal, flat)
    np.savez_compressed(p, pal=pal, L=L, flat=flat)
    return pal, L, flat


if __name__ == '__main__':
    import sys
    pal, L, flat = run(force=True)
    print('palette', len(pal), 'flat frac', flat.mean())
