"""Pepper's hand shading pass (24 Oct): after the cleanup (cleanup.py, head.py) her coat is repainted in the manner of a
1994 animated-feature portrait: clean clusters, one key light from the upper left, a cool rim light from the right,
and a few deliberate sheen shapes.
  - RAMP: five blue-blacks K0..K4 (K0 is the picture's ink, so her lines stay the outline colour) and two cool
    sheen colours S1, S2
  - the black masses of the cleanup (the outline, the mouth, the shadow the ears cast on her face) stay K0, their
    edges smoothed (a majority filter that leaves the outline ring alone)
  - the rest of the coat starts as K2 and is painted BY HAND in layers of small polygons and strokes, game
    coordinates: the shadow shapes (K1), the lit planes (K3), their cores (K4), the sheen (S1, S2) and the rim;
    then the ink strokes (the wink, the brow creases) and the nose, tongue and bandana tidies"""
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

K0 = (1, 2, 18)
K1 = (24, 22, 40)
K2 = (42, 38, 57)
K3 = (64, 55, 72)
K4 = (96, 80, 92)
S1 = (112, 128, 170)
S2 = (190, 204, 230)
RAMP = [K0, K1, K2, K3, K4, S1, S2]

def poly(pts, shape=(240, 320)):
    im = Image.new('L', (shape[1], shape[0]), 0); ImageDraw.Draw(im).polygon(pts, fill=1, outline=1)
    return np.array(im).astype(bool)

def line(pts, w=1, shape=(240, 320)):
    im = Image.new('L', (shape[1], shape[0]), 0); ImageDraw.Draw(im).line(pts, fill=1, width=w)
    return np.array(im).astype(bool)

# the lamp post and the bushes behind her ear and shoulder fell into the coat mask: left alone
NOT_PEPPER = poly([(0, 149), (29, 149), (31, 151), (36, 152), (39, 156), (41, 160), (44, 165), (44, 167), (38, 168),
                   (38, 187), (22, 187), (22, 200), (0, 200)])

def smooth_ink(k0, coat, keep):
    """the black masses' edges smoothed: inside the coat a pixel takes the 3 x 3 majority (K0 or not), twice;
    `keep` (the outline ring) is never changed; ink crumbs under 6 px go"""
    m = k0.copy()
    for _ in range(2):
        n = ndimage.uniform_filter(m.astype(float), 3) * 9
        new = np.where(n >= 5, True, np.where(n <= 3, False, m))
        m = np.where(coat & ~keep, new, m) & coat
    lb, nn = ndimage.label(m)
    if nn:
        sz = ndimage.sum(m, lb, range(1, nn + 1))
        for i in np.nonzero(sz < 6)[0]: m[lb == i + 1] = False
    return m

