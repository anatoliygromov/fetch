"""City Park leaf piles (play line, decoration drawn over Pepper, 46 px/m). Two slots from one render so the pair
match: riverwalk/art/scene/park_leaves.png (the heap, 48 x 22, 0.48 m, the LEAVES boxes at x 92, 1008, 1516, 44-48 x
12, bottom on the path y 328) and park_leaves_flat.png (the same leaves after Pepper ran through: spread low, 54 x 9).
Both are centred on the box and stand on the path. Frame 256 x 256, Pepper at 1x on the same ground line."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=240, pepper_x=8)
LEAF = (170, 140, 120, 255)
HX, FX = 100, 176                       # the heap's and the flat spread's left edges
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.ellipse([HX, G - 22, HX + 47, G + 16], fill=f(LEAF))               # the heap: a low dome, 48 x 22
    D.rectangle([HX, G - 4, HX + 47, G - 1], fill=f(LEAF))
    D.ellipse([FX, G - 9, FX + 53, G + 6], fill=f(LEAF))                 # the flat spread: 54 x 9
    D.rectangle([FX, G - 3, FX + 53, G - 1], fill=f(LEAF))
# the mask keeps only the frame's rows above the ground
m.paste(0, (0, G, 256, 256)); c.paste((255, 0, 255, 255), (HX, G, 256, 256))
save('cp_leaves', c, m, {'heap': [HX, G - 22, 48, 22], 'flat': [FX, G - 9, 54, 9], 'ground': G})
