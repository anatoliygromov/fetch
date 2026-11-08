#!/usr/bin/env python3
"""plan.py: the owner-approved plan that every paid art job needs (8 Nov 2026, owner 14:19: "how do we make sure you're
not skipping stuff?", 14:20: "yes" to the plan gate).

No approved plan, no credits: tools/preflight.py refuses any job without a "plan" whose approval is the owner's own
words AND whose content is unchanged since he approved it (the approval stores a hash of the plan; any later edit,
even one size, voids it and he has to approve again).

A plan (art/gen/plans/<name>.plan.json) lists every object the job will make:
  {"name": "rt_sheet2_roofs", "level": "rooftops", "kind": "sheet" | "scene" | "asset",
   "why": "what it is for, in one or two sentences",
   "jobs": ["rt_sheet2_roofs"],                        the job names this plan covers
   "frame": [320, 240],                                sheets: the template frame in game pixels
   "background": [255, 0, 255],                        sheets: the flat key colour
   "pepper": [x, y],                                   sheets: where Pepper's real sprite stands (scale anchor)
   "style_refs": ["art/gen/concepts/rt_hotel_concept_a.png"],
   "objects": [{"id": "A", "what": "...", "source": "<concept png> (where in it) | new: <why no concept shows it>",
                "size": [w, h], "role": "obstacle" | "decoration" | "terrain" | "backdrop",
                "layer": "play" | "back" | "mid" | "far" | "front", "view": "front",
                "box": [x, y, w, h], "detail": "every look requirement, in words"}],
   "approval": {"words": "...", "when": "...", "sha": "..."}}       written ONLY by `plan.py approve`

  python3 -I tools/plan.py check PLAN                     problems, exit 1 if any (approval included)
  python3 -I tools/plan.py approve PLAN --words W --when T   record the owner's yes (his words, quoted) and the hash
  python3 -I tools/plan.py template PLAN                  sheets: draw the template from the plan's boxes
                                                          (art/gen/sheets/<name>_template.png at 4x, + _320.png)
  python3 -I tools/plan.py page PLAN OUT.md               a readable page of the plan for the owner"""
import hashlib, json, os, sys

ROLES = ('obstacle', 'decoration', 'terrain', 'backdrop')
LAYERS = ('play', 'back', 'mid', 'far', 'front', 'char')
NEED = ('id', 'what', 'source', 'size', 'role', 'layer', 'view', 'detail')


def load(path): return json.load(open(path))


def sha(plan):
    body = {k: v for k, v in plan.items() if k != 'approval'}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def problems(plan, approval=True):
    bad = []
    for f in ('name', 'level', 'kind', 'why', 'jobs', 'objects'):
        if not plan.get(f): bad.append(f"plan '{f}' missing")
    ids = set()
    for o in plan.get('objects', []):
        oid = o.get('id', '?')
        for f in NEED:
            if not o.get(f): bad.append(f"object {oid}: '{f}' missing")
        if oid in ids: bad.append(f"object id {oid} used twice")
        ids.add(oid)
        if o.get('view') and o['view'] != 'front':
            bad.append(f"object {oid}: view must be 'front' (owner 14:15: frontal perspective)")
        if o.get('role') and o['role'] not in ROLES: bad.append(f"object {oid}: role must be one of {ROLES}")
        if o.get('layer') and o['layer'] not in LAYERS: bad.append(f"object {oid}: layer must be one of {LAYERS}")
        src = str(o.get('source', ''))
        if src and not src.startswith('new:') and not os.path.exists(src.split(' ')[0]):
            bad.append(f"object {oid}: source {src.split(' ')[0]} not found (a concept png, or 'new: why')")
        if plan.get('kind') == 'sheet':
            b = o.get('box')
            if not b or len(b) != 4: bad.append(f"object {oid}: a sheet object needs box [x, y, w, h]")
            else:
                if list(b[2:]) != list(o.get('size', [])): bad.append(f"object {oid}: box size {b[2:]} != size {o.get('size')}")
                fw, fh = plan.get('frame', [320, 240])
                if b[0] < 2 or b[1] < 2 or b[0] + b[2] > fw - 2 or b[1] + b[3] > fh - 2:
                    bad.append(f"object {oid}: box {b} not inside the {fw}x{fh} frame with a 2 px margin")
    if plan.get('kind') == 'sheet':
        boxes = [(o['id'], o['box']) for o in plan.get('objects', []) if o.get('box') and len(o['box']) == 4]
        px, py = plan.get('pepper', [None, None])
        if px is None: bad.append("sheet: 'pepper' [x, y] missing (Pepper's real sprite is the scale anchor)")
        else: boxes.append(('Pepper', [px, py, 52, 38]))
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                (a, (ax, ay, aw, ah)), (b, (bx, by, bw, bh)) = boxes[i], boxes[j]
                if ax < bx + bw + 6 and bx < ax + aw + 6 and ay < by + bh + 6 and by < ay + ah + 6:
                    bad.append(f"boxes {a} and {b} closer than 6 px (each piece must be cut out on its own)")
    if approval:
        ap = plan.get('approval') or {}
        if not ap.get('words') or not ap.get('when'):
            bad.append("plan not approved: the owner reads the plan page and says yes; then plan.py approve --words")
        elif ap.get('sha') != sha(plan):
            bad.append("plan changed after the owner approved it: show him the new version and approve again")
    return bad


