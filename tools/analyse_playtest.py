#!/usr/bin/env python3
"""Playtest lab analysis (docs/playtest/method.md).

  analyse_playtest.py plan   OUT   print the replay commands that capture the frames (one per line, love args)
  analyse_playtest.py report OUT   results.json, summary.md, method.md (copied), timeline_<level>.png,
                                   frames_<level>.png, fail_<level>_<n>.png

OUT holds runs/ (one JSON per run, from riverwalk/playtest.lua) and caps/ (the captured frames).
Everything here is computed from the run files; nothing is typed in by hand.
"""
import glob
import json
import os
import shutil
import statistics as st
import sys
from collections import Counter, defaultdict

LEVELS = ["citypark", "downtown", "riverwalk"]
LEVEL_NAME = {"citypark": "1 City Park", "downtown": "2 Downtown", "riverwalk": "3 River Walk"}
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PERSONAS = json.load(open(os.path.join(REPO, "docs/playtest/personas.json")))["personas"]
PIDS = [p["id"] for p in PERSONAS]
PBY = {p["id"]: p for p in PERSONAS}
HAZARD_SPEED = {"cart": 100, "tram": 110, "bike": 115}
# the events that count for pacing (something happens on screen)
PACE = {"bone", "checkpoint", "hint", "hazard", "magpie_flee", "magpie_drop", "cat_scared", "ball_pickup", "girl_given",
        "scramble", "heart_lost", "mech_use", "ball_home"}
# what a text teaches: the same table as riverwalk/pt_bot.lua
TEACH = [("HOLD A", "held"), ("HOLD B", "walk"), ("BARK", "bark"), ("CRAWL", "crawl"), ("X:", "act"), ("PICK UP", "act"),
         ("RIDE THE DUCK BOAT", "ride"), ("RIDE THE PONTOON", "ride"), ("LEAF CART", "hazard"), ("TRAM!", "hazard"),
         ("BIKES!", "hazard"), ("PUSH TO CLIMB", "scramble")]
OPTIONAL = {"oak", "frame", "parasols", "shop sign", "awning", "awning 2", "statue", "statue hat"}   # optional detours (bones)
MECH_NAME = {"held": "held jump (hold A)", "walk": "sneak / walk (hold B)", "crawl": "crawl (Down)", "bark": "bark (Y)",
             "act": "pick up / give (X)", "scramble": "ledge scramble", "ride": "ride a moving platform",
             "hazard": "wait out a hazard on a perch"}


def pct(x):
    return f"{100 * x:.0f}%"


def med(xs, d=0):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return round(st.median(xs), d) if d else round(st.median(xs))


