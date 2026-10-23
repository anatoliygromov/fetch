"""tools/build_oldtown.py: Downtown's Old Town row (riverwalk/art/scene/town_facades.png), houses BUILT from stamped
parts (art/pilot-oldtown, 23 Oct 2026; docs/BIBLE.md section 3, the crispness bar).

  python3 -I tools/build_oldtown.py [--check] [--parts out.png]

Each repeated part (window, gable window, door, step of a stepped gable, cornice, string course, plinth) is drawn
ONCE below as a small grid of colour roles, then stamped on an integer grid. Every window of a storey is the same
part at the same height, evenly spaced; storeys are equal; walls are one flat fill with one shade band (the right
edge, light from the upper left); every tread of a gable is the same step part. No resampling of any kind.

The colours are the strip's own 12 (no new colour); each house maps the roles to them. The houses not rebuilt yet
are kept pixel for pixel from source_scenery/town_facades_v06.png (the strip as it was on main v0.6), so the script
regenerates the output exactly. --check: rebuild in memory and fail if the file on disk differs.

The strip is decoration on the mid layer (scrolls 0.5, faded by the game): no outline, edges by a darker shade.
"""
import os, sys, argparse
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "source_scenery", "town_facades_v06.png")
OUT = os.path.join(ROOT, "riverwalk", "art", "scene", "town_facades.png")

# the strip's 12 colours (luma in brackets)
C = dict(
    yellow=(225, 184, 127),     # (190) plaster
    red=(180, 99, 76),          # (121) plaster
    stone=(166, 148, 132),      # (152) cornices, plinths, door frames
    glass=(85, 94, 106),        # (93)
    ochre=(184, 143, 107),      # (151) plaster / yellow's shade
    umber=(127, 111, 102),      # (115) joints, roofs, door split
    frame=(174, 171, 168),      # (172) window frames and glazing bars
    cream=(231, 209, 166),      # (211) plaster
    door=(84, 70, 66),          # (74)
    slate=(123, 129, 136),      # (128)
    brick=(128, 79, 67),        # (92) red's shade
    light=(221, 213, 200),      # (214) lit stone: lintels, sills, cornice tops, gable coping
)

# ---- the parts, drawn once. Roles: W wall, S wall shade, L lit stone, T stone, F frame, G glass, K door leaf,
# ---- D door split / joint, R roof; '.' leaves what is under it.
WINDOW = [          # 7 x 11 window (2 x 2 panes of 2 x 4) with lintel, sill and the sill's shadow: 9 x 14
    "LLLLLLLLL",
    ".FFFFFFF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FFFFFFF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FFFFFFF.",
    "LLLLLLLLL",
    "SSSSSSSSS",
]
GABLE_WINDOW = [    # 7 x 9 attic window (2 x 2 panes of 2 x 3): 9 x 12
    "LLLLLLLLL",
    ".FFFFFFF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FFFFFFF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FGGFGGF.",
    ".FFFFFFF.",
    "LLLLLLLLL",
    "SSSSSSSSS",
]
GABLE_WINDOW_ON_CORNICE = GABLE_WINDOW[:10]   # the cornice below is its sill
DOOR = ["LLLLLLLLL"] + ["TKKKDKKKT"] * 17       # 7 x 17 double door in a stone frame: 9 x 18
STEP_L = ["LL", "L.", "L.", "L.", "L."]           # a gable step, left side: lit tread and riser (2 x 5)
STEP_R = ["LL", ".S", ".S", ".S", ".S"]           # right side: lit tread, riser in shade
TOP_BLOCK_EDGE_L = ["L", "L", "L", "L", "L"]
CORNICE = ["L", "T", "S"]                         # rows: lit top, stone, the shadow it casts on the wall
STRING = ["L", "T", "S"]
PLINTH = ["L", "T", "T", "T", "T"]
FINIAL = [".D.", ".D.", "DDD"]

