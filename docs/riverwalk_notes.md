# Level 3: River Walk (notes on the level changes)

River Walk has final art, so everything added here is either existing art placed again or drawn in code in the
art's own colours, following the rules: obstacles crisp, mid-tone, with their own 1 px dark outline; decoration
faded 28%, no outline, base at y 184 - 10 = 174; nothing ever covers Pepper.

## What changed

| Where | Change | Why |
| --- | --- | --- |
| Screen 1, the left edge | Pepper's kennel by her house (drawn in code, 34x36, wood and a red roof board). Its roof and walls are solid down to the doorway (y 148-165): 19 px to crawl in. A gold bone is inside. | A secret (KENNEL): go left at the start and crawl in. It ends 1 px left of Pepper's box at the start. |
| Bike zone 1 | Two kiosks at the back of the pavement (decoration) with striped awnings over the pavement (obstacles, one-way, top y 112, drawn in code). The checkpoint lamp moved from x 954 to 1074 to make room. | The second route (KIOSK ROOFS, a secret, gold bone on the second awning): from the bin, running held jumps onto the awnings, high above the bikes, down onto the planter. |
| The pontoon | A rope ferry: a rope from the quay to the ferry's hull; the ferry's crew winch it. It waits by the ferry and comes to the quay (60 px/s) when Pepper is near (from x 1150, the last flower box of bike zone 1). Standing on it, it takes her across (30 px/s, after a 0.3 s pause) and stays there. | No waiting: it is at the quay when she gets down the steps. |
| Bike zone 2 | A planter (the existing art, 44x30) right before the bin as a step: 30 px up (a tapped hop and a scramble), then 26 px to the bin top. The grit box moved 16 px left (x 2600-2686) so the pavement between it and the planter is wide enough for Pepper (46 px); the pot moved to x 2548. | Softer spike: the bin was 56 px from the pavement. |
| Bikes | A bike is sent 1 s before it reaches the right edge of the screen: its bell rings, and a small warning sign (a yellow diamond with "!" and an arrow, 13x13) shows at the right edge at the lane's height until it is on screen. If Pepper stands there the sign moves above her head. | Warning before traffic. |

Bones: 51 (46 before; 3 gold: the wheelhouse, the kennel, the second kiosk awning). Secrets: 2 (KENNEL, KIOSK
ROOFS), counted on the tally.

**Hard mode** (`carry.hard` from the menu, `--hard` for the checks): 1 heart, bikes 25% faster (143.75 px/s).

## The autopilot and Pepper's trace

The autopilot now takes the kiosk roofs over bike zone 1 and, in bike zone 2, a held jump from the grit box
straight onto the bin. It clears the level in about 35 s, no hearts lost, 44 of 51 bones, 1 of 2 secrets; the
same in hard mode. `tools/pepper_golden_trace.txt` was recorded again: the first 459 steps are identical; at step
460 the autopilot, on the bin top, now jumps for the first awning instead of running off the bin (a level and
autopilot change, not a Pepper change). Pepper herself is proven unchanged by `tools/check_pepper_lab.sh`
(1,401 steps in a test room, no level involved) and `tools/check_pepper_files.sh` (her five files are identical
to aa38be5).

## Checks

`love riverwalk --physics`: 33 checks (17 before), new: the planter step and the bin, the pontoon waiting,
coming and crossing, the kiosk route, the kennel (blocks a walk, crawl in, gold bone, crawl out), the secrets, a
bike sent 1 s before the edge, hard mode. `--qa`: 0 problems. `--test` adds shots of the kennel, the kiosk roofs
over a bike, a bike's warning sign, the pontoon at the quay and the planter step.
