"""River Walk scale calls still open (STATUS "Known, next"; placement audit item 2): the lamp posts and the rowing
boats, shown in the approved sample-screen look (frames from art/rw-sample-screen 80ec97f, --lookshots at x 450 and
2240) with grey blockouts at the candidate sizes. Prep for the owner's decision; nothing here is game art.
  Lamp: now 101 px (2.2 m, the concept's size, approved art) | 138 px (3.0 m) | 184 px (4.0 m) | 207 px (4.5 m), foot
        on the pavement's back edge (y 174) at the lamp's x (590, screen x 280 with the camera at 310). Beside the
        true-scale house (door 98 px) and lime (trunk 23 px) the 101 px lamp reads as a garden lamp; at 4 m and more
        the lantern (the checkpoint light) is cut by or above the top of the screen on the upper promenade.
  Boat: now about 62 px drawn (56 px deck, 1.2 m) | 160 px (3.5 m, a real rowing boat) outlined in magenta round the
        boat under Pepper. A 160 px boat changes the harbour's play (deck length, gaps, the jetty), so it is a level
        change as well as art.
Writes docs/review/25oct-night/prep/rw_scale_calls_2x.png. Run from the repo root."""
from PIL import Image, ImageDraw

D = 'docs/review/25oct-night/prep/'
GREY, GDK = (150, 152, 160), (110, 112, 122)
MAG = (255, 0, 255)


def lamp(d, cx, foot, h):
    """A park lamp h px tall in real proportions at 46 px a metre: plinth 12 x 18 (0.25 x 0.4 m), post 6 px (0.13 m),
    lantern 20 x 28 (0.45 x 0.6 m) under a cap. The lantern is what lights up at a checkpoint."""
    d.rectangle([cx - 6, foot - 18, cx + 5, foot - 1], fill=GDK)
    d.rectangle([cx - 3, foot - h + 30, cx + 2, foot - 18], fill=GREY)
    top = foot - h
    d.rectangle([cx - 10, top + 6, cx + 9, top + 30], fill=(214, 200, 120))            # lantern (pale yellow)
    d.polygon([(cx - 12, top + 6), (cx, top), (cx + 11, top + 6)], fill=GDK)


lf = Image.open(D + 'rw_lamp_frame_1x.png').convert('RGB')
panels = []
for h, lab in ((None, 'now: 101 px = 2.2 m (approved art)'), (138, '138 px = 3.0 m: lantern top at y 36'),
               (184, '184 px = 4.0 m: lantern top at y -10, mostly cut'), (207, '207 px = 4.5 m: lantern off screen')):
    im = lf.copy()
    if h: lamp(ImageDraw.Draw(im), 280, 174, h)
    panels.append((im, lab))
bf = Image.open(D + 'rw_boat_frame_1x.png').convert('RGB')
b2 = bf.copy(); db = ImageDraw.Draw(b2)
cx, deck = 182, 219                                    # the boat under Pepper (camera 2100)
db.polygon([(cx - 80, deck), (cx + 79, deck), (cx + 70, deck + 14), (cx - 72, deck + 14)], outline=MAG)
panels += [(bf, 'boat now: about 62 px = 1.3 m'), (b2, 'magenta: 160 px = 3.5 m')]
S = 2
W, H = 320 * S, 240 * S
sheet = Image.new('RGB', (W * 4 + 36, 30 + (H + 30) * 2), (30, 30, 34))
ds = ImageDraw.Draw(sheet)
ds.text((8, 8), 'River Walk scale calls (prep, night of 25 Oct): lamp posts and rowing boats at their candidate sizes, '
        'grey and magenta blockouts on the approved sample-screen look, 2x', fill=(240, 240, 240))
for i, (im, lab) in enumerate(panels):
    x = i * (W + 12) if i < 4 else (i - 4) * (W + 12)
    y = 30 if i < 4 else 30 + H + 30
    sheet.paste(im.resize((W, H), Image.NEAREST), (x, y + 18))
    ds.text((x + 4, y + 2), lab, fill=(255, 230, 120))
sheet.save(D + 'rw_scale_calls_2x.png')
print('written', D + 'rw_scale_calls_2x.png')
