#!/usr/bin/env python3
"""traffic2_board.py: board and review images for the traffic 2 cars (5 Nov). The game's --test shots 20-24
(riverwalk/tests.lua; 640 x 480 window = the 320 x 240 canvas at exactly 2x) are taken 1:1 by one pixel per 2 x 2
block (integer, no averaging); the in-game frames at 3x in colour | greyscale (Rec.601), a before | after, each car
at 4x.   python3 -I tools/traffic2_board.py AFTER_DIR BEFORE_DIR"""
import sys
import numpy as np
from PIL import Image
D = 'docs/review/05nov/rw-traffic2'


def one(p): return Image.fromarray(np.array(Image.open(p).convert('RGB'))[::2, ::2])


def grey(im):
    l = (np.array(im).astype(float) @ [0.299, 0.587, 0.114]).round().clip(0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([l, l, l]))


def pair(a, b, k=3, gap=3):
    W, H = a.size; c = Image.new('RGB', (W * 2 + gap, H), (30, 32, 38)); c.paste(a, (0, 0)); c.paste(b, (W + gap, 0))
    return c.resize((c.width * k, c.height * k), Image.NEAREST)


if __name__ == '__main__':
    A, B = sys.argv[1], sys.argv[2]
    shots = (('24_traffic_van', 'van'), ('23_traffic_taxi', 'taxi'), ('22_traffic_crawl', 'estate'))
    rows = []
    for n, lab in shots:
        a, b = one(f'{A}/{n}.png'), one(f'{B}/{n}.png')
        a.save(f'{D}/ingame_{n}_1x.png'); b.save(f'{D}/before_{n}_1x.png')
        pair(a, grey(a)).save(f'{D}/board/rwtraffic2_road_{lab}_3x.png')
        rows.append(pair(b, a, k=1, gap=4))
    c = Image.new('RGB', (rows[0].width, sum(r.height + 4 for r in rows)), (30, 32, 38)); y = 0
    for r in rows: c.paste(r, (0, y)); y += r.height + 4
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(f'{D}/board/rwtraffic2_before_after_3x.png')
    for nm in ('road_car2', 'road_car3', 'road_car5'):
        im = Image.open(f'riverwalk/art/scene/{nm}.png').convert('RGBA'); bg = Image.new('RGBA', im.size, (140, 170, 200, 255))
        bg.alpha_composite(im); bg.resize((im.width * 4, im.height * 4), Image.NEAREST).save(f'{D}/board/{nm}_4x.png')
    print('board images in', D + '/board')
