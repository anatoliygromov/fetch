#!/usr/bin/env python3
"""tools/fix_dt_06nov.py: the board's "fix" calls on Downtown pieces (owner, 25 Oct), fixed BY HAND, by rule: every
changed pixel is written to art/source/<name>/edits.json (x, y, from, to, rule) and the result to
art/source/<name>/<name>.aseprite (tools/aseprite_io.py). No automated clean pass (BIBLE 3, owner 25 Oct): nothing
here finds or smooths "dirt"; each rule names the pixels it changes and why. The original is kept beside the source
(<name>_before.png) and every run starts from it, so the fix is repeatable and reviewable.

  town_house1, town_house2  "decoration drawn with an outline, contrast": the black outline round the silhouette and
                            the black cornice lip become the darker shade of the material they edge (its own colour,
                            BIBLE: decoration has no outline); house 1's glass and white frames are brought 9 and 21
                            luma closer so the house sits within the back layer's 120 contrast.
  town_awning64, town_awning80  the canvas's stripes ran crooked and at 4 to 6 px; the valance's tongues were uneven
                            and mixed red and cream at random. Now: vertical stripes 8 px wide, red and cream in turn,
                            each ending in one tongue of the same 8 px part (stamped), on both awnings the same pixels;
                            the two reds of awning80 become awning64's one red. The rail, the silhouette and the 1 px
                            ink outline are unchanged.
  town_table_front          the cafe table was the darkest thing on the street (luma 40, darker than Pepper): the top and
                            legs go mid-tone in their own blue and steel ramps (about 110 on screen, as the crates),
                            the legs' dark edges and the top's underside become the ink outline, so the silhouette is
                            closed on both sides of each leg.

  python3 -I tools/fix_dt_06nov.py            apply (writes the pngs, edits.json, .aseprite)
  python3 -I tools/fix_dt_06nov.py --check    fail if a png on disk differs from the fix
"""
import os, sys, json, argparse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aseprite_io  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "riverwalk", "art", "scene")
SRC = os.path.join(ROOT, "art", "source")


def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def before(name):
    """the original pixels: art/source/<name>/<name>_before.png (copied from the game file on the first run)"""
    d = os.path.join(SRC, name); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + "_before.png")
    if not os.path.exists(p): Image.open(os.path.join(SCENE, name + ".png")).convert("RGBA").save(p)
    return np.array(Image.open(p).convert("RGBA"))


class Edit:
    def __init__(self, a):
        self.a = a.copy(); self.log = []

    def set(self, x, y, rgb, rule):
        old = tuple(int(v) for v in self.a[y, x, :3])
        if self.a[y, x, 3] == 0 or old == tuple(rgb): return
        self.a[y, x, :3] = rgb
        self.log.append(dict(x=int(x), y=int(y), was="%02x%02x%02x" % old, now="%02x%02x%02x" % tuple(rgb), rule=rule))


def opaque(a): return a[..., 3] > 0


def edge_mask(a):
    """silhouette edge: an opaque pixel with a transparent 4-neighbour or on the image's border"""
    on = opaque(a); h, w = on.shape
    pad = np.pad(on, 1, constant_values=False)
    nb = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    return on & ~nb


def inward(a, x, y, skip):
    """the colour one step inside the silhouette from an edge pixel (the first opaque neighbour, scanning 1-3 px in
    the four directions, that is not one of the `skip` colours)"""
    h, w = a.shape[:2]
    for d in range(1, 4):
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            xx, yy = x + dx * d, y + dy * d
            if 0 <= xx < w and 0 <= yy < h and a[yy, xx, 3] and "%02x%02x%02x" % tuple(a[yy, xx, :3]) not in skip:
                return "%02x%02x%02x" % tuple(a[yy, xx, :3])
    return None


