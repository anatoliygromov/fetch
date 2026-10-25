"""destray: remove stray pixels from a finished pixel-art layer without touching lines or patterns.
A stray is a same-colour cluster (8-connected) of 1 or 2 pixels in total that is not part of a regular pattern
(a checker or a 2/3 px window lattice: same colour repeated at +-2 or +-3 along a row or column). Lines of 3 px or
more are never touched. A stray takes the most common colour among its 8 neighbours (ties: nearest in luma).
Protected boxes are skipped. Usage: clean_rgba(rgba_array, protect=bool_mask) -> new array."""
import numpy as np
from scipy import ndimage
N8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
def _key(a):
    op = a[...,3] > 0
    return np.where(op, (a[...,0].astype(np.int64)<<16)|(a[...,1].astype(np.int64)<<8)|a[...,2], -1), op
def stray_mask(a, protect=None):
    k, op = _key(a); H, W = k.shape
    small = np.zeros((H,W), bool)
    st = np.ones((3,3), int)
    for c in np.unique(k[op]):
        lab, n = ndimage.label(k == c, structure=st)
        if n == 0: continue
        sizes = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n+1))
        bad = np.flatnonzero(sizes <= 2) + 1
        if len(bad): small |= np.isin(lab, bad)
    P2 = np.pad(k, 3, constant_values=-1)
    nb = lambda dy, dx: P2[3+dy:3+dy+H, 3+dx:3+dx+W]
    lattice = np.zeros((H,W), bool)
    for d in (2, 3):
        lattice |= ((nb(0,-d)==k)&(nb(0,d)==k)) | ((nb(-d,0)==k)&(nb(d,0)==k))
    chk = sum((nb(dy,dx)==k).astype(int) for dy,dx in [(-1,-1),(-1,1),(1,-1),(1,1)])
    lattice |= chk >= 2                      # checker: diagonal mates
    m = small & op & ~lattice
    if protect is not None: m &= ~protect
    return m
def clean_rgba(a, protect=None, passes=3):
    a = a.copy(); H, W, _ = a.shape
    for _ in range(passes):
        m = stray_mask(a, protect); ys, xs = np.nonzero(m)
        if not len(ys): break
        new = a.copy(); op = a[...,3] > 0
        for y, x in zip(ys, xs):
            me = tuple(int(v) for v in a[y,x,:3]); cand = {}
            for dy, dx in N8:
                yy, xx = y+dy, x+dx
                if 0 <= yy < H and 0 <= xx < W and op[yy,xx]:
                    c = tuple(int(v) for v in a[yy,xx,:3])
                    if c != me: cand[c] = cand.get(c, 0) + 1
            if cand:
                new[y,x,:3] = max(cand.items(), key=lambda t: (t[1], -abs(sum(t[0]) - sum(me))))[0]
        a = new
    return a
