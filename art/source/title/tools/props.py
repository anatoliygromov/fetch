"""props: the title background's thin built objects redrawn by rule (25 Oct).
    python3 art/source/title/tools/props.py        (from the repo root), then build_title_regrid.py
Reads art/source/title/regrid/pre_props/bg_noplate_320.png (the background as it was after destray) and writes
art/source/title/regrid/bg_noplate_320.png. Sampling the painting broke thin man-made objects (a lamp post is
5 px wide, a mullion 1 px), so they are drawn here once, cleanly, on the game grid, from positions and widths
measured on the painting (source_title/title_original.png, 7.5 painting px per game px):

  Left lamp (axis x 33): finial, roof with a dark shade face, a mid face and a 2 px lit band that runs down the
  roof's right edge as an even 1:1 staircase to the brim's lit end, a tan lip; lantern with two glass panes,
  a 1 px dark mullion and a 1 px frame tapering in even 4-row steps; glow orange / amber / cream (amber at the
  panes' outer columns); rim, collar, neck and ring; a straight post x 31..35 (outline, two body columns, ONE
  1 px highlight at x 34, outline); lower moulding, base and plinth (the highlight runs on at x 34).
  Right lamp (axis x 287, the same design at about a third of the size): finial, roof, brim with its lit end,
  two 1 px panes (one yellow each) with the mullion and frame, rim, a 2 px post (outline, a dimmer highlight),
  base and plinth.

The old lamp pixels outside the new shapes take the painting's colour there, chosen among the colours that occur
round them (never a blend, never a new colour); the sky right round the left post is cleaned the same way.
Pepper's pixels (pepper_region.png alpha, and her painted outline and bandana under it) are never painted."""
import os
import numpy as np
from PIL import Image
from skimage.color import rgb2lab
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from destray import stray_mask

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'art', 'source', 'title', 'regrid')
PAINTING = os.path.join(ROOT, 'source_title', 'title_original.png')
W, H = 320, 240

C = {  # every colour is one the background already uses
    'O': (4, 15, 46),      # outline / shade
    'D': (19, 39, 74),     # dark body
    'B': (35, 45, 70),     # body
    'M': (67, 63, 81),     # roof mid face
    'H': (111, 92, 93),     # highlight column (the painting's mauve)
    'L': (127, 104, 99),   # lit face
    'T': (228, 183, 144),  # tan lip
    'r': (233, 134, 49),   # glow: orange
    'a': (253, 181, 63),   # glow: amber
    'c': (254, 226, 180),  # glow: cream
    'y': (255, 227, 96),   # glow: yellow (the small lantern's panes, one colour each)
    'S': (54, 54, 80),     # bench slat
    'Q': (80, 75, 98),     # bin lid top, the seat's back edge
    'P': (93, 73, 74),     # bin lid and base ring, lit
    'R': (127, 90, 81),    # boat deck (wood)
    'k': (210, 126, 90),   # mast (orange wood)
    'w': (255, 245, 206),  # sail, rigging
    'g': (75, 91, 125),    # mast (grey)
    't': (204, 163, 143),  # mast tip
}

