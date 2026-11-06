# FETCH!

A retro side-scrolling platformer about Pepper, a black Labrador girl with a pink bandana, who fetches her ball across
Stockholm and brings it back to Mia. Pixel art at 320x240 in the spirit of the 1994 Lion King game. Made for kids of
about 6 to 10, parents playing with them, and retro handheld fans. Built in [LÖVE](https://love2d.org) 11.5, first for
the Anbernic RG35XX (640x480, shown 2x).

## Play it

- **Latest build:** the newest [Release](../../releases) has `FETCH.love`. Install LÖVE 11.5 and open it
  (`love FETCH.love`), or copy it to a handheld that runs LÖVE (PortMaster).
- **From the source:** `love riverwalk` (the game folder is still called `riverwalk`, after the first level).
- **Controls:** D-pad or arrows move, A / space jump, down crawls, B sneaks, X picks up, Y barks, L/R sniff, Start
  pauses. The game shows them on its Controls page.

## The levels

Played in order, one ball story across them; lives and score carry over, a saved level select opens as you go.

| # | Level | Where | State |
| --- | --- | --- | --- |
| 1 | River Walk | the summer waterfront, kiosks, bikes, the harbour and its rowing boats | art pass in progress |
| 2 | City Park (tall) | the autumn park, the old oak, the pond, the treetop walk | art pass in progress |
| 3 | Downtown (tall) | the old town, the market, the high road over the roofs, the vintage tram | art pass in progress |
| 4 | Rooftops | | greybox |
| 5 | Söder Hill | | greybox |
| 6 | Night Harbour | | greybox |

Every level ends with a real fetch: pick up the ball and give it to Mia.

## How the game is made

- **Rules:** [`docs/BIBLE.md`](docs/BIBLE.md) (pillars, gameplay, art and UI rules, the gates). It wins over everything.
- **Where we are:** [`docs/STATUS.md`](docs/STATUS.md). **Order of work:** [`docs/WORKFLOW.md`](docs/WORKFLOW.md).
- **Art:** game pixels come from SpriteCook at game size or are built from parts on a grid; Artlist paints concepts
  (design targets) only. Every piece passes `tools/asset_qa.py`, a QA card (`tools/qa_card.py`), an independent review
  and the owner's review board before it counts as approved. Credits are logged in `art/gen/ledger.csv`.
- **Checks** (also run by GitHub Actions on every pull request and on main):

      sh tools/check_pepper.sh        # Pepper's feel is frozen: PEPPER UNCHANGED
      sh tools/check_flow.sh          # menus and a whole run, 125 checks
      sh tools/check_tiled.sh         # the Tiled maps match the level files
      python3 tools/check_backdrop.py
      SDL_AUDIODRIVER=dummy XDG_DATA_HOME=$(mktemp -d) xvfb-run -a love riverwalk --level riverwalk --physics
      python3 tools/check_curve.py --order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night --seeds 10 --out $(mktemp -d)

## Folders

| Folder | What is in it |
| --- | --- |
| `riverwalk/` | the game (Lua): `main.lua`, `stage.lua`, `scene.lua`, `flow.lua`, levels in `level/`, art in `art/` |
| `maps/` | Tiled maps of the levels |
| `art/` | sources (`art/source/*.aseprite`), palettes, generation jobs, concepts, the credit ledger |
| `tools/` | build scripts for built art, checks, QA cards, the asset pipeline |
| `docs/` | rules, status, beat sheets, layer ladder, review frames (`docs/review/<date>/`) |

## Branches

`main` is the release; every push to it builds a Release. Work happens on short branches (`art/*`, `night/*`,
`ui/*`) that are merged into a `prod/integrate-*` branch, checked, and then into main with the owner's yes. Merged
branches are deleted; `docs/branches_archive.md` lists each deleted branch and its last commit so any can be restored.

The October history of this README is in `docs/README_history_oct.md`.
