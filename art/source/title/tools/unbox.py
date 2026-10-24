"""Takes the painting's PRESS ANY KEY TO START box out (x 154-273, y 190-204 on the game grid) and rebuilds the
railing behind it from the painting's own rows: the bars over the water (rows 186-189) carry on down, the lower
rail is the top rail's rows (184-185), the hedge at the railing's foot and the kerb come from the open stretch left
of the box (x 141-153), the first pavement rows from the pavement just under the box. Whole pixels copied, nothing
drawn new. Works on palette indices (H x W)."""
import numpy as np
X0, X1, Y0, Y1 = 154, 274, 190, 205        # the box: x X0..X1-1, y Y0..Y1-1
HEDGE = 174                                # left of this the railing has the hedge behind it, right of it the water

def unbox(idx, lum):
    o = idx.copy()
    cols = range(X0, X1)
    bars = {x: (lum[186:190, x] <= 50).sum() >= 3 for x in cols}       # a bar or a post: dark all the way down
    lx0, lx1 = 141, 154                                                 # the open stretch left of the box
    for x in cols:
        lt = lx0 + (x - X0) % (lx1 - lx0)
        for y in range(190, 197):
            o[y, x] = idx[186 + (y - 190) % 4, x]
            if x < HEDGE and not bars[x]:                               # the hedge behind the bars, from the left
                t = lt if lum[y, lt] > 32 else (lt + 1 if lt + 1 < lx1 else lt - 1)
                o[y, x] = idx[y, t]
        o[197, x], o[198, x] = idx[184, x], idx[185, x]
        for y in (199, 200, 201):
            o[y, x] = idx[186 + (y - 199), x] if bars[x] else idx[y, lt]
            if not bars[x] and lum[y, lt] <= 32: o[y, x] = idx[y, lt + 1 if lt + 1 < lx1 else lt - 1]   # (no stray bar from the tile)
        o[202, x] = idx[202, lt]
        o[203, x], o[204, x] = idx[206, x], idx[207, x]
    # the rails are dark iron: light specks on them (flowers showing through, in the painting's rows 184-185 and so
    # in their copy at 197-198) take the rail colour beside them
    for y in (184, 185, 197, 198):
        for x in range(X0, HEDGE):
            ys = y if y < 197 else y - 13                               # the painting's row it shows
            if lum[ys, x] > 140:
                k = x - 1
                while k > X0 - 20 and lum[ys, k] > 140: k -= 1
                o[y, x] = o[y, k]
    return o
