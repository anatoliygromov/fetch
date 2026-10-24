"""Grid finding for a painting whose pixel grid drifts a little: dynamic programming over edge positions.
edges(profile, lo, hi, target): positions e_0 < e_1 < ... (cell borders) with each step in [lo, hi], maximising the
summed edge strength minus a penalty for steps away from target. Returns float border positions."""
import numpy as np

def dp_edges(sig, lo=6, hi=9, target=7.5, pen=None):
    n = len(sig)
    sig = sig / (sig.mean() + 1e-9)
    if pen is None: pen = 0.6
    NEG = -1e18
    best = np.full(n, NEG); prev = np.full(n, -1, int)
    for i in range(0, hi):           # first border anywhere in the first cell
        best[i] = sig[i]
    for i in range(n):
        if best[i] == NEG: continue
        for s in range(lo, hi + 1):
            j = i + s
            if j >= n: break
            v = best[i] + sig[j] - pen * (s - target) ** 2
            if v > best[j]: best[j] = v; prev[j] = i
    end = int(np.argmax(best[n - hi:]) + n - hi)
    out = [end]
    while prev[out[-1]] >= 0: out.append(prev[out[-1]])
    return np.array(out[::-1])

def profile(a, axis, band=None):
    """edge strength between neighbouring pixels along axis (1: between columns x and x+1)"""
    a = a.astype(float)
    g = np.abs(np.diff(a, axis=axis)).sum(axis=2)
    return g.sum(axis=0) if axis == 1 else g.sum(axis=1)

def dp_fixed(sig, n_cells, total, lo=6, hi=9, target=7.5, pen=0.35):
    """Borders b_0 = 0 < b_1 < ... < b_n = total with steps in [lo, hi] maximising the edge strength at the inner
    borders minus pen * (step - target)^2. sig[i]: the strength of the edge between source pixel i-1 and i."""
    s = np.zeros(total + 1); s[1:total] = sig[:total - 1]
    s = s / (np.median(s[s > 0]) + 1e-9); s = np.minimum(s, 6)
    NEG = -1e18
    best = np.full(total + 1, NEG); best[0] = 0
    back = np.zeros((n_cells + 1, total + 1), np.int8)
    for k in range(1, n_cells + 1):
        nb = np.full(total + 1, NEG)
        for st in range(lo, hi + 1):
            cand = np.full(total + 1, NEG); cand[st:] = best[:-st] - pen * (st - target) ** 2
            m = cand > nb; nb[m] = cand[m]; back[k][m] = st
        nb = nb + s
        best = nb
    out = [total]
    for k in range(n_cells, 0, -1): out.append(out[-1] - int(back[k][out[-1]]))
    return np.array(out[::-1])
