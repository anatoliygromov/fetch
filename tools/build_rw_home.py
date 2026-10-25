#!/usr/bin/env python3
"""River Walk HOME house, screen 1, at true scale (46 px a metre), taller than the viewport. 25 Oct 2026.

Back layer, decoration: no outline, every edge is a darker shade of its own material. Built from parts drawn once and
stamped on an integer grid (BIBLE 3, the crispness bar); no resampling, binary alpha, 19 colours.
The flat gable pilot (art/rw-gable-true) was "ok, but not really artistic, super flat" (owner, 25 Oct), so this one
gets its volume from the light: sun from the upper left, every part that stands out of the wall (stone surround,
keystone, cornice, sills, quoins, drainpipe, lamp) drops a 2 px shadow on the wall below and to its right, and the
door and window openings are recessed (shaded top and left reveal, lit right reveal). Look reference only: the
golden screen "River Walk B" (Artlist, 25 Oct); no pixel is taken from it.

Sizes (46 px/m): door opening 46 x 98 (1.0 x 2.1 m) on a granite step, fanlight 16, window 46 x 72, ground storey
147 (3.2 m) from the pavement to the string course, granite plinth 16 (0.35 m). Upper floor: its wall and the bottom of
its windows run out of the top of the screen.

Image 184 x 180, drawn with its bottom on the pavement's back edge (game y 174): the bottom row is at game y 173 and
the top row at game y -6, so the house's top is never on screen (tools/check_backdrop.py). Window opening 46 x 70.

Usage: build_rw_home.py [OUT.png]   default riverwalk/art/scene/rw_home.png (+ an 8x parts sheet in art/source/rw_home/)
"""
import os
import sys

import numpy as np
from PIL import Image

W, H = 184, 180
OFF = 5                      # image y = game y + OFF (ground: game y 174 = image row 179)

PAL = {                      # 20 colours, per-material ramps, neutral darks
    'pl_hi': (250, 214, 142), 'pl': (238, 188, 104), 'pl_sh': (212, 154, 84), 'pl_dk': (168, 110, 62),   # ochre plaster
    'st_hi': (250, 240, 220), 'st': (228, 212, 182), 'st_sh': (192, 172, 142), 'st_dk': (146, 126, 102),  # sandstone
    'gr_hi': (194, 196, 202), 'gr': (156, 158, 168), 'gr_sh': (118, 120, 132),                          # granite
    'ir': (86, 88, 100), 'ink': (40, 42, 54),                                                             # iron, dark
    'dr_hi': (112, 156, 104), 'dr': (68, 110, 72), 'dr_dk': (40, 70, 48),                                 # door green
    'gl_hi': (196, 220, 236), 'gl': (98, 126, 152),                                                       # glass (its shade: iron)
    'brass': (244, 204, 105), 'wh': (247, 249, 250),                                                  # brass, window white
}
assert len(PAL) == 20
NAMES = list(PAL)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.full((h, w), -1, np.int16)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = NAMES.index(c)

    def rect(self, x, y, w, h, c):
        x0, y0, x1, y1 = max(0, x), max(0, y), min(self.w, x + w), min(self.h, y + h)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1] = NAMES.index(c)

    def hline(self, x, y, w, c): self.rect(x, y, w, 1, c)
    def vline(self, x, y, h, c): self.rect(x, y, 1, h, c)

    def stamp(self, part, x, y):
        h, w = part.a.shape
        for yy in range(h):
            for xx in range(w):
                v = part.a[yy, xx]
                if v >= 0 and 0 <= x + xx < self.w and 0 <= y + yy < self.h:
                    self.a[y + yy, x + xx] = v

    def shadow(self, part, x, y, dx=2, dy=2, on=('pl', 'pl_hi'), c='pl_sh'):
        """Cast the part's shadow onto the wall: plaster pixels under the part shifted by (dx, dy) turn darker."""
        h, w = part.a.shape
        wall = [NAMES.index(n) for n in on]
        for yy in range(h):
            for xx in range(w):
                if part.a[yy, xx] < 0: continue
                tx, ty = x + xx + dx, y + yy + dy
                if 0 <= tx < self.w and 0 <= ty < self.h and self.a[ty, tx] in wall:
                    self.a[ty, tx] = NAMES.index(c)

    def image(self, scale=1):
        rgb = np.zeros((self.h, self.w, 4), np.uint8)
        for i, n in enumerate(NAMES):
            rgb[self.a == i] = (*PAL[n], 255)
        im = Image.fromarray(rgb, 'RGBA')
        return im.resize((self.w * scale, self.h * scale), Image.NEAREST) if scale > 1 else im


