#!/usr/bin/env python3
"""tools/build_dt_props.py: the tall Downtown's street props (art/dt-props-06nov), BUILT from parts drawn once and
stamped on integer grids, in the sample screen's colours (tools/build_dt_street.py: the bread crates' pine, the ink).
46 px a metre, binary alpha, no resampling, 0 credits. Obstacles (Pepper stands on them): one unbroken 1 px ink
outline. Decoration: no outline, edges a darker shade of its own colour.

The boxes in riverwalk/level/tiled/downtown_tall.lua are not moved. Where a true size and a box disagree, the box wins
for what Pepper stands on and the numbers are in docs/review/06nov/dt_props/README.md.

  town_parasol<W>.png  play, one-way top (W = 40, 48, 64, 96; town_parasol.png = 64): a cafe parasol's canopy, the
                       box's width exactly (+2 for the ink), red and cream panels of 8 px, a scalloped valance, rounded
                       shoulders; at x0 - 1, y0 - 1. The pole is drawn in code (scene.lua PARASOL).
  town_kiosk.png       play, solid 40 x 36: the kiosk's ice cream freezer (0.87 x 0.78 m): a white lid with a handle,
                       a blue enamel body with a picture panel of three ice creams (no text), a rubber bumper, a kick
                       plate on two castors; at x0 - 1, y0 - 1. (A newspaper kiosk is 2.6 m, 120 px: no box fits.)
  town_pedestal.png    play, solid 48 x 40: the statue's red granite plinth (1.04 x 0.87 m): a moulded cap, the die
                       with a bronze plaque (a dog's paw in relief, no text), a base course; at x0 - 1, y0 - 1.
  town_stall.png       play, solid 64 x 28: the market stall's counter (a pine top board, a green planked front) with
                       three crates of produce on it behind her (apples, carrots, lettuces); at x0 - 1, y0 - 15.
  town_crate_front<W>.png  play, solid (W = 28, 32, 36): one apple crate in the bread crates' build (15 rows on the
                       16 px pitch, the ink shared with the crate above), apples heaped 3 px over the rim; scene.lua
                       CRATES stacks one per 16 px at x0 - 1. town_crate_front.png = 32.
  town_sign.png        back, decoration (faded by the game): the RIVER sign, a pedestrian sign post 2.3 m (106 px)
                       with a blue plate 0.6 m (28 px) carrying a white wave and an arrow (no text); centred on the box,
                       bottom on the back line.

  python3 -I tools/build_dt_props.py             write them all (riverwalk/art/scene/)
  python3 -I tools/build_dt_props.py --check     fail if a file on disk differs from the build
  python3 -I tools/build_dt_props.py --sheet P   all pieces at 5x beside the approved bench, bin and lamp
"""
import os, sys, argparse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_dt_street import Cv, C, OUT  # noqa: E402  (the sample screen's canvas and colours)

C.update(
    # parasol canvas (the awnings' red and cream)
    rl=(214, 82, 68), rm=(184, 56, 56), rd=(138, 40, 48),
    kl=(244, 234, 210), km=(228, 214, 188), kd=(182, 164, 144),
    # the freezer: white enamel lid, blue enamel body, rubber, steel
    el=(244, 242, 232), em=(214, 210, 198), es=(160, 156, 150),
    bl1=(112, 168, 214), bm1=(76, 132, 186), bs1=(54, 98, 148), bd1=(38, 70, 110),
    ru=(56, 60, 70), rk=(84, 90, 100), kc=(172, 208, 232),            # the picture card: a pale blue, not white
    # ice creams: waffle cone, strawberry, mint, chocolate, a lolly, its stick
    cn=(214, 160, 90), cnd=(160, 104, 52), pi=(242, 150, 178), pid=(200, 100, 136),
    mi=(156, 216, 172), mid=(92, 166, 118), ch=(128, 78, 48), lo=(240, 112, 64), lol=(252, 180, 84), st=(226, 200, 150),
    # red granite (Stockholm's statues stand on it), bronze
    gl=(178, 118, 104), gm=(150, 94, 84), gs=(118, 72, 66), gd=(86, 52, 50),
    zl=(204, 166, 88), zm=(160, 124, 60), zd=(104, 78, 40),
    # produce: apples, carrots, lettuces (the lettuce greens also make the carrot tops); the stall's green paint
    al=(232, 98, 76), am=(192, 46, 46), ad=(130, 30, 36),
    # (final review: the apple crates repeat) pears, bread, a checked cloth
    q1=(214, 214, 104), q2=(168, 176, 64), q3=(112, 122, 44),
    c1=(196, 140, 72), c2=(160, 104, 48), c3=(110, 66, 32),
    ol=(246, 150, 60), om=(218, 108, 34),
    ll=(156, 208, 96), lm=(108, 168, 72), ld=(70, 122, 56),
    pl=(108, 146, 98), pm=(84, 120, 78), ps=(62, 94, 62), pd=(44, 68, 48),
    # the sign: blue plate, white symbol, grey steel post
    sbl=(84, 132, 192), sbm=(56, 100, 164), sbd=(38, 70, 120), swh=(236, 240, 244),
    pol=(150, 160, 170), pom=(112, 122, 134), pos=(80, 88, 100),
)


