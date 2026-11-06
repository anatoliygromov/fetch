#!/usr/bin/env python3
"""tools/cut_rowboat.py: the round 2 rowing boat render (GPT 2.5 Sunburst 2K, art/gen/renders/rw_rowboat_r2a_raw.png,
owner 6 Nov 19:53: "rerender this asset in spritecook, it's really low quality") to the 1x still.
  1. tools/grid4_cut.py on the 2048 render (the blockout's 512 grid, 4 image px per art px; one pixel per cell,
     majority or centre, never an average) -> art/source/rw_rowboat/cut_r2a.png (the dog and the magenta removed);
  2. colours: k-means to K colours over the boat's own pixels (the render has thousands of near colours), each pixel
     takes its nearest centre: no new colours are mixed, no dithering;
  3. the magenta fringe (purple edge pixels) is cleared; lone pixels are merged by tools/cleanpass.py and the outline
     closed by tools/outline_complete.py --skip-bottom.
Writes art/source/rw_rowboat/still.png (239 x 77)."""
import os, subprocess, sys
import numpy as np
from PIL import Image
from scipy.cluster.vq import kmeans2
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art', 'source', 'rw_rowboat')
K = int(sys.argv[1]) if len(sys.argv) > 1 else 18
a = np.array(Image.open(os.path.join(SRC, 'cut_r2a.png')).convert('RGBA'))
al = a[..., 3] > 0
rgb = a[..., :3].astype(float)
fringe = al & (rgb[..., 0] > 120) & (rgb[..., 2] > 90) & (rgb[..., 1] < 0.6 * rgb[..., 0]) & (rgb[..., 1] < 0.75 * rgb[..., 2])
al &= ~fringe
px = rgb[al]
np.random.seed(6)
cent, lab = kmeans2(px, K, minit='++', seed=6, iter=40)
out = np.zeros_like(a); q = np.zeros(rgb.shape)
q[al] = cent[lab]
out[..., :3] = np.clip(np.round(q), 0, 255).astype(np.uint8); out[..., 3] = np.where(al, 255, 0)
tmp = os.path.join(SRC, '_q.png'); Image.fromarray(out).save(tmp)
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'cleanpass.py'), tmp, tmp, '--max-colours', '20'], check=True)
subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'outline_complete.py'), tmp, os.path.join(SRC, 'still.png'), '--skip-bottom'], check=True)
os.remove(tmp)
