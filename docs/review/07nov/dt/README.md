# Downtown (tall), 7 Nov: the low row built (option A, Phase 2), track dt, branch `day/07nov-dt`

Phase 1 (the diagnosis, the options, the greyboxes, the concept briefs) is in `design/`. The owner picked option A
(the roofs of a low true-scale row are the high road), with yes to real tiled roofs at the roof tier, the start house
as a two-storey house, and canopies on the middle tier as part of the shop fronts (no hung balconies anywhere).
Concepts (Artlist, design targets only, never cut): `art/gen/concepts/dt_design_A1_a.png` .. `A4_a.png`.

## What changed

- **The low row** (`tools/build_dt_rooftops.py`, `--check` PASS, 47 files, 0 credits): every building is built. The
  ground floors are whole-pixel crops of the approved styled fronts (`town_front_tall<k>_<s>`, rows 284-431, plaster
  swapped as the game does), the start house is `town_door`'s ground and first floor, the tram shed holds
  `town_gateway`; the arcade's three arches, the guild hall's ashlar wall, the glass hall are drawn by rule; the
  roofs are stamped parts (tile courses, lead sheets, granite coping and parapet, crow steps, chimney, dormer, flower
  boxes). Roofs Pepper walks on are play pieces: unbroken 1 px ink outline, unfaded, the walk's ink row at the box's
  top - 1, the image exactly the box + 1 px a side, so the hit box is the art. Fronts are decoration: no outline,
  faded 28 % by the game, in the fronts' own ramps (every front with its roof stays within the back layer's 20
  colours, except the bakery: two approved bays side by side, 21).
- **The placement table** `riverwalk/dt_lowrow.lua` (generated) and `arthooks.lua` (`H.LOW_ROW`, `H.lowRowPiece`,
  `H.drawLowRow`): each building claims the map boxes it draws or hides. Hidden: the tall fronts, the HOUSE boxes,
  the plaza balconies' rails, the gallery / loggia / dormer / ledge / flower-roof kit, the wall-lantern brackets (the
  high lamps are posts on the roof terraces). `scene.lua`: one line, `Sc.drawBalconyRails` off in low-row mode. With
  the table absent, everything draws as before.
