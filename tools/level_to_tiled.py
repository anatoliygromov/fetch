#!/usr/bin/env python3
"""Converts FETCH! levels to Tiled maps, and Tiled maps to the Lua file the game reads.

  python3 tools/level_to_tiled.py citypark [downtown ...]   level -> maps/<name>.tmx + its Lua export
  python3 tools/level_to_tiled.py --all                     the same for every level in riverwalk/levels.lua
  python3 tools/level_to_tiled.py --export maps/citypark.tmx [out.lua]
                                                            a Tiled map -> the Lua export the game loads
                                                            (what Tiled's File > Export does; default target:
                                                            the one stored in the map, riverwalk/level/tiled/)
  python3 tools/level_to_tiled.py --upgrade maps/*.tmx      older maps -> drag-safe fields (relx. / rely. / relxy.,
                                                            hints with a height as boxes), in place, and exports
                                                            them; the levels the game loads stay the same
  python3 tools/level_to_tiled.py --tileset                 (re)draws maps/terrain.png
  options: --out DIR (where the .tmx go, default maps/), --export-dir DIR (default riverwalk/level/tiled/)

A level today is riverwalk/level/<name>.map (terrain, 8 x 8 px cells) plus riverwalk/level/<name>.lua (the table L).
The Tiled map holds both: a tile layer "terrain" and object layers. riverwalk/tiled.lua turns the export back into
the same rows and the same table L. The rules (docs/tiled.md has them for designers):

  * Each object goes into the list L[<class>] (Tiled's Class field, called Type before Tiled 1.9); an empty class
    means the layer's name. A dotted class goes into a nested list: "magpie.perches" -> L.magpie.perches.
    start, ball, girl, cat, fox and exit are single objects (L.start = {...}), everything else is a list, in the
    order of the objects in the map.
  * A rectangle gives x0, x1, y0, y1 (x0 = left, y1 = bottom). Its property "box" can name other fields for its
    sides, in the order left,right,top,bottom ("-" or nothing: not used): bike zones "zoneX0,zoneX1", hints
    "x0,x1", hatches "1,2,3" (a list { x0, x1, y }). Zones with no top and bottom are drawn as bands above the map.
  * A point gives x and y.
  * The object's name is the field "name" (a property "name" wins, so name = "" survives the trip).
  * Every other custom property is copied as it is. A text property that starts with "{" is a Lua table, written
    the way the level files write it, e.g. call = "{ 600, 830 }".
  * Drag-safe fields (REL below): positions that belong to an object (a boat's from / to, a lift's fromY / toY, a
    goose's x0 / x1...) are stored as offsets from the object's own x and y: relx.<field>, rely.<field>,
    relxy.<field>. The loader adds the position back, so dragging the object moves them too. A hint with a height
    (minY, maxY) is a box in the map: its top edge is minY, its bottom edge maxY ("-" in box: that edge does not count).
  * Map properties are the level's other fields (time, art, scenery, intro...). A dotted name sets a nested field:
    "magpie.flee" -> L.magpie.flee. An empty list is kept as "{}", so it still exists.

The level table is read by running the level file in Lua: lua5.1, luajit or lua if one is installed, else LOVE.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = os.path.join(ROOT, "riverwalk")
LEVELS = os.path.join(GAME, "level")
MAPS = os.path.join(ROOT, "maps")
EXPORTS = os.path.join(LEVELS, "tiled")
DUMPER = os.path.join(ROOT, "tools", "tiled", "dump_level.lua")
CELL = 8

# terrain characters (world.lua): tile id in the tileset, colour, what it is
TERRAIN = [
    ("#", (92, 96, 112), "solid"),
    ("~", (70, 130, 200), "water"),
    ("/", (150, 120, 80), "slope up to the right"),
    ("\\", (150, 120, 80), "slope down to the right"),
]

# object layers, in the order they are stacked in Tiled (first = bottom), with their colour in Tiled
LAYERS = [
    ("props", "#ffa040"),
    ("zones", "#ff4060"),
    ("movers", "#40c0ff"),
    ("critters", "#c060ff"),
    ("lamps", "#ffe040"),
    ("bones", "#ffffff"),
    ("story", "#40ff80"),
]
# which layer a level field goes to (a field not named here gets a layer of its own)
FIELD_LAYER = {
    "props": "props", "pieces": "props", "passages": "props",
    "bikes": "zones", "hatches": "zones", "barrels": "zones", "secrets": "zones",
    "movers": "movers", "critters": "critters",
    "lamps": "lamps", "lights": "lamps", "bones": "bones",
    "start": "story", "ball": "story", "girl": "story", "cat": "story", "fox": "story", "exit": "story",
    "magpie.perches": "story", "fox.hideouts": "story", "hints": "story",
}
# single objects (riverwalk/tiled.lua knows the same list); any other class is a list
SINGLES = ["start", "ball", "girl", "cat", "fox", "exit"]
# lists whose items are plain arrays: which item index each side of the rectangle is
POSITIONAL = {"hatches": ["1", "2", "3"]}
# the fields riverwalk/tiled.lua sets itself
SKIP = {"map"}
# properties shown first in Tiled
FIRST = ["kind", "layer", "art", "label", "text", "btn", "need"]
# Drag-safe fields: positions that belong to an object are stored as offsets from the object's own x and y (a
# rectangle's top left corner, a point's pin), as the property relx.<field> (x), rely.<field> (y) or relxy.<field>
# (points: { x =, y = } or { x, y }, or a list of them). riverwalk/tiled.lua adds the object's position back.
# So dragging an object in Tiled moves everything that belongs to it. Per class: field -> axis.
REL = {
    "movers": {"from": "x", "to": "x", "call": "x", "rope": "x", "fromY": "y", "toY": "y", "winch": "xy"},
    "critters": {"x0": "x", "x1": "x"},             # a goose (a point): the stretch it walks
    "props": {"ax": "x", "ay": "y"},                # River Walk's pictures: their anchor
    "pieces": {"bx0": "x", "bx1": "x", "door": "y", "foot": "y"},  # a kiosk's booth, the kennel's doorway, the path
                                                    # a piece stands on (tall levels)
    "barrels": {"trigger": "x", "rest": "xy"},
    "bikes": {"endX": "x", "depot": "x"},           # (a band: x only; its minY is not used by the game)
}
REL_PREFIX = {"x": "relx.", "y": "rely.", "xy": "relxy."}
# hints with a height (minY, maxY: where her feet must be) are boxes in the map: top = minY, bottom = maxY
HEIGHT_BOX = {"hints": ("minY", "maxY")}


# ---------------------------------------------------------------------------------------------------- reading Lua
def lua_cmd():
    for exe in ("lua5.1", "luajit", "lua"):
        p = shutil.which(exe)
        if p:
            return [p]
    return None


def run_lua(script, args):
    """Runs a Lua script file with arguments (a plain Lua interpreter, or LOVE headless) and returns stdout."""
    cmd = lua_cmd()
    if cmd:
        return subprocess.run(cmd + [script] + args, check=True, capture_output=True, text=True).stdout
    love = shutil.which("love")
    mac = "/Applications/love.app/Contents/MacOS/love"
    if not love and os.path.exists(mac):
        love = mac
    if not love:
        sys.exit("level_to_tiled: needs lua5.1, luajit, lua or love on the PATH")
    runner = os.path.join(ROOT, "tools", "tiled", "love_runner")
    return subprocess.run([love, runner, script] + args, check=True, capture_output=True, text=True).stdout


def fix_keys(v):
    """JSON from dump_level.lua: '#<n>' keys were numeric keys in Lua."""
    if isinstance(v, dict):
        return {(int(k[1:]) if k.startswith("#") else k): fix_keys(x) for k, x in v.items()}
    if isinstance(v, list):
        return [fix_keys(x) for x in v]
    return v


def read_level(name):
    script = os.path.join(ROOT, "tools", "tiled", "dump_cli.lua")
    return fix_keys(json.loads(run_lua(script, [DUMPER, os.path.join(LEVELS, name + ".lua")])))


def read_rows(path):
    with open(path) as f:
        return [line.rstrip("\n") for line in f if line.strip("\n")]


# -------------------------------------------------------------------------------------------- relative positions
def shift(v, axis, bx, by):
    """v plus the object's position (bx, by); with -bx, -by: an absolute value as an offset. See REL."""
    if isinstance(v, bool) or not isinstance(v, (int, float, list, dict)):
        return v
    if isinstance(v, (int, float)):
        return v + (by if axis == "y" else bx)
    if isinstance(v, dict):
        out = dict(v)
        if axis == "xy":
            if "x" in v or "y" in v:
                if isinstance(v.get("x"), (int, float)):
                    out["x"] = v["x"] + bx
                if isinstance(v.get("y"), (int, float)):
                    out["y"] = v["y"] + by
                return out
            if isinstance(v.get(1), (int, float)):
                out[1] = v[1] + bx
                if isinstance(v.get(2), (int, float)):
                    out[2] = v[2] + by
                return out
        i = 1
        while i in v:
            out[i] = shift(v[i], axis, bx, by)
            i += 1
        return out
    if axis == "xy" and v and isinstance(v[0], (int, float)) and not isinstance(v[0], bool):
        return [v[0] + bx] + ([v[1] + by] if len(v) > 1 else []) + v[2:]
    return [shift(x, axis, bx, by) for x in v]


