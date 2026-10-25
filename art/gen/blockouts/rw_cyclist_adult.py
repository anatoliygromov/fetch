"""Adult city cyclist (River Walk hazard, char layer). 46 px/m: head top with helmet 1.85 m = 85 px, bike 1.8 m = 83 px,
wheel 0.70 m = 32 px, hubs 51 px apart, saddle 41 px, bars 46 px, head 11 px, helmet 3 px on top."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame()
WHEEL, BODY, FRAME, HELMET = (70, 70, 80, 255), (175, 175, 180, 255), (110, 110, 120, 255), (215, 215, 220, 255)
rx, fx, wy = 78, 129, G - 16
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    for x in (rx, fx): D.ellipse([x - 16, wy - 16, x + 15, wy + 15], outline=f(WHEEL), width=2)
    crank, saddle, bars = (100, G - 13), (91, G - 41), (123, G - 46)
    D.line([(rx, wy), crank, saddle, (rx, wy)], fill=f(FRAME), width=2)
    D.line([crank, (118, G - 38), saddle], fill=f(FRAME), width=2)
    D.line([(fx, wy), (118, G - 38), bars], fill=f(FRAME), width=2)
    D.rectangle([132, G - 42, 143, G - 34], fill=f((150, 120, 80, 255)))      # basket
    D.line([(86, G - 42), (96, G - 42)], fill=f(FRAME), width=2)              # saddle
    D.line([saddle, (103, G - 66)], fill=f(BODY), width=9)                    # torso
    D.ellipse([101, G - 81, 112, G - 70], fill=f(BODY))                       # head, 11 px
    D.chord([99, G - 85, 114, G - 72], 180, 360, fill=f(HELMET))              # helmet, top at G-85
    D.line([(105, G - 63), (123, G - 47)], fill=f(BODY), width=4)             # arm
    D.line([saddle, (106, G - 34), (103, crank[1] + 5)], fill=f(BODY), width=6)  # leg
save('rw_cyclist_adult', c, m, {'ground': G, 'pepper_x': 4})
