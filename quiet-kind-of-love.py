#!/usr/bin/env python3
# =============================================================================
# AIRBORNE — a Westlife-style power ballad, harmony from Smashing Pumpkins
# "1979", drums in the style of Nick Villa (Magdalena Bay's Imaginal Disk).
#
#   ~ "hold me like the morning / till i touch the clouds" ~
#
# Why it is written the way it is (researched, not invented):
#
# WESTLIFE SONGWRITING (their #1s: Swear It Again, Flying Without Wings,
# My Love, You Raise Me Up...):
#   - power ballad form: sparse verse -> rising pre-chorus -> full chorus
#   - the "elevating modulation": final chorus key change up a whole step
#     ("My Love" goes C -> D for the last chorus)
#   - a cappella / voice-first intros, 4-part harmony stacks on the hook,
#     bridge stripped back then rebuilt, chorus hook repeated and re-sung
#     higher at the end
#   - melody flow: syllabic verse, pre-chorus sequences up a step each bar,
#     chorus = big leap up to a held note, cascading release
#
# HARMONY — Smashing Pumpkins "1979" (1995, key A), a well-defined 90s
# alternative progression, transposed to G (verse) / D (chorus):
#   verse:  A - Emaj7 - E - A - Emaj7 - E - A - F#m7 - B      (I - V7 - V ...)
#           -> G - Dmaj7 - D - G - Dmaj7 - D - G - Em7 - A
#   chorus: E - Emaj7 - Amaj7 (x3) - F#m7 - B - E             (a fifth down)
#           -> D - Dmaj7 - Gmaj7 ... - Em7 - A - D
#   bridge: C#m - A - B - C#m - B - C#m - A - F#m7 - B        (vi - IV - V)
#           -> Em - G - A - Em - A - Em - G - Em7 - A
#   coda:   A - Emaj7 - E - A - E
# The maj7-on-the-V and maj7 washes are the song's whole identity.
#
# DRUMS — Nick Villa (touring drummer for Magdalena Bay, ex-Tabula Rasa):
# the Imaginal Disk record replaced programmed drums with live ones; the
# sound is busy, thunderous, human, with disco four-on-the-floor moments
# (Cry For Me, That's My Floor) and "stutter-stepping" grooves. So:
#   - verses: syncopated off-beat kicks, no straight 1-3 pumping
#   - pre-chorus: kick creeps toward 4-on-the-floor, tom fill out
#   - chorus: disco 4-on-floor with velocity lift, snare 2&4 + ghost notes,
#     claps doubling the backbeat, open hat on the "and of 4", 16th-note
#     stutter endings, tom runs into the next section
#   - bridge: cross-stick rim groove, then snare 16th build + roll
#
# All instruments are synthesis functions built earlier in this project
# (pad / pluck / keys / bell / bass / stab / riser / blip / crackle, the
# modal drum kit, the formant vocal synth, the L2-normalized reverb IR).
# numpy + scipy only.  Usage:  python3 airborne.py
# Writes airborne.wav and airborne-instrumental.wav (both, one run).
# =============================================================================

import re
import numpy as np
from scipy import signal as sg

SR = 44100
BPM = 80.0
BEAT = 60.0 / BPM          # 0.75 s per beat
BAR = 4.0
DUR = 180.0                # placeholder, body redefines
TOTAL = DUR + 3.5          # bus length: reverb tail headroom

# ------------------------------------------------------------------ helpers
def T(b):
    return b * BEAT

_NOTE = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
         'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def midi(nm):
    m = re.match(r'([A-G][#b]?)(-?\d)', nm)
    return (int(m.group(2)) + 1) * 12 + _NOTE[m.group(1)]
def hz(nm):
    return 440.0 * 2 ** ((midi(nm) - 69) / 12.0)
