#!/usr/bin/env python3
"""Layer wireframe of a level, screen by screen (25 Oct 2026).

Draws what the level file places on each depth layer as flat colour boxes, so the composition of every screen can be
read without art: what is far, what is behind Pepper, what she can use, what moves, what is in front.

  layer_wireframe.py riverwalk OUT.png [--cols 3] [--scale 2]

Reads riverwalk/level/<name>.lua (props, lamps, movers, critters, bikes, ball, girl, pieces) and <name>.map
(8 px cells: # solid, ~ water, / \\ slopes). The far layers are drawn as the bands they occupy on screen.
"""
import re
import sys

from PIL import Image, ImageDraw, ImageFont

LV = sys.argv[1]
OUT = sys.argv[2]
COLS = int(sys.argv[sys.argv.index("--cols") + 1]) if "--cols" in sys.argv else 3
S = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 2
src = open(f"riverwalk/level/{LV}.lua").read()
rows = open(f"riverwalk/level/{LV}.map").read().split("\n")
rows = [r for r in rows if r]
W = len(rows[0]) * 8
H = len(rows) * 8

C = {
    "sky": (226, 233, 241), "clouds": (240, 244, 248), "city": (205, 211, 226), "shore": (190, 206, 190),
    "water": (164, 190, 214), "back": (236, 214, 160), "backtx": (120, 96, 50), "ground": (150, 152, 162),
    "play": (255, 255, 255), "playedge": (208, 52, 44), "move": (240, 138, 36), "goal": (242, 201, 76),
    "road": (84, 88, 108), "front": (34, 34, 40), "pepper": (20, 20, 24), "grid": (255, 255, 255),
}
font = ImageFont.load_default()


def field(s, k):
    m = re.search(r"\b" + k + r"\s*=\s*(-?[\d.]+|\"[^\"]*\"|true|false|FX\s*[+-]\s*\d+|FX)", s)
    if not m:
        return None
    v = m.group(1)
    if v.startswith('"'):
        return v.strip('"')
    if v in ("true", "false"):
        return v == "true"
    if v.startswith("FX"):
        fx = int(re.search(r"local FX = (\d+)", src).group(1))
        return fx + (int(v.replace("FX", "").replace(" ", "") or 0))
    return float(v)


def block(name):
    m = re.search(r"^L\." + name + r"\s*=\s*{(.*?)^}", src, re.S | re.M)
    return m.group(1) if m else ""


def entries(body):
    out = []
    for line in body.split("\n"):
        line = line.split("--")[0] if not line.strip().startswith("os.getenv") else line
        if "{" in line and ("x0" in line or "x =" in line or "zoneX0" in line):
            out.append(line)
    return out


props = []
skip_pilot = True
for line in entries(block("props")):
    if "rw_gable_front" in line and skip_pilot:
        continue
    props.append({k: field(line, k) for k in ("name", "kind", "layer", "x0", "x1", "y0", "y1", "art", "hidden",
                                               "railing", "ax", "ay")})

img = Image.new("RGB", (W, 240 if H <= 240 else H), C["sky"])
d = ImageDraw.Draw(img)
# far layers as their screen bands (River Walk numbers; other levels draw what they declare)
d.rectangle([0, 61, W, 138], fill=C["city"])
d.rectangle([0, 113, W, 146], fill=C["shore"])
d.rectangle([0, 146, W, 240], fill=C["water"])
for x in range(0, W, 400):
    d.ellipse([x + 60, 30, x + 160, 60], fill=C["clouds"])
# back layer
for p in props:
    if p["layer"] == "back" and p["x0"] is not None:
        d.rectangle([p["x0"], p["y0"], p["x1"] - 1, p["y1"] - 1], fill=C["back"])
        if p["railing"]:
            d.line([p["x0"], p["y0"] + 2, p["x1"], p["y0"] + 2], fill=C["backtx"])
        lab = p["name"] or p["art"] or ("railing" if p["railing"] else "")
        if lab:
            d.text((p["x0"] + 2, max(p["y0"], 0) + 2), lab.lower(), fill=C["backtx"], font=font)
for ln in entries(block("lamps")):
    x, y = field(ln, "x"), field(ln, "y")
    d.rectangle([x - 2, y - 101, x + 2, y - 10], fill=C["back"], outline=C["backtx"])
    d.ellipse([x - 4, y - 106, x + 4, y - 98], fill=C["goal"])
