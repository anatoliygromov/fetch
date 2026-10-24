"""Menu pieces drawn on the pixel grid (0 credits) for the title menu, OPTIONS, the CONTROLS page and the controls
strip (docs/ui_design.md, 24 Oct). Same method and palette as icons8.py: one disc shape and one light direction,
outline (64,11,6), 1 px shadow (36,8,5).
  g_a, g_b, g_x, g_y   button coins for the strip and the controls page: 13 px gold coins, the small font's letter in ink
  g_l, g_r, g_start    the shoulder buttons and START as small gold pills with their name in ink
  g_dpad, g_lr, g_down the d-pad, 13 px (g_lr: left and right lit, for "change" and MOVE; g_down: down lit, CRAWL)
  k_<name>             keyboard keycaps, 13 px tall: a cream key with its name in ink (SPACE, ESC, SHIFT, ENTER, X, Z, Q)
                       and the arrow keys (k_left, k_right, k_up, k_down)
  tog_on, tog_off      the HARD MODE switch: a 25 x 13 pill, knob right on gold / knob left on dark
  ribbon_menu          the straight title ribbon, wider (OPTIONS, CONTROLS in the mid font)
  handheld             the RG35XX drawn front-on: the screen, the d-pad left, X / Y / A / B in a diamond right
                       (A right, B bottom), SELECT and START, L1 / R1 on the top corners
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'v7_icons', 'tools')); sys.path.insert(0, os.path.join(HERE, '..', 'font')); sys.path.insert(0, HERE)
import icons7 as I7
import style8 as S8
from icons8 import GOLD, DARK, INK, CROSS, put, outline_of, shadow, ribbon

CREAM = dict(hi=(255, 252, 240), body=(246, 232, 200), low=(214, 190, 150), side=(176, 146, 104))
INKL = (84, 34, 14)                          # letters on gold / cream (the ink font's top colour)

def letter7(s):
    """the small font's text as a mask (glyph bodies only)"""
    G = S8.FONTS[7]; rows = []
    w = S8.width(7, s); m = np.zeros((7, w), bool); x = 0
    for ch in s:
        if ch == ' ': x += S8.SPACE[7]; continue
        g = S8.mask(7, ch if ch in G else ch.upper()); m[:, x:x + g.shape[1]] |= g; x += g.shape[1] + S8.GAP[7]
    return m

def coin(ch, D=13):
    disc, edge, rim, face, lit, ci = I7.disc_parts(D); img = np.zeros((D, D, 4), np.uint8)
    img[disc] = (238, 166, 38, 255); img[disc & (lit > 0.3)] = (246, 182, 46, 255)
    in1 = disc & ~edge; ring = in1 & ~ndimage.binary_erosion(in1, structure=CROSS, border_value=0)
    I7.paint_rim(img, ring, lit); img[edge] = (*INK, 255)
    m = letter7(ch); h, w = m.shape; oy, ox = ci - (h - 1) // 2, ci - (w - 1) // 2
    put(img, m, INKL, oy, ox)
    return img

