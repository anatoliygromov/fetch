# City Park leaf front off (Look.LEAF_ON = false, owner 7 Nov)

# Round 1 (reviewer, 7 Nov)

Branch day/07nov-sky at 73da2e3 and f01b75d. Looked at the 18 high-road screens (tiers y 24 and y 0, x 0 to 2560) at 2x
in colour and greyscale, and the maker's before/after pairs at x 640 and x 1920 after forming my own view.

Verdict: PASS. The high road looks finished at the bottom, not cut.

| Item | PASS/FAIL | Evidence |
| --- | --- | --- |
| The bottom of the screen reads as a place | PASS | On every high-road screen the bottom edge runs through tree trunks, the rope bridge deck, the platforms and the lamp heads of the path below (x 960, 1280, 1600 at y 24: trunks and the lamp top at screen x 60-75, y 200-240). It reads as looking down from the canopy, which is what the tier is. |
| Nothing floats or ends in the air | PASS | The trunks continue past the bottom edge (taller than the viewport); the platforms attach to their trunks. |
| Pepper still framed | PASS | She is the darkest shape on every screen; the old black band added nothing to her read. |
| Any empty flat strip at the bottom | PASS | At x 2240 and x 2560 the bottom shows the far tree line and the peach lawn with the climbing frame's top: the same ground the path tier shows, not a void. |
| The test in tests_citypark_tall.lua | PASS | The new check reports 0 clumps drawn with the front off and keeps the old keep-out checks alive with it on. |

No fix proposed. If the owner wants a frame back later, the right thing is not a band but a few whole foreground
branches hanging in from the top corners at the front scale (about 60 px/m), dark silhouette, never at the bottom.

# Round 2 (reviewer, 7 Nov)

No change to the leaf front; re-checked the 18 high-road screens at e6b62a4 with the new sky. Still finished at the
bottom. PASS.
