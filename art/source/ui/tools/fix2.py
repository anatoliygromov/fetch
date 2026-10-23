# review fixes on the clean pieces: the magenta-born maroon (121,13,42) becomes its neighbours' colour; the dark
# (not won) medals lifted so they read on the dark panel; Pepper's HUD head gets a 1 px cream rim (a variant)
import os, numpy as np
from PIL import Image
from scipy import ndimage
C = '/tmp/claude-0/ui/kit/clean'
FR = np.array([121, 13, 42]); n_fix = 0
for f in os.listdir(C):
    if not f.endswith('.png') or f.startswith('pepper'): continue
    a = np.array(Image.open(f'{C}/{f}').convert('RGBA')); op = a[..., 3] > 0
    m = op & (np.abs(a[..., :3].astype(int) - FR).sum(-1) < 30)
    for y, x in zip(*np.nonzero(m)):
        nb = [tuple(a[yy, xx, :3]) for yy in range(max(0, y-1), min(a.shape[0], y+2)) for xx in range(max(0, x-1), min(a.shape[1], x+2))
              if (yy, xx) != (y, x) and a[yy, xx, 3] and not m[yy, xx]]
        if nb:
            v, c = np.unique(np.array(nb), axis=0, return_counts=True); a[y, x, :3] = v[c.argmax()]; n_fix += 1
    Image.fromarray(a).save(f'{C}/{f}')
print('maroon fixed', n_fix)
for n in ['medal_nohit_dark', 'medal_bones_dark', 'medal_par_dark']:
    a = np.array(Image.open(f'{C}/{n}.png').convert('RGBA')); op = a[..., 3] > 0
    rgb = a[..., :3].astype(float); lum = rgb @ [0.299, 0.587, 0.114]
    lift = op & (lum > 30)                                # keep the outline, lift the body towards a dull bronze
    rgb[lift] = rgb[lift] * 0.45 + np.array([168, 132, 92]) * 0.55
    a[..., :3] = rgb.round().clip(0, 255).astype(np.uint8); Image.fromarray(a).save(f'{C}/{n}.png')
a = np.array(Image.open(f'{C}/pepper_head.png').convert('RGBA'))
a = np.pad(a, ((1, 1), (1, 1), (0, 0))); op = a[..., 3] > 0
ring = ndimage.binary_dilation(op, structure=np.ones((3, 3))) & ~op
a[ring] = (250, 232, 190, 255); Image.fromarray(a).save(f'{C}/pepper_head_rim.png')