def pmap(cv, rows, key, x, y):
    """stamp a little picture given as strings; '.' is left as it is"""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch != ".": cv.put(x + dx, y + dy, key[ch])


def ink_ring(cv):
    """the outline: a 1 px ink ring round the shape, including its bottom row (it stands on the ground)"""
    cv.outline("ink")


# ---- the parasol -----------------------------------------------------------------------------------------------
PANEL = 8


def parasol(w):
    """a cafe parasol's canopy for a one-way box w wide: art w + 2 wide, at x0 - 1, y0 - 1. Rows: ink, the lit top
    (shoulders rounded), the canopy, its shade, a scalloped valance (one tongue per 8 px panel)"""
    assert w % PANEL == 0, "the panels are 8 px: the box width must be a multiple of 8"
    W, H = w + 2, 14
    cv = Cv(W, H)
    n = w // PANEL
    for i in range(n):
        x0 = 1 + i * PANEL; x1 = x0 + PANEL - 1
        red = i % 2 == 0
        L, M, D = ("rl", "rm", "rd") if red else ("kl", "km", "kd")
        cv.rect(x0, 1, x1, 1, L)                                       # the lit top
        cv.rect(x0, 2, x1, 7, M)                                       # the canopy
        cv.rect(x0, 2, x0, 7, L) if i == 0 else None                   # the sun side's edge
        cv.rect(x0, 8, x1, 8, D)                                       # the canopy's lower edge in shade
        cv.rect(x0, 9, x1, 10, M); cv.rect(x0 + 1, 11, x1 - 1, 11, M)  # the tongue
        cv.rect(x0 + 2, 12, x1 - 2, 12, D)                             # its rounded end, in shade
        cv.put(x1, 9, D); cv.put(x1, 10, D); cv.put(x1 - 1, 11, D)     # the tongue's shaded right side
    # rounded shoulders: the top row's ends and the first canopy row's end pixels go
    for x in (1, 2, W - 3, W - 2): cv.put(x, 1, "")
    for x in (1, W - 2): cv.put(x, 2, "")
    ink_ring(cv)
    return cv


# ---- the kiosk's ice cream freezer -----------------------------------------------------------------------------
CONE = ["..pp..",
        ".pppP.",
        ".pppP.",
        "mmmmMm",
        "mmmmmM",
        "cccccC",
        ".cccC.",
        ".cccC.",
        "..cC..",
        "..cC..",
        "..C..."]
CONE_K = {"p": "pi", "P": "pid", "m": "mi", "M": "mid", "c": "cn", "C": "cnd"}
LOLLY = [".oo.",
         "oOoo",
         "oOoo",
         "oOoo",
         "oooo",
         "oooo",
         "lllo",
         "llll",
         ".ss.",
         ".ss.",
         ".ss."]
LOLLY_K = {"o": "lo", "O": "lol", "l": "lol", "s": "cn"}
CHOC = [".hh.",
        "hHhh",
        "hHhh",
        "hhhh",
        "hhhh",
        "hhhh",
        "pppp",
        "pppp",
        ".ss.",
        ".ss.",
        ".ss."]
