# Changelog

Each delivered build is a git tag. `git checkout v0.1` goes back to any of them.

## Branch `art/animals`: the gull and the cat redrawn (owner, 25 Oct: "it has holes and doesnt really look like a bird", "same for cat")
- **Method:** one still per animal from SpriteCook Pixel Engine Image at its exact game size, animated at 1x with pixel-engine-v1.5; frames only cropped, padded and aligned by whole pixels. `tools/build_animals.py`: palette snapped to each animal's own still (no flicker), specks out, small holes in the fur filled (outlined gaps left open), the 1 px dark outline closed, the cat's lone coat pixels merged into the coat.
- **Gull (riverwalk/art/gull.png, 8 frames 48 x 44):** wingspan about 44 px, a little smaller than life on the owner's call (the 58 px first version was "massive"). A looping wingbeat; frame 3 (wings swept back) is the swoop. critters.lua: 8 frames, body centre (28, 18), the nest gull's feet on row 28.
- **Cat (riverwalk/art/cat.png, 8 x 3 cells of 24 x 24):** the owner's Abyssinian at true scale, 16 px sitting (owner's pick; was 30 px). Rows idle (tail curl, ear twitch, blink), leap (crouch, arched back, spring, up, top, down, land), run (stand, gallop). scene.lua: 24 px cells, feet at (12, 23).
- asset_qa: both WARN only (wingbeat size changes, a leap and a flight leave the ground). Credits: SpriteCook 218 for the family (stills 36, animations 182, two of them cat retries with more room), within the owner's yes: 180, then about 38 for the smaller gull.
- Checks: PEPPER UNCHANGED, flow 125/125, QA 0 problems (River Walk, Downtown tall). Frames: docs/review/25oct/animals/.

## Branch `ops/board-25oct`: the owner's board review turned into the art backlog (25 Oct)
- 42 board items: 1 approve, 12 fix, 28 redraw, 1 open. **docs/art_backlog.md** groups them into families per level
  (tier, method, order), River Walk first. BIBLE: no automated clean pass on existing art (owner, 25 Oct); a row in
  the rejection log. No art changed, 0 credits.

## Branch `art/tall-backdrop-rule`: back buildings and front trees taller than the viewport (25 Oct)
- Owner rule (25 Oct): back-layer buildings and the front row of trees are taller than the viewport; their top is never
  on screen. In BIBLE section 3 and `art/gen/rules.json` (`taller_than_viewport`).
- **tools/check_backdrop.py** fails any such decor prop whose top is on screen. River Walk today: HOME (top y 39),
  TREE (47) and the near tree at x 1056 (39) fail; the gable (-1) and cafe (-31) pass. City Park and Downtown draw their
  art in scene code and are checked by eye in their screen sweep for now.
- Added to the pre-merge checks (BIBLE section 8) and the rejection log. The fix is part of the River Walk sample
  screen (STATUS). No art changed, 0 credits.

## Branch `ops/workflow`: the workflow the owner can trust, enforced in code (25 Oct)
Built on `prod/integrate` with `art/preflight` merged. Tools and docs only; no game file changed, 0 credits.
- **docs/WORKFLOW.md:** the order of work for assets (families of 4 to 6, tiers A/B/C, 10 steps) and levels; the owner
  touches the work twice (the spend line, the board); session start and end; the learning loop.
- **tools/pipeline.py:** each asset's steps as a state machine (`art/gen/status/`); a step is refused until the one
  before it is done and its proof exists (render, cut with no fails, in-game frame, .aseprite polish, a 9-item review
  by a reviewer who did not make it, the owner's board approve).
- **tools/ledger.py, art/gen/ledger.csv:** every credit (plan, spent, verdict) and yield per tool and family. The 3-25
  Oct history is backfilled from the credit audit.
- **tools/preflight.py:** now refuses Artlist models for game pixels (owner, 25 Oct: references only), jobs without a
  family, tier or slot, more than 3 paid jobs per asset and days over 500 Artlist / 150 SpriteCook credits (unless
  `--owner-ok`); writes the ledger plan row. SpriteCook models in `art/gen/rules.json` with today's prices.
- **tools/make_palette.py, art/palettes/riverwalk.gpl:** River Walk's locked palette (56 colours, all from approved
  art; Pepper's kept whole). **tools/grid_cut.py** snaps every new sprite to it.
- **docs/BIBLE.md** (sections 4, 7, 8, 9), **docs/STATUS.md**, **docs/art_learnings.md** (with the rejection log),
  docs/art_ledger.md points to the new ledger.
- Checks: PEPPER UNCHANGED (4591 steps), flow 125 of 125.

## Branch `art/title-props`: the title's thin built objects redrawn by rule (25 Oct)
- **Props (art/source/title/tools/props.py, bg_noplate_320.png; the old layer kept in regrid/pre_props/):** sampling the painting broke thin man-made objects, so each is drawn once on the game grid from positions, widths and colours measured on the painting, palette colours only: the left lamp (finial, roof with its shade face, mid face and a 2 px lit band down the right edge as an even staircase to the brim's lit end, tan lip, two glass panes with a 1 px mullion and a frame tapering in even 4-row steps, glow orange / amber / cream, rim, collar, neck, ring, a straight post x 31..35 with ONE unbroken highlight column, moulding, base and plinth round Pepper's outline); the far quay lamp at the same design a third the size (two yellow panes with mullion and frame, 2 px post); the bench (three slats with lit top edges, end frame, seat, cross bar, cast legs); the bin (lid, four even slats, base ring); both big railing posts identical (6 px shaft with one highlight column, cap lit on the right); straight 1 px masts on the left boat (with even rigging and boom), the small boat and the boat at x 256 (with its hull). Old lamp pixels take the colour round them nearest the painting there; the sky by the left post is cleaned of specks. Rebuild: `python3 art/source/title/tools/props.py` then `build_title_regrid.py`.
- **Checks:** new tools/props_check.py (drawn as specified, no new colours, no L-corner doubles in lines and edges, highlight and outline columns unbroken where visible): ALL PASS. stray_check 0, check_pepper PEPPER UNCHANGED, check_flow 125 of 125. Crops at 8x (painting, before, after): out/props_*_8x.png (not committed).

## Branch `ui/title-regrid`: the regridded title picture (24 Oct)
- **The picture (riverwalk/art/title/base.png):** the approved regrid composite: the background without the old PRESS ANY KEY plate (railing and pavement there now), Pepper's head and bandana, the logo and the tagline plate, in that order, with the logo and the plate baked in so nothing old can peek round them. Sources in art/source/title/regrid/ (copied as approved, pixels unchanged); `python3 art/source/title/tools/build_title_regrid.py` rebuilds base.png, the layers and riverwalk/title_regrid.lua from them (build_title.py runs it at its end). composite.png there is the reference the idle title is checked against.
- **Logo and plate (title.lua):** new variants T.LOGO = "regrid" and T.TAGLINE = "regrid", the defaults: each layer cropped to its box and drawn exactly where it sits in the composite (logo 124,17, plate 149,77; the plate over the logo, the composite's order). The logo's shine (logo_hi_regrid.png) and 160 twinkle points are cut the way build_title.py cut them for the older logos (the fill's upper edges and its lightest stripe, every 3rd, above y 72). The older logos and plates stay selectable. T.CX is 220, the new plate's centre (frame x 150..290), so PRESS START and the menu rows sit centred under it.
- **Pepper still (T.PEPPER_ANIM = false):** the old mouth and eye frames do not match the new Pepper; the overlays are skipped, the code kept.
- **Bird (T.BIRD_ANIM = false):** the old flapping overlay is a jagged two-tone stroke next to the new art's clean 1 px V, so the painting's bird stays in base.png and the overlay is off (build_title_regrid.py BIRD_OUT paints it out, for when an overlay in the new style exists).
- **River sparkles (T.SPARKLES):** the old streaks landed on boats, the bridge and the sail reflections in tan colours; they are now the new water's own 24 light ripple streaks (open water only), each dimmed to the water round it in its off phase, so base.png keeps every ripple as painted.
- **Checks:** tools/title_frames.py (new shots title_shine_22/24/26 and title_star_0..5; the older-variant shots restore the defaults before the menu shots). The idle title differs from the composite in 27 pixels, all animated (26 ripple pixels in their off phase, 1 twinkle star pixel); the menu frames differ only inside the menu, PRESS START and the strip bodies (and 1 ripple pixel). layout_qa_menus.py ALL PASS, check_pepper.sh PEPPER UNCHANGED, check_flow.sh 125 of 125.

## Branch `ui/umlaut`: Ö as a capital (24 Oct)
- **Ö (art/source/ui/v8/font, style8.py, build8.py, uifont.lua):** the Ö of SÖDER HILL read as a lowercase ö (a short O under its dots). Now it is the capital O itself in the 7 and 13 px fonts and an O shortened by 1 row in the 17 px font (so the dots clear the level card's picture frame), with the two dots drawn above the cap line, 1 px clear of the O, as 16-bit fonts do. Fonts can carry accent rows (ABOVE): the atlas cells grow upward by asc rows (7 px: 2, 13 px: 3, 17 px: 3) and the text's box and every layout stay as they were. New frames: select_5_pad, pause_soder, font_umlaut (the word in every size and style). Checked at 8x: out/umlaut_8x.png (not committed).

## Branch `ui/review-fixes`: fixes from the independent screen review (24 Oct)
- **1 Locked level cards (flow.lua, tests_cards.lua, art/ui/cards rooftops, soder, night):** the pictures shot again by tools/card_shots.py with the greybox debug labels (CHIMNEY STACK, CRATES, BIKES) and the placeholder bones left out; unlocked cards unchanged. The padlock sits three quarters across the picture, clear of Pepper (F.SEL.PEPPER); a locked or missing level's strip shows BROWSE and BACK only. layout_qa_menus.py checks the padlock is on the picture's middle line, clear of Pepper, and the two-item strip.
- **2 Medals not won (art/source/ui/v8 screens8.py, build8.py; art/ui/medal_*_off.png):** an empty dark socket where the disc would be: ink edge, a thin 1 px gold rim lit from the top left, the hollow in the kit's dark brown with shade under the upper rim; no ribbon, no picture, nothing bronze. Placed by its medal's box, so the level cards and the tally keep their layout. Won medals unchanged.
- **3 Story text for a child (level files and their Tiled maps and exports, stage.lua, night.lua, chase.lua, levels.lua, talk.lua, uifont.lua, the v8 fonts):** every intro card, story card and Mia line at most 6 short words a 7 year old knows (no FERRY, PONTOON, JETTY, MAGPIE, CANAL; BOAT, RAFT, DOCK, BIRD, WATER instead); no button names in story text: the Night intro no longer says HOLD L1 OR Q, sniffing is taught by a hint bubble (HOLD SNIFF with the L1 shoulder or the Q key and a sniff picture), like every other action; River Walk's story card no longer says "in the park". SÖDER HILL with the Ö: drawn on the 7, 13 and 17 px grids (the full stop's dots over a shorter O); uifont.lua reads text as UTF-8. Every change, old and new: out/text_changes.md. Flow tests updated where they read old text: the magpie line is now found by BIRD STILL (two checks), and sniff is a known hint button. Screens: talk_3rows (a made-up three-row line) is now talk_longest (the longest real line); new hint_sniff, hint_sniff_key.
- **4 Hint bubble pictures (screens8.py, talk.lua; art/ui/pic_*.png, new h_a/h_b/h_x/h_y):** every action picture now shows Pepper in her own colours (black Labrador, pink bandana, her exact palette), drawn on the grid at half her size after her approved frames (stand, crouch, jump, crawl, sniff, bark; her frames only read), each pose about 20 px tall in a 1 px light rim so the black dog reads on the dark bubble; pictures 32 to 39 x 22 to 26. SNEAK is the low crouch with two quiet steps, no "z". The face buttons in the bubble are 15 px coins with the 7-row letter in ink on a flat gold face (legible at 1x); strip coins unchanged. Words unchanged (at most 3).
- **5 One name for the bonus (bonus.lua, screens8.py ribbon_wide):** FETCH FRENZY! is the only title: the intro card drops A GOLDEN BONE BONUS and the round's name (BALL RALLY, STICK TIME, FRISBEE FLOAT stay only for the checks); under the ribbon CATCH WHAT MIA THROWS! and the goal row (ball, 11 CATCHES, +1, Pepper's head); the card is 26 px shorter. The ribbon is 16 px wider, the words 14 px from its ends. When every throw was caught before the clock ran out, the end says ALL CAUGHT! instead of TIME UP! (drawing only, B:allCaught reads the round's state). layout_qa_menus.py checks every ribbon's words keep 4 px from its ends; new frame bonus_allcaught.
- **6 Pieces off panels (flow.lua, hud.lua):** the level card's HARD badge sits on the picture's top right corner, fully inside the card (it straddled the panel's top border). A tally with NEW BEST! or HARD gets a 25 px foot row inside its panel: the stamp lands at its right, 8 px in from the frame (it hung below the panel), the HARD badge on its left (it sat on the panel's corner). Over menus and cards the sound toast takes the controls strip's place for its moment, in the hint bubble's frame (18 px tall), so it never covers a card's words (it covered the level card's medals and time); while playing it stays under the HUD. layout_qa_menus.py checks HARD fully inside a card (10 px in) or on the ribbon, the stamp fully inside a panel, the toast over nothing written; all three fail on the old frames.
- **7 HUD score (hud.lua U.status):** the score is drawn in the 7 px font (secondary text, docs/ui_design.md), smaller than the 13 px bone count, right-aligned under it with a clear row between. layout_qa_menus.py checks it on every HUD frame.

## Branch `ui/panel-hud`: no HUD row under the cards (24 Oct)
- **Drawing only (main.lua, bonus.lua, flow.lua):** while a centred card is up over the game (level intro, story, pause and QUIT?, controls from the pause, GAME OVER, GOOD GIRL! tally, FETCH FRENZY intro and result) the HUD row is not drawn at all; the warm dim and the controls strip stay. The pause already shows the bones found, the tally the level's points. The ending card moved 4 px down and a card dropping in never rises above the 4 px top margin, so no ribbon or frame is cut by the screen's top. Talk panel and hint bubbles unchanged. Checks: layout_qa_menus.py checks no HUD piece outside a card's panel and the 4 px top margin; layout_qa8.py checks no HUD row under a card (instead of filtering it out). Sheet: out/panel_hud_before_after.png (not committed).

## Branch `ui/hud-v8` step 3: every remaining screen in the kit (24 Oct)
Follows docs/ui_design.md. Drawing only: logic, inputs and saves as they were unless a line says otherwise. Frames:
`python3 tools/screen_frames.py` (out_ui/step3/frames, colour and greyscale at 3x), checks: `python3
tools/layout_qa_menus.py out_ui/step3/frames`.
- **Level select as cards (flow.lua F.drawSelect, F.selectCard):** one big card per level on the title picture under the
  warm dim: the kit's gold panel, a LEVEL n ribbon over its top edge, the level's picture in a thin gold frame
  (frame_s), its name in the 17 px font, the three medals won from the save (each with its picture: heart NO HIT,
  bone ALL BONES, clock PAR) on the left of one row and the clock, the best time and the best points on its right.
  Locked: the picture darkened with a big gold padlock on it (a level without its file: COMING SOON). Left / right
  (up / down too, so nothing learnt stops working) browse, wrapping as before; the next card slides in over 0.12 s
  (ease out) with a new `slide` sound (sfx.lua). Gold arrows either side nudge out and back, a dot per level under
  the card, the controls strip `BROWSE  (A) PLAY  (B) BACK`. Unlocking and saves unchanged.
- **The pictures (riverwalk/art/ui/cards/<name>.png, 216 x 118):** native 1x crops of the game, no scaling, shot by
  `python3 tools/card_shots.py` (riverwalk/tests_cards.lua, `love riverwalk --cardshots`: each level alone, Pepper
  at its characteristic spot, the camera settled, no HUD): River Walk by the ice cream kiosk, City Park by the goose
  and the leaf pile, Downtown at the market, Rooftops on the chimney stack with the gull, Soder Hill under the lamp,
  Night Harbour in the lantern light. (Rooftops, Soder Hill and Night Harbour are still greybox, so their pictures
  are too.)
- **Level intro card (flow.lua F.drawIntro, main.lua):** the smooth warm dim (the dotted checker is gone here), the
  kit's gold panel with the LEVEL n ribbon over its top edge, the level's name in the 17 px font and its story (intro
  lines 3 and 4) in the 13 px font, each line split where its halves are most even when it is wider than the card
  (F.wrap); the card drops in (6 frames, ease out). The controls strip `(A) GO` replaces the blinking PRESS ANY
  BUTTON (any button still starts the level). The card goes centred above the strip, else at the top, else just
  above the strip, the first that misses Pepper (F.cardTop; if none does, the one that covers least of her).
- **Talk panels (talk.lua T.sayLayout, T.drawSay):** the girl's (Mia's) lines in the kit's gold panel sized to the
  words (13 px cream, at most 188 px a row, split where the halves are most even, up to 3 rows), her portrait (the
  same talking loop, cut to head and face, 42 x 38, on a light warm window) in the thin gold frame on the panel's
  side, 8 px over its end, standing up out of it (Pepper's portrait, for a line of hers without a button, on the
  left). Bottom: the group's bottom at the margin, the right side (clear of the lives); top: under the HUD (y 46),
  when Pepper is low; never over her (same rule and timings). The panel rises 6 px into place over 6 frames.
  No continue glyph: these lines go by themselves (4.5 s, or when the zone is left) and no button moves them on
  (A is jump), so a glyph would teach a wrong button; A only goes on on the story card, which shows it.
- **Flow test change (tests_flow.lua "hints: all fit the panel"):** it checked the old blue panel's drawing (2 rows,
  scale 2 letters) for the girl's lines too; now a girl's line may take 3 rows of the 13 px font. Pepper's lines
  keep their checks.
- **In-level hints and nudges (talk.lua T.bubble, T.drawBubble, T.drawNudge):** Pepper's control hints leave the
  portrait panel (it is for story moments only) for a small bubble near her: the kit-style bubble (a 9-slice: ink
  outline, a 1 px gold rim, the dark warm fill) with a tail toward her, the button as the device used last shows it
  (the gamepad's coin or d-pad, or the keyboard's keycap), a picture of the action (pic_<kind>, 28 x 20 on the grid:
  Pepper as a cream pictogram with her pink bandana, what she uses in gold: run, hop, big jump, climb, crawl, duck,
  stay on, drop, bounce, pick up, give, bark, sneak) and at most 3 words in the 13 px font, one or two rows. Placed
  above her head, else beside her (the tail on the side toward her), else above at the screen's top, else under
  her; always on screen and never over her sprite. It rises 4 px in over 6 frames and goes when the hint stops
  applying (same rules and timings). A nudge for the same button makes the bubble bounce (0 to 3 px, away from her);
  a nudge for another button (a guess while pushing) gets its own bouncing bubble (Down: CRAWL, A: HOP), replacing
  the big round button over her head.
- **Hint words shown (the level files keep their texts; talk.lua T.hintRows):** "TAP: HOP" -> HOP (10 hints);
  "HOLD: BIG JUMP" -> HOLD / BIG JUMP, "HOLD: CLIMB" -> HOLD / CLIMB, "HOLD: SNEAK" -> HOLD / SNEAK, "HOLD: STAY ON"
  -> HOLD / STAY ON (two rows, no colon); "BARK: SHOO!" -> BARK / SHOO!; "STOP, THEN HOP" -> STOP / THEN HOP;
  "BOUNCE ON IT" -> BOUNCE / ON IT; "BOUNCE ACROSS" -> BOUNCE / ACROSS; "RUN, HOLD: BIG JUMP" (the lab level, 4
  words) -> HOLD / BIG JUMP. Unchanged: PICK UP, GIVE, CRAWL, DUCK!, BARK!, RUN.
- **Flow test change (tests_flow.lua "hints: all fit the panel"):** Pepper's hints are checked on the bubble: at most
  2 rows and at most 3 words shown (was: one row of scale 2 letters in the old panel).
- **Pause (flow.lua F.drawPause, F.pauseCard):** the warm dim, the kit's gold panel with the PAUSED ribbon, the
  level's name (7 px) and the bones found (the bone and the count, 13 px gold); the rows GO ON, SOUND, CONTROLS,
  QUIT as plain outlined 13 px text, only the selected row gold with the paw coin before it (eased between rows,
  1 px bob), SOUND's 9-segment meter at the right; the row boxes and the A / B coins and tabs hanging off the frame
  are gone; the controls strip `(A) OK (B) BACK` (`CHANGE (B) BACK` on SOUND). The quit question in the same card:
  QUIT TO MENU? (13 px gold) over NO / YES, QUIT. The card goes where it misses Pepper (F.cardTop).
- **CONTROLS in the pause (new row, main.lua pauseAction):** opens the controls page over the warm-dimmed level;
  B or A goes back to the pause, Start still goes on playing. QUIT moved from the third row to the fourth.
- **Flow test changes (tests_flow.lua):** "pause: QUIT asks first", "pause: YES, QUIT goes to the menu" and the
  hard mode test's way out through the pause press Down once more (QUIT is the fourth row now); new checks "pause:
  CONTROLS opens the controls page" and "pause: B goes back from the controls page". 124 of 124 pass.
- **Tally as a show (flow.lua F.tallyPlan, F.tallyStep, F.tallySkip, F.tallyCard):** the warm dim, the kit's panel
  under the arched GOOD GIRL! ribbon. BONES counts up from 0 with a tick per bone (at most 1.5 s), then FETCH (the
  level's bonus line), TIME BONUS and the TOTAL (the level's points, counting up with a tick each 500 as before),
  4 lines, each sliding in with its picture (the bone, the ball, the clock), 7 px label, 13 px gold value. Then the
  three medals pop in one by one (their pictures: heart, bone, clock; a sound for won, a thud for not) with their
  names; the clear time, the best time (gold when it is new) and SECRETS found in the small font; NEW BEST! lands
  as a red stamp across the frame's bottom right (a new best score or time) with a thud (new `stamp` sound); then
  the controls strip `(A) OK`. Same numbers as before; the run's score still counts on the HUD.
- **Any button skips the show (main.lua anyKey):** a press during the show jumps to its end (all numbers shown); the
  next press goes on as before. The update moved from main.lua into F.tallyStep (the show's own timetable; the
  tally is done when the show ends, about 4 to 6 s, was 1.8 s).
- **Flow test change:** new check "tally: any button skips the show to its end" (the clean clear). 125 of 125 pass.
- **Story card between levels (flow.lua F.drawStory, F.storyCard):** a story moment, so the portrait panel: the warm
  dim, Mia telling the outro in the kit's gold panel (13 px, each line split where its halves are most even), her
  portrait (talking while it is read) in the thin gold frame on the panel's right end; the card drops in; after
  2 s the strip `(A) GO ON` (only A, as before) replaces the small blinking A button.
- **GAME OVER (F.drawOver, F.overCard):** the warm dim, the gold panel with the GAME OVER ribbon, TRY AGAIN / MENU as
  plain outlined text (only the selected one gold, the paw coin before it, eased), the strip `(A) OK`.
- **The ending (F.drawEnding):** the title picture under the warm dim, the gold panel under the arched GOOD GIRL!
  ribbon: the outro (13 px), FINAL SCORE (7 px) and the score (17 px gold), NEW BEST RUN! (13 px gold, blinking) or
  BEST RUN (7 px), THE END (17 px gold), THANKS FOR PLAYING (7 px), the strip `(A) OK` after 2 s.
- **FETCH FRENZY (bonus.lua, hud.lua U.bonusStatus):** the HUD row in the v8 style (the ball and CATCHES against the
  goal, gold and +1 once reached; the watch and the seconds, the last 5 blinking; the points); the intro card (the
  gold panel, a new wide ribbon FETCH FRENZY!, A GOLDEN BONE BONUS, the round's name in 17 px gold, CATCH WHAT MIA
  THROWS! in 13 px, the goal as the ball, 11 CATCHES, +1 and Pepper's head; was "11 CATCHES: EXTRA LIFE"; the
  strip `(A) GO`); READY..., GO!, the last seconds and TIME UP! in the 17 px gold font; the result card like the
  tally (CATCHES, IN THE AIR, POINTS; EXTRA LIFE! with Pepper's head, or GOOD TRY, PEPPER! and the goal in 7 px;
  the strip `(A) OK`); the +100 pops in the 7 px font.
