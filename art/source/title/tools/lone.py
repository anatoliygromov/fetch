import numpy as np
def lone(a, box=None):
    """fraction of pixels none of whose 4 neighbours share their colour"""
    a = a.astype(np.int64); k = a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]
    if box: x0, y0, x1, y1 = box; k = k[y0:y1, x0:x1]
    p = np.pad(k, 1, constant_values=-1)
    c = p[1:-1, 1:-1]
    same = (p[:-2, 1:-1] == c) | (p[2:, 1:-1] == c) | (p[1:-1, :-2] == c) | (p[1:-1, 2:] == c)
    return 1 - same.mean()
