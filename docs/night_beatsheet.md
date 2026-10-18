# Level 5: Night Harbour (beat sheet)

The finale and the hardest level. Its manner is **sniff in the dark**: the harbour is dark except for pools of
lamplight, a fox has the ball, and Pepper finds it with her nose.

Story: it got dark on the way home along the harbour, and a fox snatched Mia's ball. Pepper sniffs out where it
hides, barks it out of each hideout, picks up the ball where it drops it, and brings it home to Mia at the front
door. Ending: "HOME AT LAST. MIA HUGGED PEPPER GOOD NIGHT."

Files: `riverwalk/level/night.lua` (props, lights, boats, the fox, bones, hints), `riverwalk/level/night.map`
(made by `tools/make_night_map.py`), `riverwalk/night.lua` (the night rules), `riverwalk/tests_night.lua`.

## Numbers
| | |
| --- | --- |
| Length | 14 screens, 4480 px (the plan said about 13; the slipway screen was added for length) |
| Autopilot clear | 81.3 s (near-perfect play; target about 90 s) |
| Par | 135 s (81.3 x 1.6, rounded up to 5 s) |
| Time limit | 420 s |
| Checkpoints | 5 lamps: x 296, 1240, 2200, 3176, 3760 (largest gap 976 px, about 3 screens) |
| Bones | 54, three gold: the shed roof, under the low jetty, the top of the crate tower |
| Secrets | 2: SHED ROOF (screen 7), CRATE TOWER (screen 12) |
| Water | 8 gaps; falling in costs a heart and puts Pepper back at the last lamp |

## Screens
| # | x | Name | What happens |
| --- | --- | --- | --- |
| 1 | 0 | The quay | The fox sits on the quay with the ball. Within 120 px it runs off into the dark to hideout 1. Mia: "A FOX TOOK MY BALL!" |
| 2 | 320 | Lantern street | A 48 px water gap (TAP: HOP), then fish crates (16 and 32 px). Mia teaches the sniff: "SNIFF! HOLD L1 OR Q". |
| 3 | 640 | The tarp | Hideout 1: under the tarp of a beached boat. Sniff close by to find it (its eyes shine), then bark: it bolts. |
| 4 | 960 | Old jetty | Two crumbling planks over 160 px of water: hop, hop. "OLD PLANKS! KEEP MOVING!" |
| 5 | 1280 | The rowboat | A rowboat goes to and fro (28 px/s) over a 240 px gap. Hop down onto it, ride, hop up the far quay. |
| 6 | 1600 | Fish boxes | A box step (16, 32 px), the net shed: crawl under it (19 px) or run over its roof. |
| 7 | 1920 | The fish crates | Hideout 2: behind the crates. High route: the crate stack, then a held jump to the shed roof (gold bone, secret). |
| 8 | 2240 | Rotten planks | Four crumbling planks in a row over 240 px of water: four tap hops, no stopping. |
| 9 | 2560 | Two boats | A small boat, the mooring post (top y 176), a second boat, the far quay. Timing. |
| 10 | 2880 | The low jetty | Hideout 3: under the jetty. Sniff, bark: the fox drops the ball and runs off for good. Crawl in, pick it up (gold bone). |
| 11 | 3200 | Back over | Carrying the ball: a rowboat (24 px/s), then one crumbling plank over 96 px of water. |
| 12 | 3520 | Crate tower | 16, 32, then 64 px of crates. The top is the CRATE TOWER secret (gold bone); or walk on. |
| 13 | 3840 | The slipway | Still carrying: a boat, one crumbling plank in a lamp's light, a second boat, the quay. "WAIT FOR THE BOAT!" |
| 14 | 4160 | Home | Mia waits at the front door under the porch light. Give her the ball (X). THE END. |

## Mechanics (night.lua)
- **Darkness** (`L.dark`): a 320 x 240 canvas, dark blue (deeper at the top), with light pools stamped in by blend
  multiply: every lamp, `L.lights` (lanterns, boat lights, windows, the porch) and a pool round Pepper herself.
  The pools are clear in the middle with three dithered steps of dusk to the edge, and a faint warm glow is added.
  No shader, cheap enough for the handheld.
- **What the dark never hides**: Pepper (her own pool), every floor she can stand on (a moonlit edge on terrain
  tops, solid and one-way props, the boats), the water (a shimmering line), the crumbling planks (drawn over the
  darkness), the fox when it runs (drawn over, a little dimmer), the dropped ball (a faint glow), Mia and the house.
- **What the dark hides**: bones outside a light, and the hidden fox. Secrets are only seen by climbing.
- **Sniff** (hold L1 / R1 on the handheld, Q on the keyboard): standing on the ground, Pepper stops and plays her
  sniff clip. The stage does not run her controller that step, so her movement code is untouched
  (`check_pepper` UNCHANGED). A trail of glowing dots runs 200 px from her nose towards the fox's hideout (an arrow
  if it is further), or the dropped ball, or Mia once she carries it. Bones within 200 px glow.
- **The fox** (`L.fox`): three hideouts (TARP x 804, CRATES x 2096, JETTY x 3020). Hidden, it has to be found:
  0.4 s of sniffing within 150 px finds it (a chime, its eyes shine, Mia: "THERE IT IS! BARK!"). A bark within
  96 px (48 px up or down) chases it to the next hideout; at the last one it drops the ball and runs off the level.
  A bark before it is found, or from too far, only gets a "?" over its eyes.
- **Crumbling planks** (`crumble = true` props): 0.5 s after Pepper lands on one it shakes, then falls into the
  water; it is back 3 s later (when she is not in its way), with a faint outline first.
- **Boats**: ping-pong movers 12 px below the quay (a hop up to get off). Pepper rides them standing or sniffing.

## Hints
Pepper's button hints: BARK! (the fox found and in range), PICK UP, GIVE. Mia's lines: the fox, sniffing
("SNIFF! HOLD L1 OR Q" near a hidden fox), the planks, the boat, "BRING ME THE BALL!", "GO BACK FOR THE BALL!"
(only once the fox has dropped it). The sniff hint is Mia's line, not a button hint, because the flow test only
allows the A, B, X, Y and Down buttons in Pepper's hints.

## Art needed later (greybox now)
| Piece | Size (px) | Notes |
| --- | --- | --- |
| Fox: sit, run (2 frames), peek (eyes in the dark) | 24 x 12 | now drawn in code (night.lua FOX) |
| Night harbour backdrop: sky, moon, warehouses, cranes | 640 x 240 parallax | replaces the greybox town; stars and moon are code now |
| Quay edge and stone tile | 32 x 56 tiles | dark granite, a lit top edge |
| Water at night | 32 x 32, animated | dark with moon glints |
| Crumbling plank | 32 x 6, 40 x 6 | old wood, cracks; a shake and a falling frame |
| Rowboat / small boat | 56 x 14, 48 x 14 | with a lantern at the bow |
| Lantern post | 8 x 40 | with a 5 x 6 lamp |
| Mooring post | 16 x 64 | |
| Net shed, fish shed with roof | 72 x 26, 96 x 80 | |
| Fish crates (stack, tower) | 32 x 16 tiles | |
| Tarp over a beached boat | 88 x 24 | |
| Low jetty | 120 x 26 | deck and legs |
| Mia's house with door, windows, porch light | 128 x 112 | warm windows |
