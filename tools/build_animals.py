#!/usr/bin/env python3
"""build_animals.py: the gull and the cat, round 2 (25 Oct 2026, owner on the board: "the cat needs to be bigger,
slightly smaller than the dog, the gull needs to be smaller too"; then "go" on a cat about 30 px sitting and a gull
about 32 px wingspan).

Sources (SpriteCook, art/gen/renders/): each animal is ONE still from Pixel Engine Image at its exact game size,
animated at 1x with pixel-engine-v1.5 (no resampling anywhere; frames are only cropped, padded and aligned by whole
pixels):
  rw_gull32_flap_sheet.png 8 frames 54 x 54, a looping wingbeat (from still rw_gull32_a.png, 34 x 20)
  dt_cat30_idle_sheet.png  8 frames 48 x 48, sitting: tail curl, ear twitch, blink (from still dt_cat30_b.png, 32 x 32)
  dt_cat30_leap_sheet.png  8 frames 48 x 48: sit, crouch, arched back, spring, up, top, down, land
  dt_cat30_run_sheet.png   8 frames 48 x 48: sit, stand, running loop (frames 3-8)
Clean-up on these NEW frames, as for Pepper's clips (claude/spritecook-pipeline.md): every pixel snapped to the
animal's own still palette (no colour flicker), alpha to 0/255, detached specks of 1-3 px removed, enclosed holes of
1-4 px filled with their most common neighbour unless the ring is outline-dark (a gap drawn on purpose), lone pixels
of the coat or wing greys merged into their neighbours, the 1 px dark outline closed (tools/outline_complete.py; the
cat's ground row left alone).
Out: riverwalk/art/gull.png (8 cells of GULL_CELL) and riverwalk/art/cat.png (8 x 3 cells of CAT_CELL: idle, leap,
run; the cat's feet on the cell's bottom row, every row aligned on the sitting frame 1, the sitting cat centred)."""
import os
import sys
from collections import Counter
import numpy as np
from PIL import Image
from scipy import ndimage

R = 'art/gen/renders/'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_palette import lab
import outline_complete

CAT_CELL = (48, 48)            # w, h; feet on row 47, the sitting cat's middle at x 24
GULL_CROP = (9, 5, 45, 49)     # x0, y0, x1, y1 inside the 54 x 54 animation frames -> 36 x 44 cells
GULL_CELL = (GULL_CROP[2] - GULL_CROP[0], GULL_CROP[3] - GULL_CROP[1])


def palette_of(path):
    a = np.array(Image.open(R + path).convert('RGBA'))
    return np.unique(a[a[..., 3] > 0][:, :3], axis=0)


def snap(f, pal):
    """every pixel takes the nearest colour (Lab) of the animal's own still: one colour per pixel, nothing blended"""
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


def shift(f, dx, dy, h=None, w=None):
    h = h or f.shape[0]; w = w or f.shape[1]; out = np.zeros((h, w, 4), np.uint8)
    ys, xs = np.nonzero(f[..., 3])
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
    assert ok.all(), 'frame content would be cut'
    out[ny, nx] = f[ys, xs]
    return out


