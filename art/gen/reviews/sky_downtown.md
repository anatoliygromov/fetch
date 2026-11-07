# sky_downtown.png (painted sky, Downtown)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-sky at f01b75d, worktree review-sky07. File 960 x 360, 10 colours. Looked at the file at 2x and 5x, all
34 screens of downtown_tall (tiers y 240, 120, 0) at 2x in colour and greyscale, the top of the world (y 0 x 2880) at
4x, the wrap at 2x, the bands version beside it. asset_qa: WARN (4 blotches).

Verdict: FAIL for one placement defect; otherwise the cleanest of the three skies and finished.

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Painted, not technical bands | PASS | Deep blue to pale blue in four tones with long wavy tongues (the lighter streak band at rows 150-215 has a slow curved edge), white cumulus with short pale undersides, a near-white horizon. Reads as a bright midday. |
| No visible repeat on one screen | PASS | The low bank (rows 207-218, x 297-455 and 781-960) has lobes of two sizes and is never on screen: at every tier it sits behind the far roofs (screen y 87-98 at the street, lower at the high tiers). The two cumulus banks differ. |
| No seam at the wrap | PASS | 0.3 % of rows differ at the wrap against 0.5 % for a typical column pair; nothing visible. |
| No banding stripes | PASS | The straightest joins (rows 220-225, 45 % of columns) are behind the roofs. |
| No lone specks | PASS | 5 lone pixels in the file, all inside the lobes' shading and under 2 px; nothing reads at 5x. |
| Lightest, calmest layer; play reads in greyscale | PASS | Greyscale 2x, 34 screens: Pepper, the bones, the crates and the route read; the sky is only seen above the roofs and is the lightest thing there. |
| Clouds never compete with play | PASS | No sky behind the street tier at all; at y 120 and y 0 the banks sit above the gables, never behind a platform. |
| Cloud undersides at 185 or more | PASS | c4d6ee = 211, d8e4f2 = 226. |
| Tall level: the 120 rows above | FAIL | At camera y 0 the screen top is file row 48 (120 minus the far layer's 72 px rise). The bank at rows 35-62, x 250-400, straddles it: its bottom 14 rows show sliced flat along the screen top on y 0 x 0 (screen x 255-320), x 320 (x 235-320), x 640 (x 215-320), x 960 (x 185-220, the rest behind the gable), x 2560 (x 265-320), x 2880 (x 100-260) and x 3200 (x 85-245). It is the first thing seen when Pepper reaches the roofs. No seam with any old above-band: the file covers all 360 rows. |
| Motion | PASS | Same code path as River Walk, integer offsets, two quads; nothing tears. |
| Consistency (bright midday, one family) | PASS | White tops, pale undersides, clean blues; same lobe and streak hand as the other two. |
| Would the owner call it technical, dirty, flat? | PASS | No. |

Fix:
1. Move the bank at rows 35-62 wholly below row 48 with its top at row 53 or lower (it then sits at screen y 5-32 at the roof tier, under the sliced position), or delete it; the second bank at rows 88-112 already sits well. Add the same rule to build_sky --check as for City Park (no cloud pixel within 4 rows of row 120 - round(camYMax x 0.3)).
