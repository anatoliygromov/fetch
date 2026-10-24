"""A registered video frame sampled onto the title's game grid: each game pixel the mean of the inner half of its
cell in the frame (video = s * game + offset), then the title palette's nearest colour."""
import numpy as np, cv2

def sample(frame_bgr, s, ox, oy, box):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB).astype(float)
    H, W, _ = rgb.shape
    x0, y0, x1, y1 = box
    out = np.zeros((y1 - y0, x1 - x0, 3))
    for j, y in enumerate(range(y0, y1)):
        va, vb = oy + s * (y + 0.25), oy + s * (y + 0.75)
        ya, yb = int(np.floor(va)), max(int(np.floor(va)) + 1, int(np.ceil(vb)))
        for i, x in enumerate(range(x0, x1)):
            ua, ub = ox + s * (x + 0.25), ox + s * (x + 0.75)
            xa, xb = int(np.floor(ua)), max(int(np.floor(ua)) + 1, int(np.ceil(ub)))
            blk = rgb[max(0, ya):min(H, yb), max(0, xa):min(W, xb)].reshape(-1, 3)
            out[j, i] = np.median(blk, axis=0) if len(blk) else 0
    return out
