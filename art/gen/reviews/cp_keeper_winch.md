# Round 1 (reviewer, 6-7 Nov night)

Piece: riverwalk/art/scene/park_keeper_winch.png, 8 frames of 80 x 80, the new face (26 pixels changed against review/06nov-base, bbox x 34-594, y 25-36).
Looked at: all 8 heads at 10x and 20x, old sheet beside new at 4x, in game at x 960 y 144 (world 960-1010) at 8x.
Script: `asset_qa.py --frames 80x80 --level cp` PASS on play and on back.

| Item | Verdict | Evidence |
| --- | --- | --- |
| Faces (checklist 5) | PASS | every frame: one eye (profile), a nose point, a mouth as a 1 px darker mark, an ear dot, the ponytail; identical pixels in all 8 heads (frame 8 differs from frame 1 by 4 px in the whole frame) |
| Repeated parts | PASS | hat, coat, winch drum the same across frames |
| Shading / Outline | PASS | 1 px ink unbroken, flat ramps |
| Mirrored read | PASS | he faces the winch in game |
| Animation | PASS | the crank turns, feet planted, nothing boils |
| crisp / reads / scale / owner | PASS | 64 px tall = 1.4 m bent over the winch; reads as a keeper at 1x |

Verdict: PASS. The base review's "keeper has no face" is fixed.
