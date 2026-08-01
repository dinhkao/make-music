#!/usr/bin/env python3
# =============================================================================
# IMAGO — an original song, built entirely from scratch.
#
#   ~ "the worm doesn't mourn the cocoon / it hums the same song underwater" ~
#
# Concept: at 3:03am a woman finds a copy of herself in the glass of her phone
# screen — already wearing her favorite dress backwards, already ahead of
# herself. The copy is the "imago": the final, adult form of an insect that
# has finished metamorphosis. She realizes the future self was built from her,
# not against her — "you're just me with better lighting."
#
# Inspired by the spirit of Magdalena Bay's "Imaginal Disk" (2024):
#   - extended minor-7th harmony wandering in verses, stark simple chorus loop
#   - chromatic passing chords (Bbm7, Bmaj7) and mode-mix (bVI, bVII) colors
#   - verse whisper -> disco 4-on-the-floor chorus -> prog drum "boss battle"
#   - sung melodic lines, CD-skip stutter, vinyl crackle bed
#   - a vulnerable ending: arp + bell + fade
#
# Everything here — engine, instruments, vocal formant synthesis, drums, mix —
# is original code written for this song. numpy + scipy only.
# Usage:  python3 imago.py            -> writes imago.wav
# =============================================================================

import re
import numpy as np
from scipy import signal as sg

SR = 44100
BPM = 100.0
BEAT = 60.0 / BPM          # 0.6 s per beat
BAR = 4.0                  # beats per bar
TOTAL = 187.0              # seconds of bus

# ------------------------------------------------------------------ helpers
def T(b):                  # beats -> seconds
    return b * BEAT

_NOTE = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
         'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
def midi(nm):
    m = re.match(r'([A-G][#b]?)(-?\d)', nm)
    return (int(m.group(2)) + 1) * 12 + _NOTE[m.group(1)]
def hz(nm):
    return 440.0 * 2 ** ((midi(nm) - 69) / 12.0)
def mhz(m):
    """midi number -> frequency"""
    return 440.0 * 2 ** ((m - 69) / 12.0)

class Bus:
    """stereo float64 mixing bus with equal-power pan"""
    def __init__(self, secs=TOTAL):
        n = int(secs * SR)
        self.L = np.zeros(n)
        self.R = np.zeros(n)
    def add(self, t, x, pan=0.0, gain=1.0):
        i0 = int(t * SR)
        n = len(x)
        if i0 >= len(self.L) or n == 0:
            return
        i1 = min(i0 + n, len(self.L))
        x = x[:i1 - i0] * gain
        gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.L[i0:i1] += x * gl
        self.R[i0:i1] += x * gr

def lp(x, cut, order=2):
    b, a = sg.butter(order, cut / (SR / 2), 'low')
    return sg.lfilter(b, a, x)

def hp(x, cut, order=2):
    b, a = sg.butter(order, cut / (SR / 2), 'high')
    return sg.lfilter(b, a, x)

def bp(x, lo, hi, order=2):
    b, a = sg.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return sg.lfilter(b, a, x)

def lpsweep(x, f0, f1, K=28):
    """lowpass with a slowly opening cutoff; hanning overlap-add of blocks"""
    n = len(x)
    if n == 0:
        return x
    seg = max(n // K, 4)
    hop = seg // 2
    out = np.zeros(n + seg)
    win = np.hanning(seg)
    for j in range(K):
        a0 = min(j * hop, n - 1)
        a1 = min(a0 + seg, n)
        if a1 <= a0:
            break
        cut = f0 * (f1 / f0) ** (j / max(K - 1, 1))
        piece = lp(x[a0:a1], cut)
        m = a1 - a0
        out[a0:a0 + m] += piece * win[:m]
    return out[:n]

def fades(x, a=0.02, r=0.1):
    na, nr = int(a * SR), int(r * SR)
    x = x.copy()
    x[:na] *= np.linspace(0, 1, na)
    x[-nr:] *= np.linspace(1, 0, nr)
    return x

# ------------------------------------------------------------- instruments
def pad(notes, dur, atk=0.8, cut=3600.0, det=9.0, seed=0, gain=1.0, sweep=0):
    """supersaw pad: 5 detuned saws per note, filtered, slow attack"""
    n = int(dur * SR) + int(0.15 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        f = mhz(m)
        ph = 2 * np.pi * f * t
        for d in (-det, -det * 0.45, 0.0, det * 0.45, det):
            out += sg.sawtooth(ph * 2 ** (d / 1200)) / 5.0
    out /= max(1, len(notes))
    out = np.tanh(out * 0.6)
    if sweep > 0:
        out = lpsweep(out, cut * 0.18, cut, K=sweep)
    else:
        out = lp(out, cut)
    e = np.minimum(1, t / atk) ** 1.5
    rel = int(min(0.25, dur) * SR)
    e[-rel:] *= np.linspace(1, 0, rel)
    return np.tanh(out * e * 0.8 * gain)

def padat(bus, t0, notes, dur, **kw):
    bus.add(t0, pad(notes, dur, **kw), gain=1.0)

def pluck(f, dur, gain=1.0, color=2.007):
    """FM-ish pluck: sine + slightly inharmonic second partial"""
    n = int(min(dur, 2.5) * SR)
    t = np.arange(n) / SR
    tau = 0.28 + 0.5 * min(dur, 2.5)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
    x += 0.35 * np.sin(2 * np.pi * f * color * t) * np.exp(-t / (tau * 0.55))
    x += 0.12 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / (tau * 0.35))
    return np.tanh(x * 1.3) * gain

def keys(f, dur, gain=1.0, idx=4.0):
    """FM tine keys: index-modulated sine + overtone, soft attack"""
    n = int(min(dur, 3.0) * SR)
    t = np.arange(n) / SR
    I = idx * np.exp(-t * 5.0)
    x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * 2 * t))
    x += 0.5 * np.sin(2 * np.pi * f * 4.01 * t) * np.exp(-t * 9.0)
    x *= np.exp(-t * (1.4 + 2.0 / max(dur, 0.2)))
    x *= np.minimum(1, t * 160)
    return np.tanh(x * 1.2) * gain

