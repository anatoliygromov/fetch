Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), round 1, 6 Nov 2026

# Review gate 8: Downtown roof kit, far spire, balconies, details, fountain (art/dt-roofs-06nov, head 0ed0010)

Method: asset_qa on all 15 (14 PASS, spring WARN as the maker said), check_backdrop OK. Own frames with tools/dt_sample_frames.sh
(look on) at camera y 0, 120, 240 and x 560, 780, 900, 1150, 1250, 1500, 1640, 1760, 1900, 2120, 2380, 2400, 3100, colour and
grey, 1x and 3x (/tmp/rv06/own, /tmp/rv06/own2, /tmp/rv06/up3). Files at 4x to 8x beside bench, bin, lamp and Pepper's real
cell (0,0,60,52) in /tmp/rv06/s. Palette, edge ink, bar pitch and baluster gaps checked by numpy. Metres at 46 px/m (play, back).
Colour use: all 15 files are 100 % in art/palettes/downtown.gpl; the ink is (18,18,26) on every play edge (edge dark 1.00; spring 0.75).
On screen (luma): loggia p10 35 / med 71; gallery88 p10 15 / med 104; balcony56 p10 15 / med 97; footbridge p10 15 / med 101;
house walls behind med 148 to 152. Every play piece is darker than the wall it hangs on.

