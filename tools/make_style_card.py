#!/usr/bin/env python3
"""make_style_card.py [K]: the style card sent as image 2 with every generation job. Approved River Walk sprites
(Pepper, Mia, bench, bin, lamp post, planter; no lettered pieces) at 1x on flat magenta, standing on one line, saved at an integer K
(default 8) so the model sees the same pixel density it must draw at. Out: art/gen/style_card_riverwalk.png (+ _1x)."""
import sys
from PIL import Image

K = int(sys.argv[1]) if len(sys.argv) > 1 else 8
A = 'riverwalk/art/'
def crop(path, box=None):
    im = Image.open(path).convert('RGBA')
    if box: im = im.crop(box)
    return im.crop(im.getbbox())
parts = [crop(A + 'pepper.png', (0, 0, 60, 52)), crop(A + 'girl.png', (0, 0, 66, 66)),
         crop(A + 'scene/bin.png'), crop(A + 'scene/lamp_post.png'), crop(A + 'scene/bench.png'),
         crop(A + 'scene/planter_sq.png')]
W = sum(p.width for p in parts) + 6 * (len(parts) + 1); H = 112; G = 108
c = Image.new('RGBA', (W, H), (255, 0, 255, 255)); x = 6
for p in parts:
    c.alpha_composite(p, (x, G - p.height)); x += p.width + 6
c.convert('RGB').save('art/gen/style_card_riverwalk_1x.png')
c.convert('RGB').resize((W * K, H * K), Image.NEAREST).save('art/gen/style_card_riverwalk.png')
print('style card', W, 'x', H, 'at', K, 'x')