def bell(f, dur=2.6, gain=1.0):
    """FM bell for the ending"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    ei = 3.2 * np.exp(-t * 3.0)
    x = np.sin(2 * np.pi * f * t + ei * np.sin(2 * np.pi * f * 3.52 * t))
    x += 0.4 * np.sin(2 * np.pi * f * 2.02 * t) * np.exp(-t * 4.5)
    x *= np.exp(-t * 1.5)
    x *= np.minimum(1, t * 700)
    return np.tanh(x * 1.2) * gain

def bass(f, dur, gain=1.0, bright=0.25):
    """saw+sub bass with a short pluck envelope"""
    n = int(min(dur, 2.0) * SR)
    t = np.arange(n) / SR
    x = sg.sawtooth(2 * np.pi * f * t) * bright
    x += np.sin(2 * np.pi * f * t) * (1 - bright)
    x = lp(np.tanh(x * 1.8), 700 + 900 * bright)
    x *= np.exp(-t * (3.2 + 1.8 / max(dur, 0.4)))
    x *= np.minimum(1, t * 900)
    return x * gain

def bassat(bus, t0, mroot, dur, gain, bright=0.25):
    bus.add(t0, bass(mhz(mroot), dur, gain, bright))

def stab(notes, dur=0.8, gain=1.0, cut=2600.0):
    """orchestra-hit-ish string stab: detuned saws, fast attack, noise bite"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        f = mhz(m)
        for d in (-6, 0, 6, 11):
            out += sg.sawtooth(2 * np.pi * f * 2 ** (d / 1200)) / 4.0
    out = np.tanh(out * 0.8)
    out = lp(out, cut)
    rng = np.random.default_rng(42)
    bite = bp(rng.standard_normal(n), 1800, 6000) * np.exp(-t * 26)
    out += bite * 0.4
    e = np.minimum(1, t * 220) * np.exp(-t * (2.2 + 1.2 / max(dur, 0.5)))
    return out * e * gain

def riser(dur, gain=1.0, f0=250.0, f1=8200.0):
    """noise riser with swept bandpass and rising gain"""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    rng = np.random.default_rng(7)
    out = np.zeros(n)
    for k, fr in enumerate(np.geomspace(f0, f1, 8)):
        w = np.exp(-((t - k / 7.0) ** 2) / (2 * 0.10 ** 2))
        out += bp(rng.standard_normal(n), fr * 0.7, fr * 1.4) * w
    out *= t ** 2.2
    return out * gain

