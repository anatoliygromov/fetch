# Night branch art (6 Oct 2026): the leftover greyboxes of River Walk get real art.
# Sources in source_scenery/ (SpriteCook, 1 image px = 1 art px but ~2000-4600 near-duplicate colours).
#   pier_spritecook.png      -> art/scene/pier.png     granite bridge abutment over the crawl passage (screen 7)
#   pontoon_spritecook.png   -> art/scene/pontoon.png  the drifting pontoon (screen 5)
#   pile_spritecook.png      -> art/scene/pile.png     dark mooring pile in the foreground frame
#   clouds_*_spritecook.png  -> art/scene/cloud1..N.png  sky clouds
#   bones are drawn here by hand (art/scene/bone.png, bone_gold.png)
# Nothing is resampled smoothly: sizes change by cutting or repeating whole rows/columns, or by block reduction.
import os, numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import rgb2lab
from sklearn.cluster import KMeans
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source_scenery')
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'scene')

def load(n):
    a = np.array(Image.open(os.path.join(SRC, n)).convert('RGBA'))
    ys, xs = np.nonzero(a[..., 3] > 20)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def palette(a, k, seed=1):
    # k-means in Lab over the opaque pixels, then a despeckle pass (lone pixels take their neighbours' colour)
    H, W = a.shape[:2]
    on = a[..., 3] > 20
    rgb = a[..., :3]
    lab = rgb2lab(rgb / 255.0)
    km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(lab[on])
    idx = np.full((H, W), -1); idx[on] = km.labels_
    pal = np.array([rgb[on][km.labels_ == i].mean(0) for i in range(k)]).round().astype(np.uint8)
    for _ in range(2):
        out = idx.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                c = idx[y, x]
                if c < 0: continue
                nb = idx[y - 1:y + 2, x - 1:x + 2].ravel().tolist(); nb.pop(4)
                if min(nb) < 0 or sum(1 for n in nb if n == c) > 1: continue
                vals, cnt = np.unique(nb, return_counts=True)
                if cnt.max() >= 5: out[y, x] = vals[np.argmax(cnt)]
        idx = out
    o = np.zeros((H, W, 4), np.uint8)
    o[idx >= 0, :3] = pal[idx[idx >= 0]]; o[idx >= 0, 3] = 255
    return o

def cut_cols(a, x0, n): return np.concatenate([a[:, :x0], a[:, x0 + n:]], axis=1)
def best_cut(a, lo, hi, n):
    # the column x in lo..hi where removing n columns leaves the smallest seam (column x vs column x+n)
    v = a[..., :3].astype(int)
    return min(range(lo, hi), key=lambda x: np.abs(v[:, x] - v[:, x + n]).sum())

def pier():
    # 188 x 167 -> 138 wide: one brick period (25 px) is cut out of each side panel, where the cornice has no
    # joints, so the courses and the balustrade stay whole. Then the dark strip under the lintel is cut back to
    # the lintel and a passage is added below it (see scene.lua: it is drawn behind Pepper).
    a = load('pier_spritecook.png')
    x = best_cut(a, 8, 30, 25); a = cut_cols(a, x, 25)
    x = best_cut(a, a.shape[1] - 45, a.shape[1] - 30, 25); a = cut_cols(a, x, 25)
    a = palette(a, 12)
    # the lintel's last row: the lowest row that is mostly light stone
    L = a[..., :3].astype(int).sum(2)
    rows = [y for y in range(a.shape[0]) if (L[y] > 350).mean() > 0.6]
    a = a[:max(rows) + 2]                                         # + its dark outline row
    return a

# the pontoon: SpriteCook drew it about 4x the game's scale, and a 4x reduction came out muddy, so it is drawn
# here by hand at 54 x 12 in the render's own colours (sampled from it): a plank deck seen slightly from above,
# its front board, two float drums and a cleat. Pepper stands on deck row 2 (the mover's top).
def _pontoon_rows():
    W = 54
    def row(fill, l, r, mid=None, every=None, off=0):
        r_ = [' '] * W
        for x in range(l, r + 1): r_[x] = fill
        r_[l] = r_[r] = 'o'
        if mid:
            for x in range(l + 1 + off, r, every): r_[x] = mid
        return ''.join(r_)
    rows = [row('o', 2, 51),
            row('h', 1, 52, 'L', 7, 6),
            row('d', 0, 53, 'k', 7, 6),
            row('d', 0, 53, 'k', 7, 6),
            row('f', 0, 53),
            row('s', 0, 53),
            row('o', 1, 52)]
    floats = []
    for fill, mid in (('G', None), ('g', 'x'), ('g', 'x'), ('q', 'x')):
        a = list(row(fill, 3, 21, mid, 8, 6)); b = row(fill, 32, 50, mid, 8, 4)
        floats.append(''.join(b[x] if x >= 32 else a[x] for x in range(W)))
    a = list(row('o', 4, 20)); b = row('o', 33, 49)
    floats.append(''.join(b[x] if x >= 33 else a[x] for x in range(W)))
    rows += floats
    rows[2] = rows[2][:27] + 'cc' + rows[2][29:]                    # the cleat
    rows[1] = rows[1][:26] + 'oo' + rows[1][28:] if False else rows[1]
    return rows
