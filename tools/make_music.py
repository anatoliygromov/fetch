#!/usr/bin/env python3
"""FETCH! music: the tunes written as data, a small chip synth, and the files the game plays.

    python3 tools/make_music.py              all tunes -> riverwalk/music/*.ogg (+ title.mod), manifest
    python3 tools/make_music.py --out DIR    also copies the files, a piano roll PNG per tune and chords.txt to DIR
    python3 tools/make_music.py title        only the named tunes

The sound is a 90s console sound chip: pulse 1 (the tune), pulse 2 (echo, harmony, answers, chord arpeggios),
a 16-step triangle for the bass and a noise channel for the drums (an LFSR like the real chips). Everything is
rendered at 44100 Hz and filtered down to 22050 Hz mono, the rate of the game's sound effects.

Notation (one string per channel, bars split by '|', every bar 16 sixteenths):
    F#4:4    a note and its length in sixteenths      r:2   a rest        -:4   the last note goes on (a tie)
    [C4 E4 G4]:8   a chord, played as a fast arpeggio (the chip way of playing chords on one channel)
    flags after the length: s staccato, v vibrato, > accent, q quiet, u scoop up into the note, d droop at the end
Drums: 16 characters a bar, k kick, s snare, t rim tick; hats lane: h closed, o open, c crash; '.' nothing.
A one-bar drum pattern repeats over the whole section.
Generated parts: bass ('bounce' root / octave eighths, 'drive' root eighths, 'pizz' plucked quarters, 'walk'
walking quarters, 'hold'), pulse 2 ('echo' the tune delayed and quieter, 'arp' chord arpeggios in a rhythm).

A looping tune is rendered twice over and the tail of the second pass (echo, ringing notes) is folded onto the
start, so the last sample runs into the first without a click. Each tune is set to the same loudness (RMS), with
its peak kept under -1 dBFS; the game plays music about 6 dB under the sound effects (sfx.lua).
"""
import os
import re
import shutil
import struct
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUSIC = os.path.join(ROOT, "riverwalk", "music")
HI, SR = 44100, 22050
RMS_DB = -17.0          # every tune's loudness (RMS of the sounding part)
PEAK_DB = -1.0          # never above this

# ---------------------------------------------------------------------------------------------------------------
# notes and chords
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", name)
    if not m:
        raise ValueError("bad note " + name)
    return 12 * (int(m[3]) + 1) + NAMES[m[1]] + (1 if m[2] == "#" else -1 if m[2] == "b" else 0)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


QUAL = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11],
        "sus4": [0, 5, 7], "dim": [0, 3, 6], "6": [0, 4, 7, 9]}


def chord(sym):
    """'F#m7' -> (bass pitch class, [pitch classes])"""
    m = re.fullmatch(r"([A-G][#b]?)(maj7|m7|sus4|dim|m|7|6|)(?:/([A-G][#b]?))?", sym)
    if not m:
        raise ValueError("bad chord " + sym)
    root = midi(m[1] + "0") % 12
    pcs = [(root + i) % 12 for i in QUAL[m[2]]]
    bass = midi(m[3] + "0") % 12 if m[3] else root
    return bass, pcs


def in_range(pc, lo):
    """the pitch with class pc at or just above midi note lo"""
    return lo + (pc - lo) % 12


# ---------------------------------------------------------------------------------------------------------------
# parsing a song into events (row = a sixteenth note)
TOKEN = re.compile(r"(\[[^\]]+\]|[A-G][#b]?-?\d|r|-):(\d+)([sv>qud]*)$")


def bars_of(text):
    return [b for b in text.split("|") if b.strip()]


def parse_part(text, start, nbars, what):
    """a written part -> list of events; each bar must hold 16 sixteenths"""
    evs, last = [], None
    bars = bars_of(text) if text else []
    if bars and len(bars) != nbars:
        raise ValueError(f"{what}: {len(bars)} bars, the section has {nbars}")
    for bi, bar in enumerate(bars):
        row = 0
        for tok in bar.split():
            m = TOKEN.match(tok.replace(" ", ""))
            if not m:
                raise ValueError(f"{what} bar {bi + 1}: bad token {tok}")
            n, ln, fl = m[1], int(m[2]), set(m[3])
            if n == "-":
                if last is None:
                    raise ValueError(f"{what}: a tie with nothing before it")
                last["len"] += ln
            elif n == "r":
                last = None
            else:
                notes = [midi(x) for x in n[1:-1].split()] if n.startswith("[") else [midi(n)]
                last = {"row": start + bi * 16 + row, "len": ln, "notes": notes, "flags": fl}
                evs.append(last)
            row += ln
        if row != 16:
            raise ValueError(f"{what} bar {bi + 1}: {row} sixteenths, not 16: {bar.strip()}")
    return evs


def chord_spans(chords, start):
    """'D | G | Em A' -> [(row, len, symbol)]"""
    out = []
    for bi, bar in enumerate(bars_of(chords)):
        syms = bar.split()
        each = 16 // len(syms)
        for i, s in enumerate(syms):
            out.append((start + bi * 16 + i * each, each, s))
    return out


