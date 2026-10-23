"""tools/qa_card.py: one QA card (PNG) per asset from tools/asset_qa.py's JSON (docs/asset_qa.md).

  python3 -I tools/asset_qa.py --all --json out/qa.json
  python3 -I tools/qa_card.py out/qa.json out/cards NAME --frame NAME=ingame.png [--slot NAME=WxH]
  python3 -I tools/qa_card.py out/qa.json out/drafts [names] --draft      (working cards, never shown to the owner)

THE GATE (owner, 23 Oct; docs/BIBLE.md): a card for the owner is refused, and nothing is written, unless every asset
on it has (1) an in-game frame (--frame, a screenshot of the asset where the game draws it), shown in colour and in
greyscale, and (2) a slot: a size in asset_qa.SLOTS or one given with --slot, checked here. The 5x zoom with the
approved bench, bin and lamp beside it is always on the card. --draft skips the gate and stamps DRAFT on the card.

A card shows, top to bottom:
  - the verdict, the numbers against the layer's ladder row, every failed or warned check
  - the asset AS DRAWN (fade + look shader) at 1x and 2x (2x = how it looks on the RG35XX)
  - the file at up to 5x with every flagged pixel boxed, one colour per check (legend on the card), and the approved
    bench, bin and lamp at the same zoom beside it (the crispness and scale bar)
  - buildings: each storey's windows lined up at 8x, a window that differs from the others boxed red, its odd pixels marked
  - sheets: an animated GIF per row as drawn, at 3x (beside the card: <name>_rowN.gif)
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_qa as Q

BG, PANEL, TXT, DIM = (30, 30, 35), (44, 44, 50), (232, 232, 236), (150, 150, 160)
VCOL = {"PASS": (90, 200, 110), "WARN": (240, 190, 60), "FAIL": (235, 70, 70)}
CCOL = {"stray": (255, 220, 0), "outline": (255, 40, 40), "pinholes": (0, 230, 255), "specks": (0, 230, 255),
        "windows": (255, 0, 200), "frames": (255, 140, 0), "alpha": (160, 90, 255), "ladder": (120, 255, 120),
        "blotches": (60, 140, 255), "noise": (255, 255, 255), "decor-ink": (170, 170, 170)}
REFS = ["bench", "bin", "lamp_post"]

def font(s):
    try: return ImageFont.load_default(size=s)
    except TypeError: return ImageFont.load_default()
F, FB, FS = font(15), font(20), font(13)

def checker(w, h, c0=(190, 190, 196), c1=(170, 170, 178), s=8):
    y, x = np.mgrid[0:h, 0:w]
    m = ((x // s + y // s) % 2).astype(bool)
    out = np.empty((h, w, 3), np.uint8); out[~m] = c0; out[m] = c1
    return Image.fromarray(out, "RGB")

def on_bg(im, bg):
    b = bg.copy(); b.paste(im, (0, 0), im); return b

def zoom(im, z): return im.resize((im.width * z, im.height * z), Image.NEAREST)

def drawn_image(d):
    im = np.array(Image.open(d["_path"]).convert("RGBA"))
    a = im[..., 3] > 127
    rgb = Q.as_drawn(im[..., :3] / 255.0, a, d["level"], None if d["layer"] == "char" else d["layer"], d["fade"])
    out = np.concatenate([(rgb * 255).round().astype(np.uint8), (a * 255).astype(np.uint8)[..., None]], 2)
    return Image.fromarray(out, "RGBA")

def wrap(text, width_px, f):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) > width_px and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def card(d, reg, out_dir, frame=None, slot=None, draft=False):
    name = d["name"]
    raw = Image.open(d["_path"]).convert("RGBA")
    W0, H0 = raw.size
    z = max(2, min(5, 1900 // max(1, W0)))
    blocks = []
    # 1 header
    lines = [(f"{name}", FB, VCOL[d["verdict"]]),
             (f"{d['verdict']}   layer {d['layer']}   level {d['level']}   fade {d['fade']:.2f}   {W0} x {H0} px" +
              (f"   frames {d['frames'][0]}x{d['frames'][1]}" if d.get("frames") else "") + (f"   building" if d.get("building") else "") +
              (f"   becomes {d['info']['hook']}" if d["info"].get("hook") else ""), F, TXT)]
    i = d["info"]; row = Q.LADDER.get(d["layer"], {})
    lad = "   ".join(("outline required" if k == "outline" else f"{k} {v}") for k, v in row.items())
    lines.append((f"on screen: darkest {i.get('p10')}  median {i.get('median')}  light {i.get('p90')}   colours {i.get('colours')}   lone {i.get('lone')} %" +
                  f"   dirt {i.get('noise', 0)} %   blotches {i.get('blotches', 0)}" + (f"   outline {i['outline']} %" if "outline" in i else "") + f"      ladder row: {lad}", F, DIM))
    for c in d["checks"]:
        col = {"fail": (235, 70, 70), "warn": (240, 190, 60)}.get(c["sev"], DIM)
        for k, ln in enumerate(wrap(f"{c['sev'].upper()}  {c['id']}: {c['msg']}", 1880, F)):
            lines.append(("    " + ln if k else ln, F, col))
    if not d["checks"]: lines.append(("no findings", F, (90, 200, 110)))
    if slot: lines.append((f"slot {slot[0]} x {slot[1]} px: " + ("OK" if (W0, H0) == tuple(slot) else f"WRONG ({W0} x {H0})"), F,
                           (90, 200, 110) if (W0, H0) == tuple(slot) else (235, 70, 70)))
    if draft: lines.insert(0, ("DRAFT: not passed through the gate, not for the owner", FB, (240, 190, 60)))
    hh = 14 + sum(28 if f is FB else 20 for _, f, _ in lines)
    blocks.append(("header", lines, hh))
    # 2 as drawn 1x and 2x
    dr = drawn_image(d)
    a1 = on_bg(dr, checker(W0, H0, (128, 128, 132), (118, 118, 122), 4))
    a2 = zoom(a1, 2)
    asd = Image.new("RGB", (a1.width + a2.width + 30, a2.height + 26), PANEL)
    ImageDraw.Draw(asd).text((8, 4), "as drawn (fade + look shader): 1x and 2x", font=FS, fill=DIM)
    asd.paste(a1, (8, 22)); asd.paste(a2, (a1.width + 22, 22))
    blocks.append(("img", asd))
    # 2b the in-game frame, colour and greyscale (the gate)
    if frame:
        fr = Image.open(frame).convert("RGB"); fz = 2 if fr.width <= 480 else 1
        fc = zoom(fr, fz); fg = fc.convert("L").convert("RGB")
        fb = Image.new("RGB", (fc.width * 2 + 34, fc.height + 26), PANEL)
        ImageDraw.Draw(fb).text((8, 4), f"in the game at {fz}x: colour, then greyscale (lightest layers at the back?)", font=FS, fill=DIM)
        fb.paste(fc, (8, 22)); fb.paste(fg, (fc.width + 26, 22))
        blocks.append(("img", fb))
    # 3 the file at z, flagged pixels boxed, the references beside (a sheet: every frame at 5x, wrapped)
    if d.get("frames"): z = 5 if d["frames"][0] <= 100 else 3
    big = zoom(on_bg(raw, checker(W0, H0)), z)
    dd = ImageDraw.Draw(big)
    used = set()
    for c in d["checks"]:
        col = CCOL.get(c["id"], (255, 255, 255))
        for x, y in c.get("pixels", [])[:3000]:
            dd.rectangle([x * z, y * z, x * z + z - 1, y * z + z - 1], outline=col); used.add(c["id"])
    if d.get("frames"):
        fw, fh = d["frames"]
        tiles = []
        for ry in range(H0 // fh):
            for cx in range(W0 // fw):
                if np.array(raw.crop((cx * fw, ry * fh, cx * fw + fw, ry * fh + fh)))[..., 3].sum() < 10 * 255: continue
                t = big.crop((cx * fw * z, ry * fh * z, (cx + 1) * fw * z, (ry + 1) * fh * z))
                ImageDraw.Draw(t).text((3, 1), f"r{ry + 1} c{cx + 1}", font=FS, fill=(60, 60, 70))
                tiles.append(t)
        per = max(1, 1880 // (fw * z + 6)); n = len(tiles)
        lines_ = (n + per - 1) // per
        big = Image.new("RGB", (min(n, per) * (fw * z + 6), lines_ * (fh * z + 6)), PANEL)
        for k, t in enumerate(tiles): big.paste(t, ((k % per) * (fw * z + 6), (k // per) * (fh * z + 6)))
    refs = []
    for rn in REFS:
        if rn in reg and rn != name and H0 <= 160 and not d.get("frames"):
            refs.append(zoom(on_bg(Image.open(reg[rn]["path"]).convert("RGBA"), checker(*Image.open(reg[rn]["path"]).size)), z))
    rw = sum(r.width + 12 for r in refs)
    pw = big.width + (rw + 24 if refs else 0) + 16
    ph = max([big.height] + [r.height for r in refs]) + 44
    p = Image.new("RGB", (pw, ph), PANEL); pd = ImageDraw.Draw(p)
    legend = "   ".join(k for k in CCOL if k in used)
    pd.text((8, 4), f"the file at {z}x" + (f"   boxed: {legend} (colours as listed below)" if used else "") +
            ("      approved bench, bin, lamp at the same zoom" if refs else ""), font=FS, fill=DIM)
    p.paste(big, (8, 22))
    x = big.width + 32
    for r in refs: p.paste(r, (x, 22 + max(0, big.height - r.height))); x += r.width + 12
    lx = 8
    for k in CCOL:
        if k in used:
            pd.rectangle([lx, ph - 16, lx + 10, ph - 6], outline=CCOL[k]); pd.text((lx + 14, ph - 19), k, font=FS, fill=CCOL[k]); lx += 28 + int(FS.getlength(k))
    blocks.append(("img", p))
    # 4 windows lineup
    win = d["info"].get("windows")
    if isinstance(win, dict) and win.get("storeys"):
        Z = 8; rows = []
        for si, st in enumerate(win["storeys"]):
            tiles = []
            for k, w in enumerate(st["windows"]):
                x0, y0, ww, hh_ = w["x"], w["y"], w["w"], w["h"]
                crop = raw.crop((x0, y0, x0 + ww, y0 + hh_))
                t = zoom(on_bg(crop, checker(ww, hh_)), Z)
                diff = st["diffs"][k] if k < len(st["diffs"]) else 0
                td = ImageDraw.Draw(t)
                for c in d["checks"]:
                    if c["id"] != "windows": continue
                    for px, py in c["pixels"]:
                        if x0 <= px < x0 + ww and y0 <= py < y0 + hh_:
                            td.rectangle([(px - x0) * Z, (py - y0) * Z, (px - x0) * Z + Z - 1, (py - y0) * Z + Z - 1], outline=CCOL["windows"])
                fr = Image.new("RGB", (t.width + 8, t.height + 8), (235, 70, 70) if diff else (60, 60, 68))
                fr.paste(t, (4, 4)); tiles.append(fr)
            if not tiles: continue
            rh = max(t.height for t in tiles) + 26
            r = Image.new("RGB", (max(1880, sum(t.width + 10 for t in tiles) + 16), rh), PANEL)
            ImageDraw.Draw(r).text((8, 3), f"storey {si + 1} (y {st['y']}): " + ("; ".join(st.get("problems", [])) or "all windows the same"),
                                   font=FS, fill=(235, 70, 70) if st.get("problems") else (90, 200, 110))
            x = 8
            for t in tiles: r.paste(t, (x, 22)); x += t.width + 10
            rows.append(r)
        if rows:
            hdr = Image.new("RGB", (900, 24), PANEL)
            ImageDraw.Draw(hdr).text((8, 4), "windows per storey at 8x (red frame: differs from the others; magenta boxes: the odd pixels)", font=FS, fill=DIM)
            blocks.append(("img", hdr)); blocks += [("img", r) for r in rows]
    # 5 GIFs for sheets
    if d.get("frames"):
        fw, fh = d["frames"]
        for ry in range(H0 // fh):
            frs = []
            for cx in range(W0 // fw):
                f = dr.crop((cx * fw, ry * fh, cx * fw + fw, ry * fh + fh))
                if np.array(f)[..., 3].sum() < 10 * 255: continue
                frs.append(zoom(on_bg(f, Image.new("RGB", (fw, fh), (128, 128, 132))), 3))
            if len(frs) > 1:
                frs[0].save(os.path.join(out_dir, f"{name}_row{ry + 1}.gif"), save_all=True, append_images=frs[1:], duration=100, loop=0)
    # assemble
    W = max(1920, max((b[1].width for b in blocks if b[0] == "img"), default=0) + 24)
    H = sum((b[2] if b[0] == "header" else b[1].height) + 12 for b in blocks) + 12
    cv = Image.new("RGB", (W, H), BG); cd = ImageDraw.Draw(cv)
    y = 12
    for b in blocks:
        if b[0] == "header":
            cd.rectangle([0, y - 12, 8, y + b[2]], fill=VCOL[d["verdict"]])
            yy = y
            for t, f, col in b[1]: cd.text((20, yy), t, font=f, fill=col); yy += 28 if f is FB else 20
            y += b[2] + 12
        else:
            cv.paste(b[1], (12, y)); y += b[1].height + 12
    path = os.path.join(out_dir, ("DRAFT_" if draft else "") + f"{d['verdict']}_{name}.png")
    cv.save(path, optimize=True)
    return path

def main():
    args = sys.argv[1:]
    draft = "--draft" in args
    frames, slots, pos, k = {}, {}, [], 0
    while k < len(args):
        a = args[k]
        if a in ("--frame", "--slot"):
            n, v = args[k + 1].split("=", 1)
            if a == "--frame": frames[n] = v
            else: slots[n] = tuple(int(t) for t in v.lower().split("x"))
            k += 2; continue
        if a != "--draft": pos.append(a)
        k += 1
    data = json.load(open(pos[0])); out = pos[1]; only = set(pos[2:])
    reg = Q.registry()
    todo = [d for d in data if not only or d["name"] in only]
    if not draft:
        refused = []
        for d in todo:
            n = d["name"]
            if n not in frames or not os.path.exists(frames[n]): refused.append(f"{n}: no in-game frame (--frame {n}=path)")
            if n not in slots and n in Q.SLOTS: slots[n] = Q.SLOTS[n][:2]
            if n not in slots: refused.append(f"{n}: no slot (add it to asset_qa.SLOTS or pass --slot {n}=WxH)")
        if refused:
            print("REFUSED by the gate, no card written:"); print("\n".join("  " + r for r in refused)); sys.exit(2)
    os.makedirs(out, exist_ok=True)
    for d in todo:
        d["_path"] = d["file"] if os.path.isabs(d["file"]) else os.path.join(Q.ROOT, d["file"])
        if not os.path.exists(d["_path"]) and d["name"] in reg: d["_path"] = reg[d["name"]]["path"]
        sl = slots.get(d["name"])
        if sl and Image.open(d["_path"]).size != tuple(sl):
            w, h = Image.open(d["_path"]).size
            d["verdict"] = "FAIL"; d["checks"].insert(0, {"id": "slot", "sev": "fail", "msg": f"{w} x {h} px, its slot is {sl[0]} x {sl[1]}"})
        print(card(d, reg, out, frames.get(d["name"]), sl, draft))

if __name__ == "__main__":
    main()
