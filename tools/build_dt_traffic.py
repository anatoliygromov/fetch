#!/usr/bin/env python3
"""build_dt_traffic.py: the Downtown traffic family (6 Nov 2026): the cargo bike (cut 1:1 from a SpriteCook render)
and the vintage tram (BUILT at true scale from parts drawn once, in the colours and design of a SpriteCook render).

  python3 -I tools/build_dt_traffic.py cargo          cut -> clean -> key -> wheels by rule -> outline (art/source/dt_cargo_bike/)
  python3 -I tools/build_dt_traffic.py cargo_pedal    the pedal loop from the pixel-engine sheet (legs only, wheels by rule)
  python3 -I tools/build_dt_traffic.py tram           riverwalk/art/scene/tram_vintage.png + tram_vintage_wheel.png

Every pixel changed after the cut is listed in art/source/NAME/edits*.json. Never resampled."""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_traffic as bt

N = 'dt_cargo_bike'; S = f'art/source/{N}'
FRONT, BACK = (92, 188, (10, 11, 12)), (180, 184, (14, 15, 16))      # blockout centres and radii


def cargo():
    os.system(f'python3 -I tools/cleanpass.py {S}/{N}_cut.png {S}/{N}_clean.png --tol 90')
    ked = bt.fix_key(f'{S}/{N}_clean.png', f'{S}/{N}_clean.png')
    cj = json.load(open(f'art/gen/out/{N}.cut.json')); bx, by = cj['box'][:2]
    a = np.array(Image.open(f'{S}/{N}_clean.png').convert('RGBA'))
    cent = []
    for gx, gy, rs in (FRONT, BACK):
        s, cx, cy, r = bt.fit_wheel(a, gx - bx, gy - by, rs); cent.append((cx, cy, r))
    f, e = bt.wheels(N, src=f'{S}/{N}_clean.png', centres=cent)
    os.system(f'python3 -I tools/outline_complete.py {S}/{N}_wheels.png {S}/{N}_ol.png --skip-bottom')
    json.dump({'centres': [list(map(int, c)) for c in f], 'key_edits': ked, 'wheel_edits': e}, open(f'{S}/edits_build.json', 'w'))
    print('wheels', f)


if __name__ == '__main__' and sys.argv[1] == 'cargo':
    cargo()


def _edits(a, out, why, mask=None):
    ed = []
    for y, x in zip(*np.nonzero((out != a).any(2) if mask is None else ((out != a).any(2) & mask))):
        ed.append({'x': int(x), 'y': int(y), 'from': [int(v) for v in a[y, x]], 'to': [int(v) for v in out[y, x]], 'why': why})
    return ed


