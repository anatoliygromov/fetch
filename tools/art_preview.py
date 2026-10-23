#!/usr/bin/env python3
"""The art preview's pictures (r8/preview), from tools/art_preview.sh's runs in OUT/before, OUT/after, OUT/misfit:
  OUT/pairs/<shot>_1x.png and _3x.png   placeholder (before) | art (after), side by side, labelled
  OUT/tour/dt_<shot>_3x.png             the tall Downtown with the art, every stop of the tour at 3x
  OUT/tour_downtown_tall.png            the tour on one sheet (1x shots shown at 2x)
  OUT/misfit_pieces.png                 the pieces that do not fit their boxes, drawn there anyway (not in the build)
  OUT/gif_*.gif                         the cargo bike, the tram, the bonus throw (and its slow motion), a promenade bike
  OUT/overview.png                      one sheet of in-game shots with the art
The game captures at 2x (640 x 480); 1x is every second pixel (exact), 3x is 1x scaled by 3 (nearest).
  python3 tools/art_preview.py [OUT]
"""
import os
import sys
from PIL import Image, ImageDraw

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/out/r8-preview"
INK, PAPER, GOLD = (20, 22, 32), (240, 236, 226), (250, 200, 60)


def one_x(im):
    return im.convert("RGB").resize((im.width // 2, im.height // 2), Image.NEAREST)


def scale(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def label(im, text, h=14):
    o = Image.new("RGB", (im.width, im.height + h), INK)
    o.paste(im, (0, h))
    ImageDraw.Draw(o).text((4, 2), text, fill=PAPER)
    return o


def shot(tag, name):
    p = os.path.join(OUT, tag, "%s_%s.png" % (tag, name))
    return Image.open(p) if os.path.exists(p) else None


def names(tag):
    d = os.path.join(OUT, tag)
    return sorted(f[len(tag) + 1:-4] for f in os.listdir(d) if f.endswith(".png"))


def grid(ims, cols, gap=4, bg=INK):
    w, h = max(i.width for i in ims), max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    o = Image.new("RGB", (cols * w + (cols + 1) * gap, rows * h + (rows + 1) * gap), bg)
    for i, im in enumerate(ims):
        o.paste(im, (gap + (i % cols) * (w + gap), gap + (i // cols) * (h + gap)))
    return o


def gif(tag, run, out, ms, crop=None, k=1, step=1):
    d = os.path.join(OUT, tag, "%s_%s" % (tag, run))
    if not os.path.isdir(d):
        return
    frames = []
    for f in sorted(os.listdir(d))[::step]:
        im = one_x(Image.open(os.path.join(d, f)))
        if crop:
            im = im.crop(crop)
        frames.append(scale(im, k).quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE))
    frames[0].save(os.path.join(OUT, out), save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
    print("%s: %d frames" % (out, len(frames)))


def main():
    os.makedirs(os.path.join(OUT, "pairs"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "tour"), exist_ok=True)
    after = names("after")
    for n in after:
        a, b = shot("after", n), shot("before", n)
        if not b:
            continue
        a1, b1 = one_x(a), one_x(b)
        for k in (1, 3):
            pair = Image.new("RGB", (b1.width * 2 * k + 4 * k, b1.height * k), INK)
            pair.paste(scale(b1, k), (0, 0))
            pair.paste(scale(a1, k), (b1.width * k + 4 * k, 0))
            label(pair, "%s   left: before (placeholder / old art)   right: art batch 1" % n, 14 * k // (2 if k > 1 else 1)).save(
                os.path.join(OUT, "pairs", "%s_%dx.png" % (n, k)))
    tour = [n for n in after if n.startswith("dt_")]
    for n in tour:
        scale(one_x(shot("after", n)), 3).save(os.path.join(OUT, "tour", "%s_3x.png" % n))
    grid([label(scale(one_x(shot("after", n)), 2), n) for n in tour], 3).save(os.path.join(OUT, "tour_downtown_tall.png"))
    if os.path.isdir(os.path.join(OUT, "misfit")):
        mis = [("dt_gable_chimney", "gable: 4 steps of ~20 px over the level's 15 steps of 4 px; chimney 24 wide on a 16 px box"),
               ("dt_chimney_top", "chimney: Pepper on the 16 px box, the pots 7 px over it, the golden bone among them"),
               ("dt_dormer", "dormer: pitched roof (left 19 px slope) on a flat 56 px box")]
        ims = [label(scale(one_x(shot("misfit", n)), 2), t) for n, t in mis if shot("misfit", n)]
        grid(ims, len(ims)).save(os.path.join(OUT, "misfit_pieces.png"))
    gif("after", "dt_cargo_bike", "gif_cargo_bike.gif", 33, k=2)
    gif("after", "dt_tram", "gif_tram.gif", 67, k=2)
    gif("after", "bonus_throw", "gif_bonus_throw.gif", 20, k=2, step=1)
    gif("after", "bonus_throw", "gif_bonus_throw_slow_3x.gif", 100, crop=(0, 120, 120, 200), k=3, step=1)
    gif("before", "bonus_throw", "gif_bonus_throw_before_slow_3x.gif", 100, crop=(0, 120, 120, 200), k=3, step=1)
    gif("after", "rw_promenade_bike", "gif_promenade_bike.gif", 33, k=2)
    # the overview: every piece in the game once, 1x shots at 2x
    pick = ["rw_promenade_rider1", "rw_promenade_rider2", "rw_road_riders", "bonus_throw_f3", "bonus_throw_f6",
            "dt_cargo_bike_under_kiosk", "dt_tram_at_stop", "dt_loggia", "dt_loggia_from_street", "dt_gallery",
            "dt_ledges", "dt_footbridge", "dt_bakery_fronts", "dt_plaza_street", "dt_spire_a", "dt_flower_roof"]
    ov = [label(scale(one_x(shot("after", n)), 2), n) for n in pick if shot("after", n)]
    grid(ov, 4).save(os.path.join(OUT, "overview.png"))
    print("pairs %d, tour %d, overview %d" % (len(os.listdir(os.path.join(OUT, "pairs"))), len(tour), len(ov)))


if __name__ == "__main__":
    main()
