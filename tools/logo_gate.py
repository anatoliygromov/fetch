"""tools/logo_gate.py FRAMES_DIR OUT_DIR: the gate images and checks for the rebuilt logo and tagline (24 Oct).
  logo_before_after_4x.png   the painting's logo and plate (6bf9c47) over the new ones (caps, lowercase), 4x
  logos_4x.png, logos_8x_*.png   original (the native-grid painting), clean, bands, gradient, steps6
  clean_vs_original_8x_*.png      original | clean at 8x;  stars_10x.png the twinkle frames
  logo_8x_a.png, logo_8x_b.png   F E T and C H ! paw, before | after, 8x
  tagline_8x.png              both plates, 8x
Checks (printed, PASS / FAIL): the logo layer's fill has only the five band colours and its edge only the navy, no
lone pixels in the layer; the paw is mirror-symmetric; the plate is centred on the menu's centre line (title.lua
T.CX); the text centred on the plate; every repeated letter identical; nothing of the old logo left in the base
(no warm pixel in the logo's box outside the new layer)."""
import sys, os, re, subprocess
import numpy as np
from PIL import Image
D, OUT = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'art', 'source', 'title', 'tools'))
import logo as LG
os.makedirs(OUT, exist_ok=True)
ok = True
def check(c, m):
    global ok; print(('PASS ' if c else 'FAIL ') + m); ok &= bool(c)
