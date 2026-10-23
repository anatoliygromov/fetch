import sys, os, json, shutil, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rebuild9 import rebuild, draw, rebuild3, draw3
C = '/tmp/claude-0/ui/kit/clean'; F = '/tmp/claude-0/ui/kit/final'; shutil.rmtree(F, ignore_errors=True)
for d in ('font_big', 'pieces', 'frames'): os.makedirs(f'{F}/{d}')
meta = {}
for n in ['panel_menu', 'panel_wide', 'panel_menu_cream', 'panel_wide_cream']:
    a = np.array(Image.open(f'{C}/{n}.png')); s = rebuild(a); Image.fromarray(draw(s, a.shape[1], a.shape[0])).save(f'{F}/frames/{n}.png')
    meta[n] = dict(kind='nine', left=s['L'], right=s['R'], top=s['T'], bottom=s['B'])
for n, L, R in [('row_normal', 4, 4), ('row_selected', 17, 4), ('row_disabled', 4, 4), ('ribbon', None, None), ('health_full', 18, 6), ('health_empty', 18, 6)]:
    a = np.array(Image.open(f'{C}/{n}.png')); s = rebuild3(a, L, R)
    out = draw3(s, a.shape[1]) if n.startswith(('row', 'ribbon')) else a
    Image.fromarray(out).save(f'{F}/frames/{n}.png'); meta[n] = dict(kind='three', left=s['L'], right=s['R'])
for f in os.listdir(C):
    n = f[:-4]
    if n.startswith(('letter_', 'digit_')): shutil.copy(f'{C}/{f}', f'{F}/font_big/{f}')
    elif n not in meta: shutil.copy(f'{C}/{f}', f'{F}/pieces/{f}')
json.dump(meta, open(f'{F}/frames/slices.json', 'w'), indent=1)
rows = []
for d in ('pieces', 'frames', 'font_big'):
    for f in sorted(os.listdir(f'{F}/{d}')):
        if not f.endswith('.png'): continue
        a = np.array(Image.open(f'{F}/{d}/{f}').convert('RGBA')); op = a[..., 3] > 0
        alpha_ok = set(np.unique(a[..., 3]).tolist()) <= {0, 255}
        lab, n = ndimage.label(op, structure=np.ones((3, 3))); sizes = ndimage.sum(op, lab, range(1, n + 1))
        specks = int(sum(1 for s in sizes if s <= 4)) if n > 1 else 0
        holes = ndimage.binary_fill_holes(op) & ~op; hl, hn = ndimage.label(holes); hs = ndimage.sum(holes, hl, range(1, hn + 1))
        pin = int(sum(1 for s in hs if s <= 2))
        key = (a[..., 0].astype(int) << 16) | (a[..., 1].astype(int) << 8) | a[..., 2]
        lone = 0
        for y, x in zip(*np.nonzero(op)):
            nb = key[max(0, y-1):y+2, max(0, x-1):x+2]; m = op[max(0, y-1):y+2, max(0, x-1):x+2]
            if ((nb == key[y, x]) & m).sum() <= 1: lone += 1
        rows.append(dict(group=d, name=f[:-4], w=int(a.shape[1]), h=int(a.shape[0]), colours=int(len(np.unique(key[op]))),
                         lone_pct=round(100 * lone / int(op.sum()), 1), specks=specks, pinholes=pin, alpha_binary=bool(alpha_ok)))
json.dump(rows, open(f'{F}/qa.json', 'w'), indent=1)
bad = [r for r in rows if r['lone_pct'] > 5.8 or r['specks'] or r['pinholes'] or not r['alpha_binary']]
print(len(rows), 'pieces; max lone', max(r['lone_pct'] for r in rows), '%; max colours', max(r['colours'] for r in rows), '; flagged', len(bad))
for r in bad: print('  ', r)
