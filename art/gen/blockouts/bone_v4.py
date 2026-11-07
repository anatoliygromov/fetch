# bone_v4 (owner 7 Nov 15:26: "I think the bones need to be more volumetric"): three horizontal bones beside Pepper at
# 1x on a 128 x 128 frame (GPT 2.5 Sunburst 1K: 8 image px per art px): 15 x 9 (today's slot), 19 x 11, 23 x 13.
# The mask is the middle one (the target); the others show the same design at the other sizes.
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, md, g = frame(128, 128, pepper_x=4)
def bone(dd, x0, y0, w, h, col):
    r = max(2, h // 2 - 1)                                   # knob height
    sh = max(1, h // 3)                                      # shaft half-height
    cy = y0 + h // 2
    dd.rectangle([x0 + r, cy - sh, x0 + w - 1 - r, cy + sh], fill=col)
    for kx in (x0, x0 + w - 2 * r):
        dd.ellipse([kx, y0, kx + 2 * r - 1, y0 + h // 2], fill=col)
        dd.ellipse([kx, y0 + h // 2, kx + 2 * r - 1, y0 + h - 1], fill=col)
G = (150, 150, 150, 255)
bone(d, 70, 20, 15, 9, G)
bone(d, 66, 50, 19, 11, G); bone(md, 66, 50, 19, 11, 255)
bone(d, 64, 82, 23, 13, G)
save('bone_v4', c, m, {"subject": "collectible bone, three sizes", "target_px": [19, 11]})
