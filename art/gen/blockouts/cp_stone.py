"""City Park stepping stone (play, obstacle, 46 px/m): five in the ponds and the creek (STONE boxes 24 x 52 at x 736,
792, 2056, 2136, 2216; top y 332, the water's surface y 352). Slot riverwalk/art/scene/park_stone.png, 26 x 55,
drawn at the box's x - 1, y - 1. A granite boulder 0.52 m wide standing 0.45 m out of the water: the top 21 rows are
above the water, the rest is under it (the game tints it with the pond). Frame 256 x 256, Pepper at 1x."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=240, pepper_x=8)
OX, OY = 120, G - 55
ROCK, WET, LINE = (150, 150, 155, 255), (95, 95, 100, 255), (60, 120, 170, 255)
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rounded_rectangle(R(0, 0, 25, 54), radius=8, fill=f(ROCK))      # the boulder, a rounded top
    D.rectangle(R(1, 18, 24, 20), fill=f(WET))                         # wet band at the waterline
    D.rectangle(R(1, 21, 24, 54), fill=f(WET))                         # under the water
for x in range(OX - 6, OX + 32):
    if not (OX <= x <= OX + 25): d.point((x, OY + 21), fill=LINE)       # the water line beside it (not in the mask)
save('cp_stone', c, m, {'ox': OX, 'oy': OY, 'art': [26, 55], 'water_row': 21})
