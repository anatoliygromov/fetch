#!/usr/bin/env python3
"""tools/build_dt_rooftops.py: the tall Downtown's low row, option A (day/07nov-dt; design docs/review/07nov/dt/design/,
targets art/gen/concepts/dt_design_A1_a.png .. A4_a.png, never cut).

The street is lined with LOW true-scale buildings (46 px/m) whose roofs are the high road: a two-storey bakery, its
flat-roofed wing (the old BALCONY box), the three-arch cafe arcade (LOGGIA), the guild hall with its stepped gable
(GUILD ROOF and its steps, the CHIMNEY on the ridge), two market pavilions with lead roofs (the GALLERY boxes) and
shop canopies (the middle tier's BALCONY boxes), the tram shed (DORMER), the kiosk house and the shelter house
(the roof ledges), the glass flower hall with its roof garden (FLOWER ROOF), the canal house (the last ledge).
Behind them the mid row (town_facades.png, scroll 0.5) and the sky. Screens 1-3 and 9-11 get one-storey houses
with decorative roofs on the `closed` boxes (and the plain fronts after the canal); the start house is two storeys
with a roof (town_door's ground floor unchanged).

Everything is BUILT: the ground floors are whole-pixel crops of the approved styled fronts (town_front_tall<k>_<s>,
rows 284-431, plaster swapped as arthooks.lua does), the roofs are stamped parts (a tile course, a ridge, a lead
sheet, a coping, a parapet, a chimney, a dormer, a window box) on the integer grid. Roofs Pepper walks on are play
pieces: an unbroken 1 px ink outline, drawn unfaded, the art's top row at the box's top - 1. Fronts are decoration:
no outline, faded 28 % by the game (their colours are source values, as the fronts' own).

Files (riverwalk/art/scene/): dtl_<name>_front.png, dtl_<name>_roof.png, dtl_<name>_canopy<k>.png,
dtl_closed<k>.png; the placement table riverwalk/dt_lowrow.lua (read by arthooks.lua).

  python3 -I tools/build_dt_rooftops.py            write them
  python3 -I tools/build_dt_rooftops.py --check    fail if a file on disk differs from the build
"""
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "riverwalk", "art", "scene")
STREET, BACK = 424, 414                    # her street; the back line the fronts stand on
GF_TOP = 284                               # the front files' row where the ground floor's plain wall starts

# ---- colours ------------------------------------------------------------------------------------------------------
INK = (18, 18, 26, 255)
# play pieces (not faded): on-screen values, a step darker than the fronts (the ladder: her line is the darkest)
TILE = [(204, 104, 70), (172, 78, 54), (136, 58, 42), (100, 42, 34)]           # lit, mid, shade, joint
LEAD = [(176, 180, 186), (140, 146, 154), (108, 114, 122), (84, 90, 98)]
GRAN = [(172, 166, 154), (140, 134, 124), (108, 102, 94), (80, 76, 70)]
BRICK = [(166, 86, 62), (132, 64, 48), (98, 46, 36)]
MORTAR = (196, 176, 150)
WOOD = [(168, 118, 70), (128, 86, 50), (90, 58, 36)]
CANVAS = [(222, 214, 198), (196, 62, 58), (150, 44, 44)]
IRON = [(70, 96, 84), (46, 66, 58)]
GLASS = [(150, 184, 206), (112, 146, 172), (84, 112, 140)]
LEAF = [(92, 142, 70), (58, 100, 50)]
BLOOM = [(212, 64, 70), (236, 150, 60), (230, 120, 160), (244, 220, 90)]
SOIL = (82, 58, 42)
# decoration (faded 28 % towards efe6da by the game): source values, so the roofs sit one step lighter than the play roofs
# (the decorative roofs use the styled fronts' own ramps, so a front with its roof stays within the back layer's 20
# colours: the oak ramp J / K / D as brown clay tile, the granite L / T / V as coping, parapet, lead and chimney cap)
D_TILE = [(136, 92, 60), (104, 66, 44), (68, 44, 32), (68, 44, 32)]
D_LEAD = [(135, 130, 120), (110, 103, 95), (77, 72, 68), (77, 72, 68)]
D_GRAN = [(135, 130, 120), (110, 103, 95), (77, 72, 68), (77, 72, 68)]
D_BRICK = [(136, 92, 60), (104, 66, 44), (68, 44, 32)]
D_MORTAR = (68, 44, 32)
D_GLASS = [(100, 128, 150), (72, 98, 120)]
D_IRON = [(44, 64, 56), (28, 42, 36)]
D_DARK = (40, 34, 36)                                    # an alley's / arcade's inside
D_PLASTER = {"yellow": ((135, 106, 66), (116, 85, 53)), "red": ((154, 82, 63), (127, 64, 51)), "cream": ((129, 115, 88), (110, 94, 68)),
             "ochre": ((137, 101, 66), (114, 81, 53)), "stone": ((115, 105, 96), (96, 86, 78))}
