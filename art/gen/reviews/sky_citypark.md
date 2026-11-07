# sky_citypark.png (painted sky, City Park)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-sky at f01b75d, worktree review-sky07. File 960 x 360, 10 colours. Looked at the file at 2x and 5x, all
27 screens of citypark_tall (tiers y 144, 24, 0) at 2x in colour and greyscale, the horizon of y 24 x 0 at 4x, the
top of the world (y 0 x 0) at 6x, the wrap at 2x, and the bands version beside it. asset_qa: WARN (2 blotches).

Verdict: FAIL. The upper sky and the cumulus bank are good and the autumn light is right. The horizon zone is where
the owner's "technical" word still applies: a ruler-straight diagonal, a full-width flat lavender stripe and a row of
identical scallops. And at the top of the world a cloud bank is sliced flat by the screen edge on four screens.

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| Painted, not technical bands | FAIL | Above row 190 it is painted (lavender blue with wavy tongues, a 250 px cumulus bank). Below it: the amber glow's top edge is one straight diagonal 260 px long (file rows 193-210, x 360-620, long even steps; on screen y 24 x 0 at y 97-105); under it a full-width lavender stripe with flat straight edges (rows 222-232, screen y 102-112 at the path tier). Warm, cool, warm, cool in four flat stripes is banding. |
| No visible repeat on one screen | FAIL | The low bank is 9 identical small lobes in a straight row (rows 213-220, x 370-510; also x 0-90 and 890-960). Seen between the towers right of the Stadshuset on y 144 x 0 and x 320 (screen x 165-250, y 96-100) and on y 24 x 0. |
| No seam at the wrap | PASS | 0.6 % of rows differ at the wrap, the same as any column pair; a window across it shows nothing. |
| No banding stripes | FAIL | See the first row. The cumulus bank's base is also a dead-straight 2 px lavender line across 250 px (rows 178-180, x 40-300), a shelf under the lobes. |
| No lone specks | FAIL | Inside the big bank: 1 px slanted scraps at x 134-140, rows 156-166, and x 76-82, rows 170-172; more under the right bank at x 560-600, rows 165-175. At 5x the lobes look scratched. asset_qa 15 lone pixels. |
| Lightest, calmest layer; play reads in greyscale | PASS | Greyscale 2x, 27 screens: Pepper, the bones, the bin, the goose and the route read; the sky is the lightest thing. |
| Clouds never compete with play | PASS | The banks sit at screen y 40-60 (path tier) and y 0-50 (high tiers), above the far city, never behind the platforms Pepper uses. |
| Cloud undersides at 185 or more | PASS | bdb4de = 187. |
| Tall level: the 120 rows above | FAIL | At camera y 0 the screen top is file row 77 (120 minus the far layer's 43 px rise). The bank at rows 65-90, x 200-395, straddles it, so its bottom half shows sliced flat along the screen top on y 0 x 0 (screen x 200-320), x 320 (x 185-320), x 2240 (x 90-280) and x 2560 (x 180-250). The player can never scroll up to the rest, so it reads as a cropped sky. No seam with any old above-band: the file covers all 360 rows. |
| Motion | PASS | Same code path as River Walk (integer offset, two quads); the top-tier renders at x 0 and x 320 differ by the expected 16 px shift with nothing torn. |
| Consistency (golden autumn afternoon, one family) | PASS | Amber glow, cream lobes, violet undersides: its own hour, same hand as the other two. |
| Would the owner call it technical? | FAIL | The horizon zone, yes, for the three straight-edged stripes. |

Fixes:
1. Move the bank at rows 65-90 so no lobe crosses row 77: wholly below with its top at row 82 or lower (then it sits at screen y 5-30 at the top tier), or delete it. Add to build_sky --check: no cloud pixel within 4 rows of row 120 - round(camYMax x 0.3) for a tall level (CP 77, DT 48).
2. The glow's top edge: build it from two or three overlapping tongues with the same wavy stepped joins the blue uses above, runs of 6-20 px, never one 260 px slope.
3. The lavender stripe at rows 222-232: cut it into three or four streaks of 60-180 px with 1 px tapered ends, as concept b's low streaks are, instead of a full-width band.
4. The low bank: vary radius 3-7 px and gaps 2-9 px, drop every third lobe, or keep a flat bank without scallops.
5. The bank base at rows 178-180: let it wander 1 row under the lobes, or break it under every second lobe.
6. Scraps: no cloud stroke narrower than 2 px, no cloud piece under 6 px.
