# FETCH! Status

## Night of 9 Nov: audit of main (unattended run, 0 credits, no art or level changes)

Base: `main` at e560cb4. STATUS "Next 7 days", "Known, next" and the board have nothing open for night work, and no new owner decisions since 8 Nov. Audit only, no track branches, no game files changed.

**Checks on main:** PEPPER UNCHANGED (3908 steps). Flow 125/125. Tiled PASSED. check_approved ALL MERGED. check_curve (`riverwalk,citypark_tall,downtown_tall,rooftops,soder,night`, 20 seeds x 8 personas): T1, T3, T4 PASS, **T2 FAIL**, identical to 7 and 8 Nov.

**Finding (S2, unchanged):** River Walk screen 13 takes 36% of failures, limit 35%. Soder Hill screen 9 shows 50% but is under the 20-failure rule. Fixing it is a level change and needs your yes plus a Pepper trace re-record.

**Decision waiting:** fix River Walk screen 13, or accept 1 point over the limit?

**Problems:** check_curve cannot draw its chart (no matplotlib). Shallow clone note from check_approved. Sandbox setup: `love` needed `apt-get update` first; pip needed `--cert /root/.ccr/ca-bundle.crt` to finish.

**Branches:** `ops/night-09nov` only (this STATUS). No night/* branches.

## Night of 8 Nov: audit of main (unattended run, 0 credits, no art or level changes)

Base: `main` at e560cb4 (v0.7, sound pass, plan gate tooling). STATUS "Next 7 days" and the board have nothing open for night work, so this run audited and changed no game files. No track branches were made. This STATUS carries forward the 7 Nov one below.

**Checks on main:** PEPPER UNCHANGED (3908 steps). Flow 125/125. Tiled PASSED. check_approved ALL MERGED. BACKDROP OK. check_curve (`riverwalk,citypark_tall,downtown_tall,rooftops,soder,night`, 20 seeds x 8 personas): T1, T3, T4 PASS, **T2 FAIL**.

**Finding (S2, same as 7 Nov):** River Walk screen 13 takes 36% of failures, limit 35%. Soder Hill screen 9 shows 50% but is under the 20-failure rule. Unchanged since last night, so the plan gate commits did not affect it. Not fixed: it is a level change and needs your yes plus a Pepper trace re-record.

**Board read:** 178 decisions (55 approve, 31 fix, 82 redraw, 10 empty). Nothing new to act on without credits or new scope.

**Decision waiting:** fix River Walk screen 13 (level change, Pepper trace re-record), or accept 1 point over the limit?

**Problems:** none besides T2. check_curve could not draw its chart (no matplotlib in the sandbox); the numbers are fine. Shallow clone note from check_approved.

**Branches:** `ops/night-08nov` only (this STATUS). No night/* branches.

## Night of 7 Nov: audit of main (unattended run, 0 credits, no art or level changes)

Base: `main` at 57440ca (v0.7 plus the sound pass). Nothing in STATUS "Next 7 days" or on the board was open for night work, so this run audited and changed no game files. No track branches were made.

**Checks on main:**
- PEPPER UNCHANGED (3908 steps identical). Flow 125/125. check_approved: ALL MERGED.
- Tiled PASSED. (It failed at first only because the sandbox's system Pillow was broken; a clean venv fixed it. Not a game bug.)
- check_curve with `riverwalk,citypark_tall,downtown_tall,rooftops,soder,night`: T1, T3, T4 PASS, **T2 FAIL**.

**The one finding (S2): T2 spot share.** River Walk screen 13 takes 36.2% of failures (75 of 207); the limit is 35%. Soder Hill screen 9 shows 50%, but only 10 failures, so it is under the 20-failure rule and passes. The result is identical on 2c04160 (v0.7 merge, before the sound pass), so the sound pass did not cause it. The 7 Nov STATUS said T1-T4 PASS on prod/integrate-f; I could not reproduce that, possibly the later River Walk commits (e133677: rowers, jetty, ferry) shifted it. I did not bisect further.

**Decision waiting:** fix screen 13 of River Walk (a level change, needs your yes and a Pepper trace re-record), or accept 1.2 points over the limit?

**Still waiting from before:** the board cards, gull and cat size picks, open or closed street, the leaf front.

**Branches:** `ops/night-07nov` only (this STATUS). No night/* branches.

## Night of 6-7 Nov: the three levels brought to finished quality (live session, owner asleep)

**Owner, 20:01 to 20:19:** a proper lift in assets and game design tonight, 3 levels ready with full visual QA by the morning; use Fable and several agents; repo should feel mature and up to date; coordinate with the other sessions; the "Game porting and launch plan" rowboat was terrible, make it work. Picks: SpriteCook up to 900, Artlist up to 3,000 for concepts, merge to main as v0.7 if every check and the independent review pass, prune merged branches with an archive list, repo stays public, this session owns the rowboat and the "FETCH level asset plan" session's work.

**Method change (art):** hero pieces start from a concept painted into the real game frame (Artlist, design target only, preflighted as a concept job, ledger "reference"), then split: geometry BUILT by rule, only living parts from SpriteCook at game size with the concept as reference, mechanical motion keyed by rule, water and contact in code. Every track was checked by an independent Fable reviewer, then a fresh final-gate reviewer on the integration.

**Branches:** `prod/integrate-f` (= `night/06nov-integrate-f`) holds everything below on top of `prod/integrate-e` (the 12 `art/*-06nov` branches of the afternoon session). Tracks: `night/06nov-rw`, `night/06nov-cp`, `night/06nov-dt`; `night/06nov-concepts` (preflight concept jobs, concepts), `night/06nov-repo` (README). Reviews: `review/06nov-base`, `-rw`, `-cp`, `-dt`, `-final`.

**River Walk:** the rowing boat rebuilt (hull and oars built by rule, the grandpa rower from SpriteCook, a 7-frame loop by rule with a rest pose, the hull in the water with tint, ripples, wake, splashes; rower at the stern, Pepper amidships); harbour 208 px wider; kennel at true scale; jetty rebuilt as a landing stage; pontoon and ferry in the water; road one step darker; ground joins and audit fixes of the afternoon merged. Review: all screens PASS.
**City Park (tall):** true-scale weeping willow; pond bank kit after the concept; trunk pillars are lime trees; fork ledges redrawn as limbs (method changed after two failed rounds); root flares; keeper face; goose fly row; solid playground. Review: all 27 screens PASS.
**Downtown (tall):** 37 styled true-scale fronts built from parts; the high road attached (corbels, consoles, wall lanterns); green iron tram shelter; canal surface, poles in the flood, granite basin and stairs; open squares with a paved floor at both street ends so the spire stays (6a); `H.CLOSED_STREET` switches to a closed street. Review: all 33 screens PASS.
**Also:** hint bubbles in the light design (`ui/hint-bubbles-06nov`, owner 6 Nov); README rewritten; `docs/not_merged.txt` lists the rejected rowboat 240ffbe.

**Checks on prod/integrate-f:** PEPPER UNCHANGED (level trace re-recorded for the wider harbour, as for every River Walk change; lab trace 1401 steps identical), flow 125/125, Tiled PASSED, BACKDROP OK, check_approved ALL MERGED, physics on all six levels, autopilot GOOD GIRL, check_curve T1-T4 PASS.

**Credits tonight:** SpriteCook 140 of 900 (cp_willow 76, rw_rower 64; balance 2,100), both in the game. Artlist 1,440 of 3,000 (four concept sets, reference). Ledger matches the accounts.

**Board:** four new cards (River Walk, City Park, Downtown, gull and cat sizes).

**Waiting for the owner (max 3):**
1. The board: the three level cards (approve, fix or reject per piece) and their questions.
2. Gull and cat size picks (size sheets on the board); decision 2 open or closed street.
3. Your leaf front (decision 5) floats when the camera is up in the trees: keep, or tie to the ground?

**Scheduled night run (21:00, `ops/night-06nov`):** audit only, 0 credits; its two questions (which rowboat, hint bubbles) are settled above.

**Next if he says nothing:** the board fix rounds after his decisions; the animals after his size picks (credits per his yes).

## Evening of 6 Nov: fixes from the owner's play of the 6 Nov preview (live session, 0 credits)

**Owner, 19:06 to 19:13:** the cyclist rides behind the flower boxes; old speech panel; "boat is still ridiculously small"; "this asphalt transition is crazy", "the asphalt is moving weirdly", "why asphalt color differ here?". 19:10: "Go".

**Cause of the first two:** his decisions of 24 Oct (`ui/hud-v8`, speech bubbles) and 25 Oct (`play/bikes-front`) sat on side branches. `prod/integrate-h` had the bubbles, but `prod/integrate`, `-b`, `-c` and every preview since were built without them. New check `tools/check_approved.py [BASE]` lists owner-marked commits missing from a branch; run it before every preview or integration (`docs/not_merged.txt` for what is left out on purpose).

**Branches:**
- `preview/06nov` = `preview/05nov-night` + `ui/hud-v8` + `play/bikes-front` + the road fix + the rowboat spec. Build: `2d game test/PREVIEW 6 Nov evening/FETCH_PREVIEW_06nov_fix.love`.
- `prod/integrate-d` = `prod/integrate-c` + the same three fixes (no 5 Nov art, which still waits for the board).
- Checks on `preview/06nov`: PEPPER UNCHANGED (4591), flow 125/125, Tiled PASS, BACKDROP OK, River Walk physics 55/55, curve T1-T4 PASS, check_approved ALL MERGED.

**Road:** the road is painted only under the level promenade (y 184); under the two ramps and the lower quay a granite quay wall (`tools/make_quaywall.py`, level courses anchored in the world). Before, the asphalt there was a sheared copy at another scroll speed and shade.

**Rowboat (spec only, nothing spent):** `art/gen/jobs/rw_rowboat.json` (hull and rower render, 4.0 m = 185 px, 24 credits) and `rw_rower.json` (the rower alone, Pixel Engine, 12 credits), then the rowing loop from the rower still (26). Preflight PASS. **Total 62 SpriteCook credits.** The harbour (water x 2192-2640) must grow by about 200 px to keep two boats and the jetty; the level after it shifts right (0 credits, level change).

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
