#!/usr/bin/env python3
"""tools/build_rooftops_backdrop.py: Rooftops' backdrop BUILT by rule (8 Nov 2026, phase 1 family E, 0 credits): the
painted sky, the far town, the mid town and the back row of houses behind Pepper's roofs, so no roof, slab or step
hangs over empty sky (audit RW5, RW9, RW10). Design target: art/gen/concepts/rt_hotel_concept_a.png (reference
only): a warm peach-to-amber sky, a church spire and far roofs, red tile roofs and chimney stacks with clay pots
behind ochre houses with a sandstone parapet.

  python3 -I tools/build_rooftops_backdrop.py              write riverwalk/levelart/rooftops/{sky,far,mid}.png,
                                                            back_<x>_<y>.png and backdrop.lua
  python3 -I tools/build_rooftops_backdrop.py --check      fail if a file on disk is not what this script builds
  python3 -I tools/build_rooftops_backdrop.py --preview D  previews (the back row over the ground, the strips)

Layers, back to front (docs/layer_ladder.md: the further back, the lighter; the darkest of each layer measured):
  sky   960 x 360, tools/build_sky.py's painter with this level's tones (row 0 = screen y -120); flat tones with wavy
        stepped joins, cumulus banks of stamped lobes. Rises 0.03 of the camera's climb.
  far   640 x 240 strip, 3 tones: roofs and gables, the German Church's spire and the Great Church's tower, a warm rim
        on the lit (left, top) edges. Scroll 0.1, rises 0.03 of the climb; filled to its bottom (it never ends on
        screen). Darkest >= 145, contrast <= 35.
  mid   640 x 240 strip at half scale (storeys 48 px): house fronts with tile roofs, gables, chimneys and 2-pane
        windows on one grid. Scroll 0.5, rises 0.06 of the climb; filled to its bottom. Darkest >= 105.
  back  true scale, with the world: one back house per block of the front row (each block at most 224 px), its top
        a parapet and a hipped tile roof, 32-80 px over the highest roof near it (the higher the tier, the lower it
        stands; none at the very top: open sky over the summit), its front down to the roofs, in the front row's
        ramps 25 % towards the sky's horizon. Inside the light court it is the court's shaded back wall.
The look shader leaves sky, far and mid as built (their script layers are neutral)."""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_rooftops_art as A          # the map, the houses, the palette, the window
import build_sky as BS                  # the painted sky's painter

OUT = A.OUT
HAZE = (252, 222, 172)                  # the level's warm horizon: the back row is mixed 30 % towards it, never grey
BACK_K, BACK_GREY = 0.30, 0.0          # (round 3, producer 8 Nov: lighter in value, but keep the colour: one warm haze)
CAMY_MAX = 960

SKY = dict(                                                  # warm late afternoon: peach above, amber at the horizon
    seed=4808, light=(-0.80, -0.60), camymax=96,             # (camymax 96: the sky rises 0.03 x 960 = 29 rows)
    tones=[("f4d2b8", None, 0), ("f6d8b8", -30, 5), ("f8dcb6", 30, 5),
           ("fae0b2", 70, 4, dict(jit=1, extra=3, tl=(60, 180))), ("fce4b0", 98, 3, dict(jit=1, extra=2, tl=(60, 180)))],
    streaks=[(3, 64, 4, (70, 180), (2, 3)), (4, 92, 4, (80, 200), (2, 3)), (2, 20, 3, (60, 140), (1, 2))],
    cloud=dict(lit1="fffaee", lit2="fff0dc", body="fae2cc", under="f0d4c0"),
    banks=[dict(x=40, w=210, base=40, h=30, peak=0.42, r=(8, 14), under=(3, 6)),
           dict(x=500, w=240, base=52, h=32, peak=0.55, r=(8, 15), under=(3, 6)),
           dict(x=780, w=120, base=6, h=18, peak=0.45, r=(6, 10), under=(2, 4))],
    low=[dict(x=120, w=200, base=96, h=7), dict(x=420, w=140, base=93, h=5), dict(x=700, w=220, base=95, h=8)],
    wisps=[(300, 18, 28, 4), (640, 10, 24, 3), (900, 30, 26, 4), (180, -40, 24, 3)],
)

