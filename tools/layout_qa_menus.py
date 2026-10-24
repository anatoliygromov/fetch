"""tools/layout_qa_menus.py FRAMES_DIR: layout checks for the title and the menus (pilot 2) on the frames
tools/title_frames.py writes (<shot>.png, 320 x 240, and <shot>.txt: the bodies placed, name x0 y0 x1 y1 inclusive).
  title: PRESS START centred on the menu's centre line (title.lua T.CX)
  main menu: every row centred on that line, even pitch, the paw cursor on the selected row's centre line, 4 px
             before its label
  options: the panel, the ribbon and the title centred on the screen; labels share one left edge, even pitch; the
           meter and the switch share one right edge and sit on their rows' centre lines; the cursor on the selected
           row's centre line; equal room above and below the rows inside the panel
  controls: the panel, ribbon and title centred; glyphs centred in one column, labels share one left edge, keys one
            right edge, each row's glyph, label and keys on one centre line, even pitch; the handheld on the rows'
            middle line and inside the panel
  strip (every menu screen): centred on the screen, bodies' bottom at y 235 (the margin), glyphs and labels on one
         centre line, the same place on every screen
  nothing overlaps (text, glyphs, controls); pieces: every edge pixel is the outline (64,11,6) or the shadow (36,8,5)
Prints PASS / FAIL lines, then ALL PASS or SOME FAIL."""
import sys, os, glob, re
import numpy as np
from PIL import Image
D = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CX = float(re.search(r'T\.CX = ([\d.]+)', open(f'{ROOT}/riverwalk/title.lua').read()).group(1))
ok = True
def check(cond, msg):
    global ok; print(('PASS ' if cond else 'FAIL ') + msg); ok &= bool(cond)
def load(shot):
    out = []
    for l in open(f'{D}/{shot}.txt'):
        p = l.split()
        if len(p) == 5: out.append(dict(name=p[0], x0=int(p[1]), y0=int(p[2]), x1=int(p[3]), y1=int(p[4])))
    return out
def cx(b): return (b['x0'] + b['x1']) / 2
def cy(b): return (b['y0'] + b['y1']) / 2
def many(bs, *n): return [b for b in bs if b['name'] in n]
def overlaps(bs):
    r = []
    for i, a in enumerate(bs):
        for b in bs[i + 1:]:
            if not (a['x1'] < b['x0'] or b['x1'] < a['x0'] or a['y1'] < b['y0'] or b['y1'] < a['y0']): r.append((a['name'], b['name']))
    return r
def pitch_even(ys): d = np.diff(sorted(ys)); return len(set(d.tolist())) <= 1, d.tolist()
strips = {}
def strip(shot, bs):
    s = many(bs, 'glyph', 'strip')
    s = [b for b in s if b['y0'] >= 200]
    x0, x1 = min(b['x0'] for b in s), max(b['x1'] for b in s)
    check(abs((x0 + x1) / 2 - 159.5) <= 0.5, f'{shot}: strip centred on the screen ({x0}-{x1})')
    check(max(b['y1'] for b in s) == 235, f'{shot}: strip bodies end at the margin (y {max(b["y1"] for b in s)})')
    check(len({cy(b) for b in s}) == 1, f'{shot}: strip glyphs and labels on one centre line {sorted({cy(b) for b in s})}')
    strips[shot] = (min(b['y0'] for b in s), max(b['y1'] for b in s))
    return s

