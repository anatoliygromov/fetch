"""Step 3 pieces drawn on the pixel grid (0 credits) for the remaining screens (docs/ui_design.md, 24 Oct): the level
select's cards, the talk panel, the hint bubbles, the tally show. Same method and palette as icons8.py / menu8.py:
outline (64,11,6), 1 px shadow (36,8,5), the kit's golds, one light direction (top left).
  arrow_l, arrow_r     the level select's browse arrows (gold, 9 x 15 body)
  lock                 the padlock over a locked level's picture (gold, 17 x 20)
  dot_on, dot_off      the level select's page dots (7 x 7)
  frame_s              a thin gold frame, a 9-slice (corners 4 x 4, window transparent): the card's picture, the
                       talk panel's portrait
  medal_<kind>_on/off  the three medals with their picture: nohit (a heart), bones (a bone), par (a clock); not
                       won: the bronze disc, its picture dark (the slot shows what there is to win)
  bubble               the hint bubble: a 9-slice (corners 4 x 4), dark warm fill, a gold rim, ink outline
  tail_d, tail_u, tail_l, tail_r   the bubble's tail toward Pepper (drawn over the bubble's edge)
  ball                 a red ball coin (the bonus round's catches, the tally's FETCH line)
  stamp                NEW BEST! as a red stamp plate (cream letters, the small font... the mid font)
  pic_<kind>           the hint pictures (24 x 20): Pepper in cream as a pictogram and what she uses in gold
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'v7_icons', 'tools')); sys.path.insert(0, os.path.join(HERE, '..', 'font')); sys.path.insert(0, HERE)
import icons7 as I7
import style8 as S8
from icons8 import GOLD, DARK, INK, CROSS, BRONZE, RIM, put, outline_of, shadow, MINI_PAW

CREAM = (246, 232, 200); CREAM_HI = (255, 252, 240); CREAM_LO = (214, 190, 150)
RED = dict(light=(255, 120, 112), mid=(214, 52, 60), dark=(150, 30, 40))
BALL = dict(light=(255, 150, 150), mid=(226, 64, 70), dark=(160, 34, 44))
PAL = {'o': INK, 'L': GOLD['light'], 'G': GOLD['gold'], 'M': GOLD['mid'], 'D': GOLD['dark'], 'E': GOLD['deep'],
       'c': CREAM, 'C': CREAM_HI, 'l': CREAM_LO, 'r': RED['mid'], 'R': RED['light'], 'q': RED['dark'],
       'f': DARK['fill'], 'n': DARK['line'], 'w': DARK['low']}

def chars(rows, pal=PAL):
    h, w = len(rows), max(len(r) for r in rows)
    img = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in pal: img[y, x] = (*pal[ch], 255)
    return img

def arrow(right=True):
    rows = []
    for y in range(15):
        n = 8 - abs(y - 7)
        rows.append([x < n for x in range(9)])
    m = np.array(rows)
    M = np.zeros((17, 11), bool); M[1:16, 1:10] = m
    img = np.zeros((17, 11, 4), np.uint8)
    put(img, outline_of(M, cross=True), INK)
    yy, xx = np.mgrid[0:17, 0:11]
    put(img, M, GOLD['gold'])
    put(img, M & (yy <= 4), GOLD['light']); put(img, M & (yy >= 11), GOLD['mid']); put(img, M & (yy >= 13), GOLD['dark'])
    # the lit top edge of the slope
    edge_in = M & ~ndimage.binary_erosion(M, structure=CROSS, border_value=0)
    put(img, edge_in & (yy < 8), GOLD['light'])
    put(img, edge_in & (yy > 8), GOLD['dark'])
    if not right: img = img[:, ::-1]
    return img

LOCK = [
    ".....ooooooo.....",
    "....oLLLLLLLo....",
    "...oLMoooooMLo...",
    "...oLo.....oMo...",
    "...oLo.....oMo...",
    "...oMo.....oDo...",
    "...oMo.....oDo...",
    ".ooooooooooooooo.",
    "oLLLLLLLLLLLLLLLo",
    "oLGGGGGGGGGGGGGDo",
    "oLGGGGGoooGGGGGDo",
    "oLGGGGGoooGGGGGDo",
    "oLGGGGGGoGGGGGGDo",
    "oLGGGGGGoGGGGGGDo",
    "oLGGGGGGGGGGGGGDo",
    "oMMMMMMMMMMMMMMDo",
    "oDDDDDDDDDDDDDDDo",
    ".ooooooooooooooo.",
]

def lock_big(bw=25, bh=17, sw=17, sh=13, th=3):
    """a bigger padlock for the card's picture: a gold body bw x bh with a keyhole, a shackle sw wide, th thick"""
    W, H = bw + 2, sh + bh + 2
    img = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    cx = (W - 1) / 2
    # the shackle: an arch (a half ring on top, straight legs down into the body)
    r_out = sw / 2; r_in = r_out - th
    cy = 1 + r_out
    d = np.hypot(xx - cx, yy - cy)
    arch = ((d <= r_out - 0.1) & (d > r_in - 0.1) & (yy <= cy)) | ((np.abs(xx - cx) <= r_out - 0.1) & (np.abs(xx - cx) > r_in - 0.1) & (yy > cy) & (yy < sh + 2))
    body = np.zeros((H, W), bool); body[sh + 1:sh + 1 + bh, 1:1 + bw] = True
    for (y, x) in ((sh + 1, 1), (sh + 1, bw), (sh + bh, 1), (sh + bh, bw)): body[y, x] = False
    put(img, outline_of(arch, cross=True), INK)
    put(img, arch, GOLD['mid']); put(img, arch & (xx < cx), GOLD['light']); put(img, arch & (xx > cx + r_in), GOLD['dark'])
    put(img, outline_of(body, cross=True), INK)
    put(img, body, GOLD['gold'])
    ys = np.nonzero(body.any(1))[0]; y0, y1 = ys.min(), ys.max()
    put(img, body & (yy == y0), GOLD['light']); put(img, body & (xx == 1) , GOLD['light'])
    put(img, body & (yy == y1), GOLD['dark']); put(img, body & (yy == y1 - 1), GOLD['mid']); put(img, body & (xx == bw), GOLD['dark'])
    kx, ky = int(round(cx)), sh + 1 + bh // 2 - 3
    for (y, x) in ((0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0)): img[ky + y, kx + x] = (*INK, 255)
    img[ky + 2, kx - 1] = (*INK, 255); img[ky + 2, kx + 1] = (*INK, 255)
    return img

