"""City Park old oak (back layer, 46 px/m), screen 6 (x 1724, the level's OAK). Owner's pick 26 Oct (plan decision 1):
true-width trunk 1 m = 46 px (24 today), one leaf mass with its top above the world. Its low boughs are the play
ledges drawn by code (y 244 to 300, 28 to 84 px up) and stay; the leaf mass starts above them (underside about
110 px up at the trunk, lower at the sides) so the CROWN ledge (136 px up) and the golden twig (176 up) sit in the
leaves. Crown 470 px wide (10 m): it fills screen 6 at the high road. 2K on a 512 frame, as cp_lime."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 256
t0, t1 = cx - 14, cx + 14      # 29 px drawn for a 46 px trunk: retry 1 (5 Nov), the 2K probe drew the trunk 1.6x (74 px)
cl, cr = cx - 235, cx + 234    # crown 470 px wide (10 m): fills the frame, so the model has no room to enlarge it (5 Nov lime pilot: a 250 px crown came back 468)
under = G - 110
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl, -360, cr, under + 30], fill=f(CROWN))
    D.rectangle([t0, under - 30, t1, G - 1], fill=f(TRUNK))
    D.polygon([(t0 - 10, G - 1), (t0, G - 26), (t1, G - 26), (t1 + 10, G - 1)], fill=f(TRUNK))   # root flare
    D.line([(cx - 10, under - 10), (cx - 110, under - 70)], fill=f(LIMB), width=10)
    D.line([(cx + 10, under - 10), (cx + 105, under - 80)], fill=f(LIMB), width=10)
    D.line([(cx, under - 20), (cx - 6, 0)], fill=f(LIMB), width=9)
save('cp_oak', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'underside': under,
                      'note': 'crown runs out of the top edge'})
