#!/usr/bin/env python3
"""Stand-ins for the first art batch's hooks (docs/art_hooks_r8.md), to check each anchor in the game.

  python3 tools/preview_art_hooks.py "$XDG_DATA_HOME/love/pepper_riverwalk"

Writes a labelled, outlined, striped rectangle of the expected size for every hook into that LOVE save folder
(art/... under it). LOVE reads the save folder before the game folder, so the game then draws them as if the art
were in riverwalk/art/. Never point it at the repo. Delete the folder to go back.
"""
import sys, os
from PIL import Image, ImageDraw
root = os.path.abspath(sys.argv[1])
repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root.startswith(repo + os.sep) or root == repo:
    sys.exit("not inside the repo: give the LOVE save folder")
def make(rel, w, h, col, frames=1, label=""):
    im = Image.new("RGBA", (w * frames, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for f in range(frames):
        x = f * w
        d.rectangle([x, 0, x + w - 1, h - 1], fill=col + (255,), outline=(20, 20, 30, 255))
        for k in range(0, h, 8): d.line([x + 1, k, x + w - 2, k], fill=(255, 255, 255, 90))
        d.text((x + 3, 2), (label or os.path.basename(rel)[:8]) + str(f + 1), fill=(0, 0, 0, 255))
    p = os.path.join(root, rel); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
make("art/scene/cargo_bike.png", 96, 76, (230, 60, 200))
make("art/scene/cargo_bike_pedal.png", 96, 76, (230, 60, 200), 8, "CB")
make("art/scene/tram_vintage.png", 300, 130, (40, 90, 220))
for i in (1, 2):
    make("art/scene/cyclist_adult%d.png" % i, 76, 76, (230, 120, 40))
    make("art/scene/cyclist_adult%d_pedal.png" % i, 76, 76, (230, 120, 40), 8, "CY")
make("art/girl_throw.png", 66, 66, (240, 200, 40), 8, "T")
make("art/scene/town_roof_loggia.png", 122, 48, (200, 40, 40))
make("art/scene/town_roof_gallery88.png", 90, 32, (40, 200, 40))
make("art/scene/town_roof_gallery72.png", 74, 32, (40, 160, 40))
make("art/scene/town_roof_chimney.png", 18, 46, (120, 40, 40))
make("art/scene/town_roof_dormer.png", 58, 36, (40, 200, 200))
make("art/scene/town_roof_flower_roof.png", 90, 14, (240, 120, 160))
make("art/scene/town_roof_gable.png", 122, 80, (160, 80, 40))
make("art/scene/town_roof_ledge.png", 24, 9, (90, 90, 240))
make("art/scene/town_footbridge.png", 162, 52, (120, 120, 120))
make("art/scene/town_front_tall1.png", 80, 240, (250, 210, 120))
make("art/scene/town_front_tall2.png", 88, 240, (220, 140, 110))
make("art/scene/town_front_tall3.png", 96, 240, (240, 230, 140))
make("art/scene/town_row.png", 320, 130, (170, 170, 210))
make("art/scene/spire_riddarholmen.png", 32, 400, (60, 90, 80))
