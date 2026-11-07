#!/usr/bin/env python3
"""build_sky.py: the painted sky of River Walk, City Park and Downtown, BUILT by rule (day of 7 Nov 2026, owner on the
board card "haze": "the sky now feels very technical, this doesnt feel like a gradient, we need something more
artistic"). Design target: art/gen/concepts/sky_paint_rw_a.png and _b.png (reference only, never cut).

  python3 -I tools/build_sky.py            write riverwalk/art/scene/sky_<level>.png and skyline_<level>.png
                                            (+ art/source/sky/<level>.json: the tones and their pixel counts)
  python3 -I tools/build_sky.py --check    fail if a file on disk is not what this script builds, or a rule is broken
  python3 -I tools/build_sky.py --sheet D  also write previews (1x and 3x, colour and greyscale) into folder D

The sky (one PNG per level, 960 x 360, opaque, row 0 = screen y -120: the rows above y 0 are a tall level's sky,
Look.SKY_ABOVE; look.lua draws rows 120-359 in a flat level). 1 art px = 1 game px, it wraps seamlessly sideways
(look.lua scrolls it at 0.05 of the camera plus a slow drift).
  * 4 to 6 flat sky tones laid as long horizontal shapes: each join between two tones is a slow wave held in flat
    runs of 6 to 20 px, so it steps by 1 px at a time. No straight full-width band, no dither, no blend.
  * long calm streaks low down (the concept's b): thin lenses of the next lighter tone with stepped, tapered ends.
  * cumulus banks of stamped round lobes: each lobe is drawn once per radius (lit top in 2 tones, body) and stamped on
    the integer grid, left to right, so every lobe keeps its sunlit top-left; then the cool underside along the bank's
    flat bottom (a row of small scallops). A low long bank rests behind the skyline, a few small wisps high up.
  * cloud tones never darker than luma 185 (docs/layer_ladder.md, clouds row), 4 cloud colours.
The skyline (skyline_<level>.png, 320 x 77, from the approved skyline.png, which is not changed): the concept's far
city, one clean light blue-violet shape (2 tones: the far parts and the nearer, darker parts of the drawing), with a
1 px warm rim on its lit edges (left and top: the sun is upper left; Downtown's high sun: top only). Its colours are
final: look.lua draws it with a neutral city look (no haze on top)."""
import os, sys, json, math
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "riverwalk/art/scene")
SRC = os.path.join(ROOT, "art/source/sky")
W, H, TOP = 960, 360, -120                      # TOP: the screen y of row 0
W601 = np.array([0.299, 0.587, 0.114])


def hexc(h): return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def luma(c): return float(np.dot(W601, c))


