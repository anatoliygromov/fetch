"""tools/cleanup_gate.py OUT_DIR: before / after images of the title cleanup (art/source/title/tools/cleanup.py):
the native-grid painting (still_painting.png) and the cleaned picture (still_clean.png), side by side:
  title_3x.png, title_3x_grey.png    the whole picture, 3x
  head_8x.png, head_8x_grey.png      Pepper's head
  bandana_8x.png, leaves_8x.png      (+ _grey)
  masks.png                          the materials, one colour each
and the numbers: colours and lone pixels (no 4-neighbour of its colour), whole picture and Pepper."""
import sys, os, glob
import numpy as np
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'art', 'source', 'title')
a = Image.open(f'{T}/still_painting.png').convert('RGB'); b = Image.open(f'{T}/still_clean.png').convert('RGB')
def grey(im): return im.convert('L').convert('RGB')
def pair(box, k, name):
    for g in (False, True):
        x, y = (grey(a), grey(b)) if g else (a, b)
        ca, cb = x.crop(box), y.crop(box); w, h = ca.size
        o = Image.new('RGB', (w * k * 2 + 8, h * k), (255, 0, 255))
        o.paste(ca.resize((w * k, h * k), Image.NEAREST), (0, 0)); o.paste(cb.resize((w * k, h * k), Image.NEAREST), (w * k + 8, 0))
        o.save(f'{OUT}/{name}{"_grey" if g else ""}.png')
pair((0, 0, 320, 240), 3, 'title_3x'); pair((40, 78, 150, 176), 8, 'head_8x'); pair((20, 160, 140, 236), 8, 'bandana_8x'); pair((0, 0, 120, 70), 8, 'leaves_8x')
cols = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (255, 0, 255), (255, 128, 200), (140, 70, 20), (0, 200, 0), (80, 80, 80), (255, 230, 120),
        (200, 180, 150), (80, 160, 255), (255, 255, 255), (120, 120, 200), (0, 80, 255), (255, 80, 80), (40, 40, 40), (220, 200, 160), (100, 60, 30), (255, 0, 128), (0, 0, 0)]
o = np.zeros((240, 320, 3), np.uint8)
for i, f in enumerate(sorted(glob.glob(f'{T}/masks/*.png'))):
    m = np.array(Image.open(f)) > 0; o[m] = cols[i % len(cols)]
Image.fromarray(o).resize((960, 720), Image.NEAREST).save(f'{OUT}/masks.png')
sys.path.insert(0, os.path.join(T, 'tools')); import cleanup as C
A, B = np.array(a).astype(int), np.array(b).astype(int)
keep = np.array(Image.open(f'{T}/masks/rest.png')) >= 0
pep = np.zeros((240, 320), bool)
for n in ('coat', 'nose', 'eye', 'tongue', 'bandana'): pep |= np.array(Image.open(f'{T}/masks/{n}.png')) > 0
logo = np.ones((240, 320), bool)
for f in glob.glob(f'{T}/masks/*.png'): logo &= ~(np.array(Image.open(f)) > 0)       # the logo and plate: in no mask
pic = ~logo
for n, X in (('before', A), ('after', B)):
    print(f'{n}: colours {len(np.unique(X[pic].reshape(-1, 3), axis=0))}, lone pixels {C.lone(X, pic) * 100:.2f} % (Pepper {C.lone(X, pep) * 100:.2f} %)')