DOT_ON = ["..ooo..", ".oLLGo.", "oLLGGDo", "oLGGGDo", "oGGGDDo", ".oDDDo.", "..ooo.."]
DOT_OFF = ["..ooo..", ".onnno.", "onwwwno", "onwwwno", "onwwwno", ".onnno.", "..ooo.."]

def frame_s():
    """12 x 12, corners 4: ink, gold (light top-left, dark bottom-right), gold, ink; the window transparent"""
    rows = [
        ".oooooooooo.",
        "oLLLLLLLLLLo",
        "oLGGGGGGGGDo",
        "oLGoooooooDo",
        "oLGo....oMDo",
        "oLGo....oMDo",
        "oLGo....oMDo",
        "oLGo....oMDo",
        "oLGooooooMDo",
        "oLMMMMMMMMDo",
        "oDDDDDDDDDDo",
        ".oooooooooo.",
    ]
    return chars(rows)

PICS = {
    'nohit': ([".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."], RED['mid'], RED['light']),
    'bones': (["##...##", ".#####.", ".#####.", "##...##"], CREAM, CREAM_HI),
    'par':   (["..###..", ".##h##.", "###h###", "###hh##", "#######", ".#####.", "..###.."], CREAM, CREAM_HI),
}
def medal(kind, on, D=15):
    disc, edge, rim, face, lit, ci = I7.disc_parts(D)
    H = D + 4; img = np.zeros((H, D, 4), np.uint8); o = 4
    rib = (214, 52, 60) if on else (120, 84, 70); ribd = (150, 30, 40) if on else (90, 60, 50)
    for x0 in (ci - 4, ci + 1):
        for y in range(1, 5):
            for x in range(x0, x0 + 4):
                if 0 <= x < D: img[y, x] = (*(rib if (x - x0) in (1, 2) else ribd), 255)
    tabs = img[..., 3] > 0; put(img, outline_of(tabs), INK)
    pal = RIM if on else BRONZE
    sub = np.zeros((D, D, 4), np.uint8); sub[edge] = (*INK, 255)
    for m, col in ((rim & (lit > 0.55), pal['light']), (rim & (lit <= 0.55) & (lit > -0.2), pal['gold']), (rim & (lit <= -0.2) & (lit > -0.7), pal['mid']), (rim & (lit <= -0.7), pal['dark'])):
        put(sub, m, col)
    put(sub, face, (238, 166, 38) if on else BRONZE['gold']); put(sub, face & (lit > 0.3), (246, 182, 46) if on else BRONZE['light'])
    rows, col, hi = PICS[kind]
    p = np.array([[c in '#h' for c in r] for r in rows]); ph, pw = p.shape
    hands = np.array([[c == 'h' for c in r] for r in rows])
    oy, ox = ci - (ph - 1) // 2, ci - (pw - 1) // 2
    if on:
        put(sub, p, col, oy, ox)
        ys, xs = np.nonzero(p); top = ys.min()
        for y, x in zip(ys, xs):                                  # a lit pixel top left of the picture
            if y == top and x == xs[ys == top].min(): sub[oy + y, ox + x] = (*hi, 255)
        put(sub, hands, INK, oy, ox)                              # the clock's hands in ink
    else:
        put(sub, p, BRONZE['dark'], oy, ox); put(sub, hands, BRONZE['light'], oy, ox)
    m = sub[..., 3] > 0; img[o:o + D][m] = sub[m]
    return img

