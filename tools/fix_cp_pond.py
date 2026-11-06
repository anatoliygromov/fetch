#!/usr/bin/env python3
"""fix_cp_pond.py: the stepping stone cut at the water (art/cp-pond-06nov, 6 Nov 2026, 0 credits, hand fix by rule).

  python3 -I tools/fix_cp_pond.py      -> riverwalk/art/scene/park_stone.png, art/source/park_stone/ (edits.json, .aseprite)

The owner (6 Nov, the tall pond): "this thing looks weird". The stone filled its whole 52 px box down to the bottom of
the world and the pond was drawn half see-through over its lower part: a grey glass pillar standing in the water. A
stepping stone is a rock whose top sticks out of the water. Every STONE box (City Park and City Park tall, the pond
and the creek) has its top 20 px over the water's surface (box y0 332, water 352; flat level 188 and 208).

The rule, on the 26 x 55 column made by tools/polish_cp_props.py (kept as art/source/park_stone/park_stone_column.png):
  1. keep rows 0-29: the rounded top and the rock face down to the art's own wet band (row 29, where its grey starts)
  2. splice out the 10 straight rows of the sides that join best (the same band cost as polish_cp_props.py)
  3. add one ink row under it: the waterline, the same row as the pond's own dark edge line (y 351)
  4. hand rule for the splice's specks: a lone pixel (no 8-neighbour of its colour) not touching the outline takes
     the colour most of its 8 neighbours have (each pixel recorded in edits.json; the rim's lone pixels are detail)
The rock is then 26 x 21 (the box's 24 + its outline each side; its top row the outline over the box's top).
scene.lua draws it standing on the water, and only there a dark reflection wobbling under it; the box is unchanged.
"""
import os, sys, json, shutil
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'park_stone'
SRC = os.path.join(ROOT, 'art/source', NAME)
COLUMN = os.path.join(SRC, NAME + '_column.png')
OUT = os.path.join(ROOT, 'riverwalk/art/scene', NAME + '.png')
KEEP, SPLICE, LO, HI = 30, 10, 8, 19


def band_cost(a, al, i, k):
    p, q, pa, qa = a[i - 1], a[i + k], al[i - 1], al[i + k]
    both = pa & qa
    d = np.sqrt(((p.astype(int) - q.astype(int)) ** 2).sum(-1))[both].sum()
    return d + 400 * (pa ^ qa).sum()


def main():
    if not os.path.exists(COLUMN):                       # the column as polish_cp_props.py made it (once)
        shutil.copyfile(OUT, COLUMN)
    im = np.array(Image.open(COLUMN).convert('RGBA'))
    assert im.shape[:2] == (55, 26), im.shape
    rgb, al = im[..., :3].copy(), im[..., 3] > 127
    rgb, al = rgb[:KEEP], al[:KEEP]
    at = min(range(LO, HI + 1), key=lambda i: band_cost(rgb, al, i, SPLICE))
    keep = np.r_[0:at, at + SPLICE:KEEP]
    rgb, al = rgb[keep], al[keep]
    cols = np.unique(im[..., :3][im[..., 3] > 127], axis=0)
    ink = cols[(cols.astype(float) @ [0.299, 0.587, 0.114]).argmin()]
    rgb = np.concatenate([rgb, np.tile(ink, (1, rgb.shape[1], 1))]); al = np.concatenate([al, np.ones((1, al.shape[1]), bool)])
    hand = []
    H, W = al.shape
    key = (rgb[..., 0].astype(int) << 16) | (rgb[..., 1].astype(int) << 8) | rgb[..., 2]
    for y in range(H):
        for x in range(W):
            if not al[y, x]: continue
            nb = [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and 0 <= y + dy < H and 0 <= x + dx < W]
            if len(nb) < 8 or not all(al[q] for q in nb): continue
            ks = [key[q] for q in nb]
            if key[y, x] in ks or (ink == rgb[y, x]).all(): continue      # (not lone, or the outline)
            if any((rgb[q] == ink).all() for q in nb): continue          # (on the rim: detail, kept)
            vals, cnt = np.unique(ks, return_counts=True); k = int(vals[cnt.argmax()])
            new = np.array([(k >> 16) & 255, (k >> 8) & 255, k & 255], np.uint8)
            hand.append({'x': x, 'y': y, 'from': '%02x%02x%02x' % tuple(int(v) for v in rgb[y, x]), 'to': '%02x%02x%02x' % tuple(int(v) for v in new),
                         'why': 'a lone speck inside the rock face after the splice: its neighbours\' colour'})
            rgb[y, x] = new; key[y, x] = k
    out = np.dstack([rgb, np.where(al, 255, 0)]).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(OUT)
    Image.fromarray(out, 'RGBA').save(os.path.join(SRC, NAME + '.png'))
    aseprite_io.write(os.path.join(SRC, NAME + '.aseprite'), [out], layer=NAME)
    ed = os.path.join(SRC, 'edits.json')
    log = json.load(open(ed))
    log['pond'] = {'date': '2026-11-06', 'branch': 'art/cp-pond-06nov', 'source': 'art/source/park_stone/park_stone_column.png',
                   'why': 'the owner: "this thing looks weird" (a grey pillar in the pond). A stepping stone is the top of a rock '
                          'standing out of the water: the art ends at the waterline, the box (24 x 52) is unchanged',
                   'ops': [{'crop_rows': [0, KEEP]}, {'splice_rows': {'removed': [int(at), int(at + SPLICE - 1)], 'of_the_size_then': True}},
                           {'add_row': {'at': int(out.shape[0] - 1), 'colour': '%02x%02x%02x' % tuple(int(v) for v in ink),
                                        'why': 'the waterline: the pond\'s dark edge row (y 351)'}}],
                   'hand': hand,
                   'size': [int(out.shape[1]), int(out.shape[0])],
                   'colours': int(len(np.unique(out[..., :3][out[..., 3] > 0], axis=0)))}
    json.dump(log, open(ed, 'w'), indent=1)
    print(f'{NAME}: 26 x 55 -> {out.shape[1]} x {out.shape[0]}, rows {at}-{at + SPLICE - 1} spliced out, '
          f'{len(hand)} specks by hand rule, {log["pond"]["colours"]} colours')


if __name__ == '__main__':
    main()