def blip(f, dur=0.32, gain=1.0):
    """soft sine chirp blip (system boot)"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * (1 + 0.02 * np.sin(2 * np.pi * 6 * t)) * t)
    x *= np.exp(-t * 9) * np.minimum(1, t * 400)
    return x * gain

def crackle(dur, gain=1.0, dens=0.035):
    """low vinyl crackle bed"""
    n = int(dur * SR)
    rng = np.random.default_rng(11)
    t = np.arange(n) / SR
    imp = (rng.random(n) < dens / 60).astype(float) * rng.standard_normal(n) * 2.5
    imp = sg.lfilter([1], [1, -0.5], imp)
    imp = bp(imp, 900, 8000)
    hiss = bp(rng.standard_normal(n), 400, 9000) * 0.09
    lfo = 1 + 0.3 * np.sin(2 * np.pi * 0.13 * t)
    return np.tanh((imp + hiss) * lfo * 0.8) * gain

# --------------------------------------------------------------- drums
def kick(f0=110.0, f1=43.0, dur=0.5, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 34)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 9)
    x *= np.minimum(1, t * 600)
    rng = np.random.default_rng(1)
    click = bp(rng.standard_normal(n), 2500, 9000) * np.exp(-t * 420) * 0.5
    return np.tanh((x + click) * 1.5) * vel

def snare(vel=1.0, ghost=False, dur=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(2)
    body = np.sin(2 * np.pi * 196 * t) * np.exp(-t * 24)
    noise = bp(rng.standard_normal(n), 1400, 7000) * np.exp(-t * 30)
    x = body * 0.5 + noise
    if ghost:
        x *= 0.4
        x = lp(x, 6000)
    return np.tanh(x * 1.6) * vel

def hat(vel=1.0, open_=False):
    dur = 0.5 if open_ else 0.07
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    x = bp(rng.standard_normal(n), 7000, 16000)
    x *= np.exp(-t * (18 if open_ else 90))
    return np.tanh(x * 1.4) * vel

def clap(vel=1.0):
    dur = 0.32
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(4)
    out = np.zeros(n)
    for off in (0.0, 0.010, 0.022):
        i0 = int(off * SR)
        seg = bp(rng.standard_normal(n - i0), 700, 4200) * np.exp(-np.arange(n - i0) / SR * 60)
        out[i0:] += seg
    return np.tanh(out * 1.5) * vel

def tom(f=140.0, vel=1.0):
    dur = 0.42
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    fgl = f * (1 + 0.5 * np.exp(-t * 30))
    ph = 2 * np.pi * np.cumsum(fgl) / SR
    x = np.sin(ph) * np.exp(-t * 8)
    x += bp(rng.standard_normal(n), 800, 3000) * np.exp(-t * 18) * 0.4
    return np.tanh(x * 1.4) * vel

def crash(vel=1.0):
    dur = 1.8
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(6)
    x = bp(rng.standard_normal(n), 3500, 14000) * np.exp(-t * 2.6)
    x += np.sin(2 * np.pi * 6300 * t) * np.exp(-t * 5) * 0.3
    return np.tanh(x * 1.2) * vel

def rim(vel=1.0):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(8)
    x = np.sin(2 * np.pi * 1150 * t) * np.exp(-t * 80)
    x += bp(rng.standard_normal(n), 1800, 6000) * np.exp(-t * 120) * 0.6
    return x * vel

# ------------------------------------------------------------ vocal synth
# vowel formants (F1 F2 F3) — my own table
VOW = {'a':(700,1150,2450), 'e':(500,1750,2500), 'i':(300,2100,2800),
       'o':(500,850,2400),  'u':(350,600,2400),  'uh':(600,1200,2500),
       'ay':(560,1800,2520), 'ai':(720,1350,2520), 'ow':(600,900,2360),
       'oi':(460,1050,2400)}
DIPHEND = {'ay':(300,2100,2800), 'ai':(300,2100,2800), 'ow':(350,600,2400),
           'oi':(300,2100,2800)}
# consonant recipes: (dur_s, band_low, band_high, noise_gain) — rough but mine
CONS = {'p':(0.030,1800,6000,0.8), 't':(0.035,3500,8000,0.9), 'k':(0.040,2000,7000,0.9),
        'b':(0.035,250,1500,0.9),  'd':(0.040,250,2000,0.9),  'g':(0.045,200,1800,0.9),
        's':(0.085,5000,11000,0.7),'sh':(0.10,2600,6500,0.7),  'z':(0.070,4300,9000,0.5),
        'f':(0.070,3800,8000,0.6), 'th':(0.075,3000,7000,0.6), 'v':(0.060,1600,4500,0.5),
        'ch':(0.090,2500,6500,0.8), 'j':(0.080,1600,4800,0.7), 'h':(0.050,1200,4200,0.5),
        'm':(0.075,400,1400,0.7),  'n':(0.070,600,2400,0.7),  'ng':(0.080,500,2000,0.7),
        'w':(0.045,500,1200,0.5),  'y':(0.040,1800,3200,0.4),  'r':(0.045,900,2000,0.5),
        'l':(0.050,700,2200,0.5),  'sk':(0.075,4500,9500,0.7), 'dr':(0.050,900,2400,0.7),
        'br':(0.050,500,1600,0.7), 'tr':(0.050,2200,5000,0.7), 'gr':(0.050,500,1800,0.7),
        'sp':(0.060,4000,9000,0.6), 'st':(0.060,4000,9000,0.6), 'ts':(0.040,4000,9000,0.5),
        'dz':(0.045,2000,5000,0.6), 'lf':(0.060,1500,5000,0.4), 'nd':(0.055,700,2500,0.5),
        'nt':(0.045,2000,6000,0.5), 'rt':(0.045,2500,6500,0.5), 'rs':(0.055,3000,7000,0.5),
        'rm':(0.060,500,1500,0.6),  'rk':(0.050,2000,6000,0.6), 'wn':(0.050,800,2600,0.5),
        'dl':(0.050,800,2400,0.5),  'rtz':(0.060,2500,7000,0.5)}
BRIGHT = {'croon':1.0, 'hush':0.9, 'shout':1.18}

def resonator(x, fc, bw):
    """cascadable bandpass biquad (RBJ cookbook)"""
    q = max(fc / bw, 0.5)
    w0 = 2 * np.pi * fc / SR
    alpha = np.sin(w0) / (2 * q)
    a0 = 1 + alpha
    b0 = alpha / a0; b1 = 0.0; b2 = -alpha / a0
    a1 = -2 * np.cos(w0) / a0; a2 = (1 - alpha) / a0
    return sg.lfilter([b0, b1, b2], [1.0, a1, a2], x)

def syll(f0, dur, onset, vowel, coda, gain=1.0, style='croon',
         breath=0.12, seed=0, detune=0.0, vib=5.3):
    """one sung syllable: glottal pulse train -> formant cascade -> consonants"""
    n = int(max(dur, 0.15) * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(900 + seed)
    # --- glottal source: jittered pulse train, vibrato, croon fall ---
    f = f0 * 2 ** (detune / 1200)
    vib_ = 1 + 0.006 * np.sin(2 * np.pi * vib * t + rng.uniform(0, 6.28)) * \
        np.clip((t - 0.12) * 3.0, 0, 1)
    fall = 1 - 0.030 * np.exp(-t * 7)
    farr = f * vib_ * fall
    ph = np.cumsum(farr) / SR
    k = np.floor(ph).astype(np.int64)
    edge = np.zeros(n, dtype=bool); edge[1:] = k[1:] != k[:-1]
    train = np.zeros(n); train[edge] = 1.0
    gl = np.exp(-np.arange(int(0.012 * SR)) / (0.0031 * SR))
    train = sg.fftconvolve(train, gl, 'same')
    train *= np.sqrt(farr / 200.0)               # keep loudness flat-ish
    train /= (np.max(np.abs(train)) + 1e-9)
    # --- vowel formants (diphthong = gliding between sets) ---
    fs = VOW.get(vowel, VOW['a'])
    vdur = max(dur - 0.02, 0.10)
    i0v = int((dur - vdur) * SR)
    seg = train[i0v:i0v + int(vdur * SR)]
    if vowel in DIPHEND:
        end = DIPHEND[vowel]
        blk = max(len(seg) // 24, 4)
        hop = blk // 2
        K = max(len(seg) // hop - 1, 1)
        win = np.hanning(blk)
        tmp = np.zeros(len(seg) + blk)
        for j in range(K):
            a0 = j * hop
            a1 = min(a0 + blk, len(seg))
            if a1 <= a0:
                break
            tt = (a0 + a1) / 2.0 / len(seg)
            F1 = fs[0] + (end[0] - fs[0]) * tt
            F2 = fs[1] + (end[1] - fs[1]) * tt
            F3 = fs[2] + (end[2] - fs[2]) * tt
            piece = resonator(resonator(resonator(seg[a0:a1], F1, 110 * (0.8 + 0.2 * tt)),
                                        F2, 220 * (0.8 + 0.2 * tt)), F3, 420)
            m = a1 - a0
            tmp[a0:a0 + m] += piece * win[:m]
        seg = tmp[:len(seg)]
    else:
        b = BRIGHT[style]
        seg = resonator(seg, fs[0], 110 * b)
        seg = resonator(seg, fs[1], 220 * b)
        seg = resonator(seg, fs[2], 420 * b)
    x = np.zeros(n)
    x[i0v:i0v + len(seg)] = seg
    # --- breath noise ---
    bn = bp(rng.standard_normal(n), 900, 4200) * (0.05 + breath * 0.5)
    x += bn
    # --- onset consonant ---
    if onset and onset in CONS:
        c = CONS[onset]; cn = int(c[0] * SR)
        cc = bp(rng.standard_normal(cn), c[1], c[2]) * c[3]
        x[:cn] += cc * np.minimum(1, np.arange(cn) / (0.008 * SR))
    # --- coda consonant ---
    if coda and coda in CONS:
        c = CONS[coda]; cn = int(c[0] * SR)
        cc = bp(rng.standard_normal(cn), c[1], c[2]) * c[3] * 0.8
        x[-cn:] += cc * np.minimum(1, np.arange(cn)[::-1] / (0.008 * SR))
    # --- syllable envelope ---
    a = 0.022 if style != 'hush' else 0.045
    e = np.minimum(1, t / a)
    rel = int(min(0.10, dur * 0.4) * SR)
    e[-rel:] *= np.linspace(1, 0, rel)
    return np.tanh(x * 1.4) * e * gain

STYLES = {'hush':(0.55, 0.32), 'croon':(0.95, 0.14), 'shout':(1.10, 0.26)}

def line(bus, t0_beats, events, gain=1.0, style='croon', seedbase=0):
    """place a sung line; events = (beat, dur, note, vowel, onset, coda)"""
    g0, br = STYLES.get(style, (0.9, 0.15))
    for (b, d, nm, vw, on, cd) in events:
        t = T(t0_beats + b)
        x = syll(hz(nm), d, on, vw, cd, gain=gain * g0,
                 style=style, breath=br, seed=seedbase + int(b * 100))
        bus.add(t, x, pan=-0.06)
        if style == 'shout':                     # wall-of-sound doubling
            for k, dd in ((1, 7.0), (2, -6.0)):
                y = syll(hz(nm), d, on, vw, cd, gain=gain * 0.34,
                         style=style, breath=br, seed=seedbase + int(b * 100) + k,
                         detune=dd, vib=5.3 + k)
                bus.add(t, y, pan=-0.12 + 0.12 * k)

# ---------------------------------------------------------------- reverb
def make_ir(dur=1.9, tau=0.62, seed=21):
    """synthetic hall impulse: dense tail + a few early taps, L2-normalized"""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / tau)
    ir = lp(ir, 7500)
    for off, g in ((0.023, 0.35), (0.037, 0.28), (0.051, 0.22), (0.073, 0.16),
                   (0.096, 0.12), (0.13, 0.09)):
        i0 = int(off * SR)
        ir[i0:i0 + 200] += g * np.exp(-np.arange(200) / (0.02 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))       # unit energy: convolution preserves level
    return ir

def reverb(x, wet=0.32):
    ir = make_ir()
    y = sg.fftconvolve(x, ir, 'same')
    return x * (1 - wet) + y * wet

# =======================================================================
# SONG — IMAGO (C minor, 100 bpm)
# =======================================================================
SECS = [('INTRO',8), ('V1',8), ('PRE',4), ('CH1',8), ('V2',8),
        ('BREAK',8), ('PRE2',4), ('CH2',8), ('BRIDGE',8), ('CH3',8), ('OUT',4)]
S = {}; _b = 0.0
for _n, _c in SECS:
    S[_n] = _b; _b += _c * BAR
END_BEATS = _b
DUR = T(END_BEATS)                       # ~182.4 s
print('IMAGO  bars', int(END_BEATS / BAR), ' duration', round(DUR, 1), 's')

# chords: (root MIDI, pad voicing, bass root MIDI)
CH = {
 'Cm7':  (36, (60,63,67,70), 36), 'Abmaj7': (44, (56,60,63,67), 44),
 'Fm7':  (41, (53,56,60,63), 41), 'G7':    (43, (55,59,62,65), 43),
 'Bb':   (46, (58,62,65,69), 46), 'Cm':    (36, (60,63,67,72), 36),
 'Bbm7': (46, (58,61,65,68), 46), 'Bbmaj7':(46, (58,62,65,69), 46),
 'Bmaj7':(47, (59,63,66,70), 47), 'Bm7b5': (47, (47,50,53,57), 47),
 'Fm7b5':(41, (53,56,59,62), 41), 'Ab':    (44, (56,60,63,67), 44),
}
VP1 = ['Cm7','Abmaj7','Fm7','G7']       # V1:  i - bVI - iv - V7
VP2 = ['Cm7','Abmaj7','Bbm7','G7']      # V2:  chromatic bVIIm in
PP  = ['Fm7','Abmaj7','Bbmaj7','G7']    # PRE: rising 4-bars
CP  = ['Cm','Ab','Bb','G7']             # CH:  stark simple loop
BRKP= ['Fm7','Abmaj7','Bbmaj7','Bmaj7'] # BREAK: bVII# chromatic climb
BRP = ['Cm7','Bm7b5','Bbmaj7','Abmaj7'] # BRIDGE: chromatic descent
def bar_at(sec, i): return S[sec] + i * BAR

bus = Bus(); drm = Bus(); vx = Bus()

# ------------------------------------------------------------ arrangement
cr = crackle(T(END_BEATS) + 3, 0.045, 0.035)          # vinyl bed all along
bus.add(0, cr, gain=1.0)

# ---- INTRO: dark boot. ticks -> blips -> pad opening, arp ----
for i in range(8):
    b = bar_at('INTRO', i)
    if i >= 1:                                          # system clock ticks
        for p in range(4):
            drm.add(T(b + p), hat(0.30 if i < 6 else 0.42))
    if i == 0:
        for p, f in ((0.0, 523.25), (0.9, 659.25), (1.8, 783.99)):
            bus.add(T(b + p), blip(f), pan=0.15, gain=0.35)
    if i >= 2:
        root, voic, brt = CH['Cm7']
        padat(bus, T(b), [m + 12 for m in voic], 2.3, atk=1.6, cut=2600,
              seed=i, gain=0.22, sweep=26)
        for p, m in enumerate([voic[0], voic[1], voic[2], voic[3], voic[2], voic[1]]):
            bus.add(T(b + p * 0.5), pluck(mhz(m + 12), 1.1, 0.34),
                    pan=0.25 if p % 2 else -0.25)
    if i == 5:
        drm.add(T(b + 1), riser(2.4, 0.05, 200, 5000))

# ---- V1: hushed vocal, sparse groove ----
V1 = [
 # "i woke up at three oh three"
 [(0,.5,'C4','ai','',''),(.5,.5,'D4','ow','w',''),(1,.5,'Eb4','u','','p'),
  (1.5,.5,'D4','a','','t'),(2,.5,'Eb4','i','th',''),(2.5,.5,'D4','o','',''),
  (3,.5,'Eb4','i','th',''),(3.5,.5,'C4','i','th','')],
 # "the sky was installing itself"
 [(0,.5,'G4','e','th',''),(.5,.5,'G4','ai','sk',''),(1,.5,'Eb4','uh','w','z'),
  (1.5,.5,'F4','i','','n'),(2,.5,'G4','o','st',''),(2.5,.5,'F4','i','','ng'),
  (3,.5,'Eb4','i','','t'),(3.5,.5,'D4','e','s','lf')],
 # "copy of me on the ceiling"
 [(0,.5,'Ab4','o','k',''),(.5,.5,'Ab4','i','p',''),(1,.5,'F4','o','','v'),
  (1.5,.5,'G4','i','m',''),(2,.5,'Eb4','o','','n'),(2.5,.5,'D4','e','th',''),
  (3,.5,'Eb4','i','s','l'),(3.5,.5,'C4','i','','ng')],
 # "already ahead of herself"
 [(0,.5,'F4','a','','l'),(.5,.5,'G4','i','r',''),(1,.5,'F4','i','',''),
  (1.5,.5,'Eb4','e','',''),(2,.5,'G4','e','h',''),(2.5,.5,'F4','o','','v'),
  (3,.5,'Eb4','e','h',''),(3.5,.5,'D4','e','s','lf')],
 # "she wears my favorite dress"
 [(0,.5,'G4','i','sh',''),(.5,.5,'Ab4','i','w','z'),(1,.5,'G4','ai','m',''),
  (1.5,.5,'F4','a','f',''),(2,.5,'G4','o','v',''),(2.5,.5,'Ab4','ai','r',''),
  (3,1,'Ab4','e','dr','s')],
 # "backwards, like she already knows"
 [(0,.5,'Ab4','a','b','k'),(.5,.5,'G4','u','w','dz'),(1,.5,'F4','ai','l',''),
  (1.5,.5,'G4','i','sh',''),(2,.5,'Ab4','a','','l'),(2.5,.5,'G4','i','r',''),
  (3,.5,'F4','i','',''),(3.5,.5,'G4','ow','n','z')],
 # "every word i'm about to say"
 [(0,.5,'G4','e','','v'),(.5,.5,'F4','i','r',''),(1,.5,'Ab4','u','w',''),
  (1.5,.5,'G4','ai','','m'),(2,.5,'F4','e','',''),(2.5,.5,'G4','ow','b','t'),
  (3,.5,'Eb4','u','t',''),(3.5,.5,'G4','ay','s','')],
 # "before i let it go"
 [(0,.5,'Eb4','i','b',''),(.5,.5,'F4','o','f',''),(1,.5,'G4','ai','',''),
  (1.5,.5,'Ab4','e','l',''),(2,.5,'G4','i','','t'),(2.5,1,'F4','o','g','')],
]
for i in range(8):
    b = bar_at('V1', i)
    chord = VP1[i % 4]; root, voic, brt = CH[chord]
    padat(bus, T(b), [m + 12 for m in voic], 2.0, atk=0.8, cut=2600, seed=i, gain=0.14)
    bassat(bus, T(b), mhz(brt), 1.1, 0.20)
    bassat(bus, T(b + 2.5), mhz(brt), 0.5, 0.14)
    if i % 2 == 0:
        bus.add(T(b + 0.5), pluck(mhz(voic[1] + 12), 1.2, 0.16), pan=-0.3)
    if i % 2 == 0:
        drm.add(T(b + 0), kick(vel=0.55)); drm.add(T(b + 2.5), kick(vel=0.4))
        drm.add(T(b + 1.5), snare(vel=0.5)); drm.add(T(b + 3.5), snare(0.22, ghost=True))
        for p in range(4):
            drm.add(T(b + p), hat(0.16))
            drm.add(T(b + p + 0.5), hat(0.26, open_=(p == 3)))
    else:
        drm.add(T(b), kick(vel=0.4))
        for p in range(4):
            drm.add(T(b + p + 0.5), hat(0.16))
    if i == 7:
        drm.add(T(b + 3.2), riser(2.2, 0.05, 250, 5000))
    line(vx, b, V1[i], gain=0.8, style='hush', seedbase=100 + i * 17)

# ---- PRE: keys come in, rising ----
PRE = [
 # "and she says, don't be scared"
 [(0,.5,'F4','a','','n'),(.5,.5,'G4','i','sh',''),(1,.5,'G4','ay','s','z'),
  (1.5,.5,'Ab4','o','d','t'),(2,.5,'Bb4','i','b',''),(2.5,1.5,'Bb4','e','sk','d')],
 # "this is where the skin comes off"
 [(0,.5,'Bb4','i','th','s'),(.5,.5,'Ab4','i','','z'),(1,.5,'G4','e','w',''),
  (1.5,.5,'G4','e','th',''),(2,.5,'Ab4','i','sk',''),(2.5,.5,'Bb4','u','k','m'),
  (3,.5,'C5','o','','f')],
 # "it's not dying, it's arriving"
 [(0,.5,'C5','i','','ts'),(.5,.5,'D5','o','n','t'),(1,.5,'Eb5','ai','d',''),
  (1.5,.5,'Eb5','i','','ng'),(2,.5,'D5','i','','ts'),(2.5,.5,'Eb5','a','',''),
  (3,.5,'F5','i','r',''),(3.5,.5,'Eb5','i','','ng')],
 [],
]
for i in range(4):
    b = bar_at('PRE', i)
    chord = PP[i]; root, voic, brt = CH[chord]
    padat(bus, T(b), [m + 12 for m in voic], 2.0, atk=0.4, cut=3400 + 500 * i,
          seed=30 + i, gain=0.20)
    bus.add(T(b), keys(mhz(voic[0] + 12), 2.0, 0.24), pan=-0.2)
    bus.add(T(b + 1.5), keys(mhz(voic[2] + 12), 1.8, 0.18), pan=0.2)
    bassat(bus, T(b), mhz(brt), 0.9, 0.24)
    bassat(bus, T(b + 2), mhz(brt + 12), 0.7, 0.18)
    for p in range(4):
        drm.add(T(b + p), hat(0.20))
        drm.add(T(b + p + 0.5), hat(0.30, open_=(p == 3)))
    drm.add(T(b + 0), kick(vel=0.6)); drm.add(T(b + 2), kick(vel=0.5))
    drm.add(T(b + 3), kick(vel=0.5)); drm.add(T(b + 1.5), snare(vel=0.6))
    drm.add(T(b + 3.5), snare(vel=0.4))
    if i == 2:
        drm.add(T(b + 1.0), riser(2.8, 0.07, 300, 7000))
    if i < 3:
        line(vx, b, PRE[i], gain=0.95, style='croon', seedbase=300 + i * 17)
drm.add(T(S['PRE'] + 4 * BAR - 0.05), crash(0.8))

# ---- CH1: disco 4-on-the-floor, stark loop ----
HOOK = [
 [(0,.75,'Eb5','i','',''),(.75,.75,'D5','a','m',''),(1.5,.5,'C5','o','g',''),
  (2,.5,'Eb5','i','',''),(2.5,.5,'D5','a','m',''),(3,.75,'C5','o','g','')],
 [(0,.5,'D5','u','y','r'),(.5,.5,'C5','u','j','t'),(1,.5,'C5','i','m',''),
  (1.5,.5,'Bb4','i','w','th'),(2,.5,'Bb4','e','b','t'),(2.5,.5,'C5','e','t','r'),
  (3,.5,'D5','ai','l','t'),(3.5,.5,'C5','i','','ng')],
 [(0,.75,'Eb5','i','',''),(.75,.75,'D5','a','m',''),(1.5,.5,'C5','o','g',''),
  (2,.5,'Bb4','i','',''),(2.5,.5,'C5','a','m',''),(3,.75,'D5','o','g','')],
 [(0,.5,'D5','ay','s','m'),(.5,.5,'D5','ow','','l'),(1,.5,'C5','i','dr',''),
  (1.5,.5,'C5','u','b','t'),(2,.5,'Bb4','i','','ts'),(2.5,.5,'C5','ow','g','r'),
  (3,.5,'D5','i','','ng'),(3.5,.5,'Eb5','i','w','ng')],
 [(0,.75,'Eb5','i','',''),(.75,.75,'D5','a','m',''),(1.5,.5,'C5','o','g',''),
  (2,.5,'Eb5','i','',''),(2.5,.5,'D5','a','m',''),(3,.75,'C5','o','g','')],
 [(0,.5,'D5','ai','','m'),(.5,.5,'C5','o','n','t'),(1,.5,'C5','u','n',''),
  (1.5,.5,'Bb4','ai','','m'),(2,.5,'Bb4','u','j','t'),(2.5,.5,'C5','i','f',''),
  (3,.5,'D5','i','n',''),(3.5,.5,'C5','e','sh','d')],
 [(0,.75,'Eb5','i','',''),(.75,.75,'D5','a','m',''),(1.5,.5,'C5','o','g',''),
  (2,.5,'Eb5','i','',''),(2.5,.5,'D5','a','m',''),(3,.75,'F5','o','g','')],
 [(0,.5,'D5','u','l','k'),(.5,.5,'Eb5','u','h',''),(1,.5,'F5','i','f',''),
  (1.5,.5,'Eb5','a','n',''),(2,.5,'D5','i','l',''),(2.5,.5,'C5','u','l','nd'),
  (3,.5,'D5','u','t',''),(3.5,.5,'Eb5','i','s','ng')],
]
def chorus(b, i):
    chord = CP[i % 4]; root, voic, brt = CH[chord]
    padat(bus, T(b), [m + 12 for m in voic], 2.0, atk=0.12, cut=5600, seed=60 + i,
          gain=0.24)
    for p in range(4):                                    # disco octave bass
        bassat(bus, T(b + p), mhz(brt), 0.45, 0.30)
        bassat(bus, T(b + p + 0.5), mhz(brt + 12), 0.4, 0.24)
    bus.add(T(b), keys(mhz(voic[0] + 12), 1.4, 0.20), pan=-0.25)
    for p in range(4):                                    # 4-on-the-floor
        drm.add(T(b + p), kick(vel=0.9 if p % 2 == 0 else 0.75))
    drm.add(T(b + 1.5), snare(vel=0.85)); drm.add(T(b + 3.5), snare(vel=0.75))
    drm.add(T(b + 1.5), clap(0.6)); drm.add(T(b + 3.5), clap(0.5))
    for p in range(4):
        drm.add(T(b + p), hat(0.35))
        drm.add(T(b + p + 0.5), hat(0.55, open_=(p % 2 == 1)))
    if i % 4 == 0:
        drm.add(T(b), crash(0.7))
for i in range(8):
    b = bar_at('CH1', i)
    chorus(b, i)
    line(vx, b, HOOK[i], gain=1.0, style='shout', seedbase=500 + i * 17)
drm.add(T(S['CH1'] + 7 * BAR + 3.4), riser(2.0, 0.06, 250, 5500))

# ---- V2: fuller vocal, chromatic bVIIm ----
for i in range(8):
    b = bar_at('V2', i)
    chord = VP2[i % 4]; root, voic, brt = CH[chord]
    padat(bus, T(b), [m + 12 for m in voic], 2.0, atk=0.6, cut=3000, seed=90 + i,
          gain=0.18)
    bassat(bus, T(b), mhz(brt), 1.0, 0.24)
    bassat(bus, T(b + 2.5), mhz(brt), 0.5, 0.18)
    if i % 2 == 0:
        bus.add(T(b + 0.5), pluck(mhz(voic[1] + 12), 1.2, 0.18), pan=0.3)
    if i % 4 == 2:
        bus.add(T(b), keys(mhz(voic[2] + 12), 1.6, 0.14), pan=-0.3)
    drm.add(T(b + 0), kick(vel=0.7)); drm.add(T(b + 2.5), kick(vel=0.55))
    drm.add(T(b + 1.5), snare(vel=0.6)); drm.add(T(b + 3.5), snare(0.3, ghost=True))
    for p in range(4):
        drm.add(T(b + p), hat(0.18))
        drm.add(T(b + p + 0.5), hat(0.28, open_=(p == 3)))
    line(vx, b, V1[i], gain=0.95, style='croon', seedbase=700 + i * 17)

# ---- BREAK: prog drum battle, string stabs, chromatic climb ----
for i in range(8):
    b = bar_at('BREAK', i)
    chord = BRKP[i % 4]; root, voic, brt = CH[chord]
    for p, mlist in ((1.0, voic), (3.0, [m + 3 for m in voic])):
        bus.add(T(b + p), stab(mlist, 0.9, 0.20, cut=2400 + 500 * i), pan=-0.2)
    bassat(bus, T(b + 1), mhz(brt), 0.8, 0.34)
    bassat(bus, T(b + 3), mhz(brt), 0.8, 0.34)
    for p in range(4):
        drm.add(T(b + p), kick(vel=0.95 if p % 2 == 0 else 0.8))
        drm.add(T(b + p), hat(0.42))
    drm.add(T(b + 1.5), snare(vel=0.9)); drm.add(T(b + 3.5), snare(vel=0.9))
    drm.add(T(b + 0.5), clap(0.5)); drm.add(T(b + 2.5), clap(0.5))
    if i % 2 == 0:
        drm.add(T(b), crash(0.9))
    if i in (1, 3, 5):                                    # tom runs
        for k, ff in enumerate((90, 115, 145, 180)):
            drm.add(T(b + k * 0.5 + 2.0), tom(f=ff, vel=0.7))
    if i == 6:                                            # snare build
        for k in range(16):
            drm.add(T(b + k * 0.25), snare(vel=0.3 + 0.05 * k))
    if i == 7:                                            # full roll + crash
        for k in range(24):
            drm.add(T(b + k * 0.1667), snare(vel=0.75))
        drm.add(T(b + 3.5), crash(1.0))
        bus.add(T(b + 3.3), riser(1.4, 0.10, 500, 9000))

# ---- PRE2: bigger pre, all in ----
for i in range(4):
    b = bar_at('PRE2', i)
    chord = PP[i]; root, voic, brt = CH[chord]
    padat(bus, T(b), [m + 12 for m in voic], 2.0, atk=0.25, cut=4600 + 600 * i,
          seed=130 + i, gain=0.24)
    bus.add(T(b), keys(mhz(voic[0] + 12), 2.0, 0.26), pan=-0.2)
    bus.add(T(b + 1.5), keys(mhz(voic[2] + 12), 1.8, 0.20), pan=0.2)
    bassat(bus, T(b), mhz(brt), 0.9, 0.28)
    bassat(bus, T(b + 2), mhz(brt + 12), 0.7, 0.20)
    for p in range(4):
        drm.add(T(b + p), kick(vel=0.75)); drm.add(T(b + p), hat(0.26))
    drm.add(T(b + 1.5), snare(vel=0.75)); drm.add(T(b + 3.5), snare(vel=0.6))
    if i == 2:
        drm.add(T(b + 1.0), riser(2.8, 0.09, 300, 8000))
    if i < 3:
        line(vx, b, PRE[i], gain=1.05, style='croon', seedbase=900 + i * 17)
drm.add(T(S['PRE2'] + 4 * BAR - 0.05), crash(0.9))

# ---- CH2: choir octave joins ----
for i in range(8):
    b = bar_at('CH2', i)
    chorus(b, i)
    line(vx, b, HOOK[i], gain=1.05, style='shout', seedbase=1100 + i * 17)
    for ev in HOOK[i]:                                    # octave halo
        t = T(b + ev[0])
        mm = re.match(r'([A-G][#b]?)(\d+)', ev[2])
        nm = mm.group(1) + str(int(mm.group(2)) + 1)
        x = syll(hz(nm), ev[1], ev[4], ev[3], ev[5], gain=0.16, style='shout',
                 breath=0.2, seed=2000 + int(ev[0] * 100), vib=5.6)
        vx.add(t, x, pan=0.2)

# ---- BRIDGE: stripped, descending, stutter ----
BR = [
 # "the worm doesn't mourn"
 [(0,1,'G4','e','th',''),(1,.75,'C5','u','w','m'),(1.75,.5,'D5','u','d','z'),
  (2.25,.25,'D5','i','n','t'),(2.5,1.5,'C5','o','m','')],
 # "it hums the same song underwater"
 [(0,.5,'C5','i','','t'),(.5,.5,'D5','u','h','m'),(1,.5,'Eb5','e','th',''),
  (1.5,.5,'Eb5','ay','s','m'),(2,.75,'D5','o','s','ng'),(2.75,.25,'C5','u','','n'),
  (3,.25,'Bb4','e','d','r'),(3.25,.25,'C5','o','w',''),(3.5,.25,'D5','e','t','')],
 # "every version is a true one"
 [(0,.5,'G4','e','','v'),(.5,.5,'Bb4','i','r',''),(1,.5,'C5','u','v',''),
  (1.5,.5,'D5','o','sh','n'),(2,.5,'C5','i','','z'),(2.5,.5,'Bb4','e','',''),
  (3,.5,'C5','u','tr',''),(3.5,.5,'Eb5','u','w','n')],
 # "waiting for her turn"
 [(0,.5,'D5','ay','w','t'),(.5,.5,'C5','i','','ng'),(1,.75,'Bb4','o','f','r'),
  (1.75,.75,'C5','e','h','r'),(2.5,1.5,'D5','u','t','n')],
 # "and i don't need to be better"
 [(0,.5,'Eb5','a','','n'),(.5,.5,'D5','ai','',''),(1,.5,'C5','o','d','t'),
  (1.5,.5,'Eb5','i','n',''),(2,.5,'D5','u','t',''),(2.5,.5,'C5','i','b',''),
  (3,.5,'Bb4','e','b','t'),(3.5,.5,'C5','e','t','')],
 # "i just need to be this"
 [(0,.5,'C5','ai','',''),(.5,.5,'D5','u','j','t'),(1,.5,'Eb5','i','n',''),
  (1.5,.5,'D5','u','t',''),(2,.5,'C5','i','b',''),(2.5,1.5,'Bb4','i','th','s')],
 # "hold the mirror up to the sky"
 [(0,.5,'D5','o','h','l'),(.5,.5,'Eb5','e','th',''),(1,.5,'F5','i','m',''),
  (1.5,.5,'Eb5','e','r',''),(2,.5,'D5','u','','p'),(2.5,.5,'C5','u','t',''),
  (3,.5,'D5','e','th',''),(3.5,.5,'Eb5','ai','sk','')],
 # "say hello to all the me's i've been"
 [(0,.5,'C5','e','h','l'),(.5,.5,'D5','o','l',''),(1,.5,'Eb5','u','t',''),
  (1.5,.5,'D5','o','','l'),(2,.5,'C5','e','th',''),(2.5,.5,'Bb4','i','m','z'),
  (3,.5,'C5','ai','','v'),(3.5,.5,'D5','i','b','')],
]
for i in range(8):
    b = bar_at('BRIDGE', i)
    chord = BRP[i % 4]; root, voic, brt = CH[chord]
    padat(bus, T(b), [m + 12 for m in voic], 2.0, atk=1.2, cut=2400, seed=150 + i,
          gain=0.15)
    bassat(bus, T(b), mhz(brt), 2.0, 0.16)
    bus.add(T(b + 1), keys(mhz(voic[0] + 12), 2.4, 0.15), pan=-0.2)
    for p in (0, 1, 2, 3):
        drm.add(T(b + p), hat(0.10))
        drm.add(T(b + p + 0.5), rim(0.35))
    drm.add(T(b + 2.5), tom(f=92, vel=0.5))
    if i in (1, 3, 5):
        drm.add(T(b + 1.5), snare(vel=0.35))
    line(vx, b, BR[i], gain=1.0, style='croon', seedbase=1300 + i * 17)
# CD-skip stutter on the pad in bridge bar 7 (my own digital artifact)
b7 = bar_at('BRIDGE', 7)
seg = pad([m + 12 for m in CH['Cm7'][1]], 0.5, atk=0.01, cut=3200, seed=77, gain=0.30)
for k in range(6):
    bus.add(T(b7 + 2.0 + k * 0.065), seg[:int(0.09 * SR)] if k % 2 else seg)
bus.add(T(b7 + 2.6), riser(1.6, 0.10, 400, 8800))

# ---- CH3: everything, peak, brief high note ----
for i in range(8):
    b = bar_at('CH3', i)
    chorus(b, i)
    ev = HOOK[i]
    if i == 7:
        ev = [(e[0], e[1], 'G5' if e[2] == 'Eb5' and e[3] == 'i' else e[2],
               e[3], e[4], e[5]) for e in ev]
    line(vx, b, ev, gain=1.1, style='shout', seedbase=1600 + i * 17)
    for e in ev:
        t = T(b + e[0])
        mm = re.match(r'([A-G][#b]?)(\d+)', e[2])
        nm = mm.group(1) + str(int(mm.group(2)) + 1)
        x = syll(hz(nm), e[1], e[4], e[3], e[5], gain=0.20, style='shout',
                 breath=0.2, seed=3000 + int(e[0] * 100), vib=5.6)
        vx.add(t, x, pan=0.2)
    if i % 2 == 0:
        drm.add(T(b), crash(0.85))

# ---- OUT: vulnerability. arp + bell + fade ----
for i in range(4):
    b = bar_at('OUT', i)
    root, voic, brt = CH['Cm7']
    padat(bus, T(b), [m + 12 for m in voic], 2.3, atk=1.4, cut=2400, seed=200 + i,
          gain=0.13, sweep=20)
    for p, m in enumerate([voic[0], voic[1], voic[2], voic[3], voic[2], voic[1],
                           voic[0], voic[1]]):
        bus.add(T(b + p * 0.5), pluck(mhz(m + 12), 1.2, 0.22),
                pan=0.25 if p % 2 else -0.25)
    if i < 2:
        drm.add(T(b + 0), kick(vel=0.30)); drm.add(T(b + 2), kick(vel=0.25))
        drm.add(T(b + 0.5), hat(0.15))
        drm.add(T(b + 2.5), hat(0.15))
# final sung "imago" — slow, then a last bell
b0 = bar_at('OUT', 0)
for (p, d, nm, vw, on, cd) in [(0,1.5,'Eb5','i','',''),(1.5,1,'D5','a','m',''),
                               (2.5,1.5,'C5','o','g','')]:
    x = syll(hz(nm), d, on, vw, cd, gain=0.60, style='croon', breath=0.2,
             seed=4100 + int(p * 100), vib=5.0)
    vx.add(T(b0 + p), x, pan=-0.06)
# whisper echo "imago" near the end
for (p, d, nm, vw, on, cd) in [(0,1.4,'Eb5','i','',''),(1.4,1,'D5','a','m',''),
                               (2.4,1.6,'C5','o','g','')]:
    x = syll(hz(nm), d, on, vw, cd, gain=0.28, style='hush', breath=0.4,
             seed=4300 + int(p * 100), vib=4.6)
    vx.add(T(bar_at('OUT', 2) + p), x, pan=0.25)
bus.add(T(bar_at('OUT', 3) + 2.0), bell(hz('C5'), 3.2, 0.14))

# ================================================================= mix
drmL = reverb(drm.L, 0.22); drmR = reverb(drm.R, 0.22)
vxL = reverb(vx.L, 0.42); vxR = reverb(vx.R, 0.42)

L = bus.L * 0.42 + drmL * 0.30 + vxL * 0.50
R = bus.R * 0.42 + drmR * 0.30 + vxR * 0.50
L = lp(L, 15500); R = lp(R, 15500)
g = np.tanh(1.35)
L = np.tanh(L * 1.35) / g; R = np.tanh(R * 1.35) / g
pk = max(np.max(np.abs(L)), np.max(np.abs(R)))
L *= 0.92 / pk; R *= 0.92 / pk
n = int(DUR * SR)
L = L[:n]; R = R[:n]
fade_in = int(0.125 * SR)
L[:fade_in] *= np.linspace(0, 1, fade_in)
R[:fade_in] *= np.linspace(0, 1, fade_in)
fade = int(3.0 * SR)
L[-fade:] *= np.linspace(1, 0, fade) ** 1.3
R[-fade:] *= np.linspace(1, 0, fade) ** 1.3

st = np.stack([L, R], axis=1).astype(np.float32)
import wave
w = wave.open('imago.wav', 'wb')
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype('<i2').tobytes())
w.close()
print('written imago.wav', round(n / SR, 1), 's, peak', round(pk, 3))
