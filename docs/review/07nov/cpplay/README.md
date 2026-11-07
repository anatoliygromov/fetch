# City Park playground: the climbing frame and the front bush (7 Nov 2026, branch day/07nov-cpplay)

0 credits. No image service called. Both pieces built by rule in a script with `--check`.

## What the owner said (FETCH! Art Review, 7 Nov)
- park_frame_06n: redraw, "looks really weird".
- park_bush_06n: redraw (no comment).
- Kept as they are (approved): the play tower, rope bridges, arbour, winch keeper, hedge, trimmed hedge, leaves, hollow log.

## 1. The climbing frame (riverwalk/art/scene/park_frame.png, 90 x 67)

**What it is in the game.** The boxes did not move. In citypark_tall (the flat City Park has the same boxes 144 px higher):
- STEP 2716-2732, top 316, 12 px, solid, hidden (this image draws it): the hop up from the path.
- FRAME 2712-2784, top 304, one-way: the low deck, 12 px over the step.
- the top deck 2724-2800, top 280, one-way: 24 px over the low deck. The magpie's perch 11 sits on it (beat sheet: "the frame's top bar").
- two decoration boxes 2712-2716 and 2796-2800 (posts, not drawn by the game).

**What was wrong.** Blue pipes in a different family from the approved tower beside it: two tall posts, two stacked bars, a short ladder and a yellow stool on legs. It read as a cage, a gate or a bunk bed. A dog cannot use a ladder. History in `frames/frame_history_4x.png` (22 Oct greybox, 22 Oct with the rungs, 6 Nov audit, now). None of the old versions was better: all are the same pipe cage.

**What I built.** `tools/build_cp_frame.py` (`--check`). A little play house in the approved play tower's own build, so the playground reads as one set:
- every surface Pepper stands on is the tower's yellow deck (`tower_deck` from tools/build_cp_built.py: lit cap, flat front, shade row, bolts, 1 px ink), drawn exactly on its box;
- every deck stands on the tower's grey posts (`tower_post`): the low deck on two posts to the path (the left one on the 2712 decoration box), the top deck on a short post standing on the low deck (the tower's own rule for an upper deck) and a tall one on the 2796 decoration box down to the path;
- the step is a yellow tread on a red box: a step, not a stool;
- between the two decks, the slide tower's red panel with its round window, the window cut 1:1 from the approved park_slide.png. One window: two read as a face. Under the low deck it stays open, as Pepper walks the path under it.

9 colours, all from the tower and the slide. Nothing floats, no free bar ends, no thin bars. The open version without the panel (`--variant open`, in `frames/frame_rejected_open_variant_5x.png`) read as a table and a bench, so I did not use it.

`tools/build_cp_built.py` now takes the frame from the new script. I ran it: every other piece it builds came out byte for byte the same.

Frames (3x, colour on top, greyscale below, before left, after right):
- `frames/frame_x2560_before_after_3x.png`: Pepper on the top deck.
- `frames/frame_x2600_pepper_low_deck_before_after_3x.png`: Pepper on the low deck, in front of the red panel.
- `frames/frame_flat_citypark_x2560.png`: the flat City Park, the same art on its own boxes.

## 2. The front bush (riverwalk/art/scene/park_bush.png, 75 x 34)

**Where it shows.** The two front-layer props of the City Parks (citypark_tall x 620 and 1900, top y 365; scene.lua `Sc.drawPropArt`, `T.bush`), scrolled 1.4x. Only its top 19 rows are on screen, at the bottom edge, on the dark earth band. Pepper's feet are at 328 or higher, so it never covers her. Its top is now 2 rows lower than the old twigs.

**What was wrong.** A painted lump re-shaded twice on 6 Nov (fix_cp_bush.py, then fix_cp_audit.py): twigs and spikes sticking up, one flat mass, and a rim of orange dots that read as specks on the 6 Nov card. History in `frames/bush_history_6x.png` (22 Oct painted, 6 Nov re-shaded, 6 Nov rimmed, now). The 22 Oct one is noisy; the two 6 Nov ones keep the twigs. None was better.

**What I built.** `tools/build_cp_bush.py` (`--check`). A round leafy mound of seven leaf clumps. Two clumps are drawn once (radius 11 and 8: a core disc with round leaves every 45 degrees, so the edge is scalloped by whole leaves, not noise) and stamped back to front on an integer grid, the outer ones lowest. Three colours: the City Park front band's own dark and rim (look.lua), and one clump-edge colour half way from its mid to its rim. The back-lit rim runs along the top edge; a thin lighter line marks a clump's upper edge where it lies over the clump behind. No outline (decoration). (The band's own mid was too close to the dark: asset_qa flagged those edge lines as blotches.)

Frames: `frames/bush_x0460_before_after_3x.png`, `frames/bush_x1740_before_after_3x.png` (look at the bottom edge).

## Cards and checks
| Check | Result |
| --- | --- |
| asset_qa park_frame (play, cp) | PASS: 9 colours, outline 100 %, lone 0.3 % (`cards/PASS_park_frame.png`) |
| asset_qa park_bush (front, cp) | PASS: 3 colours, on screen median 20, lone 0.4 %, blotches 0 (`cards/PASS_park_bush.png`, slot passed as `--slot park_bush=75x34`; it is not in asset_qa.SLOTS) |
| build_cp_frame.py / build_cp_bush.py --check | OK / OK |
| check_pepper.sh | PEPPER UNCHANGED (3908 steps identical) |
| citypark_tall --physics | 97 of 97, the same as origin/main (97 of 97) |
| check_flow.sh | 125 of 125 |
| check_tiled.sh | passed (no map touched) |

The cards' in-game frames: `frames/frame_ingame_x2560.png`, `frames/bush_ingame_x0460.png`.

## Open questions
1. The play house reads as a stepped climbing block in the tower's colours. If the owner would rather have a timber balance beam or a bridge, the boxes allow it, but a top deck 24 px over a low deck that overlaps it by 60 px will always look like two storeys.
2. The bush is now a calm dark mound with no warm rim pixels. If the owner wants it to catch more light, the next lever is a warm rim on the two top clumps only, as one rule.
3. The old fix scripts (tools/fix_cp_bush.py, the bush part of tools/fix_cp_audit.py) are superseded. They would overwrite the new bush if run again. Should they be removed?
