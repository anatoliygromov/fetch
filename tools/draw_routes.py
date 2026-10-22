#!/usr/bin/env python3
"""Paper maps with the routes drawn on: a Tiled map rendered by tools/tiled/render_map.py, plus the main route (a
thick light-blue line), the high route (orange), and markers: lamps (yellow L), secrets (S), the golden bone (a
gold star), steam puffs (white arrows up, with their lift), loose tiles (red X), the landmark (a magenta ring).

  python3 tools/draw_routes.py citypark_tall [out.png]     (default: /home/claude/out/design-round2/<name>_routes.png)
  python3 tools/draw_routes.py rooftops_sketch [out.png]

The routes are Pepper's feet, point by point, in ROUTES below (world px). Lamps, secrets, the golden bone, steam
and loose tiles are read from the map itself.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tiled"))
sys.path.insert(0, HERE)
import render_map as R  # noqa: E402

ROOT = os.path.dirname(HERE)
ROUTES = {
    "citypark_tall": {
        "rows": 3, "scale": 2, "landmark": (2832, 60),
        "main": [(60, 328), (150, 328), (196, 312), (240, 328), (320, 328), (340, 300), (448, 300), (470, 328),
                 (700, 328), (748, 332), (804, 332), (840, 346), (920, 346), (960, 328), (1180, 328), (1268, 312),
                 (1300, 328), (1330, 272), (1363, 272), (1416, 300), (1488, 300), (1585, 328), (1700, 328),
                 (2000, 328), (2068, 332), (2148, 332), (2228, 332), (2306, 328), (2400, 300), (2476, 300),
                 (2536, 300), (2600, 328), (2640, 296), (2640, 256), (2640, 216), (2716, 184), (2800, 152),
                 (2724, 120), (2810, 88), (2856, 88), (2856, 328), (2840, 328)],
        "high": [(400, 300), (440, 300), (528, 256), (578, 256), (628, 216), (944, 216), (1008, 200), (1116, 184),
                 (1220, 200), (1324, 232), (1428, 216), (1532, 200), (1620, 200), (1700, 192), (1772, 192),
                 (1772, 152), (1772, 192), (1832, 192), (1928, 200), (2312, 200), (2372, 216), (2472, 200),
                 (2568, 216), (2640, 216)],
        "high2": [[(1345, 272), (1345, 232)], [(1778, 244), (1856, 224), (1800, 192)]],   # ways up 2 and 3
    },
    "rooftops": {
        "rows": 1, "scale": 1, "landmark": (3744, 184),
        "main": [(40, 1144), (576, 1144), (768, 952), (896, 952), (960, 888), (1024, 952), (1256, 952), (1256, 840),
                 (1300, 856), (1792, 856), (1856, 792), (1920, 856), (2024, 856), (2024, 744), (2060, 760),
                 (2112, 760), (2176, 696), (2240, 760), (2374, 760), (2374, 648), (2420, 664), (2464, 664),
                 (2480, 760), (3052, 760), (3052, 648), (3100, 664), (3294, 664), (3294, 552), (3340, 568),
                 (3388, 568), (3420, 440), (3480, 448), (3514, 448), (3514, 360), (3560, 376), (3612, 376),
                 (3612, 264), (3640, 280), (3698, 280), (3698, 168), (3744, 184), (3700, 276), (3672, 376),
                 (3640, 376)],
        "high": [(1398, 856), (1398, 744), (1440, 760), (1680, 760), (1792, 728), (1888, 696), (1938, 696),
                 (1938, 584), (1980, 600), (2112, 568), (2240, 536), (2560, 536), (2600, 600), (2848, 600),
                 (2896, 552), (2930, 600), (2954, 600), (2954, 440), (2990, 456), (3330, 424), (3438, 424),
                 (3438, 264), (3470, 280)],
        "high2": [],
    },
    "rooftops_sketch": {
        "rows": 1, "scale": 1, "landmark": (1824, 136),
        "main": [(40, 904), (288, 904), (480, 712), (768, 712), (864, 616), (960, 712), (1008, 712), (1200, 520),
                 (1264, 520), (1328, 456), (1392, 520), (1440, 520), (1632, 328), (1692, 328), (1692, 216),
                 (1700, 232), (1778, 232), (1778, 120), (1824, 136), (1850, 136), (1870, 328), (1740, 328)],
        "high": [(632, 712), (632, 600), (640, 616), (662, 616), (662, 504), (720, 520), (812, 520), (868, 520),
                 (924, 520), (1000, 520), (1104, 488), (1200, 456), (1218, 456), (1218, 344), (1280, 360),
                 (1364, 360), (1420, 360), (1496, 360), (1500, 312), (1500, 360), (1526, 360), (1526, 216),
                 (1580, 232)],
        "high2": [],
    },
}
MAIN, HIGH = (110, 210, 255), (255, 150, 40)


def main(argv):
    name = argv[0]
    out = argv[1] if len(argv) > 1 else "/home/claude/out/design-round2/%s_routes.png" % name
    cfg = ROUTES[name]
    tmx = os.path.join(ROOT, "maps", name + ".tmx")
    S = cfg["scale"]
    W, H, rows, layers = R.load(tmx)
    top = -min([0] + [o["y"] for _, objs in layers for o in objs]) + 4
    im = R.render(tmx, S).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    font = ImageFont.load_default()

    def P(x, y):
        return (x * S, (y + top) * S)

    def line(pts, col, w):
        d.line([P(x, y - 6) for x, y in pts], fill=col + (230,), width=w * S, joint="curve")

    line(cfg["main"], MAIN, 3)
    line(cfg["high"], HIGH, 3)
    for seg in cfg["high2"]:
        line(seg, HIGH, 2)
    for lname, objs in layers:
        for o in objs:
            p, cls, x, y = o["p"], o["cls"], o["x"], o["y"]
            if cls == "lamps":
                d.rectangle([P(x - 6, y - 60), P(x + 6, y - 48)], fill=(255, 225, 70, 255))
                d.text(P(x - 3, y - 60), "L", fill=(0, 0, 0, 255), font=font)
            elif cls == "secrets":
                d.ellipse([P(x - 2, y - 22), P(x + 10, y - 10)], fill=(255, 215, 0, 255))
                d.text(P(x + 1, y - 22), "S", fill=(0, 0, 0, 255), font=font)
            elif cls == "bones" and p.get("golden"):
                cx, cy = x, y - 16
                star = []
                for k in range(10):
                    import math
                    r = 9 if k % 2 == 0 else 4
                    a = -math.pi / 2 + k * math.pi / 5
                    star.append(P(cx + r * math.cos(a), cy + r * math.sin(a)))
                d.polygon(star, fill=(255, 200, 0, 255), outline=(120, 60, 0, 255))
            elif cls == "steam":
                x1, lift = x + o["w"], p.get("lift", 96)
                cx = (x + x1) / 2
                d.rectangle([P(x, y), P(x1, y + 8)], fill=(235, 235, 240, 255))
                d.line([P(cx, y), P(cx, y - lift)], fill=(235, 235, 240, 200), width=2 * S)
                d.polygon([P(cx - 6, y - lift + 8), P(cx + 6, y - lift + 8), P(cx, y - lift)], fill=(235, 235, 240, 255))
                d.text(P(x1 + 2, y - 12), "%s +%d%s" % (o["name"] or "STEAM", lift, " (bark)" if p.get("bark") else ""),
                       fill=(235, 235, 240, 255), font=font)
            elif cls == "props" and p.get("loose"):
                d.line([P(x, y - 4), P(x + o["w"], y + 6)], fill=(255, 60, 60, 255), width=2 * S)
                d.line([P(x, y + 6), P(x + o["w"], y - 4)], fill=(255, 60, 60, 255), width=2 * S)
    lx, ly = cfg["landmark"]
    d.ellipse([P(lx - 30, ly - 30), P(lx + 30, ly + 30)], outline=(255, 80, 255, 255), width=2 * S)
    d.text(P(lx - 28, ly + 32), "LANDMARK", fill=(255, 80, 255, 255), font=font)
    im = Image.alpha_composite(im, ov).convert("RGB")
    # a legend in the top left corner
    lg = ImageDraw.Draw(im)
    lg.rectangle([4, 4, 300, 92], fill=(16, 18, 22))
    entries = [(MAIN, "main route (the low road)"), (HIGH, "high route (thin: other ways up)"),
               ((255, 225, 70), "L lamp (checkpoint)"), ((255, 215, 0), "S secret / star: the golden bone"),
               ((235, 235, 240), "steam puff (vent, arrow: its lift)"), ((255, 60, 60), "X loose tile")]
    for k, (col, txt) in enumerate(entries):
        lg.rectangle([10, 10 + k * 13, 30, 18 + k * 13], fill=col)
        lg.text((36, 8 + k * 13), txt, fill=(230, 230, 230), font=font)
    im = R.stack(im, cfg["rows"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out)
    print("wrote", out, im.size)


if __name__ == "__main__":
    main(sys.argv[1:])
