# bone_v3 (owner 7 Nov: "the bones look a bit chunkier now, good, but they need to look like something the dog would
# want to collect, more calling for attention, more volumetric"): the collectible bone at 16 x 10 beside Pepper at 1x
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, md, g = frame()
x0, y0 = 70, g - 30                                    # at Pepper's head height, where bones float
for dd in (d, md):
    col = (150, 150, 150, 255) if dd is d else 255
    dd.rectangle([x0 + 3, y0 + 3, x0 + 12, y0 + 6], fill=col)            # the shaft
    for kx in (x0, x0 + 12):                                              # two knobs at each end
        dd.ellipse([kx, y0, kx + 3, y0 + 4], fill=col); dd.ellipse([kx, y0 + 5, kx + 3, y0 + 9], fill=col)
save('bone_v3', c, m, {"subject": "collectible bone", "target_px": [16, 10]})
