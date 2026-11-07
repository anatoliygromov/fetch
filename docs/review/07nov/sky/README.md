# Sky track, 7 Nov: the painted sky and clean hazes (branch `day/07nov-sky`)

Owner, board card "haze" (7 Nov): "The sky now feels very technical, this doesn't feel like a gradient, we need
something more artistic. Also in this particular scene with buildings, the old town buildings look really dirty."
Design target: `art/gen/concepts/sky_paint_rw_a.png` and `_b.png`. They are references only and are never cut into the game.

## What changed

1. **A painted sky per level, built by code** (`tools/build_sky.py`, with `--check`), in `riverwalk/art/scene/sky_<level>.png`
   (960 x 360, 1 art px = 1 game px, wraps sideways, row 0 = screen y -120 for the tall levels):
   - 5 or 6 flat sky tones laid as long horizontal shapes. Each join is a slow wave held in flat runs of 6 to 20 px,
     so it steps 1 px at a time. Broad "tongues" reach from one tone into the next. There are no straight full-width bands, no dither and no blends.
   - Long, calm streaks low down (taken from concept b).
   - Cumulus banks built from round lobes that are drawn once per radius and stamped on the grid: big lobes at the back, each keeping
     its sunlit top-left in 2 warm tones, smaller lobes lower down, a cool underside of scallops and a flat bottom.
   - A low long bank behind the skyline (taken from concept b) and a few small wisps high up.
   - River Walk: summer morning, low sun from the upper left, a cream-gold glow over the skyline (concept a).
     City Park: golden autumn afternoon, light blues over an amber glow, violet-blue undersides. Downtown: bright
     midday, clean blues, white tops, short flat undersides (sun high, so the light comes from nearly straight above).
   - The sky moves at 0.05 of the camera plus a 2 px a second drift. The old drifting cloud sprites are retired
     while it is on, because they clashed in style with the banks.
2. **The far city** (`skyline_<level>.png`, built from the approved `skyline.png`, which is unchanged): one clean, light
   blue-violet shape in 2 close tones, with a 1 px warm rim on its lit edges (left and top; on Downtown, top only).
   It is lighter than the trees in front, as in concept a.
3. **The "dirty" old town (haze):** the cause was the mix towards a cool grey-blue haze (Downtown mid `b2c3d9`, k 0.30,
   plus a load-time fade of 0.25 to the same colour). Mixing salmon or ochre with its opposite hue greys it: the
   salmon wall measured `#b98e8e` (saturation 0.23), and the cream house `#d2cfc6` (0.12).
   Now each level's far hazes are clean light tints of its own sky's horizon colour, and a new `clean` amount gives back the colour that
   the mix takes away (the luma is unchanged, so the ladder holds). After the change: salmon `#d7968a` (0.49) and cream `#ebe0c7` (0.47).
   The facades are not redrawn (the DT track owns them). Only the shader and fade side changed.

   | level, layer | before (haze, k) | after (haze, k, clean) |
   | --- | --- | --- |
   | River Walk shore | 9fb3cc, 0.30 | a6c4e2, 0.28, 0.55 |
   | City Park shore / mid | dcc0c4, 0.30 / ecccae, 0.14 | e4c8ae, 0.30, 0.55 (round 2, was f2d6bc) / f2d4b4, 0.14, 0.5 |
   | Downtown shore / mid | bcc8da, 0.34 / b2c3d9, 0.30 | c2d6ec, 0.30, 0.6 / dae8f6, 0.24, 0.45 |
   | far city (all) | city haze 0.46-0.52 | final colours in the file, neutral look |
   | back (all) | unchanged (already clean warm tints) | unchanged |

4. **City Park leaf front off** (owner, 7 Nov, separate commit): see `leaf/`. River Walk's hedge band is untouched.

**One switch for before and after:** `LOOK_SKY=bands` (or `Look.PAINTED = false` in look.lua) gives back the old band sky,
the cloud sprites, the old hazes and the old skyline. The "before" frames here were made that way and are pixel
identical to main.

## Round 2 (reviewer's 6 fixes, art/gen/reviews/sky_sweep_07nov.md on review/07nov-sky)

All six fixes are in `tools/build_sky.py`. Before/after of all 30 failed screens: `round2/` (`<level>_y<camY>_x<cam>_2x.png`
is round 1 | round 2 at 2x, colour then greyscale; `_4x.png` is the sky rows at 4x). Before = round 1 (f01b75d).