# ---- left lamp: rows (y, x0, pattern); '.' leaves the background ----
POST_L = 'ODDHO'
LEFT_TOP = [
    (42, 33, 'O'),
    (43, 33, 'O'),
    (44, 32, 'OOO'),
    (45, 32, 'OOO'),
    (46, 31, 'OOOOO'),
    (47, 32, 'OOO'),
    (48, 31, 'OOOLO'),
    (49, 30, 'OOOOLLO'),
    (50, 29, 'OOOOOMLLO'),
    (51, 28, 'OOOOOOMMLLO'),
    (52, 27, 'OOOOOOOMMMLLO'),
    (53, 26, 'OOOOOOOOTTTTLLO'),
    (54, 25, 'OOOOOOOOOMMMMMLLO'),
    (55, 24, 'OOOOOOOOOOOOOOOOLLO'),
    (56, 24, 'OOOOOOOOOOOOOOOOOOO'),
    (57, 26, 'OrrrrrrOrrrrrrO'),
    (58, 26, 'OrrrrrrOrrrrrrO'),
    (59, 26, 'OaaaaaaOaaaaaaO'),
    (60, 26, 'OaaaaaaOaaaaaaO'),
    (61, 27, 'OaccccOccccaO'),
    (62, 27, 'OaccccOccccaO'),
    (63, 27, 'OaccccOccccaO'),
    (64, 27, 'OaccccOccccaO'),
    (65, 28, 'OacccOcccaO'),
    (66, 28, 'OaaaaOaaaaO'),
    (67, 28, 'OaaaaOaaaaO'),
    (68, 28, 'OaaaaOaaaaO'),
    (69, 28, 'OOOOBBBBBBO'),
    (70, 27, 'OOOOOOOOOOOOO'),
    (71, 27, 'OOOOOOOOOOOOO'),
    (72, 29, 'OOOOOOOOO'),
    (73, 30, 'OOOBBBO'),
    (74, 31, POST_L),
    (75, 31, POST_L),
    (76, 29, 'OOOBBHBBO'),
    (77, 29, 'OOOBBHBBO'),
    (78, 29, 'OOOOOOOOO'),
    (79, 30, 'OOOOOOO'),
] + [(y, 31, POST_L) for y in range(80, 171)] + [
    (171, 29, 'OOOLLLLLO'),
    (172, 28, 'OOOOOOOOOOO'),
    (173, 28, 'OOOBBLLLBBO'),
] + [(y, 29, 'ODDBBBBBO') for y in range(174, 179)] + [(y, 29, 'ODDBHBBBO') for y in range(179, 187)] + [
    (187, 28, 'OMMMMMMMMMO'),
] + [(y, 28, 'ODDDBHH') for y in range(188, 192)]   # right of x 34 Pepper's outline, then the pavement

# ---- right lamp ----
RIGHT = [
    (129, 287, 'O'),
    (130, 287, 'O'),
    (131, 286, 'OLO'),
    (132, 284, 'OOOOOLO'),
    (133, 285, 'OOOOO'),
    (134, 285, 'OyOyO'),
    (135, 285, 'OyOyO'),
    (136, 285, 'OyOyO'),
    (137, 286, 'OOO'),
] + [(y, 286, 'OM') for y in range(138, 164)] + [
    (164, 285, 'OBMO'),
    (165, 285, 'OBMO'),
    (166, 285, 'OBMO'),
    (167, 284, 'OMMMMO'),
]
RIGHT_BOX = (284, 128, 291, 168)    # the old right lamp: its navy, its orange block, the blocks at its base
OLD_RIGHT = [(0x15, 0x34, 0x6a), (0x3b, 0x40, 0x5e), (0x19, 0x30, 0x59), (0x01, 0x25, 0x55), (0xfd, 0xb5, 0x3f),
             (0x13, 0x27, 0x4a), (0xa2, 0x89, 0x8c)]
OLD_RIGHT_POST = (285, 128, 288, 168)  # (35,45,70) is also a bush colour: only on the old post's columns

# ---- bench (its left end; the screen cuts it at x 319): back with three slats (lit top edges L, H, M), its end
# frame x 299, the seat (back edge, lit top, front, underside), a cross bar and two cast legs ----
BENCH = [(183, 299, 'O'), (184, 299, 'O' + 'L' * 20)] + [(y, 299, 'O' + 'S' * 20) for y in (185, 186, 187)] + [
    (188, 299, 'O' * 21), (189, 299, 'O' + 'H' * 20)] + [(y, 299, 'O' + 'S' * 20) for y in (190, 191, 192)] + [
    (193, 299, 'O' * 21), (194, 299, 'O' + 'M' * 20), (195, 299, 'O' + 'B' * 20), (196, 299, 'O' * 21),
    (197, 295, 'O' + 'Q' * 24), (198, 295, 'O' + 'L' * 24), (199, 295, 'O' + 'S' * 24), (200, 295, 'O' + 'D' * 24),
    (201, 295, 'O' * 25), (202, 297, 'O' * 8), (203, 299, 'OO'), (203, 302, 'OO')] + [
    (y, 298, 'OO') for y in (204, 205, 206)] + [(y, 297, 'OO') for y in (207, 208, 209)] + [
    (y, 302, 'OO') for y in range(204, 210)] + [(210, 296, 'OOO')]
