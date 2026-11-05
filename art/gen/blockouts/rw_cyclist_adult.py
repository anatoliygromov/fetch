"""Adult city cyclist 1 (River Walk promenade bikes and the road's bike lane, char layer). 46 px/m: helmet top 1.85 m
= 85 px, bike 1.8 m = 83 px, wheel 0.70 m = 32 px, hubs 51 px apart, saddle 41 px, bars 46 px, head 11 px.
5 Nov: re-drawn on SpriteCook's own 256 x 256 grid (NB 2.1 pixel mode at 1K returns about 1 px = 1 art px on a
256 frame; docs/art_generation.md), Pepper at 1x, the rider in the same shapes as the 25 Oct blockout, moved right."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=170, pepper_x=8)
WHEEL, BODY, FRAME, HELMET = (70, 70, 80, 255), (175, 175, 180, 255), (110, 110, 120, 255), (215, 215, 220, 255)
X = 66                                  # shift of the 25 Oct shapes (Pepper ends at x 60)
rx, fx, wy = 78 + X, 129 + X, G - 16
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    for x in (rx, fx): D.ellipse([x - 16, wy - 16, x + 15, wy + 15], outline=f(WHEEL), width=2)
    crank, saddle, bars = (100 + X, G - 13), (91 + X, G - 41), (123 + X, G - 46)
    D.line([(rx, wy), crank, saddle, (rx, wy)], fill=f(FRAME), width=2)
    D.line([crank, (118 + X, G - 38), saddle], fill=f(FRAME), width=2)
    D.line([(fx, wy), (118 + X, G - 38), bars], fill=f(FRAME), width=2)
    D.rectangle([132 + X, G - 42, 143 + X, G - 34], fill=f((150, 120, 80, 255)))      # basket
    D.line([(86 + X, G - 42), (96 + X, G - 42)], fill=f(FRAME), width=2)              # saddle
    D.line([saddle, (103 + X, G - 66)], fill=f(BODY), width=9)                        # torso
    D.ellipse([101 + X, G - 81, 112 + X, G - 70], fill=f(BODY))                       # head, 11 px
    D.chord([99 + X, G - 85, 114 + X, G - 72], 180, 360, fill=f(HELMET))              # helmet, top at G-85
    D.line([(105 + X, G - 63), (123 + X, G - 47)], fill=f(BODY), width=4)             # arm
    D.line([saddle, (106 + X, G - 34), (103 + X, crank[1] + 5)], fill=f(BODY), width=6)  # leg
save('rw_cyclist_adult', c, m, {'ground': G, 'pepper_x': 8})
