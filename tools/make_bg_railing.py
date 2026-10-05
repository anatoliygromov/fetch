# Builds the decorative (background) railing from the SpriteCook tube railing
# (source_scenery/railing_bg_spritecook.png, asset 7d30bc38-449b-460d-ba0a-92d324452723, 175x30 once cropped):
# an open railing (two tube rails on slim posts, no balusters), so it never looks like the obstacle fence.
# Its shades are mapped onto the lamp post's own palette (dark to light), so it belongs with the other decoration;
# the game then fades it like the lamps. Written in three pieces for tiling:
#   rail_bg_left.png  the left post (columns 0-4)
#   rail_bg_unit.png  a span and the middle post (columns 5-88), repeated
#   rail_bg_end.png   the last span and the right post (columns 89-174)
import os, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = np.array(Image.open(os.path.join(ROOT, 'source_scenery', 'railing_bg_spritecook.png')).convert('RGBA'))
ys, xs = np.nonzero(a[..., 3]); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
L = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
LAMP = {3: (15, 21, 40), 4: (49, 64, 88), 5: (53, 69, 95), 6: (53, 69, 95), 7: (69, 88, 112), 8: (88, 109, 134)}
out = np.zeros_like(a)
op = a[..., 3] > 0
band = np.clip((L // 25).astype(int), 3, 8)
for k, c in LAMP.items():
    m = op & (band == k); out[m, :3] = c; out[m, 3] = 255
D = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
Image.fromarray(out[:, :5]).save(os.path.join(D, 'rail_bg_left.png'))
Image.fromarray(out[:, 5:89]).save(os.path.join(D, 'rail_bg_unit.png'))
Image.fromarray(out[:, 89:]).save(os.path.join(D, 'rail_bg_end.png'))
print('background railing', out.shape[1], 'x', out.shape[0])
