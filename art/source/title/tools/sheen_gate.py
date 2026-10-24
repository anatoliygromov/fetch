"""Review images for Pepper's shading pass (shade.py):
    python3 art/source/title/tools/sheen_gate.py OUT_DIR FRAMES_DIR [OLD_CLEAN]
  head_8x.png, head_8x_grey.png    her head at 8x in three columns: the native-grid painting (old, noisy), the
                                   cleanup before this pass (OLD_CLEAN, default a1e0e15's still_clean.png from git)
                                   and the picture now (still_clean.png)
  title_3x.png, title_3x_grey.png  the whole title as the game draws it (FRAMES_DIR/title_idle.png from
                                   tools/title_frames.py), 3x
  title_loop_2x.gif                copied from FRAMES_DIR
and the lone-pixel numbers (a pixel with no 4-neighbour of its colour) on Pepper for the three."""
import os, sys, io, shutil, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cleanup as CL, shade as SH
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
T = os.path.join(ROOT, 'art', 'source', 'title')
OUT, FR = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
if len(sys.argv) > 3: mid = Image.open(sys.argv[3]).convert('RGB')
else:
    blob = subprocess.run(['git', 'show', 'a1e0e15:art/source/title/still_clean.png'], cwd=ROOT, capture_output=True).stdout
    mid = Image.open(io.BytesIO(blob)).convert('RGB')
old = Image.open(f'{T}/still_painting.png').convert('RGB'); new = Image.open(f'{T}/still_clean.png').convert('RGB')
BOX, K = (40, 78, 150, 176), 8
for g in (False, True):
    cs = []
    for im in (old, mid, new):
        c = im.crop(BOX)
        if g: c = c.convert('L').convert('RGB')
        cs.append(c.resize((c.width * K, c.height * K), Image.NEAREST))
    o = Image.new('RGB', (sum(c.width for c in cs) + 16, cs[0].height), (255, 0, 255)); x = 0
    for c in cs: o.paste(c, (x, 0)); x += c.width + 8
    o.save(f'{OUT}/head_8x{"_grey" if g else ""}.png')
t = Image.open(f'{FR}/title_idle.png').convert('RGB')
t.resize((960, 720), Image.NEAREST).save(f'{OUT}/title_3x.png')
t.convert('L').convert('RGB').resize((960, 720), Image.NEAREST).save(f'{OUT}/title_3x_grey.png')
shutil.copy(f'{FR}/title_loop_2x.gif', f'{OUT}/title_loop_2x.gif')
M = {n: np.array(Image.open(f'{T}/masks/{n}.png')) > 0 for n in ('coat', 'nose', 'eye', 'tongue', 'bandana')}
pep = (M['coat'] & ~SH.NOT_PEPPER) | M['nose'] | M['eye'] | M['tongue'] | M['bandana']
for n, im in (('old painting', old), ('a1e0e15 clean', mid), ('shaded', new)):
    a = np.array(im).astype(int)
    print(f'{n}: lone pixels on Pepper {CL.lone(a, pep) * 100:.2f} %, her colours {len(np.unique(a[pep], axis=0))}')
