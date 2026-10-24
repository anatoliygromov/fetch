"""Pixel-art line rules for the logo stripes (copied from lines.py and extended)."""
import numpy as np
from scipy import ndimage as ndi
from logo_common import shift, N4, N8


def nb(m, dy, dx):
    return shift(m, dy, dx)


def lcorners(line):
    """Joint pixels of an L (Aseprite pixel-perfect): one horizontal and one vertical
    neighbour that touch each other diagonally, and no other neighbours."""
    m = line.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    out = np.zeros_like(m)
    for (hy, hx) in [(0, 1), (0, -1)]:
        for (vy, vx) in [(1, 0), (-1, 0)]:
            out |= m & nb(m, hy, hx) & nb(m, vy, vx) & (n8 == 2)
    return out


def remove_lcorners(line):
    m = line.astype(bool).copy()
    for _ in range(6):
        c = lcorners(m)
        if not c.any():
            break
        yy, xx = np.indices(m.shape)
        for par in (0, 1):
            cc = lcorners(m) & ((yy + xx) % 2 == par)
            m &= ~cc
    return m


def bridge_gaps(s, dom, it=2):
    """add a domain cell lying between two stripe cells that do not touch each other."""
    s = s.copy()
    for _ in range(it):
        cand = dom & ~s
        add = np.zeros_like(s)
        for i, (ay, ax) in enumerate(N8):
            for (by, bx) in N8[i + 1:]:
                if max(abs(ay - by), abs(ax - bx)) <= 1:
                    continue
                add |= cand & nb(s, ay, ax) & nb(s, by, bx)
        if not add.any():
            break
        s |= add
    return s


def drop_short(s, n):
    lab, k = ndi.label(s, structure=np.ones((3, 3)))
    if k == 0:
        return s
    sz = ndi.sum(s, lab, np.arange(1, k + 1))
    return np.isin(lab, np.flatnonzero(sz >= n) + 1)


def lcorner_count(line):
    return int(lcorners(line).sum())
