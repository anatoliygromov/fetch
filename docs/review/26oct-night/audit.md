# Audit of prod/integrate (c1c37a4), night of 26 Oct

0 credits, no code or art changed. Run at 20:40-20:55 Stockholm, LÖVE 11.5.

| Check | Result |
|---|---|
| tools/check_pepper.sh | PEPPER UNCHANGED, 4591 steps identical |
| tools/check_flow.sh | 125 of 125 passed |
| tools/check_tiled.sh | PASSED (run with bash; the file is not executable) |
| --qa, all six levels | 0 problems each |
| tools/check_curve.py, 10 seeds, approved order | T1 to T4 PASS; lost runs 0.0, 3.8, 1.2, 2.5, 0.0, 0.0 % |
| tools/check_backdrop.py | FAIL, 3 pieces: riverwalk.lua:54 building (top y 39), :55 tree (47), :70 tree_near (39) |

The backdrop fail is known. `art/rw-sample-screen` (80ec97f) replaces these pieces and is waiting for the merge decision.

Notes
- `tools/check_tiled.sh` has no execute bit. `bash tools/check_tiled.sh` works.
- apt python3-numpy breaks next to /usr/local python here; a venv with pip works.
