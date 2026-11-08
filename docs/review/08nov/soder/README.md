# Söder Hill, phase 1 (8 Nov 2026): greybox to built art, 0 credits

Branch `lv/08nov-soder`. Everything is built by rule in `tools/build_soder_art.py` (palette `PAL`, written to
`riverwalk/levelart/soder/palette.lua`; swap the provisional colours there when the producer's concept palette is
final) and drawn by `riverwalk/levelart/soder.lua`. Design target: `art/gen/concepts/sh_cafe_concept_a.png`
(reference only, its colours sampled, nothing cut from it).

## Files

| File | What |
| --- | --- |
| `sheet_before.png`, `sheet_before_grey.png` | every screen at camY 0, base `lv/08nov-base` (greybox) |
| `sheet_after.png`, `sheet_after_grey.png` | the same frames on this branch |
| `01_stair_flight_x1176_4x.png` | street to landing to 8 px steps to landing to street, the kerb stepping down |
| `02_hatch_x2320_4x.png` | two open cellar hatches: rim, cellar and step, steel lid against the house |
| `03_sign_bracket_x720_4x.png` | sign on its bracket (wall plates, chains), the raised balcony on corbels with its door |
| `04_tables_parasols_x2700_4x.png` | Downtown's tables and parasols, poles down to the tables, shadows |
| `05_arch_x3400_4x.png` | the arch block on its two piers, plain wall behind |
| `06_balcony_hatches_x3600_4x.png` | the 180 px balcony, two doors onto it, two hatches under it |
| `07_quay_end_x4900_4x.png` | the quay, the cliff wall, Mia's stair, the harbour, the railing |
| `08_terrace_barrels_x1880_4x.png` | a hatch, the terrace with the barrel stack |
| each `*_grey.png` | the same in greyscale (Pepper and every hazard read) |

Frames: `LOOK_SWEEP=1 LOOK_STEP=320 ... love riverwalk --level soder --lookshots`.

## Checks

- `--physics` 29/29 (as base), `--qa` 0 problems (11703 runs), PEPPER UNCHANGED, `check_flow` 139/139,
  `check_tiled` passed, `check_backdrop` OK, `build_soder_art.py --check` OK.
- `asset_qa.py`: balconies, cart, planter, terrace, bollard, railing PASS; the sign, awning and arch sprites PASS on
  their obstacle part (the outline check reads their un-outlined holders as breaks: by design, holders are decoration).
  The ground and back tiles are 512 px cuts of whole terraces: per tile more than 20 colours (several houses or
  materials side by side); per house 14 to 17 colours (the tool checks it). The outline check does not apply to terrain.
- Layer luma (file colours, median / 10th pct): sky 222/187, far city 185/175, harbour 166/166, roofs 177/147,
  houses 121/89, street 101/64. Lightest at the back, the street darkest.

## Open

- Phase 2 pieces (renders) are listed in the track report; the stand-ins here: the flower trough for BIKES, Downtown's
  tables (the concept wants dark wood tops on curly iron legs), the barrels at 14 px (the plan's 20-22 px changes physics).
- The joins kit (`joins.lua`) has no Söder kinds, so its check would pass empty: the module marks its joins, but a
  `Jn.kinds` branch for `def.levelart == "soder"` (street, landing, stair, hatch, quay) is a shared-file change.
