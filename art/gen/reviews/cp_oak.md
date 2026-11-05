Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), rounds 1-3, 5 Nov 2026

# Review gate 8: cp_oak.png (old oak, 388x343) - 5 Nov 2026, independent reviewer

Judged from the file (5x/6x crops), fresh game frames (tools/layer_frames_tall.py citypark_tall --ids, 27 frames) and scene.lua. Rec.601 luma. File pixel positions are x,y in cp_oak.png; screen positions are in the 320x240 frame.

1. Scale: FAIL. Trunk 54-55 px wide at 50-60 px up (61 at 40, 68 at 30, 98 at 20, 138 at 10). The plan's old oak spec is 46 px (citypark_tall.md line 128); the big oak's 60 belongs to screen 9. 55 is +9 over 46 (+20 %) and -5 under 60: outside the 2 px tolerance either way. Top is above the world (y -24 to -33), good. Pepper (26 px) against a 55 px trunk reads as a 2 m trunk, not 1 m.
2. Layer: FAIL. Medians order correctly (back 135 against mid 154, tree line 175-181, city 190, sky 202). But the back-layer highlight colour #f6ad35 (8.4 % of the art) is (255,187,63), luma 193 on screen, as light as the far city (190-195) and lighter than the tree line median (175) and the mid p90 (180). 3106 px at y24, screen 6. Back p99 is 209, back max 215. A nearer layer must be darker. Darkest side is fine (back p10 83-100; min 67).
3. Outline: FAIL. Trunk and every limb carry a 1-2 px near-black edge: #150e15 (luma 16, 7.1 % of the art) and #332324 (6.2 %); asset_qa decor-ink WARN 71 %. After the 0.28 fade it is (70,62,90), luma 67, a cool violet 1 px ring around warm brown bark (screen 6, x 19-96 and 150-230, y 30-171 at y144). Decoration must have no ink edge, only a darker shade of its own colour. It is also the darkest thing in the back layer, close to the ledges' own ink.
4. Shapes: FAIL (minor). (a) Nine detached limb fragments sit inside the crown, each ink-outlined, connected to nothing: file boxes (259,70)-(293,86), (93,70)-(134,96), (313,148)-(340,167), (67,104)-(105,116), (220,54)-(239,78), (288,201)-(316,215), (38,108)-(67,120), (286,98)-(305,114), (147,34)-(163,52). They read as stray sticks next to the real ledges. (b) The crown is cut flat by the image edge: x=0 rows 96-117, 147-154, 159-183 (55 px), x=387 rows 88-91, 98-101. (c) Leaf edges are stepped with irregular 1-3 px teeth.
5. Shading: FAIL. Leaf masses are 3-tone patchwork with irregular blotches and no leaf structure, e.g. file (120-300, 40-140) and (0-90,140-200). The approved rw_lime (same size class) has leaf-by-leaf shapes and clean ramps. asset_qa blotch check passes, but the eye sees mottling. Lone pixels 0.96 % (rw_lime 1.6 %), fine.
6. Palette: PASS. 10 colours, no alpha. Note the citypark palette was built from this asset (make_palette.py keep list), so it is self-approving; darks #150e15 are slightly violet, not neutral.
7. View: PASS. Front-on, trunk and limbs side view, no tops.
8. Fit: FAIL. Beside the approved lime, bench, bin and lamp it is blotchy and lower in detail (leaf puffs 60-120 px wide against rw_lime's 4-6 px leaves). On screens 5 and 7 it sits beside old-style canopies with a visible change of density (see cp_sample_screen.md item 6).
9. Read: PASS. An autumn oak, friendly, reads at 1x. At camera y 0 and 24 the leaves fill the screen, ledges stay clear.

Task checks: (1) ledges against limbs, PASS (ledge ink luma 20 against limb edge 67; ledge body 91-128 is near trunk 100, so the outline carries it); (7) n/a.

VERDICT (round 1): FAIL (6 items)

## Round 2 (fix 02fd5cb, fresh frames /tmp/review_cp/r2, 27 frames)

Scale is an owner question: measures unchanged, trunk 55 at 50 up, 61 at 40, 98 at 20 (old oak spec 46, big oak 60). Not failed.

1. Scale: PASS (owner question, measures above).
2. Layer: PASS. Highlight #f6ad35 is now #e48c28 (luma 154, 8.4 %). Back layer on screen (screens 5-9, all cameras): p10 106, median 135, p99 188, 2.0 % at 185 or over (round 1: p99 209, 5.4 % at 190+). Below city (190-195) and tree line.
3. Outline: PASS. #150e15 is gone; the darkest colour is now #332324 (luma 39, 10.7 %), a dark bark brown used as shade inside the trunk and limbs, no 1-2 px near-black ring (6x crop of file (130-290,140-260)). Screen-level: back min 67 (from the lime, see cp_lime). asset_qa still WARNs decor-ink 73 % (relative-darkness measure), which I judge a shade of its own colour now.
4. Shapes: PASS. All nine floating limb fragments are deleted (checked each round 1 box: crown leaf only). Flat cuts carved: x=0 now 19 px in three runs (rows 103-110, 149-152, 168-174; was 55 px), x=387 four px (89-90, 99-100). Carved edges look round in the 5x crop; no new notches.
5. Shading: FAIL. Patchwork is reduced a little but still 3-tone blotches without leaf structure, and asset_qa now WARNs blotches: 19 patches of 2-24 px in a near colour (it did not before), e.g. file (120-300,40-140), the maroon islands at (20-60,60-80) and (0-90,140-200). Lone 0.95 %. Merged leaf islands: the dark maroon gap areas between puffs have become larger flat fields, which is cleaner but flatter.
6. Palette: PASS (8 colours).
7. View: PASS.
8. Fit: FAIL. Still blotchy against rw_lime at 1x/3x. The old-canopy overlap is fixed (round 1 item 8 seam): no starburst at screen 5 (x 55-130, y 30-95 at y144) any more.
9. Read: PASS.

VERDICT: FAIL (2 items)

# Round 3 (dc2b405; fresh frames /tmp/review_cp/r3, screens 5-8 at y 0, 24, 144)

Scale is an owner question: trunk 55 at 50 up, 61 at 40, 98 at 20 (old oak spec 46, big oak 60). Not failed.

1. Scale: PASS (not applicable as a fail: owner question, measures above).
2. Layer: PASS. Highlight luma 154 raw; trees on screen stay under 190 (back p99 188; the few back pixels at 190+ are lamp glass and arbour slats, screen 8).
3. Outline: PASS. Darkest #332324 (luma 39) is bark shade; no ink ring. asset_qa decor-ink WARN 73 % is the relative-darkness measure.
4. Shapes: PASS. No loose limb bits; flat cuts stay carved (x=0: 19 px in rows 103-110, 149-152, 168-174; x=387: 4 px).
5. Shading: FAIL (minor). The merges cut asset_qa blotches from 19 to 9, but leaf fields are still irregular 3-tone patchwork with small dark islands, e.g. file (115-130,125-135) (small ring island), (20-60,60-80), and ragged maroon fields between puffs at (100-300,40-170). Lone 0.95 %. Cleaner than round 1, still the least crisp of the three big trees.
6. Palette: PASS (8 colours).
7. View: PASS.
8. Fit: PASS (1x). In the frames it reads as one family with the new lime and ash; at 3x it is noisier than the lime.
9. Read: PASS.

VERDICT: FAIL (1 items)