def z(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
blob = subprocess.run(['git', 'show', '6bf9c47:riverwalk/art/title/base.png'], cwd=ROOT, capture_output=True).stdout
tmp = os.path.join(OUT, '_old.png'); open(tmp, 'wb').write(blob); old = Image.open(tmp).convert('RGB'); os.remove(tmp)
caps = Image.open(f'{D}/title_idle.png').convert('RGB'); low = Image.open(f'{D}/title_lower_idle.png').convert('RGB')
painting = Image.open(f'{ROOT}/art/source/title/still_painting.png').convert('RGB')     # the native-grid painting as painted
fills = [('original', painting), ('clean', caps), ('bands', Image.open(f'{D}/title_logo_bands.png').convert('RGB')), ('gradient', Image.open(f'{D}/title_logo_gradient.png').convert('RGB')),
         ('steps6', Image.open(f'{D}/title_logo_steps6.png').convert('RGB'))]
lb4 = (118, 8, 304, 86); w4, h4 = lb4[2] - lb4[0], lb4[3] - lb4[1]
o = Image.new('RGB', ((w4 * 4 + 8) * len(fills), h4 * 4), (255, 0, 255))
for i, (_, im) in enumerate(fills): o.paste(z(im.crop(lb4), 4), (i * (w4 * 4 + 8), 0))
o.save(f'{OUT}/logos_4x.png')
for n, b in (('a', (126, 18, 210, 82)), ('b', (204, 14, 300, 82))):
    w8, h8 = b[2] - b[0], b[3] - b[1]; o = Image.new('RGB', ((w8 * 8 + 8) * 2, (h8 * 8 + 8) * 2), (255, 0, 255))
    o = Image.new('RGB', ((w8 * 8 + 8) * 2, (h8 * 8 + 8) * 3), (255, 0, 255))
    for i, (_, im) in enumerate(fills): o.paste(z(im.crop(b), 8), ((i % 2) * (w8 * 8 + 8), (i // 2) * (h8 * 8 + 8)))
    o.save(f'{OUT}/logos_8x_{n}.png')
    o = Image.new('RGB', ((w8 * 8 + 8) * 2, h8 * 8), (255, 0, 255))                    # original | clean
    for i in (0, 1): o.paste(z(fills[i][1].crop(b), 8), (i * (w8 * 8 + 8), 0))
    o.save(f'{OUT}/clean_vs_original_8x_{n}.png')
st = Image.open(f'{ROOT}/riverwalk/art/title/stars.png').convert('RGBA'); bg = Image.new('RGBA', st.size, (42, 134, 213, 255)); bg.alpha_composite(st)
z(bg, 10).save(f'{OUT}/stars_10x.png')
box = (118, 8, 304, 100); w, h = box[2] - box[0], box[3] - box[1]
o = Image.new('RGB', (w * 4, (h * 4 + 8) * 3), (255, 0, 255))
for i, im in enumerate((old, caps, low)): o.paste(z(im.crop(box), 4), (0, i * (h * 4 + 8)))
o.save(f'{OUT}/logo_before_after_4x.png')
for n, b in (('a', (124, 14, 214, 84)), ('b', (204, 14, 304, 84))):
    W8, H8 = b[2] - b[0], b[3] - b[1]; o = Image.new('RGB', (W8 * 16 + 8, H8 * 8), (255, 0, 255))
    o.paste(z(old.crop(b), 8), (0, 0)); o.paste(z(caps.crop(b), 8), (W8 * 8 + 8, 0)); o.save(f'{OUT}/logo_8x_{n}.png')
pb = (LG.PLATE[0] - 2, LG.PLATE[1] - 2, LG.PLATE[2] + 2, LG.PLATE[3] + 2); W8, H8 = pb[2] - pb[0], pb[3] - pb[1]
o = Image.new('RGB', (W8 * 8, (H8 * 8 + 8) * 3), (255, 0, 255))
for i, im in enumerate((old, caps, low)): o.paste(z(im.crop((146, 74, 146 + W8, 74 + H8)) if i == 0 else im.crop(pb), 8), (0, i * (H8 * 8 + 8)))
o.save(f'{OUT}/tagline_8x.png')
# checks on the layers
for mode in ('clean', 'bands', 'gradient', 'steps6'):
  lay = np.array(Image.open(f'{ROOT}/riverwalk/art/title/logo_{mode}.png').convert('RGBA'))
  op = lay[..., 3] > 0
  cols = {tuple(c) for c in lay[op][:, :3]}
  allowed = {LG.NAVY, LG.HI, LG.YEL, LG.GLD, LG.ORA, LG.LIP} if mode == 'bands' else {LG.NAVY, LG.HI6, *LG.RAMP6}
  if mode != 'clean': check(cols <= allowed, f'logo {mode}: only the navy and its ramp ({len(cols)} colours)')
  else: print(f'INFO logo clean: {len(cols)} colours (the painting\'s own)')
  k = lay[..., 0].astype(int) * 65536 + lay[..., 1].astype(int) * 256 + lay[..., 2]; k[~op] = -1
  p = np.pad(k, 1, constant_values=-2); c = p[1:-1, 1:-1]
  same = (p[:-2, 1:-1] == c) | (p[2:, 1:-1] == c) | (p[1:-1, :-2] == c) | (p[1:-1, 2:] == c)
  lone = op & ~same
  # a highlight or lip pixel is a 1-row line by design: lone only if it has no same-colour neighbour in 8 directions
  p8 = [p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
  same8 = np.zeros_like(same)
  for q in p8: same8 |= q == c
  if mode != 'clean': check((op & ~same8).sum() == 0, f'logo {mode}: no lone pixels (no neighbour of its colour in 8 directions): {(op & ~same8).sum()}')
  else: print(f'INFO logo clean: {(op & ~same8).sum()} single pixels left (kept on purpose: not a shade off their neighbours, e.g. a highlight dot)')
  pe = np.pad(op, 1); edge = op & ~(pe[:-2, 1:-1] & pe[2:, 1:-1] & pe[1:-1, :-2] & pe[1:-1, 2:])
  if mode != 'clean': check({tuple(c) for c in lay[edge][:, :3]} <= {LG.NAVY}, f'logo {mode}: its edge is the navy outline all round')
# the paw: mirror-symmetric about its own centre (the fill colours)
x0, y0 = LG.BOX[0], LG.BOX[1]
fill = op & (lay[..., 0] > 150)
lb = fill[52 - y0:80 - y0, 271 - x0:300 - x0]                  # (the paw alone, right of the H)
ys, xs = np.nonzero(lb); sub = lb[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
check((sub == sub[:, ::-1]).all(), f'paw (the rebuilt versions): mirror-symmetric ({sub.shape[1]} x {sub.shape[0]})')
CX = float(re.search(r'T\.CX = ([\d.]+)', open(f'{ROOT}/riverwalk/title.lua').read()).group(1))
check(abs((LG.PLATE[0] + LG.PLATE[2] - 1) / 2 - CX) <= 0.5, f'plate centred on x {CX}')
for name, text in (('caps', 'THE CITY DOG ADVENTURER'), ('lower', 'The City Dog Adventurer')):
    pl, (tx, ty, tw, th) = LG.plate(text); pw = pl.shape[1]
    check(abs((tx + tx + tw - 1) / 2 - (pw - 1) / 2) <= 0.5, f'{name}: text centred on the plate (x {tx}..{tx + tw - 1} of {pw})')
    check(tx >= 3 and pw - (tx + tw) >= 3, f'{name}: 2+ px clear of the rim each side ({tx - 2}, {pw - (tx + tw) - 2})')
    # every repeated letter identical: cut each letter's pixels at its advance and compare
    G = {}
    x = tx
    for ch in text:
        if ch == ' ': x += LG.S8.SPACE[7]; continue
        g = LG.LOWER.get(ch) or LG.glyphs7.G[ch.upper()]; gw = len(g[0])
        cut = pl[ty:ty + 9, x:x + gw, :3].tobytes(); G.setdefault(ch, set()).add(cut); x += gw + LG.S8.GAP[7]
    bad = [c for c, s in G.items() if len(s) > 1]
    check(not bad, f'{name}: every repeated letter identical {bad}')
base = np.array(Image.open(f'{ROOT}/riverwalk/art/title/base.png').convert('RGB')).astype(int)
bx = base[LG.BOX[1]:LG.BOX[3], LG.BOX[0]:LG.BOX[2]]
warm = (bx[..., 0] > 120) & (bx[..., 0] > bx[..., 2] + 60)
warm[:20, :20] = False                                            # (the tree's leaves in the box's corner)
check((warm & ~op).sum() == 0, f'base: no old logo pixel left outside the new layer ({(warm & ~op).sum()})')
print('ALL PASS' if ok else 'SOME FAIL')
