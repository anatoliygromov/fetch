"""Herring gull, drawn smaller than life on the owner's call (25 Oct 17:27, "the bird turns out massive" at 58 px):
wingspan 40 px, body 19 px, gliding side view facing right, wings spread and raised a little (the animation source).
Frame 96 x 72 with Pepper at 1x for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(96, 72, ground=70, pepper_x=2)
BODY, WING, TIP, BEAK = (220, 220, 225, 255), (150, 150, 160, 255), (60, 60, 70, 255), (230, 190, 60, 255)
cx, cy = 70, 22                                   # body centre, flying above the dog
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cx - 9, cy - 3, cx + 9, cy + 3], fill=f(BODY))                # body 19 px
    D.ellipse([cx + 5, cy - 5, cx + 11, cy], fill=f(BODY))                   # head
    D.polygon([(cx + 11, cy - 4), (cx + 14, cy - 3), (cx + 11, cy - 2)], fill=f(BEAK))
    D.polygon([(cx - 9, cy - 1), (cx - 13, cy - 3), (cx - 13, cy + 1)], fill=f(BODY))   # tail
    D.polygon([(cx - 3, cy - 2), (cx - 20, cy - 12), (cx - 22, cy - 10), (cx - 1, cy + 1)], fill=f(WING))  # far wing up-back
    D.polygon([(cx + 1, cy - 2), (cx + 16, cy - 11), (cx + 18, cy - 9), (cx + 3, cy + 1)], fill=f(WING))  # near wing
    D.polygon([(cx - 18, cy - 11), (cx - 22, cy - 13), (cx - 22, cy - 9)], fill=f(TIP))
    D.polygon([(cx + 14, cy - 10), (cx + 18, cy - 12), (cx + 18, cy - 8)], fill=f(TIP))
save('rw_gull', c, m, {'ground': G, 'pepper_x': 2})
