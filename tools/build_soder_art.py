#!/usr/bin/env python3
"""build_soder_art.py: Söder Hill's art, BUILT by rule (8 Nov 2026, owner: "finish levels 4-6"). 0 credits.

    python3 -I tools/build_soder_art.py              write riverwalk/levelart/soder/*.png and palette.lua
    python3 -I tools/build_soder_art.py --check      fail if a file on disk is not what this script builds
    python3 -I tools/build_soder_art.py --preview D  also write previews (the level at 1x, colour and greyscale) to D

Design target: the producer's concept art/gen/concepts/sh_cafe_concept_a.png (reference only, never cut; its colours
are sampled into PAL below). Everything here is drawn at game size, 1 art px = 1 game px, front-on, from parts drawn
once and stamped on integer grids. The art follows the level: the street's tops come from riverwalk/level/soder.map
and the hatches and props from riverwalk/level/soder.lua; --check fails when they changed and the files did not.

Files (riverwalk/levelart/soder/):
  palette.lua        PAL as a Lua table (the ONE palette: swap the hex values here and rebuild)
  ground_NN.png      the street, 512 x 240 tiles (NN = x / 512): granite setts in running bond (5 courses, longer
                     and taller towards the front), a granite kerb, the retaining wall below (8 px courses on one
                     world grid); the six stair flights as 8 px stone steps (Sc.STEP_RW) between granite landing
                     slabs; the open cellar hatches (iron rim, the dark cellar with a step inside, the plank lid
                     standing open against the house); the harbour quay (big slabs, a coping, the quay wall)
  back_NN.png        the house fronts behind the street, true scale (46 px a metre), 512 x 240 tiles: plaster in
                     the concept's ochre, rust red, salmon and yellow, granite socles, 4-pane windows, panelled
                     doors in stone surrounds, shop windows, drain pipes, corner pilasters; alleys with a stone
                     wall at the stair flights; at the bottom the quay's cliff wall, Mia's stair and the harbour
  props/*.png        the play pieces and their holders (signs on their brackets, the awning on its arm, ...)
  sky.png, skyline.png, far.png, mid.png   the backdrop (sky by tools/build_sky.py's rules, the far city, the
                     harbour water, a row of roofs down the hill)
"""
import os, sys, re, math
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "riverwalk/levelart/soder")
W, H, TILE = 5120, 240, 512
MPX = 46                                    # px a metre

# ------------------------------------------------------------------------------------------------ the palette
# Per-material ramps (light to dark), sampled from the concept (sh_cafe_concept_a.png) and set in golden evening
# light (sun low, upper left). Neutral darks. The ladder: back layer darkest 10th pct >= 80 luma.
PAL = {
    # street setts (granite, grey-brown)
    "sett_lit": "c4b19c", "sett_a": "a99786", "sett_b": "9d8c7e", "sett_c": "b2a08e", "sett_j": "6a5b53",
    "contact": "4c3f3a",
    # kerb and landing granite
    "kerb_lit": "d6c6b2", "kerb_1": "bcac9c", "kerb_2": "a69688", "kerb_3": "8c7c72", "kerb_j": "6e6058", "kerb_sh": "4e423e",
    # retaining wall (rough granite blocks)
    "wall_lit": "8a786c", "wall_a": "726259", "wall_b": "6a5a52", "wall_c": "7a6a60", "wall_j": "4a3d39",
    # stair treads
    "tread_lit": "dccbb6", "tread": "c2b2a0", "tread_2": "b2a291", "tread_j": "7c6c62",
    # quay slabs
    "quay_lit": "d2c4b2", "quay_a": "b8aa9a", "quay_b": "ae9f90", "quay_j": "786a62",
    # cellar
    "cel_1": "4a3a34", "cel_2": "33282a", "cel_3": "231c1e", "cel_step": "5e4c44",
    # iron (rims, railings, pipes, brackets)
    "iron_lit": "6c625e", "iron": "3a3232", "iron_d": "241e1f", "ink": "1c1718",
    # the back row's ironwork (drain pipes, the cliff's railings): one step lighter (back layer: darkest 80, contrast 120)
    "bi_lit": "a08e84", "bi": "6c5e5a", "bi_d": "564a48",
    # lid planks (weathered oak)
    "lid_lit": "a0744c", "lid": "84603e", "lid_d": "66482e",
    # the hatch lids: steel checker plate
    "steel_lit": "b4aca4", "steel": "8e8680", "steel_d": "68605c",
    # plaster walls: base, pilaster (lighter), shade (darker) per house colour
    "ochre": "cc9454", "ochre_p": "e0ae70", "ochre_d": "b07c44",
    "rust": "a84e36", "rust_p": "c26a4c", "rust_d": "8c3e2a",
    "salmon": "d47c58", "salmon_p": "e8a884", "salmon_d": "b46448",
    "yellow": "d8ac5c", "yellow_p": "ecc888", "yellow_d": "b88e48",
    # socle (house plinth, granite)
    "socle_lit": "b49c86", "socle": "947c68", "socle_d": "7a6454",
    # windows: light frame, glass, reflection, sill
    "frame_lit": "f0e2c8", "frame": "d4c2a4", "frame_d": "a08a70", "glass": "5c6874", "glass_2": "6e7c88",
    "glass_r": "a4aeb0", "sill": "c8b8a4",
    # doors: green panelled, wooden brown; stone surround
    "door_lit": "5e8456", "door": "46664a", "door_d": "324c36",
    "wood_lit": "8e6444", "wood": "70503a", "wood_d": "563c2c",
    "stone_lit": "e2d2b8", "stone": "c6b498", "stone_d": "a08c74",
    # shop fascia and awnings, parasols (red and cream stripes)
    "red_lit": "c45a44", "red": "a84434", "red_d": "843428", "cream": "eedcb0", "cream_d": "d6c094",
    # cafe sign board
    "board_lit": "6a5248", "board": "4e3c36", "board_d": "3a2c28", "cup": "eee0c4", "cup_d": "c4ae8c",
    # sky (golden evening) and the far layers
    "sky_0": "e8a860", "sky_1": "f2bc68", "sky_2": "f8cc74", "sky_3": "fad88c", "sky_4": "fbe2a6",
    "cl_lit1": "fff0d4", "cl_lit2": "fcdcac", "cl_body": "eebc90", "cl_under": "dca084",
    "city_main": "d8b0a0", "city_near": "cca4a0", "city_rim": "fde4b0",
    "water_1": "c89c84", "water_2": "b88e80", "water_lit": "f4d4a4",
    "mid_roof": "a8786c", "mid_roof_d": "9a6c64", "mid_wall_a": "d4a888", "mid_wall_b": "cc9c84",
    "mid_wall_c": "dcb494", "mid_win": "a88c84", "mid_chim": "b88c78",
    # barrel
    "oak_lit": "b07c4c", "oak": "8c5e36", "oak_d": "6a4428", "hoop": "4a4240", "hoop_lit": "8a8078",
}


def hexc(h): return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


C = {k: hexc(v) for k, v in PAL.items()}
LUMA = np.array([0.299, 0.587, 0.114])


# ------------------------------------------------------------------------------------------------ the level
def read_map():
    rows = [l.rstrip("\n") for l in open(os.path.join(ROOT, "riverwalk/level/soder.map")) if l.strip()]
    top, slope = {}, {}
    for x in range(W):
        c = x // 8
        for r, line in enumerate(rows):
            ch = line[c]
            if ch == "#":
                top[x] = r * 8; break
            if ch == "\\":
                top[x] = r * 8 + (x - c * 8); slope[x] = True; break
    return top, slope


