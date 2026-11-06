"""City Park tall: the oak climbing parts as one parts sheet (6 Nov, family cp_boughs_06nov). The owner rejected the
code-drawn branches, boughs, twigs, leaf masses, nest, stump and trunks as lifeless; one render gives the bark and leaf
material for all of them, cut 1:1 into parts that the game stamps over the SAME boxes (scene.lua). True scale, 46 px/m:
the ledges' bark body is 6 px tall (the one-way box), 8 at the trunk end, 4 at the tip; the big oak's trunk is 32 px
(BIG OAK box), the small trunks 8, 10 and 12 px; the stump is its 24 x 28 box; the nest 28 x 10 plus twigs; the low
bough 32 x 16 (its box) rising 16 px over 26 into a leaf mass about 44 x 34. 512 frame, 2K at 4 px per art px.
Grey key: dark grey = bark, light grey = leaves, mid grey = the nest's woven twigs, near-white = the stump's cut top."""
import sys; sys.path.insert(0, 'tools')
from blockout_lib import frame, save
W, H = 512, 512
c, d, m, dm, G = frame(W, H, ground=H - 6, pepper_x=4)
BARK, LEAF, NEST, CUT = (95, 95, 100, 255), (180, 180, 185, 255), (140, 140, 145, 255), (215, 215, 215, 255)
parts = {}


def limb(D, f, x0, x1, y, base=8, body=6, tip=4, twig=True):
    """a straight limb, its top flat at y: base thick at x0 (cut where it meets a trunk out of view), tapering on the
    underside to the tip at x1, a leafy twig rising past the tip"""
    D.polygon([(x0, y), (x1, y), (x1, y + tip - 1), (x1 - 24, y + body - 1), (x0 + 18, y + body - 1), (x0, y + base - 1)], fill=f(BARK))
    if twig:
        D.line([(x1, y + 1), (x1 + 10, y - 7)], fill=f(BARK), width=2)
        D.ellipse([x1 + 4, y - 18, x1 + 24, y - 5], fill=f(LEAF))


for D, f in ((d, lambda col: col), (dm, lambda col: 255)):
    # 1 the big oak's trunk: 32 px, a root flare at its foot (BIG OAK, x 2744-2776)
    D.rectangle([80, 150, 111, G - 1], fill=f(BARK))
    D.polygon([(72, G - 1), (80, G - 16), (111, G - 16), (119, G - 1)], fill=f(BARK))
    # 2 three small trunks, 8, 10 and 12 px, 140 tall, small flares
    for x, w in ((140, 8), (162, 10), (188, 12)):
        D.rectangle([x, G - 140, x + w - 1, G - 1], fill=f(BARK))
        D.polygon([(x - 3, G - 1), (x, G - 8), (x + w - 1, G - 8), (x + w + 2, G - 1)], fill=f(BARK))
    # 3 the stump (STUMP, 24 x 28): bark sides, a light cut top
    D.rectangle([230, G - 28, 253, G - 1], fill=f(BARK))
    D.rectangle([230, G - 28, 253, G - 25], fill=f(CUT))
    # 4 two long limbs, tip to the right (mirrored in the game for the other side)
    limb(D, f, 150, 450, 40)
    limb(D, f, 150, 360, 84)
    # 5 a fork: a bough lying across a trunk's top, tips both ways
    D.rectangle([272, 140, 295, 190], fill=f(BARK))
    D.polygon([(170, 130), (400, 130), (400, 133), (360, 135), (300, 138), (268, 138), (210, 135), (170, 133)], fill=f(BARK))
    for x, s in ((170, -1), (400, 1)):
        D.line([(x, 131), (x + s * 10, 123)], fill=f(BARK), width=2)
        D.ellipse([min(x + s * 4, x + s * 24), 112, max(x + s * 4, x + s * 24), 125], fill=f(LEAF))
    # 6 the low bough: level 32 x 16 (free end left, rounded), then rising 16 px over 26 into a leaf mass
    D.ellipse([150, 230, 166, 245], fill=f(BARK)); D.rectangle([158, 230, 182, 245], fill=f(BARK))
    D.polygon([(182, 230), (196, 224), (208, 214), (210, 222), (198, 234), (182, 245)], fill=f(BARK))
    D.ellipse([186, 188, 232, 224], fill=f(LEAF))
    # 7 the magpie's nest: a bowl of twigs 30 x 12 in a small fork
    D.ellipse([300, 222, 334, 240], fill=f(NEST)); D.rectangle([300, 222, 334, 230], fill=f(NEST))
    D.line([(296, 238), (338, 238)], fill=f(BARK), width=3)
    # 8 leaf clumps, five sizes (decoration at tips, round the low bough's mass)
    x = 250
    for w, h in ((14, 10), (18, 12), (22, 15), (28, 18), (36, 24)):
        D.ellipse([x, 300 - h, x + w - 1, 299], fill=f(LEAF)); x += w + 12
    x = 250
    for w, h in ((16, 11), (20, 14), (26, 17), (32, 20)):
        D.ellipse([x, 350 - h, x + w - 1, 349], fill=f(LEAF)); x += w + 14
save('cp_boughs', c, m, {'ground': G, 'pepper_x': 4, 'grey': {'bark': BARK[:3], 'leaf': LEAF[:3], 'nest': NEST[:3], 'cut': CUT[:3]},
                         'parts': {'big_trunk': [72, 150, 120, G], 'small_trunks': [[140, 8], [162, 10], [188, 12]],
                                   'stump': [230, G - 28, 254, G], 'limb1': [150, 40, 450], 'limb2': [150, 84, 360],
                                   'fork': [170, 130, 400, 'trunk', 272, 296], 'lowbough': [150, 230, 182, 246],
                                   'nest': [300, 222, 335, 240], 'clumps_y': [300, 350]}})
