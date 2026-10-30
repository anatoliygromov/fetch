#!/usr/bin/env python3
"""River Walk GABLE house, screen 12, at true scale (46 px a metre), taller than the viewport. 25 Oct 2026 (night).

The narrow Old Town house left of the cafe (replaces the prop using art "gable", whose details were smothered by the
script clean pass; the old file stays in the repo). Built the way the approved HOME house (tools/build_rw_home.py)
was built: back layer, decoration, no outline (every edge is a darker shade of its own material), parts drawn once and
stamped on an integer grid, binary alpha, at most 20 colours, volume from the light: sun from the upper left, every
part that stands out of the wall (lesene, surrounds, string course, portal, sills, flower boxes, wall anchors) drops a
2 px shadow on the wall below and to its right, and the door and window openings are recessed (shaded top and left
reveal, lit right reveal).

Its own details, so it reads as a different house from HOME: orange-ochre plaster (HOME is yellow ochre) with its
corner lesene and eared window surrounds painted a lighter tone, the way Gamla stan houses are, and no string course;
a grey Gotland sandstone portal (pilasters on bases, capitals, lintel, entablature, a segmental pediment) round an oak
double door with lozenge panels under a four-light transom; a hood over the window (four panes a casement, HOME has
three); a smooth stone socle (HOME: granite blocks); iron wall anchors at the floor line; red geraniums in boxes on
the upper sills.

Sizes (46 px/m): door opening 46 x 98 (leaves) on a stone step, transom 12, window 46 x 72 (top at game y 66, as
HOME's), socle 16. Upper floor: its wall and the bottom of its windows (sills at game y 20) run out of the top.

Image 148 x 180, drawn with its bottom on the pavement's back edge (prop x0 3568, y1 174): the bottom row is at game
y 173 and the top row at game y -6, so the top is never on screen (tools/check_backdrop.py). The bench (play layer,
x 3545-3647) stands in front of the window; the portal's left pilaster starts at x 3648, right of it.

Usage: build_rw_gable.py [OUT.png]   default riverwalk/art/scene/rw_gable.png (+ an 8x parts sheet in art/source/rw_gable/)
"""
import os
import sys

import numpy as np
from PIL import Image

W, H = 148, 180
OFF = 6                      # image row = game y + OFF (the bottom row, 179, is drawn at game y 173)

PAL = {                      # 20 colours, per-material ramps, neutral darks
    'tr_hi': (255, 232, 196), 'pl_hi': (248, 200, 144), 'pl': (234, 162, 100), 'pl_sh': (204, 128, 78),  # orange-ochre plaster
    'st_hi': (240, 236, 224), 'st': (210, 206, 192), 'st_sh': (170, 166, 154), 'st_dk': (124, 120, 112),  # grey sandstone
    'dr_hi': (168, 112, 70), 'dr': (128, 80, 50), 'dr_dk': (88, 54, 38),                                  # oak door
    'gl_hi': (196, 220, 236), 'gl': (98, 126, 152),                                                       # glass (its shade: iron)
    'ir': (86, 88, 100), 'ink': (40, 42, 54),                                                             # iron, dark
    'wh': (247, 249, 250), 'brass': (244, 204, 105),                                                      # window white, brass
    'fl': (218, 70, 64), 'fl_dk': (164, 44, 48), 'lf': (86, 132, 66),                                     # geranium, leaf
}
assert len(PAL) == 20


