#!/usr/bin/env python3
"""check_lab_runup.py: the playtest lab's run-up stays on its floor (night/25oct-lab, 26 Oct 2026).

City Park tall, persona liam8, playthrough seed 3 (level seed 302), carrying River Walk's lives, score and controls:
a short jump at x 1817 drops Pepper to the low road; the lab puts her back on the ash branch (x 1901, y 200). Its
recovery used to walk a 32 px run-up back to x 1867, past the branch's left end (x 1888), so she stepped off onto the
ledge below, ran off that and landed on the low road at x 1987 again, every retry, until the run was "lost" (14 of
160 City Park runs at 20 seeds, curve T4 FAIL). pt_bot.lua now stops the run-up at the floor's edge.
This replays that run and passes when it clears. About a minute; needs LOVE (headless: xvfb-run).
Run from the repo root: python3 tools/check_lab_runup.py"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt_common import run_one, ensure_perfect

tmp = tempfile.mkdtemp(prefix="lab_runup_")
route = ensure_perfect(tmp, "citypark_tall")                    # the clean run and its route map
carry = os.path.join(tmp, "carry.json")
json.dump({"known": {"act": True, "crawl": True, "heldjump": True}, "seen": {}, "lives": 3, "score": 12770,
           "fresh": False}, open(carry, "w"))
d = run_one("citypark_tall", "liam8", 302, os.path.join(tmp, "liam8.json"), route_file=route, carry_file=carry)
if not d:
    print("LAB RUN-UP: no result (the run crashed)"); sys.exit(1)
fails = [(f["spot"], f["cause"], f["x"], f["y"]) for f in d.get("fails", [])]
ok = d.get("result") == "clear"
print(f"LAB RUN-UP {'OK' if ok else 'FAIL'}: {d.get('result')} in {d.get('play_time', 0):.1f} s, fails {fails}")
sys.exit(0 if ok else 1)