CHOC_K = {"h": "ch", "H": "cn", "p": "pi", "s": "cn"}


def kiosk():
    """the kiosk's ice cream freezer for the KIOSK box (40 x 36): 42 x 37 at x0 - 1, y0 - 1"""
    W, H = 42, 37
    cv = Cv(W, H)
    # the lid (rows 1-4): white enamel, a chrome handle
    cv.rect(2, 1, 39, 1, "el"); cv.rect(1, 2, 40, 3, "em"); cv.rect(1, 2, 1, 3, "el"); cv.rect(40, 2, 40, 3, "es")
    cv.rect(1, 4, 40, 4, "es")
    cv.rect(16, 2, 25, 2, "el"); cv.rect(16, 3, 25, 3, "ru")                  # the handle: lit rail, its shadow
    # the body (rows 5-30): blue enamel, lit on the left, shaded on the right, shade under the lid
    cv.rect(1, 5, 40, 30, "bm1"); cv.rect(1, 6, 1, 30, "bl1"); cv.rect(39, 6, 40, 30, "bs1")
    cv.rect(1, 5, 40, 5, "bd1")
    # the picture panel (rows 9-26, x 6-35): a pale blue card in a dark frame, three ice creams on it
    cv.rect(6, 9, 35, 26, "bd1"); cv.rect(7, 10, 34, 25, "kc"); cv.rect(7, 25, 34, 25, "bl1"); cv.rect(34, 10, 34, 25, "bl1")
    pmap(cv, CONE, CONE_K, 9, 12)
    pmap(cv, LOLLY, LOLLY_K, 19, 12)
    pmap(cv, CHOC, CHOC_K, 27, 12)
    # the bumper (rows 28-29) and the kick plate on two castors (rows 31-35)
    cv.rect(1, 28, 40, 28, "rk"); cv.rect(1, 29, 40, 29, "ru")
    cv.rect(2, 31, 39, 32, "ru"); cv.rect(2, 31, 39, 31, "rk")
    for cx in (4, 33):
        cv.rect(cx, 33, cx + 4, 34, "ru"); cv.rect(cx + 1, 35, cx + 3, 35, "ru"); cv.put(cx + 1, 33, "rk")
    cv.rect(1, 30, 40, 30, "bs1")                                           # the body's foot in shade
    ink_ring(cv)
    return cv


# ---- the statue's pedestal --------------------------------------------------------------------------------------
PAW = ["..zd.zd..",
       "..dd.dd..",
       "zd.....zd",
       "dd.zzd.dd",
       "..zzzzd..",
       ".zzzzzzd.",
       ".zzzzzzd.",
       "..dd.dd.."]
PAW_K = {"z": "zl", "d": "zd"}


def pedestal():
    """the PEDESTAL box (48 x 40): 50 x 41 at x0 - 1, y0 - 1. Polished red granite in three courses"""
    W, H = 50, 41
    cv = Cv(W, H)
    # the cap (rows 1-5): a slab, a cyma under it, the shadow line
    cv.rect(1, 1, 48, 1, "gl"); cv.rect(1, 2, 48, 3, "gm"); cv.rect(1, 2, 1, 3, "gl"); cv.rect(48, 2, 48, 3, "gs")
    cv.rect(2, 4, 47, 4, "gs"); cv.rect(3, 5, 46, 5, "gd")
    # the die (rows 6-31, x 5-44)
    cv.rect(5, 6, 44, 31, "gm"); cv.rect(5, 6, 5, 31, "gl"); cv.rect(43, 6, 44, 31, "gs"); cv.rect(5, 6, 44, 6, "gd")
    # a sunk panel round the plaque (rows 9-28, x 10-39): its top and left edges in shade, bottom and right lit
    cv.rect(10, 9, 39, 9, "gs"); cv.rect(10, 9, 10, 28, "gs"); cv.rect(11, 28, 39, 28, "gl"); cv.rect(39, 10, 39, 28, "gl")
    # the bronze plaque (rows 12-25, x 15-34): a bevelled frame, a paw in relief
    cv.rect(15, 12, 34, 25, "zm"); cv.rect(15, 12, 34, 12, "zl"); cv.rect(15, 12, 15, 25, "zl")
    cv.rect(16, 25, 34, 25, "zd"); cv.rect(34, 13, 34, 25, "zd")
    cv.rect(17, 14, 32, 23, "zd"); cv.rect(18, 15, 32, 23, "zm")             # the sunk field
    pmap(cv, PAW, PAW_K, 21, 15)                                               # a dog's paw in relief
    # the base (rows 32-39): a moulding, then the full-width course
    cv.rect(3, 32, 46, 32, "gl"); cv.rect(3, 33, 46, 33, "gs")
    cv.rect(1, 34, 48, 34, "gl"); cv.rect(1, 35, 48, 39, "gm"); cv.rect(1, 34, 1, 39, "gl"); cv.rect(47, 35, 48, 39, "gs")
    cv.rect(1, 39, 48, 39, "gs")
    ink_ring(cv)
    return cv