def mhz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)
def name(m):
    return _NAMES[m % 12] + str(m // 12 - 1)

class Bus:
    """stereo float64 mixing bus with equal-power pan"""
    def __init__(self, secs=None):
        if secs is None:
            secs = TOTAL
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
    """FM bell"""
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

def bassat(bus, t0, mroot, dur, gain, bright=0.3):
    """place bass from a MIDI root (correct: one mhz() conversion)"""
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
    """soft sine chirp blip"""
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
VOW = {'a':(700,1150,2450), 'e':(500,1750,2500), 'i':(300,2100,2800),
       'o':(500,850,2400),  'u':(350,600,2400),  'uh':(600,1200,2500),
       'ay':(560,1800,2520), 'ai':(720,1350,2520), 'ow':(600,900,2360),
       'oi':(460,1050,2400)}
DIPHEND = {'ay':(300,2100,2800), 'ai':(300,2100,2800), 'ow':(350,600,2400),
           'oi':(300,2100,2800)}
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
STYLES = {'hush':(0.55, 0.32), 'croon':(0.95, 0.14), 'shout':(1.10, 0.26)}

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
    train *= np.sqrt(farr / 200.0)
    train /= (np.max(np.abs(train)) + 1e-9)
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
    bn = bp(rng.standard_normal(n), 900, 4200) * (0.05 + breath * 0.5)
    x += bn
    if onset and onset in CONS:
        c = CONS[onset]; cn = int(c[0] * SR)
        cc = bp(rng.standard_normal(cn), c[1], c[2]) * c[3]
        x[:cn] += cc * np.minimum(1, np.arange(cn) / (0.008 * SR))
    if coda and coda in CONS:
        c = CONS[coda]; cn = int(c[0] * SR)
        cc = bp(rng.standard_normal(cn), c[1], c[2]) * c[3] * 0.8
        x[-cn:] += cc * np.minimum(1, np.arange(cn)[::-1] / (0.008 * SR))
    a = 0.022 if style != 'hush' else 0.045
    e = np.minimum(1, t / a)
    rel = int(min(0.10, dur * 0.4) * SR)
    e[-rel:] *= np.linspace(1, 0, rel)
    return np.tanh(x * 1.4) * e * gain

def line(bus, t0_beats, events, gain=1.0, style='croon', seedbase=0):
    """place a sung line; events = (beat, dur, note, vowel, onset, coda)"""
    g0, br = STYLES.get(style, (0.9, 0.15))
    for (b, d, nm, vw, on, cd) in events:
        t = T(t0_beats + b)
        x = syll(hz(nm), d, on, vw, cd, gain=gain * g0,
                 style=style, breath=br, seed=seedbase + int(b * 100))
        bus.add(t, x, pan=-0.06)
        if style == 'shout':
            for k, dd in ((1, 7.0), (2, -6.0)):
                y = syll(hz(nm), d, on, vw, cd, gain=gain * 0.34,
                         style=style, breath=br, seed=seedbase + int(b * 100) + k,
                         detune=dd, vib=5.3 + k)
                bus.add(t, y, pan=-0.12 + 0.12 * k)

def shift(events, semis):
    """transpose an event list by semis (note names stay valid)"""
    return [(b, d, name(midi(nm) + semis), vw, on, cd) for (b, d, nm, vw, on, cd) in events]

def halo(bus, t0_beats, events, gain=0.13, seedbase=2000):
    """airy octave-above echo of a line (Westlife air layer)"""
    for (b, d, nm, vw, on, cd) in events:
        x = syll(hz(name(midi(nm) + 12)), d, on, vw, cd, gain=gain,
                 style='shout', breath=0.2, seed=seedbase + int(b * 100), vib=5.6)
        bus.add(T(t0_beats + b), x, pan=0.2)

def hookline(bus, t0_beats, events, gain=1.0, seedbase=0, tenor=0.5, halo_g=0.13):
    """Westlife stack: lead (doubled) + third-below tenor + octave halo"""
    line(bus, t0_beats, events, gain=gain, style='shout', seedbase=seedbase)
    line(bus, t0_beats, shift(events, -4), gain=gain * tenor, style='croon',
         seedbase=seedbase + 7)
    halo(bus, t0_beats, events, gain=halo_g, seedbase=seedbase + 40)

def choir(bus, t0_beats, voicing, gain=0.09, seedbase=5000):
    """low 'ooo' block on the chord (the boyband choir pad)"""
    for k, m in enumerate(voicing[:3]):
        x = syll(mhz(m), 2.7, '', 'u', '', gain=gain, style='croon',
                 breath=0.1, seed=seedbase + k)
        bus.add(T(t0_beats), x, pan=-0.2 + 0.2 * k)

# ---------------------------------------------------------------- reverb
def make_ir(dur=1.9, tau=0.62, seed=21):
    """synthetic hall impulse: dense tail + early taps, L2-normalized"""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / tau)
    ir = lp(ir, 7500)
    for off, g in ((0.023, 0.35), (0.037, 0.28), (0.051, 0.22), (0.073, 0.16),
                   (0.096, 0.12), (0.13, 0.09)):
        i0 = int(off * SR)
        ir[i0:i0 + 200] += g * np.exp(-np.arange(200) / (0.02 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))
    return ir

def reverb(x, wet=0.32):
    ir = make_ir()
    y = sg.fftconvolve(x, ir, 'same')
    return x * (1 - wet) + y * wet


def bar_chords(bardef):
    """per-bar list of (chord, split_beat) pairs; SPLIT entries may be a
    2-name tuple (chords at beats 0,2) or explicit (chord,beat) pairs"""
    out = []
    for c in bardef:
        if c in SPLIT:
            v = SPLIT[c]
            if isinstance(v[0], tuple):
                out.append(v)
            else:
                ch1, ch2 = v
                out.append(((ch1, 0), (ch2, 2)))
        else:
            out.append(((c, 0),))
    return out

def chord_at(splitlist, beat):
    for ch, sp in splitlist:
        if beat >= sp:
            cur = ch
    return cur

# ---- bass lines: melodic, never root-pumping. (beat, midi, dur, gain)
BASSL = {          # half-note passing lines for verses / bridge
 'G':     [(0,43,1.7,.30),(1.7,45,.55,.22),(2.25,47,.7,.20)],
 'D':     [(0,38,1.8,.30),(1.8,45,1.1,.22)],
 'Dmaj7': [(0,38,1.6,.30),(1.6,42,.6,.22),(2.2,45,.7,.20)],
 'Em7':   [(0,40,1.5,.30),(1.5,43,.55,.22),(2.05,47,.8,.20)],
 'A':     [(0,45,1.5,.32),(1.5,49,.6,.24),(2.1,52,.8,.24)],
 'Em':    [(0,40,1.8,.32),(1.8,47,1.1,.24)],
 'Gmaj7': [(0,43,1.6,.30),(1.6,47,.6,.22),(2.2,50,.7,.20)],
}
BASSP = {          # rising pre-chorus
 'Em7': [(0,40,1.1,.34),(1.1,47,1.8,.26)],
 'G':   [(0,43,1.1,.34),(1.1,50,1.8,.26)],
 'A':   [(0,45,1.1,.36),(1.1,52,1.4,.30),(2.5,49,.5,.26)],
}
BASS8 = {          # 8th-note arpeggios for choruses (Villa drive)
 'D':     [(0,38,.5,.32),(.5,45,.45,.24),(1,50,.5,.28),(1.5,45,.45,.24),
           (2,50,.5,.28),(2.5,45,.45,.24),(3,47,.5,.24),(3.5,45,.45,.24)],
 'Dmaj7': [(0,38,.5,.30),(.5,42,.45,.24),(1,45,.5,.26),(1.5,42,.45,.24)],
 'Gmaj7': [(0,43,.5,.30),(.5,47,.45,.24),(1,50,.5,.26),(1.5,47,.45,.24)],
 'Em7':   [(0,40,.5,.30),(.5,43,.45,.24),(1,47,.5,.26),(1.5,43,.45,.24)],
 'A':     [(0,45,.5,.32),(.5,49,.45,.26),(1,52,.5,.28),(1.5,49,.45,.26)],
 'E':     [(0,40,.5,.34),(.5,47,.45,.26),(1,52,.5,.30),(1.5,47,.45,.26),
           (2,52,.5,.30),(2.5,47,.45,.26),(3,49,.5,.26),(3.5,47,.45,.26)],
 'Emaj7': [(0,40,.5,.32),(.5,44,.45,.26),(1,47,.5,.28),(1.5,44,.45,.26)],
 'Amaj7': [(0,45,.5,.34),(.5,49,.45,.28),(1,52,.5,.30),(1.5,49,.45,.28)],
 'F#m7':  [(0,42,.5,.32),(.5,45,.45,.26),(1,49,.5,.28),(1.5,45,.45,.26)],
 'B':     [(0,47,.5,.34),(.5,51,.45,.28),(1,54,.5,.30),(1.5,51,.45,.28)],
}
BASSC = {          # coda
 'E':     [(0,40,2.9,.30)],
 'Bmaj7': [(0,47,1.7,.30),(1.7,51,1.1,.24)],
 'B':     [(0,47,2.9,.30)],
}

