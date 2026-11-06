# rw_rowboat (the built hull, riverwalk/art/scene/rw_rowboat.png, 185 x 62)

# Round 1 (reviewer, 6-7 Nov night)

Branch `night/06nov-rw` at 4709eeb. Looked at: the file at 5x, the sweep screens x 1920 to 2880 at 2x and 5x,
14 shots of the ride (LOOK_SPOTS 2330,216 repeated) at 3x and 5x, against concept b and the owner's rejection of
the r2 boat (flat orange slab, no planks, sitting on the water like a sticker). `asset_qa.py --level rw`: PASS.

| Item | Result | Evidence |
| --- | --- | --- |
| Scale | PASS | 185 px = 4.0 m at 46 px/m; Pepper is a third of the hull, as in concept b; the rail 4 px over the quay |
| Layer | PASS | play row, outlined, asset_qa ladder clean |
| Outline | PASS | unbroken 1 px ink round the whole hull, the stem and the transom |
| Shapes | PASS | five clinker strakes straight amidships, the bow sheer rises 12 px in even 2-3 px steps, the transom 5 px |
| Shading | PASS | strakes ramp light to dark top to bottom, a white strake under the 2 px rail; no mottling, no specks |
| Palette | PASS | 10 colours, neutral ink |
| View | PASS | front-on, no inside, no top |
| Fit | PASS | as crisp as the bench and bin at 1x and 5x |
| Read | PASS | a child reads a wooden rowing boat at 1x |
| Crisp | PASS | no area-averaged edges, no lone pixels |
| Nothing floats | PASS | rows 48-61 under the waterline carry the water tint (wet, darker hull) and a ripple row of white dashes runs along row 48; the hull sits IN the water, not on it |
| Consistency with concept b | PASS, one note | planks, white strake, rail and sheer match; the hue is honey-orange where the concept is a warmer red-brown mahogany |
| "Terrible, dirty, flat or floating?" | No | the slab is gone: planks, a wet hull, a waterline |

Verdict: PASS. Show it.

Suggested tweak, not a blocker: shift the three lower strakes one step towards red-brown (concept b's mahogany) so
the owner's word "orange" cannot come back; it also separates the honey oar from the hull (see rw_rower.md).

# Round 2 (reviewer, 6-7 Nov night)

Branch `night/06nov-rw` at df396bb, merged into `review/06nov-rw`. Looked at: the file's bow and stern at 7x, the
re-rendered sweep (13 screens), 14 ride shots both ways at 3x and 5x. `asset_qa.py --level rw`: PASS.

| Item | Result | Evidence |
| --- | --- | --- |
| Colour against concept b | PASS | the lower strakes are red-brown mahogany now, the top strake and rail still light; no more honey-orange |
| Bow sheer and seams | PASS | the sheer rises in runs that shorten toward the stem (5, 4, 3, 2 px), every plank seam fans into the stem with no 1 px jaggies at 7x |
| Everything else from round 1 | PASS | unchanged: outline, planks, wet hull tint, ripple row, scale |

Verdict: PASS. Finished.
