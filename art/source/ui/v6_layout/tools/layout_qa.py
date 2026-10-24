import json, numpy as np
from PIL import Image, ImageDraw
OUT = '/tmp/claude-0/ui/preview6'; L = json.load(open(f'{OUT}/layout_log.json')); M = 4; TOP_C = 14.5; ok = True
def c(i): return ((i['x0'] + i['x1']) / 2, (i['y0'] + i['y1']) / 2)
def by(shot, name): return [i for i in L[shot] if i['name'] == name]
def check(cond, msg):
    global ok; print(('PASS ' if cond else 'FAIL ') + msg); ok &= bool(cond)
hud = {i['name']: i for i in L['hud']}
top = ['health', 'clock', 'time', 'bone', 'bones']; bot = ['head', 'lives', 'coin', 'score']
tc = [c(hud[n])[1] for n in top]; check(max(tc) - min(tc) <= 0.5, f'top row centre lines {tc}')
check(hud['health']['x0'] == M, f"left margin {hud['health']['x0']}"); check(hud['bones']['x1'] == 319 - M, f"right margin {319 - hud['bones']['x1']}")
check(min(hud[n]['y0'] for n in top) >= M, f"top margin {min(hud[n]['y0'] for n in top)}")
check(hud['health']['y0'] == M, f"tallest top item at the margin: health y0 {hud['health']['y0']}")
for a, b in (('clock', 'time'), ('bone', 'bones'), ('head', 'lives'), ('coin', 'score')):
    check(hud[b]['x0'] - hud[a]['x1'] - 1 == 3, f'{a} -> {b} gap {hud[b]["x0"] - hud[a]["x1"] - 1}')
gl = hud['clock']['x0'] - hud['health']['x1'] - 1; gr = hud['bone']['x0'] - hud['time']['x1'] - 1; check(abs(gl - gr) <= 1, f'equal gaps between the top groups: {gl} / {gr}')
bc = [c(hud[n])[1] for n in bot]; check(max(bc) - min(bc) <= 0.5, f'bottom row centre lines {bc}')
check(max(hud[n]['y1'] for n in bot) == 239 - M, f"bottom margin {239 - max(hud[n]['y1'] for n in bot)}")
check(hud['head']['x0'] == M and hud['score']['x1'] == 319 - M, 'bottom row side margins')
for shot in ('pause', 'select'):
    rows = by(L[shot] and shot, 'row'); labels = by(shot, 'label')
    xs = {r['x0'] for r in rows}; ws = {r['x1'] - r['x0'] for r in rows}; check(len(xs) == 1 and len(ws) == 1, f'{shot}: rows share x and width')
    pitches = {b['y0'] - a['y0'] for a, b in zip(rows, rows[1:])}; check(len(pitches) == 1, f'{shot}: even row pitch {pitches}')
    check(len({l['x0'] for l in labels}) == 1, f'{shot}: labels share one left edge')
    lc = [abs(c(l)[1] - c(r)[1]) for l, r in zip(labels, rows)]; check(max(lc) <= 0.5, f'{shot}: labels centred in their rows')
    pan = by(shot, 'panel')[0]; check(abs((pan['x0'] + pan['x1']) / 2 - 159.5) <= 0.5, f'{shot}: panel centred')
    lm = rows[0]['x0'] - pan['x0']; rm = pan['x1'] - rows[0]['x1']; check(lm == rm, f'{shot}: row side padding {lm}/{rm}')
    ov = []
    items = L[shot]
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if a['name'] in ('panel', 'row', 'ribbon') or b['name'] in ('panel', 'row', 'ribbon'): continue
            if not (a['x1'] < b['x0'] or b['x1'] < a['x0'] or a['y1'] < b['y0'] or b['y1'] < a['y0']): ov.append((a['name'], b['name']))
    check(not ov, f'{shot}: no overlapping text / icons {ov[:4]}')
for shot in ('pause', 'select'):
    cur = by(shot, 'cursor')[0]; lab = by(shot, 'label')[0]; check(lab['x0'] - cur['x1'] - 1 == 3, f"{shot}: cursor to label gap {lab['x0'] - cur['x1'] - 1}")
print('ALL PASS' if ok else 'SOME FAIL')
# guides for the eye check
im = Image.open(f'{OUT}/hud_1x.png').convert('RGB').resize((1280, 960), Image.NEAREST); d = ImageDraw.Draw(im); S = 4
for y in (TOP_C, ): d.line([(0, y * S + 2), (1280, y * S + 2)], fill=(0, 255, 0))
for x in (M, 319 - M, 159.5): d.line([(x * S + 2, 0), (x * S + 2, 960)], fill=(255, 0, 255))
for y in (M, 239 - M): d.line([(0, y * S + 2), (1280, y * S + 2)], fill=(0, 255, 255))
bc_ = (hud['head']['y0'] + hud['head']['y1']) / 2; d.line([(0, bc_ * S + 2), (1280, bc_ * S + 2)], fill=(0, 255, 0))
im.crop((0, 0, 1280, 120)).save(f'{OUT}/guides_top.png'); im.crop((0, 840, 1280, 960)).save(f'{OUT}/guides_bottom.png')
