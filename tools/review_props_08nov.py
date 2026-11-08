#!/usr/bin/env python3
"""review_props_08nov.py PIECE LEVEL XS FILE=WxH [FILE=WxH ...]: the review folder of one 8 Nov prop
(docs/review/08nov/props/PIECE/): the 1x files, in-game frames (LOOK_SWEEP=1 LOOK_XS, look on) in colour and greyscale at
1x and 4x, the files at 5x beside the approved bench, bin and lamp, asset_qa (play layer; the tool has no Söder or Night
look, so --level dt --fade 0: these props are drawn unfaded) and the qa_card per file.
  python3 -I tools/review_props_08nov.py cafe_table soder 2600,2680 riverwalk/levelart/soder/props/parasol.png=66x43 ..."""
import os, sys, shutil, subprocess, tempfile, glob
from PIL import Image, ImageOps
piece, level, xs = sys.argv[1], sys.argv[2], sys.argv[3]
files = [a.split('=') for a in sys.argv[4:]]
R = f'docs/review/08nov/props/{piece}'; os.makedirs(R, exist_ok=True)
for f, _ in files: shutil.copy(f, R)
d = tempfile.mkdtemp()
env = dict(os.environ, SDL_AUDIODRIVER='dummy', XDG_DATA_HOME=d, LOOK_SWEEP='1', LOOK_XS=xs)
subprocess.run(['timeout', '180', 'xvfb-run', '-a', 'love', 'riverwalk', '--level', level, '--lookshots'], env=env,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
frames = []
for p in sorted(glob.glob(f'{d}/love/*/sweep_*.png')):
    x = p.rsplit('_x', 1)[1][:-4]; n = f'{R}/frame_x{x}'
    im = Image.open(p).convert('RGB'); g = ImageOps.grayscale(im)
    im.save(n + '.png'); g.save(n + '_grey.png')
    im.resize((1280, 960), Image.NEAREST).save(n + '_4x.png'); g.resize((1280, 960), Image.NEAREST).save(n + '_4x_grey.png')
    frames.append(n + '.png')
ims = [Image.open(f).convert('RGBA') for f, _ in files] + \
      [Image.open(f'riverwalk/art/scene/{n}.png').convert('RGBA') for n in ('bench', 'bin', 'lamp_post')]
W = sum(i.width for i in ims) + 8 * (len(ims) + 1); H = max(i.height for i in ims) + 16
c = Image.new('RGBA', (W, H), (196, 170, 150, 255) if level == 'soder' else (40, 52, 96, 255)); x = 8
for i in ims: c.alpha_composite(i, (x, H - 8 - i.height)); x += i.width + 8
c.resize((W * 5, H * 5), Image.NEAREST).save(f'{R}/x5_beside_bench_bin_lamp.png')
for f, slot in files:
    n = os.path.basename(f)[:-4]; j = f'{d}/qa_{n}.json'
    subprocess.run(['python3', '-I', 'tools/asset_qa.py', '--file', f, '--layer', 'play', '--level', 'dt', '--fade', '0', '--json', j])
    for old in glob.glob(f'{R}/*_{n}.png'): os.remove(old)
    subprocess.run(['python3', '-I', 'tools/qa_card.py', j, R, n, '--frame', f'{n}={frames[0]}', '--slot', f'{n}={slot}'])
print('frames', frames)
