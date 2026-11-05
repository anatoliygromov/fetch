"""City Park lime (back layer, 46 px/m), the tall level's climbed limes (screen 6: x 1528 and the ash slot at 1916).
Owner's pick 26 Oct (City Park plan decision 1): true-width trunk 0.5 m = 23 px, one leaf mass per tree whose top is
above the world. The level is 384 px tall and the high road's camera reaches y 0, so the tree must run from the path
(y 328) past y 0: 328 px and more. A 1K SpriteCook render holds about 256 art px, so this job is 2K on a 512 frame
(the probe checks that 2K returns a ~512 px grid). Crown 250 px wide like the approved River Walk lime, its underside
90 px up so the limes' branch ledges (96 to 144 px up) sit in the leaves."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 256
t0, t1 = cx - 11, cx + 11      # 23 px trunk
cl, cr = cx - 125, cx + 124    # crown 250 px wide
under = G - 90                 # crown underside 90 px up (2.0 m)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl, -260, cr, under + 4], fill=f(CROWN))                         # crown, its top far above the frame
    D.rectangle([t0, under - 40, t1, G - 1], fill=f(TRUNK))
    D.polygon([(t0 - 4, G - 1), (t0, G - 14), (t1, G - 14), (t1 + 4, G - 1)], fill=f(TRUNK))
    D.line([(cx - 4, under - 30), (cx - 75, under - 90)], fill=f(LIMB), width=9)
    D.line([(cx + 4, under - 30), (cx + 70, under - 100)], fill=f(LIMB), width=8)
    D.line([(cx, under - 40), (cx - 4, 0)], fill=f(LIMB), width=8)
save('cp_lime', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'underside': under,
                       'note': 'crown runs out of the top edge'})
