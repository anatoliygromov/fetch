"""tools/asset_qa.py: the asset QA gate (23 Oct 2026; docs/asset_qa.md).

Every asset is checked AS THE GAME DRAWS IT (file -> load-time fade -> the layer's look shader, from
tools/measure_layers.py) and in DETAIL (the pixels themselves). A FAIL means the asset is not shown to the owner.

  python3 -I tools/asset_qa.py --all [--json out.json]            every asset the game uses (+ batch 1 on r8/art)
  python3 -I tools/asset_qa.py town_house1 goose                    named assets
  python3 -I tools/asset_qa.py --file new.png --layer play --level dt [--fade 0.28] [--building] [--frames 34x34]
                                                                    a new file, before it goes into the game

Checks (id: what fails)
  alpha      semi-transparent pixels (alpha must be 0 or 255)
  blotches   2-24 px patches of a near colour inside a fill (dirty plaster); approved pieces have none
  slot       batch 1 / new art: the size its hook expects (docs/art_hooks_r8.md)
  noise      single pixels a shade off the fill around them (dirt): fail over 1 % (props, buildings), warn over 0.3 %
  stray      lone pixels (no 8-neighbour of the same colour) over the limit: 2 % buildings, 5 % others (warn 3 %)
  specks     opaque bits of 1-4 px floating free of the body
  pinholes   transparent holes of 1-4 px inside the body
  outline    play pieces and characters: silhouette edge pixels lighter than the 1 px dark outline (< 98 % dark)
  decor-ink  decoration on a far or back layer outlined like an obstacle (> 30 % dark edge, warn)
  colours    more colours than the layer allows
  ladder     on-screen lightness: darker than the layer's darkest, or more contrast than it allows (front: too light)
  windows    buildings: every window on a storey must be the same pixels; panes the same size, filled, aligned
  frames     sheets: a colour missing in one frame of a row (a lost eye, a hand), the feet moving, colours used in
             a single frame only (flicker), a sudden size jump, plus specks / pinholes / outline per frame
"""
import sys, os, re, json, argparse
from collections import Counter, defaultdict
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure_layers as ML                                       # registry A, shader presets S, shade(), fades

ROOT, ART = ML.ROOT, ML.ART
W601 = np.array([0.299, 0.587, 0.114])

# the layer ladder (docs/layer_ladder.md): darkest on screen (10th pct), max contrast (p90 - p10), max colours
LADDER = {
    "clouds": dict(p10=185, contrast=70, colours=5),
    "city":   dict(p10=145, contrast=35, colours=8),
    "shore":  dict(p10=125, contrast=60, colours=12),
    "mid":    dict(p10=105, contrast=85, colours=14),
    "water":  dict(p10=75, contrast=160, colours=20),
    "back":   dict(p10=80, contrast=120, colours=20),
    "ground": dict(colours=20),
    "play":   dict(colours=20, outline=True),
    "char":   dict(colours=24, outline=True),
    "front":  dict(median_max=40, contrast=40, colours=8),
}
# animated sheets: frame width x height (from the code that cuts them)
FRAMES = {
    "pepper": (60, 52), "girl": (66, 66), "cat": (48, 48), "goose": (34, 34), "gull": (36, 44),
    "park_keeper_cart": (82, 82), "park_keeper_winch": (80, 80), "rowboat": (182, 96), "mia_throw": (66, 66),
}
ROLL = ("road_cyclist1_roll", "road_cyclist2_roll")              # 4 frames side by side (drawn: Rd.art().riders)
# what the game never draws (loaded but unused, or replaced in the played level): not checked
NOT_DRAWN = {"cyclist1", "cyclist2", "cyclist1_roll", "cyclist2_roll", "town_spout"}
# measure_layers' layer is the prop's map layer; the look the game draws it with can differ (stage.lua: decoration on
# Pepper's line takes the back look)
LAYER_FIX = {"pier": "back"}
# art drawn in more than one level: the ladder is checked under each level's look
SHARED = {"skyline": ("rw", "cp", "dt"), "water": ("rw", "cp"), "bench": ("rw", "cp", "dt"), "bin": ("rw", "cp", "dt"),
          "lamp_post": ("rw", "cp", "dt"), "park_log": ("rw", "cp"),
          **{f"cloud{i}": ("rw", "cp", "dt") for i in range(1, 9)}}
