"""Helpers for blockout scripts in art/gen/blockouts/<name>.py (see docs/art_generation.md).
A blockout is a game-size frame (default 150x112, 4:3, so a Nano Banana Pro 1K render is exactly 8 image px per game
px) on flat magenta with Pepper's real sprite at 1x and grey shapes for every part of the subject at true scale.
The mask holds the subject only and is the answer key for tools/grid_cut.py."""
import json
import numpy as np
from PIL import Image, ImageDraw

RULES = json.load(open('art/gen/rules.json'))
MAGENTA = (255, 0, 255, 255)


def pepper():
    p = RULES['pepper']
    im = Image.fromarray(np.array(Image.open(p['file']).convert('RGBA'))[p['cell'][1]:p['cell'][3], p['cell'][0]:p['cell'][2]])
    return im.crop(im.getbbox())


def frame(w=150, h=112, ground=None, pepper_x=4):
    """Canvas, its drawer, a mask and its drawer, with Pepper standing on the ground line at pepper_x."""
    ground = h - 6 if ground is None else ground
    c = Image.new('RGBA', (w, h), MAGENTA); m = Image.new('L', (w, h), 0)
    p = pepper(); c.alpha_composite(p, (pepper_x, ground - p.height))
    return c, ImageDraw.Draw(c), m, ImageDraw.Draw(m), ground


def save(name, c, m, meta):
    c.save(f'art/gen/blockouts/{name}.png'); m.save(f'art/gen/blockouts/{name}_mask.png')
    json.dump(meta, open(f'art/gen/blockouts/{name}.json', 'w'), indent=1)
    bb = m.getbbox(); print(name, 'frame', c.size, 'subject', bb[2] - bb[0], 'x', bb[3] - bb[1])
