"""City Park mid trees (mid layer, 23 px/m, half speed). Owner's pick 26 Oct (plan decision 2b): young 6 m trees,
138 px tall, the far city above them; new art so they stop repeating the high road's canopies. Three different young
trees in one frame (a lime, a maple, a slim birch), each with its whole crown, standing on the frame's ground line. 1K, 256 frame."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 256, 256
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
TRUNK, CROWN = (95, 95, 100, 255), (180, 180, 185, 255)
trees = [(100, 80, 92), (178, 70, 84), (240, 26, 100)]   # centre x, crown width, crown height: a lime, a maple, a slim birch
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    for cx, cw, ch in trees:
        top = G - 138
        D.ellipse([cx - cw // 2, top, cx + cw // 2 - 1, top + ch], fill=f(CROWN))
        D.rectangle([cx - 3, top + ch - 14, cx + 2, G - 1], fill=f(TRUNK))     # 6 px trunk (0.25 m)
save('cp_midtrees', c, m, {'ground': G, 'pepper_x': 4, 'trees': trees, 'note': 'two young trees, 138 px tall'})
