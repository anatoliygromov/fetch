"""City Park magpie in flight (6 Nov): the same bird as cp_magpie (30 px beak tip to tail tip), side view facing
right, wings raised: 30 x 22 px. The flap loop is animated from this still at 1x. Pepper at 1x for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(112, 64, ground=58, pepper_x=4)
X0, Y0 = 72, 20
BODY, WHITE, TAIL, WING = (70, 70, 78, 255), (210, 210, 216, 255), (110, 120, 130, 255), (90, 100, 120, 255)
def P(x, y): return (X0 + x, Y0 + y)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([P(0, 15), P(1, 17), P(12, 15), P(11, 12)], fill=f(TAIL))        # tail straight out behind
    D.ellipse([*P(9, 11), *P(24, 18)], fill=f(BODY))
    D.ellipse([*P(21, 10), *P(27, 16)], fill=f(BODY))
    D.polygon([P(26, 12), P(29, 13), P(26, 14)], fill=f(BODY))
    D.polygon([P(12, 13), P(9, 0), P(15, 2), P(19, 13)], fill=f(WING))        # wing raised
    D.ellipse([*P(13, 15), *P(20, 18)], fill=f(WHITE))
    D.line([P(18, 21), P(15, 18)], fill=f(BODY), width=1)                       # legs tucked
save('cp_magpie_fly', c, m, {'tail_x': X0, 'top_y': Y0, 'art': [30, 22]})
# the flap loop (pixel-engine animation of the flight still, 6 Nov) is sized by the same frame
save('cp_magpie_flap', c, m, {'tail_x': X0, 'top_y': Y0, 'art': [30, 22], 'from': 'cp_magpie_fly'})
