#!/usr/bin/env python3
"""Draws a Tiled map (maps/<name>.tmx) as a PNG, layer by layer, without Tiled.

  python3 tools/tiled/render_map.py maps/citypark.tmx out.png [--scale 2] [--rows 3]

--rows N cuts the level into N strips stacked under each other (easier to look at than one long strip).
Colours: terrain grey (solid) and blue (water); props orange (solid, filled), yellow (one-way, top edge drawn
thick), grey outline (decoration); zones red; movers cyan with their path; critters purple with their patrol;
lamps yellow; bones white (gold: super); story green (start, Mia, the ball, perches numbered); hints as bands.
A dashed line marks Pepper's usual feet line (y 184) and each screen (320 px) is numbered. Zones with no height
(hints, bike zones) are bands above the map, as in Tiled.
"""
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from level_to_tiled import tmx_props, parse_lua, shift  # noqa: E402

REL = {"relx": "x", "rely": "y", "relxy": "xy"}


def absolute(p, x, y):
    """relx. / rely. / relxy. properties (drag-safe offsets) back to the plain fields, as riverwalk/tiled.lua does."""
    out = {k: v for k, v in p.items() if k.split(".", 1)[0] not in REL}
    for k, v in p.items():
        pre, _, field = k.partition(".")
        if pre in REL and field:
            if isinstance(v, str) and v.lstrip().startswith("{"):
                v = parse_lua(v)
            out[field] = shift(v, REL[pre], round(x), round(y))
    return out

TERR = {"#": (78, 82, 96), "~": (52, 104, 168), "/": (120, 100, 70), "\\": (120, 100, 70)}
PROP = {"solid": (255, 150, 60), "oneway": (255, 220, 70), "decor": (150, 150, 160)}
LAYER = {"zones": (255, 70, 100), "movers": (70, 200, 255), "critters": (190, 100, 255), "lamps": (255, 225, 70),
         "bones": (245, 245, 245), "story": (80, 255, 130), "props": (255, 160, 64)}


def load(path):
    root = ET.parse(path).getroot()
    w, h = int(root.get("width")), int(root.get("height"))
    chars = {}
    for ts in root.findall("tileset"):
        fg = int(ts.get("firstgid"))
        for t in ts.findall("tile"):
            p = dict(tmx_props(t))
            if "char" in p:
                chars[fg + int(t.get("id"))] = p["char"]
    rows = []
    for el in root.findall("layer"):
        if el.get("name") == "terrain":
            cells = [int(c) for c in el.find("data").text.replace("\n", "").split(",") if c.strip()]
            rows = ["".join(chars.get(g % 536870912, "?") if g else "." for g in cells[r * w:(r + 1) * w])
                    for r in range(h)]
    layers = []
    for el in root.findall("objectgroup"):
        objs = []
        for o in el.findall("object"):
            objs.append({"name": o.get("name", ""), "cls": o.get("type", o.get("class", "")) or el.get("name"),
                         "x": float(o.get("x")), "y": float(o.get("y")),
                         "w": float(o.get("width", 0)), "h": float(o.get("height", 0)),
                         "point": o.find("point") is not None,
                         "p": absolute(dict(tmx_props(o)), float(o.get("x")), float(o.get("y")))})
        layers.append((el.get("name"), objs))
    return w * 8, h * 8, rows, layers