BENCH_OLD = [((300, 183, 320, 184), [(127, 90, 81)]), ((295, 202, 306, 212), [(4, 15, 46), (7, 16, 40), (1, 17, 53), (19, 39, 74), (35, 45, 70), (54, 54, 80),
                                     (0, 0, 0), (0, 1, 19), (152, 121, 108), (97, 86, 101)])]

# ---- bin by the railing: lid (top, rim face lit on the right, rim), shadow, a light ring, a body of four 2 px
# slats between dark lines (shade slat D, two body slats B, the lit slat M), base ring lit on the right, base ----
BIN = [(175, 276, 'O' + 'Q' * 12 + 'O'), (176, 276, 'O' + 'B' * 5 + 'P' * 7 + 'O'), (177, 275, 'O' * 16)] + [
    (y, 276, 'O' * 14) for y in (178, 179, 180)] + [(181, 276, 'O' * 6 + 'M' * 7 + 'O')] + [
    (y, 276, 'ODDOBBOBBOMMOO') for y in range(182, 204)] + [
    (204, 275, 'O' + 'D' * 6 + 'MMM' + 'PPPP' + 'OO'), (205, 275, 'O' + 'B' * 14 + 'O'), (206, 275, 'O' * 16),
    (207, 275, 'O' * 16)]


def railing_post(x0):
    """The big railing posts, both the same: a 6 px shaft (outline, dark, body, light body, ONE highlight column,
    outline) from the cap to the kerb; cap top 4 px, cap 8 px lit on its right, collar."""
    return [(175, x0 + 1, 'OOOO'), (176, x0 + 1, 'OOOO'), (177, x0 - 1, 'ODDDLLLO'), (178, x0 - 1, 'O' * 8)] + [
        (y, x0, 'ODBSMO') for y in range(179, 203)]


POSTS = railing_post(186) + railing_post(215)
POSTS_OLD = [((221, 177, 222, 203), [(1, 17, 53)]), ((220, 175, 221, 177), [(67, 63, 81)])]   # the old right post
# was 7 px (x 215..221) and its top sat 1 px right; the left one already stood on x 186..191

# ---- boats: straight 1 px masts. Left boat (x 142): mast through the deck to the hull, the two rigging lines as
# even 3-row staircases, the boom. Small boat: mast x 178 between its two sails. Boat at x 256: the mast the full
# height (the painting's gap below the sail tops is an artefact) with its tip, and its hull (deck, navy). ----
BOATS = [(y, 142, 'k') for y in range(141, 157)] + [
    (y, 141, 'w') for y in (144, 145, 146)] + [(y, 140, 'w') for y in (147, 148, 149)] + [
    (y, 139, 'w') for y in (150, 151, 152, 153)] + [
    (y, 143, 'w') for y in (144, 145, 146)] + [(y, 144, 'w') for y in (147, 148, 149)] + [
    (y, 145, 'w') for y in (150, 151, 152)] + [(153, 146, 'w'), (154, 139, 'kkk.kkkk')] + [
    (145, 179, 'w')] + [(y, 179, 'w') for y in range(146, 153)] + [(y, 178, 'g') for y in range(147, 158)] + [
    (y, 177, 'wgww') for y in (153, 154)] + [(y, 175, 'wwwgwww') for y in (155, 156)] + [
    (151, 177, 'wgw'), (152, 177, 'wgw'), (157, 178, 'gwww')] + [
    (135, 256, 't'), (136, 256, 't')] + [(y, 256, 'g') for y in range(137, 155)] + [
    (155, 251, 'R' * 13), (156, 251, 'B' * 12)]
