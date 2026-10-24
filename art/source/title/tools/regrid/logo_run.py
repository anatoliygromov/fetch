"""Build the logo, write the output contract files and measure every gate.
usage: python3 logo_run.py [iteration-label]"""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_common import *
import logo as LG
import logo_qa as QA

OUT = LG.OUT


def compare(res_rgba, x0, y0, x1, y1, path, scale=10):
    src = Image.open(SRC).convert('RGB')
    o = src.crop((int(round(x0 * PX)), int(round(y0 * PY)), int(round(x1 * PX)), int(round(y1 * PY)))).resize(
        ((x1 - x0) * scale, (y1 - y0) * scale), Image.LANCZOS)
    # result composited on the painting's own cell colours so the context reads
    bg = np.array(src.resize((NX, NY), Image.BOX))
    r = np.where(res_rgba[..., 3:] > 0, res_rgba[..., :3], (bg * 0.35 + 165).astype(np.uint8))
    r = Image.fromarray(r[y0:y1, x0:x1]).resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST)
    w, h = o.size
    c = Image.new('RGB', (2 * w + 8, h), (255, 255, 255)); c.paste(o, (0, 0)); c.paste(r, (w + 8, 0))
    c.save(path)


DETAILS = {
    'cmp_FET': (122, 14, 222, 88),
    'cmp_CH_paw': (205, 8, 302, 78),
    'cmp_depth_F': (122, 30, 172, 88),
    'cmp_depth_ET': (160, 40, 215, 80),
    'cmp_counters_E_C': (168, 22, 240, 66),
    'cmp_highlight_FET': (124, 10, 214, 42),
    'cmp_highlight_CH': (210, 6, 300, 38),
    'cmp_paw': (268, 50, 300, 78),
}


def main(label='final'):
    R = LG.build()
    idx, pal = R['idx'], R['pal']
    used = sorted(set(idx[idx >= 0].tolist()))
    rgba = np.zeros((NY, NX, 4), np.uint8)
    rgba[idx >= 0, :3] = pal[idx[idx >= 0]]
    rgba[idx >= 0, 3] = 255
    mask = idx >= 0
    Image.fromarray(rgba, 'RGBA').save(os.path.join(OUT, 'logo_rgba.png'))
    Image.fromarray((mask * 255).astype(np.uint8)).save(os.path.join(OUT, 'logo_mask.png'))
    palette = [tohex(pal[i]) for i in used]
    json.dump({'palette': palette, 'names': {tohex(pal[i]): LG.NAMES[i] for i in used}},
              open(os.path.join(OUT, 'palette.json'), 'w'), indent=1)
    for name, box in DETAILS.items():
        compare(rgba, *box, os.path.join(OUT, name + '.png'))
    Image.fromarray(rgba, 'RGBA').resize((NX * 4, NY * 4), Image.NEAREST).save(os.path.join(OUT, 'logo_rgba_x4.png'))
    # gates
    geo = QA.geometry_gate(R)
    lines = QA.lines_gate(R)
    col = QA.colour_gate(R, rgba, palette)
    pat = QA.pattern_gate(R)
    form = QA.form_gate(rgba, mask)
    form_fair = QA.form_gate_fair(rgba, mask)
    rep = dict(label=label, geometry=[(n, round(float(i), 4), round(float(b), 3)) for n, i, b in geo],
               lines=lines, colour={k: v for k, v in col.items() if k != 'mixel_map'}, pattern=pat, form=form, form_fair=form_fair, depth=R['G'].get('depth'),
               palette=palette, owned_cells=int(mask.sum()), pawinfo=[tuple(str(v) for v in t) for t in R['G']['pawinfo']])
    json.dump(rep, open(os.path.join(OUT, 'metrics_%s.json' % label), 'w'), indent=1, default=str)
    print(json.dumps(rep, indent=1, default=str))
    return R, rgba, rep


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'final')
