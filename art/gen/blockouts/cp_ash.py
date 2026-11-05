"""City Park ash (back layer, 46 px/m), the tall level's ASH at x 1916 (screen 6's right edge and screen 7). Decision 1:
trunk 0.5 m = 23 px, one leaf mass whose top runs above the world; its crown leans right over the alder walk (world x
2000 to 2300, deck 128 px up) so the high road there runs through leaves. Trunk at x 90 of the frame, crown from x 10
to x 500 (490 px, 10.6 m, an old ash leaning to the open side), underside 95 px up. 512 frame, 2K at 4 px per art px."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 120
t0, t1 = cx - 11, cx + 11
under = G - 95
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([10, -300, 501, under + 4], fill=f(CROWN))
    D.rectangle([t0, under - 40, t1, G - 1], fill=f(TRUNK))
    D.polygon([(t0 - 4, G - 1), (t0, G - 14), (t1, G - 14), (t1 + 4, G - 1)], fill=f(TRUNK))
    D.line([(cx + 2, under - 30), (cx + 150, under - 110)], fill=f(LIMB), width=8)
    D.line([(cx + 4, under - 60), (cx + 300, under - 170)], fill=f(LIMB), width=7)
    D.line([(cx - 2, under - 35), (cx - 60, under - 120)], fill=f(LIMB), width=7)
    D.line([(cx, under - 40), (cx + 20, 0)], fill=f(LIMB), width=8)
save('cp_ash', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'underside': under, 'note': 'crown leans right over the alder walk'})
