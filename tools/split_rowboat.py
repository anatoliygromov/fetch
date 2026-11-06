#!/usr/bin/env python3
"""tools/split_rowboat.py: splits the cleaned rowing-boat still (art/source/rw_rowboat/still.png) into
  hull.png  - the boat with the man and the near oar taken out (their pixels refilled along each row from the nearest
              hull pixel, as the planks run level; above the gunwale the man's place is empty)
  rower.png - the man above the gunwale and the near oar on their own (the source of the rowing loop), same canvas
The whole-boat loop of 6 Nov redrew the hull in every frame (52-72 % of its pixels changed), so the hull stays the
still and only the rower is animated (owner, 6 Nov: "boat is still ridiculously small"; credits yes 19:37).
Measured on the round 2 still (239 x 77, owner 6 Nov 19:53 asked for a better render) at 5x: the man x 94-149 above
row 44 (the gunwale is row 40), the oar from the handle (144, 28) through (100, 50) and (80, 62) to the blade at (50, 73)."""
import os
import numpy as np
from PIL import Image, ImageDraw
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'art', 'source', 'rw_rowboat')
s = np.array(Image.open(os.path.join(SRC, 'still.png')).convert('RGBA'))
H, W = s.shape[:2]
GUN, RIM = 38, 44                       # above GUN the man's place is empty; GUN..RIM is the rim behind him, refilled
man = np.zeros((H, W), bool); man[:RIM, 94:150] = True
bi = Image.new('L', (W, H), 0); bd = ImageDraw.Draw(bi)
bd.line([(144, 28), (100, 50), (80, 62), (50, 73)], fill=255, width=8, joint='curve')
bd.polygon([(44, 66), (68, 60), (84, 63), (70, 78), (44, 78)], fill=255)          # the blade
band = np.array(bi) > 0
fillm = band | man
hull = s.copy()
for y in range(H):
    xs = [x for x in range(W) if not fillm[y, x] and s[y, x, 3] > 0]
    for x in range(W):
        if not fillm[y, x]: continue
        if y < GUN and man[y, x]:
            hull[y, x] = 0; continue
        if not xs: hull[y, x] = 0; continue
        n = min(xs, key=lambda v: abs(v - x)); hull[y, x] = s[y, n]
# outside the hull's own silhouette (the blade below the keel, the oar left of the bow) nothing stays
inside = np.zeros((H, W), bool)
for y in range(H):
    xs = [x for x in range(W) if s[y, x, 3] > 0 and not fillm[y, x]]
    if xs: inside[y, min(xs):max(xs) + 1] = True
hull[~inside & band] = 0
diff = (np.abs(s[..., :3].astype(int) - hull[..., :3].astype(int)).sum(-1) > 30) | (s[..., 3] != hull[..., 3])
WHITE = np.isin(s[..., :3].astype(int) @ np.array([65536, 256, 1]), [c[0] * 65536 + c[1] * 256 + c[2] for c in
    ((250, 240, 220), (255, 248, 234), (225, 225, 225), (181, 185, 191))])   # the white strake is never the oar
rower = np.zeros_like(s); keep = (band & diff & ~WHITE) | (man & (np.arange(H)[:, None] < GUN + 1))
rower[keep] = s[keep]; rower[s[..., 3] == 0] = 0
Image.fromarray(hull, 'RGBA').save(os.path.join(SRC, 'hull.png'))
Image.fromarray(rower, 'RGBA').save(os.path.join(SRC, 'rower.png'))
bb = Image.fromarray(rower, 'RGBA').getbbox()
print('hull', W, 'x', H, 'rower bbox', bb)
