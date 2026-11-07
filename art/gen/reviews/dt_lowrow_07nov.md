Reviewer: independent gate-8 visual reviewer (Claude, did not make these assets), round 1, 7 Nov 2026

# Review gate 8: the Downtown low row, 47 `dtl_` files (branch day/07nov-dt, head ab40394)

# Round 1 (reviewer, 7 Nov)

Method: every file at 5x beside the approved bench, bin and lamp (riverwalk/art/scene/), the fronts at 2x in a
row, numpy on the files (empty rows, run widths, colours), `asset_qa.py --file` (roofs and canopies as play,
fronts as back + building: the maker's results reproduce), and the 33 sweep frames at 1x to 8x (the screen list
is in `dt_sweep_07nov.md`). Metres at 46 px/m. Pepper on screen 52 px long, 40 px tall. The 9-item checklist of
`docs/asset_qa.md` plus the eye checks of the brief; a FAIL names the fix.

Shared facts. Everything is crisp: flat fills, straight lines, stamped parts, no area-averaged edges, no
blotches, no lone pixels (asset_qa noise and stray 0 on every file). The ink is one colour on every play edge.
The failures below are design and placement failures, not dirt.

## The roof strips: dtl_wing_roof 66x23, dtl_arcade_roof 122x25, dtl_pav1_roof 90x23, dtl_pav2_roof 74x23, dtl_kioskhouse_roof 58x21, dtl_shelterhouse_roof 58x21, dtl_canalhouse_roof 50x21 (play)

One drawing at seven widths: a brick parapet (two courses, brown-grey), a grey ashlar band, a beige fascia,
1 px ink all round. On screen: median 135, darkest 24, the cap row 237.
1. Scale: PASS. 21 px above the box = 0.46 m, a knee-high parapet.
2. Layer: FAIL as drawn. The BIBLE's obstacle is "crisp, mid-tone, 1 px dark outline". This is a dark bar: the
   brick body sits at 100 to 135 on light walls (150 to 207); on the y 120 sheets the seven strips are the only
   dark things on the screen, so they read as bars laid on a wall, not as the top of a building. Fix: body in
   a mid-tone granite (on-screen median 150 to 165), the coping 2 px at about 200, and a 3 px lead-seam row
   (two greys) under the coping so the top reads as a roof edge; same ramp on all seven and on the shed and
   hall strips.
3. Outline: PASS (unbroken, one ink).
4. Shapes: PASS.
5. Shading: PASS (flat ramps, light from the upper left on the cap).
6. Palette: PASS (8 colours).
7. View: PASS (a front and a thin cap).
8. Fit: PASS for crispness beside the bench (same pixel size, same edge). FAIL for the read: it is a parapet
   without a building that ends in a roof. Fix: under the strip a 6 px tile eave course (two oxblood shades,
   the 4 px scallop stamp) on the pavilions, kiosk house, shelter house and canal house, so each building ends
   in a roof, not in a wall strip. The wing and the arcade keep lead (A1) but get the lighter coping.
9. Read: PASS as "stand here" (a child sees the dark bar). FAIL as "roof". Nothing says roof: no tile, no
   slope, no ridge, no gutter.
VERDICT: FAIL (layer value, the roof read). One fix for all seven files.

## dtl_shed_roof 90x33 (play): the tram shed's parapet with the dormer

The same strip plus a 24x12 px dormer (brown box, grey window, red cap) standing on top of the coping at x 33-56.
1. Scale: FAIL. 24x12 px is 0.52 by 0.26 m: smaller than Pepper's head. A dormer is a window a person stands
   behind: 40x30 px at least.
2. Layer: FAIL (the strip, as above).
3. Outline: PASS.
4. Shapes: PASS.
5. Nothing floats: FAIL. The dormer stands on the coping, in front of nothing: a flat roof behind a parapet
   would hide a dormer's sill. Fix: draw the dormer behind the parapet (its sill hidden by the coping, 40x30
   with a two-course tile cap), or drop it; the box stays 1912-2000 either way.
VERDICT: FAIL.

## dtl_hall_roof 162x19 (play): the flower hall's roof garden

A thin dark ledge with a row of 2 px flower dots and a coping.
1. Scale: FAIL. The concept (A3) is an iron railing with planters along the top of the glass hall: 12 px of
   railing and 16x6 planters. This is an 8 px ledge with dots; at 1x it is a line.
