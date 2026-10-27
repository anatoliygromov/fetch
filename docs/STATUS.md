# FETCH! Status

As of Sun 25 Oct 2026, night (23:43). Rules: `docs/BIBLE.md`. Decisions: the review board, https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk.

## Owner's go, 26 Oct evening (live)

Picks given on "Ok gå" to my recommendations. 0 credits, no image service call, nothing merged into main. Picks are recorded here, not on the board.

**Yes (code only, built):** both plans' haze re-tune; City Park sky (4), leaf front (5), small fixes 8 a to f; Downtown small fixes 6 a to d.
**Picked, not built (new art, needs a credits yes for a brief):** City Park trunks at true width (1), mid trees b (2), duck boat 120 px (7), screen 9 kept (9), Downtown first floor a (1), shelter and gateways at true scale a (4). Held: City Park 6, Downtown 5.
**Screen 12 river view:** B (gable door bay only, 116 px). Not built.

**Merged (owner's yes, 27 Oct):** `prod/integrate-c` (29aec89) = `prod/integrate-b` + `night/26oct-cp-code` + `night/26oct-dt-code`. Only conflicts: CHANGELOG (kept both) and `tools/layer_wireframe_tall.py` (the Downtown copy is a superset). Checks on the merge: PEPPER UNCHANGED, flow 125/125, Tiled PASS, QA 0 problems on all six levels, physics City Park 97/97 and Downtown 102/102, curve T1-T4 PASS (10 seeds). check_backdrop: 1 piece, the known River Walk gable. Not in `main`.

**Branches** (off `prod/integrate-b` 0be7994; checks green or equal to base: PEPPER UNCHANGED, flow 125/125, Tiled PASS, QA 0, curve T1-T4 PASS)
- `night/26oct-cp-code` (c5850e7): luma far city 169 to 191, tree line 166 to 181, mid 164 to 154; sky 158 to 202; leaf front; fixes 8 a (legs), b, c (ledge drawn as branch, Pepper stands on it), d (lamp 976 to x 1028), e, f. Skipped 8a gate and 8g leaf piles: outlines are baked into approved art. Caveat: sky 202 is close to the clouds' darkest 10 % (201). Notes: `docs/review/26oct-night/cp/README.md`.
- `night/26oct-dt-code` (834ec4d): luma far city 163 to 187, roofs 171 to 176, old town 180 to 169; spire from screen 1; railings 46 px; four more front pieces; loggia and galleries a draw-time tint (art untouched). Downtown sky not done. Notes: `docs/review/26oct-night/dt/README.md`.

---

## Night of 26 Oct, second run (21:00 Stockholm, no work)

0 credits, no image service call, nothing merged. `ops/night-26oct` already belongs to the earlier run today, so this run used `ops/night-26oct-b` (same base, b2a10c6). Board read at 21:05: newest decision is still 25 Oct 19:18, so no approved work is waiting; every open item needs the owner or credits (redraws). The audit ran at 19:49 UTC on `prod/integrate` (c1c37a4) and no branch has moved since, so I did not repeat it. No new tracks.

**Look at:** `docs/review/26oct-night/audit.md` on `night/26oct-audit`.

**Waiting for the owner:** the three questions of 25 Oct night, unchanged. `prod/integrate-b` (0be7994) now exists from an earlier run; it is not merged anywhere.

**Problems:** two routines still fire the same night. Suggest turning one off.

**Next run, if he says nothing:** the same, nothing new.

---

## Night of 26 Oct (unattended run, 20:40 to 21:00 Stockholm)

0 credits, no image service call, nothing merged. Base: `ops/night-25oct` STATUS. Board read at 20:42: no decision after the 25 Oct 20:18 ones, so no approved art work was waiting. All three 25 Oct questions are still open, so I built nothing new and audited.

**Branch** `night/26oct-audit`, off `prod/integrate` c1c37a4: `docs/review/26oct-night/audit.md`. PEPPER UNCHANGED, flow 125/125, Tiled PASS, QA 0 problems on all six levels, curve T1-T4 PASS at 10 seeds. Only fail: `check_backdrop.py`, 3 pieces (building, tree, tree_near), known, fixed by `art/rw-sample-screen`.

**Look at:** `docs/review/26oct-night/audit.md`.

**Waiting for the owner:** the three questions of 25 Oct night are unchanged (prod/integrate-b merge, gable and cafe river view pick, City Park and Downtown plan decisions).

**Problems:** `tools/check_tiled.sh` has no execute bit. apt numpy is broken here; a pip venv fixes it. The older routine may still run twice a night.

**Next run, if he says nothing:** audit again, nothing new.

---

## Night of 25 Oct (unattended run, 20:28 to 23:43 Stockholm)

0 credits, no image service call, nothing merged, nothing posted to the board or to the Layer Plans doc. Base read at 20:30: `preview/25oct-pm` f54a219 (this branch is cut from it); the evening session's newer STATUS (`preview/25oct-late` 6c82a8b, 21:31) is kept below this section. Board at 20:16-20:18: approve cloud8_v2, park_log_v2, pier_v2, skyline_v2, rw_home, rw_lime, rw_rail_bg; redraw gull_v3 and cat_v2 (done since as `art/animals-r2`). No board decision after 20:18.

**Branches** (off `art/rw-sample-screen` 80ec97f, approved tonight, or `prod/integrate` c1c37a4; all checks green)
1. `night/25oct-rw-street` (a8f1461), off 80ec97f. "Known, next": the gable and the cafe at true scale on screen 12, built from stamped parts like HOME (tier C, 0 credits). `rw_gable` 148 x 180, `rw_cafe` 124 x 180, 20 colours each, 0 lone pixels, tops at y -6; palette riverwalk.gpl v3 (109 colours). Independent review: round 1 FAIL on small located defects, fixed; round 2 PASS 9/9 on both. Pipeline: both at review, next the board. As built, screen 12 keeps 48 px of river view; the layer plan asked for the left half (160 px): options sheet on the branch.
   `night/25oct-rw-street-late` (7f1adc8): the same pieces on the 4096 px River Walk of `art/animals-r2`. Merge this one if `art/animals-r2` goes in, the first if not.
2. `night/25oct-fixes` (f3bf4c0), off 80ec97f. S2 from "Known, next": the quay railings stopped 7 and 69 px short (water showed before the gable), now they reach their props, posts at least 48 px apart (physics test 20). `layout_qa8.py` no longer crashes on the v8 pause (ALL PASS, 169 checks). `check_backdrop.py` measures every column as drawn and lists rw_home and rw_lime (it now fails the old gable alone, correctly). Reviewed, 4 findings fixed.
3. `night/25oct-prep` (654151a), off c1c37a4. Lamp post and rowing boat scale sheet (a lamp of 4 m or more hides its checkpoint light above the screen; 3 m keeps it); `preflight.py` takes the owner's picked size for animals (`owner_size`; `art/animals-r2` had to set the cat's real height to 0.65 m to pass). Reviewed.
4. `night/25oct-cp-plan` (fa7fd12), off c1c37a4. The City Park (tall) layer plan in the River Walk tab's form, the Layer Plans doc's "Next": `docs/layer_plans/citypark_tall.md` with a wireframe and colour and grey sweeps of every screen. Findings: the same 87 px crowns used at two depths, treetop trunks 8 px (true 18-37), keepers 57-64 px (adults need 81), the duck boat 54 px (needs 120), three street lamps in the treetops, both roads in one frame put screens 3-9 at 4-10 usable pieces, far layers out of order (169, 166, 164). 10 decisions at its top. An independent fact-check confirmed the key numbers; its five corrections are in. Not copied into the Layer Plans doc.
   `night/25oct-dt-plan` (f4117ff), stacked on the City Park plan (its tools): the Downtown (tall) plan, `docs/layer_plans/downtown_tall.md`, the doc's other "Next". Findings: the high road is 3.1 to 4.2 m up, a first floor, while the houses behind stop at 2.7 to 4.0 m with roofs on top, so 11 of 12 house tops show; three house scales on one street (doors 93, 58 and 25 px); far layers darkest at the back (163, 171, 180); on the circled plaza screen the statue, crates and awning sit only 4 to 35 luma off the fronts behind them; the shelter is 1.04 m as drawn (real 2.5 m). 6 decisions at its top.
