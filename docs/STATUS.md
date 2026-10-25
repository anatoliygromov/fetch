# FETCH! Status

As of Sun 25 Oct 2026, 15:30. Rules: `docs/BIBLE.md`. Decisions: the review board, https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk.

## Today (25 Oct, afternoon): the River Walk sample screen

- Branch `art/rw-sample-screen` (off `prod/integrate` c1c37a4). Screen 1 (Home) at final quality: the house at true scale (built from stamped parts, `tools/build_rw_home.py`, 0 credits), the street lime (SpriteCook, 48 credits, trunk 23 px, crown cut by the top), the quay railing at 50 px (`tools/make_bg_railing50.py`, 0 credits). The lime also replaces tree_near on screen 4. check_backdrop now passes (was 3 fails).
- Checks green on the branch: PEPPER UNCHANGED, flow 125/125, Tiled PASSED, BACKDROP OK, physics 54/54, QA 0 problems, autopilot GOOD GIRL!, check_curve T1-T4 PASS.
- Independent review: round 1 found 8 fails (lime rim, frame-cut crown, house quoin gap); fixed; round 2 9/9 PASS on all three (`art/gen/reviews/`).
- On the board: family card "River Walk sample screen" (3 pieces). `tools/pipeline.py status`: rw_home, rw_lime, rw_rail_bg wait for the board.
- Palette `art/palettes/riverwalk.gpl` is v2 on this branch (86 colours: v1 + the three pieces' ramps); it stands only with the board approve.
- Frames: `docs/review/25oct/`. Build on the Mac: `2d game test/FETCH_SAMPLE_25oct.love`.

## Waiting for the owner (max 3)

1. Board: the River Walk sample screen family (approve, fix or reject per piece).
2. Play `_g`, then merge `prod/integrate` into main as v0.7? (recommended: yes, after his play).
3. Logo and tagline: which logo and which tagline.

## Known, next

- After the sample screen is approved: merge `art/rw-sample-screen` into a new `prod/integrate-*`, then the River Walk families in docs/art_backlog.md order (gable and cafe at true scale on screen 12, fixes by hand, road traffic, water).
- Pre-existing: `Sc.railing` builds railings from whole 84 px units, so a railing stops up to 83 px short of its prop (67 px on promenade B).
- Child playtest with the kit (`docs/playtest_kit.md`) still open.
- River Walk scale calls still open from the layer plan: lamp posts (101 px or 207 px), rowing boats (62 px or 160 px).

## Credits

- 25 Oct afternoon: SpriteCook 48 (rw_lime: probe 24 + retry 24), within the owner's yes of up to 72. SpriteCook 1,030 left.

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
