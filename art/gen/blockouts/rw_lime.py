"""River Walk street lime (back layer, 46 px/m), the tree on screens 1 and 4, cut by the top of the screen.
Retry 1 (25 Oct): the probe on a 384 frame came back on SpriteCook's own pixel grid at 0.67x (trunk 17 px, not 23),
because NB 2.1 at 1K draws art pixels of about 4 image px whatever the frame. So the frame is now 256 x 256, the size
of that grid, and holds only the part of the tree a player can see: trunk 0.5 m = 23 px, clear trunk 2.2 m = 100 px,
crown 5.0 m = 230 px wide running out of the top edge. Visible height 250 px (5.4 m); in the game the top 76 px sit
above the screen."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 256, 256
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 136                       # trunk centre
t0, t1 = cx - 11, cx + 11      # 23 px trunk
cl, cr = cx - 115, cx + 114    # crown 230 px wide
under = G - 100                # crown underside 100 px up (2.2 m)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl, -150, cr, under + 4], fill=f(CROWN))                         # crown, its top far above the frame
    D.rectangle([t0, under - 40, t1, G - 1], fill=f(TRUNK))                     # trunk
    D.polygon([(t0 - 4, G - 1), (t0, G - 14), (t1, G - 14), (t1 + 4, G - 1)], fill=f(TRUNK))   # flared foot
    D.line([(cx - 4, under - 30), (cx - 70, under - 75)], fill=f(LIMB), width=9)               # main limbs
    D.line([(cx + 4, under - 30), (cx + 66, under - 85)], fill=f(LIMB), width=8)
    D.line([(cx, under - 40), (cx - 4, 0)], fill=f(LIMB), width=8)
save('rw_lime', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'underside': under,
                       'note': 'crown runs out of the top edge'})
