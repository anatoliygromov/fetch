#!/usr/bin/env python3
"""rt_kit_fix.py: Rooftops kit pieces as the CONCEPT'S OWN PIXELS with surgical fixes only (owner 12:23: "I only was
talking about the fixes, but art needs to be preserved"). Allowed changes, each counted and shown on a change map:
  1 cut out: everything that is not the piece becomes transparent;
  2 line glitches: a pixel that breaks a straight line it sits in (its two neighbours along the line agree with each
    other and not with it) takes the line's colour;
  3 holes: sky-coloured pixels enclosed inside the piece take their row neighbours' colour;
  4 completion: a part the concept hid (the window's bottom frame, the chimney's base) continues the piece's own rows.
Nothing is redrawn. Source: art/source/rt_lockfill/final.png (the concept on the game grid). Writes art/source/rt_kit/."""
import numpy as np
from PIL import Image
SRC = np.asarray(Image.open('art/source/rt_lockfill/final.png').convert('RGB')).astype(int)
LUM = lambda a: a @ np.array([.299, .587, .114])

def glitches(rgb, mask, region):
    """rule 2 inside region (y0, y1, x0, x1): one pass, horizontal and vertical lines"""
    out = rgb.copy(); n = 0
    y0, y1, x0, x1 = region
    for y in range(max(1, y0), min(rgb.shape[0] - 1, y1)):
        for x in range(max(1, x0), min(rgb.shape[1] - 1, x1)):
            if not mask[y, x]: continue
            p = tuple(rgb[y, x])
            for (a, b) in (((y, x - 1), (y, x + 1)), ((y - 1, x), (y + 1, x))):
                if mask[a] and mask[b] and tuple(rgb[a]) == tuple(rgb[b]) and tuple(rgb[a]) != p:
                    # only when the pixel is alone on its line: its other two neighbours do not share its colour either
                    oth = [(y, x - 1), (y, x + 1)] if a[0] != y else [(y - 1, x), (y + 1, x)]
                    if all(tuple(rgb[o]) != p for o in oth):
                        out[y, x] = rgb[a]; n += 1; break
    return out, n

def window():
    x0, y0, x1, y1 = 205, 113, 227, 135                          # the frame, as the concept draws it (22 x 22)
    rgb = SRC[y0:y1, x0:x1].copy(); h, w = rgb.shape[:2]
    mask = np.ones((h, w), bool)
    fixed, ng = glitches(rgb, mask, (0, h, 0, w))
    top = fixed[0:3][::-1]                                          # 4 the hidden bottom: the frame's own top rows,
    full = np.concatenate([fixed, top], 0)                           #   mirrored
    m = np.ones(full.shape[:2], bool)
    return full, m, rgb, ng, top.shape[0] * w

def chimney():
    x0, y0, x1, y1 = 224, 30, 270, 78
    rgb = SRC[y0:y1, x0:x1].copy(); h, w = rgb.shape[:2]
    lum = LUM(rgb); sky = (lum > 200) & (rgb[..., 2] > 140)
    mask = np.zeros((h, w), bool)
    for (a, b) in ((233, 242), (243, 253), (254, 264)):              # the pots' columns
        mask[0:48 - y0, a - x0:b - x0] = ~sky[0:48 - y0, a - x0:b - x0]
    mask[48 - y0:, 228 - x0:268 - x0] = True                         # the slab
    mask[55 - y0:, 228 - x0:267 - x0] = True; mask[55 - y0:, 266 - x0:] = False   # the body
    holes = np.zeros_like(mask)                                       # 3 enclosed sky pixels, inside ONE pot only
    for (a, b) in ((233, 242), (243, 253), (254, 264)):              #   (the gaps between pots are real)
        for y in range(0, 48 - y0):
            xs = [x for x in range(a - x0, b - x0) if mask[y, x]]
            for x in range(a - x0, b - x0):
                if sky[y, x] and xs and min(xs) < x < max(xs): holes[y, x] = True
    fixed = rgb.copy()
    for y, x in zip(*np.nonzero(holes)):
        fixed[y, x] = rgb[y, max(xx for xx in np.nonzero(mask[y])[0] if xx < x)]
    mask2 = mask | holes
    fixed, ng = glitches(fixed, mask2, (56 - y0, h, 233 - x0, 262 - x0))   # 2 inside the body only
    body_rows = [r for r in range(56 - y0, h)]
    clean = min(body_rows, key=lambda r: len(np.unique(fixed[r, 230 - x0:264 - x0], axis=0)))   # 4 the base: the body's
    ext = np.repeat(fixed[clean:clean + 1], 10, 0); mext = np.repeat(mask2[clean:clean + 1], 10, 0)   # cleanest row
    full = np.concatenate([fixed, ext], 0); m = np.concatenate([mask2, mext], 0)
    return full, m, rgb, ng, int(holes.sum()), int(mext.sum())

def rgba(rgb, m):
    a = np.zeros(rgb.shape[:2] + (4,), np.uint8); a[..., :3] = rgb; a[..., 3] = np.where(m, 255, 0); return a

if __name__ == '__main__':
    import json
    wf, wm, wsrc, wng, wext = window()
    cf, cm, csrc, cng, chol, cext = chimney()
    Image.fromarray(rgba(wf, wm)).save('art/source/rt_kit/window.png')
    Image.fromarray(rgba(cf, cm)).save('art/source/rt_kit/chimney_big.png')
    rep = {'window': {'size': list(wf.shape[1::-1]), 'line_glitches_fixed': wng, 'completed_px': wext},
           'chimney_big': {'size': list(cf.shape[1::-1]), 'line_glitches_fixed': cng, 'holes_filled': chol, 'completed_px': cext}}
    json.dump(rep, open('art/source/rt_kit/fixes.json', 'w'), indent=1); print(rep)
