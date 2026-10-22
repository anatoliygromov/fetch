#!/usr/bin/env python3
"""Runs the playtest lab: every persona x level x seed, in parallel (one LOVE process per run, each with its own
XDG_DATA_HOME, SDL_AUDIODRIVER=dummy, under xvfb-run -a). Results: one JSON per run in <out>/runs/.

  python3 tools/run_playtest.py [--seeds 20] [--jobs N] [--out /home/claude/out/r4-playtest] [--levels a,b] [--personas a,b]

Rooftops has two roads: each run picks the high road with the persona's `explore` chance (never when `rush`),
from the seed, and passes it on as AUTO_ROUTE=high (the autopilot's own switch). Runs already on disk are skipped.
"""
import argparse, json, os, random, shutil, subprocess, tempfile, time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVELS = ["citypark", "citypark_tall", "riverwalk", "downtown", "downtown_tall", "rooftops", "soder", "night"]


def route_for(persona, level, seed):
    if level != "rooftops":
        return None
    if persona.get("rush"):
        return "low"
    r = random.Random(f"{persona['id']}-{seed}").random()
    return "high" if r < persona.get("explore", 0) else "low"


def one(job):
    level, pid, seed, route, out = job
    if os.path.exists(out):
        return out, 0.0
    env = dict(os.environ)
    tmp = tempfile.mkdtemp(prefix="pt_xdg_")
    env.update(XDG_DATA_HOME=tmp, SDL_AUDIODRIVER="dummy")
    if route == "high":
        env["AUTO_ROUTE"] = "high"
    else:
        env.pop("AUTO_ROUTE", None)
    t0 = time.time()
    try:
        subprocess.run(["timeout", "600", "xvfb-run", "-a", "love", "riverwalk", "--level", level, "--auto",
                        "--playtest", pid, "--seed", str(seed), "--out", out],
                       cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if os.path.exists(out) and route:
        d = json.load(open(out)); d["route"] = route; json.dump(d, open(out, "w"))
    return out, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--out", default="/home/claude/out/r4-playtest")
    ap.add_argument("--levels", default=",".join(LEVELS))
    ap.add_argument("--personas", default="")
    a = ap.parse_args()
    personas = json.load(open(os.path.join(ROOT, "docs/playtest/personas.json")))["personas"]
    if a.personas:
        personas = [p for p in personas if p["id"] in a.personas.split(",")]
    runs = os.path.join(a.out, "runs"); os.makedirs(runs, exist_ok=True)
    jobs = []
    for lv in a.levels.split(","):                        # the clean baselines first (both rooftops roads)
        for route in (["low", "high"] if lv == "rooftops" else [None]):
            jobs.append((lv, "perfect", 1, route, os.path.join(runs, f"{lv}{'_' + route if route else ''}__perfect__1.json")))
    for seed in range(1, a.seeds + 1):                    # seed by seed, so a cut run still covers everything
        for lv in a.levels.split(","):
            for p in personas:
                jobs.append((lv, p["id"], seed, route_for(p, lv, seed), os.path.join(runs, f"{lv}__{p['id']}__{seed}.json")))
    t0 = time.time(); n = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for out, dt in ex.map(one, jobs):
            n += 1
            if n % 50 == 0:
                print(f"{n}/{len(jobs)} runs, {time.time() - t0:.0f} s", flush=True)
    print(f"done: {n} runs in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
