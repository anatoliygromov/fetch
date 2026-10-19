"""Builds the art for the critters and set pieces added on levels/v2 (19 Oct, SpriteCook, 250 credits):

  riverwalk/art/goose.png           rows walk (8), hiss (6), fly (8); 34 x 34 cells, feet on row 33, faces right
  riverwalk/art/gull.png            6 flap frames, 26 x 26 cells, faces right
  riverwalk/art/scene/rowboat.png   8 rowing frames, 70 x 70 cells; hull x 4-64, the deck on row 55
  riverwalk/art/scene/town_tramshed70.png, town_tramshed96.png   the tram shed front, 70 and 96 px wide
  riverwalk/art/scene/rw_jetty.png  the harbour jetty, 48 x 41

Sources (all SpriteCook, Nano Banana 2.1 still images; animations pixel-engine-v1.5 from the 1x sources):
  source_sheets/goose_source.png (asset 3ce87d96, made from e42044c1), goose_walk.png (12af62e2),
  goose_hiss.png (b93c87a7), goose_fly.png (5ddc79b1); gull_source.png (58d1c78a, from b405df2f),
  gull_flap.png (7f1334dd); rowboat_source.png (000403bc, from da3dc833), rowboat_row.png (f7b4974a);
  source_scenery/tramshed_spritecook.png (f0a432e3), jetty_spritecook.png (db280da5).
The still images were reduced to game size with a box filter, snapped to their own palette and given a 1 px dark
outline (shrink below). Animation cleanup like the cat's: the animator's grey matte at the edges becomes
transparent, detached specks go, and a 1 px dark outline closes every open edge."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SS, SC = os.path.join(ROOT, "source_sheets"), os.path.join(ROOT, "source_scenery")
ART = os.path.join(ROOT, "riverwalk", "art")


def shrink(src, W, H, cut=0.5):
    """box-filter a still image to W x H, snap to its own colours, 1 px dark outline"""
    a = np.array(Image.open(src).convert("RGBA")).astype(float)
    pre = np.dstack([a[..., :3] * (a[..., 3:4] / 255), a[..., 3]])
    sm = np.array(Image.fromarray(pre.clip(0, 255).astype(np.uint8), "RGBA").resize((W, H), Image.BOX)).astype(float)
    A = sm[..., 3] / 255
    pal = np.unique(a[a[..., 3] > 127][:, :3], axis=0)
    out = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            if A[y, x] > cut:
                c = sm[y, x, :3] / A[y, x]
                out[y, x, :3] = pal[((pal - c) ** 2).sum(1).argmin()]; out[y, x, 3] = 255
    return outline(out, pal[pal.sum(1).argmin()])


def outline(img, dark):
    op = img[..., 3] > 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    lum = img[..., :3].astype(int).sum(-1)
    img[edge & (lum > 200), :3] = dark
    return img


def clean(f):
    """one animation frame: matte off, specks off, dark outline"""
    f = f.copy()
    rgb = f[..., :3].astype(int)
    al = f[..., 3] >= 128
    sat = rgb.max(-1) - rgb.min(-1)
    grey = (sat < 6) & (abs(rgb[..., 0] - 126) < 6)              # the animator's #7e7e7e matte
    for _ in range(3):                                           # peel it from the outside in
        pad = np.pad(al, 1)
        border = al & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        al &= ~(grey & border)
    lab, k = nd.label(al, structure=np.ones((3, 3)))
    if k > 1:
        sizes = nd.sum(al, lab, range(1, k + 1))
        for i, s in enumerate(sizes, 1):
            if s < 5: al[lab == i] = False
    f[..., 3] = np.where(al, 255, 0)
    dark = rgb[al][rgb[al].sum(1).argmin()]
    return outline(f, dark)


def sheet(name, fw, frames=None):
    a = np.array(Image.open(os.path.join(SS, name)).convert("RGBA"))
    n = a.shape[1] // fw
    return [clean(a[:, i * fw:(i + 1) * fw]) for i in (frames or range(n))]


def save(rows, path):
    h, w = rows[0][0].shape[:2]
    out = np.zeros((h * len(rows), w * max(len(r) for r in rows), 4), np.uint8)
    for r, fs in enumerate(rows):
        for i, f in enumerate(fs): out[r * h:(r + 1) * h, i * w:(i + 1) * w] = f
    Image.fromarray(out).save(path); print(os.path.relpath(path, ROOT), out.shape[1], "x", out.shape[0])


save([sheet("goose_walk.png", 34), sheet("goose_hiss.png", 34), sheet("goose_fly.png", 34)], os.path.join(ART, "goose.png"))
save([sheet("gull_flap.png", 26)], os.path.join(ART, "gull.png"))
save([sheet("rowboat_row.png", 70)], os.path.join(ART, "scene", "rowboat.png"))

shed = shrink(os.path.join(SC, "tramshed_spritecook.png"), 81, 41)     # cornice row 0, wall to row 36, rails below
for w in (70, 96):                                                       # narrower: drop brick columns; wider: repeat
    if w < shed.shape[1]:
        out = np.concatenate([shed[:, :4], shed[:, 4 + shed.shape[1] - w:]], 1)
    else:
        add, parts = w - shed.shape[1], [shed[:, :20]]
        while add > 0:
            parts.append(shed[:, 4:4 + min(add, 16)]); add -= min(add, 16)
        out = np.concatenate(parts + [shed[:, 20:]], 1)
    Image.fromarray(out).save(os.path.join(ART, "scene", "town_tramshed%d.png" % w))
    print("riverwalk/art/scene/town_tramshed%d.png" % w, out.shape[1], "x", out.shape[0])
Image.fromarray(shrink(os.path.join(SC, "jetty_spritecook.png"), 48, 41)).save(os.path.join(ART, "scene", "rw_jetty.png"))
print("riverwalk/art/scene/rw_jetty.png 48 x 41")
