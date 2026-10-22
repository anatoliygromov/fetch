#!/usr/bin/env python3
"""Whole-game mode of the playtest lab: a persona plays the levels of an order as one playthrough.

  python3 tools/run_campaign.py --order riverwalk,citypark,downtown,rooftops,soder,night [--seeds 20] [--jobs N]
                                [--out /home/claude/out/r6-lab/campaign] [--personas a,b]

What carries from one level to the next (docs/playtest/method.md, "Whole-game mode"):
- lives and score, as in the real flow: a cleared level hands its lives and its tally score (with the time bonus) to
  the next level (St.new(def, { score, lives })). GAME OVER inside a level follows the real rule: TRY AGAIN restarts
  that level with 3 lives and the score it started with (the bot does this, pt_bot.lua).
- the controls: a control found (by trying, or read in a hint) is known for the rest of the playthrough; its trying
  time is paid once. A control whose button glyph was on screen in a hint but is not known yet: trying is halved.
- a level the persona does not clear (quit, session time, or a run the lab lost) still ends; the playthrough goes on
  at the next level as LEVEL SELECT starts a run (3 lives, score 0), as if a helper got them past it. Its metrics
  say so (fresh_start). The FETCH FRENZY bonus round is not played (no extra lives from it).
Each level run is one LOVE process (tools/pt_common.py) with --carry and the clean run's route map (--route).
Results: <out>/runs/<pid>__<seed>__<k>_<level>.json, one per level of each playthrough; skipped if already there.
"""
import argparse, json, os, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt_common import run_one, ensure_perfect, perfect_file, personas as load_personas, rooftops_route


def level_seed(seed, k):
    return seed * 100 + k


def playthrough(job):
    order, pid, persona, seed, out = job
    runs = os.path.join(out, "runs"); perf = os.path.join(out, "perfect")
    carry = {"lives": 3, "score": 0, "known": {}, "seen": {}}
    results = []
    for k, lv in enumerate(order, 1):
        f = os.path.join(runs, f"{pid}__{seed}__{k}_{lv}.json")
        road = rooftops_route(persona, lv, seed)
        d = None
        if os.path.exists(f):
            try:
                d = json.load(open(f))
            except Exception:
                d = None
        if d is None:
            fd, cf = tempfile.mkstemp(prefix="pt_carry_", suffix=".json"); os.close(fd)
            json.dump(carry, open(cf, "w"))
            try:
                d = run_one(lv, pid, level_seed(seed, k), f, route=road,
                            route_file=perfect_file(perf, lv, road if lv == "rooftops" else None), carry_file=cf)
            finally:
                os.remove(cf)
            if d is None:
                d = {"persona": pid, "level": lv, "result": "crash", "fails": [], "discover": []}
            d.update(order=order, k=k, playthrough_seed=seed, carry_in_full=carry)
            json.dump(d, open(f, "w"))
        results.append(d)
        co = d.get("carry_out") or {}
        known = co.get("known") if isinstance(co.get("known"), dict) else {}
        seen = co.get("seen") if isinstance(co.get("seen"), dict) else {}
        carry = {"known": {**carry["known"], **known}, "seen": {m: v for m, v in {**carry["seen"], **seen}.items() if m not in known}}
        if d.get("result") == "clear" and co.get("lives"):
            carry.update(lives=co["lives"], score=co.get("score", 0), fresh=False)
        else:                                            # not cleared: on at the next level, as LEVEL SELECT starts it
            carry.update(lives=3, score=0, fresh=True)
    return pid, seed, results


def run_campaign(order, out, seeds=20, jobs=None, pids=None, progress=True):
    os.makedirs(os.path.join(out, "runs"), exist_ok=True)
    perf = os.path.join(out, "perfect")
    plist = [p for p in load_personas() if not pids or p["id"] in pids]
    pj = []
    for lv in dict.fromkeys(order):
        for road in (["low", "high"] if lv == "rooftops" else [None]):
            pj.append((lv, road))
    jobs = jobs or max(2, (os.cpu_count() or 2) + 1)
    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(lambda a: ensure_perfect(perf, *a), pj))
    work = [(order, p["id"], p, s, out) for s in range(1, seeds + 1) for p in plist]
    t0 = time.time(); n = 0; done = []
    with ThreadPoolExecutor(jobs) as ex:
        for r in ex.map(playthrough, work):
            done.append(r); n += 1
            if progress and n % 16 == 0:
                print(f"  {n}/{len(work)} playthroughs, {time.time() - t0:.0f} s", flush=True)
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--out", default="/home/claude/out/r6-lab/campaign")
    ap.add_argument("--personas", default="")
    a = ap.parse_args()
    order = a.order.split(",")
    run_campaign(order, a.out, a.seeds, a.jobs, a.personas.split(",") if a.personas else None)
    print("done:", a.out)


if __name__ == "__main__":
    main()
