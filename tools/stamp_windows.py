"""Stamp windows (art/freefix): every window of one size on a storey (or, --across-storeys, on a wall) becomes the
same pixels, on the storey's grid. Buildings drawn with flat glass (the plaza houses). No resize, no new colours,
alpha untouched.

  python3 -I tools/stamp_windows.py src.png dst.png [--across-storeys [--near]] [--no-grid] [--no-equal] [--no-heavy]
                                    [--keep-glass] [--grow N] [--skip x,y ...]

1. Windows: tools/asset_qa.py's window detection (glass panes grouped into windows). Each window grows to its outer
   box: the frame, reveal and sill around the glass (pixels not near the wall colour, 4-connected to the glass, at
   most --grow px out, default 3). Detections inside one window merge.
2. Groups: same wall colour and storey (tops within 4 px), then the same glass size (1 px off counts as the same: a
   stray pixel). --across-storeys: one group per wall and size; --near: sizes 1 px apart on other storeys too.
3. The stamp box: the glass size plus the widest frame margins of the group (a sill 1 px longer is still covered).
   Alignment: each window is matched to the group at shifts of up to 2 px; the best shift is where it really is.
4. The reference: per pixel, the colour most windows of the group have (ties: the window nearest the others). Then
   cleaned (not with --keep-glass): inside the glass area every pixel is glass (the most common glass colour: no
   specks, no streaks) or a glazing bar (a row or column at least 75 % not glass); the bars move so the panes are
   equal when the glass divides evenly (a single bar may become 2 px for that, unless --no-heavy); each side of each
   ring around the glass (reveal, frame, sill) takes its majority colour (the box's outermost ring is left as it is).
5. The grid: within a storey the windows take the storey's most common top; 3 or more windows on a storey whose
   spacing is even to within 1 px are put on the exact spacing; --across-storeys also lines up windows in a column.
   No window moves more than 1 px.
6. Stamp: the reference goes into each window's grid position; what was window before and is not now (a 1 px shift)
   takes the wall colour. A line that runs on through the box's border (a cornice) keeps its border pixel. Pixels
   outside the window boxes are never changed; a window whose box touches transparency is left alone.

Not for painted glass (reflections, two-tone glass: cafe, gable, town_facades): the glass clean flattens it and the
detection splits the windows. Look at the result at 5x before keeping it.
"""
import sys, os, argparse
from collections import Counter
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_qa as Q

W601 = Q.W601

def dist(c0, c1): return float(np.sqrt(((np.asarray(c0, float) - np.asarray(c1, float)) ** 2).sum()))

def detect(rgb, a):
    r = Q.Report("x", dict(layer="back"))
    Q.window_check(r, rgb, a)
    w = r.info.get("windows")
    if not isinstance(w, dict): return None, []
    return w["threshold"], [dict(x=v["x"], y=v["y"], w=v["w"], h=v["h"]) for st in w["storeys"] for v in st["windows"]]

def ring_colour(rgb, a, x0, y0, x1, y1, r0=3, r1=5):
    """the most common exact colour 3-5 px outside the box (x1, y1 exclusive)"""
    H, W = a.shape
    X0, Y0, X1, Y1 = max(0, x0 - r1), max(0, y0 - r1), min(W, x1 + r1), min(H, y1 + r1)
    m = np.zeros((H, W), bool); m[Y0:Y1, X0:X1] = True
    m[max(0, y0 - r0 + 1):min(H, y1 + r0 - 1), max(0, x0 - r0 + 1):min(W, x1 + r0 - 1)] = False
    px = rgb[m & a]
    if not len(px): return None
    return tuple(Counter(map(tuple, px.tolist())).most_common(1)[0][0])

