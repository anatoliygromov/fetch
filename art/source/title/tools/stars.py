"""90s twinkle stars for the logo (Sega / SNES style), drawn pixel by pixel: 3 sizes, 6 frames each
(grow, grow, flash, shrink, shrink, gone-to-a-dot), a white core and pale yellow arm tips, no outline (they sit on
the letters' upper edges, half on the dark navy outline, where white reads). Sheet: rows = sizes (small, medium,
large), 6 cells of 11 x 11 each, the star centred in its cell (centre at 5, 5)."""
import numpy as np
WHITE, PALE = (255, 255, 255), (255, 246, 176)
C = 11

def star(r, flash=False):
    a = np.zeros((C, C, 4), np.uint8); c = C // 2
    def px(x, y, col): a[c + y, c + x] = (*col, 255)
    px(0, 0, WHITE)
    for k in range(1, r + 1):                       # four arms, 1 px wide, white near the core, pale at the tips
        col = WHITE if k <= max(1, r // 2) else PALE
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): px(dx, dy, col)
    if r >= 3:                                      # a plus-shaped core for the bigger stars
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)): px(dx, dy, PALE)
    if flash:                                       # the flash: short diagonal rays
        d = max(1, (r + 1) // 2)
        for k in range(1, d + 1):
            for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                if not (r >= 3 and k == 1): px(sx * (k + (1 if r >= 3 else 0)), sy * (k + (1 if r >= 3 else 0)), PALE)
    return a

FRAMES = {0: [(0, 0), (1, 0), (2, 0), (2, 1), (1, 0), (0, 0)],     # small:  dot, 1, 2, flash, 1, dot
          1: [(1, 0), (2, 0), (3, 0), (3, 1), (2, 0), (1, 0)],     # medium
          2: [(1, 0), (2, 0), (4, 0), (5, 1), (3, 0), (1, 0)]}     # large

def sheet():
    s = np.zeros((C * 3, C * 6, 4), np.uint8)
    for size, fr in FRAMES.items():
        for i, (r, fl) in enumerate(fr): s[size * C:(size + 1) * C, i * C:(i + 1) * C] = star(r, bool(fl))
    return s
