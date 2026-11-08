#!/usr/bin/env python3
"""rt_concept_assets.py: the Rooftops main concept (rt_hotel_concept_a) cut into separate assets, 1 game pixel each
(8 Nov 2026, owner 13:42: "this is our main concept art. we need to cut it into separate assets").

Source: art/source/rt_lockfill/final.png, the concept on the game's 320 x 240 grid with the parts Pepper, the goose,
the bones and the tile piles covered already completed from the concept itself (the lock-and-complete pilot).
Nothing is redrawn or recoloured. Each asset is a box from that picture with
  * cut out: what is not the piece becomes transparent (sky; the roof tiles behind a chimney or dormer);
  * completed (roofs only): tiles a chimney or dormer hid continue their own row (the roof's 23 px tile period), and
    every completed pixel is counted.
Writes art/source/rt_assets/<name>.png, report.json (box, size, colours, cut-out and completed pixels) and
sheet.png (every asset at 4x on a checker, labelled)."""
import json, os
import numpy as np
from PIL import Image, ImageDraw

SRC = 'art/source/rt_lockfill/final.png'
OUT = 'art/source/rt_assets'
A = np.asarray(Image.open(SRC).convert('RGB')).astype(np.uint8)
I = A.astype(int)
R, G, B = I[..., 0], I[..., 1], I[..., 2]
SKY = (R > 225) & (G > 185) & (B > 130) & (R - B < 110)              # the pale evening sky and its bands
FAR = (R > 175) & (G > 130) & (B > 100) & (R - B < 75) & ~SKY        # the pale far town behind the roofs
TILE = (R > G + 35) & (R - B > 35) & (R > 95)                         # clay reds, lit and shaded
TILE_DK = (R > G + 25) & (G < 60)                                     # the tiles' dark joints


def box_mask(x0, y0, x1, y1):
    m = np.zeros(A.shape[:2], bool); m[y0:y1, x0:x1] = True; return m


# name: (layer, box x0 y0 x1 y1 (exclusive), how the piece is told from what is behind it, note)
ASSETS = {
    'spire':          ('far',  (60, 10, 78, 62), 'not_sky_far', 'the church spire over the far town; its foot is behind the roofs'),
    'chimney_small':  ('back', (4, 50, 22, 80),  'not_sky_tile', 'the plain stucco stack, left'),
    'chimney_pots3':  ('back', (82, 40, 104, 80), 'not_sky_tile_body', 'the stack with three clay pots'),
    'chimney_big':    ('back', (227, 31, 269, 88), 'not_sky_tile_body', 'the big stack with three pots, on the coping'),
    'dormer_small':   ('back', (110, 66, 132, 87), 'poly', 'the little gable dormer in the left roof'),
    'gable_end':      ('back', (157, 44, 180, 87), 'poly', 'the right roof\'s gable end with its slit window'),
    'roof_left':      ('back', (0, 58, 160, 87), 'roof', 'the left roof: ridge, tile courses (chimneys and dormer completed)'),
    'roof_right':     ('back', (162, 43, 320, 87), 'roof', 'the right roof: ridge caps, tile courses (big chimney completed)'),
    'coping':         ('play', (0, 87, 320, 101), 'all', 'the parapet Pepper walks: stone blocks and the wall shadow under them'),
    'ledge':          ('play', (96, 136, 160, 148), 'all', 'the lower ledge between the skylights (one block run)'),
    'facade_storey':  ('back', (100, 101, 320, 136), 'all', 'the plaster storey with its row of windows, under the coping'),
    'window':         ('back', (205, 113, 227, 136), 'all', 'the upper window (its foot is the ledge)'),
    'window_sill':    ('back', (55, 197, 81, 232), 'window_sill', 'the lower window with its sill'),
    'skylight_left':  ('play', (1, 139, 96, 176), 'skylight', 'the glass lantern, left'),
    'skylight_right': ('play', (160, 139, 257, 176), 'skylight', 'the glass lantern, right'),
    'copper_canopy':  ('back', (143, 172, 320, 193), 'canopy', 'the hotel\'s copper canopy (runs on past the frame)'),
    'hotel_front':    ('back', (148, 192, 320, 240), 'all', 'the hotel\'s stone front: cornice, pilasters, tall windows (runs on below the frame)'),
}


