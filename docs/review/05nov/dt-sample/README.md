# Downtown sample screen (art/dt-sample-05nov, night of 5 Nov 2026)

Screen 7 of `downtown_tall` (camera x 1920), at the high road camera (y 120) and the street camera (y 240). Owner's picks of
26 Oct from `docs/layer_plans/downtown_tall.md` (branch night/25oct-dt-plan): 1a (first floor) and 4a (shelter and
gateways at true scale, crate perches). Everything is built from parts on integer grids: 0 SpriteCook credits, 0 Artlist.

Pieces (scripts: `tools/build_tall_fronts.py`, `tools/build_dt_street.py`; sources `art/source/dt_sample/*.aseprite`):
town_front_tall1-3 (432 tall), town_shelter_tall, town_gateway70/96, town_crates70/96, town_breadboard, town_crate_leg, town_hood.
Code: `riverwalk/arthooks.lua` (H.FIRST_FLOOR, drawTownBack, drawTownGateways, drawTownStops, townPiece), `stage.lua` (one call).
The level map is unchanged.

Frames: `frames_before/`, `frames_after/` (1x, `tools/dt_sample_frames.sh`), board images `board/`
(`tools/dt_sample_board.py`), QA cards `cards/`, the board entry `board_item.json`.

## Luma, screen 7 (median / darkest 10 %, share of the screen; `tools/layer_frames_tall.py downtown_tall --ids`)

| Layer | y 120 before | y 120 after | y 240 before | y 240 after |
| --- | --- | --- | --- | --- |
| sky | 120 / 95, 49 % | - | 108 / 108, 7 % | - |
| clouds, far city, tree line (far roofs), mid (old town row) | 236, 187, 172, 148; 6 % | - | 236, -, 172, -; under 1 % | - |
| back | 179 / 125, 39 % | 179 / 125, 96 % | 154 / 125, 55 % | 169 / 126, 65 % |
| ground | - | - | 89 / 53, 27 % | 89 / 53, 27 % |
| play | 135 / 15, 4 % | 137 / 15, 3 % | 111 / 2, 10 % | 109 / 15, 6 % |
| Pepper and pickups | 58 / 1, 2 % | 58 / 1, 2 % | 58 / 1, 2 % | 58 / 1, 2 % |

Order on the screen: back 169-179, play 109-137, Pepper 58. The back median rises from 154 to 169 in the street frame
because the houses' plaster (unchanged colours, about 179 on screen) now fills what the sky and the old town row filled.

## Checks (branch head)
PEPPER UNCHANGED (4591 steps), flow 125/125, Tiled PASSED, `downtown_tall --physics` 102/102, `--qa` 0 problems in 14643
runs, `--auto` GOOD GIRL, `check_curve` T1-T4 PASS (order riverwalk..night, 10 seeds), `asset_qa`: the 11 new pieces PASS
(the library's 8 FAILs are the same as on the base), check_backdrop: only the known River Walk gable. Downtown is not in
check_backdrop's scope (scene code); its tops were checked in the sweep at camera y 0: never on screen.

## Open doubts for the reviewer
1. The far layers and the spire are hidden wherever the tall street runs (screens 5-8); the spire shows on 1-4 and 9-11.
2. Screen 6: the four small plaza houses (decision 2, not picked) now stand at a quarter scale in front of 3-storey fronts.
3. Screen 10: `town_gateway96` stands alone on the flooded square, no house behind it, so its cornice top shows.
4. The plain high road ledges (x 2016, 2112) keep their small stone cornice art: on the facade they read as stone shelves.
5. The tram stop sign and the cargo bike's rider are still drawn in code (decision 5, held); the rider passes behind the
   board at 48 px, which crosses his waist.
6. The street lamp on the gallery (x 1830) stands against the facade (decision 5's wall lanterns, held).
7. Back median 169 in the street frame against the plan's 154 (see above).
