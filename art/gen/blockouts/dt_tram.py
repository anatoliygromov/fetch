"""Downtown (tall) vintage tram, back lane (arthooks.lua tram lane, rails at the street line minus 10), 46 px/m.
A Stockholm-style old blue and cream tram seen exactly from the side, driving LEFT. True scale: 3.3 m to the top of
the clerestory = 152 px, 10.9 m in the render (500 px: what fits the 512 frame of NB 2.1 at 2K); the game's tram is
lengthened to about 12 m by stamping one more identical window bay (windows are a repeated part, built). Wheels
0.68 m = 31 px on two bogies (wheelbase 1.6 m = 74 px). Floor 0.85 m, window sill 1.75 m, window top 2.65 m.
The trolley pole is drawn by rule after the cut (a thin line; it would leave the frame). Pepper at 1x in the top
left corner for scale (she is not in the scene)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, _ = frame(512, 512, ground=120, pepper_x=4)
G = 500                                            # the rail line
BLUE, CREAM, GLASS, ROOF, DARK, WHEEL, LAMP, DRIVER = ((140, 140, 150, 255), (205, 205, 210, 255), (95, 95, 105, 255),
    (115, 115, 120, 255), (70, 70, 78, 255), (55, 55, 60, 255), (235, 235, 200, 255), (160, 150, 140, 255))
x0, x1 = 6, 505                                    # 500 px
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rectangle([x0 + 18, G - 152, x1 - 18, G - 146], fill=f(ROOF))          # clerestory
    D.rounded_rectangle([x0 + 2, G - 147, x1 - 2, G - 138], 5, fill=f(ROOF))  # roof
    D.rounded_rectangle([x0, G - 140, x1, G - 34], 8, fill=f(BLUE))           # body
    D.rectangle([x0, G - 130, x1, G - 78], fill=f(CREAM))                     # cream window band + letter board
    D.rectangle([x0 + 4, G - 122, x0 + 36, G - 82], fill=f(GLASS))           # front cab window
    D.rectangle([x0 + 14, G - 106, x0 + 26, G - 84], fill=f(DRIVER))         # the driver
    D.rectangle([x0 + 42, G - 122, x0 + 74, G - 36], fill=f(GLASS))          # front door (glazed)
    for i in range(7):                                                        # 7 identical passenger windows
        wx = 92 + i * 52; D.rectangle([wx, G - 122, wx + 39, G - 84], fill=f(GLASS))
    D.rectangle([x1 - 54, G - 122, x1 - 22, G - 36], fill=f(GLASS))          # rear door
    D.rectangle([x1 - 16, G - 122, x1 - 4, G - 84], fill=f(GLASS))           # rear end window
    D.rectangle([x0, G - 38, x1, G - 31], fill=f(DARK))                      # skirt
    D.rectangle([x0, G - 58, x0 + 5, G - 51], fill=f(LAMP))                  # headlamp
    for bc in (125, 386):                                                     # bogies
        D.rectangle([bc - 52, G - 30, bc + 52, G - 16], fill=f(DARK))
        for wc in (bc - 37, bc + 37):
            D.ellipse([wc - 15, G - 31, wc + 15, G - 1], fill=f(WHEEL))
save('dt_tram', c, m, {'ground': G, 'pepper_x': 4, 'pepper_ground': 120, 'bogies': [125, 386], 'wheel_d': 31,
                       'windows': [92 + i * 52 for i in range(7)], 'window_w': 40})
