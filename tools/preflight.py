#!/usr/bin/env python3
"""preflight.py JOB.json [JOB2.json ...]: the gate before any generation credit is spent (docs/art_generation.md).

A job is refused unless every rule in art/gen/rules.json holds:
  - level and layer known; the kind may be generated (buildings, fonts, UI are BUILT, never generated);
  - size against Pepper: target height = real height x the layer's px per metre (within the tolerance);
  - the blockout exists, has Pepper's real sprite at 1x, and its frame divides the model's output exactly, so the
    render lands on a whole-pixel grid (k image px per game px, the same k across and down);
  - the mask (subject only) matches the target size;
  - the level's style card exists;
  - the job's own words carry no forbidden look words (haze, pale, misty, faded, ...).
On a pass it WRITES the prompt (the fixed art-direction block, the level's light, the layer's outline and colour cap
are put in by this script, not by hand) and the upload images, and prints one line for the owner with the credits.
Exit code 1 on any failure."""
import sys, json, os
import numpy as np
from PIL import Image

R = json.load(open('art/gen/rules.json'))
os.makedirs('art/gen/prompts', exist_ok=True); os.makedirs('art/gen/upload', exist_ok=True)


def find_pepper(img):
    """True if Pepper's sprite sits in the blockout pixel for pixel."""
    p = R['pepper']
    sp = np.array(Image.open(p['file']).convert('RGBA'))[p['cell'][1]:p['cell'][3], p['cell'][0]:p['cell'][2]]
    ys, xs = np.nonzero(sp[..., 3]); sp = sp[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    a = np.array(img.convert('RGBA')); h, w = sp.shape[:2]; on = sp[..., 3] > 0
    for y in range(a.shape[0] - h + 1):
        for x in range(min(a.shape[1] - w + 1, 40)):
            if np.array_equal(a[y:y + h, x:x + w][on][:, :3], sp[on][:, :3]):
                return True
    return False


def check(path):
    J = json.load(open(path)); n = J['name']; bad = []
    lay = R['layers'].get(J.get('layer')); lev = R['levels'].get(J.get('level'))
    if not lay: bad.append(f"layer '{J.get('layer')}' not in rules ({', '.join(R['layers'])})")
    if not lev: bad.append(f"level '{J.get('level')}' not in rules")
    kind = J.get('kind', '')
    if kind in R['kinds_built']: bad.append(f"kind '{kind}' is BUILT from stamped parts, never generated (crispness bar)")
    elif kind not in R['kinds_generated']: bad.append(f"kind '{kind}' unknown")
    model = R['models'].get(J.get('model', R['default_model']))
    if not model: bad.append(f"model '{J.get('model')}' not in rules")
    tw, th = J['target_px']
    if lay and 'real_height_m' in J:
        want = J['real_height_m'] * lay['px_per_m']
        if abs(th - want) / want > R['size_tolerance']:
            bad.append(f"target height {th} px but {J['real_height_m']} m x {lay['px_per_m']} px/m = {want:.0f} px")
    elif lay and J.get('layer') in ('char', 'play', 'back', 'mid', 'front'):
        bad.append("real_height_m missing: every piece is sized from its real height and the layer scale")
    bo = f"art/gen/blockouts/{n}.png"; mk = f"art/gen/blockouts/{n}_mask.png"; k = None
    if not os.path.exists(bo) or not os.path.exists(mk):
        bad.append(f"blockout {bo} or its mask missing (draw it with tools/blockout_lib.py)")
    else:
        b = Image.open(bo); fw, fh = b.size
        if not find_pepper(b): bad.append("Pepper's real sprite at 1x not found in the blockout (scale reference)")
        if model:
            ow, oh = model['out']
            if ow % fw or oh % fh or ow // fw != oh // fh:
                bad.append(f"frame {fw}x{fh} does not divide {model['name']} output {ow}x{oh} into whole pixels "
                           f"(use 150x112 for 1K, 150x112 or 300x224 for 2K)")
            else:
                k = ow // fw
        m = np.array(Image.open(mk)) > 0; ys, xs = np.nonzero(m)
        mw, mh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if abs(mw - tw) > 2 or abs(mh - th) > 2: bad.append(f"mask is {mw}x{mh}, target {tw}x{th}")
    if lev and not os.path.exists(lev['style_card']): bad.append(f"style card {lev['style_card']} missing (tools/make_style_card.py)")
    words = ' '.join(str(J.get(f, '')) for f in ('subject', 'part_map', 'size_sentence', 'extra')).lower()
    hit = [w for w in R['forbidden_words'] if w in words]
    if hit: bad.append(f"forbidden look words in the job text: {', '.join(hit)} (distance is done by the game)")
    for f in ('subject', 'part_map', 'size_sentence'):
        if not J.get(f): bad.append(f"'{f}' missing")
    if bad:
        print(f"PREFLIGHT FAIL {n}:"); [print('  -', x) for x in bad]; return None
    prompt = (f"Image 1 is an exact-scale layout for a 2D side-view pixel-art game sprite, drawn on an even grid where "
              f"one art pixel is exactly a {k}x{k} block of image pixels. Redraw ONLY the grey shapes as: {J['subject']}. "
              f"Part map: {J['part_map']}\nRules:\n"
              f"1. Every part keeps exactly the position and size of its grey shape. Do not enlarge, shrink or move "
              f"anything. The black dog is the scale reference: {J['size_sentence']}\n"
              f"2. Leave the black dog exactly as it is.\n"
              f"3. The background stays flat solid magenta #FF00FF everywhere. No ground, no shadow, no sky, no "
              f"buildings, no other objects, no text, no logos.\n"
              f"4. {R['art_direction']} {lev['light']}. Outline: {lay['outline']}. At most {lay['colours']} colours.\n"
              f"Keep the framing of image 1." + (f"\n{J['extra']}" if J.get('extra') else ''))
    open(f'art/gen/prompts/{n}.txt', 'w').write(prompt)
    Image.open(bo).convert('RGB').resize((fw * k, fh * k), Image.NEAREST).save(f'art/gen/upload/{n}_blockout.png')
    job = {'name': n, 'model': model['name'], 'modelId': model['artlist']['modelId'], 'settings': model['artlist']['settings'],
           'inputs': [f'art/gen/upload/{n}_blockout.png', lev['style_card']], 'prompt_file': f'art/gen/prompts/{n}.txt',
           'k': k, 'frame': [fw, fh], 'credits': model['credits'] * J.get('variants', 1)}
    json.dump(job, open(f'art/gen/prompts/{n}.job.json', 'w'), indent=1)
    print(f"PREFLIGHT PASS {n}: {J['layer']} {lay['px_per_m']} px/m, {tw}x{th} px ({J.get('real_height_m')} m), "
          f"{fw}x{fh} frame = {k} px grid on {model['name']}, style card {J['level']}, {job['credits']} credits")
    return job


if __name__ == '__main__':
    jobs = [check(p) for p in sys.argv[1:]]
    ok = [j for j in jobs if j]
    print(f"\n{'Rulebook check passed' if len(ok) == len(jobs) else 'BLOCKED'}: {len(ok)}/{len(jobs)} jobs, "
          f"{sum(j['credits'] for j in ok)} credits")
    sys.exit(0 if len(ok) == len(jobs) else 1)
