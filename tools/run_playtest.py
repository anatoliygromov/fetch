#!/usr/bin/env python3
"""Runs the playtest lab: every persona x level x seed, in parallel (one LOVE process per run, each with its own
XDG_DATA_HOME, SDL_AUDIODRIVER=dummy, under xvfb-run -a). Results: one JSON per run in <out>/runs/.

  python3 tools/run_playtest.py [--seeds 20] [--jobs N] [--out /home/claude/out/r4-playtest] [--levels a,b] [--personas a,b]
                                [--recovery v2|v1]

The clean (perfect) runs go first: each one records its route map, and the persona runs get it (--route) for
recovery v2 (docs/playtest/method.md). --recovery v1 runs the bot as on 22 Oct (no route map).

Rooftops has two roads: each run picks the high road with the persona's `explore` chance (never when `rush`),
from the seed, and passes it on as AUTO_ROUTE=high (the autopilot's own switch). Runs already on disk are skipped.
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt_common import ROOT, run_one, rooftops_route as route_for, perfect_file

LEVELS = ["citypark", "citypark_tall", "riverwalk", "downtown", "downtown_tall", "rooftops", "soder", "night"]


def one(job):
    level, pid, seed, route, out, route_file = job
    if os.path.exists(out):
        return out, 0.0
    t0 = time.time()
    run_one(level, pid, seed, out, route=route, route_file=route_file)
    return out, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--out", default="/home/claude/out/r4-playtest")
    ap.add_argument("--levels", default=",".join(LEVELS))
    ap.add_argument("--personas", default="")
    ap.add_argument("--recovery", default="v2", help="v2 (route map from the clean run) or v1 (the 22 Oct bot)")
    a = ap.parse_args()
    from pt_common import personas as load_personas
    personas = load_personas()
    if a.personas:
        personas = [p for p in personas if p["id"] in a.personas.split(",")]
    runs = os.path.join(a.out, "runs"); os.makedirs(runs, exist_ok=True)
    pjobs = []                                            # the clean runs first (both rooftops roads): their route maps
    for lv in a.levels.split(","):
        for route in (["low", "high"] if lv == "rooftops" else [None]):
            pjobs.append((lv, "perfect", 1, route, perfect_file(runs, lv, route), None))
    with ThreadPoolExecutor(a.jobs) as ex:
        list(ex.map(one, pjobs))
    jobs = []
    for seed in range(1, a.seeds + 1):                    # seed by seed, so a cut run still covers everything
        for lv in a.levels.split(","):
            for p in personas:
                route = route_for(p, lv, seed)
                rf = None if a.recovery == "v1" else perfect_file(runs, lv, route if lv == "rooftops" else None)
                jobs.append((lv, p["id"], seed, route, os.path.join(runs, f"{lv}__{p['id']}__{seed}.json"), rf))
    t0 = time.time(); n = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for out, dt in ex.map(one, jobs):
            n += 1
            if n % 50 == 0:
                print(f"{n}/{len(jobs)} runs, {time.time() - t0:.0f} s", flush=True)
    print(f"done: {n} runs in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