def cut(name):
    layer, (x0, y0, x1, y1), how, note = ASSETS[name]
    rgb = A[y0:y1, x0:x1].copy(); h, w = rgb.shape[:2]
    sky, far, tile, tdk = (m[y0:y1, x0:x1] for m in (SKY, FAR, TILE, TILE_DK))
    done = np.zeros((h, w), bool)
    if how == 'all':
        m = np.ones((h, w), bool)
    elif how == 'not_sky_far':
        m = ~sky
    elif how in ('not_sky_tile', 'not_sky_tile_body'):
        # the stack: everything not sky; below the slab the body is a solid block, so the tiles round it go (the
        # block's columns are the slab's own span), the pots above the slab keep their clay reds
        m = ~sky
        slab_rows = [y for y in range(h) if (~sky[y] & ~tile[y]).sum() >= 0.6 * w]
        top_slab = slab_rows[0] if slab_rows else 0
        for y in range(top_slab, h):
            xs = np.nonzero(~tile[y] & ~tdk[y] & ~sky[y])[0]
            row = np.zeros(w, bool)
            if len(xs): row[xs.min():xs.max() + 1] = True
            m[y] = row
        for y in range(top_slab):                                    # above the slab: pots (clay), not the tiles of
            m[y] &= ~far[y]                                          # the roof behind if the box reaches them
    elif how == 'poly':
        # a gable: the dark frame lines are the edges; inside the outermost dark pixels of each row
        dark = (I[y0:y1, x0:x1].sum(2) < 230) & ~tile
        m = np.zeros((h, w), bool)
        for y in range(h):
            xs = np.nonzero(dark[y])[0]
            if len(xs) >= 2: m[y, xs.min():xs.max() + 1] = True
        m &= ~sky
    elif how == 'roof':
        # the roof field: tiles, their dark joints and the ridge caps; what stands in front (chimneys, dormers,
        # the gable end) is completed from the same row, one tile period (23 px) to the side
        m = ~sky & ~far
        front = ~(tile | tdk) & m
        # keep thin dark/brown tile pixels that sit inside tile runs (joints): only wide non-tile runs are fronts
        fr = np.zeros_like(front)
        for y in range(h):
            x = 0
            while x < w:
                if front[y, x]:
                    a = x
                    while x < w and front[y, x]: x += 1
                    if x - a >= 4: fr[y, a:x] = True
                else: x += 1
        for y in range(h):
            for x in np.nonzero(fr[y])[0]:
                for k in (1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6):
                    xx = x + 23 * k
                    if 0 <= xx < w and m[y, xx] and not fr[y, xx]:
                        rgb[y, x] = rgb[y, xx]; done[y, x] = True; break
        m = m | done
    elif how == 'window_sill':
        m = np.ones((h, w), bool)
        wall = (np.abs(I[y0:y1, x0:x1] - [208, 140, 77]).sum(2) < 6) | (np.abs(I[y0:y1, x0:x1] - [243, 180, 103]).sum(2) < 6)
        m &= ~wall
    elif how == 'skylight':
        blk = (rgb == [5, 5, 5]).all(2)
        m = np.zeros((h, w), bool); prev = None
        for y in range(h):
            xs = np.nonzero(blk[y])[0]
            if len(xs) >= 2 and xs.max() - xs.min() > 20: prev = (xs.min(), xs.max())
            if y >= h - 2 and prev: prev = (min(prev[0], 0), max(prev[1], w - 1))
            if prev: m[y, prev[0]:prev[1] + 1] = True
    elif how == 'canopy':
        # the copper and its dark edge lines; the plaster wall behind its sloped left end goes
        wall = (R[y0:y1, x0:x1] > 150) & (G[y0:y1, x0:x1] > 90) & (G[y0:y1, x0:x1] < 190) & (B[y0:y1, x0:x1] < 115) \
               & (R[y0:y1, x0:x1] - B[y0:y1, x0:x1] > 70)
        m = np.zeros((h, w), bool)
        for y in range(h):
            xs = np.nonzero(~wall[y])[0]
            if len(xs): m[y, xs.min():] = True
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = rgb; out[..., 3] = np.where(m, 255, 0)
    return out, {'layer': layer, 'box': [x0, y0, x1, y1], 'size': [w, h], 'note': note,
                 'colours': int(len(np.unique(rgb[m], axis=0))), 'cut_out_px': int((~m).sum()),
                 'completed_px': int(done.sum()), 'redrawn_px': 0}


def sheet(items, path, s=3):
    pad, lab = 10, 14
    rows, x, y, rh, maxw = [], pad, pad, 0, 1300
    pos = {}
    for n, a in items:
        w, h = a.shape[1] * s, a.shape[0] * s + lab
        if x + w > maxw: x = pad; y += rh + pad; rh = 0
        pos[n] = (x, y); x += w + pad; rh = max(rh, h)
    H = y + rh + pad
    im = Image.new('RGBA', (maxw, H), (40, 42, 48, 255)); d = ImageDraw.Draw(im)
    for n, a in items:
        px, py = pos[n]; h, w = a.shape[:2]
        chk = Image.new('RGBA', (w * s, h * s))
        cd = ImageDraw.Draw(chk)
        for yy in range(0, h * s, 6):
            for xx in range(0, w * s, 6):
                cd.rectangle([xx, yy, xx + 5, yy + 5], fill=(92, 96, 104, 255) if (xx // 6 + yy // 6) % 2 else (72, 76, 84, 255))
        chk.alpha_composite(Image.fromarray(a, 'RGBA').resize((w * s, h * s), Image.NEAREST))
        im.alpha_composite(chk, (px, py + lab)); d.text((px, py), f'{n} {w}x{h}', fill=(235, 235, 235, 255))
    im.convert('RGB').save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    rep, items = {'source': SRC, 'assets': {}}, []
    for n in ASSETS:
        a, info = cut(n)
        Image.fromarray(a, 'RGBA').save(f'{OUT}/{n}.png')
        rep['assets'][n] = info; items.append((n, a))
        print(f"{n:15s} {info['size']} {info['layer']:5s} colours {info['colours']:3d} cut out {info['cut_out_px']:5d} completed {info['completed_px']}")
    json.dump(rep, open(f'{OUT}/report.json', 'w'), indent=1)
    sheet(items, f'{OUT}/sheet.png')


if __name__ == '__main__':
    main()
