"""tools/ui_sheet.py FRAMES_DIR OUT.png [SHOT ...]: a contact sheet of the UI's real frames (tools/ui_frames.py) at 2x,
four across, each with its name. Without SHOTs: every frame in FRAMES_DIR."""
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
D, out = sys.argv[1], sys.argv[2]
shots = sys.argv[3:] or sorted(os.path.basename(f)[:-4] for f in glob.glob(f'{D}/*.png') if not f.endswith('_3x.png') and '_guides' not in f)
try: font = ImageFont.load_default(size=18)
except TypeError: font = ImageFont.load_default()
N = 4; cw, chh = 640 + 16, 480 + 36
rows = (len(shots) + N - 1) // N
sheet = Image.new('RGB', (N * cw + 16, rows * chh + 16), (30, 30, 35)); d = ImageDraw.Draw(sheet)
for i, s in enumerate(shots):
    im = Image.open(f'{D}/{s}.png').convert('RGB').resize((640, 480), Image.NEAREST)
    x, y = 16 + (i % N) * cw, 16 + (i // N) * chh
    d.text((x, y), s, font=font, fill=(232, 232, 236)); sheet.paste(im, (x, y + 26))
sheet.save(out); print(out, sheet.size, len(shots), 'screens')
