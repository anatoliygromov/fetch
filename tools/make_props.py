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
    ('gritbox_spritecook.png', 'gritbox.png', 14),
    ('planter_sq_spritecook.png', 'planter_sq.png', 14),
    ('cafe_spritecook.png', 'cafe.png', 28),
    ('ferry_spritecook.png', 'ferry.png', 24),
    ('tree_near_spritecook.png', 'tree_near.png', 20),
    ('tree_far_spritecook.png', 'tree_far.png', 20),
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
FONT = {'S': ['###', '#..', '###', '..#', '###'], 'A': ['.#.', '#.#', '###', '#.#', '#.#'],
        'N': ['#..#', '##.#', '#.##', '#..#', '#..#'], 'D': ['##.', '#.#', '#.#', '#.#', '##.']}
def grit_prep(a):
    # the grit box (sandlåda) also came out at 2x; halved, its SAND label smears, so the label is repainted:
    # the plank between the dark lines (rows 26-31) is cleared to its own colour and SAND is set in a 3x5 font
    a = half(a)
    plank = a[28, 40].copy(); ink = np.array([188, 200, 186, 255], np.uint8)
    for y in range(26, 32):
        for x in range(46, 66):
            if a[y, x, 3]: a[y, x] = plank
    x = 48
    for ch in 'SAND':
        g = FONT[ch]
        for dy, row in enumerate(g):
            for dx, c in enumerate(row):
                if c == '#': a[26 + dy, x + dx] = ink
        x += len(g[0]) + 1
    return a
def deoutline(a):
    # decoration has no dark outline (that is for things Pepper can use): each outline pixel on the silhouette's
    # edge takes the colour of its brightest opaque neighbour inside the shape
    a = a.copy(); H, W = a.shape[:2]
    on = a[..., 3] > 0
    L = a[..., :3].astype(int).sum(2)
    edge = [(y, x) for y in range(H) for x in range(W) if on[y, x] and any(
        not (0 <= y + dy < H and 0 <= x + dx < W and on[y + dy, x + dx]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    es = set(edge); out = a.copy()
    for y, x in edge:
        if L[y, x] > 200: continue                                 # already light: not an outline pixel
        best = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and on[yy, xx] and (yy, xx) not in es and L[yy, xx] > L[y, x] + 60:
                    if best is None or L[yy, xx] > L[best]: best = (yy, xx)
        if best: out[y, x] = a[best]
    return out
def ferry_prep(a):
    # "a little bigger" (user): the open decks get longer and the saloon windows, the white band and the hull taller,
    # by repeating plain columns and rows (no seams): 222 x 84 becomes 252 x 93
    def grow(a, spec, axis):
        parts, prev = [], 0
        for i in sorted(spec):
            parts.append(np.take(a, range(prev, i + 1), axis=axis))
            parts.append(np.repeat(np.take(a, [i], axis=axis), spec[i], axis=axis)); prev = i + 1
        parts.append(np.take(a, range(prev, a.shape[axis]), axis=axis))
        return np.concatenate(parts, axis=axis)
    return grow(grow(a, {13: 4, 24: 6, 31: 5, 170: 5, 185: 6, 193: 4}, 1), {54: 4, 65: 2, 75: 3}, 0)
PREP = {'bench.png': bench_prep, 'gritbox.png': grit_prep, 'ferry.png': ferry_prep,
        'tree_far.png': lambda a: deoutline(half(a)), 'tree_near.png': deoutline,
        'cafe.png': deoutline, 'gable.png': deoutline}
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
