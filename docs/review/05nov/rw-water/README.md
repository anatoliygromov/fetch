# River Walk water family, 5 Nov 2026 (branch art/rw-water-05nov)

Owner's board calls (25 Oct): ferry redraw, pile redraw. The rowing boat is not here (animals round 2 waits on the board).

| Asset | Game file | Size | How | Credits |
| --- | --- | --- | --- | --- |
| rw_ferry (tier A, play) | riverwalk/art/scene/ferry.png | 252 x 79 (was 252 x 93) | SpriteCook NB 2.1 1K pixel, render rw_ferry_n5a, then `tools/build_ferry.py` | 24 (1 job, 2 variants) |
| rw_pile (tier C, front) | riverwalk/art/scene/pile.png | 18 x 182 | built by rule, `tools/build_pile.py` | 0 |

## The boat's size (a design call for the owner)
Pepper's route on screen 6 is fixed: deck y 206 (x 1562-1797), cabin roof y 184 (x 1620-1740, a hop up), wheelhouse
roof y 154 (x 1657-1705, a held jump). At 46 px/m that is a 5.1 m boat with a cabin 0.48 m above the deck: the old art
drew a commuter ferry (a 20-25 m ship) on it, so it read as a toy. The new art is a small Stockholm harbour water taxi
(a motor launch) at true size on exactly those lines, so the scale is right and nothing in the level moves. The level's
story words still say "ferry"; the intro says "THE BALL IS ON A BOAT!".

## The ferry's method
Blockout `art/gen/blockouts/rw_ferry.py` (256 frame, Pepper at 1x, the boat's parts on the route's lines). Variant a
followed the layout within 2-7 px; variant b drew a bigger boat (296 px) and was not used. After `build_traffic.py cut`
(palette snap) the cut was mottled (red specks in the wood, grey in the white), its foredeck was a strip of deck planks
seen from above (no tops), the bow stood 5 px above her deck box and the wheelhouse roof 5 px under hers. So
`tools/build_ferry.py` draws every flat part by rule in the cut's own colours on the route's exact lines: hull with a
raked stem and rounded transom, strake, white topsides lit at the bow and shaded at the stern, boot line, red bottom;
cabin with roof cap, roof shadow, two plank seams; four portholes stamped from the cleanest one of the cut (identical,
22 px apart); lifebuoy, windows, fenders and flag drawn by rule. The edits list is every pixel that differs from the
cut placed where the game draws it (8383 of 10342 opaque pixels: the method is a rebuild on the render's design). One 1 px ink
outline all round; no railings (the board's holes and clutter).

## Checks
asset_qa ferry PASS (15 colours, outline 100 %, lone 0.1 %), pile PASS (8 colours). PEPPER UNCHANGED, flow 125/125,
River Walk --physics 55 PASS (ferry deck to saloon roof, saloon roof to wheelhouse roof, pontoon), check_backdrop:
only the known gable (unchanged from the base). .aseprite sources round-trip pixel for pixel.

## For the reviewer
1. Is the boat too plain beside the bench and bin? The white hull is a flat fill with a highlight row, a two-row shade
   band and lit/shaded ends; the cabin wood is flat with two seams.
2. The lifebuoy is 13 px, drawn by rule with 8 bands: check it reads as a lifebuoy at 1x.
3. The flag (x 241-251) and staff stand past the deck box (x 237): decoration on the boat, Pepper never stands there.
4. The wheelhouse roof cap is x 97-145 (box 97-145), body x 99-143; the cabin roof x 60-180 (box 60-180).
5. The red bottom (y 225-231) shows below the waterline (y 224): the river is drawn behind the boat, as before.
6. The pile: only its top 15-19 px are ever on screen (rim, top of the timber, the rope lashing).

Frames: `ingame_*_1x.png` (after), `before_*_1x.png`. Board images: `board/`. Cards: `cards/`.