5. `night/25oct-lab` (d9fe696), off c1c37a4. S2: curve T4 failed at 20 seeds (City Park tall, 9.4 % lost runs, the same on main). Cause: the playtest bot's 32 px run-up walked Pepper off the ash branch's end, then off the ledge below, every retry. The run-up now stops at the floor's edge (lab only; game untouched). 20 seeds: T1-T4 PASS, City Park lost 0.6 %, parents DI 26.4 -> 18.9, River Walk identical; later levels move slightly through the carried lives and score. Test `tools/check_lab_runup.py`. Reviewed. 10 seeds: T1-T4 PASS, City Park lost 3.8 % -> 1.2 %.

**Trials (local only, not pushed).** `prod/integrate` + `art/rw-sample-screen` + `art/rw-fixes` + `night/25oct-fixes` + `night/25oct-rw-street`: only CHANGELOG conflicts (keep both sections); every check green, curve T1-T4 PASS (10 seeds) with DI as on the base. `preview/25oct-late` + `night/25oct-fixes` + `night/25oct-rw-street-late`: merges clean, every check green, curve as on its base.

**Look at**
- `docs/review/25oct-night/rw_street/screen12_river_view_options_3x.png`, `rw_screen12_before_after_3x.png`, `cards/` (`night/25oct-rw-street`).
- `docs/layer_plans/citypark_tall.md` and `citypark_tall/wireframe.png` (`night/25oct-cp-plan`); `docs/layer_plans/downtown_tall.md` and `downtown_tall/contact.png` (`night/25oct-dt-plan`).
- `docs/review/25oct-night/fixes/railing_promenadeB_end_before_after_3x.png` (`night/25oct-fixes`); `docs/review/25oct-night/prep/rw_scale_calls_2x.png` (`night/25oct-prep`).

