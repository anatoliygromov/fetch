"""Builds the regridded title screen (24 Oct) from its four approved layers:
    python3 art/source/title/tools/build_title_regrid.py          (from the repo root; a few seconds)
Sources (art/source/title/regrid/, all 320 x 240 in game pixels, final; their pixels are not changed here):
    bg_noplate_320.png   the background, without the old PRESS ANY KEY plate (railing and pavement there now)
    pepper_region.png    Pepper's head and bandana (RGBA)
    logo_r4.png          the logo (RGBA)
    tagline_region.png   the tagline plate (RGBA)
Composite order: background, Pepper, logo, tagline. Writes (riverwalk/art/title/, data in riverwalk/title_regrid.lua):
    base.png             the full composite: the logo and the tagline baked in, so nothing old peeks round them;
                         the painting's bird stays in it (title.lua T.BIRD_ANIM is off: the old bird overlay's pixels
                         are out of style next to the new art). With BIRD_OUT = True the bird is painted out with the
                         sky round it instead (for the overlay).
    logo_regrid.png      the logo layer cropped to its box (T.LOGO = "regrid"), logo_hi_regrid.png its shine (the
                         letters' fill brightened, as build_title.py does), title_regrid.lua the box and the twinkle
                         points (the fill's upper edges and its lightest highlight stripe, every 3rd, above y 72)
    tagline_regrid.png   the tagline plate cropped to its box (T.TAGLINE = "regrid")
    ripples              the river sparkles: the light ripple streaks on open water in the composite, each with the
                         water colour round it; title.lua dims a streak to that colour in its off phase, so base.png
                         keeps every ripple as painted.
build_title.py (the old pipeline: the painting's own layers) writes its base.png and then runs this, so base.png is
always the regrid composite."""
import os
import numpy as np
from collections import Counter
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'art', 'source', 'title', 'regrid')
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'title')
W, H = 320, 240
BIRD_OUT = False                       # True: paint the bird out of base.png (only with title.lua T.BIRD_ANIM on)
BIRD_BOX = (246, 100, 272, 112)        # x0, y0, x1, y1: the painting's bird (a dark V in the sky)


def load_rgba(name):
    a = np.array(Image.open(os.path.join(SRC, name)).convert('RGBA'))
    assert a.shape == (H, W, 4), (name, a.shape)
    assert set(np.unique(a[..., 3]).tolist()) <= {0, 255}, name + ': alpha must be 0 or 255'
    return a


def crop_box(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def save(a, name):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))


