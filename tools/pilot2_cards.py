"""tools/pilot2_cards.py FRAMES_DIR OUT_DIR [checks.txt]: the two QA cards of UI pilot 2.
  card_title.png  the old title picture and the new one side by side at 4x (whole, and 4x crops of Pepper, the city
                  and the rebuilt railing), the numbers (colours, lone pixels per region), the palette, the title
                  frames in colour and greyscale, Pepper's mouth and eye frames at 5x with what changes in each
  card_menus.png  every menu screen in colour and greyscale, 5x crops of every new piece and glyph and of the
                  controls strip on both devices, and the layout checks (tools/layout_qa_menus.py)
checks.txt: lines to print on both cards (check_flow, check_pepper, layout QA)."""
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
CHECKS = [l.rstrip() for l in open(sys.argv[3])] if len(sys.argv) > 3 else []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'art', 'source', 'title', 'tools'))
from lone import lone
os.makedirs(OUT, exist_ok=True)
def font(s):
    try: return ImageFont.load_default(size=s)
    except TypeError: return ImageFont.load_default()
F, FB = font(18), font(26)
BG, TXT, OKC, BAD = (30, 30, 35), (232, 232, 236), (90, 200, 110), (235, 70, 70)
def z(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
def grey(im): g = im.convert('L'); return Image.merge('RGB', (g, g, g))
def rgb(p): return Image.open(p).convert('RGB')
def rgba_on(p, bg=(70, 110, 160)):
    a = Image.open(p).convert('RGBA'); b = Image.new('RGBA', a.size, bg + (255,)); b.alpha_composite(a); return b.convert('RGB')

class Card:
    def __init__(s, W): s.W = W; s.parts = []; s.h = 10
    def text(s, t, f=F, col=TXT): s.parts.append(('t', t, f, col, s.h)); s.h += (36 if f is FB else 24)
    def img(s, im, x=10): s.parts.append(('i', im, x, s.h)); return im
    def row(s, ims, gap=16, label=None):
        if label: s.text(label)
        x = 10; hmax = 0
        for im in ims: s.parts.append(('i', im, x, s.h)); x += im.width + gap; hmax = max(hmax, im.height)
        s.h += hmax + 14
    def save(s, path):
        c = Image.new('RGB', (s.W, s.h + 10), BG); d = ImageDraw.Draw(c)
        for p in s.parts:
            if p[0] == 't': d.text((10, p[4]), p[1], font=p[2], fill=p[3])
            else: c.paste(p[1], (p[2], p[3]))
        c.save(path); print(path, c.size)
def checks(card):
    if not CHECKS: return
    card.text('Checks', FB)
    for l in CHECKS: card.text(l, F, OKC if ('PASS' in l or 'UNCHANGED' in l or 'passed' in l) and 'FAIL' not in l else BAD if 'FAIL' in l else TXT)

# ---------------- the title card
blob = subprocess.run(['git', 'show', '6bf9c47:riverwalk/art/title/base.png'], cwd=ROOT, capture_output=True).stdout
tmp = os.path.join(OUT, '_old_base.png'); open(tmp, 'wb').write(blob); old = rgb(tmp); os.remove(tmp)
still = rgb(f'{D}/title_idle.png')
new = rgb(os.path.join(ROOT, 'riverwalk', 'art', 'title', 'base.png'))
card = Card(2640)
card.text('UI pilot 2 · TITLE · the painting on its native grid, Pepper pants and blinks (no box, no dim)', FB)
card.text('Left: the title before (6bf9c47, resampled 1792 -> 240, k-means 64). Right: now (the 7.5 px grid, one colour per cell, the window registered to the drawn pixel; 62 colours, two-group palette; the PRESS ANY KEY box taken out). 4x.')
card.row([z(old, 4), z(new, 4)])
regs = {'Pepper': (20, 80, 150, 240), 'city': (150, 100, 320, 185), 'logo': (118, 10, 304, 84), 'all': (0, 0, 320, 240)}
a_old, a_new = np.array(old), np.array(new)
card.text('Lone pixels (no 4-neighbour of the same colour), before -> now: ' + ',  '.join(
    f'{k} {lone(a_old, v if k != "all" else None) * 100:.1f} % -> {lone(a_new, v if k != "all" else None) * 100:.1f} %' for k, v in regs.items())
    + f';  colours {len(np.unique(a_old.reshape(-1, 3), axis=0))} -> {len(np.unique(a_new.reshape(-1, 3), axis=0))}')
crops = [((40, 80, 150, 175), 'Pepper'), ((150, 95, 320, 180), 'the city and the river'), ((130, 175, 300, 215), 'the railing rebuilt where the box was')]
for box, name in crops:
    w = box[2] - box[0]
    card.row([z(old.crop(box), 6 if w < 130 else 5), z(new.crop(box), 6 if w < 130 else 5)], label=f'{name}: before | now')
pal = rgb(os.path.join(ROOT, 'art', 'source', 'title', 'palette.png'))
card.row([z(pal, 3)], label='the palette (62 colours: 22 for Pepper\'s coat, bandana, tongue and eye, 40 for the rest)')
card.row([z(rgb(f'{D}/title_idle.png'), 2), z(grey(rgb(f'{D}/title_idle.png')), 2), z(rgb(f'{D}/title_press.png'), 2), z(grey(rgb(f'{D}/title_press.png')), 2)],
         label='The title as the game draws it, 2x: idle (PRESS START off) colour, greyscale; PRESS START on colour, greyscale')
mouth = rgb(os.path.join(ROOT, 'riverwalk', 'art', 'title', 'mouth.png')); eye = rgb(os.path.join(ROOT, 'riverwalk', 'art', 'title', 'eye.png'))
def frames_with_diff(strip, n):
    w = strip.width // n; fr = [strip.crop((i * w, 0, (i + 1) * w, strip.height)) for i in range(n)]
    out = []
    for i, f in enumerate(fr):
        out.append(z(f, 8))
        if i:
            d = (np.array(f) != np.array(fr[0])).any(2); m = np.array(fr[0]).copy() // 3; m[d] = (255, 60, 200)
            out.append(z(Image.fromarray(m), 8))
    return out
card.row(frames_with_diff(mouth, 3), label='The pant (8x): the still, tongue half down (+ its changed pixels in magenta), tongue down (+ changed). Outline from the video t2 frames 18 / 21, pixels from the still')
card.row(frames_with_diff(eye, 3), label='The blink (8x): the still, half shut (+ changed), shut (+ changed). Drawn on the still\'s own colours; everything else identical to the still (diff mask)')
card.text('Loop: pant rest, rest, half, down, down, half at 8 fps (0.75 s a breath); blink half, shut, shut, half at 12 fps every 3.4 / 4.6 / 3.9 / 4.3 s. GIF: frames/title_loop_2x.gif')
card.text('Clouds and sailboats stay still: painted into the sky and the water (not separable without repainting). The lamp glow overlay is gone (a translucent blend, off-palette).')
checks(card)
card.save(f'{OUT}/card_title.png')

# ---------------- the menus card
card = Card(2640)
card.text('UI pilot 2 · MENUS · main menu, OPTIONS, CONTROLS, the controls strip (docs/ui_design.md, 24 Oct)', FB)
def pair(n): im = rgb(f'{D}/{n}.png'); return [z(im, 2), z(grey(im), 2)]
card.row(pair('menu_1_pad') + pair('menu_2_pad'), label='Main menu, gamepad glyphs: PLAY selected (colour, grey), LEVELS selected (colour, grey). 2x')
card.row(pair('menu_3_key') + pair('options_1_pad'), label='OPTIONS selected (keyboard glyphs); OPTIONS panel with SOUND selected (the strip says CHANGE with the d-pad)')
card.row(pair('options_2_key') + pair('options_hard_on'), label='OPTIONS: HARD MODE selected (keyboard: SPACE ON); HARD MODE on (the switch green, the strip says OFF)')
card.row(pair('options_3_pad') + pair('controls_pad'), label='OPTIONS: CONTROLS selected; the CONTROLS page (the handheld, each button\'s action, the keyboard keys)')
card.row(pair('controls_key'), label='The CONTROLS page with the keyboard glyphs in the strip')
ui = os.path.join(ROOT, 'riverwalk', 'art', 'ui')
pieces = ['g_a', 'g_b', 'g_x', 'g_y', 'g_l', 'g_r', 'g_start', 'g_dpad', 'g_lr', 'g_down', 'tog_off', 'tog_on']
card.row([z(rgba_on(f'{ui}/{n}.png'), 5) for n in pieces], gap=12, label='5x: the gamepad glyphs (A B X Y, L1 R1 START, d-pad, d-pad left / right) and the HARD MODE switch')
keys = ['k_space', 'k_esc', 'k_shift', 'k_enter', 'k_x', 'k_z', 'k_q', 'k_left', 'k_right', 'k_up', 'k_down']
card.row([z(rgba_on(f'{ui}/{n}.png'), 5) for n in keys], gap=12, label='5x: the keycaps')
card.row([z(rgba_on(f'{ui}/handheld.png'), 5), z(rgba_on(f'{ui}/ribbon_menu.png'), 5)], label='5x: the handheld (RG35XX: d-pad left, X top, Y left, A right, B bottom, SELECT / START, L1 / R1) and the wide ribbon')
for n in ('menu_1_pad', 'menu_1_key', 'options_1_pad', 'options_2_key'):
    im = rgb(f'{D}/{n}.png'); card.row([z(im.crop((80, 216, 240, 240)), 5)], label=f'5x: the controls strip ({n})')
im = rgb(f'{D}/menu_1_pad.png'); card.row([z(im.crop((150, 125, 300, 190)), 5)], label='5x: the main menu rows and the paw cursor')
im = rgb(f'{D}/options_1_pad.png'); card.row([z(im.crop((60, 50, 260, 172)), 5)], label='5x: the OPTIONS panel')
checks(card)
card.save(f'{OUT}/card_menus.png')
