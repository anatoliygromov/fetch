"""B0 (r8/art): the chapter 1 style sheet, composited in code from approved 1x art (no generation, 0 credits).

Output: source_sheets/r8_style_ch1_2x.png (2x nearest upscale of a 1x composite; uploaded to SpriteCook as the
style reference for every batch 1 generation) and source_sheets/r8_style_ch1_1x.png.
Three panels, each on its own level's ground strip and sky colour (riverwalk/look.lua bands): River Walk (the screen-1
building, lamp, road cyclist, Mia, Pepper, bin, bench), City Park (the oak, the leaf-cart keeper, the goose, Pepper),
Downtown (two plaza houses, the kiosk, the cat, the awning, crates, Pepper), and a strip of each level's sky bands.
Pepper's and Mia's frames are only read (never written)."""
import os
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "riverwalk", "art")
SC = os.path.join(ART, "scene")


def load(p): return Image.open(p).convert("RGBA")


def cell(p, cw, ch, c=0, r=0):
    return load(p).crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))


def tight(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


PEPPER = tight(cell(os.path.join(ART, "pepper.png"), 60, 52))
MIA = tight(cell(os.path.join(ART, "girl.png"), 66, 66))
CAT = tight(cell(os.path.join(ART, "cat.png"), 48, 48))
GOOSE = tight(cell(os.path.join(ART, "goose.png"), 34, 34))
KEEPER = tight(cell(os.path.join(SC, "park_keeper_cart.png"), 82, 82))
S = lambda n: tight(load(os.path.join(SC, n)))

PANELS = [
    ("pavement.png", "f4dcb3", "b2c6da",
     [S("building.png"), S("lamp_post.png"), S("road_cyclist1.png"), MIA, PEPPER, S("bin.png"), S("bench.png")]),
    ("park_ground.png", "efcb9b", "a6adc3",
     [S("park_oak.png"), KEEPER, GOOSE, PEPPER, MIA]),
    ("town_ground.png", "e3e9e3", "8db2da",
     [S("town_house1.png"), S("town_house3.png"), S("town_kiosk.png"), CAT, PEPPER, S("town_crate_front.png"), S("town_house2.png")]),
]
SKIES = [["4b7ec2", "5a8aca", "6b98d1", "80a8d7", "98b8db", "b2c6da", "cbd1d4", "dfd7c9", "ecdabd", "f4dcb3"],
         ["6a83b8", "7b91bf", "8f9fc3", "a6adc3", "bebac0", "d4c3b7", "e5c9a9", "efcb9b", "f4cc8e", "f7cd86"],
         ["3e72c3", "4d7fc9", "5f8ecf", "75a0d5", "8db2da", "a7c3de", "c0d3e0", "d5e0e2", "e3e9e3", "ebefe5"]]

GAP, FOOT, GROUND, H = 4, 140, 20, 160
panels = []
for ground, lo, hi, items in PANELS:
    w = sum(i.width for i in items) + GAP * (len(items) + 1)
    p = Image.new("RGBA", (w, H))
    a = np.zeros((H, w, 4), np.uint8)
    top, bot = np.array(hexc(hi)), np.array(hexc(lo))
    for y in range(FOOT):                                        # a plain two-colour sky, banded every 20 rows
        t = min(1, (y // 20) * 20 / FOOT)
        a[y, :] = (top * (1 - t) + bot * t).astype(np.uint8)
    p = Image.fromarray(a)
    g = load(os.path.join(SC, ground))
    for x in range(0, w, g.width):
        p.alpha_composite(g.crop((0, 0, min(g.width, w - x), GROUND)), (x, FOOT))
    x = GAP
    for im in items:
        p.alpha_composite(im, (x, FOOT - im.height + 1 if im is not KEEPER else FOOT - im.height + 1))
        x += im.width + GAP
    panels.append(p)
rows = [[panels[0], panels[1]], [panels[2]]]
W = max(sum(p.width for p in r) + 4 * (len(r) - 1) for r in rows)
sheet = Image.new("RGBA", (W, H * 2 + 4), hexc("2a2a32"))
y = 0
for r in rows:
    x = 0
    for p in r:
        sheet.alpha_composite(p, (x, y)); x += p.width + 4
    y += H + 4
for i, sk in enumerate(SKIES):                                   # the three levels' sky bands as swatches
    for j, c in enumerate(sk):
        sheet.paste(Image.new("RGBA", (16, 16), hexc(c)), (panels[2].width + 12 + j * 16, H + 12 + i * 20))
out = os.path.join(ROOT, "source_sheets")
sheet.save(os.path.join(out, "r8_style_ch1_1x.png"))
sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(os.path.join(out, "r8_style_ch1_2x.png"))
print("source_sheets/r8_style_ch1_1x.png", sheet.size, "and _2x", (sheet.width * 2, sheet.height * 2))
