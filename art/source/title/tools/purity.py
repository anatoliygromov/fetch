import numpy as np
from PIL import Image
def purity_grid(a, xs, ys, inner=0.5, q=12):
    """xs, ys: cell start borders (len n+1). Mean majority fraction of each cell's inner box, and the sampled image."""
    H, W, _ = a.shape
    nx, ny = len(xs) - 1, len(ys) - 1
    out = np.zeros((ny, nx, 3), np.uint8); pur = np.zeros((ny, nx))
    m = (1 - inner) / 2
    for j in range(ny):
        y0, y1 = ys[j], ys[j + 1]
        ya = int(round(y0 + (y1 - y0) * m)); yb = max(ya + 1, int(round(y1 - (y1 - y0) * m)))
        for i in range(nx):
            x0, x1 = xs[i], xs[i + 1]
            xa = int(round(x0 + (x1 - x0) * m)); xb = max(xa + 1, int(round(x1 - (x1 - x0) * m)))
            blk = a[ya:min(yb, H), xa:min(xb, W)].reshape(-1, 3)
            if len(blk) == 0: blk = a[min(ya, H - 1):min(ya, H - 1) + 1, min(xa, W - 1):min(xa, W - 1) + 1].reshape(-1, 3)
            k = (blk // q).astype(np.int32); key = k[:, 0] * 4096 + k[:, 1] * 64 + k[:, 2]
            vals, cnt = np.unique(key, return_counts=True); best = vals[cnt.argmax()]
            out[j, i] = blk[key == best].mean(axis=0).round()
            pur[j, i] = cnt.max() / len(blk)
    return out, pur
