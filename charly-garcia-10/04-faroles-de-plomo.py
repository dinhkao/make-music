#!/usr/bin/env python3
"""Ten-song renderer, standard library only.

The palette is limited to instruments already made in this project:
EP/Wurlitzer keys, warm bass, detuned strings, lead/solo synth, choir,
Karplus-Strong pluck, and the project's synthesized drum family.

Run any numbered file directly. It writes a full MP3 and an instrumental
MP3 beside itself. MP3 encoding uses the installed ffmpeg command only;
the Python renderer has no third-party dependencies.
"""
from array import array
from pathlib import Path
import math
import random
import shutil
import subprocess
import sys
import wave

SR = 22050
TAU = 2.0 * math.pi
LUT_N = 4096
SINE = tuple(math.sin(TAU * i / LUT_N) for i in range(LUT_N))
DRUM_CACHE = {}
BEAT_S = 1.0

def osc(cycles):
    return SINE[int(cycles * LUT_N) & (LUT_N - 1)]

def hz(midi):
    return 440.0 * 2.0 ** ((midi - 69.0) / 12.0)

def saw(cycles, n=6):
    return sum(osc(cycles * k) / k for k in range(1, n + 1)) / 1.75

def soft(x, drive=1.0):
    return math.tanh(x * drive)

def env(t, dur, attack, release, sustain=1.0, decay=0.0):
    if attack and t < attack:
        return t / attack
    if decay and t < attack + decay:
        return 1.0 + (sustain - 1.0) * ((t - attack) / decay)
    if release and t > dur - release:
        return max(0.0, (dur - t) / release) ** 1.15 * sustain
    return sustain

def pan_gains(pan):
    pan = max(-1.0, min(1.0, pan))
    return math.cos((pan + 1.0) * math.pi / 4.0), math.sin((pan + 1.0) * math.pi / 4.0)

def add_note(targets, kind, start, dur, midi, amp, pan=0.0, det=0.0, seed=0):
    if dur <= 0:
        return
    start_i = int(start * SR)
    if start_i >= len(targets[0][0]) or start_i + int(dur * SR) < 0:
        return
    first = max(0, -start_i)
    count = min(int(dur * SR), len(targets[0][0]) - max(0, start_i))
    if count <= first:
        return
    f0 = hz(midi) * 2.0 ** (det / 1200.0)
    phase = 0.13 * (seed % 17)
    lg, rg = pan_gains(pan)
    lp = 0.0
    for i in range(first, count):
        t = i / SR
        vib = 0.012 * min(1.0, t / 0.35) * math.sin(TAU * 5.2 * t + seed) if kind in ("lead", "solo") else 0.0
        phase += f0 * 2.0 ** (vib / 12.0) / SR
        if kind == "ep":
            raw = osc(phase) + .50 * osc(phase * 2) + .25 * osc(phase * 3) + .12 * osc(phase * 4.1) + .06 * osc(phase * 5.9)
            e = env(t, dur, .006, min(.10, dur * .2), .62, min(.18, dur * .25))
            raw *= 1 + .12 * math.sin(TAU * 4.7 * t)
        elif kind == "wurli":
            raw = osc(phase + (.055 * (2 * math.exp(-t * 5.5) + .35)) * osc(phase * 2)) + .36 * osc(phase * 1.001)
            lp += .12 * (raw - lp)
            raw = lp
            e = env(t, dur, .010, min(.12, dur * .24), .78, .04)
            raw *= 1 + .10 * math.sin(TAU * 5.4 * t)
        elif kind == "bass":
            raw = soft(osc(phase) + .30 * osc(phase * 2) + .08 * osc(phase * 3), 1.65) * .80
            e = env(t, dur, .008, min(.16, dur * .30), .86, .08)
        elif kind == "strings":
            raw = (saw(phase * .9975, 5) + saw(phase, 5) + saw(phase * 1.0025, 5)) / 3
            lp += .035 * (raw - lp)
            raw = lp
            e = env(t, dur, max(.10, dur * .28), min(.35, dur * .22), .72)
        elif kind == "lead":
            raw = (saw(phase, 7) + saw(phase * 1.004, 7)) / 2
            lp += .08 * (raw - lp)
            raw = lp
            e = env(t, dur, .018, min(.14, dur * .24), .72, .03)
        elif kind == "solo":
            raw = soft(saw(phase, 8) + .55 * saw(phase * .996, 7) + .35 * saw(phase * 1.006, 7), 1.8)
            lp += .11 * (raw - lp)
            raw = lp
            e = env(t, dur, .010, min(.18, dur * .23), .72, .02)
        elif kind == "choir":
            raw = (saw(phase, 6) + .33 * saw(phase * 1.005, 5)) * (.70 + .30 * math.sin(TAU * .23 * t))
            e = env(t, dur, max(.20, dur * .35), min(.55, dur * .25), .62)
        elif kind == "ks":
            raw = (osc(phase) + .34 * osc(phase * 2) + .18 * osc(phase * 3) + .08 * osc(phase * 4)) * math.exp(-t / .52)
            e = env(t, dur, .004, min(.10, dur * .20), .92)
        else:
            continue
        value = raw * e * amp
        j = start_i + i
        if 0 <= j < len(targets[0][0]):
            for left, right in targets:
                left[j] += value * lg
                right[j] += value * rg

