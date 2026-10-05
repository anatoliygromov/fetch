# Changelog

Each delivered build is a git tag. `git checkout v0.1` goes back to any of them.

## Trial branch `try/scenery-v2` (not merged)
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
