#!/usr/bin/env python3
"""River Walk CAFE, screen 12, at true scale (46 px a metre), taller than the viewport. 25 Oct 2026 (night).

The cafe where Mia waits, the level's last building (replaces the prop using art "cafe", whose window railings the
script clean pass holed; the old file stays in the repo). Built like the approved HOME house (tools/build_rw_home.py)
and the GABLE beside it (tools/build_rw_gable.py, whose palette-aware Canvas and window it uses): back layer,
decoration, no outline (every edge a darker shade of its own material), parts drawn once and stamped on an integer
grid, binary alpha, at most 20 colours, volume from the light (sun upper left: parts that stand out of the wall drop
a 2 px shadow down and to the right, the awning a deeper one; openings recessed with a shaded top and left reveal).

Cream plaster; a sage-painted shopfront: two piers under a plain fascia (no lettering, no sign,
no logo anywhere), a shop window of two equal lights (frame and mullion stamped, the two lights pixel-identical) over
a panelled stall riser, two green enamel lamps hanging inside, a striped awning (red and cream stripes, 10 px, a clean
repeat, its scalloped valance stamped per stripe; the 30 px light pitch is three stripes, so the awning's shadow
falls the same on both lights), and a glazed shop door under a three-light transom on a granite
step. Upper floor: the bottoms of two windows in stucco surrounds on corbelled sills, cut by the top edge.

Mia (game x 3768-3790, feet 184) stands in front of the shop window's right light and the pier: behind her, at game
y 140-184, only the white stall riser panel, the pier and the granite base, so her dark hoodie reads.

Sizes (46 px/m): door opening 46 x 98 (leaf) under a 14 px transom, shop window lights 27 x 74, stall riser 27,
granite base 16, the cornice 150 px above the pavement.

Image 124 x 180, drawn with its bottom on the pavement's back edge (prop x0 3716, y1 174), its right edge on the
level's right edge (3840, the camera never passes it): bottom row at game y 173, top row at game y -6, so its top is
never on screen (tools/check_backdrop.py).

Usage: build_rw_cafe.py [OUT.png]   default riverwalk/art/scene/rw_cafe.png (+ an 8x parts sheet in art/source/rw_cafe/)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rw_gable import Canvas, part_window, parts_sheet      # noqa: E402  (shared with the gable)

W, H = 124, 180
OFF = 6                      # image row = game y + OFF (the bottom row, 179, is drawn at game y 173)

PAL = {                      # 20 colours; glass, iron, white, brass, the reds and the granite shared with the street
    'cr_hi': (255, 248, 234), 'cr': (246, 232, 206), 'cr_sh': (222, 200, 166), 'cr_dk': (180, 156, 124),  # cream plaster
    'sg_hi': (180, 210, 180), 'sg': (138, 176, 146), 'sg_sh': (104, 142, 116), 'sg_dk': (72, 106, 88),    # sage paint
    'wh': (247, 249, 250),                                                                                # window white
    'aw_hi': (238, 112, 96), 'fl': (218, 70, 64), 'fl_dk': (164, 44, 48),                                 # awning red
    'gl_hi': (196, 220, 236), 'gl': (98, 126, 152),                                                       # glass
    'ir': (86, 88, 100), 'ink': (40, 42, 54),                                                             # iron, dark
    'gr_hi': (194, 196, 202), 'gr': (156, 158, 168), 'gr_sh': (118, 120, 132),                            # granite
    'brass': (244, 204, 105),                                                                             # brass
}
assert len(PAL) <= 20

WALL = ('cr', 'cr_hi')
SHADE = {'cr': 'cr_sh', 'cr_hi': 'cr', 'wh': 'cr_sh', 'gl': 'ir', 'gl_hi': 'gl', 'gr_hi': 'gr', 'gr': 'gr_sh',
         'sg_hi': 'sg', 'sg': 'sg_sh', 'sg_sh': 'sg_dk'}



def C(w, h): return Canvas(w, h, PAL)


def shade_cast(c, part, x, y, dx=2, dy=2, m=None, x_min=0):
    """The part's cast shadow, every material by its own shade (the awning falls on glass, paint and plaster)."""
    m = m or SHADE
    h, w = part.a.shape
    for yy in range(h):
        for xx in range(w):
            if part.a[yy, xx] < 0: continue
            sx, sy = xx + dx, yy + dy
            if 0 <= sx < w and 0 <= sy < h and part.a[sy, sx] >= 0: continue
            if x + sx < x_min: continue
            v = c.at(x + sx, y + sy)
            if v in m: c.put(x + sx, y + sy, m[v])