for f in sorted(glob.glob(f'{D}/*.txt')):
    shot = os.path.basename(f)[:-4]; bs = load(shot)
    if shot.startswith('title_press'):
        p = many(bs, 'press')[0]; check(abs(cx(p) - CX) <= 0.5, f'{shot}: PRESS START centred on x {CX} ({cx(p)})')
    elif shot.startswith('menu_'):
        labels = many(bs, 'label'); cur = many(bs, 'cursor')[0]
        check(all(abs(cx(b) - CX) <= 0.5 for b in labels), f'{shot}: rows centred on x {CX} {[cx(b) for b in labels]}')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        sel = int(shot.split('_')[1]) - 1; lb = sorted(labels, key=lambda b: b['y0'])[sel]
        check(abs(cy(cur) - cy(lb)) <= 1, f'{shot}: cursor on the selected row\'s centre line (bob 1 px) ({cy(cur)} vs {cy(lb)})')
        check(lb['x0'] - cur['x1'] - 1 == 4, f'{shot}: cursor 4 px before its label ({lb["x0"] - cur["x1"] - 1})')
        s = strip(shot, bs)
        check(not overlaps(labels + [cur] + s), f'{shot}: nothing overlaps {overlaps(labels + [cur] + s)}')
    elif shot.startswith('options'):
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        labels = sorted(many(bs, 'label'), key=lambda b: b['y0'])
        check(len({b['x0'] for b in labels}) == 1, f'{shot}: labels share one left edge')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        ctl = many(bs, 'meter', 'toggle')
        check(len({b['x1'] for b in ctl}) == 1, f'{shot}: meter and switch share one right edge {[b["x1"] for b in ctl]}')
        for b, l in zip(sorted(ctl, key=lambda b: b['y0']), labels[:2]): check(abs(cy(b) - cy(l)) <= 0.5, f'{shot}: {b["name"]} on its row\'s centre line ({cy(b)} vs {cy(l)})')
        cur = many(bs, 'cursor')[0]; sel = 1 if 'hard' in shot else int(shot.split('_')[1]) - 1
        check(abs(cy(cur) - cy(labels[sel])) <= 1, f'{shot}: cursor on the selected row\'s centre line (bob 1 px)')
        top, bot = labels[0]['y0'] - P['y0'], P['y1'] - labels[-1]['y1']
        check(abs(top - bot) <= 1, f'{shot}: rows centred in the panel (above {top}, below {bot})')
        s = strip(shot, bs)
        items = labels + ctl + [cur, T] + s
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
    elif shot.startswith('controls'):
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]; Hh = many(bs, 'handheld')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        labels = sorted(many(bs, 'label'), key=lambda b: b['y0'])
        check(len({b['x0'] for b in labels}) == 1, f'{shot}: labels share one left edge')
        e, d = pitch_even([b['y0'] for b in labels]); check(e, f'{shot}: even row pitch {d}')
        gl = [b for b in many(bs, 'glyph') if b['y0'] < 200]; ks = many(bs, 'key')
        rows = {}
        for b in gl: rows.setdefault(b['y0'], []).append(b)
        cxs = {(min(b['x0'] for b in r) + max(b['x1'] for b in r)) / 2 for r in rows.values()}
        check(max(cxs) - min(cxs) <= 1, f'{shot}: glyphs centred in one column {sorted(cxs)}')
        kr = {}
        for b in ks: kr.setdefault(b['y0'], []).append(b)
        check(len({max(b['x1'] for b in r) for r in kr.values()}) == 1, f'{shot}: keys share one right edge')
        check(all(abs(cy(l) - cy(rows[y][0])) <= 0.5 and abs(cy(l) - cy(kr[y][0])) <= 0.5 for l, y in zip(labels, sorted(rows))), f'{shot}: each row on one centre line')
        mid = (labels[0]['y0'] + labels[-1]['y1']) / 2
        check(abs(cy(Hh) - mid) <= 1, f'{shot}: handheld on the rows\' middle line ({cy(Hh)} vs {mid})')
        check(Hh['x0'] - P['x0'] >= 18 and Hh['y0'] - P['y0'] >= 8 and P['y1'] - Hh['y1'] >= 8, f'{shot}: handheld inside the panel, clear of its frame')
        top, bot = labels[0]['y0'] - P['y0'], P['y1'] - labels[-1]['y1']
        check(abs(top - bot) <= 1, f'{shot}: rows centred in the panel (above {top}, below {bot})')
        s = strip(shot, bs)
        items = labels + gl + ks + [Hh, T] + s
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
    elif shot.startswith('select'):
        s = strip(shot, bs)
        if 'slide' in shot: continue                                       # (two cards mid-slide: the strip only)
        P = many(bs, 'panel')[0]; R = many(bs, 'ribbon')[0]; T = many(bs, 'title')[0]; N = many(bs, 'name')[0]; Pic = many(bs, 'picture')[0]
        for n, b in (('panel', P), ('ribbon', R), ('title', T), ('name', N), ('picture', Pic)): check(abs(cx(b) - 159.5) <= 0.5, f'{shot}: {n} centred ({cx(b)})')
        check(Pic['x0'] - P['x0'] >= 8 and P['x1'] - Pic['x1'] >= 8 and Pic['y0'] > P['y0'] and P['y1'] > N['y1'], f'{shot}: picture and name inside the panel')
        ar = sorted(many(bs, 'arrow'), key=lambda b: b['x0'])
        check(len(ar) == 2 and abs((ar[0]['x0'] + ar[1]['x1']) / 2 - 159.5) <= 1 and cy(ar[0]) == cy(ar[1]), f'{shot}: arrows either side, symmetric (1 px nudge), one centre line')
        check(all(abs(cy(a) - cy(Pic)) <= 1 for a in ar), f'{shot}: arrows on the picture\'s middle line ({[cy(a) for a in ar]} vs {cy(Pic)})')
        check(ar[0]['x1'] < P['x0'] and ar[1]['x0'] > P['x1'] and ar[0]['x0'] >= 4 and ar[1]['x1'] <= 315, f'{shot}: arrows outside the card, on the screen')
        md = sorted(many(bs, 'medal'), key=lambda b: b['x0'])
        check(len(md) == 3 and md[0]['x0'] == Pic['x0'] + 4, f'{shot}: three medals from the picture\'s left edge ({md[0]["x0"]} vs {Pic["x0"] + 4})')
        e, d = pitch_even([b['x0'] for b in md]); check(e, f'{shot}: medals evenly spaced {d}')
        row = md + many(bs, 'clock', 'time', 'score')
        check(max(cy(b) for b in row) - min(cy(b) for b in row) <= 0.5, f'{shot}: medals, clock, time and points on one centre line {sorted({cy(b) for b in row})}')
        sc = many(bs, 'score')
        if sc: check(sc[0]['x1'] == Pic['x1'] - 4, f'{shot}: points end at the picture\'s right edge ({sc[0]["x1"]} vs {Pic["x1"] - 4})')
        lk = many(bs, 'lock')
        if lk: check(abs(cx(lk[0]) - cx(Pic)) <= 0.5 and abs(cy(lk[0]) - cy(Pic)) <= 0.5, f'{shot}: padlock centred on the picture')
        dots = many(bs, 'dot')
        check(abs((min(b['x0'] for b in dots) + max(b['x1'] for b in dots)) / 2 - 159.5) <= 0.5 and min(b['y0'] for b in dots) > P['y1'] and max(b['y1'] for b in dots) < s[0]['y0'] - 2, f'{shot}: dots centred between the card and the strip')
        items = [T, N] + row + many(bs, 'lock', 'hard') + s + dots
        check(not overlaps(items), f'{shot}: nothing overlaps {overlaps(items)}')
