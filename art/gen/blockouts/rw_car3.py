"""River Walk road car 3: a yellow taxi saloon seen from the side, nose to the LEFT. Near lane, 55 px/m:
4.4 m long = 242 px, 1.45 m body + 0.2 m roof sign = 1.65 m = 91 px, wheels 0.62 m = 34 px, wheelbase 2.7 m = 149 px."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=96, pepper_x=8)
G = 236
BODY, GLASS, WHEEL, LAMP = (150, 150, 160, 255), (205, 205, 215, 255), (70, 70, 80, 255), (230, 230, 200, 255)
x0, x1 = 7, 248                          # 242 px
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(x0, G - 40), (x0 + 6, G - 46), (x0 + 62, G - 50), (x0 + 96, G - 79), (x1 - 82, G - 79), (x1 - 50, G - 52),
               (x1 - 4, G - 50), (x1, G - 44), (x1, G - 12), (x0 + 2, G - 12)], fill=f(BODY))   # bonnet, cabin, boot
    D.rectangle([x0 + 121 - 16, G - 90, x0 + 121 + 15, G - 80], fill=f(LAMP))          # the roof sign: a lit box
    D.polygon([(x0 + 70, G - 52), (x0 + 98, G - 75), (x1 - 84, G - 75), (x1 - 56, G - 52)], fill=f(GLASS))
    D.rectangle([x0 + 1, G - 40, x0 + 7, G - 35], fill=f(LAMP))
    for cx in (x0 + 40, x0 + 40 + 149):
        D.ellipse([cx - 17, G - 33, cx + 16, G], fill=f(WHEEL))                         # wheels 34 px
save('rw_car3', c, m, {'ground': G, 'pepper_x': 8})