class Canvas:
    """An indexed canvas for one palette (build_rw_home.py's Canvas, with the palette as a parameter)."""

    def __init__(self, w, h, pal=PAL):
        self.w, self.h, self.pal, self.names = w, h, pal, list(pal)
        self.a = np.full((h, w), -1, np.int16)

    def i(self, c): return self.names.index(c)

    def at(self, x, y):
        return self.names[self.a[y, x]] if 0 <= x < self.w and 0 <= y < self.h and self.a[y, x] >= 0 else None

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = self.i(c)

    def rect(self, x, y, w, h, c):
        x0, y0, x1, y1 = max(0, x), max(0, y), min(self.w, x + w), min(self.h, y + h)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1] = self.i(c)

    def hline(self, x, y, w, c): self.rect(x, y, w, 1, c)
    def vline(self, x, y, h, c): self.rect(x, y, 1, h, c)

    def stamp(self, part, x, y):
        h, w = part.a.shape
        for yy in range(h):
            for xx in range(w):
                v = part.a[yy, xx]
                if v >= 0 and 0 <= x + xx < self.w and 0 <= y + yy < self.h:
                    self.a[y + yy, x + xx] = self.i(part.names[v])

    def shadow(self, part, x, y, dx=2, dy=2, on=('pl', 'pl_hi'), c='pl_sh'):
        """Cast the part's shadow onto the wall: wall pixels under the part shifted by (dx, dy) turn darker."""
        h, w = part.a.shape
        wall = [self.i(n) for n in on]
        for yy in range(h):
            for xx in range(w):
                if part.a[yy, xx] < 0: continue
                tx, ty = x + xx + dx, y + yy + dy
                sx, sy = xx + dx, yy + dy                      # (a part never shades itself)
                if 0 <= sx < w and 0 <= sy < h and part.a[sy, sx] >= 0: continue
                if 0 <= tx < self.w and 0 <= ty < self.h and self.a[ty, tx] in wall:
                    self.a[ty, tx] = self.i(c)

    def remap(self, x, y, w, h, m):
        """Recolour a box by a name map (a reveal's shade inside an opening)."""
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                v = self.at(xx, yy)
                if v in m: self.a[yy, xx] = self.i(m[v])

    def image(self, scale=1):
        rgb = np.zeros((self.h, self.w, 4), np.uint8)
        for i, n in enumerate(self.names):
            rgb[self.a == i] = (*self.pal[n], 255)
        im = Image.fromarray(rgb, 'RGBA')
        return im.resize((self.w * scale, self.h * scale), Image.NEAREST) if scale > 1 else im


def parts_sheet(ps, pal):
    w = sum(p.w for p in ps) + 4 * (len(ps) + 1); h = max(p.h for p in ps) + 8
    s = Canvas(w, h, pal); x = 4
    for p in ps: s.stamp(p, x, 4); x += p.w + 4
    return s


# ---- parts, each drawn once ------------------------------------------------------------------------------------

def part_window(w=46, h=72, rows=4, sky_rows=1, pal=PAL, shade='st_hi'):
    """Swedish two-casement window, `rows` panes a casement, white-painted wood (its shade `shade`). Glass a flat mid
    blue with a dark top-left inner edge (the bars' shadow) and, in the top `sky_rows` panes, the sky's reflection
    as two clean diagonal streaks. Frame lit top-left, shaded bottom-right (HOME's window with its own pane count)."""
    p = Canvas(w, h, pal)
    p.rect(0, 0, w, h, 'wh')
    p.hline(1, h - 1, w - 1, shade); p.vline(w - 1, 1, h - 1, shade)
    cw = (w - 3 - 3 - 2) // 2
    ph = (h - 6 - 2 * (rows - 1)) // rows
    for cx in (3, 3 + cw + 2):
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
    p.vline(3 + cw, 3, h - 6, 'wh'); p.vline(4 + cw, 3, h - 6, shade)
    return p


def part_eared_surround(w, h, t=4, ear=2, ear_h=5):
    """A painted plaster surround (light tone) with ears at the top corners: lit top and left, shaded right/bottom."""
    p = Canvas(w + 2 * ear, h)
    x0 = ear
    p.rect(x0, 0, w, t, 'pl_hi'); p.rect(x0, 0, t, h, 'pl_hi'); p.rect(x0 + w - t, 0, t, h, 'pl_hi')
    p.rect(x0, h - t, w, t, 'pl_hi')
    p.rect(0, 0, ear, ear_h, 'pl_hi'); p.rect(x0 + w, 0, ear, ear_h, 'pl_hi')          # the ears
    p.hline(0, 0, w + 2 * ear, 'tr_hi'); p.vline(0, 0, ear_h, 'tr_hi'); p.vline(x0, ear_h, h - ear_h, 'tr_hi')
    p.hline(0, ear_h - 1, ear, 'pl_sh'); p.hline(x0 + w, ear_h - 1, ear, 'pl_sh')       # under the ears
    p.vline(w + 2 * ear - 1, 1, ear_h - 1, 'pl_sh'); p.vline(x0 + w - 1, ear_h, h - ear_h, 'pl_sh')
    p.hline(x0 + 1, h - 1, w - 1, 'pl_sh')
    p.vline(x0 + t - 1, t - 1, h - 2 * t + 2, 'pl_sh'); p.hline(x0 + t - 1, t - 1, w - 2 * t + 2, 'pl_sh')  # inner arris
    return p


