"""Step 3 pieces drawn on the pixel grid (0 credits) for the remaining screens (docs/ui_design.md, 24 Oct): the level
select's cards, the talk panel, the hint bubbles, the tally show. Same method and palette as icons8.py / menu8.py:
outline (64,11,6), 1 px shadow (36,8,5), the kit's golds, one light direction (top left).
  arrow_l, arrow_r     the level select's browse arrows (gold, 9 x 15 body)
  lock                 the padlock over a locked level's picture (gold, 17 x 20)
  dot_on, dot_off      the level select's page dots (7 x 7)
  frame_s              a thin gold frame, a 9-slice (corners 4 x 4, window transparent): the card's picture, the
                       talk panel's portrait
  medal_<kind>_on/off  the three medals with their picture: nohit (a heart), bones (a bone), par (a clock); not
                       won (review fix 2): an empty dark socket with a thin gold rim where the disc would be
  bubble               the hint bubble: a 9-slice (corners 4 x 4), dark warm fill, a gold rim, ink outline
  tail_d, tail_u, tail_l, tail_r   the bubble's tail toward Pepper (drawn over the bubble's edge)
  ball                 a red ball coin (the bonus round's catches, the tally's FETCH line)
  stamp                NEW BEST! as a red stamp plate (cream letters, the small font... the mid font)
  pic_<kind>           the hint pictures (about 34 x 23, review fix 4): Pepper in her own colours, drawn on the grid
                       at half her size after her frames, and what she uses in gold
  h_a, h_b, h_x, h_y   the hint bubble's button coins (15 px, the letter in ink on a flat face)
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'v7_icons', 'tools')); sys.path.insert(0, os.path.join(HERE, '..', 'font')); sys.path.insert(0, HERE)
import icons7 as I7
import style8 as S8
from icons8 import GOLD, DARK, INK, CROSS, BRONZE, RIM, put, outline_of, shadow, MINI_PAW, ribbon

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
def socket(D=15):
    """(review fix 2) a medal not won: an empty dark socket where the disc would be (no ribbon, no picture): the ink
    edge, a thin 1 px gold rim (lit top left), the hollow in the kit's dark brown, its upper left in shade and its lower
    right lip catching the light, so it reads as a hole waiting for a medal"""
    disc, edge, rim, face, lit, ci = I7.disc_parts(D)
    H = D + 4; img = np.zeros((H, D, 4), np.uint8); o = 4
    in1 = disc & ~edge; hollow = ndimage.binary_erosion(in1, structure=CROSS, border_value=0); ring = in1 & ~hollow
    lip = hollow & ~ndimage.binary_erosion(hollow, structure=CROSS, border_value=0)
    sub = np.zeros((D, D, 4), np.uint8); sub[edge] = (*INK, 255)
    for m, col in ((ring & (lit > 0.2), GOLD['gold']), (ring & (lit <= 0.2) & (lit > -0.6), GOLD['mid']), (ring & (lit <= -0.6), GOLD['dark'])):
        put(sub, m, col)
    put(sub, hollow, DARK['fill'])
    put(sub, lip & (lit > 0.2), DARK['top'])                      # the shade under the upper left rim
    put(sub, lip & (lit < -0.6), DARK['low'])                     # the lower right lip, lit
    m = sub[..., 3] > 0; img[o:o + D][m] = sub[m]
    return img

def medal(kind, on, D=15):
    if not on: return socket(D)
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
    "oDffffffDo",
    ".oDffffDo.",
    "..oDffDo..",
    "...oDDo...",
    "....oo....",
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


# ---- (owner 24 Oct: "more like a speech bubble, this looks like a painting frame") the speech bubble for talk lines
# and hints: a 9-slice (corners 6 x 6), round pixel corners, ink outline, a cream fill with a light top row and a soft
# lower shade, one colour family, no gold. Its tails point at the speaker (talk) or at Pepper (hints).
def speech(N=13, R=4):
    """N x N, the round corners of a radius-R pixel circle (symmetric on both axes): ink outline, cream fill, the top
    inner row lit, the bottom two inner rows and the right inner column in the soft shade"""
    m = np.zeros((N, N), bool)
    for y in range(N):
        for x in range(N):
            cx = min(max(x, R), N - 1 - R); cy = min(max(y, R), N - 1 - R)
            m[y, x] = (x - cx) ** 2 + (y - cy) ** 2 <= (R + 0.35) ** 2
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS, border_value=0)
    body = m & ~edge
    img = np.zeros((N, N, 4), np.uint8)
    put(img, edge, INK); put(img, body, CREAM)
    top = body & ~np.roll(body, 1, 0); put(img, top, CREAM_HI)                      # the lit top inner row
    bot1 = body & ~np.roll(body, -1, 0); bot2 = body & ~np.roll(body & ~bot1, -1, 0) & ~bot1
    put(img, bot1 | bot2, CREAM_LO)
    return img

def stails(W=8, H=6):
    """the comic tail pointing right (r) or left (l): its base column lies over the bubble's side outline (cream there,
    so the outline opens); a flat top edge and a lower edge slanting up to the point, ink outside, cream inside.
    (d, u: the old symmetric tails, kept for nothing; returned for the build's names)"""
    m = np.zeros((H, W), bool)
    for x in range(W):
        h = int(round((H - 1) * (1 - x / (W - 1)))) + 1          # the column's height, H at the base down to 1 at the point
        m[:h, x] = True
    img = np.zeros((H, W, 4), np.uint8)
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS, border_value=0)
    edge[:, 0] = False; edge[0, 0] = True; edge[H - 1, 0] = True     # the base stays open (cream) except its two ends
    put(img, m, CREAM); put(img, edge, INK)
    r = img; l = img[:, ::-1].copy()
    d = np.transpose(img, (1, 0, 2)).copy(); u = d[::-1].copy()
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

