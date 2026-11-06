"""City Park stepping stone and hollow log in one frame (play, obstacles, 46 px/m), one GPT 2.5 job for two slots
(6 Nov: Nano Banana 2.1 drew the small hedge at twice its blockout width, so small props go to GPT 2.5, which follows
the blockout's grid; the two are paired to save a job).
- park_stone.png, 26 x 55: five in the ponds and the creek (STONE boxes 24 x 52 at x 736, 792, 2056, 2136, 2216; top
  y 332, water y 352), drawn at x - 1, y - 1. A granite boulder 0.52 m wide standing 0.45 m out of the water; the
  top 21 rows are above the water, the rest under it (the game tints it with the pond).
- park_hollowlog.png, 44 x 27: the piece at x 1564 (top ledge y 302, foot 328), drawn at x - 1, y - 1. A fallen
  trunk 0.95 m long, 0.58 m thick, lying along the path, its left end cut and hollow; match the approved park_log.
Frame 256 x 256, Pepper at 1x on the same ground line."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=240, pepper_x=8)
SX, SY = 100, G - 55                     # the stone
LX, LY = 160, G - 27                     # the log
ROCK, WET, LINE = (150, 150, 155, 255), (95, 95, 100, 255), (60, 120, 170, 255)
BARK, FACE, HOLE = (120, 120, 125, 255), (200, 200, 200, 255), (40, 40, 45, 255)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rounded_rectangle([SX, SY, SX + 25, SY + 54], radius=8, fill=f(ROCK))
    D.rectangle([SX + 1, SY + 18, SX + 24, SY + 54], fill=f(WET))
    D.rounded_rectangle([LX + 4, LY, LX + 43, LY + 26], radius=6, fill=f(BARK))
    D.ellipse([LX, LY, LX + 13, LY + 26], fill=f(FACE))
    D.ellipse([LX + 3, LY + 4, LX + 10, LY + 22], fill=f(HOLE))
for x in range(SX - 6, SX + 32):
    if not (SX <= x <= SX + 25): d.point((x, SY + 21), fill=LINE)
save('cp_rocklog', c, m, {'stone': [SX, SY, 26, 55], 'log': [LX, LY, 44, 27], 'water_row': 21})
