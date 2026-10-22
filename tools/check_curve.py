#!/usr/bin/env python3
"""Acceptance test of the difficulty curve: plays an order in whole-game mode for all eight personas and checks it.

  python3 tools/check_curve.py --order riverwalk,citypark,downtown,rooftops,soder,night [--seeds 20] [--jobs N]
                               [--out /home/claude/out/r6-lab/curve_<name>] [--name new] [--groups kids,parents]
                               [--x 8] [--spot-max 0.35] [--elsa-min 0.5] [--lost-max 0.05] [--analyse-only]

Runs tools/run_campaign.py (each persona plays the order as one playthrough per seed; runs already on disk are
reused), then reports per group (kids, parents, retro) and per level:
  DI v2 (and the old DI v1 beside it), the learning seconds, the worst spot's share of the level's failures,
  Elsa's clear rate, and the lost-run rate. Exit code 0 when every target passes, 1 otherwise.

Targets (docs/playtest/method.md, "Acceptance test"):
  T1 sawtooth, for each group in --groups (default kids and parents; retro is reported, not judged), on DI v2:
     (a) no spike: every level is at most X (default 8) DI points harder than the hardest of the next two levels
         (the last but one: than the last); dips are fine, a level that towers over what follows is not;
     (b) it climbs: the second half of the order is at least as hard as the first half (mean DI v2; the middle
         level of an odd order counts in neither), and the last level is at least as hard as the first.
  T2 no spot (a screen of the beat sheet, else a 320 px screen) has more than 35% of a level's failures (all personas,
     runs the lab kept; levels with fewer than 20 failures pass).
  T3 Elsa (6) clears every level in at least 50% of her playthroughs.
  T4 the lab loses under 5% of the runs on every level (a lost run: the bot, not the player, lost the route).

DI v1 (22 Oct) = 50 x quit rate + 10 x hearts lost per minute + 5 x failures at the run's worst spot (mean, cap 6)
               + 5 x (median clear time / clean clear time - 1, cap 5).
DI v2 separates learning from failing: the same four terms, but the trying time (standing, finding a control the
persona does not know yet) is taken out of the play minutes and of the clear time, and a failure that taught a control
(the held jump that came out as a hop) is not counted at its spot. The learning seconds are reported on their own.
"""
import argparse, collections, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt_common import NAMES, beat_name, personas as load_personas, perfect_file
from run_campaign import run_campaign

GROUPS = ["kids", "parents", "retro"]


def learning(r):
    return sum(x.get("dur", 0) for x in r.get("discover", []) if x.get("how") == "tried")


def learn_fails(r):
    """Failures that taught a control: a fail at the same moment a held-jump trying time began."""
    ts = [x["t"] for x in r.get("discover", []) if x.get("how") == "tried" and x.get("mech") == "heldjump"]
    return {i for i, f in enumerate(r.get("fails", [])) if any(abs(f["t"] - t) < 0.05 for t in ts)}


def persona_level(rs, perfect_t):
    good = [r for r in rs if r["result"] not in ("lost", "crash")]
    m = {"runs": len(rs), "lost": len(rs) - len(good)}
    if not good:
        return m
    n = len(good)
    clears = [r for r in good if r["result"] == "clear"]
    m["clear_rate"] = len(clears) / n
    m["quit_rate"] = sum(r["result"] in ("quit", "session", "stuck") for r in good) / n
    play = sum(r["play_time"] for r in good) / 60
    learn = sum(learning(r) for r in good) / 60
    hearts = sum(r["hearts_lost"] for r in good)
    m["hearts_per_min"] = hearts / max(play, 1e-6)
    m["hearts_per_min_v2"] = hearts / max(play - learn, 1e-6)
    w1, w2 = [], []
    for r in good:
        lf = learn_fails(r)
        c1 = collections.Counter(x["spot"] for x in r["fails"])
        c2 = collections.Counter(x["spot"] for i, x in enumerate(r["fails"]) if i not in lf)
        w1.append(min(6, max(c1.values()) if c1 else 0)); w2.append(min(6, max(c2.values()) if c2 else 0))
    m["worst_spot"] = statistics.mean(w1); m["worst_spot_v2"] = statistics.mean(w2)
    ct1 = [r["clear_time"] for r in clears if r.get("clear_time")]
    ct2 = [r["clear_time"] - learning(r) for r in clears if r.get("clear_time")]
    m["over1"] = min(5, statistics.median(ct1) / perfect_t - 1) if ct1 and perfect_t else 5.0
    m["over2"] = min(5, max(0, statistics.median(ct2) / perfect_t - 1)) if ct2 and perfect_t else 5.0
    m["learn_s"] = statistics.median([learning(r) for r in good])
    m["DI1"] = 50 * m["quit_rate"] + 10 * m["hearts_per_min"] + 5 * m["worst_spot"] + 5 * m["over1"]
    m["DI2"] = 50 * m["quit_rate"] + 10 * m["hearts_per_min_v2"] + 5 * m["worst_spot_v2"] + 5 * m["over2"]
    return m