# ---- the props in the hint pictures: Mia, a bird, arrows (each outlined on its own, cross, in the order listed)
GIRL = [".###.", "#####", ".###.", "..#..", "#####", ".###.", ".###.", ".#.#.", ".#.#."]
BIRD = ["#.....#", "##...##", ".##.##.", "..###..", "...#..."]
_UP = ["...#...", "..###..", ".#####.", "#######", "..###..", "..###..", "..###.."]
ARROWS = {'up': _UP, 'down': _UP[::-1], 'right': [''.join(r[y] for r in _UP[::-1]) for y in range(7)]}
def mask(rows): return np.array([[c == '#' for c in r.ljust(max(len(x) for x in rows), '.')] for r in rows])
# (review fix 4) the hint pictures with Pepper in her own colours: a black Labrador with her pink bandana, drawn on the
# grid at half her size after her approved frames (art/pepper.png: idle, crouch, jump, crawl, sniff, bark; her
# palette exactly: outline, shade, coat, the blue-grey sheen on her back, the bandana's three pinks), each pose about
# 20 px tall, with a 1 px light rim so the black dog reads on the bubble's dark fill (as the HUD head's rim). What
# she uses stays gold and outlined in ink; motion marks gold. No "z" for SNEAK: the low crouch says it.
PEP = {'o': (1, 1, 2), 's': (23, 24, 31), 'b': (57, 56, 71), 'h': (112, 132, 156), 'P': (250, 100, 200), 'p': (196, 60, 150),
       'q': (155, 46, 118)}