# ---- parts, each drawn once ------------------------------------------------------------------------------------

def part_door_leaf(w=22, h=98):
    """One leaf of a panelled double door: frame, a tall upper and a short lower raised panel, light upper left."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'dr')
    p.vline(0, 0, h, 'dr_hi'); p.hline(0, 0, w, 'dr_hi')           # lit stile and top rail
    p.vline(w - 1, 1, h - 1, 'dr_dk')                               # shaded meeting edge
    for (py, ph) in ((6, 50), (62, 30)):                            # raised panels
        x0, pw = 4, w - 8
        p.rect(x0, py, pw, ph, 'dr')
        p.hline(x0, py, pw, 'dr_dk'); p.vline(x0, py, ph, 'dr_dk')            # sunk edge in shadow (top, left)
        p.hline(x0 + 1, py + ph - 1, pw - 1, 'dr_hi'); p.vline(x0 + pw - 1, py + 1, ph - 1, 'dr_hi')  # lit edge
        p.rect(x0 + 3, py + 3, pw - 6, ph - 6, 'dr')
        p.hline(x0 + 3, py + 3, pw - 6, 'dr_hi'); p.vline(x0 + 3, py + 3, ph - 6, 'dr_hi')    # raised field: lit top-left
        p.hline(x0 + 4, py + ph - 4, pw - 7, 'dr_dk'); p.vline(x0 + pw - 4, py + 4, ph - 7, 'dr_dk')
    return p


def part_fanlight(w=46, h=16):
    """Segmental fanlight over the door: glass under a flat arch (stone in the two corners above it), five bars
    radiating from the bottom centre, a 2 px transom bar; the sky's reflection in one clean band at the top left."""
    import math
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'st')
    cx = (w - 1) / 2
    R = (cx ** 2 + 64) / 16.0                      # circle through the edges at y 8 and the crown at y 0
    for x in range(w):
        top = int(round(R - math.sqrt(max(0.0, R * R - (x - cx) ** 2))))
        for y in range(max(0, top), h - 2):
            p.put(x, y, 'gl')
        if 0 <= top < h - 2: p.put(x, top, 'st_sh')            # the arch's shaded soffit line
    for x in range(w):                                         # reflection band
        for y in range(h - 2):
            if p.a[y, x] == NAMES.index('gl') and 6 <= x + 2 * y <= 9 + 0 and x < w // 2: p.put(x, y, 'gl_hi')
    for ang in (-56, -28, 0, 28, 56):
        t = math.radians(ang)
        for st in range(0, 60):
            x = int(round(cx + math.sin(t) * st * 0.5)); y = int(round(h - 3 - math.cos(t) * st * 0.5))
            if 0 <= y < h - 2 and 0 <= x < w and p.a[y, x] in (NAMES.index('gl'), NAMES.index('gl_hi')):
                p.put(x, y, 'st')
    p.hline(0, h - 2, w, 'st_hi'); p.hline(0, h - 1, w, 'st_sh')      # transom bar
    return p