# ---- parts, each drawn once ------------------------------------------------------------------------------------

def part_frame(w, h, t=4):
    """A cream stucco surround: lit top and left, shaded right and bottom, a shaded inner arris."""
    p = C(w, h)
    p.rect(0, 0, w, t, 'cr_hi'); p.rect(0, 0, t, h, 'cr_hi'); p.rect(w - t, 0, t, h, 'cr_hi'); p.rect(0, h - t, w, t, 'cr_hi')
    p.vline(w - 1, 1, h - 1, 'cr_sh'); p.hline(1, h - 1, w - 1, 'cr_sh')
    p.vline(t - 1, t - 1, h - 2 * t + 2, 'cr_sh'); p.hline(t - 1, t - 1, w - 2 * t + 2, 'cr_sh')
    return p


def part_sill(w, h=4):
    """A cream stone sill on two small corbels."""
    p = C(w, h + 3)
    p.rect(0, 0, w, h, 'cr'); p.hline(0, 0, w, 'cr_hi'); p.hline(0, h - 1, w, 'cr_dk'); p.vline(w - 1, 0, h, 'cr_sh')
    for x in (4, w - 8):
        p.rect(x, h, 4, 2, 'cr'); p.hline(x, h + 2, 4, 'cr_sh'); p.put(x + 3, h, 'cr_sh'); p.put(x + 3, h + 1, 'cr_sh')
    return p


def part_band(w, h=8):
    """The cornice between the floors: cream, lit top, shaded underside."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'cr'); p.hline(0, 0, w, 'cr_hi'); p.hline(0, 1, w, 'cr_hi')
    p.hline(0, h - 3, w, 'cr_sh'); p.hline(0, h - 2, w, 'cr_sh'); p.hline(0, h - 1, w, 'cr_dk')
    return p


def part_fascia(w, h=12):
    """The shopfront's entablature in sage paint: a 3 px cornice, the plain fascia board (no lettering), a 2 px
    architrave."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'sg')
    p.hline(0, 0, w, 'sg_hi'); p.hline(0, 1, w, 'sg_hi'); p.hline(0, 2, w, 'sg_dk')            # the cornice
    p.hline(0, 3, w, 'sg_sh')                                                                     # its shade on the board
    p.hline(0, h - 3, w, 'sg_hi'); p.hline(0, h - 2, w, 'sg'); p.hline(0, h - 1, w, 'sg_dk')     # the architrave
    return p


def part_pier(w, h):
    """A painted pier (pilaster) of the shopfront: lit left arris, shaded right."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'sg'); p.vline(0, 0, h, 'sg_hi'); p.vline(w - 1, 0, h, 'sg_sh')
    return p


def part_light(w=27, h=74):
    """One shop window light: flat glass with the bars' shadow on its top and left inner edge and the sky's reflection
    as two clean diagonal streaks (3 px and 1 px), below the awning's shadow."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'gl'); p.hline(0, 0, w, 'ir'); p.vline(0, 0, h, 'ir')
    for u in range(1, w):
        for v in range(24, h):
            sd = u + (v - 24)
            if 10 <= sd <= 12 or sd == 16: p.put(u, v, 'gl_hi')
    return p


def part_lamp():
    """A brass pendant lamp on its cord: a dome shade, lit upper left, its dark rim and the warm bulb under it."""
    art = ["...k...",
           "...k...",
           "...k...",
           "...k...",
           "...k...",
           "..hbb..",
           ".hbbbb.",
           "hbbbbbd",
           "ddddddd",
           "..yyy.."]
    p = C(7, len(art))
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch != '.': p.put(x, y, {'k': 'ink', 'h': 'cr_hi', 'b': 'brass', 'd': 'ir', 'y': 'cr_hi'}[ch])
    return p


