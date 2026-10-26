"""Size options for the gull and cat redraws (night of 25 Oct): grey blockouts beside Pepper's real sprite at 1x, for
the owner's next spend line. Board, 25 Oct 20:16: gull_v3 redraw, "the gull needs to be smaller too" (it was 44 px
span; 58 px was "massive", he picked about 40); cat_v2 redraw, "the cat needs to be bigger, slightly smaller than the
dog" (it was 16 px sitting). Pepper: 52 px nose to tail, 38 px to the top of her head (rules.json pepper).
Shapes are the blockout shapes of art/gen/blockouts/dt_cat.py and rw_gull.py (art/animals) drawn at each option's
size; nothing here is game art and no pixel of a rejected sprite is reused.
Writes docs/review/25oct-night/prep/animals_sizes_1x.png and animals_sizes_4x.png (labels in the margin).
Run from the repo root: python3 art/gen/blockouts/animals_sizes_25oct.py"""
import sys
sys.path.insert(0, 'tools')
from PIL import Image, ImageDraw
from blockout_lib import pepper

OUT = 'docs/review/25oct-night/prep/'
SKY, PAVE, EDGE = (196, 214, 232, 255), (226, 206, 170, 255), (180, 160, 128, 255)
COAT, EAR, DARK = (150, 150, 158, 255), (120, 120, 128, 255), (90, 90, 98, 255)
BODY, WING, TIP = (200, 200, 206, 255), (140, 140, 150, 255), (80, 80, 90, 255)
CATS = [('now', 16, 'rejected 20:16 (16 px)'), ('A', 27, 'A 27 px (70 %)'), ('B', 30, 'B 30 px (80 %)'), ('C', 34, 'C 34 px (90 %)')]
GULLS = [('now', 44, 'rejected 20:16 (44 px)'), ('A', 36, 'A 36 px'), ('B', 32, 'B 32 px'), ('C', 28, 'C 28 px')]


def cat_sit(d, x0, g, h):
    """Sitting cat facing right, h px to the ear tips (dt_cat.py's shapes, which are 15 px tall, at scale k)."""
    k = h / 15.0
    X = lambda v: x0 + round(v * k); Y = lambda v: g - round(v * k)
    d.ellipse([X(0), Y(10), X(8), Y(1)], fill=COAT)
    d.rectangle([X(5), Y(11), X(8), Y(1)], fill=COAT)
    d.ellipse([X(4), Y(15), X(11), Y(9)], fill=COAT)
    d.polygon([(X(5), Y(13)), (X(6), Y(15)), (X(7), Y(13))], fill=EAR)
    d.polygon([(X(8), Y(13)), (X(10), Y(15)), (X(10), Y(12))], fill=EAR)
    d.line([(X(0), Y(1)), (X(-1), Y(4))], fill=COAT, width=max(2, round(2 * k)))


def cat_run(d, x0, g, h):
    """The same cat stretched out running, nose to rump about 1.4 x its sitting height, tail behind."""
    L = round(1.4 * h); bh = max(4, round(0.32 * h)); top = g - round(0.62 * h)
    d.ellipse([x0, top, x0 + L - round(0.25 * h), top + bh], fill=COAT)                  # body
    hx = x0 + L - round(0.32 * h); hs = round(0.3 * h)
    d.ellipse([hx, top - round(0.15 * h), hx + hs, top - round(0.15 * h) + hs], fill=COAT)   # head
    lw = max(2, round(0.08 * h))
    for fx, bx in ((x0 + round(0.15 * h), -1), (x0 + L - round(0.45 * h), 1)):      # legs, reaching
        d.line([(fx, top + bh - 1), (fx + bx * round(0.18 * h), g - 1)], fill=DARK, width=lw)
    d.line([(x0, top + 2), (x0 - round(0.45 * h), top - round(0.1 * h))], fill=COAT, width=lw)   # tail
    return L


def gull(d, cx, cy, span):
    """Gliding gull facing right, `span` px wing tip to wing tip (rw_gull.py's shapes, which span 40 px, at scale k)."""
    k = span / 40.0
    P = lambda x, y: (cx + round(x * k), cy + round(y * k))
    d.ellipse([*P(-9, -3), *P(9, 3)], fill=BODY)
    d.ellipse([*P(5, -5), *P(11, 0)], fill=BODY)
    d.polygon([P(-9, -1), P(-13, -3), P(-13, 1)], fill=BODY)
    d.polygon([P(-3, -2), P(-20, -12), P(-22, -10), P(-1, 1)], fill=WING)
    d.polygon([P(1, -2), P(16, -11), P(18, -9), P(3, 1)], fill=WING)
    d.polygon([P(-18, -11), P(-22, -13), P(-22, -9)], fill=TIP)
    d.polygon([P(14, -10), P(18, -12), P(18, -8)], fill=TIP)


pep = pepper()
W, H = 640, 170
G1, G2 = 66, 166                                   # ground lines of the cat row and the gull row
im = Image.new('RGBA', (W, H), SKY)
d = ImageDraw.Draw(im)
for g in (G1, G2):
    d.rectangle([0, g, W, g + 3], fill=PAVE); d.line([(0, g), (W, g)], fill=EDGE)
labels = []
x = 6
for i, (key, h, lab) in enumerate(CATS):           # cat row: Pepper, then the cat sitting and running
    im.alpha_composite(pep, (x, G1 - pep.height))
    cat_sit(d, x + pep.width + 4, G1, h)
    rx = x + pep.width + 4 + round(0.75 * h) + 8 + round(0.45 * h)       # the running cat, its tail clear of the sitting one
    L = cat_run(d, rx, G1, h)
    labels.append((x, 2, lab))
    x = rx + L + 16
x = 6
for key, span, lab in GULLS:                       # gull row: Pepper with the gull over her, at swoop height
    im.alpha_composite(pep, (x, G2 - pep.height))
    gull(d, x + pep.width // 2 + 4, G2 - pep.height - 14, span)
    labels.append((x, 76, lab))
    x += max(pep.width, span) + 70
im.convert('RGB').save(OUT + 'animals_sizes_1x.png')
S = 4
big = im.convert('RGB').resize((W * S, H * S), Image.NEAREST)
sheet = Image.new('RGB', (W * S, H * S + 60), (30, 30, 34)); sheet.paste(big, (0, 60))
ds = ImageDraw.Draw(sheet)
ds.text((8, 6), 'Gull and cat redraw: size options beside Pepper (52 px long, 38 px tall), grey blockouts, 4x. '
        'Cat: % of her height, sitting and running. Gull: wingspan.', fill=(240, 240, 240))
ds.text((8, 26), 'Board 20:16: gull "smaller too" (was 44 px); cat "bigger, slightly smaller than the dog" (was 16 px).',
        fill=(240, 240, 240))
for lx, ly, lab in labels:
    ds.rectangle([lx * S, 60 + ly * S, lx * S + 7 * len(lab) + 6, 60 + ly * S + 14], fill=(30, 30, 34))
    ds.text((lx * S + 3, 60 + ly * S + 2), lab, fill=(255, 230, 120))
sheet.save(OUT + 'animals_sizes_4x.png')
print('written', OUT + 'animals_sizes_1x.png', OUT + 'animals_sizes_4x.png')
