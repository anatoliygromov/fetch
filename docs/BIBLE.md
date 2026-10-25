# FETCH! Bible

The rules everyone follows. Only rules the owner stated or approved, each with its date. A new owner rule goes in the same day. "Playbook" means the "FETCH! Production Playbook" (https://claude.ai/artifact/7jBNJ7deWvc8QkUvA2j47W), approved 23 Oct.

## 1 Pillars

- **Pepper is the star.** A girl, a black Labrador (owner, 5 Oct). Nothing may cover her (owner, 6 Oct).
- **The 1994 Lion King on the Mega Drive is the bar:** layers, graphics, gameplay (owner, 12 Oct). Art "as good as in Lion King", very crisp (owner, 23 Oct).
- **Cute for a 7 year old,** his daughter (owner, 23 Oct).
- **Stockholm,** after the owner's reference photos (owner, 6 Oct).
- **Real fetch logic** that makes sense to a child (owner, 6 Oct).

## 2 Gameplay rules

- Every level ends with a real fetch: pick up the ball, give it to Mia, who waits at the end (owner, 6 Oct).
- Nothing moves by itself. The ball moves only by a throw, gravity or an animal (owner, 6 Oct).
- Obstacles and decoration never look alike. Obstacles: crisp, mid-tone, 1 px dark outline, on Pepper's line. Decoration: no outline (owner, 6 Oct).
- Pepper's files, clips, speeds and physics are frozen (owner, 6 Oct). `tools/check_pepper.sh` must print PEPPER UNCHANGED.
- No music in builds. Sound effects stay (owner, 22 Oct).
- Level order: River Walk, City Park (tall), Downtown (tall), Rooftops, Söder Hill, Night Harbour (owner, 23 Oct).

## 3 Art rules

**The layer rule (owner, 23 Oct).** The layer furthest from Pepper is the lightest. Each nearer layer is darker. Her play line is darkest and most contrasted; the foreground darker still. Distance is one clean palette step per layer, in the level's own haze, done by the game. Full table: `docs/layer_ladder.md`.

| Layer | Scroll x | Scale | Darkest luma | Max contrast | Colours | Outline |
| --- | --- | --- | --- | --- | --- | --- |
| clouds | 0.05 + drift | free | 185 | 70 | 5 | none |
| far city | capped | silhouettes | 145 | 35 | 6-8 | none |
| far shore | 0.25-0.3 | 12-14 px/m | 125 | 60 | 8-12 | none |
| mid | 0.5 | ~23 px/m | 105 | 85 | 10-14 | none |
| water | 0.3-0.55 | - | 75 | 160 | 20 | none |
| back | 1.0 | 46 px/m | 80 | 120 | 20 | none |
| play | 1.0 | 46 px/m | outline | full | 20 / 24 | 1 px dark |
| front | 1.3-1.4 | ~60 px/m | median 40 | 40 | 3-8 | dark silhouette |

Exception: the light pavement under Pepper stays (owner, 23 Oct).

**The crispness bar (owner, 23 Oct).** Buildings are built, not cut. Each window, door, cornice and gable step is drawn once and stamped on an integer grid. Windows on a storey are pixel-identical and evenly spaced. Walls are flat fills. Lone pixels under 2 % for buildings, 5 % for the rest.

**Pixels on a grid (owner, 4 Oct and 23 Oct).** Allowed: a 1:1 cut on the render's own grid, integer block-majority reduction, whole-pixel crop or pad. Never: non-integer or off-grid resampling, box filters, lifted darks, baked fades. Wrong size means regenerate or change the level.

**Outline (owner, 6 Oct and 23 Oct).** Obstacles and characters: unbroken 1 px dark outline. Decoration: none, edges by a darker shade of its own colour.

**Front-on (owner, 12 Oct).** Seen from the front at Pepper's height. A front and a thin cap. No tops, sides or insides.

**Scale to Pepper (owner, 23 Oct).** What she stands on is true scale, 46 px per metre, within her 46 px jump. Big things go on a slower layer.

**No haze in prompts (owner, 23 Oct).** Never "hazy", "pale", "misty" or "faded". Deliver full local colour.

**Approved art is never changed without the owner's yes (owner, 4 Oct and 23 Oct).** No code-drawn characters or titles (owner, 22 Oct).

## 4 The art pipeline (playbook, 23 Oct)

1. **Keys first.** Pepper, bench, lamp, kiosk plus 3 to 5 new key pieces per level set the bar.
2. **Aseprite is the home of every asset.** One .aseprite source per asset in the repo. Claude does the pixel work through an Aseprite MCP server. The owner directs and approves; he never draws.
3. **Generators draft only.** A render is used only if it is on a clean grid and can be cut 1:1. Otherwise it is a reference. **Game pixels come from SpriteCook; Artlist is for mood, concepts and lighting references only (owner, 25 Oct).**
4. **Stamped parts** for architecture and tiles.
5. **One palette per level,** from per-material ramps with neutral darks.
6. **Animation at 1x:** approved still, SpriteCook pixel engine at 1x, then per-frame cleanup.
7. **The enforced gates** before the owner sees anything.

Each level gets an approved golden screen before a credit is spent on its pieces: its **sample screen**, final quality, built from approved pieces (owner, 25 Oct).

**The order of work is `docs/WORKFLOW.md` (owner, 25 Oct):** families of 4 to 6 assets, tiers A/B/C, `tools/pipeline.py` refuses a step without its proof, the owner sees a spend line and the board only.

## 5 UI rules (owner, 23 Oct)

- Cute for a 7 year old, in the Lion King HUD spirit, matching the title.
- Fonts built on a grid: one stroke width, the same colour band per row, 1 px outline, drop shadow. Generated lettering and the default 5x7 font are out.
- One size and one centre line per HUD row.
- Eye check at 4 to 6x on every screen, plus `layout_qa`, before the owner sees it.

## 6 The gates and Definition of Done (playbook, 23 Oct)

1. Brief: what, why, the bar, slot, cost. Approved in batches.
2. Pilot: one piece through all checks.
3. The owner approves the pilot (one fix round).
4. Batch: the rest, matched to the pilot.
5. Independent review by an agent that did not make it.
6. Board: approve, fix or redraw.
7. Merge to main in the weekly build. Frozen and guarded.

Asset gates and checklist: `docs/asset_qa.md`. Nothing is done until it passes its row:

| Area | 10 stars means | Test |
| --- | --- | --- |
| Feel | Pepper answers in one frame; every hit has a tell | check_pepper; RG35XX play |
| Fun | New idea every screen; one set piece per level | Beat sheet; the daughter asks again |
| Kid readability | A 7 year old clears level 1 alone, never stuck 30 s | Watch her play |
| Levels | Par 60 to 90 s; no dead stretch over 5 s; no softlocks | check_curve, autopilot |
| Art | Lion King crispness; light to dark; Pepper reads | QA gates; golden screen |
| UI | One grid font, one centre line, cute | layout_qa; eye check at 4x |
| Juice | Dust, splash, bounce and a sound per action | Checklist |
| Tech | 60 fps on RG35XX, no crash, load under 3 s | Friday handheld build |

- The gates are enforced. `tools/qa_card.py` refuses a card without 5x crops, the colour and greyscale game frame, and the slot check. The reviewer rejects incomplete cards.
- Two failed rounds means change the method or tool.
- At most 3 tracks running and 3 items waiting for the owner. No branch waits over a week. Main is always playable.

## 7 Credits

- Ask the owner before spending any credit (owner, 23 Oct). Credits only on final assets (owner, 23 Oct).
- Pilots only until the brief and pilot pass. Only the art track spends SpriteCook credits (playbook, 23 Oct).
- Log every credit in `art/gen/ledger.csv` with `tools/ledger.py` (preflight writes the plan row; the spent row follows the charge). `tools/ledger.py report` gives yield per tool and family.
- Caps (owner, 25 Oct): 3 paid jobs per asset, 2 retries per family, 500 Artlist and 150 SpriteCook credits a day. Over a cap needs the owner's words.
- A weekly credit audit runs on Sundays. Target: 70 % of credits in the game.

## 8 Where things live and how sessions start

- **The repo is the truth:** `anatoliygromov/fetch`. Not in the repo or on the board means it does not exist (playbook, 23 Oct).
- **`docs/STATUS.md` is the control tower.** The producer session reads it, works and hands over through it.
- **Decisions live on the review board:** https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk, copied into STATUS. Reversible ones go ahead on the default after 48 hours. Credits, scope and merges to main always wait.
- **Sessions start** with the fetch-game-manager skill: BIBLE.md, STATUS.md, WORKFLOW.md, `tools/pipeline.py status`, `tools/ledger.py report`. One producer session at a time; one session per work block.
- **Branches:** one pull request each. Nothing enters `round1` or `main` without the owner's yes (owner, 23 Oct). Push branches, not tags.
- **Tests,** each with its own save folder:

      SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$(mktemp -d) xvfb-run -a love riverwalk --level X --test

- **Before any merge:** `tools/check_pepper.sh`, `tools/check_flow.sh`, `tools/check_tiled.sh`, `python3 tools/check_curve.py --order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night --seeds 10 --out <fresh dir>`, and `python3 -I tools/asset_qa.py` for art. GitHub Actions run the first three on every pull request and on main, and publish a Release (FETCH.love) on every push to main; the tag comes from `VERSION`.
- **Owner cards:** `tools/qa_card.py` refuses a card without an in-game frame (`--frame`) and a slot (`--slot` or asset_qa.SLOTS). A wrong slot fails the card. `--draft` cards are for working only, never for the owner.

## 9 Resolved contradictions

| Older rule | Replaced by |
| --- | --- |
| Compressed architecture (22 Oct) | True scale, tall houses on a mid row (owner, 23 Oct) |
| Cool-grey load-time fade (6 Oct) | One haze per layer in each level's colour (owner, 23 Oct) |
| Downtown facades fade 0.10 on art/haze | 0.25 (owner, 23 Oct) |
| Only Pepper and Mia outlined (5 Oct) | Obstacles outlined, decoration not (owner, 6 Oct) |
| Box-filter downscale (19 Oct pipeline) | Grid only (owner, 23 Oct) |
| One shared 64-colour palette | One palette per level (playbook, 23 Oct) |
| Title by a pixel artist or SpriteCook (22 Oct) | Native grid in Aseprite; artist as fallback (playbook, 23 Oct) |
| Builds in dated Mac folders | GitHub Releases (playbook, 23 Oct) |
| Decisions in docs and chat | The review board (playbook, 23 Oct) |
| 14 project notes at session start | BIBLE and STATUS (playbook, 23 Oct) |
| River Walk as level 3 | River Walk first (owner, 23 Oct) |
| 28 Nov beta fast track | Beta set after the gold level; May 2027 stands (playbook, 23 Oct) |
| Artlist renders cut to game pixels (25 Oct pilot) | SpriteCook for pixels, Artlist references only (owner, 25 Oct) |
| `docs/art_ledger.md` table | `art/gen/ledger.csv` via `tools/ledger.py` (owner, 25 Oct) |
| Assets one at a time | Families of 4 to 6, tiers A/B/C, `docs/WORKFLOW.md` (owner, 25 Oct) |
