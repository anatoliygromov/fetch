# Art for the two greybox levels (fix 11, 6 Oct 2026): City Park (level 1) and Downtown (level 2), in the River
# Walk style. Modelled on tools/make_night_art.py.
#
# Sources in source_scenery/ (SpriteCook renders, gemini-3.1-flash-image, River Walk props and Pepper as style and
# scale references). They came through the browser already reduced to 24 colours (median cut), to keep the
# download small; this script quantises each piece again to 5-12 colours (k-means in Lab) and despeckles it.
#   cp_props1_spritecook.png   log, leaf pile, flat leaves, picnic table (drawn at ~2x: halved, or cut)
#   cp_props2_spritecook.png   hedge, leaf cart, duck boat, stepping stone (1x)
#   cp_oak_spritecook.png      the big oak (1x)
#   cp_treeline_spritecook.png far autumn tree line strip (1x)
#   cp_ground_spritecook.png   path and grass strip (drawn at 2x: halved, then mirrored to a 240 px loop)
#   cp_bgset_spritecook.png    two autumn trees, swing set, park gate, a bush (1x)
#   dt_props1_spritecook.png   awning, crates, parasol, market stall, cafe table (1x)
#   dt_statue_spritecook.png   bronze statue (1x), granite pedestal (halved)
#   dt_tram_spritecook.png     the tram (halved)
#   dt_kioskset_spritecook.png doorway, tram shelter, kiosk, RIVER sign (1x)
#   dt_facades_spritecook.png  old town facades strip (halved)
#   dt_roofs_spritecook.png    far roofs and spires strip (halved)
#   dt_ground_spritecook.png   cobbled pavement and street strip (halved, mirrored)
#   cp_willow_spritecook.png   weeping willow (halved), dt_houses_spritecook.png: the three houses of the rooftop
#                              route (1x). The Downtown tub is River Walk's planter, cut.
# Drawn here by hand: the hedge's stems, the playground slide and climbing frame, the cafe
# table legs and parasol pole, the shop sign, the fountain (rims, bowl, spout), the foreground bollards.
# The oak's branches, the willows' boughs and the balconies are drawn in scene.lua, from their one-way boxes.
# Also by hand: the winch, the hollow log, the fountain's top tier.
#
# Nothing is resampled smoothly: sizes change only by cutting or repeating whole rows/columns, or by an exact 2x
# block reduction (half()).
# Obstacles keep (or get) a 1 px dark outline; decoration has its outline removed (deoutline) and is faded in
# the game (scene.lua), so the files here are unfaded.
import os, numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import rgb2lab
from sklearn.cluster import KMeans
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source_scenery')
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'scene')
INK = (29, 24, 22)                                                # outline colour for the hand-drawn obstacles

def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def sheet(n): return np.array(Image.open(os.path.join(SRC, n + '_spritecook.png')).convert('RGBA'))

def piece(n, x0, y0, x1, y1, minpx=12):
    # the pixels of sheet n inside the box (inclusive), without loose specks of neighbouring pieces, trimmed
    a = sheet(n)[y0:y1 + 1, x0:x1 + 1].copy()
    lab, k = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    for i in range(1, k + 1):
        if (lab == i).sum() < minpx: a[lab == i] = 0
    return trim(a)

