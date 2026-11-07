#!/usr/bin/env python3
"""fix_gritbox_07nov.py: the grit box in its old greens (day/07nov-ground, 0 credits).

The owner, 7 Nov board, gritbox_front_06n: "Green sand box was better in terms of colors". The 6 Nov audit rebuilt
the box front-on as pine (tools/fix_rw_audit_06nov.py gritbox()) because the old green chest had a 3/4 side face and
read as a dumpster. That fix stays (front-on, a front and a thin cap: BIBLE), and the colours go back: every pine
colour of the built box maps by rule to the old box's forest-green ramp, read from
art/source/gritbox_front/gritbox_front_before_06nov_audit.png (lid #739e6c lip, #4c754c, #3f6540; body #335437,
shade #29482f, gaps #132117, batten light #648a61). The iron hasp and the 1 px ink stay. Same 88 x 32 slot and box.

  python3 -I tools/fix_gritbox_07nov.py           # writes the png, the .aseprite and edits.json "07nov_green"
  python3 -I tools/fix_gritbox_07nov.py --check   # the game file equals the build
"""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import aseprite_io
from fix_rw_audit_06nov import gritbox, hx

SCENE = 'riverwalk/art/scene'
KEY = '07nov_green'
PINE = dict(LIT=hx('d8a868'), BASE=hx('b8844c'), SHADE=hx('8c6038'), GAP=hx('5c3c24'))
LID = {PINE['LIT']: hx('739e6c'), PINE['BASE']: hx('4c754c'), PINE['SHADE']: hx('3f6540')}       # rows 1-5
BODY = {PINE['LIT']: hx('3f6540'), PINE['BASE']: hx('335437'), PINE['SHADE']: hx('29482f'), PINE['GAP']: hx('132117')}
BATTEN_LIT = hx('648a61')                                              # the battens' lit left columns (x 3 and 80)


def build():
    a = gritbox()
    out = a.copy()
    H, W = a.shape[:2]
    for y in range(H):
        for x in range(W):
            if not a[y, x, 3]: continue
            c = tuple(int(v) for v in a[y, x, :3])
            if y <= 5: m = LID
            else: m = BODY
            to = m.get(c)
            if y >= 8 and c == PINE['LIT'] and x in (3, 80): to = BATTEN_LIT
            if to: out[y, x, :3] = to
    return out


def main():
    new = build()
    p = f'{SCENE}/gritbox_front.png'
    if '--check' in sys.argv:
        cur = np.array(Image.open(p).convert('RGBA'))
        ok = cur.shape == new.shape and not (cur != new).any()
        print('gritbox_front', 'OK' if ok else 'DIFFERS'); sys.exit(0 if ok else 1)
    old = np.array(Image.open(p).convert('RGBA'))
    d = 'art/source/gritbox_front'
    J = json.load(open(f'{d}/edits.json'))
    ed = [{'x': int(x), 'y': int(y), 'from': old[y, x].tolist(), 'to': new[y, x].tolist(),
           'why': 'owner 7 Nov: the green box was better in colour; pine ramp mapped to the old green ramp by rule'}
          for y, x in zip(*np.nonzero((old != new).any(-1)))]
    J[KEY] = {'rule': 'tools/fix_gritbox_07nov.py: fix_rw_audit_06nov.gritbox() with LID / BODY / BATTEN_LIT colour maps',
              'pixels': ed}
    json.dump(J, open(f'{d}/edits.json', 'w'), indent=0)
    aseprite_io.write(f'{d}/gritbox_front.aseprite', [new], layer='gritbox_front')
    Image.fromarray(new, 'RGBA').save(p)
    print('gritbox_front', len(ed), 'pixels, colours', len(np.unique(new[new[..., 3] > 0][:, :3], axis=0)))


if __name__ == '__main__':
    main()