# ---- HAND layers ------------------------------------------------------------------------------------------------
# each entry: (tone, kind, points[, width]); kind 'p' polygon, 'l' polyline, 'x' single pixels; painted in order;
# lower case on the lit coat only (so a shape may run past the ink masses' edges), upper case over the ink too
# (tone 0 there draws ink, any other tone takes ink away)
INK_EDITS = [   # ('-', polygon): ink taken away; ('+', polygon): ink added; ('l', polyline, width): an ink stroke
    ('-', [(60, 112), (94, 112), (94, 129), (60, 129)]),          # the wink's old blobs (redrawn in LAYERS)
]
# STAMPS: hand-drawn pixel blocks, (x, y of the top-left, rows); '0' ink, '1'..'4' K1..K4, 's' S1, 'S' S2, '.' leaves
# the pixel as it is; drawn after LAYERS; only '0' paints over ink
STAMPS = [
    # the wink: one arched lid stroke (two pixels thick, tapering at the ends), the lid lit above it,
    # the cheek pushed up into the arch under it, three tidy lashes at its inner end
    (60, 113, [
        "..................................",
        "............2222222222222.........",
        "..........33333333333333333.......",
        "........333333400000003333333.....",
        ".......333333000000000003330333...",
        "......33333300033333330003033033..",
        ".....3333300003333333330003303303.",
        "....33333000444333333344400033033.",
        "...333330044444444444444444003333.",
        "...333300444444444444444444403333.",
        "...3330444444444444444444444433...",
        "....33444444444444444444444444....",
        "......33333444444444444433333.....",
        "........3333333333333333333.......",
    ]),
    # the left ear's sheen, along the fold where the ear turns over at the top
    (54, 97, [
        ".....ss",
        "...ss..",
        "..s....",
        ".s.....",
    ]),
    # the brow over the open eye: the lit ridge with its sheen, the crease, the upper lid catching the light
    (98, 90, [
        "......3333333............",
        ".....3344ss443...........",
        "....33444444433..........",
        "...3333000000332222......",
        "..333003333330011222.....",
        "..33022222222222111122...",
        "...222222222222221111....",
        "...2222222222222221111...",
        "....222222222222221111...",
    ]),
    # the nose's top: one clean outline, the leather's lit plane, the wet highlight as it was painted (cream streak,
    # warm glint, soft tips), a cool rim on its right, the two nostrils' upper rims
    (96, 121, [
        "................3.............",
        "............33333333..........",
        "........3333333330000333......",
        ".......333000000000000000.....",
        "......3300000iiiiiddiiiim.....",
        "......00000iiigghhhhhiimmm....",
        ".....00000iiiigghhhhhiiimm....",
        "....000000iihhhhhhiiiiiii00...",
        "....00000ddhhiiiii0000000000..",
        "....00000iiiiiii000000000000..",
        "...00000iiii000000000iiii000..",
        "...0000i0000i0000000i0000i00..",
    ]),
    # the dome's sheen: one crisp arched highlight on the forehead, a smaller echo by the left ear
    (72, 85, [
        "........ssssss.......",
        "....sssssSSsssss.....",
        "..sss4444444444sss...",
        ".s4444444444444444s..",
        "..44444444444444444..",
    ]),
    (66, 94, [
        "..s.",
        ".ss.",
        "ss..",
    ]),
    # the muzzle top's sheen, hugging the nose's upper left
    (98, 120, [
        ".......sss",
        ".....sSs..",
        "...sss....",
        "..ss......",
    ]),
]
LAYERS = [
    # -- the muzzle's top plane, running from between the eyes down to the nose
    (3, 'p', [(93, 108), (100, 106), (104, 112), (110, 116), (118, 119), (118, 121), (104, 121), (96, 120), (92, 114)]),
    (4, 'p', [(96, 112), (101, 111), (106, 115), (113, 118), (104, 119), (97, 117)]),
]

# ---- the base: a tone field cut into K1..K4 -----------------------------------------------------------------------
# three parts: the painting's own light (its tone, softly blurred: where the painter lit the fur), the forms lit
# from the upper left (small ellipsoids), and the ink masses embossed (beside a black mass the side towards the light
# is in its shadow, the side away from it is a lit edge), which gives every form a clean edge on one light
LIGHT = np.array([-0.62, -0.70, 0.55]); LIGHT = LIGHT / np.linalg.norm(LIGHT)
LDIR = np.array([-0.66, -0.75])                 # towards the light in the picture plane (x, y)
FORMS = [   # name, cx, cy, rx, ry, a polygon it is limited to (None: the nearest ellipse wins)
    ('skull', 88, 104, 42, 30), ('cheekL', 80, 132, 22, 15), ('muzzle', 108, 138, 22, 14), ('jaw', 92, 166, 34, 12),
    ('earL', 36, 128, 26, 40), ('earR', 138, 114, 18, 32), ('chest', 70, 230, 100, 70)]
SHARE = (0.25, 0.37, 0.27, 0.11)                # of the lit coat: K1, K2, K3, K4