# pieces cut into tiles: their left and right columns are joins, not silhouette
TILES = {"rail_bg_left", "rail_bg_unit", "rail_bg_end", "pavement", "road", "park_ground", "town_ground", "water"}
# slots (docs/art_hooks_r8.md): width, height, tolerance on each (0 = exact). Batch 1 files are named differently
# from their hooks: HOOK says which game file each one becomes
SLOTS = {"cargobike": (96, 76, 0, 0), "cargobike_pedal": (768, 76, 0, 0), "mia_throw": (528, 66, 0, 0),
         "cyclist_a_84": (76, 76, 8, 8), "cyclist_b_84": (76, 76, 8, 8), "cyclist_a_92": (76, 76, 8, 8), "cyclist_b_92": (76, 76, 8, 8),
         "roof_gable": (122, 80, 0, 20), "roof_loggia": (122, 48, 0, 12), "roof_gallery88": (90, 32, 0, 8),
         "roof_gallery72": (74, 32, 0, 8), "roof_chimney": (18, 46, 0, 0), "roof_dormer": (58, 36, 0, 9),
         "footbridge": (162, 52, 0, 13), "house_tall_a": (80, 240, 0, 0), "house_tall_b": (88, 240, 0, 0),
         "house_tall_c": (96, 240, 0, 0), "tram_vintage": (300, 130, 30, 15)}
HOOK = {"cargobike": "cargo_bike", "cargobike_pedal": "cargo_bike_pedal", "mia_throw": "girl_throw",
        "cyclist_a_84": "cyclist_adult1", "cyclist_b_84": "cyclist_adult2", "roof_gable": "town_roof_gable",
        "roof_loggia": "town_roof_loggia", "roof_gallery88": "town_roof_gallery88", "roof_gallery72": "town_roof_gallery72",
        "roof_chimney": "town_roof_chimney", "roof_dormer": "town_roof_dormer", "roof_ledge32": "town_roof_ledge",
        "footbridge": "town_footbridge", "house_tall_a": "town_front_tall1", "house_tall_b": "town_front_tall2",
        "house_tall_c": "town_front_tall3", "facades_square": "town_row", "spire_riddarholmen": "town_spire",
        "roof_awning56": "(no hook: the kit has no awning)"}
BUILDINGS = {"town_house1", "town_house2", "town_house3", "town_facades", "town_row", "building", "cafe", "gable",
             "facades_square", "house_tall_a", "house_tall_b", "house_tall_c"}
ORGANIC = {"tree", "tree_far", "tree_near", "park_tree1", "park_tree2", "park_oak", "park_willow", "park_willow_tall",
           "park_hedge", "park_bush", "park_leaves", "park_leaves_flat", "park_treeline", "skyline", "far_shore_bridge"}
FROZEN = {"pepper"}                                               # Pepper's files are frozen: report only
# owner-approved exceptions (check ids that only warn for these)
EXCEPT = {"cafe": {"colours"}, "gable": {"colours"}, "pavement": {"ladder"},
          "bone": {"outline"}, "bone_gold": {"outline"},                   # pickups: white, unoutlined by design
          "lamp_post": {"decor-ink"}, "kiosk_kaffe": {"decor-ink"}, "kiosk_glass": {"decor-ink"}}   # the approved River Walk set


# ------------------------------------------------------------------------------------------------ small tools
def label(mask, conn8=True):
    """connected components (pure numpy + python, no scipy): returns (labels, n)"""
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32); n = 0
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] if conn8 else [(-1, 0), (1, 0), (0, -1), (0, 1)]
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]: continue
        n += 1; lab[y0, x0] = n; st = [(y0, x0)]
        while st:
            y, x = st.pop()
            for dy, dx in nb:
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n; st.append((yy, xx))
    return lab, n

def keys(rgb, a):
    k = (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2]
    return np.where(a, k, -1)

def lone_mask(key, a):
    h, w = key.shape
    pad = np.pad(key, 1, constant_values=-2)
    same = np.zeros_like(a)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy: same |= pad[1+dy:1+dy+h, 1+dx:1+dx+w] == key
    return a & ~same

def edge_mask(a):
    pa = np.pad(a, 1)
    return a & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])

def as_drawn(rgb01, a, lvl, layer, fade):
    """RGB 0-1 as on screen: the load-time fade towards the level's haze for the layer, then the layer's look shader"""
    out = ML.fade_to(rgb01.copy(), fade, lvl, layer if layer != "char" else None)
    if layer and layer != "char":
        flat = ML.shade(out[a], ML.S[lvl][layer]); out[a] = flat
    return out

def pts(mask, limit=400):
    ys, xs = np.nonzero(mask)
    return [[int(x), int(y)] for y, x in list(zip(ys, xs))[:limit]]


