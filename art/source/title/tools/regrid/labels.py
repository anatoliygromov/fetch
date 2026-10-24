"""Step 2: the global palette, as per-material ramps built from flat cell interiors.

Samples: the source pixels of every cell interior (cell box shrunk by 1 px) that are
flat (max channel difference to the 4 neighbours below FLAT_T). Anti-aliased edge
pixels never become palette colours.

Per material (the 320x240 masks in art/source/title/masks; cells outside every mask
are 'logo' inside the logo/tagline box, else 'other'), the samples are clustered in
CIE Lab (k-means, Gerstner et al. style "superpixel then palette" is replaced by the
grid cells themselves), clusters closer than the material's merge distance are
merged (largest support wins), and each cluster is represented by its MEDOID: the
most frequent exact colour among its members (unfake.js "dominant colour"), so every
palette colour is a colour the painting really uses in flat areas. Finally the
materials are merged globally (near duplicates collapse to the better supported
colour) and every material keeps the list of global colours that form its ramp.
"""
import numpy as np, os, json
from scipy import ndimage as ndi
from sklearn.cluster import KMeans
from common import load_src, srgb_to_lab, CACHE, OUT, NX, NY, load_mask, hexs, MASKS

FLAT_T = 10
MATERIALS = ['sky', 'clouds', 'city', 'water', 'boats', 'leaves', 'trunk', 'stone', 'lamp', 'lantern',
             'railing', 'pavement', 'bench', 'flowers', 'coat', 'bandana', 'eye', 'nose', 'tongue', 'rest']
# (k for k-means, merge distance in Lab, min support in px)
PARAMS = {'coat': (18, 3.2, 150), 'sky': (10, 4.0, 300), 'logo': (24, 4.5, 120), 'eye': (8, 6, 40),
          'nose': (8, 5, 40), 'tongue': (8, 6, 60), 'bandana': (10, 5, 100), 'flowers': (8, 7, 25),
          'lantern': (8, 6, 40)}
DEFAULT = (14, 6.0, 150)
GLOBAL_MERGE = 3.8   # always merge closer pairs than this
PAL_TARGET = 128
COAT_MIN = 8         # Pepper's coat keeps at least this many dark values (6+ values plus sheen)
LOGO_BOX = (95, 12, 305, 98)   # cells x0, y0, x1, y1 (logo and tagline)
TAG2_BOX = (150, 188, 280, 210)  # "PRESS ANY KEY" box


def material_map(erode=False):
    mat = np.full((NY, NX), -1, np.int16)
    for k, name in enumerate(MATERIALS):
        m = load_mask(name)
        if erode:
            e = ndi.binary_erosion(m)
            if e.sum() >= 0.3 * m.sum():
                m = e
        mat[m & (mat < 0)] = k
    names = MATERIALS + ['logo', 'other']
    lg = np.zeros((NY, NX), bool)
    for (x0, y0, x1, y1) in (LOGO_BOX, TAG2_BOX):
        lg[y0:y1, x0:x1] = True
    mat[(mat < 0) & lg] = len(MATERIALS)
    mat[mat < 0] = len(MATERIALS) + 1
    return mat, names


def flatness(a):
    f = a.astype(np.float32)
    g = np.zeros(a.shape[:2], np.float32)
    for ax in (0, 1):
        for s in (1, -1):
            g = np.maximum(g, np.abs(np.roll(f, s, ax) - f).max(2))
    return g


def interior_mask(I, J):
    """True for pixels that are not on the outer 1 px ring of their cell."""
    inn = np.ones(I.shape, bool)
    inn[:, 1:] &= I[:, 1:] == I[:, :-1]; inn[:, :-1] &= I[:, :-1] == I[:, 1:]
    inn[1:] &= J[1:] == J[:-1]; inn[:-1] &= J[:-1] == J[1:]
    return inn


def medoid(rgb):
    key = (rgb[:, 0].astype(np.int64) << 16) | (rgb[:, 1].astype(np.int64) << 8) | rgb[:, 2]
    v, n = np.unique(key, return_counts=True)
    if n.max() >= 3:
        b = v[n.argmax()]
        return np.array([(b >> 16) & 255, (b >> 8) & 255, b & 255], np.uint8)
    # no exact repeats: the member nearest the mean
    m = rgb.astype(np.float32).mean(0)
    return rgb[((rgb - m) ** 2).sum(1).argmin()].astype(np.uint8)


