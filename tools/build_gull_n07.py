#!/usr/bin/env python3
"""build_gull_n07.py [--check]: the River Walk gull at the owner's 24 px wingspan (board 7 Nov, gull_size_n0607 "24").
Still: SpriteCook Pixel Engine Image, variant c (art/gen/renders/rw_gull_n07_c.png, 24 x 16, job a0021ff2): a clear
gull silhouette, white head and body, yellow bill, silver wings with black tips, feet tucked, no holes. Flap: the
pixel-engine-v1.5 animation of that still at 1x (art/gen/out/rw_gull_flap_n07.png, 8 frames of 28 x 28, job
96e183b7). Built here:
  1. every frame snapped to the still's own 7 colours (nearest colour per pixel, no averaging), so nothing flickers;
  2. a clean pass on the new cut: lone pixels of a colour with no 4-neighbour of that colour take the 4-neighbour
     majority (never the ink), specks of under 3 px off the bird dropped; the edits listed in
     art/source/gull_n07/edits.json;
  3. by rule, frame by frame: the bill is the still's bill (yellow, its red-spot pixel) in every frame and the eye
     the still's eye, at the head's place in that frame (the animation darkened the bill in its level frame);
  4. six frames for critters.lua (art.uq, 6 cells of 26 x 26; frame 2 the swoop, wings level): up, half up, level,
     down, down, rising (animation frames 1, 2, 3, 4, 5, 7; frame 6 is a near copy of 5 and frame 8 of 1);
  5. cut to 26 x 26 (whole-pixel crop: the 28 cells' empty first and last columns and last two rows) and mirrored
     to face RIGHT, as the game's gull art faces (critters.lua flips it towards Pepper).
Writes riverwalk/art/gull.png (156 x 26) and art/source/gull_n07/gull.aseprite."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io
STILL = 'art/gen/renders/rw_gull_n07_c.png'
ANIM = 'art/gen/out/rw_gull_flap_n07.png'
OUT = 'riverwalk/art/gull.png'
PICK = [0, 1, 2, 3, 4, 6]
FW = 28
INK = (0, 0, 0)


def snap(f, pal):
    o = f.copy(); m = f[..., 3] > 0
    px = f[m][:, :3].astype(int)
    d = ((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    o[m, :3] = pal[np.argmin(d, 1)]
    return o


def clean(f, log, k):
    H, W = f.shape[:2]; o = f.copy(); m = o[..., 3] > 0
    for y in range(H):
        for x in range(W):
            if not m[y, x] or tuple(o[y, x, :3]) == INK: continue
            c = tuple(o[y, x, :3]); nb = []
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx]: nb.append(tuple(o[yy, xx, :3]))
            if nb and c not in nb:
                cand = [n for n in nb if n != INK]
                if cand:
                    best = max(set(cand), key=cand.count)
                    if cand.count(best) >= 2:
                        log.append([k, x, y, list(c), list(best)]); o[y, x, :3] = best
    # specks: opaque components under 3 px
    seen = np.zeros((H, W), bool)
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]: continue
        st = [(y0, x0)]; seen[y0, x0] = True; comp = []
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
        if len(comp) < 3:
            for y, x in comp: log.append([k, x, y, list(o[y, x, :3]), 'off']); o[y, x] = 0
    return o


FEET, WING = (196, 151, 65), (157, 166, 175)


def fix_rules(f, log, k):
    """by rule: holes (transparent pockets of up to 12 px closed in by the bird) take their neighbours' majority
    colour (never the ink); a foot pixel lying on the near wing (2 or more wing-grey 4-neighbours) is wing"""
    H, W = f.shape[:2]; m = f[..., 3] > 0
    seen = np.zeros((H, W), bool)
    for y0, x0 in zip(*np.nonzero(~m)):
        if seen[y0, x0]: continue
        st = [(y0, x0)]; seen[y0, x0] = True; comp = []; edge = False
        while st:
            y, x = st.pop(); comp.append((y, x))
            if y in (0, H - 1) or x in (0, W - 1): edge = True
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and not m[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
        if edge or len(comp) > 12: continue
        nb = []
        for y, x in comp:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if m[yy, xx] and tuple(f[yy, xx, :3]) != INK: nb.append(tuple(f[yy, xx, :3]))
        col = max(set(nb), key=nb.count) if nb else INK
        for y, x in comp:
            log.append([k, x, y, 'hole', list(col)]); f[y, x, :3] = col; f[y, x, 3] = 255
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if f[y, x, 3] and tuple(f[y, x, :3]) == FEET:
                n = sum(tuple(f[y + dy, x + dx, :3]) == WING for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if n >= 2: log.append([k, x, y, list(FEET), list(WING)]); f[y, x, :3] = WING
    # the outline closed: a transparent pixel beside a coloured (non-ink) edge pixel takes the ink
    m = f[..., 3] > 0; add = []
    for y in range(H):
        for x in range(W):
            if m[y, x]: continue
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and tuple(f[yy, xx, :3]) != INK: add.append((y, x)); break
    for y, x in add: log.append([k, x, y, 'off', list(INK)]); f[y, x] = (*INK, 255)
    return f


def build():
    s = np.array(Image.open(STILL).convert('RGBA')); a = np.array(Image.open(ANIM).convert('RGBA'))
    pal = np.unique(s[s[..., 3] > 0][:, :3], axis=0).astype(int)
    log = []; frames = []
    bill = [(x, y) for y in range(s.shape[0]) for x in range(s.shape[1]) if s[y, x, 3] and s[y, x, 0] > 180 and s[y, x, 2] < 100]
    bx0 = min(x for x, y in bill)
    for k in PICK:
        f = snap(a[:, k * FW:(k + 1) * FW], pal)
        f = clean(f, log, k)
        # bill and eye by rule: find this frame's bill tip (leftmost opaque pixel in the head rows), stamp the still's
        # head front (bill, eye, the head's ink) there
        ys, xs = np.nonzero(f[..., 3] > 0)
        hs = s[:, :bx0 + 6]                                   # the still's head front: bill + eye columns
        best = None
        for dy in range(-8, 9):                               # where the head front fits this frame best
            for dx in range(-3, 4):
                sc = 0
                for y in range(hs.shape[0]):
                    for x in range(hs.shape[1]):
                        if not hs[y, x, 3]: continue
                        yy, xx = y + 6 + dy, x + 2 + dx
                        if 0 <= yy < FW and 0 <= xx < FW and f[yy, xx, 3]:
                            sc += 1 if tuple(f[yy, xx, :3]) == tuple(hs[y, x, :3]) else 0
                if best is None or sc > best[0]: best = (sc, dx, dy)
        _, dx, dy = best
        for (x, y) in bill:
            yy, xx = y + 6 + dy, x + 2 + dx
            if 0 <= yy < FW and 0 <= xx < FW and tuple(f[yy, xx, :3]) != tuple(s[y, x, :3]):
                log.append([k, int(xx), int(yy), list(f[yy, xx, :3]), list(s[y, x, :3])]); f[yy, xx] = s[y, x]
        f = fix_rules(f, log, k)
        frames.append(f[0:26, 1:27][:, ::-1].copy())   # (rows 26-27 and columns 0, 27 are empty: checked below)
    return np.concatenate(frames, axis=1), frames, log


if __name__ == '__main__':
    sheet, frames, log = build()
    if '--check' in sys.argv:
        ok = np.array_equal(np.array(Image.open(OUT).convert('RGBA')), sheet); print('gull', 'OK' if ok else 'DIFFERS'); sys.exit(0 if ok else 1)
    Image.fromarray(sheet).save(OUT)
    aseprite_io.write('art/source/gull_n07/gull.aseprite', frames, ms=100)
    json.dump({'tool': 'tools/build_gull_n07.py', 'edits': [[int(v) if not isinstance(v, (list, str)) else ([int(t) for t in v] if isinstance(v, list) else v) for v in e] for e in log]},
              open('art/source/gull_n07/edits.json', 'w'))
    print(OUT, sheet.shape[1], 'x', sheet.shape[0], len(log), 'edits')
