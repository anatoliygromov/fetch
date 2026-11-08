#!/usr/bin/env python3
"""fidelity_card.py CONCEPT HOLES OUT.png LABEL=frame.png ...: the fidelity gate (8 Nov). Each in-game frame (320x240,
shot at the concept's camera spot) is compared with the concept, cell by cell on the game grid: colour distance (CIELAB
dE, mean and 95th percentile) and edge overlap (how many of the concept's edges the frame keeps), leaving out where the
game draws its own sprites (Pepper, goose, bones, loose tiles). Writes a card: the panels at 3x in colour and greyscale,
the numbers under each, and prints them."""
import sys, numpy as np, cv2
from PIL import Image, ImageDraw
con_p, holes_p, out_p = sys.argv[1:4]
frames = [a.split('=', 1) for a in sys.argv[4:]]
con = Image.open(con_p).convert('RGB').resize((320, 240), Image.BOX)
skip = np.load(holes_p).copy()
for x in (4, 36, 68, 164, 196, 228): skip[134:144, x - 1:x + 25] = True          # the loose tiles
for (x0, y0) in ((40, 160), (200, 158)): skip[y0:y0 + 14, x0:x0 + 18] = True     # the bones in the skylight dips
lab = lambda im: cv2.cvtColor(np.asarray(im).astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
def edges(im):
    g = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY).astype(float)
    return (np.abs(np.diff(g, axis=1, append=g[:, -1:])) + np.abs(np.diff(g, axis=0, append=g[-1:]))) > 40
ce = edges(con) & ~skip
rows = []
panels = [('concept (Artlist)', con)] + [(n, Image.open(p).convert('RGB')) for n, p in frames]
for n, im in panels[1:]:
    d = np.linalg.norm(lab(im) - lab(con), axis=2)[~skip]
    fe = edges(im)
    keep = (ce & cv2.dilate(fe.astype(np.uint8), np.ones((3, 3))).astype(bool)).sum() / max(1, ce.sum())
    rows.append((n, d.mean(), np.percentile(d, 95), keep))
    print(f'{n:28s} colour distance mean {d.mean():5.2f}  95th {np.percentile(d, 95):5.1f}   concept edges kept {keep*100:5.1f}%')
S = 3; W, H = 320 * S, 240 * S; pad = 12; txt = 46
card = Image.new('RGB', (len(panels) * (W + pad) + pad, 2 * (H + pad) + txt + pad), (24, 24, 28))
dr = ImageDraw.Draw(card)
for i, (n, im) in enumerate(panels):
    x = pad + i * (W + pad)
    card.paste(im.resize((W, H), Image.NEAREST), (x, pad))
    card.paste(im.convert('L').convert('RGB').resize((W, H), Image.NEAREST), (x, pad + H + pad))
    label = n if i == 0 else f'{n}:  dE {rows[i-1][1]:.1f} (95th {rows[i-1][2]:.0f}),  edges kept {rows[i-1][3]*100:.0f}%'
    dr.text((x, 2 * (H + pad) + 10), label, fill=(235, 235, 235))
card.save(out_p); print('card', out_p)
