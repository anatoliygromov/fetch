# Art needed after the r5/bugs sweep (22 Oct)

Scale rule (owner): scale everything to the dog. Pepper's back 27 px, head 38 px; Mia 59 px (about 46 px a metre).
All new art at 1x game pixels (no upscaled sprites), side or front view at about Pepper's eye height, obstacles crisp
with a 1 px dark outline, decoration faded with no outline. See `scale_lineup.png` for the current sizes.

| Priority | Asset | Problem now | Target size (game px) | Notes |
|---|---|---|---|---|
| 1 | `town_tram.png` (Downtown tram) | 105 x 34: as tall as Pepper, a toy | about 300 x 150 (two-car Stockholm tram, about 3.3 m tall) | Needs a level change too: Pepper dodges it on the shelter and shed roofs (41-48 px). Options: the tram runs in a lane behind Pepper's line with a crossing to time, or the hazard becomes a tram arriving at a raised platform. Hit box and `w`, `h` in `level/downtown.lua` follow |
| 1 | `town_tramshed70.png`, `town_tramshed96.png` | 41 px tall, smaller than Mia | at least 170 px tall to swallow the new tram | Goes with the tram |
| 1 | `town_shelter.png` (tram stop) | 72 x 48: shorter than Mia | about 120 x 105 (2.3 m) | Its roof is a perch at 48 px today; at scale it is out of jump reach, so it becomes decoration or gets a step |
| 2 | `park_keeper_cart.png` (leaf cart keeper, 8 frames of 82 x 82) | the man is 61 px, Mia's height | man about 80-84 px; frames about 104 x 104; the wheelbarrow about 34 px to the handles | Hit box stays the cart (48 x 26) so the picnic-table perch still works |
| 2 | `park_keeper_winch.png` (the winch man, 8 frames of 80 x 80) | 57 px, shorter than Mia | man about 80-84 px; frames about 100 x 100 | Decoration (faded), no hit box |
| 3 | `town_door.png` and `town_house1-3.png` | door 58 px, houses 118-126 px with Pepper-sized doors | door about 95 px; a house front at least 300 px, or keep the small houses but stand them clearly further back (higher base, more haze) | Decoration; first choice is the cheaper "further back" |
| 3 | `park_boat.png`, `park_boat_front.png` (duck boat) | 54 x 33: smaller than Pepper's length | about 110 x 60 (a swan pedal boat) | The deck must stay at the mover's top (Pepper rides it); the hull can grow downwards and the neck upwards |
| 4 | a treetop lantern (new) | the high road's checkpoints are full street lamps standing in the canopies | about 12 x 30, hanging from or standing on a branch, lit and unlit | Tall City Park only (`lamps` on ledges above the path) |
| 4 | `road_car1-5.png` near-lane cars (optional) | cut at the bottom of the screen by design (wheels below y 240) | only if the owner wants whole cars: the road band is 41 px, so this needs a lower camera or a taller road band, not just art | Owner decision first |
| 5 | `road_cyclist1-2.png` (optional) | now also the promenade bikes (73 x 75, rider 1.27x Mia); the owner's guide asks 1.6-1.8x Mia | promenade rider about 85-95 px if the owner wants bigger; wheels stay about 29-32 px | The current art is a correct 1x interim; a near-lane variant could be a little bigger than the promenade one |
| 5 | `cyclist1.png`, `cyclist2.png` (+ `_roll`) | no longer used in play (the old child-sized promenade bikes) | none | Can be retired from the art set |
