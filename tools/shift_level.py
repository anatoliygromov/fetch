#!/usr/bin/env python3
"""Open a gap in a level to insert new screens: every x at or right of CUT moves DELTA px to the right.

  python3 tools/shift_level.py <level name> <cut x> <delta> [<test file> ...]

- level/<name>.lua: the x-like fields (x, x0, x1, ax, bx0, bx1, zoneX0, zoneX1, endX, from, to), the pairs
  call = { a, b } and rope = { a, b }, and `local FX = n`. Lines that are only comments are left alone.
- level/<name>.map: DELTA/8 columns are inserted at column CUT/8, copying the column just left of the cut
  (so the ground runs on; the new screens' own terrain is drawn afterwards with tools/edit_map.py or by hand).
- test files: x literals in the autopilot / physics patterns: p.x >= n (any comparison), tp(n, ...), x0 >= n,
  .x < n, `spots = { ... }`, and `s.girl.x`-free literals in at(...) conditions. Check the tests afterwards.
DELTA must be a multiple of 8 (one map cell)."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = r'(?:x|x0|x1|ax|bx0|bx1|zoneX0|zoneX1|endX|from|to)'

def sh(v, cut, d): return v + d if v >= cut else v

def shift_lua(path, cut, d):
    out = []
    for line in open(path).read().split('\n'):
        if line.strip().startswith('--'): out.append(line); continue
        code, sep, com = line.partition('--')
        code = re.sub(r'\b(' + KEYS + r')(\s*=\s*)(-?\d+)', lambda m: m.group(1) + m.group(2) + str(sh(int(m.group(3)), cut, d)), code)
        code = re.sub(r'\b(call|rope)(\s*=\s*\{\s*)(-?\d+)(\s*,\s*)(-?\d+)', lambda m: m.group(1) + m.group(2) + str(sh(int(m.group(3)), cut, d)) + m.group(4) + str(sh(int(m.group(5)), cut, d)), code)
        code = re.sub(r'^(local FX = )(\d+)', lambda m: m.group(1) + str(sh(int(m.group(2)), cut, d)), code)
        out.append(code + sep + com)
    open(path, 'w').write('\n'.join(out))

def shift_map(path, cut, d):
    assert d % 8 == 0 and cut % 8 == 0
    rows = [r for r in open(path).read().split('\n') if r]
    c, n = cut // 8, d // 8
    rows = [r[:c] + r[c - 1] * n + r[c:] for r in rows]
    open(path, 'w').write('\n'.join(rows) + '\n')

def shift_test(path, cut, d):
    s = open(path).read()
    f = lambda m: m.group(1) + str(sh(int(m.group(2)), cut, d))
    s = re.sub(r'(p\.x\s*[<>]=?\s*)(\d{3,4})\b', f, s)
    s = re.sub(r'(\.x0\s*[<>]=?\s*)(\d{3,4})\b', f, s)
    s = re.sub(r'(tp\()(\d{2,4})\b', f, s)
    s = re.sub(r'(local spots = \{)([^}]*)\}', lambda m: m.group(1) + re.sub(r'\d+', lambda k: str(sh(int(k.group(0)), cut, d)), m.group(2)) + '}', s)
    open(path, 'w').write(s)

if __name__ == '__main__':
    name, cut, d = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    shift_lua(os.path.join(ROOT, 'riverwalk', 'level', name + '.lua'), cut, d)
    shift_map(os.path.join(ROOT, 'riverwalk', 'level', name + '.map'), cut, d)
    for t in sys.argv[4:]: shift_test(t, cut, d)
    print('shifted', name, 'at', cut, 'by', d)
