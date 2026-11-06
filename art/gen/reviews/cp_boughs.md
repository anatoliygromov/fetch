Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), round 1, 6 Nov 2026

# Review gate 8: cp_boughs_06nov (City Park tall climbing parts, branch art/cp-boughs-06nov, head d9a337f)

Frames are mine: whole level swept at camera y 144 / 24 / 0 (x every 280) plus y 70 and 110 at the low bough, in
colour, 1x (art/gen/reviews/cp_boughs_frames/, 3x/4x crops of them read by eye). Pieces at 5x beside Pepper, bench,
bin, lamp: cp_boughs_frames/pieces_5x_beside_bench_bin_lamp_pepper.png, s4_limbs.png, s4_trunks.png. Positions are
screen x,y of the 1x frame unless "world". Real-world size assumed: Pepper (labrador) shoulder 0.6 m = 28 px.
asset_qa --file: limb, limbx, low, stump PASS; low_leaves, clumps, nest, trunk, trunk9, trunk10 report "FAIL" under
--file only because they are not registered as decoration (outline rule for play); check_backdrop: BACKDROP OK.

## Scale (46 px/m play/back)
- Limbs 8-9 px thick = 0.18 m; thick limb 336 px long = 7.3 m, thin 249 px = 5.4 m. Big oak trunk 33 px = 0.72 m
  (a park oak, fine). Small trunks 9-10 px = 0.2 m. Stump 24 x 28 = 0.5 x 0.6 m (a stump, fine). Low bough 32 x 16 = 0.7 x 0.35 m.
- Owner question: a 0.2 m trunk (9-10 px) carries a 0.18 m limb that is 4-5 m long (fork ledges at world y 130-300,
  e.g. frame y144 x1120 at (95-155,45-65)). The limb is as thick as its tree.

## Per piece, 9 items (1 Scale, 2 Layer, 3 Outline, 4 Shapes, 5 Shading, 6 Palette, 7 View, 8 Fit, 9 Read)

### cp_bough_limb and cp_bough_limbx (play, ink)
1 PASS (owner question above). 2 PASS (ink 1 px, play). 3 PASS.
4 FAIL: ruler-straight tube, 8 rows from x 3 to x 215 with no taper, knot or kink (limb 249x37: rows 13-36; limbx
  336x37). Left end is a flat vertical saw cut, 8 px, at x 0 (limb rows 13-20, limbx rows 16-23). Twig fans at the tip
  are 2-3 px broken sticks (limb x 225-249, rows 0-30).
5 PASS (6 and 7 colours, bark ramp, no mottling). 6 PASS. 7 PASS.
8 FAIL: in the sample screens the saw-cut end shows in four places where a limb should meet wood:
  - Frame y110 x1800 (screen 85-118,112-128, world 1885-1918, 222-238): lower limb ends in a square stub lying on the
    big trunk's face (trunk x 80-110); it looks laid in front, not grown from it.
  - Frame y144 x1400 crop (132-150,55-70, world 1532-1550,199-214): the long limb begins with a flat end inside
    the trunk's width, drawn over the fork limb below it, a stitched double limb.
  - Frame y000 x1680 (65-127,140-165, world 1745-1807,140-165): a short limb with a flat left end floating in the leaf mass,
    no trunk anywhere near.
  - Frame y000 x0560 (35-147,213-227, world 595-707,213-227): thick limb floating, left end flat, no trunk under it
    (only a lamp post), orange tuft on the tip.
  Also (frame y144 x1400 crop, 0-30,90-100): thin limb cut off flat at x 22, nothing behind it.
9 FAIL (minor): the fork ledge on a 9-10 px pole (frame y144 x1120, screen 63-155,42-65, trunk x 93-103) reads as a hat
  stand or a T-shaped table, not a tree. At 1x a child sees "a stick on a stick".
VERDICT: FAIL (3 items: 4, 8, 9)

### cp_bough_low (play, ink, 106x70)
1 PASS (0.7 x 0.35 m level part). 2 PASS. 3 PASS.
4 FAIL: the level part is a fat log with a flat round saw face on the left, x 0-3 rows 34-45; the right 40 px dissolve
  into ragged, un-inked pieces (x 62-105, rows 18-60), orange patch at (52-60,40-48).
5 PASS. 6 PASS. 7 FAIL: a log end shown face-on (the sawn end) cuts "no sides or insides".
8 FAIL: frame y070 x2100 (117-167,95-112, world 2217-2267,165-182): the log sits on air at the end of the walkway
  with only two thin posts (x 153, 192) behind it, no trunk beneath; the leaf mass to its right sits on a 10 px trunk
  at x 200-210 that does not touch the log. Pepper stands on a floating log.
9 FAIL: reads as a log or a cannon pointing out of a bush, not a bough.
VERDICT: FAIL (4 items: 4, 7, 8, 9)

### cp_bough_low_leaves (decoration, unfaded, 106x70)
1 PASS. 2 FAIL: unfaded saturated red and orange (255,121,38 to 255,165,44, luma up to 190) on screen, in front of the
  tree line (median 135); it is the brightest mass on its screen (frame y070 x2100, (160-220,45-110)).
