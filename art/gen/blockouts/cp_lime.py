"""City Park lime, round 3 (5 Nov): the method changes after two failed review rounds (GPT 2.5 Sunburst, which follows
the reference grid, with the approved River Walk lime and the fixed old oak as style). Decision 1 at the plan's lime
size: trunk 0.5 m = 23 px at the base, one leaf mass 250 px wide (as rw_lime) whose top runs above the world: the tree
stands on y 319 in a 384 px tall level, so it must be over 330 px tall; here the crown runs out of the frame's top.
Crown underside 90 px up (the limes' ledges, 96 to 144 px up, sit in the leaves). 512 frame, 2K at 4 px per art px."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 256
t0, t1 = cx - 11, cx + 11
cl, cr = cx - 125, cx + 124
under = G - 90
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl, -330, cr, under + 4], fill=f(CROWN))
    D.rectangle([t0, under - 40, t1, G - 1], fill=f(TRUNK))
    D.polygon([(t0 - 4, G - 1), (t0, G - 14), (t1, G - 14), (t1 + 4, G - 1)], fill=f(TRUNK))
    D.line([(cx - 4, under - 30), (cx - 70, under - 90)], fill=f(LIMB), width=8)
    D.line([(cx + 4, under - 30), (cx + 66, under - 100)], fill=f(LIMB), width=7)
    D.line([(cx, under - 40), (cx - 3, 0)], fill=f(LIMB), width=8)
save('cp_lime', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'underside': under})