def q(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def words(s):
    return len(s.split())


def load(out):
    runs, auto = [], {}
    for f in sorted(glob.glob(os.path.join(out, "runs", "*.json"))):
        try:
            d = json.load(open(f))
        except Exception as e:
            print("unreadable run file", f, e, file=sys.stderr)
            continue
        d["file"] = os.path.basename(f)
        if d.get("persona") == "autopilot":
            auto[d["level"]] = d
        else:
            d["events"] = sorted(d["events"], key=lambda e: (e["t"], e["step"]))
            runs.append(d)
    return runs, auto


def sel(runs, level, persona=None, mode="campaign"):
    return [r for r in runs if r["level"] == level and r["mode"] == mode and (persona is None or r["persona"] == persona)]


# ---------------------------------------------------------------- metrics
def run_metrics(r):
    ev = r["events"]
    idle = Counter()
    for e in ev:
        if e["type"] == "idle":
            why = e.get("why") or "idle"
            if why.startswith("waiting"):
                why = "waiting for " + why.split(":")[1].strip()
            idle[why] += e["dur"]
    hearts = [e for e in ev if e["type"] == "heart_lost"]
    m = {"idle": dict(idle), "idle_total": sum(idle.values()), "hearts": hearts}
    if r["level"] == "citypark":
        drop = next((e for e in ev if e["type"] == "magpie_drop"), None)
        m["magpie_t"] = drop["t"] if drop else None
        m["magpie_perch"] = drop.get("perch") if drop else None
        m["magpie_flees"] = sum(1 for e in ev if e["type"] == "magpie_flee")
    if r["level"] == "downtown":
        seen = next((e for e in ev if e["type"] == "hint" and "CAT" in e["text"]), None)
        cat = next((e for e in ev if e["type"] == "cat_scared"), None)
        pick = next((e for e in ev if e["type"] == "ball_pickup"), None)
        m["cat_t"] = (cat["t"] - seen["t"]) if (cat and seen) else None
        m["cat_pick_t"] = (pick["t"] - seen["t"]) if (pick and seen) else None
    return m


def longest_gap(ev, end):
    ts = [0.0] + sorted(e["t"] for e in ev if e["type"] in PACE) + [end]
    best, at = 0, 0
    for a, b in zip(ts, ts[1:]):
        if b - a > best:
            best, at = b - a, a
    return best, at


def per_bin(ev, end, size=10):
    n = int(end // size) + 1
    bins = [0] * n
    for e in ev:
        if e["type"] in PACE and e["t"] <= end:
            bins[min(n - 1, int(e["t"] // size))] += 1
    return bins


def grid_cell(rs):
    clears = [r for r in rs if r["result"] == "clear"]
    hearts = [r["hearts_lost"] for r in rs]
    out = {
        "runs": len(rs), "clears": len(clears), "completion": len(clears) / len(rs) if rs else 0,
        "play_median": med([r["play_time"] for r in clears], 1), "play_p25": q([r["play_time"] for r in clears], .25),
        "play_p75": q([r["play_time"] for r in clears], .75),
        "total_median": med([r["total_time"] for r in clears], 1),
        "cards_median": med([r["card_time"] + r["story_card_est"] for r in rs], 1),
        "approx_mean": round(st.mean([r["approx_time"] for r in rs]), 1),
        "hearts_median": med(hearts, 1), "hearts_mean": round(st.mean(hearts), 2),
        "hearts_max": max(hearts),
        "lives_lost_mean": round(st.mean([r["lives_lost"] for r in rs]), 2),
        "game_overs": sum(r["game_overs"] for r in rs),
        "retries_mean": round(st.mean([r["retries"] for r in rs]), 1), "retries_median": med([r["retries"] for r in rs], 1),
        "bones_pct": st.mean([r["bones"] / r["bones_total"] for r in rs]),
        "bones_pct_clear": st.mean([r["bones"] / r["bones_total"] for r in clears]) if clears else None,
        "gold_mean": round(st.mean([r["gold"] for r in rs]), 2), "gold_total": rs[0]["gold_total"] if rs else 0,
    }
    quits = Counter()
    for r in rs:
        if r["result"] != "clear" and r.get("quit"):
            qi = r["quit"]
            quits[f"{qi['ob']} (screen {qi['screen']}, {qi['cause']})"] += 1
        elif r["result"] != "clear":
            quits[r["result"]] += 1
    out["quits"] = dict(quits)
    fails, causes, places = Counter(), Counter(), Counter()
    for r in rs:
        for k, v in (r["fails"] or {}).items():
            fails[k] += v
        for e in r["events"]:
            if e["type"] == "heart_lost":
                causes[e.get("cause", "?")] += 1
                places[e.get("ob") or f"screen {e['screen']}"] += 1
    out["fails_per_run"] = {k: round(v / len(rs), 2) for k, v in fails.most_common()}
    out["heart_causes"] = dict(causes)
    out["heart_places"] = dict(places.most_common())
    ms = [run_metrics(r) for r in rs]
    idle = Counter()
    for m in ms:
        for k, v in m["idle"].items():
            idle[k] += v
    out["idle_per_run"] = {k: round(v / len(rs), 1) for k, v in idle.most_common()}
    out["idle_total_median"] = med([m["idle_total"] for m in ms], 1)
    # mechanics found by trying
    disc = defaultdict(list)
    druns = defaultdict(set)
    for r in rs:
        for d in r["discoveries"]:
            disc[d["mech"]].append(d.get("dur"))
            druns[d["mech"]].add(r["file"])
    out["discoveries"] = {k: {"runs": len(druns[k]), "median_s": med([x for x in v if x is not None], 1)} for k, v in disc.items()}
    if rs and rs[0]["level"] == "citypark":
        out["magpie_drop_t_median"] = med([m["magpie_t"] for m in ms], 1)
        out["magpie_flees_mean"] = round(st.mean([m["magpie_flees"] for m in ms]), 1)
        out["magpie_drop_perch"] = dict(Counter(m["magpie_perch"] for m in ms))
    if rs and rs[0]["level"] == "downtown":
        out["cat_t_median"] = med([m["cat_t"] for m in ms], 1)
        out["cat_pick_t_median"] = med([m["cat_pick_t"] for m in ms], 1)
    out["longest_gap_median"] = med([longest_gap(r["events"], r["play_time"])[0] for r in rs], 1)
    out["picks"] = dict(Counter(f"{k}:{v}" for r in rs for k, v in (r.get("picks") or {}).items()))
    return out


# where each mechanic is first really needed (from the level files and beat sheets): x, what, and the obstacle names
# the bots use there (pt_routes.lua). "Really needed": the first place where not knowing it stops you.
NEED = {
    "citypark": {"walk": (130, "the magpie on the path (it flees from a running Pepper 110 px off)", ["magpie"]),
                 "bark": (150, "the magpie", ["magpie"]), "act": (233, "the ball, dropped by the magpie", ["ball"]),
                 "crawl": (528, "the hedge (19 px gap; no way over it from the path)", ["hedge"]),
                 "ride": (840, "the duck boat", ["boat"]),
                 "held": (984, "the bin (56 px: held jump + scramble; the 28 px bench also works with a tap + scramble)", ["bin"]),
                 "scramble": (1008, "the bin", ["bin"]), "hazard": (1056, "the leaf cart zone", ["picnic table", "leaf cart"])},
    "downtown": {"crawl": (368, "the cafe tables (or jump onto them)", ["cafe tables"]),
                 "held": (1120, "the pedestal (40 px)", ["pedestal"]), "bark": (1120, "the cat on the statue", ["cat", "pedestal"]),
                 "act": (1180, "the ball under the statue", ["ball"]),
                 "hazard": (1610, "the tram zone", ["kiosk", "shelter", "tram"])},
    "riverwalk": {"held": (641, "the bin (56 px: held jump + scramble)", ["bin"]), "scramble": (641, "the bin", ["bin"]),
                  "hazard": (790, "bike zone 1", ["bikes 1: grit box", "bikes 1: planter", "bikes 1: flower box"]),
                  "ride": (1400, "the pontoon", ["pontoon"]), "act": (1668, "the ball on the wheelhouse", ["ball"]),
                  "crawl": (1936, "the bridge pier", ["bridge"])},
}


def level_hints(level):
    import re
    src = open(os.path.join(REPO, "riverwalk/level", level + ".lua")).read()
    return [m for m in re.findall(r'text = "([^"]+)"', src)]


def teach_table(level, auto, runs):
    """For each mechanic: the first text that teaches it in the clean run (and who can read it), where it is first
    really needed, and how the persona runs did there."""
    ev = auto["events"] if auto else []
    intro = {"citypark": "A MAGPIE STOLE THE GIRL'S BALL! SNEAK UP AND BARK, PEPPER!",
             "downtown": "A CAT IS SITTING ON THE BALL! BARK IT AWAY. BRING THE BALL!",
             "riverwalk": "THE BALL LANDED ON A BOAT. FETCH IT FOR THE GIRL!"}[level]
    taught = {}
    for pat, m in TEACH:
        if pat in intro and m not in taught:
            taught[m] = {"t": 0.0, "x": 60, "text": "intro card: " + intro, "who": "all"}
    for e in ev:
        if e["type"] == "hint":
            for pat, m in TEACH:
                if pat in e["text"] and m not in taught:
                    taught[m] = {"t": e["t"], "x": e["x"], "text": e["text"], "who": "short + all" if words(e["text"]) <= 4 else "all"}
    rs = sel(runs, level)
    rows = []
    for m, (nx, what, obs) in sorted(NEED[level].items(), key=lambda kv: kv[1][0]):
        nt = next((e["t"] for e in ev if e["x"] >= nx - 20), None)
        fail_runs = hurt_runs = 0
        for r in rs:
            if m == "walk":
                bad = any(e["type"] == "magpie_flee" for e in r["events"])
                hurt = False
            else:
                bad = any(e.get("ob") in obs and e["type"] in ("retry", "heart_lost") for e in r["events"])
                hurt = any(e.get("ob") in obs and e["type"] == "heart_lost" for e in r["events"])
            fail_runs += bad
            hurt_runs += hurt
        t = taught.get(m)
        rows.append({"mech": m, "taught": t, "need": {"x": nx, "t": nt, "what": what}, "gap": (nt - t["t"]) if (t and nt is not None) else None,
                     "fail_runs": fail_runs, "hurt_runs": hurt_runs, "runs": len(rs),
                     "fail_label": "runs where the magpie flew off at least once" if m == "walk" else "runs with a retry or heart lost there"})
    return rows


def hints_seen(level, auto, runs):
    rs = sel(runs, level)
    out = []
    for h in level_hints(level):
        clean = any(e["type"] == "hint" and e["text"] == h for e in (auto or {}).get("events", []))
        n = sum(1 for r in rs if any(e["type"] == "hint" and e["text"] == h for e in r["events"]))
        out.append({"text": h, "words": words(h), "clean_run": clean, "persona_runs": n, "runs": len(rs)})
    return out


def hazard_table(level, runs):
    rs = sel(runs, level)
    out = {}
    for r in rs:
        ev = r["events"]
        hz = [e for e in ev if e["type"] == "hazard"]
        if not hz:
            out.setdefault("none", 0)
            out["none"] += 1
            continue
        first = hz[0]
        kind = first["kind"]
        nxt = hz[1]["t"] if len(hz) > 1 else 1e9
        hit = any(e["type"] == "heart_lost" and e.get("cause") == kind and first["t"] <= e["t"] < min(nxt, first["t"] + 8) for e in ev)
        warn = (first["hx"] - first["x"]) / HAZARD_SPEED.get(kind, 110)
        d = out.setdefault(kind, {"runs": 0, "hit_first": 0, "warn": [], "met": 0, "hits_total": 0})
        d["runs"] += 1
        d["hit_first"] += hit
        d["warn"].append(warn)
        d["hits_total"] += sum(1 for e in ev if e["type"] == "heart_lost" and e.get("cause") == kind)
    for k, d in out.items():
        if isinstance(d, dict):
            d["warn_median_s"] = med(d.pop("warn"), 2)
    out["runs"] = len(rs)
    return out


def failure_spots(level, runs):
    """(obstacle -> failures, hearts, quits, runs affected) over the campaign runs of a level"""
    rs = sel(runs, level)
    spots = defaultdict(lambda: {"retries": 0, "hearts": 0, "quits": 0, "runs": set(), "by": Counter(), "causes": Counter()})
    for r in rs:
        for e in r["events"]:
            ob = e.get("ob")
            if not ob:
                continue
            if e["type"] == "retry":
                s = spots[ob]; s["retries"] += 1; s["runs"].add(r["file"]); s["by"][r["persona"]] += 1; s["causes"][e.get("cause")] += 1
            elif e["type"] == "heart_lost":
                s = spots[ob]; s["hearts"] += 1; s["runs"].add(r["file"]); s["by"][r["persona"]] += 1
                s["causes"]["heart: " + str(e.get("cause"))] += 1
            elif e["type"] == "quit":
                s = spots[ob]; s["quits"] += 1; s["runs"].add(r["file"]); s["by"][r["persona"]] += 1
    out = []
    for ob, s in spots.items():
        score = s["retries"] + s["hearts"] + 5 * s["quits"]
        out.append({"ob": ob, "score": score, "retries": s["retries"], "hearts": s["hearts"], "quits": s["quits"],
                    "runs_affected": len(s["runs"]), "runs": len(rs), "by": dict(s["by"].most_common()), "causes": dict(s["causes"].most_common())})
    return sorted(out, key=lambda x: -x["score"])


# ---------------------------------------------------------------- captures
def typical_run(runs, level):
    cl = [r for r in sel(runs, level) if r["result"] == "clear"]
    m = st.median(r["play_time"] for r in cl)
    return min(cl, key=lambda r: (abs(r["play_time"] - m), r["file"]))


def key_moments(r):
    ev = r["events"]
    pick, used = [], set()

    def add(e, kind, label, off=0):
        if e is None or kind in used:
            return
        used.add(kind)
        pick.append((e["step"] + off, e["t"] + off / 60, label))

    first = lambda f: next((e for e in ev if f(e)), None)
    add(first(lambda e: e["type"] == "start"), "start", "start", 20)
    add(first(lambda e: e["type"] == "hint" and not e.get("say")), "hint", "first hint")
    add(first(lambda e: e["type"] == "magpie_flee"), "flee", "the magpie flies off", 20)
    add(first(lambda e: e["type"] == "magpie_drop"), "drop", "bark: it drops the ball", 6)
    add(first(lambda e: e["type"] == "cat_scared"), "cat", "bark: the cat is scared", 12)
    add(first(lambda e: e["type"] == "ball_pickup"), "pickup", "X: the ball picked up", 4)
    add(first(lambda e: e["type"] == "mech_use" and e["mech"] == "crawl"), "crawl", "crawling", 30)
    add(first(lambda e: e["type"] == "mech_use" and e["mech"] == "ride"), "ride", "riding the " + "boat/pontoon", 20)
    add(first(lambda e: e["type"] == "scramble"), "scramble", "ledge scramble", 4)
    add(first(lambda e: e["type"] == "hazard"), "hazard", "a hazard comes", 70)
    add(first(lambda e: e["type"] == "bone" and e.get("gold")), "gold", "gold bone", 0)
    add(first(lambda e: e["type"] == "heart_lost"), "heart", "a heart lost", -20)
    add(first(lambda e: e["type"] == "girl_given"), "give", "X: given to the girl", 30)
    pick.sort()
    return pick[:10]


def fail_frames(r, ob):
    ev = r["events"]
    for i, e in enumerate(ev):
        if e.get("ob") != ob:
            continue
        if e["type"] == "drown":
            return e, [e["step"] - 45, e["step"], e["step"] + 45], "fell in the water"
        if e["type"] == "hit":
            return e, [e["step"] - 35, e["step"], e["step"] + 25], "hit by the " + e.get("kind", "?")
        if e["type"] == "retry" and e.get("cause") == "missed jump":
            return e, [e["step"] - 75, e["step"] - 25, e["step"] + 20], "the jump falls short, she tries again"
        if e["type"] == "retry" and e.get("cause") == "stuck":
            j = next((x for x in reversed(ev[:i]) if x["type"] == "jump" and x["step"] > e["step"] - 900), None)
            if j:
                return e, [j["step"] - 20, j["step"] + 22, e["step"] + 30], "the jump falls short, stuck, tries again"
            return e, [e["step"] - 150, e["step"] - 30, e["step"] + 40], "stuck, tries again"
    return None, None, None


def plan(out):
    runs, auto = load(out)
    lines = []
    caps = {"frames": {}, "fails": {}}
    for L in LEVELS:
        r = typical_run(runs, L)
        km = key_moments(r)
        caps["frames"][L] = {"run": r["file"], "moments": km}
        jobs = defaultdict(set)
        jobs[r["file"]] |= {s for s, _, _ in km}
        caps["fails"][L] = []
        for spot in failure_spots(L, runs)[:3]:
            best = None
            for p, _ in Counter(spot["by"]).most_common():
                for rr in sorted(sel(runs, L, p), key=lambda x: x["file"]):
                    e, steps, what = fail_frames(rr, spot["ob"])
                    if e:
                        best = (rr, e, steps, what)
                        break
                if best:
                    break
            if not best:
                continue
            rr, e, steps, what = best
            steps = [max(1, s) for s in steps]
            caps["fails"][L].append({"ob": spot["ob"], "run": rr["file"], "steps": steps, "what": what, "t": e["t"], "persona": rr["persona"]})
            jobs[rr["file"]] |= set(steps)
        for f, steps in jobs.items():
            rr = next(x for x in runs if x["file"] == f)
            args = f"--level {rr['level']} --playtest {rr['persona']} --seed {rr['seed']}" + (" --fresh" if rr["mode"] == "fresh" else "")
            lines.append(f"{args} --out {out}/caps/{f} --capture-steps {','.join(str(s) for s in sorted(steps))} --capture-prefix {out}/caps/{f[:-5]}")
    json.dump(caps, open(os.path.join(out, "caps", "plan.json"), "w"), indent=1)
    print("\n".join(lines))


# ---------------------------------------------------------------- pictures
def font(size):
    from PIL import ImageFont
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size=size)


def cap_img(out, run_file, step):
    from PIL import Image
    p = os.path.join(out, "caps", f"{run_file[:-5]}_{step:06d}.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGB")
    if im.size != (640, 480):                       # the window is 2x; make sure of it (nearest neighbour)
        im = im.resize((640, 480), Image.NEAREST)
    return im


def strip(images, captions, title, path, cols):
    from PIL import Image, ImageDraw
    W, H, CAP, HEAD, PAD = 640, 480, 34, 44, 8
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W + (cols + 1) * PAD, HEAD + rows * (H + CAP + PAD) + PAD), (252, 252, 251))
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 10), title, fill=(11, 11, 11), font=font(22))
    for i, (im, c) in enumerate(zip(images, captions)):
        x = PAD + (i % cols) * (W + PAD)
        y = HEAD + (i // cols) * (H + CAP + PAD)
        if im is not None:
            sheet.paste(im, (x, y))
        else:
            d.rectangle([x, y, x + W, y + H], outline=(180, 180, 180))
            d.text((x + 10, y + 10), "(frame missing)", fill=(82, 81, 78), font=font(16))
        d.text((x + 4, y + H + 6), c, fill=(82, 81, 78), font=font(17))
    sheet.save(path)


COLORS = {"bone": "#eda100", "checkpoint": "#008300", "hint": "#2a78d6", "hazard": "#4a3aa7", "hurt": "#e34948",
          "retry": "#eb6834", "story": "#1baf7a", "wait": "#c9c8c2", "trying": "#e87ba4"}


def ev_class(e):
    t = e["type"]
    if t == "bone":
        return "bone"
    if t == "checkpoint":
        return "checkpoint"
    if t == "hint":
        return "hint"
    if t == "hazard":
        return "hazard"
    if t in ("heart_lost", "drown", "hit"):
        return "hurt"
    if t in ("retry", "quit", "gave_up"):
        return "retry"
    if t in ("magpie_flee", "magpie_drop", "cat_scared", "ball_pickup", "girl_given", "ball_lost", "ball_home", "fetch_approx"):
        return "story"
    return None


def timeline_png(L, auto, runs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = []
    if auto:
        rows.append(("autopilot (clean run)", auto["events"], auto["play_time"]))
    for p in PIDS:
        rs = sel(runs, L, p)
        if not rs:
            continue
        clears = [r for r in rs if r["result"] == "clear"] or rs
        m = st.median(r["play_time"] for r in clears)
        r = min(clears, key=lambda r: (abs(r["play_time"] - m), r["file"]))
        rows.append((f"{PBY[p]['name']} ({p}) seed {r['seed']}" + ("" if r["result"] == "clear" else " QUIT"), r["events"], r["play_time"]))
    tmax = max(t for _, _, t in rows) + 5
    fig = plt.figure(figsize=(14, 2.4 + 0.42 * len(rows)), dpi=110)
    fig.patch.set_facecolor("#fcfcfb")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.3, 0.42 * len(rows)], hspace=0.35)
    ax0 = fig.add_subplot(gs[0])
    if auto:
        b = per_bin(auto["events"], auto["play_time"])
        ax0.bar([i * 10 + 5 for i in range(len(b))], b, width=8, color="#2a78d6", label="autopilot: events per 10 s")
    allb = [per_bin(r["events"], r["play_time"]) for r in sel(runs, L) if r["result"] == "clear"]
    if allb:
        n = max(len(b) for b in allb)
        medb = [st.median([b[i] for b in allb if i < len(b)]) for i in range(n) if sum(1 for b in allb if i < len(b)) >= len(allb) / 2]
        ax0.plot([i * 10 + 5 for i in range(len(medb))], medb, color="#eb6834", lw=2, marker="o", ms=4,
                 label="all persona runs (clears): median events per 10 s")
    ax0.set_xlim(0, tmax)
    ax0.set_ylabel("events / 10 s", color="#52514e")
    ax0.legend(loc="upper right", frameon=False, fontsize=9)
    ax0.set_title(f"{LEVEL_NAME[L]}: pacing (bones, lamps, hints, hazards, story beats, mechanics) and timelines", loc="left", fontsize=12)
    ax = fig.add_subplot(gs[1])
    for i, (name, ev, end) in enumerate(rows):
        y = len(rows) - 1 - i
        for e in ev:
            if e["type"] == "idle":
                c = COLORS["trying"] if e.get("why") == "trying buttons" else COLORS["wait"]
                ax.add_patch(plt.Rectangle((e["t"], y - 0.32), e["dur"], 0.64, color=c, lw=0, zorder=1))
        for e in ev:
            c = ev_class(e)
            if not c:
                continue
            mk = {"bone": "|", "checkpoint": "s", "hint": "v", "hazard": ">", "hurt": "X", "retry": "o", "story": "D"}[c]
            size = 90 if (c == "bone" and e.get("gold")) else (40 if c != "bone" else 30)
            if c == "bone" and e.get("gold"):
                mk = "*"
            ax.scatter([e["t"]], [y], marker=mk, s=size, color=COLORS[c], zorder=3, linewidths=1.5 if mk == "|" else 0.5,
                       edgecolors="white" if mk not in ("|",) else None)
        ax.plot([0, end], [y, y], color="#d9d8d3", lw=1, zorder=0)
        ax.scatter([end], [y], marker="|", s=160, color="#0b0b0b", zorder=4)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=9)
    ax.set_xlim(0, tmax)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("seconds of play (game time)", color="#52514e")
    for a in (ax0, ax):
        a.set_facecolor("#fcfcfb")
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.tick_params(colors="#52514e")
        a.grid(axis="x", color="#e8e7e2", lw=0.8)
        a.set_axisbelow(True)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    leg = [Line2D([], [], marker="|", ls="", color=COLORS["bone"], ms=9, mew=1.5, label="bone"),
           Line2D([], [], marker="*", ls="", color=COLORS["bone"], ms=11, label="gold bone"),
           Line2D([], [], marker="s", ls="", color=COLORS["checkpoint"], ms=7, label="lamp lit"),
           Line2D([], [], marker="v", ls="", color=COLORS["hint"], ms=7, label="hint / message"),
           Line2D([], [], marker=">", ls="", color=COLORS["hazard"], ms=7, label="hazard spawned"),
           Line2D([], [], marker="X", ls="", color=COLORS["hurt"], ms=8, label="hurt / in the water"),
           Line2D([], [], marker="o", ls="", color=COLORS["retry"], ms=7, label="retry / quit"),
           Line2D([], [], marker="D", ls="", color=COLORS["story"], ms=6, label="story beat (magpie, cat, ball, girl)"),
           Patch(color=COLORS["wait"], label="standing still > 1 s"), Patch(color=COLORS["trying"], label="trying buttons"),
           Line2D([], [], marker="|", ls="", color="#0b0b0b", ms=11, label="end (clear or quit)")]
    ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.09 - 0.9 / len(rows)), ncol=6, frameon=False, fontsize=8.5)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


