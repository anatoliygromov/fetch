# River Walk props, 6 Nov 2026 (branch art/rw-props-06nov, family rw_props_06nov)

Triage of every never-reviewed River Walk piece in the list: `asset_qa.py`, 4-5x beside bench, bin and lamp, and
the game's frames (`frames/sweep_riverwalk_y000_x*.png`, look on, 1x). Credits: 48 (one job, rw_birch).

| Piece | File, size | Layer | Verdict | Method | asset_qa |
| --- | --- | --- | --- | --- | --- |
| rw_birch (replaces tree_far) | rw_birch.png 192x250 | back | NEW | SpriteCook GPT 2.5 1K, refs blockout + rw_lime 4x, 48 credits; grid4_cut, cut_cp_tree --green, polish, 2 rules | WARN decor-ink 44 % (its own dark leaf shade; rw_lime is 52 %) |
| gritbox_front | 88x32 | play | FIXED by hand | the "SAND" letters (no text in art) take the plank fill, 63 px | PASS |
| cloud2 | 117x39 | clouds | FIXED by hand | 5 px of 2x2 checker dither take their neighbours' colour | WARN 2 blotches (as before) |
| cloud5 | 87x32 | clouds | FIXED by hand | 9 px of checker dither taken out | PASS |
| kennel | 34x36 | play | kept | falu red with white corners, 0.75 m, crisp 1 px ink, the doorway is its whole crawl box | PASS |
| pontoon | 54x12 | play | kept | grey deck on floats, outlined, the mover's box | PASS |
| rw_jetty | 48x41 | play | kept | plank deck on crossed piles, outlined, true width | PASS |
| pot | 17x27 | back | kept | clean at 5x; 3 dirt px under the fail line | WARN noise 0.9 % |
| cloud3 | 115x45 | clouds | kept | no dither found; soft shapes like cloud8 | WARN noise 0.3 %, 1 blotch |
| tree_far | 101x100 | back | REPLACED | a 2.2 m tree on the 46 px/m line (a sapling next to rw_lime), ink edge 66 %, 4.5 % lone px, 10 pinholes | (file kept, no longer drawn) |

## rw_birch
A Swedish silver birch at true scale: trunk 14-16 px (0.35 m), lowest leaves 95 px up, crown 192 px (4.2 m), its top
above the screen (y -76). Pepper in the blockout and in the cut: 52 x 38 (1:1). Level: the two tree_far props now
draw rw_birch with the trunk where tree_far's trunk stood (x 460 and 2918, y0 -76); scene.lua loads it with the
back fade; rules.json lists it as a tree for check_backdrop. Hand rules in `tools/fix_rw_props_06nov.py` (every
pixel in `art/source/rw_birch/edits.json`): a 3 px near-twin colour merged; the leaf highlight two steps down (#c8dd3c -> #b6d434 -> #9ac22a, review round 1:
highlight on screen 212 -> 204 -> 190, under the far city's p99 194). Highlight 9 % of the art.
My eye at 5x: clumps with lit tops, a white trunk with a grey shade side and black marks; as crisp as the lime.

## Files
`cards/` (qa_card, frames and slots given), `frames/`, `qa.json`.

## Checks
PEPPER UNCHANGED, flow 125/125 (with its own save folder; a run sharing the default save folder with other tracks
gave 4-10 random save FAILs), Tiled PASS, BACKDROP OK (rw_birch at y -76), `--physics` riverwalk 55/55.