bus = Bus(); drm = Bus(); vx = Bus()

def keysarp(b, chord, gain=0.15):
    """piano broken chord on the FM keys"""
    _, voic, _ = CH[chord]
    bus.add(T(b), keys(mhz(voic[0] + 12), 1.0, gain), pan=-0.2)
    bus.add(T(b + 1), keys(mhz(voic[1] + 12), 0.9, gain * 0.8), pan=-0.1)
    bus.add(T(b + 2), keys(mhz(voic[2] + 12), 0.9, gain * 0.8), pan=0.0)
    bus.add(T(b + 2.75), keys(mhz(voic[1] + 12), 0.8, gain * 0.7), pan=0.1)
    bus.add(T(b), keys(mhz(voic[0] + 12), 2.2, gain * 0.55), pan=-0.3)  # soft chord

def padbar(b, chord, gain=0.12, cut=2400.0, atk=1.0, seed=0, sweep=0):
    """sweep>0 opens the pad's cutoff over the bar (orchestra swell)"""
    _, voic, _ = CH[chord]
    kw = dict(atk=atk, cut=cut, seed=seed, gain=gain)
    if sweep:
        kw['sweep'] = sweep
    padat(bus, T(b), [m + 12 for m in voic], 2.5, **kw)

def bassbar(b, chord, table, at=0.0):
    for (bt, m, d, g) in table[chord]:
        bassat(bus, T(b + at + bt), m, d, g)

def bassbar_split(b, splitlist, table, at0=0.0):
    for ch, sp in splitlist:
        bassbar(b, ch, table, at=sp)

def keysbar_split(b, splitlist, gain=0.15):
    for ch, sp in splitlist:
        _, voic, _ = CH[ch]
        bus.add(T(b + sp), keys(mhz(voic[0] + 12), 1.0, gain), pan=-0.2)
        bus.add(T(b + sp + 1), keys(mhz(voic[1] + 12), 0.9, gain * 0.8), pan=-0.1)
        bus.add(T(b + sp + 2), keys(mhz(voic[2] + 12), 0.9, gain * 0.8), pan=0.0)
        bus.add(T(b + sp + 2.75), keys(mhz(voic[1] + 12), 0.8, gain * 0.7), pan=0.1)

# ------------------------------------------------------------ Villa drums
def vverse(b, vel=0.55):
    """syncopated verse groove: off-beat kicks, 2&4 snare, ghost notes"""
    drm.add(T(b + 0), kick(0.62 * vel)); drm.add(T(b + 2.5), kick(0.5 * vel))
    drm.add(T(b + 3.5), kick(0.42 * vel))
    drm.add(T(b + 1), snare(0.52 * vel)); drm.add(T(b + 3), snare(0.52 * vel))
    drm.add(T(b + 1.5), snare(0.18, ghost=True)); drm.add(T(b + 2.5), snare(0.16, ghost=True))
    drm.add(T(b + 0.5), rim(0.28 * vel))
    for p in range(16):
        v = 0.13 + 0.07 * (p % 4 == 0)
        drm.add(T(b + p * 0.25), hat(v))
    drm.add(T(b + 3.75), hat(0.30, open_=True))      # push into next bar

def vpre(b, i, vel=0.75):
    """pre-chorus: kick creeps to 4-on-the-floor, tom fill out"""
    if i < 3:
        drm.add(T(b + 0), kick(0.6 * vel)); drm.add(T(b + 1), kick(0.55 * vel))
        drm.add(T(b + 2), kick(0.55 * vel)); drm.add(T(b + 3), kick(0.5 * vel))
    else:
        for p in range(4):
            drm.add(T(b + p), kick((0.8 if p % 2 == 0 else 0.65) * vel))
    drm.add(T(b + 1), snare(0.62 * vel)); drm.add(T(b + 3), snare(0.62 * vel))
    drm.add(T(b + 1.5), snare(0.2, ghost=True))
    for p in range(16):
        v = 0.15 + 0.09 * (p % 4 == 0)
        drm.add(T(b + p * 0.25), hat(v))
    drm.add(T(b + 3.75), hat(0.35, open_=True))
    if i == 3:
        for k, ff in enumerate((90, 115, 145, 180)):
            drm.add(T(b + 2.5 + k * 0.25), tom(f=ff, vel=0.65))
        drm.add(T(b + 3.2), riser(2.2, 0.06, 250, 6500))

def vchorus(b, i, loud=1.0):
    """Villa disco chorus: 4-on-floor, snare+clap, ghosts, open hats, stutters"""
    for p in range(4):
        drm.add(T(b + p), kick((0.9 if p % 2 == 0 else 0.78) * loud))
    drm.add(T(b + 1), snare(0.85 * loud)); drm.add(T(b + 3), snare(0.85 * loud))
    drm.add(T(b + 1), clap(0.5)); drm.add(T(b + 3), clap(0.5))
    drm.add(T(b + 0.75), snare(0.18, ghost=True))
    drm.add(T(b + 1.5), snare(0.22, ghost=True)); drm.add(T(b + 2.5), snare(0.2, ghost=True))
    for p in range(16):
        v = 0.30 + 0.12 * (p % 4 == 0)
        drm.add(T(b + p * 0.25), hat(v))
    drm.add(T(b + 1.75), hat(0.35, open_=True)); drm.add(T(b + 3.75), hat(0.5, open_=True))
    if i % 4 == 3:                                    # stutter-step ending
        drm.add(T(b + 3.5), snare(0.5)); drm.add(T(b + 3.75), snare(0.55))
        drm.add(T(b + 3.875), snare(0.5))
    if i % 2 == 0:
        drm.add(T(b), crash(0.7))
    if i == 7:                                        # tom run out
        for k, ff in enumerate((90, 115, 145, 180)):
            drm.add(T(b + 2.0 + k * 0.5), tom(f=ff, vel=0.7))
        drm.add(T(b + 3.95), crash(0.9))

