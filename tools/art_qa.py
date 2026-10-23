"""Art QA (docs/asset_plan_22oct.md section 3.3): checks every proposal against the owner's rules.

  python3 tools/art_qa.py                  checks the batch 1 files in riverwalk/art/r8/ against SPEC below
  python3 tools/art_qa.py FILE ROLE [W H]  checks one file; ROLE is obstacle, decoration or character

Per file (per frame for clip sheets):
  size      the file's size against the target (exact W x H, or W or H alone when the other follows the art; +-10 %
            when the target is an "about" size, marked ~)
  colours   the number of opaque colours against the role's limit (obstacle 6-20, decoration 6-16, character <= 24)
  outline   share of silhouette pixels that are dark (luma under 72): obstacles and characters 95 % or more,
            decoration under 10 %
  lone      share of opaque pixels with no same-colour 8-neighbour (under 8 %, decoration and foliage under 12 %)
  isolated  opaque pixels with no opaque 8-neighbour at all: must be 0
  alpha     pixels that are neither fully transparent nor fully opaque: must be 0
  matte     silhouette pixels in the animator's grey (#7e7e7e +-8, unsaturated): must be 0
Prints one line per file and FAIL lines; exit code 1 if anything failed."""
import os
import sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R8 = os.path.join(ROOT, "riverwalk", "art", "r8")
DARK = 72
LIMITS = {"obstacle": (6, 20), "decoration": (6, 16), "character": (2, 24)}

# file: (role, target w, target h, frames). None = follows the art; a string "~N" = about N (+-10 %)
SPEC = {
    "cyclist_a_84.png": ("character", None, 84, 1), "cyclist_b_84.png": ("character", None, 84, 1),
    "cyclist_a_92.png": ("character", None, 92, 1), "cyclist_b_92.png": ("character", None, 92, 1),
    "cyclist_a_84_pedal.png": ("character", None, 84, 8), "cyclist_b_84_pedal.png": ("character", None, 84, 8),
    "cyclist_a_92_pedal.png": ("character", None, 92, 8), "cyclist_b_92_pedal.png": ("character", None, 92, 8),
    "mia_throw.png": ("character", None, "~60", 8),
    "cargobike.png": ("obstacle", "~96", "~76", 1), "cargobike_pedal.png": ("obstacle", "~96", "~76", 8),
    "tram_vintage.png": ("decoration", "~300", 130, 1),
    "roof_loggia.png": ("obstacle", 120, None, 1), "roof_gallery88.png": ("obstacle", 88, None, 1),
    "roof_gallery72.png": ("obstacle", 72, None, 1), "roof_gable.png": ("obstacle", 148, None, 1),
    "roof_chimney.png": ("obstacle", 24, "~56", 1), "roof_dormer.png": ("obstacle", 56, None, 1),
    "roof_awning56.png": ("obstacle", 56, None, 1), "roof_ledge32.png": ("obstacle", 32, 8, 1),
    "roof_ledge48.png": ("obstacle", 48, 8, 1), "roof_ledge64.png": ("obstacle", 64, 8, 1),
    "house_tall_a.png": ("decoration", "~90", 240, 1), "house_tall_b.png": ("decoration", "~90", 240, 1),
    "house_tall_c.png": ("decoration", "~90", 240, 1), "facades_square.png": ("decoration", None, 130, 1),
    "footbridge.png": ("obstacle", 160, None, 1), "spire_riddarholmen.png": ("decoration", None, 400, 1),
}


def size_ok(have, want):
    if want is None: return True
    if isinstance(want, str):
        w = float(want[1:])
        return abs(have - w) <= 0.10 * w
    return have == want


def check_frame(a, role):
    op = a[..., 3] > 0
    alpha = int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum())
    cols = a[op][:, :3]
    ncol = len(np.unique(cols, axis=0)) if len(cols) else 0
    pad = np.pad(op, 1)
    sil = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    lum = a[..., :3].astype(float) @ [0.299, 0.587, 0.114]
    dark = (sil & (lum < DARK)).sum() / max(1, sil.sum())
    key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
    key[~op] = -1
    H, W = op.shape
    kp = np.pad(key, 1, constant_values=-2)
    same = np.zeros_like(op)
    anyn = np.zeros_like(op)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0: continue
            nb = kp[1 + dy:H + 1 + dy, 1 + dx:W + 1 + dx]
            same |= nb == key
            anyn |= nb >= 0
    lone = (op & ~same).sum() / max(1, op.sum())
    isolated = int((op & ~anyn).sum())
    rgb = a[..., :3].astype(int)
    matte = int((sil & ((rgb.max(-1) - rgb.min(-1)) < 8) & (np.abs(rgb[..., 0] - 126) <= 8)).sum())
    return dict(ncol=ncol, dark=dark, lone=lone, isolated=isolated, alpha=alpha, matte=matte)


def check(path, role, tw=None, th=None, frames=1):
    a = np.array(Image.open(path).convert("RGBA"))
    H, W = a.shape[:2]
    fw = W // frames
    fails = []
    if not size_ok(fw, tw): fails.append("width %d (target %s)" % (fw, tw))
    if not size_ok(H, th): fails.append("height %d (target %s)" % (H, th))
    rs = [check_frame(a[:, i * fw:(i + 1) * fw], role) for i in range(frames)]
    ncol = len(np.unique(a[a[..., 3] > 0][:, :3], axis=0))
    lo, hi = LIMITS[role]
    if not lo <= ncol <= hi: fails.append("%d colours (%s %d-%d)" % (ncol, role, lo, hi))
    dark = min(r["dark"] for r in rs) if role != "decoration" else max(r["dark"] for r in rs)
    if role == "decoration" and dark >= 0.10: fails.append("outline %.0f %% dark (decoration < 10 %%)" % (100 * dark))
    if role != "decoration" and dark < 0.95: fails.append("outline %.0f %% dark (needs 95 %%)" % (100 * dark))
    lone = max(r["lone"] for r in rs)
    lim = 0.12 if role == "decoration" else 0.08
    if lone >= lim: fails.append("lone pixels %.1f %% (< %d %%)" % (100 * lone, 100 * lim))
    for k in ("isolated", "alpha", "matte"):
        v = sum(r[k] for r in rs)
        if v: fails.append("%s %d" % (k, v))
    line = "%-26s %-10s %4d x %-4d %s %2d col  outline %3.0f%%  lone %4.1f%%  %s" % (
        os.path.basename(path), role, fw, H, "x%d" % frames if frames > 1 else "  ", ncol, 100 * dark, 100 * lone,
        "PASS" if not fails else "FAIL: " + "; ".join(fails))
    return line, fails


def main():
    bad = 0
    if len(sys.argv) > 2:
        tw = sys.argv[3] if len(sys.argv) > 3 else None
        th = sys.argv[4] if len(sys.argv) > 4 else None
        conv = lambda v: None if v is None else (v if v.startswith("~") else int(v))
        line, fails = check(sys.argv[1], sys.argv[2], conv(tw), conv(th))
        print(line)
        return 1 if fails else 0
    for name, (role, tw, th, n) in SPEC.items():
        p = os.path.join(R8, name)
        if not os.path.exists(p):
            print("%-26s MISSING" % name); bad += 1; continue
        line, fails = check(p, role, tw, th, n)
        print(line)
        bad += bool(fails)
    print("%d of %d files pass" % (len(SPEC) - bad, len(SPEC)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
