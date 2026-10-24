"""Shared helpers for the title regrid pipeline."""
import numpy as np
from PIL import Image
import os

SRC = os.environ.get('REGRID_SRC', '/home/claude/fetch/source_title/title_original.png')
NX, NY = 320, 240
CACHE = os.environ.get('REGRID_CACHE', '/tmp/claude-0/rg/cache')
os.makedirs(CACHE, exist_ok=True)


def load_src():
    return np.array(Image.open(SRC).convert('RGB'))


def srgb_to_lab(rgb):
    """rgb uint8 or float 0..255 (...,3) -> CIE Lab (...,3) float32."""
    c = np.asarray(rgb, np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], np.float32)
    xyz = c @ M.T
    xyz /= np.array([0.95047, 1.0, 1.08883], np.float32)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1).astype(np.float32)


def luma(rgb):
    return np.asarray(rgb, np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)


def save(arr, path, scale=1):
    im = Image.fromarray(np.asarray(arr, np.uint8))
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