def vbridge(b, i):
    """bridge: rim groove, then 16th snare build and roll"""
    drm.add(T(b + 1), rim(0.4)); drm.add(T(b + 3), rim(0.4))
    drm.add(T(b + 0), kick(0.5)); drm.add(T(b + 2.5), kick(0.4))
    for p in range(8):
        drm.add(T(b + p * 0.5), hat(0.12))
    if i == 3:
        drm.add(T(b + 0), tom(f=92, vel=0.5))
    if i == 4:                                        # snare build
        for k in range(16):
            drm.add(T(b + k * 0.25), snare(vel=0.2 + 0.03 * k))
    if i == 5:                                        # full roll
        for k in range(24):
            drm.add(T(b + k * 0.1667), snare(vel=0.7))
        drm.add(T(b + 3.2), riser(1.8, 0.08, 350, 8000))
        drm.add(T(b + 3.95), crash(1.0))


# ================================================================= mix
def master(busL, busR, vxL, vxR, out, DUR):
    drmL = reverb(drm.L, 0.22); drmR = reverb(drm.R, 0.22)
    vL = reverb(vxL, 0.42) if vxL is not None else None
    vR = reverb(vxR, 0.42) if vxR is not None else None
    L = busL * 0.42 + drmL * 0.30 + (vL * 0.50 if vL is not None else 0)
    R = busR * 0.42 + drmR * 0.30 + (vR * 0.50 if vR is not None else 0)
    L = lp(L, 15500); R = lp(R, 15500)
    g = np.tanh(1.35)
    L = np.tanh(L * 1.35) / g; R = np.tanh(R * 1.35) / g
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)))
    L *= 0.92 / pk; R *= 0.92 / pk
    n = int(DUR * SR)
    L = L[:n]; R = R[:n]
    fi = int(0.125 * SR)
    L[:fi] *= np.linspace(0, 1, fi); R[:fi] *= np.linspace(0, 1, fi)
    fd = int(3.0 * SR)
    L[-fd:] *= np.linspace(1, 0, fd) ** 1.3; R[-fd:] *= np.linspace(1, 0, fd) ** 1.3
    st = np.stack([L, R], axis=1).astype(np.float32)
    import wave
    w = wave.open(out, 'wb')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
    w.close()
    print('written', out, round(n / SR, 1), 's, peak', round(pk, 3))

# =======================================================================
# SONG — A QUIET KIND OF LOVE (E major, 76 bpm, 56 bars = 2:57)
#
# The tenth and last of the Westlife set — the greatest-hits closer:
#   - "Fool Again": a cappella opening (voice + four-part block)
#   - "My Love": the final chorus up a whole step (E -> F#)
#   - "Flying Without Wings": the song closes on one held chord held by
#     the full 4-voice stack, bells fading underneath
#
# Harmony — Radiohead "No Surprises" (1997, F major, 76 bpm, music-box
# lullaby): verse F - Bbmaj7 - Gm - F; chorus Am - Dm - Gm - C - F with
# the repeated Gm-C resolving to F on "silent, silent"; the maj7 iv color
# and glockenspiel arpeggios are the identity. Transposed to E major:
#   verse:  E Amaj7 | F#m E            (maj7 IV color kept)
#   chorus: C#m F#m | Bm B | Bm B | E E   ("silent, silent" on the E)
#   pre:    E F#m | A B                (rising, lands on V)
#   bridge: D C | Am B                 (bVII bVI iv V, the modal shift)
#   coda:   F# held with the stack, bells to fade
# The bell synth is the glockenspiel.
# =======================================================================
BPM = 76.0
BEAT = 60.0 / BPM
BAR = 4.0
SECS = [('INTRO',2), ('V1',8), ('PRE1',4), ('CH1',8), ('V2',6),
        ('PRE2',4), ('CH2',8), ('BRIDGE',4), ('CH3',8), ('CODA',4)]
S = {}; _b = 0.0
for _n, _c in SECS:
    S[_n] = _b; _b += _c * BAR
END_BEATS = _b
DUR = T(END_BEATS)
TOTAL = DUR + 3.5
print('A QUIET KIND OF LOVE  bars', int(END_BEATS / BAR), ' duration', round(DUR, 1), 's')

CH = {
 'E':   (40, (52,56,59,64), 40),   'Amaj7': (45, (57,61,64,68), 45),
 'F#m': (42, (54,57,61,66), 42),   'C#m': (37, (49,52,56,61), 37),
 'Bm':  (47, (59,62,66,71), 47),   'B':  (47, (59,63,66,70), 47),
 'A':   (45, (57,61,64,69), 45),   'D':  (38, (50,54,57,62), 38),
 'C':   (36, (48,52,55,60), 36),   'Am': (45, (57,60,64,69), 45),
 'F#':  (42, (54,58,61,66), 42),   'D#m':(39, (51,54,58,63), 39),
 'G#m': (44, (56,59,63,68), 44),   'C#': (37, (49,53,56,61), 37),
 'B2':  (47, (59,63,66,70), 47),
}
SPLIT = {'EF#m': ('E','F#m'), 'AB': ('A','B'), 'DC': ('D','C'),
         'AmB': ('Am','B')}
V1BAR  = ['E','Amaj7','F#m','E'] * 2
PREBAR = ['E','F#m','A','B']
CHBAR  = ['C#m','F#m','Bm','B','Bm','B','E','E']
V2BAR  = ['E','Amaj7','F#m','E','E','Amaj7']
BRBAR  = ['DC','AmB','DC','AmB']
CH3BAR = ['D#m','G#m','C#m','C#','C#m','C#','F#','F#']   # whole step up
CODABAR= ['F#','F#','F#','F#']

