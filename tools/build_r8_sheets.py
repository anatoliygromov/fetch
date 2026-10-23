"""r8/art batch 1: the owner's contact sheets, one per line at 3x plus an overview at 2x, in /home/claude/out/r8-art/
(or the folder given as the first argument). Every asset stands on its level's ground strip next to Pepper and Mia
at the same scale; the chosen variant first, then the alternates (SpriteCook's own pixel output, shown at 1x as
generated, for comparison) and the old art it is meant to replace. Hit boxes and play lines are drawn in red where
gameplay depends on them. Nothing here is loaded by the game."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r8lib import ROOT, ART, SC, SS, R8, load, crop, palette_snap, despeckle, outline, mirror, fit_height

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/out/r8-art"
os.makedirs(OUT, exist_ok=True)
SCENE = os.path.join(ART, "scene")
SKY = {"riverwalk": (178, 198, 218), "citypark": (230, 200, 160), "downtown": (167, 195, 222)}
GROUND = {"riverwalk": "pavement.png", "citypark": "park_ground.png", "downtown": "town_ground.png"}


def img(p):
    return Image.open(p).convert("RGBA")


def cellcrop(p, cw, ch, c=0, r=0):
    im = img(p).crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
    return im.crop(im.getbbox())


PEPPER = cellcrop(os.path.join(ART, "pepper.png"), 60, 52)
MIA = cellcrop(os.path.join(ART, "girl.png"), 66, 66)


def frames(p, n=8):
    im = img(p)
    w = im.width // n
    return [im.crop((i * w, 0, (i + 1) * w, im.height)) for i in range(n)]


def sheet(name, level, rows, title, scale=3, boxes=()):
    """rows: list of lists of (image, label). Each row stands on the level's ground, Pepper and Mia at its start."""
    pad, gh = 6, 20
    built = []
    for items in rows:
        items = [(PEPPER, "Pepper"), (MIA, "Mia")] + items
        w = sum(i.width for i, _ in items) + pad * (len(items) + 1)
        h = max(i.height for i, _ in items) + 16 + gh
        built.append((items, w, h))
    W = max(w for _, w, _ in built)
    H = sum(h for _, _, h in built) + 14
    c = Image.new("RGBA", (W, H), SKY[level] + (255,))
    g = img(os.path.join(SCENE, GROUND[level]))
    y = 14
    labels = []
    for items, w, h in built:
        foot = y + h - gh
        for x in range(0, W, g.width):
            c.alpha_composite(g.crop((0, 0, min(g.width, W - x), gh)), (x, foot))
        x = pad
        for im, lab in items:
            c.alpha_composite(im, (x, foot - im.height))
            labels.append((x, foot - im.height - 9, lab, im.width))
            x += im.width + pad
        y += h
    big = c.resize((W * scale, H * scale), Image.NEAREST)
    d = ImageDraw.Draw(big)
    d.text((6, 4), title, fill=(20, 20, 30, 255))
    for x, yy, lab, iw in labels:
        d.text((x * scale, max(16, yy * scale)), lab, fill=(20, 20, 30, 255))
    for (x0, y0, x1, y1) in boxes:
        d.rectangle((x0 * scale, y0 * scale, x1 * scale - 1, y1 * scale - 1), outline=(220, 30, 30, 255), width=2)
    p = os.path.join(OUT, name)
    big.save(p)
    print(p, big.size)
    return c


R = lambda n: img(os.path.join(R8, n))
OLD = lambda n: img(os.path.join(SCENE, n))
SRC = lambda n: img(os.path.join(SC, n))