def noise(rng):
    return rng.uniform(-1.0, 1.0)

def drum_sample(kind, open_hat=False, seed=0):
    key = (kind, bool(open_hat), seed)
    if key in DRUM_CACHE:
        return DRUM_CACHE[key]
    rng = random.Random(seed)
    if kind == "kick":
        n, out, phase, prev = int(.36 * SR), array("f", [0.0]) * int(.36 * SR), 0.0, 0.0
        for i in range(n):
            t = i / SR
            phase += (43 + 122 * math.exp(-t / .028)) / SR
            click = (noise(rng) - prev) * math.exp(-t / .0012) * .18
            prev = click
            out[i] = soft(math.sin(TAU * phase) * math.exp(-t / .09) * 1.8 + click, 1.35) * min(1, t / .002)
    elif kind == "snare":
        n, out, prev = int(.31 * SR), array("f", [0.0]) * int(.31 * SR), 0.0
        for i in range(n):
            t = i / SR
            x = noise(rng)
            out[i] = (math.sin(TAU * 190 * t) * math.exp(-t / .045) * .50 + (x - prev) * math.exp(-t / .055) * .95) * min(1, t / .002)
            prev = x
    elif kind == "hat":
        n, out = int((.24 if open_hat else .055) * SR), array("f", [0.0]) * int((.24 if open_hat else .055) * SR)
        p1, p2 = 0.0, 0.0
        for i in range(n):
            t = i / SR
            x = noise(rng)
            h1, h2 = x - p1, (x - p1) - p2
            p1, p2 = x, x - p1
            out[i] = (.42 * h1 + .32 * h2) * math.exp(-t / (.12 if open_hat else .021)) * min(1, t / .001)
    elif kind == "tom":
        n, out, phase = int(.30 * SR), array("f", [0.0]) * int(.30 * SR), 0.0
        for i in range(n):
            t = i / SR
            phase += (88 + 74 * math.exp(-t / .04)) / SR
            out[i] = math.sin(TAU * phase) * math.exp(-t / .085) * min(1, t / .003)
    elif kind in ("ride", "tamb"):
        decay = .22 if kind == "ride" else .038
        n, out, prev = int((.68 if kind == "ride" else .14) * SR), array("f", [0.0]) * int((.68 if kind == "ride" else .14) * SR), 0.0
        for i in range(n):
            t = i / SR
            x = noise(rng)
            out[i] = (x - prev) * math.exp(-t / decay) * (.46 if kind == "ride" else .24)
            prev = x
    elif kind == "clap":
        n, out = int(.20 * SR), array("f", [0.0]) * int(.20 * SR)
        for i in range(n):
            t = i / SR
            out[i] = sum(noise(rng) * math.exp(-(t - off) / decay) for off, decay in ((.006, .006), (.027, .010), (.055, .018)) if t >= off) * .20
    else:
        out = array("f")
    DRUM_CACHE[key] = out
    return out

