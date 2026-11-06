# River Walk ground joins (art/rw-ground-06nov, 6 Nov, 0 credits)

The owner: "these connections of asphalt really look weird, this is still the first level even". Every terrain join in River Walk (map `level/riverwalk.map`, 8 px cells), before and after, 3x, colour and grey (`*_grey.png`). Camera x in brackets; Pepper at camera + 140.

| Join | x | Frames (cam) | What changed |
| --- | --- | --- | --- |
| Road end, ramp down to the quay | 1280-1312 | ramp_down_road_end_x1280 (1120) | kerb turns the corner; ramp is one 45 degree band with a coping stone; wall courses line up with the quay; railing end post on the flat (x 1280) |
| Quay end at the river | 1392 | quay_end_river_x1392 (1240) | coping to the water's edge, quoined corner |
| Far quay starts | 1808 | quay_start_x1808 (1700) | same, mirrored |
| Bridge passage | 1936-2072 | bridge_passage_x1936 (1860) | stone arch under the pier art, shaded vault, flat shadow bands ending at the jambs |
| Far quay end at the harbour | 2192 | quay_end_harbour_x2192 (2040) | coping and quoins |
| Quay after the harbour | 2640 | quay_start_x2640 (2500) | coping and quoins |
| Ramp up, road starts | 2792-2824 | ramp_up_road_start_x2824 (2660) | ramp band and coping, kerb corner |
| Railing start | 2880 | railing_start_x2880 (2760) | unchanged: the approved left post is there |
| Front band | everywhere on the road | front_hedge_a (0), front_hedge_b (320) | clipped hedges with round ends instead of grass spikes and bollard pegs |

Level start (x 0) and end (x 3840) are the level's edges (the house and the cafe); the camera never passes them.

Road: road.png (tools/make_road.py) flat asphalt, 64 px dashes on a 160 px pitch, 32 flecks on a grid. asset_qa: WARN, 32 "blotches" of 2 px: the flecks, on purpose.
Approved art untouched: pavement.png, pier.png, rail_bg_*. Pepper unchanged.
