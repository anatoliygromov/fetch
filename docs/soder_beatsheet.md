# Level 4: Söder Hill (beat sheet)

The fourth level, and the first one that changes the manner of play: a chase down a steep Söder street, our
version of Lion King's Stampede. The screen moves on by itself, the ball rolls ahead of Pepper down the hill, and
she has to keep up: hop, jump and crawl without stopping to think. Everything she does here she learned in levels
1 to 3; what is new is the pressure.

- **Size:** 16 screens, 5120 px (640 x 30 cells of 8 px). The street steps down the hill from feet y 112 at the top
  to the quay at y 208, 16 px at a time, on six short flights of stairs (x 400, 1176, 1936, 2616, 3216, 3896).
  Terrain: `level/soder.map`, written by `tools/make_soder.py`. Everything else: `level/soder.lua`.
- **Time limit:** 200 s. **Par:** 118 s (autopilot 73.3 s x 1.6).
- **Story (level 4 of 5):** River Walk's outro: "UP ON SODER MIA DROPPED / THE BALL. IT ROLLED AWAY...". The ball
  rolls all the way down the hill and stops against the quay railing; Mia comes down the stairs; Pepper picks the
  ball up and gives it to her. Outro (into Level 5): "IT GOT DARK ON THE WAY / HOME. A FOX TOOK THE BALL!".
- **Moves used:** run, tap hop, held jump, crawl, scramble, one-way tops, pick up, give. No bark: nobody to bark at.

## The mechanic (`riverwalk/chase.lua`, `L.scroll`)

| Piece | Rule |
| --- | --- |
| The scroll | The camera's left edge moves right by itself at the speed of the section it is in (`L.scroll.speeds`): 50 px/s at the top, 62, 70, 78 in the middle, 70 and 60 near the quay. Pepper runs at 120, so she can always get ahead. The camera rides with the scroll, at most 24 px ahead. It stops at the level's end. |
| The left edge | Pushes Pepper along. If something she didn't jump or crawl under is in the way, she is pinned: a heart, and back to the last lamp ("OUCH! JUMP OR CRAWL, PEPPER!"). "KEEP UP, PEPPER!" when she falls back to the left 56 px (every 6 s at most). |
| The right side | While the ball rolls, Pepper can't run (on the ground) further than 240 px into the screen; past it she drifts back. A jump still flies at her full speed. So the chase sets the pace, and she always sees 60 px or more of what is coming. |
| Hatches | Open cellar hatches are gaps in the street (24 to 40 px). Falling in costs a heart, back to the lamp ("OOPS! AN OPEN HATCH"). Drawn as dark holes with the lid standing open beside them. |
| The ball | Rolls ahead of her, always on screen (200 to 312 px from the left edge) and always ahead of her nose. It hops onto whatever stands in the street, rolls under signs and skims across hatches. At x 5088 it stops against the railing and lies there to be picked up (normal ball from then on). |
| Barrels | Two stacks of barrels on terraces. When the ball rolls past, it knocks one barrel loose (a "spring" sound, it pops up first): it rolls down the stairs at 30 px/s, slower than the chase, so Pepper catches up with it and has to jump it (a held jump; a tap hop is too short). Touching it costs a heart (knock-back, no respawn). A barrel that falls into a hatch is gone. |
| Respawn | Starts the chase again from the lamp: the ball back on screen, the barrels still ahead back on their stacks. |
| Hard mode | 1 heart, same chase. |

## Screens

