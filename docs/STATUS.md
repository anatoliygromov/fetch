# FETCH! Status

## Evening of 6 Nov, producer session 2 (18:30 to 21:10): the asset run for River Walk, City Park and Downtown

**Owner:** 18:38 "Spend the credits, make assets"; 18:45 "All 3 levels now, up to 2,000" (lifts BIBLE 4's sample-screen wait and the 150 a day cap for this run only); 18:43 "use more agents for efficiency"; 19:12 "you're spending SpriteCook credits on assets with wrong scale" (all paid calls stopped at 19:12 and not resumed); then "looks weird" on the City Park pond, the Downtown high road, the River Walk asphalt joins, and the dark hint panels.

**Two producer sessions ran at once tonight** (BIBLE 8 says one). The other one made `preview/06nov` (hud-v8, bikes-front, road, rowing boats). This session never pushed to it; `preview/06nov-run` is built on top of it.

**Credits (SpriteCook):** this session 632 (oak 76, birch 48, City Park props 216, City Park critters 62, oak climbing parts 60, Downtown traffic 134, Downtown props 36). Wasted on wrong scale: 108 (Nano Banana 2.1 renders: cargo bike 24, tram 36, hedge 24, tub 24) plus a duplicate duck boat (48). The other session: 302 (rowing boats 162, willow 76, rower 64). Balance 2,100 at 21:00. Artlist 0 (own account, 60,530, renews 26 Nov). Ledger on `preview/06nov-run` matches the account for this session's jobs.

**New rule, now code:** `tools/scale_gate.py` measures Pepper and the subject in every paid render before any cut or retry; preflight refuses Nano Banana 2.1 for blockout jobs (`rules.json no_blockout_models`); the default model is GPT 2.5 Sunburst. Line in `docs/art_learnings.md`.

**Build:** `preview/06nov-run` (head after this commit), `2d game test/PREVIEW 6 Nov late/FETCH_PREVIEW_06nov_late.love`. Checks: PEPPER UNCHANGED, flow 125/125, Tiled, BACKDROP OK, physics on all 8 levels, autopilot GOOD GIRL on the three, QA 0 problems, asset_qa 4 old FAILs (base 6), curve T1-T4 PASS.

**Merged into the run branch** (each family passed an independent review, 1 to 3 rounds): tools/scale-gate-06nov, art/cp-oak-06nov, art/rw-props-06nov, art/rw-ground-06nov, art/rw-audit-06nov, art/dt-traffic-06nov, art/dt-props-06nov, art/dt-roofs-06nov, art/dt-built-06nov, art/dt-highroad-06nov, art/dt-audit-06nov, art/cp-built-06nov, art/cp-props-06nov, art/cp-critters-06nov, art/cp-pond-06nov, art/cp-audit-06nov, ui/hint-bubbles-06nov. **Not merged:** art/cp-boughs-06nov (oak climbing branches FAILED two review rounds: the game keeps the code branches; method change is the owner's call), art/cp-backtrees-06nov (willow spec only).

**State per level** (everything the game draws, measured by hooking love.graphics.draw over the full sweep and an autopilot run):
- River Walk: new and on the board: road and quay joins, bridge arch, front hedges, birch, grit box, pontoon, kennel, bone outline. Waiting on the board from 5 Nov: traffic (2 cards), water taxi and piles, street (gable bay, cafe). Approved: bench, bin, lamp, kiosks, planter, flower box, pavement, haze, cloud8, park_log, pier, skyline, home, lime, railing. Owner calls: kiosks (60 px), lamps (101 or 207 px), the wooden pier's legs, kennel, jetty and pontoon sizes, the other session's rowing boats (not on the board).
- City Park tall: new and on the board: old oak (round 4 PASS), magpie, duck boat (two to pick from), goose fly row, hedge, leaves, hollow log, bush, pond with bank and waterline, granite stones, rope bridges, arbour, play tower, keeper's winch, climbing frame, front bushes, earth bands, gate, swings. Still code-drawn and weak: the oak climbing branches, the bare peach plain at the high camera. On the board from 5 Nov: lime, ash, mid trees.
- Downtown tall: new and on the board: tram (solid, true size), cargo bike, props, roof kit, balconies, fountain, facades, far roofs, door, gate, house 3, bollard, fixes on houses 1 and 2, awnings and table, the high road on true-scale fronts (flag H.PLAZA_FRONTS), the quay and canal edges, lanterns, footbridge piers. Owner calls: plaza houses (true-scale fronts or doll houses), kiosk, parasol and stall boxes below true scale, tram size, statue. On the board from 5 Nov: the sample screen pieces.
- All levels: every in-level hint in the light speech bubble.

**Waiting for the owner (board v13, 14 new cards at the top):** approve, fix or reject per piece; the questions on each card; the decision card on the oak climbing branches (about 300 to 380 credits for whole trees, or keep the code). Also: which session is the producer; resume paid jobs (1,444 left of his 2,000 for this run).

**Known:** `maps/riverwalk.tmx` differs from `level/riverwalk.lua` (13 places, decorative); `tools/check_flow.sh` shares one save folder, so parallel runs fail falsely (give it its own XDG_DATA_HOME); asset_qa's bone exception is out of date (bones now outlined).

## Evening of 6 Nov: fixes from the owner's play of the 6 Nov preview (live session, 0 credits)

**Owner, 19:06 to 19:13:** the cyclist rides behind the flower boxes; old speech panel; "boat is still ridiculously small"; "this asphalt transition is crazy", "the asphalt is moving weirdly", "why asphalt color differ here?". 19:10: "Go".

**Cause of the first two:** his decisions of 24 Oct (`ui/hud-v8`, speech bubbles) and 25 Oct (`play/bikes-front`) sat on side branches. `prod/integrate-h` had the bubbles, but `prod/integrate`, `-b`, `-c` and every preview since were built without them. New check `tools/check_approved.py [BASE]` lists owner-marked commits missing from a branch; run it before every preview or integration (`docs/not_merged.txt` for what is left out on purpose).

**Branches:**
- `preview/06nov` = `preview/05nov-night` + `ui/hud-v8` + `play/bikes-front` + the road fix + the rowboat spec. Build: `2d game test/PREVIEW 6 Nov evening/FETCH_PREVIEW_06nov_fix.love`.
- `prod/integrate-d` = `prod/integrate-c` + the same three fixes (no 5 Nov art, which still waits for the board).
- Checks on `preview/06nov`: PEPPER UNCHANGED (4591), flow 125/125, Tiled PASS, BACKDROP OK, River Walk physics 55/55, curve T1-T4 PASS, check_approved ALL MERGED.

**Road:** the road is painted only under the level promenade (y 184); under the two ramps and the lower quay a granite quay wall (`tools/make_quaywall.py`, level courses anchored in the world). Before, the asphalt there was a sheared copy at another scroll speed and shade.

**Rowboat (done, 6 Nov 19:37 to 20:10):** owner's yes ("use credits"), then "rerender this asset in spritecook, it's really low quality". In the game: round 2, GPT 2.5 2K (`rw_rowboat_r2`), 239 px boat (1.29x the 4 m spec, kept for quality), rower animated on his own; the harbour 352 px wider. SpriteCook 162 credits in all (round 1 76, round 2 86), ledger matches. Build: `PREVIEW 6 Nov evening/FETCH_PREVIEW_06nov_boats.love`. Not on the board yet.

**Waiting for the owner:** (1) play the build; (2) yes to 62 credits for the rowboat; (3) merge `prod/integrate-d` into main?

## Night of 5 Nov: SpriteCook run (live session, owner asleep)

**Owner, 21:45 and 21:47:** "we have a new token allowance on Spritecook, go use it! plan first and then execute as much as possible" and "Make sure you can execute over night without me needing to do stuff, I go sleep now". Read as: the yes on tonight's total, and his words to lift the 150 a day SpriteCook cap for tonight only. Every other rule stands: preflight on every job, 3 paid jobs per asset, 2 retries per family, gates 1 to 8, nothing reaches him but the board, nothing merged to main.

**Balance at start:** SpriteCook 3,634. Artlist: 0 tonight.

**Plan, ceiling 900 SpriteCook credits** (the rest stays for the fix rounds after his board review):

| Track | Branch | What | Method | Cap |
| --- | --- | --- | --- | --- |
| 1 | `art/rw-traffic-05nov` | River Walk road traffic family (A): promenade cyclist (rw_cyclist_adult), road_cyclist1 and 2 with their roll clips, road_car1, road_car4 | SpriteCook stills at the lane scale, pixel-engine animation at 1x, polish, review | 300 |
| 2 | `art/cp-sample-05nov` | City Park sample screen, screen 6 (old oak) at both cameras, with his 26 Oct picks 1 (true-width trunks, one leaf mass per tree) and 2b (young 6 m mid trees, 138 px) | SpriteCook for the plants; screen built in the game | 300 |
| 3 | `art/dt-sample-05nov` | Downtown sample screen, with his 26 Oct picks 1a (first floor: houses run past the top) and 4a (shelter and gateway at true scale, crates as perches) | built from stamped parts (0 credits); SpriteCook only for organic pieces | 150 |
| 4 | `art/rw-water-05nov` (after track 1) | River Walk ferry (A); the pile built (C) | SpriteCook still, polish, review | 150 |

Not tonight, by the rules: the duck boat and other City Park and Downtown pieces wait for their sample screens (BIBLE 4); animals round 2 and the gable fix B still wait on the board.

Progress is added below as tracks finish.

## Result (night of 5-6 Nov)

**SpriteCook: 600 credits spent of the 900 ceiling** (3,634 to 3,034; ledger `art/gen/ledger.csv` matches the account to the credit). Artlist 0. Every job preflighted with the owner's words; no family went over 3 paid jobs per asset or 2 retries.

**On the board, six family cards** (each piece passed an independent reviewer that did not make it, after 1 to 4 rounds):

| Card | Pieces | Credits | Questions for the owner |
| --- | --- | --- | --- |
| River Walk water | ferry (now a small water taxi on the same route boxes), mooring pile (built) | 24 | keep the water taxi, or change the level for a bigger ferry? |
| River Walk traffic | 2 promenade riders with pedal loops, 2 lane riders at 55 px/m, estate car, hatchback | 220 | car sizes; redraw the other cars too (done, next card) |
| River Walk traffic 2 | van, taxi (blank lit roof box), estate | 72 | van side plain or a picture without letters? |
| City Park sample screen | lime, ash, 3 young mid trees PASS; the old oak shown but NOT passed (leaf patchwork after 3 rounds and a re-cut) | 284 | yes to regenerate the oak (about 76, over the family retry cap)? trunk widths (oak 54, lime 36, ash 29-33 vs plan 46/60 and 23) |
| River Walk street, screen 12 | the gable's door bay (your option B, 116 px river view) and the cafe, built at true scale | 0 | keep option B, or the whole gable back? |
| Downtown sample screen | fronts 1-4 past the top, portal top, bay window with the golden bone pier, shelter, gateway, crates, board on crate legs (all built, 0 credits) | 0 | screen 10's old brick gate (no house there); the checkpoint lamp in front of the arch. Note: the street is darker and calmer than before so it sits below the far layers |

**Playable build:** `2d game test/PREVIEW 6 Nov night/FETCH_PREVIEW_06nov.love` = branch `preview/05nov-night` (all six families merged on top of `prod/integrate-c`; not an integration branch, nothing merged into main or prod). Checks on it: PEPPER UNCHANGED, flow 125/125, Tiled PASS, physics River Walk 55/55, City Park tall 97/97, Downtown tall 102/102, curve T1-T4 PASS, asset QA 6 FAIL (all old library art: building, cafe, gable, rail_bg_left, town_bollard, park_leaves_flat). BACKDROP OK (the River Walk gable, the last fail, is fixed).

**Branches:** `art/rw-traffic-05nov`, `art/rw-traffic2-05nov`, `art/rw-water-05nov`, `art/cp-sample-05nov`, `art/dt-sample-05nov`, `art/rw-street-05nov`, `preview/05nov-night`, `ops/spritecook-05nov`.

**Tool fixes found tonight** (each on its branch, all in the preview):
- `tools/grid_cut.py` skipped palette lines with a leading space (every colour with red under 100), so palette snaps lost every dark. Fixed.
- `tools/preflight.py` priced references once per job; SpriteCook bills them per variation (a 2-variant job with 3 references is 76, not 52). Fixed.
- `tools/pipeline.py` now reads only the latest "# Round N" section of a review.
- `tools/asset_qa.py`: `--layer lane` works; `--file` uses the game's own fade when `--fade` is not given.
- New: `tools/aseprite_io.py` (write and check .aseprite without the app, so polish works when the Mac sleeps), `tools/grid4_cut.py`, `tools/build_traffic.py`, `tools/build_ferry.py`, `tools/build_pile.py`, `tools/build_dt_street.py`.

**Not spent, by the rules:** City Park and Downtown pieces wait for their sample screens' approval (BIBLE 4); the oak regeneration and anything over a family cap wait for the owner's words; animals round 2 still waits on the board.

**Waiting for the owner (max 3):**
1. The board: six family cards from tonight (approve, fix or reject per piece; the questions above).
2. Play `FETCH_PREVIEW_06nov.love`.
3. Still open from before: merge `prod/integrate-c` into main as v0.7.


---


As of Sun 25 Oct 2026, 15:30. Rules: `docs/BIBLE.md`. Decisions: the review board, https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk.

## Today (25 Oct, afternoon): the River Walk sample screen

- Branch `art/rw-sample-screen` (off `prod/integrate` c1c37a4). Screen 1 (Home) at final quality: the house at true scale (built from stamped parts, `tools/build_rw_home.py`, 0 credits), the street lime (SpriteCook, 48 credits, trunk 23 px, crown cut by the top), the quay railing at 50 px (`tools/make_bg_railing50.py`, 0 credits). The lime also replaces tree_near on screen 4. check_backdrop now passes (was 3 fails).
- Checks green on the branch: PEPPER UNCHANGED, flow 125/125, Tiled PASSED, BACKDROP OK, physics 54/54, QA 0 problems, autopilot GOOD GIRL!, check_curve T1-T4 PASS.
- Independent review: round 1 found 8 fails (lime rim, frame-cut crown, house quoin gap); fixed; round 2 9/9 PASS on all three (`art/gen/reviews/`).
- On the board: family card "River Walk sample screen" (3 pieces). `tools/pipeline.py status`: rw_home, rw_lime, rw_rail_bg wait for the board.
- Palette `art/palettes/riverwalk.gpl` is v2 on this branch (86 colours: v1 + the three pieces' ramps); it stands only with the board approve.
- Frames: `docs/review/25oct/`. Build on the Mac: `2d game test/SAMPLE SCREEN 25 Oct/FETCH_SAMPLE_25oct.love` (branch head 54b2f07).

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