def make_relative(cls, d, x, y, band):
    """Moves the fields of REL[cls] in d (an object's custom properties) to relx. / rely. / relxy. offsets."""
    for field, axis in REL.get(cls, {}).items():
        if field in d and not (band and axis != "x"):
            d[REL_PREFIX[axis] + field] = shift(d.pop(field), axis, -x, -y)


# --------------------------------------------------------------------------------------------------- Lua literals
def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def lua_num(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer()):
        return str(int(v))
    return repr(v)


IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def lua_literal(v):
    """A value as Lua source, the way the level files write it: { 600, 830 }, { x = 1, y = 2 }."""
    if isinstance(v, str):
        return lua_str(v)
    if isinstance(v, (bool, int, float)):
        return lua_num(v)
    if isinstance(v, list):
        return "{ " + ", ".join(lua_literal(x) for x in v) + " }" if v else "{}"
    if isinstance(v, dict):
        parts = []
        for k in sorted(v, key=lambda k: (isinstance(k, str), str(k))):
            key = k if isinstance(k, str) and IDENT.match(k) else "[%s]" % (lua_str(k) if isinstance(k, str) else k)
            parts.append("%s = %s" % (key, lua_literal(v[k])))
        return "{ " + ", ".join(parts) + " }" if parts else "{}"
    raise TypeError(v)


