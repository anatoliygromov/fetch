#!/usr/bin/env python3
"""check_backdrop.py [LEVEL ...]: back-layer buildings and front-row trees must be taller than the viewport, so their
top is never on screen (owner, 25 Oct; art/gen/rules.json taller_than_viewport). Reads the decor props of the flat
level files (riverwalk/level/*.lua) and fails any listed art whose top y0 is inside the screen (y0 > max_top_y).
Levels drawn by scene code (City Park, Downtown, the tall levels) are checked by eye in their screen sweep
(LOOK_SWEEP=1 ... --lookshots) until their art moves to decor props. Exit 1 on any failure."""
import sys, re, json, glob, os

R = json.load(open('art/gen/rules.json'))['taller_than_viewport']
files = [f'riverwalk/level/{l}.lua' for l in sys.argv[1:]] or sorted(glob.glob('riverwalk/level/*.lua'))
bad = 0
for f in files:
    for i, line in enumerate(open(f), 1):
        if 'decor' not in line or 'art' not in line: continue
        a = re.search(r'art\s*=\s*"([^"]+)"', line); y = re.search(r'y0\s*=\s*(-?\d+)', line)
        if not a or not y: continue
        art, y0 = a.group(1), int(y.group(1))
        if art in R['exempt']: continue
        if art in R['arts'] or any(h in art for h in R['name_hints']):
            x = re.search(r'x0\s*=\s*(-?\d+)', line)
            ok = y0 <= R['max_top_y']
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {os.path.basename(f)}:{i} {art} at x {x.group(1) if x else '?'}: top y {y0}"
                  + ('' if ok else f" is on screen; it must be {R['max_top_y']} or above (taller than the viewport)"))
print(f"\n{'BACKDROP OK' if not bad else f'BACKDROP FAIL: {bad} piece(s) show their top'}")
sys.exit(1 if bad else 0)
