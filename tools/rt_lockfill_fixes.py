#!/usr/bin/env python3
"""rt_lockfill_fixes.py DIR: the hand pass for the Rooftops lock-and-complete pilot (8 Nov), written as explicit,
repeatable edits. Only pixels inside the holes change (the lock stays). Window lower halves hidden by the concept's
tile piles come from the window on the same storey (measured left edges 34, 77, 163, 205, 248, 291: spacing 42-43),
the bare wall between them continues its row, and the ledges' left corners are mirrors of the visible right corner."""
import sys, numpy as np
from PIL import Image
D = sys.argv[1]
cut = np.asarray(Image.open(f'{D}/cut.png').convert('RGB')); out = np.asarray(Image.open(f'{D}/filled.png').convert('RGB')).copy()
holes = np.load(f'{D}/holes.npy'); orig = ~holes
WIN = {77: 34, 205: 163, 248: 163}                   # hidden window (left edge) <- clean window on the same storey
WW = 22
edits = 0
for (x0, x1) in ((54, 101), (213, 264)):             # the two tile-pile zones, wall rows above the ledge line
    for y in range(110, 139):                        # down to the skylight frame line (y 139)
        for x in range(x0, x1):
            if not holes[y, x]: continue
            src = None
            for wx, sx in WIN.items():
                if wx <= x < wx + WW: src = (y, x - wx + sx)
            if src is None:                          # bare wall: nearest original pixel of this row outside windows
                cand = [j for j in range(320) if orig[y, j] and not any(w <= j < w + WW for w in (0, 34, 77, 120, 163, 205, 248, 291))]
                j = min(cand, key=lambda j: abs(j - x)); src = (y, j)
            out[y, x] = cut[src]; edits += 1
for (lx, rx) in ((96, 159), (256, 159)):             # ledge left corners <- mirror of the right corner of the ledge at 96-160
    for y in range(134, 146):
        for d in range(0, 8):
            x = lx + d
            if x < 320 and holes[y, x] and orig[y, rx - d]:
                out[y, x] = cut[y, rx - d]; edits += 1
# (review fix, 8 Nov 11:20) the right skylight's top-left corner: Pepper's feet hid it; it is the left skylight's
# left end moved one skylight right (x <- x - 160), the ledge's end (x < 160) left as it is
for y in range(134, 148):
    for x in range(160, 178):
        if holes[y, x] and orig[y, x - 160]: out[y, x] = cut[y, x - 160]; edits += 1
# skylight right ends and the ledge corner beside them (the whole tile-pile zone): the right skylight (160-256) sits
# halfway between the ledges (centre 208), so its hidden right end is the mirror of its visible left end (x <- 416 - x);
# the left skylight's right end is the same mirror moved one skylight left (x <- 256 - x). Sources are read after the
# corner fix above.
src = out.copy()
for (z0, z1, m) in ((54, 101, 256), (214, 262, 416)):
    for y in range(139, 179):
        for x in range(z0, z1):
            sx = m - x
            if holes[y, x] and 0 <= sx < 320: out[y, x] = src[y, sx]; edits += 1
# the wall rows between the window bottoms and the skylight frame (y 136-138) over both dips: plain wall from the
# nearest original pixel of the row inside the same dip (the windows get their sills in rt_windows_palette.py)
for (d0, d1) in ((0, 96), (160, 256)):
    for y in (136, 137, 138):
        for x in range(d0, d1):
            if holes[y, x]:
                row = [j for j in range(d0, d1) if orig[y, j]]
                if row: out[y, x] = cut[y, min(row, key=lambda j: abs(j - x))]; edits += 1
# the bare wall under the coping (y 97-111): filled pixels take the nearest original pixel of the row that is plain
# wall (close to the row's median), so no wall mark (anchor tick) is copied into the fills
lumc = cut.astype(float) @ np.array([.299, .587, .114])
for y in range(97, 112):
    med = np.median(lumc[y][orig[y]]) if orig[y].any() else 0
    plain = [j for j in range(320) if orig[y, j] and abs(lumc[y, j] - med) < 12]
    for x in range(320):
        if holes[y, x] and plain:
            j = min(plain, key=lambda j: abs(j - x))
            if abs(j - x) < 60: out[y, x] = cut[y, j]; edits += 1
assert (out[orig] == cut[orig]).all(); print(f'LOCK OK; hand-pass edits {edits} px')
Image.fromarray(out).save(f'{D}/filled.png')
