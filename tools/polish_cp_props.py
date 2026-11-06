#!/usr/bin/env python3
"""polish_cp_props.py [NAME ...]: fit each City Park prop of the 6 Nov family to its slot and polish it by rule.

  python3 -I tools/polish_cp_props.py                -> riverwalk/art/scene/NAME.png, art/source/NAME/NAME.aseprite,
                                                        art/source/NAME/edits.json

Input: art/source/NAME/NAME_cut.png (tools/cut_cp_props.py). The render is never resampled. A piece that came out
longer or taller than its box is fitted by SPLICING: whole rows or columns of real pixels are taken out (a band of k
straight rows or columns, chosen where the rows on either side of the band match best, so the seam is invisible on
horizontal bark grain, leaf clumps or granite), every kept pixel stays exactly as the render drew it. Then:
  - obstacles: the 1 px outline closed in the piece's ink after the splice (seams can open the silhouette);
  - decoration (the leaf piles): no ink; an edge darker than luma 45 takes the darkest leaf shade;
  - hand edits from HAND below (pixel, colour), each with its reason.
Every changed or removed pixel is listed in art/source/NAME/edits.json; the .aseprite source is written by
tools/aseprite_io.py (one layer, one frame)."""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io
import cleanpass

LUM = np.array([0.299, 0.587, 0.114])

# name: list of ops; ('crop_rows', a, b) keeps rows a..b-1; ('splice_rows', k, lo, hi) removes the best band of k rows
# whose first row is in lo..hi; the same for columns; outline True for obstacles
PLAN = {
    'park_hedge':       dict(ops=[('splice_rows', 5, 12, 48)], outline=True,
                             why='77 rows to 72: the box is 53 solid rows over a 19 row crawl gap; 5 rows of leaf clumps out of the body'),
    'park_leaves':      dict(ops=[('splice_rows', 5, 5, 18)], outline=False, tol=90,
                             why='27 rows to 22: the heap is drawn over Pepper and must stay under her back (26 px)'),
    'park_leaves_flat': dict(ops=[], outline=False, tol=90, palette_from='park_leaves', why='as cut (64 x 12): the same leaves spread low'),
    'park_stone':       dict(ops=[('splice_cols', 3, 6, 20), ('crop_rows', 0, 55)], outline=True,
                             why='29 to 26 wide: the STONE box is 24 + its 1 px outline each side; the 56th row is below the world'),
    'park_hollowlog':   dict(ops=[('trim_top_stub',), ('splice_cols', 28, 16, 30), ('splice_rows', 3, 8, 20)], outline=True,
                             why='72 x 34 to 44 x 27: the piece is 42 wide and 26 tall (top ledge y 302, foot 328); the branch stub, '
                                 '28 columns of horizontal bark grain and 3 rows of the trunk out'),
    'park_boat_front':  dict(ops=[], outline=True, why='as cut (58 x 38); its deck row is 20 (scene.lua Sc.drawMoverArt)'),
}

# hand edits after the fit: (x, y, rgb or None for clear, reason); filled in after the 5x look
HAND = {
    'park_leaves_flat': [(27, 3, 'nb', 'a dark leaf speck inside the lit leaves (asset_qa noise)'),
                         (13, 5, 'nb', 'a dark leaf speck (asset_qa noise)'),
                         (36, 10, 'nb', 'a dark leaf speck (asset_qa noise)'),
                         (6, 8, 'nb', 'a 5 px blotch of a near rust inside the rim (asset_qa blotches)'),
                         (5, 9, 'nb', 'the same blotch'), (3, 10, 'nb', 'the same blotch'), (4, 10, 'nb', 'the same blotch'),
                         (5, 10, 'nb', 'the same blotch')],
}


def band_cost(a, al, i, k, axis):
    """How different the two lines that meet when lines i..i+k-1 are removed (colour distance, alpha mismatch)."""
    if axis == 0:
        p, q, pa, qa = a[i - 1], a[i + k], al[i - 1], al[i + k]
    else:
        p, q, pa, qa = a[:, i - 1], a[:, i + k], al[:, i - 1], al[:, i + k]
    both = pa & qa
    d = np.sqrt(((p.astype(int) - q.astype(int)) ** 2).sum(-1))[both].sum()
    return d + 400 * (pa ^ qa).sum()


def splice(a, al, k, lo, hi, axis):
    best = min(range(lo, hi + 1), key=lambda i: band_cost(a, al, i, k, axis))
    keep = np.r_[0:best, best + k:a.shape[axis]]
    return np.take(a, keep, axis), np.take(al, keep, axis), best


def merge_blotches(rgb, al, passes=3):
    """the new cut's blotches (asset_qa's rule: a 2-24 px patch of one colour inside a near colour, distance < 45,
    not a 1 px drawn line) take the colour around them. Only on a new cut, before the hand polish (BIBLE)."""
    from scipy import ndimage
    rgb = rgb.copy(); merged = []
    for _ in range(passes):
        key = (rgb[..., 0].astype(int) << 16) | (rgb[..., 1].astype(int) << 8) | rgb[..., 2]
        key = np.where(al, key, -1); done = 0
        for k in np.unique(key[al]):
            lab_, n = ndimage.label(key == k, structure=np.ones((3, 3)))
            for i in range(1, n + 1):
                mm = lab_ == i; sz = mm.sum()
                if not (2 <= sz <= 24): continue
                ys, xs = np.nonzero(mm)
                if min(np.ptp(ys), np.ptp(xs)) == 0 and max(np.ptp(ys), np.ptp(xs)) >= 3: continue
                ring = ndimage.binary_dilation(mm, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])) & ~mm
                rk = key[ring]
                if (rk < 0).any(): continue
                vals, cnt = np.unique(rk, return_counts=True)
                if cnt.max() / cnt.sum() < 0.8: continue
                o = int(vals[cnt.argmax()]); oc = np.array([(o >> 16) & 255, (o >> 8) & 255, o & 255])
                if np.sqrt(((oc - rgb[ys[0], xs[0]].astype(int)) ** 2).sum()) >= 45: continue
                rgb[mm] = oc; done += 1; merged.append([int(xs.min()), int(ys.min()), int(sz)])
        if not done: break
    return rgb, merged