# ---- the plaza houses -------------------------------------------------------------------------------------------
# per house: the dark outline colours, and each material colour's own darker shade (an existing colour of the house)
HOUSES = {
    "town_house1": dict(
        ink={"020100"},
        shade={"b1b8a4": "767b69", "b4b89d": "767b69", "bcc0af": "767b69", "767b69": "767b69", "8c9089": "767b69",
               "5c5856": "767b69", "edf1e1": "767b69", "5b3b34": "5c5856", "282b36": "5c5856"},
        # contrast: glass 282b36 -> 3a3e4a (+9 luma), frames edf1e1 -> d6dccb (-21 luma), every pixel of each;
        # then every colour x 0.66 (value): the house at the sample screen's back value (on screen about 150, as the
        # tall fronts behind it; it was 201, lighter than the old town row across the square)
        remap={"282b36": "3a3e4a", "edf1e1": "d6dccb"}, value=0.66),
    "town_house2": dict(
        ink={"020100", "151c28", "282b36"},
        shade={"bf5b42": "854733", "b95e43": "854733", "854733": "5a3a33", "86624f": "5a3a33", "5d5957": "5d5957",
               "5a3a33": "5a3a33", "eaedde": "854733", "b9bdac": "5d5957"},
        remap={}, value=1.0),                                       # (already at the fronts' value: 157 on screen)
}


def fix_house(name):
    R = HOUSES[name]
    a0 = before(name); E = Edit(a0)
    em = edge_mask(a0)
    for y, x in zip(*np.nonzero(em)):
        c = "%02x%02x%02x" % tuple(a0[y, x, :3])
        if c in R["ink"]:
            m = inward(a0, x, y, R["ink"])
            if m: E.set(x, y, hx(R["shade"].get(m, "5c5856" if name == "town_house1" else "5a3a33")),
                        "silhouette outline -> the darker shade of the material it edges")
    if name == "town_house2":                                        # the cornice's black lip (rows 42) inside
        for x in range(a0.shape[1]):
            c = "%02x%02x%02x" % tuple(a0[42, x, :3])
            if a0[42, x, 3] and not em[42, x] and c in R["ink"]:
                E.set(x, 42, hx("5a3a33"), "the cornice's black lip -> the plaster's darkest shade")
    for y, x in zip(*np.nonzero(opaque(E.a))):
        c = "%02x%02x%02x" % tuple(E.a[y, x, :3])
        if c in R["remap"]: E.set(x, y, hx(R["remap"][c]), "contrast: glass lighter, frames darker (whole colour)")
    if R["value"] != 1.0:
        for y, x in zip(*np.nonzero(opaque(E.a))):
            E.set(x, y, tuple(int(round(v * R["value"])) for v in E.a[y, x, :3]), "value: every colour x %.2f, the "
                  "sample screen's back value" % R["value"])
    return E


# ---- the awnings ------------------------------------------------------------------------------------------------
AW = dict(a=hx("060201"), r=hx("ca463c"), rd=hx("9d2e34"), c=hx("e9ddc7"), cd=hx("bcac9e"))
TONGUE = ["aSSSSSSa",                                               # one valance tongue (rows 14-17), stamped
          ".aSSSSa.",
          "..aSSa..",
          "...aa..."]


