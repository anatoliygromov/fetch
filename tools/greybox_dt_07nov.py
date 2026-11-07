#!/usr/bin/env python3
"""Greybox frames for the Downtown (tall) redesign, 7 Nov (docs/review/07nov/dt/design/README.md).

Flat-colour 320x240 mock frames, boxes coloured by role, Pepper's real sprite at 1x for scale:
  as-is   the level as it is today, every map box drawn by its role (what is walkable, what is decoration)
  A       option A, "the roofs of the low row": a row of low true-scale buildings on the street whose roofs are the
          high road, the tall old-town houses on the mid row behind, sky above
  B       option B, "the portico street": the tall fronts kept, one continuous stone portico along them whose top
          is the high road, nothing else on the walls at that height

  python3 tools/greybox_dt_07nov.py [out dir]      (default docs/review/07nov/dt/design/greybox)

World y as in the level: the street at 424, the high road 232-280. Camera (cx, cy) as in the game (cy 240 is the
street tier). Writes <name>.png (1x) and <name>_3x.png.
"""
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.chdir(ROOT)
from blockout_lib import pepper  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/review/07nov/dt/design/greybox"

# the colour code (one colour per role; the same in every frame)
SKY = (118, 168, 226)
CLOUD = (236, 240, 246)
MID = (214, 206, 206)          # the mid row's houses (lighter: further away)
MID_ROOF = (186, 182, 196)
MID_WIN = (198, 194, 204)
WALL = (204, 168, 136)         # back decoration: walls at Pepper's scale (no outline)
WALL2 = (184, 150, 118)
ROOF = (168, 92, 72)           # a roof Pepper walks on (play: outlined)
ROOF_LIT = (214, 134, 104)
WALK = (150, 122, 92)          # a stone surface Pepper walks on (play: outlined)
WALK_LIT = (196, 168, 132)
INK = (38, 30, 32)
DECO = (172, 154, 146)         # decoration props (no outline)
WATER = (58, 98, 172)          # hazard
STREET = (126, 112, 118)
KERB = (164, 156, 158)
ROUTE = (255, 150, 40)
GOLD = (250, 200, 60)
SPIRE = (196, 198, 214)
WIN = (118, 128, 150)

W, H = 320, 240


def new():
    im = Image.new("RGB", (W, H), SKY)
    return im, ImageDraw.Draw(im)


