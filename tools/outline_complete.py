"""Complete a 1 px dark outline in place: every opaque pixel with a transparent 4-neighbour whose luma >= 70
takes the file's own outline colour (its most common dark edge colour). No resize, no new colours."""
import sys, numpy as np
from PIL import Image
def edge_mask(al):
    pa = np.pad(al, 1)
    return al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
def run(src, dst, skip_rows=(), ink=None, ring=False):
    a = np.array(Image.open(src).convert("RGBA"))
    al = a[..., 3] > 127
    lum = a[..., :3] @ [0.299, 0.587, 0.114]
    e = edge_mask(al)
    dk = e & (lum < 70)
    cols, n = np.unique(a[dk][:, :3], axis=0, return_counts=True)
    ink = np.array(ink) if ink is not None else cols[n.argmax()]
    fix = e.copy() if ring else e & (lum >= 70)
    for r in skip_rows: fix[r, :] = False
    a[fix, :3] = ink; a[fix, 3] = 255
    Image.fromarray(a).save(dst)
    e2 = edge_mask(a[..., 3] > 127); l2 = a[..., :3] @ [0.299, 0.587, 0.114]
    print(src.split('/')[-1], "ink", ink.tolist(), "recoloured", int(fix.sum()), "dark edge %.0f%%" % ((e2 & (l2 < 70)).sum() / e2.sum() * 100))
if __name__ == "__main__":
    ink = [int(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    run(sys.argv[1], sys.argv[2], ink=ink, ring=ink is not None)
