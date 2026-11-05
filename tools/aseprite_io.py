#!/usr/bin/env python3
"""aseprite_io.py: write and read .aseprite sources without the Aseprite app (RGBA, one layer, N frames).

Why: the polish step (docs/WORKFLOW.md step 7) needs an .aseprite source newer than the cut. The Aseprite MCP runs
on the owner's Mac, which may be asleep during unattended runs. This writes a standard Aseprite 1.3 file (32-bit RGBA,
zlib cels, a tag per animation) that the app opens normally, and reads one back to check it.

  python3 -I tools/aseprite_io.py write OUT.aseprite FRAME1.png [FRAME2.png ...] [--ms 100] [--layer art]
  python3 -I tools/aseprite_io.py sheet OUT.aseprite SHEET.png FW FH [--ms 100]   # a sheet cut into frames
  python3 -I tools/aseprite_io.py check OUT.aseprite REF.png [FW FH]               # pixel-identical round trip
"""
import struct, sys, zlib
import numpy as np
from PIL import Image


def _chunk(kind, data):
    return struct.pack('<IH', len(data) + 6, kind) + data


def _string(s):
    b = s.encode('utf8')
    return struct.pack('<H', len(b)) + b


def write(path, frames, ms=100, layer='art'):
    """frames: list of HxWx4 uint8 arrays, all the same size."""
    h, w = frames[0].shape[:2]
    out = []
    for i, f in enumerate(frames):
        chunks = []
        if i == 0:
            chunks.append(_chunk(0x2004, struct.pack('<HHHHHHB3x', 3, 0, 0, 0, 0, 0, 255) + _string(layer)))
        a = np.ascontiguousarray(f.astype(np.uint8))
        a[a[..., 3] == 0] = 0
        cel = struct.pack('<HhhBHh5x', 0, 0, 0, 255, 2, 0) + struct.pack('<HH', w, h) + zlib.compress(a.tobytes(), 9)
        chunks.append(_chunk(0x2005, cel))
        body = b''.join(chunks)
        out.append(struct.pack('<IHHH2xI', len(body) + 16, 0xF1FA, len(chunks), ms, len(chunks)) + body)
    body = b''.join(out)
    head = struct.pack('<IHHHHHIHII B3x H BB hhHH', 128 + len(body), 0xA5E0, len(frames), w, h, 32, 1, 100, 0, 0,
                       0, 0, 1, 1, 0, 0, 16, 16)
    head += b'\0' * (128 - len(head))
    open(path, 'wb').write(head + body)


def read(path):
    d = open(path, 'rb').read()
    size, magic, nf, w, h, depth = struct.unpack_from('<IHHHHH', d, 0)
    assert magic == 0xA5E0 and depth == 32, 'not a 32-bit aseprite file'
    p, frames = 128, []
    for _ in range(nf):
        fsize, fm, old, ms = struct.unpack_from('<IHHH', d, p)
        n = struct.unpack_from('<I', d, p + 12)[0] or old
        q, img = p + 16, np.zeros((h, w, 4), np.uint8)
        for _ in range(n):
            csize, kind = struct.unpack_from('<IH', d, q)
            if kind == 0x2005:
                li, x, y, op, ct = struct.unpack_from('<HhhBH', d, q + 6)
                if ct == 2:
                    cw, ch = struct.unpack_from('<HH', d, q + 6 + 16)
                    px = np.frombuffer(zlib.decompress(d[q + 6 + 20:q + csize]), np.uint8).reshape(ch, cw, 4)
                    img[y:y + ch, x:x + cw] = px
            q += csize
        frames.append(img); p += fsize
    return frames


def _png(p):
    return np.array(Image.open(p).convert('RGBA'))


def _cut(sheet, fw, fh):
    return [sheet[y:y + fh, x:x + fw] for y in range(0, sheet.shape[0] - fh + 1, fh)
            for x in range(0, sheet.shape[1] - fw + 1, fw)]


if __name__ == '__main__':
    a = sys.argv[1:]
    ms = int(a[a.index('--ms') + 1]) if '--ms' in a else 100
    layer = a[a.index('--layer') + 1] if '--layer' in a else 'art'
    a = [x for i, x in enumerate(a) if x not in ('--ms', '--layer') and (i == 0 or a[i - 1] not in ('--ms', '--layer'))]
    if a[0] == 'write':
        write(a[1], [_png(p) for p in a[2:]], ms, layer); print('wrote', a[1], len(a) - 2, 'frame(s)')
    elif a[0] == 'sheet':
        fr = _cut(_png(a[2]), int(a[3]), int(a[4])); write(a[1], fr, ms, layer); print('wrote', a[1], len(fr), 'frames')
    elif a[0] == 'check':
        got = read(a[1]); ref = _png(a[2])
        want = _cut(ref, int(a[3]), int(a[4])) if len(a) > 4 else [ref]
        clean = []
        for f in want:
            f = f.copy(); f[f[..., 3] == 0] = 0; clean.append(f)
        ok = len(got) == len(clean) and all(np.array_equal(g, c) for g, c in zip(got, clean))
        print('ASEPRITE ROUND TRIP', 'OK' if ok else 'DIFFERS', a[1], len(got), 'frame(s)'); sys.exit(0 if ok else 1)
