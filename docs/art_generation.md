# Generating art with Artlist (25 Oct 2026)

Gate 2 ("Make") for characters, animals, props and vehicles made with a model. Buildings, facades, fonts and UI are
BUILT (docs/asset_qa.md), never generated; the scripts below refuse them. Rules live in `art/gen/rules.json`; change
them there.

## Why (the 25 Oct pilot)
3,360 credits, 3 usable pieces: the model ignored a grey target box and drew subjects 1.15x to 2.7x too big (the
cyclist read as a child), copied whole scenes from a full game screen used as style, and the render was shrunk by an
uneven factor with averaging (the batch 1 defect). The steps below make each of those fail before a credit is spent.

## Steps
1. **Job** `art/gen/jobs/NAME.json`: level, layer (char, play, back, mid, front), kind, real height in metres, target
   size in px (= real height x the layer's px per metre), 2-4 check measures, subject, part map, a size sentence
   relative to the dog, model (default Nano Banana Pro 1K), variants.
2. **Blockout** `art/gen/blockouts/NAME.py` (uses `tools/blockout_lib.py`): a 150 x 112 frame on flat magenta,
   Pepper's real sprite at 1x, grey shapes for every part at true scale (worn and carried things included), and the
   subject mask. 150 x 112 divides the 1K output (1200 x 896) into exact 8 px cells.
3. **Preflight** `python3 tools/preflight.py art/gen/jobs/NAME.json ...`: refuses the job unless the layer scale,
   the whole-pixel frame, Pepper at 1x, the mask size, the style card and the job's words all hold. On a pass it writes
   the prompt (art-direction block, the level's light, the layer's outline and colour cap added by the script) to
   `art/gen/prompts/NAME.txt`, the upload images to `art/gen/upload/`, and one line with the credits. That line is
   all the owner needs: yes or no.
4. **Generate** with exactly that prompt and those two inputs (blockout, then the style card
   `art/gen/style_card_riverwalk.png`, approved sprites only, no lettered pieces; `tools/make_style_card.py`).
5. **Cut** `python3 tools/grid_cut.py RENDER NAME`: one colour per 8 x 8 cell (majority, else centre; never an
   average), magenta keyed, Pepper and stray scenery dropped, compared with the mask (size within 8 %, 85 % of the
   drawing on the blockout, 80 % of the blockout drawn, under 3 % strays, 70 % of cells with one clear colour).
6. **Gates 3-7** as in docs/asset_qa.md: `cleanpass.py`, `outline_complete.py --skip-bottom`, `asset_qa.py`,
   an in-game frame (`LOOK_SPOTS=x,y LOOK_BIKE=dx` with the file in place, `--lookshots`), `qa_card.py` with
   `--frame` and `--slot`, an independent review, then the Art Review board.

## First piece through it
`rw_cyclist_adult_v0`: the owner's pick from the first run (Nano Banana Pro 1K, made on the older 168 x 126 blockout,
cut on its own detected grid with `--pitch auto`, 90 % clean cells), clean pass and outline: asset_qa PASS 84 x 85,
20 colours, card in `art/gen/out/cards/`. New jobs use the 150 x 112 frame (`rw_cyclist_adult` passes preflight).
