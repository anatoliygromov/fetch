# Cleans the SpriteCook obstacle and building art (round 2, 5 Oct 2026) into riverwalk/art/scene/.
# Each source in source_scenery/ is a cropped SpriteCook render with ~500-7000 near-duplicate colours.
#   * palette: k-means in Lab (16 colours for props, 28 for buildings), so the art matches the hand-sized
#     palettes of the screen-1 building (16) and keeps its pixel grid (no scaling)
#   * despeckle: a lone pixel whose 8 neighbours mostly share one close colour takes that colour
#   * buildings: specks that float free of the facade (cut-off side balconies) are dropped
#   * these assets carry their own 1 px dark outline, so Sc.outline is NOT applied on top
import os, numpy as np
from PIL import Image
from skimage.color import rgb2lab
from sklearn.cluster import KMeans
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = [  # source, output, colours
    ('bench_v2_spritecook.png', 'bench.png', 16),
    ('bin_v2_spritecook.png', 'bin.png', 14),
    ('flowerbox_spritecook.png', 'flowerbox.png', 16),
    ('flowerbox_low_spritecook.png', 'flowerbox_low.png', 16),
    ('planter_sq_spritecook.png', 'planter_sq.png', 14),
    ('cafe_spritecook.png', 'cafe.png', 28),
    ('gable_spritecook.png', 'gable.png', 24),
]
def half(a):
    # the Stockholm bench came out at twice the game's pixel scale: each 2x2 block becomes one pixel, keeping the
    # darkest pixel where the block holds outline (so 1 px lines survive) and the median colour elsewhere
    a = a.astype(int)
    H, W = a.shape[:2]
    p = np.zeros(((H + 1) // 2 * 2, (W + 1) // 2 * 2, 4), int); p[:H, :W] = a
    out = np.zeros((p.shape[0] // 2, p.shape[1] // 2, 4), np.uint8)
    for y in range(out.shape[0]):
        for x in range(out.shape[1]):
            blk = p[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(4, 4)
            on = blk[blk[:, 3] > 20]
            if len(on) < 2: continue
            L = on[:, :3].sum(1)
            c = on[np.argmin(L)] if L.min() < 120 else np.median(on, axis=0)
            out[y, x, :3] = c[:3]; out[y, x, 3] = 255
    return out
def bench_prep(a):
    a = half(a)                                                    # 103 x 48
    # longer posts: post row 40 is repeated 3 times, so the seat top is 28 px up (y 156, above the bikes) and
    # Pepper has 19 px to crawl under it, as with the bench before
    return np.concatenate([a[:41], np.repeat(a[40:41], 3, axis=0), a[41:]], axis=0)
PREP = {'bench.png': bench_prep}
def clean(src, k, solo=False, prep=None):
    a = np.array(Image.open(src).convert('RGBA'))
    if prep: a = prep(a)
    H, W = a.shape[:2]
    on = a[..., 3] > 20
    rgb = a[..., :3]
    lab = rgb2lab(rgb / 255.0)
    km = KMeans(n_clusters=k, n_init=4, random_state=1).fit(lab[on])
    idx = np.full((H, W), -1)
    idx[on] = km.labels_
    pal = np.array([rgb[on][km.labels_ == i].mean(0) for i in range(k)]).round().astype(np.uint8)
    for _ in range(2):
        out = idx.copy()
        for y in range(H):
            for x in range(W):
                c = idx[y, x]
                if c < 0: continue
                nb = [idx[yy, xx] for yy in range(max(0, y - 1), min(H, y + 2)) for xx in range(max(0, x - 1), min(W, x + 2)) if (yy, xx) != (y, x)]
                nb = [n for n in nb if n >= 0]
                if len(nb) == 8 and sum(1 for n in nb if n == c) <= 1:
                    vals, cnt = np.unique(nb, return_counts=True)
                    m = vals[np.argmax(cnt)]
                    if cnt.max() >= 5 and np.linalg.norm(lab[y, x] - km.cluster_centers_[m]) < 18: out[y, x] = m
        idx = out
    if solo:                                                       # keep the facade and what touches it
        from scipy import ndimage
        lab_, n = ndimage.label(idx >= 0, structure=np.ones((3, 3)))
        sizes = ndimage.sum(np.ones_like(lab_), lab_, range(1, n + 1))
        idx[(lab_ > 0) & (lab_ != 1 + int(np.argmax(sizes)))] = -1
    o = np.zeros((H, W, 4), np.uint8)
    o[idx >= 0, :3] = pal[idx[idx >= 0]]
    o[idx >= 0, 3] = 255
    return o
if __name__ == '__main__':
    for s, d, k in JOBS:
        o = clean(os.path.join(ROOT, 'source_scenery', s), k, d in ('cafe.png', 'gable.png'), PREP.get(d))
        if d == 'cafe.png':                                        # side balconies and a wall plant stick out past
            o[32:, :6] = 0; o[32:, 149:] = 0                       # the facade below the roof: trim to the wall
            o = o[:, :150]
        Image.fromarray(o).save(os.path.join(ROOT, 'riverwalk', 'art', 'scene', d))
        print(d, o.shape[1], 'x', o.shape[0], len(np.unique(o[o[..., 3] > 0][:, :3], axis=0)), 'colours')