def read_level():
    src = open(os.path.join(ROOT, "riverwalk/level/soder.lua")).read()
    props = []
    for m in re.finditer(r'\{ name = "([^"]*)",\s*kind = "(\w+)",\s*layer = "(\w+)",\s*x0 = (\d+),\s*x1 = (\d+),\s*y0 = (\d+),\s*y1 = (\d+)', src):
        props.append(dict(name=m.group(1), kind=m.group(2), layer=m.group(3), x0=int(m.group(4)), x1=int(m.group(5)),
                          y0=int(m.group(6)), y1=int(m.group(7))))
    hb = re.search(r"L\.hatches = \{(.*?)\n\}", src, re.S).group(1)
    hatches = [tuple(int(v) for v in t) for t in re.findall(r"\{ (\d+), (\d+), (\d+) \}", hb)]
    return props, hatches


TOP, SLOPE = read_map()
PROPS, HATCHES = read_level()
RAISED = [(p["x0"], p["x1"], p["y0"]) for p in PROPS if p["name"] == "BALCONY"]   # balconies: a door behind each
STAIRS = []
for x in sorted(SLOPE):
    if x - 1 not in SLOPE: STAIRS.append(x)                       # each flight's first column (16 px: two cells)
STEP = 8                                                          # Sc.STEP_RW: 8 px stone steps
LANDING = 12                                                      # the granite landing slab at each end of a flight
QUAY_X = STAIRS[-1] + 16                                          # the harbour quay: from the last flight's foot
CLIFF_X = 4400                                                    # the quay's cliff wall, up to Mia's stair


def step_top(x):
    """a stair column's tread top: the slope's top rounded to the 8 px step (River Walk's stepTop)"""
    t0 = TOP[x]
    base = TOP[0]
    return base + int(math.floor((t0 - base) / STEP + 0.5)) * STEP


def street_top(x):
    """the drawn top (feet line) of column x, or None over a hatch"""
    if x not in TOP: return None
    return step_top(x) if x in SLOPE else TOP[x]


def hatch_at(x):
    for h in HATCHES:
        if h[0] <= x < h[1]: return h
    return None


def kind_at(x):
    if x not in TOP: return "hatch"
    if x in SLOPE: return "stair"
    for s in STAIRS:
        if s - LANDING <= x < s or s + 16 <= x < s + 16 + LANDING: return "landing"
    return "quay" if x >= QUAY_X + LANDING else "street"


def h32(*a):
    """a small deterministic hash"""
    v = 2166136261
    for k in a:
        v = ((v ^ (k & 0xffffffff)) * 16777619) & 0xffffffff
    v ^= v >> 13; v = (v * 1274126177) & 0xffffffff; v ^= v >> 16
    return v


class Img:
    def __init__(self, w, h):
        self.a = np.zeros((h, w, 4), np.uint8); self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x, :3] = C[c] if isinstance(c, str) else c; self.a[y, x, 3] = 255

    def rect(self, x, y, w, h, c):
        x0, y0, x1, y1 = max(0, x), max(0, y), min(self.w, x + w), min(self.h, y + h)
        if x1 > x0 and y1 > y0:
            self.a[y0:y1, x0:x1, :3] = C[c] if isinstance(c, str) else c; self.a[y0:y1, x0:x1, 3] = 255

    def clear(self, x, y, w, h):
        x0, y0, x1, y1 = max(0, x), max(0, y), min(self.w, x + w), min(self.h, y + h)
        if x1 > x0 and y1 > y0: self.a[y0:y1, x0:x1] = 0

    def paste(self, o, x, y):
        """alpha paste (binary alpha)"""
        sx0, sy0 = max(0, -x), max(0, -y)
        dx0, dy0 = max(0, x), max(0, y)
        w, h = min(o.w - sx0, self.w - dx0), min(o.h - sy0, self.h - dy0)
        if w <= 0 or h <= 0: return
        src = o.a[sy0:sy0 + h, sx0:sx0 + w]
        m = src[..., 3] > 0
        dst = self.a[dy0:dy0 + h, dx0:dx0 + w]
        dst[m] = src[m]

    def flip(self):
        o = Img(self.w, self.h); o.a = self.a[:, ::-1].copy(); return o


# ------------------------------------------------------------------------------------------------ C + D: the ground
# rows relative to the feet line t: t-12 contact shadow under the house socles; t-11 .. t+11 the street's surface
# (5 sett courses); t+12 .. t+18 the kerb; t+19 down the retaining wall (8 px courses on one world grid).
COURSES = [(3, 6), (3, 7), (4, 8), (4, 9), (4, 10)]               # (rows, sett length) back to front, + 1 px joints


