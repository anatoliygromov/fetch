# City Park hollow log: Pepper crawls inside (7 Nov)

Owner, 7 Nov: "isnt hollow wood suppose to make the dog climb inside? it looks like shes just crawling on the side".

Before, the log was one picture drawn before Pepper, so she crawled in front of all of it. Now it is two layers and she goes into the dark mouth at the left end, the near bark wall hides her, and she comes out of the mouth at the right end.

## What changed

- `tools/build_cp_hollowlog_layers.py` (new) splits the log into two 44 x 27 files, made from `park_hollowlog.png` (kept unchanged), using its palette, ink and bark pixels. The two cut ends are drawn by rule in the script. No credits, no generator.
  - `riverwalk/art/scene/park_hollowlog_back.png`: the hollow inside. A deep warm dark, darkest behind the near wall, a step lighter in each mouth, and lighter again at each mouth's outer side and on its floor, so the tube reads. Two grain lines on the far inner wall.
  - `riverwalk/art/scene/park_hollowlog_front.png`: the near bark wall, the shell top (with the moss) and the two cut ends. Each end is a ring around a round mouth: ink, a 1 px bark edge, light end grain with a growth ring, and a dark lip. The far (right) end is one step darker, turned away from the light. The mouths are holes in this layer, open from row 6 (world y 307) down to the path, 9 px wide in the middle. That gives 21 px at the crown, taller than her 19 px crawl box.
  - `.aseprite` sources sit next to the old one in `art/source/park_hollowlog/`. `--check` fails if the files on disk differ from what the script builds.
- `riverwalk/scene.lua`: `Sc.drawPieceArt` draws the back layer in the play pass, before Pepper. The new `Sc.drawPieceFront(stage, cam)` draws the front layer after her, in the play layer's look. The front goes after Pepper only while she is crouched under the shell with her sprite over the log. Otherwise it is drawn before her, as before, so nothing covers her when she stands beside the log or on top of it (BIBLE 1, "nothing may cover her"). Being hidden inside the log is the owner's 7 Nov ask. If the two files are missing, the old single file is drawn as before.
- `riverwalk/stage.lua`: one line, `Sc.drawPieceFront(self, cam)`, right after Pepper and the ball she carries. It comes before the bikes, so bikes still ride in front of everything (owner, 25 Oct).
- `riverwalk/setpieces.lua`: the stage is passed on to `Sc.drawPieceArt` (one argument).
- `riverwalk/tests_look.lua`: a frames option, `LOOK_CRAWL="x,x,.."` with `LOOK_CRAWLY`, `LOOK_CAM` and `LOOK_FRAME`, which places Pepper crawling for these frames.
- Collision is unchanged. The map is untouched: the shell top is still solid at y 302 and the crawl gap is still 19 px.
- Pepper is unchanged (no Pepper file touched).

## The gold bone (secret, x 1585)

It lies behind the near wall, the darkest part of the inside. The back layer covers it and so does the front, so it cannot be seen from outside. She takes it when her nose reaches it (her box reaches it at about x 1563, with the super-bone sound and +1000). So it is never shown before she gets to it. The tests check that it is counted as found and taken.

## Frames (tall City Park, camera x 1440, look on, no HUD)

| Frame | Pepper x | 1x | 3x |
| --- | --- | --- | --- |
| approaching | 1528 | `01_approach_1x.png` | `01_approach_3x.png` |
| half inside | 1556 | `02_half_inside_1x.png` | `02_half_inside_3x.png` |
| fully inside | 1585 | `03_inside_1x.png` | `03_inside_3x.png` |
| coming out | 1612 | `04_coming_out_1x.png` | `04_coming_out_3x.png` |

- `before_after.png`: the same four moments on main (left) and on this branch (right), at 3x.
- `03_inside_grey_1x.png` and `03_inside_grey_3x.png`: the inside frame in greyscale. Pepper's body (luma about 58) reads lighter than the inside (35 to 50), and her black outline holds her shape.
- `art_6x.png`: the old file, the back layer, the front layer, and back plus front, at 6x.

Note: her crawl sprite is 59 px long and the log is 44 px, so "fully inside" shows her hindquarters in the left mouth and her head out of the right one, with her middle hidden by the near wall.

## Checks (each run with its own XDG_DATA_HOME, xvfb-run -a, SDL_AUDIODRIVER=dummy)

- `love riverwalk --level citypark_tall --test`: the screenshot tour ran through, exit 0
- `love riverwalk --level citypark --physics` (tests_citypark): 85 of 85 passed, including "hollow log: stops a walk", "a held jump lands on top", "crawl through it" (x 1635) and "secret: HOLLOW LOG counted (gold bone inside)"
- `love riverwalk --level citypark_tall --physics`: 97 of 97 passed
- `--qa`: citypark_tall 12761 runs, 0 problems; citypark 7862 runs, 0 problems
- `tools/check_flow.sh`: 125 of 125 passed
- `tools/check_pepper.sh`: PEPPER UNCHANGED (3908 steps identical)
- `python3 -I tools/asset_qa.py --file ... --layer play --level cp`: both layers PASS (the front's outline is complete, including a dark lip around each mouth)
- `python3 -I tools/build_cp_hollowlog_layers.py --check`: OK

## Levers (each a single yes)

1. A longer log (for example 60 px, a map change) would hide all of her middle and give a longer "inside" moment.
2. Brighter end grain on the far (right) end, to match the left end.
3. A wider mouth (11 px) with thinner rings, so more of her shows at each end.
