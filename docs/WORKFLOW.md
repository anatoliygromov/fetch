# FETCH! workflow (owner, 25 Oct 2026)

How every session works, for assets and for levels. The rules are in `docs/BIBLE.md`; this file is the order of work.
Why it exists: the 3-25 Oct audit (`art/gen/ledger.csv`, `python3 tools/ledger.py report`): 76 % of Artlist and about
43 % of SpriteCook credits were wasted, mostly by making assets before the target was fixed, using a painting model
for game pixels, and repeating known mistakes. The owner wants to trust the work and look only at finished results.

## The owner touches the work twice
1. **The spend line** at preflight: "Family X, N assets, C credits, rulebook check passed. Go?" Yes or no.
2. **The Art Review board** (https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk): one card per family or level.
   Approve, fix or reject per item. Nothing reaches him anywhere else.

## Session start and end (fetch-game-manager skill)
- **Start:** read `docs/BIBLE.md`, `docs/STATUS.md`, `docs/WORKFLOW.md`; run `python3 tools/pipeline.py status` and
  `python3 tools/ledger.py report --since <last Monday>`; read the board decisions. Then one message: where we are,
  the plan for this session, its credit cap. Wait for go.
- **During:** one producer session at a time. Builders in parallel only on independent tracks, each in its own git
  worktree, at most 3.
- **End:** update `docs/STATUS.md` (what changed, what waits for the owner, credits today), push the branches, put a
  playable build in `2d game test/<date>` on the Mac when there is one. The next session starts from STATUS, never from
  chat memory. One session per work block.

## Assets (fetch-art-director skill)
The unit is a **family**: 4 to 6 assets of one layer and one scale (street furniture, people and bikes, trees).

**Tiers** (art/gen/rules.json): **A** stars (Pepper, Mia, hazards and obstacles on her line, title): full pipeline,
polish and review always. **B** scenery behind her and the mid layer: family sheet, shared review, polish only flagged
items. **C** far layers, sky, ground, anything repeated or geometric: built in code or from stamped parts, never
generated.

**Tools:** SpriteCook makes game pixels (exact size, pixel on) and animation from a finished 1x still. Artlist is for
mood, concepts and lighting references only, never game pixels (owner, 25 Oct). Aseprite holds every source and does
the polish. Buildings, fonts and UI are built on the grid.

**Before the first family of a level:** the level's layer plan, its locked palette (`tools/make_palette.py LEVEL`,
`art/palettes/`) and its **sample screen**: one screen brought to final quality with the approved pieces. The owner
approves the sample screen once; every later asset is judged by "does it sit in that screen?".

| # | Step | Command | Proof (pipeline.py refuses without it) |
|---|---|---|---|
| 1 | Spec card per asset from the layer plan: layer, real size, px, check measures, tier, family, slot | `pipeline.py new NAME`, `done NAME spec` | `art/gen/jobs/NAME.json` |
| 2 | Blockout: Pepper at 1x, grey parts at true scale incl. hats and bags | `art/gen/blockouts/NAME.py` | png + mask |
| 3 | Preflight, then the spend line to the owner | `preflight.py art/gen/jobs/*.json` | pass, ledger plan row, within caps |
| 4 | One probe for the family; max 2 retries, each changes one named input | the tool, then `ledger.py spent JOB N` | render + ledger spent row |
| 5 | Cut on the grid, snap to the level palette, clean pass, checks | `grid_cut.py`, `cleanpass.py`, `asset_qa.py` | cut json with no fails |
| 6 | In-game frame beside bench, bin, lamp, 1x and 3x, colour and grey | `LOOK_SPOTS=… --lookshots` | frame newer than the cut |
| 7 | Polish in Aseprite within a fixed budget; over budget is a reject | Aseprite MCP | .aseprite newer than the cut |
| 8 | Independent review, 9 items (rules.json), one reviewer call per family | Agent, cheaper model | `art/gen/reviews/NAME.md` all PASS |
| 9 | Board card per family | `qa_card.py` | the owner's approve |
| 10 | Wire in on a branch; reject gets one line of cause plus a new rule or check in the same session | `pipeline.py done NAME shipped` | slot file in the game, ledger in_game |

**Caps** (rules.json): 3 paid jobs per asset, 2 retries per family, 500 Artlist and 150 SpriteCook credits a day.
Over a cap needs the owner's words (`preflight.py --owner-ok "…"`). Stop and report instead of trying again.

**A script PASS is never "ready".** Steps 6 to 8 are eyes: mine at 5x, then a reviewer who did not make it.

## Levels (fetch-level-quality skill)
1. Layer plan and beat sheet (`docs/*_beatsheet.md`, the Layer Plans doc). 2. Greybox in Tiled/level files.
3. Checks: `check_pepper.sh` (PEPPER UNCHANGED), `check_flow.sh`, `check_tiled.sh`, `check_curve.py` on the level
order. 4. Playtest lab bots. 5. Independent review (a fresh agent with BIBLE and the level, not the maker's notes).
6. Board card with a playable build on the Mac. Art for a level starts only after its layer plan is approved.

## Learning loop
- Every rejection: one line in `docs/art_learnings.md` (what the owner saw, the cause, the check). A cause seen
  before becomes code in preflight, grid_cut or asset_qa in the same session.
- Every Sunday: the scheduled credit audit (yield per tool and family, target 70 % of credits in the game). Two weeks
  under target: change the method, not the prompt.
