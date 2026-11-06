# City Park tall: the weirdness audit, fixed (art/cp-audit-06nov, 6 Nov 2026, 0 credits)

Every image: the same camera spot before (left, the merge of cp-pond, cp-props and cp-critters, 46f12bf) and after
(right), 1x frames from `tools/cp_built_frames.sh` (look on, no HUD), shown at 3x, in colour and in grey. Spot names:
camera y (0 high road, 24, 144 the path) and camera x.

| Fix | Frames | What changed | Method | asset_qa |
| --- | --- | --- | --- | --- |
| 1 pond and creek | 1_pond_y144_x0640, x1920, x0480 | water up to a waterline 16 px over its box under a short lit bank (lawn, lit lip, sunlit earth going damp and wet, granite stones at its foot); the bank curves round at each end; the basin's sides slope in under water; no dark cut beside a pond. Stepping stones: warm grey granite with moss (was pink), a ripple ring at the waterline | scene.lua `Sc.drawPondBank`, `Sc.stoneRipple` (code, by rule); park_stone colour map (`tools/fix_cp_audit.py stone`) | park_stone PASS |
| 2 rose arbour | 2_arbour_y144_x2240, y024_x2240 | slats and posts in the walks' timber ramp (were white paint, the brightest thing on screen); the vine winds round each post (was a zig-zag that read as crossing garlands) | `tools/build_cp_built.py` | slats, posts PASS |
| 3 play tower | 3_tower_y144_x2400 | a second post under each deck's free end: the upper deck stands on the lower one, the lower deck rests on the slide tower's roof | `tools/build_cp_built.py`, scene.lua `drawDeck` | cp_tower_post4x34, 4x6 PASS |
| 4 rope bridges | 4_bridges_y024_x1920, y024_x0640 | the tree ledges the walks run on from (PLANE TREE, ASH) are landings of the deck's build, same thickness and plank pitch, no outline between: one deck; hangers every 32 px (were 16) | `tools/build_cp_built.py`, scene.lua `drawTierProp` | decks, rails, landings PASS |
| 5 winch keeper | 5_keeper_y144_x0800 | the winch (WINCH prop, park_keeper_winch.png) was half behind the walk's right pylon: drawn 8 px right, both posts, the drum and the crank show | scene.lua `Sc.WINCH_DX` | art unchanged |
| 6 hedge | 6_hedge_y144_x0320 | top trimmed: rounded corners (r 16), a dip making two clumps (clear of the orange leaves), side notches; box and crawl gap unchanged; bones were already drawn in front | `tools/fix_cp_audit.py hedge` (116 px in edits.json) | WARN stray 3.2 % (was 3.1 %, organic leaves), as before |
| 7 climbing frame | 7_frame_y144_x2560 | the blue crate is the frame's hidden STEP box: now a yellow tread on legs; the frame: no top rail, no rungs between the bars (the cage), a strut at each bar's free end, a ladder up the left | `tools/build_cp_built.py` `build_frame` | park_frame PASS |
| 8 front layer | 8_front_y000_x0000, y000_x0320, y024_x2400 | the leaf front's clumps: whole leaves and a tapering bank, rounded ends (were cut straight); clumps drop clear of lamp bases and every ledge; the front bushes on the earth band: a thin back-lit rim on top | look.lua `Look.leaves`; `tools/fix_cp_audit.py bush` | park_bush PASS |
| 9 strata | 9_strata_y144_x0480, x1760 | path and earth rows of park_ground.png each their majority colour: flat bands, no speckle or flecks; the "black smudges" are the front bushes (fix 8) | `tools/fix_cp_audit.py ground` | park_ground PASS |

Left alone, as asked: the oak's climbing branches, the bare peach plain, the duck boat (both versions), the oak and
lime tree art. Not in the list and not changed: the duck boat's rope (critters' map) now shows as a thin line across
the pond's surface from the second stone to the right bank, where before it was lost on the dark band.

Checks (each with its own save folder): PEPPER UNCHANGED; flow 125/125; TILED CHECK PASSED; BACKDROP OK;
citypark_tall `--physics` 97/97; citypark_tall `--auto` GOOD GIRL; citypark `--physics` 85/85.
