#!/bin/sh
# tools/rw_sample_frames.sh: the River Walk sample screen review frames (docs/review/25oct/): screens 1, 4 and 10 as
# the game draws them (look on, no HUD), 1x and a 3x colour | greyscale sheet, and before/after (the before frames
# were made from prod/integrate c1c37a4), then the QA cards for the three new pieces.
set -e
X=$(mktemp -d); O=docs/review/25oct
LOOK_SPOTS="60,184;1074,184;3080,184" SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$X timeout 120 xvfb-run -a love riverwalk --level riverwalk --lookshots >/dev/null 2>&1 || true
D=$(ls -d $X/love/*)
python3 -I - "$D" "$O" <<'PY'
import sys
from PIL import Image
D, out = sys.argv[1], sys.argv[2] + '/'
for n, name in (('01', 'rw_sample_screen1'), ('02', 'rw_sample_screen4'), ('03', 'rw_sample_screen10')):
    im = Image.open(f'{D}/look_{n}_after.png').convert('RGB'); im.save(out + name + '_1x.png')
    W, H = im.size
    c = Image.new('RGB', (W * 3 * 2 + 12, H * 3 + H + 12), (30, 30, 34))
    c.paste(im.resize((W * 3, H * 3), Image.NEAREST), (0, 0)); c.paste(im.convert('L').convert('RGB').resize((W * 3, H * 3), Image.NEAREST), (W * 3 + 12, 0))
    c.paste(im, (0, H * 3 + 12)); c.paste(im.convert('L').convert('RGB'), (W + 12, H * 3 + 12))
    c.save(out + name + '_sheet.png')
for s in ('1', '4'):
    b = Image.open(out + f'rw_screen{s}_before_1x.png').convert('RGB'); a = Image.open(out + f'rw_sample_screen{s}_1x.png').convert('RGB')
    c = Image.new('RGB', (320 * 3 * 2 + 12, 240 * 3), (30, 30, 34))
    c.paste(b.resize((960, 720), Image.NEAREST), (0, 0)); c.paste(a.resize((960, 720), Image.NEAREST), (972, 0)); c.save(out + f'rw_screen{s}_before_after_3x.png')
PY
mkdir -p out
python3 -I tools/asset_qa.py --file riverwalk/art/scene/rw_home.png --layer back --level rw --fade 0.28 --building --json out/qa_home.json | head -1
python3 -I tools/asset_qa.py --file riverwalk/art/scene/rw_lime.png --layer back --level rw --fade 0.28 --json out/qa_lime.json | head -1
python3 -I tools/asset_qa.py --file art/source/rw_rail_bg_assembled.png --layer back --level rw --fade 0.28 --json out/qa_rail.json | head -1
python3 -I -c "
import json
a = []
for f in ('home', 'lime', 'rail'): a += json.load(open(f'out/qa_{f}.json'))
json.dump(a, open('out/qa_rw_sample.json', 'w'))"
F=$O/rw_sample_screen1_1x.png
python3 -I tools/qa_card.py out/qa_rw_sample.json $O/cards rw_home rw_lime rw_rail_bg_assembled --frame rw_home=$F --frame rw_lime=$F --frame rw_rail_bg_assembled=$F --slot rw_home=184x180 --slot rw_lime=250x251 --slot rw_rail_bg_assembled=343x50
