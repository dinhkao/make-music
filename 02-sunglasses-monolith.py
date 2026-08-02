#!/usr/bin/env python3
"""
02-sunglasses-monolith.py — Post-Rock Fuzz Escalation (inspired by Black Country, New Road 'Sunglasses' & Slint)
E Major / E Dorian scale. Starts quiet/spacious, escalates into massive fuzz crescendo.
Nick Villa drum style: Minimal rimshots -> stutter-step ghost notes -> thunderous double-kick post-rock rolls.
Outputs: 02-sunglasses-monolith.mp3 and 02-sunglasses-monolith-instrumental.mp3
"""
import os
import sys
import re
import subprocess
import numpy as np
from scipy import signal as sg

SR = 44100
NAME = "02-sunglasses-monolith"

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
def ks(m, dur, damp=0.995, bright=0.55, seed=0):
    key = (m, round(dur, 2), round(bright, 2), seed)
    if key in _KS: return _KS[key]
    f = hz(m); N = max(int(round(SR / f)), 2); L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1200 + m * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(800 + 6500 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst) * np.linspace(1, 0.2, N)
    exc = np.zeros(L); exc[:N] = burst
    A = np.zeros(N + 2); A[0] = 1.0; A[N] = -damp / 2; A[N+1] = -damp / 2
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.45)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y.astype(np.float32)
    return _KS[key]

def fuzz_gtr(m, dur, g=0.15, drive=8.0):
    x = ks(m, dur, damp=0.997, bright=0.85).astype(np.float64)
    x = np.tanh(x * drive)
    bq, aq = sg.butter(2, [300 / (SR / 2), 4200 / (SR / 2)], 'band')
    x = sg.lfilter(bq, aq, x)
    return (x * env(len(x), 0.005, 0.1, 0.85, 0.15) * g).astype(np.float32)

def bassn(m, dur, g=0.30):
    L = int(dur * SR) + int(0.15 * SR); t = np.arange(L) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    x = np.tanh(x * 1.8)
    bq, aq = sg.butter(2, 550 / (SR / 2), 'low')
    return (sg.lfilter(bq, aq, x) * env(L, 0.01, 0.1, 0.8, 0.12) * g).astype(np.float32)

def voice_synth(m, dur, vow='o', g=0.15):
    L = int(dur * SR) + int(0.2 * SR); t = np.arange(L) / SR; f = hz(m)
    src = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)
    bq, aq = sg.butter(2, [400 / (SR / 2), 2200 / (SR / 2)], 'band')
    src = sg.lfilter(bq, aq, src)
    return (src * env(L, 0.08, 0.2, 0.7, 0.25) * g).astype(np.float32)

IDEAL = [1.0000, 1.5934, 2.1356, 2.2952, 2.6528, 2.9172]
def modal(f0, taus, gains, L, rng):
    t = np.arange(L) / SR; ph = 2 * np.pi * f0 * t; out = np.zeros(L)
    for r, tau, gn in zip(IDEAL, taus, gains):
        if f0 * r < SR / 2.1: out += gn * np.exp(-t / tau) * np.sin(ph * r)
    return out

