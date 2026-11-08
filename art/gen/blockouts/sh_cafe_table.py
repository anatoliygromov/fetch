"""Söder Hill cafe table with its parasol (play, 46 px/m; 8 Nov props pilot, family sh_props_08nov).
The boxes are fixed by riverwalk/level/soder.lua (section 9, street y 176): PARASOL oneway x 2692-2756, y 108-112 (Pepper
stands on its top), TABLE solid x 2700-2748, y 150-157 (a ledge; 19 px to crawl under), the pole decor x 2722-2726.
Art 66 x 69, drawn at game (2691, 107): rows 0-13 the canopy (row 0 its ink on y 107, the top flat over the whole box),
rows 14-42 the pole, rows 43-50 the table top (50 px, ink 1 px outside the box), rows 51-68 the curly iron legs to the
street. Frame 256 x 256 (GPT 2.5 Sunburst 1K draws the blockout grid at 4 image px per art px), Pepper at 1x on the same
street for scale. The cut splits it at row 43: sh_parasol (66 x 43, with its pole) and sh_table (50 x 26)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 256, 256
c, d, m, dm, G = frame(W, H, ground=H - 40, pepper_x=8)
OX, OY = 120, G - 69                     # art (0, 0) = game (2691, 107)
CANOPY, VAL, POLE, TOP, RIM, LEG = (200, 200, 206, 255), (165, 165, 172, 255), (70, 70, 76, 255), \
    (120, 120, 128, 255), (95, 95, 102, 255), (60, 60, 66, 255)
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rectangle([OX + 1, OY, OX + 64, OY], fill=f(CANOPY))                  # the flat top Pepper stands on
    D.rectangle([OX, OY + 1, OX + 65, OY + 9], fill=f(CANOPY))              # the canopy
    for i in range(6):                                                      # the scalloped valance, 6 x 11 px
        x0 = OX + i * 11
        D.rectangle([x0, OY + 10, x0 + 10, OY + 11], fill=f(VAL))
        D.ellipse([x0 + 1, OY + 9, x0 + 9, OY + 13], fill=f(VAL))
    D.rectangle([OX + 31, OY + 14, OX + 34, OY + 42], fill=f(POLE))         # the pole, down into the table top
    D.rectangle([OX + 8, OY + 43, OX + 57, OY + 50], fill=f(TOP))           # the round table top seen side-on
    D.rectangle([OX + 8, OY + 47, OX + 57, OY + 50], fill=f(RIM))           # its thick rim
    D.rectangle([OX + 30, OY + 51, OX + 35, OY + 56], fill=f(LEG))          # the iron column
    for s in (-1, 1):                                                       # two curly legs out to the feet
        cx = OX + 32.5
        pts = [(cx + s * 2, OY + 56), (cx + s * 6, OY + 59), (cx + s * 11, OY + 62), (cx + s * 15, OY + 65), (cx + s * 18, OY + 67)]
        D.line(pts, fill=f(LEG), width=2)
        fx = int(cx + s * 18)
        D.ellipse([fx - 2, OY + 64, fx + 2, OY + 68], outline=f(LEG), width=1)   # the scroll at the foot
        D.line([(cx + s * 2, OY + 57), (cx + s * 4, OY + 67)], fill=f(LEG), width=2)  # the inner (back) leg
save('sh_cafe_table', c, m, {'ox': OX, 'oy': OY, 'art': [66, 69], 'ground': G, 'game_origin': [2691, 107],
                             'split_row': 43})
