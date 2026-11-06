"""City Park weeping willow (back layer, 46 px/m), the pond's willow under the treetop walk (City Park tall, screen 3,
the WILLOWS crowns at x 664-944). 6 Nov 2026. Today three 1.8-2.0 m willows (park_willow, park_willow_tall, 65 px
wide): bushes at Pepper's scale. One willow at true scale instead: trunk 0.6 m (28 px; drawn 18, GPT 2.5 widens a
trunk about 1.5x, 5 Nov lime and oak), crown 7 m = 322 px wide whose top runs out of the frame, the hanging curtain
reaching down to about 1.2 m (55 px) above the ground. 512 frame, as cp_lime (GPT 2.5 2K, 4 px grid)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 300
t0, t1 = cx - 9, cx + 8
cl, cr = cx - 161, cx + 160
hang = G - 55                    # the lowest strands
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl, -260, cr, G - 150], fill=f(CROWN))                            # the crown, top above the frame
    D.rectangle([cl + 6, G - 260, cr - 6, hang], fill=f(CROWN))                  # the hanging curtain, straight sides
    D.rectangle([t0, G - 300, t1, G - 1], fill=f(TRUNK))
    D.polygon([(t0 - 6, G - 1), (t0, G - 16), (t1, G - 16), (t1 + 6, G - 1)], fill=f(TRUNK))
    D.line([(cx - 3, G - 220), (cx - 110, G - 330)], fill=f(LIMB), width=8)
    D.line([(cx + 3, G - 230), (cx + 100, G - 340)], fill=f(LIMB), width=7)
save('cp_willow', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'hang': hang,
                         'note': 'crown runs out of the top edge; the curtain hangs to 55 px above the ground'})