def add_sample(targets, sample, start, amp, pan=0.0):
    start_i = int(start * SR)
    if start_i >= len(targets[0][0]) or start_i + len(sample) < 0:
        return
    lg, rg = pan_gains(pan)
    first, last = max(0, -start_i), min(len(sample), len(targets[0][0]) - start_i)
    for i in range(first, last):
        j, value = start_i + i, sample[i] * amp
        for left, right in targets:
            left[j] += value * lg
            right[j] += value * rg

def chord_notes(song, chord):
    root = song["root"] + 12 + chord[0]
    return [root + i for i in chord[1]]

def chord_bass(song, chord):
    return song["root"] + chord[0] + chord[2] - 12

def voicing(targets, song, chord, start, dur, kind, amp, seed):
    notes = chord_notes(song, chord)
    center = (len(notes) - 1) / 2
    for i, midi in enumerate(notes):
        add_note(targets, kind, start, dur, midi, amp / len(notes), (i - center) * .22, seed=seed + i)

def keys(targets, song, chord, start, beat, style, seed):
    if style == "arp":
        notes = chord_notes(song, chord)
        for i in range(8):
            add_note(targets, "ks", start + beat * i * .5, beat * .42, notes[(i + seed) % len(notes)] + (12 if i in (3, 7) else 0), .11, -.24 if i % 2 == 0 else .24, seed=seed + i)
    elif style == "vamp":
        for b, d, kind, a in ((0, 1.15, "wurli", .92), (1.5, .40, "ep", .62), (2.5, .65, "wurli", .80), (3.25, .30, "ep", .56)):
            voicing(targets, song, chord, start + beat * b, beat * d, kind, .16 * a, seed + int(b * 10))
    elif style == "stabs":
        for b, d, a in ((0, .48, .92), (1.75, .30, .58), (2.5, .48, .82), (3.5, .22, .48)):
            voicing(targets, song, chord, start + beat * b, beat * d, "ep", .17 * a, seed + int(b * 10))
    elif style == "broken":
        voicing(targets, song, chord, start, beat * 1.75, "ep", .14, seed)
        voicing(targets, song, chord, start + beat * 2.25, beat * .70, "wurli", .12, seed + 3)
        notes = chord_notes(song, chord)
        for i, midi in enumerate(notes[:3]):
            add_note(targets, "ks", start + beat * 3.25, beat * .42, midi + (12 if i == 2 else 0), .08, (i - 1) * .24, seed=seed + i)
    elif style == "sustain":
        voicing(targets, song, chord, start, beat * 3.85, "ep", .18, seed)
        voicing(targets, song, chord, start + beat * 2, beat * 1.7, "wurli", .055, seed + 9)
    else:
        voicing(targets, song, chord, start, beat * 3.4, "ep", .15, seed)

def bass(targets, song, chord, start, beat, variant, seed):
    pattern = (
        ((0,0,.65,.34),(.75,7,.30,.25),(1.5,10,.36,.28),(2.25,5,.42,.25),(3,11,.30,.29),(3.5,0,.25,.28)),
        ((0,0,1.20,.32),(1.5,7,.35,.24),(2.25,5,.40,.26),(3.25,10,.45,.28)),
        ((0,0,.35,.36),(.50,7,.22,.24),(1.25,10,.30,.28),(2,5,.32,.27),(2.75,11,.25,.30),(3.5,7,.24,.22)),
        ((0,0,.50,.34),(.75,-1,.26,.25),(1.5,-2,.26,.25),(2.25,7,.45,.31),(3,10,.30,.28),(3.5,11,.24,.27)),
        ((0,0,.35,.35),(.66,2,.23,.24),(1.33,4,.23,.24),(2,7,.34,.31),(2.66,9,.24,.26),(3.33,11,.26,.29)),
    )[variant % 5]
    root = chord_bass(song, chord)
    for i, (b, off, d, amp) in enumerate(pattern):
        midi = root + off
        while midi < 28:
            midi += 12
        add_note(targets, "bass", start + beat * b, beat * d, midi, amp, -.05, seed=seed + i)

