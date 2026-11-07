#!/usr/bin/env python3
"""build_bikes_n07.py: the bikes of River Walk and Downtown, split into parts (track chars, 7 Nov 2026).

  python3 -I tools/build_bikes_n07.py           build everything
  python3 -I tools/build_bikes_n07.py --check   fail if a file on disk differs from what this script builds

Owner, board 7 Nov: cyclist_adult1 "redraw: terrible details", cyclist_adult2 "fix: terrible details", the cargo bike
"needs total rework, the details are off, stray pixels etc". The 5 and 6 Nov bikes were one SpriteCook picture each:
lumpy wheels, ragged tubes, mottled coats, legs re-drawn over a picture. As the 6 Nov rowing boat (approved), a bike
is now made of parts:
  RIDER  the only DRAWN part: SpriteCook GPT 2.5 render art/gen/renders/rw_riders_n07_a_raw.png (job 424061dc), cut
         1:1 on its own 4 px grid (tools/grid4_cut.py: 95 % clean cells; Pepper 52 x 38 in it, so the riders are at
         true scale, 1.85 m with the helmet = 85-87 px), magenta keyed (the magenta fringe too), each rider's colours
         reduced to its own most used ones (nearest colour, never an average), a clean pass on the new cut; then by
         rule: the legs and shoes taken off below the hip (they are keyed per pedal frame).
  LEGS   keyed by rule per frame, as the rower's arm: hip on the saddle, thigh 19 px and shin 21 px (two-bone reach,
         the knee forward), in the rider's own three trouser colours (near leg lit on top, shaded under; far leg one
         step darker), a shoe of the rider's own shoe colours on each pedal.
  BIKE   BUILT by rule at 46 px a metre: wheels 31 px (0.68 m) with an ink tyre edge, a grey tyre, a silver rim, a
         dark inner rim, 8 even dark spokes turned 11.25 degrees a frame, a hub; a Dutch city frame (step-through
         for her, a diamond frame for him) as 1 px tubes in the frame's colour inside one ink outline, mudguards,
         a closed chain case, chainring and crank (one turn in 8 frames), a leather saddle, swept-back bars, a front
         lamp, her wicker basket, his rear rack. The cargo bike: the same rider geometry over a 0.66 m rear wheel,
         a long low beam to a 0.5 m front wheel, a wooden plank box of round loaves and a baguette between them.
  INK    one 1 px ink outline round the rider, the frame and the parts; the wheels carry their own (the spokes
         stay 1 px and dark, so the see-through wheel passes the outline check).
Promenade bikes face RIGHT (road.lua and stage.lua mirror them), the cargo bike faces LEFT (built facing right and
mirrored, so the baker keeps his own light). Light from the upper left on the built parts.
Files: riverwalk/art/scene/cyclist_adult1.png, cyclist_adult2.png (88 x 87) + _pedal.png (8 x 88 x 87);
cargo_bike.png (116 x 88) + cargo_bike_pedal.png (8 x 116 x 88). Every changed pixel of the rider cuts is listed in
art/source/bikes_n07/edits.json; .aseprite sources there."""
import json, math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io

CUT = 'art/gen/out/rw_riders_n07_a_cut.png'        # tools/grid4_cut.py art/gen/renders/rw_riders_n07_a_raw.png (phase 0,0)
SRC = 'art/source/bikes_n07'
hexc = lambda h: (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))
INK = hexc('#17181f')
TYRE = hexc('#3a3c44')
STEEL, STEEL_D = hexc('#b4bac4'), hexc('#5d626c')
RIM, RIM_IN, SPOKE, HUB = STEEL, INK, TYRE, STEEL      # (asset_qa: 20 colours: the parts share 6)
CASE, CASE_L = INK, STEEL_D
LAMP = STEEL
LEATHER, LEATHER_L = hexc('#6b4128'), hexc('#a8723a')
WICKER = [STEEL, hexc('#a8723a'), hexc('#6b4128')]   # a wire rim, wicker body, ribs
BREAD = [hexc('#f2c97a'), hexc('#d99a4a')]
WOOD = [BREAD[1], hexc('#a8723a'), hexc('#a8723a'), hexc('#6b4128')]   # the box shares the bread's and the leather's colours
FRAMES = {'black': [STEEL_D, TYRE]}      # 'jeans': the rider's own two lighter trouser colours (set per bike)