def part_window(w=46, h=72, rows=3, sky_rows=1, curtains=False):
    """Swedish two-casement window, `rows` panes a casement, white-painted wood (white, its shade the stone). Glass a flat mid blue
    with a dark top-left inner edge (the bars' shadow) and, in the top `sky_rows` panes, the sky's reflection as two
    clean diagonal streaks (3 px and 1 px). Frame lit top-left, shaded bottom-right."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'wh')                                        # white-painted wood
    p.hline(1, h - 1, w - 1, 'st'); p.vline(w - 1, 1, h - 1, 'st')  # shaded bottom and right edge
    cw = (w - 3 - 3 - 2) // 2
    ph = (h - 6 - 2 * (rows - 1)) // rows
    for k, cx in enumerate((3, 3 + cw + 2)):
        for r in range(rows):
            y0 = 3 + r * (ph + 2)
            p.rect(cx, y0, cw, ph, 'gl')
            p.hline(cx, y0, cw, 'ir'); p.vline(cx, y0, ph, 'ir')
            if r < sky_rows:
                a = int(cw * 0.75)
                for u in range(1, cw):
                    for v in range(1, ph):
                        sd = u + v
                        if a <= sd <= a + 2 or sd == a + 6: p.put(cx + u, y0 + v, 'gl_hi')
    p.vline(3 + cw, 3, h - 6, 'wh'); p.vline(4 + cw, 3, h - 6, 'st')
    if curtains:                                   # white tie-back curtains on the outer side of each casement
        gh = h - 6; tie = 3 + int(gh * 0.6)
        for k in (0, 1):
            for y in range(3, h - 3):
                if y <= tie:
                    cwid = max(3, int(round((cw * 0.5) * (1 - (y - 3) / (tie - 3)) ** 1.3)) + 3)
                else:
                    cwid = 4 + (y - tie) // 8
                for i in range(cwid):
                    x = 3 + i if k == 0 else w - 4 - i
                    edge = i == cwid - 1
                    fold = (i % 4 == 2) and y < tie - 2
                    p.put(x, y, 'st_sh' if (edge or fold) else 'st_hi')
            tx = 3 + 2 if k == 0 else w - 4 - 2
            p.rect(tx - 1, tie, 3, 2, 'brass')     # the tie
    return p


def part_window_frame(w, h, t=5):
    """Sandstone surround round an opening: lit top and left, shaded right and bottom edges."""
    p = Canvas(w, h)
    p.rect(0, 0, w, t, 'st'); p.rect(0, 0, t, h, 'st'); p.rect(w - t, 0, t, h, 'st'); p.rect(0, h - t, w, t, 'st')
    p.hline(0, 0, w, 'st_hi'); p.vline(0, 0, h, 'st_hi')
    p.vline(w - 1, 1, h - 1, 'st_sh'); p.hline(1, h - 1, w - 1, 'st_sh')
    p.vline(t - 1, t - 1, h - 2 * t + 2, 'st_sh'); p.hline(t - 1, t - 1, w - 2 * t + 2, 'st_sh')   # inner arris
    return p


def part_sill(w, h=4):
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'st'); p.hline(0, 0, w, 'st_hi'); p.hline(0, h - 1, w, 'st_dk'); p.vline(w - 1, 0, h, 'st_sh')
    return p


def part_quoin(w, h):
    """One corner stone: lit top edge and left arris, dark joint at the bottom."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'st')
    p.hline(0, 0, w, 'st_hi'); p.vline(0, 0, h, 'st_hi')
    p.hline(0, h - 1, w, 'st_dk'); p.vline(w - 1, 0, h - 1, 'st_sh')
    return p


def part_plinth_block(w, h=8):
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'gr')
    p.hline(0, 0, w, 'gr_hi'); p.vline(0, 0, h - 1, 'gr_hi')
    p.hline(0, h - 1, w, 'gr_sh'); p.vline(w - 1, 1, h - 1, 'gr_sh')
    return p


def part_lamp():
    """Wall lantern (iron, warm glass), 9 x 18, on a bracket."""
    p = Canvas(9, 18)
    p.rect(3, 0, 3, 2, 'ir'); p.hline(1, 2, 7, 'ink'); p.hline(2, 3, 5, 'ir')       # finial, roof
    p.rect(2, 4, 5, 8, 'brass'); p.vline(1, 4, 8, 'ink'); p.vline(7, 4, 8, 'ink'); p.vline(4, 4, 8, 'ir')
    p.rect(2, 4, 2, 3, 'st_hi')                                                          # glint
    p.hline(1, 12, 7, 'ink'); p.hline(3, 13, 3, 'ir'); p.vline(4, 14, 4, 'ink')
    return p


def part_pipe(h):
    """Drainpipe, 4 px: lit left column, iron body, dark right edge."""
    p = Canvas(4, h)
    p.vline(0, 0, h, 'gr'); p.rect(1, 0, 2, h, 'ir'); p.vline(3, 0, h, 'ink')
    for y in range(8, h - 6, 40):                                                     # brackets
        p.hline(0, y, 4, 'ink'); p.hline(0, y + 1, 4, 'ir')
    return p