PEP_RIM = CREAM_LO
PEPPER = {
'stand': [
"..................oooo....",
".................ohhhbo...",
"................obsbbbboo.",
"o...............obsbobbbbo",
"oo..............obsbbbbbbo",
"obo.............obssbbbooo",
".obo.ooooooooooPPpsbbo....",
"..obohhhhhhhhhhbPPpoo.....",
"...obbbbbbbbbbbbbPpo......",
"...obbbbbbbbbbbbbbpo......",
"...obbbbbbbbbbbbbbbo......",
"...osbbbbbbbbbbbbbbo......",
"...ossbbbsssssbbbbbo......",
"...obbbsooooooosbbbo......",
"...obbsso....obsbbo.......",
"...obbsso....obsbbo.......",
"...obbsso....obsbbo.......",
"...obbo.o....o.obbo.......",
"..obbbo........obbbo......",
"..oooo.........oooo.......",
],
'low': [
"....................oooo....",
"...................ohhhbo...",
"..................obsbbbboo.",
"o.................obsbobbbbo",
"oo....ooooooooooooobsbbbbbbo",
".oo.oohhhhhhhhhhhhPPssbbooo.",
"..oobbbbbbbbbbbbbbbPPpbo....",
"...obbbbbbbbbbbbbbbbPpo.....",
"...obbbbbbbbbbbbbbbbbpo.....",
"...osbbbbbbbbbbbbbbbbbo.....",
"...ossbbbsssssssssbbbbo.....",
"..obbbsoooooooooosbbbo......",
".obbbbo.........obbbbbo.....",
".ooooo..........oooooo......",
],
'jump': [
".....................oooo...",
"....................ohhhbo..",
"...................obsbbbboo",
"..................obsbobbbbo",
"............ooooo.obsbbbbbbo",
"........oooohhhhhoPPssbbbooo",
"o....oooohhbbbbbbbbPPpbo....",
"oooooohhbbbbbbbbbbbbPpo.....",
".ooobbbbbbbbbbbbbbbbbpo.....",
"....obbbbbbbbbbbbbbbbbo.....",
"....obbbbssssssbbbbbbboo....",
"...obbbsoooooooosbbbobbo....",
"..obbso.........obbo.obbo...",
".obbso..........obo...ooo...",
"obbo...........obo..........",
"ooo............oo...........",
],
'crawl': [
"......................oooo....",
".....................ohhhbo...",
".......oooooooooooooobsbbbboo.",
"o....oohhhhhhhhhhhhhobsbobbbbo",
"oooooobbbbbbbbbbbbbPPsbbbbbbbo",
".ooobbbbbbbbbbbbbbbbPPpsbbooo.",
"...obbbbbbbbbbbbbbbbbPpoooo...",
"...osbbbbsssssssssbbbbpo......",
"..obbbbbooooooooooobbbbbo.....",
".obbbbbbo........obbbbbbbo....",
".ooooooo.........ooooooooo....",
],
'sniff': [
"o...........................",
"oo..........................",
"obo.........................",
".obo.ooooooooooooo..........",
"..obohhhhhhhhhhhhhoo........",
"...obbbbbbbbbbbbbbbbo.......",
"...obbbbbbbbbbbbbbbbbo......",
"...obbbbbbbbbbbbbbbPPbo.....",
"...osbbbbbbbbbbbbbbbPPbo....",
"...ossbbbsssssbbbbbbbPpo....",
"...obbbsoooooooosbbbbbpoo...",
"...obbsso....obsbbo.obbhho..",
"...obbsso....obsbbo.osbbbbo.",
"...obbsso....obsbbo.osbobbbo",
"...obbsso....obsbbo.osbbbbbo",
"...obbsso....obsbbo..obbbbbo",
"...obbo.o....o.obbo...ooooo.",
"..obbbo........obbbo........",
"..oooo.........oooo.........",
],
'bark': [
"..................oooo....",
".................ohhhbo...",
"................obsbbbboo.",
"o...............obsbobbbbo",
"oo..............obsbbbooo.",
"obo.............obssbPPo..",
".obo.ooooooooooPPpsbbooo..",
"..obohhhhhhhhhhbPPpoo.....",
"...obbbbbbbbbbbbbPpo......",
"...obbbbbbbbbbbbbbpo......",
"...obbbbbbbbbbbbbbbo......",
"...osbbbbbbbbbbbbbbo......",
"...ossbbbsssssbbbbbo......",
"...obbbsooooooosbbbo......",
"...obbsso....obsbbo.......",
"...obbsso....obsbbo.......",
"...obbsso....obsbbo.......",
"...obbo.o....o.obbo.......",
"..obbbo........obbbo......",
"..oooo.........oooo.......",
],
}

def picture2(W, H, elems):
    """elems: (kind, x, y, ...) drawn in order into W x H; a Pepper pose's x, y is its rim's top-left"""
    img = np.zeros((H, W, 4), np.uint8)
    for e in elems:
        k, x, y = e[0], e[1], e[2]
        if k in PEPPER:
            rows = PEPPER[k]; h, w = len(rows), max(len(r) for r in rows)
            m = np.zeros((H, W), bool); sub = np.zeros((H, W, 4), np.uint8)
            for yy, r in enumerate(rows):
                for xx, c in enumerate(r):
                    if c in PEP: m[y + 1 + yy, x + 1 + xx] = True; sub[y + 1 + yy, x + 1 + xx] = (*PEP[c], 255)
            put(img, outline_of(m, cross=True), PEP_RIM); img[m] = sub[m]
            continue
        if k == 'box': m = np.ones((e[4], e[3]), bool); col = GOLD['gold']
        elif k == 'girl': m = mask(GIRL); col = CREAM
        elif k == 'bird': m = mask(BIRD); col = CREAM
        elif k == 'ball': m = mask([".##.", "####", "####", ".##."]); col = BALL['mid']
        elif k in ARROWS: m = mask(ARROWS[k]); col = GOLD['light']
        elif k == 'dot': m = np.ones((2, 2), bool); col = GOLD['light']
        elif k == 'wave': m = mask(e[3]); col = GOLD['light']
        M = np.zeros((H, W), bool); h, w = m.shape; M[y:y + h, x:x + w] = m
        put(img, outline_of(M, cross=True), INK); put(img, M, col)
        if k == 'box':
            put(img, M & np.roll(~M, 1, axis=0), GOLD['light']); put(img, M & np.roll(~M, -1, axis=0) & (np.arange(H)[:, None] > y), GOLD['dark'])
        if k == 'ball': img[y, x + 1] = (*BALL['light'], 255)
        if k == 'girl':
            for (yy, xx) in ((0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 1), (2, 3)): img[y + yy, x + xx] = (*GOLD['gold'], 255)
            for yy in range(4, 7):
                for xx in range(5):
                    if M[y + yy, x + xx]: img[y + yy, x + xx] = (*DARK['line'], 255)
    return img
