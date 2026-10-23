"""Blotch clean (art/freefix): recolour the blotches tools/asset_qa.py's blotch_check finds, without blurring.
A blotch = a patch of 2-24 px of one colour (8-connected) whose 4-neighbour ring is all opaque, at least 80 % one
other colour, and that colour is near (RGB distance < TOL, default 45, the check's limit). Not a blotch: a drawn 1 px
line (1 px thick and 4 px or longer: a seam, a panel line). The patch takes the ring's colour. Silhouette edge pixels
are never changed (a patch touching the silhouette has transparency in its ring and is skipped), alpha is never
changed, no new colours appear (the ring colour is already in the file). Repeats until nothing changes (max 4 passes).
--wrap: the art tiles sideways (ground strips): the left and right columns are joins and stay as they are.
--keep x0,y0,x1,y1 (repeatable): leave this box alone (a face, a lamp, a sign drawn on purpose).
--border: pixels on the image border may change too (art cut by the frame: a door's sill on the ground line).

  python3 -I tools/blotch_clean.py src.png dst.png [--tol 45] [--wrap] [--keep 10,4,20,12]"""
import sys, os, argparse, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asset_qa import label, keys, edge_mask

def blotches(rgb, a, tol=45.0, protect=None):
    """[(mask, ring colour key)] for every blotch, as asset_qa.blotch_check counts them"""
    key = keys(rgb.astype(int), a); out = []
    for k in np.unique(key[a]):
        lab, c = label(key == k, True)
        if not c: continue
        sizes = np.bincount(lab.ravel())
        for i in range(1, c + 1):
            if not (2 <= sizes[i] <= 24): continue
            mm = lab == i
            ys, xs = np.nonzero(mm); bh, bw = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
            if min(bh, bw) == 1 and max(bh, bw) >= 4: continue          # a drawn 1 px line
            pm = np.pad(mm, 1)
            ring = (pm[:-2, 1:-1] | pm[2:, 1:-1] | pm[1:-1, :-2] | pm[1:-1, 2:]) & ~mm
            rk = key[ring]
            if (rk < 0).any(): continue
            vals, cnt = np.unique(rk, return_counts=True)
            if cnt.max() / cnt.sum() < 0.8: continue
            o = int(vals[cnt.argmax()])
            d = np.sqrt(sum((((o >> s) & 255) - ((int(k) >> s) & 255)) ** 2 for s in (16, 8, 0)))
            if d < tol and not (protect is not None and (mm & protect).any()): out.append((mm, o))
    return out

def clean(rgb, a, tol=45.0, wrap=False, keep=(), passes=4, border=False):
    rgb = rgb.copy(); h, w = a.shape
    protect = edge_mask(a)
    if border:                                                         # the image border is not a silhouette edge here
        pa = np.pad(a, 1, mode="edge")
        protect = a & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
    if wrap: protect[:, 0] = protect[:, -1] = True
    for x0, y0, x1, y1 in keep: protect[y0:y1 + 1, x0:x1 + 1] = True
    total, n0 = 0, None
    for _ in range(passes):
        bl = blotches(rgb, a, tol, protect)
        if n0 is None: n0 = len(bl)
        if not bl: break
        for mm, o in bl:
            rgb[mm] = ((o >> 16) & 255, (o >> 8) & 255, o & 255); total += int(mm.sum())
    return rgb, total, n0 or 0, len(blotches(rgb, a, tol, protect))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--tol", type=float, default=45); ap.add_argument("--wrap", action="store_true")
    ap.add_argument("--border", action="store_true", help="patches on the image border may change (art cut by the frame, e.g. a door standing on the ground line)")
    ap.add_argument("--keep", action="append", default=[], help="x0,y0,x1,y1: a box left alone")
    o = ap.parse_args()
    im = np.array(Image.open(o.src).convert("RGBA"))
    a = im[..., 3] > 127
    cols0 = len(np.unique(keys(im[..., :3].astype(int), a)[a]))
    rgb, n, b0, b1 = clean(im[..., :3], a, o.tol, o.wrap, [tuple(int(v) for v in k.split(",")) for k in o.keep], border=o.border)
    im[..., :3] = rgb
    Image.fromarray(im).save(o.dst)
    cols1 = len(np.unique(keys(rgb.astype(int), a)[a]))
    print(f"{o.src.split('/')[-1]:24} blotches {b0} -> {b1}  colours {cols0} -> {cols1}  changed {n} px")
