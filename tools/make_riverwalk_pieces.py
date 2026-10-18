#!/usr/bin/env python3
"""Art for River Walk's three pieces that were drawn as flat boxes in code (setpieces.lua), at exactly their old
sizes, so collision and layout stay the same:
  kennel.png (34 x 36): Pepper's kennel, Swedish falu red with white corner trim, a flat roof of dark boards (the
      top Pepper stands on, y 148), a bone sign, and the open doorway below y 165 that she crawls into (dark inside).
      An obstacle: crisp, 1 px dark outline.
  kiosk_kaffe.png (64 x 56), kiosk_glass.png (56 x 56): the two kiosks at the back of the pavement, decoration (no
      outline; setpieces.lua fades them towards the haze like every decoration): green painted panels, a lit window
      with cups / ice cream cones, a counter, a sign (KAFFE, GLASS).
  awning_88.png, awning_80.png (88 / 80 x 10): their striped awnings, obstacles (outline): a lit top row, red and
      white stripes with a shaded underside, a scalloped hem.
Colours are River Walk's own (setpieces.lua: the flower box wood, the bench green, the awning red and white)."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, '..', 'riverwalk', 'art', 'scene')
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
INK = (18, 18, 26)
class G:
    def __init__(s, w, h): s.w, s.h, s.p = w, h, {}
    def px(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.p[(x, y)] = c
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.px(x, y, c)
    def save(s, name):
        im = Image.new('RGBA', (s.w, s.h))
        for (x, y), c in s.p.items(): im.putpixel((x, y), c + (255,))
        im.save(os.path.join(ART, name)); print(name, s.w, 'x', s.h)
FONT = {'K': ['101', '110', '100', '110', '101'], 'A': ['010', '101', '111', '101', '101'],
        'F': ['111', '100', '110', '100', '100'], 'E': ['111', '100', '110', '100', '111'],
        'G': ['011', '100', '101', '101', '011'], 'L': ['100', '100', '100', '100', '111'],
        'S': ['011', '100', '010', '001', '110']}
def text(g, s, x, y, c):
    for ch in s:
        for r, row in enumerate(FONT[ch]):
            for k, b in enumerate(row):
                if b == '1': g.px(x + k, y + r, c)
        x += 4
# --- the kennel ----------------------------------------------------------------------------------------------
FALU, FALU_D, FALU_L = hx('9e3a2b'), hx('74281f'), hx('c0503a')
TRIM, TRIM_D = hx('efece4'), hx('c9c4b8')
ROOF, ROOF_L = hx('3a3a44'), hx('5a5a66')
k = G(34, 36)
k.rect(0, 0, 33, 35, INK)
k.rect(1, 1, 32, 2, ROOF_L); k.rect(1, 3, 32, 4, ROOF)              # the flat roof: two dark boards, lit edge
for x in range(4, 32, 7): k.px(x, 3, ROOF_L)
k.rect(0, 5, 33, 5, INK)
k.rect(1, 6, 32, 34, FALU)                                           # the falu red planks
for y in range(9, 35, 4): k.rect(1, y, 32, y, FALU_D)
for y in range(7, 35, 4): k.rect(1, y, 32, y, FALU_L)
k.rect(1, 6, 3, 34, TRIM); k.rect(3, 6, 3, 34, TRIM_D)               # white corner trims
k.rect(30, 6, 32, 34, TRIM); k.rect(30, 6, 30, 34, TRIM_D)
k.rect(11, 8, 22, 12, INK); k.rect(12, 9, 21, 11, TRIM)              # the bone sign
for x, y in ((13, 9), (13, 11), (20, 9), (20, 11)): k.px(x, y, TRIM_D)
k.rect(14, 10, 19, 10, hx('d9c9a8'))
k.rect(4, 16, 29, 35, INK)                                           # the doorway (y 165 = row 17): dark inside,
k.rect(5, 17, 28, 35, hx('1e1a1e'))                                  # rounded top corners, a lit sill line
k.px(5, 17, INK); k.px(28, 17, INK)
k.rect(6, 18, 27, 18, hx('2c262a'))
k.save('kennel.png')
# --- the kiosks ----------------------------------------------------------------------------------------------
GREEN, GREEN_D, GREEN_L = hx('3f6b48'), hx('2c4e35'), hx('5a8a62')
GLASS, GLASS_L = hx('9fb8c8'), hx('d6e4ea')
CREAM, CREAM_D = hx('e8dcc0'), hx('c8b894')
def kiosk(w, sign, goods, name):
    g = G(w, 56)
    g.rect(0, 0, w - 1, 55, GREEN_D)
    g.rect(2, 0, w - 3, 55, GREEN)
    g.rect(2, 0, 2, 55, GREEN_L)                                     # lit left edge
    g.rect(4, 2, w - 5, 8, CREAM); g.rect(4, 8, w - 5, 8, CREAM_D)   # the sign board
    text(g, sign, w // 2 - len(sign) * 2 + 1, 3, GREEN_D)
    g.rect(5, 11, w - 6, 27, GREEN_D)                                # the window: frame, glass, glints
    g.rect(6, 12, w - 7, 26, GLASS)
    g.rect(7, 13, w - 8, 13, GLASS_L)
    for i in range(6, 9): g.px(w - 8 - (i - 6), 14 + i - 6, GLASS_L)
    goods(g, w)
    g.rect(4, 28, w - 5, 31, CREAM); g.rect(4, 32, w - 5, 32, CREAM_D)   # the counter
    for x0 in (5, w // 2 + 1):                                       # two panels below
        g.rect(x0, 35, x0 + w // 2 - 7, 52, GREEN_D); g.rect(x0 + 1, 36, x0 + w // 2 - 8, 51, GREEN)
        g.rect(x0 + 1, 36, x0 + w // 2 - 8, 36, GREEN_L)
    g.save(name)
def cups(g, w):
    for x in range(9, w - 10, 7):
        g.rect(x, 21, x + 3, 25, CREAM); g.px(x + 4, 22, CREAM); g.px(x + 4, 23, CREAM); g.rect(x, 25, x + 3, 25, CREAM_D)
        g.px(x + 1, 19, hx('ffffff')); g.px(x + 2, 18, hx('ffffff'))
def cones(g, w):
    cols = [hx('f0b8c8'), hx('f2e6c0'), hx('8a5a3a'), hx('b8d8a0')]
    for i, x in enumerate(range(9, w - 10, 7)):
        g.rect(x, 18, x + 3, 20, cols[i % 4]); g.px(x, 18, hx('ffffff'))
        g.rect(x, 21, x + 3, 21, hx('d9a05a')); g.rect(x + 1, 22, x + 2, 24, hx('c08040')); g.px(x + 1, 25, hx('c08040'))
kiosk(64, 'KAFFE', cups, 'kiosk_kaffe.png')
kiosk(56, 'GLASS', cones, 'kiosk_glass.png')
# --- the awnings ---------------------------------------------------------------------------------------------
RED, RED_D, RED_L = hx('c8473f'), hx('9a3530'), hx('e0645a')
WHITE, WHITE_D = hx('efece4'), hx('c9c4b8')
def awning(w, name):
    g = G(w, 10)
    g.rect(0, 0, w - 1, 7, INK)
    for i in range(0, w - 2, 8):
        red = (i // 8) % 2 == 0
        x0, x1 = 1 + i, min(w - 2, i + 8)
        g.rect(x0, 1, x1, 1, RED_L if red else hx('ffffff'))          # lit top
        g.rect(x0, 2, x1, 5, RED if red else WHITE)
        g.rect(x0, 6, x1, 6, RED_D if red else WHITE_D)               # shaded underside
    for i in range(0, w - 1, 8):                                       # the scalloped hem
        red = (i // 8) % 2 == 0
        g.rect(i + 2, 7, i + 5, 9, INK); g.rect(i + 3, 7, i + 4, 8, RED_D if red else WHITE_D)
    g.save(name)
awning(88, 'awning_88.png'); awning(80, 'awning_80.png')
