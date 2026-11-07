# GROUND track, round 3 (7 Nov): the kennel only

Review: `review/07nov-ground` 40f01ef, rw_kennel.md Round 2. The float was fixed, but the 32 px flat lid on a 38-row
wall read as a red chest or crate.

## What changed (tools/build_rw_kennel.py, --check)

- A 20 px ridge board (x 12-31, 2 rows) on a low 1 in 4 pitch: one row down every 4 px, 3 rows to the eaves.
- The eaves 2 px past the walls (walls x 2-41).
- The roof 6 rows deep at every column, so it reads as a thin low gable.
- The walls back to 30 rows at the corners. The art is 44 x 40 (was 44 x 44), top at y 144, bottom row y 183.
- The door crown stays at y 165, so the crawl, the gold bone and the start are unchanged. The ridge box is x 16-28
  from y 144 (was 140), the eaves box x 0-44 from y 148 (was 145).
- asset_qa PASS, 11 colours. Card: `PASS_kennel.png`.

## Paw gaps, measured on the frames (`kennel_paw_gaps.txt`, `kennel_pepper_x16_22_30_5x.png`)

| Pepper at | Hind paws | Front paws |
| --- | --- | --- |
| x 16 | cols 6-9: 3, 3, 2, 2 px (on the first slope step) | cols 27-31: 0 px (on the board) |
| x 22 | cols 12-15: 0 px | cols 33-37: 2, 2, 2, 3, 3 px |
| x 30 | cols 20-23: 0 px | cols 41-43: 4 px; 44-45 past the kennel's edge |

The expected figures were about 2 px under the heel and 1 px under the paw. Measured: 2-3 px where a paw is on the
first slope step, 4 px at the eave when she stands at x 30. On the board itself it is 0.

## For the owner to choose

`kennel_choice_round1_gable_round2_lid_round3_lowgable_3x.png`: the three kennels in the garden at 3x, colour over
greyscale. `kennel_files_8x_round1_round2_round3.png`: the three files at 8x.

1. Round 1, a classic gable: Pepper's paws float 5-9 px over the slopes on the peak.
2. Round 2, a flat ridge board: 0 px under her paws, but it reads as a chest.
3. Round 3, a low gable (now in the game): 0-3 px under her paws, 4 px at the eave.

## Checks

PEPPER UNCHANGED; riverwalk --physics 56/56 (kennel stops a walk, crawl in for the gold bone, crawl out: PASS);
check_flow 125/125; TILED CHECK PASSED (the map re-exported for the boxes).