BASSL = {
 'E':   [(0,40,1.7,.32),(1.7,47,1.2,.24)],
 'Amaj7':[(0,45,1.7,.32),(1.7,52,1.2,.24)],
 'F#m': [(0,42,1.7,.30),(1.7,49,1.2,.22)],
 'C#m': [(0,37,1.7,.30),(1.7,44,1.2,.22)],
 'Bm':  [(0,47,1.7,.30),(1.7,54,1.2,.22)],
 'B':   [(0,47,1.7,.32),(1.7,54,1.2,.24)],
 'A':   [(0,45,1.5,.32),(1.5,52,1.3,.24)],
 'D':   [(0,38,1.5,.30),(1.5,45,1.3,.22)],
 'C':   [(0,36,1.5,.30),(1.5,43,1.3,.22)],
 'Am':  [(0,45,1.5,.30),(1.5,52,1.3,.22)],
}
BASSP = {
 'E':   [(0,40,1.0,.34),(1.0,47,1.8,.26)],
 'F#m': [(0,42,1.0,.34),(1.0,49,1.8,.26)],
 'A':   [(0,45,1.0,.36),(1.0,52,1.8,.28)],
 'B':   [(0,47,1.0,.36),(1.0,54,1.8,.28)],
}
BASS8 = {
 'C#m': [(0,37,.5,.32),(.5,44,.45,.24),(1,49,.5,.28),(1.5,44,.45,.24),
         (2,49,.5,.28),(2.5,44,.45,.24),(3,51,.5,.24),(3.5,44,.45,.24)],
 'F#m': [(0,42,.5,.32),(.5,49,.45,.24),(1,54,.5,.28),(1.5,49,.45,.24),
         (2,54,.5,.28),(2.5,49,.45,.24),(3,56,.5,.24),(3.5,49,.45,.24)],
 'Bm':  [(0,47,.5,.32),(.5,54,.45,.24),(1,59,.5,.28),(1.5,54,.45,.24),
         (2,59,.5,.28),(2.5,54,.45,.24),(3,61,.5,.24),(3.5,54,.45,.24)],
 'B':   [(0,47,.5,.32),(.5,54,.45,.24),(1,59,.5,.28),(1.5,54,.45,.24),
         (2,59,.5,.28),(2.5,54,.45,.24),(3,61,.5,.24),(3.5,54,.45,.24)],
 'E':   [(0,40,.5,.32),(.5,47,.45,.24),(1,52,.5,.28),(1.5,47,.45,.24),
         (2,52,.5,.28),(2.5,47,.45,.24),(3,54,.5,.24),(3.5,47,.45,.24)],
 'D#m': [(0,39,.5,.32),(.5,46,.45,.24),(1,51,.5,.28),(1.5,46,.45,.24),
         (2,51,.5,.28),(2.5,46,.45,.24),(3,53,.5,.24),(3.5,46,.45,.24)],
 'G#m': [(0,44,.5,.32),(.5,51,.45,.24),(1,56,.5,.28),(1.5,51,.45,.24),
         (2,56,.5,.28),(2.5,51,.45,.24),(3,58,.5,.24),(3.5,51,.45,.24)],
 'C#':  [(0,37,.5,.32),(.5,44,.45,.24),(1,49,.5,.28),(1.5,44,.45,.24),
         (2,49,.5,.28),(2.5,44,.45,.24),(3,48,.5,.24),(3.5,44,.45,.24)],
 'F#':  [(0,42,.5,.32),(.5,49,.45,.24),(1,54,.5,.28),(1.5,49,.45,.24),
         (2,54,.5,.28),(2.5,49,.45,.24),(3,56,.5,.24),(3.5,49,.45,.24)],
}
BASSC = {
 'F#':  [(0,42,3.4,.30)],
}

bus = Bus(); drm = Bus(); vx = Bus()

def musicbox(b, ch, gain=0.09):
    """the glockenspiel arpeggio (bell synth) — the song's identity"""
    _, voic, _ = CH[ch]
    seq = [voic[0] + 12, voic[1] + 12, voic[2] + 12, voic[0] + 24]
    for p, m in enumerate(seq):
        bus.add(T(b + p * 0.75), bell(mhz(m), 2.2, gain),
                pan=0.2 if p % 2 else -0.2)

