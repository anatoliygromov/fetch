# kit A's native glyphs restyled to the chosen example: bolder by 1 px, yellow top / orange bottom bands with a
# highlight row, a maroon outline and a darker 1 px shadow down-right. Same rules for every glyph.
import os, json, numpy as np
from PIL import Image
from scipy import ndimage
SRC = '/tmp/claude-0/ui/kit/final/font_big'; OUT = '/tmp/claude-0/ui/v4/font'
MAROON = (64, 11, 6); SHADOW = (36, 8, 5)
STYLES = {
  'gold':  dict(hi=(255, 244, 168), top=(255, 216, 56), mid=(252, 180, 40), bot=(238, 128, 30), deep=(214, 96, 24)),
  'cream': dict(hi=(255, 255, 255), top=(255, 250, 230), mid=(250, 238, 206), bot=(240, 222, 182), deep=(226, 204, 160)),
  'dim':   dict(hi=(210, 196, 172), top=(196, 182, 158), mid=(186, 172, 148), bot=(174, 160, 136), deep=(160, 146, 122)),
}
def fill_mask(a):
    L = a[..., :3].astype(float) @ [0.299, 0.587, 0.114]; return (a[..., 3] > 0) & (L > 100)
def bold(m):
    b = m.copy(); b[:, 1:] |= m[:, :-1]                       # one px wider to the right
    # keep counters open: a counter (hole) that the bolding closed is reopened from the original
    holes = ndimage.binary_fill_holes(m) & ~m
    lab, n = ndimage.label(holes)
    for i in range(1, n + 1):
        h = lab == i
        if (h & ~b).sum() == 0: b[h] = False
    return b
def clean(m):
    # single-pixel bumps and notches on the silhouette
    m = m.copy()
    for _ in range(2):
        nb = ndimage.convolve(m.astype(int), np.ones((3, 3), int), mode='constant') - m
        m[(m) & (nb <= 1)] = False                            # lone / spur pixels
        m[(~m) & (nb >= 6) & ndimage.binary_fill_holes(m)] = True
    return m
def style(m, s, cap_top, cap_bot):
    pad = 2; H, W = m.shape
    M = np.zeros((H + pad * 2 + 1, W + pad * 2 + 1), bool); M[pad:pad + H, pad:pad + W] = m
    o = np.zeros(M.shape + (4,), np.uint8)
    ring = ndimage.binary_dilation(M, structure=np.ones((3, 3))) & ~M
    sh = np.zeros_like(M); sh[1:, 1:] = (M | ring)[:-1, :-1]; sh &= ~(M | ring)
    o[sh] = (*SHADOW, 255); o[ring] = (*MAROON, 255)
    st = STYLES[s]; span = max(1, cap_bot - cap_top)
    for y in range(H):
        t = (y - cap_top) / span
        col = st['hi'] if y == cap_top else st['top'] if t < 0.52 else st['mid'] if t < 0.62 else st['bot'] if t < 0.88 else st['deep']
        o[pad + y][M[pad + y]] = (*col, 255)
    return o
if __name__ == "__main__":
    files = sorted(f for f in os.listdir(SRC) if f.endswith('.png'))
    masks = {f[:-4]: clean(bold(fill_mask(np.array(Image.open(f'{SRC}/{f}').convert('RGBA'))))) for f in files}
    # crop each mask to its fill and record the cap line: letters share one cap height, digits another
    def crop(m):
        ys, xs = np.nonzero(m); return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    masks = {k: crop(v) for k, v in masks.items()}
    caps = {}
    for grp in ('letter_', 'digit_'):
        hs = [v.shape[0] for k, v in masks.items() if k.startswith(grp) and k[-1].isalnum() and len(k) == len(grp) + 1]
        caps[grp] = max(set(hs), key=hs.count)
    meta = {}
    for s in STYLES:
        os.makedirs(f'{OUT}_{s}', exist_ok=True)
        for k, m in masks.items():
            grp = 'letter_' if k.startswith('letter_') else 'digit_'
            H = m.shape[0]; cap = caps[grp]
            # glyphs a pixel taller or shorter than the cap: pad to the cap so every glyph sits on one baseline
            if k[-1].isalnum() and len(k) == len(grp) + 1 and H != cap:
                if H < cap: m = np.vstack([np.zeros((cap - H, m.shape[1]), bool), m])
                else: m = m[H - cap:]
            img = style(m, s, 0, m.shape[0] - 1); Image.fromarray(img).save(f'{OUT}_{s}/{k}.png')
            meta[k] = [int(img.shape[1]), int(img.shape[0])]
    json.dump(dict(caps=caps, sizes=meta), open('/tmp/claude-0/ui/v4/font_meta.json', 'w'), indent=0)
    print('caps', caps)
