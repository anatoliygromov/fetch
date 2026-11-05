# Review for the pipeline: rw_road_rider2

Reviewer: independent gate 8 reviewer (Claude, session 01XkeHCnH2RKgEVTGUWoSKBw; did not make the asset). Written by the reviewer in round 3 (5 Nov) after the builder's hand edits (f450098). Round 2 verdict was FAIL on light direction (both), orange fringe and face (rider 2); the details are in art/gen/reviews/road_rider2.md. The game file: road_rider2.

# Round 3

1. Scale: right size next to Pepper and in its slot (within 2 px): PASS. 104x103 = 1.87 m at 55 px/m (hooks 102, 1 px over, harmless); bike wheel 37 px against car wheels 33 px; helmet level with the hatchback roof, lane 12 px nearer; only rows 0-49 show.
2. Layer: values on its ladder row: PASS. Ink #000000 darkest; script lane layer WARN only for 1 small blotch (no FAIL).
3. Outline: unbroken 1 px ink: PASS. Outer silhouette #000000; hand edits (changed px x30-66, y2-59) left it intact; only far-side tubes and spokes in #373737 are exposed (unchanged from round 2).
4. Shapes: round things round, straight lines straight, no lumps or jaggies: PASS. Wheels untouched by the edits (changed pixels all above y60): rings r17.1 +/-0.5, 8 even spokes.
5. Shading: ramps of 3-4 shades, light upper left, no mottling, no lone specks: FAIL. Fixed since round 2: the orange skin fringe is gone (only neck (54,20) and hand (67-71,43-47) skin remain), jacket now left-lit (shape-normalised left/right third 73/68, was 77/89), backpack top-lit. NOT fixed: the helmet is still lit from the right: left/right third luma 129/142 (round 2: 121/155), and by eye the bright end of the grey band sits at the right (x62-68,y2-6) with the dark bottom-left; it is the one piece of this sprite that conflicts with the level's upper-left light when the rider goes right (unflipped). Fix: move the helmet highlight to the left end of the band (x40-52,y2-6). Also the jacket and backpack carry scattered light-green and tan dabs (jacket sleeve diagonal dashes x60-70,y30-42; backpack speckle x26-44,y22-38), 73 lone px (20.3 per 1000), acceptable but busier than the promenade rider.
6. Palette: only level-palette colours, whites white, darks neutral, within colour cap: PASS. 15 colours (cap 20), all in riverwalk.gpl; ink pure black.
7. View: side profile as road traffic, no tops/insides: PASS. Side profile, backpack, no tops or insides.
8. Fit: beside bench, bin, lamp at 1x and 3x as crisp and dense: PASS. 20.3 lone px per 1000 (bench 16, bin 10), same ink as the bench, same pixel size; torso has 40-47 % of its colour patches at 3 px or less (promenade riders 36 %), a little textured but not dirty at 1x and 3x.
9. Read: cute and clear for a 7 year old at 1x: PASS. Face redrawn clean (dark eye, nose bump, beard, hidden mouth, no brown patch or blue speckle), bearded cyclist with helmet and backpack reads at 1x in the road frame (board/rwtraffic_road_car4_lanerider2_3x.png).

VERDICT: FAIL (1 item)
