#!/usr/bin/env python3
"""Art batch 1 into the game (r8/preview): puts each file of riverwalk/art/r8/ (docs/art_batch1.md) where its hook
looks for it (docs/art_hooks_r8.md). Only whole-pixel operations: copy, mirror, re-lay frames into bigger cells
(padding), never a resample.

  python3 tools/wire_r8_art.py            write the hook files
  python3 tools/wire_r8_art.py --list     print their paths (relative to riverwalk/), one per line
  python3 tools/wire_r8_art.py --misfit D write the pieces that do NOT fit their boxes (gable, chimney, dormer) under
                                          their hook names into the folder D (a LOVE save folder), for the
                                          diagnostic shots only; they are not wired into the game

Not wired (they do not fit their boxes, see CHANGELOG.md, r8/preview): roof_gable.png (4 steps of about 20 px; the
level's gable is 15 steps of 4 px), roof_chimney.png (24 wide on a 16 px box, its pots 7 px over the top the golden
bone sits on), roof_dormer.png (a pitched roof on a flat 56 px box), roof_awning56.png (the springy awning keeps its
art: not hooked, and drawn from the side).
"""
import os
import sys
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "riverwalk")
SRC = os.path.join(ROOT, "art", "r8")

COPY = {
    # Downtown street (D1)
    "art/scene/cargo_bike.png": "cargobike.png",
    "art/scene/cargo_bike_pedal.png": "cargobike_pedal.png",
    # River Walk: the promenade riders (84 px) and the road's near lane (92 px, one step closer to the camera)
    "art/scene/cyclist_adult1.png": "cyclist_a_84.png",
    "art/scene/cyclist_adult2.png": "cyclist_b_84.png",
    "art/scene/cyclist_adult1_pedal.png": "cyclist_a_84_pedal.png",
    "art/scene/cyclist_adult2_pedal.png": "cyclist_b_84_pedal.png",
    "art/scene/cyclist_adult1_near.png": "cyclist_a_92.png",
    "art/scene/cyclist_adult2_near.png": "cyclist_b_92.png",
    "art/scene/cyclist_adult1_near_pedal.png": "cyclist_a_92_pedal.png",
    "art/scene/cyclist_adult2_near_pedal.png": "cyclist_b_92_pedal.png",
    # the tall Downtown's high road (obstacles, each drawn at its box's width, the outline row at the box's top - 1)
    "art/scene/town_roof_loggia.png": "roof_loggia.png",
    "art/scene/town_roof_gallery88.png": "roof_gallery88.png",
    "art/scene/town_roof_gallery72.png": "roof_gallery72.png",
    "art/scene/town_roof_ledge.png": "roof_ledge64.png",          # the 3-slice for any width
    "art/scene/town_roof_ledge48.png": "roof_ledge48.png",        # exact for the 48 px ledge
    "art/scene/town_footbridge.png": "footbridge.png",
    # decoration (faded by the game)
    "art/scene/town_front_tall1.png": "house_tall_a.png",
    "art/scene/town_front_tall2.png": "house_tall_b.png",
    "art/scene/town_front_tall3.png": "house_tall_c.png",
    "art/scene/town_row.png": "facades_square.png",
    "art/scene/spire_riddarholmen.png": "spire_riddarholmen.png",
}
MIRROR = {"art/scene/tram_vintage.png": "tram_vintage.png"}     # drawn facing right; the tram drives left
THROW = "art/girl_throw.png"                                      # 8 cells 57 x 60 -> girl.png's 66 x 66
THROW_AT = (5, 6)    # where a 57 x 60 cell goes in a 66 x 66 one: frame 1 (standing) then matches girl.png's idle
                     # frame 1 pixel for pixel but 13 (feet on row 65, feet centre on x 33 as every girl.png cell)
MISFIT = {"art/scene/town_roof_gable.png": "roof_gable.png", "art/scene/town_roof_chimney.png": "roof_chimney.png",
          "art/scene/town_roof_dormer.png": "roof_dormer.png"}


def out(rel, im, base=ROOT):
    p = os.path.join(base, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p)


def main():
    if "--list" in sys.argv:
        for rel in list(COPY) + list(MIRROR) + [THROW]:
            print(rel)
        return
    if "--misfit" in sys.argv:
        d = sys.argv[sys.argv.index("--misfit") + 1]
        for rel, src in MISFIT.items():
            out(rel, Image.open(os.path.join(SRC, src)).convert("RGBA"), d)
        return
    for rel, src in COPY.items():
        out(rel, Image.open(os.path.join(SRC, src)).convert("RGBA"))
    for rel, src in MIRROR.items():
        out(rel, Image.open(os.path.join(SRC, src)).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT))
    t = Image.open(os.path.join(SRC, "mia_throw.png")).convert("RGBA")
    n = t.width // 57
    sheet = Image.new("RGBA", (66 * n, 66), (0, 0, 0, 0))
    for i in range(n):
        sheet.paste(t.crop((i * 57, 0, i * 57 + 57, 60)), (i * 66 + THROW_AT[0], THROW_AT[1]))
    out(THROW, sheet)
    print("wired %d files" % (len(COPY) + len(MIRROR) + 1))


if __name__ == "__main__":
    main()
