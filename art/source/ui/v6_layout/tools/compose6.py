# FETCH! UI v6: one layout system. Every number here comes from the spec below.
import sys, os, json, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, '/tmp/claude-0/ui/v5')
from rebuild9 import rebuild, draw, rebuild3, draw3
import font5
K = '/tmp/claude-0/ui/kit/clean'; I = '/tmp/claude-0/ui/v6/icons'; OUT = '/tmp/claude-0/ui/preview6'; os.makedirs(OUT, exist_ok=True)
REPO = '/home/claude/anatoliygromov/fetch/riverwalk'
SHADOW = np.array([36, 8, 5])
# ---- the spec
M = 4                      # screen margin to every drawn body (shadows may sit in the margin)
GAP_ICON = 3               # icon to its number
TOP_C = 4 + 10.5           # top row centre line (the 22 px health bar fills rows 4-25)
BOT_BOTTOM = 239 - M       # bottom row: the tallest body ends here
PANEL_PAD = 14             # panel outer edge to its rows / text
ROW_H, ROW_GAP = 24, 4     # menu rows
TEXT_IN = 26               # row left edge to its text: the paw (4 + 19 px) and the 3 px icon gap + 1
CURSOR_IN = 4              # row left edge to the paw
# ----
def P(n): return np.array(Image.open(f'{K}/{n}.png').convert('RGBA'))
def IC(n): return np.array(Image.open(f'{I}/{n}.png').convert('RGBA'))
def T(text, style='cream'): return font5.text(text, style)
def body(a):
    """the drawn shape without its drop shadow: (x0, y0, x1, y1) inside the image"""
    m = (a[..., 3] > 0) & ~np.all(a[..., :3] == SHADOW, axis=-1)
    ys, xs = np.nonzero(m); return xs.min(), ys.min(), xs.max(), ys.max()
LOG = []
def place(f, a, x=None, y=None, name='', cx=None, cy=None, right=None, bottom=None):
    """place by body: left x / centre cx / right edge; top y / centre cy / bottom edge"""
    bx0, by0, bx1, by1 = body(a); bw, bh = bx1 - bx0 + 1, by1 - by0 + 1
    if cx is not None: x = int(np.floor(cx - (bw - 1) / 2 + 0.5))
    if right is not None: x = right - bw + 1
    if cy is not None: y = int(np.floor(cy - (bh - 1) / 2 + 0.5))
    if bottom is not None: y = bottom - bh + 1
    im = Image.fromarray(f); im.alpha_composite(Image.fromarray(a), (x - bx0, y - by0)); f[:] = np.array(im)
    LOG.append(dict(name=name, x0=x, y0=y, x1=x + bw - 1, y1=y + bh - 1)); return x, y, x + bw - 1, y + bh - 1
