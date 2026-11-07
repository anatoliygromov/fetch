#!/usr/bin/env python3
"""tools/dt_bone_overlap.py: every bone of the tall Downtown against the art on Pepper's line (day/07nov-dt, round 2b).

A bone is drawn 11 x 6 at (x - 5, y - 12), bobbing 2 px. It must not sit on a play piece's drawn pixels: the low
row's roofs (below the walk's top: a bone on the walk stands in front of the parapet), canopies and fountain (riverwalk/dt_lowrow.lua and their files), the statue and its hat, the fountain's
jets (the arcs of arthooks.lua H.drawLowFountainJets), or inside any play box. Prints each overlap with the piece
and the clearance needed; --fix moves those bones up (8 px at a time, up to 24) in maps/downtown_tall.tmx.

  python3 tools/dt_bone_overlap.py [--fix]
"""
import os, re, sys
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "riverwalk", "art", "scene")
TMX = os.path.join(ROOT, "maps", "downtown_tall.tmx")

def lua_table():
    txt = open(os.path.join(ROOT, "riverwalk", "dt_lowrow.lua")).read()
    pieces = []
    # a roof: only its rows from the walk's top down count (a bone on the walk stands in front of the parapet, as a
    # bone on a crate stands in front of the wall behind it)
    for m in re.finditer(r'roof = "([^"]+)", rx = (-?\d+), ry = (-?\d+), trigger = \{ (\d+), (\d+) \}', txt):
        pieces.append((m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(5))))
    for m in re.finditer(r'\{ (\d+), (\d+), "([^"]+)", (-?\d+), (-?\d+) \}', txt):
        pieces.append((m.group(3), int(m.group(4)), int(m.group(5))))
    return pieces

def masks():
    out = []
    for piece in lua_table():
        name, x, y = piece[:3]
        a = np.array(Image.open(os.path.join(SCENE, name + ".png")).convert("RGBA"))[..., 3] > 0
        if len(piece) == 4:
            a = a.copy(); a[:max(0, piece[3] - y)] = False
        out.append((name, x, y, a))
    return out

def jets_mask():
    pts = set()
    cx = (1776 + 1808) // 2
    for d in (-1, 1):
        for i in range(2, 29):
            k = i / 28
            x = cx + d * int(round(4 + 46 * k)); y = int(round(304 - 16 * k + 130 * k * k))
            for dx in (0, 1):
                for dy in (0, 1):
                    pts.add((x + dx - (1 if d < 0 else 0), y + dy))
    return pts

def main(fix=False):
    tree = ET.parse(TMX); root = tree.getroot()
    bones, boxes = [], []
    for og in root.findall("objectgroup"):
        for o in og.findall("object"):
            a = o.attrib
            if og.attrib.get("name") == "bones":
                bones.append((o, int(float(a["x"])), int(float(a["y"]))))
            elif og.attrib.get("name") == "props":
                props = {p.attrib["name"]: p.attrib.get("value") for p in o.findall("properties/property")}
                boxes.append((a.get("name", ""), int(float(a["x"])), int(float(a["y"])), int(float(a["x"]) + float(a.get("width", 0))),
                              int(float(a["y"]) + float(a.get("height", 0))), props))
    ms = masks()
    jets = jets_mask()
    statue = [b for b in boxes if b[0] in ("STATUE",)]
    hits = []
    for o, bx, by in bones:
        x0, x1, y0, y1 = bx - 5, bx + 6, by - 14, by - 4            # the bone's rows with its bob
        why = []
        for name, px, py, a in ms:
            h, w = a.shape
            sx0, sx1, sy0, sy1 = max(x0, px), min(x1, px + w), max(y0, py), min(y1, py + h)
            if sx1 > sx0 and sy1 > sy0 and a[sy0 - py:sy1 - py, sx0 - px:sx1 - px].any():
                why.append(name)
        for n, bx0, by0, bx1, by1, p in boxes:
            if p.get("layer") == "play" and p.get("kind") in ("solid", "oneway", "decor") and n not in ("", None) and x1 > bx0 and x0 < bx1 and y1 > by0 and y0 < by1:
                if n == "STATUE" or p.get("kind") != "decor":
                    why.append("box " + n)
        if any((x, y) in jets for x in range(x0, x1) for y in range(y0, y1)):
            why.append("jets")
        if why:
            hits.append((o, bx, by, why))
    for o, bx, by, why in hits:
        print(f"bone ({bx}, {by}) on {', '.join(sorted(set(why)))}")
    print(f"{len(bones)} bones, {len(hits)} overlap")
    if fix and hits:
        for o, bx, by, why in hits:
            ny = by
            for _ in range(3):
                ny -= 8
                x0, x1, y0, y1 = bx - 5, bx + 6, ny - 14, ny - 4
                clear = not any((x, y) in jets for x in range(x0, x1) for y in range(y0, y1))
                for name, px, py, a in ms:
                    h, w = a.shape
                    sx0, sx1, sy0, sy1 = max(x0, px), min(x1, px + w), max(y0, py), min(y1, py + h)
                    if sx1 > sx0 and sy1 > sy0 and a[sy0 - py:sy1 - py, sx0 - px:sx1 - px].any(): clear = False
                for n, bx0, by0, bx1, by1, p in boxes:
                    if p.get("layer") == "play" and (n == "STATUE" or p.get("kind") in ("solid", "oneway")) and n and x1 > bx0 and x0 < bx1 and y1 > by0 and y0 < by1: clear = False
                if clear: break
            print(f"  moved ({bx}, {by}) -> y {ny}")
            o.attrib["y"] = str(ny)
        tree.write(TMX, encoding="UTF-8", xml_declaration=True)
        print("written", TMX)

if __name__ == "__main__":
    main("--fix" in sys.argv)
