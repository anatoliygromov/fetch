# The passing traffic on the road and the promenade bikes (riverwalk/art/scene/car1-5.png, cyclist1-2.png).
#   * cars: source_scenery/cars_spritecook.png is one SpriteCook sheet of cars (asset 050dc075); each car is cut
#     out by its connected silhouette, left to right, top to bottom
#   * cyclists: SpriteCook draws them about 3x too big and on no pixel grid, so each 3 x 3 block becomes one pixel
#     (the darkest pixel where the block holds outline, otherwise the median), then palette + despeckle
#   * the cars face left in the files and the game flips them for traffic going right; the cyclists face right
#     and the game flips them for bikes going left
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

# The near lane's traffic at its perspective size (preview/art, 6 Oct 2026): the road is closer to the camera than
# the promenade, so its cars and cyclists are drawn bigger than Mia and Pepper (Mia 60 px is about 1.35 m).
# One SpriteCook render per car (1x, 157-218 px long), lengthened by repeating single body columns between the
# wheels (spread out, each once), so 190-235 px; the van and the hatchback were drawn facing right and are
# mirrored (every car file faces left; the game flips them for traffic going right). road_car5 is the Volvo in
# silver (its blue body shades turned grey). See-through window glass is filled; the taxi's sign is stored
# mirrored so it reads right in the game. The cyclists (150 px renders on a 2x grid) are halved, 73 x 75,
# facing right. The promenade bikes keep cyclist1.png.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_town_art import half, trim
def load(n):
    a = np.array(Image.open(os.path.join(SRC, n + '_spritecook.png')).convert('RGBA'))
    return trim(a)
def lengthen(a, n):
    W = a.shape[1]
    cols = sorted(int(W * 0.38 + i * (W * 0.26) / max(1, n - 1)) for i in range(n))
    out, prev = [], 0
    for c in cols:
        out.append(a[:, prev:c + 1]); out.append(a[:, c:c + 1]); prev = c + 1
    out.append(a[:, prev:])
    return np.concatenate(out, axis=1)
def silver(a):
    o = a.copy()
    rgb = o[..., :3].astype(int)
    blue = (o[..., 3] > 0) & (rgb[..., 2] > rgb[..., 0] + 12) & (rgb[..., 2] > rgb[..., 1] + 4)
    L = (rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11)
    g = np.clip(L * 1.9 + 40, 0, 235).astype(np.uint8)
    for c in range(3): o[..., c][blue] = (g[blue] + (c == 2) * 6).clip(0, 255)
    return o
def glass(a):
    # windows the render left see-through (a checker of transparent pixels): the holes inside the silhouette take
    # the colour of the glass pixels around them
    on = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(on) & ~on
    if holes.any():
        ring = ndimage.binary_dilation(holes) & on
        c = np.median(a[ring][:, :3], axis=0).astype(np.uint8)
        a = a.copy(); a[holes, :3] = c; a[holes, 3] = 255
    return a
def unmirror_sign(a):
    # the taxi's roof sign: the game shows the car mirrored (it drives right), so the sign's letters are stored
    # mirrored, to read the right way round on screen
    on = a[..., 3] > 0
    widths = on.sum(1)
    rows = [y for y in range(a.shape[0]) if 0 < widths[y] < a.shape[1] * 0.3]
    r1 = 0
    while r1 < len(rows) and rows[r1] == r1: r1 += 1
    if r1 == 0: return a
    xs = np.nonzero(on[:r1].any(0))[0]
    a = a.copy(); a[:r1, xs.min():xs.max() + 1] = a[:r1, xs.min():xs.max() + 1][:, ::-1]
    return a
ROAD = [('rc_volvo', False, 16), ('rc_van', True, 32), ('rc_taxi', False, 24), ('rc_hatch', True, 24)]
for k, (n, mirror, extra) in enumerate(ROAD):
    a = glass(load(n))
    if mirror: a = a[:, ::-1]
    if n == 'rc_taxi': a = unmirror_sign(a)
    Image.fromarray(lengthen(a, extra)).save(tmp)
    o = clean(tmp, 16)
    if n == 'rc_hatch':                                           # its windows came with a baked-in checker of two
        top = o[:32]                                              # greys: made one glass grey
        L = top[..., :3].astype(int).sum(2)
        lt = (top[..., 3] > 0) & (L > 520) & (top[..., 2].astype(int) > top[..., 0].astype(int))
        if lt.any():
            vals, cnt = np.unique(top[lt][:, :3], axis=0, return_counts=True); light = vals[np.argmax(cnt)]
            near = (top[..., 3] > 0) & (np.abs(top[..., :3].astype(int) - light).sum(2) == 0)
            mid = (top[..., 3] > 0) & (L > 400) & (L <= 520) & (top[..., 2].astype(int) > top[..., 0].astype(int))
            vals, cnt = np.unique(top[mid][:, :3], axis=0, return_counts=True)
            if len(vals): top[near, :3] = vals[np.argmax(cnt)]
    Image.fromarray(o).save(os.path.join(OUT, 'road_car%d.png' % (k + 1))); print('road_car%d' % (k + 1), o.shape[1], 'x', o.shape[0])
    if k == 0:
        o5 = silver(o)
        Image.fromarray(o5).save(os.path.join(OUT, 'road_car5.png')); print('road_car5', o5.shape[1], 'x', o5.shape[0])
for k, n in enumerate(['rc_cyclist3', 'rc_cyclist2']):
    Image.fromarray(half(load(n))).save(tmp)
    o = clean(tmp, 14)
    Image.fromarray(o).save(os.path.join(OUT, 'road_cyclist%d.png' % (k + 1))); print('road_cyclist%d' % (k + 1), o.shape[1], 'x', o.shape[0])
os.remove(tmp)
