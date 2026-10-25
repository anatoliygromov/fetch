"""Herring gull, drawn smaller than life on the owner's call (25 Oct 17:27, "the bird turns out massive" at 58 px):
wingspan 32 px, body 15 px (second size call, 20:16: "the gull needs to be smaller too"), gliding side view facing right, wings spread and raised a little (the animation source).
Frame 96 x 72 with Pepper at 1x for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(96, 72, ground=70, pepper_x=2)
BODY, WING, TIP, BEAK = (220, 220, 225, 255), (150, 150, 160, 255), (60, 60, 70, 255), (230, 190, 60, 255)
cx, cy = 70, 22                                   # body centre, flying above the dog
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cx - 7, cy - 2, cx + 7, cy + 2], fill=f(BODY))                # body 15 px
    D.ellipse([cx + 4, cy - 4, cx + 9, cy], fill=f(BODY))                    # head
    D.polygon([(cx + 9, cy - 3), (cx + 11, cy - 2), (cx + 9, cy - 1)], fill=f(BEAK))
    D.polygon([(cx - 7, cy - 1), (cx - 10, cy - 2), (cx - 10, cy + 1)], fill=f(BODY))   # tail
    D.polygon([(cx - 2, cy - 2), (cx - 16, cy - 9), (cx - 17, cy - 7), (cx - 1, cy + 1)], fill=f(WING))  # far wing up-back
    D.polygon([(cx + 1, cy - 2), (cx + 13, cy - 9), (cx + 14, cy - 7), (cx + 3, cy + 1)], fill=f(WING))  # near wing
    D.polygon([(cx - 14, cy - 8), (cx - 17, cy - 10), (cx - 17, cy - 7)], fill=f(TIP))
    D.polygon([(cx + 11, cy - 8), (cx + 14, cy - 10), (cx + 14, cy - 7)], fill=f(TIP))
save('rw_gull', c, m, {'ground': G, 'pepper_x': 2})
