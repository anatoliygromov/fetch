"""River Walk road car 5: a silver boxy Swedish estate car seen from the side, nose to the LEFT. Near lane, 55 px/m:
4.4 m long = 242 px, 1.48 m tall = 81 px, wheels 0.62 m = 34 px, wheelbase 2.77 m = 152 px."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=96, pepper_x=8)
G = 236
BODY, GLASS, WHEEL, LAMP = (150, 150, 160, 255), (205, 205, 215, 255), (70, 70, 80, 255), (230, 230, 200, 255)
x0, x1 = 7, 248                          # 242 px
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(x0, G - 42), (x0 + 4, G - 48), (x0 + 56, G - 51), (x0 + 84, G - 80), (x1 - 8, G - 80), (x1 - 3, G - 76),
               (x1, G - 48), (x1, G - 12), (x0 + 2, G - 12)], fill=f(BODY))        # bonnet, long square roof, upright back
    D.polygon([(x0 + 64, G - 53), (x0 + 87, G - 76), (x1 - 12, G - 76), (x1 - 10, G - 53)], fill=f(GLASS))
    D.rectangle([x0 + 1, G - 42, x0 + 7, G - 37], fill=f(LAMP))
    for cx in (x0 + 40, x0 + 40 + 152):
        D.ellipse([cx - 17, G - 33, cx + 16, G], fill=f(WHEEL))                         # wheels 34 px
save('rw_car5', c, m, {'ground': G, 'pepper_x': 8})
