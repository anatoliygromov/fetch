"""tools/build_tagline.py [--preview DIR]: the title's tagline plate, rebuilt clean (owner 7 Nov: "stray pixels, maybe
we need a better chunkier type"). Writes riverwalk/art/title/tagline_chunky.png.
  Plate: the regrid plate's colours and build (navy edge, light blue rim, navy fill), the same 3-step chamfer on all
         four corners (single steps, no doubled ones, no loose end pixels), 20 px tall like the old plate, wide enough for the text
         with 6 px of navy each side, centred on the menu's centre line (title.lua T.CX = 220).
  Type:  the game's own 7 px UI font (art/ui/font7_cream.png, the menus' font: 2 px stems, caps), outline and
         shadow recoloured from the menus' brown to the plate's deep navy so the letters sit in the plate.
--preview DIR also writes before/after crops of the title (base.png with the plate drawn on) at 4x."""
import re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RW = ROOT / "riverwalk"
TEXT = "THE CITY DOG ADVENTURER"
NAVY, RIM = (1, 37, 85, 255), (62, 166, 242, 255)
DEEP, DEEP2 = (0, 18, 46, 255), (0, 10, 30, 255)      # the outline and shadow, in the plate's navy
OUTLINE, SHADOW = (64, 11, 6, 255), (36, 8, 5, 255)    # the menu font's own
H, PAD, CHAMFER, CX, Y = 20, 6, 3, 220, 77


def font7():
    t = (RW / "uifont_data.lua").read_text()
    blk = re.search(r"\[7\] = \{(.*?)\} \},", t, re.S).group(1)
    f = {k: int(v) for k, v in re.findall(r"(h|gap|space|asc) = (\d+)", blk.split("cells")[0])}
    f["cells"] = {ch: (int(x), int(w)) for ch, x, w in re.findall(r'\["(.)"\] = \{ (\d+), (\d+) \}', blk)}
    return f


def render(text, recolour=True):
    f = font7()
    atlas = Image.open(RW / "art/ui/font7_cream.png").convert("RGBA")
    ch_h = f["h"] + 5 + f["asc"]
    w = 0
    for ch in text:
        w += f["space"] if ch == " " else f["cells"][ch][1] + f["gap"]
    w -= f["gap"]
    out = Image.new("RGBA", (w + 6, f["h"] + 6), (0, 0, 0, 0))
    x = 2
    for ch in text:
        if ch == " ":
            x += f["space"]; continue
        cx, cw = f["cells"][ch]
        g = atlas.crop((cx, 0, cx + cw + 5, ch_h))
        out.alpha_composite(g, (x - 2, -f["asc"]))      # the body's top-left at (x, 0) + the cell's 2 px margin
        x += cw + f["gap"]
    if recolour:
        px = out.load()
        for yy in range(out.height):
            for xx in range(out.width):
                if px[xx, yy] == OUTLINE: px[xx, yy] = DEEP
                elif px[xx, yy] == SHADOW: px[xx, yy] = DEEP2
    return out.crop(out.getbbox()), w


def plate(text_img):
    """the outer shape: a rectangle with the same CHAMFER-step 45 degree cut on all four corners. Ring 0 (pixels with a
    side outside the shape) is the navy edge against the sky, ring 1 (a side on ring 0) the light blue rim, one pixel
    wide on the straights and single steps on the cuts; the rest the navy fill. As the old plate: edge, rim, fill."""
    w = text_img.width + 2 * PAD + 4
    def inset(y): return max(0, CHAMFER - y, y - (H - 1 - CHAMFER))
    def inside(x, y): return 0 <= y < H and inset(y) <= x <= w - 1 - inset(y)
    ring0 = {(x, y) for y in range(H) for x in range(w) if inside(x, y)
             and any(not inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    ring1 = {(x, y) for y in range(H) for x in range(w) if inside(x, y) and (x, y) not in ring0
             and any((x + dx, y + dy) in ring0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    im = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(H):
        for x in range(w):
            if inside(x, y): px[x, y] = RIM if (x, y) in ring1 else NAVY
    tx = (w - text_img.width) // 2
    ty = (H - text_img.height + 1) // 2
    im.alpha_composite(text_img, (tx, ty))
    return im


def main():
    txt, _ = render(TEXT)
    im = plate(txt)
    out = RW / "art/title/tagline_chunky.png"
    im.save(out)
    x0 = int(CX - (im.width - 1) / 2 + 0.5)
    print(f"tagline_chunky.png {im.width}x{im.height}, placed at x {x0}..{x0 + im.width - 1}, y {Y}..{Y + H - 1}")
    if "--preview" in sys.argv:
        d = Path(sys.argv[sys.argv.index("--preview") + 1]); d.mkdir(parents=True, exist_ok=True)
        base = Image.open(RW / "art/title/base.png").convert("RGBA")
        box = (120, 30, 320, 110)
        before = base.crop(box)
        aft = base.copy(); aft.alpha_composite(im, (x0, Y)); after = aft.crop(box)
        brown, _ = render(TEXT, recolour=False); im2 = plate(brown)
        alt = base.copy(); alt.alpha_composite(im2, (x0, Y)); alt = alt.crop(box)
        bw, bh = before.size
        sheet = Image.new("RGBA", (bw * 3 + 8, bh), (26, 26, 30, 255))
        for i, s in enumerate((before, after, alt)): sheet.paste(s, (i * (bw + 4), 0))
        sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(d / "tagline_compare_4x.png")
        aft.save(d / "title_with_chunky.png")


if __name__ == "__main__":
    main()
