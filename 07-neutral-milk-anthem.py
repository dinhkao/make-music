#!/usr/bin/env python3
"""
07-neutral-milk-anthem.py — Lo-Fi Chamber Folk Punk (inspired by Neutral Milk Hotel & Elliott Smith)
G Major scale (108 BPM 6/8 waltz feel).
Chord progression: G -> G/F# -> Em -> Em/D -> C -> D (chromatic descending bassline waltz).
Nick Villa drum style: Punchy modal waltz (Kick on 1, Snare on 3 & 5, energetic flam fills).
Outputs: 07-neutral-milk-anthem.mp3 and 07-neutral-milk-anthem-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "07-neutral-milk-anthem"

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
def ks(m, dur, damp=0.995, bright=0.6, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1700 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(800 + 6000 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.45)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def accordion(m, dur, g=0.12):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    sig = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(4 * np.pi * f * t) + 0.4 * np.sin(6 * np.pi * f * t)
    sig += 0.5 * np.sin(2 * np.pi * f * 1.004 * t)
    bq, aq = sg.butter(2, [300 / (SR / 2), 3800 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.03, 0.1, 0.85, 0.15) * g).astype(np.float32)

def horn_solo(m, dur, g=0.15):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    vib = 1 + 0.007 * np.sin(2 * np.pi * 5.0 * t)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    sig = sum(np.sin(ph * k) / (k**1.15) for k in range(1, 12))
    bq, aq = sg.butter(2, [250 / (SR / 2), 4000 / (SR / 2)], 'band')
    return (sg.lfilter(bq, aq, sig) * env(L, 0.05, 0.15, 0.8, 0.2) * g).astype(np.float32)

def bassn(m, dur, g=0.28):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    bq, aq = sg.butter(2, 500 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.01, 0.1, 0.8, 0.12) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=77):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=48):
        L = int(0.4 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.2 * np.exp(-t / 0.025))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
        return (np.tanh(x * 1.5) * vel).astype(np.float32)
    def snare(self, vel=1.0, art='center'):
        L = int(0.35 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1]); taus = np.array([0.05, 0.15, 0.12, 0.08, 0.06, 0.05])
        body = modal(190, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1200 / (SR / 2), 8500 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / 0.12)
        x = body * 0.5 + wire * 0.8
        return (np.tanh(x * 1.3) * vel * (0.4 if art=='ghost' else 1.0)).astype(np.float32)
    def flam(self, vel=1.0):
        a = self.snare(vel * 0.4, art='ghost')
        b = self.snare(vel, art='center')
        gap = int(0.02 * SR)
        out = np.zeros(len(b) + gap)
        out[:len(a)] += a; out[gap:gap+len(b)] += b
        return out.astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(707)
    kit = DrumKit(155)
    
    TOTAL_SEC = 160.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    # 6/8 waltz time @ 108 BPM eighths (~0.555s per beat)
    bpm = 108.0
    sp_8th = 60.0 / bpm
    bar68 = 6 * sp_8th # ~3.333s per bar
    
    TOTAL_BARS = int(TOTAL_SEC / bar68)
    
    # Neutral Milk Hotel chromatic descending bassline waltz
    chords_nmh = [
        ('G2', ['G3', 'B3', 'D4']),   # G
        ('F#2', ['F#3', 'A3', 'D4']), # G/F#
        ('E2', ['E3', 'G3', 'B3']),   # Em
        ('D2', ['D3', 'F#3', 'A3']),  # Em/D
        ('C2', ['C3', 'E3', 'G3']),   # C
        ('D2', ['D3', 'F#3', 'A3']),  # D
    ]
    
    for bar_idx in range(TOTAL_BARS):
        b_root, b_notes = chords_nmh[bar_idx % len(chords_nmh)]
        b_t = bar_idx * bar68
        
        # Bass on beat 0
        put(inst_bus, b_t, bassn(nn(b_root), sp_8th * 2.5, g=0.30))
        
        # Acoustic Guitar Strumming (waltz pattern: 1-boom, 2-chik, 3-chik, 4-boom, 5-chik, 6-chik)
        for step in range(6):
            t_g = b_t + step * sp_8th + rng.uniform(-0.005, 0.005)
            if step in [0, 3]:
                # Boom (bass string)
                put(inst_bus, t_g, ks(nn(b_root) + 12, sp_8th * 1.5, bright=0.6, seed=bar_idx*6+step), g=0.08)
            else:
                # Chik (strum chord)
                for n_str in b_notes:
                    put(inst_bus, t_g + rng.uniform(0, 0.008), ks(nn(n_str), sp_8th * 1.2, bright=0.55, seed=bar_idx*6+step), g=0.04)

        # Accordion Harmony
        if bar_idx >= 2:
            for n_str in b_notes:
                put(inst_bus, b_t, accordion(nn(n_str), bar68 * 0.9, g=0.04))

        # Horn Counter-Melody (Lead)
        if bar_idx >= 6 and bar_idx % 2 == 0:
            h_n = b_notes[(bar_idx) % len(b_notes)]
            t_h = b_t + 1.5 * sp_8th + rng.uniform(-0.008, 0.008)
            put(lead_bus, t_h, horn_solo(nn(h_n) + 12, sp_8th * 3.0, g=0.16), g=1.0)

        # Nick Villa Folk-Punk Drums (Kick on 0, Snare on 2 & 4, Flam fills)
        put(inst_bus, b_t + 0 * sp_8th, kit.kick(1.0))
        put(inst_bus, b_t + 2 * sp_8th, kit.snare(0.9))
        put(inst_bus, b_t + 4 * sp_8th, kit.snare(0.95))
        
        if bar_idx % 4 == 3:
            put(inst_bus, b_t + 5 * sp_8th, kit.flam(1.1))

    print("Mixing and writing WAVs...")
    ir_len = int(1.4 * SR)
    ir = np.random.default_rng(77).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.5 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.26):
        padded = np.concatenate([np.zeros(int(0.02 * SR)), sig])
        res = sg.fftconvolve(padded, ir)[:len(sig)]
        return sig + wet * res

    mix_full = np.tanh(apply_reverb(lead_bus + inst_bus) * 1.15) * 0.85
    mix_inst = np.tanh(apply_reverb(inst_bus) * 1.15) * 0.85

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
