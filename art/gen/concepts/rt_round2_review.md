# Rooftops concepts round 2: independent review (8 Nov 2026, 0 credits)

Owner 14:47: "the 20 concept scenes are just duplicates ... lots of wrong perspective ... did art director look at them?" They had gone to him unchecked (concept_score crashed on a path bug). Review by a fresh agent that did not make them; automatic scores in rt_round2_concept_score.txt (grid and colour distance only; it cannot see design).

Result: 0 PASS, 7 PARTIAL (street a/b, stairwell a, market a, dryingyard b, lightcourt b), 13 FAIL. 18 of 20 break the front-view rule. Variety 3/10.

Main defects:
- Perspective: cobbled ground planes going back, stair treads with tops, side walls, 3/4 chairs, one-point courtyard (lightcourt a), boxes with tops.
- Geometry moved: the dog moved or doubled (stairwell b, dryingyard a, scaffold a, sauna b, longroof b, roofcafe a/b); boards or tiles missing; slopes reversed (longroof a).
- Copies of the hotel painting: roofcafe a and longroof b almost whole; the top band (roofline, three chimneys, spire) in street b, scaffold b, roofcafe a, sauna a; the copper canopy over the stone front in lightwell a, longroof a/b, roofcafe a/b; the dog pasted at the hotel's position.
- The same everywhere: a spire in all 20, the same ochre wall and windows, one golden sky.

Cuttable pieces (from the review): street awning, lantern, shop front, door; stairwell windows; market chimney and vent; drying yard washing line and awning; light court back wall, balconies with brackets, downpipe, post; planter boxes; sauna b tall chimney with nest; roof cafe b parasol set and stair house; light well attic window and bracketed board.

Causes (the prompts): the hotel painting sent as Image 2 to every job; shared boilerplate (far town with spire, the hotel's materials list) in every prompt; perspective words in the subjects ("seen from the side", "seen from inside", "flight of steps"); weak view wording.

Next prompts must: drop the hotel painting as a reference (a materials swatch with no dog instead); drop the spire and hotel boilerplate; strict elevation wording (roofs as flat bands or triangles, steps as a sawtooth of risers, ground as one flat band, no tops, no side walls); state the dog's box and "exactly one dog, unchanged, not mirrored", then an overlay check that rejects moved geometry; give each scene its own look (wall colours, metal or copper roofs, time of day); one pilot scene through the checks before any batch, under an approved plan.
