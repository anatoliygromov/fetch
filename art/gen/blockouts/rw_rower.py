"""The rower of the River Walk rowing boat on his own, for the rowing loop (pixel engine animation from this 1x still):
an adult in a navy coat and a flat cap seated on the thwart, facing right (the stern), both hands on the oar handles;
the near oar from his hands down to the water, blade under the surface. 63 x 52 (row 0 = world y 177, his seat row 33,
waterline row 47). The hull is the boat's own still (rw_rowboat); this sprite is drawn over it at its thwart.
Pixel Engine Image works at the exact size, so the frame is the sprite itself with Pepper beside it for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
OX, OY = 70, 20
c, d, m, dm, G = frame(150, 112, ground=OY + 35, pepper_x=8)
SKIN, COAT, CAP, TROUS, OAR, BLADE = ((225, 190, 160, 255), (60, 80, 140, 255), (60, 60, 70, 255), (70, 70, 80, 255),
    (170, 140, 90, 255), (150, 120, 80, 255))
def P(pts): return [(OX + x, OY + y) for x, y in pts]
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse(R(30, 1, 41, 12), fill=f(SKIN)); D.rectangle(R(29, 0, 42, 4), fill=f(CAP))            # head 11 px, cap
    D.polygon(P([(26, 13), (44, 13), (47, 33), (24, 33)]), fill=f(COAT))                           # torso
    D.rectangle(R(40, 30, 60, 35), fill=f(TROUS))                                                  # thighs to the stretcher
    D.polygon(P([(42, 18), (62, 22), (62, 26), (42, 23)]), fill=f(COAT))                           # arms
    D.line(P([(62, 24), (14, 46), (4, 50)]), fill=f(OAR), width=2)                                 # oar
    D.polygon(P([(0, 47), (10, 48), (8, 51), (0, 51)]), fill=f(BLADE))
save('rw_rower', c, m, {'ox': OX, 'oy': OY, 'art': [63, 52]})
