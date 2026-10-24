"""PEPPER track, QA: comparison images and gates."""
import numpy as np, os
from PIL import Image
from scipy import ndimage as ndi
import pepper_seg as S
import lines as LN
from common import SRC, srgb_to_lab, luma

NX, NY = 320, 240
CW, CH = S.CW, S.CH
_SRC = None


def src():
    global _SRC
    if _SRC is None:
        _SRC = np.array(Image.open(SRC).convert('RGB'))
    return _SRC


def compare(rgb, alpha, box, scale=10, path=None, bg=(255, 0, 255)):
    """box in cells (i0, j0, i1, j1): original | result, both at `scale` px per cell."""
    i0, j0, i1, j1 = box
    a = src()
    crop = Image.fromarray(a[int(round(j0 * CH)):int(round(j1 * CH)), int(round(i0 * CW)):int(round(i1 * CW))])
    w, h = (i1 - i0) * scale, (j1 - j0) * scale
    left = np.array(crop.resize((w, h), Image.LANCZOS))
    r = rgb[j0:j1, i0:i1].copy()
    r[~alpha[j0:j1, i0:i1]] = bg
    right = np.array(Image.fromarray(r).resize((w, h), Image.NEAREST))
    gap = np.full((h, 6, 3), 255, np.uint8)
    im = Image.fromarray(np.hstack([left, gap, right]))
    if path:
        im.save(path)
    return im


def orig_cells():
    """the painting box-averaged per output cell (uniform grid)."""
    a = src().astype(np.float64)
    xs = np.floor((np.arange(2400) + 0.5) / CW).astype(int)
    ys = np.floor((np.arange(1792) + 0.5) / CH).astype(int)
    idx = (ys[:, None] * NX + xs[None, :]).ravel()
    out = np.zeros((NY * NX, 3))
    n = np.bincount(idx, minlength=NX * NY)
    for c in range(3):
        out[:, c] = np.bincount(idx, weights=a[..., c].ravel(), minlength=NX * NY) / n
    return out.reshape(NY, NX, 3)


def orig_cells_excluding(owned_full):
    """per cell mean luma of the painting pixels NOT in owned_full (2400 x 1792 bool):
    what the neighbouring track shows in a cell this track does not take."""
    a = luma(src().astype(np.float64))
    xs = np.floor((np.arange(2400) + 0.5) / CW).astype(int)
    ys = np.floor((np.arange(1792) + 0.5) / CH).astype(int)
    idx = (ys[:, None] * NX + xs[None, :]).ravel()
    w = (~owned_full).ravel().astype(np.float64)
    s = np.bincount(idx, weights=a.ravel() * w, minlength=NX * NY)
    n = np.bincount(idx, weights=w, minlength=NX * NY)
    with np.errstate(invalid='ignore'):
        return (s / n).reshape(NY, NX)


def form_gate(rgb, alpha, owned_full=None):
    o = luma(orig_cells())
    r = luma(rgb.astype(np.float64))
    # cells this track does not take show what the neighbouring material shows there
    # (the painting without this track's pixels), so both sides of the region edge are
    # treated alike
    if owned_full is not None:
        ox = orig_cells_excluding(owned_full)
        r = np.where(alpha, r, np.where(np.isnan(ox), o, ox))
    else:
        r = np.where(alpha, r, o)
    bo = ndi.uniform_filter(o, 5, mode='nearest'); br = ndi.uniform_filter(r, 5, mode='nearest')
    d = np.abs(bo - br)[alpha]
    return float(d.mean()), float(np.percentile(d, 95)), np.abs(bo - br) * alpha


def mixels(rgb, alpha, edge_de=20.0, tol=6.0, diff=3.0, dots_only=False):
    """A pixel whose colour lies between its two opposite neighbours' colours (both
    differing from it by more than `diff` dE) along a strong edge (the neighbours
    differ by more than edge_de). dots_only: count only anti-aliasing dots, i.e. such
    pixels whose colour does not continue along the edge (neither neighbour across
    the a-b axis has the same colour); a 1 px ramp band is then not a mixel."""
    lab = srgb_to_lab(rgb)
    bad = np.zeros(alpha.shape, bool)
    same = lambda dy, dx: (np.roll(rgb, (dy, dx), (0, 1)) == rgb).all(-1)
    for dy, dx in ((0, 1), (1, 0)):
        a = np.roll(lab, (dy, dx), (0, 1)); b = np.roll(lab, (-dy, -dx), (0, 1))
        aa = np.roll(alpha, (dy, dx), (0, 1)) & np.roll(alpha, (-dy, -dx), (0, 1)) & alpha
        ab = np.linalg.norm(a - b, axis=-1)
        pa = np.linalg.norm(lab - a, axis=-1); pb = np.linalg.norm(lab - b, axis=-1)
        between = (pa + pb) <= ab + tol
        m = aa & (ab > edge_de) & between & (pa > diff) & (pb > diff)
        if dots_only:
            m &= ~same(dx, dy) & ~same(-dx, -dy)
        bad |= m
    bad[0] = bad[-1] = False; bad[:, 0] = bad[:, -1] = False
    return bad


def lcorner_count(line):
    m = line.astype(bool)
    n8 = sum(LN.nb(m, dy, dx).astype(int) for dy, dx in LN.N8)
    c = np.zeros_like(m)
    for (hy, hx) in [(0, 1), (0, -1)]:
        for (vy, vx) in [(1, 0), (-1, 0)]:
            c |= m & LN.nb(m, hy, hx) & LN.nb(m, vy, vx) & ~LN.nb(m, vy + hy, vx + hx) & (n8 == 2)
    return c


def line_gaps(line, info):
    """endpoints of the rasterized line that are not endpoints of a painted line:
    an 8-connected component count compared with the traced polylines."""
    m = line.astype(bool)
    n8 = sum(LN.nb(m, dy, dx).astype(int) for dy, dx in LN.N8)
    ends = m & (n8 == 1)
    iso = m & (n8 == 0)
    return ends, iso


def upscale_mask(m):
    """output cell mask -> painting resolution."""
    xs = np.floor((np.arange(2400) + 0.5) / CW).astype(int)
    ys = np.floor((np.arange(1792) + 0.5) / CH).astype(int)
    return m[ys][:, xs]


def iou_bd(pm, om):
    """pm painting mask, om output-upscaled mask (same shape). IoU and mean
    symmetric boundary distance in painting px."""
    inter = (pm & om).sum(); uni = (pm | om).sum()
    iou = inter / max(uni, 1)
    bp = pm & ~ndi.binary_erosion(pm); bo = om & ~ndi.binary_erosion(om)
    if not bp.any() or not bo.any():
        return iou, np.inf
    dto = ndi.distance_transform_edt(~bo); dtp = ndi.distance_transform_edt(~bp)
    bd = 0.5 * (dto[bp].mean() + dtp[bo].mean())
    return iou, bd
