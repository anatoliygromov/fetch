"""Light-touch cleanup of the title picture (24 Oct, 0 credits): picture "light" (T.PICTURE in riverwalk/title.lua).
    python3 -I art/source/title/tools/light_clean.py [--threshold 12] [--strict] [--report]     (from the repo root)

Starts from the painting on its native grid (the build's layers before the material cleanup, commit eac9c04, kept in
art/source/title/painting_layers/) and keeps its value structure and shading. No ramps, no blur, no mode filter:
every shade band of the painting stays. Only specks change:
  a speck is a bit of one colour of 1 or 2 pixels (4-connected, so a pixel that touches its colour only at a
  corner counts: the painting's noise is a diagonal checker of two shades) whose luma differs from the median of
  the pixels round it by more than THRESHOLD luma steps. It takes the colour of the ring's majority (a colour seen
  at least twice; ties go to the one nearest the ring's median luma), counting only the ring pixels of its own
  material (art/source/title/masks). A speck whose ring is mostly another material is left alone (no merge
  across a material edge). Three passes, the most deviant specks first; a speck next to one just changed waits
  for the next pass.
  --strict: the narrow rule only (single pixels with no same-colour 8-neighbour). On this painting it changes
  0.8 % of the pixels and the result looks the same as the painting: its noise is diagonal and 2 px crumbs.
Protected: lines (a same-colour diagonal chain of 3 or more pixels about as long as its box, and ink, luma under
16, joined to 2 or more other ink pixels: outlines, lashes, the mouth line); the eye and nose (catchlights), the
far city (its 1 to 2 px windows), the flowers, the lantern and the boats; the logo area (no mask: the logo layer
covers it). Before that, colours closer than dE 2.5 merge into the more used one (2 pairs of dark blues).

Writes riverwalk/art/title/base_light.png, mouth_light.png, eye_light.png (Pepper's pant and blink, animated by
diff: each frame is the light still outside the pixels the painting's frame changes; those pixels cleaned the same
way) and bird_light.png (the painting's bird, which matches its base). --report prints the form check (5x5 box blur
of luma, mean and 95th percentile difference against the painting) and the lone-pixel rates for the painting (A),
the current default "clean" (B, a1e0e15), the rejected hand shading pass (C, a3096c6) and this result (D).
"""
import os, io, re, subprocess, argparse
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import rgb2lab

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'art', 'source', 'title', 'painting_layers')
MASKS = os.path.join(ROOT, 'art', 'source', 'title', 'masks')
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'title')
THRESHOLD = 12           # luma steps (0..255) between a speck and the median of the pixels round it
MAXSIZE, PASSES = 2, 3
SKIP = ('eye', 'nose', 'city', 'flowers', 'lantern', 'boats')
PEPPER = ('coat', 'nose', 'eye', 'tongue', 'bandana')
MERGE_DE = 2.5
INK = 16
OFFS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ST4, ST8 = ndimage.generate_binary_structure(2, 1), np.ones((3, 3), bool)

def load(p): return np.array(Image.open(p).convert('RGB')).astype(np.int32)
def luma(a): return a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
def key(a): return (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]
def rgb(k): return [(k >> 16) & 255, (k >> 8) & 255, k & 255]

def materials(shape):
    names = sorted(f[:-4] for f in os.listdir(MASKS) if f.endswith('.png'))
    lab = np.full(shape, -1, np.int32)
    for i, n in enumerate(names): lab[np.array(Image.open(os.path.join(MASKS, n + '.png'))) > 0] = i
    return lab, names

def lone_mask(img):
    """pixels with no same-colour 8-neighbour"""
    k = key(img); H, W = k.shape; p = np.pad(k, 1, constant_values=-1)
    return ~np.stack([p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] == k for dy, dx in OFFS]).any(0)

