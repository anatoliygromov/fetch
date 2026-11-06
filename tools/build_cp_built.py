#!/usr/bin/env python3
"""build_cp_built.py: City Park (tall) pieces built by rule, 0 credits (art/cp-built-06nov, 6 Nov 2026).

  python3 -I tools/build_cp_built.py          -> riverwalk/art/scene/*.png, riverwalk/cp_built.lua, art/source/<name>/

The BIBLE's crispness bar for anything repeated: each part (plank end, post, rope twist, leg, brace, brick, bar,
chain link, rose) is drawn once as a 2 to 4 colour sprite and stamped on an integer grid. Flat fills, straight
lines straight, light from the upper left. True scale, 46 px a metre on Pepper's line. Front-on: a front and a thin
cap, no tops seen from above. Obstacles (what Pepper stands on) have an unbroken 1 px ink outline (1d1816, the
slide's and frame's ink); decoration has none, its edge a darker shade of its own colour.

Pieces:
  park_gate        the park's entrance at x 0 (decoration, back, faded 28 % in scene.lua): two brick piers on a
                   granite plinth under a sandstone cap and ball, 2.1 m (96 px); a wrought iron double gate (painted the bench's green) 1.4 m wide
                   and 1.6 m high between them, the left leaf shut, the right one open (seen edge-on at its pier)
  park_swings      the swing set (decoration, back): a green steel frame 2.3 m high, legs splayed, two yellow seats
                   on chains, 0.45 m off the ground
  cp_walk<x>_*     the plank walks TREETOP WALK (x 704) and ALDER WALK (x 1968), rope bridges (art/cp-pond-06nov):
                   the deck (play, outlined, exactly the box plus its outline), a timber pylon at each end on dry
                   ground with a rope cable sagging between their tops and a hanger to the deck at every plank joint
                   (decoration, behind Pepper), the pylons' legs under the deck with knee braces (decoration, faded)
  cp_arbour_*      the rose arbour: each slat (play, outlined) and its two posts with a climbing rose and a swag of
                   roses under the slat (decoration, faded)
  cp_tower_*       the play tower: its yellow decks (play, outlined) and grey posts (outlined, as the slide's)

The tier pieces are drawn over exactly their boxes (read from the level's Tiled export); riverwalk/cp_built.lua
lists each image with its box, and scene.lua draws an image only when its box still matches (else the old code)."""
import os, re, sys, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, 'riverwalk/art/scene')
SRC = os.path.join(ROOT, 'art/source')
LEVEL = os.path.join(ROOT, 'riverwalk/level/tiled/citypark_tall.lua')


def hx(h):
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


INK = hx('1d1816')
# timber (walks): City Park palette v1 (art/palettes/citypark.gpl), one warm brown ramp
T_GAP, T_SHADE, T_DEEP, T_MID, T_LIGHT = hx('3e2421'), hx('5e4127'), hx('7b5c44'), hx('9a6333'), hx('b87e39')
T_RAILSH = hx('8b5232')                                  # the rail's shaded side (kept over luma 80: back decoration)
ROPE, ROPE_SH = hx('937d51'), hx('7b5c44')
IRON, IRON_HI = hx('2f3237'), hx('5d636f')
# white paint (arbour) and the coral rose, green leaves: palette v1
W_CAP, W_FACE, W_SH = hx('f7f9fa'), hx('f4eef3'), hx('b5a8d7')
R_DK, R_MID, R_LT = hx('ce3531'), hx('f78671'), hx('f7a67f')
G_DK, G_MID, G_LT = hx('2b4a38'), hx('3f6549'), hx('578058')
# the play tower: the slide's own yellow and greys (park_slide.png), the light from palette v1
Y_LT, Y_MID, Y_SH = hx('f4cc69'), hx('e8b83f'), hx('b5872a')
P_LT, P_MID = hx('9aa3ab'), hx('6b737b')
# brick and stone (gate): brick from palette v1; the sandstone is the winch keeper's khaki (park_keeper_winch.png,
# already in the park; not in palette v1: a new ramp, it stands only with the owner's approve)
B_LT, B_MID, B_ALT, B_SH, B_DK, MORTAR = hx('b57336'), hx('8f4631'), hx('84492c'), hx('723b2e'), hx('573029'), hx('937d51')
S_LT, S_MID, S_SH = hx('cfc19d'), hx('a79b6f'), hx('7a6c48')
GR_LT, GR_MID, GR_SH = hx('706860'), hx('504a46'), hx('494949')     # granite plinth: palette v1 greys
I_DK, I_MID, I_LT = hx('2b4a38'), hx('3f6549'), hx('578058')       # wrought iron, painted the bench's green
# swings: the bench's green (approved bench, also in palette v1), the slide's yellow seats, the slide's greys
SW_LT, SW_MID, SW_SH = hx('578058'), hx('40684a'), hx('2b4a38')


