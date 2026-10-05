# The passing traffic on the road and the promenade bikes (riverwalk/art/scene/car1-5.png, cyclist1-2.png).
#   * cars: source_scenery/cars_spritecook.png is one SpriteCook sheet of cars (asset 050dc075); each car is cut
#     out by its connected silhouette, left to right, top to bottom
#   * cyclists: SpriteCook draws them about 3x too big and on no pixel grid, so each 3 x 3 block becomes one pixel
#     (the darkest pixel where the block holds outline, otherwise the median), then palette + despeckle
#   * all of them face left in the files; the game flips them for traffic going right
import os, sys, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_props import clean
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, 'source_scenery'), os.path.join(ROOT, 'riverwalk', 'art', 'scene')
def down3(a):
    a = a.astype(int); H, W = a.shape[:2]; k = 3
    p = np.zeros(((H + 2) // 3 * 3, (W + 2) // 3 * 3, 4), int); p[:H, :W] = a
    out = np.zeros((p.shape[0] // 3, p.shape[1] // 3, 4), np.uint8)
    for y in range(out.shape[0]):
        for x in range(out.shape[1]):
            blk = p[3 * y:3 * y + 3, 3 * x:3 * x + 3].reshape(-1, 4); on = blk[blk[:, 3] > 20]
            if len(on) < 4: continue
            L = on[:, :3].sum(1)
            c = on[np.argmin(L)] if (L < 120).sum() >= 2 else np.median(on, axis=0)
            out[y, x, :3] = c[:3]; out[y, x, 3] = 255
    ys, xs = np.where(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
tmp = os.path.join(OUT, '_tmp.png')
a = np.array(Image.open(os.path.join(SRC, 'cars_spritecook.png')).convert('RGBA'))
lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
objs = [(s, i + 1) for i, s in enumerate(ndimage.find_objects(lab)) if (s[0].stop - s[0].start) * (s[1].stop - s[1].start) > 400]
objs.sort(key=lambda o: (o[0][0].start // 30, o[0][1].start))
for k, (s, i) in enumerate(objs[:5]):
    sub = a[s].copy(); sub[lab[s] != i] = 0
    Image.fromarray(sub).save(tmp)
    o = clean(tmp, 16)
    Image.fromarray(o).save(os.path.join(OUT, 'car%d.png' % (k + 1))); print('car%d' % (k + 1), o.shape[1], 'x', o.shape[0])
for k, f in enumerate(['cyclist1_spritecook.png', 'cyclist2_spritecook.png']):
    Image.fromarray(down3(np.array(Image.open(os.path.join(SRC, f)).convert('RGBA')))).save(tmp)
    o = clean(tmp, 14)
    Image.fromarray(o).save(os.path.join(OUT, 'cyclist%d.png' % (k + 1))); print('cyclist%d' % (k + 1), o.shape[1], 'x', o.shape[0])
os.remove(tmp)
