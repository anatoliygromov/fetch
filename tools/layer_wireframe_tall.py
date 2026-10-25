#!/usr/bin/env python3
"""Layer wireframe of a tall art level, screen by screen and tier by tier (25 Oct 2026, City Park layer plan).

The tall version of tools/layer_wireframe.py (branch art/layer-plans, which reads the flat level files). This one
reads a Tiled export, riverwalk/level/tiled/<level>.lua (what the game loads, through tiled.lua), and places every
piece the way the park art code does (scene.lua: Sc.drawFarArt, Sc.drawTreetops and its tier(), Sc.drawPropArt,
stage.lua St:draw), as flat colour boxes:

  red      usable: she stands on it, crawls under it, jumps over it (obstacles, perches, ledges, the duck boat)
  orange   moving: the duck boat's run, geese, the leaf carts' zones
  yellow   pickup, goal or signal: bones, the ball, Mia, the magpie's perches, lamp posts, leaf piles
  beige    decoration behind her (back layer)
  purple   decoration standing on her line by mistake (none found means none drawn)
  dark     the front frame (1.3 scroll)
  far      sky, clouds, far city, tree line, mid trees, the pond: in their own light colours

Each screen is drawn at each camera height the sweep uses (tests_look.lua: the bottom of the world, camera y 144,
the low road; and the top, camera y 0, the high road), with the far layers moved as Vc.parallax moves them
(far 0.3, mid 0.6 of the camera's rise). Pepper stands where the sweep puts her: x = camera + 140, on the highest
floor 60 to 236 px down the screen.

  python3 -I tools/layer_wireframe_tall.py citypark_tall OUT.png [--cols 3] [--scale 2] [--report OUT.json]
  python3 -I tools/layer_wireframe_tall.py downtown_tall OUT.png --tiers 120,240 [--report OUT.json]

City Park's art (L.art = "park") is placed by classify(); Downtown's town art (L.art = "town") by classify_town(),
after scene.lua's town branch and arthooks.lua (the roof kit, the tall fronts, the cargo bikes, the back lane's tram,
the far spire), with the town's far layers (far roofs 0.25, old town facades 0.5) drawn as their art's silhouettes.
--tiers Y1,Y2 picks the camera heights (default: the top and the bottom of the world). Downtown's roofs are seen from
camera y 64 to 112, so its plan uses --tiers 120,240 (the sweep's middle and bottom heights). City Park's output is
unchanged by the town code.

--report writes the measured numbers per screen (usable pieces per road, back pieces, front pieces, empty path,
bones, lamps, perches, sizes in px) that the layer plan quotes. Nothing in the game is read but the level export
and the art files' sizes; nothing is written but OUT.png and the report.
"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "riverwalk/art/scene")

# ------------------------------------------------------------------------------------------------------------------
# the Tiled Lua export, read as data (a small reader for Lua table literals: strings, numbers, booleans, tables)
TOK = re.compile(r'\s+|--[^\n]*|"(?:\\.|[^"\\])*"|\[\s*"(?:\\.|[^"\\])*"\s*\]|[{}=,]|-?\d+(?:\.\d+)?(?:e-?\d+)?|[A-Za-z_]\w*')


def lua_table(text):
    text = text[text.index("{"):]
    toks = [t for t in TOK.findall(text) if t.strip() and not t.startswith("--")]
    pos = [0]

    def unq(s):
        return bytes(s[1:-1], "utf-8").decode("unicode_escape")

    def val():
        t = toks[pos[0]]
        pos[0] += 1
        if t == "{":
            arr, obj = [], {}
            while toks[pos[0]] != "}":
                t2 = toks[pos[0]]
                if pos[0] + 1 < len(toks) and toks[pos[0] + 1] == "=" and (t2[0].isalpha() or t2[0] == "_" or t2.startswith("[")):
                    k = unq(t2.strip("[] \t")) if t2.startswith("[") else t2
                    pos[0] += 2
                    obj[k] = val()
                else:
                    arr.append(val())
                if toks[pos[0]] == ",":
                    pos[0] += 1
            pos[0] += 1
            return obj if obj else arr
        if t.startswith('"'):
            return unq(t)
        if t in ("true", "false"):
            return t == "true"
        if t == "nil":
            return None
        return float(t) if "." in t or "e" in t else int(t)
    return val()


def literal(s):
    """a property written as a Lua table ("{ 600, 830 }")"""
    return lua_table(s) if isinstance(s, str) and s.strip().startswith("{") else s


def shift(v, axis, bx, by):
    if isinstance(v, (int, float)):
        return v + (by if axis == "y" else bx)
    if isinstance(v, list):
        return [shift(x, axis, bx, by) for x in v]
    if isinstance(v, dict):
        out = dict(v)
        if "x" in v or "y" in v:
            out["x"] = v.get("x", 0) + bx
            out["y"] = v.get("y", 0) + by
        return out
    return v


def load(level):
    """the level as tiled.lua makes it: L (classes as lists) and the terrain rows (8 px cells)"""
    m = lua_table(open(os.path.join(ROOT, f"riverwalk/level/tiled/{level}.lua")).read())
    L = {"props_": m.get("properties", {})}
    for k, v in m.get("properties", {}).items():
        L[k] = literal(v)
    chars = {}
    for ts in m.get("tilesets", []):
        for t in ts.get("tiles", []):
            c = (t.get("properties") or {}).get("char")
            if c:
                chars[ts["firstgid"] + t["id"]] = c
    rows = []
    for layer in m["layers"]:
        if layer.get("type") == "tilelayer" and layer.get("name") == "terrain":
            w, h, d = layer["width"], layer["height"], layer["data"]
            rows = ["".join(chars.get(d[r * w + c] % 536870912, ".") if d[r * w + c] else "." for c in range(w)) for r in range(h)]
    for layer in m["layers"]:
        if layer.get("type") != "objectgroup" or layer["name"].startswith("#"):
            continue
        for o in layer.get("objects", []):
            cls = o.get("type") or o.get("class") or layer["name"]
            if o.get("shape") == "text" or cls.startswith("#"):
                continue
            p = o.get("properties") or {}
            it = {}
            bx, by = round(o["x"]), round(o["y"])
            if o.get("shape") == "point":
                it["x"], it["y"] = bx, by
            else:
                sides = [round(o["x"]), round(o["x"] + o["width"]), round(o["y"]), round(o["y"] + o["height"])]
                for i, s in enumerate((p.get("box") or "x0,x1,y0,y1").split(",")[:4]):
                    s = s.strip()
                    if s not in ("-", ""):
                        it[s] = sides[i]
            if o.get("name"):
                it["name"] = o["name"]
            rel = []
            for k, v in p.items():
                mm = re.match(r"^(relx|rely|relxy)\.(.+)$", k)
                if mm:
                    rel.append((mm.group(2), {"relx": "x", "rely": "y", "relxy": "xy"}[mm.group(1)], v))
                elif k != "box":
                    it[k] = literal(v)
            for f, ax, v in rel:
                it[f] = shift(literal(v), ax, bx, by)
            if cls in ("start", "ball", "girl", "cat", "fox", "exit"):
                L[cls] = it
            else:
                t = L
                segs = cls.split(".")
                for s in segs[:-1]:
                    t = t.setdefault(s, {})
                t.setdefault(segs[-1], []).append(it)
    return L, rows


# ------------------------------------------------------------------------------------------------------------------
# the park art code's rules, in Python (scene.lua; line numbers on prod/integrate c1c37a4)
def art_size(name):
    im = Image.open(os.path.join(ART, name + ".png"))
    return im.size


def frame_bbox(name, fw, fh, i=0):
    """the opaque box of frame i of a sheet of fw x fh cells"""
    im = Image.open(os.path.join(ART, name + ".png")).convert("RGBA")
    return im.crop((i * fw, 0, i * fw + fw, fh)).getbbox()


def tier(props, foot):
    """scene.lua tier(): which props are the treetop tier, and as what"""
    TIER_NAMES = {"TREETOP WALK": "walk", "ALDER WALK": "walk", "ARBOUR": "slat", "PLAY TOWER": "deck", "LOW BOUGH": "lowbough"}
    role = {}
    named = [p for p in props if p.get("layer") != "front" and p.get("kind") != "decor" and p["y1"] <= foot - 90 and p.get("name")]
    last = None
    ledges = []
    for i, p in enumerate(props):
        if p.get("layer") == "front":
            continue
        if p.get("kind") != "decor" and p["y1"] <= foot - 90:
            who = p if p.get("name") else next((q for q in named if q["x0"] < p["x1"] and q["x1"] > p["x0"]), None) or last
            if p.get("name"):
                last = p
            role[i] = TIER_NAMES.get(who["name"], "branch") if who else "branch"
            role[("who", i)] = who["name"] if who else ""
            ledges.append(i)
        elif p.get("kind") == "decor" and p["y0"] <= foot - 100:
            if p.get("name") == "NEST":
                role[i] = "nest"
            elif p.get("name") == "BIG OAK":
                role[i] = "trunk"
            elif p["x1"] - p["x0"] <= 12 and p["y1"] >= foot - 40:
                role[i] = "trunk"
            elif p["x1"] - p["x0"] >= 48 and p["y1"] <= foot - 100:
                role[i] = "canopy"
            else:
                role[i] = "skip"
    for i, r in list(role.items()):                       # a trunk under a deck or a slat is its post
        if isinstance(i, tuple):
            continue
        p = props[i]
        if r == "trunk" and p.get("name") != "BIG OAK":
            post = None
            for j in ledges:
                q = props[j]
                if role[j] in ("deck", "slat") and q["x0"] < p["x1"] and q["x1"] > p["x0"] and q["y1"] <= p["y0"] + 2:
                    post = role[j]
            for q in props:
                if p["y1"] < foot and q.get("kind") == "oneway" and q["x0"] < p["x1"] and q["x1"] > p["x0"] and q["y0"] > p["y0"] and q["y1"] <= p["y1"]:
                    post = "deck"
            if post:
                role[i] = "towerpost" if post == "deck" else "skip"
    return role


def classify(L, rows):
    """every drawn thing: (kind, road, box in world px, label). kind: usable, moving, pickup, signal, back, front, misplaced"""
    foot = L.get("foot", 184)
    props = L.get("props", [])
    role = tier(props, foot)
    out = []
    owner_names = [p for p in props if p.get("name") and p.get("layer") != "front"]

    def owner(p):
        cx = (p["x0"] + p["x1"]) / 2
        best, bd = None, 1e9
        for q in owner_names:
            d = max(0, q["x0"] - cx, cx - q["x1"])
            if d < bd:
                best, bd = q, d
        return best

    d = foot - 184                                            # dy(): the art's fixed lines follow the path line
    sizes = {n: art_size(n) for n in ("park_gate", "park_oak", "park_swings", "park_willow", "park_willow_tall", "park_slide",
                                      "park_hedge", "park_log", "park_table_front", "park_stone", "park_frame",
                                      "park_hollowlog", "park_leaves", "park_bush", "park_boat_front", "bench", "bin", "lamp_post")}
    wl = next((p for p in props if p.get("name") == "WILLOWS"), None)
    crowns = [p for p in props if wl and p.get("kind") == "decor" and p.get("layer") == "back" and
              (p is wl or (not p.get("name") and p["x1"] - p["x0"] == wl["x1"] - wl["x0"] and p["y1"] - p["y0"] == wl["y1"] - wl["y0"]
                           and abs(p["x0"] - wl["x0"]) < 200))]
    for i, p in enumerate(props):
        n = p.get("name") or ""
        road = "high" if p["y1"] <= foot - 90 else "low"
        box = [p["x0"], p["y0"], p["x1"], p["y1"]]
        if p.get("layer") == "front":
            w, h = sizes["park_bush"]
            cx = (p["x0"] + p["x1"]) / 2
            out.append(dict(kind="front", road="low", box=[cx - w // 2, max(221 + d, p["y0"]), cx - w // 2 + w, max(221 + d, p["y0"]) + h],
                            label="bush", scroll=1.3, mid=cx))
            continue
        r = role.get(i)
        if r == "towerpost":
            out.append(dict(kind="back", road="both", box=[p["x0"], p["y0"], p["x1"], foot], label="post", role="leg"))
            continue
        if r in ("trunk", "canopy", "nest"):
            lab = {"trunk": "BIG OAK trunk" if n == "BIG OAK" else "trunk", "canopy": "canopy", "towerpost": "post", "nest": "NEST"}[r]
            if r == "trunk":
                box = [p["x0"], p["y0"], p["x1"], foot]
            out.append(dict(kind="back", road="high" if r in ("canopy", "nest") else "both", box=box, label=lab, role=r, i=i))
            continue
        if r == "skip":
            continue
        if r == "walk":                                       # drawWalkLegs: a timber every 60 px, to the ground or the bed
            for lx in range(p["x0"] + 6, p["x1"] - 10 + 1, 60):
                wet = any(rows[rr][lx // 8] == "~" for rr in range(len(rows)))
                out.append(dict(kind="back", road="both", box=[lx - 1, p["y1"], lx + 5, len(rows) * 8 if wet else foot], label="post",
                                role="leg"))
        if r == "slat":                                       # drawSlatPosts: two posts with roses, down to the path
            for px_ in (p["x0"] + 2, p["x1"] - 7):
                out.append(dict(kind="back", road="both", box=[px_, p["y1"], px_ + 5, foot], label="post", role="leg"))
        if r in ("walk", "slat", "deck", "lowbough", "branch"):
            who = role.get(("who", i), "").lower()
            lab = n.lower() or {"slat": "arbour slat", "deck": "tower deck"}.get(r) or \
                {"limes": "lime", "twig": "stub", "bough": "oak bough", "nest bough": "oak bough"}.get(who, (who + " " if who else "") + "branch")
            out.append(dict(kind="usable", road="high", box=box, label=lab, role=r, i=i, owner=who))
            continue
        if p.get("kind") in ("solid", "oneway"):
            if p.get("hidden") and n == "HOLLOW LOG":
                continue                                      # (drawn as the piece, below)
            lab, noart = n.lower(), False
            if not n:                                         # drawPropArt: an unnamed box is drawn by its owner
                o = owner(p)
                on_ = (o.get("name", "") if o else "")
                if on_ in ("OAK", "BRANCH"):
                    lab = "oak branch"
                elif on_ in ("SLIDE", "PLAY TOWER") and p.get("kind") == "oneway":
                    lab = "tower deck"
                elif p.get("hidden") and on_ == "SLIDE":
                    lab = "slide tower"
                elif on_ == "FRAME":
                    lab = "frame bar"
                else:
                    lab, noart = (on_.lower() + " ledge"), True
            if n == "STEP":
                lab = "frame step"
            dbox = list(box)
            if n == "HEDGE":
                w, h = sizes["park_hedge"]; dbox = [p["x0"], p["y0"], p["x0"] + w, p["y0"] + h]
            elif n == "BENCH":
                w, h = sizes["bench"]; dbox = [p["x0"] - 3, 184 + d - h, p["x0"] - 3 + w, 184 + d]
            elif n == "BIN":
                w, h = sizes["bin"]; dbox = [p["x0"] - 1, 184 + d - h, p["x0"] - 1 + w, 184 + d]
            elif n == "PICNIC TABLE":
                w, h = sizes["park_table_front"]; dbox = [p["x0"], p["y0"], p["x0"] + w, p["y0"] + h]
            elif n == "LOG":
                w, h = sizes["park_log"]; dbox = [p["x0"], p["y0"] - 4, p["x0"] + w, p["y0"] - 4 + h]
            elif n == "STONE":
                w, h = sizes["park_stone"]; dbox = [p["x0"] - 1, p["y0"] - 1, p["x0"] - 1 + w, p["y0"] - 1 + h]
            elif n == "FRAME":
                w, h = sizes["park_frame"]; dbox = [p["x0"] - 1, 119 + d, p["x0"] - 1 + w, 119 + d + h]
            out.append(dict(kind="usable", road=road, box=box, draw=dbox, label=lab + (" (no art!)" if noart else ""), i=i, noart=noart))
            continue
        if p.get("kind") == "decor" and p.get("layer") == "play":
            if p.get("leaves"):
                w, h = sizes["park_leaves"]
                cx = (p["x0"] + p["x1"]) / 2
                out.append(dict(kind="signal", road="low", box=[cx - w // 2, p["y1"] - h, cx - w // 2 + w, p["y1"]], label="leaves"))
            else:
                out.append(dict(kind="misplaced", road=road, box=box, label=(n or "decor").lower()))
            continue
        if p.get("kind") == "decor" and p.get("layer") == "back":
            base = 175 + d                                    # the back edge (y 174 on a flat level)
            if n == "GATE":
                w, h = sizes["park_gate"]; out.append(dict(kind="back", road="low", box=[p["x0"], base - h, p["x0"] + w, base], label="gate"))
            elif n == "OAK":
                w, h = sizes["park_oak"]; cx = (p["x0"] + p["x1"]) / 2
                out.append(dict(kind="back", road="low", box=[cx - 94, base - h, cx - 94 + w, base], label="old oak"))
            elif n == "SWINGS":
                w, h = sizes["park_swings"]; cx = (p["x0"] + p["x1"]) / 2
                out.append(dict(kind="back", road="low", box=[cx - w // 2, base - h, cx - w // 2 + w, base], label="swings"))
            elif n == "WILLOWS":
                for k, c in enumerate(crowns):
                    tall = c["y1"] < 120 + d
                    w, h = sizes["park_willow_tall" if tall else "park_willow"]
                    cx = (c["x0"] + c["x1"]) // 2
                    x0 = cx - 32 if k % 2 == 0 else cx + 33 - w
                    out.append(dict(kind="back", road="low", box=[x0, base - h, x0 + w, base], label="willow"))
            elif n == "WINCH":
                bb = frame_bbox("park_keeper_winch", 80, 80)
                X = (p["x0"] + p["x1"]) // 2                       # mirrored, origin (60, 79) at (X, 174 + d)
                out.append(dict(kind="back", road="low", box=[X + 60 - bb[2] + 1, 174 + d - 79 + bb[1], X + 60 - bb[0] + 1, 174 + d - 79 + bb[3]],
                                label="winch man"))
            elif n == "SLIDE":
                w, h = sizes["park_slide"]
                out.append(dict(kind="usable", road="low", box=[p["x0"] - 1, p["y0"] - 1, p["x0"] - 1 + w, p["y0"] - 1 + h], label="slide",
                                art_only=True))
    for pc in L.get("pieces", []):
        if pc.get("kind") == "hollowlog":
            w, h = sizes["park_hollowlog"]
            out.append(dict(kind="usable", road="low", box=[pc["x0"] - 1, pc["y0"] - 1, pc["x0"] - 1 + w, pc["y0"] - 1 + h], label="hollow log"))
    lw, lh = sizes["lamp_post"]
    for l in L.get("lamps", []):
        high = l["y"] < foot - 40
        top = l["y"] - (-1 if high else 10) - lh
        out.append(dict(kind="signal", road="high" if high else "low", box=[l["x"] - lw // 2, top, l["x"] - lw // 2 + lw, top + lh], label="lamp"))
    for m in L.get("movers", []):
        w, h = sizes["park_boat_front"]
        out.append(dict(kind="usable", road="low", box=[m["x0"] - 3, m["y0"] - 18, m["x0"] - 3 + w, m["y0"] - 18 + h], label=(m.get("name") or "").lower(),
                        mover=True))
        a, b = m.get("from", m["x0"]), m.get("to", m["x0"])
        out.append(dict(kind="moving", road="low", box=[a, m["y0"] - 20, b + (m["x1"] - m["x0"]), m["y1"] + 2], label="boat run"))
    for c in L.get("critters", []):
        out.append(dict(kind="moving", road="low", box=[c.get("x0", c["x"]) - 16, c["y"] - 33, c.get("x1", c["x"]) + 18, c["y"]], label=c.get("kind", "")))
    bb = frame_bbox("park_keeper_cart", 82, 82)
    for z in L.get("bikes", []):
        y = z.get("roadY", foot)
        out.append(dict(kind="moving", road="low", box=[z.get("endX", z["zoneX0"]), y - (81 - bb[1]), z["zoneX1"], y], label="leaf cart zone"))
    for bn in L.get("bones", []):
        out.append(dict(kind="pickup", road="high" if bn["y"] <= foot - 90 else "low", box=[bn["x"] - 5, bn["y"] - 12, bn["x"] + 6, bn["y"] - 6],
                        label="gold" if bn.get("super") else "", gold=bool(bn.get("super")), golden=bool(bn.get("golden"))))
    for k, pr in enumerate((L.get("magpie") or {}).get("perches", [])):
        out.append(dict(kind="pickup", road="high" if pr["y"] <= foot - 90 else "low", box=[pr["x"] - 11, pr["y"] - 13, pr["x"] + 11, pr["y"]],
                        label=f"perch {k + 1}", perch=True))
    if "girl" in L:
        g = L["girl"]
        out.append(dict(kind="pickup", road="low", box=[g["x"] - 10, g["y"] - 59, g["x"] + 10, g["y"]], label="mia"))
    if "ball" in L:
        b = L["ball"]
        out.append(dict(kind="pickup", road="low", box=[b["x"] - 3, b["y"] - 6, b["x"] + 3, b["y"]], label="ball"))
    return out


# ------------------------------------------------------------------------------------------------------------------
# the town art code's rules (L.art = "town", the tall Downtown), in Python: scene.lua Sc.drawPropArt's town branch,
# arthooks.lua H.townPiece (the roof kit), H.drawTownBack (the tall fronts), H.drawTrams, H.drawCargo, H.drawFarSpire,
# Sc.drawFarArt's town branch (as on night/25oct-cp-plan 497bd84). Pieces she uses are boxed where their art is drawn;
# the art sizes are read from the files.
TOWN_ART = ("town_door", "town_house1", "town_house2", "town_house3", "town_sign", "town_crate_front", "town_table_front",
            "town_parasol", "town_shopsign", "town_stall", "town_awning64", "town_awning80", "town_tramshed70",
            "town_tramshed96", "town_statue", "town_pedestal", "town_rim", "town_bowl", "town_kiosk", "town_shelter",
            "town_tub", "town_tier", "town_bollard", "town_roof_loggia", "town_roof_gallery72", "town_roof_gallery88",
            "town_roof_chimney", "town_roof_dormer", "town_roof_flower_roof", "town_roof_gable", "town_roof_ledge",
            "town_footbridge", "lamp_post")
TOWN_KIT = ("LOGGIA", "GALLERY", "CHIMNEY", "DORMER", "FLOWER ROOF", "GUILD ROOF", "FOOTBRIDGE")


def town_high(foot):
    """the roofs: a box whose bottom is 130 px or more over the street (the beat sheet's high road, y 200 to 286)"""
    return foot - 130


def classify_town(L, rows):
    """every drawn thing of a town level, as classify() does for the park"""
    foot = L.get("foot", 184)
    d = foot - 184
    props = L.get("props", [])
    sz = {n: art_size(n) for n in TOWN_ART}
    hi = town_high(foot)
    out = []
    named = [p for p in props if p.get("name") and p.get("layer") != "front"]

    def owner(p):
        cx = (p["x0"] + p["x1"]) / 2
        best, bd = None, 1e9
        for q in named:
            dd = max(0, q["x0"] - cx, cx - q["x1"])
            if dd < bd:
                best, bd = q, dd
        return best
    gset, g0 = set(), None                                    # arthooks gable(): GUILD ROOF and the steps after it
    for i, p in enumerate(props):
        if p.get("name") == "GUILD ROOF":
            g0, gx1, gtop, gbot = i, p["x1"], p["y0"], p["y1"]
            gset.add(i)
            j = i + 1
            while j < len(props) and not props[j].get("name") and props[j].get("kind") != "decor" and props[j]["x0"] == gx1:
                gset.add(j); gx1 = props[j]["x1"]; gtop = min(gtop, props[j]["y0"]); j += 1
            gbox = [p["x0"] - 1, gtop - 1, p["x0"] - 1 + sz["town_roof_gable"][0], gtop - 1 + sz["town_roof_gable"][1]]
            gall = [p["x0"], gtop, gx1, gbot]

    def centred(p, name, top):
        w, h = sz[name]
        x = (p["x0"] + p["x1"]) // 2 - w // 2
        return [x, top, x + w, top + h]
    nb = 0
    for i, p in enumerate(props):
        n = p.get("name") or ""
        w, h = p["x1"] - p["x0"], p["y1"] - p["y0"]
        road = "high" if p["y1"] <= hi else "low"
        box = [p["x0"], p["y0"], p["x1"], p["y1"]]
        if p.get("layer") == "front":                          # a bollard at 1.3
            bw, bh = sz["town_bollard"]
            cx = (p["x0"] + p["x1"]) / 2
            top = max(221 + d, p["y0"])
            out.append(dict(kind="front", road="low", box=[cx - bw // 2, top, cx - bw // 2 + bw, top + bh], label="bollard", scroll=1.3,
                            mid=cx))
            continue
        if p.get("kind") == "decor" and p.get("layer") == "back":
            if n == "RIDDARHOLMEN":
                continue                                      # (drawn far: H.drawFarSpire)
            if n in ("", "BAKERY", "GUILD HOUSE") and w >= 48 and h >= 100:
                nb += 1                                       # a tall front (H.drawTownBack), cut at its top
                out.append(dict(kind="back", road="both", box=box, label=(n.lower() if n else "tall front"), role="front",
                                plaster=p.get("plaster", "")))
            elif n == "DOOR":
                bw, bh = sz["town_door"]
                out.append(dict(kind="back", road="low", box=[p["x0"], 175 + d - bh, p["x0"] + bw, 175 + d], label="door"))
            elif n == "HOUSE":
                k = sum(1 for q in props[:i + 1] if q.get("name") == "HOUSE")
                out.append(dict(kind="back", road="low", box=centred(p, "town_house%d" % ((k - 1) % 3 + 1), 0), label="plaza house"))
                b = out[-1]["box"]; hh = b[3] - b[1]; b[1], b[3] = 175 + d - hh, 175 + d
            elif n == "RIVER":
                b = centred(p, "town_sign", 0); hh = b[3] - b[1]; b[1], b[3] = 175 + d - hh, 175 + d
                out.append(dict(kind="back", road="low", box=b, label="river sign"))
            continue                                          # (unnamed: posts, poles, the fountain's column)
        if p.get("kind") == "decor" and p.get("layer") == "play":
            if n == "STATUE":                                 # its arm and hat are ledges: an obstacle (play look)
                bw, bh = sz["town_statue"]
                out.append(dict(kind="usable", road="low", box=[p["x0"] - 1, p["y0"] - 4, p["x0"] - 1 + bw, p["y0"] - 4 + bh], label="statue",
                                art_only=True))
            else:
                out.append(dict(kind="misplaced", road=road, box=box, label=(n or "decor").lower()))
            continue
        if p.get("kind") not in ("solid", "oneway"):
            continue
        high = p["y0"] <= foot - 120                          # arthooks high()
        lab, dbox, extra = n.lower(), list(box), None
        if i in gset:                                         # the stepped gable: drawn once, with its first step
            if i != g0:
                out.append(dict(kind="usable", road="high", box=box, draw=box, label="guild roof", i=i, hidden=True))
                continue
            lab, dbox, box = "guild roof", list(gbox), list(gall)
        elif high and (n == "" or n in TOWN_KIT):
            if n == "FOOTBRIDGE":
                dbox = centred(p, "town_footbridge", p["y0"] - 1 - 12)
            elif n == "GALLERY":
                dbox = centred(p, "town_roof_gallery%d" % w, p["y0"] - 1)
            elif n:
                dbox = centred(p, "town_roof_" + n.lower().replace(" ", "_"), p["y0"] - 1)
            else:
                lab, dbox = "roof ledge", [p["x0"] - 1, p["y0"] - 1, p["x1"] + 1, p["y0"] - 1 + sz["town_roof_ledge"][1]]
        else:
            if not n:
                o = owner(p)
                on_ = o.get("name", "") if o else ""
                if on_ == "CRATES":
                    n = "CRATES"
                else:
                    lab = on_.lower() + (" hat" if on_ == "STATUE" else " ledge")
            if n == "CRATES":
                k = max(1, int(h / 16 + 0.5))
                lab, dbox = "crates", [p["x0"], p["y1"] - 16 * k - 12, p["x0"] + sz["town_crate_front"][0], p["y1"]]
            elif n == "TABLE":
                bw, bh = sz["town_table_front"]; dbox = [p["x0"] - 1, p["y0"], p["x0"] - 1 + bw, p["y0"] + bh]
            elif n == "PARASOL":
                bw, bh = sz["town_parasol"]; dbox = [p["x0"], p["y0"] - 1, p["x0"] + bw, p["y0"] - 1 + bh]
                lab = "springy parasol" if p.get("bounce") else "parasol"
            elif n == "SIGN":                                 # the board (art rows 5 to 29) on its post
                dbox = [p["x0"] - 1, p["y0"] - 1, p["x0"] + 46, p["y0"] + 24]
                lab, extra = "sign", [p["x0"] + 36, p["y0"] + 24, p["x0"] + 42, p["y0"] + 106]
            elif n == "STALL":
                bw, bh = sz["town_stall"]; dbox = [p["x0"] - 1, p["y0"] - 15, p["x0"] - 1 + bw, p["y0"] - 15 + bh]
            elif n == "AWNING":
                nm = "town_awning80" if w >= 72 else "town_awning64"
                dbox = centred(p, nm, p["y0"] - 1)
                lab = ("window awning" if high else "awning") if not p.get("bounce") else ("springy window awning" if high else "springy awning")
            elif n in ("GATE", "TRAM SHED"):
                dbox, lab = [p["x0"], p["y0"], p["x1"], p["y0"] + min(h, 41)], "courtyard gate"
            elif n == "PEDESTAL":
                bw, bh = sz["town_pedestal"]; dbox = [p["x0"], p["y0"], p["x0"] + bw, p["y0"] + bh]
            elif n == "ARM":
                lab = "statue arm"
            elif n == "RIM":
                bw, bh = sz["town_rim"]; dbox = [p["x0"] - 1, p["y0"] - 1, p["x0"] - 1 + bw, p["y0"] - 1 + bh]
            elif n == "FOUNTAIN":
                bw, bh = sz["town_bowl"]; dbox = [p["x0"] - 1, p["y0"] - 1, p["x0"] - 1 + bw, p["y0"] - 1 + bh]
                lab = "fountain bowl"
            elif n == "KIOSK":
                bw, bh = sz["town_kiosk"]; dbox = [p["x0"] - 1, p["y0"] - 1, p["x0"] - 1 + bw, p["y0"] - 1 + bh]
            elif n == "SHELTER":
                bw, bh = sz["town_shelter"]; dbox = [p["x0"], p["y0"], p["x0"] + bw, p["y0"] + bh]
            elif n == "TUB":
                bw, bh = sz["town_tub"]; dbox = [p["x0"], p["y0"] - 13, p["x0"] + bw, p["y0"] - 18 + bh]   # (rows 5 to 45)
            elif n == "BALCONY":                              # drawBalcony: a 9 px railing, the slab, brackets
                dbox = [p["x0"] - 1, p["y0"] - 9, p["x1"] + 1, p["y0"] + 11]
            elif n == "TIER":
                bw, bh = sz["town_tier"]; dbox = [p["x0"] - 1, p["y0"] - 1, p["x0"] - 1 + bw, p["y0"] - 1 + bh]
                lab = "fountain tier"
        it = dict(kind="usable", road=road, box=box, draw=dbox, label=lab, i=i)
        if extra:
            it["post"] = extra
        if n in ("PEDESTAL", "ARM") or lab == "statue hat":   # one piece to a child: the statue she climbs,
            it["set"] = "statue"                              # the fountain, a stack of crates
        elif n in ("RIM", "FOUNTAIN", "TIER"):
            it["set"] = "fountain"
        elif lab == "crates":
            for q in out:
                if q.get("label") == "crates" and q["box"][0] <= box[2] and q["box"][2] >= box[0] and q["box"][3] >= box[1] - 1:
                    q.setdefault("set", "crates%d" % q["i"])
                    it["set"] = q["set"]
        out.append(it)
    lw, lh = sz["lamp_post"]
    for l in L.get("lamps", []):
        high = l["y"] < foot - 40
        top = l["y"] - (-1 if high else 10) - lh
        lx = l["x"] - lw // 2
        if high:                                              # (its whole foot on the ledge, stage.lua)
            for p in props:
                if p.get("kind") != "decor" and p["y0"] == l["y"] and p["x0"] <= l["x"] < p["x1"]:
                    lx = max(p["x0"], min(p["x1"] - lw, lx))
        out.append(dict(kind="signal", road="high" if high else "low", box=[lx, top, lx + lw, top + lh], label="lamp"))
    for z in L.get("bikes", []):                              # cargo bikes: drawn right of their courtyard gate
        y = z.get("roadY", foot)
        out.append(dict(kind="moving", road="low", box=[z.get("depot", z["zoneX0"]), y - 77, z["zoneX1"], y], label="cargo bike zone"))
    for t in L.get("trams", []):                              # the vintage tram: decoration in the back lane
        out.append(dict(kind="moving", road="both", box=[t["x0"], t["y1"] - 130, t["x1"], t["y1"]], label="tram lane (back, faded)",
                        back=True))
        out.append(dict(kind="back", road="low", box=[t["stop"] - 6, t["y1"] - 57, t["stop"] + 8, t["y1"]], label="tram stop"))
    for c in L.get("critters", []):
        out.append(dict(kind="moving", road="low", box=[c.get("x0", c["x"]) - 16, c["y"] - 33, c.get("x1", c["x"]) + 18, c["y"]], label=c.get("kind", "")))
    for bn in L.get("bones", []):
        out.append(dict(kind="pickup", road="high" if bn["y"] <= hi else "low", box=[bn["x"] - 5, bn["y"] - 12, bn["x"] + 6, bn["y"] - 6],
                        label="gold" if bn.get("super") else "", gold=bool(bn.get("super")), golden=bool(bn.get("golden"))))
    if "cat" in L:
        c = L["cat"]
        out.append(dict(kind="pickup", road="low", box=[c["x"] - 9, c["y"] - 29, c["x"] + 11, c["y"] + 1], label="cat"))
    if "girl" in L:
        g = L["girl"]
        out.append(dict(kind="pickup", road="low", box=[g["x"] - 10, g["y"] - 59, g["x"] + 10, g["y"]], label="mia"))
    if "ball" in L:
        b = L["ball"]
        out.append(dict(kind="pickup", road="low", box=[b["x"] - 3, b["y"] - 6, b["x"] + 3, b["y"]], label="ball"))
    return out


def surfaces(L, rows):
    """the floors Pepper can stand on: terrain tops and the tops of solid and one-way boxes"""
    S = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "#" and (r == 0 or rows[r - 1][c] != "#"):
                S.append((c * 8, c * 8 + 8, r * 8))
    for p in L.get("props", []):
        if p.get("kind") in ("solid", "oneway"):
            S.append((p["x0"], p["x1"], p["y0"]))
    for m in L.get("movers", []):
        S.append((m["x0"], m["x1"], m["y0"]))
    return S


# ------------------------------------------------------------------------------------------------------------------
C = {
    "sky": (226, 233, 241), "clouds": (240, 244, 248), "city": (205, 211, 226), "shore": (190, 206, 190),
    "mid": (174, 194, 174), "water": (164, 190, 214), "back": (236, 214, 160), "backtx": (120, 96, 50),
    "ground": (150, 152, 162), "play": (255, 255, 255), "playedge": (208, 52, 44), "move": (240, 138, 36),
    "goal": (242, 201, 76), "goaltx": (130, 96, 10), "front": (34, 34, 40), "pepper": (20, 20, 24),
    "purple": (150, 0, 150), "bank": (128, 120, 104), "frame": (0, 0, 0),
}


def rng(seed):
    s = [seed]

    def f(a, b):
        s[0] = (s[0] * 1103515245 + 12345) % 2147483648
        return a + (s[0] % 100000) / 100000 * (b - a)
    return f


def mid_trees(W):
    """Sc.buildArt: the near trees of the park's mid layer (parallax 0.5), deterministic"""
    r, out, x = rng(47), [], -30
    while x < 320 + (W - 320) * 0.5 + 64:
        out.append((x, 1 + len(out) % 2))
        x = x + 90 + int(r(10, 90) // 1)
    return out


def mask(name, colour):
    """an art file's silhouette in one flat colour (the far layers of the town, drawn as their art's shape)"""
    im = Image.open(os.path.join(ART, name + ".png")).convert("RGBA")
    a = im.split()[3].point(lambda v: 255 if v >= 128 else 0)
    flat = Image.new("RGB", im.size, colour)
    return flat, a


def far_town(L, d, cam, far, mid, font, W):
    """Sc.drawFarArt's town branch: the far roofs and spires (0.25, bottom y 160), Riddarholmen's spire on the same
    layer (H.drawFarSpire: at the level's end it stands over its box), the old town facades (0.5, bottom y 178)"""
    im = d._image
    rf, ra = mask("town_roofs", C["shore"])
    ox = int(cam * 0.25) % rf.width
    for x in range(-ox, 320, rf.width):
        im.paste(rf, (x, 160 - rf.height + far), ra)
    d.text((4, 160 - 40 + far), "far roofs 0.25", fill=(90, 110, 90), font=font)
    sp = next((p for p in L.get("props", []) if p.get("name") == "RIDDARHOLMEN"), None)
    if sp:
        sf, sa = mask("spire_riddarholmen", (168, 190, 168))
        camEnd = max(0, W - 320)
        x = int((sp["x0"] + sp["x1"]) / 2 - cam * 0.3 - camEnd * 0.7 - sf.width / 2 + 0.5)
        if -sf.width < x < 320:
            im.paste(sf, (x, 8 + far), sa)
            d.text((x + sf.width + 2, 20 + far), "spire (far)", fill=(70, 92, 70), font=font)
    ff, fa = mask("town_facades", C["mid"])
    ox = int(cam * 0.5) % ff.width
    for x in range(-ox, 320, ff.width):
        im.paste(ff, (x, 178 - ff.height + mid), fa)
    d.text((4, 178 - 12 + mid), "old town facades 0.5", fill=(70, 92, 70), font=font)


def frame(L, rows, items, cam, cy, font, foot, W, H):
    """one screen at camera (cam, cy), 320 x 240"""
    im = Image.new("RGB", (320, 240), C["sky"])
    d = ImageDraw.Draw(im)
    camYMax = H - 240
    rel = camYMax - cy
    far, mid = round(rel * 0.3), round(rel * 0.6)
    for x0, y0 in ((60, 22), (190, 44), (280, 14)):         # clouds (0.05 + drift): a light band
        d.ellipse([x0 - (cam * 0.05) % 120, y0 + far, x0 + 70 - (cam * 0.05) % 120, y0 + 18 + far], fill=C["clouds"])
    d.rectangle([0, 150 - 77 + far, 319, 150 + far], fill=C["city"])        # far city: the skyline, bottom y 150
    d.text((4, 150 - 77 + far + 2), "far city (128 px a level)", fill=(110, 116, 140), font=font)
    if L.get("art") == "town":
        far_town(L, d, cam, far, mid, font, W)
    else:
        d.rectangle([0, 177 - 31 + far, 319, 177 + far], fill=C["shore"])       # the far tree line (0.25), bottom y 177
        d.text((4, 177 - 31 + far + 2), "tree line 0.25", fill=(90, 110, 90), font=font)
        tw, th = art_size("park_tree1")
        for x, i in mid_trees(W):                                               # mid trees (0.5), bottom y 180
            sx = x - int(cam * 0.5)
            if -tw < sx < 330:
                d.rectangle([sx + 6, 180 - th + mid, sx + tw - 6, 180 + mid - 1], fill=C["mid"])
                d.rectangle([sx + tw // 2 - 3, 180 - 30 + mid, sx + tw // 2 + 3, 180 + mid - 1], fill=(150, 170, 150))
        d.text((4, 180 - 12 + mid), "mid trees 0.5", fill=(70, 92, 70), font=font)

    def wx(x):
        return x - cam

    def wy(y):
        return y - cy
    # the pond: far bank (lawn, earth) then the water, down to the world's bottom
    water_cols = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "~":
                water_cols.setdefault(c, r)
    runs, prev = [], None
    for c in sorted(water_cols):
        if prev is not None and c == prev + 1 and water_cols[c] == water_cols[prev]:
            runs[-1][1] = c
        else:
            runs.append([c, c, water_cols[c]])
        prev = c
    for c0, c1, r in runs:
        x0, x1, y0 = c0 * 8, c1 * 8 + 8, r * 8
        d.rectangle([wx(x0), wy(172 + foot - 184), wx(x1) - 1, wy(y0) - 1], fill=C["bank"])
        d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(H)], fill=C["water"])
    back = [it for it in items if it["kind"] == "back"]
    town = L.get("art") == "town"
    for it in sorted(back, key=lambda t: {"canopy": 0, "trunk": 1, "front": 0}.get(t.get("role"), 2)):
        x0, y0, x1, y1 = it["box"]
        col = {"nest": (196, 160, 100), "leg": (214, 186, 126)}.get(it.get("role"), C["back"])
        d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], fill=col)
        if it.get("role") == "canopy" or town:
            d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], outline=(196, 166, 108) if town else (214, 190, 136))
    for t in (items if town else []):                         # the tram lane: moving decoration on the back layer
        if t.get("back"):
            x0, y0, x1, y1 = t["box"]
            for xx in range(int(wx(x0)), int(wx(x1)), 6):
                d.line([xx, wy(y0), xx + 2, wy(y0)], fill=C["move"], width=2)
                d.line([xx, wy(y1) - 1, xx + 2, wy(y1) - 1], fill=C["move"], width=2)
            d.text((max(wx(x0), 0) + 3, wy(y0) + 3), t["label"], fill=C["move"], font=font)
    for it in back:
        x0, y0, x1, y1 = it["box"]
        if it.get("role") in ("trunk", "towerpost") and it["label"] == "trunk":
            continue
        if it["label"] in ("post",):
            continue
        d.text((wx(x0) + 2, max(wy(y0), 0) + 2), it["label"], fill=C["backtx"], font=font)
    for r, row in enumerate(rows):                                          # terrain
        for c, ch in enumerate(row):
            if ch == "#":
                d.rectangle([wx(c * 8), wy(r * 8), wx(c * 8) + 7, wy(r * 8) + 7], fill=C["ground"])
            elif ch in "/\\":
                pts = [(wx(c * 8), wy(r * 8 + 8)), (wx(c * 8 + 8), wy(r * 8 + 8)), (wx(c * 8 + 8), wy(r * 8))] if ch == "/" else \
                      [(wx(c * 8), wy(r * 8)), (wx(c * 8), wy(r * 8 + 8)), (wx(c * 8 + 8), wy(r * 8 + 8))]
                d.polygon(pts, fill=C["ground"])
    for it in items:                                                        # lamps (back look), signals
        if it["kind"] == "signal":
            x0, y0, x1, y1 = it["box"]
            if it["label"] == "lamp":
                d.rectangle([wx(x0) + 4, wy(y0) + 8, wx(x1) - 5, wy(y1) - 1], fill=C["back"], outline=C["goaltx"])
                d.ellipse([wx(x0) + 1, wy(y0), wx(x1) - 2, wy(y0) + 11], fill=C["goal"], outline=C["goaltx"])
                d.text((wx(x0) - 4, wy(y0) - 11), "lamp", fill=C["goaltx"], font=font)
            else:
                d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], fill=(250, 232, 170), outline=C["goal"], width=2)
                d.text((wx(x0) + 2, wy(y0) - 11), it["label"], fill=C["goaltx"], font=font)
    for it in items:                                                        # usable, then moving
        if it["kind"] == "usable":
            x0, y0, x1, y1 = it.get("draw") or it["box"]
            if it.get("hidden"):
                continue
            if it.get("post"):                                # a sign's post, under its board
                a0, b0, a1, b1 = it["post"]
                d.rectangle([wx(a0), wy(b0), wx(a1) - 1, wy(b1) - 1], fill=C["play"], outline=C["playedge"])
            if it.get("art_only"):
                d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], outline=C["playedge"])
                continue
            if it.get("noart"):                               # a ledge she can stand on that nothing draws
                for xx in range(int(wx(x0)), int(wx(x1)), 4):
                    d.line([xx, wy(y0), xx + 1, wy(y0)], fill=C["purple"])
                    d.line([xx, wy(y1) - 1, xx + 1, wy(y1) - 1], fill=C["purple"])
                continue
            d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], fill=C["play"], outline=C["playedge"], width=2 if y1 - y0 > 7 else 1)
    for it in items:
        if it["kind"] == "moving" and not it.get("back"):
            x0, y0, x1, y1 = it["box"]
            d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], outline=C["move"], width=2)
            d.text((wx(x0) + 3, wy(y0) + 2), it["label"], fill=C["move"], font=font)
        if it["kind"] == "misplaced":
            x0, y0, x1, y1 = it["box"]
            d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], fill=C["back"], outline=C["purple"], width=2)
            d.text((wx(x0) + 2, wy(y0) - 11), it["label"] + " (decor on her line!)", fill=C["purple"], font=font)
    seen = set()
    for it in items:                                                        # labels of usable pieces, once each
        if it["kind"] == "usable" and not it.get("art_only") and not it.get("hidden"):
            x0, y0, x1, y1 = it.get("draw") or it["box"]
            lab = it["label"]
            key = (lab, round(wx(x0) / 60))
            if key in seen:
                continue
            seen.add(key)
            ty = wy(y0) + 2 if y1 - y0 >= 14 else wy(y0) - 11
            d.text((wx(x0) + 2, ty), lab, fill=C["purple"] if it.get("noart") else C["playedge"], font=font)
    for it in items:                                                        # pickups and goals
        if it["kind"] == "pickup":
            x0, y0, x1, y1 = it["box"]
            if it.get("perch"):
                d.polygon([(wx(x0) + 4, wy(y1) - 2), (wx(x1) - 4, wy(y1) - 2), ((wx(x0) + wx(x1)) / 2, wy(y0) + 2)], outline=C["goaltx"])
                d.text((wx(x0) - 2, wy(y0) - 10), it["label"].replace("perch ", "p"), fill=C["goaltx"], font=font)
            elif it["label"] in ("mia", "cat"):
                d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], fill=C["goal"], outline=C["pepper"])
                d.text((wx(x0) + 1, wy(y0) + 2), it["label"], fill=C["pepper"], font=font)
            else:
                d.rectangle([wx(x0), wy(y0), wx(x1) - 1, wy(y1) - 1], fill=(255, 190, 40) if it.get("gold") else C["goal"],
                            outline=C["goaltx"])
    # Pepper where the sweep puts her
    px = cam + 140
    fys = [y for (a, b, y) in surfaces(L, rows) if a <= px + 4 and b >= px - 4 and cy + 60 <= y <= cy + 236]
    if fys:
        fy = min(fys)
        d.rectangle([wx(px) - 26, wy(fy) - 38, wx(px) + 25, wy(fy) - 1], fill=C["pepper"])
        d.text((wx(px) - 22, wy(fy) - 34), "pepper", fill=(220, 220, 220), font=font)
    for it in items:                                                        # front frame (1.3)
        if it["kind"] == "front":
            x0, y0, x1, y1 = it["box"]
            camf = cam + (cam + 160 - it["mid"]) * 0.3
            d.rectangle([x0 - camf, wy(y0), x1 - camf - 1, wy(min(y1, H)) - 1], fill=C["front"])
            d.text((x0 - camf + 3, wy(y0) + 3), "front " + it["label"] + " 1.3", fill=(200, 200, 200), font=font)
    return im


