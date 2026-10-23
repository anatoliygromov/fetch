# sample a generated image on its own pixel grid: one colour per art pixel (majority of the block's inner area)
import sys, numpy as np
from PIL import Image
sys.path.insert(0, __import__('os').path.dirname(__file__))
from pitch import best_pitch
def native(path, pitch=None, offx=None, offy=None):
    a = np.array(Image.open(path).convert('RGB'))
    H, W, _ = a.shape
    if pitch is None:
        px, ox, _ = best_pitch(np.abs(np.diff(a.astype(float),axis=1)).sum(axis=2).sum(axis=0))
        py, oy, _ = best_pitch(np.abs(np.diff(a.astype(float),axis=0)).sum(axis=2).sum(axis=1))
    else: px=py=pitch; ox=offx; oy=offy
    # edges sit at off + k*p (diff index i = edge between i and i+1) -> cell starts at off+1
    sx = (ox + 1) % px; sy = (oy + 1) % py
    nx = int((W - sx) // px); ny = int((H - sy) // py)
    out = np.zeros((ny, nx, 3), np.uint8)
    for j in range(ny):
        y0 = sy + j*py; ys = slice(int(round(y0 + py*0.25)), max(int(round(y0 + py*0.25))+1, int(round(y0 + py*0.75))))
        for i in range(nx):
            x0 = sx + i*px; xs = slice(int(round(x0 + px*0.25)), max(int(round(x0 + px*0.25))+1, int(round(x0 + px*0.75))))
            blk = a[ys, xs].reshape(-1, 3)
            # majority after light rounding
            q = (blk // 8).astype(np.int32); key = q[:,0]*1024 + q[:,1]*32 + q[:,2]
            vals, cnt = np.unique(key, return_counts=True); k = vals[cnt.argmax()]
            out[j, i] = blk[key == k].mean(axis=0)
    return Image.fromarray(out), (px, py, sx, sy)
if __name__ == "__main__":
    im, g = native(sys.argv[1]); im.save(sys.argv[2]); print(im.size, "grid %.3f %.3f start %.2f %.2f" % g)