# ------------------------------------------------------------------------------------------------ the checks
class Report:
    def __init__(self, name, meta):
        self.name, self.meta, self.checks, self.info = name, meta, [], {}
    def add(self, cid, sev, msg, pixels=None, **extra):
        if cid in EXCEPT.get(self.name, ()): sev, msg = "note", msg + " (owner-approved exception)"
        if self.name in FROZEN and sev == "fail": sev, msg = "warn", msg + " (frozen file: report only)"
        self.checks.append(dict(id=cid, sev=sev, msg=msg, pixels=pixels or [], **extra))
    def merged(self):
        """one line per check: the same finding in many frames becomes 'in N frames (r1c1, ...)'"""
        out, groups = [], {}
        for c in self.checks:
            m = re.match(r"(.*) \(frame row (\d+), col (\d+)\)(.*)", c["msg"])
            if not m: out.append(c); continue
            k = (c["id"], c["sev"])
            if k not in groups:
                groups[k] = dict(id=c["id"], sev=c["sev"], msg=re.sub(r"\d+", "#", m.group(1) + m.group(4)), pixels=[], frames=[], first=m.group(1) + m.group(4))
                out.append(groups[k])
            g = groups[k]; g["pixels"] += c["pixels"]; g["frames"].append(f"r{m.group(2)}c{m.group(3)}")
        for g in groups.values():
            f = g.pop("frames"); first = g.pop("first")
            g["msg"] = first + f" in {len(f)} frame(s), first {f[0]}" + (": " + ", ".join(f[1:13]) + (" ..." if len(f) > 13 else "") if len(f) > 1 else "")
        return out
    def verdict(self):
        s = {c["sev"] for c in self.checks}
        return "FAIL" if "fail" in s else ("WARN" if "warn" in s else "PASS")
    def json(self):
        return dict(name=self.name, verdict=self.verdict(), **self.meta, info=self.info, checks=self.merged())

def body_checks(r, rgb, a, ox=0, oy=0, where="", strict=True):
    """specks, pinholes (on one frame or a whole still); ox/oy shift pixel positions into sheet space"""
    lab, n = label(a, True)
    if n > 1:
        sizes = np.bincount(lab.ravel())[1:]
        big = sizes.max()
        small = [i + 1 for i, s in enumerate(sizes) if s <= 8 and big >= 40 and i + 1 != sizes.argmax() + 1]
        if small:
            m = np.isin(lab, small); p = [[x + ox, y + oy] for x, y in pts(m)]
            r.add("specks", "fail", f"{len(small)} floating speck(s) of 1-8 px{where}", p)
    hole = ~a
    hl, hn = label(hole, False)
    if hn:
        border = set(np.unique(np.concatenate([hl[0], hl[-1], hl[:, 0], hl[:, -1]]))) - {0}
        sizes = np.bincount(hl.ravel())
        lumr = rgb @ W601
        pin = []
        for i in range(1, hn + 1):
            if i in border or sizes[i] > 4: continue
            m = hl == i
            pm = np.pad(m, 1)
            ring = (pm[:-2, 1:-1] | pm[2:, 1:-1] | pm[1:-1, :-2] | pm[1:-1, 2:]) & a
            if ring.any() and (lumr[ring] < 70).mean() >= 0.7: continue      # an outlined gap (between slats): drawn on purpose
            pin.append(i)
        if pin:
            m = np.isin(hl, pin); p = [[x + ox, y + oy] for x, y in pts(m)]
            r.add("pinholes", "fail" if strict else "warn", f"{len(pin)} pinhole(s) inside the shape{where}", p)

def blotch_check(r, rgb255, a, strict=True):
    """blotchy fill: small patches (2-24 px) of one colour sitting inside a near colour (distance < 45). Painted or
    filtered art leaves them (the 'dirty plaster'); approved pieces (bench, bin, lamp, kiosk, planter) have none."""
    key = keys(rgb255, a); flagged = []; n = 0
    for k in np.unique(key[a]):
        lab, c = label(key == k, True)
        if not c: continue
        sizes = np.bincount(lab.ravel())
        for i in range(1, c + 1):
            if not (2 <= sizes[i] <= 24): continue
            mm = lab == i
            ys_, xs_ = np.nonzero(mm); bh, bw = ys_.max() - ys_.min() + 1, xs_.max() - xs_.min() + 1
            if min(bh, bw) == 1 and max(bh, bw) >= 4: continue        # a drawn 1 px line (a panel line, a seam)
            pm = np.pad(mm, 1)
            ring = (pm[:-2, 1:-1] | pm[2:, 1:-1] | pm[1:-1, :-2] | pm[1:-1, 2:]) & ~mm
            rk = key[ring]
            if (rk < 0).any(): continue
            vals, cnt = np.unique(rk, return_counts=True)
            if cnt.max() / cnt.sum() < 0.8: continue
            o = int(vals[cnt.argmax()])
            d = np.sqrt(sum((((o >> sh) & 255) - ((int(k) >> sh) & 255)) ** 2 for sh in (16, 8, 0)))
            if d < 45: n += 1; flagged += pts(mm)
    pct = len(flagged) / max(1, a.sum()) * 100
    r.info["blotches"] = n
    if n and pct > 0.3:
        r.add("blotches", "fail" if strict else "warn", f"{n} blotch(es) of 2-24 px in a near colour ({pct:.1f} % of the art): dirty fill", flagged)
    elif n:
        r.add("blotches", "warn", f"{n} blotch(es) of 2-24 px in a near colour", flagged)