# bike geometry, image coords facing right, ground row 86 (rw_riders_n07.py blockout uses the same)
G = 86
WR = 15                       # wheel radius: 31 px across
HIP = (36, 47)
RIDER_DY = 2                  # the render's helmet sits 3 px over the spec: the rider is set 2 px down on the saddle
BB = (40, 74)
CRANK = 7
L1, L2 = 19, 21

# the riders in the cut: columns, the blockout's image offset (rw_riders_n07.py), flipped (faces left)
RIDERS = {
    'A': dict(cols=(60, 118), ox=46, flip=False),
    'B': dict(cols=(119, 175), ox=104, flip=False),
    'C': dict(cols=(176, 236), ox=154, flip=True),
}
GROUND_IN_CUT = 200
N_RIDER = 13


def is_key(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return (r > 170 and b > 170 and g < 120) or (r > 120 and b > 110 and g < min(r, b) - 70)


def rider_cut(cut, who, log):
    """one rider from the cut, in its 88 x 87 image coords facing RIGHT (C is mirrored), keyed and reduced"""
    R = RIDERS[who]; x0, x1 = R['cols']
    W, H = 88, 87
    out = np.zeros((H, W, 4), np.uint8)
    for y in range(cut.shape[0]):
        iy = y - GROUND_IN_CUT + G
        if not 0 <= iy < H: continue
        for x in range(x0, x1):
            c = cut[y, x]
            if is_key(c): continue
            ix = x - R['ox'] if not R['flip'] else 87 - (x - R['ox'])
            if 0 <= ix < W: out[iy, ix, :3] = c[:3]; out[iy, ix, 3] = 255
    # colours: the render's pixels carry small noise (about 1,900 colours per rider). Groups of near colours (5 bits
    # a channel) each stand for their most frequent real colour; the most used groups are kept while at least T apart
    # (T grows until at most N are left), and every pixel takes the nearest kept colour: real colours, never averages
    m = out[..., 3] > 0
    px = out[m][:, :3].astype(int)
    key = (px[:, 0] >> 3) * 1024 + (px[:, 1] >> 3) * 32 + (px[:, 2] >> 3)
    reps = []
    for kk in np.unique(key):
        g = px[key == kk]; u, cn = np.unique(g, axis=0, return_counts=True); reps.append((len(g), u[np.argmax(cn)]))
    reps.sort(key=lambda t: -t[0])
    wd = np.array([1.0, 1.3, 0.8])
    fixed = [np.array(c_) for c_ in (INK, TYRE, STEEL_D, STEEL, LEATHER, LEATHER_L)]   # the parts' colours: shared
    for T in range(18, 80, 2):
        keep = list(fixed)
        for n_, c_ in reps:
            if n_ < 3: continue
            if all((((c_ - k_) * wd) ** 2).sum() > T * T for k_ in keep): keep.append(c_)
        if len(keep) <= N_RIDER + len(fixed): break
    keep = np.array(keep)
    d = ((((px[:, None, :] - keep[None, :, :]) * wd) ** 2).sum(-1))
    newpx = keep[np.argmin(d, 1)]
    ys, xs = np.nonzero(m)
    for (y, x, a_, b_) in zip(ys, xs, px, newpx):
        if (a_ != b_).any(): log.append([who, 'reduce', int(x), int(y), a_.tolist(), b_.tolist()])
    out[m, :3] = newpx
    # the darkest kept colour is the rider's ink: unify it with the family ink
    lum = keep @ np.array([0.299, 0.587, 0.114])
    ink = keep[np.argmin(lum)]
    out[m & np.all(out[..., :3] == ink, -1), :3] = INK
    # by rule: the coat's red that the reduction gave to cheek and brow pixels in the head (rows 0-19) becomes the
    # face's own shade (the skin colour next darker than the lightest)
    if who == 'A':
        hm = m.copy(); hm[17:] = False
        sk = [tuple(c) for c in keep.tolist() if c[0] > 200 and 140 < c[1] < 200 and c[2] < 170]
        sk.sort(key=lambda c: -sum(c))
        if len(sk) >= 2:
            red = [tuple(c) for c in keep.tolist() if c[0] > c[1] + 60 and c[0] > c[2] + 50 and c[0] < 235]
            for y, x in zip(*np.nonzero(hm)):
                if tuple(out[y, x, :3]) in red: log.append([who, 'face', int(x), int(y), out[y, x, :3].tolist(), list(sk[1])]); out[y, x, :3] = sk[1]
    # clean pass on the new cut: lone pixels (no 4-neighbour of their colour, 3+ of one other non-ink colour)
    o = out.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not o[y, x, 3] or tuple(o[y, x, :3]) == INK: continue
            nb = [tuple(o[y + dy, x + dx, :3]) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if o[y + dy, x + dx, 3]]
            if tuple(o[y, x, :3]) in nb: continue
            cand = [n for n in nb if n != INK]
            if cand:
                best = max(set(cand), key=cand.count)
                if cand.count(best) >= 3:
                    log.append([who, 'lone', x, y, o[y, x, :3].tolist(), list(best)]); out[y, x, :3] = best
    # small patches (1-24 px) of a colour inside one surrounding fill of a near colour (within 45 luma, never the ink)
    # take that fill: the render's dabs and the reduction's speckle (asset_qa noise and blotches)
    lumf = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    for _ in range(2):
        seen = np.zeros((H, W), bool); o = out.copy()
        for y0 in range(H):
            for x0 in range(W):
                if seen[y0, x0] or not o[y0, x0, 3] or tuple(o[y0, x0, :3]) == INK: continue
                col = tuple(o[y0, x0, :3]); st = [(y0, x0)]; seen[y0, x0] = True; comp = []
                while st:
                    y, x = st.pop(); comp.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and not seen[yy, xx] and o[yy, xx, 3] and tuple(o[yy, xx, :3]) == col:
                            seen[yy, xx] = True; st.append((yy, xx))
                if len(comp) > 24: continue
                ring = []
                cs = set(comp)
                for y, x in comp:
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if (yy, xx) in cs: continue
                        ring.append(tuple(o[yy, xx, :3]) if 0 <= yy < H and 0 <= xx < W and o[yy, xx, 3] else None)
                if None in ring or not ring: continue
                best = max(set(ring), key=ring.count)
                lim = 45 if len(comp) <= 4 else 32                  # (a 5-24 px patch: a blotch in asset_qa's words)
                if best != INK and ring.count(best) >= 0.75 * len(ring) and abs(lumf(best) - lumf(col)) < lim:
                    for y, x in comp: log.append([who, 'patch', x, y, list(col), list(best)]); out[y, x, :3] = best
    return out


def leg_palette(r, who):
    """the trouser and shoe colours, read off the cut's legs (rows 62-78 for trousers, the shoe rows 79-84)"""
    def cols(y0, y1):
        sub = r[y0:y1]; m = sub[..., 3] > 0
        px = [tuple(c) for c in sub[m][:, :3].tolist() if tuple(c) not in (INK, TYRE)]
        u = {}
        for c in px: u[c] = u.get(c, 0) + 1
        return sorted(u, key=lambda c: -u[c])
    sh = cols(80, 85)[:2]
    tr = [c for c in cols(60, 76) if c not in sh and c not in (LEATHER, LEATHER_L)]
    sat = lambda c: max(c) - min(c)
    tr = [c for c in tr if abs(sat(c) - sat(tr[0])) < 30][:3]          # one material: the main trouser colour's family
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    tr = sorted(tr, key=lum, reverse=True); sh = sorted(sh, key=lum, reverse=True)
    while len(tr) < 3: tr.append(tr[-1])
    while len(sh) < 2: sh.append(sh[-1])
    return tr, sh


def strip_legs(r, who, tr, sh, hem, log):
    """the legs and shoes off: trouser and shoe colours from the hem down, then ink left with nothing to outline"""
    o = r.copy(); H, W = r.shape[:2]
    kill = set(map(tuple, tr)) | set(map(tuple, sh)) | {LEATHER, LEATHER_L, TYRE, STEEL_D}
    for y in range(hem, H):
        for x in range(W):
            if o[y, x, 3] and tuple(o[y, x, :3]) in kill: log.append([who, 'leg', x, y, o[y, x, :3].tolist(), 'off']); o[y, x] = 0
    for y in range(hem - 2, H):                                  # everything under the hem but the coat itself goes
        for x in range(W):
            if y >= hem + 2 and o[y, x, 3] and tuple(o[y, x, :3]) != INK:
                log.append([who, 'leg', x, y, o[y, x, :3].tolist(), 'off']); o[y, x] = 0
    # bits left under the hem (a boot's edge, a fold): pieces of under 8 px are dropped
    seen = np.zeros((H, W), bool)
    for y0, x0 in zip(*np.nonzero(o[..., 3] > 0)):
        if seen[y0, x0] or y0 < hem: continue
        st = [(y0, x0)]; seen[y0, x0] = True; comp = []
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and o[yy, xx, 3] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
        if len(comp) < 8:
            for y, x in comp: log.append([who, 'bit', x, y, o[y, x, :3].tolist(), 'off']); o[y, x] = 0
    changed = True
    while changed:                                               # ink that outlines nothing any more
        changed = False
        for y in range(H):
            for x in range(W):
                if o[y, x, 3] and tuple(o[y, x, :3]) == INK:
                    ok = False
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < H and 0 <= xx < W and o[yy, xx, 3] and tuple(o[yy, xx, :3]) != INK: ok = True
                    if not ok: o[y, x] = 0; changed = True; log.append([who, 'ink', x, y, list(INK), 'off'])
    return o


# ---- drawing helpers (binary, on a numpy canvas)
def seg_mask(W, H, p, q, w):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    px, py = p; qx, qy = q; dx, dy = qx - px, qy - py; L2_ = dx * dx + dy * dy or 1
    t = np.clip(((xx - px) * dx + (yy - py) * dy) / L2_, 0, 1)
    d = np.hypot(xx - (px + t * dx), yy - (py + t * dy))
    return d <= w / 2


def line_px(p, q):
    """Bresenham, 1 px"""
    (x0, y0), (x1, y1) = (int(round(p[0])), int(round(p[1]))), (int(round(q[0])), int(round(q[1])))
    pts = []; dx, dy = abs(x1 - x0), -abs(y1 - y0); sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1); err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy
    return pts


