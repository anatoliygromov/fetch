#!/usr/bin/env python3
"""Turns the playtest runs (tools/run_playtest.py) into tables, the difficulty index and charts.

  python3 tools/analyse_playtest.py [--out /home/claude/out/r4-playtest]

Reads <out>/runs/*.json. Writes <out>/summary.csv (persona x level), <out>/spots.csv (failures per spot),
<out>/summary.json (everything the report quotes), <out>/difficulty_by_level.png, <out>/clear_quit_heatmap.png,
<out>/stalls_<level>.png (the three worst levels), and docs/playtest/summary_22oct.json (small, committed).

Difficulty index (DI), per persona per level, on runs the lab did not lose (result "lost" is left out):
  DI = 50 * quit rate                                   (quit = patience ran out, or the session ran out)
     + 10 * hearts lost per minute played
     +  5 * failures at the run's worst spot (mean over runs, capped at 6)
     +  5 * (median clear time / perfect clear time - 1)   (capped at 5; campaign-adjusted, see below)
A group's DI is the mean of its personas' DIs. Campaign adjustment: a control found by trying on an earlier level of
the order is known, so its trying time is taken off the clear time (the order changes it, so it is per order).
"""
import collections, csv, glob, json, os, re, statistics, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "/home/claude/out/r4-playtest"
LEVELS = ["citypark", "citypark_tall", "riverwalk", "downtown", "downtown_tall", "rooftops", "soder", "night"]
NAMES = {"citypark": "City Park", "citypark_tall": "City Park (tall)", "riverwalk": "River Walk", "downtown": "Downtown",
         "downtown_tall": "Downtown (tall)", "rooftops": "Rooftops", "soder": "Soder Hill", "night": "Night Harbour"}
GROUPS = ["kids", "parents", "retro"]
ORDERS = {
    "proposed A (City Park, Downtown)": ["citypark", "riverwalk", "downtown", "rooftops", "soder", "night"],
    "proposed B (City Park tall, Downtown)": ["citypark_tall", "riverwalk", "downtown", "rooftops", "soder", "night"],
    "proposed C (City Park, Downtown tall)": ["citypark", "riverwalk", "downtown_tall", "rooftops", "soder", "night"],
    "proposed D (City Park tall, Downtown tall)": ["citypark_tall", "riverwalk", "downtown_tall", "rooftops", "soder", "night"],
    "current A (City Park, Downtown 2nd)": ["citypark", "downtown", "riverwalk", "rooftops", "soder", "night"],
    "current B (City Park tall, Downtown tall 2nd)": ["citypark_tall", "downtown_tall", "riverwalk", "rooftops", "soder", "night"],
}

personas = json.load(open(os.path.join(ROOT, "docs/playtest/personas.json")))["personas"]
PIDS = [p["id"] for p in personas]
PGROUP = {p["id"]: p["group"] for p in personas}
PNAME = {p["id"]: f"{p['name']} {p['age']}" for p in personas}


# ---- beats: the screens of each level, from its beat sheet (x ranges)
def beats(level):
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
            elif cells[1].isdigit():                                     # Night Harbour: | n | x | name |
                x0 = int(cells[1]); out.append((x0, x0 + 320, f"{cells[0]} {cells[2].strip('* ')}"))
        seen, uniq = set(), []                                           # (the tall sheets have a perch table too)
        for b in out:
            if b[2].split()[0] in seen:
                break
            seen.add(b[2].split()[0]); uniq.append(b)
        out = uniq
    return out


BEATS = {lv: beats(lv) for lv in LEVELS}


def beat_name(level, x):
    for x0, x1, n in BEATS[level]:
        if x0 <= x < x1:
            return n
    return f"screen {int(x // 320) + 1}"


# ---- load
runs = collections.defaultdict(list)
perfect = {}
for f in glob.glob(os.path.join(OUT, "runs", "*.json")):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if d["persona"] == "perfect":
        key = d["level"] + ("_high" if "_high__" in f else "")
        perfect[key] = d
        continue
    runs[(d["persona"], d["level"])].append(d)

if not runs:
    sys.exit("no runs in " + OUT)


def perfect_time(d):
    key = d["level"] + ("_high" if d.get("route") == "high" else "")
    p = perfect.get(key) or perfect.get(d["level"])
    return p["clear_time"] if p and p.get("clear_time") else None


def needed_mechs(level):
    m = set()
    for (pid, lv), rs in runs.items():
        if lv == level:
            for r in rs:
                for x in r["discover"]:
                    m.add(x["mech"])
    return m


NEED = {lv: needed_mechs(lv) for lv in LEVELS}


