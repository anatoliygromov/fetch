# HUD icons drawn on the pixel grid: one disc shape and one light direction for the watch, the paw medallion and coin,
# and the health bar. Shared outline (64,11,6) and 1 px shadow (36,8,5).
import numpy as np
from PIL import Image
from scipy import ndimage
INK = (64, 11, 6); SH = (36, 8, 5)
RIM = dict(light=(255, 222, 92), gold=(250, 188, 48), mid=(230, 144, 34), dark=(196, 102, 24))
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
def disc_parts(D=19):
    c = (D - 1) / 2; yy, xx = np.mgrid[0:D, 0:D]; r = np.hypot(xx - c, yy - c)
    disc = r <= c + 0.35
    edge = disc & ~ndimage.binary_erosion(disc, structure=CROSS, border_value=0)
    in1 = disc & ~edge; in2 = ndimage.binary_erosion(in1, structure=CROSS, border_value=0); in3 = ndimage.binary_erosion(in2, structure=CROSS, border_value=0)
    rim = in1 & ~in3; face = in3
    lit = np.cos(np.arctan2(yy - c, xx - c) + 3 * np.pi / 4)
    return disc, edge, rim, face, lit, int(c)
def paint_rim(img, rim, lit, oy=0, ox=0):
    for m, col in ((rim & (lit > 0.55), RIM['light']), (rim & (lit <= 0.55) & (lit > -0.2), RIM['gold']), (rim & (lit <= -0.2) & (lit > -0.7), RIM['mid']), (rim & (lit <= -0.7), RIM['dark'])):
        ys, xs = np.nonzero(m); img[ys + oy, xs + ox] = (*col, 255)
def shadow(img):
    a = np.pad(img, ((0, 1), (0, 1), (0, 0))); op = a[..., 3] > 0; sh = np.zeros_like(op); sh[1:, 1:] = op[:-1, :-1]; a[sh & ~op] = (*SH, 255); return a
PAW = ["...##.##...", "..###.###..", "#.###.###.#", "##.#...#.##", "##.......##", "....###....", "..#######..", ".#########.", ".#########.", "..##...##.."]
def medallion(D=19):
    disc, edge, rim, face, lit, ci = disc_parts(D); img = np.zeros((D, D, 4), np.uint8)
    img[edge] = (*INK, 255); paint_rim(img, rim, lit); img[face] = (238, 166, 38, 255)
    # a soft lit half on the face (top-left a tone lighter), then the paw in deep brown
    fl = face & (lit > 0.3); img[fl] = (246, 182, 46, 255)
    ph, pw = len(PAW), len(PAW[0]); oy, ox = ci - ph // 2, ci - pw // 2
    for y, row in enumerate(PAW):
        for x, v in enumerate(row):
            if v == '#': img[oy + y, ox + x] = (150, 66, 18, 255)
    return img
def watch(D=19, crown=2):
    disc, edge, rim, face, lit, ci = disc_parts(D); img = np.zeros((D + crown, D, 4), np.uint8); o = crown
    def put(m, col): ys, xs = np.nonzero(m); img[ys + o, xs] = (*col, 255)
    put(edge, INK); paint_rim(img, rim, lit, oy=o); put(face, (252, 238, 206))
    for (y, x) in [(3, ci), (D - 4, ci), (ci, 3), (ci, D - 4)]: img[o + y, x] = (196, 140, 70, 255)
    for d in range(1, 6): img[o + ci - d, ci] = (*INK, 255)
    for d in range(1, 4): img[o + ci, ci + d] = (*INK, 255)
    img[o + ci, ci] = (206, 44, 32, 255)
    img[0, ci - 1:ci + 2] = (*INK, 255); img[1, ci - 2] = (*INK, 255); img[1, ci + 2] = (*INK, 255); img[1, ci - 1:ci + 2] = (*RIM['gold'], 255)
    return img
SEG = {'red': ((255, 124, 108), (228, 52, 44), (160, 28, 28)), 'orange': ((255, 196, 96), (242, 142, 32), (190, 90, 20)),
       'yellow': ((255, 248, 160), (255, 214, 44), (214, 156, 20)), 'empty': ((112, 60, 38), (84, 40, 24), (58, 24, 14))}
def health_bar(n, D=19, seg_w=12, seg_gap=2):
    W = D - 4 + 6 + 3 * seg_w + 2 * seg_gap + 4; img = np.zeros((D, W, 4), np.uint8)
    y0, y1 = 3, D - 4                                 # the capsule rows (13 rows tall)
    x0, x1 = D - 6, W - 1
    cap = np.zeros((D, W), bool); cap[y0:y1 + 1, x0:x1 + 1] = True
    for dx, dy in ((0, 0), (1, 0), (0, 1)): cap[y0 + dy, x1 - dx] = False; cap[y1 - dy, x1 - dx] = False   # round the right end
    edge = cap & ~ndimage.binary_erosion(cap, structure=np.ones((3, 3)), border_value=0); body = cap & ~edge
    img[edge] = (*INK, 255); img[body] = (*RIM['gold'], 255)
    img[y0 + 1][body[y0 + 1]] = (*RIM['light'], 255); img[y1 - 1][body[y1 - 1]] = (*RIM['dark'], 255)
    colours = ['red', 'orange', 'yellow']
    sx = D + 1                                        # segments start right of the medallion
    for i in range(3):
        name = colours[i] if i < n else 'empty'; hi, mid, lo = SEG[name]
        s0, s1, t0, t1 = sx + i * (seg_w + seg_gap), sx + i * (seg_w + seg_gap) + seg_w - 1, y0 + 3, y1 - 3
        seg = np.zeros((D, W), bool); seg[t0:t1 + 1, s0:s1 + 1] = True
        for (yy, xx) in ((t0, s0), (t0, s1), (t1, s0), (t1, s1)): seg[yy, xx] = False
        ring = ndimage.binary_dilation(seg, structure=CROSS) & ~seg & body
        img[ring] = (*RIM['dark'], 255); img[seg] = (*mid, 255)
        img[t0][seg[t0]] = (*hi, 255); img[t1][seg[t1]] = (*lo, 255)
    m = medallion(D); op = m[..., 3] > 0; img[:, :D][op] = m[op]
    return img
if __name__ == "__main__":
    import os
    out = {'clock': watch(), 'coin': medallion(), 'bar_3': health_bar(3), 'bar_2': health_bar(2), 'bar_1': health_bar(1), 'bar_0': health_bar(0)}
    for k, v in out.items(): Image.fromarray(shadow(v)).save(f'/tmp/claude-0/ui/v6/icons/{k}.png')
    ims = [Image.open(f'/tmp/claude-0/ui/v6/icons/{k}.png') for k in ['clock', 'coin', 'bar_3', 'bar_2', 'bar_0']]
    S = 8; W = sum(i.width * S + 14 for i in ims); H = max(i.height for i in ims) * S + 10
    bg = Image.new('RGBA', (W, H), (74, 150, 232, 255)); x = 5
    for i in ims: bg.alpha_composite(i.resize((i.width * S, i.height * S), Image.NEAREST), (x, 5)); x += i.width * S + 14
    bg.save('/tmp/claude-0/ui/v6/icons7_8x.png')
    m = medallion(); shp = m[..., 3] > 0; print('medallion symmetric shape', bool((shp == shp[:, ::-1]).all() and (shp == shp[::-1]).all()))
    paw = np.array([[c == '#' for c in r] for r in PAW]); print('paw symmetric', bool((paw == paw[:, ::-1]).all()))
    for k, v in out.items(): print(k, v.shape[1], 'x', v.shape[0])
