# Lock and complete: concept art to game layers (8 Nov 2026)

Owner, 8 Nov: "I want to make sure that the concept art is being translated as close to the original as possible in
terms of details", "we need a super solid way to keep doing it", then "let's work on what you recommend" (lock and complete).

## Why
The concepts (Nano Banana Pro edits of real 320x240 game frames, art/gen/concepts/) are already pixel art on the game's
grid: 3.75 image px per game px. Cutting them 1:1 keeps every detail; any redraw (SpriteCook, Pixel Engine, a fresh
sprite sheet) reinterprets. All 23 concepts made this way score 83-93 % clean cells and dE 1.7-5.5 (tools/concept_score.py).

## Steps (Rooftops pilot: art/source/rt_lockfill, branch art/08nov-lockfill)
1. Cut: `tools/concept_cut.py CONCEPT cut.png 320 240` (grid offset from edges; per cell a label vote, colour from the
   original pixels with the winning label; never box or bilinear).
2. Masks: holes = what game sprites cover in the concept (Pepper, goose, bones, the concept's own tile piles), grown
   1-2 px; far = sky, spire and far town above the near skyline.
3. Complete, free: `LF_PERIOD=43,42 tools/lockfill.py DIR` fills each hole by copying from the concept itself (the best
   matching shift or mirror inside the same layer band, several sources in turn; bare wall continues its row), then
   `tools/rt_lockfill_fixes.py DIR` (the hand pass as explicit edits). LOCK OK = 0 changed pixels outside the holes.
   Paid option, with the owner's yes on the total: a SpriteCook edit (Nano Banana Pro, 16 credits an image) of the
   holes only, then the same lock. Not needed for the hotel roof screen.
4. Crispness: `tools/rt_windows_palette.py DIR`: one window per storey stamped onto the others (positions as the concept
   has them), palette ramps (64 k-means in Lab, merged under dE 3.5), lone pixels.
5. Layers: `tools/rt_pilot_layers.py DIR riverwalk/levelart/rooftops` (pilot_far.png at scroll 0.25, pilot_near.png with
   the world); loose tiles keep the game's 24x6 and take the concept's clay (`tools/rt_pilot_tile.py`).
6. Gate: `tools/fidelity_card.py CONCEPT holes.npy card.png LABEL=frame.png ...` on frames shot at the concept's camera.
   Hotel roof: round 3 dE 30.3 / concept edges kept 38 %; pilot dE 3.35 / 97 %.
Aseprite source (all steps as layers): Mac `2d game test/aseprite-work/rt_lockfill/rooftops_pilot.aseprite`.

## Independent review (8 Nov 11:15) and fixes
Round 1: FAIL in game (the screen itself close to pass). Fixed, 0 credits:
- far layer: the run-on rows made streaks when the camera looked up and its 320 px edge showed. Now opaque and
  wrapping, sideways parallax only (moves with the world up and down), hidden parts continued along their own row,
  near-roof rims and dark leaks kept out; drawn only behind the pilot's columns (one seam, not two).
- near layer: split into back and terrain; the terrain runs on three storeys below the frame (no cut at camY 248-280).
- windows: stamped only where the concept pixel is not in a cast shadow; sills on the upper windows over the dips.
- fragments: the right skylight's top-left corner (from the left skylight's left end), both skylight ends mirrored
  whole, the wall over the dips, no copied wall ticks.
- the real resting camera is y 208 (vcam FLOOR 168): frames at 208 are on the card.
Left for the owner: the colour call (the look on changes little: dE 3.4 -> 4.4; the back roofs are as dark as the
ledges, p10 64 vs 63, the ladder wants the back at 80+); the coping row 48 px over Pepper reads like a ledge just out
of reach; the glass skylight boxes over the dips hide that she can fall in; the pilot is one screen (hard seams with
round 3 at its left and right edge until the parts kit builds the rest).

## Open
- The rest of Rooftops: the parts kit (window, tile row, coping, chimney, skylight) cut from this screen, stamped.
- Owner's colour call: the pilot is drawn without the look (the concept's colours); its play line is lighter than the
  back wall in places (the concept's choice).
- The concept recipe additions for the next concepts: claude/concept-to-pixel-08nov.md (project doc).
