"""The title painting (source_title/title_original.png, 2400 x 1792) to the game's pixels, one colour per cell.
The painting's cells are about 7.5 px (2400 / 320) but drift by a pixel or two from place to place (pitch.py finds
7.5 in y, x wobbles; no single phase fits the whole image). So: the even 7.5 px grid (320 x 239 cells, the last row
padded once to 240), and inside each cell the sample window (the inner 3 x 3 px, never leaving the cell) is placed at
the spot of the cell's centre region where the colour is most uniform (the cell-centre majority of native.py, with the
window registered to the drawn pixel). No resampling, no filtering: every output pixel is the mean of the source
pixels of one colour bin of one cell."""
import numpy as np
from PIL import Image

P = 7.5

def sample(a, ox=0.0, oy=0.0, shift=2, win=3, q=12):
    H, W, _ = a.shape
    nx = int((W - ox) // P); ny = int(np.ceil((H - oy) / P))
    out = np.zeros((ny, nx, 3), np.uint8); pur = np.zeros((ny, nx))
    k = (a // q).astype(np.int32); key = k[..., 0] * 4096 + k[..., 1] * 64 + k[..., 2]
    for j in range(ny):
        cy = oy + (j + 0.5) * P
        for i in range(nx):
            cx = ox + (i + 0.5) * P
            best = None
            for dy in range(-shift, shift + 1):
                for dx in range(-shift, shift + 1):
                    ya = int(round(cy + dy - win / 2)); xa = int(round(cx + dx - win / 2))
                    ya = max(0, min(H - win, ya)); xa = max(0, min(W - win, xa))
                    kk = key[ya:ya + win, xa:xa + win].ravel()
                    vals, cnt = np.unique(kk, return_counts=True)
                    c = cnt.max() - 0.01 * (abs(dx) + abs(dy))          # ties: the centre wins
                    if best is None or c > best[0]: best = (c, ya, xa, vals[cnt.argmax()])
            _, ya, xa, v = best
            # the colour: every pixel of that bin in the cell's inner half (more pixels, the same drawn pixel)
            y0, y1 = int(round(cy - P / 4 - 0.5)), int(round(cy + P / 4 + 0.5)); x0, x1 = int(round(cx - P / 4 - 0.5)), int(round(cx + P / 4 + 0.5))
            y0, x0 = max(0, min(y0, ya)), max(0, min(x0, xa)); y1, x1 = min(H, max(y1, ya + win)), min(W, max(x1, xa + win))
            blk = a[y0:y1, x0:x1].reshape(-1, 3); kb = key[y0:y1, x0:x1].ravel()
            out[j, i] = blk[kb == v].mean(axis=0).round()
            pur[j, i] = (kb == v).mean()
    return out, pur

if __name__ == "__main__":
    import sys
    a = np.array(Image.open(sys.argv[1]).convert('RGB'))
    o, p = sample(a, float(sys.argv[3]) if len(sys.argv) > 3 else 0, float(sys.argv[4]) if len(sys.argv) > 4 else 0)
    Image.fromarray(o).save(sys.argv[2]); print(o.shape, 'purity', p.mean())
