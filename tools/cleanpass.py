"""Clean pass (art/fixes): remove lone pixels without blurring.
A lone pixel = an opaque pixel none of whose 8 neighbours has its exact colour. It takes the most common colour
among its opaque 8 neighbours, but only when that colour is close to it (RGB distance < TOL): noise between two
near tones goes, deliberate single pixels (eyes, highlights, outline corners, window dots) stay. Silhouette edge
pixels are never changed, alpha is never changed, no new colours appear. Optional: --max-colours N merges the least
used colours into their nearest kept colour. --wrap: the art tiles sideways (ground strips)."""
import sys, argparse, numpy as np
from PIL import Image

def lone_mask(key, a, wrap):
    h, w = key.shape
    pad = np.pad(key, 1, mode="wrap") if wrap else np.pad(key, 1, constant_values=-2)
    same = np.zeros_like(a)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy: same |= pad[1+dy:1+dy+h, 1+dx:1+dx+w] == key
    return a & ~same

def keys(rgb, a):
    k = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    return np.where(a, k, -1)

def lone_pct(rgb, a, wrap=False): return lone_mask(keys(rgb, a), a, wrap).sum() / a.sum() * 100

def clean(rgb, a, tol, wrap, passes=3):
    h, w = a.shape
    pa = np.pad(a, 1, mode="wrap" if wrap else "constant")
    edge = a & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:]) if not wrap else a & ~(pa[:-2, 1:-1] & pa[2:, 1:-1])
    rgb = rgb.copy(); total = 0
    for _ in range(passes):
        key = keys(rgb, a)
        lone = lone_mask(key, a, wrap) & ~edge
        ys, xs = np.nonzero(lone); changed = 0
        new = rgb.copy()
        for y, x in zip(ys, xs):
            nb = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if not (dx or dy): continue
                    yy, xx = y + dy, x + dx
                    if wrap: xx %= w
                    if 0 <= yy < h and 0 <= xx < w and a[yy, xx]:
                        k = int(key[yy, xx]); nb[k] = nb.get(k, 0) + 1
            if not nb: continue
            best = max(nb.items(), key=lambda kv: kv[1])
            if best[1] < 3: continue                        # no clear majority around it: leave it
            c = np.array([(best[0] >> 16) & 255, (best[0] >> 8) & 255, best[0] & 255])
            if np.sqrt(((c - rgb[y, x].astype(int)) ** 2).sum()) < tol:
                new[y, x] = c; changed += 1
        rgb = new; total += changed
        if not changed: break
    return rgb, total

def reduce_colours(rgb, a, n):
    key = keys(rgb, a)
    u, cnt = np.unique(key[a], return_counts=True)
    if len(u) <= n: return rgb, 0
    order = np.argsort(cnt)[::-1]; keep = u[order[:n]]; drop = u[order[n:]]
    kc = np.stack([(keep >> 16) & 255, (keep >> 8) & 255, keep & 255], 1).astype(int)
    rgb = rgb.copy()
    for d in drop:
        dc = np.array([(d >> 16) & 255, (d >> 8) & 255, d & 255])
        lum = lambda c: c @ np.array([0.299, 0.587, 0.114])
        dist = ((kc - dc) ** 2).sum(1) + 4 * (lum(kc) - lum(dc)) ** 2     # keep values (the layer ladder) first
        rgb[key == d] = kc[dist.argmin()]
    return rgb, len(drop)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--tol", type=float, default=60); ap.add_argument("--max-colours", type=int)
    ap.add_argument("--wrap", action="store_true")
    o = ap.parse_args()
    im = np.array(Image.open(o.src).convert("RGBA"))
    a = im[..., 3] > 127
    rgb = im[..., :3]
    before = (lone_pct(rgb, a, o.wrap), len(np.unique(keys(rgb, a)[a])))
    merged = 0
    if o.max_colours: rgb, merged = reduce_colours(rgb, a, o.max_colours)
    rgb, n = clean(rgb, a, o.tol, o.wrap)
    im[..., :3] = rgb
    Image.fromarray(im).save(o.dst)
    after = (lone_pct(rgb, a, o.wrap), len(np.unique(keys(rgb, a)[a])))
    print(f"{o.src.split('/')[-1]:24} lone {before[0]:5.1f}% -> {after[0]:5.1f}%  colours {before[1]} -> {after[1]}  changed {n} px, merged {merged}")