def pill(text, h=13, pad=3, base=None):
    """a rounded gold pill with its text in ink (L1, R1, START)"""
    t = letter7(text); w = t.shape[1] + 2 * pad + 2
    m = np.ones((h, w), bool)
    for y, x in ((0, 0), (0, 1), (1, 0), (0, w - 1), (0, w - 2), (1, w - 1), (h - 1, 0), (h - 1, 1), (h - 2, 0), (h - 1, w - 1), (h - 1, w - 2), (h - 2, w - 1)): m[y, x] = False
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS, border_value=0); body = m & ~edge
    img = np.zeros((h, w, 4), np.uint8); put(img, edge, INK); put(img, body, GOLD['gold'])
    ys, xs = np.nonzero(body); y0, y1 = ys.min(), ys.max()
    img[y0][body[y0]] = (*GOLD['light'], 255); img[y1][body[y1]] = (*GOLD['dark'], 255)
    put(img, t, INKL, (h - 7) // 2, pad + 1)
    return img

def keycap(text=None, arrow=None, minw=13):
    """a cream keycap 13 px tall: 1 px ink outline, a light top row, a 2 px darker front at the bottom"""
    if arrow:
        up = ["...#...", "..###..", ".#####.", "#######", "..###..", "..###..", "..###.."]
        a = {'up': up, 'down': up[::-1], 'left': [''.join(r[y] for r in up) for y in range(7)],
             'right': [''.join(r[y] for r in up)[::-1] for y in range(7)]}[arrow]
        t = np.array([[c == '#' for c in r] for r in a])
    else: t = letter7(text)
    h = 13; w = max(minw, t.shape[1] + 6)
    m = np.ones((h, w), bool)
    for y, x in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)): m[y, x] = False
    edge = m & ~ndimage.binary_erosion(m, structure=np.ones((3, 3)), border_value=0); body = m & ~edge
    img = np.zeros((h, w, 4), np.uint8); put(img, edge, INK); put(img, body, CREAM['body'])
    ys, xs = np.nonzero(body); y0, y1 = ys.min(), ys.max()
    img[y0][body[y0]] = (*CREAM['hi'], 255)
    img[y1][body[y1]] = (*CREAM['side'], 255); img[y1 - 1][body[y1 - 1]] = (*CREAM['low'], 255)
    th, tw = t.shape; oy = 1 + (h - 3 - th) // 2; ox = (w - tw) // 2
    put(img, t, INKL, oy, ox)
    return img

def dpad(lit=None, S=13, arm=5):
    """a gold d-pad cross S px; lit: arms drawn light (the ones the screen uses)"""
    m = np.zeros((S, S), bool); a0 = (S - arm) // 2; m[a0:a0 + arm, :] = True; m[:, a0:a0 + arm] = True
    edge = m & ~ndimage.binary_erosion(m, structure=np.ones((3, 3)), border_value=0); body = m & ~edge
    img = np.zeros((S, S, 4), np.uint8); put(img, edge, INK)
    put(img, body, GOLD['gold'])
    yy, xx = np.mgrid[0:S, 0:S]; c = (S - 1) / 2
    arms = {'left': body & (xx < a0), 'right': body & (xx >= a0 + arm), 'up': body & (yy < a0), 'down': body & (yy >= a0 + arm)}
    if lit:                                            # the unused arms dark, the used ones gold with a light edge
        for k in arms:
            if k not in lit: put(img, arms[k], DARK['line'])
        for k in lit: put(img, arms[k] & ((yy == a0 + 1) if k in ('left', 'right') else (xx == a0 + 1)), GOLD['light'])
    if not lit:
        for k, col in (('up', GOLD['light']), ('left', GOLD['light']), ('down', GOLD['dark']), ('right', GOLD['dark'])):
            ys, xs = np.nonzero(arms[k] & ((xx == a0 + 1) | (yy == a0 + 1) if k in ('up', 'left') else (xx == a0 + arm - 2) | (yy == a0 + arm - 2)))
            img[ys, xs] = (*col, 255)
    img[int(c), int(c)] = (*GOLD['deep'], 255)
    return img

