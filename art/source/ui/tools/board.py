import sys, os, json, numpy as np
from PIL import Image, ImageDraw
D = sys.argv[1]; out = sys.argv[2]; S = int(sys.argv[3]) if len(sys.argv) > 3 else 4
order = ['panel_menu','panel_wide','panel_menu_cream','panel_wide_cream','row_normal','row_selected','row_disabled','ribbon','health_full','health_empty',
 'cursor_paw','pepper_head','heart_full','heart_empty','icon_clock','icon_bone','icon_bone_gold','icon_ball','icon_lock','icon_speaker',
 'medal_nohit_won','medal_bones_won','medal_par_won','medal_nohit_dark','medal_bones_dark','medal_par_dark','btn_a','btn_b','btn_a_bronze','dpad','volume_bar','toggle_on','toggle_off']
order += ['digit_'+c for c in '0123456789'] + ['digit_x','digit_slash','digit_colon'] + ['letter_'+c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
ims = [(n, Image.open(f'{D}/{n}.png')) for n in order if os.path.exists(f'{D}/{n}.png')]
W = 1500; x = y = 12; rowh = 0; pos = []
for n, im in ims:
    w, h = im.width*S, im.height*S
    if x + w > W - 12: x = 12; y += rowh + 26; rowh = 0
    pos.append((n, im, x, y)); x += w + 18; rowh = max(rowh, h)
H = y + rowh + 30
bg = Image.new('RGBA', (W, H), (52, 58, 78, 255)); d = ImageDraw.Draw(bg)
for n, im, x, y in pos:
    bg.alpha_composite(im.resize((im.width*S, im.height*S), Image.NEAREST), (x, y))
    d.text((x, y + im.height*S + 3), f"{n.replace('letter_','').replace('digit_','')} {im.width}x{im.height}", fill=(220, 220, 230))
bg.save(out); print(bg.size)
