import numpy as np
from PIL import Image
from scipy import ndimage
import sys; sys.path.insert(0, '/tmp/claude-0/ui/v5'); sys.path.insert(0, '/tmp/claude-0/ui/v4')
from glyphs import G
from restyle import style, STYLES
def glyph(ch, st):
    m = np.array([[c == '#' for c in r] for r in G[ch]]); return style(m, st, 0, 12)
def text(t, st='cream', gap=1, space=5):
    ims = []
    for ch in t:
        if ch == ' ': ims.append(None); continue
        k = ch if ch in G else ch.upper()
        if k not in G: ims.append(None); continue
        ims.append(glyph(k, st))
    h = max(a.shape[0] for a in ims if a is not None); adv = lambda a: a.shape[1] - 4 + gap   # 4 = pad on both sides minus 1 px outline each
    w = sum(adv(a) if a is not None else space for a in ims) + 4; o = np.zeros((h, w, 4), np.uint8); x = 0
    for a in ims:
        if a is None: x += space; continue
        im = Image.fromarray(o); im.alpha_composite(Image.fromarray(a), (x, 0)); o = np.array(im); x += adv(a)
    return o
if __name__ == "__main__":
    lines = [('ABCDEFGHIJKLM', 'gold'), ('NOPQRSTUVWXYZ', 'gold'), ('0123456789 !?.:-/+x', 'gold'), ('PAUSED  GO ON  SOUND  QUIT', 'cream'),
             ('RIVER WALK  CITY PARK  DOWNTOWN', 'cream'), ('ROOFTOPS  SODER HILL  NIGHT HARBOUR', 'dim'), ('300  12/97  x3  007840', 'gold')]
    ims = [text(t, s) for t, s in lines]; W = max(i.shape[1] for i in ims) + 8; Ht = sum(i.shape[0] + 3 for i in ims) + 6
    bg = np.zeros((Ht, W, 4), np.uint8); bg[...] = (64, 32, 22, 255); y = 4
    for i in ims:
        im = Image.fromarray(bg); im.alpha_composite(Image.fromarray(i), (4, y)); bg = np.array(im); y += i.shape[0] + 3
    Image.fromarray(bg).resize((W * 5, Ht * 5), Image.NEAREST).save('/tmp/claude-0/ui/v5/sheet_5x.png'); print(W, Ht)
