"""Downtown (tall) cargo bike, the street hazard (arthooks.lua drawCargo, hit box the left 80 x 26 px: the cargo box
and the front wheel). A long john (box between the front wheel and the handlebar), riding LEFT, ridden by the
baker's delivery man. 46 px/m: rider 1.85 m with the helmet = 85 px (the River Walk riders are the bar); bike 2.5 m
= 116 px; front wheel 20 in (0.5 m) = 23 px, back wheel 26 in (0.67 m) = 31 px; box 0.95 x 0.48 m = 44 x 22 px,
its top 0.65 m up (30 px, the hit box's 26 plus the rim); bars 1.05 m (48 px), saddle 0.9 m (42 px).
NB 2.1 pixel mode at 1K: a 256 frame comes back 1:1 (docs/art_generation.md). Pepper at 1x on the same ground."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=200, pepper_x=8)
WHEEL, BODY, FRAME, HELMET, BOX, BREAD = ((70, 70, 80, 255), (175, 175, 180, 255), (110, 110, 120, 255),
                                          (215, 215, 220, 255), (150, 120, 80, 255), (200, 170, 120, 255))
X = 80                                             # the bike's front (left) end
fw, rw = (X + 12, G - 12, 11), (X + 100, G - 16, 15)
crank, saddle, head, bars = (X + 80, G - 13), (X + 88, G - 42), (X + 70, G - 30), (X + 68, G - 48)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    for cx, cy, r in (fw, rw): D.ellipse([cx - r, cy - r, cx + r, cy + r], outline=f(WHEEL), width=2)
    D.line([(fw[0], fw[1]), (X + 22, G - 9), (head[0], G - 9), crank], fill=f(FRAME), width=2)   # the long low frame
    D.line([(head[0], G - 9), head, bars], fill=f(FRAME), width=2)                              # head tube, stem
    D.line([crank, saddle], fill=f(FRAME), width=2); D.line([crank, (rw[0], rw[1]), saddle], fill=f(FRAME), width=2)
    D.line([(bars[0] - 3, bars[1]), (bars[0] + 4, bars[1])], fill=f(FRAME), width=2)            # handlebar
    D.line([(saddle[0] - 4, saddle[1]), (saddle[0] + 5, saddle[1])], fill=f(FRAME), width=2)    # saddle
    D.rectangle([X + 20, G - 30, X + 63, G - 9], fill=f(BOX))                                   # the cargo box
    for bx in (X + 24, X + 42): D.ellipse([bx, G - 35, bx + 14, G - 27], fill=f(BREAD))         # loaves over the rim
    D.line([saddle, (X + 80, G - 67)], fill=f(BODY), width=10)                                  # torso
    D.ellipse([X + 73, G - 80, X + 84, G - 69], fill=f(BODY))                                   # head, 11 px
    D.chord([X + 71, G - 85, X + 86, G - 72], 180, 360, fill=f(HELMET))                         # helmet, top at G-85
    D.line([(X + 78, G - 63), bars], fill=f(BODY), width=4)                                     # arm to the bars
    D.line([saddle, (X + 73, G - 32), (crank[0] - 2, crank[1] + 4)], fill=f(BODY), width=6)     # leg to the pedal
save('dt_cargo_bike', c, m, {'ground': G, 'pepper_x': 8, 'front_wheel': fw, 'back_wheel': rw})