def prop(name, v):
    """A Tiled custom property (name, type, value text)."""
    if isinstance(v, bool):
        return (name, "bool", "true" if v else "false")
    if isinstance(v, int):
        return (name, "int", str(v))
    if isinstance(v, float):
        return (name, "int", str(int(v))) if v.is_integer() else (name, "float", repr(v))
    if isinstance(v, str):
        return (name, "string", v)
    return (name, "string", lua_literal(v))


def order_keys(keys):
    return sorted(keys, key=lambda k: (FIRST.index(k) if k in FIRST else len(FIRST), str(k)))


# ----------------------------------------------------------------------------------------------- level -> objects
def is_geo(d):
    return isinstance(d, dict) and (("x" in d and "y" in d) or ("x0" in d and "x1" in d)
                                    or ("zoneX0" in d and "zoneX1" in d))


def to_object(item, cls, map_h, positional=None):
    """One level item -> a Tiled object dict: name, cls, shape, x, y, w, h, props (list of (name, type, value))."""
    o = {"name": "", "cls": cls, "props": []}
    if positional:
        vals = [item[int(k) - 1] for k in positional]
        rest = {i + 1: v for i, v in enumerate(item) if str(i + 1) not in positional}
        x0, x1, y0 = vals[0], vals[1], vals[2]
        o.update(shape="rectangle", x=x0, y=y0, w=x1 - x0, h=max(8, map_h - y0))
        o["props"].append(("box", "string", ",".join(positional)))
        d = rest
    else:
        d = dict(item)
        if "x" in d and "y" in d:
            o.update(shape="point", x=d.pop("x"), y=d.pop("y"), w=0, h=0)
        else:
            kx0 = "x0" if "x0" in d else "zoneX0"
            kx1 = "x1" if "x1" in d else "zoneX1"
            x0, x1 = d.pop(kx0), d.pop(kx1)
            side = [kx0, kx1, "-", "-"]
            hb = HEIGHT_BOX.get(cls)
            if hb and "y0" not in d and (hb[0] in d or hb[1] in d):   # a hint with a height: a box in the map
                side[2] = hb[0] if hb[0] in d else "-"
                side[3] = hb[1] if hb[1] in d else "-"
                y0 = d.pop(hb[0]) if hb[0] in d else 0       # no minY: from the top of the map
                y1 = d.pop(hb[1]) if hb[1] in d else map_h   # no maxY: to the bottom
            elif "y0" in d:
                y0 = d.pop("y0")
                side[2] = "y0"
                if "y1" in d:
                    y1 = d.pop("y1")
                    side[3] = "y1"
                else:
                    y1 = y0 + 8
            else:                                   # a zone with no height: a band above the map (level_to_layers)
                y0, y1 = 0, 8
                o["band"] = True
            o.update(shape="rectangle", x=x0, y=y0, w=x1 - x0, h=y1 - y0)
            while side and side[-1] == "-":
                side.pop()
            box = ",".join(side)
            if box != "x0,x1,y0,y1":
                o["props"].append(("box", "string", box))
        if "name" in d:
            n = d.pop("name")
            if n:
                o["name"] = n
            else:
                o["props"].append(prop("name", n))
        make_relative(cls, d, o["x"], o["y"], o.get("band"))
    for k in order_keys(d.keys()):
        o["props"].append(prop(str(k), d[k]))
    return o


