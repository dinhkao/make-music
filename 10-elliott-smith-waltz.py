#!/usr/bin/env python3
"""
10-elliott-smith-waltz.py — 90s Chamber Singer-Songwriter Indie (inspired by Elliott Smith 'Waltz #2' & 'Waltz #1')
C Minor / Eb Major scale (112 BPM 3/4 waltz feel).
Chord progression: Cm -> G7/B -> Cm/Bb -> F/A -> Fm/Ab -> Cm/G -> G7 (classic chromatic descending bassline waltz).
Nick Villa drum style: Gentle brush waltz (Kick on 1, brush snares on 2 & 3, subtle rimshots).
Outputs: 10-elliott-smith-waltz.mp3 and 10-elliott-smith-waltz-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "10-elliott-smith-waltz"

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
def ks(m, dur, damp=0.996, bright=0.5, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(2000 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(700 + 5500 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.45)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def cello_pad(m, dur, g=0.12):
    L = int(dur * SR) + int(0.3 * SR); t = np.arange(L) / SR; f = hz(m)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 4.8 * t)
    sig = np.sin(2 * np.pi * f * vib * t) + 0.4 * np.sin(4 * np.pi * f * vib * t) + 0.2 * np.sin(6 * np.pi * f * vib * t)
    bq, aq = sg.butter(2, [200 / (SR / 2), 2200 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.15, 0.2, 0.85, 0.3) * g).astype(np.float32)

def rhodes_soft(m, dur, g=0.12):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    sig = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    bq, aq = sg.butter(2, 2200 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.008, 0.1, 0.75, 0.2) * g).astype(np.float32)

def bassn(m, dur, g=0.28):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    bq, aq = sg.butter(2, 480 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.01, 0.1, 0.8, 0.12) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=101):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=45):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.0 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
        return (np.tanh(x * 1.4) * vel).astype(np.float32)
    def brush_snare(self, vel=1.0):
        L = int(0.25 * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1400 / (SR / 2), 6500 / (SR / 2)], 'band')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / 0.1) * vel * 0.4).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(1010)
    kit = DrumKit(333)
    
    TOTAL_SEC = 165.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    # 3/4 waltz time @ 112 BPM (~0.535s per beat)
    bpm = 112.0
    spb = 60.0 / bpm
    bar34 = 3 * spb # ~1.607s per bar
    
    TOTAL_BARS = int(TOTAL_SEC / bar34)
    
    # Elliott Smith chromatic descending bassline waltz
    chords_elliott = [
        ('C2', ['C3', 'Eb3', 'G3']),    # Cm
        ('B1', ['B2', 'D3', 'F3', 'G3']),# G7/B
        ('Bb1', ['Bb2', 'D3', 'F3', 'Ab3']),# Cm/Bb
        ('A1', ['A2', 'C3', 'F3']),     # F/A
        ('Ab1', ['Ab2', 'C3', 'Eb3', 'F3']),# Fm/Ab
        ('G1', ['G2', 'C3', 'Eb3', 'G3']),# Cm/G
        ('G1', ['G2', 'B2', 'D3', 'F3', 'G3']),# G7
    ]
    
    for bar_idx in range(TOTAL_BARS):
        b_root, b_notes = chords_elliott[bar_idx % len(chords_elliott)]
        b_t = bar_idx * bar34
        
        # Bass note on beat 0
        put(inst_bus, b_t, bassn(nn(b_root), spb * 2.2, g=0.28))
        
        # Fingerpicked Acoustic Guitar (Waltz pattern: beat 0 bass, beats 1 & 2 strum)
        for beat in [1, 2]:
            t_g = b_t + beat * spb + rng.uniform(-0.005, 0.005)
            for n_str in b_notes:
                put(inst_bus, t_g + rng.uniform(0, 0.006), ks(nn(n_str), spb * 1.2, bright=0.5, seed=bar_idx*3+beat), g=0.045)

        # Cello Pad Harmony
        for n_str in b_notes[:2]:
            put(inst_bus, b_t, cello_pad(nn(n_str), bar34 * 0.95, g=0.04))

        # Soft Melodic Rhodes (Lead)
        if bar_idx >= 4 and bar_idx % 2 == 0:
            m_n = b_notes[(bar_idx) % len(b_notes)]
            t_m = b_t + 1.0 * spb + rng.uniform(-0.006, 0.006)
            put(lead_bus, t_m, rhodes_soft(nn(m_n) + 12, spb * 1.8, g=0.15), g=1.0)

        # Nick Villa Brush Drum Waltz (Kick on 0, soft brush snare on 1 & 2)
        put(inst_bus, b_t + 0 * spb, kit.kick(0.85))
        put(inst_bus, b_t + 1 * spb, kit.brush_snare(0.7))
        put(inst_bus, b_t + 2 * spb, kit.brush_snare(0.8))

    print("Mixing and writing WAVs...")
    ir_len = int(1.6 * SR)
    ir = np.random.default_rng(101).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.55 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.28):
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