def gen_bass(style, spans):
    evs = []
    for row, ln, sym in spans:
        bass, pcs = chord(sym)
        r = in_range(bass, 40)               # E2 .. D#3
        fifth = r + 7 if r + 7 <= 52 else r - 5           # the fifth above, or the one below when too high
        if style == "bounce":
            for k in range(0, ln, 2):
                evs.append({"row": row + k, "len": 2, "notes": [r + (12 if (k // 2) % 2 else 0)], "flags": {"s"}})
        elif style == "drive":
            for k in range(0, ln, 2):
                evs.append({"row": row + k, "len": 2, "notes": [r], "flags": set()})
        elif style == "pizz":
            for k in range(0, ln, 4):
                evs.append({"row": row + k, "len": 4, "notes": [r if (k // 4) % 2 == 0 else fifth],
                            "flags": {"s", "p"}})
        elif style == "walk":
            third = in_range(pcs[1], r)
            five = in_range(pcs[2], r)
            seq = [r, third, five, five + 2 if five + 2 < r + 12 else r + 12]
            for i, k in enumerate(range(0, ln, 4)):
                evs.append({"row": row + k, "len": 4, "notes": [seq[i % 4]], "flags": set()})
        elif style == "hold":
            evs.append({"row": row, "len": ln, "notes": [r], "flags": set()})
        else:
            raise ValueError("bass style " + style)
    return evs


def gen_arp(rhythm, spans, lo=62):
    """chord arpeggios: rhythm is 16 chars a bar, 'x' starts a chord that lasts to the next mark, '.' holds,
    '_' a rest"""
    evs = []
    for row, ln, sym in spans:
        _, pcs = chord(sym)
        tones = sorted(in_range(pc, lo) for pc in pcs[:3])
        for k in range(ln):
            c = rhythm[(row + k) % 16]
            if c == "x":
                n = 1
                while k + n < ln and rhythm[(row + k + n) % 16] == ".":
                    n += 1
                evs.append({"row": row + k, "len": n, "notes": tones, "flags": {"s"} if n <= 2 else set()})
    return evs


def build(song):
    """the song's sections -> events per channel, the chord spans and the section marks"""
    ch = {"lead": [], "p2": [], "bass": [], "drum": []}
    spans_all, marks = [], []
    row = 0
    for sec in song["sections"]:
        nb = len(bars_of(sec["chords"]))
        spans = chord_spans(sec["chords"], row)
        spans_all += spans
        marks.append((row, sec["name"]))
        vol = sec.get("lead_vol", 1.0)
        lead = parse_part(sec.get("lead", ""), row, nb, song["name"] + " " + sec["name"] + " lead")
        for e in lead:
            e.update(vol=vol, duty=sec.get("lead_duty", song.get("lead_duty", 0.25)))
        ch["lead"] += lead
        p2 = sec.get("p2", "")
        if isinstance(p2, tuple):
            kind = p2[0]
            if kind == "echo":            # ('echo', delay rows, volume)
                for e in lead:
                    ch["p2"].append(dict(e, row=e["row"] + p2[1], vol=e["vol"] * p2[2],
                                         duty=sec.get("p2_duty", 0.125), echo=True))
            elif kind == "arp":           # ('arp', rhythm, volume)
                for e in gen_arp(p2[1], spans, p2[3] if len(p2) > 3 else 62):
                    e.update(vol=p2[2], duty=sec.get("p2_duty", 0.5))
                    ch["p2"].append(e)
        else:
            evs = parse_part(p2, row, nb, song["name"] + " " + sec["name"] + " p2")
            for e in evs:
                e.update(vol=sec.get("p2_vol", 0.6), duty=sec.get("p2_duty", 0.5))
            ch["p2"] += evs
        b = sec.get("bass", "bounce")
        if b in ("bounce", "drive", "pizz", "walk", "hold"):
            evs = gen_bass(b, spans)
        else:
            evs = parse_part(b, row, nb, song["name"] + " " + sec["name"] + " bass")
        for e in evs:
            e.update(vol=sec.get("bass_vol", 1.0))
        ch["bass"] += evs
        for lane in ("drums", "hats"):
            pat = bars_of(sec.get(lane, ""))
            if not pat:
                continue
            if len(pat) == 1:
                pat = pat * nb
            if len(pat) != nb:
                raise ValueError(f"{song['name']} {sec['name']} {lane}: {len(pat)} bars, not {nb}")
            for bi, p in enumerate(pat):
                p = p.strip()
                if len(p) != 16:
                    raise ValueError(f"{song['name']} {sec['name']} {lane} bar {bi + 1}: {len(p)} steps")
                for k, c in enumerate(p):
                    if c != ".":
                        ch["drum"].append({"row": row + bi * 16 + k, "len": 1, "drum": c,
                                           "vol": sec.get("drum_vol", 1.0)})
        row += nb * 16
    return ch, spans_all, marks, row


# ---------------------------------------------------------------------------------------------------------------
# the synth
def row_time(song, row):
    """seconds at a row; swing moves the off-beat eighth later (0.5 = straight)"""
    beat = 60.0 / song["bpm"]
    s = song.get("swing", 0.5)
    q, r = divmod(row, 4)
    pos = [0.0, s / 2, s, s + (1 - s) / 2][r]
    return (q + pos) * beat


def blep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    y[m] = x * x + x + x + 1
    return y


def pulse(freq, duty):
    dt = freq / HI
    ph = np.cumsum(dt) - dt[0]
    t = ph % 1.0
    naive = np.where(t < duty, 1.0, -1.0)
    return naive + blep(t, dt) - blep((t + 1 - duty) % 1.0, dt) - (2 * duty - 1)   # (centred on zero)


def triangle(freq):
    ph = np.cumsum(freq / HI) % 1.0
    tri = 1 - 4 * np.abs(ph - 0.5)
    return np.floor((tri + 1) / 2 * 15.999) / 7.5 - 1       # 16 steps, like the chip


def lfsr(short):
    reg, out = 1, []
    for _ in range(93 if short else 32767):
        bit = (reg ^ (reg >> (6 if short else 1))) & 1
        reg = (reg >> 1) | (bit << 14)
        out.append(1.0 if reg & 1 else -1.0)
    return np.array(out)


NOISE_LONG, NOISE_SHORT = lfsr(False), lfsr(True)


def noise(n, clock, short=False, seed=0):
    tab = NOISE_SHORT if short else NOISE_LONG
    idx = (seed + (np.arange(n) * clock / HI).astype(np.int64)) % len(tab)
    return tab[idx]


def drum(c):
    """one drum hit as samples at HI"""
    def t_(sec):
        return np.arange(int(sec * HI)) / HI
    if c == "k":
        t = t_(0.16)
        f = 50 + 110 * np.exp(-t / 0.025)
        x = triangle(f) * np.exp(-t / 0.07)
        x[: int(0.004 * HI)] += noise(int(0.004 * HI), 20000) * 0.5
        return x * 1.0
    if c == "s":
        t = t_(0.18)
        return noise(len(t), 14000, seed=777) * np.exp(-t / 0.055) * 0.8 + \
            triangle(np.full(len(t), 185.0)) * np.exp(-t / 0.03) * 0.6
    if c == "t":
        t = t_(0.03)
        return noise(len(t), 30000, short=True) * np.exp(-t / 0.008) * 0.45
    if c in "ho":
        t = t_(0.04 if c == "h" else 0.2)
        x = noise(len(t), 44100, seed=1234)
        x = np.diff(x, prepend=0) * 0.5
        return x * np.exp(-t / (0.012 if c == "h" else 0.07)) * 0.55
    if c == "c":
        t = t_(1.0)
        x = noise(len(t), 40000, seed=4321)
        x = np.diff(x, prepend=0) * 0.5
        return x * np.exp(-t / 0.3) * 0.5
    raise ValueError("drum " + c)


CH_GAIN = {"lead": 0.30, "p2": 0.27, "bass": 0.42, "drum": 0.32}


def render_note(song, e, chname):
    t0 = row_time(song, e["row"])
    t1 = row_time(song, e["row"] + e["len"])
    fl = e["flags"]
    dur = t1 - t0
    gate = dur * (0.5 if "s" in fl else 0.92)
    if "p" in fl:
        gate = min(gate, 0.11)
    rel = 0.012 if chname != "bass" else 0.02
    n = int((gate + rel) * HI)
    t = np.arange(n) / HI
    notes = e["notes"]
    if len(notes) > 1:                                    # chip chord: step through the notes 40 times a second
        steps = (t * 40).astype(int) % len(notes)
        semis = np.array(notes, dtype=float)[steps]
    else:
        semis = np.full(n, float(notes[0]))
    if "v" in fl or (chname == "lead" and dur >= 0.45 and len(notes) == 1):
        ramp = np.clip((t - 0.14) / 0.12, 0, 1)
        semis = semis + 0.22 * ramp * np.sin(2 * np.pi * 5.6 * t)
    if "u" in fl:
        semis = semis - 1.0 * np.clip(1 - t / 0.05, 0, 1)
    if "d" in fl:
        semis = semis - 2.5 * np.clip((t - gate * 0.55) / (gate * 0.45), 0, 1) ** 2
    f = hz(semis)
    if chname == "bass":
        x = triangle(f)
        sus, dec = 0.85, 0.3
    else:
        x = pulse(f, e.get("duty", 0.5))
        sus, dec = (0.5, 0.12) if "s" in fl else (0.62, 0.2)
    env = sus + (1 - sus) * np.exp(-t / dec)
    env *= np.clip(t / 0.002, 0, 1)                         # 2 ms attack (no click)
    env *= np.clip((gate + rel - t) / rel, 0, 1)            # release
    vol = e.get("vol", 1.0) * (1.25 if ">" in fl else 1.0) * (0.6 if "q" in fl else 1.0)
    return int(round(t0 * HI)), x * env * vol


def render(song, loop):
    ch, spans, marks, rows = build(song)
    length = row_time(song, rows)
    L = int(round(length * SR))
    Lh = 2 * L
    tail = int(3.0 * HI)
    buf = np.zeros(Lh + tail)
    for name, evs in ch.items():
        cb = np.zeros_like(buf)
        for e in evs:
            if name == "drum":
                x = drum(e["drum"]) * e["vol"]
                i0 = int(round(row_time(song, e["row"]) * HI))
            else:
                i0, x = render_note(song, e, name)
            i0 %= Lh if loop else len(buf)
            n = min(len(x), len(cb) - i0)
            cb[i0:i0 + n] += x[:n]
        buf += cb * CH_GAIN[name]
    if loop:
        out = buf[:Lh].copy()
        out[:tail] += buf[Lh:Lh + tail]                       # the tail runs on into the start
        lo = resample_poly(np.concatenate([out, out, out]), 1, 2)[L:2 * L]      # filtered as a circle
    else:
        end = Lh + int(song.get("ring", 0.5) * HI)
        out = buf[:end].copy()
        fade = int(0.08 * HI)
        out[-fade:] *= np.linspace(1, 0, fade)
        lo = resample_poly(out, 1, 2)
        L = len(lo)
    lo -= np.mean(lo) if loop else 0.0
    return lo, ch, spans, marks, rows, length


def normalise(x):
    sounding = np.abs(x) > 1e-3
    rms = np.sqrt(np.mean(x[sounding] ** 2)) if sounding.any() else 1.0
    g = 10 ** (RMS_DB / 20) / rms
    peak = np.max(np.abs(x)) * g
    limit = 10 ** (PEAK_DB / 20)
    if peak > limit:
        g *= limit / peak
    return x * g


# ---------------------------------------------------------------------------------------------------------------
# a ProTracker MOD (4 channels: pulse, pulse, triangle, noise as looped 8-bit samples). LOVE plays .mod through
# libmodplug: tiny files, the real tracker sound. Each pulse note is a short looped wave, the tracker's own
# arpeggio (0xy) plays the chords, 4xy the vibrato, ECx cuts staccato notes.
PERIODS = [856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480, 453,
           428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240, 226,
           214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120, 113]


def mod_sample(data, loop=True, vol=64):
    b = bytes((int(max(-128, min(127, round(v)))) & 0xFF) for v in data)
    if len(b) % 2:
        b += b"\0"
    return {"data": b, "loop": loop, "vol": vol}


def write_mod(song, path, title):
    ch, spans, marks, rows = build(song)
    # samples: 1 pulse 25%, 2 pulse 12.5%, 3 pulse 50%, 4 triangle, 5 kick, 6 snare, 7 hat, 8 crash, 9 tick
    # A one-cycle wave of 32 bytes played at Amiga period p sounds at 3546895 / p / 32 Hz. C-1 (period 856) then
    # is 129.5 Hz: about C3, so tracker octave 1-3 covers C3-B5 for the pulses. The triangle uses 64 bytes a
    # cycle: one octave lower (C2-B4).
    def pulse_wave(duty, n=32):
        return [100 if i < duty * n else -100 for i in range(n)]
    tri = [(1 - 4 * abs(i / 64 - 0.5)) * 120 for i in range(64)]
    tri = [round(v / 16) * 16 for v in tri]

    def drum_8(c, rate=16574):
        x = drum(c)
        x = resample_poly(x, rate, HI)
        return [v * 110 for v in x]
    samples = [mod_sample(pulse_wave(0.25)), mod_sample(pulse_wave(0.125)), mod_sample(pulse_wave(0.5)),
               mod_sample(tri), mod_sample(drum_8("k"), False), mod_sample(drum_8("s"), False),
               mod_sample(drum_8("h"), False), mod_sample(drum_8("c"), False), mod_sample(drum_8("t"), False)]
    names = ["pulse 25", "pulse 12.5", "pulse 50", "triangle", "kick", "snare", "hat", "crash", "tick"]
    drum_ins = {"k": 5, "s": 6, "h": 7, "o": 7, "c": 8, "t": 9}

    def period(m, octave_base):
        i = m - octave_base
        while i < 0:
            i += 12
        while i >= 36:
            i -= 12
        return PERIODS[i]
    # speed 6 ticks a row at the tempo that gives one row = a sixteenth: BPM in tracker terms = song bpm
    nrows = rows
    grid = [[None] * 4 for _ in range(nrows)]

    def put(r, c, cell):
        if 0 <= r < nrows:
            grid[r][c] = cell
    duty_ins = {0.25: 1, 0.125: 2, 0.5: 3}
    for c, name in enumerate(("lead", "p2", "bass")):
        for e in ch[name]:
            base = 48 if name != "bass" else 36          # pulses: tracker C-1 = midi 48; triangle: C-1 = 36
            ins = 4 if name == "bass" else duty_ins.get(e.get("duty", 0.5), 3)
            vol = int(min(64, 40 * e.get("vol", 1.0) * (1.2 if ">" in e["flags"] else 1)))
            if name == "bass":
                vol = 60
            notes = e["notes"]
            eff = (0xC, vol)
            if len(notes) > 1:
                a, b = (notes[1] - notes[0]) % 16, (notes[2] - notes[0]) % 16 if len(notes) > 2 else 0
                eff = (0x0, (a << 4) | b)
            put(e["row"] % nrows, c, (period(notes[0], base), ins, eff))
            if len(notes) > 1:
                for k in range(1, e["len"]):
                    if grid[(e["row"] + k) % nrows][c] is None:
                        put((e["row"] + k) % nrows, c, (0, 0, eff))
            cut = e["len"] // 2 if "s" in e["flags"] or "p" in e["flags"] else e["len"]
            if cut < e["len"]:
                r = (e["row"] + cut) % nrows
                if grid[r][c] is None:
                    put(r, c, (0, 0, (0xC, 0)))
            elif "v" in e["flags"] and e["len"] >= 4:
                for k in range(2, e["len"]):
                    r = (e["row"] + k) % nrows
                    if grid[r][c] is None:
                        put(r, c, (0, 0, (0x4, 0x63)))
            elif name != "bass" and e["len"] >= 3:
                r = (e["row"] + e["len"] - 1) % nrows                  # short release before the next note
                if grid[r][c] is None:
                    put(r, c, (0, 0, (0xC, 0)))
    for e in ch["drum"]:
        r = e["row"] % nrows
        cur = grid[r][3]
        if cur is not None and e["drum"] in "ho":
            continue                                                    # a hat under a kick or snare: kick wins
        put(r, 3, (214, drum_ins[e["drum"]], (0xC, 48 if e["drum"] in "kc" else 40)))
    npat = (nrows + 63) // 64
    pats = b""
    for p in range(npat):
        for r in range(64):
            rr = p * 64 + r
            for c in range(4):
                cell = grid[rr][c] if rr < nrows else None
                if rr == 0 and c == 3 and cell is None:
                    cell = (0, 0, (0, 0))
                per, ins, (fx, arg) = cell if cell else (0, 0, (0, 0))
                if rr == 0 and c == 0:
                    pass
                pats += struct.pack(">BBBB", (ins & 0xF0) | (per >> 8), per & 0xFF, ((ins & 0x0F) << 4) | fx, arg)
    # tempo: set speed 6, BPM = bpm (one row = a sixteenth at 6 ticks); put it on row 0 channel 3 or 2's effect
    pats = bytearray(pats)

    def set_eff(row, chan, fx, arg):
        o = (row * 4 + chan) * 4
        pats[o + 2] = (pats[o + 2] & 0xF0) | fx
        pats[o + 3] = arg
    # find two cells with no effect on row 0 for F06 and Fxx
    used = []
    for c in range(4):
        o = c * 4
        if pats[o + 2] & 0x0F == 0 and pats[o + 3] == 0 and c not in used:
            used.append(c)
    if len(used) < 2:
        used = [3, 2]
    set_eff(0, used[0], 0xF, 6)
    set_eff(0, used[1], 0xF, min(255, song["bpm"]))
    # the last row jumps back to the start (B00): the module loops by itself, with no gap (LOVE's own looping of
    # a module restarts it after a short silence); the jump goes in a cell with no effect if there is one
    free = [c for c in range(4) if pats[((nrows - 1) * 4 + c) * 4 + 2] & 0x0F == 0
            and pats[((nrows - 1) * 4 + c) * 4 + 3] == 0]
    set_eff(nrows - 1, free[0] if free else 2, 0xB, 0)
    out = bytearray(title.encode()[:20].ljust(20, b"\0"))
    for i in range(31):
        if i < len(samples):
            s = samples[i]
            ln = len(s["data"]) // 2
            out += names[i].encode()[:22].ljust(22, b"\0")
            out += struct.pack(">HBBHH", ln, 0, s["vol"], 0 if s["loop"] else 0, ln if s["loop"] else 1)
        else:
            out += b"\0" * 22 + struct.pack(">HBBHH", 0, 0, 0, 0, 1)
    out += bytes([npat, 127]) + bytes(range(npat)) + b"\0" * (128 - npat) + b"M.K."
    out += pats
    for s in samples:
        out += s["data"]
    with open(path, "wb") as f:
        f.write(out)
    return len(out)


# ---------------------------------------------------------------------------------------------------------------
# THE TUNES

# Title: D major, 132 bpm, 20 bars (36.4 s). A fanfare intro, the hook (A: call 4 bars, answer 4 bars, echoed by
# pulse 2), B in B minor with call (pulse 1) and response (pulse 2), A' over the bright flat-seven chord (C in D),
# and a turnaround on IV - V that runs back into the intro.
TITLE = {
    "name": "title", "bpm": 132, "key": "D major", "mood": "bright, a little heroic",
    "sections": [
        {"name": "Intro", "chords": "D | A",
         "lead": "D5:3> D5:3> D5:2 F#5:4 A5:4 | E5:3> E5:3> E5:2 C#5:4 A4:4",
         "p2": "F#4:3 F#4:3 F#4:2 A4:4 D5:4 | C#5:3 C#5:3 C#5:2 A4:4 E4:4", "p2_vol": 0.75,
         "bass": "D3:3 D3:3 D3:2 A2:4 D3:4 | A2:3 A2:3 A2:2 E2:4 A2:4",
         "drums": "k..k..k.s...s.s. | k..k..k.s.s.ssss", "hats": "c............... | ................"},
        {"name": "A", "chords": "D | G | D | A | D | G | Em A | D",
         "lead": "F#4:4 A4:4 D5:6 C#5:2 | B4:4 A4:2 G4:2 A4:8v | F#4:4 A4:4 D5:4 E5:2 F#5:2 | E5:8v C#5:4 A4:4 |"
                 "F#4:4 A4:4 D5:6 C#5:2 | B4:4 D5:2 E5:2 D5:4 B4:4 | G4:2 B4:2 E5:4 C#5:2 E5:2 A5:4 | F#5:2 E5:2 D5:12v",
         "p2": ("echo", 3, 0.4),
         "drums": "k...s...k.k.s...", "hats": "h.h.h.h.h.h.h.h."},
        {"name": "B", "chords": "Bm | G | Em | A",
         "lead": "B4:2 C#5:2 D5:2 F#5:4 r:6 | B4:2 C#5:2 D5:2 G5:4 r:6 | E5:2 F#5:2 G5:2 A5:2 B5:4 A5:2 G5:2 |"
                 "E5:4 C#5:2 E5:2 A5:8v",
         "p2": "r:10 F#5:2 E5:2 D5:2 | r:10 G5:2 F#5:2 D5:2 | C#5:2 D5:2 E5:2 F#5:2 G5:4 F#5:2 E5:2 |"
               "C#5:4 A4:2 C#5:2 E5:8", "p2_vol": 0.7,
         "bass": "drive", "drums": "k..ks...k..ks..k", "hats": "h.hhh.hhh.hhh.hh"},
        {"name": "A'", "chords": "D | C | G | A",
         "lead": "F#4:4 A4:4 D5:6 C#5:2 | E5:4 D5:2 C5:2 G4:8v | B4:4 D5:4 G5:4 F#5:2 G5:2 | A5:12v r:4",
         "p2": "D4:4 F#4:4 A4:6 A4:2 | C5:4 B4:2 A4:2 E4:8 | G4:4 B4:4 D5:4 D5:2 D5:2 | C#5:12 r:4", "p2_vol": 0.7,
         "drums": "k...s...k.k.s...", "hats": "c.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h."},
        {"name": "Turnaround", "chords": "G | A",
         "lead": "r:4 D5:2s D5:2s E5:2s E5:2s F#5:2s G5:2s | A5:4 G5:2s F#5:2s E5:2s C#5:2s A4:4",
         "p2": ("echo", 3, 0.4),
         "bass": "G2:4 A2:4 B2:4 C#3:4 | A2:2 A2:2 A2:2 A2:2 B2:2 B2:2 C#3:2 C#3:2",
         "drums": "k...s...k.k.s... | k.s.s.s.s.s.ssss", "hats": "h.h.h.h.h.h.h.h. | h.h.h.h........."},
    ]}

# City Park: G major, 126 bpm with a light shuffle, 42 bars (80 s). Playful staccato A tune (call 4 bars, answer
# 4 bars), A2 with a turn to B7 and E minor, the sneaky B section in E minor (tiptoe staccato on a thin 12.5%
# pulse, plucked bass, only ticks and hats: creeping up on the magpie), C with honking stabs answered by pulse 2
# (barking at the geese), A' with chord arpeggios under the tune, and a turnaround (C - D7) back to the intro.
CITYPARK = {
    "name": "citypark", "bpm": 126, "swing": 0.6, "key": "G major (B section E minor)",
    "mood": "playful, bouncy, sneaky moments",
    "sections": [
        {"name": "Intro", "chords": "G | G | C | D7",
         "lead": "r:16 | r:16 | r:16 | r:8 A4:2s B4:2s C5:2s C#5:2s",
         "p2": ("arp", "x.x.x...x.x.x...", 0.55),
         "drums": "k.......k....... | k.......k.....k. | k...s...k.k.s... | k...s...k.k.s.ss",
         "hats": "h.h.h.h.h.h.h.h."},
        {"name": "A", "chords": "G | Em | C | D | G | Em | Am D | G",
         "lead": "D5:2s r:2 B4:2s D5:2s G5:4 F#5:2s G5:2s | E5:2s G5:2s B5:4 A5:2s G5:2s E5:4 |"
                 "C5:2s r:2 E5:2s G5:2s A5:4 G5:2s E5:2s | A5:4 F#5:2s D5:2s E5:2s F#5:2s D5:4 |"
                 "D5:2s r:2 B4:2s D5:2s G5:4 F#5:2s G5:2s | B5:2s r:2 G5:2s E5:2s B4:4 C5:2 D5:2 |"
                 "C5:2s E5:2s A5:4 F#5:2s A5:2s D6:4 | B5:4 G5:2s D5:2s G5:4 r:4",
         "p2": ("echo", 3, 0.38),
         "drums": "k...s...k.k.s...", "hats": "h.h.h.h.h.h.h.h."},
        {"name": "A2", "chords": "G | Em | C | D | B7 | Em | Am D7 | G",
         "lead": "D5:2s r:2 B4:2s D5:2s G5:4 F#5:2s G5:2s | E5:2s G5:2s B5:4 A5:2s G5:2s E5:4 |"
                 "C5:2s r:2 E5:2s G5:2s A5:4 G5:2s E5:2s | A5:4 F#5:2s D5:2s r:4 D5:1 E5:1 F#5:2s |"
                 "F#5:4 D#5:2s F#5:2s A5:4 F#5:4 | G5:4 E5:2s B4:2s E5:8v |"
                 "A5:2s G5:2s E5:2s C5:2s D5:2s F#5:2s C6:2s A5:2s | G5:4 D5:2s B4:2s G4:4 r:4",
         "p2": "B4:2s r:2 G4:2s B4:2s D5:4 D5:2s D5:2s | B4:2s E5:2s G5:4 F#5:2s E5:2s B4:4 |"
               "A4:2s r:2 C5:2s E5:2s F#5:4 E5:2s C5:2s | F#5:4 D5:2s A4:2s r:4 A4:1 C5:1 D5:2s |"
               "D#5:4 B4:2s D#5:2s F#5:4 D#5:4 | E5:4 B4:2s G4:2s B4:8 |"
               "E5:2s E5:2s C5:2s A4:2s A4:2s D5:2s A5:2s F#5:2s | D5:4 B4:2s G4:2s D4:4 r:4", "p2_vol": 0.5,
         "drums": "k...s...k.k.s... | k...s...k.k.s... | k...s...k.k.s... | k...s...k.k.s... |"
                  "k...s...k.k.s... | k...s...k.k.s... | k...s...k.k.s... | k...s...s.s.s.s.",
         "hats": "h.h.h.h.h.h.h.h."},
        {"name": "B (sneaking)", "chords": "Em | Em | C | B7 | Em | Em | Am | B7",
         "lead": "E4:1s r:1 F#4:1s r:1 G4:1s r:3 B4:1s r:1 A4:1s r:1 G4:1s r:3 |"
                 "E4:1s r:1 F#4:1s r:1 G4:1s r:1 G#4:1s r:1 A4:2s r:2 B4:2s r:2 |"
                 "C5:1s r:1 B4:1s r:1 A4:1s r:3 G4:1s r:1 A4:1s r:1 C5:1s r:3 |"
                 "B4:2s r:2 D#5:2s r:2 F#5:1s E5:1s D#5:1s C5:1s B4:2s r:2 |"
                 "E4:1s r:1 F#4:1s r:1 G4:1s r:3 B4:1s r:1 A4:1s r:1 G4:1s r:3 |"
                 "E4:1s r:1 F#4:1s r:1 G4:1s r:1 G#4:1s r:1 A4:2s r:2 B4:2s r:2 |"
                 "A4:1s r:1 C5:1s r:1 E5:1s r:3 D#5:1s r:1 E5:1s r:1 C5:1s r:3 |"
                 "B4:4v r:2 F#4:1s G4:1s A4:1s B4:1s C5:1s D#5:1s F#5:2 r:2",
         "lead_duty": 0.125, "lead_vol": 0.85, "p2": ("echo", 2, 0.3), "p2_duty": 0.125,
         "bass": "pizz", "bass_vol": 0.9,
         "drums": "....t.......t...", "hats": "h...h...h...h...", "drum_vol": 0.7},
        {"name": "C (geese)", "chords": "C | D | Bm Em | Am D",
         "lead": "C5:2> r:2 C5:2> r:2 E5:2s G5:2s E5:2s C5:2s | D5:2> r:2 D5:2> r:2 F#5:2s A5:2s F#5:2s D5:2s |"
                 "F#5:2s D5:2s B4:4 G5:2s E5:2s B4:4 | A5:2> r:2 A5:2> r:2 C6:2s B5:2s A5:2s F#5:2s",
         "p2": "G4:2> r:2 G4:2> r:2 r:8 | A4:2> r:2 A4:2> r:2 r:8 | r:4 F#4:2s D4:2s r:4 G4:2s E4:2s |"
               "C5:2> r:2 C5:2> r:2 r:8", "p2_vol": 0.8, "p2_duty": 0.25,
         "bass": "drive",
         "drums": "k.s.k.s.k...s.s.", "hats": "c...h...h...h... | h...h...h...h... | h...h...h...h... | h...h...h...o..."},
        {"name": "A'", "chords": "G | Em | C | D | G | Em | Am D | G",
         "lead": "D5:2s r:2 B4:2s D5:2s G5:4 F#5:2s G5:2s | E5:2s G5:2s B5:4 A5:2s G5:2s E5:4 |"
                 "C5:2s r:2 E5:2s G5:2s A5:4 G5:2s E5:2s | A5:4 F#5:2s D5:2s E5:2s F#5:2s D5:4 |"
                 "D5:2s r:2 B4:2s D5:2s G5:4 F#5:2s G5:2s | B5:2s r:2 G5:2s E5:2s B4:4 C5:2 D5:2 |"
                 "C5:2s E5:2s A5:4 F#5:2s A5:2s D6:4 | B5:4 G5:2s D5:2s G5:4 r:4",
         "p2": ("arp", "x.x.x.x.x.x.x.x.", 0.4, 55),
         "drums": "k...s...k.k.s...", "hats": "c.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. |"
         "h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h. | h.h.h.h.h.h.h.h."},
        {"name": "Turnaround", "chords": "C | D7",
         "lead": "E5:2s G5:2s C6:4 B5:2s A5:2s G5:4 | F#5:2s A5:2s C6:2s A5:2s F#5:2s D5:2s C5:2s A4:2s",
         "p2": ("echo", 3, 0.38), "bass": "walk",
         "drums": "k...s...k.k.s... | k...s.s.s.s.ssss", "hats": "h.h.h.h.h.h.h.h. | h.h.h.h........."},
    ]}

# Level clear: D major, 150 bpm, 2 bars and a ring (3.6 s): a rising arpeggio to the top D over I - IV - V, and the
# top D held over I with vibrato.
CLEAR = {
    "name": "jingle_clear", "bpm": 150, "key": "D major", "mood": "triumphant", "ring": 0.4,
    "sections": [{"name": "Fanfare", "chords": "D D G A | D",
                  "lead": "D5:2> F#5:2 A5:2 D6:6 B5:2 C#6:2 | D6:12v r:4",
                  "p2": "F#4:2 A4:2 D5:2 B4:6 G5:2 A5:2 | F#5:12v r:4", "p2_vol": 0.7,
                  "bass": "D2:4 D3:4 G2:4 A2:4 | D2:12 r:4",
                  "drums": "k.k.k...s...s.ss | k...............", "hats": "c............... | c..............."}]}

# Game over: D minor, 100 bpm, one bar and a ring (2.9 s): a falling line over Dm - Bb - A - Dm, the last note
# drooping down.
OVER = {
    "name": "jingle_over", "bpm": 100, "key": "D minor", "mood": "sad, gentle (kids play this)", "ring": 0.5,
    "sections": [{"name": "Fall", "chords": "Dm Bb A Dm",
                  "lead": "A4:3 F4:3 E4:2 D4:8vd",
                  "p2": "F4:3 D4:3 C#4:2 A3:8d", "p2_vol": 0.7,
                  "bass": "D2:4 A#1:4 A1:4 D2:4", "drums": "k.......k.......", "drum_vol": 0.6}]}

# Fetch sting ("GOOD GIRL!"): D major, 160 bpm, 1.5 s: a quick arpeggio up, then two notes like the words.
FETCH = {
    "name": "jingle_fetch", "bpm": 160, "key": "D major", "mood": "happy, quick", "ring": 0.06,
    "sections": [{"name": "Good girl", "chords": "D",
                  "lead": "D5:1 F#5:1 A5:1 D6:1 B5:2> D6:6v r:4",
                  "p2": "A4:1 D5:1 F#5:1 A5:1 G5:2 A5:6 r:4", "p2_vol": 0.6,
                  "bass": "D2:2 r:2 A2:2 D3:6 r:4",
                  "drums": "k...s.k.........", "hats": "c..............."}]}

SONGS = [TITLE, CITYPARK, CLEAR, OVER, FETCH]
LOOPS = {"title", "citypark"}


# ---------------------------------------------------------------------------------------------------------------
def chord_chart(song, marks, spans, length, rows):
    lines = [f"{song['name']}: {song['key']}, {song['bpm']} bpm" + (f", shuffle {song['swing']}" if song.get('swing') else "")
             + f", {rows // 16} bars, {length:.2f} s" + (" (loops)" if song["name"] in LOOPS else ""),
             f"  mood: {song['mood']}"]
    for sec in song["sections"]:
        bars = [" ".join(b.split()) for b in bars_of(sec["chords"])]
        lines.append(f"  {sec['name']:<14} | " + " | ".join(bars) + " |")
    return "\n".join(lines)


def piano_roll(song, x, ch, spans, marks, rows, path):
    from PIL import Image, ImageDraw
    px = 3 if rows <= 400 else 2
    W = max(400, rows * px + 60)
    lanes = [("lead", 52, 92, (250, 210, 70)), ("p2", 52, 92, (110, 200, 250)), ("bass", 28, 64, (240, 120, 90))]
    H = 70 + sum((hi - lo) * 2 + 14 for _, lo, hi, _ in lanes) + 60 + 30
    img = Image.new("RGB", (W, H), (18, 20, 30))
    d = ImageDraw.Draw(img)
    d.text((6, 4), f"{song['name']}  {song['key']}  {song['bpm']} bpm  {rows // 16} bars", fill=(230, 230, 230))
    # waveform
    wy, wh = 20, 44
    cols = W - 60
    for c in range(cols):
        a = int(c * len(x) / cols)
        b = max(a + 1, int((c + 1) * len(x) / cols))
        seg = x[a:b]
        d.line([(60 + c, wy + wh / 2 - seg.max() * wh / 2), (60 + c, wy + wh / 2 - seg.min() * wh / 2)],
               fill=(120, 220, 140))
    d.text((4, wy + 16), "wave", fill=(160, 160, 160))
    y = 70
    for name, lo, hi, col in lanes:
        h = (hi - lo) * 2
        d.rectangle([60, y, 60 + rows * px, y + h], fill=(28, 30, 44))
        for m in range(lo, hi):
            if m % 12 == 0:
                d.line([(60, y + (hi - m) * 2), (60 + rows * px, y + (hi - m) * 2)], fill=(44, 48, 66))
        for e in ch[name]:
            for k, m in enumerate(e["notes"]):
                yy = y + (hi - max(lo, min(hi, m))) * 2
                c = col if not e.get("echo") else tuple(v // 2 for v in col)
                x0 = 60 + e["row"] * px
                d.rectangle([x0, yy - 1, x0 + max(1, e["len"] * px - 1), yy], fill=c)
        d.text((4, y + h / 2 - 5), name, fill=(200, 200, 200))
        y += h + 14
    # drums
    rowy = {"k": 0, "s": 8, "t": 16, "h": 24, "o": 32, "c": 40}
    d.text((4, y + 20), "drums", fill=(200, 200, 200))
    for e in ch["drum"]:
        x0 = 60 + e["row"] * px
        d.rectangle([x0, y + rowy[e["drum"]], x0 + px - 1, y + rowy[e["drum"]] + 5], fill=(200, 200, 210))
    y += 52
    for r in range(0, rows + 1, 16):
        d.line([(60 + r * px, 66), (60 + r * px, y)], fill=(70, 74, 96))
    for row, ln, sym in spans:
        d.text((61 + row * px, y + 2), sym, fill=(240, 200, 120))
    for row, name in marks:
        d.line([(60 + row * px, 64), (60 + row * px, y + 26)], fill=(250, 250, 250))
        d.text((62 + row * px, y + 14), name, fill=(255, 255, 255))
    img.save(path)


def main():
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    names = set(args)
    os.makedirs(MUSIC, exist_ok=True)
    if out:
        os.makedirs(out, exist_ok=True)
    tmp = os.path.join(MUSIC, ".tmp.wav")
    manifest, charts = [], []
    for song in SONGS:
        if names and song["name"] not in names:
            continue
        loop = song["name"] in LOOPS
        x, ch, spans, marks, rows, length = render(song, loop)
        x = normalise(x)
        pcm = np.round(np.clip(x, -1, 1) * 32767).astype(np.int16)
        wavfile.write(tmp, SR, pcm)
        ogg = os.path.join(MUSIC, song["name"] + ".ogg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:a", "libvorbis", "-q:a", "3", ogg], check=True)
        peak = 20 * np.log10(np.max(np.abs(x)))
        snd = np.abs(x) > 1e-3
        rms = 20 * np.log10(np.sqrt(np.mean(x[snd] ** 2)))
        join = abs(float(x[-1]) - float(x[0]))
        step = float(np.percentile(np.abs(np.diff(x)), 99))
        print(f"{song['name']:<14} {len(x) / SR:6.2f} s  {len(x):7d} samples  peak {peak:5.1f} dBFS  rms {rms:5.1f} dB"
              f"  loop join {join:.4f} (99% step {step:.4f})  {os.path.getsize(ogg) // 1024} KB")
        manifest.append(f"{song['name']} {len(x)} {SR} {'loop' if loop else 'once'}")
        charts.append(chord_chart(song, marks, spans, length, rows))
        if out:
            shutil.copy(ogg, out)
            shutil.copy(tmp, os.path.join(out, song["name"] + ".wav"))
            piano_roll(song, x, ch, spans, marks, rows, os.path.join(out, song["name"] + ".png"))
        if song["name"] == "title":
            size = write_mod(song, os.path.join(MUSIC, "title.mod"), "FETCH! title")
            print(f"{'title.mod':<14} {size // 1024} KB (tracker module, 4 channels)")
            if out:
                shutil.copy(os.path.join(MUSIC, "title.mod"), out)
    os.remove(tmp)
    if not names:
        with open(os.path.join(MUSIC, "manifest.txt"), "w") as f:
            f.write("# made by tools/make_music.py: name, samples, rate, loop or once (tools/check_music.sh)\n")
            f.write("\n".join(manifest) + "\n")
    if out:
        with open(os.path.join(out, "chords.txt"), "w") as f:
            f.write("FETCH! music: chord charts (made by tools/make_music.py)\n\n" + "\n\n".join(charts) + "\n")


if __name__ == "__main__":
    main()
