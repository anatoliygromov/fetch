"""River Walk road lane rider 1 (5 Nov, review fix round 1): the road's bike lane is drawn at 55 px/m (road.lua; the
cars are), so the lane rider is its own asset at that scale, never the promenade rider scaled. 1.85 m with the helmet =
102 px, bike 1.8 m = 99 px, wheel 0.70 m = 39 px. Only rows 0-49 show in the game (RIDER_TOP 190): head, body, hands,
handlebar; the legs and wheels are below the frame, so no pedal loop is needed. The shapes are the promenade rider's
blockout at 55/46 of its size (a blockout, not art). Frame 256 x 256 with Pepper at 1x."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=200, pepper_x=8)
k = 55 / 46
def P(x, y): return (round(130 + (x - 78) * k), round(G - (106 - y) * k))   # promenade blockout coords (G=106) -> here
WHEEL, BODY, FRAME, HELMET = (70, 70, 80, 255), (175, 175, 180, 255), (110, 110, 120, 255), (215, 215, 220, 255)
r = round(16 * k)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    for x in (78, 129):
        cx, cy = P(x, 90); D.ellipse([cx - r, cy - r, cx + r - 1, cy + r - 1], outline=f(WHEEL), width=2)
    rx, wy, crank, saddle, bars, mid = P(78, 90), P(129, 90), P(100, 93), P(91, 65), P(123, 60), P(118, 68)
    D.line([rx, crank, saddle, rx], fill=f(FRAME), width=2); D.line([crank, mid, saddle], fill=f(FRAME), width=2)
    D.line([wy, mid, bars], fill=f(FRAME), width=2)
    D.rectangle([*P(132, 64), *P(143, 72)], fill=f((150, 120, 80, 255)))      # basket
    D.line([P(86, 64), P(96, 64)], fill=f(FRAME), width=2)
    D.line([saddle, P(103, 40)], fill=f(BODY), width=11)
    D.ellipse([*P(101, 25), *P(112, 36)], fill=f(BODY))
    D.chord([*P(99, 21), *P(114, 34)], 180, 360, fill=f(HELMET))
    D.line([P(105, 43), P(123, 59)], fill=f(BODY), width=5)
    D.line([saddle, P(106, 72), P(103, 98)], fill=f(BODY), width=7)
save('rw_road_rider1', c, m, {'ground': G, 'pepper_x': 8})