def cargo_polish():
    """Hand polish by rule on the new cut (art/source/dt_cargo_bike/edits_polish.json): stray reds off the helmet,
    lone pixels in the loaves take their neighbours' colour, the box face drawn again as three planks of one pattern
    with metal corner plates (the cut's planks had uneven rows and specks)."""
    a = np.array(Image.open(f'{S}/{N}_ol.png').convert('RGBA')); out = a.copy(); H, W = a.shape[:2]; ed = []
    C = lambda *v: np.array([*v, 255], np.uint8)
    RED = (206, 53, 49)
    isink = lambda p: p[3] > 0 and int(p[0]) + int(p[1]) + int(p[2]) < 20
    # 1 reds below the helmet (specks in the bread and the box): the most common neighbour colour
    for y in range(20, H):
        for x in range(W):
            if a[y, x, 3] and tuple(a[y, x, :3]) == RED:
                nb = [tuple(a[yy, xx]) for yy, xx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1), (y-1, x-1), (y+1, x+1), (y-1, x+1), (y+1, x-1))
                      if 0 <= yy < H and 0 <= xx < W and a[yy, xx, 3] and tuple(a[yy, xx, :3]) != RED]
                if nb: out[y, x] = max(set(nb), key=nb.count)
    ed += _edits(a, out, 'red speck off the helmet'); b = out.copy()
    # 2 lone pixels in the loaves (x 16-66, y 34-59): a colour none of its 4 neighbours has, not ink
    for _ in range(2):
        c = out.copy()
        for y in range(34, 59):
            for x in range(16, 67):
                p = c[y, x]
                if not p[3] or isink(p): continue
                nb = [tuple(c[yy, xx]) for yy, xx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)) if c[yy, xx, 3]]
                if nb and tuple(p) not in nb:
                    col = [n for n in nb if int(n[0]) + int(n[1]) + int(n[2]) >= 20]
                    if col: out[y, x] = max(set(col), key=col.count)
    ed += _edits(b, out, 'lone pixel in the loaves takes its neighbours colour'); b = out.copy()
    # 3 the box face, rows 60-76: three planks of one pattern
    HI, FILL, SH, DK, END = C(244, 204, 105), C(178, 124, 60), C(150, 94, 42), C(112, 64, 28), C(122, 59, 42)
    PL, PM, PD, PH = C(91, 91, 91), C(55, 55, 55), C(28, 28, 28), C(132, 146, 156)
    planks = [(60, 6, (28, 44, 55)), (66, 6, (24, 37, 50)), (72, 5, (31, 44, 52))]
    xr = 63
    for y0, n, grain in planks:
        for k in range(n):
            y = y0 + k
            x0 = x = 40
            while x0 > 0 and not (out[y, x0 - 1, 3] == 0 or isink(out[y, x0 - 1])): x0 -= 1
            row = HI if k == 0 else (SH if k == n - 1 else FILL)
            for x in range(x0, xr + 1): out[y, x] = row
            if k == 2:
                for g in grain:
                    for x in range(g, g + 4): out[y, x] = SH
            out[y, xr] = DK if k else SH                          # the right end in shadow
            out[y, max(x0, 22)] = SH if k else HI                  # the left end post
    for cx, cy in ((23, 60), (60, 60), (23, 74), (60, 74)):        # corner plates, 3 x 3, lit from the upper left
        for dy in range(3):
            for dx in range(3):
                out[cy + dy, cx + dx] = PH if (dx, dy) == (0, 0) else (PD if (dx == 2 or dy == 2) else PL)
    ed += _edits(b, out, 'box face drawn again: three planks of one pattern, corner plates'); b = out.copy()
    # 4 asset_qa blotch on the trousers (74-75, 56): the colour around it
    for x, y in ((74, 56), (75, 56)):
        nb = [tuple(b[yy, xx]) for yy, xx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)) if b[yy, xx, 3] and (yy, xx) not in ((56, 74), (56, 75))]
        out[y, x] = max(set(nb), key=nb.count)
    ed += _edits(b, out, 'blotch on the trousers takes the colour around it'); b = out.copy()
    # 5 lone pixels (no same colour in the 8 around) in the jacket, face and helmet fills (x 64-100, y 0-50), not ink:
    # they take the most common colour around them (asset_qa stray 3.7 %, the River Walk riders pass under 3 %)
    for y in range(1, 50):
        for x in range(64, 101):
            p = b[y, x]
            if not p[3] or isink(p): continue
            nb8 = [tuple(b[yy, xx]) for yy in (y - 1, y, y + 1) for xx in (x - 1, x, x + 1) if (yy, xx) != (y, x) and b[yy, xx, 3]]
            if tuple(p) in nb8 or len(nb8) < 8: continue
            col = [n for n in nb8 if int(n[0]) + int(n[1]) + int(n[2]) >= 20]
            if col: out[y, x] = max(set(col), key=col.count)
    ed += _edits(b, out, 'lone pixel in the rider takes the most common colour around it')
    Image.fromarray(out).save(f'{S}/{N}_pol.png')
    json.dump(ed, open(f'{S}/edits_polish.json', 'w'))
    print('polish', len(ed), 'px')


if __name__ == '__main__' and sys.argv[1] == 'cargo_polish':
    cargo_polish()


# ===================================================================================================================
# the vintage tram, BUILT (6 Nov): the NB 2.1 2K render (art/gen/renders/dt_tram_n6a.png) came back on a 256 grid, half
# true scale, so it is the design and colour reference only (as the 5 Nov ferry's flat parts): every part is drawn
# once by rule at 46 px/m and stamped. 12.35 m body = 568 px (8 identical passenger windows on a 52 px pitch, two
# folding doors, the cab with the driver), 3.3 m to the clerestory = 152 px, wheels 0.68 m = 31 px on two bogies
# (wheelbase 1.6 m = 74 px), the trolley pole trailing up to the right. Back layer: no outline, edges a darker shade.
# The wheels are their own sheet (tram_vintage_wheel.png, 4 frames turned 11.25 degrees each: 8 spokes, so the loop
# closes), drawn behind the body where the image is clear; the body never moves.
TC = dict(
    blue_l=(98, 140, 178), blue=(68, 104, 136), blue_d=(46, 74, 102),
    cream_l=(252, 243, 216), cream=(241, 227, 193), cream_d=(206, 188, 150),
    roof_l=(116, 116, 128), roof=(82, 82, 94), roof_d=(56, 56, 64), under=(74, 74, 86), wheel_d=(36, 36, 42),
    glass=(54, 62, 80), glass_r=(98, 110, 134), steel=(140, 142, 152), lamp=(255, 226, 140),
    skin=(238, 190, 152), skin_d=(196, 144, 110), navy=(40, 50, 92), gold=(228, 186, 70))