- **The sound toast (hud.lua U.volumeToast):** a small gold panel with SOUND (7 px) and the 9 segments, under the HUD
  while playing, above the controls strip over menus and cards.
- **Dev panels (main.lua):** the tuning panel (Tab) and the debug line (G) in the 7 px font on the warm dark.
- **Old code removed:** hud.lua's blue signs, boxes, prompt banner, 5x7 text, the dotted checker dim, the old lock, dog,
  medal, volume bar and HARD tag, the code-drawn picture signs; talk.lua's round button glyphs and the old panel;
  flow.lua's checker backdrop. Nothing in the UI uses bigfont.lua any more.
- **All screens:** out_ui/step3/all_screens.png (every UI screen at 2x, 24 frames: title, menu, options, controls,
  level select, intro, talk, hints, nudge, pause, quit, controls from the pause, tally, story, game over, ending,
  bonus intro / play / result, sound toast), looked at: nothing old left.
- **Left as they are (not UI screens):** the in-world tells drawn with bigfont.lua ("!" over a hissing goose, the cat,
  a bike; "?" when an animal hears a bark; chase.lua, critters.lua, scene.lua, roofs.lua, night.lua) and the greybox
  prop labels (CAT, HOLLOW LOG, CRATES, TERRACE...; scene.lua, setpieces.lua), which go when those levels get art;
  the dithered dust puffs (extras.lua), pavement fades (scene.lua) and lantern light (night.lua) are level art;
  the title's logo dither is the title track's.
- **Pieces (art/source/ui/v8/tools/screens8.py, built by build8.py):** arrow_l / arrow_r, lock / lock_big, dot_on /
  dot_off, frame_s, medal_<kind>_on / _off, bubble and its tails, ball, stamp, pic_<kind>, g_right (the d-pad, right lit), ribbon_wide.

## Branch `ui/hud-v8` pilot 2: the title on its native grid, Pepper pants and blinks, the new main menu (24 Oct)
Follows docs/ui_design.md (the owner's UI design, 24 Oct). Stops here for the owner's yes.
- **Title picture (art/source/title/tools/build_title.py):** the painting sampled one colour per cell on its 7.5 px
  grid (320 x 239, the last row repeated once), the sample window registered to the drawn pixel inside each cell (the
  painting's grid drifts a pixel or two, so one fixed phase broke outlines such as the wink); 62 colours from a
  two-group k-means (22 for Pepper's coat, bandana, tongue and eye, 40 for the rest), no dithering. Lone pixels
  5.8 % -> 4.4 % (Pepper 4.5 -> 4.2, city 7.7 -> 5.6, logo 7.1 -> 4.9). The painting's PRESS ANY KEY box is taken out
  and the railing behind it rebuilt from the painting's own rows.
- **Pepper animated:** a calm pant (rest, rest, tongue half down, down, down, half; 8 fps) whose tongue outline comes
  from the owner's video t2 (frames 18 and 21, registered to the still on her head by a scale and translation
  search) with the still's own tongue pixels stretched to it; a blink every 3.4 to 4.6 s (half shut, shut, half; her
  open eye, drawn on the still's colours). Only the changing pixels are drawn (mouth.png 28 x 20, eye.png 18 x 19);
  every other pixel is the still. The sparkles, the bird and the logo shine stay; the lamp glow overlay is gone
  (off-palette blend); clouds and sailboats stay still (not separable). tools/make_title.py is superseded.
- **Title flow:** the logo and a blinking PRESS START (13 px gold, no box, no dim) on the menu's centre line (x 220.5,
  the subtitle banner's centre). Then the main menu: PLAY, LEVELS, OPTIONS as outlined 13 px text on the picture,
  only the selected row gold, the paw coin before it (eased 0.1 s between rows, 1 px bob). PLAY starts the run at
  the furthest open level (was: always level 1); LEVELS is the level select as it was; BEST RUN is off the title
  (still on the ending).
- **OPTIONS:** the warm dim, the gold panel and a wider ribbon; SOUND (9 segments: the volume is now 0 to 9, so the
  pause's meter shows 9 too), HARD MODE (a switch: A, left or right), CONTROLS (a page: the RG35XX drawn on the grid,
  a row per control with its button, its action and its keyboard key(s)).
- **The controls strip (hud.lua U.strip):** one component at the same place on every menu screen (centred, bottom at
  the margin), `(A) OK  (B) BACK` style with 7 px labels; glyphs follow the last device (input.lua I.last: 13 px gold
  A / B coins on a gamepad, SPACE / ESC keycaps on a keyboard). Used on the main menu, OPTIONS and CONTROLS; the
  pause and the tally switch to it in the next step.
- **Pieces (art/source/ui/v8/tools/menu8.py, built by build8.py):** button coins A B X Y, L1 R1 START pills, d-pad and
  d-pad left / right, 11 keycaps, the HARD MODE switch, the handheld, ribbon_menu.
- **Flow test changes (riverwalk/tests_flow.lua):** "menu: START GAME is selected" -> "menu: PLAY is selected";
  "game over: TRY AGAIN restarts the level" now expects the last level (PLAY started the furthest open one); HARD MODE
  is reached through OPTIONS (down, down, A, then down, A); new checks: OPTIONS' SOUND left / right, CONTROLS opens
  and B goes back, B from OPTIONS goes back to the menu. 122 of 122 pass; PEPPER UNCHANGED.
- **CONTROLS: a CRAWL row** (Down: crouch and crawl) after JUMP, the d-pad with its down arm lit / the down-arrow key;
  MOVE shows the d-pad left / right and the left / right keys; 8 rows, pitch 20 -> 17 px (the font unchanged). The
  title build's source video art/source/title/video/t2.mp4 is committed (t1, t3 are not).
- **The logo and the tagline rebuilt on the grid (art/source/title/tools/logo.py, 0 credits):** each letter's silhouette
  from the native grid fitted with straight segments (even staircase steps), the painting's 2 px navy outline and 2 px
  depth, one navy block behind the letters as painted; fill: a highlight row on the top edge, three hard bands
  (yellow, gold, orange) and a red-orange lip, the painting's own colours, no dither, no lone pixels. The paw redrawn
  mirror-symmetric. The tagline plate redrawn (navy, light rim, even cut corners, 154 x 19, centred on x 220.5) with
  the v8 7 px font in two versions for the owner to pick: THE CITY DOG ADVENTURER (default, title.lua T.TAGLINE =
  "caps") and The City Dog Adventurer (new hand-drawn lowercase in the same family, "lower"). Both are layers over the
  painting, whose old logo and plate are painted out with the sky; the shine runs on the new letters. Gate:
  tools/logo_gate.py (before / after at 4x and 8x, the checks).
- **The logo's fill, three versions (title.lua T.LOGO):** "gradient" (default: the painting's yellow-to-orange ramp in
  six steps, each step's first two rows an ordered 2 x 2 checker with the step above, phase fixed to the screen, a
  highlight row on top), "steps6" (the six steps hard) and "bands" (three bands and a lip). Same silhouettes, outline,
  depth and paw; logo_<mode>.png and logo_hi_<mode>.png. The unused eye_closed.png and press_off.png are removed.
- **"clean" logo (the new default, T.LOGO = "clean") and 90s sparkles:** the painting's own logo pixels (depth, bevel,
  highlight streaks, outline, paw) with only the speckle replaced: per letter and row the dithered yellow / gold /
  orange pixels average to a level (smoothed over 3 rows), set as a solid colour or an ordered 2 x 2 checker of its
  two nearest ramp colours on a fixed screen phase; lone pixels a shade off their neighbours take their colour;
  8 one-pixel outline wobbles straightened. Twinkle stars (stars.py: 3 sizes, 6 frames grow-flash-shrink, white and
  pale yellow) pop one at a time every 0.6 to 1.4 s on the letters' upper edges and highlight streaks (a seeded
  schedule, the same every run), and the shine sweeps every 5 to 7 s instead of 3.6. Both run on every logo version.
  The title GIF is now 9 s at 12 fps.
