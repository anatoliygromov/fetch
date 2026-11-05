"""River Walk boat (the 'ferry' of screen 6): a small harbour water taxi, a 5.5 m motor launch, at true scale on Pepper's
line (46 px/m). Its size is set by the route Pepper already runs and nothing of it moves: deck y 206 over x 2-237 of
the art, the cabin roof y 184 over x 60-180, the wheelhouse roof y 154 over x 97-145, waterline y 224, bottom y 233.
The art is 252 x 79 (rows 0-78 = world y 154-232; the old 93 px image had 14 empty-ish rows of mast above the roof).
Frame 256 x 256 (SpriteCook's own pixel grid at 1K), Pepper at 1x above it for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=96, pepper_x=8)
OX, OY = 2, 160                          # art (0, 0) in the frame
HULL, BOTTOM, CABIN, GLASS, WH, SCREEN, BUOY, STAFF, FLAG = ((70, 70, 80, 255), (150, 80, 70, 255), (150, 150, 160, 255),
    (205, 205, 215, 255), (200, 200, 208, 255), (90, 90, 100, 255), (200, 60, 60, 255), (120, 100, 80, 255), (60, 90, 170, 255))
def P(pts): return [(OX + x, OY + y) for x, y in pts]
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon(P([(2, 52), (237, 52), (237, 66), (233, 78), (16, 78), (6, 64)]), fill=f(HULL))      # hull, bow raked left
    D.polygon(P([(9, 70), (236, 70), (233, 78), (16, 78)]), fill=f(BOTTOM))                         # below the waterline
    D.rectangle(R(60, 30, 180, 51), fill=f(CABIN))                                                  # cabin 121 x 22
    for i in range(4):
        D.rectangle(R(70 + i * 23, 36, 70 + i * 23 + 13, 45), fill=f(GLASS))                       # four windows
    D.rectangle(R(97, 0, 145, 29), fill=f(WH))                                                      # wheelhouse 49 x 30
    D.polygon(P([(98, 6), (110, 6), (110, 20), (98, 20)]), fill=f(SCREEN))                          # windscreen
    D.ellipse(R(161, 35, 171, 45), fill=f(BUOY))                                                    # lifebuoy
    D.rectangle(R(240, 20, 241, 51), fill=f(STAFF))                                                 # flag staff
    D.rectangle(R(242, 21, 251, 28), fill=f(FLAG))                                                  # flag
save('rw_ferry', c, m, {'ox': OX, 'oy': OY, 'art': [252, 79]})