def bubble():
    """12 x 12, corners 4: ink outline (round corners), a 1 px gold rim (light top, dark bottom), the dark fill"""
    rows = [
        "..oooooooo..",
        ".oLLLLLLLLo.",
        "oLLffffffLLo",
        "oLffffffffDo",
        "oLffffffffDo",
        "oLffffffffDo",
        "oLffffffffDo",
        "oLffffffffDo",
        "oLffffffffDo",
        "oDDffffffDDo",
        ".oDDDDDDDDo.",
        "..oooooooo..",
    ]
    return chars(rows)

# the tails: drawn with their base row/column over the bubble's outline (the base pixels are the bubble's rim and fill,
# so the outline opens where the tail joins)
TAIL_D = [
    "oDffffDo",
    ".oDffDo.",
    "..oDDo..",
    "...oo...",
]
def tails():
    d = chars(TAIL_D)
    u = d[::-1].copy()
    # the up tail: the lit rim at its base
    for y in range(u.shape[0]):
        for x in range(u.shape[1]):
            if tuple(u[y, x, :3]) == GOLD['dark'] and u[y, x, 3]: u[y, x, :3] = GOLD['light']
    r = np.transpose(d, (1, 0, 2)).copy()
    l = r[:, ::-1].copy()
    for y in range(l.shape[0]):
        for x in range(l.shape[1]):
            if tuple(l[y, x, :3]) == GOLD['dark'] and l[y, x, 3]: l[y, x, :3] = GOLD['light']
    return d, u, l, r

def ball(D=13):
    disc, edge, rim, face, lit, ci = I7.disc_parts(D); img = np.zeros((D, D, 4), np.uint8)
    inner = disc & ~edge
    put(img, inner, BALL['mid']); put(img, inner & (lit > 0.45), BALL['light']); put(img, inner & (lit < -0.6), BALL['dark'])
    img[edge] = (*INK, 255)
    img[3, 4] = (255, 236, 230, 255); img[3, 5] = (255, 236, 230, 255); img[4, 3] = (255, 236, 230, 255)
    return img

def stamp():
    """NEW BEST! on a red plate: ink outline, a light top row, a dark foot, the mid font in cream (outlined in ink)"""
    t = S8.text(13, 'NEW BEST!', 'cream')                            # (body at 2, 2; outline and shadow round it)
    th, tw = t.shape[:2]
    w, h = tw + 8, th + 4
    m = np.ones((h, w), bool)
    for y, x in ((0, 0), (0, 1), (1, 0), (0, w - 1), (0, w - 2), (1, w - 1), (h - 1, 0), (h - 1, 1), (h - 2, 0), (h - 1, w - 1), (h - 1, w - 2), (h - 2, w - 1)): m[y, x] = False
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS, border_value=0); body = m & ~edge
    img = np.zeros((h, w, 4), np.uint8); put(img, edge, INK); put(img, body, RED['mid'])
    ys, xs = np.nonzero(body); y0, y1 = ys.min(), ys.max()
    img[y0][body[y0]] = (*RED['light'], 255); img[y1][body[y1]] = (*RED['dark'], 255); img[y1 - 1][body[y1 - 1]] = (*RED['dark'], 255)
    # an inner dashed line like an ink stamp's border (every other pixel, 2 px in)
    for x in range(4, w - 4, 2): img[2, x] = (*RED['light'], 255)
    tm = t[..., 3] > 0
    sub = img[2:2 + th, 3:3 + tw]; sub[tm] = t[tm]
    return img

def build(out):
    meta = {}
    def save(name, a, sh=True):
        a = shadow(a) if sh else a; Image.fromarray(a).save(f'{out}/{name}.png'); meta[name] = (a.shape[1], a.shape[0])
    save('arrow_r', arrow(True)); save('arrow_l', arrow(False))
    save('lock', chars(LOCK)); save('lock_big', lock_big())
    save('dot_on', chars(DOT_ON)); save('dot_off', chars(DOT_OFF), sh=False)
    save('frame_s', frame_s(), sh=False)
    for k in ('nohit', 'bones', 'par'):
        save(f'medal_{k}_on', medal(k, True)); save(f'medal_{k}_off', medal(k, False))
    save('bubble', bubble(), sh=False)
    d, u, l, r = tails()
    save('tail_d', d, sh=False); save('tail_u', u, sh=False); save('tail_l', l, sh=False); save('tail_r', r, sh=False)
    save('ball', ball())
    save('stamp', stamp())
    return meta

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k, v in build(out).items(): print(k, v)
