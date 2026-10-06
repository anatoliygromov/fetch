# FETCH! playtest lab: method

What the synthetic playtest measures, how the persona bots play, and what is approximated. Read this before trusting a
number in summary.md. Code: `riverwalk/playtest.lua`, `pt_bot.lua`, `pt_routes.lua`, `pt_log.lua`, `pt_json.lua`;
`tools/run_playtest.sh`; `tools/analyse_playtest.py`. Personas: `docs/playtest/personas.json`.

## In one paragraph

The real game runs headless (LÖVE 11.5, the real `stage.lua`, `pepper.lua` and level files, 1/60 s fixed steps, no
drawing). A bot drives Pepper through the same button interface the autopilots use (`I.force` for held buttons,
`love.keypressed` for presses). The bot follows each level's autopilot route, but every press goes through a persona
layer: timing jitter, reaction delays, hold errors, knowledge of the controls, trying buttons to find a control,
retrying after failures and quitting when patience runs out. Everything the game does in response (jumps, falls,
the magpie, the cat, bikes, the timer, hearts, respawns) is the real game. The numbers are therefore measured on the
real game for a modelled player: the game side is exact, the player side is a model, documented below.

## Measured exactly (the game decides)

- Physics and collisions of every jump, landing, scramble, crawl and fall; whether a press of a given length at a
  given spot reaches a ledge.
- Hazards: when bikes, the leaf cart and the tram spawn and whether they hit Pepper; the moving boat and pontoon.
- The magpie (City Park): it flees perch to perch by the game's own rule (110 px from a running Pepper, 40 px from a
  walking one) and drops the ball when a bark lands within 95 px. The cat (Downtown) by its own rule.
- Hearts, lives, drowning, the game's own respawn at the last lit lamp, TIME UP, GAME OVER.
- Bones and gold bones collected, lamps lit, hints and messages shown (and when a message hides a hint).
- Game time (play time at 1/60 s per step, the same in every run; independent of how fast the machine is).
- The event log (`pt_log.lua`): it only watches the game after each step, so it also rides along with the real
  autopilot (`--auto --log`) for the clean pacing baseline.

## Modelled (the persona layer, `pt_bot.lua`)

Persona parameters come from `personas.json`; the few extra numbers below are assumptions, stated here.

- **Route.** Each level's autopilot step list, copied into `pt_routes.lua` (the autopilots and their `--auto`
  runs are untouched; the Pepper golden trace still matches). Changes from the autopilot, each marked in the file:
  the City Park climbing frame, the Downtown sign and awning, the River Walk quay before the pontoon and the statue
  hat: the autopilot stops with 2 to 4 px to spare, which no person aims for, so the bot brakes in the air or stops a
  few pixels earlier; moving platforms are timed (see timing); River Walk got a "wait for a bike that is coming" on
  the last perch of each bike zone (City Park and Downtown already wait for the cart and the tram). The bots never
  invent routes: bones that no route passes are never collected, so bones % is capped by the routes (autopilot
  a perfect bot taking every optional part: 37/40, 37/40, 45/46).
- **Optional parts.** City Park: the oak (gold bone), the climbing frame (bones; with the ball in her mouth it is
  optional, without it everyone climbs because the magpie's last perch is there). Downtown: the parasols and the
  shop sign (gold bone; skipped = crawl under the tables as the hint says), the market awnings, the statue's hat
  (gold bone). Each is taken with probability `explore`; `rush` skips them all (Downtown cafe: Mikael hops table to
  table instead of crawling). A persona who fails an optional part `patience` times gives it up, not the level.
- **Timing.** A positional press (jump at x) lands N(0, `timing_sd_ms`) early or late; early presses are modelled
  by checking the step's condition on where Pepper will be (x + vx * lead). A reactive step (waiting for the ball to
  drop, for the cart or tram to pass, to bark at a perched bird, to press X at the ball) waits `reaction_ms` +
  N(0, timing_sd) first. Moving platforms (duck boat, pontoon) are anticipated: people see them coming, so the start
  is timed on where the platform will be when Pepper gets to the edge (no reaction delay, the timing jitter only).
- **Hold errors.** With chance `hold_error` a held jump comes out as a short press (A let go after 60 to 160 ms:
  24 to 29 px instead of 46) and a tap as a held jump (0.3 to 0.45 s).
- **Knowledge.** A control is known if the persona can read a text that teaches it: reads=all: the intro card,
  every hint and message; reads=short: hints and messages of 4 words or less (5 of the 33 hints in the three levels qualify: RIDE THE DUCK BOAT, TRAM! GET UP HIGH, BIKES! GET UP HIGH twice, RIDE THE PONTOON); reads=
  none: nothing. Text-to-control table (same in the bot and the analysis): HOLD A = held jump, HOLD B = sneak, BARK =
  bark, CRAWL = crawl, X: / PICK UP = X, RIDE THE ... = wait for the platform, LEAF CART / TRAM! / BIKES! = wait the
  hazard out on a perch. Assumption: a reader who reads "BARK" finds the bark button at once.
  Campaign mode (the main grid): a level starts knowing what the levels before it needed (the level select only
  opens a level after the one before it is cleared); waiting for one hazard or platform carries over to the next
  kind. Fresh mode (`--fresh`, a separate table): levels 2 and 3 without that.
- **Not knowing a control.** Not knowing held jump, every jump is a short press; not knowing crawl, Down is never
  held; not knowing sneak, B is never held; not knowing a wait, the bot goes without waiting. When that makes the
  route fail at an obstacle (stuck, in the water), the persona tries buttons there for a discovery time (gamma with 2
  degrees, mean `discovery_s`) with real random presses (left / right, A short or held, B, Y, Down, X; they avoid
  walking into water or off an edge they can see, within 24 px of where they started; X is not pressed while carrying the ball once they know X drops it), then knows it
  and retries. Bark and X are needed at a target (the bird, the cat, the ball, the girl): there the trying starts at
  once and ends early when a random press works (a bark in range drops the ball). Waits are learnt by the failure
  itself (falling in, being hit), without trying buttons. A bark that works by chance teaches the bark.
