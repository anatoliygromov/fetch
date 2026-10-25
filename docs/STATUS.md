# FETCH! Status

As of Sun 25 Oct 2026, night (21:57). Rules: `docs/BIBLE.md`. Decisions: the review board, https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk.

## Night of 25 Oct (unattended run, 20:28 to 21:57 Stockholm)

0 credits, no image service call, nothing merged, nothing posted to the board. Base read at 20:30: `preview/25oct-pm` f54a219 (this branch is cut from it); the evening session's newer STATUS (`preview/25oct-late` 6c82a8b, 21:31) is kept below this section. Board at 20:16-20:18: approve cloud8_v2, park_log_v2, pier_v2, skyline_v2, rw_home, rw_lime, rw_rail_bg; redraw gull_v3 and cat_v2 (done since as `art/animals-r2`).

**Tracks** (night branches off `art/rw-sample-screen` 80ec97f, approved tonight, or `prod/integrate` c1c37a4)
1. `night/25oct-rw-street` (1b1d8ee), off 80ec97f. "Known, next": the gable and the cafe at true scale on screen 12, built from stamped parts like HOME (tier C, 0 credits). `rw_gable` 148 x 180, `rw_cafe` 124 x 180, 20 colours each, 0 lone pixels, tops at y -6; the railing ends at the gable; palette riverwalk.gpl v3 (109 colours). Independent review: round 1 FAIL on small located defects, fixed; round 2 PASS 9/9 on both. Pipeline: both at review, next the board. Checks green (PEPPER UNCHANGED, flow 125/125, Tiled, BACKDROP OK, physics and QA 0 problems on all six levels, curve T1-T4 PASS).
   `night/25oct-rw-street-late` (7f1adc8), the same pieces ported onto `preview/25oct-late` (River Walk is 4096 px there: +256 px). Checks green. Merge this one if `art/animals-r2` goes in, the first if not.
2. `night/25oct-fixes` (f3bf4c0), off 80ec97f. S2 from "Known, next": the quay railings stopped 7 and 69 px short (water showed before the gable); the remainder now goes into the last bays, posts at least 48 px apart (new physics test 20, widths 89-430). `layout_qa8.py` crashed on the v8 pause; it now checks the v8 pause and tally as drawn (ALL PASS, 169 checks). `check_backdrop.py` read the declared y0, so the old gable passed with its stepped top in view; it now measures every column and lists rw_home and rw_lime. Independent review: 4 findings, all fixed. Checks green; BACKDROP fails the old gable on this branch alone (true), OK with track 1.
3. `night/25oct-prep` (654151a), off c1c37a4. Grey-blockout sheets: lamp post and rowing boat scale on the sample-screen frames (a lamp of 4 m or more hides its checkpoint light above the screen; 3 m keeps it), gull and cat sizes (decided since by the evening session). `preflight.py` takes the owner's picked size for animals (`owner_size`), reviewed: `art/animals-r2` had to set the cat's real height to 0.65 m to get past the check.

**Trials (local only, not pushed).** `prod/integrate` + `art/rw-sample-screen` + `art/rw-fixes` + `night/25oct-fixes` + `night/25oct-rw-street`: only CHANGELOG conflicts (keep both sections); every check green, layout_qa8 ALL PASS, curve T1-T4 PASS with DI as on the base. `preview/25oct-late` + `night/25oct-fixes` + `night/25oct-rw-street-late`: merges clean; every check green (PEPPER UNCHANGED against its re-recorded trace, flow 125/125, Tiled, BACKDROP OK, physics and QA 0 problems), curve T1-T4 PASS with DI identical to `preview/25oct-late`.

**Look at**
- `docs/review/25oct-night/rw_street/rw_screen12_before_after_3x.png`, `rw_street_5x_with_bench_bin_lamp.png`, `cards/PASS_rw_gable.png`, `cards/PASS_rw_cafe.png` (`night/25oct-rw-street`).
- `docs/review/25oct-night/fixes/railing_promenadeB_end_before_after_3x.png` (`night/25oct-fixes`).
- `docs/review/25oct-night/prep/rw_scale_calls_2x.png` and `README.md` (`night/25oct-prep`).

**Waiting for the owner (new tonight)**
1. Merge into a new `prod/integrate-b`: `art/rw-sample-screen`, `art/rw-fixes`, `night/25oct-fixes`, `night/25oct-prep`? (yes or no). The railing fix changes how the approved railing is put together at its ends, not its pixels.
2. Board: "River Walk street backdrop": rw_gable, rw_cafe (approve, fix or redraw). The card is on the branch; not posted.
3. Two night routines are enabled (20:00 "FETCH! night manager" and 21:01 "Fetch Night Manager"); four night runs started tonight. Keep which one?
Still open from before: "Animals round 2" on the board; play `_g`, then v0.7; logo and tagline; lamp post height (sheet ready).

**Problems**
- The 20:29 run-now and the 21:01 run of the second routine made `ops/night-25oct-b`, `night/25oct-tools` (a second layout_qa8 crash fix, its stale FAILs left open) and `ops/night-25oct-c` (an audit). `night/25oct-tools` duplicates `night/25oct-fixes`: drop it.
- With 20 seeds those runs saw curve T4 FAIL on City Park (tall), 9.4 % lost runs, the same on main (pre-existing). With BIBLE's 10 seeds it passes.
- At 20:41 I stopped every running game process by mistake; the art agent re-ran its checks.
- The FETCH! project docs are not reachable from a cloud session: tonight's facts are here, in `docs/art_learnings.md` and in the prep README.
- `apt-get install love` fails in its man-page step; LÖVE 11.5 works. No matplotlib: the curve chart is skipped, numbers unaffected.

**Next run, if he says nothing:** no merges. River Walk road traffic and water need credits, so prep only: the City Park layer plan (the 0-credit step before its families) if he agrees, else an audit.

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