class Canvas:
    def __init__(self, W, H):
        self.W, self.H = W, H; self.a = np.zeros((H, W, 3), np.uint8); self.m = np.zeros((H, W), bool)
        self.ol = np.zeros((H, W), bool)               # pixels that take part in the ink outline

    def px(self, x, y, c, ol=True):
        if 0 <= x < self.W and 0 <= y < self.H: self.a[y, x] = c; self.m[y, x] = True; self.ol[y, x] |= ol

    def mask(self, mk, c, ol=True):
        self.a[mk] = c; self.m |= mk
        if ol: self.ol |= mk

    def tube(self, p, q, col, w=1):
        """a tube core: 1 px (or 2 px: lit top/left and the frame's dark under it) in the frame colours"""
        pts = line_px(p, q)
        steep = abs(q[1] - p[1]) > abs(q[0] - p[0])
        for x, y in pts:
            self.px(x, y, col[0])
            if w == 2: self.px(x + (1 if steep else 0), y + (0 if steep else 1), col[1])

    def sprite(self, img, ox, oy, ol=True):
        m = img[..., 3] > 0; ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            self.px(x + ox, y + oy, tuple(img[y, x, :3]), ol)


def wheel_img(R, phase):
    D = 2 * R + 1; a = np.zeros((D, D, 4), np.uint8)
    yy, xx = np.mgrid[0:D, 0:D]; dx, dy = xx - R, yy - R; r = np.hypot(dx, dy)
    def put(mk, c): a[mk, :3] = c; a[mk, 3] = 255
    put((r <= R + 0.5) & (r > R - 0.6), INK)
    put((r <= R - 0.6) & (r > R - 2.0), TYRE)
    put((r <= R - 2.0) & (r > R - 2.9), RIM)
    put((r <= R - 2.9) & (r > R - 4.3), RIM_IN)
    for k in range(8):
        th = math.radians(phase + k * 45)
        for x, y in line_px((R + 2.2 * math.cos(th), R + 2.2 * math.sin(th)), (R + (R - 3.5) * math.cos(th), R + (R - 3.5) * math.sin(th))):
            put((yy == y) & (xx == x), SPOKE)
    put(r <= 2.3, RIM_IN); put(r <= 1.0, HUB)
    return a


