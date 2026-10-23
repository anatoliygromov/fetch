# rebuild a frame as a true 9-slice: corners as drawn (ornament extent found from the silhouette), each edge one
# representative 1 px column/row (the most common one along that edge) repeated, the inside one flat fill.
import sys, os, json, numpy as np
from PIL import Image
from collections import Counter
def extent(a):
    """corner sizes from the silhouette: where the outer outline leaves its straight line"""
    op = a[..., 3] > 0; H, W = op.shape
    top = np.array([np.argmax(op[:, x]) if op[:, x].any() else H for x in range(W)])
    bot = np.array([H - 1 - np.argmax(op[::-1, x]) if op[:, x].any() else -1 for x in range(W)])
    lef = np.array([np.argmax(op[y, :]) if op[y].any() else W for y in range(H)])
    rig = np.array([W - 1 - np.argmax(op[y, ::-1]) if op[y].any() else -1 for y in range(H)])
    def run(v, mode, n):
        i = 0
        while i < n // 2 - 1 and not (v[i] == mode and v[i+1] == mode and v[i+2] == mode): i += 1
        return i
    mt, mb = Counter(top).most_common(1)[0][0], Counter(bot).most_common(1)[0][0]
    ml, mr = Counter(lef).most_common(1)[0][0], Counter(rig).most_common(1)[0][0]
    L = max(run(top, mt, W), run(bot, mb, W)); R = max(run(top[::-1], mt, W), run(bot[::-1], mb, W))
    T = max(run(lef, ml, H), run(rig, mr, H)); B = max(run(lef[::-1], ml, H), run(rig[::-1], mr, H))
    return L, R, T, B, (mt, mb, ml, mr)
def common_line(lines):
    keys = [l.tobytes() for l in lines]; k = Counter(keys).most_common(1)[0][0]
    return lines[keys.index(k)]
def rebuild(a, pad=1):
    H, W = a.shape[:2]; L, R, T, B, m = extent(a)
    L = R = max(L, R) + pad; T = B = max(T, B, min(L - pad, H // 2 - 3)) + pad      # symmetric, corners at least as tall as wide
    top = common_line([a[:T, x] for x in range(L, W - R)]); bot = common_line([a[H - B:, x] for x in range(L, W - R)])
    lef = common_line([a[y, :L] for y in range(T, H - B)]); rig = common_line([a[y, W - R:] for y in range(T, H - B)])
    inside = a[T:H - B, L:W - R].reshape(-1, 4); fill = Counter(map(bytes, inside)).most_common(1)[0][0]
    fill = np.frombuffer(fill, np.uint8)
    return dict(tl=a[:T, :L], tr=a[:T, W - R:], bl=a[H - B:, :L], br=a[H - B:, W - R:], top=top, bottom=bot, left=lef, right=rig, fill=fill,
                L=L, R=R, T=T, B=B)
def draw(s, w, h):
    o = np.zeros((h, w, 4), np.uint8); L, R, T, B = s['L'], s['R'], s['T'], s['B']
    o[T:h - B, L:w - R] = s['fill']
    for x in range(L, w - R): o[:T, x] = s['top']; o[h - B:, x] = s['bottom']
    for y in range(T, h - B): o[y, :L] = s['left']; o[y, w - R:] = s['right']
    o[:T, :L] = s['tl']; o[:T, w - R:] = s['tr']; o[h - B:, :L] = s['bl']; o[h - B:, w - R:] = s['br']
    return o
def rebuild3(a, L=None, R=None):
    """horizontal 3-slice (rows, ribbon, bars): caps full height, the middle the most common full column"""
    H, W = a.shape[:2]
    if L is None:
        l, r, t, b, m = extent(a); L, R = l + 1, r + 1
    mid = common_line([a[:, x] for x in range(L, W - R)])
    return dict(left=a[:, :L], right=a[:, W - R:], mid=mid, L=L, R=R)
def draw3(s, w):
    H = s['mid'].shape[0]; o = np.zeros((H, w, 4), np.uint8)
    for x in range(s['L'], w - s['R']): o[:, x] = s['mid']
    o[:, :s['L']] = s['left']; o[:, w - s['R']:] = s['right']; return o
if __name__ == "__main__":
    D = sys.argv[1]; out = sys.argv[2]; os.makedirs(out, exist_ok=True); meta = {}
    for n in ['panel_menu', 'panel_wide', 'panel_menu_cream', 'panel_wide_cream']:
        a = np.array(Image.open(f'{D}/{n}.png').convert('RGBA')); s = rebuild(a)
        sheet = draw(s, a.shape[1], a.shape[0]); Image.fromarray(sheet).save(f'{out}/{n}.png')
        meta[n] = dict(kind='nine', w=a.shape[1], h=a.shape[0], left=s['L'], right=s['R'], top=s['T'], bottom=s['B'])
        print(n, meta[n])
    for n, L, R in [('row_normal', 4, 4), ('row_selected', 17, 4), ('row_disabled', 17, 4), ('ribbon', None, None), ('health_full', 18, 6), ('health_empty', 18, 6)]:
        a = np.array(Image.open(f'{D}/{n}.png').convert('RGBA')); s = rebuild3(a, L, R)
        Image.fromarray(draw3(s, a.shape[1])).save(f'{out}/{n}.png')
        meta[n] = dict(kind='three', w=a.shape[1], h=a.shape[0], left=s['L'], right=s['R']); print(n, meta[n])
    json.dump(meta, open(f'{out}/slices.json', 'w'), indent=1)
