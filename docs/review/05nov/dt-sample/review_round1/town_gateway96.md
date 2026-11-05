Reviewer: independent agent (gate 8), 5 Nov 2026, art/dt-sample-05nov. Judged from the PNG at 5x, numpy, asset_qa and the frames in /tmp/review_dt/frames (tools/dt_sample_frames.sh, 11 screens x camera y 120 and 240). Script PASS not taken as a pass.

Asset: town_gateway96 (140x138), courtyard gateway at 3 m, decoration on the back line, placed at x3050-3190 (centred on the GATE box 3072-3168).

1. Scale: PASS - 138 px = 3.0 m; jambs 16 px, arch 82 to 108 px wide inside.
2. Layer: FAIL - the stone wall is the lightest back piece: median 192, p90 225 on screen (S10 y240 frame, x185-200), against the old town row 168 and far roofs 169 behind it, and plaster 179 on neighbouring houses. Back must be darker than the far layers. (asset_qa FAILs it without a fade: darkest 63, contrast 150; it PASSes at --fade 0.28, so the script depends on the fade argument; the on-screen number is what counts.)
3. Outline: PASS - none; edges are darker shades of the stone.
4. Shapes: PASS - jamb courses at identical rows left and right (0 px differ), keystone centred, arch symmetric apart from the light side. Arch outer curve has 2 to 4 px steps, even left and right.
5. Shading: PASS - light from the upper left; the dark interior has one shade band.
6. Palette: FAIL - colours (58,50,56), 7,917 px (the whole interior), and (42,36,42), 357 px, are not in art/palettes/downtown.gpl, though the palette's own keep list names town_gateway70.
7. View: PASS - front-on, a thin cornice.
8. Fit: FAIL - the piece includes its own rectangular stone wall with a flat cornice top, so it lands as a pasted block, not a hole in a house wall. At 70 it straddles the seam between two houses (x1912) with the plaza house x1832-1900 and its balcony in front of the left half; at 96 there is no house at all (screen 10, see dt_sample_screen.md). Lone pixels 0.17 to 0.19 %.
9. Read: PASS as an archway; the cream block with two windows and hedge inside the arch reads as a house seen far back. Not usable, correctly: nothing on it is a ledge.

Fix list: lower the stone value under the far row (about 150 on screen); add the two interior colours to the palette or snap them; put the arch in a house (plaster wall, no stone slab) or give it a house behind it on screen 10.

VERDICT: FAIL (3 items)
