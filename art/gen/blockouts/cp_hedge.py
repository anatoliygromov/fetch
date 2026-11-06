"""City Park hedge (play, 46 px/m), board redraw 25 Oct; placement audit: "a hedge to the ground with a crawl gap of
leaves" (the old one read as topiary on stilts). Slot: riverwalk/art/scene/park_hedge.png, 64 x 72, drawn at the
HEDGE box's top (x 528, y 256; solid 64 x 53, the crawl gap under it is 19 px tall, y 309-328 on the path).
A clipped box hedge 1.57 m tall: the clipped body (rows 0-52, what Pepper stands on and bumps), and under it the
shady gap at the hedge's foot (rows 53-71): woody stems in deep shade with leaves on the ground, the hedge's sides
reaching the ground. Frame 256 x 256 (SpriteCook's own grid at 1K), Pepper at 1x on the same ground line."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=240, pepper_x=8)
OX, OY = 110, G - 72
BODY, SHADE, STEM, LITTER = (150, 150, 150, 255), (60, 60, 64, 255), (110, 95, 85, 255), (175, 140, 110, 255)
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rounded_rectangle(R(0, 0, 63, 56), radius=3, fill=f(BODY))      # the clipped body, a ragged leafy lower edge
    D.rectangle(R(0, 50, 7, 71), fill=f(BODY))                         # the hedge's left side to the ground
    D.rectangle(R(56, 50, 63, 71), fill=f(BODY))                       # and its right side
    D.rectangle(R(8, 57, 55, 69), fill=f(SHADE))                       # the shady gap under it
    for sx in (13, 22, 31, 40, 49):
        D.rectangle(R(sx, 55, sx + 1, 69), fill=f(STEM))               # woody stems in the shade
    D.rectangle(R(8, 70, 55, 71), fill=f(LITTER))                      # fallen leaves on the ground in the gap
save('cp_hedge', c, m, {'ox': OX, 'oy': OY, 'art': [64, 72], 'solid_rows': [0, 52], 'gap_rows': [53, 71]})