BOATS_OLD = [((137, 140, 149, 155), [(255, 245, 206), (229, 145, 80), (152, 121, 108), (97, 86, 101)]),
             ((174, 150, 182, 158), [(255, 245, 206), (75, 91, 125), (78, 115, 160)]),
             ((257, 136, 258, 139), [(204, 163, 143)]),
             ((250, 154, 265, 157), [(228, 183, 144), (127, 104, 99), (54, 54, 80), (35, 45, 70)])]


def lamp_mask(a, box, cols):
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), bool)
    sub = a[y0:y1, x0:x1]
    for c in cols:
        m[y0:y1, x0:x1] |= (sub == np.array(c)).all(-1)
    return m


def draw(a, rows, keep):
    """Paints the rows; returns the mask of painted pixels. keep: pixels never painted."""
    m = np.zeros((H, W), bool)
    for y, x0, pat in rows:
        for i, ch in enumerate(pat):
            x = x0 + i
            if ch == '.' or keep[y, x]: continue
            a[y, x] = C[ch]; m[y, x] = True
    return m


class Painting:
    def __init__(self, pal):
        P = np.array(Image.open(PAINTING).convert('RGB')).astype(float)
        self.P = P; self.sx = P.shape[1] / W; self.sy = P.shape[0] / H

    def cell(self, x, y):
        cx, cy = (x + 0.5) * self.sx, (y + 0.5) * self.sy
        return np.median(self.P[int(cy - 2):int(cy + 3), int(cx - 2):int(cx + 3)].reshape(-1, 3), 0)


def refill(a, holes, fixed, paint):
    """Each hole pixel takes the colour of the nearest kept pixel to its left, right, above or below (the
    background the old lamp stood in front of), choosing among those four the one nearest the painting's colour at
    its cell (Lab). Never a blend: only colours already round it."""
    out = a.copy()
    ok = ~holes & ~fixed
    for y, x in zip(*np.nonzero(holes)):
        cand = []
        for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            yy, xx = y + dy, x + dx
            while 0 <= yy < H and 0 <= xx < W and not ok[yy, xx] and abs(yy - y) + abs(xx - x) < 12:
                yy += dy; xx += dx
            if 0 <= yy < H and 0 <= xx < W and ok[yy, xx]: cand.append(a[yy, xx])
        if not cand: continue
        cand = np.array(cand)
        lab = rgb2lab(cand[None] / 255.0)[0]
        t = rgb2lab(paint.cell(x, y)[None, None] / 255.0)[0, 0]
        out[y, x] = cand[((lab - t) ** 2).sum(1).argmin()]
    return out


def tidy(a, region, fixed, passes=3):
    """Specks in a region (a pixel whose colour none of its 4 neighbours shares) take the most common colour of
    their 8 neighbours. fixed pixels (the lamps) are never changed and never counted."""
    for _ in range(passes):
        n = 0; b = a.copy()
        for y, x in zip(*np.nonzero(region & ~fixed)):
            me = tuple(a[y, x])
            if any(tuple(a[yy, xx]) == me for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))): continue
            cnt = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and not fixed[yy, xx]:
                        c = tuple(a[yy, xx]); cnt[c] = cnt.get(c, 0) + 1
            if cnt:
                b[y, x] = max(cnt.items(), key=lambda t: t[1])[0]; n += 1
        a = b
        if not n: break
    return a


