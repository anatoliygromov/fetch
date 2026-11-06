#!/usr/bin/env python3
"""build_rw_rowboat.py: the River Walk rowing boat (night of 6 Nov 2026), split into parts (owner, 6 Nov: the
SpriteCook r2 boat was "really terrible": rower and oar one AI picture, AI-animated, so arm and oar did not connect;
the hull one flat orange slab with no planks; no waterline).

  python3 -I tools/build_rw_rowboat.py           build everything
  python3 -I tools/build_rw_rowboat.py --check   fail if a file on disk differs from what this script builds

Design target: art/gen/concepts/rw_rowboat_concept_b.png (Artlist, reference only, never cut). Parts:
  HULL  BUILT by rule (riverwalk/art/scene/rw_rowboat.png): a 4.0 m Stockholm eka at 46 px/m = 185 px, seen exactly
        from the side, bow LEFT (the stem rises 12 px), a small square transom RIGHT (rises 5 px). Clinker planks are
        clean bands that follow the sheer, each 5 px: lit top edge, two mid rows, a shade row, a dark lap; a white
        top strake under a dark gunwale rail; a brass rowlock on the rail. One 1 px ink outline (Pepper stands on
        it). Colours from art/palettes/riverwalk.gpl ramps (honey wood, white paint, brass).
  OARS  BUILT per frame by rule: a straight pole (2 px core, lit over shade, ink outline) with a flat blade, pivoting
        on the rowlock: the oar is a line through the pivot, handle 16 px inboard, blade end 48 px outboard (as seen
        from the side), swept fore and aft (phi) and tipped (beta) so the blade is buried on the drive and lifted on
        the return.
  ROWER the only DRAWN part: SpriteCook GPT 2.5 render art/gen/out/rw_rower_a.png (job db5f2e89), cut 1:1 on its own
        grid (SpriteCook's pixel output; the raw 1024 render is only 67 % clean on a 4 px grid, and its fists reach
        past the blockout, so grid_cut.py would drop them), magenta keyed, colours mapped to 18 of its own colours
        plus the one ink (nearest colour, no averaging of pixels), a clean pass on the new cut, then by rule: the
        render's arms and fists taken off (left of his chest line), the chest refilled with the jumper's own
        vertical ribs, his legs below the gunwale dropped (the hull hides them). The fists are stamped back from
        the render (one 9 x 10 piece) on the oar handle in every frame; the near arm is drawn by rule from shoulder
        to wrist (upper arm 13 px, forearm 14 px, a two-bone reach) in the sleeve's own four colours.
  LOOP  6 frames keyed by rule (riverwalk/art/scene/rw_rower.png, 6 x 64 x 62): catch, drive, drive, finish, return,
        return. He leans 2 px forward at the catch and 1 px back at the finish; the fists sit on the handle in every
        frame and the arm joins them to the shoulder.
Lines (frame row = world y - 176, hull x = frame x): rail top amidships row 36 (world 212 = Pepper's deck, the
mover's top), waterline row 48 (world 224), keel row 57. The water tint below row 48, the ripples, the wake and the
splash are drawn in code (setpieces.lua Sp.drawRowboat). Every changed pixel of the rower cut is listed in
art/source/rw_rower/edits.json."""
import json, math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

hexc = lambda h: np.array([int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255], np.uint8)
INK = hexc('#17181f')                                                   # the one ink (setpieces' obstacle ink family)
RAIL_L, RAIL = hexc('#805032'), hexc('#583626')                          # gunwale rail: lit top, dark
WHITE, WHITE_S = hexc('#f0ece0'), hexc('#d2cec0')                        # the white top strake, its lower edge
W_L, W_M, W_S, W_LAP = hexc('#eebc68'), hexc('#d49a54'), hexc('#a87046'), hexc('#805032')   # varnished honey planks
BRASS_L, BRASS = hexc('#f4cc69'), hexc('#bf6d36')                       # the rowlock
OAR_L, OAR_S = hexc('#eebc68'), hexc('#a87046')                          # the oar: lit over shade