V1 = [
 # "there's a quiet in the evening"
 [(0,.6,'E4','e','th','r'),(.6,.55,'E4','a','',''),(1.15,.6,'G#4','ai','k','w'),
  (1.75,.55,'B4','e','','t'),(2.3,.6,'B4','i','','n'),
  (2.9,.55,'A4','e','th',''),(3.45,.6,'G#4','i','','v')],
 # "when the traffic fades away"
 [(0,.6,'G#4','e','w','n'),(.6,.55,'A4','e','th',''),(1.15,.6,'B4','a','tr','f'),
  (1.75,.55,'B4','i','','k'),(2.3,.6,'A4','ay','f','d'),
  (2.9,.55,'G#4','z','',''),(3.45,.7,'F#4','ay','w','')],
 # "and the kettle stops its singing"
 [(0,.6,'F#4','a','','n'),(.6,.55,'G#4','e','th',''),(1.15,.6,'B4','e','k','t'),
  (1.75,.55,'B4','l','',''),(2.3,.6,'A4','o','st','p'),
  (2.9,.55,'G#4','s','',''),(3.45,.6,'F#4','i','','ts'),(4.05,.5,'E4','i','s','ng')],
 # "and the clock has nothing to say"
 [(0,.6,'E4','a','','n'),(.6,.55,'G#4','e','th',''),(1.15,.6,'B4','o','k','l'),
  (1.75,.55,'B4','o','k',''),(2.3,.6,'A4','a','h','z'),
  (2.9,.55,'G#4','u','n','th'),(3.45,.55,'F#4','i','','ng'),(4.0,.55,'E4','u','t',''),
  (4.55,.5,'E4','ay','s','')],
 # "it's the hush before the snowfall"
 [(0,.6,'E4','i','','ts'),(.6,.55,'G#4','e','th',''),
  (1.15,.6,'B4','u','h','sh'),(1.75,.55,'B4','i','b',''),(2.3,.6,'A4','o','f','r'),
  (2.9,.55,'G#4','e','th',''),
  (3.45,.6,'F#4','o','sn','w')],
 # "it's the calm before the dawn"
 [(0,.6,'F#4','i','','ts'),(.6,.55,'G#4','e','th',''),
  (1.15,.6,'A4','a','k','lm'),(1.75,.55,'B4','i','b',''),(2.3,.6,'A4','o','f','r'),
  (2.9,.55,'G#4','e','th',''),(3.45,.7,'F#4','o','d','n')],
 # "and i'm learning to be still now"
 [(0,.6,'G#4','a','','n'),(.6,.55,'A4','ai','','m'),(1.15,.6,'B4','u','l','r'),
  (1.75,.55,'B4','i','','ng'),(2.3,.6,'A4','u','t',''),
  (2.9,.55,'G#4','i','b',''),
  (3.45,.6,'F#4','i','st','l'),(4.05,.5,'E4','ow','n','')],
 # "in the silence you have drawn"
 [(0,.6,'F#4','i','','n'),(.6,.55,'G#4','e','th',''),(1.15,.6,'B4','ai','s','l'),
  (1.75,.55,'B4','e','n',''),(2.3,.6,'A4','s','',''),
  (2.9,.55,'G#4','u','y',''),(3.45,.55,'F#4','a','h','v'),(4.0,.55,'E4','o','dr','n')],
]
PRE = [
 # "and i don't need the fireworks"
 [(0,.6,'B4','a','','n'),(.6,.55,'B4','ai','',''),
  (1.15,.6,'A4','o','d','nt'),
  (1.75,.55,'A4','i','n','d'),(2.3,.6,'G#4','e','th',''),
  (2.9,.55,'F#4','ai','f','r'),(3.45,.6,'E4','u','w','r'),(4.05,.5,'E4','o','k','s')],
 # "to tell me you are near"
 [(0,.6,'F#4','u','t',''),(.6,.55,'G#4','e','t','l'),(1.15,.6,'A4','i','m',''),
  (1.75,.55,'B4','u','y',''),(2.3,.6,'A4','a','','r'),
  (2.9,1.0,'G#4','i','n','r')],
 # "i can hear you in the quiet"
 [(0,.6,'C#5','ai','',''),(.6,.55,'C#5','a','k','n'),(1.15,.6,'B4','i','h','r'),
  (1.75,.55,'B4','u','y',''),(2.3,.6,'A4','i','','n'),
  (2.9,.55,'G#4','e','th',''),
  (3.45,.6,'F#4','ai','k','w'),(4.05,.5,'E4','e','','t')],
 # "better than i ever hear"
 [(0,.6,'F#4','e','b','t'),(.6,.55,'G#4','e','t','r'),
  (1.15,.6,'A4','a','th','n'),
  (1.75,.55,'B4','ai','',''),
  (2.3,.6,'C#5','e','','v'),(2.9,.55,'B4','e','','r'),
  (3.45,.7,'A4','i','h','r')],
]
HOOK = [
 # "it's a quiet kind of love"
 [(0,.9,'G#4','i','','ts'),(.9,.6,'B4','a','',''),(1.5,.6,'D5','ai','k','w'),
  (2.1,.55,'C#5','e','','t'),(2.65,.6,'B4','ai','k','n'),
  (3.25,.6,'A4','d','',''),(3.85,.55,'G#4','o','','v')],
 # "soft as snow upon the ground"
 [(0,.6,'A4','o','s',''),(.6,.55,'B4','a','','z'),
  (1.15,.6,'C#5','o','sn','w'),
  (1.75,.55,'B4','u','p',''),
  (2.3,.6,'A4','o','','n'),
  (2.9,.55,'G#4','e','th',''),
  (3.45,.7,'F#4','ow','gr','nd')],
 # "it's a quiet kind of love" (higher landing)
 [(0,.9,'G#4','i','','ts'),(.9,.6,'B4','a','',''),(1.5,.6,'E5','ai','k','w'),
  (2.1,.55,'D5','e','','t'),(2.65,.6,'C#5','ai','k','n'),
  (3.25,.6,'B4','d','',''),(3.85,.55,'A4','o','','v')],
 # "and it's the loudest sound i've found"
 [(0,.6,'B4','a','','n'),(.6,.55,'C#5','i','','ts'),
  (1.15,.6,'E5','e','th',''),
  (1.75,.55,'E5','ow','l','d'),
  (2.3,.6,'D5','e','st',''),
  (2.9,.55,'C#5','ow','s','nd'),
  (3.45,.55,'B4','ai','','v'),
  (4.0,.55,'A4','ow','f','nd')],
 # "no alarms, no siren call"
 [(0,.6,'A4','o','n',''),(.6,.55,'B4','a','',''),
  (1.15,.6,'C#5','l','','m'),
  (1.75,.55,'D5','o','','n'),
  (2.3,.6,'C#5','ai','s','r'),
  (2.9,.55,'B4','e','','n'),
  (3.45,.7,'A4','o','k','l')],
 # "just the steady beat of you"
 [(0,.6,'G#4','u','j','st'),(.6,.55,'A4','e','th',''),
  (1.15,.6,'B4','e','st',''),
  (1.75,.55,'B4','e','d',''),
  (2.3,.6,'C#5','i','b','t'),
  (2.9,.55,'B4','o','','v'),
  (3.45,.7,'A4','u','y','')],
 # "it's a quiet kind of love" (final)
 [(0,.6,'G#4','i','','ts'),(.6,.6,'B4','a','',''),
  (1.2,.6,'E5','ai','k','w'),
  (1.8,.55,'D5','e','','t'),
  (2.35,.6,'C#5','ai','k','n'),
  (2.95,.55,'B4','d','',''),
  (3.5,.6,'A4','o','','v'),
  (4.1,.5,'B4','','','')],
 # "and it's everything"
 [(0,.7,'C#5','a','','n'),(.7,.6,'D5','i','','ts'),
  (1.3,.6,'E5','e','','v'),
  (1.9,.55,'E5','i','r',''),
  (2.45,.6,'D5','e','th',''),
  (3.05,.55,'C#5','i','','ng'),
  (3.6,.6,'B4','i','',''),
  (4.2,.5,'A4','','','')],
]
V2 = [
 # "i have lived in loud cathedrals"
 [(0,.6,'E4','ai','',''),(.6,.55,'G#4','a','h','v'),
  (1.15,.6,'B4','i','l','v'),
  (1.75,.55,'B4','d','',''),
  (2.3,.6,'A4','i','','n'),
  (2.9,.55,'G#4','ow','l','d'),
  (3.45,.6,'F#4','k','','th'),
  (4.05,.5,'E4','e','dr','l')],
 # "with their bells of gold and brass"
 [(0,.6,'F#4','i','w','th'),(.6,.55,'G#4','e','th',''),
  (1.15,.6,'A4','e','b','l'),
  (1.75,.55,'B4','z','',''),
  (2.3,.6,'A4','o','','v'),
  (2.9,.55,'G#4','o','g','l'),
  (3.45,.55,'F#4','a','','n'),
  (4.0,.55,'E4','a','br','s')],
 # "but the sermon that has saved me"
 [(0,.6,'G#4','u','b','t'),(.6,.55,'A4','e','th',''),
  (1.15,.6,'B4','u','s','r'),
  (1.75,.55,'B4','o','m',''),
  (2.3,.6,'A4','a','th','t'),
  (2.9,.55,'G#4','a','h','z'),
  (3.45,.6,'F#4','ay','s','v'),
  (4.05,.5,'E4','d','','')],
 # "is the whisper when you pass"
 [(0,.6,'E4','i','','z'),(.6,.55,'G#4','e','th',''),
  (1.15,.6,'B4','i','w',''),
  (1.75,.55,'B4','e','sp','r'),
  (2.3,.6,'A4','e','w','n'),
  (2.9,.55,'G#4','u','y',''),
  (3.45,.7,'F#4','a','p','s')],
 # "so i'm building my own chapel"
 [(0,.6,'G#4','o','s',''),(.6,.55,'A4','ai','','m'),
  (1.15,.6,'B4','i','b','l'),
  (1.75,.55,'B4','d','',''),
  (2.3,.6,'A4','i','','ng'),
  (2.9,.55,'G#4','ai','m',''),
  (3.45,.6,'F#4','o','','n'),
  (4.05,.5,'E4','a','ch','p')],
 # "out of evenings soft and slow"
 [(0,.6,'F#4','ow','','t'),(.6,.55,'G#4','o','','v'),
  (1.15,.6,'A4','i','','v'),
  (1.75,.55,'B4','i','','ng'),
  (2.3,.6,'A4','z','',''),
  (2.9,.55,'G#4','o','s','f'),
  (3.45,.55,'F#4','a','','n'),
  (4.0,.55,'E4','o','sl','w')],
]
BR = [
 # "and if the world should come to shouting"
 [(0,.6,'G#4','a','','n'),(.6,.55,'A4','i','f',''),
  (1.15,.6,'B4','e','th',''),
  (1.75,.55,'B4','u','w','r'),
  (2.3,.6,'A4','l','d',''),
  (2.9,.55,'G#4','u','sh','d'),
  (3.45,.6,'F#4','u','k','m'),
  (4.05,.5,'E4','u','t',''),
  (4.55,.5,'E4','o','sh','t')],
 # "let the noise roll off my back"
 [(0,.6,'F#4','e','l','t'),(.6,.55,'G#4','e','th',''),
  (1.15,.6,'A4','o','n','z'),
  (1.75,.55,'B4','o','r','l'),
  (2.3,.6,'A4','o','','f'),
  (2.9,.55,'G#4','ai','m',''),
  (3.45,.7,'F#4','a','b','k')],
 # "i'll be standing in the quiet"
 [(0,.6,'G#4','ai','','l'),(.6,.55,'A4','i','b',''),
  (1.15,.6,'B4','e','st',''),
  (1.75,.55,'B4','a','','n'),
  (2.3,.6,'A4','d','',''),
  (2.9,.55,'G#4','i','','n'),
  (3.45,.6,'F#4','e','th',''),
  (4.05,.5,'E4','ai','k','w'),
  (4.55,.5,'E4','e','','t')],
 # "where i keep your voice intact"
 [(0,.6,'F#4','e','w','r'),(.6,.55,'G#4','ai','',''),
  (1.15,.6,'A4','i','k','p'),
  (1.75,.55,'B4','u','y',''),
  (2.3,.6,'C#5','o','v',''),
  (2.9,.55,'B4','s','',''),
  (3.45,.55,'A4','i','','n'),
  (4.0,.55,'G#4','a','t','k'),
  (4.55,.5,'F#4','a','','kt')],
]
CH3 = [shift(l, 2) for l in HOOK]                    # whole step up (E -> F#)
CODA_1 = [(0,.9,'A4','i','','ts'),(.9,.6,'C#5','a','',''),
          (1.5,.6,'F#5','ai','k','w'),
          (2.1,.55,'E5','e','','t'),
          (2.65,.6,'D#5','ai','k','n'),
          (3.25,.6,'C#5','d','',''),
          (3.85,1.2,'B4','o','','v')]
