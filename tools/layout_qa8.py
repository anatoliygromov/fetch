"""tools/layout_qa8.py FRAMES_DIR [OUT_DIR]: the v6 layout checks (art/source/ui/v6_layout/tools/layout_qa.py) on the
game's real frames. tools/ui_frames.py writes each frame (<shot>.png, 320 x 240) and the bodies the UI placed in it
(<shot>.txt: name x0 y0 x1 y1, inclusive, shadows left out). Checks:
  every logged box is what was drawn: a text box's outline column holds the outline colour in the frame
  HUD: the top row on one centre line; the margins; icon to number 3 px; the time group centred; the score
       right-aligned under the bones; the bottom row on one line at the bottom margin; nothing overlaps
  pause: rows share x and width, even pitch; labels share one left edge and sit centred in their rows; the panel,
         the ribbon, the title and the subtitle centred; equal side padding; cursor to label 3 px; the A / B group
         centred; no text or icons overlapping
  tally: the panel, the ribbon and the title centred; each column's labels share a left edge and its values a right
         edge; even row pitch; medals and their labels on one line; nothing overlapping
  pieces: one outline colour (64,11,6) and one shadow colour (36,8,5) on every piece's edge (art/ui/*.png)
Writes guides (<shot>_guides_4x.png: green centre lines, magenta margins and the screen centre, cyan boxes) to
OUT_DIR and prints PASS / FAIL lines, then ALL PASS or SOME FAIL."""
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw
D = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = 4; INK = (64, 11, 6); SH = (36, 8, 5)
ok = True
def check(cond, msg):
    global ok; print(('PASS ' if cond else 'FAIL ') + msg); ok &= bool(cond)
HUDN = {'health', 'clock', 'time', 'bone', 'bones', 'score', 'head', 'lives', 'hard'}
def load(shot):
    boxes = []
    for line in open(f'{D}/{shot}.txt'):
        p = line.split()
        if len(p) == 5: boxes.append(dict(name=p[0], x0=int(p[1]), y0=int(p[2]), x1=int(p[3]), y1=int(p[4])))
    if not shot.startswith('hud'): boxes = [b for b in boxes if b['name'] not in HUDN]     # (the HUD under the dim)
    return np.array(Image.open(f'{D}/{shot}.png').convert('RGB')), boxes
def c(b): return ((b['x0'] + b['x1']) / 2, (b['y0'] + b['y1']) / 2)
def one(bs, n): r = [b for b in bs if b['name'] == n]; return r[0] if r else None
def many(bs, n): return [b for b in bs if b['name'] == n]
def overlaps(bs, skip=()):
    out = []
    items = [b for b in bs if b['name'] not in skip]
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if not (a['x1'] < b['x0'] or b['x1'] < a['x0'] or a['y1'] < b['y0'] or b['y1'] < a['y0']): out.append((a['name'], b['name']))
    return out
TEXT = {'time', 'bones', 'score', 'lives', 'label', 'title', 'subtitle', 'hint', 'tlabel', 'tvalue', 'mlabel', 'press', 'note', 'hard'}
def drawn(f, bs, shot):
    bad = []
    for b in bs:
        if b['name'] not in TEXT or b['name'] == 'title': continue          # (the title is ink, no outline)
        col = f[b['y0']:b['y1'] + 1, b['x0']]; row = f[b['y0'], b['x0']:b['x1'] + 1]
        if not (np.all(col == INK, axis=1).any() and np.all(row == INK, axis=1).any()): bad.append(b['name'])
    check(not bad, f'{shot}: every logged text box matches the drawn outline {bad[:5]}')
def guides(f, bs, shot, lines=()):
    S = 4; im = Image.fromarray(f).resize((320 * S, 240 * S), Image.NEAREST); d = ImageDraw.Draw(im)
    for x in (M, 319 - M, 159.5): d.line([(x * S + 2, 0), (x * S + 2, 240 * S)], fill=(255, 0, 255))
    for y in (M, 239 - M): d.line([(0, y * S + 2), (320 * S, y * S + 2)], fill=(255, 0, 255))
    for y in lines: d.line([(0, y * S + 2), (320 * S, y * S + 2)], fill=(0, 255, 0))
    for b in bs: d.rectangle([b['x0'] * S, b['y0'] * S, b['x1'] * S + S - 1, b['y1'] * S + S - 1], outline=(0, 255, 255))
    im.save(f'{OUT}/{shot}_guides_4x.png')

