#!/usr/bin/env python3
"""pipeline.py: the asset workflow as a state machine (docs/WORKFLOW.md). A step is refused until the step before it
is done AND its proof exists, so nothing reaches the owner half made.

  pipeline.py status [--family F]                     every asset, its last step, what is next, what blocks it
  pipeline.py new NAME                                start an asset from its spec art/gen/jobs/NAME.json
  pipeline.py done NAME STEP [--render P] [--frame P] [--aseprite P] [--none REASON] [--board TEXT] [--build P]

Steps (tier A and B): spec, blockout, preflight, probe, cut, ingame, polish, review, board, shipped
Steps (tier C, built): spec, built, ingame, review, board, shipped
Proof per step:
  spec       jobs/NAME.json with level, layer, kind, tier, family, slot {file, where}, target_px
  blockout   blockouts/NAME.png and NAME_mask.png
  preflight  prompts/NAME.job.json newer than the spec (tools/preflight.py passed)
  probe      a ledger 'spent' row for the asset and --render (the render file, kept in art/gen/renders/)
  cut        out/NAME.cut.json with no fails (tools/grid_cut.py)
  ingame     --frame: a game frame with the asset in place (colour; greyscale is made from it), newer than the cut
  polish     --aseprite: the .aseprite source, newer than the cut, plus its exported png at the slot size;
             tier B only: --none REASON when the review flagged nothing to polish
  review     art/gen/reviews/NAME.md: 'Reviewer:' line (not the maker), all 9 checklist items PASS (rules.json)
  board      --board "approve ..." copied from the Art Review board decision (the owner's approve)
  shipped    the slot file exists in the game; writes the ledger verdict in_game
  built      --build: the script that builds it, and the slot file exists"""
import sys, os, json, re, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger

R = json.load(open('art/gen/rules.json'))
G = 'art/gen'; ST = f'{G}/status'
os.makedirs(ST, exist_ok=True)


def opt(n):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else None


def load(n):
    p = f'{ST}/{n}.json'
    if not os.path.exists(p): sys.exit(f'{n}: not started (pipeline.py new {n})')
    return json.load(open(p))


def save(s): json.dump(s, open(f"{ST}/{s['name']}.json", 'w'), indent=1)


def newer(a, b): return os.path.exists(a) and (not os.path.exists(b) or os.path.getmtime(a) >= os.path.getmtime(b))


def proof(s, step):
    n = s['name']; J = json.load(open(f'{G}/jobs/{n}.json')); bad = []; ev = {}
    if step == 'spec':
        for f in ('level', 'layer', 'kind', 'tier', 'family', 'slot', 'target_px'):
            if not J.get(f): bad.append(f'spec field {f} missing')
        if J.get('slot') and not (J['slot'].get('file') and J['slot'].get('where')): bad.append('slot needs file and where')
    elif step == 'blockout':
        for f in (f'{G}/blockouts/{n}.png', f'{G}/blockouts/{n}_mask.png'):
            if not os.path.exists(f): bad.append(f'{f} missing')
    elif step == 'preflight':
        if not newer(f'{G}/prompts/{n}.job.json', f'{G}/jobs/{n}.json'): bad.append('no preflight pass newer than the spec')
    elif step == 'probe':
        if not any(r.get('asset') == n for r in ledger.spent_rows()): bad.append('no ledger spent row (tools/ledger.py spent JOB CREDITS)')
        r = opt('--render')
        if not r or not os.path.exists(r): bad.append('--render: the render file')
        ev['render'] = r
    elif step == 'cut':
        p = f'{G}/out/{n}.cut.json'
        if not os.path.exists(p): bad.append('no cut (tools/grid_cut.py)')
        elif json.load(open(p))['fails']: bad.append(f"cut failed: {json.load(open(p))['fails']}")
    elif step == 'ingame':
        f = opt('--frame'); ref = f'{G}/out/{n}.cut.json' if s['tier'] != 'C' else J['slot']['file']
        if not f or not newer(f, ref): bad.append('--frame: an in-game frame made after the cut')
        ev['frame'] = f
    elif step == 'polish':
        a = opt('--aseprite'); none = opt('--none')
        if none and s['tier'] == 'B': ev['none'] = none
        elif not a or not a.endswith('.aseprite') or not newer(a, f'{G}/out/{n}.cut.json'):
            bad.append('--aseprite: the .aseprite source saved after the cut' + (' (tier B: or --none REASON)' if s['tier'] == 'B' else ''))
        else: ev['aseprite'] = a
    elif step == 'review':
        p = f'{G}/reviews/{n}.md'
        if not os.path.exists(p): bad.append(f'{p} missing (independent reviewer, 9 items)')
        else:
            t = open(p).read(); m = re.search(r'^Reviewer:\s*(.+)$', t, re.M)
            if not m or 'maker' in m.group(1).lower(): bad.append("'Reviewer:' line missing or the maker")
            items = re.findall(r'^\s*([1-9])\.\s.*?\b(PASS|FAIL)\b', t, re.M)
            got = {int(i): v for i, v in items}
            miss = [i for i in range(1, len(R['review_checklist']) + 1) if i not in got]
            if miss: bad.append(f'checklist items not answered: {miss}')
            fails = [i for i, v in got.items() if v == 'FAIL']
            if fails: bad.append(f'checklist FAIL on {fails}: fix and review again')
    elif step == 'board':
        b = opt('--board')
        if not b or not b.lower().startswith('approve'): bad.append("--board 'approve ...': the owner's decision from the board")
        ev['board'] = b
    elif step == 'shipped':
        if not os.path.exists(J['slot']['file']): bad.append(f"{J['slot']['file']} not in the game")
    elif step == 'built':
        b = opt('--build')
        if not b or not os.path.exists(b): bad.append('--build: the build script')
        if not os.path.exists(J['slot']['file']): bad.append(f"{J['slot']['file']} missing")
        ev['build'] = b
    return bad, ev