# ------------------------------------------------------------------------------------------------ the three skies
# tones: (colour, the screen y where this tone starts at its mean, the join's wave amplitude in px[, options]), top to
# bottom; options: jit = how far each flat run may wander from the slow wave (px), extra = more tongues on this join,
# shorter and overlapping the first ones, tl = the tongues' length range.
# camymax: a tall level's vertical camera range; at the top of the world the screen's top row is file row
# 120 - round(camymax * 0.3) (vcam.lua, the far layers rise 0.3), and no cloud may be cut there (--check).
# streaks: (tone index drawn, centre y, how many, length range, thickness range).
# banks: dict(x = left edge, w, base = flat bottom's screen y, h = height of the tallest lobe, peak = where along the
#   bank the tallest part is (0-1), r = lobe radius range, under = the underside's scallop height range, tail = long
#   thin tails at the base). low: flat soft banks behind the skyline (x, w, base, h), no scallops (concept b).
#   wisps: (x, y, w, h).
# light: the direction the light comes from (x, y), y up negative. rim: which edges of the skyline take the warm rim.
LEVELS = {
    "riverwalk": dict(                                                  # summer morning, warm low sun upper left
        seed=1994, light=(-0.62, -0.78), camymax=0,
        tones=[("4a80c6", None, 0), ("6293cc", 40, 4), ("8cb0d6", 55, 4), ("c3cfd0", 68, 3), ("f0e2c0", 80, 3)],
        streaks=[(2, 50, 4, (60, 150), (2, 3)), (3, 63, 4, (70, 180), (2, 3)), (4, 75, 4, (80, 200), (2, 4)),
                 (3, 86, 3, (40, 110), (1, 2))],
        cloud=dict(lit1="fff6e0", lit2="f1e0c4", body="c6cfe8", under="acbae2"),
        banks=[dict(x=18, w=232, base=52, h=44, peak=[(0.34, 1.0, 0.42), (0.78, 0.55, 0.25)], r=(8, 22), under=(4, 8)),
               dict(x=520, w=300, base=60, h=38, peak=[(0.30, 0.62, 0.30), (0.68, 1.0, 0.36)], r=(7, 20), under=(4, 7)),
               dict(x=330, w=120, base=30, h=14, peak=0.45, r=(5, 8), under=(2, 4))],
        low=[dict(x=150, w=190, base=94, h=8), dict(x=372, w=120, base=92, h=6), dict(x=690, w=210, base=91, h=9),
             dict(x=930, w=90, base=95, h=5)],
        wisps=[(240, 16, 26, 4), (458, 9, 36, 5), (290, 22, 14, 3), (880, 14, 30, 4), (618, 20, 18, 3)],
        city=dict(main="9aaee0", near="8ea2d6", rim="e8bb7c", rim_edges=("left", "top")),
    ),
    "citypark": dict(                                                   # golden autumn afternoon, warm amber glow
        seed=2610, light=(-0.70, -0.71), camymax=144,
        # (round 2) the warm joins wander (jit) and are cut by extra shorter tongues that overlap: no long even slope
        tones=[("a8c2ee", None, 0), ("b6cbee", -40, 5), ("c6d2ea", 34, 5),
               ("ead6bc", 82, 3, dict(jit=1, extra=4, tl=(60, 180))), ("f4cd98", 104, 3, dict(jit=1, extra=3, tl=(60, 180))),
               ("f5c37e", 128, 3, dict(jit=1, extra=2, tl=(60, 180)))],
        streaks=[(3, 74, 4, (70, 180), (2, 3)), (4, 96, 4, (80, 200), (2, 4)), (5, 118, 4, (60, 160), (2, 3)),
                 (2, 22, 3, (60, 140), (1, 2)), (1, -60, 3, (60, 140), (1, 2))],
        cloud=dict(lit1="fff0d2", lit2="fad9aa", body="d8cee6", under="bdb4de"),
        banks=[dict(x=40, w=260, base=64, h=40, peak=0.40, r=(9, 17), under=(4, 9)),
               dict(x=560, w=230, base=56, h=32, peak=0.55, r=(8, 14), under=(4, 8)),
               dict(x=200, w=200, base=-12, h=22, peak=0.40, r=(7, 12), under=(3, 6))],   # (round 2: top row 86, was 64)
        low=[dict(x=120, w=150, base=110, h=6), dict(x=380, w=170, base=113, h=7), dict(x=620, w=90, base=108, h=5),
             dict(x=800, w=130, base=112, h=6)],
        wisps=[(360, 18, 30, 4), (470, 8, 18, 3), (900, 24, 34, 5), (860, -18, 26, 4)],
        # (round 2) the fill a step darker and a quarter less violet, so the city parts from the amber glow
        city=dict(main="bab8d2", near="b2b0ca", rim="fde6b4", rim_edges=("left", "top")),
    ),
    "downtown": dict(                                                   # bright midday, high white sun, clean blues
        seed=1110, light=(-0.30, -0.95), camymax=240,
        tones=[("3e7ac8", None, 0), ("4a86d0", -40, 5), ("6aa0da", 22, 5), ("98c0e4", 62, 4), ("c6deee", 94, 3),
               ("e8f2f4", 120, 3)],
        streaks=[(4, 88, 4, (60, 160), (2, 3)), (5, 112, 4, (80, 200), (2, 3)), (3, 54, 3, (60, 140), (1, 2))],
        cloud=dict(lit1="ffffff", lit2="eef4fa", body="d8e4f2", under="c4d6ee"),
        banks=[dict(x=60, w=170, base=40, h=30, peak=0.45, r=(8, 14), under=(2, 3)),
               dict(x=470, w=200, base=56, h=30, peak=0.50, r=(8, 14), under=(2, 3)),
               dict(x=760, w=130, base=-10, h=22, peak=0.45, r=(7, 11), under=(2, 3)),
               dict(x=250, w=150, base=-42, h=22, peak=0.50, r=(7, 12), under=(2, 3))],   # (round 2: top row 56, was 36)
        low=[dict(x=260, w=170, base=104, h=6), dict(x=480, w=110, base=101, h=5), dict(x=760, w=160, base=100, h=6)],
        wisps=[(330, 14, 30, 4), (640, 6, 22, 3), (900, 28, 26, 4), (560, -40, 24, 3)],
        # (DT follow-up, 7 Nov) behind the rebuilt tall houses the far city is low and simple: tops only, a few broad
        # roof and dome shapes, no spires or thin towers (low = the tops' height range in px: build_sky.low_city)
        city=dict(main="c6d2e8", near="c0cee6", rim="eef2f4", rim_edges=("top",), low=(20, 28)),
    ),
}
ROLES = ("sky", "cloud")


# ------------------------------------------------------------------------------------------------ helpers
class Rng:
    """a tiny LCG (the game's rng): the same numbers on every machine"""
    def __init__(self, seed): self.s = seed

    def __call__(self, a, b):
        self.s = (self.s * 1103515245 + 12345) % 2147483648
        return a + (self.s % 100000) / 100000 * (b - a)

    def i(self, a, b): return int(math.floor(self(a, b + 0.999)))