| # | Screen (x) | Street y | Pepper does | Set pieces (size) | Hazards | Bones | Lamp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | The top (0-320) | 112 | The ball rolls away at once. Run; tap A over a crate. | CRATE 32x16 | the edge | 2 | |
| 2 | First stairs (320-640) | 112 > 128 | Hold A: a held jump onto a tall crate stack (32 px). | CRATES 32x32 | the edge | 3 | |
| 3 | The cafe sign (640-960) | 128 | Crawl under a hanging sign (19 px gap). Crate steps up to a balcony (high route, gold bone, secret CAFE BALCONY). | SIGN 32x37 + bracket, crate 32x16, CRATES 32x32, BALCONY one-way 64 wide (y 70) | the edge | 5 (1 gold) | |
| 4 | First hatch (960-1280) | 128 > 144 | A tap hop over a 32 px hatch; down the stairs. | hatch 1040-1072 | hatch | 3 | x 1240 |
| 5 | Parked bikes (1280-1600) | 144 | Hop the bikes (20 px); crawl under a low awning. | BIKES 40x20, AWNING 32x39 + arm | the edge | 3 | |
| 6 | The terrace (1600-1920) | 144 | A held jump over a hatch straight onto the terrace (24 px up). The ball knocks a barrel off the stack on it. | hatch 1824-1856, TERRACE 56x24, barrel stack (4 barrels, 14x14) | hatch, barrel | 2 | |
| 7 | Barrel street (1920-2240) | 144 > 160 | Catch up with the barrel and jump it; crawl under a sign. | SIGN 32x37 + bracket | barrel, the edge | 3 | |
| 8 | Two hatches (2240-2560) | 160 | Hop, land, hop (24 and 32 px). | hatches 2320-2344, 2424-2456 | hatches | 3 | x 2580 |
| 9 | Cafe tables (2560-2880) | 160 > 176 | Hop onto the tables (19 px; crawling under both is too slow for the chase) or jump up to the parasols (high road, 2 bones). | 2 TABLES 48x7 (top y 150), 2 PARASOLS one-way 64 wide (y 108), poles | the edge | 4 | |
| 10 | The fruit cart (2880-3200) | 176 | A held jump onto the cart (40 px), a jump over a 40 px hatch, a jump onto the second terrace: the second barrel. | CART 40x40, hatch 3040-3080, TERRACE 56x24, barrel stack | hatch, barrel | 2 | |
| 11 | The arch (3200-3520) | 176 > 192 | Down the stairs, jump the barrel, crawl through a low arch (19 px). | ARCH 32x61 | barrel, the edge | 2 | |
| 12 | High street (3520-3840) | 192 | Crate steps up, a held jump onto a long balcony over two hatches (gold bone, secret HIGH STREET), or stay low and hop both hatches. | crate 32x16, CRATES 32x32, BALCONY one-way 180 wide (y 120), hatches 3600-3632, 3720-3752 | hatches | 6 (1 gold) | |
| 13 | Down to the quay (3840-4160) | 192 > 208 | The last stairs, hop a crate. | CRATE 32x16 | the edge | 1 | x 3860 |
| 14 | The quay (4160-4480) | 208 | Crawl under a sign, hop two bollards (14 px). | SIGN 32x37 + bracket, 2 bollards 12x14 | the edge | 3 | |
| 15 | Crate stack (4480-4800) | 208 | Hop up and over (16 + 16 px). | crate 32x16, CRATES 32x32 | the edge | 2 | |
| 16 | The end (4800-5120) | 208 | The ball stops against the railing; the scroll stops. Pick it up (X), carry it back to Mia at the foot of the stairs (x 5000), give it (X): GOOD GIRL! | STAIRS (decor), RAILING 24x36 | none | 1 | |

Total: 45 bones, 2 of them gold (the cafe balcony, the high street balcony). 3 lamps. 2 secrets.

Measured (`--auto`): AUTOPILOT GOOD GIRL!: bones 41/45, secrets 1/2, lives 3 hearts 3, 73.3 s played. The same in
hard mode (1 heart, no hit). Compare: City Park 31.4 s, Downtown 29.8 s, River Walk 35.1 s.

## Art needed later (greybox now; sizes in level pixels)

| Piece | Size | Notes |
| --- | --- | --- |
| Söder street background | 320 px wide tile, up to y 172 | steep old houses (ochre, red, yellow plaster), roofs stepping down to the right; the hill should read as a slope |
| Street ground | 8 px cells | cobbles, with the 16 px stair flights (two 45° cells) as stone steps |
| Open cellar hatch | 24-40 px wide hole, lid 2x14 standing open | dark hole with a wooden lid, iron hinges |
| Barrel | 14 x 14, rolling: 4 frames | oak staves and two hoops; a stack of 4 (3 + 1) |
| Terrace | 56 x 24 | a wooden cafe deck with a rail |
| Crate / crates | 32 x 16, 32 x 32 | reuse the town crates |
| Hanging sign + bracket | 32 x 37, bracket 48 x 4 | a cafe sign (coffee cup), 19 px gap under it |
| Low awning + arm | 32 x 39, arm 4 x 26 | a striped awning |
| Parked bikes | 40 x 20 | two bikes leaning together |
| Cafe table + parasol | table 48 x 7 on a pole, parasol 64 x 4 top | reuse Downtown's if spotless |
| Fruit cart | 40 x 40 | wooden cart with fruit crates |
| Low arch | 32 x 61 | a stone passage arch (Söder's "gränd") |
| Balconies | 64 x 4, 180 x 4 | wrought-iron balconies, one-way tops |
| Bollards | 12 x 14 | iron quay bollards |
| Stairs (Mia's) | 80 x 86 | the stone stairs down to the quay |
| Quay railing | 24 x 36 | iron railing; water beyond it |
