"""The Downtown cat (an Abyssinian, the owner's cat) sitting, at true scale (46 px/m): 0.33 m to the ear tips =
15 px, 0.25 m wide with the tail curled round the paws = 12 px, facing right. Frame 72 x 56 with Pepper at 1x."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(72, 56, ground=54, pepper_x=2)
COAT, EAR = (205, 120, 60, 255), (170, 90, 50, 255)
x0 = 56
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([x0, G - 10, x0 + 8, G - 1], fill=f(COAT))                    # haunch and body
    D.rectangle([x0 + 5, G - 11, x0 + 8, G - 1], fill=f(COAT))              # chest and front legs
    D.ellipse([x0 + 4, G - 15, x0 + 11, G - 9], fill=f(COAT))               # head
    D.polygon([(x0 + 5, G - 13), (x0 + 6, G - 15), (x0 + 7, G - 13)], fill=f(EAR))
    D.polygon([(x0 + 8, G - 13), (x0 + 10, G - 15), (x0 + 10, G - 12)], fill=f(EAR))
    D.line([(x0, G - 1), (x0 - 1, G - 4)], fill=f(COAT), width=2)            # tail tip
save('dt_cat', c, m, {'ground': G, 'pepper_x': 2})