def outline_check(r, rgb255, a, need, cls, ox=0, oy=0, where="", tile=False):
    """the outline is a property of the file, measured on its own pixels (a load-time fade must not hide a gap).
    Not counted: the bottom row (ground contact), a tile's join columns. Front pieces: dark silhouette with a lit rim,
    no rule. Play pieces and characters: complete. Decoration: none (ladder); if one is drawn it must not be broken"""
    if cls == "front": return None
    e = edge_mask(a)
    rows = np.nonzero(a.any(1))[0]
    if len(rows): e[rows.max(), :] = False
    if tile: e[:, 0] = False; e[:, -1] = False
    if not e.any(): return None
    lum = rgb255 @ W601
    dark = e & (lum < 70)
    share = dark.sum() / e.sum() * 100
    gaps = e & ~dark
    p = [[x + ox, y + oy] for x, y in pts(gaps)]
    if need:
        if share < 98: r.add("outline", "fail", f"outline {share:.0f} % dark{where}: {int(gaps.sum())} edge px break it", p)
    elif share >= 80:
        if share < 98:
            r.add("outline", "fail", f"decoration drawn with an outline ({share:.0f} %){where}, broken in {int(gaps.sum())} px: "
                  "redraw it without one (the ladder rule for decoration) or complete it", p)
        elif not where:
            r.add("decor-ink", "warn", f"decoration outlined like an obstacle: {share:.0f} % of its edge is dark")
    elif share > 30 and not where:
        r.add("decor-ink", "warn", f"decoration outlined like an obstacle: {share:.0f} % of its edge is dark")
    return share