def part_hood(w, h=5):
    """A small plaster cornice over a window: lit top, shaded soffit."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'pl_hi'); p.hline(0, 0, w, 'tr_hi'); p.hline(1, h - 2, w - 2, 'pl'); p.hline(1, h - 1, w - 2, 'pl_sh')
    p.vline(w - 1, 1, h - 1, 'pl_sh'); p.put(0, h - 1, 'pl_sh')
    return p


def part_sill(w, h=4, c=('st_hi', 'st', 'st_sh', 'st_dk')):
    hi, mid, sh, dk = c
    p = Canvas(w, h)
    p.rect(0, 0, w, h, mid); p.hline(0, 0, w, hi); p.hline(0, h - 1, w, dk); p.vline(w - 1, 0, h, sh)
    return p


def part_flowerbox(w=50):
    """An oak window box with red geraniums: a row of round flower heads over leaves, light from the upper left."""
    p = Canvas(w, 12)
    p.rect(0, 6, w, 6, 'dr'); p.hline(0, 6, w, 'dr_hi'); p.hline(0, 11, w, 'dr_dk'); p.vline(w - 1, 6, 6, 'dr_dk')
    p.vline(0, 6, 6, 'dr_hi')
    for x in range(1, w - 1):                                       # leaves: a band with a scalloped top
        top = 2 if (x // 3) % 2 else 3
        for y in range(top, 6): p.put(x, y, 'lf')
    head = [".f.f.",                                                # one geranium head (a cluster), stamped
            "fffff",
            "ffffd",
            ".fdd."]
    for k, hx in enumerate(range(5, w - 6, 8)):                    # margins 5 and 6: centred in the box
        hy = 0 if k % 2 == 0 else 1
        for yy, row in enumerate(head):
            for xx, ch in enumerate(row):
                if ch != '.': p.put(hx + xx, hy + yy, 'fl' if ch == 'f' else 'fl_dk')
    for y in range(2, 6):                                           # no 1 px glass notch between a leaf and a head
        for x in range(1, w - 1):                                   # (review round 2: x 36, row 2 in both boxes)
            if p.a[y, x] < 0 and p.a[y, x - 1] >= 0 and p.a[y, x + 1] >= 0: p.put(x, y, 'lf')
    return p


def part_lesene(w, h):
    """The corner strip, painted a lighter tone: lit left arris, shaded right arris."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'pl_hi'); p.vline(0, 0, h, 'tr_hi'); p.vline(w - 1, 0, h, 'pl_sh')
    return p


def part_band(w, h=6):
    """The string course between the floors, a painted plaster band: lit top, shaded underside."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'pl_hi'); p.hline(0, 0, w, 'tr_hi'); p.hline(0, h - 2, w, 'pl'); p.hline(0, h - 1, w, 'pl_sh')
    return p


def part_anchor():
    """An iron wall anchor (ankarslut): an S of 1 px iron with a square plate in the middle; lit upper-left pixels."""
    art = [".###.",
           "#...#",
           "#....",
           ".#...",
           "..#..",
           "..#..",
           "..#..",
           ".#O#.",
           ".OOO.",
           ".###.",
           "..#..",
           "..#..",
           "..#..",
           "...#.",
           "....#",
           "#...#",
           ".###."]
    p = Canvas(5, len(art))
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch == '#': p.put(x, y, 'ink')
            elif ch == 'O': p.put(x, y, 'ir')
    return p


def part_pilaster(w=7, h=112):
    """A sandstone pilaster shaft with a sunken panel: lit left arris, shaded right, the panel's top/left in shade."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'st'); p.vline(0, 0, h, 'st_hi'); p.vline(w - 1, 0, h, 'st_sh')
    p.vline(2, 4, h - 8, 'st_sh'); p.hline(2, 4, w - 4, 'st_sh'); p.vline(w - 3, 5, h - 9, 'st_hi'); p.hline(3, h - 5, w - 5, 'st_hi')
    return p


