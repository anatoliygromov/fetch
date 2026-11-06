"""Downtown flower tub (play, 46 px/m): the TUB box is 32 x 28 (0.70 x 0.61 m, a wooden planter tub, true size) and
the plant on it was a 17 px sprig. The new plant: a clipped round box shrub, 0.55 m (25 px) across and 0.5 m (23 px)
over the rim, standing in the tub's soil. Art 32 x 51 (rows 0-22 the shrub, rows 23-50 the tub = the box). Frame 256 x
256 (NB 2.1 1K draws about 4 image px per art px), Pepper at 1x on the same ground for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 256, 256
c, d, m, dm, G = frame(W, H, ground=H - 40, pepper_x=8)
OX, OY = 120, G - 51                     # art (0, 0) in the frame
TUB, RIM, SHRUB, SOIL = (120, 120, 128, 255), (165, 165, 172, 255), (190, 190, 196, 255), (80, 80, 86, 255)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([OX + 3, OY, OX + 28, OY + 25], fill=f(SHRUB))                 # the clipped ball, 26 x 26
    D.rectangle([OX, OY + 23, OX + 31, OY + 50], fill=f(TUB))                # the tub, 32 x 28
    D.rectangle([OX, OY + 23, OX + 31, OY + 25], fill=f(RIM))                # its rim
save('town_tub', c, m, {'ox': OX, 'oy': OY, 'art': [32, 51], 'ground': G})