def ik(hip, ankle, l1=L1, l2=L2, fwd=1):
    """knee of a two-bone leg from hip to ankle, bent forward"""
    hx, hy = hip; ax, ay = ankle; dx, dy = ax - hx, ay - hy; d = min(math.hypot(dx, dy), l1 + l2 - 0.01)
    a = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    base = math.atan2(dy, dx)
    ang = base - a * fwd                                  # the knee towards the front (x+) and up
    return (hx + l1 * math.cos(ang), hy + l1 * math.sin(ang))


def draw_leg(c, hip, pedal, tr, sh, far):
    """thigh 6 px, shin 5 px, the shoe 7 x 3 on the pedal; near: lit top row, shade under; far: one step darker"""
    W, H = c.W, c.H
    ankle = (pedal[0] - 1, pedal[1] - 3)
    knee = ik(hip, ankle)
    lit, mid, dk = (tr[1], tr[1], INK) if far else (tr[0], tr[0], tr[1])
    mk = seg_mask(W, H, hip, knee, 6.2) | seg_mask(W, H, knee, ankle, 4.8)
    c.mask(mk, mid)
    top = mk & ~np.roll(mk, 1, 0); bot = mk & ~np.roll(mk, -1, 0)
    c.a[bot] = dk                                            # (no lit top row: on a slanted leg it is a stair of single pixels)
    # shoe: heel over the ankle, toe forward, sole on the pedal row
    sx, sy = int(round(pedal[0])), int(round(pedal[1]))
    s_top, s_bot = (sh[1], INK) if far else (sh[0], sh[1])
    for x in range(sx - 3, sx + 3): c.px(x, sy - 2, s_top)
    for x in range(sx - 3, sx + 4): c.px(x, sy - 1, s_top)
    for x in range(sx - 3, sx + 4): c.px(x, sy, s_bot)
    return knee


