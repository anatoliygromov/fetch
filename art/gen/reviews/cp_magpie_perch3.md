# Round 1 (reviewer, 6-7 Nov night)

Piece: magpie perch 3 at world (585, 259) on the hedge (riverwalk/art/scene/park_hedge.png, 66 x 72, an outlined obstacle at world 552-618); the ball lands on the hedge top (tests_citypark_tall: y 256).
Looked at: frame x 320 y 144 at 6x, the hedge's top profile from the file.

| Item | Verdict | Evidence |
| --- | --- | --- |
| Perch reads | PASS | a trimmed box hedge with a 1 px dark outline: a solid thing a bird stands on |
| Ball on the hedge top | PASS | the top profile is rows 0-6 across the middle (a 3 px wobble, a 4 px dip at columns 34-39), rounded corners over the outer 6 px. A ball at y 256 sits on the leaf line, 1-3 px into the leaves at the dip, which is how a ball sits on a clipped hedge. Not floating |
| Hedge art | PASS (script WARN) | 3.2 % lone pixels and 4 blotches are the leaf texture; it is approved art, not touched this round |

## The maker's question: perch 3's ball landing on the hedge top
Fine as drawn. Keep the landing x between columns 10 and 56 of the hedge (world 562-608) so it never sits on the rounded corners, and keep y 256 so it sits a pixel into the leaves rather than on top of the outline.