def canvas(w, h): return np.zeros((h, w, 4), np.uint8)


def rect(a, x, y, w, h, c):
    if w > 0 and h > 0: a[max(0, y):max(0, y + h), max(0, x):max(0, x + w)] = c


def put(a, x, y, c):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]: a[y, x] = c


def stamp(a, part, x, y):
    """part: HxWx4, transparent where alpha 0"""
    h, w = part.shape[:2]
    m = part[..., 3] > 0
    sub = a[y:y + h, x:x + w]; mm = m[:sub.shape[0], :sub.shape[1]]
    sub[mm] = part[:sub.shape[0], :sub.shape[1]][mm]


def save(name, a, folder=None, frames=None):
    folder = folder or name
    d = os.path.join(SRC, folder); os.makedirs(d, exist_ok=True)
    im = Image.fromarray(a, 'RGBA')
    im.save(os.path.join(SCENE, name + '.png')); im.save(os.path.join(d, name + '.png'))
    aseprite_io.write(os.path.join(d, name + '.aseprite'), frames or [a], layer=name)
    cols = len(np.unique(a[a[..., 3] > 0][:, :3], axis=0))
    print(f'{name:22} {a.shape[1]:4} x {a.shape[0]:<4} {cols:2} colours')
    return cols


# ---------------------------------------------------------------------------------------------- the level's boxes
def props():
    t = open(LEVEL).read()
    out = []
    for m in re.finditer(r'\{\s*id = (\d+),\s*name = "([^"]*)",\s*type = "props",\s*shape = "rectangle",\s*x = ([\d.-]+),'
                         r'\s*y = ([\d.-]+),\s*width = ([\d.]+),\s*height = ([\d.]+),.*?properties = \{(.*?)\}', t, re.S):
        i, n, x, y, w, h, pr = m.groups()
        P = dict(re.findall(r'\["(\w+)"\] = "?([^",\n]*)"?', pr))
        x, y, w, h = (int(float(v)) for v in (x, y, w, h))
        out.append(dict(id=int(i), name=P.get('name', n) if n == '' else n, x0=x, y0=y, x1=x + w, y1=y + h,
                        kind=P.get('kind'), layer=P.get('layer'), hidden=P.get('hidden') == 'true'))
    return out


def water_runs():
    t = open(LEVEL).read()
    seg = t[t.index('type = "tilelayer"'):]
    d = list(map(int, re.findall(r'\d+', re.search(r'data = \{(.*?)\}', seg, re.S).group(1))))
    W = 360; xs = set()
    for i, v in enumerate(d):
        if v == 2: xs.add(i % W)
    runs, x = [], 0
    for c in sorted(xs):
        if runs and c == runs[-1][1]: runs[-1][1] = c + 1
        else: runs.append([c, c + 1])
    return [(a * 8, b * 8) for a, b in runs]


FOOT, WORLD_H = 328, 384


