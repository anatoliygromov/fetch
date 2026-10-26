"""tools/measure_layers.py OUT.json: the layer ladder check (doc "FETCH! Asset Library by Layer", 23 Oct).
Measure every art file as it appears on screen: file -> load-time fade -> the layer's look shader.
The load-time fade goes to the level's own haze for the layer (look.lua; decision 3, 23 Oct), by the level's amount
for the layer (look.lua `fade`) unless the piece has its own amount (OWN). Ends with the ladder per level: median
and darkest (10th pct) per layer, pooled over the level's assets (python3 -I tools/measure_layers.py --ladder).
Reports on-screen lightness (Rec.601 luma 0-255, as the shader) p10 / median / p90, colours, lone pixels,
dark-edge share, ordered-dither share, size."""
import sys, json, numpy as np
from PIL import Image
import os, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "riverwalk/art/")
# batch 1 art lives on branch r8/art: extracted to a temp folder when the script runs (r8_dir(); asset_qa.py imports
# this file for its registry and maths, so nothing runs on import)
R8 = tempfile.mkdtemp(prefix="r8art_") + "/"
def r8_dir():
    REF = next((r for r in ("r8/art", "origin/r8/art") if subprocess.run(["git", "-C", ROOT, "rev-parse", "-q", "--verify", r], capture_output=True).returncode == 0), None)
    for f in (subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", REF, "riverwalk/art/r8/"], capture_output=True, text=True).stdout.split() if REF else []):
        open(R8 + os.path.basename(f), "wb").write(subprocess.run(["git", "-C", ROOT, "show", REF + ":" + f], capture_output=True).stdout)
    return R8

def hx(h): return np.array([int(h[i:i+2], 16) / 255 for i in (0, 2, 4)])
def L(warm, cool, sat, haze, k): return dict(warm=warm, cool=cool, sat=sat, haze=hx(haze), k=k)
S = {
 "rw": dict(clouds=L(0.9,1.6,1.0,"f7ead2",0.10), city=L(0.2,1.8,0.70,"aaa6d0",0.46), shore=L(0.5,1.5,1.05,"9fb3cc",0.30),
            mid=L(0.8,1.3,1.2,"c9d0d8",0.15), water=L(0.5,1.2,1.35,"8fb4d8",0.06), back=L(1.0,1.2,1.35,"f0e0c6",0.10),
            ground=L(0.75,1.3,1.20,"000000",0), play=L(0.7,0.8,1.18,"000000",0), front=L(0.0,1.8,1.10,"1b1934",0.40)),
 "cp": dict(clouds=L(1.2,1.7,1.0,"f9e0c0",0.14), city=L(0.2,1.9,0.60,"dccfe0",0.52), shore=L(0.6,1.5,1.05,"dcc0c4",0.30),
            mid=L(1.0,1.3,1.25,"ecccae",0.14), water=L(0.6,1.3,1.30,"86a2bc",0.06), back=L(1.1,1.3,1.30,"f0d2b0",0.10),
            ground=L(0.8,1.0,1.10,"000000",0), play=L(0.8,0.9,1.18,"000000",0), front=L(0.0,1.8,1.10,"1e1626",0.40)),
 "dt": dict(clouds=L(0.5,1.4,1.0,"ffffff",0.04), city=L(0.2,1.7,0.70,"a7bad6",0.50), shore=L(0.4,1.4,1.00,"b2c3d9",0.34),
            mid=L(0.7,1.3,1.15,"d6dee8",0.18), water=L(0.4,1.2,1.35,"7fb0d8",0.05), back=L(0.8,1.2,1.25,"efe6da",0.08),
            ground=L(0.9,0.7,1.10,"000000",0), play=L(0.7,0.8,1.15,"000000",0), front=L(0.0,1.8,1.10,"141a26",0.40)),
}
# the load-time fade amounts per level and layer (look.lua Look.scripts[...].fade); layers not listed are not faded
FADE = {"rw": dict(back=0.28), "cp": dict(shore=0.40, mid=0.38, back=0.20), "dt": dict(shore=0.70, mid=0.10, back=0.28)}
# pieces with their own amount (scene.lua park gate and winch keeper, arthooks.lua tram and spire); the haze is the level's
OWN = {"park_gate": 0.28, "park_keeper_winch": 0.35, "tram_vintage": 0.40, "spire_riddarholmen": 0.45}
OLD_HAZE = np.array([200, 210, 222]) / 255                        # the cool grey every fade went to before decision 3
W = np.array([0.299, 0.587, 0.114])
LEVELS = {"rw": "River Walk", "cp": "City Park", "dt": "Downtown"}

def haze(lvl, layer):
    """the load-time fade's target: the level's haze for the layer (the back haze for a layer without one)"""
    return S[lvl].get(layer or "back", S[lvl]["back"])["haze"]

def fade_in(name, lvl, layer, fade=None):
    """the amount `name` is faded by in level `lvl` (art shared between levels takes each level's amount)"""
    if layer is None: return 0.0
    if name in OWN: return OWN[name]
    return FADE[lvl].get(layer, 0.0)

def fade_to(rgb, fade, lvl, layer):
    """RGB 0-1 after the load-time fade (k of the way to the level's haze for the layer)"""
    return rgb + (haze(lvl, layer) - rgb) * fade if fade else rgb

def shade(rgb, p):
    l = rgb @ W
    rgb = l[:, None] + (rgb - l[:, None]) * p["sat"]
    rgb = rgb + p["warm"] * (l * l)[:, None] * np.array([0.080, 0.032, -0.048])
    rgb = rgb + p["cool"] * ((1 - l) ** 2)[:, None] * np.array([-0.030, -0.045, 0.085])
    rgb = rgb * (1 - p["k"]) + p["haze"] * p["k"]
    return np.clip(rgb, 0, 1)

def stats(path, lvl, layer, fade=0.0, shader=True):
    im = np.array(Image.open(path).convert("RGBA")).astype(float) / 255
    h, w, _ = im.shape
    a = im[..., 3] > 0.5
    semi = ((im[..., 3] > 0.02) & (im[..., 3] < 0.98)).sum()
    rgb = im[..., :3].copy()
    rgb = fade_to(rgb, fade, lvl, layer)
    flat = rgb[a]
    if shader and layer: flat = shade(flat, S[lvl][layer])
    lum = flat @ W * 255
    out = rgb.copy(); out[a] = flat
    # colours (on file), lone pixels: no 8-neighbour shares its exact colour
    q = (im[..., :3] * 255).round().astype(int)
    key = (q[..., 0] << 16) | (q[..., 1] << 8) | q[..., 2]
    key = np.where(a, key, -1)
    ncol = len(np.unique(key[a]))
    pad = np.pad(key, 1, constant_values=-2)
    same = np.zeros_like(a)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0: continue
            same |= pad[1+dy:1+dy+h, 1+dx:1+dx+w] == key
    lone = (a & ~same).sum() / max(1, a.sum()) * 100
    # silhouette edge: opaque pixels with a transparent 4-neighbour; dark = on-screen luma < 70
    pa = np.pad(a, 1)
    edge = a & ~(pa[:-2, 1:-1] & pa[2:, 1:-1] & pa[1:-1, :-2] & pa[1:-1, 2:])
    ol = out @ W * 255
    dark_edge = (edge & (ol < 70)).sum() / max(1, edge.sum()) * 100
    # ordered dither: 2x2 checker of exactly two colours (A B / B A) inside the art
    k00, k01, k10, k11 = key[:-1, :-1], key[:-1, 1:], key[1:, :-1], key[1:, 1:]
    chk = (k00 == k11) & (k01 == k10) & (k00 != k01) & (k00 >= 0) & (k01 >= 0)
    dither = chk.sum() / max(1, a.sum()) * 100
    return dict(w=w, h=h, p10=round(float(np.percentile(lum, 10))), med=round(float(np.median(lum))),
                p90=round(float(np.percentile(lum, 90))), ncol=ncol, lone=round(lone, 1), dark_edge=round(dark_edge),
                dither=round(dither, 1), semi=int(semi))

# asset -> (level script, layer, load-time fade) as the code draws it (corrected after QA, 23 Oct). fade True: the
# level's amount for the layer (FADE); a number: the piece's own amount (OWN); 0: not faded
A = []
def add(names, lvl, layer, fade=0.0, base=ART + "scene/", group=""):
    for n in names: A.append((group, n, base + n + ".png", lvl, layer, fade_in(n, lvl, layer) if fade else 0.0))
add(["cloud%d" % i for i in range(1, 9)], "rw", "clouds", group="River Walk")
add(["skyline"], "rw", "city", group="River Walk")
add(["far_shore_bridge"], "rw", "shore", group="River Walk")
add(["water"], "rw", "water", group="River Walk")
add(["building", "cafe", "gable", "tree", "tree_far", "tree_near", "pot", "lamp_post"], "rw", "back", True, group="River Walk")
add(["kiosk_kaffe", "kiosk_glass"], "rw", "back", True, group="River Walk")          # setpieces.lua art()
add(["rail_bg_left", "rail_bg_unit", "rail_bg_end"], "rw", "back", True, group="River Walk")   # Sc.railing decor fade
add(["pavement", "road"], "rw", "ground", group="River Walk")
add(["awning_80", "awning_88", "bench", "bin", "flowerbox_front", "gritbox_front", "planter_sq", "kennel", "ferry", "pier",
     "pontoon", "rw_jetty", "rowboat", "park_log", "road_cyclist1", "road_cyclist2",
     "road_car1", "road_car2", "road_car3", "road_car4", "road_car5"], "rw", "play", group="River Walk")
add(["pile"], "rw", "front", group="River Walk")
add(["park_treeline"], "cp", "shore", True, group="City Park")      # (art/haze: faded too)
add(["park_tree1", "park_tree2"], "cp", "mid", True, group="City Park")
add(["park_oak", "park_willow", "park_willow_tall", "park_gate", "park_swings"], "cp", "back", True, group="City Park")
add(["park_keeper_winch"], "cp", "back", True, group="City Park")   # scene.lua WINCH (art/fixes), its own 35 %
add(["park_leaves"], "cp", "play", group="City Park")
add(["park_slide"], "cp", "ground", group="City Park")   # unfaded art under the back shader
add(["park_ground"], "cp", "ground", group="City Park")
add(["park_hedge", "park_log", "park_hollowlog", "park_table_front", "park_stone", "park_boat_front", "park_frame",
     "park_keeper_cart"], "cp", "play", group="City Park")
add(["park_bush"], "cp", "front", group="City Park")
add(["town_roofs"], "dt", "shore", True, group="Downtown")
add(["town_facades"], "dt", "mid", True, group="Downtown")
add(["town_door", "town_sign", "town_spout"], "dt", "back", True, group="Downtown")
add(["town_house1", "town_house2", "town_house3"], "dt", "back", True, group="Downtown")   # art/fixes, decision 4
add(["town_statue"], "dt", "play", group="Downtown")   # art/fixes: tagged play
add(["town_ground"], "dt", "ground", group="Downtown")
add(["town_tramshed70", "town_tramshed96", "town_crate_front", "town_parasol", "town_table_front", "town_stall", "town_awning80",
     "town_awning64", "town_pedestal", "town_shelter", "town_kiosk", "town_tub", "town_rim", "town_bowl", "town_tier",
     "town_shopsign"], "dt", "play", group="Downtown")
add(["town_bollard"], "dt", "front", group="Downtown")
add(["pepper", "girl", "cat", "goose", "gull", "ball"], "rw", None, base=ART, group="Characters (never shaded)")
add(["facades_square"], "dt", "mid", True, base=R8, group="Batch 1 (rejected)")
add(["spire_riddarholmen"], "dt", "back", True, base=R8, group="Batch 1 (rejected)")     # arthooks.lua drawTownBack, own 45 %
add(["house_tall_a", "house_tall_b", "house_tall_c"], "dt", "back", True, base=R8, group="Batch 1 (rejected)")
add(["tram_vintage"], "dt", "back", True, base=R8, group="Batch 1 (rejected)")           # arthooks.lua TRAM_FADE, own 40 %
add(["cyclist_a_84", "cyclist_b_84", "cyclist_a_92", "cyclist_b_92"], "rw", "play", base=R8, group="Batch 1 (rejected)")
add(["cargobike", "roof_gable", "roof_chimney", "roof_loggia", "roof_gallery72", "roof_gallery88", "roof_dormer",
     "roof_ledge32", "roof_awning56", "footbridge"], "dt", "play", base=R8, group="Batch 1 (rejected)")
add(["mia_throw"], "rw", None, base=R8, group="Batch 1 (rejected)")

# the ladder per level: each layer pooled over the level's own assets as drawn (the clouds and the skyline are the sky
# and the far city of all three), and the sky's horizon (its painted bands from y 76 down, behind the far layers).
# Batch 1 (not in the game) and the characters are left out.
LADDER_LAYERS = ("clouds", "city", "shore", "mid", "back", "play")
def sky_luma(lvl):
    key = {"rw": "riverwalk", "cp": "citypark", "dt": "downtown"}[lvl]
    src = open(os.path.join(ROOT, "riverwalk/look.lua")).read()
    blk = src.split(key + " = {", 1)[1].split("bands = {", 1)[1].split("fg = ", 1)[0].split("above = ", 1)[0]
    import re
    bands = [(int(y), h) for y, h in re.findall(r'\{\s*(\d+),\s*"([0-9a-f]{6})"\s*\}', blk)]
    rows = []
    for i, (y, h) in enumerate(bands):
        y1 = bands[i + 1][0] if i + 1 < len(bands) else 240
        rows += [hx(h) @ W * 255] * max(0, y1 - max(y, 76))
    return np.array(rows)

def drawn_luma(path, lvl, layer, fade):
    im = np.array(Image.open(path).convert("RGBA")).astype(float) / 255
    rgb = fade_to(im[..., :3][im[..., 3] > 0.5], fade, lvl, layer)
    return shade(rgb, S[lvl][layer]) @ W * 255

def ladder():
    out = {}
    for lvl, grp in LEVELS.items():
        pools = {"horizon": [sky_luma(lvl)]}
        for g, n, p, l, layer, fade in A:
            if n == "skyline": pools.setdefault("city", []).append(drawn_luma(p, lvl, "city", 0.0))
            elif n.startswith("cloud"): pools.setdefault("clouds", []).append(drawn_luma(p, lvl, "clouds", 0.0))
            elif g == grp and layer in LADDER_LAYERS and os.path.exists(p): pools.setdefault(layer, []).append(drawn_luma(p, lvl, layer, fade))
        out[lvl] = {k: (round(float(np.median(np.concatenate(v)))), round(float(np.percentile(np.concatenate(v), 10))))
                    for k, v in pools.items()}
    return out

if __name__ == "__main__" and "--ladder" in sys.argv:
    for lvl, row in ladder().items():
        ks = [k for k in LADDER_LAYERS if k in row]
        bad = [f"{a}>{b} {('median', 'darkest')[i]}" for a, b in zip(ks, ks[1:]) for i in (0, 1) if row[a][i] <= row[b][i]]
        print(f"{LEVELS[lvl]:10} median/darkest " + "  ".join(f"{k} {row[k][0]}/{row[k][1]}" for k in ["horizon"] + ks)
              + ("  light to dark" if not bad else "  NOT light to dark: " + ", ".join(bad)))
    sys.exit(0)

if __name__ == "__main__":
    r8_dir()
    rows = []
    for g, n, p, lvl, layer, fade in A:
        try: s = stats(p, lvl, layer, fade, shader=layer is not None)
        except Exception as e: print("skip", n, e, file=sys.stderr); continue
        s.update(group=g, name=n, lvl=lvl, layer=layer or "char", fade=fade); rows.append(s)
    json.dump(rows, open(sys.argv[1], "w"), indent=0)
    for r in rows:
        print(f"{r['group'][:10]:10} {r['name']:20} {r['layer']:6} f{r['fade']:.2f} {r['w']:4}x{r['h']:<4} "
              f"L {r['p10']:3}/{r['med']:3}/{r['p90']:3} col {r['ncol']:3} lone {r['lone']:5} edgeDk {r['dark_edge']:3}% dith {r['dither']:4} semi {r['semi']}")
