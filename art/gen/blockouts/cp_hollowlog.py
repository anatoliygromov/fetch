"""City Park hollow log (play, obstacle, 46 px/m): Pepper hops over it or crawls through (piece at x 1564, y 302, the
top a ledge 42 wide, foot 328). Slot riverwalk/art/scene/park_hollowlog.png, 44 x 27, drawn at x - 1, y - 1. A fallen
trunk 0.95 m long and 0.58 m thick lying along the path, its left end cut and hollow (the dark hole Pepper crawls
into), its right end broken. Match the approved park_log (bark and cut end). Frame 256 x 256, Pepper at 1x."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=240, pepper_x=8)
OX, OY = 110, G - 27
BARK, FACE, HOLE = (120, 120, 125, 255), (200, 200, 200, 255), (40, 40, 45, 255)
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rounded_rectangle(R(4, 0, 43, 26), radius=6, fill=f(BARK))      # the trunk's side
    D.ellipse(R(0, 0, 13, 26), fill=f(FACE))                           # the cut end: a ring of light wood
    D.ellipse(R(3, 4, 10, 22), fill=f(HOLE))                           # the hollow
save('cp_hollowlog', c, m, {'ox': OX, 'oy': OY, 'art': [44, 27]})