def level_to_layers(L, map_h):
    """Splits the level table into object layers and map properties."""
    layers = {n: [] for n, _ in LAYERS}
    extra = []                                   # layers for fields this script does not know
    mprops = []

    def add(field, items, cls, positional=None):
        lname = FIELD_LAYER.get(field)
        if lname is None:
            lname = field.replace(".", "_")
            if lname not in layers:
                layers[lname] = []
                extra.append(lname)
        for it in items:
            layers[lname].append(to_object(it, cls, map_h, positional))

    known = [f for f in FIELD_LAYER if "." not in f and f != "hints"] + ["magpie", "hints"]
    for key in sorted(L, key=lambda k: (known.index(k) if k in known else len(known), k)):
        v = L[key]
        if key in SKIP:
            continue
        if isinstance(v, list) and v and key in POSITIONAL:
            add(key, v, key, POSITIONAL[key])
        elif isinstance(v, list) and v and all(is_geo(x) for x in v):
            add(key, v, key)
        elif isinstance(v, dict) and is_geo(v):
            single = {k: x for k, x in v.items() if not (isinstance(x, list) and x and all(is_geo(y) for y in x))}
            add(key, [single], key)
            if key not in SINGLES:
                mprops.append(("singles", "string", key))
            for k, x in v.items():
                if k not in single:
                    add(key + "." + k, x, key + "." + k)
        elif isinstance(v, dict):
            for k in order_keys(v.keys()):
                x = v[k]
                if isinstance(x, list) and x and all(is_geo(y) for y in x):
                    add(key + "." + k, x, key + "." + k)
                else:
                    mprops.append(prop(key + "." + str(k), x))
        else:
            mprops.append(prop(key, v))
    # several "singles" entries -> one
    singles = [p[2] for p in mprops if p[0] == "singles"]
    mprops = [p for p in mprops if p[0] != "singles"]
    if singles:
        mprops.append(("singles", "string", ",".join(singles)))
    order = [n for n, _ in LAYERS] + extra
    banded = [o for n in order for o in layers[n] if o.get("band")]
    for i, o in enumerate(banded):                  # stacked above the map, the first one on top
        o["y"] = -10 * (len(banded) - i)
    colors = dict(LAYERS)
    return [(n, colors.get(n, "#a0a0a0"), layers[n]) for n in order], mprops


# ------------------------------------------------------------------------------------------------------ TMX writer
def props_xml(props, indent):
    if not props:
        return ""
    pad = " " * indent
    out = [pad + "<properties>"]
    for n, t, v in props:
        ta = "" if t == "string" else ' type="%s"' % t
        out.append('%s <property name=%s%s value=%s/>' % (pad, quoteattr(n), ta, quoteattr(v)))
    out.append(pad + "</properties>")
    return "\n".join(out) + "\n"


def export_target(name):
    return os.path.relpath(os.path.join(EXPORTS, name + ".lua"), MAPS)