def merge_lone(sheet, cw, ch, keep):
    """a lone pixel of one of the `keep` shades (no 8-neighbour of its colour, inside its own cell) takes its most
    common neighbouring shade of that set; eyes, nose, beak and outline keep their single pixels"""
    H, W = sheet.shape[:2]; merged = 0
    for _ in range(2):
        for y in range(H):
            for x in range(W):
                c = tuple(int(v) for v in sheet[y, x, :3])
                if sheet[y, x, 3] == 0 or c not in keep: continue
                cy0, cx0 = (y // ch) * ch, (x // cw) * cw
                nb = [tuple(int(v) for v in sheet[yy, xx, :3]) for yy in range(max(cy0, y - 1), min(cy0 + ch, y + 2))
                      for xx in range(max(cx0, x - 1), min(cx0 + cw, x + 2)) if (yy, xx) != (y, x) and sheet[yy, xx, 3]]
                if c in nb: continue
                same = [n for n in nb if n in keep]
                if same: sheet[y, x, :3] = Counter(same).most_common(1)[0][0]; merged += 1
    return merged


def keep_body(sheet, cw, ch):
    """everything detached from a cell's main body goes (review 25 Oct r2: ink bars under the cat's paws in the leap,
    a lone foot of the gull): the animal is one piece"""
    gone = 0
    for y0 in range(0, sheet.shape[0], ch):
        for x0 in range(0, sheet.shape[1], cw):
            c = sheet[y0:y0 + ch, x0:x0 + cw]
            al = c[..., 3] > 0
            lbl, n = ndimage.label(al, structure=np.ones((3, 3)))
            if n > 1:
                sizes = ndimage.sum(al, lbl, range(1, n + 1))
                rest = (lbl != int(np.argmax(sizes)) + 1) & al
                c[rest] = 0; gone += int(rest.sum())
    return gone


def ink_at(sheet, cw, ch, fixes, ink):
    """close named 1 px outline gaps: (row, col, x, y) cells and pixels, 1-based row and col"""
    for r, c, x, y in fixes:
        sheet[(r - 1) * ch + y, (c - 1) * cw + x] = (*ink, 255)


def main():
    log = []
    # gull: 8 frames 54 x 54 cropped by whole pixels to 36 x 44 cells
    x0, y0, x1, y1 = GULL_CROP
    raw = frames('rw_gull32_flap_sheet.png', 54, 54, 8)
    for f0 in raw:
        crop = f0.copy(); crop[y0:y1, x0:x1] = 0
        assert not (crop[..., 3] >= 128).any(), 'gull frame content outside the crop'
    gp = palette_of('rw_gull32_a.png')
    gw, gh = GULL_CELL
    sheet = np.zeros((gh, gw * 8, 4), np.uint8)
    for i, f in enumerate(raw):
        f, n = clean(snap(f[y0:y1, x0:x1].copy(), gp)); log.append(('gull', i + 1, n)); sheet[:, i * gw:(i + 1) * gw] = f
    greys = {tuple(int(v) for v in c) for c in gp if max(c) - min(c) < 24 and 60 < np.mean(c) < 235}
    log.append(('gull greys merged', merge_lone(sheet, gw, gh, greys)))
    # review r2 G2: the pink feet showed in frames 1-4 and 8 only (gone in 5-6, a loose one in 7): it flies with them
    # tucked, so the pink goes in every frame, and any ink left hanging off the belly with it
    pink = np.array([[int(v) for v in c] for c in gp if c[0] > 180 and int(c[0]) - int(c[1]) > 50 and c[2] > 90])
    if len(pink):
        m = (sheet[..., 3] > 0) & (sheet[..., :3][:, :, None, :] == pink[None, None]).all(3).any(2)
        sheet[m] = 0; log.append(('gull feet px', int(m.sum())))
    gink = tuple(int(v) for v in gp[np.argmin(gp.astype(int).sum(1))])
    for _ in range(2):                                                    # ink spurs left by the feet
        al = sheet[..., 3] > 0; isink = al & (sheet[..., :3] == gink).all(2)
        pa = np.pad(al & ~isink, 1)
        body_nb = sum(np.roll(np.roll(pa, dy, 0), dx, 1)[1:-1, 1:-1] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
        spur = isink & (body_nb == 0)
        sheet[spur] = 0
    log.append(('gull detached px', keep_body(sheet, gw, gh)))
    ink_at(sheet, gw, gh, [(1, 5, 27, 36), (1, 5, 28, 36), (1, 5, 29, 36)], gink)   # review G3: frame 5's wing-tip edge
    Image.fromarray(sheet).save('riverwalk/art/gull.png')
    outline_complete.run('riverwalk/art/gull.png', 'riverwalk/art/gull.png')      # it flies: closed all round
    # cat: three rows of 48 x 48; leap and run aligned to idle frame 1 (the same sitting pose), feet on row 47
    idle = frames('dt_cat30_idle_sheet.png', 48, 48, 8)
    leap = frames('dt_cat30_leap_sheet.png', 48, 48, 8)
    run = frames('dt_cat30_run_sheet.png', 48, 48, 8)
    def box(f):
        ys, xs = np.nonzero(f[..., 3] >= 128); return xs.min(), xs.max(), ys.max()
    cw, ch = CAT_CELL
    i0 = box(idle[0])
    dxi = cw // 2 - (i0[0] + i0[1] + 1) // 2; dyi = ch - 1 - i0[2]          # the sitting cat centred, feet on 47
    rows = [[shift(f, dxi, dyi, ch, cw) for f in idle]]
    for seq in (leap, run):
        b = box(seq[0])
        dx, dy = i0[1] - b[1] + dxi, i0[2] - b[2] + dyi                      # right edge (the face) and feet line
        rows.append([shift(f, dx, dy, ch, cw) for f in seq])
    cp = palette_of('dt_cat30_b.png')
    cat = np.zeros((ch * 3, cw * 8, 4), np.uint8)
    for r, seq in enumerate(rows):
        for i, f in enumerate(seq):
            f, n = clean(snap(f, cp)); log.append(('cat', r + 1, i + 1, n))
            cat[r * ch:(r + 1) * ch, i * cw:(i + 1) * cw] = f
    # coat: the orange and brown shades (warm, mid luma): lone ticks merge into the neighbouring coat shade
    coat = {tuple(int(v) for v in c) for c in cp.astype(int) if c[0] > c[2] + 40 and 60 < c @ np.array([0.299, 0.587, 0.114]) < 200
            and not (c[0] > 200 and c[2] > 120)}                                 # (the ear pink stays)
    log.append(('cat coat lone merged', merge_lone(cat, cw, ch, coat)))
    log.append(('cat detached px', keep_body(cat, cw, ch)))                 # review r2 F1, F2: bars and specks under the paws
    # review r2 F1, F2, by hand: the shadow bar under the front paw in leap frames 2-4 (it touches the paw on a
    # corner, so it is not detached), the lone ink pixel at (25, 47) in leap frames 5 and 6
    gone = []
    for c in (2, 3): gone += [(c, x, y) for y in (45, 46) for x in range(31, 36)] + [(c, 35, 47)]
    gone += [(4, x, 46) for x in range(32, 36)] + [(4, x, 45) for x in range(32, 36)] + [(4, 35, 47)]
    gone += [(5, 25, 47), (6, 25, 47)]
    for c, x, y in gone: cat[ch + y, (c - 1) * cw + x] = 0
    cink = tuple(int(v) for v in cp[np.argmin(cp.astype(int).sum(1))])
    ink_at(cat, cw, ch, [(1, 4, 7, 28), (1, 8, 2, 36), (2, 2, 27, 27), (2, 4, 35, 22), (2, 5, 23, 44)], cink)   # review F3
    Image.fromarray(cat).save('riverwalk/art/cat.png')
    outline_complete.run('riverwalk/art/cat.png', 'riverwalk/art/cat.png', skip_bottom=True, frames=(cw, ch))
    filled = [l for l in log if l[-1]]
    print(f'gull.png {gw * 8}x{gh}, cat.png {cw * 8}x{ch * 3}; idle shifted', (dxi, dyi), '; fixes:', filled or 'none')


if __name__ == '__main__':
    main()
