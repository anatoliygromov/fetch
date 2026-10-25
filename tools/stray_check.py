"""tools/stray_check.py IMAGE [OUT_MARKED.png] [--protect x0,y0,x1,y1 ...]: counts stray pixels the way
art/source/title/tools/destray.py defines them (same-colour clusters of 1 or 2 px, not in a checker or a 2/3 px
lattice, outside protected boxes) and writes a 4x map with each one boxed in magenta. Exit 1 if any are found."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'source', 'title', 'tools'))
from destray import stray_mask
args = [a for a in sys.argv[1:]]
boxes = []
if '--protect' in args:
    i = args.index('--protect'); boxes = [tuple(int(v) for v in b.split(',')) for b in args[i+1:]]; args = args[:i]
a = np.array(Image.open(args[0]).convert('RGBA'))
prot = np.zeros(a.shape[:2], bool)
for x0, y0, x1, y1 in boxes: prot[y0:y1, x0:x1] = True
m = stray_mask(a, prot); ys, xs = np.nonzero(m)
print('STRAY', int(m.sum()))
if len(args) > 1:
    im = Image.open(args[0]).convert('RGB'); W, H = im.size; im = im.resize((W*4, H*4), Image.NEAREST); d = ImageDraw.Draw(im)
    for y, x in zip(ys, xs): d.rectangle([x*4-2, y*4-2, x*4+5, y*4+5], outline=(255, 0, 255))
    im.save(args[1])
sys.exit(1 if m.sum() else 0)
