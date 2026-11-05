#!/usr/bin/env python3
"""tools/dt_sample_board.py BEFORE_DIR AFTER_DIR OUT_DIR: the Downtown sample screen's board images (art/dt-sample-05nov).

BEFORE_DIR / AFTER_DIR hold tools/dt_sample_frames.sh frames (sweep_downtown_y<cy>_x<cx>.png, 1x) of the base and of
this branch. Writes to OUT_DIR:
  dt_sample_s7_ba.png        screen 7 (camera x 1920) at 3x, before | after, high road (y 120) over street (y 240)
  dt_sample_s7_sheet.png     screen 7 after: colour | greyscale (Rec.601 luma, as the look shader) at 3x, then 1x
  dt_sample_hiding_ba.png    the gateway and the shelter (camera x 1840), street, and the guild house (x 1560), high road, 3x, before | after
  dt_<piece>_5x.png          each new piece at 5x (4x for the fronts) beside the approved bench, bin and lamp
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "riverwalk", "art", "scene")
BG = (36, 38, 44)


def fr(d, cy, cx): return Image.open(os.path.join(d, f"sweep_downtown_y{cy:03d}_x{cx:04d}.png")).convert("RGB")
def z(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
def grey(im):
    a = np.asarray(im, np.float32); l = (a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114).round().astype(np.uint8)
    return Image.fromarray(np.stack([l] * 3, -1))


def grid(rows, gap=8):
    w = max(sum(i.width for i in r) + gap * (len(r) + 1) for r in rows)
    h = sum(max(i.height for i in r) for r in rows) + gap * (len(rows) + 1)
    c = Image.new("RGB", (w, h), BG); y = gap
    for r in rows:
        x = gap
        for i in r: c.paste(i, (x, y)); x += i.width + gap
        y += max(i.height for i in r) + gap
    return c


def piece_sheet(names, k, out):
    """pieces at k x, on a mid-grey, with the approved bench, bin and lamp at the same zoom, all on one base line"""
    ims = [Image.open(os.path.join(ART, n + ".png")).convert("RGBA") for n in names + ["bench", "bin", "lamp_post"]]
    H = max(i.height for i in ims) * k + 24; W = sum(i.width * k + 16 for i in ims) + 16
    c = Image.new("RGBA", (W, H), (150, 156, 166, 255)); x = 16
    for i in ims:
        c.alpha_composite(z(i, k), (x, H - 12 - i.height * k)); x += i.width * k + 16
    c.convert("RGB").save(out)


if __name__ == "__main__":
    B, A, O = sys.argv[1:4]
    os.makedirs(O, exist_ok=True)
    grid([[z(fr(B, 120, 1920), 3), z(fr(A, 120, 1920), 3)], [z(fr(B, 240, 1920), 3), z(fr(A, 240, 1920), 3)]]).save(f"{O}/dt_sample_s7_ba.png")
    hi, st = fr(A, 120, 1920), fr(A, 240, 1920)
    grid([[z(hi, 3), z(grey(hi), 3)], [z(st, 3), z(grey(st), 3)], [hi, grey(hi), st, grey(st)]]).save(f"{O}/dt_sample_s7_sheet.png")
    grid([[z(fr(B, 240, 1840), 3), z(fr(A, 240, 1840), 3)], [z(fr(B, 120, 1560), 3), z(fr(A, 120, 1560), 3)]]).save(f"{O}/dt_sample_hiding_ba.png")
    piece_sheet(["town_front_tall1", "town_front_tall2", "town_front_tall3", "town_front_tall4"], 2, f"{O}/dt_fronts_2x.png")
    piece_sheet(["town_shelter_tall", "town_breadboard", "town_crate_leg"], 5, f"{O}/dt_shelter_5x.png")
    piece_sheet(["town_gateway", "town_crates70"], 5, f"{O}/dt_gateway_5x.png")
    piece_sheet(["town_portal_top", "town_oriel"], 5, f"{O}/dt_guild_5x.png")
    # the upper window at 6x: the one part stamped on every upper storey
    win = Image.open(os.path.join(ART, "town_front_tall1.png")).convert("RGB").crop((8, 150, 72, 250))
    z(win, 6).save(f"{O}/dt_window_6x.png")
    print("written", sorted(os.listdir(O)))