def part_block(w, h):
    """A stone block (pilaster base or capital): lit top and left, shaded right, dark joint at the bottom."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'st'); p.hline(0, 0, w, 'st_hi'); p.vline(0, 0, h, 'st_hi')
    p.vline(w - 1, 1, h - 1, 'st_sh'); p.hline(0, h - 1, w, 'st_dk')
    return p


def part_door_leaf(w=23, h=98):
    """One leaf of an Old Town oak double door: a square top panel with a raised lozenge, a tall middle panel and a
    low bottom panel; light from the upper left."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'dr')
    p.vline(0, 0, h, 'dr_hi'); p.hline(0, 0, w, 'dr_hi')
    p.vline(w - 1, 1, h - 1, 'dr_dk')
    x0, pw = 4, w - 8
    for (py, ph) in ((5, pw), (5 + pw + 5, 44), (h - 26, 21)):
        p.hline(x0, py, pw, 'dr_dk'); p.vline(x0, py, ph, 'dr_dk')                     # sunk edge in shade
        p.hline(x0 + 1, py + ph - 1, pw - 1, 'dr_hi'); p.vline(x0 + pw - 1, py + 1, ph - 1, 'dr_hi')   # lit edge
    # the lozenge in the top panel, raised: lit upper-left faces, shaded lower-right faces
    cx, cy, r = x0 + pw // 2, 5 + pw // 2, pw // 2 - 3
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = abs(dx) + abs(dy)
            if d == r: p.put(cx + dx, cy + dy, 'dr_hi' if dy < 0 or (dy == 0 and dx < 0) else 'dr_dk')
    # the middle panel: a raised field, lit top-left
    py, ph = 5 + pw + 5, 44
    p.hline(x0 + 3, py + 3, pw - 6, 'dr_hi'); p.vline(x0 + 3, py + 3, ph - 6, 'dr_hi')
    p.hline(x0 + 4, py + ph - 4, pw - 7, 'dr_dk'); p.vline(x0 + pw - 4, py + 4, ph - 7, 'dr_dk')
    return p


def part_transom(w=46, h=14):
    """Four equal lights over the door: oak bars 2 px, a 2 px oak transom bar at the bottom; sky streak top left."""
    p = Canvas(w, h)
    p.rect(0, 0, w, h, 'dr')
    lw = (w - 3 * 2) // 4
    for k in range(4):
        x = k * (lw + 2)
        p.rect(x, 0, lw, h - 2, 'gl'); p.hline(x, 0, lw, 'ir'); p.vline(x, 0, h - 2, 'ir')
        for u in range(1, lw):                                   # one 2 px reflection streak per light
            for v in range(1, h - 2):
                if 8 <= u + v <= 9: p.put(x + u, v, 'gl_hi')
    p.hline(0, h - 2, w, 'dr_hi'); p.hline(0, h - 1, w, 'dr_dk')
    return p


def part_pediment(w, rise=10, t=4):
    """A segmental pediment: a stone arc (moulded cap) over a plain stone tympanum; lit top, shaded soffit."""
    import math
    p = Canvas(w, rise + t)
    cx = (w - 1) / 2
    R = (cx ** 2 + rise ** 2) / (2 * rise)
    for x in range(w):
        top = int(round(R - math.sqrt(max(0.0, R * R - (x - cx) ** 2))))
        for y in range(top, rise + t):
            p.put(x, y, 'st')
        p.put(x, top, 'st_hi')
        if top + 1 < rise + t: p.put(x, top + 1, 'st_hi' if x < cx else 'st')
        if top + t - 1 < rise + t: p.put(x, top + t - 1, 'st_sh')                     # the cap's shaded underside
    p.hline(0, rise + t - 1, w, 'st_sh')
    return p