def analyse(order, out, args):
    P = load_personas()
    pg = {p["id"]: p["group"] for p in P}
    runs = collections.defaultdict(list)
    rdir = os.path.join(out, "runs")
    for f in os.listdir(rdir):
        if not f.endswith(".json"):
            continue
        d = json.load(open(os.path.join(rdir, f)))
        if d.get("order") != order:
            continue
        runs[(d["persona"], d["k"])].append(d)
    perf = {}
    for k, lv in enumerate(order, 1):
        ts = []
        for road in (["low", "high"] if lv == "rooftops" else [None]):
            pf = perfect_file(os.path.join(out, "perfect"), lv, road)
            if os.path.exists(pf):
                ts.append(json.load(open(pf)).get("clear_time"))
        perf[k] = statistics.mean([t for t in ts if t]) if any(ts) else None
    levels = []
    for k, lv in enumerate(order, 1):
        L = {"k": k, "level": lv, "personas": {}, "groups": {}}
        allr = [r for p in P for r in runs[(p["id"], k)]]
        for p in P:
            L["personas"][p["id"]] = persona_level(runs[(p["id"], k)], perf[k])
        for g in GROUPS:
            ms = [L["personas"][p["id"]] for p in P if pg[p["id"]] == g and "DI2" in L["personas"][p["id"]]]
            L["groups"][g] = {"DI1": statistics.mean(m["DI1"] for m in ms) if ms else None,
                              "DI2": statistics.mean(m["DI2"] for m in ms) if ms else None,
                              "learn_s": statistics.mean(m["learn_s"] for m in ms) if ms else None,
                              "clear": statistics.mean(m["clear_rate"] for m in ms) if ms else None}
        spots = collections.Counter()
        for r in allr:
            if r["result"] in ("lost", "crash"):
                continue
            for x in r["fails"]:
                pos = r.get("spot_pos", {}).get(x["spot"], [x["x"], x["y"]])
                spots[beat_name(lv, pos[0])] += 1
        tot = sum(spots.values())
        L["failures"] = tot
        L["worst_spot"] = spots.most_common(1)[0] if spots else ("-", 0)
        L["worst_share"] = (L["worst_spot"][1] / tot) if tot else 0.0
        L["lost_rate"] = sum(r["result"] in ("lost", "crash") for r in allr) / max(1, len(allr))
        L["runs"] = len(allr)
        e = L["personas"].get("elsa6", {})
        L["elsa_clear"] = e.get("clear_rate")
        L["fresh_starts"] = sum(1 for r in allr if (r.get("carry_in_full") or {}).get("fresh"))
        L["lab_walks"] = sum(r.get("lab_walks", 0) for r in allr) / max(1, len(allr))
        levels.append(L)
    # ---- targets
    checks = {}
    judged = args.groups.split(",")
    for g in GROUPS:
        d = [L["groups"][g]["DI2"] for L in levels]
        if any(v is None for v in d):
            checks[g] = {"pass": False, "why": ["no data"]}
            continue
        why = []
        for i in range(len(d) - 1):
            nxt = max(d[i + 1:i + 3])
            if d[i] > nxt + args.x:
                why.append(f"spike: {NAMES[order[i]]} ({d[i]:.0f}) > next two max ({nxt:.0f}) + {args.x:g}")
        h = len(d) // 2
        first, second = d[:h], d[len(d) - h:]
        if statistics.mean(second) < statistics.mean(first):
            why.append(f"does not climb: second half {statistics.mean(second):.0f} < first half {statistics.mean(first):.0f}")
        if d[-1] < d[0]:
            why.append(f"last level ({d[-1]:.0f}) easier than the first ({d[0]:.0f})")
        checks[g] = {"pass": not why, "why": why, "judged": g in judged}
    t1 = all(checks[g]["pass"] for g in judged)
    t2 = all(L["worst_share"] <= args.spot_max or L["failures"] < 20 for L in levels)
    t3 = all((L["elsa_clear"] or 0) >= args.elsa_min for L in levels)
    t4 = all(L["lost_rate"] < args.lost_max for L in levels)
    res = {"order": order, "seeds": args.seeds, "levels": levels, "sawtooth": checks,
           "targets": {"T1 sawtooth": t1, "T2 spot share": t2, "T3 Elsa clears": t3, "T4 lost runs": t4},
           "params": {"x": args.x, "spot_max": args.spot_max, "elsa_min": args.elsa_min, "lost_max": args.lost_max, "groups": judged}}
    return res


