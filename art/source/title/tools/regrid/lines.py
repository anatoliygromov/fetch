"""Pixel-art line rules on the output grid."""
import numpy as np
from scipy import ndimage as ndi

N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
N8 = N4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def shift(m, dy, dx, fill=False):
    out = np.full_like(m, fill)
    H, W = m.shape
    ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
    xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
    out[yd, xd] = m[ys, xs]
    return out


def nb(m, dy, dx):
    """value of the neighbour at (y+dy, x+dx) for every pixel."""
    return shift(m, dy, dx)


def lcorners(line, keep_corners=True):
    """Pixels of a 1 px line that form the joint of an L (Aseprite pixel-perfect):
    one horizontal and one vertical line neighbour, and those two touch diagonally,
    and removing the joint does not cut the line (the joint has no other neighbours)."""
    m = line.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    out = np.zeros_like(m)
    for (hy, hx) in [(0, 1), (0, -1)]:
        for (vy, vx) in [(1, 0), (-1, 0)]:
            c = m & nb(m, hy, hx) & nb(m, vy, vx) & ~nb(m, vy, hx) & (n8 == 2)
            if keep_corners:
                # a real corner: both legs run on for at least two pixels
                c &= ~(nb(m, 2 * hy, 2 * hx) & nb(m, 2 * vy, 2 * vx))
            out |= c
    return out


def remove_lcorners(line):
    m = line.astype(bool).copy()
    for _ in range(4):
        c = lcorners(m)
        if not c.any():
            break
        # remove one of each adjacent pair only: process in raster order checkerboard
        for par in (0, 1):
            yy, xx = np.indices(m.shape)
            cc = lcorners(m) & ((yy + xx) % 2 == par)
            m &= ~cc
    return m


def isolated(m):
    m = m.astype(bool)
    n8 = sum(nb(m, dy, dx).astype(int) for dy, dx in N8)
    return m & (n8 == 0)


def ring(fill):
    """inner boundary ring: fill pixels with a 4-neighbour outside the fill."""
    f = fill.astype(bool)
    out = np.zeros_like(f)
    for dy, dx in N4:
        out |= f & ~shift(f, dy, dx, fill=False)
    return out


def runs_along(line):
    """Run lengths of a 1 px line traced as a chain. Returns a list of lists (per chain)
    of horizontal or vertical run lengths between steps."""
    pass
