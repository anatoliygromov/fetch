"""PEPPER track, step 3: tone-preserving boundary refinement.

The re-drawn fill can lose the painting's tonal mass where a minority tone is
narrower than a cell, or where a 1 px intermediate band sits between two very
different tones. This pass moves class boundaries by single cells, greedily,
when that lowers the error between the 5 x 5 blurred luma of the result and of
the painting (the form gate's own measure) and does not add mixels. A cell may
only take a class that already touches it on at least two sides, and no cell
may be left without a same-class 4-neighbour, so shapes keep smooth edges and
no specks appear. Lines, outline cells and protected classes never change.
"""
import numpy as np
from scipy import ndimage as ndi
from common import srgb_to_lab, luma

N4 = ((0, 1), (1, 0), (0, -1), (-1, 0))


def colour_index(c, j, i, pairs, bayer):
    if c < 1000:
        return c
    k, lv = divmod(c - 1000, 4)
    a, b = pairs[k]
    return b if bayer[j % 2, i % 2] < lv else a


def refine(cmap, fixed_idx, own, pal, pairs, bayer, target, outside, protect=(), passes=8,
           mix_w=40.0, edge_de=20.0, tol=6.0, eps=1.0, verbose=False):
    """cmap: class per cell (-1 = not a fill cell); fixed_idx: palette index for fixed
    cells (lines, rings, outline), -1 elsewhere; target: blurred painting luma per
    cell; outside: luma shown in non-owned cells."""
    NY, NX = cmap.shape
    lum_p = luma(pal.astype(np.float64))
    lab_p = srgb_to_lab(pal)
    idx = np.full((NY, NX), -1, np.int32)
    for j, i in zip(*np.nonzero(cmap >= 0)):
        idx[j, i] = colour_index(cmap[j, i], j, i, pairs, bayer)
    fx = fixed_idx >= 0
    idx[fx] = fixed_idx[fx]
    alive = own & (idx >= 0)
    R = np.where(alive, lum_p[np.maximum(idx, 0)], outside)
    E = ndi.uniform_filter(R, 5, mode='nearest') - target

    def is_mix(j, i):
        if not (1 <= j < NY - 1 and 1 <= i < NX - 1) or idx[j, i] < 0:
            return 0
        p = lab_p[idx[j, i]]
        for dy, dx in ((0, 1), (1, 0)):
            a_, b_ = idx[j - dy, i - dx], idx[j + dy, i + dx]
            if a_ < 0 or b_ < 0:
                continue
            A, B = lab_p[a_], lab_p[b_]
            ab = np.linalg.norm(A - B)
            pa = np.linalg.norm(p - A); pb = np.linalg.norm(p - B)
            if ab > edge_de and pa + pb <= ab + tol and pa > 3 and pb > 3:
                return 1
        return 0

    def local_mix(j, i):
        return sum(is_mix(j + dy, i + dx) for dy, dx in ((0, 0),) + N4)

    cand_cells = [(j, i) for j, i in zip(*np.nonzero(alive & ~fx & (cmap >= 0)))]
    protect = set(protect)
    total = 0
    for it in range(passes):
        changed = 0
        for j, i in cand_cells:
            c0 = cmap[j, i]
            if c0 in protect:
                continue
            nbc = [cmap[j + dy, i + dx] if 0 <= j + dy < NY and 0 <= i + dx < NX else -2 for dy, dx in N4]
            opts = set(c for c in nbc if c >= 0 and c != c0 and c not in protect)
            if not opts:
                continue
            # the old class must not leave a neighbour stranded
            j0, j1, i0, i1 = max(0, j - 2), min(NY, j + 3), max(0, i - 2), min(NX, i + 3)
            win = E[j0:j1, i0:i1]
            winm = alive[j0:j1, i0:i1]
            f0 = (win[winm] ** 2).sum()
            m0 = local_mix(j, i)
            best = None
            for c in opts:
                if sum(1 for x in nbc if x == c) < 2:
                    continue
                if not _keeps_neighbours(cmap, j, i, c0, NY, NX):
                    continue
                pi = colour_index(c, j, i, pairs, bayer)
                d = (lum_p[pi] - lum_p[idx[j, i]]) / 25.0
                f1 = ((win[winm] + d) ** 2).sum()
                old = idx[j, i]; idx[j, i] = pi
                m1 = local_mix(j, i)
                idx[j, i] = old
                gain = (f1 - f0) + mix_w * (m1 - m0)
                if gain < -eps and (best is None or gain < best[0]):
                    best = (gain, c, pi, d)
            if best is not None:
                _, c, pi, d = best
                cmap[j, i] = c; idx[j, i] = pi
                E[j0:j1, i0:i1] += d
                changed += 1
        total += changed
        if verbose:
            print('refine pass', it, 'changed', changed)
        if changed == 0:
            break
    return cmap, idx, total


def _keeps_neighbours(cmap, j, i, c0, NY, NX):
    """after (j, i) leaves class c0, every 4-neighbour of class c0 that had a same-class
    4-neighbour still has one."""
    for dy, dx in N4:
        y, x = j + dy, i + dx
        if not (0 <= y < NY and 0 <= x < NX) or cmap[y, x] != c0:
            continue
        n_same = 0
        for ey, ex in N4:
            yy, xx = y + ey, x + ex
            if (yy, xx) == (j, i):
                continue
            if 0 <= yy < NY and 0 <= xx < NX and cmap[yy, xx] == c0:
                n_same += 1
        if n_same == 0:
            return False
    return True


def clean_dots(cmap, idx, fixed, pal, pairs, bayer, edge_de=20.0, tol=6.0, diff=6.0, rounds=3):
    """Anti-aliasing dots (a cell between its two opposite neighbours' colours that does
    not continue along the edge) take the class of the closer of those neighbours, when
    that neighbour is a fill cell."""
    lab = srgb_to_lab(pal)
    NY, NX = idx.shape
    n = 0
    for _ in range(rounds):
        changed = 0
        for j in range(1, NY - 1):
            for i in range(1, NX - 1):
                if idx[j, i] < 0 or fixed[j, i]:
                    continue
                p = lab[idx[j, i]]
                for dy, dx in ((0, 1), (1, 0)):
                    a, b = (j - dy, i - dx), (j + dy, i + dx)
                    if idx[a] < 0 or idx[b] < 0:
                        continue
                    A, B = lab[idx[a]], lab[idx[b]]
                    ab = np.linalg.norm(A - B); pa = np.linalg.norm(p - A); pb = np.linalg.norm(p - B)
                    if not (ab > edge_de and pa + pb <= ab + tol and pa > diff and pb > diff):
                        continue
                    c1, c2 = (j + dx, i + dy), (j - dx, i - dy)
                    if idx[c1] == idx[j, i] or idx[c2] == idx[j, i]:
                        continue
                    q = a if pa <= pb else b
                    if cmap[q] >= 0:
                        cmap[j, i] = cmap[q]
                        idx[j, i] = colour_index(cmap[q], j, i, pairs, bayer)
                    else:           # a line or stroke colour: copy the colour itself
                        cmap[j, i] = -1
                        idx[j, i] = idx[q]
                    changed += 1
                    break
        n += changed
        if not changed:
            break
    return cmap, idx, n