SRC = ((135, 106, 66), (116, 85, 53))


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c if len(c) == 4 else (*c, 255)

    def rect(self, x0, y0, x1, y1, c):
        """inclusive corners"""
        if x1 < x0 or y1 < y0:
            return
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(self.w - 1, x1), min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        self.a[y0:y1 + 1, x0:x1 + 1] = c if len(c) == 4 else (*c, 255)

    def hline(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vline(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def paste(self, im, x, y):
        """an RGBA array or Canvas, alpha over"""
        src = im.a if isinstance(im, Canvas) else im
        h, w = src.shape[:2]
        for yy in range(h):
            ty = y + yy
            if 0 <= ty < self.h:
                for xx in range(w):
                    tx = x + xx
                    if 0 <= tx < self.w and src[yy, xx, 3] > 0:
                        self.a[ty, tx] = src[yy, xx]

    def outline(self):
        """an unbroken 1 px ink outline around the silhouette, inside the canvas (the canvas has a 1 px margin)"""
        solid = self.a[..., 3] > 0
        pad = np.pad(solid, 1)
        nb = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
        edge = nb & ~solid
        self.a[edge] = INK

    def image(self):
        return Image.fromarray(self.a, "RGBA")


def load_front(k, style, plaster):
    """a styled front, plaster swapped (arthooks.lua plasterImg), as an RGBA array"""
    path = os.path.join(SCENE, f"town_front_tall{k}_{style}.png")
    a = np.array(Image.open(path).convert("RGBA"))
    to = D_PLASTER[plaster]
    for j in range(2):
        m = (a[..., 0] == SRC[j][0]) & (a[..., 1] == SRC[j][1]) & (a[..., 2] == SRC[j][2])
        a[m, :3] = to[j]
    return a


def ground_floor(k, style, plaster, w, top_row=GF_TOP):
    """the front's ground floor cropped symmetrically to w columns (or widened by its edge column), rows top_row..431"""
    a = load_front(k, style, plaster)[top_row:432]
    fw = a.shape[1]
    if w <= fw:
        l = (fw - w) // 2
        return a[:, l:l + w].copy()
    l = (w - fw) // 2
    out = np.zeros((a.shape[0], w, 4), np.uint8)
    out[:, :l] = a[:, :1]
    out[:, l:l + fw] = a
    out[:, l + fw:] = a[:, -1:]
    return out


def upper_floor(k, style, plaster, w):
    """rows 140-283 of a styled front (the first floor: its windows, cornice)"""
    a = load_front(k, style, plaster)[140:GF_TOP]
    fw = a.shape[1]
    if w <= fw:
        l = (fw - w) // 2
        return a[:, l:l + w].copy()
    l = (w - fw) // 2
    out = np.zeros((a.shape[0], w, 4), np.uint8)
    out[:, :l] = a[:, :1]
    out[:, l:l + fw] = a
    out[:, l + fw:] = a[:, -1:]
    return out


# ---- roof parts (drawn once, stamped) -------------------------------------------------------------------------------
def tile_courses(c, x0, x1, y0, y1, pal, phase=0, joints=True):
    """clay tile courses, 4 rows each: a lit row, a mid row, a shade row, a joint row; the tiles' vertical joints every
    6 px, staggered course to course (joints=False: plain courses, the decorative roofs at the back: half detail)"""
    for y in range(y0, y1 + 1):
        r = (y - y0) % 4
        c.hline(x0, x1, y, pal[r])
    if not joints:
        return
    for y in range(y0, y1 + 1, 4):
        off = 3 if ((y - y0) // 4 + phase) % 2 else 0
        for x in range(x0 + off, x1 + 1, 6):
            c.vline(x, y, min(y1, y + 2), pal[3])


def lead_sheet(c, x0, x1, y0, y1, pal):
    """a flat lead roof seen edge-on: a lit top row, the sheet, a seam every 16 px"""
    c.rect(x0, y0, x1, y1, pal[1])
    c.hline(x0, x1, y0, pal[0])
    if y1 > y0:
        c.hline(x0, x1, y1, pal[2])
    for x in range(x0 + 8, x1, 16):
        c.vline(x, y0, y1, pal[2])


def coping(c, x0, x1, y, pal, h=3):
    """a stone coping / cornice band h rows tall: lit top, mid, shade"""
    c.rect(x0, x1, y, y + h - 1, pal[1]) if False else None
    c.rect(x0, y, x1, y + h - 1, pal[1])
    c.hline(x0, x1, y, pal[0])
    c.hline(x0, x1, y + h - 1, pal[2])


def parapet(c, x0, x1, y0, y1, pal, mortar):
    """a low stone parapet behind the walk: ashlar in running bond, a lit coping row"""
    c.rect(x0, x1, y0, y1, pal[1]) if False else None
    c.rect(x0, y0, x1, y1, pal[1])
    c.hline(x0, x1, y0, pal[0])
    for y in range(y0 + 3, y1, 4):
        c.hline(x0, x1, y, pal[2])
        for x in range(x0 + (4 if ((y - y0) // 4) % 2 else 10), x1, 12):
            c.vline(x, y - 3, y - 1, pal[2])


def chimney(c, x0, x1, y0, y1, brick, mortar, cap):
    """a brick chimney with a stone cap (2 rows, 1 px wider each side) and two clay pots on it is drawn by the caller"""
    c.rect(x0, y0 + 2, x1, y1, brick[1])
    if brick is BRICK:                                                 # (the decorative chimney: a plain stack)
        for y in range(y0 + 2, y1 + 1, 3):
            c.hline(x0, x1, y, mortar)
            for x in range(x0 + (2 if ((y - y0) // 3) % 2 else 5), x1, 6):
                c.put(x, y + 1, mortar); c.put(x, y + 2, mortar)
    c.vline(x0, y0 + 2, y1, brick[0])
    c.vline(x1, y0 + 2, y1, brick[2])
    c.rect(x0 - 1, y0, x1 + 1, y0 + 1, cap[1]); c.hline(x0 - 1, x1 + 1, y0, cap[0])


def window_box(c, x, y, w, pal_wood, blooms, phase):
    """a terracotta / wood box w wide with leaves and blooms over it (the box's top row at y)"""
    c.rect(x, y, x + w - 1, y + 3, pal_wood[1]); c.hline(x, x + w - 1, y, pal_wood[0]); c.hline(x, x + w - 1, y + 3, pal_wood[2])
    for i, bx in enumerate(range(x + 1, x + w - 1, 3)):
        c.put(bx, y - 1, LEAF[0] if (i + phase) % 2 else LEAF[1]); c.put(bx + 1, y - 1, LEAF[1])
        c.put(bx + ((i + phase) % 2), y - 2, blooms[(i + phase) % len(blooms)])


def dormer(c, x, y, w, h, tile, lead, glass):
    """a little gabled dormer on a roof: its face with a window, a tile cap; x, y its top-left; h its face height"""
    c.rect(x + 1, y + 3, x + w - 2, y + h - 1, D_PLASTER["cream"][0])
    c.rect(x + 3, y + 5, x + w - 4, y + h - 3, glass[1]); c.vline(x + (w // 2), y + 5, y + h - 3, glass[0])
    c.rect(x, y, x + w - 1, y + 2, tile[1]); c.hline(x, x + w - 1, y, tile[0])
    c.hline(x - 1, x + w, y + 2, tile[2])


def pediment_roof(c, x0, x1, eave_y, ridge_y, rx, tile):
    """a pitched tile roof seen from the front: the two slopes between the eave line and the ridge, as tile courses
    clipped to the triangle (x0..x1 at eave_y, the ridge at rx, ridge_y), a ridge cap"""
    tmp = Canvas(c.w, c.h)
    tile_courses(tmp, x0, x1, ridge_y, eave_y, tile, joints=tile is TILE)
    for y in range(ridge_y, eave_y + 1):
        k = (y - ridge_y) / max(1, (eave_y - ridge_y))
        lx = int(round(rx - (rx - x0) * k)); rxx = int(round(rx + (x1 - rx) * k))
        tmp.a[y, :max(0, lx)] = 0; tmp.a[y, min(c.w, rxx + 1):] = 0
    c.paste(tmp, 0, 0)
    c.hline(rx - 1, rx + 1, ridge_y, tile[0]); c.put(rx, ridge_y - 1, tile[0])
    for y in range(ridge_y, eave_y + 1):                       # the ridge-to-eave hips: a dark line
        k = (y - ridge_y) / max(1, (eave_y - ridge_y))
        c.put(int(round(rx - (rx - x0) * k)), y, tile[3]); c.put(int(round(rx + (x1 - rx) * k)), y, tile[3])


def stepped_gable(c, x0, x1, eave_y, ridge_y, tile, gran, step_w=8, step_h=4, deco=False):
    """a stepped gable (the old town's crow steps) over a tile roof: the silhouette steps in step_w px for every
    step_h rows from both ends up to a flat top; a 3 row granite cap on every step, a dark riser on its side"""
    n = max(1, min((eave_y - ridge_y) // step_h, (x1 - x0 + 1) // (2 * step_w)))
    for y in range(ridge_y, eave_y + 1):
        i = min(n, (eave_y - y + step_h - 1) // step_h)
        if (eave_y - y) > n * step_h:
            continue
        lx, rx = x0 + i * step_w, x1 - i * step_w
        if lx > rx:
            continue
        c.hline(lx, rx, y, tile[1] if y % 4 else tile[0])
    for i in range(1, n + 1):
        ty = eave_y - i * step_h
        lx0, lx1 = x0 + i * step_w, (x0 + (i + 1) * step_w - 1 if i < n else x1 - n * step_w)
        rx0, rx1 = (x1 - (i + 1) * step_w + 1 if i < n else lx0), x1 - i * step_w
        for a, b in ((lx0, lx1), (rx0, rx1)):
            c.rect(a, ty, b, ty + 2, gran[1]); c.hline(a, b, ty, gran[0]); c.hline(a, b, ty + 2, gran[2])
        c.vline(lx0, ty, ty + step_h - 1, gran[2]); c.vline(rx1, ty, ty + step_h - 1, gran[2])
    return x0 + n * step_w, x1 - n * step_w


# ---- the buildings ---------------------------------------------------------------------------------------------------
FILES = {}
LUA = []


def save(name, c):
    FILES[name] = c.image()


def building_front(name, w, gf, eave_y, extra_rows=None, cornice=True, pal=D_GRAN):
    """a front: its ground floor (an RGBA block whose bottom is the back line 414) under a cornice at eave_y, any wall
    rows between filled with the block's top row; returns (array, top_y)"""
    gh = gf.shape[0]
    wall_top = BACK - gh
    top = eave_y
    h = BACK - top
    c = Canvas(w, h)
    c.paste(gf, 0, wall_top - top)
    if wall_top > top:                                                 # fill up to the cornice with the plain wall row
        for y in range(top, wall_top):
            c.a[y - top] = gf[0]
    if cornice:
        coping(c, 0, w - 1, 0, pal, 4)
    return c


def flat_roof_play(name, bx0, bx1, by0, by1, parapet_h=10, pal=LEAD, deco_boxes=False, cornice_h=5):
    """a lead flat roof that is a play piece: the walk's top at by0 (ink at by0 - 1), a parapet behind rising
    parapet_h over it, a cornice under the sheet; the image is the box + 1 px each side; returns (canvas, x, y)"""
    w = bx1 - bx0 + 2
    top = by0 - 1 - parapet_h
    h = (by1 + cornice_h + 1) - top
    c = Canvas(w, h)
    oy = -top
    parapet(c, 1, w - 2, by0 - parapet_h + oy, by0 - 1 + oy, GRAN, MORTAR)
    lead_sheet(c, 1, w - 2, by0 + oy, by1 - 1 + oy, pal)
    coping(c, 1, w - 2, by1 + oy, GRAN, cornice_h)
    if deco_boxes:
        for i, x in enumerate(range(4, w - 14, 16)):
            window_box(c, x, by0 + oy - 3, 12, WOOD, BLOOM, i)
    c.outline()
    c.hline(1, w - 2, by0 - 1 + oy, INK)                                # the ink row over the walk, unbroken
    return c, bx0 - 1, top


def main(check=False):
    tmx = ET.parse(os.path.join(ROOT, "maps", "downtown_tall.tmx")).getroot()
    boxes = []
    for og in tmx.findall("objectgroup"):
        if og.attrib.get("name") != "props":
            continue
        for o in og.findall("object"):
            a = o.attrib
            props = {p.attrib["name"]: p.attrib.get("value") for p in o.findall("properties/property")}
            d = dict(props)
            d.update(name=a.get("name", ""), x0=int(float(a["x"])), y0=int(float(a["y"])), x1=int(float(a["x"]) + float(a.get("width", 0))),
                     y1=int(float(a["y"]) + float(a.get("height", 0))))
            boxes.append(d)

    def lua_building(name, x0, x1, front, fx, fy, roof=None, rx=0, ry=0, trigger=None, claims=(), canopies=()):
        LUA.append(dict(name=name, x0=x0, x1=x1, front=front, fx=fx, fy=fy, roof=roof, rx=rx, ry=ry, trigger=trigger, claims=list(claims), canopies=list(canopies)))

    # ---- the start house: town_door's ground floor and first floor, a tile gable over them (decoration) ----------
    a = np.array(Image.open(os.path.join(SCENE, "town_door.png")).convert("RGBA"))[140:432]   # 140 x 292, bottom at 414
    w = a.shape[1]
    top = BACK - 292 - 60
    c = Canvas(w, BACK - top)
    c.paste(a, 0, 60)
    coping(c, 0, w - 1, 56, D_GRAN, 4)
    pediment_roof(c, 0, w - 1, 56, 4, w // 2, D_TILE)
    chimney(c, w - 30, w - 21, 14, 40, D_BRICK, D_MORTAR, D_GRAN)
    save("dtl_start_front", c)
    lua_building("start", 0, 140, "dtl_start_front", 0, top, claims=[(0, 360)])

    # ---- the closed boxes and the plain fronts after the canal: one-storey houses with decorative roofs -----------
    k = 0
    for b in boxes:
        isfront = b.get("kind") == "decor" and b.get("layer") == "back" and b["x1"] - b["x0"] >= 48 and b["y1"] - b["y0"] >= 100 and b["name"] in ("", None)
        if not isfront or b["x0"] < 1180 and not b.get("closed") or 1180 <= b["x0"] < 2640:
            continue
        if 2480 <= b["x0"] < 2640:
            continue                                                   # the canal gap stays open (the breather)
        k += 1
        bw = b["x1"] - b["x0"]
        fronts = [int(ch) for ch in str(b.get("fronts", "1")) if ch.isdigit()] or [1]
        style, plaster = b.get("style", "a"), b.get("plaster", "yellow")
        n = len(fronts)
        base, extra = bw // n, bw - (bw // n) * n
        gf = np.zeros((432 - GF_TOP, bw, 4), np.uint8)
        x = 0
        for i, fk in enumerate(fronts):
            ww = base + (1 if i < extra else 0)
            gf[:, x:x + ww] = ground_floor(fk, style, plaster, ww)
            x += ww
        two = k % 4 == 2                                               # every fourth house has a first floor
        uf = np.concatenate([upper_floor(fk, style, plaster, base + (1 if i < extra else 0)) for i, fk in enumerate(fronts)], axis=1) if two else None
        eave = BACK - gf.shape[0] - 6 - (uf.shape[0] if two else 0)
        kind = ("gable", "step", "flat", "gable", "step")[k % 5]
        ridge = eave - (38 if kind != "flat" else 12)
        c = Canvas(bw, BACK - ridge + 2)
        oy = ridge - 2
        c.paste(gf, 0, BACK - gf.shape[0] - oy)
        if two:
            c.paste(uf, 0, BACK - gf.shape[0] - uf.shape[0] - oy)
        for y in range(eave, BACK - gf.shape[0] - (uf.shape[0] if two else 0)):
            c.a[y - oy] = gf[0]
        coping(c, 0, bw - 1, eave - oy, D_GRAN, 4)
        c.rect(bw - 2, eave - oy + 4, bw - 1, BACK - oy - 1, D_PLASTER[plaster][1])   # the house's right edge in shade
        if kind == "gable":
            pediment_roof(c, 0, bw - 1, eave - oy - 4, ridge - oy, bw // 2, D_TILE)
        elif kind == "step":
            stepped_gable(c, 0, bw - 1, eave - oy - 4, ridge - oy, D_TILE, D_GRAN, step_w=max(6, bw // 10), step_h=4)
        else:
            lead_sheet(c, 0, bw - 1, ridge - oy + 4, eave - oy - 5, D_LEAD)
            parapet(c, 0, bw - 1, ridge - oy, ridge - oy + 3, D_GRAN, D_MORTAR)
        if k % 3 == 1:
            chimney(c, bw - 16, bw - 9, ridge - oy - 10, eave - oy - 2, D_BRICK, D_MORTAR, D_GRAN)
        save(f"dtl_closed{k}_front", c)
        lua_building(f"closed{k}", b["x0"], b["x1"], f"dtl_closed{k}_front", b["x0"], oy, claims=[(b["x0"], b["y0"])])

    # ---- the bakery 1180-1328: shop bay + door bay (style a, yellow), a first floor, a stepped gable, decoration --
    bw = 148
    gf = np.concatenate([ground_floor(2, "a", "yellow", 74), ground_floor(1, "a", "yellow", 74)], axis=1)
    uf = np.concatenate([upper_floor(2, "a", "yellow", 74), upper_floor(1, "a", "yellow", 74)], axis=1)
    ridge = 136 - 40
    c = Canvas(bw, BACK - ridge + 2)
    oy = ridge - 2
    c.paste(gf, 0, BACK - gf.shape[0] - oy)
    c.paste(uf, 0, BACK - gf.shape[0] - uf.shape[0] - oy)
    eave = BACK - gf.shape[0] - uf.shape[0]
    coping(c, 0, bw - 1, eave - oy, D_GRAN, 4)
    stepped_gable(c, 0, bw - 1, eave - oy - 4, ridge - oy, D_TILE, D_GRAN, step_w=10, step_h=4)
    chimney(c, 20, 27, ridge - oy - 8, eave - oy - 6, D_BRICK, D_MORTAR, D_GRAN)
    save("dtl_bakery_front", c)
    lua_building("bakery", 1180, 1328, "dtl_bakery_front", 1180, oy, claims=[(1180, 300)])

    # ---- the wing 1328-1392: a door bay, its lead flat the walk (BALCONY box 1328-1392 y 272-278) ----------------
    gf = ground_floor(1, "d", "red", 64, top_row=302)
    c = building_front("wing", 64, gf, 284, pal=D_GRAN)
    save("dtl_wing_front", c)
    r, rx, ry = flat_roof_play("wing", 1328, 1392, 272, 278)
    save("dtl_wing_roof", r)
    lua_building("wing", 1328, 1392, "dtl_wing_front", 1328, 284, "dtl_wing_roof", rx, ry, trigger=(1328, 272), claims=[(1328, 272), (1320, 278)])

    # ---- the cafe arcade 1416-1536: three round arches (LOGGIA box 1416-1536 y 280-286) ---------------------------
    bw = 120
    top = 292
    c = Canvas(bw, BACK - top)
    P = D_PLASTER["cream"]
    c.rect(0, 0, bw - 1, BACK - top - 1, P[0])
    for ax in (6, 44, 82):                                            # piers 6 px, arches 32 wide, crown at 304
        pass
    for i in range(3):
        ax = 8 + i * 38                                               # the opening 32 wide: 8..39, 46..77, 84..115
        ox0, ox1 = ax, ax + 31
        # the dark inside, its back wall lit by a cafe window
        c.rect(ox0, 324 - top, ox1, BACK - top - 1, D_DARK)
        for y in range(308 - top, 324 - top):                         # the round head: a half circle
            dy = (324 - top) - y
            half = int(round((16 ** 2 - dy ** 2) ** 0.5)) if dy <= 16 else 0
            c.hline(ax + 16 - half, ax + 15 + half, y, D_DARK)
        c.rect(ox0 + 6, 350 - top, ox1 - 6, 404 - top, D_GLASS[1]); c.rect(ox0 + 7, 352 - top, ox0 + 11, 400 - top, D_GLASS[0])
        c.rect(ox0 + 14, 352 - top, ox0 + 14, 404 - top, (90, 70, 50)); c.rect(ox0 + 6, 378 - top, ox1 - 6, 379 - top, (90, 70, 50))
        # the granite voussoirs: a 3 px ring round the head and the piers' quoins
        for y in range(304 - top, 324 - top):
            dy = (324 - top) - y
            ho = int(round((19 ** 2 - dy ** 2) ** 0.5)) if dy <= 19 else 0
            hi = int(round((16 ** 2 - dy ** 2) ** 0.5)) if dy <= 16 else 0
            c.hline(ax + 16 - ho, ax + 16 - hi - 1, y, D_GRAN[1]); c.hline(ax + 16 + hi, ax + 15 + ho, y, D_GRAN[1])
        c.rect(ox0 - 3, 324 - top, ox0 - 1, BACK - top - 1, D_GRAN[1]); c.rect(ox1 + 1, 324 - top, ox1 + 3, BACK - top - 1, D_GRAN[1])
        c.vline(ox0 - 3, 324 - top, BACK - top - 1, D_GRAN[0]); c.vline(ox1 + 3, 324 - top, BACK - top - 1, D_GRAN[2])
        for y in range(336 - top, BACK - top, 12):
            c.hline(ox0 - 3, ox0 - 1, y, D_GRAN[2]); c.hline(ox1 + 1, ox1 + 3, y, D_GRAN[2])
    c.rect(0, BACK - top - 4, bw - 1, BACK - top - 1, D_GRAN[2])          # the plinth
    coping(c, 0, bw - 1, 0, D_GRAN, 4)
    save("dtl_arcade_front", c)
    r, rx, ry = flat_roof_play("arcade", 1416, 1536, 280, 286, parapet_h=12)
    save("dtl_arcade_roof", r)
    lua_building("arcade", 1416, 1536, "dtl_arcade_front", 1416, top, "dtl_arcade_roof", rx, ry, trigger=(1416, 280), claims=[(1416, 280), (1404, 286)])

    # ---- the guild hall 1552-1680: granite ashlar, a pedimented door at 1562-1606, the porch (BALCONY 1552-1608 y 312),
    # the stepped gable (GUILD ROOF 1560-1568 y 272 and its steps up to the ridge 1616-1656 y 244, down to 1680 y 256),
    # the chimney (1628-1644, 200-244) on the ridge ------------------------------------------------------------------
    bw = 128
    top = 288
    c = Canvas(bw, BACK - top)
    c.rect(0, 0, bw - 1, BACK - top - 1, D_GRAN[1])
    for y in range(0, BACK - top, 10):                                 # ashlar courses in running bond
        c.hline(0, bw - 1, y, D_GRAN[2])
        for x in range((8 if (y // 10) % 2 else 20), bw, 24):
            c.vline(x, y + 1, y + 9, D_GRAN[2])
        c.hline(0, bw - 1, y + 1, D_GRAN[0])
    g6 = load_front(6, "c", "ochre")[326:432]                          # the granite front's door with its surround (rows 326-431)
    door = g6[:, 48:100]                                               # 52 columns round the door's centre (col 74)
    c.paste(door, 10 + 0, 326 - top)
    coping(c, 0, bw - 1, 0, D_GRAN, 4)
    c.rect(0, BACK - top - 4, bw - 1, BACK - top - 1, D_GRAN[2])
    save("dtl_guild_front", c)
    # the porch: a granite slab on two square piers over the door, its top the walk at 312
    pw = 56 + 2
    c = Canvas(pw, 326 - 311 + 2)
    c.rect(1, 1, pw - 2, 5, GRAN[1]); c.hline(1, pw - 2, 1, GRAN[0]); c.hline(1, pw - 2, 5, GRAN[2])
    c.rect(2, 6, 5, 326 - 311, GRAN[2]); c.rect(pw - 6, 6, pw - 3, 326 - 311, GRAN[2])   # the brackets
    c.outline(); c.hline(1, pw - 2, 0, INK)
    save("dtl_guild_canopy1", c)
    # the gable: the steps' tops are the boxes (8 px steps of 4 px up from 272 at 1560 to 244 at 1616, flat to 1656,
    # down to 256 at 1680); the roof image spans the hall 1552-1680 from the chimney top to the cornice
    rtop = 199
    c = Canvas(bw + 2, 290 - rtop)
    oy = -rtop
    ox = -1552 + 1
    # the tile roof under the parapet: filled down to the cornice row 288 (the front's coping starts there)
    steps = [(1560, 1568, 272), (1568, 1576, 268), (1576, 1584, 264), (1584, 1592, 260), (1592, 1600, 256), (1600, 1608, 252),
             (1608, 1616, 248), (1616, 1656, 244), (1656, 1664, 248), (1664, 1672, 252), (1672, 1680, 256)]
    tile_courses(c, 1, bw, 244 + oy, 289 + oy, TILE, phase=1)
    for y in range(244, 290):                                          # clip to the stepped line
        lx = 1552
        for sx0, sx1, sy in steps:
            if sy <= y:
                lx = sx0; break
        rxx = 1680
        for sx0, sx1, sy in reversed(steps):
            if sy <= y:
                rxx = sx1; break
        if y < 272:
            c.a[y + oy, :max(0, lx + ox)] = 0
            c.a[y + oy, min(c.w, rxx + ox):] = 0
    for i, (sx0, sx1, sy) in enumerate(steps):                          # the granite steps: 6 rows, lit top, dark foot
        c.rect(sx0 + ox, sy + oy, sx1 - 1 + ox, sy + 5 + oy, GRAN[1]); c.hline(sx0 + ox, sx1 - 1 + ox, sy + oy, GRAN[0]); c.hline(sx0 + ox, sx1 - 1 + ox, sy + 5 + oy, GRAN[2])
        if i < len(steps) - 1 and steps[i + 1][2] < sy:                 # the riser of the next step up (left slope)
            c.vline(sx1 - 1 + ox, steps[i + 1][2] + oy, sy - 1 + oy, GRAN[2])
        if i > 0 and steps[i - 1][2] < sy:                              # the riser on the right slope
            c.vline(sx0 + ox, steps[i - 1][2] + oy, sy - 1 + oy, GRAN[2])
    # the eave rows 272-289 outside the first step (1552-1560) and after the last (1680): the tile roof's edge
    c.a[272 + oy:290 + oy, 0:1552 + ox] = 0
    for y in range(272, 290):
        c.hline(1552 + ox, 1559 + ox, y, TILE[1] if y % 4 else TILE[3])
    chimney(c, 1628 + ox, 1643 + ox, 200 + oy, 243 + oy, BRICK, MORTAR, GRAN)
    c.rect(1631 + ox, 196 + oy, 1633 + ox, 199 + oy, BRICK[2]); c.rect(1638 + ox, 196 + oy, 1640 + ox, 199 + oy, BRICK[2])   # two pots
    c.outline()
    for sx0, sx1, sy in steps:
        c.hline(sx0 + ox, sx1 - 1 + ox, sy - 1 + oy, INK)
    c.hline(1627 + ox, 1644 + ox, 199 + oy, INK)
    save("dtl_guild_roof", c)
    lua_building("guild", 1552, 1680, "dtl_guild_front", 1552, top, "dtl_guild_roof", 1552 - 1, rtop - 4, trigger=(1560, 272),
                 claims=[(1560, 272), (1568, 268), (1576, 264), (1584, 260), (1592, 256), (1600, 252), (1608, 248), (1616, 244), (1656, 248), (1664, 252), (1672, 256),
                         (1628, 200), (1552, 282), (1536, 296)],
                 canopies=[(1552, 312, "dtl_guild_canopy1", 1551, 311)])

    # ---- the market pavilions 1680-1768 (GALLERY y 256) and 1816-1888 (GALLERY y 256): shop bays, lead flats ----------
    for name, x0, x1, style, plaster, cx0, cx1, cy in (("pav1", 1680, 1768, "e", "yellow", 1656, 1712, 336), ("pav2", 1816, 1888, "b", "cream", 1840, 1896, 344)):
        bw = x1 - x0
        gf = ground_floor(2, style, plaster, bw, top_row=302)
        c = building_front(name, bw, gf, 266)
        save(f"dtl_{name}_front", c)
        r, rx, ry = flat_roof_play(name, x0, x1, 256, 262, parapet_h=10)
        save(f"dtl_{name}_roof", r)
        # the canopy: a wooden lean-to on iron brackets, its top the box's top; the box is cx0..cx1 at cy
        cw = cx1 - cx0 + 2
        c = Canvas(cw, 14)
        c.rect(1, 1, cw - 2, 4, WOOD[1]); c.hline(1, cw - 2, 1, WOOD[0]); c.hline(1, cw - 2, 4, WOOD[2])   # the fascia board
        for x in (3, cw // 2 - 4, cw - 11):                             # three iron brackets: right-angle triangles
            for k in range(8):                                          # against the wall, the slab on their top
                c.hline(x + k, x + 7, 5 + k, IRON[1] if k else IRON[0])
        c.outline(); c.hline(1, cw - 2, 0, INK)
        save(f"dtl_{name}_canopy1", c)
        claims = [(x0, 256), (cx0, cy)]
        lua_building(name, x0, x1, f"dtl_{name}_front", x0, 266, f"dtl_{name}_roof", rx, ry, trigger=(x0, 256), claims=claims,
                     canopies=[(cx0, cy, f"dtl_{name}_canopy1", cx0 - 1, cy - 1)])

    # ---- the tram shed 1912-2000 (DORMER box widened to 1912-2000 y 264): the gateway in a plastered shed wall, a lead
    # flat with a little dormer on it ----------------------------------------------------------------------------------
    bw = 88
    top = 270
    c = Canvas(bw, BACK - top)
    P = D_PLASTER["yellow"]
    c.rect(0, 0, bw - 1, BACK - top - 1, P[0])
    gw = np.array(Image.open(os.path.join(SCENE, "town_gateway.png")).convert("RGBA"))
    c.paste(gw, 4, BACK - top - gw.shape[0])
    c.rect(0, BACK - top - 4, bw - 1, BACK - top - 1, D_GRAN[2])
    coping(c, 0, bw - 1, 0, D_GRAN, 4)
    save("dtl_shed_front", c)
    r, rx, ry = flat_roof_play("shed", 1912, 2000, 264, 270, parapet_h=8)
    d = Canvas(26, 20)                                                 # a dormer standing behind the parapet: 24 wide
    dormer(d, 1, 1, 24, 16, TILE, LEAD, GLASS)
    d.outline()
    big = Canvas(r.w, r.h + 12)
    big.paste(d, 32, 0); big.paste(r, 0, 12)
    r, ry = big, ry - 12
    r.hline(1, r.w - 2, 264 - ry - 1, INK)
    save("dtl_shed_roof", r)
    lua_building("shed", 1912, 2000, "dtl_shed_front", 1912, top, "dtl_shed_roof", rx, ry, trigger=(1912, 264), claims=[(1912, 264), (1912, 270)])

    # ---- the kiosk house 2016-2072 (ledge y 248) and the shelter house 2112-2168 (ledge y 264): narrow door bays -----
    for name, x0, x1, y, style, plaster in (("kioskhouse", 2016, 2072, 248, "b", "cream"), ("shelterhouse", 2112, 2168, 264, "d", "red")):
        bw = x1 - x0
        gf = ground_floor(1, style, plaster, bw, top_row=314)        # (below the hanging sign: a plain wall over the door)
        c = building_front(name, bw, gf, y + 10)
        save(f"dtl_{name}_front", c)
        r, rx, ry = flat_roof_play(name, x0, x1, y, y + 6, parapet_h=8)
        save(f"dtl_{name}_roof", r)
        lua_building(name, x0, x1, f"dtl_{name}_front", x0, y + 10, f"dtl_{name}_roof", rx, ry, trigger=(x0, y), claims=[(x0, y), (x0 - 16, y + 8), (2000, 256), (2088, 272)])

    # ---- the glass flower hall 2216-2376 (FLOWER ROOF widened to 2216-2376 y 232; the springy AWNING 2208-2264 y 272 on
    # its front): an iron-and-glass hall, flower boxes on its roof garden -----------------------------------------------
    bw = 160
    top = 238
    c = Canvas(bw, BACK - top)
    c.rect(0, 0, bw - 1, BACK - top - 1, D_GLASS[1])
    for x in range(0, bw, 20):                                          # iron mullions every 20 px
        c.rect(x, 0, x + 1, BACK - top - 1, D_IRON[0]); c.vline(x + 1, 0, BACK - top - 1, D_IRON[1])
    for y in (0, 40, 80, 120, 150):                                     # transoms
        c.rect(0, y, bw - 1, y + 1, D_IRON[0])
    for x in range(2, bw, 20):                                          # a lit pane column (the reflection)
        c.rect(x + 2, 2, x + 5, BACK - top - 1, D_GLASS[0])
    c.rect(0, 150, bw - 1, 153, D_IRON[0])
    for px in (0, bw - 4):                                              # granite pilasters at both ends (no dark edge)
        c.rect(px, 0, px + 3, BACK - top - 1, D_GRAN[1]); c.vline(px, 0, BACK - top - 1, D_GRAN[0]); c.vline(px + 3, 0, BACK - top - 1, D_GRAN[2])
    c.rect(0, BACK - top - 24, bw - 1, BACK - top - 1, D_GRAN[1])      # a granite plinth wall with the door
    c.hline(0, bw - 1, BACK - top - 24, D_GRAN[0])
    c.rect(bw // 2 - 22, BACK - top - 97, bw // 2 + 21, BACK - top - 1, (90, 70, 50))   # the door: oak, 2.1 m
    c.rect(bw // 2 - 20, BACK - top - 95, bw // 2 - 2, BACK - top - 3, (120, 90, 60)); c.rect(bw // 2 + 1, BACK - top - 95, bw // 2 + 19, BACK - top - 3, (120, 90, 60))
    for y in range(BACK - top - 90, BACK - top - 8, 24):
        c.rect(bw // 2 - 18, y, bw // 2 - 4, y + 12, D_GLASS[1]); c.rect(bw // 2 + 3, y, bw // 2 + 17, y + 12, D_GLASS[1])
    c.rect(bw // 2 - 22, BACK - top - 97, bw // 2 + 21, BACK - top - 96, D_IRON[1])
    coping(c, 0, bw - 1, 0, D_GRAN, 4)
    save("dtl_hall_front", c)
    r, rx, ry = flat_roof_play("hall", 2216, 2376, 232, 238, parapet_h=6, deco_boxes=True)
    save("dtl_hall_roof", r)
    lua_building("hall", 2216, 2376, "dtl_hall_front", 2216, top, "dtl_hall_roof", rx, ry, trigger=(2216, 232), claims=[(2216, 232), (2180, 240), (2296, 238)])

    # ---- the canal house 2416-2464 (ledge y 248): a narrow door bay, a lead flat ------------------------------------
    gf = ground_floor(1, "e", "yellow", 48, top_row=314)
    c = building_front("canalhouse", 48, gf, 258)
    save("dtl_canalhouse_front", c)
    r, rx, ry = flat_roof_play("canalhouse", 2416, 2464, 248, 254, parapet_h=8)
    save("dtl_canalhouse_roof", r)
    lua_building("canalhouse", 2416, 2464, "dtl_canalhouse_front", 2416, 258, "dtl_canalhouse_roof", rx, ry, trigger=(2416, 248), claims=[(2416, 248), (2384, 256), (2404, 296)])

    # ---- the plaza's old HOUSE boxes are claimed (nothing drawn: the low row stands there) -----------------------------
    LUA.append(dict(name="houses", x0=0, x1=0, front=None, fx=0, fy=0, roof=None, rx=0, ry=0, trigger=None,
                    claims=[(1536, 296), (1644, 288), (1832, 296), (2404, 296), (1700, 288), (1912, 270), (2000, 256), (2088, 272), (2180, 240), (2296, 238), (2384, 256)], canopies=[]))

    # ---- write ---------------------------------------------------------------------------------------------------------
    lines = ["-- generated by tools/build_dt_rooftops.py (day/07nov-dt): the tall Downtown's low row, option A. Do not edit.",
             "-- buildings = { { name, x0, x1, front = file, fx, fy (the front's top-left, decoration), roof = file, rx, ry",
             "--   (the roof's top-left, a play piece drawn when the trigger box is drawn), trigger = { x0, y0 },",
             "--   claims = { { x0, y0 }, ... } (map boxes this building draws or hides), canopies = { { x0, y0, file, ix, iy } } } }",
             "return {"]
    for b in LUA:
        def q(v):
            return ("\"%s\"" % v) if isinstance(v, str) else ("nil" if v is None else str(v))
        cl = ", ".join("{ %d, %d }" % c for c in b["claims"])
        ca = ", ".join('{ %d, %d, "%s", %d, %d }' % c for c in b["canopies"])
        tr = ("{ %d, %d }" % tuple(b["trigger"])) if b["trigger"] else "nil"
        lines.append('  { name = "%s", x0 = %d, x1 = %d, front = %s, fx = %d, fy = %d, roof = %s, rx = %d, ry = %d, trigger = %s, claims = { %s }, canopies = { %s } },'
                     % (b["name"], b["x0"], b["x1"], q(b["front"]), b["fx"], b["fy"], q(b["roof"]), b["rx"], b["ry"], tr, cl, ca))
    lines.append("}")
    lua_text = "\n".join(lines) + "\n"
    lua_path = os.path.join(ROOT, "riverwalk", "dt_lowrow.lua")
    bad = 0
    for name, im in FILES.items():
        path = os.path.join(SCENE, name + ".png")
        if check:
            if not os.path.exists(path) or np.any(np.array(Image.open(path).convert("RGBA")) != np.array(im)):
                print("DIFFERS", path); bad += 1
        else:
            im.save(path)
    if check:
        if not os.path.exists(lua_path) or open(lua_path).read() != lua_text:
            print("DIFFERS", lua_path); bad += 1
        print("build_dt_rooftops --check:", "FAIL" if bad else "PASS", len(FILES), "files")
        sys.exit(1 if bad else 0)
    open(lua_path, "w").write(lua_text)
    print("wrote", len(FILES), "files and", lua_path)
    for name, im in FILES.items():
        print(" ", name, im.size)


if __name__ == "__main__":
    main(check="--check" in sys.argv)
