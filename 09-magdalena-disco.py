#!/usr/bin/env python3
"""
09-magdalena-disco.py — Progressive Synth-Pop / Disco-Indie (inspired by Magdalena Bay 'Imaginal Disk' & 'Cry for Me')
B Minor / D Major scale (124 BPM 4/4 energetic dance drive).
Chord progression: Bm7 -> Gmaj7 -> Em9 -> F#7alt.
Nick Villa drum style: Live disco four-on-the-floor, rapid hi-hat chokes, syncopated backbeat snare + claps.
Outputs: 09-magdalena-disco.mp3 and 09-magdalena-disco-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "09-magdalena-disco"

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
def ks(m, dur, damp=0.996, bright=0.7, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1900 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(900 + 7000 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.4)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def funk_bass(m, dur, g=0.32):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)
    x = np.tanh(x * 2.5)
    bq, aq = sg.butter(2, 750 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.005, 0.06, 0.75, 0.1) * g).astype(np.float32)

def fm_ep(m, dur, g=0.14):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    mod = 2.0 * np.exp(-t * 8) * np.sin(2 * np.pi * f * 2.001 * t)
    sig = np.sin(2 * np.pi * f * t + mod)
    bq, aq = sg.butter(2, 4200 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.005, 0.1, 0.8, 0.15) * g).astype(np.float32)

def pop_lead(m, dur, g=0.16):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.5 * t)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    sig = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    bq, aq = sg.butter(2, [400 / (SR / 2), 3500 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.02, 0.12, 0.82, 0.18) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=99):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=48):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.4 * np.exp(-t / 0.02))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
        return (np.tanh(x * 1.6) * vel).astype(np.float32)
    def snare(self, vel=1.0):
        L = int(0.35 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1]); taus = np.array([0.05, 0.15, 0.12, 0.08, 0.06, 0.05])
        body = modal(195, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1200 / (SR / 2), 8500 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / 0.12)
        x = body * 0.5 + wire * 0.85
        return (np.tanh(x * 1.35) * vel).astype(np.float32)
    def hat(self, vel=1.0, op=False):
        L = int((0.22 if op else 0.04) * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(3, 7500 / (SR / 2), 'high')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / (0.15 if op else 0.025)) * vel * 0.4).astype(np.float32)
    def clap(self, vel=1.0):
        L = int(0.2 * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1100 / (SR / 2), 4200 / (SR / 2)], 'band')
        return (sg.lfilter(bq, aq, n) * np.exp(-t / 0.04) * vel * 0.45).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(909)
    kit = DrumKit(222)
    
    TOTAL_SEC = 160.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    bpm = 124.0
    spb = 60.0 / bpm
    bar44 = 4 * spb # ~1.935s per bar
    
    TOTAL_BARS = int(TOTAL_SEC / bar44)
    
    # Magdalena Bay / 70s Disco progression: Bm7 -> Gmaj7 -> Em9 -> F#7alt
    chords_magbay = [
        ('B2', ['B3', 'D4', 'F#4', 'A4']),    # Bm7
        ('G2', ['G3', 'B3', 'D4', 'F#4']),   # Gmaj7
        ('E2', ['E3', 'G3', 'B3', 'D4', 'F#4']),# Em9
        ('F#2', ['F#3', 'A#3', 'C#4', 'E4', 'G4']),# F#7alt
    ]
    
    for bar_idx in range(TOTAL_BARS):
        b_root, b_notes = chords_magbay[bar_idx % len(chords_magbay)]
        b_t = bar_idx * bar44
        
        # Octave Disco Funk Bassline (16th-note syncopation)
        for step in np.arange(0, 4, 0.25):
            if step % 0.5 == 0:
                put(inst_bus, b_t + step * spb, funk_bass(nn(b_root), spb * 0.4, g=0.30))
            elif step % 0.25 == 0:
                put(inst_bus, b_t + step * spb, funk_bass(nn(b_root) + 12, spb * 0.3, g=0.22))

        # Bright FM EP Stabs
        for beat in [0.5, 1.5, 2.5, 3.5]:
            for n_str in b_notes:
                put(inst_bus, b_t + beat * spb + rng.uniform(-0.003, 0.003), fm_ep(nn(n_str), spb * 0.5, g=0.04))

        # Magdalena Bay Vocal-like Synth Hook (Lead)
        if bar_idx >= 4 and bar_idx % 2 == 0:
            l_n = b_notes[(bar_idx * 2) % len(b_notes)]
            t_l = b_t + 0.5 * spb + rng.uniform(-0.005, 0.005)
            put(lead_bus, t_l, pop_lead(nn(l_n) + 12, spb * 1.5, g=0.16), g=1.0)
            put(lead_bus, t_l + 1.5 * spb, pop_lead(nn(l_n) + 14, spb * 1.5, g=0.14), g=1.0)

        # Nick Villa Four-on-the-Floor Disco Drums (Kick 1-2-3-4, Snare+Clap 2&4, Hi-hat chokes on 16ths)
        for b in range(4):
            put(inst_bus, b_t + b * spb, kit.kick(1.0))
            if b in [1, 3]:
                put(inst_bus, b_t + b * spb, kit.snare(1.0))
                put(inst_bus, b_t + b * spb, kit.clap(0.85))
                
        for h in np.arange(0, 4, 0.5):
            is_open = (h in [0.5, 1.5, 2.5, 3.5])
            put(inst_bus, b_t + h * spb + rng.uniform(-0.003, 0.003), kit.hat(0.75, op=is_open))

    print("Mixing and writing WAVs...")
    ir_len = int(1.2 * SR)
    ir = np.random.default_rng(99).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.4 * SR))
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
