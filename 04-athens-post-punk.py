#!/usr/bin/env python3
"""
04-athens-post-punk.py — Math Noise Post-Punk (inspired by Black Country, New Road 'Science Fair' & 'Athens, France')
C# Minor / Tritone Phrygian scale. Driving 5/4 asymmetric meter (150 BPM).
Nick Villa drum style: Aggressive ghost notes, 5/4 kick syncopation, open hi-hat sizzles.
Outputs: 04-athens-post-punk.mp3 and 04-athens-post-punk-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "04-athens-post-punk"

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
def ks(m, dur, damp=0.994, bright=0.75, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1400 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(900 + 7500 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.5)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def crunch_gtr(m, dur, g=0.16, drive=5.5):
    x = ks(m, dur, damp=0.995, bright=0.80).astype(np.float64)
    x = np.tanh(x * drive)
    bq, aq = sg.butter(2, [350 / (SR / 2), 4800 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, x) * env(len(x), 0.004, 0.08, 0.8, 0.12) * g).astype(np.float32)

def noise_lead(m, dur, g=0.15):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    vf = 1 + 0.015 * np.sin(2 * np.pi * 6.5 * t)
    ph = 2 * np.pi * np.cumsum(f * vf) / SR
    sig = np.sin(ph) + 0.5 * np.sin(3 * ph) + 0.3 * np.sin(5 * ph)
    sig = np.tanh(sig * 4.0)
    bq, aq = sg.butter(2, [500 / (SR / 2), 5200 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.02, 0.1, 0.85, 0.15) * g).astype(np.float32)

def bassn(m, dur, g=0.32):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t)
    x = np.tanh(x * 2.2)
    bq, aq = sg.butter(2, 700 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.008, 0.08, 0.85, 0.1) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=44):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=50):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.4 * np.exp(-t / 0.02))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
        return (np.tanh(x * 1.5) * vel).astype(np.float32)
    def snare(self, vel=1.0, art='center'):
        L = int(0.35 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1]); taus = np.array([0.05, 0.15, 0.12, 0.08, 0.06, 0.05])
        body = modal(195, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1200 / (SR / 2), 8500 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / (0.12 if art=='center' else 0.05))
        x = body * 0.5 + wire * 0.85
        return (np.tanh(x * 1.3) * vel * (0.35 if art=='ghost' else 1.0)).astype(np.float32)
    def tom(self, vel=1.0, tune=120):
        L = int(0.55 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.7, 0.5, 0.3, 0.2, 0.1]); taus = np.array([0.25, 0.2, 0.15, 0.12, 0.1, 0.08])
        x = modal(tune, taus, g, L, self.rng)
        return (np.tanh(x * 1.2) * vel).astype(np.float32)
    def hat(self, vel=1.0, op=False):
        L = int((0.26 if op else 0.05) * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(3, 7500 / (SR / 2), 'high')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / (0.18 if op else 0.025)) * vel * 0.4).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(404)
    kit = DrumKit(111)
    
    TOTAL_SEC = 155.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    # 5/4 time @ 150 BPM (~0.4s per quarter note)
    bpm = 150.0
    spb = 60.0 / bpm
    bar54 = 5 * spb # 2.0s per bar
    
    TOTAL_BARS = int(TOTAL_SEC / bar54)
    
    # Tritone Phrygian progression: C#m(b5) -> F#m/C# -> G/C# -> G#7
    chords_54 = [
        ('C#2', ['C#3', 'E3', 'G3', 'B3']),
        ('C#2', ['C#3', 'F#3', 'A3', 'C#4']),
        ('G2', ['G3', 'B3', 'D4', 'F4']),
        ('G#2', ['G#3', 'B#3', 'D#4', 'F#4']),
    ]
    
    for bar_idx in range(TOTAL_BARS):
        b_root, b_notes = chords_54[bar_idx % len(chords_54)]
        b_t = bar_idx * bar54
        
        # 5/4 Bass syncopation (beats 0, 1.5, 3, 4)
        for beat_off in [0.0, 1.5, 3.0, 4.0]:
            t_b = b_t + beat_off * spb + rng.uniform(-0.004, 0.004)
            put(inst_bus, t_b, bassn(nn(b_root), spb * 1.2, g=0.30))

        # Staccato Crunch Guitar Riff in 5/4
        for step in range(5):
            n_str = b_notes[step % len(b_notes)]
            t_g = b_t + step * spb + rng.uniform(-0.006, 0.006)
            put(inst_bus, t_g, crunch_gtr(nn(n_str), spb * 0.8, g=0.08, drive=6.0))

        # Screeching Noise Lead (Science Fair style)
        if bar_idx >= 8 and bar_idx % 2 == 1:
            lead_n = b_notes[(bar_idx * 3) % len(b_notes)]
            t_l = b_t + 2.0 * spb + rng.uniform(-0.005, 0.005)
            put(lead_bus, t_l, noise_lead(nn(lead_n) + 12, spb * 2.5, g=0.15), g=1.0)

        # Nick Villa Aggressive 5/4 Drumming (accent beats 0, 2, 3.5, 4.5)
        put(inst_bus, b_t + 0.0 * spb, kit.kick(1.0))
        put(inst_bus, b_t + 1.0 * spb, kit.snare(0.4, art='ghost'))
        put(inst_bus, b_t + 2.0 * spb, kit.snare(0.95, art='center'))
        put(inst_bus, b_t + 3.0 * spb, kit.kick(0.85))
        put(inst_bus, b_t + 3.5 * spb, kit.snare(0.4, art='ghost'))
        put(inst_bus, b_t + 4.0 * spb, kit.kick(0.9))
        put(inst_bus, b_t + 4.5 * spb, kit.hat(0.9, op=True))
        
        for h in range(5):
            put(inst_bus, b_t + h * spb + 0.5 * spb, kit.hat(0.6))

    print("Mixing and writing WAVs...")
    ir_len = int(1.2 * SR)
    ir = np.random.default_rng(44).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.4 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.22):
        padded = np.concatenate([np.zeros(int(0.02 * SR)), sig])
        res = sg.fftconvolve(padded, ir)[:len(sig)]
        return sig + wet * res

    mix_full = np.tanh(apply_reverb(lead_bus + inst_bus) * 1.2) * 0.85
    mix_inst = np.tanh(apply_reverb(inst_bus) * 1.2) * 0.85

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
