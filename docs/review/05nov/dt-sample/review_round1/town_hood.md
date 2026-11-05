Reviewer: independent agent (gate 8), 5 Nov 2026, art/dt-sample-05nov. Judged from the PNG at 5x, numpy, asset_qa and the frames in /tmp/review_dt/frames (tools/dt_sample_frames.sh, 11 screens x camera y 120 and 240). Script PASS not taken as a pass.

Asset: town_hood (58x19), the dormer's copper window hood, a play perch (box DORMER x1920-1976, y264).

1. Scale: PASS - 58x19 matches the slot and the box (+1 px outline row above); 1.26 m wide.
2. Layer: FAIL - on screen (S7 y120 frame, x2..56, y144..158) median 189, p10 104, against plaster 179 and the gateway stone behind it. A play perch must be the darkest, most contrasted layer; only the outline separates it. Existing play pieces are 111.
3. Outline: PASS - unbroken 1 px ink, one colour (asset_qa PASS, 0 lone pixels).
4. Shapes: PASS - five equal panel lines, two equal corbels (mirror differences are shading only), straight edges.
5. Shading: PASS - light upper left, 3-shade copper.
6. Palette: PASS - 7 colours, all in downtown.gpl.
7. View: PASS - front-on, thin cap.
8. Fit: PASS in crispness; FAIL in context, see dt_sample_screen.md: it hangs at x1920-1978, y263-282 above the gateway's right shoulder and the shop front, with no window under it (the nearest window sill is 36 px higher), so it reads as a bracket shelf, not a window hood.
9. Read: PASS - reads as a ledge to stand on.

Fix list: lift the fill darker than the plaster (about 130 on screen); put the box under a real window or draw the window it covers.

VERDICT: FAIL (1 item)