2. Layer, 3. Outline, 4. Shapes, 5. Shading, 6. Palette, 7. View: PASS.
8. Fit: FAIL (the one high point of the route is the thinnest piece on the screen).
9. Read: FAIL (a ledge, not a garden). Fix: railing 12 px with 2 px posts every 16, three planters 16x6 with
   two flower colours, the ink outline on the railing's top rail only.
VERDICT: FAIL.

## dtl_guild_roof 130x91 (play): the guild hall's crow-step gable and chimney

A red running-bond brick fill, grey stone crow steps, a brick chimney 18 px wide with a stone cap.
1. Scale: PASS. 2.8 by 2.0 m; chimney 0.4 by 1.1 m; the steps 8 px are a slope, fine.
2. Layer: PASS (play; outlined).
3. Outline: PASS.
4. Shapes: PASS (steps even, chimney straight).
5. Shading: FAIL. The brick fill runs 55 to 135 in luma at a 4 px pitch across 130x91 px: the busiest surface
   in the level (the frames at x 1600 y 120: it is the first thing the eye lands on). This is the A2 fault the
   brief said not to copy (a busy gable mass). Fix: the roof surface in tile courses (the scallop stamp, two
   oxblood shades, contrast at most 60 across the fill); brick only on the crow steps' edge and the chimney.
6. Palette: PASS (13).
7. View: PASS.
8. Fit: PASS (the chimney with the bone reads at every tier).
9. Read: FAIL. It reads as a brick wall with a stepped top on a stone box, not as a tiled roof. The owner said
   yes to real tiled roofs at the roof tier; this is the one roof that could carry tile and it is brick.
VERDICT: FAIL (the fill).

## dtl_pav1_canopy1 58x14, dtl_pav2_canopy1 58x14, dtl_guild_canopy1 58x17 (play): the middle tier

A brown plank with three dark green sawtooth teeth hanging under it, 1 px ink.
1. Scale: PASS (1.26 by 0.3 m).
2. Layer: PASS. 3. Outline: PASS. 4. Shapes: PASS. 5. Shading: PASS. 6. Palette: PASS (5 to 7). 7. View: PASS.
8. Fit: FAIL. The owner's yes was "canopies kept on the middle tier as part of the shop fronts, no hung
   balconies anywhere". These are hung shelves: a plank with pennants fixed to a blank wall. pav1's is drawn at
   x 1655-1713 while its pavilion is 1680-1768: 25 px of it hangs on the guild hall's stone wall, across the
   seam of two buildings, and its pavilion's shop window (1692-1755) is only a third under it. pav2's at
   1839-1897 overhangs its pavilion (1816-1888) by 9 px into the alley. The guild's at 1552-1610 over the
   guild's door is the only one that sits on a front. None spans its shop window.
9. Read: FAIL. A child sees a shelf with flags, and it is a third walking vocabulary beside the parapets and
   the street's striped awnings.
Fix: a cloth canopy in the street awning's vocabulary (the approved springy awning's ramp), width = its shop
window + 8 px (pav1 window 1692-1755 so 72 wide, pav2 1820-1883 so 72, guild door 1572-1613 so 50), depth
10 px, a 3 px valance with a 1 px ink edge, fixed at the window head and inside its building's x (pav1
1688-1760, pav2 1816-1888, guild 1568-1618). The boxes move with
them; physics rerun.
VERDICT: FAIL (all three).

## dtl_arcade_front 120x122 (back, building): the cafe arcade

Beige wall, three round arches with dark reveals and windows inside, a cornice band.
1. Scale: FAIL. The arch openings are 26 px wide (0.57 m) and about 90 tall beside a 52 px dog: slits, not
   an arcade. The concept's arches are 1.5 m. Fix: two arches of 46 px in the 120 px front (piers 8 px), the
   statue in front of the middle pier as now.
2. Layer: PASS (back; faded by the game). 3. Outline: PASS (none). 4. Shapes: PASS (arches round and
   identical). 5. Shading: PASS. 6. Palette: PASS (8). 7. View: PASS.
8. Fit: FAIL for silhouette: the wall (on screen 150 to 200) is the mid row's value (155 to 207); on the y 120
   greyscale sheet the arcade has no edge against the house behind it. Fix: a 4 px dentil cornice and a 2 px
   shadow line under the roof strip, and the low row's plaster one step darker than the mid row's (see the
   mid row fix in the sweep review).
