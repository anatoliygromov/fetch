#!/usr/bin/env python3
"""fix_cp_winch.py: the board's fix call on park_keeper_winch (owner, 25 Oct: "a colour lost in one frame"), by hand
rule, no automated clean pass (art/cp-built-06nov, 6 Nov 2026, 0 credits).

  python3 -I tools/fix_cp_winch.py   -> riverwalk/art/scene/park_keeper_winch.png (640 x 80, 8 frames of 80 x 80),
                                        art/source/park_keeper_winch/{edits.json, park_keeper_winch.aseprite, _old.png}

What asset_qa found: the coat's deepest green #101a10 is in 7 of the 8 frames (1 to 12 loose pixels a frame, none in
frame 3), and a near-ink #312f2a sits as one pixel in frames 4 and 5 only: colours that come and go between frames
flicker. Both are single pixels inside the coat or at the winch, never a shape of their own. The rule, per pixel:
  #101a10  touching the outside (a transparent 4-neighbour): the ink #040302 (the outline stays whole);
           else touching the coat (#3f603e or #28442c): the coat's dark #28442c;
           else: the 4-neighbour colour nearest in RGB.
  #312f2a  the 4-neighbour colour nearest in RGB.
Every changed pixel is written to edits.json. Afterwards every colour is in all 8 frames."""
import os, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
F = 'riverwalk/art/scene/park_keeper_winch.png'
D = 'art/source/park_keeper_winch'; os.makedirs(D, exist_ok=True)
OLD = f'{D}/park_keeper_winch_old.png'
if not os.path.exists(OLD): Image.open(F).save(OLD)
src = np.array(Image.open(OLD).convert('RGBA')); a = src.copy()
h, w = a.shape[:2]
hexs = lambda p: '#%02x%02x%02x%02x' % tuple(int(v) for v in p)
col = lambda s: np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)])
INK, COAT_DK = col('040302'), col('28442c'); COAT = [col('3f603e'), col('28442c')]
edits = []
for bad, rule in (('101a10', 'coat'), ('312f2a', 'near')):
    c = col(bad)
    ys, xs = np.nonzero((src[..., :3] == c).all(-1) & (src[..., 3] > 0))
    for y, x in zip(ys, xs):
        nb = [src[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
              if 0 <= y + dy < h and (x + dx) // 80 == x // 80 and 0 <= x + dx < w]
        opaque = [n for n in nb if n[3] > 0 and not (n[:3] == c).all() and not (n[:3] == col('101a10')).all()]
        if rule == 'coat' and any(n[3] == 0 for n in nb): new = INK
        elif rule == 'coat' and any((n[:3] == k).all() for n in opaque for k in COAT): new = COAT_DK
        else: new = min(opaque, key=lambda n: ((n[:3].astype(int) - c) ** 2).sum())[:3]
        a[y, x, :3] = new
        edits.append([int(x), int(y), hexs(a[y, x]), f'was #{bad}, frame {x // 80 + 1}'])
Image.fromarray(a, 'RGBA').save(F); Image.fromarray(a, 'RGBA').save(f'{D}/park_keeper_winch.png')
frames = [a[:, i * 80:(i + 1) * 80] for i in range(8)]
aseprite_io.write(f'{D}/park_keeper_winch.aseprite', frames, ms=100, layer='park_keeper_winch')
json.dump({'asset': 'park_keeper_winch', 'base': OLD, 'method': 'hand rule (tools/fix_cp_winch.py), no clean pass',
           'changed': len(edits), 'pixels': edits}, open(f'{D}/edits.json', 'w'), indent=0)
sets = [set(map(tuple, f[f[..., 3] > 0][:, :3])) for f in frames]
print('changed', len(edits), 'pixels; colours per frame', [len(s) for s in sets], '; in every frame:', len(set.intersection(*sets)), 'of', len(set.union(*sets)))
