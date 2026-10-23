"""tools/freefix.py: the 0-credit fix pass over the "Fix free" list of docs/asset_qa_triage.md (art/freefix, 23 Oct).

  python3 -I tools/freefix.py OUT_DIR [names]      re-runs every recipe from the files at BASE (so it can be repeated)

Per asset, in this order: stamp windows (buildings, tools/stamp_windows.py), blotch clean (tools/blotch_clean.py),
clean pass (tools/cleanpass.py), outline completion (tools/outline_complete.py), then the small pixel patches below,
then tools/asset_qa.py. Writes the fixed file in place and OUT_DIR/<name>_before_after.png (5x, neutral grey).
The owner's rules: no resize or resample, no new colours, alpha stays binary, sizes stay; Pepper's files untouched.

Patches (each takes the pixels asset_qa.py flags, nothing else):
  pinholes   a 1-4 px gap between two parts (arm and body) takes the outline ink: at 2x a gap that small reads as dirt
  specks     a free-floating bit of 1-8 px is removed (made transparent)
  flicker    a colour used in one frame only, 3 px or less, takes the colour most of its neighbours have
  merge      one colour becomes another colour already in the file (the layer ladder)
"""
import sys, os, subprocess, shutil, tempfile
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_qa as Q

BASE = "9d29233"
T = "python3 -I " + HERE + "/"
# recipe per asset: (steps, note). Steps: stamp[:args] blotch[:args] clean[:args] outline[:args] pinholes specks
# flicker merge:RRGGBB>RRGGBB. Approved River Walk art is marked APPROVED (the owner signs off the change).
RECIPES = {
    # buildings (stamped windows)
    "town_house1": ("stamp:--across-storeys --near|blotch|clean", "windows stamped (one window per wall, the attic bar 2 px for equal panes)"),
    "town_house2": ("stamp:--across-storeys --near|blotch|clean", "windows stamped (one window per wall)"),
    "town_house3": ("stamp|blotch|clean|outline:--skip-bottom", "windows stamped per storey; decoration outline completed"),
    "town_facades": ("", "not changed: the painted strip's windows need a redraw (the stamp made them worse)"),
    "building": ("blotch|clean", "APPROVED"),
    "cafe": ("blotch|clean", "APPROVED; windows not stamped (painted glass)"),
    "gable": ("blotch", "APPROVED; windows not stamped (painted glass)"),
    # City Park
    "park_gate": ("blotch|clean|outline:--skip-bottom", "decoration drawn with an outline: completed"),
    "park_hedge": ("clean:--tol 40|outline:--skip-bottom", "organic: light clean pass; play piece outline completed"),
    "park_keeper_cart": ("blotch|outline:--skip-bottom --frames 82x82|pinholes", "outline completed per frame"),
    "park_keeper_winch": ("blotch|outline:--skip-bottom --frames 80x80|pinholes", "decoration drawn with an outline: completed"),
    "park_leaves_flat": ("clean", "organic: clean pass"),
    # Downtown
    "town_awning64": ("outline:--skip-bottom|clean", ""),
    "town_awning80": ("outline:--skip-bottom", ""),
    "town_bollard": ("", "not changed: median 41 on screen, the front layer allows 40 (a code value, not a pixel fix)"),
    "town_door": ("blotch:--border|clean", "the sill on the ground line cleaned too"),
    "town_kiosk": ("blotch|clean|outline:--skip-bottom", ""),
    "town_parasol": ("clean|outline:--skip-bottom", ""),
    "town_pedestal": ("blotch", ""),
    "town_roofs": ("blotch|clean", ""),
    "town_shelter": ("blotch", ""),
    "town_stall": ("blotch|clean", ""),
    "town_statue": ("blotch|clean", ""),
    "town_table_front": ("outline:--skip-bottom", ""),
    "town_tramshed70": ("blotch", ""),
    "town_tramshed96": ("blotch", ""),
    # River Walk
    "cloud8": ("merge:a1b5cb>aec1d4|clean", "the darkest shade merged into the next one (ladder)"),
    "ferry": ("blotch|clean|merge:1a1e23>1a1d24|merge:272c31>263032|merge:272e32>263032|merge:3872aa>3572af",
              "4 near-duplicate colours merged (distance 1-6); outline not completed: inking the 1 px railings, mast and flag "
              "clutters the upper deck (tried, reverted); the pinholes are railing gaps"),
    "park_log": ("blotch|clean", ""),
    "pier": ("blotch|outline:--skip-bottom", "decoration drawn with an outline: completed"),
    "pile": ("blotch", ""),
    "rail_bg_unit": ("blotch:--wrap", ""),
    "road_car1": ("blotch|clean", ""),
    "road_car4": ("blotch|clean", ""),
    "road_cyclist1": ("blotch|clean", ""),
    "road_cyclist1_roll": ("blotch|clean", "the pinhole is a gap between spokes: left"),
    "road_cyclist2": ("blotch|clean|specks", ""),
    "road_cyclist2_roll": ("blotch|clean|specks", ""),
    "rowboat": ("blotch|flicker|clean", ""),
    "skyline": ("clean:--tol 40|specks", "organic: light clean pass"),
    "gull": ("flicker|clean:--tol 40", "character: defects only"),
}

def qa(name, path, d):
    return Q.check(name, path, d["level"], d["layer"], d["fade"], d["building"], d["frames"], d.get("levels"))

def pixels(rep, cid, word=""):
    return [tuple(p) for c in rep.checks if c["id"] == cid and c["sev"] == "fail" and word in c["msg"] for p in c["pixels"]]

