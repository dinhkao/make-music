#!/usr/bin/env python3
"""
08-radiohead-pyramids.py — Experimental Art-Rock (inspired by Radiohead 'Pyramid Song')
F# Harmonic Minor scale (136 BPM 8ths, 16-beat asymmetric cycle: 3+3+3+3+4).
Chord progression: F#m -> Gmaj7/F# -> F#m6 -> Esus4 -> F#m.
Nick Villa drum style: Stutter-step snare rimshots, cymbal swells, off-beat syncopated kick.
Outputs: 08-radiohead-pyramids.mp3 and 08-radiohead-pyramids-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "08-radiohead-pyramids"

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
def ks(m, dur, damp=0.996, bright=0.4, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1800 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(500 + 4500 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.4)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def rhodes_dark(m, dur, g=0.14):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    sig = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    bq, aq = sg.butter(2, 1800 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.01, 0.1, 0.75, 0.25) * g).astype(np.float32)

def synth_lead_swell(m, dur, g=0.15):
    L = int(dur * SR) + int(0.3 * SR); t = np.arange(L) / SR; f = hz(m)
    vib = 1 + 0.010 * np.sin(2 * np.pi * 5.8 * t)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    sig = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    bq, aq = sg.butter(2, [300 / (SR / 2), 3200 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.2, 0.2, 0.8, 0.3) * g).astype(np.float32)

def subbass(m, dur, g=0.32):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t)
    bq, aq = sg.butter(2, 350 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.02, 0.1, 0.85, 0.2) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=88):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=44):
        L = int(0.45 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.0 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
        return (np.tanh(x * 1.5) * vel).astype(np.float32)
    def snare(self, vel=1.0, art='rim'):
        L = int(0.35 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1]); taus = np.array([0.05, 0.15, 0.12, 0.08, 0.06, 0.05])
        body = modal(185, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1100 / (SR / 2), 7800 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / (0.12 if art=='center' else 0.04))
        x = body * 0.4 + wire * 0.8
        return (np.tanh(x * 1.3) * vel * (0.35 if art=='ghost' else (0.75 if art=='rim' else 1.0))).astype(np.float32)
    def hat(self, vel=1.0, op=False):
        L = int((0.3 if op else 0.04) * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(3, 7500 / (SR / 2), 'high')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / (0.22 if op else 0.025)) * vel * 0.35).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(808)
    kit = DrumKit(177)
    
    TOTAL_SEC = 165.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    # 16-beat asymmetric cycle @ 136 BPM eighths (~0.441s per 8th note)
    bpm = 136.0
    sp_8th = 60.0 / bpm
    cycle16 = 16 * sp_8th # ~7.058s per cycle
    
    TOTAL_CYCLES = int(TOTAL_SEC / cycle16)
    
    # Radiohead Pyramid Song modal chord cycle
    chords_radiohead = [
        ('F#2', ['F#3', 'A3', 'C#4', 'E#4']), # F#m(maj7)
        ('F#2', ['G3', 'B3', 'D4', 'F#4']),   # Gmaj7/F#
        ('F#2', ['F#3', 'A3', 'C#4', 'D#4']), # F#m6
        ('E2', ['E3', 'A3', 'B3', 'E4']),     # Esus4
    ]
    
    # Asymmetric 16-beat offsets: 0, 3, 6, 9, 12 (3+3+3+3+4)
    offsets_16 = [0, 3, 6, 9, 12]
    
    for cycle_idx in range(TOTAL_CYCLES):
        c_root, c_notes = chords_radiohead[cycle_idx % len(chords_radiohead)]
        c_t = cycle_idx * cycle16
        
        # Asymmetric Sub-Bass & Dark Rhodes Chords
        for off_idx, beat_off in enumerate(offsets_16):
            t_sub = c_t + beat_off * sp_8th + rng.uniform(-0.006, 0.006)
            dur_sub = (3 if off_idx < 4 else 4) * sp_8th
            put(inst_bus, t_sub, subbass(nn(c_root), dur_sub * 0.9, g=0.32))
            
            for n_str in c_notes:
                put(inst_bus, t_sub, rhodes_dark(nn(n_str), dur_sub * 0.85, g=0.06))

        # Swelling Lead Synth
        if cycle_idx >= 2 and cycle_idx % 2 == 1:
            l_n = c_notes[(cycle_idx) % len(c_notes)]
            t_l = c_t + 6.0 * sp_8th + rng.uniform(-0.008, 0.008)
            put(lead_bus, t_l, synth_lead_swell(nn(l_n) + 12, sp_8th * 6.0, g=0.16), g=1.0)

        # Nick Villa Asymmetric Drum Pattern
        for off_idx, beat_off in enumerate(offsets_16):
            t_d = c_t + beat_off * sp_8th
            if off_idx % 2 == 0:
                put(inst_bus, t_d, kit.kick(1.0))
            else:
                put(inst_bus, t_d, kit.snare(0.9, art='rim'))
                
            put(inst_bus, t_d + 1.5 * sp_8th, kit.snare(0.35, art='ghost'))
            put(inst_bus, t_d + 2.5 * sp_8th, kit.hat(0.8, op=(off_idx==4)))

    print("Mixing and writing WAVs...")
    ir_len = int(1.8 * SR)
    ir = np.random.default_rng(88).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.6 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.32):
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