WAVE_S = ["#.", ".#", ".#", "#."]; WAVE_L = ["#..", ".#.", "..#", "..#", ".#.", "#.."]
PICTURES = {   # W, H, elements (Pepper's poses: stand 28 x 22 with the rim, low 30 x 16, jump 30 x 18, crawl 32 x 13, sniff 30 x 21, bark 28 x 22)
    'run':    (35, 23, [('box', 1, 7, 4, 1), ('box', 2, 11, 4, 1), ('box', 1, 15, 4, 1), ('stand', 7, 0)]),
    'hop':    (33, 24, [('box', 19, 20, 11, 2), ('jump', 0, 0)]),
    'jump':   (34, 24, [('box', 23, 11, 9, 11), ('jump', 0, 0)]),
    'climb':  (36, 26, [('box', 29, 1, 5, 23), ('up', 9, 1), ('jump', 0, 7)]),
    'crawl':  (36, 22, [('box', 1, 1, 34, 2), ('box', 1, 3, 2, 17), ('box', 33, 3, 2, 17), ('crawl', 2, 7)]),
    'duck':   (34, 25, [('bird', 25, 1), ('low', 0, 9)]),
    'stay':   (33, 24, [('down', 9, 1), ('box', 1, 21, 31, 2), ('low', 1, 5)]),
    'drop':   (38, 26, [('box', 1, 22, 26, 2), ('down', 30, 16), ('stand', 0, 0)]),
    'bounce': (38, 24, [('box', 2, 21, 26, 2), ('up', 30, 3), ('jump', 0, 0)]),
    'pickup': (35, 23, [('sniff', 0, 0), ('ball', 29, 17)]),
    'give':   (39, 23, [('stand', 0, 1), ('ball', 25, 7), ('girl', 33, 12)]),
    'bark':   (35, 23, [('bark', 0, 0), ('wave', 28, 6, WAVE_S), ('wave', 31, 5, WAVE_L)]),
    'sneak':  (32, 22, [('dot', 1, 19), ('dot', 6, 19), ('low', 2, 4)]),
    'sniff':  (36, 23, [('sniff', 0, 1), ('dot', 31, 18), ('dot', 33, 14), ('dot', 31, 10)]),
}

def hint_coin(ch, D=15):
    """(review fix 4) the bubble's button coin, 15 px: a flat gold face (no light change behind the letter) and the
    small font's letter (7 rows) in ink, 2 px of face round it, so the letter reads at 1x"""
    from menu8 import letter7
    disc, edge, rim, face, lit, ci = I7.disc_parts(D); img = np.zeros((D, D, 4), np.uint8)
    img[disc] = (*GOLD['gold'], 255)
    in1 = disc & ~edge; ring = in1 & ~ndimage.binary_erosion(in1, structure=CROSS, border_value=0)
    I7.paint_rim(img, ring, lit); img[edge] = (*INK, 255)
    m = letter7(ch); h, w = m.shape; oy, ox = ci - (h - 1) // 2, ci - (w - 1) // 2
    put(img, m, INK, oy, ox)
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
    save('speech', speech(), sh=False)
    sd, su, sl, sr = stails()
    save('stail_d', sd, sh=False); save('stail_u', su, sh=False); save('stail_l', sl, sh=False); save('stail_r', sr, sh=False)
    save('ball', ball())
    rw, mw = ribbon(176, 19, arch=0); save('ribbon_wide', rw); meta['ribbon_wide_body'] = mw     # FETCH FRENZY! (review fix 5: 176, the words well clear of its ends)
    for k, (w, h, el) in PICTURES.items(): save('pic_' + k, picture2(w, h, el))
    for ch in 'ABXY': save('h_' + ch.lower(), hint_coin(ch))
    from menu8 import dpad
    save('g_right', dpad(lit=['right']))
    save('stamp', stamp())
    return meta

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k, v in build(out).items(): print(k, v)
