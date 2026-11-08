"""Cut a pixel-style concept onto the game grid: edge-aligned cells, label vote, colour from the original pixels of the winning label."""
import sys, numpy as np, cv2
from PIL import Image
src_p, out_p, GW, GH = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
src = np.asarray(Image.open(src_p).convert('RGB')).astype(np.float32)
H, W, _ = src.shape; pw, ph = W/GW, H/GH
g = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(float)
ex = np.abs(np.diff(g, axis=1)).sum(0); ey = np.abs(np.diff(g, axis=0)).sum(1)
def best(e, p, n):
    offs = np.arange(0, p, 0.05)
    sc = [sum(e[int(o + k*p)] for k in range(n) if int(o + k*p) < len(e)) for o in offs]
    return offs[int(np.argmax(sc))] + 1.0   # edge sits between px x and x+1
ox, oy = best(ex, pw, GW), best(ey, ph, GH)
# temporary palette for voting
K = 48
Z = src.reshape(-1, 3)
_, lab, cen = cv2.kmeans(Z, K, None, (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 2, cv2.KMEANS_PP_CENTERS)
lab = lab.reshape(H, W)
out = np.zeros((GH, GW, 3), np.uint8); conf = np.zeros((GH, GW))
for j in range(GH):
    y0 = oy + (j-1)*ph; y1 = y0 + ph
    ya, yb = max(0, int(np.ceil(y0 + 0.5))), min(H, int(np.floor(y1 - 0.5)))
    if yb <= ya: ya, yb = max(0, int(y0)), min(H, int(y1)+1)
    for i in range(GW):
        x0 = ox + (i-1)*pw; x1 = x0 + pw
        xa, xb = max(0, int(np.ceil(x0 + 0.5))), min(W, int(np.floor(x1 - 0.5)))
        if xb <= xa: xa, xb = max(0, int(x0)), min(W, int(x1)+1)
        L = lab[ya:yb, xa:xb].ravel(); P = src[ya:yb, xa:xb].reshape(-1, 3)
        c = np.bincount(L, minlength=K); w = c.argmax()
        out[j, i] = P[L == w].mean(0).round(); conf[j, i] = c[w]/len(L)
Image.fromarray(out).save(out_p)
print(f'pitch {pw:.3f}x{ph:.3f} offset {ox:.2f},{oy:.2f}  cells with a clear winner (>60%): {(conf>0.6).mean()*100:.1f}%')
