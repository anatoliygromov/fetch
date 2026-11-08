"""Söder cafe parasol with its pole (retry 1 of the pilot sh_cafe_table, 8 Nov): Pixel Engine Image draws at exactly
66 x 43. Art (0, 0) = game (2691, 107): rows 0-13 the canopy, its top row flat over the PARASOL box (x 2692-2756, Pepper
stands on y 108), rows 14-42 the pole (cols 31-34, x 2722-2725) down to the table top (y 150). Pepper at 1x beside it
on the street (y 176) for scale only (Pixel Engine takes no references)."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
c, d, m, dm, G = frame(256, 256, ground=216, pepper_x=8)
OX, OY = 120, G - 69
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.rectangle([OX + 1, OY, OX + 64, OY], fill=f((200, 200, 206, 255)))
    D.rectangle([OX, OY + 1, OX + 65, OY + 13], fill=f((200, 200, 206, 255)))
    D.rectangle([OX + 31, OY + 14, OX + 34, OY + 42], fill=f((70, 70, 76, 255)))
save('sh_parasol', c, m, {'ox': OX, 'oy': OY, 'art': [66, 43], 'ground': G, 'game_origin': [2691, 107]})
