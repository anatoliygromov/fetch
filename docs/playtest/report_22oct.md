# FETCH! synthetic playtest, 22 Oct: is the level order progressive?

## The answer

**No, not yet.** In the proposed order (City Park, River Walk, Downtown, Rooftops, Soder Hill, Night Harbour) the
difficulty goes down, up, down, down, up for the kids and the parents. Three things cause it:

1. **River Walk is the easiest level in the set** for every group (difficulty index 21 / 19 / 7 for kids / parents /
   retro), and it comes second, after a first level that is two to three times harder.
2. **Level 1 is a spike, whichever City Park you pick.** City Park scores 48 / 57 / 14, the tall City Park 52 / 48 /
   18. Neither is a gentle first level for Elsa (6) or Anna (38): Elsa clears City Park in 33% of runs and the tall
   one in none; Anna clears 5% and 20%.
3. **Downtown (level 3) is the hardest level before the finale** (59 / 47 / 18) and harder than the two levels after
   it (Rooftops 25 / 31 / 22, Soder Hill 16 / 10 / 24). Night Harbour then climbs again (38 / 45 / 10).

For the retro players every level is easy (7 to 24) and the order is flat with small bumps: Soder Hill is their
hardest level (Mikael, who never waits, runs into the barrels) and Night Harbour their easiest.

**Candidates.** Level 1: neither is gentle; City Park is the better first level for the kids (Elsa 33% clears vs 0%,
kids index 48 vs 52), the tall one is a little kinder to the parents (48 vs 57) but asks for a held jump on screen 2
before any text teaches it (Anna had to find it by trying in 19 of 20 runs). Keep **City Park** as level 1 and fix
its two spots below. Level 3: **Downtown** clearly beats Downtown (tall), which is harder for kids and parents
(70 / 70 vs 59 / 47; clears 33% / 25% vs 50% / 52%).

**River Walk at 2 or at 3?** By the same index the current order (Downtown 2nd, River Walk 3rd) is smoother: the
sum of the drops along the order is 43 for kids and 57 for parents, against 73 and 75 for the proposed order. But
neither order is progressive, because City Park and Downtown are both harder than everything after them except
Night Harbour. The real fix is to soften City Park and Downtown (fixes 1 to 4 below); after that River Walk works at 2.

## The numbers

Difficulty index (DI) per level and group, as each level plays when it is the first one played (no controls known
in advance). Higher is harder. Clear rates are on the runs the lab kept; failures per minute on all runs.

| Level | DI kids | DI parents | DI retro | clear % kids / parents / retro | failures per minute kids / parents / retro | runs the lab lost |
|---|---|---|---|---|---|---|
| City Park | 48 | 57 | 14 | 58 / 39 / 96 | 2.8 / 3.6 / 2.5 | 49 of 160 |
| City Park (tall) | 52 | 48 | 18 | 62 / 60 / 100 | 3.8 / 3.6 / 2.9 | 66 of 160 |
| River Walk | 21 | 19 | 7 | 93 / 85 / 100 | 1.4 / 1.2 / 0.8 | 5 of 160 |
| Downtown | 59 | 47 | 18 | 50 / 52 / 100 | 3.6 / 3.4 / 2.7 | 83 of 160 |
| Downtown (tall) | 70 | 70 | 14 | 33 / 25 / 100 | 3.6 / 3.4 / 2.7 | 101 of 160 |
| Rooftops | 25 | 31 | 22 | 100 / 88 / 100 | 1.1 / 0.9 / 1.6 | 54 of 160 |
| Soder Hill | 16 | 10 | 24 | 100 / 100 / 100 | 0.6 / 0.0 / 0.7 | 34 of 160 |
| Night Harbour | 38 | 45 | 10 | 67 / 52 / 100 | 3.3 / 3.6 / 4.3 | 133 of 160 |

**The formula.** Per persona per level: DI = 50 x quit rate + 10 x hearts lost per minute played + 5 x failures at
the run's worst spot (mean, capped at 6) + 5 x (median clear time / the autopilot's clear time - 1, capped at 5). A
group's DI is the mean of its personas (kids: Elsa 6, Liam 8, Maja 10; parents: Anna 38, Johan 41; retro: Mikael
37, Sara 34, Tomas 44). In an order, a control found by trying on an earlier level is known, so its trying time comes
off the clear time; that changes little (the order charts show it).

**Runs.** 8 personas x 8 levels x 20 seeds = 1,280 runs, plus the clean autopilot runs (Rooftops on both roads),
all on the real game. Rooftops: each run takes the high road with the persona's explore chance (Sara always, Mikael
never). "Runs the lab lost": after three failures in a row at one spot the lab tries once with the autopilot's
exact buttons; if even that fails, the bot (not the player) has lost the route there, and the run is left out of the
DI. Those runs are not quits; see the caveats.

Per persona (clear % / quit % / median clear time / hearts lost per run / DI):

