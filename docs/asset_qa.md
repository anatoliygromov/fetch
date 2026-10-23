# Asset QA: the gates every asset passes (23 Oct 2026)

The owner's bar: the Lion King look, very crisp. No asset reaches him, and no SpriteCook credit is spent on a final,
until it has passed the gates below. Read `claude/art-learnings.md` (project doc) and `docs/layer_ladder.md` first.

## The gates

| Gate | What | Credits | Who passes it |
| --- | --- | --- | --- |
| 0 Brief | One card per asset: layer, slot size (px), scale (46 px/m on Pepper's line), palette ramps, outline rule, view (front-on), its repeated parts (windows, wheels, posts), the approved pieces it must match. | 0 | the owner approves briefs in batches |
| 1 Pilot | One piece of each kind goes through gates 2 to 6 before the rest of its batch is generated. A failed pilot changes the brief, not the batch. | the pilot only | gate 4 to 6 |
| 2 Make | Small pieces drawn at game size (Pixel Engine); bigger ones on their own pixel grid. Buildings are BUILT: each repeated part drawn once and stamped on an integer grid. Never resample by a non-integer factor. | after gate 0 | the maker |
| 3 Clean | `tools/stamp_windows.py` (buildings: one clean window stamped on the storey grid), `tools/blotch_clean.py` (blotches), `tools/cleanpass.py` (stray pixels), `tools/outline_complete.py` (outline gaps), palette locked across frames. `tools/freefix.py` is the recipe per asset of the 23 Oct pass. | 0 | the maker |
| 4 Checks | `python3 -I tools/asset_qa.py --file X.png --layer L --level rw\|cp\|dt [--fade F] [--building] [--frames WxH]`. Any FAIL: back to gate 3, or to gate 2 if the drawing is wrong. | 0 | the script |
| 5 Card | `tools/qa_card.py`: the asset as drawn at 1x and 2x, the file at 5x with every flagged pixel boxed, the approved bench, bin and lamp beside it, the windows lined up, the frames at 5x and a GIF; plus an in-game frame in colour and greyscale (`tools/fix_shots.sh` with `LOOK_SPOTS`). | 0 | the maker |
| 6 Review | An agent that did not make the asset goes through the card with the checklist below and lists every defect with its pixel position, or "none" per item. Defects go back to gate 3. | 0 | a fresh agent |
| 7 Owner | The owner sees the card. Only an approved asset goes on a branch for `round1`. | 0 | the owner |

## The checks (tools/asset_qa.py)

Measured on the file and as the game draws it (load-time fade from scene.lua, setpieces.lua, arthooks.lua; the look
shader from look.lua; shared art under every level's look). Calibrated on 23 Oct: the approved bench, bin, lamp,
both kiosks, planter and flower box pass; the owner's examples (plaza house windows, the winch keeper's outline,
batch 1's plaster) fail.

| Check | Fails when |
| --- | --- |
| alpha | any semi-transparent pixel |
| slot | the size differs from its hook (docs/art_hooks_r8.md) |
| noise | over 1 % single pixels a shade off the fill around them (props, buildings) |
| stray | over 5 % lone pixels (2 % for buildings) |
| blotches | 2-24 px patches of a near colour inside a fill over 0.3 % of the art (dirty plaster) |
| specks | free-floating bits of 1-8 px |
| pinholes | 1-4 px holes in a fill (outlined gaps between slats are allowed) |
| outline | a play piece or character with a broken 1 px dark outline; decoration drawn with a broken outline |
| colours | more colours than the layer allows |
| ladder | darker than the layer's darkest on screen, in any level it is drawn in |
| windows | buildings: windows of one storey and wall not pixel-identical (a 1 px shift counts), panes unequal, off one grid, or speckled (a 2 x 2 window is fine since art/freefix) |
| frames | sheets: not whole frames; a colour in one frame only (flicker); warnings for a colour lost in one frame, feet moving, size jumps |

## The review checklist (gate 6): what the script cannot judge

Go through the card at 5x, item by item, and write a defect with its position or "none":
1. Every repeated part the same: windows across storeys and across neighbouring houses, wheels, spokes, posts, balusters, wall ties, roof tiles.
2. Wheels round and spokes even; symmetric parts symmetric.
3. One light direction across the piece; shading in ramps, no random dark or light dabs.
4. Outline 1 px everywhere, one ink colour; no doubled or 2 px stretches.
5. Faces: both eyes (where seen), nose, mouth in every frame; hands and feet whole; nothing "boils" between frames.
6. Scale against Pepper (46 px a metre): doors, steps, people; the slot and anchor in docs/art_hooks_r8.md.
7. Mirrored as the game draws it (the keepers are drawn flipped): still reads right.
8. In game: only the part that shows (tall fronts: the lower 136-176 px); the lit lamp; tinted water (City Park's pond).
9. Next to the approved bench, bin and lamp: as crisp, as clean, the same pixel size.

## Credits

`docs/art_ledger.md` records each asset's gate, credits spent and status. Credits are spent only from gate 2, only
for a brief the owner approved, and only for a pilot until it passes. Defects found later are fixed at gate 3 (0
credits); a regeneration needs a reason written in the ledger (the drawing itself is wrong).

## Commands

    python3 -I tools/asset_qa.py --all --json out/qa.json          # the whole library (+ batch 1 from r8/art)
    python3 -I tools/qa_card.py out/qa.json out/cards [names]       # cards (FAIL_/WARN_/PASS_<name>.png, GIFs)
    python3 -I tools/qa_triage.py out/qa.json docs/asset_qa_triage.md
    python3 -I tools/asset_qa.py --file new.png --layer play --level dt --building    # one new file

Needs python3 with numpy and Pillow (no scipy). The library run takes about 15 s.
