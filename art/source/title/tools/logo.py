"""The FETCH! logo and the tagline plate rebuilt as UI layers on the grid (24 Oct, 0 credits).
The painting's letters have a dithered gradient fill and wobbly outlines, and its tagline is a smeared fake font. So:
  logo:    the silhouettes of F, E, T, C, H, ! (the warm pixels of each letter on the native grid) are fitted with
           polygons (cv2.approxPolyDP, 1.2 px) and filled again: straight runs, even staircase steps. Each letter
           gets the painting's 2 px dark navy outline and its 2 px drop downwards (the depth), letters stacked left
           to right as painted (each one's outline over the one before). Fill: a highlight row on the top edge, then
           three hard horizontal bands (yellow, gold, orange, by the letter's own height) and a red-orange lip on
           its bottom edge: the painting's own five warm colours, no dither. The paw (the !'s dot) is redrawn
           symmetric: four toes as mirrored ovals and a round pad, the same outline and bands.
  plate:   the tagline plate redrawn: navy fill, a 1 px light rim, a 1 px darkest-navy outline, corners cut 2-1,
           a little wider than the painting's so the v8 small font fits; the text centred, 1 px dark shadow.
           Two versions: THE CITY DOG ADVENTURER (the 7 px capitals) and The City Dog Adventurer (the same
           family with hand-drawn lowercase, x-height 5, descenders 2).
  patch:   the painting's old logo and plate are painted out of the base with the sky round them (each pixel the
           nearest untouched pixel on its row), so nothing of the old logo shows where the new one is slimmer.
"""
import os, sys
import numpy as np
import cv2
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'ui', 'v8', 'font'))
import style8 as S8, glyphs7

NAVY = (2, 17, 53)                       # the painting's outline navy (021135)
HI, YEL, GLD, ORA, LIP = (254, 226, 101), (255, 187, 4), (253, 162, 10), (254, 104, 7), (218, 59, 23)
BOX = (118, 8, 304, 86)                  # the logo's box (x0, y0, x1, y1), the layer and the shine
PLATE = (144, 77, 298, 96)               # the new plate (x0, y0, x1, y1 exclusive)
PLATE_FILL, PLATE_RIM, PLATE_LINE, TEXT_SH = (3, 37, 84), (51, 154, 223), (2, 17, 53), (2, 17, 53)

def warm(img): return (img[..., 0] > 120) & (img[..., 0] > img[..., 2] + 60)
def navy(img):
    lum = 0.3 * img[..., 0] + 0.59 * img[..., 1] + 0.11 * img[..., 2]
    return (img[..., 2] > img[..., 0] + 20) & (lum < 100)          # the outline navy and the mid blues of its edge

def glyph_masks(img):
    """the letters' warm components in x order (F E T C H !) and the paw's parts"""
    w = warm(img); w[:, :126] = False; w[78:] = False; w[:12] = False
    lb, n = ndimage.label(w)
    comps = []
    for i in range(1, n + 1):
        m = lb == i
        if m.sum() < 15: continue
        ys, xs = np.nonzero(m); comps.append((xs.min(), ys.min(), xs.max(), ys.max(), m))
    letters = [c for c in comps if c[4].sum() > 300]; paw = [c for c in comps if c[4].sum() <= 300 and c[1] > 50]
    letters.sort(key=lambda c: c[0])
    return [c[4] for c in letters], [c[4] for c in paw]