| Persona | City Park | City Park (tall) | River Walk | Downtown | Downtown (tall) | Rooftops | Soder Hill | Night Harbour |
|---|---|---|---|---|---|---|---|---|
| Elsa 6 | 33 / 67 / 282 s / 0.0 / 77 | 0 / 100 / - / 1.5 / 101 | 79 / 21 / 223 s / 3.5 / 44 | 0 / 100 / - / 0.0 / 95 | 0 / 100 / - / 0.0 / 95 | 100 / 0 / 206 s / 3.8 / 29 | 100 / 0 / 163 s / 6.8 / 31 | 33 / 67 / 164 s / 2.0 / 63 |
| Liam 8 | 56 / 44 / 82 s / 1.0 / 48 | 88 / 12 / 120 s / 0.9 / 34 | 100 / 0 / 76 s / 1.1 / 13 | 50 / 50 / 222 s / 0.0 / 63 | 0 / 100 / - / 0.0 / 105 | 100 / 0 / 143 s / 3.9 / 30 | 100 / 0 / 92 s / 1.2 / 9 | all lost |
| Maja 10 | 85 / 15 / 69 s / 0.2 / 21 | 100 / 0 / 105 s / 1.1 / 23 | 100 / 0 / 67 s / 0.6 / 6 | 100 / 0 / 159 s / 0.0 / 19 | 100 / 0 / 100 s / 0.0 / 9 | 100 / 0 / 93 s / 1.6 / 16 | 100 / 0 / 81 s / 1.2 / 9 | 100 / 0 / 151 s / 0.0 / 14 |
| Anna 38 | 5 / 95 / 135 s / 1.8 / 83 | 20 / 80 / 107 s / 1.8 / 73 | 70 / 30 / 68 s / 1.2 / 31 | 5 / 95 / 170 s / 0.8 / 76 | 0 / 100 / - / 0.0 / 90 | 75 / 25 / 124 s / 3.6 / 41 | 100 / 0 / 101 s / 1.4 / 10 | 5 / 95 / 151 s / 1.1 / 75 |
| Johan 41 | 73 / 27 / 69 s / 0.5 / 31 | 100 / 0 / 105 s / 1.1 / 23 | 100 / 0 / 67 s / 0.6 / 7 | 100 / 0 / 139 s / 0.0 / 18 | 50 / 50 / 89 s / 2.0 / 51 | 100 / 0 / 77 s / 2.5 / 20 | 100 / 0 / 82 s / 1.3 / 9 | 100 / 0 / 156 s / 0.0 / 15 |
| Mikael 37 | 100 / 0 / 121 s / 0.0 / 15 | 100 / 0 / 107 s / 0.1 / 16 | 100 / 0 / 138 s / 0.2 / 11 | 100 / 0 / 117 s / 0.1 / 13 | 100 / 0 / 135 s / 0.0 / 13 | 100 / 0 / 84 s / 1.9 / 16 | 100 / 0 / 213 s / 12.0 / 55 | 100 / 0 / 162 s / 0.0 / 10 |
| Sara 34 | 100 / 0 / 64 s / 0.0 / 6 | 100 / 0 / 89 s / 0.6 / 16 | 100 / 0 / 67 s / 0.3 / 4 | 100 / 0 / 156 s / 0.0 / 21 | 100 / 0 / 120 s / 0.0 / 12 | 100 / 0 / 145 s / 1.8 / 27 | 100 / 0 / 81 s / 1.1 / 8 | all lost |
| Tomas 44 | 87 / 13 / 67 s / 0.3 / 19 | 100 / 0 / 106 s / 0.8 / 21 | 100 / 0 / 67 s / 0.6 / 6 | 100 / 0 / 175 s / 0.0 / 19 | 100 / 0 / 146 s / 0.0 / 17 | 100 / 0 / 128 s / 1.9 / 23 | 100 / 0 / 85 s / 1.2 / 9 | all lost |

The clean autopilot clears: City Park 44.2 s, City Park (tall) 38.6 s, River Walk 66.3 s, Downtown 51.6 s, Downtown
(tall) 56.9 s, Rooftops 54.1 s (high road 51.8 s), Soder Hill 73.3 s, Night Harbour 81.3 s. Forced waiting in the
clean runs: Night Harbour 38.6 s and River Walk 24.1 s (boats, the pontoon); every other level under 8 s.

Charts (in `/home/claude/out/r4-playtest/`): `difficulty_by_level.png` (the index per group along each candidate
order), `clear_quit_heatmap.png` (clear and quit rate per level and persona), `stalls_downtown_tall.png`,
`stalls_downtown.png`, `stalls_citypark_tall.png` (the three hardest levels: red cells = seconds stalled, trying or
recovering, summed over all runs; yellow rings = failures). Tables: `summary.csv`, `spots.csv`, `summary.json`;
the small summary committed here: `docs/playtest/summary_22oct.json`.

## Spikes and flat stretches

