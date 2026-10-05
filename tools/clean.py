import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Cleanup pass for Pepper frames: palette snap, detached-speck removal, eye normalisation.
import numpy as np
from scipy import ndimage as nd
PAL = np.array([
    (1, 1, 2), (23, 24, 31), (57, 56, 71), (93, 99, 111), (112, 132, 156),   # outline, shadow, body, mid, highlight
    (247, 249, 250),                                                          # eye
    (250, 100, 200), (196, 60, 150), (155, 46, 118),                          # bandana light, mid, dark
    (206, 53, 49)], dtype=int)                                                # the red ball, same red as art/ball.png
OUTLINE, SHADOW, BODY, MID, HI, EYE, PK1, PK2, PK3, RED = range(10)
LIGHT = {MID, HI, EYE, PK1, PK2, PK3}

def snap(f):
    """returns index map (-1 = transparent) after snapping every opaque pixel to the palette"""
    al = f[..., 3] >= 128
    rgb = f[..., :3].astype(int)
    d = ((rgb[..., None, :] - PAL[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    idx[~al] = -1
    return idx

def despeck(idx, keep_min=13, log=None):
    lab, k = nd.label(idx >= 0, structure=np.ones((3, 3)))
    if k <= 1: return idx
    sizes = nd.sum(idx >= 0, lab, range(1, k + 1))
    big = int(np.argmax(sizes)) + 1
    for i, s in enumerate(sizes, 1):
        if i != big and s < keep_min:
            idx[lab == i] = -1
            if log is not None: log.append(int(s))
    return idx

def eye_candidates(idx):
    op = idx >= 0
    ys, xs = np.nonzero(op)
    front = xs.max()
    cols = xs >= front - 14
    top = ys[cols].min()
    out = []
    H, W = idx.shape
    for y in range(top, min(H - 1, top + 8)):
        for x in range(max(1, front - 14), min(W - 1, front)):
            v = idx[y, x]
            if v < 0 or v not in LIGHT: continue
            nb = idx[y - 1:y + 2, x - 1:x + 2]
            if (nb < 0).any(): continue                       # on the silhouette edge: not an eye
            others = [int(n) for n in nb.flatten()]
            others.remove(int(v))
            if any(o in LIGHT for o in others): continue      # part of a highlight strip or the bandana
            out.append((x, y))
    return out

def fix_eye(idx, at=None):
    """normalise the eye to the white eye colour; at=(x,y) forces a position"""
    if at is not None:
        idx[at[1], at[0]] = EYE; return idx, [at]
    c = eye_candidates(idx)
    if len(c) == 1:
        x, y = c[0]; idx[y, x] = EYE
    return idx, c

def to_rgba(idx):
    out = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    out[m, :3] = PAL[idx[m]]; out[m, 3] = 255
    return out

def head_mask(idx, ox, oy, w=16, h=14):
    m = np.zeros((h, w), bool)
    H, W = idx.shape
    for y in range(h):
        for x in range(w):
            yy, xx = oy + y, ox + x
            if 0 <= yy < H and 0 <= xx < W: m[y, x] = idx[yy, xx] >= 0
    return m

def place_eye_like(idx, ref, ref_eye, search=5):
    """find the shift that best overlays ref's head on idx's head, put the eye at ref_eye + shift"""
    ex, ey = ref_eye
    ox, oy = ex - 9, ey - 6
    rm = head_mask(ref, ox, oy)
    best = None
    for dy in range(-search, search + 1):
        for dx in range(-search, search + 1):
            m = head_mask(idx, ox + dx, oy + dy)
            score = (m == rm).mean()
            if best is None or score > best[0]: best = (score, dx, dy)
    s, dx, dy = best
    x, y = ex + dx, ey + dy
    if idx[y, x] in (SHADOW, BODY, OUTLINE) and (idx[y-1:y+2, x-1:x+2] >= 0).all():
        idx[y, x] = EYE
        return idx, (x, y), s
    return idx, None, s

def clean_row(frames, no_eye=(), force_eye=None, keep_min=13):
    """frames: list of RGBA arrays of one animation. no_eye: frame numbers (1-based) left without an eye (blinks).
    force_eye: {frame: (x, y)}. Returns cleaned RGBA frames and a report."""
    force_eye = force_eye or {}
    idxs, eyes, rep = [], [], []
    for i, f in enumerate(frames, 1):
        log = []
        idx = despeck(snap(f), keep_min=keep_min, log=log)
        if i in force_eye: idx, c = fix_eye(idx, force_eye[i])
        elif i in no_eye: c = []
        else: idx, c = fix_eye(idx)
        eyes.append(c[0] if len(c) == 1 else None)
        idxs.append(idx); rep.append((i, eyes[-1], log))
    for i, idx in enumerate(idxs):                       # frames with no eye found: copy from the nearest frame that has one
        if eyes[i] is None and (i + 1) not in no_eye:
            order = sorted([j for j in range(len(idxs)) if eyes[j] is not None], key=lambda j: abs(j - i))
            if order:
                j = order[0]
                idxs[i], pos, s = place_eye_like(idx, idxs[j], eyes[j])
                rep[i] = (i + 1, ('copied', pos, round(s, 2)), rep[i][2])
    return [to_rgba(x) for x in idxs], rep

# ---- outline (stroke) and generic palette helpers ----
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
def add_outline(idx, out_i, dark):
    """draw a 1 px stroke outside the silhouette wherever the edge pixel is not already dark"""
    H, W = idx.shape
    new = idx.copy()
    for y in range(H):
        for x in range(W):
            if idx[y, x] >= 0: continue
            for dy, dx in N4:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and idx[yy, xx] >= 0 and idx[yy, xx] not in dark:
                    new[y, x] = out_i; break
    return new

def snap_to(f, pal):
    al = f[..., 3] >= 128
    d = ((f[..., :3].astype(int)[..., None, :] - pal[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1); idx[~al] = -1
    return idx

def rgba_from(idx, pal):
    out = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    out[m, :3] = pal[idx[m]]; out[m, 3] = 255
    return out

def lone_pixels(idx, skip):
    """recolour single interior pixels whose colour none of the 8 neighbours share (noise), except 'skip' colours"""
    H, W = idx.shape; out = idx.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            v = idx[y, x]
            if v < 0 or v in skip: continue
            nb = idx[y - 1:y + 2, x - 1:x + 2].flatten().tolist(); nb.pop(4)
            if -1 in nb or v in nb: continue
            out[y, x] = max(set(nb), key=nb.count)
    return out

def clean_pepper_row(frames, no_eye=(), force_eye=None):
    cl, rep = clean_row(frames, no_eye=no_eye, force_eye=force_eye)
    res = []
    for f in cl:
        idx = snap(f)
        idx = lone_pixels(idx, skip={EYE, PK1, PK2, PK3, OUTLINE, RED})
        idx = add_outline(idx, OUTLINE, dark={OUTLINE, SHADOW})
        res.append(to_rgba(idx))
    return res, rep

def girl_palette():
    from PIL import Image
    s = np.array(Image.open(os.path.join(ROOT,'source_sheets','girl_side_idle.png')).convert('RGBA'))
    cols = sorted(set(map(tuple, s[s[..., 3] >= 128][:, :3].tolist())))
    return np.array(cols, int)

def clean_girl_row(frames, pal):
    lum = pal @ np.array([0.3, 0.59, 0.11])
    dark = set(np.nonzero(lum < 40)[0].tolist())
    out_i = int(np.argmin(lum))
    res = []
    for f in frames:
        idx = despeck(snap_to(f, pal))
        idx = add_outline(idx, out_i, dark)
        res.append(rgba_from(idx, pal))
    return res
