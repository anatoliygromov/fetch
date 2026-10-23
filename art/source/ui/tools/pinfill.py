import sys, os, numpy as np
from PIL import Image
from scipy import ndimage
D = sys.argv[1]; tot = 0
for f in os.listdir(D):
    if not f.endswith('.png'): continue
    a = np.array(Image.open(f'{D}/{f}').convert('RGBA')); op = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op; hl, hn = ndimage.label(holes)
    for i in range(1, hn + 1):
        m = hl == i
        if m.sum() > 2: continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols = a[ring][:, :3]; vals, cnt = np.unique(cols, axis=0, return_counts=True)
        # the outline is the darkest common neighbour: prefer dark
        lum = vals.astype(float) @ [0.299, 0.587, 0.114]; best = vals[np.argmin(lum - cnt * 8)]
        a[m, :3] = best; a[m, 3] = 255; tot += int(m.sum())
    Image.fromarray(a).save(f'{D}/{f}')
print('filled', tot, 'px')