def write_tmx(path, name, L, rows):
    cols, nrows = len(rows[0]), len(rows)
    for r in rows:
        if len(r) != cols:
            sys.exit("%s: terrain rows have different lengths" % name)
    gid = {ch: i + 1 for i, (ch, _, _) in enumerate(TERRAIN)}
    layers, mprops = level_to_layers(L, nrows * CELL)
    nid = 1
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<map version="1.8" tiledversion="1.8.2" orientation="orthogonal" renderorder="right-down" '
           'width="%d" height="%d" tilewidth="%d" tileheight="%d" infinite="0" backgroundcolor="#20242c" '
           'nextlayerid="%d" nextobjectid="%d">'
           % (cols, nrows, CELL, CELL, len(layers) + 2, 1 + sum(len(o) for _, _, o in layers)),
           ' <editorsettings>',
           '  <export target=%s format="lua"/>' % quoteattr(export_target(name)),
           ' </editorsettings>']
    out.append(props_xml(mprops, 1).rstrip("\n")) if mprops else None
    out.append(' <tileset firstgid="1" name="terrain" tilewidth="8" tileheight="8" tilecount="%d" columns="%d">'
               % (len(TERRAIN), len(TERRAIN)))
    out.append('  <image source="terrain.png" width="%d" height="8"/>' % (CELL * len(TERRAIN)))
    for i, (ch, _, what) in enumerate(TERRAIN):
        out.append('  <tile id="%d">' % i)
        out.append(props_xml([("char", "string", ch), ("what", "string", what)], 3).rstrip("\n"))
        out.append('  </tile>')
    out.append(' </tileset>')
    out.append(' <layer id="1" name="terrain" width="%d" height="%d">' % (cols, nrows))
    out.append('  <data encoding="csv">')
    lines = []
    for r in rows:
        cells = []
        for ch in r:
            if ch == ".":
                cells.append("0")
            elif ch in gid:
                cells.append(str(gid[ch]))
            else:
                sys.exit("%s: unknown terrain character %r (add it to TERRAIN)" % (name, ch))
        lines.append(",".join(cells))
    out.append(",\n".join(lines))
    out.append('</data>')
    out.append(' </layer>')
    for li, (lname, color, objs) in enumerate(layers):
        out.append(' <objectgroup id="%d" name=%s color="%s" draworder="index">' % (li + 2, quoteattr(lname), color))
        for o in objs:
            attrs = 'id="%d"' % nid
            nid += 1
            if o["name"]:
                attrs += " name=%s" % quoteattr(o["name"])
            if o["cls"]:
                attrs += " type=%s" % quoteattr(o["cls"])
            attrs += ' x="%s" y="%s"' % (lua_num(o["x"]), lua_num(o["y"]))
            if o["shape"] == "rectangle":
                attrs += ' width="%s" height="%s"' % (lua_num(o["w"]), lua_num(o["h"]))
            body = props_xml(o["props"], 3)
            if o["shape"] == "point":
                body += "   <point/>\n"
            if body:
                out.append("  <object %s>\n%s  </object>" % (attrs, body))
            else:
                out.append("  <object %s/>" % attrs)
        out.append(' </objectgroup>')
    out.append('</map>')
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


# ------------------------------------------------------------------------------------- TMX -> Lua export (Tiled's)
def tmx_value(p):
    t, v = p.get("type", "string"), p.get("value")
    if v is None:
        v = p.text or ""
    if t == "bool":
        return v == "true"
    if t == "int":
        return int(v)
    if t == "float":
        f = float(v)
        return int(f) if f.is_integer() else f
    return v


def tmx_props(el):
    ps = el.find("properties")
    return [] if ps is None else [(p.get("name"), tmx_value(p)) for p in ps.findall("property")]


def num(s, default=0):
    if s is None:
        return default
    f = float(s)
    return int(f) if f.is_integer() else f


class Lua:
    """Writes a nested structure as a Lua table, in the layout Tiled's Lua export uses."""

    def __init__(self):
        self.out = []

    def val(self, v, ind):
        if isinstance(v, dict):
            self.out.append("{\n")
            for k, x in v.items():
                self.out.append("  " * (ind + 1) + ("%s = " % k if IDENT.match(k) else "[%s] = " % lua_str(k)))
                self.val(x, ind + 1)
                self.out.append(",\n")
            self.out.append("  " * ind + "}")
        elif isinstance(v, list):
            self.out.append("{\n")
            for x in v:
                self.out.append("  " * (ind + 1))
                self.val(x, ind + 1)
                self.out.append(",\n")
            self.out.append("  " * ind + "}")
        elif isinstance(v, Props):
            if not v.items:
                self.out.append("{}")
                return
            self.out.append("{\n")
            for k, x in v.items:
                self.out.append("  " * (ind + 1) + "[%s] = %s,\n" % (lua_str(k), lua_literal(x)))
            self.out.append("  " * ind + "}")
        elif isinstance(v, Raw):
            self.out.append(v.text)
        else:
            self.out.append(lua_literal(v))


