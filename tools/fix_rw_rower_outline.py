#!/usr/bin/env python3
"""Thin the rower's doubled outline to 1 px (owner 7 Nov: "the dude in the boat has double stroke on him").

Rule: an opaque pixel P is a doubled outline when P is dark (luma < 50), P touches no transparent pixel (it is not
the outline itself), and for some direction d: the pixel P-d is the outline (dark and touching transparency) and the
pixel P+d is light (luma >= 50). P takes the colour of P+d. Run once on the art; every changed pixel is listed in
art/source/rw_rower/edits.json. --check: rerunning changes nothing.
"""
import json, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "riverwalk/art/scene/rw_rower.png"
LOG = ROOT / "art/source/rw_rower/edits.json"

def luma(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def passes(im):
    w, h = im.size; px = im.load()
    def op(x, y): return 0 <= x < w and 0 <= y < h and px[x, y][3] > 0
    def edge(x, y): return op(x, y) and any(not op(x + dx, y + dy) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))
    def dark(x, y): return op(x, y) and luma(px[x, y]) < 50
    ch = []
    for y in range(h):
        for x in range(w):
            if not dark(x, y) or edge(x, y): continue
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                ox, oy, ix, iy = x - dx, y - dy, x + dx, y + dy
                if edge(ox, oy) and dark(ox, oy) and op(ix, iy) and luma(px[ix, iy]) >= 50:
                    ch.append((x, y, px[x, y], px[ix, iy])); break
    return ch

im = Image.open(ART).convert("RGBA")
ch = passes(im)
if "--check" in sys.argv:
    print("OK" if not ch else f"{len(ch)} doubled outline pixels"); sys.exit(1 if ch else 0)
px = im.load()
for x, y, old, new in ch: px[x, y] = new
im.save(ART)
LOG.write_text(json.dumps({"rule": __doc__.strip().splitlines()[0], "changed": [
    {"x": x, "y": y, "frame": x // 92 + 1, "from": list(o), "to": list(n)} for x, y, o, n in ch]}, indent=1))
print(len(ch), "pixels changed")