- **The map** (`maps/downtown_tall.tmx`, export regenerated): BALCONY 1552 y 344 -> 312 (the guild hall's porch roof
  sits over its 2.1 m door; from the statue's arm it is 34 px across and 36 up, a running held jump); DORMER
  1920-1976 -> 1912-2000 (the whole tram shed roof: the gap from the pavilion is 24, to the kiosk house 16);
  FLOWER ROOF 2288-2376 -> 2216-2376 (the whole flower hall roof: the springy awning's bounce now lands on it).
  Nothing else moved: the bakery sign, the wing (272), the arcade (280), the crow steps (272 to 244), the chimney
  (200), the pavilions (256), the kiosk house (248), the shelter house (264), the canal house (248), the footbridge
  (272), every street piece. `tests_downtown_tall.lua`: the two middle-tier rows for the porch.
- Alleys: the gaps between the walkable roofs (16 to 48 px) are open slots between the houses; the mid row shows
  through them, which is also how a jump gap reads from the roofs.
- `tools/draw_routes.py` middle tier updated; `tools/asset_qa.py` and `tools/measure_layers.py` register every
  `dtl_` file (fronts back + building, roofs and canopies play); `docs/art_hooks_r8.md` has the section;
  `tools/pipeline.py`: family `dt_lowrow` (tier C, built, ingame; next: the independent review).

## Frames

- `beside_concept/A1..A4_before_concept_after.png`: before (main), the concept, after (in game, 3x).
- `after/`: the four concept screens in game at 1x, 3x and 3x greyscale. `before/`: the same spots on main.
- `sweep/tiers_screens_*.png`: every screen at every camera tier (2x), after. (`design/asis/` has the before.)
- `cards/`: `tools/qa_card.py` cards (PASS) for the guild roof, the arcade roof, a pavilion roof, the hall roof,
  the shed roof, a shop canopy; 5x beside the bench, bin and lamp; in-game frame in colour and greyscale.
- `routes_before.png`, `routes_after.png`.

## Checks (each with its own XDG_DATA_HOME)

| Check | Result |
| --- | --- |
| `tools/check_pepper.sh` | PEPPER UNCHANGED: 3908 steps identical |
| `--physics downtown_tall` | 102 of 102 passed (two middle-tier rows updated for the porch) |
| `--qa downtown_tall` | 14862 runs, 880680 frames, 0 problems |
| `--auto downtown_tall` | GOOD GIRL! 56.8 s, 64/102 bones, 3/5 secrets, no heart lost (base 56.2 s, 65/102) |
| `tools/check_flow.sh` | 125 of 125 passed |
| `tools/check_tiled.sh` | TILED CHECK PASSED |
| `tools/check_backdrop.py` | BACKDROP OK |
| `tools/check_curve.py` (10 seeds, branch) | T1-T4 PASS; Downtown (tall) DI kids 11.6, parents 24.7, retro 8.1, worst spot 4 Bakery row (20 %), Elsa 100 %, lost 3.8 % |
| `tools/check_curve.py` (10 seeds, base main 5f30120) | T1-T4 PASS; Downtown (tall) DI kids 11.6, parents 18.5, retro 7.9, worst spot 4 Bakery row (21 %), Elsa 100 %, lost 1.2 % |
| `tools/build_dt_rooftops.py --check` | PASS, 47 files |
| `tools/asset_qa.py --file` on every `dtl_` file | roofs and canopies (20 files): PASS. Fronts: 22 PASS, 1 WARN (closed2: one near-colour patch), 5 FAIL by heuristics on approved parts: `dtl_bakery_front` 21 colours (the shop bay + the door bay, 19 + 18 approved colours, side by side); `dtl_closed10/14/18_front` "speck in the glass" on the approved shop bay's goods seen as a storey window; `dtl_hall_front` the glass hall's panes read as uneven storey windows (it has no storeys). Not changed: the parts are the approved fronts and the glasshouse is one glazed wall. |

## Known limits and open points (for the reviewer and the owner)

1. The fountain (basin, column, bowl, jets) is unchanged: it now stands free between the two pavilions with the sky
   and the mid row behind, which was the owner's "weird on top of the buildings". The jets are the 6 Nov streams.
   A rebuild to the A2 concept (a granite column with a ball finial, a round basin) is the next piece.
2. The mid row (`town_facades.png`, "needs total rework") is unchanged: with the low row in front it is the lighter
   layer behind the roofs. A rebuild from the styled parts at half size is the piece after the fountain.
3. The sky (the haze "very technical") is unchanged.
4. The decorative roofs of screens 1-3 and 9-11 are half detail by design (no joints, the fronts' own ramps): they
   sit a step lighter behind the street pieces and never have an outline, so nothing there reads as standable.
5. The flower hall is a plain glazed wall with granite pilasters: more iron lattice would help its character; left
   calm on purpose (the awning and the roof garden are the route).
6. The porch at 312 replaces the first middle-tier balcony at 344: the arm -> porch jump is +36 up over 34 px (a
   running held jump, proven by --physics); the middle tier is a secret route, so the difficulty curve did not move
   (T1-T4 PASS, DI within 1 of the base).

7. The curve: kids unchanged (11.6), parents 18.5 -> 24.7 (now inside the owner's 22-28 band for the mid levels),
   retro 7.9 -> 8.1, lost runs 1.2 % -> 3.8 % (10 seeds; T1-T4 PASS on both). The map moved three boxes, so the
   levers if the reviewer wants the base numbers back: the porch at 312 (36 up from the arm; 344 would need a
   1.5 m door under it), or the flower hall roof back to 2288-2376 (then the bounce needs Right held again).

# Round 2 (after the independent review, art/gen/reviews/dt_sweep_07nov.md and dt_lowrow_07nov.md)

All eight fixes of the review, in its order, plus the two items from other tracks. Frames in `round2/`:
`beside_concept/` (round 1 | concept | round 2 at 3x), `after/` (1x, 3x, 3x grey), `before/` (round 1 at 3x and
grey), `sweep/` (every screen at every tier, 2x colour stacks and 1x greyscale tier rows), `cards/` (8 PASS cards),
`routes_round2.png`.

| Fix | Done | Where |
| --- | --- | --- |
| 1 Mid row vertical scroll | The mid layer moves with the world in the tall Downtown: `L.vmid = 1.0` in `level/downtown_tall.lua`, read by `vcam.lua` `Vc.parallax` (one line: a level's own mid factor, else `Vc.MID`; the other tall levels unchanged). Its foot stays at world 388 at every tier: its lowest storey (windows 338-368) is 52 px below the lowest eave (286) and 100 below the highest; the storey over the roofs has its windows at 200-220. Nothing of it stands on a cornice at any tier (sweep y 120, x 0 to 3200). | vcam.lua, level/downtown_tall.lua |
| 2 Mid row lighter, quieter, half size | `town_facades.png` rebuilt (960 x 330, 14 colours, asset_qa PASS at mid): three plaster pairs, 3 or 4 storeys of 70 px, one 14x22 window per 24 px of front, frames in the plaster's shade, glass source 134/148/166, pink-grey tile hips and lead flats, a chimney on every third house, one garden wall with a gate (sky through it behind the fountain at the A2 camera). Measured on screen: mid walls median 201 (A1, A2), low row walls 152-156: 45 luma apart. look.lua untouched. | tools/build_dt_rooftops.py (mid row block) |
| 3 Roof strips as roofs | One ramp on all nine strips: granite parapet body (on screen median 162), a 2 px coping, the ink row, a 3 px lead seam row on the walk, a 6 px scallop tile eave course (two oxblood shades, contrast 28) on pav1, pav2, the kiosk, shelter and canal houses, under it a 4 px dentil cornice and a 2 px shadow; the wing and the arcade keep lead (no eave course). | `roof_strip()` |
| 4 Fronts with an edge | The cornice and shadow are in every roof strip (unfaded, crisp); the low row's plaster is 45 luma under the mid row's; the kiosk house, shelter house and canal house each have a 28x40 (28x32 on the shelter house) shuttered window over the door. | `shuttered_window()` |
| 5 Decorative roof kit | No empty rows: the hip sits on the cornice band, the chimney's foot is in the roof (numpy: no transparent row inside any front). Hats are tile hips (scallop courses, two oxblood shades, a 2 px stone ridge cap, no step caps); chimneys 10 px with a 2 px stone cap, body in the oak ramp one shade darker than the tile. Every closed house, the start house and the bakery. | `hip_roof()`, `chimney()` |
| 6 Canopies | Cloth canopies in the street awning's ramp (town_awning64's four colours): the box's width + 2, a 10 px sloping cloth, a 3 px scalloped valance with the ink edge. Boxes: PORCH 1568-1618 y 312 (a granite slab on brackets over the guild door 1572-1613), CANOPY 1680-1752 y 336 (pav1: the reviewer's 1688-1760 left a 70 px gap from the porch that the running jump does not clear, lands at x 1701; 1680 starts at the pavilion's own edge and spans its window 1692-1755 but 3 px), CANOPY 1816-1888 y 344 (pav2, as given). Physics 102/102 with the middle tier rows rewritten. | map, `cloth_canopy()` |
| 7 Fountain to A2 | Built: a 16 px granite column with a capital and a ball finial, top at y 296; the bowl 48 px at y 344 (the TIER box) with water in it; the plinth 32 px at y 400 (the FOUNTAIN box); the two rim blocks (RIM boxes); a kerb basin 1736-1848: a far coping, a water band, a 3 px kerb at the street, and below the street the basin's outer face in the quay wall's blocks (the water box's pit no longer shows as a pond). Jets: two 2 px arcs from the capital into the basin's band with a running highlight (`H.drawLowFountainJets`, called from `Sc.drawTerrainArt` before the play props, so the column stands in front of their first pixels). At the y 120 tier sky shows behind the column through the mid row's garden-wall gap at the A2 camera (x 1580). | `dtl_fountain_*`, arthooks.lua, scene.lua |
| 8 Openings | Arcade: two arches of 46 px on 10 / 8 / 10 px piers, the statue in front of the middle pier. Shed gate: an arched carriage gate 62 px wide and 100 px tall from x 1934 (its left jamb is the cargo bike's depot line, see A) to 1996. Not 100 px: the shed is 1912-2000 and the kiosk house starts at 2016 (a route gap of 16 px); a 100 px gate would need the shed to swallow that gap or the crates to cover the opening again. It is the baker's cargo bike's gate, 1.35 m. Dormer: 40x30 behind the parapet, its sill hidden, a two-course tile cap. Roof garden: a 12 px wrought-iron railing in ink with three 16x6 planters (outlined). Guild roof: scallop tile fill (contrast 28), brick only on the chimney, granite crow steps as before. | `build_dt_rooftops.py` |
| A Cargo bike doorway | GATE 1864-1934 (was 1868-1938, same width and height), zone 1 depot 1934 (`relx.depot` 4), the shed's gate opening starts at 1934: the crates (1863-1934) end at the jamb and the bike is clipped exactly at it. Zone 2 (3168) is the free courtyard gate's right jamb already (opening 3070-3170); unchanged. Checked by geometry (the depot line, the crates' right edge and the jamb are the same column); no bike frame rendered. | map |
| B Names | BALCONY / LOGGIA / GALLERY / DORMER and the three unnamed ledges renamed in the map: WING ROOF, ARCADE ROOF, PAVILION ROOF (2), SHED ROOF, KIOSK ROOF, SHELTER ROOF, CANAL ROOF, PORCH, CANOPY (2). Tests and draw_routes use coordinates; their labels updated. | map, tests, draw_routes |

Checks (own XDG each): PEPPER UNCHANGED; physics 102/102; qa 14878 runs 0 problems; auto 57.1 s, 64/102 bones, no
heart lost; check_flow 125/125; check_tiled PASS; backdrop OK; check_curve 10 seeds T1-T4 PASS, Downtown (tall) DI
kids 11.9, parents 24.7, retro 7.8, lost 2.5 % (round 1: 11.6 / 24.7 / 8.1 / 3.8 %; base 11.6 / 18.5 / 7.9 / 1.2 %);
`build_dt_rooftops.py --check` PASS (52 files). asset_qa: all 21 play pieces PASS, town_facades PASS (mid),
dtl_fountain_basin PASS (ground); fronts 34 PASS, 1 WARN, 4 heuristic FAILs on approved parts as in round 1
(bakery 22 colours and closed14 21: two approved bays plus the oxblood tile; closed10/14/18 "speck in the glass" on
the approved shop bay's goods). No credits spent, no SpriteCook or Artlist calls.

Open: the sky haze (sky track); the hint bubbles over the canopies read as before.

# Round 3 (after the second review, 5187d45, and the art director's notes)

Frames in `round3/`: `beside_concept/` (round 2 | concept | round 3 at 3x), `after/`, `before/` (round 2),
`sweep/` (every screen at every tier, colour stacks and greyscale rows), `cargo/` (the cargo bike at the shed's
gate, 1x and 3x), `cards/`, `routes_round3.png`.

| Item | Done |
| --- | --- |
| Bones (chars reviewer) | `tools/dt_bone_overlap.py`: every bone against the play art (roof images below the walk's top, canopies, the fountain, the statue, the jets, play boxes). Moved: 1452/1476 y 384 -> x 1444/1484 (off the statue's coat), the hat's gold bone 316 -> 308, the plinth and bowl bones 1792 -> 1775 (off the column). 102 bones, 0 overlap; physics 102/102 (counts, pickups, "within a jump of a floor" hold). Commit f52c3fc. |
| Violet kerb face and quay wall | A second ground paint with the look off (`stage.lua` `groundRaw`, only the tall Downtown with the low row), its rows from the kerb face down drawn over the graded street with `Look.off()`, as the bonus round does; the drains are drawn in that pass. Measured on screen: 72/66/64, 78/72/69, joints 47/43/47, the file's own; the street's cobbles pixel-identical to before. No look.lua change. Commit b97f143. |
| R3.1 the canal house's balcony | Box 2420 y 328 renamed CANOPY, claimed, drawn as a cloth canopy over the canal house's door (box width + 2, the same ramp). The route keeps it (tub -> table -> parasol -> the canopy: physics row passes). |
| R3.2 the lamp in the gate | Lamp 1959 -> 2040 (2008 and 2030 put the respawn inside or against the KIOSK box 1980-2020: `--qa` 5 problems; at 2040 her 34 px box clears it and the shelter: 0 problems). The checkpoint moves with it; physics and curve rerun. `cargo/cargo_at_gate_x1962_*.png`: the bike clipped at the jamb 1934, the opening clear, the lamp in front of the shelter's end. `LOOK_CARGO=x` now also works in a sweep (tests_look.lua). |
| R3.3 the hats' stripes | The rows beside a hip were filled with the ground floor's top row (window frame pixels: vertical stripes). They are transparent now: the hip is the silhouette, sky or the mid row shows beside it (`front_canvas(fill_rows=6)`). The hips' edge pixels in the lit shade (no dark rim: asset_qa decor-ink clean). |
| AD.1 sky | The mid row's foot lowered to world 430 (under the street line; `Sc.MID_FOOT_LOW`, scene.lua, low-row mode only) and cut to three storeys of 64 px with 36 px hips: its cornice at 234, gables to 198. At the y 120 tier: 78 px of sky over the gables, 50 to 86 px of houses over the low row's eaves; the far roofs (0.25) and the spire are the skyline behind. |
| AD.2 front row colour | The low row's plasters a step more saturated than the tall fronts' (the swap is the build's): ochre 0.49, salmon 0.35, oxblood 0.40, cream 0.30 measured on screen (bakery, pav1 0.49; the wing 0.35); values unchanged (153 to 173). Tile hips 36 to 44 px over the eave on the bakery, the start house and the closed row; the guild gable 28 px (its boxes). |
| AD.3 mid row tint | Pale ochre, pale rose, pale grey-blue, cream (source saturation 0.3 to 0.5; on screen after the mid fade and the look's 0.7 saturation about 0.1 to 0.15 on the walls, lower where the windows are sampled); walls 184 to 195 on screen against the low row's 153 to 173. asset_qa PASS at mid (14 colours). |

Checks: PEPPER UNCHANGED; physics 102/102; qa 0 problems; auto 57.1 s; flow 125/125; tiled PASS; backdrop OK;
curve T1-T4 PASS, Downtown (tall) kids 11.9, parents 24.7, lost 2.5 %; build --check PASS (53 files); asset_qa:
every play piece, the basin and the mid row PASS; fronts: 2 colour flags (bakery 22, closed14 21: two approved bays
plus the tile pair) and 1 WARN (closed2). No credits.
