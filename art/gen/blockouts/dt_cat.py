"""The Downtown cat (an Abyssinian, the owner's cat) sitting, 30 px to the ear tips, "slightly smaller than the dog"
(owner 25 Oct 20:16; Pepper's head top is 38 px), 22 px wide with the tail round the paws, facing right.
Frame 96 x 56 with Pepper at 1x."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(96, 56, ground=54, pepper_x=2)
COAT, EAR = (205, 120, 60, 255), (170, 90, 50, 255)
x0 = 62
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([x0, G - 20, x0 + 16, G - 1], fill=f(COAT))                   # haunch and body
    D.rectangle([x0 + 10, G - 22, x0 + 16, G - 1], fill=f(COAT))            # chest and front legs
    D.ellipse([x0 + 8, G - 29, x0 + 21, G - 17], fill=f(COAT))              # head
    D.polygon([(x0 + 9, G - 25), (x0 + 11, G - 30), (x0 + 14, G - 25)], fill=f(EAR))
    D.polygon([(x0 + 16, G - 25), (x0 + 20, G - 30), (x0 + 21, G - 23)], fill=f(EAR))
    D.line([(x0, G - 1), (x0 - 3, G - 8)], fill=f(COAT), width=3)            # tail tip
save('dt_cat', c, m, {'ground': G, 'pepper_x': 2})