X0, LB = 2, 568                       # the body's left edge (2 px room for the headlamp) and length
TW, TH = X0 + LB, 188                 # image size; the bottom row is the rail line - 1 (the wheels' lowest row)
WIN = [92 + i * 52 for i in range(8)]                  # passenger windows (left x, from the body's left)
BOGIES = (125, LB - 125)
WHEELS = [X0 + b + d for b in BOGIES for d in (-37, 37)]   # wheel centres x in the image; centre row TH - 16
DOOR_F, DOOR_R = (42, 74), (LB - 55, LB - 23)
DRIVER = [".....NNNNNNNNN......",
          "....NNNNNNNNNNN.....",
          "....NNNNNNGNNNNN....",
          "....NNNNNNNNNNNN....",
          ".UUUUUUUUUUUUUU.....",
          "....SSSSSSSSHHHH....",
          "...SSSSSSSSSSHHH....",
          "...SUSSSSSSSSSHH....",
          "..SSSSSSSSSSSSHH....",
          ".SSSSSSSSSSSSsHH....",
          "..SSSSSSSSSSsHH.....",
          "...SsssSSSSSsH......",
          "....SSSSSSSs........",
          ".....sSSSSs.........",
          "......sSSs..........",
          "...NNNCCNNNNNNN.....",
          "..NNNNNCNNNNNNNNN...",
          ".NNNNNNNNNNNNNNNNN..",
          "NNNNNGNNNNNNNNNNNNN.",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNGNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN",
          "NNNNNNNNNNNNNNNNNNNN"]