class DrumKit:
    def __init__(self, seed=55):
        self.rng = np.random.default_rng(seed)
    def kick(self, vel=1.0, tune=45):
        L = int(0.45 * SR); t = np.arange(L) / SR
        f = tune * (1 + 2.2 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
        return (np.tanh(x * 1.6) * vel).astype(np.float32)
    def snare(self, vel=1.0, art='center'):
        L = int(0.38 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.6, 0.4, 0.3, 0.2, 0.1]); taus = np.array([0.06, 0.18, 0.14, 0.09, 0.07, 0.05])
        body = modal(185, taus, g, L, self.rng)
        wire = self.rng.standard_normal(L)
        bq, aq = sg.butter(2, [1000 / (SR / 2), 8000 / (SR / 2)], 'band')
        wire = sg.lfilter(bq, aq, wire) * np.exp(-t / (0.15 if art=='center' else 0.05))
        x = body * 0.5 + wire * 0.9
        return (np.tanh(x * 1.4) * vel * (0.35 if art=='ghost' else (0.7 if art=='rim' else 1.0))).astype(np.float32)
    def tom(self, vel=1.0, tune=100):
        L = int(0.6 * SR); t = np.arange(L) / SR
        g = np.array([1.0, 0.7, 0.5, 0.3, 0.2, 0.1]); taus = np.array([0.3, 0.24, 0.18, 0.14, 0.1, 0.08])
        x = modal(tune, taus, g, L, self.rng)
        return (np.tanh(x * 1.3) * vel).astype(np.float32)
    def hat(self, vel=1.0, op=False):
        L = int((0.28 if op else 0.04) * SR); t = np.arange(L) / SR
        n = self.rng.standard_normal(L)
        bq, aq = sg.butter(3, 7000 / (SR / 2), 'high')
        x = sg.lfilter(bq, aq, n) * np.exp(-t / (0.2 if op else 0.02))
        return (x * vel * 0.35).astype(np.float32)

