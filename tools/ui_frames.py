"""tools/ui_frames.py OUT_DIR: runs `love riverwalk --uishots` headless and writes the UI's real frames to OUT_DIR as
320 x 240 PNGs (the window is 640 x 480, the game drawn at exactly 2x, so every 2nd pixel is the game's pixel).
Also writes <name>_3x.png for looking at. Env UI_X / UI_Y move Pepper (default 760, 184)."""
import os, sys, subprocess, tempfile, glob
import numpy as np
from PIL import Image

out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'out_ui/frames')
os.makedirs(out, exist_ok=True)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = tempfile.mkdtemp()
env = dict(os.environ, SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=data)
r = subprocess.run(['xvfb-run', '-a', 'love', 'riverwalk', '--uishots'], cwd=root, env=env, capture_output=True, text=True, timeout=180)
print(r.stdout[-400:], r.stderr[-2000:] if r.returncode else '')
for f in sorted(glob.glob(f'{data}/love/*/ui_*.png')):
    a = np.array(Image.open(f).convert('RGBA'))
    if a.shape[:2] != (480, 640): print('unexpected size', f, a.shape); continue
    assert (a[0::2, 0::2] == a[1::2, 1::2]).all(), 'not an exact 2x frame: ' + f
    g = a[0::2, 0::2]
    n = os.path.basename(f)[3:-4]
    Image.fromarray(g).save(f'{out}/{n}.png')
    Image.fromarray(g).resize((960, 720), Image.NEAREST).save(f'{out}/{n}_3x.png')
    t = f[:-4] + '.txt'
    if os.path.exists(t): open(f'{out}/{n}.txt', 'w').write(open(t).read())
    print('frame', n)