def paint_out_bird(img):
    """The bird's pixels (much darker than the sky round them) take the most common colour of their non-bird
    4-neighbours, repeated until none is left: flat sky tones exactly as around it."""
    x0, y0, x1, y1 = BIRD_BOX
    lum = img[..., :3].astype(int) @ np.array([30, 59, 11]) // 100
    sky = np.median(lum[y0:y1, x0:x1])
    bird = np.zeros((H, W), bool)
    bird[y0:y1, x0:x1] = lum[y0:y1, x0:x1] < sky - 8
    n = int(bird.sum())
    while bird.any():
        nxt = bird.copy()
        for y, x in zip(*np.nonzero(bird)):
            nb = Counter(tuple(img[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if not bird[yy, xx])
            if nb: img[y, x] = nb.most_common(1)[0][0]; nxt[y, x] = False
        bird = nxt
    return n


def ripples(img):
    """Light streaks on open water: lighter than the water (luma over 190, blue over 170), with water at both ends
    and above or below every pixel, and at least 5 water pixels round each (the rule build_title.py used for the
    painting's sparkles). Each streak's off colour is the commonest water colour touching it."""
    a = img.astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    water = (b > r + 50) & (b > g + 10) & (lum > 60) & (lum < 175)
    spark = np.zeros((H, W), bool)
    for y in range(140, 190):                                         # the river: below the bridge, above the railing
        for x in range(120, W - 1):
            if lum[y, x] > 190 and b[y, x] > 170 and water[y - 1:y + 2, x - 1:x + 2].sum() >= 5: spark[y, x] = True
    out = []
    for y in range(H):
        x = 0
        while x < W:
            if not spark[y, x]: x += 1; continue
            x0 = x
            while x < W and spark[y, x]: x += 1
            if not (water[y, x0 - 1] and water[y, x] and all(water[y - 1, k] or water[y + 1, k] for k in range(x0, x))): continue
            nb = Counter()
            for k in range(x0, x):
                for yy, xx in ((y - 1, k), (y + 1, k), (y, x0 - 1), (y, x)):
                    if water[yy, xx] and not spark[yy, xx]: nb[tuple(int(v) for v in a[yy, xx])] += 1
            c = nb.most_common(1)[0][0]
            if 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2] < 120: continue      # next to a hull or a shadow: not open water
            out.append((x0, y, x - x0) + c)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = np.array(Image.open(os.path.join(SRC, 'bg_noplate_320.png')).convert('RGB'))
    assert bg.shape == (H, W, 3)
    pepper, logo, tag = load_rgba('pepper_region.png'), load_rgba('logo_r4.png'), load_rgba('tagline_region.png')
    comp = bg.copy()
    for lay in (pepper, logo, tag):
        m = lay[..., 3] > 0; comp[m] = lay[..., :3][m]
    Image.fromarray(comp).save(os.path.join(SRC, 'composite.png'))     # the reference the idle title is checked against
    base = comp.copy()
    nbird = paint_out_bird(base) if BIRD_OUT else 0
    save(base, 'base.png')
    lua = ['-- generated by art/source/title/tools/build_title_regrid.py: the regridded title (T.LOGO = "regrid",',
           '-- T.TAGLINE = "regrid"): layer boxes, the logo\'s twinkle points and the river ripples', 'return {']
    # ---- the logo: cropped to its box, placed where it sits in the composite; its shine and twinkle points
    lx0, ly0, lx1, ly1 = crop_box(logo)
    reg = logo[ly0:ly1, lx0:lx1]
    save(reg, 'logo_regrid.png')
    fill = (reg[..., 3] > 0) & (reg[..., 0] > 150) & (reg[..., 0].astype(int) > reg[..., 2].astype(int) + 60)
    lightest = fill & (reg[..., 0] > 250) & (reg[..., 1] > 215)
    up = np.zeros_like(fill); up[1:] = fill[:-1]
    cand = np.nonzero((fill & ~up) | lightest)
    pts = sorted({(int(x) + lx0, int(y) + ly0) for y, x in zip(*cand) if y + ly0 < 72})[::3]
    hi = reg[..., :3].astype(float) + (np.array([255, 248, 214]) - reg[..., :3]) * 0.6
    save(np.dstack([np.clip(hi, 0, 255), fill * 255]), 'logo_hi_regrid.png')
    lua.append('  logo = { x = %d, y = %d, w = %d, h = %d },' % (lx0, ly0, lx1 - lx0, ly1 - ly0))
    lua.append('  sparkle_points = { %s },' % ', '.join('{ %d, %d }' % p for p in pts))
    # ---- the tagline plate: cropped, placed exactly
    tx0, ty0, tx1, ty1 = crop_box(tag)
    save(tag[ty0:ty1, tx0:tx1], 'tagline_regrid.png')
    lua.append('  plate = { x = %d, y = %d, w = %d, h = %d },' % (tx0, ty0, tx1 - tx0, ty1 - ty0))
    # ---- the river ripples (title.lua T.SPARKLES)
    rp = ripples(comp)
    lua.append('  ripples = {')
    for q in rp: lua.append('    { %d, %d, %d, %d, %d, %d },' % q)
    lua.append('  },')
    lua.append('}')
    open(os.path.join(ROOT, 'riverwalk', 'title_regrid.lua'), 'w').write('\n'.join(lua) + '\n')
    print('regrid title: base colours %d; logo box %d,%d %dx%d, twinkle points %d; plate box %d,%d %dx%d; ripples %d; bird px painted out %d'
          % (len(np.unique(base.reshape(-1, 3), axis=0)), lx0, ly0, lx1 - lx0, ly1 - ly0, len(pts), tx0, ty0, tx1 - tx0, ty1 - ty0, len(rp), nbird))


if __name__ == '__main__':
    main()