FAR = {"rim": "f2d8c0", "main": "e8c8b0", "near": "dab69e"}
MID = {"wa": "ecbe88", "wb": "f0cc8c", "wc": "eab894", "wd": "f0d4aa", "wsh": "dcaa7c", "cap": "f4dcbc",
       "tile_hi": "eca880", "tile": "e2946a", "tile_sh": "d4845c", "frame": "b89c8e", "glass": "a8b4bc",
       "glass_hi": "ccd4d8", "ch": "c49c88"}


def hexc(h): return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], np.uint8)


class Rng(BS.Rng): pass


# ------------------------------------------------------------------------------------------------ sky
def sky():
    BS.LEVELS["rooftops"] = SKY
    rgb, img, nsky, stats = BS.build_sky("rooftops")
    return rgb, img, nsky, stats


# ------------------------------------------------------------------------------------------------ far town
def far():
    W, H, BASE = 640, 240, 110                   # BASE: the strip row the roofs' eaves stand on (room for the spires)
    m = np.zeros((H, W), np.uint8)               # 0 empty, 1 main, 2 near (towers)
    m[BASE:, :] = 1
    r = Rng(4211)
    x = 0
    while x < W:                                 # roofs: blocks with gable or hipped tops, a chimney now and then
        w = r.i(26, 58)
        if W - (x + w) < 26: w = W - x
        h = r.i(6, 20)
        m[BASE - h:BASE, x:x + w] = 1
        kind = r.i(0, 2)
        if kind == 0:                            # a pitched roof seen from the eaves side: 1 up for 2 across
            for d in range(1, w // 4):
                m[BASE - h - d, x + 2 * d:x + w - 2 * d] = 1
        elif kind == 1:                          # a stepped gable end
            for s in range(1, 4):
                m[BASE - h - 4 * s:BASE - h - 4 * (s - 1), x + 4 * s:x + w - 4 * s] = 1
        if r(0, 1) < 0.5:
            cx = x + r.i(4, max(5, w - 8))
            m[BASE - h - 8:BASE - h, cx:cx + 3] = 1
        x += w
    def tower(cx, w, body, spire, cupola=False):
        m[BASE - body:BASE, cx - w // 2:cx + (w + 1) // 2] = 2
        y = BASE - body
        if cupola:                               # the Great Church: a lantern, a dome, an obelisk
            for d in range(6):
                hw = (w // 2 - 1) - (d * d) // 6
                m[y - d - 1, cx - hw:cx + hw] = 2
            m[y - 6 - spire:y - 6, cx - 1:cx + 1] = 2
        else:                                    # the German Church: a needle spire on a short drum
            m[y - 6:y, cx - w // 2 + 2:cx + w // 2 - 2] = 2
            y -= 6
            for d in range(spire):
                hw = max(0, int(round((w // 2 - 2) * (1 - d / spire))))
                m[y - d - 1, cx - hw:cx + hw + 1] = 2
    tower(150, 16, 44, 58)
    tower(300, 20, 40, 14, cupola=True)
    tower(590, 14, 50, 52)                       # (round 3) the spire in view from the hotel roof (camera x 4224)
    out = np.zeros((H, W, 4), np.uint8)
    out[m == 1] = np.append(hexc(FAR["main"]), 255)
    out[m == 2] = np.append(hexc(FAR["near"]), 255)
    a = m > 0
    edge = a & ~np.roll(a, 1, axis=1)            # lit edges: left (the strip wraps) and top
    pa = np.pad(a, 1)
    edge |= a & ~pa[:-2, 1:-1]
    out[edge] = np.append(hexc(FAR["rim"]), 255)
    return out


# ------------------------------------------------------------------------------------------------ mid town
def mid():
    W, H = 640, 240
    leg = {k: np.append(hexc(v), 255) for k, v in MID.items()}
    a = np.zeros((H, W, 4), np.uint8)
    def fill(x0, y0, x1, y1, k): a[max(0, y0):max(0, y1), max(0, x0):x1] = leg[k]
    widths = [56, 72, 48, 64, 80, 52, 68, 60, 44, 96]            # 640 in all
    tops = [40, 24, 52, 32, 16, 44, 28, 36, 56, 20]
    walls = ["wa", "wb", "wc", "wd", "wb", "wa", "wd", "wc", "wb", "wa"]
    x = 0
    for i, w in enumerate(widths):
        t = tops[i]; wk = walls[i]
        fill(x, t, x + w, H, wk)
        fill(x, t, x + w, t + 3, "cap"); fill(x, t + 3, x + w, t + 5, "wsh")          # cornice and its shade
        if i % 3 == 1:                                          # a front gable with tile edges
            for d in range(w // 2):
                fill(x + d, t - d, x + w - d, t - d + 1, wk)
                if d % 1 == 0:
                    for e, k in ((0, "tile_hi"), (1, "tile"), (2, "tile_sh")):
                        if x + d + e < x + w // 2: a[t - d, x + d + e] = leg[k]
                        if x + w - d - 1 - e >= x + w // 2: a[t - d, x + w - d - 1 - e] = leg[k]
        else:                                                   # a tile roof behind the cornice: courses of 3 rows
            rh = 12
            for rr in range(rh):
                y = t - rh + rr; inset = rh - rr
                for xx in range(x + inset, x + w - inset):
                    k = "tile_hi" if rr == 0 else ("tile_sh" if rr % 3 == 2 or (xx + (rr // 3) * 3) % 6 == 0 else "tile")
                    a[y, xx] = leg[k]
            if i % 2 == 0:                                      # a chimney with its pot
                cx = x + w * 2 // 3
                fill(cx, t - rh - 8, cx + 5, t - rh + 4, "ch"); fill(cx + 1, t - rh - 11, cx + 4, t - rh - 8, "tile")
        n = max(1, (w - 8) // 14)                               # windows: 7 x 11, one grid, storeys of 48 px
        span = (n - 1) * 14 + 7
        for L in range(H - 48, t + 4, -48):
            wy = L + 12
            if wy < t + 12: continue
            for j in range(n):
                wx = x + (w - span) // 2 + j * 14
                fill(wx, wy, wx + 7, wy + 11, "frame")
                fill(wx + 1, wy + 1, wx + 3, wy + 10, "glass"); fill(wx + 4, wy + 1, wx + 6, wy + 10, "glass")
                a[wy + 1, wx + 1] = leg["glass_hi"]; a[wy + 1, wx + 4] = leg["glass_hi"]
                fill(wx - 1, wy + 11, wx + 8, wy + 12, "cap")
        fill(x + w - 1, t + 5, x + w, H, "wsh")                 # the party wall: one shade column
        x += w
    return a


# ------------------------------------------------------------------------------------------------ back row
def back_rgb():
    """the front row's palette, 25 % towards the horizon"""
    rgb = A.RGB.astype(float).copy()
    k = np.full((len(rgb), 1), BACK_K); gk = np.full((len(rgb), 1), BACK_GREY)
    for n in ("crt_hi", "crt", "crt_sh", "crt_dk"): k[A.IDX[n]], gk[A.IDX[n]] = 0.15, 0.15   # the light court: in shade
    rgb[1:, :3] = rgb[1:, :3] + (np.array(HAZE) - rgb[1:, :3]) * k[1:]
    l = rgb[1:, :3] @ BS.W601
    rgb[1:, :3] = rgb[1:, :3] + (l[:, None] - rgb[1:, :3]) * gk[1:]
    return np.round(rgb).astype(np.uint8)


def back_blocks():
    cuts = sorted({0, 288, 576} | {h[0] for h in A.HOUSES} | {A.HOUSES[-1][1]})
    blocks = []
    for a, b in zip(cuts, cuts[1:]):
        n = max(1, -(-(b - a) // 224))
        for i in range(n): blocks.append((a + (b - a) * i // n, a + (b - a) * (i + 1) // n))
    return blocks


def back(top, W, H):
    cv = A.Canvas(W, H)
    blocks = back_blocks()
    rotate = {"ochre": "salmon", "yellow": "ochre", "salmon": "yellow", "cream": "salmon", "rust": "yellow", "court": "court"}   # 4 ramps (20 colours)
    house_at = {}
    for h in A.HOUSES:
        for x in range(h[0], h[1]): house_at[x] = h
    yb = []
    for i, (a, b) in enumerate(blocks):
        ref = int(top[max(0, a - 32):min(W, b + 32)].min())
        lift = 64 if ref >= 600 else 48 if ref >= 376 else 32 if ref >= 184 else None   # (round 3: lower, as the concept)
        yb.append(None if lift is None else (ref - lift - [0, 16, 8, 24][i % 4]) // 8 * 8)
    for i, (a, b) in enumerate(blocks):
        y = yb[i]
        if y is None: continue
        mid_ = (a + b) // 2
        pl = A.PLASTER["court" if 4800 <= mid_ < 5200 else rotate[house_at.get(mid_, (0, 0, "ochre"))[2]]]
        bottom = lambda x: int(top[x]) + 12
        for x in range(a, b): cv.fill(x, y + 6, x + 1, bottom(x), pl)
        for x in range(a, b): cv.fill(x, y + 6, x + 1, min(bottom(x), y + 10), pl + "_sh")
        # open sides (the neighbour lower): one darker column, the edge in its own colour
        lo_l = i == 0 or yb[i - 1] is None or yb[i - 1] > y
        lo_r = i == len(blocks) - 1 or yb[i + 1] is None or yb[i + 1] > y
        if lo_l: cv.fill(a, y + 6, a + 1, bottom(a), pl + "_sh")
        if lo_r: cv.fill(b - 1, y + 6, b, bottom(b - 1), pl + "_sh")
        # the parapet: a sandstone cap 6 rows (no ink: decoration), 2 px over the open sides
        x0, x1 = a - (2 if lo_l else 0), b + (2 if lo_r else 0)
        for rr, n in enumerate(("cap_hi", "cap_hi", "cap", "cap", "cap_sh", "cap_sh")): cv.fill(x0, y + rr, x1, y + rr + 1, n)
        for xx in range(a + 24, b - 8, 24): cv.fill(xx, y + 2, xx + 1, y + 5, "cap_sh")
        # a hipped tile roof behind the parapet, 16 rows, courses of 4 in running bond
        RH = 16
        for rr in range(RH):                                    # red clay in rows: a ridge, then courses of 4 rows
            yy = y - RH + rr; inset = RH - rr + 4                # (a lit row, two tile rows with the joints in
            for xx in range(a + inset, b - inset):               # running bond, a dark bottom row)
                c, r = (rr - 1) // 4, (rr - 1) % 4
                if rr == 0: n = "tile_dk"
                elif r == 0: n = "tile_hi"
                elif r == 3: n = "tile_dk"
                elif (xx + c * 4) % 8 == 0: n = "tile_sh"
                else: n = "tile"
                cv.put(xx, yy, n)
        if i % 2 == 0 and b - a >= 64:                          # a brick stack, a stone cap, three clay pots
            cx = a + (b - a) * 2 // 3
            y0s = y - RH - 16
            for yy in range(y0s, y - 4):
                for xx in range(cx, cx + 16):
                    if (yy - y0s) % 4 == 3 or (xx - cx + ((yy - y0s) // 4 % 2) * 4) % 8 == 0: n = "cap_hi"   # mortar
                    elif cx + 16 - xx <= 2: n = "ch_sh"
                    else: n = "ch"
                    cv.put(xx, yy, n)
            cv.fill(cx - 2, y0s - 4, cx + 18, y0s - 3, "cap_hi"); cv.fill(cx - 2, y0s - 3, cx + 18, y0s, "cap")
            cv.fill(cx - 2, y0s - 1, cx + 18, y0s, "cap_sh")
            for px in (cx + 1, cx + 6, cx + 11):
                cv.fill(px, y0s - 11, px + 4, y0s - 4, "tile"); cv.fill(px + 3, y0s - 11, px + 4, y0s - 4, "tile_sh")
                cv.fill(px - 1, y0s - 12, px + 5, y0s - 11, "tile_hi")
        # windows on the front row's storey grid
        win = A.window()
        n = max(1, (b - a - 2 * A.MARGIN - A.WIN_W) // A.PITCH + 1)
        span = (n - 1) * A.PITCH + A.WIN_W
        for L in range(A.STOREY0, A.STREET - A.STOREY, A.STOREY):
            wy = L + A.WIN_TOP
            if wy < y + 18: continue
            for j in range(n):
                wx = a + (b - a - span) // 2 + j * A.PITCH
                if max(top[wx - 2:wx + A.WIN_W + 2].min(), 0) > wy - 4: cv.sprite(win, wx - 2, wy)
        if a == 0:                                              # the street cafe: a striped awning over the windows
            ay = A.STREET - 52
            for xx in range(a + 24, a + 216):
                k = "tile" if ((xx - a) // 8) % 2 == 0 else "cap_hi"
                cv.fill(xx, ay, xx + 1, ay + 7, k); cv.put(xx, ay, "tile_hi" if k == "tile" else "cap_hi")
                if (xx - a) % 8 in (2, 3, 4, 5): cv.put(xx, ay + 7, k)
    return cv


def back_chunks(cv, W, H):
    out = {}
    for cy in range(0, H, A.CHUNK):
        for cx in range(0, W, A.CHUNK):
            a = cv.a[cy:cy + A.CHUNK, cx:cx + A.CHUNK]
            ys, xs = np.nonzero(a)
            if len(ys) == 0: continue
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            out[(cx + int(x0), cy + int(y0))] = a[y0:y1, x0:x1]
    return out


def manifest(bc):
    lines = ["-- written by tools/build_rooftops_backdrop.py: the backdrop of the Rooftops art (do not edit)", "return {",
             "  sky = \"sky.png\", far = \"far.png\", mid = \"mid.png\",",
             "  -- the strips' rows: far roofs' eaves at row 110, mid tops from row 16", "  back = {"]
    for (x, y), a in sorted(bc.items()):
        lines.append(f'    {{ x = {x}, y = {y}, w = {a.shape[1]}, h = {a.shape[0]}, file = "back_{x}_{y}.png" }},')
    lines += ["  },", "}", ""]
    return "\n".join(lines)


def main():
    check = "--check" in sys.argv
    prev = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    g = A.load_map()
    W, H, top, kind, solid = A.terrain(g)
    rgb, img, nsky, stats = sky()
    fa, mi = far(), mid()
    fails = BS.checks("rooftops", rgb, img, nsky, stats, fa[:117])
    bcv = back(top, W, H)
    brgb = back_rgb()
    bc = back_chunks(bcv, W, H)
    files = {"sky.png": rgb, "far.png": fa, "mid.png": mi}
    for (x, y), a in bc.items(): files[f"back_{x}_{y}.png"] = brgb[a]
    man = manifest(bc)
    if check:
        for f, a in files.items():
            p = os.path.join(OUT, f)
            mode = "RGB" if a.shape[-1] == 3 else "RGBA"
            if not os.path.exists(p) or not np.array_equal(np.array(Image.open(p).convert(mode)), a): fails.append(f + " differs")
        mp = os.path.join(OUT, "backdrop.lua")
        if not os.path.exists(mp) or open(mp).read() != man: fails.append("backdrop.lua differs")
    else:
        for f in os.listdir(OUT):
            if f.startswith("back_"): os.remove(os.path.join(OUT, f))
        for f, a in files.items(): Image.fromarray(a, "RGB" if a.shape[-1] == 3 else "RGBA").save(os.path.join(OUT, f), optimize=True)
        open(os.path.join(OUT, "backdrop.lua"), "w").write(man)
    # the ladder (docs/layer_ladder.md): darkest (10th pct) and contrast per layer
    def lum(a):
        a = a.reshape(-1, a.shape[-1]); a = a[a[:, 3] > 0] if a.shape[1] == 4 else a
        return a[:, :3].astype(float) @ BS.W601
    for name, a, dmin, cmax in (("far", fa, 145, 35), ("mid", mi, 105, 85), ("back", brgb[bcv.a][bcv.a > 0][None], 80, 120)):
        l = lum(a); p10, p90 = np.percentile(l, 10), np.percentile(l, 90)
        print(f"  {name:5} darkest {p10:.0f} median {np.median(l):.0f} contrast {p90 - p10:.0f} colours {len(np.unique(a.reshape(-1, a.shape[-1]), axis=0))}")
        if p10 < dmin: fails.append(f"{name}: darkest {p10:.0f} < {dmin}")
        if p90 - p10 > cmax + 3: fails.append(f"{name}: contrast {p90 - p10:.0f} > {cmax}")
    if prev:
        os.makedirs(prev, exist_ok=True)
        gr = np.array(Image.open(os.path.join(prev, "ground_full.png")).convert("RGB")) if os.path.exists(os.path.join(prev, "ground_full.png")) else None
        bim = Image.fromarray(brgb[bcv.a], "RGBA")
        canvas = Image.new("RGBA", bim.size, (250, 222, 176, 255)); canvas.alpha_composite(bim)
        cv2, *_ = A.build()
        canvas.alpha_composite(Image.fromarray(A.RGB[cv2.a], "RGBA"))
        canvas.convert("RGB").save(os.path.join(prev, "back_full.png"))
        Image.fromarray(fa).save(os.path.join(prev, "far.png")); Image.fromarray(mi).save(os.path.join(prev, "mid.png"))
        Image.fromarray(rgb).save(os.path.join(prev, "sky.png"))
    print(f"rooftops backdrop: sky, far, mid, {len(bc)} back chunks, clouds {stats['cloud_share']} %"
          + ("" if not fails else "\n" + "\n".join("FAIL " + f for f in fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