# ---- INTRO: a cappella 4-part block (bar 1), bells join (bar 2) ----
INTOP = [
 ('top',   [(0,1.3,'E4','a','',''),(1.6,1.3,'G#4','a','','')]),
 ('mid',   [(0,1.3,'B3','a','',''),(1.6,1.3,'E4','a','','')]),
 ('tenor', [(0,1.3,'G#3','a','',''),(1.6,1.3,'B3','a','','')]),
 ('low',   [(0,1.3,'E3','a','',''),(1.6,1.3,'E3','a','','')]),
]
for (vn, ev) in INTOP:
    line(vx, S['INTRO'], ev, gain=0.5, style='croon', seedbase=10)
    line(vx, S['INTRO'] + BAR, ev, gain=0.4, style='croon', seedbase=20)
b1 = S['INTRO'] + BAR
padbar(b1, 'E', gain=0.08, cut=1900, atk=1.6, seed=1)
musicbox(b1, 'E', gain=0.10)
bassbar(b1, 'E', BASSL)

# ---------------------------------------------------------- arrangement
# ---- V1: voice + music box, bass in, no drums ----
for i in range(8):
    b = S['V1'] + i * BAR
    ch = V1BAR[i]
    musicbox(b, ch, gain=0.09)
    padbar(b, ch, gain=0.06, cut=1800, atk=1.6, seed=100 + i)
    if i >= 2:
        bassbar(b, ch, BASSL)
    if i >= 5:
        vverse(b, vel=0.4)
    line(vx, b, V1[i], gain=0.80, style='croon', seedbase=200 + i * 17)

