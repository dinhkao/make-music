#!/usr/bin/env python3
"""
06-pink-floyd-eclipse.py — 70s Psychedelic Art-Rock (inspired by Pink Floyd 'Breathe' & David Bowie)
E Minor / G Major scale (72 BPM slow spacious 4/4 groove).
Chord progression: Em9 - A79 - Em9 - A79 - Cmaj7 - Bm7 - Am7 - D7 (classic 70s Pink Floyd Breathe progression).
Nick Villa drum style: Deep spacious tom grooves, ride bell accents, subtle snare flams, slow heavy kick.
Outputs: 06-pink-floyd-eclipse.mp3 and 06-pink-floyd-eclipse-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "06-pink-floyd-eclipse"

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
def ks(m, dur, damp=0.997, bright=0.5, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1600 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(700 + 5500 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.4)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def psych_lead(m, dur, g=0.16):
    L = int(dur * SR) + int(0.25 * SR); t = np.arange(L) / SR; f = hz(m)
    vib = 1 + 0.012 * np.sin(2 * np.pi * 5.5 * t)
    sig = np.sin(2 * np.pi * f * vib * t) + 0.4 * np.sin(4 * np.pi * f * vib * t)
    sig = np.tanh(sig * 2.5)
    bq, aq = sg.butter(2, [350 / (SR / 2), 3500 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.04, 0.2, 0.85, 0.25) * g).astype(np.float32)

def organ_drawbar(m, dur, g=0.10):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    sig = sum(np.sin(2 * np.pi * f * k * t) * (1.0 / k**0.85) for k in (1, 2, 3, 4, 6))
    sig *= (1 + 0.08 * np.sin(2 * np.pi * 6.2 * t))
    bq, aq = sg.butter(2, 3200 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.02, 0.1, 0.9, 0.15) * g).astype(np.float32)

def deep_bass(m, dur, g=0.30):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    bq, aq = sg.butter(2, 400 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.01, 0.1, 0.85, 0.15) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=66):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=40):
        L = int(0.5 * SR); t = np.arange(L) / SR
        f = tune * (1 + 1.8 * np.exp(-t / 0.035))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.25)
        return (np.tanh(x * 1.5) * vel).astype(np.float32)
    def snare(self, vel=1.0):
        L = int(0.4 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1]); taus = np.array([0.07, 0.2, 0.15, 0.1, 0.08, 0.06])
        body = modal(175, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1000 / (SR / 2), 7500 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / 0.15)
        x = body * 0.55 + wire * 0.75
        return (np.tanh(x * 1.3) * vel).astype(np.float32)
    def tom(self, vel=1.0, tune=95):
        L = int(0.7 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.7, 0.5, 0.3, 0.2, 0.1]); taus = np.array([0.35, 0.28, 0.2, 0.15, 0.12, 0.1])
        x = modal(tune, taus, g, L, self.rng)
        return (np.tanh(x * 1.3) * vel).astype(np.float32)
    def ride_bell(self, vel=1.0):
        L = int(0.8 * SR); t = np.arange(L) / SR
        f = 580.0
        x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.52 * t) + 0.3 * np.sin(2 * np.pi * f * 2.11 * t)
        return (x * np.exp(-t / 0.35) * vel * 0.3).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(606)
    kit = DrumKit(144)
    
    TOTAL_SEC = 170.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    bpm = 72.0
    spb = 60.0 / bpm # ~0.833s per beat
    bar44 = 4 * spb # ~3.333s per bar
    
    TOTAL_BARS = int(TOTAL_SEC / bar44)
    
    # Pink Floyd "Breathe" progression: Em9 -> A79 -> Em9 -> A79 -> Cmaj7 -> Bm7 -> Am7 -> D7
    chords_breathe = [
        ('E2', ['E3', 'G3', 'B3', 'D4', 'F#4']),  # Em9
        ('A2', ['A3', 'C#4', 'E4', 'G4', 'B4']),  # A79
        ('E2', ['E3', 'G3', 'B3', 'D4', 'F#4']),  # Em9
        ('A2', ['A3', 'C#4', 'E4', 'G4', 'B4']),  # A79
        ('C2', ['C3', 'E3', 'G3', 'B3']),         # Cmaj7
        ('B2', ['B3', 'D4', 'F#4', 'A4']),        # Bm7
        ('A2', ['A3', 'C4', 'E4', 'G4']),         # Am7
        ('D2', ['D3', 'F#3', 'A3', 'C4']),        # D7
    ]
    
    for bar_idx in range(TOTAL_BARS):
        b_root, b_notes = chords_breathe[bar_idx % len(chords_breathe)]
        b_t = bar_idx * bar44
        
        # Deep Sub Bass on 1 & 3
        put(inst_bus, b_t + 0 * spb, deep_bass(nn(b_root), spb * 1.8, g=0.32))
        put(inst_bus, b_t + 2 * spb, deep_bass(nn(b_root), spb * 1.8, g=0.28))
        
        # Leslie Drawbar Organ Swells
        for n_str in b_notes:
            put(inst_bus, b_t, organ_drawbar(nn(n_str), bar44 * 0.9, g=0.04))

        # Arpeggiated Clean Guitar
        for step, n_str in enumerate(b_notes):
            t_g = b_t + (step * 0.5 + rng.uniform(-0.006, 0.006)) * spb
            put(inst_bus, t_g, ks(nn(n_str), spb * 1.5, bright=0.4, seed=bar_idx*5+step), g=0.05)

        # Psychedelic Expressive Lead Guitar (David Gilmour style bends & vibrato)
        if bar_idx >= 4 and bar_idx % 2 == 1:
            l_n = b_notes[(bar_idx * 2) % len(b_notes)]
            t_l = b_t + (1.0 + rng.uniform(-0.008, 0.008)) * spb
            put(lead_bus, t_l, psych_lead(nn(l_n) + 12, spb * 2.5, g=0.18), g=1.0)

        # Nick Villa 70s Slow Spacious Drums (ride bell on beats, heavy snare backbeat, tom rolls)
        put(inst_bus, b_t + 0 * spb, kit.kick(1.0))
        put(inst_bus, b_t + 1 * spb, kit.snare(0.95))
        put(inst_bus, b_t + 2 * spb, kit.kick(0.85))
        put(inst_bus, b_t + 3 * spb, kit.snare(1.0))
        
        for h in range(4):
            put(inst_bus, b_t + h * spb, kit.ride_bell(0.8))
            
        if bar_idx % 4 == 3:
            put(inst_bus, b_t + 3.0 * spb, kit.tom(1.0, tune=130))
            put(inst_bus, b_t + 3.5 * spb, kit.tom(1.1, tune=90))

    print("Mixing and writing WAVs...")
    ir_len = int(2.0 * SR)
    ir = np.random.default_rng(66).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.7 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.35):
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