# ---- the house ----------------------------------------------------------------------------------------------------

def build():
    c = Canvas(W, H)
    g = lambda y: y + OFF                                     # game y -> image y
    QX = W - 14                                               # corner quoins, 14 px
    c.rect(0, 0, W, H, 'pl')                                  # plaster to the corner (short quoins show wall left of them)
    # string course between the floors (top of the ground storey at game y 27 = 147 px above the pavement)
    sc_y = g(22)
    band = Canvas(QX + 2, 8)
    band.rect(0, 0, QX + 2, 8, 'st'); band.hline(0, 0, QX + 2, 'st_hi'); band.hline(0, 1, QX + 2, 'st_hi')
    band.hline(0, 5, QX + 2, 'st_sh'); band.hline(0, 6, QX + 2, 'st_sh'); band.hline(0, 7, QX + 2, 'st_dk')
    # upper floor: window bottoms over the door and over the window, sills, then the band
    for wx in (40, 112):
        up = part_window(46, 40, rows=2, sky_rows=2)
        c.stamp(up, wx, g(-25))
        sill = part_sill(54)
        c.stamp(sill, wx - 4, g(13)); c.shadow(sill, wx - 4, g(13))
    c.stamp(band, 0, sc_y); c.shadow(band, 0, sc_y, dx=0, dy=3, c='pl_sh')
    # quoins: long and short stones, the building's corner
    y = g(30)
    k = 0
    while y < g(158):
        qh = 12
        qw = 14 if k % 2 == 0 else 10
        q = part_quoin(qw, qh)
        c.stamp(q, W - qw, y); c.shadow(q, W - qw, y, dx=0, dy=2)
        y += qh; k += 1
    c.rect(QX, g(-5), 14, g(22) - g(-5), 'pl')               # upper floor corner: quoins continue
    y = g(-5) - 2; k = 1
    while y < g(22):
        qw = 14 if k % 2 == 0 else 10
        q = part_quoin(qw, 12); c.stamp(q, W - qw, y); y += 12; k += 1
    # granite plinth, two courses, staggered joints
    for row, (py, ph) in enumerate(((g(158), 8), (g(166), 9))):
        x = -12 if row else 0
        bw = 30
        while x < W:
            b = part_plinth_block(bw, ph); c.stamp(b, x, py); x += bw
    c.hline(0, g(158), W, 'gr_hi')
    # the door: surround (pilasters, entablature, keystone), recess, two leaves, fanlight, granite step
    DX, DW = 40, 46                    # opening x 40..85
    top_open = g(58)                   # fanlight top (game y 58); door leaves from game y 74 to 172
    sur = part_window_frame(DW + 14, g(172) - top_open + 7, t=7)
    c.stamp(sur, DX - 7, top_open - 7); c.shadow(sur, DX - 7, top_open - 7)
    ent = Canvas(DW + 22, 10)                                   # entablature with a cornice cap
    ent.rect(0, 2, DW + 22, 8, 'st'); ent.hline(0, 0, DW + 22, 'st_hi'); ent.hline(0, 1, DW + 22, 'st')
    ent.hline(2, 2, DW + 18, 'st_dk'); ent.hline(2, 3, DW + 18, 'st_hi'); ent.hline(0, 9, DW + 22, 'st_dk')
    ent.vline(DW + 21, 0, 10, 'st_sh')
    c.stamp(ent, DX - 11, top_open - 17); c.shadow(ent, DX - 11, top_open - 17)
    key = Canvas(9, 14)                                         # keystone, wider at the top
    for yy in range(14):
        inset = yy // 7
        key.rect(inset, yy, 9 - 2 * inset, 1, 'st')
        key.put(inset, yy, 'st_hi'); key.put(8 - inset, yy, 'st_sh')
    key.hline(0, 0, 9, 'st_hi'); key.hline(1, 13, 7, 'st_dk')
    c.stamp(key, DX + DW // 2 - 4, top_open - 8); c.shadow(key, DX + DW // 2 - 4, top_open - 8, on=('st', 'st_hi'), c='st_sh')
    fan = part_fanlight(DW, 16)
    c.stamp(fan, DX, top_open)
    leaf = part_door_leaf(23, g(172) - g(74))
    c.stamp(leaf, DX, g(74))
    leaf2 = part_door_leaf(23, g(172) - g(74)); c.stamp(leaf2, DX + 23, g(74))
    c.vline(DX + 22, g(74), g(172) - g(74), 'ink')               # the meeting gap
    for kx in (DX + 19, DX + 26):                                # brass knobs
        c.rect(kx, g(120), 2, 2, 'brass'); c.put(kx + 1, g(121), 'pl_dk')
    # recess: the lintel and the left reveal throw shade into the opening (light from the upper left)
    for yy in range(top_open, g(172)):
        for xx in range(DX, DX + 3):
            v = NAMES[c.a[yy, xx]]
            c.a[yy, xx] = NAMES.index({'dr_hi': 'dr', 'dr': 'dr_dk', 'gl': 'ir', 'gl_hi': 'gl', 'st': 'st_sh',
                                        'st_hi': 'st', 'brass': 'brass'}.get(v, v))
    for xx in range(DX, DX + DW):
        for yy in range(top_open, top_open + 2):
            v = NAMES[c.a[yy, xx]]
            c.a[yy, xx] = NAMES.index({'gl': 'ir', 'gl_hi': 'gl', 'st': 'st_sh', 'st_hi': 'st'}.get(v, v))
    step = Canvas(DW + 16, 3)
    step.rect(0, 0, DW + 16, 3, 'gr'); step.hline(0, 0, DW + 16, 'gr_hi'); step.hline(0, 2, DW + 16, 'gr_sh')
    c.stamp(step, DX - 8, g(172))
    # the wall lantern right of the door
    lamp = part_lamp(); c.stamp(lamp, DX + DW + 11, g(70)); c.shadow(lamp, DX + DW + 11, g(70))
    arm = Canvas(4, 3); arm.hline(0, 0, 4, 'ink'); arm.put(0, 1, 'ink'); arm.put(0, 2, 'ir')   # bracket into the wall
    c.stamp(arm, DX + DW + 8, g(72)); c.shadow(arm, DX + DW + 8, g(72))                     # bracket into the wall
    # the window, with its surround and sill
    WX, WY, WWd, WH = 112, g(66), 46, 70
    fr = part_window_frame(WWd + 10, WH + 10, t=5)
    c.stamp(fr, WX - 5, WY - 5); c.shadow(fr, WX - 5, WY - 5)
    win = part_window(WWd, WH, rows=3, curtains=True); c.stamp(win, WX, WY)
    for yy in range(WY, WY + WH):                               # reveal shade on the left and top of the glass
        for xx in range(WX, WX + 2):
            v = NAMES[c.a[yy, xx]]; c.a[yy, xx] = NAMES.index({'st_hi': 'st_sh', 'st': 'st_sh'}.get(v, v))
    sill = part_sill(WWd + 16, 5); c.stamp(sill, WX - 8, WY + WH + 5); c.shadow(sill, WX - 8, WY + WH + 5)
    # drainpipe at the corner, from the top down into the plinth, with its shoe
    pipe = part_pipe(g(158))
    c.stamp(pipe, QX - 6, 0); c.shadow(pipe, QX - 6, 0, dx=2, dy=0)
    c.rect(QX - 7, g(155), 6, 3, 'ir'); c.hline(QX - 7, g(155), 6, 'gr'); c.hline(QX - 7, g(157), 6, 'ink')
    return c


def parts_sheet():
    ps = [part_door_leaf(23, 98), part_fanlight(), part_window(), part_window_frame(56, 80), part_quoin(14, 12),
          part_plinth_block(30), part_lamp(), part_sill(62, 5)]
    w = sum(p.w for p in ps) + 4 * (len(ps) + 1); h = max(p.h for p in ps) + 8
    s = Canvas(w, h); x = 4
    for p in ps: s.stamp(p, x, 4); x += p.w + 4
    return s


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'riverwalk/art/scene/rw_home.png'
    c = build()
    c.image().save(out)
    os.makedirs('art/source/rw_home', exist_ok=True)
    parts_sheet().image(8).save('art/source/rw_home/parts_8x.png')
    a = c.a
    used = len(np.unique(a[a >= 0]))
    print(f'{out}: {W}x{H}, {used} colours')