# ---- PRE1 ----
for i in range(4):
    b = S['PRE1'] + i * BAR
    ch = PREBAR[i]
    musicbox(b, ch, gain=0.10)
    padbar(b, ch, gain=0.09 + 0.02 * i, cut=2300 + 400 * i, atk=1.0, seed=300 + i)
    bassbar(b, ch, BASSP)
    vpre(b, i, vel=0.6)
    line(vx, b, PRE[i], gain=0.95, style='croon', seedbase=400 + i * 17)

# ---- CH1 ----
for i in range(8):
    b = S['CH1'] + i * BAR
    ch = CHBAR[i]
    musicbox(b, ch, gain=0.11)
    padbar(b, ch, gain=0.15, cut=4000, atk=0.5, seed=500 + i)
    bassbar(b, ch, BASS8)
    choir(vx, b, CH[ch][1], gain=0.08, seedbase=600 + i)
    vchorus(b, i, loud=1.0)
    hookline(vx, b, HOOK[i], gain=1.0, seedbase=700 + i * 17)

# ---- V2 ----
for i in range(6):
    b = S['V2'] + i * BAR
    ch = V2BAR[i]
    musicbox(b, ch, gain=0.09)
    padbar(b, ch, gain=0.07, cut=2000, atk=1.4, seed=800 + i)
    bassbar(b, ch, BASSL)
    vverse(b, vel=0.5)
    line(vx, b, V2[i], gain=0.95, style='croon', seedbase=900 + i * 17)

# ---- PRE2 ----
for i in range(4):
    b = S['PRE2'] + i * BAR
    ch = PREBAR[i]
    musicbox(b, ch, gain=0.11)
    padbar(b, ch, gain=0.12 + 0.02 * i, cut=2900 + 500 * i, atk=0.7, seed=1000 + i)
    bassbar(b, ch, BASSP)
    vpre(b, i, vel=0.8)
    line(vx, b, PRE[i], gain=1.0, style='croon', seedbase=1100 + i * 17)
drm.add(T(S['CH2'] - 0.05), crash(0.8))

# ---- CH2 ----
for i in range(8):
    b = S['CH2'] + i * BAR
    ch = CHBAR[i]
    musicbox(b, ch, gain=0.12)
    padbar(b, ch, gain=0.17, cut=4200, atk=0.4, seed=1200 + i)
    bassbar(b, ch, BASS8)
    choir(vx, b, CH[ch][1], gain=0.09, seedbase=1300 + i)
    vchorus(b, i, loud=1.0)
    hookline(vx, b, HOOK[i], gain=1.05, seedbase=1400 + i * 17, halo_g=0.14)

# ---- BRIDGE: the modal shift (D C | Am B), rim groove, build ----
for i in range(3):
    b = S['BRIDGE'] + i * BAR
    sl = bar_chords(BRBAR)[i]
    padbar(b, chord_at(sl, 0), gain=0.08, cut=1900, atk=1.6, seed=1500 + i)
    keysbar_split(b, sl, gain=0.11)
    for ch, sp in sl:
        bassbar(b, ch, BASSL, at=sp)
    musicbox(b, chord_at(sl, 0), gain=0.08)
    drm.add(T(b + 1), rim(0.35)); drm.add(T(b + 3), rim(0.35))
    drm.add(T(b + 0), kick(0.45)); drm.add(T(b + 2.5), kick(0.35))
    for p in range(8):
        drm.add(T(b + p * 0.5), hat(0.10))
    line(vx, b, BR[i], gain=1.0, style='croon', seedbase=1600 + i * 17)
bb = S['BRIDGE'] + 3 * BAR
padbar(bb, 'B', gain=0.12, cut=3000, atk=0.6, seed=44, sweep=16)
keysarp(bb, 'B', gain=0.14)
bassbar(bb, 'B', BASSP)
for k in range(16):
    drm.add(T(bb + k * 0.25), snare(vel=0.18 + 0.03 * k))
drm.add(T(bb + 3.2), riser(1.9, 0.09, 300, 8000))
drm.add(T(bb + 3.95), crash(1.0))

# ---- CH3: THE KEY CHANGE. whole step up, everything, held stack ----
for i in range(8):
    b = S['CH3'] + i * BAR
    ch = CH3BAR[i]
    musicbox(b, ch, gain=0.13)
    padbar(b, ch, gain=0.20, cut=5000, atk=0.3, seed=1700 + i, sweep=20)
    bassbar(b, ch, BASS8)
    choir(vx, b, CH[ch][1], gain=0.11, seedbase=1800 + i)
    vchorus(b, i, loud=1.08)
    drm.add(T(b), crash(0.75))
    if i % 2 == 0:
        bus.add(T(b + 0.5), stab([m + 12 for m in CH[ch][1]], 0.8, 0.15, cut=3000), pan=-0.2)
    hookline(vx, b, CH3[i], gain=1.1, seedbase=1900 + i * 17, halo_g=0.15)
b7 = S['CH3'] + 7 * BAR                # the held F# chord + full stack
for ev in CODA_1:
    line(vx, b7, [ev], gain=1.1, style='shout', seedbase=2400)
    line(vx, b7, [shift([ev], -4)[0]], gain=0.55, style='croon', seedbase=2500)
    line(vx, b7, [shift([ev], -7)[0]], gain=0.45, style='croon', seedbase=2600)
    line(vx, b7, [shift([ev], 12)[0]], gain=0.30, style='croon', seedbase=2700)
    line(vx, b7, [shift([ev], -12)[0]], gain=0.38, style='croon', seedbase=2800)
    choir(vx, b7, CH['F#'][1], gain=0.10, seedbase=2900)
drm.add(T(b7 + 3.6), crash(0.9))

# ---- CODA: held F#, bells fade ----
for i in range(4):
    b = S['CODA'] + i * BAR
    padbar(b, 'F#', gain=0.10, cut=2100, atk=1.5, seed=2100 + i)
    musicbox(b, 'F#', gain=0.09)
    keysarp(b, 'F#', gain=0.11)
    bassbar(b, 'F#', BASSC)
    if i == 0:
        drm.add(T(b + 0), kick(0.35)); drm.add(T(b + 2), kick(0.30))
        for p in range(8):
            drm.add(T(b + p * 0.5), hat(0.09))

master(bus.L, bus.R, vx.L, vx.R, 'quiet-kind-of-love.wav', DUR)
master(bus.L, bus.R, None, None, 'quiet-kind-of-love-instrumental.wav', DUR)
