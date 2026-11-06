#!/usr/bin/env python3
"""tools/check_approved.py [BASE]: owner decisions that are not in the branch being built.

Why (owner, 6 Nov): the 6 Nov preview showed bikes behind the flower boxes and the old speech panel, though the
owner had decided both on 24-25 Oct. The fixes sat on side branches (play/bikes-front, ui/hud-v8) that no later
integration took in, so every new build lost them again. Run this before building any preview or integration.

It lists every commit on any remote branch whose subject carries "(owner," (the repo's mark for a change the
owner asked for or approved) and whose change is not in BASE (default HEAD; cherry-picks count as in).
Branches or commits left out on purpose go in docs/not_merged.txt, one per line: a branch name, or a short
commit hash, then " # why". Exit 1 if anything is missing.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'

def git(*a):
    return subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True).stdout

skip = set()
p = os.path.join(ROOT, 'docs', 'not_merged.txt')
if os.path.exists(p):
    for line in open(p):
        t = line.split('#')[0].strip()
        if t: skip.add(t)

if git('rev-parse', '--is-shallow-repository').strip() == 'true':
    print('note: shallow clone; fetch with --depth=500 or more so old branches are compared correctly')

missing = {}
for ref in git('for-each-ref', '--format=%(refname:short)', 'refs/remotes').split():
    br = ref.split('/', 1)[1] if '/' in ref else ref
    if br in skip or br == 'HEAD':
        continue
    # commits on the branch whose change is not in base (git's patch-id match counts cherry-picks as in)
    out = git('log', '--cherry-pick', '--right-only', '--no-merges', '--format=%h\t%s', f'{base}...{ref}')
    for line in out.splitlines():
        h, s = line.split('\t', 1)
        if '(owner,' in s and h not in skip:
            missing.setdefault(br, []).append((h, s))

# a commit can sit on several branches: report it once, under the first branch that has it
seen, n = set(), 0
for br in sorted(missing):
    rows = [(h, s) for h, s in missing[br] if h not in seen]
    if not rows:
        continue
    print(f'{br}:')
    for h, s in rows:
        print(f'  {h} {s}'); seen.add(h); n += 1
print(f'APPROVED NOT MERGED: {n}' if n else 'APPROVED ALL MERGED')
sys.exit(1 if n else 0)
