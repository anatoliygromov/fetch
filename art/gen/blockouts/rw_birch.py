"""River Walk street birch (back layer, 46 px/m), replaces tree_far (x 520 and 2978, a 2.2 m tree: a sapling at the
quay's scale, outlined like an obstacle). 6 Nov 2026. A silver birch at true scale, cut by the top of the screen like
rw_lime: trunk 0.35 m = 16 px, clear trunk 2.5 m = 115 px, crown 4.3 m = 200 px wide running out of the top edge.
256 frame (GPT 2.5 1K draws it on a 4 px grid, as the City Park lime did on 2K)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 256, 256
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 150                       # trunk centre (Pepper stands left of the crown)
t0, t1 = cx - 8, cx + 7        # 16 px trunk
cl, cr = cx - 100, cx + 99     # crown 200 px wide
under = G - 115                # crown underside 115 px up (2.5 m)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl, -200, cr, under + 6], fill=f(CROWN))                         # crown, its top far above the frame
    D.rectangle([t0, under - 40, t1, G - 1], fill=f(TRUNK))                     # trunk
    D.polygon([(t0 - 3, G - 1), (t0, G - 10), (t1, G - 10), (t1 + 3, G - 1)], fill=f(TRUNK))   # foot
    D.line([(cx - 3, under - 30), (cx - 55, under - 80)], fill=f(LIMB), width=6)               # main limbs
    D.line([(cx + 3, under - 35), (cx + 50, under - 90)], fill=f(LIMB), width=5)
    D.line([(cx, under - 40), (cx - 2, 0)], fill=f(LIMB), width=6)
save('rw_birch', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'underside': under,
                        'note': 'crown runs out of the top edge'})