def alt_rider(px, H):
    """the alternate picture through the same steps as the chosen one (for comparison only)"""
    a = np.array(px)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a = crop(a)
    a = outline(crop(despeckle(palette_snap(fit_height(a, H), 20))))
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def split2(im):
    a = np.array(im)
    col = (a[..., 3] > 0).any(0)
    xs = np.where(~col[10:-10])[0] + 10
    mid = xs[np.argmin(np.abs(xs - a.shape[1] // 2))]
    return im.crop((0, 0, mid, im.height)), im.crop((mid, 0, im.width, im.height))


# B0
img(os.path.join(SS, "r8_style_ch1_2x.png")).save(os.path.join(OUT, "B0_style_sheet.png"))
print(os.path.join(OUT, "B0_style_sheet.png"))

# B1 cyclists (stills), alternate v2 through the same steps, old riders
v2 = SRC("r8_b1_cyclists_v2_px.png")
wa, wb = split2(v2)
sheet("B1_cyclists.png", "riverwalk", [
    [(R("cyclist_a_84.png"), "A 84 (chosen v1)"), (R("cyclist_b_84.png"), "B 84"),
     (R("cyclist_a_92.png"), "A 92 road"), (R("cyclist_b_92.png"), "B 92 road")],
    [(alt_rider(wa, 84), "alt v2 A 84"), (alt_rider(wb, 84), "alt v2 B 84"),
     (OLD("road_cyclist1.png"), "old road_cyclist1"), (OLD("cyclist1.png"), "old cyclist1")]],
    "B1 promenade + road cyclists (SpriteCook 252eab71 chosen, 1ec80228 alt)")

# B2, B3 pedal loops
sheet("B2_pedal_loops_84.png", "riverwalk",
      [[(f, "A%d" % (i + 1)) for i, f in enumerate(frames(os.path.join(R8, "cyclist_a_84_pedal.png")))],
       [(f, "B%d" % (i + 1)) for i, f in enumerate(frames(os.path.join(R8, "cyclist_b_84_pedal.png")))]],
      "B2 pedal loops, promenade riders 84 px (2616973e, 3121eb01)")
sheet("B3_pedal_loops_92.png", "riverwalk",
      [[(f, "A%d" % (i + 1)) for i, f in enumerate(frames(os.path.join(R8, "cyclist_a_92_pedal.png")))],
       [(f, "B%d" % (i + 1)) for i, f in enumerate(frames(os.path.join(R8, "cyclist_b_92_pedal.png")))]],
      "B3 pedal loops, road riders 92 px (ee8116f0, 99b22d00)")

# B4 Mia throw
sheet("B4_mia_throw.png", "citypark",
      [[(f, "%d" % (i + 1)) for i, f in enumerate(frames(os.path.join(R8, "mia_throw.png")))]],
      "B4 Mia throw (c576fd67 from her standing pose 7ca7be0e); frame 8 does not settle back to standing")

# B5 cargo bike: still with its 80 x 26 hit box (box + front wheel, bottom-left), loop, alternate, old tram
cb = R("cargobike.png")
v2c = np.array(SRC("r8_b5_cargobike_v2_px.png"))
v2c[..., 3] = np.where(v2c[..., 3] >= 128, 255, 0)
alt = Image.fromarray(outline(despeckle(palette_snap(crop(v2c), 20))).astype(np.uint8), "RGBA").transpose(Image.FLIP_LEFT_RIGHT)
pw = PEPPER.width + MIA.width + 3 * 6
hx, hy = pw, 14 + max(cb.height, PEPPER.height, MIA.height, alt.height, 34) + 16 - 26
sheet("B5_cargo_bike.png", "downtown",
      [[(cb, "cargo bike (chosen v1, hit box red)"), (alt, "alt v2"), (OLD("town_tram.png"), "old tram (hazard)")],
       [(f, "%d" % (i + 1)) for i, f in enumerate(frames(os.path.join(R8, "cargobike_pedal.png")))]],
      "B5 cargo bike hazard (48ad61dc; loop 005b2cf2). Hit box 80 x 26 = cargo box + front wheel",
      boxes=[(hx, hy, hx + 80, hy + 26)])

# B6 tram
sheet("B6_tram.png", "downtown",
      [[(R("tram_vintage.png"), "vintage tram (chosen v1, faded in code)"), (OLD("town_tram.png"), "old toy tram")],
       [(SRC("r8_b6_tram_v2_px.png"), "alt v2 as generated (218 px)")]],
      "B6 vintage tram, back lane decoration (ebc29363 chosen, 8453ee61 alt)")

# B7 roof kit
kit = ["roof_loggia.png", "roof_gallery88.png", "roof_gallery72.png", "roof_gable.png", "roof_chimney.png",
       "roof_dormer.png", "roof_awning56.png", "roof_ledge32.png", "roof_ledge48.png", "roof_ledge64.png"]
sheet("B7_roof_kit.png", "downtown",
      [[(R(k), k[5:-4]) for k in kit[:4]], [(R(k), k[5:-4]) for k in kit[4:]],
       [(SRC("r8_b7_roofkit_v2_px.png"), "alt v2 sheet as generated"), (SRC("r8_b7_roofkit_v1_px.png"), "v1 sheet as generated")]],
      "B7 Downtown roof kit (d4d99e4f chosen, 62b951f5 alt); dormer side face cut off")

# B8 tall house fronts with the screen-1 building for window scale
sheet("B8_house_fronts.png", "downtown",
      [[(R("house_tall_a.png"), "house a"), (R("house_tall_b.png"), "house b"), (R("house_tall_c.png"), "house c"),
        (OLD("building.png"), "screen-1 building (scale)"), (OLD("town_house1.png"), "old house")],
       [(SRC("r8_b8_housefronts_v2_px.png"), "alt v2 as generated")]],
      "B8 tall Old Town house fronts, 240 px (d69a16d5 chosen, c2ea74b3 alt)")

# B9 facades across the square
sheet("B9_facades.png", "downtown",
      [[(R("facades_square.png"), "row across the square (chosen v2)"), (OLD("town_facades.png"), "old town_facades")],
       [(SRC("r8_b9_facades_v1_px.png"), "alt v1 as generated")]],
      "B9 row of house fronts across the square (f6200cac chosen, f24f1355 alt)")

# B10 footbridge, deck line in red
fb = R("footbridge.png")
sheet("B10_footbridge.png", "downtown",
      [[(fb, "footbridge (chosen v1: dog painted out, plank tops cut)"),
        (SRC("r8_b10_footbridge_v2_px.png"), "alt v2 as generated (also has a dog)")]],
      "B10 canal footbridge, 160 px (326e9348 chosen, 8e25f928 alt)")

# B11 spire
sheet("B11_spire.png", "downtown",
      [[(R("spire_riddarholmen.png"), "spire 400 px (chosen v2)"), (SRC("r8_b11_spire_v1_px.png"), "alt v1 as generated"),
        (OLD("building.png"), "screen-1 building")]],
      "B11 Riddarholmen spire (34933164 chosen, 66272059 alt)")

# overview at 2x: every chosen asset beside Pepper and Mia
ov = [[(R("cyclist_a_84.png"), "B1"), (R("cyclist_b_92.png"), "B1 road"), (frames(os.path.join(R8, "mia_throw.png"))[3], "B4"),
       (cb, "B5"), (R("tram_vintage.png"), "B6")],
      [(R(k), "B7") for k in kit[:6]] + [(R("footbridge.png"), "B10")],
      [(R("house_tall_a.png"), "B8"), (R("house_tall_b.png"), "B8"), (R("house_tall_c.png"), "B8"),
       (R("facades_square.png"), "B9"), (R("spire_riddarholmen.png"), "B11")]]
sheet("overview.png", "downtown", ov, "FETCH batch 1 (r8/art) overview, 2x", scale=2)