def hud(shot):
    f, bs = load(shot); h = {b['name']: b for b in bs}
    top = [n for n in ('health', 'clock', 'time', 'bone', 'bones') if n in h]
    check(len(top) == 5, f'{shot}: the whole top row is drawn {top}')
    tc = [c(h[n])[1] for n in top]; check(max(tc) - min(tc) <= 0.5, f'{shot}: top row centre lines {tc}')
    check(h['health']['x0'] == M, f"{shot}: left margin {h['health']['x0']}")
    check(h['bones']['x1'] == 319 - M and h['score']['x1'] == 319 - M, f"{shot}: right margin {319 - h['bones']['x1']} / score {319 - h['score']['x1']}")
    check(min(h[n]['y0'] for n in top) == M, f"{shot}: top margin {min(h[n]['y0'] for n in top)} (the watch, the tallest, at the margin)")
    for a, b in (('clock', 'time'), ('bone', 'bones'), ('head', 'lives')):
        if a in h and b in h: check(h[b]['x0'] - h[a]['x1'] - 1 == 3, f'{shot}: {a} -> {b} gap {h[b]["x0"] - h[a]["x1"] - 1}')
    gc = (h['clock']['x0'] + h['time']['x1']) / 2; check(abs(gc - 159.5) <= 0.5, f'{shot}: the time group centred: {gc}')
    gap = h['score']['y0'] - h['bones']['y1'] - 1; check(1 <= gap <= 3, f'{shot}: the score {gap} px under the bones count')
    if 'head' in h:
        check(abs(c(h['head'])[1] - c(h['lives'])[1]) <= 0.5, f"{shot}: bottom row centre lines {c(h['head'])[1]} {c(h['lives'])[1]}")
        check(h['head']['y1'] == 239 - M and h['head']['x0'] == M, f"{shot}: bottom row margins {239 - h['head']['y1']} / {h['head']['x0']}")
    ov = overlaps(bs); check(not ov, f'{shot}: nothing overlaps {ov[:4]}')
    drawn(f, bs, shot); guides(f, bs, shot, [c(h['clock'])[1]] + ([c(h['head'])[1]] if 'head' in h else []))

def pause(shot):
    f, bs = load(shot)
    rows = many(bs, 'row'); labels = many(bs, 'label'); pan = one(bs, 'panel'); rib = one(bs, 'ribbon')
    check(len({r['x0'] for r in rows}) == 1 and len({r['x1'] - r['x0'] for r in rows}) == 1, f'{shot}: rows share x and width')
    check(len({b['y0'] - a['y0'] for a, b in zip(rows, rows[1:])}) <= 1, f'{shot}: even row pitch {[b["y0"] - a["y0"] for a, b in zip(rows, rows[1:])]}')
    check(len({l['x0'] for l in labels}) == 1, f'{shot}: labels share one left edge {sorted({l["x0"] for l in labels})}')
    lc = [abs(c(l)[1] - c(r)[1]) for l, r in zip(labels, rows)]; check(lc and max(lc) <= 0.5, f'{shot}: labels centred in their rows {lc}')
    for n in ('panel', 'ribbon', 'title', 'subtitle'):
        b = one(bs, n)
        if b: check(abs(c(b)[0] - 159.5) <= 0.5, f'{shot}: {n} centred ({c(b)[0]})')
    lm = rows[0]['x0'] - pan['x0']; rm = pan['x1'] - rows[0]['x1']; check(lm == rm, f'{shot}: row side padding {lm}/{rm}')
    t = one(bs, 'title'); check(t and abs(c(t)[1] - c(rib)[1]) <= 1.5, f'{shot}: the title on the ribbon\'s centre line')
    cur = one(bs, 'cursor')
    if cur:
        lab = min(labels, key=lambda l: abs(c(l)[1] - c(cur)[1])); check(lab['x0'] - cur['x1'] - 1 == 3, f"{shot}: cursor to label gap {lab['x0'] - cur['x1'] - 1}")
        r = min(rows, key=lambda r: abs(c(r)[1] - c(cur)[1])); check(abs(c(cur)[1] - c(r)[1]) <= 0.5, f'{shot}: cursor centred on its row')
    btn = many(bs, 'button')
    if btn: gc = (btn[0]['x0'] + btn[-1]['x1']) / 2; check(abs(gc - 159.5) <= 0.5, f'{shot}: A / B group centred ({gc})')
    ov = overlaps(bs, skip=('panel', 'row', 'ribbon', 'tab', 'button', 'cursor', 'meter', 'seg')); check(not ov, f'{shot}: no text overlapping {ov[:4]}')
    drawn(f, bs, shot); guides(f, bs, shot, [c(r)[1] for r in rows])

