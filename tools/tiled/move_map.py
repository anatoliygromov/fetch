#!/usr/bin/env python3
"""Drags everything in a Tiled map (for tools/check_tiled.sh): python3 move_map.py in.tmx out.tmx dx dy
Every object moves by (dx, dy) and dy / 8 empty rows are added at the top of the terrain, as Map > Resize Map with
an offset does in Tiled (dy: a multiple of 8). The check then proves that what belongs to an object moved with it."""
import sys
import xml.etree.ElementTree as ET


def num(v):
    f = float(v)
    return str(int(f)) if f.is_integer() else repr(f)


def main(src, dst, dx, dy):
    dx, dy = int(dx), int(dy)
    tree = ET.parse(src)
    root = tree.getroot()
    w, add = int(root.get("width")), dy // 8
    root.set("height", str(int(root.get("height")) + add))
    for layer in root.iter("layer"):
        layer.set("height", str(int(layer.get("height")) + add))
        data = layer.find("data")
        data.text = "\n" + ",\n".join([",".join(["0"] * w)] * add + [data.text.strip()]) + "\n"
    for o in root.iter("object"):
        o.set("x", num(float(o.get("x", 0)) + dx))
        o.set("y", num(float(o.get("y", 0)) + dy))
    tree.write(dst, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