def crank_pts(theta):
    t = math.radians(theta)
    return (BB[0] + CRANK * math.cos(t), BB[1] + CRANK * math.sin(t))


def build_bike(rider, legs, kind, frame_col, k, extras):
    """one frame k (0-7) of a promenade bike, image 88 x 87 facing right"""
    W, H = 88, 87; c = Canvas(W, H); col = FRAMES[frame_col] if frame_col in FRAMES else [legs[0][0], legs[0][1]]
    rear, front = (17, G - WR), (68, G - WR)
    theta = k * 45.0                                       # the near pedal: frame 0 at 3 o'clock (forward)
    # far crank and far leg (behind the frame)
    fp = crank_pts(theta + 180)
    draw_leg(c, (HIP[0] - 1, HIP[1]), fp, *legs, far=True)
    for x, y in line_px(BB, fp): c.px(x, y, STEEL_D)
    # frame
    seat = (34, 48); head_top, head_bot = (61, 47), (63, 55)
    c.tube(BB, seat, col, 2)                                # seat tube
    c.tube(seat, rear, col)                                 # seat stay
    c.tube(BB, rear, col)                                   # chain stay
    if kind == 'step':                                      # step-through: a swept down tube, a low second tube
        for p, q in (((41, 72), (48, 64)), ((48, 64), (62, 54))): c.tube(p, q, col, 2)
        c.tube((36, 64), (50, 60), col); c.tube((50, 60), (62, 51), col)
    else:                                                   # diamond: top tube and down tube
        c.tube((35, 50), head_top, col, 2); c.tube(BB, head_bot, col, 2)
    c.tube(head_top, head_bot, col, 2)                      # head tube
    c.tube(head_bot, front, col, 2)                         # fork
    c.tube((33, 48), (33, 46), (STEEL, STEEL_D))            # seat post
    # mudguards: arcs over both wheels, 1 px of the frame colour
    for (cx, cy), a0, a1 in ((rear, 196, 350), (front, 196, 344)):
        for d in range(a0, a1, 1):
            t = math.radians(d); c.px(int(round(cx + (WR + 1.2) * math.cos(t))), int(round(cy + (WR + 1.2) * math.sin(t))), col[0])
    # chain case: a closed plate from the chainring to the rear hub
    from PIL import Image as _I, ImageDraw as _D
    im = _I.new('L', (W, H), 0); _D.Draw(im).polygon([(19, 69), (37, 70), (43, 72), (43, 76), (37, 78), (19, 73)], fill=255)
    cm = np.array(im) > 0; c.mask(cm, CASE); c.a[cm & ~np.roll(cm, 1, 0)] = CASE_L
    # rack (his) and basket (hers)
    if 'rack' in extras:
        c.tube((8, 52), (30, 52), (STEEL, STEEL_D)); c.tube((9, 52), (15, 70), (STEEL, STEEL_D)); c.tube((28, 52), (33, 48), (STEEL, STEEL_D))
    # saddle
    for y, x0, x1 in ((44, 29, 38), (45, 29, 37), (46, 31, 35)):
        for x in range(x0, x1): c.px(x, y, LEATHER_L if y == 44 else LEATHER)
    # near crank, chainring
    c.mask(seg_mask(W, H, BB, BB, 3.2), STEEL)
    np_ = crank_pts(theta)
    # wheels (own ink, drawn now so the legs and the rider sit over them; not part of the outline pass)
    phase = k * 11.25
    wim = wheel_img(WR, phase)
    for (cx, cy) in (rear, front):
        wm = wim[..., 3] > 0; ys, xs = np.nonzero(wm)
        for y, x in zip(ys, xs):
            X, Y = x + cx - WR, y + cy - WR
            if not c.m[Y, X]: c.px(X, Y, tuple(wim[y, x, :3]), ol=False)
    # bars: stem, swept-back bars to the grip under the hand, a front lamp
    c.tube(head_top, (62, 44), (STEEL, STEEL_D)); c.tube((62, 44), (66, 43), (STEEL, STEEL_D)); c.tube((66, 43), (61, 42), (STEEL, STEEL_D))
    c.px(65, 52, LAMP); c.px(66, 52, LAMP); c.px(65, 53, STEEL_D); c.px(66, 53, STEEL_D)
    if 'basket' in extras:                                  # wicker: 14 x 9 on the bars, over the front wheel
        for y in range(43, 52):
            for x in range(65, 79):
                rim = y == 43; rib = (x - 65) % 4 == 2; foot = y == 51
                c.px(x, y, WICKER[0] if rim else (WICKER[2] if (rib or foot) else WICKER[1]))
    # near leg, then its crank arm and pedal, then the rider over everything (coat over the thigh's top)
    draw_leg(c, HIP, np_, *legs, far=False)
    for x, y in line_px(BB, np_): c.px(x, y, STEEL)
    c.sprite(rider, 0, RIDER_DY)
    return c


