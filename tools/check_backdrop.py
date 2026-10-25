#!/usr/bin/env python3
"""check_backdrop.py [LEVEL ...]: back-layer buildings and front-row trees must be taller than the viewport, so their
top is never on screen (owner, 25 Oct; art/gen/rules.json taller_than_viewport). Reads the decor props of the flat
level files (riverwalk/level/*.lua) and measures each listed art as the game draws it (scene.lua Sc.drawProp: the
image's bottom on the prop's ay or y1, so its top is that minus the image's height; the prop's y0 is not used):
  a building (any listed art not in "trees") fails when the top of ANY of its columns is on screen (y > max_top_y):
  a gable's steps or a roof's slope seen against the sky is its top seen;
  a tree (rules "trees") fails when its highest pixel is on screen: the crown is cut by the top edge, its sides may
  come down into the picture.
(night/25oct-fixes: the check read the prop's declared y0, so the old gable passed with 58 of its 70 columns topped on
screen; rw_home and rw_lime were not listed.) Levels drawn by scene code (City Park, Downtown, the tall levels) are
checked by eye in their screen sweep (LOOK_SWEEP=1 ... --lookshots) until their art moves to decor props.
Exit 1 on any failure."""
import sys, re, json, glob, os
import numpy as np
from PIL import Image

R = json.load(open('art/gen/rules.json'))['taller_than_viewport']
TREES = set(R.get('trees', []))
files = [f'riverwalk/level/{l}.lua' for l in sys.argv[1:]] or sorted(glob.glob('riverwalk/level/*.lua'))
bad = 0


def num(k, line):
    m = re.search(r'\b' + k + r'\s*=\s*(-?\d+)', line)            # (whole keys: ay, not delay)
    return int(m.group(1)) if m else None


for f in files:
    for i, line in enumerate(open(f), 1):
        if 'decor' not in line or 'art' not in line: continue
        a = re.search(r'art\s*=\s*"([^"]+)"', line)
        if not a: continue
        art = a.group(1)
        if art in R['exempt']: continue
        if not (art in R['arts'] or any(h in art for h in R['name_hints'])): continue
        y1, ay, x0 = num('y1', line), num('ay', line), num('x0', line)
        p = f'riverwalk/art/scene/{art}.png'
        if y1 is None or not os.path.exists(p):
            bad += 1; print(f"FAIL {os.path.basename(f)}:{i} {art}: no y1 or no {p}"); continue
        op = np.array(Image.open(p).convert('RGBA'))[..., 3] > 0
        top = (ay if ay is not None else y1) - op.shape[0]            # the image's top row on screen
        cols = [top + int(np.argmax(op[:, x])) for x in range(op.shape[1]) if op[:, x].any()]
        if art in TREES:
            worst, n_on, kind = min(cols), int(min(cols) > R['max_top_y']), 'tree'
        else:
            worst, kind = max(cols), 'building'
            n_on = sum(c > R['max_top_y'] for c in cols)
        ok = n_on == 0
        bad += not ok
        what = (f"highest pixel at y {worst}" if kind == 'tree' else f"lowest column top at y {worst}")
        print(f"{'ok  ' if ok else 'FAIL'} {os.path.basename(f)}:{i} {art} ({kind}) at x {x0}: {what}"
              + ('' if ok else (f", {n_on} of {len(cols)} columns show their top" if kind == 'building' else '')
                 + f"; it must be {R['max_top_y']} or above (taller than the viewport)"))
print(f"\n{'BACKDROP OK' if not bad else f'BACKDROP FAIL: {bad} piece(s) show their top'}")
sys.exit(1 if bad else 0)
