"""tools/build_oldtown.py: Downtown's Old Town row (riverwalk/art/scene/town_facades.png), every house BUILT from
stamped parts (art/pilot-oldtown, 23 Oct 2026; docs/BIBLE.md section 3, the crispness bar).

  python3 -I tools/build_oldtown.py                    write town_facades.png
  python3 -I tools/build_oldtown.py --check            fail if the file on disk is not what this script builds
  python3 -I tools/build_oldtown.py --houses DIR       also write each house alone (DIR/<name>.png) for asset_qa
  python3 -I tools/build_oldtown.py --parts out.png    a sheet of the parts at 8x

Each repeated part (window, narrow window, attic window, dormer, door, shop window, balcony, gable step, bell
shoulder, cornice, string course, plinth, chimney, downpipe) is drawn ONCE below as a small grid of colour roles and
stamped on an integer grid. Every window of a storey is the same part at the same height, evenly spaced; the
storeys of a house are equal; walls are one flat fill with one shade band (the right edge, light from the upper
left); every step of a gable is the same part. No resampling of any kind.

Seven houses, as on Stockholm's Vasterlanggatan: each its own colour, height, top (stepped gable, bell gable,
pediment, mansard roof with dormers) and door, all from the same parts. Windows of houses with the same wall colour
sit on the same rows or at least 5 px apart (asset_qa groups a storey by wall colour and height).

The colours are the strip's own 12 (no new colour); each house maps the roles to them. Only the pavement rows (111
on) come from source_scenery/town_facades_v06.png (the strip as it was on main v0.6), so the script regenerates the
output exactly. The strip is decoration on the mid layer (scrolls 0.5, faded by the game): no outline, edges by a
darker shade.
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "source_scenery", "town_facades_v06.png")
OUT = os.path.join(ROOT, "riverwalk", "art", "scene", "town_facades.png")
GROUND = 111                                         # rows 111-113: the pavement line, kept from the base

# the strip's 12 colours (luma in brackets)
C = dict(
    yellow=(225, 184, 127),     # (190) plaster
    red=(180, 99, 76),          # (121) plaster, roof tiles
    stone=(166, 148, 132),      # (152) plaster, cornices, plinths, door frames
    glass=(85, 94, 106),        # (93)
    ochre=(184, 143, 107),      # (151) plaster / yellow's shade
    umber=(127, 111, 102),      # (115) joints, roof ridges, door split, dormer caps
    frame=(174, 171, 168),      # (172) window frames and glazing bars
    cream=(231, 209, 166),      # (211) plaster
    door=(84, 70, 66),          # (74) door leaves, balcony iron
    slate=(123, 129, 136),      # (128) downpipe
    brick=(128, 79, 67),        # (92) red's shade
    light=(221, 213, 200),      # (214) lit stone: lintels, sills, cornice tops, gable coping
)

# ---- the parts, drawn once. Roles: W wall, S wall shade, L lit stone, T stone, F frame, G glass, K door leaf / iron,
# ---- D umber (joint, door split, ridge, dormer cap), R roof, Q roof shade; M / N plinth and f dormer frame, the
# ---- same on every house; '.' leaves what is under it.
# ---- Each part is stamped by the top-left of its frame (or body); "at" is that point inside the part.
P = {}
def part(name, rows, at=(0, 0)):
    assert len({len(r) for r in rows}) == 1, name
    P[name] = dict(rows=rows, at=at)

part("window", [    # 7 x 11 (2 x 2 panes of 2 x 4) with lintel, sill and the sill's shadow
    "LLLLLLLLL",
    ".FFFFFFF.",
    ".FGGFGGF.", ".FGGFGGF.", ".FGGFGGF.", ".FGGFGGF.",
    ".FFFFFFF.",
    ".FGGFGGF.", ".FGGFGGF.", ".FGGFGGF.", ".FGGFGGF.",
    ".FFFFFFF.",
    "LLLLLLLLL",
    "SSSSSSSSS"], (1, 1))
part("narrow", [    # 4 x 11 (1 x 2 panes of 2 x 4)
    "LLLLLL",
    ".FFFF.",
    ".FGGF.", ".FGGF.", ".FGGF.", ".FGGF.",
    ".FFFF.",
    ".FGGF.", ".FGGF.", ".FGGF.", ".FGGF.",
    ".FFFF.",
    "LLLLLL",
    "SSSSSS"], (1, 1))
part("attic", [     # 7 x 9 attic window (2 x 2 panes of 2 x 3)
    "LLLLLLLLL",
    ".FFFFFFF.",
    ".FGGFGGF.", ".FGGFGGF.", ".FGGFGGF.",
    ".FFFFFFF.",
    ".FGGFGGF.", ".FGGFGGF.", ".FGGFGGF.",
    ".FFFFFFF.",
    "LLLLLLLLL",
    "SSSSSSSSS"], (1, 1))
part("attic_on_cornice", P["attic"]["rows"][:10], (1, 1))          # the cornice below is its sill
part("dormer", [    # the attic window in a dormer: umber cap, wall cheeks; it sits on the roof (no shadow)
    "....D....",
    "...DDD...",
    "..DDDDD..",
    ".DDDDDDD.",
    "LLLLLLLLL",
    "WfffffffW",
    "WfGGfGGfW", "WfGGfGGfW", "WfGGfGGfW",
    "WfffffffW",
    "WfGGfGGfW", "WfGGfGGfW", "WfGGfGGfW",
    "WfffffffW",
    "LLLLLLLLL"], (1, 5))
part("door", ["LLLLLLLLL"] + ["TKKKDKKKT"] * 17, (1, 1))           # 7 x 17 double door in a stone frame
part("door1", ["LLLLLL"] + ["TKKKKT"] * 17, (1, 1))                 # 4 x 17 single door
part("shop", [      # 13 x 11 shop window (3 x 2 panes of 3 x 4) with a lintel and a stone stall riser
    "LLLLLLLLLLLLLLL",
    ".FFFFFFFFFFFFF.",
    ".FGGGFGGGFGGGF.", ".FGGGFGGGFGGGF.", ".FGGGFGGGFGGGF.", ".FGGGFGGGFGGGF.",
    ".FFFFFFFFFFFFF.",
    ".FGGGFGGGFGGGF.", ".FGGGFGGGFGGGF.", ".FGGGFGGGFGGGF.", ".FGGGFGGGFGGGF.",
    ".FFFFFFFFFFFFF.",
    "LLLLLLLLLLLLLLL",
    ".TTTTTTTTTTTTT."], (1, 1))
part("balcony", [   # wrought iron balcony under a window's sill (in place of its shadow): rail, balusters, slab
    "KKKKKKKKKKK",
    "K.K.K.K.K.K",
    "K.K.K.K.K.K",
    "TTTTTTTTTTT"], (2, 0))
part("step_l", ["LL", "L.", "L.", "L.", "L."])                     # a gable step, left: lit tread and riser
part("step_r", ["LL", ".S", ".S", ".S", ".S"])                     # right: lit tread, riser in shade
part("shoulder_l", [                                                # a bell gable's shoulder (8 x 8), left
    ".....LLL",
    "...LLWWW",
    "..LWWWWW",
    ".LWWWWWW",
    ".LWWWWWW",
    "LWWWWWWW",
    "LWWWWWWW",
    "LWWWWWWW"])
part("shoulder_r", [                                                # the same, right (vertical edge in shade)
    "LLL.....",
    "WWWLL...",
    "WWWWWL..",
    "WWWWWWS.",
    "WWWWWWS.",
    "WWWWWWWS",
    "WWWWWWWS",
    "WWWWWWWS"])
part("cap", ["..LLL..", ".LWWWL.", "LWWWWWL"])                      # a bell gable's top (7 x 3)
part("finial", [".D.", ".D.", "DDD"], (1, 3))
part("chimney", ["LLLLL", ".TTS.", ".TTS.", ".TTS.", ".TTS.", ".TTS."], (1, 0))
for n, rows in dict(cornice=["L", "T", "S"], string=["L", "T", "S"], plinth=["M", "N", "N", "N", "N"]).items():
    part(n, rows)

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.role = np.full((h, w), ".", dtype="<U1")
    def put(self, x, y, role):
        if 0 <= x < self.w and 0 <= y < self.h: self.role[y, x] = role
    def rect(self, x0, y0, x1, y1, role):          # inclusive
        if x1 < x0 or y1 < y0: return
        self.role[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = role
    def stamp(self, name, x, y):                   # (x, y): where the part's anchor goes
        p = P[name]; ax, ay = p["at"]
        for dy, row in enumerate(p["rows"]):
            for dx, ch in enumerate(row):
                if ch != ".": self.put(x - ax + dx, y - ay + dy, ch)
    def band(self, name, x0, x1, y):               # a horizontal band: each row of the part across x0..x1
        for dy, row in enumerate(P[name]["rows"]): self.rect(x0, y + dy, x1, y + dy, row[0])

# ---- the tops
def stepped(cv, top, t):
    """a stepped gable: levels of equal height, each narrower by the same step; every step is the same part"""
    lv, sw, n, hw0, cx = t["level_h"], t["step_w"], t["levels"], t["top_hw"], t["cx"]
    y_top = top - lv * n
    for k in range(n):                                # k = 0 is the top block
        hw = hw0 + sw * k; y0 = y_top + lv * k
        cv.rect(cx - hw, y0, cx + hw, y0 + lv - 1, "W")
    for k in range(n):
        hw = hw0 + sw * k; y0 = y_top + lv * k
        if k == 0:
            cv.rect(cx - hw, y0, cx + hw, y0, "L")
            cv.rect(cx - hw, y0, cx - hw, y0 + lv - 1, "L")
            cv.rect(cx + hw, y0 + 1, cx + hw, y0 + lv - 1, "S")
        else:
            cv.stamp("step_l", cx - hw, y0)
            cv.stamp("step_r", cx + hw - 1, y0)
    cv.stamp("finial", cx, y_top)

def bell(cv, top, t):
    """a bell gable: levels of two shoulders (the same part) and a block between, then a cap"""
    l, r, y = t["left"], t["right"], top
    for _ in range(t["levels"]):
        y -= 8
        cv.rect(l + 8, y, r - 8, y + 7, "W")
        cv.stamp("shoulder_l", l, y); cv.stamp("shoulder_r", r - 7, y)
        l, r = l + 8, r - 8
    assert r - l == 6, "the cap is 7 px wide"
    cv.stamp("cap", l, y - 3)
    cv.stamp("finial", l + 3, y - 3)

def pediment(cv, top, t):
    """a 45 degree pediment from x l..r on the cornice: lit coping on both slopes (they face up)"""
    l, r = t["left"], t["right"]
    d = 0
    while l + d <= r - d:
        y = top - 1 - d
        cv.rect(l + d, y, r - d, y, "W")
        cv.put(l + d, y, "L"); cv.put(r - d, y, "L")
        if l + d + 1 >= r - d - 1: cv.rect(l + d, y, r - d, y, "L")
        d += 1
    if t.get("finial"): cv.stamp("finial", (l + r) // 2, top - d)

def mansard(cv, top, t):
    """a mansard roof: steep slopes going in 1 px every `rise` rows, ridge in umber, right slope's edge in shade"""
    l, r, h, rise = t["left"], t["right"], t["height"], t["rise"]
    for d in range(h):
        y = top - 1 - d; i = d // rise
        cv.rect(l + i, y, r - i, y, "R")
        cv.put(r - i, y, "Q")
        if d == h - 1: cv.rect(l + i, y, r - i, y, "D")