def light_of(nx, ny):
    k = np.sqrt(nx ** 2 + ny ** 2); s = np.where(k > 0.97, 0.97 / np.maximum(k, 1e-6), 1.0); nx, ny = nx * s, ny * s
    nz = np.sqrt(1 - nx ** 2 - ny ** 2)
    return np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)

def form_light(mask):
    H, W = mask.shape; yy, xx = np.mgrid[0:H, 0:W].astype(float)
    best = np.full((H, W), 1e9); val = np.zeros((H, W))
    for n, cx, cy, rx, ry in FORMS:
        e = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        t = mask & (e < best); best[t] = e[t]
        val[t] = light_of((xx - cx) / rx, (yy - cy) / ry)[t]
    return val

def shifted(a, dx, dy):
    return ndimage.shift(a, (dy, dx), order=1, mode='nearest')

def base_tone(coat, ink, painting, outline, W_P=0.3, W_F=0.7, W_E=1.1, SIG=1.4):
    lit = coat & ~ink
    Lp = painting.astype(float).mean(-1); mf = coat.astype(float)
    tp = ndimage.gaussian_filter(Lp * mf, SIG) / (ndimage.gaussian_filter(mf, SIG) + 1e-6)
    tp = np.clip((tp - 15) / 45, 0, 1)
    fl = form_light(coat)
    G = ndimage.gaussian_filter((ink & ~outline).astype(float), 1.0)     # the silhouette is no groove: not embossed
    emb = shifted(G, -2 * LDIR[0], -2 * LDIR[1]) - shifted(G, 2 * LDIR[0], 2 * LDIR[1])
    # shifted(G, -d) at p is G(p + d): ink towards the light of p -> positive -> shadow
    val = W_P * tp + W_F * fl - W_E * emb
    v = val[lit]; cuts = np.quantile(v, np.cumsum(SHARE)[:-1])
    t = np.ones(coat.shape, int)
    for c in cuts: t += (val > c) & lit
    return t

def crumbs(tone, lit, maxsize=3, passes=3):
    """lone pixels and crumbs of up to maxsize pixels of one tone take the tone most of their neighbours have"""
    for _ in range(passes):
        ch = 0
        for v in np.unique(tone[lit]):
            lb, n = ndimage.label((tone == v) & lit)
            if not n: continue
            sz = np.bincount(lb.ravel())[1:]
            for i in np.nonzero(sz <= maxsize)[0]:
                c = lb == i + 1; ring = ndimage.binary_dilation(c, np.ones((3, 3))) & ~c & lit
                if not ring.any(): continue
                vv, cc = np.unique(tone[ring], return_counts=True); tone[c] = vv[cc.argmax()]; ch += 1
        if not ch: break
    return tone

# the far side: zones where the forms turn away from the key light; their tones drop a step and the cool rim light
# runs along their outer edge (S1 where the outline is the next pixel to the right, K3 one pixel further in)
FAR = [
    [(126, 99), (140, 97), (151, 104), (151, 142), (128, 143), (126, 120)],          # the right ear's hanging flap
    [(119, 112), (125, 112), (130, 124), (131, 150), (122, 152), (118, 140)],         # the far cheek, beyond the nose
]

def far_side(tone, coat, outline):
    for pts in FAR:
        z = poly(pts) & coat & (tone != 0)
        tone[z] = np.maximum(1, tone[z] - 1)
        r1 = z & np.roll(outline, -1, axis=1)
        r2 = z & ~r1 & np.roll(r1, -1, axis=1)
        tone[r2] = 3; tone[r1] = 5
    return tone

# the body under the bandana: its ink masses and tones were ragged; it is redrawn from the painting's own light,
# blurred wide (sigma 2.2) so only its big forms stay (the near shoulder, the chest's folds, the far chest), cut into
# ink / K1 / K2 / K3 by fixed shares, the cluster edges then smoothed by a majority filter; a cast shadow under the
# bandana's edges; the outline kept
BODY_POLY = [(38, 168), (150, 164), (150, 240), (0, 240), (0, 200), (22, 200), (22, 187), (38, 187)]
BODY_SHARE = (0.42, 0.32, 0.20, 0.06)           # ink, K1, K2, K3