# ------------------------------------------------------------------------------------------------ the plank walks
def pitch_for(w, post=4, lo=40, hi=48, want=44):
    """posts of width `post` from margin m to the far end's margin m, at an equal pitch; returns (m, pitch, n)"""
    best = None
    for m in range(2, 8):
        span = w - post - 2 * m
        for p in range(lo, hi + 1):
            if span % p == 0:
                k = (abs(p - want), m)
                if best is None or k < best[0]: best = (k, m, p, span // p + 1)
    return best[1:]


def walk_deck(w, bolts):
    """the deck: box w x 6 plus its 1 px outline. Row 0 the planks' lit top edge (the thin cap), row 1 their ends
    (7 px plank, a 1 x 2 px joint, pitch 8 from the box's left), row 2 their shadow on the stringer, rows 3-5 the stringer
    with a bolt (2 x 2) at each x in bolts (box columns: every fourth hanger, and a pylon under the box)"""
    a = canvas(w + 2, 8)
    rect(a, 0, 0, w + 2, 8, INK)
    for x in range(w):
        gap = x % 8 == 7 and x < w - 1
        a[1, x + 1] = T_GAP if gap else T_LIGHT
        a[2, x + 1] = T_GAP if gap else T_MID
        a[3, x + 1] = T_SHADE
        a[4, x + 1] = T_MID; a[5, x + 1] = T_MID
        a[6, x + 1] = T_DEEP
    for bx in bolts:
        bx += 1
        if 1 <= bx < w:
            a[4, bx] = IRON_HI; a[4, bx + 1] = IRON_HI; a[5, bx] = IRON; a[5, bx + 1] = IRON
    return a


def rope_rows(a, x0, x1, ytop, sag_of, phase_of):
    """a 2 px rope from column x0 to x1-1, its top row at ytop + sag; the twist: a 3 px diagonal stamp, its phase
    counted from each span's start so every span is the same pixels. Where the rope drops a row from one column to
    the next, the lower row of the column before is carried over, so the rope never breaks"""
    prev = None
    for x in range(x0, x1):
        y = ytop + sag_of(x); d = phase_of(x) % 3
        a[y, x] = ROPE_SH if d == 0 else ROPE
        a[y + 1, x] = ROPE if d == 2 else ROPE_SH
        if prev is not None and abs(y - prev) > 1:
            for yy in range(min(y, prev) + 2, max(y, prev)):
                a[yy, x if y > prev else x - 1] = ROPE_SH
        prev = y


# (art/cp-pond-06nov) The walks are rope bridges. The owner looked at the tall pond: "this thing looks weird". The
# legs ran from the high walkway straight down into the water every 46 px, in front of the willows and the bank,
# like cage bars (and cross braces made it worse). No tree trunk stands under either walk, so each is now hung, the
# way a child knows a rope bridge: a stout timber pylon at each end standing on dry ground (the bank or the path),
# one rope cable from pylon top to pylon top sagging over the water, and a hanger from it to the deck at every
# plank joint. Nothing stands in the water, nothing crosses the pond under the deck. The deck (what Pepper stands
# on) is the same box, still straight: it does not move.
PYLON, CAP = 6, 62                                     # a pylon's width; its top over the deck's top (1.35 m)
DROP = 30                                              # the cable: from 3 px under the pylon tops down to 32 px over the deck


def ground_top():
    """per 8 px column of the map: the top of its terrain (None: no terrain), and the set of wet columns"""
    t = open(LEVEL).read()
    seg = t[t.index('type = "tilelayer"'):]
    d = list(map(int, re.findall(r'\d+', re.search(r'data = \{(.*?)\}', seg, re.S).group(1))))
    W = 360; H = len(d) // W
    top = {}
    for c in range(W):
        for r in range(H):
            if d[r * W + c] == 1: top[c] = r * 8; break
    return top


def ground_lamps():
    """x of every lamp post standing on the path (the level's lamps on FOOT): a pylon keeps clear of them"""
    t = open(LEVEL).read()
    return [int(float(x)) for x, y in re.findall(r'type = "lamps",\s*shape = "\w+",\s*x = ([\d.-]+),\s*y = ([\d.-]+)', t)
            if int(float(y)) == FOOT]


def walk_pylons(p, water):
    """the two pylons (x of their left column, world): at the walk's end over dry ground, under the box (2 px in);
    where the end is over the water (or a lamp post stands there), just outside the box on the bank or the path"""
    x0, x1 = p['x0'], p['x1']
    top = ground_top(); lamps = ground_lamps()

    def dry(a, b):
        return (all(not any(r0 <= x < r1 for r0, r1 in water) and top.get(x // 8) for x in range(a, b))
                and not any(a - 8 < lx_ < b + 8 for lx_ in lamps))
    lx = x0 + 2 if dry(x0 + 2, x0 + 2 + PYLON) else x0 - PYLON
    rx = x1 - PYLON - 2 if dry(x1 - PYLON - 2, x1 - 2) else x1
    for x in (lx, rx):
        assert dry(x, x + PYLON), f"a pylon of the walk at {x0} would stand in the water at x {x}"
    return lx, rx, top[lx // 8], top[rx // 8]


def walk_hangers(p, lx, rx):
    """hangers at every other plank joint (box column 7 + 16 k) between the pylons, 4 px clear of each (at every
    joint they stood as close as a harp's strings over the canopies)"""
    return [x for x in range(p['x0'] + 7, p['x1'] - 1, 16) if lx + PYLON + 4 <= x < rx - 4]


def walk_rail(p, lx, rx, hangers):
    """the rail (decoration, behind Pepper, unfaded as the old rail's posts): each pylon's part over the deck, 6 px
    with a lit left side, a shaded right side and a rounded cap; the cable (2 px, twisted) lashed under each cap and
    sagging DROP px to the middle; a 1 px hanger from the cable to the deck at each plank joint. Image: from the left
    pylon (or the box) to the right one, CAP + 1 rows, its bottom row the row over the deck's outline (y0 - 2)"""
    ex0, ex1 = min(p['x0'], lx), max(p['x1'], rx + PYLON)
    H = CAP - 1
    a = canvas(ex1 - ex0, H)
    for px in (lx - ex0, rx - ex0):
        rect(a, px, 1, PYLON, H - 1, T_MID)               # the old rail posts' colours (kept over luma 80: back)
        rect(a, px, 1, 1, H - 1, T_LIGHT); rect(a, px + PYLON - 1, 1, 1, H - 1, T_RAILSH)
        rect(a, px + 1, 0, PYLON - 2, 1, T_LIGHT)         # the rounded cap
    c0, c1 = lx + PYLON - ex0, rx - ex0                 # the cable's span: pylon to pylon
    L = c1 - c0
    ytop = 4

    def sag(x):
        u = (x - c0 + 0.5) / L
        return int(round(DROP * 4 * u * (1 - u)))
    for hx_ in hangers:                                  # hangers first: the cable over them
        x = hx_ - ex0
        rect(a, x, ytop + sag(x) + 2, 1, H - (ytop + sag(x) + 2), ROPE_SH)
        rect(a, x, H - 2, 1, 2, ROPE)                    # the tie at the deck (a lighter knot)
    rope_rows(a, c0, c1, ytop, sag, lambda x: x - c0)
    for px in (lx - ex0, rx - ex0):                      # the lashing: a whipping round the pylon under its cap
        rect(a, px, ytop - 1, PYLON, 4, ROPE_SH); rect(a, px, ytop, PYLON, 1, ROPE)
    return a, ex0


def walk_legs(p, lx, rx, glx, grx):
    """each pylon's part under the deck, from the deck's bottom down to the ground it stands on (6 px, the same
    timber and colours as its part over the deck, so each pylon reads as one post: not faded, drawn with the walk in
    front of the willows), with a knee brace 1:1 up to the deck's stringer on the side the deck is (10 px, 2 px
    thick). Nothing else: no legs in the water, no tie across. Image: the rail's width, from y1 to the pylons' feet"""
    x0, x1, y1 = p['x0'], p['x1'], p['y1']
    ex0, ex1 = min(x0, lx), max(x1, rx + PYLON)
    H = max(glx, grx) - y1
    a = canvas(ex1 - ex0, H)
    for px, g in ((lx, glx), (rx, grx)):
        X = px - ex0; bot = g - y1
        rect(a, X, 0, PYLON, bot, T_MID)                  # the same timber as its part over the deck (unfaded)
        rect(a, X, 0, 1, bot, T_LIGHT); rect(a, X + PYLON - 1, 0, 1, bot, T_RAILSH)
        for side in (-1, 1):
            if (side < 0 and px - 10 < x0) or (side > 0 and px + PYLON + 10 > x1): continue   # only under the deck
            for i in range(10):
                bx = X - 1 - i if side < 0 else X + PYLON + i
                put(a, bx, 10 - i, T_MID); put(a, bx, 11 - i, T_RAILSH)
        rect(a, X - 1, bot - 2, PYLON + 2, 2, T_RAILSH)  # its foot: a sill on the ground
    return a, ex0


# ------------------------------------------------------------------------------------------------ the rose arbour
ROSE = np.array([[0, 1, 1, 1], [1, 3, 3, 1], [1, 3, 1, 1], [0, 1, 1, 0]])   # a 4 x 4 rose: coral petals, a red heart


def stamp_rose(a, x, y, flip=False):
    """the rose drawn once; flip: mirrored (its full top corner always towards the post it climbs)"""
    R = ROSE[:, ::-1] if flip else ROSE
    for j in range(4):
        for i in range(4):
            v = R[j, i]
            if v: put(a, x + i, y + j, {1: R_MID, 2: R_LT, 3: R_DK}[v])


def arbour_slat(w):
    """the slat Pepper stands on: box w x 6 plus the outline; a white painted beam, lit cap, a shade row under"""
    a = canvas(w + 2, 8)
    rect(a, 0, 0, w + 2, 8, INK)
    rect(a, 1, 1, w, 1, W_CAP); rect(a, 1, 2, w, 4, W_FACE); rect(a, 1, 6, w, 1, W_SH)
    return a


def arbour_posts(w, h):
    """its two posts (5 px, 0.11 m) at the slat's x0+2 and x1-7, from under the slat to the path; a climbing rose
    up each (a vine crossing the post every 12 px, leaves on alternate sides, a rose every 24 px); a swag of roses
    hanging under the slat between the posts. Image: the slat's width and 6 px each side (the leaves and roses
    outside the posts), from the slat's bottom (y1) to the path"""
    PAD = 6
    a = canvas(w + 2 * PAD, h)
    xs = (PAD + 2, PAD + w - 7)
    for px in xs:
        rect(a, px, 0, 5, h, W_FACE); rect(a, px, 0, 1, h, W_CAP); rect(a, px + 4, 0, 1, h, W_SH)
    TRI = (0, 1, 2, 3, 4, 4, 4, 3, 2, 1, 0, 0)          # the vine winds across the post's front, 12 px a turn
    for k, px in enumerate(xs):                          # the climbing rose
        for y in range(2, h - 3):
            put(a, px + TRI[y % 12], y, G_MID)
        for y in range(2, h - 6):
            f = 0 if y % 12 == 11 else 4 if y % 12 == 5 else None
            if f == 0:                                   # a leaf pair where the vine turns, outside the post
                rect(a, px - 2, y, 2, 2, G_LT)
                if (y // 12 + k) % 2 == 0: stamp_rose(a, px - 4, y + 2)
            elif f == 4:
                rect(a, px + 5, y, 2, 2, G_LT)
                if (y // 12 + k) % 2 == 1: stamp_rose(a, px + 5, y + 2, flip=True)
    # the swag: a vine that sags 4 px between the posts' inner faces, a rose every 8 px along it
    l, r = xs[0] + 5, xs[1]
    L = r - l
    for x in range(l, r):
        u = (min(x - l, r - 1 - x) + 0.5) / L
        y = 1 + int(round(4 * 4 * u * (1 - u) * 0.5 * 2))
        put(a, x, y, G_MID); put(a, x, y - 1, G_DK)
    for x in range(l + 3, r - 3, 8):
        u = (min(x + 1 - l, r - 2 - x) + 0.5) / L
        y = 1 + int(round(4 * 4 * u * (1 - u) * 0.5 * 2))
        stamp_rose(a, x, y)
    return a


# ------------------------------------------------------------------------------------------------ the play tower
def tower_deck(w):
    """a yellow deck: box w x 6 plus the outline; lit cap, flat front, a shade row; a bolt 2 px in at each end"""
    a = canvas(w + 2, 8)
    rect(a, 0, 0, w + 2, 8, INK)
    rect(a, 1, 1, w, 1, Y_LT); rect(a, 1, 2, w, 4, Y_MID); rect(a, 1, 6, w, 1, Y_SH)
    for bx in (3, w - 3):
        a[3, bx] = P_LT; a[3, bx + 1] = P_MID; a[4, bx] = P_MID; a[4, bx + 1] = INK
    return a


def tower_post(w, h):
    """a grey post (the slide's): ink sides, a lit left column; a foot plate on the path"""
    a = canvas(w + 2, h)
    rect(a, 0, 0, w + 2, h, INK)                         # (its top row is under the deck: ink, so the outline is whole)
    rect(a, 1, 1, w, h - 2, P_MID); rect(a, 1, 1, 1, h - 2, P_LT)
    return a


# ---------------------------------------------------------------------------------------------------- the gate
def brick_pier(w, h, phase=0):
    """a brick shaft: courses 4 px (brick 3 + mortar 1), bricks 11 + 1 joint, stretcher bond (half offset); every
    third brick in a course the second brick shade (a fixed pattern, no noise); the left column lit, the right two
    columns in shade"""
    a = canvas(w, h)
    for y in range(h):
        c = y // 4; r = y % 4
        for x in range(w):
            if r == 3: col = MORTAR
            else:
                xx = x + (6 if c % 2 else 0) + phase
                if xx % 12 == 11: col = MORTAR
                else:
                    k = xx // 12
                    col = B_ALT if (k + c) % 3 == 0 else B_MID
                    if r == 0: col = B_LT if col == B_MID else B_MID          # each brick's lit top row
            a[y, x] = col
        a[y, 0] = B_LT if y % 4 != 3 else MORTAR
        a[y, w - 2] = B_SH if y % 4 != 3 else B_SH
        a[y, w - 1] = B_DK
    return a


def ball(d):
    """a stone ball d px across: lit upper left, shade lower right (by rule on the pixel centre)"""
    a = canvas(d, d)
    r = d / 2
    for y in range(d):
        for x in range(d):
            dx, dy = x + 0.5 - r, y + 0.5 - r
            if dx * dx + dy * dy <= r * r:
                s = (dx + dy) / r
                a[y, x] = S_LT if s < -0.55 else S_SH if s > 0.55 else S_MID
    return a


def pier(h_shaft):
    """one pier, 30 px wide overall: granite plinth (28 px, 8 rows), brick shaft (26 px), sandstone cap (30 px,
    3 rows plus a 28 px fillet), a neck and a 10 px ball"""
    W = 30
    parts = []
    H = 10 + 2 + 1 + 3 + h_shaft + 8
    a = canvas(W, H)
    y = 0
    stamp(a, ball(10), 10, 0); y = 10
    rect(a, 12, y, 6, 2, S_MID); rect(a, 12, y, 1, 2, S_LT); rect(a, 17, y, 1, 2, S_SH); y += 2   # the neck
    rect(a, 1, y, 28, 1, S_LT); y += 1                                                        # cap: the top fillet
    rect(a, 0, y, 30, 2, S_MID); rect(a, 0, y, 30, 1, S_LT); rect(a, 0, y + 2, 30, 1, S_SH)    # the cornice
    rect(a, 0, y, 1, 3, S_LT); rect(a, 29, y, 1, 3, S_SH); y += 3
    stamp(a, brick_pier(26, h_shaft), 2, y); y += h_shaft
    rect(a, 1, y, 28, 8, GR_MID); rect(a, 1, y, 28, 1, GR_LT); rect(a, 1, y, 1, 8, GR_LT); rect(a, 28, y, 1, 8, GR_SH)
    rect(a, 1, y + 4, 28, 1, GR_SH)                                                          # the plinth's two courses
    return a


def gate_leaf(w, h):
    """a wrought iron leaf, w x h: a frame of 2 px rails (top, middle, bottom) and stiles, 1 px bars on a 4 px
    pitch with spear tips 3 px over the top rail, short dog bars between them in the lower panel, a frieze of
    rosettes in the top panel"""
    a = canvas(w, h + 4)
    top = 4
    for bx in range(1, w, 4):                            # the bars and their spear tips
        rect(a, bx, top - 1, 1, h + 1, I_MID)
        put(a, bx, top - 3, I_LT); rect(a, bx - 1, top - 2, 3, 1, I_MID)
    for ry in (top, top + 14, top + h - 3):              # rails: lit top row, dark under
        rect(a, 0, ry, w, 1, I_LT); rect(a, 0, ry + 1, w, 1, I_DK)
    rect(a, 0, top - 1, 2, h + 1, I_DK); rect(a, 0, top - 1, 1, h + 1, I_LT)     # the hanging stile (up to its hinge cap)
    rect(a, w - 2, top, 2, h, I_DK); rect(a, w - 2, top, 1, h, I_LT)             # the meeting stile
    for dx in range(3, w - 3, 4):                        # dog bars: a short bar between each pair, lower panel
        rect(a, dx, top + h - 12, 1, 9, I_MID)
    # the top panel: a frieze of rosettes, one 3 x 3 rosette between each pair of bars (drawn once, stamped on the pitch)
    for bx in range(1, w - 4, 4):                        # (a rosette: a lit cross round a dark boss, no hole)
        cx, cy = bx + 1, top + 6
        for i, j in ((1, 0), (0, 1), (2, 1), (1, 2)): put(a, cx + i, cy + j, I_LT)
        put(a, cx + 1, cy + 1, I_DK)
    return a


def build_gate():
    SHAFT = 72                                           # 18 courses
    P = pier(SHAFT)
    PH = P.shape[0]                                      # 96
    OPEN = 64                                            # 1.4 m between the piers' shafts
    W = 30 + OPEN - 4 + 30                               # the caps overhang 2 px into the opening on each side
    a = canvas(W, PH)
    leaf_h = 70                                          # 1.6 m to the spear tips with the 4 px tips
    lw = 32
    lx = 30 - 2                                          # the shut leaf hangs on the left pier's shaft face
    L = gate_leaf(lw, leaf_h)
    stamp(a, L, lx, PH - 2 - L.shape[0])                 # 2 px over the ground
    # the open right leaf, swung back 90 degrees against the right pier: its stile edge-on, with its tips
    ex = W - 30 + 2 - 4
    ey = PH - 2 - L.shape[0]
    rect(a, ex, ey + 4, 3, leaf_h, I_DK); rect(a, ex, ey + 4, 1, leaf_h, I_LT)
    put(a, ex + 1, ey + 1, I_LT); rect(a, ex, ey + 2, 3, 1, I_MID); put(a, ex + 1, ey + 3, I_MID)
    for hy in (ey + 8, ey + leaf_h - 4):                 # its hinge straps on the pier
        rect(a, ex + 3, hy, 2, 2, I_DK)
    for hy in (PH - 2 - L.shape[0] + 8, PH - 2 - 8):     # the shut leaf's hinge straps
        rect(a, lx - 2, hy, 2, 2, I_DK)
    stamp(a, P, 0, 0); stamp(a, P, W - 30, 0)
    return a


# --------------------------------------------------------------------------------------------------- the swings
def build_swings():
    """front-on: a top beam 5 px (2.3 m to its top: 106 px), legs 4 px splayed out 1 in 8 at each end, two seats
    (16 x 3, yellow) hung on chains (1 px, links of 2 px, grey) 0.45 m (21 px) over the ground. Decoration: no
    outline, edges a darker shade of the green"""
    H = 106; beam = 56; spread = H // 8
    W = beam + 2 * spread + 2
    a = canvas(W, H)
    bx0 = spread + 1
    for y in range(H):                                    # legs: straight 1:8 stairs, lit outer edge on the left
        o = (y - 2) // 8 if y >= 2 else 0
        lx = bx0 - o; rx = bx0 + beam - 4 + o
        rect(a, lx, y, 4, 1, SW_MID); put(a, lx, y, SW_LT); put(a, lx + 3, y, SW_SH)
        rect(a, rx, y, 4, 1, SW_MID); put(a, rx, y, SW_LT); put(a, rx + 3, y, SW_SH)
    rect(a, bx0 - 1, 0, beam + 2, 5, SW_MID)             # the beam, over the legs' tops
    rect(a, bx0 - 1, 0, beam + 2, 1, SW_LT); rect(a, bx0 - 1, 4, beam + 2, 1, SW_SH)
    rect(a, bx0 - 1, 0, 1, 5, SW_LT); rect(a, bx0 + beam, 0, 1, 5, SW_SH)
    seat_y = H - 1 - 21
    for sx in (bx0 + 8, bx0 + beam - 8 - 16):             # two seats, 16 px, mirrored about the beam's middle
        for cx in (sx + 1, sx + 14):                      # chains with a hook at the beam
            put(a, cx, 5, P_MID)
            for y in range(6, seat_y):
                put(a, cx, y, P_LT if (y // 2) % 2 == 0 else P_MID)
        rect(a, sx, seat_y, 16, 3, Y_MID); rect(a, sx, seat_y, 16, 1, Y_LT); rect(a, sx, seat_y + 2, 16, 1, Y_SH)
    return a


# ------------------------------------------------------------------------------------------------------- main
def main():
    P = props(); water = water_runs()
    print('water runs', water)
    data = []                                            # riverwalk/cp_built.lua

    def entry(key, box, files):
        data.append((key, box, files))

    save('park_gate', build_gate())
    save('park_swings', build_swings())
    named = [p for p in P if p['name'] in ('TREETOP WALK', 'ALDER WALK') and p['y1'] <= FOOT - 90]
    for p in named:
        w = p['x1'] - p['x0']
        lx, rx, glx, grx = walk_pylons(p, water)
        hangers = walk_hangers(p, lx, rx)
        rail, ex0 = walk_rail(p, lx, rx, hangers)
        bolts = [h - p['x0'] - 1 for h in hangers[3::4]] + [x + 2 - p['x0'] for x in (lx, rx) if p['x0'] <= x and x + PYLON <= p['x1']]
        deck = walk_deck(w, bolts)
        legs, _ = walk_legs(p, lx, rx, glx, grx)
        k = f"cp_walk{p['x0']}"
        save(k + '_deck', deck, k); save(k + '_rail', rail, k); save(k + '_legs', legs, k)
        print(f"  {p['name']}: a rope bridge, pylons at x {lx} and {rx} (ground y {glx}, {grx}), {len(hangers)} hangers, "
              f"span {rx - lx - PYLON} px; nothing in the water")
        entry(k, p, {'deck': (k + '_deck', p['x0'] - 1, p['y0'] - 1, False),
                     'rail': (k + '_rail', ex0, p['y0'] - 1 - rail.shape[0], False),
                     'legs': (k + '_legs', ex0, p['y1'], False)})
    # the arbour's slats: the ARBOUR ledge and the unnamed ledges of the tier after it up to the PLAY TOWER
    tier = [p for p in P if p['kind'] in ('oneway', 'solid') and p['y1'] <= FOOT - 90 and p['layer'] != 'front']
    arb = next(p for p in tier if p['name'] == 'ARBOUR'); tow = next(p for p in tier if p['name'] == 'PLAY TOWER')
    slats = [p for p in tier if arb['x0'] <= p['x0'] < tow['x0'] - 8 and (p['name'] in ('', 'ARBOUR'))
             and not any(q['name'] == 'PLAY TOWER' and q['x0'] < p['x1'] and q['x1'] > p['x0'] for q in tier)]
    for p in slats:
        w = p['x1'] - p['x0']; h = FOOT - p['y1']
        s = f'cp_arbour_slat{w}'; po = f'cp_arbour_posts{w}x{h}'
        save(s, arbour_slat(w), 'cp_arbour'); save(po, arbour_posts(w, h), 'cp_arbour')
        entry(f"arbour{p['x0']}", p, {'slat': (s, p['x0'] - 1, p['y0'] - 1, False), 'posts': (po, p['x0'] - 6, p['y1'], True)})
    # the play tower's decks: PLAY TOWER and the one-way ledge under it (the lower deck), and their posts
    decks = [tow] + [p for p in P if p['kind'] == 'oneway' and p['name'] == '' and p['x0'] < tow['x1'] and p['x1'] > tow['x0'] - 20
                     and p['y0'] > tow['y0'] and p['y1'] < FOOT - 40]
    for p in decks:
        w = p['x1'] - p['x0']; d = f'cp_tower_deck{w}'
        save(d, tower_deck(w), 'cp_tower')
        entry(f"tower{p['x0']}", p, {'deck': (d, p['x0'] - 1, p['y0'] - 1, False)})
    posts = [p for p in P if p['kind'] == 'decor' and p['name'] == '' and p['x1'] - p['x0'] <= 12
             and p['y1'] < FOOT and p['y1'] >= FOOT - 40 and p['y0'] <= FOOT - 100
             and tow['x0'] - 20 <= p['x0'] < tow['x1']]
    for p in posts:
        top = p['y0']
        for q in decks:                                   # a post under a lower deck starts at that deck
            if q is not tow and q['x0'] < p['x1'] and q['x1'] > p['x0'] and q['y0'] > p['y0']: top = q['y0']
        w = p['x1'] - p['x0']; h = FOOT - top; n = f'cp_tower_post{w}x{h}'
        save(n, tower_post(w, h), 'cp_tower')
        entry(f"towerpost{p['x0']}", p, {'post': (n, p['x0'] - 1, top, False)})
    with open(os.path.join(ROOT, 'riverwalk/cp_built.lua'), 'w') as f:
        f.write('-- generated by tools/build_cp_built.py (art/cp-built-06nov): the built art of the tall City Park\'s\n'
                '-- plank walks, rose arbour and play tower, per box. scene.lua draws an image only when the prop\'s box\n'
                '-- is still this box (else its code drawing). file, x, y (world, top left), faded (to the back haze)\n'
                'return {\n')
        for key, b, files in data:
            parts = []
            for k, v in files.items():
                if k == 'wet': parts.append('wet = { ' + ', '.join(f'{{ {x}, {w} }}' for x, w in v) + ' }')
                else: parts.append(f'{k} = {{ "{v[0]}", {v[1]}, {v[2]}, {str(v[3]).lower()} }}')
            f.write(f'  ["{b["x0"]},{b["y0"]},{b["x1"]},{b["y1"]}"] = {{ ' + ', '.join(parts) + ' },\n')
        f.write('}\n')
    print('wrote riverwalk/cp_built.lua,', len(data), 'boxes')


if __name__ == '__main__':
    os.chdir(ROOT)
    main()
