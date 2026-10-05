# Makes riverwalk/art/title.png (320x240, the game's screen) from the title painting in source_title/.
# The painting is pixel art drawn at about 7.5 source px per game px but not on an exact grid, so each game
# pixel takes the median colour of the middle half of its cell (crisper than averaging, robust to the grid drift).
import os, numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = np.array(Image.open(os.path.join(ROOT, 'source_title', 'title_original.png')).convert('RGB'))
W, H = 320, 240
h, w = src.shape[:2]
out = np.zeros((H, W, 3), np.uint8)
for j in range(H):
    y0 = int((j + 0.25) * h / H); y1 = max(y0 + 1, int((j + 0.75) * h / H))
    for i in range(W):
        x0 = int((i + 0.25) * w / W); x1 = max(x0 + 1, int((i + 0.75) * w / W))
        out[j, i] = np.median(src[y0:y1, x0:x1].reshape(-1, 3), axis=0)
Image.fromarray(out).save(os.path.join(ROOT, 'riverwalk', 'art', 'title.png'))
print('title.png', W, H)
