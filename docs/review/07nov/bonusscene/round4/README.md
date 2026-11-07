# Bonus round 4: Downtown's square from the rebuilt Downtown (7 Nov)

Branch `day/07nov-bonusdt`, from `day/07nov-integration` (715541c, the Downtown low-row rebuild merged). Only
`riverwalk/bonusscene.lua` changed (`farDowntown`, `midRow`, `buildDowntown`). 0 credits, no new art files.

## What changed

- **The backdrop is the level's new mid row** (`town_facades.png`: big pastel houses at half scale, crow steps, Dutch
  gables and hips, a door in every ground floor), faded and graded as the level's mid layer. The old far roofs and
  spires strip is gone.
- **Ground floors on the square's far kerb** (y 164): every house ends in its ground floor and door on the kerb of
  the square's floor, so the old straight cut of windows over a band is gone. The square's floor (setts, kerb,
  bollards) stays under the back grade. Its bollards are set at x 2, 66, 130, 194 and 258 so none stands in front of
  a door. The lamp post (far left), the street's setts and kerb and the ungraded granite quay wall are as before.
  `downtown_join_4x.png`.
- **The sky and the low skyline stay behind**: Downtown's painted sky and clouds, and its painted low skyline with its
  foot just under the row's cornice, so it shows between and over the gables.

## The storeys

The row's file is three storeys of 64 px (250 px tall). With its ground floors on the kerb, its gables would be off
the top of the screen and the sky hidden; with one upper storey kept, the gables are still cut by the top edge
(`storeys_0_1_2_2x.png`: none kept, one kept, the file as it is). Its two upper storeys are pixel-identical stamped
bands (checked; `tools/build_dt_rooftops.py` stamps them), so the bonus loads the row without them: gables, cornice
and the ground floor, whole pixels, nothing redrawn or scaled, the file untouched. The houses read as one-storey
gabled houses round the square. If the owner wants taller houses, `BS.DT_STOREYS = 1` keeps one storey and the
gables meet the top edge.

## Rooftops

Rooftops falls back to Downtown's scene, so it changed with it (`4_rooftops_*`). Checked: same scene, the ball
reads on the pastel walls.

## Frames

`3_downtown_tall_*` (frame 240, a frisbee in the air) and `4_rooftops_*` (frame 120, a ball): `_before` and `_after`
at 1x, 3x and greyscale 2x, plus `_before_after_2x.png` (before left, after right, colour over greyscale). The rest
of the folder above (`../`) is from `day/07nov-bonusscene` before the integration.

## Checks (final code)

- Bonus tests (`love riverwalk --bonus --physics`): 23 of 23 passed.
- `love riverwalk --bonus` and `--level X --bonus` for riverwalk, citypark_tall, downtown_tall, rooftops, soder and
  night: no Lua errors. Downtown and Rooftops played through by the autopilot with the same results as before
  (C 13 of 14, A 14 of 15).
- `tools/check_flow.sh`: 125 of 125 passed.
- `tools/check_pepper.sh`: PEPPER UNCHANGED (3908 steps identical).

Each run with its own `XDG_DATA_HOME=$(mktemp -d)`, under `xvfb-run -a`, `SDL_AUDIODRIVER=dummy`.
