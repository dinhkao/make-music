"""Drum synthesis v2 - punchy, drum-like. + tom + crash."""
import numpy as np
from dsp import filt


def _atk(n, sr, ms=0.002):
    """2ms attack ramp to kill digital clicks."""
    a = int(ms * sr)
    r = np.ones(n)
    if a > 0 and a < n:
        r[:a] = np.linspace(0, 1, a)
    return r


def kick(amp, sr):
    """Deep punchy kick: 160->45Hz sweep + click + saturation."""
    n = int(0.28 * sr)
    t = np.arange(n) / sr
    f = 45 + 115 * np.exp(-t / 0.028)
    ph = 2 * np.pi * np.cumsum(f) / sr
    sig = np.sin(ph)
    body = np.tanh(sig * 3.0) * 0.9
    env = np.exp(-t / 0.09)
    env *= np.minimum(1, t / 0.002)
    nc = int(0.006 * sr)
    rng = np.random.default_rng(1)
    click = np.clip(rng.standard_normal(nc), -2, 2) * np.exp(-np.arange(nc) / (0.0012 * sr))
    out = np.concatenate([click, np.zeros(n - nc)])
    return ((body * env + out * 0.35) * _atk(n, sr) * amp).astype(np.float32)


def snare(amp, sr):
    """Cracky snare: body 190Hz + crack 1.8k + sizzle 7k."""
    n = int(0.3 * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(2)
    noise = rng.standard_normal(n)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.045)
    crack = filt(noise, sr, "bp", 1800) * np.exp(-t / 0.06)
    sizzle = filt(noise, sr, "hp", 6500) * np.exp(-t / 0.04)
    sig = body * 0.6 + crack * 1.6 + sizzle * 0.5
    return (sig * _atk(n, sr) * amp).astype(np.float32)


def hat(amp, sr, open_=False):
    """Hi-hat with body + sizzle (closed 0.035s, open 0.4s)."""
    d = 0.4 if open_ else 0.035
    n = int(d * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(n)
    body = filt(noise, sr, "bp", 4200) * 0.7
    sizzle = filt(noise, sr, "hp", 9000) * 1.0
    sig = (body + sizzle) * np.exp(-t / (d * 0.4))
    return (sig * _atk(n, sr) * amp).astype(np.float32)


def tom(amp, sr, pitch=1.0):
    """Floor/rack tom: swept sine + shell noise."""
    n = int(0.3 * sr)
    t = np.arange(n) / sr
    f0 = 120 * pitch
    f = f0 * 0.55 + f0 * 0.45 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / sr
    sig = np.sin(ph)
    sig = np.tanh(sig * 2.2) * 0.85
    rng = np.random.default_rng(6)
    shell = filt(rng.standard_normal(n), sr, "bp", 700) * 0.3
    env = np.exp(-t / 0.08) * np.minimum(1, t / 0.003)
    return ((sig + shell) * env * _atk(n, sr) * amp).astype(np.float32)


def crash(amp, sr):
    """Bright crash: noise HP 4k, long shimmer decay."""
    n = int(1.2 * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n)
    sig = filt(noise, sr, "hp", 3800)
    sig += 0.4 * filt(noise, sr, "bp", 5200)
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.32)
    return (sig * env * _atk(n, sr) * amp).astype(np.float32)


def shaker(amp, sr):
    n = int(0.05 * sr)
    t = np.arange(n) / sr
    noise = filt(np.random.default_rng(4).standard_normal(n), sr, "bp", 6500)
    return (noise * np.exp(-t / 0.02) * _atk(n, sr) * amp).astype(np.float32)


def tamb(amp, sr):
    n = int(0.12 * sr)
    t = np.arange(n) / sr
    noise = filt(np.random.default_rng(5).standard_normal(n), sr, "bp", 6000)
    return (noise * np.exp(-t / 0.045) * _atk(n, sr) * amp).astype(np.float32)


def crackle(dur, amp, sr, seed=9):
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
                pop = np.clip(rng.standard_normal(L), -2.2, 2.2) \
                    * np.exp(-np.arange(L) / (0.0012 * sr))
                out[pos:pos + L] += pop
    hiss = filt(rng.standard_normal(n), sr, "hp", 3000) * 0.06
    return ((out + hiss) * amp).astype(np.float32)
