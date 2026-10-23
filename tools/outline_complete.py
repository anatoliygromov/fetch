"""Complete a 1 px dark outline in place: every opaque pixel with a transparent 4-neighbour whose luma >= 70
takes the file's own outline colour (its most common dark edge colour). No resize, no new colours.

  python3 -I tools/outline_complete.py src.png dst.png [r,g,b]       (an ink given: the whole edge takes it)
  python3 -I tools/outline_complete.py src.png dst.png --skip-bottom [--frames WxH] [--tile]
      --skip-bottom  leave each frame's lowest row alone (ground contact: tools/asset_qa.py does not count it)
      --frames WxH   a sheet: the lowest row of every frame
      --tile         leave the left and right columns alone (tile joins)"""
import sys, numpy as np
from PIL import Image
def edge_mask(al):
    pa = np.pad(al, 1)
    return al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
def run(src, dst, skip_rows=(), ink=None, ring=False, skip_bottom=False, frames=None, tile=False):
    a = np.array(Image.open(src).convert("RGBA"))
    al = a[..., 3] > 127
    lum = a[..., :3] @ [0.299, 0.587, 0.114]
    e = edge_mask(al)
    dk = e & (lum < 70)
    cols, n = np.unique(a[dk][:, :3], axis=0, return_counts=True)
    ink = np.array(ink) if ink is not None else cols[n.argmax()]
    fix = e.copy() if ring else e & (lum >= 70)
    for r in skip_rows: fix[r, :] = False
    if skip_bottom:
        H, W = al.shape
        fw, fh = frames or (W, H)
        for fy in range(0, H, fh):
            for fx in range(0, W, fw):
                rows = np.nonzero(al[fy:fy + fh, fx:fx + fw].any(1))[0]
                if len(rows): fix[fy + rows.max(), fx:fx + fw] = False
    if tile: fix[:, 0] = False; fix[:, -1] = False
    a[fix, :3] = ink; a[fix, 3] = 255
    Image.fromarray(a).save(dst)
    e2 = edge_mask(a[..., 3] > 127); l2 = a[..., :3] @ [0.299, 0.587, 0.114]
    print(src.split('/')[-1], "ink", ink.tolist(), "recoloured", int(fix.sum()), "dark edge %.0f%%" % ((e2 & (l2 < 70)).sum() / e2.sum() * 100))
if __name__ == "__main__":
    args = [v for v in sys.argv[1:] if not v.startswith("--")]
    fr = next((v.split("=", 1)[1] for v in sys.argv if v.startswith("--frames=")), None)
    if "--frames" in sys.argv: fr = sys.argv[sys.argv.index("--frames") + 1]; args.remove(fr)
    ink = [int(v) for v in args[2].split(",")] if len(args) > 2 else None
    run(args[0], args[1], ink=ink, ring=ink is not None, skip_bottom="--skip-bottom" in sys.argv,
        frames=tuple(int(v) for v in fr.split("x")) if fr else None, tile="--tile" in sys.argv)