W, H = 185, 62                       # hull image (frame rows: world y - 176)
Y0 = 176
RAIL_Y, WATER_Y, KEEL_Y = 212, 224, 233
ROWLOCK = (98, 211)                  # the oar's pivot (world y), on the rail
BOW_RISE, STERN_RISE = 12, 5
FLAT = (62, 128)                     # the sheer is level (y 212) between these columns


def sheer(x):
    """World y of the top of the gunwale at column x: level amidships, a smooth rise to the bow and the transom."""
    if x < FLAT[0]: t = (FLAT[0] - x) / FLAT[0]; return RAIL_Y - round(BOW_RISE * t ** 2.2)
    if x > FLAT[1]: t = (x - FLAT[1]) / (W - 1 - FLAT[1]); return RAIL_Y - round(STERN_RISE * t ** 2.0)
    return RAIL_Y


def stem_x(y):
    """The bow's front edge: the stem stands nearly upright, then curves back into the keel (the forefoot)."""
    top = sheer(0); t = (y - top) / (KEEL_Y - top)
    if t <= 0.4: return round(2 * t / 0.4)                            # the upright stem: 2 px of rake
    return 2 + round(24 * ((t - 0.4) / 0.6) ** 1.7)                   # the forefoot curving back into the keel


def keel(x):
    """World y of the bottom: flat, rising a little to the transom's foot (world y 227)."""
    if x <= 150: return KEEL_Y
    t = (x - 150) / (W - 1 - 150); return KEEL_Y - round(6 * t ** 1.6)


def hull():
    a = np.zeros((H, W, 4), np.uint8)
    inside = np.zeros((H, W), bool)
    for x in range(W):
        for y in range(sheer(x), keel(x) + 1):
            if x >= stem_x(y): inside[y - Y0, x] = True
    # fills by rule, column by column, rows counted down from the sheer (bands follow the sheer)
    for x in range(W):
        s = sheer(x)
        for y in range(s, keel(x) + 1):
            r = y - s
            if not inside[y - Y0, x]: continue
            if r <= 2: c = (INK, RAIL_L, RAIL)[r]                     # the gunwale rail under the outline: lit, dark
            elif r <= 5: c = WHITE if r < 5 else WHITE_S              # the white top strake
            else:
                k = (r - 6) % 5                                       # clinker planks, 5 px each
                c = (W_L, W_M, W_M, W_S, W_LAP)[k]
            a[y - Y0, x] = c
    # the stem post at the bow: a 2 px darker band along the front edge, lit on its inner side
    for y in range(sheer(0), KEEL_Y + 1):
        x0 = stem_x(y)
        for dx, c in ((1, W_S), (2, W_S), (3, W_L)):
            if x0 + dx < W and inside[y - Y0, x0 + dx]: a[y - Y0, x0 + dx] = c
    # the transom's edge board: 2 px in shade at the stern
    for y in range(sheer(W - 1), keel(W - 1) + 1):
        for x in (W - 3, W - 2):
            if inside[y - Y0, x] and y - sheer(x) > 1: a[y - Y0, x] = W_S
    # the outline: every inside pixel that touches the outside (4-neighbours) is ink
    out = np.zeros_like(inside)
    for y in range(H):
        for x in range(W):
            if not inside[y, x]: continue
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                yy, xx = y + dy, x + dx
                if not (0 <= yy < H and 0 <= xx < W) or not inside[yy, xx]: out[y, x] = True
    a[out] = INK
    # the rowlock: a brass fork standing on the rail at the pivot, outlined
    rx, ry = ROWLOCK
    for (dx, dy), c in {(-1, -2): BRASS_L, (1, -2): BRASS, (-1, -1): BRASS_L, (0, -1): BRASS, (1, -1): BRASS}.items():
        a[ry + dy - Y0 - 1 + 1, rx + dx] = c                          # (rows ry-2, ry-1: on top of the rail ink)
    for (dx, dy) in ((-2, -2), (-2, -1), (2, -2), (2, -1), (-1, -3), (1, -3), (0, -2)):
        if a[ry + dy - Y0, rx + dx, 3] == 0 or (dx, dy) == (0, -2): a[ry + dy - Y0, rx + dx] = INK
    return a


