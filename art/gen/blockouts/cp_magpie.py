"""City Park magpie, perched (6 Nov): size B from docs/review/06nov/cp_critters/magpie_sizes_4x.png, 30 px beak tip to
tail tip, 18 px tall (feet to crown), facing right. The girl's 6 px ball hangs from the beak (St:beak). Grey shapes
only, Pepper at 1x for scale. Pixel Engine Image draws it at exactly 30 x 18 from text; this frame is the scale record."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(112, 64, ground=58, pepper_x=4)
X0 = 72                                         # tail tip
BODY, WHITE, TAIL, LEG = (70, 70, 78, 255), (210, 210, 216, 255), (110, 120, 130, 255), (60, 60, 66, 255)
def P(x, y): return (X0 + x, G - 18 + y)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([P(0, 13), P(1, 15), P(14, 10), P(12, 7)], fill=f(TAIL))
    D.ellipse([*P(10, 4), *P(23, 13)], fill=f(BODY))
    D.ellipse([*P(19, 0), *P(26, 7)], fill=f(BODY))
    D.polygon([P(25, 3), P(29, 4), P(25, 5)], fill=f(LEG))
    D.ellipse([*P(15, 8), *P(21, 12)], fill=f(WHITE))
    D.ellipse([*P(12, 5), *P(17, 8)], fill=f(WHITE))
    for lx in (16, 18): D.line([P(lx, 12), P(lx, 17)], fill=f(LEG), width=1)
save('cp_magpie', c, m, {'ground': G, 'tail_x': X0, 'art': [30, 18]})