# ---------------------------------------------------------------- report
def fmt_t(x):
    return "-" if x is None else f"{x:.0f}"


def report(out):
    runs, auto = load(out)
    res = {"generated_from": f"{len(runs)} persona runs + {len(auto)} autopilot runs", "personas": PERSONAS, "levels": {}}
    for L in LEVELS:
        lv = {"grid": {}, "fresh": {}}
        for p in PIDS:
            rs = sel(runs, L, p)
            if rs:
                lv["grid"][p] = grid_cell(rs)
            fr = sel(runs, L, p, "fresh")
            if fr:
                lv["fresh"][p] = grid_cell(fr)
        a = auto.get(L)
        if a:
            gap, at = longest_gap(a["events"], a["play_time"])
            lv["autopilot"] = {"play_time": a["play_time"], "bones": a.get("bones"), "bones_total": a.get("bones_total"),
                               "events_per_10s": per_bin(a["events"], a["play_time"]), "longest_gap_s": round(gap, 1), "longest_gap_from_s": round(at, 1),
                               "hearts_lost": sum(1 for e in a["events"] if e["type"] == "heart_lost")}
        lv["teach"] = teach_table(L, a, runs)
        lv["hints"] = hints_seen(L, a, runs)
        lv["hazards"] = hazard_table(L, runs)
        lv["failure_spots"] = failure_spots(L, runs)[:10]
        res["levels"][L] = lv
    # the runs themselves, events summarised
    slim = []
    for r in runs:
        ev = r["events"]
        keep = [{k: e[k] for k in e if k not in ("T",)} for e in ev if e["type"] not in ("bone", "mech_use", "bark", "idle", "fun_bark", "jump", "scramble")]
        slim.append({k: r[k] for k in r if k not in ("events", "file")} | {
            "file": "runs/" + r["file"], "event_counts": dict(Counter(e["type"] for e in ev)),
            "idle": run_metrics(r)["idle"], "key_events": keep})
    res["runs"] = slim
    json.dump(res, open(os.path.join(out, "results.json"), "w"), indent=1)

    # pictures
    caps = json.load(open(os.path.join(out, "caps", "plan.json"))) if os.path.exists(os.path.join(out, "caps", "plan.json")) else None
    for L in LEVELS:
        timeline_png(L, auto.get(L), runs, os.path.join(out, f"timeline_{L}.png"))
        if not caps:
            continue
        fr = caps["frames"][L]
        rr = next(x for x in runs if x["file"] == fr["run"])
        imgs = [cap_img(out, fr["run"], s) for s, _, _ in fr["moments"]]
        caps_txt = [f"{t:5.1f} s  {label}" for _, t, label in fr["moments"]]
        strip(imgs, caps_txt, f"{LEVEL_NAME[L]}: key moments of a typical run ({PBY[rr['persona']]['name']}, {rr['persona']}, seed {rr['seed']}, "
              f"{rr['play_time']:.0f} s, the clear closest to the median of all clears)", os.path.join(out, f"frames_{L}.png"), 5)
        for n, f in enumerate(caps["fails"][L], 1):
            imgs = [cap_img(out, f["run"], s) for s in f["steps"]]
            rr = next(x for x in runs if x["file"] == f["run"])
            spot = next(s for s in res["levels"][L]["failure_spots"] if s["ob"] == f["ob"])
            strip(imgs, ["before", "during: " + f["what"], "after"],
                  f"{LEVEL_NAME[L]}, failure spot {n}: {f['ob']}  ({spot['retries']} retries, {spot['hearts']} hearts, {spot['quits']} quits in "
                  f"{spot['runs']} runs).  Frames from {PBY[rr['persona']]['name']} ({rr['persona']}) seed {rr['seed']} at {f['t']:.1f} s",
                  os.path.join(out, f"fail_{L}_{n}.png"), 3)
    write_summary(out, res, runs, auto, caps)
    src = os.path.join(REPO, "docs/playtest/method.md")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(out, "method.md"))
    print("wrote", out)