def width(a): b = body(a); return b[2] - b[0] + 1
def height(a): b = body(a); return b[3] - b[1] + 1
def bar(n):
    b = IC('bar_full').copy(); y = b.shape[0] // 2; row = b[y, :, :3].astype(int); segs = []; cur = None
    for x in range(b.shape[1]):
        r, g, bb = row[x]; s = 'red' if (r > 200 and g < 110) else 'orange' if (r > 200 and 110 <= g < 175 and bb < 80) else 'yellow' if (r > 220 and g >= 175 and bb < 110) else None
        if cur is None or s != cur[0]:
            if cur and cur[0]: segs.append(cur)
            cur = [s, x, x]
        else: cur[2] = x
    if cur and cur[0]: segs.append(cur)
    segs = [s for s in segs if s[2] - s[1] > 4]; E = IC('bar_empty'); ecol = E[E.shape[0] // 2, E.shape[1] // 3, :3]
    for s in segs[n:]:
        reg = b[:, s[1] - 1:s[2] + 2]; L = reg[..., :3].astype(float) @ [0.299, 0.587, 0.114]; m = (reg[..., 3] > 0) & (L > 95)
        reg[m, :3] = (ecol * np.where(L[m] > 200, 1.25, 1.0)[:, None]).clip(0, 255).astype(np.uint8)
    return b
def group(f, parts, cy, left=None, right=None, cx=None, names=()):
    """icon + number groups: parts laid out left to right with GAP_ICON between, all centred on cy"""
    total = sum(width(p) for p in parts) + GAP_ICON * (len(parts) - 1)
    x = left if left is not None else (right - total + 1 if right is not None else int(np.floor(cx - (total - 1) / 2 + 0.5)))
    for p, n in zip(parts, names): place(f, p, x=x, cy=cy, name=n); x += width(p) + GAP_ICON
def hud(f, hearts=2, bottom=True):
    # three groups spread with equal gaps between the margins (space-between)
    gs = [[bar(hearts)], [IC('clock'), T('300', 'gold')], [IC('bone'), T('12/97', 'gold')]]
    ws = [sum(width(p) for p in g) + GAP_ICON * (len(g) - 1) for g in gs]; gap = ((320 - 2 * M) - sum(ws)) / 2
    xs = [M, int(np.floor(M + ws[0] + gap + 0.5)), 319 - M - ws[2] + 1]
    for g, x, nm in zip(gs, xs, [['health'], ['clock', 'time'], ['bone', 'bones']]): group(f, g, TOP_C, left=x, names=nm)
    if bottom:
        hd = IC('head'); cy = BOT_BOTTOM - (height(hd) - 1) / 2
        group(f, [hd, T('x3', 'gold')], cy, left=M, names=['head', 'lives'])
        group(f, [IC('coin'), T('007840', 'gold')], cy, right=319 - M, names=['coin', 'score'])
def checker(frame):
    f = frame.copy(); m = (np.add.outer(np.arange(240), np.arange(320)) % 2) == 0; f[m] = (20, 24, 36, 255); return f
def grey(a):
    g = (a[..., :3].astype(float) @ [0.299, 0.587, 0.114]).astype(np.uint8); return np.dstack([g, g, g, a[..., 3]])
def save(a, name):
    Image.fromarray(a).save(f'{OUT}/{name}_1x.png'); Image.fromarray(a).resize((960, 720), Image.NEAREST).save(f'{OUT}/{name}_3x.png')
    Image.fromarray(grey(a)).save(f'{OUT}/{name}_grey_1x.png')
def tall_row(name, w, h):
    a = P(name)
    if name == 'row_selected': mid = a[:, a.shape[1] // 2]; a[:, 3:17] = mid[:, None]
    r = draw3(rebuild3(a, 4, 4), w); TT = BB = 5; mid = r[r.shape[0] // 2]
    return np.concatenate([r[:TT], np.repeat(mid[None], h - TT - BB, 0), r[-BB:]], 0)
def panel(f, x, y, w, h, title):
    place(f, draw(rebuild(P('panel_menu')), w, h), x=x, y=y, name='panel')
    rib = draw3(rebuild3(P('ribbon')), max(120, width(T(title)) + 50)); place(f, rib, cx=x + (w - 1) / 2, y=y - 8, name='ribbon')
    t = T(title, 'cream'); place(f, t, cx=x + (w - 1) / 2, cy=y - 8 + 10, name='title')
def rows(f, x, y, w, items):
    """items: (label, state, extra) with state in sel / normal / locked; extra draws on the right of the row"""
    for i, (lab, state, extra) in enumerate(items):
        ry = y + i * (ROW_H + ROW_GAP)
        place(f, tall_row('row_selected' if state == 'sel' else 'row_normal', w, ROW_H), x=x, y=ry, name='row')
        if state == 'sel': place(f, P('cursor_paw'), x=x + CURSOR_IN, cy=ry + (ROW_H - 1) / 2, name='cursor')
        t = T(lab, 'dim' if state == 'locked' else 'cream'); place(f, t, x=x + TEXT_IN, cy=ry + (ROW_H - 1) / 2, name='label')
        if extra: extra(f, x + w - 1 - 6, ry + (ROW_H - 1) / 2)
def hints(f, cx, cy, pairs):
    parts = []
    for btn, lab in pairs: parts += [(P(btn), 'btn'), (T(lab, 'cream'), 'hint')]
    widths = [width(p) for p, _ in parts]; total = sum(widths) + GAP_ICON * len(pairs) + 16 * (len(pairs) - 1)
    x = int(np.floor(cx - (total - 1) / 2 + 0.5))
    for i, (p, n) in enumerate(parts):
        place(f, p, x=x, cy=cy, name=n); x += width(p) + (GAP_ICON if i % 2 == 0 else 16)
frame = np.array(Image.open('/tmp/claude-0/shots/look_01_after.png').convert('RGBA'))
title = np.array(Image.open(f'{REPO}/art/title/base.png').convert('RGBA'))
if __name__ == "__main__":
    shots = {}
    LOG.clear(); f = frame.copy(); hud(f); save(f, 'hud'); shots['hud'] = list(LOG)
    # dialogue: the panel spans the screen between the margins; the bottom HUD hides while it shows
    LOG.clear(); f = frame.copy(); hud(f, 3, bottom=False)
    px, pw, ph = M, 320 - 2 * M, 44; py = 239 - M - ph + 1
    place(f, draw(rebuild(P('panel_wide')), pw, ph), x=px, y=py, name='panel')
    port = np.array(Image.open(f'{REPO}/art/portraits/pepper_talk.png').convert('RGBA'))[8:56, 5:69]
    place(f, port, x=px + 6, bottom=py + ph - 1 - 3, name='portrait')
    cy = py + (ph - 1) / 2; bx = px + 6 + 64 + 6
    place(f, P('btn_b'), x=bx, cy=cy, name='btn'); t = T('HOLD: SNEAK', 'cream'); place(f, t, x=bx + width(P('btn_b')) + GAP_ICON + 2, cy=cy, name='text')
    save(f, 'dialogue'); shots['dialogue'] = list(LOG)
    # pause
    LOG.clear(); f = checker(frame); w = 212; x = 160 - w // 2
    n = 3; inner = PANEL_PAD; sub_h = 18; foot_h = 22
    h = inner + 6 + sub_h + 6 + n * ROW_H + (n - 1) * ROW_GAP + 10 + foot_h + inner - 6
    y = 120 - h // 2 + 4
    panel(f, x, y, w, h, 'PAUSED')
    t = T('RIVER WALK', 'gold'); place(f, t, cx=159.5, y=y + inner + 6, name='subtitle')
    ry = y + inner + 6 + sub_h + 6
    vol = lambda f, xr, cy: place(f, P('volume_bar'), right=xr, cy=cy, name='volume')
    rows(f, x + inner, ry, w - 2 * inner, [('GO ON', 'sel', None), ('SOUND', 'normal', vol), ('QUIT', 'normal', None)])
    hints(f, 159.5, ry + n * ROW_H + (n - 1) * ROW_GAP + 10 + (foot_h - 1) / 2, [('btn_a', 'OK'), ('btn_b', 'BACK')])
    save(f, 'pause'); shots['pause'] = list(LOG)
    # level select
    LOG.clear(); f = checker(title); w = 320 - 2 * M - 4; x = 160 - w // 2; n = 6
    h = inner + 4 + n * ROW_H + (n - 1) * ROW_GAP + 8 + foot_h + inner - 6; y = 239 - M - h + 1
    panel(f, x, y, w, h, 'LEVEL SELECT')
    names = ['RIVER WALK', 'CITY PARK', 'DOWNTOWN', 'ROOFTOPS', 'SODER HILL', 'NIGHT HARBOUR']
    def medals(won):
        def fn(f, xr, cy):
            for k, m in enumerate(['par', 'bones', 'nohit']):
                md = P(f'medal_{m}_{"won" if won[2 - k] else "dark"}'); place(f, md, right=xr - k * (width(md) + 2), cy=cy, name='medal')
        return fn
    lock = lambda f, xr, cy: place(f, P('icon_lock'), right=xr, cy=cy, name='lock')
    items = []
    for i, nm in enumerate(names):
        st = 'sel' if i == 0 else ('locked' if i >= 2 else 'normal')
        items.append((f'{i + 1}  {nm}', st, medals([True, True, True]) if i == 0 else medals([True, True, False]) if i == 1 else lock))
    ry = y + inner + 4; rows(f, x + inner, ry, w - 2 * inner, items)
    hints(f, 159.5, ry + n * ROW_H + (n - 1) * ROW_GAP + 8 + (foot_h - 1) / 2, [('btn_a', 'PLAY'), ('btn_b', 'BACK')])
    save(f, 'select'); shots['select'] = list(LOG)
    json.dump(shots, open(f'{OUT}/layout_log.json', 'w'), default=int, indent=0)
    ims = [Image.open(f'{OUT}/{n}_3x.png') for n in ['hud', 'dialogue', 'pause', 'select']]
    s = Image.new('RGB', (1950, 1470), (30, 30, 30))
    for i, im in enumerate(ims): s.paste(im, (10 + (i % 2) * 970, 10 + (i // 2) * 730))
    s.save(f'{OUT}/overview_v6.png'); print('ok')