def window_check(r, rgb255, a):
    """buildings: find the glass panes, group them into windows, compare windows of one size on one wall pixel by
    pixel (the most common version is the reference; a 1 px shift is reported as a shift). Within a storey a
    difference fails; between storeys of the same wall it warns (a ground floor may differ on purpose)."""
    H, Wd = a.shape
    lum = rgb255 @ W601
    near_clear = ~np.pad(a, 1, constant_values=False)
    nc = np.zeros_like(a)                                          # opaque pixels within 1 px of transparency
    for dy in (0, 1, 2):
        for dx in (0, 1, 2): nc |= near_clear[dy:dy+H, dx:dx+Wd]
    best = None
    for thr in (50, 70, 90, 110, 130):
        g = a & (lum < thr)
        lab, n = label(g, False)
        panes = []
        for k in range(1, n + 1):
            m = lab == k
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
            w, h = x1 - x0 + 1, y1 - y0 + 1
            if not (2 <= w <= 10 and 2 <= h <= 14): continue
            if len(ys) / (w * h) < 0.85: continue                 # glass is a filled rectangle
            if (m & nc).any(): continue                            # not the silhouette's outline (gable diagonals)
            panes.append(dict(x=int(x0), y=int(y0), w=int(w), h=int(h), n=int(len(ys)), k=k))
        if best is None or len(panes) > len(best[1]): best = (thr, panes, lab)
    thr, panes, lab = best
    if len(panes) < 4:
        r.info["windows"] = "no window panes found"; return
    # windows: panes close together (gap <= 4 px both ways)
    panes.sort(key=lambda p: (p["y"], p["x"]))
    used, windows = set(), []
    for i, p in enumerate(panes):
        if i in used: continue
        grp = [i]; used.add(i); changed = True
        while changed:
            changed = False
            for j, q in enumerate(panes):
                if j in used: continue
                for gi in grp:
                    g = panes[gi]
                    if q["x"] <= g["x"] + g["w"] + 4 and g["x"] <= q["x"] + q["w"] + 4 and q["y"] <= g["y"] + g["h"] + 4 and g["y"] <= q["y"] + q["h"] + 4:
                        grp.append(j); used.add(j); changed = True; break
        ps = [panes[g] for g in grp]
        xs0 = min(p["x"] for p in ps); ys0 = min(p["y"] for p in ps)
        xs1 = max(p["x"] + p["w"] for p in ps); ys1 = max(p["y"] + p["h"] for p in ps)
        windows.append(dict(x=xs0 - 1, y=ys0 - 1, w=xs1 - xs0 + 2, h=ys1 - ys0 + 2, panes=ps))
    # the wall each window sits on: the most common colour 3-5 px outside it, coarsely (blotches must not split a wall)
    for w in windows:
        x0, y0, x1, y1 = max(0, w["x"] - 5), max(0, w["y"] - 5), min(Wd, w["x"] + w["w"] + 5), min(H, w["y"] + w["h"] + 5)
        ring = np.ones((y1 - y0, x1 - x0), bool)
        ix0, iy0 = w["x"] - 2 - x0, w["y"] - 2 - y0
        ring[max(0, iy0):max(0, iy0) + w["h"] + 4, max(0, ix0):max(0, ix0) + w["w"] + 4] = False
        px = rgb255[y0:y1, x0:x1][ring & a[y0:y1, x0:x1]]
        w["wall"] = Counter(map(tuple, (px // 40).tolist())).most_common(1)[0][0] if len(px) else None
    # storeys: same wall, tops within 4 px
    windows.sort(key=lambda w: (w["y"], w["x"]))
    storeys = []
    for w in windows:
        for st in storeys:
            if abs(st[0]["y"] - w["y"]) <= 4 and st[0]["wall"] == w["wall"]: st.append(w); break
        else: storeys.append([w])
    def crop(w, cw, ch, dx=0, dy=0):
        x0, y0 = w["x"] + dx, w["y"] + dy
        if x0 < 0 or y0 < 0 or x0 + cw > Wd or y0 + ch > H: return None
        return np.concatenate([rgb255[y0:y0+ch, x0:x0+cw].reshape(-1, 3), a[y0:y0+ch, x0:x0+cw].reshape(-1, 1)], 1)
    def compare(group):
        """returns per window: (diff px at the best shift, shift, flagged pixels) against the group's reference"""
        sizes = Counter((w["w"], w["h"]) for w in group)
        (cw, ch), _ = sizes.most_common(1)[0]
        same = [w for w in group if (w["w"], w["h"]) == (cw, ch)]
        crops = [crop(w, cw, ch) for w in same]
        valid = [c for c in crops if c is not None]
        if len(valid) < 2: return cw, ch, sizes, {}
        ref = Counter(c.tobytes() for c in valid).most_common(1)[0][0]
        refc = next(c for c in valid if c.tobytes() == ref)
        res = {}
        for w in same:
            bestd = None
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    c = crop(w, cw, ch, dx, dy)
                    if c is None: continue
                    d = np.any(c != refc, 1).reshape(ch, cw)
                    if bestd is None or d.sum() < bestd[0].sum() or (d.sum() == bestd[0].sum() and (dx, dy) == (0, 0)): bestd = (d, dx, dy)
            d, dx, dy = bestd
            fl = [[int(w["x"] + dx + xx), int(w["y"] + dy + yy)] for yy, xx in zip(*np.nonzero(d))]
            if (dx, dy) != (0, 0):                                  # shifted: mark the window's frame
                fl += [[w["x"] + xx, w["y"]] for xx in range(cw)] + [[w["x"] + xx, w["y"] + ch - 1] for xx in range(cw)]
            res[id(w)] = (int(d.sum()), (dx, dy), fl)
        return cw, ch, sizes, res
    flagged, info, fails, warns = [], [], [], []
    for si, st in enumerate(storeys):
        st.sort(key=lambda w: w["x"])
        rec = dict(y=int(st[0]["y"]), windows=[dict(x=w["x"], y=w["y"], w=w["w"], h=w["h"]) for w in st], diffs=[], problems=[])
        if len(st) >= 2:
            cw, ch, sizes, res = compare(st)
            if len(sizes) > 1: rec["problems"].append("window sizes differ: " + ", ".join(f"{a_}x{b_}" for a_, b_ in sizes))
            if len({w["y"] for w in st}) > 1: rec["problems"].append("windows not on one line (tops at y " + ", ".join(map(str, sorted({w["y"] for w in st}))) + ")")
            for w in st:
                d = res.get(id(w))
                rec["diffs"].append(d[0] if d else -1)
                if d and (d[0] or d[1] != (0, 0)):
                    flagged += d[2]
                    rec["problems"].append(f"window at x {w['x']}: " + (f"{d[0]} px differ" if d[0] else "") +
                                           (f"{' and ' if d[0] else ''}shifted {d[1][0]:+d},{d[1][1]:+d} px" if d[1] != (0, 0) else ""))
        for w in st:                                                # inside a window: panes alike and filled
            ps = w["panes"]
            # panes the same size and on one grid (a 2 x 2 window has two rows of panes: each row on one line, each
            # column on one line); before 23 Oct (art/freefix) any second row of panes failed here
            gx, gy = sorted({p["x"] for p in ps}), sorted({p["y"] for p in ps})
            if len({(p["w"], p["h"]) for p in ps}) > 1 or len(ps) != len(gx) * len(gy) or \
               {(p["x"], p["y"]) for p in ps} != {(x_, y_) for x_ in gx for y_ in gy}:
                rec["problems"].append(f"window at x {w['x']}: its panes differ in size or height")
                for p in ps: flagged += [[p["x"] + xx, p["y"]] for xx in range(p["w"])]
            for p in ps:
                if p["n"] < p["w"] * p["h"]:
                    box = lab[p["y"]:p["y"]+p["h"], p["x"]:p["x"]+p["w"]] != p["k"]
                    flagged += [[p["x"] + int(xx), p["y"] + int(yy)] for yy, xx in zip(*np.nonzero(box))]
                    rec["problems"].append(f"window at x {w['x']}: {p['w']*p['h'] - p['n']} speck(s) in the glass")
        if rec["problems"]: fails.append(si)
        info.append(rec)
    # across storeys of one wall: windows of the same size should be the same window
    walls = defaultdict(list)
    for w in windows: walls[w["wall"]].append(w)
    cross = []
    for wall, ws in walls.items():
        if len({w["y"] for w in ws}) < 2: continue
        cw, ch, sizes, res = compare(ws)
        nd = [w for w in ws if id(w) in res and res[id(w)][0]]
        if nd: cross.append(f"{len(nd)} of {len([w for w in ws if id(w) in res])} same-size windows on one wall differ between storeys")
    r.info["windows"] = dict(threshold=thr, storeys=info, cross=cross)
    if fails:
        msgs = [f"storey {si + 1}: " + "; ".join(info[si]["problems"][:3]) for si in fails]
        r.add("windows", "fail", f"{len(fails)} of {len(storeys)} storeys have uneven windows. " + " | ".join(msgs[:4]) + (" ..." if len(msgs) > 4 else ""), flagged)
    if cross: r.add("windows", "warn", "; ".join(cross))

def frame_checks(r, rgb255, a, drawn, fw, fh, need_outline):
    H, Wd = a.shape
    if H % fh or Wd % fw or H < fh or Wd < fw:
        r.add("frames", "fail", f"the sheet ({Wd} x {H}) is not a whole number of {fw} x {fh} frames")
        return
    rows, cols = H // fh, Wd // fw
    key = keys(rgb255, a)
    per = {}
    for ry in range(rows):
        for cx in range(cols):
            sl = (slice(ry*fh, ry*fh+fh), slice(cx*fw, cx*fw+fw))
            fa = a[sl]
            if fa.sum() < 10: continue
            per[(ry, cx)] = dict(a=fa, key=key[sl], cols=set(np.unique(key[sl][fa]).tolist()),
                                 n=int(fa.sum()), bottom=int(np.nonzero(fa.any(1))[0].max()))
    r.info["frames"] = dict(fw=fw, fh=fh, count=len(per))
    # per frame: specks, pinholes, outline
    shares = []
    for (ry, cx), f in per.items():
        sl = (slice(ry*fh, ry*fh+fh), slice(cx*fw, cx*fw+fw))
        body_checks(r, rgb255[sl], f["a"], cx*fw, ry*fh, f" (frame row {ry+1}, col {cx+1})")
        s = outline_check(r, rgb255[sl], f["a"], need_outline, r.meta["layer"], cx*fw, ry*fh, f" (frame row {ry+1}, col {cx+1})")
        if s is not None: shares.append(s)
    # across frames, per row
    lost, flick, jumps, feet = [], [], [], []
    colour_frames = Counter()
    for f in per.values():
        for c in f["cols"]: colour_frames[c] += 1
    for ry in range(rows):
        fr = sorted([(cx, f) for (y, cx), f in per.items() if y == ry])
        if len(fr) < 3: continue
        cnt = Counter()
        for _, f in fr:
            for c in f["cols"]: cnt[c] += 1
        avg = {c: np.mean([(f["key"] == c).sum() for _, f in fr if c in f["cols"]]) for c in cnt}
        common = {c for c, k in cnt.items() if k >= 0.75 * len(fr) and k < len(fr) and avg[c] >= 3}
        for cx, f in fr:
            miss = [c for c in common if c not in f["cols"]]
            if miss:
                lost.append(f"row {ry+1} col {cx+1}: {len(miss)} colour(s) the other frames have")
        bots = [f["bottom"] for _, f in fr]
        if max(bots) - min(bots) > 1: feet.append(f"row {ry+1}: lowest pixel moves {max(bots) - min(bots)} px")
        for (c0, f0), (c1, f1) in zip(fr, fr[1:]):
            if abs(f1["n"] - f0["n"]) > 0.25 * max(f0["n"], f1["n"]): jumps.append(f"row {ry+1}: col {c0+1} -> {c1+1} size {f0['n']} -> {f1['n']} px")
    singles = [c for c, k in colour_frames.items() if k == 1]
    fl_px = []
    for c in singles:
        m = key == c
        if m.sum() <= 3: fl_px += pts(m); flick.append(c)
    if lost: r.add("frames", "warn", "a colour missing in one frame (a lost eye or hand; fine if it is a blink): " + "; ".join(lost[:5]) + (" ..." if len(lost) > 5 else ""))
    if flick: r.add("frames", "fail", f"{len(flick)} colour(s) used in one frame only, 3 px or less (flicker)", fl_px)
    if feet: r.add("frames", "warn", "feet not anchored (fine in a jump or flight): " + "; ".join(feet[:4]))
    if jumps: r.add("frames", "warn", "size jumps between frames: " + "; ".join(jumps[:3]))
    if shares:
        r.info["outline_min"] = round(min(shares))
        if not need_outline and 30 < np.mean(shares) < 80:
            r.add("decor-ink", "warn", f"decoration outlined like an obstacle: {np.mean(shares):.0f} % of its edge is dark")

def noise_mask(rgb255, a, lone):
    """lone pixels that are dirt, not detail: their colour is near (< 45) the colour most of their neighbours have"""
    H, Wd = a.shape
    key = keys(rgb255, a); out = np.zeros_like(a)
    for y, x in zip(*np.nonzero(lone)):
        nb = key[max(0, y-1):y+2, max(0, x-1):x+2].ravel()
        nb = nb[(nb >= 0) & (nb != key[y, x])]
        if len(nb) < 5: continue
        k, c = Counter(nb.tolist()).most_common(1)[0]
        if c < 4: continue
        d = np.sqrt(sum((((k >> sh) & 255) - ((int(key[y, x]) >> sh) & 255)) ** 2 for sh in (16, 8, 0)))
        if d < 45: out[y, x] = True
    return out

def check(name, path, lvl, layer, fade, building=False, frames=None, levels=None):
    im = np.array(Image.open(path).convert("RGBA"))
    rgb255 = im[..., :3].astype(int); alpha = im[..., 3]
    a = alpha > 127
    cls = "char" if layer is None else layer
    meta = dict(file=os.path.relpath(path, ROOT) if path.startswith(ROOT) else path, level=lvl, layer=cls, fade=fade,
                w=int(im.shape[1]), h=int(im.shape[0]), building=bool(building), frames=frames)
    r = Report(name, meta)
    drawn = as_drawn(rgb255 / 255.0, a, lvl, layer, fade)
    lum = (drawn[a] @ W601) * 255
    key = keys(rgb255, a)
    ncol = len(np.unique(key[a]))
    lone = lone_mask(key, a)
    lone_pct = lone.sum() / max(1, a.sum()) * 100
    p10, med, p90 = (float(np.percentile(lum, q)) for q in (10, 50, 90))
    r.info.update(colours=ncol, lone=round(lone_pct, 1), p10=round(p10), median=round(med), p90=round(p90))
    row = LADDER.get(cls, {})
    # alpha
    semi = ((alpha > 2) & (alpha < 253)).sum()
    if semi: r.add("alpha", "fail", f"{semi} semi-transparent pixels", pts((alpha > 2) & (alpha < 253)))
    # slot (batch 1 hooks)
    if name in SLOTS:
        sw, sh, tw, th = SLOTS[name]
        if abs(im.shape[1] - sw) > tw or abs(im.shape[0] - sh) > th:
            r.add("slot", "fail", f"{im.shape[1]} x {im.shape[0]} px, its slot is {sw}" + (f"±{tw}" if tw else "") + f" x {sh}" + (f"±{th}" if th else "") +
                  (f" (game file {HOOK[name]})" if name in HOOK else ""))
    if name in HOOK: r.info["hook"] = HOOK[name]
    # noise: stray pixels that are dirt (a near colour inside a fill), not detail
    noise = noise_mask(rgb255, a, lone)
    npct = noise.sum() / max(1, a.sum()) * 100
    r.info["noise"] = round(npct, 1)
    if npct > 1.0 and cls not in ("char", "ground") and name not in ORGANIC:
        r.add("noise", "fail", f"{int(noise.sum())} dirt pixels ({npct:.1f} %): single pixels a shade off the fill around them", pts(noise, 2000))
    elif npct > 0.3:
        r.add("noise", "warn", f"{int(noise.sum())} dirt pixels ({npct:.1f} %): single pixels a shade off the fill around them", pts(noise, 2000))
    # stray pixels
    lim = 2 if building else 5
    if lone_pct > lim: r.add("stray", "fail", f"{lone_pct:.1f} % lone pixels (limit {lim} %)", pts(lone, 2000))
    elif lone_pct > 3 and not building: r.add("stray", "warn", f"{lone_pct:.1f} % lone pixels (aim under 3 %)", pts(lone, 2000))
    # colours
    if "colours" in row and ncol > row["colours"]:
        r.add("colours", "fail", f"{ncol} colours, the {cls} layer allows {row['colours']}")
    # the ladder (on-screen lightness), under every level's look the art is drawn in
    if "p10" in row:
        for lv in (levels or (lvl,)):
            fl = ML.fade_in(name, lv, layer) if (fade and lv != lvl) else fade   # (shared art: each level's amount)
            dl = as_drawn(rgb255 / 255.0, a, lv, layer, fl)
            q10 = float(np.percentile((dl[a] @ W601) * 255, 10))
            if q10 < row["p10"] - 2:
                r.add("ladder", "fail", f"darkest {q10:.0f} on screen in {lv}, the {cls} layer's darkest is {row['p10']}", pts(a & ((dl @ W601) * 255 < row["p10"]), 600))
    if "contrast" in row and p90 - p10 > row["contrast"] + 3:
        r.add("ladder", "warn", f"contrast {p90 - p10:.0f}, the {cls} layer allows {row['contrast']}")
    if "median_max" in row and med > row["median_max"]:
        r.add("ladder", "fail", f"median {med:.0f}, the front layer must be {row['median_max']} or darker")
    # body, outline, frames, windows
    need = bool(row.get("outline"))
    organic = name in ORGANIC or cls in ("clouds", "water")
    strict = cls in ("play", "char") or building
    blotch_check(r, rgb255, a, strict=not organic and cls not in ("char", "ground"))   # fur, cloth, cobbles: warn only
    if frames:
        frame_checks(r, rgb255, a, drawn, frames[0], frames[1], need)
    else:
        body_checks(r, rgb255, a, strict=strict)
        if cls not in ("ground", "water"):
            s = outline_check(r, rgb255, a, need, cls, tile=name in TILES)
            if s is not None: r.info["outline"] = round(s)
    if building: window_check(r, rgb255, a)
    return r


# ------------------------------------------------------------------------------------------------ the registry
def registry():
    """name -> (path, level, layer, fade, building, frames): the game's assets as measure_layers maps them"""
    out = {}
    r8 = ML.r8_dir()
    for g, n, p, lvl, layer, fade in ML.A:
        p = p.replace(ML.R8, r8)
        if not os.path.exists(p): continue
        if n in NOT_DRAWN or n in out: continue
        out[n] = dict(path=p, level=lvl, layer=LAYER_FIX.get(n, layer), fade=fade, group=g, building=n in BUILDINGS,
                      frames=FRAMES.get(n), levels=SHARED.get(n))
    # pieces measure_layers does not list (animated sheets, cyclists' wheels, small props)
    extra = [("park_keeper_cart", "cp", "play", 0.0), ("rowboat", "rw", "play", 0.0), ("park_leaves_flat", "cp", "play", 0.0),
             ("bone", "rw", None, 0.0), ("bone_gold", "rw", None, 0.0)]
    for n, lvl, layer, fade in extra:
        p = os.path.join(ART, "scene", n + ".png")
        if os.path.exists(p) and n not in out:
            out[n] = dict(path=p, level=lvl, layer=layer, fade=fade, group="Extra", building=False, frames=FRAMES.get(n), levels=None)
    for n in ROLL:
        p = os.path.join(ART, "scene", n + ".png")
        if os.path.exists(p):
            w, h = Image.open(p).size
            out[n] = dict(path=p, level="rw", layer="play", fade=0.0, group="River Walk", building=False, frames=(w // 4, h), levels=None)
    for n in ("cyclist_a_84_pedal", "cyclist_b_84_pedal", "cyclist_a_92_pedal", "cyclist_b_92_pedal", "cargobike_pedal"):
        p = os.path.join(r8, n + ".png"); s = os.path.join(r8, n.replace("_pedal", "") + ".png")
        if os.path.exists(p) and os.path.exists(s):
            w, h = Image.open(s).size
            out[n] = dict(path=p, level="dt" if "cargo" in n else "rw", layer="play", fade=0.0, group="Batch 1 (rejected)", building=False, frames=(w, h), levels=None)
    for n in ("roof_ledge48", "roof_ledge64"):
        p = os.path.join(r8, n + ".png")
        if os.path.exists(p): out[n] = dict(path=p, level="dt", layer="play", fade=0.0, group="Batch 1 (rejected)", building=False, frames=None, levels=None)
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*"); ap.add_argument("--all", action="store_true"); ap.add_argument("--json")
    ap.add_argument("--file"); ap.add_argument("--layer", default="play"); ap.add_argument("--level", default="rw")
    ap.add_argument("--fade", type=float, default=0.0); ap.add_argument("--building", action="store_true")
    ap.add_argument("--frames", help="WxH of one frame for a sheet")
    o = ap.parse_args()
    reps = []
    if o.file:
        fr = tuple(int(v) for v in o.frames.split("x")) if o.frames else None
        layer = None if o.layer == "char" else o.layer
        reps.append(check(os.path.splitext(os.path.basename(o.file))[0], os.path.abspath(o.file), o.level, layer, o.fade, o.building, fr))
    else:
        reg = registry()
        names = list(reg) if o.all else o.names
        for n in names:
            if n not in reg: print("unknown asset:", n, file=sys.stderr); continue
            d = reg[n]
            rep = check(n, d["path"], d["level"], d["layer"], d["fade"], d["building"], d["frames"], d.get("levels"))
            rep.meta["group"] = d["group"]; reps.append(rep)
    out = [r.json() for r in reps]
    if o.json: json.dump(out, open(o.json, "w"), indent=1)
    nf = 0
    for r in out:
        nf += r["verdict"] == "FAIL"
        print(f"{r['verdict']:4}  {r['name']:22} {r['layer']:6} {r['w']:4}x{r['h']:<4}  " +
              " | ".join(f"{c['id']}: {c['msg']}" for c in r["checks"] if c["sev"] in ("fail", "warn")))
    print(f"\n{len(out)} assets: {sum(r['verdict']=='PASS' for r in out)} PASS, {sum(r['verdict']=='WARN' for r in out)} WARN, {nf} FAIL")
    sys.exit(1 if nf else 0)

if __name__ == "__main__":
    main()
