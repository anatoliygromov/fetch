# Downtown sample screen (art/dt-sample-05nov, night of 5 Nov 2026)

Screen 7 of `downtown_tall` (camera x 1920), at the high road camera (y 120) and the street camera (y 240). Owner's picks of
26 Oct from `docs/layer_plans/downtown_tall.md` (branch night/25oct-dt-plan): 1a (first floor) and 4a (shelter and
gateways at true scale, crate perches). Everything is built from parts on integer grids: 0 SpriteCook credits, 0 Artlist.

Pieces (scripts: `tools/build_tall_fronts.py`, `tools/build_dt_street.py`; sources `art/source/dt_sample/*.aseprite`), after round 1:
town_front_tall1-4 (432 tall), town_shelter_tall, town_gateway, town_crates70, town_breadboard, town_crate_leg, town_portal_top, town_oriel.
Code: `riverwalk/arthooks.lua` (H.FIRST_FLOOR, drawTownBack, gatewayX, drawTownGateways, drawTownStops, drawTownPerches, townPiece), `stage.lua` (two calls).
The level map is unchanged.

Frames: `frames_before/`, `frames_after/` (1x, `tools/dt_sample_frames.sh`), board images `board/`
(`tools/dt_sample_board.py`), QA cards `cards/`, the board entry `board_item.json`.

## Review round 1 (FAIL, 5 Nov) and what changed (`review_round1/`)

