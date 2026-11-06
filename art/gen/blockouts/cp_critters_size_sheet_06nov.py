"""Size sheet for the cp_critters family (6 Nov, the producer's ask): the finished magpie (perched and flying) and the
duck boat, each beside Pepper's real sprite at 1x, as the game draws them (feet / deck on one line); 1x and 4x.
Writes docs/review/06nov/cp_critters/size_sheet.png (4x, with labels) and size_sheet_1x.png.
Run from the repo root: python3 art/gen/blockouts/cp_critters_size_sheet_06nov.py"""
import sys
sys.path.insert(0, 'tools')
from PIL import Image, ImageDraw
from blockout_lib import pepper

OUT = 'docs/review/06nov/cp_critters/'
SKY, PAVE, EDGE = (196, 214, 232, 255), (226, 206, 170, 255), (180, 160, 128, 255)
pep = pepper(); mag = Image.open('riverwalk/art/magpie.png').convert('RGBA'); boat = Image.open('riverwalk/art/scene/cp_duckboat.png').convert('RGBA')
ball = Image.open('riverwalk/art/ball.png').convert('RGBA')
W, H, G = 330, 76, 66
im = Image.new('RGBA', (W, H), SKY); d = ImageDraw.Draw(im)
d.rectangle([0, G, W, H], fill=PAVE); d.line([(0, G), (W, G)], fill=EDGE)
labels = []
x = 4
im.alpha_composite(pep, (x, G - pep.height)); labels.append((x, 'Pepper 38 tall, 52 long')); x += pep.width + 6
fx = x + 20                                                        # magpie feet (cell 20, 25) on the line
im.alpha_composite(mag.crop((0, 0, 32, 26)), (fx - 20, G - 25)); im.alpha_composite(ball, (fx + 12 - 3, G - 9 - 6))
labels.append((x, 'magpie 30 x 18')); x += 40
im.alpha_composite(mag.crop((64, 0, 96, 26)), (x, G - 25 - 20)); labels.append((x, 'flying, 30 x 22')); x += 44
im.alpha_composite(boat, (x, G - 41))                             # deck (row 41) on the line
im.alpha_composite(pep, (x + 40, G - pep.height)); labels.append((x, 'duck boat 92 x 60 (2 m), Pepper on its deck'))
im = im.crop((0, 0, x + 100, H))
im.convert('RGB').save(OUT + 'size_sheet_1x.png')
S = 4
sheet = Image.new('RGB', (im.width * S, im.height * S + 40 + im.height + 8), (30, 30, 34))
ds = ImageDraw.Draw(sheet)
ds.text((8, 6), 'cp_critters at true game size beside Pepper\'s real sprite: 4x (top) and 1x (bottom). Feet and deck on one line.', fill=(240, 240, 240))
sheet.paste(im.convert('RGB').resize((im.width * S, im.height * S), Image.NEAREST), (0, 30))
for lx, lab in labels:
    ds.rectangle([lx * S, 30, lx * S + 7 * len(lab) + 6, 44], fill=(30, 30, 34)); ds.text((lx * S + 3, 31), lab, fill=(255, 230, 120))
sheet.paste(im.convert('RGB'), (8, 30 + im.height * S + 6))
sheet.save(OUT + 'size_sheet.png')
print('written', OUT + 'size_sheet.png')
