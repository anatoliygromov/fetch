"""Pepper's head finished after the cleanup (cleanup.py), by rule and by hand:
  - her eye and nose stay the painting's own pixels (their catchlights, the nose's blue sheen and its brown glint
    are deliberate shapes the cleanup would lose)
  - the dark lines (the wink, the mouth line, the ear edges, the outline: her darkest colour) are made continuous:
    a 1 px gap between two line pixels (left-right, up-down or diagonal) is closed
  - HAND: pixel lists below, game coordinates, (x, y, source) where source is a colour name"""
import numpy as np

def lines_closed(img, mask, ink):
    """1 px gaps in the darkest lines inside mask closed (a pixel between two ink pixels on opposite sides)"""
    out = img.copy(); H, W, _ = img.shape
    isink = (img == ink).all(-1)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not mask[y, x] or isink[y, x]: continue
            for (a, b) in (((0, -1), (0, 1)), ((-1, 0), (1, 0)), ((-1, -1), (1, 1)), ((-1, 1), (1, -1))):
                if isink[y + a[0], x + a[1]] and isink[y + b[0], x + b[1]]:
                    # only where the gap breaks a line: the two other neighbours across it are not ink
                    o1 = (y + a[1], x - a[0]); o2 = (y - a[1], x + a[0])
                    if not isink[o1] and not isink[o2]: out[y, x] = ink; break
    return out

# HAND: the wink redrawn as one clean lid stroke rising to the right, thick in the middle, thin at the ends, with three
# short lashes (it was a 3-row blob after the cleanup). Rows: (y, x0, x1) inclusive, in her darkest colour.
WINK_CLEAR = (66, 113, 91, 123)          # x0, y0, x1, y1 exclusive: the old ink here becomes her fur
WINK = [(122, 67, 70), (121, 69, 78), (120, 76, 84), (119, 82, 87), (118, 86, 88)]
LASHES = [(80, 119), (79, 118), (79, 117), (84, 118), (84, 117), (85, 116), (88, 117), (89, 116)]

def hand(out, ink, fur):
    x0, y0, x1, y1 = WINK_CLEAR
    reg = out[y0:y1, x0:x1]; m = (reg == ink).all(-1); reg[m] = fur
    for y, a, b in WINK: out[y, a:b + 1] = ink
    for x, y in LASHES: out[y, x] = ink
    return out

def finish(clean, painting, mats):
    out = clean.copy()
    keep = mats['eye'] | mats['nose']
    out[keep] = painting[keep]
    pep = mats['coat'] | mats['nose'] | mats['eye'] | mats['tongue'] | mats['bandana']
    vals, cnt = np.unique(out[mats['coat']], axis=0, return_counts=True)
    lum = vals.sum(1); ink = vals[np.argmin(lum)]
    out = lines_closed(out, mats['coat'], ink)
    vc = [tuple(v) for v in vals]; fur = vals[np.argmax(cnt)]       # her commonest coat colour
    out = hand(out, ink, fur)
    return out
