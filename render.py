"""render - mix FX: reverb, chorus, write_wav. (scipy-free except chorus)."""
import numpy as np
from scipy import signal as sg
from gi_engine import SR


def _ir(secs, decay, seed):
    n = int(secs * SR)
    t = np.arange(n) / SR
    r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-t / decay)
    b, a = sg.butter(2, 4500 / (SR / 2), 'low')
    ir = sg.lfilter(b, a, ir)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    return ir


def _conv(x, ir):
    n = len(x) + len(ir) - 1
    X = np.fft.rfft(x, n)
    Y = np.fft.rfft(ir, n)
    return np.fft.irfft(X * Y, n)[:len(x)]


def reverb(L, R, secs=1.5, wet=0.20):
    """Stereo convolution reverb (mid/side-ish crossfeed)."""
    irL = _ir(secs, secs * 0.35, 0)
    irR = _ir(secs, secs * 0.40, 1)
    outL = L + wet * _conv(L, irL) + 0.7 * wet * _conv(R, irL)
    outR = R + wet * _conv(R, irR) + 0.7 * wet * _conv(L, irR)
    return outL, outR


def chorus(x, depth=0.004, rate=0.8, voices=2):
    """Detuned delayed copies chorus."""
    n = len(x)
    t = np.arange(n) / SR
    out = x.copy()
    for i in range(voices):
        d = (depth * np.sin(2 * np.pi * rate * (0.9 + 0.2 * i) * t + i) * SR).astype(int)
        idx = np.clip(np.arange(n) - d, 0, n - 1)
        out += x[idx] * 0.5
    return out / (1.0 + 0.5 * voices)


def write_wav(path, data, sr=SR):
    """Write 16-bit stereo WAV. data: (N,2) or (2,N)."""
    import wave
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    if data.shape[0] == 2 and data.shape[1] != 2:
        data = data.T
    pcm = (np.clip(data, -1, 1) * 32767.0).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