def runs(r, lo=6, hi=20):
    """cut [0, W) into flat runs of lo-hi px (the last one ends exactly at W)"""
    xs, x = [], 0
    while x < W:
        n = r.i(lo, hi)
        if W - (x + n) < lo: n = W - x
        xs.append((x, x + n)); x += n
    return xs


def profile(r, L, t):
    """the thickness along a lens (a tongue, a streak, a low bank) of length L and up to t px: it grows 1 px at a
    time from 1 px at each end, each step after a flat run of 6-20 px chosen apart for each side, so its edges are
    uneven stairs, never a ruled slope; the 1 px ends are 6 px or longer"""
    t = max(1, min(t, 1 + (L // 2) // 6))
    def side():
        st = [r.i(6, 20) for _ in range(t - 1)]
        while sum(st) > L // 2 and any(v > 6 for v in st): st = [max(6, v - 2) for v in st]
        out, pos = np.ones(L, int), 0
        for v in st:
            pos += v
            if pos < L: out[pos:] += 1
        return out
    left, right = side(), side()[::-1]
    return np.minimum(np.minimum(left, right), t)


def wave(r, amp, jit=0):
    """a join's y offset per column: two slow sines with a whole number of periods across W (so it wraps), held flat
    over each run, rounded; neighbouring runs differ by at most 1 px"""
    if amp == 0: return np.zeros(W, int)
    k1, k2 = r.i(1, 3), r.i(4, 7)
    p1, p2 = r(0, 1), r(0, 1)
    out = np.zeros(W, int)
    prev = None
    for a, b in runs(r):
        m = (a + b) / 2
        v = amp * (0.65 * math.sin(2 * math.pi * (k1 * m / W + p1)) + 0.35 * math.sin(2 * math.pi * (k2 * m / W + p2)))
        v = int(round(v)) + (r.i(-jit, jit) if jit else 0)
        if prev is not None: v = max(prev - 1, min(prev + 1, v))
        out[a:b] = v; prev = v
    # the wrap: walking back from the end, each run within 1 px of the one after it (the last one of column 0's run)
    edges = [0] + [x for x in range(1, W) if out[x] != out[x - 1]] + [W]
    nxt = out[0]
    for a, b in reversed(list(zip(edges, edges[1:]))):
        v = max(nxt - 1, min(nxt + 1, out[a]))
        if v == out[a]: break
        out[a:b] = v; nxt = v
    return out


def lobe(r, light, cut=(0.86, 0.66), off=0.8):
    """one round lobe of radius r, drawn once: 0 outside, 1 lit top, 2 lit edge, 3 body. The shading is a set of
    crescents: a pixel's distance from a point `off` r away from the light (down-right of the centre) decides its tone,
    so the lit tones hug the lobe's rim on the light's side (cut: the two distances, in radii)"""
    lx, ly = light
    n = int(math.ceil(r)) + 1
    px_, py_ = -lx * r * off, -ly * r * off
    st = np.zeros((2 * n + 1, 2 * n + 1), np.uint8)
    for dy in range(-n, n + 1):
        for dx in range(-n, n + 1):
            if dx * dx + dy * dy > r * r + r * 0.6: continue
            q = math.hypot(dx - px_, dy - py_) / max(1.0, r)
            st[dy + n, dx + n] = 1 if q > cut[0] else (2 if q > cut[1] else 3)
    return st, n


STAMPS = {}


def stamp(img, role, x, y, r, base, light, toneidx, cut=(0.86, 0.66)):
    """stamp the lobe of radius r with its centre at (x, y) (screen y), cut flat at the bank's base"""
    key = (r, light, cut)
    if key not in STAMPS: STAMPS[key] = lobe(r, light, cut)
    st, n = STAMPS[key]
    for dy in range(-n, n + 1):
        yy = y + dy
        if yy > base: break
        row = yy - TOP
        if row < 0 or row >= H: continue
        for dx in range(-n, n + 1):
            t = st[dy + n, dx + n]
            if t:
                xx = (x + dx) % W
                img[row, xx] = toneidx[t]; role[row, xx] = 1


def bank(img, role, r, b, light, T, sky):
    """a cumulus bank: a back row of big lobes under an envelope (tallest at `peak`), spaced so each keeps a big
    sunlit crescent; a front row of smaller, shaded lobes low down (lit edge and body only); then the underside
    scallops along the flat bottom"""
    x0, w, base, h = b["x"], b["w"], b["base"], b["h"]
    rlo, rhi = b["r"]
    lit = {1: T["lit1"], 2: T["lit2"], 3: T["body"]}
    low = {1: T["lit2"], 2: T["body"], 3: T["body"]}

    peaks = b["peak"] if isinstance(b["peak"], (list, tuple)) else [(b["peak"], 1.0, 0.5)]

    def env(u):                                                         # the top's height along the bank, 0-1: the
        v = 0.22                                                        # highest of its domes (where, how high, how wide)
        for pk, hk, wd in peaks:
            v = max(v, hk * (1 - ((u - pk) / wd) ** 2))
        return min(1.0, v)
    # tier 1, the back row, left to right: few big lobes under the envelope, each new one covering the shaded
    # side of the one before
    x, row1 = x0 + rlo, []
    while x < x0 + w - rlo * 0.6:
        u = (x - x0) / w
        top = base - h * env(u) * r(0.86, 1.08)
        rr = max(rlo, min(rhi, int(round((base - top) / 1.6 + r(-1.5, 1.5)))))
        cy = int(round(top + rr))
        stamp(img, role, int(x), cy, rr, base, light, lit, cut=(0.78, 0.62))
        row1.append((int(x), cy, rr))
        x += max(5, int(rr * r(1.25, 1.6)))
    # tier 2: medium lobes lower down, between and in front of the big ones (their lit tops over the big ones'
    # shaded sides: the bank's puffs read stacked, not in a row)
    for (xa, ya, ra), (xb, yb, rb) in zip(row1, row1[1:]):
        rr = max(rlo, int(min(ra, rb) * r(0.6, 0.8)))
        xm = (xa + xb) // 2 + r.i(-2, 3)
        u = (xm - x0) / w
        cy = base - int(h * env(u) * r(0.30, 0.42))
        stamp(img, role, xm, cy, rr, base, light, lit)
    # body tone only in the lower part of the bank: higher up the shaded side of a lobe is the lit edge tone (no
    # cool slivers between the sunlit tops)
    for xx in range(x0 - 2, x0 + w + 2):
        u = min(1.0, max(0.0, (xx - x0) / w))
        lim = base - int(h * env(u) * 0.42)
        for yy in range(base - h - 2, lim):
            row, cx = yy - TOP, xx % W
            if 0 <= row < H and role[row, cx] and img[row, cx] == T["body"]: img[row, cx] = T["lit2"]
    # the front row: smaller lobes centred near the base, in the shaded tones
    x = x0 + rlo + r.i(2, 8)
    while x < x0 + w - rlo:
        rr = r.i(max(4, rlo - 1), max(5, (rlo + rhi) // 2))
        cy = base - int(rr * r(0.15, 0.45))
        stamp(img, role, int(x), cy, rr, base, light, low, cut=(1.05, 0.9))
        x += max(4, int(rr * r(1.5, 2.1)))
    # the underside: scallops along the base (inside the bank only), flat bottom
    ulo, uhi = b["under"]
    x = x0 - 2
    while x < x0 + w + 2:
        ru = r.i(uhi + 1, uhi + 5)
        hgt = r.i(ulo, uhi)
        for dx in range(-ru, ru + 1):
            hh = int(round(hgt * math.sqrt(max(0.0, 1 - (dx / (ru + 0.5)) ** 2))))
            xx = (int(x) + dx) % W
            for yy in range(base - hh + 1, base + 1):
                row = yy - TOP
                if 0 <= row < H and role[row, xx] == 1: img[row, xx] = T["under"]
        x += max(3, int(ru * r(1.3, 1.9)))
    # (round 2) the flat bottom wanders: in some runs of 6-20 px the bottom row is sky, so the base is never one ruled
    # line under the whole bank
    x, up = x0 - 4, r(0, 1) < 0.5
    row = base - TOP
    while x < x0 + w + 4:
        n = r.i(6, 20)
        if up and 0 <= row < H:
            for xx in range(x, x + n):
                cx = xx % W
                if role[row, cx]: img[row, cx] = sky[row, cx]; role[row, cx] = 0
        x += n; up = not up if r(0, 1) < 0.8 else up


def stratus(img, role, r, b, T):
    """a low flat soft bank resting behind the skyline (the concept's b; round 2: no scallops, no tails): a lens with
    uneven stepped edges, its top row lit, its bottom row the underside, and a second shorter lens on top of it"""
    x0, w, base, h = b["x"], b["w"], b["base"], b["h"]

    def lens(xa, L, ybot, t, under):
        th = profile(r, L, t)
        for k in range(L):
            cx = (xa + k) % W
            for d in range(th[k]):
                row = ybot - d - TOP
                if not 0 <= row < H: continue
                if d == th[k] - 1 and th[k] > 1: img[row, cx] = T["lit1"]
                elif d == 0 and under and th[k] > 2: img[row, cx] = T["under"]
                else: img[row, cx] = T["body"]
                role[row, cx] = 1
    lens(x0, w, base, max(3, h // 2 + 1), True)
    L2 = int(w * r(0.4, 0.6)); xa = x0 + int(w * r(0.1, 0.35))
    lens(xa, L2, base - 2, max(3, h // 2 + 1), False)


def wisp(img, role, x, y, w, h, light, T):
    """a small flat wisp: 2-3 overlapping flattened lobes, lit top tone over a body bottom row"""
    for xx in range(x, x + w):
        u = (xx - x) / max(1, w - 1)
        hh = int(round(h * math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2 * 1.0)) * (1.0 if u < 0.6 else 0.8)))
        hh = max(1, hh)
        for k in range(hh):
            row = y - k - TOP
            if 0 <= row < H:
                img[row, xx % W] = T["body"] if k == 0 else (T["lit2"] if k < hh - 1 or hh <= 2 else T["lit1"])
                role[row, xx % W] = 1


def clean_lone(img, role):
    """a generated pixel with no 8-neighbour of its own tone takes the tone most of its neighbours have (on this
    script's own pixels only, before anything is saved)"""
    for _ in range(2):
        pad = np.pad(img, ((1, 1), (0, 0)), mode="edge")
        pad = np.concatenate([pad[:, -1:], pad, pad[:, :1]], axis=1)    # wraps sideways
        same = np.zeros(img.shape, bool)
        nb = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                v = pad[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
                nb.append(v); same |= v == img
        ys, xs = np.nonzero(~same)
        for y, x in zip(ys, xs):
            vals = [int(n[y, x]) for n in nb]
            img[y, x] = max(set(vals), key=vals.count)
    for _ in range(4):                                                  # no 2x2 checker of two tones
        k00, k01, k10, k11 = img[:-1, :-1], img[:-1, 1:], img[1:, :-1], img[1:, 1:]
        ys, xs = np.nonzero((k00 == k11) & (k01 == k10) & (k00 != k01))
        if not len(ys): break
        for y, x in zip(ys, xs): img[y, x + 1] = img[y, x]


def cloud_faults(img, nsky):
    """(round 2, the reviewer's rule) cloud pixels that are scraps: a stroke narrower than 2 px (not inside any 2 x 2
    block of its own tone, nor a flat horizontal run of 6 px or more: a rim or an underside row), or a piece of one
    tone, or of cloud, under 6 px. Returns two masks: thin, small (the sky wraps sideways)"""
    cl = img >= nsky
    def thin_of(m):
        mr = np.roll(m, -1, axis=1)                                     # the right neighbour (wraps)
        B = np.zeros_like(m)                                            # B[y, x]: the 2x2 block with top-left (y, x)
        B[:-1] = m[:-1] & mr[:-1] & m[1:] & mr[1:]
        blk = B | np.roll(B, 1, axis=1)
        blk[1:] |= B[:-1] | np.roll(B, 1, axis=1)[:-1]
        run = np.zeros(m.shape, int)                                    # horizontal run length through each pixel
        for y in np.nonzero(m.any(axis=1))[0]:
            row = m[y]
            if row.all(): run[y] = W; continue
            start = int(np.argmin(row))                                 # begin at a gap, so runs over the wrap count
            k = 0
            idx = [(start + j) % W for j in range(W)]
            seg = []
            for xx in idx + [None]:
                if xx is not None and row[xx]: seg.append(xx); continue
                for q in seg: run[y, q] = len(seg)
                seg = []
        return m & ~blk & (run < 6)
    thin = np.zeros(img.shape, bool)
    thin |= thin_of(cl)
    for t in np.unique(img[cl]): thin |= thin_of(img == t) & cl
    small = np.zeros(img.shape, bool)
    seen = np.zeros(img.shape, bool)
    for mode in ("cloud", "tone"):
        seen[:] = False
        ys, xs = np.nonzero(cl)
        for y0, x0 in zip(ys, xs):
            if seen[y0, x0]: continue
            key = None if mode == "cloud" else img[y0, x0]
            stack, comp = [(y0, x0)], []
            seen[y0, x0] = True
            while stack:
                y, x = stack.pop(); comp.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, (x + dx) % W
                    if 0 <= yy < H and not seen[yy, xx] and cl[yy, xx] and (key is None or img[yy, xx] == key):
                        seen[yy, xx] = True; stack.append((yy, xx))
            if len(comp) < 6:
                for y, x in comp: small[y, x] = True
    return thin, small


def clean_cloud(img, sky, nsky):
    """remove the scraps cloud_faults finds, on this script's own pixels before saving: a scrap takes the cloud tone
    most of its 8 neighbours have (another tone than its own), or the sky under it when it has no cloud around"""
    for it in range(30):
        thin, small = cloud_faults(img, nsky)
        bad = thin | small
        if not bad.any(): return
        ys, xs = np.nonzero(bad)
        new = img.copy()
        for y, x in zip(ys, xs):
            vals = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    yy, xx = y + dy, (x + dx) % W
                    if 0 <= yy < H and not bad[yy, xx]: vals.append(int(img[yy, xx]))
            cvals = [v for v in vals if v >= nsky and v != img[y, x]]
            ncl = sum(v >= nsky for v in vals)

            def fits(v):                                                # v would sit in a 2x2 block of v here
                for dy in (-1, 0):
                    for dx in (-1, 0):
                        if all((yy == y and xx % W == x) or (0 <= yy < H and img[yy, xx % W] == v)
                               for yy in (y + dy, y + dy + 1) for xx in (x + dx, x + dx + 1)): return True
                return False
            good = sorted({v for v in cvals if fits(v)}, key=lambda v: -cvals.count(v))
            if good and ncl >= 4: new[y, x] = good[0]; continue
            if it >= 12 and ncl == 8:                                   # stuck inside: a block needs one more pixel
                done = False
                for v in sorted(set(cvals), key=lambda v: -cvals.count(v)):
                    for dy in (-1, 0):
                        for dx in (-1, 0):
                            cells = [(yy, xx % W) for yy in (y + dy, y + dy + 1) for xx in (x + dx, x + dx + 1)
                                     if not (yy == y and xx % W == x)]
                            if not all(0 <= yy < H for yy, _ in cells): continue
                            off = [(yy, xx) for yy, xx in cells if img[yy, xx] != v]
                            if len(off) == 1 and img[off[0]] >= nsky:
                                new[y, x] = v; new[off[0]] = v; done = True; break
                        if done: break
                    if done: break
                if done: continue
            if it >= 12 and ncl < 8: new[y, x] = sky[y, x]             # still stuck on an edge: the sky
            elif ncl >= 4 and cvals: new[y, x] = max(set(cvals), key=cvals.count)
            else: new[y, x] = sky[y, x]
        img[:] = new


# ------------------------------------------------------------------------------------------------ build
def build_sky(name):
    c = LEVELS[name]
    r = Rng(c["seed"])
    pal = [hexc(t[0]) for t in c["tones"]]
    T = {}
    for k in ("lit1", "lit2", "body", "under"):
        T[k] = len(pal); pal.append(hexc(c["cloud"][k]))
    nsky = len(c["tones"])
    img = np.zeros((H, W), np.uint8)
    role = np.zeros((H, W), np.uint8)
    # the tones: tone i covers every row at or below its join (mean y + the join's wave)
    joins = []
    for i, tone in enumerate(c["tones"]):
        col, y0, amp = tone[:3]
        opt = tone[3] if len(tone) > 3 else {}
        if y0 is None: img[:, :] = i; continue
        wv = wave(r, amp, opt.get("jit", 0))
        joins.append((i, y0 + wv, opt))
        for x in range(W):
            img[max(0, y0 + wv[x] - TOP):, x] = i
    # tongues: broad long shapes where one tone reaches into its neighbour (up from the join, or down from it), with
    # stepped tapered ends, so no join reads as a ruled line
    def tongue(i, jy, x, L, t, up):
        th = profile(r, L, t)
        for k in range(L):
            xx = (x + k) % W
            for d in range(th[k]):
                row = (jy[xx] - 1 - d if up else jy[xx] + d) - TOP
                if 0 <= row < H: img[row, xx] = i if up else i - 1
    for i, jy, opt in joins:
        x = r.i(0, 120)
        up = r(0, 1) < 0.5
        tl = opt.get("tl", (90, 260))
        while x < W:
            L = r.i(*tl)
            tongue(i, jy, x, L, r.i(3, 7), up)
            x += L + r.i(40, 160); up = not up
        for _ in range(opt.get("extra", 0)):                          # overlapping, shorter, thinner
            tongue(i, jy, r.i(0, W - 1), r.i(tl[0], (tl[0] + tl[1]) // 2), r.i(2, 5), r(0, 1) < 0.5)
    # streaks: thin lenses of tone `ti`, flat bottom, stepped tapered ends
    for ti, yc, n, (llo, lhi), (tlo, thi) in c["streaks"]:
        for _ in range(n):
            L = r.i(llo, lhi); t = r.i(tlo, thi); x0 = r.i(0, W - 1); y = yc + r.i(-4, 4)
            prof = profile(r, L, t)
            for k in range(L):
                for d in range(prof[k]):
                    row = y - d - TOP
                    if 0 <= row < H: img[row, (x0 + k) % W] = ti
    light = tuple(c["light"])
    sky = img.copy()                                                    # the sky under the clouds
    for b in c["low"]: stratus(img, role, r, b, T)
    for x, y, w, h in c["wisps"]: wisp(img, role, x, y, w, h, light, T)
    for b in c["banks"]: bank(img, role, r, b, light, T, sky)
    clean_lone(img, role)
    clean_cloud(img, sky, nsky)
    role = (img >= nsky).astype(np.uint8)
    rgb = np.array(pal, np.uint8)[img]
    stats = dict(tones=[t[0] for t in c["tones"]], cloud=c["cloud"], light=c["light"],
                 counts={("%02x%02x%02x" % pal[i]): int((img == i).sum()) for i in range(len(pal))},
                 roles={"sky": [("%02x%02x%02x" % pal[i]) for i in range(nsky)],
                        "cloud": [("%02x%02x%02x" % pal[i]) for i in range(nsky, len(pal))]},
                 cloud_share=round(float(role.mean()) * 100, 1))
    return rgb, img, nsky, stats


def low_city(lo, hi, seed=320):
    """a low simple far city for Downtown (follow-up, 7 Nov: behind the rebuilt tall houses the full skyline read
    busy): tops only, built from 3 parts drawn by rule and placed on the grid along a 320 px strip that repeats: a flat
    block, a block with a low gable roof (1 px up every 2 px) and a block with a round dome on it. Bodies 14-20 px,
    tops lo-hi px, shapes 18-44 px wide, so nothing thin: no spires, no towers. Returns the silhouette, hi + 2 rows."""
    r = Rng(seed)
    H2, w = hi + 2, 320
    out = np.zeros((H2, w), bool)
    out[H2 - (lo - 6):, :] = True                                        # the continuous base under the tops
    def fill(x0, x1, ytop):
        for x in range(x0, x1): out[max(0, ytop):, x % w] = True
    kinds = ["gable", "dome", "flat", "gable", "flat", "dome", "gable", "flat"]
    x, k = 0, 0
    while x < w:
        bw = r.i(18, 44)
        if w - (x + bw) < 18: bw = w - x                                 # the strip ends exactly at 320
        kind = kinds[k % len(kinds)]; k += 1
        hb = r.i(lo - 4, lo + 2)                                         # body height
        fill(x, x + bw, H2 - hb)
        if kind == "gable":                                              # a low pitched roof, 1 px up every 2 px
            ap = min(bw // 4, hi - hb)
            for d in range(1, ap + 1): fill(x + 2 * d, x + bw - 2 * d, H2 - hb - d)
        elif kind == "dome":                                             # a round dome, centred on the block
            rr = min(bw // 2 - 3, hi - hb)
            cx = x + bw / 2 - 0.5
            for xx in range(x, x + bw):
                dx = xx - cx
                if abs(dx) <= rr:
                    fill(xx, xx + 1, H2 - hb - int(round(math.sqrt(max(0.0, rr * rr - dx * dx)))))
        x += bw + (r.i(0, 6) if x + bw < w - 24 else 0)
    return out


def build_skyline(name):
    """the far city from the approved skyline.png: 2 clean tones and a 1 px warm rim on the lit edges (Downtown: the
    low simple city of low_city, one clean fill and the rim)"""
    c = LEVELS[name]["city"]
    src = np.array(Image.open(os.path.join(SCENE, "skyline.png")).convert("RGBA"))
    a = src[..., 3] > 127
    if c.get("low"):
        a = low_city(c["low"][0], c["low"][1])
        out = np.zeros(a.shape + (4,), np.uint8)
        out[a] = hexc(c["main"]) + (255,)
        pa = np.pad(a, 1)
        edge = np.zeros_like(a)
        if "left" in c["rim_edges"]: edge |= a & ~np.roll(a, 1, axis=1)
        if "top" in c["rim_edges"]: edge |= a & ~pa[:-2, 1:-1]
        out[edge] = hexc(c["rim"]) + (255,)
        return out
    lum = src[..., :3].astype(float) @ W601
    q = np.unique(lum[a])
    cut = np.sort(q)[2] if len(q) > 3 else q.max()                      # the drawing's 3 darkest colours: the nearer parts
    out = np.zeros_like(src)
    out[a & (lum > cut)] = hexc(c["main"]) + (255,)
    out[a & (lum <= cut)] = hexc(c["near"]) + (255,)
    pa = np.pad(a, 1)
    edge = np.zeros_like(a)
    if "left" in c["rim_edges"]: edge |= a & ~np.roll(a, 1, axis=1)      # the strip repeats: column 0 joins column 319
    if "top" in c["rim_edges"]: edge |= a & ~pa[:-2, 1:-1]
    out[edge] = hexc(c["rim"]) + (255,)
    return out


def write_png(path, arr, mode):
    Image.fromarray(arr, mode).save(path, optimize=True)


def checks(name, rgb, img, nsky, stats, city):
    """the rules; returns a list of failures"""
    bad = []
    c = LEVELS[name]
    if not 4 <= nsky <= 6: bad.append(f"{name}: {nsky} sky tones (4 to 6)")
    for k, h in c["cloud"].items():
        if luma(hexc(h)) < 185: bad.append(f"{name}: cloud {k} {h} luma {luma(hexc(h)):.0f} < 185 (clouds row)")
    # no straight full-width join: every row that starts a tone somewhere must not start it everywhere
    for row in range(1, H):
        ch = img[row] != img[row - 1]
        if ch.all(): bad.append(f"{name}: row {row + TOP} is a straight full-width join"); break
    # (round 2) no cloud cut by the top of the world: no cloud pixel within 4 rows of the screen's top row at the top
    # of a tall level (or at y 0 of a flat one)
    edge = 120 - int(round(c.get("camymax", 0) * 0.3))
    band = img[max(0, edge - 4):edge + 5] >= nsky
    if band.any(): bad.append(f"{name}: {int(band.sum())} cloud pixels within 4 rows of row {edge} (the top of the world)")
    stats["top_row"] = edge
    # (round 2) no cloud stroke narrower than 2 px, no cloud piece under 6 px
    thin, small = cloud_faults(img, nsky)
    if thin.any(): bad.append(f"{name}: {int(thin.sum())} cloud pixels in strokes narrower than 2 px, e.g. x {int(np.nonzero(thin)[1][0])} row {int(np.nonzero(thin)[0][0])}")
    if small.any(): bad.append(f"{name}: {int(small.sum())} cloud pixels in pieces under 6 px")
    # no dither: 2x2 checkers of two colours
    k00, k01, k10, k11 = img[:-1, :-1], img[:-1, 1:], img[1:, :-1], img[1:, 1:]
    chk = ((k00 == k11) & (k01 == k10) & (k00 != k01)).sum()
    if chk > 0: bad.append(f"{name}: {chk} 2x2 dither checkers")
    # seamless: column W-1 next to column 0 behaves like any other neighbour pair
    diff = lambda a_, b_: int((a_ != b_).sum())
    seam = diff(img[:, -1], img[:, 0])
    typ = max(diff(img[:, x], img[:, x + 1]) for x in range(W - 1))
    if seam > max(4, typ): bad.append(f"{name}: the wrap seam differs in {seam} rows (the most for any column pair: {typ})")
    # lone pixels
    pad = np.pad(img, 1, mode="edge"); same = np.zeros(img.shape, bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy: same |= pad[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] == img
    lone = (~same).mean() * 100
    if lone > 0.5: bad.append(f"{name}: {lone:.2f} % lone pixels")
    stats["lone"] = round(float(lone), 3)
    # the far city: 3 colours, darkest on screen >= 145, contrast within the city row
    a = city[..., 3] > 0
    cl = city[..., :3][a].astype(float) @ W601
    p10, p90 = np.percentile(cl, 10), np.percentile(cl, 90)
    if p10 < 145: bad.append(f"{name}: skyline darkest {p10:.0f} < 145")
    if p90 - p10 > 35 + 3: bad.append(f"{name}: skyline contrast {p90 - p10:.0f} > 35")
    stats["city"] = dict(p10=round(float(p10)), median=round(float(np.median(cl))), p90=round(float(p90)),
                         colours=int(len(np.unique(city[..., :3][a], axis=0))))
    # the horizon behind the far layers (rows from screen y 76 down to 150) stays lighter than the far city
    hz = rgb[76 - TOP:150 - TOP].reshape(-1, 3).astype(float) @ W601
    stats["horizon"] = dict(p10=round(float(np.percentile(hz, 10))), median=round(float(np.median(hz))))
    if np.median(hz) <= np.median(cl): bad.append(f"{name}: horizon median {np.median(hz):.0f} not lighter than the city {np.median(cl):.0f}")
    return bad


def sheet(name, rgb, outdir):
    """previews: the whole strip at 1x, and its first screen at 3x, each with its greyscale under it"""
    os.makedirs(outdir, exist_ok=True)
    im = Image.fromarray(rgb, "RGB")
    g = im.convert("L").convert("RGB")
    s = Image.new("RGB", (W, H * 2 + 4), (20, 20, 20)); s.paste(im, (0, 0)); s.paste(g, (0, H + 4))
    s.save(os.path.join(outdir, f"sky_{name}_strip.png"))
    crop = im.crop((0, 0, 320, H)).resize((960, H * 3), Image.NEAREST)
    crop.save(os.path.join(outdir, f"sky_{name}_3x.png"))


def main():
    check = "--check" in sys.argv
    out = sys.argv[sys.argv.index("--sheet") + 1] if "--sheet" in sys.argv else None
    fails = []
    for name in LEVELS:
        rgb, img, nsky, stats = build_sky(name)
        city = build_skyline(name)
        fails += checks(name, rgb, img, nsky, stats, city)
        p_sky, p_city = os.path.join(SCENE, f"sky_{name}.png"), os.path.join(SCENE, f"skyline_{name}.png")
        p_js = os.path.join(SRC, f"{name}.json")
        if check:
            for p, arr in ((p_sky, rgb), (p_city, city)):
                if not os.path.exists(p): fails.append(f"missing {os.path.relpath(p, ROOT)}"); continue
                disk = np.array(Image.open(p).convert("RGBA" if arr.shape[-1] == 4 else "RGB"))
                if disk.shape != arr.shape or (disk != arr).any():
                    fails.append(f"{os.path.relpath(p, ROOT)} is not what build_sky.py builds")
        else:
            os.makedirs(SRC, exist_ok=True)
            write_png(p_sky, rgb, "RGB"); write_png(p_city, city, "RGBA")
            json.dump(stats, open(p_js, "w"), indent=1)
        print(f"{name:10} tones {nsky} + 4 cloud, clouds {stats['cloud_share']} %, lone {stats['lone']} %, "
              f"horizon {stats['horizon']['median']}/{stats['horizon']['p10']}, city {stats['city']}")
        if out: sheet(name, rgb, out)
    for f in fails: print("FAIL", f)
    print("build_sky: " + ("OK" if not fails else f"{len(fails)} problems"))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
