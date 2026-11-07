"""The riders of the 7 Nov bikes (track chars): only the LIVING parts are drawn by SpriteCook; the bikes (wheels,
frames, baskets, the cargo box) are built by rule (tools/build_bikes_n07.py) and the legs keyed by rule per pedal
frame, as the 6 Nov rower's arm. Three riders at 46 px/m on one 256 frame (GPT 2.5 Sunburst 1K: a 4 px grid):
  A  the promenade rider 1 (cyclist_adult1): a woman in a red coat, facing RIGHT
  B  the promenade rider 2 (cyclist_adult2): a man in a green jacket with a backpack, facing RIGHT
  C  the Downtown cargo bike's baker (cargo_bike): white jacket, red helmet, facing LEFT
Bike geometry (rider coords of an 88 x 87 bike image, ground row 86; tools/build_bikes_n07.py uses the same):
wheels 31 px (0.68 m), hubs 51 px apart, saddle top 43 px over the ground (0.93 m), bars 46 px, bottom bracket
(40, 74), crank 7 px. Rider 1.85 m with the helmet = 85 px: helmet top on row 1, head 11 px, hip on the saddle
(34, 42), shoulder (40, 20), hands on the grips (59, 40). Legs drawn to the pedals at 3 and 9 o'clock."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
G = 200
c, d, m, dm, _ = frame(256, 256, ground=G, pepper_x=6)
SKIN, HELMET = (225, 190, 160, 255), (200, 200, 205, 255)
COLS = {'A': {'coat': (170, 70, 70, 255), 'legs': (80, 80, 90, 255), 'helmet': (225, 225, 230, 255), 'extra': None},
        'B': {'coat': (80, 120, 85, 255), 'legs': (80, 95, 130, 255), 'helmet': (150, 150, 155, 255), 'extra': (140, 110, 80, 255)},
        'C': {'coat': (230, 230, 225, 255), 'legs': (70, 70, 80, 255), 'helmet': (190, 60, 60, 255), 'extra': None}}
def rider(D, f, ox, who, flip=False, s=1.0, gy=G):
    """one rider, rider coords (88 x 87 image, ground row 86) at scale s, put with its image left edge at ox"""
    k = COLS[who]
    def P(x, y):
        x, y = x * s, 86 - (86 - y) * s
        return (ox + (88 * s - 1 - x if flip else x), gy - 86 + y)
    def poly(pts, col): D.polygon([P(*p) for p in pts], fill=f(col))
    def line(pts, col, w): D.line([P(*p) for p in pts], fill=f(col), width=max(1, round(w * s)))
    def ell(x0, y0, x1, y1, col):
        a, b = P(x0, y0), P(x1, y1); D.ellipse([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=f(col))
    line([(34, 44), (41, 58), (34, 81)], k['legs'], 5)                       # far leg to the pedal at 9 o'clock
    line([(36, 44), (50, 54), (47, 81)], k['legs'], 6)                       # near leg to the pedal at 3 o'clock
    poly([(43, 79), (52, 79), (52, 82), (43, 82)], (90, 60, 45, 255))        # near shoe
    if who == 'B' and k['extra']: poly([(29, 22), (36, 20), (37, 36), (29, 37)], k['extra'])   # backpack
    if who == 'A':                                                           # a coat to mid thigh
        poly([(35, 19), (45, 19), (46, 30), (44, 48), (30, 50), (31, 30)], k['coat'])
    else:
        poly([(35, 19), (45, 19), (46, 30), (42, 45), (31, 45), (32, 30)], k['coat'])
    line([(42, 22), (51, 32), (59, 40)], k['coat'], 4)                       # near arm to the grip
    ell(57, 38, 61, 42, SKIN)                                                # hand
    ell(37, 5, 48, 16, SKIN)                                                 # head 11 px
    poly([(36, 6), (38, 2), (42, 1), (47, 2), (50, 6), (49, 8), (36, 8)], k['helmet'])   # helmet, top on row 1
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    rider(D, f, 46, 'A'); rider(D, f, 104, 'B'); rider(D, f, 154, 'C', flip=True)
save('rw_riders_n07', c, m, {'ground': G, 'pepper_x': 6, 'riders': {'A': [46, 'right'], 'B': [104, 'right'], 'C': [154, 'left']},
                             'rider_image': [88, 87], 'image_ground_row': 86})
