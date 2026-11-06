"""(round 2, 6 Nov: the owner called the first render "really low quality": GPT 2.5 Sunburst 2K on a 512 frame, 4 image
px per art px, as the 5 Nov City Park lime; same parts at the same sizes.)
River Walk rowing boat (screens 8-9, the harbour) at true scale on Pepper's line (46 px/m), owner 6 Nov: "boat is
still ridiculously small" (the old one: hull 60 px = 1.3 m, a child-sized rower). A classic Stockholm wooden rowing
boat (eka), 4.0 m = 184 px, freeboard 0.35 m (16 px) amidships, the sheer rising 5 px to bow and stern; an adult
rower on the middle thwart facing the stern, as rowers do, both oars in the water. Art 185 x 56: row 0 = world y 177,
gunwale row 31 (y 208), Pepper's deck row 35 (y 212: she stands on the stern thwart), waterline row 47 (y 224),
keel row 55. Frame 512 x 512 (GPT 2.5 2K: 2048 px, 4 px per art px), Pepper at 1x on the deck line beside it for scale. Art 185 x 56 (hull x 0-184)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
OX, OY = 170, 300                        # art (0, 0) in the frame
c, d, m, dm, G = frame(512, 512, ground=OY + 32, pepper_x=8)
HULL, STRAKE, SEAT, SKIN, COAT, HAIR, TROUS, OAR, BLADE = ((90, 90, 100, 255), (150, 150, 160, 255), (175, 175, 185, 255),
    (225, 190, 160, 255), (60, 80, 140, 255), (110, 80, 50, 255), (70, 70, 80, 255), (170, 140, 90, 255), (150, 120, 80, 255))
def P(pts): return [(OX + x - 4, OY + y) for x, y in pts]
def R(x0, y0, x1, y1): return [OX + x0 - 4, OY + y0, OX + x1 - 4, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon(P([(4, 26), (40, 30), (96, 31), (152, 30), (188, 26), (184, 44), (172, 55), (20, 55), (8, 44)]), fill=f(HULL))  # hull, sheer rising to both ends
    D.line(P([(4, 27), (40, 31), (96, 32), (152, 31), (188, 27)]), fill=f(STRAKE), width=2)                                   # gunwale rail
    D.line(P([(8, 37), (40, 39), (96, 40), (152, 39), (184, 37)]), fill=f(STRAKE), width=1)                                   # a plank line
    # the rower (seated on the middle thwart at x 70-100, facing the stern = right; head 11 px, torso 0.6 m)
    D.ellipse(R(80, 1, 91, 12), fill=f(SKIN)); D.rectangle(R(80, 0, 91, 4), fill=f(HAIR))                                   # head, hair
    D.polygon(P([(76, 13), (94, 13), (97, 30), (74, 30)]), fill=f(COAT))                                                     # torso, coat
    D.polygon(P([(92, 18), (112, 22), (112, 26), (92, 23)]), fill=f(COAT))                                                   # arms forward to the handles
    D.line(P([(112, 24), (60, 47), (44, 52)]), fill=f(OAR), width=2)                                                         # the near oar, blade in the water
    D.polygon(P([(36, 49), (48, 50), (46, 54), (34, 53)]), fill=f(BLADE))
save('rw_rowboat_r2', c, m, {'ox': OX, 'oy': OY, 'art': [185, 56]})