PARTS = dict(window=WINDOW, gable_window=GABLE_WINDOW, door=DOOR, step_l=STEP_L, step_r=STEP_R,
             cornice=CORNICE, plinth=PLINTH, finial=FINIAL)

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.role = np.full((h, w), ".", dtype="<U1")
    def put(self, x, y, role):
        if 0 <= x < self.w and 0 <= y < self.h: self.role[y, x] = role
    def rect(self, x0, y0, x1, y1, role):          # inclusive
        self.role[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = role
    def stamp(self, part, x, y):
        for dy, row in enumerate(part):
            for dx, ch in enumerate(row):
                if ch != ".": self.put(x + dx, y + dy, ch)
    def row(self, part, x0, x1, y):                 # a horizontal band: each part row across x0..x1
        for dy, row in enumerate(part): self.rect(x0, y + dy, x1, y + dy, row[0])

def build_house(h):
    """h: a house spec -> (x0, canvas of roles, role -> colour)"""
    x0, x1 = h["x0"], h["x1"]
    W = x1 - x0 + 1
    cv = Canvas(W, 111)                              # rows 0..110; row 111 on is the pavement (kept)
    cx = (W - 1) // 2 if W % 2 else None             # the centre column (local)
    top = h["cornice"]                               # first row of the main cornice
    # the body: joint on the left, flat wall, one shade band on the right (light from the upper left)
    cv.rect(0, top, W - 1, 110, "W")
    cv.rect(0, top, 0, 110, "D")
    cv.rect(W - 1, top, W - 1, 110, "S")
    # the gable: levels of equal height, each narrower by the same step; every step is the same part
    g = h.get("gable")
    if g:
        lv_h, step_w, n, hw0 = g["level_h"], g["step_w"], g["levels"], g["top_hw"]
        y_top = top - lv_h * n                       # top row of the top block
        # the roof behind, one 45 degree slope each side from the body's corners up to the gable
        if g.get("roof") is not None:
            ry, rx0, rx1 = g["roof"], g["roof_x0"], g["roof_x1"]   # the slope starts at (rx0, ry) and (rx1, ry)
            for y in range(top):
                for x in range(rx0, rx1 + 1):
                    if y >= ry - min(x - rx0, rx1 - x): cv.put(x, y, "R")
            for x in g.get("roof_cols", []): cv.rect(x, ry, x, top - 1, "R")
        for k in range(n):                           # k = 0 is the top block
            hw = hw0 + step_w * k
            y0 = y_top + lv_h * k
            cv.rect(cx - hw, y0, cx + hw, y0 + lv_h - 1, "W")
        for k in range(n):
            hw = hw0 + step_w * k
            y0 = y_top + lv_h * k
            if k == 0:
                cv.rect(cx - hw, y0, cx + hw, y0, "L")
                cv.stamp(TOP_BLOCK_EDGE_L, cx - hw, y0)
                cv.stamp([".S"] * lv_h, cx + hw - 1, y0); cv.put(cx + hw, y0, "L")
            else:
                cv.stamp(STEP_L, cx - hw, y0)
                cv.stamp(STEP_R, cx + hw - 1, y0)
        cv.stamp(FINIAL, cx - 1, y_top - 3)
        for (wx, wy, part) in g.get("windows", []):
            cv.stamp(PARTS[part] if isinstance(part, str) else part, wx, wy)
    # cornice, string course, plinth: full-width bands
    cv.row(CORNICE, 0, W - 1, top)
    if h.get("string") is not None: cv.row(STRING, 0, W - 1, h["string"])
    cv.row(PLINTH, 0, W - 1, 106)
    # the storeys: one window part, stamped at the same columns on every storey, equal storey heights
    for y in h["storeys"]:
        for x in h["cols"]: cv.stamp(WINDOW, x - 1, y - 1)
    # the ground floor
    gf = h["ground"]
    for x in gf.get("cols", []): cv.stamp(WINDOW, x - 1, gf["win_y"] - 1)
    if "door" in gf: cv.stamp(DOOR, gf["door"] - 1, gf["door_y"] - 1)
    return x0, cv, {k: C[v] for k, v in h["colours"].items()}

# ---- the houses (x on the strip; the strip is 225 x 114 and repeats)
HOUSES = {
    # the red stepped-gable house (the pilot): 37 px, 3 storeys of 16 px, a gable of 6 levels of 5 px with
    # treads of 2 px, two attic windows on the cornice and one above
    "red_gable": dict(
        x0=42, x1=78, cornice=33, string=84,
        cols=[4, 15, 26],                                   # window columns (local x of the frame's left)
        storeys=[39, 55, 71],                               # each storey's window top (frame row)
        ground=dict(cols=[4, 26], win_y=93, door=15, door_y=89),
        gable=dict(level_h=5, step_w=2, levels=6, top_hw=7,
                   windows=[(8, 23, GABLE_WINDOW_ON_CORNICE), (20, 23, GABLE_WINDOW_ON_CORNICE),
                            (14, 10, "gable_window")]),
        colours=dict(W="red", S="brick", L="light", T="stone", F="frame", G="glass", K="door", D="umber",
                     R="umber"),
        # the old house's pixels cleared before the new one goes in: rows 33 on x 42..78, above that x 43..78
        clear=[(42, 33, 78, 110), (43, 0, 78, 32)],
    ),
}

def render(names=None):
    base = np.array(Image.open(BASE).convert("RGBA"))
    out = base.copy()
    for name, h in HOUSES.items():
        if names and name not in names: continue
        for (a0, b0, a1, b1) in h["clear"]: out[b0:b1 + 1, a0:a1 + 1] = 0
        x0, cv, pal = build_house(h)
        for y in range(cv.h):
            for x in range(cv.w):
                r = cv.role[y, x]
                if r == ".": continue
                out[y, x0 + x] = (*pal[r], 255)
    return base, out

def house_alone(name):
    """one house on its own (transparent around it), as the parts build it: for asset_qa and the cards"""
    x0, cv, pal = build_house(HOUSES[name])
    im = np.zeros((cv.h, cv.w, 4), np.uint8)
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.role[y, x] != ".": im[y, x] = (*pal[cv.role[y, x]], 255)
    return im

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the file on disk is not what the script builds")
    ap.add_argument("--house", help="also write one house's crop (rows 0-110) to this path, as NAME=path")
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
    if o.house:
        n, p = o.house.split("=", 1)
        Image.fromarray(house_alone(n)).save(p)
        print(f"{n}: {p}")
