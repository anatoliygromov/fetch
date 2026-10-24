"""tools/screen_frames.py [OUT_DIR] [SHOT ...]: runs `love riverwalk --screenshots` headless (riverwalk/tests_screens.lua)
and writes every step 3 UI screen to OUT_DIR (default out_ui/step3/frames) as a 320 x 240 PNG (the window is 640 x
480, the game drawn at exactly 2x, so every 2nd pixel is the game's), with <name>_3x.png and <name>_3x_grey.png for
looking at and <name>.txt (the bodies placed, for tools/layout_qa_menus.py)."""
import os, sys, subprocess, tempfile, glob, shutil
import numpy as np
from PIL import Image
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, 'out_ui', 'step3', 'frames'))
shutil.rmtree(out, ignore_errors=True); os.makedirs(out, exist_ok=True)
data = tempfile.mkdtemp()
env = dict(os.environ, SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=data)
r = subprocess.run(['xvfb-run', '-a', 'love', 'riverwalk', '--screenshots'], cwd=root, env=env, capture_output=True, text=True, timeout=400)
if r.returncode or 'SCREENSHOTS' not in r.stdout: print(r.stdout[-600:], r.stderr[-3000:]); sys.exit(1)
for f in sorted(glob.glob(f'{data}/love/*/s_*.png')):
    a = np.array(Image.open(f).convert('RGBA'))
    if a.shape[:2] != (480, 640): print('unexpected size', f, a.shape); continue
    assert (a[0::2, 0::2] == a[1::2, 1::2]).all(), 'not an exact 2x frame: ' + f
    g = Image.fromarray(a[0::2, 0::2]).convert('RGB')
    n = os.path.basename(f)[2:-4]
    g.save(f'{out}/{n}.png')
    g.resize((960, 720), Image.NEAREST).save(f'{out}/{n}_3x.png')
    g.convert('L').convert('RGB').resize((960, 720), Image.NEAREST).save(f'{out}/{n}_3x_grey.png')
    t = f[:-4] + '.txt'
    if os.path.exists(t): shutil.copy(t, f'{out}/{n}.txt')
    print('frame', n)
shutil.rmtree(data, ignore_errors=True)