1. **Top of the tall worlds:** the City Park high bank moved down to rows 86-108 (was 64-90, cut at row 77), the
   Downtown one to rows 56-78 (was 36-62, cut at row 48). The banks and wisps that sat above the top row, never seen, are gone.
   `--check` now fails on any cloud pixel within 4 rows of row 120 - round(camYMax x 0.3) (City Park 77, Downtown 48,
   River Walk 120).
2. **The low bank behind the skyline (all three):** there are no stamped lobes anymore. Each low bank is now 3 or 4 flat soft
   pieces (concept b): a lens with uneven stepped edges, a lit top row, an underside row and a shorter lens on top. There are no tails.
3. **City Park horizon:** the warm joins wander 1 px per flat run (6-20 px) and get 2-4 extra shorter tongues that overlap
   (60-180 px), so there is no long even slope. The full-width lavender stripe is now 4 separate low pieces of 90-170 px
   with 1 px ends of 6 px or more. The row of identical scallops is gone with point 2. Every tongue, streak and lens now
   grows in uneven steps (`profile()`, each step after a run of 6-20 px), never a ruled slope.
4. **Cloud scraps:** a clean pass on the script's own pixels, and a `--check` rule: no cloud stroke narrower than
   2 px (a pixel must sit in a 2 x 2 block of its own tone, or in a flat horizontal run of 6+ px: a rim or an
   underside row) and no cloud piece, or piece of one cloud tone, under 6 px. All three skies: 0 and 0.
5. **Cumulus base:** in runs of 6-20 px the bank's bottom row steps up 1 px, so the base wanders instead of one ruled
   line (every bank, River Walk's left one too).
6. **City Park far city:** fill from luma 197 to 188 (`bab8d2`, near `b2b0ca`), a quarter less violet. It now sits 14
   luma under the glow (was 5 in greyscale). To keep the ladder, City Park's far tree-line haze goes one step down
   (`f2d6bc` to `e4c8ae`; shore 191/180 to 184/172). Lever: "City Park city as round 1" = back to `c4c0e2` / `b8b4d8`
   and the old shore haze.

Kept, as the reviewer advised: cloud undersides at luma 185 or more, the cloud sprites retired while the painted sky is on.

Checks, round 2: build_sky --check OK (the new rules included). asset_qa: sky_riverwalk and sky_citypark PASS, sky_downtown and the 3 skylines
WARN (small blotches). The library has the same 27 FAILs as the old path. --physics River Walk 55/55, City Park tall 98/98, Downtown tall 102/102.
check_flow 125/125, check_tiled PASSED, check_backdrop OK, PEPPER UNCHANGED, check_curve T1-T4 PASS with the same DI as
round 1. Ladder: City Park 202/202, 222/187, city 188/180, shore 184/172, mid 157/135, back 141/116 (light to dark);
River Walk and Downtown as in round 1.

## Downtown far city, low and simple (follow-up, 7 Nov)

The DT reviewer: behind the rebuilt tall houses the full skyline (towers, domes, spires) was the one thing the concepts
do not have, and at the top tier it read busy. `skyline_downtown.png` is now 320 x 30: tops only, built by
`build_sky.low_city()` from three parts placed on the grid (a flat block, a low gable 1 px up every 2 px, a round
dome), bodies 14-20 px, tops 20-28 px, shapes 18-44 px wide, so there are no spires and no thin towers. It is one clean fill
`c6d2e8` (luma 209: under the clouds' darkest 211, over the far roofs' 207) with the warm rim on the tops. River Walk and
City Park keep theirs. Frames: `dt_city_low/downtown_y000_x*_2x.png`: the top tier on a scratch merge of this branch
with day/07nov-dt at a2506f8 (not committed anywhere), before | after at 2x, colour and greyscale. On this branch alone
the old houses hide the far city at the top tier. Lever: "Downtown city as before" = remove `low` from its city entry in
build_sky.py.

## Where to look

- `concept_rw_before_after.png`: River Walk before | after (top), concept a | concept b (bottom).
- Per level, 2 frames, each as `_1x.png` (before | after, colour and greyscale), `_3x.png` (the top 160 rows at 3x)
  and the raw `_before.png` / `_after.png`:
  - River Walk: `rw_sky` (the ferry, sky-heavy) and `rw_buildings` (screen 1, the house).
  - City Park tall: `cp_sky_high` (top of the level), `cp_sky_path` (the gate), `cp_pond` (the far city over the pond).
  - Downtown tall: `dt_sky_roofs` (sky over the old town roofs) and `dt_street_row` (the old town row at street level).
- `cards/`: QA cards for the 6 new files (5x beside the bench, bin and lamp, plus an in-game frame in colour and greyscale).
- `leaf/`: City Park high road with and without the leaf front.

## Numbers (tools/measure_layers.py --ladder, median/darkest on screen)

| Level | horizon | clouds | city | shore | mid | back |
| --- | --- | --- | --- | --- | --- | --- |
| River Walk before | 223/208 | 238/199 | 169/155 | 163/130 | - | 170/117 |
| River Walk after | 226/226 | 226/186 | 174/162 | 167/133 | - | 170/117 |
| City Park before | 209/205 | 239/201 | 191/178 | 181/169 | 154/132 | 141/116 |
| City Park after (round 2) | 202/202 | 222/187 | 188/180 | 184/172 | 157/135 | 141/116 |
| Downtown before | 237/190 | 236/195 | 200/187 | 197/184 | 171/139 | 152/100 |
| Downtown after (DT follow-up) | 239/217 | 243/211 | 209/209 | 207/193 | 185/155 | 152/100 |

City Park and Downtown run light to dark. River Walk's "shore median under back median" is the same as on main (its light
house fronts, noted in docs/layer_ladder.md). Cloud tones are all luma 185 or more (the clouds row), and the far city has 3 colours with contrast 12.

