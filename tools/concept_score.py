import sys, numpy as np, cv2, subprocess, re
from PIL import Image
def grid_strength(a, n):
    g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(float)
    res = []
    for e, L, N in [(np.abs(np.diff(g, axis=1)).sum(0), a.shape[1], n[0]), (np.abs(np.diff(g, axis=0)).sum(1), a.shape[0], n[1])]:
        p = L / N
        offs = np.arange(0, p, 0.05)
        sc = [np.mean([e[int(o + k*p)] for k in range(N) if int(o + k*p) < len(e)]) for o in offs]
        res.append(max(sc) / e.mean())   # edge energy on grid lines vs average
    return min(res)
for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert('RGB'))
    out = subprocess.run(['python3', '/home/claude/tools/concept_cut.py', f, '/tmp/_c.png', '320', '240'], capture_output=True, text=True).stdout
    clear = float(re.search(r': ([\d.]+)%', out).group(1))
    cut = Image.open('/tmp/_c.png'); box = Image.fromarray(a).resize((320, 240), Image.BOX)
    lab = lambda im: cv2.cvtColor(np.asarray(im).astype(np.float32)/255, cv2.COLOR_RGB2LAB)
    de = np.linalg.norm(lab(cut) - lab(box), axis=2).mean()
    print(f'{f:32s} grid {grid_strength(a,(320,240)):.2f}  clear {clear:5.1f}%  dE {de:.1f}')