# ------------------------------------------------------------------------------------------------------------------
def report(L, rows, items, W, H, foot, tiers=None):
    """the numbers per screen the plan quotes"""
    n = (W + 319) // 320
    S = []
    water = set()
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "~":
                water.update(range(c * 8, c * 8 + 8))
    path = set()
    for (a, b, y) in surfaces(L, rows):
        if y == foot:
            path.update(range(a, b))
    for s in range(n):
        x0, x1 = s * 320, min(W, s * 320 + 320)

        def on(it):
            bx0, by0, bx1, by1 = it["box"]
            c = (bx0 + bx1) / 2
            return x0 <= c < x1
        row = dict(screen=s + 1, x=[x0, x1])
        for road in ("low", "high"):
            us = [it for it in items if it["kind"] == "usable" and it["road"] == road and on(it) and not it.get("art_only") and not it.get("hidden")]
            row[f"usable_{road}"] = [it["label"] for it in us]
            if tiers:                                           # (the town) pieces as a child sees them
                row[f"pieces_{road}"] = len(set(it.get("set", "i%d" % it.get("i", 0)) for it in us))
            row[f"bones_{road}"] = sum(1 for it in items if it["kind"] == "pickup" and not it.get("perch") and it["label"] in ("", "gold")
                                       and it["road"] == road and on(it))
            row[f"lamps_{road}"] = [it["box"][0] + 7 for it in items if it["label"] == "lamp" and it["road"] == road and on(it)]
            row[f"perches_{road}"] = [it["label"] for it in items if it.get("perch") and it["road"] == road and on(it)]
        row["back"] = sorted(set(it["label"] for it in items if it["kind"] == "back" and on(it) and it["label"] not in ("post",)))
        row["front"] = [it["label"] for it in items if it["kind"] == "front" and on(it)]
        row["moving"] = [it["label"] for it in items if it["kind"] == "moving" and on(it)]
        row["misplaced"] = [it["label"] for it in items if it["kind"] == "misplaced" and on(it)]
        busy = set()
        for it in items:                                        # what stands on the path (low road)
            if it["kind"] in ("usable", "signal") and it["road"] == "low" and it["label"] != "lamp":
                bx0, by0, bx1, by1 = it.get("draw") or it["box"]
                if by1 >= foot - 2 and by0 < foot:
                    busy.update(range(int(bx0), int(bx1)))
        free = [x for x in range(x0, x1) if x in path and x not in busy and x not in water]
        run, best, prev = 0, 0, None
        for x in free:
            run = run + 1 if prev is not None and x == prev + 1 else 1
            best = max(best, run)
            prev = x
        row["empty_path_px"] = len(free)
        row["longest_empty_run_px"] = best
        row["water_px"] = len([x for x in range(x0, x1) if x in water])
        for cy in (tiers or (0, H - 240)):                      # what one frame shows (the sweep's cameras)
            def seen(it):
                bx0, by0, bx1, by1 = it["box"]
                return bx1 > x0 and bx0 < x1 and by1 > cy and by0 < cy + 240
            vis = [it for it in items if seen(it)]
            row[f"frame_y{cy}"] = dict(
                usable=len([it for it in vis if it["kind"] == "usable" and not it.get("art_only") and not it.get("hidden")]),
                back=len([it for it in vis if it["kind"] == "back" and it["label"] not in ("post",)]),
                signals=len([it for it in vis if it["kind"] == "signal"]),
                moving=len([it for it in vis if it["kind"] == "moving"]),
                pickups=len([it for it in vis if it["kind"] == "pickup" and not it.get("perch")]),
                front=len([it for it in vis if it["kind"] == "front"]))
        S.append(row)
    return S


