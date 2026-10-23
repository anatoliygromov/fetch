"""tools/ui_card.py STEP FRAMES_DIR OUT_DIR SHOT [SHOT ...] [--target ref.png] [--qa qa.txt]: the gate card for a screen the
code composes (hud, pause, tally): the in-game frame (the first SHOT) in colour and greyscale at 2x, every other shot
at 2x, 5x crops of every placed body (from <shot>.txt, grouped by screen region), and the layout checks.
Also writes the side-by-side: the owner's target scaled down to 320 x 240 (a reference, BOX filter, for looking only)
next to our frame, both at 3x (sbs_<step>.png)."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
args = sys.argv[1:]
def opt(n):
    if n in args: i = args.index(n); v = args[i + 1]; del args[i:i + 2]; return v
target = opt('--target'); qa = opt('--qa')
step, D, OUT, shots = args[0], args[1], args[2], args[3:]
os.makedirs(OUT, exist_ok=True)
def font(s):
    try: return ImageFont.load_default(size=s)
    except TypeError: return ImageFont.load_default()
F, FB = font(16), font(24)
BG, TXT = (30, 30, 35), (232, 232, 236)
def z(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
def grey(im): g = im.convert('L'); return Image.merge('RGB', (g, g, g))
def boxes(shot):
    out = []
    for l in open(f'{D}/{shot}.txt'):
        p = l.split()
        if len(p) == 5: out.append((p[0], *map(int, p[1:])))
    return out

main = Image.open(f'{D}/{shots[0]}.png').convert('RGB')
# side by side
if target:
    t = Image.open(target).convert('RGB').resize((320, 240), Image.BOX)
    sbs = Image.new('RGB', (960 * 2 + 30, 720 + 50), BG); d = ImageDraw.Draw(sbs)
    sbs.paste(z(t, 3), (10, 40)); sbs.paste(z(main, 3), (960 + 20, 40))
    d.text((10, 8), f'TARGET (owner render, scaled to 320 x 240 for reference)', font=F, fill=TXT)
    d.text((980, 8), f'OURS: the game frame ({shots[0]}), 3x', font=F, fill=TXT)
    sbs.save(f'{OUT}/sbs_{step}.png'); print(f'{OUT}/sbs_{step}.png')
# crops: the union box of the bodies in each region (top-left, top-centre, top-right, bottom ...), at 5x
regions = {}
HUDN = {'health', 'clock', 'time', 'bone', 'bones', 'score', 'head', 'lives', 'hard'}
for name, x0, y0, x1, y1 in boxes(shots[0]):
    if step != 'hud' and name in HUDN: continue                        # (the HUD under the dim)
    key = ('T' if y0 < 80 else 'B' if y0 > 160 else 'M') + ('L' if x1 < 110 else 'R' if x0 > 210 else 'C')
    r = regions.setdefault(key, [x0, y0, x1, y1]); r[0] = min(r[0], x0); r[1] = min(r[1], y0); r[2] = max(r[2], x1); r[3] = max(r[3], y1)
crops = []
for key, (x0, y0, x1, y1) in sorted(regions.items()):
    c = main.crop((max(0, x0 - 3), max(0, y0 - 3), min(320, x1 + 5), min(240, y1 + 5)))
    if c.width * 5 > 1900: c = c.crop((0, 0, 1900 // 5, c.height))
    crops.append((key, z(c, 5)))
lines = [l.rstrip() for l in open(qa)] if qa else []
others = [Image.open(f'{D}/{s}.png').convert('RGB') for s in shots[1:]]
W = 1960
H = 60 + 480 + 30 + sum(c.height + 30 for _, c in crops) + (((len(others) + 2) // 3) * 500 if others else 0) + 22 * len(lines) + 60
card = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(card); y = 10
d.text((10, y), f'UI v8 · {step} · in-game frame {shots[0]} (colour, greyscale, 2x) · 5x crops of every placed body · layout checks', font=FB, fill=TXT); y += 40
card.paste(z(main, 2), (10, y)); card.paste(z(grey(main), 2), (660, y)); y += 490
for key, c in crops:
    d.text((10, y), f'5x: {key}', font=F, fill=TXT); y += 22; card.paste(c, (10, y)); y += c.height + 8
for i, (s, im) in enumerate(zip(shots[1:], others)):
    if i % 3 == 0 and i: y += 500
    d.text((10 + (i % 3) * 650, y), s, font=F, fill=TXT); card.paste(z(im, 2), (10 + (i % 3) * 650, y + 20))
if others: y += 500
for l in lines:
    d.text((10, y), l, font=F, fill=(90, 200, 110) if l.startswith('PASS') or l == 'ALL PASS' else (235, 70, 70) if 'FAIL' in l else TXT); y += 22
card = card.crop((0, 0, W, y + 20)); card.save(f'{OUT}/card_{step}.png'); print(f'{OUT}/card_{step}.png')
