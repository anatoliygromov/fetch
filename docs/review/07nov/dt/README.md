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
| `tools/check_curve.py` (10 seeds, base) | see the CURVE BASE line at the end of this file |
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

CURVE BASE (origin/main 5f30120, 10 seeds): filled in below when the run finishes.
