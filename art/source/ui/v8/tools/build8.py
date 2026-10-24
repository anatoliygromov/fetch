"""Builds the v8 UI into the game: riverwalk/art/ui/*.png and riverwalk/uifont_data.lua.
  python3 art/source/ui/v8/tools/build8.py            (from the repo root)
Font atlases: one strip per size and style, one cell per glyph (W + 5 px: the body at x + 2, the outline and the
shadow round it), all cells H + 5 + asc tall (asc: the rows an accent such as the dots of Ö needs above the cap line). uifont_data.lua lists each glyph's cell x and body width.
Pieces: icons8.py and menu8.py (drawn on the grid), the v7 clock, bone and head as they are, and the kit's panel frame
(kit/frames/panel_menu, a true 9-slice: slices 15 / 15 / 16 / 16)."""
import os, sys, shutil
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.normpath(os.path.join(HERE, '..', '..'))
ROOT = os.path.normpath(os.path.join(UI, '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'font')); sys.path.insert(0, HERE)
import style8 as S8, icons8, menu8, screens8
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'ui')
ATLASES = {7: ['cream', 'gold', 'dim'], 13: ['gold', 'cream', 'dim', 'ink'], 17: ['ink', 'gold']}

def atlases():
    lua = ['-- made by art/source/ui/v8/tools/build8.py: the v8 font metrics (one family, three sizes). Do not edit.',
           '-- per size: h (glyph body rows), gap (px between bodies), space (px), cells: char = { cell x, body width }',
           'return {']
    for size, styles in ATLASES.items():
        G = S8.FONTS[size]; keys = sorted(G.keys(), key=lambda k: (not k.isalpha(), not k.isdigit(), k))
        H = len(G['A']); x = 0; cells = {}
        strips = {st: [] for st in styles}
        for k in keys:
            w = len(G[k][0]); cells[k] = (x, w); x += w + 5
            for st in styles:                                      # (umlaut fix) every cell S8.ASC rows taller on top
                g = S8.glyph(size, k, st); g = np.pad(g, ((H + 5 + S8.ASC[size] - g.shape[0], 0), (0, 0), (0, 0)))
                strips[st].append(g)
        for st in styles:
            a = np.concatenate(strips[st], axis=1); Image.fromarray(a).save(f'{OUT}/font{size}_{st}.png')
        def q(k): return '["' + ('\\' + k if k in '"\\' else k) + '"]'
        lua.append(f'  [{size}] = {{ h = {H}, asc = {S8.ASC[size]}, gap = {S8.GAP[size]}, space = {S8.SPACE[size]}, styles = {{ ' + ', '.join(f'"{s}"' for s in styles) + ' }, cells = {')
        lua.append('    ' + ', '.join(f'{q(k)} = {{ {cx}, {w} }}' for k, (cx, w) in cells.items()))
        lua.append('  } },')
    lua.append('}')
    open(os.path.join(ROOT, 'riverwalk', 'uifont_data.lua'), 'w', encoding='utf-8').write('\n'.join(lua) + '\n')

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    atlases()
    meta = icons8.build(OUT)
    meta.update(menu8.build(OUT))                                  # the menu pieces (title menu, options, controls)
    meta.update(screens8.build(OUT))                               # step 3: the level cards, talk, hints, tally
    for n in ('clock', 'bone', 'head'): shutil.copy(os.path.join(UI, 'v7_icons', 'icons', f'{n}.png'), f'{OUT}/{n}.png')
    shutil.copy(os.path.join(UI, 'kit', 'frames', 'panel_menu.png'), f'{OUT}/panel.png')
    # each piece's drawn body (its pixels without the drop shadow) inside its image: what the layout places by
    lua = ['-- made by art/source/ui/v8/tools/build8.py: each UI piece\'s body box (x0, y0, x1, y1) in its image, the drop',
           '-- shadow left out (the layout places bodies, BIBLE 5 / v6 spec). Do not edit.', 'return {']
    for f in sorted(os.listdir(OUT)):
        if f.startswith('font') or not f.endswith('.png'): continue
        a = np.array(Image.open(f'{OUT}/{f}').convert('RGBA')); m = (a[..., 3] > 0) & ~np.all(a[..., :3] == S8.SHADOW, axis=-1)
        ys, xs = np.nonzero(m)
        if f.startswith('medal_') and f.endswith('_off.png'):        # (review fix 2) the empty socket is placed by its
            b = np.array(Image.open(f'{OUT}/{f[:-8]}_on.png').convert('RGBA'))   # medal's box (it sits where the disc would)
            m = (b[..., 3] > 0) & ~np.all(b[..., :3] == S8.SHADOW, axis=-1); ys, xs = np.nonzero(m)
        lua.append(f'  {f[:-4]} = {{ {xs.min()}, {ys.min()}, {xs.max()}, {ys.max()} }},')
        print(f, a.shape[1], 'x', a.shape[0], 'body', xs.min(), ys.min(), xs.max(), ys.max())
    for k in ('ribbon_pause', 'ribbon_tally', 'ribbon_menu', 'ribbon_wide'):                    # the ribbons' main band: x0, x1, top row, height
        b = meta[k + '_body']; lua.append(f"  {k}_band = {{ {b['bx0']}, {b['bx1']}, {b['top']}, {b['Hb']} }},")
    lua.append('}')
    open(os.path.join(ROOT, 'riverwalk', 'uiart_data.lua'), 'w').write('\n'.join(lua) + '\n')