9. Read: PASS at the street tier with the statue (A4 is the closest screen to its concept).
VERDICT: FAIL (arch scale, silhouette).

## dtl_wing_front 64x130 (back): the bakery's wing

Pink plaster, grey quoins, a double door 36x90.
1. Scale: PASS (door 0.8 by 2 m). 2 to 7: PASS. 8. Fit: FAIL for silhouette, same as the arcade (no cornice,
same value as the mid row). 9. Read: PASS.
VERDICT: FAIL (silhouette only; the cornice fix).

## dtl_guild_front 128x126 (back): the guild hall's ashlar wall and door

1. Scale: PASS (door 36x90, hall 2.7 m). 2 to 7: PASS. 8. Fit: PASS (the stone reads as a different material
from the plaster around it; it has an edge). 9. Read: PASS.
VERDICT: PASS.

## dtl_pav1_front 88x148, dtl_pav2_front 72x148 (back): the market pavilions

Ochre plaster, a shop bay (green / red frame) from the approved parts.
1. Scale: PASS. 2 to 7: PASS (approved parts). 8. Fit: FAIL for silhouette: plaster at 152 on screen beside
the mid row's pink house at 155 (x 1600 y 120); the only edge is the dark roof strip. Fix as the arcade (dentil
cornice, shadow line, plaster one step darker than the mid row). 9. Read: PASS at the street.
VERDICT: FAIL (silhouette).

## dtl_kioskhouse_front 56x156, dtl_shelterhouse_front 56x140, dtl_canalhouse_front 48x156 (back)

Plain plaster strips with a door (36x90).
1. Scale: PASS. 2 to 7: PASS. 8. Fit: FAIL. 56 px of blank plaster at 156 between mid-row walls at 155 to
176 (x 1920 y 120): the house is invisible except for its bar. Fix as the arcade, plus one storey-height detail
each (a shuttered window 28x40 at y 300, or a sign) so the strip reads as a house. 9. Read: FAIL at y 120
(a strip), PASS at the street behind the kiosk and the shelter.
VERDICT: FAIL (silhouette, read at the high tier).

## dtl_shed_front 88x144 (back): the tram shed

Granite wall with a round-arched gate.
1. Scale: FAIL. The gate opening is 40 px (0.87 m): a door. A tram gate is the approved tramshed96's width
(about 100 px) or at least 2.5 m (115 px). Fix: the gate the whole 88 px wide (piers at the edges) or the shed
grown to 128 px with a 100 px gate; the roof strip and the DORMER box (1912-2000) follow.
2 to 7: PASS. 8. Fit: PASS (granite, an edge). 9. Read: FAIL at 1x: a stone house with a door, not a shed.
VERDICT: FAIL (gate scale).

## dtl_hall_front 160x176 (back): the glass flower hall

Blue-grey glazing in granite pilasters, a door.
1. Scale: PASS (3.5 by 3.8 m). 2 to 7: PASS (asset_qa's "uneven storey windows" is the heuristic reading one
glazed wall as storeys; not a defect). 8. Fit: PASS (the glass is a different material; it has an edge).
9. Read: PASS as a glass house; the maker's note that more lattice would help is right but not a FAIL.
VERDICT: PASS.

## dtl_start_front 140x352 (back, building): the start house

The approved town_door ground floor plus a first floor with two windows and flower boxes, a hipped roof of
brown courses, a chimney stick.
1. Scale: PASS (2 storeys 7.7 m; door 36x90).
2 to 4: PASS. 5. Shading: PASS. 6. Palette: PASS (20). 7. View: PASS.
8. Fit: FAIL on two counts. The chimney at x 130 is an 8x24 brown stick in the roof's own dark colour with no
cap: a plank. The roof is brown with pink course lines; the mid row's roofs behind it (x 0 y 0) are the same
brown at the same value (128 median both), so the one true-scale roof on screen 1 does not step forward from
the half-scale roofs behind it. Fix: chimney 10 px wide, a 2 px stone cap, body one shade darker than the roof;
roof in two oxblood tile shades (the scallop stamp, 4 px courses, 2 px ridge cap) and the mid row's roofs
25 luma lighter.
9. Read: PASS (a two-storey house).
VERDICT: FAIL (chimney, roof value).

