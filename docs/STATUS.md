# FETCH! Status

As of Sun 25 Oct 2026, evening. Rules: `docs/BIBLE.md`. Decisions: the review board, https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk.

## Night of 25 Oct (unattended run)

Base: `ops/night-25oct` f54a219 (same as `preview/25oct-pm`). `ops/night-25oct` already existed from the evening session, so this STATUS is on `ops/night-25oct-b`. 0 credits, no art touched, nothing merged.
- Track 1, `night/25oct-tools` (654d6a0): `tools/layout_qa8.py` no longer crashes on the v8 pause frames (STATUS "Known, next"). Tools only, no game code.
- Audit on the base (no change): PEPPER UNCHANGED (4591 steps), flow 125/125, Tiled PASSED, BACKDROP OK. Curve (tall order, 20 seeds x 8 personas): T1, T2, T3 PASS, T4 FAIL (City Park tall lost runs 9.4%, the known failure; Downtown 1.9, Rooftops 1.2, others 0). DI kids/parents: River Walk 12.7/13.9, City Park 14.0/26.4, Downtown 12.9/16.1, Rooftops 21.2/22.1, Soder 17.4/14.3, Night 19.6/24.2.
- layout_qa8 on 22 fresh UI frames now finishes. Open FAILs: cursor to label gap is 4 (check says 3) on four pause frames; pause_sound cursor not centred on its label; tally label left edges 48 and 71 (check expects one per side); 8 picture edges use colour (214,190,150), not outline or shadow. Either the check is stale or the UI is off. Not tuned away.
- Skipped: Sc.railing (whole 84 px units) changes how approved River Walk art looks, so it waits for a yes. Level changes for T4: not started, no approved ask.

Look at: CHANGELOG entry on `night/25oct-tools`; run `python3 tools/ui_frames.py out && python3 tools/layout_qa8.py out out_guides`.
Decisions waiting: 1. Is the pause cursor gap 4 right (then set the check to 4)? 2. Fix Sc.railing to end flush with its prop? 3. Work on City Park tall lost runs (T4)?
Problems: apt install of python libs broke PIL/numpy here; used a venv. Not a repo issue.

---

## Today (25 Oct, afternoon and evening)

Three branches, each off `prod/integrate` c1c37a4, all checks green; together on `preview/25oct-pm` (build on the Mac: `2d game test/PREVIEW 25 Oct pm/FETCH_PREVIEW_25oct_pm.love`).
- `art/rw-sample-screen` (80ec97f): River Walk sample screen, screen 1: true-scale house (built, 0 credits), street lime (SpriteCook 48), quay railing 50 px. Palette riverwalk.gpl v2 (86). Board: family "River Walk sample screen".
- `art/rw-fixes` (64adc24): cloud8, park_log, pier, skyline fixed pixel by pixel (0 credits; every pixel in art/source/rw_fixes/edits.json). The gull left for a redraw (owner 16:00). Board: family "River Walk fixes by hand".
- `art/animals` (a640156): gull and cat redrawn (owner: "holes, doesnt really look like a bird", "same for cat"). Gull wingspan about 44 px (owner: the 58 px version was "massive", picked about 40); cat true scale, 16 px sitting (owner's pick). SpriteCook 218. Board: family "Animals".
- Checks on the preview: PEPPER UNCHANGED, flow 125/125, Tiled PASSED, BACKDROP OK, QA 0 problems (River Walk, Downtown tall). Independent reviews in art/gen/reviews/ (all fix lists applied).
- Board decision recorded: gull = redraw (owner in chat, 16:00).

## Waiting for the owner (max 3)

1. Board: the three family cards (sample screen, fixes, animals). Approve, fix or reject per piece.
2. Play `_g`, then merge `prod/integrate` into main as v0.7? (recommended: yes, after his play).
3. Logo and tagline: which logo and which tagline.

## Known, next

- After the board: merge the approved branches into a new `prod/integrate-*`; add the gull and cat colours to the palettes (make_palette keep list).
- Next River Walk families (docs/art_backlog.md): gable and cafe at true scale on screen 12, road traffic, water.
- Pre-existing: `Sc.railing` builds railings from whole 84 px units, so a railing stops up to 83 px short of its prop (67 px on promenade B).
- Ledger rows were added on three branches; the preview merge joins them (art/gen/ledger.csv).
- Child playtest with the kit (`docs/playtest_kit.md`) still open. River Walk scale calls open: lamp posts, rowing boats.

## Credits

- 25 Oct: SpriteCook 266 (lime 48, animals 218), over the 150 daily cap with the owner's words (16:03 and 17:27). SpriteCook 812 left.

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
