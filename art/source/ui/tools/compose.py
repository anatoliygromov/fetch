# preview the kit as the game would draw it, on real 320x240 frames
import sys, os, re, json, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from rebuild9 import rebuild, draw, rebuild3, draw3
K = '/tmp/claude-0/ui/kit/clean'; OUT = '/tmp/claude-0/ui/preview'; os.makedirs(OUT, exist_ok=True)
REPO = '/home/claude/anatoliygromov/fetch/riverwalk'
def P(n): return np.array(Image.open(f'{K}/{n}.png').convert('RGBA'))
def paste(dst, src, x, y):
    im = Image.fromarray(dst); im.alpha_composite(Image.fromarray(src), (int(x), int(y))); dst[:] = np.array(im)
# the small 5x7 font from bigfont.lua, for body text
src = open(f'{REPO}/bigfont.lua').read()
G = {}
for m in re.finditer(r'(\S+)\s*=\s*\{\s*((?:"[.#]+",?\s*)+)\}', src):
    k = m.group(1).strip('[]"\''); rows = re.findall(r'"([.#]+)"', m.group(2))
    if len(rows) == 7: G[k] = rows
def small(text, col, scale=1, shadow=(28, 16, 12, 255)):
    text = text.upper(); w = max(1, len(text) * 6 * scale); o = np.zeros((7 * scale + scale, w + scale, 4), np.uint8)
    for pass_, c, off in ((0, shadow, scale), (1, col, 0)):
        x = 0
        for ch in text:
            g = G.get(ch) or G.get(f'["{ch}"]')
            if g:
                for yy, r in enumerate(g):
                    for xx, v in enumerate(r):
                        if v == '#': o[yy*scale+off:(yy+1)*scale+off, x+xx*scale+off:x+(xx+1)*scale+off] = c
            x += 6 * scale
    return o
CREAM = (250, 232, 190, 255); GOLD = (255, 205, 70, 255)
INK = (40, 18, 10, 255)
def styled2(text, top=(255, 214, 72, 255), bottom=(240, 142, 32, 255), outline=INK):
    text = text.upper(); w = len(text) * 12 + 2; o = np.zeros((16, w, 4), np.uint8); mask = np.zeros((16, w), bool); x = 1
    for ch in text:
        g = G.get(ch) or G.get(f'["{ch}"]')
        if g:
            for yy, r in enumerate(g):
                for xx, v in enumerate(r):
                    if v == '#': mask[1 + yy*2:3 + yy*2, x + xx*2:x + xx*2 + 2] = True
        x += 12
    from scipy import ndimage
    ring = ndimage.binary_dilation(mask, structure=np.ones((3, 3))) & ~mask; o[ring] = outline
    for yy in range(16): o[yy][mask[yy]] = top if yy <= 7 else bottom
    return o
