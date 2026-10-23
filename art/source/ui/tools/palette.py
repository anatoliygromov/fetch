# one shared palette for the kit (k-means, weighted), then a clean pass: lone pixels that are only a shade off
# their neighbours take the neighbours' colour; real detail (eyes, highlights far from neighbours) stays.
import sys, os, glob, json, numpy as np
from PIL import Image
from scipy.cluster.vq import kmeans2
from scipy import ndimage
K = int(sys.argv[1]) if len(sys.argv) > 1 else 48
RAW = '/tmp/claude-0/ui/kit/raw'; OUT = '/tmp/claude-0/ui/kit/clean'; os.makedirs(OUT, exist_ok=True)
files = sorted(glob.glob(RAW + '/*.png'))
imgs = {os.path.basename(f)[:-4]: np.array(Image.open(f).convert('RGBA')) for f in files}
px = np.concatenate([p[p[...,3] > 0][:, :3] for p in imgs.values()]).astype(float)
def lab(rgb):  # cheap perceptual space: scaled RGB with luma emphasis
    r,g,b = rgb[...,0], rgb[...,1], rgb[...,2]
    y = 0.299*r + 0.587*g + 0.114*b
    return np.stack([y*1.5, (r-g)*0.8, (b-(r+g)/2)*0.6], -1)
np.random.seed(3)
sample = px[np.random.choice(len(px), min(len(px), 60000), replace=False)]
cent, _ = kmeans2(lab(sample), K, minit='++', iter=40, seed=3)
# palette colour = mean RGB of the members (in RGB)
lbl = np.argmin(((lab(sample)[:, None, :] - cent[None]) ** 2).sum(-1), 1)
pal = np.array([sample[lbl == k].mean(0) if (lbl == k).any() else [0,0,0] for k in range(K)]).round().astype(np.uint8)
CAP = {'digit': 6, 'letter': 6, 'cursor': 6, 'heart': 6, 'icon': 8, 'medal': 8, 'btn': 7, 'dpad': 6, 'toggle': 8,
       'volume': 6, 'row': 8, 'ribbon': 8, 'panel': 10, 'health': 11, 'pepper': 10}
def cap_for(n):
    for k, v in CAP.items():
        if n.startswith(k): return v
    return 10
def nearest(c, P): return np.argmin(((lab(c.astype(float))[:, None, :] - lab(P.astype(float))[None]) ** 2).sum(-1), 1)
def own_palette(p, k):
    c = p[p[...,3] > 0][:, :3].astype(float); cent, l = kmeans2(c, k, minit='++', iter=40, seed=5)
    return np.array([c[l == i].mean(0) for i in range(k) if (l == i).any()]).round().astype(np.uint8)
def quant(p, n):
    out = p.copy(); m = p[...,3] > 0
    if n.startswith('pepper'):
        P = own_palette(p, 10); k = nearest(p[...,:3][m], P); out[...,:3][m] = P[k]; out[...,3] = np.where(m, 255, 0); return out
    k = nearest(p[...,:3][m], pal)
    # keep the piece's most used palette colours (its ramps), remap the rest to the nearest kept one
    used, cnt = np.unique(k, return_counts=True); order = used[np.argsort(-cnt)]
    keep = list(order[:cap_for(n)])
    # always keep the darkest used colour (the outline) and the lightest (the highlight)
    lum = lambda i: pal[i].astype(float) @ [0.299, 0.587, 0.114]
    for extra in (min(used, key=lum), max(used, key=lum)):
        if extra not in keep: keep[-1 if len(keep) >= cap_for(n) else len(keep):] = [extra]
    keep = np.array(sorted(set(keep)))
    k2 = keep[nearest(pal[k], pal[keep])]
    out[...,:3][m] = pal[k2]; out[...,3] = np.where(m, 255, 0); return out
def lone(p):
    a = p[...,3] > 0; key = (p[...,0].astype(int) << 16) | (p[...,1].astype(int) << 8) | p[...,2]
    H, W = a.shape; L = np.zeros_like(a)
    for y in range(H):
        for x in range(W):
            if not a[y, x]: continue
            same = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (dy or dx) and 0 <= y+dy < H and 0 <= x+dx < W and a[y+dy, x+dx] and key[y+dy, x+dx] == key[y, x]: same = True
            L[y, x] = not same
    return L
def clean(p, thr=70):
    p = p.copy(); L = lone(p); H, W = L.shape; fixed = 0
    a = p[...,3] > 0; edge = a & ~ndimage.binary_erosion(a, structure=np.ones((3,3)), border_value=0)
    lum = p[...,:3].astype(float) @ [0.299, 0.587, 0.114]
    for y, x in zip(*np.nonzero(L & edge & (lum > 90))): p[y, x, 3] = 0
    L = lone(p)
    for y, x in zip(*np.nonzero(L)):
        nb = [tuple(p[y+dy, x+dx, :3]) for dy in (-1,0,1) for dx in (-1,0,1) if (dy or dx) and 0 <= y+dy < H and 0 <= x+dx < W and p[y+dy, x+dx, 3]]
        if not nb: p[y, x, 3] = 0; continue
        vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True); best = vals[cnt.argmax()]
        if np.abs(best.astype(int) - p[y, x, :3].astype(int)).sum() < thr * 3 and cnt.max() >= 3: p[y, x, :3] = best; fixed += 1
    return p, fixed
report = {}
for n, p in imgs.items():
    q = quant(p, n); l0 = lone(q).sum() / max(1, (q[...,3] > 0).sum())
    c, f = clean(q); c2, f2 = clean(c)
    l1 = lone(c2).sum() / max(1, (c2[...,3] > 0).sum())
    Image.fromarray(c2).save(f'{OUT}/{n}.png')
    report[n] = dict(size=[p.shape[1], p.shape[0]], colours=int(len(np.unique(c2[c2[...,3] > 0][:, :3], axis=0))), lone_before=round(100*l0, 1), lone_after=round(100*l1, 1))
json.dump(report, open('/tmp/claude-0/ui/kit/clean_report.json', 'w'), indent=1)
Image.fromarray(np.repeat(np.repeat(pal[None], 8, 0), 8, 1)).save('/tmp/claude-0/ui/kit/palette.png')
for n, r in report.items(): print(f"{n:18s} {r['size'][0]:3d}x{r['size'][1]:3d} col {r['colours']:2d} lone {r['lone_before']:5.1f}% -> {r['lone_after']:4.1f}%")
