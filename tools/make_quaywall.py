# Draws the granite quay wall under River Walk's ramps and the lower quay (riverwalk/art/scene/quaywall.png,
# 320 x 48, tiles left to right). Built by rule here; nothing from outside. Owner, 6 Nov: the road under the ramps
# was a sheared copy of the asphalt, so wherever the walk is not the level promenade (y 184) the ground below the
# kerb is this wall instead (Sc.paintGround), and the road starts where the promenade is level.
#   * colours: the road's blue-grey family (make_road.py) so the wall sits at the road's value; joints in the kerb's
#     shadow (72, 82, 107), light from the upper left (lit top and left edge of each block, darker bottom row)
#   * courses 12 px tall, blocks 22 to 46 px long in running bond, a little grain; level courses everywhere:
#     the game anchors the tile at world y QUAY_Y0 (scene.lua), so on a ramp the slope cuts the courses, never shears them
#   * wraps at x = 320
import os, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'riverwalk', 'art', 'scene', 'quaywall.png')
W, H, CH = 320, 48, 12
BASE = np.array([96, 103, 124]); LIT = np.array([118, 125, 144]); SHADE = np.array([84, 91, 111])
JOINT = np.array([72, 82, 107]); GRAIN_L = np.array([108, 115, 135]); GRAIN_D = np.array([88, 95, 115])
rng = np.random.default_rng(6)
img = np.tile(BASE, (H, W, 1)).astype(int)
for c in range(H // CH):
    y0 = c * CH
    # block lengths for this course, wrapping exactly at W
    x, cuts = (0 if c % 2 == 0 else 17), []
    while True:
        cuts.append(x % W)
        x += int(rng.integers(22, 47))
        if x - (0 if c % 2 == 0 else 17) > W - 22: break
    cuts = sorted(set(cuts))
    for y in range(y0, y0 + CH):
        r = y - y0
        for xx in range(W):
            if r == 0: img[y, xx] = JOINT                                  # bed joint
            elif r == 1: img[y, xx] = LIT                                  # the block's lit top
            elif r == CH - 1: img[y, xx] = SHADE                           # its darker foot
    for cx in cuts:
        for y in range(y0 + 1, y0 + CH):
            img[y, cx] = JOINT                                             # head joint
            img[y, (cx + 1) % W] = LIT if y > y0 + 1 else LIT              # lit left edge of the next block
            img[y, (cx - 1) % W] = SHADE if y > y0 + 1 else img[y, (cx - 1) % W]
    # grain inside the blocks: 1-2 px flecks, sparse
    for _ in range(140):
        y = y0 + int(rng.integers(2, CH - 1)); xx = int(rng.integers(0, W))
        if any((xx - k) % W in cuts for k in (-1, 0, 1)): continue
        img[y, xx] = GRAIN_L if rng.random() < 0.5 else GRAIN_D
Image.fromarray(img.astype(np.uint8), 'RGB').convert('RGBA').save(OUT)
print('wrote', OUT, W, 'x', H)