def tram():
    im = np.zeros((TH, TW, 4), np.uint8)

    def k2y(k): return TH - k                                   # k: height above the rail (the blockout's G - k)

    def put(x, k, c):
        y = k2y(k)
        if 0 <= x < TW and 0 <= y < TH: im[y, x] = (*TC[c], 255) if isinstance(c, str) else (*c, 255)

    def box(x0, x1, ktop, kbot, c):                            # inclusive, body x (from X0), k from top to bottom
        for k in range(kbot, ktop + 1):
            for x in range(x0, x1 + 1): put(X0 + x, k, c)

    # roof: clerestory 152-147 (vents over the pillars), the curved roof 147-137 with rounded ends
    box(18, LB - 19, 152, 147, 'roof'); box(18, LB - 19, 152, 152, 'roof_l'); box(18, LB - 19, 147, 147, 'roof_d')
    for wx in WIN + [WIN[-1] + 52]:
        box(wx - 8, wx - 5, 150, 149, 'roof_d')
    for k in range(137, 147):
        inset = {146: 4, 145: 2, 144: 1}.get(k, 0)
        box(inset, LB - 1 - inset, k, k, 'roof_l' if k >= 145 else ('roof_d' if k <= 138 else 'roof'))
    # body: cream band 136-80, blue 79-39, skirt 38-31
    box(0, LB - 1, 136, 80, 'cream')
    box(0, LB - 1, 136, 127, 'blue'); box(0, LB - 1, 136, 136, 'blue_d'); box(0, LB - 1, 127, 127, 'blue_d')   # the blue letter board
    box(0, LB - 1, 79, 39, 'blue'); box(0, LB - 1, 79, 79, 'blue_d'); box(0, LB - 1, 78, 78, 'blue_l')
    box(0, LB - 1, 61, 61, 'blue_l'); box(0, LB - 1, 60, 60, 'blue_d')         # the beading
    box(0, LB - 1, 39, 39, 'blue_d')
    box(0, LB - 1, 83, 83, 'cream_l')                                            # the sill moulding, lit
    box(0, 0, 126, 80, 'cream_l'); box(0, 0, 135, 128, 'blue_l'); box(0, 0, 79, 40, 'blue_l')                   # the lit front edge
    box(LB - 1, LB - 1, 126, 80, 'cream_d'); box(LB - 1, LB - 1, 135, 128, 'blue_d'); box(LB - 1, LB - 1, 79, 40, 'blue_d')   # the back edge in shade
    box(0, LB - 1, 38, 31, 'under'); box(0, LB - 1, 38, 38, 'roof_d')

    def window(x0, w, glass_top=122, glass_bot=84, toplight=True):
        box(x0, x0 + w - 1, glass_top, glass_bot, 'glass')
        box(x0, x0 + w - 1, glass_top, glass_top, 'cream_d'); box(x0, x0, glass_top, glass_bot, 'cream_d')   # recess shade
        if toplight:
            box(x0 + 1, x0 + w - 1, glass_top - 10, glass_top - 11, 'cream')                                 # the toplight bar
        # reflections: two strokes from the lower left up to the right, the same in every window
        for x in range(x0 + 1, x0 + w):
            for k in range(glass_bot, glass_top):
                if toplight and glass_top - 11 <= k <= glass_top - 10: continue
                d = (x - x0) - (k - glass_bot) * 0.75
                if 6 <= d < 9 or 14 <= d < 15: put(X0 + x, k, 'glass_r')

    for wx in WIN: window(wx, 40)
    window(4, 33, toplight=False)                                                 # the cab window
    window(LB - 17, 13, toplight=False)                                           # the rear end window
    # the driver in the cab, facing left (cap, face, shoulders); the window sill hides the rest
    pal = {'N': 'navy', 'G': 'gold', 'U': 'under', 'S': 'skin', 's': 'skin_d', 'H': 'roof_d', 'C': 'cream_l'}
    for r, row in enumerate(DRIVER):
        for c_, ch in enumerate(row):
            if ch in pal and 116 - r > 84: put(X0 + 10 + c_, 116 - r, pal[ch])
    # two folding doors: two leaves, glass over a blue panel, a step under
    for d0, d1 in (DOOR_F, DOOR_R):
        box(d0, d1, 124, 36, 'blue_d')
        mid = (d0 + d1) // 2
        for l0, l1 in ((d0 + 1, mid - 1), (mid + 1, d1 - 1)):
            box(l0, l1, 123, 37, 'blue')
            box(l0 + 2, l1 - 2, 120, 72, 'glass'); box(l0 + 2, l1 - 2, 120, 120, 'roof_d')
            for x in range(l0 + 2, l1 - 1):
                for k in range(72, 121):
                    d = (x - l0 - 2) - (k - 72) * 0.25
                    if 3 <= d < 5: put(X0 + x, k, 'glass_r')
            box(l0 + 2, l1 - 2, 66, 44, 'blue_d'); box(l0 + 3, l1 - 2, 65, 44, 'blue')   # the lower panel, inset
            box(l0, l0, 123, 37, 'blue_l')
        box(mid - 2, mid - 2, 98, 90, 'steel'); box(mid + 2, mid + 2, 98, 90, 'steel')      # grab handles
        box(d0 - 1, d1 + 1, 35, 33, 'steel'); box(d0 - 1, d1 + 1, 33, 33, 'roof_d')        # the step
    # headlamp on the front end, a lit lens in a dark rim; a small red lamp on the back
    for k in range(51, 59):
        for x in (-2, -1, 0, 1, 2):
            put(X0 + x, k, 'under' if (k in (51, 58) or x == -2) else ('lamp' if x >= 0 else 'roof_d'))
    box(LB - 2, LB - 1, 56, 52, (196, 52, 46))
    # under the body: the bogies (side frame, axle boxes, bolster), the equipment box, the lifeguard tray
    for b in BOGIES:
        box(b - 50, b + 50, 22, 17, 'under'); box(b - 50, b + 50, 22, 22, 'roof')
        box(b - 9, b + 9, 30, 22, 'under'); box(b - 7, b + 7, 28, 26, 'roof_d'); box(b - 7, b + 7, 24, 24, 'roof_d')
        for wc in (b - 37, b + 37):
            box(wc - 5, wc + 5, 23, 12, 'roof'); box(wc - 5, wc + 5, 23, 23, 'roof_l')
            box(wc - 5, wc - 5, 22, 12, 'roof_l'); box(wc + 5, wc + 5, 22, 12, 'roof_d')
            box(wc - 1, wc + 1, 17, 15, 'steel')
    box(200, LB - 201, 30, 24, 'under'); box(200, LB - 201, 30, 30, 'roof')
    for x in range(208, LB - 205, 16): box(x, x + 9, 28, 26, 'roof_d')
    box(0, 22, 30, 24, 'under'); box(0, 22, 30, 30, 'roof')                      # the front apron
    # the trolley pole: a base on the clerestory, the pole trailing up to the right, the shoe at its tip
    box(376, 389, 156, 153, 'under'); box(376, 389, 156, 156, 'roof')
    x0p, k0p, x1p, k1p = 384, 156, 444, 185
    n = x1p - x0p
    for i in range(n + 1):
        x = x0p + i; k = round(k0p + (k1p - k0p) * i / n)
        put(X0 + x, k, 'roof'); put(X0 + x, k - 1, 'under')
    box(x1p - 1, x1p + 4, 187, 185, 'under'); box(x1p, x1p + 3, 187, 187, 'steel')
    os.makedirs('art/source/dt_tram', exist_ok=True)
    Image.fromarray(im).save('art/source/dt_tram/tram_vintage.png')
    # the wheel sheet: 4 frames of 31 x 31, spokes turned 11.25 degrees a frame (anticlockwise on screen: it rolls left)
    R = 15; fr = []
    for f in range(4):
        w = np.zeros((31, 31, 4), np.uint8)
        for y in range(31):
            for x in range(31):
                d = np.hypot(x - R, y - R); k = int(round(d))
                c = None
                if k == R: c = 'under'
                elif k == R - 1: c = 'roof_d'
                elif k == R - 2: c = 'steel'
                elif k <= R - 3: c = 'wheel_d'
                if k <= 2: c = 'steel' if k <= 1 else 'roof_d'
                if c: w[y, x] = (*TC[c], 255)
        for s in range(8):
            t = np.radians(-11.25 * f + s * 45)
            for q in np.arange(3.0, R - 2.5, 0.25):
                x, y = int(round(R + q * np.cos(t))), int(round(R + q * np.sin(t)))
                w[y, x] = (*TC['roof'], 255)
        fr.append(w)
    Image.fromarray(np.concatenate(fr, 1)).save('art/source/dt_tram/tram_vintage_wheel.png')
    meta = dict(size=[TW, TH], body_x=X0, body_len=LB, door_front_centre=X0 + (DOOR_F[0] + DOOR_F[1]) // 2,
                wheels_x=WHEELS, wheel_r=R, wheel_centre_row=TH - 16, windows=[X0 + w for w in WIN], window_w=40)
    json.dump(meta, open('art/source/dt_tram/tram_vintage.json', 'w'), indent=1)
    print('tram', TW, 'x', TH, meta)