def trim(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def palette(a, k, seed=1):
    # k-means in Lab over the opaque pixels, then a despeckle pass (lone pixels take their neighbours' colour)
    H, W = a.shape[:2]
    on = a[..., 3] > 20
    rgb = a[..., :3]
    lab = rgb2lab(rgb / 255.0)
    k = min(k, len(np.unique(rgb[on], axis=0)))
    km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(lab[on])
    idx = np.full((H, W), -1); idx[on] = km.labels_
    pal = np.array([rgb[on][km.labels_ == i].mean(0) for i in range(k)]).round().astype(np.uint8)
    for _ in range(2):
        out = idx.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                c = idx[y, x]
                if c < 0: continue
                nb = idx[y - 1:y + 2, x - 1:x + 2].ravel().tolist(); nb.pop(4)
                if min(nb) < 0 or sum(1 for n in nb if n == c) > 1: continue
                vals, cnt = np.unique(nb, return_counts=True)
                if cnt.max() >= 5: out[y, x] = vals[np.argmax(cnt)]
        idx = out
    o = np.zeros((H, W, 4), np.uint8)
    o[idx >= 0, :3] = pal[idx[idx >= 0]]; o[idx >= 0, 3] = 255
    return o

def half(a):
    # exact 2x block reduction: the darkest pixel where the block holds outline (1 px lines survive), else the
    # median colour (as make_props.half)
    a = a.astype(int); H, W = a.shape[:2]
    p = np.zeros(((H + 1) // 2 * 2, (W + 1) // 2 * 2, 4), int); p[:H, :W] = a
    out = np.zeros((p.shape[0] // 2, p.shape[1] // 2, 4), np.uint8)
    for y in range(out.shape[0]):
        for x in range(out.shape[1]):
            blk = p[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(4, 4)
            on = blk[blk[:, 3] > 20]
            if len(on) < 2: continue
            L = on[:, :3].sum(1)
            c = on[np.argmin(L)] if L.min() < 120 else np.median(on, axis=0)
            out[y, x, :3] = c[:3]; out[y, x, 3] = 255
    return out

def take(a, spans, axis):
    # whole rows (axis 0) or columns (axis 1) in the given [a, b) spans, in order: cuts and repeats
    return np.concatenate([np.take(a, range(s, e), axis=axis) for s, e in spans], axis=axis)
def rows(a, *spans): return take(a, spans, 0)
def cols(a, *spans): return take(a, spans, 1)
def rep(a, i, n, axis):
    # repeat row/column i n extra times
    return np.concatenate([np.take(a, range(0, i + 1), axis=axis), np.repeat(np.take(a, [i], axis=axis), n, axis=axis),
                           np.take(a, range(i + 1, a.shape[axis]), axis=axis)], axis=axis)

def best_cut(a, lo, hi, n, axis=1):
    # where removing n columns (rows) leaves the smallest seam
    v = a.astype(int)
    hi = min(hi, a.shape[axis] - n)
    if axis == 1: return min(range(lo, hi), key=lambda x: np.abs(v[:, x] - v[:, x + n]).sum())
    return min(range(lo, hi), key=lambda y: np.abs(v[y] - v[y + n]).sum())
def cut(a, lo, hi, n, axis=1):
    i = best_cut(a, lo, hi, n, axis)
    return np.concatenate([np.take(a, range(0, i), axis=axis), np.take(a, range(i + n, a.shape[axis]), axis=axis)], axis=axis)

def outline(a, col=INK):
    # a 1 px outline around the silhouette, outside the art (1 px bigger on every side), as Sc.outline
    H, W = a.shape[:2]
    o = np.zeros((H + 2, W + 2, 4), np.uint8); o[1:-1, 1:-1] = a
    on = o[..., 3] > 0
    ring = ndimage.binary_dilation(on, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])) & ~on
    o[ring, :3] = col; o[ring, 3] = 255
    return o

def deoutline(a):
    # decoration has no dark outline: each dark pixel on the silhouette's edge takes the colour of its brightest
    # opaque neighbour inside the shape (as make_props.deoutline)
    a = a.copy(); H, W = a.shape[:2]
    on = a[..., 3] > 0
    L = a[..., :3].astype(int).sum(2)
    inner = ndimage.binary_erosion(on, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    out = a.copy()
    for y, x in zip(*np.nonzero(on & ~inner)):
        if L[y, x] > 200: continue
        best = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and inner[yy, xx] and L[yy, xx] > L[y, x] + 60:
                    if best is None or L[yy, xx] > L[best]: best = (yy, xx)
        if best: out[y, x] = a[best]
    return out

def canvas(w, h): return np.zeros((h, w, 4), np.uint8)
def put(a, x, y, c):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]: a[y, x, :3] = c; a[y, x, 3] = 255
def rect(a, x0, y0, x1, y1, c):                                  # inclusive
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): put(a, x, y, c)
def paste(dst, src, x, y):
    h, w = src.shape[:2]
    m = src[..., 3] > 0
    dst[y:y + h, x:x + w][m] = src[m]

def mirror_loop(a): return np.concatenate([a, a[:, ::-1]], axis=1)  # a strip that tiles seamlessly

# ---------------------------------------------------------------- City Park
def park_ground():
    # 240 x 133 at 2x: halved (120 x 67), mirrored to a 240 px loop, one more earth row (68 rows: y 172-240)
    a = half(sheet('cp_ground'))
    a = rep(a, a.shape[0] - 1, 1, 0)
    return mirror_loop(palette(a, 12))

def park_treeline():
    # the far tree line: its bottom rows (holes, pale trunks) are cut off; it stands behind the near trees
    a = trim(sheet('cp_treeline'))
    a = a[:31]
    return mirror_loop(palette(a, 10))

def park_tree(i):
    a = piece('cp_bgset', *[(162, 89, 248, 195), (251, 89, 336, 195)][i])
    return deoutline(palette(a, 10))

def park_gate():
    return deoutline(palette(piece('cp_bgset', 122, 178, 180, 248), 10))

def park_swings():
    # 114 x 96: the middle of the top bar and one swing are cut out (two seats become one wide gap less): 82 wide
    a = piece('cp_bgset', 0, 153, 113, 248)
    a = cut(a, 40, 60, 30)
    return deoutline(palette(a, 8))

def park_bush():
    # the foreground bush tops (dark, near the camera, not faded): the bush, darkened
    a = palette(piece('cp_bgset', 255, 215, 329, 248), 6)
    a[..., :3] = (a[..., :3].astype(int) * 0.55).astype(np.uint8)
    return a

def park_log():
    a = half(piece('cp_props1', 4, 66, 94, 107))                  # 46 x 21: body rows 4-20
    a = cut(a, 14, 30, 6)                                         # 40 wide
    return palette(a, 9)

def half_bright(a):
    # exact 2x block reduction keeping the brighter half of each block (the leaf piles: the plain half() keeps the
    # dark veins and the pile turns into a spotted shell)
    a = a.astype(int); H, W = a.shape[:2]
    p = np.zeros(((H + 1) // 2 * 2, (W + 1) // 2 * 2, 4), int); p[:H, :W] = a
    out = np.zeros((p.shape[0] // 2, p.shape[1] // 2, 4), np.uint8)
    for y in range(out.shape[0]):
        for x in range(out.shape[1]):
            blk = p[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(4, 4)
            on = blk[blk[:, 3] > 20]
            if len(on) < 2: continue
            o = on[np.argsort(-on[:, :3].sum(1))][:max(1, len(on) // 2)]
            out[y, x, :3] = np.median(o, axis=0)[:3]; out[y, x, 3] = 255
    return out

LEAF_INK = (74, 38, 18)
def park_leaves():
    # leaf pile 94 x 39 (2x): halved (47 x 20), 7 colours, its own dark outline (it is in Pepper's way)
    a = half_bright(piece('cp_props1', 119, 67, 212, 105))
    return outline(palette(a, 7), LEAF_INK)

def park_leaves_flat():
    a = half_bright(piece('cp_props1', 0, 125, 98, 153))
    return outline(palette(trim(a), 7), LEAF_INK)

def park_table():
    # picnic table 111 x 38 (1x): 39 columns cut between the legs (72 wide), rows cut from the legs (28 tall), and
    # the space under the top boarded up (it is solid: Pepper cannot crawl under it)
    a = piece('cp_props1', 113, 120, 223, 157)
    a = cut(a, 30, 70, 39)
    a = cut(a, 23, 27, 10, axis=0)
    a = palette(a, 9)
    H, W = a.shape[:2]
    # the side boards: between the top (row 0-4) and the bench, behind the legs
    L = a[..., :3].astype(int).sum(2)
    board = a[2, W // 2, :3].copy(); dark = a[0, W // 2, :3].copy()
    shade = (board.astype(int) * 0.72).astype(np.uint8)
    for y in range(5, 15):
        for x in range(6, W - 6):
            if a[y, x, 3] == 0: put(a, x, y, shade if y % 4 else dark)
    return a

def park_hedge():
    # hedge 70 x 58 (1x): the body (rows 0-49) cut to 64 wide and 53 tall; two woody stems carry it, at its ends
    a = piece('cp_props2', 0, 82, 69, 139)
    body = a[:50]
    body = cut(body, 20, 45, 6)
    body = rep(body, 25, 3, 0)                                    # 53 rows
    body = palette(body, 10)
    W = body.shape[1]
    o = canvas(W, 53 + 19)
    bark, barkd = hexc('6b4a2e'), hexc('4a3220')
    for sx in (5, W - 9):                                         # stems 4 px wide, outlined
        rect(o, sx - 1, 50, sx + 4, 71, INK)
        rect(o, sx, 50, sx + 3, 71, bark); rect(o, sx + 3, 50, sx + 3, 71, barkd)
    paste(o, body, 0, 0)
    return o

def park_stone():
    # 35 x 25 (1x), 26 wide; below its 25 rows the stone goes on down (row 20 repeated) to the pond floor
    a = piece('cp_props2', 76, 115, 110, 139)
    a = cut(a, 8, 20, 9)
    a = rep(a, 20, 30, 0)
    return palette(a, 7)

def park_boat():
    return palette(piece('cp_props2', 116, 107, 169, 139), 10)

def park_cart():
    # leaf cart 48 x 39 (1x): rows cut from the leaf heap and the barrow body, so it is 28 tall (under the table top)
    a = piece('cp_props2', 174, 101, 221, 139)
    a = cut(a, 3, 9, 3, axis=0)
    a = cut(a, 12, 22, 8, axis=0)
    return palette(a, 10)

def park_oak():
    # 187 x 168 (1x): 38 rows of plain trunk cut out (130 tall: crown top y 44, roots y 174). Decoration.
    a = trim(sheet('cp_oak'))
    a = cut(a, 85, 140, 38, axis=0)
    return deoutline(palette(a, 12))

def park_slide():
    # the playground slide, by hand, to the map's shape: the tower (32 wide, deck y 152, 32 tall to the path) and
    # the slide (45 degrees, 32 x 32, from the deck's right edge down to the path). Handrail posts up to y 124.
    # Image 64 x 61: its (0, 0) is level (1664, 123); the deck is row 29.
    W, H = 66, 62
    o = canvas(W, H)
    red, redd, redl = hexc('c8473a'), hexc('8f2f27'), hexc('e2715d')
    yel, yeld = hexc('e8b83f'), hexc('b5872a')
    gry, gryd = hexc('9aa3ab'), hexc('6b737b')
    D = 29                                                         # deck row (y 152)
    # posts (metal), the deck (yellow planks), the ladder rungs, the rail
    for px in (1, 28):
        rect(o, px, 2, px + 2, H - 1, gry); rect(o, px + 2, 2, px + 2, H - 1, gryd)
    rect(o, 0, D, 31, D + 3, yel); rect(o, 0, D + 3, 31, D + 3, yeld)
    for y in range(D + 9, H - 1, 6): rect(o, 4, y, 27, y, gryd)
    rect(o, 0, 1, 31, 2, red); rect(o, 0, 2, 31, 2, redd)          # the handrail top bar
    for x in range(6, 28, 6): rect(o, x, 3, x, D - 1, gryd)        # rail bars
    # the slide: a red chute 45 degrees from (32, D) to (63, D + 31), 5 px thick, side wall below it
    for i in range(32):
        x, y = 32 + i, D + i
        put(o, x, y, redl); put(o, x, y + 1, red); put(o, x, y + 2, red); put(o, x, y + 3, redd)
    for i in range(0, 30, 10):                                     # its two little legs
        rect(o, 34 + i, D + 4 + i, 35 + i, H - 1, gryd)
    return outline(trim(o))

def park_frame():
    # the climbing frame (r6/levels: wider, with a step): two posts (level x 2712 and 2796, y 120-184), two bars
    # (y 160: 2712-2784, y 136: 2724-2800) and a low step inside it (2716-2732, top y 172), metal pipes in blue.
    # Image origin = level (2711, 119), the FRAME prop's x0 - 1. (Before: posts 2712 and 2772, bars 2712-2760 and
    # 2728-2776, no step; 60% of City Park's failures were on its 48 px bars.)
    W, H = 91, 66
    o = canvas(W, H)
    blu, blud, blul = hexc('3f7fb6'), hexc('2c5a85'), hexc('7fb4dd')
    def post(x):
        rect(o, x, 1, x + 3, H - 1, blu); rect(o, x, 1, x, H - 1, blul); rect(o, x + 3, 1, x + 3, H - 1, blud)
    def bar(x0, x1, y):
        rect(o, x0, y, x1, y + 3, blu); rect(o, x0, y, x1, y, blul); rect(o, x0, y + 3, x1, y + 3, blud)
    post(1); post(85)
    bar(1, 73, 41); bar(13, 88, 17)
    rect(o, 1, 1, 88, 2, blud)                                     # the top rail between the posts
    for x in range(21, 73, 9): rect(o, x, 21, x + 1, 40, blud)     # rungs between the bars
    rect(o, 5, 53, 20, H - 1, blud); rect(o, 6, 53, 19, 53, blul); rect(o, 6, 54, 19, H - 2, blu)   # the step
    return outline(trim(o))

# ---------------------------------------------------------------- Downtown
def town_ground():
    a = half(sheet('dt_ground'))
    a = rep(a, a.shape[0] - 1, 2, 0)
    return mirror_loop(palette(a, 12))

def town_facades():
    # the facades strip, halved (225 x 114), cut at the last whole house so it loops
    a = half(trim(sheet('dt_facades')))
    return deoutline(palette(a, 12))

def town_roofs():
    a = half(trim(sheet('dt_roofs')))
    return mirror_loop(deoutline(palette(a, 10)))

def town_crate():
    # apple crate 43 x 33 (1x): 11 columns and 5 rows cut out of the planks: 32 x 28, the box 16 rows under its
    # rim, the apples heaped above it
    a = piece('dt_props1', 0, 66, 42, 98)
    a = cut(a, 12, 28, 11)
    a = cut(a, 14, 24, 5, axis=0)
    return palette(a, 9)

def town_parasol():
    # a square market parasol seen from the side: the 64 px awning with 6 more rows of its stripes cut (12 tall)
    a = town_awning(64)
    return cut(a, 2, 8, 6, axis=0)

def town_table():
    # the bistro table top (rows 0-7 of the 50 x 42 render) on two thin legs at its sides (by hand), 26 tall
    a = piece('dt_props1', 48, 112, 97, 153)
    top = palette(a[:8], 6)
    W = top.shape[1]
    o = canvas(W, 26)
    leg, legd = hexc('3d4a4d'), hexc('262e30')
    for lx in (5, W - 8):
        rect(o, lx - 1, 7, lx + 3, 25, INK); rect(o, lx, 7, lx + 2, 25, leg); rect(o, lx + 2, 7, lx + 2, 25, legd)
        rect(o, lx - 3, 24, lx + 5, 25, INK); rect(o, lx - 2, 24, lx + 4, 24, leg)
    paste(o, top, 0, 0)
    return o

def town_stall():
    # market stall 66 x 54 (1x): the top tier of fruit boxes cut off (rows 0-8), 2 rows out of the counter front
    a = piece('dt_props1', 104, 102, 169, 155)
    a = a[9:]
    a = cut(a, 26, 40, 2, axis=0)
    return palette(a, 12)

def town_awning(w):
    # awning 74 x 27 (1x): 9 rows cut from the stripes (18 tall); stripes repeated (80) or cut (64) to the width
    a = piece('dt_props1', 148, 65, 221, 91)
    a = cut(a, 2, 14, 9, axis=0)
    if w > a.shape[1]:
        period = 10
        x = 30
        while a.shape[1] < w:
            n = min(period, w - a.shape[1])
            a = np.concatenate([a[:, :x + period], a[:, x:x + n], a[:, x + period:]], axis=1)
    elif w < a.shape[1]: a = cut(a, 20, 40, a.shape[1] - w)
    return palette(a, 6)

def town_statue():
    # bronze statue 70 x 123 (1x): hat, head, the pointing arm and chest (rows 0-43), the coat's hem (87-99) and the
    # legs (112-122): 68 tall, so the hat is at y 76, the arm's top at y 107/108 and the feet on the pedestal (144)
    a = piece('dt_statue', 0, 30, 69, 152)
    a = rows(a, (0, 44), (87, 100), (112, 123))
    return palette(a, 9)

def town_pedestal():
    # granite pedestal 77 x 77, halved (39 x 39), widened to 48 by repeating plain stone columns, 40 tall
    a = half(piece('dt_statue', 107, 72, 183, 148))
    a = rep(a, 4, 4, 1); a = rep(a, a.shape[1] - 6, 5, 1)
    a = rep(a, 20, 1, 0)
    return palette(a, 8)

def town_tram():
    # the tram 209 x 71, halved (105 x 36), two rows of the blue skirt cut: 105 x 34
    a = half(piece('dt_tram', 0, 69, 208, 139))
    a = cut(a, 20, 28, 2, axis=0)
    return palette(a, 12)

def town_door():
    return deoutline(palette(piece('dt_kioskset', 0, 78, 54, 135) if False else piece('dt_kioskset', 67, 78, 100, 135), 10))

def town_shelter():
    # tram shelter 76 x 49 (1x): 4 columns cut (72 wide), 1 row; its glass (transparent in the render) is filled
    # with a pale glass colour
    a = piece('dt_kioskset', 112, 87, 187, 135)
    a = cut(a, 30, 45, 4)
    a = cut(a, 20, 30, 1, axis=0)
    a = palette(a, 9)
    H, W = a.shape[:2]
    filled = ndimage.binary_fill_holes(a[..., 3] > 0)
    glass, glassl = hexc('b9cbd3'), hexc('d7e3e8')
    for y, x in zip(*np.nonzero(filled & (a[..., 3] == 0))):
        put(a, x, y, glassl if (x + 2 * y) % 23 < 2 else glass)
    # the open band under the roof between the posts is glass too (rows 5..last-6)
    return a

def town_kiosk():
    # kiosk 55 x 47 (1x): 13 columns cut from the shutter (42 wide), 10 rows: 42 x 37 (40 x 36 + outline)
    # It came out nearly black-green: lifted to a mid-tone green (all but its outline), so Pepper (a black dog)
    # stands out in front of it
    a = piece('dt_kioskset', 0, 89, 54, 135)
    a = cut(a, 14, 30, 13)
    a = cut(a, 10, 22, 10, axis=0)
    a = palette(a, 11)
    on = a[..., 3] > 0
    L = a[..., :3].astype(int).sum(2)
    ink = on & (L <= np.percentile(L[on], 12))
    lift = np.clip(a[..., :3].astype(int) * 1.45 + 28, 0, 255).astype(np.uint8)
    a[on & ~ink, :3] = lift[on & ~ink]
    return a

def town_sign():
    return deoutline(palette(piece('dt_kioskset', 195, 98, 213, 135), 7))

def town_shopsign():
    # the shop sign: an iron bar (the ledge, 40 x 4) from its post, with a painted board hanging under it (a pretzel,
    # the old bakers' sign), by hand. Origin = level (559, 75): the bar's top is row 5 (y 80); post at the right.
    W, H = 46, 110
    o = canvas(W, H)
    iron, ironl = hexc('3b3d42'), hexc('6a6e75')
    gold, goldd, board, boardd = hexc('e2b54a'), hexc('a87a26'), hexc('7a3b2a'), hexc('592a1d')
    rect(o, 40, 1, 43, H - 1, iron); rect(o, 40, 1, 40, H - 1, ironl)   # post (x 599-602)
    rect(o, 38, 0, 45, 1, iron)                                    # its cap
    rect(o, 1, 5, 41, 8, iron); rect(o, 1, 5, 41, 5, ironl)        # the bar (y 80-83)
    for x in range(30, 40): put(o, x, 9 + (x - 30) // 2, iron)     # a bracket stay
    for x in (8, 26): rect(o, x, 9, x, 11, iron)                   # chains
    rect(o, 4, 12, 30, 27, board); rect(o, 4, 27, 30, 27, boardd); rect(o, 4, 12, 30, 12, gold)
    # a pretzel in gold: two loops and a twist
    for (cx, cy) in ((13, 19), (21, 19)):
        for t in range(0, 360, 20):
            import math
            put(o, round(cx + 4 * math.cos(math.radians(t))), round(cy + 4 * math.sin(math.radians(t))), gold)
    for x in range(12, 23): put(o, x, 24 - abs(x - 17) // 2, goldd)
    return outline(trim(o))

def stone_block(w, h, top=True, seed=0):
    # granite blocks for the fountain (colours from the bridge pier art): courses 8 high, joints staggered
    st, stl, std, joint = hexc('9d958d'), hexc('c1b9b0'), hexc('77706a'), hexc('5e5852')
    o = canvas(w, h)
    rng = np.random.RandomState(seed)
    for y in range(h):
        for x in range(w):
            c = st
            if (y % 8) == 7: c = joint
            elif ((x + (y // 8) * 9) % 18) == 0: c = joint
            elif (y % 8) == 0: c = stl
            elif rng.rand() < 0.06: c = std
            put(o, x, y, c)
    if top: rect(o, 0, 0, w - 1, 1, stl)
    return o

def town_rim():
    # a basin rim (16 x 16 box): a granite block with a coping stone on top, outlined
    o = stone_block(16, 16, seed=2)
    rect(o, 0, 0, 15, 2, hexc('c1b9b0')); rect(o, 0, 3, 15, 3, hexc('77706a'))
    return outline(o)

def town_bowl():
    # the fountain: bowl 32 wide (top y 160) on a column down into the water, the spout above (decoration,
    # drawn in scene.lua: water jets). Image: the bowl's lip is row 1 (y 160 after the outline row).
    W, H = 32, 80
    o = canvas(W, H)
    st, stl, std = hexc('a29a92'), hexc('c9c1b8'), hexc('6f6862')
    rect(o, 0, 0, 31, 2, stl); rect(o, 0, 3, 31, 6, st); rect(o, 2, 7, 29, 9, st); rect(o, 5, 10, 26, 11, std)
    rect(o, 2, 6, 29, 6, std)
    col = stone_block(14, H - 12, top=False, seed=5)
    paste(o, col, 9, 12)
    rect(o, 9, 12, 9, H - 1, stl); rect(o, 22, 12, 22, H - 1, std)
    return outline(o)

def town_spout():
    # the spout on the bowl: a small stone finial (12 x 10), decoration; the jets are drawn in code
    o = canvas(12, 12)
    st, stl, std = hexc('a29a92'), hexc('c9c1b8'), hexc('6f6862')
    rect(o, 4, 0, 7, 1, stl); rect(o, 3, 2, 8, 3, st); rect(o, 5, 4, 6, 9, st); rect(o, 2, 10, 9, 11, std)
    return o

def town_bollard():
    # a dark granite bollard top for the foreground frame (rises into the bottom of the screen from y 221)
    W, H = 16, 40
    o = canvas(W, H)
    st, stl, std = hexc('3d3a38'), hexc('5b5753'), hexc('2a2827')
    for y in range(H):
        hw = 7 if y > 4 else [4, 6, 7, 7, 7][y]
        for x in range(8 - hw, 8 + hw):
            put(o, x, y, stl if x < 8 - hw + 2 else (std if x >= 8 + hw - 3 else st))
    rect(o, 2, 8, 13, 8, std)
    return o

# ---------------------------------------------------------------- set pieces added by the level fixes (preview/art)
def park_willow(extra=0):
    # weeping willow 130 x 168 (1x), halved (65 x 84); extra rows of trunk for a taller one. Decoration.
    a = half(trim(sheet('cp_willow')))
    if extra: a = rep(a, 70, extra, 0)
    return deoutline(palette(a, 10))

def park_winch():
    # the park keeper's rope winch on the far bank (20 x 14, decoration): a wooden drum with rope coils on two
    # A-frame legs, a crank handle. By hand.
    o = canvas(20, 14)
    wood, woodd, woodl = hexc('8a5a34'), hexc('5e3d22'), hexc('b07a4a')
    rope, roped, iron = hexc('d8c79a'), hexc('a8956a'), hexc('4a4d52')
    for i in range(10):                                           # A-frame legs
        put(o, 3 + i // 3, 13 - i, woodd); put(o, 16 - i // 3, 13 - i, woodd)
    rect(o, 4, 4, 15, 9, wood); rect(o, 4, 4, 15, 4, woodl); rect(o, 4, 9, 15, 9, woodd)   # the drum
    for x in range(5, 15, 2): rect(o, x, 5, x, 8, rope)           # rope coils
    for x in range(6, 15, 2): rect(o, x, 5, x, 8, roped)
    rect(o, 2, 6, 3, 7, iron); rect(o, 0, 2, 1, 7, iron); rect(o, 0, 1, 2, 2, iron)   # the crank
    rect(o, 2, 13, 17, 13, woodd)                                 # the footing
    return o

def park_hollowlog():
    # the hollow log (42 x 27: level 1244-1286, y 158-184): a fallen trunk with rounded bark (Pepper stands on its
    # top), both cut ends showing light wood rings round a dark hole low down (she crawls through it). The body hides
    # what is inside. Colours from the log art. By hand, then the 1 px outline.
    W, H = 40, 25
    o = canvas(W, H)
    bark, barkd, barkl = hexc('7b4f30'), hexc('54341f'), hexc('9c6a43')
    cutw, cutd = hexc('d9b483'), hexc('a9824f')
    dark = hexc('21160f')
    for y in range(H):
        inset = 2 if y in (0, H - 1) else (1 if y in (1, H - 2) else 0)
        for x in range(inset, W - inset): put(o, x, y, bark)
    rect(o, 2, 0, W - 3, 0, barkl); rect(o, 1, 1, W - 2, 1, barkl)
    for i, y in enumerate(range(5, H - 3, 4)):                    # bark grooves, broken
        for x in range(4 + (i * 5) % 7, W - 6, 9): rect(o, x, y, x + 4, y, barkd)
    rect(o, 2, H - 2, W - 3, H - 2, barkd)
    for cx in (4, W - 5):                                         # the cut ends: rings and the hole
        for y in range(H):
            for x in range(cx - 4, cx + 5):
                dx, dy = (x - cx) / 4.6, (y - 12) / 12.6
                r = dx * dx + dy * dy
                if r <= 1:
                    hx, hy = (x - cx) / 3.2, (y - 15) / 8.6
                    if hx * hx + hy * hy <= 1 and y >= 8: put(o, x, y, dark)
                    elif r > 0.72: put(o, x, y, cutd)
                    else: put(o, x, y, cutw)
    return outline(o)

def town_tub():
    # the flower tub before the pedestal (32 wide, top y 156, 28 tall): River Walk's square planter, 12 columns
    # cut out of its middle and 2 rows out of its planks (its rim stays row 18)
    a = np.array(Image.open(os.path.join(OUT, 'planter_sq.png')).convert('RGBA'))
    a = cut(a, 14, 28, 12)
    a = cut(a, 26, 40, 2, axis=0)
    return a

def town_house(i):
    # the three houses of the rooftop route (crisp obstacles: their balconies are ledges). 1x, natural widths, the
    # heights fitted to the boxes: 118 (grey), 126 (red, 2 rows cut), 118 (ochre, 13 rows cut between floors)
    if i == 0: return palette(piece('dt_houses', 147, 45, 200, 162), 11)
    if i == 1:
        a = piece('dt_houses', 70, 35, 127, 162)
        return palette(cut(a, 90, 100, 2, axis=0), 11)
    a = piece('dt_houses', 0, 36, 51, 166)
    return palette(cut(a, 62, 82, 13, axis=0), 11)

def town_tier():
    # the fountain's top tier: a stone dish 48 wide (its top the ledge, y 104) on a column down to the bowl (y 160),
    # the column wider at its foot (the old spout). Origin = level (1447, 103). By hand, then the outline.
    W, H = 48, 56
    o = canvas(W, H)
    st, stl, std = hexc('a29a92'), hexc('c9c1b8'), hexc('6f6862')
    rect(o, 0, 0, W - 1, 1, stl); rect(o, 0, 2, W - 1, 3, st); rect(o, 3, 4, W - 4, 4, std); rect(o, 8, 5, W - 9, 6, std)
    rect(o, 20, 7, 27, H - 1, st); rect(o, 20, 7, 20, H - 1, stl); rect(o, 27, 7, 27, H - 1, std)
    for y in range(12, H - 6, 9): rect(o, 20, y, 27, y, std)
    rect(o, 18, H - 8, 29, H - 1, st); rect(o, 18, H - 8, 29, H - 8, stl); rect(o, 29, H - 8, 29, H - 1, std)
    return outline(o)

if __name__ == '__main__':
    import sys
    def save(a, n):
        Image.fromarray(a).save(os.path.join(OUT, n))
        print(n, a.shape[1], 'x', a.shape[0], len(np.unique(a[a[..., 3] > 0][:, :3], axis=0)), 'colours')
    jobs = {
        'park_ground.png': park_ground, 'park_treeline.png': park_treeline,
        'park_tree1.png': lambda: park_tree(0), 'park_tree2.png': lambda: park_tree(1),
        'park_gate.png': park_gate, 'park_swings.png': park_swings, 'park_bush.png': park_bush,
        'park_log.png': park_log, 'park_leaves.png': park_leaves, 'park_leaves_flat.png': park_leaves_flat,
        'park_table.png': park_table, 'park_hedge.png': park_hedge, 'park_stone.png': park_stone,
        'park_boat.png': park_boat, 'park_cart.png': park_cart, 'park_oak.png': park_oak,
        'park_slide.png': park_slide, 'park_frame.png': park_frame,
        'town_ground.png': town_ground, 'town_facades.png': town_facades, 'town_roofs.png': town_roofs,
        'town_crate.png': town_crate, 'town_parasol.png': town_parasol, 'town_table.png': town_table,
        'town_stall.png': town_stall, 'town_awning80.png': lambda: town_awning(80),
        'town_awning64.png': lambda: town_awning(64), 'town_statue.png': town_statue,
        'town_pedestal.png': town_pedestal, 'town_tram.png': town_tram, 'town_door.png': town_door,
        'town_shelter.png': town_shelter, 'town_kiosk.png': town_kiosk, 'town_sign.png': town_sign,
        'town_shopsign.png': town_shopsign, 'town_rim.png': town_rim, 'town_bowl.png': town_bowl,
        'town_spout.png': town_spout, 'town_bollard.png': town_bollard,
        'park_willow.png': park_willow, 'park_willow_tall.png': lambda: park_willow(8),
        'park_winch.png': park_winch, 'park_hollowlog.png': park_hollowlog,
        'town_tub.png': town_tub, 'town_house1.png': lambda: town_house(0), 'town_house2.png': lambda: town_house(1),
        'town_house3.png': lambda: town_house(2), 'town_tier.png': town_tier,
    }
    only = sys.argv[1:]
    for n, f in jobs.items():
        if not only or any(o in n for o in only): save(f(), n)