def main():
    src = np.array(Image.open(os.path.join(SRC, 'pre_props', 'bg_noplate_320.png')).convert('RGBA'))
    a = src[..., :3].copy()
    pep = np.array(Image.open(os.path.join(SRC, 'pepper_region.png')))[..., 3] > 0
    ai = a.astype(int)
    lum = ai @ np.array([30, 59, 11]) // 100
    yy, _ = np.mgrid[0:H, 0:W]
    # Pepper as painted in the background under her layer: her near-black outline and the pink bandana (low down)
    pep_bg = (yy > 165) & ((lum < 12) | ((ai[..., 0] > 180) & (ai[..., 1] < 130) & (ai[..., 2] > 80)))
    keep = pep | pep_bg
    paint = Painting(None)

    # left lamp: the old lamp's pixels = its navy and mauve colours (and the glow, in the lantern) inside the
    # columns it spans; the branch (browns), the tree (greens), the wall and the sky keep theirs
    navy = [(4, 15, 46), (7, 16, 40), (1, 17, 53), (19, 39, 74), (35, 45, 70), (54, 54, 80), (59, 64, 94),
            (67, 63, 81), (81, 65, 68), (64, 54, 63), (111, 92, 93), (127, 104, 99), (97, 86, 101), (80, 75, 98)]
    glow = [(233, 134, 49), (253, 181, 63), (254, 226, 180), (255, 227, 96)]
    old = lamp_mask(a, (25, 40, 45, 80), navy) | lamp_mask(a, (25, 40, 45, 75), glow) | \
        lamp_mask(a, (28, 80, 39, 192), navy[:9] + navy[10:]) | lamp_mask(a, (26, 170, 28, 177), navy)
    old &= ~keep
    # the branch above the roof keeps its colours (browns are not in the list); the tree's dark greens neither
    newL = draw(a, LEFT_TOP, keep)
    holes = old & ~newL
    a = refill(a, holes, newL | keep, paint)

    # right lamp
    oldR = (lamp_mask(a, RIGHT_BOX, OLD_RIGHT) | lamp_mask(a, OLD_RIGHT_POST, [(0x23, 0x2d, 0x46)])) & ~keep
    newR = draw(a, RIGHT, keep)
    a = refill(a, oldR & ~newR, newR | keep, paint)

    # bench, bin, railing posts, boats: the same way (old pixels by colour inside their boxes)
    new_all = newL | newR; old_all = holes | oldR
    for name, rows, olds in (('bench', BENCH, BENCH_OLD), ('bin', BIN, []), ('posts', POSTS, POSTS_OLD),
                             ('boats', BOATS, BOATS_OLD)):
        oldm = np.zeros((H, W), bool)
        for box, cols in olds: oldm |= lamp_mask(a, box, cols)
        oldm &= ~keep & ~new_all
        newm = draw(a, rows, keep)
        a = refill(a, oldm & ~newm, newm | new_all | keep, paint)
        print(name, int(newm.sum()), 'px, refilled', int((oldm & ~newm).sum()))
        new_all |= newm; old_all |= oldm & ~newm

    # right round every rebuilt object (the sky by the left post above all): specks take their neighbours' colour
    fixed = new_all | keep
    from scipy import ndimage
    near = ndimage.binary_dilation(new_all | old_all, iterations=2)
    a = tidy(a, near & ~fixed, fixed)
    # then any 1-2 px cluster left round them (destray's rule) takes its commonest non-object neighbour colour
    for _ in range(4):
        rgba = np.dstack([a, src[..., 3]])
        m = stray_mask(rgba, protect=fixed | ~near)
        if not m.any(): break
        b = a.copy()
        for y, x in zip(*np.nonzero(m)):
            cnt = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and not fixed[yy, xx] and tuple(a[yy, xx]) != tuple(a[y, x]):
                        c = tuple(a[yy, xx]); cnt[c] = cnt.get(c, 0) + 1
            if cnt: b[y, x] = max(cnt.items(), key=lambda t: t[1])[0]
        a = b
    pal = set(map(tuple, src[..., :3].reshape(-1, 3).tolist()))
    assert all(c in pal for c in C.values()), 'a colour not in the background palette'
    assert set(map(tuple, a.reshape(-1, 3).tolist())) <= pal, 'a new colour'

    out = np.dstack([a, src[..., 3]]).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(SRC, 'bg_noplate_320.png'))
    print('left lamp', int(newL.sum()), 'px, refilled', int(holes.sum()), '| right lamp', int(newR.sum()),
          'px, refilled', int((oldR & ~newR).sum()))


if __name__ == '__main__':
    main()