## dtl_bakery_front 148x320 (back, building): the bakery

Two approved bays side by side, a first floor with flower boxes, a low stepped roof band.
1. Scale: PASS. 2 to 5: PASS. 6. Palette: FAIL by the script (21 colours; two approved bays): accepted, the
parts are approved; not a visual defect. 7. View: PASS. 8. Fit: FAIL (small): the roof is a 16 px stepped
band with the chimney stick again (no cap). Fix as the start house's chimney; the band is fine as a parapet.
9. Read: PASS.
VERDICT: FAIL (chimney only).

## dtl_closed1 to closed22 _front (back, building): the 22 decorative shops and houses of screens 1-4 and 9-11

Three kinds. One-storey shops with a stepped roof hat (closed1, 3, 4, 5, 8, 9, 11, 13, 15, 16, 19, 20, 21;
194 tall), one-storey shops with a flat cornice and a chimney stick (closed7, 12, 17; 168), two-storey houses
with a hip roof or a flat top (closed2, 6, 10, 14, 18, 22; 312 to 338). Ground floors from the approved fronts.
1. Scale: PASS (doors 36x90, windows 36x60, storeys 140).
2. Layer: PASS (back, faded; on screen 125 to 166; a step darker than the mid row's cream, the same as its pink
   and ochre: see the sweep review).
3. Outline: PASS (none).
4. Shapes: FAIL. The roof hats are striped brown triangles with grey step caps at each course end: they read
   as ziggurats, not tile (x 320, 640, 3200 at y 120). The chimneys are 5 to 8 px brown sticks with no cap, in
   the roof's dark colour (closed1 x 80-87, 8x18; closed4; closed13 5x30; closed16; closed7 and 22 on flat
   tops): planks.
5. Nothing floats: FAIL. File rows are empty between the roof and the house: rows 37 to 39 on closed3, 5, 8,
   15, 18, 20 (a 3 px slit: the mid row shows through across the whole width, x 640 y 120 screen y 137-139,
   x 0 y 120 the same rows), row 39 on closed1, 4, 10, 13, 16, 19 (1 px), row 13 on closed7 and 22 (the chimney
   1 px off its roof).
6. Palette: PASS (10 to 21; closed10/14/18's "speck in the glass" is the approved shop bay's goods, not a
   defect).
7. View: PASS.
8. Fit: PASS for crispness (stamped, same pixel size as the bench).
9. Read: PASS at the street tier (shops and houses). FAIL at the roof tiers (hats and sticks).
Fix, one kit for all 22: fill the empty rows so the hat and the chimney touch the cornice; redraw the hat as a
tile hip (three 4 px scallop courses in two oxblood shades, a 2 px ridge cap, no step caps); chimneys 10 px
wide with a 2 px stone cap and a body one shade darker than the roof. The ground floors stay.
VERDICT: FAIL (the roofs and chimneys; the ground floors pass).

## Summary

| Piece | Verdict | Cause |
| --- | --- | --- |
| wing, arcade, pav1, pav2, kioskhouse, shelterhouse, canalhouse roof strips | FAIL | dark bar, no roof read |
| shed roof | FAIL | the strip, plus a 24x12 dormer standing on the coping |
| hall roof | FAIL | an 8 px ledge for a roof garden |
| guild roof | FAIL | brick fill, the busiest mass on the screen |
| pav1, pav2, guild canopies | FAIL | hung planks with teeth, off their shop fronts, pav1's across two buildings |
| arcade front | FAIL | 26 px arches; no silhouette |
| wing front | FAIL | no silhouette |
| guild front | PASS | |
| pav1, pav2 fronts | FAIL | no silhouette against the mid row |
| kioskhouse, shelterhouse, canalhouse fronts | FAIL | blank strips, invisible but for the bar |
| shed front | FAIL | 40 px gate |
| hall front | PASS | |
| start front | FAIL | plank chimney, roof at the mid row's value |
| bakery front | FAIL | plank chimney |
| closed1-22 fronts | FAIL | hats as ziggurats, plank chimneys, 1 to 3 px slits under the roofs |

2 PASS, 45 FAIL. The FAILs come from five causes: the parapet-only roof language, the value of the low row
against the mid row, the canopy drawing and placement, four doll-sized openings and details, and the decorative
roof kit (hats, sticks, slits). None of the 47 is dirty.
