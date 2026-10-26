#!/usr/bin/env python3
"""The real game frames of a level, every screen at each height tier, as a contact sheet (25 Oct 2026).

  python3 -I tools/layer_frames_tall.py LEVEL OUTDIR [--step 320] [--ids] [--frames DIR]

1. Runs the look sweep (riverwalk/tests_look.lua, LOOK_SWEEP=1): the camera steps LOOK_STEP px along the level at
   each height tier (a tall level: the bottom of the world, then every 120 px up, then the top), look on, no HUD,
   Pepper on the highest floor at the camera + 140. Its own save folder (XDG_DATA_HOME=$(mktemp -d)) each run.
2. OUTDIR/contact.png: the frames at 1x, one row per height tier (the top of the world first), screens left to
   right. OUTDIR/contact_grey.png: the same in greyscale (Rec.601 luma, as the look shader and
   tools/measure_layers.py), to judge the light-to-dark order of the layers.
3. --ids: the same sweep again in a temp copy of riverwalk/ with tools/layer_ids_hook.lua, which turns each pass
   of St:draw into a flat layer number, so every pixel of every frame is known to be sky, clouds, far city, tree
   line, mid, water, back, ground, play, front or a character (bones, Mia, Pepper). OUTDIR/layers.json: per tier
   and per frame, each layer's share of the screen and its luma p10 / median / p90 in the colour frame, and the
   ladder pooled per tier. OUTDIR/frames/ (or --frames DIR) keeps the 1x frames and the id maps (id_*.png, red
   channel = id x 20).
The game in the repo is never changed; the copy for --ids lives in a temp folder and is removed.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {1: "sky", 2: "clouds", 3: "far city", 4: "tree line", 5: "mid", 6: "water", 7: "back", 8: "ground", 9: "play",
         10: "front", 11: "characters", 12: "other"}
ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def sweep(level, step, game_dir, env_extra=None):
    data = tempfile.mkdtemp(prefix="xdg_")
    env = dict(os.environ, LOOK_SWEEP="1", LOOK_STEP=str(step), SDL_AUDIODRIVER="dummy", XDG_DATA_HOME=data)
    env.update(env_extra or {})
    r = subprocess.run(["timeout", "300", "xvfb-run", "-a", "love", game_dir, "--level", level, "--lookshots"],
                       cwd=os.path.dirname(game_dir), env=env, capture_output=True, text=True)
    out = [l for l in r.stdout.splitlines() if l.startswith("SWEEP") or l.startswith("[layer ids]")]
    files = sorted(glob.glob(os.path.join(data, "love", "*", "sweep_*.png")))
    return files, data, out


def parse(f):
    b = os.path.basename(f)[:-4].split("_")              # sweep_<name>_y<cy>_x<cx>
    return int(b[-2][1:]), int(b[-1][1:])


def sheet(files, grey, out, title):
    tiers = sorted({parse(f)[0] for f in files})
    xs = sorted({parse(f)[1] for f in files})
    font = ImageFont.load_default()
    gap, head, left = 4, 16, 0
    S = Image.new("RGB", (len(xs) * (320 + gap) - gap, 22 + len(tiers) * (240 + head + gap)), (24, 24, 28))
    d = ImageDraw.Draw(S)
    d.text((4, 5), title, fill=(230, 230, 230), font=font)
    for r, cy in enumerate(tiers):
        y = 22 + r * (240 + head + gap)
        for c, cx in enumerate(xs):
            f = next(f for f in files if parse(f) == (cy, cx))
            im = Image.open(f).convert("RGB")
            if grey:
                im = im.convert("L").convert("RGB")
            x = left + c * (320 + gap)
            d.text((x + 2, y + 2), f"screen {c + 1}  x {cx}-{cx + 320}  camera y {cy}", fill=(210, 210, 210), font=font)
            S.paste(im, (x, y + head))
    S.save(out)
    return tiers, xs


def luma(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def stats(colour_files, id_files):
    by = {parse(f): f for f in id_files}
    res = {"frames": [], "tiers": {}}
    pool, count = {}, {}
    for f in colour_files:
        key = parse(f)
        if key not in by:
            continue
        c = np.asarray(Image.open(f).convert("RGB")).astype(float)
        ids = np.rint(np.asarray(Image.open(by[key]).convert("RGB"))[..., 0] / 20).astype(int)
        L = luma(c)
        count[key[0]] = count.get(key[0], 0) + 1
        fr = {"camera_y": key[0], "x": key[1], "layers": {}}
        for i in ORDER:
            m = ids == i
            n = int(m.sum())
            if n == 0:
                continue
            v = L[m]
            fr["layers"][NAMES[i]] = {"share": round(n / m.size, 3), "p10": round(float(np.percentile(v, 10))),
                                      "median": round(float(np.median(v))), "p90": round(float(np.percentile(v, 90)))}
            pool.setdefault(key[0], {}).setdefault(i, []).append(v)
        res["frames"].append(fr)
    for cy, d in sorted(pool.items()):
        res["tiers"][str(cy)] = {NAMES[i]: {"p10": round(float(np.percentile(np.concatenate(v), 10))),
                                            "median": round(float(np.median(np.concatenate(v)))),
                                            "share": round(float(sum(len(x) for x in v)) / (count[cy] * 320 * 240), 3)}
                                 for i, v in sorted(d.items())}
    return res


def main():
    level, outdir = sys.argv[1], sys.argv[2]
    step = int(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 320
    fdir = sys.argv[sys.argv.index("--frames") + 1] if "--frames" in sys.argv else os.path.join(outdir, "frames")
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    files, data, out = sweep(level, step, os.path.join(ROOT, "riverwalk"))
    print(*out)
    if not files:
        sys.exit("no frames: the sweep did not run")
    kept = []
    for f in files:
        dst = os.path.join(fdir, os.path.basename(f))
        shutil.copy(f, dst)
        kept.append(dst)
    shutil.rmtree(data, ignore_errors=True)
    title = f"{level}: the game's frames (look on, no HUD), every screen at each camera height; LOOK_SWEEP=1 LOOK_STEP={step}"
    tiers, xs = sheet(kept, False, os.path.join(outdir, "contact.png"), title)
    sheet(kept, True, os.path.join(outdir, "contact_grey.png"), title + " (greyscale, Rec.601 luma)")
    print("contact sheets:", len(tiers), "tiers x", len(xs), "screens")
    if "--ids" in sys.argv:
        tmp = tempfile.mkdtemp(prefix="layerids_")
        game = os.path.join(tmp, "riverwalk")
        shutil.copytree(os.path.join(ROOT, "riverwalk"), game)
        shutil.copy(os.path.join(ROOT, "tools", "layer_ids_hook.lua"), os.path.join(game, "layer_ids_hook.lua"))
        t = os.path.join(game, "tests_look.lua")
        src = open(t).read()
        open(t, "w").write('if os.getenv("LAYER_IDS") then require("layer_ids_hook") end\n' + src)
        ids, data, out = sweep(level, step, game, {"LAYER_IDS": "1"})
        print(*out)
        id_kept = []
        for f in ids:
            dst = os.path.join(fdir, "id_" + os.path.basename(f))
            shutil.copy(f, dst)
            id_kept.append(dst)
        shutil.rmtree(data, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
        idf = [f for f in id_kept]
        # (the id maps are named id_sweep_..., parse() reads the last two fields, so they line up with the colour frames)
        res = stats(kept, idf)
        json.dump(res, open(os.path.join(outdir, "layers.json"), "w"), indent=1)
        print("layers.json:", len(res["frames"]), "frames")
        for cy, d in res["tiers"].items():
            print("camera y", cy, "  ".join(f"{k} {v['median']}/{v['p10']} ({v['share'] * 100:.0f} %)" for k, v in d.items()))


if __name__ == "__main__":
    main()