def part_entablature(w, cap=3):
    """Architrave, frieze and a projecting cornice over the portal (the cornice `cap` px wider each side)."""
    h = 14
    p = Canvas(w, h)
    # cornice: rows 0-3, full width
    p.rect(0, 0, w, 4, 'st'); p.hline(0, 0, w, 'st_hi'); p.hline(0, 3, w, 'st_sh'); p.vline(w - 1, 0, 4, 'st_sh')
    p.hline(1, 1, w - 2, 'st_hi')
    # frieze and architrave: rows 4-13, inset by `cap`
    p.rect(cap, 4, w - 2 * cap, 10, 'st')
    p.hline(cap, 4, w - 2 * cap, 'st_dk')                          # the shadow under the cornice
    p.vline(cap, 5, 9, 'st_hi'); p.vline(w - cap - 1, 4, 10, 'st_sh')
    p.hline(cap, 10, w - 2 * cap, 'st_hi'); p.hline(cap, 13, w - 2 * cap, 'st_sh')   # architrave fascia
    return p


# ---- the house ----------------------------------------------------------------------------------------------------

def build():
    c = Canvas(W, H)
    g = lambda y: y + OFF                                     # game y -> image row
    c.rect(0, 0, W, H, 'pl')
    WX = 18                                                    # the window opening, x 18..63
    DX = 87                                                    # the door opening, x 87..132 (game 3655..3700)
    EAR = 2
    # upper floor: the window bottoms over the window and over the door, eared surrounds, sills, flower boxes
    UB = g(20)                                                 # the upper windows' bottom (game y 20)
    for wx in (WX, DX):
        sur = part_eared_surround(46 + 8, 43, ear=EAR)              # its bottom band hides under the 3 px sill
        c.stamp(sur, wx - 4 - EAR, UB - 40); c.shadow(sur, wx - 4 - EAR, UB - 40)
        up = part_window(46, 40, rows=2, sky_rows=2)
        c.stamp(up, wx, UB - 40)
        sill = part_sill(46 + 10, 3)
        c.stamp(sill, wx - 5, UB); c.shadow(sill, wx - 5, UB)
        box = part_flowerbox(48)
        c.stamp(box, wx - 1, UB - 11); c.shadow(box, wx - 1, UB - 11)
    # the iron wall anchors at the floor line: by the corner and between the bays
    for ax in (10, 67):                                         # centres 12 and 69: symmetric about the window axis
        an = part_anchor(); c.stamp(an, ax, g(26)); c.shadow(an, ax, g(26))
    # the smooth stone socle, 16 px
    c.rect(0, g(158), W, 16, 'st')
    c.hline(0, g(158), W, 'st_hi'); c.hline(0, g(160), W, 'st_sh'); c.hline(0, g(173), W, 'st_sh')
    c.hline(0, g(166), W, 'st_sh'); c.hline(0, g(167), W, 'st_hi')                       # one course joint (HOME's grain)
    # the corner lesene, on the socle, up out of the top
    les = part_lesene(8, g(158))
    c.stamp(les, 0, 0); c.shadow(les, 0, 0, dx=2, dy=0)
    # the window: eared surround, hood, the window, sill
    WY, WH = g(66), 72
    sur = part_eared_surround(46 + 8, WH + 8, ear=EAR)
    c.stamp(sur, WX - 4 - EAR, WY - 4); c.shadow(sur, WX - 4 - EAR, WY - 4)
    hood = part_hood(46 + 8 + 2 * EAR + 4, 5)
    c.stamp(hood, WX - 4 - EAR - 2, WY - 9); c.shadow(hood, WX - 4 - EAR - 2, WY - 9)
    win = part_window(46, WH, rows=4)
    c.stamp(win, WX, WY)
    c.remap(WX, WY, 2, WH, {'wh': 'st_hi'})                                # the reveal's shade on the left
    c.remap(WX, WY, 46, 2, {'wh': 'st_hi'})                                # and under the lintel (the frame's own
                                                                           # shade line stays one tone)
    sill = part_sill(46 + 14, 5); c.stamp(sill, WX - 7, WY + WH + 4); c.shadow(sill, WX - 7, WY + WH + 4)
    # the portal: pilasters on bases with capitals, entablature, segmental pediment
    PL, PR = DX - 7, DX + 46                                   # pilaster x (7 px each)
    top = g(61)                                                # transom top (12 px); leaves from game y 73 to 171
    # the lintel between the capitals, its underside in the opening's shade
    c.rect(PL + 7, top - 5, 46, 5, 'st'); c.hline(PL + 7, top - 5, 46, 'st_hi'); c.hline(PL + 7, top - 1, 46, 'st_sh')
    for px in (PL, PR):
        sh = part_pilaster(7, g(149) - top)
        c.stamp(sh, px, top); c.shadow(sh, px, top)
        base = part_block(7, 22); c.stamp(base, px, g(149)); c.shadow(base, px, g(149), on=('pl', 'pl_hi'))
        c.shadow(base, px, g(149), on=('st', 'st_hi'), c='st_sh')
        cap = part_block(9, 5); c.stamp(cap, px - 1, top - 5); c.shadow(cap, px - 1, top - 5)
    ent = part_entablature(46 + 14 + 6, cap=3)
    ex = PL - 3
    c.stamp(ent, ex, top - 5 - 14); c.shadow(ent, ex, top - 5 - 14)
    ped = part_pediment(ent.w, rise=8, t=4)
    c.stamp(ped, ex, top - 19 - ped.h); c.shadow(ped, ex, top - 19 - ped.h)
    # the opening: transom and the two leaves, recessed
    tr = part_transom(46, 12); c.stamp(tr, DX, top)
    for k in (0, 1):
        leaf = part_door_leaf(23, 98); c.stamp(leaf, DX + 23 * k, g(73))
    c.vline(DX + 22, g(73), 98, 'ink')                         # the meeting gap
    for kx in (DX + 19, DX + 25):                              # brass knobs, each with its 2 px shade under it
        c.rect(kx, g(118), 2, 2, 'brass'); c.hline(kx, g(120), 2, 'dr_dk')
    c.remap(DX, top, 3, g(171) - top, {'dr_hi': 'dr', 'dr': 'dr_dk', 'gl': 'ir', 'gl_hi': 'gl'})
    c.remap(DX, top, 46, 2, {'dr_hi': 'dr', 'dr': 'dr_dk', 'gl': 'ir', 'gl_hi': 'gl'})
    step = Canvas(46 + 18, 3)
    step.rect(0, 0, step.w, 3, 'st'); step.hline(0, 0, step.w, 'st_hi'); step.hline(0, 2, step.w, 'st_sh')
    c.stamp(step, DX - 9, g(171))
    return c