## town_roof_loggia (122x26, play): 2.65 m x 0.57 m
1. Scale: PASS (owner question: the five arch openings are 14 x 11 px, 0.30 x 0.24 m, about Pepper's head width; it reads as a blind arcade slab, not a loggia a dog could walk into. The 120 px box fixes the width.)
2. Layer: PASS. 3. Outline: PASS (unbroken ink). 4. Shapes: PASS (five arches on a 24 px pitch, identical). 5. Shading: PASS (6 colours, no specks).
6. Palette: PASS. 7. View: PASS. 8. Fit: PASS. 9. Read: PASS (stone arcade parapet; the dark arch fill 42,36,42 reads as niches).
VERDICT: PASS

## town_roof_gallery88 (90x32, play): 1.96 m x 0.70 m
1. Scale: PASS (vase balusters 8 x 20 px = 0.17 x 0.43 m, balustrade 0.70 m, low but fine for a ledge she stands on).
2. Layer: PASS. 3. Outline: PASS. 4. Shapes: PASS, WARN: the end gaps are not the inner vase shape, 4 px wide at row 5 (x7-10 and x79-82) against 2 px inside, so the first and last balusters are part-vases. 5. Shading: PASS. 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS (crisp as the lamp at 3x). 9. Read: PASS (stone balustrade).
VERDICT: PASS

## town_roof_gallery72 (74x32, play)
1. Scale: PASS. 2. Layer: PASS. 3. Outline: PASS.
4. Shapes: FAIL. The 10 px baluster pitch does not divide the 74 px width: the end gaps are slivers, 1 px wide at rows 5-7 and 10-14 and 3 px at the swell (x7-9 left, x64-66 right), against 6 px swell and 2 px neck inside. At 5x the first and last balusters are cut into thin splinters, so the gallery's parts are not identical and the ends look like damage. Fix: shorten or widen so the 5 or 6 vases are whole (width 72 holds 6 whole vases of 10 px pitch only with an 8 px margin each side).
5. Shading: PASS. 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS. 9. Read: PASS.
VERDICT: FAIL (1 item)

## town_roof_flower_roof (90x14, play)
1. Scale: PASS (owner question: the five terracotta boxes are 14 x 8 px, 0.30 x 0.17 m; a real window box is 0.6 to 1 m wide; they read as tiny pots next to Pepper, 44 px long.)
2. Layer: PASS. 3. Outline: PASS. 4. Shapes: PASS (five identical boxes, even gaps). 5. Shading: PASS (11 colours, blooms are 2 px red dabs with one green shade, no lone specks). 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS. 9. Read: PASS (cute).
VERDICT: PASS

## town_roof_ledge (16x9, 3-slice, play)
1. Scale: PASS (slab 0.2 m, modillion 8 px). 2. Layer: PASS. 3. Outline: PASS. 4. Shapes: PASS. 5. Shading: PASS. 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS (dentil teeth read cleanly at 1x). 9. Read: PASS (cornice shelf; it floats on the wall with no bracket, a level choice).
VERDICT: PASS

## town_footbridge (162x52, play)
1. Scale: PASS (owner question: the railing is H.BRIDGE_RAIL = 12 px = 0.26 m, knee to chest of Pepper, while the balconies have a 46 px (1 m) rail; real handrail 1.1 m. Frame /tmp/rv06/up3/sweep_downtown_y120_x2400.png.)
2. Layer: PASS. 3. Outline: PASS. 4. Shapes: PASS (pickets on a 4 px pitch, posts on the deck joints, smooth arch). 5. Shading: PASS. 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS. 9. Read: PASS (iron footbridge, clear).
VERDICT: PASS

## spire_riddarholmen (36x260, shore at 0.70)
1. Scale: PASS (owner question: 260 px at the shore's 12 to 14 px/m is about 20 m; the real spire is about 90 m. In frame it stands about 2x the far-shore houses, which reads right.)
2. Layer: PASS (file luma 53 to 143; on screen the spire is 171 to 188, the far houses about 190 to 220; it is lighter than the sky behind it, 107 to 153, by up to 80, a ghost in front of blue; same as the far city, so accepted). 3. Outline: PASS (none, edge stays its own shade). 4. Shapes: PASS (lattice diamonds even, straight tower). 5. Shading: PASS (8 colours). 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS. 9. Read: PASS (church spire with a cross).
VERDICT: PASS

## town_balcony56 and town_balcony64 (58x57, 66x57, play)
1. Scale: PASS (rail 46 px = 1.0 m, 56 / 64 px = 1.2 / 1.4 m wide, as wide as the house window; a French balcony.)
2. Layer: PASS. 3. Outline: PASS. 4. Shapes: PASS (3 px bars on an 8 px pitch, gaps 5 px, ring frieze rows 3-6, identical in both). 5. Shading: PASS. 6. Palette: PASS. 7. View: PASS.
8. Fit: PASS.
9. Read: FAIL. It reads as a birdcage or a jail window, the same fault as the walkway legs tonight. A 46 px wall of 3 px dark bars, 5 px gaps (a bar every 8 px for 46 rows, 7 bars), with no top rail and no open band; the house behind shows through the bars and the golden bones sit "inside" it (frames x1500, x1640, x2380 at y120, bones at 3x (240,640), (125,620)). At 3x it looks like a cage hung on a wall. Fix idea: a solid or half-solid lower panel with the bars only in the upper 20 px and a thick top rail, or fewer, wider-spaced bars (3 px on a 12 px pitch) with a handrail.
VERDICT: FAIL (1 item, both files)

## town_spring (36x10, 4 frames of 9 x 10)
1. Scale: PASS (0.2 m wide, tucked under an awning's post). 2. Layer: PASS.
3. Outline: FAIL. Frames 0 to 2 are cut open at the bottom: frame 0 row 6 is red (x1-7) with no ink under it, frame 1 row 7, frame 2 row 8; only frame 3 has its closing ink row (row 9). Edge ink 0.75. It hangs free under the awning with no post under it, so the open red end shows.
4. Shapes: PASS (flat bands, not round, acceptable at 9 px). 5. Shading: PASS. 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS (crisp). 
9. Read: FAIL. At 1x under the awnings (frames /tmp/rv06/up3/sweep_downtown_y240_x0780.png, y240_x2380.png) it is a red clump at each awning corner, like a tassel or a red cuff on the post; nothing says "spring". A coil needs a visible zigzag or round loops.
VERDICT: FAIL (3 items)

## town_stopsign (19x101, back, faded)
1. Scale: PASS (owner question: 2.2 m tall, disc 19 px = 0.41 m; the disc is about Pepper's head, small but true to a tram sign.)
2. Layer: PASS. 3. Outline: PASS (none, own darker rim). 4. Shapes: PASS (round disc, straight pole). 5. Shading: PASS. 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS, WARN: it stands under the shelter's roof and behind its glass, so the glass streak crosses the disc (3x frame y240_x1900, about (650-690, 255-300)) and the pole sits on a shelter post line. 9. Read: PASS (green ring, white disc, tram).
VERDICT: PASS

## town_jet (24x88, 4 frames of 6 x 88, back, unfaded)
1. Scale: PASS (owner question: streams are 2 px wide, 0.04 m, 88 px = 1.9 m long, thinner than a garden hose; they fall 7 px outside the tier past the bowl.)
2. Layer: PASS, WARN: the white dashes are 253 on screen against walls of 120 to 150, contrast about 130 on a back row with max 120.
3. Outline: PASS. 4. Shapes: PASS. 5. Shading: PASS (3 colours, no specks; no lone drops). 6. Palette: PASS. 7. View: PASS. 8. Fit: PASS. 9. Read: PASS, WARN: dead straight, regular 1 px dashes read as beaded string until you see it animate; a kid will read water, a pixel artist a dotted line. Crop /tmp/rv06/s/jetcrop.png.
VERDICT: PASS

## town_tier (50x58), town_bowl (34x82), town_rim (18x18), play
1. Scale: PASS (tier 1.1 m wide, bowl 0.74 m, rim block 0.4 m). 2. Layer: PASS. 3. Outline: PASS (unbroken ink on all three). 4. Shapes: PASS (symmetric, coursed stone lines even, no jaggies). 5. Shading: PASS (4 colours, speckle gone). 6. Palette: PASS. 7. View: PASS (front and thin cap). 8. Fit: PASS (as crisp as the lamp and bin at 1x and 3x). 9. Read: PASS (stone fountain).
VERDICT: PASS (all three)

# Summary
PASS (9/9): loggia, gallery88, flower_roof, ledge, footbridge, spire, stopsign, jet, tier, bowl, rim.
FAIL: gallery72 (Shapes), balcony56 and balcony64 (Read), spring (Outline, Read).
`pipeline.py done NAME review` was not run: none of these 15 has a pipeline status (not started, no art/gen/jobs spec), so it refuses.

# Round 2 (re-check of the 5 fixed pieces, head 8f6b63d)
Frames (own, look on, 1x and 3x, colour and grey): /tmp/claude-0/-home-claude/87159006-489b-566e-ae4a-e83d2f5ae5ab/scratchpad/r2/ (camera y 120 and 0 at x 1440, 1700, 1860, 2300; y 240 at x 640; s/ has x 780 and 2380 at y 240 and 120). Files at 5x beside bench, lamp_post, bin: r2/f_gal.png, f_bal.png, f_spr.png, f_spr16.png. asset_qa and check_backdrop: PASS / BACKDROP OK.

## town_roof_gallery72 (74x32) and town_roof_gallery88 (90x32)
4. Shapes: PASS. Pitch is 16 px and the end gaps now equal the inner gaps (row 6: 6 px at both ends and between every pair; row 13: 7 px swell gap; rows 10 and 20: 8 px at both ends), both files. Every vase whole, 4 and 5 identical. Other 8 items unchanged: PASS.
VERDICT: PASS (both, 9/9)

## town_balcony56 and town_balcony64 (58x60, 66x60)
Better: it is now an open iron railing (3 px handrail, bottom rail, 4 posts, a ring per panel) and the house reads through it, a French balcony; not a jail window. Items 1 to 8: PASS.
9. Read: FAIL. The bones still look caged. They sit in the railing plane, behind the bars: at camera y 120 x 2380 the two bones at 1x (about x56-68 and x84-98, y 197) have a post at x91 crossing the right bone's right end and a post at x50 touching the left bone's left end; in x1440 frame the left balcony's bone at 3x (395-440, 640) is cut by the centre post. Rail is also boxed in ink on all four sides, 46 px tall. A kid sees a bone locked behind bars.
Fix ideas: draw the bones in front of the railing (or at the rail level above the handrail), or move the bones to the gaps between posts (posts at 8, 31, 54 of 58, gaps 20 px, bone 14 px), or lower the rail panel so the bones stand over it.
VERDICT: FAIL (1 item, both files)

## town_spring (36x10, 4 frames)
3. Outline: PASS (every frame closes with its ink row, 16x crop r2/f_spr16.png). 9. Read: PASS. It is now a grey steel coil of flat bands at each awning post (frames s/x3__y240_x0780.png, x2380), no red tassel; reads as a spring clamp more than a round coil at 1x, but it is crisp, steel, and the squash frames differ. WARN: bands are flat slabs, at 9 px a zigzag is not possible; fine. Others PASS.
VERDICT: PASS (9/9)

# Round 2 summary
PASS: gallery72, gallery88, town_spring. FAIL: balcony56, balcony64 (Read: bones behind bars).