def part_shop_window(lw=27, lh=74, t=3, bar=3):
    """The shop window frame (sage paint) with its two equal lights, each stamped from one part with its lamp."""
    w = t + lw + bar + lw + t; h = t + lh + t
    p = C(w, h)
    p.rect(0, 0, w, h, 'sg')
    p.hline(0, 0, w, 'sg_hi'); p.vline(0, 0, h, 'sg_hi')
    p.vline(w - 1, 1, h - 1, 'sg_sh'); p.hline(1, h - 1, w - 1, 'sg_sh')
    p.vline(t + lw + bar - 1, t, lh, 'sg_sh')                        # the mullion's shaded right arris
    light = part_light(lw, lh); lamp = part_lamp()
    for x in (t, t + lw + bar):
        p.stamp(light, x, t)
        p.stamp(lamp, x + (lw - lamp.w) // 2, t + 17)
        p.vline(x + (lw - lamp.w) // 2 + 3, t + 1, 16, 'ink')          # the cord up to the ceiling
    return p


def part_riser_panel(w=27, h=21):
    """One raised panel of the stall riser (sage paint): sunk edge in shade top-left, lit bottom-right edge, the
    raised field lit top-left."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'sg')
    p.hline(0, 0, w, 'sg_dk'); p.vline(0, 0, h, 'sg_dk')
    p.hline(1, h - 1, w - 1, 'sg_hi'); p.vline(w - 1, 1, h - 1, 'sg_hi')
    p.hline(3, 3, w - 6, 'sg_hi'); p.vline(3, 3, h - 6, 'sg_hi')
    p.hline(4, h - 4, w - 7, 'sg_sh'); p.vline(w - 4, 4, h - 7, 'sg_sh')
    return p


def part_awning(stripes=7, sw=10, slope=13):
    """The awning, front-on: a roller box, the sloping cloth (lit, the thin cap) and the valance with a scalloped
    edge, red and cream stripes `sw` px wide in a clean repeat; every stripe's scallop is the same stamp."""
    scallop = ["1111111111",
               "1111111111",
               "1111111111",
               "1111111111",
               "1111111111",
               ".11111111.",
               "..111111.."]
    w = stripes * sw; h = 3 + slope + len(scallop)
    p = C(w, h)
    p.rect(0, 0, w, 3, 'gr'); p.hline(0, 0, w, 'gr_hi'); p.hline(0, 2, w, 'gr_sh')            # the roller box
    for k in range(stripes):
        red = k % 2 == 0
        hi, mid, dk = ('aw_hi', 'fl', 'fl_dk') if red else ('cr_hi', 'cr', 'cr_sh')
        x0 = k * sw
        p.rect(x0, 3, sw, slope, hi)                                  # the sloping cloth, in the sun
        p.hline(x0, 3, sw, mid)                                       # its top, in the box's shade
        for yy, row in enumerate(scallop):                            # the valance, facing us
            for xx, ch in enumerate(row):
                if ch == '1': p.put(x0 + xx, 3 + slope + yy, mid)
        p.hline(x0, 3 + slope, sw, dk)                                # the fold between cloth and valance
        p.put(x0 + 1, 3 + slope + 5, dk); p.put(x0 + sw - 2, 3 + slope + 5, dk)  # the scallop's rounded bottom
        p.hline(x0 + 2, 3 + slope + 6, sw - 4, dk)
    p.vline(w - 1, 3, slope, 'fl_dk')
    return p


def part_door_leaf(w=46, h=98):
    """A glazed shop door in sage paint: stiles and rails, a big light with the sky's streaks, a brass push bar,
    a raised kick panel; light from the upper left."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'sg')
    p.vline(0, 0, h, 'sg_hi'); p.hline(0, 0, w, 'sg_hi'); p.vline(w - 1, 1, h - 1, 'sg_sh')
    gx, gy, gw, gh = 6, 6, w - 12, 58
    p.rect(gx, gy, gw, gh, 'gl'); p.hline(gx, gy, gw, 'ir'); p.vline(gx, gy, gh, 'ir')
    p.hline(gx, gy + gh, gw + 1, 'sg_hi'); p.vline(gx + gw, gy, gh + 1, 'sg_hi')
    for u in range(1, gw):
        for v in range(1, gh):
            sd = u + v
            if 14 <= sd <= 16 or sd == 20: p.put(gx + u, gy + v, 'gl_hi')
    p.rect(gx + 2, gy + 40, gw - 4, 2, 'brass'); p.hline(gx + 2, gy + 42, gw - 4, 'ir')       # the push bar
    py = gy + gh + 6; ph = h - py - 7
    p.hline(gx, py, gw, 'sg_dk'); p.vline(gx, py, ph, 'sg_dk')
    p.hline(gx + 1, py + ph - 1, gw - 1, 'sg_hi'); p.vline(gx + gw - 1, py + 1, ph - 1, 'sg_hi')
    p.hline(gx + 3, py + 3, gw - 6, 'sg_hi'); p.vline(gx + 3, py + 3, ph - 6, 'sg_hi')
    p.hline(gx + 4, py + ph - 4, gw - 7, 'sg_sh'); p.vline(gx + gw - 4, py + 4, ph - 7, 'sg_sh')
    return p


def part_transom(w=46, h=14, n=3, bar=2):
    """The transom over the door: `n` equal lights between sage bars."""
    p = C(w, h)
    p.rect(0, 0, w, h, 'sg')
    lw = (w - (n - 1) * bar) // n
    for k in range(n):
        x = k * (lw + bar)
        p.rect(x, 0, lw, h, 'gl'); p.hline(x, 0, lw, 'ir'); p.vline(x, 0, h, 'ir')
        for u in range(1, lw):
            for v in range(1, h):
                if 7 <= u + v <= 8: p.put(x + u, v, 'gl_hi')
    return p


def part_granite(w, h=8):
    p = C(w, h)
    p.rect(0, 0, w, h, 'gr'); p.hline(0, 0, w, 'gr_hi'); p.vline(0, 0, h - 1, 'gr_hi')
    p.hline(0, h - 1, w, 'gr_sh'); p.vline(w - 1, 1, h - 1, 'gr_sh')
    return p


# ---- the cafe -----------------------------------------------------------------------------------------------------

def build():
    c = C(W, H)
    g = lambda y: y + OFF                                     # game y -> image row
    c.rect(0, 0, W, H, 'cr')
    SX = 6                                                     # the shop window frame, x 6..68
    PX = SX + 63                                               # the middle pier, x 69..75
    DX = 78                                                    # the door opening, x 78..123 (game 3794..3839)
    # upper floor: two window bottoms in stucco surrounds, on sills with corbels
    UB = g(16)
    for wx in (15, 74):                                        # (44 tall: the image's top row cuts the meeting rail)
        fr = part_frame(54, 48); c.stamp(fr, wx - 4, UB - 44); c.shadow(fr, wx - 4, UB - 44, on=WALL, c='cr_sh')
        up = part_window(46, 44, rows=2, sky_rows=2, pal=PAL, shade='cr_sh'); c.stamp(up, wx, UB - 44)
        c.remap(wx, UB - 44, 2, 44, {'wh': 'cr_sh'})                             # the reveal's shade on the left
        sill = part_sill(58, 4); c.stamp(sill, wx - 6, UB); c.shadow(sill, wx - 6, UB, on=WALL, c='cr_sh')
    # the cornice between the floors (150 px above the pavement)
    band = part_band(W, 8); c.stamp(band, 0, g(24)); c.shadow(band, 0, g(24), dx=0, dy=3, on=WALL, c='cr_sh')
    # the granite base, two courses, staggered joints
    for row, (py, ph) in enumerate(((g(158), 8), (g(166), 8))):
        x = -10 if row else 0
        while x < W:
            b = part_granite(26, ph); c.stamp(b, x, py); x += 26
    # the shopfront: fascia, piers, the shop window over its stall riser, the door frame
    fas = part_fascia(W, 12); c.stamp(fas, 0, g(36))
    for px, pw in ((0, 6), (PX, DX - 2 - PX)):
        pr = part_pier(pw, g(158) - g(48)); c.stamp(pr, px, g(48))
    sw = part_shop_window()
    c.stamp(sw, SX, g(50))
    c.rect(SX, g(130), 63, 28, 'sg')                           # the stall riser: sill, two raised panels, bottom rail
    c.hline(SX, g(130), 63, 'sg_hi'); c.hline(SX, g(132), 63, 'sg_sh')
    for k in (0, 1):
        pan = part_riser_panel(27, 21); c.stamp(pan, SX + 3 + k * 30, g(134))
    c.hline(SX, g(157), 63, 'sg_sh')
    c.rect(DX - 2, g(48), 2, g(171) - g(48), 'sg'); c.rect(DX + 46, g(48), W - DX - 46, g(171) - g(48), 'sg')
    c.vline(W - 1, g(48), g(171) - g(48), 'sg_sh')
    c.rect(DX, g(48), 46, g(57) - g(48), 'sg'); c.hline(DX, g(56), 46, 'sg_sh')
    tr = part_transom(46, 14); c.stamp(tr, DX, g(57))
    c.rect(DX, g(71), 46, 2, 'sg'); c.hline(DX, g(71), 46, 'sg_hi'); c.hline(DX, g(72), 46, 'sg_sh')
    leaf = part_door_leaf(46, 98); c.stamp(leaf, DX, g(73))
    REV = {'sg_hi': 'sg_sh', 'sg': 'sg_sh', 'gl': 'ir', 'gl_hi': 'gl'}       # (the frame's own shade stays one tone)
    c.remap(DX, g(57), 3, g(171) - g(57), REV)                 # the reveal's shade: left side and under the lintels
    c.remap(DX + 3, g(57), 43, 2, REV); c.remap(DX + 3, g(73), 43, 2, REV)
    step = part_granite(46 + 6, 3); c.stamp(step, DX - 3, g(171))           # the door's granite step
    # the awning over the shop window, last: its deep shadow on the glass, the frame and the piers
    aw = part_awning(); ax = SX + 63 // 2 - aw.w // 2
    c.stamp(aw, ax, g(48)); shade_cast(c, aw, ax, g(48), 2, 3, x_min=SX)      # (not on the left pier: a ragged sliver)
    return c


def verify(c):
    """The repeats are pixel-identical in the finished image (the window check of asset_qa sees no panes this big):
    the two shop window lights below the awning (with their lamps and the awning's shadow), the two stall riser
    panels, the two upper windows, every pair of awning stripes."""
    g = lambda y: y + OFF
    a = c.a
    same = lambda x0, x1, y, w, h: np.array_equal(a[y:y + h, x0:x0 + w], a[y:y + h, x1:x1 + w])
    ok = {'shop lights': same(9, 39, g(71), 27, g(127) - g(71)), 'riser panels': same(9, 39, g(134), 27, 21),
          'upper windows': same(15, 74, 0, 46, g(16)),
          'awning stripes': all(same(2, 2 + 20 * k, g(48), 20, 21) for k in (1, 2))}
    for k, v in ok.items():
        if not v: sys.exit(f'verify: {k} differ')
    return ok


def parts():
    return [part_awning(), part_shop_window(), part_riser_panel(), part_door_leaf(), part_transom(),
            part_lamp(), part_frame(54, 44), part_sill(58), part_granite(26)]


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'riverwalk/art/scene/rw_cafe.png'
    c = build()
    c.image().save(out)
    os.makedirs('art/source/rw_cafe', exist_ok=True)
    parts_sheet(parts(), PAL).image(8).save('art/source/rw_cafe/parts_8x.png')
    a = c.a
    used = len(np.unique(a[a >= 0]))
    print(f'{out}: {W}x{H}, {used} colours; identical: {", ".join(verify(c))}')
