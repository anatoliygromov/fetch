# FETCH! difficulty curve, r7/curve (22 Oct): the tall order passes

The planned order with the tall levels, played in whole-game mode by the eight personas, 10 seeds each:

```
python3 tools/check_curve.py --name tall --order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night --seeds 10 --out /home/claude/out/r7-curve
```

Method: `docs/playtest/method.md`. Targets: T1 sawtooth for kids and parents (no level more than 8 DI v2 points over
the hardest of the next two; the second half at least as hard as the first; the last level at least as hard as the
first), T2 no spot over 35% of a level's failures, T3 Elsa (6) clears every level in at least half her
playthroughs, T4 under 5% lost runs.

## Final result (exit 0: all four targets pass)

| # | Level | DI v2 kids / parents / retro | worst spot (share) | Elsa clears | lost runs | perfect run (`--auto`) |
|---|---|---|---|---|---|---|
| 1 | River Walk | 18.0 / 14.0 / 7.1 | screen 12 (33%) | 90% | 0.0% | 66.3 s (unchanged) |
| 2 | City Park (tall) | 12.6 / 17.6 / 6.4 | 2 Bench and hedge (29%) | 100% | 3.8% | 39.1 s (unchanged) |
| 3 | Downtown (tall) | 11.6 / 18.5 / 7.9 | 4 Bakery row (21%) | 100% | 1.2% | 56.2 s (was 56.6) |
| 4 | Rooftops | 20.0 / 16.5 / 5.8 | screen 9 (30%) | 80% | 1.2% | 58.1 s low road (was 54.1), 54.4 s high road (was 51.8) |
| 5 | Soder Hill | 15.7 / 14.7 / 8.9 | 16 The end (50% of 2: not judged) | 100% | 0.0% | 73.3 s (unchanged) |
| 6 | Night Harbour | 19.2 / 24.7 / 13.7 | 8 Rotten planks (28%) | 90% | 0.0% | 82.6 s (was 81.3) |

- sawtooth kids PASS (first half 14.1, second half 18.3; last 19.2 against first 18.0), parents PASS (16.7 against
  18.6; last 24.7 against 14.0), retro PASS (not judged).
- Chart: `/home/claude/out/r7-curve/curve_tall.png`; raw runs and `curve.json` in `/home/claude/out/r7-curve/`;
  the output: `/home/claude/out/r7-curve/final_curve.txt`.

## How the check reuses runs (caching)

`run_campaign.py` keeps one JSON per persona, seed and level of the order (`runs/<persona>__<seed>__<k>_<level>.json`)
and the clean run per level (`perfect/<level>__perfect__1.json`) and skips any that exist. It does not look at the
level files: after a change the runs on disk are stale. Each iteration below therefore used a fresh `--out`
(`/home/claude/out/r7-curve/iterN/`), copying only the runs of the levels before the first changed one (k 1 and 2:
River Walk and City Park tall never changed) and the perfect runs of unchanged levels. A changed level also changes
what the next levels get (lives, score, controls), so every level from the first changed one on was played again.
The lab is deterministic: the same files give the same numbers (iter6 and the final run are identical).

## Iterations (DI v2 kids / parents; worst spot and its share; Elsa's clears; lost runs)

