"""Söder cafe table (retry 1 of the pilot sh_cafe_table, 8 Nov): Pixel Engine Image draws at exactly 50 x 26.
Art (0, 0) = game (2699, 150): rows 0-7 the top (TABLE box x 2700-2748, y 150-157, ink 1 px outside left and right),
rows 8-25 the iron column and curly legs down to the street (y 176). Pepper at 1x beside it for scale only."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=216, pepper_x=8)
OX, OY = 128, G - 26
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rectangle([OX, OY, OX + 49, OY + 7], fill=f((120, 120, 128, 255)))
    D.rectangle([OX + 22, OY + 8, OX + 27, OY + 13], fill=f((60, 60, 66, 255)))
    for s in (-1, 1):
        cx = OX + 24.5
        D.line([(cx + s * 2, OY + 13), (cx + s * 8, OY + 18), (cx + s * 14, OY + 22), (cx + s * 18, OY + 24)], fill=f((60, 60, 66, 255)), width=2)
save('sh_table', c, m, {'ox': OX, 'oy': OY, 'art': [50, 26], 'ground': G, 'game_origin': [2699, 150]})