def run(name):
    P = PLAN[name]
    im = np.array(Image.open(f'art/source/{name}/{name}_cut.png').convert('RGBA'))
    rgb, al = im[..., :3].copy(), im[..., 3] > 127
    log = {'name': name, 'cut': f'art/source/{name}/{name}_cut.png', 'cut_size': [im.shape[1], im.shape[0]], 'why': P['why'],
           'ops': [], 'outline_px': [], 'hand': []}
    for op in P['ops']:
        if op[0] == 'crop_rows':
            rgb, al = rgb[op[1]:op[2]], al[op[1]:op[2]]; log['ops'].append({'crop_rows': [op[1], op[2]]})
        elif op[0] == 'trim_top_stub':
            # rows at the top that hold less than a third of the widest row are a stub on the trunk: they go
            w = al.sum(1); n = 0
            while w[n] < w.max() / 3: n += 1
            rgb, al = rgb[n:], al[n:]; log['ops'].append({'trim_top_rows': int(n)})
        else:
            axis = 0 if op[0] == 'splice_rows' else 1
            rgb, al, at = splice(rgb, al, op[1], op[2], op[3], axis)
            log['ops'].append({op[0]: {'removed': [int(at), int(at + op[1] - 1)], 'of_the_size_then': True}})
    # trim empty margins left by a splice
    ys, xs = np.nonzero(al)
    rgb, al = rgb[ys.min():ys.max() + 1, xs.min():xs.max() + 1], al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgb, n_clean = cleanpass.clean(rgb.astype(np.uint8), al, P.get('tol', 60), False)
    log['clean_changed'] = int(n_clean)
    if P.get('palette_from'):                          # the same leaves: the heap's colours, nearest in Lab
        from make_palette import lab
        pal = np.unique(np.array(Image.open(f"riverwalk/art/scene/{P['palette_from']}.png").convert('RGBA'))[..., :3][
            np.array(Image.open(f"riverwalk/art/scene/{P['palette_from']}.png").convert('RGBA'))[..., 3] > 0], axis=0)
        px = rgb[al].astype(float); d = ((lab(px)[:, None, :] - lab(pal.astype(float))[None]) ** 2).sum(-1)
        rgb[al] = pal[d.argmin(1)]; log['palette_from'] = P['palette_from']
        rgb, n2 = cleanpass.clean(rgb, al, P.get('tol', 60), False); log['clean_changed'] += int(n2)
    rgb, merged = merge_blotches(rgb, al)
    log['blotches_merged'] = merged
    lum = rgb.astype(float) @ LUM
    pa = np.pad(al, 1)
    edge = al & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
    cols = np.unique(rgb[al], axis=0); cl = cols.astype(float) @ LUM
    if P['outline']:
        ink = cols[cl.argmin()]
        fix = edge & (np.abs(rgb.astype(int) - ink).sum(-1) > 0)
        rgb[fix] = ink
    else:
        warm = cols[(cols[:, 0].astype(int) - cols[:, 2] > 40)]          # the leaves' own colours (red over blue)
        wl = warm.astype(float) @ LUM
        rim = warm[wl.argmin()]                                            # their darkest shade: the rim
        fix = edge & (np.abs(rgb.astype(int) - rim).sum(-1) > 0)
        rgb[fix] = rim
    log['outline_px'] = [[int(x), int(y)] for y, x in zip(*np.nonzero(fix))]
    for x, y, c, why in HAND.get(name, []):
        old = rgb[y, x].tolist() if al[y, x] else None
        if isinstance(c, str):                            # 'nb': the most common colour of its 8 neighbours
            nb = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and 0 <= yy < al.shape[0] and 0 <= xx < al.shape[1] and al[yy, xx]:
                        k = tuple(int(v) for v in rgb[yy, xx]); nb[k] = nb.get(k, 0) + 1
            c = list(max(nb.items(), key=lambda kv: kv[1])[0])
        if c is None: al[y, x] = False
        else: rgb[y, x] = c; al[y, x] = True
        log['hand'].append({'x': x, 'y': y, 'from': old, 'to': c, 'why': why})
    out = np.dstack([rgb, (al * 255).astype(np.uint8)]); out[~al] = 0
    Image.fromarray(out).save(f'riverwalk/art/scene/{name}.png')
    aseprite_io.write(f'art/source/{name}/{name}.aseprite', [out])
    log['size'] = [out.shape[1], out.shape[0]]; log['colours'] = int(len(np.unique(rgb[al], axis=0)))
    json.dump(log, open(f'art/source/{name}/edits.json', 'w'), indent=1)
    print(f"{name:18} {log['cut_size']} -> {log['size']}  colours {log['colours']}  ops {log['ops']}  "
          f"edge {len(log['outline_px'])}  clean {n_clean}  hand {len(log['hand'])}")


if __name__ == '__main__':
    for n in (sys.argv[1:] or PLAN): run(n)