def main():
    lv, outp = sys.argv[1], sys.argv[2]
    cols = int(sys.argv[sys.argv.index("--cols") + 1]) if "--cols" in sys.argv else 3
    S = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 2
    L, rows = load(lv)
    W, H = len(rows[0]) * 8, len(rows) * 8
    foot = L.get("foot", 184)
    town = L.get("art") == "town"
    items = classify_town(L, rows) if town else classify(L, rows)
    font = ImageFont.load_default()
    n = (W + 319) // 320
    tiers = [0, H - 240] if H > 240 else [0]                 # the high road on top, the low road under it
    if "--tiers" in sys.argv:                                # (the town: the roofs' camera is not the top of the world)
        tiers = [int(v) for v in sys.argv[sys.argv.index("--tiers") + 1].split(",")]
    cw, ch = 320 * S, 240 * S
    pad, head, top = 8, 22, 30
    rows_n = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cw + pad) - pad, top + rows_n * (len(tiers) * (ch + 4) + head + pad)), (255, 255, 255))
    sd = ImageDraw.Draw(sheet)
    x = 4                                                   # the legend
    for col, txt in ((C["playedge"], "usable"), (C["move"], "moving"), (C["goal"], "pickup, goal, lamp, leaves"),
                     (C["back"], "decoration behind her"), (C["purple"], "on her line by mistake / ledge with no art"),
                     (C["front"], "front (1.3)"), (C["mid"], "old town facades 0.5" if town else "mid trees 0.5"),
                     (C["shore"], "far roofs, spire 0.25" if town else "tree line 0.25"),
                     (C["city"], "far city"), (C["water"], "water"), (C["pepper"], "Pepper (sweep spot)")):
        sd.rectangle([x, 8, x + 14, 20], fill=col, outline=(0, 0, 0))
        sd.text((x + 18, 9), txt, fill=(0, 0, 0), font=font)
        x += 24 + int(sd.textlength(txt, font=font)) + 10
    for i in range(n):
        cam = min(i * 320, W - 320)
        x = (i % cols) * (cw + pad)
        y = top + (i // cols) * (len(tiers) * (ch + 4) + head + pad)
        sd.text((x + 2, y + 5), f"screen {i + 1}: x {cam}-{cam + 320}   (top: high road, camera y {tiers[0]};  bottom: low road, camera y {tiers[-1]})",
                fill=(0, 0, 0), font=font)
        for k, cy in enumerate(tiers):
            fr = frame(L, rows, items, cam, cy, font, foot, W, H).resize((cw, ch), Image.NEAREST)
            sheet.paste(fr, (x, y + head + k * (ch + 4)))
    sheet.save(outp)
    print("screens", n, "tiers", tiers, "size", sheet.size)
    if "--report" in sys.argv:
        rp = sys.argv[sys.argv.index("--report") + 1]
        json.dump(dict(level=lv, size=[W, H], foot=foot, screens=report(L, rows, items, W, H, foot, tiers if town else None),
                       items=[{k: v for k, v in it.items() if k != "i"} for it in items]), open(rp, "w"), indent=1)
        print("report", rp)


if __name__ == "__main__":
    main()
