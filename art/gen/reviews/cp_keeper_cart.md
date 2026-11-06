# Round 1 (reviewer, 6-7 Nov night)

Piece: riverwalk/art/scene/park_keeper_cart.png, 8 frames of 82 x 82, drawn mirrored by scene.lua keeperCart; the fix removed 51 pixels of dirt (bbox x 20-642, y 22-77) and nothing else.
Looked at: old sheet beside new at 4x, frames 1-2 at 6x. He is a triggered hazard (bikes zones at world 1376 and 2350) so the lookshot sweep does not show him; judged on the sheet.
Script: `asset_qa.py --frames 82x82 --layer play --level cp` PASS (on back it fails the ladder, as any play piece does).

| Item | Verdict | Evidence |
| --- | --- | --- |
| Faces | PASS | flat cap, eye, nose, grey beard in every frame |
| Repeated parts | PASS | the barrow and its wheel identical across frames; spokes even |
| Shading / Outline | PASS | the dirt specks are gone, fills flat, 1 px ink unbroken |
| Animation | PASS | walk cycle steps, hands on the handles in every frame |
| crisp / reads / scale / owner | PASS | |

Verdict: PASS.
