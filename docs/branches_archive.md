# Merged branches to delete (archive)

These branches can be deleted (owner's yes, 6 Nov 20:10): every commit on them is in main (v0.7, 2c04160). The night session could not delete them: the session's git proxy refuses deleting branches it did not create. One command deletes them all from a Mac clone: `cut -d'`' -f2 docs/branches_archive.md | grep / | xargs -n 10 git push origin --delete`. Kept: main, round1, prod/*, ops/*, every branch of 6 Nov (names with 06nov) and anything not merged. To restore one: `git push origin <commit>:refs/heads/<name>`.

| Branch | Last commit | Date | Subject |
| --- | --- | --- | --- |
| `art/cp-sample-05nov` | 24b145d | 2026-11-05 | cp_midtrees review done |
| `art/dt-sample-05nov` | b437460 | 2026-11-05 | Board v10: Downtown sample screen card; 12 pieces review done |
| `art/fixes` | 428c2af | 2026-10-23 | Art fixes: statue tagged play, winch keeper and plaza houses faded, outlines completed, cl |
| `art/freefix` | 825fa8b | 2026-10-23 | Free fix pass: stamped windows, blotch clean, outlines, pixel patches (0 credits) |
| `art/haze` | f0331f9 | 2026-10-23 | Every fade in the level's own haze (owner decision 3) |
| `art/layers` | bbd5e90 | 2026-10-23 | Layer ladder: measuring tool, greyscale shots, ladder doc |
| `art/pilot-oldtown` | d942274 | 2026-10-23 | Old Town row: all seven houses built from the shared stamped parts |
| `art/placement` | 60d0388 | 2026-10-24 | High road lamps: the foot drawn wholly on its ledge (Downtown x 2420) |
| `art/preflight` | 287f148 | 2026-10-25 | art: preflight gate for generated art, whole-pixel grid cut, style card (25 Oct) |
| `art/qa` | c5c9a09 | 2026-10-23 | Asset QA gate: checks, cards, triage, the gates doc and the credit ledger |
| `art/rw-fixes` | 64adc24 | 2026-10-25 | River Walk fixes: the gull goes to a redraw (owner, 16:00), file back as on main; rejectio |
| `art/rw-sample-screen` | 80ec97f | 2026-10-25 | STATUS: build path |
| `art/rw-street-05nov` | 816e110 | 2026-11-05 | Board v12: River Walk street screen 12 card; rw_gable_bay review done |
| `art/rw-traffic-05nov` | 6534f8d | 2026-11-05 | Board v8: River Walk traffic family card; rw_road_rider2 review done |
| `art/rw-traffic2-05nov` | 3152be1 | 2026-11-05 | Board v11: River Walk traffic 2 card; three cars review done |
| `art/rw-water-05nov` | 1203607 | 2026-11-05 | Board v7: River Walk water family card |
| `art/tall-backdrop-rule` | 10bbf4d | 2026-10-25 | Rule: back buildings and front trees taller than the viewport, with tools/check_backdrop.p |
| `art/title-destray` | c8317a1 | 2026-10-25 | Title: remove stray pixels (clusters of 1-2 px) from all layers; stray_check tool |
| `art/title-props` | 0304d2a | 2026-10-25 | Title: thin built objects redrawn by rule (both lamps, bench, bin, railing posts, boat mas |
| `assets/complete` | c9e6ea8 | 2026-10-18 | Front-on picnic table; art for River Walk's kennel, kiosks and awnings |
| `assets/v2` | 60ceebc | 2026-10-19 | Credits count fixed in the changelog and the build script (250) |
| `audio/music` | fd6c530 | 2026-10-22 | make_music.py: piano rolls keep the wave and the notes on one time scale (jingles too) |
| `design/round2` | 4cb2b42 | 2026-10-22 | Rooftops: beat sheet, paper map and engine specs; route renders for both maps |
| `engine/height` | d302095 | 2026-10-22 | Night darkness follows the camera's y; the checks' results in the changelog |
| `engine/round2` | 5f618b7 | 2026-10-22 | CHANGELOG: notes for docs/tiled.md; rewrap |
| `fix/console` | 8e28369 | 2026-10-07 | Changelog: fix/console |
| `level4/soder` | 0187f76 | 2026-10-19 | Level 4 docs: Soder Hill beat sheet and CHANGELOG entry |
| `level5/night` | 75b43a6 | 2026-10-19 | docs/night_beatsheet.md and the CHANGELOG section for level5/night |
| `levels/v2` | cb5fc90 | 2026-10-19 | Readability: a taller goose with a hissing pose, a bigger rower leaning into the oars, gul |
| `lk/look` | 9c3bcbd | 2026-10-12 | Lion King look: colour scripts for City Park and Downtown, front-on crate, table and duck  |
| `ml/art` | 84e6bb6 | 2026-10-06 | Changelog: City Park and Downtown art (branch ml/art) |
| `ml/fixes` | 659be90 | 2026-10-06 | The girl is Mia; bikes ride forwards |
| `ml/levels` | 6d89d26 | 2026-10-06 | Docs: beat sheets, River Walk notes, changelog for ml/levels |
| `ml/ui` | 36e2cd2 | 2026-10-06 | Changelog: talk panel, nudges, medals, shared play, HARD MODE |
| `multilevel` | 06a86e7 | 2026-10-06 | Playtest: the eight personas |
| `night/25oct-fixes` | f3bf4c0 | 2026-10-25 | Review fixes: railing remainder shared by two even bays (no doubled post), layout_qa8 tall |
| `night/25oct-lab` | d9fe696 | 2026-10-25 | Lab run-up: probe Pepper's paw span less the walkback's stop, not x +-1 (review); River Wa |
| `night/25oct-prep` | 654151a | 2026-10-25 | Prep notes: the animal sizes and the boat call were decided in the evening session (art/an |
| `night/25oct-rw-street` | a8f1461 | 2026-10-25 | Screen 12 river view options for the owner: as built 48 px, gable door bay only 116 px, ca |
| `night/26oct-cp-code` | c5850e7 | 2026-10-26 | City Park (tall): the low bough's leaf patches on whole pixels (review fix of 8 e) |
| `night/26oct-dt-code` | 834ec4d | 2026-10-26 | Downtown: review frames and notes for the code-only changes |
| `night/30oct-gable-b` | be9bf9f | 2026-10-30 | River Walk screen 12: river view option B, the gable shows its door bay only (116 px river |
| `night/all` | 4e52536 | 2026-10-05 | Merge night/citypark into night/all |
| `night/base` | 4fe7c5d | 2026-10-05 | Tools: Pepper trace check (--auto --trace) and the golden trace of the approved build |
| `night/citypark` | 282fd41 | 2026-10-05 | check_pepper.sh: private temp files; show a Lua error if the run crashes |
| `night/pepper-extras` | 9dbec8f | 2026-10-05 | Extras: the bone pop is drawn behind Pepper, so its +100 never covers her |
| `night/riverwalk-art` | 75c3ee4 | 2026-10-05 | check_pepper.sh: private temp files; show a Lua error if the run crashes |
| `play/bikes-front` | 60f57ae | 2026-10-25 | BIBLE: passing bikes ride in front of Pepper (owner, 25 Oct) |
| `polish/round2` | e9f3000 | 2026-10-22 | docs/tiled.md: tall levels, lifts, hints by height, drag-safe numbers, Tiled versions, a n |
| `preview/05nov-night` | dff15cf | 2026-11-05 | STATUS: River Walk street card, backdrop check clean |
| `preview/art` | 884b87e | 2026-10-06 | Changelog: near-lane traffic at its perspective size |
| `r3/bonus` | 9faab2a | 2026-10-22 | FETCH FRENZY in the flow test: tally -> bonus -> story with a golden bone, no bonus withou |
| `r3/citypark-art` | ae47aae | 2026-10-22 | Tall City Park: the treetop tier dressed (branches, trunks, canopies, walks, arbour, tower |
| `r3/design` | 36ad53c | 2026-10-22 | CHANGELOG: check results for r3/design |
| `r3/rooftops` | 813bdbc | 2026-10-22 | Rooftops: beat sheet as built, route render entry, changelog |
| `r4/playtest` | dc00863 | 2026-10-22 | Playtest report 22 Oct: the level order checked (20 runs per persona per level) |
| `r5/bugs` | 2383a1d | 2026-10-22 | Bug list 22 Oct: docs/bugs_22oct.md (16 items, 7 fixed, the rest for the art plan or the o |
| `r6/engine` | fabcffa | 2026-10-22 | Tests: the safety nets in every level's --physics run (tests_safety.lua); three tests upda |
| `r6/lab` | e8dbbab | 2026-10-22 | Playtest baseline v2 (22 Oct): three orders in whole-game mode, 8 personas x 10 seeds |
| `r6/levels` | 82c910f | 2026-10-22 | Par time for City Park after the frame fix; branch checks and what is left in the changelo |
| `r7/curve` | bf723ce | 2026-10-23 | Changelog: the r7 curve result and the branch checks |
| `r8/levels` | 1b3a08c | 2026-10-23 | Changelog: r8/levels checks and the curve; the tour's tram shot from the shelter |
| `r9/levels` | e72bd69 | 2026-10-23 | Merge branch 'r9/rooftops' into r9/levels |
| `r9/night-ball` | e4fe435 | 2026-10-23 | Night Harbour: a knocked ball that rolls off a boat comes back where Pepper was hit |
| `r9/rooftops` | f15a9e5 | 2026-10-23 | Rooftops beat sheet as built after r9, and the CHANGELOG entry |
| `title/redraw` | 7692685 | 2026-10-22 | Title round 2: Pepper redrawn on her portrait as a Labrador (muzzle, ears, eye, maroon mou |
| `tools/tiled` | a6d809b | 2026-10-22 | Tiled: docs/tiled.md, a guide for drawing levels in Tiled |
| `try/scenery-v2` | aa38be5 | 2026-10-05 | Trial (preview): longer level, road and traffic, decoration rules for houses and trees |
| `ui/hud-v8` | 895d937 | 2026-10-24 | Sky: flat steps instead of dotted dither rows between bands (owner, 24 Oct) |
| `ui/panel-hud` | 7177cf2 | 2026-10-24 | UI: no HUD row under the centred cards; 4 px top margin for every card |
| `ui/review-fixes` | d69c2b4 | 2026-10-24 | UI review fix 7: the HUD score in the 7 px font, smaller than the bone count, right-aligne |
| `ui/title-regrid` | 867e76e | 2026-10-24 | Title: the regridded picture (composite base, regrid logo and plate, Pepper still, paintin |
| `ui/umlaut` | 94c9e38 | 2026-10-24 | UI: Ö is a capital O with its dots above the cap line in all three fonts |

Added night of 12 Nov (fully in main at e560cb4, not made by a night run, left for the owner to delete):

| Branch | Last commit | Date | Subject |
| --- | --- | --- | --- |
| `sfx/07nov-main` | 57440ca | 2026-11-07 | sfx: crack a little quieter (peak 0.40 to about 0.27, in line with the rest) |