| Finding | Change |
| --- | --- |
| Back lighter than the far layers (plaster 179, gateway 192) | Every built colour set from its on-screen luma (`tools/asset_qa.py` as drawn, back fade 0.28 + shader): plaster 146-156 per house (`H.PLASTER`, the art's yellow ramp), granite 166 / 148 / 126, frames 170. On screen the houses are 145-152, the old town row 169, the far roofs 172-181 |
| Perches as light as the wall (179) | Crate wood and bread re-ramped: crates, legs and board 104-107 median on screen (apple crates 107) |
| Crate sizes 35, 32 and 14 high | One crate: 34 x 17 front-on, 16 x 17 end-on, 18 px pitch; the 96 stack is gone (screen 10 keeps its old gate) |
| Crate legs without an outline | Play pieces, outlined, two whole crates each; the board is two planks (12 rows) so they fit |
| String courses differ, 144 apart | The course is the ground floor's cornice (7 rows) repeated at rows 0, 140, 280: storeys pixel-identical |
| Shelter glints (dashed, white, contrast 159) | One 2 px 45 degree band per pane in a mid glass colour; poster card dimmed; contrast within 120 |
| Gateway a block across a seam; alone on screen 10; colours not in the palette | An arch with no wall of its own, 80 wide, centred in the house holding the GATE's right end (x 1912-2000); no gateway where no house (screen 10: the old gate piece); palette re-made after the change, every colour in it |
| Hood floating with no window | Removed: the dormer's ledge is the plain stone ledge, like the high road's other ledges |
| Guild house a stub (pick 1a not done) | Full height with its own front (148 px, windows at the sides); the stepped gable is the portal top (`town_portal_top.png`), the chimney the bay window's roof (`town_oriel.png`); perches unchanged |
| Rider cut at the waist by board and crates | The crate perches are drawn in their own pass before the cargo bikes (`H.drawTownPerches`, stage.lua) |
| asset_qa depends on --fade | `--file` now uses the game's own fade for the file when --fade is not given and prints it |
| Palette | v1 is made from these pieces: their "only palette colours" check passes by construction, not as evidence. The house plasters other than yellow are swapped at draw time and are not in the file |

Left for the owner (card notes, no change): the plaza houses at small scale (decision 2), lamps across window panes, the high road ledges as shelves (their old art, 137 on screen, only 11 above the back), the far layers hidden on the tall street (x 1180-2480), the street ends.

## Review round 2 (c3cb066: fronts 1-3, gateway, crates, legs, portal top PASS) and what changed

| Finding | Change |
| --- | --- |
| town_front_tall4: windows flush with the house edges, the right one clipped by 2 columns | Second floor: two windows with the street's margins (14 px left, 12 right, the cast shadow on the right), whole and pixel-identical (blocks at x 14 and 78); first floor: no windows, the bay window stands there |
| town_shelter_tall: poster card 194 on screen | Card (113, 108, 94): about 150 on screen; the pink a step under it |
| town_breadboard: (73, 8) not ink | The second plank's grain stops at x 72: the outline is closed |
| town_oriel: a chimney with a small window, at the wall's value | Now a bay window at the house's scale: `town_oriel_bay.png` (decoration, 58 wide, 135 on screen, a 44 px window with the house's panes and frames, a 3 px shade down its right edge, a sill, a corbel stepping in to the crown) under `town_oriel.png` (play, the copper roof, front-on, a thin cap 9 rows: its flat 16 px top is the CHIMNEY box's top, the golden bone exactly where it was; 113-132 on screen) |
| Street lamp x 1958 inside the arch (x 1916-1996) | Not moved: no other house front fits. House 1912-2000 is the only one where the cargo bike comes out (its run starts at x 1930); 2000-2180 are behind the shelter, 1700-1912 has the plaza houses and the fountain in front. The lamp is a checkpoint (it cannot move). The lamp stands in front of the arch: a card note |
| Window panes drab (124, 26 under the plaster) | Glass (31, 37, 45), reflection (47, 55, 62): panes about 100 on screen, 52 under the plaster; the back contrast stays within 120 (frames 171 to panes 100) |

Card notes, no change (round 2): the portal top partly behind the balcony and plaza houses, the dormer ledge reading as a lintel, the shelves, screen 10's old brick gate (no house there), the plaza houses at small scale, the far layers hidden on the tall street, the street ends, the bike's depot clip.

## Review round 3 (f50160f: 11 of 13 PASS) and what changed

| Finding | Change |
| --- | --- |
| town_oriel: a 60 px outlined roof over the 16 px solid CHIMNEY box (art wider than its hit box; an invisible core in the bay) | Split: `town_oriel.png` is now exactly the box (18 x 45 with its outline): the bay window's central stone pier under a copper cap, the golden bone's perch at y 200 unchanged, so what stops Pepper is what she sees. The bay's roof across 58 px moved into `town_oriel_bay.png` (decoration, no outline, edges a darker copper, 124 to 150 on screen), with two lights either side of the pier |
| Screen 10 keeps the old brick gate | No change (no house there): on the card as the question, with the lamp in the arch |

## Luma after round 1 (median / darkest 10 %, share of the screen; `tools/layer_frames_tall.py downtown_tall --ids`)

| Frame | Back before | Back after | Play after | Far layers visible |
| --- | --- | --- | --- | --- |
| screen 7, y 120 | 179 / 125, 39 % | 148 / 125, 96 % | 137 / 15 | none |
| screen 7, y 240 | 154 / 125, 55 % | 145 / 111, 63 % | 105 / 15 | none |
| x 1600, y 120 (guild house) | 154 / 122, 26 % | 145 / 125, 82 % | 104 / 12 | none |
| x 1600, y 240 | 154 / 122, 44 % | 145 / 122, 53 % | 104 / 15 | none |
| x 2880 (no houses) | - | - | 71 | old town row 169, far roofs 181, far city 194 |

Order: far city 187-194 > far roofs 172-181 > old town row 169 > houses 145-152 > play 104-137 > Pepper 58.

## Checks (round 3 head: the same results)
PEPPER UNCHANGED (4591 steps), flow 125/125, Tiled PASSED, `downtown_tall --physics` 102/102, `--qa` 0 problems in 14643
runs, `--auto` GOOD GIRL, `check_curve` T1-T4 PASS (order riverwalk..night, 10 seeds), `asset_qa`: the 11 pieces PASS as
drawn (library 8 FAIL as on the base), check_backdrop: only the known River Walk gable.