if __name__ == '__main__' and sys.argv[1] == 'tram':
    tram()


def cargo_pedal():
    """The pedal loop (as the River Walk riders', build_traffic.pedal): outside the leg zone (x 64-98, y 46-88, not
    the wheels) every frame is the polished still, pixel-identical; in it the pixel-engine frame's pixels snapped to
    the still's colours; both wheels redrawn by rule each frame, turned 22.5 degrees a frame. Then the outline is
    closed per frame and asset_qa's pinholes filled (edits_pedal.json)."""
    import subprocess, tempfile
    fr = bt.pedal(N, zone=(64, 46, 98, 88), off=(8, 44))
    H, W = fr[0].shape[:2]
    raw = f'{S}/{N}_pedal_raw.png'; ol = f'{S}/{N}_pedal_ol.png'
    subprocess.run(['python3', '-I', 'tools/outline_complete.py', raw, ol, '--skip-bottom', '--frames', f'{W}x{H}'])
    tj = tempfile.mktemp(suffix='.json')
    subprocess.run(['python3', '-I', 'tools/asset_qa.py', '--file', ol, '--layer', 'char', '--level', 'dt', '--frames', f'{W}x{H}', '--json', tj], capture_output=True)
    d = json.load(open(tj))[0]; a = np.array(Image.open(ol).convert('RGBA')); out = a.copy(); ed = []
    for c in d['checks']:
        if c['id'] != 'pinholes': continue
        for x, y in c['pixels']:
            nb = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if a[yy, xx, 3] > 0]
            if nb: out[y, x] = max(set(nb), key=nb.count)
    # the trousers in the leg zone: a 3 x 3 majority among the trouser colours (the pixel-engine frames mottle them)
    T = {(91, 91, 91), (64, 74, 86), (55, 55, 55), (28, 28, 28)}
    for _ in range(2):
        b = out.copy()
        for f in range(out.shape[1] // W):
            for y in range(46, 88):
                for x in range(f * W + 64, f * W + 98):
                    if not b[y, x, 3] or tuple(b[y, x, :3]) not in T: continue
                    nb = [tuple(b[yy, xx, :3]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                          if 0 <= yy < H and b[yy, xx, 3] and tuple(b[yy, xx, :3]) in T]
                    m = max(set(nb), key=nb.count)
                    if nb.count(m) > nb.count(tuple(b[y, x, :3])): out[y, x, :3] = m
    r = np.array(Image.open(raw).convert('RGBA'))
    ed = _edits(r, out, 'outline closed, pinhole filled, or trouser speck to the majority around it')
    Image.fromarray(out).save(f'{S}/{N}_pedal.png'); json.dump(ed, open(f'{S}/edits_pedal.json', 'w'))
    print('pedal', out.shape, len(ed), 'px')


if __name__ == '__main__' and sys.argv[1] == 'cargo_pedal':
    cargo_pedal()
