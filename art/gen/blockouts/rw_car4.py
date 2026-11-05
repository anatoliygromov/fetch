"""River Walk road car 4: a small red city hatchback seen from the side, nose to the LEFT. Near lane, 55 px/m:
3.3 m long = 181 px, 1.3 m tall = 71 px, wheels 0.58 m = 32 px, wheelbase 2.4 m = 132 px. Frame 256 x 256
(SpriteCook's own pixel grid at 1K). Pepper at 1x on her own line above it for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=96, pepper_x=8)
G = 236
BODY, GLASS, WHEEL, LAMP = (150, 150, 160, 255), (205, 205, 215, 255), (70, 70, 80, 255), (230, 230, 200, 255)
x0, x1 = 38, 218                         # 181 px
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(x0, G - 40), (x0 + 6, G - 46), (x0 + 40, G - 50), (x0 + 74, G - 71), (x1 - 22, G - 71), (x1 - 4, G - 58),
               (x1, G - 40), (x1, G - 12), (x0 + 2, G - 12)], fill=f(BODY))        # short bonnet, tall cabin, hatch
    D.polygon([(x0 + 48, G - 50), (x0 + 76, G - 67), (x1 - 24, G - 67), (x1 - 10, G - 52), (x1 - 10, G - 50)], fill=f(GLASS))
    D.rectangle([x0 + 1, G - 40, x0 + 7, G - 35], fill=f(LAMP))
    for cx in (x0 + 26, x0 + 26 + 132):
        D.ellipse([cx - 16, G - 31, cx + 15, G], fill=f(WHEEL))                         # wheels 32 px
save('rw_car4', c, m, {'ground': G, 'pepper_x': 8})