def wall_course(y):
    """the retaining wall's course at row y: courses of 9 and 7 rows in turn on one world grid (16 px a pair: every
    street top is a multiple of 16, so the first course always starts right under the kerb). (index, row in it, rows)"""
    u = (y - 3) % 16
    k = 2 * ((y - 3) // 16)
    return (k, u, 9) if u < 9 else (k + 1, u - 9, 7)


def wall_block(k, x):
    """the block of course k at column x: blocks 22 to 44 long, laid from x = -64 with lengths by hash: (index, x0)"""
    bx, i = -64 + (h32(k, 7) % 30), 0
    while True:
        L = 22 + h32(k, i, 3) % 23
        if bx + L > x: return i, bx
        bx += L; i += 1


def wall_col(g, x, y0, y1=H):
    """the retaining wall from row y0 down: rough granite blocks in courses of 9 and 7 rows (world grid), three block
    shades by hash, each block's top row lit and its last row a step darker, 1 px joints"""
    for y in range(y0, y1):
        k, r, n = wall_course(y)
        if r == n - 1: g.px(x, y, "wall_j"); continue
        i, bx = wall_block(k, x)
        if x == bx: g.px(x, y, "wall_j"); continue
        shade = ("wall_a", "wall_b", "wall_c")[h32(k, i, 11) % 3]
        g.px(x, y, "wall_lit" if r == 0 else ("wall_b" if r == n - 2 and shade != "wall_b" else shade))


def sett_col(g, x, t):
    y = t - 11
    for ci, (rows, L) in enumerate(COURSES):
        off = (L // 2) * (ci % 2) + ci * 3
        u = (x + off) % (L + 1)
        k = (x + off) // (L + 1)
        shade = ("sett_a", "sett_b", "sett_c")[h32(ci, k, 5) % 3]
        for r in range(rows):
            if u == L: c = "sett_j"
            elif r == 0: c = "sett_lit" if u < L - 1 else shade
            else: c = shade
            g.px(x, y + r, c)
        g.px(x, y + rows, "sett_j")
        y += rows + 1


def kerb_col(g, x, t, joint, edge=None):
    rows = ["kerb_lit", "kerb_1", "kerb_2", "kerb_2", "kerb_2", "kerb_3", "kerb_sh"]
    for r, c in enumerate(rows):
        if joint and 1 <= r <= 5: c = "kerb_j"
        g.px(x, t + 12 + r, c)


def slab_col(g, x, t, pal, joint, split, lit_x=False):
    """a granite slab surface (landing, tread, quay): rows t-11 .. t+11, a joint row at `split` rows from the back"""
    lit, a, b, j = pal
    for r in range(23):
        y = t - 11 + r
        if joint or r == split: c = j
        elif r == 0 or r == split + 1: c = lit
        else: c = a if r < split else b
        if lit_x and not joint and r != split: c = lit
        g.px(x, y, c)


def build_ground():
    g = Img(W, H)
    front = Img(W, H)                    # the kerb and wall in front of each hatch, drawn again over Pepper
    for x in range(W):
        k = kind_at(x)
        if k == "hatch": continue
        t = street_top(x)
        g.px(x, t - 12, "contact")
        if k == "street":
            sett_col(g, x, t)
            kerb_col(g, x, t, x % 32 == 0)
        elif k == "landing":
            first = kind_at(x - 1) != "landing"
            last = kind_at(x + 1) != "landing"
            slab_col(g, x, t, ("kerb_lit", "kerb_1", "kerb_2", "kerb_j"), first, 11, lit_x=last and False)
            kerb_col(g, x, t, first)
        elif k == "stair":
            edge = street_top(x - 1) != t                                  # a step's first column: the joint
            slab_col(g, x, t, ("tread_lit", "tread", "tread_2", "tread_j"), edge, 11)
            kerb_col(g, x, t, edge)
        elif k == "quay":
            L = 46
            u = (x - QUAY_X) % L
            slab_col(g, x, t, ("quay_lit", "quay_a", "quay_b", "quay_j"), u == 0, 10)
            # the quay's coping (the kerb in heavier granite, joints every metre)
            kerb_col(g, x, t, u == 0)
        wall_col(g, x, t + 19)
    # a step's riser seen from the side: the lower tread's back corner gets the landing's lit arris
    # open cellar hatches
    for (x0, x1, t) in HATCHES:
        hatch(g, front, x0, x1, t)
    return g, front


def hatch(g, front, x0, x1, t):
    """an open cellar hatch: the street's surface opens (iron rim on all four sides), inside the dark cellar with its
    stone step, the kerb and the wall run on in front (and are drawn again over Pepper as she drops in), the lid (oak
    planks, two iron straps, hinged at the back) stands open against the house"""
    w = x1 - x0
    for x in range(x0, x1):
        for y in range(t - 11, t + 12):
            r = y - (t - 11)
            c = "cel_1" if r < 4 else ("cel_2" if r < 11 else "cel_3")
            g.px(x, y, c)
        # the cellar's stone step, on the left inside (lit tread, its face)
        if x - x0 < min(12, w // 3):
            g.px(x, t - 1, "cel_step"); g.px(x, t, "cel_2")
            for y in range(t + 1, t + 12): g.px(x, y, "cel_2")
        g.px(x, t - 12, "iron_lit"); g.px(x, t - 11, "iron")                      # the rim's back edge
        g.px(x, t + 11, "iron_lit")                                              # its front edge
        kerb_col(g, x, t, x == x0 or x == x1 - 1)
        wall_col(g, x, t + 19)
        for y in range(t + 11, H):                                               # copy for the front pass
            front.a[y, x] = g.a[y, x]
    for x in (x0 - 2, x0 - 1, x1, x1 + 1):                                       # the rim's sides (2 px iron)
        inner = x in (x0 - 1, x1)
        for y in range(t - 11, t + 12):
            g.px(x, y, "iron" if inner else "iron_d")
        g.px(x, t - 12, "iron_lit")
    # the lid: a steel plate the width of the hole, LID px tall, swung up from the rim's back edge against the house:
    # we see its underside, an angle-iron frame (2 px) with a cross brace and rivets, a lit left edge and top
    # (decoration: no outline). Grey steel, so it never reads as one of the wooden crates.
    LID = 26
    y0 = t - 12 - LID
    hgt = LID
    for y in range(y0, t - 12):
        v = y - y0
        for x in range(x0, x1):
            u = x - x0
            if u == 0 or v == 0: c = "steel_lit"
            elif u == w - 1 or v == hgt - 1: c = "steel_d"
            elif u <= 2 or v <= 2 or u >= w - 3 or v >= hgt - 3: c = "steel"
            else:
                # the cross brace: the two diagonals, 2 px
                d1 = abs(u * (hgt - 1) - v * (w - 1)) / max(w, hgt)
                d2 = abs(u * (hgt - 1) - (hgt - 1 - v) * (w - 1)) / max(w, hgt)
                c = "steel" if min(d1, d2) < 1.3 else "steel_d"
            g.px(x, y, c)
        for (rx, ry) in ((1, 1), (w - 3, 1), (1, hgt - 3), (w - 3, hgt - 3)):
            g.px(x0 + rx, y0 + ry, "steel_lit")
    for hx in (x0 + 4, x1 - 7):                                                  # the hinges at the foot
        g.rect(hx, t - 14, 3, 2, "iron_d"); g.px(hx, t - 14, "iron_lit")


# ------------------------------------------------------------------------------------------------ parts
def window_part(w=40, h=66):
    """a 4-pane window (true scale 0.87 x 1.43 m): light frame 3 px (lit top and left), a mullion and a transom
    (2 px), glass with the sky's reflection in the upper left pane, the reveal's shadow on the top and left (the sun
    is upper left), a stone sill under it"""
    p = Img(w + 4, h + 4)
    p.rect(0, 0, w + 4, h + 4, "stone_d")                                        # the plaster reveal's edge
    p.rect(2, 1, w, h, "frame")
    p.rect(2, 1, w, 1, "frame_lit"); p.rect(2, 1, 1, h, "frame_lit")
    gx0, gy0, gw, gh = 5, 4, w - 6, h - 6
    p.rect(gx0, gy0, gw, gh, "glass")
    p.rect(gx0, gy0, gw, 2, "glass"); p.rect(gx0, gy0, 2, gh, "glass")      # the reveal's shadow side lit less
    mx = gx0 + gw // 2 - 1
    ty = gy0 + int(gh * 0.38)
    p.rect(mx, gy0, 2, gh, "frame"); p.rect(mx, gy0, 1, gh, "frame_lit")
    p.rect(gx0, ty, gw, 2, "frame"); p.rect(gx0, ty, gw, 1, "frame_lit")
    for i in range(6):                                                           # the reflection: a short diagonal
        p.rect(gx0 + 4 + i, gy0 + 3 + i * 2, 2, 2, "glass_r")
    p.rect(0, h + 1, w + 4, 2, "stone"); p.rect(0, h + 1, w + 4, 1, "stone_lit")  # the sill
    p.rect(1, h + 3, w + 2, 1, "stone_d")
    return p


def door_part(green=True, w=50, h=104):
    """a panelled double door in a stone surround (1.1 x 2.2 m): surround 5 px (lit left and top), a lintel with a
    keystone, a fanlight, two leaves of three panels each"""
    L, M, D = ("door_lit", "door", "door_d") if green else ("wood_lit", "wood", "wood_d")
    p = Img(w + 10, h + 12)
    p.rect(0, 0, w + 10, h + 12, "stone_d")
    p.rect(0, 0, w + 9, h + 12, "stone")
    p.rect(0, 0, 1, h + 12, "stone_lit"); p.rect(0, 0, w + 9, 1, "stone_lit")
    p.rect(w // 2 + 1, 0, 8, 9, "stone_lit"); p.rect(w // 2 + 2, 1, 6, 8, "stone")   # the keystone
    p.rect(w // 2 + 8, 1, 1, 8, "stone_d")
    fy = 10
    p.rect(5, fy, w, 12, "frame"); p.rect(7, fy + 2, w - 4, 8, "glass")         # the fanlight
    for i in range(1, 4): p.rect(5 + i * w // 4, fy + 2, 2, 8, "frame")
    p.rect(7, fy + 2, w - 4, 1, "glass")
    dy = fy + 12
    p.rect(5, dy, w, h + 12 - dy, D)
    lw = (w - 2) // 2
    for li in range(2):
        lx = 6 + li * (lw + 1)
        p.rect(lx, dy + 1, lw - 1, h + 11 - dy - 1, M)
        p.rect(lx, dy + 1, 1, h + 11 - dy - 1, L)
        ph = (h + 11 - dy - 10) // 3
        for k in range(3):
            py = dy + 4 + k * (ph + 2)
            p.rect(lx + 4, py, lw - 9, ph - 2, D)
            p.rect(lx + 5, py + 1, lw - 10, ph - 3, M)
            p.rect(lx + 5, py + ph - 3, lw - 10, 1, L)
    p.rect(5 + w // 2 - 3, dy + 44, 2, 3, "stone_lit")                          # the handles (brass-ish)
    p.rect(5 + w // 2 + 2, dy + 44, 2, 3, "stone_lit")
    return p


def shop_part(w=92, h=96):
    """a shop window (2 x 2.1 m): a stone surround, a plain fascia board (no letters) in the shop's colour, glass in
    three lights over a wooden stall board"""
    p = Img(w + 8, h)
    p.rect(0, 0, w + 8, h, "stone_d"); p.rect(0, 0, w + 7, h, "stone"); p.rect(0, 0, 1, h, "stone_lit"); p.rect(0, 0, w + 7, 1, "stone_lit")
    p.rect(4, 4, w, 12, "door_d"); p.rect(4, 4, w, 1, "door_lit"); p.rect(5, 5, w - 2, 10, "door")
    gy = 18
    p.rect(4, gy, w, h - gy - 28, "frame")
    p.rect(6, gy + 2, w - 4, h - gy - 32, "glass")
    p.rect(6, gy + 2, w - 4, 2, "glass")
    for i in (1, 2):
        mx = 4 + i * w // 3
        p.rect(mx, gy, 3, h - gy - 28, "frame"); p.rect(mx, gy, 1, h - gy - 28, "frame_lit")
    for i in range(8): p.rect(12 + i, gy + 6 + i * 2, 2, 2, "glass_r")
    p.rect(4, h - 28, w, 28, "stone_d"); p.rect(5, h - 27, w - 2, 26, "stone"); p.rect(5, h - 27, w - 2, 1, "stone_lit")
    for i in range(3):
        bx = 9 + i * (w - 10) // 3
        p.rect(bx, h - 23, (w - 10) // 3 - 6, 18, "stone_d"); p.rect(bx + 1, h - 22, (w - 10) // 3 - 8, 16, "stone")
    return p


def pipe(img, x, y0, y1):
    """a cast-iron drain pipe 4 px (lit left), brackets every 46 px, a shoe at its foot turning to the street"""
    for y in range(y0, y1):
        img.px(x, y, "bi_lit"); img.px(x + 1, y, "bi"); img.px(x + 2, y, "bi"); img.px(x + 3, y, "bi_d")
    for y in range(y1 - 20, y0, -MPX):
        img.rect(x - 1, y, 6, 2, "bi_d")
    img.rect(x, y1 - 4, 7, 4, "bi"); img.rect(x, y1 - 4, 7, 1, "bi_lit"); img.rect(x + 6, y1 - 3, 1, 3, "bi_d")


# ------------------------------------------------------------------------------------------------ the back row
BAY = 76                       # one window bay (1.65 m)
EDGE = 20                      # each house's margin to its first bay (the pilaster 10 px inside it)
STOREY = 138                   # 3 m
SOCLE = 12
COLOURS = ["ochre", "rust", "salmon", "yellow"]


def house(nbays, colour, special, seed, ml=EDGE, mr=EDGE):
    """a house front nbays wide, from its base (the street's back edge, row H - 1) up past the top of the screen.
    special: {bay index: "door" | "green" | "shop" | "high_door" | "none"}"""
    w = ml + mr + nbays * BAY
    hgt = 300
    img = Img(w, hgt)
    base = hgt                                                     # the row under the socle's last row
    img.rect(0, 0, w, base, colour)
    # one shade band: the pilasters at both corners, 10 px, a step lighter, their outer px a step darker
    for px0 in (0, w - 10):
        img.rect(px0, 0, 10, base, colour + "_p")
    img.rect(w - 1, 0, 1, base, colour + "_d")
    img.rect(9, 0, 1, base, colour + "_d"); img.rect(w - 10, 0, 1, base, colour + "_d")
    # the string course between the storeys: 4 px (lit, stone, stone, shadow on the plaster)
    sy = base - SOCLE - STOREY
    img.rect(0, sy, w, 1, "stone_lit"); img.rect(0, sy + 1, w, 2, "stone"); img.rect(0, sy + 3, w, 1, colour + "_d")
    # the socle: granite, lit top row, joints every 46 px
    img.rect(0, base - SOCLE, w, SOCLE, "socle")
    img.rect(0, base - SOCLE, w, 1, "socle_lit"); img.rect(0, base - SOCLE + 1, w, 1, "socle_lit")
    img.rect(0, base - 1, w, 1, "socle_d")
    for x in range(seed % 23, w, MPX): img.rect(x, base - SOCLE + 2, 1, SOCLE - 3, "socle_d")
    win = window_part()
    ww = win.w
    for b in range(nbays):
        cx = ml + b * BAY + BAY // 2
        sp = special.get(b)
        # the first floor's window, over every bay: sill 0.9 m over the string course
        img.paste(win, cx - ww // 2, sy - 41 - win.h + 3)
        if sp in ("door", "green"):
            d = door_part(green=(sp == "green"))
            img.paste(d, cx - d.w // 2, base - SOCLE - d.h + 2)
            img.rect(cx - d.w // 2 - 2, base - SOCLE, d.w + 4, SOCLE, "stone_lit")       # its threshold step
            img.rect(cx - d.w // 2 - 2, base - SOCLE + 1, d.w + 4, SOCLE - 2, "stone")
            img.rect(cx - d.w // 2 - 2, base - 1, d.w + 4, 1, "stone_d")
        elif sp == "shop":
            s = shop_part()
            img.paste(s, cx - s.w // 2, base - SOCLE - s.h)
        elif sp == "none":
            pass
        elif isinstance(sp, tuple) and sp[0] == "high_door":               # a door onto a raised balcony
            d = door_part(green=True)
            img.paste(d, cx - d.w // 2, sp[1] - d.h)
        else:
            img.paste(win, cx - ww // 2, base - SOCLE - 41 - win.h + 3)
            # a cellar vent in the socle under it
            img.rect(cx - 6, base - SOCLE + 3, 12, 6, "socle_d"); img.rect(cx - 5, base - SOCLE + 4, 10, 4, "socle_d")
            for vx in range(cx - 4, cx + 5, 3): img.rect(vx, base - SOCLE + 4, 1, 4, "bi_d")
    return img


def alley(img, x0, x1):
    """an alley (gränd) between two houses at a stair flight, going down the hill away from the street: its stone
    wall (1.2 m) on the back edge, the coping lit; over it the backdrop shows (the roofs below, the far city)"""
    tops = [street_top(x) for x in range(x0, x1) if street_top(x) is not None]
    top_y = min(tops) - 12 - 55
    for x in range(x0, x1):
        t = street_top(x)
        b = t - 12
        wall_col(img, x, top_y, b)
        img.px(x, top_y - 3, "kerb_lit"); img.px(x, top_y - 2, "kerb_1"); img.px(x, top_y - 1, "kerb_3")
    for x in (x0, x1 - 1):                                             # the houses' shadowed returns beside it
        pass


HOUSE_COLOURS = []                     # each house's colour count (the back layer allows 20 per piece): --check


def stretch_houses(b, a, z, si):
    """houses filling [a, z) exactly: 3 to 5 bays each, the spare px shared out as wider margins"""
    L = z - a
    groups = []
    nb = (L - 2 * EDGE) // BAY
    while True:
        groups = []
        left = nb
        while left > 0:
            k = min(left, 3 + h32(si, len(groups)) % 3)
            if 0 < left - k < 3: k = left - 3 if left - 3 >= 3 else left
            groups.append(k); left -= k
        spare = L - sum(EDGE * 2 + k * BAY for k in groups)
        if spare >= 0: break
        nb -= 1
    t = next(street_top(xx) for xx in range(a, z) if street_top(xx) is not None)
    base = t - 12
    x = a
    for gi, k in enumerate(groups):
        extra = spare // len(groups) + (1 if gi < spare % len(groups) else 0)
        colour = COLOURS[(si * 2 + gi + 1) % len(COLOURS)]
        special = {}
        ml = EDGE + extra // 2

        def bay_x(bi): return x + ml + bi * BAY + BAY // 2

        def blocked(bi, half=34):
            """a door or shop window here would stand behind a piece in the street (hidden or crowded)"""
            cx = bay_x(bi)
            return any(p["layer"] == "play" and p["name"] not in ("BALCONY",) and p["x0"] < cx + half and p["x1"] > cx - half
                       for p in PROPS) or any(h[0] < cx + half and h[1] > cx - half for h in HATCHES)
        free = [bi for bi in range(k) if not blocked(bi)]
        if k >= 3 and free:
            special[free[h32(si, gi, 1) % len(free)]] = "green" if (si + gi) % 2 == 0 else "door"
        free = [bi for bi in free if bi not in special]
        if k >= 4 and (si + gi) % 3 == 0 and free:
            special[free[h32(si, gi, 2) % len(free)]] = "shop"
        for p in PROPS:                                                # behind the arch, a sign's bracket or the awning's
            if p["name"] in ("ARCH", "SIGN", "AWNING"):                # arm: plain wall (their plates go into plaster)
                for bi in range(k):
                    if p["x0"] - 20 < bay_x(bi) + 24 and p["x1"] + 20 > bay_x(bi) - 24: special[bi] = "none"
        for (bx0, bx1, by) in RAISED:                                  # a raised balcony on this house: a door onto it
            for bi in range(k):
                cx = x + EDGE + extra // 2 + bi * BAY + BAY // 2
                if bx0 <= cx < bx1: special[bi] = ("high_door", by - base + 300 + 0)
        hs = house(k, colour, special, h32(si, gi), EDGE + extra // 2, EDGE + extra - extra // 2)
        HOUSE_COLOURS.append(len(np.unique(hs.a[hs.a[..., 3] > 0][:, :3], axis=0)))
        b.paste(hs, x, base - hs.h)
        wpx = hs.w
        if gi < len(groups) - 1: pipe(b, x + wpx - 3, 0, base)
        x += wpx


def cliff(b, x0, x1, top):
    """the quay's cliff wall (Söder's retaining wall down to the harbour) from the quay's back edge up to `top`: big
    granite blocks, a coping, an iron railing on it, and the upper terrace's houses behind"""
    for x in range(x0, x1):
        base = street_top(x) - 12
        wall_col(b, x, top + 3, base)
        b.px(x, top, "kerb_lit"); b.px(x, top + 1, "kerb_1"); b.px(x, top + 2, "kerb_3")
    railing_run(b, x0, x1, top)


def railing_run(b, x0, x1, top):
    """an iron railing 1 m tall on a coping at row `top`: posts every 46 px, balusters every 6 px, top and bottom
    rails (decoration: no outline, its edges a darker iron)"""
    y0 = top - MPX
    for x in range(x0, x1):
        b.px(x, y0, "bi_lit"); b.px(x, y0 + 1, "bi"); b.px(x, y0 + 2, "bi_d")
        b.px(x, top - 4, "bi"); b.px(x, top - 3, "bi_d")
        if (x - x0) % 6 == 3:
            for y in range(y0 + 3, top - 4): b.px(x, y, "bi")
        if (x - x0) % MPX == 2 or x == x1 - 3:
            for y in range(y0 - 2, top): b.px(x, y, "bi_lit"); b.px(x + 1, y, "bi"); b.px(x + 2, y, "bi_d")


def mia_stair(b, x0, x1, ytop, ybot):
    """Mia's stair from the upper terrace (ytop, at x0) down to the quay (ybot, at x1): 8 px steps on one grid, each
    tread lit, the stair's stone flank under them stepped by whole px, an iron handrail along it"""
    n = int(round((ybot - ytop) / 8))
    run = (x1 - x0) / n
    for i in range(n):
        sx0, sx1 = x0 + int(round(i * run)), x0 + int(round((i + 1) * run))
        ty = ytop + i * 8
        for x in range(sx0, sx1):
            b.px(x, ty, "tread_lit"); b.px(x, ty + 1, "tread")
            for y in range(ty + 2, ty + 8): b.px(x, y, "tread_2" if x != sx0 else "tread_j")
            for y in range(ty + 8, ybot): b.px(x, y, "kerb_3" if (y - ty) % 8 != 0 else "kerb_j")
    # the handrail: posts on every other step, the rail stepped down along the nosings 40 px over them
    for i in range(0, n, 2):
        px0 = x0 + int(round(i * run)) + 2
        ty = ytop + i * 8
        for y in range(ty - 38, ty): b.px(px0, y, "bi"); b.px(px0 + 1, y, "bi_d")
    for x in range(x0, x1):
        i = min(n - 1, int((x - x0) / run))
        y = ytop + int((x - x0) * 8 / run) - 40
        b.px(x, y, "bi_lit"); b.px(x, y + 1, "bi"); b.px(x, y + 2, "bi_d")


def build_back():
    b = Img(W, H)
    st = STAIRS
    # the stretches of houses between the flights; alleys at the flights (30 px before, 30 after)
    cuts = [(0, st[0] - 30)] + [(st[i] + 46, st[i + 1] - 30) for i in range(len(st) - 1)]
    for si, (a, z) in enumerate(cuts):
        stretch_houses(b, a, z, si)
        if si > 0: alley(b, cuts[si - 1][1], a)
    # the quay: houses from the last flight to the cliff, the cliff and Mia's stair, then the open harbour
    qa, cl = st[-1] + 46, CLIFF_X
    alley(b, cuts[-1][1], qa)
    stretch_houses(b, qa, cl, len(cuts))
    stairs = next(p for p in PROPS if p["name"] == "STAIRS")
    cliff(b, cl, stairs["x0"], stairs["y0"])
    # the upper terrace's houses behind the railing (their base on the coping)
    up = house(6, "salmon", {1: "green", 4: "door"}, 99, EDGE, EDGE)
    b.paste(up, cl, stairs["y0"] - 4 - up.h)
    railing_run(b, cl, stairs["x0"], stairs["y0"])
    mia_stair(b, stairs["x0"], stairs["x1"], stairs["y0"], stairs["y1"])
    for x in range(stairs["x1"], W):                                  # the quay's far edge against the harbour: a coping
        base = street_top(x) - 12
        b.px(x, base - 3, "kerb_lit"); b.px(x, base - 2, "kerb_1"); b.px(x, base - 1, "kerb_3")
        if (x - stairs["x1"]) % 46 == 0: b.px(x, base - 2, "kerb_j"); b.px(x, base - 1, "kerb_j")
    return b


# ------------------------------------------------------------------------------------------------ B: the props
# Every piece Pepper stands on or bumps has a 1 px dark outline (ink) on its hit box's own edge pixels, so the art is
# exactly the box. Holders (brackets, arms, chains, wall plates, poles) are decoration: no outline, a darker iron edge.
def outline(img, solid=None):
    """ink on every opaque pixel that touches a transparent one (4-neighbour) or the image's edge"""
    a = img.a[..., 3] > 0 if solid is None else solid
    p = np.pad(a, 1)
    edge = a & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    img.a[edge, :3] = C["ink"]; img.a[edge, 3] = 255


def disc(img, cx, cy, r, c):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r * 0.6: img.px(cx + x, cy + y, c)


def picture(img, kind, cx, cy):
    """the sign's picture (no letters): a coffee cup, a loaf, a fish"""
    if kind == "cup":
        img.rect(cx - 6, cy - 2, 11, 8, "cup"); img.rect(cx - 6, cy - 2, 11, 1, "cup_d")      # the cup, its rim
        img.rect(cx - 5, cy + 6, 9, 1, "cup"); img.rect(cx - 4, cy + 7, 7, 1, "cup_d")
        img.rect(cx + 5, cy, 2, 1, "cup"); img.rect(cx + 7, cy + 1, 1, 3, "cup"); img.rect(cx + 5, cy + 4, 2, 1, "cup")
        img.rect(cx - 9, cy + 8, 17, 1, "cup"); img.rect(cx - 8, cy + 9, 15, 1, "cup_d")     # the saucer
        for i, (dx, dy) in enumerate(((-3, -4), (-2, -5), (-3, -6), (-2, -7), (1, -4), (2, -5), (1, -6), (2, -7))):
            img.px(cx + dx, cy + dy, "cup_d")                                                # the steam
    elif kind == "loaf":
        for y in range(-4, 5):
            hw = int(round(9 * math.sqrt(max(0, 1 - (y / 5.2) ** 2))))
            img.rect(cx - hw, cy + y, hw * 2, 1, "lid_lit" if y < -1 else ("lid" if y < 3 else "lid_d"))
        for k in (-5, 0, 5): img.px(cx + k - 1, cy - 2, "cup"); img.px(cx + k, cy - 3, "cup"); img.px(cx + k + 1, cy - 4, "cup")
    elif kind == "fish":
        for y in range(-4, 5):
            hw = int(round(8 * math.sqrt(max(0, 1 - (y / 5.0) ** 2))))
            img.rect(cx - hw - 2, cy + y, hw * 2, 1, "cup" if y < 2 else "cup_d")
        for y in range(-4, 5): img.rect(cx + 6, cy + y, 1 + (abs(y) > 1), 1, "cup")             # the tail
        img.px(cx - 6, cy - 1, "board_d")


def sign_set(pic):
    """a hanging sign on its bracket: the bar 48 x 4 fixed to the wall by a plate at each end, two chains, the board
    32 x 37 (outlined) with a picture. The image's (0, 0) is world (bracket x0 - 1, bracket y0 - 3)."""
    img = Img(50, 51)
    bx0 = 1                                                     # bracket x0
    for px0 in (bx0, bx0 + 44):                                 # the wall plates
        img.rect(px0, 0, 4, 10, "iron_d"); img.rect(px0, 0, 1, 10, "iron"); img.px(px0 + 2, 2, "iron_lit"); img.px(px0 + 2, 7, "iron_lit")
    img.rect(bx0, 3, 48, 1, "iron_lit"); img.rect(bx0, 4, 48, 2, "iron"); img.rect(bx0, 6, 48, 1, "iron_d")
    for i in range(10):                                          # a scroll over the bar's middle
        img.px(bx0 + 19 + i, 2 - (1 if 2 < i < 7 else 0), "iron")
    for chx in (bx0 + 12, bx0 + 35):                             # the chains: links of 2 and 1 px
        for y in range(7, 13):
            if y % 2: img.rect(chx, y, 2, 1, "iron")
            else: img.px(chx, y, "iron_d"); img.px(chx + 1, y, "iron_d") if False else None
    b = Img(32, 37)
    b.rect(0, 0, 32, 37, "board"); b.rect(2, 2, 28, 33, "board_d"); b.rect(3, 3, 26, 31, "board")
    b.rect(2, 2, 28, 1, "board_lit"); b.rect(2, 2, 1, 33, "board_lit")
    picture(b, pic, 16, 18)
    outline(b)
    img.paste(b, bx0 + 8, 13)
    return img


def awning_set():
    """the low striped awning (32 x 39, outlined) hanging from its iron arm (4 x 26) fixed to the wall. Image (0, 0)
    is world (awning x0 - 1, arm y0 - 2)."""
    img = Img(35, 68)
    ax = 1 + 28                                                  # the arm box's x0 (1508 - 1479)
    img.rect(ax - 1, 0, 6, 6, "iron_d"); img.rect(ax - 1, 0, 1, 6, "iron"); img.px(ax + 2, 2, "iron_lit")   # the plate
    for y in range(2, 28): img.px(ax + 1, y, "iron_lit"); img.px(ax + 2, y, "iron_d")
    a = Img(32, 39)
    for x in range(32):
        stripe = "red" if (x // 4) % 2 == 0 else "cream"
        for y in range(3, 33): a.px(x, y, stripe)
        a.px(x, 3, "red_lit" if stripe == "red" else "cream")
        u = x % 8                                                   # the scalloped valance, one scallop per pair
        depth = (4, 5, 6, 6, 6, 6, 5, 4)[u]
        for y in range(33, 33 + depth): a.px(x, y, "red_d" if stripe == "red" else "cream_d")
    a.rect(0, 0, 32, 3, "iron"); a.rect(0, 0, 32, 1, "iron_lit")    # the top rail
    outline(a)
    img.paste(a, 1, 28)
    return img


def balcony(w):
    """an iron balcony w wide: its railing 1 m (46 rows, drawn behind Pepper), the stone slab (the one-way top) and
    stone corbels into the wall. (w + 2) x 60; the slab's ink row 46 is the box's top - 1."""
    img = Img(w + 2, 60)
    R = 46
    # the railing: top rail, two lower rails, posts every ~20 px, bars every 4 px
    n = max(2, round(w / 20))
    posts = [1 + round(i * (w - 3) / n) for i in range(n + 1)]
    for x in range(1, w + 1):
        img.px(x, 0, "ink"); img.px(x, 1, "iron_lit"); img.px(x, 2, "iron"); img.px(x, 3, "iron_d")
        for y in (30, 31, 42, 43): img.px(x, y, "iron" if y % 2 == 0 else "iron_d")
        if (x - 1) % 4 == 2:
            for y in range(4, 30): img.px(x, y, "iron")
            for y in range(32, 42): img.px(x, y, "iron")
    for px0 in posts:
        for y in range(0, R): img.px(px0, y, "ink"); img.px(px0 + 1, y, "iron_lit"); img.px(px0 + 2, y, "ink")
    for px0 in posts[:-1]:                                         # a ring in each panel's middle
        mx = px0 + (posts[posts.index(px0) + 1] - px0) // 2 + 1
        for (dx, dy) in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            img.px(mx + dx, 17 + dy, "iron")
    # the slab: rows 46-52, stone, lit top; ink round it
    s = Img(w + 2, 14)
    s.rect(0, 0, w + 2, 7, "stone"); s.rect(1, 1, w, 1, "stone_lit"); s.rect(1, 5, w, 1, "stone_d")
    cor = [4] + ([4 + round(i * (w - 14) / max(1, round(w / 60))) for i in range(1, round(w / 60))]) + [w - 10]
    for cx in cor:                                                 # corbels: stone consoles tapering into the wall
        for r, (dx, ww) in enumerate(((0, 8), (0, 8), (1, 6), (1, 6), (2, 4), (2, 4))):
            s.rect(cx + dx, 7 + r, ww, 1, "stone" if r < 4 else "stone_d")
            s.px(cx + dx, 7 + r, "stone_lit")
    outline(s)
    img.paste(s, 0, 46)
    return img


def terrace(w=56, h=24):
    """a cafe's timber deck on posts (w x h, outlined): the plank top, a fascia beam, skirt boards, corner posts"""
    t = Img(w, h)
    t.rect(0, 0, w, 4, "wood"); t.rect(0, 1, w, 1, "wood_lit"); t.rect(0, 3, w, 1, "wood_d")
    t.rect(0, 4, w, 3, "lid"); t.rect(0, 4, w, 1, "lid_lit")
    for x in range(w):
        for y in range(7, h):
            t.px(x, y, "wood_d" if (x % 5 == 0) else ("lid_d" if y > h - 4 else "lid"))
    for px0 in (1, w - 6):
        t.rect(px0, 4, 5, h - 4, "wood"); t.rect(px0, 4, 1, h - 4, "wood_lit"); t.rect(px0 + 4, 4, 1, h - 4, "wood_d")
    outline(t)
    return t


def cart():
    """the fruit cart (40 x 40, outlined): two crates of apples and pears on a plank bed, two spoked wheels"""
    c = Img(40, 40)
    for k, fruit in ((0, "red"), (1, "door_lit")):
        x0 = 1 + k * 19
        c.rect(x0, 0, 19, 14, "lid"); c.rect(x0, 0, 19, 1, "lid_lit")
        c.rect(x0 + 1, 1, 17, 4, "board_d")
        for i in range(4): disc(c, x0 + 3 + i * 4, 3, 1, fruit); c.px(x0 + 3 + i * 4, 2, "cream")
        for y in (6, 10): c.rect(x0 + 1, y, 17, 1, "lid_d")
        c.rect(x0, 0, 1, 14, "lid_d")
    c.rect(0, 14, 40, 12, "wood"); c.rect(0, 14, 40, 1, "wood_lit")
    for y in (17, 20, 23): c.rect(0, y, 40, 1, "wood_d")
    for wx in (9, 30):
        disc(c, wx, 31, 8, "iron")
        disc(c, wx, 31, 6, "lid_d")
        for a in range(8):
            for r in range(1, 7):
                c.px(wx + int(round(r * math.cos(a * math.pi / 4))), 31 + int(round(r * math.sin(a * math.pi / 4))), "lid_lit")
        disc(c, wx, 31, 1, "iron")
    sol = c.a[..., 3] > 0
    outline(c, sol)
    return c


def bollard():
    """a cast-iron mooring bollard 12 x 14, outlined: a cap, a waist, the body, lit left"""
    b = Img(12, 14)
    b.rect(0, 0, 12, 3, "iron"); b.rect(2, 3, 8, 2, "iron_d"); b.rect(1, 5, 10, 9, "iron")
    b.rect(1, 0, 1, 3, "iron_lit"); b.rect(2, 5, 1, 9, "iron_lit"); b.rect(9, 5, 1, 9, "iron_d")
    outline(b)
    return b


def planter():
    """(phase 1 stand-in for the parked BIKES, 40 x 20: the plan's true-scale scooters are a render) a wooden flower
    trough with red geraniums, outlined"""
    p = Img(40, 20)
    p.rect(0, 7, 40, 11, "lid"); p.rect(0, 7, 40, 1, "lid_lit")
    for x in range(4, 40, 9): p.rect(x, 8, 1, 10, "lid_d")
    p.rect(2, 18, 5, 2, "wood_d"); p.rect(33, 18, 5, 2, "wood_d")
    for i in range(9):
        cx = 3 + i * 4 + (i % 2)
        p.rect(cx - 1, 3, 4, 4, "door"); p.px(cx, 2, "door_lit")
        if i % 2 == 0: disc(p, cx + 1, 2, 2, "red"); p.px(cx, 1, "red_lit")
    outline(p)
    return p


def railing_end():
    """the quay railing at the level's end (24 x 36, outlined): two posts, three rails, bars, a lifebuoy"""
    r = Img(24, 36)
    for x in range(24):
        for y in (0, 1, 2): r.px(x, y, ("iron_lit", "iron", "iron_d")[y])
        for y in (17, 18, 32, 33): r.px(x, y, "iron" if y % 2 else "iron_d")
    for x in range(3, 22, 4):
        for y in range(3, 36): r.px(x, y, "iron")
    for px0 in (0, 20):
        r.rect(px0, 0, 4, 36, "iron"); r.rect(px0, 0, 1, 36, "iron_lit"); r.rect(px0 + 3, 0, 1, 36, "iron_d")
    sol = r.a[..., 3] > 0
    outline(r, sol)
    for y in range(-8, 9):                                          # the lifebuoy, red and cream quarters, its own ink
        for x in range(-8, 9):
            d = math.sqrt(x * x + y * y)
            if 3.2 <= d <= 7.9:
                if d > 7.0 or d < 4.0: c = "ink"
                else:
                    ang = (math.degrees(math.atan2(y, x)) + 360 + 45) % 360
                    c = "cream" if int(ang // 90) % 2 else "red"
                    if c == "red" and y < -1 and x < 0: c = "red_lit"
                r.px(12 + x, 12 + y, c)
    outline(r)
    return r


def arch_set(street):
    """the low arch (a passage through a house, Söder's grändportal): the arch block 32 x 61 (outlined: she crawls
    under it) of granite ashlar with a ring of voussoirs and a keystone over the passage, and its two piers (8 px,
    decoration, no outline) standing on the street's back edge. Image (0, 0) = world (arch x0 - 8, arch y0)."""
    a = Img(48, street - 12 - 112)
    hh = a.h
    for px0 in (0, 40):                                             # the piers: quoins of 9 + 7 rows, lit tops
        for y in range(hh):
            k, r, n = wall_course(y + 112)
            for x in range(px0, px0 + 8):
                c = "kerb_2" if (k % 2 == 0) else "kerb_1"
                if r == 0: c = "kerb_lit"
                if r == n - 1: c = "kerb_j"
                if x == px0 + 7 and px0 == 0: c = "kerb_3"
                if x == px0 and px0 == 40: c = "kerb_3"
                a.px(x, y, c)
    for px0 in (0, 40):                                             # the piers' caps
        a.rect(px0, 0, 8, 1, "stone_lit"); a.rect(px0, 1, 8, 2, "stone"); a.rect(px0, 3, 8, 1, "stone_d")
    b = Img(32, 61)
    for y in range(61):
        k, r, n = wall_course(y + 112)
        for x in range(32):
            i, bx = (x + (k % 2) * 8) // 16, 0
            c = "kerb_1" if (k + i) % 2 else "kerb_2"
            if r == 0: c = "kerb_lit"
            if r == n - 1 or (x + (k % 2) * 8) % 16 == 0: c = "kerb_j"
            b.px(x, y, c)
    # the arch ring over the passage: voussoirs between two circles centred under the block
    cx, cy = 15.5, 72
    for y in range(36, 61):
        for x in range(32):
            d = math.hypot(x - cx, y - cy)
            if 20 <= d <= 27:
                ang = math.degrees(math.atan2(y - cy, x - cx))
                seg = int((ang + 180) // 12)
                c = "stone" if seg % 2 else "stone_lit"
                if abs(x - cx) < 2.5 and y < 52: c = "stone_lit"            # the keystone
                if d > 26.2: c = "stone_d"
                b.px(x, y, c)
            elif d < 20:
                b.px(x, y, "kerb_3")                                    # the passage's shadowed soffit
    outline(b)
    a.paste(b, 8, 0)
    return a


def build_props():
    P = {}
    for pic in ("cup", "loaf", "fish"): P["sign_" + pic] = sign_set(pic)
    P["awning"] = awning_set()
    for p in PROPS:
        if p["name"] == "BALCONY": P[f"balcony{p['x1'] - p['x0']}"] = balcony(p["x1"] - p["x0"])
    P["terrace"] = terrace(); P["cart"] = cart(); P["bollard"] = bollard(); P["planter"] = planter()
    P["railing"] = railing_end()
    ar = next(p for p in PROPS if p["name"] == "ARCH")
    P["arch"] = arch_set(street_top(ar["x0"]))
    return P


# ------------------------------------------------------------------------------------------------ E: the backdrop
# The sky is built by tools/build_sky.py's own rules (flat tones with stepped wavy joins, streaks, stamped cumulus
# lobes), given Söder's golden evening; the far city is build_sky's skyline recoloured (one clean warm shape, a rim).
SKY = dict(
    seed=508, light=(-0.78, -0.62), camymax=0,
    tones=[("e8b274", None, 0), ("efbc76", 30, 4), ("f4c67c", 62, 4), ("f8d28a", 92, 3), ("fadca0", 118, 3)],
    streaks=[(2, 52, 4, (60, 150), (2, 3)), (3, 82, 4, (70, 180), (2, 3)), (4, 110, 4, (80, 200), (2, 4))],
    cloud=dict(lit1="fff2d8", lit2="fde0b4", body="f4c89e", under="e8b090"),
    banks=[dict(x=40, w=210, base=46, h=34, peak=0.40, r=(8, 16), under=(3, 6)),
           dict(x=520, w=260, base=60, h=30, peak=0.55, r=(8, 14), under=(3, 6))],
    low=[dict(x=150, w=180, base=100, h=7), dict(x=620, w=200, base=104, h=6)],
    wisps=[(330, 16, 30, 4), (840, 24, 24, 3)],
    city=dict(main="dcae98", near="d2a492", rim="fde6b8", rim_edges=("left", "top")),
)


def build_sky_files():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import build_sky as BS
    BS.LEVELS["soder"] = SKY
    rgb, _img, _n, _stats = BS.build_sky("soder")
    city = BS.build_skyline("soder")
    sky = np.zeros(rgb.shape[:2] + (4,), np.uint8); sky[..., :3] = rgb; sky[..., 3] = 255
    return sky[120:], city                                         # a flat level: the screen's rows only


def build_far():
    """the harbour (far layer, below the far city): flat evening water, two tones in long bands, the sun's glints in
    short flat dashes, 320 wide (it repeats), 120 tall"""
    f = Img(320, 120)
    f.rect(0, 0, 320, 120, "water_1")
    f.rect(0, 0, 320, 2, "water_lit")                              # the far shore's light line
    for y in range(8, 120, 9):                                     # long darker bands, nearer ones longer
        for x0 in range(h32(y, 1) % 40, 320, 60 + y // 2):
            f.rect(x0, y, 24 + y // 3, 1, "water_2")
    for y in range(4, 60, 5):                                      # the sun's glints, flat dashes
        for x0 in range(h32(y, 2) % 50, 320, 70):
            f.rect(x0, y, 6 + (y % 3) * 2, 1, "water_lit")
    return f


MID_W, MID_H = 2400, 240


def build_mid():
    """the roofs down the hill (mid layer, about 23 px a metre): plaster upper storeys with small 4-pane windows and
    tin roofs with standing seams and chimneys, stepping down left to right; the row ends in a gable at MID_W - 80
    (the harbour opens beyond it). Row 20 is the ridge line's mean."""
    m = Img(MID_W, MID_H)
    x, i = 0, 0
    walls = ("mid_wall_a", "mid_wall_b", "mid_wall_c")
    end = MID_W - 80
    while x < end:
        w = min(end - x, 70 + h32(i, 1) % 60)
        if end - x - w < 50: w = end - x
        ridge = 20 + (h32(i, 2) % 3 - 1) * 6
        eave = ridge + 14
        col = walls[i % 3]
        m.rect(x, eave, w, MID_H - eave, col)
        m.rect(x, eave, 1, MID_H - eave, "mid_chim")                # the house's lit corner
        for wy in (eave + 8, eave + 42, eave + 76):                 # windows: 12 x 18, stamped on a 22 px grid
            for wx in range(x + 8, x + w - 14, 22):
                m.rect(wx, wy, 12, 18, "mid_win"); m.rect(wx, wy, 12, 1, "mid_chim")
                m.rect(wx + 5, wy, 2, 18, col); m.rect(wx, wy + 7, 12, 2, col)
        for y in range(ridge, eave):                                # the roof: a front-on slope, seams every 4 px
            k = y - ridge
            for xx in range(x - 2 + 0, x + w + 2):
                m.px(xx, y, "mid_roof_d" if (xx - x) % 4 == 0 else "mid_roof")
            m.px(x - 2, y, "mid_roof_d")
        m.rect(x - 2, ridge, w + 4, 1, "mid_chim")                  # the ridge, lit
        if w > 60:                                                  # a chimney
            cx = x + 12 + h32(i, 3) % (w - 30)
            m.rect(cx, ridge - 10, 6, 11, "mid_chim"); m.rect(cx - 1, ridge - 11, 8, 2, "mid_roof_d")
        x += w; i += 1
    return m


# ------------------------------------------------------------------------------------------------ output
def tiles(img, name, files):
    for i in range(0, W, TILE):
        files[f"{name}_{i // TILE:02d}.png"] = img.a[:, i:i + TILE].copy()


def palette_lua():
    lines = ["-- Söder Hill's palette (tools/build_soder_art.py writes this file from its PAL table: edit it there)",
             "return {"]
    for k in sorted(PAL):
        r, g, b_ = hexc(PAL[k])
        lines.append(f"  {k} = {{ {r / 255:.4f}, {g / 255:.4f}, {b_ / 255:.4f} }},")
    lines.append("}")
    return "\n".join(lines) + "\n"


def preview(files, ground, back, outdir):
    os.makedirs(outdir, exist_ok=True)
    sky = np.zeros((H, W, 3), np.uint8); sky[:] = C["sky_2"]
    im = Image.fromarray(sky, "RGB").convert("RGBA")
    im.alpha_composite(Image.fromarray(back.a, "RGBA"))
    im.alpha_composite(Image.fromarray(ground.a, "RGBA"))
    for i in range(0, W, 1280):
        part = im.crop((i, 0, i + 1280, H))
        part.save(os.path.join(outdir, f"level_{i:04d}.png"))
    im.convert("L").save(os.path.join(outdir, "level_grey.png"))
    im.save(os.path.join(outdir, "level.png"))


def main():
    check = "--check" in sys.argv
    pdir = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    files = {}
    ground, front = build_ground()
    back = build_back()
    tiles(ground, "ground", files)
    tiles(front, "front", files)
    tiles(back, "back", files)
    for n, im in build_props().items(): files["props/" + n + ".png"] = im.a
    sky, city = build_sky_files()
    files["sky.png"], files["skyline.png"] = sky, city
    files["far.png"], files["mid.png"] = build_far().a, build_mid().a
    fails = []
    if max(HOUSE_COLOURS) > 20: fails.append(f"a house has {max(HOUSE_COLOURS)} colours (back layer: 20)")
    print("houses:", len(HOUSE_COLOURS), "colours per house", min(HOUSE_COLOURS), "to", max(HOUSE_COLOURS))
    if check:
        for n, arr in files.items():
            p = os.path.join(OUT, n)
            if not os.path.exists(p): fails.append("missing " + n); continue
            d = np.array(Image.open(p).convert("RGBA"))
            if d.shape != arr.shape or (d != arr).any(): fails.append(n + " is not what build_soder_art.py builds")
        if open(os.path.join(OUT, "palette.lua")).read() != palette_lua(): fails.append("palette.lua differs")
    else:
        os.makedirs(os.path.join(OUT, "props"), exist_ok=True)
        for n, arr in files.items():
            Image.fromarray(arr, "RGBA").save(os.path.join(OUT, n), optimize=True)
        open(os.path.join(OUT, "palette.lua"), "w").write(palette_lua())
    if pdir: preview(files, ground, back, pdir)
    for f in fails: print("FAIL", f)
    print("build_soder_art:", "OK" if not fails else f"{len(fails)} problems", f"({len(files)} files)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