def ink_of(im):
    a = im[..., 3] > 127
    e = Q.edge_mask(a); lum = im[..., :3] @ Q.W601
    cols, n = np.unique(im[e & (lum < 70)][:, :3], axis=0, return_counts=True)
    return cols[n.argmax()]

def patch(step, name, path, d):
    im = np.array(Image.open(path).convert("RGBA")); n = 0
    rep = qa(name, path, d)
    if step == "pinholes":
        ink = ink_of(im)
        for x, y in pixels(rep, "pinholes"): im[y, x, :3] = ink; im[y, x, 3] = 255; n += 1
    elif step == "specks":
        for x, y in pixels(rep, "specks"): im[y, x, 3] = 0; im[y, x, :3] = 0; n += 1
    elif step == "flicker":
        a = im[..., 3] > 127
        for x, y in pixels(rep, "frames", "flicker"):
            nb = Counter(tuple(im[yy, xx, :3]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
                         if (yy, xx) != (y, x) and 0 <= yy < im.shape[0] and 0 <= xx < im.shape[1] and a[yy, xx]
                         and tuple(im[yy, xx, :3]) != tuple(im[y, x, :3]))
            if nb: im[y, x, :3] = nb.most_common(1)[0][0]; n += 1
    elif step.startswith("merge:"):
        src, dst = step[6:].split(">")
        s = np.array([int(src[i:i + 2], 16) for i in (0, 2, 4)]); t = np.array([int(dst[i:i + 2], 16) for i in (0, 2, 4)])
        m = (im[..., :3] == s).all(2) & (im[..., 3] > 127)
        assert ((im[..., :3] == t).all(2) & (im[..., 3] > 127)).any(), "merge target not in the file"
        im[m, :3] = t; n = int(m.sum())
    Image.fromarray(im).save(path)
    return f"{step}: {n} px"

def ba(before, after, out, z=5):
    b, a = Image.open(before).convert("RGBA"), Image.open(after).convert("RGBA")
    def on(im):
        bg = Image.new("RGBA", im.size, (128, 128, 132, 255)); bg.alpha_composite(im)
        return bg.convert("RGB").resize((im.width * z, im.height * z), Image.NEAREST)
    B, A = on(b), on(a); g = 16
    o = Image.new("RGB", (B.width * 2 + g * 3, B.height + g * 2 + 16), (72, 72, 76))
    dr = ImageDraw.Draw(o); dr.text((g, 4), "before", fill=(230, 230, 230)); dr.text((B.width + 2 * g, 4), "after", fill=(230, 230, 230))
    o.paste(B, (g, 20)); o.paste(A, (B.width + 2 * g, 20)); o.save(out)

def main():
    out = sys.argv[1]; only = sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    reg = Q.registry(); tmp = tempfile.mkdtemp(prefix="freefix_")
    for name, (steps, note) in RECIPES.items():
        if only and name not in only: continue
        d = reg[name]; path = d["path"]; rel = os.path.relpath(path, Q.ROOT)
        orig = os.path.join(tmp, name + "_orig.png")
        open(orig, "wb").write(subprocess.run(["git", "-C", Q.ROOT, "show", f"{BASE}:{rel}"], capture_output=True, check=True).stdout)
        shutil.copy(orig, path)
        log = []
        sts = [s for s in steps.split("|") if s]
        if any(s.startswith("blotch") for s in sts) and any(s.startswith("clean") for s in sts):
            sts.append(next(s for s in sts if s.startswith("blotch")))   # again: a clean pass can leave a patch
        for st in sts:
            kind, _, args = st.partition(":")
            tool = {"stamp": "stamp_windows.py", "blotch": "blotch_clean.py", "clean": "cleanpass.py", "outline": "outline_complete.py"}.get(kind)
            if tool:
                if kind == "clean" and name in Q.TILES and "--wrap" not in args: args += " --wrap"
                r = subprocess.run(f"{T}{tool} {path} {path} {args}", shell=True, capture_output=True, text=True)
                if r.returncode: raise SystemExit(r.stdout + r.stderr)
                log.append(f"{kind}: " + r.stdout.strip().splitlines()[-1].split(".png", 1)[-1].strip())
            else:
                log.append(patch(st, name, path, d))
        im0, im1 = np.array(Image.open(orig).convert("RGBA")), np.array(Image.open(path).convert("RGBA"))
        assert im0.shape == im1.shape and (im0[..., 3] > 127).sum() >= 0
        a0 = im0[..., 3] > 127
        c0 = set(map(tuple, im0[a0][:, :3].tolist())); c1 = set(map(tuple, im1[im1[..., 3] > 127][:, :3].tolist()))
        assert c1 <= c0, f"{name}: new colours"
        assert set(np.unique(im1[..., 3]).tolist()) <= {0, 255} or set(np.unique(im1[..., 3]).tolist()) == set(np.unique(im0[..., 3]).tolist())
        r = qa(name, path, d); r0 = qa(name, orig, d)
        f0 = sorted({c["id"] for c in r0.checks if c["sev"] == "fail"}); f1 = sorted({c["id"] for c in r.checks if c["sev"] == "fail"})
        w1 = sorted({c["id"] for c in r.checks if c["sev"] == "warn"})
        changed = int((im0 != im1).any(2).sum())
        if changed: ba(orig, path, os.path.join(out, f"{name}_before_after.png"))
        print(f"{name:20} {r0.verdict()} -> {r.verdict():4}  fails {','.join(f0) or '-'} -> {','.join(f1) or '-'}  warns {','.join(w1) or '-'}  "
              f"{changed} px  [{'; '.join(log)}]" + (f"  ({note})" if note else ""), flush=True)

if __name__ == "__main__":
    main()
