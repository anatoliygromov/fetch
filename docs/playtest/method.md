# FETCH! playtest lab: method (22 Oct, r4/playtest)

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
- **Lost runs** (the lab's own limit): after 3 failures in a row at one spot the lab makes one try with the
  autopilot's exact buttons. If even that fails, the route cannot be picked up from where the person's mistake left
  the game (the ball, a critter or a boat is somewhere the route does not expect): the run ends as `lost` and is
  left out of the difficulty index. If the clean try passes, the run goes on (this helps patient personas a little).
- **Exploration.** Rooftops: the high road with chance `explore` (never when `rush`). Elsewhere the route is the
  autopilot's: bones and secrets are what that route takes, less what failures cost.
- **Waits.** Forced waiting = the autopilot holding nothing while Pepper stands, in stretches of 1 s or more.
- **Stalls.** Seconds trying controls, recovering, or standing still while the route goes on, per 32 px cell.

## Metrics (tools/analyse_playtest.py)

Per persona per level: clear rate, quit rate and where, hearts and lives lost, game overs, clear time (median, p90),
time over the perfect run, waits, bones %, secrets, controls found (read or tried, trying time), failures per spot.
Difficulty index: DI = 50 x quit rate + 10 x hearts lost per minute + 5 x failures at the worst spot (mean, capped
at 6) + 5 x (median clear time / perfect clear time - 1, capped at 5); a group's DI is the mean of its personas.
Also on all runs (lost ones up to where they were lost): failures and hearts per minute, share of the route done.

## Limits

Eight personas are eight parameter sets. The bots do not learn technique, do not wander off the route, and do not
press random buttons while trying. Where a critter or the ball can end up off the scripted path (the magpie, the cat,
the fox) the lab loses runs; the report gives the lost count per level. Compare levels and spots with each other,
and check anything surprising by playing it.
