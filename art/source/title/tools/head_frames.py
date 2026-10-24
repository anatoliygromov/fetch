"""Pepper's head frames for the title loop, from the owner's Artlist videos (art/source/title/video).
Each video frame is registered to the still on her head (register.py) and sampled onto the game grid (vsample.py).
A pose changes the still only where the video changes: the pose frame is compared with the same video's neutral
frame (the one that matches the still: tongue out, left eye winking), in Lab; pixels inside the pose's region that
moved more than THR become the mask; the mask is opened (no lone pixels) and closed (no pinholes); inside it the
pose's pixels in the title palette, outside it the still, untouched. So between frames only her mouth or her eye
changes and nothing else shimmers."""
import numpy as np
from scipy import ndimage
from skimage.color import rgb2lab

def compose(still_idx, pal, pose_rgb, neutral_rgb, region, thr=14.0, nearest=None):
    """still_idx: H x W palette indices of the still crop; pose / neutral: H x W x 3 video samples of the same crop;
    region: (x0, y0, x1, y1) in the crop. Returns the frame's indices and the mask."""
    lp, ln = rgb2lab(pose_rgb / 255.0), rgb2lab(neutral_rgb / 255.0)
    d = np.sqrt(((lp - ln) ** 2).sum(-1))
    x0, y0, x1, y1 = region
    reg = np.zeros(d.shape, bool); reg[y0:y1, x0:x1] = True
    m = (d > thr) & reg
    m = ndimage.binary_opening(m, structure=np.ones((2, 2)))
    m = ndimage.binary_closing(m, structure=np.ones((3, 3))) & reg
    m = ndimage.binary_fill_holes(m)
    pi = nearest(pose_rgb.astype(float), pal)
    out = still_idx.copy(); out[m] = pi[m]
    return out, m

def majority_clean(idx, mask, passes=2):
    """inside the mask, a pixel none of whose 4 neighbours share its colour takes the colour most of its 8 share"""
    H, W = idx.shape
    for _ in range(passes):
        o = idx.copy()
        for y, x in zip(*np.nonzero(mask)):
            c = idx[y, x]
            n4 = [idx[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < H and 0 <= xx < W]
            if c in n4: continue
            n8 = idx[max(0, y - 1):y + 2, max(0, x - 1):x + 2].ravel(); n8 = n8[n8 != c]
            v, k = np.unique(n8, return_counts=True); o[y, x] = v[k.argmax()]
        idx = o
    return idx

# ---- the pant: the tongue's outline from the video, its pixels from the still --------------------------------------
from skimage.color import rgb2lab as _lab
TONGUE_BOX = (62, 55, 125, 97)          # (in the head crop) where the tongue can be

def tongue_mask(rgb):
    lab = _lab(rgb / 255.0); m = (lab[..., 1] > 18) & (lab[..., 0] > 30)
    x0, y0, x1, y1 = TONGUE_BOX; r = np.zeros(m.shape, bool); r[y0:y1, x0:x1] = True; m &= r
    lb, n = ndimage.label(m)
    if n == 0: return m
    sz = ndimage.sum(m, lb, range(1, n + 1)); m = lb == (1 + np.argmax(sz))
    m = ndimage.binary_closing(m, structure=np.ones((3, 3))) | m
    return ndimage.binary_fill_holes(ndimage.binary_opening(m, structure=np.ones((2, 2))))

def pant(still_idx, still_rgb, pose_rgb):
    """the still's tongue stretched to the pose's tongue outline, column by column: each new tongue pixel takes the
    still's tongue pixel at the same place along its column (top to bottom, so the rim, the groove and the shine
    stay where they are on the tongue); a column the still has no tongue in copies the nearest column that has.
    Only pixels where the tongue grows change (the pant opens the tongue down; the dark mouth round it stays)."""
    T = tongue_mask(still_rgb); N = tongue_mask(pose_rgb) | T
    out = still_idx.copy()
    cols = [x for x in range(T.shape[1]) if T[:, x].any()]
    for x in range(N.shape[1]):
        ny = np.nonzero(N[:, x])[0]
        if len(ny) == 0: continue
        sx = x if T[:, x].any() else min(cols, key=lambda c: abs(c - x))
        ty = np.nonzero(T[:, sx])[0]
        t0, t1 = ty.min(), ty.max(); n0, n1 = ny.min(), ny.max()
        for y in ny:
            if T[y, x]: continue
            u = (y - n0) / max(1, n1 - n0); sy = int(round(t0 + u * (t1 - t0)))
            out[y, x] = still_idx[sy, sx]
    return out, N & ~T

# ---- the blink: drawn on the still's own pixels ----------------------------------------------------------------
def eye_span(L, y, x0=104, x1=122):
    """the open eye's span on row y: from its outline's first to last pixel (L < 4) between x0 and x1; above the
    outline (the lid's rim) the run of rim pixels (L 20-30) over the eye"""
    xs = [x for x in range(x0, x1) if L[y, x] < 4]
    if not xs and y < 100: xs = [x for x in range(108, 120) if 19 < L[y, x] < 31]
    return (min(xs), max(xs)) if xs else None

def blink(idx, L, rows, lid, ink, fur, rim=None, rimline=()):
    """closes the open eye: its rows (in game coordinates) filled flat with the fur colour `fur`, then the lid:
    `lid` = [(x, y), ...] in the darkest outline colour `ink`, and `rimline` (the lit edge of the lid) in `rim`"""
    out = idx.copy(); m = np.zeros(idx.shape, bool)
    for y in rows:
        sp = eye_span(L, y)
        if not sp: continue
        a, b = sp
        for _ in range(2):                                    # the eye's lighter rim beside the outline goes too
            if 19 < L[y, a - 1] < 31: a -= 1
            if 19 < L[y, b + 1] < 31: b += 1
        out[y, a:b + 1] = fur; m[y, a:b + 1] = True
    for x, y in rimline: out[y, x] = rim; m[y, x] = True
    for x, y in lid: out[y, x] = ink; m[y, x] = True
    return out, m
