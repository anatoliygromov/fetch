"""Geometry checks for the three v8 sizes (the v5 method, geomqa.py, for every size).
python3 geomqa8.py   -> per size: widths, and every issue (0 issues is the gate)
Checks: one height; no empty side column (even spacing); every row the same width; letters and digits touch the cap row and the baseline row (one cap
line and one baseline per size); the symmetric set mirror-symmetric; no lone pixels; no 1 px vertical hairlines in
the body rows (except where a shape needs one: M W tips, the comma); in the 17 px font, no 2 px runs in the body."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glyphs7, glyphs13, glyphs17
SYM = set('AHIMOTUVWXY08-+:.!x')
SIZES = {7: (glyphs7.G, "MW,'"), 13: (glyphs13.G, "M'Q,"), 17: (glyphs17.G, 'MWQ')}
ACC = {7: glyphs7.ABOVE, 13: glyphs13.ABOVE, 17: glyphs17.ABOVE}   # (umlaut fix) accented capitals: a 17 px Ö's cap row is its accent gap

def runs(row):
    out, n, x0 = [], 0, 0
    for i, v in enumerate(row + '.'):
        if v == '#':
            if n == 0: x0 = i
            n += 1
        elif n: out.append((x0, n)); n = 0
    return out

def check(H, G, hair_ok):
    fails = []
    for k, g in G.items():
        w = len(g[0]); m = np.array([[c == '#' for c in r] for r in g])
        if len(g) != H: fails.append((k, 'height', len(g))); continue
        if any(len(r) != w for r in g): fails.append((k, 'row widths differ'))
        if k.isalnum() and k != 'x' and (not (m[0].any() or k in ACC[H]) or not m[H - 1].any()): fails.append((k, 'cap or baseline row empty'))
        if k in ACC[H] and any(len(r) != w for r in ACC[H][k]): fails.append((k, 'accent width differs'))
        if k in SYM and not (m == m[:, ::-1]).all(): fails.append((k, 'not symmetric'))
        if not m[:, 0].any() or not m[:, -1].any(): fails.append((k, 'an empty side column (spacing)'))
        b0, b1 = (1, H - 2) if H == 7 else (2, H - 3)
        for y in range(b0, b1 + 1):
            for x0, n in runs(g[y]):
                if n == 1 and k not in hair_ok: fails.append((k, f'1px run row {y} x {x0}'))
                if H == 17 and n == 2 and k not in 'MWQ': fails.append((k, f'2px run row {y} x {x0}'))
        for y in range(H):
            for x in range(w):
                if m[y, x] and not any(0 <= y + dy < H and 0 <= x + dx < w and m[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    fails.append((k, 'lone pixel', x, y))
    return fails

if __name__ == "__main__":
    total = 0
    for H, (G, ok) in SIZES.items():
        f = check(H, G, ok); total += len(f)
        widths = {k: len(g[0]) for k, g in G.items()}
        print(f'{H} px: {len(G)} glyphs, widths', {w: ''.join(sorted(k for k in widths if widths[k] == w)) for w in sorted(set(widths.values()))})
        print(f'  {len(f)} issues'); [print('   ', x) for x in f]
    print('TOTAL', total, 'issues')
