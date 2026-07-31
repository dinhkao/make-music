"""Drum synthesis + vinyl crackle bed."""
import numpy as np
from dsp import filt


def kick(amp, sr):
    n = int(0.12 * sr)
    t = np.arange(n) / sr
    f = 45 + 75 * np.exp(-t / 0.02)
    ph = 2 * np.pi * np.cumsum(f) / sr
    sig = np.sin(ph) * np.exp(-t / 0.05)
    nc = int(0.004 * sr)
    click = np.random.default_rng(1).standard_normal(nc) * np.exp(-np.arange(nc) / (0.001 * sr))
    out = np.concatenate([click, np.zeros(n - nc)])
    return ((sig + out * 0.4) * amp).astype(np.float32)


def snare(amp, sr):
    n = int(0.18 * sr)
    t = np.arange(n) / sr
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    noise = filt(np.random.default_rng(2).standard_normal(n), sr, "bp", 2000)
    return ((body * 0.5 + noise * 1.5) * np.exp(-t / 0.09) * amp).astype(np.float32)


def hat(amp, sr, open_=False):
    d = 0.3 if open_ else 0.04
    n = int(d * sr)
    t = np.arange(n) / sr
    noise = filt(np.random.default_rng(3).standard_normal(n), sr, "hp", 7000)
    return (noise * np.exp(-t / (d * 0.35)) * amp).astype(np.float32)


def shaker(amp, sr):
    n = int(0.05 * sr)
    t = np.arange(n) / sr
    noise = filt(np.random.default_rng(4).standard_normal(n), sr, "bp", 6500)
    return (noise * np.exp(-t / 0.02) * amp).astype(np.float32)


def tamb(amp, sr):
    n = int(0.12 * sr)
    t = np.arange(n) / sr
    noise = filt(np.random.default_rng(5).standard_normal(n), sr, "bp", 6000)
    return (noise * np.exp(-t / 0.045) * amp).astype(np.float32)


def crackle(dur, amp, sr, seed=7):
    """Vinyl hiss + random pops (film-grain texture)."""
    rng = np.random.default_rng(seed)
    n = int(dur * sr)
    out = np.zeros(n)
    pops = rng.random(int(dur * 8))
    for i, p in enumerate(pops):
        if p < 0.3:
            pos = int(i * sr / 8)
            L = int(0.004 * sr)
            if pos + L < n:
                out[pos:pos + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (0.0012 * sr))
    hiss = filt(rng.standard_normal(n), sr, "hp", 3000) * 0.06
    return ((out + hiss) * amp).astype(np.float32)
