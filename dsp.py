"""DSP helpers: FFT filters, convolution reverb, delay, master bus."""
import numpy as np


def filt(sig, sr, kind="lp", fc=2000.0):
    """Simple FFT filter. kind: lp / hp / bp. fc in Hz."""
    n = len(sig)
    X = np.fft.rfft(sig)
    f = np.fft.rfftfreq(n, 1.0 / sr)
    if kind == "lp":
        H = 1.0 / (1.0 + (f / fc) ** 2)
    elif kind == "hp":
        H = (f / max(fc, 1.0)) ** 2 / (1.0 + (f / max(fc, 1.0)) ** 2)
    else:
        H = np.exp(-((f - fc) / (fc * 0.7)) ** 2)
    return np.fft.irfft(X * H, n)


def make_ir(sr, secs=1.7, decay=0.55, seed=0):
    """Exponentially decaying noise impulse response (Schroeder-ish)."""
    n = int(secs * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(seed)
    ir = rng.standard_normal(n) * np.exp(-t / decay)
    return filt(ir, sr, "lp", 4200)


def conv(sig, ir):
    """Fast convolution via FFT, returns len(sig)."""
    L = len(sig) + len(ir) - 1
    X = np.fft.rfft(sig, L)
    Y = np.fft.rfft(ir, L)
    return np.fft.irfft(X * Y, L)[: len(sig)]


def reverb(sig, sr, ir, predelay=0.03, wet=0.4):
    """Convolution reverb: sig + wet*IR."""
    n = int(predelay * sr)
    pad = np.concatenate([np.zeros(n), sig])
    dry = sig
    wet_sig = conv(pad, ir)[: len(sig)]
    return dry + wet * wet_sig


def delay(sig, sr, t=0.375, fb=0.42, taps=6):
    """Multi-tap echo (dotted-8th style)."""
    d = int(t * sr)
    out = np.zeros(len(sig) + d * taps)
    out[: len(sig)] = sig
    x = sig.copy()
    for i in range(taps):
        x = np.concatenate([np.zeros(d), x])[: len(sig)]
        x = x * fb
        out[d * (i + 1): d * (i + 1) + len(sig)] += x
    return out[: len(sig)]


def master(stereo, sr, gain=0.92):
    """Soft clip at fixed gain (keeps dynamics, no normalize)."""
    return np.tanh(stereo * 1.08) * gain


def write_wav(path, stereo, sr):
    """Write 16-bit stereo WAV."""
    import wave
    pcm = (np.clip(stereo, -1, 1) * 32767.0).astype("<i2")
    frames = pcm.T.tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(frames)