def finish(c):
    """the ink outline round the outlined parts, on transparent pixels only"""
    H, W = c.H, c.W; ol = c.ol; out = np.zeros_like(ol)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = np.zeros_like(ol); ys0, ys1 = max(0, dy), H + min(0, dy); xs0, xs1 = max(0, dx), W + min(0, dx)
        sh[ys0:ys1, xs0:xs1] = ol[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]; out |= sh
    out &= ~c.m
    rgba = np.zeros((H, W, 4), np.uint8); rgba[c.m, :3] = c.a[c.m]; rgba[c.m, 3] = 255
    rgba[out, :3] = INK; rgba[out, 3] = 255
    return rgba


def build_cargo(rider, legs, k):
    """one frame of the Downtown cargo bike (a long john), 116 x 88, built facing right (mirrored at the end):
    the rider over a 0.66 m rear wheel with the promenade geometry (rows +1: ground row 87), a long low beam forward
    to a 0.5 m front wheel, a plank box of bread between them. The hit box (arthooks.lua: the left 80 px of the
    left-facing image, bottom 26 px) is the front wheel and the box"""
    W, H = 116, 88; g = 87; c = Canvas(W, H); col = [STEEL_D, TYRE]
    dy = g - G                                          # 1: the cargo image is one row taller than the promenade bikes
    P = lambda p: (p[0], p[1] + dy)
    rear, front, fr = (17, g - WR), (101, g - 11), 11
    theta = k * 45.0
    fp = P(crank_pts(theta + 180))
    draw_leg(c, P((HIP[0] - 1, HIP[1])), fp, *legs, far=True)
    for x, y in line_px(P(BB), fp): c.px(x, y, STEEL_D)
    seat = P((34, 48))
    c.tube(P(BB), seat, col, 2); c.tube(seat, rear, col); c.tube(P(BB), rear, col)
    c.tube((33, 48 + dy), (33, 46 + dy), (STEEL, STEEL_D))
    # the long john: head tube behind the box, a low beam from the bottom bracket under the box to the front fork
    head_top, head_bot = (52, 46 + dy), (54, 60 + dy)
    c.tube(seat, head_top, col, 2); c.tube(head_top, head_bot, col, 2); c.tube(P(BB), (56, 78 + dy), col, 2)
    c.tube((56, 78 + dy), (92, 78 + dy), col, 2); c.tube((92, 78 + dy), front, col, 2); c.tube((92, 66 + dy), front, col, 2)
    c.tube((56, 70 + dy), (92, 70 + dy), (STEEL, STEEL_D))   # the steering rod to the front fork
    for (cx, cy), r_, a0, a1 in ((rear, WR, 196, 350), (front, fr, 200, 340)):
        for d in range(a0, a1):
            t = math.radians(d); c.px(int(round(cx + (r_ + 1.2) * math.cos(t))), int(round(cy + (r_ + 1.2) * math.sin(t))), col[0])
    from PIL import Image as _I, ImageDraw as _D
    im = _I.new('L', (W, H), 0); _D.Draw(im).polygon([(19, 69 + dy), (37, 70 + dy), (43, 72 + dy), (43, 76 + dy), (37, 78 + dy), (19, 73 + dy)], fill=255)
    cm = np.array(im) > 0; c.mask(cm, CASE); c.a[cm & ~np.roll(cm, 1, 0)] = CASE_L
    for y, x0, x1 in ((44, 29, 38), (45, 29, 37), (46, 31, 35)):
        for x in range(x0, x1): c.px(x, y + dy, LEATHER_L if y == 44 else LEATHER)
    c.mask(seg_mask(W, H, P(BB), P(BB), 3.2), STEEL)
    np_ = P(crank_pts(theta))
    phase = k * 11.25
    for (cx, cy), r_ in ((rear, WR), (front, fr)):
        wim = wheel_img(r_, phase * WR / r_ if r_ != WR else phase)
        ys, xs = np.nonzero(wim[..., 3] > 0)
        for y, x in zip(ys, xs):
            X, Y = x + cx - r_, y + cy - r_
            if not c.m[Y, X]: c.px(X, Y, tuple(wim[y, x, :3]), ol=False)
    # the box: 0.8 m long, 0.45 m deep, planks (lit top edge, mid, a dark seam every 6 rows), corner posts, on the beam
    bx0, bx1, by0, by1 = 58, 92, 60 + dy, 77 + dy
    # bread first (it stands in the box, the box's front plank hides its bottom): three round loaves and a baguette
    for (lx, ly, lw, lh) in ((61, 52, 10, 9), (70, 51, 11, 10), (79, 52, 10, 9)):
        mk = np.zeros((H, W), bool); yy, xx = np.mgrid[0:H, 0:W]
        mk = ((xx - (lx + lw / 2 - 0.5)) / (lw / 2)) ** 2 + ((yy - (ly + dy + lh - 0.5)) / lh) ** 2 <= 1.0
        mk &= yy < by0 + 1
        c.mask(mk, BREAD[1]); c.a[mk & ~np.roll(mk, 1, 0)] = BREAD[0]; c.a[mk & ~np.roll(mk, 1, 1)] = BREAD[0]
        c.a[mk & ~np.roll(mk, -1, 1)] = WOOD[1]                  # each loaf's right edge in the crust's dark: they part
        for sx in (lx + 2, lx + lw - 4):                       # two score marks, light
            for t in range(2): c.px(sx + t, ly + dy + 2 + t, BREAD[0])
    bag = seg_mask(W, H, (85, 40 + dy), (88, 60 + dy), 3.6)    # the baguette, upright at the front corner
    c.mask(bag & ~c.m, BREAD[1]); c.a[bag & ~np.roll(bag, 1, 1)] = BREAD[0]
    for yb in (43, 48, 53): c.px(86, yb + dy, BREAD[0]); c.px(87, yb + 1 + dy, BREAD[0])
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            post = x in (bx0, bx0 + 1, bx1 - 1, bx1)
            r_ = (y - by0) % 6 if y < by1 - 1 else 5
            colr = WOOD[3] if post and r_ != 0 else (WOOD[0] if r_ == 0 else (WOOD[3] if r_ == 5 else (WOOD[1] if r_ < 3 else WOOD[2])))
            c.px(x, y, colr)
    # bars: stem behind the box, grips under the hands
    c.tube(head_top, (54, 43 + dy), (STEEL, STEEL_D)); c.tube((54, 43 + dy), (60, 43 + dy), (STEEL, STEEL_D))
    c.px(91, 62 + dy, STEEL); c.px(91, 63 + dy, STEEL)          # a lamp on the box's front post
    draw_leg(c, P(HIP), np_, *legs, far=False)
    for x, y in line_px(P(BB), np_): c.px(x, y, STEEL)
    c.sprite(rider, 0, RIDER_DY + dy)
    return c


