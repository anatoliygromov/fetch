#!/usr/bin/env python3
"""scale_gate.py --job NAME RENDER.png [RENDER2.png ...]: the scale gate on a paid render (6 Nov 2026).

Why: on 6 Nov Nano Banana 2.1 renders on a blockout came back with Pepper at 1x but the subject 1.3x to 4x too big
(cargo bike rider 152 px against Pepper's 38; tub 2.4x; hedge 3x), and one came back on a half-size grid (tram,
Pepper 19 px). The owner saw it ("you're spending SpriteCook credits on assets with wrong scale"). Nothing measured
the render before more credits went in. Run this on every render BEFORE any cut, retry or further paid job.

What it does, per render (0 credits, no resampling of game pixels: it only measures):
  1. k = render width / blockout frame width (whole number, or FAIL).
  2. Samples the render at the centre of every k x k cell (measuring only).
  3. Background = magenta (#FF00FF family) or transparent.
  4. Pepper: the dark pixels in a window around where she sits in the blockout. Her box must be her real sprite's
     size (52 x 38) within 2 px. Missing or wrong size = FAIL (the render is not on the blockout's scale).
  5. Subject: every other non-background pixel. Its box must be within 10 % of the blockout mask's box in width
     and height (crowns cut by the top edge: the height check uses the mask's height).
Exit 1 on any FAIL. A FAIL render is rejected in the ledger (tools/ledger.py verdict ... rejected) and the next job
must change the method, not repeat it (docs/art_learnings.md)."""
import sys, os, json, argparse
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

R = json.load(open('art/gen/rules.json'))
TOL_PEPPER = 2
TOL_SUBJ = 0.10


def pepper_sprite():
    p = R['pepper']
    sp = np.array(Image.open(p['file']).convert('RGBA'))[p['cell'][1]:p['cell'][3], p['cell'][0]:p['cell'][2]]
    ys, xs = np.nonzero(sp[..., 3]); return sp[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def find_pepper(bo):
    sp = pepper_sprite(); h, w = sp.shape[:2]; on = sp[..., 3] > 0
    for y in range(bo.shape[0] - h + 1):
        for x in range(min(bo.shape[1] - w + 1, 60)):            # Pepper stands at the left (preflight)
            if np.array_equal(bo[y:y + h, x:x + w][on][:, :3], sp[on][:, :3]):
                return x, y, w, h
    return None


def bg_mask(a):
    r, g, b, al = [a[..., i].astype(int) for i in range(4)]
    return (al < 128) | ((r > 180) & (g < 90) & (b > 180))


def gate(name, render):
    bo = np.array(Image.open(f'art/gen/blockouts/{name}.png').convert('RGBA'))
    mk = np.array(Image.open(f'art/gen/blockouts/{name}_mask.png').convert('L')) > 127
    fh, fw = bo.shape[:2]
    im = Image.open(render).convert('RGBA'); W, H = im.size
    out = []
    if W % fw or H % fh or W // fw != H // fh:
        return [f"FAIL grid: render {W}x{H} is not a whole multiple of the {fw}x{fh} frame"]
    k = W // fw
    a = np.array(im)[k // 2::k, k // 2::k]
    bg = bg_mask(a)
    pp = find_pepper(bo)
    if not pp: return ["FAIL blockout: Pepper's real sprite is not in the blockout"]
    px, py, pw, ph = pp
    win = np.zeros_like(bg); win[max(0, py - 8):py + ph + 8, max(0, px - 8):px + pw + 8] = True
    lum = a[..., :3].astype(float) @ [0.299, 0.587, 0.114]
    dog = win & ~bg & (lum < 90)
    if not dog.any():
        out.append(f"FAIL pepper: no dog where she sits in the blockout (k {k})")
    else:
        ys, xs = np.nonzero(dog); dw, dh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        ok = abs(dw - pw) <= TOL_PEPPER and abs(dh - ph) <= TOL_PEPPER
        out.append(f"{'PASS' if ok else 'FAIL'} pepper: {dw}x{dh} in the render, {pw}x{ph} in the blockout (k {k})")
    subj = ~bg & ~win
    my, mx = np.nonzero(mk)
    tw, th = mx.max() - mx.min() + 1, my.max() - my.min() + 1
    if not subj.any():
        out.append("FAIL subject: nothing drawn outside Pepper's window")
    else:
        ys, xs = np.nonzero(subj); sw, sh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        rw, rh = sw / tw, sh / th
        ok = abs(rw - 1) <= TOL_SUBJ and abs(rh - 1) <= TOL_SUBJ
        out.append(f"{'PASS' if ok else 'FAIL'} subject: {sw}x{sh} against the mask's {tw}x{th} ({rw:.2f}x, {rh:.2f}x)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--job', required=True); ap.add_argument('renders', nargs='+')
    o = ap.parse_args()
    bad = 0
    for r in o.renders:
        lines = gate(o.job, r)
        v = 'FAIL' if any(l.startswith('FAIL') for l in lines) else 'PASS'
        bad += v == 'FAIL'
        print(f"SCALE {v} {o.job} {os.path.basename(r)}")
        for l in lines: print("   " + l)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
