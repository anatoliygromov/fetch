"""The v8 fonts styled: one family, three sizes (7, 13, 17 rows), the v5 styling for every size: a highlight row, a
yellow top and an orange bottom (gold), cream, dim; one 1 px outline (64,11,6) and a 1 px drop shadow (36,8,5) down
and right. 'ink' is for letters on a gold ribbon: dark brown, no outline, a 1 px light line under each stroke.
A glyph image is (H + 5) x (W + 5): the body at (2, 2), 1 px outline round it, the shadow 1 px further down-right.
Text advances W + GAP[size] per glyph (the bodies GAP px apart, the outlines between them), a space SPACE[size]."""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glyphs7, glyphs13, glyphs17
FONTS = {7: glyphs7.G, 13: glyphs13.G, 17: glyphs17.G}
GAP = {7: 1, 13: 2, 17: 2}
SPACE = {7: 3, 13: 5, 17: 7}
INK = (64, 11, 6); SHADOW = (36, 8, 5)
STYLES = {
  'gold':  dict(hi=(255, 244, 168), top=(255, 216, 56), mid=(252, 180, 40), bot=(238, 128, 30), deep=(214, 96, 24)),
  'cream': dict(hi=(255, 255, 255), top=(255, 250, 230), mid=(250, 238, 206), bot=(240, 222, 182), deep=(226, 204, 160)),
  'dim':   dict(hi=(210, 196, 172), top=(196, 182, 158), mid=(186, 172, 148), bot=(174, 160, 136), deep=(160, 146, 122)),
  'ink':   dict(top=(84, 34, 14), bot=(66, 24, 10), emboss=(255, 224, 120)),
}
def band(st, y, H):
    t = y / max(1, H - 1)
    return st['hi'] if y == 0 else st['top'] if t < 0.52 else st['mid'] if t < 0.62 else st['bot'] if t < 0.88 else st['deep']
def mask(size, ch):
    return np.array([[c == '#' for c in r] for r in FONTS[size][ch]])
def glyph(size, ch, style):
    m = mask(size, ch); H, W = m.shape; pad = 2
    M = np.zeros((H + pad * 2 + 1, W + pad * 2 + 1), bool); M[pad:pad + H, pad:pad + W] = m
    o = np.zeros(M.shape + (4,), np.uint8); st = STYLES[style]
    if style == 'ink':
        em = np.zeros_like(M); em[1:, :] = M[:-1, :]; em &= ~M
        o[em] = (*st['emboss'], 255)
        for y in range(H):
            col = st['top'] if y < H * 0.6 else st['bot']
            o[pad + y][M[pad + y]] = (*col, 255)
        return o
    ring = ndimage.binary_dilation(M, structure=np.ones((3, 3))) & ~M
    sh = np.zeros_like(M); sh[1:, 1:] = (M | ring)[:-1, :-1]; sh &= ~(M | ring)
    o[sh] = (*SHADOW, 255); o[ring] = (*INK, 255)
    for y in range(H): o[pad + y][M[pad + y]] = (*band(st, y, H), 255)
    return o
def width(size, s):
    """body width of a text (glyph bodies and the gaps between them, no outline)"""
    G = FONTS[size]; w = 0; n = 0
    for ch in s:
        if ch == ' ': w += SPACE[size]; continue
        k = ch if ch in G else ch.upper()
        w += len(G[k][0]) + GAP[size]; n += 1
    return w - (GAP[size] if n and s[-1] != ' ' else 0)
def text(size, s, style='cream'):
    """an RGBA image of the text: the first body pixel at (2, 2)"""
    G = FONTS[size]; H = len(G['A']); W = width(size, s) + 5
    o = Image.new('RGBA', (W, H + 5)); x = 0
    for ch in s:
        if ch == ' ': x += SPACE[size]; continue
        k = ch if ch in G else ch.upper()
        o.alpha_composite(Image.fromarray(glyph(size, k, style)), (x, 0)); x += len(G[k][0]) + GAP[size]
    return np.array(o)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    lines = [(17, 'GOOD GIRL!', 'ink'), (17, 'ABCDEFGHIJKLM', 'gold'), (17, 'NOPQRSTUVWXYZ', 'gold'), (17, '0123456789 !?.:-', 'gold'),
             (13, 'PAUSED', 'ink'), (13, 'ABCDEFGHIJKLM', 'gold'), (13, 'NOPQRSTUVWXYZ', 'cream'), (13, '0123456789 !?.:-/+x,', 'gold'),
             (7, 'LEVEL 1 RIVER WALK', 'cream'), (7, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'cream'), (7, '0123456789 !?.,:-+/x\'', 'cream'),
             (7, 'BONES 54/54  FETCH 2000  SECRETS 0/2', 'cream'), (7, 'TIME BONUS 4190  SCORE 6190', 'gold'),
             (7, 'NO HIT  ALL BONES  PAR 1:30  TIME 0:58.3', 'dim'), (7, 'PRESS ANY BUTTON', 'cream')]
    ims = []
    for size, s, st in lines:
        a = text(size, s, st)
        if st == 'ink':
            bg = np.zeros((a.shape[0] + 6, a.shape[1] + 10, 4), np.uint8); bg[...] = (246, 190, 62, 255)
            im = Image.fromarray(bg); im.alpha_composite(Image.fromarray(a), (5, 3)); a = np.array(im)
        ims.append(a)
    W = max(i.shape[1] for i in ims) + 8; Ht = sum(i.shape[0] + 3 for i in ims) + 6
    bg = Image.new('RGBA', (W, Ht), (64, 32, 22, 255)); y = 4
    for i in ims: bg.alpha_composite(Image.fromarray(i), (4, y)); y += i.shape[0] + 3
    bg.save(f'{out}/sheet_1x.png'); bg.resize((W * 5, Ht * 5), Image.NEAREST).save(f'{out}/sheet_5x.png'); print(W, Ht)