def drums(targets, variant, start, section, bar, last, seed):
    v = (variant + section * 2) % 10
    if section == 0:
        kicks = ((0,.60), (2.5,.30)) if v % 2 else ((0,.62),)
        snares, hats = (), ((0,.09),(1,.08),(2,.09),(3,.08))
    elif section == 5:
        kicks = ((0,.70),(1.75,.33),(3.25,.45))
        snares, hats = ((2.5,.62),), ((0,.10),(.75,.09),(1.5,.10),(2.25,.10),(3,.12),(3.75,.11))
    elif section in (3, 6):
        kicks = ((0,.96),(.5,.40),(1.25,.50),(1.75,.34),(2.5,.86),(3.0,.40),(3.5,.47))
        snares = ((1,.92),(3,.97))
        hats = tuple((i * .5, .13 + .04 * ((i + v) % 3 == 0)) for i in range(8))
    else:
        kicks = ((0,.84),(.75,.30),(1.5,.62),(2.25,.38),(2.75,.70),(3.5,.40))
        snares, hats = ((1,.76),(3,.84)), tuple((i * .5, .09 + .04 * (i % 3 == v % 3)) for i in range(8))
    rng = random.Random(seed + bar * 31 + v)
    def hit(kind, beat, amp, pan=0, op=False, jitter=True):
        dt = rng.uniform(-.008, .008) if jitter else 0
        add_sample(targets, drum_sample(kind, op, seed + int(beat * 100) + len(kind)), start + beat * BEAT_S + dt, amp, pan)
    for b, a in kicks: hit("kick", b, a, -.05)
    for b, a in snares: hit("snare", b, a, .02)
    for b, a in hats: hit("hat", b, a, .20)
    for b, a in ((.75,.18),(1.75,.18),(2.75,.22)):
        if section not in (0, 7): hit("snare", b, a, -.04)
    if section in (3, 6):
        for b, a in ((1.5,.20),(3.5,.24)): hit("hat", b, a, .22, True)
        for b, a in ((1,.24),(3,.27)): hit("clap", b, a, -.22)
        for b, a in ((.5,.07),(1.5,.08),(2.5,.08),(3.5,.09)): hit("tamb", b, a, .30)
        for b, a in ((0,.11),(1,.11),(2,.12),(3,.12)): hit("ride", b, a, .34)
    if last and section in (2, 5, 6):
        for i, (b, a) in enumerate(((2.0,.12),(2.25,.18),(2.5,.26),(2.75,.34),(3.0,.44),(3.25,.54),(3.5,.64),(3.75,.74))):
            hit("tom" if i % 3 else "snare", b, a, -.14 + .14 * (i % 3), False)

def motifs(seed):
    cells = (
        (7,10,12,10,7,5,7,10),
        (7,9,12,14,12,10,7,5),
        (5,7,10,12,14,12,10,7),
        (0,2,5,7,5,2,-1,0),
        (4,7,9,12,11,9,7,4),
        (0,3,7,10,9,7,3,0),
        (2,5,7,11,10,7,5,2),
        (7,12,10,5,7,14,12,7),
        (0,4,7,11,9,7,4,0),
        (5,9,12,15,14,12,9,5),
    )
    cell = cells[seed % len(cells)]
    verse, chorus = [], []
    for bar in range(4):
        for i, off in enumerate(cell):
            beat = (i * .5) if i < 4 else (i - 4) * .75
            dur = .34 + .16 * ((i + bar) % 3 == 0)
            verse.append((bar, beat, off, dur, .22 + .04 * (i % 3 == 0)))
        chorus.extend(((bar, b, off + (12 if bar in (1,3) else 0), d, a + .08) for _, b, off, d, a in verse[-8:]))
    pre = [(0,0,12, .80,.30),(0,1.5,14,.55,.24),(0,2.5,16,.70,.28),(1,0,17,1.0,.34),(2,0,15,.70,.27),(2,1.5,14,.50,.24),(2,2.5,12,.70,.27),(3,0,19,1.25,.36)]
    bridge = [(0,0,10,1.10,.26),(0,1.5,12,.55,.22),(0,2.75,14,.65,.25),(1,0,15,.75,.27),(1,2,12,.60,.23),(2,0,10,.95,.25),(2,1.5,7,.65,.23),(3,0,5,1.50,.26)]
    return {"verse": verse, "pre": pre, "chorus": chorus, "bridge": bridge, "outro": [(0,0,12,1.7,.22),(1,0,10,1.5,.20)]}

