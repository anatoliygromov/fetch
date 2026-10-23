"""r8/art batch 1, lines B1 to B5 (people and bikes): the 1x stills and the clip sheets, in riverwalk/art/r8/.

Sources (SpriteCook; asset ids, prompts and credits in docs/art_batch1.md):
  source_scenery/r8_b1_cyclists_v1_px.png   the chosen cyclists picture (252eab71), SpriteCook's pixel output
  source_scenery/r8_b5_cargobike_v1_px.png  the chosen cargo bike (48ad61dc), SpriteCook's pixel output (already 1x)
  source_sheets/r8_<name>_1x.png            the 1x stills that were imported to SpriteCook as the animation sources.
      They were made in the browser by tools/r8_browser_reduce.js from the two pictures above (SpriteCook files can
      only be uploaded from there) and downloaded again byte for byte; tools/r8lib.py does the same steps in Python.
  source_sheets/r8_<name>_pedal.png         the pedal loops (pixel-engine-v1.5, 8 frames each)
  source_sheets/r8_mia_throw.png            Mia's throw (pixel-engine-v1.5 from her standing pose 7ca7be0e)
Outputs:
  cyclist_a_84.png, cyclist_b_84.png        promenade riders (woman red coat; man green jacket), 84 px tall, face right
  cyclist_a_92.png, cyclist_b_92.png        road (near lane) riders, 92 px tall, face right
  cargobike.png                             the cargo bike with its rider, 102 x 76, faces left, box at the left
  cyclist_a_84_pedal.png ... cyclist_b_92_pedal.png, cargobike_pedal.png, mia_throw.png
      8 frames in one row, every cell the same size (the clips' common bounding box), wheels / feet on the bottom row.
      The cargo clip is mirrored like the still (the animator was given the bike facing right)."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r8lib import SS, R8, load, save, outline, mirror, despeckle, drop_isolated
from scipy import ndimage as nd


def clean(f):
    """one animation frame: binary alpha, the animator's grey matte (#7e7e7e) peeled from the outside in, specks
    under 5 px gone, lone pixels merged, 1 px outline in the frame's darkest colour"""
    f = f.copy()
    rgb = f[..., :3].astype(int)
    al = f[..., 3] >= 128
    grey = ((rgb.max(-1) - rgb.min(-1)) < 8) & (np.abs(rgb[..., 0] - 126) < 8)
    for _ in range(3):
        pad = np.pad(al, 1)
        border = al & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        al &= ~(grey & border)
    lab, k = nd.label(al, structure=np.ones((3, 3)))
    if k > 1:
        sizes = nd.sum(al, lab, range(1, k + 1))
        for i, s in enumerate(sizes, 1):
            if s < 5: al[lab == i] = False
    f[..., 3] = np.where(al, 255, 0)
    f[~al, :3] = 0
    return outline(despeckle(f, passes=1))


def clip(name, flip=False):
    a = load(os.path.join(SS, name))
    fh = a.shape[0]
    n = a.shape[1] // fh
    frames = [clean(a[:, i * fh:(i + 1) * fh]) for i in range(n)]
    if flip: frames = [mirror(f) for f in frames]
    op = np.any([f[..., 3] > 0 for f in frames], 0)
    ys, xs = np.where(op)
    frames = [f[ys.min():ys.max() + 1, xs.min():xs.max() + 1] for f in frames]
    return np.concatenate(frames, 1), frames[0].shape[1], frames[0].shape[0]


for name in ("cyclist_a_84", "cyclist_b_84", "cyclist_a_92", "cyclist_b_92"):
    save(drop_isolated(load(os.path.join(SS, "r8_%s_1x.png" % name))), os.path.join(R8, name + ".png"))
save(mirror(load(os.path.join(SS, "r8_cargobike_1x.png"))), os.path.join(R8, "cargobike.png"))

CELLS = {}
for name, flip in (("cyclist_a_84", False), ("cyclist_b_84", False), ("cyclist_a_92", False),
                   ("cyclist_b_92", False), ("cargobike", True)):
    sheet, cw, ch = clip("r8_%s_pedal.png" % name, flip)
    save(sheet, os.path.join(R8, name + "_pedal.png"))
    CELLS[name + "_pedal"] = (cw, ch)
sheet, cw, ch = clip("r8_mia_throw.png")
save(sheet, os.path.join(R8, "mia_throw.png"))
CELLS["mia_throw"] = (cw, ch)
for k, (cw, ch) in CELLS.items():
    print("  cells", k, cw, "x", ch, "x 8")