def report(res):
    order = res["order"]
    print("order:", " > ".join(NAMES[l] for l in order), f"({res['seeds']} seeds x 8 personas)")
    print(f"{'level':18s} " + " ".join(f"{g:>13s}" for g in GROUPS) + "   learn s k/p/r   worst spot (share)          Elsa  lost")
    for L in res["levels"]:
        g = L["groups"]
        di = " ".join(f"{g[x]['DI2']:6.1f} ({g[x]['DI1']:4.0f})" if g[x]["DI2"] is not None else f"{'-':>13s}" for x in GROUPS)
        ls = "/".join(f"{g[x]['learn_s']:.0f}" if g[x]["learn_s"] is not None else "-" for x in GROUPS)
        ws = f"{L['worst_spot'][0][:20]} ({100 * L['worst_share']:.0f}%)"
        el = "-" if L["elsa_clear"] is None else f"{100 * L['elsa_clear']:.0f}%"
        print(f"{L['k']} {NAMES[L['level']]:16s} {di}   {ls:13s}   {ws:27s} {el:>5s} {100 * L['lost_rate']:4.1f}%")
    print("DI v2 per group (DI v1 in brackets)")
    for g, c in res["sawtooth"].items():
        tag = "" if c.get("judged") else " (not judged)"
        print(f"sawtooth {g}: {'PASS' if c['pass'] else 'FAIL'}{tag}" + ("" if c["pass"] else ": " + "; ".join(c["why"])))
    for t, ok in res["targets"].items():
        print(f"{t}: {'PASS' if ok else 'FAIL'}")


def chart(res, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    GC = {"kids": "#d1495b", "parents": "#2e86ab", "retro": "#5b8e3e"}
    lv = res["levels"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    xs = range(len(lv))
    for g in GROUPS:
        ax[0].plot(xs, [L["groups"][g]["DI2"] for L in lv], "-o", color=GC[g], lw=2, label=f"{g} DI v2")
        ax[0].plot(xs, [L["groups"][g]["DI1"] for L in lv], "--", color=GC[g], lw=1, alpha=0.6, label=f"{g} DI v1")
    labels = [f"{L['k']} {NAMES[L['level']]}" for L in lv]
    for a in ax:
        a.set_xticks(list(xs)); a.set_xticklabels(labels, rotation=30, ha="right", fontsize=8); a.grid(alpha=0.3)
    ax[0].set_ylabel("difficulty index"); ax[0].legend(fontsize=7, ncol=2); ax[0].set_title("Difficulty along the order (whole-game mode)")
    ax[1].bar([x - 0.2 for x in xs], [100 * L["worst_share"] for L in lv], 0.4, color="#888", label="worst spot share %")
    ax[1].bar([x + 0.2 for x in xs], [100 * (L["elsa_clear"] or 0) for L in lv], 0.4, color="#d1495b", label="Elsa clear %")
    ax[1].axhline(35, color="#444", ls=":", lw=1); ax[1].axhline(50, color="#d1495b", ls=":", lw=1)
    ax[1].set_ylim(0, 105); ax[1].legend(fontsize=8); ax[1].set_title("Worst spot share and Elsa's clear rate")
    fig.suptitle(" > ".join(NAMES[l] for l in res["order"]))
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--groups", default="kids,parents")
    ap.add_argument("--x", type=float, default=8.0)
    ap.add_argument("--spot-max", type=float, default=0.35)
    ap.add_argument("--elsa-min", type=float, default=0.5)
    ap.add_argument("--lost-max", type=float, default=0.05)
    ap.add_argument("--analyse-only", action="store_true")
    a = ap.parse_args()
    order = a.order.split(",")
    name = a.name or "_".join(order)
    out = a.out or f"/home/claude/out/r6-lab/curve_{name}"
    if not a.analyse_only:
        print(f"whole-game mode: {len(order)} levels x 8 personas x {a.seeds} seeds -> {out}", flush=True)
        run_campaign(order, out, a.seeds, a.jobs)
    res = analyse(order, out, a)
    json.dump(res, open(os.path.join(out, "curve.json"), "w"), indent=1, default=str)
    try:
        chart(res, os.path.join(out, f"curve_{name}.png"))
    except Exception as e:                                   # (charts are a nice-to-have)
        print("chart:", e)
    report(res)
    sys.exit(0 if all(res["targets"].values()) else 1)


if __name__ == "__main__":
    main()