TOPS = dict(stepped=stepped, bell=bell, pediment=pediment, mansard=mansard)

def build_house(h):
    """h: a house spec -> (x0, canvas of roles, role -> colour)"""
    W = h["x1"] - h["x0"] + 1
    cv = Canvas(W, GROUND)
    top = h["cornice"]                               # first row of the main cornice
    for (name, x, y) in h.get("behind", []): cv.stamp(name, x, y)      # chimneys
    TOPS[h["top"]["type"]](cv, top, h["top"])
    # the body: joint on the left, flat wall, one shade band on the right (light from the upper left)
    cv.rect(0, top, W - 1, GROUND - 1, "W")
    cv.rect(0, top, 0, GROUND - 1, "D")
    cv.rect(W - 1, top, W - 1, GROUND - 1, "S")
    cv.band("cornice", 0, W - 1, top)
    if h.get("string") is not None: cv.band("string", 0, W - 1, h["string"])
    cv.band("plinth", 0, W - 1, GROUND - 5)
    # the storeys: one window part per storey, stamped on every column of it at the storey's height
    for (name, cols, ys) in h["windows"]:
        for y in ys:
            for x in cols: cv.stamp(name, x, y)
    for (name, x, y) in h.get("parts", []): cv.stamp(name, x, y)
    pal = dict(M="light", N="stone", f="frame", **h["colours"])   # one plinth, one dormer frame for the row
    return h["x0"], cv, {k: C[v] for k, v in pal.items()}