def pct(v, q):
    v = sorted(v)
    if not v:
        return None
    k = (len(v) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def metrics(pid, level, known_before=frozenset()):
    rs = runs.get((pid, level), [])
    good = [r for r in rs if r["result"] != "lost"]
    m = {"persona": pid, "group": PGROUP[pid], "level": level, "runs": len(rs), "lost": len(rs) - len(good)}
    if not good:
        return m
    n = len(good)
    clears = [r for r in good if r["result"] == "clear"]
    quits = [r for r in good if r["result"] in ("quit", "session")]
    m["clear_rate"] = len(clears) / n
    m["quit_rate"] = len(quits) / n
    m["session_out"] = sum(r["result"] == "session" for r in good) / n
    play = sum(r["play_time"] for r in good) / 60
    m["hearts_per_min"] = sum(r["hearts_lost"] for r in good) / max(play, 1e-6)
    m["hearts_lost"] = statistics.mean(r["hearts_lost"] for r in good)
    m["lives_lost"] = statistics.mean(r["lives_lost"] for r in good)
    m["gameovers"] = statistics.mean(r["gameovers"] for r in good)
    worst = []
    for r in good:
        c = collections.Counter(x["spot"] for x in r["fails"])
        worst.append(max(c.values()) if c else 0)
    m["worst_spot_fails"] = statistics.mean(min(w, 6) for w in worst)
    m["retries"] = statistics.mean(len(r["fails"]) for r in good)

    def adj(r):                                       # the trying time for controls known from earlier levels
        return sum(x["dur"] for x in r["discover"] if x["how"] == "tried" and x["mech"] in known_before)
    ct = [r["clear_time"] - adj(r) for r in clears if r.get("clear_time")]
    m["clear_median"] = statistics.median(ct) if ct else None
    m["clear_p90"] = pct(ct, 0.9) if ct else None
    over = [min(5, (r["clear_time"] - adj(r)) / perfect_time(r) - 1) for r in clears if r.get("clear_time") and perfect_time(r)]
    m["time_over_perfect"] = statistics.median(over) if over else 5.0
    m["waits"] = statistics.mean(r["waits"] for r in good)
    m["bones_pct"] = statistics.mean(100 * r["bones"] / max(1, r["bones_total"]) for r in good)
    m["secrets"] = statistics.mean(r["secrets"] for r in good)
    m["secrets_total"] = good[0]["secrets_total"]
    disc = collections.defaultdict(list)
    for r in good:
        for x in r["discover"]:
            if x["mech"] not in known_before:
                disc[x["mech"]].append(x)
    m["discover"] = {k: {"runs": len(v), "tried": sum(x["how"] == "tried" for x in v),
                         "median_s": statistics.median([x["dur"] for x in v if x["how"] == "tried"] or [0])} for k, v in disc.items()}
    m["DI"] = 50 * m["quit_rate"] + 10 * m["hearts_per_min"] + 5 * m["worst_spot_fails"] + 5 * m["time_over_perfect"]
    m["routes"] = dict(collections.Counter(r.get("route") or "main" for r in good))
    return m


# ---- per persona x level (fresh: nothing known)
rows = [metrics(pid, lv) for lv in LEVELS for pid in PIDS]
by = {(m["persona"], m["level"]): m for m in rows}


def group_di(level, known=frozenset()):
    out = {}
    for g in GROUPS:
        v = [metrics(pid, level, known)["DI"] for pid in PIDS if PGROUP[pid] == g and "DI" in by[(pid, level)]]
        out[g] = statistics.mean(v) if v else None
    return out


order_di = {}
for name, order in ORDERS.items():
    known, seq = set(), []
    for lv in order:
        seq.append({"level": lv, **group_di(lv, frozenset(known))})
        known |= NEED[lv]
    order_di[name] = seq


def check(seq):
    flags = []
    for g in GROUPS:
        for a, b in zip(seq, seq[1:]):
            if a[g] is None or b[g] is None:
                continue
            if a[g] > b[g] + 2:
                flags.append(f"{g}: {NAMES[a['level']]} ({a[g]:.0f}) harder than the next, {NAMES[b['level']]} ({b[g]:.0f})")
            elif abs(b[g] - a[g]) <= 2:
                flags.append(f"{g}: flat from {NAMES[a['level']]} ({a[g]:.0f}) to {NAMES[b['level']]} ({b[g]:.0f})")
    return flags


def roughness(seq):                                  # the sum of the drops (a smooth order has none) per group
    return {g: sum(max(0, a[g] - b[g]) for a, b in zip(seq, seq[1:]) if a[g] is not None and b[g] is not None) for g in GROUPS}


# ---- spots: failures and quits per beat
spots = []
for lv in LEVELS:
    c = collections.Counter(); q = collections.Counter(); stall = collections.Counter(); who = collections.defaultdict(collections.Counter)
    total = 0
    for pid in PIDS:
        for r in runs.get((pid, lv), []):
            if r["result"] == "lost":
                continue
            for x in r["fails"]:
                pos = r["spot_pos"].get(x["spot"], [x["x"], x["y"]])
                b = beat_name(lv, pos[0]); c[b] += 1; who[b][pid] += 1; total += 1
            if r["result"] in ("quit", "session") and r.get("quit_xy"):
                q[beat_name(lv, r["spot_pos"].get(r["quit_spot"], r["quit_xy"])[0])] += 1
            for key, v in r["stall"].items():
                cx = int(key.split(",")[0]) * 32
                stall[beat_name(lv, cx)] += sum(v[1:])                       # trying, recovering, standing (not waits)
    for b, n in c.most_common():
        spots.append({"level": lv, "beat": b, "failures": n, "share": n / max(total, 1), "quits": q[b],
                      "stall_s_per_run": stall[b] / max(1, sum(len(runs.get((p, lv), [])) for p in PIDS)),
                      "worst_persona": PNAME[who[b].most_common(1)[0][0]]})

# ---- every run, the lost ones too (up to where the lab lost the route): failures and hearts per minute played,
# and where the lab lost the route (spots to check by hand)
allrun = {}
lostspots = []
for lv in LEVELS:
    for g in GROUPS:
        rs = [r for p in PIDS if PGROUP[p] == g for r in runs.get((p, lv), [])]
        mins = sum(r["play_time"] for r in rs) / 60
        allrun[f"{lv}|{g}"] = {"fails_per_min": sum(len(r["fails"]) for r in rs) / max(mins, 1e-6),
                               "hearts_per_min": sum(r["hearts_lost"] for r in rs) / max(mins, 1e-6),
                               "lost_share": sum(r["result"] == "lost" for r in rs) / max(1, len(rs)),
                               "route_done": statistics.mean(r["max_step"] / max(1, r["steps_total"]) for r in rs) if rs else None}
    c = collections.Counter()
    for p in PIDS:
        for r in runs.get((p, lv), []):
            if r["result"] == "lost":
                c[beat_name(lv, r["spot_pos"].get(r["quit_spot"], r.get("quit_xy") or [0, 0])[0])] += 1
    for b, n in c.most_common(3):
        lostspots.append({"level": lv, "beat": b, "lost_runs": n})

# ---- write tables
os.makedirs(OUT, exist_ok=True)
cols = ["level", "persona", "group", "runs", "lost", "clear_rate", "quit_rate", "session_out", "hearts_lost", "hearts_per_min",
        "lives_lost", "gameovers", "retries", "worst_spot_fails", "clear_median", "clear_p90", "time_over_perfect", "waits",
        "bones_pct", "secrets", "secrets_total", "DI"]
with open(os.path.join(OUT, "summary.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for m in rows:
        w.writerow([round(m[c], 3) if isinstance(m.get(c), float) else m.get(c) for c in cols])
with open(os.path.join(OUT, "spots.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(spots[0].keys())); w.writeheader(); w.writerows(spots)

summary = {"perfect": {k: {"clear_time": v.get("clear_time"), "bones": v["bones"], "bones_total": v["bones_total"],
                           "secrets": v["secrets"], "waits": v["waits"]} for k, v in perfect.items()},
           "rows": rows, "orders": order_di, "flags": {k: check(v) for k, v in order_di.items()},
           "roughness": {k: roughness(v) for k, v in order_di.items()}, "spots": spots[:400],
           "fresh_group_di": {lv: group_di(lv) for lv in LEVELS}, "need": {k: sorted(v) for k, v in NEED.items()},
           "runs_per_cell": {f"{p}|{l}": len(v) for (p, l), v in runs.items()}, "allrun": allrun, "lostspots": lostspots}
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)
small = {k: summary[k] for k in ("perfect", "orders", "flags", "roughness", "fresh_group_di", "need", "allrun", "lostspots")}
small["table"] = [{c: (round(m[c], 3) if isinstance(m.get(c), float) else m.get(c)) for c in cols} for m in rows]
small["spots_top"] = [s for s in spots if s["failures"] >= 5][:60]
json.dump(small, open(os.path.join(ROOT, "docs/playtest/summary_22oct.json"), "w"), indent=1)

# ---- charts
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

GC = {"kids": "#d1495b", "parents": "#2e86ab", "retro": "#5b8e3e"}
fig, axes = plt.subplots(2, 3, figsize=(15, 8.5), sharey=True)
for ax, (name, seq) in zip(axes.flat, order_di.items()):
    xs = range(len(seq))
    for g in GROUPS:
        ax.plot(xs, [s[g] for s in seq], "-o", color=GC[g], label=g, lw=2)
    ax.set_xticks(list(xs)); ax.set_xticklabels([f"{i + 1} {NAMES[s['level']]}" for i, s in enumerate(seq)], rotation=35, ha="right", fontsize=8)
    ax.set_title(name, fontsize=10); ax.grid(alpha=0.3)
axes[0][0].set_ylabel("difficulty index"); axes[1][0].set_ylabel("difficulty index")
axes[0][0].legend()
fig.suptitle("Difficulty index by level, per player group, for each candidate order (higher = harder)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "difficulty_by_level.png"), dpi=110); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
for ax, key, title, cmap in ((axes[0], "clear_rate", "Clear rate", "Greens"), (axes[1], "quit_rate", "Quit rate (patience or session ran out)", "Reds")):
    M = np.array([[by[(p, lv)].get(key, np.nan) for p in PIDS] for lv in LEVELS], dtype=float)
    ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(PIDS))); ax.set_xticklabels([PNAME[p] for p in PIDS], rotation=35, ha="right")
    ax.set_yticks(range(len(LEVELS))); ax.set_yticklabels([NAMES[l] for l in LEVELS])
    for i in range(len(LEVELS)):
        for j in range(len(PIDS)):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{100 * M[i, j]:.0f}", ha="center", va="center", fontsize=8, color="black" if M[i, j] < 0.6 else "white")
    ax.set_title(title + " (%)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "clear_quit_heatmap.png"), dpi=110); plt.close(fig)

# stall maps of the three hardest levels (mean DI over all personas)
mean_di = {lv: statistics.mean(by[(p, lv)]["DI"] for p in PIDS if "DI" in by[(p, lv)]) for lv in LEVELS}
worst3 = sorted(LEVELS, key=lambda l: -mean_di[l])[:3]
summary["worst3"] = worst3
for lv in worst3:
    tmx = os.path.join(ROOT, "maps", f"{lv}.tmx")
    png = os.path.join(OUT, f"map_{lv}.png")
    if not os.path.exists(png):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/tiled/render_map.py"), tmx, png, "--scale", "1"], cwd=ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(png):
        continue
    im = Image.open(png).convert("RGB")
    head = open(tmx).read(2000)
    mw = re.search(r'<map[^>]*\bwidth="(\d+)"', head); mh = re.search(r'<map[^>]*\bheight="(\d+)"', head)
    tw = re.search(r'tilewidth="(\d+)"', head)
    H = int(mh.group(1)) * int(tw.group(1)) if mh and tw else im.height
    top = im.height - H
    cells = collections.Counter(); fails = collections.Counter()
    for p in PIDS:
        for r in runs.get((p, lv), []):
            if r["result"] == "lost":
                continue
            for key, v in r["stall"].items():
                cx, cy = map(int, key.split(",")); cells[(cx, cy)] += sum(v[1:])
            for x in r["fails"]:
                fails[(x["x"] // 32, x["y"] // 32)] += 1
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    mx = max(cells.values()) if cells else 1
    for (cx, cy), v in cells.items():
        a = int(40 + 200 * min(1, (v / mx) ** 0.5))
        d.rectangle([cx * 32, top + cy * 32, cx * 32 + 31, top + cy * 32 + 31], fill=(255, 40, 40, a))
    fm = max(fails.values()) if fails else 1
    for (cx, cy), v in fails.items():
        rr = 3 + int(10 * (v / fm) ** 0.5)
        x, y = cx * 32 + 16, top + cy * 32 + 16
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 255, 0, 255), width=2)
    out = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    strip = 1600                                                        # long levels: stacked strips
    n = (out.width + strip - 1) // strip
    sheet = Image.new("RGB", (min(strip, out.width), out.height * n + 6 * (n - 1)), (0, 0, 0))
    for i in range(n):
        sheet.paste(out.crop((i * strip, 0, min(out.width, (i + 1) * strip), out.height)), (0, i * (out.height + 6)))
    sheet.save(os.path.join(OUT, f"stalls_{lv}.png"))
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)

# ---- console digest
print("fresh DI per group:")
for lv in LEVELS:
    g = summary["fresh_group_di"][lv]
    print(f"  {NAMES[lv]:18s} " + "  ".join(f"{k} {v:5.1f}" for k, v in g.items() if v is not None), " lost", sum(by[(p, lv)]["lost"] for p in PIDS), "of", sum(by[(p, lv)]["runs"] for p in PIDS))
for name, seq in order_di.items():
    print(name, " | ".join(f"{NAMES[s['level']]}: " + "/".join("-" if s[g] is None else f"{s[g]:.0f}" for g in GROUPS) for s in seq), "rough", {k: round(v, 1) for k, v in roughness(seq).items()})
print("worst3", worst3)
for k, v in allrun.items(): print(k, {a: (round(b, 2) if b is not None else None) for a, b in v.items()})
for x in lostspots: print("lost", x)
