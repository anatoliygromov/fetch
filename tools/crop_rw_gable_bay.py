"""Screen 12, river view option B (owner pick, 26 Oct): the gable shows only its door bay.
5 Nov: rw_gable_bay.png is now BUILT as its own narrow front by tools/build_rw_gable.py (build_bay): the door bay of
the gable's grid (x 68-148) with its own corner lesene, and no cut window column or half wall anchor at its left edge
(the old pixel crop showed half an anchor and the stubs of the window's sills and hood). This script only calls it.
Usage: crop_rw_gable_bay.py   (run from the repo root)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_rw_gable import build_bay

build_bay().save('riverwalk/art/scene/rw_gable_bay.png')
