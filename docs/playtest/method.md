# FETCH! playtest lab: method (22 Oct, r4/playtest; recovery v2, whole-game mode, DI v2 and the acceptance test: r6/lab)

What the synthetic playtest measures, how the persona bots play, and what is a model. Read this before trusting a
number in a report. Code: `riverwalk/playtest.lua`, `riverwalk/pt_bot.lua`, `riverwalk/pt_json.lua`;
`tools/run_playtest.py`; `tools/analyse_playtest.py`. Personas: `docs/playtest/personas.json`.

## In one paragraph

The real game runs headless (LOVE 11.5, the real level files and every game module, 1/60 s fixed steps, no drawing,
600 steps per frame). The level's own autopilot (`tests_<level>.lua --auto`, the same one the checks use) plays,
reading the real game state and deciding what to press. The lab stands between the autopilot's buttons and the game:
everything the autopilot presses goes through a persona layer (reaction delays, early and late presses, hold errors,
controls that must be found first, failures, recovery, patience). So the routes are always today's routes: when a
level changes, its autopilot changes, and the lab follows. **The game side is exact; the player side is a model.**

## How it hooks in

`love riverwalk --level <name> --auto --playtest <persona> --seed <n> --out <file>`. `main.lua` gains one line: with
`--playtest` it loads `playtest.lua` after the autopilot. Nothing in the game changes: no level, map, stage, world,
camera, lift, roof, critter, set piece, Pepper or art file. The lab only:
- reads and sets the autopilot runner's own variables (`steps`, `i`, `since`, `old`) through Lua's debug library;
- gives the autopilot its wanted buttons (`I.force` as the autopilot sets it) and the game the persona's buttons
  (`I.force` read inside the game step); presses (`love.keypressed`) are queued the same way;
- wraps `St.respawn` and `St.loseHeart` to count (they still do exactly what they did);
- turns off screenshots and printing. Rooftops' high road: `AUTO_ROUTE=high`, the autopilot's own switch.
The `perfect` persona is the autopilot through the same layer with no errors: it must clear every level as `--auto`
does (City Park 44.2 s), which proves the layer adds nothing by itself.

## Measured exactly (the game decides)

Physics and collisions of every jump, landing and fall; whether a press of a given length at a given spot works;
every hazard, critter and moving platform (bikes, carts, trams, geese, gulls, the magpie, the cat, the fox, barrels,
boats, lifts, steam puffs, loose tiles); hearts, lives, TIME UP, GAME OVER, the game's own respawn at the last lamp;
bones, secrets, hints on screen; game time.

## Modelled (pt_bot.lua)

- **Timing.** Each autopilot step that waits for a place on the route (its condition reads only Pepper) gets a
  timing error N(0, `timing_sd_ms`): early presses are made by letting the autopilot see Pepper `x + vx * error`
  ahead; late ones are queued. Stopping (letting go of a direction) is never late: people stop short, not long.
- **Reactions.** A step whose condition reads the world (a boat, a tram, the ball, a critter) and that fires after
  Pepper has stood still for 0.3 s or more is a reaction: delay `reaction_ms` + N(0, `timing_sd_ms`).
  Everything an autopilot does in the same action keeps its spacing (the same delay).
  Soder Hill's autopilot is one reactive loop: each of its presses gets a fresh timing error.
- **Hold errors.** With chance `hold_error` a held jump is let go after 60 to 160 ms (a hop), or a tap is held for
  0.3 to 0.45 s.
- **Knowing the controls.** Texts on screen teach: reads=all every hint, reads=short hints of 4 words or less,
  reads=none nothing. Keywords: BIG JUMP / CLIMB = held jump, CRAWL / DUCK = crawl, BARK / SHOO = bark, PICK UP /
  GIVE = X, SNEAK = walk, SNIFF = sniff. The first time the route needs a control the persona does not know (bark,
  X, walk, sniff, crawl) the persona stands for a trying time, gamma with 2 degrees and mean `discovery_s`, then knows
  it. Not knowing the held jump: every held jump comes out as a hop until the first failure, then the trying time.
  Each run starts knowing nothing; the analysis takes off trying time for controls found on earlier levels of an
  order (campaign adjustment, per order).
