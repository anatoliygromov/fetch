# River Walk traffic 2, 5 Nov 2026 (branch art/rw-traffic2-05nov)

The road's other three cars, in the method and style of the reviewed traffic family (docs/review/05nov/rw-traffic/,
road_car1 and road_car4 PASS in review round 2). Board question from that family: "the road's other three cars
(taxi, van, car 5) are the old art: redraw them in the same style next?" This is that redraw, ready for review.

| Asset | Game file | Size | Render | Credits |
| --- | --- | --- | --- | --- |
| rw_car2 (pilot) | road_car2.png, white panel van | 242 x 102 (4.4 x 1.85 m) | rw_car2_n5b (variant a came back 42 x 42, off grid) | 24 |
| rw_car3 | road_car3.png, yellow taxi | 246 x 93 (4.5 x 1.7 m with the sign) | rw_car3_n5a | 24 |
| rw_car5 | road_car5.png, silver 1990s estate | 250 x 89 (4.5 x 1.62 m with rails) | rw_car5_n5a | 24 |

72 SpriteCook credits of the 120 cap, 3 paid jobs (one per asset), no family retry. Ledger: art/gen/ledger.csv.

Method: blockouts art/gen/blockouts/rw_car{2,3,5}.py; preflight with the owner's 5 Nov words; render cut 1:1
(tools/build_traffic.py cut, then `car`: new-cut clean pass tol 90, key remnants, outline); tools/fix_traffic2.py
base (one ink #000000; the near-ink shades into #373737 or the roof dark #282a36; one wheel drawn once by rule, round,
steel rim lit from the upper left, stamped on both centres on one axle line, art/source/NAME/wheels.json; the outer
silhouette in the ink), tidy (the new cut's speck pass: 1-3 px specks of a body colour inside another body colour;
glass by rule: one flat glass, one 2 px reflection band; art/source/NAME/tidy.json), hand (art/source/NAME/hand.json).
Every changed pixel: art/source/NAME/edits.json. Sources: art/source/NAME/NAME.aseprite (tools/aseprite_io.py, round
trip checked).

In-game frames: --test shots 22 (estate by the bench), 23 (taxi by the bin, new), 24 (van by the bin, new), taken 1:1
from the 2x window; ingame_*_1x.png and before_*_1x.png. Board images: board/. Cards: cards/.

## For the reviewer
1. Only the top 48 rows of a car show in the game (CAR_TOP 192 to the screen edge); the wheels never show. The van
   is the tallest (102 px) with the same top line, so it sits lower than the cars; that is the existing road rule.
2. The taxi's first cut had a black roof and pillars; in game only the sign, the roof and the glass showed, so it read
   as a dark car. Roof and pillars are now yellow; the B-pillar and the window rubbers stay dark.
3. road_car5 is 89 px tall against 81 asked: the roof rails (8 px). Waived as road_car1 was (cut.json).
4. The wheels are drawn by rule (flat steel wheel, 4 holes) rather than copied from the render as on car1 and car4.
5. road_car2: asset_qa WARN on 2 blotches, the two ends of the e9d1b2 crease line at row 55 (x 9-19 and 60-62); a
   few light specks may remain on the van's bonnet (x 15-30, y 45-52).

## Review round 1 fixes (d2c2804: taxi PASS; van and estate fixes), 0 credits
- road_car2: A-pillar rows 5-42 (x 33-70): the windscreen's edge strip one flat glass #35455f (15 px), the pillar's
  black line closed at (52, 19) where a grey dab broke it, the band between the two black lines one flat #faf6f0
  (236 px; rows 5-8 at the roof corner included, where the same dashes ran on); the 12 bonnet specks take their
  neighbours' colour; the 8 px orange side marker removed. 272 px changed in all, all inside x 4-70, y 5-58.
- road_car5: an ink row over the lower roof-rack rail, (129-220, 5): 85 px. Nothing else changed.
