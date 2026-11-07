#!/usr/bin/env python3
"""tools/build_dt_rooftops.py: the tall Downtown's low row, option A (day/07nov-dt; design docs/review/07nov/dt/design/,
targets art/gen/concepts/dt_design_A1_a.png .. A4_a.png, never cut). Round 2 after the independent review
(art/gen/reviews/dt_sweep_07nov.md, dt_lowrow_07nov.md): roofs as roofs, the mid row rebuilt lighter at half size,
cloth canopies, the fountain to the A2 concept, openings at true scale, the decorative roof kit without slits.

The street is lined with LOW true-scale buildings (46 px/m) whose roofs are the high road: a two-storey bakery, its
flat-roofed wing (WING ROOF), the two-arch cafe arcade (ARCADE ROOF), the guild hall with its crow-step tile gable
(GUILD ROOF and its steps, the CHIMNEY on the ridge) and its porch (PORCH), two market pavilions with lead roofs
(PAVILION ROOF) and cloth shop canopies (CANOPY), the tram shed (SHED ROOF; the cargo bike's gateway), the kiosk
house and the shelter house (KIOSK ROOF, SHELTER ROOF), the glass flower hall with its railed roof garden (FLOWER
ROOF), the canal house (CANAL ROOF); the fountain (RIM, FOUNTAIN, TIER) built to the A2 concept. Behind them the
mid row (town_facades.png, scroll 0.5, moving with the world: L.vmid 1.0) and the sky. Screens 1-3 and 9-11 get
one-storey houses with tile hips on the `closed` boxes (and the plain fronts after the canal); the start house is
two storeys with a roof (town_door's ground floor unchanged).

Everything is BUILT: the ground floors are whole-pixel crops of the approved styled fronts (town_front_tall<k>_<s>,
rows 284-431, plaster swapped as arthooks.lua does), the roofs are stamped parts (a 4 px scallop tile course, a
lead seam, a coping, a parapet, a dentil cornice, a chimney, a dormer, a railing, a planter) on the integer grid.
Roofs Pepper walks on are play pieces: an unbroken 1 px ink outline, drawn unfaded, the art's top row at the box's
top - 1, the image the box + 1 px a side. Fronts are decoration: no outline, faded 28 % by the game (source values).

Files (riverwalk/art/scene/): dtl_<name>_front.png, dtl_<name>_roof.png, dtl_<name>_canopy<k>.png, dtl_closed<k>_front.png,
dtl_fountain_*.png, town_facades.png (the mid row); the placement table riverwalk/dt_lowrow.lua (arthooks.lua).

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
# play pieces (not faded): on-screen values. One ramp across every roof strip (review fix 3): granite body median
# 150-165, the coping about 200, a lead seam in two greys, the tile eave in two oxblood shades (contrast under 60)
GRAN = [(206, 200, 188), (166, 160, 148), (130, 124, 114), (96, 90, 84)]      # coping, body, shade, dark
LEAD = [(150, 154, 160), (118, 122, 130)]
TILE = [(176, 82, 62), (138, 58, 48)]                                            # oxblood lit, oxblood shade
BRICK = [(166, 86, 62), (132, 64, 48), (98, 46, 36)]
MORTAR = (196, 176, 150)
GLASS = [(150, 184, 206), (112, 146, 172)]
IRON = [(70, 96, 84), (46, 66, 58)]
LEAF = [(92, 142, 70), (58, 100, 50)]
BLOOM = [(212, 64, 70), (244, 220, 90)]
SOIL = (82, 58, 42)
# the approved street awning's cloth (town_awning64.png): the canopies share it (review fix 6)
CANVAS = [(233, 221, 199), (202, 70, 60), (157, 46, 52), (188, 172, 158)]
# decoration (faded 28 % towards efe6da by the game): source values from the styled fronts' own ramps where they
# exist, so a front with its roof stays near the back layer's 20 colours. The tile hips take two oxblood shades (the
# red plaster pair of the fronts): the mid row's roofs are 25 luma lighter than these on screen
D_TILE = [(154, 82, 63), (104, 66, 44)]                                          # lit (the red plaster), shade (the oak K): 28 luma apart
D_GRAN = [(135, 130, 120), (110, 103, 95), (77, 72, 68)]                        # the fronts' granite L, T, V
D_CHIM = [(104, 66, 44), (68, 44, 32)]                                           # the chimney one shade darker than the roof (the oak K, D)
D_GLASS = [(100, 128, 150), (72, 98, 120)]
D_IRON = [(44, 64, 56), (28, 42, 36)]
D_DARK = (40, 34, 36)                                    # an alley's / arcade's inside
D_OAK = [(136, 92, 60), (104, 66, 44), (68, 44, 32)]
D_FRAME = (140, 137, 131)
D_PLASTER = {"yellow": ((135, 106, 66), (116, 85, 53)), "red": ((154, 82, 63), (127, 64, 51)), "cream": ((129, 115, 88), (110, 94, 68)),
             "ochre": ((137, 101, 66), (114, 81, 53)), "stone": ((115, 105, 96), (96, 86, 78))}
SRC = ((135, 106, 66), (116, 85, 53))
# the mid row (scroll 0.5, faded 25 % towards b2c3d9 and the look's mid band): source values set for on-screen
# plaster medians of 185-210 (the low row sits at 150-160), glass about 140, frames in the plaster's light shade,
# roofs a pink-grey about 25 luma above the low row's hips
M_PLASTER = [((232, 224, 206), (214, 204, 184)), ((226, 202, 160), (206, 180, 136)), ((228, 196, 182), (206, 170, 156))]
M_GLASS = (134, 148, 166)
M_ROOF = [(206, 150, 132), (170, 116, 100)]
M_STONE = (198, 192, 180)
M_STONE2 = (178, 172, 162)
M_LEAD = [M_STONE, M_STONE2]
M_DOOR = (150, 110, 80)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c if len(c) == 4 else (*c, 255)

    def rect(self, x0, y0, x1, y1, c):
        """inclusive corners"""
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
        y0, x0 = max(0, -y), max(0, -x)
        y1, x1 = min(h, self.h - y), min(w, self.w - x)
        if y1 <= y0 or x1 <= x0:
            return
        s = src[y0:y1, x0:x1]
        d = self.a[y + y0:y + y1, x + x0:x + x1]
        m = s[..., 3] > 0
        d[m] = s[m]

    def outline(self):
        """an unbroken 1 px ink outline around the silhouette, inside the canvas (the canvas has a 1 px margin)"""
        solid = self.a[..., 3] > 0
        pad = np.pad(solid, 1)
        nb = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
        self.a[nb & ~solid] = INK

    def image(self):
        return Image.fromarray(self.a, "RGBA")


def load_front(k, style, plaster):
    """a styled front, plaster swapped (arthooks.lua plasterImg), as an RGBA array"""
    a = np.array(Image.open(os.path.join(SCENE, f"town_front_tall{k}_{style}.png")).convert("RGBA"))
    to = D_PLASTER[plaster]
    for j in range(2):
        m = (a[..., 0] == SRC[j][0]) & (a[..., 1] == SRC[j][1]) & (a[..., 2] == SRC[j][2])
        a[m, :3] = to[j]
    return a


def fit(a, w):
    """rows of a front cropped symmetrically to w columns, or widened by its edge columns"""
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


def ground_floor(k, style, plaster, w, top_row=GF_TOP):
    return fit(load_front(k, style, plaster)[top_row:432], w)


def upper_floor(k, style, plaster, w):
    return fit(load_front(k, style, plaster)[140:GF_TOP], w)


# ---- parts, drawn once and stamped ------------------------------------------------------------------------------------
def scallop_courses(c, x0, x1, y0, y1, pal, phase=0):
    """clay tile in 4 px courses: a lit row, two body rows, a row of tile ends (the scallop: the shade colour at every
    tile's two bottom corners, tiles 4 px wide, staggered course to course). Contrast: the two shades only."""
    lit, sh = pal
    for y in range(y0, y1 + 1):
        r = (y - y0) % 4
        c.hline(x0, x1, y, lit if r == 0 else (sh if r == 3 else lit))
        if r == 1 or r == 2:
            c.hline(x0, x1, y, lit)
        if r == 3:
            off = 2 if (((y - y0) // 4 + phase) % 2) else 0
            c.hline(x0, x1, y, sh)
            for x in range(x0 + off + 1, x1 + 1, 4):
                c.put(x, y, lit); c.put(x + 1, y, lit)
        if r == 2:
            off = 2 if (((y - y0) // 4 + phase) % 2) else 0
            for x in range(x0 + off, x1 + 1, 4):
                c.put(x, y, sh)


def coping2(c, x0, x1, y, pal):
    """the 2 px light coping: lit row, body row"""
    c.hline(x0, x1, y, pal[0]); c.hline(x0, x1, y + 1, pal[1])


def ashlar(c, x0, x1, y0, y1, pal, course=4, bond=12):
    """granite ashlar in running bond: body, a shade joint row per course, head joints staggered"""
    c.rect(x0, y0, x1, y1, pal[1])
    for y in range(y0 + course - 1, y1 + 1, course):
        c.hline(x0, x1, y, pal[2])
        for x in range(x0 + (bond // 2 if ((y - y0) // course) % 2 else 2), x1, bond):
            c.vline(x, y - course + 1, y - 1, pal[2])


def dentil_cornice(c, x0, x1, y, pal, dark):
    """4 px: a lit top row, a dentil row (2 px blocks, 1 px gaps), a body row, a shade row; then a 2 px shadow"""
    c.hline(x0, x1, y, pal[0])
    c.hline(x0, x1, y + 1, pal[2])
    for x in range(x0, x1 + 1, 3):
        c.put(x, y + 1, pal[1]); c.put(x + 1, y + 1, pal[1])
    c.hline(x0, x1, y + 2, pal[1]); c.hline(x0, x1, y + 3, pal[2])
    c.rect(x0, y + 4, x1, y + 5, dark)


def chimney(c, x0, y0, y1, body, cap, w=10):
    """a chimney w px wide from y0 (the cap's top row) down to y1 (into the roof): a 2 px stone cap one px wider a
    side, the body one shade darker than the roof"""
    c.rect(x0, y0 + 2, x0 + w - 1, y1, body[0])
    c.vline(x0 + w - 1, y0 + 2, y1, body[1])
    c.rect(x0 - 1, y0, x0 + w, y0 + 1, cap[1]); c.hline(x0 - 1, x0 + w, y0, cap[0])


def hip_roof(c, x0, x1, eave_y, ridge_y, pal, cap, ridge_w=None):
    """a hipped tile roof front-on: scallop courses clipped to the trapezoid from the eave (x0..x1 at eave_y, the
    roof's bottom row) up to the ridge (ridge_w wide at ridge_y), a 2 px ridge cap, a dark hip line each side"""
    tmp = Canvas(c.w, c.h)
    scallop_courses(tmp, x0, x1, ridge_y, eave_y, pal)
    rw = ridge_w if ridge_w is not None else max(8, (x1 - x0 + 1) // 3)
    rx0, rx1 = (x0 + x1 + 1 - rw) // 2, (x0 + x1 + 1 - rw) // 2 + rw - 1
    for y in range(ridge_y, eave_y + 1):
        k = (y - ridge_y) / max(1, eave_y - ridge_y)
        lx = int(round(rx0 - (rx0 - x0) * k)); rxx = int(round(rx1 + (x1 - rx1) * k))
        tmp.a[y, :max(0, lx)] = 0; tmp.a[y, min(c.w, rxx + 1):] = 0
        tmp.put(lx, y, pal[1]); tmp.put(rxx, y, pal[1])
    c.paste(tmp, 0, 0)
    c.rect(rx0 - 1, ridge_y - 1, rx1 + 1, ridge_y, cap[1]); c.hline(rx0 - 1, rx1 + 1, ridge_y - 1, cap[0])


def railing(c, x0, x1, y0, h, pal, planters=()):
    """an iron roof railing: a top rail, posts every 16 px, a lower rail (planters: see planter_row)"""
    c.hline(x0, x1, y0, pal[0])
    for x in range(x0, x1 + 1, 16):
        c.vline(x, y0, y0 + h - 1, pal[1])
    c.vline(x1, y0, y0 + h - 1, pal[1])
    c.hline(x0, x1, y0 + h - 3, pal[1])


def planter_row(c, y0, h, planters):
    """planters (x, w) 6 px tall standing on the roof at the railing's foot, flowers over them"""
    for i, (px, pw) in enumerate(planters):
        c.rect(px, y0 + h - 6, px + pw - 1, y0 + h - 1, D_OAK[1] if False else (150, 96, 60))
        c.hline(px, px + pw - 1, y0 + h - 6, (178, 120, 78))
        for j, bx in enumerate(range(px + 1, px + pw - 1, 3)):
            c.put(bx, y0 + h - 7, LEAF[(i + j) % 2]); c.put(bx + 1, y0 + h - 7, LEAF[1])
            c.put(bx + (j % 2), y0 + h - 8, BLOOM[(i + j) % 2])


def shuttered_window(c, x, y, w, h, plaster):
    """a 28x40 window with a stone sill and lintel and louvred oak shutters either side (the blank houses)"""
    c.rect(x - 1, y - 1, x + w, y + h, D_GRAN[1]); c.hline(x - 1, x + w, y - 1, D_GRAN[0])
    c.rect(x + 1, y + 1, x + w - 2, y + h - 2, D_GLASS[1])
    c.rect(x + 2, y + 2, x + 3, y + h - 3, D_GLASS[0])
    c.vline(x + w // 2, y + 1, y + h - 2, D_FRAME); c.hline(x + 1, x + w - 2, y + h // 2, D_FRAME)
    for sx in (x - 7, x + w + 1):
        c.rect(sx, y, sx + 5, y + h - 1, D_OAK[1])
        for yy in range(y + 2, y + h - 2, 4):
            c.hline(sx + 1, sx + 4, yy, D_OAK[2])
    c.rect(x - 8, y + h, x + w + 7, y + h + 1, D_GRAN[1]); c.hline(x - 8, x + w + 7, y + h, D_GRAN[0])


# ---- the buildings ---------------------------------------------------------------------------------------------------
FILES = {}
LUA = []


def save(name, c):
    FILES[name] = c.image()


def lua_building(name, x0, x1, front, fx, fy, roof=None, rx=0, ry=0, trigger=None, claims=(), canopies=()):
    LUA.append(dict(name=name, x0=x0, x1=x1, front=front, fx=fx, fy=fy, roof=roof, rx=rx, ry=ry, trigger=trigger, claims=list(claims), canopies=list(canopies)))


def front_canvas(w, gf, top, plaster, extra=None):
    """a front image from the row `top` (world) down to the back line: the ground floor block (bottom on 414), any
    upper block over it, plain wall above that, the house's right edge in shade"""
    c = Canvas(w, BACK - top)
    y = BACK - gf.shape[0]
    c.paste(gf, 0, y - top)
    if extra is not None:
        y -= extra.shape[0]
        c.paste(extra, 0, y - top)
    for yy in range(top, y):
        c.a[yy - top] = gf[0]
    c.rect(w - 2, 0, w - 1, BACK - top - 1, D_PLASTER[plaster][1])
    return c


def roof_strip(bx0, bx1, by0, by1, parapet_h=10, tile_eave=True, dormer=None, garden=False):
    """a flat roof that is a play piece (review fix 3 and 4, one ramp for all): from the top, the parapet (ashlar,
    a 2 px light coping), the ink row at by0 - 1, the lead seam row on the walk (3 px, two greys), the rest of the
    walk in lead, a 6 px tile eave course (tile_eave), a 4 px dentil cornice and a 2 px shadow. The image is the
    box + 1 px a side. dormer: (x, w, h) a dormer standing on the roof behind the parapet, its sill hidden by the
    coping. garden: the parapet is a 12 px iron railing with three planters (the flower hall).
    Returns (canvas, world x, world y)."""
    w = bx1 - bx0 + 2
    above = parapet_h if not garden else 12
    if dormer:
        above = max(above, dormer[2] + 2)
    top = by0 - 1 - above
    eave = 6 if tile_eave else 0
    h = (by1 - top) + eave + 6 + 1
    c = Canvas(w, h)
    oy = -top
    if dormer:
        dx, dw, dh = dormer
        dy0 = by0 - 1 - dh + 2 + oy                                  # its sill 2 px behind the coping
        c.rect(dx, dy0 + 3, dx + dw - 1, by0 - 1 + oy, GRAN[1])
        c.rect(dx + 2, dy0 + 5, dx + dw - 3, by0 - 1 + oy, GLASS[1]); c.rect(dx + 3, dy0 + 6, dx + 5, by0 - 1 + oy, GLASS[0])
        c.vline(dx + dw // 2, dy0 + 5, by0 - 1 + oy, GRAN[0]); c.vline(dx + dw // 2 - 1, dy0 + 5, by0 - 1 + oy, GRAN[0])
        c.hline(dx + 2, dx + dw - 3, (dy0 + 5 + by0 - 1 + oy) // 2, GRAN[0])
        scallop_courses(c, dx - 1, dx + dw, dy0 - 1, dy0 + 2, TILE)  # a two-course tile cap, 1 px wider a side
        c.hline(dx - 1, dx + dw, dy0 - 1, GRAN[0])
    if not garden:
        ashlar(c, 1, w - 2, by0 - parapet_h + oy, by0 - 1 + oy, GRAN)
        coping2(c, 1, w - 2, by0 - parapet_h + oy, GRAN)
    # the walk: the lead seam row under the ink, the lead below
    c.rect(1, by0 + oy, w - 2, by1 - 1 + oy, LEAD[0])
    c.hline(1, w - 2, by0 + 1 + oy, LEAD[1]); c.hline(1, w - 2, by0 + 2 + oy, LEAD[1])
    for x in range(1 + 8, w - 2, 16):
        c.vline(x, by0 + oy, by1 - 1 + oy, LEAD[1])
    y = by1 + oy
    if tile_eave:
        scallop_courses(c, 1, w - 2, y, y + 5, TILE)
        y += 6
    dentil_cornice(c, 1, w - 2, y, GRAN, GRAN[3])
    if garden:                                                         # the planters first (outlined with the strip)
        planter_row(c, by0 - 1 - 12 + oy, 12, [(w // 6, 16), (w // 2 - 8, 16), (w - w // 6 - 16, 16)])
    c.outline()
    c.hline(1, w - 2, by0 - 1 + oy, INK)                               # the ink row over the walk, unbroken
    if garden:                                                         # then the wrought-iron railing in ink
        railing(c, 1, w - 2, by0 - 1 - 12 + oy, 12, [INK, INK])
    return c, bx0 - 1, top


def cloth_canopy(w):
    """a shop canopy in the street awning's vocabulary (review fix 6): the box's width + 2, a 10 px sloping cloth in
    the awning's stripes, a 3 px scalloped valance with an ink edge, the ink row on top"""
    c = Canvas(w, 15)
    for x in range(1, w - 1):
        stripe = ((x - 1) // 8) % 2
        for y in range(1, 11):
            c.put(x, y, CANVAS[1] if stripe else CANVAS[0])
    c.hline(1, w - 2, 1, CANVAS[3])
    for x in range(1, w - 1):                                          # the valance: the stripes continue, a scalloped hem
        stripe = ((x - 1) // 8) % 2
        c.put(x, 11, CANVAS[2] if stripe else CANVAS[3]); c.put(x, 12, CANVAS[2] if stripe else CANVAS[3])
        if (x - 1) % 8 not in (0, 7):
            c.put(x, 13, CANVAS[2] if stripe else CANVAS[3])
    c.outline()
    c.hline(1, w - 2, 0, INK)
    return c


def main(check=False):
    tmx = ET.parse(os.path.join(ROOT, "maps", "downtown_tall.tmx")).getroot()
    boxes = []
    for og in tmx.findall("objectgroup"):
        if og.attrib.get("name") != "props":
            continue
        for o in og.findall("object"):
            a = o.attrib
            d = {p.attrib["name"]: p.attrib.get("value") for p in o.findall("properties/property")}
            d.update(name=a.get("name", ""), x0=int(float(a["x"])), y0=int(float(a["y"])), x1=int(float(a["x"]) + float(a.get("width", 0))),
                     y1=int(float(a["y"]) + float(a.get("height", 0))))
            boxes.append(d)

    # ---- the start house: town_door's ground and first floor, a tile hip over them, a chimney (decoration) ------------
    a = np.array(Image.open(os.path.join(SCENE, "town_door.png")).convert("RGBA"))[140:432]   # 140 x 292, bottom at 414
    w = a.shape[1]
    ridge = BACK - 292 - 6 - 44
    top = ridge - 4
    c = Canvas(w, BACK - top)
    c.paste(a, 0, BACK - 292 - top)
    eave = BACK - 292 - top                                             # the first row of the house block: the cornice
    dentil_cornice(c, 0, w - 1, eave - 6, D_GRAN, D_PLASTER["red"][1]) if False else None
    c.rect(0, eave - 6, w - 1, eave - 1, D_GRAN[1]); c.hline(0, w - 1, eave - 6, D_GRAN[0]); c.hline(0, w - 1, eave - 1, D_GRAN[2])
    for x in range(0, w, 3):
        c.put(x, eave - 5, D_GRAN[2])
    hip_roof(c, 0, w - 1, eave - 7, ridge - top, D_TILE, D_GRAN, ridge_w=48)
    chimney(c, w - 32, ridge - top - 10, eave - 10, D_CHIM, D_GRAN)
    save("dtl_start_front", c)
    lua_building("start", 0, 140, "dtl_start_front", 0, top, claims=[(0, 360)])

    # ---- the closed boxes and the plain fronts after the canal: one-storey shops and houses with tile hips -----------
    k = 0
    for b in boxes:
        isfront = b.get("kind") == "decor" and b.get("layer") == "back" and b["x1"] - b["x0"] >= 48 and b["y1"] - b["y0"] >= 100 and b["name"] in ("", None)
        if not isfront or b["x0"] < 1180 and not b.get("closed") or 1180 <= b["x0"] < 2640 or 2480 <= b["x0"] < 2640:
            continue
        k += 1
        bw = b["x1"] - b["x0"]
        fronts = [int(ch) for ch in str(b.get("fronts", "1")) if ch.isdigit()] or [1]
        style, plaster = b.get("style", "a"), b.get("plaster", "yellow")
        n = len(fronts)
        base, extra = bw // n, bw - (bw // n) * n
        widths = [base + (1 if i < extra else 0) for i in range(n)]
        gf = np.concatenate([ground_floor(fk, style, plaster, ww) for fk, ww in zip(fronts, widths)], axis=1)
        two = k % 4 == 2
        uf = np.concatenate([upper_floor(fk, style, plaster, ww) for fk, ww in zip(fronts, widths)], axis=1) if two else None
        wall_top = BACK - gf.shape[0] - (uf.shape[0] if two else 0)
        flat = k % 5 == 2
        rise = 14 if flat else min(44, 10 + bw // 3)
        ridge = wall_top - 6 - rise
        top = ridge - 4
        c = front_canvas(bw, gf, top, plaster, extra=uf)
        e = wall_top - top                                              # the cornice band: 6 rows over the wall block
        c.rect(0, e - 6, bw - 1, e - 1, D_GRAN[1]); c.hline(0, bw - 1, e - 6, D_GRAN[0]); c.hline(0, bw - 1, e - 1, D_GRAN[2])
        for x in range(0, bw, 3):
            c.put(x, e - 5, D_GRAN[2])
        if flat:                                                        # a lead flat behind a low parapet
            ashlar(c, 0, bw - 1, e - 6 - rise, e - 7, D_GRAN, course=4, bond=12)
            c.hline(0, bw - 1, e - 6 - rise, D_GRAN[0])
        else:
            hip_roof(c, 0, bw - 1, e - 7, ridge - top, D_TILE, D_GRAN, ridge_w=max(10, bw // 3))
        if k % 3 == 1:
            chimney(c, bw - 22, ridge - top - 8, e - 10, D_CHIM, D_GRAN)
        save(f"dtl_closed{k}_front", c)
        lua_building(f"closed{k}", b["x0"], b["x1"], f"dtl_closed{k}_front", b["x0"], top, claims=[(b["x0"], b["y0"])])

    # ---- the bakery 1180-1328: shop bay + door bay (style a, yellow), a first floor, a crow-step gable, a chimney ----
    bw = 148
    gf = np.concatenate([ground_floor(2, "a", "yellow", 74), ground_floor(1, "a", "yellow", 74)], axis=1)
    uf = np.concatenate([upper_floor(2, "a", "yellow", 74), upper_floor(1, "a", "yellow", 74)], axis=1)
    wall_top = BACK - gf.shape[0] - uf.shape[0]
    ridge = wall_top - 6 - 36
    top = ridge - 4
    c = front_canvas(bw, gf, top, "yellow", extra=uf)
    e = wall_top - top
    c.rect(0, e - 6, bw - 1, e - 1, D_GRAN[1]); c.hline(0, bw - 1, e - 6, D_GRAN[0]); c.hline(0, bw - 1, e - 1, D_GRAN[2])
    for x in range(0, bw, 3):
        c.put(x, e - 5, D_GRAN[2])
    hip_roof(c, 0, bw - 1, e - 7, ridge - top, D_TILE, D_GRAN, ridge_w=60)
    chimney(c, 24, ridge - top - 6, e - 10, D_CHIM, D_GRAN)
    save("dtl_bakery_front", c)
    lua_building("bakery", 1180, 1328, "dtl_bakery_front", 1180, top, claims=[(1180, 300)])

    # ---- the wing 1328-1392: a door bay under the lead flat (WING ROOF 1328-1392 y 272-278) ---------------------------
    r, rx, ry = roof_strip(1328, 1392, 272, 278, parapet_h=10, tile_eave=False)
    save("dtl_wing_roof", r)
    gf = ground_floor(1, "d", "red", 64, top_row=302)
    top = 278 + 6 + 1                                                   # under the roof image (its cornice ends at 284)
    c = front_canvas(64, gf, top, "red")
    save("dtl_wing_front", c)
    lua_building("wing", 1328, 1392, "dtl_wing_front", 1328, top, "dtl_wing_roof", rx, ry, trigger=(1328, 272), claims=[(1328, 272), (1320, 278)])

    # ---- the cafe arcade 1416-1536: two round arches of 46 px on 8 to 10 px piers (ARCADE ROOF 1416-1536 y 280-286)
    r, rx, ry = roof_strip(1416, 1536, 280, 286, parapet_h=12, tile_eave=False)
    save("dtl_arcade_roof", r)
    bw = 120
    top = 286 + 6 + 1
    c = Canvas(bw, BACK - top)
    P = D_PLASTER["cream"]
    c.rect(0, 0, bw - 1, BACK - top - 1, P[0])
    for ox0 in (10, 64):                                                # the openings 10..55 and 64..109 (46 px)
        ox1 = ox0 + 45
        cx = ox0 + 23
        spring = 350 - top                                              # the arch springs at 350, its crown at 327
        c.rect(ox0, spring, ox1, BACK - top - 1, D_DARK)
        for y in range(327 - top, spring):
            dy = spring - y
            half = int(round((23 ** 2 - dy ** 2) ** 0.5)) if dy <= 23 else 0
            c.hline(cx - half, cx - 1 + half, y, D_DARK)
        # a lit cafe window and a door inside, under the arch
        c.rect(ox0 + 6, 356 - top, ox1 - 6, 404 - top, D_GLASS[1]); c.rect(ox0 + 7, 358 - top, ox0 + 12, 400 - top, D_GLASS[0])
        c.vline(cx, 356 - top, 404 - top, D_OAK[1]); c.hline(ox0 + 6, ox1 - 6, 380 - top, D_OAK[1])
        # the granite voussoir ring and the piers' edges
        for y in range(323 - top, spring):
            dy = spring - y
            ho = int(round((27 ** 2 - dy ** 2) ** 0.5)) if dy <= 27 else 0
            hi = int(round((23 ** 2 - dy ** 2) ** 0.5)) if dy <= 23 else 0
            c.hline(cx - ho, cx - hi - 1, y, D_GRAN[1]); c.hline(cx + hi, cx - 1 + ho, y, D_GRAN[1])
        c.rect(ox0 - 4, spring, ox0 - 1, BACK - top - 1, D_GRAN[1]); c.rect(ox1 + 1, spring, ox1 + 4, BACK - top - 1, D_GRAN[1])
        c.vline(ox0 - 4, spring, BACK - top - 1, D_GRAN[0]); c.vline(ox1 + 4, spring, BACK - top - 1, D_GRAN[2])
        for y in range(spring + 11, BACK - top, 12):
            c.hline(ox0 - 4, ox0 - 1, y, D_GRAN[2]); c.hline(ox1 + 1, ox1 + 4, y, D_GRAN[2])
    c.rect(0, BACK - top - 4, bw - 1, BACK - top - 1, D_GRAN[2])          # the plinth
    c.rect(bw - 2, 0, bw - 1, BACK - top - 1, P[1])
    save("dtl_arcade_front", c)
    lua_building("arcade", 1416, 1536, "dtl_arcade_front", 1416, top, "dtl_arcade_roof", rx, ry, trigger=(1416, 280), claims=[(1416, 280), (1404, 286)])

    # ---- the guild hall 1552-1680: ashlar, a door at 1572-1613 under the porch (PORCH 1568-1618 y 312), the crow-step
    # gable (GUILD ROOF 1560-1568 y 272 and its steps up to the ridge 1616-1656 y 244, down to 1680 y 256) in tile,
    # the chimney (1628-1644, 200-244) on the ridge, the cornice at 288 ------------------------------------------------
    bw = 128
    top = 288
    c = Canvas(bw, BACK - top)
    ashlar(c, 0, bw - 1, 0, BACK - top - 1, D_GRAN, course=10, bond=24)
    g6 = load_front(6, "c", "ochre")[326:432]                          # the granite front's door with its surround
    c.paste(g6[:, 48:100], 1572 - 1552 - 6, 326 - top)                 # 52 columns round the door (file col 74): door at 1572-1613
    c.rect(0, 0, bw - 1, 5, D_GRAN[1]); c.hline(0, bw - 1, 0, D_GRAN[0]); c.hline(0, bw - 1, 5, D_GRAN[2])
    for x in range(0, bw, 3):
        c.put(x, 1, D_GRAN[2])
    c.rect(0, BACK - top - 4, bw - 1, BACK - top - 1, D_GRAN[2])
    save("dtl_guild_front", c)
    # the porch: a granite slab on two brackets over the door, its top the walk at 312 (50 px: the door + 8)
    pw = 50 + 2
    c = Canvas(pw, 16)
    c.rect(1, 1, pw - 2, 5, GRAN[1]); c.hline(1, pw - 2, 1, GRAN[0]); c.hline(1, pw - 2, 5, GRAN[2])
    for bx in (2, pw - 8):
        for k2 in range(8):
            c.hline(bx + (k2 if bx == 2 else 0), bx + (5 if bx == 2 else 5 - k2), 6 + k2, GRAN[2])
    c.outline(); c.hline(1, pw - 2, 0, INK)
    save("dtl_guild_canopy1", c)
    # the gable: tile courses under granite crow steps, the chimney in brick
    rtop = 199
    c = Canvas(bw + 2, 290 - rtop)
    oy = -rtop
    ox = -1552 + 1
    steps = [(1560, 1568, 272), (1568, 1576, 268), (1576, 1584, 264), (1584, 1592, 260), (1592, 1600, 256), (1600, 1608, 252),
             (1608, 1616, 248), (1616, 1656, 244), (1656, 1664, 248), (1664, 1672, 252), (1672, 1680, 256)]
    scallop_courses(c, 1, bw, 244 + oy, 289 + oy, TILE, phase=1)
    for y in range(244, 272):                                          # clip to the stepped line
        lx = 1680
        for sx0, sx1, sy in steps:
            if sy <= y:
                lx = sx0; break
        rxx = 1552
        for sx0, sx1, sy in reversed(steps):
            if sy <= y:
                rxx = sx1; break
        c.a[y + oy, :max(0, lx + ox)] = 0
        c.a[y + oy, min(c.w, rxx + ox):] = 0
    for i, (sx0, sx1, sy) in enumerate(steps):                          # the granite steps: 6 rows, lit top, dark foot
        c.rect(sx0 + ox, sy + oy, sx1 - 1 + ox, sy + 5 + oy, GRAN[1]); c.hline(sx0 + ox, sx1 - 1 + ox, sy + oy, GRAN[0]); c.hline(sx0 + ox, sx1 - 1 + ox, sy + 5 + oy, GRAN[2])
        if i < len(steps) - 1 and steps[i + 1][2] < sy:
            c.vline(sx1 - 1 + ox, steps[i + 1][2] + oy, sy - 1 + oy, GRAN[2])
        if i > 0 and steps[i - 1][2] < sy:
            c.vline(sx0 + ox, steps[i - 1][2] + oy, sy - 1 + oy, GRAN[2])
    c.a[272 + oy:290 + oy, 0:1552 + ox] = 0
    # the chimney in brick with a stone cap and two pots
    cx0, cx1 = 1628 + ox, 1643 + ox
    c.rect(cx0, 202 + oy, cx1, 243 + oy, BRICK[1])
    for y in range(204 + oy, 244 + oy, 3):
        c.hline(cx0, cx1, y, MORTAR)
        for x in range(cx0 + (2 if ((y - 204 - oy) // 3) % 2 else 5), cx1, 6):
            c.put(x, y + 1, MORTAR); c.put(x, y + 2, MORTAR)
    c.vline(cx0, 202 + oy, 243 + oy, BRICK[0]); c.vline(cx1, 202 + oy, 243 + oy, BRICK[2])
    c.rect(cx0 - 1, 200 + oy, cx1 + 1, 201 + oy, GRAN[1]); c.hline(cx0 - 1, cx1 + 1, 200 + oy, GRAN[0])
    c.rect(cx0 + 3, 196 + oy, cx0 + 5, 199 + oy, BRICK[2]); c.rect(cx1 - 5, 196 + oy, cx1 - 3, 199 + oy, BRICK[2])
    c.outline()
    for sx0, sx1, sy in steps:
        c.hline(sx0 + ox, sx1 - 1 + ox, sy - 1 + oy, INK)
    c.hline(cx0 - 1, cx1 + 1, 199 + oy, INK)
    save("dtl_guild_roof", c)
    lua_building("guild", 1552, 1680, "dtl_guild_front", 1552, top, "dtl_guild_roof", 1552 - 1, rtop - 4, trigger=(1560, 272),
                 claims=[(1560, 272), (1568, 268), (1576, 264), (1584, 260), (1592, 256), (1600, 252), (1608, 248), (1616, 244), (1656, 248), (1664, 252), (1672, 256),
                         (1628, 200), (1552, 282), (1536, 296), (1568, 312)],
                 canopies=[(1568, 312, "dtl_guild_canopy1", 1567, 311)])

    # ---- the market pavilions 1680-1768 and 1816-1888 (PAVILION ROOF y 256): shop bays, lead flats with a tile eave,
    # cloth canopies over their shop windows (CANOPY 1688-1760 y 336, 1816-1888 y 344) ----------------------------------
    for name, x0, x1, style, plaster, cx0, cx1, cy in (("pav1", 1680, 1768, "e", "yellow", 1680, 1752, 336), ("pav2", 1816, 1888, "b", "cream", 1816, 1888, 344)):
        bw = x1 - x0
        r, rx, ry = roof_strip(x0, x1, 256, 262, parapet_h=10, tile_eave=True)
        save(f"dtl_{name}_roof", r)
        gf = ground_floor(2, style, plaster, bw, top_row=302)
        top = 262 + 6 + 6 + 1
        c = front_canvas(bw, gf, top, plaster)
        save(f"dtl_{name}_front", c)
        cv = cloth_canopy(cx1 - cx0 + 2)
        save(f"dtl_{name}_canopy1", cv)
        lua_building(name, x0, x1, f"dtl_{name}_front", x0, top, f"dtl_{name}_roof", rx, ry, trigger=(x0, 256), claims=[(x0, 256), (cx0, cy)],
                     canopies=[(cx0, cy, f"dtl_{name}_canopy1", cx0 - 1, cy - 1)])

    # ---- the tram shed 1912-2000 (SHED ROOF 1912-2000 y 264): the cargo bike's gateway, an arched carriage gate 62 px
    # wide (1934-1996, the bike's depot line at 1934 is its left jamb) and 100 px tall in a plastered wall; a 40x30
    # dormer behind the parapet --------------------------------------------------------------------------------------------
    bw = 88
    r, rx, ry = roof_strip(1912, 2000, 264, 270, parapet_h=8, tile_eave=True, dormer=(26, 40, 30))
    save("dtl_shed_roof", r)
    top = 270 + 6 + 6 + 1
    c = Canvas(bw, BACK - top)
    P = D_PLASTER["yellow"]
    c.rect(0, 0, bw - 1, BACK - top - 1, P[0])
    gx0, gx1 = 1934 - 1912, 1996 - 1912                                 # the opening 22..84
    gcx = (gx0 + gx1) // 2
    gtop = 314 - top                                                    # 100 px tall: 314 to 414
    spring = gtop + 31
    c.rect(gx0, spring, gx1, BACK - top - 1, D_DARK)
    for y in range(gtop, spring):
        dy = spring - y
        half = int(round((31 ** 2 - dy ** 2) ** 0.5)) if dy <= 31 else 0
        c.hline(gcx - half, gcx + half, y, D_DARK)
    gw = np.array(Image.open(os.path.join(SCENE, "town_gateway.png")).convert("RGBA"))   # the approved gateway's inside
    inside = gw[20:138, 14:66]                                          # (its courtyard: a lit back wall, the hut)
    c.paste(inside, gcx - 26, BACK - top - inside.shape[0])
    for y in range(gtop - 4, spring):                                   # the voussoir ring, 4 px
        dy = spring - y
        ho = int(round((35 ** 2 - dy ** 2) ** 0.5)) if dy <= 35 else 0
        hi = int(round((31 ** 2 - dy ** 2) ** 0.5)) if dy <= 31 else 0
        c.hline(gcx - ho, gcx - hi - 1, y, D_GRAN[1]); c.hline(gcx + hi + 1, gcx + ho, y, D_GRAN[1])
    c.rect(gx0 - 4, spring, gx0 - 1, BACK - top - 1, D_GRAN[1]); c.rect(gx1 + 1, spring, gx1 + 4, BACK - top - 1, D_GRAN[1])
    c.vline(gx0 - 4, spring, BACK - top - 1, D_GRAN[0]); c.vline(gx1 + 4, spring, BACK - top - 1, D_GRAN[2])
    for y in range(spring + 11, BACK - top, 12):
        c.hline(gx0 - 4, gx0 - 1, y, D_GRAN[2]); c.hline(gx1 + 1, gx1 + 4, y, D_GRAN[2])
    c.rect(0, BACK - top - 4, bw - 1, BACK - top - 1, D_GRAN[2])
    c.rect(bw - 2, 0, bw - 1, BACK - top - 1, P[1])
    save("dtl_shed_front", c)
    lua_building("shed", 1912, 2000, "dtl_shed_front", 1912, top, "dtl_shed_roof", rx, ry, trigger=(1912, 264), claims=[(1912, 264), (1912, 270)])

    # ---- the kiosk house 2016-2072 (KIOSK ROOF y 248) and the shelter house 2112-2168 (SHELTER ROOF y 264): narrow door
    # bays with one shuttered window over the door -----------------------------------------------------------------------
    for name, x0, x1, y, style, plaster in (("kioskhouse", 2016, 2072, 248, "b", "cream"), ("shelterhouse", 2112, 2168, 264, "d", "red")):
        bw = x1 - x0
        r, rx, ry = roof_strip(x0, x1, y, y + 6, parapet_h=8, tile_eave=True)
        save(f"dtl_{name}_roof", r)
        gf = ground_floor(1, style, plaster, bw, top_row=314)
        top = y + 6 + 6 + 6 + 1
        c = front_canvas(bw, gf, top, plaster)
        wh = 40 if y == 248 else 32
        shuttered_window(c, 14, 318 - wh - 8 - top, 28, wh, plaster)
        save(f"dtl_{name}_front", c)
        lua_building(name, x0, x1, f"dtl_{name}_front", x0, top, f"dtl_{name}_roof", rx, ry, trigger=(x0, y), claims=[(x0, y), (x0 - 16, y + 8), (2000, 256), (2088, 272)])

    # ---- the glass flower hall 2216-2376 (FLOWER ROOF 2216-2376 y 232; the springy AWNING 2208-2264 y 272 on its
    # front): an iron-and-glass hall between granite pilasters, a railed roof garden with three planters ----------------
    bw = 160
    r, rx, ry = roof_strip(2216, 2376, 232, 238, parapet_h=10, tile_eave=False, garden=True)
    save("dtl_hall_roof", r)
    top = 238 + 6 + 1
    c = Canvas(bw, BACK - top)
    c.rect(0, 0, bw - 1, BACK - top - 1, D_GLASS[1])
    for x in range(0, bw, 20):                                          # iron mullions every 20 px
        c.rect(x, 0, x + 1, BACK - top - 1, D_IRON[0]); c.vline(x + 1, 0, BACK - top - 1, D_IRON[1])
    for y in (40, 80, 120, 150):                                        # transoms
        c.rect(0, y, bw - 1, y + 1, D_IRON[0])
    c.rect(0, 0, bw - 1, 2, D_GRAN[1]); c.hline(0, bw - 1, 0, D_GRAN[0])   # a granite head under the roof's cornice
    for x in range(2, bw, 20):                                          # a lit pane column (the reflection)
        c.rect(x + 2, 2, x + 5, BACK - top - 1, D_GLASS[0])
    for x in range(10, bw, 20):                                         # the lattice: a glazing bar in every pane
        c.vline(x, 0, BACK - top - 1, D_IRON[1])
    c.rect(0, 150, bw - 1, 153, D_IRON[0])
    for px in (0, bw - 4):                                              # granite pilasters at both ends
        c.rect(px, 0, px + 3, BACK - top - 1, D_GRAN[1]); c.vline(px, 0, BACK - top - 1, D_GRAN[0]); c.vline(px + 3, 0, BACK - top - 1, D_GRAN[2])
    c.rect(0, BACK - top - 24, bw - 1, BACK - top - 1, D_GRAN[1])      # a granite plinth wall with the door
    c.hline(0, bw - 1, BACK - top - 24, D_GRAN[0])
    c.rect(bw // 2 - 22, BACK - top - 97, bw // 2 + 21, BACK - top - 1, (90, 70, 50))   # the door: oak, 2.1 m
    c.rect(bw // 2 - 20, BACK - top - 95, bw // 2 - 2, BACK - top - 3, (120, 90, 60)); c.rect(bw // 2 + 1, BACK - top - 95, bw // 2 + 19, BACK - top - 3, (120, 90, 60))
    for y in range(BACK - top - 90, BACK - top - 8, 24):
        c.rect(bw // 2 - 18, y, bw // 2 - 4, y + 12, D_GLASS[1]); c.rect(bw // 2 + 3, y, bw // 2 + 17, y + 12, D_GLASS[1])
    c.rect(bw // 2 - 22, BACK - top - 97, bw // 2 + 21, BACK - top - 96, D_IRON[1])
    save("dtl_hall_front", c)
    lua_building("hall", 2216, 2376, "dtl_hall_front", 2216, top, "dtl_hall_roof", rx, ry, trigger=(2216, 232), claims=[(2216, 232), (2180, 240), (2296, 238)])

    # ---- the canal house 2416-2464 (CANAL ROOF y 248): a narrow door bay with a shuttered window, a lead flat --------
    r, rx, ry = roof_strip(2416, 2464, 248, 254, parapet_h=8, tile_eave=True)
    save("dtl_canalhouse_roof", r)
    gf = ground_floor(1, "e", "yellow", 48, top_row=314)
    top = 254 + 6 + 6 + 1
    c = front_canvas(48, gf, top, "yellow")
    shuttered_window(c, 10, 318 - 40 - 8 - top, 28, 40, "yellow")
    save("dtl_canalhouse_front", c)
    lua_building("canalhouse", 2416, 2464, "dtl_canalhouse_front", 2416, top, "dtl_canalhouse_roof", rx, ry, trigger=(2416, 248), claims=[(2416, 248), (2384, 256), (2404, 296)])

    # ---- the fountain to the A2 concept (review fix 7): a kerb basin 1736-1848 with a water band behind a 3 px kerb
    # (decoration, drawn with the FOUNTAIN box), the two rim blocks (RIM 1720-1736 and 1848-1864, y 408, play), the
    # plinth (FOUNTAIN 1776-1808 y 400, play), the column 16 px with the bowl (TIER 1768-1816 y 344, play) and the ball
    # finial at 296; the jets are 2 px arcs drawn in code (arthooks.lua H.drawLowFountain) ------------------------------
    c = Canvas(112, 72)                                                 # the basin front: 1736-1848, y 408-480: the water
    c.rect(0, 0, 111, 1, GRAN[1]); c.hline(0, 111, 0, GRAN[0])         # band behind the kerb, then the basin's outer
    c.rect(0, 2, 111, 12, (96, 150, 190))                               # face below the street in the quay wall's blocks
    c.hline(0, 111, 2, (160, 200, 224))                                 # (the water box's pit is a sunken basin, not a pond)
    for x in range(6, 106, 23):
        c.hline(x, x + 4, 7, (160, 200, 224))
    c.rect(0, 13, 111, 15, GRAN[1]); c.hline(0, 111, 13, GRAN[0]); c.hline(0, 111, 15, GRAN[2])   # the 3 px kerb
    Q = [(106, 91, 103), (89, 75, 98), (83, 68, 95), (70, 58, 92)]
    c.rect(0, 16, 111, 71, Q[2])
    for y in range(16, 72, 8):
        c.hline(0, 111, y, Q[0]); c.hline(0, 111, y + 7, Q[3])
        for x in range((12 if ((y - 16) // 8) % 2 else 0), 112, 24):
            c.vline(x, y + 1, y + 6, Q[3])
    save("dtl_fountain_basin", c)
    c = Canvas(18, 18)                                                  # a rim block (16 x 16 + ink)
    ashlar(c, 1, 16, 1, 16, GRAN, course=5, bond=8)
    coping2(c, 1, 16, 1, GRAN)
    c.outline(); c.hline(1, 16, 0, INK)
    save("dtl_fountain_rim", c)
    c = Canvas(34, 26)                                                  # the plinth 1776-1808, y 400-424 (+ ink)
    ashlar(c, 1, 32, 1, 24, GRAN, course=6, bond=16)
    coping2(c, 1, 32, 1, GRAN)
    c.outline(); c.hline(1, 32, 0, INK)
    save("dtl_fountain_plinth", c)
    c = Canvas(50, 106)                                                 # the column, bowl and finial: x 1767-1817, y 295-401
    oy = -295
    cx0, cx1 = 1784 - 1767, 1799 - 1767                                 # the column 16 px
    c.rect(cx0, 304 + oy, cx1, 400 + oy, GRAN[1]); c.vline(cx0, 304 + oy, 400 + oy, GRAN[0]); c.vline(cx1, 304 + oy, 400 + oy, GRAN[2])
    c.rect(cx0 - 2, 304 + oy, cx1 + 2, 307 + oy, GRAN[1]); c.hline(cx0 - 2, cx1 + 2, 304 + oy, GRAN[0])   # the capital
    c.rect(cx0 - 2, 392 + oy, cx1 + 2, 400 + oy, GRAN[1]); c.hline(cx0 - 2, cx1 + 2, 392 + oy, GRAN[0])   # the base
    for y in range(312 + oy, 390 + oy, 12):
        c.hline(cx0 + 1, cx1 - 1, y, GRAN[2])
    # the ball finial 8 px on a neck
    c.rect(cx0 + 6, 302 + oy, cx1 - 6, 303 + oy, GRAN[2])
    for y in range(296, 302):
        dy = 299 - y
        half = int(round((3.6 ** 2 - dy ** 2) ** 0.5)) if abs(dy) <= 3.6 else 0
        c.hline(1791 - 1767 - half, 1791 - 1767 + half + 1, y + oy, GRAN[1])
    c.put(1791 - 1767 - 1, 297 + oy, GRAN[0]); c.put(1791 - 1767, 297 + oy, GRAN[0])
    # the bowl: 48 wide, its rim the walk at 344, water in it, the underside curving to the column
    c.rect(1, 344 + oy, 48, 346 + oy, GRAN[1]); c.hline(1, 48, 344 + oy, GRAN[0])
    c.rect(4, 347 + oy, 45, 349 + oy, (96, 150, 190)); c.hline(6, 43, 347 + oy, (160, 200, 224))
    for i, (x0b, x1b) in enumerate(((4, 45), (7, 42), (11, 38), (16, 33))):
        c.rect(x0b, 350 + i * 2 + oy, x1b, 351 + i * 2 + oy, GRAN[2] if i else GRAN[1])
    c.outline(); c.hline(1, 48, 343 + oy, INK)
    save("dtl_fountain_column", c)
    LUA.append(dict(name="fountain", x0=1720, x1=1864, front=None, fx=0, fy=0, roof="dtl_fountain_plinth", rx=1775, ry=399, trigger=(1776, 400),
                    claims=[(1776, 400), (1720, 408), (1848, 408), (1768, 344), (1786, 368), (1788, 348)],
                    canopies=[(1720, 408, "dtl_fountain_rim", 1719, 407), (1848, 408, "dtl_fountain_rim", 1847, 407), (1768, 344, "dtl_fountain_column", 1767, 295),
                              (1776, 400, "dtl_fountain_basin", 1736, 408)]))

    # ---- the plaza's old HOUSE boxes and the other hidden boxes are claimed (nothing drawn) ------------------------------
    LUA.append(dict(name="houses", x0=0, x1=0, front=None, fx=0, fy=0, roof=None, rx=0, ry=0, trigger=None,
                    claims=[(1536, 296), (1644, 288), (1832, 296), (2404, 296), (1700, 288), (1912, 270), (2000, 256), (2088, 272), (2180, 240), (2296, 238), (2384, 256)], canopies=[]))

    # ---- the mid row, rebuilt at half size (review fix 2): town_facades.png, scroll 0.5, its foot at screen 148 on
    # the street tier (world 388), moving with the world (L.vmid 1.0). Four storeys of 70 px (3 m at 23 px/m) so the
    # storey that shows over the low row's roofs (its windows at 200-220) is 12 px over the highest eave and 50 over
    # the others; one window per 24 px of front (14 x 22), frames in the plaster's light shade, glass about 140 on
    # screen, pink-grey tile hips or lead flats 25 luma over the low row's roofs, a chimney here and there -----------
    mid_houses = [(0, 72, "hip"), (72, 148, "step"), (148, 220, "flat"), (220, 304, "hip"), (304, 376, "step"), (376, 472, "hip"),
                  (472, 544, "flat"), (544, 628, "hip"), (628, 700, "step"), (700, 796, "hip"), (796, 868, "flat"), (868, 960, "hip")]
    MW, MH = 960, 330
    c = Canvas(MW, MH)
    foot = MH                                                           # row 330 = world 388 on the street tier
    for hi, (hx0, hx1, kind) in enumerate(mid_houses):
        P = M_PLASTER[hi % len(M_PLASTER)]
        hw = hx1 - hx0
        storeys = 4 if hi % 3 == 1 else 3                               # (a taller house every third: a skyline)
        if hi == 0:                                                     # a garden wall with a gate: sky over it (the
            c.rect(hx0, foot - 40, hx1 - 1, foot - 1, M_STONE)          # fountain's gap at the A2 camera)
            c.hline(hx0, hx1 - 1, foot - 40, M_STONE2)
            c.rect(hx0 + 28, foot - 36, hx0 + 43, foot - 1, M_DOOR)
            for y in range(foot - 32, foot - 1, 8):
                c.hline(hx0 + 4, hx1 - 5, y, M_STONE2)
            continue
        wall_top = foot - 70 * storeys
        c.rect(hx0, wall_top, hx1 - 1, foot - 1, P[0])
        c.rect(hx1 - 2, wall_top, hx1 - 1, foot - 1, P[1])
        for s in range(storeys):                                        # storeys: a course line, windows 14 x 22
            sy = foot - 70 * (s + 1)
            c.hline(hx0, hx1 - 1, sy + 69, P[1])
            wy = sy + 26
            n = max(1, (hw - 10) // 24)
            gap = (hw - n * 14) / (n + 1)
            for i in range(n):
                wx = int(round(hx0 + gap + i * (14 + gap)))
                if s == 0 and i == n // 2:                               # the ground floor's door in the middle
                    c.rect(wx - 1, foot - 46, wx + 14, foot - 1, M_STONE)
                    c.rect(wx, foot - 44, wx + 13, foot - 1, M_DOOR)
                    c.vline(wx + 7, foot - 44, foot - 1, P[1])
                    continue
                c.rect(wx - 1, wy - 1, wx + 14, wy + 22, P[1])          # the frame in the plaster's shade
                c.rect(wx, wy, wx + 13, wy + 21, M_GLASS)
                c.vline(wx + 7, wy, wy + 21, P[0]); c.hline(wx, wx + 13, wy + 10, P[0])
                c.hline(wx - 1, wx + 14, wy + 22, M_STONE)
        c.rect(hx0, wall_top - 4, hx1 - 1, wall_top - 1, M_STONE)      # the cornice
        c.hline(hx0, hx1 - 1, wall_top - 1, M_STONE2)
        ridge = wall_top - 4 - (40 if kind != "flat" else 10)
        if kind == "hip":
            hip_roof(c, hx0, hx1 - 1, wall_top - 5, ridge, M_ROOF, [M_STONE, M_STONE2], ridge_w=max(10, hw // 3))
        elif kind == "step":
            n = min(6, hw // 12)
            for i in range(n + 1):
                y = wall_top - 5 - i * 7
                lx, rxx = hx0 + i * 5, hx1 - 1 - i * 5
                if lx > rxx:
                    break
                c.rect(lx, y - 6, rxx, y, P[0])
                c.rect(lx, y - 6, rxx, y - 5, M_STONE)
            c.rect(hx0 + 8, wall_top - 5 - 48, hx1 - 9, wall_top - 5 - 2, P[0]) if False else None
            # the gable's own windows
            for i in range(max(1, (hw - 40) // 24)):
                wx = hx0 + 20 + i * 24
                if wx + 14 < hx1 - 20:
                    c.rect(wx, wall_top - 5 - 24, wx + 9, wall_top - 5 - 10, M_GLASS); c.vline(wx + 4, wall_top - 5 - 24, wall_top - 5 - 10, P[0])
        else:
            c.rect(hx0, ridge, hx1 - 1, wall_top - 5, M_LEAD[1]); c.hline(hx0, hx1 - 1, ridge, M_LEAD[0])
            c.rect(hx0, ridge - 3, hx1 - 1, ridge - 1, M_STONE)
        if hi % 3 == 0:
            cxm = hx1 - 20
            c.rect(cxm, ridge - 12, cxm + 7, wall_top - 6, M_ROOF[1]); c.rect(cxm - 1, ridge - 14, cxm + 8, ridge - 13, M_STONE)
    FILES["town_facades"] = c.image()

    # ---- write ---------------------------------------------------------------------------------------------------------
    lines = ["-- generated by tools/build_dt_rooftops.py (day/07nov-dt): the tall Downtown's low row, option A. Do not edit.",
             "-- buildings = { { name, x0, x1, front = file, fx, fy (the front's top-left, decoration), roof = file, rx, ry",
             "--   (the roof's top-left, a play piece drawn when the trigger box is drawn), trigger = { x0, y0 },",
             "--   claims = { { x0, y0 }, ... } (map boxes this building draws or hides), canopies = { { x0, y0, file, ix, iy } } } }",
             "return {"]
    for b in LUA:
        def q(v):
            return ('"%s"' % v) if isinstance(v, str) else ("nil" if v is None else str(v))
        cl = ", ".join("{ %d, %d }" % tuple(cc) for cc in b["claims"])
        ca = ", ".join('{ %d, %d, "%s", %d, %d }' % tuple(cc) for cc in b["canopies"])
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