**Waiting for the owner (new tonight)**
1. Merge into a new `prod/integrate-b`: `art/rw-sample-screen`, `art/rw-fixes`, `night/25oct-fixes`, `night/25oct-prep`, `night/25oct-lab`? (yes or no). The railing fix changes how the approved railing is put together at its ends, not its pixels; the lab fix changes the curve's numbers (above).
2. Board: rw_gable and rw_cafe, and screen 12's river view: A as built (48 px), B the gable's door bay only (116 px), C the cafe alone (196 px). Pick.
3. The City Park and Downtown layer plans: their decisions (10 and 6, at the top of each)? Yes, or strike any.
Still open from before: "Animals round 2" on the board; play `_g`, then v0.7; logo and tagline; lamp post height (sheet ready).

**Problems**
- Four night runs started tonight from two enabled routines (20:00 "FETCH! night manager", older prompt; 21:01 "Fetch Night Manager", tonight's prompt, also run by hand at 20:29). The extra runs left `ops/night-25oct-b`, `ops/night-25oct-c` and `night/25oct-tools` (a duplicate layout_qa8 fix): drop them. Suggest turning the 20:00 routine off.
- At 20:41 I stopped every running game process by mistake; the art agent re-ran its checks.
- The FETCH! project docs are not reachable from a cloud session: tonight's facts are here, in `docs/art_learnings.md`, the prep README and the CHANGELOG sections.
- `apt-get install love` fails in its man-page step; LÖVE 11.5 works. No matplotlib: the curve chart is skipped, numbers unaffected.

**Next run, if he says nothing:** no merges, no new plans (both "Next" plans are done): an audit of every check on `prod/integrate`, and the gable and cafe river view built as he picks.

---

## Today (25 Oct, afternoon and evening)

Three branches, each off `prod/integrate` c1c37a4, all checks green; together on `preview/25oct-pm` (build on the Mac: `2d game test/PREVIEW 25 Oct pm/FETCH_PREVIEW_25oct_pm.love`).
- `art/rw-sample-screen` (80ec97f): River Walk sample screen, screen 1: true-scale house (built, 0 credits), street lime (SpriteCook 48), quay railing 50 px. Palette riverwalk.gpl v2 (86). Board: family "River Walk sample screen".
- `art/rw-fixes` (64adc24): cloud8, park_log, pier, skyline fixed pixel by pixel (0 credits; every pixel in art/source/rw_fixes/edits.json). The gull left for a redraw (owner 16:00). Board: family "River Walk fixes by hand".
- `art/animals` (a640156): gull and cat redrawn (owner: "holes, doesnt really look like a bird", "same for cat"). Gull wingspan about 44 px (owner: the 58 px version was "massive", picked about 40); cat true scale, 16 px sitting (owner's pick). SpriteCook 218. Board: family "Animals".
- Checks on the preview: PEPPER UNCHANGED, flow 125/125, Tiled PASSED, BACKDROP OK, QA 0 problems (River Walk, Downtown tall). Independent reviews in art/gen/reviews/ (all fix lists applied).
- Board decision recorded: gull = redraw (owner in chat, 16:00).

Late evening: `art/animals-r2` (cb117c1, off `art/animals`), on the owner's board calls (cat bigger, gull smaller) and "go" on real-size boats with wider harbours (spend: "Yes, up to 260").
- Cat 32 px sitting (48 x 48 cells), gull 34 px span (36 x 44 cells, 7-frame flap), rowing boat 182 px hull (182 x 96 cells; a man rowing; cut at the water surface). SpriteCook 178.
- River Walk harbour +256 px (level 4096), Night Harbour rowboat gaps +128 px each (level 4736, lamps moved to stay 1000 px apart). Golden trace re-recorded (level change; Pepper lab unchanged).
- Checks: physics River Walk 54/54, Night 40/40, Downtown tall 102/102, Rooftops 139/139; QA 0 problems; flow 125/125; Tiled PASS. Curve: T1-T3 PASS, T4 FAIL as on base. DI kids/parents River Walk 12.7/13.9 -> 5.5/9.3, Night 19.6/24.2 -> 19.8/32.2.
- Two independent review passes (art/gen/reviews/animals_r2_25oct.md), all fixes in. Board: family "Animals round 2" (replaces "Animals").
- Preview: `preview/25oct-late` = `preview/25oct-pm` + `art/animals-r2` (build on the Mac: `2d game test/PREVIEW 25 Oct late/FETCH_PREVIEW_25oct_late.love`).

## Waiting for the owner (max 3)

1. Board: "Animals round 2" (and the boat length, 182 px against the planned 160). Approve, fix or redraw per piece.
2. Play `_g`, then merge `prod/integrate` into main as v0.7? (recommended: yes, after his play).
3. Logo and tagline: which logo and which tagline.

## Known, next

- After the board: merge the approved branches into a new `prod/integrate-*`; add the gull and cat colours to the palettes (make_palette keep list).
- Next River Walk families (docs/art_backlog.md): gable and cafe at true scale on screen 12, road traffic, water.
- Pre-existing: `Sc.railing` builds railings from whole 84 px units, so a railing stops up to 83 px short of its prop (67 px on promenade B).
- Ledger rows were added on three branches; the preview merge joins them (art/gen/ledger.csv).
- Child playtest with the kit (`docs/playtest_kit.md`) still open. River Walk scale calls open: lamp posts, rowing boats.

## Credits

- 25 Oct: SpriteCook 444 (lime 48, animals 218, animals round 2 178), over the 150 daily cap with the owner's words (16:03, 17:27, 20:20). SpriteCook 634 left.

---

## Earlier today (kept from the 13:30 STATUS)

## Main

- `main` is **v0.6** (1b5a30f, Fri 20:15). Nothing merged since.

## Integration branch: `prod/integrate` (27be9b4)

Everything waiting, in one playable build (`FETCH_PREVIEW_24oct_g.love` on the owner's Mac). All checks pass: PEPPER UNCHANGED, flow 125/125, Tiled, QA 0 problems on all six levels.
- `ui/hud-v8`: every screen in the new UI (title, menu, options, controls, level select cards, intro, talk panel, hint bubbles, pause, tally show, story, game over, ending, Fetch Frenzy, sound toast). No old style left.
- `ui/panel-hud`: no HUD row under centred cards.
- `ui/review-fixes`: from an independent review of all 65 screens. Locked cards show the real picture, empty sockets for medals not won, story and Mia lines at most 6 words a child knows (list: CHANGELOG), sniff taught by a hint bubble, Pepper in her colours on hint pictures, FETCH FRENZY! the only bonus name, ALL CAUGHT!, pieces inside panels, smaller HUD score. `ui/umlaut`: SÖDER with a capital Ö.
- `art/pilot-oldtown`, `art/placement`, `r9/levels` (Rooftops 23 screens, Night Harbour ball fix), `ops/regroup` (playtest kit).
- Title picture: the material cleanup (a1e0e15). Not taken: the hand shading pass on `ui/title-sheen` (owner: bad shading). Tried and not better: `art/title-light` (keeps the shading but stays mottled).

## Waiting for the owner (13:30, superseded above)

1. Play `_g`. Then merge `prod/integrate` into main as v0.7? (recommended: yes, after his play).
2. Logo and tagline: which logo (clean, gradient, bands, steps6) and which tagline (capitals or lowercase).
3. Child playtest with the kit (`docs/playtest_kit.md`).

## Known, next

- River Walk scale calls from the placement audit (houses, lamps, railing a third to half of true size).
- Greybox labels still show in Söder Hill and Night Harbour levels (they go with their art).
- `layout_qa8.py` crashes on pause frames (expects the old row boxes): update it.
- Two producer sessions worked the same branches on 24 Oct. From now on the producer is the session using the `fetch-game-manager` skill. The nightly run (22:39) uses `night/*` branches only.

## Credits

- SpriteCook 1,078 left. Artlist 34,795 left (plan 80,000 renews 26 Oct). 25 Oct: 6,380 Artlist spent (golden screens, pilot, cyclist probe).
- Ledger: `art/gen/ledger.csv`, `python3 tools/ledger.py report`. 3-25 Oct backfilled: Artlist 31,740 spent, 2 % in the game; SpriteCook ~4,068, ~57 % in the game.

## Board review (owner, 25 Oct, 13:35)

- 42 items: 1 approve (haze), 12 fix, 28 redraw, 1 open (town_statue). Plan by level and family: `docs/art_backlog.md`. Free script fixes on existing art are out (BIBLE).

## Workflow (owner, 25 Oct)

- `docs/WORKFLOW.md` is the order of work; `tools/pipeline.py status` shows every asset's step. Start sessions with the fetch-game-manager skill.
- Next art: the River Walk sample screen (approved pieces + the missing 3-4), cap 300 credits, then families. It must fix the owner's 25 Oct rule "taller than the viewport": `tools/check_backdrop.py` fails HOME (building, top y 39), TREE (tree, 47) and tree_near (x 1056, 39). The true-scale house is built from stamped parts (0 credits); the street trees are tall limes with the crown cut by the top edge. Palette: `art/palettes/riverwalk.gpl` (v1, 56 colours from approved art).
- Branch `ops/workflow` (this setup) is merged into `prod/integrate`.

How to update this file: rewritten by the producer session at the end of each working session.