- **The magpie.** A persona who knows sneak walks up to a perched magpie (from up to 200 px, on the path) and
  barks 70 to 85 px away. One who does not runs on with the route: the real magpie flees; the first flight starts a
  background clock (a discovery time) after which sneak is known, and from then on they sneak at the next perch
  they reach on the path. At the last perch (the climbing frame) the bird stays and everyone barks there. Elsa's fun
  barks (one per 10 s on average, from her bio) and Liam's (one per 20 s) are real presses and can drop the ball.
- **Failures and retries.** Stuck = a step's condition not met in 1.5 x its autopilot time limit, pushing against
  something for 1.5 s, or standing still for 2.5 s outside a wait; a missed jump onto a box (River Walk perches); the
  game's own respawns (water, a life lost, TIME UP). Before calling it stuck the bot checks whether a later
  obstacle's start already holds (she hopped over the log instead of onto it) and goes on from there without a
  retry. A retry backs up to where the obstacle began if that is on the same floor (real walking, real time);
  otherwise Pepper is put back at the last lit lamp (the game's own respawn function), with 1 s of walking per 120 px
  added to the approximate time, and the route restarts at the first obstacle ahead of that lamp after a short
  run-up. Every retry counts at its obstacle; at `patience` failures at one obstacle the persona quits there
  (Anna and the kids quit, the adults would ask for help: the same number). A GAME OVER restarts the level and
  counts as a failure at that spot. Session cap: 600 s of play for Elsa (her bio: she plays 10 minutes), 1200 s
  for the others.
- **No learning of technique.** The bot does not slow down or change how it does a jump after failing it. At the
  few precision spots (the stepping stones, the hat, the bin with a short press) this makes repeat failures somewhat
  more likely than for a real player.
- **Cards.** The intro card: reads=all read the two story lines (1 s + 0.25 s per word for adults, 0.4 s for Maja),
  others press after 0.8 to 1.2 s, Mikael after 0.6 s. The tally: until it has counted up, plus a reaction. The story
  card between levels is not shown in a single-level run; its time is estimated the same way as the intro and
  reported apart (`story_card_est`).

## Approximated (reported separately as approx_time)

- **Fetching the ball where the route does not go.** The ball can land off the route (the magpie dropped it on the
  oak's low left branch, the ball came back to an earlier lamp after a fall in the pond, it is behind Pepper on a
  higher level). Then the human cost is computed, not played: 2 x (horizontal + vertical distance) / 100 px/s, two
  reactions, 0.8 s per 30 px climb, each climb jump failing with chance `hold_error` (0.7 if the held jump is not
  known yet) at 1.5 s per failure; at `patience` failures the persona quits there. Pepper is then given the ball
  where she stands, and the cost is taken off the level timer. Where the ball lies on Pepper's floor within 160 px,
  the bot really walks to it and presses X.
- **Walking back to a lamp** after a stuck retry that could not back up on foot: distance / 120 px/s.

## Metrics (tools/analyse_playtest.py)

- Completion % = runs ending in GOOD GIRL! (`result = clear`); quit points: obstacle, screen, cause.
- Time to clear: game time of the clears (median, p25 to p75); total = play + intro card + tally + estimated story
  card + approximated time.
- Hearts lost: every heart the game takes (water, bike, cart, tram); a TIME UP is a life, counted under lives.
- Retries: the bot's failure count (stuck, missed jump, water, life lost), per obstacle.
- Waiting / idle: Pepper standing still for more than 1 s while playing, labelled by what the bot was doing
  (waiting for a platform or hazard, reacting, trying buttons, sneaking up to the magpie, fetching, backing up).
- Bones %, gold bones per run; mechanics found by trying (runs, median seconds of trying); the magpie: time of the
  drop, flights before it, the perch; the cat: seconds from the "BARK AT THE CAT" hint to the cat scared and to the
  ball picked up.
- Pacing: events per 10 s of play (bones, lamps, hints, hazards, story beats, first use of a mechanic, scrambles,
  hearts) in the autopilot's clean run and the median over the persona clears; the longest stretch with none.
- Taught before tested: the first text that teaches a mechanic in the clean run and who can read it, against where
  the level first really needs it (positions from the level files, listed in `NEED` in the analysis), and how many
  persona runs failed at that spot. Which hints a clean run never shows (a message covers the banner).
- Hazard first encounter: share of runs losing a heart to the first bike / cart / tram they meet; seconds from its
  spawn to reaching Pepper's x.

## Pictures

All frames are real frames of real runs: the runs are deterministic for a persona, level, seed and mode, so the
analysis picks the moments from the event logs and a second run of the same seed draws and saves exactly those
steps (`--capture-steps`). 640 x 480 = the 320 x 240 game at 2x, nearest neighbour. `frames_<level>.png`: the clear
closest to the median time of all clears; `fail_<level>_<n>.png`: the three obstacles with the most retries + hearts
+ 5 x quits, from the persona with the most failures there (before, during, after); `timeline_<level>.png`: events
per 10 s and the event strips of the autopilot and of each persona's median run.

## Limits

Eight personas are eight parameter sets, not eight people: the spread across seeds is the spread of the model.
The route is fixed: a bot never explores a different line, looks around, or gets distracted (except Elsa's and
Liam's fun barks). Reading speed, the discovery model and the 4-word rule are assumptions. Use the numbers to compare
spots, levels and personas with each other, and the pictures to see what happens; check anything surprising by
playing it.