- **Spike: level 1 (either City Park) is harder than level 2 (River Walk)** for all three groups.
- **Spike: Downtown (3) is harder than Rooftops (4)** for kids and parents, and harder than Soder Hill (5).
- **Drop: Rooftops (4) to Soder Hill (5)** for kids and parents; Soder Hill is the easiest level for parents.
- **Drop for the retro players: Soder Hill (23) to Night Harbour (8).**
- **Flat: River Walk to Rooftops for the kids in the current order** (19 to 18).
- **Single spots that cause most of a level's failures:** City Park's climbing frame (screen 9, 60% of the level's
  failures), the tall City Park's bench and hedge (screen 2, 54%), Downtown's cafe terrace (screen 2, 46%; the same
  in Downtown (tall), 48%). River Walk's failures are spread over screens 2 and 3 (32% and 30%).

## Top 10 fixes, by impact

1. **City Park, climbing frame (screen 9, x about 2720).** 60% of City Park's failures (399), 17 quits; worst for
   Tomas, Liam, Mikael. A tapped hop that has to stop in the air on a one-way bar: a late release or a held press
   overshoots. Make the first bar wider or lower so a plain held jump lands on it, or let a walk-up step reach it.
2. **Downtown, cafe terrace (screen 2).** 46% of Downtown's failures, 20 quits (Elsa, Anna). Crawl under the tables
   or hop onto one: Elsa needs crawl before she has found it and Anna fails the table hop. Give the table a crate
   step (a tap hop up) and keep the crawl as the bonus way.
3. **Tall City Park, bench and hedge (screen 2, way up 1).** 54% of its failures; Anna found the held jump by
   trying in 19 of 20 runs (median 15 s) because the level asks for it before "HOLD: BIG JUMP" is shown. Show the
   hint before the first held jump, or make the first step up a tap hop.
4. **City Park, the gate (the magpie, screen 1).** Elsa spends a median 14 s finding sneak, 12 s finding bark and
   44 s finding X before she even has the ball; 36 runs were lost here (the route could not be picked up again once the magpie had moved on). Let the
   first perch take a bark from anywhere on screen, and pulse the X glyph by the dropped ball.
5. **Downtown (tall), the plaza (the cat on the statue).** 85 of its 101 lost runs end here: after a late or early
   bark the ball is not where the route expects it. Check by hand that the ball always drops to the street and is
   easy to reach; Liam and Anna clear this level in no run.
6. **Night Harbour, fish crates (hideout 2, x about 1930 to 2050).** 116 runs lost here: after a miss on the crate
   stack or the shed roof the route could not be picked up again. Check by hand; Anna and Elsa clear 5% and 33%.
7. **River Walk, screens 2 and 3 (bench, flower box, bin climb, first bike zone).** 62% of River Walk's failures;
   Elsa loses 3.5 hearts a run. The bin's jump-and-scramble while bikes come is the hard bit: move the first bike
   zone one screen later, after the bin.
8. **Rooftops, screen 9.** 29% of its failures (Elsa); kids and Anna lose 3.6 to 3.9 hearts a run on Rooftops.
   Soften the hazard there (a longer steam-puff warning or a slower loose tile).
9. **Soder Hill, the barrels.** Mikael loses 12 hearts a run and Elsa 6.8: the barrel comes from behind while
   Pepper runs. Give the barrel a sound or a shadow tell a second earlier, or roll it slower.
10. **Night Harbour and River Walk waits.** 38.6 s and 24.1 s of forced waiting in a clean run (boats, pontoon);
    the retro players hate it. Shorten the boat cycles, or let Pepper call the boat as on River Walk's pontoon.

## Caveats

- **Many runs were lost on four levels** (Night Harbour 133 of 160, Downtown (tall) 101, Downtown 83, tall City Park
  66). Lost runs are left out of the DI, so those levels look easier than they are; Night Harbour's index rests on
  27 runs, and none for Liam, Sara or Tomas. The failure rate per minute (all runs, lost ones up to where they were
  lost) gives the same ranking: River Walk, Rooftops and Soder Hill low; both City Parks, both Downtowns and Night
  Harbour high.
- The lab is weakest where a critter or the ball goes somewhere the route does not expect (the magpie, the cat, the
  fox): the autopilots script one path through those.
- The bots do not learn technique: a precision spot (the climbing frame) fails again and again for a persona who
  keeps the same timing spread. Real players get better; the spot's share is still the right signal.
- Not knowing a control costs standing time (trying buttons), not random presses; fun barks are not modelled.
- Soder Hill's autopilot handles its own respawns, so its failures show as hearts more than as retries.
- City Park's and Downtown's beat sheets list 6 screens; the levels are longer now, so later spots are named
  "screen N" (320 px each). River Walk and Rooftops have no screen table, so all their spots are "screen N".
- Eight personas are eight parameter sets, not eight people. Use the numbers to compare levels and spots; check
  anything surprising by playing it. The method: `docs/playtest/method.md`.
