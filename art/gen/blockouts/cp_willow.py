"""City Park weeping willow (back layer, 46 px/m), the pond's willow under the treetop walk (City Park tall, screen 3,
the WILLOWS crowns at x 664-944). 6 Nov 2026. Today three 1.8-2.0 m willows (park_willow, park_willow_tall, 65 px
wide): bushes at Pepper's scale. One willow at true scale instead: trunk 0.6 m (28 px; drawn 18, GPT 2.5 widens a
trunk about 1.5x, 5 Nov lime and oak), crown 7 m = 322 px wide whose top runs out of the frame, the hanging curtain
reaching down to about 1.2 m (55 px) above the ground. 512 frame, as cp_lime (GPT 2.5 2K, 4 px grid).
r1 (night 6 Nov, cp track): a willow's outline, not a keyhole: a domed top that widens into a curtain flaring out to
its full width at the bottom (a fountain), a ragged hem of strand tips, a short trunk that forks low (2.6 m) into
three heavy limbs arching up and out, instead of a 6.5 m pole with a straight-sided box hung under an egg."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, LIMB, CROWN = (95, 95, 100, 255), (125, 125, 130, 255), (180, 180, 185, 255)
cx = 300
t0, t1 = cx - 9, cx + 8
cl, cr = cx - 161, cx + 160
hang = G - 55                    # the lowest strands
fork = G - 120                   # the trunk forks at 2.6 m
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([cl + 20, -200, cr - 20, G - 200], fill=f(CROWN))                 # the dome, its top above the frame
    D.polygon([(cl + 20, 53), (cr - 20, 53), (cr, hang - 14), (cl, hang - 14)], fill=f(CROWN))  # from the dome's widest row the curtain flares out
    for i, x in enumerate(range(cl, cr - 5, 12)):                                # a ragged hem: strand tips of uneven lengths
        D.rectangle([x, hang - 16, min(x + 11, cr), hang - (0, 7, 3, 11, 1, 5)[i % 6]], fill=f(CROWN))
    D.rectangle([t0, fork - 30, t1, G - 1], fill=f(TRUNK))                      # a short trunk
    D.polygon([(t0 - 6, G - 1), (t0, G - 16), (t1, G - 16), (t1 + 6, G - 1)], fill=f(TRUNK))
    D.line([(cx - 4, fork), (cx - 70, fork - 110), (cx - 105, fork - 200)], fill=f(LIMB), width=9, joint='curve')
    D.line([(cx + 4, fork - 6), (cx + 66, fork - 115), (cx + 98, fork - 210)], fill=f(LIMB), width=8, joint='curve')
    D.line([(cx, fork - 20), (cx + 6, fork - 150), (cx - 4, fork - 260)], fill=f(LIMB), width=7, joint='curve')
save('cp_willow', c, m, {'ground': G, 'pepper_x': 4, 'trunk_x': [t0, t1], 'crown_x': [cl, cr], 'hang': hang,
                         'fork': fork, 'note': 'crown runs out of the top edge; the curtain flares to full width and hangs to 55 px above the ground'})
