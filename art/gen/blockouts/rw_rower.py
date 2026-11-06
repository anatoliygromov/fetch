"""The rower of the River Walk rowing boats (screens 8-9, the harbour), the only DRAWN part of the boat (night 6 Nov:
the hull and the oars are built by rule, tools/build_rw_rowboat.py; the rowing loop is keyed by rule from this still).
Design target: art/gen/concepts/rw_rowboat_concept_b.png (the grandpa rower: flat cap, white beard, navy knit jumper).
True scale on Pepper's line (46 px/m): he sits on the middle thwart (seat top world y 216, 8 px under the gunwale at
y 208), seat to cap top 0.92 m = 42 px, so his cap top is at y 174, level with Pepper's head when she stands on the
boat's deck (y 212). Head 11 px (0.24 m), face to the LEFT (the bow, as in the concept). Both hands forward at chest
height as if on the oar handle; no oar is drawn (the oars are built by rule and the arms re-keyed per frame).
Art 31 x 43: row 0 = world y 174 (cap top), the gunwale crosses at row 34, seat row 42.
256 frame: GPT 2.5 Sunburst 1K draws on a 4 px grid (tools/grid4_cut.py), as the cargo bike rider did (5 Nov).
Pepper at 1x stands on the deck line (world y 212 = frame row 180) beside him for scale."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 256, 256
G = 180                                   # Pepper's feet: the boat's deck, world y 212
c, d, m, dm, _ = frame(W, H, ground=G, pepper_x=8)
OX, OY = 112, G - 38                      # art (0, 0) = world y 174 (cap top), 38 px above the deck
CAP, SKIN, BEARD, JUMPER, TROUS, HAND = ((80, 80, 88, 255), (225, 190, 160, 255), (235, 235, 238, 255),
                                         (60, 80, 140, 255), (70, 70, 80, 255), (215, 180, 150, 255))
def P(pts): return [(OX + x, OY + y) for x, y in pts]
def R(x0, y0, x1, y1): return [OX + x0, OY + y0, OX + x1, OY + y1]
for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    D.polygon(P([(12, 30), (14, 15), (25, 14), (29, 21), (30, 34), (29, 42), (13, 42)]), fill=f(JUMPER))   # torso, back to the right
    D.rectangle(R(2, 34, 26, 42), fill=f(TROUS))                                                           # thighs forward to the knees
    D.ellipse(R(10, 2, 21, 13), fill=f(SKIN))                                                              # head, 11 px, facing left
    D.polygon(P([(9, 9), (18, 9), (18, 13), (14, 16), (10, 15)]), fill=f(BEARD))                          # short white beard
    D.polygon(P([(9, 0), (23, 0), (24, 4), (7, 5), (7, 3)]), fill=f(CAP))                                 # flat cap, brim to the left
    D.line(P([(18, 18), (10, 24), (5, 23)]), fill=f(JUMPER), width=5)                                     # the near arm, forward
    D.ellipse(R(0, 20, 5, 26), fill=f(HAND))                                                               # both fists, on the handle
save('rw_rower', c, m, {'ox': OX, 'oy': OY, 'art': [31, 43], 'ground': G, 'pepper_x': 8,
                        'world_row0': 174, 'gunwale_row': 34, 'seat_row': 42})