class Props:
    def __init__(self, items):
        self.items = items


class Raw:
    def __init__(self, text):
        self.text = text


def tmx_to_lua(tmx_path):
    root = ET.parse(tmx_path).getroot()
    if root.get("infinite") == "1":
        sys.exit("%s: the map is infinite; make it a fixed size (Map > Map Properties > Infinite off)" % tmx_path)
    m = {"version": root.get("version", "1.8"), "luaversion": "5.1", "tiledversion": root.get("tiledversion", ""),
         "class": "", "orientation": root.get("orientation"), "renderorder": root.get("renderorder", "right-down"),
         "width": int(root.get("width")), "height": int(root.get("height")),
         "tilewidth": int(root.get("tilewidth")), "tileheight": int(root.get("tileheight")),
         "nextlayerid": int(root.get("nextlayerid", 1)), "nextobjectid": int(root.get("nextobjectid", 1)),
         "properties": Props(tmx_props(root)), "tilesets": [], "layers": []}
    for ts in root.findall("tileset"):
        if ts.get("source"):
            sys.exit("%s: external tilesets are not supported, embed it (Map > Embed Tileset)" % tmx_path)
        tiles = [{"id": int(t.get("id")), "properties": Props(tmx_props(t))} for t in ts.findall("tile")]
        m["tilesets"].append({"name": ts.get("name"), "firstgid": int(ts.get("firstgid")),
                              "tilewidth": int(ts.get("tilewidth")), "tileheight": int(ts.get("tileheight")),
                              "tilecount": int(ts.get("tilecount", 0)), "properties": Props(tmx_props(ts)),
                              "tiles": tiles})
    for el in root:
        if el.tag == "layer":
            data = el.find("data")
            if data.get("encoding") != "csv":
                sys.exit("%s: tile layer data must be CSV (Map > Map Properties > Tile Layer Format)" % tmx_path)
            w, h = int(el.get("width")), int(el.get("height"))
            cells = [c.strip() for c in data.text.replace("\n", "").split(",") if c.strip()]
            rows = [", ".join(cells[r * w:(r + 1) * w]) for r in range(h)]
            m["layers"].append({"type": "tilelayer", "x": 0, "y": 0, "width": w, "height": h,
                                "id": int(el.get("id")), "name": el.get("name"),
                                "visible": el.get("visible", "1") != "0", "opacity": 1, "offsetx": 0, "offsety": 0,
                                "parallaxx": 1, "parallaxy": 1, "properties": Props(tmx_props(el)),
                                "encoding": "lua",
                                "data": Raw("{\n        " + ",\n        ".join(rows) + "\n      }")})
        elif el.tag == "objectgroup":
            objs = []
            for o in el.findall("object"):
                shape = "rectangle"
                for s in ("point", "ellipse", "polygon", "polyline", "text"):
                    if o.find(s) is not None:
                        shape = s
                objs.append({"id": int(o.get("id")), "name": o.get("name", ""),
                             "type": o.get("type", o.get("class", "")), "shape": shape,
                             "x": num(o.get("x")), "y": num(o.get("y")),
                             "width": num(o.get("width")), "height": num(o.get("height")),
                             "rotation": num(o.get("rotation")), "visible": o.get("visible", "1") != "0",
                             "properties": Props(tmx_props(o))})
            m["layers"].append({"type": "objectgroup", "draworder": el.get("draworder", "topdown"),
                                "id": int(el.get("id")), "name": el.get("name"),
                                "visible": el.get("visible", "1") != "0", "opacity": 1, "offsetx": 0, "offsety": 0,
                                "parallaxx": 1, "parallaxy": 1, "properties": Props(tmx_props(el)),
                                "objects": objs})
    w = Lua()
    w.out.append("return ")
    w.val(m, 0)
    return "".join(w.out) + "\n"