def outer_box(rgb, a, w, wall, grow=3, tol=45):
    """the window's outer box: non-wall pixels 4-connected to the glass box, at most `grow` px out"""
    H, W = a.shape
    x0, y0, x1, y1 = w["x"], w["y"], w["x"] + w["w"], w["y"] + w["h"]
    X0, Y0, X1, Y1 = max(0, x0 - grow), max(0, y0 - grow), min(W, x1 + grow), min(H, y1 + grow)
    sub = rgb[Y0:Y1, X0:X1].astype(float)
    nonwall = a[Y0:Y1, X0:X1] & (np.sqrt(((sub - np.array(wall, float)) ** 2).sum(2)) >= tol)
    seen = np.zeros_like(nonwall)
    seen[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
    st = list(zip(*np.nonzero(seen)))
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < seen.shape[0] and 0 <= xx < seen.shape[1] and nonwall[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True; st.append((yy, xx))
    ys, xs = np.nonzero(seen)
    return [int(xs.min() + X0), int(ys.min() + Y0), int(xs.max() + X0 + 1), int(ys.max() + Y0 + 1)]

def crop(img, x, y, w, h):
    H, W = img.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H: return None
    return img[y:y + h, x:x + w]

def consensus(crops, order):
    """per pixel the most common value; ties go to the crop listed first in `order`"""
    st = np.stack(crops)                                            # n, h, w, 4
    n, h, w, _ = st.shape
    k = (st[..., 0].astype(np.int64) << 24) | (st[..., 1].astype(np.int64) << 16) | (st[..., 2].astype(np.int64) << 8) | st[..., 3]
    out = np.empty((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            c = Counter(k[:, y, x].tolist()); best = max(c.values())
            v = next(k[i, y, x] for i in order if c[k[i, y, x]] == best)
            out[y, x] = ((v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, v & 255)
    return out

def clean_reference(ref, thr, equal=True, heavy=True):
    """glass area: glass colour or mullion; mullions moved for equal panes. Returns (ref, notes)"""
    rgb = ref[..., :3].astype(int); a = ref[..., 3] > 127
    lum = rgb @ W601
    dark = a & (lum < thr)
    lab, n = Q.label(dark, False)
    if not n: return ref, ["no glass"]
    sizes = np.bincount(lab.ravel())
    glass = np.isin(lab, [i for i in range(1, n + 1) if sizes[i] >= 2])
    if not glass.any(): return ref, ["no glass"]
    gcol = Counter(map(tuple, rgb[glass].tolist())).most_common(1)[0][0]
    # glass: dark and near the glass colour (a dark reveal or shadow beside the glass is frame, not glass)
    glass &= np.sqrt(((rgb - np.array(gcol)) ** 2).sum(2)) < 45
    lab, n = Q.label(glass, False); sizes = np.bincount(lab.ravel())
    glass = np.isin(lab, [i for i in range(1, n + 1) if sizes[i] >= 2])
    if not glass.any(): return ref, ["no glass"]
    ys, xs = np.nonzero(glass)
    gy0, gy1, gx0, gx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    box = glass[gy0:gy1, gx0:gx1]; gh, gw = box.shape
    if not a[gy0:gy1, gx0:gx1].all(): return ref, ["glass touches transparency: left as it is"]
    colm = [x for x in range(gw) if (~box[:, x]).mean() >= 0.75]
    rowm = [y for y in range(gh) if (~box[y, [x for x in range(gw) if x not in colm]]).mean() >= 0.75] if len(colm) < gw else []
    lines = np.zeros((gh, gw), bool)
    for x in colm: lines[:, x] = True
    for y in rowm: lines[y, :] = True
    sub = rgb[gy0:gy1, gx0:gx1]
    mcol = Counter(map(tuple, sub[lines].tolist())).most_common(1)[0][0] if lines.any() else None
    notes = []
    def even(idx, total):
        """mullion lines (indices) -> evenly placed if the panes can be equal"""
        if not idx: return idx
        groups = []
        for i in idx:
            if groups and i == groups[-1][-1] + 1: groups[-1].append(i)
            else: groups.append([i])
        t = {len(g) for g in groups}
        if len(t) != 1: return idx
        t = t.pop(); k = len(groups)
        if groups[0][0] == 0 or groups[-1][-1] == total - 1: return idx    # a line on the glass edge: not a mullion
        rest = total - k * t
        if rest % (k + 1) and k == 1 and t == 1 and heavy and (total - 2) % 2 == 0:       # one bar: one px heavier makes it divide
            t += 1; rest = total - t; notes.append(f"bar made {t} px for equal panes")
        if rest % (k + 1): notes.append(f"panes cannot be equal ({total} px, {k} mullion(s) of {t})"); return idx
        p = rest // (k + 1)
        new = [j * (p + t) + p + s for j in range(k) for s in range(t)]
        if new != idx: notes.append(f"mullions moved {idx} -> {new} for equal panes")
        return new
    if equal:
        colm = even(colm, gw); rowm = even(rowm, gh)
    out = ref.copy()
    for y in range(gh):
        for x in range(gw):
            out[gy0 + y, gx0 + x, :3] = mcol if (mcol is not None and (x in colm or y in rowm)) else gcol
    changed = int((out != ref).any(2).sum())
    if changed: notes.append(f"glass cleaned: {changed} px")
    # the frame: each side of each ring around the glass (reveal, frame, sill, wall) one colour, corners as they are
    H_, W_ = out.shape[:2]; fixed = 0
    for d in range(1, max(gy0, gx0, H_ - gy1, W_ - gx1)):          # not the box's outermost ring: it meets the wall
        y0, y1, x0, x1 = gy0 - d, gy1 - 1 + d, gx0 - d, gx1 - 1 + d
        sides = []
        if y0 >= 1: sides.append([(y0, x) for x in range(max(1, x0 + 1), min(W_ - 1, x1))])
        if y1 < H_ - 1: sides.append([(y1, x) for x in range(max(1, x0 + 1), min(W_ - 1, x1))])
        if x0 >= 1: sides.append([(y, x0) for y in range(max(1, y0 + 1), min(H_ - 1, y1))])
        if x1 < W_ - 1: sides.append([(y, x1) for y in range(max(1, y0 + 1), min(H_ - 1, y1))])
        for side in sides:
            if len(side) < 3: continue
            c = Counter(tuple(out[y, x, :3].tolist()) for y, x in side)
            col, n = c.most_common(1)[0]
            if n / len(side) < 0.6 or n == len(side): continue
            for y, x in side:
                if tuple(out[y, x, :3].tolist()) != col: out[y, x, :3] = col; fixed += 1
    if fixed: notes.append(f"frame cleaned: {fixed} px")
    return out, notes

def run(src, dst, across=False, grid=True, equal=True, skip=(), verbose=True, near=False, heavy=True, clean=True, grow=3):
    im = np.array(Image.open(src).convert("RGBA"))
    rgb = im[..., :3].astype(int); a = im[..., 3] > 127
    H, W = a.shape
    thr, wins = detect(rgb, a)
    log = []
    if not wins: return im, ["no windows found"]
    # outer boxes, merged (two detections in one window are one window)
    boxes = []
    for w in wins:
        if any(abs(w["x"] - sx) <= 1 and abs(w["y"] - sy) <= 1 for sx, sy in skip): continue
        wall = ring_colour(rgb, a, w["x"], w["y"], w["x"] + w["w"], w["y"] + w["h"])
        if wall is None: continue
        b = outer_box(rgb, a, w, wall, grow); i = [w["x"], w["y"], w["x"] + w["w"], w["y"] + w["h"]]
        for o in boxes:
            if b[0] < o["b"][2] and o["b"][0] < b[2] and b[1] < o["b"][3] and o["b"][1] < b[3]:
                o["b"] = [min(b[0], o["b"][0]), min(b[1], o["b"][1]), max(b[2], o["b"][2]), max(b[3], o["b"][3])]
                o["i"] = [min(i[0], o["i"][0]), min(i[1], o["i"][1]), max(i[2], o["i"][2]), max(i[3], o["i"][3])]; break
        else: boxes.append(dict(b=b, i=i, wall=wall))
    for o in boxes:
        x0, y0, x1, y1 = o["b"]
        o["wall"] = ring_colour(rgb, a, x0, y0, x1, y1, 1, 3) or o["wall"]
        o["wk"] = tuple(v // 40 for v in o["wall"])
        o["w"], o["h"] = o["i"][2] - o["i"][0], o["i"][3] - o["i"][1]
        o["m"] = (o["i"][0] - x0, o["i"][1] - y0, x1 - o["i"][2], y1 - o["i"][3])     # margins: left, top, right, bottom
        pa = np.pad(a, 1)[y0:y1 + 2, x0:x1 + 2]
        o["edge"] = not pa.all()
    # groups: wall and storey, then the same glass size (1 px off counts as the same: a stray pixel)
    storeys = []
    for o in sorted(boxes, key=lambda o: (o["i"][1], o["i"][0])):
        if o["edge"]: log.append(f"window at {o['i'][0]},{o['i'][1]}: touches transparency, left alone"); continue
        for st in storeys:
            if st[0]["wk"] == o["wk"] and abs(st[0]["i"][1] - o["i"][1]) <= 4: st.append(o); break
        else: storeys.append([o])
    groups = []
    for st in storeys:
        rest = list(st)
        while rest:
            (cw, ch), _ = Counter((o["w"], o["h"]) for o in rest).most_common(1)[0]
            grp = [o for o in rest if abs(o["w"] - cw) <= 1 and abs(o["h"] - ch) <= 1]
            rest = [o for o in rest if o not in grp]
            groups.append(dict(wk=st[0]["wk"], size=(cw, ch), ws=grp))
    if across:                                                         # one window per wall and size
        merged = []
        for g in groups:
            for m in merged:
                if m["wk"] == g["wk"] and (m["size"] == g["size"] or (near and abs(m["size"][0] - g["size"][0]) <= 1 and abs(m["size"][1] - g["size"][1]) <= 1)):
                    if (len(g["ws"]), g["size"]) > (len(m["ws"]), m["size"]): m["size"] = g["size"]
                    m["ws"] += g["ws"]; break
            else: merged.append(dict(g, ws=list(g["ws"])))
        groups = merged
    new = im.copy()
    for g in groups:
        stamp_group(im, new, g["ws"], g["size"], thr, across, grid, equal, log, heavy, clean)
    if verbose:
        for l in log: print("  " + l)
    return new, log

def stamp_group(im, new, grp, size, thr, across, grid, equal, log, heavy=True, clean=True):
    H, W = im.shape[:2]
    # the stamp box: the glass size plus the widest frame margins of the group (frame, reveal, sill: a sill drawn 1 px
    # longer on one window is still covered, and the consensus decides each pixel)
    m = [max(o["m"][k] for o in grp) for k in range(4)]
    cw, ch = size[0] + m[0] + m[2], size[1] + m[1] + m[3]
    # alignment: the exact-size windows give a first reference, each window takes the shift that matches it best
    pos = [(o["i"][0] - m[0], o["i"][1] - m[1]) for o in grp]
    exact = [i for i, o in enumerate(grp) if (o["w"], o["h"]) == size] or list(range(len(grp)))
    crops = [crop(im, *pos[i], cw, ch) for i in exact]
    ok = [(i, c) for i, c in zip(exact, crops) if c is not None]
    if not ok: return
    ref = Counter(c.tobytes() for _, c in ok).most_common(1)[0][0]
    ref = next(c for _, c in ok if c.tobytes() == ref).copy()
    for _ in range(3):
        for i, o in enumerate(grp):
            best = None
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    c = crop(im, pos[i][0] + dx, pos[i][1] + dy, cw, ch)
                    if c is None: continue
                    d = int((c != ref).any(2).sum()) + (abs(dx) + abs(dy)) * 0.1
                    if best is None or d < best[0]: best = (d, dx, dy)
            pos[i] = (pos[i][0] + best[1], pos[i][1] + best[2])
        crops = [crop(im, *p, cw, ch) for p in pos]
        if len(grp) >= 2:
            tot = [sum(int((c != c2).any(2).sum()) for c2 in crops) for c in crops]
            ref = consensus(crops, list(np.argsort(tot)))
        else:
            ref = crops[0].copy()
    if not (ref[..., 3] > 127).all():                                 # a window must be wholly opaque
        log.append(f"group {cw}x{ch} at {pos[0]}: not wholly opaque, left alone"); return
    ref, notes = clean_reference(ref, thr, equal, heavy) if clean else (ref, ["kept as drawn (--keep-glass)"])
    # the grid
    tgt = list(pos)
    if grid:
        storeys = {}
        for i, p in enumerate(pos):
            for k in storeys:
                if abs(k - p[1]) <= 4: storeys[k].append(i); break
            else: storeys[p[1]] = [i]
        for k, idx in storeys.items():
            ys = Counter(pos[i][1] for i in idx).most_common(1)[0][0]
            for i in idx:
                if abs(pos[i][1] - ys) <= 1: tgt[i] = (tgt[i][0], ys)
            if len(idx) >= 3:
                idx = sorted(idx, key=lambda i: pos[i][0]); xs = [pos[i][0] for i in idx]
                bestfit = None
                for s in range(max(1, (xs[-1] - xs[0]) // (len(xs) - 1) - 1), (xs[-1] - xs[0]) // (len(xs) - 1) + 2):
                    for x0 in range(xs[0] - 1, xs[0] + 2):
                        dev = [x0 + j * s - x for j, x in enumerate(xs)]
                        m = max(abs(d) for d in dev); moved = sum(d != 0 for d in dev)
                        if m <= 1 and (bestfit is None or (moved, m) < bestfit[0]): bestfit = ((moved, m), x0, s)
                if bestfit:
                    for j, i in enumerate(idx): tgt[i] = (bestfit[1] + j * bestfit[2], tgt[i][1])
        if across:                                                     # columns: windows above each other line up
            cols = {}
            for i, p in enumerate(tgt):
                for k in cols:
                    if abs(k - p[0]) <= 1: cols[k].append(i); break
                else: cols[p[0]] = [i]
            for k, idx in cols.items():
                if len(idx) < 2: continue
                xm = Counter(tgt[i][0] for i in idx).most_common(1)[0][0]
                for i in idx: tgt[i] = (xm, tgt[i][1])
    # stamp
    changed = 0
    for i, o in enumerate(grp):
        tx, ty = tgt[i]
        if tx < 0 or ty < 0 or tx + cw > W or ty + ch > H: continue
        X0, Y0 = min(pos[i][0], tx), min(pos[i][1], ty)
        X1, Y1 = max(pos[i][0] + cw, tx + cw), max(pos[i][1] + ch, ty + ch)
        if not (im[Y0:Y1, X0:X1, 3] > 127).all(): log.append(f"window at {o['i'][0]},{o['i'][1]}: shifted box meets transparency, left alone"); continue
        old = new[Y0:Y1, X0:X1].copy()
        reg = np.zeros((Y1 - Y0, X1 - X0), bool)                       # where the window was (moved: becomes wall)
        reg[pos[i][1] - Y0:pos[i][1] - Y0 + ch, pos[i][0] - X0:pos[i][0] - X0 + cw] = True
        ins = np.zeros_like(reg); ins[ty - Y0:ty - Y0 + ch, tx - X0:tx - X0 + cw] = True
        blk = new[Y0:Y1, X0:X1]
        blk[ins] = ref.reshape(-1, 4)
        # the box's outermost ring: a line that runs on outside the box (a cornice, a string course) is kept
        for yy in range(ty, ty + ch):
            for xx in range(tx, tx + cw):
                if not (yy in (ty, ty + ch - 1) or xx in (tx, tx + cw - 1)): continue
                o_ = im[yy, xx]
                for ny, nx in ((yy - 1, xx), (yy + 1, xx), (yy, xx - 1), (yy, xx + 1)):
                    if ty <= ny < ty + ch and tx <= nx < tx + cw: continue
                    if 0 <= ny < H and 0 <= nx < W and (im[ny, nx] == o_).all() and (new[ny, nx] == o_).all() and \
                       ((ny == yy and xx in (tx, tx + cw - 1)) or (nx == xx and yy in (ty, ty + ch - 1))):
                        # runs on in the line's own direction: horizontal lines cross the left/right sides only
                        pass
                    else: continue
                    nxt = (yy + (yy - ny), xx + (xx - nx))
                    if ty <= nxt[0] < ty + ch and tx <= nxt[1] < tx + cw and (im[nxt] == o_).all():
                        new[yy, xx] = o_; break
        blk[reg & ~ins, :3] = o["wall"]
        changed += int((blk != old).any(2).sum())
    log.append(f"group {cw}x{ch} x{len(grp)} at " + ", ".join(f"{p[0]},{p[1]}" + (f"->{t[0]},{t[1]}" if t != p else "") for p, t in zip(pos, tgt)) +
               f": {changed} px" + ("; " + "; ".join(notes) if notes else ""))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--across-storeys", action="store_true"); ap.add_argument("--no-grid", action="store_true")
    ap.add_argument("--no-equal", action="store_true")
    ap.add_argument("--keep-glass", action="store_true", help="no glass or frame cleaning: the windows only become the group's consensus (painted glass, reflections)")
    ap.add_argument("--grow", type=int, default=3, help="how far a window's frame and sill may reach past the glass found (default 3)")
    ap.add_argument("--no-heavy", action="store_true", help="never make a glazing bar 2 px to get equal panes")
    ap.add_argument("--near", action="store_true", help="with --across-storeys: windows 1 px off in size on other storeys count as the same window")
    ap.add_argument("--skip", nargs="*", default=[], help="x,y of a detected window to leave alone (a door, a sign)")
    o = ap.parse_args()
    new, log = run(o.src, o.dst, o.across_storeys, not o.no_grid, not o.no_equal, [tuple(int(v) for v in s.split(",")) for s in o.skip], near=o.near, heavy=not o.no_heavy, clean=not o.keep_glass, grow=o.grow)
    im = np.array(Image.open(o.src).convert("RGBA"))
    a = im[..., 3] > 127
    assert (new[..., 3] == im[..., 3]).all(), "alpha changed"
    c0 = set(map(tuple, im[a][:, :3].tolist())); c1 = set(map(tuple, new[a][:, :3].tolist()))
    assert c1 <= c0, "new colours"
    Image.fromarray(new).save(o.dst)
    print(f"{o.src.split('/')[-1]:24} windows stamped: {int((new != im).any(2).sum())} px changed, colours {len(c0)} -> {len(c1)}")
