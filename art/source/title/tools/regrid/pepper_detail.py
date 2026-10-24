"""PEPPER track, round 2: hand-traced details (unfake.js's manual cleanup step, as data).

Some painted details are thinner than an output cell and near-black, so the automatic
line pass cannot tell them from fur specks: the wink's three lashes and the brow arc
over the open eye. Their centrelines were traced by eye from the painting at 4x to 10x
(painting pixel coordinates, see the ASCII dumps in out/notes.md) and are drawn as
1 px pixel-perfect lines. Inside each clear box the near-black pixels they replace are
taken out of the fill, so no dark blob remains around them.
"""
import numpy as np
from scipy import ndimage as ndi

STROKES = [
    # wink lashes, from tip to the wink's end (blocks at x 588-600 y 854-862 -> 620-640 y 884-890 etc.)
    dict(name='lash_left', pts=[(594, 858), (611, 868), (626, 878), (634, 888)]),
    dict(name='lash_mid', pts=[(650, 857), (644, 868), (639, 879)]),
    dict(name='lash_right', pts=[(662, 877), (652, 887), (646, 896)]),
    # brow arc over the open eye (black blocks x 792-798 y 740-748 up to x 836-852 y 706-716)
    dict(name='brow', thick=2, pts=[(797, 750), (801, 736), (808, 725), (819, 716), (833, 712), (847, 713), (858, 717)]),
]
CLEAR_BOXES = [
    (580, 848, 672, 892),     # the lash area above the wink's thick arc
    (786, 702, 858, 754),     # the brow arc
]
# the knot's tip: inside this box the dog mask is limited to the bandana plus one
# painted outline block, so the dark lamp post behind the tip is not taken as Pepper
KNOT_BOX = (230, 1230, 330, 1430)
KNOT_OUTLINE_PX = 9


def clear_mask(shape, box0):
    m = np.zeros(shape, bool)
    for x0, y0, x1, y1 in CLEAR_BOXES:
        m[max(0, y0 - box0[1]):y1 - box0[1], max(0, x0 - box0[0]):x1 - box0[0]] = True
    return m


def trim_knot(D, B, box0):
    x0, y0, x1, y1 = KNOT_BOX
    sl = (slice(max(0, y0 - box0[1]), y1 - box0[1]), slice(max(0, x0 - box0[0]), x1 - box0[0]))
    r = KNOT_OUTLINE_PX
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    near_b = ndi.binary_dilation(B, (xx * xx + yy * yy) <= r * r)
    out = D.copy()
    out[sl] &= near_b[sl]
    lab, n = ndi.label(out)
    if n > 1:
        sz = ndi.sum(out, lab, range(1, n + 1))
        out = lab == (np.argmax(sz) + 1)
    return out
