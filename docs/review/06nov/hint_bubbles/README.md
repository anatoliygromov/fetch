# Hint bubbles in the light design (branch ui/hint-bubbles-06nov, 6 Nov, 0 credits)

Owner, 6 Nov, on a River Walk frame with the dark CRAWL bubble: "these also need to be in new lighter bubble design".
Every control hint now draws in the cream speech bubble of the talk lines (talk.lua T.drawBubble). Before is
`preview/06nov` (0201944a), after is this branch.

- `before/` and `after/`: the same frames. `<name>.png` is the full frame at 1x (320 x 240), `<name>_4x.png` a 4x crop
  round the bubble and Pepper (the same crop before and after).
- `hint_<level>_<nn>`: every control hint of the level in its own zone, gamepad glyphs (`hints.txt` lists each one's
  button and text); `_01_key` is the first hint with the keyboard's glyphs. Made by
  `python3 tools/hint_frames.py OUT --root <checkout>`. Levels: riverwalk 8, citypark_tall 13, downtown_tall 15,
  rooftops 7, soder 5, night 5. The bonus round has no in-level hints.
- `ui_hint_*`, `ui_nudge_*`: from `tools/screen_frames.py` (`--screenshots`): made-up places (Pepper high on the
  screen, the bubble beside her or under her; the grey box is her made-up sprite box) and the two nudges.

Checks: tools/layout_qa_menus.py hint checks PASS on all 54 in-level frames and the --screenshots frames (bubble inside
the margins, never over Pepper, glyph, picture and words inside on one centre line, at most 2 rows, the tail toward
her and its tip 1 to 5 px from her box). Looked at by eye at 4x, every frame.