def poly_clean(m, eps=1.2):
    """the mask's outline fitted with straight segments and filled again (holes kept)"""
    cs, hier = cv2.findContours(m.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = np.zeros(m.shape, np.uint8)
    for i, c in enumerate(cs):
        a = cv2.approxPolyDP(c, eps, True)
        cv2.fillPoly(out, [a], 0 if hier[0][i][3] >= 0 else 1)
    return out.astype(bool)

DISC5 = np.array([[0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0]], bool)
def outline(m, r=2):
    return ndimage.binary_dilation(m, structure=DISC5 if r == 2 else np.ones((3, 3), bool))

# the painting's logo ramp in six steps (its five warm colours and the one between its gold and its orange) and a
# lighter highlight for the gradient versions' top edge
RAMP6 = [(254, 226, 101), (255, 187, 4), (253, 162, 10), (254, 133, 9), (254, 104, 7), (218, 59, 23)]
HI6 = (255, 244, 184)
def bands(fill, lay, mode='bands'):
    """the fill, by the shape's own height (top to bottom):
      bands     three hard bands (yellow, gold, orange), a highlight row on the top edge, a lip on the bottom edge
      steps6    the six-step ramp as hard bands, the highlight row on top
      gradient  the six steps with each step's first two rows an ordered 2 x 2 checker of it and the step above,
                the checker's phase fixed to the screen ((x + y) even), so every letter's pattern lines up"""
    ys, xs = np.nonzero(fill); y0, y1 = ys.min(), ys.max(); H = max(1, y1 - y0 + 1)
    up = np.zeros_like(fill); up[1:] = fill[:-1]; top = fill & ~up
    if mode == 'bands':
        for y, x in zip(ys, xs):
            t = (y - y0) / max(1, H - 1)
            lay[y, x] = (*(YEL if t < 0.42 else GLD if t < 0.64 else ORA), 255)
        dn = np.zeros_like(fill); dn[:-1] = fill[1:]; bot = fill & ~dn
        lay[top] = (*HI, 255); lay[bot & ~top] = (*LIP, 255)
        return
    starts = [y0 + int(round(k * H / 6)) for k in range(6)]          # each step's first row
    def step(y): return max(k for k in range(6) if starts[k] <= y)
    for y, x in zip(ys, xs):
        k = step(y)
        if mode == 'gradient' and k > 0 and y - starts[k] < 2 and (x + y) % 2 == 0: k -= 1
        lay[y, x] = (*RAMP6[k], 255)
    lay[top] = (*HI6, 255)

def oval(w, h):
    """a filled oval w x h, symmetric left-right and top-bottom (built from its top-left quarter)"""
    m = np.zeros((h, w), bool); cy, cx = (h - 1) / 2, (w - 1) / 2
    for y in range(h):
        for x in range(w):
            if ((x - cx) / (w / 2)) ** 2 + ((y - cy) / (h / 2)) ** 2 <= 1.0: m[y, x] = True
    return m | m[:, ::-1] | m[::-1, :]

def paw_mask(shape, parts):
    """the paw redrawn symmetric about the pad's centre line: toes 5 x 6 (inner pair higher), a pad 14 x 12"""
    allp = np.zeros(shape, bool)
    for p in parts: allp |= p
    ys, xs = np.nonzero(allp)
    cx2 = 2 * ((xs.min() + xs.max() + 1) // 2)    # twice the centre line, even: an even-width paw mirrors exactly
    pad = max(parts, key=lambda p: p.sum()); py, px = np.nonzero(pad)
    m = np.zeros(shape, bool)
    def place(sh, x0, y0): m[y0:y0 + sh.shape[0], x0:x0 + sh.shape[1]] |= sh
    pw, ph = 14, 12
    pd = oval(pw, ph); pd[0, :] = pd[1, :] & np.roll(pd[1, :], 1) & np.roll(pd[1, :], -1)   # a flatter top
    place(pd, cx2 // 2 - pw // 2, py.max() - ph + 1)
    toe = oval(5, 6)
    top = ys.min()
    for dx, dy in ((3, 0), (8, 4)):              # inner toes 3 px off the centre, outer 8 px and 4 px lower
        xl = cx2 // 2 - dx - 3; xr = cx2 - (xl + 5)
        place(toe, xl, top + dy); place(toe, xr, top + dy)
    return m

def build(img, mode='bands'):
    """returns the logo layer (H x W x 4), the base with the old logo and plate painted out, and the logo's mask"""
    H, W, _ = img.shape
    letters, paw = glyph_masks(img)
    lay = np.zeros((H, W, 4), np.uint8)
    shapes = [poly_clean(m) for m in letters] + [paw_mask((H, W), paw)]
    def depth_of(f):
        o = outline(f); d_ = o.copy()
        for d in (1, 2): s = np.zeros_like(o); s[d:] = o[:-d]; d_ |= s
        return d_
    allnavy = np.zeros((H, W), bool)
    for f in shapes: allnavy |= depth_of(f)
    # one navy block behind the letters, as painted: the narrow gaps between neighbouring outlines closed
    allnavy = ndimage.binary_closing(allnavy, structure=DISC5, iterations=1) | allnavy
    allnavy = ndimage.binary_fill_holes(allnavy)
    lay[allnavy] = (*NAVY, 255)
    for f in shapes:                              # back to front: F first, the paw last
        lay[depth_of(f)] = (*NAVY, 255)
        bands(f, lay, mode)
    # no lone pixels: a fill pixel with no neighbour of its colour (8 ways) takes the colour most of its fill
    # neighbours share (a band boundary crossing a thin stroke can leave one)
    for _ in range(3):
        k = lay[..., 0].astype(int) * 65536 + lay[..., 1].astype(int) * 256 + lay[..., 2]; k[lay[..., 3] == 0] = -1
        fixed = 0
        for y, x in zip(*np.nonzero((lay[..., 3] > 0) & (lay[..., 0] > 150))):
            nb = k[y - 1:y + 2, x - 1:x + 2].ravel(); c = k[y, x]
            if (nb == c).sum() > 1: continue
            cand = [v for v in nb if v != c and v >= 0 and (v >> 16) > 150]
            if mode == 'gradient' and any(v == c for v in k[y - 1:y + 2:2, x - 1:x + 2:2].ravel()): continue   # (a checker pixel)
            if not cand: continue
            v = max(set(cand), key=cand.count); lay[y, x, :3] = (v >> 16, (v >> 8) & 255, v & 255); fixed += 1
        if not fixed: break
    # the old logo and plate out of the base: warm or navy pixels near the old letters, and the old plate's box
    old = np.zeros((H, W), bool)
    for m in letters + paw: old |= m
    near = ndimage.binary_dilation(old, iterations=6)
    pm = (warm(img) | navy(img)) & near
    pm[76:98, 146:296] = True
    pm |= ndimage.binary_dilation(pm, iterations=1) & (navy(img) | warm(img))
    base = img.copy()
    for y in range(H):
        xs = np.nonzero(pm[y])[0]
        for x in xs:
            l = x - 1
            while l >= 0 and pm[y, l]: l -= 1
            r = x + 1
            while r < W and pm[y, r]: r += 1
            src = l if (x - l <= r - x and l >= 0) or r >= W else r
            base[y, x] = img[y, src]
    return lay, base, pm

# ---- the tagline -------------------------------------------------------------------------------------------------
LOWER = {          # the v8 small font's lowercase: x-height 5 (rows 2-6 of the capitals' 7), ascenders 7, descenders 2
    'h': ["##...", "##...", "####.", "##.##", "##.##", "##.##", "##.##"],
    'e': [".....", ".....", ".###.", "##.##", "#####", "##...", ".####"],
    'i': ["##", "..", "##", "##", "##", "##", "##"],
    't': [".##.", ".##.", "####", ".##.", ".##.", ".##.", "..##"],
    'y': [".....", ".....", "##.##", "##.##", "##.##", ".####", "...##", "##.##", ".###."],
    'o': [".....", ".....", ".###.", "##.##", "##.##", "##.##", ".###."],
    'g': [".....", ".....", ".####", "##.##", "##.##", "##.##", ".####", "...##", ".###."],
    'd': ["...##", "...##", ".####", "##.##", "##.##", "##.##", ".####"],
    'v': [".....", ".....", "##.##", "##.##", "##.##", ".###.", "..#.."],
    'n': [".....", ".....", "####.", "##.##", "##.##", "##.##", "##.##"],
    'u': [".....", ".....", "##.##", "##.##", "##.##", "##.##", ".####"],
    'r': [".....", ".....", "##.##", "####.", "##...", "##...", "##..."],
}
def text_mask(s):
    rows = 9
    gl = []
    for ch in s:
        if ch == ' ': gl.append(None); continue
        g = LOWER.get(ch) or glyphs7.G[ch.upper()]
        gl.append(np.array([[c == '#' for c in r] for r in g] + [[False] * len(g[0])] * (rows - len(g))))
    w = sum(S8.SPACE[7] if g is None else g.shape[1] + S8.GAP[7] for g in gl) - S8.GAP[7]
    m = np.zeros((rows, w), bool); x = 0
    for g in gl:
        if g is None: x += S8.SPACE[7]; continue
        m[:, x:x + g.shape[1]] |= g; x += g.shape[1] + S8.GAP[7]
    return m

def plate(text):
    """the plate with its text, as a layer the size of PLATE (RGBA); the text centred on the plate"""
    x0, y0, x1, y1 = PLATE; w, h = x1 - x0, y1 - y0
    p = np.zeros((h, w, 4), np.uint8)
    m = np.ones((h, w), bool)
    for (y, x) in ((0, 0), (0, 1), (1, 0), (0, w - 1), (0, w - 2), (1, w - 1), (h - 1, 0), (h - 1, 1), (h - 2, 0), (h - 1, w - 1), (h - 1, w - 2), (h - 2, w - 1)): m[y, x] = False
    edge = m & ~ndimage.binary_erosion(m, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    inner = m & ~edge
    rim = inner & ~ndimage.binary_erosion(inner, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), border_value=0)
    p[m] = (*PLATE_FILL, 255); p[rim] = (*PLATE_RIM, 255); p[edge] = (*PLATE_LINE, 255)
    t = text_mask(text); th, tw = t.shape
    caps = all(c == ' ' or c.isupper() for c in text)
    body_h = 7
    ty = (h - body_h) // 2 if caps else (h - body_h) // 2 - 1   # the capitals' 7 rows centred (lowercase: 1 up for the descenders)
    tx = (w - tw) // 2
    st = S8.STYLES['cream']
    ys, xs = np.nonzero(t)
    for y, x in zip(ys, xs):                       # the shadow first, 1 px down and right
        if 0 <= ty + y + 1 < h and 0 <= tx + x + 1 < w and inner[ty + y + 1, tx + x + 1]: p[ty + y + 1, tx + x + 1] = (*TEXT_SH, 255)
    for y, x in zip(ys, xs):
        col = S8.band(st, y, body_h) if y < body_h else st['deep']
        p[ty + y, tx + x] = (*col, 255)
    return p, (tx, ty, tw, th)

# ---- "clean": the painting's own logo, only its noise tidied ------------------------------------------------------
RAMP3 = [(255, 187, 4), (253, 162, 10), (254, 104, 7)]   # the dithered gradient's colours, light to dark
def old_logo_mask(img):
    """the painting's logo as it is: its letters, outline, depth and paw (warm or navy pixels next to the letters),
    without the old tagline plate"""
    letters, paw = glyph_masks(img)
    old = np.zeros(img.shape[:2], bool)
    for m in letters + paw: old |= m
    near = ndimage.binary_dilation(old, iterations=6)
    m = (warm(img) | navy(img)) & near
    m[77:98, 146:296] = False
    return m, letters, paw

def _straighten(lay, fillm):
    """1 px bumps and notches on an edge that is straight 2 px either side, on the silhouette and on the fill's edge
    against the outline: a bump goes, a notch is filled (with its neighbour's colour); checked in all 4 directions"""
    n = 0
    for target in ('sil', 'fill'):
        for rot in range(4):
            L = np.rot90(lay, rot).copy()
            M = np.rot90(L[..., 3] > 0 if target == 'sil' else fillm, rot).copy() if target == 'fill' else (L[..., 3] > 0)
            if target == 'fill': M = np.rot90(fillm, rot).copy()
            H, W = M.shape
            for y in range(1, H - 1):
                for x in range(2, W - 2):
                    # a bump: M at (x, y) alone on its row, the row below straight and full, the row above empty
                    if M[y, x] and not M[y, x - 1] and not M[y, x + 1] and M[y + 1, x - 2:x + 3].all() and not M[y - 1, x - 1:x + 2].any():
                        L[y, x] = L[y, x - 1] if target == 'fill' else 0; M[y, x] = False; n += 1
                    # a notch: a hole of 1 in a row that is full 2 px either side, the row above empty there
                    elif not M[y, x] and M[y, x - 2:x].all() and M[y, x + 1:x + 3].all() and M[y + 1, x] and not M[y - 1, x - 2:x + 3].any():
                        L[y, x] = L[y, x - 1]; M[y, x] = True; n += 1
            lay[...] = np.rot90(L, -rot)
            if target == 'fill': fillm[...] = np.rot90(M, -rot)
    return n

def clean(img):
    """the painting's logo layer with the speckle replaced: per letter and row, the dithered gradient pixels
    (its yellow, gold and orange) average to a level; the level, smoothed over 3 rows, is set as a solid colour or an
    ordered 2 x 2 checker of its two nearest ramp colours ((x + y) even takes the lighter), aligned to the screen.
    Highlight streaks, the bevel, the outline and the depth (every other colour) stay exactly as painted."""
    H, W, _ = img.shape
    m, letters, paw = old_logo_mask(img)
    lay = np.zeros((H, W, 4), np.uint8); lay[m, :3] = img[m]; lay[m, 3] = 255
    key = {c: i for i, c in enumerate(RAMP3)}
    def lvl(p): return key.get(tuple(int(v) for v in p), -1)
    for g in letters + [np.logical_or.reduce(paw)]:
        ys, xs = np.nonzero(g); y0, y1 = ys.min(), ys.max()
        rows = {}
        for y in range(y0, y1 + 1):
            xx = [x for x in np.nonzero(g[y])[0] if lvl(img[y, x]) >= 0]
            if xx: rows[y] = (xx, np.mean([lvl(img[y, x]) for x in xx]))
        if not rows: continue
        yl = sorted(rows)
        for y in yl:
            near_ = [rows[yy][1] for yy in (y - 1, y, y + 1) if yy in rows]
            lv = np.mean(near_)
            k = int(round(lv * 2))                    # half steps: even = a solid colour, odd = a checker
            for x in rows[y][0]:
                c = k // 2 if k % 2 == 0 else (k // 2 if (x + y) % 2 == 0 else k // 2 + 1)
                lay[y, x, :3] = RAMP3[min(2, c)]
    # lone pixels a shade off: no neighbour of its colour in 8 directions, close (dE < 18) to the colour most of its
    # neighbours share -> that colour (the checker keeps its diagonal neighbours, so it is never touched)
    from skimage.color import rgb2lab
    for _ in range(2):
        k = lay[..., 0].astype(int) * 65536 + lay[..., 1].astype(int) * 256 + lay[..., 2]; k[lay[..., 3] == 0] = -1
        lab = rgb2lab(lay[..., :3] / 255.0)
        o = lay.copy()
        for y, x in zip(*np.nonzero(lay[..., 3] > 0)):
            nb = k[max(0, y - 1):y + 2, max(0, x - 1):x + 2]; c = k[y, x]
            if (nb == c).sum() > 1: continue
            vals = [v for v in nb.ravel() if v != c and v >= 0]
            if len(vals) < 5: continue
            v = max(set(vals), key=vals.count)
            ys_, xs_ = np.nonzero(nb == v); yy, xx = ys_[0] + max(0, y - 1), xs_[0] + max(0, x - 1)
            if np.linalg.norm(lab[y, x] - lab[yy, xx]) < 18: o[y, x, :3] = lay[yy, xx, :3]
        lay = o
    fillm = (lay[..., 3] > 0) & (lay[..., 0] > 120) & (lay[..., 0].astype(int) > lay[..., 2].astype(int) + 60)
    nst = _straighten(lay, fillm)
    return lay, nst
