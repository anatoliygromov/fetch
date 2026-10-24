"""Step 1: the output grid.

The painting's pseudo-pixels are not on one lattice: their local pitch runs from
about 7.4 px to 11 px (measured by autocorrelation of the edge map per 160 px
tile). A 320 x 240 grid must keep an average pitch of 7.5 x 7.467 px to keep the
painting's geometry, so the grid can only follow the painted block edges locally,
within a small tolerance. This module builds both the uniform grid and a refined
grid (each line moved by at most TOL px toward the painting's edges, per band of
16 cells, by dynamic programming), and measures, per 16 x 16 cell region, the
fraction of strong colour changes that land within 1 px of a cell border.
"""
import numpy as np, os
from scipy.ndimage import maximum_filter1d
from common import load_src, NX, NY, CACHE

BAND = 16
TOL = 2


def grad(a):
    f = a.astype(np.float32)
    gx = np.abs(np.diff(f, axis=1)).max(2)  # gx[y, x]: change between x and x+1
    gy = np.abs(np.diff(f, axis=0)).max(2)
    return gx, gy


def dp_lines(prof, n, length, tol=TOL, lam=0.0):
    """Choose n-1 interior border positions b_k (integer, border between b-1 and b) near k*length/n."""
    P = length / n
    base = np.round(np.arange(1, n) * P).astype(int)
    offs = np.arange(-tol, tol + 1)
    m = len(offs)
    sc = np.zeros((n - 1, m)); bp = np.zeros((n - 1, m), int)
    def val(k, j):
        b = base[k] + offs[j]
        return prof[b - 1] if 1 <= b <= len(prof) else 0.0
    for j in range(m):
        sc[0, j] = val(0, j)
    for k in range(1, n - 1):
        for j in range(m):
            best, arg = -1e18, 0
            for i in range(m):
                pitch = (base[k] + offs[j]) - (base[k - 1] + offs[i])
                if pitch < 5:
                    continue
                s = sc[k - 1, i] - lam * (offs[j] - offs[i]) ** 2
                if s > best:
                    best, arg = s, i
            sc[k, j] = best + val(k, j); bp[k, j] = arg
    j = int(sc[-1].argmax()); out = np.zeros(n - 1, int)
    for k in range(n - 2, -1, -1):
        out[k] = base[k] + offs[j]; j = bp[k, j]
    return out


def build(a, refine=True, tol=TOL):
    H, W = a.shape[:2]
    gx, gy = grad(a)
    ncx = int(np.ceil(NX / BAND)); ncy = int(np.ceil(NY / BAND))
    # x borders per y band, band centres in source y
    XB, yc = [], []
    for b in range(ncy):
        r0, r1 = b * BAND, min(NY, (b + 1) * BAND)
        y0, y1 = int(r0 * H / NY), int(r1 * H / NY)
        prof = gx[y0:y1].sum(0)
        prof = prof / (prof.mean() + 1e-6)
        XB.append(dp_lines(prof, NX, W, tol, lam=0.3) if refine else np.round(np.arange(1, NX) * W / NX).astype(int))
        yc.append((y0 + y1) / 2)
    YB, xc = [], []
    for b in range(ncx):
        c0, c1 = b * BAND, min(NX, (b + 1) * BAND)
        x0, x1 = int(c0 * W / NX), int(c1 * W / NX)
        prof = gy[:, x0:x1].sum(1)
        prof = prof / (prof.mean() + 1e-6)
        YB.append(dp_lines(prof, NY, H, tol, lam=0.3) if refine else np.round(np.arange(1, NY) * H / NY).astype(int))
        xc.append((x0 + x1) / 2)
    XB = np.array(XB, float); YB = np.array(YB, float)
    # interpolate borders per source row / column
    yy = np.arange(H); xx = np.arange(W)
    Xr = np.stack([np.interp(yy, yc, XB[:, k]) for k in range(NX - 1)], 1)  # H x 319
    Yc = np.stack([np.interp(xx, xc, YB[:, k]) for k in range(NY - 1)], 1)  # W x 239
    # index maps: pixel centre x+0.5 compared with border b (border between b-1 and b sits at b)
    I = np.empty((H, W), np.int16); J = np.empty((H, W), np.int16)
    for y in range(H):
        I[y] = np.searchsorted(Xr[y], xx + 0.5)
    for x in range(W):
        J[:, x] = np.searchsorted(Yc[x], yy + 0.5)
    return I, J, Xr, Yc


def alignment(a, I, J, thr=40, region=16):
    """Fraction of strong colour changes within 1 px of a cell border, per region."""
    gx, gy = grad(a)
    H, W = a.shape[:2]
    pkx = (gx == maximum_filter1d(gx, 5, axis=1)) & (gx > thr)
    pky = (gy == maximum_filter1d(gy, 5, axis=0)) & (gy > thr)
    # border positions: where I changes along x (between x-1 and x)
    bx = np.zeros((H, W), bool); bx[:, 1:] = I[:, 1:] != I[:, :-1]
    by = np.zeros((H, W), bool); by[1:] = J[1:] != J[:-1]
    # an edge at gx[y,x] lies between x and x+1 -> border position x+1; within 1 px: border at x, x+1 or x+2
    nbx = bx.copy(); nbx[:, :-1] |= bx[:, 1:]; nbx[:, 1:] |= bx[:, :-1]
    nby = by.copy(); nby[:-1] |= by[1:]; nby[1:] |= by[:-1]
    okx = pkx & nbx[:, 1:]; oky = pky & nby[1:]
    ci = I[:, :-1] // region; cj = J[:, :-1] // region
    nr = (int(np.ceil(NY / region)), int(np.ceil(NX / region)))
    tot = np.zeros(nr); ok = np.zeros(nr)
    np.add.at(tot, (cj[pkx], ci[pkx]), 1); np.add.at(ok, (cj[okx], ci[okx]), 1)
    ci = I[:-1] // region; cj = J[:-1] // region
    np.add.at(tot, (cj[pky], ci[pky]), 1); np.add.at(ok, (cj[oky], ci[oky]), 1)
    frac = ok / np.maximum(tot, 1)
    return frac, tot, ok.sum() / tot.sum()


def run(refine=False, force=False):
    p = os.path.join(CACHE, 'grid_%d.npz' % int(refine))
    if os.path.exists(p) and not force:
        z = np.load(p); return z['I'], z['J']
    a = load_src()
    I, J, Xr, Yc = build(a, refine)
    np.savez_compressed(p, I=I, J=J)
    return I, J


if __name__ == '__main__':
    a = load_src()
    for refine in (False, True):
        I, J = run(refine, force=True)
        frac, tot, overall = alignment(a, I, J)
        sig = tot > 50
        print('refine', refine, 'overall %.3f' % overall, 'regions>=0.9: %d/%d' % ((frac[sig] >= 0.9).sum(), sig.sum()),
              'median region %.3f' % np.median(frac[sig]))
        sizes = np.diff(np.c_[np.zeros((I.shape[0], 1)), np.nonzero(np.diff(I, axis=1))[1].reshape(I.shape[0], -1)], axis=1) if False else None
