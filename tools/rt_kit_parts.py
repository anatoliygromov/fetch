#!/usr/bin/env python3
"""rt_kit_parts.py: the Rooftops parts kit, BUILT clean on the grid from the concept's design (8 Nov; owner 12:07 on the
cut window and chimney: the cut pieces carry the concept's pixel noise). Sizes, layout and colours are the concept's
(rt_hotel_concept_a, the lock-and-complete screen); the drawing is by rule: light from the upper left, 3-4 tones per
material, no specks, transparent round the piece, complete (nothing left hidden). Writes art/source/rt_kit/*.png."""
import os, numpy as np
from PIL import Image
OUT = 'art/source/rt_kit'; os.makedirs(OUT, exist_ok=True)
C = {  # the concept's own colours (final.png, sampled)
    'w_dk': (67, 42, 39), 'w_sh': (98, 62, 44), 'w': (117, 82, 62), 'w_hi': (154, 114, 81),           # window wood
    'gl': (87, 101, 107), 'gl_dk': (59, 68, 82), 'gl_hi': (137, 148, 149),                              # glass
    'st_hi': (204, 174, 139), 'st': (162, 139, 117), 'st_sh': (127, 104, 95), 'st_dk': (71, 59, 57),     # sandstone
    'ch_hi': (161, 128, 107), 'ch': (141, 109, 90), 'ch_sh': (98, 71, 66), 'ch_dk': (79, 64, 57),        # chimney stucco
    'cl_hi': (223, 123, 77), 'cl': (198, 107, 74), 'cl_sh': (133, 58, 44), 'cl_dk': (70, 32, 27),        # clay pots
}
def canvas(w, h): return np.zeros((h, w, 4), np.uint8)
def px(a, x, y, c):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]: a[y, x, :3] = C[c]; a[y, x, 3] = 255
def rect(a, x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1): px(a, x, y, c)

def window():
    """22 x 24 four-pane window (the concept's size and layout) and a 24 px sill: a dark outer frame, the inner frame
    lit on top and left, shaded right and bottom; mullion and transom 2 px (lit left/top, shade right/bottom); each
    pane glass with a shadow row under the frame and a 2 px glint"""
    a = canvas(24, 27); ox = 1
    rect(a, ox, 0, ox + 22, 24, 'w_dk')
    rect(a, ox + 1, 1, ox + 21, 23, 'w')
    rect(a, ox + 1, 1, ox + 21, 2, 'w_hi'); rect(a, ox + 1, 1, ox + 2, 23, 'w_hi')           # lit top and left
    rect(a, ox + 20, 2, ox + 21, 23, 'w_sh'); rect(a, ox + 2, 22, ox + 21, 23, 'w_sh')       # shaded right and bottom
    for (x0, y0) in ((3, 3), (12, 3), (3, 13), (12, 13)):                                    # panes 7 x 8
        rect(a, ox + x0, y0, ox + x0 + 7, y0 + 8, 'gl')
        rect(a, ox + x0, y0, ox + x0 + 7, y0 + 1, 'gl_dk'); rect(a, ox + x0, y0, ox + x0 + 1, y0 + 8, 'gl_dk')
        px(a, ox + x0 + 4, y0 + 2, 'gl_hi'); px(a, ox + x0 + 3, y0 + 3, 'gl_hi')
    rect(a, ox + 10, 3, ox + 11, 21, 'w_hi'); rect(a, ox + 11, 3, ox + 12, 21, 'w_sh')        # mullion
    rect(a, ox + 3, 11, ox + 19, 12, 'w_hi'); rect(a, ox + 3, 12, ox + 19, 13, 'w_sh')        # transom
    px(a, ox + 10, 12, 'w_hi'); px(a, ox + 11, 11, 'w_hi')
    rect(a, 0, 24, 24, 25, 'st_hi'); rect(a, 0, 25, 24, 26, 'st'); rect(a, 1, 26, 23, 27, 'st_sh')   # sill
    return a

def pot(a, x, y1, h):
    """a clay chimney pot standing on y1 (the concept's shape): a near-straight cylinder 8 px wide, a small rounded lip
    1 px wider each side on top with a dark opening, a 2-row foot as wide as the lip; lit left, shaded right"""
    def row(y, x0, x1, top=False, under=False):
        for xx in range(x0, x1):
            k, w = xx - x0, x1 - x0
            c = 'cl_hi' if k < 2 else ('cl_sh' if k >= w - 2 else 'cl')
            if xx == x1 - 1: c = 'cl_dk'
            if under and c != 'cl_dk': c = 'cl_sh'
            px(a, xx, y, c)
    yt = y1 - h
    row(yt, x + 1, x + 9)                                     # lip top, corners rounded
    for xx in range(x + 3, x + 7): px(a, xx, yt, 'cl_dk')     # the opening
    row(yt + 1, x, x + 10); row(yt + 2, x, x + 10, under=True)   # the lip, its underside
    for y in range(yt + 3, y1 - 2): row(y, x + 1, x + 9)      # the body
    row(y1 - 2, x, x + 10); row(y1 - 1, x, x + 10, under=True)   # the foot

def chimney(body_w=36, body_h=30, pots=(13, 16, 13)):
    """the big chimney: stucco body (lit left band, shaded right band, darker edges, the slab's shadow under it),
    a sandstone slab overhanging 3 px, three clay pots on even spacing (the middle one taller)"""
    W = body_w + 6; top = max(pots) + 1; H = top + 5 + body_h
    a = canvas(W, H); bx = 3; sy = top                                                        # slab top row
    rect(a, bx, sy + 5, bx + body_w, H, 'ch')
    rect(a, bx, sy + 5, bx + 3, H, 'ch_hi'); rect(a, bx + body_w - 4, sy + 5, bx + body_w, H, 'ch_sh')
    rect(a, bx, sy + 5, bx + 1, H, 'ch_dk'); rect(a, bx + body_w - 1, sy + 5, bx + body_w, H, 'ch_dk')
    rect(a, bx + 1, sy + 5, bx + body_w - 1, sy + 7, 'ch_sh')                                 # the slab's shadow
    rect(a, bx + 1, sy + 12, bx + body_w - 1, sy + 13, 'ch_hi'); rect(a, bx + 1, sy + 13, bx + body_w - 1, sy + 14, 'ch_sh')   # string course
    rect(a, 0, sy, W, sy + 5, 'st'); rect(a, 0, sy, W, sy + 1, 'st_hi')
    rect(a, 0, sy + 3, W, sy + 4, 'st_sh'); rect(a, 0, sy + 4, W, sy + 5, 'st_dk')
    rect(a, 0, sy + 1, 1, sy + 4, 'st_hi'); rect(a, W - 1, sy + 1, W, sy + 4, 'st_sh')
    n = len(pots); gap = (body_w - n * 10) // (n + 1)
    for i, h in enumerate(pots):
        pot(a, bx + gap + i * (10 + gap), sy, h)
    return a

if __name__ == '__main__':
    Image.fromarray(window()).save(f'{OUT}/window.png')
    Image.fromarray(chimney()).save(f'{OUT}/chimney_big.png')
    print('window', window().shape[1::-1], 'chimney_big', chimney().shape[1::-1])
