"""Local grid check for the logo region: fraction of the painting's strong colour changes
that fall within 1 px of a cell border, for the uniform 320 x 240 grid and its best
sub-cell offset, plus the painting's own block pitch inside the logo."""
import numpy as np
from scipy.ndimage import maximum_filter1d
from logo_common import load_src, PX, PY

X0, X1, Y0, Y1 = 935, 2245, 130, 578


def edges(a, thr=40):
    s = a[Y0:Y1, X0:X1].astype(np.float32)
    gx = np.abs(np.diff(s, axis=1)).max(2); gy = np.abs(np.diff(s, axis=0)).max(2)
    px = (gx == maximum_filter1d(gx, 5, axis=1)) & (gx > thr)
    py = (gy == maximum_filter1d(gy, 5, axis=0)) & (gy > thr)
    return np.nonzero(px)[1] + X0 + 1, np.nonzero(py)[0] + Y0 + 1


def frac_near(v, P, off):
    r = np.mod(v - off, P); d = np.minimum(r, P - r)
    return (d <= 1.0).mean()


def pitch(v):
    best = max(((abs(np.exp(2j * np.pi * v / P).mean()), P) for P in np.arange(6.5, 11, 0.05)))
    return best[1], best[0]


if __name__ == '__main__':
    a = load_src()
    ex, ey = edges(a)
    fx, fy = frac_near(ex, PX, 0), frac_near(ey, PY, 0)
    bx = max((frac_near(ex, PX, o), o) for o in np.arange(0, PX, 0.25))
    by = max((frac_near(ey, PY, o), o) for o in np.arange(0, PY, 0.25))
    print('edges', len(ex), len(ey))
    print('uniform grid: x %.3f y %.3f' % (fx, fy))
    print('best offset: x %.3f at %.2f px, y %.3f at %.2f px' % (bx[0], bx[1], by[0], by[1]))
    print('chance level (3 px of %.1f): %.3f' % (PX, 3 / PX))
    print('painting block pitch in the logo: x %.2f (R %.2f), y %.2f (R %.2f)' % (*pitch(ex), *pitch(ey)))