def progressions(spec):
    return {
        "intro": spec[0],
        "verse": spec[1],
        "pre": spec[2],
        "chorus": spec[3],
        "bridge": spec[4],
        "outro": spec[0],
    }

# Root is a low MIDI root. Chords are (root offset, intervals, bass offset).
# These are deliberate progressions, not a four-chord pop loop.
SONGS = [
    ("Neon Is a Country", 50, 112, 0, "vamp", [
        [(0,(0,3,7,10),0),(5,(0,3,7,10),0)],
        [(0,(0,3,7,10),0),(5,(0,3,7,10),0),(0,(0,3,7,10),0),(8,(0,4,7,10),-1)],
        [(8,(0,4,7,10),0),(10,(0,4,7,10),0),(5,(0,3,7,10),0),(7,(0,4,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,3,7,10),0),(7,(0,4,7,10),0),(9,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(1,(0,4,7,10),0),(2,(0,3,7,10),0),(-1,(0,4,7,10),0)]
    ]),
    ("Aire de los Ausentes", 53, 96, 1, "sustain", [
        [(0,(0,4,7,11),0),(7,(0,3,7,10),0)],
        [(0,(0,4,7,11),0),(7,(0,3,7,10),0),(10,(0,4,7,10),0),(0,(0,4,7,11),0)],
        [(5,(0,3,7,10),0),(8,(0,4,7,10),0),(10,(0,4,7,10),0),(11,(0,3,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,4,7,11),0),(7,(0,3,7,10),0),(2,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(3,(0,4,7,10),0),(5,(0,3,7,10),0),(8,(0,4,7,10),0)]
    ]),
    ("Vidrio en el Aire", 57, 124, 2, "vamp", [
        [(0,(0,3,7,10),0),(7,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(7,(0,4,7,10),0),(5,(0,3,7,10),0),(0,(0,3,7,10),0)],
        [(5,(0,4,7,10),0),(7,(0,4,7,10),0),(9,(0,4,7,10),0),(11,(0,4,7,10),0)],
        [(5,(0,4,7,10),0),(7,(0,3,7,10),0),(0,(0,3,7,10),0),(4,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(1,(0,4,7,10),0),(2,(0,3,7,10),0),(3,(0,4,7,10),0)]
    ]),
    ("Faroles de Plomo", 55, 118, 3, "arp", [
        [(0,(0,4,7,10),0),(7,(0,3,7,10),0)],
        [(0,(0,4,7,10),0),(7,(0,4,7,10),0),(2,(0,3,7,10),0),(4,(0,4,7,10),0)],
        [(9,(0,4,7,10),0),(7,(0,4,7,10),0),(5,(0,3,7,10),0),(4,(0,4,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,4,7,10),0),(7,(0,3,7,10),0),(4,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(1,(0,4,7,10),0),(3,(0,3,7,10),0),(5,(0,4,7,10),0)]
    ]),
    ("La Luz No Firma", 48, 108, 4, "broken", [
        [(0,(0,4,7,11),0),(5,(0,3,7,10),0)],
        [(0,(0,4,7,11),0),(5,(0,3,7,10),0),(7,(0,4,7,10),0),(3,(0,3,7,10),0)],
        [(2,(0,3,7,10),0),(5,(0,4,7,10),0),(7,(0,4,7,10),0),(11,(0,3,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,3,7,10),0),(7,(0,4,7,10),0),(9,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(-1,(0,4,7,10),0),(1,(0,3,7,10),0),(2,(0,4,7,10),0)]
    ]),
    ("Casi Revolución", 52, 104, 5, "stabs", [
        [(0,(0,3,7,10),0),(7,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(7,(0,4,7,10),0),(2,(0,3,7,10),0),(9,(0,4,7,10),0)],
        [(5,(0,4,7,10),0),(7,(0,4,7,10),0),(9,(0,4,7,10),0),(11,(0,4,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,3,7,10),0),(7,(0,4,7,10),0),(2,(0,3,7,10),0)],
        [(0,(0,3,7,10),0),(1,(0,4,7,10),0),(2,(0,3,7,10),0),(4,(0,4,7,10),0)]
    ]),
    ("Separata de Medianoche", 45, 92, 6, "sustain", [
        [(0,(0,4,7,11),0),(7,(0,3,7,10),0)],
        [(0,(0,4,7,11),0),(7,(0,3,7,10),0),(3,(0,4,7,10),0),(10,(0,3,7,10),0)],
        [(5,(0,3,7,10),0),(8,(0,4,7,10),0),(10,(0,4,7,10),0),(11,(0,3,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,4,7,11),0),(7,(0,3,7,10),0),(2,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(2,(0,4,7,10),0),(5,(0,3,7,10),0),(8,(0,4,7,10),0)]
    ]),
    ("La Máquina del Eco", 54, 100, 7, "arp", [
        [(0,(0,4,7,11),0),(5,(0,3,7,10),0)],
        [(0,(0,4,7,11),0),(5,(0,3,7,10),0),(9,(0,4,7,10),0),(4,(0,3,7,10),0)],
        [(2,(0,4,7,10),0),(5,(0,3,7,10),0),(7,(0,4,7,10),0),(11,(0,3,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,3,7,10),0),(7,(0,4,7,10),0),(9,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(1,(0,4,7,10),0),(3,(0,3,7,10),0),(6,(0,4,7,10),0)]
    ]),
    ("Pálido en la Radio", 50, 88, 8, "broken", [
        [(0,(0,3,7,10),0),(8,(0,4,7,10),0)],
        [(0,(0,3,7,10),0),(8,(0,4,7,10),0),(5,(0,4,7,10),0),(3,(0,3,7,10),0)],
        [(5,(0,4,7,10),0),(7,(0,4,7,10),0),(9,(0,3,7,10),0),(11,(0,4,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,3,7,10),0),(7,(0,4,7,10),0),(4,(0,3,7,10),0)],
        [(0,(0,3,7,10),0),(-1,(0,4,7,10),0),(2,(0,3,7,10),0),(5,(0,4,7,10),0)]
    ]),
    ("Cielo de Plomo", 49, 120, 9, "stabs", [
        [(0,(0,4,7,11),0),(9,(0,3,7,10),0)],
        [(0,(0,4,7,11),0),(9,(0,3,7,10),0),(5,(0,4,7,10),0),(3,(0,3,7,10),0)],
        [(2,(0,4,7,10),0),(5,(0,3,7,10),0),(7,(0,4,7,10),0),(11,(0,3,7,10),0)],
        [(5,(0,4,7,11),0),(0,(0,3,7,10),0),(7,(0,4,7,10),0),(4,(0,3,7,10),0)],
        [(0,(0,3,7,10),0),(1,(0,4,7,10),0),(2,(0,3,7,10),0),(6,(0,4,7,10),0)]
    ]),
]

def make_song(spec):
    title, root, tempo, motif_id, default_style, prog = spec
    names = ("intro", "verse", "pre", "chorus", "bridge", "outro")
    p = progressions(prog)
    sections = (
        ("intro", 4, "intro", None, True),
        ("verse", 8, "verse", "verse", False),
        ("pre", 4, "pre", "pre", True),
        ("chorus", 8, "chorus", "chorus", True),
        ("verse2", 8, "verse", "verse", False),
        ("bridge", 8, "bridge", "bridge", True),
        ("final", 8, "chorus", "chorus", True),
        ("outro", 4, "outro", "outro", False),
    )
    return {"title":title, "root":root, "tempo":tempo, "motif_id":motif_id, "default_style":default_style, "progressions":p, "sections":sections}

def render_song(song):
    global BEAT_S
    beat = 60.0 / song["tempo"]
    BEAT_S = beat
    total_bars = sum(x[1] for x in song["sections"])
    n = int((total_bars * 4 * beat + 1.4) * SR)
    fl, fr = array("f", [0.0]) * n, array("f", [0.0]) * n
    il, ir = array("f", [0.0]) * n, array("f", [0.0]) * n
    all_targets, full_targets = ((fl,fr),(il,ir)), ((fl,fr),)
    mot = motifs(song["motif_id"])
    bar_no = 0
    for si, (name, bars, prog_name, motif_name, pad) in enumerate(song["sections"]):
        progression = song["progressions"][prog_name]
        for local in range(bars):
            start = bar_no * 4 * beat
            chord = progression[local % len(progression)]
            style = song["default_style"] if name not in ("intro", "outro") else ("arp" if name == "outro" and song["motif_id"] % 2 else "sparse")
            if name == "chorus" or name == "final":
                style = "stabs" if song["motif_id"] % 2 else "sustain"
            keys(all_targets, song, chord, start, beat, style, si * 100 + local)
            if pad:
                voicing(all_targets, song, chord, start, beat * 4.3, "strings", .13 if name != "bridge" else .10, si + local)
            bass(all_targets, song, chord, start, beat, song["motif_id"] + si, si * 31 + local)
            drums(all_targets, song["motif_id"], start, si, local, local == bars - 1, 4000 + si * 101)
            if motif_name and not (name == "intro"):
                current = local % 4
                for mb, b, off, dur, amp in mot[motif_name]:
                    if mb == current:
                        kind = "solo" if name == "bridge" and (mb + int(b * 2)) % 5 == 0 else "lead"
                        add_note(full_targets, kind, start + (b) * beat, dur * beat, song["root"] + 24 + off, amp, -.16 if int(b * 2) % 2 == 0 else .16, seed=5000 + si * 17 + off)
            if name in ("chorus", "final"):
                for k, midi in enumerate(chord_notes(song, chord)[:3]):
                    add_note(all_targets, "choir", start, beat * 3.7, midi + (12 if k == 2 else 0), .06, (k - 1) * .28, seed=si + k)
            bar_no += 1
    finish(fl, fr, song["tempo"])
    finish(il, ir, song["tempo"])
    return (fl, fr), (il, ir), n / SR

def finish(left, right, tempo):
    n, d1, d2 = len(left), int(.19 * SR), int(.37 * SR)
    old_l, old_r = array("f", left), array("f", right)
    for i in range(n):
        if i >= d1:
            left[i] += old_r[i-d1] * .085
            right[i] += old_l[i-d1] * .085
        if i >= d2:
            left[i] += old_l[i-d2] * .045
            right[i] += old_r[i-d2] * .045
        left[i], right[i] = math.tanh(left[i] * 1.12), math.tanh(right[i] * 1.12)
    peak = max(1e-9, max(max(abs(x) for x in left), max(abs(x) for x in right)))
    gain = .88 / peak
    for i in range(n):
        left[i] *= gain
        right[i] *= gain
    fi, fo = int(.025 * SR), int(.85 * SR)
    for i in range(min(fi, n)):
        q = i / max(1, fi)
        left[i] *= q; right[i] *= q
    for i in range(max(0, n-fo), n):
        q = (n-i) / max(1, fo)
        left[i] *= q; right[i] *= q

def write_wav(path, left, right):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        for start in range(0, len(left), 8192):
            pcm = array("h")
            for i in range(start, min(start + 8192, len(left))):
                pcm.append(max(-32767, min(32767, int(left[i] * 32767))))
                pcm.append(max(-32767, min(32767, int(right[i] * 32767))))
            w.writeframes(pcm.tobytes())

def main():
    number = int(Path(__file__).stem.split("-", 1)[0]) - 1
    song = make_song(SONGS[number])
    out = Path(__file__).resolve().parent
    stem = Path(__file__).stem
    (full, inst, seconds) = render_song(song)
    full_wav, inst_wav = out / (stem + ".wav"), out / (stem + "-instrumental.wav")
    full_mp3, inst_mp3 = out / (stem + ".mp3"), out / (stem + "-instrumental.mp3")
    write_wav(full_wav, *full); write_wav(inst_wav, *inst)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is needed only to encode the MP3 deliverables")
    for wav_path, mp3_path in ((full_wav, full_mp3), (inst_wav, inst_mp3)):
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", "192k", "-ar", str(SR), str(mp3_path)], check=True)
    if "--keep-wav" not in sys.argv:
        full_wav.unlink(missing_ok=True); inst_wav.unlink(missing_ok=True)
    print(f"{song['title']}: {seconds:.2f}s -> {full_mp3.name}, {inst_mp3.name}")

if __name__ == "__main__":
    main()
