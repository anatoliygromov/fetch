#!/usr/bin/env python3
"""tools/dt_props_size_sheet.py OUT.png: the dt_props_06nov pieces beside Pepper's real sprite on one ground line, at
1x (top) and 4x (below), with a 1 m (46 px) ruler. No resampling except whole-number nearest-neighbour zoom."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
R = json.load(open('art/gen/rules.json'))
S = 'riverwalk/art/scene/'
p = R['pepper']
pep = Image.open(p['file']).convert('RGBA').crop(tuple(p['cell'])); pep = pep.crop(pep.getbbox())
names = ['town_kiosk', 'town_parasol40', 'town_parasol48', 'town_parasol64', 'town_parasol96', 'town_pedestal',
         'town_stall', 'town_tub', 'town_crate_front28', 'town_crate_front32', 'town_crate_front36', 'town_sign',
         'town_shopsign']
ims = [('pepper', pep)] + [(n, Image.open(S + n + '.png').convert('RGBA')) for n in names]
gap = 8; W = sum(i.width for _, i in ims) + gap * (len(ims) + 3) + 10; Hs = max(i.height for _, i in ims)
def strip():
    c = Image.new('RGBA', (W, Hs + 4), (150, 160, 172, 255)); x = gap + 10
    d = ImageDraw.Draw(c)
    d.rectangle([2, Hs + 3 - 46, 4, Hs + 2], fill=(200, 40, 40, 255))          # the 1 m ruler (46 px)
    for _, im in ims:
        c.alpha_composite(im, (x, Hs + 2 - im.height)); x += im.width + gap
    d.line([0, Hs + 2, W, Hs + 2], fill=(70, 70, 80, 255))
    return c
s1 = strip(); s4 = s1.resize((s1.width * 4, s1.height * 4), Image.NEAREST)
out = Image.new('RGBA', (s4.width, s1.height + 30 + s4.height + 40), (40, 42, 48, 255))
d = ImageDraw.Draw(out)
d.text((6, 4), "1x: Pepper's real sprite (left) and every dt_props_06nov piece on one ground line; red bar = 1 m (46 px)", fill=(230, 230, 236, 255))
out.alpha_composite(s1, (0, 18))
y4 = s1.height + 30
d.text((6, y4 - 10), "4x (nearest neighbour)", fill=(230, 230, 236, 255))
out.alpha_composite(s4, (0, y4 + 4))
x = (gap + 10) * 4
for n, im in ims:
    d.text((x, out.height - 34), n.replace('town_', ''), fill=(230, 230, 236, 255))
    d.text((x, out.height - 20), f"{im.width}x{im.height}", fill=(170, 170, 180, 255))
    x += (im.width + gap) * 4
out.save(sys.argv[1]); print(sys.argv[1], out.size)
