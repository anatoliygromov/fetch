Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), round 1, 6 Nov 2026

# Review gate 8: River Walk props family (gritbox_front, cloud2, cloud3, cloud5, kennel, pontoon, rw_jetty, pot), 6 Nov 2026

rw_birch has its own file (rw_birch.md): FAIL on Layer. Own frames at /home/claude/rv/: x3_sweep_riverwalk_y000_x0000 (kennel, pot, oak), x0750 (gritbox, second pot), x1300 (pontoon), x2300 (jetty), x3400, plus small5x.png (all beside bench, bin, lamp at 5x), pep_<piece>.png (4x beside Pepper's real 52x38 sprite), grit6.png, jkp8.png, cl_chk.png, clouds5x.png. Greyscale: g2_*.png. asset_qa: gritbox, cloud5, kennel, pontoon, rw_jetty PASS; cloud2 WARN 2 blotches; cloud3 WARN 10 dirt px, 1 blotch; pot WARN 3 dirt px (0.9 %). check_backdrop OK.

Scale, metres at 46 px/m (Pepper 52 px = 1.13 m nose to tail, 38 px = 0.83 m standing):
- gritbox_front 88x32 = 1.9 x 0.7 m (a grit bin is about 1.2 x 0.8 m): reads big, fine.
- kennel 34x36 = 0.74 x 0.78 m, door 28x17. Narrower than Pepper is long (34 vs 52) and 2 px lower than she stands.
- pontoon 54x12 = 1.17 x 0.26 m, standing box 48 px wide; Pepper is 52 px long.
- rw_jetty 48x41 = 1.04 m deck width, 0.9 m high; Pepper stands on it with her nose about 19 px past the deck's right edge (frame x2300).
- pot 17x27 = 0.37 x 0.59 m, back layer: right for a flower pot.
- clouds: free scale.

Per piece (items 1-9; Scale, Layer, Outline, Shapes, Shading, Palette, View, Fit, Read):

gritbox_front: 1 PASS, 2 PASS (play), 3 PASS (1 px dark ink, unbroken), 4 PASS, 5 PASS (lone dark px at file (8,15), 1 px, nit), 6 PASS (11 greens, dark neutral), 7 PASS, 8 PASS (as crisp as the bench slats at 1x and 3x), 9 PASS (the text is gone; now a plain green box, reads as a bin or crate, not as sand). VERDICT: PASS.

cloud2 and cloud5: 1 PASS, 2 PASS (clouds: darkest 191, contrast 62, 5 colours), 3 PASS (none), 4 PASS, 5 PASS (the dither is gone; one 2x2 checker left in each, cloud2 (63,13) and cloud5 (41,14), too small to see at 5x), 6 PASS, 7 PASS, 8 PASS, 9 PASS. VERDICT: PASS for both.

cloud3: all 9 PASS. 10 one-pixel notches in the rim (asset_qa 0.3 %) read as cloud edge at 5x. VERDICT: PASS.

kennel: 1 PASS with OWNER QUESTION (0.74 x 0.78 m, 34 px wide against Pepper's 52 px length; she crawls into a box smaller than herself, will look "super small" in frame x0000 where it sits beside the 100 px door), 2 PASS, 3 PASS (1 px dark ink), 4 PASS, 5 PASS (flat red planks, no mottling), 6 PASS (corner posts #ded9bd cream, dark neutral), 7 PASS, 8 PASS, 9 PASS (red box, white posts, bone plaque, black doorway; flat grey roof, so it reads as a kiosk or box before a doghouse; the bone plaque saves it). VERDICT: PASS (owner question: scale; maybe a pitched roof).

pontoon: 1 PASS with OWNER QUESTION (1.17 x 0.26 m, its 48 px standing box is shorter than Pepper's body; it reads as a grey stone slab on two floats next to the 56 px rowing boat and the 100 px quay), 2 PASS, 3 PASS, 4 PASS, 5 PASS (one dark rivet px at the deck centre, (27,3), reads as a bolt), 6 PASS, 7 PASS, 8 PASS, 9 PASS (slab on water, reads as a pontoon only because of the rope). VERDICT: PASS (owner question: scale).

rw_jetty: 1 PASS with OWNER QUESTION (deck 1.04 m, Pepper's nose and chest overhang 19 px; at 3x it looks like a small table), 2 PASS, 3 PASS, 4 PASS, 5 PASS (moss at the foot, 15 colours), 6 PASS, 7 PASS, 8 PASS, 9 PASS (three posts 5 px wide with two X braces and sky between, reads as a trestle on piles, not as cage bars; the black ink on the posts is heavy against blue water). VERDICT: PASS (owner question: scale).

pot: 1 PASS, 2 PASS (back, raw darkest 67), 3 PASS (no ink, grey rim shade), 4 PASS, 5 PASS (3 dirt px inside the leaves, no mottling at 8x), 6 PASS, 7 PASS, 8 PASS (soft but clean beside the lamp), 9 PASS. VERDICT: PASS.

Pipeline: only rw_birch is in tools/pipeline.py, so `done review` was not run for the others (no row) and not for rw_birch (FAIL).