def body(tone, coat, bandana, ring, painting):
    H, W = coat.shape; yy, xx = np.mgrid[0:H, 0:W]
    top = np.full(W, 178)
    for x in range(W):
        ys = np.nonzero(bandana[160:, x])[0]
        if len(ys): top[x] = 160 + ys.min()
    reg = poly(BODY_POLY) & coat & (yy > top[None, :])
    Lp = painting.astype(float).mean(-1); mf = reg.astype(float)
    tp = ndimage.gaussian_filter(Lp * mf, 2.2) / (ndimage.gaussian_filter(mf, 2.2) + 1e-6)
    tp = tp - 6 * (xx > 120)                    # the far chest a little darker (it turns from the light)
    cuts = np.quantile(tp[reg], np.cumsum(BODY_SHARE)[:-1])
    t = sum((tp > c).astype(int) for c in cuts)
    for _ in range(3):                          # the clusters' edges smoothed: each pixel the 3 x 3 majority
        best = t.copy(); bc = np.zeros(t.shape)
        for v in range(4):
            c = ndimage.uniform_filter(((t == v) & reg).astype(float), 3)
            better = c > bc; best[better] = v; bc[better] = c[better]
        t = np.where(reg, best, t)
    shadow = np.zeros_like(coat)
    for d in (1, 2, 3): shadow |= np.roll(bandana, d, axis=0)
    t[shadow & ~bandana] = 0
    tone[reg] = t[reg]
    tone[reg & ring] = 0
    return tone

# the bandana: three pinks and a shadow; its tones redrawn from the painting's light blurred a little (sigma 0.9,
# so the folds stay as long clean streaks), cut by the shares the cleanup gave it, the edges smoothed by a majority
# filter and crumbs merged; the knot's tips keep their outline
BANDANA = [(93, 21, 58), (183, 32, 86), (246, 58, 103), (254, 107, 131)]
BANDANA_SHARE = (0.02, 0.17, 0.39, 0.42)

def majority(t, reg, n, passes=2):
    for _ in range(passes):
        best = t.copy(); bc = np.zeros(t.shape)
        for v in range(n):
            c = ndimage.uniform_filter(((t == v) & reg).astype(float), 3)
            better = c > bc; best[better] = v; bc[better] = c[better]
        t = np.where(reg, best, t)
    return t

def bandana(out, mask, painting):
    Lp = painting.astype(float) @ np.array([0.3, 0.59, 0.11]); mf = mask.astype(float)
    tp = ndimage.gaussian_filter(Lp * mf, 0.9) / (ndimage.gaussian_filter(mf, 0.9) + 1e-6)
    cuts = np.quantile(tp[mask], np.cumsum(BANDANA_SHARE)[:-1])
    t = sum((tp > c).astype(int) for c in cuts)
    t = majority(t, mask, 4)
    t = crumbs(t, mask, maxsize=2)
    for v, c in enumerate(BANDANA): out[mask & (t == v)] = c
    return out

# the nose's own colours (its leather, its cool rim, the wet highlight and its warm glint), for the nose stamp
NOSE_COLS = dict(i=(9, 23, 57), m=(54, 61, 90), h=(254, 234, 202), g=(210, 129, 83), d=(163, 138, 138))
CH = '01234sS' + ''.join(NOSE_COLS)
PAL = np.array(RAMP + list(NOSE_COLS.values()))

