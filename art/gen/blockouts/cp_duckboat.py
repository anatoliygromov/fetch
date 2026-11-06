"""City Park duck boat (play, a mover Pepper rides, 46 px/m). Slot riverwalk/art/scene/park_boat_front.png, 54 x 33,
drawn at the mover's x - 3, y - 18 (DUCK BOAT box 48 x 6, deck y 346 = art row 18), mirrored when it paddles right.
Made facing LEFT. A little pedal boat shaped like a duck, seen exactly from the side: the hull's top edge is a flat
deck at row 18 over x 3-51, the neck and head rise at the bow (left), a short tail at the stern, the water from row
25 (the game tints it). Its size is set by the mover (the ladder doc: it needs mover changes to grow). Frame 256."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=240, pepper_x=8)
OX, OY = 110, G - 33
HULL, STRIPE, HEAD, BEAK, EYE = (200, 200, 205, 255), (200, 110, 90, 255), (215, 215, 220, 255), (230, 150, 60, 255), (40, 40, 40, 255)
def P(pts): return [(OX + x, OY + y) for x, y in pts]
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon(P([(1, 18), (53, 18), (53, 24), (49, 31), (42, 32), (10, 32), (4, 28), (1, 22)]), fill=f(HULL))   # hull
    D.polygon(P([(44, 18), (53, 11), (53, 18)]), fill=f(HULL))                                                  # tail
    D.rectangle(R(1, 22, 53, 23), fill=f(STRIPE))                                                             # rub stripe
    D.rounded_rectangle(R(6, 6, 14, 18), radius=3, fill=f(HEAD))                                              # neck
    D.ellipse(R(4, 0, 17, 11), fill=f(HEAD))                                                                  # head
    D.polygon(P([(0, 6), (5, 5), (5, 9), (1, 9)]), fill=f(BEAK))                                              # beak
    D.rectangle(R(9, 3, 10, 4), fill=f(EYE))                                                                  # eye
save('cp_duckboat', c, m, {'ox': OX, 'oy': OY, 'art': [54, 33], 'deck_row': 18, 'water_row': 25})