- **Title picture cleanup (art/source/title/tools/cleanup.py, head.py; masks in art/source/title/masks):** 19
  materials (coat, nose, eye, tongue, bandana, trunk, leaves, lamp, lantern, stone, sky, clouds, city, water, boats,
  railing, pavement, bench, flowers); each gets a small ramp of the painting's own colours (coat 5, bandana 4, tongue
  4, leaves 5, water 4, sky its 4 bands ...); textured shading turned into clean tone areas (a masked blur, the steps
  dealt out by rank so each keeps its share); lone pixels and 2-pixel crumbs merged per material; near-twin colours
  merged (Pepper's ramps protected). Pepper's eye and nose keep the painting's pixels, her dark lines are closed, the
  wink is redrawn by hand as one clean lid stroke with three lashes. The far city keeps its texture (its windows).
  Lone pixels 4.2 % -> 1.0 % (Pepper 3.8 % -> 0.4 %), 62 -> 48 colours. The pant and blink frames are rebuilt from
  the cleaned head. Gate: tools/cleanup_gate.py.
- **Gates:** tools/title_frames.py (frames at 3x, colour and greyscale, the title loop GIF at 2x),
  tools/layout_qa_menus.py (226 checks, all pass), tools/pilot2_cards.py: out_ui/pilot2/card_title.png and
  card_menus.png.

## Branch `ui/hud-v8` step 3: the level tally "GOOD GIRL!" to the owner's target (23 Oct, night)
- **Card (flow.lua, drawing only; same data and timing):** the smooth warm dim, the kit's gold panel 230 x 113, an
  arched ribbon (a parabola: runs shorten evenly to the ends; tails folded behind) with GOOD GIRL! in the 17 px big
  font, two columns in the 7 px small font: BONES, the level's bonus (FETCH), SECRETS, TIME BONUS, then SCORE in
  gold (counting up); TIME, BEST and the three medals (15 px: a gold paw coin on a red ribbon when won, a plain bronze
  disc when not) with NO HIT, ALL BONES, PAR 1:47. NEW BEST SCORE! / NEW BEST TIME! blink under SCORE; PRESS ANY
  BUTTON sits on the frame's bottom line; HARD on a red plate on the frame. Centred, or at the top when Pepper would
  be under it (it then ends at row 136, above her on the ground).
- **Checks:** layout_qa8 ALL PASS on all 11 frames (62 on the tally: columns' edges, every label with its value on its
  line, even pitch, medals and labels on one line 3 px apart, centred, nothing overlapping); qa_card PASS for
  medal_on, medal_off, ribbon_tally, font7_cream / gold / dim, font17_ink; check_pepper PEPPER UNCHANGED;
  check_flow 116 of 116.

## Branch `ui/hud-v8` step 2: the pause to the owner's target (23 Oct, night)
- **Dim:** one full-screen dark brown rectangle (40,20,12) at 75 % (hud.lua U.dimWarm); no checker dither.
- **Card (flow.lua, drawing only; the menu logic and inputs unchanged):** the kit's gold panel as a true 9-slice
  (hud.lua U.panel, kit/frames/panel_menu), a straight PAUSED ribbon (13 px ink letters) over its top edge, the level in
  the small font, three rows 140 x 19 (selected: gold with the 21 px paw coin over its left end; others dark and inset),
  SOUND with one segment per volume step (10, the game's range) in a dark trough, the A / B coins (23 px) on the frame's
  bottom line with OK / BACK on orange tabs hanging behind it. QUIT asks in the same card (QUIT TO THE MENU?, NO /
  YES, QUIT). The card is centred, or at the top when Pepper would be under it.
- **Checks:** layout_qa8 61 PASS on the four pause frames (rows, pitch, labels' edge and centre lines, everything
  centred, cursor gap 3, the A / B group centred, every edge pixel the one outline or shadow colour); qa_card PASS
  for btn_a, btn_b, tab, coin_paw, row_on, row_off, seg_on, seg_off, ribbon_pause; check_pepper PEPPER UNCHANGED;
  check_flow 116 of 116.

## Branch `ui/hud-v8` step 1: the HUD to the owner's target (23 Oct, night)
Built on main v0.6. 0 credits, no generated pixels: everything drawn on the pixel grid. Owner direction: the three
target renders (art/source/ui/ref) are "this exact layout and quality"; fonts on a grid, one family.
- **Fonts (art/source/ui/v8/font):** one family, three sizes, each glyph drawn pixel by pixel: **7 px small** (new:
  stems 2, bars 1, corners cut 1, for body text and subtitles), **13 px mid** (v7 unchanged, plus a comma), **17 px
  big** (new, for titles: stems 4, bars 3, serifs 2 rows; kit/font_big, generated lettering, only as the guide).
  geomqa8.py on all three: 0 issues (one cap line and baseline per size, symmetric letters mirror-symmetric, no lone
  pixels, no hairlines, no empty side columns, so letters sit evenly apart). style8.py: the v5 styling at every size.
- **Pieces (v8/tools/icons8.py):** the v7 health capsule stretched by whole segments to 100 x 19, coins, tabs, rows,
  meter, medals, ribbons; **build8.py** writes them, the font atlases and their metrics into riverwalk/art/ui,
  uifont_data.lua and uiart_data.lua (each piece's body box, shadow left out).
- **HUD (hud.lua U.status, replaces the blue signs, no flag):** health bar top left, the watch and the time centred,
  the bone and its count top right with the score under it, Pepper's head and x3 bottom left. The v6 spec: 4 px
  margins, one centre line (14) for the top row, 3 px icon gaps, one outline and one shadow colour; the last 30 s blink
  dim; HARD on a red plate under the time. While playing, a group Pepper is under steps aside (main.lua passes her rect).
  **uifont.lua** draws the fonts at whole pixels. The other screens' helpers (blue boxes, 5x7 text) are unchanged.
- **Tools:** `love riverwalk --uishots` (tests_ui.lua) shoots the HUD, pause and tally and logs every placed body;
  tools/ui_frames.py (frames at 1x), tools/layout_qa8.py (the v6 checks on real frames: 42 PASS on the HUD),
  tools/ui_card.py (side-by-side with the target, the screen card).
- **Checks:** check_pepper PEPPER UNCHANGED (4591 steps); check_flow 116 of 116 (with a fresh XDG_DATA_HOME).
## Branch `art/pilot-oldtown`: Downtown's Old Town row built from stamped parts (23 Oct)
Built on main v0.6 (1b5a30f). 0 credits, no generation, no resampling, no new colour (the strip's own 12), alpha binary.
Aseprite was not built yet on this machine, so the build is a script.
- **tools/build_oldtown.py** builds `riverwalk/art/scene/town_facades.png` from parts drawn once (window 7 x 11 with
  lintel, sill and its shadow; attic window 7 x 9; double door; gable step; cornice, string course, plinth) and
  stamped on an integer grid; what is not rebuilt comes pixel for pixel from **source_scenery/town_facades_v06.png**
  (the strip as on v0.6). `--check` fails if the file differs from the build; `--houses DIR` writes each house alone
  for asset_qa and the cards; `--parts out.png` a sheet of the parts at 8x.
- **Pilot: the red stepped-gable house** (x 42-78): 3 storeys of 16 px, 3 identical windows per storey 4 px apart, the
  ground floor's 2 windows and door on the same columns, a gable as wide as the wall of 6 levels of 5 px with 2 px
  treads, 3 attic windows; flat wall with one shade band (right edge), light from the upper left. asset_qa
  (`--building`, mid, dt): WARN (contrast 106, as the old row's 103), lone pixels 0.0 %, every storey's windows
  identical, 8 colours. The row's lone pixels 1.9 % -> 1.5 %; the row still fails on the other houses' windows.
- **The whole row rebuilt** from the same parts (added: narrow window, dormer, single door, shop window, balcony, bell
  gable shoulder and cap, chimney, downpipe): yellow bell gable, the red stepped gable (pilot, unchanged), cream
  pediment with balconies, grey stone under a mansard with two dormers, ochre mansard with one dormer, narrow yellow
  bell gable, narrow red pediment; each its own colour, height, top and door. Houses of one wall colour keep their
  windows on the same rows or 5 px apart. Only the pavement rows (111 on) come from the v0.6 file.
  asset_qa per house: yellow_bell, red_gable, cream_pediment, stone_mansard WARN (contrast 102-106 only), ochre_mansard,
  yellow_narrow, red_narrow PASS; lone pixels 0.0 % each, every storey's windows identical, 8-10 colours. The row:
  FAIL -> WARN (contrast 102, was 103), lone pixels 1.9 % -> 0.1 %, 31 storeys all identical, 12 colours.
- check_flow is flaky under load on this machine (111-116 of 116, the same on the v0.6 file); 116 of 116 on a clean run.
- **Checks:** check_pepper PEPPER UNCHANGED (4591 steps), check_flow 116 of 116.
## Branch `art/placement`: placement audit of the three demo levels and its fixes (23 Oct)
Built on main v0.6. No credits; Pepper untouched; approved art unchanged (its findings are listed for the owner).
- **docs/placement_audit.md**: every screen of River Walk, City Park (tall) and Downtown (tall) checked for size against
  Pepper (46 px a metre), cropping, grounding, front-on view, composition and quality; one table per level (asset, x,
  problem, severity 1-3, fix, owner approval) with 3x evidence crops in docs/placement_audit/.
- **tests_look.lua**: `LOOK_SWEEP=1 love riverwalk --level L --lookshots` saves every screen of a level (the camera
  every 300 px, `LOOK_STEP`, at each height tier of a tall level), look on, no HUD.
- **River Walk:** the road is no longer drawn under the bridge pier (x 1936-2072): road.lua took the pier's row at
  y 184 for promenade and painted asphalt and lane dashes over the quay; the quay pavement now runs through the passage.
- **City Park (tall):** the lamp posts on the high road (x 864, 1696, 2624; Downtown's 1830 and 2420 too) stand on
  their walk, branch, deck or gallery; they floated 10 px over it (stage.lua put every lamp's foot at the pavement's
  back edge). The play tower's outer post was drawn as a 4 px tree trunk from the oak's canopy to the path; it is a
  grey post again, under the tower's lower deck, which is now drawn (it was an invisible step left of the slide's
  cage). Both tower posts reach the path. The low bough over the alder walk is drawn front-on, level over its box and
  curving up into the leaves as it thins (it read as a crate seen from above at an angle).
- **Downtown (tall):** the code placeholders of the high road are replaced by art built from stamped parts at 0
  credits (cards in out_place/, not committed): **tools/build_tall_fronts.py** (town_front_tall1-3: a door, a shop
  front and a carriage gate, one ground-floor bay each at true scale, a door 2.0 m = 92 px), **tools/build_roof_kit.py**
  (the stepped gable, chimney, two galleries, loggia, dormer, flower roof, the ledge 3-slice, the footbridge: crisp,
  outlined, front-on), **tools/build_spire.py** (Riddarholmen's brick tower and openwork iron spire). Each `--check`
  proves its files are what it builds. arthooks.lua: a back box is one building, split into bays (or its `fronts`),
  in one plaster (`plaster`, swapped by exact colour), a stone coping on the cut; the spire is drawn on the far roofs
  layer behind the old town row (it stood at scroll 1.0 in front of it). maps/downtown_tall.tmx: houses (decoration,
  no collision) under every high road piece that floated in the sky (the galleries, two ledges, the window awning,
  both ends of the footbridge); the guild house's box starts under its gable. docs/art_hooks_r8.md: the new slots.
- **High road lamps:** a lamp's foot is drawn wholly on its ledge (Downtown's lamp at x 2420 stood half off the
  ledge's left end); drawing only, the checkpoints keep their x. All five high lamps checked in a frame each.

## Regroup (23 Oct, evening): main v0.6, BIBLE and STATUS, the enforced gate, checks and releases on GitHub
The owner's decisions of 23 Oct (merge list): round1 becomes main as v0.6; art/freefix merged with the approved River
Walk building, cafe and gable kept unchanged; art/haze merged with Downtown's facades at 0.25 (was 0.10 on the branch)
so their windows sit back until the Aseprite redraw; r8/art and title/pixels closed and kept as reference.
- **docs/BIBLE.md** (the rules, each with its date) and **docs/STATUS.md** (the control tower) replace the 14 project
  notes as what a session reads first (FETCH! Production Playbook).
- **tools/qa_card.py** enforces the gate: an owner card needs an in-game frame (colour and greyscale on the card) and a
  slot; otherwise it is refused and nothing is written. A wrong slot fails the card. `--draft` for working cards.
- **.github/workflows/checks-and-release.yml**: check_pepper, check_flow and check_tiled on every pull request and push
  to main; a Release with FETCH.love on every push to main, tagged from **VERSION** (v0.6), so no tag push is needed.
- **Checks:** check_pepper PEPPER UNCHANGED (4591 steps), check_flow 116 of 116, check_tiled PASSED, the curve
  (`--order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night --seeds 10`) T1-T4 PASS, `--qa` riverwalk,
  citypark_tall and downtown_tall 0 problems.

## Branch `art/freefix`: the "Fix free" list fixed at 0 credits (23 Oct)
Built on `round1` (9d29233). No credits, no resize, no new colours, alpha binary, sizes unchanged; Pepper untouched.
- **tools/blotch_clean.py**: a 2-24 px patch of one colour inside a near colour (asset_qa's blotch check) takes the
  surrounding colour; silhouette edges never change. **tools/stamp_windows.py**: per storey (or wall) one clean
  reference window (consensus of the windows, glass one colour, equal panes, frame sides one colour) stamped into
  every window on the storey's grid. **tools/freefix.py**: the recipe per asset (stamp, blotch, clean, outline,
  pixel patches) re-run from 9d29233. tools/outline_complete.py: `--skip-bottom`, `--frames`, `--tile`.
- **asset_qa windows check**: panes must be equal and on one grid; before, any window with two rows of panes failed.
- **Fixed** (41 on the list: 13 PASS, 21 WARN, 7 still FAIL): the plaza houses' windows stamped (town_house1/2 one
  window per wall, town_house3 per storey; house1's attic bar 2 px for equal panes); blotches cleaned wherever the check found them;
  outlines completed on the awnings, parasol, table, kiosk, hedge, keeper cart and, as drawn-with-outline decoration,
  park_gate, park_keeper_winch (the crank is now ink), town_house3, pier; ferry 24 -> 20 colours (4 near duplicates);
  cloud8's darkest shade merged into the next (ladder); specks off both cyclist2 sheets and the skyline; flicker
  pixels on the rowboat and gull.
- **Approved River Walk art changed (owner to approve)**: building (blotches, noise, stray: the glass streaks went),
  cafe (blotches, stray), gable (4 blotches). Their windows are not stamped (painted glass).
- **Still failing**: town_facades, cafe, gable windows (painted glass; need a redraw), ferry outline and pinholes
  (inking the railings cluttered the deck: reverted), park_leaves_flat stray (leaf texture), town_bollard ladder
  (median 41 vs 40: a code value), road_cyclist1_roll pinhole (a gap between spokes).
- **Checks:** check_pepper PEPPER UNCHANGED (4591 steps), check_flow 116 of 116, check_tiled PASSED;
  check_pepper_files cannot run in this shallow clone (aa38be5 missing; Pepper's 5 files are identical to 9d29233).
## Branch `art/haze`: every fade in the level's own haze (23 Oct)
Built on `round1` (9d29233). Code and tools only; no art file changed. Owner decision 3: the cool-grey load-time fade
is retired; the whole distance step is done in each level's own haze colour (look.lua's colour script, per layer).
- **look.lua**: each colour script has a `fade` table, the load-time amount per layer. River Walk: back 28 % (as
  before). City Park: tree line 35 % (was none), round trees 48 % (was 28 %), back 20 % (was 28 %). Downtown: roofs
  70 % (was 45 %), facades 10 % (was 40 %), back 28 %. Own amounts kept: park gate 28 %, winch keeper 35 %, vintage
  tram 40 %, spire 45 %.
- **scene.lua**: Sc.haze, Sc.fadeK, Sc.fadeC, Sc.fadeData fade to the haze of the level being played (Look.key);
  every faded image (Sc.art, the park and town art, the railing, the canopies, the bark and roses) is cached per
  colour script. **setpieces.lua** (kiosks) and **arthooks.lua** (tram, tall fronts, spire, roof kit walls) use them.
  **stage.lua** sets the colour script before the level's art is built.
- Fixed: City Park's willows are darker than the round trees behind (median 156 / 159-166); Downtown's far roofs are
  lighter than the facades (173/161 against 170/124, were 162/139 against 184/154); the winch keeper reads warm.
- River Walk: decoration warmer by about R +12, G +4, B -10 and luma +5 on its pixels (0-16 % of a frame); nothing else.
- **tools/measure_layers.py**: the model fades to the level's haze by the level's amounts (FADE, OWN); `--ladder`
  prints the ladder per level. **tools/asset_qa.py** uses it (shared art takes each level's amount). Ladder results:
  no new fail; one new warn (town_facades contrast 92, mid allows 85).
- docs/layer_ladder.md: the fades and the ladder table per level.

## Branch `art/qa`: the asset QA gate (23 Oct)
Built on `art/fixes`. Tools and docs only; no art changed.
- **tools/asset_qa.py**: every asset checked as the game draws it and in detail (alpha, slot, noise, stray, blotches,
  specks, pinholes, outline, colours, ladder in every level it is drawn in, windows pixel by pixel, frames). Exit 1 on
  any FAIL. Calibrated: the approved bench, bin, lamp, kiosks, planter and flower box pass; the plaza house windows,
  the winch keeper's outline and batch 1's plaster fail.
- **tools/qa_card.py**: one card per asset (as drawn 1x/2x, the file at 5x with flagged pixels boxed beside the
  bench, bin and lamp, windows lined up at 8x, frames at 5x and GIFs). **tools/qa_triage.py**: the defect list.
- **docs/asset_qa.md**: the gates (brief, pilot, make, clean, checks, card, independent review, owner), the review
  checklist, the credit rule. **docs/art_ledger.md**: credits per asset. **docs/asset_qa_triage.md**: the library on
  23 Oct (133 assets: 31 PASS, 36 WARN, 41 to fix free, 25 batch 1 rejected).
- tools/measure_layers.py runs nothing on import now (asset_qa imports it).
- An independent agent reviewed the tools against the game code; its findings (wrong look for the pier, unused
  files, slot sizes, outline on decoration and front pieces, window grouping, merged messages) are fixed.

## Branch `art/fixes`: the layer-ladder code fixes and a clean pass (23 Oct)
Built on `round1` with `art/layers` merged (tools/measure_layers.py, tools/layer_shots.sh). No credits, no new art.
Owner decisions of 23 Oct (Asset Library doc): all five recommendations accepted; decision 4 (lighten the plaza
houses now) is done here.
- **Statue tagged play** (maps/downtown.tmx, downtown_tall.tmx, level/downtown.lua and both exports): its arm and hat
  are ledges, so it takes the play look (stage.lua, PLAYLOOK). Still decoration for collision; nothing moves.
- **Winch keeper faded 35 %** (scene.lua): darks 17 -> 86 on screen.
- **Plaza houses faded 28 %** (scene.lua, decision 4): darks 50-54 -> 96-99. Their outlines are baked in; the redraw
  comes later under decision 2(a).
- **Outlines completed** (tools/outline_complete.py, in place, no resize): town_pedestal (38 -> 100 %, the stone ink
  29,24,22), town_stall (81 -> 100 %), town_shelter (82 -> 100 %). The ferry was checked and left as it is: every
  deck edge Pepper stands on (hull, saloon roof, wheelhouse roof) is already outlined; the light edges are the
  railings, mast and flag, which are decoration.
- **Clean pass** (tools/cleanpass.py: a lone pixel takes its neighbours' majority colour only when that colour is
  close, so eyes, highlights and outline corners stay; no new colours, edges and alpha untouched): tree, tree_far,
  tree_near, rw_jetty (+ its outline ink unified), park_log, park_willow, park_willow_tall, park_swings, park_leaves,
  park_leaves_flat, park_hedge, town_statue, town_ground (wraps), town_crate_front, town_stall, town_tramshed70/96
  (22 -> 20 colours), goose (39 -> 24 colours), gull. Every file now under 5 % lone pixels.
- **tools/fix_shots.sh** and `LOOK_SPOTS` in tests_look.lua: frames of chosen spots on any level (before / after).
- **Checks:** check_pepper PEPPER UNCHANGED (4591 steps), check_flow 116 of 116, check_tiled PASSED (0 FAIL),
  `--qa` downtown_tall and citypark_tall 0 problems, the curve (`check_curve.py --order riverwalk,citypark_tall,
  downtown_tall,rooftops,soder,night --seeds 10`, fresh out) T1-T4 PASS with the same DI numbers as r8/levels.
## Branch `r9/rooftops`: Rooftops climbs to the nest and runs down to the roof cafe (23 Oct)
Built on `round1`. Pepper's files are untouched (PEPPER UNCHANGED), no art, no music. Design and every number:
`docs/rooftops_beatsheet.md`.
- **Eleven more screens** (tools/make_rooftops.py, its r9 block; maps/rooftops.tmx and its export written again
  from it): the map is 7472 x 1200 px (was 4160). Both roads meet on the roof bar's terrace and climb together: the
  hotel roof (two skylights of loose tiles under a second gull, a goose by the hotel kitchen's vent over a chimney
  block), the light court (the tower: a drop to 664 and four puffs up three balconies, one of them loose tiles by
  the hood), the tall block (lamp, goose), the scaffold (two loose boards, tap hops), the cafe awning's bounce, the
  chimney stacks (held jumps up two loose tiles over a dip), the sauna roof (lamp, skylight, third gull). The nest
  moves to the tallest chimney (top 88); the sauna's bark there drops the ball and lifts her up. The reward: four
  pitched roofs down to the roof cafe (472), where Mia waits now. No new verb. New vents: HOTEL KITCHEN, COURT FAN,
  LAUNDRY HOOD, KITCHEN HOOD, BATH FAN (each with someone running it); level time 420 s.
- **Numbers:** `--auto` 92.4 s on both roads (was 58.1 and 54.4; they share the climb and ride the same puff).
  Par 148 (was 87; levels.lua). Playtest lab, the game's order, 10 seeds: Rooftops DI v2 kids / parents 23.5 / 26.1
  (was 20.0 / 16.5), Elsa 78%, T1 to T4 pass; 20 seeds: 21.2 / 22.1.
- **Checks** (tests_rooftops.lua): `--physics` 139 of 139 (was 103): every new vent, jump, fall and bridge with
  Pepper's own controller; every loose tile drops her safely; the ledge fall proof covers the court's balconies
  (46 falls). `--qa` 0 problems (a post under the first balcony stops a ball knocked off the hotel roof). The
  autopilot plays the new screens on both roads; the `--test` tour has 17 new spots. `check_flow` 116 of 116,
  `check_tiled` passes. Route render: `tools/draw_routes.py` has the roads as built (r7 and r9).
## Branch `r9/night-ball`: a knocked ball that rolls off a boat comes back where Pepper was hit (23 Oct)
Built on `round1`. Fixes the Night Harbour `--qa` problem left open in docs/playtest/curve_r7.md.
- **The bug:** hit at the quay's edge before the slipway (x 3812) while carrying, the ball landed on the moving
  slipway boat. Landing cleared its knock spot (b.knock), so when the boat rowed out from under it, it fell in the
  water and went back to the ball's home: x 240 with no lamp lit (the level's start), else the jetty at x 3020.
- **The fix** (stage.lua only): a knocked ball that lands on a mover (a boat or a lift) keeps its knock spot, so
  it comes back on the quay by where she was hit (x 3788). The knock spot is cleared when Pepper picks the ball up.
- Checks: `--qa` 0 problems on night (was 1), riverwalk, citypark_tall, downtown_tall, soder; `--physics` night
  40 of 40, riverwalk 54 of 54; check_flow 116 of 116; check_tiled passes; PEPPER UNCHANGED.

## Branch `r8/levels`: the tall City Park and Downtown in the game, the cargo bike, hooks for the first art batch (23 Oct)
Built on `round1`. The owner's decisions of 23 Oct: D2 (the tall City Park and Downtown replace the flat ones) and D1
(Downtown's street hazard is a cargo bike with its rider; a true-scale vintage tram rolls by in the back lane as
scenery). Pepper's files, music and sfx are untouched; no art was generated.
- **D2: the tall levels are levels 2 and 3** (levels.lua, flow.lua, maps/downtown_tall.tmx and its export,
  tests_flow.lua, tests_downtown_tall.lua): the order is River Walk, City Park (tall), Downtown (tall), Rooftops,
  Soder Hill, Night Harbour. They carry the flat levels' titles, numbers, intro and story cards (already in their
  maps); par times 63 s (39.1 s autopilot) and 90 s (56.2 s). The flat City Park and Downtown stay in `level/` as
  fallbacks (their old lines are in levels.lua, commented out: put one back in place of its tall twin to switch).
  A save that opened a flat level opens its tall twin (`was` in levels.lua, `F.load`). **The tall Downtown gets
  Downtown's art** (`art = "town"`, `foot = 424`, as r3 did for the tall City Park): the street looks as Downtown
  does; the high road's pieces are code-drawn until the roof kit lands (below). Four hints were longer than the
  panel's three words and are now `HOLD: CLIMB UP` (the tall City Park's tree and tower, the tall Downtown's way
  up from the bakery sign) and `HOLD: BOUNCE` (the plaza parasol); the generators say the same. New flow checks:
  the order, every level's cards agree with levels.lua, an old save opens the tall twin; the City Park talk checks
  run on the tall City Park (its path 144 px lower). `check_flow` 116 of 116.
- **D1: the cargo bike** (level/downtown.lua, maps/downtown.tmx written again from it, maps/downtown_tall.tmx, their
  exports, new `riverwalk/arthooks.lua`, stage.lua, scene.lua, tests_downtown.lua, tests_downtown_tall.lua): both
  Downtowns' tram zones are cargo bike zones (`kind = "cargo"`), the same hit box (80 x 26: the cargo box and the
  front wheel), the same speeds and rhythm (110 px/s every 6 s, 130 px/s every 4 s: about 9 and 11 km/h, a loaded
  cargo bike's pace), so the kiosk, the shelter roof and the gates stay the same perches and the autopilots the
  same times. The tell is the bell (1 s before it comes in, and little rings by the handlebar as it enters) and the
  blinking sign. The baker's delivery man rides over the back wheel, drawn tall (about 76 px, like the leaf-cart
  keeper) and never hurts. The bike is drawn behind the obstacles on Pepper's line (the kiosk and the gates hide
  its wheels; Pepper on a perch is drawn over the rider), as River Walk's bikes. Placeholder: an outlined box bike
  with a rider drawn in code (about 92 x 76), replaced by `art/scene/cargo_bike.png` (and `cargo_bike_pedal.png`)
  when they exist. **The tram sheds are courtyard gates** (`GATE`, the same boxes, the same art without the rails,
  the same `depot` code): the bike rides into the courtyard through the gateway. Girl lines: CARGO BIKE! GET UP
  HIGH! and A FAST BIKE! GET UP!
- **D1: the vintage tram in the back lane** (`L.trams`, arthooks.lua; `tools/level_to_tiled.py` and
  `tools/tiled/check_tiled.lua` know the lane's `stop`): on both tram streets a true-scale tram (300 x 130, faded 40%
  towards the haze: the far lane) comes in off the right edge of the screen, brakes to a halt with its front door at
  a tram stop sign by the shelter, waits 3 s, and drives off to the left; one every 16 s while the screen is over the
  street. Its driver sits in the front cab; a trolley pole reaches up. Rails at the street line minus 10 (behind
  Pepper's line, where decoration stands); drawn before the back props, so everything on her line and Pepper are in
  front of it. Never a hazard. Placeholder drawn in code; `art/scene/tram_vintage.png` when it exists. New checks
  (tall Downtown): the cargo bike zones' kind and hit box, the two tram lanes, the tram comes in off screen, stops
  at its sign for 3 s and leaves, no heart lost (102 of 102); flat Downtown 81 of 81. `--auto` 51.4 s and 56.2 s, as
  before.
- **Hooks for the first art batch** (arthooks.lua, road.lua, bonus.lua, scene.lua; `docs/art_hooks_r8.md` lists every
  name, size and anchor; `tools/preview_art_hooks.py` writes labelled stand-ins into a LOVE save folder to check them
  without committing art). Each piece looks for its file and falls back cleanly: the cargo bike and its pedal sheet,
  the vintage tram (above); the promenade and road cyclists `cyclist_adult1-2.png` with `_pedal` sheets (else
  `road_cyclist1-2`); Mia's throw `art/girl_throw.png` (8 frames in girl.png's cells) in the bonus round's throws
  (else the wave and cheer clips); the row across the square `town_row.png` (else `town_facades.png`, both
  Downtowns). The tall Downtown's old town: the roof kit `town_roof_<name>[<width>].png` over the high road's boxes
  (loggia, galleries, chimney, dormer, flower roof), the stepped gable `town_roof_gable.png`, the other ledges
  `town_roof_ledge.png` (a 3-slice), `town_footbridge.png`; the tall house fronts `town_front_tall1-3.png` filling
  the back boxes under the roofs (drawn before the other back props, so Downtown's houses with balconies stand in
  front); the far landmark `spire_riddarholmen.png`. Until they land, all of these are drawn in code (crisp and
  outlined: stone ledges, an arcade, a balustrade, a brick chimney and gable, a copper dormer cap, flower boxes,
  the footbridge's deck, rail and arch; faded: plaster fronts with windows, cornices and doors, the openwork spire)
  instead of the grey labelled boxes. Checked with stand-ins for every file (all drawn at their anchors, the bonus
  round's throw frames, River Walk's autopilot 66.3 s unchanged).
- **Docs** (progression.md, the beat sheets of both City Parks and Downtowns, needs_art_22oct.md): D1 and D2 noted
  where they change what the sheets say. The tall Downtown's `--test` tour has three new shots: the cargo bike
  passing under Pepper on the kiosk, the vintage tram at its stop, a tram coming in on the second street.
- **Checks on this branch:** `check_pepper` PEPPER UNCHANGED (4591 steps), `check_pepper_files` 5 files identical,
  `check_flow` 116 of 116, `check_tiled` PASSED, `--physics` riverwalk 54, citypark 85, downtown 81, citypark_tall
  94, downtown_tall 102, rooftops 103, soder 29, night 40, lab_tall 43 (all pass), `--auto` 66.3, 44.6, 51.4, 39.1,
  56.2, 58.1 (high road 54.4), 73.3, 82.6, 25.9 s (no heart lost; unchanged), `--qa` 0 problems on every level but
  Night Harbour (1, the slipway's known ball sweep spot, as on round1). **The curve** (`tools/check_curve.py --order
  riverwalk,citypark_tall,downtown_tall,rooftops,soder,night --seeds 10`, out `/home/claude/out/r8-levels/curve_r8`):
  T1 to T4 PASS; DI v2 kids / parents 18.0 / 14.0, 12.6 / 17.6, 11.6 / 18.5, 20.0 / 16.5, 15.7 / 14.7, 19.2 / 24.7,
  the same as r7/curve (the cargo bike keeps the tram's numbers; the playtest lab never reads the art). Screenshots
  of the cargo bike placeholder and the vintage tram: `/home/claude/out/r8-levels/` (sheet
  `r8_cargo_bike_and_tram_sheet.png`).
- **Left for later:** the art itself (the batch-1 files drop in by name); `tools/make_downtown_tall.py` still writes
  the tall Downtown without `art`/`foot` (the map in Tiled is the source now); Rooftops' and Night Harbour's par times
  still come from their r6 autopilot times (58.1 and 82.6 s since r7 would give 93 and 133).
## Branch `r7/curve`: the tall order's difficulty curve passes the acceptance test (22 Oct)
Built on `round1`. The planned order with the tall levels (River Walk, City Park tall, Downtown tall, Rooftops,
Soder Hill, Night Harbour), measured with `tools/check_curve.py --name tall --seeds 10`; every iteration's numbers are
in `docs/playtest/curve_r7.md`. Pepper's files, music, sfx and the title are untouched.
- **Downtown (tall), softer** (maps/downtown_tall.tmx and its export, tests_downtown_tall.lua): it was the spike
  (kids 24, parents 26; Anna and Elsa quit at the cafe terrace and the statue). The cafe terrace: both parasols at
  y 362 (were 354), 16 px apart (were 48): a 36 px held jump up from the table, a walk across, and the shop sign
  8 px lower (34 px up). Way up A: a crate step (x 1172-1208, 24 px) after the bakery crates, so a tap hop reaches
  the springier awning. The plaza: with the ball, a springy cafe parasol right of the statue (x 1512-1552, 20 px over
  the street, bounce 136) bounces Pepper up to the loggia (HOLD: BOUNCE UP!); the four held jumps up the statue
  (pedestal, arm, hat, loggia) stay as the way to the STATUE HAT secret. The flooded square: the first parasol 12 px
  lower (a tap hop from the crate reaches it). Autopilot: two tap hops onto the market stall (the r6 crate step);
  it lets go of Right only once Pepper is off the shop sign and the market awning (a player who stops short on the
  edge was a stuck in the lab). New checks: the parasols, the plaza parasol held and tapped, the way up A crate
  step, the flooded square tapped (98 of 98). `--auto` 56.2 s (was 56.6), no heart lost.
  Before/after: `/home/claude/out/r7-curve/downtown_tall_before_after.png`.
- **Rooftops, a peak: a 13th screen, the drying yard** (tools/make_rooftops.py, maps/rooftops.tmx and its export,
  tests_rooftops.lua): x 3344-3664 on T3 (568), between the balcony vent and the roof bar; everything from x 3344 on
  moved 320 px right (the generator now inserts the screen; it also matches the map's Tiled edits again: LEVEL 4,
  the outro, BARK on Y, HOP ON FAN, BOUNCE ON IT). The combined beat before the finale: a dip 144 px wide and 40 deep
  with a staircase of two loose tiles over it up to a chimney stack (three held jumps, 32 px up each, no stopping:
  a tile drops 0.6 s after she lands), under the roof bar's gull; a miss drops her into the dip (a held jump and a
  scramble get her out, left). Off the stack's right side she drops onto the springy awning, which bounces her onto
  the water tank. The high road crosses above at 456 (a ledge, two loose tiles) and its ledge 424 now starts over
  the stack. Hint HOLD: BIG JUMP at the dip. 12 new bones (88). Checks 103 of 103 (new: the staircase held and
  tapped, out of the dip, off the stack onto the tank; counts 14 vents, 21 tiles). `--auto` low road 58.1 s (was
  54.1), high road 54.4 s (was 51.8). The goose spot (screen 9) was 43% of the failures; now 30%.
  Before/after: `/home/claude/out/r7-curve/rooftops_before_after.png`.
- **Soder Hill, a step up** (level/soder.lua; maps/soder.tmx and its export written again from it with
  `tools/level_to_tiled.py`): a third terrace with a barrel stack after the balcony's hatches (x 3776-3832, 24 px
  over the street; the barrel at x 3820, set off when the ball passes x 3786, 34 px/s). A threat from ahead with the
  barrels' tells (the "!" as it comes off the stack, the rumble and "!" when she closes in, its shadow); the screen
  still pushes. `--physics` 29 of 29, `--auto` 73.3 s (unchanged), no heart lost.
  Before/after: `/home/claude/out/r7-curve/soder_before_after.png`.
- **Night Harbour, the hardest for parents** (level/night.lua, tests_night.lua; maps/night.tmx and its export
  written again from it): tighter timing windows, nothing hidden, no new kind of threat. The rotten planks (screen 8)
  are 24 px wide (were 32), the same middles, so each tap hop must land on a narrower plank (their shake, scramble
  sound and the planks drawn over the dark are unchanged). Back over (screen 11), carrying the ball: two narrow
  crumbling planks (x 3440 and 3480) instead of one. The slipway's second boat rows faster and further (30 px/s, to
  x 4040; was 22, to 4028). Tried and taken back: a faster first slipway boat and a narrower slipway plank (the
  slipway took 40 to 58% of the level's failures, a T2 fail). Autopilot: the first plank hop 6 px earlier.
  `--physics` 40 of 40, `--auto` 82.6 s (was 81.3), no heart lost.
  Before/after: `/home/claude/out/r7-curve/night_before_after.png`.
- **The curve** (`docs/playtest/curve_r7.md`: six iterations, what moved and why, what is left): the tall order
  passes T1 to T4 (exit 0). DI v2 kids / parents: River Walk 18.0 / 14.0, City Park (tall) 12.6 / 17.6, Downtown
  (tall) 11.6 / 18.5 (was 24.1 / 26.0), Rooftops 20.0 / 16.5 (was 16.0 / 13.3), Soder Hill 15.7 / 14.7 (was
  9.6 / 7.3), Night Harbour 19.2 / 24.7 (was 15.1 / 23.4); worst spots 21 to 33%; Elsa clears 80 to 100%; lost runs
  0 to 3.8%. Chart `/home/claude/out/r7-curve/curve_tall.png`. Checks: `check_pepper` UNCHANGED (4591 steps),
  `check_flow` 113 of 113, `check_tiled` PASSED, `--physics` riverwalk 54, citypark 85, downtown 81, citypark_tall
  94, downtown_tall 98, rooftops 103, soder 29, night 40 (all pass), `--auto` 66.3, 44.6, 51.4, 39.1, 56.2, 58.1
  (high road 54.4), 73.3, 82.6 s, `--qa` 0 problems on River Walk, City Park, Downtown, Downtown (tall), Rooftops
  and Soder Hill, 1 on Night Harbour (the ball sweep at the slipway's edge, see the curve doc).

## Branch `r6/engine`: safety nets, the same in every level (22 Oct)
Built on `round1`. Benchmark principles 5, 6 and 7 (`docs/benchmark_22oct.md` section 4) in the engine, so every
level gets them without level changes. Hard mode (`stage.hard`: `carry.hard` from the menu's `hard.txt`, or `--hard`)
keeps the old rules everywhere. Pepper's files are untouched; music is untouched.
- **A free first mistake** (stage.lua `St:hazardHit`, `St:knockBall`, `St:spotNear`, `St:ballLands`): when a hazard
  hits Pepper while she carries the ball (bikes, leaf carts, trams and any other kind in `L.bikes`, geese, gulls, the
  chase's barrels), the ball pops out with her knock-back and she keeps her hearts; she still gets the hurt sound,
  the knock-back and 1.5 s of blinking, and Mia says "OOPS! GET THE BALL!". Without the ball a hit costs a heart as
  before. The ball flies along with her (60% of her knock-back speed, up 150 px/s); if that flight would end in the
  water or inside a box (`St:ballLands` runs it ahead), it pops straight up instead; if even that fails, it splashes
  and comes back 0.6 to 1.2 s later on a spot fixed at the hit: the floor under her paws, the nearest clear spot
  within 48 px (never a boat or a lift, they move on), else by the last lamp. critters.lua (goose, gull), chase.lua
  (barrel) and the bike loop call `St:hazardHit`; a hazard added later only has to call it after `p:hurt`.
  Not hits, unchanged: the water and a fall out of the world (a heart and back to the lamp, as before: returning her
  to the bank where she fell was weighed and left out, because the "last safe ground" can be a crumbling plank, a
  loose tile, a boat or a bike lane, and the tests and autopilots rely on the lamp), the chase's pin and hatches,
  time up. In hard mode a hit costs a heart even with the ball, and the goose and the gull still knock it out.
  main.lua (one line): a knocked-out ball also loses the NO HIT medal (a hit is a hit).
  qa.lua: a 4th sweep, the ball sweep: at every 24 px on every surface, hit from either side while carrying, the
  ball must come to rest where she can pick it up (or ride a boat, or reach Mia) within 3.3 s.
- **Lamps heal** (stage.lua): lighting a checkpoint lamp gives back one heart, up to the most she can have, and a
  red heart pops out of the lamp's light and floats up 26 px, fading, over 1.2 s; it rings the existing "heart"
  chime instead of the lamp's "checkpoint" chime so the gift is heard (at full hearts the lamp chimes as before).
  Not in hard mode (1 heart).
- **Tells** (principle 7). Audit of every hazard's warning, at least 0.5 s and on screen before it can hit:
  bikes, carts, trams (bell, honk or ding 1 s before the front reaches the screen edge, and the blinking sign at
  that edge: OK); goose (0.5 s hiss, rearing pose and a "!" before the charge: OK at the minimum; a goose walked
  into from behind or landed on from a jump has no hiss, it is in plain view); gull (squawk and its shadow on her
  floor 0.9 s before the swoop: OK); steam (never hurts); loose roof tiles (0.6 s shake, clink and grit; they only
  drop her, never fall on her); Night Harbour's crumbling planks (0.5 s shake and a scramble sound); the fox (never
  hurts); hatches and water (static, in view). Added in code: **the chase's barrels** (chase.lua) now show a
  blinking "!" as they come off the stack (with the existing "spring"), a "!" again with a rumble ("push") while
  Pepper closes in within 110 px behind one (about a second at a run), and a shadow on the street; the playtest
  found Soder Hill's barrels the costliest hazard for Mikael and Elsa (fix 9). Art-dependent tells left for the
  art plan: a goose pose for "annoyed, about to turn" (so a goose walked into from behind warns too), a barrel
  wobble frame on the stack, a cart keeper or tram driver waving as the bell rings.
- **Tests** (`tests_safety.lua`, one line in each level's tests file): every level's `--physics` run ends with the
  safety checks, found from the level itself: for each hazard type (each vehicle kind, goose, gull, barrel) a hit
  while carrying (ball out, no heart, the ball at rest within 160 px where she can get it), a hit without the ball
  (a heart), a hit in hard mode (a heart, as before); and the first checkpoint lamp (gives a heart and pops one,
  never past 3, nothing in hard mode). `SAFETY_SHOTS=1` saves the first hit of each kind and the lamp's heart to
  `shots_safety/` (the GIFs in `/home/claude/out/r6-engine/`). Three tests changed, with reasons: City Park's
  "leaf cart: a running jump clears it" starts at 3 hearts (she runs past the lamp at x 1624, which now heals);
  Downtown's goose bite while carrying now checks the ball out and no heart; the lab's pit fall has its respawn
  lamp lit (as it is in play; lighting it would heal). Checks: `check_pepper` UNCHANGED (4591 steps),
  `check_pepper_files` identical, flow 103 of 103, `check_tiled` all PASS, `--physics` all pass (citypark 82,
  downtown 79, riverwalk 49, soder 29, night 40, lab_tall 43, citypark_tall 91, rooftops 97, downtown_tall 90; were
  73, 70, 40, 23, 37, 40, 82, 88, 81), `--auto` 44.2, 51.6, 66.3, 73.3, 81.3, 25.9, 38.5, 54.1 (low road), 56.9 s,
  unchanged, `--qa` 0 problems on City Park, Downtown and River Walk (ball sweep included).

## Branch `r6/lab`: the playtest lab, recovery v2, whole-game mode, DI v2 and the curve check (22 Oct)
Built on `round1`. The lab only (`riverwalk/playtest.lua`, `riverwalk/pt_bot.lua`, `tools/`); no game file changes,
it still hooks in only through main.lua's `--playtest` flag. Method: `docs/playtest/method.md`.
- **Recovery v2** (pt_bot.lua, playtest.lua, tools/pt_common.py, tools/run_playtest.py): the clean run now records a
  route map (where each autopilot step began: place, floor, mover, buttons, speed, and the world's sig: the ball, the
  magpie's perch, the fox's hideout, the cat; and the x range and lowest floor each step ran over). The persona runs
  get it (`--route`). A persona who leaves the route (more than 72 px beside it or 20 px below it for 0.3 s) fails
  there at once (`offroute`) instead of running on into the water; after any failure the bot settles, fetches a
  loose ball, chases the magpie if it sits where the clean run never saw it, else walks to the nearest step on her
  floor with the same sig and the autopilot goes on from there with the clean run's buttons; nothing on her floor:
  the lab moves her there and charges the walk (`lab_walks`). A step picked up out of sequence that errors counts as
  a stuck. Lost runs on the 22 Oct bot (5 seeds, every level): 127 of 320 (40%); with v2, see the baseline.
- **Whole-game mode** (tools/run_campaign.py, pt_bot.lua `--carry`): a persona plays an order as one playthrough.
  Lives and the tally score carry over as in the real flow; GAME OVER is TRY AGAIN (the level again, 3 lives, the
  score it started with). Controls found stay known for the rest of the playthrough (trying time paid once); a hint
  whose button glyph was on screen halves the trying time of a control not known yet. A level not cleared ends there
  and the playthrough goes on at the next level as LEVEL SELECT starts it. One JSON per level of each playthrough.
- **DI v2 and the acceptance test** (tools/check_curve.py): DI v2 takes the trying time out of the play minutes and
  the clear time and does not count the failure that taught a control; learning seconds are reported on their own;
  DI v1 stays beside it. `check_curve.py --order ...` runs whole-game mode for the eight personas and checks T1
  sawtooth (no level more than 8 DI points above the hardest of the next two; the second half at least as hard as
  the first, the last level at least as hard as the first; kids and parents), T2 no spot over 35% of a level's
  failures, T3 Elsa clears every level in 50% of her playthroughs, T4 under 5% lost runs; exit 0 when all pass.
- **The fox's sig** (pt_bot.lua): whether the fox was sniffed out at its hideout is part of the world sig, so a
  persona who missed the shed roof on Night Harbour goes back to sniff before she barks (it was picked up after the
  sniff, and the bark found no fox).
- **Baseline v2** (docs/playtest/baseline_v2_22oct.md, charts in /home/claude/out/r6-lab/): round1 as it is, three
  orders (current; new: River Walk first, Rooftops 4th; tall: the tall City Park and Downtown) in whole-game mode,
  8 personas x 10 seeds. No order passes; the tall order comes closest (only Downtown (tall) spikes; Elsa clears every
  level in 80% or more). City Park and Downtown are the spikes of the other two, and the last three levels are flat
  and easier than the middle in every order. Lost runs: 41% on 22 Oct, 2.3% now (Downtown 8.8%, City Park (tall)
  7.5%, City Park 5.6% still over 5%). check_pepper: PEPPER UNCHANGED; check_flow: 103 of 103; City Park --auto 44.2 s.

## Branch `r6/levels`: the new level order, River Walk as the tutorial, the spikes smoothed (22 Oct)
Built on `round1`. The owner's new strategy (ten levels; five built, plus Rooftops) and the synthetic playtest of
22 Oct (`docs/playtest/report_22oct.md`). Pepper's files are untouched.
- **The new order** (levels.lua, every level's intro and story card, main.lua's header, docs/progression.md, the
  Rooftops beat sheet; its own commit so it can be reverted alone): 1 River Walk, 2 City Park, 3 Downtown,
  4 Rooftops, 5 Soder Hill, 6 Night Harbour. The story is one day: in the morning Mia throws the ball by the river
  and it lands on a ferry; late morning a magpie steals it in the park; at noon a cat sits on it on the plaza; early
  in the afternoon a gull at the street cafe takes it up to its nest; in the afternoon it rolls down Soder Hill; on
  the way home in the dark a fox takes it. New story cards: River Walk's ("LATE MORNING IN THE PARK. A MAGPIE
  SNATCHED THE BALL!"), City Park's ("NOON IN TOWN..."), Downtown's (the gull), Rooftops' first one (Soder Hill).
  **Rooftops is in** as level 4: its flow works (intro card, tally, its new story card, par time 87 s from its
  54.1 s autopilot clear; `--flowtest` plays it in the run). Decision: the cards count the levels as they are played
  (1 to 6), not the plan's slots (Soder Hill 6, Night Harbour 9), so a child never sees LEVEL 4 followed by LEVEL 6;
  when Metro and the others are built, the numbers move up. The tall City Park and Downtown carry their twins'
  numbers and story. Par times stay with their levels. Rooftops' button hints follow the panel's rule (one to three
  words): "HOP ON FAN", "BOUNCE ON IT"; its BARK! hint showed the B button (sneak), now Y. LEVEL SELECT fits six
  rows (26 px from y 40; flow.lua). `tests_flow.lua` runs City Park's talk checks where City Park now is (run 2).
- **River Walk is the tutorial** (level/riverwalk.lua, maps/riverwalk.tmx and its export, tests.lua): one control at
  a time on flat pavement, in the order she needs them, nothing harmful in the first two screens. RUN at the start;
  the bench: CRAWL under it (the hint now teaches the low way; the seat is still a held jump up); a new fallen
  branch under the big tree (`LOG`, x 270-310, 21 px: the park's log art, loaded in scene.lua) for the first
  TAP: HOP; the flower box: HOLD: BIG JUMP; the bin: HOLD: CLIMB; the ferry: PICK UP; the bridge: CRAWL with the
  ball; GIVE to Mia at the end (the level's real fetch; there is no earlier Mia to give to). **Threats shown safely
  first:** a bike zone of its own covers only the bin's top (Pepper's middle is between 624 and 693 only up there),
  so as she climbs the bin one bike rides right under her ("A BIKE! STAY UP HERE!"): survivable by doing nothing.
  Bike zone 1 then rides at the tutorial's pace again (every 6.5 s, 115 px/s; levels/v2 had 5.5 s, 125 px/s; the
  playtest's fix 7: screens 2-3 had 62% of the failures). A third gull circles over the ferry and the far quay
  while she fetches the ball and never swoops (its x1 is left of its x0, so critters.lua gives it no stretch to
  hunt in); the harbour's gull is the first that swoops. Layout otherwise unchanged (one prop, one bone on it).
  New checks: the branch stops a walk and a tapped hop lands on it; the first bike is sent as she lands on the bin
  and passes under her with no heart lost; the first gull never swoops (45 of 45). The autopilot hops the branch and
  waits on the last flower box of bike zone 1 for a bike to pass (slower bikes changed the timing): 66.3 s, no heart
  lost. **The golden trace was re-recorded**: the first difference is step 218, the autopilot jumping onto the new
  branch (x 241); Pepper herself is proven unchanged by `check_pepper_lab` (1401 lab steps identical) and
  `check_pepper_files` (5 files identical to aa38be5).
- **Picture signs for children who cannot read** (hud.lua `U.pict`, talk.lua `T.picFor`): every control hint now
  shows a little scene between the button and the words, 14 x 12 cells of 3 px: Pepper (the HUD's dog, standing or
  crouched, white) and what she uses (gold: the ground, a box, a bar, arrows; the ball pink; Mia). Pictures: run,
  hop (a low box), big jump (a tall box), climb (an arrow up a wall), crawl (under a bench), duck (a gull above),
  stay on, drop through, bounce, pick up (an arrow to the ball), give (the ball to Mia), bark (sound arcs), sneak
  (soft steps and a "z"). The words stay for readers; a hint can name its picture (`pic`), else its words choose
  it. A control hint now stays on one row (smaller words rather than two rows). The d-pad glyph is a hint button
  too (`btn = "right"`: RUN). "HOLD + PUSH: CLIMB" is now "HOLD: CLIMB" (River Walk, both City Parks) so it keeps
  the big letters beside the picture. `tests_flow.lua` checks every Pepper hint of every level has a picture.
- **City Park's climbing frame** (level/citypark.lua, maps/citypark.tmx and the tall map, their exports, the frame's
  art in tools/make_town_art.py, tests_citypark.lua and tests_citypark_tall.lua): 60% of City Park's failures were
  here (x about 2720): a tap hop that had to stop in the air on a 48 px one-way bar. The frame is wider (posts 2712
  and 2796, was 2772) with a step inside it (x 2716-2732, 12 px up: any hop; drawn in the art, its box hidden), the
  low bar 72 px (2712-2784, y 160), the top bar 76 px (2724-2800, y 136; the magpie's last perch, the ball 48 px up
  as before). A running held jump from the path lands on the low bar, a held jump from the step or the low bar
  lands on the top bar, a tap hop goes up one at a time. Hints at the frame: TAP: HOP onto the step, HOLD: BIG JUMP
  from it. New checks: the step, a held jump from the step to the top bar, a running held jump onto the low bar
  (76 of 76; tall: 85 of 85). Before/after: `/home/claude/out/r6-levels/citypark_frame_before_after.png`. City
  Park's own held jump is taught on flat ground at the bench (screen 2) and in River Walk before it.
- **Tall City Park: the held jump is shown before it is needed** (maps/citypark_tall.tmx, scene.lua): the first held
  jump (the bench seat, then the hedge) came where the magpie's BARK! hint wins the panel, so the level asked for
  it before HOLD: BIG JUMP was shown (Anna found it by trying in 19 of 20 runs). A **stump** (x 250-274, 28 px,
  drawn in code, a bone on it) is a safe practice ledge on the path before the bench, with HOLD: BIG JUMP before it
  (x 196-250); a second HOLD: BIG JUMP shows on the bench seat for the jump up to the hedge (way up 1). There is
  ground between the stump and the bench (48 px), so the crawl under the bench stays; the stump keeps clear of the
  lamp at 296 (a respawn there landed inside it in a first try: `--qa` found it). Two bones moved off the stump's
  box. The autopilot: the stump, down, the bench seat, the hedge (39.1 s).
- **Downtown's cafe terrace** (level/downtown.lua, maps/downtown.tmx and its export, tests_downtown.lua): 46% of the
  level's failures and 20 quits (Elsa had not found crawl yet, Anna missed the held jump onto the table). An apple
  crate (x 300-332, 16 px) splits the jump: a tap hop onto it, a tap hop from it onto the table (10 px up). The
  36 px of street between crate and table keep the crawl under both tables as the other way. Hints: TAP: HOP before
  the crate and on it, CRAWL only on the street by the table. No parasol on the terrace bounces; the first springy
  awning (BOUNCE ON IT, x 968) stays after it. New checks: a tapped hop onto the crate, a tapped hop from it onto
  the table (72 of 72). Before/after: `/home/claude/out/r6-levels/downtown_terrace_before_after.png`.
- **Tall Downtown, softer for kids** (maps/downtown_tall.tmx, tests_downtown_tall.lua): the same terrace crate, and
  crate steps at its other two held jumps of the main road (the stall heatmap's next hot spots): before the market
  stall (x 656-688: two tap hops onto the counter) and before the flower tub at the plaza (x 1368-1400: tap hops up
  to the tub and the pedestal). Their hints say TAP: HOP now. Six new jump checks (87 of 87); autopilot 56.6 s.
- **Par times** (levels.lua): City Park's par is 72 s (its autopilot clear is 44.6 s with the wider frame); the others
  are unchanged (River Walk 66.3 s, Downtown 51.4 s, Rooftops 54.1 s, Soder Hill 73.3 s, Night Harbour 81.3 s).
- **Not done (time box): Rooftops and Soder Hill are still short for their slots.** Rooftops needs a 13th screen and
  one combined beat (target 90 to 110 s; now 54.1 s on the low road), Soder Hill one combined beat (keep 70 to 90 s;
  now 73.3 s). Rooftops is in the order anyway as level 4; it is the easiest-reading of the climbs for now.
- Checks on this branch: `check_pepper` PEPPER UNCHANGED (4591 steps, the re-recorded trace), `check_pepper_lab`
  1401 lab steps identical, `check_pepper_files` 5 files identical, `check_flow` 113 of 113, `check_tiled` all PASS,
  `--physics` riverwalk 45, citypark 76, downtown 72, rooftops 88, soder 23, night 37, citypark_tall 85,
  downtown_tall 87, lab_tall 40 (all pass), `--auto` 66.3, 44.6, 51.4, 54.1 (low road), 73.3, 81.3 s and
  citypark_tall 39.1, downtown_tall 56.6, lab_tall 25.9 s (no heart lost), `--qa` 0 problems on River Walk, City
  Park, Downtown and the tall City Park.

## Branch `r5/bugs`: visual and presentation bugs, scale to the dog (22 Oct)
Built on `round1`. The owner's report ("the bike is too small, the cars get cropped when they pass") and a sweep of
every level, the menus and the cards. The bug list with evidence: `docs/bugs_22oct.md`. Pepper's files are untouched.
- **River Walk's bikes are an adult's bike** (stage.lua, level/riverwalk.lua, maps/riverwalk.tmx and its export): the
  promenade cyclists now use the road cyclists' art (`road_cyclist1-2.png`, 73 x 75, true 1x pixels; the two riders
  take turns) instead of `cyclist1.png` (49 x 50, a child's bike: the wheels were 19 px, smaller than Pepper's
  27 px back). The wheels are now as tall as her back, the rider 1.27x Mia. The hit box follows the drawn bike from
  wheel to wheel: 70 x 28 (was 48 x 26); 28 px keeps the perches (tops y 152-154) safe. The bikes ride behind the
  obstacles on her line (a flower box hides their wheels), so the taller rider no longer rides through Pepper on a
  box. `tests.lua`'s bell timing reads the zone's hit box.
- **Road traffic is never sliced** (road.lua): cars and cyclists only come in and leave at a screen edge. Before, a
  car drove into the end of its stretch of road (where the promenade turns into the quay steps) and was cut in half
  there by the road's scissor, could pop out of the start of a stretch on screen, and was removed on screen when it
  passed the end. Now one is sent only when its stretch reaches far enough past the screen for it to cross at the
  camera's present speed; if Pepper then runs after it so that the end would come into view, it speeds up or drops
  behind; it is removed only once wholly off screen; a cut (respawn) clears the road. Cars drive both ways now (300-
  380 px/s, about 25-30 km/h; were 110-170) so traffic still passes while Pepper runs right; cyclists 190-240 px/s.
  `LOOK_CHECK=1` prints `ROAD CUT` if a vehicle ever meets a road end on screen: none in the autopilot.
  The `--test` tour's traffic shots mark their vehicles `still` (kept through the shot's camera cut, at their world
  x); the planter shot's car starts inside its stretch of road (x 2830; at 2790 it hung over the quay steps).
- **River Walk's far shore ran out** (scene.lua): the shore layer was built for the 3200 px level (1196 px wide); at
  3840 px the camera needs 1376 px, so over the last two screens the trees ended in a hard edge with bare sand-coloured
  sky beside them. The trees now go back and forth to 1600 px. The far skyline's range was fixed at 2880 px too, so
  it stood still over the last 640 px; it now uses the level's own width.
- **LEVEL SELECT fits five levels** (flow.lua): the rows were 46 px, made for three levels; with five, SODER HILL ran
  under the "A PLAY  B BACK" footer, NIGHT HARBOUR hung off the bottom of the panel and the screen, and the SOUND
  pill sat on its text. Rows are now 30 px (the panel 208 px tall), so all five and the footer fit inside it.
- **The bug list** (`docs/bugs_22oct.md`): 16 items, 7 fixed here; the rest need new art (the Downtown tram, its shed
  and stop are toy-sized next to Pepper; the leaf cart keeper and the winch man are Mia's height; doors, the duck
  boat, a treetop lantern) or an owner decision (near-lane cars framed off at the bottom). The art list with target
  sizes goes to the asset plan. Checks: `check_pepper` UNCHANGED, `check_pepper_files` identical, flow 103 of 103,
  `check_tiled` all PASS, `--physics` all levels as before (73, 70, 40, 23, 37, 40, 82, 88, 81), `--auto` 44.2, 51.6,
  66.3, 73.3, 81.3 s unchanged (the wider bike hit box changes no autopilot time), `--qa` 0 problems.

## Branch `r4/playtest`: the playtest lab, ported to today's levels, and the level order checked (22 Oct)
Built on `round1`. The lab from `ml/playtest` (6 Oct, never merged) rebuilt around the levels' own autopilots.
The game is untouched: `main.lua` gains one line (`--playtest`, only with `--auto`); no level, map, stage, world,
camera, lift, roof, critter, set piece, Pepper or art file changes.
- **The persona layer wraps the current autopilot** (`riverwalk/pt_bot.lua`, `playtest.lua`): `tests_<level>.lua
  --auto` still decides what to press from the real game state; the lab sits between its buttons (`I.force`,
  `love.keypressed`) and the game and adds reaction delays, early and late presses, hold errors, controls found by
  trying, failures, recovery (back up on foot or back to the lamp, then on along the route), patience and quits.
  Routes stay current by themselves; Rooftops' high road comes from the autopilot's own `AUTO_ROUTE=high`.
  `pt_json.lua` comes over unchanged; the old copied routes (`pt_routes.lua`) are gone.
- **Runs:** `tools/run_playtest.py` (all personas x levels x seeds, one LOVE process per run, each with its own
  `XDG_DATA_HOME`, `SDL_AUDIODRIVER=dummy`, `xvfb-run -a`). A run takes about a second (no drawing).
- **Analysis and method:** `tools/analyse_playtest.py` (per persona and level: clears, quits and where, hearts,
  lives, game overs, clear times, waits, bones, secrets, controls found, failures per beat-sheet screen; the
  difficulty index per group along each candidate order; charts and stall maps); `docs/playtest/method.md`
  rewritten for the new design (what is exact, what is modelled, the recovery model, lost runs).
- **The order report** (`docs/playtest/report_22oct.md`, `docs/playtest/summary_22oct.json`; 1,280 runs, 20 per
  persona per level): the proposed order is not progressive. River Walk is the easiest level for every group; City
  Park (either version) and Downtown are spikes. City Park and Downtown beat their tall versions as levels 1 and 3;
  the current order (Downtown 2nd) is smoother by the index. Top fixes: City Park's climbing frame, Downtown's cafe
  terrace, the tall City Park's first held jump, the magpie at the gate. Checks: `check_pepper` UNCHANGED, flow 103
  of 103, City Park `--auto` 44.2 s as before.

## Pepper's file check narrowed to what she uses (22 Oct, evening)
- `tools/check_pepper_files.sh` flagged world.lua: engine/round2 gave `Wd:groundAt` an optional `fromY` for carts,
  bikes and the gull on tall levels. Pepper never calls it. The check now proves the rest of world.lua (all her
  collision) byte-identical to aa38be5, with that one function left out, and fails if pepper.lua ever calls it.
  The trace check (`check_pepper.sh`) was identical all along.

## Branch `r3/citypark-art`: the tall City Park gets City Park's art, and a treetop tier dressed to match (22 Oct)
Built on `round1`. Scene and art only; no new generated art (no SpriteCook): the treetops use the approved park art
in `art/scene/` and pieces drawn in code. Pepper's files are untouched (`check_pepper` UNCHANGED).
- **The park art at any path height.** The art levels' fixed lines (the path at y 184, decoration's base at y 175,
  the pond's bank and water line, the bench, bin, oak, gate, swings, frame, willows, winch, the duck boat's water,
  Downtown's door, table, fountain, shelter, houses) are now placed from the level's path line: `L.foot` (default
  184; stage.lua sets `Sc.FOOT` before it draws, and scene.lua adds `dy() = FOOT - 184`). The painted path is
  clamped to `foot` (was 184), the pond's water runs to the bottom of the world, the hollow log's art shadow sits
  on its piece's `foot`. `look.lua`'s foreground band finds the flat ground at `foot` and stands on the world's
  bottom row (a flat level: screen y 240 as before). `tools/level_to_tiled.py` keeps a piece's `foot` drag-safe
  (`rely.foot`). Proof: the `--test` tours drawn on `round1` and on this branch, 147 of 153 shots pixel
  identical (River Walk 24 of 26, City Park 21 of 23, Downtown 30 of 31, Night 24 of 25, Soder Hill 22 of 22,
  lab_tall 13 of 13, Rooftops 13 of 13); the 6 others differ only in the debug view's FPS / MS counter
  (x 8-30, y 456-470 of the 640 x 480 shot).
- **The tall City Park has City Park's art.** `maps/citypark_tall.tmx` gets `art = "park"` and `foot = 328`, the
  hollow log's piece back (standing on the path: `rely.foot`) with its prop hidden as in City Park, and the title
  loses "(greybox)"; export regenerated, `tools/make_citypark_tall.py` makes the same (checked with `--force` into
  a scratch copy). On the path the camera rests at the bottom of the world, so the low road now looks as City Park
  does today. `--physics` 82 of 82 as before.
- **The treetop tier, dressed** (`scene.lua`: `Sc.drawTreetops`, called before the back props, and the tier's
  ledges in `Sc.drawPropArt`). Only existing art and code-drawn pieces; no box or test changed. The tier is
  found from the map: ledges 90 px or more over the path (`L.foot`), decoration 100 px or more over it; parts by
  name, an unnamed ledge belongs to the named ledge over it, else to the one before it in the map:
  - branches (the plane tree, the limes, the old oak's crown, twig and stub, the ash, the big oak's boughs): crisp
    and outlined like the old oak's branches: a bough lying across its trunk (thick over it, thin at the tips,
    leafy twigs at both tips), or a branch reaching out from the nearest trunk (`drawBranch`, as in City Park)
  - trunks: the narrow decoration boxes, drawn faded down to the path with flaring roots and bark furrows, up into
    their canopy; the big oak's 32 px trunk with knots. A canopy with no trunk near one end gets one there on dry
    ground (the alders on the creek's far bank): nothing floats
  - canopies: the crowns of `park_tree1`, `park_tree2` and `park_oak` (their trunks masked out, faded as
    decoration), overlapping over each crown box; the big oak's crown is oak crowns over two rows of trees, the old
    oak's top is one oak crown over its art
  - the treetop walk and the alder walk: a plank deck (crisp, outlined), a rope hand-rail on posts behind Pepper,
    timber legs with cross ties down to the path or into the water (seen through it, as the stepping stones are)
  - the rose arbour: white slats (crisp) with a rose along their front, each on two faded posts with a climbing rose
  - the play tower: yellow decks and grey posts, crisp, as the slide tower's art
  - the low bough over the alder walk: a thick crisp bough bending up into the leaves towards its trunk
  - the magpie's nest at the top of the big oak: dark twigs, not faded, a stray twig or two, so it reads from below
- **The sky goes on above the old horizon.** In a tall art level with the look on, the sky rises with the far city
  (factor 0.3, so the warm glow stays behind the skyline) and goes on 120 rows above its old top in five deeper
  blue bands (City Park's script: `above`; a script without them carries its top step on upwards), with a second,
  sparser row of high clouds (`L.cloudsHigh`). A flat level, or the look off, draws its sky as before.
- **Checks.** `tools/tiled/check_tiled.lua`'s drag check knows a piece's `foot` moves with it. The tall tour
  (`--test`) also shoots every screen on the low road (`ct_31`-`ct_39`) and up in the treetops (`ct_41`-`ct_49`).

## Branch `r3/bonus`: FETCH FRENZY, the golden bone bonus round (22 Oct)
Built on `round1`. Gameplay only, no new art, no SpriteCook. Pepper's files are untouched (`check_pepper` UNCHANGED).
- **The rule.** A level cleared with at least one of its golden bones found (`super` bones, `bone_gold` art; every
  level has two to four) opens FETCH FRENZY after the tally, before the story card (`Flow.bonusOpen`). No golden
  bone: tally, then the story card as before. Its points go into the tally's and the run's score.
- **The round** (`riverwalk/bonus.lua`). One screen of City Park lawn (City Park's own sky, skyline, tree line,
  near trees and path, drawn by `scene.lua`), 30 seconds. Mia stands on the left and throws every item with a
  throwing animation (her wave clip winds up for 0.36 s with the item in her hand, the cheer clip's open arms let
  go); nothing moves by itself. Balls bounce and roll, sticks spin and drop flat, frisbees glide down slowly.
  Pepper is the levels' Pepper (`pepper.lua`'s controller and numbers): she runs, hops, jumps, crawls; her body box
  catches. In the air: +100, on the lawn: +50, both count as catches; off the screen or 3 s lying still: lost.
  The stick and the frisbee are a few hand-placed pixels in code (12 x 3, 12 x 5); the ball is `art/ball.png`.
- **Three rounds**, so two levels in a row never play the same one: BALL RALLY (levels 1 and 4), STICK TIME (2 and
  5), FRISBEE FLOAT (3). Each starts with a short and a long ball to learn the arc; 14 or 15 throws.
- **Extra life at 11 catches** (`B.LIFE_AT`). Tuned with a model child set before tuning (reacts 0.45-0.9 s late,
  runs to a spot up to 50 px off, jumps up to 0.25 s off time, skips 40% of the jumps): 50% of 120 model rounds
  reach 11 (10 would be 84%). At most 9 lives. Best points saved in `bonus_best.txt`.
- **Screens.** Intro card (FETCH FRENZY!, the goal, PRESS ANY BUTTON), READY... GO!, three signs (catches against
  the goal, the time, points), the last 5 seconds big with a tick, TIME UP!, the result card (catches, in the air,
  points, EXTRA LIFE! or GOOD TRY), then the flow goes on. Cards never cover Pepper (she is drawn over them).
- **Hooks**: `main.lua` (state `bonus`, `--bonus`, `--level X --bonus`, `--bonus --physics`, `--bonus --auto`),
  `flow.lua` (`bonusOpen`, `bonusBest`), `hud.lua` (`U.bonusStatus`).
- **Checks**: `love riverwalk --bonus --physics` (`tests_bonus.lua`) 23 of 23: every throw lands on the lawn under
  the signs and before the time is up; every throw can be caught in the air by the real controller starting
  where the throw before landed (simulated, 44 of 44); Mia winds up before every throw; the timer ends the round;
  the extra life at 11, not 10; the points; the autopilot catches 13-14 of each round; the model child; the flow
  (golden bone: tally, bonus, story; none: tally, story). `--bonus --auto` records the autopilot (rec/).
- **The flow test reaches it** (`tools/check_flow.sh`, 103 of 103, was 94). Three small hooks in
  `tests_flow.lua` (marked `[bonus]`): run level 1 is cleared with a golden bone, so the bonus opens between its
  tally and its story card (no extra life, the points carry into level 2's score); level 2 checks there is no
  bonus without one; the clean clear at the end (every bone) plays it with the extra life before the ending.
  The cases themselves are `tests_bonus.flow`. Screens: `flow_b*.png` (run) and `flow_c*.png` (clean clear).

## Branch `r3/design`: the tall Downtown and the Metro plan (22 Oct)
Built on `round1`. Level design only: no engine files changed, no SpriteCook, music untouched.
- **Downtown, tall** (`downtown_tall`, greybox, not in `levels.lua`: `love riverwalk --level downtown_tall`). A
  Tiled map, `maps/downtown_tall.tmx` (440 x 60 cells, 3520 x 480 px, 11 x 2 screens), exported to
  `level/tiled/downtown_tall.lua`; `level/downtown_tall.lua` loads it. Its first version is drawn by
  `tools/make_downtown_tall.py` from Downtown (moved down 30 rows: the street is at y 424, and on the street the
  camera rests at the bottom of the world, so the low road looks as before), plus the high road over the roofs:
  a balcony from the bakery sign, the loggia over the statue (the cat can be barked off from there), the guild
  house's pitched roof (one-way steps 4 px high) with its chimney (the golden bone), the gallery over the fountain
  in two solid halves (the gap between them drops onto the fountain's top tier), six roof ledges over tram street
  and the flower market with a springy window awning, and the footbridge over the canal. Both roads meet before the
  flooded square. The trams have `roadY = 424`. 2 lamps up high, 27 more bones, the GOLDEN BONE secret (5 in all),
  the landmark (Riddarholmen church's spire over the river stairs). Greybox only: no `L.art` (the town art is
  drawn at y 184). Downtown's old balcony route stays as a middle tier under the roofs.
- **Checks** (`riverwalk/tests_downtown_tall.lua`): `--physics` 81 of 81: the world and camera, the trams on the
  street only (both zones: set off with the warning, hurt on the street, pass under the shelter, never come on the
  roofs), her 46 / 24 px measured, 47 jumps simulated with her own controller (the low road, the two ways up, the
  high road standing and running, the old balcony route under the new roofs), 4 jumps that must fail, the roof's
  steps and the chimney, 63 ways off the high road all land with no heart lost and never in the water, the solid
  walks over water, the cat from the loggia, bones, lamps, secrets, the fetch ends the level. `--auto` plays the
  high road with the ball: GOOD GIRL! in 56.9 s, no heart lost, 4 of 5 secrets. `--qa` 0 problems.
  `tools/check_tiled.sh` covers `downtown_tall` (LEVELS, MAPPED, its export up to date).
- **Paper map with routes:** `python3 tools/draw_routes.py downtown_tall <out.png>`.
- **`docs/downtown_tall_beatsheet.md`**: the four beats of bounce and carry, screen by screen on both roads, every
  jump with Pepper's numbers, the cat from above, timing (par 85 s), what the engine must add (the town art and the
  look at any height), open questions.
- **Metro, the paper map** (level 5 in the plan; not wired into the game): `docs/metro_beatsheet.md` and
  `maps/metro_sketch.tmx` (320 x 90 cells, 2560 x 720 px, drawn by `tools/make_metro_sketch.py`): Sergels torg and
  the ticket hall, the long passage, Stockholm City's platform, the tunnel and Odenplan, three rows in a zig-zag
  joined by switchback escalators. New kinds of objects in the map: `escalators`, `walkways`, `gates`, `doors`,
  `wagon`, `signs`, `hazards`. The beat sheet specifies them for the engine (moving steps riding and walking
  against them, walkways, ticket gates with passengers and the booth, screen doors with chime, light and timer,
  the work wagon's ride with ducking under warned tunnel signs and its camera, the suitcase and the floor
  scrubber), with the checks to write. `tools/draw_routes.py metro_sketch` draws escalators with arrows,
  walkways, gates, doors, the wagon's ride and the signs.

- **Checks on this branch:** `check_pepper` PEPPER UNCHANGED (4591 steps), `check_flow` 94 of 94, `check_tiled`
  passed (downtown_tall in LEVELS and MAPPED, its export up to date), Downtown `--physics` 70 of 70, downtown_tall
  `--physics` 81 of 81, citypark_tall `--physics` 82 of 82. Renders, the screenshot sheet and the autopilot GIF are
  in `/home/claude/out/r3-design/`.

## Branch `r3/rooftops`: Rooftops at full length, readable steam (22 Oct)
Built on `round1`. Level design, the rooftops' own code and checks; greybox, no SpriteCook. Pepper's files are
untouched (`check_pepper` UNCHANGED).
- **Rooftops, full length** (`tools/make_rooftops.py`, now standalone: it no longer starts from the paper map).
  12 x 5 screens, 3840 x 1200 px (was 6 x 4). The skyline climbs to the right in tiers: the street (1144), the
  bakery (T1 952), T1b (856), the market hall and the laundry (T2 760), the roof bar (T3 568), Mia's roof cafe (T4
  376), the copper roof (280), the nest chimney (184). The four beats of the steam puffs and loose tiles: the
  kitchen fan up a wall too tall to jump, with a flat roof under it, and the light well's three loose tiles with a
  fan in the well to climb out (introduce, safe); the market hall (a puff over the sweep's chimneys, the skylight's
  tiles), the laundry vent and the balcony's tiles between two puffs (practise); the roof garden's goose and the roof
  bar's gull and springy awning with puffs (combine); the sauna that only steams on a bark, at the nest (twist). The
  high road floats over it on ledges, 8 loose tiles and 4 puffs, with the golden bone on the bakery's chimney pot
  and the secret ROOF WALKWAY; it meets the low road on the copper roof. 14 vents, 17 loose tiles, 7 lamps, 76
  bones. Story: Mia takes the building's stairs up to the roof cafe; Pepper goes over the roofs.
- **Steam you can read on a light sky** (`roofs.lua`). The column is now cloud blobs with a crisp blue-grey outline,
  a shaded underside and a lit top (`Rf.blob`), still drawn behind Pepper. Every vent has a visible cap on a stem
  over its mouth: at rest grey, while it warns it turns orange, hops 1 to 3 px and rattles sideways, with small
  outlined wisps and dark specks leaking out and the "!" over it; during the puff it stands open. The landmark from
  below (`Rf.drawLandmark`): while the nest chimney is above the screen, a faded far copy of it (the nest, the gull
  circling, the sauna's thread of steam) stands at the top of the sky, sliding slower than the world, behind the
  roofs.
- **Checks** (`tests_rooftops.lua`): `--physics` 88 of 88 (every vent's apex, its landing with no input and when
  steering, the warning, the cycle, one lift per puff, crouching, a bark, the sauna; every vent runs; the loose
  tiles and all six bridges; every jump on both roads with Pepper's controller; the walls too tall to jump without a
  puff; 27 falls off the high road all land safely below; no bone in a solid; the nest; the fetch). `--auto`: the
  low road GOOD GIRL! in 54.1 s, no heart lost; `AUTO_ROUTE=high`: the high road in 51.8 s, both secrets.
  `--qa`: 12446 runs, 0 problems. The low road is about 6 s under the Morning chapter's 60 to 90 s; the beat sheet
  says how to close it (one more screen on T2).
- **Docs and tools:** `docs/rooftops_beatsheet.md` rewritten to match the build (tiers, beats, both roads, every
  jump, every puff, lamps, timing, open questions). `tools/draw_routes.py` has a `rooftops` entry (the routes on the
  new map). No engine file changed (stage, world, vcam, lift, critters, main untouched).

## Branch `engine/round2`: the review's engine fixes and the rooftops mechanics (22 Oct)
Built on `round1`. Engine only, greybox, no SpriteCook. Pepper's files are untouched (`check_pepper` UNCHANGED).
- **The lift never waits at her crouched height** (review, SHOULD FIX 2). A lift coming down over a crouched Pepper
  waited 16 px over her paws; when she let go of Down she stood up into the platform (pepper.lua's headroom test
  sees only solids). `lift.lua` now keeps her standing room (26 px) plus 2 px (`Lf.CLEAR`) clear over her whether
  she crouches or not, and a lift that is already lower than that over her (she crawled in under it) is wound back
  up by its operator until she has room. lab_tall `--physics`: 4 new checks (the review's case, crouched then
  standing; a lift too low over her backs up), 34 of 34.
- **Traffic and ground at any height** (the flat levels' y 184 made a level's field). A bike, cart or tram zone in
  `L.bikes` may give `roadY`, the feet line its road is at (default 184: every existing level is unchanged). The
  vehicle drives at `roadY` (and follows the terrain from 34 px above it, as the bikes did from y 150), the
  warning sign sits at its height, and a zone with `roadY` counts Pepper in only while her feet are on that road
  or up to `band` px (default 90) above it, so a cart on the low road says nothing to her up in the trees.
  `world:groundAt(x, fromY)` finds the highest terrain floor (slopes too) at or below any `fromY`; without
  `fromY` it is the old search (below y 150). In a tall world (more than 240 px) the cat's run, the gull's target
  floor (the floor right under her, ledges too) use it; the gull circles at its height on screen (camera y + 86),
  so it swoops to the floor it targets at any height. The kennel and the hollow log stand on `pc.foot` (default
  184). `qa.lua`'s bikes drive at their zone's `roadY`.
- **The leaf carts are back in the tall City Park.** `tools/make_citypark_tall.py` keeps City Park's two cart zones
  as zones (`roadY = 328`, the low road) with their hints ("CART! GET UP HIGH!", on the low road only), not on a
  `#carts` note layer; `maps/citypark_tall.tmx` and its export regenerated (`check_tiled` passes).
  `tests_citypark_tall.lua --physics` 82 of 82: 5 new cart checks (a cart sets off with its warning as she walks
  in on the path, drives at y 328, hurts her there, passes under her on the picnic table, never comes while she is
  on a treetop over the run). The autopilot (the high road) is unchanged: GOOD GIRL! in 38.5 s.
- **QA in tall levels** (review 5). `qa.lua` flagged "below the level" at 4 px under the world, while the fall rule
  (stage.lua) lets her drop 24 px out of the bottom before it takes her out of play: now 24 + 8 px. A QA run also
  clears a pending fall and puts the vertical camera on her when it places her. `--qa` on lab_tall: 4283 runs,
  0 problems (was 18 false ones); on citypark_tall: 11734 runs, 0 problems.
- **The lab pit can be fallen into** (review 4). It was 32 px: Pepper's feet span 26 px, she has coyote time and
  scrambles up 12 px, so she walked or scrambled across and the fall rule was only reached by tests. It is now
  96 px (x 160-256, `tools/make_lab_tall.py`): a running held jump clears it, a running tap hop only just makes it
  with a scramble at the far edge, walking off or running off the edge falls in (a heart, back to the lamp). The
  hint is "RUN, HOLD: BIG JUMP", the bone over it moved onto the jump's arc. For designers (docs/tiled.md is on
  another branch): a gap Pepper must not walk or scramble across is at least 64 px; a running held jump clears
  about 110 px (from her numbers, not measured). lab_tall `--physics` 40 of 40 (6 new pit checks, all played, no
  teleport), `--auto` GOOD GIRL! in 25.9 s, 13/13 bones, `--qa` 0 problems.
- **The ground in chunks** (review 8). The painted ground (terrain, pavement, path) was one canvas as big as the
  world (a 16 x 3 screen level: 15 to 20 MB of video memory, and wider or taller than the handheld's largest
  texture). It is now cut into canvases of 512 x 512 px (`Sc.CHUNK`, the last ones smaller), each drawn only when
  it is on screen, and a chunk with no terrain or water in it (the sky of a tall level) is not made at all
  (lab_tall: 3 chunks, 1.6 MB instead of 2.6 MB). Each chunk is painted by the same code moved to its origin
  (`clip()` is the scissor in world coordinates), drawing only its own columns; each column's terrain runs are
  worked out once per world and shared. Load time as before (Soder Hill 38 ms, City Park 47 ms here).
  `St.ground` is a `Sc.Ground` with `:draw(cam, camY)`, `:release()` and `:bytes()`. Proof: the `--test` tours
  drawn on `round1` and on this branch are pixel identical: River Walk 24 of 26 shots, City Park 21 of 23, Downtown
  28 of 31, Soder Hill 22 of 22; the others differ only in the debug view's FPS / MS counter
  (`/home/claude/out/engine-round2/debug_counter_diff.png`). lab_tall (its pit changed since round1) drawn with one
  big chunk and with 512 px chunks: 140 of 140 shots identical, across both chunk seams.
- **Steam puffs** (`riverwalk/roofs.lua`, data from Tiled: objects of class `steam`, the level's `L.steam`). Fields:
  `name`; the box `x0, x1, y0, y1` is the vent hood, a solid box (keep it 4 px tall so Pepper walks onto it; its
  top `y0` is the mouth); `lift` (px: the puff's apex is `y0 - lift`, exactly); `every` (s, the whole cycle; 0 =
  only on a bark); `warn` (s, default 0.8: the hood's flap rattles, a "!" over it, two wisps rise 8 px); `puff` (s,
  default 0.9: a semi-transparent column of steam up to `y0 - lift - 16`, 3 frames, behind Pepper); `phase` (s into
  the first rest, so neighbours do not puff together); `bark` (true: it never puffs by itself; a "?" shows over it);
  `say` (the line the first time a bark turns it up); `source` (who makes it: a note). Cycle: rest
  (`every - warn - puff`), warn, puff. A bark with Pepper within 80 px across and her feet within 60 px of `y0`
  starts the warning now. While it puffs, Pepper over the mouth (feet x within `x0 - 6 .. x1 + 6`, feet y within
  `y0 - lift .. y0 + 2`), not crouched, is launched once per puff: only her upward speed is set,
  `vy = -sqrt(2 * 560 * (y - apex))`, and her jump base moved so letting go of A does not cut the rise short (as
  the springy awnings' `bounce`); her controller is untouched. Steam never hurts; Down on the hood stays put.
- **Loose tiles** (props with `loose = true`, one-way ledges 24 x 6; Night Harbour's crumbling planks made general,
  for any level; Night's own planks are unchanged). The moment she stands on one it shakes (`Rf.SHAKE` = 0.6 s, 2 px
  every 0.1 s, a clink, grit), then it is no floor: it falls with gravity and breaks on the roof below (it only
  drops while she is on it, so it never falls on her); `Rf.GONE` = 3 s later it is back, once her box is out of its
  place (a faint outline 0.6 s before).
- **The gull's nest**: `L.magpie` with `look = "gull"` draws the magpie as a gull (`Cr.drawBird`); with one perch it
  stays put, a bark within `bark` px (95) across and 110 px up or down makes it let go of the ball.
- **Rooftops, playable greybox** (`rooftops`, not in `levels.lua`: `love riverwalk --level rooftops`).
  `tools/make_rooftops.py` turns the paper map into `maps/rooftops.tmx`, exported to `level/tiled/rooftops.lua`
  (`tools/check_tiled.sh` checks it is up to date); `level/rooftops.lua` loads it. From the sketch: hoods 4 px tall,
  each lift set so its apex is 16 px over the floor it serves (108, the oven's 140), phases, the oven's vent 8 px
  right on a 16 px longer chimney ledge (at x 1516 her body touched the chimney pot, which stopped the lift), the
  nest as the gull's perch, hints (PICK UP, GIVE, BARK!, the kitchen fan's "HOLD: STAY PUT"). The finale: the
  terrace fan lifts her through the copper roof; one bark there makes the gull drop the ball on the chimney and the
  sauna steam up; its puff carries her to the chimney's top; the ball; a step down onto the sauna's hood, Down + A to
  the terrace, the fetch. `tests_rooftops.lua`: `--physics` 42 of 42 (every vent's apex within 1 px, its landing
  with no input and when steering, the 0.8 s warning before a lift, the cycle, one lift per puff, crouching, a bark
  turns a vent up, the sauna only on a bark; a loose tile a floor for 0.6 s, back after 3 s and not while she is in
  its place, the bridge of three crossed with running tap hops; the cafe table (jump on, crawl under), the walk
  from the street to the terrace, the high road's plain jumps and the chimney pot's scramble, the step off the
  chimney, Down + A off the copper roof; the nest; the fetch ends the level). `--auto`: the low road and the
  finale, GOOD GIRL! in 21.8 s, 21/34 bones, no heart lost. `--qa`: 5509 runs, 0 problems. `--test`: a tour and
  frames of a puff and a loose tile.
- **For `docs/tiled.md`** (on another branch, not touched here): new fields to document are a zone's `roadY` and
  `band`, the `steam` objects and their properties, props with `loose = true`, `magpie.look = "gull"`, a piece's
  `foot`, and the minimum gap width (64 px). The loader (`tiled.lua`) needed no change: all of it passes through.

## Branch `polish/round2`: Tiled maps you can drag safely, and the guide brought up to date (22 Oct)
Built on `round1`. Tools and docs only: no engine, level or map files changed.
- **Drag-safe fields.** Positions that belong to an object (a boat's or lift's `from`, `to`, `fromY`, `toY`,
  `winch`, a ferry's `call` and `rope`, a goose's `x0` / `x1`, River Walk's picture anchor `ax` / `ay`, a kiosk's
  `bx0` / `bx1`, the kennel's `door`, a barrel's `trigger` and `rest`, a bike or tram zone's `endX` and `depot`) are
  now stored in the Tiled map as offsets from the object itself: `relx.<field>` (from its x), `rely.<field>` (from
  its y), `relxy.<field>` (points). `riverwalk/tiled.lua` adds the object's position back, so dragging an object
  in Tiled, or adding rows at the top of a map, moves everything that belongs to it. A hint with a height (`minY`,
  `maxY`) is now a box in the map instead of a band above it: its top edge is `minY`, its bottom edge `maxY`.
  Older maps and exports with plain numbers load exactly as before. (A bike zone's `minY` stays a plain number:
  the game does not use it.)
- **`tools/level_to_tiled.py --upgrade maps/*.tmx`** rewrites older maps with the drag-safe fields, in place,
  keeping notes, layers and object ids, and exports them; the levels the game loads stay the same. The maps on this
  branch are not upgraded yet (the engine branch is editing `citypark_tall.tmx`): run it once after merging.
  The converter also reads a level drawn only in Tiled (`citypark_tall`: its table and rows from its export).
- **`tools/check_tiled.sh`** now covers seven levels (the five, `lab_tall`, `citypark_tall`): the round trip (also
  through Tiled 1.8.2's own export) gives identical tables and rows; the committed maps upgraded in a scratch folder
  give the same levels; and every map, fresh and upgraded, dragged by (16, 80) with 10 rows added on top
  (`tools/tiled/move_map.py`) gives the same level with every position moved along. On the old maps that last
  check fails, as it should (night: 12 boat `from` / `to` left behind).
- **`tools/tiled/render_map.py`** reads the drag-safe fields too (a boat's path, a goose's stretch); the old and
  the upgraded Night Harbour map render to the same PNG.
- **`docs/tiled.md` brought up to date** (review item 9): which Tiled (1.8 or later, checks on 1.8.2, newer ones
  call Type "Class"), the numbers that move with their object, lifts (`rely.fromY`, `rely.toY`, `relxy.winch`,
  one-way, waits rather than squash), hints for one floor (a box: `minY`, `maxY`), barrels, tram depots, the
  smallest gap she falls into (64 px), tall levels (the camera, adding rows at the bottom or at the top and what
  moves with them), and a short "make a new level" walkthrough.

## The old title is back (22 Oct, evening)
- The hand-pixeled title (branch `title/redraw`) was rejected by the owner: the 19 Oct title has far more charm.
  Its merge is reverted on `round1`; the branch is kept for reference. The window is now called "FETCH!".

## Music out of the builds (22 Oct, evening)
- The owner takes music on separately, so builds have no music for now: the merge of `audio/music` (title and
  City Park tunes, jingles) is reverted on `round1`, and the old synthesised loop is switched off
  (`S.MUSIC = false` in sfx.lua). Sound effects are unchanged. The tunes stay on branch `audio/music`.

## Branch `design/round2`: the tall City Park and the Rooftops plan (22 Oct)
Built on `round1` (the height engine, Tiled, music). Level design only: no engine files changed, no SpriteCook.
- **City Park, tall** (`citypark_tall`, greybox, not in `levels.lua`: `love riverwalk --level citypark_tall`).
  A Tiled map, `maps/citypark_tall.tmx` (360 x 48 cells, 2880 x 384 px), exported to
  `level/tiled/citypark_tall.lua`; `level/citypark_tall.lua` loads it. Its first version is drawn by
  `tools/make_citypark_tall.py` from City Park (moved down 18 rows: the path is at y 328, and on the path the
  camera rests at the bottom of the world, so the low road looks as before) plus the new treetop tier: the plane
  tree and the treetop walk over the pond, seven lime trees, the old oak's crown and its top twig (the golden
  bone), the ash and the alder walk over the creek (a low bough to crawl under), the rose arbour, the play tower and
  the big oak, the magpie's nest at its top (its 12th and last perch; 3 new high perches on the way). 3 lamps up
  high, 30 more bones (the 3 on the willows went), 4 secrets (TREETOP WALK and GOLDEN BONE are new; WILLOWS went with the willow branches).
  Greybox only: no `L.art`, the hollow log a plain box, and the leaf carts wait on a note layer `#carts` (a cart
  zone starts only while Pepper's feet are above y 184 and the cart drives at y 184: the engine must read a
  zone's y first; see the beat sheet).
- **Checks** (`riverwalk/tests_citypark_tall.lua`): `--physics` 77 of 77: the world and camera, her 46 / 24 px
  measured, 40 jumps simulated with her own controller (the low road's climbs, the 3 ways up, every high-road
  jump standing and some running, the finale), 3 jumps that must fail, the crawl, 124 ways off the high road
  (walk off and run-jump off each end, Down + A through each one-way ledge) all land with no heart lost and never in
  the water, the two walks over water are solid, the magpie's 12 perches (where the ball lands after a bark),
  3 perches that ignore a bark from below, the nest perch stays put, bones (none in a solid, all within a jump),
  the fetch ends the level. `--auto` plays the high road and the finale: GOOD GIRL! in 38.5 s, no heart lost,
  2 of 4 secrets. `--test` a screenshot tour. `tools/check_tiled.sh` also checks its export is up to date.
- **`docs/citypark_tall_beatsheet.md`**: the four beats of the magpie idea, screen by screen on both roads, every
  jump with Pepper's numbers, the 12 perches, secrets and the golden bone, timing (par 75 s), what the engine must
  add (cart zones, the hollow log, the art and the look at any height), open questions.
- **Rooftops, the paper map** (level 3 in the plan; not wired into the game): `docs/rooftops_beatsheet.md` and
  `maps/rooftops_sketch.tmx` (240 x 120 cells, 1920 x 960 px, drawn by `tools/make_rooftops_sketch.py`): the street
  and the cafe, three stairwells, flat roofs T1 and T2, two pitched roofs, the roof terrace (Mia), the copper roof
  and the nest chimney (the landmark, top y 136). The main route takes the stairwells; the high route rides six
  steam puffs and five loose tiles, with the golden bone on a chimney pot. Two new kinds of objects in the map:
  `steam` (vents: lift, every, warn, puff, source, bark) and props with `loose = true`. The beat sheet specifies them
  for the engine: the steam puff (cycle, warning, the lift as `vy = -sqrt(2 * 560 * h)` with the bounce's jumpBase
  trick, one lift per puff, a bark starts a puff) and the loose tile (Night's crumble made general: 0.6 s shake,
  fall, back after 3 s), plus the gull's nest and the checks to write.
- **Paper maps with routes** (`tools/draw_routes.py <map>`): the map rendered by `render_map.py` with the main route
  (blue), the high route (orange), lamps, secrets, the golden bone, steam puffs with their lift, loose tiles and the
  landmark. Renders, the autopilot GIF and a screenshot tour are in `/home/claude/out/design-round2/`.
- **City Park tall, hints:** City Park's hints for one spot show only on the low road (`minY = 290`), so "STOP, THEN
  HOP" no longer shows on the alder walk.
- **Checks on this branch:** `check_pepper` PEPPER UNCHANGED (4591 steps), `check_flow` 94 of 94, `check_tiled`
  passed (and citypark_tall's export up to date), City Park `--physics` 73 of 73, citypark_tall `--physics` 77 of 77,
  its autopilot GOOD GIRL! in 38.5 s.

## Branch `engine/height`: levels that climb and drop (22 Oct)
Built on `main` (v0.5). The engine for the tall levels (rooftops, the building site, the metro); the five levels
play and draw exactly as before. Greybox, no SpriteCook credits.
- **Tall worlds.** A level map may have more than 30 rows: the world is rows x 8 px high (`world.height`). The
  ground canvases are as tall as the world. Everything that assumed 240 (a lost ball, the shadows' floor search,
  Soder Hill's hatch rule) uses the world's height, which is 240 in the five levels.
- **The vertical camera** (`riverwalk/vcam.lua`). `s.cam` is still the camera's x; `s.camY` is new (the world y at
  the top of the screen; always 0 in a world 240 px high). Standing, the camera settles so the floor she stands on
  is at screen y 168 (a "platform snap": eased, at most 300 px/s). In the air there is a dead zone (her feet between
  screen y 64 and 204): hops and jumps do not bob the screen. Falling more than 24 px below the floor she left, it
  leads down (her feet go to screen y 120). Up held while she stands still looks up 64 px, Down held while she is
  crouched and still looks down 64 px, after 0.5 s. What Up and Down do to Pepper is unchanged. `Vc.snap(s)` puts
  the camera on her at once (the start, a respawn; tests use it after moving her).
- **Drawing.** `St:draw` draws the world translated by `-camY` (the HUD, the talk panels and the foreground band
  stay screen space; the night's darkness stamps its light pools at their screen y, `night.lua`). The far layers move down slower than the world as the camera rises
  (sky 0.1, far city 0.3, mid trees / houses 0.6, from the bottom of the world), so climbing rises over the city;
  the sky's top colour fills in above. `Talk.pepperRect` and the cards' Pepper (main.lua) use her screen y.
- **Movers on both axes** (`riverwalk/lift.lua`): an `L.movers` entry with `fromY` (and `toY`) goes to and fro along
  the line from (`from`, `fromY`) to (`to`, `toY`) at `speed` px/s, resting `pause` s at each end. It is one-way (jump
  up through it, Down + A drops off), carries Pepper and a resting ball both ways, and never crushes her: if carrying
  her would push her into a solid, or the platform would come down (or slide) into her, it waits. `winch = { x, y }`
  draws its motor house with the operator who runs it. Movers without `fromY` are moved exactly as before.
- **Hints by height:** a hint in `L.hints` may have `minY` as well as `maxY` (her feet between them), so a tall
  level can say different things on different floors.
- **Falls.** Falling out of the bottom of the world costs a heart and goes back to the last lamp, as the water does
  (`fallT`; not on Soder Hill, whose hatches have their own rule). Landing on a lower floor costs nothing.
- **The test level `lab_tall`** (`level/lab_tall.lua`, `.map` from `tools/make_lab_tall.py`; not in the play order:
  `love riverwalk --level lab_tall`): 3 x 3 screens (960 x 720). The ground floor with a pit, stairs up, three 4 px
  steps, a scaffold of one-way planks, a beam with a 128 px drop onto F2, the goods lift up to the roof, 3 lamps, 13
  bones, Mia on the roof with the ball nearby: pick it up, give it to her.
- **Checks:** `riverwalk/tests_lab_tall.lua`: `--physics` (30 checks: the camera up the stairs, no bob on a jump,
  look up and down, the tall drop and the lead down, the lift up and down, waiting under a ceiling and over her head,
  the pit, the fetch, and the five flat levels at camera y 0), `--auto` (clears it: 25.9 s, 13/13 bones, no heart
  lost), `--test` (a screenshot tour, frames of looking up and down in `rec_lab_tall_look/`).
- **The five levels unchanged:** `check_pepper` (all three) UNCHANGED; `--physics` 73, 70, 40, 23, 37 of the same
  checks pass; the autopilots' runs are identical (44.2, 51.6, 66.3, 73.3, 81.3 s, same bones); `--qa` 0 problems
  with the same run and frame counts; `check_flow` 94 of 94. The `--test` tours of all five levels drawn on `main`
  and on this branch are pixel identical (120 of 127 shots; the other 7 differ only in the debug view's FPS counter).
  (Run the checks with their own `XDG_DATA_HOME` when other copies of the game run at the same time: they share the
  save folder, and `check_flow` fails when two runs write its files at once.)

## Branch `tools/tiled`: levels in Tiled, the map editor (22 Oct)
Built on `main` (v0.5). No SpriteCook credits. See `docs/tiled.md`.
- **Levels as Tiled maps** (`tools/level_to_tiled.py`): a level (`level/<name>.map` and `level/<name>.lua`) becomes
  `maps/<name>.tmx`, a map Tiled 1.8 and later opens: the terrain as a tile layer of 8 x 8 px cells (tileset
  `maps/terrain.png`: solid, water, two slopes, each tile carrying its map character), the rest as objects in the
  layers props, zones, movers, critters, lamps, bones and story, and the level's other fields (time, art, intro...)
  as map properties. Each map remembers its export target, so Tiled's File > Export (Ctrl+E) writes
  `riverwalk/level/tiled/<name>.lua`, the file the game reads; `--export` does the same without Tiled. The level
  table is read by running the level file in Lua (lua5.1, luajit or lua, else LOVE: `tools/tiled/love_runner`).
  All five levels converted.
- **The loader** (`riverwalk/tiled.lua`): `require("tiled").load("level/tiled/<name>.lua")` gives back the terrain
  rows and the table L the game uses today. It is generic: an object goes into the list named by its class (empty:
  the layer's name; "magpie.perches" is a nested list; start, ball, girl, cat, fox and exit are single objects), a
  rectangle gives x0, x1, y0, y1 (or the fields its "box" property names), a point x and y, a polyline its points,
  and every custom property passes through, so new kinds of objects (lifts, vertical movers) need no change. Any
  number of rows: a tall map just works. Text objects and layers named "#..." are notes. The terrain rows go to
  the save folder as `tiled_<name>.map` (as `pepperlab.lua` does) and L.map names that file: no change to
  `world.lua` or `stage.lua`.
- **The check** (`tools/check_tiled.sh`, `tools/tiled/check_tiled.lua`): all five levels go level files -> Tiled
  map -> export -> loader and come back identical (deep compare, lists in order, and every terrain row); the same
  through Tiled's own Lua export (`tiled --export-map`, Tiled 1.8.2 here); the game's exports are up to date with
  `maps/*.tmx`; a tall map (50 rows) with new kinds of objects loads; and which maps were changed in Tiled.
- **City Park loads from Tiled.** `level/citypark.lua` starts with `local USE_TILED = true` and returns the level
  from `level/tiled/citypark.lua`; the rest of the file (and `citypark.map`) stays as the fallback: set it to
  false to play the original. Its physics checks, autopilot (44.2 s, as before), QA and the flow test pass
  unchanged. The other four levels still load from their own files; switching one is the same two lines.
- **Zones with no height** (hints, bike and tram zones, gull stretches) are bands stacked above the map in Tiled,
  the first one on top, so they no longer cover the level. **A preview without Tiled:**
  `tools/tiled/render_map.py maps/<name>.tmx out.png --rows 3` draws a map layer by layer (terrain, props by kind,
  zones, movers with their paths, geese with their stretches, lamps, bones, the magpie's perches numbered, hints).
  The tools find LOVE and Tiled in `/Applications` on a Mac with no Lua installed.
- **`docs/tiled.md`**, a guide for drawing levels: the files, opening a map, the units and Pepper's limits (34 x 26
  px, 16 crouched; hop 24, held jump 46, scramble 58 px), what each layer and object means, adding a prop, a bone
  or a lamp, notes, exporting (Ctrl+E), running the game on a Mac, switching a level to Tiled and back, taller maps.

## Branch `assets/v2`: the tram fix and art for the new pieces (19 Oct)
Built on `levels/v2`.
- **The trams end in tram sheds** (Downtown). Before, the first tram vanished in plain view before the fountain,
  and the second drove on across the flooded square on its rails. Now each line ends in a tram shed (`TRAM SHED`,
  a solid prop) with its door on the right: a zone's `depot` is the door's x; the tram is drawn and hurts only
  right of it (a scissor), so it drives in and is gone. The shed roofs are perches: the first shed stands after
  the fountain (a hop from the rim), the second at the far side of the flooded square, where the last bounce
  lands. The second kiosk is gone; the first kiosk moved 12 px right, so the lamp between shed and kiosk has
  room for Pepper. New checks: tram 2 goes into its shed and never over the water; no bone in any level is
  inside a solid. The test tour shows a tram driving into each shed.
- **Art for the new pieces** (SpriteCook, 250 credits; `tools/build_critters_art.py`, sources in `source_sheets/` and
  `source_scenery/`): the goose (walk, rearing hiss with wings up, take-off and flight: 22 frames), the gull (6 flap
  frames), the rowing boat with its rower (8 rowing frames), the harbour jetty, and the tram shed (70 and 96 px
  wide). Still images were made at about 2-5x game size, reduced with a box filter, snapped to their own colours
  and outlined; the animations were made from those 1x images, so they keep the game's pixel scale. Each was
  pulled out of the browser as a false-colour picture and checked against a hash of its pixels (all exact).
  Code drawings stay as the fallback when a file is missing.
  - The goose's frame follows what it does: walking (by distance, so its feet don't slide), rearing up to hiss,
    flapping as it charges, standing, taking off and flying away when barked at. The "!" sits above its head.
  - The rowing boats' decks are 7 px lower (y 219: the hull sits in the water). The rower rows while the boat
    moves and sits at the end it rows towards, so Pepper, boarding at the other end, never hides him.
  - The gull swoops 2 px higher, so a crawling Pepper on the quay (3 px above a boat's deck) still ducks it.
  - `tools/check_pepper.sh`: the River Walk trace re-recorded (first difference step 2295, the lower decks);
    the lab and file checks are unchanged.

## Branch `level4/soder`: Level 4, Söder Hill, the chase (night of 18-19 Oct)
Built on `levels/v2` (c218a0e). Greybox, no SpriteCook credits. See `docs/soder_beatsheet.md`.
- **A new manner of play, Lion King's Stampede our way** (`riverwalk/chase.lua`, `L.scroll`): the screen moves on by
  itself (50 to 78 px/s by section) and the ball rolls ahead of Pepper down the hill, always on screen. The left
  edge pushes her along; pinned against something she didn't jump or crawl under costs a heart and sends her back
  to the last lamp. On the ground she can't run further than 240 px into the screen while the ball rolls, so the
  chase sets the pace (a jump still flies at full speed). Open cellar hatches are gaps in the street (a heart).
  The ball knocks a barrel off a stack twice: it rolls down the stairs slower than the chase; jump it (a heart on
  touch). At the bottom the ball stops against the quay railing, the scroll stops, and it is a normal fetch: pick
  it up, give it to Mia.
- **The level** (`level/soder.lua`, `level/soder.map` from `tools/make_soder.py`): 16 screens (5120 px), six stair
  flights from y 112 down to the quay at y 208, 7 hatches, 2 barrel stacks, crates, hanging signs and an awning
  and an arch to crawl under, bikes, cafe tables with parasols, a fruit cart, two balconies (gold bones, secrets
  CAFE BALCONY and HIGH STREET), 3 lamps, 45 bones. Time 200 s, par 118 s. Autopilot: 73.3 s, no hit (the other
  levels: 31.4, 29.8, 35.1 s).
- **Flow:** added to `levels.lua` as level 4. River Walk now has an outro leading into it ("UP ON SODER MIA DROPPED
  / THE BALL. IT ROLLED AWAY..."); Söder Hill's outro leads into Level 5 ("IT GOT DARK ON THE WAY / HOME. A FOX TOOK
  THE BALL!").
- **Hooks in `stage.lua`** (one line each, commented): `Ch.init` in `St.new`, `Ch.pre` at the start of `St:update`,
  `Ch.update` after the camera, `Ch.drawBack` and `Ch.draw`, and the rolling ball drawn like a resting one.
- **QA:** `qa.lua`'s fuzz no longer drops a bike into a level without bike zones (it crashed on Söder Hill); the
  random sequence for the other levels is unchanged.
- **Checks:** `riverwalk/tests_soder.lua`: `--physics` (23 checks), `--auto`, `--test` (a 16-screen screenshot
  tour). `--qa` 0 problems. `check_flow` 83/83, `check_pepper` (all three) UNCHANGED, the other levels' physics and
  autopilot unchanged.
## Branch `level5/night`: Level 5, Night Harbour (night of 18-19 Oct)
Built on `levels/v2` (c218a0e). The finale: sniff in the dark. Greybox, no SpriteCook credits. See
`docs/night_beatsheet.md`.
- **The level** (`level/night.lua`, `level/night.map` from `tools/make_night_map.py`): 14 screens (4480 px) along
  the harbour at night. A fox snatched the ball; Pepper sniffs out its three hideouts (a tarp, fish crates, under
  the low jetty), barks it on, picks up the ball it drops and brings it home to Mia at the front door ("HOME AT
  LAST."). Eight water gaps, two rowboats and four small boats (ping-pong movers), eight crumbling planks, a
  mooring post, a net shed to crawl under, a crate tower. 5 checkpoint lamps, 54 bones (3 gold), 2 secrets,
  time 420 s. Autopilot clear 81.3 s; par 135 s.
- **The night rules** (`night.lua`, new): the darkness (a canvas with dithered light pools from the lamps,
  lanterns, boat lights, windows, the porch and Pepper herself; moonlit edges on every floor and the water, so the
  path always reads), sniffing (hold L1 / R1 or Q: Pepper stops and sniffs, a trail of dots points at the hidden
  fox, the dropped ball or Mia, nearby bones glow), the fox (drawn in code; found by sniffing, chased on by a
  bark), crumbling planks (`crumble = true`: 0.5 s, then they fall, back after 3 s).
- **Hooks in `stage.lua`** (each marked `[night hook]`): create `s.night` for a dark level, skip Pepper's
  controller while she sniffs (her movement code is untouched: `check_pepper` UNCHANGED), the bark, the update,
  the fox's hint conditions, bones hidden in the dark, and three draw calls.
- **Controls** (`main.lua`): L1 / R1 now sniff (held); the Lion King look toggles with the L key only
  (`--classic` still starts with it off). `look.lua`'s header says so.
- **`levels.lua`**: the `night` line (number 5, par 135).
- **`qa.lua`**: the fuzz no longer throws bikes at a level without bike zones (it crashed on Night Harbour); the
  random sequence for the other levels is the same.
- **Tests** (`tests_night.lua`): `--physics` 37 checks, `--auto` the scripted clear (rec/ every 3rd frame),
  `--test` a 14-screen screenshot tour plus the fox, sniffing, planks and the tally. `--qa` 0 problems,
  `tools/check_flow.sh` 81 of 81 (unchanged), other levels' physics and autopilot unchanged.

## Branch `levels/v2`: QA, balance and two new levels (night of 18-19 Oct)
Built on `assets/complete`.
- **QA fixes** (an independent QA pass; probes dropped the ball at every x on every surface, 23,216 cases):
  - The ball could be lost forever (it flew out of the level at the edges, or slipped under stairs and the slide)
    or end up inside solid props (flower boxes, grit boxes, the bin, the pier, the stall, the pedestal) where Pepper
    could not pick it up. Now it drops at Pepper's own x when her mouth is inside a wall, never leaves the level
    (kept 14 px from the edges), stops at walls in flight, and any ball that rests out of reach (inside a solid, out
    of the level, or falling for over 2.5 s) goes back to its home spot. Every case now ends with a reachable ball.
  - Mia accepted a ball Pepper never brought (barking the magpie off its last perch while standing by her gave
    FETCH): she now takes a ball only where it lands next to her.
  - A ball resting on the duck boat or the pontoon rides with it (it hovered over the water when the boat left).
  - TIME UP while drowning cost a life and then a heart: the timer waits while Pepper is respawning.
  - The status signs step aside while Pepper is up under them (from the statue's hat, the shop sign, the oak top
    she was hidden behind the HUD).
  - River Walk: "FIND THE BALL ON THE BOAT!" only until Pepper has picked it up; then "GO BACK FOR THE BALL!".
  - Story cards also go on with Start / Enter (kids press it). The volume toast sits at the bottom over menus and
    cards. The old ground canvas (3 MB) is released when a level restarts. Stale comments fixed.
- **Critters** (`riverwalk/critters.lua`, `L.critters`; docs/progression.md): creatures with simple, readable rules.
  Every one warns first, and a bark is always a good answer.
  - Goose: walks to and fro. When Pepper is in front of it within 70 px it hisses (0.5 s, a "!"), then charges.
    Its bite costs a heart, then it struts off the other way (never two bites in a row). A bark within 80 px sends
    it flapping off for good (+200, "SHOO!"). It is 20 px tall: a held jump clears it.
  - Gull (used in River Walk): circles high, squawks and shows its shadow where Pepper is, then swoops down to her
    head height. Crawling ducks under it; a bark while it squawks scares it off for 4 s.
  - `bounce = h` on a prop (used in Downtown): landing on it launches Pepper h px up. Only her upward speed is set,
    so Pepper's own movement is untouched.
  - Hooks in `stage.lua`, one line each: `Cr.init`, `Cr.update`, `Cr.bark`, `Cr.bounce`, `Cr.draw`, and the
    "BARK: SHOO!" hint (`need = "goose"`, only for a goose ahead of Pepper). Two new sounds: hiss, squawk.
- **Level 1, City Park: sneak and bark, 6 to 9 screens** (2880 px; `tools/shift_level.py` opened the gaps and moved
  every x, map column and test literal after them):
  - New screen 4, the goose lawn: a leaf pile with bones, the first goose, and a log (a magpie perch).
  - New screen 7, the creek: three small stepping stones over deep water, 56 px apart. Running across fails (she
    drops past her scramble reach); a jump from standing carries her one stone. Hint: "STOP, THEN HOP". A second
    goose waits on the far bank and hisses as she lands.
  - New screen 8, the rose walk: a second leaf cart run (carts a little faster, every 5.5 s): wait on the bench,
    then the picnic table. A magpie perch on the bench's backrest.
  - 9 magpie perches (was 6), 68 bones, 8 lamps. Autopilot clear 44 s, no hit (was 31 s).
  - QA: lamps moved off the log and the picnic table (a respawn stood inside them); `qa.lua`'s bike sweep tests
    crouch-only spots (under a bench) crouched only. Flow checks use x 1900 for the magpie line.
- **Level 2, Downtown: bounce and carry, 6 to 11 screens** (3520 px):
  - New screen 4, the bakery row: a springy awning launches Pepper over a crate wall 64 px high (more than a jump
    and a scramble); a springier one reaches the bakery sign (gold bone, secret BAKERY SIGN). Holding Down she can
    stand on a springy top. Springy tops have red coil springs on their posts and dip as they launch her.
  - New screen 8, the flower market: two geese on the cobbles. A bite knocks the ball out of Pepper's mouth. Bark
    them off, or go high: the tub, the cafe table, the springy parasol, the balcony.
  - New screen 9, the canal: the awning at the water's edge launches Pepper over it onto a crate wall on the far
    quay. Walking in costs a heart.
  - New screen 10, the flooded square: three springy parasols standing in the water, 88 px apart. From a crate
    at the edge, a held jump onto the first; holding Right she bounces from one to the next and lands on the
    kiosk across the water (our version of Lion King's hippo and rhino bounces). From the street a jump can't
    reach a parasol.
  - New screen 11, tram street again: a faster tram (130 px/s, every 4 s; the first one 110 px/s, every 6 s), so
    Pepper waits for two: on the kiosk, then on the shelter roof. Its zone ends at the shelter, so Mia's spot is
    safe once she is down.
  - `L.ballHomeAtLamps`: a lamp Pepper reaches while carrying the ball becomes its home, so a ball lost in the
    canal comes back by that lamp ("THE BALL IS BACK BY THE LAMP"), not five screens back at the statue.
  - 6 lamps for 11 screens (was 5 for 6), 75 bones, 4 secrets. Autopilot clear 51.5 s, no hit (was 29.8 s);
    hard mode clears too.
- **Level 3, River Walk: water and traffic, 10 to 12 screens** (3840 px):
  - New screens 8 and 9, the harbour, on the quay's level after the bridge: open water with two rowing boats
    (movers with `pause`: a rower in each rows to and fro and rests 1.5 s at each end; drawn in code in
    `setpieces.lua`) and a wooden jetty on piles between them. Hop on, ride, jump onto the jetty, wait for the
    next boat. A gull circles over the water: it squawks and shows its shadow, then swoops at a standing Pepper.
    Crawl to duck ("DUCK!"), or bark while it squawks. Gold high over the jetty (secret JETTY JUMP).
  - Bike zone 2 also has a gull. Bikes a little faster: zone 1 125 px/s every 5.5 s (was 115, 6.5), zone 2
    135 px/s every 5 s (was 115, 6).
  - 5 lamps for 12 screens (was 8 for 10). `L.ballHomeAtLamps` here too.
  - Autopilot clear 66.3 s, no hit (was 35.1 s); hard mode clears too.
  - `tools/check_pepper.sh`: the golden trace re-recorded (the first difference is step 1658, the autopilot
    stopping at the quay to wait for a boat). Pepper herself is unchanged: the lab check (1401 steps) and the
    file check against aa38be5 still pass.
- **Pars** (`levels.lua`, the autopilot's time times about 1.6): City Park 71 s (was 60), Downtown 83 s (was 55),
  River Walk 107 s (was 60). `docs/progression.md` has the measured table: the levels now get longer and harder
  from 1 to 5 (autopilot 44, 52, 66, 73, 81 s).
- **Fixes from an independent review** (a fresh agent played and probed the new sections):
  - Softlock: a lost ball's home by a lamp could be inside a solid (City Park's bin lamp, Downtown's lamp by the
    flooded square's crate), and the ball looped "THE BALL IS BACK" forever. Homes now come from `St:homeNear`
    (24 px past the lamp, 24 px before, or the respawn spot itself, the first that is clear), and a home that
    is still no good falls back to the checkpoint. New checks: every City Park lamp's home is clear; a ball lost
    in the flooded square rests by the lamp, pickable.
  - City Park: the lamp after the creek is now on the far bank (2300), and that goose patrols 2350-2372: a
    respawn no longer lands between a goose and the cart run.
  - "BARK: SHOO!" shows only when a bark would work (80 px, the same as the bark).
  - Gulls: the warning shadow sits on the floor under Pepper even when she is mid-jump (or on the boat under
    her), and is wider than her so it shows; the gull circles below the hint panel and the HUD; a bark resets
    its timer (it came straight back before). River Walk's harbour gull swoops every 4.5 s (was 3.2) and the
    second boat rows faster, so the wait on the jetty is shorter; the second gull is over promenade B before
    the bike zone, not over the bikes.
  - Downtown: "HOLD: STAY ON" (Down) shows above the first springy awning. A springy top's dip counts down by
    time, not frames. The test tour's shots of screens 8-11 now have Pepper on screen.
  - The River Walk golden trace re-recorded again (the harbour timing changed); lab and file checks unchanged.
- **Readability:** the goose is redrawn taller (a long neck when walking; neck stretched out low, beak open and a
  wing up when it hisses), so it reads as a goose, not a duck; its hit box is unchanged. The rower is bigger (red
  cap, face, coat) and leans into each stroke; the oars have a dark outline. Gulls circle a little lower (y 86),
  clear of the hint panel.

## Branch `assets/complete`: the missing assets (18 Oct)
Built on `lk/look` (9c3bcbd). Every placeholder left in the three levels gets real art.
- **The Downtown cat** (`art/cat.png`, `tools/build_cat.py`, `Sc.cat`): modelled on the user's Abyssinian (ruddy
  ticked coat, very large ears, green eyes, pale chin). A hand-pixeled 30 px sitting cat (`source_sheets/
  cat_sit_source.png`, SpriteCook asset 3a0c5b07) animated in SpriteCook (pixel-engine-v1.5, 3 clips, 78 credits):
  idle (tail curl, ear twitch, blink), startle and leap, gallop. Cleaned like Pepper's clips (the animator's grey
  matte removed, 10-colour palette, specks, 1 px outline). It sits on the ball facing Pepper, crouches and arches
  its back when scared, leaps and gallops off. The greybox cat (`Sc.catGrey`) stays for greybox levels.
- **The park keeper pushes the leaf cart** (`art/scene/park_keeper_cart.png`, `tools/build_keeper.py`): City
  Park's cart hazard no longer drives by itself. An older keeper (flat cap, grey beard, green work jacket), styled on
  the River Walk cyclist with the old cart as reference (SpriteCook 14e58436, 36 credits for 3 options) and given an
  8-frame walk cycle (26 credits). Drawn mirrored (the barrow leads, right to left), the barrow's middle on the
  48 x 26 hit box, wheel and boots on the line; the stride follows the distance covered so the boots don't slide.
  Hit box, speed and timing unchanged.
- **A second keeper turns the duck boat's winch** (`art/scene/park_keeper_winch.png`): the rope ferry no longer
  moves by itself. A keeper in the same uniform (grey beanie, ponytail) at a post winch with a rope drum (SpriteCook
  0a12ae1a, 36 credits for 3 options; crank loop 26 credits), drawn mirrored so the winch faces the pond, in place of
  the small `park_winch` drawing. She cranks (10 fps) only while the boat is moving (`Sc.winchFrame`, set in
  St:draw from the rope ferries' `dx`), else she holds the handle.
- **Front-on picnic table** (`art/scene/park_table_front.png`, `tools/make_table_front.py`): the three-quarter
  table becomes the long side seen at Pepper's height: the tabletop's front edge with a thin cap (the top she stands
  on, y 156), the leg posts and the near bench, in the table's own colours, outlined. Same 72 x 28 box.
- **River Walk's code-drawn pieces get art** (`tools/make_riverwalk_pieces.py`, drawn by setpieces.lua at the old
  sizes, the code boxes stay as a fallback): Pepper's kennel in falu red with white corner trim, a flat roof of dark
  boards and a bone sign over the doorway she crawls into (`kennel.png`, 34 x 36); the two kiosks, KAFFE with cups
  and GLASS with ice cream cones, panelled green fronts and a lit window (decoration, faded at load); their awnings
  with a lit top, shaded underside and scalloped hem (`awning_88.png`, `awning_80.png`, outlined obstacles).
- Checks on the branch: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, the autopilot clears all
  three, PEPPER UNCHANGED (trace 2717 steps, lab 1401 steps, files).
- SpriteCook credits for this branch: 238 (1,974 before, 1,736 left).
- **A proper magpie** (`Sc.magpie`): the 14 x 10 placeholder becomes a 24 px magpie pixeled at game size (black
  head and breast, white belly and shoulder patch, long blue-green tail): perched, a tail flick, and two flight
  poses (wings up with white primaries, wings down). The ball hangs at its new beak (`St:beak`). Its perches,
  ranges and behaviour are unchanged (City Park physics 64/64, QA 0 problems).

## Branch `lk/look`, part 2: City Park and Downtown (12 Oct)
- **A colour script per level** (`Look.scripts` in look.lua), as Lion King gives every level its own light:
  River Walk a summer morning (as before), **City Park a golden autumn afternoon** (blue-violet sky to an amber
  horizon, the skyline dusty lilac, the far tree line and near trees hazed warm), **Downtown a bright midday**
  (deep blue sky to a pale horizon, the roofs and facades hazed cool so the street stands out). The art levels' sky,
  clouds, skyline, far and near layers, pond/basin, props and ground go through the same split-tone shader;
  Pepper, Mia, the ball, the bones, the cat and the magpie do not.
- **No foreground band in City Park and Downtown:** their bottom band (the earth, the quay wall) is already dark,
  and dark shapes on it did not read. The foreground now finds the flat ground at Pepper's line itself (River Walk's
  clumps are the same as before), and a script can also use chain fences.
- **More front-on props** (`tools/make_front_view.py`, collision boxes and sizes unchanged, originals kept):
  - `town_crate_front`: the slanted rim corners removed, the apples heaped behind the straight front edge.
  - `town_table_front`: the round top seen from above becomes a 5-row slab at the same top row; the legs reach it.
  - `park_boat_front`: the duck boat's floor and seats no longer show; the near side of the hull rises to the deck
    line Pepper stands on, with the far side's inside as a pale band above it.
- Not changed, for the user to decide: the picnic table (drawn three-quarter, needs a redraw), the hollow log (both
  open ends show, which a side view cannot, but they tell you it can be crawled through). The stone posts, the
  market stall and the log read fine front-on.
- `--lookshots` works on every level (`--level citypark|downtown`).
- Checks: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, autopilot clears all three with no
  foreground overlap, PEPPER UNCHANGED (trace, lab and files).

## Branch `lk/look`: the Lion King look (12 Oct)
Built on `fix/console` (8e28369). River Walk only; City Park and Downtown are unchanged. L (keyboard) or L1 / R1
(handheld) switches the look off and on to compare; `--classic` starts with it off. Code in `riverwalk/look.lua`.
- **Colour script:** one key light for the level (summer morning) and a haze colour per distance, instead of one cool
  grey haze for everything.
- **Split toning per layer (a shader, art files untouched):** light colours lean warm, dark ones lean blue-violet,
  colours a little richer. The further back a layer is, the more it turns into its haze: the skyline lavender against
  a warm horizon, the far shore blue-green, the water deeper. Each colour in maps to one colour out. Pepper, Mia, the
  ball, the bones, the warning signs and the HUD are drawn without it.
- **Sky:** 10 painted bands from deep blue to warm cream at the horizon, joined by 3 rows of 2 x 2 ordered dither.
- **The road recedes:** the road rows scroll 1x at the kerb to 1.3x at the bottom of the screen, in 5 bands chosen so
  the lane markings, manhole covers and drains never shear. Near-lane cars and cyclists slide with their row (only the
  camera movement since they appeared counts, so they still drive in from the edge). The pavement Pepper walks on
  stays at 1x.
- **Foreground band:** dark, back-lit grass verges with shrubs and pairs of bollards, 1.4x, only in front of the road.
  Tops at y 218 (y 206 deep inside a stretch of road, where Pepper only walks at y 184). Never over Pepper: checked on
  every frame of the autopilot run with `LOOK_CHECK=1` (0 overlaps).
- **Front-on boxes (user note: the flower box and the grit box were drawn from above, unlike the bench, bin and square
  planter):** `tools/make_front_view.py` makes `flowerbox_front.png` (the slanted rim and the soil removed, the flowers
  on a bed of leaves behind the rim's straight front edge) and `gritbox_front.png` (front face only, the lid a thin
  band, the side face dropped, plain plank columns repeated to keep the 88 px width; 32 rows, so its top is the
  collision top). Collision boxes unchanged. The originals are kept.
- `--lookshots`: before / after shots of the 10 screens without HUD (tests_look.lua).
- Checks: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, autopilot clears all three,
  PEPPER UNCHANGED (trace, lab and files); Pepper's pixels identical with the look on and off.

## Branch `fix/console`: after the first RG35XX test (7 Oct)
Built on `preview/art` (884b87e).
- **Sound volume on the handheld:** the game has its own volume (0 = off to 10), saved in `settings.txt`.
  - The volume buttons work in the game if the firmware passes them on as the keys `volumeup` / `volumedown` / `mute`;
    a small SOUND bar shows for 1.6 s. They never count as "any button" on the title or the cards.
  - The pause has a SOUND row: left / right (d-pad or stick) turn it down or up, A steps it up and wraps round to OFF.
    This works whatever the firmware does with the volume buttons.
  - Select only toggles the debug view with `--dev` or a test flag (it showed by accident on the handheld).
  - Every key and button press is printed as `[input] ...` (and joysticks when they connect). PortMaster's launcher
    keeps the output in `ports/fetch/log.txt`, so the next console test shows what the volume buttons really send.
- **Rolling wheels:** the promenade bikes and the road's cyclists turn their wheels as they ride. `tools/make_wheels.py`
  clears each wheel's inside (the old spoke pattern never moved) and redraws a hub and spokes (8 on the small bikes,
  12 on the road's) in 4 steps, keeping legs, shoes and the frame's light tubes in front; output `*_roll.png` next to
  the still art. `Rd.drawBike` picks the step from the distance ridden (wheel radius x spoke gap / 4 per step), so the
  wheels turn at the bike's real speed, forwards in both directions. Riders' legs still do not pedal.
- Checks: flow 73/73, physics 33/64/57, QA 0 problems on all three levels, autopilot clears all three,
  PEPPER UNCHANGED (trace, lab and files).

## Branch `ml/ui`: talk panel, nudges, medals, shared play
Built on `ml/fixes` (dad26c3), from the synthetic playtest: kids could not read the long hints and got stuck.
- **Talk panel (talk.lua):** the text banner hints are now short dialogue lines. Pepper (bottom left) says the
  control hints as a drawn button picture plus 1 to 3 words: [B] HOLD: SNEAK, [DOWN] CRAWL, [Y] BARK!, [X] PICK UP,
  [X] GIVE, [A] HOLD: BIG JUMP, [A] HOLD + PUSH: CLIMB, [A] TAP: HOP. The girl (bottom right) says the goal and story
  lines (BRING ME THE BALL!, IT DROPPED THE BALL!). The portraits play their talking loops at 9 fps while the line
  is said, then rest on frame 1. The buttons are drawn in code (RG35XX: A right, B bottom, X top, Y left; the d-pad
  for Down). The panel never covers Pepper: when she is low (the quay, the duck boat) it moves to the top of the
  screen, or is not drawn. Teaching hints win over other messages; a girl's zone line goes away after 4.5 s.
- **Hints that never showed:** the log hop (the magpie hint always matched first: now sneak while running at the
  magpie, the hop once she sneaks, BARK! in range), the magpie line (it started at x 1560, where nobody still lacked
  the ball: now from x 300) and GO BACK: BARK AT THE CAT (it now starts where a bark stops reaching the cat). The
  City Park climb hint starts at x 900. New hint needs: `catnear`, `magpienear`, `magpieahead`.
- **Stuck nudge:** 2 s pushing without getting anywhere, or 3 s idle where a control hint applies: the needed
  button bounces above Pepper's head (Down if she fits through crouching, else A, when no hint applies) until a
  button is pressed. It only reads Pepper's position, speed and the buttons.
- **Tally:** clear time, best time per level (`time_<name>.txt`), medals NO HIT, ALL BONES, PAR TIME (par in
  levels.lua: 60, 55, 60 s), kept in `medals_<name>.txt` and shown on the level select. SECRETS n/m when the stage
  reports `secrets` and `secretsTotal`. The tally sits where it misses Pepper.
- **Shared play:** GAME OVER offers TRY AGAIN (the same level, 3 lives, the score it started with) or MENU. Story
  cards wait 2 s, then only A goes on (a blinking A shows). The pause has GO ON and QUIT, and QUIT asks (NO first);
  B and Esc only go back, never quit. Cards move to miss Pepper, and she is drawn again over the dim.
- **HARD MODE:** a main menu item, saved in `hard.txt`, passed to the stage as `carry.hard` (`self.hard`). A HARD tag
  on the HUD, tally and level select; no hints and no nudges. (The gameplay side is on the sibling branch.)
- Flow test: 67 checks (was 32). Physics 17/40/45, QA 0 problems on all three levels.
- Pepper is unchanged: `tools/check_pepper.sh` still finds all 2,752 steps identical.

## Branch `ml/levels`: kinder spots, no waiting, traffic warnings, secrets, hard mode (level side)
Built on `ml/fixes` (dad26c3), from the persona playtest (kids quit at a few spots and waited too long). The hint
UI, the tally drawing and the menu are on a sibling branch; this branch gives them `stats().secrets`,
`stats().secretsTotal` and `self.hard`.
- **Pepper is frozen, and proven so without a level:**
  - `love riverwalk --pepperlab` builds a small test room in code (28 and 56 px blocks, a low bar, a one-way
    ledge, a moving deck, a water pit, stairs) and plays a fixed 1,401-step script (stand, walk, run, tap and
    held jumps with scrambles, falls and landings, crawl, skid, turn, bark, pick up, up and down through the
    ledge, a ride, a jump over the pit, stairs, a walk into the water), printing her state every step.
    `tools/check_pepper_lab.sh` compares it with `tools/pepper_lab_golden.txt` (recorded before any other change):
    PEPPER UNCHANGED.
  - `tools/check_pepper_files.sh`: pepper.lua, pepper_frames.lua, art/pepper.png, input.lua and world.lua are
    byte-identical to aa38be5.
  - `tools/pepper_golden_trace.txt` (River Walk on autopilot) was recorded again because the level changed: the
    first 459 steps are identical; at step 460 the autopilot, standing on the bin, jumps for the new kiosk awning
    instead of running off the bin. 2,717 steps now (2,752 before).
- **Engine (`setpieces.lua`, called from small hooks in `stage.lua`):**
  - Hard mode: `St.new(def, { hard = true })` (or `--hard` for the checks): 1 heart (also after a lost life),
    bikes, the leaf cart and the tram 25% faster.
  - Rope ferries (a mover with `call`): they wait at their far end, are winched to the near end when Pepper comes
    near and wait there for her, and carry her across when she stands on them. Their rope is drawn.
  - Traffic: a bike, cart or tram is sent so that its front reaches the screen edge 1 s later; its bell rings
    then (new `ding` for the tram, made in code like the other sounds), and a small warning sign (13x13 yellow
    diamond with "!" and an arrow) shows at the right edge at the lane's height until it is on screen, above
    Pepper's head if she stands there. The old gold bars are gone. `start = "enter"`: a zone sends its first
    vehicle as soon as Pepper walks in.
  - Secrets (`L.secrets`): reaching one plays a jingle (`secret`) and says "SECRET! NAME n/N"; `stats()` returns
    `secrets` and `secretsTotal`.
  - Code-drawn pieces (`L.pieces`): Pepper's kennel, the kiosks and their awnings, the hollow log. Their
    collision is an ordinary hidden prop with the same box.
  - The magpie can have a calmer perch (`flee` per perch).
- **City Park:** the first magpie perch flees a running Pepper only at 80 px (bark range 95; the log stops a
  running kid at 81 px). The oak's high left branch is no longer a perch; the magpie sits on the lamp post
  before the oak instead, and every perch now drops the ball on the path or on a top of the main route (checked
  for all seven). Stepping-stone gaps 32 px (were 40). The duck boat is a rope ferry (the park keeper's winch)
  and waits at the stone. The leaf cart sets off when Pepper walks into its zone. New: the high route over the
  pond along three willows' branches (from the hedge top), a hollow log on the path (hop over or crawl through,
  a gold bone hidden inside). Secrets: WILLOWS, HOLLOW LOG, OAK TOP. 44 bones (4 gold).
- **Downtown:** a flower tub (28 px) as a step before the 40 px pedestal. The tram sets off when Pepper walks into
  its zone. New: the rooftop route with the ball, from the statue's arm along three balconies and over the
  fountain's top tier, down by the lamp before tram street. Secrets: SHOP SIGN, STATUE HAT, ROOFTOPS. 45 bones
  (3 gold).
- **River Walk:** a planter as a step before the bin in bike zone 2 (the grit box and the pot moved a little).
  The pontoon is a rope ferry and waits at the quay. New: the high route over bike zone 1 on two kiosks' striped
  awnings (the checkpoint lamp moved from 954 to 1074), Pepper's kennel by the house at the left edge (crawl in
  for a gold bone). Secrets: KENNEL, KIOSK ROOFS. 51 bones (3 gold). See `docs/riverwalk_notes.md`.
- **Checks:** `--physics` River Walk 33/33, City Park 64/64, Downtown 57/57 (each secret reachable, each second
  route completed, the ferries, the traffic start and its 1 s warning, hard mode); a test result of nil now
  counts as a failure. `--qa` 0 problems on all three. `--auto` clears all three, also with `--hard`, and prints
  bones, secrets, hearts and time. `--test` has shots of every new spot. `--flowtest` 32/32.
- **Docs:** `docs/citypark_beatsheet.md` and `docs/downtown_beatsheet.md` updated (secrets, second routes, no
  waiting, hard mode, checks); `docs/riverwalk_notes.md` is new.

## Branch `preview/art`: near-lane traffic at its perspective size
- **Cars and cyclists on the road** (River Walk) are drawn for the near lane, which is closer to the camera than the
  promenade: cars about 180-235 x 70-92 px (a Volvo estate in blue and in silver, a delivery van, a taxi, a red
  hatchback), cyclists 73 x 75. Their tops are at y 192, below Pepper's feet, and the frame crops their wheels.
  The promenade bikes keep their size (their hit box is fixed).
- **Facing:** every moving thing faces the way it moves: cars (right), road cyclists (either way), promenade bikes,
  the tram and the leaf cart (left; the cart is now mirrored, its wheel leading), the duck boat, the magpie.
- 7 SpriteCook renders (84 credits; 288 for the art in all). All checks pass.

## Branch `preview/art`: art for the new set pieces
- **City Park:** the three willows over the pond (faded trees, crisp boughs on their ledges), the keeper's winch on
  the far bank, the hollow log (a fallen trunk with hollow ends; it hides the gold bone inside).
- **Downtown:** the flower tub before the pedestal, the three houses of the rooftop route (crisp and outlined, with
  iron balconies as their ledges), the fountain's top tier with water falling from its rims.
- **Far layers:** Downtown's facades and roofs are faded further (40% and 45%, as River Walk's far shore), so the
  obstacles and the climbable houses stand out.
- **Window titles:** "(greybox)" dropped for City Park and Downtown.
- 2 SpriteCook renders (24 credits; 204 for the art in all). No box moved; all checks pass.

## Branch `ml/art`: City Park and Downtown art (fix 11)
Built on `ml/fixes`. Not merged yet: the before/after sheets are for approval first.
- **Art instead of the greyboxes** in levels 1 and 2, in the River Walk style. A level flag `L.art = "park"` /
  `"town"` turns it on; without it the level is drawn as boxes again. No collision box, map, hint, hazard or flow
  changed: every piece is drawn from its prop's box, so box and art stay together.
- **City Park:** the far city (River Walk's skyline), an autumn tree line, near autumn trees, a sandy path with grass
  and earth, the park gate, the leaf piles (they flatten when Pepper runs through), the log, the bench and the bin
  (River Walk's), the hedge on two stems (the crawl gap reads as a gap), the pond with its far bank, mossy stepping
  stones and the duck boat (it faces the way it paddles, its hull in the water), the picnic table (boarded under its
  top: it is solid), the leaf cart, the big oak with branches drawn on its ledges, the slide, the climbing frame,
  the swings, dark bush tops in the foreground below Pepper's line.
- **Downtown:** the far city, old town roofs and spires, a row of Gamla stan facades, a cobbled pavement and street,
  the doorway, apple crates as steps, cafe tables (two legs, so the crawl gap shows) under market parasols, the
  bakers' sign, the market stall and its awnings on posts, the bronze statue (hat and pointing arm on their ledges)
  on its granite pedestal, the fountain (rims, bowl, water jets, its basin), the kiosk, the tram shelter, the tram,
  the RIVER sign, the stone stairs down to the river, granite bollard tops in the foreground.
- **Rules kept:** obstacles are crisp, mid-tone, with their own 1 px dark outline, on Pepper's line; decoration is
  faded 28% with no outline, its base at y 174; nothing is drawn over Pepper (foreground only from y 221 down). The
  magpie and the cat are still drawn in code (the cat is still its labelled box).
- **Making it:** 13 SpriteCook renders (180 credits) in `source_scenery/`, turned into `art/scene/park_*.png` and
  `town_*.png` by `tools/make_town_art.py` (cuts and repeats of whole rows and columns, exact 2x reductions,
  palettes of 5-12 colours, despeckle). The slide, the climbing frame, the oak's branches, the table legs, the shop
  sign, the fountain and the bollards are drawn by hand.
- Pepper is unchanged (`tools/check_pepper.sh`: 2,752 steps identical); physics 17/17, 40/40, 45/45; QA 0 problems
  in all three levels.

## Branch `multilevel`: three levels, one story
Built on `night/all` (the night's River Walk art, Pepper's extras and the City Park greybox). Not merged yet.
- **Game logic rules:** every level ends with a real fetch: Pepper picks up the ball (X) and gives it to the girl (X),
  who waits at the level's end. The ball only moves when someone moves it (a throw, a fall, an animal).
- **The story over three levels:**
  1. City Park: a magpie has stolen the girl's ball; she waits by the swings.
  2. Downtown: in town the ball rolled across the plaza and a cat sat on it; she waits at the stairs to the river.
  3. River Walk: by the river she throws it again and it lands on a ferry; she waits by the cafe.
- **levels.lua:** the play order.
- **Engine (stage.lua):**
  - Score and lives carry over from level to level; hearts refill.
  - The magpie (`L.magpie`): it sits on a perch with the ball in its beak and flies to the next perch when Pepper comes
    near: at 110 px if she runs, only at 40 px if she walks (hold B). A bark within 95 px startles it: it drops the
    ball, which falls with gravity onto whatever is below (path, bench seat, bin, branch, tower), and flies away. On
    its last perch (the climbing frame) it stays. If the ball falls in the pond it comes back by the last lamp.
  - The magpie is drawn in code (14 x 10 px, black and white, blue tail); it flaps when it flies.
  - `L.exit` (reach a point to clear, optionally with the ball) stays in the engine but no level uses it now.
- **City Park:** the magpie replaces the cat in the oak; the first perch is just past the log, so the level opens with
  the lesson: sneak up, bark. 40 physics checks (new: the magpie flees a running Pepper, lets a walking one come
  close, ignores a far bark, drops the ball on a near bark, the ball falls to the path or onto the oak's branch).
- **Downtown:** the girl waits at the top of the stairs down to the river; giving her the ball clears the level
  (FETCH 2000), the stairs alone do not.
- **Font:** an apostrophe and brackets.
- Pepper is unchanged: `tools/check_pepper.sh` still finds all 2,752 steps identical.

## Branch `multilevel`: game flow
- **Menus:** after the title screen's PRESS ANY KEY a small menu opens over the title picture (dimmed, the logo stays bright): START GAME and LEVEL SELECT. Up and down move, A, Space or Enter chooses, B or Esc goes back.
- **START GAME** plays the levels of `levels.lua` in order: 1 City Park, 2 Downtown, 3 River Walk.
- **Level select:** all three levels. Level 1 is always open; a level opens when the one before it is cleared. Locked levels are dimmed with a padlock. A level whose file is missing says COMING SOON and a run skips it (so Downtown can be added later without other changes). Choosing a level plays from it to the end, with fresh lives and score.
- **One run:** one score for the whole run, lives carry from level to level, hearts refill and the timer starts again in every level.
- **Tally per level:** BONES, the level's bonus (FETCH 2000, or BALL from an exit level), TIME BONUS, then the level's POINTS and the run's SCORE. The points still count up with ticks.
- **Story card:** after the tally, the cleared level's outro lines, then the next level's intro card.
- **Ending:** after the last level, GOOD GIRL! with the final score, the best run, THE END and THANKS FOR PLAYING. A button press after 2 s goes back to the title.
- **GAME OVER** goes back to the title. Unlocked levels stay open.
- **Pause:** shows the level's number and name. Start or Enter goes on; B or Esc quits to the title (no longer quits the game). Esc on the title screen quits the game.
- **Saved:** `progress.txt` (open levels) and `best_run.txt` (best run). The best per level stays in `best.txt` (River Walk) and `best_<level>.txt`, now the level's own points.
- **`default_level.txt` and `build_citypark.sh` are gone:** the level select replaces them. `love riverwalk --level <name>` starts a run at that level without the menus. The test flags still play one level alone, River Walk unless `--level` names another.
- **Font:** a comma.
- **New check:** `love riverwalk --flowtest` (or `tools/check_flow.sh`) drives the real menus with key presses through a whole run and checks the carry-over, the refilled hearts, the saved unlocks, the locks and the skipped missing level: 26 of 26 pass. It saves a screenshot of every screen and one sheet of them, `flow_screens.png`. It uses its own save files.
- **Checks unchanged:** PEPPER UNCHANGED (2752 steps identical), River Walk `--physics` 17/17 and `--qa` 0 problems, City Park `--physics` 36/36 and `--qa` 0 problems.

## Branch `multilevel`: Level 2 Downtown greybox
Built on `ml/downtown` from the multilevel engine (ef6e8b3). Beat sheet in `docs/downtown_beatsheet.md`.
- **Level 2, Downtown (greybox):** a Stockholm old town street and plaza. 6 screens, 1920 px, 300 s, 40 bones (2 gold), 5 lamp checkpoints.
  - Old town lane: hop up the crate steps.
  - Cafe terrace: crawl under the cafe tables or jump on them; their parasols are one-way tops; from the second parasol a jump reaches the shop sign (gold bone).
  - Market: onto the stall's counter and up onto its awning; a crate stack up to a second awning.
  - The plaza: the cat sits on the ball on the statue's arm. Bark near it (90 px): it startles, leaps off and runs away, the ball drops to the street. Pick it up. The pedestal, arm and hat are a climb (gold bone).
  - The fountain: carry the ball over the basin, rim to bowl to rim. Falling in costs a heart, and the ball goes back by the statue.
  - Tram street: the tram drives through like the bikes; wait on the kiosk or the tram stop roof. The girl waits at the stairs down to the river (changed later: see the top section).
- **Story text:** intro "A CAT IS SITTING ON THE BALL!", pickup "BRING THE BALL TO THE GIRL!", outro "BY THE RIVER SHE THREW IT / AGAIN. IT LANDED ON A FERRY...".
- **Greybox town:** `greyStyle = "town"` swaps the park's far trees and bushes for far roofs with church spires and near old town facades (stepped gables, rows of windows, doors). City Park and River Walk draw exactly as before: their `--test` screenshots are pixel-identical to ef6e8b3.
- **Engine (small, generic):** a hazard zone can set its hit box (`w`, `h`) and `rail = true` (it keeps to the street's line, so the tram does not drive down the river stairs); the greybox label is the zone's kind (CART, TRAM); the tally shows the level's own bonus (BALL 1000 here, FETCH 2000 otherwise).
- **Checks:** `love riverwalk --level downtown --physics` 45/45, `--auto` plays to GOOD GIRL! (no hearts lost, 37/40 bones, about 33 s), `--test` screenshot tour, `--qa` 0 problems. Unchanged: River Walk `--physics` 17/17 and `--qa` 0 problems, City Park `--physics` 36/36 and `--qa` 0 problems, PEPPER UNCHANGED.

## Night branch `night/riverwalk-art` (not merged, 6 Oct 2026)
Built on the trial branch `try/scenery-v2`. Every greybox left in River Walk now has art. Pepper is untouched:
`tools/check_pepper.sh` plays the level on autopilot and finds her position, speed, clip and frame identical on
all 2,752 steps. No collision box changed. All art is made by `tools/make_night_art.py` (sources in `source_scenery/`).
- **Bridge on screen 7:** a pale granite bridge abutment with a cornice and a balustrade (SpriteCook, 138 x 162)
  replaces the grey pier. Pepper still crawls under its lintel (y 192). The passage under it is dark at the back
  and the pavement inside is shaded, so it reads as a low way through.
  - Fitted by cutting one brick period out of each side panel, so nothing was rescaled.
- **Pontoon:** a plank deck on two float drums (54 x 12) replaces the PONTOON box. SpriteCook drew it 4x too big and
  a 4x reduction came out muddy, so it is drawn by hand in the render's own colours.
- **Clouds:** eight soft SpriteCook clouds replace the white boxes. They drift as before.
- **Bones:** small hand-drawn bones (11 x 6) with an outline; super bones are gold.
- **Foreground posts:** the two dark bars are now the tops of tarred mooring piles at the bottom edge of the screen
  (three of them). Their tops are below every line Pepper stands on, so they never hide her.
- **Far shore:** the far bridge has 8 arches instead of 40, and the trees continue after it.
- **New check:** `tools/check_pepper.sh` with `love riverwalk --auto --trace` and the golden trace of the approved build.
- **Credits:** 96 SpriteCook credits (4 generations x 2 variations).

## Night branch `night/pepper-extras` (not merged)
- **Visual extras around Pepper** (`riverwalk/extras.lua`), small and pixel-hard, 90s console style. Each has its own switch in `Ex.on`, all on:
  - **Landing dust (`dust_land`):** after a fall of 12 px or more, little puffs roll out from her paws, 1 to 3 each side by fall height. Not on small steps.
  - **Skid dust (`dust_skid`):** while she skids, a small puff kicks off her front paws every few steps and stays behind as she slides.
  - **Run-start kick (`dust_start`):** when she breaks into a gallop from standing, one small puff behind her back paws.
  - **Splash (`splash`):** when she falls in the river: a white burst, a crown of drops, a broken foam line across her that thins out, two ripples sliding away.
  - **Bone pop (`bone_pop`):** a picked-up bone twinkles where it was and a tiny +100 (gold +1000 for a super bone) floats up and blinks out. It is drawn behind her, so it never covers her.
- **Colours:** dust is the pavement's warm greys a step lighter than its lightest stone, so it reads as dust off the paving; the splash uses the river art's light blues. Puffs grow, then break up into a dither and thin out (palette steps, no alpha). Everything scrolls with the level.
- **E key:** all extras off / on in the game, for comparing. `love riverwalk --noextras` starts with them off.
- **Pepper unchanged:** her art, clips, frames, speeds, tuning and physics are untouched (`pepper.lua`, `pepper_frames.lua` and `pepper.png` not edited). The extras only watch her from `stage.lua` and draw. `tools/check_pepper.sh`: PEPPER UNCHANGED (2752 steps identical); 17 physics checks pass; `--qa` 0 problems.

## Night branch `night/citypark` (not merged)
- **Level 1, City Park (greybox):** 6 screens, 1920 px, 300 s. Beat sheet in `docs/citypark_beatsheet.md`.
  - The gate: hop onto the log; a leaf pile hides bones.
  - Benches: jump onto the bench or crawl under it; crawl through the hedge gap. A running jump from the seat reaches the hedge top (gold bone).
  - The pond: stepping stones, then the duck boat (moving platform). Falling in costs a heart.
  - Leaf cart: climb the bin (jump + scramble); the park keeper's cart drives through like the bikes. Get up on the picnic table.
  - The big oak: the cat sits on the girl's ball. Bark near it (90 px): it startles, leaps off and runs away, the ball drops. Branches to climb for a gold bone.
  - Playground: slide tower and slide, climbing frame, the girl. GOOD GIRL!
  - 40 bones (2 gold), 5 lamp checkpoints.
- **Choosing the level:** `love riverwalk --level citypark`. River Walk is still the default. `./build_citypark.sh` builds `CITYPARK_greybox.love`, where City Park is the default (`default_level.txt` in the zip). Best scores are kept per level.
- **Greybox scenery for City Park:** misty boxes per parallax layer, flat grey ground with a 1 px edge, labelled boxes for props, greybox lamp posts and cat. River Walk draws exactly as before (its screenshots are pixel-identical to `night/base`).
- **Engine additions (used by City Park only):** the cat (sit, scared, leap, run, gone), leaf piles drawn over bones that flatten when Pepper runs through, a cart kind for hazard zones, label placement for thin props, the mover's own name as its label.
- **Checks:** City Park `--physics` 38/38, `--auto` plays to GOOD GIRL! (no hearts lost), `--qa` 0 problems. River Walk unchanged: `--physics` 17/17, `--qa` 0 problems, PEPPER UNCHANGED.

## Trial branch `try/scenery-v2` (not merged)
- **Longer level, reworked layout:** River Walk is now 3200 px (10 screens, 420 s).
  - Obstacles stand apart with clear pavement between them and repeat along the level: bench, flower box, bin, grit box, planter.
  - Two bike zones with spaced perches (all above the bikes).
  - The river is wider for the bigger ferry. Lamps every 300-490 px, all checkpoints. 46 bones.
- **Starter composition kept:** the original house and tree, now decoration (faded, base on the pavement's back edge). Their cut left edges sit on the level's left edge, so nothing looks cropped.
- **Decoration rules for houses and trees:** gable, cafe, house and trees are faded like the lamps and have no dark outline. Two more trees along the promenade: the round SpriteCook tree and the original tree completed by SpriteCook.
- **Ferry a little bigger** (252x93): longer decks, taller saloon windows; deck y 206, saloon roof y 184, wheelhouse roof y 154 (ball).
- **The road:** a new asphalt texture (grain, worn tyre tracks, cracks, repair patches, dashed centre line), manhole covers and kerb drains (tools/make_road.py).
- **Traffic:** cars and cyclists pass on the road in the near lane, only where there is road (road.lua). The promenade bikes are drawn as cyclists and ride up and down the stairs instead of floating.
- **QA:** `love riverwalk --qa` (0 problems); 17 physics checks; the autopilot plays to GOOD GIRL!
- **Commuter ferry** (user pick, from their photos of the Djurgården ferry): one image on screen 4 with three hidden boxes: the deck (y 206), the saloon roof (y 188, a hop up) and the wheelhouse roof (y 158, a held jump up), where the ball lies. The old CABIN box and mast are gone.
- **Grit box (SAND)** replaces the low flower box on screen 2 (top y 152, half way up its sloping lid). Halved from a 2x render; the label is repainted.
- **Every lamp is a checkpoint** now, so every lamp lights up when Pepper passes (the one at x 498 never did).
- **Checks:** 16 physics checks (the ferry's two climbs replace the cabin scramble). The autopilot plays to GOOD GIRL!
- **Stockholm bench and bin** (from the user's photos):
  - **Bench (103x51):** green slats, black frame, ball-knob armrests, straight posts. It came out at twice the game scale, so `tools/make_props.py` halves it and lengthens the posts 3 px, keeping the seat at y 156 (crawl gap 19 px). A wider ground shadow fills the pavement under the seat so it no longer looks like it floats (`depth` on the prop, `Sc.shadow`).
  - **Bin (38x59):** the black city bin with gold bands and the shield. Same top (y 128).
- **Obstacles redrawn, bigger and mid-tone (round 2, SpriteCook):** they keep their own 1 px outline, so they no longer look black. `tools/make_props.py` cleans them (16-colour palette, despeckle).
  - **Bench (114x56):** only the seat is solid (y 156-165). Pepper crawls under it (19 px clear) or jumps onto it (28 px up: a held jump or a hop plus a scramble).
  - **Bin (44x60):** top at y 128 (56 px, as high as the cabin roof). A short jump from the bench seat, or a scramble from the pavement.
  - **Screen 2:** the iron fences and grey planters are replaced by a flower box (top y 152), a square planter (y 154) and a low flower box (y 157), all above the bikes. The lamp at x 470 moved to 498.
- **Buildings on screen 6:** a stepped-gable house and a cafe, redrawn in SpriteCook at the screen-1 building's scale (the eight Artlist buildings were about 1.5x too small). The girl stands in front of the cafe. The decorative railing there now stops at the gable; the BIKES box and the top-right foreground box are gone.
- **Checks:** 15 physics checks (new: crawl under the bench, scramble onto the bin, the flower box). The autopilot plays to GOOD GIRL!
- **Skyline, pavement, building and tree** from four 4x images, saved at 1x (exact 4x pixel blocks, nothing lost).
  - **Skyline:** it replaces the grey city. It scrolls at 0.08 and is followed by its own first 128 columns, so only one City Hall tower ever shows.
  - **Pavement:** it is painted along every walkable top, with its back edge 12 px behind Pepper's walking line, then the kerb and road. The bridge pier stays greybox.
  - **Building and tree:** they replace Pepper's home box, the door box and the top-left foreground box. They stand on the pavement's back edge.
- **Title screen:** shown when the game starts, cleaned up and animated. `tools/make_title.py` builds it from `source_title/title_original.png`.
  - **Clean-up:** the painting is brought down to the game's 320x240 (each pixel takes the median colour of its cell), reduced to a 64-colour palette and despeckled.
  - **Layers:** it is cut into layers in `art/title/`, with positions in `title_data.lua`.
  - **Animation (`title.lua`):**
    - the screen fades in
    - the river's sparkles twinkle
    - both lamps glow and flicker
    - Pepper blinks her open eye, sometimes twice
    - the bird flaps, glides and drifts
    - a shine sweeps across the logo
    - PRESS ANY KEY TO START blinks
  - **On a key press:** the text blinks fast and the screen fades out to the level card.
- **New bench and pot:** revised art, same sizes, so nothing else changed.
- **Lamp posts and pot:** they stand on the back edge of the pavement by the water. Their bases are 10 px behind Pepper's walking line.
- **Railings split, preview for review (may be reverted):**
  - **Decoration by the water:** an open tube railing from SpriteCook (asset 7d30bc38). Its shades are mapped onto the lamp post's palette by `tools/make_bg_railing.py`, then faded like the lamps. No outline; Pepper cannot stand on it. It runs along the water on screens 1 to 2 and screen 6.
  - **Obstacles on screen 2:** two short sections of the iron fence on Pepper's line (x 256-344 and 448-536), chained with the two planters for dodging the bikes.
    - They are crisp and outlined, and they block her.
    - Their balusters are longer (a plain baluster row repeated), so the top at y 152 is above the bikes.
  - **Removed:** standing on the long railing, and the Down + A drop-through check (replaced by a fence check).
- **Quay railing:** new SpriteCook railing (asset 2b178488), cleaned to 8 colours by `tools/make_railing.py`.
  - **Tiling:** sections (left post and span) repeat along the railing and a closing post ends it.
  - **Obstacle style:** Pepper uses it, so it is outlined like the bench and bin and never faded. The outline goes round the whole assembled railing, so it has no seams.
  - **Position:** its posts stand on the pavement's back edge.
  - **Height:** the handrail she stands on is now y 152 (was 149), still above the bikes (they reach up to y 158). The railing runs x 256 to 672, and the bones on it moved with it.
- **Obstacles back on Pepper's line:** the bench and bin stand on Pepper's walking line again (seat top y 173, bin top y 158). Set back, they looked like things she could walk past.
- **River:** a new water sprite from SpriteCook (asset d19d28b6) replaces the old river strip.
  - **Clean-up (`tools/make_water.py`):**
    - the haze rows above the waterline are dropped
    - the deepest rows repeat to the bottom of the screen
    - 20 colours, despeckled
  - **Animation:** each row scrolls on its own.
    - The far water moves with the far shore and barely flows; the near water flows faster.
    - Every row wobbles a pixel or two.
    - The glints ride with their rows and twinkle.
- **Shadows:** soft ground shadows under Pepper, the girl, the ball and the props. Pepper's shadow stays on the floor under her and shrinks as she jumps.
- **Checkpoint lamps:** a lit lamp has a warm glow with a slight flicker, and a flash of light when it lights up.
- **Obstacle course vs decoration:**
  - Things Pepper can use (bench, bin) get the characters' 1 px dark outline.
  - Decoration (pot, lamp posts) is faded 28% towards the haze.
  - Both are done in code; the art files are untouched.
- **Checks:**
  - 13 of 13 physics checks pass.
  - The autopilot finishes the level.
  - The checks skip the title.

## v0.3 (5 Oct 2026)
- Scenery art from `riverwalk_scenery_v1`: far shore and bridge, river, bench, bin, pot, lamp post. The files are unaltered.
- **Far shore:** the 320 px strip is extended to the 800 px the layer needs. One of its arches is repeated and the bridge closes with its own left end mirrored.
- **River:** the fallable river on the quay shows the river art instead of a grey box.
- **Lamps:** a passed checkpoint lamp now glows warm (only the glass pixels are recoloured) instead of turning into a gold box.
- **Bench (gameplay):**
  - The bench is its real size (11 px seat), so it is a hop: walk into it and you stop, a hop lands on the seat.
  - The crawl lesson moves to the bridge on screen 5. The screen 1 crawl hint is gone, and the bones under the bench now sit on the seat.
- **Bin (gameplay):** the bin is its real size (17x26), so its top is 11 px lower.
- **Pot:** decoration between the bench and the bin, where the concept has it.
- **Checks:**
  - 13 of 13 physics checks pass; the bench checks now test the hop.
  - The autopilot finishes the level.

## v0.2 (5 Oct 2026)
- Pepper is drawn 1 px lower at all times, so her paws sit in the ground line and she no longer looks like she is floating. The ball in her mouth moves with her. Drawing only: collisions and jump heights are unchanged.

## v0.1 (5 Oct 2026)
- Approved baseline: greybox level, Pepper (14 cleaned SpriteCook clips), the girl (5 standing clips), the ball. All unapproved scenery art removed.

## Title: stray pixels removed (25 Oct)
- art/source/title/tools/destray.py: removes same-colour clusters of 1 or 2 px that are not in a checker or a 2/3 px lattice; lines of 3 px or more are never touched (verified: 0 changed pixels in shapes of 3+ px). Protected: the tagline, the eye, the cathedral, brick building and grey block window grids, the bird (art/source/title/regrid/destray_boxes.txt).
- Applied to the four title layers consistently (pre-clean copies in art/source/title/regrid/pre_destray/). 2,262 px changed; strays 2,238 -> 0. The logo keeps its ordered-dither fade.
- tools/stray_check.py: the same definition as a check (exit 1 on any stray), 4x map output.
