#!/usr/bin/env python3
"""build_cars_n07.py: the River Walk road cars BUILT by rule (track chars, 7 Nov 2026).

  python3 -I tools/build_cars_n07.py           build riverwalk/art/scene/road_car1-4.png (+ .aseprite sources)
  python3 -I tools/build_cars_n07.py --check   fail if a file on disk differs from what this script builds

Owner, board 7 Nov: road_car1 and road_car4 "redraw"; road_car2 and road_car3 "needs clean up in details" (redraw).
The 5 Nov cars were SpriteCook pictures snapped to the palette: mottled paint, ragged trim, lumpy wheels, speckled
glass. A car is geometry, so each one is now built from parts at the road lane's scale (55 px a metre, road.lua):
  BODY   one side profile polygon per car (bumper, bonnet, windscreen, roof, tail), the wheel arches cut out as
         circles 3 px wider than the tyre; paint in a 5-step ramp by rule: the top-facing row lit (bonnet, roof),
         the shoulder under the window line light, the door field mid, the lower door below the crease shade, the
         two sill rows dark; a 1 px darker lip round each arch over the dark wheel well.
  GLASS  the greenhouse polygon in a 3-step blue-grey glass ramp (top rows darker under the roof, one clean
         45-degree glint per pane), framed by 1 px black rubber; pillars as quads (black trim B and C pillars,
         body-coloured D pillar).
  PARTS  drawn once, stamped: the wheel (tyre with a lit arc, rim with 5 even spokes, hub cap; one wheel per car
         size, identical front and back), the door handle, the mirror, head and tail lamps, the plastic bumpers,
         door seams (1 px, the paint's dark), the rub crease (dark over light).
  INK    one 1 px ink outline round the whole silhouette (the cars are traffic: drawn as obstacles), the
         bench's ink.
Cars face LEFT (road.lua mirrors them for the near lane). Light from the upper left. The game shows the top 48 rows
(road.lua CAR_TOP 192): roof, glass, the shoulder; the rest is built as carefully for the board."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

OUT = 'riverwalk/art/scene'
SRC = 'art/source/cars_n07'
hexc = lambda h: (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))
INK = hexc('#17181f')
TRIM = hexc('#23242c')                        # black rubber, B/C pillars, the tyre
# (asset_qa colours: the play layer allows 20; near-blacks and greys are shared between the parts)
GLASS = [hexc('#3a4558'), hexc('#6a7d96'), hexc('#93a6bd')]   # dark (under the roof, the driver), mid, light
GLINT = hexc('#d4e0ec')
HUB = GLINT
TYRE, TYRE_L = TRIM, hexc('#43454e')
WELL = INK
RIM_D, RIM, RIM_L = hexc('#4a4e58'), hexc('#a4aab4'), hexc('#d3d8de')
PLAST, PLAST_L = TYRE_L, RIM_D
CHROME, CHROME_D = RIM_L, RIM
LAMP, LAMP_D = hexc('#f6eccb'), hexc('#c9b98c')
TAIL, TAIL_D = hexc('#c4303a'), hexc('#7d1c24')
TAIL_L = TAIL
AMBER = hexc('#e9a23b')
PAINTS = {   # hi, light, mid, shade, dark
    'blue':   [hexc('#6d86ad'), hexc('#3f5a86'), hexc('#2c4268'), hexc('#223352'), hexc('#19253c')],
    'white':  [hexc('#ffffff'), hexc('#f2f0ea'), hexc('#dedcd5'), hexc('#bdbcb7'), hexc('#97979a')],
    'yellow': [hexc('#fff0a0'), hexc('#f8d462'), hexc('#ecb944'), hexc('#c98f2c'), hexc('#97661f')],
    'red':    [hexc('#f2856f'), hexc('#d84a3e'), hexc('#b8332f'), hexc('#8f2428'), hexc('#661a1f')],
}


def poly_mask(W, H, pts):
    im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
    return np.array(im) > 0


def disc(W, H, cx, cy, r):
    yy, xx = np.mgrid[0:H, 0:W]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r


def wheel(R):
    """one wheel, (2R+1) square, centre (R, R): tyre ring 5-6 px with a lit arc top-left, rim lip, 5 even spokes on
    the dark rim well, a hub cap; built once per size and stamped at both axles"""
    D = 2 * R + 1; a = np.zeros((D, D, 3), np.uint8); m = np.zeros((D, D), bool)
    yy, xx = np.mgrid[0:D, 0:D]; dx, dy = xx - R, yy - R; r = np.hypot(dx, dy); ang = np.arctan2(dy, dx)
    rim_r = R * 0.68
    m = r <= R + 0.3
    a[m] = TYRE
    lit = m & (r > rim_r + 2.2) & (r <= R - 1.2) & (ang > -2.6) & (ang < -1.0)
    a[lit] = TYRE_L
    side = m & (r > rim_r + 0.4) & (r <= rim_r + 1.4)        # the tyre's sidewall bead round the rim
    a[side] = TYRE_L
    well = r <= rim_r + 0.4
    a[well] = RIM_D
    lip = well & (r > rim_r - 1.0)
    a[lip] = RIM
    a[lip & (ang > -2.9) & (ang < -0.6)] = RIM_L
    for k in range(5):                                   # spokes: 5 even, each a 3 px wide band from hub to lip
        th = -math.pi / 2 + k * 2 * math.pi / 5
        ux, uy = math.cos(th), math.sin(th)
        along = dx * ux + dy * uy; across = np.abs(-dx * uy + dy * ux)
        sp = well & (along > 0) & (r < rim_r - 0.6) & (across <= 1.7 - 0.5 * along / rim_r)   # tapering to the lip
        a[sp] = RIM
        a[sp & (across <= 0.9 - 0.4 * along / rim_r)] = RIM_L
    hub = r <= max(2.0, R * 0.17)
    a[hub] = RIM_D; a[r <= 1.0] = HUB
    return a, m


class Car:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.a = np.zeros((H, W, 3), np.uint8); self.m = np.zeros((H, W), bool)

    def put(self, mask, col):
        self.a[mask] = col; self.m |= mask


def build(spec):
    W, H = spec['W'], spec['H']; G = H - 1; R = spec['R']; P = PAINTS[spec['paint']]
    c = Car(W, H)
    body = poly_mask(W, H, spec['body'])
    for cx in spec['wheels']:
        body &= ~disc(W, H, cx, G - R, R + 3.4)
    glass = poly_mask(W, H, spec['glass']) & body
    # paint by rule
    paint = body & ~glass
    rows = np.arange(H)[:, None] * np.ones((1, W), int)
    c.put(paint, P[2])
    belt = spec['belt']; crease = spec['crease']; sill = spec['sill']
    c.a[paint & (rows > crease)] = P[3]
    c.a[paint & (rows >= sill - 1)] = P[4]
    c.a[paint & (rows > belt) & (rows <= belt + 3)] = P[1]
    c.a[paint & (rows == belt + 2)] = P[0]                     # the shoulder's reflection line, under the window trim
    band = paint & (rows >= crease - 5) & (rows <= crease - 3)  # the sky's reflection along the doors, over the crease
    c.a[band] = P[1]
    up = np.zeros_like(paint); up[1:] = paint[1:] & ~(paint[:-1] | glass[:-1]); up[0] = paint[0]
    c.a[up] = P[0]
    up2 = np.zeros_like(paint); up2[1:] = paint[1:] & up[:-1] & ~up[1:]
    c.a[up2 & (rows < belt)] = P[1]
    # crease: a dark line over a light line
    x0, x1 = spec['crease_x']
    cr = np.zeros_like(paint); cr[crease, x0:x1] = True; cr &= paint
    c.a[cr] = P[4]; cr2 = np.zeros_like(paint); cr2[crease + 1, x0:x1] = True; cr2 &= paint; c.a[cr2] = P[1]
    # arch lips: 1 px of the paint's dark round each arch
    for cx in spec['wheels']:
        ring = disc(W, H, cx, G - R, R + 4.4) & ~disc(W, H, cx, G - R, R + 3.4) & paint
        c.a[ring] = P[4]
        flare = disc(W, H, cx, G - R, R + 5.4) & ~disc(W, H, cx, G - R, R + 4.4) & paint & (rows < G - R - R * 0.55)
        c.a[flare] = P[1]                                     # the wheel arch's flare catches the light on top
        well = disc(W, H, cx, G - R, R + 3.4) & ~disc(W, H, cx, G - R, R + 0.3)
        wellm = well & (rows < G - R + 2)
        c.put(wellm, WELL)
    # plastic bumpers and parts (polygons in plastic)
    for pts in spec.get('plastic', []):
        pm = poly_mask(W, H, pts); c.put(pm, PLAST)
        t = np.zeros_like(pm); t[1:] = pm[1:] & ~pm[:-1]; c.a[t] = PLAST_L
    # glass
    c.put(glass, GLASS[1])
    gtop = glass & (rows < spec['glass_dark_to'])
    c.a[gtop] = GLASS[0]
    for hx, hy in spec.get('drivers', []):                    # a head and shoulders behind the glass, a shade darker
        dm = (disc(W, H, hx, hy, 4.6) | poly_mask(W, H, [(hx - 8, spec['belt']), (hx - 6, hy + 6), (hx + 6, hy + 6), (hx + 9, spec['belt'])])) & glass
        c.a[dm & (rows >= spec['glass_dark_to'])] = GLASS[0]
    for gx, gy, gl in spec.get('glints', []):                 # one clean 45-degree glint per pane, 2 px wide
        for i in range(gl):
            for j, col in ((0, GLASS[2]), (1, GLINT), (2, GLINT), (3, GLASS[2])):
                x, y = gx + i + j, gy - i
                if 0 <= x < W and 0 <= y < H and glass[y, x] and not np.array_equal(c.a[y, x], TRIM): c.a[y, x] = col
    # rubber round the glass: 1 px trim on the paint side
    gr = np.zeros_like(glass)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        gr |= np.roll(np.roll(glass, dy, 0), dx, 1)
    gr &= paint
    c.a[gr] = TRIM
    for pts in spec.get('pillars', []):                       # black trim pillars over the glass
        pm = poly_mask(W, H, pts) & (glass | gr); c.a[pm] = TRIM
    for pts, col in spec.get('paint_pillars', []):
        pm = poly_mask(W, H, pts) & (glass | gr); c.a[pm] = P[col]
    # door seams
    for line in spec.get('seams', []):
        im = Image.new('L', (W, H), 0); ImageDraw.Draw(im).line([tuple(p) for p in line], fill=255, width=1)
        sm = (np.array(im) > 0) & paint; c.a[sm] = P[4]
    for hx, hy in spec.get('handles', []):                    # handle: 6 x 2, chrome over its shadow
        c.a[hy, hx:hx + 6] = CHROME; c.a[hy + 1, hx:hx + 6] = P[4]; c.a[hy, hx] = CHROME_D
    for pts, kind in spec.get('lamps', []):
        pm = poly_mask(W, H, pts)
        if kind == 'head':
            c.put(pm, LAMP); e = pm & ~np.roll(pm, -1, 0); c.a[e] = LAMP_D
        elif kind == 'tail':
            c.put(pm, TAIL); t = pm & ~np.roll(pm, 1, 1); c.a[t] = TAIL_L; b = pm & ~np.roll(pm, -1, 0); c.a[b] = TAIL_D
        elif kind == 'amber':
            c.put(pm, AMBER)
        elif kind == 'grille':
            c.put(pm, TRIM)
        elif kind == 'chrome':
            c.put(pm, CHROME); b = pm & ~np.roll(pm, -1, 0); c.a[b] = CHROME_D
        elif kind == 'roofsign':
            c.put(pm, LAMP); t = pm & ~np.roll(pm, 1, 0); c.a[t] = GLINT
            b = pm & ~np.roll(pm, -1, 0); c.a[b] = LAMP_D
    for pts in spec.get('mirror', []):
        pm = poly_mask(W, H, pts); c.put(pm, P[2]); t = pm & ~np.roll(pm, 1, 0); c.a[t] = P[0]
        b = pm & ~np.roll(pm, -1, 0); c.a[b] = P[3]
    for (x0, y0, x1, y1) in spec.get('rails', []):            # roof rails: a bar with two feet
        c.a[y0, x0:x1 + 1] = CHROME; c.a[y0 + 1, x0:x1 + 1] = CHROME_D; c.m[y0:y0 + 2, x0:x1 + 1] = True
        for fx in (x0 + 2, x1 - 4):
            c.a[y0 + 2:y1 + 1, fx:fx + 3] = TRIM; c.m[y0 + 2:y1 + 1, fx:fx + 3] = True
    # wheels, stamped
    wa, wm = wheel(R)
    for cx in spec['wheels']:
        ys, xs = np.nonzero(wm)
        c.a[ys + G - 2 * R, xs + cx - R] = wa[ys, xs]; c.m[ys + G - 2 * R, xs + cx - R] = True
    # ink outline round the silhouette (outside pixels next to the shape), then the shape's own edge pixels that
    # touch transparency become ink where the outline would leave the image
    m = c.m.copy()
    # slivers: shape pieces of under 6 px cut off by the arches (they would get a speck of outline) are dropped
    lab = np.zeros(m.shape, int); n = 0
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]: continue
        n += 1; st = [(y0, x0)]; lab[y0, x0] = n; comp = []
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]: lab[yy, xx] = n; st.append((yy, xx))
        if len(comp) < 6:
            for y, x in comp: m[y, x] = False
    out = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = np.zeros_like(m)
        ys0, ys1 = max(0, dy), H + min(0, dy); xs0, xs1 = max(0, dx), W + min(0, dx)
        sh[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
        out |= sh
    out &= ~m
    rgba = np.zeros((H, W, 4), np.uint8); rgba[m, :3] = c.a[m]; rgba[m, 3] = 255
    rgba[out, :3] = INK; rgba[out, 3] = 255
    # the image border: shape pixels on the border row/column take the ink
    for sl in (np.s_[0, :], np.s_[-1, :], np.s_[:, 0], np.s_[:, -1]):
        e = m[sl]; rgba[sl][e, :3] = INK
    return rgba


# ---- the cars, on the 5 Nov cars' own silhouettes (their proportions were right: roof, bonnet and wheel lines as
# measured on the old files), coordinates before the 1 px pad that leaves room for the ink outline (top, left, right).
# W, H the old slot; R = tyre radius; ground row = H - 1.
CARS = {
 # an estate (a Volvo V70 of the 2000s), dark blue, 4.4 m at 55 px/m
 'road_car1': dict(W=241, H=88, R=19, paint='blue', wheels=[48, 197], belt=38, crease=56, crease_x=(70, 228), sill=76,
    body=[(3, 76), (0, 72), (0, 56), (3, 47), (8, 42), (20, 38), (40, 33), (60, 30), (68, 27), (71, 26), (88, 15),
          (100, 8), (108, 5), (116, 4), (214, 4), (220, 6), (226, 9), (231, 20), (235, 32), (238, 42), (240, 52),
          (240, 72), (237, 75), (218, 75), (215, 76)],
    glass=[(73, 37), (73, 27), (89, 17), (101, 10), (110, 7), (214, 8), (220, 10), (227, 24), (231, 37)],
    glass_dark_to=12,
    pillars=[[(81, 37), (99, 15), (103, 15), (86, 37)], [(134, 8), (138, 8), (138, 37), (134, 37)],
             [(180, 8), (184, 8), (184, 37), (180, 37)]],
    paint_pillars=[([(213, 8), (220, 8), (229, 37), (221, 37)], 2)],
    glints=[(108, 32, 12), (148, 32, 14), (194, 32, 13)],
    seams=[[(73, 39), (73, 74)], [(136, 39), (136, 74)], [(182, 39), (182, 62), (179, 68)]],
    handles=[(124, 43), (170, 43)],
    lamps=[([(2, 48), (14, 46), (17, 50), (15, 53), (3, 54)], 'head'), ([(1, 56), (6, 56), (6, 58), (1, 58)], 'amber'),
           ([(230, 20), (233, 23), (238, 44), (234, 44), (229, 26)], 'tail'), ([(1, 59), (14, 59), (14, 61), (1, 61)], 'grille')],
    plastic=[[(0, 70), (25, 70), (26, 76), (3, 76), (0, 72)], [(216, 69), (240, 69), (240, 72), (237, 75), (216, 75)]],
    drivers=[(112, 22)],
    mirror=[[(78, 36), (86, 33), (89, 34), (88, 40), (79, 40)]],
    rails=[(118, 0, 210, 3)]),
 # a panel van (a Ford Transit), white, 4.4 m long, 1.85 m tall
 'road_car2': dict(W=242, H=102, R=19, paint='white', wheels=[42, 186], belt=48, crease=66, crease_x=(60, 238), sill=89,
    body=[(3, 89), (0, 84), (0, 60), (2, 54), (6, 50), (18, 46), (30, 43), (36, 38), (52, 16), (62, 5), (68, 2),
          (76, 0), (236, 0), (240, 3), (241, 6), (241, 84), (238, 89)],
    glass=[(38, 47), (38, 39), (53, 17), (62, 7), (68, 4), (100, 4), (100, 47)],
    glass_dark_to=15,
    pillars=[[(46, 47), (60, 24), (64, 24), (51, 47)]],
    glints=[(70, 41, 16)],
    seams=[[(102, 2), (102, 88)], [(152, 26), (152, 88)], [(236, 4), (236, 80)], [(102, 24), (238, 24)]],
    handles=[(90, 53), (142, 53)],
    lamps=[([(1, 54), (14, 52), (18, 56), (15, 59), (2, 60)], 'head'), ([(1, 61), (6, 61), (6, 63), (1, 63)], 'amber'),
           ([(238, 40), (241, 40), (241, 66), (238, 66)], 'tail'), ([(1, 64), (16, 64), (16, 67), (1, 67)], 'grille')],
    plastic=[[(0, 82), (26, 82), (28, 89), (3, 89), (0, 84)], [(220, 82), (241, 82), (241, 84), (238, 89), (220, 89)],
             [(102, 74), (162, 74), (162, 77), (102, 77)]],
    drivers=[(78, 22)],
    mirror=[[(34, 40), (42, 36), (45, 37), (44, 47), (35, 47)]]),
 # a saloon taxi (a Volvo S80), yellow, a roof sign, 4.5 m
 'road_car3': dict(W=246, H=93, R=18, paint='yellow', wheels=[44, 192], belt=42, crease=58, crease_x=(70, 232), sill=81,
    body=[(3, 81), (0, 76), (0, 58), (3, 52), (8, 48), (24, 44), (44, 41), (62, 38), (68, 35), (88, 20), (98, 15),
          (106, 13), (162, 13), (170, 15), (186, 24), (200, 34), (206, 37), (220, 38), (236, 40), (243, 44), (245, 52),
          (245, 76), (242, 80), (224, 80), (221, 81)],
    glass=[(70, 41), (70, 36), (89, 22), (99, 17), (107, 15), (162, 16), (168, 18), (182, 28), (194, 41)],
    glass_dark_to=20,
    pillars=[[(80, 41), (96, 24), (100, 24), (85, 41)], [(130, 16), (134, 16), (134, 41), (130, 41)]],
    paint_pillars=[([(160, 16), (167, 17), (188, 41), (177, 41)], 2)],
    glints=[(106, 36, 11), (146, 36, 12)],
    seams=[[(76, 43), (76, 79)], [(132, 43), (132, 79)], [(176, 43), (176, 63), (172, 70)], [(196, 40), (236, 42)]],
    handles=[(120, 47), (164, 47)],
    lamps=[([(2, 52), (14, 49), (18, 52), (16, 55), (3, 56)], 'head'), ([(1, 58), (6, 58), (6, 60), (1, 60)], 'amber'),
           ([(238, 44), (244, 47), (244, 56), (238, 56)], 'tail'), ([(1, 61), (16, 61), (16, 63), (1, 63)], 'grille'),
           ([(112, 4), (134, 4), (137, 12), (109, 12)], 'roofsign')],
    plastic=[[(0, 75), (24, 75), (26, 81), (3, 81), (0, 76)], [(220, 74), (245, 74), (245, 76), (242, 80), (220, 80)]],
    drivers=[(116, 28)],
    mirror=[[(78, 40), (86, 37), (89, 38), (88, 44), (79, 44)]]),
 # a small hatchback (a Toyota Yaris of the 2000s), red, 3.4 m
 'road_car4': dict(W=185, H=77, R=15, paint='red', wheels=[30, 157], belt=30, crease=46, crease_x=(50, 178), sill=64,
    body=[(3, 64), (0, 60), (0, 46), (3, 38), (8, 33), (24, 29), (40, 25), (50, 21), (66, 10), (78, 4), (88, 1),
          (146, 1), (156, 2), (164, 5), (170, 12), (176, 20), (181, 28), (183, 36), (184, 60), (181, 64)],
    glass=[(52, 29), (52, 22), (67, 11), (79, 5), (89, 3), (146, 4), (156, 6), (166, 14), (174, 29)],
    glass_dark_to=7,
    pillars=[[(61, 29), (76, 12), (80, 12), (66, 29)], [(112, 4), (116, 4), (116, 29), (112, 29)]],
    paint_pillars=[([(148, 4), (157, 6), (174, 29), (163, 29)], 2)],
    glints=[(84, 25, 10), (126, 25, 11)],
    seams=[[(52, 31), (52, 63)], [(114, 31), (114, 50), (111, 56)], [(166, 8), (178, 30)]],
    handles=[(102, 35)],
    lamps=[([(2, 40), (13, 37), (17, 40), (15, 44), (3, 45)], 'head'), ([(1, 47), (5, 47), (5, 49), (1, 49)], 'amber'),
           ([(176, 22), (181, 28), (183, 40), (178, 40)], 'tail'), ([(1, 50), (12, 50), (12, 52), (1, 52)], 'grille')],
    plastic=[[(0, 59), (15, 59), (16, 64), (3, 64), (0, 60)], [(164, 58), (184, 58), (184, 60), (181, 64), (164, 64)]],
    drivers=[(96, 16)],
    mirror=[[(58, 28), (65, 25), (68, 26), (67, 32), (59, 32)]]),
}


def padded(spec, p=1):
    """the 1 px pad (top, left, right) for the ink outline: every coordinate + p, W + 2p, H + p"""
    s = dict(spec); s['W'] = spec['W'] + 2 * p; s['H'] = spec['H'] + p
    sh = lambda pts: [(x + p, y + p) for x, y in pts]
    for k in ('body', 'glass'): s[k] = sh(spec[k])
    for k in ('pillars', 'plastic', 'mirror', 'seams'): s[k] = [sh(q) for q in spec.get(k, [])]
    s['paint_pillars'] = [(sh(q), c) for q, c in spec.get('paint_pillars', [])]
    s['lamps'] = [(sh(q), k) for q, k in spec.get('lamps', [])]
    s['wheels'] = [x + p for x in spec['wheels']]
    for k in ('belt', 'crease', 'sill', 'glass_dark_to'): s[k] = spec[k] + p
    s['crease_x'] = tuple(x + p for x in spec['crease_x'])
    s['glints'] = [(x + p, y + p, l) for x, y, l in spec.get('glints', [])]
    s['handles'] = [(x + p, y + p) for x, y in spec.get('handles', [])]
    s['rails'] = [(a + p, b + p, c + p, d + p) for a, b, c, d in spec.get('rails', [])]
    return s


def main():
    check = '--check' in sys.argv; bad = 0
    names = [a for a in sys.argv[1:] if not a.startswith('--')] or list(CARS)
    os.makedirs(SRC, exist_ok=True)
    for n in names:
        a = build(padded(CARS[n])); p = f'{OUT}/{n}.png'
        cols = len(np.unique(a[a[..., 3] > 0][:, :3], axis=0))
        if check:
            same = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), a)
            print(n, 'OK' if same else 'DIFFERS'); bad += not same
        else:
            Image.fromarray(a).save(p); aseprite_io.write(f'{SRC}/{n}.aseprite', [a])
            print(p, a.shape[1], 'x', a.shape[0], cols, 'colours')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
