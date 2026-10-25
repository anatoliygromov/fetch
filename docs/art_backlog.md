# FETCH! art backlog (from the board, 25 Oct 2026)

The owner's review of the 42 board items (25 Oct, 13:29-13:35): 1 approve, 12 fix, 28 redraw, 1 open (town_statue).
The work is done family by family through `docs/WORKFLOW.md`. Order: River Walk (sample screen first), City Park,
Downtown. Nothing here is started without its spend line; fixes cost 0 credits.

## What the owner said
- **The free clean pass made art worse.** Building and gable: "details are smothered"; cafe: "you are taking away the
  details, the after is not better, the metal fence on the windows has holes". Automated blotch and dirt cleaning on
  existing art is out (BIBLE section 3). Existing art is fixed by hand in Aseprite or redrawn.
- **Scale in the scene.** Tram shed and shelter: "look at the size in the scene, it's super small". Every redraw is
  sized from real metres against Pepper (46 px a metre) and checked in an in-game frame.
- **Approved:** one haze per layer (already on main).
- **Taller than the viewport** (same day): back buildings and front-row trees run past the top of the screen.

## River Walk (level 1, first)
| Family | Tier, method | Pieces | Board call |
| --- | --- | --- | --- |
| RW street backdrop (sample screen) | C, built from stamped parts at true scale, taller than the viewport | house (building), gable, cafe, background railing (rail_bg_unit) | redraw |
| RW front trees (sample screen) | B, SpriteCook, crowns cut by the top edge | tree, tree_near | rule, 25 Oct |
| RW road traffic | A, SpriteCook at the near-lane scale, cleaned and polished by hand | road_car1, road_car4, road_cyclist1, road_cyclist1_roll, road_cyclist2, road_cyclist2_roll (+ the adult promenade cyclist) | redraw |
| RW water | A (ferry, rowboat), C (pile) | ferry, rowboat, pile | redraw |
| RW fixes, 0 credits, by hand | fix in Aseprite, no scripts | cloud8 (darkest shade), pier (decoration drawn with an outline), park_log (lone pixels), skyline (blotches, pinholes), gull (lone pixels, frame size jumps) | fix |

## City Park (level 2)
| Family | Tier, method | Pieces | Board call |
| --- | --- | --- | --- |
| CP park props | B, SpriteCook; gate built | park_gate, park_hedge, park_leaves_flat | redraw |
| CP fixes, by hand | fix in Aseprite | park_keeper_cart (dirt pixels), park_keeper_winch (a colour lost in one frame) | fix |

## Downtown (level 3)
| Family | Tier, method | Pieces | Board call |
| --- | --- | --- | --- |
| DT street backdrop | C, built from stamped parts at true scale, taller than the viewport | town_facades, town_house3, town_door, town_roofs | redraw |
| DT street props | A/B, SpriteCook at true scale | town_kiosk, town_parasol, town_pedestal, town_stall, town_shelter, town_tramshed70, town_tramshed96, town_bollard | redraw |
| DT fixes, by hand | fix in Aseprite | town_house1, town_house2 (decoration drawn with an outline, contrast), town_awning64, town_awning80, town_table_front | fix |
| Open | owner's call | town_statue | not decided |

## Order
1. River Walk sample screen: street backdrop + front trees (STATUS), cap 300 credits.
2. River Walk fixes (0 credits) and road traffic, then water.
3. City Park, then Downtown, each starting with its layer plan, palette and sample screen.
