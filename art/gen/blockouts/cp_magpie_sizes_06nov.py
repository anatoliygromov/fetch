"""Size options for the City Park magpie (6 Nov), after animals_sizes_25oct.py: grey blockouts beside Pepper's real
sprite at 1x, with the owner's sized animals of 25 Oct beside them (branch art/animals-r2: the cat 32 px sitting,
the gull 34 px span, about 32 px beak to tail) and the girl's ball (6 px) in the beak.
A real magpie is about 0.45 m beak to tail, about half of it tail: 21 px at 46 px/m.
Options (beak tip to tail tip): A 24 px (the code magpie today), B 30 px, C 36 px.
Writes docs/review/06nov/cp_critters/magpie_sizes_1x.png and magpie_sizes_4x.png.
Run from the repo root: python3 art/gen/blockouts/cp_magpie_sizes_06nov.py"""
import sys, subprocess, io
sys.path.insert(0, 'tools')
from PIL import Image, ImageDraw
from blockout_lib import pepper

OUT = 'docs/review/06nov/cp_critters/'
SKY, PAVE, EDGE = (196, 214, 232, 255), (226, 206, 170, 255), (180, 160, 128, 255)
BODY, WHITE, TAIL, LEG = (70, 70, 78, 255), (210, 210, 216, 255), (110, 120, 130, 255), (60, 60, 66, 255)
OPTS = [('A', 24, 'A 24 px (today)'), ('B', 30, 'B 30 px (picked)'), ('C', 36, 'C 36 px')]


def magpie(d, x0, g, L):
    """Perched magpie facing right, L px from tail tip (x0) to beak tip, feet on g. Unit shapes for L = 30."""
    k = L / 30.0
    P = lambda x, y: (x0 + round(x * k), g - round(18 * k) + round(y * k))
    d.polygon([P(0, 14), P(2, 16), P(14, 10), P(12, 7)], fill=TAIL)            # the long tail, sloping down-back
    d.ellipse([*P(10, 4), *P(23, 13)], fill=BODY)                               # body
    d.ellipse([*P(19, 1), *P(26, 7)], fill=BODY)                                # head
    d.polygon([P(25, 3), P(30, 4), P(25, 5)], fill=LEG)                         # beak
    d.ellipse([*P(15, 8), *P(21, 12)], fill=WHITE)                              # white belly
    d.ellipse([*P(12, 5), *P(17, 8)], fill=WHITE)                               # white shoulder patch
    for lx in (16, 18):
        d.line([P(lx, 12), P(lx, 18)], fill=LEG, width=1)                       # legs
    return P(30, 4)


def r2(path):
    return Image.open(io.BytesIO(subprocess.check_output(['git', 'show', 'origin/art/animals-r2:' + path]))).convert('RGBA')


pep = pepper(); ball = Image.open('riverwalk/art/ball.png').convert('RGBA')
cat = r2('riverwalk/art/cat.png').crop((0, 0, 48, 48)); gull = r2('riverwalk/art/gull.png').crop((0, 0, 36, 44))
W, H = 560, 84
G = 76
im = Image.new('RGBA', (W, H), SKY)
d = ImageDraw.Draw(im)
d.rectangle([0, G, W, H], fill=PAVE); d.line([(0, G), (W, G)], fill=EDGE)
labels = []
x = 4
im.alpha_composite(pep, (x, G - pep.height)); x += pep.width + 4
im.alpha_composite(cat, (x - 6, G - 48)); labels.append((x - 2, 2, 'cat 32')); x += 40
im.alpha_composite(gull, (x - 2, G - 48)); labels.append((x, 2, 'gull 34 span')); x += 48
for key, L, lab in OPTS:
    im.alpha_composite(pep, (x, G - pep.height))
    bx, by = magpie(d, x + pep.width + 6, G, L)
    im.alpha_composite(ball, (bx - 2, by + 1))                                  # the ball hangs from the beak tip
    labels.append((x + pep.width + 2, 2, lab))
    x += pep.width + L + 30
im = im.crop((0, 0, x, H))
im.convert('RGB').save(OUT + 'magpie_sizes_1x.png')
S = 4
big = im.convert('RGB').resize((im.width * S, H * S), Image.NEAREST)
sheet = Image.new('RGB', (im.width * S, H * S + 44), (30, 30, 34)); sheet.paste(big, (0, 44))
ds = ImageDraw.Draw(sheet)
ds.text((8, 6), 'Magpie size options beside Pepper (38 px tall), the 25 Oct cat and gull, grey blockouts, 4x. '
        'Beak tip to tail tip; real 0.45 m = 21 px at 46 px/m.', fill=(240, 240, 240))
ds.text((8, 24), 'Picked B (30 px): the gull is about 32 px long, the cat 32 px sitting; B reads beside both.', fill=(240, 240, 240))
for lx, ly, lab in labels:
    ds.rectangle([lx * S, 44 + ly * S, lx * S + 7 * len(lab) + 6, 44 + ly * S + 14], fill=(30, 30, 34))
    ds.text((lx * S + 3, 44 + ly * S + 2), lab, fill=(255, 230, 120))
sheet.save(OUT + 'magpie_sizes_4x.png')
print('written', OUT + 'magpie_sizes_1x.png', OUT + 'magpie_sizes_4x.png')
