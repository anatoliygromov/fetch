"""tools/card_shots.py: the level select's pictures (ui/hud-v8 step 3, 0 credits). Runs `love riverwalk --cardshots`
headless (riverwalk/tests_cards.lua: each level at its characteristic spot, the camera settled, the level drawn
without HUD or talk at 320 x 240) and crops each frame 1:1 (a native 1x crop, no scaling) to W x H round Pepper:
her body two fifths across, her feet FEET px from the top. Writes riverwalk/art/ui/cards/<name>.png and, for looking
at, out_ui/step3/cards_3x.png (every picture at 3x) and the uncropped frames.
  python3 tools/card_shots.py            (from the repo root; needs LOVE and xvfb-run)
CARDS_ALL=1 shoots every eighth of each level instead, to choose new spots (tests_cards.lua SPOTS)."""
import os, re, sys, subprocess, tempfile, glob, shutil
from PIL import Image
W, H, FEET = 216, 118, 98
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, 'riverwalk', 'art', 'ui', 'cards'); os.makedirs(out, exist_ok=True)
look = os.path.join(root, 'out_ui', 'step3', 'cards'); os.makedirs(look, exist_ok=True)
data = tempfile.mkdtemp()
env = dict(os.environ, SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=data)
r = subprocess.run(['xvfb-run', '-a', 'love', 'riverwalk', '--cardshots'], cwd=root, env=env, capture_output=True, text=True, timeout=600)
if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
made = []
for m in re.finditer(r'^card (\S+) x (\d+) y (\d+) cam (\d+),(\d+)', r.stdout, re.M):
    name, x, y, cam, camy = m.group(1), *map(int, m.groups()[1:])
    src = glob.glob(f'{data}/love/*/card_{name}_{x}.png')[0]
    im = Image.open(src).convert('RGB')
    sx, sy = x - cam, y - camy                                     # Pepper's feet on screen
    x0 = max(0, min(320 - W, sx - W * 2 // 5)); y0 = max(0, min(240 - H, sy - FEET))
    crop = im.crop((x0, y0, x0 + W, y0 + H))
    if os.environ.get('CARDS_ALL'): crop.save(f'{look}/{name}_{x}.png'); continue
    crop.save(f'{out}/{name}.png'); im.save(f'{look}/{name}_frame.png'); made.append((name, crop))
    print('card', name, 'x', x, 'crop', x0, y0)
if made:
    pad = 6; sheet = Image.new('RGB', (pad + 3 * (W + pad), pad + 2 * (H + pad)), (30, 20, 16))
    for i, (n, c) in enumerate(made): sheet.paste(c, (pad + (i % 3) * (W + pad), pad + (i // 3) * (H + pad)))
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(root, 'out_ui', 'step3', 'cards_3x.png'))
shutil.rmtree(data, ignore_errors=True)
