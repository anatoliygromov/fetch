# preview/06nov-run: the drawn-asset sweep (6 Nov, integration)

The game's own frames of the three levels on preview/06nov-run before the rowing boats merge (look on, no HUD), made by
`python3 -I tools/layer_frames_tall.py <level> docs/review/06nov/preview/<level>` (LOOK_SWEEP=1, LOOK_STEP=320,
its own save folder per run).

| Folder | What |
| --- | --- |
| `riverwalk/` | 12 screens, 1 tier: `contact.png`, `contact_grey.png`, `frames/` (1x) |
| `citypark_tall/` | 9 screens x 3 camera heights: `contact.png`, `contact_grey.png`, `frames/` |
| `downtown_tall/` | 11 screens x 3 camera heights: `contact.png`, `contact_grey.png`, `frames/` |

Merged families: scale gate, cp-oak, dt-traffic, dt-props, dt-roofs, dt-built, rw-props, cp-pond (with cp-built),
cp-props, cp-critters, and the other session's preview/06nov. Not merged: cp-boughs, cp-backtrees.

Notes from the sweep (for the reviewers, not verdicts):
- City Park: the duck boat is cp-critters' cp_duckboat.png on the 80 px mover; park_boat_front.png is not drawn on
  the tall level (the flat City Park still draws it). The rose arbour slats (screens 8-9, high tier) are near white.
- River Walk: the two birches (x 460, 2918) replace tree_far; check_tiled reports this as a NOTE (map changed on purpose).
