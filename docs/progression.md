# FETCH! progression and balance plan (5 levels), 19 Oct

## Where we are (measured)
| Level | Length | Lamps (checkpoints) | Ways to lose a heart | Autopilot clear |
| --- | --- | --- | --- | --- |
| 1 City Park | 6 screens (1920 px) | 5, one per screen | the leaf cart, the pond | 31.4 s |
| 2 Downtown | 6 screens (1920 px) | 5, one per screen | the tram, the fountain | 29.8 s |
| 3 River Walk | 10 screens (3200 px) | 8 | 2 bike zones, the river | 35.1 s |

Problems:
- **Too short.** The autopilot plays near-perfectly and needs 30 to 35 s per level. A tool-assisted (perfect) run
  of Lion King (Genesis) takes 14:02 for 10 levels, about 84 s per level, so even our perfect play is 2.5 times
  shorter than theirs.
- **Too easy.** There are no creatures that bite back, only one or two traffic zones per level, and a checkpoint
  on every screen. Nothing asks for timing under pressure.
- **Not progressive.** Level 2 is shorter and has fewer hazards than level 1. Level 3 is long, but most of it is
  open pavement.
- **Every level plays the same way.** Each one is walk right, hop over or onto props, and wait for the traffic.
  Lion King changes its manner from level to level:
  - Pride Lands: platforming plus the first critters.
  - Can't Wait to be King: riding and bouncing on animals, plus a puzzle.
  - Elephant Graveyard: climbing, geysers and hyenas.
  - Stampede: a forced-forward chase.
  - Simba's Exile: rolling boulders.
  - Hakuna Matata: waterfalls and logs.

## The plan: one new idea per level, rising pressure
| | 1 City Park | 2 Downtown | 3 River Walk | 4 Söder Hill (new) | 5 Night Harbour (new) |
| --- | --- | --- | --- | --- | --- |
| Manner | sneak and bark | bounce and carry | water and traffic | the chase | sniff in the dark |
| New mechanic | geese (bark to shoo, or hop over) | springy awnings and parasols launch Pepper high; carry the ball through the second half | rowing boats on open water (moving platforms); gulls swoop (crawl to dodge) | the screen scrolls on by itself; the ball rolls ahead down the hill | darkness with lamp pools; sniff (L1/R1, Q) shows the scent trail; a fox hides the ball |
| Length (target) | 9 screens | 10 screens | 12 screens | 16 screens | 13 screens |
| Autopilot clear (target) | ~50 s | ~60 s | ~75 s | ~70 s (scroll) | ~90 s |
| Checkpoints | every screen | every 1.5 screens | every 2 screens | 3 in the level | every 3 screens |
| Hazards | leaf cart, 3 geese, pond | tram x2, 2 geese on the plaza, fountain | 3 bike zones (a little faster), gulls, open water | gaps, low signs, a barrel the ball knocks loose, the edge of the screen | water gaps, crumbling planks, rocking boats, the dark |

Rules kept in every level:
- Pepper's movement stays exactly the same (`check_pepper` must say UNCHANGED).
- Nothing moves by itself: a goose walks, a gull flies, a keeper pushes, the ball rolls downhill, someone rows the
  boat.
- Every level ends with a real fetch: pick up the ball and give it to Mia.
- Nothing covers Pepper.
- Obstacles are crisp and outlined; decoration is faded.
- For kids 6-10, damage is always readable. Every hazard warns first (a honk, a bell, a squawk, a shadow), and a
  bark is always a useful answer.

## The story across five levels
1. City Park: a magpie steals Mia's ball.
2. Downtown: a cat sits on it on the plaza.
3. River Walk: Mia throws it by the river, and it lands on a ferry.
4. Söder Hill: on the steep street up to Söder, the ball slips out of Mia's hands and rolls all the way down the
   hill. Chase it before it reaches the water.
5. Night Harbour: it gets dark on the way home along the harbour, and a fox snatches the ball. Sniff out where it
   hides, then bring the ball home to Mia at the door. THE END.

## New engine pieces (shared)
- `L.critters`: creatures with simple rules.
  - **goose**: patrols between x0 and x1. It hisses, then charges when Pepper is in front within 70 px, and its
    bite costs a heart. A bark within 80 px shoos it away for good (+200). It is 22 px tall, so a held jump clears
    it.
  - **gull**: circles high above. Every few seconds it squawks and its shadow appears, then it swoops down to
    Pepper's head height (standing). Crawling ducks under it; contact costs a heart.
- `bounce = h` on a prop: landing on it launches Pepper h px high (springy awnings and parasols). Her own jump is
  untouched: the launch only sets her upward speed.
- `crumble = true` on a prop: 0.5 s after Pepper stands on it, it shakes, falls away, and comes back after 3 s.
- Level 4: `L.scroll` makes the camera move on by itself. The left edge of the screen pushes Pepper; pinned
  against a wall by it, she loses a heart. The ball rolls ahead on the ground.
- Level 5: `L.dark` draws darkness with light pools. Sniffing shows a trail of glowing dots to the fox's hideout,
  and makes hidden bones glow.
