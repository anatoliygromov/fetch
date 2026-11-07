#!/usr/bin/env python3
"""The collectible bones, built by rule (owner 7 Nov 15:02: "chunkier now, good, but they need to look like something
the dog would want to collect, more calling for attention, more volumetric").

Same 15 x 9 silhouette and box as the 7 Nov bone (so no bone moves in any level); the volume is a light from the
upper left in five steps per bone, the colours from SpriteCook's render art/gen/out/bone_v3_3.png (Pixel Engine,
job bone_v3, 24 credits; it drew the bone on a slant at 16 x 16, so only its colours and shading are used): a glossy
streak along the shaft's top, lit upper knobs, a warm golden underside and a deeper shade under the lower knobs,
one dark brown ink. The gold bone is the same pixels in a gold ramp. The sparkle that calls for attention is drawn
in code (stage.lua).

    python3 tools/build_bones.py          write riverwalk/art/scene/bone.png and bone_gold.png
    python3 tools/build_bones.py --check  fail if the files differ from a fresh build
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "riverwalk/art/scene"

# O ink, H highlight, C cream, M mid, G gold shade, D deep shade, . clear
GRID = [
    ".OOO.......OOO.",
    "OHHCO.....OHCCO",
    "OHCCOOOOOOOCCMO",
    "OCHHHHHHHHHHCMO",
    ".OCCCCCCCCCCMO.",
    "OMGGGGGGGGGGGGO",
    "OMGDOOOOOOOMGDO",
    "OGDDO.....OGDDO",
    ".OOO.......OOO.",
]
WHITE = {"O": (75, 33, 4), "H": (255, 254, 239), "C": (249, 231, 193), "M": (240, 212, 158),
         "G": (228, 182, 108), "D": (196, 140, 70)}
GOLD = {"O": (92, 54, 10), "H": (255, 250, 214), "C": (255, 218, 96), "M": (246, 186, 54),
        "G": (214, 138, 26), "D": (160, 88, 12)}


def build(pal):
    h, w = len(GRID), len(GRID[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, row in enumerate(GRID):
        assert len(row) == w
        for x, ch in enumerate(row):
            if ch != ".":
                im.putpixel((x, y), pal[ch] + (255,))
    return im


def main():
    bad = 0
    for name, pal in (("bone", WHITE), ("bone_gold", GOLD)):
        im = build(pal)
        f = OUT / f"{name}.png"
        if "--check" in sys.argv:
            old = Image.open(f).convert("RGBA")
            if old.size != im.size or old.tobytes() != im.tobytes():
                print("DIFFERS", f.name); bad += 1
        else:
            im.save(f); print(f.name, im.size)
    if "--check" in sys.argv:
        print("OK" if not bad else f"{bad} differ")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