def nxt(s):
    steps = R['steps'][s['tier']]; done = [x for x in steps if x in s['steps']]
    return steps[len(done)] if len(done) < len(steps) else None


def cmd_new(n):
    J = json.load(open(f'{G}/jobs/{n}.json'))
    if J.get('tier') not in R['steps']: sys.exit('spec needs tier A, B or C')
    s = {'name': n, 'family': J.get('family'), 'tier': J['tier'], 'steps': {}}
    save(s); print(f'{n}: started, tier {s["tier"]}, family {s["family"]}; next: spec')


def cmd_done(n, step):
    s = load(n); want = nxt(s)
    if step != want: sys.exit(f'REFUSED {n} {step}: next step is {want}')
    bad, ev = proof(s, step)
    if bad:
        print(f'REFUSED {n} {step}:'); [print('  -', b) for b in bad]; sys.exit(1)
    s['steps'][step] = dict(ev, time=dt.datetime.now().strftime('%Y-%m-%d %H:%M')); save(s)
    if step == 'shipped': ledger.add(kind='verdict', asset=n, status='in_game', note='pipeline shipped')
    print(f'{n}: {step} done; next: {nxt(s) or "nothing, it is in the game"}')


def cmd_status(fam=None):
    rows = [json.load(open(f'{ST}/{f}')) for f in sorted(os.listdir(ST)) if f.endswith('.json')]
    rows = [r for r in rows if not fam or r['family'] == fam]
    print(f"{'asset':<28}{'family':<16}{'tier':<6}{'last done':<12}{'next':<12}blocker")
    for s in rows:
        last = [x for x in R['steps'][s['tier']] if x in s['steps']]
        n = nxt(s); blk = ''
        if n:
            bad, _ = proof(s, n) if n not in ('probe', 'ingame', 'polish', 'board', 'built') else ([], {})
            blk = '; '.join(bad)[:70] if bad else ('owner: board' if n == 'board' else 'ready')
        print(f"{s['name']:<28}{s['family'] or '-':<16}{s['tier']:<6}{(last[-1] if last else '-'):<12}{n or 'shipped':<12}{blk}")
    if not rows: print('(no assets in the pipeline)')


if __name__ == '__main__':
    a = sys.argv[1:] or ['status']
    if a[0] == 'status': cmd_status(opt('--family'))
    elif a[0] == 'new': cmd_new(a[1])
    elif a[0] == 'done': cmd_done(a[1], a[2])
    else: print(__doc__); sys.exit(2)