- **Failures.** The autopilot's step not done in 1.5 x its own time limit (stuck), any game respawn (water, a fall,
  a life, TIME UP), or a GAME OVER (TRY AGAIN: the level from the start). Each is counted at the step it happened
  (its spot = where that step was first entered, named by the beat sheet's screen).
- **Recovery** (the bot never freezes): after a stuck, Pepper walks back (on foot, hopping over anything in the way)
  to the latest earlier step on the same floor that is at least 40 px before the failing one, and the route goes on
  from there with the buttons the autopilot held then. If there is none, the game's respawn puts her at the last lamp
  and she stands for the walk back (distance / 120 px/s, 1 to 6 s). After a game respawn she waits out the respawn,
  fetches the ball if she was carrying it and it came back nearby (walks to it, presses X), then goes to the
  earliest-nearest step before the failure and on along the route.
- **Patience and quitting.** At `patience` failures at one spot the persona quits there. Session cap: 600 s of play
  for Elsa, 1200 s for the others (counted as quits).
- **Recovery v2** (r6/lab; replaces the paragraph above when the clean run's route map is given, which
  `run_playtest.py`, `run_campaign.py` and `check_curve.py` always do; `--recovery v1` gives the old bot). The clean
  run (`perfect`) records a **route map**: for every autopilot step, where it was first entered (x, y, on the ground
  or not, on a boat or lift or not, speed, the buttons held, whether a button was pressed as it began) and the
  **world sig** then: the ball (in her mouth, with the magpie / cat / fox, loose, given), the magpie's perch while
  it has the ball, the fox's hideout, the cat sitting or not; and the x range and lowest floor the step ran over.
  - *Off the route*: Pepper stands for 0.3 s more than 72 px to the side of where the clean run ran during this
    step, or 20 px below the lowest floor it stood on (she missed a jump and ran on below, or past the place the
    step waits for): a failure (`offroute`) at this step, then recovery. (Before, the held direction carried her on
    until the step timed out, often into water far away: the main cause of lost runs.)
  - *Picking the route up* (after a stuck, an offroute or the game's respawn; first she settles: off boats and lifts,
    on the ground, the respawn and the ball's way home over): (1) the ball lies loose within 480 px (and 64 px up or
    down): fetch it (walk, turn, hop what is in the way, X); (2) the magpie has the ball on
    a perch the clean run never saw it on: sneak (if she knows how) up to bark range and bark; (3) the steps whose
    clean entry is on her floor (|dy| < 10, within 480 px), with the same world sig (the magpie may be further along
    than the step saw it), where the clean run stood still or ran on (not mid-jump, not on a mover, not the frame
    a button was pressed, not coasting on its speed with no direction held): after a stuck the nearest one at or behind her (with a 32 px run-up if the clean run was
    running there); after an offroute or a respawn the nearest either way (ahead counts 1.5 times its distance).
    She walks there (hopping what is in the way; 8 s at most) and the autopilot goes on from that step with the
    clean run's buttons; (4) nothing on her floor: the ball lies loose elsewhere (it went home after a fall): she
    walks back to it; else she walks to the nearest step with the same sig anywhere. The lab moves her there with
    the game's own respawn (`St:respawn` with the spot as the lamp) and she stands for the walk, distance / 120
    px/s, at most 20 s (`lab_walks`, `lab_walk_s` in each result; the dangers on the way back are not played);
    (5) the nearest step anywhere, from where she stands. Soder Hill's reactive autopilot picks itself up.
  - A step she keeps leaving gets a wider margin (72 px more for each offroute there, at most 288 px), so a step
    whose clean run stood still (a goose, the ball) does not trap her in a loop. A step that raises an error when
    picked up out of sequence (it needed the step before it, Rooftops' vent rides) counts as a stuck and is never
    picked again.
  - Its spots: failures in a reactive autopilot (Soder Hill: one step) are counted per screen, not per step.
  - The clean try that decides a lost run (below) only proves the route lost when it ends stuck or off the route;
    if the game's hazards end it (a respawn, GAME OVER) it proves nothing and may be tried again later.
- **Lost runs** (the lab's own limit): after 3 failures in a row at one spot the lab makes one try with the
  autopilot's exact buttons. If even that fails, the route cannot be picked up from where the person's mistake left
  the game (the ball, a critter or a boat is somewhere the route does not expect): the run ends as `lost` and is
  left out of the difficulty index. If the clean try passes, the run goes on (this helps patient personas a little).
- **Exploration.** Rooftops: the high road with chance `explore` (never when `rush`). Elsewhere the route is the
  autopilot's: bones and secrets are what that route takes, less what failures cost.
- **Waits.** Forced waiting = the autopilot holding nothing while Pepper stands, in stretches of 1 s or more.
- **Stalls.** Seconds trying controls, recovering, or standing still while the route goes on, per 32 px cell.

## Whole-game mode (tools/run_campaign.py)

A persona plays the levels of an order as one playthrough (one LOVE process per level, `--carry` hands on):
- **lives and score** as in the real flow: a cleared level passes its lives and its tally score (time bonus
  included) to the next level, as `St.new(def, { score, lives })` does (the lab sets those fields on the fresh stage).
  GAME OVER inside a level follows the real rule: TRY AGAIN restarts the level with 3 lives and the score it started
  with. The FETCH FRENZY bonus round is not played (no extra lives from it).
- **controls**: a control found (by trying, or read in a hint the persona can read) is known for the rest of the
  playthrough: its trying time is paid once. A hint whose button glyph was on screen (seen; for a reader or not)
  for a control not yet known halves its trying time (mean `discovery_s` x 0.5): the glyph says which button.
- a level not cleared (quit, session time, lost) ends there; the playthrough goes on at the next level as LEVEL
  SELECT starts a run (3 lives, score 0), as if a helper got them past it (`fresh` in its `carry_in_full`).
- per-level metrics are recorded inside the run (one JSON per level; `k` = its place in the order).

## Metrics (tools/analyse_playtest.py)

Per persona per level: clear rate, quit rate and where, hearts and lives lost, game overs, clear time (median, p90),
time over the perfect run, waits, bones %, secrets, controls found (read or tried, trying time), failures per spot.
Difficulty index: DI = 50 x quit rate + 10 x hearts lost per minute + 5 x failures at the worst spot (mean, capped
at 6) + 5 x (median clear time / perfect clear time - 1, capped at 5); a group's DI is the mean of its personas.
Also on all runs (lost ones up to where they were lost): failures and hearts per minute, share of the route done.

## Difficulty index v2 and the acceptance test (tools/check_curve.py)

DI v1 (above) stays for comparison. On a level played first, much of v1 is learning: standing while trying buttons
adds to the clear time, and a held jump that comes out as a hop until it is found is a failure at a spot. DI v2
separates learning from failing: the same four terms and weights, but the trying time is taken out of the play minutes
(hearts per minute) and out of the clear time (time over the clean run, never below 0), and a failure that taught a
control (the hop that should have been a held jump) is not counted at its spot. The learning seconds (median trying
time per run) are reported on their own, per level and group.

`check_curve.py --order a,b,c` runs whole-game mode for all eight personas (`--seeds`, default 20) and judges:
- **T1 sawtooth** (on DI v2, per group; kids and parents judged, retro reported): (a) no spike: every level is at
  most X = 8 DI points harder than the hardest of the next two levels (a dip is fine, a level that towers over what
  follows is not); (b) it climbs: the mean DI of the second half of the order is at least the first half's (the
  middle level of an odd order counts in neither), and the last level is at least as hard as the first.
- **T2 spots**: no spot (a beat-sheet screen, else a 320 px screen) has more than 35% of a level's failures (all
  personas, runs the lab kept; a level with fewer than 20 failures passes).
- **T3 Elsa**: Elsa (6) clears every level in at least 50% of her playthroughs.
- **T4 lost runs**: under 5% on every level.
Exit code 0 when all four pass. `--x`, `--spot-max`, `--elsa-min`, `--lost-max`, `--groups` change the targets.

## Limits

Eight personas are eight parameter sets. The bots do not learn technique, do not wander off the route, and do not
press random buttons while trying. Recovery v2 picks the route up from where a mistake left Pepper and
the world, but the walk back to a far ball or step is timed, not played (`lab_walks`). Compare levels and spots with each other,
and check anything surprising by playing it.