def paint(img, mats, painting):
    out = img.copy()
    coat = mats['coat'] & ~NOT_PEPPER
    nose = mats['nose']
    pep_all = coat | nose | mats['eye'] | mats['tongue'] | mats['bandana']
    dark = img.mean(-1) < 8                         # the ink and its near-black twins (merged into it later)
    k0 = dark & coat
    ring = coat & ndimage.binary_dilation(~(pep_all | (mats['coat'] & NOT_PEPPER)), np.ones((5, 5)))
    k0 = smooth_ink(k0, coat, ring)
    for L in INK_EDITS:                                   # the ink masses reshaped by hand first
        m = poly(L[1]) if L[0] != 'l' else line(L[1], L[2])
        k0 = (k0 | (m & coat)) if L[0] in ('+', 'l') else (k0 & ~m)
    tone = base_tone(coat, k0, painting, ring)
    tone = crumbs(tone, coat & ~k0)
    tone[k0] = 0
    tone = far_side(tone, coat, k0)
    ring0 = ring & dark
    tone = body(tone, coat, mats['bandana'], ring0, painting)
    tone = crumbs(tone, coat, maxsize=2)
    for L in LAYERS:
        t, kind, pts = L[0], L[1], L[2]
        if kind in 'pP': m = poly(pts)
        elif kind in 'lL': m = line(pts, L[3] if len(L) > 3 else 1)
        else:
            m = np.zeros(coat.shape, bool)
            for x, y in pts: m[y, x] = True
        if kind.islower(): m &= tone != 0           # lower case: on the lit coat only; upper case: over ink too
        tone[m & coat] = t
    # the nose: its black and its highlight colours stay, its noise (the navy specks) goes black, the fur round it
    # inside its mask takes the tone of the nearest coat pixel; then the stamp redraws its top
    _, (iy, ix) = ndimage.distance_transform_edt(~(coat & (tone > 0)), return_indices=True)
    for y, x in zip(*np.nonzero(nose)):
        c = tuple(img[y, x])
        if img[y, x].mean() < 32: tone[y, x] = 0       # its black, its near-blacks and the navy specks
        elif c in NOSE_COLS.values(): tone[y, x] = CH.index([k for k, v in NOSE_COLS.items() if v == c][0])
        else: tone[y, x] = tone[iy[y, x], ix[y, x]]
    canvas = coat | nose
    for x0, y0, rows in STAMPS:
        for dy, r in enumerate(rows):
            for dx, ch in enumerate(r):
                if ch == '.': continue
                y, x = y0 + dy, x0 + dx
                if canvas[y, x] and (ch == '0' or tone[y, x] != 0 or nose[y, x]): tone[y, x] = CH.index(ch)
    for t in range(len(PAL)):
        m = canvas & (tone == t); out[m] = PAL[t]
    out[pep_all & (img.mean(-1) < 5)] = K0               # the eye's near-black twin is the ink too
    out = tongue_line(out, mats['tongue'], coat)
    out = bandana(out, mats['bandana'], painting)
    return out, dict(coat=coat, k0=tone == 0)

# the tongue's centre line: one clean stroke of its darkest red; the coat pixels that made the old groove become tongue
GROOVE = [(110, 152), (111, 153), (112, 154), (113, 155), (113, 156), (114, 157), (114, 158), (114, 159), (115, 160),
          (115, 161)]
TONGUE_DARK = (93, 21, 58)            # the bandana's shadow colour, already in the picture

def tongue_line(out, tongue, coat):
    inside = ndimage.binary_fill_holes(ndimage.binary_closing(tongue, np.ones((3, 3)))) & coat
    inside[:, :105] = False; inside[:, 120:] = False; inside[:148] = False
    for _ in range(3):
        for y, x in zip(*np.nonzero(inside)):
            nb = [tuple(out[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if tongue[yy, xx] or ((yy, xx) not in zip(*np.nonzero(inside)))]
            nb = [c for c in nb if c != K0 and tuple(c) not in map(tuple, RAMP)]
            if nb:
                v, k = np.unique(np.array(nb), axis=0, return_counts=True); out[y, x] = v[k.argmax()]
    for x, y in GROOVE: out[y, x] = TONGUE_DARK
    return out