def toggle(on, w=25, h=13):
    m = np.ones((h, w), bool)
    for y, x in ((0, 0), (0, 1), (1, 0), (0, w - 1), (0, w - 2), (1, w - 1), (h - 1, 0), (h - 1, 1), (h - 2, 0), (h - 1, w - 1), (h - 1, w - 2), (h - 2, w - 1)): m[y, x] = False
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS, border_value=0); body = m & ~edge
    img = np.zeros((h, w, 4), np.uint8); put(img, edge, INK)
    if on:
        put(img, body, (84, 168, 60)); ys, xs = np.nonzero(body)
        img[ys.min()][body[ys.min()]] = (140, 214, 96, 255); img[ys.max()][body[ys.max()]] = (52, 112, 40, 255)
    else:
        put(img, body, DARK['fill']); ys, xs = np.nonzero(body)
        img[ys.min()][body[ys.min()]] = (*DARK['top'], 255); img[ys.max()][body[ys.max()]] = (*DARK['low'], 255)
    disc, ed, rim, face, lit, ci = I7.disc_parts(11)
    kn = np.zeros((11, 11, 4), np.uint8); kn[disc] = (*CREAM['body'], 255); kn[disc & (lit > 0.35)] = (*CREAM['hi'], 255)
    kn[disc & (lit < -0.55)] = (*CREAM['low'], 255); kn[ed] = (*INK, 255)
    ox = w - 12 if on else 1
    mm = kn[..., 3] > 0; img[1:12, ox:ox + 11][mm] = kn[mm]
    return img