# ---- the houses, left to right (x on the strip; it is 225 px wide and repeats). Window columns and rows are the
# ---- frame's top-left, local to the house. Grid A: cornice 33, storeys at 39 / 55 / 71 (16 px), string 84.
RED = dict(W="red", S="brick", L="light", T="stone", F="frame", G="glass", K="door", D="umber")
HOUSES = {
    # yellow bell-gabled house, 3 windows a storey 4 px apart, door on the left; a downpipe on its right
    "yellow_bell": dict(
        x0=0, x1=40, cornice=33, string=84,
        top=dict(type="bell", left=1, right=39, levels=2),
        windows=[("window", [6, 17, 28], [39, 55, 71]), ("window", [17, 28], [93]), ("attic_on_cornice", [17], [24])],
        parts=[("door", 6, 89)],
        colours=dict(W="yellow", S="ochre", L="light", T="stone", F="frame", G="glass", K="door", D="umber",
                     ),
        pipe=40),
    # the red stepped-gable house (the pilot): 37 px, a gable as wide as the wall of 6 levels of 5 px with treads
    # of 2 px, two attic windows on the cornice and one above
    "red_gable": dict(
        x0=42, x1=78, cornice=33, string=84,
        top=dict(type="stepped", level_h=5, step_w=2, levels=6, top_hw=7, cx=18),
        windows=[("window", [4, 15, 26], [39, 55, 71]), ("window", [4, 26], [93]),
                 ("attic_on_cornice", [9, 21], [24]), ("attic", [15], [11])],
        parts=[("door", 15, 89)],
        colours=dict(RED)),
    # cream house, 3 tall storeys (18 px) under a pediment, 2 windows a storey, balconies on the top floor, door
    # on the left
    "cream_pediment": dict(
        x0=79, x1=113, cornice=29, string=84,
        top=dict(type="pediment", left=5, right=29, finial=True),
        windows=[("window", [7, 21], [35, 53, 71]), ("window", [21], [93])],
        parts=[("balcony", 7, 47), ("balcony", 21, 47), ("door", 7, 89)],
        colours=dict(W="cream", S="yellow", L="stone", T="ochre", F="frame", G="glass", K="door", D="umber")),
    # grey stone house under a red mansard roof with two dormers and a chimney; shop window and door
    "stone_mansard": dict(
        x0=114, x1=152, cornice=33, string=84,
        top=dict(type="mansard", left=1, right=37, height=17, rise=2),
        behind=[("chimney", 25, 10)],
        windows=[("window", [5, 16, 27], [39, 55, 71]), ("dormer", [9, 23], [24])],
        parts=[("shop", 5, 93), ("door", 27, 89)],
        colours=dict(W="stone", S="umber", L="yellow", T="ochre", F="light", G="glass", K="door", D="umber",
                     R="red", Q="brick")),
    # ochre house, storeys at 31 / 47 / 63 (grid C), a mansard roof with one dormer and a chimney, shop and door
    "ochre_mansard": dict(
        x0=153, x1=187, cornice=25, string=76,
        top=dict(type="mansard", left=1, right=33, height=15, rise=3),
        behind=[("chimney", 7, 4)],
        windows=[("window", [3, 14, 25], [31, 47, 63]), ("dormer", [14], [11])],
        parts=[("door", 4, 89), ("shop", 17, 93)],
        colours=dict(W="ochre", S="umber", L="light", T="stone", F="frame", G="glass", K="door", D="umber",
                     R="red", Q="brick")),
    # narrow yellow house, grid C, a one-level bell gable, 2 narrow windows a storey, door in the middle
    "yellow_narrow": dict(
        x0=188, x1=212, cornice=25, string=76,
        top=dict(type="bell", left=1, right=23, levels=1),
        windows=[("narrow", [6, 15], [31, 47, 63])],
        parts=[("door", 9, 89)],
        colours=dict(W="yellow", S="ochre", L="light", T="stone", F="frame", G="glass", K="door", D="umber")),
    # narrow red house, 4 storeys at 17 / 33 / 49 / 65 (6 px off the pilot's rows), a pediment, one narrow window
    # a storey, single door
    "red_narrow": dict(
        x0=213, x1=224, cornice=11, string=78,
        top=dict(type="pediment", left=1, right=10),
        windows=[("narrow", [4], [17, 33, 49, 65])],
        parts=[("door1", 4, 89)],
        colours=dict(RED)),
}

