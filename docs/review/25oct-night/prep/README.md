# Night of 25 Oct: prep for the owner's next calls

**Update 21:45:** the evening session (`art/animals-r2`, `preview/25oct-late`, 21:26) already took the owner's go on
the cat (32 px sitting), the gull (34 px span) and real-size rowing boats (182 px, harbour +256 px). Section 1 and the
boat half of section 2 are kept for the record only; the lamp call stays open. Section 4's preflight change still
matters: `art/animals-r2` set the cat's `real_height_m` to 0.65 (a cat is about 0.33 m) to get its 30 px past the
true-scale check; `owner_size` records the owner's call instead.

Made on the night run (0 credits, no image service). Nothing here changes the game; the sheets are grey blockouts on
real game frames. Rules: `docs/BIBLE.md`. Board decisions read at 20:30 (the owner's review at 20:16-20:18).

## 1. Gull and cat redraw: size (board 20:16, both "redraw")

Sheet: `animals_sizes_4x.png` (1x: `animals_sizes_1x.png`; script `art/gen/blockouts/animals_sizes_25oct.py`).
Grey blockouts beside Pepper's real sprite (52 px nose to tail, 38 px to the top of her head).

| | Was | Owner, 20:16 | A | B | C |
| --- | --- | --- | --- | --- | --- |
| Cat, sitting, to the ear tips | 16 px (true scale) | "bigger, slightly smaller than the dog" | 27 px (70 % of her height) | **30 px (80 %)** | 34 px (90 %) |
| Gull, wingspan | 44 px (58 was "massive", he picked "about 40") | "smaller too" | 36 px | **32 px** | 28 px |

The running cat on the sheet is about 1.4 times its sitting height long (B: 42 px against her 52).
Default if he only says "go": B and B.

**Spend line draft:** "Family animals, redraw: gull (still + 8-frame flap) and cat (still + idle, leap, run), 6 jobs,
128 SpriteCook credits at 25 Oct prices (gull 12 + 26, cat 12 + 3 x 26). Go?" Notes for that line:
- Both assets are over the cap of 3 paid jobs per asset already (art/animals ledger: dt_cat 6 jobs, rw_gull 4), so
  preflight needs his words (`--owner-ok`) for the cap as well, not only for credits.
- 128 is within the 150 a day cap. The cat's leap and run needed one retry each last time (+52 = 180): over the cap.
- Bigger cells: the cat's 24 x 24 cell and feet anchor in `scene.lua` `Sc.cat`, the gull's 48 x 44 in `critters.lua`.
- Preflight now takes the owner's size (night/25oct-prep, see 4).

## 2. River Walk scale calls (STATUS "Known, next": lamp posts, rowing boats)

Sheet: `rw_scale_calls_2x.png` (frames: `rw_lamp_frame_1x.png`, `rw_boat_frame_1x.png` from `art/rw-sample-screen`
80ec97f; script `art/gen/blockouts/rw_scale_calls_25oct.py`).

**Lamp posts** (approved art, 101 px = 2.2 m; five lamps, every one a checkpoint that lights up). Measured with the
foot on the upper promenade's back edge (y 174):

| Height | Metres | Lantern on screen? |
| --- | --- | --- |
| 101 px (now) | 2.2 | yes, a garden lamp beside the true-scale house (door 98 px) |
| 138 px | 3.0 | yes, lantern top at y 36 |
| 184 px | 4.0 | mostly cut, lantern top at y -10 |
| 207 px | 4.5 | no, the lantern is above the screen |

A checkpoint's light must be seen, so 4.0 m and 4.5 m only work with the lantern moved down the post or the light
drawn lower. 3.0 m reads with the house and keeps the light. Changing the lamp changes approved art: his call.

**Rowing boats** (2, movers Pepper rides; deck 56 px, drawn about 62 px = 1.3 m). A real rowing boat is about 3.5 m
= 160 px (magenta outline). BIBLE: "what she stands on is true scale". 160 px changes the harbour's play (deck
length, the gaps to the jetty, from/to of each boat), so it is a level change first, then art.

## 3. Merge prep: the approved pieces into a new `prod/integrate-*`

Board 20:16-20:18 approved: rw_home, rw_lime, rw_rail_bg (`art/rw-sample-screen`) and cloud8, park_log, pier,
skyline (`art/rw-fixes`). Not approved: gull and cat (`art/animals` stays out).

Local trial only (nothing pushed, no branch made): `prod/integrate` c1c37a4 + `art/rw-sample-screen` +
`art/rw-fixes` + `night/25oct-fixes`. One conflict: `CHANGELOG.md` (each branch adds a section at the top; keep
both). Checks on the trial: see STATUS "Night of 25 Oct" on `ops/night-25oct`.

## 4. The learning loop for tonight's two rejections

- `docs/art_learnings.md` rows (on `ops/night-25oct`): gull still too big at 44 px; cat too small at true scale.
- `tools/preflight.py` (this branch): an `owner_size` field (px, his words, the sheet he picked from) replaces the
  true-scale height check for animals only, and an animal must carry it (rules.json `size_sheet_kinds`). Without
  this, preflight refuses a 30 px cat (0.33 m x 46 = 15 px). Reviewed by an independent agent; its four findings
  fixed. Tested on eight sample jobs (no files written).
- The 218 SpriteCook credits of `art/animals`: verdict "rejected" for rw_gull and dt_cat, to write with
  `tools/ledger.py verdict` when that branch's ledger rows are merged (they exist only there).