3 PASS. 4 FAIL: flat-bottomed silhouette with a hole at file (17-20,30-40) and torn lower edge, no leaf shapes.
5 PASS. 6 PASS. 7 PASS.
8 FAIL: looks pasted on: darker and redder than every tree around it, hard 1x edge, no fade.
9 PASS.
VERDICT: FAIL (3 items: 2, 4, 8)

### cp_bough_clumps (decoration, back fade, 272x35, 9 clumps)
1 PASS. 2 FAIL: on screen (255,165,44) luma 190 (frame y000 x2520, (153-172,168-182)), equal to the far city (190) and
  above the canopy p90 155; back layer must stay darker than what lies behind it.
3 PASS. 4 FAIL: each clump is a flat-bottomed lump with a dark shadow band under it (4 rows), like a cushion; nine
  nearly identical shapes.
5 PASS. 6 PASS. 7 PASS.
8 FAIL: pasted on: stuck on every twig tip as a flame (every ledge of the level, e.g. frame y000 x2520 (150-175,165-185)
  and (305-320,105-120)), brighter than the tree it supposedly belongs to.
9 FAIL (minor): the "burning twig" at every tip is the first thing a child sees.
VERDICT: FAIL (4 items: 2, 4, 8, 9)

### cp_bough_nest (decoration, unfaded, 42x19)
1 PASS (0.9 m). 2 PASS. 3 PASS. 4 PASS. 5 FAIL: lone pixels 3.5 % (aim under 3 %), loose twig dots at (2-4,0-4) and
  (36-41,1-5). 6 PASS. 7 PASS. 8 PASS (sits on the limb at frame y000 x2560 crop (720-850,140-185)).
9 PASS (dark, low contrast bowl, reads, no egg).
VERDICT: FAIL (1 item: 5)

### cp_bough_stump (play, ink, 32x30)
All 9 PASS. Cut top with rings, ramp bark, 1 px ink, 0.5 x 0.6 m beside Pepper, reads as a stump
(frame y144 x0560 area). VERDICT: PASS

### cp_bough_trunk (big oak, 57x357, decoration)
1 PASS (33 px = 0.72 m). 2 PASS. 3 PASS (own dark shade on the right, accepted as cp_ash/cp_lime). 4 PASS (straight
  trunk, root flare, 1 px step in the shade edge at file (56,140-240), minor). 5 PASS. 6 PASS. 7 PASS.
8 PASS. 9 PASS.
VERDICT: PASS (the stub limbs of the limb pieces are listed above)

### cp_bough_trunk9, cp_bough_trunk10 (decoration, 21x140, 20x140)
1 PASS (owner question: 0.2 m). 2 PASS. 3 PASS. 4 PASS. 5 PASS. 6 PASS. 7 PASS.
8 PASS. 9 FAIL (minor): bare poles under a bare fork read as a stand (see limb item 9).
VERDICT: FAIL (1 item: 9, owner decision whether the fork should sit on a leafy tree)

## Three things the owner would notice
1. Floating or stuck-on limbs: saw-cut flat ends over trunk faces and limbs in air with no trunk (list in limb item 8, the low bough).
2. Orange flame tufts on every twig tip, brighter than the canopy.
3. The low bough: a face-on sawn log with a red leaf blob next to it.

No piece got `pipeline.py done`: the family asset cp_boughs has 9 PASS only for the stump and big trunk.

# Round 2
Reviewer: same independent reviewer, 6 Nov 2026, head 2e2663b. Own frames: whole high road at camera y 144, 110, 70, 24, 0
(x every 280 plus 1960), montages and 3-5x crops in art/gen/reviews/cp_boughs_frames/r2/ (m_144, m_110, m_070, m_024,
m_000, low.png, forks.png, longlimb.png). asset_qa PASS for limb, limbx, low, nest, stump; check_backdrop OK.

Fixed since round 1: orange tufts and clumps gone, saw-cut ends gone, trunks are 33 px oak trunks.

- low bough: FAIL (4, 7, 8, 9). Camera y70 x1960, screen (253-320, 114-132): a flat rectangular slab 0.7 x 0.35 m with a
  hard vertical left end (x 253), shaded like a plank, lying in front of the walk's posts (x 253 post is hidden behind
  its end), hovering above the deck with air under it. Reads as a sawn log across the rail. A bough, not a log, is needed.
- thin and thick limbs: FAIL (4, 9). Straight strips with a bracket crotch (x1400 y70, (100-250,200-230)). Where they cross
  a trunk the pale faded band (x1400 y70, (110-155,205-215)) reads as a stripe or shelf, not a branch: it is a different
  colour from both trunk and limb. Fork tops on the 33 px trunks (x840 y70, (130-205,200-235) and (240-310,150-175)) are
  flat-topped trunk stumps with two corbels: a table or column capital, not a fork.
- stump: PASS. big oak trunk: PASS. nest: PASS. leaf mass, clumps, small trunks: removed (n/a).
Verdict: not good enough for the owner. Two failed rounds: change the method (grow limbs from the canopy art, or draw
whole forked trees as one piece, not strips stamped over trunks).