def render_house(name):
    x0, cv, pal = build_house(HOUSES[name])
    im = np.zeros((cv.h, cv.w, 4), np.uint8)
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.role[y, x] != ".": im[y, x] = (*pal[cv.role[y, x]], 255)
    return x0, im

def render():
    base = np.array(Image.open(BASE).convert("RGBA"))
    out = np.zeros_like(base)
    out[GROUND:] = base[GROUND:]
    for name, h in HOUSES.items():
        x0, im = render_house(name)
        m = im[..., 3] > 0
        out[:GROUND, x0:x0 + im.shape[1]][m] = im[m]
        if h.get("pipe") is not None:                 # the downpipe between this house and the next
            x = x0 + h["pipe"] + 1
            out[h["cornice"]:GROUND - 5, x] = (*C["slate"], 255)
            out[GROUND - 5:GROUND, x] = out[GROUND - 5:GROUND, x - 1]
    return base, out

def parts_sheet(path, z=8):
    cols = {"W": (200, 120, 90), "S": C["brick"], "L": C["light"], "T": C["stone"], "F": C["frame"], "G": C["glass"],
            "K": C["door"], "D": C["umber"], "R": C["red"], "Q": C["brick"], "M": C["light"], "N": C["stone"], "f": C["frame"]}
    ims = []
    for n, p in P.items():
        rows = p["rows"]; a = np.zeros((len(rows), len(rows[0]), 4), np.uint8)
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != ".": a[y, x] = (*cols[ch], 255)
        ims.append(Image.fromarray(a).resize((a.shape[1] * z, a.shape[0] * z), Image.NEAREST))
    W = sum(i.width for i in ims) + 10 * (len(ims) + 1); H = max(i.height for i in ims) + 20
    sheet = Image.new("RGBA", (W, H), (60, 60, 66, 255)); x = 10
    for i in ims: sheet.alpha_composite(i, (x, 10)); x += i.width + 10
    sheet.save(path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the file on disk is not what the script builds")
    ap.add_argument("--houses", help="also write each house alone to this folder (<name>.png)")
    ap.add_argument("--parts", help="write a sheet of the parts at 8x to this path")
    o = ap.parse_args()
    base, out = render()
    cols0 = set(map(tuple, base[base[..., 3] > 0][:, :3].tolist()))
    cols1 = set(map(tuple, out[out[..., 3] > 0][:, :3].tolist()))
    assert cols1 <= cols0, "a new colour"
    assert set(np.unique(out[..., 3]).tolist()) <= {0, 255}, "semi-transparent pixels"
    if o.check:
        disk = np.array(Image.open(OUT).convert("RGBA"))
        ok = disk.shape == out.shape and (disk == out).all()
        print("town_facades.png", "matches the build" if ok else "DIFFERS from the build"); sys.exit(0 if ok else 1)
    Image.fromarray(out).save(OUT)
    print(f"town_facades.png: {int((out != base).any(2).sum())} px rebuilt, {len(cols1)} colours")
    if o.houses:
        os.makedirs(o.houses, exist_ok=True)
        for n in HOUSES:
            Image.fromarray(render_house(n)[1]).save(os.path.join(o.houses, n + ".png"))
    if o.parts: parts_sheet(o.parts)
