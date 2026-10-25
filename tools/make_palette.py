#!/usr/bin/env python3
"""make_palette.py LEVEL [N]: the level's locked palette for NEW assets (BIBLE 4.5, docs/WORKFLOW.md).

Built only from approved art of that level (list below), so it adds no colour of its own: the colours are clustered
in Lab, weighted by how often they are drawn, and every cluster is represented by a real approved colour (the medoid),
never an average. Pepper's and the ball's colours are kept whole. Approved files are not changed.
Out: art/palettes/LEVEL.gpl (Aseprite/GIMP), LEVEL.png (1 px per colour), LEVEL_swatch.png (16x, labelled by ramp).
tools/grid_cut.py snaps every new sprite to this palette."""
import sys, os
import numpy as np
from PIL import Image

APPROVED = {
    'riverwalk': {
        'keep': ['pepper.png', 'ball.png'],
        'pool': ['girl.png', 'scene/bench.png', 'scene/bin.png', 'scene/lamp_post.png', 'scene/planter_sq.png', 'scene/pot.png',
                 'scene/flowerbox.png', 'scene/gritbox.png', 'scene/kiosk_kaffe.png', 'scene/rail_seg.png',
                 'scene/building.png', 'scene/tree.png', 'scene/cafe.png', 'scene/gable.png', 'scene/pavement.png'],
    },
}


def lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def colours(files):
    out = {}
    for f in files:
        a = np.array(Image.open('riverwalk/art/' + f).convert('RGBA')).reshape(-1, 4)
        a = a[a[:, 3] > 0][:, :3]
        v, c = np.unique(a, axis=0, return_counts=True)
        for col, n in zip(map(tuple, v), c): out[col] = out.get(col, 0) + int(n)
    return out


def main():
    level = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 56
    spec = APPROVED[level]
    keep = colours(spec['keep']); pool = colours(spec['pool'])
    for c in keep: pool.pop(c, None)
    P = np.array(list(pool), float); W = np.array([pool[tuple(map(int, p))] for p in P], float)
    k = max(1, N - len(keep)); L = lab(P)
    rng = np.random.default_rng(1)
    cent = L[rng.choice(len(L), k, replace=False, p=W / W.sum())]
    for _ in range(60):
        lab_ = np.argmin(((L[:, None] - cent[None]) ** 2).sum(2), 1)
        for j in range(k):
            m = lab_ == j
            if m.any(): cent[j] = (L[m] * W[m, None]).sum(0) / W[m].sum()
    med = []
    for j in range(k):
        m = np.where(lab_ == j)[0]
        if len(m): med.append(P[m[np.argmin(((L[m] - cent[j]) ** 2).sum(1))]])
    pal = [tuple(map(int, c)) for c in keep] + [tuple(map(int, c)) for c in med]
    pal = sorted(set(pal), key=lambda c: (round(lab(np.array([c], float))[0, 0] / 12), c))
    os.makedirs('art/palettes', exist_ok=True)
    with open(f'art/palettes/{level}.gpl', 'w') as fh:
        fh.write(f'GIMP Palette\nName: FETCH {level}\nColumns: 8\n#\n')
        for c in pal: fh.write(f'{c[0]:3d} {c[1]:3d} {c[2]:3d}\t#{c[0]:02x}{c[1]:02x}{c[2]:02x}\n')
    Image.fromarray(np.array([pal], np.uint8), 'RGB').save(f'art/palettes/{level}.png')
    cols = 8; rows = (len(pal) + cols - 1) // cols
    sw = Image.new('RGB', (cols * 16, rows * 16), (255, 0, 255))
    for i, c in enumerate(pal): sw.paste(c, ((i % cols) * 16, (i // cols) * 16, (i % cols) * 16 + 16, (i // cols) * 16 + 16))
    sw.save(f'art/palettes/{level}_swatch.png')
    print(f'{level}: {len(pal)} colours ({len(keep)} kept whole from the characters, {len(med)} from {len(pool)} prop colours)')


if __name__ == '__main__':
    main()
