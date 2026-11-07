#!/usr/bin/env python3
"""build_bones_n07.py [--check]: the collectible bones, built by rule (owner, board 7 Nov, bones_06n: "Bones need to be
chunkier and look more distinctive"). Was 11 x 6 (make_night_art.py BONE: a 2 px shaft, knobs 1 px proud).
Now 15 x 9: a classic double-knob dog bone, four round knobs (each a 3 px disc inside its outline) and a 3 px thick shaft, one
1 px dark outline all round (an item Pepper collects reads like a play piece), a cream body with a white highlight
along the top knobs and the shaft's top row, a warm shade along the bottom row and under the lower knobs, and a 1 px
notch between each pair of knobs so the double knob reads at 1x. The gold super bone is the same shape in gold.
Writes riverwalk/art/scene/bone.png and bone_gold.png (the game centres them by their size: stage.lua and
night.lua keep the old centre x and bottom row). --check rebuilds in memory and compares with the files."""
import sys, os
import numpy as np
from PIL import Image
OUT = 'riverwalk/art/scene'
# o outline, h highlight, w body, s shade. Drawn by hand on the grid, symmetric left-right.
BONE = [
    ".ooo.......ooo.",
    "ohhwo.....ohhwo",
    "ohwwooooooowwwo",
    "ohwwwhhhhhwwwso",
    ".owwwwwwwwwwwo.",
    "owwwwssssswwwso",
    "owwsooooooowsso",
    "owsso.....owsso",
    ".ooo.......ooo.",
]
PALS = {
    'bone': {'o': (74, 52, 34), 'h': (255, 255, 250), 'w': (240, 230, 206), 's': (196, 172, 132)},
    'bone_gold': {'o': (92, 54, 10), 'h': (255, 246, 196), 'w': (246, 200, 70), 's': (204, 142, 34)},
}


def build(pal):
    H, W = len(BONE), len(BONE[0]); a = np.zeros((H, W, 4), np.uint8)
    for y, r in enumerate(BONE):
        assert len(r) == W
        for x, ch in enumerate(r):
            if ch in pal: a[y, x, :3] = pal[ch]; a[y, x, 3] = 255
    return a


if __name__ == '__main__':
    check = '--check' in sys.argv; bad = 0
    for n, pal in PALS.items():
        a = build(pal); p = os.path.join(OUT, n + '.png')
        if check:
            same = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), a)
            print(n, 'OK' if same else 'DIFFERS'); bad += not same
        else:
            Image.fromarray(a).save(p); print(p, a.shape[1], 'x', a.shape[0])
    sys.exit(1 if bad else 0)