check(len(set(strips.values())) == 1, f'strip: the same place on every screen {sorted(set(strips.values()))}')
# pieces
INK = (64, 11, 6); SH = (36, 8, 5)
for n in ['g_a', 'g_b', 'g_x', 'g_y', 'g_l', 'g_r', 'g_start', 'g_dpad', 'g_lr', 'g_down', 'k_space', 'k_esc', 'k_shift', 'k_enter', 'k_x', 'k_z', 'k_q',
          'k_left', 'k_right', 'k_up', 'k_down', 'tog_on', 'tog_off', 'handheld', 'ribbon_menu',
          'arrow_l', 'arrow_r', 'lock', 'lock_big', 'dot_on', 'dot_off', 'frame_s', 'bubble', 'ball', 'stamp',
          'medal_nohit_on', 'medal_nohit_off', 'medal_bones_on', 'medal_bones_off', 'medal_par_on', 'medal_par_off']:
    a = np.array(Image.open(f'{ROOT}/riverwalk/art/ui/{n}.png').convert('RGBA')); op = a[..., 3] > 0
    p = np.pad(op, 1); edge = op & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    cols = {tuple(c) for c in a[edge][:, :3]}
    check(cols <= {INK, SH}, f'piece {n}: edge pixels only outline / shadow' + ('' if cols <= {INK, SH} else f' (also {sorted(cols - {INK, SH})[:3]})'))
    check(set(np.unique(a[..., 3]).tolist()) <= {0, 255}, f'piece {n}: alpha 0 or 255')
print('ALL PASS' if ok else 'SOME FAIL')
