"""r8/art batch 1, lines B6 to B11 (Downtown scenery): builds the 1x proposals in riverwalk/art/r8/ from the SpriteCook
sources in source_scenery/r8_*.png (asset ids, prompts and credits in docs/art_batch1.md).

Sources: `_px.png` is SpriteCook's own pixel output (cut out, at its detected pixel grid); `_raw4.png` is the generator's
raw render (white ground) box-reduced 4x in the browser before the transfer (the raw files are 2 to 2.8K wide and
cannot be moved whole). The pixel outputs came back smaller than the targets for the tram, the kit, the house fronts
and the spire, so those are built from the raw render (keyed white ground, box filter down: never scaled up).

Outputs (new files only; nothing in riverwalk/art/scene/ is touched):
  tram_vintage.png        B6  back-lane tram, decoration (no outline), about 300 x 130
  roof_loggia.png         B7  loggia front, 120 wide (one-way top: row 0)
  roof_gallery88.png, roof_gallery72.png      gallery halves, 88 and 72 wide (top rail: row 0)
  roof_gable.png          B7  guild house stepped gable end, 148 wide (the GUILD HOUSE box)
  roof_chimney.png        B7  brick chimney with three pots, 24 wide (CHIMNEY box 16 wide sits inside)
  roof_dormer.png         B7  dormer, front only (its generated side face cut off), 56 wide
  roof_awning56.png       B7  striped window awning on iron arms, 56 wide
  roof_ledge32/48/64.png  B7  stone roof ledges, 8 tall
  house_tall_a/b/c.png    B8  five-storey house fronts, decoration, 240 tall
  facades_square.png      B9  row of house fronts across the square, decoration, 130 tall (repeats by whole houses)
  footbridge.png          B10 canal footbridge, 160 wide, obstacle (the painted dog removed, see below)
  spire_riddarholmen.png  B11 Riddarholmen's spire, decoration, 400 tall
Obstacles get the 1 px dark outline; decoration gets none (dark edge pixels take the darkest inner shade)."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r8lib import SC, R8, load, save, key_white, crop, bbox, box_resize, fit_height, palette_snap, despeckle, \
    outline, no_outline, components, silhouette


def src(name, keyed=True, everywhere=False):
    """keyed: the white ground that touches the border goes; everywhere: all near-white goes (pieces with no white
    of their own, whose railings and arms enclose patches of the ground)"""
    a = load(os.path.join(SC, name))
    if everywhere:
        rgb = a[..., :3].astype(int)
        a = a.copy()
        a[(rgb.min(-1) >= 240) & (rgb.max(-1) - rgb.min(-1) < 12), 3] = 0
        return defringe(a)
    return defringe(key_white(a)) if keyed else a


def defringe(a, passes=2):
    """the render's edge pixels are blended with the white ground: pale unsaturated silhouette pixels go"""
    a = a.copy()
    for _ in range(passes):
        rgb = a[..., :3].astype(int)
        pale = (rgb.min(-1) >= 200) & ((rgb.max(-1) - rgb.min(-1)) < 30)
        a[silhouette(a) & pale, 3] = 0
    return a


def glaze(a, glass=(64, 78, 102)):
    """white ground seen through windows (enclosed white, not reached by the border key) becomes window glass"""
    a = a.copy()
    rgb = a[..., :3].astype(int)
    w = (a[..., 3] > 0) & (rgb.min(-1) >= 236) & ((rgb.max(-1) - rgb.min(-1)) < 14)
    a[w, :3] = glass
    return a


def fit_width(a, W):
    h, w = a.shape[:2]
    return box_resize(a, W, max(1, round(h * W / w)))


def obstacle(a, n=14):
    return outline(crop(despeckle(palette_snap(a, n))))


def lift_darks(a, floor=76, edge_only=False):
    """far-layer decoration: no colour darker than `floor` luma (dark tones read as strokes at a distance); each
    dark colour is scaled up to the floor, keeping its hue (edge_only: only on the silhouette)"""
    a = a.copy()
    op = silhouette(a) if edge_only else a[..., 3] > 0
    rgb = a[..., :3].astype(float)
    l = rgb @ [0.299, 0.587, 0.114]
    m = op & (l < floor)
    k = floor / np.maximum(l[m], 1)
    a[m, :3] = np.clip(rgb[m] * k[:, None] + (rgb[m] < 1) * floor, 0, 255).round().astype(np.uint8)
    return a


def decoration(a, n=14, lift=False):
    d = no_outline(crop(despeckle(palette_snap(a, n))))
    return lift_darks(d) if lift else d


def decoration_h(a, H, n=14, lift=False):
    """decoration at an exact height: peeling the stroke takes a row or two, so fit a little taller and retry"""
    extra = 0
    for _ in range(4):
        d = decoration(fit_height(a, H + extra), n, lift)
        if d.shape[0] >= H:
            return d[d.shape[0] - H:]
        extra += H - d.shape[0]
    return d


