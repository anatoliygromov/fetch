"""tools/hint_frames.py OUT_DIR [LEVEL ...] [--root GAME_ROOT]: runs `love riverwalk --level <LEVEL> --hintshots`
headless (riverwalk/tests_hints.lua, each run with its own save folder) and writes every control hint of each level,
in its zone, to OUT_DIR as a 320 x 240 PNG (the window is 640 x 480, the game drawn at exactly 2x, so every 2nd pixel
is the game's), <name>_4x.png for looking at, <name>.txt (the bodies placed, for tools/layout_qa_menus.py) and
hints.txt (frame, button, text). Default levels: the six of the run. --root: another checkout (before / after)."""
import os, sys, subprocess, tempfile, glob, shutil
import numpy as np
from PIL import Image
args = sys.argv[1:]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if '--root' in args:
    i = args.index('--root'); root = os.path.abspath(args[i + 1]); del args[i:i + 2]
out = os.path.abspath(args[0]); levels = args[1:] or ['riverwalk', 'citypark_tall', 'downtown_tall', 'rooftops', 'soder', 'night']
os.makedirs(out, exist_ok=True)
index = []
for lv in levels:
    data = tempfile.mkdtemp()
    env = dict(os.environ, SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=data)
    r = subprocess.run(['xvfb-run', '-a', 'love', 'riverwalk', '--level', lv, '--hintshots'], cwd=root, env=env,
                       capture_output=True, text=True, timeout=400)
    if r.returncode or 'HINTSHOTS' not in r.stdout: print(lv, 'FAILED', r.stdout[-600:], r.stderr[-3000:]); sys.exit(1)
    hints = [l[5:] for l in r.stdout.splitlines() if l.startswith('HINT ')]
    print(lv, len(hints), 'hints')
    for l in hints: index.append(f'{lv} {l}')
    for f in sorted(glob.glob(f'{data}/love/*/hint_*.png')):
        a = np.array(Image.open(f).convert('RGBA'))
        if a.shape[:2] != (480, 640): print('unexpected size', f, a.shape); continue
        assert (a[0::2, 0::2] == a[1::2, 1::2]).all(), 'not an exact 2x frame: ' + f
        g = Image.fromarray(a[0::2, 0::2]).convert('RGB')
        n = os.path.basename(f)[:-4]
        g.save(f'{out}/{n}.png'); g.resize((1280, 960), Image.NEAREST).save(f'{out}/{n}_4x.png')
        t = f[:-4] + '.txt'
        if os.path.exists(t): shutil.copy(t, f'{out}/{n}.txt')
    shutil.rmtree(data, ignore_errors=True)
open(f'{out}/hints.txt', 'w').write('\n'.join(index) + '\n')