| iter | change | Downtown (tall) | Rooftops | Soder Hill | Night Harbour | T1 T2 T3 T4 |
|---|---|---|---|---|---|---|
| 0 | round1 as it is | 24.1 / 26.0, Cafe terrace 32%, 60% | 16.0 / 13.3, screen 9 43% | 9.6 / 7.3 | 15.1 / 23.4, slipway 26% | F F P P |
| 1 | DT: terrace parasol 8 px lower, the second wider; the springy plaza parasol (32 px up) to the loggia | 26.1 / 19.6, 31%, 60% | 14.8 / 13.3 | same | same | F F P P |
| 2 | DT: both parasols at 362 (walk across), sign 8 px lower; crate steps (bakery, way up A); flooded square parasol lower | 20.9 / 30.3, 24%, 78% (Anna quit 6 of 10) | 14.4 / 13.3 | same | same | F F P P |
| 3 | DT: the bakery crate dropped (she lands under that awning, never before it), way up A crate at 400; RT: drying yard v1 (run over loose tiles, a stack vent) | 20.5 / 27.3 | 14.2 / 13.0, screen 9 40% (the new screen took 3 failures) | same | same | F F P P |
| 4 | DT autopilot: let go of Right only once off the sign and the awning, two taps onto the stall; plaza parasol 20 px (a tap reaches it); RT: drying yard v2 (loose-tile staircase, 96 px well with a fan); SD: third barrel; NT: slipway boats faster, narrow slipway plank, back over two planks | 11.6 / 18.5, Bakery row 21%, 100% | 19.0 / 22.6, 31%, Elsa 80%, **lost 11.2%** (the well) | 15.7 / 14.7 | 28.9 / 48.1, **slipway 58%**, Elsa 70% | P F P F |
| 5 | RT: the well 40 px deep, no fan (she scrambles out); NT: first slipway boat back to 26 px/s, rotten planks 24 px wide | same | 20.0 / 16.5, screen 9 30%, lost 1.2% | same | 28.2 / 40.2, slipway 40% | P F P P |
| 6 | NT: the slipway plank back to 32 px | same | same | same | 19.2 / 24.7, rotten planks 28%, Elsa 90% | **P P P P** |
| final | RT hint text HOLD: BIG JUMP (flow check); whole order again on the committed tree | same | same | same | same | P P P P |

## Reading it

- **Downtown (tall)** was the spike because two careful players quit: Anna (patience 3) and Elsa (patience 4) at
  the held jumps of the terrace, the statue climb with the ball and the stall. Half of those quits were the bot
  stopping short on the edge of the shop sign or the market awning (its "let go" came early and it stood there): the
  autopilot now lets go once she is off the edge. With the springy parasol at the plaza the climb with the ball is
  one bounce (the level's own idea, bounce then carry); the statue climb stays for the STATUE HAT.
- **Rooftops** rises from 16 / 13 to 20 / 16.5 with one screen: the drying yard's three held jumps up two loose
  tiles. Its new failures (screen 11) dilute the goose (screen 9, 43% to 30%). A first version (run over loose
  tiles, a stack vent) added 3 failures in 80 runs: running and riding puffs are what every persona does well.
  A 96 px well with a fan in it lost 11% of the runs (the bot could not find its way out of the well), so the dip is
  40 px deep and she scrambles out.
- **Soder Hill** (9.6 / 7.3 to 15.7 / 14.7): its DI is hearts per minute; the third barrel stack adds hearts for
  everyone but Mikael. Still almost no failures (the chase carries the bot on), so its worst spot is noise.
- **Night Harbour** is the hardest level for parents (24.7) and the last level is at least as hard as the first for
  kids (19.2 against 18.0), but for kids Rooftops (20.0) is a hair harder. The slipway is the lever with the most
  bite and the least spread: tightened, it took 40 to 58% of the failures (T2), so the extra difficulty sits in the
  rotten planks (screen 8) and the way back instead.

## What is left

- Night Harbour for kids: 19.2, under the 25 to 30 asked for. Next lever: a second fair beat in the second half
  (screen 12 or 13: a plank, a boat and a hop in the boat's light), not the slipway's first jump alone.
- Rooftops' perfect run is 58.1 s (asked: 90 to 110 s). One screen of held jumps adds 4 s for the autopilot. Getting
  to 90 s needs about three more screens or puffs that make the clean run wait; DI is at 20 / 16.5 (asked 22 to 28).
- `--qa` on Night Harbour: 1 problem in 8037 ball-sweep runs (0 on round1): hit from the left at the quay's very
  edge before the slipway (x 3812) while carrying, the ball splashes and goes back to x 240 (the level's ball start)
  because no lamp is lit in the sweep's stage. It is the r6 safety net's fallback; in play the lamp at x 3760 is lit
  by then. The change of timing comes from the new planks (the sweep reaches that spot at another moment of the
  boats' rowing). Left for the engine owner.
- 10 seeds per persona; parents are two personas, so one quit moves their DI by 2.5.