PONTOON = _pontoon_rows()
PONTOON_PAL = {'o': '2c3035', 'h': 'b7b1a1', 'L': '9c9688', 'd': '878277', 'k': '625d53', 'c': '1c1f22',
               'f': '625d53', 's': '423f39', 'G': '6b747a', 'g': '4a5257', 'x': '2c3035', 'q': '383d42'}
def pontoon():
    # colours sampled from the render (k-means, 7 colours: 2c3035 423f39 4a5257 625d53 878277 b7b1a1), plus
    # two in-between shades for the plank seams and the floats' top
    o = np.zeros((len(PONTOON), len(PONTOON[0]), 4), np.uint8)
    for y, r in enumerate(PONTOON):
        for x, ch in enumerate(r):
            if ch in PONTOON_PAL: o[y, x, :3] = hexc(PONTOON_PAL[ch]); o[y, x, 3] = 255
    return o

def half(a):
    a = a.astype(int); H, W = a.shape[:2]
    p = np.zeros(((H + 1) // 2 * 2, (W + 1) // 2 * 2, 4), int); p[:H, :W] = a
    out = np.zeros((p.shape[0] // 2, p.shape[1] // 2, 4), np.uint8)
    for y in range(out.shape[0]):
        for x in range(out.shape[1]):
            blk = p[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(4, 4)
            on = blk[blk[:, 3] > 20]
            if len(on) < 2: continue
            vals, cnt = np.unique(on, axis=0, return_counts=True)
            out[y, x] = vals[np.argmax(cnt)]; out[y, x, 3] = 255
    return out

def pile():
    # halved (36 -> 18 wide), then lengthened to 182 px by repeating plain pole rows between the iron bands
    a = palette(load('pile_spritecook.png'), 8)
    a = half(a)
    H = a.shape[0]
    # plain rows: rows that equal the next row
    same = [y for y in range(H - 1) if (a[y] == a[y + 1]).all()]
    need = 182 - H
    if need > 0:
        pick = same[len(same) // 3] if same else H // 3
        pick2 = same[2 * len(same) // 3] if len(same) > 2 else pick
        a = np.concatenate([a[:pick], np.repeat(a[pick:pick + 1], need // 2, 0), a[pick:pick2],
                            np.repeat(a[pick2:pick2 + 1], need - need // 2, 0), a[pick2:]], 0)
    return a

def clouds():
    out = []
    for n in ('clouds_a_spritecook.png', 'clouds_b_spritecook.png'):
        a = palette(load(n), 5)
        lab, k = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
        for i in range(1, k + 1):
            ys, xs = np.nonzero(lab == i)
            if len(ys) < 150: continue
            c = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
            c[lab[ys.min():ys.max() + 1, xs.min():xs.max() + 1] != i] = 0
            out.append(c)
    out.sort(key=lambda c: -c.shape[1])
    return out

# bones, by hand. o outline, w bone, s shade, h highlight
BONE = ['.oo.....oo.',
        'ohwo...owwo',
        '.owwwwwwwo.',
        '.owsssssso.',
        'owso...osso',
        '.oo.....oo.']
def bone(pal):
    h, w = len(BONE), len(BONE[0])
    o = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(BONE):
        for x, ch in enumerate(r):
            if ch in pal: o[y, x, :3] = pal[ch]; o[y, x, 3] = 255
    return o
def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

if __name__ == '__main__':
    def save(a, n):
        Image.fromarray(a).save(os.path.join(OUT, n))
        print(n, a.shape[1], 'x', a.shape[0], len(np.unique(a[a[..., 3] > 0][:, :3], axis=0)), 'colours')
    save(pier(), 'pier.png')
    save(pontoon(), 'pontoon.png')
    save(pile(), 'pile.png')
    for i, c in enumerate(clouds()): save(c, 'cloud%d.png' % (i + 1))
    save(bone({'o': hexc('5b4a36'), 'w': hexc('f4eddc'), 's': hexc('d2c5a6'), 'h': hexc('ffffff')}), 'bone.png')
    save(bone({'o': hexc('6b4410'), 'w': hexc('f6cf4f'), 's': hexc('d39a2a'), 'h': hexc('fff6c8')}), 'bone_gold.png')
