"""Blockout for the adult city cyclist (RW hazard, play layer). 46 px/m. Frame 168x126 game px (4:3), ground y 118.
Measures: rider 81 px tall (1.75 m seated head top), wheel 32 px (0.70 m), hubs 51 px apart (1.1 m), bike 83 px long,
saddle 41 px (0.9 m), bars 46 px (1.0 m), head 11 px."""
import numpy as np
from PIL import Image, ImageDraw
G = 118
c = Image.new('RGBA', (168, 126), (255, 0, 255, 255)); d = ImageDraw.Draw(c)
m = Image.new('L', (168, 126), 0); dm = ImageDraw.Draw(m)          # subject mask for the checker
pep = Image.fromarray(np.array(Image.open('/home/claude/fetch/riverwalk/art/pepper.png').convert('RGBA'))[0:52, 0:60]); pep = pep.crop(pep.getbbox())
c.alpha_composite(pep, (6, G - pep.height))
WHEEL, BODY, FRAME = (70, 70, 80, 255), (175, 175, 180, 255), (110, 110, 120, 255)
rx, fx, wy = 88, 139, G - 16
for D in (d, dm):
    f = (lambda col: col) if D is d else (lambda col: 255)
    for x in (rx, fx): D.ellipse([x - 16, wy - 16, x + 15, wy + 15], outline=f(WHEEL), width=2)
    crank = (110, G - 13); saddle = (101, G - 41); bars = (133, G - 46)
    D.line([(rx, wy), crank, saddle, (rx, wy)], fill=f(FRAME), width=2)       # rear triangle
    D.line([crank, (128, G - 38), saddle], fill=f(FRAME), width=2)              # down tube, top tube
    D.line([(fx, wy), (128, G - 38), bars], fill=f(FRAME), width=2)             # fork, stem
    D.rectangle([142, G - 42, 153, G - 34], fill=f((150, 120, 80, 255)))       # basket
    D.line([(96, G - 42), (106, G - 42)], fill=f(FRAME), width=2)              # saddle
    D.line([saddle, (113, G - 66)], fill=f(BODY), width=9)                     # torso, hip to shoulder
    D.ellipse([111, G - 81, 122, G - 70], fill=f(BODY))                        # head 11 px, top at G-81
    D.line([(115, G - 63), (133, G - 47)], fill=f(BODY), width=4)              # arm to bars
    D.line([saddle, (116, G - 34), (113, crank[1] + 5)], fill=f(BODY), width=6)  # thigh, shin to pedal
c.save('blockouts/rw_cyclist_adult.png'); m.save('blockouts/rw_cyclist_adult_mask.png')
c.convert('RGB').resize((168 * 8, 126 * 8), Image.NEAREST).save('blockouts/rw_cyclist_adult_8x.png')
bb = m.getbbox(); print('subject bbox', bb, 'w', bb[2] - bb[0], 'h', bb[3] - bb[1])
