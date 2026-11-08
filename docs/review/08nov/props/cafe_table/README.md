# Söder cafe table and parasol (pilot, 8 Nov, family sh_props_08nov)

Söder Hill section 9, camera x 2560-2880, Pepper's line (play, 46 px a metre). Two sprites so the existing layout keeps
working, both drawn by `riverwalk/levelart/soder.lua` (TABLE, PARASOL):

| File | Size | Drawn at | Box (riverwalk/level/soder.lua, unchanged) | asset_qa | Card |
| --- | --- | --- | --- | --- | --- |
| `riverwalk/levelart/soder/props/parasol.png` | 66 x 43 | x0 - 1, y0 - 1 | PARASOL oneway 64 x 4 at y 108 (x 2692, 2772) | PASS, 11 colours | `PASS_parasol.png` |
| `riverwalk/levelart/soder/props/table.png` | 50 x 26 | x0 - 1, y0 | TABLE solid 48 x 7 at y 150 (x 2700, 2780) | PASS, 7 colours | `PASS_table.png` |

- Parasol: the canopy's top row is the 1 px ink on y 107, flat over the whole 64 px box (Pepper stands on y 108); 8
  red and cream panels whose seams fan out from the pole, a dark hem, a scalloped valance; the pole (4 px with its ink,
  x 2722-2725, the old pole decor box) from the canopy to the table top, a collar under the canopy. The code-drawn pole is
  no longer drawn when the file is there.
- Table: a walnut top seen side-on on the box (lit top row, two grain lines, the thick rim turning under, the low sun
  on the right end), a column with a knob and two curly iron legs to the street (y 175), 19 px to crawl under as before.
- Light from the right (Söder, low evening sun). Obstacle outline: 1 px Söder ink (1c1718) all round both.
- asset_qa has no Söder look, so it ran as `--level dt --fade 0` (these props are drawn unfaded on the play line).

## How it was made (credits 88: 64 + 12 + 12)
1. Try 1, `sh_cafe_table` (GPT 2.5 Sunburst 1K, edit = the 256 blockout with Pepper at 1x, style = the River Walk
   style card with the bench, bin and lamp + the concept crop; 2 variants, 64 credits, job a2fdb1b8). Pepper stayed 1:1,
   but the parasol came back 109 and 119 px wide for 66 (1.65x, 1.8x) and domed, the table 64 and 75 px for 50. Fail.
2. Try 2, `sh_parasol` and `sh_table` (Pixel Engine Image at exactly 66 x 43 and 50 x 26, 12 + 12 credits, jobs
   ffc652ee and f0b6f96d). The canopy domed again (it cannot stand on a flat 64 px platform) and the table top was
   12 rows thick, seen from above. Fail.
3. Method change (brief: after two fails change the method): BUILT by rule, `tools/build_sh_props.py`, colours from the
   concept (canopy red and cream, walnut) and Söder's ink and iron. The legs were first the Pixel Engine table's legs
   cut 1:1; at 4x beside the bench they read thin and gappy, so they are hand-placed too. All renders in `raw/` as
   the design references. No SpriteCook pixel is in the game.

Design call to check: the concept's parasol is a dome with a finial; the box is a flat 64 px platform, so the canopy
has a flat top and suggests the dome only by the fanned seams.

## Review folder
- `raw/`: every SpriteCook output (GPT raw 1024 and its 4 px grid cut, the Pixel Engine 1x outputs)
- `parasol.png`, `table.png`: the 1x files
- `x5_beside_bench_bin_lamp.png`: both at 5x beside the approved bench, bin and lamp
- `frame_x2600*.png`, `frame_x2680*.png`: in game, look on, 1x and 4x, colour and greyscale
- `PASS_parasol.png`, `PASS_table.png`: the qa cards (tools/qa_card.py)
- Rebuild: `python3 -I tools/build_sh_props.py && python3 -I tools/review_props_08nov.py cafe_table soder 2600,2680 riverwalk/levelart/soder/props/parasol.png=66x43 riverwalk/levelart/soder/props/table.png=50x26`

## Checks
PEPPER UNCHANGED (3908), physics Söder 29/29, Night 40/40, `--qa` Söder 11703 runs 0 problems, Night 8037 runs 0
problems, flow 139/139.

## Gate 6, independent review: PENDING
This session had no Agent tool, so no fresh reviewer could be started from it. The maker's own pass of the checklist
(not a gate 6 verdict): repeated parts equal (8 panels of 8 px, scallops identical, the legs mirrored); one light
direction (right); 1 px ink all round, one ink; scale: table top at Pepper's back height (26 px), canopy 66 px; fits
its boxes exactly; as clean as the bench at 5x. To do by the producer: a fresh agent with only the cards, the code path
(`riverwalk/levelart/soder.lua` TABLE / PARASOL, `riverwalk/level/soder.lua` section 9) and the slots above.