def merge_twins(img):
    pal, inv, cnt = np.unique(img.reshape(-1, 3), axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(img.shape[:2]); lab = rgb2lab(pal[None] / 255.0)[0]
    d = np.sqrt(((lab[:, None] - lab[None]) ** 2).sum(2)); np.fill_diagonal(d, 99)
    to = np.arange(len(pal))
    for a, b in zip(*np.where(np.triu(d < MERGE_DE))):
        lo, hi = (a, b) if cnt[a] < cnt[b] else (b, a)
        to[to == to[lo]] = to[hi]
    return pal[to[inv]].astype(np.int32)

def protected_lines(img):
    """thin diagonal chains of one colour (a checker texture fills its box instead) and joined ink strokes"""
    k = key(img); out = np.zeros(k.shape, bool)
    for c in np.unique(k):
        lb, n = ndimage.label(k == c, ST8)
        for i, sl in enumerate(ndimage.find_objects(lb), 1):
            comp = lb[sl] == i; sz = comp.sum()
            if sz >= 3 and sz <= 1.3 * max(comp.shape): out[sl] |= comp
    ink = luma(img) < INK
    lb, n = ndimage.label(ink, ST8)
    out |= ink & (np.bincount(lb.ravel())[lb] >= 3)
    return out

def clean(img, mat, names, threshold=THRESHOLD, strict=False):
    """returns the cleaned picture and the mask of changed pixels"""
    out = merge_twins(img); H, W = mat.shape
    skip = np.isin(mat, [names.index(s) for s in SKIP if s in names]) | (mat < 0)
    for _ in range(PASSES):
        k = key(out); Y = luma(out)
        prot = skip | protected_lines(out)
        if strict: prot |= ~lone_mask(out)
        lab = np.zeros((H, W), np.int32); nl = 0
        for c in np.unique(k):
            lb, n = ndimage.label(k == c, ST4); lab[lb > 0] = lb[lb > 0] + nl; nl += n
        size = np.bincount(lab.ravel())
        objs = ndimage.find_objects(lab)
        jobs = []
        for i in np.unique(lab[(size[lab] <= (1 if strict else MAXSIZE)) & ~prot]):
            sl = objs[i - 1]
            y0, y1, x0, x1 = max(sl[0].start - 1, 0), min(sl[0].stop + 1, H), max(sl[1].start - 1, 0), min(sl[1].stop + 1, W)
            comp = lab[y0:y1, x0:x1] == i
            if prot[y0:y1, x0:x1][comp].any(): continue
            mm = mat[y0:y1, x0:x1]; m0 = mm[comp][0]
            if (mm[comp] != m0).any(): continue
            ring = ndimage.binary_dilation(comp, ST8) & ~comp
            same = ring & (mm == m0)
            if same.sum() < 0.6 * ring.sum(): continue               # at a material edge: never merge across it
            ks, ys = k[y0:y1, x0:x1][same], Y[y0:y1, x0:x1][same]
            med = np.median(ys); dev = abs(Y[y0:y1, x0:x1][comp][0] - med)
            if dev <= threshold: continue
            u, c = np.unique(ks, return_counts=True)
            if c.max() < 2: continue                                 # no majority round it: leave the painting
            kk = min(u[c == c.max()], key=lambda q: abs(ys[ks == q][0] - med))
            jobs.append((dev, (y0, y1, x0, x1), comp, kk))
        jobs.sort(key=lambda j: -j[0]); done = np.zeros((H, W), bool)
        for dev, (y0, y1, x0, x1), comp, kk in jobs:
            if done[y0:y1, x0:x1].any(): continue                    # a neighbour just changed: decide next pass
            out[y0:y1, x0:x1][comp] = rgb(kk); done[y0:y1, x0:x1] |= comp
        if not jobs: break
    return out, (out != img).any(2)

def data_rect(name):
    t = open(os.path.join(ROOT, 'riverwalk', 'title_data.lua')).read()
    return tuple(int(v) for v in re.search(name + r' = \{ x = (\d+), y = (\d+), w = (\d+), h = (\d+), n = (\d+)', t).groups())

def git_png(rev, path):
    try: b = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (rev, path)], capture_output=True, check=True).stdout
    except Exception: return None
    return load(io.BytesIO(b))

def form(a, b, region):
    d = np.abs(ndimage.uniform_filter(luma(a), 5, mode='nearest') - ndimage.uniform_filter(luma(b), 5, mode='nearest'))[region]
    return d.mean(), np.percentile(d, 95)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--threshold', type=float, default=THRESHOLD); ap.add_argument('--strict', action='store_true')
    ap.add_argument('--report', action='store_true'); ap.add_argument('--out', default=OUT)
    build(ap.parse_args())

def build(a=None):
    """writes the light layers (build_title.py calls this with the defaults)"""
    if a is None: a = argparse.Namespace(threshold=THRESHOLD, strict=False, report=False, out=OUT)
    A = load(os.path.join(SRC, 'base.png'))
    mat, names = materials(A.shape[:2])
    D, ch = clean(A, mat, names, a.threshold, a.strict)
    os.makedirs(a.out, exist_ok=True)
    Image.fromarray(D.astype(np.uint8)).save(os.path.join(a.out, 'base_light.png'))
    for name in ('mouth', 'eye'):
        x, y, w, h, n = data_rect(name)
        st = load(os.path.join(SRC, name + '.png')); fr = [st[:, f * w:(f + 1) * w] for f in range(n)]
        assert (fr[0] == A[y:y + h, x:x + w]).all(), name + ': frame 0 is not the painting'
        outf = []
        for f in fr:
            full = A.copy(); full[y:y + h, x:x + w] = f
            cf, _ = clean(full, mat, names, a.threshold, a.strict)
            moved = (f != fr[0]).any(2)
            o = D[y:y + h, x:x + w].copy(); o[moved] = cf[y:y + h, x:x + w][moved]; outf.append(o)
        Image.fromarray(np.concatenate(outf, 1).astype(np.uint8)).save(os.path.join(a.out, name + '_light.png'))
    Image.open(os.path.join(SRC, 'bird.png')).save(os.path.join(a.out, 'bird_light.png'))
    pep = np.isin(mat, [names.index(s) for s in PEPPER]); allr = np.ones_like(pep)
    print('light%s: threshold %g, %d px changed (%.2f %%; Pepper %d), colours %d -> %d' % (' (strict)' if a.strict else '',
          a.threshold, ch.sum(), ch.mean() * 100, (ch & pep).sum(), len(np.unique(key(A))), len(np.unique(key(D)))))
    if a.report:
        vs = [('A', A), ('B', git_png('a1e0e15', 'riverwalk/art/title/base.png')),
              ('C', git_png('a3096c6', 'riverwalk/art/title/base.png')), ('D', D)]
        print('     form vs A (5x5 luma): Pepper mean / p95    all mean / p95    lone px: Pepper / all   colours')
        for nm, v in vs:
            if v is None: continue
            lm = lone_mask(v)
            print('  %s %28.2f / %-6.2f %12.2f / %-6.2f %14.2f %% / %.2f %% %8d' % ((nm,) + form(A, v, pep) + form(A, v, allr) +
                  (lm[pep].mean() * 100, lm.mean() * 100, len(np.unique(key(v))))))

if __name__ == '__main__':
    main()