def export(tmx_path, out=None):
    if out is None:
        root = ET.parse(tmx_path).getroot()
        t = root.find("editorsettings/export")
        if t is None:
            sys.exit("%s has no export target; give one: --export map.tmx out.lua" % tmx_path)
        out = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(tmx_path)), t.get("target")))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as f:
        f.write(tmx_to_lua(tmx_path))
    return out


# ----------------------------------------------------------------------------------------------------- the tileset
def write_tileset(path):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (CELL * len(TERRAIN), CELL), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (ch, col, _) in enumerate(TERRAIN):
        x = i * CELL
        light = tuple(min(255, c + 50) for c in col)
        if ch == "/":
            d.polygon([(x, 7), (x + 7, 0), (x + 7, 7)], fill=col + (255,))
            d.line([(x, 7), (x + 7, 0)], fill=light + (255,))
        elif ch == "\\":
            d.polygon([(x, 0), (x + 7, 7), (x, 7)], fill=col + (255,))
            d.line([(x, 0), (x + 7, 7)], fill=light + (255,))
        else:
            d.rectangle([x, 0, x + 7, 7], fill=col + (255,))
            d.line([(x, 0), (x + 7, 0)], fill=light + (255,))
            if ch == "~":
                d.point([(x + 1, 3), (x + 2, 2), (x + 3, 3), (x + 5, 3), (x + 6, 2)], fill=(200, 230, 255, 255))
            else:
                d.point([(x + 2, 3), (x + 5, 5)], fill=light + (255,))
    im.save(path)


# --------------------------------------------------------------------------- upgrade: an older map made drag-safe
TOKEN = re.compile(r'\s*(?:(-?\d+\.?\d*(?:[eE][-+]?\d+)?)|("(?:[^"\\]|\\.)*")|([A-Za-z_][A-Za-z0-9_]*)|(.))')


def parse_lua(text):
    """A Lua table literal as the level files write them ({ 600, 830 }, { x = 1, y = 2 }, nested) -> list / dict."""
    toks = []
    pos = 0
    text = text.strip()
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        n, st, ident, ch = m.groups()
        if n is not None:
            toks.append(("v", int(n) if re.match(r"^-?\d+$", n) else float(n)))
        elif st is not None:
            toks.append(("v", json.loads(st)))
        elif ident is not None:
            toks.append(("v", {"true": True, "false": False}.get(ident, ident)) if ident in ("true", "false")
                        else ("id", ident))
        elif ch.strip():
            toks.append(("p", ch))
    i = 0

    def value():
        nonlocal i
        kind, v = toks[i]
        if kind == "p" and v == "{":
            i += 1
            d, n = {}, 0
            while not (toks[i] == ("p", "}")):
                if toks[i][0] == "id" and i + 1 < len(toks) and toks[i + 1] == ("p", "="):
                    k = toks[i][1]
                    i += 2
                    d[k] = value()
                elif toks[i] == ("p", "["):
                    i += 1
                    k = value()
                    i += 2                          # ] =
                    d[k] = value()
                else:
                    n += 1
                    d[n] = value()
                if toks[i] == ("p", ","):
                    i += 1
            i += 1
            if d and all(isinstance(k, int) for k in d) and sorted(d) == list(range(1, len(d) + 1)):
                return [d[k] for k in range(1, len(d) + 1)]
            return d if d else []
        i += 1
        return v
    return value()


def box_sides(props):
    b = props.get("box")
    return [s.strip() for s in b.get("value", "").split(",")] if b is not None else ["x0", "x1", "y0", "y1"]


def remove_child(parent, el):
    kids = list(parent)
    i = kids.index(el)
    if i > 0 and i == len(kids) - 1:
        kids[i - 1].tail = el.tail                  # keep the indentation of the closing tag
    parent.remove(el)


