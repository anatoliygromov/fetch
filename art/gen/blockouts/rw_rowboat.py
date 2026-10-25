"""River Walk rowing boat with its rower at true scale (46 px/m), owner 25 Oct 20:18 ("go": real size): a 3.5 m
wooden rowing boat = 160 px long, the hull 0.45 m = 21 px from gunwale to waterline, the rower an adult seated
facing the stern, head top about 1.0 m above the gunwale = 46 px, oars out. Side view facing left (the way it rows).
Frame 256 x 256 (SpriteCook's own pixel grid at 1K, see docs/art_generation.md) with Pepper at 1x."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=150, pepper_x=8)
HULL, BODY, HEAD, OAR = (120, 90, 60, 255), (150, 150, 160, 255), (210, 180, 160, 255), (100, 80, 60, 255)
x0, x1 = 60, 219                      # 160 px hull
wl = G + 15                           # waterline 15 px below the dog's feet line (the deck is her floor)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon([(x0, G - 6), (x1, G - 6), (x1 - 12, wl), (x0 + 10, wl)], fill=f(HULL))     # hull 21 px deep
    D.rectangle([128, G - 40, 146, G - 7], fill=f(BODY))                                 # rower's body, seated mid-aft
    D.ellipse([130, G - 52, 144, G - 38], fill=f(HEAD))                                  # head (top at gunwale - 46)
    D.line([(137, G - 25), (96, G + 14)], fill=f(OAR), width=3)                          # oar into the water
save('rw_rowboat', c, m, {'ground': G, 'pepper_x': 8})