def box():
    """The mover's box on the hull (level/riverwalk.lua ROWBOAT x0 = hull x + 25, 154 px): columns 25-178, where the
    rail is at most 4 px above the deck (y 212); the bow and the transom rise above it."""
    b0, b1 = 25, 179
    assert all(RAIL_Y - sheer(x) <= 4 for x in range(b0, b1))
    return b0, b1


# ---- the rower --------------------------------------------------------------------------------------------------
RENDER, CROP = 'art/gen/out/rw_rower_a.png', (104, 137, 144, 183)    # his 40 x 46 on the render's own grid
RX0 = 89                     # the rower sprite's x on the hull (his chest at hull x 110, his back at 128)
SRC = 'art/source/rw_rower'
ARM_L = ((63, 92, 136), (55, 73, 120), (42, 64, 107))  # the sleeve: lit, mid, shade (his own jumper's colours)


def rower_cut():
    """The cut on the render's grid (1:1), the magenta key, his colours (18 of the render's own + the ink: each
    pixel takes the nearest, nothing averaged), one clean pass on the new cut. Deterministic (fixed seed)."""
    a = np.array(Image.open(RENDER).convert('RGBA')).astype(int)[CROP[1]:CROP[3], CROP[0]:CROP[2]].copy()
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    a[(r > 150) & (g < 120) & (b > 150) & (r - g > 80), 3] = 0          # the magenta ground and its fringe
    op = a[..., 3] > 0; a[~op] = 0; a[op, 3] = 255
    rgb = a[..., :3].astype(float); dark = op & (rgb.sum(-1) < 75)
    pts = rgb[op & ~dark]; rng = np.random.default_rng(1); K = 18
    c = pts[rng.choice(len(pts), K, replace=False)]
    for _ in range(40):
        lab = ((pts[:, None] - c[None]) ** 2).sum(-1).argmin(1)
        for k in range(K):
            if (lab == k).any(): c[k] = pts[lab == k].mean(0)
    med = np.array([pts[((pts - c[k]) ** 2).sum(-1).argmin()] for k in range(K)])   # real render colours (medoids)
    pal = np.vstack([INK[:3], med]).astype(int)
    idx = ((rgb[:, :, None] - pal[None, None]) ** 2).sum(-1).argmin(-1); idx[dark] = 0
    out = np.zeros_like(a); out[..., :3] = pal[idx]; out[..., 3] = np.where(op, 255, 0)
    # clean pass (new cut only): a lone pixel (no 8-neighbour of its colour), not ink, not on the silhouette edge,
    # takes the most common colour around it when that one is near it
    h, w = op.shape; o2 = out.copy()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not op[y, x] or idx[y, x] == 0: continue
            nb = [tuple(out[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx)]
            if any(n[3] == 0 for n in nb) or tuple(out[y, x]) in nb: continue
            nb = [n for n in nb if sum(n[:3]) >= 75]
            if not nb: continue
            m = max(set(nb), key=nb.count)
            if sum((int(m[i]) - int(out[y, x, i])) ** 2 for i in range(3)) < 90 ** 2: o2[y, x] = m
    return a.astype(np.uint8), o2.astype(np.uint8)


def chest(y): return 20 + (y - 21) // 6                              # his chest's front edge under the beard


def inside(poly, x, y):
    n, j, c = len(poly), len(poly) - 1, False
    for i in range(n):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c


ARM_OVER = [(19, 21), (28, 20), (33, 28), (24, 34), (19, 34)]       # where the render's arms lay over his chest


def rower_parts(cl):
    """By rule on the clean cut: the fists (one piece, stamped on the oar handle every frame), the torso without
    arms (chest refilled with the jumper's vertical ribs, as they run below the arms), nothing below the rail."""
    fists = np.zeros((11, 10, 4), np.uint8)
    for y in range(21, 32):
        for x in range(0, 10):
            if cl[y, x, 3] and x < 9 + (y > 26): fists[y - 21, x] = cl[y, x]
    for y in range(11):                                              # close the wrist (cut from the forearm) with ink
        xs = [x for x in range(10) if fists[y, x, 3]]
        if xs and xs[-1] >= 7: fists[y, xs[-1]] = INK
    t = cl.copy()
    rib = {x: cl[34, x].copy() for x in range(22, 39)}
    for y in range(20, 36):
        for x in range(0, 40):
            if 21 <= y and x < chest(y): t[y, x] = 0                  # arms and fists off, left of his chest
            elif inside(ARM_OVER, x + 0.5, y + 0.5) and t[y, x, 3] and x >= chest(y):
                t[y, x] = INK if x == chest(y) else rib[x if x >= 22 else x + 4]
    t[36:] = 0                                                       # the hull hides him from the rail down
    # one closed ink outline: a transparent pixel next to a non-ink edge pixel (where the render's edge was magenta
    # fringe, the nose and the brim) becomes ink; under the cut (row 35) the ink sits on row 36, on the rail's ink
    isink = lambda p: p[3] and int(p[0]) + int(p[1]) + int(p[2]) < 75
    o = t.copy()
    for y in range(37):
        for x in range(40):
            if t[y, x, 3] if y < 36 else False: continue
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < 36 and 0 <= xx < 40 and t[yy, xx, 3] and not isink(t[yy, xx]):
                    if y < 36 or dy == -1: o[y, x] = INK
                    break
    return fists, o


def oar_pose(phi, beta):
    """World points of the oar (as seen from the side): handle end, pivot, blade end."""
    rx, ry = ROWLOCK; Lin, Lout = 16, 48
    ux, uy = math.cos(math.radians(beta)) * math.sin(math.radians(phi)), math.sin(math.radians(beta))
    return (rx - Lin * ux, ry - Lin * uy), (rx, ry), (rx + Lout * ux, ry + Lout * uy), (ux, uy)


LOOP = [  # phi (fore-aft, + = blade aft/right), beta (tip: blade down), lean (px, - = forward/left)
    (40, 30, -2),    # catch: reached forward, blade goes in (splash)
    (15, 31, -1),    # drive
    (-12, 31, 0),    # drive
    (-36, 24, 1),    # finish: hands at his chest, blade comes out
    (-12, 12, 0),    # return: hands low, blade lifted over the water
    (20, 12, -1),    # return
]
FX0, FW = 62, 74             # the loop frame on the hull: hull x 62-135, rows as the hull (world y 176-237)


def limb(mask, p0, p1, rad):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy or 1
    for y in range(mask.shape[0]):
        for x in range(mask.shape[1]):
            t = max(0, min(1, ((x + 0.5 - x0) * dx + (y + 0.5 - y0) * dy) / L2))
            px, py = x0 + t * dx, y0 + t * dy
            if (x + 0.5 - px) ** 2 + (y + 0.5 - py) ** 2 <= rad * rad: mask[y, x] = True


def frame(torso, fists, phi, beta, lean):
    f = np.zeros((H, FW, 4), np.uint8)
    put = lambda wx, wy, c: f.__setitem__((wy - Y0, wx - FX0), c) if 0 <= wy - Y0 < H and 0 <= wx - FX0 < FW else None
    # 1 the torso, leaning
    for y in range(37):
        for x in range(40):
            if torso[y, x, 3]: put(RX0 + x + lean, Y0 + y, torso[y, x])
    # 2 the oar: a 1 px pole and a flat blade, lit over shade, one ink outline round both
    (hx, hy), _, (bx, by), (ux, uy) = oar_pose(phi, beta)
    core = np.zeros((H, FW), np.uint8)                                # 1 lit, 2 shade
    n = int(max(abs(bx - hx), abs(by - hy)) * 2) + 1
    for i in range(n + 1):
        t = i / n; x, y = hx + (bx - hx) * t, hy + (by - hy) * t
        cx, cy = int(math.floor(x)) - FX0, int(math.floor(y)) - Y0
        if 0 <= cy < H and 0 <= cx < FW: core[cy, cx] = 1
    u2 = ux * ux + uy * uy; ul = math.sqrt(u2)
    nx, ny = -uy / ul, ux / ul                                        # the blade's across direction (unit)
    if ny > 0: nx, ny = -nx, -ny                                      # pointing up: the lit side
    for y in range(H):
        for x in range(FW):
            wx, wy = x + FX0 + 0.5, y + Y0 + 0.5
            s = ((wx - 98) * ux + (wy - 211) * uy) / u2                # along the oar from the pivot (48 = blade end)
            d = (wx - 98) * nx + (wy - 211) * ny                       # across it, + = up
            if 35 <= s <= 48 and abs(d) <= 2.4 - max(0.0, (s - 46.0) * 0.8): core[y, x] = 1 if d > 0.3 else 2
    oarm = core > 0
    for y in range(H):
        for x in range(FW):
            if oarm[y, x]: f[y, x] = OAR_L if core[y, x] == 1 else OAR_S
    for y in range(H):
        for x in range(FW):
            if not oarm[y, x] and any(0 <= y + dy < H and 0 <= x + dx < FW and oarm[y + dy, x + dx]
                                      for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))): f[y, x] = INK
    # 3 the near arm, shoulder to wrist (two bones), in his sleeve's colours, outlined
    gx, gy = round(hx) + 1, round(hy)                                 # the grip: the near fist's middle on the handle
    wx, wy = gx + 5, gy                                               # his wrist, the fists' right side
    sx, sy = RX0 + 28 + lean, Y0 + 24                                 # his shoulder
    L1, L2 = 12, 12
    d = max(1e-6, math.hypot(wx - sx, wy - sy)); dd = min(d, L1 + L2 - 0.01)
    a1 = math.acos(max(-1, min(1, (L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd))))
    base = math.atan2(wy - sy, wx - sx)
    ex, ey = sx + L1 * math.cos(base - a1), sy + L1 * math.sin(base - a1)      # the elbow: down and back
    if ey < sy + L1 * math.sin(base + a1): ex, ey = sx + L1 * math.cos(base + a1), sy + L1 * math.sin(base + a1)
    am = np.zeros((H, FW), bool); limb(am, (sx - FX0, sy - Y0), (ex - FX0, ey - Y0), 2.8)
    fm = np.zeros((H, FW), bool); limb(fm, (ex - FX0, ey - Y0), (wx - FX0, wy - Y0), 2.2)
    arm = am | fm
    for y in range(H):
        for x in range(FW):
            if not arm[y, x] or y + Y0 >= RAIL_Y: continue
            px, py = x + FX0 + 0.5, y + Y0 + 0.5
            (p0, p1, r) = ((sx, sy), (ex, ey), 2.8) if am[y, x] else ((ex, ey), (wx, wy), 2.2)
            vx, vy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(vx, vy) or 1
            nxx, nyy = -vy / L, vx / L
            if nyy > 0: nxx, nyy = -nxx, -nyy                           # the normal pointing up
            dist = (px - p0[0]) * nxx + (py - p0[1]) * nyy              # + = toward the top side (lit)
            f[y, x] = ARM_L[0] + (255,) if dist > 0.2 else (ARM_L[1] + (255,) if dist > -1.2 else ARM_L[2] + (255,))
    for y in range(H):
        for x in range(FW):
            if arm[y, x] or y + Y0 >= RAIL_Y or (x + FX0 - sx) ** 2 + (y + Y0 - sy) ** 2 < 9: continue
            if any(0 <= y + dy < H and 0 <= x + dx < FW and arm[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                f[y, x] = INK
    for x in range(FW):                                               # the arm's cut at the rail: ink on the rail's row
        if arm[RAIL_Y - Y0 - 1, x] and f[RAIL_Y - Y0, x, 3] == 0: f[RAIL_Y - Y0, x] = INK
    # 4 the fists on the handle (stamped from the render)
    for y in range(11):
        for x in range(10):
            if fists[y, x, 3] and gy - 4 + y < RAIL_Y: put(gx - 4 + x, gy - 4 + y, fists[y, x])
            elif fists[y, x, 3] and gy - 4 + y == RAIL_Y: put(gx - 4 + x, RAIL_Y, INK)          # (cut at the rail)
    return f, (bx, by), (hx, hy)


FILES = {}


def build():
    FILES['riverwalk/art/scene/rw_rowboat.png'] = hull()
    raw, cl = rower_cut()
    fists, torso = rower_parts(cl)
    frames, info = [], []
    for phi, beta, lean in LOOP:
        f, blade, hand = frame(torso, fists, phi, beta, lean)
        frames.append(f); info.append({'phi': phi, 'beta': beta, 'lean': lean, 'blade_end': [round(blade[0], 1), round(blade[1], 1)],
                                       'handle': [round(hand[0], 1), round(hand[1], 1)]})
    FILES['riverwalk/art/scene/rw_rower.png'] = np.concatenate(frames, axis=1)
    FILES[SRC + '/cut.png'] = raw; FILES[SRC + '/clean.png'] = cl; FILES[SRC + '/torso.png'] = torso; FILES[SRC + '/fists.png'] = fists
    px = [[int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in torso[y, x])]
          for y, x in zip(*np.nonzero((torso != cl).any(-1)))]
    cpx = [[int(x), int(y), '#%02x%02x%02x%02x' % tuple(int(v) for v in cl[y, x])]
           for y, x in zip(*np.nonzero((cl != raw).any(-1)) )]
    return {'asset': 'rw_rower', 'base': f'{SRC}/cut.png = {RENDER} crop {list(CROP)}, 1:1, magenta keyed',
            'colours_and_clean': {'method': '18 render colours (medoids) + the ink, nearest colour; lone pixels take the most common neighbour', 'changed': len(cpx), 'pixels': cpx},
            'parts': {'method': 'arms and fists off left of the chest line, the chest under the arms refilled with the jumper ribs of row 34 (each column its own colour), rows 36+ dropped (the hull hides them); fists cut rows 21-31 cols 0-9, wrist closed with ink', 'changed': len(px), 'pixels': px},
            'loop': info}


def save(check):
    os.makedirs('art/source/rw_rowboat', exist_ok=True)
    bad = []
    for path, arr in FILES.items():
        if check:
            if not os.path.exists(path) or not np.array_equal(np.array(Image.open(path).convert('RGBA')), arr):
                bad.append(path)
        else:
            Image.fromarray(arr).save(path)
    return bad


if __name__ == '__main__':
    check = '--check' in sys.argv
    edits = build()
    os.makedirs(SRC, exist_ok=True)
    bad = save(check)
    if not check:
        json.dump(edits, open(SRC + '/edits.json', 'w'))
        cl = FILES[SRC + '/clean.png']
        json.dump({'name': 'rw_rower', 'size': [int(cl.shape[1]), int(cl.shape[0])], 'render': RENDER,
                   'cut_by': "SpriteCook's pixel output on its own grid, taken 1:1 (crop %s), nothing resampled; tools/build_rw_rowboat.py" % list(CROP),
                   'measures_px': {'cap_top_row': 0, 'face_rows': [8, 19], 'face_px': 12, 'head_with_cap_px': 21, 'gunwale_row': 36,
                                   'fists_on_handle': 'stamped on the oar handle in every frame (by construction)'},
                   'colours': len({tuple(v) for v in cl.reshape(-1, 4) if v[3]}), 'fails': []},
                  open('art/gen/out/rw_rower.cut.json', 'w'), indent=1)
        aseprite_io.write(SRC + '/rw_rower.aseprite', [FILES['riverwalk/art/scene/rw_rower.png'][:, i * FW:(i + 1) * FW] for i in range(len(LOOP))], ms=110)
        aseprite_io.write('art/source/rw_rowboat/rw_rowboat.aseprite', [FILES['riverwalk/art/scene/rw_rowboat.png']])
    b0, b1 = box()
    print('hull', W, 'x', H, 'box cols', b0, b1, 'sheer bow', sheer(0), 'stern', sheer(W - 1))
    if check:
        print('CHECK FAIL: ' + ', '.join(bad) if bad else 'CHECK PASS: every file is what the script builds')
        sys.exit(1 if bad else 0)
