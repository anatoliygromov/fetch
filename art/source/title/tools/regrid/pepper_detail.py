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
    # two short 1 px lashes rising from the top of the arc's right end (2 to 3 cells each)
    dict(name='lash_a', pts=[(619, 889), (614, 880), (610, 873)]),
    dict(name='lash_b', pts=[(641, 892), (646, 881), (651, 870)]),
    # the wink's arc: one smooth curve of constant 2 px weight (centreline from the
    # column centroids of the painted arc, x 490-640)
    dict(name='wink', thick=3, pts=[(490, 954), (508, 943), (528, 928), (550, 914), (574, 906), (600, 903), (622, 904), (642, 909)]),
    # the knot's crease between the left tail and the knot body (darkest pink #751249)
    dict(name='knot_crease', colour=58, layer=2, pts=[(352, 1262), (358, 1280), (372, 1291), (390, 1295), (404, 1306)]),
    # brow arc over the open eye (black blocks x 792-798 y 740-748 up to x 836-852 y 706-716)
    dict(name='brow', thick=2, pts=[(797, 750), (801, 736), (808, 725), (819, 716), (833, 712), (847, 713), (858, 717)]),
]
CLEAR_BOXES = [
    (575, 848, 680, 896),     # the lash area above the wink's thick arc
    (470, 890, 660, 966),     # the wink's arc
    (786, 702, 858, 754),     # the brow arc
]
# the knot's tip: inside this box the dog mask is limited to the bandana plus one
# painted outline block, so the dark lamp post behind the tip is not taken as Pepper
KNOT_BOX = (230, 1230, 330, 1430)
KNOT_OUTLINE_PX = 9


def clear_mask(shape, box0, LN=None, radius=13):
    """near the traced strokes only (within `radius` px of a stroke), inside the boxes."""
    import cv2
    m = np.zeros(shape, bool)
    for x0, y0, x1, y1 in CLEAR_BOXES:
        m[max(0, y0 - box0[1]):y1 - box0[1], max(0, x0 - box0[0]):x1 - box0[0]] = True
    near = np.zeros(shape, np.uint8)
    for st in STROKES:
        q = np.array(st['pts'], float) - [box0[0], box0[1]]
        cv2.polylines(near, [np.round(q).astype(np.int32).reshape(-1, 1, 2)], False, 1, 2 * radius + 1)
    return m & near.astype(bool)


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


# the open eye's cream cells (output cell (j, i)): the catchlight (2 x 3 with the
# top-left corner cut, as painted) and the sclera crescent stepping evenly down-left
EYE_CREAM = [(105, 113), (105, 114), (106, 112), (106, 113), (106, 114), (107, 112), (107, 113), (107, 114),
             (109, 117), (109, 118), (110, 117), (110, 118), (111, 117), (111, 118), (112, 117), (112, 118),
             (113, 117), (113, 118), (114, 116), (114, 117), (115, 115), (115, 116), (116, 114), (116, 115)]


# the left ear's tone ramp, dark to light (palette ids): its shading is rebuilt as
# ordered bands, plain tone, 50 % checker on one global 2 x 2 lattice, next tone
EAR_RAMP = [2, 1, 0, 11, 7, 10]
