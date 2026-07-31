"""Synthesized instruments (additive/FM-ish). All return mono float32."""
import numpy as np
from dsp import filt


def note_freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def _saw(freq, n, sr, det=1.0):
    t = np.arange(n) / sr
    ph = 2 * np.pi * freq * det * t
    return sum((1.0 / h) * np.sin(ph * h) for h in range(1, 9))


def ep(freq, dur, amp, sr):
    """Rhodes-ish electric piano: inharmonic partials + tremolo."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    parts = [(1.0, 1.0), (2.0, 0.5), (3.0, 0.28), (4.1, 0.15), (5.9, 0.05)]
    sig = sum(a * np.sin(2 * np.pi * freq * p * t) for p, a in parts)
    sig += 0.6 * sum(a * np.sin(2 * np.pi * freq * 1.0015 * p * t) for p, a in parts)
    env = np.exp(-t / (dur * 0.45))
    env *= np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.05)
    trem = 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    return (sig * env * trem * amp).astype(np.float32)


def bass(freq, dur, amp, sr):
    """Warm bass: sine + harmonics + soft saturation."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.3 * np.sin(4 * np.pi * freq * t)
           + 0.08 * np.sin(6 * np.pi * freq * t))
    sig = np.tanh(sig * 1.8) * 0.8
    env = np.minimum(1, t / 0.008)
    env *= 0.72 + 0.28 * np.exp(-t / (dur * 0.5))
    env *= np.minimum(1, (dur - t) / 0.05)
    return (sig * env * amp).astype(np.float32)


def strings(freqs, dur, amp, sr, cut=1400.0):
    """Detuned saw stack + lowpass, slow attack (pad)."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = np.zeros(n)
    for f in freqs:
        for d in (0.9975, 1.0, 1.0025):
            sig += _saw(f, n, sr, d)
    sig /= 3.0 * len(freqs)
    sig = filt(sig, sr, "lp", cut)
    a = max(0.25, dur * 0.35)
    env = np.minimum(1, t / a) * np.minimum(1, (dur - t) / 0.4)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5 * t)
    return (sig * env * vib * amp).astype(np.float32)


def lead(freq, dur, amp, sr):
    """Soft lead 'voice': saw + LP + vibrato."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = (_saw(freq, n, sr) + _saw(freq, n, sr, 1.004)) / 2
    sig = filt(sig, sr, "lp", 2600)
    vib = 1 + 0.010 * np.minimum(1, t / 0.4) * np.sin(2 * np.pi * 5.5 * t)
    env = np.minimum(1, t / 0.015) * np.minimum(1, (dur - t) / 0.08)
    return (sig * env * vib * amp).astype(np.float32)


def solo(freq, dur, amp, sr):
    """Psychedelic lead: detuned saws, drive, dip + vibrato."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = (_saw(freq, n, sr) + _saw(freq, n, sr, 0.996) + _saw(freq, n, sr, 1.006))
    sig = np.tanh(sig * 2.2)
    sig = filt(sig, sr, "lp", 3600)
    dip = 1 - 0.01 * np.exp(-t / 0.03)
    vib = 1 + 0.02 * np.sin(2 * np.pi * 6 * t)
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.1)
    return (sig * env * vib * dip * amp).astype(np.float32)


def choir(freqs, dur, amp, sr):
    """Wordless 'ah' choir: detuned saws through formant bands."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    sig = np.zeros(n)
    for f in freqs:
        for d in (0.995, 1.0, 1.005):
            sig += _saw(f, n, sr, d)
    sig /= 3.0 * len(freqs)
    sig = (1.0 * filt(sig, sr, "bp", 750)
           + 0.7 * filt(sig, sr, "bp", 1150)
           + 0.5 * filt(sig, sr, "bp", 2600))
    env = np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 0.8)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 4.2 * t + 0.5)
    return (sig * env * vib * amp).astype(np.float32)


def ks(freq, dur, amp, sr, damp=0.5):
    """Karplus-Strong pluck - acoustic guitar-ish string."""
    n = int(dur * sr)
    L = max(2, int(sr / freq))
    rng = np.random.default_rng(0)
    buf = rng.uniform(-1, 1, L)
    k = max(1, int(damp * L / 8))
    w = np.ones(k) / k
    buf = np.convolve(buf, w, 'same')
    buf *= 1.0 / (np.max(np.abs(buf)) + 1e-9)
    cycles = int(np.ceil(n / L)) + 1
    out = np.tile(buf, cycles)[:n]
    env = np.exp(-np.arange(n) / (0.45 * sr))  # ring ~0.45s
    env *= np.minimum(1, np.arange(n) / (0.004 * sr))
    return (out * env * amp).astype(np.float32)


def clap(amp, sr):
    """Handclap: double burst noise."""
    n = int(0.18 * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(8)
    noise = rng.standard_normal(n)
    sig = filt(noise, sr, "bp", 1400)
    burst = np.zeros(n)
    b1, b2 = int(0.005 * sr), int(0.03 * sr)
    burst[:int(0.02 * sr)] = np.exp(-np.arange(int(0.02 * sr)) / (0.006 * sr))
    burst[b2:b2 + int(0.05 * sr)] = np.exp(-np.arange(int(0.05 * sr)) / (0.01 * sr))
    out = sig * burst * 1.2
    out *= np.minimum(1, t / 0.001)
    return (out * amp).astype(np.float32)
