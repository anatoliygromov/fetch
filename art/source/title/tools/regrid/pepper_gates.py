"""PEPPER track: run the renderer, measure every gate, write outputs.

usage: python3 pepper_gates.py [tag]
"""
import sys, os, json, time
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import pepper_render as PR
import pepper_seg as S
import pepper_qa as Q
import lines as LN

OUT = os.environ.get('PEPPER_OUT', '/home/claude/wt/rg-pepper/out')
NX, NY = 320, 240
VIEWS = dict(top=(50, 76, 110, 100), lear=(15, 92, 65, 172), eye=(100, 100, 130, 124), brow=(86, 92, 128, 112),
             wink=(64, 102, 104, 126), nose=(96, 122, 134, 144), mouth=(64, 134, 130, 164),
             tongue=(94, 148, 130, 174), rear=(112, 80, 152, 150), knot=(30, 162, 66, 190),
             folds=(56, 165, 140, 229))


def upscale_region(idx):
    """output palette-index cells -> label image at the region's painting resolution."""
    H, W = S.BOX[3] - S.BOX[1], S.BOX[2] - S.BOX[0]
    I, J = PR.cell_maps((H, W))
    return idx[J][:, I]


def geometry(info):
    pal, L, D, B, O = info['pal'], info['L'], info['D'], info['B'], info['O']
    src_parts = info['parts']
    Lo = upscale_region(info['idx'])
    Do = Lo >= 0
    Lo2 = np.where(Do, Lo, 0)
    Bo = S.bandana_mask(pal, Lo2, Do)
    out_parts = S.part_masks_from_labels(pal, Lo2, Do, Bo)
    res = {}
    for k in ('head', 'earL', 'earR', 'eye', 'nose', 'tongue', 'bandana'):
        pm = src_parts[k] & O
        om = out_parts[k] & Do
        iou, bd = Q.iou_bd(pm, om)
        res[k] = dict(iou=round(float(iou), 4), bd_cells=round(float(bd / PR.CW), 3))
    # whole owned silhouette
    iou, bd = Q.iou_bd(O, Do)
    res['owned'] = dict(iou=round(float(iou), 4), bd_cells=round(float(bd / PR.CW), 3))
    return res, out_parts


def line_metrics(info):
    idx = info['idx']
    masks = []
    for cells, col, lay, d in info['lines']:
        if d['thick'] != 1 or d.get('dropped'):
            continue
        m = PR.cells_to_mask(cells) & (idx == col)
        if m.sum() >= 3:
            masks.append(('line', m, PR.cells_to_mask(cells)))
    for k, shp in ((k_, info['shp'][k_]) for k_ in ('eye', 'nose')):
        r = PR.ring_of(shp) & (idx == info['line_id'])
        masks.append(('ring_' + k, r, PR.ring_of(shp)))
    masks.append(('outline', info['outer_cells'] & (idx == info['line_id']), info['outer_cells']))
    lc = 0; gaps = 0; ok = tot = 0
    for name, m, drawn in masks:
        lc += int(Q.lcorner_count(m).sum())
        # a gap: the drawn line split into more 8-components than it had when drawn
        n0 = ndi.label(drawn, np.ones((3, 3)))[1]
        n1 = ndi.label(m, np.ones((3, 3)))[1]
        gaps += max(0, n1 - n0)
        r, t = LN.staircase_regularity(m)
        ok += r * t; tot += t
    return dict(lcorners=lc, gaps=gaps, staircase=round(ok / max(tot, 1), 4), stair_windows=int(tot))


