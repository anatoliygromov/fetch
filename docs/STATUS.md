# FETCH! Status

As of Sat 24 Oct 2026, 13:30. Rules: `docs/BIBLE.md`. Decisions: the review board, https://claude.ai/artifact/36whD8obiWsrZc4AvPCdXk.

## Main

- `main` becomes **v0.6** tonight. It is `round1` (9d29233) plus:
  - `art/freefix`, with the approved River Walk building, cafe and gable kept as they were;
  - `art/haze`, with Downtown facades faded at 0.25.
- `r8/art` and `title/pixels` are closed. Kept as reference, not merged.

## Kids' test build (Sat 24 Oct, 13:30)

`preview/night` (53f2b59) = main v0.6 + ui/hud-v8 (every UI screen in the new style, the cleaned and animated title,
the rebuilt logo, speech bubbles, the smooth sky) + ui/title-sheen + art/pilot-oldtown + art/placement + r9/night-ball.
Packed as KIDS TEST 24 Oct/ on the Mac (FETCH_KIDS_TEST_24oct.love, the RG35XX zip, the playtest sheet). QA: PEPPER
UNCHANGED, flow 125/125, Tiled passed, curve T1-T4 PASS, --qa 0 problems on all six levels, physics all pass, the packed
file cleared River Walk on autopilot. Nothing merged into main yet: waiting for the owner after the kids' test.

## Night of 23 to 24 Oct (0 credits, about 1.4M tokens in the tracks, budget 5M)

Pushed, not merged, each waiting for the owner:
- `ui/hud-v8` (961aba3): HUD, pause and tally rebuilt to the owner's three targets; fonts 7, 13 and 17 px on the grid; smooth warm pause dim. Layout QA all pass. Cards: out_ui/card_hud, card_pause, card_tally. Open: title menu, level select and story panels still in the old blue style.
- `art/pilot-oldtown` (d942274): Downtown's Old Town row, all seven houses rebuilt from shared stamped parts (tools/build_oldtown.py). Crisp; flatter than the old row (a shade band and lintels are a cheap second pass).
- `art/placement` (60d0388): placement audit of levels 1 to 3 (docs/placement_audit.md). Fixed: River Walk road under the pier; City Park lamps, play tower post and deck, low bough; Downtown fronts, roof kit and spire built from stamped parts, houses under the floating high road, lamps on their ledges. 17 findings on approved art or design are listed for the owner.
- Aseprite runs in the cloud workspace (headless, scripting), at /home/claude/ase/aseprite/build/bin/aseprite.
- Two unverified drafts found uncommitted in the worktrees were set aside, not merged.

## Tracks running

- **Levels** (a separate session, its own branch off `round1`): the Night Harbour ball bug (ball knocked out at the slipway returns to x 240) and Rooftops length (58 s against 60 to 90 s). It must rebase on the new main before its pull request.

## Waiting for the owner

1. Approve the Aseprite MCP connection.
2. Child playtest, Sat 24 Oct, 20 minutes, on the current build.
3. The gold level art pilots: the red cyclist re-cut and the Old Town house from stamped parts.

## Next 7 days

| Day | Work | Owner's part |
| --- | --- | --- |
| Sat 24 Oct | BIBLE and STATUS in the repo; release Action on main; card script enforces the gates; child test | Yes or no on merges; save the asset-gates skill; play with his daughter |
| Sun 25 to Wed 28 Oct | Two-piece proof through the gates; haze per layer; free fixes; Night Harbour bug and Rooftops length | The board, 30 min a day |
| Thu 29 to Fri 30 Oct | Child test fixes, UI wired in, juice checklist; Aseprite pilot on one Old Town house | Approve or reject the pilot |
| Fri 31 Oct | Merge to main builds a Release; retro with measured rates | Play the build; 15-min retro |

## Credits

- SpriteCook: about 1,078 (before today's spend; none logged today). Ledger: `docs/art_ledger.md`.
- Artlist: about 42,450.

## Open decisions

- UI kit v6: approve, then wire into hud.lua, flow.lua and talk.lua.
- Save the `fetch-asset-gates` skill.
- Title screen route (native grid in Aseprite first).
- Release: commercial-use terms for SpriteCook and Artlist art; Gromov Design AB or personal; a findable name.
- Metro: open wagon or carriage (after the demo).
- Music route (tracker files), later.

How to update this file: rewritten by the producer session at the end of each working session.
