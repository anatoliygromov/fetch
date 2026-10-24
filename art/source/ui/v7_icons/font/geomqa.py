# geometry checks: size, baseline/cap, stem widths, mirror symmetry, ragged single pixels, width classes
import numpy as np
from glyphs import G
SYM = set('AHIMOTUVWXY08-+:.!x')
fails = []
def runs(row):
    out = []; n = 0
    for v in row + '.':
        if v == '#': n += 1
        elif n: out.append(n); n = 0
    return out
for k, g in G.items():
    w = len(g[0]); m = np.array([[c == '#' for c in r] for r in g])
    if len(g) != 13: fails.append((k, 'height', len(g)))
    if any(len(r) != w for r in g): fails.append((k, 'row widths differ'))
    if k.isalnum() and k != 'x':
        if not m[0].any() or not m[12].any(): fails.append((k, 'cap or baseline row empty'))
    if k in SYM and not (m == m[:, ::-1]).all(): fails.append((k, 'not symmetric'))
    # stems: in the body rows (2-10) every run must be 2 or 3 px wide, or a bar (whole-width-ish run)
    for y in range(2, 11):
        for rl in runs(g[y]):
            if rl == 1 and k not in "M'Q": fails.append((k, f'1px run row {y}'))
            if rl in (4,) and k not in 'GNKXWMQ4R2Z/x': fails.append((k, f'4px run row {y}'))
    # lone pixels: no 4-neighbour
    for y in range(13):
        for x in range(w):
            if m[y, x] and not any(0 <= y + dy < 13 and 0 <= x + dx < w and m[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                fails.append((k, 'lone pixel', x, y))
widths = {k: len(g[0]) for k, g in G.items()}
print('widths', {w: ''.join(sorted(k for k in widths if widths[k] == w)) for w in sorted(set(widths.values()))})
print(len(fails), 'issues'); [print(' ', f) for f in fails]