## Checks

- `python3 -I tools/build_sky.py --check`: OK (4-6 tones, clouds 185+, no straight join, 0 dither checkers, seamless
  wrap, lone pixels 0.001 % or less, the horizon lighter than the far city).
- asset_qa: the 6 new files WARN only (2 to 4 small blotches each: tongue ends and the source skyline's few odd pixels).
  The whole library has the same 27 FAILs as the old path (batch 1 and older; none new).
- `--physics`: River Walk 55/55, City Park tall 98/98, Downtown tall 102/102, Rooftops 139/139.
- check_flow 125/125, check_tiled PASSED, check_backdrop OK, PEPPER UNCHANGED.
- check_curve (10 seeds, the 6-level order): T1-T4 PASS. DI kids/parents: River Walk 8.5/10.9, City Park 12.6/14.6, Downtown 11.6/18.5,
  Rooftops 23.5/26.1, Soder 15.7/14.7, Night 19.1/20.9. No level geometry changed.
- Greyscale: Pepper, the bones and the route read against the new sky in every frame. The darkest sky tone (River Walk top,
  luma 120) is the same value as the old band top.
- Rooftops, Soder and Night are greybox levels and do not use this path: no change there. Night is not touched.

## Levers (each one a single change)

- "glow warmer / cooler": the horizon tone of the level (`build_sky.py` LEVELS[..].tones, last entry).
- "City Park city lighter / more violet": back to round 1 (`c4c0e2` / `b8b4d8`, shore haze `f2d6bc`).
- "fewer clouds" / "bigger clouds": remove a bank, or raise its `h` and `r` (LEVELS[..].banks).
- "calmer sky": fewer streaks and tongues (LEVELS[..].streaks; the tongue length in build_sky()).
- "clouds still": `Look.SKY_DRIFT = 0` (look.lua).
- "rim light off": `rim_edges=()` for the level's city (build_sky.py), or "far city as before": `LOOK_SKY=bands`.
- "old town more / less colour": Downtown mid `clean` (look.lua paint, now 0.45; 0 = the dull mix of before).
- "far trees warmer": River Walk shore haze towards the cream glow (`a6c4e2` to, for example, `d8d8c8`). I kept it a clean
  light blue, because cream over green reads khaki.
- "cloud undersides darker, like the concept": possible only below luma 185, which needs the owner's yes to break the clouds row.

## Open questions for the owner

1. The concept's cloud bodies are darker lavender (luma about 170). Ours stay at luma 185 or more (the ladder's clouds row), so they read a little lighter than the concept. Keep the rule, or allow darker undersides?
2. The cloud sprites (including the approved cloud8_v2) are retired while the painted sky is on. They are still in the repo and return with `LOOK_SKY=bands`.