def build_song():
    print(f"Building {NAME}...")
    rng = np.random.default_rng(202)
    kit = DrumKit(88)
    
    TOTAL_SEC = 160.0
    TOTAL_SAMPLES = int(TOTAL_SEC * SR)
    lead_bus = np.zeros(TOTAL_SAMPLES)
    inst_bus = np.zeros(TOTAL_SAMPLES)
    
    # --- Part 1: Quiet Spoken Intro (0 - 45s) @ 76 BPM 4/4 ---
    bpm1 = 76.0; spb1 = 60.0 / bpm1; bar1 = 4 * spb1 # ~3.158s per bar
    t_curr = 0.0
    chords_clean = [
        ('E3', ['E4', 'G#4', 'B4', 'D#5']),  # Emaj7
        ('C#3', ['C#4', 'E4', 'G#4', 'B4']), # C#m7
        ('B2', ['B3', 'D#4', 'F#4', 'C#5']), # Badd9
        ('A2', ['A3', 'C#4', 'E4', 'G#4']),  # Amaj7
    ]
    
    for bar_idx in range(14):
        b_root, b_notes = chords_clean[bar_idx % len(chords_clean)]
        b_t = t_curr + bar_idx * bar1
        
        # Clean arpeggiated guitar
        put(inst_bus, b_t, bassn(nn(b_root), bar1 * 0.9, g=0.22))
        for step, n_str in enumerate(b_notes):
            t_n = b_t + (step * 0.75 + rng.uniform(-0.008, 0.008)) * spb1
            put(inst_bus, t_n, ks(nn(n_str), spb1 * 1.5, bright=0.5, seed=bar_idx*10+step), g=0.06)
            
        # Subtle vocal hum lead
        if bar_idx >= 4:
            v_note = b_notes[(bar_idx // 2) % len(b_notes)]
            put(lead_bus, b_t + 1.0 * spb1, voice_synth(nn(v_note), spb1 * 2.0, vow='o', g=0.12), g=1.0)
            
        # Nick Villa minimal drum groove (rimshot, subtle hats, ghost notes)
        if bar_idx >= 2:
            put(inst_bus, b_t + 0 * spb1, kit.kick(0.8))
            put(inst_bus, b_t + 1 * spb1, kit.snare(0.7, art='rim'))
            put(inst_bus, b_t + 2 * spb1, kit.snare(0.3, art='ghost'))
            put(inst_bus, b_t + 3 * spb1, kit.snare(0.85, art='rim'))
            for h in np.arange(0, 4, 0.5):
                put(inst_bus, b_t + h * spb1, kit.hat(0.35 + (0.15 if h%1==0 else 0)))

    t_curr += 14 * bar1

    # --- Part 2: Accelerando & Fuzz Escalation (45s - 105s) ---
    # Shift to 6/8 feel driving post-rock pulse @ 132 BPM
    bpm2 = 132.0; spb2 = 60.0 / bpm2; bar68 = 6 * spb2 # ~2.727s per bar
    fuzz_chords = [
        ('E2', ['E3', 'G3', 'B3', 'E4']),   # Em
        ('G2', ['G3', 'B3', 'D4', 'G4']),   # G
        ('A2', ['A3', 'C#4', 'E4', 'A4']),  # A
        ('Bb2', ['Bb3', 'D4', 'F4', 'Bb4']),# Bb (BCNR chromatic tritone tension)
    ]
    
    for bar_idx in range(22):
        b_root, b_notes = fuzz_chords[bar_idx % len(fuzz_chords)]
        b_t = t_curr + bar_idx * bar68
        intensity = 1.0 + (bar_idx / 22.0) * 0.6
        
        # Heavy Fuzz Wall & Bass
        for sub in [0, 3]:
            put(inst_bus, b_t + sub * spb2, bassn(nn(b_root), spb2 * 2.5, g=0.35 * intensity))
            for n_str in b_notes:
                put(inst_bus, b_t + sub * spb2 + rng.uniform(-0.004, 0.004), fuzz_gtr(nn(n_str), spb2 * 2.5, g=0.10 * intensity, drive=9.0))
        
        # Screaming Lead Guitar
        if bar_idx >= 6:
            lead_n = b_notes[(bar_idx * 3) % len(b_notes)]
            t_l = b_t + (1.5 + rng.uniform(-0.005, 0.005)) * spb2
            put(lead_bus, t_l, fuzz_gtr(nn(lead_n) + 12, spb2 * 3.0, g=0.14 * intensity, drive=12.0), g=1.0)

        # Nick Villa Intense 6/8 Post-Rock Drums (stutter ghost notes, heavy tom fills)
        put(inst_bus, b_t + 0 * spb2, kit.kick(1.0 * intensity))
        put(inst_bus, b_t + 1.5 * spb2, kit.snare(0.4 * intensity, art='ghost'))
        put(inst_bus, b_t + 3 * spb2, kit.snare(1.0 * intensity))
        put(inst_bus, b_t + 4.5 * spb2, kit.kick(0.85 * intensity))
        put(inst_bus, b_t + 5.5 * spb2, kit.hat(0.9, op=True))
        
        if bar_idx % 4 == 3:
            put(inst_bus, b_t + 4 * spb2, kit.tom(1.0, tune=150))
            put(inst_bus, b_t + 4.5 * spb2, kit.tom(1.0, tune=110))
            put(inst_bus, b_t + 5 * spb2, kit.tom(1.1, tune=80))

    t_curr += 22 * bar68

    # --- Part 3: Climax & Dissolution (105s - 155s) ---
    for bar_idx in range(18):
        b_t = t_curr + bar_idx * (4 * spb1)
        # Full heavy unison wall
        put(inst_bus, b_t, bassn(nn('E1'), 4 * spb1, g=0.4))
        for n_s in ['E3', 'G3', 'B3', 'E4', 'G4']:
            put(inst_bus, b_t, fuzz_gtr(nn(n_s), 4 * spb1, g=0.12, drive=14.0))
            put(lead_bus, b_t + 2 * spb1, fuzz_gtr(nn(n_s)+12, 2 * spb1, g=0.14, drive=16.0), g=1.0)
            
        # Nick Villa Thunderous Double Kick Rolls
        for step in np.arange(0, 4, 0.25):
            if step % 0.5 == 0:
                put(inst_bus, b_t + step * spb1, kit.kick(1.1))
            else:
                put(inst_bus, b_t + step * spb1, kit.snare(1.0))

    # Final Ring Out
    t_curr += 18 * (4 * spb1)
    put(inst_bus, t_curr, kit.kick(1.2))
    put(inst_bus, t_curr, kit.snare(1.2))
    put(inst_bus, t_curr, bassn(nn('E1'), 5.0, g=0.45))
    put(inst_bus, t_curr, fuzz_gtr(nn('E2'), 5.0, g=0.2, drive=15.0))

    print("Mixing and writing WAVs...")
    ir_len = int(1.5 * SR)
    ir = np.random.default_rng(15).standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.5 * SR))
    ir /= np.sqrt(np.sum(ir**2))
    
    def apply_reverb(sig, wet=0.28):
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
