"""Screen 12, river view option B (owner pick, 26 Oct): the gable shows only its door bay.
rw_gable_bay.png = the right 80 px of rw_gable.png (x 68-148), a pixel-exact crop, nothing redrawn or resampled.
Usage: crop_rw_gable_bay.py   (run from the repo root)"""
from PIL import Image

X0, X1 = 68, 148
im = Image.open('riverwalk/art/scene/rw_gable.png').convert('RGBA')
im.crop((X0, 0, X1, im.height)).save('riverwalk/art/scene/rw_gable_bay.png')