# terrain
for r, row in enumerate(rows):
    for c, ch in enumerate(row):
        if ch == "#":
            d.rectangle([c * 8, r * 8, c * 8 + 7, r * 8 + 7], fill=C["ground"])
        elif ch == "~":
            d.rectangle([c * 8, r * 8, c * 8 + 7, r * 8 + 7], fill=(120, 150, 190))
        elif ch in "/\\":
            pts = [(c * 8, r * 8 + 8), (c * 8 + 8, r * 8 + 8), (c * 8 + 8, r * 8)] if ch == "/" else \
                  [(c * 8, r * 8), (c * 8, r * 8 + 8), (c * 8 + 8, r * 8 + 8)]
            d.polygon(pts, fill=C["ground"])
# the road in front of the promenade (River Walk)
if LV == "riverwalk":
    for r, row in enumerate(rows):
        pass
    d.rectangle([0, 199, 1240, 240], fill=C["road"]); d.rectangle([2880, 199, W, 240], fill=C["road"])
# play layer: usable props outlined, decoration on the play layer flagged
for p in props:
    if p["layer"] != "play" or p["x0"] is None:
        continue
    usable = p["kind"] in ("solid", "oneway")
    box = [p["x0"], p["y0"], p["x1"] - 1, p["y1"] - 1]
    if usable:
        d.rectangle(box, fill=C["play"], outline=C["playedge"], width=2)
        lab = (p["name"] or p["art"] or "").lower()
        d.text((p["x0"] + 3, p["y0"] + 3), lab, fill=C["playedge"], font=font)
    else:
        d.rectangle(box, fill=C["back"], outline=(150, 0, 150), width=2)
        d.text((p["x0"] + 2, p["y0"] + 2), ((p["name"] or p["art"] or "").lower()) + " (decor on play!)",
               fill=(150, 0, 150), font=font)
for ln in entries(block("movers")):
    x0, x1, y0, y1, a, b = (field(ln, k) for k in ("x0", "x1", "y0", "y1", "from", "to"))
    d.rectangle([a, y0, (b or a) + (x1 - x0), y1 + 2], outline=C["move"], width=1)
    d.rectangle([x0, y0 - 6, x1, y1], fill=C["move"])
    d.text((x0 + 2, y0 - 16), (field(ln, "name") or "").lower(), fill=C["move"], font=font)
for ln in entries(block("bikes")):
    z0, z1 = field(ln, "zoneX0"), field(ln, "zoneX1")
    d.rectangle([z0, 156, z1, 184], outline=C["move"], width=1)
    d.text((z0 + 3, 158), "bike zone", fill=C["move"], font=font)
for ln in entries(block("critters")):
    x0, x1 = field(ln, "x0"), field(ln, "x1")
    if x1 and x0 and x1 > x0:
        d.line([x0, 86, x1, 86], fill=C["move"], width=2)
        d.text((x0 + 3, 74), (field(ln, "kind") or "").lower(), fill=C["move"], font=font)
for k in ("ball", "girl"):
    m = re.search(r"^L\." + k + r"\s*=\s*{([^}]*)}", src, re.M)
    if m:
        x, y = field(m.group(1), "x"), field(m.group(1), "y")
        if k == "ball":
            d.ellipse([x - 4, y - 8, x + 4, y], fill=C["goal"], outline=C["pepper"])
        else:
            d.rectangle([x - 10, y - 60, x + 10, y - 1], fill=C["goal"], outline=C["pepper"])
            d.text((x - 9, y - 58), "mia", fill=C["pepper"], font=font)
st = re.search(r"^L\.start\s*=\s*{([^}]*)}", src, re.M)
if st:
    x, y = field(st.group(1), "x"), field(st.group(1), "y")
    d.rectangle([x - 26, y - 38, x + 26, y - 1], fill=C["pepper"])
# front layer
for p in props:
    if p["layer"] == "front" and p["x0"] is not None:
        d.rectangle([p["x0"], p["y0"], p["x1"] - 1, min(p["y1"], 240)], fill=C["front"])

# cut into screens with numbers and a 1 px frame
n = (W + 319) // 320
rowsn = (n + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * (320 * S + 8), rowsn * (240 * S + 24)), (255, 255, 255))
sd = ImageDraw.Draw(sheet)
for i in range(n):
    cut = img.crop((i * 320, 0, i * 320 + 320, 240)).resize((320 * S, 240 * S), Image.NEAREST)
    x, y = (i % COLS) * (320 * S + 8), (i // COLS) * (240 * S + 24)
    sheet.paste(cut, (x, y + 20))
    sd.text((x + 2, y + 4), f"screen {i + 1}: x {i * 320}-{i * 320 + 320}", fill=(0, 0, 0), font=font)
sheet.save(OUT)
print("screens", n, "size", sheet.size)
