"""hintdog_n07.py: Pepper in the hint pictures, redrawn by rule (track chars, 7 Nov 2026).

Owner, board 7 Nov, hint_bubbles_06n: "the design needs to be clearer and also the dog needs to be more distinctive.
looks really dirty now". The 6 Nov pictures were half-size copies of her frames with a 1 px cream rim (made for the
old dark bubble) and a drop shadow: on the light bubble the rim and the shadow read as dirt, and her head was 6 px.
Now each pose is built from a few clean parts, one ink outline round the whole dog, no rim, no shadow:
  HEAD   one stamp, 12 x 8 inside the ink (half her body length: the face is the thing that reads at 1x): a round
         skull with a soft sheen, the snout forward with the nose on its tip, a white eye with its pupil, the
         floppy ear hanging behind in the shade colour; a barking variant with the mouth open.
  BANDANA her pink, a triangle under the jaw (light, mid, the fold), 3 to 4 rows: the thing that says "Pepper".
  BODY   a filled ellipse, sheen on the top row, shade under it; legs as short bars with the far pair in shade;
         the tail as a 2 px stroke.
Colours: her own (art/pepper.png): coat, shade, the blue-grey sheen (one step softer), ink, the bandana's three pinks,
plus white for the eye."""
import math
import numpy as np

COL = {'o': (1, 1, 2), 's': (23, 24, 31), 'b': (57, 56, 71), 'h': (96, 100, 124), 'w': (255, 255, 255),
       'P': (250, 100, 200), 'p': (196, 60, 150), 'q': (155, 46, 118)}
HEAD = ["..bbbbb.....",
        ".bhhbbbb....",
        "bbhbbbbbbbb.",
        "bbbbwobbbbbo",
        "sbbbbbbbbbbb",
        "ssbbbbbbsss.",
        "sss.bbbbb...",
        ".ss........."]
HEAD_BARK = ["..bbbbb.....",
             ".bhhbbbbbbbo",
             "bbhbbbbbbbb.",
             "bbbbwobbbs..",
             "sbbbbbbs....",
             "ssbbbbbbbbb.",
             "sss.bbbbb...",
             ".ss........."]


class Dog:
    def __init__(self, W, H):
        self.W, self.H = W, H; self.c = np.full((H, W), '.', dtype='<U1')

    def put(self, x, y, k):
        if 0 <= x < self.W and 0 <= y < self.H: self.c[y, x] = k

    def stamp(self, rows, x0, y0):
        for j, r in enumerate(rows):
            for i, k in enumerate(r):
                if k != '.': self.put(x0 + i, y0 + j, k)

    def ellipse(self, cx, cy, rx, ry, rot=0.0):
        t = math.radians(rot); m = np.zeros((self.H, self.W), bool)
        yy, xx = np.mgrid[0:self.H, 0:self.W]; dx, dy = xx - cx, yy - cy
        u, v = dx * math.cos(t) + dy * math.sin(t), -dx * math.sin(t) + dy * math.cos(t)
        m = (u / rx) ** 2 + (v / ry) ** 2 <= 1.0
        self.c[m] = 'b'
        top = m & ~np.roll(m, 1, 0); bot = m & ~np.roll(m, -1, 0)
        self.c[top] = 'h'; self.c[bot] = 's'

    def bar(self, p, q, w, k):
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(float)
        (px, py), (qx, qy) = p, q; dx, dy = qx - px, qy - py; L2 = dx * dx + dy * dy or 1
        t = np.clip(((xx - px) * dx + (yy - py) * dy) / L2, 0, 1)
        m = np.hypot(xx - (px + t * dx), yy - (py + t * dy)) <= w / 2
        self.c[m] = k

    def rect(self, x0, y0, x1, y1, k):
        self.c[y0:y1 + 1, x0:x1 + 1] = k

    def bandana(self, x, y):
        """a triangle under the jaw: 5 px wide at its top row, 3 rows down to the point"""
        for j, (a, b) in enumerate(((0, 5), (1, 4), (2, 3))):
            for i in range(a, b + 1): self.put(x + i, y + j, 'P' if j == 0 else ('p' if i < b else 'q'))
        self.put(x + 2, y + 3, 'q')


def pose(kind):
    """the pose as a grid of colour keys (no outline: the caller adds the ink round it), facing right"""
    if kind in ('stand', 'bark', 'sniff'):
        d = Dog(28, 20)
        d.bar((4, 9), (1, 4), 2.2, 'b')                              # tail up
        d.rect(13, 13, 14, 18, 's'); d.rect(7, 13, 8, 18, 's')       # far legs (shade)
        d.ellipse(11, 10, 7.6, 3.6)                                  # body
        d.rect(15, 12, 17, 19, 'b'); d.put(18, 19, 'b')              # near front leg, paw forward
        d.rect(4, 12, 6, 19, 'b'); d.put(7, 19, 'b')                 # near back leg
        if kind == 'sniff':
            d.bar((16, 8), (19, 12), 4.5, 'b')                       # neck down
            d.bandana(14, 8)                                         # on the neck, under the head
            d.stamp(HEAD, 16, 11)
        else:
            d.rect(15, 5, 18, 9, 'b')                                # neck
            d.stamp(HEAD_BARK if kind == 'bark' else HEAD, 15, 0)
            d.bandana(16, 7)
        return d
    if kind == 'low':
        d = Dog(30, 14)
        d.bar((3, 7), (0, 6), 2.2, 'b')
        d.rect(14, 10, 15, 13, 's'); d.rect(8, 10, 9, 13, 's')
        d.ellipse(12, 8, 9.2, 3.1)
        d.rect(17, 10, 19, 13, 'b'); d.put(20, 13, 'b'); d.rect(4, 10, 6, 13, 'b'); d.put(7, 13, 'b')
        d.rect(17, 4, 20, 7, 'b')
        d.stamp(HEAD, 18, 0)
        d.bandana(18, 6)
        return d
    if kind == 'jump':
        d = Dog(30, 17)
        d.bar((4, 6), (0, 2), 2.2, 'b')
        d.bar((15, 10), (19, 14), 2.0, 's'); d.bar((7, 10), (3, 14), 2.0, 's')
        d.ellipse(11, 8, 8.4, 3.4, rot=-10)
        d.bar((17, 9), (22, 14), 2.6, 'b'); d.bar((5, 10), (0, 15), 2.6, 'b')
        d.rect(16, 3, 19, 7, 'b')
        d.stamp(HEAD, 17, 0)
        d.bandana(18, 6)
        return d
    if kind == 'crawl':
        d = Dog(32, 11)
        d.bar((2, 5), (0, 4), 2.0, 'b')
        d.ellipse(12, 7, 10.2, 2.6)
        d.rect(18, 8, 24, 9, 'b'); d.rect(0, 8, 6, 9, 'b')           # legs flat, forward and back
        d.stamp(HEAD, 19, 1)
        d.bandana(20, 7)
        return d
    raise KeyError(kind)