def tally(shot):
    f, bs = load(shot)
    for n in ('panel', 'ribbon', 'title', 'press'):
        b = one(bs, n)
        if b: check(abs(c(b)[0] - 159.5) <= 0.5, f'{shot}: {n} centred ({c(b)[0]})')
    t, rib = one(bs, 'title'), one(bs, 'ribbon')
    L = [b for b in bs if b['name'] == 'tlabel']; V = [b for b in bs if b['name'] == 'tvalue']
    for side, test in (('left', lambda b: b['x0'] < 160), ('right', lambda b: b['x0'] >= 160)):
        ls = [b for b in L if test(b)]; vs = [b for b in V if test(b)]
        check(len({b['x0'] for b in ls}) == 1, f'{shot}: {side} labels share a left edge {sorted({b["x0"] for b in ls})}')
        check(len({b['x1'] for b in vs}) <= 1, f'{shot}: {side} values share a right edge {sorted({b["x1"] for b in vs})}')
        for l in ls:
            v = [x for x in vs if abs(c(x)[1] - c(l)[1]) <= 0.5]; check(len(v) == 1, f'{shot}: {side} label at y {l["y0"]} has its value on its line')
    ll = sorted([b for b in L if b['x0'] < 160], key=lambda b: b['y0'])
    p = [b['y0'] - a['y0'] for a, b in zip(ll, ll[1:])]; check(len(set(p[:-1])) <= 1, f'{shot}: even left row pitch {p} (the last one, SCORE, after a gap)')
    for m in many(bs, 'medal'):
        ml = [b for b in many(bs, 'mlabel') if abs(c(b)[1] - c(m)[1]) <= 0.5]; check(len(ml) == 1 and ml[0]['x0'] - m['x1'] - 1 == 3, f'{shot}: medal at y {m["y0"]}: label on its line, 3 px gap')
    ov = overlaps(bs, skip=('panel', 'ribbon')); check(not ov, f'{shot}: nothing overlapping {ov[:4]}')
    drawn(f, bs, shot); guides(f, bs, shot)

def pieces():
    bad = []
    for p in sorted(glob.glob(f'{ROOT}/riverwalk/art/ui/*.png')):
        n = os.path.basename(p)[:-4]
        if n.startswith('font17_ink') or n.startswith('font13_ink') or n in ('panel', 'head', 'row_off', 'seg_off', 'tab'): continue   # ink (no outline); the kit frame; the v7 head (cream rim); inset rows; the tab's top hides under its coin
        a = np.array(Image.open(p).convert('RGBA')); op = a[..., 3] > 0
        pad = np.pad(op, 1); edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        cols = {tuple(v) for v in a[edge][:, :3]}
        if not cols <= {INK, SH}: bad.append((n, sorted(cols - {INK, SH})[:3]))
    check(not bad, f'pieces: every edge pixel is the outline (64,11,6) or the shadow (36,8,5) {bad[:4]}')

if __name__ == "__main__":
    for s in sorted(glob.glob(f'{D}/*.txt')):
        shot = os.path.basename(s)[:-4]
        if shot.startswith('hud'): hud(shot)
        elif shot.startswith('pause'): pause(shot)
        elif shot.startswith('tally'): tally(shot)
    pieces()
    print('ALL PASS' if ok else 'SOME FAIL')
