"""Shared bits of the playtest lab's Python side (tools/run_playtest.py, tools/run_campaign.py, tools/check_curve.py):
running one LOVE process for one persona on one level, the personas, and the beats (screens) of each level.

One run = `love riverwalk --level <lv> --auto --playtest <persona> --seed <n> --out <json>` with its own
XDG_DATA_HOME (a fresh temp dir), SDL_AUDIODRIVER=dummy, under xvfb-run -a. --route gives the clean run's route map
(recovery v2); --carry gives lives, score and the controls known from the levels before (whole-game mode).
"""
import json, os, re, shutil, subprocess, tempfile, time, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"citypark": "City Park", "citypark_tall": "City Park (tall)", "riverwalk": "River Walk", "downtown": "Downtown",
         "downtown_tall": "Downtown (tall)", "rooftops": "Rooftops", "soder": "Soder Hill", "night": "Night Harbour"}


def personas():
    return json.load(open(os.path.join(ROOT, "docs/playtest/personas.json")))["personas"]


def rooftops_route(persona, level, seed):
    """Rooftops has two roads: the high one with the persona's explore chance (never when rush), from the seed."""
    if level != "rooftops":
        return None
    if persona.get("rush"):
        return "low"
    r = random.Random(f"{persona['id']}-{seed}").random()
    return "high" if r < persona.get("explore", 0) else "low"


def run_one(level, pid, seed, out, route=None, route_file=None, carry_file=None, timeout=600):
    """One headless run; returns the result dict (or None if the run wrote nothing)."""
    env = dict(os.environ)
    tmp = tempfile.mkdtemp(prefix="pt_xdg_")
    env.update(XDG_DATA_HOME=tmp, SDL_AUDIODRIVER="dummy")
    if route == "high":
        env["AUTO_ROUTE"] = "high"
    else:
        env.pop("AUTO_ROUTE", None)
    cmd = ["timeout", str(timeout), "xvfb-run", "-a", "love", "riverwalk", "--level", level, "--auto",
           "--playtest", pid, "--seed", str(seed), "--out", out]
    if route_file and os.path.exists(route_file):
        cmd += ["--route", route_file]
    if carry_file:
        cmd += ["--carry", carry_file]
    try:
        subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.exists(out):
        return None
    d = json.load(open(out))
    if route:                                   # the Rooftops road (perfect runs keep their route map in "route")
        d["road"] = route
        if d.get("persona") != "perfect":
            d["route"] = route
        json.dump(d, open(out, "w"))
    return d


def perfect_file(dirpath, level, route=None):
    return os.path.join(dirpath, f"{level}{'_' + route if route else ''}__perfect__1.json")


def ensure_perfect(dirpath, level, route=None):
    """The clean run of a level (and road): its clear time and its route map. Run once, kept on disk."""
    os.makedirs(dirpath, exist_ok=True)
    f = perfect_file(dirpath, level, route)
    if not os.path.exists(f):
        run_one(level, "perfect", 1, f, route=route)
    return f


# ---- beats: the screens of each level, from its beat sheet (x ranges); else "screen N" (320 px)
def _beats(level):
    path = os.path.join(ROOT, "docs", f"{level}_beatsheet.md")
    out = []
    if os.path.exists(path):
        for line in open(path):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or not cells[0].isdigit():
                continue
            m = re.search(r"\((\d+)\s*-\s*(\d+)\)", cells[1])
            if m:
                name = re.sub(r"\s*\(.*", "", cells[1]).strip("* ")
                out.append((int(m.group(1)), int(m.group(2)), f"{cells[0]} {name}"))
            elif cells[1].isdigit():
                x0 = int(cells[1]); out.append((x0, x0 + 320, f"{cells[0]} {cells[2].strip('* ')}"))
        seen, uniq = set(), []
        for b in out:
            if b[2].split()[0] in seen:
                break
            seen.add(b[2].split()[0]); uniq.append(b)
        out = uniq
    return out


_BEATS = {}


def beat_name(level, x):
    if level not in _BEATS:
        _BEATS[level] = _beats(level)
    for x0, x1, n in _BEATS[level]:
        if x0 <= x < x1:
            return n
    return f"screen {int(x // 320) + 1}"