def handheld():
    """the RG35XX, front-on, 78 x 124 (+ shoulders). Warm dark shell like the panels, the kit's gold buttons."""
    W, H = 78, 126
    SH0 = 4                                            # the shoulder buttons stick out above the shell
    img = np.zeros((H + SH0, W, 4), np.uint8)
    # L1 / R1: gold bumps on the top corners, behind the shell
    for x0 in (6, W - 6 - 18):
        b = np.zeros((H + SH0, W), bool); b[0:8, x0:x0 + 18] = True; b[0, x0] = b[0, x0 + 17] = False
        e = b & ~ndimage.binary_erosion(b, structure=np.ones((3, 3)), border_value=0)
        put(img, b, GOLD['mid']); img[1, x0 + 1:x0 + 17] = (*GOLD['light'], 255); img[2, x0 + 1:x0 + 17] = (*GOLD['gold'], 255); put(img, e, INK)
    o = SH0
    shell = np.zeros((H + SH0, W), bool); shell[o:o + H, :] = True
    for (y, x) in ((o, 0), (o, 1), (o + 1, 0), (o, W - 1), (o, W - 2), (o + 1, W - 1)): shell[y, x] = False
    for d in range(7):                                 # the round bottom right corner (the Game Boy shape) and a small one left
        r = 7 - int(round(np.sqrt(max(0, 49 - (7 - d) ** 2))))
        y = o + H - 1 - (7 - 1 - d)
    yy, xx = np.mgrid[0:H + SH0, 0:W]
    cx, cy, R = W - 1 - 12, o + H - 1 - 12, 12.4
    shell[(xx > cx) & (yy > cy) & (np.hypot(xx - cx, yy - cy) > R)] = False
    cx2, cy2, R2 = 3, o + H - 1 - 3, 3.4
    shell[(xx < cx2) & (yy > cy2) & (np.hypot(xx - cx2, yy - cy2) > R2)] = False
    edge = shell & ~ndimage.binary_erosion(shell, structure=CROSS, border_value=0); body = shell & ~edge
    SHELL = dict(fill=(92, 52, 36), hi=(132, 82, 54), lo=(62, 32, 22))
    put(img, body, SHELL['fill'])
    inner = ndimage.binary_erosion(body, structure=CROSS, border_value=0)
    ring = body & ~inner
    put(img, ring & ((yy < o + 3) | (xx < 2)), SHELL['hi']); put(img, ring & ((yy > o + H - 4) | (xx > W - 3)), SHELL['lo'])
    put(img, edge, INK)
    # the screen: a bezel and a glass with a tiny title (sky, Pepper's black head, the gold logo bar)
    bx0, by0, bw, bh = 7, o + 7, W - 14, 50
    bez = np.zeros_like(shell); bez[by0:by0 + bh, bx0:bx0 + bw] = True
    put(img, bez, (40, 22, 16)); put(img, bez & ~ndimage.binary_erosion(bez, structure=np.ones((3, 3)), border_value=0), INK)
    gx0, gy0, gw, gh = bx0 + 5, by0 + 5, bw - 10, bh - 10
    glass = np.zeros_like(shell); glass[gy0:gy0 + gh, gx0:gx0 + gw] = True
    put(img, glass, (64, 136, 220))
    put(img, glass & (yy >= gy0 + gh - 8), (214, 186, 140))                      # the pavement
    put(img, glass & (yy >= gy0 + gh - 9) & (yy < gy0 + gh - 8), (40, 52, 80))  # the railing line
    for k in range(gx0 + 2, gx0 + gw, 4): img[gy0 + gh - 12:gy0 + gh - 9, k] = (40, 52, 80, 255)
    lg = glass & (yy >= gy0 + 4) & (yy < gy0 + 10) & (xx >= gx0 + 22) & (xx < gx0 + gw - 4)
    put(img, lg, GOLD['gold']); put(img, lg & (yy == gy0 + 4), GOLD['light']); put(img, lg & (yy == gy0 + 9), GOLD['dark'])
    for k in range(3):                                                           # two little clouds
        for cx0, cy0 in ((gx0 + 6, gy0 + 14), (gx0 + 30, gy0 + 20)):
            img[cy0 + k // 2, cx0 + k * 2:cx0 + k * 2 + 6 - k] = (250, 246, 236, 255)
    # d-pad left, the four face buttons in a diamond right (X top, Y left, A right, B bottom)
    dp = dpad(S=19, arm=7); dy0 = o + 70
    m = dp[..., 3] > 0; img[dy0:dy0 + 19, 7:26][m] = dp[m]
    cxb, cyb = W - 21, o + 79
    for ch, dx, dy in (('X', 0, -11), ('Y', -11, 0), ('A', 11, 0), ('B', 0, 11)):
        c = shadow(coin(ch))
        m = c[..., 3] > 0; y0, x0 = cyb + dy - 6, cxb + dx - 6; img[y0:y0 + 14, x0:x0 + 14][m] = c[m]
    # SELECT and START: two small dark pills
    for x0 in (24, 42):
        p = np.zeros_like(shell); p[o + 101:o + 105, x0:x0 + 12] = True
        p[o + 101, x0] = p[o + 101, x0 + 11] = p[o + 104, x0] = p[o + 104, x0 + 11] = False
        put(img, p, (40, 22, 16)); put(img, p & (yy == o + 101), (20, 10, 6))
        img[o + 102, x0 + 1:x0 + 11] = (*GOLD['mid'], 255) if x0 == 42 else (*SHELL['hi'], 255)
    # the speaker grille, bottom right
    for k in range(4):
        for j in range(4 - k % 2):
            img[o + 108 + k * 3, W - 22 + j * 3 + (k % 2)] = (*SHELL['lo'], 255)
    return img

def build(out):
    meta = {}
    def save(name, a, sh=True):
        a = shadow(a) if sh else a; Image.fromarray(a).save(f'{out}/{name}.png'); meta[name] = (a.shape[1], a.shape[0])
    for ch in 'ABXY': save('g_' + ch.lower(), coin(ch))
    save('g_l', pill('L1')); save('g_r', pill('R1')); save('g_start', pill('START'))
    save('g_dpad', dpad()); save('g_lr', dpad(lit=['left', 'right'])); save('g_down', dpad(lit=['down']))
    for n in ('SPACE', 'ESC', 'SHIFT', 'ENTER', 'X', 'Z', 'Q'): save('k_' + n.lower(), keycap(n))
    for a in ('left', 'right', 'up', 'down'): save('k_' + a, keycap(arrow=a))
    save('tog_on', toggle(True)); save('tog_off', toggle(False))
    save('handheld', handheld())
    rm, mm = ribbon(124, 19, arch=0); save('ribbon_menu', rm); meta['ribbon_menu_body'] = mm     # OPTIONS, CONTROLS
    return meta

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k, v in build(out).items(): print(k, v)
