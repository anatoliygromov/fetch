"""v8 pieces drawn on the pixel grid (0 credits), with the v7 method and palette (icons7.py): one disc shape and one
light direction for every coin, the shared outline (64,11,6) and 1 px shadow (36,8,5).
  bar_0..3      the v7 health capsule with its paw medallion, stretched by whole segments to 100 x 19 (+ shadow)
  coin_paw      the menu cursor: the v7 paw medallion at 21 px
  btn_a, btn_b  A / B coin buttons, 25 px, the mid font's A / B in ink on the face
  tab           the orange pill under a coin button (OK / BACK are drawn on it in the small font)
  row_on/off    menu rows: selected (gold, raised) and not selected (dark, inset)
  seg_on/off    one sound meter segment, lit and unlit
  medal_on/off  tally medals: a 15 px gold paw coin on a small ribbon / a plain bronze disc
  ribbon_pause, ribbon_tally   the title ribbons: a straight one and an arched one, with folded tails
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'v7_icons', 'tools')); sys.path.insert(0, os.path.join(HERE, '..', 'font'))
import icons7 as I7
import style8 as S8
INK, SH, RIM = I7.INK, I7.SH, I7.RIM
CROSS = I7.CROSS
GOLD = dict(light=(255, 222, 92), gold=(250, 188, 48), mid=(230, 144, 34), dark=(196, 102, 24), deep=(150, 66, 18))
ORANGE = dict(light=(255, 172, 92), mid=(238, 120, 40), dark=(196, 80, 24))
BRONZE = dict(light=(206, 150, 96), gold=(176, 118, 66), mid=(150, 94, 50), dark=(118, 70, 36))
DARK = dict(fill=(44, 22, 14), top=(30, 13, 8), line=(108, 62, 34), low=(84, 46, 26))

def shadow(img): return I7.shadow(img)
def put(img, m, col, oy=0, ox=0):
    ys, xs = np.nonzero(m); img[ys + oy, xs + ox] = (*col, 255)
def outline_of(m, cross=True):
    st = CROSS if cross else np.ones((3, 3), int)
    return ndimage.binary_dilation(m, structure=st) & ~m

def health_bar(n): return I7.health_bar(n, D=19, seg_w=23, seg_gap=3)

def coin_letter(ch, D=25):
    disc, edge, rim, face, lit, ci = I7.disc_parts(D); img = np.zeros((D, D, 4), np.uint8)
    img[edge] = (*INK, 255); I7.paint_rim(img, rim, lit); img[face] = (238, 166, 38, 255); img[face & (lit > 0.3)] = (246, 182, 46, 255)
    g = S8.glyph(13, ch, 'ink'); gm = g[..., 3] > 0; ys, xs = np.nonzero(gm)
    g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; gh, gw = g.shape[:2]
    oy, ox = ci - (gh - 1) // 2 - 0, ci - (gw - 1) // 2
    m = g[..., 3] > 0; img[oy:oy + gh, ox:ox + gw][m] = g[m]
    return img

def tab(w=35, h=27):
    """a pill, open at the top (hidden under the coin): rounded bottom corners, orange with a lit top and a shaded foot"""
    m = np.zeros((h, w), bool); m[:, :] = True
    for d, cut in ((0, 3), (1, 1), (2, 1)):                       # bottom corners 3-1-1 (a round end)
        y = h - 1 - d; m[y, :cut] = False; m[y, w - cut:] = False
    body = ndimage.binary_erosion(m, structure=CROSS, border_value=0); body[0, 1:-1] = m[0, 1:-1]
    edge = m & ~body
    img = np.zeros((h, w, 4), np.uint8); put(img, edge, INK); put(img, body, ORANGE['mid'])
    ys, xs = np.nonzero(body)
    for y, x in zip(ys, xs):
        if x == 1: img[y, x] = (*ORANGE['light'], 255)
        if not body[min(h - 1, y + 1), x] or y == h - 2: img[y, x] = (*ORANGE['dark'], 255)
    return img

def row(w, h, on):
    m = np.ones((h, w), bool)
    for y, x in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)): m[y, x] = False
    edge = m & ~ndimage.binary_erosion(m, structure=np.ones((3, 3)), border_value=0); body = m & ~edge
    img = np.zeros((h, w, 4), np.uint8)
    if on:
        put(img, edge, INK); put(img, body, GOLD['gold'])
        ys, xs = np.nonzero(body); y0, y1 = ys.min(), ys.max()
        img[y0][body[y0]] = (*GOLD['light'], 255); img[y1 - 1][body[y1 - 1]] = (*GOLD['mid'], 255); img[y1][body[y1]] = (*GOLD['dark'], 255)
    else:
        put(img, edge, DARK['line']); put(img, body, DARK['fill'])
        ys, xs = np.nonzero(body); y0, y1 = ys.min(), ys.max()
        img[y0][body[y0]] = (*DARK['top'], 255); img[y1][body[y1]] = (*DARK['low'], 255)
    return img

def seg(on, w=4, h=11):
    m = np.ones((h, w), bool)
    img = np.zeros((h + 2, w + 2, 4), np.uint8); M = np.zeros((h + 2, w + 2), bool); M[1:-1, 1:-1] = m
    put(img, outline_of(M, cross=True), INK)
    if on:
        put(img, M, GOLD['gold']); img[1, 1:-1] = (*GOLD['light'], 255); img[h, 1:-1] = (*GOLD['dark'], 255); img[h - 1, 1:-1] = (*GOLD['mid'], 255)
    else:
        put(img, M, (62, 30, 18)); img[1, 1:-1] = (40, 18, 10, 255); img[h, 1:-1] = (84, 46, 26, 255)
    return img

MINI_PAW = [".##.##.", ".##.##.", "#.....#", "#.###.#", ".#####.", ".#####."]
def medal(on, D=15):
    disc, edge, rim, face, lit, ci = I7.disc_parts(D)
    H = D + 4; img = np.zeros((H, D, 4), np.uint8); o = 4
    # the ribbon: two tabs above the disc, pointing up-out (a V), red when won, dull when not
    rib = (214, 52, 60) if on else (120, 84, 70); ribd = (150, 30, 40) if on else (90, 60, 50)
    for x0, sx in ((ci - 4, 1), (ci + 1, -1)):
        for y in range(5):
            for x in range(x0, x0 + 4):
                if 0 <= x < D: img[y, x] = (*(rib if (x - x0) in (1, 2) else ribd), 255)
    tabs = img[..., 3] > 0; ring = outline_of(tabs) ; ring[o:, :] = False
    put(img, ring & (np.arange(D)[None, :] >= 0), INK)
    pal = RIM if on else BRONZE
    sub = np.zeros((D, D, 4), np.uint8); sub[edge] = (*INK, 255)
    for m, col in ((rim & (lit > 0.55), pal['light']), (rim & (lit <= 0.55) & (lit > -0.2), pal['gold']), (rim & (lit <= -0.2) & (lit > -0.7), pal['mid']), (rim & (lit <= -0.7), pal['dark'])):
        put(sub, m, col)
    put(sub, face, (238, 166, 38) if on else BRONZE['gold']); put(sub, face & (lit > 0.3), (246, 182, 46) if on else BRONZE['light'])
    if on:
        for y, r in enumerate(MINI_PAW):
            for x, v in enumerate(r):
                if v == '#': sub[ci - 3 + y, ci - 3 + x] = (150, 66, 18, 255)
    m = sub[..., 3] > 0; img[o:o + D][m] = sub[m]
    return img

def ribbon(Wb, Hb, arch=0, tail=14, tuck=4, drop=5, notch=4):
    """a banner: the body Wb x Hb (its top raised by `arch` px in the middle, a parabola: runs shorten evenly to the
    ends), a tail behind each end, `drop` px lower, with a V notch, and a dark fold where it turns behind the body"""
    W = Wb + 2 * (tail - tuck); H = arch + Hb + drop
    bx0 = tail - tuck; bx1 = bx0 + Wb - 1
    def off(x):
        if not arch: return 0
        u = (x - (bx0 + bx1) / 2) / (Wb / 2); return arch - int(np.floor(arch * (1 - u * u) + 0.5))
    img = np.zeros((H, W, 4), np.uint8)
    th = Hb - 2                                                    # tail height
    for side in (0, 1):
        t = np.zeros((H, W), bool)
        ty0 = arch + drop
        for x in range(tail):
            for y in range(ty0, ty0 + th):
                d = min(x, tail - 1 - x) if False else x
                yc = ty0 + (th - 1) / 2
                if x < notch and abs(y - yc) < notch - x: continue      # the V cut into the outer end
                X = x if side == 0 else W - 1 - x
                t[y, X] = True
        e = outline_of(t, cross=False) & ~t
        put(img, e, INK); put(img, t, GOLD['mid'])
        ys, xs = np.nonzero(t)
        for y, x in zip(ys, xs):
            if y == ty0: img[y, x] = (*GOLD['gold'], 255)
            if y == ty0 + th - 1: img[y, x] = (*GOLD['dark'], 255)
        # the fold: the tail's inner end, under the body's end, in deep shade
        for y in range(ty0, ty0 + th):
            for k in range(tuck + 3):
                X = (tail - 1 - k) if side == 0 else (W - tail + k)
                if t[y, X]: img[y, X] = (*GOLD['deep'], 255)
    b = np.zeros((H, W), bool)
    for x in range(bx0, bx1 + 1):
        y0 = off(x); b[y0:y0 + Hb, x] = True
    e = outline_of(b, cross=False) & ~b
    # outline: the body's own silhouette edge (its outer rows and columns), 1 px, stairs kept thin
    body = b & ~(outline_of(~b, cross=True) & b)
    edge = b & ~body
    put(img, edge, INK); put(img, body, GOLD['gold'])
    for x in range(bx0 + 1, bx1):
        y0 = off(x)
        img[y0 + 1, x] = (*GOLD['light'], 255)
        img[y0 + Hb - 3, x] = (*GOLD['mid'], 255); img[y0 + Hb - 2, x] = (*GOLD['dark'], 255)
    for x in (bx0 + 1, bx1 - 1):                                    # the body's ends curl: one shaded column
        y0 = off(x)
        for y in range(y0 + 1, y0 + Hb - 1): img[y, x] = (*GOLD['mid'], 255)
    return img, dict(bx0=bx0, bx1=bx1, top=off((bx0 + bx1) // 2), Hb=Hb, arch=arch)

def build(out):
    os.makedirs(out, exist_ok=True); meta = {}
    def save(name, a, sh=True):
        a = shadow(a) if sh else a; Image.fromarray(a).save(f'{out}/{name}.png'); meta[name] = (a.shape[1], a.shape[0])
    for n in range(4): save(f'bar_{n}', health_bar(n))
    save('coin_paw', I7.medallion(21))
    save('btn_a', coin_letter('A')); save('btn_b', coin_letter('B'))
    save('tab', tab())
    save('row_on', row(140, 19, True)); save('row_off', row(140, 19, False), sh=False)
    save('seg_on', seg(True), sh=False); save('seg_off', seg(False), sh=False)
    save('medal_on', medal(True)); save('medal_off', medal(False))
    rp, mp = ribbon(93, 19, arch=0); save('ribbon_pause', rp); meta['ribbon_pause_body'] = mp
    rt, mt = ribbon(146, 25, arch=5, tail=22, tuck=6, drop=6, notch=6); save('ribbon_tally', rt); meta['ribbon_tally_body'] = mt
    return meta

if __name__ == "__main__":
    out = sys.argv[1]; meta = build(out)
    for k, v in meta.items(): print(k, v)