def colour_metrics(info, rgb, alpha):
    pal, idx, L = info['pal'], info['idx'], info['L']
    palset = set(map(tuple, pal[np.unique(idx[idx >= 0])]))
    off = sum(1 for c in map(tuple, rgb[alpha]) if c not in palset)
    # the colour occurs inside its cell in the painting (label map), or in an 8-neighbour cell
    H, W = L.shape
    I, J = PR.cell_maps((H, W))
    cell = (J[:, None] * NX + I[None, :])
    occ = {}
    for c in np.unique(idx[idx >= 0]):
        cc = np.unique(cell[L == c])
        occ[c] = np.zeros(NX * NY, bool); occ[c][cc] = True
        occ[c] = occ[c].reshape(NY, NX)
    own_ok = nb_ok = n = 0
    for c in occ:
        m = idx == c
        n += m.sum()
        own_ok += (m & occ[c]).sum()
        nb_ok += (m & ndi.binary_dilation(occ[c], np.ones((3, 3)))).sum()
    mix = Q.mixels(rgb, alpha)
    dots = Q.mixels(rgb, alpha, diff=6.0, dots_only=True)
    return dict(off_palette=int(off), colours=len(palset), in_cell=round(own_ok / n, 4),
                in_cell_or_nb=round(nb_ok / n, 4), mixels_strict=int(mix.sum()),
                mixel_dots=int(dots.sum())), mix


def checker_phase(info):
    """Measured on the output: for every dither pair (a, b), 2 x 2 checker windows must
    have b on even (i + j) cells, a lone b in an a field must sit on Bayer cell 0
    ((j, i) even, even), a lone a in a b field on Bayer cell 3 ((j, i) odd, even)."""
    idx = info['idx']; pairs = info['pairs']
    jj, ii = np.indices(idx.shape)
    par = (ii + jj) % 2 == 0
    good = bad = 0
    for a, b in pairs:
        m = (idx == a) | (idx == b)
        w = m[:-1, :-1] & m[1:, :-1] & m[:-1, 1:] & m[1:, 1:]
        alt = (idx[:-1, :-1] == idx[1:, 1:]) & (idx[1:, :-1] == idx[:-1, 1:]) & (idx[:-1, :-1] != idx[1:, :-1])
        cw = w & alt
        g_ = cw & (((idx[:-1, :-1] == b) & par[:-1, :-1]) | ((idx[:-1, :-1] == a) & ~par[:-1, :-1]))
        good += int(g_.sum()); bad += int((cw & ~g_).sum())
        # lone dots
        for lone, field, pos in ((b, a, (0, 0)), (a, b, (1, 0))):
            f = idx == field
            nf = sum(np.roll(np.roll(f, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
            dots = (idx == lone) & (nf == 8)
            # only dots inside a regular pattern (another dot two cells away) count
            reg = dots & (np.roll(idx == lone, 2, 1) | np.roll(idx == lone, -2, 1))
            ok = reg & (jj % 2 == pos[0]) & (ii % 2 == pos[1])
            good += int(ok.sum()); bad += int((reg & ~ok).sum())
    return dict(pattern_cells=good + bad, in_phase=round(good / max(good + bad, 1), 4))


def run(tag='cur', params=None, views=True):
    t = time.time()
    rgb, alpha, info = PR.render(params, verbose=False)
    m = {}
    m['geometry'], out_parts = geometry(info)
    m['lines'] = line_metrics(info)
    m['colour'], mix = colour_metrics(info, rgb, alpha)
    m['pattern'] = checker_phase(info)
    Ofull = np.zeros((1792, 2400), bool)
    x0, y0, x1, y1 = S.BOX
    Ofull[y0:y1, x0:x1] = info['O']
    fm, fp, fmap = Q.form_gate(rgb, alpha, Ofull)
    m['form'] = dict(mean=round(fm, 3), p95=round(fp, 3))
    m['cells'] = int(alpha.sum())
    m['seconds'] = round(time.time() - t, 1)
    d = os.path.join(OUT, 'work', tag)
    os.makedirs(d, exist_ok=True)
    PR.save_rgba(rgb, alpha, os.path.join(d, 'pepper_region.png'))
    np.savez_compressed(os.path.join(d, 'state.npz'), rgb=rgb, alpha=alpha, idx=info['idx'], fmap=fmap, mix=mix)
    if views:
        for k, b in VIEWS.items():
            Q.compare(rgb, alpha, b, 10, os.path.join(d, 'v_%s.png' % k))
        Q.compare(rgb, alpha, (15, 75, 152, 229), 5, os.path.join(d, 'all_5x.png'))
    json.dump(m, open(os.path.join(d, 'metrics.json'), 'w'), indent=1)
    return m, rgb, alpha, info


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'cur'
    m, *_ = run(tag)
    print(json.dumps(m, indent=1))
