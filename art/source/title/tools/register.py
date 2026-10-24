"""Registers a video frame to the title still on Pepper's head: a scale and translation search (template matching,
normalised cross-correlation) of the still's head box, scaled up by s, over the frame. video = s * game + (ox, oy)."""
import cv2, numpy as np

def register(still_rgb, frame_bgr, box=(22, 78, 150, 135), scales=np.arange(3.0, 3.6, 0.01), near=None, win=24):
    g = cv2.cvtColor(still_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    V = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    tpl0 = g[box[1]:box[3], box[0]:box[2]]
    best = None
    for s in scales:
        tpl = cv2.resize(tpl0, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST); tpl = cv2.GaussianBlur(tpl, (0, 0), 1.0)
        if near is not None:                                  # search only round the previous fit
            px, py = near[1] + near[0] * box[0], near[2] + near[0] * box[1]
            x0, y0 = int(max(0, px - win)), int(max(0, py - win))
            sub = V[y0:int(py + win) + tpl.shape[0], x0:int(px + win) + tpl.shape[1]]
            if sub.shape[0] < tpl.shape[0] or sub.shape[1] < tpl.shape[1]: continue
            r = cv2.matchTemplate(sub, tpl, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r); loc = (loc[0] + x0, loc[1] + y0)
        else:
            r = cv2.matchTemplate(V, tpl, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
        if best is None or mx > best[0]: best = (mx, s, loc)
    mx, s, loc = best
    return s, loc[0] - s * box[0], loc[1] - s * box[1], mx
