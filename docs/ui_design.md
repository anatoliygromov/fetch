# FETCH! UI design (owner, 24 Oct 2026)

The UI is designed for the player, not copied from the target renders. The renders set the look (gold frames, ribbons,
chunky gold numbers, warm dark panels); layout and behaviour follow this page. Audience: a 7 year old on a 3.5 inch
640 x 480 screen (the game at 2x), and retro fans.

## Principles
- One panel style (the kit's gold 9-slice), one cursor (the bouncing paw coin), one smooth warm dim, no checker dither.
- One controls strip, always in the same place at the bottom of every menu screen: `(A) OK   (B) BACK` (labels change
  per screen, the place never does). Never buttons hanging off a panel.
- 2 to 4 choices per screen. Rows are plain outlined text on the panel; only the selected row is emphasised (gold
  text, the paw cursor, a 1 px bob). No box around every row.
- Pictures before words: icons and screenshots carry meaning; text at most 3 words for actions.
- Every move and choice has a sound and a little motion (6-frame ease in, 4-frame out).
- Fonts: 17 px for titles and ribbons, 13 px for labels and numbers, 7 px only for secondary text (the controls strip,
  subtitles), never for instructions a child must read.

## Glyphs follow the input device
The last device used decides the glyphs: on a gamepad (the RG35XX) round A and B coins in its layout (A right, B
bottom); on a keyboard keycaps (SPACE, ESC, arrows). Drawn as kit-style pieces that fit the 13 px row.

## Screens
1. **Title:** the title picture reprocessed from source_title/title_original.png on its native grid (no dim, no
   dither). Pepper animated: a 4 to 6 frame pant and blink loop cut from the 5 Oct Artlist videos on the same grid and
   palette; only her head changes between frames. Clouds and boats drift in code. The logo and a blinking PRESS
   START, no box.
2. **Main menu** (after Start): PLAY, LEVELS, OPTIONS as outlined text on the art, centred under the logo, paw cursor.
   PLAY continues from the furthest unlocked level. BEST RUN leaves the title.
3. **Options:** SOUND (9 segments), HARD MODE (toggle), CONTROLS. Gold panel.
4. **Controls page** (from Options and Pause): a drawn handheld with every button labelled with its action, plus the
   keyboard equivalents.
5. **Level select:** one big card per level: a real screenshot of the level, its number and name, 3 medal slots, the
   best time; left and right browse with a slide; locked levels show a padlock over the darkened picture. (A Stockholm
   map with Pepper walking between levels is the 1.0 version.)
6. **Pause:** gold panel, PAUSED ribbon, the level name and bones found; rows GO ON, SOUND, CONTROLS, QUIT.
7. **Tally:** a show, not a table: BONES counts up with a tick per bone, then FETCH, TIME BONUS, TOTAL (4 lines);
   medals pop in one by one; NEW BEST lands as a stamp; then the controls strip.
8. **HUD:** the owner's target layout (health top left, clock and time top centre, bones top right, lives bottom
   left). The clock stays (owner, 24 Oct). The score is smaller than the bone count; Pepper's head gets a light rim so
   it reads on the dark road.
9. **In-level hints:** a small bubble near Pepper with the button glyph and a picture of the action, at most 3 words,
   gone after the action is done. The portrait panel is for story moments only.