def verify(c):
    """The repeats are pixel-identical in the finished image (the window check of asset_qa sees no panes this big):
    the two upper windows with their surrounds and flower boxes, the two pilasters with their bases and capitals."""
    g = lambda y: y + OFF
    a = c.a
    same = lambda x0, x1, y, w, h: np.array_equal(a[y:y + h, x0:x0 + w], a[y:y + h, x1:x1 + w])
    ok = {'upper windows and flower boxes': same(18 - 6, 87 - 6, 0, 58, g(20) + 3),
          'pilaster capitals': same(87 - 7 - 1, 87 + 46 - 1, g(61) - 5, 9, 5),
          'pilasters': same(87 - 7, 87 + 46, g(61), 7, g(171) - g(61))}
    for k, v in ok.items():
        if not v: sys.exit(f'verify: {k} differ')
    return ok


def parts():
    return [part_door_leaf(), part_transom(), part_window(46, 72), part_eared_surround(54, 80), part_hood(62),
            part_pilaster(7, 60), part_block(9, 22), part_pediment(68, 9), part_entablature(68, 4), part_flowerbox(50),
            part_anchor(), part_sill(60, 5)]


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'riverwalk/art/scene/rw_gable.png'
    c = build()
    c.image().save(out)
    os.makedirs('art/source/rw_gable', exist_ok=True)
    parts_sheet(parts(), PAL).image(8).save('art/source/rw_gable/parts_8x.png')
    a = c.a
    used = len(np.unique(a[a >= 0]))
    print(f'{out}: {W}x{H}, {used} colours; identical: {", ".join(verify(c))}')