# ---- produce and crates -----------------------------------------------------------------------------------------
APPLE = [".aAa.",
         "aAaaa",
         "aaamm",
         ".mmm."]
APPLE_K = {"a": "am", "A": "al", "m": "ad"}


def heap(cv, x0, x1, ytop, motif, key, step=4, rows=2):
    """a heap of round fruit over [x0, x1]: a full row, a shorter staggered row above it"""
    for r in range(rows):
        y = ytop + (rows - 1 - r) * 3
        off = 0 if r % 2 == 0 else step // 2
        xs = list(range(x0 + off + r * 2, x1 - 3 - r * 2 + 1, step))
        for x in xs: pmap(cv, motif, key, x, y)


PEAR = ["..q..",
        ".qQq.",
        "qQqqm",
        ".qmm."]
PEAR_K = {"q": "q2", "Q": "q1", "m": "q3"}
LOAF = [".cCc.",
        "cCccm",
        "cccmm",
        ".mmm."]
LOAF_K = {"c": "c2", "C": "c1", "m": "c3"}
FILLS = {"apples": (APPLE, APPLE_K), "pears": (PEAR, PEAR_K), "bread": (LOAF, LOAF_K)}

def apple_crate(w, fill="apples"):
    """one apple crate for a CRATES box w wide: w + 2 x 21 (rows 0-3 the apples over the rim, row 4 the ink, 15 rows
    of crate, row 20 the ink it shares with the crate under it). The bread crates' build: lit top rail, hand slot,
    an opening of apples, the middle slat, a low opening, the bottom rail, posts lit left and shaded right"""
    W, H = w + 2, 21
    cv = Cv(W, H)
    T = 4                                                                    # the crate's top ink row
    iw = W - 6; n = (iw + 1) // 6; x0 = 3 + (iw - (n * 6 - 1)) // 2
    mot, key = FILLS.get(fill, FILLS["apples"])
    if fill != "cloth":
        for i in range(n): pmap(cv, mot[:3], key, x0 + i * 6, 1)              # the fruit's tops over the rim
    cv.rect(1, T + 1, W - 2, T + 15, "wm")
    cv.rect(1, T + 1, W - 2, T + 1, "wl")                                    # top rail
    cv.rect(W // 2 - 4, T + 2, W // 2 + 3, T + 2, "wd")                      # the hand slot
    o1, o2, mid = (T + 4, T + 7), (T + 10, T + 12), T + 8
    for a, b in (o1, o2): cv.rect(3, a, W - 4, b, "wi")
    # apples in the openings (the same apple, on a 4 px pitch)
    if fill == "cloth":                                                      # empty, a checked cloth over its
        for y in range(1, T + 8):                                            # rim and down the front opening
            for x in range(3, W - 3):
                if y <= 3 and (x < 4 or x > W - 5): continue
                if y >= T and y < o1[0]: continue
                cv.put(x, y, "rm" if ((x // 3) + (y // 3)) % 2 else "kl")
        cv.rect(3, o2[0], W - 4, o2[1], "wi")
    else:
        for i in range(n): pmap(cv, mot, key, x0 + i * 6, o1[0])
        for i in range(n): pmap(cv, mot[:3], key, x0 + i * 6, o2[0])
    cv.rect(1, mid, W - 2, mid, "wl"); cv.rect(1, mid + 1, W - 2, mid + 1, "ws")   # the middle slat
    cv.rect(1, T + 13, W - 2, T + 13, "wl"); cv.rect(1, T + 15, W - 2, T + 15, "ws")   # bottom rail
    cv.rect(1, T + 1, 1, T + 15, "wl"); cv.rect(2, T + 2, 2, T + 15, "wm")          # posts
    cv.rect(W - 3, T + 2, W - 3, T + 15, "wm"); cv.rect(W - 2, T + 1, W - 2, T + 15, "ws")
    cv.rect(2, o1[0], 2, o1[1], "ws"); cv.rect(2, o2[0], 2, o2[1], "ws")
    ink_ring(cv)
    cv.rect(0, H - 1, W - 1, H - 1, "ink")                                   # the bottom ink (shared on a stack)
    return cv


CARROT = ["l.L.",
          ".lL.",
          "oooO",
          ".oO.",
          ".oO.",
          "..O."]
CARROT_K = {"l": "lm", "L": "ld", "o": "ol", "O": "om"}
LETTUCE = [".lLl..",
           "lLlll.",
           "llLlmd",
           "mlllmd",
           ".mmdd."]
LETTUCE_K = {"l": "ll", "L": "lm", "m": "lm", "d": "ld"}


def produce_crate(cv, x0, w, y_top, kind):
    """a low produce crate w wide on the counter: its body rows y_top+5 .. y_top+10 (the ink round it is the
    canvas outline), the produce heaped over its rim in rows y_top .. y_top+4"""
    by = y_top + 6
    cv.rect(x0, by, x0 + w - 1, by + 5, "wm"); cv.rect(x0, by, x0 + w - 1, by, "wl")
    cv.rect(x0 + 1, by + 3, x0 + w - 2, by + 3, "wd")                              # the slat gap
    cv.rect(x0, by + 1, x0, by + 5, "wl"); cv.rect(x0 + w - 1, by + 1, x0 + w - 1, by + 5, "ws")
    if kind == "apples":
        for x in range(x0 + 1, x0 + w - 4, 6): pmap(cv, APPLE, APPLE_K, x, y_top + 2)
        for x in range(x0 + 4, x0 + w - 7, 6): pmap(cv, APPLE[:3], APPLE_K, x, y_top)
    elif kind == "carrots":
        for i, x in enumerate(range(x0 + 1, x0 + w - 4, 4)): pmap(cv, CARROT, CARROT_K, x, y_top + (1 if i % 2 else 0))
    else:
        for x in range(x0 + 1, x0 + w - 6, 6): pmap(cv, LETTUCE, LETTUCE_K, x, y_top + 1)


def stall():
    """the STALL box (64 x 28): 66 x 43 at x0 - 1, y0 - 15. Rows 1-14 the produce crates behind her, row 15 = y0 the
    counter's top (where she stands), the planked front down to the ground"""
    W, H = 66, 43
    cv = Cv(W, H)
    # three produce crates on the counter's back (x 2-21, 23-42, 44-63), bodies down to row 13
    for x0, kind in ((2, "apples"), (23, "carrots"), (44, "lettuces")):
        produce_crate(cv, x0, 20, 2, kind)
    # the counter top: a pine board (rows 15-18), 1 px over the front at each end
    cv.rect(1, 15, 64, 15, "wl"); cv.rect(1, 16, 64, 17, "wm"); cv.rect(1, 18, 64, 18, "ws")
    # the front (rows 19-41, x 2-63): green planks of 6 px, lit left, a dark seam right
    cv.rect(2, 19, 63, 41, "pm")
    for x in range(2, 64, 6):
        cv.rect(x, 19, x, 41, "pl"); cv.rect(min(x + 5, 63), 19, min(x + 5, 63), 41, "ps")
    cv.rect(2, 19, 63, 19, "pd")                                                  # shade under the board
    cv.rect(2, 37, 63, 37, "pl"); cv.rect(2, 38, 63, 41, "ps")                     # the kick rail
    cv.rect(2, 41, 63, 41, "pd")
    ink_ring(cv)
    cv.rect(0, H - 1, W - 1, H - 1, "ink")
    return cv


# ---- the RIVER sign (back decoration) ---------------------------------------------------------------------------
WAVE = ["..ww....ww..",
        ".w..w..w..w.",
        "w....ww....w"]
ARROW = ["....w...",
         "....ww..",
         "wwwwwww.",
         "wwwwwwww",
         "wwwwwww.",
         "....ww..",
         "....w..."]


def river_sign():
    """a pedestrian sign post, 2.3 m (106 px), a blue plate 0.6 x 0.28 m (28 x 13) at the top: decoration, no ink"""
    W, H = 28, 106
    cv = Cv(W, H)
    cv.rect(0, 0, 27, 12, "sbm"); cv.rect(0, 0, 27, 0, "sbl"); cv.rect(0, 0, 0, 12, "sbl")
    cv.rect(27, 1, 27, 12, "sbd"); cv.rect(1, 12, 27, 12, "sbd")
    cv.rect(2, 2, 25, 2, "swh"); cv.rect(2, 10, 25, 10, "swh"); cv.rect(2, 2, 2, 10, "swh"); cv.rect(25, 2, 25, 10, "swh")
    pmap(cv, [r[:9] for r in WAVE], {"w": "swh"}, 4, 4)
    pmap(cv, ARROW, {"w": "swh"}, 15, 3)
    # the post (x 12-14) from under the plate to the ground; a clamp at the plate, a foot
    cv.rect(12, 13, 14, 103, "pom"); cv.rect(12, 13, 12, 103, "pol"); cv.rect(14, 13, 14, 103, "pos")
    cv.rect(11, 13, 15, 13, "pos")
    cv.rect(11, 103, 15, 105, "pom"); cv.rect(11, 103, 11, 105, "pol"); cv.rect(15, 103, 15, 105, "pos")
    cv.rect(10, 105, 16, 105, "pos")
    return cv


def build():
    out = {f"town_parasol{w}": parasol(w) for w in (40, 48, 64, 96)}
    out["town_parasol"] = parasol(64)
    out["town_kiosk"] = kiosk()
    out["town_pedestal"] = pedestal()
    out["town_stall"] = stall()
    for w in (28, 32, 36):
        out[f"town_crate_front{w}"] = apple_crate(w)
        for f in ("pears", "bread", "cloth"): out[f"town_crate_front{w}_{f}"] = apple_crate(w, f)
    out["town_crate_front"] = apple_crate(32)
    out["town_sign"] = river_sign()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--sheet")
    ap.add_argument("--only", nargs="*")
    o = ap.parse_args()
    bad = 0; ims = {}
    for n, cv in build().items():
        if o.only and n not in o.only: continue
        im = cv.png(); ims[n] = im; p = os.path.join(OUT, n + ".png")
        ncol = len({tuple(c) for c in im[im[..., 3] > 0][:, :3].tolist()})
        if o.check:
            ok = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert("RGBA")), im)
            print(p, "matches the build" if ok else "DIFFERS from the build"); bad += not ok
        else:
            Image.fromarray(im).save(p); print(f"{p} {im.shape[1]} x {im.shape[0]}, {ncol} colours")
    if o.sheet:
        z = 5; ref = ["bench", "bin", "lamp_post"]
        allims = [np.array(Image.open(os.path.join(OUT, r + ".png")).convert("RGBA")) for r in ref] + \
                 [im for n, im in ims.items() if n not in ("town_parasol", "town_crate_front")]
        W = sum(i.shape[1] * z + 20 for i in allims) + 20; H = max(i.shape[0] for i in allims) * z + 40
        sh = Image.new("RGBA", (W, H), (96, 104, 118, 255)); x = 20
        for im in allims:
            sh.alpha_composite(Image.fromarray(im).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST), (x, H - 20 - im.shape[0] * z)); x += im.shape[1] * z + 20
        sh.save(o.sheet)
    sys.exit(1 if bad else 0)
