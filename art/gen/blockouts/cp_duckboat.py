"""City Park duck boat (6 Nov): a two-seat pedal boat shaped like a duck, 2.0 m long = 92 px (46 px/m), seen from the
side, the duck facing LEFT (the game mirrors it when it paddles right). The flat deck where Pepper stands is the
mover's top (y0) on art row 47; the duck's head top is 1.0 m above the deck (row 0); the hull runs 12 px under the
deck to its keel (row 59; the pond's surface is at row 54, so rows 54-59 are under water). 92 x 60 px.
Pepper at 1x standing on the deck for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save, pepper
from PIL import Image
c, d, m, dm, G = frame(104, 96, ground=82, pepper_x=200)       # Pepper placed by hand below (on the deck)
OX, OY = 4, 82 - 47                                             # art (0, 0): deck row 47 on the frame's ground line
HULL, HULL2, HEAD, BEAK, SEAT, EYE = ((200, 200, 206, 255), (150, 150, 160, 255), (215, 215, 222, 255), (230, 150, 60, 255),
                                     (120, 120, 132, 255), (40, 40, 44, 255))
def P(pts): return [(OX + x, OY + y) for x, y in pts]
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon(P([(4, 47), (91, 47), (91, 44), (86, 40), (84, 47), (91, 52), (82, 59), (14, 59), (2, 52)]), fill=f(HULL))   # hull, tail up at the stern
    D.rectangle(R(4, 52, 88, 55), fill=f(HULL2))                                                # a band along the hull
    D.polygon(P([(10, 47), (12, 20), (22, 20), (26, 47)]), fill=f(HEAD))                        # neck
    D.ellipse(R(6, 0, 30, 24), fill=f(HEAD))                                                    # head
    D.polygon(P([(0, 11), (8, 8), (8, 16), (0, 14)]), fill=f(BEAK))                             # beak, pointing left
    D.ellipse(R(13, 7, 17, 11), fill=f(EYE))
    D.rectangle(R(56, 36, 62, 47), fill=f(SEAT))                                                # seat back
pp = pepper(); c.alpha_composite(pp, (OX + 30, 82 - pp.height))
save('cp_duckboat', c, m, {'ox': OX, 'oy': OY, 'deck_row': 47, 'water_row': 54, 'art': [92, 60]})
