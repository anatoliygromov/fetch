Reviewer: independent gate-8 art reviewer (Claude, did not make these assets), round 1, 6 Nov 2026

Frames (my own, downtown_tall, LOOK_SPOTS y 424, LOOK_TRAM=2349, LOOK_CARGO): art/gen/reviews/dt_traffic_frames/ (street_cargo_3x, tram_street_3x, tram_back_end_3x, tram_end_game6x, cargo_5x beside bench/bin/lamp, pedal_legs5x, wheel8x). asset_qa and check_backdrop run: tram PASS, wheel PASS, cargo WARN (stray 3.0 %), pedal PASS, backdrop OK.

# tram_vintage.png (570x188, back lane, fade 40 %)

Scale: 570 px = 12.4 m, clerestory 152 px = 3.3 m, wheels 31 px = 0.67 m at 46 px/m. Real vintage Stockholm car about 12 m long and 3.3 m high: matches. Owner question: it is 188 px tall (78 % of the screen) and 1.8 screens long, and it hides the street's house fronts behind it for 570 px. It is taller than the 3 storey house in the mid layer behind it (frame tram_street_3x) because the layers differ in scale. Door at 60 px sits on the stop sign (checked, correct).

1. Scale: PASS (owner question, numbers above).
2. Layer: FAIL. The cream band and window frames (#f1e3c1 and #fcf3d8, 10 % of the art) are on screen luma 212 (233,210,169). The houses behind it are 145-151 (frame tram_street_3x, red house 145, tan 151), the ladder's mid median 170, far city 175. 6,359 px of the 320x240 frame are above luma 195, nearly all tram. In the greyscale card frame the tram band is the whitest thing on screen, brighter than the sky. The nearer layer must be darker than what is behind it. Windows 137 and body 158 are fine. Fix by darkening the cream (about #c9b88f raw) or raising the fade only for it.
3. Outline: PASS (none; edges are darker own shades; outline 4 %).
4. Shapes: PASS. Windows pixel-identical, even pitch, straight lines, roof and bogies straight. Pantograph arm is a clean 1 px stair line.
5. Shading: PASS. Flat fills, 19 colours, lone 0.0 %, no blotches.
6. Palette: PASS (darks are blue-leaning, accepted for a painted tram).
7. View: PASS (side view, thin roof cap).
8. Fit: PASS (as crisp as the lamp at 3x).
9. Read: PASS (a tram with a little driver, door and windows).
Note, not a fail: at its stop the tram's back end (world x 2634) ends 6 px short of the red canal-side house (x 2640). The end wall is in plain view with a 6 px sliver of sky and far houses between (tram_end_game6x.png, screen x 173-180 at camera 2460). It does not pass behind the houses at the stop; it only passes behind them on arrival from the right. Looks like a tangent. Move the stop 12 px or more left to hide it, or leave it. The open space under the body shows the street behind the bogies, fine at 40 % fade.

VERDICT: FAIL (1 item: Layer)

# tram_vintage_wheel.png (4 x 31x31)

Wheel 31 px = 0.67 m. Eight spokes, 11.25 degrees a frame, loop closes at 45 degrees. 5 colours, lone 0.0 %, on screen p10 123 and 150 rim. Sits centred on the bogie bars (checked in game).

1-9: all PASS. Outline none (decoration), shapes round, even steps, view side-on, reads as a wheel at 1x.

VERDICT: PASS

# cargo_bike.png (116x88, play line, obstacle)

Scale: rider with helmet 85 px = 1.85 m, bike 116 px = 2.5 m, wheels 30 px = 0.65 m. Same rider as the River Walk bikes. Hit box 80x26 covers the front wheel and the box (box rows 61-87). Pepper 60x52 beside it at 1x and 4x: reads right.

1. Scale: PASS.
2. Layer: PASS (play, outline, luma 2 to 205, 22 colours against 24).
3. Outline: PASS (unbroken #020202, same as Pepper and the bench; asset_qa outline 99 %).
4. Shapes: PASS. Wheels round, spokes straight. Stray 3.0 % are the spokes and the helmet's stair edge, under the 5 % rule.
5. Shading: PASS. Box planks and loaves in clean ramps, no blotches. Trousers show light streaks (mild).
6. Palette: PASS.
7. View: PASS (side view, rider faces left, travel direction right to left).
8. Fit: PASS at 1x and 3x beside bench, bin, lamp.
9. Read: PASS (baker with baguettes, cute).

VERDICT: PASS

# cargo_bike_pedal.png (8 x 116x88)

Frames differ only in legs, wheels and pedal area (x 5-110). 
1. Scale: PASS. 2. Layer: PASS. 3. Outline: PASS. 
4. Shapes: PASS (leg positions are plausible, no loose parts).
5. Shading: FAIL. Trousers are two mottled greys with a flat black far leg that merges with the steering stem: frame 3 file (x 232+..., i.e. frame x 68-82, y 46-70), frame 4 (x 68-80, y 46-72), frame 5 and 7 (x 66-80, y 48-70). The near leg changes thickness frame to frame (frame 7 thigh about 14 px wide against 9 px in frame 1). The still's trousers are cleaner than frames 3-7. The maker lists this as known.
6. Palette: PASS. 7. View: PASS.
8. Fit: FAIL. At 3x the legs are the least crisp part of the bike beside the bench and lamp (pedal_legs5x.png).
9. Read: PASS.

VERDICT: FAIL (2 items: Shading, Fit). Redraw the far leg as one dark ramp and the near leg at one width, then re-run.