def fix_awning(name):
    a0 = before(name); E = Edit(a0)
    h, w = a0.shape[:2]
    ink = AW["a"]
    em = edge_mask(a0)
    for x in range(w):                                              # the canvas, rows 4-13: stripes of 8 px
        k = (x // 8) % 2
        lit, dark = (AW["r"], AW["rd"]) if k == 0 else (AW["c"], AW["cd"])
        for y in range(4, 14):
            if not a0[y, x, 3]: continue
            if tuple(a0[y, x, :3]) == ink and (em[y, x] or y == 13 and (x == 0 or x == w - 1)): continue   # the outline
            if em[y, x] and y < 13: continue                        # its diagonal side edges stay as drawn
            E.set(x, y, dark if y in (4, 13) else lit, "stripes 8 px, red and cream in turn; row 4 the shadow under "
                  "the rail, row 13 the hem")
    for y in range(14, h):                                          # the valance: clear, then one tongue per stripe
        for x in range(w):
            if a0[y, x, 3]:
                E.a[y, x, 3] = 0
                E.log.append(dict(x=x, y=y, was="%02x%02x%02x" % tuple(a0[y, x, :3]), now="transparent", rule="valance redrawn"))
    for i in range(w // 8):
        k = i % 2; dark = AW["rd"] if k == 0 else AW["cd"]
        for dy, row in enumerate(TONGUE):
            for dx, ch in enumerate(row):
                if ch == ".": continue
                x, y = i * 8 + dx, 14 + dy
                rgb = ink if ch == "a" else dark
                old = E.a[y, x].copy()
                E.a[y, x] = (*rgb, 255)
                if tuple(old) != (*rgb, 255):
                    E.log.append(dict(x=x, y=y, was=("%02x%02x%02x" % tuple(old[:3])) if old[3] else "transparent",
                                      now="%02x%02x%02x" % rgb, rule="one tongue per stripe, the same part stamped"))
    for y in range(h):                                              # awning80's second red -> the one red
        for x in range(w):
            if E.a[y, x, 3] and tuple(E.a[y, x, :3]) in (hx("cd4f42"), hx("c73f36")):
                E.set(x, y, AW["r"], "one red on both awnings")
            elif E.a[y, x, 3] and tuple(E.a[y, x, :3]) == hx("9b2e34"): E.set(x, y, AW["rd"], "one red shade")
            elif E.a[y, x, 3] and tuple(E.a[y, x, :3]) == hx("bbab9d"): E.set(x, y, AW["cd"], "one cream shade")
            elif E.a[y, x, 3] and tuple(E.a[y, x, :3]) == hx("e9dec7"): E.set(x, y, AW["c"], "one cream")
    return E


# ---- the cafe table ---------------------------------------------------------------------------------------------
TABLE = {"566c97": ("7f97c4", "the top's lit edge, mid-tone"), "405070": ("5a72a0", "the top's face, mid-tone"),
         "2d1c1f": ("010100", "the top's underside: the silhouette's ink"), "1d1816": ("010100", "the legs' edges: ink"),
         "3d4a4d": ("66757c", "the legs' steel, mid-tone"), "262e30": ("4a565c", "the legs' shade, mid-tone")}


def fix_table(name):
    a0 = before(name); E = Edit(a0)
    for y, x in zip(*np.nonzero(opaque(a0))):
        c = "%02x%02x%02x" % tuple(a0[y, x, :3])
        if c in TABLE: E.set(x, y, hx(TABLE[c][0]), TABLE[c][1])
    return E


FIX = {"town_house1": fix_house, "town_house2": fix_house, "town_awning64": fix_awning, "town_awning80": fix_awning,
       "town_table_front": fix_table}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("names", nargs="*")
    o = ap.parse_args(); bad = 0
    for n in (o.names or FIX):
        E = FIX[n](n)
        p = os.path.join(SCENE, n + ".png")
        if o.check:
            ok = np.array_equal(np.array(Image.open(p).convert("RGBA")), E.a)
            print(p, "matches the fix" if ok else "DIFFERS from the fix"); bad += not ok; continue
        Image.fromarray(E.a).save(p)
        d = os.path.join(SRC, n)
        json.dump(dict(asset=n, source=f"art/source/{n}/{n}_before.png", tool="tools/fix_dt_06nov.py",
                       changed=len(E.log), edits=E.log), open(os.path.join(d, "edits.json"), "w"), indent=0)
        aseprite_io.write(os.path.join(d, n + ".aseprite"), [E.a])
        print(f"{p}: {len(E.log)} pixels changed by rule")
    sys.exit(1 if bad else 0)