class View:
    def __init__(self, cx, cy):
        self.cx, self.cy = cx, cy
        self.im, self.d = new()
        self.rel = 240 - cy                         # as vcam.lua: the mid row rises 0.6, the far layers 0.3

    def sx(self, x):
        return x - self.cx

    def sy(self, y):
        return y - self.cy

    def box(self, x0, y0, x1, y1, c, outline=None, lit=None):
        a, b = self.sx(x0), self.sy(y0)
        e, f = self.sx(x1), self.sy(y1)
        self.d.rectangle([a, b, e - 1, f - 1], fill=c)
        if lit:
            self.d.rectangle([a, b, e - 1, b], fill=lit)
        if outline:
            self.d.rectangle([a - 1, b - 1, e, f], outline=outline)

    def play(self, x0, y0, x1, y1, roof=False):
        c, l = (ROOF, ROOF_LIT) if roof else (WALK, WALK_LIT)
        self.box(x0, y0, x1, y1, c, outline=INK, lit=l)

    def gable(self, x0, x1, eave, ridge, rx=None, roof=True):
        """a pitched roof seen from the front: eave at y eave, the ridge at ridge (rx: the ridge's x, default middle)"""
        rx = (x0 + x1) // 2 if rx is None else rx
        pts = [(self.sx(x0), self.sy(eave)), (self.sx(rx), self.sy(ridge)), (self.sx(x1), self.sy(eave))]
        self.d.polygon(pts, fill=ROOF if roof else WALL2, outline=INK if roof else None)

    def text(self, x, y, s, c=INK):
        self.d.text((self.sx(x), self.sy(y)), s, fill=c)

    def label(self, x, y, s, c=(255, 255, 255)):
        self.d.text((x, y), s, fill=c)

    def route(self, pts, c=ROUTE):
        self.d.line([(self.sx(x), self.sy(y)) for x, y in pts], fill=c, width=2)

    def dot(self, x, y, c=GOLD, r=2):
        self.d.ellipse([self.sx(x) - r, self.sy(y) - r, self.sx(x) + r, self.sy(y) + r], fill=c, outline=INK)

    def pepper(self, x, y):
        p = pepper()
        self.im.paste(p, (self.sx(x) - p.width // 2, self.sy(y) - p.height), p)

    def save(self, name, caption):
        self.d.rectangle([0, 0, W - 1, 9], fill=(20, 20, 24))
        self.label(2, 0, caption)
        os.makedirs(OUT, exist_ok=True)
        self.im.save(f"{OUT}/{name}.png")
        self.im.resize((W * 3, H * 3), Image.NEAREST).save(f"{OUT}/{name}_3x.png")
        print("wrote", f"{OUT}/{name}.png")


# ----------------------------------------------------------------------------------------------- common scenery
def sky_and_mid(v, houses, clouds=((40, 30), (170, 22), (280, 36)), spire=None):
    """the sky, a cloud or two, the mid row's tall houses (23 px/m, scroll 0.5 x / 0.6 y) standing on the square 30 px
    up behind the street; houses: list of (x0, x1, roof kind, roofline) in mid-layer px"""
    for cx, cy in clouds:
        x = (cx - v.cx * 0.05) % 400 - 40
        y = cy + int(v.rel * 0.1)
        v.d.ellipse([x, y, x + 36, y + 14], fill=CLOUD); v.d.ellipse([x + 10, y - 8, x + 34, y + 10], fill=CLOUD)
    if spire is not None:
        x = spire - v.cx * 0.03
        y = 40 + int(v.rel * 0.3)
        v.d.polygon([(x, y - 70), (x - 7, y), (x + 7, y)], fill=SPIRE)
    foot = 148 + int(v.rel * 0.6)   # the mid row's foot on screen: 148 at the street tier (scene.lua, 30 px up), moving down 0.6
    for x0, x1, kind, top in houses:
        a, b = x0 - v.cx * 0.5, x1 - v.cx * 0.5
        if b < 0 or a > W:
            continue
        t = foot - top
        v.d.rectangle([a, t, b - 1, foot], fill=MID)
        if kind == "gable":
            v.d.polygon([(a, t), ((a + b) / 2, t - (b - a) * 0.45), (b - 1, t)], fill=MID_ROOF)
        elif kind == "step":
            n = 4; sw = (b - a) / 2 / n
            for i in range(n):
                v.d.rectangle([a + i * sw, t - (i + 1) * 9, b - 1 - i * sw, t], fill=MID_ROOF)
        else:
            v.d.rectangle([a, t - 14, b - 1, t], fill=MID_ROOF)
        # windows: one per 24 px, storeys of 64 px
        for yy in range(int(t) + 16, int(foot) - 10, 64):
            for xx in range(int(a) + 6, int(b) - 10, 24):
                v.d.rectangle([xx, yy, xx + 9, yy + 14], fill=MID_WIN)
    # the square's floor under the mid row down to the street's far kerb
    if v.sy(424) > foot:
        v.d.rectangle([0, foot, W, min(H, v.sy(424))], fill=(176, 170, 172))


MID_HOUSES = [(0, 120, "gable", 150), (120, 210, "step", 170), (210, 330, "flat", 140), (330, 420, "gable", 160),
              (420, 560, "step", 180), (560, 650, "flat", 150), (650, 770, "gable", 165), (770, 860, "step", 175),
              (860, 1000, "flat", 145), (1000, 1100, "gable", 160), (1100, 1230, "step", 170), (1230, 1330, "gable", 150),
              (1330, 1460, "flat", 165), (1460, 1560, "step", 180), (1560, 1700, "gable", 150), (1700, 1800, "flat", 160)]


def street(v, x0=-1000, x1=9000, water=()):
    if v.sy(424) >= H:
        return
    v.d.rectangle([v.sx(x0), v.sy(424), v.sx(x1), v.sy(424) + 6], fill=KERB)
    v.d.rectangle([v.sx(x0), v.sy(430), v.sx(x1), H], fill=STREET)
    for a, b in water:
        v.d.rectangle([v.sx(a), v.sy(424), v.sx(b) - 1, H], fill=WATER)


# ----------------------------------------------------------------------------------------------- as is
def load_map():
    t = ET.parse("maps/downtown_tall.tmx")
    rows = []
    for og in t.getroot().findall("objectgroup"):
        for o in og.findall("object"):
            a = o.attrib
            props = {p.attrib["name"]: p.attrib.get("value") for p in o.findall("properties/property")}
            rows.append((og.attrib.get("name"), a.get("name", ""), int(float(a.get("x", 0))), int(float(a.get("y", 0))),
                         int(float(a.get("width", 0))), int(float(a.get("height", 0))), props))
    return rows


def as_is(cx, cy, name, caption, px=None):
    v = View(cx, cy)
    rows = load_map()
    sky_and_mid(v, MID_HOUSES, spire=3396)
    # the back fronts (decoration, 432 px tall, past the top): drawn first
    for g, n, x, y, w, h, p in rows:
        if g == "props" and p.get("kind") == "decor" and p.get("layer") == "back" and w >= 48 and h >= 100 and not p.get("closed"):
            v.box(x, y - 300, x + w, 424, WALL if (x // 100) % 2 else WALL2)
            for yy in range(y - 280, 400, 70):
                for xx in range(x + 10, x + w - 20, 36):
                    v.box(xx, yy, xx + 18, yy + 34, WIN)
    street(v, water=[(1736, 1848), (2480, 2640)])
    for g, n, x, y, w, h, p in rows:
        if g != "props" or p.get("closed"):
            continue
        k, l = p.get("kind"), p.get("layer")
        if k == "decor" and l == "back" and not (w >= 48 and h >= 100):
            v.box(x, y, x + w, y + h, DECO)
        elif k == "decor" and l == "play":
            v.box(x, y, x + w, y + h, DECO)
        elif k in ("solid", "oneway") and l == "play":
            v.play(x, y, x + w, y + h)
            if n and w >= 40:
                v.text(x + 1, y - 9 if y > v.cy + 12 else y + h + 1, n.lower())
    for g, n, x, y, w, h, p in rows:
        if g == "bones":
            v.dot(x, y - 6, GOLD, 1)
    if px:
        v.pepper(*px)
    v.save(name, caption)


# ----------------------------------------------------------------------------------------------- option A
def low_front(v, x0, x1, eave, kind="shed", door=None, awning=None, windows=True, shop=False):
    """a low true-scale building on the street: its wall from the street up to its eave (decoration), a door 2.1 m
    (97 px), a shop window; the roof is drawn by the caller (play)"""
    v.box(x0, eave, x1, 424, WALL if kind == "shed" else WALL2)
    if door:
        v.box(door, 424 - 97, door + 44, 424, (120, 84, 64))
    if windows:
        for xx in range(x0 + 12, x1 - 30, 40):
            if door and door - 30 < xx < door + 50:
                continue
            if shop:
                v.box(xx, 424 - 110, xx + 28, 424 - 20, WIN)
            else:
                v.box(xx, eave + 30, xx + 20, eave + 70, WIN)
    if awning:
        a, b, y = awning
        v.box(a, y, b, y + 4, (200, 60, 60))


def option_a_plaza():
    """A1: screen 4-5 at the roof tier: the bakery (2 storeys, its sign and roof terrace = way up A), the cafe
    loggia (an open arcade on the plaza, its lead roof is the walkway), the statue with the cat under its edge"""
    v = View(1240, 100)
    sky_and_mid(v, MID_HOUSES, spire=3396)
    street(v)
    # the bakery: a 2 storey house, eave at 296, a stepped gable up to 232 on its left, a roof terrace at 272 right
    low_front(v, 1180, 1320, 300, kind="house", door=1200, shop=True)
    v.gable(1176, 1324, 300, 236, rx=1250)                      # its tile roof (play: a one-way slope), the ridge 236
    v.play(1270, 304, 1310, 308)                                # the bakery sign (gold bone) hangs under the eave, as today
    v.box(1320, 282, 1400, 424, WALL)                           # the bakery's wing: a lower flat-roofed house
    v.play(1328, 272, 1392, 278, roof=True)                     # the roof terrace (the old BALCONY box): a flat lead roof with a parapet
    v.box(1326, 262, 1394, 272, DECO)                           # its parapet behind her
    # the cafe loggia: an open arcade 1404-1548, three round arches, its roof the walkway at 280
    v.box(1404, 286, 1548, 424, WALL2)
    for ax in (1412, 1460, 1508):
        v.d.pieslice([v.sx(ax), v.sy(300), v.sx(ax + 32), v.sy(332)], 180, 360, fill=(70, 60, 70))
        v.box(ax, 316, ax + 32, 424, (70, 60, 70))
    v.play(1416, 280, 1536, 286, roof=True)                     # the loggia's roof (LOGGIA box as today)
    v.box(1414, 270, 1538, 280, DECO)                           # a low parapet behind her
    # the statue in front of the arcade (as today: pedestal 384, arm 348, hat 316)
    v.play(1440, 384, 1488, 424)
    v.box(1450, 320, 1478, 384, (76, 120, 100))
    v.play(1478, 348, 1518, 352); v.play(1452, 316, 1476, 320)
    v.box(1506, 334, 1518, 348, (230, 140, 60))                 # the cat on the arm
    v.dot(1512, 352, (240, 60, 60), 3)                          # the ball
    # the next house (the guild hall's gable starts at the screen's right)
    v.box(1552, 300, 1700, 424, WALL)
    v.route([(1290, 304), (1360, 272), (1392, 272), (1460, 280), (1536, 280)])
    v.text(1330, 250, "roof terrace")
    v.text(1420, 258, "loggia roof: bark the cat from here")
    v.text(1184, 222, "bakery")
    v.pepper(1372, 272)
    v.save("A1_plaza_roofs", "A1  option A: the bakery roof terrace and the loggia roof over the statue  (cam 1240, 100)")


def option_a_guild():
    """A2: screen 6 at the roof tier: the guild hall (one storey, a tall stepped gable roof, the chimney on its
    ridge), the fountain plaza with two market pavilions whose flat roofs are the galleries"""
    v = View(1580, 90)
    sky_and_mid(v, MID_HOUSES, spire=3396)
    street(v, water=[(1736, 1848)])
    v.box(1404, 286, 1552, 424, WALL2); v.play(1416, 280, 1536, 286, roof=True)   # the loggia (left edge)
    # the guild hall: wall 1552-1700 up to its eave 282; the stepped gable is the ROOF (play), ridge 244, chimney
    low_front(v, 1552, 1700, 282, kind="house", door=1600)
    steps = [(1560, 1568, 272), (1568, 1576, 268), (1576, 1584, 264), (1584, 1592, 260), (1592, 1600, 256),
             (1600, 1608, 252), (1608, 1616, 248), (1616, 1656, 244), (1656, 1664, 248), (1664, 1672, 252), (1672, 1680, 256)]
    v.d.polygon([(v.sx(1552), v.sy(282)), (v.sx(1636), v.sy(246)), (v.sx(1700), v.sy(282))], fill=ROOF, outline=INK)
    for a, b, y in steps:
        v.play(a, y, b, y + 6, roof=True)
    v.play(1628, 200, 1644, 244)                                # the chimney (the golden bone)
    v.dot(1636, 192, GOLD, 3)
    # the fountain plaza: two market pavilions (one storey, flat lead roofs with a parapet = the galleries at 256)
    for a, b in ((1680, 1768), (1816, 1888)):
        v.box(a, 262, b, 424, WALL)
        v.play(a, 256, b, 262, roof=True)
        v.box(a - 2, 246, b + 2, 256, DECO)
        v.box(a + 8, 336, b - 8, 344, DECO)                     # the pavilion's canopy (the old middle-tier balcony)
        v.play(a + 8, 344, b - 8, 348)
    # the fountain stands free between them: the basin at the street, the column, the top tier at 344
    v.play(1720, 408, 1736, 424); v.play(1848, 408, 1864, 424)
    v.box(1786, 348, 1798, 400, DECO); v.play(1768, 344, 1816, 348); v.play(1776, 400, 1808, 424)
    v.box(1700, 262, 1912, 424, WALL2) if False else None
    v.box(1888, 270, 1912, 424, WALL2)
    v.route([(1536, 280), (1560, 272), (1611, 244), (1636, 200), (1660, 248), (1680, 256), (1768, 256), (1816, 256), (1888, 256)])
    v.text(1556, 212, "guild hall roof")
    v.text(1684, 232, "pavilion roof")
    v.text(1760, 290, "gap over the fountain")
    v.pepper(1600, 256)
    v.save("A2_guild_fountain_roofs", "A2  option A: the guild hall's gable roof and chimney, the pavilion roofs over the fountain  (cam 1580, 90)")


def option_a_tram():
    """A3: screens 7-8 at the roof tier: the tram shed's roof with its dormer, the kiosk and shelter row's roofs,
    the flower hall with its springy awning and roof garden, the canal house, the footbridge"""
    v = View(2060, 90)
    sky_and_mid(v, MID_HOUSES, spire=3396)
    street(v, water=[(2480, 2640)])
    # the tram shed: a wide low shed 1912-2000, roof 270, a dormer on it at 264
    low_front(v, 1912, 2000, 276, door=None, windows=False)
    v.box(1930, 424 - 100, 1982, 424, (70, 60, 70))              # the shed's gate (the cargo bike rides in)
    v.play(1920, 264, 1976, 270, roof=True)                     # the DORMER: the shed's flat roof
    # the kiosk house: 2000-2088, eave 254, the roof ledge at 248 (a flat roof)
    low_front(v, 2000, 2088, 254, door=2010, shop=True)
    v.play(2016, 248, 2072, 254, roof=True)
    v.box(2014, 240, 2074, 248, DECO)
    # the shelter house 2088-2180, eave 270, ledge 264
    low_front(v, 2088, 2180, 270, door=2130)
    v.play(2112, 264, 2168, 270, roof=True)
    # the flower hall: 2180-2384, a glass hall, the springy awning over its door at 272, the roof garden at 232
    low_front(v, 2180, 2384, 238, kind="house", door=2225, shop=True)
    v.play(2208, 272, 2264, 278)                                # the springy awning (bounce 56)
    v.box(2210, 268, 2262, 272, (200, 60, 60))
    v.play(2288, 232, 2376, 238, roof=True)                     # the FLOWER ROOF: the hall's roof garden
    v.box(2286, 222, 2378, 232, DECO)
    v.text(2290, 212, "roof garden")
    # the canal house 2384-2480, eave 254, ledge 248
    low_front(v, 2384, 2480, 254, door=2420)
    v.play(2416, 248, 2464, 254, roof=True)
    # the footbridge over the canal 2480-2640 at 272 (solid)
    v.play(2480, 272, 2640, 278)
    v.box(2480, 260, 2640, 272, DECO)
    v.route([(1888, 256), (1920, 264), (1976, 264), (2016, 248), (2072, 248), (2112, 264), (2168, 264), (2236, 272),
             (2262, 216), (2300, 232), (2376, 232), (2416, 248), (2464, 248), (2480, 272), (2640, 272)])
    v.text(1916, 240, "tram shed roof")
    v.text(2110, 244, "shelter roof")
    v.text(2400, 230, "canal house")
    v.pepper(2140, 264)
    v.save("A3_tram_flower_roofs", "A3  option A: tram shed, kiosk and shelter roofs, the flower hall's awning and roof garden, the footbridge  (cam 2060, 90)")


def option_a_street():
    """A4: the plaza at the street tier: the loggia's arcade, the statue, the guild hall's door, the fountain free"""
    v = View(1420, 240)
    sky_and_mid(v, MID_HOUSES, spire=3396)
    street(v, water=[(1736, 1848)])
    v.box(1300, 300, 1400, 424, WALL); v.play(1328, 272, 1392, 278, roof=True)
    v.box(1404, 286, 1548, 424, WALL2)
    for ax in (1412, 1460, 1508):
        v.d.pieslice([v.sx(ax), v.sy(300), v.sx(ax + 32), v.sy(332)], 180, 360, fill=(70, 60, 70))
        v.box(ax, 316, ax + 32, 424, (70, 60, 70))
    v.play(1416, 280, 1536, 286, roof=True)
    v.play(1440, 384, 1488, 424); v.box(1450, 320, 1478, 384, (76, 120, 100))
    v.play(1478, 348, 1518, 352); v.play(1452, 316, 1476, 320)
    v.box(1506, 334, 1518, 348, (230, 140, 60)); v.dot(1512, 352, (240, 60, 60), 3)
    v.play(1512, 404, 1552, 408); v.box(1530, 408, 1534, 424, DECO)
    low_front(v, 1552, 1700, 282, kind="house", door=1600)
    v.d.polygon([(v.sx(1552), v.sy(282)), (v.sx(1636), v.sy(246)), (v.sx(1700), v.sy(282))], fill=ROOF, outline=INK)
    for a, b in ((1680, 1768), (1816, 1888)):
        v.box(a, 262, b, 424, WALL); v.play(a, 256, b, 262, roof=True)
        v.box(a + 8, 336, b - 8, 344, DECO); v.play(a + 8, 344, b - 8, 348)
    v.play(1720, 408, 1736, 424); v.play(1848, 408, 1864, 424)
    v.box(1786, 348, 1798, 400, DECO); v.play(1768, 344, 1816, 348); v.play(1776, 400, 1808, 424)
    v.play(1408, 396, 1440, 424)
    v.text(1416, 300, "open arcade (cafe)")
    v.text(1556, 296, "guild hall")
    v.text(1690, 270, "market pavilion")
    v.pepper(1424, 396)
    v.save("A4_plaza_street", "A4  option A at the street: the arcade, the statue and the cat, the guild hall, the pavilions and the fountain  (cam 1420, 240)")


# ----------------------------------------------------------------------------------------------- option B
def tall_front(v, x0, x1, shade=0):
    """a true-scale tall house (the approved styled fronts): from the street past the top of the screen"""
    v.box(x0, -200, x1, 424, WALL if shade == 0 else WALL2)
    for yy in range(-180, 200, 128):                             # storeys above the portico: calm, no balconies
        for xx in range(x0 + 14, x1 - 30, 44):
            v.box(xx, yy, xx + 24, yy + 56, WIN)


def portico(v, x0, x1, top, arches=True):
    """the stone portico: round arches on piers from the street up to its top; its top is the walk (play, outlined)
    with a low parapet behind"""
    v.box(x0, top + 6, x1, 424, (150, 140, 136))
    if arches:
        for ax in range(x0 + 8, x1 - 40, 48):
            v.d.pieslice([v.sx(ax), v.sy(top + 30), v.sx(ax + 36), v.sy(top + 66)], 180, 360, fill=(74, 64, 70))
            v.box(ax, top + 48, ax + 36, 424, (74, 64, 70))
    v.play(x0, top, x1, top + 6)
    v.box(x0 - 2, top - 10, x1 + 2, top, DECO)


def option_b_plaza():
    v = View(1240, 100)
    v.d.rectangle([0, 0, W, H], fill=SKY)
    tall_front(v, 1180, 1320); tall_front(v, 1320, 1404, 1); tall_front(v, 1404, 1552); tall_front(v, 1552, 1700, 1)
    street(v)
    portico(v, 1180, 1320, 304)                                  # the bakery's portico: its top at the sign's height
    v.play(1270, 304, 1310, 308)                                 # the sign hangs off the portico's corner (gold)
    portico(v, 1328, 1392, 272)                                  # a step up
    portico(v, 1416, 1536, 280)                                  # the loggia: the portico over the statue
    v.play(1440, 384, 1488, 424); v.box(1450, 320, 1478, 384, (76, 120, 100))
    v.play(1478, 348, 1518, 352); v.play(1452, 316, 1476, 320)
    v.box(1506, 334, 1518, 348, (230, 140, 60)); v.dot(1512, 352, (240, 60, 60), 3)
    portico(v, 1560, 1700, 272, arches=False)
    v.route([(1290, 304), (1360, 272), (1392, 272), (1460, 280), (1536, 280)])
    v.text(1184, 262, "portico top: the walk")
    v.text(1420, 258, "loggia: bark from here")
    v.pepper(1372, 272)
    v.save("B1_plaza_portico", "B1  option B: the tall fronts kept, one stone portico along them, its top the walk  (cam 1240, 100)")


def option_b_guild():
    v = View(1580, 90)
    v.d.rectangle([0, 0, W, H], fill=SKY)
    tall_front(v, 1404, 1552); tall_front(v, 1552, 1700, 1); tall_front(v, 1700, 1912)
    street(v, water=[(1736, 1848)])
    portico(v, 1416, 1536, 280)
    # the guild house's porch: the portico rises in steps to a landing with a lantern (the chimney box: the gold)
    v.box(1552, 282, 1700, 424, (150, 140, 136))
    steps = [(1560, 1568, 272), (1568, 1576, 268), (1576, 1584, 264), (1584, 1592, 260), (1592, 1600, 256),
             (1600, 1608, 252), (1608, 1616, 248), (1616, 1656, 244), (1656, 1664, 248), (1664, 1672, 252), (1672, 1680, 256)]
    for a, b, y in steps:
        v.play(a, y, b, y + 6)
    v.d.pieslice([v.sx(1596), v.sy(300), v.sx(1656), v.sy(360)], 180, 360, fill=(74, 64, 70)); v.box(1596, 330, 1656, 424, (74, 64, 70))
    v.play(1628, 200, 1644, 244); v.dot(1636, 192, GOLD, 3)
    # the fountain's flanks: the portico a storey higher (the galleries), the gap over the fountain
    for a, b in ((1680, 1768), (1816, 1888)):
        portico(v, a, b, 256)
    v.play(1720, 408, 1736, 424); v.play(1848, 408, 1864, 424)
    v.box(1786, 348, 1798, 400, DECO); v.play(1768, 344, 1816, 348); v.play(1776, 400, 1808, 424)
    v.box(1888, 270, 1912, 424, (150, 140, 136)); v.play(1888, 264, 1912, 270)
    v.route([(1536, 280), (1560, 272), (1611, 244), (1636, 200), (1660, 248), (1680, 256), (1768, 256), (1816, 256), (1888, 256)])
    v.text(1556, 212, "guild porch steps")
    v.text(1684, 232, "portico, a storey higher")
    v.pepper(1600, 256)
    v.save("B2_guild_fountain_portico", "B2  option B: the guild porch's steps and lantern, the portico over the fountain's flanks  (cam 1580, 90)")


def option_b_tram():
    v = View(2060, 90)
    v.d.rectangle([0, 0, W, H], fill=SKY)
    tall_front(v, 1912, 2000); tall_front(v, 2000, 2088, 1); tall_front(v, 2088, 2180); tall_front(v, 2180, 2296, 1)
    tall_front(v, 2296, 2384); tall_front(v, 2384, 2480, 1)
    street(v, water=[(2480, 2640)])
    portico(v, 1920, 1976, 264); portico(v, 2016, 2072, 248); portico(v, 2112, 2168, 264)
    v.play(2208, 272, 2264, 278); v.box(2210, 268, 2262, 272, (200, 60, 60))
    portico(v, 2288, 2376, 232); portico(v, 2416, 2464, 248)
    v.play(2480, 272, 2640, 278); v.box(2480, 260, 2640, 272, DECO)
    v.route([(1888, 256), (1920, 264), (1976, 264), (2016, 248), (2072, 248), (2112, 264), (2168, 264), (2236, 272),
             (2262, 216), (2300, 232), (2376, 232), (2416, 248), (2464, 248), (2480, 272), (2640, 272)])
    v.text(1916, 240, "portico pieces, each on its arches")
    v.pepper(2140, 264)
    v.save("B3_tram_flower_portico", "B3  option B: the portico in pieces along the tram street, the springy awning, the footbridge  (cam 2060, 90)")


def option_b_street():
    v = View(1420, 240)
    v.d.rectangle([0, 0, W, H], fill=SKY)
    tall_front(v, 1320, 1404, 1); tall_front(v, 1404, 1552); tall_front(v, 1552, 1700, 1); tall_front(v, 1700, 1912)
    street(v, water=[(1736, 1848)])
    portico(v, 1328, 1392, 272); portico(v, 1416, 1536, 280)
    v.play(1440, 384, 1488, 424); v.box(1450, 320, 1478, 384, (76, 120, 100))
    v.play(1478, 348, 1518, 352); v.play(1452, 316, 1476, 320)
    v.box(1506, 334, 1518, 348, (230, 140, 60)); v.dot(1512, 352, (240, 60, 60), 3)
    v.play(1512, 404, 1552, 408); v.play(1408, 396, 1440, 424)
    v.box(1552, 282, 1700, 424, (150, 140, 136))
    v.d.pieslice([v.sx(1596), v.sy(300), v.sx(1656), v.sy(360)], 180, 360, fill=(74, 64, 70)); v.box(1596, 330, 1656, 424, (74, 64, 70))
    for a, b in ((1680, 1768), (1816, 1888)):
        portico(v, a, b, 256)
    v.play(1720, 408, 1736, 424); v.play(1848, 408, 1864, 424)
    v.box(1786, 348, 1798, 400, DECO); v.play(1768, 344, 1816, 348); v.play(1776, 400, 1808, 424)
    v.text(1416, 300, "under the portico")
    v.text(1556, 296, "guild porch")
    v.pepper(1424, 396)
    v.save("B4_plaza_street", "B4  option B at the street: under the portico, the statue, the guild porch, the fountain  (cam 1420, 240)")


if __name__ == "__main__":
    as_is(1240, 100, "asis_1_plaza", "AS IS  screen 4-5 at the high road: every map box by role  (cam 1240, 100)", px=(1372, 272))
    as_is(1580, 90, "asis_2_guild", "AS IS  screen 6 at the high road  (cam 1580, 90)", px=(1600, 256))
    as_is(2060, 90, "asis_3_tram", "AS IS  screens 7-8 at the high road  (cam 2060, 90)", px=(2140, 264))
    as_is(1420, 240, "asis_4_street", "AS IS  the plaza at the street  (cam 1420, 240)", px=(1424, 396))
    option_a_plaza(); option_a_guild(); option_a_tram(); option_a_street()
    option_b_plaza(); option_b_guild(); option_b_tram(); option_b_street()
