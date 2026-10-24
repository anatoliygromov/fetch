"""PEPPER track: final run. Writes the output contract into out/.

out/pepper_region.png   320 x 240 RGBA, Pepper's cells opaque, the rest transparent
out/pepper_mask.png     320 x 240 L, 255 on the cells this track owns
out/pepper_palette.json the palette used (hex)
out/cmp_*.png           10x original | result per detail
out/metrics.json        every gate number of the final run
"""
import os, json, sys
import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter1d
import pepper_gates as G
import pepper_qa as Q
import pepper_seg as S
import grid as GR
from common import load_src

OUT = os.environ.get('PEPPER_OUT', '/home/claude/wt/rg-pepper/out')
DETAILS = dict(eye_brow=(98, 92, 132, 124), wink=(64, 100, 104, 126), nose_mouth=(66, 120, 136, 164),
               tongue=(94, 148, 130, 174), ear_left=(15, 92, 65, 172), ear_right=(112, 78, 152, 150),
               head_top=(48, 76, 120, 100), bandana_knot=(28, 160, 68, 190), bandana_folds=(56, 165, 140, 229),
               overview=(15, 75, 152, 229))


def grid_alignment(O):
    """principle 1 measured on this region: share of strong colour changes within 1 px
    of a cell border, for the uniform 320-grid and for a local refined grid (grid.py,
    bands of 4 cells, lines moved up to 3 px)."""
    a = load_src()
    gx, gy = GR.grad(a)
    H, W = a.shape[:2]
    Of = np.zeros((H, W), bool)
    x0, y0, x1, y1 = S.BOX
    Of[y0:y1, x0:x1] = O
    pkx = (gx == maximum_filter1d(gx, 5, axis=1)) & (gx > 40) & Of[:, :-1]
    pky = (gy == maximum_filter1d(gy, 5, axis=0)) & (gy > 40) & Of[:-1]

    def frac(XB, YB):
        ok = tot = 0
        ys, xs = np.nonzero(pkx)
        for y, x in zip(ys, xs):
            tot += 1; ok += np.min(np.abs(XB[y] - (x + 1))) <= 1
        ys, xs = np.nonzero(pky)
        for y, x in zip(ys, xs):
            tot += 1; ok += np.min(np.abs(YB[x] - (y + 1))) <= 1
        return ok / max(tot, 1)
    ux = np.round(np.arange(1, 320) * W / 320.0); uy = np.round(np.arange(1, 240) * H / 240.0)
    uni = frac(np.tile(ux, (H, 1)), np.tile(uy, (W, 1)))
    GR.BAND = 4
    _, _, Xr, Yc = GR.build(a, True, 3)
    ref = frac(Xr, Yc)
    return round(float(uni), 4), round(float(ref), 4)


def main(tag='final'):
    m, rgb, alpha, info = G.run(tag)
    os.makedirs(OUT, exist_ok=True)
    G.PR.save_rgba(rgb, alpha, os.path.join(OUT, 'pepper_region.png'))
    Image.fromarray((alpha * 255).astype(np.uint8), 'L').save(os.path.join(OUT, 'pepper_mask.png'))
    used = sorted(set(int(c) for c in np.unique(info['idx'][info['idx'] >= 0])),
                  key=lambda c: S.srgb_to_lab(info['pal'][c:c + 1])[0, 0])
    pal = ['#%02x%02x%02x' % tuple(int(v) for v in info['pal'][c]) for c in used]
    json.dump(pal, open(os.path.join(OUT, 'pepper_palette.json'), 'w'), indent=1)
    for k, b in DETAILS.items():
        Q.compare(rgb, alpha, b, 5 if k == 'overview' else 10, os.path.join(OUT, 'cmp_%s.png' % k))
    uni, ref = grid_alignment(info['O'])
    m['grid_alignment'] = dict(uniform_320=uni, local_refined=ref)
    ys, xs = np.nonzero(alpha)
    m['extent_cells'] = dict(x=[int(xs.min()), int(xs.max())], y=[int(ys.min()), int(ys.max())])
    m['palette_size'] = len(pal)
    json.dump(m, open(os.path.join(OUT, 'metrics.json'), 'w'), indent=1)
    print(json.dumps(m, indent=1))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'final')