def tall_row(name, w, h, L):
    if name == 'row_selected':                        # the plain orange bar: its middle column also replaces the paw cap
        a = P(name); mid = a[:, a.shape[1] // 2]; a[:, 3:17] = mid[:, None]; r = draw3(rebuild3(a, 4, 4), w)
    else: r = draw3(rebuild3(P(name), L, 4), w)
    T = 5; B = 5
    mid = r[r.shape[0] // 2]
    return np.concatenate([r[:T], np.repeat(mid[None], h - T - B, 0), r[-B:]], 0)
def styled(text, top=(255, 214, 72, 255), bottom=(240, 142, 32, 255), split=3, outline=INK):
    """the 5x7 letters with the kit's treatment: two colour bands and a 1 px dark outline all round"""
    text = text.upper(); w = len(text) * 6 + 2; o = np.zeros((9, w, 4), np.uint8); mask = np.zeros((9, w), bool)
    x = 1
    for ch in text:
        g = G.get(ch) or G.get(f'["{ch}"]')
        if g:
            for yy, r in enumerate(g):
                for xx, v in enumerate(r):
                    if v == '#': mask[yy + 1, x + xx] = True
        x += 6
    from scipy import ndimage
    ring = ndimage.binary_dilation(mask, structure=np.ones((3, 3))) & ~mask
    o[ring] = outline
    for yy in range(9):
        o[yy][mask[yy]] = top if yy <= split else bottom
    return o
def kitword(text, gap=1):
    gl = [P('letter_' + c) if (c.isalpha() and c != 'x') else (P('digit_' + {'/': 'slash', ':': 'colon', 'x': 'x'}.get(c, c)) if c != ' ' else None) for c in text]
    h = max(g.shape[0] for g in gl if g is not None); w = sum((g.shape[1] if g is not None else 8) + gap for g in gl)
    o = np.zeros((h + 1, w, 4), np.uint8); x = 0
    for g in gl:
        if g is None: x += 8 + gap; continue
        paste(o, g, x, h - g.shape[0]); x += g.shape[1] + gap
    return o
def digits(text, gap=0): return kitword(text.replace('X', 'x'), gap)
def health(n):
    full, empty = P('health_full'), P('health_empty'); o = empty.copy()
    mid = full[full.shape[0] // 2, :, :3].astype(int); lum = mid @ [3, 6, 1] // 10
    seg = [(18, 32), (33, 49), (51, 65)]
    for i in range(n): o[:, seg[i][0]:seg[i][1]] = full[:, seg[i][0]:seg[i][1]]
    return o
def checker(frame):
    f = frame.copy(); m = (np.add.outer(np.arange(240), np.arange(320)) % 2) == 0; f[m] = (20, 24, 36, 255); return f
def grey(a):
    g = (a[..., :3].astype(float) @ [0.299, 0.587, 0.114]).astype(np.uint8); return np.dstack([g, g, g, a[..., 3]])
def save(a, name):
    Image.fromarray(a).save(f'{OUT}/{name}_1x.png')
    Image.fromarray(a).resize((960, 720), Image.NEAREST).save(f'{OUT}/{name}_3x.png')
frame = np.array(Image.open('/tmp/claude-0/shots/look_01_after.png').convert('RGBA'))
title = np.array(Image.open(f'{REPO}/art/title/base.png').convert('RGBA'))
# 1) HUD as drawn (the kit at its native size)
f = frame.copy()
paste(f, health(2), 3, 3)
clk = P('icon_clock'); paste(f, clk, 118, 2); paste(f, digits('300'), 140, 6)
bone = P('icon_bone'); paste(f, bone, 212, 4); paste(f, digits('12/97'), 234, 4)
paste(f, styled('007840'), 274, 27)
head = P('pepper_head_rim'); paste(f, head, 3, 240 - head.shape[0] - 2); paste(f, digits('x3'), 32, 240 - 24)
save(f, 'hud_native'); save(grey(f), 'hud_native_grey')
# 2) HUD with the small numerals (5x7 at 1x, gold with a dark shadow): the kit's icons and bar, small numbers
f = frame.copy()
paste(f, health(2), 3, 3)
paste(f, clk, 130, 2); paste(f, small('300', GOLD, 2), 151, 9)
paste(f, bone, 212, 5); paste(f, small('12/97', GOLD, 2), 234, 9)
paste(f, small('SCORE 007840', CREAM, 1), 248, 28)
paste(f, head, 4, 240 - head.shape[0] - 3); paste(f, small('X3', GOLD, 2), 32, 240 - 20)
save(f, 'hud_small'); save(grey(f), 'hud_small_grey')
# 3) pause menu over the dimmed gameplay frame
f = checker(frame)
pm = draw(rebuild(P('panel_menu')), 186, 150); paste(f, pm, 67, 50)
rib = draw3(rebuild3(P('ribbon')), 132); paste(f, rib, 94, 42)
w = kitword('PAUSED'); paste(f, w, 160 - w.shape[1] // 2, 40)
t = styled('LEVEL 1  RIVER WALK'); paste(f, t, 160 - t.shape[1] // 2, 68)
for i, (lab, sel) in enumerate([('GO ON', True), ('SOUND', False), ('QUIT', False)]):
    y = 82 + i * 28; row = tall_row('row_selected' if sel else 'row_normal', 160, 24, 4); paste(f, row, 80, y)
    if sel: paste(f, P('cursor_paw'), 83, y + 3)
    t = styled2(lab, (255, 250, 232, 255), (255, 228, 176, 255)) if sel else styled2(lab, CREAM, (226, 196, 150, 255)); paste(f, t, 106, y + 4)
    if lab == 'SOUND': paste(f, P('volume_bar'), 80 + 160 - 63 - 5, y + 7)
paste(f, P('btn_a'), 98, 172); paste(f, styled('OK', CREAM, (226, 196, 150, 255)), 117, 177)
paste(f, P('btn_b'), 168, 172); paste(f, styled('BACK', CREAM, (226, 196, 150, 255)), 187, 177)
save(f, 'pause'); save(grey(f), 'pause_grey')
# 4) level select
f = checker(title)
pm = draw(rebuild(P('panel_menu')), 296, 222); paste(f, pm, 12, 12)
rib = draw3(rebuild3(P('ribbon')), 190); paste(f, rib, 65, 6)
w = kitword('LEVEL SELECT'); paste(f, w, 160 - w.shape[1] // 2, 4)
names = ['RIVER WALK', 'CITY PARK', 'DOWNTOWN', 'ROOFTOPS', 'SODER HILL', 'NIGHT HARBOUR']
for i, n in enumerate(names):
    y = 34 + i * 28; sel = i == 0; locked = i >= 2
    paste(f, tall_row('row_selected' if sel else 'row_normal', 268, 24, 4), 26, y)
    if sel: paste(f, P('cursor_paw'), 29, y + 3)
    d = digits(str(i + 1)); paste(f, d, 50, y + 1)
    t = styled2(n, (255, 250, 232, 255), (255, 228, 176, 255)) if sel else (styled2(n, (196, 176, 146, 255), (170, 150, 120, 255)) if locked else styled2(n, CREAM, (226, 196, 150, 255))); paste(f, t, 68, y + 4)
    if locked: paste(f, P('icon_lock'), 268, y + 1)
    else:
        for k, m in enumerate(['nohit', 'bones', 'par']):
            won = sel or k < 2; paste(f, P(f'medal_{m}_{"won" if won else "dark"}'), 226 + k * 20, y + 1)
paste(f, P('btn_a'), 90, 208); paste(f, styled('PLAY', CREAM, (226, 196, 150, 255)), 109, 213)
paste(f, P('btn_b'), 180, 208); paste(f, styled('BACK', CREAM, (226, 196, 150, 255)), 199, 213)
save(f, 'select'); save(grey(f), 'select_grey')
# 5) dialogue panel with Pepper's portrait
f = frame.copy(); paste(f, health(3), 3, 3)
pw = draw(rebuild(P('panel_wide')), 248, 42); paste(f, pw, 36, 194)
port = np.array(Image.open(f'{REPO}/art/portraits/pepper_talk.png').convert('RGBA'))[8:56, 5:69]
paste(f, port, 40, 240 - 48 - 4)
paste(f, P('btn_b'), 112, 206); t = styled2('HOLD: SNEAK', CREAM, (226, 196, 150, 255)); paste(f, t, 136, 207)
save(f, 'dialogue'); save(grey(f), 'dialogue_grey')
print('ok')
