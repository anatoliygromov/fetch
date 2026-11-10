# River Walk T2: what "screen 13" really is (night of 10 Nov)

check_curve T2 has failed since 7 Nov: River Walk screen 13 holds 36% of the level's failures (75 of 207), limit 35%.

## What I measured

- 73 of the 75 screen 13 failures are one thing: the autopilot reaches the girl without the ball ("GO BACK FOR THE BALL!"). 72 runs, every one still clears the level about 6.5 s later.
- I re-ran all 72 runs with logging (same seeds, same carry). Where the ball was lost:
  - 61 runs: x 3680 to 3743, screen 12, Pepper hurt. That is the open pavement between the bin (ends x 3659) and the last bench (x 3756). Bike zone 2 ends at x 3678, but a bike sent while she is on the bin still rides through the gap. 54 of the 72 runs lost no heart.
  - 6 runs: x 3904, by the girl (the ball put down early).
  - 5 runs: x 2464 to 2592, the harbour (gull or water).
- Chart: `rw_ball_lost_where.png`. The spot: `rw_screen12.png` (bin left of centre, bench right).

So the hard spot is the jump down from the bin on screen 12, not the girl. The lab counted it where it noticed.

## Options

1. **Lab fix only** (branch `night/10nov-curve`, built, checks green). The lab records where the ball was lost and T2 counts it there. River Walk worst spot becomes screen 12 at 30%. T1 to T4 PASS. No game change; every DI, Elsa and lost number is identical.
2. **Level change**: keep bikes out of the bin to bench gap (end bike zone 2 before the bin, or move the bench next to the bin). Needs your yes and a Pepper trace re-record. Not built.
3. Both 1 and 2.
4. Accept as is (1 point over).

Recommended: 1 now. 2 only if the bin to bench knock feels unfair when you play it.