def render(path, scale=2):
    W, H, rows, layers = load(path)
    S = scale
    top = -min([0] + [o["y"] for _, objs in layers for o in objs]) + 4     # bands above the map (hints, zones)
    im = Image.new("RGB", (W * S, int(H + top) * S), (32, 36, 44))
    d0 = ImageDraw.Draw(im)
    d0.rectangle([0, 0, W * S, top * S - 1], fill=(22, 24, 30))
    font = ImageFont.load_default()

    class Shift:                                   # draws with y moved down by top
        def __init__(self, d):
            self.d = d

        def _xy(self, pts):
            if pts and isinstance(pts[0], tuple):
                return [(x, y + top * S) for x, y in pts]
            return [v + (top * S if i % 2 else 0) for i, v in enumerate(pts)]

        def rectangle(self, xy, **kw):
            self.d.rectangle(self._xy(xy), **kw)

        def ellipse(self, xy, **kw):
            self.d.ellipse(self._xy(xy), **kw)

        def line(self, xy, **kw):
            self.d.line(self._xy(xy), **kw)

        def polygon(self, xy, **kw):
            self.d.polygon(self._xy(xy), **kw)

        def text(self, xy, s, **kw):
            self.d.text((xy[0], xy[1] + top * S), s, **kw)

    d = Shift(ImageDraw.Draw(im, "RGBA"))

    def R(x0, y0, x1, y1, **kw):
        d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], **kw)

    def text(x, y, s, fill):
        d.text((x * S + 1, y * S), s, fill=fill, font=font)

    for sx in range(0, W, 320):                                   # screens
        d.line([(sx * S, -top * S), (sx * S, H * S)], fill=(60, 66, 80), width=1)
        text(sx + 2, H - 12, "screen %d  x %d" % (sx // 320 + 1, sx), (120, 130, 150))
    for r, line in enumerate(rows):                               # terrain
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            x, y = c * 8, r * 8
            col = TERR.get(ch, (255, 0, 255))
            if ch == "/":
                d.polygon([(x * S, (y + 8) * S), ((x + 8) * S, y * S), ((x + 8) * S, (y + 8) * S)], fill=col)
            elif ch == "\\":
                d.polygon([(x * S, y * S), ((x + 8) * S, (y + 8) * S), (x * S, (y + 8) * S)], fill=col)
            else:
                R(x, y, x + 8, y + 8, fill=col)
    for x in range(0, W, 6):                                      # the usual feet line
        d.line([(x * S, 184 * S), ((x + 3) * S, 184 * S)], fill=(255, 255, 255, 70))

    perch = 0
    for lname, objs in layers:
        base = LAYER.get(lname, (200, 200, 200))
        band = 0
        for o in objs:
            p, cls = o["p"], o["cls"]
            x, y, w, h = o["x"], o["y"], o["w"], o["h"]
            if cls == "props":
                kind = p.get("kind", "decor")
                col = PROP.get(kind, (200, 200, 200))
                if p.get("hidden"):
                    col = (255, 120, 200)
                if kind == "solid":
                    R(x, y, x + w, y + h, fill=col + (120,), outline=col)
                elif kind == "oneway":
                    R(x, y, x + w, y + h, fill=col + (60,))
                    d.line([(x * S, y * S), ((x + w) * S, y * S)], fill=col, width=2 * S)
                else:
                    R(x, y, x + w, y + h, outline=col + (150,) if p.get("layer") != "front" else (110, 110, 120))
                if o["name"] and w >= 14:
                    text(x + 1, y + 1, o["name"], (255, 255, 255))
            elif cls in ("pieces", "passages"):
                R(x, y, x + w, y + h, outline=(255, 120, 200))
                text(x + 1, y - 9, p.get("kind", cls), (255, 120, 200))
            elif cls == "hints":
                col = (80, 255, 130) if p.get("btn") else (120, 200, 255)
                R(x, y, x + w, y + h, fill=col + (50,), outline=col + (160,))
                label = ("[%s] " % p["btn"].upper() if p.get("btn") else "") + p.get("text", "")
                if p.get("need"):
                    label += "  (%s)" % p["need"]
                text(max(x, 0) + 2, y - 1, label, col)
            elif cls == "bikes":
                col = base
                zy0 = p.get("minY", 150)
                R(x, zy0, x + w, 184, fill=col + (40,), outline=col)
                text(x + 2, zy0 + 1, "%s zone: every %ss" % (p.get("kind", "bike"), p.get("every")), col)
            elif cls == "secrets":
                R(x, y, x + w, y + h, fill=(255, 215, 0, 60), outline=(255, 215, 0))
                text(x, y - 9, "SECRET " + (o["name"] or ""), (255, 215, 0))
            elif cls == "movers":
                R(x, y, x + w, y + h, fill=base + (160,), outline=base)
                if "from" in p and "to" in p:
                    d.line([(p["from"] * S, (y + h + 2) * S), ((p["to"] + w) * S, (y + h + 2) * S)], fill=base, width=S)
                text(x, y - 9, o["name"] or "mover", base)
            elif cls == "bones":
                col = (255, 210, 60) if p.get("super") else base
                R(x - 3, y - 12, x + 3, y - 7, fill=col)
            elif cls == "lamps":
                d.line([(x * S, y * S), (x * S, (y - 40) * S)], fill=base, width=S)
                d.ellipse([(x - 3) * S, (y - 44) * S, (x + 3) * S, (y - 38) * S], fill=base)
            elif cls == "magpie.perches":
                perch += 1
                d.ellipse([(x - 3) * S, (y - 6) * S, (x + 3) * S, y * S], fill=(40, 40, 40), outline=(200, 200, 255))
                text(x + 4, y - 10, str(perch), (200, 200, 255))
            elif o["point"]:
                col = base
                d.ellipse([(x - 3) * S, (y - 6) * S, (x + 3) * S, y * S], fill=col)
                if "x0" in p and "x1" in p:
                    d.line([(p["x0"] * S, (y + 2) * S), (p["x1"] * S, (y + 2) * S)], fill=col, width=S)
                label = cls.upper() if cls not in ("critters",) else p.get("kind", cls).upper()
                text(x + 4, y - 10, label, col)
                if cls == "start":                                     # Pepper's box at the start: 34 x 26
                    R(x - 17, y - 26, x + 17, y, outline=(80, 255, 130, 160))
            else:
                R(x, y, x + w, y + h, outline=base)
                text(x + 1, y + 1, o["name"] or cls, base)
            band += 1
    return im


def stack(im, n):
    if n <= 1:
        return im
    W, H = im.size
    part = -(-W // n)
    out = Image.new("RGB", (part, H * n + 6 * (n - 1)), (16, 18, 22))
    for i in range(n):
        out.paste(im.crop((i * part, 0, min(W, (i + 1) * part), H)), (0, i * (H + 6)))
    return out


def main(argv):
    scale, nrows = 2, 1
    if "--scale" in argv:
        i = argv.index("--scale")
        scale = int(argv[i + 1])
        del argv[i:i + 2]
    if "--rows" in argv:
        i = argv.index("--rows")
        nrows = int(argv[i + 1])
        del argv[i:i + 2]
    src, out = argv[0], argv[1]
    stack(render(src, scale), nrows).save(out)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])
