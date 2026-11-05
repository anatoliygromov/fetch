"""River Walk road car 1: a dark blue Swedish estate car seen from the side, nose to the LEFT (road.lua: car art faces
left). Near lane, 55 px/m (road.lua, the road band in front of the promenade): 4.25 m long = 233 px, 1.45 m tall =
80 px, wheels 0.64 m = 35 px, wheelbase 2.7 m = 149 px, ground clearance 8 px. Frame 256 x 256 (SpriteCook's own
pixel grid at 1K). Pepper at 1x on her own line above it for scale (she is on the promenade, 46 px/m)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
from PIL import Image
c, d, m, dm, G = frame(256, 256, ground=96, pepper_x=8)
G = 236                                  # the car's road line
BODY, GLASS, WHEEL, LAMP = (150, 150, 160, 255), (205, 205, 215, 255), (70, 70, 80, 255), (230, 230, 200, 255)
x0, x1 = 12, 244                         # 233 px
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(x0, G - 44), (x0 + 6, G - 50), (x0 + 58, G - 54), (x0 + 92, G - 80), (x1 - 8, G - 80), (x1, G - 70),
               (x1, G - 14), (x0 + 2, G - 14)], fill=f(BODY))                     # body: bonnet, windscreen, long roof
    D.polygon([(x0 + 64, G - 54), (x0 + 94, G - 76), (x1 - 12, G - 76), (x1 - 10, G - 54)], fill=f(GLASS))  # windows
    D.rectangle([x0 + 1, G - 44, x0 + 7, G - 38], fill=f(LAMP))                       # headlamp (nose, left)
    for cx in (x0 + 45, x0 + 45 + 149):
        D.ellipse([cx - 17, G - 34, cx + 17, G], fill=f(WHEEL))                         # wheels 35 px
save('rw_car1', c, m, {'ground': G, 'pepper_x': 8})