def upgrade_tmx(src, dst):
    """Rewrites an older Tiled map with the drag-safe fields (REL, HEIGHT_BOX); everything else stays as it is
    (notes, layers, object ids). The level the game loads from it is the same. Returns how many fields moved."""
    tree = ET.parse(src)
    root = tree.getroot()
    map_h = int(root.get("height")) * int(root.get("tileheight"))
    moved = 0
    for og in root.iter("objectgroup"):
        lname = og.get("name", "")
        if lname.startswith("#"):
            continue
        for o in og.findall("object"):
            cls = o.get("type") or o.get("class") or lname
            if cls.startswith("#") or o.find("text") is not None:
                continue
            pel = o.find("properties")
            if pel is None:
                continue
            props = {p.get("name"): p for p in pel.findall("property")}
            point = o.find("point") is not None
            sides = box_sides(props) + ["-"] * 4
            band = not point and all(s in ("-", "") for s in sides[2:4])
            hb = HEIGHT_BOX.get(cls)
            if hb and band and (hb[0] in props or hb[1] in props):
                top = tmx_value(props[hb[0]]) if hb[0] in props else 0
                bottom = tmx_value(props[hb[1]]) if hb[1] in props else map_h
                side = sides[:2] + [hb[0] if hb[0] in props else "-", hb[1] if hb[1] in props else "-"]
                while side[-1] == "-":
                    side.pop()
                o.set("y", lua_num(top))
                o.set("height", lua_num(bottom - top))
                for f in hb:
                    if f in props:
                        remove_child(pel, props.pop(f))
                        moved += 1
                if "box" in props:
                    props["box"].set("value", ",".join(side))
                band = False
            x, y = round(float(o.get("x", 0))), round(float(o.get("y", 0)))
            for field, axis in REL.get(cls, {}).items():
                if field not in props or (band and axis != "x"):
                    continue
                p = props.pop(field)
                v = tmx_value(p)
                if isinstance(v, str) and v.lstrip().startswith("{"):
                    v = parse_lua(v)
                n, t, text = prop(REL_PREFIX[axis] + field, shift(v, axis, -x, -y))
                p.set("name", n)
                p.set("value", text)
                if t == "string":
                    p.attrib.pop("type", None)
                else:
                    p.set("type", t)
                moved += 1
    body = ET.tostring(root, encoding="unicode").replace(" />", "/>")
    with open(dst, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n")
    return moved


def level_names():
    with open(os.path.join(GAME, "levels.lua")) as f:
        return re.findall(r'name\s*=\s*"([a-z0-9_]+)"', f.read())


def convert(name, out_dir, export_dir):
    L = read_level(name)
    rows = L.pop("rows", None)                      # a level drawn in Tiled only: its rows come from its export
    mapfile = os.path.join(LEVELS, name + ".map")
    if os.path.exists(mapfile) or not rows:
        rows = read_rows(mapfile)
    os.makedirs(out_dir, exist_ok=True)
    tileset = os.path.join(out_dir, "terrain.png")
    if not os.path.exists(tileset):
        write_tileset(tileset)
    tmx = os.path.join(out_dir, name + ".tmx")
    write_tmx(tmx, name, L, rows)
    lua = export(tmx, os.path.join(export_dir, name + ".lua"))
    print("%s -> %s, %s" % (name, os.path.relpath(tmx, ROOT), os.path.relpath(lua, ROOT)))


def main(argv):
    out_dir, export_dir = MAPS, EXPORTS
    if "--out" in argv:
        i = argv.index("--out")
        out_dir = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    if "--export-dir" in argv:
        i = argv.index("--export-dir")
        export_dir = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    if argv[0] == "--export":
        print("exported", export(argv[1], argv[2] if len(argv) > 2 else None))
        return
    if argv[0] == "--upgrade":
        # in place (and its export, to the target stored in the map), or into --out / --export-dir
        for src in argv[1:]:
            name = os.path.splitext(os.path.basename(src))[0]
            dst = os.path.join(out_dir, os.path.basename(src)) if out_dir != MAPS else src
            if dst != src:
                os.makedirs(out_dir, exist_ok=True)
                ts = os.path.join(os.path.dirname(os.path.abspath(src)), "terrain.png")
                if os.path.exists(ts) and not os.path.exists(os.path.join(out_dir, "terrain.png")):
                    shutil.copy(ts, out_dir)
            n = upgrade_tmx(src, dst)
            has_target = ET.parse(dst).getroot().find("editorsettings/export") is not None
            if export_dir != EXPORTS:
                lua = export(dst, os.path.join(export_dir, name + ".lua"))
            elif has_target and dst == src:
                lua = export(dst)
            else:
                lua = None
            print("%s: %d fields made drag-safe%s" % (dst, n, ", exported " + lua if lua else ""))
        return
    if argv[0] == "--tileset":
        write_tileset(os.path.join(out_dir, "terrain.png"))
        return
    names = level_names() if argv[0] == "--all" else argv
    for n in names:
        convert(n, out_dir, export_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
