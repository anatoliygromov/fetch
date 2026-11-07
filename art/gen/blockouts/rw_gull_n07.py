"""The River Walk gull at the owner's pick (board 7 Nov: gull_size_n0607 "24", option C of
docs/review/06nov-night/rw/size_sheets/gull_sizes_4x.png): 24 px wingspan, wings raised in a V, the body 13 px long
with a round head and a yellow bill on the left, the tail on the right. The game cell stays 26 x 26 (critters.lua
art.uq), so the still fits a cell with 1 px to spare each side. Pixel Engine Image draws at exactly 24 x 16 (it takes
no references; this blockout is the size answer key and the cut's mask)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(150, 112, ground=106, pepper_x=4)
WING, TIP, BODY, BILL = (170, 175, 185, 255), (60, 60, 70, 255), (235, 235, 238, 255), (230, 180, 60, 255)
X, Y = 90, 60                                # the gull's top-left in the frame (in the air, above Pepper's head)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(X + 11, Y + 11), (X + 6, Y + 5), (X + 1, Y + 0), (X + 3, Y + 0), (X + 9, Y + 4), (X + 13, Y + 10)], fill=f(WING))     # far wing up-left
    D.polygon([(X + 13, Y + 11), (X + 17, Y + 4), (X + 22, Y + 0), (X + 23, Y + 1), (X + 19, Y + 7), (X + 15, Y + 12)], fill=f(WING))  # near wing up-right
    D.polygon([(X + 1, Y + 0), (X + 3, Y + 0), (X + 4, Y + 2), (X + 2, Y + 2)], fill=f(TIP))
    D.polygon([(X + 22, Y + 0), (X + 23, Y + 1), (X + 22, Y + 3), (X + 21, Y + 2)], fill=f(TIP))
    D.ellipse([X + 5, Y + 10, X + 18, Y + 14], fill=f(BODY))                       # body 13 px
    D.polygon([(X + 17, Y + 11), (X + 22, Y + 11), (X + 21, Y + 14), (X + 17, Y + 13)], fill=f(BODY))   # tail
    D.ellipse([X + 2, Y + 8, X + 7, Y + 13], fill=f(BODY))                          # head
    D.polygon([(X + 2, Y + 10), (X + 0, Y + 11), (X + 2, Y + 12)], fill=f(BILL))    # bill
    D.line([(X + 10, Y + 15), (X + 12, Y + 15)], fill=f(BILL))                      # the feet tucked under the belly
save('rw_gull_n07', c, m, {'ground': G, 'pepper_x': 4, 'gull_xy': [X, Y], 'cell': [26, 26]})
