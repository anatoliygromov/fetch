# Downtown high road attachments (consoles, pilasters, window rails, balcony doors, wall lanterns, cornice awning, footbridge springers and piers, guild house granite floor)

Files: `town_console.png` 8x7, `town_pilaster.png` 14x101, `town_window_rail.png` 44x24, `town_balcony_door.png`
38x52, `town_window_door.png` 52x50, `town_lantern_bracket.png` 18x12, `town_bridge_springer.png` 14x20,
`town_bridge_pier.png` 14x113, `town_guild_steps.png` 122x35, `town_guild_pier.png` 18x46, `town_front_tall6`
(granite ground floor). Branch night/06nov-dt 2852d9c, merged from art/dt-highroad-06nov and the audit.

# Round 1 (reviewer, 6-7 Nov night)

Looked at: every piece at 5x beside bench, bin and lamp; in game at 4x at x 1280-2600, y 120 and y 240.

## Script
console, pilaster, window rail, balcony door, window door, lantern bracket, bridge pier: PASS (`--layer back`).
springer, guild pier, guild steps: "ladder darkest 30" and "decor-ink 100 %" with `--layer back`; they are drawn
with the play ledges' ink on Pepper's line, so run them with `--layer play` and note the hook. No art change.

## Per piece
| Piece | Result | Evidence |
| --- | --- | --- |
| consoles under balconies and ledges | PASS | every balcony and roof ledge at x 1552-2464 now has two consoles into the wall; the base review's "comb ledges on blank plaster" (DT1) are gone: a French window or window door stands behind each ledge (x 1920 y 120 at 2x 380-500; x 2240 at 780-890) |
| pilasters (loggia) | PASS | from the loggia's foot to the ground at both ends of the arcade, so the arcade is the gate's entablature, not a shelf (x 1280 y 240) |
| window rails | PASS | 1 px iron, straight, on the sill, same pixel size as the balcony rails |
| balcony doors / window doors | PASS | six-pane dark French windows behind each plaza balcony, identical across the house |
| wall lanterns | PASS | bracket into the wall, the lamp hangs under it (x 1600 y 120 at 1x 550-570; x 1920 y 120 at 450-470); replaces the street lamp on the gallery (base DT4) |
| awning hung from the cornice (x 2208) | PASS | two 4 px irons from the string course to the awning bar, checked at 8x; it hangs, it does not float |
| footbridge springers and piers | PASS with one fix | granite corbel on a block pier at each foot, piers on the street (x 2480) and on the quay (x 2600); the iron arch with hangers reads at 4x. At 1x the arch rib is a 2 px line and reads as a wire. Fix: rib 3 px (dark, mid, light), hangers 1 px as now |
| guild house granite ground floor, stepped coping | PASS | flat ashlar in 3 shades, stepped coping stamped, the balustrade and iron balconies on consoles beside it |
| guild pier (pedestal on the top step) | FAIL | an 18 x 46 plinth with a dark niche standing on the landing with nothing on it; at 1x it reads as a chimney stub or a tiny door on the wall (x 1600 y 120 and y 0). Fix: put something on it (a stone urn or a 24 px lion, Lion King style) or drop it and let the coping run |

## On the owner's question 2 (granite floor instead of a stepped gable)
Keep the granite ground floor. A gable against the sky at the street tier would put a roof on screen beside
fronts that run off the top, the one scale break the level has just got rid of. The stepped coping reads as a
parapet; it only needs the plinth fix above.

Verdict: PASS for the family except the guild pier (FAIL, fix above) and the bridge rib (thicken).

# Round 2 (reviewer, 6-7 Nov night): after fix round 1 (fab6b50)

| Item | Result | Evidence |
| --- | --- | --- |
| footbridge rib | PASS | 3 px (dark, mid, light) from both springers; reads as an iron arch at 1x (x 2240-2560, y 240 and y 120) |
| guild plinth | PASS | carries a stone urn in 3 shades; reads as an urn on a pedestal on the coping (x 1600 y 120 at 4x) |
| quoins (town_quoin, 10 x 432) | PASS | dressed stone flanks where a front meets a square (x 140, 1180, 2480, 2640, 2816); the seam reads as a house end, not a cut. asset_qa PASS |

Round 1 FAILs on this family are closed.
