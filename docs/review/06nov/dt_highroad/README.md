# Downtown high road attached to its house fronts (art/dt-highroad-06nov, 6 Nov 2026, 0 credits)

The owner on the roofs frames (camera x 1440-1640, y 120): "this looks weird". Since decision 1a the fronts are true
scale and run past the top of the screen, but the high road's pieces were drawn for the old small roofs, so they hung
in the middle of a big wall. Now every piece Pepper stands on up there belongs to a facade. No box moved.

| Piece | Before | Now |
| --- | --- | --- |
| guild house (GUILD ROOF steps, x 1560-1680) | a grey brick pyramid with a brown disc, mid facade | `town_front_tall6`: a granite ground floor whose top is the steps' line, down to the street, a 2.1 m oak door, a French window behind each balcony; `town_guild_steps` is its stone coping (outlined, on the boxes) |
| CHIMNEY (x 1628, y 200) | the bay window's pier in front of a dormer window | `town_guild_pier`: a stone pedestal on the steps' landing (the golden bone on it), between the two first-floor windows (moved to x 1588 and 1670, both storeys) |
| GALLERY (x 1680, 1816) | a balustrade on nothing | stands on a string course (the fronts' own course, y 287) along the whole red house |
| LOGGIA (x 1416) | an arcade block over a gate and a shop | the portal's entablature: two granite pilasters (`town_pilaster`) to the plinth, the house under it one bay, its gate centred |
| BALCONY x 1328 (first floor) | a railing in front of a window's foot and the cornice | the window above carried down to the slab (`town_window_door`): a balcony door |
| ledges (DORMER, x 2016, 2112, 2416) | thin shelves mid wall | French balconies: the first-floor window carried down, a flush railing (`town_window_rail`), the slab on two corbels (`town_console`, the balcony's corbel) |
| plaza BALCONY x 1552, 1656, 1840, 2420 | cages on quarter-scale doll houses | decision 2a (flag): the big fronts' own ground floor (doors 2.1 m, shops; a plain bay `town_front_tall5` where a door or gate would be behind a balcony), a French window (`town_balcony_door`) behind each |
| every high road piece, every balcony, the awning | no shadow | its own silhouette as a cast shadow on the wall, 2 px right and 3 down (the wall's plaster turns into its own shade) |

Decision 2a is one flag: `arthooks.lua H.PLAZA_FRONTS` (true: the big fronts' ground floor; false: the old plaza
houses). It covers all four plaza houses with a balcony (x 1536, 1644, 1832, 2404), so the street stays one scale.

Folders: `before/` (art/dt-roofs-06nov head 348092f), `after/` (2a on), `after_oldhouses/` (2a off, the plaza spots):
the look sweep at camera y 240, 120 and 0, x 1200 to 2480 every 160, colour and `_grey`. `sheets/compare_*.png`:
before, after, after with the old houses, at 2x. `cards/` (qa_card.py, 5x beside bench, bin, lamp), `qa.json`.

Checks: asset_qa 9 PASS; `--level downtown_tall --physics` 102/102; `--auto` GOOD GIRL; PEPPER UNCHANGED; flow 125/125;
check_tiled PASSED; BACKDROP OK; build_tall_fronts, build_roof_kit, build_dt_street, build_dt_details and
build_highroad `--check` match. Sources: `art/source/dt_highroad/*.aseprite`.

Notes for the reviewer: the pedestal touches the right first-floor window's surround (x 1644 / 1645), the closest the
148 px house allows with 44 px windows; the plaza French windows are mostly behind their railings (their tops sit under
the galleries' string course line, y 295, so all four are one stamp); balcony x 1656 stands right under the gallery.
Old art (town_portal_top, town_oriel, town_oriel_bay, town_front_tall4, town_house1-3) is unchanged and still used when
its replacement file is missing or the flag is off.