def write_summary(out, res, runs, auto, caps):
    L_ = res["levels"]
    o = []
    w = o.append
    w("# FETCH! synthetic playtest: summary")
    w("")
    w(f"Generated by tools/analyse_playtest.py from {res['generated_from']}. Game time is play time at 1/60 s steps (cards "
      "not included). How the bots play and what is approximated: method.md. Every number here comes from the run files in runs/.")
    w("")
    n = {L: len(sel(runs, L, PIDS[0])) for L in LEVELS}
    w(f"Seeds per persona and level (campaign: the level played after the ones before it): " + ", ".join(f"{LEVEL_NAME[L]} {n[L]}" for L in LEVELS) + ".")
    w("")
    w("## The grid: persona x level")
    w("")
    w("Completion % | median time to clear in s of play (p25 to p75) | median hearts lost (max) | mean retries per run | bones % (gold found per run, of 2 or 1).")
    w("")
    w("| Persona | " + " | ".join(LEVEL_NAME[L] for L in LEVELS) + " |")
    w("|---|" + "---|" * len(LEVELS))
    for p in PIDS:
        cells = []
        for L in LEVELS:
            c = L_[L]["grid"].get(p)
            if not c:
                cells.append("-"); continue
            cells.append(f"**{pct(c['completion'])}** \\| {fmt_t(c['play_median'])} s ({fmt_t(c['play_p25'])} to {fmt_t(c['play_p75'])}) \\| "
                         f"{c['hearts_median']:g} ({c['hearts_max']}) \\| {c['retries_mean']:g} \\| {pct(c['bones_pct'])} ({c['gold_mean']:g}/{c['gold_total']})")
        pp = PBY[p]
        w(f"| {pp['name']} ({pp['group']}, {pp['age']}, reads {pp['reads']}) | " + " | ".join(cells) + " |")
    w("")
    w("Where they quit (runs that did not clear):")
    w("")
    for L in LEVELS:
        qs = Counter()
        for p in PIDS:
            for k, v in L_[L]["grid"].get(p, {}).get("quits", {}).items():
                qs[f"{p}: {k}"] += v
        w(f"- {LEVEL_NAME[L]}: " + ("; ".join(f"{k} x{v}" for k, v in qs.most_common()) if qs else "nobody quit"))
    w("")
    w("Time with cards: the median total (play + intro card + tally + the story card, estimated + approximated fetches/walk-backs):")
    w("")
    w("| Persona | " + " | ".join(LEVEL_NAME[L] for L in LEVELS) + " |")
    w("|---|" + "---|" * len(LEVELS))
    for p in PIDS:
        w(f"| {p} | " + " | ".join(f"{fmt_t(L_[L]['grid'][p]['total_median'])} s (cards {L_[L]['grid'][p]['cards_median']:g} s, approx {L_[L]['grid'][p]['approx_mean']:g} s)" for L in LEVELS) + " |")
    w("")
    # per level
    for L in LEVELS:
        lv = L_[L]
        w(f"## {LEVEL_NAME[L]}")
        w("")
        a = lv.get("autopilot")
        if a:
            w(f"**Pacing (autopilot clean run):** {a['play_time']:.1f} s, {a['bones']}/{a['bones_total']} bones, {a['hearts_lost']} hearts lost. "
              f"Events per 10 s: {', '.join(str(x) for x in a['events_per_10s'])}. Longest stretch with nothing new: {a['longest_gap_s']} s "
              f"(from {a['longest_gap_from_s']} s). Median longest stretch in the persona runs: "
              + ", ".join(f"{p} {lv['grid'][p]['longest_gap_median']:g} s" for p in PIDS) + ".")
            w("")
        w("**Retries and hearts by obstacle** (all personas, campaign runs; score = retries + hearts + 5 x quits):")
        w("")
        w("| Obstacle | retries | hearts | quits | runs affected | who (failures) | how |")
        w("|---|---|---|---|---|---|---|")
        for s in lv["failure_spots"][:8]:
            w(f"| {s['ob']}{' (optional)' if s['ob'] in OPTIONAL else ''} | {s['retries']} | {s['hearts']} | {s['quits']} | {s['runs_affected']} of {s['runs']} | "
              + ", ".join(f"{k} {v}" for k, v in list(s["by"].items())[:4]) + " | " + ", ".join(f"{k} {v}" for k, v in list(s["causes"].items())[:3]) + " |")
        w("")
        w("**Taught before tested?** For each mechanic: the first text in the clean run that teaches it (readable by: all = reads all; "
          "short + all = a hint of 4 words or less), where the level first really needs it, and how the persona runs did there.")
        w("")
        w("| Mechanic | taught (s: text, readable by) | first needed (x, s in the clean run, where) | s between | persona runs that failed there (with a heart lost) |")
        w("|---|---|---|---|---|")
        for row in lv["teach"]:
            t, nd = row["taught"], row["need"]
            w(f"| {MECH_NAME.get(row['mech'], row['mech'])} | " + (f"{t['t']:.1f}: \"{t['text']}\" ({t['who']})" if t else "**no text teaches it**") + " | "
              + f"x {nd['x']}, " + (f"{nd['t']:.1f} s" if nd["t"] is not None else "-") + f", {nd['what']} | "
              + (f"{row['gap']:.1f}" if row["gap"] is not None else "-") + f" | {row['fail_runs']} of {row['runs']} ({row['hurt_runs']}); {row['fail_label']} |")
        w("")
        hs = lv["hints"]
        miss = [h for h in hs if not h["clean_run"]]
        w("**Hints:** " + f"{sum(1 for h in hs if h['words'] <= 4)} of {len(hs)} are short enough for a short reader (4 words or less): "
          + ", ".join(f'"{h["text"]}"' for h in hs if h["words"] <= 4) + ". "
          + ("Not shown in the clean run (a message was on the banner, or the condition never held): " + "; ".join(
              f'"{h["text"]}" (seen in {h["persona_runs"]} of {h["runs"]} persona runs)' for h in miss) + "." if miss else "All were shown in the clean run."))
        w("")
        hz = {k: v for k, v in lv["hazards"].items() if isinstance(v, dict)}
        if hz:
            w("**Hazard, first encounter:** " + "; ".join(
                f"{k}: met in {v['runs']} of {lv['hazards']['runs']} runs, a heart lost at the first one in {v['hit_first']} "
                f"({pct(v['hit_first'] / v['runs'])}), {v['warn_median_s']} s median from spawn to reaching Pepper's x, {v['hits_total']} hits in all" for k, v in hz.items())
                + (f"; never met in {lv['hazards'].get('none', 0)} runs." if lv['hazards'].get('none') else "."))
            w("")
        if L == "citypark":
            w("**The magpie:** " + "; ".join(
                f"{p} drop at {lv['grid'][p]['magpie_drop_t_median']} s after {lv['grid'][p]['magpie_flees_mean']} flees (perch {lv['grid'][p]['magpie_drop_perch']})"
                for p in PIDS) + ".")
            w("")
        if L == "downtown":
            w("**The cat:** seconds from the 'Y: BARK AT THE CAT!' hint to the cat scared / the ball picked up: "
              + "; ".join(f"{p} {lv['grid'][p]['cat_t_median']} / {lv['grid'][p]['cat_pick_t_median']}" for p in PIDS) + ".")
            w("")
        w("**Standing still and waiting** (s per run, mean): " + "; ".join(
            f"{p}: " + ", ".join(f"{k} {v:g}" for k, v in list(lv['grid'][p]['idle_per_run'].items())[:4]) for p in PIDS) + ".")
        w("")
        d = {p: lv["grid"][p]["discoveries"] for p in PIDS if lv["grid"][p]["discoveries"]}
        w("**Mechanics found by trying** (runs that had to, median seconds of trying): "
          + ("; ".join(f"{p}: " + ", ".join(f"{m} {v['runs']} runs {v['median_s']} s" for m, v in dd.items()) for p, dd in d.items()) if d else "none") + ".")
        w("")
        w(f"Pictures: timeline_{L}.png, frames_{L}.png" + "".join(f", fail_{L}_{i + 1}.png" for i in range(len((caps or {}).get('fails', {}).get(L, [])))) + ".")
        w("")
    # fresh
    w("## Fresh players (levels 2 and 3 without having played the ones before)")
    w("")
    w("| Persona | " + " | ".join(LEVEL_NAME[L] for L in LEVELS[1:]) + " |")
    w("|---|" + "---|" * 2)
    for p in PIDS:
        cells = []
        for L in LEVELS[1:]:
            c = L_[L]["fresh"].get(p)
            if not c:
                cells.append("-"); continue
            dd = ", ".join(f"{m} {v['median_s']} s" for m, v in c["discoveries"].items())
            cells.append(f"{pct(c['completion'])} \\| {fmt_t(c['play_median'])} s \\| hearts {c['hearts_median']:g} \\| retries {c['retries_mean']:g}"
                         + (f" \\| found: {dd}" if dd else "") + (f" \\| quits: " + "; ".join(c["quits"]) if c["quits"] else ""))
        w(f"| {p} | " + " | ".join(cells) + " |")
    w("")
    # problems by persona
    w("## The biggest problems by persona (evidence)")
    w("")
    for p in PIDS:
        pp = PBY[p]
        items = []
        for L in LEVELS:
            c = L_[L]["grid"][p]
            rs = sel(runs, L, p)
            for ob, fr in list(c["fails_per_run"].items())[:2]:
                if fr >= 0.3:
                    items.append((fr, f"{LEVEL_NAME[L]}, {ob}: {fr:g} retries per run"))
            if c["completion"] < 1:
                items.append((10, f"{LEVEL_NAME[L]}: cleared {c['clears']} of {c['runs']}; quits: " + "; ".join(f"{k} x{v}" for k, v in c["quits"].items())))
            if c["hearts_mean"] >= 0.5:
                items.append((c["hearts_mean"] * 2, f"{LEVEL_NAME[L]}: {c['hearts_mean']:g} hearts lost per run ({', '.join(f'{k} {v}' for k, v in c['heart_causes'].items())}; "
                              f"at {', '.join(list(c['heart_places'])[:3])})"))
            for m, v in c["discoveries"].items():
                if v["runs"] >= len(rs) / 2:
                    items.append((v["median_s"] or 0, f"{LEVEL_NAME[L]}: had to find '{MECH_NAME.get(m, m)}' by trying in {v['runs']} of {len(rs)} runs (median {v['median_s']} s)"))
            if L == "citypark" and c["magpie_flees_mean"] >= 1:
                items.append((c["magpie_flees_mean"] * 3, f"{LEVEL_NAME[L]}: the magpie flew off {c['magpie_flees_mean']:g} times per run before the bark (drop at {c['magpie_drop_t_median']} s)"))
            wait = sum(v for k, v in c["idle_per_run"].items() if k.startswith("waiting"))
            if wait >= 5:
                items.append((wait / 2, f"{LEVEL_NAME[L]}: {wait:.0f} s per run standing and waiting (boat, cart, tram, pontoon, bikes)"))
        items.sort(key=lambda x: -x[0])
        w(f"- **{pp['name']} ({p})**: " + ("; ".join(t for _, t in items[:5]) if items else "no notable problems") + ".")
    w("")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(o) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("plan", "report"):
        print(__doc__)
        sys.exit(1)
    (plan if sys.argv[1] == "plan" else report)(os.path.abspath(sys.argv[2]))