def piece(a, box):
    x0, y0, x1, y1 = box
    return crop(a[y0:y1, x0:x1])


# B6 tram (decoration)
tram = glaze(crop(src("r8_b6_tram_v1_raw4.png")))      # its windows were drawn as holes onto the white ground
save(decoration_h(tram, 130, 14, lift=True), os.path.join(R8, "tram_vintage.png"))

# B7 roof kit (obstacles), pieces cut by their boxes in the raw4 sheet (see components() in r8lib)
kit = src("r8_b7_roofkit_v1_raw4.png", everywhere=True)
P = {"loggia": (20, 20, 297, 167), "gallery_long": (325, 28, 492, 85), "gallery_short": (327, 112, 459, 169),
     "gable": (20, 184, 233, 362), "chimney": (245, 192, 315, 349), "dormer": (358, 204, 474, 308),
     "awning": (337, 407, 489, 487), "ledge": (20, 463, 272, 487)}
save(obstacle(fit_width(piece(kit, P["loggia"]), 120)), os.path.join(R8, "roof_loggia.png"))
save(obstacle(fit_width(piece(kit, P["gallery_long"]), 88)), os.path.join(R8, "roof_gallery88.png"))
save(obstacle(fit_width(piece(kit, P["gallery_short"]), 72)), os.path.join(R8, "roof_gallery72.png"))
save(obstacle(fit_width(piece(kit, P["gable"]), 148)), os.path.join(R8, "roof_gable.png"))
save(obstacle(fit_width(piece(kit, P["chimney"]), 24), 12), os.path.join(R8, "roof_chimney.png"))
dormer = piece(kit, P["dormer"])
dormer = crop(dormer[:, :int(dormer.shape[1] * DORMER_FRONT)]) if (DORMER_FRONT := 0.70) < 1 else dormer
save(obstacle(fit_width(dormer, 56), 12), os.path.join(R8, "roof_dormer.png"))
save(obstacle(fit_width(piece(kit, P["awning"]), 56), 10), os.path.join(R8, "roof_awning56.png"))
ledge = piece(kit, P["ledge"])
for w in (32, 48, 64):
    save(obstacle(box_resize(ledge, w, 8), 6), os.path.join(R8, "roof_ledge%d.png" % w))

# B8 tall house fronts (decoration): the row of three, cut at the darkest seam near each third
row = crop(src("r8_b8_housefronts_v1_raw4.png"))
lum = (row[..., :3].astype(float) @ [0.299, 0.587, 0.114]) * (row[..., 3] > 0)
W = row.shape[1]
cuts = []
for t in (W / 3, 2 * W / 3):
    lo, hi = int(t) - 16, int(t) + 16
    cuts.append(lo + int(np.argmin(lum[100:, lo:hi].mean(0))))
for name, (x0, x1) in zip("abc", [(0, cuts[0]), (cuts[0], cuts[1]), (cuts[1], W)]):
    save(lift_darks(decoration_h(crop(row[:, x0:x1]), 240, 13), edge_only=True), os.path.join(R8, "house_tall_%s.png" % name))

# B9 the row of house fronts across the square (decoration, the far-layer strip)
fac = load(os.path.join(SC, "r8_b9_facades_v2_px.png"))
fac[..., 3] = np.where(fac[..., 3] >= 128, 255, 0)
save(decoration_h(crop(fac), 130, 14, lift=True), os.path.join(R8, "facades_square.png"))

# B10 footbridge (obstacle). The generator painted a small dog on the deck (the style reference leaking in): the
# railing and planks are periodic, so the dog's columns are replaced by the same columns one baluster bay along.
fb = obstacle(fit_width(crop(src("r8_b10_footbridge_v1_raw4.png", everywhere=True)), 160), 14)
TOP = (21, 28)                                         # rows of plank tops seen from above: cut (front-on rule)
fb = np.concatenate([fb[:TOP[0]], fb[TOP[1]:]], 0)
DOG = (DOG_X0, DOG_X1, DOG_Y0, DOG_Y1) = (40, 60, 10, 21)   # the painted dog, now in the railing rows
BAY = 35                                               # two baluster bays at 1x
fb[DOG_Y0:DOG_Y1, DOG_X0:DOG_X1] = fb[DOG_Y0:DOG_Y1, DOG_X0 + BAY:DOG_X1 + BAY]
save(fb, os.path.join(R8, "footbridge.png"))

# B11 Riddarholmen spire (decoration, far layer)
sp = crop(src("r8_b11_spire_v2_raw4.png"))
save(decoration_h(sp, 400, 12), os.path.join(R8, "spire_riddarholmen.png"))
