#!/usr/bin/env python3
"""build_animals.py: the redrawn gull and cat (25 Oct 2026, owner: the old gull "has holes and doesnt really look like a
bird", "same for cat"). The gull: wingspan about 44 px, drawn smaller than life on the owner's call ("the bird turns out
massive" at 58 px, 17:25; picked about 40 px); the cat at true scale, 16 px sitting (owner's pick).

Sources (SpriteCook, art/gen/renders/): each animal is ONE still from Pixel Engine Image at its exact game size,
animated at 1x with pixel-engine-v1.5 (no resampling anywhere; frames are only cropped, padded and aligned by whole
pixels):
  rw_gull_s_flap_sheet.png 8 frames 68 x 68, a looping wingbeat (from still rw_gull_s_a.png, 44 x 26)
  dt_cat_idle_sheet.png    8 frames 16 x 16, sitting: tail curl, ear twitch, blink
  dt_cat_leap_r1_sheet.png 8 frames 24 x 24: sit, crouch, arched back, spring, up, top, down, land
  dt_cat_run_r1_sheet.png  8 frames 24 x 24: sit, stand, gallop loop (frames 3-8)
Clean-up on these NEW frames, as for Pepper's clips (claude/spritecook-pipeline.md): every pixel snapped to the
animal's own still palette (no colour flicker), alpha to 0/255, detached specks of 1-3 px removed, enclosed holes of
1-4 px filled with their most common neighbour (the owner's "holes"), the 1 px dark outline closed
(tools/outline_complete.py; the cat's ground row left alone).
Out: riverwalk/art/gull.png (8 cells of 48 x 44) and riverwalk/art/cat.png (8 x 3 cells of 24 x 24: idle, leap, run; the
cat's feet on the cell's bottom row, the idle frames aligned to the leap's first frame)."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

R = 'art/gen/renders/'
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_palette import lab
import outline_complete


def palette_of(path):
    a = np.array(Image.open(R + path).convert('RGBA'))
    return np.unique(a[a[..., 3] > 0][:, :3], axis=0)


def snap(f, pal):
    """every pixel takes the nearest colour (Lab) of the animal's own still: the animator's drifted shades go,
    so no colour flickers between frames; one colour per pixel, nothing blended"""
    m = f[..., 3] > 0
    if m.any():
        px = f[m][:, :3].astype(float)
        idx = np.argmin(((lab(px)[:, None] - lab(pal.astype(float))[None]) ** 2).sum(2), 1)
        f[m, :3] = pal[idx]
    return f


def frames(path, fw, fh, n):
    a = np.array(Image.open(R + path).convert('RGBA'))
    return [a[:fh, i * fw:(i + 1) * fw].copy() for i in range(n)]


def clean(f):
    al = f[..., 3] >= 128
    f[..., 3] = np.where(al, 255, 0); f[~al] = 0
    lbl, n = ndimage.label(al, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(al, lbl, range(1, n + 1))
        for i, s in enumerate(sizes, 1):
            if s <= 3: f[lbl == i] = 0
    al = f[..., 3] > 0
    holes = ~al & ndimage.binary_fill_holes(al)
    lbl, n = ndimage.label(holes)
    filled = 0
    for i in range(1, n + 1):
        comp = lbl == i
        if comp.sum() > 4: continue
        ring = ndimage.binary_dilation(comp) & al
        lum = f[ring][:, :3] @ np.array([0.299, 0.587, 0.114])
        if (lum < 70).mean() >= 0.7: continue      # an outlined gap (between tail and leg): drawn on purpose
        cols, cnt = np.unique(f[ring][:, :3], axis=0, return_counts=True)
        f[comp, :3] = cols[cnt.argmax()]; f[comp, 3] = 255; filled += int(comp.sum())
    return f, filled


def shift(f, dx, dy):
    h, w = f.shape[:2]; out = np.zeros_like(f)
    ys, xs = np.nonzero(f[..., 3])
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
    assert ok.all(), 'frame content would be cut'
    out[ny, nx] = f[ys, xs]
    return out


def main():
    log = []
    # gull (smaller, owner 25 Oct 17:27): 8 frames 68 x 68 cropped by whole pixels to 48 x 44 cells
    g = frames('rw_gull_s_flap_sheet.png', 68, 68, 8)
    g = [f[18:62, 9:57].copy() for f in g]
    for f0 in frames('rw_gull_s_flap_sheet.png', 68, 68, 8):
        crop = f0.copy(); crop[18:62, 9:57] = 0
        assert not crop[..., 3].any(), 'gull frame content outside the crop'
    gp = palette_of('rw_gull_s_a.png')
    sheet = np.zeros((44, 48 * 8, 4), np.uint8)
    for i, f in enumerate(g):
        f, n = clean(snap(f, gp)); log.append(('gull', i + 1, n)); sheet[:, i * 48:(i + 1) * 48] = f
    # review 25 Oct (art/gen/reviews/animals_25oct.md), by hand: f8's 1 px see-through hole at (25,6) filled from
    # its neighbours; f6's stray foot pixel at (14,26) removed; lone pixels of the wing greys take their most common
    # neighbouring grey (mottled near wing in f2, f7, f8)
    from collections import Counter
    def nbrs(a, x, y, x0, x1):
        return [tuple(int(v) for v in a[yy, xx, :4]) for yy in range(max(0, y - 1), min(a.shape[0], y + 2))
                for xx in range(max(x0, x - 1), min(x1, x + 2)) if (yy, xx) != (y, x) and a[yy, xx, 3]]
    f = 7; x, y = f * 48 + 25, 6
    if sheet[y, x, 3] == 0:
        sheet[y, x] = Counter(nbrs(sheet, x, y, f * 48, f * 48 + 48)).most_common(1)[0][0]
    f = 5; x, y = f * 48 + 14, 26
    if sheet[y, x, 3] and len(nbrs(sheet, x, y, f * 48, f * 48 + 48)) <= 1: sheet[y, x] = 0
    GREYS = {tuple(int(v) for v in c) for c in gp if max(c) - min(c) < 24 and 60 < np.mean(c) < 235}
    for i in range(8):
        x0 = i * 48
        for y in range(44):
            for x in range(x0, x0 + 48):
                c = tuple(int(v) for v in sheet[y, x, :3])
                if sheet[y, x, 3] == 0 or c not in GREYS: continue
                nb = nbrs(sheet, x, y, x0, x0 + 48)
                if any(n[:3] == c for n in nb): continue
                g2 = [n[:3] for n in nb if n[:3] in GREYS]
                if g2: sheet[y, x, :3] = Counter(g2).most_common(1)[0][0]
    Image.fromarray(sheet).save('riverwalk/art/gull.png')
    # it flies: the 1 px dark outline closed all round (no ground row)
    outline_complete.run('riverwalk/art/gull.png', 'riverwalk/art/gull.png')
    # cat: idle padded 16 -> 24, feet on the bottom row, idle frame 1 aligned on leap frame 1
    idle = frames('dt_cat_idle_sheet.png', 16, 16, 8)
    leap = frames('dt_cat_leap_r1_sheet.png', 24, 24, 8)
    run = frames('dt_cat_run_r1_sheet.png', 24, 24, 8)
    pad = []
    for f in idle:
        c = np.zeros((24, 24, 4), np.uint8); c[8:24, 4:20] = f; pad.append(c)
    def box(f):
        ys, xs = np.nonzero(f[..., 3]); return xs.min(), xs.max(), ys.max()
    l0, i0 = box(leap[0]), box(pad[0])
    dx, dy = l0[1] - i0[1], l0[2] - i0[2]                 # right edge (the face) and feet line
    pad = [shift(f, dx, dy) for f in pad]
    for rows, name in ((pad, 'idle'), (leap, 'leap'), (run, 'run')):
        for f in rows:
            ys = np.nonzero(f[..., 3])[0]
            if name != 'leap' and ys.max() != 23: pass       # in the air only in the leap
    cp = palette_of('dt_cat_a.png')
    cat = np.zeros((72, 24 * 8, 4), np.uint8)
    for r, rows in enumerate((pad, leap, run)):
        for i, f in enumerate(rows):
            f, n = clean(snap(f, cp)); log.append(('cat', r + 1, i + 1, n))
            cat[r * 24:(r + 1) * 24, i * 24:(i + 1) * 24] = f
    # coat ticking at 16 px: a lone pixel of one of the three coat shades (no 8-neighbour of its colour) takes its most
    # common neighbouring coat shade; the eye, nose, ear pink, cream and the outline keep their single pixels
    COAT = {(186, 102, 39), (158, 85, 36), (229, 153, 70), (131, 71, 35), (212, 136, 65)}
    merged = 0
    for _ in range(2):
        key = cat[..., 0].astype(int) * 65536 + cat[..., 1].astype(int) * 256 + cat[..., 2]
        for y in range(72):
            for x in range(192):
                c = tuple(int(v) for v in cat[y, x, :3])
                if cat[y, x, 3] == 0 or c not in COAT: continue
                cy0, cx0 = (y // 24) * 24, (x // 24) * 24
                nb = [(yy, xx) for yy in range(max(cy0, y - 1), min(cy0 + 24, y + 2)) for xx in range(max(cx0, x - 1), min(cx0 + 24, x + 2))
                      if (yy, xx) != (y, x) and cat[yy, xx, 3]]
                if any(key[yy, xx] == key[y, x] for yy, xx in nb): continue
                coat = [tuple(int(v) for v in cat[yy, xx, :3]) for yy, xx in nb if tuple(int(v) for v in cat[yy, xx, :3]) in COAT]
                if coat:
                    from collections import Counter
                    cat[y, x, :3] = Counter(coat).most_common(1)[0][0]; merged += 1
    log.append(('cat coat lone merged', merged))
    # review 25 Oct, by hand: idle 2 and 7 had a black clot where the haunch is (rows 20-21, x 5-11): those two rows
    # take idle 1's haunch; four sealed 1 px pinholes take their most common neighbour
    for f in (1, 6):
        cat[20:22, f * 24 + 5:f * 24 + 12] = cat[20:22, 5:12]
    for r, f, x, y in ((2, 2, 5, 18), (2, 3, 12, 20), (2, 5, 9, 21), (1, 2, 5, 19), (1, 2, 5, 20), (1, 2, 5, 21)):
        X, Y = f * 24 + x, r * 24 + y
        if cat[Y, X, 3] == 0:
            nb = [tuple(int(v) for v in cat[yy, xx]) for yy in (Y - 1, Y, Y + 1) for xx in (X - 1, X, X + 1)
                  if (yy, xx) != (Y, X) and cat[yy, xx, 3]]
            from collections import Counter
            cat[Y, X] = Counter(nb).most_common(1)[0][0]
    Image.fromarray(cat).save('riverwalk/art/cat.png')
    # the outline closed, each frame's lowest row left alone (the paws on the ground)
    outline_complete.run('riverwalk/art/cat.png', 'riverwalk/art/cat.png', skip_bottom=True, frames=(24, 24))
    filled = [l for l in log if l[-1]]
    print('gull.png 384x44, cat.png 192x72; idle aligned by', (dx, dy), '; holes filled:', filled or 'none')


if __name__ == '__main__':
    main()
