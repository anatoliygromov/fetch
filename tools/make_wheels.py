# Rolling wheels for the bikes (code-made, from the SpriteCook cyclists in riverwalk/art/scene/).
# Each wheel's inside (the dark spoke pattern, which never moved) is cleared and redrawn as a hub and N spokes,
# in F rotation steps; everything that is not wheel colour (legs, shoes, the frame's light tubes) stays on top.
# Output: <name>_roll.png, F frames side by side (frame i = the spokes turned i/F of one spoke gap, clockwise:
# the art faces right, so the frames go forwards as the bike rides; mirrored art turns the other way by itself).
import os, math, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
F = 4
# name: wheels (cx, cy, outer r), tyre thickness, spokes, the wheel colours, spoke colour, hub colours (dark, light)
BIKES = {
  'cyclist1': dict(w=[(9, 40, 9.5), (39, 40, 9.5)], tyre=2.0, n=8,
                   wc=[(0, 0, 1), (21, 23, 28), (29, 33, 37), (43, 47, 52)], sp=(52, 57, 62), hub=((21, 23, 28), (96, 102, 108))),
  'cyclist2': dict(w=[(9, 40, 9.5), (39, 40, 9.5)], tyre=2.0, n=8,
                   wc=[(0, 0, 1), (21, 23, 28), (29, 33, 37), (43, 47, 52)], sp=(52, 57, 62), hub=((21, 23, 28), (96, 102, 108))),
  'road_cyclist1': dict(w=[(14, 60, 14.5), (58.5, 60, 14.5)], tyre=2.6, n=12,
                   wc=[(0, 0, 0), (19, 15, 12), (40, 35, 31)], sp=(58, 54, 50), hub=((19, 15, 12), (99, 98, 96))),
  'road_cyclist2': dict(w=[(14, 60, 14.5), (58.5, 60, 14.5)], tyre=2.6, n=12,
                   wc=[(0, 0, 0), (19, 15, 12), (40, 35, 31)], sp=(58, 54, 50), hub=((19, 15, 12), (99, 98, 96))),
}

def build(name, cfg):
    a = np.array(Image.open(os.path.join(ART, name + '.png')).convert('RGBA'))
    H, W = a.shape[:2]
    wc = set(map(tuple, cfg['wc']))
    frames = []
    for f in range(F):
        b = a.copy()
        for cx, cy, r in cfg['w']:
            rin = r - cfg['tyre']
            keep = np.zeros((H, W), bool)
            for y in range(H):
                for x in range(W):
                    d = math.hypot(x - cx, y - cy)
                    if d < rin and b[y, x, 3] > 0 and tuple(b[y, x, :3]) not in wc: keep[y, x] = True
            over = b.copy()
            for y in range(H):                                   # clear the inside
                for x in range(W):
                    if math.hypot(x - cx, y - cy) < rin: b[y, x] = 0
            n = cfg['n']; gap = 2 * math.pi / n
            for k in range(n):                                   # spokes: sample along each ray
                ang = k * gap + f * gap / F
                for t in np.linspace(1.2, rin - 0.3, int(rin * 4)):
                    x = int(math.floor(cx + t * math.cos(ang) + 0.5 - 1e-6)); y = int(math.floor(cy + t * math.sin(ang) + 0.5 - 1e-6))
                    if 0 <= x < W and 0 <= y < H and math.hypot(x - cx, y - cy) < rin: b[y, x] = (*cfg['sp'], 255)
            hx, hy = int(math.floor(cx)), int(math.floor(cy))      # the hub: dark square, light middle
            for y in range(hy - 1, hy + 2):
                for x in range(hx - 1, hx + 2): b[y, x] = (*cfg['hub'][0], 255)
            b[hy, hx] = (*cfg['hub'][1], 255)
            b[keep] = over[keep]                                  # legs, frame tubes, shoes stay in front
        frames.append(b)
    sheet = np.concatenate(frames, axis=1)
    Image.fromarray(sheet, 'RGBA').save(os.path.join(ART, name + '_roll.png'))
    print(name, 'x', F, 'frames', W, 'x', H)

for k, v in BIKES.items(): build(k, v)
