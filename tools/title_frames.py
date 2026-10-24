"""tools/title_frames.py OUT_DIR: runs `love riverwalk --titleshots` headless and writes the title and menu frames
(320 x 240, drawn straight to a canvas by riverwalk/tests_titleui.lua) to OUT_DIR, each also at 3x in colour and in
greyscale (<name>_3x.png, <name>_3x_grey.png), with its placed bodies (<name>.txt, for tools/layout_qa8.py), and the
title loop as an animated GIF at 2x (title_loop_2x.gif, 12 fps)."""
import os, sys, subprocess, tempfile, glob, shutil
from PIL import Image

out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'out_ui/pilot2/frames')
os.makedirs(out, exist_ok=True)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = tempfile.mkdtemp()
env = dict(os.environ, SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=data)
r = subprocess.run(['xvfb-run', '-a', 'love', 'riverwalk', '--titleshots'], cwd=root, env=env, capture_output=True, text=True, timeout=180)
print(r.stdout[-300:], r.stderr[-2000:] if r.returncode else '')
gif = []
for f in sorted(glob.glob(f'{data}/love/*/t_*.png')):
    n = os.path.basename(f)[2:-4]
    im = Image.open(f).convert('RGB')
    if n.startswith('gif_'): gif.append(im); continue
    im.save(f'{out}/{n}.png')
    im.resize((960, 720), Image.NEAREST).save(f'{out}/{n}_3x.png')
    g = im.convert('L').convert('RGB'); g.resize((960, 720), Image.NEAREST).save(f'{out}/{n}_3x_grey.png')
    t = f[:-4] + '.txt'
    if os.path.exists(t): shutil.copy(t, f'{out}/{n}.txt')
    print('frame', n)
if gif:
    big = [g.resize((640, 480), Image.NEAREST) for g in gif]
    big[0].save(f'{out}/title_loop_2x.gif', save_all=True, append_images=big[1:], duration=83, loop=0, optimize=False, disposal=1)
    print('gif', len(big), 'frames')
shutil.rmtree(data, ignore_errors=True)