def cluster_material(rgb, k, merge, minsup, seed=0):
    lab = srgb_to_lab(rgb)
    k = min(k, max(1, len(rgb) // 50))
    km = KMeans(n_clusters=k, n_init=3, random_state=seed, max_iter=300).fit(lab)
    lbl = km.labels_
    groups = [np.flatnonzero(lbl == c) for c in range(k)]
    # merge closest pairs below `merge` (largest support keeps its identity)
    while True:
        cen = np.array([lab[g].mean(0) for g in groups])
        d = np.linalg.norm(cen[:, None] - cen[None], axis=2) + np.eye(len(groups)) * 1e9
        i, j = np.unravel_index(d.argmin(), d.shape)
        if d[i, j] >= merge:
            break
        groups[i] = np.r_[groups[i], groups[j]]; groups.pop(j)
    out = []
    for g in groups:
        if len(g) < minsup:
            continue
        out.append((medoid(rgb[g]), len(g)))
    return out


def grid_arrays(I, J):
    from grid import run as grid_run
    XB, YB, I2, J2 = grid_run()
    return XB, YB, I, J


def build(a, I, J, seed=0):
    mat, names = material_map(erode=True)
    g = flatness(a)
    inn = interior_mask(I, J)
    flat = (g < FLAT_T) & inn
    m_pix = mat[J, I]
    rng = np.random.default_rng(seed)
    per = {}
    for k, name in enumerate(names):
        sel = np.flatnonzero((flat & (m_pix == k)).ravel())
        if len(sel) < 100:
            continue
        scale = 1.0
        if len(sel) > 120000:
            scale = len(sel) / 120000; sel = rng.choice(sel, 120000, replace=False)
        rgb = a.reshape(-1, 3)[sel]
        kk, merge, minsup = PARAMS.get(name, DEFAULT)
        cl = cluster_material(rgb, kk, merge, minsup / scale, seed)
        per[name] = [(c, int(n * scale)) for c, n in cl]
    # thin strokes (masts, rigging): their centre pixels form a protected 'strokes' material,
    # so a 3 to 6 px mast keeps its own colour instead of the nearest large-area colour
    import build_bg
    lab = srgb_to_lab(a)
    st = build_bg.strokes(lab, np.zeros(a.shape[:2], np.int16), *grid_arrays(I, J))
    cm = np.zeros(a.shape[:2], bool)
    for cells, col, mask, axis, (yi, xi) in st:
        if len(cells) >= 4:                 # long strokes only
            cm[yi, xi] = True
    if cm.sum() >= 50:
        rgb = a[cm]
        cl = cluster_material(rgb, 10, 8.0, 25, seed)
        per['strokes'] = [(c, int(n * 40)) for c, n in cl]
    # global merge to PAL_TARGET colours: repeatedly merge the closest pair (Lab distance,
    # nudged by support so small accents survive longer than ramp neighbours of equal
    # distance); the merged colour is the representative of the better supported one.
    items = [dict(c=c, n=n, mats={name}) for name, cl in per.items() for c, n in cl]
    def coat_count():
        return sum(1 for it in items if it['mats'] == {'coat'} or ('coat' in it['mats'] and srgb_to_lab(it['c'][None].astype(np.float32))[0, 0] < 45))
    while True:
        labs = np.array([srgb_to_lab(it['c'][None].astype(np.float32))[0] for it in items])
        n = np.array([it['n'] for it in items], float)
        d = np.linalg.norm(labs[:, None] - labs[None], axis=2)
        cost = d * (np.minimum(n[:, None], n[None]) / 2000.0) ** 0.12
        coat = np.array(['coat' in it['mats'] and labs[k, 0] < 45 for k, it in enumerate(items)])
        if coat.sum() <= COAT_MIN:
            cost[np.ix_(coat, coat)] = 1e9
        np.fill_diagonal(cost, 1e9)
        i, j = np.unravel_index(cost.argmin(), cost.shape)
        if len(items) <= PAL_TARGET and d[i, j] >= GLOBAL_MERGE:
            break
        if cost[i, j] >= 1e9:
            break
        if n[j] > n[i]:
            i, j = j, i
        items[i]['n'] += items[j]['n']; items[i]['mats'] |= items[j]['mats']
        items.pop(j)
    pal = np.array([it['c'] for it in items], np.uint8)
    L = srgb_to_lab(pal.astype(np.float32))[:, 0]
    ramps = {name: sorted([k for k, it in enumerate(items) if name in it['mats']], key=lambda k: L[k]) for name in per}
    return pal, ramps, mat, names


def save_palette(pal, ramps, path_list, path_ramps):
    # order the list material by material (ramps dark to light), each colour once
    order, seen = [], set()
    for name in sorted(ramps, key=lambda n: (n in ('logo', 'other'), n)):
        for j in ramps[name]:
            if j not in seen:
                seen.add(j); order.append(j)
    json.dump([hexs(pal[j]) for j in order], open(path_list, 'w'), indent=0)
    json.dump({name: [hexs(pal[j]) for j in r] for name, r in ramps.items()}, open(path_ramps, 'w'), indent=1)
    return pal[order]


def run(force=False):
    from grid import run as grid_run
    p = os.path.join(CACHE, 'palette.npz')
    if os.path.exists(p) and not force:
        z = np.load(p, allow_pickle=True)
        return z['pal'], z['ramps'].item()
    a = load_src()
    XB, YB, I, J = grid_run()
    pal, ramps, mat, names = build(a, I, J)
    pal = save_palette(pal, ramps, os.path.join(OUT, 'palette.json'), os.path.join(OUT, 'palette_ramps.json'))
    # re-index ramps against the ordered list
    hx = [hexs(c) for c in pal]
    rr = json.load(open(os.path.join(OUT, 'palette_ramps.json')))
    ramps = {n: [hx.index(h) for h in r] for n, r in rr.items()}
    np.savez(p, pal=pal, ramps=np.array(ramps, dtype=object))
    return pal, ramps


if __name__ == '__main__':
    pal, ramps = run(force=True)
    print('palette', len(pal))
    for n, r in ramps.items():
        print('%-9s %2d  %s' % (n, len(r), ' '.join(hexs(pal[j]) for j in r)))