def template(plan, root='.'):
    import numpy as np
    from PIL import Image, ImageDraw
    fw, fh = plan.get('frame', [320, 240])
    im = Image.new('RGB', (fw, fh), tuple(plan.get('background', [255, 0, 255]))); d = ImageDraw.Draw(im)
    for o in plan['objects']:
        x, y, w, h = o['box']; d.rectangle([x, y, x + w - 1, y + h - 1], fill=(150, 150, 156), outline=(96, 96, 104))
    pep = Image.open(os.path.join(root, 'riverwalk/art/pepper.png')).convert('RGBA').crop((0, 0, 60, 52))
    a = np.asarray(pep); ys, xs = np.nonzero(a[..., 3]); pep = pep.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    im.paste(pep, tuple(plan['pepper']), pep)
    base = f"art/gen/sheets/{plan['name']}_template"
    os.makedirs('art/gen/sheets', exist_ok=True)
    im.save(base + '_320.png'); im.resize((fw * 4, fh * 4), Image.NEAREST).save(base + '.png')
    json.dump({'boxes': {o['id']: o['box'] for o in plan['objects']}, 'pepper': plan['pepper'],
               'background': plan.get('background', [255, 0, 255]), 'scale': '4x of %dx%d' % (fw, fh), 'plan_sha': sha(plan)},
              open(base + '.json', 'w'), indent=1)
    return base + '.png'


def page(plan):
    L = [f"# {plan['name']}", '', plan['why'], '',
         f"Level: {plan['level']}. Kind: {plan['kind']}. Jobs: {', '.join(plan['jobs'])}.",
         f"Style references: {', '.join(plan.get('style_refs', []))}.", '',
         '| Id | What | Size (game px) | Role | Layer | Source | Look |', '| --- | --- | --- | --- | --- | --- | --- |']
    for o in plan['objects']:
        L.append(f"| {o['id']} | {o['what']} | {o['size'][0]} x {o['size'][1]} | {o['role']} | {o['layer']} | {o['source']} | {o['detail']} |")
    ap = plan.get('approval') or {}
    L += ['', f"Approval: {('\"' + ap['words'] + '\" (' + ap['when'] + ')') if ap.get('words') else 'NOT APPROVED'}", f"Plan hash: {sha(plan)}"]
    return '\n'.join(L) + '\n'


def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    cmd, path = sys.argv[1], sys.argv[2]; plan = load(path)
    if cmd == 'check':
        bad = problems(plan)
        print('PLAN OK ' + path if not bad else 'PLAN FAIL ' + path); [print('  -', b) for b in bad]
        sys.exit(1 if bad else 0)
    if cmd == 'approve':
        words = sys.argv[sys.argv.index('--words') + 1]; when = sys.argv[sys.argv.index('--when') + 1]
        bad = problems(plan, approval=False)
        if bad: print('cannot approve, the plan itself has problems:'); [print('  -', b) for b in bad]; sys.exit(1)
        plan['approval'] = {'words': words, 'when': when, 'sha': sha(plan)}
        json.dump(plan, open(path, 'w'), indent=1, ensure_ascii=False); print('approved', path, plan['approval']['sha'])
        os.makedirs('art/gen/plans', exist_ok=True)                   # every approval in one log, for the audit
        open('art/gen/plans/approvals.log', 'a').write(f"{when}\t{plan['name']}\t{plan['approval']['sha']}\t{words}\n")
    elif cmd == 'template':
        print(template(plan))
    elif cmd == 'page':
        open(sys.argv[3], 'w').write(page(plan)); print(sys.argv[3])


if __name__ == '__main__':
    main()
