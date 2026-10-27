# Audit of prod/integrate-c (29aec89), night of 27 Oct

0 credits, no image service call. Run at 21:00 to 21:30 Stockholm.

- PEPPER UNCHANGED (4591 steps identical).
- Flow 125/125. Tiled PASS (all six levels).
- QA 0 problems: riverwalk 7897 runs, citypark_tall 12762, downtown_tall 14643, rooftops 22708, soder 11703, night 8037.
- Curve T1-T4 PASS, 10 seeds, order riverwalk,citypark_tall,downtown_tall,rooftops,soder,night.
- check_backdrop: 1 piece fails, the River Walk gable (riverwalk.lua:107, top shows at y 50 on 58 of 70 columns). Known. The fix is the gable at true scale on screen 12, picked B by the owner, not built (needs a credits yes or a stamped-parts build he has not approved).

Setup notes: `apt-get install love` errors in its man-page step but LOVE 11.5 works. `tools/check_tiled.sh` and `tools/rw_sample_frames.sh` lack the execute bit (run with bash). Python needs a venv (pip install pillow numpy scipy) because system numpy is broken.
