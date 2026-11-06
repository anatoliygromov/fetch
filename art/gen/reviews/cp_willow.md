# Round 1 (reviewer, 6-7 Nov night)

Piece: riverwalk/art/scene/cp_willow.png, 474 x 508, 14 colours, drawn by scene.lua Sc.bigWillow on the back layer, fade 0.28.
Branch night/06nov-cp at d4f6f7d. Looked at: the file at 2x and 5x (fronds and trunk foot), the sweep frames y144/y024/y000 at x 640 in colour and greyscale, the concept art/gen/concepts/cp_pond_concept_a.png.
Script: `asset_qa.py --layer back --level cp` PASS (with --layer play it fails the outline check, which does not apply: it is decoration).

| Item | Verdict | Evidence |
| --- | --- | --- |
| Scale | PASS (note) | crown 474 px = 10.3 m, trunk foot 60 px = 1.3 m: a big park willow, true scale against Pepper; the spec said 7 m (see the question below) |
| Layer | PASS | on screen after the fade: fronds p10 116, p90 185, max 215; trunk p10 116; inside the back row (darkest 80, contrast 120); lighter than the lime trunks (p10 102) and the play line |
| Outline | PASS | none; frond edges are the darker gold of the ramp |
| Shapes | PASS | fronds hang in clean strands, branches read through them, trunk sides straight, no jaggies |
| Shading | PASS | 4 golds, 5 browns, flat fills, light from the upper left, no mottling; a few lone pixels along frond edges, well under 5 % |
| Palette | PASS | level golds and neutral browns, nothing lifted |
| View | PASS | front-on |
| Fit | PASS | beside the bench, bin and lamp at 5x it is as crisp; edges hard, no averaging |
| Read | PASS | a child says willow at 1x |
| crisp | PASS | no area-averaged edges, no blotches |
| reads at 1x | PASS | |
| true scale | PASS | |
| nothing floats | PASS | trunk foot on the back props line, 1.3 m of bare trunk under the fronds; the fronds hang behind the walkway |
| layer ladder | PASS | measured above |
| consistency with concept | PASS with a note | same gold fronds and brown trunk as concept A; the concept has three 7 m willows with sky between them and fronds that reach the water; the game has one 10 m willow whose crown fills the sky and is cut by the top edge at y 24 and y 0 |
| owner test | PASS | not dirty, flat or floating; the best piece of the night |

Verdict: PASS. Show it.

## The maker's questions
- 10 m crown vs the 7 m spec: keep 10 m. One big willow as the pond set piece works, its crown runs past the top of the screen like the rule for front trees, and at y 144 it leaves 1.3 m of trunk and the sky under the fronds. 7 m would end inside the screen at the top tiers with sky over it, which the owner rejected on River Walk. Write the 10 m into the hook table so the spec and the file agree.
- The gold highlight at about 201 luma on screen: keep. The ladder limits the darkest value and the contrast, not the lightest; the fronds measure p10 116 to p90 185, contrast under 120. The highlight sits at the sky's own value so the crown's edge melts into the sky instead of cutting it, which is right for the back layer.
