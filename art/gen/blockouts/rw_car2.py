"""River Walk road car 2: a small white panel van seen from the side, nose to the LEFT. Near lane, 55 px/m:
4.4 m long = 242 px, 1.85 m tall = 102 px, wheels 0.62 m = 34 px, wheelbase 2.75 m = 151 px. Frame 256 x 256."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=96, pepper_x=8)
G = 236
BODY, GLASS, WHEEL, LAMP = (150, 150, 160, 255), (205, 205, 215, 255), (70, 70, 80, 255), (230, 230, 200, 255)
x0, x1 = 7, 248                          # 242 px
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(x0, G - 44), (x0 + 4, G - 52), (x0 + 30, G - 58), (x0 + 58, G - 96), (x0 + 66, G - 101), (x1 - 4, G - 101),
               (x1, G - 96), (x1, G - 12), (x0 + 2, G - 12)], fill=f(BODY))      # short bonnet, tall box body
    D.polygon([(x0 + 36, G - 60), (x0 + 60, G - 92), (x0 + 72, G - 92), (x0 + 72, G - 60)], fill=f(GLASS))   # cab window
    D.rectangle([x0 + 1, G - 44, x0 + 7, G - 38], fill=f(LAMP))
    for cx in (x0 + 38, x0 + 38 + 151):
        D.ellipse([cx - 17, G - 33, cx + 16, G], fill=f(WHEEL))                         # wheels 34 px
save('rw_car2', c, m, {'ground': G, 'pepper_x': 8})