BIKES = {
    'cyclist_adult1': dict(who='A', kind='step', frame='black', extras=['basket'], hem=52),
    'cyclist_adult2': dict(who='B', kind='diamond', frame='jeans', extras=['rack'], hem=47),
}


def main():
    check = '--check' in sys.argv; bad = 0; log = []
    cut = np.array(Image.open(CUT).convert('RGB'))
    os.makedirs(SRC, exist_ok=True)
    files = {}
    for name, b in BIKES.items():
        r = rider_cut(cut, b['who'], log)
        tr, sh = leg_palette(r, b['who'])
        top = strip_legs(r, b['who'], tr, sh, b['hem'], log)
        frames = [finish(build_bike(top, (tr, sh), b['kind'], b['frame'], k, b['extras'])) for k in range(8)]
        files[f'riverwalk/art/scene/{name}.png'] = frames[0]
        files[f'riverwalk/art/scene/{name}_pedal.png'] = np.concatenate(frames, axis=1)
        if not check: aseprite_io.write(f'{SRC}/{name}.aseprite', frames, ms=90)
    r = rider_cut(cut, 'C', log)
    tr, sh = leg_palette(r, 'C')
    top = strip_legs(r, 'C', tr, sh, 50, log)
    frames = [finish(build_cargo(top, (tr, sh), k))[:, ::-1].copy() for k in range(8)]
    files['riverwalk/art/scene/cargo_bike.png'] = frames[0]
    files['riverwalk/art/scene/cargo_bike_pedal.png'] = np.concatenate(frames, axis=1)
    if not check: aseprite_io.write(f'{SRC}/cargo_bike.aseprite', frames, ms=90)
    for p, a in files.items():
        if check:
            same = os.path.exists(p) and np.array_equal(np.array(Image.open(p).convert('RGBA')), a)
            print(p, 'OK' if same else 'DIFFERS'); bad += not same
        else:
            Image.fromarray(a).save(p); print(p, a.shape[1], 'x', a.shape[0])
    if not check:
        json.dump({'tool': 'tools/build_bikes_n07.py', 'cut': CUT, 'edits': log}, open(f'{SRC}/edits.json', 'w'), default=lambda v: v.tolist() if hasattr(v, 'tolist') else int(v))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
