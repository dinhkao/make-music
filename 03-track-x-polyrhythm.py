#!/usr/bin/env python3
"""
03-track-x-polyrhythm.py — Ambient Polyrhythmic Folk-Post-Rock (inspired by Black Country, New Road 'Track X' & Steve Reich)
F Major / C Major scale. 6/8 fingerpicking over 3/4 bass polymeter.
Nick Villa drum style: Soft brush modal kit, shaker micro-grooves, open hi-hat swells.
Outputs: 03-track-x-polyrhythm.mp3 and 03-track-x-polyrhythm-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "03-track-x-polyrhythm"

def nn(s):
    m = re.match(r"^([A-Ga-g][#b]?)[^\d]*(\d+)$", s)
    if m:
        note_part, oct_part = m.group(1).upper(), int(m.group(2))
        base = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        n = base[note_part[0]]
        if len(note_part) > 1:
            n += 1 if note_part[1] == '#' else -1
        return 12 * (oct_part + 1) + n
    return 60

def hz(m): return 440.0 * 2 ** ((m - 69) / 12.0)

def env(L, a, d, s, r):
    e = np.ones(L)
    ai = min(int(a * SR), L)
    if ai > 0: e[:ai] = np.linspace(0, 1, ai)
    di = int(d * SR)
    if ai + di < L: e[ai:ai+di] = np.linspace(1, s, di); e[ai+di:] = s
    else: e[ai:] = np.linspace(1, s, max(L - ai, 1))
    ri = min(int(r * SR), L)
    if ri > 0: e[L-ri:] *= np.linspace(1, 0, ri)**1.3
    return e

def put(b, t0, x, g=1.0):
    i = int(t0 * SR)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(b) - i)
    if n > 0: b[i:i+n] += x[:n] * g

_KS = {}
def ks(m, dur, damp=0.997, bright=0.45, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1300 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(600 + 5000 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.4)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def rhodes(m, dur, g=0.12):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    sig = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    return (sig * env(L, 0.005, 0.1, 0.7, 0.2) * trem * g).astype(np.float32)

def fretless_bass(m, dur, g=0.26):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    ph = 2 * np.pi * f * t
    sig = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    bq, aq = sg.butter(2, 450 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.02, 0.15, 0.8, 0.2) * g).astype(np.float32)

def pad_synth(m, dur, g=0.08):
    L = int(dur * SR) + int(0.3 * SR); t = np.arange(L) / SR; f = hz(m)
    sig = np.sin(2 * np.pi * f * 0.998 * t) + np.sin(2 * np.pi * f * 1.002 * t)
    bq, aq = sg.butter(2, 1200 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.2, 0.3, 0.85, 0.35) * g).astype(np.float32)

class DrumKit:
    def __init__(self, seed=33):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=42):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.0 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
        return (np.tanh(x * 1.4) * vel).astype(np.float32)
    def brush_snare(self, vel=1.0):
        L = int(0.25 * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1500 / (SR / 2), 6500 / (SR / 2)], 'band')
        x = sg.lfilter(bq, aq, n) * np.exp(-t / 0.1)
        return (x * vel * 0.4).astype(np.float32)
    def shaker(self, vel=1.0):
        L = int(0.12 * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [3500 / (SR / 2), 12000 / (SR / 2)], 'band')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / 0.04) * vel * 0.3).astype(np.float32)
    def hat(self, vel=1.0, op=False):
        L = int((0.3 if op else 0.05) * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(3, 8000 / (SR / 2), 'high')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / (0.22 if op else 0.025)) * vel * 0.3).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(303)
    kit = DrumKit(99)
    
    TOTAL_SEC = 165.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    # 6/8 time @ 116 BPM eighths (~0.517s per beat)
    bpm = 116.0
    sp_8th = 60.0 / bpm
    bar68 = 6 * sp_8th # ~3.103s per bar
    
    # Lush 70s/90s maj7 & add9 chord progression
    chords_polymeter = [
        ('F2', ['F3', 'A3', 'C4', 'E4', 'G4']),   # Fmaj9
        ('E2', ['E3', 'G3', 'B3', 'D4', 'G4']),   # Cmaj7/E
        ('D2', ['D3', 'F3', 'A3', 'C4', 'E4']),   # Dm9
        ('A2', ['A3', 'C4', 'E4', 'G4']),         # Am7
        ('Bb2', ['Bb3', 'D4', 'F4', 'A4', 'C5']), # Bbmaj9
    ]
    
    TOTAL_BARS = int(TOTAL_SEC / bar68)
    
    for bar_idx in range(TOTAL_BARS):
        b_root, b_notes = chords_polymeter[bar_idx % len(chords_polymeter)]
        b_t = bar_idx * bar68
        
        # Fretless bass: 3/4 pulse over 6/8 guitar (polymetric feel on beats 0, 2, 4)
        for b_step in [0, 2, 4]:
            t_b = b_t + b_step * sp_8th + rng.uniform(-0.005, 0.005)
            put(inst_bus, t_b, fretless_bass(nn(b_root), sp_8th * 1.8, g=0.25))
            
        # 6/8 Arpeggiated fingerpicking guitar (un-quantized, humanized dynamics)
        for step in range(6):
            n_str = b_notes[step % len(b_notes)]
            t_g = b_t + step * sp_8th + rng.uniform(-0.007, 0.007)
            vel_g = 0.05 + 0.03 * (1.0 if step in [0, 3] else 0.7)
            put(inst_bus, t_g, ks(nn(n_str), sp_8th * 2.2, bright=0.45, seed=bar_idx*6+step), g=vel_g)

        # Soft Warm Synth Pad
        for n_str in b_notes[:3]:
            put(inst_bus, b_t, pad_synth(nn(n_str), bar68 * 0.95, g=0.04))

        # Rhodes Melody (Lead track)
        if bar_idx >= 4 and bar_idx % 2 == 0:
            mel_n = b_notes[(bar_idx * 2) % len(b_notes)]
            t_m = b_t + (1.5 + rng.uniform(-0.008, 0.008)) * sp_8th
            put(lead_bus, t_m, rhodes(nn(mel_n) + 12, sp_8th * 3.0, g=0.14), g=1.0)
            put(lead_bus, t_m + 1.5 * sp_8th, rhodes(nn(mel_n) + 14, sp_8th * 2.0, g=0.10), g=1.0)

        # Nick Villa Ambient Drum Texture
        if bar_idx >= 2:
            put(inst_bus, b_t + 0 * sp_8th, kit.kick(0.85))
            put(inst_bus, b_t + 3 * sp_8th, kit.brush_snare(0.8))
            put(inst_bus, b_t + 4.5 * sp_8th, kit.kick(0.7))
            put(inst_bus, b_t + 5.5 * sp_8th, kit.hat(0.8, op=True))
            for s_idx in range(6):
                put(inst_bus, b_t + s_idx * sp_8th + rng.uniform(-0.003, 0.003), kit.shaker(0.4))

    print("Mixing and writing WAVs...")
    ir_len = int(1.8 * SR)
    ir = np.random.default_rng(33).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.6 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.30):
        padded = np.concatenate([np.zeros(int(0.02 * SR)), sig])
        res = sg.fftconvolve(padded, ir)[:len(sig)]
        return sig + wet * res

    mix_full = np.tanh(apply_reverb(lead_bus + inst_bus) * 1.1) * 0.85
    mix_inst = np.tanh(apply_reverb(inst_bus) * 1.1) * 0.85

    stereo_full = np.vstack([mix_full, mix_full]).T
    stereo_inst = np.vstack([mix_inst, mix_inst]).T

    wav_full = f"{NAME}.wav"
    wav_inst = f"{NAME}-instrumental.wav"
    mp3_full = f"{NAME}.mp3"
    mp3_inst = f"{NAME}-instrumental.mp3"

    import wave
    for pth, stm in [(wav_full, stereo_full), (wav_inst, stereo_inst)]:
        pcm = (np.clip(stm, -1, 1) * 32767.0).astype("<i2")
        with wave.open(pth, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes(pcm.tobytes())

    print("Encoding MP3s with ffmpeg...")
    subprocess.run(["ffmpeg", "-y", "-i", wav_full, "-b:a", "320k", mp3_full], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-i", wav_inst, "-b:a", "320k", mp3_inst], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(wav_full): os.remove(wav_full)
    if os.path.exists(wav_inst): os.remove(wav_inst)
    print(f"Done: {mp3_full} & {mp3_inst}")

if __name__ == "__main__":
    build_song()
