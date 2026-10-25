#!/usr/bin/env python3
"""ledger.py: every credit, in one file (art/gen/ledger.csv). docs/WORKFLOW.md, BIBLE 7.

  ledger.py plan JOB ASSET FAMILY TOOL MODEL CREDITS [--note TEXT]   a planned paid job (preflight writes this)
  ledger.py spent JOB CREDITS [--note TEXT]                          after the tool charged (the real figure)
  ledger.py verdict ASSET in_game|reference|rejected|pending [--note TEXT]
  ledger.py today [TOOL]                                             credits spent today (Europe/Stockholm)
  ledger.py jobs ASSET                                               paid jobs so far for an asset
  ledger.py report [--since YYYY-MM-DD]                              yield per tool and per family

Yield = credits on assets marked in_game / credits spent. Rows are never deleted; a correction is a new row."""
import sys, csv, os, datetime as dt
from zoneinfo import ZoneInfo

F = 'art/gen/ledger.csv'
COLS = ['time', 'kind', 'job', 'asset', 'family', 'tool', 'model', 'credits', 'status', 'note']
TZ = ZoneInfo('Europe/Stockholm')


def rows():
    if not os.path.exists(F): return []
    return list(csv.DictReader(open(F)))


def add(**r):
    new = not os.path.exists(F)
    os.makedirs(os.path.dirname(F), exist_ok=True)
    with open(F, 'a', newline='') as fh:
        w = csv.DictWriter(fh, COLS)
        if new: w.writeheader()
        r.setdefault('time', dt.datetime.now(TZ).strftime('%Y-%m-%d %H:%M'))
        w.writerow({k: r.get(k, '') for k in COLS})


def opt(name, default=''):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def spent_rows(rs=None):
    rs = rs if rs is not None else rows()
    planned = {r['job']: r for r in rs if r['kind'] == 'plan'}
    out = []
    for r in rs:
        if r['kind'] == 'spent':
            p = planned.get(r['job'], {})
            out.append(dict(p, **{k: v for k, v in r.items() if v}))
    return out


def verdicts(rs=None):
    v = {}
    for r in rs if rs is not None else rows():
        if r['kind'] == 'verdict': v[r['asset']] = r['status']
    return v


def today(tool=None):
    d = dt.datetime.now(TZ).strftime('%Y-%m-%d')
    return sum(int(r['credits'] or 0) for r in spent_rows() if r['time'].startswith(d) and (not tool or r.get('tool') == tool))


def jobs(asset):
    return len([r for r in spent_rows() if r.get('asset') == asset])


def report(since=''):
    rs = rows(); v = verdicts(rs); S = [r for r in spent_rows(rs) if r['time'] >= since]
    def table(key):
        agg = {}
        for r in S:
            k = r.get(key) or '-'; a = agg.setdefault(k, [0, 0, 0, 0])
            c = int(r['credits'] or 0); st = v.get(r.get('asset'), 'pending')
            a[0] += c; a[1] += c if st == 'in_game' else 0; a[2] += c if st == 'reference' else 0
            a[3] += c if st == 'rejected' else 0
        print(f"\n{key:<14}{'spent':>8}{'in game':>9}{'ref':>7}{'wasted':>8}{'yield':>7}")
        for k, (s, g, rf, w) in sorted(agg.items()):
            print(f"{k:<14}{s:>8}{g:>9}{rf:>7}{w:>8}{(g / s if s else 0):>7.0%}")
    print(f'Ledger report since {since or "the start"} ({len(S)} paid jobs)'); table('tool'); table('family')


if __name__ == '__main__':
    a = sys.argv[1:] or ['report']
    if a[0] == 'plan':
        add(kind='plan', job=a[1], asset=a[2], family=a[3], tool=a[4], model=a[5], credits=a[6], status='planned', note=opt('--note'))
    elif a[0] == 'spent':
        add(kind='spent', job=a[1], credits=a[2], status='spent', note=opt('--note'))
    elif a[0] == 'verdict':
        assert a[2] in ('in_game', 'reference', 'rejected', 'pending'), 'verdict: in_game|reference|rejected|pending'
        add(kind='verdict', asset=a[1], status=a[2], note=opt('--note'))
    elif a[0] == 'today':
        print(today(a[1] if len(a) > 1 else None))
    elif a[0] == 'jobs':
        print(jobs(a[1]))
    elif a[0] == 'report':
        report(opt('--since'))
    else:
        print(__doc__); sys.exit(2)
