#!/usr/bin/env python3
"""revert_ground_07nov.py: put back what the owner liked better (day/07nov-ground, 0 credits).

Owner, 7 Nov board: park_ground_06n "was better before", park_stone_06n "prev was better", pontoon_06n "previous pontoon
was better". Each game file goes back, pixel for pixel, to the version the board showed as "before", which the 6 Nov
fix scripts saved next to the source:

  park_ground  art/source/park_ground/park_ground_pre_audit.png   (before tools/fix_cp_audit.py ground, 7758418)
  park_stone   art/source/park_stone/park_stone_pre_audit.png     (the pink granite cut at the water, before b342d56)
  pontoon      art/source/pontoon/pontoon_before_06nov_audit.png  (the 54 x 12 slab on two floats, before 64b0d31)

The road (road.png) goes back by its own script: tools/make_road.py as it was before 8f91328 (rebuilds the textured
road pixel for pixel). The grit box: tools/fix_gritbox_07nov.py (front-on kept, old greens back).

Each revert writes the .aseprite source and an edits.json entry "07nov_revert" (the file it came from, the reason);
the replaced 6 Nov file is kept as art/source/NAME/NAME_06nov_rejected.png.

  python3 -I tools/revert_ground_07nov.py           # do it (idempotent)
  python3 -I tools/revert_ground_07nov.py --check   # each game file equals its restored source
"""
import sys, os, json, shutil
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

SCENE = 'riverwalk/art/scene'
KEY = '07nov_revert'
REVERTS = {
    'park_ground': ('park_ground_pre_audit.png', 'owner 7 Nov: "was better before" (the 6 Nov flat bands rejected)'),
    'park_stone': ('park_stone_pre_audit.png', 'owner 7 Nov: "prev was better" (the 6 Nov grey recolour rejected)'),
    'pontoon': ('pontoon_before_06nov_audit.png', 'owner 7 Nov: "previous pontoon was better" (the 6 Nov mahogany deck rejected)'),
}


def rgba(p): return np.array(Image.open(p).convert('RGBA'))


def main():
    check = '--check' in sys.argv
    bad = 0
    for n, (src, why) in REVERTS.items():
        d = f'art/source/{n}'
        want = rgba(f'{d}/{src}')
        game = f'{SCENE}/{n}.png'
        cur = rgba(game)
        same = cur.shape == want.shape and not (cur != want).any()
        if check:
            print(n, 'OK' if same else 'DIFFERS'); bad += not same; continue
        if same: print(n, 'already restored'); continue
        shutil.copy(game, f'{d}/{n}_06nov_rejected.png')
        Image.fromarray(want, 'RGBA').save(game)
        if os.path.exists(f'{d}/{n}.png'): Image.fromarray(want, 'RGBA').save(f'{d}/{n}.png')
        aseprite_io.write(f'{d}/{n}.aseprite', [want], layer=n)
        p = f'{d}/edits.json'
        J = json.load(open(p)) if os.path.exists(p) else {'name': n}
        J[KEY] = {'from': src, 'size': [int(want.shape[1]), int(want.shape[0])], 'why': why,
                  'kept': f'{n}_06nov_rejected.png (the rejected 6 Nov file)'}
        json.dump(J, open(p, 'w'), indent=0)
        print(n, 'restored from', src, want.shape[1], 'x', want.shape[0])
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
