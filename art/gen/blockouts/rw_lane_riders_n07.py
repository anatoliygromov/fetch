"""The road's bike-lane riders at the lane's 55 px/m (road.lua: top row at y 190, only rows 0-49 show: helmet, head,
body, arms, hands). The same people as the promenade riders A and B (rw_riders_n07.py), 1.85 m with the helmet = 102
px, the same bike geometry scaled by 55/46 (wheels 37 px, hubs 61 apart). Both face RIGHT."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
G = 220
c, d, m, dm, _ = frame(256, 256, ground=G, pepper_x=6)
src = open('art/gen/blockouts/rw_riders_n07.py').read().split('for D, f in')[0].replace("c, d, m, dm, _ = frame(256, 256, ground=G, pepper_x=6)", "")
ns = {}; exec(src.replace("G = 200", f"G = {G}"), ns)
S = 55 / 46
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    ns['rider'](D, f, 52, 'A', s=S); ns['rider'](D, f, 140, 'B', s=S)
save('rw_lane_riders_n07', c, m, {'ground': G, 'pepper_x': 6, 'scale': S, 'riders': {'A': [52, 'right'], 'B': [140, 'right']}})
